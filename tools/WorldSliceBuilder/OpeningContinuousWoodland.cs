using Mutagen.Bethesda.Fallout4;
using Noggog;
using System.Text.Json;

// Fix the observed zero-edge/cubic-collar quarry face. Native terrain is the
// underlying shape; the0.4 envelope is a clearance-transition limit, not a peak.
public static class OpeningContinuousWoodland {
 static readonly Dictionary<(int,int),uint> Donors=new(){[(0,0)]=0xf29b,[(1,0)]=0xf29c,[(0,1)]=0xf2bc,[(1,1)]=0xf2bd};
 static readonly (int,int,int,int)[] Pads={(256,512,1024,1152),(1664,1792,2304,2304),(128,1536,1536,1920),(1024,1408,1280,1664),(2304,2432,3840,3968),(1536,2560,2176,3072),(1280,128,2944,896),(3564,2814,4076,3356)};
 static float[,] Decode(ILandscapeGetter land){var m=land.VertexHeightMap!;var h=new float[33,33];for(int y=0;y<33;y++)for(int x=0;x<33;x++)h[x,y]=(x>0?h[x-1,y]:y>0?h[0,y-1]:m.Offset*8)+unchecked((sbyte)((IReadOnlyArray2d<byte>)m.HeightMap)[x,y])*8;return h;}
 static float External(int x,int y)=>Math.Min(Math.Min(x,y),Math.Min(8192-x,8192-y));
 static bool Protected(int x,int y)=>x<=4096&&y<=4096&&(Pads.Any(p=>x>=p.Item1&&x<=p.Item3&&y>=p.Item2&&y<=p.Item4)||OpeningEnvironment.PathDistance(x,y)<=640);
 public static object Apply(IFallout4ModGetter native,Worldspace world){
  var cells=world.SubCells.SelectMany(b=>b.Items).SelectMany(b=>b.Items).Where(c=>c.Grid!=null&&c.Landscape!=null).ToDictionary(c=>(c.Grid!.Point.X,c.Grid.Point.Y));
  var src=native.Worldspaces.SelectMany(w=>w.SubCells).SelectMany(b=>b.Items).SelectMany(b=>b.Items).Where(c=>c.Landscape!=null&&Donors.Values.Contains(c.Landscape.FormKey.ID)).ToDictionary(c=>c.Landscape!.FormKey.ID,c=>Decode(c.Landscape!));
  if(src.Count!=4)throw new InvalidDataException("Four contiguous native Ranger LANDs required");
  var old=cells.ToDictionary(p=>p.Key,p=>Decode(p.Value.Landscape!));var anchors=new List<(int X,int Y,float H)>();
  for(int y=0;y<33;y++)for(int x=0;x<33;x++)if(Protected(x*128,y*128))anchors.Add((x*128,y*128,old[(0,0)][x,y]));
  var global=new Dictionary<(int,int),float>();
  foreach(var(xy,id)in Donors)for(int y=0;y<33;y++)for(int x=0;x<33;x++){
   int gx=xy.Item1*32+x,gy=xy.Item2*32+y,wx=gx*128,wy=gy*128;float before=old[xy][x,y],h=before;
   if(!Protected(wx,wy)){
    float cap=anchors.Min(a=>a.H+.4f*MathF.Sqrt(MathF.Pow(wx-a.X,2)+MathF.Pow(wy-a.Y,2)));h=MathF.Min(src[id][x,y]-7000,cap);
    // Only the OUTSIDE of the complete2x2 patch keeps the old two-row seam.
    // The former x/y4096 internal zeros have no special treatment.
    float t=Math.Clamp((External(wx,wy)-128)/896,0,1);t=t*t*(3-2*t);h=MathF.Round((before+(h-before)*t)/8)*8;
   }
   if(global.TryGetValue((gx,gy),out var same)&&same!=h)throw new InvalidDataException("Continuous native/shared operative height mismatch");global[(gx,gy)]=h;
  }
  float H(int gx,int gy){if(global.TryGetValue((gx,gy),out var h))return h;var found=old.Where(p=>gx>=p.Key.Item1*32&&gx<=p.Key.Item1*32+32&&gy>=p.Key.Item2*32&&gy<=p.Key.Item2*32+32).Select(p=>p.Value[gx-p.Key.Item1*32,gy-p.Key.Item2*32]).ToArray();if(found.Length==0)throw new InvalidDataException("Derivative neighbor absent");return found[0];}
  int changed=0,nativeExact=0;
  foreach(var(xy,id)in Donors){
   var land=cells[xy].Landscape!;var bytes=new Array2d<byte>(33,33,0);var normals=new Array2d<P3UInt8>(33,33,new P3UInt8(0,0,127));
   for(int y=0;y<33;y++)for(int x=0;x<33;x++){
    int gx=xy.Item1*32+x,gy=xy.Item2*32+y;float h=H(gx,gy);if(h!=old[xy][x,y])changed++;if(h==src[id][x,y]-7000)nativeExact++;
    float before=x>0?H(gx-1,gy):y>0?H(gx,gy-1):0;int delta=(int)((h-before)/8);if(delta< -128||delta>127)throw new InvalidDataException("Continuous VHGT signed delta overflow");bytes[x,y]=unchecked((byte)(sbyte)delta);
    if(External(gx*128,gy*128)<=128){normals[x,y]=((IReadOnlyArray2d<P3UInt8>)land.VertexNormals!)[x,y];continue;}
    float dx=(H(gx+1,gy)-H(gx-1,gy))/256,dy=(H(gx,gy+1)-H(gx,gy-1))/256,len=MathF.Sqrt(dx*dx+dy*dy+1);byte N(float v)=>unchecked((byte)(sbyte)Math.Clamp((int)MathF.Round(v*127/len),-127,127));normals[x,y]=new P3UInt8(N(-dx),N(-dy),N(1));
   }
   land.VertexHeightMap=new LandscapeVertexHeightMap{Offset=0,HeightMap=bytes};land.VertexNormals=normals;
  }
  var dir=new DirectoryInfo(AppContext.BaseDirectory);while(dir!=null&&!File.Exists(Path.Combine(dir.FullName,"tools/OpeningContinuousWoodland/footings.json")))dir=dir.Parent;if(dir==null)throw new InvalidDataException("Explicit continuous woodland footing plan absent");
  using var source=JsonDocument.Parse(File.ReadAllText(Path.Combine(dir.FullName,"tools/OpeningContinuousWoodland/footings.json")));var refs=cells.Values.SelectMany(c=>c.Temporary).OfType<PlacedObject>().ToDictionary(r=>r.FormKey.ID);
  foreach(var p in source.RootElement.GetProperty("poses").EnumerateArray()){
   var r=refs[p.GetProperty("localId").GetUInt32()];var before=p.GetProperty("oldXYZ");if(r.EditorID!=p.GetProperty("id").GetString()||r.Base.FormKey.ID!=p.GetProperty("base").GetUInt32()||r.Position!=new P3Float(before[0].GetSingle(),before[1].GetSingle(),before[2].GetSingle()))throw new InvalidDataException("Explicit affected passive identity/pose differs");var xyz=p.GetProperty("xyz");r.Position=new P3Float(xyz[0].GetSingle(),xyz[1].GetSingle(),xyz[2].GetSingle());
  }
  return new{scope="Observed inner zero-gutter/steep collar repair across coherent four-native-LAND field",protectedVertices=anchors.Count,changedVertices=changed,nativeExactVertices=nativeExact,datum=-7000,operativeRiseRunLimit=.4f,externalCollar=1024,passivePoses=source.RootElement.GetProperty("poses").GetArrayLength(),native="OPEN: visual mountain character and actual collision; no material/quest/actor change"};
 }
}
