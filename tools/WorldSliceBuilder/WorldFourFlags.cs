using Mutagen.Bethesda;
using Mutagen.Bethesda.Fallout4;
using Mutagen.Bethesda.Plugins;
using Noggog;

public static partial class WorldStory
{
    public static readonly Dictionary<string,(float X,float Y,float Z)> FourFlagsSites=new(){
        ["Entry"]=(3820,3100,12),["MercyReturn"]=(3820,3070,32)
    };
    public static readonly (float X,float Y) FourFlagsApproach=(3820,3000);

    public static void AuditFourFlagsApproach(IEnumerable<(string Id,float MinX,float MaxX,float MinY,float MaxY)> bounds,
        float startX,float startY,float entryX,float entryY,float returnX,float returnY)
    {
        var obstacles=bounds.Where(p=>!p.Id.Contains("Floor",StringComparison.Ordinal)).ToArray();
        void Check(float x,float y){
            if(x<96||x>4000||y<96||y>4000)throw new InvalidDataException("Fair entry outside supported flat LAND");
            foreach(var p in obstacles){
                float dx=MathF.Max(MathF.Max(p.MinX-x,0),x-p.MaxX),dy=MathF.Max(MathF.Max(p.MinY-y,0),y-p.MaxY);
                if(dx*dx+dy*dy<96*96)throw new InvalidDataException("Fair entry192-unit approach blocked: "+p.Id);
            }
        }
        for(int tick=0;tick<=100;tick++)Check(startX+(entryX-startX)*tick/100f,startY+(entryY-startY)*tick/100f);
        Check(returnX,returnY);
    }
    const string FairMaster="TLM_MQ03",FairEntry="TLM_FF_Entry",FairClone="TLM_WS_FF_Entry";

