using Mutagen.Bethesda;
using Mutagen.Bethesda.Plugins.Records;
using Mutagen.Bethesda.Fallout4;
using Noggog;
using System.Text.Json;
using System.Security.Cryptography;
using System.Buffers.Binary;
public static class OpeningRidgeSpillFinish
{
 static float Smooth(float a,float b,float x){float t=Math.Clamp((x-a)/(b-a),0,1);return t*t*(3-2*t);}
 static double DS(double a,double b,double x){double t=Math.Clamp((x-a)/(b-a),0,1);return t*t*(3-2*t);}
 static double Lift(double x,double y)=>768*DS(4352,5888,x)*(1-DS(6784,7936,x))*DS(2560,4608,y)*(1-DS(6144,7936,y));
 static float[,] Decode(ILandscapeGetter l){var m=l.VertexHeightMap!;var h=new float[33,33];for(int y=0;y<33;y++)for(int x=0;x<33;x++)h[x,y]=(x>0?h[x-1,y]:y>0?h[0,y-1]:m.Offset*8)+unchecked((sbyte)((IReadOnlyArray2d<byte>)m.HeightMap)[x,y])*8;return h;}
 static float RoadDistance(float x,float y){var p=new(float,float)[]{(448,640),(700,900),(1050,1133),(1900,1700),(2600,2200),(3048,2200),(3048,2432)};float best=float.MaxValue;for(int i=0;i<p.Length-1;i++){var a=p[i];var b=p[i+1];float dx=b.Item1-a.Item1,dy=b.Item2-a.Item2,t=Math.Clamp(((x-a.Item1)*dx+(y-a.Item2)*dy)/(dx*dx+dy*dy),0,1);best=Math.Min(best,MathF.Sqrt(MathF.Pow(x-a.Item1-t*dx,2)+MathF.Pow(y-a.Item2-t*dy,2)));}return best;}
 public static object Apply(Fallout4Mod mod,Worldspace world)
 {
  byte[] planBytes=File.ReadAllBytes(Path.Combine(AppContext.BaseDirectory,"../../../../OpeningRidgeSpillFinish/plan.json"));
  if(Convert.ToHexString(SHA256.HashData(planBytes))!="58E80489F8D28C25CD524581F50BB3533CF01F5E313584EDA983A69E817562FF")throw new InvalidDataException("Approved finite visual033 pose plan differs");
  using var plan=JsonDocument.Parse(planBytes);
  var cells=world.SubCells.SelectMany(b=>b.Items).SelectMany(b=>b.Items).Where(c=>c.Grid!=null&&c.Landscape!=null).ToDictionary(c=>(c.Grid!.Point.X,c.Grid.Point.Y));
  var old=cells.ToDictionary(k=>k.Key,k=>Decode(k.Value.Landscape!));var heights=new Dictionary<(int,int),float>();
  foreach(var(g,h)in old)for(int y=0;y<33;y++)for(int x=0;x<33;x++){
   int gx=g.Item1*32+x,gy=g.Item2*32+y;float v=h[x,y];if(g is(1,0)or(1,1))v+=(float)(Math.Round(Lift(gx*128,gy*128)/8)*8);
   if(heights.TryGetValue((gx,gy),out var other)&&other!=v)throw new InvalidDataException("033 shared height mismatch");heights[(gx,gy)]=v;
  }
  float H(int x,int y)=>heights.TryGetValue((x,y),out var v)?v:throw new InvalidDataException("Missing derivative neighbor");
  int changed=0;foreach(var g in new[]{(1,0),(1,1)}){
   var land=cells[g].Landscape!;var beforeNormals=land.VertexNormals!;var bytes=new Array2d<byte>(33,33,0);var normals=new Array2d<P3UInt8>(33,33,new P3UInt8(0,0,127));
   for(int y=0;y<33;y++)for(int x=0;x<33;x++){
    int gx=g.Item1*32+x,gy=g.Item2*32+y;float h=H(gx,gy),before=x>0?H(gx-1,gy):y>0?H(gx,gy-1):0;int delta=(int)((h-before)/8);if(delta< -128||delta>127)throw new InvalidDataException("033 VHGT signed overflow");bytes[x,y]=unchecked((byte)(sbyte)delta);if(h!=old[g][x,y])changed++;
    if(gx<=33||gx>=63||gy<=1||gy>=63){normals[x,y]=((IReadOnlyArray2d<P3UInt8>)beforeNormals)[x,y];continue;}
    float dx=(H(gx+1,gy)-H(gx-1,gy))/256,dy=(H(gx,gy+1)-H(gx,gy-1))/256,len=MathF.Sqrt(dx*dx+dy*dy+1);byte N(float a)=>unchecked((byte)(sbyte)Math.Clamp((int)MathF.Round(a*127/len),-127,127));normals[x,y]=new P3UInt8(N(-dx),N(-dy),N(1));
   }
   land.VertexHeightMap=new LandscapeVertexHeightMap{Offset=0,HeightMap=bytes};land.VertexNormals=normals;
  }
  var refs=cells.Values.SelectMany(c=>c.Temporary).Concat(world.TopCell!.Persistent).OfType<PlacedObject>().ToDictionary(r=>r.FormKey.ID);
  int feet=0,cargo=0,posts=0;
  void Move(JsonElement row,bool verticalOnly){uint id=row.GetProperty("localId").GetUInt32();var r=refs[id];var oldPose=row.GetProperty("oldPose");
   if(r.EditorID!=row.GetProperty("id").GetString()||r.Base.FormKey.ID!=row.GetProperty("base").GetUInt32()||r.Position!=new P3Float(oldPose[0].GetSingle(),oldPose[1].GetSingle(),oldPose[2].GetSingle())||r.Rotation!=new P3Float(oldPose[3].GetSingle(),oldPose[4].GetSingle(),oldPose[5].GetSingle()))throw new InvalidDataException("033 exact passive identity/oldpose differs");
   var p=row.GetProperty("pose");if(verticalOnly&&(p[0].GetSingle()!=r.Position.X||p[1].GetSingle()!=r.Position.Y))throw new InvalidDataException("033 refoot must preserve XY");r.Position=new P3Float(p[0].GetSingle(),p[1].GetSingle(),p[2].GetSingle());r.Rotation=new P3Float(p[3].GetSingle(),p[4].GetSingle(),p[5].GetSingle());
  }
  foreach(var row in plan.RootElement.GetProperty("footings").EnumerateArray()){Move(row,true);feet++;}
  foreach(var row in plan.RootElement.GetProperty("cargo").EnumerateArray()){Move(row,false);cargo++;}
  foreach(var id in plan.RootElement.GetProperty("posts").EnumerateArray()){
   var r=refs[id.GetUInt32()];if(r.Base.FormKey.ID!=0x117D36||r.MajorRecordFlagsRaw!=0)throw new InvalidDataException("033 decorative-only post guard differs");r.MajorRecordFlagsRaw|=0x800;posts++;
  }
  if(feet!=30||cargo!=3||posts!=4)throw new InvalidDataException("033 exact passive count differs");
  // Paint only current three full native HHf alpha layers, never guessed MPCD or a grass setting.
  var core=cells[(0,0)].Landscape!;var leaf=mod.LandscapeTextures.Single(t=>t.EditorID=="TLM_LTEX_OpeningLowLeafFloor");int painted=0;
  foreach(var quadrant in Enum.GetValues<Quadrant>()){
   var layers=core.Layers!.OfType<AlphaLayer>().Where(a=>a.Header!.Quadrant==quadrant).ToArray();if(layers.Length!=3)throw new InvalidDataException("033 expected three verified paint layers");
   var forest=layers.Single(a=>a.Header!.Texture.FormKey==leaf.FormKey);var gravel=layers.Single(a=>a.Header!.Texture.FormKey.ID==0x21336);var f=forest.AlphaLayerData!.Value.ToArray();var v=gravel.AlphaLayerData!.Value.ToArray();if(f.Length!=289*8||v.Length!=f.Length)throw new InvalidDataException("033 requires full verified HHf source masks");
   int q=(int)quadrant;for(int i=0;i<289;i++){
    if(BinaryPrimitives.ReadUInt16LittleEndian(f.AsSpan(i*8,2))!=i||BinaryPrimitives.ReadUInt16LittleEndian(v.AsSpan(i*8,2))!=i)throw new InvalidDataException("033 paint index differs");
    int x=i%17+(q&1)*16,y=i/17+(q>>1)*16;if(x is 0 or 32||y is 0 or 32)continue;
    float a=BinaryPrimitives.ReadSingleLittleEndian(f.AsSpan(i*8+4,4)),b=BinaryPrimitives.ReadSingleLittleEndian(v.AsSpan(i*8+4,4)),factor=Smooth(96,160,RoadDistance(x*128,y*128)),after=a*factor;
    BinaryPrimitives.WriteSingleLittleEndian(f.AsSpan(i*8+4,4),after);BinaryPrimitives.WriteSingleLittleEndian(v.AsSpan(i*8+4,4),b+(a-after)*.55f);if(after!=a)painted++;
   }
   forest.AlphaLayerData=f;gravel.AlphaLayerData=v;
  }
  return new{scope="Approved visual033 only; all editorials/operatives/coreheights retained; nativeappearanceOPEN",changedTerrainVertices=changed,backdropCells=2,passiveFeet=feet,cargo,posts,painted,maximumLift=768,outerDerivativeGuard=128,noNewForms=true};
 }
}
