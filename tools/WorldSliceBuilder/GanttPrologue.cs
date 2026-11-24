using Mutagen.Bethesda;
using Mutagen.Bethesda.Fallout4;
using Mutagen.Bethesda.Plugins;
using Noggog;
using System.Text.Json;
using System.Security.Cryptography;

public static class GanttPrologue
{
 public static object NormalizeNewArtifactHeader(string path)
 {
  // Only the newly written prologue artifact. Local0.53.1 counter adds empty quest dialog groups.
  // Do not repair historical inputs. Count actual serialized major records +GRUP, excluding TES4.
  byte[] b=File.ReadAllBytes(path);string before=Convert.ToHexString(SHA256.HashData(b));int major=0,groups=0;
  void Walk(int at,int end){while(at<end){if(at+24>end)throw new InvalidDataException("Truncated new plugin header");int n=checked((int)BitConverter.ToUInt32(b,at+4));bool group=b.AsSpan(at,4).SequenceEqual("GRUP"u8);if(group){if(n<24||at+n>end)throw new InvalidDataException("Invalid new group");groups++;Walk(at+24,at+n);at+=n;}else{if(at+24+n>end)throw new InvalidDataException("Invalid new record");major++;at+=24+n;}}if(at!=end)throw new InvalidDataException("Unconsumed new records");}
  Walk(0,b.Length);if(!b.AsSpan(0,4).SequenceEqual("TES4"u8))throw new InvalidDataException("Missing new TES4");
  int end=24+checked((int)BitConverter.ToUInt32(b,4)),p=24,countAt=-1;
  while(p<end){int n=BitConverter.ToUInt16(b,p+4);if(b.AsSpan(p,4).SequenceEqual("HEDR"u8)){if(n!=12||countAt!=-1)throw new InvalidDataException("Unexpected new HEDR");countAt=p+6+4;}p+=6+n;}
  if(p!=end||countAt<0)throw new InvalidDataException("Missing new HEDR");uint emitted=BitConverter.ToUInt32(b,countAt),normalized=checked((uint)(major-1+groups));byte[] old=b.AsSpan(countAt,4).ToArray();
  BitConverter.GetBytes(normalized).CopyTo(b,countAt);File.WriteAllBytes(path,b);
  return new{scope="NewartifactHEDRNumRecordsonly; historicalbaselineuntouched",beforeSha256=before,afterSha256=Convert.ToHexString(SHA256.HashData(b)),emitted,normalized,majorIncludingTES4=major,groups,countByteOffset=countAt,beforeBytes=Convert.ToHexString(old),afterBytes=Convert.ToHexString(b.AsSpan(countAt,4))};
 }
 public static bool IsOwnCarriage(IFallout4ModGetter addon,ICellGetter cell)
 {
  if(cell.FormKey.ModKey!=addon.ModKey||cell.FormKey.ID!=0xB46||cell.EditorID!="TLM_PROLOGUE_Carriage"||cell.Flags!=Cell.Flag.IsInteriorCell||cell.Landscape!=null||cell.NavigationMeshes.Count!=0)return false;
  var q=addon.Quests.SingleOrDefault(q=>q.EditorID=="TLM_OpeningPrologue"&&q.FormKey.ID==0xB58);
  var script=q?.VirtualMachineAdapter?.Scripts.SingleOrDefault(s=>s.Name=="TLM:OpeningPrologue");
  var prop=script?.Properties.OfType<IScriptObjectPropertyGetter>().SingleOrDefault(p=>p.Name=="CarriageCell");
  return prop!=null&&prop.Alias==-1&&prop.Object.FormKey==cell.FormKey;
 }
 public static int CheckCellGuard(string path,string damage)
 {
  var mod=Fallout4Mod.CreateFromBinary(path,Fallout4Release.Fallout4);
  if(damage=="extra-cell"||damage=="fair-cell"){
   var sub=mod.Cells.Records.Single().SubBlocks.Single();var copy=sub.Cells.Single().Duplicate(mod.GetNextFormKey());copy.EditorID=damage=="fair-cell"?"TLM_CELL_FourFlags":"TLM_UNEXPECTED_Interior";sub.Cells.Add(copy);
  }else if(damage=="wrong-carriage-id")mod.Cells.Records.Single().SubBlocks.Single().Cells.Single().EditorID="TLM_UNEXPECTED_Interior";
  else if(damage!="none")throw new InvalidDataException("Unknown finite prologue guard fixture");
  try{WorldStory.ValidatePrologueInteriorExclusion(mod);if(damage!="none")throw new InvalidDataException("Unexpected interior was accepted");Console.WriteLine("PASS exact own prologue carriage; original fair protections retained");return 0;}
  catch(InvalidDataException e)when(damage!="none"&&e.Message.StartsWith("Fair master/cell")){Console.WriteLine("REFUSED "+damage+": "+e.Message);return 0;}
 }
 public static object Add(IFallout4ModGetter native,Fallout4Mod mod,Worldspace world,Cell wreck,IFallout4ModGetter story)
 {
  // Tail only: never edit original exterior actors, entry, terrain or quest bindings.
  var marshal=world.TopCell!.Persistent.OfType<PlacedNpc>().Single(r=>r.EditorID=="TLM_WS_ST_Marshal"&&r.FormKey.ID==0x8FE);
  var arrival=world.TopCell.Persistent.Concat(wreck.Persistent).Concat(wreck.Temporary).OfType<PlacedObject>().Single(r=>r.EditorID=="TLM_WS_Arrival"&&r.FormKey.ID==0x804);
  if(marshal.Base.FormKey!=new FormKey(story.ModKey,0x840)||marshal.Position!=new P3Float(700,1050,-192))throw new InvalidDataException("Current original Gantt differs");
  var lightRoom=native.Cells.Records.SelectMany(b=>b.SubBlocks).SelectMany(b=>b.Cells).Single(c=>c.EditorID=="QASmoke"&&c.FormKey.ID==0x1F7A9);
  if(lightRoom.Lighting==null||lightRoom.LightingTemplate.FormKey.ID!=0x300E2||lightRoom.ImageSpace.FormKey.ID!=0x16C4)throw new InvalidDataException("Verified readable interior lighting donor differs");
  var cell=new Cell(mod.GetNextFormKey(),Fallout4Release.Fallout4){EditorID="TLM_PROLOGUE_Carriage",Name="Freight carriage",Flags=Cell.Flag.IsInteriorCell,Lighting=lightRoom.Lighting.DeepCopy()};
  cell.LightingTemplate.SetTo(lightRoom.LightingTemplate.FormKey);cell.ImageSpace.SetTo(lightRoom.ImageSpace.FormKey);
  var block=new CellBlock{BlockNumber=(int)(cell.FormKey.ID%10),GroupType=GroupTypeEnum.InteriorCellBlock};var sub=new CellSubBlock{BlockNumber=(int)(cell.FormKey.ID/10%10),GroupType=GroupTypeEnum.InteriorCellSubBlock};block.SubBlocks.Add(sub);sub.Cells.Add(cell);mod.Cells.Records.Add(block);
  var placements=new List<object>();
  IStaticGetter Stat(uint id,string name,string model){var s=native.Statics.Single(s=>s.FormKey.ID==id&&s.EditorID==name);if(s.Model?.File?.ToString()!=model||s.VirtualMachineAdapter!=null)throw new InvalidDataException("Verified carriage static donor differs: "+name);return s;}
  var hull=Stat(0x5CA0B,"RRBoxcar01",@"SetDressing\Railroad\RRBoxcar01.nif");
  var door=Stat(0x8EB6E,"RRBoxcarDoor01Static",@"SetDressing\Railroad\RRBoxcarDoor01.nif");
  var crate=Stat(0x211F7,"WoodCrate03",@"SetDressing\ConcMuseum\WoodCrate03.nif");
  var lantern=Stat(0x1D2C7,"Lantern01",@"SetDressing\LightFixtures\Lantern01.nif");
  var bench=Stat(0xD8F8C,"NPCBenchParkSit01Static",@"Furniture\ParkBench01.nif");
  PlacedObject Put(string edid,FormKey key,P3Float p,float yaw=0,bool persistent=false){var r=new PlacedObject(mod.GetNextFormKey(),Fallout4Release.Fallout4){EditorID=edid,Position=p,Rotation=new P3Float(0,0,yaw)};r.Base.SetTo(key);if(persistent){r.MajorRecordFlagsRaw|=0x400;cell.Persistent.Add(r);}else cell.Temporary.Add(r);placements.Add(new{edid,form=r.FormKey.ToString(),@base=key.ToString(),xyz=new[]{p.X,p.Y,p.Z},yaw,persistent});return r;}
  // Actual full-parent rendered floor is81.125 above native pivot, not OBNDminZ.
  Put("TLM_PROLOGUE_Hull",hull.FormKey,new P3Float(0,0,-81.125f));
  Put("TLM_PROLOGUE_ClosedSideDoor",door.FormKey,new P3Float(0,0,-81.125f),MathF.PI);
  Put("TLM_PROLOGUE_CargoBraceA",crate.FormKey,new P3Float(60,-320,0));
  Put("TLM_PROLOGUE_CargoBraceB",crate.FormKey,new P3Float(-60,-430,0));
  Put("TLM_PROLOGUE_CargoLantern",lantern.FormKey,new P3Float(-60,-430,29));
  Put("TLM_PROLOGUE_CarriageBench",bench.FormKey,new P3Float(0,400,0));
  var warm=native.Lights.Single(l=>l.FormKey.ID==0x560DC&&l.EditorID=="defaultLightWarm01NS");if(warm.Radius!=256||warm.VirtualMachineAdapter!=null)throw new InvalidDataException("Stock warm-light donor differs");
  Put("TLM_PROLOGUE_WarmWorkLight",warm.FormKey,new P3Float(0,-210,160));Put("TLM_PROLOGUE_WarmGanttLight",warm.FormKey,new P3Float(0,20,160));Put("TLM_PROLOGUE_LanternLight",warm.FormKey,new P3Float(-60,-430,90));
  var tool=native.Containers.Single(c=>c.FormKey.ID==0x1930B&&c.EditorID=="Vault111_Prewar_ToolBox_Empty");if(tool.Model?.File?.ToString()!=@"SetDressing\Toolbox\Toolbox.nif")throw new InvalidDataException("Native tool-case model differs");
  var caseBase=mod.Activators.AddNew("TLM_PROLOGUE_ACTI_ToolCase");caseBase.Name="Tool case";caseBase.ActivateTextOverride="Secure";caseBase.Model=new Model{File=tool.Model!.File};caseBase.ObjectBounds=tool.ObjectBounds.DeepCopy();
  var departureBase=mod.Activators.AddNew("TLM_PROLOGUE_ACTI_DepartureDoor");departureBase.Name="Carriage door";departureBase.ActivateTextOverride="Continue journey";departureBase.Model=door.Model!.DeepCopy();departureBase.ObjectBounds=door.ObjectBounds.DeepCopy();
  var toolRef=Put("TLM_PROLOGUE_ToolCase",caseBase.FormKey,new P3Float(0,-40,0),0,true);
  var departure=Put("TLM_PROLOGUE_DepartureControl",departureBase.FormKey,new P3Float(0,0,-81.125f),0,true);
  var marker=native.Statics.Single(s=>s.FormKey.ID==0x3B&&s.EditorID=="XMarker");
  var sceneArrival=Put("TLM_PROLOGUE_Arrival",arrival.Base.FormKey,new P3Float(0,-200,16),0,true);
  var sceneMarshal=Put("TLM_PROLOGUE_MarshalMarker",marker.FormKey,new P3Float(0,100,16),MathF.PI,true);
  var secured=Put("TLM_PROLOGUE_ToolCaseSecuredMarker",marker.FormKey,new P3Float(60,-410,0),0,true);
  var wreckMarshal=new PlacedObject(mod.GetNextFormKey(),Fallout4Release.Fallout4){EditorID="TLM_PROLOGUE_WreckMarshalMarker",Position=marshal.Position,Rotation=marshal.Rotation,MajorRecordFlagsRaw=0x400};wreckMarshal.Base.SetTo(marker.FormKey);world.TopCell.Persistent.Add(wreckMarshal);
  var quest=mod.Quests.AddNew("TLM_OpeningPrologue");quest.Name="An extra pair of hands";quest.Data=new QuestData{Flags=Quest.Flag.RunOnce|Quest.Flag.WarnOnAliasFillFailure,Priority=40,Type=Quest.TypeEnum.None};quest.UnusedConditions=new ExtendedList<Condition>();quest.Aliases=new ExtendedList<AQuestAlias>();
  var adapter=new QuestAdapter();quest.VirtualMachineAdapter=adapter;var script=new ScriptEntry{Name="TLM:OpeningPrologue"};adapter.Scripts.Add(script);
  void Prop(string name,FormKey key)=>script.Properties.Add(new ScriptObjectProperty{Name=name,Flags=ScriptProperty.Flag.Edited,Object=new FormLink<IFallout4MajorRecordGetter>(key),Alias=-1});
  foreach(var item in new[]{("Preview",story.Quests.Single(q=>q.EditorID=="TLM_A1").FormKey),("MainQuest",story.Quests.Single(q=>q.EditorID=="TLM_MQ01").FormKey),("SideQuest",story.Quests.Single(q=>q.EditorID=="TLM_SQ01").FormKey),("Section",mod.Quests.Single(q=>q.EditorID=="TLM_WS_A1").FormKey),("WreckEntry",mod.Quests.Single(q=>q.EditorID=="TLM_WS_Entry").FormKey),("CarriageCell",cell.FormKey),("WreckCell",wreck.FormKey),("WreckWorld",world.FormKey),("OriginalMarshal",marshal.FormKey),("SceneArrival",sceneArrival.FormKey),("SceneMarshalMarker",sceneMarshal.FormKey),("ToolCase",toolRef.FormKey),("ToolCaseSecuredMarker",secured.FormKey),("DepartureControl",departure.FormKey),("WreckMarshalMarker",wreckMarshal.FormKey),("WreckArrival",arrival.FormKey)})Prop(item.Item1,item.Item2);
  var dialoguePath=Path.Combine(AppContext.BaseDirectory,"../../../../GanttPrologue/dialogue.json");var bytes=File.ReadAllBytes(dialoguePath);if(Convert.ToHexString(SHA256.HashData(bytes))!="B6D14D09CC926040E24CB5E4883AEC37C4BBD5988DE0EDC80CA7F4BCF77DA12B")throw new InvalidDataException("Approved prologue copy differs");
  using var copy=JsonDocument.Parse(bytes);foreach(var row in copy.RootElement.GetProperty("messages").EnumerateArray()){string name=row.GetProperty("property").GetString()!;var msg=mod.Messages.AddNew("TLM_PROLOGUE_MSG_"+name);msg.Description=row.GetProperty("text").GetString()!;msg.Flags=Message.Flag.MessageBox;foreach(var b in row.GetProperty("buttons").EnumerateArray())msg.MenuButtons.Add(new MessageButton{Text=b.GetString()!});Prop(name,msg.FormKey);}
  foreach(var item in new[]{(Name:"ToolCase",Id:0,Ref:toolRef.FormKey,Role:1),(Name:"Gantt",Id:1,Ref:marshal.FormKey,Role:2),(Name:"Departure",Id:2,Ref:departure.FormKey,Role:3)}){
   var a=new QuestReferenceAlias{ID=(uint)item.Id,Name=item.Name,Flags=AQuestAlias.Flag.Optional|AQuestAlias.Flag.AllowDisabled|(item.Name=="Gantt"?AQuestAlias.Flag.AllowDead:0)};a.ForcedReference.SetTo(item.Ref);quest.Aliases.Add(a);
   var bind=new QuestFragmentAlias{Property=new ScriptObjectProperty{Object=quest.ToLink<IFallout4MajorRecordGetter>(),Alias=(short)item.Id}};var handler=new ScriptEntry{Name="TLM:OpeningPrologueInteract"};handler.Properties.Add(new ScriptIntProperty{Name="Role",Flags=ScriptProperty.Flag.Edited,Data=item.Role});bind.Scripts.Add(handler);adapter.Aliases.Add(bind);
  }
  foreach(var o in new[]{(10,"Secure the tool case behind the brace",0),(20,"Speak to Rail Marshal Gantt",1),(30,"Continue the journey",2)}){var objective=new QuestObjective{Index=(ushort)o.Item1,Flags=default,DisplayText=o.Item2};objective.Targets.Add(new QuestObjectiveTarget{AliasID=o.Item3});quest.Objectives.Add(objective);}
  return new{cell=cell.FormKey.ToString(),quest=quest.FormKey.ToString(),originalMarshal=marshal.FormKey.ToString(),wreckMarshalMarker=wreckMarshal.FormKey.ToString(),approvedCopySha256=Convert.ToHexString(SHA256.HashData(bytes)),placements,policy="Static enclosed carriage, no newactor/dispatch/oldentry change, new27properties/3aliases; no native collision or movingtrain proof"};
 }
}
