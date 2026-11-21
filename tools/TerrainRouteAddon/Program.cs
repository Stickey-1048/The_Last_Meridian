using Mutagen.Bethesda;
using Mutagen.Bethesda.Fallout4;
using Mutagen.Bethesda.Plugins;
using Mutagen.Bethesda.Plugins.Records;
using Activator = Mutagen.Bethesda.Fallout4.Activator;
using Noggog;
using System.Security.Cryptography;
using System.Text.Json;

// Separate optional addon: explicit four header-only overrides, three own persistent refs.
// Frozen input files are read/locked, never rewritten. No original child groups are emitted.
try {
 if(args.Length!=2){Console.Error.WriteLine("TerrainRouteAddon ABSOLUTE-OWNED-Fallout4.esm NEW-project-build-directory");return 2;}
 using var safe=SafeBuild.Open(args[0],args[1]);
 string workspace=Path.GetFullPath("../../../..",SafeBuild.ProjectRoot);
 string basis=Path.Combine(workspace,"work/rh-return-account-build-f491eeb/build/licensed-return-account-skeleton-001/bundle");
 using var storyLock=LockedInput.Open(Path.Combine(basis,"TheLastMeridian.esp"),"5C22EE73009BF1F6B75CFBD5C5E52A749B2086ABA847521B5B294E3ED66E81FF");
 using var worldLock=LockedInput.Open(Path.Combine(basis,"TLMWorldSlice.esp"),"ACE5F0A233A1E8124555B15812FFC445FF1AB23DAAA4D672FCDEC231C1D93FAF");
 using var terrainLock=LockedInput.Open(Path.Combine(workspace,"work/spectacle-route-landmarks-001/build/landmarks-002/TLMSpectacleTerrainPrototype.esp"),"6EB3A6167DE06353E39660180DE8858DBBBCBDEB793D3C84770BC7739AE6A81C");
 using var vanilla=Fallout4Mod.CreateFromBinaryOverlay(safe.Source,Fallout4Release.Fallout4);
 using var ws=Fallout4Mod.CreateFromBinaryOverlay(worldLock.Path,Fallout4Release.Fallout4);
 using var terrain=Fallout4Mod.CreateFromBinaryOverlay(terrainLock.Path,Fallout4Release.Fallout4);
 var oldWorld=ws.Worldspaces.Single(w=>w.FormKey.ID==0x800&&w.EditorID=="TLM_WS_Meridian");
 var oldTerrain=terrain.Worldspaces.Single(w=>w.FormKey.ID==0x800&&w.EditorID=="TLM_PROBE_WRLD_SpectacleTerrain");
 if(oldWorld.TopCell?.FormKey.ID!=0x801||oldTerrain.TopCell?.FormKey.ID!=0x801)throw new InvalidDataException("Unexpected persistent cell identity");
 var clearing=oldWorld.SubCells.SelectMany(b=>b.Items).SelectMany(s=>s.Items).Single(c=>c.FormKey.ID==0x802&&c.EditorID=="TLM_WS_Clearing");
 var oldArrival=clearing.Temporary.OfType<IPlacedObjectGetter>().Single(r=>r.FormKey.ID==0x804&&r.EditorID=="TLM_WS_Arrival");
 var arrival=oldTerrain.TopCell!.Persistent.OfType<IPlacedObjectGetter>().Single(r=>r.FormKey.ID==0x806&&r.EditorID=="TLM_PROBE_REF_Arrival");
 if(oldArrival.Position!=new P3Float(448,640,32)||oldArrival.Rotation.Z!=MathF.PI/4||oldArrival.MajorRecordFlagsRaw!=0||arrival.Position!=new P3Float(3072,1024,592)||(arrival.MajorRecordFlagsRaw&0x400)==0)throw new InvalidDataException("Reviewed marker pose/persistence changed");
 var clipboard=vanilla.MiscItems.Single(m=>m.FormKey.ID==0x22579F&&m.EditorID=="Clipboard_Prewar01");
 if(clipboard.Model is not {} clipboardModel || clipboardModel.File?.ToString()!=@"Props\Clipboard_Prewar.nif"||clipboard.ObjectBounds.First!=new P3Int16(-8,-11,0)||clipboard.ObjectBounds.Second!=new P3Int16(8,12,1))throw new InvalidDataException("Exact small control model/bounds changed");
 var mod=new Fallout4Mod(ModKey.FromNameAndExtension("TLMOptionalTerrainRoute.esp"),Fallout4Release.Fallout4);mod.ModHeader.Stats.Version=0.95f;
 foreach(var name in new[]{"Fallout4.esm","TLMSpectacleTerrainPrototype.esp","TLMWorldSlice.esp"})mod.ModHeader.MasterReferences.Add(new MasterReference{Master=ModKey.FromNameAndExtension(name)});
 Worldspace HeaderOnly(IWorldspaceGetter original){
  var header=original.DeepCopy();header.SubCells.Clear();
  var cell=original.TopCell!.DeepCopy();cell.Persistent.Clear();cell.Temporary.Clear();cell.NavigationMeshes.Clear();cell.Landscape=null;
  header.TopCell=cell;mod.Worldspaces.Add(header);return header;
 }
 var worldHeader=HeaderOnly(oldWorld);var terrainHeader=HeaderOnly(oldTerrain);
 Activator Control(string id,string name){var a=new Activator(mod.GetNextFormKey(),Fallout4Release.Fallout4){EditorID=id,Name=name,ActivateTextOverride="Use",Model=clipboardModel.DeepCopy(),ObjectBounds=clipboard.ObjectBounds.DeepCopy()};mod.Activators.Add(a);return a;}
 var outbound=Control("TLM_DEV_ACTI_VisitTerrain","[Development] Visit terrain preview");
 var back=Control("TLM_DEV_ACTI_ReturnMeridian","[Development] Return to Meridian preview");
 Message Prompt(string id,string text){var m=new Message(mod.GetNextFormKey(),Fallout4Release.Fallout4){EditorID=id,Name="Optional development travel",Description=text,Flags=Message.Flag.MessageBox};m.MenuButtons.Add(new MessageButton{Text="Travel"});m.MenuButtons.Add(new MessageButton{Text="Stay here"});mod.Messages.Add(m);return m;}
 var go=Prompt("TLM_DEV_MSG_VisitTerrain","Visit the separate two-cell terrain preview? It has no quests or characters. A return control is beside its arrival point.");
 var ret=Prompt("TLM_DEV_MSG_ReturnMeridian","Return to the Meridian road preview?");
 var anchor=new PlacedObject(mod.GetNextFormKey(),Fallout4Release.Fallout4){EditorID="TLM_DEV_REF_MeridianReturnAnchor",Position=oldArrival.Position,Rotation=oldArrival.Rotation,MajorRecordFlagsRaw=0x400};anchor.Base.SetTo(oldArrival.Base.FormKey);worldHeader.TopCell!.Persistent.Add(anchor);
 void AddControl(Worldspace owner,Activator act,string id,P3Float at,FormKey dest,Worldspace destinationWorld,Message prompt,bool outgoing){
  var r=new PlacedObject(mod.GetNextFormKey(),Fallout4Release.Fallout4){EditorID=id,Position=at,Rotation=new P3Float(0,0,0),MajorRecordFlagsRaw=0x400,VirtualMachineAdapter=new VirtualMachineAdapter{Version=6,ObjectFormat=2}};r.Base.SetTo(act.FormKey);
  var script=new ScriptEntry{Name="TLMDev:OptionalTerrainTravel"};
  foreach(var p in new[]{("Prompt",prompt.FormKey),("Destination",dest),("SourceWorld",owner.FormKey),("DestinationWorld",destinationWorld.FormKey)})script.Properties.Add(new ScriptObjectProperty{Name=p.Item1,Flags=ScriptProperty.Flag.Edited,Object=p.Item2.ToLink<IFallout4MajorRecordGetter>(),Alias=-1});
  script.Properties.Add(new ScriptBoolProperty{Name="Outbound",Flags=ScriptProperty.Flag.Edited,Data=outgoing});r.VirtualMachineAdapter.Scripts.Add(script);owner.TopCell!.Persistent.Add(r);
 }
 AddControl(worldHeader,outbound,"TLM_DEV_REF_VisitTerrain",new P3Float(256,512,0),arrival.FormKey,terrainHeader,go,true);
 AddControl(terrainHeader,back,"TLM_DEV_REF_ReturnMeridian",new P3Float(3184,1104,576),anchor.FormKey,worldHeader,ret,false);
 if(mod.Worldspaces.Count!=2||worldHeader.TopCell!.Persistent.Count!=2||terrainHeader.TopCell!.Persistent.Count!=1||mod.Quests.Count!=0||mod.Npcs.Count!=0||mod.Doors.Count!=0)throw new InvalidDataException("Unexpected addon behavior topology");
 using var bytes=new MemoryStream();mod.WriteToBinary(bytes);
 safe.CreateOutput();safe.WriteNew(mod.ModKey.FileName,bytes.ToArray());
 var receipt=new{scope="Source/local serialization only; engine merge, cross-world arrival and activation/native acceptance OPEN",plugin=mod.ModKey.FileName.String,sha256=Convert.ToHexString(SHA256.HashData(bytes.ToArray())),inputWorld=worldLock.Hash,inputTerrain=terrainLock.Hash,inputStory=storyLock.Hash,ownRefs=3,headerOverrides=4,runtime="Scripts/TLMDev/OptionalTerrainTravel.pex; separate compile/install gate",nativeAcceptance=(string?)null};safe.WriteNew("connection-receipt.json",JsonSerializer.SerializeToUtf8Bytes(receipt,new JsonSerializerOptions{WriteIndented=true}));
 Console.WriteLine(JsonSerializer.Serialize(receipt,new JsonSerializerOptions{WriteIndented=true}));return 0;
}catch(Exception error){Console.Error.WriteLine("CONNECTION REFUSED/FAILED; partial output preserved: "+error.Message);return 1;}
