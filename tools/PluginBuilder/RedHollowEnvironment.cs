using Mutagen.Bethesda;
using Mutagen.Bethesda.Fallout4;
using Mutagen.Bethesda.Plugins;
using Mutagen.Bethesda.Plugins.Records;
using Noggog;
using System.Text.Json;
using Color=System.Drawing.Color;

namespace Tlm.PluginBuilder;

// New master-owned environment only. References installed assets, never imports
// donor placed records, actors, scripts, doors, navmesh, precombine or LAND bytes.
public static class RedHollowEnvironment
{
    public const string World="TLM_WRLD_RH_Surface",Persistent="TLM_CELL_RH_SurfacePersistent",Surface="TLM_CELL_RH_Surface",Land="TLM_LAND_RH_Surface";
    public sealed record Asset(string Id,string Model,short[] Bounds);
    public static readonly Asset[] Assets={
        new("QryFloor01",@"Architecture\Quarry\QryFloor01.nif",new short[]{-256,-256,0,256,256,0}),
        new("QryCubeWall01",@"Architecture\Quarry\QryCubeWall01.nif",new short[]{-256,0,-256,256,0,256}),
        new("CaveRmCeiling512v01",@"Interiors\Cave\Rooms\CaveRmCeiling512v01.nif",new short[]{-256,-256,229,256,256,257}),
        new("QryRockM01",@"Architecture\Quarry\Rocks\QryRockM01.nif",new short[]{-87,-65,-38,106,84,81}),
        new("TreeMapleForest6",@"Landscape\Trees\TreeMapleForest6.nif",new short[]{-69,-99,-7,91,104,1223}),
        new("ShackWallFlat02",@"Architecture\Shacks\ShackWallFlat02.nif",new short[]{-128,-132,0,128,-124,198}),
        new("ShackMidRoof01",@"Architecture\Shacks\ShackMidRoof01.nif",new short[]{-130,-135,198,128,136,210})
    };
    public sealed record Piece(string Name,string Base,float X,float Y,float Z,float Yaw=0,bool Outside=false);
    public static Piece[] Geometry(){
        var p=new List<Piece>();
        void Put(string n,string b,float x,float y,float z,float yaw=0,bool outside=false)=>p.Add(new(n,b,x,y,z,yaw,outside));
        // Exact passive Dunwich mine/quarry kit, new references and layout.
        foreach(var room in new[]{("Nine",5888,7936),("Gallery",8960,11008)}){
            for(int x=room.Item2+256;x<room.Item3;x+=512)for(int y=0;y<1536;y+=512){
                Put(room.Item1+"Floor"+x+"_"+y,"QryFloor01",x,y,0);
                Put(room.Item1+"Roof"+x+"_"+y,"CaveRmCeiling512v01",x,y,256);
            }
            for(int x=room.Item2+256;x<room.Item3;x+=512){Put(room.Item1+"South"+x,"QryCubeWall01",x,-256,256);Put(room.Item1+"North"+x,"QryCubeWall01",x,1280,256,MathF.PI);}
            for(int y=0;y<1536;y+=512){Put(room.Item1+"West"+y,"QryCubeWall01",room.Item2,y,256,MathF.PI/2);Put(room.Item1+"East"+y,"QryCubeWall01",room.Item3,y,256,-MathF.PI/2);}
        }
        // Actual outdoor boundary/context; central court/bypass/work-yard clear.
        for(int x=256;x<4096;x+=512){Put("South"+x,"QryCubeWall01",x,0,256,0,true);Put("North"+x,"QryCubeWall01",x,1792,256,MathF.PI,true);}
        for(int y=256;y<1792;y+=512){Put("West"+y,"QryCubeWall01",0,y,256,MathF.PI/2,true);Put("East"+y,"QryCubeWall01",4096,y,256,-MathF.PI/2,true);}
        for(int x=256;x<4096;x+=512){Put("Trees"+x,"TreeMapleForest6",x,2300,7,0,true);Put("QuarryEdge"+x,"QryRockM01",x,1660,38,0,true);}
        // Readable small court and hoist shelters, outside operative envelopes.
        foreach(var hut in new[]{("Court",1152f), ("Hoist",3456f)}){
            Put(hut.Item1+"Back","ShackWallFlat02",hut.Item2,1536,0,0,true);
            Put(hut.Item1+"Roof","ShackMidRoof01",hut.Item2,1408,128,0,true);
        }
        return p.ToArray();
    }
    public static bool IsSurface(string name)=>RedHollow.Pieces.Any(p=>"TLM_REF_RH_"+p.Alias==name&&!p.Mercy&&p.X<5000&&p.Alias!="Fall")||name.StartsWith("TLM_REF_RH_Floor_A")||name.StartsWith("TLM_REF_RH_Floor_B");
    public static bool IsMouth(string name)=>RedHollow.Pieces.Any(p=>"TLM_REF_RH_"+p.Alias==name&&!p.Mercy&&p.X>=2944&&p.X<5000)||name.StartsWith("TLM_REF_RH_Floor_B");
    public static IEnumerable<(ICellGetter Cell,int Block,int Sub)> ReportCells(IFallout4ModGetter mod){
        foreach(var b in mod.Cells.Records)foreach(var s in b.SubBlocks)foreach(var c in s.Cells)yield return(c,b.BlockNumber,s.BlockNumber);
        foreach(var w in mod.Worldspaces.Where(w=>w.EditorID==World)){
            if(w.TopCell!=null)yield return(w.TopCell,0,0);
            foreach(var b in w.SubCells)foreach(var s in b.Items)foreach(var c in s.Items)yield return(c,b.BlockNumberX,s.BlockNumberX);
        }
    }
    public static PlacedSpec Effective(PlacedSpec p)=>IsSurface(p.EditorId)?p with{Cell=Persistent,Right=p.Right-(IsMouth(p.EditorId)?1024:0),InitiallyDisabled=p.InitiallyDisabled||p.EditorId.StartsWith("TLM_REF_RH_Floor_")}:p;
    public static IEnumerable<PlacedSpec> AddedPlaced(){
        foreach(var p in Geometry())yield return new("TLM_REF_RHE_"+p.Name,p.Outside?Persistent:RedHollow.CellId,p.Base,"Static",p.Y,p.X,p.Z,false);
        int index=0;foreach(int origin in new[]{5888,8960})for(int x=origin+128;x<origin+2048;x+=256)for(int y=-128;y<1280;y+=256)yield return new("TLM_REF_RHE_Light"+(index++),RedHollow.CellId,"defaultLightWarm01NS","Light",y,x,160,false);
    }
}

