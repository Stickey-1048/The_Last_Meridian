namespace Tlm.PluginBuilder;

/// <summary>
/// Compares the plugin as read back from disk with <see cref="Spec"/>.
/// This proves the file contains what the spec says. It does not prove the
/// Creation Kit or the game accepts it.
/// </summary>
public static class SelfCheck
{
    /// <param name="builder">The builder that wrote the plugin: which references it placed, where the player
    /// arrives in their cells, and which of the game's records it found. Those are not in the spec; they depend
    /// on the master the plugin was built against.</param>
    public static List<string> Run(Report.PluginInfo info, Builder builder)
    {
        var problems = new List<string>();
        void Expect(bool ok, string message) { if (!ok) problems.Add(message); }

        Expect(info.Masters.SequenceEqual(new[] { "Fallout4.esm" }), $"masters are [{string.Join(", ", info.Masters)}], expected exactly Fallout4.esm");

        // Records below 0x800 are only valid for the 2024 "next-gen" game and later.
        Expect(info.LowestFormId >= 0x800, $"lowest FormID is 0x{info.LowestFormId:X}; must be 0x800 or above to load on every game build");
        Expect(info.HeaderVersion is > 0.94f and < 0.96f or > 0.99f and < 1.01f, $"unexpected header version {info.HeaderVersion}");

        var ids = info.Records.Select(r => r.EditorId)
            .Concat(info.Messages.Select(m => m.EditorId))
            .Concat(info.Quests.Select(q => q.EditorId))
            .Concat(info.Cells.SelectMany(c => c.Placed).Select(p => p.EditorId ?? "(a placed reference without an EditorID)")).ToList();
        Expect(ids.All(id => id.StartsWith("TLM_")), "an EditorID is missing the TLM_ prefix");
        Expect(ids.Distinct(StringComparer.OrdinalIgnoreCase).Count() == ids.Count, "duplicate EditorID");

        foreach (var g in Spec.Globals)
            Expect(info.Records.Any(r => r.Type == "Global" && r.EditorId == g), $"global {g} missing");
        foreach (var f in Spec.Factions)
            Expect(info.Records.Any(r => r.Type == "Faction" && r.EditorId == f), $"faction {f} missing");
        foreach (var b in Spec.Books)
            Expect(info.Records.Any(r => r.Type == "Book" && r.EditorId == b.EditorId && r.Name == b.Name), $"book {b.EditorId} missing or misnamed");
        foreach (var m in Spec.MiscItems)
        {
            var got = info.Records.FirstOrDefault(r => r.Type == "MiscItem" && r.EditorId == m.EditorId && r.Name == m.Name);
            if (got == null) { problems.Add($"misc item {m.EditorId} missing or misnamed"); continue; }
            builder.BorrowedModels.TryGetValue(m.EditorId, out var model);
            Expect(got.Model == model, $"misc item {m.EditorId}: world model is '{got.Model ?? "none"}', expected '{model ?? "none"}'");
            Expect(m.ModelFrom != null || got.Model == null, $"misc item {m.EditorId}: has a world model the spec does not ask for");
        }
        foreach (var a in Spec.Activators)
            Expect(info.Records.Any(r => r.Type == "Activator" && r.EditorId == a.EditorId && r.Model == null), $"activator {a.EditorId} missing, or it has a model");

        CheckPlaced(info, builder, Expect);

        foreach (var m in Spec.Messages)
        {
            var got = info.Messages.FirstOrDefault(x => x.EditorId == m.EditorId);
            if (got == null) { problems.Add($"message {m.EditorId} missing"); continue; }
            Expect(got.Text == m.Text, $"message {m.EditorId}: text differs");
            Expect((got.Title ?? "") == (m.Title ?? ""), $"message {m.EditorId}: title is '{got.Title}', expected '{m.Title}'");
            Expect(got.Box == m.Box, $"message {m.EditorId}: box flag differs");
            Expect(got.Buttons.Select(b => b.Text).SequenceEqual(m.Buttons.Select(b => b.Text)), $"message {m.EditorId}: buttons differ");
            for (var i = 0; i < Math.Min(got.Buttons.Count, m.Buttons.Length); i++)
                Expect(got.Buttons[i].Conditions.Count == m.Buttons[i].Conditions.Length, $"message {m.EditorId} button {i}: condition count differs");
        }

        foreach (var q in Spec.Quests)
        {
            var got = info.Quests.FirstOrDefault(x => x.EditorId == q.EditorId);
            if (got == null) { problems.Add($"quest {q.EditorId} missing"); continue; }
            Expect(got.Name == q.Name, $"{q.EditorId}: name differs");
            Expect(got.Type == q.Type, $"{q.EditorId}: type is {got.Type}");
            Expect(got.Flags.Contains("StartGameEnabled") == q.StartGameEnabled, $"{q.EditorId}: Start Game Enabled differs");
            Expect(got.Flags.Contains("RunOnce"), $"{q.EditorId}: Run Once not set");
            Expect(!got.Flags.Contains("AllowRepeatedStages"), $"{q.EditorId}: repeated stages must stay off (stages are one-shot by design)");
            Expect(got.Stages.Select(s => s.Index).SequenceEqual(q.Stages.Select(s => s.Index)), $"{q.EditorId}: stage list differs");
            Expect(got.Stages.Select(s => s.Index).Distinct().Count() == got.Stages.Count, $"{q.EditorId}: duplicate stage index");
            foreach (var s in q.Stages)
            {
                var gs = got.Stages.FirstOrDefault(x => x.Index == s.Index);
                if (gs == null) continue;
                Expect(gs.Log == s.Log, $"{q.EditorId} stage {s.Index}: log text differs");
                Expect(gs.CompleteQuest == s.CompleteQuest, $"{q.EditorId} stage {s.Index}: Complete Quest differs");
            }
            Expect(got.Stages.Count(s => s.CompleteQuest) == (q.Stages.Length == 0 ? 0 : 1), $"{q.EditorId}: expected exactly one Complete Quest stage");
            // The game announces a stage (OnStageSet) once per item. A stage with
            // no item, or an item without its flags subrecord, is set silently:
            // seen in the game on 2026-11-12.
            foreach (var gs in got.Stages)
                Expect(gs.Items == 1 && gs.ItemsWithFlags == 1, $"{q.EditorId} stage {gs.Index}: has {gs.Items} item(s), {gs.ItemsWithFlags} with the flags subrecord; needs exactly one item with it, or the scripts are never told the stage was set");
            foreach (var go in got.Objectives)
                Expect(go.HasFlags, $"{q.EditorId} objective {go.Index}: flags subrecord not written");
            Expect(got.HasConditionMarker, $"{q.EditorId}: the marker between the quest's condition lists (NEXT) is not written");
            Expect(got.Objectives.Select(o => (o.Index, o.Text)).SequenceEqual(q.Objectives.Select(o => (o.Index, o.Text))), $"{q.EditorId}: objectives differ");
            Expect(got.Aliases.Select(a => a.Name).SequenceEqual(q.Aliases.Select(a => a.Name)), $"{q.EditorId}: alias list differs");
            Expect(got.Aliases.Select(a => a.Id).SequenceEqual(Enumerable.Range(0, q.Aliases.Length)), $"{q.EditorId}: alias IDs are not 0..n-1");

            foreach (var o in q.Objectives.Where(o => o.TargetAlias != null))
            {
                var want = Array.FindIndex(q.Aliases, a => a.Name == o.TargetAlias);
                var go = got.Objectives.First(x => x.Index == o.Index);
                Expect(go.TargetAliases.SequenceEqual(new[] { want }), $"{q.EditorId} objective {o.Index}: target alias differs");
            }

            for (var i = 0; i < q.Aliases.Length && i < got.Aliases.Count; i++)
            {
                var a = q.Aliases[i];
                var ga = got.Aliases[i];
                Expect(ga.Flags.Contains("QuestObject") == a.QuestObject, $"{q.EditorId} alias {a.Name}: Quest Object differs");
                Expect(ga.Flags.Contains("Essential") == a.Essential, $"{q.EditorId} alias {a.Name}: Essential differs");
                Expect(ga.Flags.Contains("Protected") == a.Protected, $"{q.EditorId} alias {a.Name}: Protected differs");
                Expect(ga.Flags.Contains("AllowDead") == a.AllowDead, $"{q.EditorId} alias {a.Name}: Allow Dead differs");
                Expect(ga.Flags.Contains("AllowDisabled") == a.AllowDisabled, $"{q.EditorId} alias {a.Name}: Allow Disabled differs");
                Expect(!(a.Essential && a.Protected), $"{q.EditorId} alias {a.Name}: Essential and Protected are mutually exclusive");
                Expect(ga.Scripts.Select(s => s.Name).SequenceEqual(a.Scripts.Select(s => s.Script)), $"{q.EditorId} alias {a.Name}: scripts differ");
                if (a.Fill == Fill.CreateIn)
                    Expect(ga.Fill != null && ga.Fill.StartsWith($"create {a.CreateItem} In alias {Array.FindIndex(q.Aliases, x => x.Name == a.CreateInAlias)}"),
                        $"{q.EditorId} alias {a.Name}: create-in fill differs ({ga.Fill})");
                if (a.Fill == Fill.Placed)
                {
                    var want = builder.PlacedKeys.TryGetValue(a.Placed ?? "", out var key) ? $"forced {key}" : null;
                    Expect(ga.Fill == want, $"{q.EditorId} alias {a.Name}: fill is '{ga.Fill ?? "none"}', expected '{want ?? "none"}'");
                    Expect(ga.Flags.Contains("Optional"), $"{q.EditorId} alias {a.Name}: an alias for a placed reference must be Optional");
                    Expect(Spec.Placed.Any(p => p.EditorId == a.Placed), $"{q.EditorId} alias {a.Name}: the spec places no reference '{a.Placed}'");
                    var spec = Spec.Placed.FirstOrDefault(p => p.EditorId == a.Placed);
                    Expect(spec == null || !spec.InitiallyDisabled || a.AllowDisabled,
                        $"{q.EditorId} alias {a.Name}: its reference starts disabled, so the alias needs Allow Disabled");
                }
                Expect(ga.DisplayName == a.DisplayName, $"{q.EditorId} alias {a.Name}: display name is '{ga.DisplayName ?? "none"}', expected '{a.DisplayName ?? "none"}'");
            }

            Expect(got.Scripts.Select(s => s.Name).SequenceEqual(q.AllScripts().Select(s => s.Script)), $"{q.EditorId}: attached scripts differ");
            foreach (var bind in q.AllScripts())
            {
                var gs = got.Scripts.FirstOrDefault(s => s.Name == bind.Script);
                if (gs == null) { problems.Add($"{q.EditorId}: script {bind.Script} not attached"); continue; }
                foreach (var p in bind.Props)
                {
                    if (p is VanillaProp) continue;   // absent in skeleton mode by design
                    var gp = gs.Props.FirstOrDefault(x => x.Name == p.Name);
                    if (gp == null) { problems.Add($"{q.EditorId}: property {p.Name} not written"); continue; }
                    switch (p)
                    {
                        case FormProp fp: Expect(gp.Target == fp.EditorId && gp.Alias == null, $"{q.EditorId}.{p.Name}: points at {gp.Target}"); break;
                        case AliasProp ap:
                            Expect(gp.Target == q.EditorId && gp.Alias == Array.FindIndex(q.Aliases, a => a.Name == ap.Alias), $"{q.EditorId}.{p.Name}: wrong alias");
                            break;
                    }
                }
            }
        }
        return problems;
    }

