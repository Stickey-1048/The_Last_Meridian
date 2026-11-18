using Mutagen.Bethesda.Fallout4;
using Mutagen.Bethesda.Plugins;
using Noggog;

public static partial class WorldStory
{
    public static readonly Dictionary<string,(float X,float Y,float Z)> RedHollowSurfaceSites=new(){
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
        ["FiringControl"]=(2816,384,12),
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
