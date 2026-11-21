using Mutagen.Bethesda;using Mutagen.Bethesda.Fallout4;using Mutagen.Bethesda.Plugins;using Noggog;using Tlm.PluginBuilder;
// New numerical stand-in assets appended after EVERY accepted fixture allocation.
// Existing deliberate variants/models are never silently reset by this module.
public static class BlackstoneFixture {
 public static void Add(Fallout4Mod mod){
  foreach(var asset in Blackstone.Load("layout-models.json").GetProperty("assets").EnumerateObject()){
   var b=asset.Value.GetProperty("bounds").EnumerateArray().Select(x=>x.GetInt16()).ToArray();var old=mod.Statics.SingleOrDefault(s=>s.EditorID==asset.Name);
   if(old!=null){var actual=old.ObjectBounds;if(old.Model?.File?.ToString()!=asset.Value.GetProperty("model").GetString()||!new[]{actual.First.X,actual.First.Y,actual.First.Z,actual.Second.X,actual.Second.Y,actual.Second.Z}.SequenceEqual(b))throw new InvalidDataException("Existing synthetic Blackstone donor collision: "+asset.Name);continue;}
   var item=mod.Statics.AddNew(asset.Name);item.Model=new Model{File=asset.Value.GetProperty("model").GetString()!};item.ObjectBounds.First=new P3Int16(b[0],b[1],b[2]);item.ObjectBounds.Second=new P3Int16(b[3],b[4],b[5]);
  }
  var light=new Light(new FormKey(mod.ModKey,0x517B0),Fallout4Release.Fallout4){EditorID="DefaultLightWhite01NS",Radius=256,Time=-1,Color=System.Drawing.Color.White};mod.Lights.Add(light);
  var door=new Door(new FormKey(mod.ModKey,0x52576),Fallout4Release.Fallout4){EditorID="ShackDoor01",Name="Service door",Model=new Model{File=@"Architecture\Shacks\ShackDoor01.nif"}};door.ObjectBounds.First=new P3Int16(-44,-10,0);door.ObjectBounds.Second=new P3Int16(44,10,192);mod.Doors.Add(door);
  var room=mod.Cells.Records.SelectMany(b=>b.SubBlocks).SelectMany(s=>s.Cells).Single(c=>c.EditorID=="QASmoke");if(room.Lighting!=null)throw new InvalidDataException("Synthetic QASmoke donor unexpectedly already lit");room.Lighting=new CellLighting{AmbientColor=System.Drawing.Color.FromArgb(255,150,150,150),DirectionalColor=System.Drawing.Color.FromArgb(255,200,200,200),DirectionalFade=1};
 }
}
