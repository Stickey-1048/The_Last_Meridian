using Mutagen.Bethesda;
using Mutagen.Bethesda.Fallout4;
using Noggog;
using System.Text.Json;
using System.Security.Cryptography;
public static class OpeningWreckTableau
{
 public static object Add(IFallout4ModGetter native,Fallout4Mod mod,Cell cell)
 {
  if(cell.FormKey.ID!=0x802||cell.Grid?.Point!=new P2Int(0,0))throw new InvalidDataException("Wreck spill must remain in original corecell");
  byte[] data=File.ReadAllBytes(Path.Combine(AppContext.BaseDirectory,"../../../../OpeningWreckTableau/placements.json"));
  if(Convert.ToHexString(SHA256.HashData(data))!="FFF45749ECDBFF629B750B57681FC2B9FC8625C58764A4CC5A181004C86479CA")throw new InvalidDataException("Measured wreck spill plan differs");
  using var plan=JsonDocument.Parse(data);int index=0;var added=new List<object>();
  foreach(var row in plan.RootElement.GetProperty("placements").EnumerateArray()){
   uint id=Convert.ToUInt32(row.GetProperty("donorId").GetString(),16);string asset=row.GetProperty("asset").GetString()!,model=row.GetProperty("model").GetString()!;
   var donor=native.Statics.Single(s=>s.FormKey.ID==id&&s.EditorID==asset);
   if(donor.Model?.File?.ToString()!=model||donor.VirtualMachineAdapter!=null||row.GetProperty("scale").GetSingle()!=1)throw new InvalidDataException("Selected passive stock wreck donor differs");
   var p=row.GetProperty("xyz");var r=new PlacedObject(mod.GetNextFormKey(),Fallout4Release.Fallout4){EditorID=row.GetProperty("id").GetString(),Position=new P3Float(p[0].GetSingle(),p[1].GetSingle(),p[2].GetSingle()),Rotation=new P3Float(0,0,row.GetProperty("yaw").GetSingle())};
   if(r.FormKey.ID!=0xB78+index)throw new InvalidDataException("Wreck spill must append after three batch sounds");
   r.Base.SetTo(donor.FormKey);cell.Temporary.Add(r);added.Add(new{id=r.EditorID,form=r.FormKey.ToString(),donor=donor.FormKey.ToString()});index++;
  }
  if(index!=7)throw new InvalidDataException("Only seven measured wreck additions authorized");
  return new{scope="Seven passive cargo/broken timber refs only; no old placement/terrain/actor/quest/audio/smoke change",added};
 }
}
