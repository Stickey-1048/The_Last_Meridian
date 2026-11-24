using Mutagen.Bethesda.Fallout4;
using Noggog;
namespace Tlm.PluginBuilder;
// Native-image access repair only. Existing activators/aliases/scripts unchanged.
public static class RedHollowAccess {
 public const string Desk="HighTechDesk01_Main_DirtyStatic";
 public static readonly PlacedSpec[] Supports={
  new("TLM_REF_RHE_AccessRosterDesk",RedHollow.CellId,Desk,"Static",640,6144,0,false),
  new("TLM_REF_RHE_AccessFiringDesk",RedHollowEnvironment.Persistent,Desk,"Static",384,2816,0,false)
 };
}
public sealed partial class Builder {
 void BuildRedHollowAccess(){
  if(_vanillaMod==null)return;
  var desk=_vanillaMod.Statics.Single(s=>s.FormKey.ID==0x1A6E6A&&s.EditorID==RedHollowAccess.Desk);
  var b=desk.ObjectBounds;
  if(desk.Model?.File?.ToString()!=@"SetDressing\HighTech\HighTechTable01_Main.nif"||!new[]{b.First.X,b.First.Y,b.First.Z,b.Second.X,b.Second.Y,b.Second.Z}.SequenceEqual(new short[]{-54,-26,0,55,26,56})||desk.VirtualMachineAdapter!=null||desk.GetType().GetProperty("Destructible")?.GetValue(desk)!=null)throw new InvalidDataException("RH access passive desk donor changed");
  foreach(var p in RedHollowAccess.Supports){
   var r=new PlacedObject(_mod.GetNextFormKey(p.EditorId),Fallout4Release.Fallout4){EditorID=p.EditorId,Position=new P3Float(p.Right,p.Ahead,p.Up),Rotation=new P3Float(0,0,0),MajorRecordFlagsRaw=0x400};r.Base.SetTo(desk.FormKey);
   var cell=p.Cell==RedHollowEnvironment.Persistent?_mod.Worldspaces.Single(w=>w.EditorID==RedHollowEnvironment.World).TopCell!:_mod.Cells.Records.SelectMany(b=>b.SubBlocks).SelectMany(s=>s.Cells).Single(c=>c.EditorID==RedHollow.CellId);
   cell.Persistent.Add(r);_placed[p.EditorId]=r.FormKey;
  }
 }
}