    /// <summary>
    /// The references the plugin places in cells of the game, as read back from the file.
    /// </summary>
    static void CheckPlaced(Report.PluginInfo info, Builder builder, Action<bool, string> Expect)
    {
        var placedIds = Spec.Placed.Select(p => p.EditorId).ToList();
        Expect(placedIds.Distinct(StringComparer.OrdinalIgnoreCase).Count() == placedIds.Count, "two placed references share an EditorID");

        var built = Spec.Placed.Where(p => builder.PlacedKeys.ContainsKey(p.EditorId)).ToList();
        var cellNames = built.Select(p => p.Cell).Distinct(StringComparer.OrdinalIgnoreCase).ToList();
        Expect(info.Cells.Count == cellNames.Count, $"the plugin has {info.Cells.Count} cell record(s), expected {cellNames.Count}");

        foreach (var cell in info.Cells)
        {
            var name = cell.EditorId ?? "(no EditorID)";
            Expect(!cell.OfThisPlugin, $"cell {name}: is a new cell of this plugin; only copies of the game's cells are expected");
            Expect(cellNames.Contains(name, StringComparer.OrdinalIgnoreCase), $"cell {name}: the spec places nothing there");
            // The plugin's copy of the cell's record goes where the master files the cell.
            if (builder.CellsFiled.TryGetValue(name, out var filed))
                Expect((cell.Block, cell.SubBlock) == filed,
                    $"cell {name} ({cell.FormKey}): filed under block {cell.Block}, sub-block {cell.SubBlock}; the master files it under {filed.Block} and {filed.SubBlock}");
            else
                Expect(false, $"cell {name} ({cell.FormKey}): the builder did not find where the master files it");
            foreach (var p in cell.Placed)
            {
                // The game's own references in the cell stay in the master. A copy
                // of one here would override it, and would be the game's data.
                Expect(p.FormKey.EndsWith(":" + Spec.PluginName, StringComparison.OrdinalIgnoreCase),
                    $"cell {name}: holds {p.FormKey}, which is not a reference of this plugin");
                Expect(placedIds.Contains(p.EditorId ?? "", StringComparer.OrdinalIgnoreCase), $"cell {name}: holds {p.EditorId ?? p.FormKey}, which the spec does not place");
            }
        }

        foreach (var p in built)
        {
            var key = builder.PlacedKeys[p.EditorId].ToString();
            var cell = info.Cells.FirstOrDefault(c => string.Equals(c.EditorId, p.Cell, StringComparison.OrdinalIgnoreCase));
            var got = cell?.Placed.FirstOrDefault(x => x.FormKey == key);
            if (got == null) { Expect(false, $"{p.EditorId}: not in cell {p.Cell} of the written plugin"); continue; }
            Expect(got.EditorId == p.EditorId, $"{p.EditorId}: EditorID read back as '{got.EditorId}'");
            var isNpc = string.Equals(p.VanillaKind, "Npc", StringComparison.OrdinalIgnoreCase);
            Expect(got.Kind == (isNpc ? "PlacedNpc" : "PlacedObject"), $"{p.EditorId}: is a {got.Kind}");
            var wantBase = p.VanillaKind == null
                ? p.Base
                : builder.VanillaFound.FirstOrDefault(v => string.Equals(v.EditorId, p.Base, StringComparison.OrdinalIgnoreCase)
                                                           && string.Equals(v.Kind, p.VanillaKind, StringComparison.OrdinalIgnoreCase))?.FormKey;
            Expect(wantBase != null && got.Base == wantBase, $"{p.EditorId}: places {got.Base}, expected {wantBase ?? p.Base}");
            // A reference a quest alias points at has to be persistent, in both senses the file has.
            Expect(got.Persistent, $"{p.EditorId}: the Persistent flag is not set");
            Expect(got.Group == "Persistent", $"{p.EditorId}: is in the cell's {got.Group} list");
            Expect(got.InitiallyDisabled == p.InitiallyDisabled, $"{p.EditorId}: Initially Disabled differs");
            if (p.BoxHalfExtents == null)
                Expect(got.Primitive == null && got.CollisionLayer == null && got.Bound == null, $"{p.EditorId}: has a primitive, a bound or a collision layer the spec does not ask for");
            else
            {
                Expect(got.Primitive == "Box" && got.Box != null && got.Box.SequenceEqual(p.BoxHalfExtents), $"{p.EditorId}: the box differs");
                Expect(builder.WritesBoxBound ? got.Bound != null && got.Bound.SequenceEqual(p.BoxHalfExtents) : got.Bound == null,
                    $"{p.EditorId}: the reference's bound is {(got.Bound == null ? "missing" : "(" + string.Join(", ", got.Bound) + ")")}; this build {(builder.WritesBoxBound ? "writes the box's reach there" : "writes none")}");
                var layerPending = builder.Pending.Any(x => x.StartsWith(p.EditorId + ": placed without a collision layer"));
                Expect((got.CollisionLayer != null) == (p.CollisionLayer != null && !layerPending), $"{p.EditorId}: collision layer is {(got.CollisionLayer == null ? "missing" : "present")}");
            }
            var arrival = builder.Arrivals.FirstOrDefault(a => string.Equals(a.Cell, p.Cell, StringComparison.OrdinalIgnoreCase));
            if (arrival == null) { Expect(false, $"{p.EditorId}: the builder did not say where the player arrives in {p.Cell}"); continue; }
            double Sq(double x) => x * x;
            var want = Math.Sqrt(Sq(p.Ahead) + Sq(p.Right) + Sq(p.Up));
            var have = Math.Sqrt(Sq(got.Position[0] - arrival.Position[0]) + Sq(got.Position[1] - arrival.Position[1]) + Sq(got.Position[2] - arrival.Position[2]));
            Expect(Math.Abs(want - have) < 0.5, $"{p.EditorId}: is {have:0.#} from the arrival point, expected {want:0.#}");
            Expect(Math.Abs(got.Position[2] - arrival.Position[2] - p.Up) < 0.01, $"{p.EditorId}: height above the arrival point differs");
        }
    }
}
