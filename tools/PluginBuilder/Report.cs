using System.Text;
using System.Text.Json;
using Mutagen.Bethesda;
using Mutagen.Bethesda.Fallout4;
using Mutagen.Bethesda.Plugins;
using Mutagen.Bethesda.Plugins.Records;

namespace Tlm.PluginBuilder;

/// <summary>
/// Reads a written plugin back from disk and describes what is in it.
/// The JSON form is what tools/check_consistency.py compares against the
/// Papyrus sources and the logic model.
/// </summary>
public static class Report
{
    public sealed record PropInfo(string Name, string Kind, string? Target, int? Alias, object? Value);
    public sealed record ScriptInfo(string Name, List<PropInfo> Props);
    public sealed record AliasInfo(int Id, string Name, string Kind, List<string> Flags, string? Fill, List<ScriptInfo> Scripts);
    public sealed record StageInfo(int Index, string? Log, string? Note, bool CompleteQuest);
    public sealed record ObjectiveInfo(int Index, string Text, List<int> TargetAliases);
    public sealed record QuestInfo(string EditorId, string FormKey, string? Name, string Type, int Priority, List<string> Flags,
        List<StageInfo> Stages, List<ObjectiveInfo> Objectives, List<AliasInfo> Aliases, List<ScriptInfo> Scripts);
    public sealed record ButtonInfo(string Text, List<string> Conditions);
    public sealed record MessageInfo(string EditorId, string FormKey, string? Title, string? Text, bool Box, List<ButtonInfo> Buttons);
    public sealed record SimpleInfo(string Type, string EditorId, string FormKey, string? Name);
    public sealed record PluginInfo(string File, List<string> Masters, float HeaderVersion, uint LowestFormId,
        List<SimpleInfo> Records, List<MessageInfo> Messages, List<QuestInfo> Quests);

