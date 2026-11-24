using Mutagen.Bethesda.Fallout4;
using Mutagen.Bethesda.Plugins;
using Noggog;
using System.Text.Json;

public static class OpeningWorkingYard
{
    public static object Apply(IFallout4ModGetter native, Fallout4Mod mod, Worldspace world)
    {
        var folder = new DirectoryInfo(AppContext.BaseDirectory);
        while (folder != null && !File.Exists(Path.Combine(folder.FullName,"tools/OpeningWorkingYard/fences.json"))) folder=folder.Parent;
        if (folder == null) throw new InvalidDataException("Working-yard placement contract absent");
        var root=Path.Combine(folder.FullName,"tools/OpeningWorkingYard");
        using var fences=JsonDocument.Parse(File.ReadAllText(Path.Combine(root,"fences.json")));
        using var papers=JsonDocument.Parse(File.ReadAllText(Path.Combine(root,"papers.json")));
        using var stations=JsonDocument.Parse(File.ReadAllText(Path.Combine(root,"stations.json")));
        var refs=world.SubCells.SelectMany(b=>b.Items).SelectMany(b=>b.Items)
            .SelectMany(c=>c.Temporary.Concat(c.Persistent)).Concat(world.TopCell!.Persistent)
            .OfType<PlacedObject>().ToDictionary(r=>r.FormKey.ID);
        var timber=native.Statics.Single(r=>r.FormKey.ID==0x118F79 && r.EditorID=="FenceWoodStr03");
        if(timber.Model?.File?.ToString()!=@"SetDressing\FencesGrates\Wood\FenceWoodStr03.nif")
            throw new InvalidDataException("Measured rough timber donor differs");
        var selected=fences.RootElement.GetProperty("selected");
        var disabled=fences.RootElement.GetProperty("disableOtherwise");
        if(selected.GetArrayLength()!=7 || disabled.GetArrayLength()!=27 || papers.RootElement.GetArrayLength()!=3)
            throw new InvalidDataException("Unexpected finite yard or clue membership");
        foreach(var p in selected.EnumerateArray())
        {
            uint id=Convert.ToUInt32(p.GetProperty("originalId").GetString(),16)&0xFFFFFF;
            var r=refs[id];var old=p.GetProperty("oldPose");var next=p.GetProperty("proposedPose");
            if(r.EditorID!=p.GetProperty("name").GetString() || r.Base.FormKey!=new FormKey(native.ModKey,0x125C67)
                || (r.MajorRecordFlagsRaw&0x800)!=0 || r.Position!=new P3Float(old[0].GetSingle(),old[1].GetSingle(),old[2].GetSingle())
                || r.Rotation!=new P3Float(old[3].GetSingle(),old[4].GetSingle(),old[5].GetSingle()) || (r.Scale??1f)!=1f)
                throw new InvalidDataException("Original selected yard segment differs");
            r.Base.SetTo(timber.FormKey);
            r.Position=new P3Float(next[0].GetSingle(),next[1].GetSingle(),next[2].GetSingle());
        }
        foreach(var p in disabled.EnumerateArray())
        {
            var r=refs[Convert.ToUInt32(p.GetProperty("originalId").GetString(),16)&0xFFFFFF];
            if(r.EditorID!=p.GetProperty("name").GetString() || r.Base.FormKey!=new FormKey(native.ModKey,0x125C67) || (r.MajorRecordFlagsRaw&0x800)!=0)
                throw new InvalidDataException("Original retired white-yard segment differs");
            r.MajorRecordFlagsRaw|=0x800;
        }
        foreach(var p in papers.RootElement.EnumerateArray())
        {
            var r=refs[p.GetProperty("localId").GetUInt32()];var old=p.GetProperty("oldXYZ");
            if(r.EditorID!=p.GetProperty("name").GetString() || r.Base.FormKey!=new FormKey(ModKey.FromNameAndExtension("TheLastMeridian.esp"),p.GetProperty("baseId").GetUInt32())
                || r.Position!=new P3Float(old[0].GetSingle(),old[1].GetSingle(),old[2].GetSingle()))
                throw new InvalidDataException("Original clue reference or pose differs");
            r.Position=new P3Float(r.Position.X,r.Position.Y,p.GetProperty("newZ").GetSingle());
        }
        var cells=world.SubCells.SelectMany(b=>b.Items).SelectMany(b=>b.Items);
        var cell=cells.Single(c=>c.Grid?.Point==new P2Int(0,0));
        var additions=stations.RootElement.GetProperty("props");
        if(additions.GetArrayLength()!=11)throw new InvalidDataException("Unexpected finite working-area membership");
        var names=new HashSet<string>(StringComparer.Ordinal);
        foreach(var p in additions.EnumerateArray())
        {
            string id=p.GetProperty("id").GetString()!;
            if(!id.StartsWith("TLM_YARD_",StringComparison.Ordinal) || !names.Add(id) || refs.Values.Any(r=>r.EditorID==id))
                throw new InvalidDataException("Duplicate or foreign working-area reference");
            var key=new FormKey(native.ModKey,Convert.ToUInt32(p.GetProperty("donorId").GetString(),16));
            string? editor;string? model;
            switch(p.GetProperty("kind").GetString())
            {
                case "STAT":var s=native.Statics.Single(r=>r.FormKey==key);editor=s.EditorID;model=s.Model?.File?.ToString();break;
                case "FURN":var f=native.Furniture.Single(r=>r.FormKey==key);editor=f.EditorID;model=f.Model?.File?.ToString();break;
                default:throw new InvalidDataException("Only measured static or native furniture donors allowed");
            }
            if(editor!=p.GetProperty("donor").GetString() || model!=p.GetProperty("model").GetString() || p.GetProperty("scale").GetSingle()!=1)
                throw new InvalidDataException("Measured working-area donor differs");
            var xyz=p.GetProperty("position");var rotation=p.GetProperty("rotation");
            var placed=new PlacedObject(mod.GetNextFormKey(),Fallout4Release.Fallout4){EditorID=id,
                Position=new P3Float(xyz[0].GetSingle(),xyz[1].GetSingle(),xyz[2].GetSingle()),
                Rotation=new P3Float(rotation[0].GetSingle(),rotation[1].GetSingle(),rotation[2].GetSingle()),Scale=1};
            placed.Base.SetTo(key);cell.Temporary.Add(placed);
        }
        return new { scope="Rough timber fragments,grounded paper clues and three existing-character working areas", newReferences=names.Count, native="OPEN: native fit, materials, clue visibility, furniture use and access", existingStoryBindingsChanged=false };
    }
}
