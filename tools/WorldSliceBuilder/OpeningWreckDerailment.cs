using Mutagen.Bethesda.Fallout4;
using Noggog;
using System.Text.Json;
public static class OpeningWreckDerailment
{
 public static object Apply(Fallout4Mod mod,Worldspace world)
 {
  var refs=world.TopCell!.Persistent.OfType<PlacedObject>().Concat(world.SubCells.SelectMany(b=>b.Items).SelectMany(b=>b.Items).SelectMany(c=>c.Temporary).OfType<PlacedObject>()).ToArray();
  var path=Path.GetFullPath(Path.Combine(AppContext.BaseDirectory,"../../../../OpeningWreckDerailment/plan.json"));
  byte[] bytes=File.ReadAllBytes(path);
  if(Convert.ToHexString(System.Security.Cryptography.SHA256.HashData(bytes))!="C23C19DC4AF60DF6963BCEBF271B4EF775AF7187DDC49FED48626BF55B9A9414")throw new InvalidDataException("Measured two-reference derailment plan changed");
  using var plan=JsonDocument.Parse(bytes);
  var changed=new List<object>();
  foreach(var p in plan.RootElement.GetProperty("moves").EnumerateArray()){
   string id=p.GetProperty("reference").GetString()!;var r=refs.Single(r=>r.EditorID==id);
   uint expected=id=="TLM_WS_EX_WreckBoxcar"?0x943u:id=="TLM_WS_EX_WreckBogie"?0x944u:throw new InvalidDataException("Unexpected derailment reference");
   uint donor=id=="TLM_WS_EX_WreckBoxcar"?0x5CA0Bu:0x5CA12u;
   if(r.FormKey.ID!=expected||r.Base.FormKey.ID!=donor)throw new InvalidDataException("Original wreck binding changed");
   var old=p.GetProperty("oldPose").EnumerateArray().Select(q=>q.GetSingle()).ToArray();
   if(r.Position!=new P3Float(old[0],old[1],old[2])||r.Rotation!=new P3Float(old[3],old[4],old[5]))throw new InvalidDataException("Original wreck pose changed");
   var v=p.GetProperty("candidatePose").EnumerateArray().Select(q=>q.GetSingle()).ToArray();
   r.Position=new P3Float(v[0],v[1],v[2]);r.Rotation=new P3Float(v[3],v[4],v[5]);changed.Add(new{id,form=r.FormKey.ToString(),oldPose=old,pose=v});
  }
  if(changed.Count!=2)throw new InvalidDataException("Exactly two wreck poses required");
  return new{scope="Two existing wreck DATA poses only; declared clockwise rotation basis. Engine orientation/Havok/native appearance unproved",changed};
 }
}
