using Mutagen.Bethesda;
using Mutagen.Bethesda.Fallout4;
using Mutagen.Bethesda.Plugins;
using Mutagen.Bethesda.Plugins.Records;
using Noggog;
using System.Buffers.Binary;
using System.Text.Json;

// Original adjacent LAND only. Core terrain/refs/quests are never rewritten.
public static class AppalachianRidges {
 static float Smooth(float t){t=Math.Clamp(t,0,1);return t*t*(3-2*t);}
 public static object Apply(IFallout4ModGetter native,Fallout4Mod mod,Worldspace world){
  var cores=world.SubCells.SelectMany(b=>b.Items).SelectMany(s=>s.Items).Where(c=>c.Landscape!=null).ToArray();if(cores.Length!=2)throw new InvalidDataException("Ridges require exact two accepted core LANDs");
  var coreH=new Dictionary<(int,int),float>();var coreN=new Dictionary<(int,int),P3UInt8>();var edgeWeights=new Dictionary<(int,int),float[]>();
  foreach(var c in cores){
   var l=c.Landscape!;var m=l.VertexHeightMap!;float[,] h=new float[33,33];int ox=c.Grid!.Point.X*32,oy=c.Grid.Point.Y*32;
   for(int y=0;y<33;y++)for(int x=0;x<33;x++){h[x,y]=(x>0?h[x-1,y]:y>0?h[0,y-1]:m.Offset*8)+unchecked((sbyte)m.HeightMap[x,y])*8;coreH.TryAdd((ox+x,oy+y),h[x,y]);coreN.TryAdd((ox+x,oy+y),l.VertexNormals![x,y]);}
   foreach(var a in l.Layers!.OfType<AlphaLayer>()){
    int layer=a.Header.Texture.FormKey.ID==0x3343c?0:a.Header.Texture.FormKey.ID==135990?1:-1;if(layer<0)throw new InvalidDataException("Core material unexpected");int q=(int)a.Header.Quadrant;
    var bytes=a.AlphaLayerData!.Value.ToArray();if(bytes.Length!=2312)throw new InvalidDataException("Core native alpha size");
    for(int i=0;i<289;i++){int x=i%17+(q&1)*16,y=i/17+(q>>1)*16;if(x!=0&&x!=32&&y!=0&&y!=32)continue;var key=(ox+x,oy+y);if(!edgeWeights.TryGetValue(key,out var w))edgeWeights[key]=w=new float[3];w[layer]=BinaryPrimitives.ReadSingleLittleEndian(bytes.AsSpan(i*8+4,4));}
   }
  }
  float H(int gx,int gy){
   if(coreH.TryGetValue((gx,gy),out var old))return old;
   float x=gx*128,y=gy*128;if(x<=-4096||x>=8192||y<=-8192||y>=8192)return 0;
   float dx=MathF.Max(MathF.Max(-x,x-4096),0),dy=MathF.Max(MathF.Max(-4096-y,y-4096),0),d=MathF.Sqrt(dx*dx+dy*dy);
   float Bell(float distance,float width)=>MathF.Exp(-distance*distance/(width*width));
   // Winding overlapping folds, unequal knobs and shoulders, not four walls.
   float west=(2550+330*MathF.Sin(y/1350))*Bell(x+2050-420*MathF.Sin(y/1850),1150);
   float east=(2320+290*MathF.Cos(y/1550+.7f))*Bell(x-6140-350*MathF.Sin(y/2100+.4f),1080);
   float north=(2530+260*MathF.Sin(x/1200))*Bell(y-6060-360*MathF.Sin(x/1750),1190);
   float south=(2240+310*MathF.Cos(x/1450))*Bell(y+6180-390*MathF.Sin(x/1650),1120);
   float shoulder=230*Smooth(d/1500)*(1+MathF.Sin(x/850+y/1300))*.5f;
   float edge=MathF.Min(MathF.Min(x+4096,8192-x),MathF.Min(y+8192,8192-y));float z=(MathF.Max(MathF.Max(west,east),MathF.Max(north,south))*Smooth(d/896)+shoulder)*Smooth((edge-128)/896);
   return MathF.Round(z/8)*8;
  }
  float Ground(float x,float y,bool upper){int gx=(int)MathF.Floor(x/128),gy=(int)MathF.Floor(y/128);float u=x/128-gx,v=y/128-gy,a=H(gx,gy),b=H(gx+1,gy),c=H(gx,gy+1),d=H(gx+1,gy+1);float one=v<=u?a+(b-a)*u+(d-b)*v:a+(d-c)*u+(c-a)*v,two=u+v<=1?a+(b-a)*u+(c-a)*v:d+(c-d)*(1-u)+(b-d)*(1-v);return upper?MathF.Max(one,two):MathF.Min(one,two);}
  P3UInt8 Normal(int gx,int gy){if(coreN.TryGetValue((gx,gy),out var n))return n;float dx=(H(gx+1,gy)-H(gx-1,gy))/256,dy=(H(gx,gy+1)-H(gx,gy-1))/256,len=MathF.Sqrt(1+dx*dx+dy*dy);byte N(float v)=>unchecked((byte)(sbyte)Math.Clamp((int)MathF.Round(v/len*127),-127,127));return new P3UInt8(N(-dx),N(-dy),N(1));}
  float[] Weights(int gx,int gy){if(edgeWeights.TryGetValue((gx,gy),out var old))return old;float h=H(gx,gy),dx=(H(gx+1,gy)-H(gx-1,gy))/256,dy=(H(gx,gy+1)-H(gx,gy-1))/256,slope=MathF.Sqrt(dx*dx+dy*dy),rock=Math.Clamp((h-1650)/1200+(slope-.55f)*.45f,0,.92f),gravel=(1-rock)*.08f;return new[]{(1-rock-gravel)*(.55f+.2f*MathF.Sin(gx*.18f+gy*.11f)),gravel,rock};}
  var soil=native.LandscapeTextures.Single(t=>t.FormKey.ID==0x125c6c&&t.EditorID=="LBlastedForestDirt01");var forest=native.LandscapeTextures.Single(t=>t.FormKey.ID==0x3343c&&t.EditorID=="LForestFloor01");var gravel=native.LandscapeTextures.Single(t=>t.FormKey.ID==135990&&t.EditorID=="LDirtGravel01");var rock=native.LandscapeTextures.Single(t=>t.FormKey.ID==0xc55fc&&t.EditorID=="LNFoothillsRubbleRock01");
  if(rock.TextureSet.FormKey.ID!=0xc55f6||rock.Grasses.Count!=0)throw new InvalidDataException("Actual native foothill rock material differs");
  var textures=new[]{forest,gravel,rock};var receipt=new List<object>();var props=new List<object>();
  var dir=new DirectoryInfo(AppContext.BaseDirectory);while(dir!=null&&!File.Exists(Path.Combine(dir.FullName,"tools/AppalachianRidges/models.json")))dir=dir.Parent;if(dir==null)throw new InvalidDataException("Ridge model metadata absent");using var metadata=JsonDocument.Parse(File.ReadAllText(Path.Combine(dir.FullName,"tools/AppalachianRidges/models.json")));var assets=metadata.RootElement.GetProperty("assets");
  int cellIndex=0;
  for(int cy=-2;cy<=1;cy++)for(int cx=-1;cx<=1;cx++){
   if(cx==0&&(cy==0||cy==-1))continue;
   short bx=checked((short)Math.Floor(cx/32d)),by=checked((short)Math.Floor(cy/32d)),sx=checked((short)Math.Floor(cx/8d)),sy=checked((short)Math.Floor(cy/8d));var block=world.SubCells.SingleOrDefault(b=>b.BlockNumberX==bx&&b.BlockNumberY==by);if(block==null){block=new WorldspaceBlock{BlockNumberX=bx,BlockNumberY=by,GroupType=GroupTypeEnum.ExteriorCellBlock};world.SubCells.Add(block);}var sub=block.Items.SingleOrDefault(s=>s.BlockNumberX==sx&&s.BlockNumberY==sy);if(sub==null){sub=new WorldspaceSubBlock{BlockNumberX=sx,BlockNumberY=sy,GroupType=GroupTypeEnum.ExteriorCellSubBlock};block.Items.Add(sub);}
   string sign(int n)=>n<0?"m"+(-n):"p"+n;string label=sign(cx)+"_"+sign(cy);var cell=new Cell(mod.GetNextFormKey(),Fallout4Release.Fallout4){EditorID="TLM_RIDGE_Cell_"+label,Name="Meridian wooded ridge",Grid=new CellGrid{Point=new P2Int(cx,cy)},WaterHeight=-2048};sub.Items.Add(cell);
   var bytes=new Array2d<byte>(33,33,0);var normals=new Array2d<P3UInt8>(33,33,new P3UInt8(0,0,127));float min=float.MaxValue,max=float.MinValue;
   for(int y=0;y<33;y++)for(int x=0;x<33;x++){int gx=cx*32+x,gy=cy*32+y;float h=H(gx,gy);int before=x>0?(int)H(gx-1,gy):y>0?(int)H(gx,gy-1):0,delta=((int)h-before)/8;if(delta< -128||delta>127)throw new InvalidDataException("Ridge VHGT delta overflow");bytes[x,y]=unchecked((byte)(sbyte)delta);normals[x,y]=Normal(gx,gy);min=MathF.Min(min,h);max=MathF.Max(max,h);}
   var land=new Landscape(mod.GetNextFormKey(),Fallout4Release.Fallout4){DATA=new byte[]{0x1d,0,0,0},VertexHeightMap=new LandscapeVertexHeightMap{Offset=0,HeightMap=bytes},VertexNormals=normals,Textures=new()};cell.Landscape=land;foreach(var t in new[]{soil,forest,gravel,rock})land.Textures.Add(t.ToLink<ILandscapeTextureGetter>());
   foreach(var q in Enum.GetValues<Quadrant>()){int ox=((int)q&1)*16,oy=((int)q>>1)*16;land.Layers.Add(new BaseLayer{Header=new LayerHeader{Texture=soil.ToLink<ILandscapeTextureGetter>(),Quadrant=q,LayerNumber=ushort.MaxValue}});for(int layer=0;layer<3;layer++){using var stream=new MemoryStream();using(var writer=new BinaryWriter(stream,System.Text.Encoding.UTF8,true))for(int y=0;y<17;y++)for(int x=0;x<17;x++){writer.Write((ushort)(y*17+x));writer.Write((ushort)0);writer.Write(Weights(cx*32+ox+x,cy*32+oy+y)[layer]);}land.Layers.Add(new AlphaLayer{Header=new LayerHeader{Texture=textures[layer].ToLink<ILandscapeTextureGetter>(),Quadrant=q,LayerNumber=(ushort)layer},AlphaLayerData=stream.ToArray()});}}
   void Put(string role,string asset,float wantedX,float wantedY,float scale){
    var a=assets.GetProperty(asset);var donor=native.Statics.Single(t=>t.EditorID==asset&&t.FormKey.ID==Convert.ToUInt32(a.GetProperty("id").GetString(),16));if(donor.Model?.File?.ToString()!=a.GetProperty("model").GetString()||donor.VirtualMachineAdapter!=null)throw new InvalidDataException("Ridge exact passive donor changed");
    var foot=a.GetProperty("nif").GetProperty("bottomBandBounds").EnumerateArray().Select(v=>v.GetSingle()*scale).ToArray();var render=a.GetProperty("nif").GetProperty("renderBounds").EnumerateArray().Select(v=>v.GetSingle()*scale).ToArray();float best=float.MaxValue,x=0,y=0,low=0,high=0;float yaw=(cellIndex*.47f+props.Count*.31f)%MathF.Tau;
    foreach(int dx in new[]{0,-128,128,-256,256,-512,512,-768,768})foreach(int dy in new[]{0,-128,128,-256,256,-512,512,-768,768}){float px=wantedX+dx,py=wantedY+dy,rad=MathF.Max(MathF.Max(MathF.Abs(render[0]),render[3]),MathF.Max(MathF.Abs(render[1]),render[4]));if(px-rad<cx*4096+128||px+rad>(cx+1)*4096-128||py-rad<cy*4096+128||py+rad>(cy+1)*4096-128||Ground(px,py,true)<240)continue;float lo=float.MaxValue,hi=float.MinValue;foreach(float fx in new[]{foot[0],0,foot[3]})foreach(float fy in new[]{foot[1],0,foot[4]}){float xx=px+fx*MathF.Cos(yaw)+fy*MathF.Sin(yaw),yy=py+fy*MathF.Cos(yaw)-fx*MathF.Sin(yaw);lo=MathF.Min(lo,Ground(xx,yy,false));hi=MathF.Max(hi,Ground(xx,yy,true));}if(hi-lo>(asset=="RockPileL01"?110:56))continue;float cost=hi-lo+MathF.Sqrt(dx*dx+dy*dy)*.12f;if(cost<best){best=cost;x=px;y=py;low=lo;high=hi;}}
    if(best==float.MaxValue)return; // Optional scenery is omitted when no measured safe footing exists.
    float z=low-foot[5]-3;var r=new PlacedObject(mod.GetNextFormKey(),Fallout4Release.Fallout4){EditorID="TLM_RIDGE_"+label+"_"+role,Position=new P3Float(x,y,z),Rotation=new P3Float(0,0,yaw),Scale=scale};r.Base.SetTo(donor.FormKey);cell.Temporary.Add(r);props.Add(new{id=r.EditorID,form=r.FormKey.ToString(),cell=cell.EditorID,asset,x,y,z,yaw,scale,groundMin=low,groundMax=high});
   }
   int cluster=0;foreach(var c in new[]{(1152+(cellIndex%3)*128,1152+(cellIndex%2)*256),(2816-(cellIndex%2)*192,2816-(cellIndex%3)*128)}){float x=cx*4096+c.Item1,y=cy*4096+c.Item2;string prefix="G"+(++cluster);Put(prefix+"A","TreeMaplePreWar03Gr",x,y,.72f);Put(prefix+"B","TreeMaplePreWar03Gr",x+224,y+128,.90f);Put(prefix+"C","TreeMaplePreWar06Gr",x-192,y+288,.85f);Put(prefix+"D","TreeMaplePreWar05Gr",x+384,y-160,.95f);Put(prefix+"E","TreeCedarShrub01",x-256,y-224,.90f);}
   Put("StoneA","RockBoulder03",cx*4096+1664,cy*4096+2048,1.4f);Put("StoneB","RockBoulder03",cx*4096+2944,cy*4096+1792,1.8f);Put("CrestRock","RockPileL01",cx*4096+2048,cy*4096+2304,1);
   receipt.Add(new{cell=cell.EditorID,form=cell.FormKey.ToString(),grid=new[]{cx,cy},minimum=min,maximum=max,land=land.FormKey.ToString()});cellIndex++;
  }
  world.ObjectBoundsMin=new P2Float(-1,-2);world.ObjectBoundsMax=new P2Float(2,2);
  return new{scope="Ten adjacent original ridge cells; exact two playable cores retained",cells=receipt,props,material=new{rock=rock.FormKey.ToString(),textureSet=rock.TextureSet.FormKey.ToString()},native="OPEN: cell residency/LOD, actual horizon/foliage/collision; not a finished limitless world"};
 }
}

