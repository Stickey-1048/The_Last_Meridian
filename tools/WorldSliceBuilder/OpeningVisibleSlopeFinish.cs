using Mutagen.Bethesda;
using Mutagen.Bethesda.Fallout4;
using Mutagen.Bethesda.Plugins.Records;
using Noggog;
using System.Buffers.Binary;
using System.Text.Json;
public static class OpeningVisibleSlopeFinish
{
 static double E(double x,double y,double cx,double cy,double rx,double ry){double v=Math.Sqrt(Math.Pow((x-cx)/rx,2)+Math.Pow((y-cy)/ry,2)),t=Math.Clamp((v-.4)/.6,0,1);return 1-t*t*(3-2*t);}
 public static object Apply(IFallout4ModGetter native,Worldspace world)
 {
  byte[] planBytes=File.ReadAllBytes(Path.Combine(AppContext.BaseDirectory,"../../../../OpeningVisibleSlopeFinish/plan.json"));
  if(Convert.ToHexString(System.Security.Cryptography.SHA256.HashData(planBytes))!="5B35730D4B59196600BEE15DC5FA1ABF5764EDFF9B73BBDE91DE05AE30233113")throw new InvalidDataException("Approved047 exact mask/pose contract changed");
  using var plan=JsonDocument.Parse(planBytes);
  var cell=world.SubCells.SelectMany(b=>b.Items).SelectMany(b=>b.Items).Single(c=>c.Grid?.Point==new P2Int(1,1));
  if(cell.Landscape?.FormKey.ID!=0xAAA)throw new InvalidDataException("047 exact LAND differs");
  var layers=cell.Landscape.Layers!.OfType<AlphaLayer>().Where(l=>(int)l.Header!.Quadrant==0).ToArray();
  if(layers.Length!=6)throw new InvalidDataException("047 inherited042 six native sparse layers required");
  var forest=layers.Single(l=>l.Header!.Texture.FormKey.ID==0x3343C);var rock=layers.Single(l=>l.Header!.Texture.FormKey.ID==0xC55F3);
  if(native.LandscapeTextures.Single(t=>t.FormKey==forest.Header!.Texture.FormKey).EditorID!="LForestFloor01"||native.LandscapeTextures.Single(t=>t.FormKey==rock.Header!.Texture.FormKey).EditorID!="LRootsEroded01Rocks01")throw new InvalidDataException("047 existing native texture identity differs");
  var rows=new Dictionary<AlphaLayer,SortedDictionary<int,byte[]>>(ReferenceEqualityComparer.Instance);
  foreach(var layer in layers){
   var b=layer.AlphaLayerData!.Value.ToArray();if(b.Length%8!=0)throw new InvalidDataException("047 HHf size");var map=new SortedDictionary<int,byte[]>();int previous=-1;
   for(int off=0;off<b.Length;off+=8){int i=BinaryPrimitives.ReadUInt16LittleEndian(b.AsSpan(off,2));if(i<=previous||i>288)throw new InvalidDataException("047 sparse native index/order differs");map.Add(i,b.AsSpan(off,8).ToArray());previous=i;}rows.Add(layer,map);
  }
  int slots=0,zeroCoverage=0;double maxIncrease=0;
  for(int i=0;i<289;i++){
   double x=4096+(i%17)*128,y=4096+(i/17)*128,C=.85*Math.Max(E(x,y,4970,5260,480,608),.8*E(x,y,5290,4880,448,448)),R=Math.Min(C,.55*E(x,y,5140,5420,224,240));if(C==0)continue;
   double oldSum=layers.Sum(l=>rows[l].TryGetValue(i,out var b)?(double)BinaryPrimitives.ReadSingleLittleEndian(b.AsSpan(4)):0d);if(oldSum<0||oldSum>1.000001)throw new InvalidDataException("047 old explicit sum invalid");if(oldSum==0)zeroCoverage++;
   foreach(var layer in layers){
    bool existed=rows[layer].TryGetValue(i,out var b);float old=existed?BinaryPrimitives.ReadSingleLittleEndian(b!.AsSpan(4)):0,next=(float)((1-C)*old+(ReferenceEquals(layer,forest)?C-R:0)+(ReferenceEquals(layer,rock)?R:0));
    if(next==old)continue;if(next<0||next>1.000001)throw new InvalidDataException("047 alpha outside range");
    if(!existed){if(next==0)continue;b=new byte[8];BinaryPrimitives.WriteUInt16LittleEndian(b,(ushort)i);rows[layer].Add(i,b);}BinaryPrimitives.WriteSingleLittleEndian(b!.AsSpan(4),next);
   }
   double sum=layers.Sum(l=>rows[l].TryGetValue(i,out var b)?(double)BinaryPrimitives.ReadSingleLittleEndian(b.AsSpan(4)):0d);
   if(Math.Abs(sum-(oldSum+(1-oldSum)*C))>1e-6||sum>1.000001)throw new InvalidDataException("047 explicit coverage transfer differs");maxIncrease=Math.Max(maxIncrease,sum-oldSum);slots++;
  }
  foreach(var layer in layers){using var stream=new MemoryStream();foreach(var row in rows[layer].Values)stream.Write(row);layer.AlphaLayerData=stream.ToArray();}
  var refs=cell.Temporary.OfType<PlacedObject>().ToArray();var moves=new List<object>();
  foreach(var p in plan.RootElement.GetProperty("moves").EnumerateArray()){
   var r=refs.Single(r=>r.EditorID==p.GetProperty("id").GetString());uint id=Convert.ToUInt32(p.GetProperty("form").GetString()![2..],16),bid=Convert.ToUInt32(p.GetProperty("base").GetString()![2..],16);var old=p.GetProperty("oldPose").EnumerateArray().Select(v=>v.GetSingle()).ToArray();
   if(r.FormKey.ID!=(id&0xFFFFFF)||r.Base.FormKey.ID!=bid||r.Scale!=p.GetProperty("scale").GetSingle()||r.Position!=new P3Float(old[0],old[1],old[2])||r.Rotation!=new P3Float(old[3],old[4],old[5]))throw new InvalidDataException("047 exact old passive binding/pose/scale differs");
   if(native.Statics.Single(s=>s.FormKey==r.Base.FormKey).Model?.File?.ToString()!=p.GetProperty("model").GetString())throw new InvalidDataException("047 known stock model differs");
   var v=p.GetProperty("proposedPose").EnumerateArray().Select(v=>v.GetSingle()).ToArray();r.Position=new P3Float(v[0],v[1],v[2]);r.Rotation=new P3Float(v[3],v[4],v[5]);moves.Add(new{id=r.EditorID,oldPose=old,pose=v});
  }
  if(moves.Count!=4||slots!=76||zeroCoverage!=10)throw new InvalidDataException("047 exact finite scope differs");return new{scope="AAA q0 existing VTXT coverage fill and four existing passive poses only; native appearance pending",slots,zeroCoverage,maxIncrease,moves};
 }
}
