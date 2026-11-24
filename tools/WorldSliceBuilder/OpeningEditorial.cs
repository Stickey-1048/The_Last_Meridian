using Mutagen.Bethesda.Fallout4;
using System.Text.Json;
public static class OpeningEditorial
{
 public static object Apply(Fallout4Mod mod)
 {
  string path=Path.Combine(AppContext.BaseDirectory,"../../../../OpeningEditorial/copy.json");
  using var source=JsonDocument.Parse(File.ReadAllText(path));var rows=source.RootElement.GetProperty("messages").EnumerateArray().ToArray();
  uint[] expected={0xB5F,0xB6C,0xB6D,0xB73};
  if(rows.Length!=4||!rows.Select(r=>r.GetProperty("localId").GetUInt32()).SequenceEqual(expected))throw new InvalidDataException("Editorial scope must remain four existing unvoiced messages");
  var changes=new List<object>();
  foreach(var row in rows){
   uint id=row.GetProperty("localId").GetUInt32();string edid=row.GetProperty("editorId").GetString()!;string before=row.GetProperty("old").GetString()!;string after=row.GetProperty("new").GetString()!;
   var message=mod.Messages.Single(m=>m.FormKey.ID==id&&m.EditorID==edid);
   if(message.Description.String!=before||after.Length>240||after.Length==0||after.Any(c=>c>127))throw new InvalidDataException("Editorial existing caption/budget differs: "+edid);
   message.Description=after;changes.Add(new{form=message.FormKey.ToString(),edid,before,after,characters=after.Length});
  }
  return new{scope="Four existing unvoiced DESC changes only; no actor/quest/button/voice/logic change",changes};
 }
}
