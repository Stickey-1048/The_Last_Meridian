using Mutagen.Bethesda;
using Mutagen.Bethesda.Fallout4;
using Mutagen.Bethesda.Plugins;
using Mutagen.Bethesda.Plugins.Allocators;
using Mutagen.Bethesda.Plugins.Cache;
using Mutagen.Bethesda.Plugins.Records;
using Noggog;
using Color = System.Drawing.Color;

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
    readonly ILinkCache<IFallout4Mod, IFallout4ModGetter>? _vanilla;
    readonly IFallout4ModGetter? _vanillaMod;
    readonly Dictionary<string, IFallout4MajorRecordGetter> _byId = new(StringComparer.OrdinalIgnoreCase);
    readonly Dictionary<string, FormKey> _placed = new(StringComparer.OrdinalIgnoreCase);

    /// <summary>Things this build could not wire, with the reason.</summary>
    public List<string> Pending { get; } = new();

    /// <summary>
    /// What each lookup in Fallout4.esm actually returned: the id asked for,
    /// the record found, and the EditorID as the master spells it.
    /// </summary>
    public List<string> VanillaNotes { get; } = new();
    /// <summary>Game records found in Fallout4.esm: the name asked for, the record, and its kind.</summary>
    public List<Report.VanillaInfo> VanillaFound { get; } = new();

    /// <summary>The references this build placed in cells of the game, by EditorID. Empty without Fallout4.esm.</summary>
    public IReadOnlyDictionary<string, FormKey> PlacedKeys => _placed;

    /// <summary>World models borrowed from items of the game: this plugin's item, and the path of the model file.</summary>
    public Dictionary<string, string> BorrowedModels { get; } = new();

    /// <summary>The actors of this plugin's own that this build made (each is a copy of one of the game's, so none without Fallout4.esm).</summary>
    public HashSet<string> MadeNpcs { get; } = new(StringComparer.OrdinalIgnoreCase);
    /// <summary>For each of the game's actors a copy was made of: does its record name a default package list, does it take one from a template, and does it name a template actor for it?</summary>
    public Dictionary<string, (bool InRecord, bool FromTemplate, bool TemplateActor)> SourceDefaultList { get; } = new(StringComparer.OrdinalIgnoreCase);

    /// <summary>For each actor of this plugin's own that was given the looks of one of the game's actors: that actor.</summary>
    public Dictionary<string, string> LooksFrom { get; } = new(StringComparer.OrdinalIgnoreCase);

    /// <summary>For each placed reference whose base is a record of the game's: that record.</summary>
    public Dictionary<string, string> PlacedGameBase { get; } = new(StringComparer.OrdinalIgnoreCase);

    /// <summary>The collision layer each placed trigger was given: the index the master has for the layer the spec names.</summary>
    public Dictionary<string, uint> PlacedLayers { get; } = new(StringComparer.OrdinalIgnoreCase);

    /// <summary>True when this build gave its boxes a bound as well (it does as most of the game's own box triggers do).</summary>
    public bool WritesBoxBound { get; private set; }

    /// <summary>The name each copied cell carries in this plugin, as read from the master (null: none could be read).</summary>
    public Dictionary<string, string?> CellNames { get; } = new(StringComparer.OrdinalIgnoreCase);

    /// <summary>Where the master files each cell this build placed something in: its block and sub-block.
    /// This plugin's copy of the cell's record has to be filed the same way.</summary>
    public Dictionary<string, (int Block, int SubBlock)> CellsFiled { get; } = new(StringComparer.OrdinalIgnoreCase);

    /// <summary>Where the player arrives in each cell this build placed something in (for the stand-in engine).</summary>
    public List<Report.ArrivalInfo> Arrivals { get; } = new();

    public Fallout4Mod Mod => _mod;

    public Builder(Fallout4Mod mod, ILinkCache<IFallout4Mod, IFallout4ModGetter>? vanilla, IFallout4ModGetter? vanillaMod = null)
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
            if (m.LooksLike != null)
            {
                if (TryFindLook("MiscItem", m.LooksLike, m.EditorId, out var look))
                {
                    item.Model = new Model { File = look.File };
                    if (look.Bounds != null) item.ObjectBounds = look.Bounds.DeepCopy();
                }
                else
                    Pending.Add($"{m.EditorId}: no world model (it borrows the look of one of the game's things, which needs Fallout4.esm)");
            }
            else if (m.ModelFrom == null)
                Pending.Add($"{m.EditorId}: no world model yet (it exists only in inventories until one is assigned)");
            else if (!TryBorrowModel(item, m.ModelFrom))
                Pending.Add($"{m.EditorId}: no world model (it borrows the one of '{m.ModelFrom}', which needs Fallout4.esm)");
        }

        foreach (var a in Spec.Activators)
        {
            // No model: placed with a box around it, it is a trigger. The
            // bounds are written (all zero), as on every record that can be placed.
            var activator = _mod.Activators.AddNew(a.EditorId);
            Track(activator);
            // With a name and a look it is something to point at and use.
            if (a.Name != null) activator.Name = a.Name;
            if (a.ActivateText != null) activator.ActivateTextOverride = a.ActivateText;
            if (a.LooksLike != null)
            {
                if (TryFindLook("MiscItem", a.LooksLike, a.EditorId, out var look))
                {
                    activator.Model = new Model { File = look.File };
                    if (look.Bounds != null) activator.ObjectBounds = look.Bounds.DeepCopy();
                }
                else
                    Pending.Add($"{a.EditorId}: no world model (it borrows the look of one of the game's things, which needs Fallout4.esm)");
            }
        }

        foreach (var c in Spec.Containers)
        {
            var container = _mod.Containers.AddNew(c.EditorId);
            container.Name = c.Name;
            Track(container);
            if (TryFindLook("Container", c.LooksLike, c.EditorId, out var look))
            {
                container.Model = new Model { File = look.File };
                if (look.Bounds != null) container.ObjectBounds = look.Bounds.DeepCopy();
            }
            else
                Pending.Add($"{c.EditorId}: no world model (it borrows the look of one of the game's containers, which needs Fallout4.esm)");
            if (TryVanilla(c.HoldsVanillaItem, "MiscItem", out var heldKey))
            {
                container.Items ??= new ExtendedList<ContainerEntry>();
                container.Items.Add(new ContainerEntry { Item = new ContainerItem { Item = new FormLink<IItemGetter>(heldKey), Count = c.Count } });
            }
            else
                Pending.Add($"{c.EditorId}: empty (it holds '{c.HoldsVanillaItem}', which needs Fallout4.esm)");
        }

        foreach (var n in Spec.Npcs)
        {
            // The id is given out whether or not the actor can be made, so that
            // the tracked id file comes out the same with and without Fallout4.esm.
            var key = _mod.GetNextFormKey(n.EditorId);
            if (n.Sex is not (null or "male" or "female"))
                throw new InvalidOperationException($"{n.EditorId}: Sex is '{n.Sex}'; it is male, female, or left out");
            if (n.Faction != null && Local(n.Faction) is not IFactionGetter)
                throw new InvalidOperationException($"{n.EditorId}: '{n.Faction}' is not a faction of this plugin");
            var whyNot = TryMakeNpc(n, key);
            if (whyNot != null) Pending.Add($"{n.EditorId}: not made ({whyNot})");
        }
        if (Spec.Npcs.Length > 0) NoteStayPackages();
        NameWhatARunNamedById();

        foreach (var b in Spec.Books)
        {
            var book = _mod.Books.AddNew(b.EditorId);
            book.Name = b.Name;
            book.BookText = b.Text;
            Track(book);
            if (!b.LooksLikeANote)
                Pending.Add($"{b.EditorId}: no world model yet");
            else if (FindNote() is { } note)
            {
                // What lets it lie in the world and be read there: the model,
                // the picture it is read on, and its sounds. All of it is
                // named, none of it copied.
                book.Model = new Model { File = note.Model!.File };
                book.ObjectBounds = note.ObjectBounds.DeepCopy();
                book.InventoryArt.SetTo(note.InventoryArt.FormKeyNullable);
                book.PickUpSound.SetTo(note.PickUpSound.FormKeyNullable);
                book.PutDownSound.SetTo(note.PutDownSound.FormKeyNullable);
                book.PreviewTransform.SetTo(note.PreviewTransform.FormKeyNullable);
                book.TextOffsetX = note.TextOffsetX;
                book.TextOffsetY = note.TextOffsetY;
                BorrowedModels[b.EditorId] = note.Model.File;
                VanillaNotes.Add($"{b.EditorId}: lies in the world and is read as the game's {note.EditorID ?? note.FormKey.ToString()} is: model '{note.Model.File}', read on {(note.InventoryArt.IsNull ? "nothing" : note.InventoryArt.FormKey.ToString())}");
            }
            else
                Pending.Add($"{b.EditorId}: no world model (it takes after one of the game's notes, which needs Fallout4.esm)");
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

        // Before the quests are filled in: their aliases point at these.
        PlaceReferences();

        foreach (var q in Spec.Quests) Fill(quests[q.EditorId], q);
    }

    // ------------------------------------------------------------- actors

    /// <summary>
    /// Makes an actor of this plugin's own as a copy of one of the game's
    /// without what makes it go about its business: its packages and its
    /// scripts, with the template flags and the template actors that would
    /// fetch either from the actor it is modelled on. Its default package
    /// list is kept or dropped as the spec says. What it looks like, what it
    /// carries and how it fights stay as they were. The build output says
    /// what the game's actor had, which is also the best account to be had
    /// here of why a placed copy of that actor does what it does.
    ///
    /// UNTESTED in the game and in the Creation Kit until docs/design/VERIFY_LOG.md says otherwise.
    /// </summary>
    /// <returns>Nothing if the actor was made; otherwise why it was not.</returns>
    string? TryMakeNpc(NpcSpec spec, FormKey key)
    {
        if (_vanilla == null) return $"it is a copy of '{spec.CopyFrom}', which needs Fallout4.esm";
        if (!TryVanilla(spec.CopyFrom, "Npc", out var sourceKey) || !_vanilla.TryResolve<INpcGetter>(sourceKey, out var source))
            return $"no Npc '{spec.CopyFrom}' in Fallout4.esm";
        // Said once for each of the game's actors, however many copies are made of it.
        if (!SourceDefaultList.ContainsKey(spec.CopyFrom)) DescribeSource(spec.CopyFrom, source);
        try
        {
            // What the copy is to be without is not read for the copy at all:
            // its scripts, with whatever they are set up with, and its packages.
            var mask = new Npc.TranslationMask(defaultOn: true)
            {
                Packages = false,
                VirtualMachineAdapter = new VirtualMachineAdapter.TranslationMask(defaultOn: false, onOverall: false),
            };
            var npc = source.Duplicate(key, mask);
            npc.EditorID = spec.EditorId;
            // Plain text, so that nothing has to be looked up in the game's strings files when the plugin is written.
            npc.Name = spec.Name;
            npc.ShortName = null;
            npc.Packages.Clear();
            npc.VirtualMachineAdapter = null;
            // A plain record, whatever the game's is: nothing here is large.
            npc.IsCompressed = false;
            // Whatever is taken away from the record must not come back from the
            // actor it is modelled on: neither by the flag that says "take this
            // from a template" nor by the template actor named for it.
            var dropped = Npc.TemplateActorType.AiPackages | Npc.TemplateActorType.Script;
            npc.TemplateActors?.AiPackagesTemplate.Clear();
            npc.TemplateActors?.ScriptTemplate.Clear();
            if (!spec.KeepDefaultPackageList)
            {
                npc.DefaultPackageList.Clear();
                dropped |= Npc.TemplateActorType.DefPackList;
                npc.TemplateActors?.DefPackListTemplate.Clear();
            }
            npc.UseTemplateActors &= ~dropped;
            var more = "";
            if (spec.Faction != null)
            {
                // Its own people and nobody else's: what the game's actor
                // belongs to decides who takes its side in a fight, and whose
                // law a blow against it breaks.
                var faction = Local(spec.Faction);
                var had = npc.Factions.Count;
                npc.Factions.Clear();
                npc.Factions.Add(new RankPlacement { Faction = new FormLink<IFactionGetter>(faction.FormKey), Rank = 0 });
                npc.CrimeFaction.Clear();
                npc.UseTemplateActors &= ~Npc.TemplateActorType.Factions;
                npc.TemplateActors?.FactionsTemplate.Clear();
                more += $"; in {spec.Faction} and in none of the game's {had} faction(s)";
            }
            if (spec.StandsBy)
            {
                npc.Aggression = Npc.AggressionType.Unaggressive;
                npc.Assistance = spec.HelpsItsOwn ? Npc.AssistanceType.HelpsAllies : Npc.AssistanceType.HelpsNobody;
                npc.Confidence = Npc.ConfidenceType.Foolhardy;
                npc.UseTemplateActors &= ~Npc.TemplateActorType.AiData;
                npc.TemplateActors?.AiDataTemplate.Clear();
                more += $"; starts no fight, {(spec.HelpsItsOwn ? "joins one of its own faction's" : "joins none")}, and does not run from one";
            }
            if (spec.Sex != null)
            {
                // The looks are worth having, not worth losing the actor for.
                try { more += FixLooks(npc, source, spec); }
                catch (Exception e) { more += $"; NOTE: its looks could not be fixed ({e.GetType().Name}: {e.Message}), so they are drawn as the game draws them"; }
            }
            // A record of the game's that the library cannot write back would
            // stop the whole build when the plugin is written, long after this.
            // So the copy is written and read on its own first, and left out if that fails.
            TrialWrite(npc);
            _mod.Npcs.Add(npc);
            Track(npc);
            MadeNpcs.Add(spec.EditorId);
            var list = !spec.KeepDefaultPackageList ? "no default package list"
                : npc.UseTemplateActors.HasFlag(Npc.TemplateActorType.DefPackList) ? "its default package list still taken from a template"
                : npc.DefaultPackageList.IsNull ? "no default package list (the game's actor names none)"
                : "its default package list kept";
            VanillaNotes.Add($"{spec.EditorId}: made as a copy of {spec.CopyFrom} with no packages and no script, and {list}; named '{spec.Name}'; still from a template: {FlagList(npc.UseTemplateActors)}; template actors still named for: {LinkList(npc.TemplateActors)}{more}");
            return null;
        }
        catch (Exception e)
        {
            // One actor that cannot be made is no reason to lose the rest of the build.
            if (_mod.Npcs.ContainsKey(key)) _mod.Npcs.Remove(key);
            VanillaNotes.Add($"NOTE {spec.EditorId}: could not be made from {spec.CopyFrom} ({e.GetType().Name}: {e.Message})");
            return $"copying '{spec.CopyFrom}' failed: {e.GetType().Name}";
        }
    }

    /// <summary>The thirteen things an actor can take from another, in the order the file keeps them, with the actor named for each.</summary>
    static IEnumerable<(string Name, IFormLinkGetter<INpcSpawnGetter> Link)> TemplateLinks(ITemplateActorsGetter t) => new (string, IFormLinkGetter<INpcSpawnGetter>)[]
    {
        ("Traits", t.TraitTemplate), ("Stats", t.StatsTemplate), ("Factions", t.FactionsTemplate), ("SpellList", t.SpellListTemplate),
        ("AiData", t.AiDataTemplate), ("AiPackages", t.AiPackagesTemplate), ("ModelOrAnimation", t.ModelOrAnimationTemplate),
        ("BaseData", t.BaseDataTemplate), ("Inventory", t.InventoryTemplate), ("Script", t.ScriptTemplate),
        ("DefPackList", t.DefPackListTemplate), ("AttackData", t.AttackDataTemplate), ("Keywords", t.KeywordsTemplate),
    };

    public static List<string> LinkNames(ITemplateActorsGetter? t) =>
        t == null ? new() : TemplateLinks(t).Where(x => !x.Link.IsNull).Select(x => x.Name).ToList();

    static string LinkList(ITemplateActorsGetter? t)
    {
        var names = LinkNames(t);
        return names.Count == 0 ? "nothing" : string.Join(", ", names);
    }

    /// <summary>
    /// Says what one of the game's actors goes about with: its packages, the
    /// lists of packages it falls back on, its scripts, what it takes from a
    /// template and from whom, and who it is (factions, keywords, voice). A
    /// script in the game can say which package a person is running only by
    /// its id; this is where the names are. Each part is read on its own: one
    /// that cannot be read is said so, and the rest still is.
    /// </summary>
    void DescribeSource(string id, INpcGetter source)
    {
        string Named<T>(FormKey k) where T : class, IFallout4MajorRecordGetter =>
            k.IsNull ? "none" : _vanilla!.TryResolve<T>(k, out var rec) && rec.EditorID != null ? $"{rec.EditorID} ({k})" : k.ToString();
        string Some(IEnumerable<string> names, int most = 12)
        {
            var all = names.ToList();
            return all.Count == 0 ? "none" : string.Join(", ", all.Take(most)) + (all.Count > most ? $", and {all.Count - most} more" : "");
        }
        string PackageList(IFormLinkNullableGetter<IFormListGetter> link)
        {
            if (link.IsNull) return "none";
            var name = Named<IFormListGetter>(link.FormKey);
            if (!_vanilla!.TryResolve<IFormListGetter>(link.FormKey, out var list)) return name;
            return $"{name}, which holds {list.Items.Count}: {Some(list.Items.Select(i => Named<IPackageGetter>(i.FormKey)))}";
        }
        void Say(string what, Func<string> read)
        {
            try { VanillaNotes.Add($"{id}: {what}: {read()}"); }
            catch (Exception e) { VanillaNotes.Add($"NOTE {id}: {what} could not be read ({e.GetType().Name}: {e.Message})"); }
        }

        var inRecord = false; var fromTemplate = false; var templateActor = false;
        try
        {
            inRecord = !source.DefaultPackageList.IsNull;
            fromTemplate = source.UseTemplateActors.HasFlag(Npc.TemplateActorType.DefPackList);
            templateActor = source.TemplateActors != null && !source.TemplateActors.DefPackListTemplate.IsNull;
        }
        catch (Exception e)
        {
            VanillaNotes.Add($"NOTE {id}: its default package list could not be read ({e.GetType().Name}: {e.Message})");
        }
        SourceDefaultList[id] = (inRecord, fromTemplate, templateActor);

        Say("the game's actor has packages", () => $"{source.Packages.Count}: {Some(source.Packages.Select(p => Named<IPackageGetter>(p.FormKey)))}");
        Say("default package list", () => PackageList(source.DefaultPackageList));
        Say("other package lists, which a copy keeps", () => Some(new (string Name, IFormLinkNullableGetter<IFormListGetter> Link)[]
            {
                ("spectator", source.SpectatorOverridePackageList), ("observe dead body", source.ObserveDeadBodyOverridePackageList),
                ("guard warn", source.GuardWarnOverridePackageList), ("combat", source.CombatOverridePackageList),
                ("follower command", source.FollowerCommandPackageList), ("follower elevator", source.FollowerElevatorPackageList),
            }.Where(x => !x.Link.IsNull).Select(x => $"{x.Name} = {PackageList(x.Link)}")));
        Say("script(s)", () => Some(source.VirtualMachineAdapter?.Scripts.Select(s => s.Name) ?? Enumerable.Empty<string>()));
        Say("takes from a template", () => FlagList(source.UseTemplateActors)
            + $"; template actors named: {(source.TemplateActors == null ? "none" : Some(TemplateLinks(source.TemplateActors).Where(x => !x.Link.IsNull).Select(x => $"{x.Name} from {Named<INpcSpawnGetter>(x.Link.FormKey)}"), 13))}"
            + $"; default template {Named<INpcSpawnGetter>(source.DefaultTemplate.FormKey)}");
        Say("who it is", () => $"factions {Some(source.Factions.Select(f => Named<IFactionGetter>(f.Faction.FormKey)))}; keywords {Some((source.Keywords ?? Enumerable.Empty<IFormLinkGetter<IKeywordGetter>>()).Select(k => Named<IKeywordGetter>(k.FormKey)))}"
            + $"; voice {Named<IVoiceTypeGetter>(source.Voice.FormKey)}; its record is {(source.IsCompressed ? "compressed" : "not compressed")}");
        Say("the master's actors and their default package lists", () =>
        {
            if (_vanillaMod == null) return "no master";
            var all = 0; var counts = new Dictionary<FormKey, int>();
            foreach (var n in _vanillaMod.Npcs)
            {
                all++;
                var k = n.DefaultPackageList.FormKeyNullable;
                if (k is { } named && !named.IsNull) counts[named] = counts.GetValueOrDefault(named) + 1;
            }
            var most = counts.OrderByDescending(c => c.Value).ThenBy(c => c.Key.ToString()).Take(3)
                .Select(c => $"{Named<IFormListGetter>(c.Key)} ({c.Value})");
            return $"{counts.Values.Sum()} of {all} name one in their own record; different lists: {counts.Count}; the commonest: {Some(most)}";
        });
    }

    /// <summary>
    /// Writes one actor into a throw-away plugin and reads it back. Throws if either fails.
    /// </summary>
    static void TrialWrite(Npc npc)
    {
        const string name = "TLM_TrialWrite.esp";
        var scratch = new Fallout4Mod(ModKey.FromNameAndExtension(name), Fallout4Release.Fallout4);
        scratch.Npcs.DuplicateInAsNewRecord(npc);
        // The library writes a plugin only under its own name, so the file gets a folder of its own.
        var folder = Path.Combine(Path.GetTempPath(), $"tlm-trial-write-{Guid.NewGuid():N}");
        var path = Path.Combine(folder, name);
        Directory.CreateDirectory(folder);
        try
        {
            scratch.BeginWrite.ToPath(path).WithNoLoadOrder().WithExtraIncludedMasters(Fallout4Esm).Write();
            using var back = Fallout4Mod.CreateFromBinaryOverlay(path, Fallout4Release.Fallout4);
            var read = back.Npcs.SingleOrDefault() ?? throw new InvalidOperationException("the copy did not read back as one actor");
            if (read.Packages.Count != 0 || read.VirtualMachineAdapter != null)
                throw new InvalidOperationException("the copy read back with packages or scripts");
            if (read.IsCompressed)
                throw new InvalidOperationException("the copy read back compressed");
        }
        finally
        {
            try { Directory.Delete(folder, recursive: true); } catch (IOException) { } catch (UnauthorizedAccessException) { }
        }
    }

    static string FlagList<T>(T flags) where T : struct, Enum
    {
        var bits = Convert.ToUInt64(flags);
        var names = Enum.GetValues<T>().Where(v => Convert.ToUInt64(v) is var bit && bit != 0 && (bits & bit) == bit).Select(v => v.ToString()).ToList();
        return names.Count == 0 ? "nothing" : string.Join(", ", names);
    }

    /// <summary>Says the names of records that a run in the game gave only as ids (Spec.NameThese).</summary>
    void NameWhatARunNamedById()
    {
        if (_vanilla == null) return;
        foreach (var (kind, id, why) in Spec.NameThese)
        {
            var key = new FormKey(Fallout4Esm, id);
            try
            {
                string? name = kind switch
                {
                    "Package" => _vanilla.TryResolve<IPackageGetter>(key, out var p) ? p.EditorID ?? "(no name)" : null,
                    _ => throw new InvalidOperationException($"this builder cannot look up a {kind} by id"),
                };
                VanillaNotes.Add(name == null
                    ? $"{key}: no {kind} of that id in the master ({why})"
                    : $"{key}: the {kind} {name} ({why})");
            }
            catch (Exception e)
            {
                VanillaNotes.Add($"NOTE {key}: could not be looked up ({e.GetType().Name}: {e.Message})");
            }
        }
    }

    /// <summary>
    /// Says which of the game's own packages look, by their names, as if they
    /// keep an actor in one place. Nothing in this build uses one: an actor of
    /// the plugin's own has no packages at all. It is here so that, should
    /// such an actor not stay where it is put, the next build can give it a
    /// package of the game's without another run just to find out the names.
    /// A name is a hint and no more; what a package does is not read.
    /// </summary>
    void NoteStayPackages()
    {
        if (_vanillaMod == null) return;
        try
        {
            string[] hints = { "Stay", "Hold", "Stand", "Wait", "EditorLoc", "Sandbox" };
            var all = 0;
            var found = new List<string>();
            foreach (var p in _vanillaMod.Packages)
            {
                all++;
                var id = p.EditorID;
                if (id == null || !id.StartsWith("Default", StringComparison.OrdinalIgnoreCase)) continue;
                if (hints.Any(h => id.Contains(h, StringComparison.OrdinalIgnoreCase))) found.Add($"{id} ({p.FormKey})");
            }
            found.Sort(StringComparer.OrdinalIgnoreCase);
            const int most = 40;
            VanillaNotes.Add($"packages: the master has {all}; {found.Count} have a name that begins 'Default' and holds one of {string.Join(", ", hints)}"
                + (found.Count == 0 ? "" : ": " + string.Join(", ", found.Take(most)) + (found.Count > most ? $", and {found.Count - most} more" : "")));
        }
        catch (Exception e)
        {
            VanillaNotes.Add($"NOTE packages: the master's packages could not be looked through ({e.GetType().Name}: {e.Message})");
        }
    }

    // ------------------------------------------------------ an actor's looks

    readonly Dictionary<string, (FormKey From, List<(FormKey Key, string Id, bool? Female)> Offered)> _looksOffered = new(StringComparer.OrdinalIgnoreCase);
    readonly Dictionary<(string Source, bool Female), int> _looksGiven = new();

    /// <summary>
    /// Gives a copy the looks of one particular actor of the sex the spec asks
    /// for. The game's actor draws its looks (and whatever else it takes from
    /// the same place) from a list of actors, one of them at random for every
    /// person placed; the copy is pointed at one actor of that list, so that
    /// a named person is the same person every time. Which one: the actors of
    /// the right sex in the order of their ids, the first copy the first of
    /// them, the second the second, and round again when they run out.
    ///
    /// UNTESTED in the game and in the Creation Kit until docs/design/VERIFY_LOG.md says otherwise.
    /// </summary>
    /// <returns>What to add to the build's line about the actor.</returns>
    string FixLooks(Npc npc, INpcGetter source, NpcSpec spec)
    {
        var female = spec.Sex == "female";
        if (!source.UseTemplateActors.HasFlag(Npc.TemplateActorType.Traits))
            return $"; NOTE: {spec.CopyFrom} draws its looks from nowhere, so the copy looks as it does, whatever the spec asks for";
        if (!_looksOffered.TryGetValue(spec.CopyFrom, out var known))
        {
            var from = source.TemplateActors != null && !source.TemplateActors.TraitTemplate.IsNull
                ? source.TemplateActors.TraitTemplate.FormKey
                : source.DefaultTemplate.FormKey;
            known = (from, LooksOffered(from));
            _looksOffered[spec.CopyFrom] = known;
            var o = known.Offered;
            string Sex(bool? f) => f == null ? "of no one sex" : f.Value ? "female" : "male";
            VanillaNotes.Add($"{spec.CopyFrom}: its looks are drawn from {NameOfSpawn(from)}, which offers {o.Count} actor(s): {o.Count(x => x.Female == false)} male, {o.Count(x => x.Female == true)} female, {o.Count(x => x.Female == null)} of no one sex"
                + (o.Count == 0 ? "" : ": " + string.Join(", ", o.Take(40).Select(x => $"{x.Id} ({Sex(x.Female)})")) + (o.Count > 40 ? $", and {o.Count - 40} more" : "")));
        }
        var fit = known.Offered.Where(x => x.Female == female).ToList();
        if (fit.Count == 0)
            return $"; NOTE: none of the actors {spec.CopyFrom} draws its looks from is known to be {spec.Sex}, so its looks are drawn as the game draws them";
        var nth = _looksGiven.GetValueOrDefault((spec.CopyFrom, female));
        _looksGiven[(spec.CopyFrom, female)] = nth + 1;
        var pick = fit[nth % fit.Count];
        // Whatever the game's actor takes from that list, the copy takes from
        // the one actor: nothing about a named person is left to chance.
        npc.TemplateActors ??= new TemplateActors();
        var t = npc.TemplateActors;
        foreach (var link in new[] { t.TraitTemplate, t.StatsTemplate, t.FactionsTemplate, t.SpellListTemplate, t.AiDataTemplate, t.AiPackagesTemplate,
                     t.ModelOrAnimationTemplate, t.BaseDataTemplate, t.InventoryTemplate, t.ScriptTemplate, t.DefPackListTemplate, t.AttackDataTemplate, t.KeywordsTemplate })
            if (link.FormKey == known.From) link.SetTo(pick.Key);
        t.TraitTemplate.SetTo(pick.Key);
        if (npc.DefaultTemplate.FormKey == known.From) npc.DefaultTemplate.SetTo(pick.Key);
        LooksFrom[spec.EditorId] = pick.Key.ToString();
        return $"; looks: those of {pick.Id} ({pick.Key}), {spec.Sex}, number {nth % fit.Count + 1} of {fit.Count}"
            + (nth >= fit.Count ? " (used before: there are more people than faces)" : "");
    }

    string NameOfSpawn(FormKey key) =>
        key.IsNull ? "nobody" : _vanilla!.TryResolve<INpcSpawnGetter>(key, out var rec) && rec.EditorID != null ? $"{rec.EditorID} ({key})" : key.ToString();

    /// <summary>The actors a list of actors offers, lists within lists followed, with the sex of each where it has one.</summary>
    List<(FormKey Key, string Id, bool? Female)> LooksOffered(FormKey from)
    {
        var offered = new List<(FormKey Key, string Id, bool? Female)>();
        var seen = new HashSet<FormKey>();
        void Walk(FormKey key, int depth)
        {
            if (key.IsNull || depth > 8 || offered.Count >= 400 || !seen.Add(key)) return;
            if (_vanilla!.TryResolve<ILeveledNpcGetter>(key, out var list))
            {
                foreach (var entry in list.Entries ?? Array.Empty<ILeveledNpcEntryGetter>())
                    if (entry.Data != null) Walk(entry.Data.Reference.FormKey, depth + 1);
            }
            else if (_vanilla.TryResolve<INpcGetter>(key, out var actor))
                offered.Add((key, actor.EditorID ?? key.ToString(), SexOf(key, 0)));
        }
        Walk(from, 0);
        offered.Sort((a, b) => a.Key.ID.CompareTo(b.Key.ID));
        return offered;
    }

    /// <summary>
    /// The sex an actor ends up with: its own, or that of the actor it takes
    /// its looks from, however far that goes. A list of actors has a sex if
    /// everybody in it has the same one. Null: none can be said.
    /// </summary>
    bool? SexOf(FormKey key, int depth)
    {
        if (key.IsNull || depth > 8) return null;
        if (_vanilla!.TryResolve<ILeveledNpcGetter>(key, out var list))
        {
            bool? all = null;
            foreach (var entry in list.Entries ?? Array.Empty<ILeveledNpcEntryGetter>())
            {
                if (entry.Data == null) continue;
                var one = SexOf(entry.Data.Reference.FormKey, depth + 1);
                if (one == null || (all != null && all != one)) return null;
                all = one;
            }
            return all;
        }
        if (!_vanilla.TryResolve<INpcGetter>(key, out var actor)) return null;
        if (!actor.UseTemplateActors.HasFlag(Npc.TemplateActorType.Traits)) return actor.Flags.HasFlag(Npc.Flag.Female);
        var from = actor.TemplateActors != null && !actor.TemplateActors.TraitTemplate.IsNull
            ? actor.TemplateActors.TraitTemplate.FormKey
            : actor.DefaultTemplate.FormKey;
        return from.IsNull ? actor.Flags.HasFlag(Npc.Flag.Female) : SexOf(from, depth + 1);
    }

    // ------------------------------------ things found by the name a player sees
    // The names the game uses inside for its things are not known here, and a
    // guess that misses costs a run on the game PC. The names a player sees
    // are known: they are on the screen. So some things are looked up by
    // those. A localized master keeps them in its strings files; without
    // those files nothing is found, and what was to borrow a look falls back
    // on the bottle cap's.

    /// <summary>A record of the game's as the lookups by name see it.</summary>
    sealed record Named(FormKey Key, string? EditorId, string? ModelFile, IObjectBoundsGetter? Bounds);

    readonly Dictionary<string, Dictionary<string, List<Named>>> _byName = new(StringComparer.OrdinalIgnoreCase);

    Dictionary<string, List<Named>> NamesOf(string kind)
    {
        if (_byName.TryGetValue(kind, out var have)) return have;
        var index = new Dictionary<string, List<Named>>(StringComparer.OrdinalIgnoreCase);
        _byName[kind] = index;
        if (_vanillaMod == null) return index;
        var all = 0; var named = 0; var failed = 0;
        string? firstFailure = null;
        void Add(FormKey key, string? editorId, Func<string?> name, Func<string?> model, Func<IObjectBoundsGetter?> bounds)
        {
            all++;
            try
            {
                var text = name();
                if (string.IsNullOrWhiteSpace(text)) return;
                named++;
                if (!index.TryGetValue(text, out var list)) index[text] = list = new List<Named>();
                list.Add(new Named(key, editorId, model(), bounds()));
            }
            catch (Exception e)
            {
                failed++;
                firstFailure ??= $"{e.GetType().Name}: {e.Message}";
            }
        }
        try
        {
            switch (kind)
            {
                case "MiscItem":
                    foreach (var r in _vanillaMod.MiscItems) Add(r.FormKey, r.EditorID, () => r.Name?.String, () => r.Model?.File, () => r.ObjectBounds);
                    break;
                case "Weapon":
                    foreach (var r in _vanillaMod.Weapons) Add(r.FormKey, r.EditorID, () => r.Name?.String, () => r.Model?.File, () => r.ObjectBounds);
                    break;
                case "Container":
                    foreach (var r in _vanillaMod.Containers) Add(r.FormKey, r.EditorID, () => r.Name?.String, () => r.Model?.File, () => r.ObjectBounds);
                    break;
                default:
                    throw new InvalidOperationException($"Spec asks for a {kind} by the name a player sees, which the builder cannot look up");
            }
        }
        catch (InvalidOperationException) { throw; }
        catch (Exception e)
        {
            failed++;
            firstFailure ??= $"{e.GetType().Name}: {e.Message}";
        }
        foreach (var list in index.Values) list.Sort((a, b) => a.Key.ID.CompareTo(b.Key.ID));
        VanillaNotes.Add($"the names a player sees: {named} of the master's {all} {kind} record(s) have one"
            + (failed == 0 ? "" : $"; NOTE: {failed} could not be read ({firstFailure})"));
        return index;
    }

    /// <summary>
    /// Finds a record of the game's by the name a player sees: the first of
    /// the names that is there and, of several records so named, the one with
    /// the lowest id.
    /// </summary>
    bool TryVanillaNamed(string kind, string[] names, string forWhat, bool needsModel, out FormKey key, out string? modelFile, out IObjectBoundsGetter? bounds, out string found)
    {
        key = FormKey.Null; modelFile = null; bounds = null; found = "";
        if (_vanilla == null) return false;
        var index = NamesOf(kind);
        foreach (var name in names)
        {
            if (!index.TryGetValue(name, out var list)) continue;
            var fit = needsModel ? list.Where(x => !string.IsNullOrEmpty(x.ModelFile)).ToList() : list;
            if (fit.Count == 0) continue;
            var pick = fit[0];
            key = pick.Key; modelFile = pick.ModelFile; bounds = pick.Bounds;
            found = $"'{name}' ({pick.EditorId ?? "no EditorID"})";
            VanillaNotes.Add($"{forWhat}: '{name}' -> {pick.Key} ({kind} {pick.EditorId ?? "with no EditorID"}; found by the name a player sees"
                + (fit.Count > 1 ? $", the first of {fit.Count} so named)" : ")"));
            var keyText = pick.Key.ToString();
            if (!VanillaFound.Any(v => v.FormKey == keyText)) VanillaFound.Add(new(pick.EditorId ?? name, keyText, kind));
            return true;
        }
        VanillaNotes.Add($"{forWhat}: no {kind} in Fallout4.esm{(needsModel ? " with a world model" : "")} is named {string.Join(" or ", names.Select(n => $"'{n}'"))}");
        return false;
    }

    /// <summary>A world model to borrow: the path of the file and the box around it.</summary>
    sealed record Look(string File, IObjectBoundsGetter? Bounds);

    /// <summary>
    /// Finds a look for a thing of this plugin's: that of the first of the
    /// game's things, by the names a player sees, that is there; or, when
    /// none is, the bottle cap's. Only the path is taken, never the file.
    /// </summary>
    bool TryFindLook(string kind, string[] names, string forWhat, out Look look)
    {
        look = null!;
        if (_vanilla == null) return false;
        string from;
        if (TryVanillaNamed(kind, names, forWhat, needsModel: true, out _, out var file, out var bounds, out var found))
        {
            look = new Look(file!, bounds);
            from = found;
        }
        else if (TryVanilla(Looks.LastResort, "MiscItem", out var lastKey) && _vanilla.TryResolve<IMiscItemGetter>(lastKey, out var last)
                 && !string.IsNullOrEmpty(last.Model?.File))
        {
            look = new Look(last.Model!.File, last.ObjectBounds);
            from = Looks.LastResort + ", for want of anything better";
            VanillaNotes.Add($"NOTE {forWhat}: none of the things it was to look like was found, so it looks like {Looks.LastResort}");
        }
        else
            return false;
        BorrowedModels[forWhat] = look.File;
        VanillaNotes.Add($"{forWhat}: world model borrowed from {from}: '{look.File}'");
        return true;
    }

    IBookGetter? _note;
    bool _noteSought;

    /// <summary>
    /// One of the game's notes for the plugin's papers to take after. Which
    /// record a note is, is not known here; what is known is that the game
    /// has many of them and that they share a few models. So: the model that
    /// most of the game's books lie in the world as, and of the books that
    /// use it a plain one (no script), the one with the lowest id.
    /// </summary>
    IBookGetter? FindNote()
    {
        if (_noteSought) return _note;
        _noteSought = true;
        if (_vanillaMod == null) return null;
        try
        {
            var byModel = new Dictionary<string, List<IBookGetter>>(StringComparer.OrdinalIgnoreCase);
            var all = 0;
            foreach (var b in _vanillaMod.Books)
            {
                all++;
                var file = b.Model?.File;
                if (string.IsNullOrEmpty(file)) continue;
                if (!byModel.TryGetValue(file, out var list)) byModel[file] = list = new List<IBookGetter>();
                list.Add(b);
            }
            if (byModel.Count == 0)
            {
                VanillaNotes.Add($"notes: none of the master's {all} book(s) has a world model to borrow");
                return null;
            }
            var most = byModel.OrderByDescending(kv => kv.Value.Count).ThenBy(kv => kv.Key, StringComparer.OrdinalIgnoreCase).First();
            _note = most.Value.OrderBy(b => b.VirtualMachineAdapter == null ? 0 : 1).ThenBy(b => b.FormKey.ID).First();
            VanillaNotes.Add($"notes: {most.Value.Count} of the master's {all} book(s) lie in the world as '{most.Key}', more than as any other model; the plugin's papers take after {_note.EditorID ?? "one with no EditorID"} ({_note.FormKey})");
        }
        catch (Exception e)
        {
            VanillaNotes.Add($"NOTE notes: the master's books could not be looked through ({e.GetType().Name}: {e.Message})");
        }
        return _note;
    }

    // ------------------------------------------------- placed references

    /// <summary>
    /// Gives this item the world model of an item of the game's: the path of
    /// the model file and the size of the box around it. Nothing else is
    /// copied; the file itself stays where it is, in the game's own archives.
    /// </summary>
    bool TryBorrowModel(MiscItem item, string from)
    {
        if (_vanilla == null) return false;
        if (!TryVanilla(from, "MiscItem", out var key) || !_vanilla.TryResolve<IMiscItemGetter>(key, out var source)) return false;
        var file = source.Model?.File;
        if (string.IsNullOrEmpty(file))
        {
            VanillaNotes.Add($"{from}: has no world model to borrow");
            return false;
        }
        item.Model = new Model { File = file };
        item.ObjectBounds = source.ObjectBounds.DeepCopy();
        BorrowedModels[item.EditorID!] = file;
        var b = item.ObjectBounds;
        VanillaNotes.Add($"{item.EditorID}: world model borrowed from {from}: '{file}', bounds ({b.First.X}, {b.First.Y}, {b.First.Z}) to ({b.Second.X}, {b.Second.Y}, {b.Second.Z})");
        return true;
    }

    /// <summary>Where the player arrives in a cell, and which way the player then faces; and the box that
    /// holds the middles of everything the game has placed in the cell (null if that could not be read).</summary>
    sealed record Arrival(P3Float Position, float Heading, bool Found, P3Float? Low = null, P3Float? High = null)
    {
        /// <summary>Is the point, seen from above, within the span of the cell's own objects? Not a promise of
        /// open floor; outside it is likely outside the room. Height is left out: a box in the air is not outside.</summary>
        public bool? Holds(P3Float p) => Low is { } lo && High is { } hi
            ? p.X >= lo.X && p.X <= hi.X && p.Y >= lo.Y && p.Y <= hi.Y
            : null;
    }

    const uint StartsDeadFlag = 0x200;
    const uint PersistentFlag = 0x400;
    const uint InitiallyDisabledFlag = 0x800;

    /// <summary>
    /// Puts <see cref="Spec.Placed"/> into cells of the game. A plugin places
    /// something in a cell it does not own by carrying its own copy of the
    /// cell's record (not of what the game has in the cell) with the new
    /// references under it.
    ///
    /// UNTESTED in the game and in the Creation Kit until docs/design/VERIFY_LOG.md says otherwise.
    /// </summary>
    void PlaceReferences()
    {
        CheckPlacedSpec();
        foreach (var group in Spec.Placed.GroupBy(p => p.Cell, StringComparer.OrdinalIgnoreCase))
        {
            // Ids are given out whether or not anything is placed, so that the
            // tracked id file comes out the same with and without Fallout4.esm.
            // A build that changed it would later block a pull on the game PC.
            var keys = new Dictionary<string, FormKey>();
            foreach (var p in group) keys.Add(p.EditorId, _mod.GetNextFormKey(p.EditorId));

            if (_vanilla == null)
            {
                foreach (var p in group) Pending.Add($"{p.EditorId}: not placed (the cell '{p.Cell}' is in Fallout4.esm)");
                continue;
            }
            if (!TryVanilla(group.Key, "Cell", out var cellKey)
                || !_vanilla.TryResolveContext<ICell, ICellGetter>(cellKey, out var context))
            {
                foreach (var p in group) Pending.Add($"{p.EditorId}: not placed (no cell '{p.Cell}' in Fallout4.esm)");
                continue;
            }

            NoteWhereFiled(cellKey, group.Key);
            var arrival = FindArrival(context.Record, group.Key);
            Arrivals.Add(new(group.Key, cellKey.ToString(), new[] { arrival.Position.X, arrival.Position.Y, arrival.Position.Z }, arrival.Heading, arrival.Found));
            var sample = group.Any(p => p.BoxHalfExtents != null) ? SampleGameTriggers() : null;

            // This plugin's copy of the cell's record. The game's own
            // references in the cell are not copied: they stay in the master.
            var cell = context.GetOrAddAsOverride(_mod);
            CopyCellName(context.Record, cell, group.Key);
            // The library's copy leaves out what is in the cell (read from its
            // copy mask: references, navigation meshes and land are all off).
            // Should that ever differ, nothing of the game's may stay: a copy
            // of one of its references here would replace it in the game.
            var theirs = cell.Persistent.Count + cell.Temporary.Count + cell.NavigationMeshes.Count + (cell.Landscape == null ? 0 : 1);
            if (theirs != 0)
            {
                cell.Persistent.Clear();
                cell.Temporary.Clear();
                cell.NavigationMeshes.Clear();
                cell.Landscape = null;
                VanillaNotes.Add($"NOTE {group.Key}: the copy of the cell's record came with {theirs} of the game's references, navigation meshes or land; they were taken out again");
            }

            foreach (var p in group)
            {
                FormKey baseKey;
                if (p.VanillaKind == null)
                {
                    if (!_byId.TryGetValue(p.Base, out var own))
                    {
                        // A record of the plugin's own that this build could not make (it says why elsewhere).
                        if (!Spec.Npcs.Any(n => n.EditorId == p.Base))
                            throw new InvalidOperationException($"{p.EditorId}: the spec places '{p.Base}', which this plugin does not define");
                        Pending.Add($"{p.EditorId}: not placed (its base '{p.Base}' was not made)");
                        continue;
                    }
                    baseKey = own.FormKey;
                }
                else if (p.BaseNames != null)
                {
                    if (!TryVanillaNamed(p.VanillaKind, p.BaseNames, p.EditorId, needsModel: true, out baseKey, out _, out _, out _))
                    {
                        Pending.Add($"{p.EditorId}: not placed (no {p.VanillaKind} of that name in Fallout4.esm)");
                        continue;
                    }
                }
                else if (!TryVanilla(p.Base, p.VanillaKind, out baseKey))
                {
                    Pending.Add($"{p.EditorId}: not placed (no {p.VanillaKind} '{p.Base}' in Fallout4.esm)");
                    continue;
                }
                if (p.VanillaKind != null) PlacedGameBase[p.EditorId] = baseKey.ToString();

                var (sin, cos) = (MathF.Sin(arrival.Heading), MathF.Cos(arrival.Heading));
                // Heading is measured from north (+Y) towards east (+X): ahead is (sin, cos), right is (cos, -sin).
                var position = new P3Float(
                    arrival.Position.X + p.Ahead * sin + p.Right * cos,
                    arrival.Position.Y + p.Ahead * cos - p.Right * sin,
                    arrival.Position.Z + p.Up);
                var flags = PersistentFlag | (p.InitiallyDisabled ? InitiallyDisabledFlag : 0u);
                // An actor is placed with a record of its own kind, whether its base is the game's or this plugin's.
                var isNpc = p.VanillaKind == null
                    ? _byId[p.Base] is INpcGetter
                    : string.Equals(p.VanillaKind, "Npc", StringComparison.OrdinalIgnoreCase);
                if (p.StartsDead)
                {
                    if (!isNpc) throw new InvalidOperationException($"{p.EditorId}: only an actor can start dead");
                    flags |= StartsDeadFlag;
                }
                if (isNpc)
                {
                    var npc = new PlacedNpc(keys[p.EditorId], Fallout4Release.Fallout4) { EditorID = p.EditorId };
                    npc.Base.SetTo(baseKey);
                    npc.Position = position;
                    // Facing the spot where the player arrives.
                    npc.Rotation = new P3Float(0, 0, NormalizeAngle(arrival.Heading + MathF.PI));
                    npc.MajorRecordFlagsRaw |= (int)flags;
                    cell.Persistent.Add(npc);
                }
                else
                {
                    var obj = new PlacedObject(keys[p.EditorId], Fallout4Release.Fallout4) { EditorID = p.EditorId };
                    obj.Base.SetTo(baseKey);
                    obj.Position = position;
                    obj.Rotation = new P3Float(0, 0, NormalizeAngle(arrival.Heading));
                    obj.MajorRecordFlagsRaw |= (int)flags;
                    if (p.BoxHalfExtents != null)
                    {
                        obj.Primitive = new PlacedPrimitive
                        {
                            // The library's Bounds are the whole sizes; the file
                            // holds half of each. Seen in the written bytes, and
                            // tools/check_plugin_layout.py reads them to make sure.
                            Bounds = new P3Float(2 * p.BoxHalfExtents[0], 2 * p.BoxHalfExtents[1], 2 * p.BoxHalfExtents[2]),
                            // What the editor draws the box with. Taken from one of
                            // the game's own box triggers when one was found.
                            Color = sample?.Template?.Color ?? Color.FromArgb(255, 128, 0),
                            Unknown = sample?.Template?.Unknown ?? 0.3f,
                            Type = PlacedPrimitive.TypeEnum.Box,
                        };
                        // The file can hold the box's reach a second time, as
                        // the reference's bound (XMBO); the format notes for
                        // the game before this one say the editor refuses a
                        // box whose two sets of numbers differ. Whether a
                        // plain trigger carries it is not known, so this does
                        // as most of the game's own box triggers do, and the
                        // build output says which way that went.
                        if (sample != null && sample.MostCarryBound)
                        {
                            obj.BoundHalfExtents = new P3Float(p.BoxHalfExtents[0], p.BoxHalfExtents[1], p.BoxHalfExtents[2]);
                            WritesBoxBound = true;
                        }
                        if (p.CollisionLayer != null)
                        {
                            if (TryVanilla(p.CollisionLayer, "CollisionLayer", out var layerKey)
                                && _vanilla.TryResolve<ICollisionLayerGetter>(layerKey, out var layer))
                            {
                                obj.CollisionLayer = layer.Index;
                                PlacedLayers[p.EditorId] = layer.Index;
                                if (sample != null && sample.Triggers > 0 && sample.MostUsedLayer != layer.Index)
                                    VanillaNotes.Add($"NOTE {p.EditorId}: uses collision layer {p.CollisionLayer} (index {layer.Index}); most of the game's box triggers sampled use {sample.Describe(sample.MostUsedLayer)}");
                            }
                            else
                                Pending.Add($"{p.EditorId}: placed without a collision layer (no '{p.CollisionLayer}' in Fallout4.esm)");
                        }
                    }
                    cell.Persistent.Add(obj);
                }
                _placed.Add(p.EditorId, keys[p.EditorId]);
                var within = arrival.Holds(position) switch
                {
                    true => "; seen from above, within the span of the room's own objects",
                    false => "; NOTE: seen from above, outside the span of the room's own objects, so likely outside the room",
                    null => "",
                };
                VanillaNotes.Add($"{p.EditorId}: placed in {group.Key} at ({position.X:0.#}, {position.Y:0.#}, {position.Z:0.#}): {p.Ahead:0.#} ahead of the arrival point, {p.Right:0.#} to its right, {p.Up:0.#} up{within}");
            }
        }
    }

    /// <summary>
    /// The name of a cell is text, and the game keeps its text apart from the
    /// master, in strings files; the master holds a number for it. This
    /// plugin holds its text itself, so the copy needs the name as text. It is
    /// read here, once, and put into the copy as plain text, so that nothing
    /// has to be looked up when the plugin is written. If the strings cannot
    /// be read the copy has no name: the room is then nameless while this
    /// plugin is loaded, and the build says so.
    /// </summary>
    void CopyCellName(ICellGetter source, ICell copy, string cellId)
    {
        var localized = _vanillaMod != null && _vanillaMod.ModHeader.Flags.HasFlag(Fallout4ModHeader.HeaderFlag.Localized);
        string? name = null;
        string? failure = null;
        try { name = source.Name?.String; }
        catch (Exception e) { failure = $"{e.GetType().Name}: {e.Message}"; }
        if (string.IsNullOrEmpty(name)) name = null;
        copy.Name = name;
        CellNames[cellId] = name;
        var how = localized ? "the master keeps its text in strings files" : "the master holds its text itself";
        if (name != null)
            VanillaNotes.Add($"{cellId}: its name is '{name}' ({how}); this plugin's copy of the cell carries it");
        else if (failure != null)
            VanillaNotes.Add($"NOTE {cellId}: its name could not be read ({failure}; {how}); this plugin's copy of the cell has none, so the room is nameless while the plugin is loaded");
        else if (localized)
            VanillaNotes.Add($"NOTE {cellId}: no name was read for it ({how}; either the cell has none or the strings were not found); this plugin's copy of the cell has none");
        else
            VanillaNotes.Add($"{cellId}: it has no name");
    }

    /// <summary>
    /// Finds the block and sub-block the master files an interior cell under.
    /// The usual rule is the last decimal digit of the cell's id and the one
    /// before it; what the master really does is what counts, so it is read,
    /// and a difference from the rule is reported, not acted on.
    /// </summary>
    void NoteWhereFiled(FormKey cellKey, string cellId)
    {
        if (_vanillaMod == null) return;
        foreach (var block in _vanillaMod.Cells.Records)
            foreach (var sub in block.SubBlocks)
                foreach (var cell in sub.Cells)
                {
                    if (cell.FormKey != cellKey) continue;
                    CellsFiled[cellId] = (block.BlockNumber, sub.BlockNumber);
                    var (ruleBlock, ruleSub) = ((int)(cellKey.ID % 10), (int)(cellKey.ID / 10 % 10));
                    var rule = (block.BlockNumber, sub.BlockNumber) == (ruleBlock, ruleSub)
                        ? "as its id asks"
                        : $"NOTE: its id would ask for block {ruleBlock}, sub-block {ruleSub}";
                    VanillaNotes.Add($"{cellId}: an interior cell, filed in the master under block {block.BlockNumber}, sub-block {sub.BlockNumber} ({rule})");
                    return;
                }
        VanillaNotes.Add($"NOTE {cellId}: not among the master's interior cells; this builder has only ever placed things in an interior cell");
    }

    static float NormalizeAngle(float radians)
    {
        var full = 2 * MathF.PI;
        var r = radians % full;
        return r < 0 ? r + full : r;
    }

    /// <summary>
    /// Things about <see cref="Spec.Placed"/> that can be wrong without the game:
    /// a trigger that holds the spot where the player arrives (someone already
    /// inside never "enters" it), and two triggers that overlap.
    /// </summary>
    static void CheckPlacedSpec()
    {
        const float clear = 100f;      // further than a standing player reaches
        var boxes = Spec.Placed.Where(p => p.BoxHalfExtents != null).ToList();
        foreach (var p in boxes)
        {
            var h = p.BoxHalfExtents!;
            if (h.Length != 3 || h.Any(x => x <= 0)) throw new InvalidOperationException($"{p.EditorId}: a box needs three sizes above zero");
            if (MathF.Abs(p.Right) <= h[0] + clear && MathF.Abs(p.Ahead) <= h[1] + clear)
                throw new InvalidOperationException($"{p.EditorId}: the box holds, or nearly holds, the spot where the player arrives");
        }
        for (var i = 0; i < boxes.Count; i++)
            for (var j = i + 1; j < boxes.Count; j++)
            {
                var (a, b) = (boxes[i], boxes[j]);
                if (!string.Equals(a.Cell, b.Cell, StringComparison.OrdinalIgnoreCase)) continue;
                var apart = MathF.Abs(a.Right - b.Right) > a.BoxHalfExtents![0] + b.BoxHalfExtents![0]
                         || MathF.Abs(a.Ahead - b.Ahead) > a.BoxHalfExtents[1] + b.BoxHalfExtents[1]
                         || MathF.Abs(a.Up - b.Up) > a.BoxHalfExtents[2] + b.BoxHalfExtents[2];
                if (!apart) throw new InvalidOperationException($"{a.EditorId} and {b.EditorId}: the two boxes overlap");
            }
    }

    /// <summary>
    /// The cell's arrival marker: where the console command "coc" puts the
    /// player. Without one the origin is used, and said so.
    /// </summary>
    Arrival FindArrival(ICellGetter cell, string cellId)
    {
        const string markerId = "COCMarkerHeading";
        var none = new Arrival(new P3Float(0, 0, 0), 0f, false);
        List<IPlacedObjectGetter> objects;
        P3Float? low = null, high = null;
        try
        {
            objects = cell.Persistent.Concat(cell.Temporary).OfType<IPlacedObjectGetter>().ToList();
            if (objects.Count > 0)
            {
                low = new P3Float(objects.Min(o => o.Position.X), objects.Min(o => o.Position.Y), objects.Min(o => o.Position.Z));
                high = new P3Float(objects.Max(o => o.Position.X), objects.Max(o => o.Position.Y), objects.Max(o => o.Position.Z));
                // How big the room is, to judge where things were put and where more could go.
                VanillaNotes.Add($"{cellId}: its {objects.Count} placed objects lie between ({low.Value.X:0.#}, {low.Value.Y:0.#}, {low.Value.Z:0.#}) and ({high.Value.X:0.#}, {high.Value.Y:0.#}, {high.Value.Z:0.#})");
            }
        }
        catch (Exception e)
        {
            // Where things go matters less than that they are there: the
            // scenario moves the player to them. So a cell whose contents the
            // library cannot read is no reason to stop the build.
            VanillaNotes.Add($"NOTE {cellId}: its placed objects could not be read ({e.GetType().Name}: {e.Message}); placing from the origin (0, 0, 0)");
            return none;
        }
        none = none with { Low = low, High = high };
        FormKey markerBase = FormKey.Null;
        if (!TryVanilla(markerId, "Static", out markerBase) && !TryVanilla(markerId, "Activator", out markerBase))
        {
            VanillaNotes.Add($"{cellId}: no arrival marker base '{markerId}' in Fallout4.esm; placing from the origin (0, 0, 0)");
            return none;
        }
        var markers = objects.Where(o => o.Base.FormKey == markerBase).ToList();
        if (markers.Count == 0)
        {
            VanillaNotes.Add($"{cellId}: none of its {objects.Count} placed objects is an arrival marker ({markerId}); placing from the origin (0, 0, 0)");
            return none;
        }
        var m = markers[0];
        VanillaNotes.Add($"{cellId}: arrival marker {m.FormKey} at ({m.Position.X:0.#}, {m.Position.Y:0.#}, {m.Position.Z:0.#}), heading {m.Rotation.Z * 180 / MathF.PI:0.#} degrees"
            + (markers.Count > 1 ? $" (the first of {markers.Count})" : ""));
        return new Arrival(m.Position, m.Rotation.Z, true, low, high);
    }

    /// <summary>What a look at some of the game's own box triggers found.</summary>
    sealed class TriggerSample
    {
        public int Cells;
        public int Triggers;
        public int WithBound;                                 // carry their reach a second time, as a bound
        public int BoundAgrees;                               // ... and the two agree
        public Dictionary<long, int> ByLayer = new();        // -1: no collision layer given
        public Dictionary<uint, string> LayerNames = new();
        public IPlacedPrimitiveGetter? Template;
        public FormKey TemplateFrom;
        public bool MostCarryBound => Triggers > 0 && WithBound * 2 > Triggers;
        public long MostUsedLayer => ByLayer.Count == 0 ? -1 : ByLayer.OrderByDescending(kv => kv.Value).ThenBy(kv => kv.Key).First().Key;
        public string Describe(long layer) => layer < 0
            ? "none"
            : LayerNames.TryGetValue((uint)layer, out var name) ? $"{name} (index {layer})" : $"index {layer}";
    }

    /// <summary>
    /// Looks at box triggers in the game's own interior cells: which collision
    /// layers they use, and what the box of one of them looks like. Reported
    /// in the build output, so that a trigger of ours that does not work can
    /// be compared with ones that do. It stops after a few hundred.
    /// </summary>
    TriggerSample SampleGameTriggers()
    {
        const int maxCells = 400, maxTriggers = 300;
        var sample = new TriggerSample();
        if (_vanilla == null || _vanillaMod == null) return sample;
        try
        {
            foreach (var layer in _vanillaMod.CollisionLayers)
                if (layer.EditorID != null) sample.LayerNames[layer.Index] = layer.EditorID;
            foreach (var block in _vanillaMod.Cells.Records)
            {
                foreach (var sub in block.SubBlocks)
                {
                    foreach (var cell in sub.Cells)
                    {
                        sample.Cells++;
                        foreach (var placed in cell.Persistent.Concat(cell.Temporary).OfType<IPlacedObjectGetter>())
                        {
                            var primitive = placed.Primitive;
                            if (primitive == null || primitive.Type != PlacedPrimitive.TypeEnum.Box) continue;
                            if (!_vanilla.TryResolve<IActivatorGetter>(placed.Base.FormKey, out _)) continue;
                            sample.Triggers++;
                            if (placed.BoundHalfExtents is { } bound)
                            {
                                sample.WithBound++;
                                // the library gives the primitive's whole sizes
                                if (MathF.Abs(bound.X - primitive.Bounds.X / 2) < 0.01f && MathF.Abs(bound.Y - primitive.Bounds.Y / 2) < 0.01f
                                    && MathF.Abs(bound.Z - primitive.Bounds.Z / 2) < 0.01f) sample.BoundAgrees++;
                            }
                            var key = placed.CollisionLayer.HasValue ? placed.CollisionLayer.Value : -1L;
                            sample.ByLayer[key] = sample.ByLayer.GetValueOrDefault(key) + 1;
                            if (sample.Template == null)
                            {
                                sample.Template = primitive;
                                sample.TemplateFrom = placed.FormKey;
                            }
                        }
                        if (sample.Cells >= maxCells || sample.Triggers >= maxTriggers) goto done;
                    }
                }
            }
            done:;
        }
        catch (Exception e)
        {
            // The sample is for information. What was counted so far is still reported.
            VanillaNotes.Add($"the look at the game's own box triggers stopped early: {e.GetType().Name}: {e.Message}");
        }
        if (sample.Triggers == 0)
            VanillaNotes.Add($"the game's own box triggers: none found in {sample.Cells} interior cells; the box is drawn with this builder's own colour");
        else
        {
            var layers = string.Join(", ", sample.ByLayer.OrderByDescending(kv => kv.Value).ThenBy(kv => kv.Key).Select(kv => $"{sample.Describe(kv.Key)} x {kv.Value}"));
            var t = sample.Template!;
            VanillaNotes.Add($"the game's own box triggers, {sample.Triggers} in {sample.Cells} interior cells: collision layer {layers}");
            VanillaNotes.Add($"of those {sample.Triggers}, {sample.WithBound} carry the box's reach a second time, as the reference's bound, and in {sample.BoundAgrees} the two agree; "
                + (sample.MostCarryBound ? "this build writes it too, as most of them do" : "this build does not write it, as most of them do not"));
            VanillaNotes.Add($"the box's colour and unknown number are copied from {sample.TemplateFrom}: colour ({t.Color.R}, {t.Color.G}, {t.Color.B}), unknown {t.Unknown:0.###}; that box reaches ({t.Bounds.X / 2:0.#}, {t.Bounds.Y / 2:0.#}, {t.Bounds.Z / 2:0.#}) from its middle");
        }
        return sample;
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
                case Tlm.PluginBuilder.Fill.Placed:
                    // Optional even when filled: an alias that stays empty in
                    // the game is then reported by name, and the quest starts.
                    aliasFlags |= AQuestAlias.Flag.Optional;
                    if (_placed.TryGetValue(a.Placed ?? throw new InvalidOperationException($"{spec.EditorId} alias {a.Name}: no placed reference named"), out var placedKey))
                        alias.ForcedReference = new FormLinkNullable<IPlacedGetter>(placedKey);
                    else
                        Pending.Add($"{spec.EditorId} alias {a.Name}: its reference {a.Placed} is not placed");
                    break;
                default:
                    aliasFlags |= AQuestAlias.Flag.Optional;
                    Pending.Add($"{spec.EditorId} alias {a.Name}: no reference yet ({a.Note ?? "placed in the test cell"})");
                    break;
            }
            if (a.DisplayName != null) alias.DisplayName.SetTo(Local(a.DisplayName).FormKey);
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

    /// <summary>The number of an alias on one of this plugin's quests, by the names the spec gives them.</summary>
    static int AliasIndex(string questId, string alias)
    {
        var quest = Spec.Quests.FirstOrDefault(q => string.Equals(q.EditorId, questId, StringComparison.OrdinalIgnoreCase))
                    ?? throw new InvalidOperationException($"Spec refers to an alias of '{questId}', which is not a quest of this plugin");
        var index = Array.FindIndex(quest.Aliases, a => string.Equals(a.Name, alias, StringComparison.OrdinalIgnoreCase));
        return index >= 0 ? index : throw new InvalidOperationException($"{questId}: no alias named '{alias}'");
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
                        Object = ap.Quest == null ? quest.ToLink<IFallout4MajorRecordGetter>() : Local(ap.Quest).ToLink<IFallout4MajorRecordGetter>(),
                        Alias = checked((short)(ap.Quest == null ? aliasId(ap.Alias) : AliasIndex(ap.Quest, ap.Alias))),
                    });
                    break;
                case AliasListProp alp:
                    var aliases = new ScriptObjectListProperty { Name = alp.Name, Flags = ScriptProperty.Flag.Edited };
                    foreach (var (ofQuest, alias) in alp.Items)
                        aliases.Objects.Add(new ScriptObjectProperty
                        {
                            Object = Local(ofQuest).ToLink<IFallout4MajorRecordGetter>(),
                            Alias = checked((short)AliasIndex(ofQuest, alias)),
                        });
                    entry.Properties.Add(aliases);
                    break;
                case StringListProp slp:
                    var strings = new ScriptStringListProperty { Name = slp.Name, Flags = ScriptProperty.Flag.Edited };
                    strings.Data.AddRange(slp.Values);
                    entry.Properties.Add(strings);
                    break;
                case VanillaNamedProp vnp:
                    if (TryVanillaNamed(vnp.Kind, vnp.Names, $"{spec.EditorId} script {bind.Script}.{vnp.Name}", needsModel: false, out var namedKey, out _, out _, out _))
                        entry.Properties.Add(new ScriptObjectProperty
                        {
                            Name = vnp.Name,
                            Flags = ScriptProperty.Flag.Edited,
                            Object = new FormLink<IFallout4MajorRecordGetter>(namedKey),
                            Alias = -1,
                        });
                    else
                        Pending.Add($"{spec.EditorId} script {bind.Script}.{vnp.Name}: needs a {vnp.Kind} named {string.Join(" or ", vnp.Names.Select(n => $"'{n}'"))} from Fallout4.esm");
                    break;
                case AmmoOfWeaponNamedProp awp:
                    var what = $"{spec.EditorId} script {bind.Script}.{awp.Name}";
                    if (TryVanillaNamed("Weapon", awp.WeaponNames, what, needsModel: false, out var weaponKey, out _, out _, out _)
                        && _vanilla!.TryResolve<IWeaponGetter>(weaponKey, out var weapon) && !weapon.Ammo.IsNull)
                    {
                        var ammoKey = weapon.Ammo.FormKey;
                        var ammoId = _vanilla.TryResolve<IAmmunitionGetter>(ammoKey, out var ammo) ? ammo.EditorID : null;
                        VanillaNotes.Add($"{what}: what that weapon fires -> {ammoKey} (Ammunition {ammoId ?? "with no EditorID"})");
                        var ammoText = ammoKey.ToString();
                        if (!VanillaFound.Any(v => v.FormKey == ammoText)) VanillaFound.Add(new(ammoId ?? "Ammunition", ammoText, "Ammunition"));
                        entry.Properties.Add(new ScriptObjectProperty
                        {
                            Name = awp.Name,
                            Flags = ScriptProperty.Flag.Edited,
                            Object = new FormLink<IFallout4MajorRecordGetter>(ammoKey),
                            Alias = -1,
                        });
                    }
                    else
                        Pending.Add($"{what}: needs what a weapon named {string.Join(" or ", awp.WeaponNames.Select(n => $"'{n}'"))} fires, from Fallout4.esm");
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
    // (the link cache is asked through its untyped face here; placing things needs the typed one)

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
        ("CollisionLayer", Typed<ICollisionLayerGetter>),
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
        ILinkCache<IFallout4Mod, IFallout4ModGetter>? vanilla = null;
        IFallout4ModGetter? master = null;
        if (fallout4Esm != null)
        {
            master = Fallout4Mod.CreateFromBinaryOverlay(fallout4Esm, Fallout4Release.Fallout4);
            vanilla = master.ToImmutableLinkCache<IFallout4Mod, IFallout4ModGetter>();
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
