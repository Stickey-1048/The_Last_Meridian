using Mutagen.Bethesda;
using Mutagen.Bethesda.Fallout4;
using Mutagen.Bethesda.Plugins;
using Mutagen.Bethesda.Plugins.Allocators;
using Mutagen.Bethesda.Plugins.Cache;
using Mutagen.Bethesda.Plugins.Records;
using Noggog;

namespace Tlm.PluginBuilder;

/// <summary>
/// Builds TheLastMeridian.esp from <see cref="Spec"/>.
///
/// Two modes:
///  - skeleton (no Fallout4.esm given): every record that lives entirely in
///    this plugin is built. Anything needing a vanilla record or a placed
///    reference is skipped and listed in <see cref="Pending"/>.
///  - full (Fallout4.esm given): vanilla records are resolved by EditorID from
///    the real master. No FormID is hard-coded anywhere.
///
/// The output of either mode has NOT been loaded in the Creation Kit or the
/// game unless docs/design/BUILD_ENV.md says so.
/// </summary>
public sealed class Builder
{
    public static readonly ModKey Fallout4Esm = ModKey.FromNameAndExtension("Fallout4.esm");

    readonly Fallout4Mod _mod;
    readonly ILinkCache? _vanilla;
    readonly Dictionary<string, IFallout4MajorRecordGetter> _byId = new(StringComparer.OrdinalIgnoreCase);

    /// <summary>Things this build could not wire, with the reason.</summary>
    public List<string> Pending { get; } = new();

    public Fallout4Mod Mod => _mod;

    public Builder(Fallout4Mod mod, ILinkCache? vanilla)
    {
        _mod = mod;
        _vanilla = vanilla;
    }

    public void Build()
    {
        foreach (var id in Spec.Globals)
        {
            var g = _mod.Globals.AddNewShort(id);
            g.EditorID = id;        // AddNewShort uses the id for allocation only
            g.Data = 0;
            Track(g);
        }

        foreach (var id in Spec.Factions)
        {
            var f = _mod.Factions.AddNew(id);
            if (id == "TLM_Fac_Caravan") f.Flags = Faction.FactionFlag.CanBeOwner;
            Track(f);
        }

        foreach (var m in Spec.MiscItems)
        {
            var item = _mod.MiscItems.AddNew(m.EditorId);
            item.Name = m.Name;
            Track(item);
            Pending.Add($"{m.EditorId}: no world model yet (it exists only in inventories until one is assigned)");
        }

        foreach (var b in Spec.Books)
        {
            var book = _mod.Books.AddNew(b.EditorId);
            book.Name = b.Name;
            book.BookText = b.Text;
            Track(book);
            Pending.Add($"{b.EditorId}: no world model yet");
        }

        // Quests are created before messages and scripts are bound, because
        // conditions and properties refer to them.
        var quests = new Dictionary<string, Quest>();
        foreach (var q in Spec.Quests)
        {
            var quest = _mod.Quests.AddNew(q.EditorId);
            quests[q.EditorId] = quest;
            Track(quest);
        }

        foreach (var m in Spec.Messages)
        {
            var msg = _mod.Messages.AddNew(m.EditorId);
            if (m.Title != null) msg.Name = m.Title;
            msg.Description = m.Text;
            if (m.Box) msg.Flags = Message.Flag.MessageBox;
            foreach (var b in m.Buttons)
            {
                var button = new MessageButton { Text = b.Text };
                foreach (var c in b.Conditions) button.Conditions.Add(ToCondition(c));
                msg.MenuButtons.Add(button);
            }
            Track(msg);
        }

        foreach (var q in Spec.Quests) Fill(quests[q.EditorId], q);
    }

    void Track(IFallout4MajorRecordGetter rec)
    {
        _byId.Add(rec.EditorID ?? throw new InvalidOperationException("record without EditorID"), rec);
    }

    IFallout4MajorRecordGetter Local(string editorId) =>
        _byId.TryGetValue(editorId, out var rec)
            ? rec
            : throw new InvalidOperationException($"Spec refers to '{editorId}', which this plugin does not define");

    Condition ToCondition(Cond c)
    {
        switch (c)
        {
            case StageDone sd:
                return new ConditionFloat
                {
                    CompareOperator = CompareOperator.EqualTo,
                    ComparisonValue = sd.Done ? 1 : 0,
                    Data = new FunctionConditionData
                    {
                        Function = Condition.Function.GetStageDone,
                        ParameterOneRecord = Local(sd.Quest).ToLink<IFallout4MajorRecordGetter>(),
                        ParameterTwoNumber = sd.Stage,
                    },
                };
            case GlobalAtLeast ge:
                return GlobalCondition(ge.Global, CompareOperator.GreaterThanOrEqualTo, ge.Value);
            case GlobalEquals eq:
                return GlobalCondition(eq.Global, CompareOperator.EqualTo, eq.Value);
            default:
                throw new NotSupportedException(c.GetType().Name);
        }
    }

