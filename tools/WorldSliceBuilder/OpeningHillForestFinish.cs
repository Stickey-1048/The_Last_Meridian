using Mutagen.Bethesda;
using Mutagen.Bethesda.Fallout4;
using Mutagen.Bethesda.Plugins.Records;
using Noggog;
using System.Buffers.Binary;
using System.Text.Json;
public static class OpeningHillForestFinish
{
 static double Smooth(double a,double b,double v){double t=Math.Clamp((v-a)/(b-a),0,1);return t*t*(3-2*t);}
 static double E(double x,double y,double cx,double cy,double rx,double ry)=>1-Smooth(.4,1,Math.Sqrt(Math.Pow((x-cx)/rx,2)+Math.Pow((y-cy)/ry,2)));
 static (double F,double R) Mask(double x,double y)=>(Math.Max(.70*E(x,y,5520,4864,640,512),.55*E(x,y,6320,5180,560,560)),Math.Max(.65*E(x,y,5600,4800,160,224),.60*E(x,y,6000,4850,192,256)));
 public static object Apply(IFallout4ModGetter native,Fallout4Mod mod,Worldspace world)
 {
  var forest=native.LandscapeTextures.Single(t=>t.FormKey.ID==0x3343C&&t.EditorID=="LForestFloor01");
  var rock=native.LandscapeTextures.Single(t=>t.FormKey.ID==0xC55F3&&t.EditorID=="LRootsEroded01Rocks01");
  var cell=world.SubCells.SelectMany(b=>b.Items).SelectMany(b=>b.Items).Single(c=>c.Grid?.Point==new P2Int(1,1));
  if(cell.Landscape?.FormKey.ID!=0xAAA)throw new InvalidDataException("042 exact backdrop LAND changed");
  var land=cell.Landscape;var summaries=new List<object>();
  foreach(var quadrant in new[]{Quadrant.BottomLeft,Quadrant.BottomRight}){
   int q=(int)quadrant;var layers=land.Layers!.OfType<AlphaLayer>().Where(l=>l.Header!.Quadrant==quadrant).ToList();
   if(layers.Count!=(q==0?5:4)||layers.Any(l=>l.Header!.Texture.FormKey==rock.FormKey))throw new InvalidDataException("042 native sparse layer contract changed");
   var f=layers.Single(l=>l.Header!.Texture.FormKey==forest.FormKey);var rows=new Dictionary<AlphaLayer,SortedDictionary<int,byte[]>>(ReferenceEqualityComparer.Instance);
   foreach(var layer in layers){
    var data=layer.AlphaLayerData!.Value.ToArray();if(data.Length%8!=0)throw new InvalidDataException("042 HHf size");
    var map=new SortedDictionary<int,byte[]>();int previous=-1;
    for(int off=0;off<data.Length;off+=8){int i=BinaryPrimitives.ReadUInt16LittleEndian(data.AsSpan(off,2));if(i<=previous||i>288)throw new InvalidDataException("042 native sparse index/order differs");previous=i;map.Add(i,data.AsSpan(off,8).ToArray());}
    rows.Add(layer,map);
   }
   var added=new AlphaLayer{Header=layers[0].Header!.DeepCopy()};added.Header.Texture.SetTo(rock.FormKey);added.Header.LayerNumber=(ushort)(layers.Max(l=>l.Header!.LayerNumber)+1);rows.Add(added,new());
   int changed=0;
   for(int i=0;i<289;i++){
    double x=4096+(q&1)*2048+(i%17)*128,y=4096+(i/17)*128;var(F,R)=Mask(x,y);if(F==0&&R==0)continue;
    double sum=layers.Sum(l=>rows[l].TryGetValue(i,out var b)?(double)BinaryPrimitives.ReadSingleLittleEndian(b.AsSpan(4)):0d);
    if(sum>1.000001||sum<0)throw new InvalidDataException("042 invalid existing explicit alpha sum");
    foreach(var layer in layers.Append(added)){
     bool existed=rows[layer].TryGetValue(i,out var bytes);float old=existed?BinaryPrimitives.ReadSingleLittleEndian(bytes!.AsSpan(4)):0;
     float next=(float)((1-F)*(1-R)*old+(layer==f?sum*F*(1-R):0)+(layer==added?sum*R:0));
     if(next==old)continue;if(next<0||next>1.000001)throw new InvalidDataException("042 invalid alpha value");
     if(!existed){if(next==0)continue;bytes=new byte[8];BinaryPrimitives.WriteUInt16LittleEndian(bytes,(ushort)i);rows[layer].Add(i,bytes);}
     // Preserve every old opaque UInt16 padding word, even nonzero values.
     BinaryPrimitives.WriteSingleLittleEndian(bytes!.AsSpan(4),next);
    }
    changed++;
   }
   foreach(var layer in layers.Append(added)){using var stream=new MemoryStream();foreach(var b in rows[layer].Values)stream.Write(b);layer.AlphaLayerData=stream.ToArray();}
   if(rows[added].Count==0)throw new InvalidDataException("042 expected local rock mask");
   int last=land.Layers.Select((l,i)=>(l,i)).Where(v=>v.l is AlphaLayer a&&a.Header!.Quadrant==quadrant).Max(v=>v.i);land.Layers.Insert(last+1,added);
   summaries.Add(new{quadrant=q,changedVertexSlots=changed,newRockRows=rows[added].Count,newRockLayer=added.Header.LayerNumber});
  }
  string path=Path.Combine(AppContext.BaseDirectory,"../../../../OpeningHillForestFinish/plan.json");byte[] bytesPlan=File.ReadAllBytes(path);
  if(Convert.ToHexString(System.Security.Cryptography.SHA256.HashData(bytesPlan))!="AACF345F57CC0E47313098F6EDF731A8C34F4D1A1929A7D9CE54DA40B9E54A5E")throw new InvalidDataException("042 approved mask/group plan differs");
  using var plan=JsonDocument.Parse(bytesPlan);var refs=world.TopCell!.Persistent.OfType<PlacedObject>().Concat(world.SubCells.SelectMany(b=>b.Items).SelectMany(b=>b.Items).SelectMany(c=>c.Temporary).OfType<PlacedObject>()).ToArray();var moved=new List<object>();
  foreach(var p in plan.RootElement.GetProperty("moves").EnumerateArray()){
   string id=p.GetProperty("id").GetString()!;var r=refs.Single(r=>r.EditorID==id);var old=p.GetProperty("oldPose").EnumerateArray().Select(v=>v.GetSingle()).ToArray();
   uint fid=Convert.ToUInt32(p.GetProperty("form").GetString()![2..],16),bid=Convert.ToUInt32(p.GetProperty("base").GetString()![2..],16);
   if(r.FormKey.ID!=(fid&0xFFFFFF)||r.Base.FormKey.ID!=bid||r.Scale!=p.GetProperty("scale").GetSingle()||r.Position!=new P3Float(old[0],old[1],old[2])||r.Rotation!=new P3Float(old[3],old[4],old[5]))throw new InvalidDataException("042 original passive binding/pose/scale changed");
   var donor=native.Statics.Single(s=>s.FormKey==r.Base.FormKey);if(donor.Model?.File?.ToString()!=p.GetProperty("model").GetString())throw new InvalidDataException("042 exact existing native model differs");
   var v=p.GetProperty("proposedPose").EnumerateArray().Select(v=>v.GetSingle()).ToArray();if(r.Rotation!=new P3Float(v[3],v[4],v[5]))throw new InvalidDataException("042 rotation must stay literal");r.Position=new P3Float(v[0],v[1],v[2]);moved.Add(new{id,oldPose=old,pose=v});
  }
  if(moved.Count!=4)throw new InvalidDataException("042 exact four-passive scope");return new{scope="AAA q0/q1 native sparse paint plus four existing passives only; native art/collision pending",summaries,moved};
 }
}
