using Mutagen.Bethesda;
using Mutagen.Bethesda.Fallout4;
using Mutagen.Bethesda.Plugins;
using Mutagen.Bethesda.Plugins.Records;
using Noggog;
using System.Text.Json;

// GREENWATER-STORY-001. The exterior builder needs the game's own master, which is not in the repository or in
// the cloud. This runs ONLY its story-cloning step (WorldStory.Add) and its own check of the written file
// (WorldStory.Validate) on a story plugin, in an otherwise EMPTY world: no terrain, no scenery, no master.
//
//   WorldSliceBuilder --story-clone-check <TheLastMeridian.esp> <new-output-directory> [--damage <kind>]
//
// With --damage the story plugin is damaged in memory first (never on disk), in one named way, so that a test
// can see the cloner refuse it.
//
// It is for a plugin built against a generated stand-in master (tools/papyrus_sim/test_greenwater_world_clone.py).
// It shows that the cloning code keeps the bindings it must. It is NOT the exterior build: no placement, route,
// collision or prop check of Program.cs runs here, and nothing it writes is a candidate artifact.
public static class StoryCloneCheck
{
    static readonly string[] Damages={"greenwater-binding-removed","greenwater-binding-to-another-quest","greenwater-binding-as-alias",
        "briefing-binding-removed","greenwater-alias-dropped","greenwater-placement-missing","road-quest-missing",
        // Not damage: a source as it was before the road existed (neither quest, no binding). It must clone as it did.
        "source-without-greenwater","night-mail-binding-removed","night-mail-binding-to-another-quest","night-mail-binding-as-alias",
        "night-mail-alias-dropped","night-mail-placement-missing","night-mail-placement-substituted","night-mail-road-missing",
        "night-mail-cell-missing","night-mail-interior-moved","source-without-night-mail","red-hollow-binding-removed","red-hollow-binding-to-another-quest","red-hollow-alias-dropped","red-hollow-placement-missing","red-hollow-road-missing","red-hollow-cell-missing","red-hollow-prisoner-forced","source-without-red-hollow","relief-ledger-missing","relief-control-substituted","relief-model-missing","relief-model-oversized","relief-ledger-binding-wrong",
        "fair-binding-removed","fair-ledger-missing","fair-cell-missing","fair-entry-substituted","fair-case-alias-substituted","fair-original-cast-forced","fair-dedicated-cast-substituted","fair-case-model-missing"};

