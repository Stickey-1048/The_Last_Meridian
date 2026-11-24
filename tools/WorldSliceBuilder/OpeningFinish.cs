using Mutagen.Bethesda;
using Mutagen.Bethesda.Fallout4;
using Mutagen.Bethesda.Plugins;
using Mutagen.Bethesda.Plugins.Records;
using Noggog;
using System.Buffers.Binary;
using System.Text.Json;

// Production opening art pass. Runs LAST: accepted actors/props/ridge LAND
// allocations remain literal, while only the original opening paint changes.
public static class OpeningFinish {
 static float Smooth(float t){t=Math.Clamp(t,0,1);return t*t*(3-2*t);}
 static float Ellipse(float x,float y,float cx,float cy,float rx,float ry)=>1-Smooth((MathF.Sqrt(MathF.Pow((x-cx)/rx,2)+MathF.Pow((y-cy)/ry,2))-.7f)/.5f);
 public static object Apply(IFallout4ModGetter native,Fallout4Mod mod,Worldspace world,Cell cell,Landscape land){
  var old=new Dictionary<(int,int),float[]>();
  foreach(var a in land.Layers!.OfType<AlphaLayer>()){
   var header=a.Header??throw new InvalidDataException("Missing alpha header");int layer=header.Texture.FormKey.ID==0x3343c?0:header.Texture.FormKey.ID==0x21336?1:-1;if(layer<0)throw new InvalidDataException("Expected accepted two-layer opening");
   int q=(int)header.Quadrant;var bytes=a.AlphaLayerData!.Value.ToArray();
   for(int i=0;i<289;i++){int x=i%17+(q&1)*16,y=i/17+(q>>1)*16;if(!old.TryGetValue((x,y),out var w))old[(x,y)]=w=new float[3];w[layer]=BinaryPrimitives.ReadSingleLittleEndian(bytes.AsSpan(i*8+4,4));}
  }
  float[,] h=new float[33,33];var map=land.VertexHeightMap!;
  for(int y=0;y<33;y++)for(int x=0;x<33;x++)h[x,y]=(x>0?h[x-1,y]:y>0?h[0,y-1]:map.Offset*8)+unchecked((sbyte)((IReadOnlyArray2d<byte>)map.HeightMap)[x,y])*8;
  float[] Weights(int ix,int iy){
   if(ix is 0 or 32||iy is 0 or 32)return old[(ix,iy)]; // exact frozen mountain seams
   float x=ix*128,y=iy*128;
   float worn=1-Smooth((OpeningEnvironment.PathDistance(x,y)-56)/112);
   float ballast=Ellipse(x,y,810,1710,650,220); // real boxcar apron, irregular edges
   float dispatch=Ellipse(x,y,710,1030,270,200)*.72f;
   float yard=Ellipse(x,y,3048,2530,460,160)*.70f;
   float storage=Ellipse(x,y,1880,2800,230,115)*.70f;
   float grain=Ellipse(x,y,3050,3800,240,110)*.70f;
   float noise=.92f+.08f*MathF.Sin(x/173+y/239);
   float gravel=MathF.Max(worn*.92f,MathF.Max(ballast*.88f,MathF.Max(dispatch,MathF.Max(yard,MathF.Max(storage,grain)))))*noise;
   float dx=(h[ix+1,iy]-h[ix-1,iy])/256,dy=(h[ix,iy+1]-h[ix,iy-1])/256,slope=MathF.Sqrt(dx*dx+dy*dy);
   float rock=(1-gravel)*Math.Clamp((slope-.30f)/.8f,0,.80f)*(.80f+.20f*MathF.Sin(x/283-y/317));
   float forest=(1-gravel-rock)*(.88f+.10f*MathF.Sin(x/211+y/353));
   return new[]{forest,gravel,rock};
  }
  var soil=native.LandscapeTextures.Single(t=>t.FormKey.ID==0x125c6c&&t.EditorID=="LBlastedForestDirt01");var forest=native.LandscapeTextures.Single(t=>t.FormKey.ID==0x3343c&&t.EditorID=="LForestFloor01");var gravel=native.LandscapeTextures.Single(t=>t.FormKey.ID==0x21336&&t.EditorID=="LDirtGravel01");var rock=native.LandscapeTextures.Single(t=>t.FormKey.ID==0xc55fc&&t.EditorID=="LNFoothillsRubbleRock01");var layers=new[]{forest,gravel,rock};
  land.Layers.Clear();land.Textures!.Clear();foreach(var t in new[]{soil,forest,gravel,rock})land.Textures.Add(t.ToLink<ILandscapeTextureGetter>());
  foreach(var quadrant in Enum.GetValues<Quadrant>()){
   int q=(int)quadrant,ox=(q&1)*16,oy=(q>>1)*16;
   land.Layers.Add(new BaseLayer{Header=new LayerHeader{Texture=soil.ToLink<ILandscapeTextureGetter>(),Quadrant=quadrant,LayerNumber=ushort.MaxValue}});
   for(int layer=0;layer<3;layer++){
    using var stream=new MemoryStream();using(var writer=new BinaryWriter(stream,System.Text.Encoding.UTF8,true))for(int y=0;y<17;y++)for(int x=0;x<17;x++){writer.Write((ushort)(y*17+x));writer.Write((ushort)0);writer.Write(Weights(ox+x,oy+y)[layer]);}
    land.Layers.Add(new AlphaLayer{Header=new LayerHeader{Texture=layers[layer].ToLink<ILandscapeTextureGetter>(),Quadrant=quadrant,LayerNumber=(ushort)layer},AlphaLayerData=stream.ToArray()});
   }
  }
  var climate=native.Climates.Single(c=>c.FormKey.ID==0x15f&&c.EditorID=="DefaultClimate").Duplicate(mod.GetNextFormKey());climate.EditorID="TLM_CLMT_OpeningReadable";
  var weathers=climate.Weathers??throw new InvalidDataException("Native weather list absent");weathers.RemoveAll(t=>t.Weather.FormKey.ID!=0x2b52a&&t.Weather.FormKey.ID!=0x1d670e&&t.Weather.FormKey.ID!=0x1c8556);
  foreach(var t in weathers)t.Chance=t.Weather.FormKey.ID==0x2b52a?84:8;
  if(weathers.Count!=3)throw new InvalidDataException("Exact readable stock climate choices missing");mod.Climates.Add(climate);world.Climate.SetTo(climate.FormKey);
  return new{scope="Own readable production climate and opening-only wear/leaf/rock paint; original terrain and ridge records retained",climate=climate.FormKey.ToString(),weather=weathers.Select(t=>new{weather=t.Weather.FormKey.ToString(),weight=t.Chance}),paint="Native BTXT/ATXT/VTXT masks, core border weights literal; no VHGT/VNML/water change",furnishing=AddProps(native,mod,cell)};
 }
 static object AddProps(IFallout4ModGetter native,Fallout4Mod mod,Cell cell){
  var dir=new DirectoryInfo(AppContext.BaseDirectory);while(dir!=null&&!File.Exists(Path.Combine(dir.FullName,"tools/OpeningProductionFinish/placements.json")))dir=dir.Parent;if(dir==null)throw new InvalidDataException("Finish source plan absent");
  using var plan=JsonDocument.Parse(File.ReadAllText(Path.Combine(dir.FullName,"tools/OpeningProductionFinish/placements.json")));using var metadata=JsonDocument.Parse(File.ReadAllText(Path.Combine(dir.FullName,"tools/OpeningProductionFinish/models.json")));var assets=metadata.RootElement.GetProperty("assets");var refs=new List<object>();
  foreach(var p in plan.RootElement.GetProperty("placements").EnumerateArray()){
   string asset=p.GetProperty("asset").GetString()!,kind=p.GetProperty("kind").GetString()!;var a=assets.GetProperty(asset);uint id=Convert.ToUInt32(a.GetProperty("id").GetString(),16);FormKey key;string? model;
   switch(kind){
    case "STAT":var s=native.Statics.Single(s=>s.FormKey.ID==id&&s.EditorID==asset);key=s.FormKey;model=s.Model?.File?.ToString();break;
    case "FURN":var f=native.Furniture.Single(s=>s.FormKey.ID==id&&s.EditorID==asset);key=f.FormKey;model=f.Model?.File?.ToString();break;
    case "MISC":var m=native.MiscItems.Single(s=>s.FormKey.ID==id&&s.EditorID==asset);key=m.FormKey;model=m.Model?.File?.ToString();break;
    case "ALCH":var food=native.Ingestibles.Single(s=>s.FormKey.ID==id&&s.EditorID==asset);key=food.FormKey;model=food.Model?.File?.ToString();break;
    case "LIGH":var l=native.Lights.Single(s=>s.FormKey.ID==id&&s.EditorID==asset);if(l.Radius!=256||l.VirtualMachineAdapter!=null)throw new InvalidDataException("Warm light donor differs");key=l.FormKey;model=l.Model?.File?.ToString();break;
    default:throw new InvalidDataException("Unapproved finish donor kind");
   }
   if(model!=a.GetProperty("model").GetString())throw new InvalidDataException("Finish exact native model path changed");
   var placed=new PlacedObject(mod.GetNextFormKey(),Fallout4Release.Fallout4){EditorID=p.GetProperty("id").GetString(),Position=new P3Float(p.GetProperty("x").GetSingle(),p.GetProperty("y").GetSingle(),p.GetProperty("z").GetSingle()),Rotation=new P3Float(0,0,p.GetProperty("yaw").GetSingle()),Scale=p.GetProperty("scale").GetSingle()};placed.Base.SetTo(key);cell.Temporary.Add(placed);refs.Add(new{id=placed.EditorID,form=placed.FormKey.ToString(),asset,kind});
  }
  return refs;
 }
}



