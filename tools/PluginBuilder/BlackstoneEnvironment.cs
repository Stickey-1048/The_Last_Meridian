using Mutagen.Bethesda;using Mutagen.Bethesda.Fallout4;using Mutagen.Bethesda.Plugins;using Mutagen.Bethesda.Plugins.Records;using Noggog;using System.Text.Json;
namespace Tlm.PluginBuilder;
public static class BlackstoneEnvironment {
 public static IEnumerable<(ICellGetter Cell,int Block,int Sub)> ReportCells(IFallout4ModGetter mod){foreach(var row in RedHollowEnvironment.ReportCells(mod))yield return row;foreach(var world in mod.Worldspaces.Where(w=>w.EditorID==Blackstone.World)){if(world.TopCell!=null)yield return(world.TopCell,0,0);foreach(var b in world.SubCells)foreach(var s in b.Items)foreach(var c in s.Items)yield return(c,b.BlockNumberX,s.BlockNumberX);}}
 public static bool OwnCell(string id)=>id is Blackstone.Persistent or Blackstone.Surface;
 public static string BaseEditor(string value){if(value.StartsWith("TLM_"))return value;var id=value.Split(':')[0];return Blackstone.Load("layout-models.json").GetProperty("assets").EnumerateObject().Single(p=>p.Value.GetProperty("id").GetString()==id).Name;}
}
public sealed partial class Builder {
 public object? BlackstoneEnvironmentReceipt{get;private set;}
 readonly Dictionary<string,float> blackstonePaperHeights=new();
 public PlacedSpec BlackstoneEffective(PlacedSpec p)=>blackstonePaperHeights.TryGetValue(p.EditorId,out var z)?p with{Up=z}:p;
 void BuildBlackstoneBases(){
  var extra=new[]{Blackstone.World,Blackstone.Persistent,Blackstone.Surface,"TLM_LAND_BS_Upper","TLM_LIGH_BS_NeutralFill","TLM_DOOR_BS_UpperService","TLM_DOOR_BS_RoomExit","TLM_DOOR_BS_Lower","TLM_DOOR_BS_LowerReturn"};var keys=extra.ToDictionary(n=>n,n=>_mod.GetNextFormKey(n));
  if(_vanillaMod==null){Pending.Add("Blackstone owned world/door/light construction requires actual master; no exterior/lighting claim in skeleton");return;}
  bool synthetic=_vanillaMod.Climates.Any(c=>c.EditorID=="RHSyntheticClimate");
  var assetMeta=Blackstone.Load("layout-models.json").GetProperty("assets");
  foreach(var item in assetMeta.EnumerateObject()){
   var expected=item.Value;var id=Convert.ToUInt32(expected.GetProperty("id").GetString(),16);var asset=_vanillaMod.Statics.SingleOrDefault(s=>s.EditorID==item.Name&&(synthetic||s.FormKey.ID==id))??throw new InvalidDataException("Blackstone exact static missing: "+item.Name);var b=asset.ObjectBounds;var bounds=new[]{(int)b.First.X,b.First.Y,b.First.Z,b.Second.X,b.Second.Y,b.Second.Z};
   if(asset.Model?.File?.ToString()!=expected.GetProperty("model").GetString()||!bounds.SequenceEqual(expected.GetProperty("bounds").EnumerateArray().Select(x=>x.GetInt32())))throw new InvalidDataException("Blackstone model/bounds changed: "+item.Name);
   foreach(var name in new[]{"VirtualMachineAdapter","Destructible"})if(asset.GetType().GetProperty(name)?.GetValue(asset)!=null)throw new InvalidDataException("Blackstone passive donor carries behavior");
  }
  var light=_vanillaMod.Lights.Single(l=>l.FormKey.ID==0x517B0&&l.EditorID=="DefaultLightWhite01NS");if(light.Radius!=256||light.VirtualMachineAdapter!=null)throw new InvalidDataException("Blackstone source light changed");var ownLight=light.Duplicate(keys["TLM_LIGH_BS_NeutralFill"]);ownLight.EditorID="TLM_LIGH_BS_NeutralFill";ownLight.Radius=512;_mod.Lights.Add(ownLight);Track(ownLight);
  var door=_vanillaMod.Doors.Single(d=>d.FormKey.ID==0x52576&&d.EditorID=="ShackDoor01");if(door.VirtualMachineAdapter!=null)throw new InvalidDataException("Blackstone door donor scripted");
  foreach(var name in extra.Where(n=>n.StartsWith("TLM_DOOR_"))){var d=door.Duplicate(keys[name]);d.EditorID=name;d.Name=Blackstone.Pieces.Single(p=>p.Base==name).Name;d.VirtualMachineAdapter=null;_mod.Doors.Add(d);Track(d);}
  var climate=_vanillaMod.Worldspaces.Single(w=>w.EditorID=="Commonwealth").Climate;if(climate.IsNull)throw new InvalidDataException("Blackstone sky climate absent");
  var world=new Worldspace(keys[Blackstone.World],Fallout4Release.Fallout4){EditorID=Blackstone.World,Name="Blackstone Station: upper freight platform",Flags=Worldspace.Flag.SmallWorld|Worldspace.Flag.CannotFastTravel|Worldspace.Flag.NoGrass|Worldspace.Flag.NoLodWater,LandDefaults=new WorldspaceLandDefaults{DefaultLandHeight=0,DefaultWaterHeight=-2048},ObjectBoundsMin=new P2Float(0,0),ObjectBoundsMax=new P2Float(4096,4096)};world.Climate.SetTo(climate.FormKey);_mod.Worldspaces.Add(world);
  world.TopCell=new Cell(keys[Blackstone.Persistent],Fallout4Release.Fallout4){EditorID=Blackstone.Persistent,MajorRecordFlagsRaw=0x400};
  var cell=new Cell(keys[Blackstone.Surface],Fallout4Release.Fallout4){EditorID=Blackstone.Surface,Name="Blackstone Station — open upper platform",Grid=new CellGrid{Point=new P2Int(0,0)},WaterHeight=-2048};var block=new WorldspaceBlock{BlockNumberX=0,BlockNumberY=0,GroupType=GroupTypeEnum.ExteriorCellBlock};var sub=new WorldspaceSubBlock{BlockNumberX=0,BlockNumberY=0,GroupType=GroupTypeEnum.ExteriorCellSubBlock};world.SubCells.Add(block);block.Items.Add(sub);sub.Items.Add(cell);
  var texture=_vanillaMod.LandscapeTextures.Single(t=>t.EditorID=="LDirtGravel01");var land=new Landscape(keys["TLM_LAND_BS_Upper"],Fallout4Release.Fallout4){DATA=new byte[]{0x1D,0,0,0},VertexNormals=new Array2d<P3UInt8>(33,33,new P3UInt8(0,0,127)),VertexHeightMap=new LandscapeVertexHeightMap{Offset=0,HeightMap=new Array2d<byte>(33,33,0)},Textures=new()};foreach(var quadrant in Enum.GetValues<Quadrant>())land.Layers.Add(new BaseLayer{Header=new LayerHeader{Texture=new FormLink<ILandscapeTextureGetter>(texture.FormKey),Quadrant=quadrant,LayerNumber=0}});land.Textures.Add(texture.ToLink<ILandscapeTextureGetter>());cell.Landscape=land;
  foreach(var c in new[]{world.TopCell,cell}){CellsFiled[c.EditorID!]=(0,0);CellNames[c.EditorID!]=c.Name?.String;Arrivals.Add(new(c.EditorID!,c.FormKey.ToString(),new[]{0f,0f,0f},0,true));}
 }
 void CompleteBlackstoneEnvironment(){
  if(_vanillaMod==null)return;var cells=BlackstoneEnvironment.ReportCells(_mod).ToDictionary(c=>c.Cell.EditorID!);var all=cells.Values.SelectMany(c=>c.Cell.Persistent.Concat(c.Cell.Temporary)).ToDictionary(r=>r.EditorID??r.FormKey.ToString());
  var lighting=_vanillaMod.Cells.Records.SelectMany(b=>b.SubBlocks).SelectMany(s=>s.Cells).Single(c=>c.EditorID=="QASmoke");if(lighting.Lighting==null)throw new InvalidDataException("Blackstone complete lighting donor absent");
  foreach(var id in new[]{Blackstone.Service,Blackstone.Lower}){var room=_mod.Cells.Records.SelectMany(b=>b.SubBlocks).SelectMany(s=>s.Cells).Single(c=>c.EditorID==id);room.Lighting=lighting.Lighting.DeepCopy();room.LightingTemplate.SetTo(lighting.LightingTemplate.FormKey);room.ImageSpace.SetTo(lighting.ImageSpace.FormKey);}
  var decor=new List<object>();foreach(var p in Blackstone.Load("layout-placements.json").GetProperty("placements").EnumerateArray()){
   var name=p.GetProperty("symbol").GetString()!;var placed=(PlacedObject)all[name];var rotation=p.GetProperty("rotationRadians").EnumerateArray().Select(n=>n.GetSingle()).ToArray();placed.Rotation=new P3Float(rotation[0],rotation[1],rotation[2]);placed.Scale=p.GetProperty("scale").GetSingle();decor.Add(new{name,key=placed.FormKey.ToString(),rotation,scale=placed.Scale});
  }
  var papers=new List<object>();foreach(var role in new[]{"JunctionRoute","Freight","RiderIndex","MaraNote","ServicePass"}){
   var placed=(PlacedObject)all["TLM_REF_BS_"+role];var book=_mod.Books.Single(b=>b.FormKey==placed.Base.FormKey);var z=56f-book.ObjectBounds.First.Z;var at=placed.Position;placed.Position=new P3Float(at.X,at.Y,z);blackstonePaperHeights[placed.EditorID!]=z;papers.Add(new{role,book=book.EditorID,minZ=book.ObjectBounds.First.Z,placedZ=z,bottom=z+book.ObjectBounds.First.Z,supportZ=56});
  }
  var diagram=(PlacedObject)all["TLM_REF_BS_Diagram"];diagram.Rotation=new P3Float(0,MathF.PI/2,0);
  var lower=(PlacedObject)all["TLM_REF_BS_ServiceDoor"];lower.Lock=new LockData{Level=LockLevel.RequiresKey};
  var mara=_mod.Npcs.Single(n=>n.EditorID=="TLM_NPC_BS_Mara");mara.Flags&=~(Npc.Flag.Essential|Npc.Flag.Protected);
  BlackstoneEnvironmentReceipt=new{inputKind=_vanillaMod.Climates.Any(c=>c.EditorID=="RHSyntheticClimate")?"Synthetic stand-in; never owned/native evidence":"Owned source requires exact native IDs",policy="New single master-owned station only; passive layout literal input, no navmesh/terrain donor/behavior imported",decor,papers,world=Blackstone.World,surface=Blackstone.Surface,land=new{grid="0,0",vertices=1089,height=0,layers=4,normals="0,0,127",support="All upper anchors must remain in [0,4096] and above actual flat height0"},lighting=new{donor=lighting.FormKey.ToString(),fullBlock=true,template=lighting.LightingTemplate.FormKey.ToString(),imageSpace=lighting.ImageSpace.FormKey.ToString(),emitter="TLM_LIGH_BS_NeutralFill",radius=512},diagram=new{key=diagram.FormKey.ToString(),position=new[]{diagram.Position.X,diagram.Position.Y,diagram.Position.Z},rotation=new[]{diagram.Rotation.X,diagram.Rotation.Y,diagram.Rotation.Z},basis="Declared CW Y: local+Z maps world-X; actual render front/hearing/native Havok remain unproved"},mechanicalDoor=new{key=lower.FormKey.ToString(),level=lower.Lock.Level.ToString()},mara=new{essential=mara.Flags.HasFlag(Npc.Flag.Essential),protectedFlag=mara.Flags.HasFlag(Npc.Flag.Protected)},native=(string?)null};
 }
}