    static IFallout4ModGetter Damaged(string story,string damage)
    {
        var bad=Fallout4Mod.CreateFromBinary(story,Fallout4Release.Fallout4);
        var a1=bad.Quests.Single(q=>q.EditorID=="TLM_A1");
        var walk=a1.VirtualMachineAdapter!.Scripts.Single(s=>s.Name=="TLM:Act1Walk");
        ScriptObjectProperty Prop(string name)=>walk.Properties.OfType<ScriptObjectProperty>().Single(p=>p.Name==name);
        var gw=bad.Quests.Single(q=>q.EditorID=="TLM_GW");
        var nm=bad.Quests.SingleOrDefault(q=>q.EditorID=="TLM_NM");
        var rh=bad.Quests.SingleOrDefault(q=>q.EditorID=="TLM_RH");
        void RemoveFair(){
            var fair=bad.Quests.SingleOrDefault(q=>q.EditorID=="TLM_MQ03");if(fair==null)return;
            walk.Properties.Remove(Prop("TLM_FourFlags"));walk.Properties.Remove(Prop("TLM_FourFlagsEntry"));
            bad.Quests.Remove(fair.FormKey);bad.Quests.Remove(bad.Quests.Single(q=>q.EditorID=="TLM_FF_Entry").FormKey);
            gw.VirtualMachineAdapter!.Scripts.Single(s=>s.Name=="TLM:GreenwaterWalk").Properties.RemoveAll(p=>p.Name=="TLM_FourFlags");
        }
        void RemoveRedHollow(){RemoveFair();if(rh==null)return;walk.Properties.Remove(Prop("TLM_RedHollow"));bad.Quests.Remove(rh.FormKey);bad.Quests.Remove(bad.Quests.Single(q=>q.EditorID=="TLM_MQ02C").FormKey);}
        void RemoveNightMail(){RemoveRedHollow();walk.Properties.Remove(Prop("TLM_NightMail"));bad.Quests.Remove(nm!.FormKey);bad.Quests.Remove(bad.Quests.Single(q=>q.EditorID=="TLM_MQ02A").FormKey);}
        switch(damage){
            case "fair-binding-removed":walk.Properties.Remove(Prop("TLM_FourFlagsEntry"));break;
            case "fair-ledger-missing":bad.Quests.Remove(bad.Quests.Single(q=>q.EditorID=="TLM_MQ03").FormKey);break;
            case "fair-cell-missing":foreach(var b in bad.Cells.Records)foreach(var s in b.SubBlocks)s.Cells.RemoveAll(c=>c.EditorID=="TLM_CELL_FourFlags");break;
            case "fair-entry-substituted":bad.Quests.Single(q=>q.EditorID=="TLM_FF_Entry").Aliases!.OfType<QuestReferenceAlias>().Single(a=>a.Name=="Entry").ForcedReference.SetTo(bad.Quests.Single(q=>q.EditorID=="TLM_FF_Entry").Aliases!.OfType<QuestReferenceAlias>().Single(a=>a.Name=="MercyReturn").ForcedReference.FormKey);break;
            case "fair-case-alias-substituted":
                var fairQuest=bad.Quests.Single(q=>q.EditorID=="TLM_MQ03");
                fairQuest.Aliases!.OfType<QuestReferenceAlias>().Single(a=>a.Name=="OriginalCase").ForcedReference.SetTo(fairQuest.Aliases!.OfType<QuestReferenceAlias>().Single(a=>a.Name=="OriginalSilver").ForcedReference.FormKey);break;
            case "fair-original-cast-forced":bad.Quests.Single(q=>q.EditorID=="TLM_MQ03").Aliases!.OfType<QuestReferenceAlias>().Single(a=>a.Name=="Pritchard").ForcedReference.SetTo(((QuestReferenceAlias)a1.Aliases![18]).ForcedReference.FormKey);break;
            case "fair-dedicated-cast-substituted":
                var fairCast=bad.Quests.Single(q=>q.EditorID=="TLM_MQ03").Aliases!.OfType<QuestReferenceAlias>().ToArray();
                fairCast.Single(a=>a.Name=="Brigg").ForcedReference.SetTo(fairCast.Single(a=>a.Name=="Grey").ForcedReference.FormKey);break;
            case "fair-case-model-missing":bad.Books.Single(b=>b.EditorID=="TLM_BOOK_FF_CourierCase").Model=null;break;
            case "red-hollow-binding-removed":walk.Properties.Remove(Prop("TLM_RedHollow"));break;
            case "red-hollow-binding-to-another-quest":Prop("TLM_RedHollow").Object.SetTo(gw.FormKey);break;
            case "red-hollow-alias-dropped":rh!.Aliases!.RemoveAt(0);break;
            case "red-hollow-placement-missing":((QuestReferenceAlias)rh!.Aliases![0]).ForcedReference.SetToNull();break;
            case "red-hollow-road-missing":bad.Quests.Remove(bad.Quests.Single(q=>q.EditorID=="TLM_MQ02C").FormKey);break;
            case "red-hollow-cell-missing":foreach(var b in bad.Cells.Records)foreach(var s in b.SubBlocks)s.Cells.RemoveAll(c=>c.EditorID=="TLM_CELL_RedHollow");break;
            case "red-hollow-prisoner-forced":rh!.Aliases!.OfType<QuestReferenceAlias>().Single(a=>a.Name=="Condemned").ForcedReference.SetTo(((QuestReferenceAlias)rh.Aliases[0]).ForcedReference.FormKey);break;
            case "source-without-red-hollow":RemoveRedHollow();break;
            case "greenwater-binding-removed":walk.Properties.Remove(Prop("TLM_Greenwater"));break;
            case "greenwater-binding-to-another-quest":Prop("TLM_Greenwater").Object.SetTo(bad.Quests.Single(q=>q.EditorID=="TLM_SQ01").FormKey);break;
            case "greenwater-binding-as-alias":Prop("TLM_Greenwater").Alias=0;break;
            case "briefing-binding-removed":walk.Properties.Remove(Prop("TLM_MercyBriefing"));break;
            case "greenwater-alias-dropped":gw.Aliases!.RemoveAt(gw.Aliases.Count-1);break;
            case "greenwater-placement-missing":((QuestReferenceAlias)gw.Aliases![3]).ForcedReference.SetToNull();break;
            case "road-quest-missing":bad.Quests.Remove(bad.Quests.Single(q=>q.EditorID=="TLM_MQ02B").FormKey);break;
            case "source-without-greenwater":
                if(nm!=null)RemoveNightMail();
                walk.Properties.Remove(Prop("TLM_Greenwater"));
                bad.Quests.Remove(gw.FormKey);bad.Quests.Remove(bad.Quests.Single(q=>q.EditorID=="TLM_MQ02B").FormKey);break;
            case "night-mail-binding-removed":walk.Properties.Remove(Prop("TLM_NightMail"));break;
            case "night-mail-binding-to-another-quest":Prop("TLM_NightMail").Object.SetTo(gw.FormKey);break;
            case "night-mail-binding-as-alias":Prop("TLM_NightMail").Alias=0;break;
            case "night-mail-alias-dropped":nm!.Aliases!.RemoveAt(nm.Aliases.Count-1);break;
            case "night-mail-placement-missing":((QuestReferenceAlias)nm!.Aliases![3]).ForcedReference.SetToNull();break;
            case "night-mail-placement-substituted":((QuestReferenceAlias)nm!.Aliases![3]).ForcedReference.SetTo(((QuestReferenceAlias)nm.Aliases[4]).ForcedReference.FormKey);break;
            case "night-mail-road-missing":bad.Quests.Remove(bad.Quests.Single(q=>q.EditorID=="TLM_MQ02A").FormKey);break;
            case "night-mail-cell-missing":foreach(var b in bad.Cells.Records)foreach(var s in b.SubBlocks)s.Cells.RemoveAll(c=>c.EditorID=="TLM_CELL_NightMail");break;
            case "night-mail-interior-moved":
                var cells=bad.Cells.Records.SelectMany(b=>b.SubBlocks).SelectMany(s=>s.Cells).ToArray();
                var own=cells.Single(c=>c.EditorID=="TLM_CELL_NightMail");var piece=own.Persistent.First(r=>r.EditorID=="TLM_REF_NM_Lockridge");
                own.Persistent.Remove(piece);cells.Single(c=>c.EditorID=="QASmoke").Persistent.Add(piece);break;
            case "source-without-night-mail":RemoveNightMail();break;
            case "relief-ledger-missing":bad.Quests.Remove(bad.Quests.Single(q=>q.EditorID=="TLM_GW_Relief").FormKey);break;
            case "relief-control-substituted":
                var storeAlias=gw.Aliases!.OfType<QuestReferenceAlias>().Single(a=>a.Name=="ReliefStores");
                storeAlias.ForcedReference.SetTo(gw.Aliases!.OfType<QuestReferenceAlias>().Single(a=>a.Name=="ReliefSupply").ForcedReference.FormKey);break;
            case "relief-model-missing":bad.Activators.Single(a=>a.EditorID=="TLM_ACTI_GW_ReliefStores").Model=null;break;
            case "relief-model-oversized":bad.Activators.Single(a=>a.EditorID=="TLM_ACTI_GW_ReliefStores").ObjectBounds.First=new P3Int16(-1000,-1000,0);break;
            case "relief-ledger-binding-wrong":gw.VirtualMachineAdapter!.Scripts.Single(s=>s.Name=="TLM:GreenwaterWalk").Properties.OfType<ScriptObjectProperty>().Single(p=>p.Name=="TLM_Relief").Object.SetTo(gw.FormKey);break;
            default:throw new ArgumentException("unknown damage: "+damage+"; one of "+string.Join(", ",Damages));
        }
        return bad;
    }

