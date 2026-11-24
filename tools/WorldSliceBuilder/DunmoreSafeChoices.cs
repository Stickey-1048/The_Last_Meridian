using Mutagen.Bethesda.Fallout4;
using Mutagen.Bethesda.Plugins;
public static class DunmoreSafeChoices
{
 public static object Apply(Fallout4Mod mod)
 {
  var message=mod.Messages.Single(m=>m.FormKey==new FormKey(ModKey.FromNameAndExtension("TheLastMeridian.esp"),0x849)&&m.EditorID=="TLM_MSG_A1_DunmoreHold");
  const string caption="Reese Dunmore: \"Fenwick's wagon stays. You can keep walking. Reach for a gun and this gets ugly.\"";
  string[] old={"[Risk combat] Pritchard hangs road-takers. Leave.","[Fight] Let them go.","What kind of share?","[Leave] I'm walking away.","[Call for help] Sheriff! Over here!"};
  if(message.Description.String!=caption||message.MenuButtons.Count!=5||!message.MenuButtons.Select(b=>b.Text?.String).SequenceEqual(old)||message.MenuButtons.Any(b=>b.Conditions.Count!=0))throw new InvalidDataException("Expected exact current Dunmore caption and unconditional five choices");
  var buttons=message.MenuButtons.ToArray();buttons[3].Text="[Leave the caravan] I'm walking away.";
  int[] order={4,3,2,0,1};message.MenuButtons.Clear();foreach(int i in order)message.MenuButtons.Add(buttons[i]);
  if(message.Description.String!=caption||"[Leave the caravan] I'm walking away.".Length>48)throw new InvalidDataException("Dunmore caption/button bounds changed");
  return new{scope="Existing choices reordered only; paired Act1 runtime required, no autoanswers/branch/fate/voice changes",form=message.FormKey.ToString(),oldIndicesInNewOrder=order,buttons=message.MenuButtons.Select(b=>b.Text?.String).ToArray(),captionUnchanged=true};
 }
}
