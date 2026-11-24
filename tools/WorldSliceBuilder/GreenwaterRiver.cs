using Mutagen.Bethesda;
using Mutagen.Bethesda.Fallout4;
using Mutagen.Bethesda.Plugins;
using Mutagen.Bethesda.Plugins.Records;
using Noggog;
using System.Text.Json;

// Original story-world southern river cell; no donor LAND/placed/navmesh import.
public static class GreenwaterRiver {
 public const float Water=-64,Deck=80;
 static float Smooth(float t){t=Math.Clamp(t,0,1);return t*t*(3-2*t);}
 public static int Height(int ix,int iy){
  if(ix==0||ix==32||iy==0||iy==32)return 0;
  float x=ix*128,y=iy*128-4096,u=iy*128,center=2700+96*MathF.Sin(u/700),d=MathF.Abs(x-center);
  float z=d<240?-192:d<1280?-192+(d-240)*.30f:120+MathF.Min(520,(d-1280)*.18f);
  // Dry town terrace and broad approach; stream remains physically carved.
  float dx=MathF.Max(MathF.Max(1280-x,x-2240),0),dy=MathF.Max(MathF.Max(-2816-y,y+1280),0),dist=MathF.Sqrt(dx*dx+dy*dy);
  if(dist<256)z+=(64-z)*(1-Smooth(dist/256));
  // A grounded far-bank landing joins the gangway to the larger dry hillside.
  float ex=MathF.Max(MathF.Max(3456-x,x-3968),0),ey=MathF.Max(MathF.Max(-2432-y,y+1920),0),ed=MathF.Sqrt(ex*ex+ey*ey);if(ed<256)z+=(88-z)*(1-Smooth(ed/256));
  float edge=MathF.Min(MathF.Min(x,4096-x),MathF.Min(u,4096-u));z*=Smooth(edge/384);
  return (int)MathF.Round(z/8)*8;
 }
 public static float Ground(float x,float y,bool upper=true){
  int ix=Math.Clamp((int)MathF.Floor(x/128),0,31),iy=Math.Clamp((int)MathF.Floor((y+4096)/128),0,31);float u=Math.Clamp((x-ix*128)/128,0,1),v=Math.Clamp((y+4096-iy*128)/128,0,1);
  float a=Height(ix,iy),b=Height(ix+1,iy),c=Height(ix,iy+1),d=Height(ix+1,iy+1);float t=v<=u?a+(b-a)*u+(d-b)*v:a+(d-c)*u+(c-a)*v,s=u+v<=1?a+(b-a)*u+(c-a)*v:d+(c-d)*(1-u)+(b-d)*(1-v);return upper?MathF.Max(t,s):MathF.Min(t,s);
 }
 public static object Apply(IFallout4ModGetter native,Fallout4Mod mod,Worldspace world,IFallout4ModGetter story){
  var common=native.Worldspaces.Single(w=>w.EditorID=="Commonwealth");if(common.Water.IsNull||common.Climate.IsNull)throw new InvalidDataException("Native water/climate unresolved");
  var water=native.Waters.Single(w=>w.FormKey.ID==0x1C358E&&w.EditorID=="ExtRiverNFoothillsWaterSW");world.Water.SetTo(water.FormKey);world.ObjectBoundsMin=new P2Float(0,-1);world.ObjectBoundsMax=new P2Float(1,1); // Mutagen bounds are cells; native NAM0/9 are units.
  var block=new WorldspaceBlock{BlockNumberX=0,BlockNumberY=-1,GroupType=GroupTypeEnum.ExteriorCellBlock};var sub=new WorldspaceSubBlock{BlockNumberX=0,BlockNumberY=-1,GroupType=GroupTypeEnum.ExteriorCellSubBlock};block.Items.Add(sub);world.SubCells.Add(block);
  var cell=new Cell(mod.GetNextFormKey(),Fallout4Release.Fallout4){EditorID="TLM_GWR_Cell",Name="Greenwater river landing",Grid=new CellGrid{Point=new P2Int(0,-1)},Flags=Cell.Flag.HasWater,WaterHeight=Water};sub.Items.Add(cell);
  var bytes=new Array2d<byte>(33,33,0);var normals=new Array2d<P3UInt8>(33,33,new P3UInt8(0,0,127));
  for(int y=0;y<33;y++)for(int x=0;x<33;x++){
   int before=x>0?Height(x-1,y):y>0?Height(0,y-1):0,delta=(Height(x,y)-before)/8;if(delta< -128||delta>127)throw new InvalidDataException("GW VHGT overflow");bytes[x,y]=unchecked((byte)(sbyte)delta);
   float dx=(Height(Math.Min(32,x+1),y)-Height(Math.Max(0,x-1),y))/(x is 0 or 32?128f:256f),dy=(Height(x,Math.Min(32,y+1))-Height(x,Math.Max(0,y-1)))/(y is 0 or 32?128f:256f),len=MathF.Sqrt(1+dx*dx+dy*dy);byte N(float a)=>unchecked((byte)(sbyte)Math.Clamp((int)MathF.Round(a/len*127),-127,127));normals[x,y]=new P3UInt8(N(-dx),N(-dy),N(1));
  }
  var land=new Landscape(mod.GetNextFormKey(),Fallout4Release.Fallout4){DATA=new byte[]{0x1D,0,0,0},VertexHeightMap=new LandscapeVertexHeightMap{Offset=0,HeightMap=bytes},VertexNormals=normals,Textures=new()};cell.Landscape=land;
  ILandscapeTextureGetter soil=native.LandscapeTextures.Single(t=>t.EditorID=="LBlastedForestDirt01"),forest=native.LandscapeTextures.Single(t=>t.EditorID=="LForestFloor01"),gravel=native.LandscapeTextures.Single(t=>t.EditorID=="LDirtGravel01");
  foreach(var t in new[]{soil,forest,gravel})land.Textures.Add(t.ToLink<ILandscapeTextureGetter>());
  foreach(var q in Enum.GetValues<Quadrant>()){
   int ox=((int)q&1)*16,oy=((int)q>>1)*16;land.Layers.Add(new BaseLayer{Header=new LayerHeader{Texture=soil.ToLink<ILandscapeTextureGetter>(),Quadrant=q,LayerNumber=ushort.MaxValue}});
   for(int layer=0;layer<2;layer++){
    using var stream=new MemoryStream();using(var writer=new BinaryWriter(stream,System.Text.Encoding.UTF8,true))for(int y=0;y<17;y++)for(int x=0;x<17;x++){
     float xx=(ox+x)*128,yy=(oy+y)*128-4096;bool deck=xx>=1280&&xx<=3072&&yy>=-2560&&yy<=-1536;float wet=1-Smooth((Ground(xx,yy)-Water)/48),path=1-Smooth((MathF.Abs(xx-1800)-96)/160);
     float gravelWeight=MathF.Max(wet*.8f,path*.75f);float w=layer==0?(1-gravelWeight)*(1-wet)*(deck?0:.55f+.25f*MathF.Sin(xx/330+yy/510)):gravelWeight;writer.Write((ushort)(y*17+x));writer.Write((ushort)0);writer.Write(w);
    }
    land.Layers.Add(new AlphaLayer{Header=new LayerHeader{Texture=(layer==0?forest:gravel).ToLink<ILandscapeTextureGetter>(),Quadrant=q,LayerNumber=(ushort)layer},AlphaLayerData=stream.ToArray()});
   }
  }
  var props=new List<object>();
  var directory=new DirectoryInfo(AppContext.BaseDirectory);while(directory!=null&&!File.Exists(Path.Combine(directory.FullName,"tools/OpeningEnvironment/donors.json")))directory=directory.Parent;
  if(directory==null)throw new InvalidDataException("GW footing metadata absent");using var footing=JsonDocument.Parse(File.ReadAllText(Path.Combine(directory.FullName,"tools/OpeningEnvironment/donors.json")));var footAssets=footing.RootElement.GetProperty("assets");
  void Put(string role,string asset,float x,float y,float z,float yaw=0,float scale=1){
   var donor=native.Statics.Single(t=>t.EditorID==asset);if(donor.Model==null||donor.VirtualMachineAdapter!=null)throw new InvalidDataException("GW passive donor unsupported");
   if(role.StartsWith("Tree")||role.StartsWith("Rock")||role.StartsWith("Understory")){
    var b=footAssets.GetProperty(asset).GetProperty("nif").GetProperty("bottomBandBounds").EnumerateArray().Select(v=>v.GetSingle()).ToArray();float lo=float.MaxValue,hi=float.MinValue;foreach(float xx in new[]{b[0],0,b[3]})foreach(float yy in new[]{b[1],0,b[4]}){lo=MathF.Min(lo,Ground(x+xx,y+yy,false));hi=MathF.Max(hi,Ground(x+xx,y+yy));}z=lo-b[5]-2;if(hi-(z+b[2])>64)throw new InvalidDataException("GW footing too steep: "+role);
   }
   var r=new PlacedObject(mod.GetNextFormKey(),Fallout4Release.Fallout4){EditorID="TLM_GWR_"+role,Position=new P3Float(x,y,z),Rotation=new P3Float(0,0,yaw)};if(scale!=1)r.Scale=scale;r.Base.SetTo(donor.FormKey);cell.Temporary.Add(r);props.Add(new{id=r.EditorID,form=r.FormKey.ToString(),asset,model=donor.Model!.File!.ToString(),x,y,z,yaw,scale});
  }
  // Contiguous stock collision floors provide town planks and Queen/gangway.
  int index=0;foreach(int x in new[]{1408,1664,1920,2176,2688,2944,3200})foreach(int y in new[]{-2432,-2176,-1920,-1664})Put("Deck"+(++index),"workshop_ShackMidFloor01B",x,y,Deck);
  Put("TownGangway","workshop_ShackMidFloor01B",2432,-2176,Deck);
  foreach(int x in new[]{3456,3712})Put("FarBankWalk"+x,"workshop_ShackMidFloor01B",x,-2176,Deck);
  foreach(int x in new[]{2320,2544,3344,3568})foreach(int y in new[]{-2288,-2064})Put("BridgePile"+x+"_"+y,"FenceWoodPost01",x,y,96-176*1.25f,scale:1.25f);
  index=0;foreach(int y in new[]{-2432,-2048,-1664})Put("QueenBarge"+(++index),"Barge_01_Mid",2944,y,Deck-3.359375f);
  Put("SkiffHull","Rowboat01",2440,-3000,-55);
  // Raised, roofed cook/store shelter and open Queen canopy, kept off approaches.
  foreach(var center in new[]{(1664,-1664),(2944,-1664)}){
   Put("Roof"+center.Item1,"ShackMidRoof01",center.Item1,center.Item2,Deck+32);
   foreach(int dx in new[]{-112,112})foreach(int dy in new[]{-112,112})Put("RoofPost"+center.Item1+"_"+dx+"_"+dy,"FenceWoodPost01",center.Item1+dx,center.Item2+dy,Deck+64);
  }
  // Gently supported irregular vegetation, not route-sized obstacles.
  index=0;foreach(var p in new[]{(512,-768),(900,-1152),(512,-1664),(768,-2304),(512,-2944),(1100,-3456),(1664,-3584),(3456,-640),(3712,-1152),(3584,-2800),(3600,-3456),(2944,-3584)})Put("Tree"+(++index),index%3==0?"TreeMapleForest6":"TreeMapleForestsmall1",p.Item1,p.Item2,Ground(p.Item1,p.Item2,false)+4);
  index=0;foreach(var p in new[]{(1000,-1400),(950,-2700),(1450,-3300),(3400,-1400),(3450,-3100),(3000,-3400)})Put("Rock"+(++index),"RockBoulder03",p.Item1,p.Item2,Ground(p.Item1,p.Item2,false)+45);
  var controlPoses=new Dictionary<string,(float X,float Y)>{["ChuteStart"]=(1440,440),["LabelChute"]=(1408,820),["LabelLanding"]=(1664,600),["ReliefStores"]=(2176,900),["OffSideArrival"]=(2600,120),["OffSideSight"]=(2660,260),["GangwaySight"]=(2400,360),["Exit"]=(1550,300),["RationBoard"]=(1960,980),["Skiff"]=(2176,120),["Table"]=(2450,540),["Strongbox"]=(3000,650),["FireControl"]=(2890,480),["Chain"]=(2500,260),["Pilot"]=(2800,200),["LabelQueen"]=(2920,900),["Rafferty"]=(2200,500),["Belden"]=(2100,380),["Crew1"]=(2380,880),["Crew2"]=(2560,920)};
  var controls=new HashSet<string>{"Exit","RationBoard","Skiff","Table","Strongbox","FireControl","Chain","Pilot","LabelChute","LabelLanding","LabelQueen","ReliefStores"};
  var bobble=native.MiscItems.Single(m=>m.FormKey.ID==0x178B62&&m.EditorID=="BobbleHead_Speech");if(bobble.Model?.File?.ToString()!=@"SetDressing\Bobbleheads\Speech.nif")throw new InvalidDataException("GW control icon donor changed");
  index=0;foreach(var p in new[]{(700,-900),(800,-1600),(950,-2000),(700,-2600),(850,-3000),(1200,-3200),(2000,-3500),(3200,-3400),(3500,-2900),(3500,-1800),(3400,-1100),(3000,-700),(1100,-900),(600,-1900),(900,-2850),(3300,-3100),(3450,-2300),(3100,-1200)})Put("Understory"+(++index),"TreeCedarShrub01",p.Item1,p.Item2,0);
  var moved=new List<object>();var buttons=new List<object>();
  foreach(var key in WorldStory.GreenwaterSites.Keys.Where(k=>k is not "MercyTravel" and not "MercyReturn" and not "ReliefSupply").ToArray()){
   var old=WorldStory.GreenwaterSites[key];var r=world.TopCell!.Persistent.Single(r=>r.EditorID=="TLM_WS_ST_GW_"+key);var xy=controlPoses.GetValueOrDefault(key,(old.X,old.Y));float x=xy.Item1,y=xy.Item2-2560,z=Deck+old.Z+(old.Z==0?32:0);
   // Separate shore and vessel with an actual water gap, crossed only by
   // the supported front gangway. Keep the coupled Queen cast in this cell.
   if(new[]{"LabelQueen","Table","Hatcher","Strongbox","Crew1","Crew2","FireControl","Burnt","OffSideArrival","OffSideSight","CargoLashed","Chain","Pilot"}.Contains(key))x+=256;
   if(controls.Contains(key)&&r is PlacedObject button){
    var original=story.Activators.Single(a=>a.FormKey==button.Base.FormKey);if(original.VirtualMachineAdapter!=null)throw new InvalidDataException("GW control model swap would import script behavior");
    var act=original.Duplicate(mod.GetNextFormKey());act.EditorID="TLM_GWR_Control_"+key;act.Model=bobble.Model!.DeepCopy();act.ObjectBounds=bobble.ObjectBounds.DeepCopy();mod.Activators.Add(act);button.Base.SetTo(act.FormKey);button.Scale=4;
    z=Deck+16+56+.01222229f;Put("ControlDesk"+key,"HighTechDesk01_Main_DirtyStatic",x,y,Deck+16);var stance=key is "Skiff" or "Strongbox" or "LabelQueen"?new[]{x-160,y,Deck+32}:key=="Pilot"?new[]{x+160,y,Deck+32}:new[]{x,y-144,Deck+32};buttons.Add(new{alias=key,reference=button.FormKey.ToString(),activator=act.FormKey.ToString(),model=act.Model!.File!.ToString(),scale=4,support=Deck+16+56,x,y,z,stance=stance});
   }
   // The steeple reference is ALSO Hatcher's MoveTo/hanging anchor: keep it
   // at the real walking surface instead of placing the actor on a kiosk.
   if(key=="Steeple")z=Deck+16;
   if(key is "CargoWhole" or "CargoReduced" or "CargoLashed" or "Burnt" &&r is PlacedObject cargo){
    var original=story.Activators.Single(a=>a.FormKey==cargo.Base.FormKey);var crate=native.Statics.Single(t=>t.FormKey.ID==0x1467CB&&t.EditorID=="CrateLargeGrayRusty");var act=original.Duplicate(mod.GetNextFormKey());act.EditorID="TLM_GWR_Cargo_"+key;act.Model=crate.Model!.DeepCopy();act.ObjectBounds=crate.ObjectBounds.DeepCopy();mod.Activators.Add(act);cargo.Base.SetTo(act.FormKey);cargo.Scale=.35f;z=Deck+16+.000006f;
   }
   if(r is PlacedObject p)p.Position=new P3Float(x,y,z);else if(r is PlacedNpc n)n.Position=new P3Float(x,y,z);WorldStory.GreenwaterSites[key]=(x,y,z);moved.Add(new{id=r.EditorID,alias=key,x,y,z,surface=Deck});
  }
  return new{cell=cell.EditorID,water=water.FormKey.ToString(),waterHeight=Water,baselineSupportedArea=1664*768,newGrossTerrainArea=4096*4096,moved,props,buttons,native="OPEN: water exposure, physics/swimming, walking/collision/visibility; scripts unchanged"};
 }
}
