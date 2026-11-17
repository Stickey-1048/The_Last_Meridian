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
        "nightmail-binding-removed","nightmail-binding-to-another-quest","nightmail-binding-as-alias","nightmail-alias-dropped",
        "nightmail-mercy-placement-missing","nightmail-road-quest-missing","nightmail-source-without-the-second-mercy-piece",
        // Not damage: a source as it was before the road existed (neither quest, no binding). It must clone as it did.
        "source-without-greenwater","source-without-nightmail"};

    static IFallout4ModGetter Damaged(string story,string damage)
    {
        var bad=Fallout4Mod.CreateFromBinary(story,Fallout4Release.Fallout4);
        var a1=bad.Quests.Single(q=>q.EditorID=="TLM_A1");
        var walk=a1.VirtualMachineAdapter!.Scripts.Single(s=>s.Name=="TLM:Act1Walk");
        ScriptObjectProperty Prop(string name)=>walk.Properties.OfType<ScriptObjectProperty>().Single(p=>p.Name==name);
        var gw=bad.Quests.Single(q=>q.EditorID=="TLM_GW");
        var nm=bad.Quests.Single(q=>q.EditorID=="TLM_NM");
        switch(damage){
            case "greenwater-binding-removed":walk.Properties.Remove(Prop("TLM_Greenwater"));break;
            case "greenwater-binding-to-another-quest":Prop("TLM_Greenwater").Object.SetTo(bad.Quests.Single(q=>q.EditorID=="TLM_SQ01").FormKey);break;
            case "greenwater-binding-as-alias":Prop("TLM_Greenwater").Alias=0;break;
            case "briefing-binding-removed":walk.Properties.Remove(Prop("TLM_MercyBriefing"));break;
            case "greenwater-alias-dropped":gw.Aliases!.RemoveAt(gw.Aliases.Count-1);break;
            case "greenwater-placement-missing":((QuestReferenceAlias)gw.Aliases![3]).ForcedReference.SetToNull();break;
            case "road-quest-missing":bad.Quests.Remove(bad.Quests.Single(q=>q.EditorID=="TLM_MQ02B").FormKey);break;
            case "source-without-greenwater":
                walk.Properties.Remove(Prop("TLM_Greenwater"));
                bad.Quests.Remove(gw.FormKey);bad.Quests.Remove(bad.Quests.Single(q=>q.EditorID=="TLM_MQ02B").FormKey);break;
            case "nightmail-binding-removed":walk.Properties.Remove(Prop("TLM_NightMail"));break;
            case "nightmail-binding-to-another-quest":Prop("TLM_NightMail").Object.SetTo(bad.Quests.Single(q=>q.EditorID=="TLM_SQ01").FormKey);break;
            case "nightmail-binding-as-alias":Prop("TLM_NightMail").Alias=0;break;
            case "nightmail-alias-dropped":nm.Aliases!.Remove(nm.Aliases!.OfType<QuestReferenceAlias>().First(a=>a.Name=="MercyReturn"));break;
            case "nightmail-mercy-placement-missing":nm.Aliases!.OfType<QuestReferenceAlias>().First(a=>a.Name=="MercyTravel").ForcedReference.SetToNull();break;
            case "nightmail-road-quest-missing":bad.Quests.Remove(bad.Quests.Single(q=>q.EditorID=="TLM_MQ02A").FormKey);break;
            case "nightmail-source-without-the-second-mercy-piece":nm.Aliases!.OfType<QuestReferenceAlias>().First(a=>a.Name=="MercyReturn").Name="Elsewhere";break;
            case "source-without-nightmail":
                walk.Properties.Remove(Prop("TLM_NightMail"));
                bad.Quests.Remove(nm.FormKey);bad.Quests.Remove(bad.Quests.Single(q=>q.EditorID=="TLM_MQ02A").FormKey);break;
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
        try{WorldStory.Add(mod,world,cell,template);}
        catch(InvalidDataException e){Console.Error.WriteLine("REFUSED: "+e.Message);return 1;}
        var plugin=Path.Combine(output,"TLMWorldSlice.esp");
        mod.BeginWrite.ToPath(plugin).WithNoLoadOrder().WithExtraIncludedMasters(ModKey.FromNameAndExtension("Fallout4.esm"),template.ModKey).Write();
        using var read=Fallout4Mod.CreateFromBinaryOverlay(plugin,Fallout4Release.Fallout4);
        try{WorldStory.Validate(read);}
        catch(InvalidDataException e){Console.Error.WriteLine("REFUSED on read-back: "+e.Message);return 1;}
        var persistent=read.Worldspaces.Single().TopCell!.Persistent.ToDictionary(p=>p.FormKey);
        var storyRefs=template.Cells.Records.SelectMany(b=>b.SubBlocks).SelectMany(b=>b.Cells).SelectMany(c=>c.Persistent.Concat(c.Temporary)).ToDictionary(p=>p.FormKey);
        object Quest(string id){
            var q=read.Quests.SingleOrDefault(x=>x.EditorID==id);
            if(q==null)return new{present=false};
            var names=template.Quests.ToDictionary(x=>x.FormKey,x=>x.EditorID);
            string Where(FormKey k)=>k.ModKey==read.ModKey?(read.Quests.FirstOrDefault(x=>x.FormKey==k)?.EditorID??k.ToString()):(names.TryGetValue(k,out var n)?n+" in "+k.ModKey.FileName:k.ToString());
            var script=q.VirtualMachineAdapter!.Scripts.First();
            return new{present=true,form=q.FormKey.ToString(),script=script.Name,properties=script.Properties.Count,
                aliases=q.Aliases!.OfType<IQuestReferenceAliasGetter>().Select(a=>{
                    // Most of the Night Mail's pieces stay where the story master put them, in its own cell: read from there.
                    var r=persistent.TryGetValue(a.ForcedReference.FormKey,out var mine)?mine:storyRefs[a.ForcedReference.FormKey];
                    P3Float pos=r switch {IPlacedNpcGetter n=>n.Position,IPlacedObjectGetter o=>o.Position,_=>default};
                    return new{name=a.Name,id=a.ID,reference=r.EditorID,x=pos.X,y=pos.Y,z=pos.Z,actor=r is IPlacedNpcGetter,flags=r.MajorRecordFlagsRaw,inAddon=persistent.ContainsKey(a.ForcedReference.FormKey)};}).ToArray(),
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
            firstSection=Quest("TLM_WS_A1"),greenwater=Quest("TLM_WS_GW"),nightMail=Quest("TLM_WS_NM"),
            sites=WorldStory.GreenwaterSites.ToDictionary(s=>s.Key,s=>new[]{s.Value.X,s.Value.Y,s.Value.Z}),
            nightMailSites=WorldStory.NightMailSites.ToDictionary(s=>s.Key,s=>new[]{s.Value.X,s.Value.Y,s.Value.Z})},new JsonSerializerOptions{WriteIndented=true}));
        return 0;
    }
}
