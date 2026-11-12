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
//                    one built on the game PC does.
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

var lowIds = variant != "default";
var caps = new MiscItem(lowIds ? Key(0xF) : mod.GetNextFormKey(), Fallout4Release.Fallout4) { EditorID = "Caps001", Name = "Bottlecap" };
mod.MiscItems.Add(caps);
var player = new Npc(lowIds ? Key(0x7) : mod.GetNextFormKey(), Fallout4Release.Fallout4) { EditorID = "Player" };
mod.Npcs.Add(player);
var someoneElse = mod.Npcs.AddNew("SomeoneElse");
string fixtures = "";
if (variant == "default")
{
    var settler = mod.Npcs.AddNew("WorkshopNPC");
    var marker = mod.Statics.AddNew("XMarker");
    fixtures = $" WorkshopNPC={settler.FormKey} XMarker={marker.FormKey}";
}

var cell = new Cell(mod.GetNextFormKey(), Fallout4Release.Fallout4) { EditorID = "StandInCell" };

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

var block = new CellBlock { BlockNumber = 0, GroupType = GroupTypeEnum.InteriorCellBlock };
var sub = new CellSubBlock { BlockNumber = 0, GroupType = GroupTypeEnum.InteriorCellSubBlock };
sub.Cells.Add(cell);
block.SubBlocks.Add(sub);
mod.Cells.Records.Add(block);

Directory.CreateDirectory(Path.GetDirectoryName(Path.GetFullPath(path))!);
// Real masters use ids below 0x800; a stand-in may too.
mod.BeginWrite.ToPath(path).WithNoLoadOrder().NoCheckIfLowerRangeDisallowed().Write();
Console.WriteLine($"wrote stand-in master ({variant}): Caps001={caps.FormKey} player reference={(placed == null ? "none" : $"{placed.FormKey} EditorID='{placed.EditorID}'")}{fixtures}");
return 0;
