using Mutagen.Bethesda;
using Mutagen.Bethesda.Fallout4;
using Mutagen.Bethesda.Plugins;
using Noggog;

public static partial class WorldStory
{
    // Called only AFTER every accepted story/scenery allocation. The ledger
    // remains in the source master; only these two controls are added here.
    public static object? CompleteReliefControls(Fallout4Mod mod,Worldspace world,IFallout4ModGetter source)
    {
        var controller=mod.Quests.SingleOrDefault(q=>q.EditorID==GreenwaterClone);
        if(controller==null)return null;
        var names=new[]{"ReliefStores","ReliefSupply"};
        var aliases=controller.Aliases!.OfType<QuestReferenceAlias>().Where(a=>names.Contains(a.Name)).ToArray();
        if(aliases.Length==0)return null; // actual older source remains supported
        if(aliases.Length!=2||!source.Quests.Any(q=>q.EditorID=="TLM_GW_Relief"))throw new InvalidDataException("Incomplete relief controller/ledger contract");
        var references=source.Cells.Records.SelectMany(b=>b.SubBlocks).SelectMany(b=>b.Cells).SelectMany(c=>c.Persistent.Concat(c.Temporary)).ToDictionary(r=>r.FormKey);
        var rows=new List<object>();
        foreach(var alias in aliases){
            if(alias.ForcedReference.IsNull||!references.TryGetValue(alias.ForcedReference.FormKey,out var original)||original is not IPlacedObjectGetter obj||obj.EditorID!="TLM_REF_GW_"+alias.Name)
                throw new InvalidDataException("Relief source control identity mismatch: "+alias.Name);
            var control=source.Activators.SingleOrDefault(a=>a.FormKey==obj.Base.FormKey)
                ??throw new InvalidDataException("Relief control must be its own source activator");
            var lo=control.ObjectBounds.First;var hi=control.ObjectBounds.Second;
            var model=control.Model?.File?.ToString();
            if(string.IsNullOrWhiteSpace(model)||lo.X < -64||hi.X>64||lo.Y < -64||hi.Y>64||lo.Z < -4||hi.Z>24)
                throw new InvalidDataException("Relief paper-control model/bounds require a new audited placement: "+alias.Name);
            var at=GreenwaterSites[alias.Name!];var placed=obj.Duplicate(mod.GetNextFormKey());
            placed.EditorID="TLM_WS_ST_GW_"+alias.Name;placed.Position=new P3Float(at.X,at.Y,at.Z);placed.Rotation=new P3Float(0,0,0);placed.MajorRecordFlagsRaw|=0xC00;
            world.TopCell!.Persistent.Add(placed);alias.ForcedReference.SetTo(placed.FormKey);
            rows.Add(new{alias=alias.Name,source=original.FormKey.ToString(),reference=placed.FormKey.ToString(),x=at.X,y=at.Y,z=at.Z,
                model,min=new[]{(int)lo.X,lo.Y,lo.Z},max=new[]{(int)hi.X,hi.Y,hi.Z}});
        }
        return new{policy="Appended after every accepted scenery ID; one master ledger, zero copied ledgers",references=rows};
    }
}
