using Mutagen.Bethesda;
using Mutagen.Bethesda.Fallout4;
using Mutagen.Bethesda.Plugins;
using Mutagen.Bethesda.Plugins.Records;
using Noggog;
using System.Text.Json;

// Optional separate exterior prototype. Never edits the existing preview ESP,
// a master record, installed files or a save. Output must be a workspace folder.
var privateMode=args.LastOrDefault();
bool combinedArt=privateMode=="--private-art-combined";
bool gatheringGreen=privateMode=="--private-gathering-green";
bool fenceComparison=combinedArt||privateMode=="--private-fence-ab";
bool shelterDetail=combinedArt||gatheringGreen||privateMode=="--private-shelter-detail";
if(fenceComparison||shelterDetail)args=args[..^1];
bool natural=args.LastOrDefault()=="--natural";
bool expanded=natural||args.LastOrDefault()=="--expand";
if(expanded)args=args[..^1];
if((fenceComparison||shelterDetail)&&!natural){Console.Error.WriteLine("Private art modes require --natural; combined mode must be explicit.");return 2;}
if(args.Length!=2&&(args.Length!=4||args[2]!="--story-source")){Console.Error.WriteLine("WorldSliceBuilder <Fallout4.esm> <new-output-directory> [--story-source <TheLastMeridian.esp>] [--expand|--natural]");return 2;}
var input=Path.GetFullPath(args[0]);var output=Path.GetFullPath(args[1]);
var comparison=OperatingSystem.IsWindows()?StringComparison.OrdinalIgnoreCase:StringComparison.Ordinal;
var masterDirectory=Path.GetDirectoryName(input)!;
if(!File.Exists(input)){Console.Error.WriteLine("Master input must exist.");return 2;}
if(args.Length==4){
 var template=Path.GetFullPath(args[3]);var templateDirectory=Path.GetDirectoryName(template)!;
 if(!File.Exists(template)||!Path.GetFileName(template).Equals("TheLastMeridian.esp",StringComparison.OrdinalIgnoreCase)){Console.Error.WriteLine("Story source must be an existing TheLastMeridian.esp.");return 2;}
 if(output.Equals(template,comparison)||output.Equals(templateDirectory,comparison)||output.StartsWith(templateDirectory+Path.DirectorySeparatorChar,comparison)){Console.Error.WriteLine("Output must stay outside the story-source input directory.");return 2;}
}
if(output.Equals(input,comparison)||output.Equals(masterDirectory,comparison)||output.StartsWith(masterDirectory+Path.DirectorySeparatorChar,comparison)){
 Console.Error.WriteLine("Output must stay outside the master input directory.");return 2;
}
if(File.Exists(output)||(Directory.Exists(output)&&Directory.EnumerateFileSystemEntries(output).Any())){
 Console.Error.WriteLine("Output must be a new or empty staging directory; existing files will not be overwritten.");return 2;
}
using var master=Fallout4Mod.CreateFromBinaryOverlay(input,Fallout4Release.Fallout4);
Directory.CreateDirectory(output);
var mod=new Fallout4Mod(ModKey.FromNameAndExtension("TLMWorldSlice.esp"),Fallout4Release.Fallout4);
mod.ModHeader.Stats.Version=0.95f;
var world=mod.Worldspaces.AddNew("TLM_WS_Meridian");
world.Name="The Last Meridian - exterior prototype";
world.Flags=Worldspace.Flag.SmallWorld|Worldspace.Flag.CannotFastTravel|Worldspace.Flag.NoGrass|Worldspace.Flag.NoLodWater;
world.LandDefaults=new WorldspaceLandDefaults {DefaultLandHeight=0,DefaultWaterHeight=-2048};
world.ObjectBoundsMin=new P2Float(0,0);world.ObjectBoundsMax=new P2Float(4096,4096);
var climate=master.Worldspaces.First(w=>w.EditorID=="Commonwealth").Climate;
if(!climate.IsNull)world.Climate.SetTo(climate.FormKey);
world.TopCell=new Cell(mod.GetNextFormKey(),Fallout4Release.Fallout4){EditorID="TLM_WS_Persistent",MajorRecordFlagsRaw=0x400};
var block=new WorldspaceBlock {BlockNumberX=0,BlockNumberY=0,GroupType=GroupTypeEnum.ExteriorCellBlock};
var sub=new WorldspaceSubBlock {BlockNumberX=0,BlockNumberY=0,GroupType=GroupTypeEnum.ExteriorCellSubBlock};
world.SubCells.Add(block);block.Items.Add(sub);
var cell=new Cell(mod.GetNextFormKey(),Fallout4Release.Fallout4){EditorID="TLM_WS_Clearing",Name="Meridian - wreck road and Mercy yard",Grid=new CellGrid {Point=new P2Int(0,0)},WaterHeight=-2048};
sub.Items.Add(cell);
var texture=master.LandscapeTextures.Single(t=>t.EditorID=="LDirtGravel01");
var land=new Landscape(mod.GetNextFormKey(),Fallout4Release.Fallout4){
 DATA=new byte[]{0x1D,0,0,0},
 VertexNormals=new Array2d<P3UInt8>(33,33,new P3UInt8(0,0,127)),
 VertexHeightMap=new LandscapeVertexHeightMap {Offset=0,HeightMap=new Array2d<byte>(33,33,0)},
 Textures=new()
};
foreach(var quadrant in Enum.GetValues<Quadrant>())land.Layers.Add(new BaseLayer {Header=new LayerHeader {Texture=new FormLink<ILandscapeTextureGetter>(texture.FormKey),Quadrant=quadrant,LayerNumber=0}});
land.Textures.Add(texture.ToLink<ILandscapeTextureGetter>());cell.Landscape=land;
var placements=new List<object>();
// PRIVATE A/B only: sixteen boundary specimens, never Yard or a global swap.
// No allocation, position, rotation, enable-state, material or terrain change.
var fenceComparisonIds=new HashSet<string>(StringComparer.Ordinal);
foreach(var side in new[]{"South","West"})for(int i=4;i<=7;i++)fenceComparisonIds.Add("Boundary"+side+i);
foreach(var side in new[]{"North","East"})for(int i=21;i<=24;i++)fenceComparisonIds.Add("Boundary"+side+i);
var fenceSwaps=new List<object>();
var specimen=fenceComparison?master.Statics.Single(x=>x.EditorID=="PicketFenceStr02"):null;
if(specimen!=null){
 var control=master.Statics.Single(x=>x.EditorID=="PicketFenceB_PW_Fence01");
 var a=control.ObjectBounds;var b=specimen.ObjectBounds;
 if(control.FormKey.ID!=0x125C67||specimen.FormKey.ID!=0x3622D||
    a.First.X!=-64||a.First.Y!=-2||a.First.Z!=0||a.Second.X!=64||a.Second.Y!=2||a.Second.Z!=96||
    b.First.X!=-64||b.First.Y!=-15||b.First.Z!=0||b.Second.X!=64||b.Second.Y!=5||b.Second.Z!=95)
  throw new InvalidDataException("Private fence identity/bounds differ from audited master; no fallback.");
}
var routeObstacles=new List<(string Id,float X,float Y,float MinX,float MaxX,float MinY,float MaxY)>();
FormKey Static(string id)=>master.Statics.Single(x=>x.EditorID==id).FormKey;
FormKey Furniture(string id)=>master.Furniture.Single(x=>x.EditorID==id).FormKey;
void Put(string id,FormKey key,float x,float y,float z=0,float yaw=0){
 // Two decorative posts otherwise seal the new west-street junction. Keep
 // their form IDs and all quest coordinates; default mode is unchanged.
 if(expanded&&id=="Main15L"){x=2450;y=2550;}
 if(expanded&&id=="Main16L"){x=2440;y=2360;}
 var p=new PlacedObject(mod.GetNextFormKey(),Fallout4Release.Fallout4){EditorID="TLM_WS_"+id,Position=new P3Float(x,y,z),Rotation=new P3Float(0,0,yaw)};
 if(specimen!=null&&fenceComparisonIds.Contains(id)){
  // Retain the already allocated reference; swap only its base. Geometry
  // checks below intentionally use the specimen's actual rotated bounds.
  fenceSwaps.Add(new{id=p.EditorID,form=p.FormKey.ToString(),oldBase=key.ToString(),newBase=specimen.FormKey.ToString(),x,y,z,yaw});
  key=specimen.FormKey;
 }
 // Keep the original route-reference allocation, but hide the dense paired
 // bollards in the expanded landscape. Explicit road markers and the town
 // gateway remain visible; the default shell keeps its original route posts.
 bool hiddenRoutePost=natural&&(id.StartsWith("Main",StringComparison.Ordinal)||id.StartsWith("Bypass",StringComparison.Ordinal));
 if(hiddenRoutePost)p.MajorRecordFlagsRaw|=0x800; // initially disabled, own reference only
 p.Base.SetTo(key);cell.Temporary.Add(p);placements.Add(new{id=p.EditorID,form=p.FormKey.ToString(),@base=key.ToString(),x,y,z,yaw,initiallyDisabled=hiddenRoutePost});
 var bounds=master.Statics.FirstOrDefault(s=>s.FormKey==key)?.ObjectBounds??master.Furniture.Single(f=>f.FormKey==key).ObjectBounds;
 if(id is "Bed" or "Couch"){
  if(x+bounds.First.X-2668<128||3428-x-bounds.Second.X<128||y+bounds.First.Y-2676<128||3180-y-bounds.Second.Y<128)
   throw new InvalidDataException("Furniture model bounds need 128-unit body clearance from the cabin wall planes: "+id);
 }
 if(!hiddenRoutePost&&id!="Arrival"&&z+bounds.Second.Z>1&&z+bounds.First.Z<128){
  var xx=new List<float>();var yy=new List<float>();
  foreach(float bx in new[]{(float)bounds.First.X,bounds.Second.X})foreach(float by in new[]{(float)bounds.First.Y,bounds.Second.Y}){xx.Add(x+bx*MathF.Cos(yaw)+by*MathF.Sin(yaw));yy.Add(y+by*MathF.Cos(yaw)-bx*MathF.Sin(yaw));}
  routeObstacles.Add((id,x,y,xx.Min(),xx.Max(),yy.Min(),yy.Max()));
 }
}
Put("Arrival",Static("COCMarkerHeading"),448,640,32,MathF.PI/4);
// Three separated station silhouettes. This first world milestone has no
// quest/actor binding; the existing playable QASmoke preview stays untouched.
Put("WreckDebrisA",Static("ExtRubble_BricksLrg_Clump01"),400,1000);
Put("WreckDebrisB",Static("StoneWallOldRubble"),800,650);
Put("WreckDeadwood",Static("DebrisPileLargeWood01"),300,1200);
Put("RoadMarkerLeft",Static("FenceWoodPost01"),1800,1860,64);
Put("RoadMarkerRight",Static("FenceWoodPost01"),2000,1540,64);
// Small roofed cabin using modular existing pieces, with a full tile's width
// deliberately absent from the front wall rather than an untested locked door.
var floor=Static("workshop_ShackMidFloor01B");var roof=Static("ShackMidRoof01");
for(int col=0;col<3;col++)for(int row=0;row<2;row++){
 float x=2792+col*256,y=2800+row*256;
 Put($"CabinFloor{col}{row}",floor,x,y,16);Put($"CabinRoof{col}{row}",roof,x,y,16);
}
var wall=Static("ShackWallFlat02");
for(int col=0;col<3;col++){
 float x=2792+col*256;
 Put("CabinBackWall"+col,wall,x,3056,16,MathF.PI);
 if(col!=1)Put("CabinFrontWall"+col,wall,x,2800,16);
}
for(int row=0;row<2;row++){
 float y=2800+row*256;
 Put("CabinLeftWall"+row,wall,2792,y,16,MathF.PI/2);
 Put("CabinRightWall"+row,wall,3304,y,16,-MathF.PI/2);
}
Put("Bed",Furniture("WorkshopNpcBedMilitaryCottLay01"),2832,2984,16);
Put("Couch",Furniture("NpcCouchSet02Weathered1x2Straight01Sit01"),3232,2984,9,MathF.PI);
// Yard fence: 128-unit panels, explicit 256-unit opening centered on X3048.
var fence=Static("PicketFenceB_PW_Fence01");
for(int i=0;i<10;i++){
 float x=2472+i*128;
 if(x<2920||x>3176)Put("YardFront"+i,fence,x,2432);
 Put("YardBack"+i,fence,x,3456);
}
for(int i=0;i<8;i++){
 float y=2496+i*128;
 Put("YardLeft"+i,fence,2408,y,0,MathF.PI/2);Put("YardRight"+i,fence,3688,y,0,MathF.PI/2);
}
// Perimeter rail discourages accidental walking off the single-cell terrain.
// It is not an invisible wall or proof that a player cannot jump the edge.
for(int i=0;i<30;i++){
 float along=192+i*128;
 Put("BoundarySouth"+i,fence,along,128);Put("BoundaryNorth"+i,fence,along,3968);
 Put("BoundaryWest"+i,fence,128,along,0,MathF.PI/2);Put("BoundaryEast"+i,fence,3968,along,0,MathF.PI/2);
}
// Continuous paired edges reserve a 256-unit main corridor. Low posts don't
// claim sign lettering; the parallel east bypass stays away from hold-up center.
var edge=Static("FenceWIBollardPost01");
var mainRoute=new[]{(448f,640f),(700f,900f),(1900f,1700f),(2600f,2200f),(3048f,2200f),(3048f,2432f)};
var bypassRoute=new[]{(1200f,1200f),(2200f,1000f),(2700f,1700f),(2600f,2200f)};
float Distance(float x,float y,(float X,float Y) a,(float X,float Y) b){float dx=b.X-a.X,dy=b.Y-a.Y,t=Math.Clamp(((x-a.X)*dx+(y-a.Y)*dy)/(dx*dx+dy*dy),0,1);return MathF.Sqrt(MathF.Pow(x-a.X-t*dx,2)+MathF.Pow(y-a.Y-t*dy,2));}
bool ClearAllRoutes(float x,float y)=>new[]{mainRoute,bypassRoute}.All(r=>Enumerable.Range(0,r.Length-1).All(i=>Distance(x,y,r[i],r[i+1])>=120));
void Route(string name,(float X,float Y)[] points){
 int index=0;
 for(int s=0;s<points.Length-1;s++){
  var a=points[s];var b=points[s+1];float dx=b.X-a.X,dy=b.Y-a.Y,len=MathF.Sqrt(dx*dx+dy*dy);
  int steps=(int)MathF.Ceiling(len/192);
  for(int i=0;i<=steps;i++){
   float t=(float)i/steps,x=a.X+t*dx,y=a.Y+t*dy;
   float lx=x-dy/len*144,ly=y+dx/len*144,rx=x+dy/len*144,ry=y-dx/len*144;
   if(ClearAllRoutes(lx,ly))Put(name+index+"L",edge,lx,ly,56);
   if(ClearAllRoutes(rx,ry))Put(name+index+"R",edge,rx,ry,56);index++;
  }
 }
}
Route("Main",mainRoute);Route("Bypass",bypassRoute);
// Verify a 192-unit-wide sampled center corridor stays clear of all placed
// object bounds at player height, including landmark debris/fences/furniture.
foreach(var route in new[]{mainRoute,bypassRoute})for(int s=0;s<route.Length-1;s++)for(int tick=0;tick<=100;tick++){
 float t=tick/100f,x=route[s].Item1*(1-t)+route[s+1].Item1*t,y=route[s].Item2*(1-t)+route[s+1].Item2*t;
 foreach(var p in routeObstacles){float dx=MathF.Max(MathF.Max(p.MinX-x,0),x-p.MaxX),dy=MathF.Max(MathF.Max(p.MinY-y,0),y-p.MaxY);if(dx*dx+dy*dy<96*96)throw new InvalidDataException("Object intrudes into 192-unit corridor: "+p.Id);}
}
var plugin=Path.Combine(output,"TLMWorldSlice.esp");
object? story=null;
var included=new List<ModKey>{ModKey.FromNameAndExtension("Fallout4.esm")};
if(args.Length==4){using var template=Fallout4Mod.CreateFromBinaryOverlay(args[3],Fallout4Release.Fallout4);story=WorldStory.Add(mod,world,cell,template);included.Add(template.ModKey);}
object? expansion=null;
object? details=null;
object? green=null;
var protectedPoints=new List<object>();
if(expanded){
 expansion=Expansion.Add(master,Put,natural);
 // Append only AFTER all existing scenery/story allocation. Default natural
 // mode and the owner bundle are unchanged.
 if(shelterDetail)details=ShelterDetails.Add(master,Put);
 if(gatheringGreen)green=GatheringGreen.Add(master,Put);
 // Recheck both old routes AND new streets after adding scenery. AABBs are
 // conservative coarse checks, not Havok/navmesh certification.
 foreach(var route in new[]{mainRoute,bypassRoute}.Concat(Expansion.Routes.Select(r=>r.Points)).Concat(gatheringGreen?GatheringGreen.Routes.Select(r=>r.Points):Enumerable.Empty<(float X,float Y)[]>()))for(int s=0;s<route.Length-1;s++)for(int tick=0;tick<=100;tick++){
  float t=tick/100f,x=route[s].Item1*(1-t)+route[s+1].Item1*t,y=route[s].Item2*(1-t)+route[s+1].Item2*t;
  foreach(var p in routeObstacles){float dx=MathF.Max(MathF.Max(p.MinX-x,0),x-p.MaxX),dy=MathF.Max(MathF.Max(p.MinY-y,0),y-p.MaxY);if(dx*dx+dy*dy<96*96)throw new InvalidDataException("Expanded object intrudes into 192-unit corridor: "+p.Id);}
 }
 foreach(var reference in world.TopCell!.Persistent){
  if(reference.EditorID is not {} id||!id.StartsWith("TLM_WS_ST_")||id is "TLM_WS_ST_AmbushSight" or "TLM_WS_ST_TownGate")continue;
  P3Float? at=reference switch {IPlacedNpcGetter n=>n.Position,IPlacedObjectGetter o=>o.Position,_=>null};
  if(at is not {} pos)throw new InvalidDataException("Missing protected story position: "+id);
  protectedPoints.Add(new{id,x=pos.X,y=pos.Y,z=pos.Z});
  foreach(var p in routeObstacles.Where(p=>p.Id.StartsWith("EX_")||p.Id is "Main15L" or "Main16L")){
   float dx=MathF.Max(MathF.Max(p.MinX-pos.X,0),pos.X-p.MaxX),dy=MathF.Max(MathF.Max(p.MinY-pos.Y,0),pos.Y-p.MaxY);
   if(dx*dx+dy*dy<128*128)throw new InvalidDataException("Expanded object intrudes into 128-unit story activation/standing space: "+p.Id+" / "+id);
  }
 }
 if(shelterDetail)foreach(var aisle in ShelterDetails.Aisles)for(int tick=0;tick<=100;tick++){
  float x=aisle.X,y=aisle.StartY+(aisle.EndY-aisle.StartY)*tick/100f;
  // Existing floors are the native-tested supporting surface atZ16, not
  // upright obstacles. No other obstruction is excluded from this screen.
  foreach(var p in routeObstacles.Where(p=>!p.Id.Contains("Floor",StringComparison.Ordinal))){
   float dx=MathF.Max(MathF.Max(p.MinX-x,0),x-p.MaxX),dy=MathF.Max(MathF.Max(p.MinY-y,0),y-p.MaxY);
   if(dx*dx+dy*dy<96*96)throw new InvalidDataException("Private shelter aisle blocked: "+aisle.Name+" / "+p.Id);
  }
 }
 if(gatheringGreen)foreach(var point in GatheringGreen.Standing)foreach(var p in routeObstacles.Where(p=>p.Id!=point.Bench)){
  float dx=MathF.Max(MathF.Max(p.MinX-point.X,0),point.X-p.MaxX),dy=MathF.Max(MathF.Max(p.MinY-point.Y,0),point.Y-p.MaxY);
  if(dx*dx+dy*dy<128*128)throw new InvalidDataException("Green bench side-entry standing space blocked: "+point.Bench+" / "+p.Id);
 }
}
mod.BeginWrite.ToPath(plugin).WithNoLoadOrder().WithExtraIncludedMasters(included.ToArray()).Write();
using var read=Fallout4Mod.CreateFromBinaryOverlay(plugin,Fallout4Release.Fallout4);
if(story!=null)WorldStory.Validate(read);
var gotWorld=read.Worldspaces.Single();var gotCell=gotWorld.SubCells.Single().Items.Single().Items.Single();
if(gotCell.Grid?.Point!=new P2Int(0,0)||gotCell.Landscape?.VertexHeightMap?.HeightMap.Width!=33||gotCell.Temporary.Count!=placements.Count)throw new InvalidDataException("World/cell/LAND/reference roundtrip failed");
var heights=gotCell.Landscape!.VertexHeightMap!.HeightMap;
if(heights.Height!=33||gotCell.Landscape.Layers.Count!=4||gotCell.Landscape.VertexNormals?.Width!=33)throw new InvalidDataException("Incomplete terrain grids/layers");
for(int y=0;y<33;y++)for(int x=0;x<33;x++)if(heights[x,y]!=0)throw new InvalidDataException("Unexpected terrain height delta");
if(read.Worldspaces.Any(w=>w.FormKey.ModKey!=mod.ModKey)||gotCell.FormKey.ModKey!=mod.ModKey)throw new InvalidDataException("Unexpected vanilla override");
if(read.EnumerateMajorRecords().Any(r=>r.FormKey.ModKey!=mod.ModKey))throw new InvalidDataException("Unexpected override record");
File.WriteAllText(Path.Combine(output,"world-slice.json"),JsonSerializer.Serialize(new{world=gotWorld.EditorID,worldForm=gotWorld.FormKey.ToString(),cell=gotCell.EditorID,cellForm=gotCell.FormKey.ToString(),entry="coc TLM_WS_Clearing (native entry pending)",terrain="new generated flat33x33LAND at height0",placementCount=placements.Count,storyReferenceCount=story==null?0:29,mainRoute=mainRoute.Select(p=>new{x=p.Item1,y=p.Item2}),bypassRoute=bypassRoute.Select(p=>new{x=p.Item1,y=p.Item2}),placements,nativeProof=story==null?"Shell: native acceptance recorded separately; no quest binding/navmesh":"Story candidate: native actor loading, alias binding, pickups, guides, peaceful choices, bypass and handoff UNVERIFIED; no navmesh/pursuit/combat proof"},new JsonSerializerOptions{WriteIndented=true}));
if(story!=null)File.WriteAllText(Path.Combine(output,"world-story.json"),JsonSerializer.Serialize(new{sourcePlugin=Path.GetFileName(args[3]),sourceSha256=Convert.ToHexString(System.Security.Cryptography.SHA256.HashData(File.ReadAllBytes(args[3]))),masters=read.ModHeader.MasterReferences.Select(m=>m.Master.ToString()),wiring=story,runtimeRequirement="Reviewed 7f3 departure runtime plus this candidate's exterior Guide and WorldEntry scripts; ESP hash alone does not establish script version"},new JsonSerializerOptions{WriteIndented=true}));
if(expansion!=null)File.WriteAllText(Path.Combine(output,"world-expansion.json"),JsonSerializer.Serialize(expansion,new JsonSerializerOptions{WriteIndented=true}));
if(expansion!=null)File.WriteAllText(Path.Combine(output,"world-clearance.json"),JsonSerializer.Serialize(new{method="Actual transformed ObjectBounds AABBs, player-height0..128; sampled every1/100segment; not Havok/navmesh proof",routeRadius=96,standingRadius=128,protectedPoints,obstacles=routeObstacles.Select(p=>new{id=p.Id,minX=p.MinX,maxX=p.MaxX,minY=p.MinY,maxY=p.MaxY})},new JsonSerializerOptions{WriteIndented=true}));
if(fenceComparison){
 if(fenceSwaps.Count!=16||gotCell.Temporary.OfType<IPlacedObjectGetter>().Count(r=>fenceComparisonIds.Contains((r.EditorID??"").Replace("TLM_WS_","",StringComparison.Ordinal))&&r.Base.FormKey==specimen!.FormKey)!=16)
  throw new InvalidDataException("Private fence comparison did not roundtrip sixteen exact base substitutions.");
 File.WriteAllText(Path.Combine(output,"private-fence-comparison.json"),JsonSerializer.Serialize(new{mode="PRIVATE sixteen-reference visual A/B; no native color/material/collision acceptance",control="00125C67 PicketFenceB_PW_Fence01",specimen="0003622D PicketFenceStr02",controlBounds=new[]{-64,-2,0,64,2,96},specimenBounds=new[]{-64,-15,0,64,5,95},unchangedYardPanels=34,unchangedBoundaryControls=104,policy="Same allocated form IDs, position, rotation, flags and pitch; no Z correction or material swap",swaps=fenceSwaps},new JsonSerializerOptions{WriteIndented=true}));
}
if(details!=null){
 var refs=gotCell.Temporary.OfType<IPlacedObjectGetter>().Where(r=>(r.EditorID??"").StartsWith("TLM_WS_EX_DETAIL_",StringComparison.Ordinal)).ToArray();
 if(refs.Length!=6)throw new InvalidDataException("Private shelter detail did not roundtrip exactly six references.");
 File.WriteAllText(Path.Combine(output,"private-shelter-details.json"),JsonSerializer.Serialize(new{detail=details,references=refs.Select(r=>new{id=r.EditorID,form=r.FormKey.ToString(),@base=r.Base.FormKey.ToString(),x=r.Position!.X,y=r.Position.Y,z=r.Position.Z,yaw=r.Rotation!.Z})},new JsonSerializerOptions{WriteIndented=true}));
}
if(green!=null){
 var refs=gotCell.Temporary.OfType<IPlacedObjectGetter>().Where(r=>(r.EditorID??"").StartsWith("TLM_WS_EX_GREEN_",StringComparison.Ordinal)).ToArray();
 if(refs.Length!=5)throw new InvalidDataException("Green did not roundtrip exactly five references.");
 File.WriteAllText(Path.Combine(output,"private-gathering-green.json"),JsonSerializer.Serialize(new{green,references=refs.Select(r=>new{id=r.EditorID,form=r.FormKey.ToString(),@base=r.Base.FormKey.ToString(),x=r.Position!.X,y=r.Position.Y,z=r.Position.Z,yaw=r.Rotation!.Z})},new JsonSerializerOptions{WriteIndented=true}));
}
Console.WriteLine($"Wrote {plugin}: NEW exterior world/cell + generated LAND, {placements.Count} shell references + {(story==null?0:29)} story references; binary readback passed. Native story acceptance pending.");
return 0;
