using Mutagen.Bethesda;
using Mutagen.Bethesda.Fallout4;
using Mutagen.Bethesda.Plugins;
using Mutagen.Bethesda.Plugins.Records;
using Noggog;
using System.Text.Json;

// Native FO4 BTXT/ATXT/VTXT, verified against owned LAND0000EDFC and the
// actual Mutagen AlphaLayer:BaseLayer schema. No native mask/MPCD is copied.
public static class OpeningMaterials {
 static float Clamp(float x)=>Math.Clamp(x,0,1);
 static float Smooth(float x){x=Clamp(x);return x*x*(3-2*x);}
 static float Rect(float x,float y,float x0,float y0,float x1,float y1){float dx=MathF.Max(MathF.Max(x0-x,x-x1),0),dy=MathF.Max(MathF.Max(y0-y,y-y1),0);return 1-Smooth(MathF.Sqrt(dx*dx+dy*dy)/96);}
 public static float Gravel(float x,float y){
  float route=1-Smooth((OpeningEnvironment.PathDistance(x,y)-96)/160);
  float hollow=1-Smooth((MathF.Sqrt(MathF.Pow(x-700,2)+MathF.Pow(y-1050,2))-320)/160);
  return MathF.Max(Rect(x,y,128,1408,1536,1920),MathF.Max(MathF.Max(route,hollow),MathF.Max(Rect(x,y,2390,2380,3740,3490),MathF.Max(Rect(x,y,1624,2672,2136,2928),Rect(x,y,2794,3672,3306,3928)))));
 }
 public static float Forest(float x,float y)=> (1-Gravel(x,y))*(.60f+.25f*MathF.Sin(x/370+y/510));
 public static object Apply(IFallout4ModGetter native,Worldspace world,Landscape land){
  ILandscapeTextureGetter Find(string name,uint id){var t=native.LandscapeTextures.Single(t=>t.EditorID==name&&t.FormKey.ID==id);if(t.TextureSet.IsNull)throw new InvalidDataException("Opening material has no actual texture set");return t;}
  var soil=Find("LBlastedForestDirt01",0x125C6C);var forest=Find("LForestFloor01",0x3343C);var gravel=native.LandscapeTextures.Single(t=>t.EditorID=="LDirtGravel01");
  if(forest.Grasses.Count!=3||soil.Grasses.Count!=0||gravel.Grasses.Count!=0)throw new InvalidDataException("Verified opening material grass links changed");
  var grasses=forest.Grasses.Select(g=>native.Grasses.Single(n=>n.FormKey==g.FormKey)).ToArray();
  land.Layers.Clear();land.Textures??=new();land.Textures.Clear();foreach(var t in new[]{soil,forest,gravel})land.Textures.Add(t.ToLink<ILandscapeTextureGetter>());
  var masks=new List<object>();
  foreach(var quadrant in Enum.GetValues<Quadrant>()){
   int q=(int)quadrant,ox=(q&1)*16,oy=(q>>1)*16;
   land.Layers.Add(new BaseLayer{Header=new LayerHeader{Texture=soil.ToLink<ILandscapeTextureGetter>(),Quadrant=quadrant,LayerNumber=ushort.MaxValue}});
   for(int layer=0;layer<2;layer++){
    using var stream=new MemoryStream();using(var writer=new BinaryWriter(stream,System.Text.Encoding.UTF8,true))for(int y=0;y<17;y++)for(int x=0;x<17;x++){
     float px=(ox+x)*128,py=(oy+y)*128,w=layer==0?Forest(px,py):Gravel(px,py);
     writer.Write((ushort)(y*17+x));writer.Write((ushort)0);writer.Write(w);
    }
    byte[] data=stream.ToArray();land.Layers.Add(new AlphaLayer{Header=new LayerHeader{Texture=(layer==0?forest:gravel).ToLink<ILandscapeTextureGetter>(),Quadrant=quadrant,LayerNumber=(ushort)layer},AlphaLayerData=data});
    masks.Add(new{quadrant=q,layer,vertices=289,bytes=data.Length,texture=(layer==0?forest:gravel).EditorID});
   }
  }
  world.Flags&=~Worldspace.Flag.NoGrass;
  return new{schema="Actual native BTXT8/ATXT8/VTXT8 entries; original authored global17x17-per-quadrant masks",baseSoil=soil.FormKey.ToString(),forest=forest.FormKey.ToString(),gravel=gravel.FormKey.ToString(),grassLinks=grasses.Select(g=>new{id=g.EditorID,form=g.FormKey.ToString(),model=g.Model?.File?.ToString()}),masks,nativeVisibility="OPEN: flag+valid native grass links and masks are data, not proof of visible vegetation/material blend"};
 }
}
