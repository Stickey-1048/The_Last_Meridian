using Mutagen.Bethesda;
using Mutagen.Bethesda.Fallout4;
using Mutagen.Bethesda.Plugins;
using Mutagen.Bethesda.Plugins.Records;
using Noggog;
using System.Text.Json;
using System.Security.Cryptography;
using Activator=Mutagen.Bethesda.Fallout4.Activator;
try{
 if(args.Length!=2){Console.Error.WriteLine("VoiceNativePilot ABSOLUTE-OWNED-Fallout4.esm NEW-project-build-directory");return 2;}
 using var safe=SafeBuild.Open(args[0],args[1]);
 var workspace=Path.GetFullPath("../../../..",SafeBuild.ProjectRoot);
 using var input=LockedInput.Open(Path.Combine(workspace,"work/rh-return-account-build-f491eeb/build/licensed-return-account-skeleton-001/bundle/TheLastMeridian.esp"),"5C22EE73009BF1F6B75CFBD5C5E52A749B2086ABA847521B5B294E3ED66E81FF");
 using var vanilla=Fallout4Mod.CreateFromBinaryOverlay(safe.Source,Fallout4Release.Fallout4);
 using var story=Fallout4Mod.CreateFromBinaryOverlay(input.Path,Fallout4Release.Fallout4);
 var surface=story.Worldspaces.Single(w=>w.FormKey.ID==0xCF7&&w.EditorID=="TLM_WRLD_RH_Surface");
 if(surface.TopCell?.FormKey.ID!=0xCF8)throw new InvalidDataException("Wrong persistent surface");
 var clipboard=vanilla.MiscItems.Single(m=>m.FormKey.ID==0x22579F&&m.EditorID=="Clipboard_Prewar01");
 var mod=new Fallout4Mod(ModKey.FromNameAndExtension("TLMVoiceNativePilot.esp"),Fallout4Release.Fallout4);mod.ModHeader.Stats.Version=0.95f;
 foreach(var name in new[]{"Fallout4.esm","TheLastMeridian.esp"})mod.ModHeader.MasterReferences.Add(new MasterReference{Master=ModKey.FromNameAndExtension(name)});
 var header=surface.DeepCopy();header.SubCells.Clear();header.TopCell!.Persistent.Clear();header.TopCell.Temporary.Clear();header.TopCell.NavigationMeshes.Clear();header.TopCell.Landscape=null;mod.Worldspaces.Add(header);
 var quest=new Quest(mod.GetNextFormKey(),Fallout4Release.Fallout4){EditorID="TLM_DEV_VoicePilot",Name="Optional voice audition",Data=new QuestData{Flags=0,Priority=1,Type=Quest.TypeEnum.None},UnusedConditions=new ExtendedList<Condition>()};mod.Quests.Add(quest);
 var shape=vanilla.Quests.SelectMany(q=>q.DialogTopics).First(t=>t.Subtype==DialogTopic.SubtypeEnum.Custom0&&t.Responses.Any(i=>i.Responses.Count>0));
 var emotion=shape.Responses.First(i=>i.Responses.Count>0).Responses[0].Emotion.FormKey;
 var rows=new List<object>();
 foreach(var row in new[]{(Name:"Blevins",Npc:0xAABu,Ref:0xB22u,Template:0x24A029u,Voice:0x2Du,VoiceName:"MaleRough",Line:"For the good of the Hollow, I'd ask you to stand back from the Mouth.",Fuz:"362C8D54DD5DB5D37C6CB7009BC7D731CE8B8572BC5E00AFCA2548E3173B6283",File:"00000803_1.fuz",Folder:"TLM_VT_Blevins_Pilot"),(Name:"Roark",Npc:0xAACu,Ref:0xB21u,Template:0x24A016u,Voice:0x13ADDu,VoiceName:"FemaleEvenToned",Line:"I'm listening to something. Say it quiet.",Fuz:"F152973FE8F96879A54B9861571208944609C7C537CD7A91534037E525DA29EF",File:"00000806_1.fuz",Folder:"TLM_VT_Roark_Pilot")}){
  var npc=story.Npcs.Single(n=>n.FormKey.ID==row.Npc&&n.EditorID=="TLM_NPC_RH_"+row.Name);
  var original=surface.TopCell!.Persistent.OfType<IPlacedNpcGetter>().Single(r=>r.FormKey.ID==row.Ref&&r.Base.FormKey==npc.FormKey);
  var template=vanilla.Npcs.Single(n=>n.FormKey.ID==row.Template);
  var voice=vanilla.VoiceTypes.Single(v=>v.FormKey.ID==row.Voice&&v.EditorID==row.VoiceName);
  if(((int)npc.UseTemplateActors&1)==0||npc.TemplateActors?.TraitTemplate.FormKey!=template.FormKey||((int)template.UseTemplateActors&1)!=0||template.Voice.FormKey!=voice.FormKey)throw new InvalidDataException("Effective Traits voice changed");
  var topic=new DialogTopic(mod.GetNextFormKey(),Fallout4Release.Fallout4){EditorID="TLM_DEV_Voice_"+row.Name,Category=shape.Category,Subtype=shape.Subtype,SubtypeName=shape.SubtypeName};topic.Quest.SetTo(quest.FormKey);
  var info=new DialogResponses(mod.GetNextFormKey(),Fallout4Release.Fallout4){EditorID="TLM_DEV_Voice_"+row.Name+"_Info",Flags=new DialogResponseFlags()};info.Topic.SetTo(topic.FormKey);info.Speaker.SetTo(npc.FormKey);
  var response=new DialogResponse{ResponseNumber=1,Text=row.Line};response.Emotion.SetTo(emotion);info.Responses.Add(response);topic.Responses.Add(info);quest.DialogTopics.Add(topic);
  Message MakeMessage(string suffix,string body,params string[] buttons){var m=new Message(mod.GetNextFormKey(),Fallout4Release.Fallout4){EditorID="TLM_DEV_Voice_"+row.Name+suffix,Name=row.Name+": optional recorded audition",Description=body,Flags=Message.Flag.MessageBox};foreach(var b in buttons)m.MenuButtons.Add(new MessageButton{Text=b});mod.Messages.Add(m);return m;}
  var prompt=MakeMessage("_Prompt","Audition an original recording with "+row.Name+"? This optional test does not advance the story. The normal conversation remains separate.","Play recording","Read text","Cancel");
  var fallback=MakeMessage("_Text",row.Line+"\n\nOriginal recorded audition text. Audio dispatch does not confirm that it was heard.","Close");
  var act=new Activator(mod.GetNextFormKey(),Fallout4Release.Fallout4){EditorID="TLM_DEV_ACTI_Voice_"+row.Name,Name="[Voice test] "+row.Name,ActivateTextOverride="Audition",Model=clipboard.Model!.DeepCopy(),ObjectBounds=clipboard.ObjectBounds.DeepCopy()};mod.Activators.Add(act);
  var control=new PlacedObject(mod.GetNextFormKey(),Fallout4Release.Fallout4){EditorID="TLM_DEV_REF_Voice_"+row.Name,Position=new P3Float(original.Position.X,original.Position.Y-128,0),Rotation=new P3Float(0,0,0),MajorRecordFlagsRaw=0x400,VirtualMachineAdapter=new VirtualMachineAdapter{Version=6,ObjectFormat=2}};control.Base.SetTo(act.FormKey);
  var script=new ScriptEntry{Name="TLMDev:VoicePilot"};
  foreach(var p in new[]{("OriginalSpeaker",original.FormKey),("ExpectedBase",npc.FormKey),("ExpectedVoice",voice.FormKey),("LineTopic",topic.FormKey),("PilotQuest",quest.FormKey),("Prompt",prompt.FormKey),("TextFallback",fallback.FormKey)})script.Properties.Add(new ScriptObjectProperty{Name=p.Item1,Flags=ScriptProperty.Flag.Edited,Object=p.Item2.ToLink<IFallout4MajorRecordGetter>(),Alias=-1});control.VirtualMachineAdapter.Scripts.Add(script);header.TopCell!.Persistent.Add(control);
  string fuz=Path.Combine(workspace,"work/voice-lip-feasibility-001/fuz-output-001/Sound/Voice/MeridianVoicePathProbe.esp",row.Folder,row.File);
  using var audio=LockedInput.Open(fuz,row.Fuz);var bytes=File.ReadAllBytes(fuz);if(System.Text.Encoding.ASCII.GetString(bytes,0,4)!="FUZE"||BitConverter.ToUInt32(bytes,4)!=1||BitConverter.ToUInt32(bytes,8)==0)throw new InvalidDataException("Invalid reviewed FUZ");
  rows.Add(new{name=row.Name,npc=npc.FormKey.ToString(),original=original.FormKey.ToString(),voice=voice.FormKey.ToString(),voiceName=voice.EditorID,template=template.FormKey.ToString(),topic=topic.FormKey.ToString(),info=info.FormKey.ToString(),subtitle=row.Line,control=control.FormKey.ToString(),position=new[]{control.Position.X,control.Position.Y,control.Position.Z},sourceFuz=fuz,fuzSha256=row.Fuz,relativePath="Sound/Voice/"+mod.ModKey.FileName+"/"+voice.EditorID+"/"+info.FormKey.ID.ToString("X8")+"_1.fuz"});
 }
 using var memory=new MemoryStream();mod.WriteToBinary(memory);safe.CreateOutput();safe.WriteNew(mod.ModKey.FileName,memory.ToArray());
 var receipt=new{scope="Opt-in original actor voice audition; no override/base mutation, story effect, install or native claim",baseHash=input.Hash,pluginSha256=Convert.ToHexString(SHA256.HashData(memory.ToArray())),shape=shape.FormKey.ToString(),shapeCategory=shape.Category.ToString(),shapeSubtype=shape.Subtype.ToString(),quest=quest.FormKey.ToString(),headerOverrides=2,ownControls=2,rows,nativeAcceptance=(string?)null};safe.WriteNew("voice-mapping.json",JsonSerializer.SerializeToUtf8Bytes(receipt,new JsonSerializerOptions{WriteIndented=true}));
 using var read=Fallout4Mod.CreateFromBinaryOverlay(Path.Combine(safe.Output,mod.ModKey.FileName),Fallout4Release.Fallout4);
 if(read.ModHeader.Stats.Version!=0.95f||read.Npcs.Count!=0||read.VoiceTypes.Count!=0||read.Quests.Count!=1||read.Quests.Single().DialogTopics.Count!=2||read.Worldspaces.Single().TopCell!.Persistent.Count!=2)throw new InvalidDataException("Pilot readback topology");
 Console.WriteLine(JsonSerializer.Serialize(receipt,new JsonSerializerOptions{WriteIndented=true}));return 0;
}catch(Exception e){Console.Error.WriteLine("VOICE PILOT FAILED; partial output preserved: "+e);return 1;}


