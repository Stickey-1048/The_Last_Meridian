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
        {
            var got = info.Records.FirstOrDefault(r => r.Type == "Book" && r.EditorId == b.EditorId && r.Name == b.Name);
            if (got == null) { problems.Add($"book {b.EditorId} missing or misnamed"); continue; }
            builder.BorrowedModels.TryGetValue(b.EditorId, out var model);
            Expect(got.Model == model, $"book {b.EditorId}: world model is '{got.Model ?? "none"}', expected '{model ?? "none"}'");
            Expect(b.LooksLikeANote || got.Model == null, $"book {b.EditorId}: has a world model the spec does not ask for");
        }
        foreach (var m in Spec.MiscItems)
        {
            var got = info.Records.FirstOrDefault(r => r.Type == "MiscItem" && r.EditorId == m.EditorId && r.Name == m.Name);
            if (got == null) { problems.Add($"misc item {m.EditorId} missing or misnamed"); continue; }
            builder.BorrowedModels.TryGetValue(m.EditorId, out var model);
            Expect(got.Model == model, $"misc item {m.EditorId}: world model is '{got.Model ?? "none"}', expected '{model ?? "none"}'");
            Expect(m.ModelFrom != null || m.LooksLike != null || got.Model == null, $"misc item {m.EditorId}: has a world model the spec does not ask for");
        }
        foreach (var a in Spec.Activators)
        {
            var got = info.Records.FirstOrDefault(r => r.Type == "Activator" && r.EditorId == a.EditorId);
            if (got == null) { problems.Add($"activator {a.EditorId} missing"); continue; }
            builder.BorrowedModels.TryGetValue(a.EditorId, out var model);
            Expect(got.Model == model, $"activator {a.EditorId}: world model is '{got.Model ?? "none"}', expected '{model ?? "none"}'");
            // One with no look is a trigger: it must have no model at all.
            Expect(a.LooksLike != null || got.Model == null, $"activator {a.EditorId}: has a world model the spec does not ask for");
            Expect(got.Name == a.Name, $"activator {a.EditorId}: named '{got.Name ?? "nothing"}', expected '{a.Name ?? "nothing"}'");
        }
        foreach (var c in Spec.Containers)
        {
            var got = info.Records.FirstOrDefault(r => r.Type == "Container" && r.EditorId == c.EditorId && r.Name == c.Name);
            if (got == null) { problems.Add($"container {c.EditorId} missing or misnamed"); continue; }
            builder.BorrowedModels.TryGetValue(c.EditorId, out var model);
            Expect(got.Model == model, $"container {c.EditorId}: world model is '{got.Model ?? "none"}', expected '{model ?? "none"}'");
            var held = builder.VanillaFound.FirstOrDefault(v => string.Equals(v.EditorId, c.HoldsVanillaItem, StringComparison.OrdinalIgnoreCase))?.FormKey;
            var want = held == null ? new List<string>() : new List<string> { $"{c.Count} of {held}" };
            Expect((got.Holds ?? new()).SequenceEqual(want), $"container {c.EditorId}: holds [{string.Join(", ", got.Holds ?? new())}], expected [{string.Join(", ", want)}]");
        }

        foreach (var n in Spec.Npcs)
        {
            var got = info.Npcs.FirstOrDefault(x => x.EditorId == n.EditorId);
            if (!builder.MadeNpcs.Contains(n.EditorId))
            {
                Expect(got == null, $"actor {n.EditorId}: is in the plugin although the build did not make it");
                continue;
            }
            if (got == null) { problems.Add($"actor {n.EditorId} missing"); continue; }
            Expect(got.Name == n.Name, $"actor {n.EditorId}: named '{got.Name}', expected '{n.Name}'");
            // What should make it stay where it is put: nothing to go about.
            Expect(got.Packages == 0, $"actor {n.EditorId}: still has {got.Packages} package(s)");
            // The default package list: as the game's actor has it (in its record or from a template), or not at all.
            builder.SourceDefaultList.TryGetValue(n.CopyFrom, out var had);
            var wantList = n.KeepDefaultPackageList && had.InRecord;
            var wantFromTemplate = n.KeepDefaultPackageList && had.FromTemplate;
            Expect(got.HasDefaultPackageList == wantList, $"actor {n.EditorId}: {(got.HasDefaultPackageList ? "has a" : "has no")} default package list, expected {(wantList ? "the one of " + n.CopyFrom : "none")}");
            Expect(got.TemplateFlags.Contains("DefPackList") == wantFromTemplate, $"actor {n.EditorId}: {(wantFromTemplate ? "no longer takes" : "still takes")} its default package list from a template");
            var wantLink = n.KeepDefaultPackageList && had.TemplateActor;
            Expect(got.TemplateLinks.Contains("DefPackList") == wantLink, $"actor {n.EditorId}: {(wantLink ? "no longer names" : "still names")} a template actor for its default package list");
            Expect(!got.Compressed, $"actor {n.EditorId}: its record is compressed");
            Expect(got.Scripts.Count == 0, $"actor {n.EditorId}: still has script(s) {string.Join(", ", got.Scripts)}");
            foreach (var flag in new[] { "AiPackages", "Script" })
            {
                Expect(!got.TemplateFlags.Contains(flag), $"actor {n.EditorId}: still takes {flag} from a template");
                // The flag gone and the actor still named for it: which of the two the game goes by is not known.
                Expect(!got.TemplateLinks.Contains(flag), $"actor {n.EditorId}: still names a template actor for {flag}");
            }
            // Whose looks: the actor the build chose, if it could choose one.
            if (builder.LooksFrom.TryGetValue(n.EditorId, out var looks))
            {
                Expect(n.Sex != null, $"actor {n.EditorId}: was given looks the spec does not ask for");
                Expect(got.LooksFrom == looks, $"actor {n.EditorId}: takes its looks from {got.LooksFrom ?? "nobody"}, expected {looks}");
                Expect(got.TemplateFlags.Contains("Traits"), $"actor {n.EditorId}: names an actor for its looks and does not take them from it");
            }
            if (n.Faction != null)
            {
                Expect((got.Factions ?? new()).SequenceEqual(new[] { n.Faction }), $"actor {n.EditorId}: is in [{string.Join(", ", got.Factions ?? new())}], expected only {n.Faction}");
                Expect(!got.TemplateFlags.Contains("Factions") && !got.TemplateLinks.Contains("Factions"), $"actor {n.EditorId}: still takes its factions from a template");
            }
            if (n.StandsBy)
            {
                var want = $"Unaggressive, {(n.HelpsItsOwn ? "HelpsAllies" : "HelpsNobody")}, Foolhardy";
                Expect(got.Temper == want, $"actor {n.EditorId}: its temper is '{got.Temper}', expected '{want}'");
                Expect(!got.TemplateFlags.Contains("AiData") && !got.TemplateLinks.Contains("AiData"), $"actor {n.EditorId}: still takes its temper from a template");
            }
        }
        // Two people with one face would be told apart only by their names.
        var faces = builder.LooksFrom.GroupBy(kv => kv.Value).Where(g => g.Count() > 1).Select(g => string.Join(" and ", g.Select(kv => kv.Key))).ToList();
        foreach (var same in faces)
            if (!builder.VanillaNotes.Any(x => x.Contains("used before: there are more people than faces")))
                problems.Add($"{same} were given the same looks, and the build did not say why");
        Expect(info.Npcs.All(x => Spec.Npcs.Any(n => n.EditorId == x.EditorId)), "the plugin holds an actor the spec does not ask for");

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
                foreach (var bind in a.Scripts)
                    if (ga.Scripts.FirstOrDefault(s => s.Name == bind.Script) is { } gs)
                        CheckProps($"{q.EditorId} alias {a.Name}", q, bind, gs, problems);
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
                CheckProps(q.EditorId, q, bind, gs, problems);
            }
        }
        return problems;
    }

    /// <summary>The properties of one attached script, as read back, against what the spec gives it.</summary>
    static void CheckProps(string where, QuestSpec q, ScriptBind bind, Report.ScriptInfo gs, List<string> problems)
    {
        void Expect(bool ok, string message) { if (!ok) problems.Add(message); }
        int AliasOf(string? questId, string alias) =>
            Array.FindIndex((questId == null ? q : Spec.Quests.First(x => x.EditorId == questId)).Aliases, a => a.Name == alias);
        var names = bind.Props.Select(p => p.Name).ToList();
        Expect(names.Distinct(StringComparer.OrdinalIgnoreCase).Count() == names.Count, $"{where} script {bind.Script}: a property is given twice");
        foreach (var p in bind.Props)
        {
            // Absent without the game's master, by design.
            if (p is VanillaProp or VanillaNamedProp or AmmoOfWeaponNamedProp) continue;
            var gp = gs.Props.FirstOrDefault(x => x.Name == p.Name);
            if (gp == null) { problems.Add($"{where}: property {p.Name} not written"); continue; }
            switch (p)
            {
                case FormProp fp: Expect(gp.Target == fp.EditorId && gp.Alias == null, $"{where}.{p.Name}: points at {gp.Target}"); break;
                case AliasProp ap:
                    Expect(gp.Target == (ap.Quest ?? q.EditorId) && gp.Alias == AliasOf(ap.Quest, ap.Alias), $"{where}.{p.Name}: wrong alias");
                    break;
                case IntProp ip: Expect(gp.Kind == "int" && Equals(gp.Value, ip.Value), $"{where}.{p.Name}: is {gp.Value}, expected {ip.Value}"); break;
                case BoolProp bp: Expect(gp.Kind == "bool" && Equals(gp.Value, bp.Value), $"{where}.{p.Name}: is {gp.Value}, expected {bp.Value}"); break;
                case IntListProp lp:
                    Expect(gp.Kind == "int[]" && ((IEnumerable<int>)gp.Value!).SequenceEqual(lp.Values), $"{where}.{p.Name}: the numbers differ");
                    break;
                case StringListProp sp:
                    Expect(gp.Kind == "string[]" && ((IEnumerable<string>)gp.Value!).SequenceEqual(sp.Values), $"{where}.{p.Name}: the texts differ");
                    break;
                case AliasListProp alp:
                    var want = alp.Items.Select(i => new Report.ObjectInfo(i.Quest, AliasOf(i.Quest, i.Alias))).ToList();
                    Expect(gp.Kind == "object[]" && ((IEnumerable<Report.ObjectInfo>)gp.Value!).SequenceEqual(want), $"{where}.{p.Name}: the aliases differ");
                    Expect(want.All(w => w.Alias >= 0), $"{where}.{p.Name}: names an alias its quest does not have");
                    break;
            }
        }
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
            builder.CellNames.TryGetValue(name, out var wantName);
            Expect(cell.Name == wantName, $"cell {name}: its name in the plugin is '{cell.Name ?? "none"}', the builder read '{wantName ?? "none"}' from the master");
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
            // An actor is placed with a record of its own kind, whether its base is the game's or this plugin's.
            var isNpc = p.VanillaKind == null
                ? Spec.Npcs.Any(n => n.EditorId == p.Base)
                : string.Equals(p.VanillaKind, "Npc", StringComparison.OrdinalIgnoreCase);
            Expect(got.Kind == (isNpc ? "PlacedNpc" : "PlacedObject"), $"{p.EditorId}: is a {got.Kind}");
            var wantBase = p.VanillaKind == null
                ? p.Base
                : p.BaseNames != null
                    // Found by the name a player sees: whichever of the game's records the build settled on.
                    ? builder.PlacedGameBase.GetValueOrDefault(p.EditorId)
                    : builder.VanillaFound.FirstOrDefault(v => string.Equals(v.EditorId, p.Base, StringComparison.OrdinalIgnoreCase)
                                                               && string.Equals(v.Kind, p.VanillaKind, StringComparison.OrdinalIgnoreCase))?.FormKey;
            Expect(wantBase != null && got.Base == wantBase, $"{p.EditorId}: places {got.Base}, expected {wantBase ?? p.Base}");
            // A reference a quest alias points at has to be persistent, in both senses the file has.
            Expect(got.Persistent, $"{p.EditorId}: the Persistent flag is not set");
            Expect(got.Group == "Persistent", $"{p.EditorId}: is in the cell's {got.Group} list");
            Expect(got.InitiallyDisabled == p.InitiallyDisabled, $"{p.EditorId}: Initially Disabled differs");
            Expect(got.StartsDead == p.StartsDead, $"{p.EditorId}: Starts Dead differs");
            Expect(!p.StartsDead || isNpc, $"{p.EditorId}: only an actor can start dead");
            if (p.BoxHalfExtents == null)
                Expect(got.Primitive == null && got.CollisionLayer == null && got.Bound == null, $"{p.EditorId}: has a primitive, a bound or a collision layer the spec does not ask for");
            else
            {
                Expect(got.Primitive == "Box" && got.Box != null && got.Box.SequenceEqual(p.BoxHalfExtents), $"{p.EditorId}: the box differs");
                Expect(builder.WritesBoxBound ? got.Bound != null && got.Bound.SequenceEqual(p.BoxHalfExtents) : got.Bound == null,
                    $"{p.EditorId}: the reference's bound is {(got.Bound == null ? "missing" : "(" + string.Join(", ", got.Bound) + ")")}; this build {(builder.WritesBoxBound ? "writes the box's reach there" : "writes none")}");
                // The layer is stored as the number the master gives the layer the spec names.
                uint? wantLayer = builder.PlacedLayers.TryGetValue(p.EditorId, out var index) ? index : null;
                Expect(got.CollisionLayer == wantLayer, $"{p.EditorId}: collision layer is {got.CollisionLayer?.ToString() ?? "missing"}, expected {wantLayer?.ToString() ?? "none"}");
                Expect(wantLayer != null || p.CollisionLayer == null || builder.Pending.Any(x => x.StartsWith(p.EditorId + ": placed without a collision layer")),
                    $"{p.EditorId}: has no collision layer, and the build did not say why");
            }
            var arrival = builder.Arrivals.FirstOrDefault(a => string.Equals(a.Cell, p.Cell, StringComparison.OrdinalIgnoreCase));
            if (arrival == null) { Expect(false, $"{p.EditorId}: the builder did not say where the player arrives in {p.Cell}"); continue; }
            double Sq(double x) => x * x;
            var want = Math.Sqrt(Sq(p.Ahead) + Sq(p.Right) + Sq(p.Up));
            var have = Math.Sqrt(Sq(got.Position[0] - arrival.Position[0]) + Sq(got.Position[1] - arrival.Position[1]) + Sq(got.Position[2] - arrival.Position[2]));
            Expect(Math.Abs(want - have) < 0.5, $"{p.EditorId}: is {have:0.#} from the arrival point, expected {want:0.#}");
            Expect(Math.Abs(got.Position[2] - arrival.Position[2] - p.Up) < 0.01, $"{p.EditorId}: height above the arrival point differs");
            // And the direction: how far ahead of the arrival point, along the way the player faces there
            // (measured from north towards east), and how far to the right of that.
            var (dx, dy) = (got.Position[0] - arrival.Position[0], got.Position[1] - arrival.Position[1]);
            var (north, east) = (Math.Cos(arrival.Heading), Math.Sin(arrival.Heading));
            var ahead = dx * east + dy * north;
            var right = dx * north - dy * east;
            Expect(Math.Abs(ahead - p.Ahead) < 0.5 && Math.Abs(right - p.Right) < 0.5,
                $"{p.EditorId}: is {ahead:0.#} ahead of the arrival point and {right:0.#} to its right, expected {p.Ahead:0.#} and {p.Right:0.#}");
        }
    }
}