    public static PluginInfo Read(string path)
    {
        using var mod = Fallout4Mod.CreateFromBinaryOverlay(path, Fallout4Release.Fallout4);
        var ids = new Dictionary<FormKey, string>();
        foreach (var rec in mod.EnumerateMajorRecords())
            if (rec.EditorID != null) ids[rec.FormKey] = rec.EditorID;

        string Target(FormKey key) => ids.TryGetValue(key, out var id) ? id : key.ToString();

        ScriptInfo Script(IScriptEntryGetter s) => new(s.Name, s.Properties.Select(p => p switch
        {
            IScriptObjectPropertyGetter o => new PropInfo(p.Name, "object", Target(o.Object.FormKey), o.Alias < 0 ? null : o.Alias, null),
            IScriptIntPropertyGetter i => new PropInfo(p.Name, "int", null, null, i.Data),
            IScriptBoolPropertyGetter b => new PropInfo(p.Name, "bool", null, null, b.Data),
            IScriptFloatPropertyGetter f => new PropInfo(p.Name, "float", null, null, f.Data),
            IScriptIntListPropertyGetter l => new PropInfo(p.Name, "int[]", null, null, l.Data.ToArray()),
            _ => new PropInfo(p.Name, p.GetType().Name, null, null, null),
        }).ToList());

        var simple = new List<SimpleInfo>();
        foreach (var g in mod.Globals) simple.Add(new("Global", g.EditorID!, g.FormKey.ToString(), null));
        foreach (var f in mod.Factions) simple.Add(new("Faction", f.EditorID!, f.FormKey.ToString(), f.Name?.String));
        foreach (var m in mod.MiscItems) simple.Add(new("MiscItem", m.EditorID!, m.FormKey.ToString(), m.Name?.String));
        foreach (var b in mod.Books) simple.Add(new("Book", b.EditorID!, b.FormKey.ToString(), b.Name?.String));

        var messages = mod.Messages.Select(m => new MessageInfo(
            m.EditorID!, m.FormKey.ToString(), m.Name?.String, m.Description?.String,
            m.Flags.HasFlag(Message.Flag.MessageBox),
            m.MenuButtons.Select(b => new ButtonInfo(b.Text?.String ?? "", b.Conditions.Select(c => Describe(c, Target)).ToList())).ToList())).ToList();

        var quests = new List<QuestInfo>();
        foreach (var q in mod.Quests)
        {
            var aliasScripts = new Dictionary<int, List<ScriptInfo>>();
            if (q.VirtualMachineAdapter != null)
                foreach (var a in q.VirtualMachineAdapter.Aliases)
                    aliasScripts[a.Property.Alias] = a.Scripts.Select(Script).ToList();

            var aliases = new List<AliasInfo>();
            foreach (var a in q.Aliases ?? Array.Empty<IAQuestAliasGetter>())
            {
                switch (a)
                {
                    case IQuestReferenceAliasGetter r:
                        string? fill = null;
                        if (r.CreateReferenceToObject != null)
                            fill = $"create {Target(r.CreateReferenceToObject.Object.FormKey)} {r.CreateReferenceToObject.Create} alias {r.CreateReferenceToObject.AliasID}";
                        else if (!r.ForcedReference.IsNull) fill = $"forced {r.ForcedReference.FormKey}";
                        else if (!r.UniqueActor.IsNull) fill = $"unique {Target(r.UniqueActor.FormKey)}";
                        aliases.Add(new((int)r.ID, r.Name ?? "", "reference", FlagNames(r.Flags), fill,
                            aliasScripts.TryGetValue((int)r.ID, out var rs) ? rs : new()));
                        break;
                    case IQuestLocationAliasGetter l:
                        aliases.Add(new((int)l.ID, l.Name ?? "", "location", FlagNames(l.Flags), null, new()));
                        break;
                }
            }

            quests.Add(new QuestInfo(
                q.EditorID!, q.FormKey.ToString(), q.Name?.String,
                q.Data?.Type.ToString() ?? "", q.Data?.Priority ?? 0,
                q.Data == null ? new() : FlagNames(q.Data.Flags),
                q.Stages.Select(s => new StageInfo(
                    s.Index,
                    s.LogEntries.Select(e => e.Entry?.String).FirstOrDefault(e => !string.IsNullOrEmpty(e)),
                    s.LogEntries.Select(e => e.Note).FirstOrDefault(n => !string.IsNullOrEmpty(n)),
                    s.LogEntries.Any(e => e.Flags.HasValue && e.Flags.Value.HasFlag(QuestLogEntry.Flag.CompleteQuest)))).ToList(),
                q.Objectives.Select(o => new ObjectiveInfo(o.Index, o.DisplayText?.String ?? "", o.Targets.Select(t => t.AliasID).ToList())).ToList(),
                aliases,
                q.VirtualMachineAdapter?.Scripts.Select(Script).ToList() ?? new()));
        }

        return new PluginInfo(
            Path.GetFileName(path),
            mod.ModHeader.MasterReferences.Select(m => m.Master.FileName.String).ToList(),
            mod.ModHeader.Stats.Version,
            ids.Keys.Where(k => k.ModKey == mod.ModKey).Select(k => k.ID).DefaultIfEmpty(0u).Min(),
            simple, messages, quests);
    }

    static List<string> FlagNames<T>(T? flags) where T : struct, Enum =>
        flags.HasValue ? FlagNames(flags.Value) : new();

    static List<string> FlagNames<T>(T flags) where T : struct, Enum =>
        Enum.GetValues<T>().Where(v => Convert.ToInt64(v) != 0 && flags.HasFlag(v)).Select(v => v.ToString()).ToList();

    static string Describe(IConditionGetter c, Func<FormKey, string> target)
    {
        var value = c is IConditionFloatGetter f ? f.ComparisonValue.ToString("0.##") : "?";
        if (c.Data is IFunctionConditionDataGetter fn)
        {
            var p1 = fn.ParameterOneRecord.IsNull ? "" : target(fn.ParameterOneRecord.FormKey);
            var p2 = fn.Function == Condition.Function.GetStageDone ? " " + fn.ParameterTwoNumber : "";
            return $"{fn.Function} {p1}{p2} {c.CompareOperator} {value}";
        }
        return c.Data.GetType().Name;
    }

