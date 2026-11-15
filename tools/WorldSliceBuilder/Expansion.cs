using Mutagen.Bethesda.Fallout4;
using Mutagen.Bethesda.Plugins;

// Explicit scenery/settlement expansion only. Appended AFTER story allocation:
// all old form IDs/story positions remain stable. Two decorative bollards
// move only in expanded mode to open the new junction. No actor/nav edits.
public static class Expansion
{
    public sealed record Route(string Name,(float X,float Y)[] Points);
    public static readonly Route[] Routes = {
        new("Freight approach",new[]{(2600f,2200f),(2260f,2200f),(1880f,2480f),(1880f,2560f)}),
        new("West street and rear supply approach",new[]{(2260f,2200f),(2260f,3558f),(3050f,3558f),(3050f,3572f)})
    };
    public static object Add(IFallout4ModGetter master, Action<string,FormKey,float,float,float,float> put)
    {
        var assets=new Dictionary<string,object>();var refs=new List<string>();
        void Place(string id,string asset,float x,float y,float z=0,float yaw=0){
            var record=master.Statics.Single(s=>s.EditorID==asset);
            assets.TryAdd(asset,new{editorId=asset,form=record.FormKey.ToString(),model=record.Model?.File?.ToString(),min=new[]{(int)record.ObjectBounds.First.X,record.ObjectBounds.First.Y,record.ObjectBounds.First.Z},max=new[]{(int)record.ObjectBounds.Second.X,record.ObjectBounds.Second.Y,record.ObjectBounds.Second.Z}});
            put("EX_"+id,record.FormKey,x,y,z,yaw);refs.Add("TLM_WS_EX_"+id);
        }
        // Actual rail assets make the rear of the wreck recognizable while
        // the existing evidence remains in its unobstructed foreground.
        Place("WreckBoxcar","RRBoxcar01",850,1700,2,MathF.PI/2);
        Place("WreckBogie","RRTrainBogie01",1100,1450,2);
        // Both annexes are deliberately open-front, three-wall shelters. No
        // interactive door, service, occupancy or collision pass is invented.
        void Shelter(string name,float cx,float cy){
            for(int col=0;col<2;col++){
                float x=cx-128+col*256;
                Place(name+"Floor"+col,"workshop_ShackMidFloor01B",x,cy,16);
                Place(name+"Roof"+col,"ShackMidRoof01",x,cy,16);
                Place(name+"Back"+col,"ShackWallFlat02",x,cy,16,MathF.PI);
            }
            Place(name+"Left","ShackWallFlat02",cx-128,cy,16,MathF.PI/2);
            Place(name+"Right","ShackWallFlat02",cx+128,cy,16,-MathF.PI/2);
        }
        Shelter("Freight",1880,2800);
        Shelter("Supply",3050,3800);
        // Existing256-wide fence opening becomes a visible240-wide gateway;
        // the roof's audited underside is214, above the128-unit check volume.
        Place("GateLeft","FenceWoodPost01",2920,2380,64);
        Place("GateRight","FenceWoodPost01",3176,2380,64);
        Place("GateCanopy","ShackMidRoof01",3048,2380,16);
        // Low rock banks and sparse trees shape otherwise flat terrain.
        // No LAND sculpting: preserving old ground/thresholds is intentional.
        Place("NorthwestBank","RockPileL01",900,2650);
        Place("SoutheastBank","RockPileL01",3550,1600);
        Place("WreckRock","RockBoulder03",350,1700,59);
        Place("WreckTree","TreeMapleForest6",450,2200,7);
        Place("NorthwestTreeA","TreeMapleForestsmall1",500,2900,4);
        Place("NorthwestTreeB","TreeMapleForestsmall1",950,3400,4);
        Place("NorthwestTreeC","TreeMapleForest6",1350,3650,7);
        Place("RoadWestTree","TreeMapleForest6",1450,2400,7);
        Place("SoutheastTreeA","TreeMapleForest6",3400,1000,7);
        Place("SoutheastTreeB","TreeMapleForest6",3650,2150,7);
        Place("TownEastTree","TreeMapleForest6",3500,3750,7);
        return new{layout="WORLD-EXPAND003",newReferences=refs.Count,referenceIds=refs,
            movedDecorativePosts=new[]{new{id="TLM_WS_Main15L",x=2450,y=2550},new{id="TLM_WS_Main16L",x=2440,y=2360}},
            areas=new[]{new{name="Wreck",purpose="Real boxcar/bogie behind the unchanged evidence foreground"},new{name="Caravan road",purpose="Open encounter and bypass, framed by sparse landscape assets"},new{name="Mercy",purpose="Existing rest/debrief cabin; open freight/repair annex and rear supply shelter; visible passable gateway"}},
            buildings=new[]{new{name="Freight/repair shelter",center=new{x=1880,y=2800},floor=new{minX=1624,maxX=2136,minY=2672,maxY=2928},openFrontWidth=504},new{name="Supply shelter",center=new{x=3050,y=3800},floor=new{minX=2794,maxX=3306,minY=3672,maxY=3928},openFrontWidth=504}},
            routes=Routes.Select(r=>new{name=r.Name,points=r.Points.Select(p=>new{x=p.X,y=p.Y}),sampledWidth=192}),
            gateway=new{clearWidth=240,roofUnderside=214},terrain="Existing flat LAND retained; rock banks provide terrain silhouette, not new heightmap",
            assets=assets.Values,nativeAcceptance="Pending walk/collision/roof/furniture/standing/view checks; no new services, occupancy, NPC navigation or navmesh proof"};
    }
}