    public static object? CompleteFourFlagsEntry(Fallout4Mod mod,Worldspace world,IFallout4ModGetter source)
    {
        var section=mod.Quests.Single(q=>q.EditorID=="TLM_WS_A1");
        var sectionWalk=section.VirtualMachineAdapter!.Scripts.Single(s=>s.Name=="TLM:Act1Walk");
        var entryBinding=sectionWalk.Properties.Where(p=>p.Name=="TLM_FourFlagsEntry").ToArray();
        var fairBinding=sectionWalk.Properties.Where(p=>p.Name=="TLM_FourFlags").ToArray();
        var original=source.Quests.SingleOrDefault(q=>q.EditorID==FairEntry);
        if(original==null){
            if(entryBinding.Length!=0||fairBinding.Length!=0||source.Quests.Any(q=>q.EditorID==FairMaster))throw new InvalidDataException("Partial Four Flags source without entry adapter");
            return null; // genuine immutable earlier source remains supported
        }
        var master=source.Quests.SingleOrDefault(q=>q.EditorID==FairMaster)??throw new InvalidDataException("Fair entry without authoritative MQ03");
        if(entryBinding.Length!=1||entryBinding[0] is not ScriptObjectProperty door||door.Alias!=-1||door.Object.FormKey!=original.FormKey||
           fairBinding.Length!=1||fairBinding[0] is not ScriptObjectProperty ledger||ledger.Alias!=-1||ledger.Object.FormKey!=master.FormKey)
            throw new InvalidDataException("Opened first section must bind exact master fair and entry adapter");
        var cell=source.Cells.Records.SelectMany(b=>b.SubBlocks).SelectMany(b=>b.Cells).SingleOrDefault(c=>c.EditorID=="TLM_CELL_FourFlags")
            ??throw new InvalidDataException("Four Flags own cell missing");
        var own=cell.Persistent.ToDictionary(p=>p.EditorID??"",p=>p);
        var caseRef=own.GetValueOrDefault("TLM_REF_FF_OriginalCase") as IPlacedObjectGetter;
        var silverRef=own.GetValueOrDefault("TLM_REF_FF_OriginalSilver") as IPlacedObjectGetter;
        if(caseRef==null||silverRef==null||caseRef.FormKey==silverRef.FormKey||caseRef.Base.FormKey==silverRef.Base.FormKey||
           !source.Books.Any(b=>b.FormKey==caseRef.Base.FormKey&&b.EditorID=="TLM_BOOK_FF_CourierCase")||
           !source.MiscItems.Any(b=>b.FormKey==silverRef.Base.FormKey&&b.EditorID=="TLM_MISC_FF_Silver"))
            throw new InvalidDataException("Original courier case and spent silver must be distinct exact physical references/bases");
        foreach(var pair in new[]{("OriginalCase",caseRef.FormKey),("OriginalSilver",silverRef.FormKey)}){
            var a=master.Aliases!.OfType<IQuestReferenceAliasGetter>().SingleOrDefault(a=>a.Name==pair.Item1);
            if(a==null||a.ForcedReference.FormKey!=pair.Item2)throw new InvalidDataException("Master original-reference alias substituted: "+pair.Item1);
        }
        var book=source.Books.Single(b=>b.FormKey==caseRef.Base.FormKey);
        var cartridge=source.MiscItems.Single(b=>b.FormKey==silverRef.Base.FormKey);
        if(string.IsNullOrWhiteSpace(book.Model?.File?.ToString())||string.IsNullOrWhiteSpace(cartridge.Model?.File?.ToString()))
            throw new InvalidDataException("Original fair evidence needs source world models");
        if(master.VirtualMachineAdapter?.Scripts.Select(s=>s.Name).OrderBy(s=>s).SequenceEqual(new[]{"TLM:FourFlagsWalk","TLM:MQ03Quest"})!=true)
            throw new InvalidDataException("Four Flags must retain one master ledger and presentation script");
        foreach(var name in new[]{"Pritchard","Talbot","Pike","Belden"}){
            var alias=master.Aliases!.OfType<IQuestReferenceAliasGetter>().SingleOrDefault(a=>a.Name==name);
            if(alias==null||!alias.ForcedReference.IsNull)throw new InvalidDataException("Original visitor must remain script-filled, never duplicated: "+name);
        }
        var actorKeys=new HashSet<FormKey>();
        foreach(var name in new[]{"Whitcomb","Brigg","Grey","Flint","Juno"}){
            if(!own.TryGetValue("TLM_REF_FF_"+name,out var placed)||placed is not IPlacedNpcGetter npc||!actorKeys.Add(npc.FormKey)||
               !source.Npcs.Any(n=>n.FormKey==npc.Base.FormKey&&n.EditorID=="TLM_NPC_FF_"+name))throw new InvalidDataException("Dedicated fair cast identity mismatch: "+name);
            var alias=master.Aliases!.OfType<IQuestReferenceAliasGetter>().SingleOrDefault(a=>a.Name==name);
            if(alias==null||alias.ForcedReference.FormKey!=npc.FormKey)throw new InvalidDataException("Dedicated fair actor alias substituted: "+name);
        }
        var allRefs=source.Cells.Records.SelectMany(b=>b.SubBlocks).SelectMany(b=>b.Cells).SelectMany(c=>c.Persistent.Concat(c.Temporary)).ToDictionary(r=>r.FormKey);
        var clone=original.Duplicate(mod.GetNextFormKey());clone.EditorID=FairClone;clone.Name="Four Flags exterior entry only (development)";
        var aliases=clone.Aliases?.OfType<QuestReferenceAlias>().ToArray()??throw new InvalidDataException("Fair entry aliases missing");
        if(aliases.Length!=2||aliases.Select(a=>a.Name).Distinct().Count()!=2||!FourFlagsSites.Keys.All(n=>aliases.Any(a=>a.Name==n)))
            throw new InvalidDataException("Fair entry must contain exactly two dedicated controls");
        var rows=new List<object>();
        foreach(var alias in aliases){
            if(alias.ForcedReference.IsNull||!allRefs.TryGetValue(alias.ForcedReference.FormKey,out var old)||old is not IPlacedObjectGetter obj||obj.EditorID!="TLM_REF_FF_"+alias.Name||(obj.MajorRecordFlagsRaw&0xC00)!=0xC00)
                throw new InvalidDataException("Fair entry source identity/persistence mismatch: "+alias.Name);
            if(alias.Name=="Entry"){
                var act=source.Activators.SingleOrDefault(a=>a.FormKey==obj.Base.FormKey&&a.EditorID=="TLM_ACTI_FF_Entry");
                var model=act?.Model?.File?.ToString();
                if(act==null||string.IsNullOrWhiteSpace(model)||act.ObjectBounds.First.X < -64||act.ObjectBounds.First.Y < -64||act.ObjectBounds.First.Z < -4||act.ObjectBounds.Second.X>64||act.ObjectBounds.Second.Y>64||act.ObjectBounds.Second.Z>24)
                    throw new InvalidDataException("Fair entry needs an audited paper-control model/bound");
            }
            var at=FourFlagsSites[alias.Name!];var placed=obj.Duplicate(mod.GetNextFormKey());
            placed.EditorID="TLM_WS_ST_FF_"+alias.Name;placed.Position=new P3Float(at.X,at.Y,at.Z);placed.Rotation=new P3Float(0,0,0);placed.MajorRecordFlagsRaw|=0xC00;
            world.TopCell!.Persistent.Add(placed);alias.ForcedReference.SetTo(placed.FormKey);
            rows.Add(new{alias=alias.Name,id=alias.ID,source=old.FormKey.ToString(),reference=placed.FormKey.ToString(),x=at.X,y=at.Y,z=at.Z});
        }
        var vmad=clone.VirtualMachineAdapter??throw new InvalidDataException("Fair entry script adapter missing");
        void Remap(ScriptObjectProperty p){if(p.Object.FormKey==original.FormKey)p.Object.SetTo(clone.FormKey);}
        foreach(var script in vmad.Scripts.Concat(vmad.Aliases.SelectMany(a=>a.Scripts)))foreach(var p in script.Properties.OfType<ScriptObjectProperty>())Remap(p);
        foreach(var a in vmad.Aliases)Remap(a.Property);
        mod.Quests.Add(clone);door.Object.SetTo(clone.FormKey);
        return new{policy="Only entry adapter and two controls appended after every prior allocation; master MQ03/cell/case/cast are never cloned",quest=clone.EditorID,master=master.FormKey.ToString(),references=rows};
    }