    public static string ToJson(PluginInfo info) =>
        JsonSerializer.Serialize(info, new JsonSerializerOptions { WriteIndented = true });

    public static string ToText(PluginInfo info, IEnumerable<string> pending, IEnumerable<string>? vanillaNotes = null)
    {
        var sb = new StringBuilder();
        sb.AppendLine($"{info.File}  (masters: {string.Join(", ", info.Masters)}; header version {info.HeaderVersion:0.00}; lowest FormID 0x{info.LowestFormId:X})");
        sb.AppendLine();
        foreach (var grp in info.Records.GroupBy(r => r.Type))
        {
            sb.AppendLine($"{grp.Key} ({grp.Count()})");
            foreach (var r in grp) sb.AppendLine($"  {r.FormKey[..6]}  {r.EditorId}{(r.Name == null ? "" : $"  \"{r.Name}\"")}");
        }
        sb.AppendLine($"Message ({info.Messages.Count})");
        foreach (var m in info.Messages)
        {
            sb.AppendLine($"  {m.FormKey[..6]}  {m.EditorId}  {(m.Box ? "[box]" : "[notification]")}  \"{m.Text}\"");
            for (var i = 0; i < m.Buttons.Count; i++)
                sb.AppendLine($"          button {i}: \"{m.Buttons[i].Text}\"{(m.Buttons[i].Conditions.Count == 0 ? "" : "  if " + string.Join(" and ", m.Buttons[i].Conditions))}");
        }
        foreach (var q in info.Quests)
        {
            sb.AppendLine();
            sb.AppendLine($"Quest {q.EditorId}  {q.FormKey[..6]}  \"{q.Name}\"  type={q.Type} priority={q.Priority} flags=[{string.Join(", ", q.Flags)}]");
            foreach (var s in q.Scripts) AppendScript(sb, "  script ", s);
            foreach (var s in q.Stages)
                sb.AppendLine($"  stage {s.Index,4}{(s.CompleteQuest ? " [complete]" : "")}  {(s.Log != null ? "\"" + s.Log + "\"" : "(" + (s.Note ?? "no log") + ")")}");
            foreach (var o in q.Objectives)
                sb.AppendLine($"  objective {o.Index}: \"{o.Text}\"{(o.TargetAliases.Count == 0 ? "" : "  -> alias " + string.Join(",", o.TargetAliases))}");
            foreach (var a in q.Aliases)
            {
                sb.AppendLine($"  alias {a.Id,2} {a.Name}  ({a.Kind}) [{string.Join(", ", a.Flags)}]{(a.Fill == null ? "" : "  fill: " + a.Fill)}");
                foreach (var s in a.Scripts) AppendScript(sb, "           script ", s);
            }
        }
        var notes = (vanillaNotes ?? Enumerable.Empty<string>()).ToList();
        if (notes.Count > 0)
        {
            sb.AppendLine();
            sb.AppendLine($"Lookups in Fallout4.esm ({notes.Count}):");
            foreach (var n in notes) sb.AppendLine("  - " + n);
        }

        var list = pending.ToList();
        sb.AppendLine();
        sb.AppendLine($"Not wired yet ({list.Count}):");
        foreach (var p in list) sb.AppendLine("  - " + p);
        return sb.ToString();
    }

    static void AppendScript(StringBuilder sb, string indent, ScriptInfo s)
    {
        sb.AppendLine($"{indent}{s.Name}");
        foreach (var p in s.Props)
        {
            var v = p.Kind switch
            {
                "object" => p.Alias.HasValue ? $"alias {p.Alias} on {p.Target}" : p.Target,
                "int[]" => "[" + string.Join(", ", ((IEnumerable<int>)p.Value!)) + "]",
                _ => Convert.ToString(p.Value),
            };
            sb.AppendLine($"{new string(' ', indent.Length + 2)}{p.Name} = {v}");
        }
    }
}
