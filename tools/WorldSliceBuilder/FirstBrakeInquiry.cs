using Mutagen.Bethesda;
using Mutagen.Bethesda.Fallout4;
using Mutagen.Bethesda.Plugins;
using Noggog;
using System.Text.Json;
using System.Security.Cryptography;
public static class FirstBrakeInquiry
{
 public static object Add(Fallout4Mod mod)
 {
  string path=Path.Combine(AppContext.BaseDirectory,"../../../../FirstBrakeInquiry/contract.json");byte[] bytes=File.ReadAllBytes(path);
  if(Convert.ToHexString(SHA256.HashData(bytes))!="21DFB0BB760C6DAAB630E3B77FCD170BB07970AB8DA663A181E89B438F3E6EAE")throw new InvalidDataException("Approved local inquiry contract differs");
  using var doc=JsonDocument.Parse(bytes);var contract=doc.RootElement;
  var a1=mod.Quests.Single(q=>q.EditorID=="TLM_WS_A1");var walk=a1.VirtualMachineAdapter!.Scripts.Single(s=>s.Name=="TLM:Act1Walk");
  var pike=a1.Aliases!.OfType<QuestReferenceAlias>().Single(a=>a.ID==19&&a.Name=="Pike").ForcedReference.FormKey;
  var sheriff=a1.Aliases!.OfType<QuestReferenceAlias>().Single(a=>a.ID==18&&a.Name=="Pritchard").ForcedReference.FormKey;
  if(pike!=new FormKey(mod.ModKey,0x911)||sheriff!=new FormKey(mod.ModKey,0x910))throw new InvalidDataException("Inquiry must use existing original exterior actors");
  foreach(var item in new[]{("OpeningOriginalPike",pike),("BlackLedgerOriginalSheriff",sheriff)}){
   var p=walk.Properties.OfType<ScriptObjectProperty>().Single(p=>p.Name==item.Item1);
   if(p.Alias!=-1||p.Object.FormKey!=item.Item2)throw new InvalidDataException("Inquiry original actor identity differs");
  }
  string[] names={"SayInquiryOffer","SayInquiryOfferDead","SayInquirySheriffMenu","SayInquiryPending","SayInquiryAdaMenu","SayInquiryHistory","SayInquiryReport","SayInquiryReported","SayInquiryUnavailable"};
  if(walk.Properties.Any(p=>p.Name=="FirstBrakeInquiry"||names.Contains(p.Name)))throw new InvalidDataException("Inquiry properties already exist");
  var q=mod.Quests.AddNew("TLM_FirstBrakeInquiry");if(q.FormKey.ID!=0xB6B)throw new InvalidDataException("Inquiry must append after roof B6A");
  q.Name=contract.GetProperty("quest").GetProperty("title").GetString()!;
  q.Data=new QuestData{Flags=Quest.Flag.WarnOnAliasFillFailure,Priority=30,Type=Quest.TypeEnum.None};q.UnusedConditions=new ExtendedList<Condition>();q.Aliases=new ExtendedList<AQuestAlias>();
  foreach(var row in contract.GetProperty("quest").GetProperty("aliases").EnumerateArray()){
   int id=row.GetProperty("id").GetInt32();if(id is not(0 or 1))throw new InvalidDataException("Unexpected journal alias");
   var a=new QuestReferenceAlias{ID=(uint)id,Name=row.GetProperty("name").GetString()!,Flags=AQuestAlias.Flag.Optional|AQuestAlias.Flag.AllowDead|AQuestAlias.Flag.AllowDisabled};a.ForcedReference.SetTo(id==0?pike:sheriff);q.Aliases.Add(a);
  }
  foreach(var row in contract.GetProperty("quest").GetProperty("objectives").EnumerateArray()){
   var o=new QuestObjective{Index=(ushort)row.GetProperty("id").GetInt32(),DisplayText=row.GetProperty("text").GetString()!,Flags=default};o.Targets.Add(new QuestObjectiveTarget{AliasID=row.GetProperty("targetAlias").GetInt32()});q.Objectives.Add(o);
  }
  void Prop(string name,FormKey key)=>walk.Properties.Add(new ScriptObjectProperty{Name=name,Flags=ScriptProperty.Flag.Edited,Object=new FormLink<IFallout4MajorRecordGetter>(key),Alias=-1});
  Prop("FirstBrakeInquiry",q.FormKey);int index=0;var messages=new List<object>();
  foreach(var row in contract.GetProperty("messages").EnumerateArray()){
   string name=row.GetProperty("property").GetString()!;if(index>=names.Length||name!=names[index])throw new InvalidDataException("Inquiry message order differs");
   var msg=mod.Messages.AddNew("TLM_MSG_"+name);if(msg.FormKey.ID!=0xB6C+index)throw new InvalidDataException("Inquiry message allocation differs");
   msg.Description=row.GetProperty("text").GetString()!;if(msg.Description.String!.Length>240)throw new InvalidDataException("Inquiry caption exceeds finite budget");msg.Flags=Message.Flag.MessageBox;
   foreach(var b in row.GetProperty("buttons").EnumerateArray())msg.MenuButtons.Add(new MessageButton{Text=b.GetString()!});Prop(name,msg.FormKey);messages.Add(new{name,form=msg.FormKey.ToString()});index++;
  }
  if(index!=9||q.Aliases.Count!=2||q.Objectives.Count!=2||q.VirtualMachineAdapter!=null)throw new InvalidDataException("Inquiry must remain scriptless two-marker journal");
  return new{scope="Optional local inquiry journal/messages; no new interaction actor/ref/stage/reward/script/masterchange",quest=q.FormKey.ToString(),messages,properties=10,originalPike=pike.ToString(),originalPritchard=sheriff.ToString()};
 }
}

