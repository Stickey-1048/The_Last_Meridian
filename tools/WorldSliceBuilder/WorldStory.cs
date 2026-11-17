using Mutagen.Bethesda;
using Mutagen.Bethesda.Fallout4;
using Mutagen.Bethesda.Plugins;
using Noggog;

// Opt-in development binding. Source records are only READ: the addon owns
// every new quest/reference; main/side quest rules stay in the explicit master.
public static partial class WorldStory
{
    // GREENWATER-STORY-001: where the Greenwater greybox stands in the owner's world. Free flat ground south of
    // the bypass road: x 1250-2850, y 200-700, at least 600 units from every tree and rock the expansion places
    // and 150 from the bypass's hidden posts; Mercy's two pieces stand in the yard, between the gateway and
    // Pritchard. The same numbers as tools/PluginBuilder/SpecGreenwater.cs (Greenwater.Parts); a test compares
    // the two. Nothing of the first section's 29 references moves.
    // MercyReturn is the one site that lies over the cabin's floor tiles (Program.cs: 256-unit tiles at x 2792,
    // 3048, 3304 and y 2800, 3056, placed at Z 16: x 2664 to 3432, y 2672 to 3184). It stands at Z 32: that
    // surface plus 16 units to settle, as the exterior's own arrival marker does. Not seen in the game.
    public static readonly Dictionary<string,(float X,float Y,float Z)> GreenwaterSites=new(){
        ["MercyTravel"]=(3150,2620,12),["MercyReturn"]=(3150,2700,32),
        ["ChuteStart"]=(1300,480,0),["LabelChute"]=(1380,580,12),["ReturnDock"]=(1640,480,100),
        ["Exit"]=(1760,380,12),["Arrival"]=(1800,300,0),["LandingSight"]=(1900,440,100),["LabelLanding"]=(1880,580,12),
        ["CargoWhole"]=(1960,650,12),["CargoReduced"]=(2040,650,12),["Steeple"]=(2000,300,12),["Opal"]=(2100,560,0),
        ["RationBoard"]=(2180,620,12),["Belden"]=(2200,400,0),["Rafferty"]=(2280,360,0),["Skiff"]=(2330,300,12),
        ["GangwaySight"]=(2450,500,100),["LabelQueen"]=(2520,600,12),["Table"]=(2600,540,12),["Hatcher"]=(2650,600,0),
        ["Strongbox"]=(2700,520,12),["Crew1"]=(2560,660,0),["Crew2"]=(2740,660,0),["FireControl"]=(2760,440,12),
        ["Burnt"]=(2620,440,12),["OffSideArrival"]=(2560,230,0),["OffSideSight"]=(2620,370,100),
        ["CargoLashed"]=(2680,300,12),["Chain"]=(2740,300,12),["Pilot"]=(2790,340,12)
    };
    const string GreenwaterQuest="TLM_GW";const string GreenwaterClone="TLM_WS_GW";const string RoadQuest="TLM_MQ02B";
    static readonly ModKey StoryMaster=ModKey.FromNameAndExtension("TheLastMeridian.esp");

