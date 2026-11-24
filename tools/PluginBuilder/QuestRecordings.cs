using Mutagen.Bethesda;
using Mutagen.Bethesda.Fallout4;
using Mutagen.Bethesda.Plugins;
namespace Tlm.PluginBuilder;
public sealed partial class Builder
{
    void BuildQuestRecordings()
    {
        // No actor voice override, dialogue ownership or story state is changed.
        // Allocate stable named IDs even in skeleton mode; absent audio stays optional.
        var categoryKey = _mod.GetNextFormKey("TLM_AUDIO_QuestRecordings");
        var lines = new[]{
            (Id:"PritchardFriend",Quest:BlackLedger.QuestId,Script:"TLM:BlackLedgerWalk",Property:"RecordedFriendAnswer",File:"pritchard_friend_answer"),
            (Id:"PritchardWarrant",Quest:BlackLedger.QuestId,Script:"TLM:BlackLedgerWalk",Property:"RecordedWarrantNext",File:"pritchard_warrant_next"),
            (Id:"RoarkAll",Quest:RedHollow.StageId,Script:"TLM:RedHollowWalk",Property:"RecordedRoarkAll",File:"roark_all_here"),
            (Id:"RoarkOpen",Quest:RedHollow.StageId,Script:"TLM:RedHollowWalk",Property:"RecordedRoarkOpen",File:"roark_rescue_only"),
            (Id:"SheriffWarning",Quest:Act1.QuestId,Script:"TLM:Act1Walk",Property:"RecordedSheriffWarning",File:"sheriff_warning"),
            (Id:"MineKnocks",Quest:RedHollow.StageId,Script:"TLM:RedHollowWalk",Property:"MineMouthKnocks",File:"mine_mouth_knocks"),
            (Id:"PritchardDispatch",Quest:Act1.QuestId,Script:"TLM:Act1Walk",Property:"RecordedDispatchCase",File:"pritchard_dispatch_case"),
            (Id:"PritchardRoads",Quest:Act1.QuestId,Script:"TLM:Act1Walk",Property:"RecordedRoadHandOff",File:"pritchard_three_roads"),
            (Id:"PritchardMineReport",Quest:RedHollow.StageId,Script:"TLM:RedHollowWalk",Property:"RecordedMineReport",File:"pritchard_mine_report")};
        var keys=lines.Select(x=>_mod.GetNextFormKey("TLM_SOUND_"+x.Id)).ToArray();
        if (_vanilla == null) { Pending.Add("Quest recordings require owned native sound descriptor/category metadata"); return; }
        var shape=_vanillaMod!.SoundDescriptors.Single(s=>s.FormKey.ID==0x1643CA && s.EditorID=="XXXTestDialogueETravis");
        var sourceCategory=_vanillaMod.SoundCategories.Single(c=>c.FormKey.ID==0x876BB && c.EditorID=="AudioCategoryVOC");
        var parent=_vanillaMod.SoundCategories.Single(c=>c.FormKey.ID==0x64451 && c.EditorID=="AudioCategoryUI");
        if (shape.Conditions.Count!=0 || shape.SoundFiles.Count!=1 || shape.Descriptors.Count!=0 || shape.LoopAndRumble?.Loop.ToString()!="None")
            throw new InvalidDataException("Known single nonlooping dialogue sound shape changed");
        if (parent.Flags!=0) throw new InvalidDataException("Recorded speech parent became menu-paused");
        var category=sourceCategory.Duplicate(categoryKey);category.EditorID="TLM_AUDIO_QuestRecordings";
        category.Parent.SetTo(parent.FormKey);category.Flags=0; // Captions are MessageBoxes; vanilla VOC pauses immediately there.
        _mod.SoundCategories.Add(category);Track(category);
        for(int i=0;i<lines.Length;i++)
        {
            var line=lines[i];var sound=shape.Duplicate(keys[i]);sound.EditorID="TLM_SOUND_"+line.Id;
            sound.SoundFiles.Clear();sound.SoundFiles.Add(@"data\Sound\FX\MeridianRecordings\"+line.File+".wav");
            sound.Category.SetTo(category.FormKey);_mod.SoundDescriptors.Add(sound);Track(sound);
            var quest=(Quest)Local(line.Quest);var script=quest.VirtualMachineAdapter!.Scripts.Single(s=>s.Name==line.Script);
            script.Properties.Add(new ScriptObjectProperty{Name=line.Property,Flags=ScriptProperty.Flag.Edited,Object=new FormLink<IFallout4MajorRecordGetter>(sound.FormKey),Alias=-1});
        }
    }
}
