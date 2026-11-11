// Builds a tiny stand-in "Fallout4.esm" holding only the two vanilla records
// the plugin builder looks up by EditorID. For testing the lookup code path;
// it is not game data.
using Mutagen.Bethesda;
using Mutagen.Bethesda.Fallout4;
using Mutagen.Bethesda.Plugins;
using Noggog;

var mod = new Fallout4Mod(ModKey.FromNameAndExtension("Fallout4.esm"), Fallout4Release.Fallout4);
var caps = mod.MiscItems.AddNew("Caps001");
caps.Name = "Bottlecap";
var npc = mod.Npcs.AddNew("Player");
var cell = new Cell(mod.GetNextFormKey(), Fallout4Release.Fallout4) { EditorID = "StandInCell" };
var placed = new PlacedNpc(mod.GetNextFormKey(), Fallout4Release.Fallout4) { EditorID = "PlayerRef" };
placed.Base.SetTo(npc);
cell.Persistent.Add(placed);
var block = new CellBlock { BlockNumber = 0, GroupType = GroupTypeEnum.InteriorCellBlock };
var sub = new CellSubBlock { BlockNumber = 0, GroupType = GroupTypeEnum.InteriorCellSubBlock };
sub.Cells.Add(cell);
block.SubBlocks.Add(sub);
mod.Cells.Records.Add(block);
mod.BeginWrite.ToPath(args[0]).WithNoLoadOrder().Write();
Console.WriteLine($"wrote {args[0]}: Caps001={caps.FormKey} PlayerRef={placed.FormKey}");
