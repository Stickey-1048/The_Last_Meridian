using Mutagen.Bethesda.Fallout4;
using Mutagen.Bethesda.Plugins;
using Noggog;

public static partial class WorldStory
{
    public static readonly string[] RedHollowOriginalAliases="MercyTravel MercyReturn GapArrival MouthArrival CageSurface CageBelow GalleryArrival Gallows Released Custody DornWithdraw Quill Roark Blevins Dorn Rope RopeBroken CourtRecord ReferralSent TollBoard Docket Transcript TollBox Bypass Watch ToMouth ToGap CageControl BelowControl FiringControl BreakControl Roster Gallery FromGallery GalleryLamp CotLamp Silver Shovel Knocking MouthOpen MouthClosed BreakOpen BreakClosed StoneDoor Exit Resolve BodyKey LabelGap LabelMouth LabelCage LabelNine LabelGallery Fall Miner01 Miner02 Miner03 Miner04 Miner05 Miner06 Miner07 Miner08 Miner09 Miner10 Miner11 Below01 Cage01 Surface01 Below02 Cage02 Surface02 Below03 Cage03 Surface03 Below04 Cage04 Surface04 Below05 Cage05 Surface05 Below06 Cage06 Surface06 Below07 Cage07 Surface07 Below08 Cage08 Surface08 Below09 Cage09 Surface09 Below10 Cage10 Surface10 Below11 Cage11 Surface11 Condemned Player".Split(' ');
    public static readonly Dictionary<string,(float X,float Y,float Z)> RedHollowSurfaceSites=new(){
        ["SurfaceFall"]=(2048,896,-700),
        ["GapArrival"]=(256,256,16),
        ["MouthArrival"]=(2304,256,16),
        ["CageSurface"]=(2560,256,16),
        ["Gallows"]=(768,512,16),
        ["Released"]=(1024,256,16),
        ["Custody"]=(512,512,16),
        ["Quill"]=(512,512,16),
        ["Roark"]=(2304,512,16),
        ["Blevins"]=(2816,512,16),
        ["Rope"]=(768,512,120),
        ["RopeBroken"]=(768,512,120),
        ["CourtRecord"]=(576,640,12),
        ["ReferralSent"]=(640,640,12),
        ["TollBoard"]=(128,512,12),
        ["Docket"]=(512,640,12),
        ["Transcript"]=(704,640,12),
        ["TollBox"]=(256,512,12),
        ["Bypass"]=(1280,256,12),
        ["Watch"]=(768,640,12),
        ["ToMouth"]=(1536,256,12),
        ["ToGap"]=(2048,256,12),
        ["CageControl"]=(2560,384,12),
        ["FiringControl"]=(2816,384,56),
        ["CotLamp"]=(3072,512,12),
        ["Silver"]=(3072,640,12),
        ["Shovel"]=(2304,640,12),
        ["Knocking"]=(2304,384,12),
        ["MouthOpen"]=(2560,640,12),
        ["MouthClosed"]=(2560,640,12),
        ["Exit"]=(2176,128,12),
        ["Resolve"]=(2560,128,12),
        ["BodyKey"]=(2944,384,12),
        ["LabelGap"]=(256,64,12),
        ["LabelMouth"]=(2304,64,12),
        ["LabelCage"]=(2560,64,12),
        ["Surface01"]=(2688,768,16),
        ["Surface02"]=(2816,768,16),
        ["Surface03"]=(2944,768,16),
        ["Surface04"]=(2560,896,16),
        ["Surface05"]=(2688,896,16),
        ["Surface06"]=(2816,896,16),
        ["Surface07"]=(2944,896,16),
        ["Surface08"]=(2560,1024,16),
        ["Surface09"]=(2688,1024,16),
        ["Surface10"]=(2816,1024,16),
        ["Surface11"]=(2944,1024,16),
    };
    public static void ValidateRedHollowAliasPrefix(IQuestReferenceAliasGetter[] aliases,bool environment){
        bool guidance=aliases.Any(a=>a.Name=="GuideSheriff");
        if(guidance&&!environment)throw new InvalidDataException("RH report guide requires the accepted environment prefix");
        if(aliases.Length!=(environment?101:99)+(guidance?1:0)||!aliases.Take(99).Select(a=>a.Name).SequenceEqual(RedHollowOriginalAliases)||!aliases.Select(a=>a.ID).SequenceEqual(Enumerable.Range(0,aliases.Length).Select(n=>(uint)n)))throw new InvalidDataException("RH original99alias prefix changed");
        if(environment&&(aliases[99].Name!="SurfaceFall"||aliases[100].Name!="GalleryFall"))throw new InvalidDataException("RH region-fall append changed");
        if(guidance&&(aliases[101].Name!="GuideSheriff"||!aliases[101].ForcedReference.IsNull||aliases[101].Flags!=(AQuestAlias.Flag.Optional|AQuestAlias.Flag.AllowDead|AQuestAlias.Flag.AllowDisabled)))throw new InvalidDataException("RH report guide must be the unprotected script-filled final alias101");
    }
    static void ValidateRedHollowGuideBinding(IQuestGetter quest,IQuestReferenceAliasGetter[] aliases){
        bool guidance=aliases.Any(a=>a.Name=="GuideSheriff");
        var bindings=quest.VirtualMachineAdapter!.Scripts.Single(s=>s.Name=="TLM:RedHollowWalk").Properties.Where(p=>p.Name=="Alias_GuideSheriff").ToArray();
        if(!guidance){if(bindings.Length!=0)throw new InvalidDataException("RH report guide binding without its alias");return;}
        if(bindings.Length!=1||bindings[0] is not IScriptObjectPropertyGetter p||p.Alias!=101||p.Object.FormKey!=quest.FormKey)throw new InvalidDataException("RH report guide binding is not its exact current alias101");
    }
    public static IEnumerable<IPlacedGetter> RedHollowSurfaceReferences(IFallout4ModGetter source){
        var world=source.Worldspaces.SingleOrDefault(w=>w.EditorID=="TLM_WRLD_RH_Surface");
        if(world==null)return Array.Empty<IPlacedGetter>(); // frozen earlier source
        if(world.TopCell?.EditorID!="TLM_CELL_RH_SurfacePersistent")throw new InvalidDataException("RH surface persistent cell missing/substituted");
        var grid=world.SubCells.SelectMany(b=>b.Items).SelectMany(s=>s.Items).ToArray();
        if(grid.Length!=1||grid[0].EditorID!="TLM_CELL_RH_Surface"||grid[0].Grid?.Point!=new P2Int(0,0)||grid[0].Landscape?.VertexHeightMap?.HeightMap.Width!=33||world.Climate.IsNull)throw new InvalidDataException("RH surface world/grid/LAND/climate invalid");
        var refs=world.TopCell.Persistent.Concat(world.TopCell.Temporary).Concat(grid[0].Persistent).Concat(grid[0].Temporary).ToArray();
        foreach(var r in refs){
            var name=r.EditorID??"";
            if(!name.StartsWith("TLM_REF_RHE_")&&!name.StartsWith("TLM_REF_RH_Floor_A")&&!name.StartsWith("TLM_REF_RH_Floor_B")&&!RedHollowSurfaceSites.ContainsKey(name.Replace("TLM_REF_RH_","")))throw new InvalidDataException("Unexpected RH surface reference: "+name);
        }
        foreach(var (name,at) in RedHollowSurfaceSites){
            var r=refs.SingleOrDefault(r=>r.EditorID=="TLM_REF_RH_"+name)??throw new InvalidDataException("RH surface original missing: "+name);
            var position=r switch{IPlacedObjectGetter obj=>obj.Position,IPlacedNpcGetter actor=>actor.Position,_=>throw new InvalidDataException("RH surface original type invalid")};
            if(position!=new P3Float(at.X,at.Y,at.Z)||(r.MajorRecordFlagsRaw&0xC00)!=0xC00)throw new InvalidDataException("RH surface original transform/persistence changed: "+name);
        }
        return refs;
    }
}
