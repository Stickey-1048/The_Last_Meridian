using Mutagen.Bethesda;
using Mutagen.Bethesda.Fallout4;
using Mutagen.Bethesda.Plugins;
using Noggog;
public static partial class WorldStory {
 public static readonly Dictionary<string,(float X,float Y,float Z)> BlackLedgerSites=new(){["Entry"]=(3120,2540,12),["MercyReturn"]=(3560,2960,16),["Public"]=(3560,3010,12),["Finish"]=(3560,3070,12)};
 public static object? CompleteBlackLedgerEntry(Fallout4Mod mod,Worldspace world,IFallout4ModGetter source){
  var section=mod.Quests.Single(q=>q.EditorID=="TLM_WS_A1");var walk=section.VirtualMachineAdapter!.Scripts.Single(s=>s.Name=="TLM:Act1Walk");
  var main=source.Quests.SingleOrDefault(q=>q.EditorID=="TLM_MQ04");var original=source.Quests.SingleOrDefault(q=>q.EditorID=="TLM_BL_Entry");
  var binding=walk.Properties.Where(p=>p.Name=="TLM_BlackLedgerEntry").ToArray();var authority=walk.Properties.Where(p=>p.Name=="TLM_BlackLedger").ToArray();
  if(main==null&&original==null){if(binding.Length!=0||authority.Length!=0)throw new InvalidDataException("Partial Black Ledger old source");return null;}
  if(main==null||original==null||binding.Length!=1||authority.Length!=1||binding[0] is not ScriptObjectProperty door||door.Object.FormKey!=original.FormKey||authority[0] is not ScriptObjectProperty ledger||ledger.Object.FormKey!=main.FormKey)throw new InvalidDataException("Black Ledger authority/entry substitution");
  if(main.VirtualMachineAdapter?.Scripts.Select(s=>s.Name).OrderBy(s=>s).SequenceEqual(new[]{"TLM:BlackLedgerWalk","TLM:MQ04Quest"})!=true)throw new InvalidDataException("Single Black Ledger ledger/controller required");
  // Only these new identity properties are translated from source actors to
  // their already existing exterior originals. Never nominate a new actor.
  var sourceSection=source.Quests.Single(q=>q.EditorID=="TLM_A1");
  foreach(var role in new[]{("BlackLedgerOriginalSheriff","Pritchard"),("BlackLedgerOriginalVane","Vane"),("BlackLedgerOriginalHaskell","Haskell")}){
   var expectedSource=sourceSection.Aliases!.OfType<IQuestReferenceAliasGetter>().Single(a=>a.Name==role.Item2).ForcedReference.FormKey;
   var expectedExterior=section.Aliases!.OfType<IQuestReferenceAliasGetter>().Single(a=>a.Name==role.Item2).ForcedReference.FormKey;
   var prop=walk.Properties.OfType<ScriptObjectProperty>().Single(p=>p.Name==role.Item1);
   if(prop.Alias!=-1||prop.Object.FormKey!=expectedSource)throw new InvalidDataException("Black Ledger source original property substituted "+role.Item2);
   prop.Object.SetTo(expectedExterior);
  }
  var refs=source.Cells.Records.SelectMany(b=>b.SubBlocks).SelectMany(b=>b.Cells).SelectMany(c=>c.Persistent.Concat(c.Temporary)).ToDictionary(r=>r.FormKey);
  var clone=original.Duplicate(mod.GetNextFormKey());clone.EditorID="TLM_WS_BL_Entry";clone.Name="Black Ledger exterior travel/read controls";
  var aliases=clone.Aliases!.OfType<QuestReferenceAlias>().ToArray();if(aliases.Length!=4||!aliases.Select(a=>a.Name!).OrderBy(x=>x).SequenceEqual(BlackLedgerSites.Keys.OrderBy(x=>x)))throw new InvalidDataException("Exact four Black Ledger exterior roles required");
  var rows=new List<object>();
  foreach(var a in aliases){
   if(!refs.TryGetValue(a.ForcedReference.FormKey,out var old)||old is not IPlacedObjectGetter obj||obj.EditorID!="TLM_REF_BL_"+a.Name||(obj.MajorRecordFlagsRaw&0xC00)!=0xC00)throw new InvalidDataException("Original Black Ledger control mismatch");
   var at=BlackLedgerSites[a.Name!];var placed=obj.Duplicate(mod.GetNextFormKey());placed.EditorID="TLM_WS_ST_BL_"+a.Name;placed.Position=new P3Float(at.X,at.Y,at.Z);placed.Rotation=new P3Float(0,0,0);placed.MajorRecordFlagsRaw|=0xC00;world.TopCell!.Persistent.Add(placed);a.ForcedReference.SetTo(placed.FormKey);
   rows.Add(new{alias=a.Name,source=old.FormKey.ToString(),reference=placed.FormKey.ToString(),x=at.X,y=at.Y,z=at.Z});
  }
  var vmad=clone.VirtualMachineAdapter??throw new InvalidDataException("Entry adapter VMAD missing");
  void Remap(ScriptObjectProperty p){if(p.Object.FormKey==original.FormKey)p.Object.SetTo(clone.FormKey);}
  foreach(var script in vmad.Scripts.Concat(vmad.Aliases.SelectMany(a=>a.Scripts)))foreach(var p in script.Properties.OfType<ScriptObjectProperty>())Remap(p);foreach(var a in vmad.Aliases)Remap(a.Property);
  mod.Quests.Add(clone);door.Object.SetTo(clone.FormKey);
  ValidateBlackLedger(mod,section);
  return new{policy="Only new entry adapter/four controls appended; original cast/main MQ04/counting room/book never cloned; no navmesh/native proof",quest=clone.EditorID,main=main.FormKey.ToString(),references=rows};
 }
 static void ValidateBlackLedger(IFallout4ModGetter addon,IQuestGetter section){
  var walk=section.VirtualMachineAdapter!.Scripts.Single(s=>s.Name=="TLM:Act1Walk");var entry=walk.Properties.OfType<IScriptObjectPropertyGetter>().Where(p=>p.Name=="TLM_BlackLedgerEntry").ToArray();var main=walk.Properties.OfType<IScriptObjectPropertyGetter>().Where(p=>p.Name=="TLM_BlackLedger").ToArray();var clone=addon.Quests.SingleOrDefault(q=>q.EditorID=="TLM_WS_BL_Entry");
  if(clone==null){if(entry.Length!=0||main.Length!=0)throw new InvalidDataException("Black Ledger binding without entry");return;}
  if(entry.Length!=1||main.Length!=1||entry[0].Object.FormKey!=clone.FormKey||main[0].Object.FormKey.ModKey!=StoryMaster)throw new InvalidDataException("Black Ledger must retain original authoritative master");
  foreach(var role in new[]{("BlackLedgerOriginalSheriff","Pritchard"),("BlackLedgerOriginalVane","Vane"),("BlackLedgerOriginalHaskell","Haskell")}){
   var expected=section.Aliases!.OfType<IQuestReferenceAliasGetter>().Single(a=>a.Name==role.Item2).ForcedReference.FormKey;var actual=walk.Properties.OfType<IScriptObjectPropertyGetter>().Single(p=>p.Name==role.Item1).Object.FormKey;if(actual!=expected)throw new InvalidDataException("Black Ledger original actor ref mismatch "+role.Item2);
  }
  var own=addon.Worldspaces.Single().TopCell!.Persistent.ToDictionary(r=>r.FormKey);
  foreach(var a in clone.Aliases!.OfType<IQuestReferenceAliasGetter>()){
   if(!BlackLedgerSites.TryGetValue(a.Name!,out var at)||!own.TryGetValue(a.ForcedReference.FormKey,out var r)||r is not IPlacedObjectGetter placed||placed.EditorID!="TLM_WS_ST_BL_"+a.Name||placed.Position!=new P3Float(at.X,at.Y,at.Z))throw new InvalidDataException("Black Ledger cloned control position/identity mismatch");
  }
 }
}
