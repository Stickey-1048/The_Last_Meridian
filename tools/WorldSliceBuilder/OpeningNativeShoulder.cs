using Mutagen.Bethesda;
using Mutagen.Bethesda.Fallout4;
using Noggog;
using System.Text.Json;
public static class OpeningNativeShoulder
{
 static readonly Dictionary<(int,int),uint> Donors=new(){[(1,0)]=0xF29C,[(1,1)]=0xF2BD};
 static float[,] Decode(ILandscapeGetter land){var m=land.VertexHeightMap!;var h=new float[33,33];for(int y=0;y<33;y++)for(int x=0;x<33;x++)h[x,y]=(x>0?h[x-1,y]:y>0?h[0,y-1]:m.Offset*8)+unchecked((sbyte)((IReadOnlyArray2d<byte>)m.HeightMap)[x,y])*8;return h;}
 static double S(double a,double b,double v){double t=Math.Clamp((v-a)/(b-a),0,1);return t*t*(3-2*t);}
 static double W(double x,double y)=>S(4352,5120,x)*(1-S(6144,7552,x))*S(3072,4352,y)*(1-S(5120,6144,y));
 public static object Apply(IFallout4ModGetter native,Worldspace world)
 {
  byte[] planBytes=File.ReadAllBytes(Path.Combine(AppContext.BaseDirectory,"../../../../OpeningNativeShoulder/plan.json"));
  if(Convert.ToHexString(System.Security.Cryptography.SHA256.HashData(planBytes))!="7395F28FE1B842E772F27564152EED06112893C6ACBCA6195C61B1CE7F484462")throw new InvalidDataException("052 approved field/Z whitelist differs");
  using var plan=JsonDocument.Parse(planBytes);
  var cells=world.SubCells.SelectMany(b=>b.Items).SelectMany(b=>b.Items).Where(c=>c.Grid!=null&&c.Landscape!=null).ToDictionary(c=>(c.Grid!.Point.X,c.Grid.Point.Y));
  if(cells[(1,0)].Landscape!.FormKey.ID!=0xA7E||cells[(1,1)].Landscape!.FormKey.ID!=0xAAA)throw new InvalidDataException("052 exact existing LAND bindings differ");
  var source=native.Worldspaces.SelectMany(w=>w.SubCells).SelectMany(b=>b.Items).SelectMany(b=>b.Items).Where(c=>c.Landscape!=null&&Donors.Values.Contains(c.Landscape.FormKey.ID)).ToDictionary(c=>c.Landscape!.FormKey.ID,c=>Decode(c.Landscape!));
  if(source.Count!=2)throw new InvalidDataException("052 two already-owned contiguous Ranger LANDs required");
  var old=cells.ToDictionary(p=>p.Key,p=>Decode(p.Value.Landscape!));var before=new Dictionary<(int,int),float>();
  foreach(var(g,h)in old)for(int y=0;y<33;y++)for(int x=0;x<33;x++){
   var key=(g.Item1*32+x,g.Item2*32+y);if(!before.TryAdd(key,h[x,y])&&key.Item1>=32&&key.Item1<=64&&key.Item2>=0&&key.Item2<=64&&before[key]!=h[x,y])throw new InvalidDataException("052 current patch/neighbor height seam differs");
  }
  var after=new Dictionary<(int,int),float>(before);var visited=new HashSet<(int,int)>();int slots=0;float maximum=0;
  foreach(var(g,id)in Donors)for(int y=0;y<33;y++)for(int x=0;x<33;x++){
   var key=(g.Item1*32+x,g.Item2*32+y);float b=old[g][x,y];double target=source[id][x,y]-7000+128;float h=(float)(Math.Round((b-W(key.Item1*128,key.Item2*128)*Math.Max(0,b-target))/8)*8);
   if(h>b||b-h>640)throw new InvalidDataException("052 no raising/max640 lowering required");if(!visited.Add(key)&&after[key]!=h)throw new InvalidDataException("052 new internal shared height mismatch");after[key]=h;if(h!=b)slots++;maximum=Math.Max(maximum,b-h);
  }
  if(slots!=413||maximum!=640)throw new InvalidDataException("052 finite quantized field differs");
  float H(int x,int y)=>after.TryGetValue((x,y),out var v)?v:throw new InvalidDataException("052 derivative neighbor absent");
  bool Changed(int x,int y)=>after[(x,y)]!=before[(x,y)];int normalVerticesRecomputed=0;
  foreach(var(g,_)in Donors){
   var land=cells[g].Landscape!;var oldNormals=land.VertexNormals!;var vhgt=new Array2d<byte>(33,33,0);var normals=new Array2d<P3UInt8>(33,33,new P3UInt8(0,0,127));
   for(int y=0;y<33;y++)for(int x=0;x<33;x++){
    int gx=g.Item1*32+x,gy=g.Item2*32+y;float previous=x>0?H(gx-1,gy):y>0?H(gx,gy-1):0;int d=(int)((H(gx,gy)-previous)/8);if(d< -128||d>127)throw new InvalidDataException("052 signed VHGT overflow");vhgt[x,y]=unchecked((byte)(sbyte)d);
    bool edge=x<=1||x>=31||(g==(1,0)&&y<=1)||(g==(1,1)&&y>=31);
    bool near=!edge&&(Changed(gx,gy)||Changed(gx-1,gy)||Changed(gx+1,gy)||Changed(gx,gy-1)||Changed(gx,gy+1));
    if(!near){normals[x,y]=((IReadOnlyArray2d<P3UInt8>)oldNormals)[x,y];continue;}
    double dx=(H(gx+1,gy)-H(gx-1,gy))/256d,dy=(H(gx,gy+1)-H(gx,gy-1))/256d,len=Math.Sqrt(1+dx*dx+dy*dy);byte N(double v)=>unchecked((byte)(sbyte)Math.Clamp((int)Math.Round(127*v/len),-127,127));normals[x,y]=new P3UInt8(N(-dx),N(-dy),N(1));normalVerticesRecomputed++;
   }
   land.VertexHeightMap=new LandscapeVertexHeightMap{Offset=0,HeightMap=vhgt};land.VertexNormals=normals;
  }
  var refs=cells.Values.SelectMany(c=>c.Temporary).OfType<PlacedObject>().ToDictionary(r=>r.FormKey.ID);var poses=new List<object>();
  foreach(var p in plan.RootElement.GetProperty("moves").EnumerateArray()){
   uint fid=Convert.ToUInt32(p.GetProperty("form").GetString()![2..],16)&0xFFFFFF;var r=refs[fid];var b=p.GetProperty("oldPose").EnumerateArray().Select(v=>v.GetSingle()).ToArray();var a=p.GetProperty("proposedPose").EnumerateArray().Select(v=>v.GetSingle()).ToArray();
   if(r.EditorID!=p.GetProperty("id").GetString()||r.Base.FormKey.ID!=p.GetProperty("base").GetUInt32()||r.Scale!=p.GetProperty("scale").GetSingle()||r.MajorRecordFlagsRaw!=p.GetProperty("flags").GetUInt32()||r.Position!=new P3Float(b[0],b[1],b[2])||r.Rotation!=new P3Float(b[3],b[4],b[5]))throw new InvalidDataException("052 exact current passive binding/pose/scale differs");
   if(a[0]!=b[0]||a[1]!=b[1]||a[3]!=b[3]||a[4]!=b[4]||a[5]!=b[5])throw new InvalidDataException("052 only Z refoot permitted");if(native.Statics.Single(s=>s.FormKey==r.Base.FormKey).Model?.File?.ToString()!=p.GetProperty("model").GetString())throw new InvalidDataException("052 existing native model differs");r.Position=new P3Float(b[0],b[1],a[2]);poses.Add(new{id=r.EditorID,oldZ=b[2],newZ=a[2]});
  }
  if(poses.Count!=14)throw new InvalidDataException("052 exact fourteen Z whitelist required");
  return new{scope="Lower native front shoulder/retain rear east ridge: A7E+AAA VHGT/VNML and14Zonly; materials/current050UI/voices/core literal",changedVertexSlots=slots,maximumLowering=maximum,normalVerticesRecomputed,poses,native="Appearance/Havok/LOD/access unproved; internalY4096 coherently changed, external patch borders fixed"};
 }
}
