using Mutagen.Bethesda;
using Mutagen.Bethesda.Fallout4;
using Mutagen.Bethesda.Plugins;
using Noggog;

public static partial class WorldStory
{
    // Only these two pieces belong in the exterior. The fifty-one-alias
    // controller still points at the master's own, separately floored cell.
    public static readonly Dictionary<string,(float X,float Y,float Z)> RedHollowSites=new(){
        ["MercyTravel"]=(3520,2600,12),["MercyReturn"]=(3490,2570,32)
    };
    const string RedHollowQuest="TLM_RH",RedHollowClone="TLM_WS_RH",RedHollowRoad="TLM_MQ02C";

    static object? AddRedHollow(Fallout4Mod mod,Worldspace world,IFallout4ModGetter source,
        Dictionary<FormKey,IPlacedGetter> sourceRefs,QuestAdapter firstSection)
    {
        var original=source.Quests.SingleOrDefault(q=>q.EditorID==RedHollowQuest);
        var bound=firstSection.Scripts.Single(s=>s.Name=="TLM:Act1Walk").Properties.Where(p=>p.Name=="TLM_RedHollow").ToArray();
        if(original==null){if(bound.Length!=0)throw new InvalidDataException("Red Hollow binding without its greybox");return null;}
        var road=source.Quests.SingleOrDefault(q=>q.EditorID==RedHollowRoad)??throw new InvalidDataException("Red Hollow greybox without its road quest");
        if(bound.Length!=1||bound[0] is not ScriptObjectProperty door||door.Alias!=-1||door.Object.FormKey!=original.FormKey)
            throw new InvalidDataException("First section is not bound to the story master's Red Hollow greybox");
        var ownCell=source.Cells.Records.SelectMany(b=>b.SubBlocks).SelectMany(b=>b.Cells).SingleOrDefault(c=>c.EditorID=="TLM_CELL_RedHollow")
            ??throw new InvalidDataException("Red Hollow own cell missing");
        var interiorRefs=ownCell.Persistent.Select(r=>r.FormKey).ToHashSet();
        var surfaceRefs=RedHollowSurfaceReferences(source).Select(r=>r.FormKey).ToHashSet();
        var clone=original.Duplicate(mod.GetNextFormKey());clone.EditorID=RedHollowClone;
        clone.Name="The Last Meridian - exterior-linked Red Hollow (development)";
        var aliases=clone.Aliases?.OfType<QuestReferenceAlias>().ToArray()??throw new InvalidDataException("Red Hollow aliases missing");
        if(aliases.Length!=99||aliases.Select(a=>a.Name).Distinct().Count()!=99||!RedHollowSites.Keys.All(n=>aliases.Any(a=>a.Name==n)))
            throw new InvalidDataException("Unexpected Red Hollow alias contract");
        var mapping=new List<object>();
        foreach(var a in aliases){
            if(a.Name=="Condemned"){
                if(!a.ForcedReference.IsNull)throw new InvalidDataException("Red Hollow prisoner must remain script-filled; never clone an earlier-road actor");
                continue;
            }
            if(a.Name=="Player"){
                if(a.ForcedReference.IsNull||a.ForcedReference.FormKey.ModKey.FileName.String!="Fallout4.esm")throw new InvalidDataException("Red Hollow load hook must remain on the vanilla player");
                continue;
            }
            if(a.ForcedReference.IsNull||!sourceRefs.TryGetValue(a.ForcedReference.FormKey,out var old)||old.EditorID!="TLM_REF_RH_"+a.Name)
                throw new InvalidDataException("Missing or substituted Red Hollow source placement: "+a.Name);
            if((old.MajorRecordFlagsRaw&0xC00)!=0xC00)throw new InvalidDataException("Red Hollow source is not persistent and initially disabled");
            var sourceKey=old.FormKey;
            if(RedHollowSites.TryGetValue(a.Name!,out var at)){
                if(old is not IPlacedObjectGetter obj)throw new InvalidDataException("Red Hollow Mercy piece must be an object");
                var placed=obj.Duplicate(mod.GetNextFormKey());placed.EditorID="TLM_WS_ST_RH_"+a.Name;
                placed.Position=new P3Float(at.X,at.Y,at.Z);placed.Rotation=new P3Float(0,0,0);placed.MajorRecordFlagsRaw|=0xC00;
                world.TopCell!.Persistent.Add(placed);a.ForcedReference.SetTo(placed.FormKey);
                mapping.Add(new{alias=a.Name,id=a.ID,source=sourceKey.ToString(),reference=placed.FormKey.ToString(),x=at.X,y=at.Y,z=at.Z,exterior=true});
            }else{
                bool exteriorSurface=surfaceRefs.Count>0&&RedHollowSurfaceSites.ContainsKey(a.Name!);
                if(!(exteriorSurface?surfaceRefs:interiorRefs).Contains(sourceKey))throw new InvalidDataException("Red Hollow original outside its declared region: "+a.Name);
                mapping.Add(new{alias=a.Name,id=a.ID,source=sourceKey.ToString(),reference=sourceKey.ToString(),exterior=false});
            }
        }
        var adapter=clone.VirtualMachineAdapter??throw new InvalidDataException("Red Hollow VMAD missing");
        void Remap(ScriptObjectProperty p){if(p.Object.FormKey==original.FormKey)p.Object.SetTo(clone.FormKey);}
        void Script(ScriptEntry s){foreach(var p in s.Properties){if(p is ScriptObjectProperty o)Remap(o);if(p is ScriptObjectListProperty l)foreach(var entry in l.Objects)Remap(entry);}}
        foreach(var s in adapter.Scripts)Script(s);
        foreach(var a in adapter.Aliases){Remap(a.Property);foreach(var s in a.Scripts)Script(s);}
        mod.Quests.Add(clone);door.Object.SetTo(clone.FormKey);
        return new{section=clone.EditorID,sectionForm=clone.FormKey.ToString(),road=road.EditorID,roadForm=road.FormKey.ToString(),references=2,masterCellReferences=95,mapping};
    }

