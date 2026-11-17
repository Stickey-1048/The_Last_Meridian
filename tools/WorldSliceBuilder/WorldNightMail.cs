using Mutagen.Bethesda;
using Mutagen.Bethesda.Fallout4;
using Mutagen.Bethesda.Plugins;
using Noggog;

public static partial class WorldStory
{
    // Only these two pieces belong in the exterior. The fifty-one-alias
    // controller still points at the master's own, separately floored cell.
    public static readonly Dictionary<string,(float X,float Y,float Z)> NightMailSites=new(){
        ["MercyTravel"]=(2950,2640,12),["MercyReturn"]=(3000,2580,32)
    };
    const string NightMailQuest="TLM_NM",NightMailClone="TLM_WS_NM",NightMailRoad="TLM_MQ02A";

    static object? AddNightMail(Fallout4Mod mod,Worldspace world,IFallout4ModGetter source,
        Dictionary<FormKey,IPlacedGetter> sourceRefs,QuestAdapter firstSection)
    {
        var original=source.Quests.SingleOrDefault(q=>q.EditorID==NightMailQuest);
        var bound=firstSection.Scripts.Single(s=>s.Name=="TLM:Act1Walk").Properties.Where(p=>p.Name=="TLM_NightMail").ToArray();
        if(original==null){if(bound.Length!=0)throw new InvalidDataException("Night Mail binding without its greybox");return null;}
        var road=source.Quests.SingleOrDefault(q=>q.EditorID==NightMailRoad)??throw new InvalidDataException("Night Mail greybox without its road quest");
        if(bound.Length!=1||bound[0] is not ScriptObjectProperty door||door.Alias!=-1||door.Object.FormKey!=original.FormKey)
            throw new InvalidDataException("First section is not bound to the story master's Night Mail greybox");
        var ownCell=source.Cells.Records.SelectMany(b=>b.SubBlocks).SelectMany(b=>b.Cells).SingleOrDefault(c=>c.EditorID=="TLM_CELL_NightMail")
            ??throw new InvalidDataException("Night Mail own cell missing");
        var interiorRefs=ownCell.Persistent.Select(r=>r.FormKey).ToHashSet();
        var clone=original.Duplicate(mod.GetNextFormKey());clone.EditorID=NightMailClone;
        clone.Name="The Last Meridian - exterior-linked Night Mail (development)";
        var aliases=clone.Aliases?.OfType<QuestReferenceAlias>().ToArray()??throw new InvalidDataException("Night Mail aliases missing");
        if(aliases.Length!=51||aliases.Select(a=>a.Name).Distinct().Count()!=51||!NightMailSites.Keys.All(n=>aliases.Any(a=>a.Name==n)))
            throw new InvalidDataException("Unexpected Night Mail alias contract");
        var mapping=new List<object>();
        foreach(var a in aliases){
            if(a.ForcedReference.IsNull||!sourceRefs.TryGetValue(a.ForcedReference.FormKey,out var old)||old.EditorID!="TLM_REF_NM_"+a.Name)
                throw new InvalidDataException("Missing or substituted Night Mail source placement: "+a.Name);
            if((old.MajorRecordFlagsRaw&0xC00)!=0xC00)throw new InvalidDataException("Night Mail source is not persistent and initially disabled");
            var sourceKey=old.FormKey;
            if(NightMailSites.TryGetValue(a.Name!,out var at)){
                if(old is not IPlacedObjectGetter obj)throw new InvalidDataException("Night Mail Mercy piece must be an object");
                var placed=obj.Duplicate(mod.GetNextFormKey());placed.EditorID="TLM_WS_ST_NM_"+a.Name;
                placed.Position=new P3Float(at.X,at.Y,at.Z);placed.Rotation=new P3Float(0,0,0);placed.MajorRecordFlagsRaw|=0xC00;
                world.TopCell!.Persistent.Add(placed);a.ForcedReference.SetTo(placed.FormKey);
                mapping.Add(new{alias=a.Name,id=a.ID,source=sourceKey.ToString(),reference=placed.FormKey.ToString(),x=at.X,y=at.Y,z=at.Z,exterior=true});
            }else{
                if(!interiorRefs.Contains(sourceKey))throw new InvalidDataException("Night Mail interior placement outside its own cell: "+a.Name);
                mapping.Add(new{alias=a.Name,id=a.ID,source=sourceKey.ToString(),reference=sourceKey.ToString(),exterior=false});
            }
        }
        var adapter=clone.VirtualMachineAdapter??throw new InvalidDataException("Night Mail VMAD missing");
        void Remap(ScriptObjectProperty p){if(p.Object.FormKey==original.FormKey)p.Object.SetTo(clone.FormKey);}
        void Script(ScriptEntry s){foreach(var p in s.Properties){if(p is ScriptObjectProperty o)Remap(o);if(p is ScriptObjectListProperty l)foreach(var entry in l.Objects)Remap(entry);}}
        foreach(var s in adapter.Scripts)Script(s);
        foreach(var a in adapter.Aliases){Remap(a.Property);foreach(var s in a.Scripts)Script(s);}
        mod.Quests.Add(clone);door.Object.SetTo(clone.FormKey);
        return new{section=clone.EditorID,sectionForm=clone.FormKey.ToString(),road=road.EditorID,roadForm=road.FormKey.ToString(),references=2,masterCellReferences=49,mapping};
    }

