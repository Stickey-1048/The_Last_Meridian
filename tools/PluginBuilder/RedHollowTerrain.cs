using Mutagen.Bethesda.Fallout4;
using Noggog;
namespace Tlm.PluginBuilder;

// RH-TERRAIN-002: original story pad remains height0. Northern exploration is
// physical LAND, not a claim of native navigation or an extension of the clock.
public static class RedHollowTerrain
{
    public static readonly RedHollowEnvironment.Asset[] Assets={
        new("workshop_ShackMidFloor01B",@"Architecture\Shacks\ShackMidFloor01B.nif",new short[]{-128,-128,-14,128,128,0}),
        new("NpcBedWoodLay01Static",@"SetDressing\Building\BedWood01.nif",new short[]{-73,-100,0,72,98,83}),
        new("NPCCouchModernDomesticSit01Static",@"Furniture\ModernDomestic\ModernDomesticCouch01.nif",new short[]{-88,-34,0,84,23,62}),
        new("FenceWoodStr01",@"SetDressing\FencesGrates\Wood\FenceWoodStr01.nif",new short[]{0,-2,3,128,4,168}),
        new("RockPileM01",@"Landscape\Rocks\RockPileM01.nif",new short[]{-159,-175,-44,114,195,98})
    };
    // Eight-unit terrain quantization; every operative footprint stays on0.
    public static int Height(int x,int y){
        int[] profile={0,16,32,64,96,128,128,128,128,128,128,160,192,224,256,288,320};
        if(y<=16)return 0;
        int height=profile[y-16];
        int ridge=(Math.Max(0,Math.Abs(x-16)-10)*2*Math.Min(y-16,4)/4)*8;
        return height+ridge;
    }
    // Exact triangle interpolation of the alternating-free LAND grid, used only
    // on axis-aligned routes/pads; steepest cell derivative is separately tested.
    public static float Ground(float x,float y){
        int ix=Math.Clamp((int)(x/128),0,31),iy=Math.Clamp((int)(y/128),0,31);
        float u=(x-ix*128)/128,v=(y-iy*128)/128;
        // All route/pad samples lie where height is X-invariant; bilinear equals
        // either triangle there. Nonroute prop support remains native-gated.
        return (1-u)*(1-v)*Height(ix,iy)+u*(1-v)*Height(ix+1,iy)+(1-u)*v*Height(ix,iy+1)+u*v*Height(ix+1,iy+1);
    }
    public static (Array2d<byte> Heights,Array2d<P3UInt8> Normals) Land(){
        var heights=new Array2d<byte>(33,33,0);var normals=new Array2d<P3UInt8>(33,33,new P3UInt8(0,0,127));
        for(int y=0;y<33;y++)for(int x=0;x<33;x++){
            int previous=x>0?Height(x-1,y):y>0?Height(0,y-1):0;
            int delta=(Height(x,y)-previous)/8;
            if(delta < -128 || delta > 127)throw new InvalidDataException("RH terrain height delta overflow");
            heights[x,y]=unchecked((byte)(sbyte)delta);
            float dx=(Height(Math.Min(x+1,32),y)-Height(Math.Max(x-1,0),y))/(x==0||x==32?128f:256f);
            float dy=(Height(x,Math.Min(y+1,32))-Height(x,Math.Max(y-1,0)))/(y==0||y==32?128f:256f);
            float length=MathF.Sqrt(dx*dx+dy*dy+1);
            byte Signed(float value)=>unchecked((byte)(sbyte)Math.Clamp((int)MathF.Round(value/length*127),-127,127));
            normals[x,y]=new P3UInt8(Signed(-dx),Signed(-dy),Signed(1));
        }
        return(heights,normals);
    }
    public sealed record Route(string Name,(float X,float Y)[] Points);
    public static readonly Route[] Routes={
        new("Court to northern camp",new[]{(1536f,256f),(2048f,256f),(2048f,1920f),(2048f,2048f),(2048f,2560f),(1280f,2560f),(1280f,3072f)}),
        new("Camp to overlook",new[]{(1280f,2560f),(2048f,2560f),(2048f,3584f),(2560f,3584f)}),
        new("Camp return to mine yard",new[]{(2048f,2688f),(2496f,2688f),(2496f,1920f),(2560f,1536f),(2560f,1280f)})
    };
    public static IEnumerable<RedHollowEnvironment.Piece> Pieces(){
        var p=new List<RedHollowEnvironment.Piece>();
        void Put(string name,string asset,float x,float y,float z,float yaw=0)=>p.Add(new("T2_"+name,asset,x,y,z,yaw,true));
        // Visible safe waiting landmark around the SAME Released1024,256.
        // Passive shelter only, no alias/package/recruitment or forced movement.
        Put("ReleasedWaitingRoof","ShackMidRoof01",1024,256,42);
        foreach(int x in new[]{896,1152})foreach(int y in new[]{128,384})Put("ReleasedWaitingPost"+x+"_"+y,"FenceWoodPost01",x,y,64);
        // Open-front camp cabin, broad clear central aisle, decorative furniture.
        for(int x=1024;x<=1536;x+=256)for(int y=2944;y<=3200;y+=256){
            Put("CabinFloor"+x+"_"+y,"workshop_ShackMidFloor01B",x,y,144);
            Put("CabinRoof"+x+"_"+y,"ShackMidRoof01",x,y,144);
        }
        for(int x=1024;x<=1536;x+=256)Put("CabinBack"+x,"ShackWallFlat02",x,3200,144,MathF.PI);
        foreach(int y in new[]{2944,3200}){Put("CabinWest"+y,"ShackWallFlat02",1024,y,144,MathF.PI/2);Put("CabinEast"+y,"ShackWallFlat02",1536,y,144,-MathF.PI/2);}
        Put("BedA","NpcBedWoodLay01Static",1024,3140,144);
        Put("BedB","NpcBedWoodLay01Static",1024,2928,144);
        Put("Couch","NPCCouchModernDomesticSit01Static",1536,3190,144);
        // A low16-unit threshold; no invisible teleport or promised sleep/sit.
        Put("CabinEntryFloor","workshop_ShackMidFloor01B",1280,2816,144);
        for(int x=768;x<=1664;x+=128)Put("CampFence"+x,"FenceWoodStr01",x,3456,Ground(x,3456)-3);
        // Fence opening from1792 to2304 is deliberately512wide and connected.
        for(int x=2304;x<=3200;x+=128)Put("CampFence"+x,"FenceWoodStr01",x,3456,Ground(x,3456)-3);
        // Tree/rock clusters frame both sides of the two visible routes.
        foreach(var at in new[]{(384,2560),(640,2944),(512,3456),(768,3712),(1536,3840),(3072,2304),(3328,2688),(3584,3072),(3328,3712),(2944,3840)})
            Put("Tree"+at.Item1+"_"+at.Item2,"TreeMapleForest6",at.Item1,at.Item2,Ground(at.Item1,at.Item2)+7);
        foreach(var at in new[]{(768,2304),(1024,2432),(2944,2560),(3072,2816),(2944,3584),(1792,3712)})
            Put("Rock"+at.Item1+"_"+at.Item2,"RockPileM01",at.Item1,at.Item2,Ground(at.Item1,at.Item2)+24);
        // Paired posts mark the open route out of the former northern barrier.
        foreach(int x in new[]{1792,2304})Put("RoutePost"+x,"FenceWoodPost01",x,1920,64);
        // New east/west boundary follows the shaped apron; no exit into void.
        for(int y=1792;y<=3840;y+=512){Put("WestBoundary"+y,"QryCubeWall01",0,y,Ground(0,Math.Max(0,y-256))+256,-MathF.PI/2);Put("EastBoundary"+y,"QryCubeWall01",4096,y,Ground(4096,Math.Max(0,y-256))+256,MathF.PI/2);}
        return p;
    }
}

