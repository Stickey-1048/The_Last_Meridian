using Mutagen.Bethesda;
using Mutagen.Bethesda.Fallout4;
using Noggog;
using Mutagen.Bethesda.Plugins;
using System.Text.Json;

// Native authored terrain is read from the owned master at build time. No native
// height arrays, sparse paint payloads, references or navigation are source assets.
public static class OpeningAuthoredWoodland {
 const int Datum=-7000, Collar=1024;
 static readonly Dictionary<(int,int),uint> Donors=new(){[(1,0)]=0xf29c,[(0,1)]=0xf2bc,[(1,1)]=0xf2bd};
 static float[,] Decode(ILandscapeGetter land){
  var map=land.VertexHeightMap??throw new InvalidDataException("Owned LAND has no VHGT");var h=new float[33,33];
  for(int y=0;y<33;y++)for(int x=0;x<33;x++)h[x,y]=(x>0?h[x-1,y]:y>0?h[0,y-1]:map.Offset*8)+unchecked((sbyte)((IReadOnlyArray2d<byte>)map.HeightMap)[x,y])*8;
  return h;
 }
 static float Segment(float x,float y,int ax,int ay,int bx,int by){float dx=bx-ax,dy=by-ay,t=Math.Clamp(((x-ax)*dx+(y-ay)*dy)/(dx*dx+dy*dy),0,1);return MathF.Sqrt(MathF.Pow(x-ax-t*dx,2)+MathF.Pow(y-ay-t*dy,2));}
 static float Distance(float x,float y){var p=new(int,int)[]{(4096,0),(8192,0),(8192,8192),(0,8192),(0,4096),(4096,4096)};return Enumerable.Range(0,p.Length).Min(i=>Segment(x,y,p[i].Item1,p[i].Item2,p[(i+1)%p.Length].Item1,p[(i+1)%p.Length].Item2));}
 public static object Apply(IFallout4ModGetter native,Fallout4Mod mod,Worldspace world){
  var cells=world.SubCells.SelectMany(b=>b.Items).SelectMany(b=>b.Items).Where(c=>c.Grid!=null).ToDictionary(c=>(c.Grid!.Point.X,c.Grid.Point.Y));
  var nativeLands=native.Worldspaces.SelectMany(w=>w.SubCells).SelectMany(b=>b.Items).SelectMany(b=>b.Items).Where(c=>c.Landscape!=null&&Donors.Values.Contains(c.Landscape.FormKey.ID)).ToDictionary(c=>c.Landscape!.FormKey.ID,c=>c.Landscape!);
  if(nativeLands.Count!=3)throw new InvalidDataException("Exact three Ranger LAND donors absent");
  var heights=cells.Where(p=>p.Value.Landscape!=null).ToDictionary(p=>p.Key,p=>Decode(p.Value.Landscape!));
  foreach(var (xy,id) in Donors){
   var src=Decode(nativeLands[id]);var dst=heights[xy];
   for(int y=0;y<33;y++)for(int x=0;x<33;x++){
    float d=Distance(xy.Item1*4096+x*128,xy.Item2*4096+y*128),t=Math.Clamp((d-128)/(Collar-128),0,1);t=t*t*(3-2*t);
    dst[x,y]=MathF.Round((dst[x,y]*(1-t)+(src[x,y]+Datum)*t)/8)*8;
   }
  }
  float Height(int gx,int gy){var matches=heights.Where(p=>gx>=p.Key.Item1*32&&gx<=p.Key.Item1*32+32&&gy>=p.Key.Item2*32&&gy<=p.Key.Item2*32+32).Select(p=>p.Value[gx-p.Key.Item1*32,gy-p.Key.Item2*32]).ToArray();if(matches.Length==0)throw new InvalidDataException("Derivative neighbor absent");if(matches.Max()-matches.Min()>.01f)throw new InvalidDataException("Authored transformed height seam");return matches[0];}
  foreach(var (xy,id) in Donors){
   var dst=cells[xy].Landscape!;var src=nativeLands[id];var h=heights[xy];var bytes=new Array2d<byte>(33,33,0);var normals=new Array2d<P3UInt8>(33,33,new P3UInt8(0,0,127));
   for(int y=0;y<33;y++)for(int x=0;x<33;x++){
    int delta=(int)((h[x,y]-(x>0?h[x-1,y]:y>0?h[0,y-1]:0))/8);if(delta< -128||delta>127)throw new InvalidDataException("Authored signed VHGT overflow");bytes[x,y]=unchecked((byte)(sbyte)delta);
    int gx=xy.Item1*32+x,gy=xy.Item2*32+y;
    if(Distance(gx*128,gy*128)<=128){normals[x,y]=((IReadOnlyArray2d<P3UInt8>)dst.VertexNormals!)[x,y];continue;}
    float dx=(Height(gx+1,gy)-Height(gx-1,gy))/256,dy=(Height(gx,gy+1)-Height(gx,gy-1))/256,n=MathF.Sqrt(dx*dx+dy*dy+1);
    byte N(float v)=>unchecked((byte)(sbyte)Math.Clamp((int)MathF.Round(v*127/n),-127,127));normals[x,y]=new P3UInt8(N(-dx),N(-dy),N(1));
   }
   dst.VertexHeightMap=new LandscapeVertexHeightMap{Offset=0,HeightMap=bytes};dst.VertexNormals=normals;
   // Preserve sparse native layer ordering, header/null links and opaque unused
   // VTXT bytes. Missing BTXT stays missing: no invented replacement base.
   dst.Layers!.Clear();foreach(var layer in src.Layers!)dst.Layers.Add(layer.DeepCopy());
   if(src.Textures==null)dst.Textures=null;else{dst.Textures!.Clear();foreach(var texture in src.Textures)dst.Textures.Add(texture);}
  }
  var dir=new DirectoryInfo(AppContext.BaseDirectory);while(dir!=null&&!File.Exists(Path.Combine(dir.FullName,"tools/OpeningAuthoredWoodland/placements.json")))dir=dir.Parent;if(dir==null)throw new InvalidDataException("Authored placement plan absent");
  using var document=JsonDocument.Parse(File.ReadAllText(Path.Combine(dir.FullName,"tools/OpeningAuthoredWoodland/placements.json")));var plan=document.RootElement;
  var refs=cells.Values.SelectMany(c=>c.Temporary).OfType<PlacedObject>().ToDictionary(r=>r.FormKey.ID);
  foreach(var p in plan.GetProperty("poses").EnumerateArray()){
   var r=refs[p.GetProperty("localId").GetUInt32()];var old=p.GetProperty("oldXYZ");if(r.EditorID!=p.GetProperty("id").GetString()||r.Base.FormKey.ID!=p.GetProperty("base").GetUInt32()||r.Position!=new P3Float(old[0].GetSingle(),old[1].GetSingle(),old[2].GetSingle()))throw new InvalidDataException("Explicit passive/furniture pose source changed");
   var xyz=p.GetProperty("xyz");r.Position=new P3Float(xyz[0].GetSingle(),xyz[1].GetSingle(),xyz[2].GetSingle());
  }
  foreach(var p in plan.GetProperty("disabled").EnumerateArray()){
   var r=refs[p.GetProperty("localId").GetUInt32()];if(r.EditorID!=p.GetProperty("id").GetString()||r.Base.FormKey.ID!=p.GetProperty("base").GetUInt32())throw new InvalidDataException("Original cabin-panel source changed");r.MajorRecordFlagsRaw|=0x800;
  }
  var cp=plan.GetProperty("cabin");var donor=native.Statics.Single(t=>t.FormKey.ID==cp.GetProperty("base").GetUInt32()&&t.EditorID=="Cabin01NoFence");if(donor.Model?.File?.ToString()!=cp.GetProperty("model").GetString())throw new InvalidDataException("Exact cabin donor model differs");var pos=cp.GetProperty("xyz");
  var cabin=new PlacedObject(mod.GetNextFormKey(),Fallout4Release.Fallout4){EditorID=cp.GetProperty("id").GetString(),Position=new P3Float(pos[0].GetSingle(),pos[1].GetSingle(),pos[2].GetSingle()),Rotation=new P3Float(0,0,cp.GetProperty("yaw").GetSingle()),Scale=1};cabin.Base.SetTo(donor.FormKey);cells[(0,0)].Temporary.Add(cabin);
  return new{scope="Three owned Ranger woodland interiors and measured native gabled cabin",datum=Datum,collar=Collar,donors=Donors.Select(p=>new{grid=new[]{p.Key.Item1,p.Key.Item2},land=p.Value}),paint="Native sparse layers copied without fabricated base/weights; native visibility remains open",poses=plan.GetProperty("poses").GetArrayLength(),disabledPanels=plan.GetProperty("disabled").GetArrayLength(),cabin=cabin.FormKey.ToString()};
 }
}
