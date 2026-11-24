using Mutagen.Bethesda;
using Mutagen.Bethesda.Fallout4;
using Mutagen.Bethesda.Plugins;
using Mutagen.Bethesda.Plugins.Records;
using Noggog;
using Tlm.PluginBuilder;

// Synthetic typed lookup fixtures only. Paths/bounds are declared producer
// contracts, not asset bytes, mesh geometry, usable game data or native evidence.
public static class CurrentProducerFixture
{
    public static readonly string[] Variants = {"plain-trigger-bounds", "current-no-static", "current-wrong-static-type", "current-static-model", "current-static-collision", "current-no-sound", "current-sound-shape"};
    public static readonly string[] AbsenceVariants = {"unnamed-player", "wrong-player", "quest-evidence", "weak-evidence"};
    public static string PlayerVariant(string variant) => AbsenceVariants.SingleOrDefault(v=>variant==v+"-with-lighting") ?? variant;
    public static void Add(Fallout4Mod mod, string variant)
    {
        FormKey Key(uint id) => new(mod.ModKey,id);
        bool preserveAbsence=AbsenceVariants.Contains(variant);
        foreach (var entry in Blackstone.Load("layout-models.json").GetProperty("assets").EnumerateObject())
        {
            var data=entry.Value;var bounds=data.GetProperty("bounds").EnumerateArray().Select(x=>x.GetInt16()).ToArray();
            var item=mod.Statics.SingleOrDefault(s=>s.EditorID==entry.Name)??mod.Statics.AddNew(entry.Name);
            item.Model=new Model{File=data.GetProperty("model").GetString()!};
            item.ObjectBounds.First=new P3Int16(bounds[0],bounds[1],bounds[2]);item.ObjectBounds.Second=new P3Int16(bounds[3],bounds[4],bounds[5]);
        }
        var light=new Light(Key(0x517B0),Fallout4Release.Fallout4){EditorID="DefaultLightWhite01NS",Radius=256};mod.Lights.Add(light);
        // The metadata table also names this desk; rekey its synthetic record
        // for the stricter access-support consumer, never create an EDID collision.
        foreach(var prior in mod.Statics.Where(s=>s.EditorID==RedHollowAccess.Desk).ToArray())mod.Statics.Remove(prior.FormKey);
        var desk=new Static(Key(0x1A6E6A),Fallout4Release.Fallout4){EditorID=RedHollowAccess.Desk,Model=new Model{File=@"SetDressing\HighTech\HighTechTable01_Main.nif"}};
        desk.ObjectBounds.First=new P3Int16(-54,-26,0);desk.ObjectBounds.Second=new P3Int16(55,26,56);mod.Statics.Add(desk);
        mod.Doors.Add(new Door(Key(0x52576),Fallout4Release.Fallout4){EditorID="ShackDoor01",Model=new Model{File=@"Synthetic\Door.nif"}});
        if(!preserveAbsence && !mod.Cells.Records.SelectMany(b=>b.SubBlocks).SelectMany(s=>s.Cells).Any(c=>c.EditorID=="QASmoke"))
        {
            // Explicit *-with-lighting variants supply this independent donor.
            // Original low-ID absence variants never acquire a test room.
            var room=new Cell(mod.GetNextFormKey(),Fallout4Release.Fallout4){EditorID="QASmoke"};
            var block=new CellBlock{BlockNumber=(int)(room.FormKey.ID%10),GroupType=GroupTypeEnum.InteriorCellBlock};
            var sub=new CellSubBlock{BlockNumber=(int)(room.FormKey.ID/10%10),GroupType=GroupTypeEnum.InteriorCellSubBlock};
            sub.Cells.Add(room);block.SubBlocks.Add(sub);mod.Cells.Records.Add(block);
        }
        foreach(var cell in mod.Cells.Records.SelectMany(b=>b.SubBlocks).SelectMany(s=>s.Cells).Where(c=>c.EditorID=="QASmoke"))
            cell.Lighting=new CellLighting{FogFar=10000};
        var race=new Race(Key(0x13746),Fallout4Release.Fallout4){EditorID="SyntheticHumanRace"};mod.Races.Add(race);
        var voice=new VoiceType(Key(0x23323),Fallout4Release.Fallout4){EditorID="MaleBoston"};mod.VoiceTypes.Add(voice);
        var finch=new Npc(Key(0x3F23D),Fallout4Release.Fallout4){EditorID="AbrahamFinch"};finch.Race.SetTo(race);mod.Npcs.Add(finch);
        var nativeOutfit=new Outfit(Key(0x1C269A),Fallout4Release.Fallout4){EditorID="SyntheticWastelanderOutfit"};mod.Outfits.Add(nativeOutfit);
        if(!preserveAbsence && !mod.Npcs.Any(n=>n.EditorID=="WorkshopNPC"))
        {
            // Explicit lighting-positive variants also declare their independent
            // current opening donors; original absence inputs keep no settler.
            var male=new Npc(Key(0x113340),Fallout4Release.Fallout4){EditorID="StandInSettlerMale01"};mod.Npcs.Add(male);
            var female=new Npc(Key(0x113346),Fallout4Release.Fallout4){EditorID="StandInSettlerFemale01",Flags=Npc.Flag.Female};mod.Npcs.Add(female);
            var list=mod.LeveledNpcs.AddNew("SyntheticOpeningDonors");list.Entries=new();
            foreach(var actor in new[]{male,female})list.Entries.Add(new(){Data=new(){Reference=new FormLink<INpcSpawnGetter>(actor.FormKey),Level=1,Count=1}});
            var source=mod.Npcs.AddNew("WorkshopNPC");source.UseTemplateActors=Npc.TemplateActorType.Traits|Npc.TemplateActorType.Inventory;
            source.TemplateActors=new();source.TemplateActors.TraitTemplate.SetTo(list.FormKey);source.TemplateActors.InventoryTemplate.SetTo(list.FormKey);
        }
        foreach(var npc in mod.Npcs.Where(n=>n.EditorID is "WorkshopNPC" or "StandInSettlerMale01" or "StandInSettlerFemale01"))
        {npc.DefaultOutfit.SetTo(nativeOutfit);npc.Race.SetTo(race);if(npc.EditorID=="StandInSettlerMale01")npc.Voice.SetTo(voice);}
        void Clothing(uint id,string name,uint addonId,string male,string? female=null)
        {
            var addon=new ArmorAddon(Key(addonId),Fallout4Release.Fallout4){EditorID="SyntheticAddon_"+name};addon.Race.SetTo(race);
            addon.WorldModel=new GenderedItem<Model?>(new Model{File=male},new Model{File=female??male});mod.ArmorAddons.Add(addon);
            var armor=new Armor(Key(id),Fallout4Release.Fallout4){EditorID=name};armor.Armatures.Add(new(){ArmorAddon=new FormLinkNullable<IArmorAddonGetter>(addon.FormKey)});mod.Armors.Add(armor);
        }
        Clothing(0xB2D8D,"Armor_Wastelander_Light",0xB2D89,@"Armor\RaiderHeavy\MUnderArmor.nif");
        Clothing(0xB3F4C,"ClothesResident5",0xB3F49,@"Clothes\Residents\5SuitM.nif");
        Clothing(0xB3F4D,"ClothesResident5Hat",0xB3F4A,@"Clothes\Residents\5HatM.nif");
        Clothing(0x1C26B9,"ClothesGenericJumpsuit",0x5E76B,@"Synthetic\MechanicM.nif",@"Clothes\RedRocketJumpsuit\RedRocketJumpsuitF.nif");
        var parent=new SoundCategory(Key(0x64451),Fallout4Release.Fallout4){EditorID="AudioCategoryUI"};mod.SoundCategories.Add(parent);
        var category=new SoundCategory(Key(0x876BB),Fallout4Release.Fallout4){EditorID="AudioCategoryVOC"};category.Parent.SetTo(parent);mod.SoundCategories.Add(category);
        var sound=new SoundDescriptor(Key(0x1643CA),Fallout4Release.Fallout4){EditorID="XXXTestDialogueETravis",LoopAndRumble=new(),Data=new SoundDescriptorStandardData()};sound.Category.SetTo(category);sound.SoundFiles.Add(@"Synthetic\NeverPlayback.wav");mod.SoundDescriptors.Add(sound);
        var pipe=mod.Statics.Single(s=>s.EditorID=="PipeAStraightHalf01");
        switch(variant)
        {
            case "current-no-static":mod.Statics.Remove(pipe.FormKey);break;
            case "current-wrong-static-type":mod.Statics.Remove(pipe.FormKey);mod.MiscItems.AddNew("PipeAStraightHalf01");break;
            case "current-static-model":pipe.Model!.File=@"Synthetic\Wrong.nif";break;
            case "current-static-collision":mod.Statics.AddNew("PipeAStraightHalf01");break;
            case "current-no-sound":mod.SoundDescriptors.Remove(sound.FormKey);break;
            case "current-sound-shape":sound.SoundFiles.Add(@"Synthetic\Extra.wav");break;
        }
    }
}