    Condition GlobalCondition(string global, CompareOperator op, float value) => new ConditionFloat
    {
        CompareOperator = op,
        ComparisonValue = value,
        Data = new FunctionConditionData
        {
            Function = Condition.Function.GetGlobalValue,
            ParameterOneRecord = Local(global).ToLink<IFallout4MajorRecordGetter>(),
        },
    };

    void Fill(Quest quest, QuestSpec spec)
    {
        quest.Name = spec.Name;
        var flags = Quest.Flag.RunOnce | Quest.Flag.WarnOnAliasFillFailure;
        if (spec.StartGameEnabled) flags |= Quest.Flag.StartGameEnabled;
        quest.Data = new QuestData
        {
            Flags = flags,
            Priority = spec.Priority,
            Type = Enum.Parse<Quest.TypeEnum>(spec.Type),
        };

        foreach (var s in spec.Stages)
        {
            var stage = new QuestStage { Index = checked((ushort)s.Index) };
            if (s.Log != null || s.CompleteQuest || s.Note != null)
            {
                var entry = new QuestLogEntry();
                if (s.Log != null) entry.Entry = s.Log;
                if (s.Note != null) entry.Note = s.Note;
                if (s.CompleteQuest) entry.Flags = QuestLogEntry.Flag.CompleteQuest;
                stage.LogEntries.Add(entry);
            }
            quest.Stages.Add(stage);
        }

        var aliasIds = new Dictionary<string, int>(StringComparer.OrdinalIgnoreCase);
        for (var i = 0; i < spec.Aliases.Length; i++) aliasIds.Add(spec.Aliases[i].Name, i);

        int AliasId(string name) => aliasIds.TryGetValue(name, out var id)
            ? id
            : throw new InvalidOperationException($"{spec.EditorId}: no alias named '{name}'");

        foreach (var o in spec.Objectives)
        {
            var objective = new QuestObjective { Index = checked((ushort)o.Index), DisplayText = o.Text };
            if (o.TargetAlias != null)
                objective.Targets.Add(new QuestObjectiveTarget { AliasID = AliasId(o.TargetAlias) });
            quest.Objectives.Add(objective);
        }

        var adapter = new QuestAdapter();
        if (spec.Script != null) adapter.Scripts.Add(ToScript(spec.Script, quest, spec, AliasId));

        if (spec.Aliases.Length > 0) quest.Aliases = new ExtendedList<AQuestAlias>();
        foreach (var a in spec.Aliases)
        {
            var id = AliasId(a.Name);
            var aliasFlags = default(AQuestAlias.Flag);
            if (a.QuestObject) aliasFlags |= AQuestAlias.Flag.QuestObject;
            if (a.Essential) aliasFlags |= AQuestAlias.Flag.Essential;
            if (a.Protected) aliasFlags |= AQuestAlias.Flag.Protected;
            if (a.AllowDead) aliasFlags |= AQuestAlias.Flag.AllowDead;
            if (a.AllowDisabled) aliasFlags |= AQuestAlias.Flag.AllowDisabled;

            if (a.IsLocation)
            {
                aliasFlags |= AQuestAlias.Flag.Optional;
                Pending.Add($"{spec.EditorId} alias {a.Name}: location not created yet ({a.Note})");
                quest.Aliases!.Add(new QuestLocationAlias { ID = (uint)id, Name = a.Name, Flags = aliasFlags });
                continue;
            }

            var alias = new QuestReferenceAlias { ID = (uint)id, Name = a.Name };
            switch (a.Fill)
            {
                case Tlm.PluginBuilder.Fill.CreateIn:
                    alias.CreateReferenceToObject = new CreateReferenceToObject
                    {
                        Object = Local(a.CreateItem!).ToLink<IFallout4MajorRecordGetter>(),
                        AliasID = checked((short)AliasId(a.CreateInAlias!)),
                        Create = CreateReferenceToObject.CreateEnum.In,
                    };
                    // The container alias is still Pending, so this one cannot
                    // be mandatory yet either.
                    aliasFlags |= AQuestAlias.Flag.Optional;
                    break;
                case Tlm.PluginBuilder.Fill.ScriptFilled:
                    aliasFlags |= AQuestAlias.Flag.Optional;
                    break;
                case Tlm.PluginBuilder.Fill.Player:
                    if (!TryFillPlayer(alias))
                    {
                        aliasFlags |= AQuestAlias.Flag.Optional;
                        Pending.Add($"{spec.EditorId} alias {a.Name}: needs PlayerRef from Fallout4.esm");
                    }
                    break;
                default:
                    aliasFlags |= AQuestAlias.Flag.Optional;
                    Pending.Add($"{spec.EditorId} alias {a.Name}: no reference yet ({a.Note ?? "placed in the test cell"})");
                    break;
            }
            alias.Flags = aliasFlags;
            quest.Aliases!.Add(alias);

            if (a.Scripts.Length > 0)
            {
                var entry = new QuestFragmentAlias
                {
                    Property = new ScriptObjectProperty
                    {
                        Object = quest.ToLink<IFallout4MajorRecordGetter>(),
                        Alias = checked((short)id),
                    },
                };
                foreach (var s in a.Scripts) entry.Scripts.Add(ToScript(s, quest, spec, AliasId));
                adapter.Aliases.Add(entry);
            }
        }

        if (adapter.Scripts.Count > 0 || adapter.Aliases.Count > 0) quest.VirtualMachineAdapter = adapter;
    }

