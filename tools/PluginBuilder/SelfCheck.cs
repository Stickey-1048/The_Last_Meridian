namespace Tlm.PluginBuilder;

/// <summary>
/// Compares the plugin as read back from disk with <see cref="Spec"/>.
/// This proves the file contains what the spec says. It does not prove the
/// Creation Kit or the game accepts it.
/// </summary>
public static class SelfCheck
{
    public static List<string> Run(Report.PluginInfo info)
    {
        var problems = new List<string>();
        void Expect(bool ok, string message) { if (!ok) problems.Add(message); }

        Expect(info.Masters.SequenceEqual(new[] { "Fallout4.esm" }), $"masters are [{string.Join(", ", info.Masters)}], expected exactly Fallout4.esm");

        // Records below 0x800 are only valid for the 2024 "next-gen" game and later.
        Expect(info.LowestFormId >= 0x800, $"lowest FormID is 0x{info.LowestFormId:X}; must be 0x800 or above to load on every game build");
        Expect(info.HeaderVersion is > 0.94f and < 0.96f or > 0.99f and < 1.01f, $"unexpected header version {info.HeaderVersion}");

        var ids = info.Records.Select(r => r.EditorId)
            .Concat(info.Messages.Select(m => m.EditorId))
            .Concat(info.Quests.Select(q => q.EditorId)).ToList();
        Expect(ids.All(id => id.StartsWith("TLM_")), "an EditorID is missing the TLM_ prefix");
        Expect(ids.Distinct(StringComparer.OrdinalIgnoreCase).Count() == ids.Count, "duplicate EditorID");

        foreach (var g in Spec.Globals)
            Expect(info.Records.Any(r => r.Type == "Global" && r.EditorId == g), $"global {g} missing");
        foreach (var f in Spec.Factions)
            Expect(info.Records.Any(r => r.Type == "Faction" && r.EditorId == f), $"faction {f} missing");
        foreach (var b in Spec.Books)
            Expect(info.Records.Any(r => r.Type == "Book" && r.EditorId == b.EditorId && r.Name == b.Name), $"book {b.EditorId} missing or misnamed");
        foreach (var m in Spec.MiscItems)
            Expect(info.Records.Any(r => r.Type == "MiscItem" && r.EditorId == m.EditorId && r.Name == m.Name), $"misc item {m.EditorId} missing or misnamed");

        foreach (var m in Spec.Messages)
        {
            var got = info.Messages.FirstOrDefault(x => x.EditorId == m.EditorId);
            if (got == null) { problems.Add($"message {m.EditorId} missing"); continue; }
            Expect(got.Text == m.Text, $"message {m.EditorId}: text differs");
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
            }

            if (q.Script != null)
            {
                var gs = got.Scripts.FirstOrDefault(s => s.Name == q.Script.Script);
                if (gs == null) { problems.Add($"{q.EditorId}: script {q.Script.Script} not attached"); continue; }
                foreach (var p in q.Script.Props)
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
}
