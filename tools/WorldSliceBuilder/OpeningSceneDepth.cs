using Mutagen.Bethesda.Fallout4;
using Mutagen.Bethesda.Plugins;
using Noggog;
using System.Text.Json;

// Passive close-range art only, allocated after every accepted ridge/reference.
public static class OpeningSceneDepth {
 public static object Apply(IFallout4ModGetter native,Fallout4Mod mod,Cell cell){
  var dir=new DirectoryInfo(AppContext.BaseDirectory);while(dir!=null&&!File.Exists(Path.Combine(dir.FullName,"tools/OpeningSceneDepth/placements.json")))dir=dir.Parent;
  if(dir==null)throw new InvalidDataException("Opening scene placement source absent");
  using var data=JsonDocument.Parse(File.ReadAllText(Path.Combine(dir.FullName,"tools/OpeningSceneDepth/placements.json")));
  using var metadata=JsonDocument.Parse(File.ReadAllText(Path.Combine(dir.FullName,"tools/OpeningSceneDepth/models.json")));var assets=metadata.RootElement.GetProperty("assets");
  var refs=new List<object>();
  foreach(var p in data.RootElement.GetProperty("placements").EnumerateArray()){
   string asset=p.GetProperty("asset").GetString()!,id=p.GetProperty("id").GetString()!;var a=assets.GetProperty(asset);
   var donor=native.Statics.Single(s=>s.EditorID==asset&&s.FormKey.ID==Convert.ToUInt32(a.GetProperty("id").GetString(),16));
   if(donor.Model?.File?.ToString()!=a.GetProperty("model").GetString()||donor.VirtualMachineAdapter!=null)throw new InvalidDataException("Scene passive owned donor mismatch");
   float x=p.GetProperty("x").GetSingle(),y=p.GetProperty("y").GetSingle(),z=p.GetProperty("z").GetSingle(),yaw=p.GetProperty("yaw").GetSingle(),scale=p.GetProperty("scale").GetSingle();
   if(x<64||x>4032||y<64||y>4032||scale<=0||scale>2)throw new InvalidDataException("Scene pose outside bounded opening");
   var placed=new PlacedObject(mod.GetNextFormKey(),Fallout4Release.Fallout4){EditorID=id,Position=new P3Float(x,y,z),Rotation=new P3Float(0,0,yaw),Scale=scale};placed.Base.SetTo(donor.FormKey);cell.Temporary.Add(placed);
   refs.Add(new{id,form=placed.FormKey.ToString(),asset,x,y,z,yaw,scale});
  }
  return new{scope="Passive near-field wreck/woodland/roadside/Mercy furnishing; no interaction/services",refs,native="OPEN: visual density, collision and material appearance"};
 }
}
