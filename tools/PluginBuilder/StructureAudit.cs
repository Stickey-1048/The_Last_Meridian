using Mutagen.Bethesda.Fallout4;

namespace Tlm.PluginBuilder;

/// <summary>
/// Counts how quests are laid out in a plugin: whether stages have items,
/// whether items and objectives carry their flags subrecords, whether the
/// marker between the two condition lists is there.
///
/// Run on the game's own master file it shows what the Creation Kit always
/// writes; run on this project's plugin it shows whether we write the same.
/// It exists because the library reads back, without complaint, a quest the
/// game does not treat the same way (docs/design/VERIFY_LOG.md, 2026-11-12).
/// It compares layouts only. It says nothing about what the game does.
/// </summary>
public static class StructureAudit
{
    public sealed record Counts(
        int Quests, int QuestsWithoutMarker,
        int Stages, int StagesWithoutItems,
        int Items, int ItemsWithoutFlags,
        int Objectives, int ObjectivesWithoutFlags)
    {
        public string Describe() =>
            $"{Quests} quests ({QuestsWithoutMarker} without the condition marker); " +
            $"{Stages} stages ({StagesWithoutItems} with no item); " +
            $"{Items} stage items ({ItemsWithoutFlags} without flags); " +
            $"{Objectives} objectives ({ObjectivesWithoutFlags} without flags)";
    }

    public static Counts Count(IEnumerable<IQuestGetter> quests)
    {
        int q = 0, qNoMarker = 0, s = 0, sNoItems = 0, i = 0, iNoFlags = 0, o = 0, oNoFlags = 0;
        foreach (var quest in quests)
        {
            q++;
            if (quest.UnusedConditions == null) qNoMarker++;
            foreach (var stage in quest.Stages)
            {
                s++;
                if (stage.LogEntries.Count == 0) sNoItems++;
                foreach (var item in stage.LogEntries)
                {
                    i++;
                    if (!item.Flags.HasValue) iNoFlags++;
                }
            }
            foreach (var objective in quest.Objectives)
            {
                o++;
                if (!objective.Flags.HasValue) oNoFlags++;
            }
        }
        return new Counts(q, qNoMarker, s, sNoItems, i, iNoFlags, o, oNoFlags);
    }

    /// <summary>Lines for the build output. <paramref name="master"/> may be null (no game file supplied).</summary>
    public static List<string> Compare(Counts ours, Counts? master)
    {
        var lines = new List<string> { $"this plugin: {ours.Describe()}" };
        if (master == null)
        {
            lines.Add("Fallout4.esm: not supplied, so there is nothing to compare with");
            return lines;
        }
        lines.Add($"Fallout4.esm: {master.Describe()}");

        void Line(string what, int oursMissing, int oursTotal, int masterMissing, int masterTotal)
        {
            if (oursTotal == 0) return;
            var theirs = masterTotal == 0
                ? "the game's file has none to compare with"
                : $"the game's own quests have it in {100.0 * (masterTotal - masterMissing) / masterTotal:0.##}% of cases ({masterTotal - masterMissing} of {masterTotal})";
            var mine = oursMissing == 0
                ? $"present in all {oursTotal} here"
                : $"MISSING in {oursMissing} of {oursTotal} here";
            var flag = oursMissing > 0 && masterTotal > 0 && masterMissing == 0 ? "  <-- DIFFERS from every quest in the game" : "";
            lines.Add($"{what}: {mine}; {theirs}{flag}");
        }
        Line("condition marker", ours.QuestsWithoutMarker, ours.Quests, master.QuestsWithoutMarker, master.Quests);
        Line("stage has an item", ours.StagesWithoutItems, ours.Stages, master.StagesWithoutItems, master.Stages);
        Line("item flags subrecord", ours.ItemsWithoutFlags, ours.Items, master.ItemsWithoutFlags, master.Items);
        Line("objective flags subrecord", ours.ObjectivesWithoutFlags, ours.Objectives, master.ObjectivesWithoutFlags, master.Objectives);
        return lines;
    }
}