    static void ValidateRedHollow(IFallout4ModGetter addon,IQuestGetter section)
    {
        var clone=addon.Quests.SingleOrDefault(q=>q.EditorID==RedHollowClone);
        var bound=section.VirtualMachineAdapter!.Scripts.Single(s=>s.Name=="TLM:Act1Walk").Properties.Where(p=>p.Name=="TLM_RedHollow").ToArray();
        if(clone==null){if(bound.Length!=0)throw new InvalidDataException("Red Hollow binding without exterior-linked greybox");return;}
        if(bound.Length!=1||bound[0] is not IScriptObjectPropertyGetter door||door.Alias!=-1||door.Object.FormKey!=clone.FormKey)
            throw new InvalidDataException("Exterior first section does not open its Red Hollow controller");
        var aliases=clone.Aliases?.OfType<IQuestReferenceAliasGetter>().ToArray()??throw new InvalidDataException("Red Hollow aliases missing");
        if(aliases.Length!=99||aliases.Select(a=>a.ID).Distinct().Count()!=99)throw new InvalidDataException("Red Hollow alias count/identity mismatch");
        var refs=addon.Worldspaces.Single().TopCell!.Persistent.ToDictionary(p=>p.FormKey);
        foreach(var a in aliases){
            if(a.Name=="Condemned"){
                if(!a.ForcedReference.IsNull)throw new InvalidDataException("Red Hollow prisoner alias unexpectedly forced");
                continue;
            }
            if(a.Name=="Player"){
                if(a.ForcedReference.IsNull||a.ForcedReference.FormKey.ModKey.FileName.String!="Fallout4.esm")throw new InvalidDataException("Red Hollow player hook unexpectedly rebound");
                continue;
            }
            if(a.ForcedReference.IsNull)throw new InvalidDataException("Red Hollow alias unfilled");
            if(RedHollowSites.TryGetValue(a.Name!,out var at)){
                if(!refs.TryGetValue(a.ForcedReference.FormKey,out var piece)||piece is not IPlacedObjectGetter obj||obj.EditorID!="TLM_WS_ST_RH_"+a.Name||obj.Position!=new P3Float(at.X,at.Y,at.Z)||(obj.MajorRecordFlagsRaw&0xC00)!=0xC00)
                    throw new InvalidDataException("Red Hollow Mercy binding/placement mismatch: "+a.Name);
            }else if(a.ForcedReference.FormKey.ModKey!=StoryMaster)throw new InvalidDataException("Red Hollow interior alias left the story master");
        }
        var vmad=clone.VirtualMachineAdapter??throw new InvalidDataException("Red Hollow VMAD missing");
        var ids=aliases.Select(a=>a.ID).ToHashSet();
        if(vmad.Aliases.Any(a=>a.Property.Object.FormKey!=clone.FormKey||!ids.Contains((uint)a.Property.Alias)||a.Scripts.Any(s=>s.Name!="TLM:RedHollowTalk")))throw new InvalidDataException("Red Hollow alias script ownership mismatch");
        var walk=vmad.Scripts.Single(s=>s.Name=="TLM:RedHollowWalk");
        foreach(var p in walk.Properties){
            if(p is IScriptObjectPropertyGetter o&&((o.Alias>=0&&o.Object.FormKey!=clone.FormKey)||(o.Alias<0&&o.Object.FormKey.ModKey!=StoryMaster)))throw new InvalidDataException("Red Hollow scalar binding mismatch: "+p.Name);
            if(p is IScriptObjectListPropertyGetter l&&l.Objects.Any(o=>o.Object.FormKey.ModKey!=(p.Name=="CastInto"?StoryMaster:addon.ModKey)))throw new InvalidDataException("Red Hollow alias-list binding mismatch: "+p.Name);
        }
        if(addon.Quests.Any(q=>q.EditorID==RedHollowRoad))throw new InvalidDataException("Red Hollow road duplicated into exterior");
    }
}
