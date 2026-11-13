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
    /// <param name="DisplayName">The message whose title the alias's reference is shown under, if any.</param>
    public sealed record AliasInfo(int Id, string Name, string Kind, List<string> Flags, string? Fill, List<ScriptInfo> Scripts, string? DisplayName = null);
    /// <param name="Items">How many items (log entries) the stage has. The game announces a stage per item.</param>
    /// <param name="ItemsWithFlags">How many of those carry their flags subrecord (QSDT).</param>
    public sealed record StageInfo(int Index, string? Log, string? Note, bool CompleteQuest, int Items, int ItemsWithFlags);
    public sealed record ObjectiveInfo(int Index, string Text, List<int> TargetAliases, bool HasFlags);
    /// <param name="HasConditionMarker">The NEXT marker between the quest's two condition lists is present.</param>
    public sealed record QuestInfo(string EditorId, string FormKey, string? Name, string Type, int Priority, List<string> Flags,
        List<StageInfo> Stages, List<ObjectiveInfo> Objectives, List<AliasInfo> Aliases, List<ScriptInfo> Scripts, bool HasConditionMarker);
    public sealed record ButtonInfo(string Text, List<string> Conditions);
    public sealed record MessageInfo(string EditorId, string FormKey, string? Title, string? Text, bool Box, List<ButtonInfo> Buttons);
    /// <param name="Model">Path of the world model, for the kinds of record that can lie in the world. Null: none.</param>
    public sealed record SimpleInfo(string Type, string EditorId, string FormKey, string? Name, string? Model = null);
    /// <summary>A record of the game's own that the plugin points at.</summary>
    public sealed record VanillaInfo(string EditorId, string FormKey, string Kind);
    /// <summary>Where the player arrives in a cell of the game this plugin places things in. Not in the plugin file:
    /// it is what the builder read from the game's master.</summary>
    /// <param name="Found">False: the cell has no arrival marker, and the origin was used.</param>
    public sealed record ArrivalInfo(string Cell, string FormKey, float[] Position, float Heading, bool Found);
    /// <summary>A reference in a cell.</summary>
    /// <param name="Kind">PlacedNpc or PlacedObject.</param>
    /// <param name="Base">EditorID when the base is a record of this plugin, otherwise its id in the master.</param>
    /// <param name="Group">Which of the cell's two lists holds it: Persistent or Temporary.</param>
    /// <param name="Box">How far the box reaches from its middle on each axis (half its size), when the reference has a box: the numbers the file holds.</param>
    /// <param name="CollisionLayer">Index of the collision layer, when one is given.</param>
    /// <param name="Bound">The reference's bound, when it has one: for a box, the same reach again.</param>
    public sealed record PlacedInfo(string? EditorId, string FormKey, string Kind, string Base, float[] Position, float[] Rotation,
        bool Persistent, bool InitiallyDisabled, string Group, string? Primitive, float[]? Box, uint? CollisionLayer, float[]? Bound = null);
    /// <summary>A cell record in the plugin. For a cell of the game's it is this plugin's copy of the record.</summary>
    /// <param name="OfThisPlugin">False: the cell belongs to a master, and the plugin only adds to it.</param>
    /// <param name="Name">The cell's name as this plugin carries it (it replaces the master's while the plugin is loaded).</param>
    public sealed record CellInfo(string? EditorId, string FormKey, bool OfThisPlugin, int Block, int SubBlock, List<PlacedInfo> Placed, string? Name = null);
    /// <summary>An actor of this plugin's own: what it would go about its business with.</summary>
    /// <param name="TemplateFlags">What the actor takes from the actor it is modelled on.</param>
    public sealed record NpcInfo(string EditorId, string FormKey, string? Name, int Packages, bool HasDefaultPackageList,
        List<string> Scripts, List<string> TemplateFlags);
    public sealed record PluginInfo(string File, List<string> Masters, float HeaderVersion, uint LowestFormId,
        List<SimpleInfo> Records, List<MessageInfo> Messages, List<QuestInfo> Quests, List<CellInfo> Cells, List<NpcInfo> Npcs);

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
        foreach (var m in mod.MiscItems) simple.Add(new("MiscItem", m.EditorID!, m.FormKey.ToString(), m.Name?.String, NullIfEmpty(m.Model?.File)));
        foreach (var b in mod.Books) simple.Add(new("Book", b.EditorID!, b.FormKey.ToString(), b.Name?.String, NullIfEmpty(b.Model?.File)));
        foreach (var a in mod.Activators) simple.Add(new("Activator", a.EditorID!, a.FormKey.ToString(), a.Name?.String, NullIfEmpty(a.Model?.File)));
        var npcs = new List<NpcInfo>();
        foreach (var n in mod.Npcs)
        {
            simple.Add(new("Npc", n.EditorID!, n.FormKey.ToString(), n.Name?.String));
            npcs.Add(new(n.EditorID!, n.FormKey.ToString(), n.Name?.String, n.Packages.Count, !n.DefaultPackageList.IsNull,
                n.VirtualMachineAdapter?.Scripts.Select(s => s.Name).ToList() ?? new(), FlagNames(n.UseTemplateActors)));
        }

        var cells = new List<CellInfo>();
        foreach (var block in mod.Cells.Records)
            foreach (var sub in block.SubBlocks)
                foreach (var cell in sub.Cells)
                {
                    var placed = new List<PlacedInfo>();
                    foreach (var (list, name) in new[] { (cell.Persistent, "Persistent"), (cell.Temporary, "Temporary") })
                        foreach (var p in list)
                        {
                            var flags = (uint)p.MajorRecordFlagsRaw;
                            float[] V(Noggog.P3Float v) => new[] { v.X, v.Y, v.Z };
                            switch (p)
                            {
                                case IPlacedNpcGetter n:
                                    placed.Add(new(n.EditorID, n.FormKey.ToString(), "PlacedNpc", Target(n.Base.FormKey), V(n.Position), V(n.Rotation),
                                        (flags & 0x400) != 0, (flags & 0x800) != 0, name, null, null, null));
                                    break;
                                case IPlacedObjectGetter o:
                                    placed.Add(new(o.EditorID, o.FormKey.ToString(), "PlacedObject", Target(o.Base.FormKey), V(o.Position), V(o.Rotation),
                                        (flags & 0x400) != 0, (flags & 0x800) != 0, name,
                                        // The library gives the whole sizes; the file holds half of each, and so does this.
                                        o.Primitive?.Type.ToString(), o.Primitive == null ? null : V(o.Primitive.Bounds / 2), o.CollisionLayer,
                                        o.BoundHalfExtents is { } bound ? V(bound) : null));
                                    break;
                                default:
                                    placed.Add(new(p.EditorID, p.FormKey.ToString(), p.GetType().Name, "?", Array.Empty<float>(), Array.Empty<float>(),
                                        (flags & 0x400) != 0, (flags & 0x800) != 0, name, null, null, null));
                                    break;
                            }
                        }
                    cells.Add(new(cell.EditorID, cell.FormKey.ToString(), cell.FormKey.ModKey == mod.ModKey, block.BlockNumber, sub.BlockNumber, placed,
                        NullIfEmpty(cell.Name?.String)));
                }

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
                            aliasScripts.TryGetValue((int)r.ID, out var rs) ? rs : new(),
                            r.DisplayName.IsNull ? null : Target(r.DisplayName.FormKey)));
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
                    s.LogEntries.Any(e => e.Flags.HasValue && e.Flags.Value.HasFlag(QuestLogEntry.Flag.CompleteQuest)),
                    s.LogEntries.Count,
                    s.LogEntries.Count(e => e.Flags.HasValue))).ToList(),
                q.Objectives.Select(o => new ObjectiveInfo(o.Index, o.DisplayText?.String ?? "", o.Targets.Select(t => t.AliasID).ToList(), o.Flags.HasValue)).ToList(),
                aliases,
                q.VirtualMachineAdapter?.Scripts.Select(Script).ToList() ?? new(),
                q.UnusedConditions != null));
        }

        return new PluginInfo(
            Path.GetFileName(path),
            mod.ModHeader.MasterReferences.Select(m => m.Master.FileName.String).ToList(),
            mod.ModHeader.Stats.Version,
            ids.Keys.Where(k => k.ModKey == mod.ModKey).Select(k => k.ID).DefaultIfEmpty(0u).Min(),
            simple, messages, quests, cells, npcs);
    }

    static string? NullIfEmpty(string? s) => string.IsNullOrEmpty(s) ? null : s;

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
            foreach (var r in grp) sb.AppendLine($"  {r.FormKey[..6]}  {r.EditorId}{(r.Name == null ? "" : $"  \"{r.Name}\"")}{(r.Model == null ? "" : $"  model: {r.Model}")}");
        }
        foreach (var n in info.Npcs)
            sb.AppendLine($"          {n.EditorId}: {n.Packages} package(s), {(n.HasDefaultPackageList ? "a" : "no")} default package list, " +
                          $"script(s) {(n.Scripts.Count == 0 ? "none" : string.Join(", ", n.Scripts))}, from a template: {(n.TemplateFlags.Count == 0 ? "nothing" : string.Join(", ", n.TemplateFlags))}");
        sb.AppendLine($"Message ({info.Messages.Count})");
        foreach (var m in info.Messages)
        {
            sb.AppendLine($"  {m.FormKey[..6]}  {m.EditorId}  {(m.Box ? "[box]" : "[notification]")}  \"{m.Text}\"{(string.IsNullOrEmpty(m.Title) ? "" : $"  title: \"{m.Title}\"")}");
            for (var i = 0; i < m.Buttons.Count; i++)
                sb.AppendLine($"          button {i}: \"{m.Buttons[i].Text}\"{(m.Buttons[i].Conditions.Count == 0 ? "" : "  if " + string.Join(" and ", m.Buttons[i].Conditions))}");
        }
        foreach (var q in info.Quests)
        {
            sb.AppendLine();
            sb.AppendLine($"Quest {q.EditorId}  {q.FormKey[..6]}  \"{q.Name}\"  type={q.Type} priority={q.Priority} flags=[{string.Join(", ", q.Flags)}]");
            foreach (var s in q.Scripts) AppendScript(sb, "  script ", s);
            sb.AppendLine($"  structure: {q.Stages.Count(s => s.Items == 1 && s.ItemsWithFlags == 1)} of {q.Stages.Count} stages have one item with its flags subrecord; " +
                          $"{q.Objectives.Count(o => o.HasFlags)} of {q.Objectives.Count} objectives have flags; condition marker {(q.HasConditionMarker ? "present" : "MISSING")}");
            foreach (var s in q.Stages)
                sb.AppendLine($"  stage {s.Index,4}{(s.CompleteQuest ? " [complete]" : "")}{(s.Items == 1 && s.ItemsWithFlags == 1 ? "" : $" [{s.Items} item(s), {s.ItemsWithFlags} with flags]")}  {(s.Log != null ? "\"" + s.Log + "\"" : "(" + (s.Note ?? "no log") + ")")}");
            foreach (var o in q.Objectives)
                sb.AppendLine($"  objective {o.Index}: \"{o.Text}\"{(o.TargetAliases.Count == 0 ? "" : "  -> alias " + string.Join(",", o.TargetAliases))}");
            foreach (var a in q.Aliases)
            {
                sb.AppendLine($"  alias {a.Id,2} {a.Name}  ({a.Kind}) [{string.Join(", ", a.Flags)}]{(a.Fill == null ? "" : "  fill: " + a.Fill)}{(a.DisplayName == null ? "" : "  shown as: " + a.DisplayName)}");
                foreach (var s in a.Scripts) AppendScript(sb, "           script ", s);
            }
        }
        foreach (var c in info.Cells)
        {
            sb.AppendLine();
            sb.AppendLine($"Cell {c.EditorId ?? "(no EditorID)"}  {c.FormKey}  {(c.OfThisPlugin ? "of this plugin" : "of the game: this plugin's copy of its record, with what the plugin adds")}  block {c.Block}, sub-block {c.SubBlock}  name: {(c.Name == null ? "none" : "\"" + c.Name + "\"")}");
            foreach (var p in c.Placed)
            {
                var flags = new List<string>();
                if (p.Persistent) flags.Add("Persistent");
                if (p.InitiallyDisabled) flags.Add("InitiallyDisabled");
                string Vec(float[] v) => "(" + string.Join(", ", v.Select(x => x.ToString("0.#", System.Globalization.CultureInfo.InvariantCulture))) + ")";
                sb.AppendLine($"  {p.FormKey[..6]}  {p.EditorId ?? "(no EditorID)"}  {p.Kind} of {p.Base}  at {Vec(p.Position)} turned {Vec(p.Rotation.Select(r => r * 180 / MathF.PI).ToArray())}  [{string.Join(", ", flags)}]  in the {p.Group} list"
                    + (p.Primitive == null ? "" : $"  {p.Primitive} {Vec(p.Box!)}")
                    + (p.Bound == null ? "" : $"  bound {Vec(p.Bound)}")
                    + (p.CollisionLayer == null ? "" : $"  collision layer {p.CollisionLayer}"));
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