    // The greybox quest, cloned as the first section is: its own persistent references at the sites above, its
    // own aliases and alias scripts, and every property that pointed at the original pointing at the clone.
    // What it puts its references INTO (the aliases of TLM_MQ02B) and the road itself stay in the story master.
    static object? AddGreenwater(Fallout4Mod mod,Worldspace world,IFallout4ModGetter source,Dictionary<FormKey,IPlacedGetter> sourceRefs,QuestAdapter firstSection)
    {
        var original=source.Quests.SingleOrDefault(q=>q.EditorID==GreenwaterQuest);
        var bound=firstSection.Scripts.Single(s=>s.Name=="TLM:Act1Walk").Properties.Where(p=>p.Name=="TLM_Greenwater").ToArray();
        if(original==null){
            // A source built before the road existed has neither the quest nor the binding.
            if(bound.Length!=0)throw new InvalidDataException("Greenwater binding without a Greenwater quest");
            return null;
        }
        var road=source.Quests.SingleOrDefault(q=>q.EditorID==RoadQuest)??throw new InvalidDataException("Greenwater greybox without its road quest");
        if(bound.Length!=1||bound[0] is not ScriptObjectProperty door||door.Alias!=-1||door.Object.FormKey!=original.FormKey)throw new InvalidDataException("First section is not bound to the story master's Greenwater greybox");
        var clone=original.Duplicate(mod.GetNextFormKey());
        clone.EditorID=GreenwaterClone;clone.Name="The Last Meridian - exterior Greenwater greybox (development)";
        mod.Quests.Add(clone);
        var aliases=clone.Aliases??throw new InvalidDataException("Missing Greenwater alias table");
        if(aliases.Count!=GreenwaterSites.Count||aliases.Any(a=>a is not QuestReferenceAlias r||!GreenwaterSites.ContainsKey(r.Name??"")))throw new InvalidDataException("Unexpected Greenwater alias contract");
        var mapping=new List<object>();
        foreach(var a in aliases.Cast<QuestReferenceAlias>()){
            if(a.ForcedReference.IsNull||!sourceRefs.TryGetValue(a.ForcedReference.FormKey,out var old))throw new InvalidDataException("Missing Greenwater source placement: "+a.Name);
            var at=GreenwaterSites[a.Name!];var key=mod.GetNextFormKey();IPlaced placed;
            if(old is IPlacedNpcGetter npc){var p=npc.Duplicate(key);p.Position=new P3Float(at.X,at.Y,at.Z);p.Rotation=new P3Float(0,0,MathF.PI);p.EditorID="TLM_WS_ST_GW_"+a.Name;placed=p;}
            else if(old is IPlacedObjectGetter obj){var p=obj.Duplicate(key);p.Position=new P3Float(at.X,at.Y,at.Z);p.Rotation=new P3Float(0,0,0);p.EditorID="TLM_WS_ST_GW_"+a.Name;placed=p;}
            else throw new InvalidDataException("Unsupported Greenwater source placement: "+a.Name);
            placed.MajorRecordFlagsRaw|=0xC00; // own persistent, initially disabled
            world.TopCell!.Persistent.Add(placed);a.ForcedReference.SetTo(key);
            mapping.Add(new{alias=a.Name,id=a.ID,source=old.FormKey.ToString(),reference=key.ToString(),x=at.X,y=at.Y,z=at.Z});
        }
        var adapter=clone.VirtualMachineAdapter??throw new InvalidDataException("Missing Greenwater VMAD");
        void Remap(ScriptObjectProperty obj){if(obj.Object.FormKey==original.FormKey)obj.Object.SetTo(clone.FormKey);}
        void Script(ScriptEntry script){foreach(var p in script.Properties){
            if(p is ScriptObjectProperty obj)Remap(obj);
            if(p is ScriptObjectListProperty list)foreach(var o in list.Objects)Remap(o);
        }}
        foreach(var s in adapter.Scripts)Script(s);
        foreach(var b in adapter.Aliases){Remap(b.Property);foreach(var s in b.Scripts)Script(s);}
        // The exterior first section opens the exterior greybox, not the test room's.
        door.Object.SetTo(clone.FormKey);
        return new{section=clone.EditorID,sectionForm=clone.FormKey.ToString(),road=road.EditorID,roadForm=road.FormKey.ToString(),references=mapping.Count,mapping};
    }