    static void ValidateNightMail(IFallout4ModGetter addon,IQuestGetter section)
    {
        var clone=addon.Quests.SingleOrDefault(q=>q.EditorID==NightMailClone);
        var bound=section.VirtualMachineAdapter!.Scripts.Single(s=>s.Name=="TLM:Act1Walk").Properties.Where(p=>p.Name=="TLM_NightMail").ToArray();
        if(clone==null){if(bound.Length!=0)throw new InvalidDataException("Night Mail binding without exterior-linked greybox");return;}
        if(bound.Length!=1||bound[0] is not IScriptObjectPropertyGetter door||door.Alias!=-1||door.Object.FormKey!=clone.FormKey)
            throw new InvalidDataException("Exterior first section does not open its Night Mail controller");
        var aliases=clone.Aliases?.OfType<IQuestReferenceAliasGetter>().ToArray()??throw new InvalidDataException("Night Mail aliases missing");
        if(aliases.Length!=51||aliases.Select(a=>a.ID).Distinct().Count()!=51)throw new InvalidDataException("Night Mail alias count/identity mismatch");
        var refs=addon.Worldspaces.Single().TopCell!.Persistent.ToDictionary(p=>p.FormKey);
        foreach(var a in aliases){
            if(a.ForcedReference.IsNull)throw new InvalidDataException("Night Mail alias unfilled");
            if(NightMailSites.TryGetValue(a.Name!,out var at)){
                if(!refs.TryGetValue(a.ForcedReference.FormKey,out var piece)||piece is not IPlacedObjectGetter obj||obj.EditorID!="TLM_WS_ST_NM_"+a.Name||obj.Position!=new P3Float(at.X,at.Y,at.Z)||(obj.MajorRecordFlagsRaw&0xC00)!=0xC00)
                    throw new InvalidDataException("Night Mail Mercy binding/placement mismatch: "+a.Name);
            }else if(a.ForcedReference.FormKey.ModKey!=StoryMaster)throw new InvalidDataException("Night Mail interior alias left the story master");
        }
        var vmad=clone.VirtualMachineAdapter??throw new InvalidDataException("Night Mail VMAD missing");
        var ids=aliases.Select(a=>a.ID).ToHashSet();
        if(vmad.Aliases.Any(a=>a.Property.Object.FormKey!=clone.FormKey||!ids.Contains((uint)a.Property.Alias)||a.Scripts.Any(s=>s.Name!="TLM:NightMailTalk")))throw new InvalidDataException("Night Mail alias script ownership mismatch");
        var walk=vmad.Scripts.Single(s=>s.Name=="TLM:NightMailWalk");
        foreach(var p in walk.Properties){
            if(p is IScriptObjectPropertyGetter o&&((o.Alias>=0&&o.Object.FormKey!=clone.FormKey)||(o.Alias<0&&o.Object.FormKey.ModKey!=StoryMaster)))throw new InvalidDataException("Night Mail scalar binding mismatch: "+p.Name);
            if(p is IScriptObjectListPropertyGetter l&&l.Objects.Any(o=>o.Object.FormKey.ModKey!=(p.Name=="CastInto"?StoryMaster:addon.ModKey)))throw new InvalidDataException("Night Mail alias-list binding mismatch: "+p.Name);
        }
        if(addon.Quests.Any(q=>q.EditorID==NightMailRoad))throw new InvalidDataException("Night Mail road duplicated into exterior");
    }
}
