using Mutagen.Bethesda;
using Mutagen.Bethesda.Fallout4;
using Mutagen.Bethesda.Plugins;
namespace Tlm.PluginBuilder;
public sealed partial class Builder
{
    void BuildAdaBookRecording()
    {
        var key = _mod.GetNextFormKey("TLM_SOUND_PikeBook");
        if (key.ID != 3977) throw new InvalidDataException("Ada book sound must append after mechanic outfit3976");
        if (_vanilla == null) { Pending.Add("Ada book recording requires owned sound descriptor metadata"); return; }
        // Exact already-tested nonlooping WAV shape and non-menu-paused category.
        var shape = _mod.SoundDescriptors.Single(s => s.EditorID == "TLM_SOUND_PritchardDispatch");
        var sound = shape.Duplicate(key);
        sound.EditorID = "TLM_SOUND_PikeBook";
        sound.SoundFiles.Clear();
        sound.SoundFiles.Add(@"data\Sound\FX\MeridianRecordings\ada_pikebook.wav");
        _mod.SoundDescriptors.Add(sound); Track(sound);
        var script = ((Quest)Local(Act1.QuestId)).VirtualMachineAdapter!.Scripts.Single(s => s.Name == "TLM:Act1Walk");
        script.Properties.Add(new ScriptObjectProperty { Name = "RecordedPikeBook", Flags = ScriptProperty.Flag.Edited,
            Object = new FormLink<IFallout4MajorRecordGetter>(sound.FormKey), Alias = -1 });
    }
}
