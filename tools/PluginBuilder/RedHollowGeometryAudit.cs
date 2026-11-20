using System.Text.Json;
namespace Tlm.PluginBuilder;

public static class RedHollowGeometryAudit
{
    public sealed record Box(string Name,string Base,bool Outside,float MinX,float MaxX,float MinY,float MaxY,float MinZ,float MaxZ);
    public static Box Bounds(RedHollowEnvironment.Piece p){
        var b=RedHollowEnvironment.Assets.Single(a=>a.Id==p.Base).Bounds;
        var corners=(from x in new[]{b[0],b[3]} from y in new[]{b[1],b[4]} select (X:p.X+x*MathF.Cos(p.Yaw)+y*MathF.Sin(p.Yaw),Y:p.Y-x*MathF.Sin(p.Yaw)+y*MathF.Cos(p.Yaw))).ToArray();
        return new(p.Name,p.Base,p.Outside,corners.Min(c=>c.X),corners.Max(c=>c.X),corners.Min(c=>c.Y),corners.Max(c=>c.Y),p.Z+b[2],p.Z+b[5]);
    }
    public static object Check(RedHollowEnvironment.Piece[] pieces){
        // Actual QryCubeWall01 triangles/packed normals are local-Y; the
        // measured Dunwich wall/floor pair establishes clockwise native yaw.
        foreach(var p in pieces.Where(p=>!p.Outside&&p.Base=="QryCubeWall01")){
            float targetX=p.Name.StartsWith("Nine")?6912:9984,targetY=512;
            float nx=-MathF.Sin(p.Yaw),ny=-MathF.Cos(p.Yaw);
            if(nx*(targetX-p.X)+ny*(targetY-p.Y)<=0)throw new InvalidDataException("RH perimeter face points away from room: "+p.Name);
        }
        for(int y=0;y<=32;y++)for(int x=0;x<=32;x++){
            int h=RedHollowTerrain.Height(x,y);
            if(h%8!=0||y<=16&&h!=0)throw new InvalidDataException("RH story pad/terrain quantization changed");
            if(x>0&&Math.Abs(h-RedHollowTerrain.Height(x-1,y))>64||y>0&&Math.Abs(h-RedHollowTerrain.Height(x,y-1))>64)throw new InvalidDataException("RH terrain step exceeds64per128");
        }
        var boxes=pieces.Select(Bounds).ToArray();int protectedCount=0;float minimumHeadroom=float.MaxValue;
        var emitters=RedHollowEnvironment.AddedPlaced().Where(p=>p.Base=="defaultLightWarm01NS").ToArray();
        void Point(string name,bool outside,float x,float y,float radius){
            if(outside&&(x<0||x>4096||y<0||y>4096))throw new InvalidDataException("RH support outside LAND: "+name);
            var relevant=boxes.Where(b=>b.Outside==outside).ToArray();
            if(!outside&&!emitters.Any(p=>(p.Right-x)*(p.Right-x)+(p.Ahead-y)*(p.Ahead-y)+(p.Up-16)*(p.Up-16)<=256*256))throw new InvalidDataException("RH control/cohort outside audited emitter radius: "+name);
            if(!outside&&!relevant.Any(b=>b.Base=="QryFloor01"&&b.MinZ==0&&b.MaxZ==0&&x-radius>=b.MinX-0.01&&x+radius<=b.MaxX+0.01&&y-radius>=b.MinY-0.01&&y+radius<=b.MaxY+0.01)){
                // Adjacent exact coplanar tiles jointly support a cohort envelope.
                for(int ix=-1;ix<=1;ix++)for(int iy=-1;iy<=1;iy++){
                    float sx=x+ix*radius,sy=y+iy*radius;
                    if(!relevant.Any(b=>b.Base=="QryFloor01"&&b.MinZ==0&&b.MaxZ==0&&sx>=b.MinX-0.01&&sx<=b.MaxX+0.01&&sy>=b.MinY-0.01&&sy<=b.MaxY+0.01))throw new InvalidDataException("RH unsupported floor envelope: "+name);
                }
            }
            foreach(var b in relevant){
                if(b.Base=="QryFloor01")continue;
                float dx=MathF.Max(MathF.Max(b.MinX-x,0),x-b.MaxX),dy=MathF.Max(MathF.Max(b.MinY-y,0),y-b.MaxY);
                if(dx*dx+dy*dy>=radius*radius-0.01)continue;
                if(b.MinZ>=144){minimumHeadroom=MathF.Min(minimumHeadroom,b.MinZ-16);continue;}
                if(b.MaxZ>0&&b.MinZ<144)throw new InvalidDataException("RH192/headroom/cohort obstruction: "+name+" / "+b.Name);
            }
            protectedCount++;
        }
        foreach(var p in RedHollow.Pieces.Where(p=>!p.Mercy&&p.Alias!="Fall")){
            bool outside=RedHollowEnvironment.IsSurface("TLM_REF_RH_"+p.Alias);
            float x=p.X-(outside&&p.X>=2944?1024:0),y=p.Y;
            // Labels lie beside the approach; their player stance stays128 back
            // inside the boundary and remains within exact256 activation reach.
            if(outside&&y==64)y=192;
            bool cohort=p.Person||p.Alias.StartsWith("Surface")||p.Alias.StartsWith("Below")||p.Alias.StartsWith("Cage")||p.Alias is "Gallows" or "Released" or "Custody" or "DornWithdraw";
            Point(p.Alias,outside,x,y,cohort?128:96);
        }
        var routes=new[]{
            ("Gap and bypass",true,new[]{(256f,256f),(1280f,256f),(1536f,256f)}),
            ("Mouth hoist",true,new[]{(2304f,256f),(2560f,256f),(2816f,256f),(2816f,384f)}),
            ("Mouth desk and cohort",true,new[]{(3072f,256f),(3072f,896f),(2560f,896f),(2560f,256f)}),
            ("Nine control and break",false,new[]{(6400f,256f),(6400f,384f),(6912f,384f),(6912f,512f)}),
            ("Gallery and return",false,new[]{(9216f,256f),(9472f,256f),(9984f,256f),(9984f,512f),(10240f,512f)})
        };
        foreach(var route in routes)for(int segment=1;segment<route.Item3.Length;segment++)for(int sample=0;sample<=100;sample++){
            var a=route.Item3[segment-1];var b=route.Item3[segment];float t=sample/100f;Point(route.Item1,route.Item2,a.Item1+(b.Item1-a.Item1)*t,a.Item2+(b.Item2-a.Item2)*t,96);
        }
        // New routes keep192width and sampled LAND rise <=32per128units.
        foreach(var route in RedHollowTerrain.Routes)for(int segment=1;segment<route.Points.Length;segment++)for(int sample=0;sample<=100;sample++){
            var a=route.Points[segment-1];var b=route.Points[segment];float t=sample/100f;
            float x=a.X+(b.X-a.X)*t,y=a.Y+(b.Y-a.Y)*t,ground=RedHollowTerrain.Ground(x,y);
            foreach(var offset in new[]{(-96f,0f),(96f,0f),(0f,-96f),(0f,96f)}){
                float px=x+offset.Item1,py=y+offset.Item2;
                if(px<0||px>4096||py<0||py>4096)throw new InvalidDataException("RH route leaves LAND");
                float dx=(RedHollowTerrain.Ground(px+8,py)-RedHollowTerrain.Ground(px-8,py))/16;
                float dy=(RedHollowTerrain.Ground(px,py+8)-RedHollowTerrain.Ground(px,py-8))/16;
                if(MathF.Sqrt(dx*dx+dy*dy)>0.36f)throw new InvalidDataException("RH route LAND slope too steep: "+route.Name);
            }
            foreach(var box in boxes.Where(box=>box.Outside)){
                float dx=MathF.Max(MathF.Max(box.MinX-x,0),x-box.MaxX),dy=MathF.Max(MathF.Max(box.MinY-y,0),y-box.MaxY);
                if(dx*dx+dy*dy>=96*96-0.01)continue;
                if(box.Base=="workshop_ShackMidFloor01B"||box.MaxZ<=ground+16.01||box.MinZ>=ground+192)continue;
                throw new InvalidDataException("RH new route obstructed: "+route.Name+" / "+box.Name);
            }
            protectedCount++;
        }
        // The original court projectile target's direct approach is unobstructed
        // at its actual target height, not merely a player-floor point.
        foreach(var b in boxes.Where(b=>b.Outside&&b.MinZ<=128&&b.MaxZ>=120))if(b.MinX<=768&&b.MaxX>=768&&b.MinY<=512&&b.MaxY>=256)throw new InvalidDataException("RH rope projectile corridor blocked: "+b.Name);
        return new{method="Typed exact model-bound AABBs;192-unit sampled paths, full128-radius cohort envelopes/support and minimum128headroom. Not native collision/navmesh/visibility proof",protectedCount,minimumHeadroom,boxes};
    }
    public static int Fixture(string path){
        try{
            var pieces=RedHollowEnvironment.Geometry();using var json=JsonDocument.Parse(File.ReadAllText(path));
            foreach(var edit in json.RootElement.EnumerateArray()){
                string name=edit.GetProperty("name").GetString()!;int index=Array.FindIndex(pieces,p=>p.Name==name);
                if(index<0)throw new InvalidDataException("Unknown RH geometry edit");var old=pieces[index];
                pieces[index]=old with{X=edit.TryGetProperty("x",out var x)?x.GetSingle():old.X,Y=edit.TryGetProperty("y",out var y)?y.GetSingle():old.Y,Z=edit.TryGetProperty("z",out var z)?z.GetSingle():old.Z,Yaw=edit.TryGetProperty("yaw",out var yaw)?yaw.GetSingle():old.Yaw};
            }
            Console.WriteLine(JsonSerializer.Serialize(Check(pieces)));return 0;
        }catch(InvalidDataException e){Console.Error.WriteLine("REFUSED: "+e.Message);return 1;}
    }
}
