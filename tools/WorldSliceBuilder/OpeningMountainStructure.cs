using Mutagen.Bethesda;
using Mutagen.Bethesda.Fallout4;
using Mutagen.Bethesda.Plugins;
using Mutagen.Bethesda.Plugins.Records;
using Noggog;
using System.Text.Json;

// Explicit three-cell sculpt/passive whitelist after all accepted allocations.
// Core physical terrain, actors and quest/camera/runtime bindings are untouched.
public static class OpeningMountainStructure {
 public static object Apply(IFallout4ModGetter native,Fallout4Mod mod,Worldspace world){
  var dir=new DirectoryInfo(AppContext.BaseDirectory);while(dir!=null&&!File.Exists(Path.Combine(dir.FullName,"tools/OpeningMountainStructure/sculpt.json")))dir=dir.Parent;if(dir==null)throw new InvalidDataException("Structure source absent");
  using var source=JsonDocument.Parse(File.ReadAllText(Path.Combine(dir.FullName,"tools/OpeningMountainStructure/sculpt.json")));var s=source.RootElement;
  var cells=world.SubCells.SelectMany(b=>b.Items).SelectMany(b=>b.Items).Where(c=>c.Grid!=null).ToDictionary(c=>(c.Grid!.Point.X,c.Grid.Point.Y));
  var refs=cells.Values.SelectMany(c=>c.Temporary).OfType<PlacedObject>().ToDictionary(r=>r.FormKey.ID);
  var textures=new uint[]{0x3343c,0x21336,0xc55fc}.Select(id=>native.LandscapeTextures.Single(t=>t.FormKey.ID==id)).ToArray();var soil=native.LandscapeTextures.Single(t=>t.FormKey.ID==0x125c6c);
  foreach(var row in s.GetProperty("cells").EnumerateArray()){
   int cx=row.GetProperty("grid")[0].GetInt32(),cy=row.GetProperty("grid")[1].GetInt32();if(!new[]{(1,0),(0,1),(1,1)}.Contains((cx,cy)))throw new InvalidDataException("Only approved visible cells");
   var cell=cells[(cx,cy)];var land=cell.Landscape!;if(land.FormKey.ID!=row.GetProperty("localId").GetUInt32())throw new InvalidDataException("Original LAND identity changed");var h=row.GetProperty("heights");var ns=row.GetProperty("normals");var ws=row.GetProperty("weights");
   var bytes=new Array2d<byte>(33,33,0);var normals=new Array2d<P3UInt8>(33,33,new P3UInt8(0,0,127));
   for(int y=0;y<33;y++)for(int x=0;x<33;x++){
    int height=h[y][x].GetInt32(),before=x>0?h[y][x-1].GetInt32():y>0?h[y-1][0].GetInt32():0,delta=(height-before)/8;if(height%8!=0||delta< -128||delta>127)throw new InvalidDataException("Signed sculpt height overflow");bytes[x,y]=unchecked((byte)(sbyte)delta);
    byte N(int i)=>unchecked((byte)(sbyte)ns[y][x][i].GetInt32());normals[x,y]=new P3UInt8(N(0),N(1),N(2));
   }
   land.VertexHeightMap=new LandscapeVertexHeightMap{Offset=0,HeightMap=bytes};land.VertexNormals=normals;land.Layers!.Clear();
   foreach(var quadrant in Enum.GetValues<Quadrant>()){
    int q=(int)quadrant,ox=(q&1)*16,oy=(q>>1)*16;land.Layers.Add(new BaseLayer{Header=new LayerHeader{Texture=soil.ToLink<ILandscapeTextureGetter>(),Quadrant=quadrant,LayerNumber=ushort.MaxValue}});
    for(int layer=0;layer<3;layer++){
     using var stream=new MemoryStream();using(var writer=new BinaryWriter(stream,System.Text.Encoding.UTF8,true))for(int y=0;y<17;y++)for(int x=0;x<17;x++){writer.Write((ushort)(y*17+x));writer.Write((ushort)0);writer.Write(ws[oy+y][ox+x][layer].GetSingle());}
     land.Layers.Add(new AlphaLayer{Header=new LayerHeader{Texture=textures[layer].ToLink<ILandscapeTextureGetter>(),Quadrant=quadrant,LayerNumber=(ushort)layer},AlphaLayerData=stream.ToArray()});
    }
   }
  }
  foreach(var p in s.GetProperty("moved").EnumerateArray()){
   var r=refs[p.GetProperty("localId").GetUInt32()];if(r.EditorID!=p.GetProperty("id").GetString()||r.EditorID?.StartsWith("TLM_RIDGE_",StringComparison.Ordinal)!=true)throw new InvalidDataException("Non-passive pose substitution");
   var old=p.GetProperty("oldXYZ");if(r.Position!=new P3Float(old[0].GetSingle(),old[1].GetSingle(),old[2].GetSingle()))throw new InvalidDataException("Original passive pose changed");r.Position=new P3Float(p.GetProperty("x").GetSingle(),p.GetProperty("y").GetSingle(),p.GetProperty("z").GetSingle());
  }
  foreach(var p in s.GetProperty("added").EnumerateArray()){
   var donor=native.Statics.Single(t=>t.FormKey.ID==0x2f79b&&t.EditorID=="RockBoulder03");var r=new PlacedObject(mod.GetNextFormKey(),Fallout4Release.Fallout4){EditorID=p.GetProperty("id").GetString(),Position=new P3Float(p.GetProperty("x").GetSingle(),p.GetProperty("y").GetSingle(),p.GetProperty("z").GetSingle()),Rotation=new P3Float(0,0,p.GetProperty("yaw").GetSingle()),Scale=p.GetProperty("scale").GetSingle()};r.Base.SetTo(donor.FormKey);cells[(p.GetProperty("grid")[0].GetInt32(),p.GetProperty("grid")[1].GetInt32())].Temporary.Add(r);
  }
  // The actual low lawn mesh is14.40units high; density12 instead of39 keeps
  // isolated low tufts. No native GRAS/LTEX or global grass settings overridden.
  var grass=native.Grasses.Single(g=>g.FormKey.ID==0x1240f5&&g.EditorID=="PreWarLawnGrassObj03").Duplicate(mod.GetNextFormKey());grass.EditorID="TLM_GRAS_OpeningLowTufts";grass.Density=12;mod.Grasses.Add(grass);
  var leaf=native.LandscapeTextures.Single(t=>t.FormKey.ID==0x3343c).Duplicate(mod.GetNextFormKey());leaf.EditorID="TLM_LTEX_OpeningLowLeafFloor";leaf.Grasses.Clear();leaf.Grasses.Add(grass.ToLink<IGrassGetter>());mod.LandscapeTextures.Add(leaf);
  var core=cells[(0,0)].Landscape!;foreach(var a in core.Layers!.OfType<AlphaLayer>())if(a.Header!.Texture.FormKey.ID==0x3343c)a.Header.Texture.SetTo(leaf.FormKey);
  core.Textures!.Clear();foreach(var key in new[]{soil.FormKey,leaf.FormKey,textures[1].FormKey,textures[2].FormKey})core.Textures.Add(key.ToLink<ILandscapeTextureGetter>());
  return new{scope="Three visible outer ridge cells, explicit passive poses, six rock accents and local low grass",cells=3,moved=s.GetProperty("moved").GetArrayLength(),added=s.GetProperty("added").GetArrayLength(),grass=grass.FormKey.ToString(),leaf=leaf.FormKey.ToString(),native="OPEN: silhouettes/canopy/outcrop contact/grass density; source rays not render proof"};
 }
}

