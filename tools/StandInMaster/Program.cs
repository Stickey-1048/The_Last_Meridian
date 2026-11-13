// Builds a tiny stand-in "Fallout4.esm" holding only the vanilla records the
// plugin builder looks up. For testing the lookup code path; it is not game data.
//
//   StandInMaster <output path> [variant]
//
// Variants:
//   default          The player reference is spelled "PlayerREF". On the real
//                    master a lookup for "PlayerRef" failed until the lookup
//                    stopped depending on letter case; this keeps that covered.
//                    Also holds an actor "WorkshopNPC" and a static "XMarker",
//                    the two forms the self-test makes its stand-ins from, so
//                    a plugin built against this file has them wired as the
//                    one built on the game PC does. And a test room "QASmoke"
//                    with an arrival marker, a few collision layers, an empty
//                    trigger base and some box triggers in other rooms: what
//                    the builder needs to place references in a cell of the
//                    game. All of it is invented here; none of it is the
//                    game's data, and the numbers are not the game's numbers.
//   bare-room        The test room exists, but with no arrival marker; and the
//                    master has no collision layers, no empty trigger base and
//                    no triggers of its own. The builder must still place what
//                    it can, from the origin, and say what it could not do.
//   unnamed-player   The player reference has no EditorID at all and sits at
//                    the conventional id 0x14. Exercises the builder's fallback.
//   wrong-player     Record 0x14 places some other actor. The builder must
//                    refuse to use it.
//   quest-evidence   No player reference record at all (what the library saw on
//                    the real master), but a dozen quests force 0x14 into an
//                    alias named "Player". The builder should accept 0x14.
//   weak-evidence    The same with only two such quests. The builder must refuse.
using Mutagen.Bethesda;
using Mutagen.Bethesda.Fallout4;
using Mutagen.Bethesda.Plugins;
using Noggog;

var path = args[0];
var variant = args.Length > 1 ? args[1] : "default";
var mod = new Fallout4Mod(ModKey.FromNameAndExtension("Fallout4.esm"), Fallout4Release.Fallout4);
FormKey Key(uint id) => new(mod.ModKey, id);

var room = variant is "default" or "bare-room";
var lowIds = !room;
var caps = new MiscItem(lowIds ? Key(0xF) : mod.GetNextFormKey(), Fallout4Release.Fallout4) { EditorID = "Caps001", Name = "Bottlecap" };
// An invented path, so that the builder has a world model to borrow.
caps.Model = new Model { File = @"StandIn\Cap.nif" };
caps.ObjectBounds = new ObjectBounds { First = new P3Int16(-2, -2, 0), Second = new P3Int16(2, 2, 1) };
mod.MiscItems.Add(caps);
var player = new Npc(lowIds ? Key(0x7) : mod.GetNextFormKey(), Fallout4Release.Fallout4) { EditorID = "Player" };
mod.Npcs.Add(player);
var someoneElse = mod.Npcs.AddNew("SomeoneElse");
string fixtures = "";
var cells = new List<Cell>();
if (room)
{
    var settler = mod.Npcs.AddNew("WorkshopNPC");
    var marker = mod.Statics.AddNew("XMarker");
    fixtures = $" WorkshopNPC={settler.FormKey} XMarker={marker.FormKey}";

    // The test room. Something of the game's own lies in each of its two
    // lists: the builder's copy of the cell must not bring either along.
    var qaSmoke = new Cell(mod.GetNextFormKey(), Fallout4Release.Fallout4) { EditorID = "QASmoke" };
    var clutter = mod.Statics.AddNew("StandInClutter");
    PlacedObject Put(IFormLinkGetter<IPlaceableObjectGetter> what, float x, float y, float z, float headingDegrees = 0)
    {
        var placedObject = new PlacedObject(mod.GetNextFormKey(), Fallout4Release.Fallout4)
        {
            Position = new P3Float(x, y, z),
            Rotation = new P3Float(0, 0, headingDegrees * MathF.PI / 180),
        };
        placedObject.Base.SetTo(what.FormKey);
        return placedObject;
    }
    qaSmoke.Temporary.Add(Put(clutter.ToLink(), 10, 20, 0));
    qaSmoke.Persistent.Add(Put(clutter.ToLink(), -300, 40, 0));
    cells.Add(qaSmoke);

    if (variant == "default")
    {
        // Where "coc qasmoke" puts the player: off the origin and turned, so
        // that a mistake in the builder's arithmetic shows.
        var cocMarker = mod.Statics.AddNew("COCMarkerHeading");
        qaSmoke.Temporary.Add(Put(cocMarker.ToLink(), 1200, -800, 64, headingDegrees: 90));

        // Collision layers. The index is what a placed trigger stores.
        foreach (var (id, index) in new[] { ("L_UNIDENTIFIED", 0u), ("L_STATIC", 1u), ("L_TRIGGER", 12u), ("L_ACTORZONE", 22u) })
        {
            var layer = mod.CollisionLayers.AddNew(id);
            layer.Index = index;
        }

        // The game's empty trigger, and box triggers in two other rooms.
        var emptyTrigger = mod.Activators.AddNew("DefaultEmptyTrigger");
        var otherTrigger = mod.Activators.AddNew("StandInScriptedTrigger");
        for (var c = 0; c < 2; c++)
        {
            var otherRoom = new Cell(mod.GetNextFormKey(), Fallout4Release.Fallout4) { EditorID = $"StandInRoom{c}" };
            for (var i = 0; i < 5; i++)
            {
                var trigger = Put((i % 2 == 0 ? emptyTrigger : otherTrigger).ToLink(), 100 * i, 0, 0);
                trigger.Primitive = new PlacedPrimitive
                {
                    Bounds = new P3Float(64 + i, 96, 128),
                    Color = System.Drawing.Color.FromArgb(10, 200, 30),
                    Unknown = 0.25f,
                    Type = PlacedPrimitive.TypeEnum.Box,
                };
                // As the editor writes a box: its reach once more, as the reference's bound. One has none.
                if (i != 4) trigger.BoundHalfExtents = new P3Float((64 + i) / 2f, 48, 64);
                // Most on L_TRIGGER, some on L_ACTORZONE, one with none.
                if (i < 3) trigger.CollisionLayer = 12;
                else if (i == 3) trigger.CollisionLayer = 22;
                otherRoom.Temporary.Add(trigger);
            }
            // A sphere, and a box around something that is not an activator: neither is a box trigger.
            var sphere = Put(emptyTrigger.ToLink(), 0, 500, 0);
            sphere.Primitive = new PlacedPrimitive { Bounds = new P3Float(50, 50, 50), Type = PlacedPrimitive.TypeEnum.Sphere };
            otherRoom.Temporary.Add(sphere);
            var boxedStatic = Put(clutter.ToLink(), 0, 900, 0);
            boxedStatic.Primitive = new PlacedPrimitive { Bounds = new P3Float(50, 50, 50), Type = PlacedPrimitive.TypeEnum.Box };
            otherRoom.Temporary.Add(boxedStatic);
            cells.Add(otherRoom);
        }
    }
}