    ScriptEntry ToScript(ScriptBind bind, Quest quest, QuestSpec spec, Func<string, int> aliasId)
    {
        var entry = new ScriptEntry { Name = bind.Script };
        foreach (var p in bind.Props)
        {
            switch (p)
            {
                case IntProp ip:
                    entry.Properties.Add(new ScriptIntProperty { Name = ip.Name, Flags = ScriptProperty.Flag.Edited, Data = ip.Value });
                    break;
                case BoolProp bp:
                    entry.Properties.Add(new ScriptBoolProperty { Name = bp.Name, Flags = ScriptProperty.Flag.Edited, Data = bp.Value });
                    break;
                case IntListProp lp:
                    var list = new ScriptIntListProperty { Name = lp.Name, Flags = ScriptProperty.Flag.Edited };
                    list.Data.AddRange(lp.Values);
                    entry.Properties.Add(list);
                    break;
                case FormProp fp:
                    entry.Properties.Add(new ScriptObjectProperty
                    {
                        Name = fp.Name,
                        Flags = ScriptProperty.Flag.Edited,
                        Object = Local(fp.EditorId).ToLink<IFallout4MajorRecordGetter>(),
                        Alias = -1,
                    });
                    break;
                case AliasProp ap:
                    entry.Properties.Add(new ScriptObjectProperty
                    {
                        Name = ap.Name,
                        Flags = ScriptProperty.Flag.Edited,
                        Object = quest.ToLink<IFallout4MajorRecordGetter>(),
                        Alias = checked((short)aliasId(ap.Alias)),
                    });
                    break;
                case VanillaProp vp:
                    if (TryVanilla(vp.EditorId, out var key))
                    {
                        entry.Properties.Add(new ScriptObjectProperty
                        {
                            Name = vp.Name,
                            Flags = ScriptProperty.Flag.Edited,
                            Object = new FormLink<IFallout4MajorRecordGetter>(key),
                            Alias = -1,
                        });
                    }
                    else
                    {
                        Pending.Add($"{spec.EditorId} script {bind.Script}.{vp.Name}: needs '{vp.EditorId}' from Fallout4.esm");
                    }
                    break;
                default:
                    throw new NotSupportedException(p.GetType().Name);
            }
        }
        return entry;
    }

    // ----------------------------------------------------- vanilla lookups
    // UNTESTED: these paths only run when Fallout4.esm is supplied, which has
    // not happened yet (see docs/design/BUILD_ENV.md once it exists).

    bool TryVanilla(string editorId, out FormKey key)
    {
        key = FormKey.Null;
        if (_vanilla == null) return false;
        if (!_vanilla.TryResolveIdentifier(editorId, out var found)) return false;
        key = found;
        return true;
    }

    bool TryFillPlayer(QuestReferenceAlias alias)
    {
        if (!TryVanilla("PlayerRef", out var key)) return false;
        alias.ForcedReference = new FormLinkNullable<IPlacedGetter>(key);
        return true;
    }

    // ------------------------------------------------------------ factory

    public static (Fallout4Mod mod, Builder builder) Create(string formKeyFile, string? fallout4Esm)
    {
        var mod = new Fallout4Mod(ModKey.FromNameAndExtension(Spec.PluginName), Fallout4Release.Fallout4);
        ILinkCache? vanilla = null;
        if (fallout4Esm != null)
        {
            var master = Fallout4Mod.CreateFromBinaryOverlay(fallout4Esm, Fallout4Release.Fallout4);
            vanilla = master.ToImmutableLinkCache();
        }

        // EditorID -> FormID assignments are kept in a text file under version
        // control, so rebuilding never renumbers existing records.
        using var allocator = new TextFileFormKeyAllocator(mod, formKeyFile);
        mod.SetAllocator(allocator);
        var builder = new Builder(mod, vanilla);
        builder.Build();
        allocator.Commit();
        return (mod, builder);
    }

    public static void Write(Fallout4Mod mod, string path)
    {
        Directory.CreateDirectory(Path.GetDirectoryName(Path.GetFullPath(path))!);
        mod.BeginWrite
            .ToPath(path)
            .WithNoLoadOrder()
            .WithExtraIncludedMasters(Fallout4Esm)
            .Write();
    }
}
