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

    /// <summary>The collision layer each placed trigger was given: the index the master has for the layer the spec names.</summary>
    public Dictionary<string, uint> PlacedLayers { get; } = new(StringComparer.OrdinalIgnoreCase);

    /// <summary>True when this build gave its boxes a bound as well (it does as most of the game's own box triggers do).</summary>
    public bool WritesBoxBound { get; private set; }

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
            if (m.ModelFrom == null)
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

        // Before the quests are filled in: their aliases point at these.
        PlaceReferences();

        foreach (var q in Spec.Quests) Fill(quests[q.EditorId], q);
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

    /// <summary>Where the player arrives in a cell, and which way the player then faces.</summary>
    sealed record Arrival(P3Float Position, float Heading, bool Found);

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
                if (p.VanillaKind == null) baseKey = Local(p.Base).FormKey;
                else if (!TryVanilla(p.Base, p.VanillaKind, out baseKey))
                {
                    Pending.Add($"{p.EditorId}: not placed (no {p.VanillaKind} '{p.Base}' in Fallout4.esm)");
                    continue;
                }

                var (sin, cos) = (MathF.Sin(arrival.Heading), MathF.Cos(arrival.Heading));
                // Heading is measured from north (+Y) towards east (+X): ahead is (sin, cos), right is (cos, -sin).
                var position = new P3Float(
                    arrival.Position.X + p.Ahead * sin + p.Right * cos,
                    arrival.Position.Y + p.Ahead * cos - p.Right * sin,
                    arrival.Position.Z + p.Up);
                var flags = PersistentFlag | (p.InitiallyDisabled ? InitiallyDisabledFlag : 0u);
                var isNpc = string.Equals(p.VanillaKind, "Npc", StringComparison.OrdinalIgnoreCase);
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
                VanillaNotes.Add($"{p.EditorId}: placed in {group.Key} at ({position.X:0.#}, {position.Y:0.#}, {position.Z:0.#}): {p.Ahead:0.#} ahead of the arrival point, {p.Right:0.#} to its right, {p.Up:0.#} up");
            }
        }
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
        FormKey markerBase = FormKey.Null;
        if (!TryVanilla(markerId, "Static", out markerBase) && !TryVanilla(markerId, "Activator", out markerBase))
        {
            VanillaNotes.Add($"{cellId}: no arrival marker base '{markerId}' in Fallout4.esm; placing from the origin (0, 0, 0)");
            return none;
        }
        List<IPlacedObjectGetter> objects;
        List<IPlacedObjectGetter> markers;
        try
        {
            objects = cell.Persistent.Concat(cell.Temporary).OfType<IPlacedObjectGetter>().ToList();
            markers = objects.Where(o => o.Base.FormKey == markerBase).ToList();
        }
        catch (Exception e)
        {
            // Where things go matters less than that they are there: the
            // scenario moves the player to them. So a cell whose contents the
            // library cannot read is no reason to stop the build.
            VanillaNotes.Add($"NOTE {cellId}: its placed objects could not be read ({e.GetType().Name}: {e.Message}); placing from the origin (0, 0, 0)");
            return none;
        }
        if (markers.Count == 0)
        {
            VanillaNotes.Add($"{cellId}: none of its {objects.Count} placed objects is an arrival marker ({markerId}); placing from the origin (0, 0, 0)");
            return none;
        }
        var m = markers[0];
        VanillaNotes.Add($"{cellId}: arrival marker {m.FormKey} at ({m.Position.X:0.#}, {m.Position.Y:0.#}, {m.Position.Z:0.#}), heading {m.Rotation.Z * 180 / MathF.PI:0.#} degrees"
            + (markers.Count > 1 ? $" (the first of {markers.Count})" : "") + $"; the cell has {objects.Count} placed objects");
        return new Arrival(m.Position, m.Rotation.Z, true);
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