    public static object AuditFourFlagsInterior(IFallout4ModGetter source,IFallout4ModGetter vanilla)
    {
        var cell=source.Cells.Records.SelectMany(b=>b.SubBlocks).SelectMany(b=>b.Cells).Single(c=>c.EditorID=="TLM_CELL_FourFlags");
        var floor=vanilla.Statics.SingleOrDefault(s=>s.EditorID=="workshop_ShackMidFloor01B")??throw new InvalidDataException("Fair floor static missing from typed master");
        var lo=floor.ObjectBounds.First;var hi=floor.ObjectBounds.Second;
        if(lo.X!=-128||lo.Y!=-128||lo.Z!=-14||hi.X!=128||hi.Y!=128||hi.Z!=0||string.IsNullOrWhiteSpace(floor.Model?.File?.ToString()))
            throw new InvalidDataException("Fair stock-floor model/bounds differ from the supported grid");
        var floors=cell.Persistent.OfType<IPlacedObjectGetter>().Where(r=>(r.EditorID??"").StartsWith("TLM_REF_FF_Floor",StringComparison.Ordinal)).ToArray();
        if(floors.Length!=63)throw new InvalidDataException("Fair needs exactly its own63floor tiles");
        for(int x=0;x<9;x++)for(int y=0;y<7;y++){
            var tile=floors.SingleOrDefault(r=>r.EditorID==$"TLM_REF_FF_Floor{x}{y}");
            if(tile==null||tile.Base.FormKey!=floor.FormKey||tile.Position!=new P3Float(x*256,y*256,0)||((uint)tile.MajorRecordFlagsRaw&0x800)!=0)
                throw new InvalidDataException("Unsupported/missing fair floor tile");
        }
        foreach(var r in cell.Persistent.Where(r=>!(r.EditorID??"").StartsWith("TLM_REF_FF_Floor",StringComparison.Ordinal))){
            var p=r switch{IPlacedObjectGetter o=>o.Position,IPlacedNpcGetter n=>n.Position,_=>throw new InvalidDataException("Unknown fair placement type")};
            if(p.X<0||p.X>2048||p.Y<0||p.Y>1536||p.Z<12||p.Z>32)throw new InvalidDataException("Fair station outside supported stock-floor grid: "+r.EditorID);
        }
        var courierBook=source.Books.Single(b=>b.EditorID=="TLM_BOOK_FF_CourierCase");
        return new{method="Typed actual master floor model/bounds and contiguous9x7source placement readback; no Havok/navmesh/native proof",floor=floor.FormKey.ToString(),model=floor.Model!.File.ToString(),tiles=63,surfaceZ=0,minX=-128,minY=-128,maxX=2176,maxY=1664,courierBookText=courierBook.BookText?.ToString()};
    }

