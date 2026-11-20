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
    public static readonly Asset[] Assets=new Asset[]{
        new("QryFloor01",@"Architecture\Quarry\QryFloor01.nif",new short[]{-256,-256,0,256,256,0}),
        new("QryCubeWall01",@"Architecture\Quarry\QryCubeWall01.nif",new short[]{-256,0,-256,256,0,256}),
        new("CaveRmCeiling512v01",@"Interiors\Cave\Rooms\CaveRmCeiling512v01.nif",new short[]{-256,-256,229,256,256,257}),
        new("QryRockM01",@"Architecture\Quarry\Rocks\QryRockM01.nif",new short[]{-87,-65,-38,106,84,81}),
        new("TreeMapleForest6",@"Landscape\Trees\TreeMapleForest6.nif",new short[]{-69,-99,-7,91,104,1223}),
        new("ShackWallFlat02",@"Architecture\Shacks\ShackWallFlat02.nif",new short[]{-128,-132,0,128,-124,198}),
        new("ShackMidRoof01",@"Architecture\Shacks\ShackMidRoof01.nif",new short[]{-130,-135,198,128,136,210})
        ,new("FenceWoodPost01",@"SetDressing\FencesGrates\Wood\FenceWoodPost01.nif",new short[]{-8,-6,-64,8,6,176})
    }.Concat(RedHollowTerrain.Assets).ToArray();
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
            for(int x=room.Item2+256;x<room.Item3;x+=512){Put(room.Item1+"South"+x,"QryCubeWall01",x,-256,256,MathF.PI);Put(room.Item1+"North"+x,"QryCubeWall01",x,1280,256,0);}
            for(int y=0;y<1536;y+=512){Put(room.Item1+"West"+y,"QryCubeWall01",room.Item2,y,256,-MathF.PI/2);Put(room.Item1+"East"+y,"QryCubeWall01",room.Item3,y,256,MathF.PI/2);}
        }
        // Actual outdoor boundary/context; central court/bypass/work-yard clear.
        for(int x=256;x<4096;x+=512){Put("South"+x,"QryCubeWall01",x,0,256,MathF.PI,true);Put("North"+x,"QryCubeWall01",x,4096,MathF.Min(RedHollowTerrain.Ground(Math.Max(0,x-256),4096),RedHollowTerrain.Ground(Math.Min(4096,x+256),4096))+256,0,true);}
        for(int y=256;y<1792;y+=512){Put("West"+y,"QryCubeWall01",0,y,256,-MathF.PI/2,true);Put("East"+y,"QryCubeWall01",4096,y,256,MathF.PI/2,true);}
        for(int x=256;x<4096;x+=512){Put("Trees"+x,"TreeMapleForest6",x,2300,RedHollowTerrain.Ground(x,2300)+7,0,true);Put("QuarryEdge"+x,"QryRockM01",x,1660,38,0,true);}
        // Readable small court and hoist shelters, outside operative envelopes.
        Put("CourtBack","ShackWallFlat02",1152,1664,0,0,true);
        Put("CourtRoof","ShackMidRoof01",1152,1408,42,0,true);
        foreach(int dx in new[]{-112,112})foreach(int dy in new[]{-112,112})Put("CourtPost"+dx+"_"+dy,"FenceWoodPost01",1152+dx,1408+dy,64,0,true);
        Put("HoistRoof","ShackMidRoof01",2816,512,42,0,true);Put("HoistDeskRoof","ShackMidRoof01",3072,512,42,0,true);
        foreach(int x in new[]{2704,3184})foreach(int y in new[]{400,624})Put("HoistPost"+x+"_"+y,"FenceWoodPost01",x,y,64,0,true);
        foreach(int y in new[]{128,384})Put("CourtGatePost"+y,"FenceWoodPost01",1408,y,64,0,true);
        Put("CourtGateRoof","ShackMidRoof01",1408,256,42,0,true);
        for(int y=0;y<1536;y+=512)Put("GallerySeal"+y,"QryCubeWall01",10528,y,256,MathF.PI/2);
        p.AddRange(RedHollowTerrain.Pieces());
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
    public static PlacedSpec Effective(PlacedSpec p)=>IsSurface(p.EditorId)?p with{Cell=Persistent,Right=p.Right-(IsMouth(p.EditorId)?1024:0),InitiallyDisabled=p.InitiallyDisabled||p.EditorId.StartsWith("TLM_REF_RH_Floor_")}:p.EditorId.StartsWith("TLM_REF_RH_Floor_")?p with{InitiallyDisabled=true}:p;
    public static IEnumerable<PlacedSpec> AddedPlaced(){
        foreach(var p in Geometry())yield return new("TLM_REF_RHE_"+p.Name,p.Outside?Persistent:RedHollow.CellId,p.Base,"Static",p.Y,p.X,p.Z,false);
        int index=0;foreach(int origin in new[]{5888,8960})for(int x=origin+128;x<origin+2048;x+=256)for(int y=-128;y<1280;y+=256)yield return new("TLM_REF_RHE_Light"+(index++),RedHollow.CellId,"defaultLightWarm01NS","Light",y,x,160,false);
        yield return new("TLM_REF_RH_SurfaceFall",Persistent,"TLM_ACTI_RHE_SurfaceFall",null,896,2048,-700,true,new[]{2048f,896f,120f});
        yield return new("TLM_REF_RH_GalleryFall",RedHollow.CellId,"TLM_ACTI_RHE_GalleryFall",null,512,9984,-700,true,new[]{1024f,768f,120f});
    }
    public static readonly AliasSpec[] FallAliases={new("SurfaceFall",Fill.Placed,AllowDisabled:true,Placed:"TLM_REF_RH_SurfaceFall",Scripts:new[]{new ScriptBind("TLM:RedHollowTalk",new IntProp("Who",46))}),new("GalleryFall",Fill.Placed,AllowDisabled:true,Placed:"TLM_REF_RH_GalleryFall",Scripts:new[]{new ScriptBind("TLM:RedHollowTalk",new IntProp("Who",47))})};
}

