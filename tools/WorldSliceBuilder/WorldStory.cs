using Mutagen.Bethesda;
using Mutagen.Bethesda.Fallout4;
using Mutagen.Bethesda.Plugins;
using Noggog;

// Opt-in development binding. Source records are only READ: the addon owns
// every new quest/reference; main/side quest rules stay in the explicit master.
public static class WorldStory
{
    public static void Validate(IFallout4ModGetter addon)
    {
        var section=addon.Quests.Single(q=>q.EditorID=="TLM_WS_A1");
        var aliases=section.Aliases?.OfType<IQuestReferenceAliasGetter>().ToArray()??throw new InvalidDataException("Story alias table missing");
        if(aliases.Length!=26||aliases.Any(a=>a.ID>=26||a.ForcedReference.IsNull||a.ForcedReference.FormKey.ModKey!=addon.ModKey))throw new InvalidDataException("Story aliases must bind exactly26new references");
        var refs=addon.Worldspaces.Single().TopCell!.Persistent.ToDictionary(p=>p.FormKey);
        if(aliases.Any(a=>!refs.ContainsKey(a.ForcedReference.FormKey)))throw new InvalidDataException("Story alias points outside new persistent world refs");
        var vmad=section.VirtualMachineAdapter??throw new InvalidDataException("Story VMAD missing");
        if(vmad.Aliases.Any(a=>a.Property.Object.FormKey!=section.FormKey||a.Property.Alias>=26))throw new InvalidDataException("Alias script ownership not remapped");
        var walk=vmad.Scripts.Single(s=>s.Name=="TLM:Act1Walk");
        foreach(var p in walk.Properties){
            if(p is IScriptObjectPropertyGetter obj&&obj.Alias>=0&&obj.Object.FormKey!=section.FormKey)throw new InvalidDataException("Own alias property points at preview");
            if(p is IScriptObjectListPropertyGetter list){
                if(p.Name=="Everything"&&list.Objects.Count!=26)throw new InvalidDataException("Everything mismatch");
                if(p.Name!="CastInto"&&list.Objects.Any(o=>o.Alias>=0&&o.Object.FormKey!=section.FormKey))throw new InvalidDataException("Own alias array points at preview");
                if(p.Name=="CastInto"&&list.Objects.Any(o=>o.Object.FormKey.ModKey!=ModKey.FromNameAndExtension("TheLastMeridian.esp")))throw new InvalidDataException("Quest rule aliases were not preserved in master");
            }
        }
        if(!addon.ModHeader.MasterReferences.Any(m=>m.Master==ModKey.FromNameAndExtension("TheLastMeridian.esp")))throw new InvalidDataException("Missing explicit story master");
        var entry=addon.Quests.Single(q=>q.EditorID=="TLM_WS_Entry");
        if(entry.Aliases?.Count>0||entry.VirtualMachineAdapter?.Scripts.Single().Name!="TLM:WorldEntry")throw new InvalidDataException("Unsafe entry wrapper layout");
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
            ["NoticeBoard"]=(3500,2900,12),["Stove"]=(2550,2920,12),["CaravanYard"]=(3450,3300,0)
        };
        var mapping=new List<object>();
        // The first26 original aliases are the actual actors/items/triggers.
        // Test-room decoration and its left/right guide copy must not leak here.
        var aliases=section.Aliases??throw new InvalidDataException("Missing original alias table");
        foreach(var a in aliases.Where(a=>a is not QuestReferenceAlias r||!sites.ContainsKey(r.Name??"")).ToArray())aliases.Remove(a);
        if(aliases.Count!=26)throw new InvalidDataException("Unexpected first-section alias contract");
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
        foreach(var binding in adapter.Aliases.Where(a=>a.Property.Alias>=26).ToArray())adapter.Aliases.Remove(binding);
        void Remap(ScriptObjectProperty obj){if(obj.Object.FormKey==original.FormKey)obj.Object.SetTo(section.FormKey);}
        void Script(ScriptEntry script){foreach(var p in script.Properties){
            if(p is ScriptObjectProperty obj)Remap(obj);
            if(p is ScriptObjectListProperty list){
                if(p.Name=="Everything")foreach(var o in list.Objects.Where(o=>o.Alias>=26).ToArray())list.Objects.Remove(o);
                foreach(var o in list.Objects)Remap(o);
            }
            if(p.Name=="EverythingNames"&&p is ScriptStringListProperty text)while(text.Data.Count>26)text.Data.RemoveAt(text.Data.Count-1);
        }}
        foreach(var s in adapter.Scripts)Script(s);
        foreach(var b in adapter.Aliases){Remap(b.Property);foreach(var s in b.Scripts)Script(s);}
        var begin=mod.Messages.AddNew("TLM_WS_Opening");begin.Description="Exterior first-section prototype: follow the route to the wreck and search the ground for the marshal's dispatch. The caravan road lies beyond; Mercy's fenced cabin is at the far end. The eastern route bypasses the optional hold-up.";begin.DisplayTime=8;
        foreach(var script in adapter.Scripts)foreach(var p in script.Properties.OfType<ScriptObjectProperty>().Where(p=>p.Name=="SayBegin"))p.Object.SetTo(begin.FormKey);
        // Duplicate the already-correct empty quest header, but use only the
        // narrow guarded entry script and no actor aliases on this wrapper.
        var entry=original.Duplicate(mod.GetNextFormKey());entry.EditorID="TLM_WS_Entry";entry.Name="Exterior story entry - explicit development only";
        entry.Aliases!.Clear();entry.VirtualMachineAdapter=new QuestAdapter();
        var start=new ScriptEntry{Name="TLM:WorldEntry"};
        void Prop(string name,FormKey key)=>start.Properties.Add(new ScriptObjectProperty{Name=name,Flags=ScriptProperty.Flag.Edited,Object=new FormLink<IFallout4MajorRecordGetter>(key),Alias=-1});
        Prop("Preview",original.FormKey);Prop("MainQuest",source.Quests.Single(q=>q.EditorID=="TLM_MQ01").FormKey);
        Prop("SideQuest",source.Quests.Single(q=>q.EditorID=="TLM_SQ01").FormKey);Prop("Section",section.FormKey);Prop("Clearing",clearing.FormKey);
        entry.VirtualMachineAdapter.Scripts.Add(start);mod.Quests.Add(entry);
        if(adapter.Scripts.Single(s=>s.Name=="TLM:Act1Walk").Properties.OfType<ScriptObjectListProperty>().Single(p=>p.Name=="Everything").Objects.Count!=26)throw new InvalidDataException("Exterior Everything binding mismatch");
        return new{section=section.EditorID,sectionForm=section.FormKey.ToString(),entry=entry.EditorID,entryForm=entry.FormKey.ToString(),explicitCommand="cqf TLM_WS_Entry Begin",mapping,limitations="Fresh dev session only; no navmesh or pursuit/combat proof. Existing quest rules reused, not overridden."};
    }
}
