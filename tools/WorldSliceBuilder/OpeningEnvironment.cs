using Mutagen.Bethesda.Fallout4;
using Mutagen.Bethesda.Plugins;
using Noggog;
using System.Text.Json;

// Original opening terrain. Own refs retain IDs/XY/links; heights are physical LAND.
public static class OpeningEnvironment {
 static readonly (float X,float Y,float Z)[] Road={(448,640,-192),(700,900,-192),(1050,1133,-192),(1900,1700,-64),(2600,2200,64),(3048,2200,128),(3048,2432,128)};
 static readonly (float X0,float Y0,float X1,float Y1,float Z)[] Pads={
  (256,512,1024,1152,-192), // entire wreck/evidence and arrival hollow
  (1664,1792,2304,2304,-16),
  (128,1536,1536,1920,-128), // full original derailed boxcar footprint
  (1024,1408,1280,1664,-128), // detached bogie support apron // encounter standing ground
  (2304,2432,3840,3968,128), // entire Mercy yard/cabin/supply footprints
  (1536,2560,2176,3072,128), // entire freight shelter/floor footprint
  (1280,128,2944,896,0) // existing southern Greenwater operative ground
 };
 static readonly (float X,float Y,float Z)[] Bypass={(1200,1200,-168),(2200,1000,0),(2700,1700,16),(2600,2200,64)};
 static float Clamp(float x)=>Math.Clamp(x,0,1);
 static float Smooth(float x){x=Clamp(x);return x*x*(3-2*x);}
 public static int Vertex(int ix,int iy){
  if(ix==0||ix==32||iy==0||iy==32)return 0; // C0 boundary to default exterior height0
  float x=ix*128,y=iy*128,best=float.MaxValue,z=-192;
  for(int i=0;i<Road.Length-1;i++){
   var a=Road[i];var b=Road[i+1];float dx=b.X-a.X,dy=b.Y-a.Y,t=Clamp(((x-a.X)*dx+(y-a.Y)*dy)/(dx*dx+dy*dy));float d=MathF.Sqrt(MathF.Pow(x-a.X-t*dx,2)+MathF.Pow(y-a.Y-t*dy,2));
   if(d<best){best=d;z=a.Z+(b.Z-a.Z)*t;}
  }
  z+=MathF.Min(640,MathF.Max(0,best-320)*(x<1800?.18f:.42f));
  // Raised tree-covered cell rim breaks the former flat horizon.
  float west=320*MathF.Max(0,1-MathF.Abs(x-384)/640)*(.75f+.25f*MathF.Sin(y/430));float east=576*MathF.Max(0,1-MathF.Abs(x-3712)/512)*(.78f+.22f*MathF.Sin(y/370));z=MathF.Max(z,MathF.Max(west,east));
  // Blended broad pads, not independent tile pivots. Every listed footprint
  // is flat across its full area, with a384-unit transition outside it.
  float? exactPad=null;foreach(var p in Pads)if(x>=p.X0&&x<=p.X1&&y>=p.Y0&&y<=p.Y1){exactPad=p.Z;break;}
  foreach(var p in Pads){float dx=MathF.Max(MathF.Max(p.X0-x,x-p.X1),0),dy=MathF.Max(MathF.Max(p.Y0-y,y-p.Y1),0),d=MathF.Sqrt(dx*dx+dy*dy);if(d<384)z=z+(p.Z-z)*(1-Smooth(d/384));}
  if(exactPad is {} flat)z=flat;
  // Wide traversable shoulders are authored from route projection, independent
  // of off-route ridge height. Both main and peaceful bypass remain walkable.
  float near=best,roadZ=RoadHeight(Road,x,y).Z;var by=RoadHeight(Bypass,x,y);if(by.D<near){near=by.D;roadZ=by.Z;}
  if(near<=384)z=roadZ;else if(near<640)z=roadZ+(z-roadZ)*Smooth((near-384)/256);
  // Complete foundation footprints override only after the gentle approach;
  // endpoint128 and cabin128 are the same physical bench.
  foreach(var p in Pads.Where(p=>p.Z==128||p.Z==-128))if(x>=p.X0&&x<=p.X1&&y>=p.Y0&&y<=p.Y1)z=p.Z;
  return (int)MathF.Round(z/8)*8;
 }
 public static float PathDistance(float x,float y)=>MathF.Min(MathF.Min(RoadHeight(Road,x,y).D,RoadHeight(Bypass,x,y).D),Expansion.Routes.Min(r=>RoadHeight(r.Points.Select(p=>(p.X,p.Y,0f)).ToArray(),x,y).D));
 static (float D,float Z) RoadHeight((float X,float Y,float Z)[] route,float x,float y){float best=float.MaxValue,z=0;for(int i=0;i<route.Length-1;i++){var a=route[i];var b=route[i+1];float dx=b.X-a.X,dy=b.Y-a.Y,t=Clamp(((x-a.X)*dx+(y-a.Y)*dy)/(dx*dx+dy*dy)),d=MathF.Sqrt(MathF.Pow(x-a.X-t*dx,2)+MathF.Pow(y-a.Y-t*dy,2));if(d<best){best=d;z=a.Z+(b.Z-a.Z)*t;}}return(best,z);}
 public static float Ground(float x,float y,bool upper=true){
  int ix=Math.Clamp((int)MathF.Floor(x/128),0,31),iy=Math.Clamp((int)MathF.Floor(y/128),0,31);float u=Clamp((x-ix*128)/128),v=Clamp((y-iy*128)/128);
  float a=Vertex(ix,iy),b=Vertex(ix+1,iy),c=Vertex(ix,iy+1),d=Vertex(ix+1,iy+1);
  float first=v<=u?a+(b-a)*u+(d-b)*v:a+(d-c)*u+(c-a)*v;
  float second=u+v<=1?a+(b-a)*u+(c-a)*v:d+(c-d)*(1-u)+(b-d)*(1-v);
  return upper?MathF.Max(first,second):MathF.Min(first,second); // bound both native diagonal choices
 }
 public static object Apply(IFallout4ModGetter native,Fallout4Mod mod,Worldspace world,Cell cell,Landscape land){
  var bytes=new Array2d<byte>(33,33,0);var normals=new Array2d<P3UInt8>(33,33,new P3UInt8(0,0,127));
  for(int y=0;y<33;y++)for(int x=0;x<33;x++){
   int before=x>0?Vertex(x-1,y):y>0?Vertex(0,y-1):0;int delta=(Vertex(x,y)-before)/8;if(delta< -128||delta>127)throw new InvalidDataException("Opening VHGT overflow");bytes[x,y]=unchecked((byte)(sbyte)delta);
   float dx=(Vertex(Math.Min(32,x+1),y)-Vertex(Math.Max(0,x-1),y))/(x is 0 or 32?128f:256f),dy=(Vertex(x,Math.Min(32,y+1))-Vertex(x,Math.Max(0,y-1)))/(y is 0 or 32?128f:256f),len=MathF.Sqrt(1+dx*dx+dy*dy);
   byte N(float v)=>unchecked((byte)(sbyte)Math.Clamp((int)MathF.Round(v/len*127),-127,127));normals[x,y]=new P3UInt8(N(-dx),N(-dy),N(1));
  }
  land.VertexHeightMap=new LandscapeVertexHeightMap{Offset=0,HeightMap=bytes};land.VertexNormals=normals;var materials=OpeningMaterials.Apply(native,world,land);
  var moved=new List<object>();var fresh=new List<object>();var hidden=new List<string>();
  var directory=new DirectoryInfo(AppContext.BaseDirectory);while(directory!=null&&!File.Exists(Path.Combine(directory.FullName,"tools/OpeningEnvironment/donors.json")))directory=directory.Parent;
  if(directory==null)throw new InvalidDataException("Opening donor metadata absent");
  using var meta=JsonDocument.Parse(File.ReadAllText(Path.Combine(directory.FullName,"tools/OpeningEnvironment/donors.json")));var assets=meta.RootElement.GetProperty("assets");
  var nativeBounds=native.Statics.Select(a=>(a.FormKey,a.ObjectBounds)).Concat(native.Furniture.Select(a=>(a.FormKey,a.ObjectBounds))).ToDictionary(a=>a.FormKey,a=>a.ObjectBounds);
  foreach(var r in cell.Temporary.Cast<IPlaced>().Concat(world.TopCell!.Persistent)){
   P3Float? at=r switch{PlacedObject op=>op.Position,PlacedNpc np=>np.Position,_=>null};if(at is not {} p)continue;
   float rise=Ground(p.X,p.Y);
   if(r is PlacedObject fixedProp&&nativeBounds.TryGetValue(fixedProp.Base.FormKey,out var bounds)){
    float yaw=fixedProp.Rotation.Z;float low=float.MaxValue;
    foreach(float xx in new[]{(float)bounds.First.X,0,bounds.Second.X})foreach(float yy in new[]{(float)bounds.First.Y,0,bounds.Second.Y})low=MathF.Min(low,Ground(p.X+xx*MathF.Cos(yaw)+yy*MathF.Sin(yaw),p.Y+yy*MathF.Cos(yaw)-xx*MathF.Sin(yaw),false));
    rise=low; // no floating low corners; structural pads remain exactly flat
   }
   if(r is PlacedObject trim){
    if(r.EditorID?.StartsWith("TLM_WS_Boundary",StringComparison.Ordinal)==true){trim.MajorRecordFlagsRaw|=0x800;hidden.Add(r.EditorID);}
    if(r.EditorID is "TLM_WS_RoadMarkerLeft" or "TLM_WS_RoadMarkerRight")trim.Scale=.40f;
   }
   float targetZ=p.Z+rise;
   if(r.EditorID is "TLM_WS_RoadMarkerLeft" or "TLM_WS_RoadMarkerRight"){
    // Original64 pivot offset belonged to the full-height post. Ground the
    // actual scaled NIF footing instead of retaining that now-floating offset.
    var b=assets.GetProperty("FenceWoodPost01").GetProperty("nif").GetProperty("bottomBandBounds").EnumerateArray().Select(v=>v.GetSingle()*.40f).ToArray();float low=float.MaxValue;
    foreach(float xx in new[]{b[0],0,b[3]})foreach(float yy in new[]{b[1],0,b[4]})low=MathF.Min(low,Ground(p.X+xx,p.Y+yy,false));
    targetZ=low-b[5]-4;
   }
   var target=new P3Float(p.X,p.Y,targetZ);
   if(r is PlacedObject objSet)objSet.Position=target;else if(r is PlacedNpc npcSet)npcSet.Position=target;
   moved.Add(new{id=r.EditorID,form=r.FormKey.ToString(),oldZ=p.Z,z=target.Z,ground=rise});
  }
  void Put(string id,string asset,float x,float y,float? support=null,float yaw=0,float scale=1){
   var expected=assets.GetProperty(asset);var a=native.Statics.Single(a=>a.EditorID==asset&&a.FormKey.ID==Convert.ToUInt32(expected.GetProperty("id").GetString(),16));
   if(a.Model?.File?.ToString()!=expected.GetProperty("model").GetString())throw new InvalidDataException("Opening owned model mismatch");
   var b=expected.GetProperty("nif").GetProperty("bottomBandBounds").EnumerateArray().Select(v=>v.GetSingle()*scale).ToArray();
   if(support==null){
    float bestCost=float.MaxValue,bx=x,by=y;var render=expected.GetProperty("nif").GetProperty("renderBounds").EnumerateArray().Select(v=>v.GetSingle()*scale).ToArray();float radius=MathF.Max(MathF.Max(MathF.Abs(render[0]),render[3]),MathF.Max(MathF.Abs(render[1]),render[4]));
    foreach(int ox in new[]{0,-64,64,-128,128})foreach(int oy in new[]{0,-64,64,-128,128}){
     float xx=x+ox,yy=y+oy;if(xx-radius<128||xx+radius>3968||yy-radius<128||yy+radius>3968||MathF.Min(RoadHeight(Road,xx,yy).D,RoadHeight(Bypass,xx,yy).D)<96+radius||Expansion.Routes.Any(route=>RoadHeight(route.Points.Select(p=>(p.X,p.Y,0f)).ToArray(),xx,yy).D<96+radius))continue;
     if(world.TopCell!.Persistent.Any(r=>{P3Float? pos=r switch{IPlacedNpcGetter n=>n.Position,IPlacedObjectGetter o=>o.Position,_=>null};return pos is {} q&&r.EditorID?.StartsWith("TLM_WS_ST_",StringComparison.Ordinal)==true&&MathF.Sqrt(MathF.Pow(q.X-xx,2)+MathF.Pow(q.Y-yy,2))<128+radius;}))continue;
     float lo=float.MaxValue,hi=float.MinValue;foreach(float fx in new[]{b[0],0,b[3]})foreach(float fy in new[]{b[1],0,b[4]}){float g=Ground(xx+fx,yy+fy,false);lo=MathF.Min(lo,g);hi=MathF.Max(hi,Ground(xx+fx,yy+fy));}float range=hi-lo;if(range>56)continue;
     float cost=range*2+MathF.Sqrt(ox*ox+oy*oy);if(cost<bestCost){bestCost=cost;bx=xx;by=yy;}
    }
    if(bestCost==float.MaxValue)throw new InvalidDataException("No bounded grounded opening prop site: "+id);x=bx;y=by;
   }
   float low=float.MaxValue,high=float.MinValue;
   foreach(float xx in new[]{b[0],0,b[3]})foreach(float yy in new[]{b[1],0,b[4]}){float gx=x+xx*MathF.Cos(yaw)+yy*MathF.Sin(yaw),gy=y+yy*MathF.Cos(yaw)-xx*MathF.Sin(yaw);low=MathF.Min(low,Ground(gx,gy,false));high=MathF.Max(high,Ground(gx,gy));}
   float z=asset=="workshop_ShackMidFloor01Foundation"?support!.Value+14:support is {} surface?surface-b[2]:low-b[5]-4;
   if(support==null&&high-(z+b[2])>64)throw new InvalidDataException("Opening prop footing too steep: "+id);
   var placed=new PlacedObject(mod.GetNextFormKey(),Fallout4Release.Fallout4){EditorID="TLM_OPEN_"+id,Position=new P3Float(x,y,z),Rotation=new P3Float(0,0,yaw)};if(scale!=1)placed.Scale=scale;placed.Base.SetTo(a.FormKey);cell.Temporary.Add(placed);
   fresh.Add(new{id=placed.EditorID,form=placed.FormKey.ToString(),asset,model=a.Model!.File!.ToString(),x,y,z,yaw,scale,groundMin=low,groundMax=high,support= support,maximumEmbed=high-(z+b[2])});
  }
  int index=0;
  foreach(var p in new[]{(192,1600),(384,2112),(256,2624),(640,2944),(512,3456),(1024,3712),(1536,3840),(1792,3840),(2304,3840),(3850,896),(3850,1408),(3880,1920),(3850,2432),(3850,2944),(3880,3456),(3850,3840)})Put("RidgeTree"+(++index),index is 2 or 4 or 6?"TreeMapleForestsmall1":"TreeMapleForest6",p.Item1,p.Item2);
  index=0;foreach(var p in new[]{(340,1040),(980,1520),(1280,1856),(1580,2512),(1220,3520)})Put("Stump"+(++index),index%2==0?"TreeStumpGS01":"TreeStumpSMarsh02",p.Item1,p.Item2);
  foreach(int x in new[]{2792,3048,3304})foreach(int y in new[]{2800,3056})Put("CabinFoundation"+x+"_"+y,"workshop_ShackMidFloor01Foundation",x,y,128);
  Put("CabinDesk","HighTechDesk01_Main_DirtyStatic",2820,2780,144);
  Put("CabinLamp","DeskLamp02On",2820,2780,200);
  Put("CabinLocker","Prewar_Locker_WallEmpty02",2720,2960,144,-MathF.PI/2);
  Put("YardBench","NPCBenchParkSit01Static",2640,2600,128);
  Put("HollowRoutePost","FenceWoodPost01",1120,1490,scale:.40f);
  Put("ShoulderRoutePost","FenceWoodPost01",1400,1120,scale:.40f);
  index=0;foreach(var p in new[]{(480,1472),(1180,1520),(1390,1980),(1480,2480),(1660,3200),(2100,3760),(3260,1050),(3350,1520),(3760,1840),(3760,2310),(800,3200),(3750,3630)})Put("Understory"+(++index),index%3==0?"Marshshrub01":index%3==1?"TreeCedarShrub01":"DeadShrub04",p.Item1,p.Item2,scale:.65f);
  index=0;foreach(var p in new[]{(3300,1450),(3490,2020),(3840,2250),(3780,2680)})Put("RockCut"+(++index),"RockBoulder03",p.Item1,p.Item2);
  // Keep exact typed site contracts in sync with the authorized ground Z
  // projection; names/XY/aliases/quests are unchanged.
  foreach(var sites in new[]{WorldStory.GreenwaterSites,WorldStory.NightMailSites,WorldStory.RedHollowSites,WorldStory.FourFlagsSites,WorldStory.BlackLedgerSites})foreach(var key in sites.Keys.ToArray()){var p=sites[key];sites[key]=(p.X,p.Y,p.Z+Ground(p.X,p.Y));}
  return new{scope="Original one-cell opening; real signedVHGT and normals; native walk/render unverified",profile=Road.Select(p=>new{x=p.X,y=p.Y,height=Ground(p.X,p.Y)}),pads=Pads.Select(p=>new{minX=p.X0,minY=p.Y0,maxX=p.X1,maxY=p.Y1,height=p.Z}),moved,newProps=fresh,hiddenBoundaryPickets=hidden,materials,terrain="Existing33grid/critical grade retained; asymmetric banks and original native material masks; native view pending"};
 }
}