public sealed partial class Builder
{
    public object? RedHollowEnvironmentReceipt {get;private set;}
    void BuildRedHollowEnvironment(){
        // Allocation is identical in skeleton and full modes, after every old ref.
        var names=new[]{RedHollowEnvironment.World,RedHollowEnvironment.Persistent,RedHollowEnvironment.Surface,RedHollowEnvironment.Land}
            .Concat(RedHollowEnvironment.Geometry().Select(p=>"TLM_REF_RHE_"+p.Name))
            .Concat(Enumerable.Range(0,96).Select(i=>"TLM_REF_RHE_Light"+i)).ToArray();
        var keys=names.ToDictionary(n=>n,n=>_mod.GetNextFormKey(n));
        if(_vanillaMod==null){Pending.Add("RH environment requires strict typed owned-master metadata; no outdoor/light construction in skeleton mode");return;}
        var assets=new Dictionary<string,IStaticGetter>();
        foreach(var expected in RedHollowEnvironment.Assets){
            var asset=_vanillaMod.Statics.SingleOrDefault(s=>s.EditorID==expected.Id)??throw new InvalidDataException("RH environment static missing: "+expected.Id);
            var b=asset.ObjectBounds;var actual=new[]{b.First.X,b.First.Y,b.First.Z,b.Second.X,b.Second.Y,b.Second.Z};
            if(!actual.SequenceEqual(expected.Bounds)||asset.Model?.File?.ToString()!=expected.Model)throw new InvalidDataException("RH environment exact model/bounds changed: "+expected.Id);
            assets.Add(expected.Id,asset);
            VanillaFound.Add(new(expected.Id,asset.FormKey.ToString(),"Static"));
        }
        var light=_vanillaMod.Lights.SingleOrDefault(l=>l.EditorID=="defaultLightWarm01NS")??throw new InvalidDataException("RH real LIGH missing");
        if(light.Radius!=256||light.Time!=-1||(uint)light.Flags!=8193||light.FadeValue!=1||light.VirtualMachineAdapter!=null||!light.Sound.IsNull)throw new InvalidDataException("RH emitter metadata/behavior changed");
        VanillaFound.Add(new(light.EditorID!,light.FormKey.ToString(),"Light"));
        var template=_vanillaMod.LightingTemplates.SingleOrDefault(t=>t.EditorID=="QuarryLightingTemplate")??throw new InvalidDataException("RH light template missing");
        var climate=_vanillaMod.Worldspaces.SingleOrDefault(w=>w.EditorID=="Commonwealth")?.Climate??throw new InvalidDataException("RH exterior climate source missing");
        if(climate.IsNull)throw new InvalidDataException("RH exterior climate absent");
        var texture=_vanillaMod.LandscapeTextures.SingleOrDefault(t=>t.EditorID=="LDirtGravel01")??throw new InvalidDataException("RH LAND texture missing");
        var world=new Worldspace(keys[RedHollowEnvironment.World],Fallout4Release.Fallout4){EditorID=RedHollowEnvironment.World,Name="Red Hollow: quarry gap and mine yard",Flags=Worldspace.Flag.SmallWorld|Worldspace.Flag.CannotFastTravel|Worldspace.Flag.NoGrass|Worldspace.Flag.NoLodWater,LandDefaults=new WorldspaceLandDefaults{DefaultLandHeight=0,DefaultWaterHeight=-2048},ObjectBoundsMin=new P2Float(0,0),ObjectBoundsMax=new P2Float(4096,4096)};
        world.Climate.SetTo(climate.FormKey);_mod.Worldspaces.Add(world);
        world.TopCell=new Cell(keys[RedHollowEnvironment.Persistent],Fallout4Release.Fallout4){EditorID=RedHollowEnvironment.Persistent,MajorRecordFlagsRaw=0x400};
        var surface=new Cell(keys[RedHollowEnvironment.Surface],Fallout4Release.Fallout4){EditorID=RedHollowEnvironment.Surface,Name="Red Hollow: outside at the Gap and Mouth",Grid=new CellGrid{Point=new P2Int(0,0)},WaterHeight=-2048};
        var block=new WorldspaceBlock{BlockNumberX=0,BlockNumberY=0,GroupType=GroupTypeEnum.ExteriorCellBlock};var sub=new WorldspaceSubBlock{BlockNumberX=0,BlockNumberY=0,GroupType=GroupTypeEnum.ExteriorCellSubBlock};world.SubCells.Add(block);block.Items.Add(sub);sub.Items.Add(surface);
        var land=new Landscape(keys[RedHollowEnvironment.Land],Fallout4Release.Fallout4){DATA=new byte[]{0x1D,0,0,0},VertexNormals=new Array2d<P3UInt8>(33,33,new P3UInt8(0,0,127)),VertexHeightMap=new LandscapeVertexHeightMap{Offset=0,HeightMap=new Array2d<byte>(33,33,0)},Textures=new()};
        foreach(var q in Enum.GetValues<Quadrant>())land.Layers.Add(new BaseLayer{Header=new LayerHeader{Texture=new FormLink<ILandscapeTextureGetter>(texture.FormKey),Quadrant=q,LayerNumber=0}});land.Textures.Add(texture.ToLink<ILandscapeTextureGetter>());surface.Landscape=land;
        var below=_mod.Cells.Records.SelectMany(b=>b.SubBlocks).SelectMany(b=>b.Cells).Single(c=>c.EditorID==RedHollow.CellId);
        foreach(var c in new[]{world.TopCell,surface}){CellsFiled[c.EditorID!]=(0,0);CellNames[c.EditorID!]=c.Name?.String;Arrivals.Add(new(c.EditorID!,c.FormKey.ToString(),new[]{0f,0f,0f},0,true));}
        var moved=new List<object>();
        foreach(var r in below.Persistent.Where(r=>RedHollowEnvironment.IsSurface(r.EditorID??"")).ToArray()){
            var old=r switch {IPlacedObjectGetter obj=>obj.Position,IPlacedNpcGetter actor=>actor.Position,_=>throw new InvalidDataException("Unexpected RH surface reference type")};var mouth=RedHollowEnvironment.IsMouth(r.EditorID!);below.Persistent.Remove(r);
            var after=new P3Float(old.X-(mouth?1024:0),old.Y,old.Z);
            if(r is PlacedObject objPlaced)objPlaced.Position=after;else if(r is PlacedNpc actorPlaced)actorPlaced.Position=after;
            if(r.EditorID!.StartsWith("TLM_REF_RH_Floor_"))r.MajorRecordFlagsRaw|=0x800;
            world.TopCell.Persistent.Add(r);moved.Add(new{reference=r.EditorID,key=r.FormKey.ToString(),before=new[]{old.X,old.Y,old.Z},after=new[]{after.X,after.Y,after.Z},parent=RedHollowEnvironment.Persistent,flags=r.MajorRecordFlagsRaw});
        }
        // RH-only light template plus explicit real emitters; generic cells intact.
        below.LightingTemplate.SetTo(template.FormKey);
        below.Lighting=new CellLighting{AmbientColor=Color.FromArgb(255,39,38,35),DirectionalColor=Color.FromArgb(255,20,20,20),DirectionalFade=1,FogNear=1200,FogFar=10000};
        foreach(var p in RedHollowEnvironment.Geometry()){
            var placed=new PlacedObject(keys["TLM_REF_RHE_"+p.Name],Fallout4Release.Fallout4){EditorID="TLM_REF_RHE_"+p.Name,Position=new P3Float(p.X,p.Y,p.Z),Rotation=new P3Float(0,0,p.Yaw),MajorRecordFlagsRaw=0x400};placed.Base.SetTo(assets[p.Base].FormKey);
            if(p.Outside)world.TopCell.Persistent.Add(placed);else below.Persistent.Add(placed);
            _placed[placed.EditorID!]=placed.FormKey;
        }
        int index=0;
        foreach(int origin in new[]{5888,8960})for(int x=origin+128;x<origin+2048;x+=256)for(int y=-128;y<1280;y+=256){
            var placed=new PlacedObject(keys["TLM_REF_RHE_Light"+index],Fallout4Release.Fallout4){EditorID="TLM_REF_RHE_Light"+index,Position=new P3Float(x,y,160),Rotation=new P3Float(0,0,0),MajorRecordFlagsRaw=0x400};placed.Base.SetTo(light.FormKey);below.Persistent.Add(placed);_placed[placed.EditorID!]=placed.FormKey;index++;
        }
        RedHollowEnvironmentReceipt=new{policy="New supported flat LAND plus selected evaluated passive Dunwich quarry/mine geometry; no imported sculpted terrain or donor behavior",world=world.EditorID,surface=surface.EditorID,underground=below.EditorID,rehomed=moved,emitter=new{id=light.EditorID,key=light.FormKey.ToString(),radius=light.Radius,flags=(uint)light.Flags,count=index},template=template.FormKey.ToString(),native="Sky/brightness/support/Havok/navmesh/culling/controller/reload unverified"};
    }
}