    public static int Run(string storyPath,string outputPath,string? damage=null)
    {
        var story=Path.GetFullPath(storyPath);var output=Path.GetFullPath(outputPath);
        if(!File.Exists(story)||!Path.GetFileName(story).Equals("TheLastMeridian.esp",StringComparison.OrdinalIgnoreCase)){Console.Error.WriteLine("Story source must be an existing TheLastMeridian.esp.");return 2;}
        if(File.Exists(output)||(Directory.Exists(output)&&Directory.EnumerateFileSystemEntries(output).Any())){Console.Error.WriteLine("Output must be a new or empty directory.");return 2;}
        var storyDirectory=Path.GetDirectoryName(story)!;
        if(output.Equals(storyDirectory,StringComparison.Ordinal)||output.StartsWith(storyDirectory+Path.DirectorySeparatorChar,StringComparison.Ordinal)){Console.Error.WriteLine("Output must stay outside the story-source input directory.");return 2;}
        IFallout4ModGetter template;
        try{template=damage==null?Fallout4Mod.CreateFromBinaryOverlay(story,Fallout4Release.Fallout4):Damaged(story,damage);}
        catch(ArgumentException e){Console.Error.WriteLine(e.Message);return 2;}
        Directory.CreateDirectory(output);
        var mod=new Fallout4Mod(ModKey.FromNameAndExtension("TLMWorldSlice.esp"),Fallout4Release.Fallout4);
        var world=mod.Worldspaces.AddNew("TLM_WS_Meridian");
        world.TopCell=new Cell(mod.GetNextFormKey(),Fallout4Release.Fallout4){EditorID="TLM_WS_Persistent",MajorRecordFlagsRaw=0x400};
        var block=new WorldspaceBlock{BlockNumberX=0,BlockNumberY=0,GroupType=GroupTypeEnum.ExteriorCellBlock};
        var sub=new WorldspaceSubBlock{BlockNumberX=0,BlockNumberY=0,GroupType=GroupTypeEnum.ExteriorCellSubBlock};
        world.SubCells.Add(block);block.Items.Add(sub);
        var cell=new Cell(mod.GetNextFormKey(),Fallout4Release.Fallout4){EditorID="TLM_WS_Clearing",Grid=new CellGrid{Point=new P2Int(0,0)}};
        sub.Items.Add(cell);
        try{WorldStory.Add(mod,world,cell,template);WorldStory.CompleteReliefControls(mod,world,template);WorldStory.CompleteFourFlagsEntry(mod,world,template);}
        catch(InvalidDataException e){Console.Error.WriteLine("REFUSED: "+e.Message);return 1;}
        var plugin=Path.Combine(output,"TLMWorldSlice.esp");
        mod.BeginWrite.ToPath(plugin).WithNoLoadOrder().WithExtraIncludedMasters(ModKey.FromNameAndExtension("Fallout4.esm"),template.ModKey).Write();
        using var read=Fallout4Mod.CreateFromBinaryOverlay(plugin,Fallout4Release.Fallout4);
        try{WorldStory.Validate(read);}
        catch(InvalidDataException e){Console.Error.WriteLine("REFUSED on read-back: "+e.Message);return 1;}
        var persistent=read.Worldspaces.Single().TopCell!.Persistent.ToDictionary(p=>p.FormKey);
        var masterRefs=template.Cells.Records.SelectMany(b=>b.SubBlocks).SelectMany(s=>s.Cells).SelectMany(c=>c.Persistent.Concat(c.Temporary)).ToDictionary(r=>r.FormKey);
        foreach(var r in WorldStory.RedHollowSurfaceReferences(template))masterRefs.Add(r.FormKey,r);
        object Quest(string id){
            var q=read.Quests.SingleOrDefault(x=>x.EditorID==id);
            if(q==null)return new{present=false};
            var names=template.Quests.ToDictionary(x=>x.FormKey,x=>x.EditorID);
            string Where(FormKey k)=>k.ModKey==read.ModKey?(read.Quests.FirstOrDefault(x=>x.FormKey==k)?.EditorID??k.ToString()):(names.TryGetValue(k,out var n)?n+" in "+k.ModKey.FileName:k.ToString());
            var script=q.VirtualMachineAdapter!.Scripts.First();
            return new{present=true,form=q.FormKey.ToString(),script=script.Name,properties=script.Properties.Count,
                aliases=q.Aliases!.OfType<IQuestReferenceAliasGetter>().Select(a=>{
                    var key=a.ForcedReference.FormKey;
                    if(key.IsNull)return (object)new{name=a.Name,id=a.ID,reference="script-filled",form="",owner="",x=0f,y=0f,z=0f,actor=false,flags=0u};
                    if(key.ModKey.FileName.String=="Fallout4.esm")return (object)new{name=a.Name,id=a.ID,reference="Player",form=key.ToString(),owner="Fallout4.esm",x=0f,y=0f,z=0f,actor=true,flags=0u};
                    var r=persistent.TryGetValue(key,out var own)?own:masterRefs[key];
                    P3Float pos=r switch {IPlacedNpcGetter n=>n.Position,IPlacedObjectGetter o=>o.Position,_=>default};
                    return new{name=a.Name,id=a.ID,reference=r.EditorID,form=r.FormKey.ToString(),owner=r.FormKey.ModKey.FileName.String,x=pos.X,y=pos.Y,z=pos.Z,actor=r is IPlacedNpcGetter,flags=r.MajorRecordFlagsRaw};}).ToArray(),
                aliasScripts=q.VirtualMachineAdapter.Aliases.Select(a=>new{alias=a.Property.Alias,on=Where(a.Property.Object.FormKey),scripts=a.Scripts.Select(s=>s.Name).ToArray()}).ToArray(),
                forms=script.Properties.OfType<IScriptObjectPropertyGetter>().Where(p=>p.Alias<0).ToDictionary(p=>p.Name,p=>Where(p.Object.FormKey)),
                ownAliases=script.Properties.OfType<IScriptObjectPropertyGetter>().Where(p=>p.Alias>=0).ToDictionary(p=>p.Name,p=>Where(p.Object.FormKey)+" alias "+p.Alias),
                lists=script.Properties.OfType<IScriptObjectListPropertyGetter>().ToDictionary(p=>p.Name,p=>p.Objects.Select(o=>Where(o.Object.FormKey)+" alias "+o.Alias).ToArray())};
        }
        Console.WriteLine(JsonSerializer.Serialize(new{
            what="Story-cloning step only, on a story plugin in an empty world. Not the exterior build.",
            masters=read.ModHeader.MasterReferences.Select(m=>m.Master.ToString()).ToArray(),
            quests=read.Quests.Select(q=>q.EditorID).ToArray(),
            persistentReferences=persistent.Count,
            firstSection=Quest("TLM_WS_A1"),greenwater=Quest("TLM_WS_GW"),nightMail=Quest("TLM_WS_NM"),redHollow=Quest("TLM_WS_RH"),
            fourFlags=Quest("TLM_WS_FF_Entry"),fourFlagsSites=WorldStory.FourFlagsSites.ToDictionary(s=>s.Key,s=>new[]{s.Value.X,s.Value.Y,s.Value.Z}),
            redHollowSites=WorldStory.RedHollowSites.ToDictionary(s=>s.Key,s=>new[]{s.Value.X,s.Value.Y,s.Value.Z}),
            nightMailSites=WorldStory.NightMailSites.ToDictionary(s=>s.Key,s=>new[]{s.Value.X,s.Value.Y,s.Value.Z}),
            sites=WorldStory.GreenwaterSites.ToDictionary(s=>s.Key,s=>new[]{s.Value.X,s.Value.Y,s.Value.Z})},new JsonSerializerOptions{WriteIndented=true}));
        return 0;
    }
}