    static void ValidateGreenwater(IFallout4ModGetter addon,IQuestGetter firstSection)
    {
        var clone=addon.Quests.SingleOrDefault(q=>q.EditorID==GreenwaterClone);
        var door=firstSection.VirtualMachineAdapter!.Scripts.Single(s=>s.Name=="TLM:Act1Walk").Properties.Where(p=>p.Name=="TLM_Greenwater").ToArray();
        if(clone==null){if(door.Length!=0)throw new InvalidDataException("Greenwater binding without the exterior greybox");return;}
        if(door.Length!=1||door[0] is not IScriptObjectPropertyGetter opened||opened.Alias!=-1||opened.Object.FormKey!=clone.FormKey)throw new InvalidDataException("Exterior first section does not open the exterior Greenwater greybox");
        var aliases=clone.Aliases?.OfType<IQuestReferenceAliasGetter>().ToArray()??throw new InvalidDataException("Greenwater alias table missing");
        if(aliases.Length!=GreenwaterSites.Count||aliases.Any(a=>a.ForcedReference.IsNull||a.ForcedReference.FormKey.ModKey!=addon.ModKey))throw new InvalidDataException("Greenwater aliases must bind exactly their own new references");
        var refs=addon.Worldspaces.Single().TopCell!.Persistent.ToDictionary(p=>p.FormKey);
        foreach(var a in aliases){
            if(!refs.TryGetValue(a.ForcedReference.FormKey,out var placed))throw new InvalidDataException("Greenwater alias points outside new persistent world refs");
            var at=GreenwaterSites[a.Name!];
            P3Float? pos=placed switch {IPlacedNpcGetter n=>n.Position,IPlacedObjectGetter o=>o.Position,_=>null};
            if(pos is not {} got||got.X!=at.X||got.Y!=at.Y||got.Z!=at.Z)throw new InvalidDataException("Greenwater reference is not at its site: "+a.Name);
            if((placed.MajorRecordFlagsRaw&0xC00)!=0xC00)throw new InvalidDataException("Greenwater reference is not persistent and initially disabled: "+a.Name);
        }
        var vmad=clone.VirtualMachineAdapter??throw new InvalidDataException("Greenwater VMAD missing");
        var ids=aliases.Select(a=>a.ID).ToHashSet();
        if(vmad.Aliases.Any(a=>a.Property.Object.FormKey!=clone.FormKey||!ids.Contains((uint)a.Property.Alias)||a.Scripts.Any(s=>s.Name!="TLM:GreenwaterTalk")))throw new InvalidDataException("Greenwater alias script ownership not remapped");
        var walk=vmad.Scripts.Single(s=>s.Name=="TLM:GreenwaterWalk");
        foreach(var p in walk.Properties){
            if(p is IScriptObjectPropertyGetter obj){
                if(obj.Alias>=0&&obj.Object.FormKey!=clone.FormKey)throw new InvalidDataException("Greenwater own alias property points at preview: "+p.Name);
                if(obj.Alias<0&&obj.Object.FormKey.ModKey!=StoryMaster)throw new InvalidDataException("Greenwater form property does not point into the story master: "+p.Name);
            }
            if(p is IScriptObjectListPropertyGetter list){
                if(p.Name!="CastInto"&&list.Objects.Any(o=>o.Object.FormKey!=clone.FormKey))throw new InvalidDataException("Greenwater own alias array points at preview: "+p.Name);
                if(p.Name=="CastInto"&&list.Objects.Any(o=>o.Object.FormKey.ModKey!=StoryMaster))throw new InvalidDataException("Road aliases were not preserved in master");
            }
        }
        if(addon.Quests.Any(q=>q.EditorID==RoadQuest))throw new InvalidDataException("The road quest was copied into the addon");
    }
    public static void Validate(IFallout4ModGetter addon)
    {
        var section=addon.Quests.Single(q=>q.EditorID=="TLM_WS_A1");
        var aliases=section.Aliases?.OfType<IQuestReferenceAliasGetter>().ToArray()??throw new InvalidDataException("Story alias table missing");
        if(aliases.Length!=29||aliases.Any(a=>a.ForcedReference.IsNull||a.ForcedReference.FormKey.ModKey!=addon.ModKey))throw new InvalidDataException("Story aliases must bind exactly29new references");
        var allowedIds=aliases.Select(a=>a.ID).ToHashSet();
        var refs=addon.Worldspaces.Single().TopCell!.Persistent.ToDictionary(p=>p.FormKey);
        if(aliases.Any(a=>!refs.ContainsKey(a.ForcedReference.FormKey)))throw new InvalidDataException("Story alias points outside new persistent world refs");
        var vmad=section.VirtualMachineAdapter??throw new InvalidDataException("Story VMAD missing");
        if(vmad.Aliases.Any(a=>a.Property.Object.FormKey!=section.FormKey||!allowedIds.Contains((uint)a.Property.Alias)))throw new InvalidDataException("Alias script ownership not remapped");
        var walk=vmad.Scripts.Single(s=>s.Name=="TLM:Act1Walk");
        foreach(var p in walk.Properties){
            if(p is IScriptObjectPropertyGetter obj&&obj.Alias>=0&&obj.Object.FormKey!=section.FormKey)throw new InvalidDataException("Own alias property points at preview");
            // ACT1-RUNTIME-001: the helper quest stays in the story master; the clone only points at it.
            if(p.Name=="TLM_MercyBriefing"&&(p is not IScriptObjectPropertyGetter brief||brief.Alias!=-1||brief.Object.FormKey.ModKey!=ModKey.FromNameAndExtension("TheLastMeridian.esp")))throw new InvalidDataException("Mercy briefing binding does not point into the story master");
            if(p is IScriptObjectListPropertyGetter list){
                if(p.Name=="Everything"&&list.Objects.Count!=29)throw new InvalidDataException("Everything mismatch");
                if(p.Name!="CastInto"&&list.Objects.Any(o=>o.Alias>=0&&o.Object.FormKey!=section.FormKey))throw new InvalidDataException("Own alias array points at preview");
                if(p.Name=="CastInto"&&list.Objects.Any(o=>o.Object.FormKey.ModKey!=ModKey.FromNameAndExtension("TheLastMeridian.esp")))throw new InvalidDataException("Quest rule aliases were not preserved in master");
            }
        }
        if(!addon.ModHeader.MasterReferences.Any(m=>m.Master==ModKey.FromNameAndExtension("TheLastMeridian.esp")))throw new InvalidDataException("Missing explicit story master");
        var guides=vmad.Aliases.SelectMany(a=>a.Scripts).Where(s=>s.Name=="TLM:Act1Guide").ToArray();
        if(guides.Length!=3||guides.Any(s=>!s.Properties.OfType<IScriptBoolPropertyGetter>().Any(p=>p.Name=="Exterior"&&p.Data)))throw new InvalidDataException("Missing exterior guide copy binding");
        var entry=addon.Quests.Single(q=>q.EditorID=="TLM_WS_Entry");
        if(entry.Aliases?.Count!=1||entry.VirtualMachineAdapter?.Scripts.Single().Name!="TLM:WorldEntry")throw new InvalidDataException("Unsafe entry wrapper layout");
        var player=entry.Aliases!.OfType<IQuestReferenceAliasGetter>().Single();
        var guard=entry.VirtualMachineAdapter!.Aliases.Single();
        if(player.ID!=0||player.ForcedReference.FormKey!=FormKey.Factory("000014:Fallout4.esm")||guard.Property.Object.FormKey!=entry.FormKey||guard.Property.Alias!=0||guard.Scripts.Single().Name!="TLM:WorldEntryPlayer")throw new InvalidDataException("Missing saved-load cancellation guard");
        var playerProperty=entry.VirtualMachineAdapter.Scripts.Single().Properties.OfType<IScriptObjectPropertyGetter>().Single(p=>p.Name=="FreshPlayer");
        if(playerProperty.Object.FormKey!=entry.FormKey||playerProperty.Alias!=0)throw new InvalidDataException("Missing guarded player-alias property");
        ValidateGreenwater(addon,section);
        ValidateNightMail(addon,section);
        ValidateRedHollow(addon,section);
    }
    public static object Add(Fallout4Mod mod, Worldspace world, Cell clearing, IFallout4ModGetter source)
    {
        if(source.ModKey!=ModKey.FromNameAndExtension("TheLastMeridian.esp"))throw new InvalidDataException("Story source must be named TheLastMeridian.esp");
        var original=source.Quests.Single(q=>q.EditorID=="TLM_A1");
        var section=original.Duplicate(mod.GetNextFormKey());
        section.EditorID="TLM_WS_A1";section.Name="The Last Meridian - exterior first section (development)";
        mod.Quests.Add(section);
        var sourceRefs=source.Cells.Records.SelectMany(b=>b.SubBlocks).SelectMany(b=>b.Cells)
            .SelectMany(c=>c.Persistent.Concat(c.Temporary)).ToDictionary(p=>p.FormKey);
        var sites=new Dictionary<string,(float X,float Y,float Z)>{
            ["Marshal"]=(700,1050,0),["Dispatch"]=(740,1000,10),["Revolver"]=(650,1000,10),
            ["Journal"]=(660,1080,10),["Ledger"]=(820,1080,10),["BrakeShoes"]=(850,1000,12),["DrawBar"]=(910,1110,12),
            ["AmbushSight"]=(1750,1710,100),["AmbushCenter"]=(1900,1950,0),["Wagon"]=(2100,2020,0),
            ["Nell"]=(1850,2040,0),["Abel"]=(2000,2040,0),["Dunmore"]=(1900,1900,0),
            ["Cutter1"]=(2050,1920,0),["Cutter2"]=(1900,2150,0),["Cutter3"]=(1740,1920,0),
            ["TownGate"]=(3048,2400,100),["Talbot"]=(2850,2530,0),["Pritchard"]=(3260,2530,0),
            ["Pike"]=(3500,2770,0),["Vane"]=(3500,3130,0),["Keene"]=(2520,2740,0),["Haskell"]=(2520,3140,0),
            ["NoticeBoard"]=(3500,2900,12),["Stove"]=(2550,2920,12),["CaravanYard"]=(3450,3300,0),
            ["GuideWreck"]=(1000,850,12),["GuideRoad"]=(2250,1950,12),["GuideMercy"]=(3380,2500,12)
        };
        var mapping=new List<object>();
        // Retain26 actual actors/items/triggers plus3 guides. Only test-room
        // decoration is omitted; guides get an explicit exterior-only copy flag.
        var aliases=section.Aliases??throw new InvalidDataException("Missing original alias table");
        foreach(var a in aliases.Where(a=>a is not QuestReferenceAlias r||!sites.ContainsKey(r.Name??"")).ToArray())aliases.Remove(a);
        if(aliases.Count!=29)throw new InvalidDataException("Unexpected first-section alias contract");
        foreach(var a in aliases.Cast<QuestReferenceAlias>()){
            if(a.ForcedReference.IsNull||!sourceRefs.TryGetValue(a.ForcedReference.FormKey,out var old))throw new InvalidDataException("Missing source placement: "+a.Name);
            var at=sites[a.Name!];var key=mod.GetNextFormKey();IPlaced placed;
            if(old is IPlacedNpcGetter npc){var p=npc.Duplicate(key);p.Position=new P3Float(at.X,at.Y,at.Z);p.Rotation=new P3Float(0,0,MathF.PI);p.EditorID="TLM_WS_ST_"+a.Name;placed=p;}
            else if(old is IPlacedObjectGetter obj){var p=obj.Duplicate(key);p.Position=new P3Float(at.X,at.Y,at.Z);p.Rotation=new P3Float(0,0,0);p.EditorID="TLM_WS_ST_"+a.Name;placed=p;}
            else throw new InvalidDataException("Unsupported source placement: "+a.Name);
            placed.MajorRecordFlagsRaw|=0xC00; // own persistent, initially disabled
            world.TopCell!.Persistent.Add(placed);a.ForcedReference.SetTo(key);
            mapping.Add(new{alias=a.Name,id=a.ID,source=old.FormKey.ToString(),reference=key.ToString(),x=at.X,y=at.Y,z=at.Z});
        }
        var adapter=section.VirtualMachineAdapter??throw new InvalidDataException("Missing source VMAD");
        foreach(var binding in adapter.Aliases.Where(a=>a.Property.Alias>=26&&a.Property.Alias<33).ToArray())adapter.Aliases.Remove(binding);
        void Remap(ScriptObjectProperty obj){if(obj.Object.FormKey==original.FormKey)obj.Object.SetTo(section.FormKey);}
        void Script(ScriptEntry script){foreach(var p in script.Properties){
            if(p is ScriptObjectProperty obj)Remap(obj);
            if(p is ScriptObjectListProperty list){
                if(p.Name=="Everything")foreach(var o in list.Objects.Where(o=>o.Alias>=26&&o.Alias<33).ToArray())list.Objects.Remove(o);
                foreach(var o in list.Objects)Remap(o);
            }
            if(p.Name=="EverythingNames"&&p is ScriptStringListProperty text)for(int i=0;i<7;i++)text.Data.RemoveAt(26);
        }}
        foreach(var s in adapter.Scripts)Script(s);
        foreach(var b in adapter.Aliases){Remap(b.Property);foreach(var s in b.Scripts)Script(s);}
        foreach(var guide in adapter.Aliases.SelectMany(a=>a.Scripts).Where(s=>s.Name=="TLM:Act1Guide"))guide.Properties.Add(new ScriptBoolProperty{Name="Exterior",Flags=ScriptProperty.Flag.Edited,Data=true});
        var begin=mod.Messages.AddNew("TLM_WS_Opening");begin.Description="Exterior first-section prototype: follow the route to the wreck and search the ground for the marshal's dispatch. The caravan road lies beyond; Mercy's fenced cabin is at the far end. The eastern route bypasses the optional hold-up.";begin.DisplayTime=8;
        foreach(var script in adapter.Scripts)foreach(var p in script.Properties.OfType<ScriptObjectProperty>().Where(p=>p.Name=="SayBegin"))p.Object.SetTo(begin.FormKey);
        // Duplicate the already-correct empty quest header, but use only the
        // narrow guarded entry script and no actor aliases on this wrapper.
        var entry=original.Duplicate(mod.GetNextFormKey());entry.EditorID="TLM_WS_Entry";entry.Name="Exterior story entry - explicit development only";
        entry.Aliases!.Clear();entry.VirtualMachineAdapter=new QuestAdapter();
        var player=new QuestReferenceAlias{ID=0,Name="FreshEntryPlayer"};
        player.ForcedReference.SetTo(FormKey.Factory("000014:Fallout4.esm"));entry.Aliases.Add(player);
        var guard=new QuestFragmentAlias{Property=new ScriptObjectProperty{Object=entry.ToLink<IFallout4MajorRecordGetter>(),Alias=0}};
        guard.Scripts.Add(new ScriptEntry{Name="TLM:WorldEntryPlayer"});entry.VirtualMachineAdapter.Aliases.Add(guard);
        var start=new ScriptEntry{Name="TLM:WorldEntry"};
        void Prop(string name,FormKey key)=>start.Properties.Add(new ScriptObjectProperty{Name=name,Flags=ScriptProperty.Flag.Edited,Object=new FormLink<IFallout4MajorRecordGetter>(key),Alias=-1});
        Prop("Preview",original.FormKey);Prop("MainQuest",source.Quests.Single(q=>q.EditorID=="TLM_MQ01").FormKey);
        Prop("SideQuest",source.Quests.Single(q=>q.EditorID=="TLM_SQ01").FormKey);Prop("Section",section.FormKey);Prop("Clearing",clearing.FormKey);
        start.Properties.Add(new ScriptObjectProperty{Name="FreshPlayer",Flags=ScriptProperty.Flag.Edited,Object=entry.ToLink<IFallout4MajorRecordGetter>(),Alias=0});
        entry.VirtualMachineAdapter.Scripts.Add(start);mod.Quests.Add(entry);
        if(adapter.Scripts.Single(s=>s.Name=="TLM:Act1Walk").Properties.OfType<ScriptObjectListProperty>().Single(p=>p.Name=="Everything").Objects.Count!=29)throw new InvalidDataException("Exterior Everything binding mismatch");
        // ACT1-RUNTIME-001: a check only; nothing is remapped or written for it. The cloned walk must keep
        // pointing at the master's own Mercy briefing quest, never at a copy, the section or nothing.
        // A source built before that quest existed has neither the quest nor the property.
        var briefing=source.Quests.SingleOrDefault(q=>q.EditorID=="TLM_MercyBriefing");
        var bound=adapter.Scripts.Single(s=>s.Name=="TLM:Act1Walk").Properties.Where(p=>p.Name=="TLM_MercyBriefing").ToArray();
        if(briefing==null?bound.Length!=0:bound.Length!=1||bound[0] is not ScriptObjectProperty helper||helper.Alias!=-1||helper.Object.FormKey!=briefing.FormKey)throw new InvalidDataException("Mercy briefing binding missing or not the story master's TLM_MercyBriefing");
        // GREENWATER-STORY-001: the second clone, after everything of the first section is allocated, so that the
        // first section's 29 references and both quests keep the ids they had.
        var greenwater=AddGreenwater(mod,world,source,sourceRefs,adapter);
        var nightMail=AddNightMail(mod,world,source,sourceRefs,adapter);
        var redHollow=AddRedHollow(mod,world,source,sourceRefs,adapter);
        return new{section=section.EditorID,sectionForm=section.FormKey.ToString(),entry=entry.EditorID,entryForm=entry.FormKey.ToString(),explicitCommand="cqf TLM_WS_Entry Begin",mapping,greenwater,nightMail,redHollow,limitations="Fresh dev session only; no navmesh or pursuit/combat proof. Existing quest rules reused, not overridden."};
    }
}
