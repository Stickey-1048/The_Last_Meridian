using Mutagen.Bethesda;
using Mutagen.Bethesda.Fallout4;
using Mutagen.Bethesda.Plugins;
using Noggog;
public static partial class WorldStory
{
 public static readonly Dictionary<string,(float X,float Y)> SheriffHelpSites=new(){
  ["HelpApproach"]=(1900,1664),["HelpWithdrawA"]=(1728,1152),["HelpWithdrawB"]=(1920,1152),
  ["HelpWithdrawC"]=(2112,1152),["HelpWithdrawD"]=(1856,1408),["HelpHome"]=(3260,2530)};
 // Run AFTER the last scenery/terrain allocation: original exterior IDs stay fixed.
 public static void CompleteSheriffHelp(Fallout4Mod mod,Worldspace world,Cell cell,IFallout4ModGetter source)
 {
  var section=mod.Quests.Single(q=>q.EditorID=="TLM_WS_A1");
  if(!section.VirtualMachineAdapter!.Scripts.Single(s=>s.Name=="TLM:Act1Walk").Properties.Any(p=>p.Name=="HelpAnchors"))return;
  var originals=source.Cells.Records.SelectMany(b=>b.SubBlocks).SelectMany(b=>b.Cells).SelectMany(c=>c.Persistent.Concat(c.Temporary)).OfType<IPlacedObjectGetter>().ToDictionary(p=>p.FormKey);
  var map=cell.Landscape?.VertexHeightMap??throw new InvalidDataException("Help anchors need actual opening LAND");
  if(map.HeightMap.Width!=33||map.HeightMap.Height!=33)throw new InvalidDataException("Help LAND grid differs");
  var h=new float[33,33];
  for(int y=0;y<33;y++)for(int x=0;x<33;x++)h[x,y]=(x>0?h[x-1,y]:y>0?h[0,y-1]:map.Offset*8)+unchecked((sbyte)map.HeightMap[x,y])*8;
  float Height(float x,float y){int ix=Math.Clamp((int)(x/128),0,31),iy=Math.Clamp((int)(y/128),0,31);float u=(x-ix*128)/128,v=(y-iy*128)/128,a=h[ix,iy],b=h[ix+1,iy],c=h[ix,iy+1],d=h[ix+1,iy+1];return MathF.Max(v<=u?a+(b-a)*u+(d-b)*v:a+(d-c)*u+(c-a)*v,u+v<=1?a+(b-a)*u+(c-a)*v:d+(c-d)*(1-u)+(b-d)*(1-v));}
  foreach(var item in SheriffHelpSites){
   var alias=section.Aliases!.OfType<QuestReferenceAlias>().Single(a=>a.Name==item.Key);
   if(!originals.TryGetValue(alias.ForcedReference.FormKey,out var old)||old.EditorID!="TLM_REF_A1_"+item.Key)throw new InvalidDataException("Original help marker mismatch");
   var fresh=old.Duplicate(mod.GetNextFormKey());fresh.EditorID="TLM_WS_ST_"+item.Key;fresh.Position=new P3Float(item.Value.X,item.Value.Y,Height(item.Value.X,item.Value.Y)+16);fresh.MajorRecordFlagsRaw|=0xC00;
   world.TopCell!.Persistent.Add(fresh);alias.ForcedReference.SetTo(fresh.FormKey);
  }
 }
}
