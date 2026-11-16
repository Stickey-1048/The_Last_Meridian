using Mutagen.Bethesda.Fallout4;
using Mutagen.Bethesda.Plugins;

// PRIVATE six-prop storage/freight set dressing, never interactive services.
public static class ShelterDetails
{
    public static readonly (string Name,float X,float StartY,float EndY)[] Aisles = {
        ("Freight center aisle",1880,2560,2824),
        ("Supply center aisle",3050,3572,3824)
    };
    public static object Add(IFallout4ModGetter master,Action<string,FormKey,float,float,float,float> put)
    {
        var rows=new List<object>();
        void Place(string name,string edid,uint form,string model,int[] min,int[] max,float x,float y,float yaw=0){
            var asset=master.Statics.Single(s=>s.EditorID==edid);
            var a=asset.ObjectBounds.First;var b=asset.ObjectBounds.Second;
            if(asset.FormKey.ID!=form||!string.Equals(asset.Model?.File?.ToString(),model,StringComparison.OrdinalIgnoreCase)||
               a.X!=min[0]||a.Y!=min[1]||a.Z!=min[2]||b.X!=max[0]||b.Y!=max[1]||b.Z!=max[2])
                throw new InvalidDataException("Private shelter STATIC audit mismatch; no fallback: "+edid);
            // The existing native-tested floor surface is Z16; all six bounds
            // start at zero. No mesh origin correction or stacked-prop guess.
            put("EX_DETAIL_"+name,asset.FormKey,x,y,16,yaw);
            rows.Add(new{name="TLM_WS_EX_DETAIL_"+name,type="STAT",editorId=edid,form=asset.FormKey.ToString(),model,min,max,x,y,z=16,yaw,top=16+max[2]});
        }
        Place("FreightCrate","WoodCrate03",0x211F7,@"SetDressing\ConcMuseum\WoodCrate03.nif",new[]{-25,-52,0},new[]{25,52,29},1695,2856,MathF.PI/2);
        Place("FreightBarrel","MetalBarrelStatic01",0x18CD4,@"SetDressing\MetalBarrel\MetalBarrel01.nif",new[]{-26,-25,0},new[]{26,25,77},1695,2750);
        Place("FreightShelf","MetalShelf01",0x17DD7,@"SetDressing\MetalFurniture\MetalShelf01.nif",new[]{-52,-24,0},new[]{52,24,129},2050,2860);
        Place("SupplyShelf","MetalShelf04",0x17DD9,@"SetDressing\MetalFurniture\MetalShelf04.nif",new[]{-53,-24,0},new[]{52,25,128},2875,3850);
        Place("SupplyCrate","WoodCrate01",0x211F5,@"SetDressing\ConcMuseum\WoodCrate01.nif",new[]{-25,-28,0},new[]{25,27,51},3225,3780,MathF.PI/2);
        Place("SupplyBarrel","WoodBarrel01",0x211F4,@"SetDressing\ConcMuseum\WoodBarrel01.nif",new[]{-27,-26,0},new[]{27,26,66},3225,3878);
        return new{mode="PRIVATE six STATIC props; storage/freight set dressing only",assetsAndPlacements=rows,
            surface="All new minZ0 on existing floorZ16; highest top145 below roof underside214. Native support/collision unverified.",
            aisles=Aisles.Select(a=>new{name=a.Name,x=a.X,startY=a.StartY,endY=a.EndY,requiredWidth=192}),
            limits="No container inventory, crafting/medical service, interaction, seating, actor, quest, terrain or navmesh change"};
    }
}
