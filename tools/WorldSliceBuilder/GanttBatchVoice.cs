using Mutagen.Bethesda;
using Mutagen.Bethesda.Fallout4;
using Mutagen.Bethesda.Plugins;
using System.Text.Json;
using System.Security.Cryptography;
public static class GanttBatchVoice
{
 public static object Add(Fallout4Mod mod)
 {
  byte[] bytes=File.ReadAllBytes(Path.Combine(AppContext.BaseDirectory,"../../../../GanttBatchVoice/audio-map.json"));
  if(Convert.ToHexString(SHA256.HashData(bytes))!="794244B9F19CB8E43CF671B23E628A745FED482E89B3421C07AD3D0F9C395A60")throw new InvalidDataException("Eligible Gantt batch map differs");
  using var doc=JsonDocument.Parse(bytes);var quest=mod.Quests.Single(q=>q.FormKey.ID==0xB58&&q.EditorID=="TLM_OpeningPrologue");
  var script=quest.VirtualMachineAdapter!.Scripts.Single(s=>s.Name=="TLM:OpeningPrologue");
  if(script.Properties.Count!=28)throw new InvalidDataException("Expected existing28-property prologue");
  var shape=mod.SoundDescriptors.Single(s=>s.FormKey.ID==0xB64&&s.EditorID=="TLM_PROLOGUE_SOUND_GanttMotive");
  if(shape.SoundFiles.Single()!=@"data\Sound\FX\MeridianRecordings\gantt_motive.wav"||shape.Category.FormKey.ID!=0xF6F||shape.Category.FormKey.ModKey==mod.ModKey||shape.Conditions.Count!=0||shape.Descriptors.Count!=0||shape.LoopAndRumble?.Loop.ToString()!="None")throw new InvalidDataException("Native-tested nonlooping motive sound shape differs");
  string[] names={"RecordedGanttWork","RecordedGanttRequest","RecordedGanttAccept"};int i=0;var added=new List<object>();
  foreach(var row in doc.RootElement.GetProperty("lines").EnumerateArray()){
   string name=row.GetProperty("property").GetString()!;if(i>=3||name!=names[i]||script.Properties.Any(p=>p.Name==name))throw new InvalidDataException("Only three exact optional audio names allowed");
   var sound=shape.Duplicate(mod.GetNextFormKey());if(sound.FormKey.ID!=0xB75+i)throw new InvalidDataException("Batch sounds must append after inquiry B74");
   sound.EditorID="TLM_PROLOGUE_SOUND_"+name;string path=row.GetProperty("descriptorPath").GetString()!;sound.SoundFiles.Clear();sound.SoundFiles.Add(path);mod.SoundDescriptors.Add(sound);
   script.Properties.Add(new ScriptObjectProperty{Name=name,Flags=ScriptProperty.Flag.Edited,Object=new FormLink<IFallout4MajorRecordGetter>(sound.FormKey),Alias=-1});
   added.Add(new{name,form=sound.FormKey.ToString(),path,durationSeconds=row.GetProperty("durationSeconds").GetDouble()});i++;
  }
  if(i!=3||script.Properties.Count!=31)throw new InvalidDataException("Expected31-property prologue after three optional sounds");
  return new{scope="Three private eligible recordings only; caption/actor/inquiry/room/master unchanged; native/listening pending",added};
 }
}