    static void ValidateFourFlags(IFallout4ModGetter addon,IQuestGetter section)
    {
        var walk=section.VirtualMachineAdapter!.Scripts.Single(s=>s.Name=="TLM:Act1Walk");
        var doors=walk.Properties.Where(p=>p.Name=="TLM_FourFlagsEntry").ToArray();
        var ledgers=walk.Properties.Where(p=>p.Name=="TLM_FourFlags").ToArray();
        var clone=addon.Quests.SingleOrDefault(q=>q.EditorID==FairClone);
        if(clone==null){if(doors.Length!=0||ledgers.Length!=0)throw new InvalidDataException("Fair binding without appended entry adapter");return;}
        if(addon.Quests.Any(q=>q.EditorID==FairMaster)||addon.Cells.Records.Any())throw new InvalidDataException("Fair master/cell must never be duplicated into exterior");
        if(doors.Length!=1||doors[0] is not IScriptObjectPropertyGetter door||door.Alias!=-1||door.Object.FormKey!=clone.FormKey||
           ledgers.Length!=1||ledgers[0] is not IScriptObjectPropertyGetter ledger||ledger.Alias!=-1||ledger.Object.FormKey.ModKey!=StoryMaster)
            throw new InvalidDataException("Fair exterior owner/ledger binding mismatch");
        var aliases=clone.Aliases?.OfType<IQuestReferenceAliasGetter>().ToArray()??throw new InvalidDataException("Fair adapter aliases missing");
        if(aliases.Length!=2||aliases.Select(a=>a.ID).Distinct().Count()!=2)throw new InvalidDataException("Fair adapter aliases must remain distinct");
        var refs=addon.Worldspaces.Single().TopCell!.Persistent.ToDictionary(r=>r.FormKey);
        foreach(var alias in aliases){
            if(!FourFlagsSites.TryGetValue(alias.Name??"",out var at)||!refs.TryGetValue(alias.ForcedReference.FormKey,out var r)||r is not IPlacedObjectGetter p||p.EditorID!="TLM_WS_ST_FF_"+alias.Name||p.Position!=new P3Float(at.X,at.Y,at.Z)||(p.MajorRecordFlagsRaw&0xC00)!=0xC00)
                throw new InvalidDataException("Fair appended entry reference mismatch");
        }
        var vmad=clone.VirtualMachineAdapter??throw new InvalidDataException("Fair adapter VMAD missing");
        if(vmad.Scripts.Single().Name!="TLM:FourFlagsEntry"||vmad.Aliases.Any(a=>a.Property.Object.FormKey!=clone.FormKey||a.Scripts.Any(s=>s.Name!="TLM:FourFlagsTalk")))
            throw new InvalidDataException("Fair entry alias/script ownership mismatch");
        var masterProp=vmad.Scripts.Single().Properties.OfType<IScriptObjectPropertyGetter>().Single(p=>p.Name=="FairQuest");
        if(masterProp.Alias!=-1||masterProp.Object.FormKey!=ledger.Object.FormKey)throw new InvalidDataException("Fair entry points at another master ledger");
    }
}