public sealed partial class Builder
{
    public object? RedHollowEnvironmentReceipt {get;private set;}
    void BuildRedHollowEnvironment(){
        // Allocation is identical in skeleton and full modes, after every old ref.
        var names=new[]{RedHollowEnvironment.World,RedHollowEnvironment.Persistent,RedHollowEnvironment.Surface,RedHollowEnvironment.Land}
            .Concat(RedHollowEnvironment.Geometry().Select(p=>"TLM_REF_RHE_"+p.Name))
            .Concat(Enumerable.Range(0,96).Select(i=>"TLM_REF_RHE_Light"+i))
            .Concat(new[]{"TLM_ACTI_RHE_SurfaceFall","TLM_REF_RH_SurfaceFall","TLM_ACTI_RHE_GalleryFall","TLM_REF_RH_GalleryFall"}).ToArray();
        var keys=names.ToDictionary(n=>n,n=>_mod.GetNextFormKey(n));
        if(_vanillaMod==null){Pending.Add("RH environment requires strict typed owned-master metadata; no outdoor/light construction in skeleton mode");return;}
        var assets=new Dictionary<string,IStaticGetter>();
        foreach(var expected in RedHollowEnvironment.Assets){
            var asset=_vanillaMod.Statics.SingleOrDefault(s=>s.EditorID==expected.Id)??throw new InvalidDataException("RH environment static missing: "+expected.Id);
            var b=asset.ObjectBounds;var actual=new[]{b.First.X,b.First.Y,b.First.Z,b.Second.X,b.Second.Y,b.Second.Z};
            if(!actual.SequenceEqual(expected.Bounds)||asset.Model?.File?.ToString()!=expected.Model)throw new InvalidDataException("RH environment exact model/bounds changed: "+expected.Id);
            foreach(string field in new[]{"VirtualMachineAdapter","Destructible"})if(asset.GetType().GetProperty(field)?.GetValue(asset)!=null)throw new InvalidDataException("RH passive base carries behavior: "+expected.Id+" / "+field);
            assets.Add(expected.Id,asset);
            VanillaFound.Add(new(expected.Id,asset.FormKey.ToString(),"Static"));
        }
        var light=_vanillaMod.Lights.SingleOrDefault(l=>l.EditorID=="defaultLightWarm01NS")??throw new InvalidDataException("RH real LIGH missing");
        if(light.Radius!=256||light.Time!=-1||(uint)light.Flags!=8193||light.FadeValue!=1||light.FalloffExponent!=1||light.Color.R!=228||light.Color.G!=203||light.Color.B!=182||light.VirtualMachineAdapter!=null||!light.Sound.IsNull)throw new InvalidDataException("RH emitter metadata/behavior changed");
        VanillaFound.Add(new(light.EditorID!,light.FormKey.ToString(),"Light"));
        var template=_vanillaMod.LightingTemplates.SingleOrDefault(t=>t.EditorID=="QuarryLightingTemplate")??throw new InvalidDataException("RH light template missing");
        if(template.AmbientColor.R!=39||template.AmbientColor.G!=38||template.AmbientColor.B!=35||template.DirectionalColor.R!=20||template.DirectionalColor.G!=20||template.DirectionalColor.B!=20||template.FogNear!=1200||template.FogFar!=10000)throw new InvalidDataException("RH exact light template settings changed");
        var lightRoom=_vanillaMod.Cells.Records.SelectMany(b=>b.SubBlocks).SelectMany(s=>s.Cells).SingleOrDefault(c=>c.EditorID=="DunwichBorers01")??throw new InvalidDataException("RH selected donor lighting room missing");
        if(lightRoom.Lighting==null||lightRoom.LightingTemplate.FormKey!=template.FormKey||(uint)lightRoom.Lighting.Inherits!=1784||lightRoom.Lighting.AmbientColor.R!=39||lightRoom.Lighting.AmbientColor.G!=38||lightRoom.Lighting.AmbientColor.B!=35)throw new InvalidDataException("RH donor room/template inheritance changed");
        var climate=_vanillaMod.Worldspaces.SingleOrDefault(w=>w.EditorID=="Commonwealth")?.Climate??throw new InvalidDataException("RH exterior climate source missing");
        if(climate.IsNull)throw new InvalidDataException("RH exterior climate absent");
        var texture=_vanillaMod.LandscapeTextures.SingleOrDefault(t=>t.EditorID=="LDirtGravel01")??throw new InvalidDataException("RH LAND texture missing");
        var geometryAudit=RedHollowGeometryAudit.Check(RedHollowEnvironment.Geometry());
        var world=new Worldspace(keys[RedHollowEnvironment.World],Fallout4Release.Fallout4){EditorID=RedHollowEnvironment.World,Name="Red Hollow: quarry gap and mine yard",Flags=Worldspace.Flag.SmallWorld|Worldspace.Flag.CannotFastTravel|Worldspace.Flag.NoGrass|Worldspace.Flag.NoLodWater,LandDefaults=new WorldspaceLandDefaults{DefaultLandHeight=0,DefaultWaterHeight=-2048},ObjectBoundsMin=new P2Float(0,0),ObjectBoundsMax=new P2Float(4096,4096)};
        world.Climate.SetTo(climate.FormKey);_mod.Worldspaces.Add(world);
        world.TopCell=new Cell(keys[RedHollowEnvironment.Persistent],Fallout4Release.Fallout4){EditorID=RedHollowEnvironment.Persistent,MajorRecordFlagsRaw=0x400};
        var surface=new Cell(keys[RedHollowEnvironment.Surface],Fallout4Release.Fallout4){EditorID=RedHollowEnvironment.Surface,Name="Red Hollow: outside at the Gap and Mouth",Grid=new CellGrid{Point=new P2Int(0,0)},WaterHeight=-2048};
        var block=new WorldspaceBlock{BlockNumberX=0,BlockNumberY=0,GroupType=GroupTypeEnum.ExteriorCellBlock};var sub=new WorldspaceSubBlock{BlockNumberX=0,BlockNumberY=0,GroupType=GroupTypeEnum.ExteriorCellSubBlock};world.SubCells.Add(block);block.Items.Add(sub);sub.Items.Add(surface);
        var terrain=RedHollowTerrain.Land();
        var land=new Landscape(keys[RedHollowEnvironment.Land],Fallout4Release.Fallout4){DATA=new byte[]{0x1D,0,0,0},VertexNormals=terrain.Normals,VertexHeightMap=new LandscapeVertexHeightMap{Offset=0,HeightMap=terrain.Heights},Textures=new()};
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
        foreach(var r in below.Persistent.Where(r=>(r.EditorID??"").StartsWith("TLM_REF_RH_Floor_")))r.MajorRecordFlagsRaw|=0x800;
        // RH-only light template plus explicit real emitters; generic cells intact.
        below.LightingTemplate.SetTo(template.FormKey);
        below.Lighting=lightRoom.Lighting.DeepCopy(); // lighting struct ONLY; no donor CELL behavior/refs/portals
        foreach(var p in RedHollowEnvironment.Geometry()){
            var placed=new PlacedObject(keys["TLM_REF_RHE_"+p.Name],Fallout4Release.Fallout4){EditorID="TLM_REF_RHE_"+p.Name,Position=new P3Float(p.X,p.Y,p.Z),Rotation=new P3Float(0,0,p.Yaw),MajorRecordFlagsRaw=0x400};placed.Base.SetTo(assets[p.Base].FormKey);
            if(p.Outside)world.TopCell.Persistent.Add(placed);else below.Persistent.Add(placed);
            _placed[placed.EditorID!]=placed.FormKey;
        }
        int index=0;
        foreach(int origin in new[]{5888,8960})for(int x=origin+128;x<origin+2048;x+=256)for(int y=-128;y<1280;y+=256){
            var placed=new PlacedObject(keys["TLM_REF_RHE_Light"+index],Fallout4Release.Fallout4){EditorID="TLM_REF_RHE_Light"+index,Position=new P3Float(x,y,160),Rotation=new P3Float(0,0,0),MajorRecordFlagsRaw=0x400};placed.Base.SetTo(light.FormKey);below.Persistent.Add(placed);_placed[placed.EditorID!]=placed.FormKey;index++;
        }
        foreach(var f in AddedFallSpecs()){
            var act=new Mutagen.Bethesda.Fallout4.Activator(keys[f.Base],Fallout4Release.Fallout4){EditorID=f.Base};_mod.Activators.Add(act);Track(act);
            var h=f.BoxHalfExtents!;var placed=new PlacedObject(keys[f.EditorId],Fallout4Release.Fallout4){EditorID=f.EditorId,Position=new P3Float(f.Right,f.Ahead,f.Up),Rotation=new P3Float(0,0,0),MajorRecordFlagsRaw=0xC00,Primitive=new PlacedPrimitive{Bounds=new P3Float(h[0]*2,h[1]*2,h[2]*2),Type=PlacedPrimitive.TypeEnum.Box,Color=Color.FromArgb(255,128,0),Unknown=0.3f}};placed.Base.SetTo(act.FormKey);
            if(WritesBoxBound)placed.BoundHalfExtents=new P3Float(h[0],h[1],h[2]);
            if(f.Cell==RedHollowEnvironment.Persistent)world.TopCell.Persistent.Add(placed);else below.Persistent.Add(placed);_placed[f.EditorId]=placed.FormKey;
        }
        RedHollowEnvironmentReceipt=new{policy="RH-TERRAIN-002: shaped original LAND, preserved story pad, northern camp/apron, evidence-based inward perimeter faces; no imported donor LAND/behavior",world=world.EditorID,surface=surface.EditorID,underground=below.EditorID,rehomed=moved,geometryAudit,selectedStatics=assets.Values.Select(a=>new{id=a.EditorID,key=a.FormKey.ToString(),model=a.Model?.File?.ToString(),min=new[]{a.ObjectBounds.First.X,a.ObjectBounds.First.Y,a.ObjectBounds.First.Z},max=new[]{a.ObjectBounds.Second.X,a.ObjectBounds.Second.Y,a.ObjectBounds.Second.Z}}).ToArray(),emitter=new{id=light.EditorID,key=light.FormKey.ToString(),radius=light.Radius,time=light.Time,flags=(uint)light.Flags,rgb=new[]{light.Color.R,light.Color.G,light.Color.B},fade=light.FadeValue,falloff=light.FalloffExponent,count=index},template=template.FormKey.ToString(),lightingSource=new{room=lightRoom.FormKey.ToString(),inherits=(uint)below.Lighting.Inherits,ambient=new[]{below.Lighting.AmbientColor.R,below.Lighting.AmbientColor.G,below.Lighting.AmbientColor.B},scope="Lighting struct only; native brightness/occlusion unverified"},native="Sky/brightness/support/Havok/navmesh/culling/controller/reload unverified"};
    }
    static IEnumerable<PlacedSpec> AddedFallSpecs()=>RedHollowEnvironment.AddedPlaced().Where(p=>p.BoxHalfExtents!=null);
}
