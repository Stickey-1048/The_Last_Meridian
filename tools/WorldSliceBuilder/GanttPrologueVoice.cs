using Mutagen.Bethesda;
using Mutagen.Bethesda.Fallout4;
using Mutagen.Bethesda.Plugins;
public static class GanttPrologueVoice
{
 public static object Add(Fallout4Mod mod,IFallout4ModGetter story)
 {
  var quest=mod.Quests.Single(q=>q.EditorID=="TLM_OpeningPrologue"&&q.FormKey.ID==0xB58);
  var script=quest.VirtualMachineAdapter!.Scripts.Single(s=>s.Name=="TLM:OpeningPrologue");
  if(script.Properties.Count!=27||script.Properties.Any(p=>p.Name=="RecordedGanttMotive"))throw new InvalidDataException("Expected exact unvoiced prologue interface");
  var shape=story.SoundDescriptors.Single(s=>s.EditorID=="TLM_SOUND_PritchardDispatch"&&s.FormKey.ID==0xF84);
  if(shape.Category.FormKey!=new FormKey(story.ModKey,0xF6F)||shape.SoundFiles.Count!=1||shape.Conditions.Count!=0||shape.Descriptors.Count!=0||shape.LoopAndRumble?.Loop.ToString()!="None")throw new InvalidDataException("Accepted nonlooping speaker sound shape differs");
  var sound=shape.Duplicate(mod.GetNextFormKey());if(sound.FormKey.ID!=0xB64)throw new InvalidDataException("Voice must append after original prologue B63");
  sound.EditorID="TLM_PROLOGUE_SOUND_GanttMotive";sound.SoundFiles.Clear();sound.SoundFiles.Add(@"data\Sound\FX\MeridianRecordings\gantt_motive.wav");mod.SoundDescriptors.Add(sound);
  script.Properties.Add(new ScriptObjectProperty{Name="RecordedGanttMotive",Flags=ScriptProperty.Flag.Edited,Object=new FormLink<IFallout4MajorRecordGetter>(sound.FormKey),Alias=-1});
  return new{scope="PRIVATE original synthetic motive recording only; acting/accent/You-versusYoure/nativehearingunapproved",sound=sound.FormKey.ToString(),property="RecordedGanttMotive",shape=shape.FormKey.ToString(),category=sound.Category.FormKey.ToString(),path=sound.SoundFiles.Single(),duration=5.28};
 }
}
