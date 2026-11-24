using Mutagen.Bethesda;
using Mutagen.Bethesda.Fallout4;
using Mutagen.Bethesda.Plugins;
using Mutagen.Bethesda.Plugins.Records;
using System.Text.Json;
using System.Security.Cryptography;
public static class PrivateRoadVoices
{
 public static bool IsExpectedCaptionOverride(IMajorRecordGetter record)
 {
  if(record.FormKey.ModKey!=ModKey.FromNameAndExtension("TheLastMeridian.esp")||record is not IMessageGetter message)return false;
  string expected=record.FormKey.ID switch{0x849=>"TLM_MSG_A1_DunmoreHold",0x874=>"TLM_MSG_A1_TalbotGate",_=>""};
  if(expected.Length==0||message.EditorID!=expected)return false;
  using var map=JsonDocument.Parse(File.ReadAllText(Path.Combine(AppContext.BaseDirectory,"../../../../PrivateRoadVoices/audio-map.json")));
  var row=map.RootElement.GetProperty("lines").EnumerateArray().Single(r=>r.GetProperty("messageId").GetUInt32()==record.FormKey.ID);
  return message.Description.String==row.GetProperty("speaker").GetString()+": \""+row.GetProperty("text").GetString()+"\"";
 }
 public static object Add(Fallout4Mod mod,IFallout4ModGetter story)
 {
  using var doc=JsonDocument.Parse(File.ReadAllText(Path.Combine(AppContext.BaseDirectory,"../../../../PrivateRoadVoices/audio-map.json")));
  var rows=doc.RootElement.GetProperty("lines").EnumerateArray().ToArray();if(rows.Length!=2)throw new InvalidDataException("Only two private road voice lines");
  var a1=mod.Quests.Single(q=>q.EditorID=="TLM_WS_A1"&&q.FormKey.ID==0x8FD);var walk=a1.VirtualMachineAdapter!.Scripts.Single(s=>s.Name=="TLM:Act1Walk");
  if(walk.Properties.Count!=116)throw new InvalidDataException("Expected current116-property first-section interface");
  var shape=story.SoundDescriptors.Single(s=>s.EditorID=="TLM_SOUND_PritchardDispatch"&&s.FormKey.ID==0xF84);
  if(shape.Category.FormKey!=new FormKey(story.ModKey,0xF6F)||shape.Conditions.Count!=0||shape.Descriptors.Count!=0||shape.SoundFiles.Count!=1||shape.LoopAndRumble?.Loop.ToString()!="None")throw new InvalidDataException("Accepted nonlooping menu-capable sound shape differs");
  void Prop(string name,FormKey key,short alias=-1){if(walk.Properties.Any(p=>p.Name==name))throw new InvalidDataException("Duplicate private voice binding");walk.Properties.Add(new ScriptObjectProperty{Name=name,Flags=ScriptProperty.Flag.Edited,Object=new FormLink<IFallout4MajorRecordGetter>(key),Alias=alias});}
  int i=0;var changes=new List<object>();
  foreach(var row in rows){
   string id=row.GetProperty("id").GetString()!;bool dunmore=i==0;if(id!=(dunmore?"DunmoreHold":"TalbotGate"))throw new InvalidDataException("Unexpected private line order");
   uint actorId=dunmore?0x90Au:0x90Fu;uint alias=dunmore?12u:17u;uint messageId=dunmore?0x849u:0x874u;
   var original=a1.Aliases!.OfType<QuestReferenceAlias>().Single(a=>a.ID==alias&&a.Name==(dunmore?"Dunmore":"Talbot"));if(original.ForcedReference.FormKey!=new FormKey(mod.ModKey,actorId))throw new InvalidDataException("Private voice must use existing original actor");
   string wave=row.GetProperty("waveSource").GetString()!;if(Convert.ToHexString(SHA256.HashData(File.ReadAllBytes(wave)))!=row.GetProperty("waveSha256").GetString())throw new InvalidDataException("Private synthetic clip differs");
   var sound=shape.Duplicate(mod.GetNextFormKey());if(sound.FormKey.ID!=0xB7F+i)throw new InvalidDataException("Sounds must append after accepted B7E");sound.EditorID="TLM_PRIVATE_SOUND_"+id;sound.SoundFiles.Clear();sound.SoundFiles.Add(@"data\"+row.GetProperty("target").GetString()!.Replace('/',(char)92));mod.SoundDescriptors.Add(sound);
   var message=story.Messages.Single(m=>m.FormKey.ID==messageId&&m.EditorID=="TLM_MSG_A1_"+id).Duplicate(new FormKey(story.ModKey,messageId));
   string expected=dunmore?"Reese Dunmore: \"Keep walking. Or stay and pick up a share.\"":"Jonah Talbot: \"Deputy Talbot. Keep your iron holstered inside the posts.\"";
   if(message.Description.String!=expected)throw new InvalidDataException("Original selected caption differs");string caption=row.GetProperty("speaker").GetString()+": \""+row.GetProperty("text").GetString()+"\"";if(caption.Length>240)throw new InvalidDataException("Private caption over budget");message.Description=caption;mod.Messages.Add(message);
   Prop(row.GetProperty("soundProperty").GetString()!,sound.FormKey);Prop(row.GetProperty("originalProperty").GetString()!,original.ForcedReference.FormKey);
   if(!dunmore)Prop("Alias_Talbot",a1.FormKey,17);
   changes.Add(new{id,sound=sound.FormKey.ToString(),message=message.FormKey.ToString(),actor=original.ForcedReference.FormKey.ToString(),alias,path=sound.SoundFiles.Single(),caption,seconds=row.GetProperty("duration").GetDouble()});i++;
  }
  if(walk.Properties.Count!=121)throw new InvalidDataException("Expected only five optional private voice properties");
  return new{scope="PRIVATE two fictional recordings only; ASR/word-fidelity/acting/native hearing unapproved",masterUnchanged=true,changes};
 }
}
