using Mutagen.Bethesda;
using Mutagen.Bethesda.Fallout4;
using Noggog;
public static class GanttRoofBacking
{
 public static object Add(IFallout4ModGetter native,Fallout4Mod mod)
 {
  var cell=mod.Cells.Records.SelectMany(b=>b.SubBlocks).SelectMany(b=>b.Cells).Single(c=>GanttPrologue.IsOwnCarriage(mod,c));
  var donor=native.Statics.Single(s=>s.FormKey.ID==0x8EB6E&&s.EditorID=="RRBoxcarDoor01Static");
  if(donor.Model?.File?.ToString()!=@"SetDressing\Railroad\RRBoxcarDoor01.nif"||donor.VirtualMachineAdapter!=null)throw new InvalidDataException("Verified opaque stock panel differs");
  var added=new List<object>();int i=0;
  // Full-parent native panel X107..113 becomes roof Z246..252 under clockwiseY+pi/2.
  // Its Z73.973..274.223 becomes X+/-100.125; six 200.75-wide panels overlap alongY.
  // Offline actual-triangle/frontface coverage is checked separately; not Havok/native opacity certification.
  foreach(float y in new float[]{-475,-285,-95,95,285,475}){
   var r=new PlacedObject(mod.GetNextFormKey(),Fallout4Release.Fallout4){EditorID="TLM_PROLOGUE_RoofBacker"+(++i),Position=new P3Float(174.098388671875f,y,139),Rotation=new P3Float(0,MathF.PI/2,0)};
   if(r.FormKey.ID!=0xB64+i)throw new InvalidDataException("Roof backers must append after voice B64");
   r.Base.SetTo(donor.FormKey);cell.Temporary.Add(r);added.Add(new{id=r.EditorID,form=r.FormKey.ToString(),donor=donor.FormKey.ToString(),xyz=new[]{r.Position.X,r.Position.Y,r.Position.Z},rotation=new[]{r.Rotation.X,r.Rotation.Y,r.Rotation.Z}});
  }
  return new{scope="Six own opaque stock roof backers only; no old geometry/light/actor/quest/material edits",added};
 }
}

