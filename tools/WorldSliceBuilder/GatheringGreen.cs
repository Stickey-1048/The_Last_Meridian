using Mutagen.Bethesda.Fallout4;
using Mutagen.Bethesda.Plugins;
using F4Furniture=Mutagen.Bethesda.Fallout4.Furniture;

// Five-reference outdoor destination, no quests/services/NPC packages.
public static class GatheringGreen
{
    public static readonly Expansion.Route[] Routes = {
        new("Green approach",new[]{(2260f,3455f),(2080f,3455f)}),
        new("Green walk loop",new[]{(2080f,3303f),(1710f,3303f),(1710f,3607f),(2080f,3607f),(2080f,3303f)}),
        new("South bench west entry",new[]{(1710f,3303f),(1696f,3190f)}),
        new("South bench east entry",new[]{(2080f,3303f),(2064f,3190f)}),
        new("North bench west entry",new[]{(1710f,3607f),(1696f,3720f)}),
        new("North bench east entry",new[]{(2080f,3607f),(2064f,3720f)})
    };
    public static readonly (string Bench,float X,float Y)[] Standing = {
        ("EX_GREEN_BenchSouth",1696,3190),("EX_GREEN_BenchSouth",2064,3190),
        ("EX_GREEN_BenchNorth",1696,3720),("EX_GREEN_BenchNorth",2064,3720)
    };
    public static object Add(IFallout4ModGetter master,Action<string,FormKey,float,float,float,float> put)
    {
        var bench=master.Furniture.Single(f=>f.EditorID=="NPCBenchParkSit01");
        var markers=bench.MarkerParameters??Array.Empty<IFurnitureMarkerParametersGetter>();
        var entries=bench.MarkerEntryPoints??Array.Empty<IFurnitureMarkerEntryPointsGetter>();
        var a=bench.ObjectBounds.First;var b=bench.ObjectBounds.Second;
        var keywords=(bench.Keywords??Array.Empty<Mutagen.Bethesda.Plugins.IFormLinkGetter<IKeywordGetter>>())
            .Select(k=>master.Keywords.Single(x=>x.FormKey==k.FormKey).EditorID??"").ToHashSet(StringComparer.Ordinal);
        if(bench.FormKey.ID!=0xDF45A||bench.Model?.File?.ToString()!=@"Furniture\ParkBench01.nif"||
           a.X!=-82||a.Y!=-43||a.Z!=0||b.X!=82||b.Y!=12||b.Z!=62||
           bench.Flags?.ToString()!="HasModel"||(uint)bench.MajorFlags!=8192||(bench.Conditions?.Count??0)!=0||bench.VirtualMachineAdapter!=null||
           (bench.Items?.Count??0)!=0||bench.BenchType!=F4Furniture.BenchTypes.None||bench.EnabledEntryPoints?.ToString()!="Right, Left"||
           !keywords.SetEquals(new[]{"AnimFurnChairSitAnims","AnimFurnAllowEating","FurnitureClassRelaxation"})||
           markers.Count!=2||!markers.Select(m=>m.Offset.X).Order().SequenceEqual(new[]{-32f,32f})||markers.Any(m=>!m.Enabled||m.Offset.Y!=0||m.Offset.Z!=0||m.RotationZ!=0)||
           entries.Count!=3||entries.Any(m=>m.Type!=F4Furniture.AnimationType.Sit||m.Points.ToString()!="Front, Right, Left"))
            throw new InvalidDataException("Green bench eligibility/model/marker audit differs from reviewed master; no fallback.");
        var hearth=master.Statics.Single(s=>s.EditorID=="CampFireMed01_Off_NoSkirt");
        var rock=master.Statics.Single(s=>s.EditorID=="RockBoulder03");
        void Check(IStaticGetter s,uint id,string model,int[] min,int[] max){
            var x=s.ObjectBounds.First;var y=s.ObjectBounds.Second;
            if(s.FormKey.ID!=id||s.Model?.File?.ToString()!=model||x.X!=min[0]||x.Y!=min[1]||x.Z!=min[2]||y.X!=max[0]||y.Y!=max[1]||y.Z!=max[2])
                throw new InvalidDataException("Green static asset audit mismatch: "+s.EditorID);
        }
        Check(hearth,0x6356D,@"Landscape\CampFireMed01_Off_NoSkirt.nif",new[]{-46,-49,3},new[]{49,51,36});
        Check(rock,0x2F79B,@"Landscape\Rocks\RockBoulder03.nif",new[]{-60,-46,-59},new[]{78,69,30});
        var refs=new List<object>();
        void Place(string name,FormKey key,float x,float y,float z,float yaw=0){
            put("EX_GREEN_"+name,key,x,y,z,yaw);refs.Add(new{id="TLM_WS_EX_GREEN_"+name,@base=key.ToString(),x,y,z,yaw});
        }
        Place("BenchSouth",bench.FormKey,1880,3190,0);
        Place("BenchNorth",bench.FormKey,1880,3720,0,MathF.PI);
        Place("UnlitHearth",hearth.FormKey,1880,3455,-3);
        Place("WestRockSouth",rock.FormKey,1525,3335,59);
        // Side-entry audit moves only this NEW proposal35south, leaving128
        // standing space at the north bench's western entry.
        Place("WestRockNorth",rock.FormKey,1525,3550,59);
        return new{scope="Five own references after E127 allocation; same LAND/story/fences/normal19 scripts",placements=refs,
            benchAudit=new{form=bench.FormKey.ToString(),flags=bench.Flags.ToString(),conditions=0,scripts=false,benchType=bench.BenchType.ToString(),headerEntries=bench.EnabledEntryPoints.ToString(),keywords,
                markers=markers.Select(m=>new{m.Enabled,x=m.Offset.X,y=m.Offset.Y,z=m.Offset.Z,m.RotationZ,rawEntryParameters=(int)m.EntryTypes}),
                entries=entries.Select(m=>new{type=m.Type.ToString(),points=m.Points.ToString()})},
            routes=Routes.Select(r=>new{name=r.Name,points=r.Points.Select(p=>new{x=p.X,y=p.Y}),width=192}),
            standing=Standing.Select(p=>new{bench="TLM_WS_"+p.Bench,x=p.X,y=p.Y,radius=128}),
            ground="Existing LANDZ0; benchbase0/hearthbound3offset-3/rockbound-59offset59. Native contact pending.",
            limits="No native player eligibility/sit/stand/orientation/walking/collision proof; no NPC gathering, navmesh, cooking/fire-damage/service or quest change"};
    }
}