var cell = new Cell(mod.GetNextFormKey(), Fallout4Release.Fallout4) { EditorID = "StandInCell" };
cells.Add(cell);

// A second placed actor, so a lookup cannot succeed just by being the only one.
var other = new PlacedNpc(mod.GetNextFormKey(), Fallout4Release.Fallout4) { EditorID = "SomeoneElseRef" };
other.Base.SetTo(someoneElse);
cell.Persistent.Add(other);

PlacedNpc? placed = null;
switch (variant)
{
    case "quest-evidence":
    case "weak-evidence":
        for (var i = 0; i < (variant == "quest-evidence" ? 12 : 2); i++)
        {
            var quest = mod.Quests.AddNew($"StandInQuest{i:00}");
            quest.Aliases = new ExtendedList<AQuestAlias>
            {
                new QuestReferenceAlias { ID = 0, Name = i % 3 == 0 ? "PlayerRef" : "Player", ForcedReference = new FormLinkNullable<IPlacedGetter>(Key(0x14)) },
                new QuestReferenceAlias { ID = 1, Name = "SomeoneElse", ForcedReference = new FormLinkNullable<IPlacedGetter>(other.FormKey) },
            };
        }
        break;
    case "default":
    case "bare-room":
        placed = new PlacedNpc(mod.GetNextFormKey(), Fallout4Release.Fallout4) { EditorID = "PlayerREF" };
        placed.Base.SetTo(player);
        break;
    case "unnamed-player":
        placed = new PlacedNpc(Key(0x14), Fallout4Release.Fallout4);
        placed.Base.SetTo(player);
        break;
    case "wrong-player":
        placed = new PlacedNpc(Key(0x14), Fallout4Release.Fallout4);
        placed.Base.SetTo(someoneElse);
        break;
    default:
        Console.Error.WriteLine($"unknown variant: {variant}");
        return 2;
}
if (placed != null) cell.Persistent.Add(placed);

// An interior cell is filed under the last decimal digit of its id (the
// block) and the one before it (the sub-block).
foreach (var c in cells)
{
    var (blockNumber, subNumber) = ((int)(c.FormKey.ID % 10), (int)(c.FormKey.ID / 10 % 10));
    var block = mod.Cells.Records.FirstOrDefault(b => b.BlockNumber == blockNumber);
    if (block == null)
    {
        block = new CellBlock { BlockNumber = blockNumber, GroupType = GroupTypeEnum.InteriorCellBlock };
        mod.Cells.Records.Add(block);
    }
    var sub = block.SubBlocks.FirstOrDefault(s => s.BlockNumber == subNumber);
    if (sub == null)
    {
        sub = new CellSubBlock { BlockNumber = subNumber, GroupType = GroupTypeEnum.InteriorCellSubBlock };
        block.SubBlocks.Add(sub);
    }
    sub.Cells.Add(c);
}

Directory.CreateDirectory(Path.GetDirectoryName(Path.GetFullPath(path))!);
// Real masters use ids below 0x800; a stand-in may too.
mod.BeginWrite.ToPath(path).WithNoLoadOrder().NoCheckIfLowerRangeDisallowed().Write();
Console.WriteLine($"wrote stand-in master ({variant}): Caps001={caps.FormKey} player reference={(placed == null ? "none" : $"{placed.FormKey} EditorID='{placed.EditorID}'")}{fixtures}");
return 0;
