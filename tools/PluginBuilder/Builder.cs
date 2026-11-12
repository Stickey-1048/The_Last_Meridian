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
    readonly IFallout4ModGetter? _vanillaMod;
    readonly Dictionary<string, IFallout4MajorRecordGetter> _byId = new(StringComparer.OrdinalIgnoreCase);

    /// <summary>Things this build could not wire, with the reason.</summary>
    public List<string> Pending { get; } = new();

    /// <summary>
    /// What each lookup in Fallout4.esm actually returned: the id asked for,
    /// the record found, and the EditorID as the master spells it.
    /// </summary>
    public List<string> VanillaNotes { get; } = new();
    /// <summary>Game records found in Fallout4.esm: the name asked for, the record, and its kind.</summary>
    public List<Report.VanillaInfo> VanillaFound { get; } = new();

    public Fallout4Mod Mod => _mod;

    public Builder(Fallout4Mod mod, ILinkCache? vanilla, IFallout4ModGetter? vanillaMod = null)
    {
        _mod = mod;
        _vanilla = vanilla;
        _vanillaMod = vanillaMod;
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
            // A message that is not a box is a line on the HUD, and the Creation
            // Kit stores how long it stays (2 seconds unless changed). Boxes
            // carry no display time.
            else msg.DisplayTime = 2;
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

        // The Creation Kit writes a marker subrecord (NEXT) between the quest's
        // two condition lists even when both are empty. The library writes it
        // only when this list exists.
        quest.UnusedConditions = new ExtendedList<Condition>();

        foreach (var s in spec.Stages)
        {
            var stage = new QuestStage { Index = checked((ushort)s.Index) };
            // Every stage gets exactly one item (the Creation Kit calls it a log
            // entry), and every item gets its flags subrecord (QSDT) even when
            // the flags are zero: that subrecord is what starts an item in the
            // file. Seen in the game on 2026-11-12: with no QSDT the stages
            // could be set, but no OnStageSet event reached the quest's script.
            // The event carries a stage id and an item id, so a stage without
            // an item has nothing to announce.
            var entry = new QuestLogEntry
            {
                Flags = s.CompleteQuest ? QuestLogEntry.Flag.CompleteQuest : default(QuestLogEntry.Flag),
            };
            if (s.Log != null) entry.Entry = s.Log;
            if (s.Note != null) entry.Note = s.Note;
            stage.LogEntries.Add(entry);
            quest.Stages.Add(stage);
        }

        var aliasIds = new Dictionary<string, int>(StringComparer.OrdinalIgnoreCase);
        for (var i = 0; i < spec.Aliases.Length; i++) aliasIds.Add(spec.Aliases[i].Name, i);

        int AliasId(string name) => aliasIds.TryGetValue(name, out var id)
            ? id
            : throw new InvalidOperationException($"{spec.EditorId}: no alias named '{name}'");

        foreach (var o in spec.Objectives)
        {
            // Flags are written even when zero, as the Creation Kit does.
            var objective = new QuestObjective { Index = checked((ushort)o.Index), Flags = default(QuestObjective.Flag), DisplayText = o.Text };
            if (o.TargetAlias != null)
                objective.Targets.Add(new QuestObjectiveTarget { AliasID = AliasId(o.TargetAlias) });
            quest.Objectives.Add(objective);
        }

        var adapter = new QuestAdapter();
        foreach (var script in spec.AllScripts()) adapter.Scripts.Add(ToScript(script, quest, spec, AliasId));

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
                    if (TryVanilla(vp.EditorId, vp.Kind, out var key))
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
    // These run only when Fallout4.esm is supplied. First run against the real
    // master: 2026-11-11 (Caps001 resolved; PlayerRef did not, which is why
    // the lookups below no longer depend on letter case).
    //
    // Mutagen's untyped lookup by EditorID is case-sensitive; its typed lookup
    // is not. The master does not always spell an EditorID the way the wiki or
    // older games do, so every lookup here ends in a typed, case-insensitive
    // one and reports the spelling the master actually uses.

    delegate bool TypedLookup(ILinkCache cache, string editorId, out FormKey key, out string? actual);

    static bool Typed<T>(ILinkCache cache, string editorId, out FormKey key, out string? actual)
        where T : class, IFallout4MajorRecordGetter
    {
        actual = null;
        if (!cache.TryResolveIdentifier<T>(editorId, out key)) return false;
        if (cache.TryResolve<T>(key, out var rec)) actual = rec.EditorID;
        return true;
    }

    // Cheap, small record types first; placed references last (there are
    // hundreds of thousands of them, so indexing them is slow).
    static readonly (string Kind, TypedLookup Lookup)[] TypedLookups =
    {
        ("MiscItem", Typed<IMiscItemGetter>),
        ("Global", Typed<IGlobalGetter>),
        ("Keyword", Typed<IKeywordGetter>),
        ("Faction", Typed<IFactionGetter>),
        ("ActorValue", Typed<IActorValueInformationGetter>),
        ("Race", Typed<IRaceGetter>),
        ("VoiceType", Typed<IVoiceTypeGetter>),
        ("Message", Typed<IMessageGetter>),
        ("FormList", Typed<IFormListGetter>),
        ("Weapon", Typed<IWeaponGetter>),
        ("Ammunition", Typed<IAmmunitionGetter>),
        ("Armor", Typed<IArmorGetter>),
        ("Book", Typed<IBookGetter>),
        ("LeveledItem", Typed<ILeveledItemGetter>),
        ("Container", Typed<IContainerGetter>),
        ("Activator", Typed<IActivatorGetter>),
        ("Static", Typed<IStaticGetter>),
        ("Furniture", Typed<IFurnitureGetter>),
        ("Npc", Typed<INpcGetter>),
        ("Package", Typed<IPackageGetter>),
        ("Quest", Typed<IQuestGetter>),
        ("Location", Typed<ILocationGetter>),
        ("Cell", Typed<ICellGetter>),
        ("Worldspace", Typed<IWorldspaceGetter>),
        ("PlacedNpc", Typed<IPlacedNpcGetter>),
        ("PlacedObject", Typed<IPlacedObjectGetter>),
    };

    /// <param name="kind">Record kind to look in, or null to try every kind.</param>
    bool TryVanilla(string editorId, string? kind, out FormKey key)
    {
        key = FormKey.Null;
        if (_vanilla == null) return false;
        foreach (var (name, lookup) in TypedLookups)
        {
            if (kind != null && !string.Equals(kind, name, StringComparison.OrdinalIgnoreCase)) continue;
            if (!lookup(_vanilla, editorId, out var found, out var actual)) continue;
            key = found;
            var spelled = actual == null || actual == editorId ? "" : $", which the master spells '{actual}'";
            VanillaNotes.Add($"{editorId} -> {found} ({name}{spelled})");
            if (!VanillaFound.Any(v => v.FormKey == found.ToString())) VanillaFound.Add(new(editorId, found.ToString(), name));
            return true;
        }
        if (kind != null && !TypedLookups.Any(t => string.Equals(t.Kind, kind, StringComparison.OrdinalIgnoreCase)))
            throw new InvalidOperationException($"Spec asks for vanilla record kind '{kind}', which the builder does not know");
        VanillaNotes.Add($"{editorId} -> NOT FOUND in Fallout4.esm{(kind == null ? "" : $" as {kind}")}");
        return false;
    }

    /// <summary>
    /// Fills the player alias with the player's reference.
    ///
    /// A wrong reference here would be a quiet, nasty bug, so a candidate is
    /// only used when the master itself vouches for it, in one of two ways:
    ///   (a) the record is visible and places the actor called "Player"; or
    ///   (b) the game's own quests force that same reference into aliases
    ///       named like "Player". On the real master (1.10.163) the library
    ///       could not see the record at all, so (a) alone was not enough.
    /// </summary>
    bool TryFillPlayer(QuestReferenceAlias alias)
    {
        if (_vanilla == null) return false;
        if (!TryVanilla("PlayerRef", "PlacedNpc", out var key))
        {
            // The player reference has carried the id 0x14 in every game on
            // this engine. Here it is only a candidate; the checks decide.
            key = new FormKey(Fallout4Esm, 0x14);
            VanillaNotes.Add($"PlayerRef: no EditorID matched; trying the conventional id {key}");
        }

        // (a) the record itself
        if (_vanilla.TryResolve<IPlacedNpcGetter>(key, out var placed))
        {
            if (_vanilla.TryResolve<INpcGetter>(placed.Base.FormKey, out var baseNpc)
                && string.Equals(baseNpc.EditorID, "Player", StringComparison.OrdinalIgnoreCase))
            {
                VanillaNotes.Add($"PlayerRef: {key} places actor '{baseNpc.EditorID}' ({baseNpc.FormKey}); accepted");
                alias.ForcedReference = new FormLinkNullable<IPlacedGetter>(key);
                NotePlayer(key);
                return true;
            }
            VanillaNotes.Add($"PlayerRef: {key} is a placed actor but does not place the actor 'Player' (its base is {placed.Base.FormKey}); not used");
            return false;
        }
        VanillaNotes.Add($"PlayerRef: {key} is not visible as a placed actor in the master");

        // (b) what the game's own quests do with it
        if (_vanillaMod != null)
        {
            var forced = 0;
            var namedPlayer = 0;
            string? example = null;
            foreach (var quest in _vanillaMod.Quests)
            {
                foreach (var a in quest.Aliases ?? Array.Empty<IAQuestAliasGetter>())
                {
                    if (a is not IQuestReferenceAliasGetter r || r.ForcedReference.FormKey != key) continue;
                    forced++;
                    if ((r.Name ?? "").Contains("player", StringComparison.OrdinalIgnoreCase))
                    {
                        namedPlayer++;
                        example ??= $"{quest.EditorID} alias '{r.Name}'";
                    }
                }
            }
            const int enough = 10;
            if (namedPlayer >= enough)
            {
                VanillaNotes.Add($"PlayerRef: {forced} vanilla quest aliases force {key}, {namedPlayer} of them named like 'Player' (e.g. {example}); accepted");
                alias.ForcedReference = new FormLinkNullable<IPlacedGetter>(key);
                NotePlayer(key);
                return true;
            }
            VanillaNotes.Add($"PlayerRef: only {namedPlayer} vanilla quest aliases named like 'Player' force {key} ({forced} aliases in all; {enough} needed); not used");
        }
        return false;
    }

    /// <summary>The reference accepted as the player goes into the list of game records found, once.</summary>
    void NotePlayer(FormKey key)
    {
        VanillaFound.RemoveAll(v => v.FormKey == key.ToString());
        VanillaFound.Add(new("PlayerRef", key.ToString(), "Player"));
    }

    // ------------------------------------------------------------ factory

    /// <summary>
    /// Plugin header version. 0.95 is the original Fallout 4 value, which every
    /// game build reads. Later Creation Kit builds write 1.0; forum reports
    /// disagree on which game builds accept that, so 0.95 is the safe default.
    /// Record FormIDs start at 0x800, which is valid under either version.
    /// </summary>
    public const float DefaultHeaderVersion = 0.95f;

    public static (Fallout4Mod mod, Builder builder) Create(string formKeyFile, string? fallout4Esm, float headerVersion = DefaultHeaderVersion)
    {
        var mod = new Fallout4Mod(ModKey.FromNameAndExtension(Spec.PluginName), Fallout4Release.Fallout4);
        mod.ModHeader.Stats.Version = headerVersion;
        ILinkCache? vanilla = null;
        IFallout4ModGetter? master = null;
        if (fallout4Esm != null)
        {
            master = Fallout4Mod.CreateFromBinaryOverlay(fallout4Esm, Fallout4Release.Fallout4);
            vanilla = master.ToImmutableLinkCache();
        }

        // EditorID -> FormID assignments are kept in a text file under version
        // control, so rebuilding never renumbers existing records.
        //
        // The allocator rewrites its file on every run, in the line endings of
        // the machine it runs on. To keep a build from marking the tracked file
        // as changed (which would later block a `git pull`), it works on a
        // copy, and the tracked file is only rewritten when its content really
        // differs, line endings aside.
        //
        // "Line endings aside" matters. On a clone made before .gitattributes
        // pinned this file to LF, the working copy has CRLF. Rewriting it only
        // to change the line endings changes its size, and git then reports it
        // as modified although its content is the same; the next pull that
        // touches the file is refused. That happened on the owner's PC on
        // 2026-11-12 (docs/design/VERIFY_LOG.md).
        var work = Path.Combine(Path.GetTempPath(), $"tlm-formkeys-{Guid.NewGuid():N}.txt");
        if (File.Exists(formKeyFile)) File.Copy(formKeyFile, work, overwrite: true);
        Builder builder;
        try
        {
            using (var allocator = new TextFileFormKeyAllocator(mod, work))
            {
                mod.SetAllocator(allocator);
                builder = new Builder(mod, vanilla, master);
                builder.Build();
                allocator.Commit();
            }
            var wanted = NormalizeLines(File.ReadAllText(work));
            var current = File.Exists(formKeyFile) ? File.ReadAllText(formKeyFile) : null;
            if (current == null || NormalizeLines(current) != wanted) File.WriteAllText(formKeyFile, wanted);
        }
        finally
        {
            if (File.Exists(work)) File.Delete(work);
        }
        return (mod, builder);
    }

    static string NormalizeLines(string text) =>
        text.Replace("\r\n", "\n").Replace("\r", "\n").TrimEnd('\n') + "\n";

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
