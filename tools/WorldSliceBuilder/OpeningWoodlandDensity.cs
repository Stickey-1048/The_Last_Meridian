using Mutagen.Bethesda.Fallout4;
using Mutagen.Bethesda.Plugins;
using Noggog;
using System.Text.Json;

// A final passive art pass. Existing terrain and story references remain owned
// by the earlier passes; only the explicitly measured obstacle moves are allowed.
public static class OpeningWoodlandDensity
{
    public static object Apply(IFallout4ModGetter native, Fallout4Mod mod, Worldspace world)
    {
        var dir = new DirectoryInfo(AppContext.BaseDirectory);
        while (dir != null && !File.Exists(Path.Combine(dir.FullName, "tools/OpeningWoodlandDensity/placements.json"))) dir = dir.Parent;
        if (dir == null) throw new InvalidDataException("Woodland density plan absent");
        using var doc = JsonDocument.Parse(File.ReadAllText(Path.Combine(dir.FullName, "tools/OpeningWoodlandDensity/placements.json")));
        var plan = doc.RootElement;
        // This is our own local grass clone, not a vanilla or global override.
        // Its dense bright lawn tufts were conspicuous in the actual yard view.
        var grass = mod.Grasses.Single(g => g.EditorID == "TLM_GRAS_OpeningLowTufts");
        if (grass.Density != 12) throw new InvalidDataException("Local grass source differs");
        grass.Density = 4;
        var cells = world.SubCells.SelectMany(b => b.Items).SelectMany(b => b.Items)
            .Where(c => c.Grid != null).ToDictionary(c => (c.Grid!.Point.X, c.Grid.Point.Y));
        var refs = cells.Values.SelectMany(c => c.Temporary.Concat(c.Persistent)).OfType<PlacedObject>()
            .Concat(world.TopCell!.Persistent.OfType<PlacedObject>()).ToDictionary(r => r.EditorID!);
        P3Float Triple(JsonElement e, int start = 0) => new(e[start].GetSingle(), e[start + 1].GetSingle(), e[start + 2].GetSingle());
        foreach (var p in plan.GetProperty("moves").EnumerateArray())
        {
            var r = refs[p.GetProperty("id").GetString()!];
            if (r.FormKey.ID != p.GetProperty("localId").GetUInt32()
                || r.Base.FormKey != new FormKey(native.ModKey, p.GetProperty("baseId").GetUInt32())
                || r.Position != Triple(p.GetProperty("oldPose")) || r.Rotation != Triple(p.GetProperty("oldPose"), 3))
                throw new InvalidDataException("Measured old obstacle differs");
            var pose = p.GetProperty("pose");
            r.Position = Triple(pose); r.Rotation = Triple(pose, 3);
            var target = cells[((int)MathF.Floor(r.Position.X / 4096), (int)MathF.Floor(r.Position.Y / 4096))];
            var owner = cells.Values.Single(c => c.Temporary.Contains(r));
            if (owner != target) { owner.Temporary.Remove(r); target.Temporary.Add(r); }
        }
        var added = new HashSet<string>(StringComparer.Ordinal);
        foreach (var p in plan.GetProperty("additions").EnumerateArray())
        {
            var id = p.GetProperty("id").GetString()!;
            if (!id.StartsWith("TLM_DENSITY_", StringComparison.Ordinal) || refs.ContainsKey(id) || !added.Add(id))
                throw new InvalidDataException("Duplicate or foreign woodland reference");
            uint baseId = Convert.ToUInt32(p.GetProperty("donorId").GetString(), 16);
            var donor = native.Statics.Single(s => s.FormKey.ID == baseId && s.EditorID == p.GetProperty("asset").GetString());
            if (donor.VirtualMachineAdapter != null || donor.Model?.File?.ToString() != p.GetProperty("model").GetString())
                throw new InvalidDataException("Passive woodland donor differs");
            var at = Triple(p.GetProperty("xyz"));
            var scale = p.GetProperty("scale").GetSingle();
            if (scale < .5f || scale > 1.5f || !float.IsFinite(at.Z)) throw new InvalidDataException("Unbounded woodland pose");
            var xy = ((int)MathF.Floor(at.X / 4096), (int)MathF.Floor(at.Y / 4096));
            if (!cells.TryGetValue(xy, out var cell)) throw new InvalidDataException("Woodland outside emitted terrain");
            var r = new PlacedObject(mod.GetNextFormKey(), Fallout4Release.Fallout4)
            {
                EditorID = id, Position = at, Rotation = new P3Float(0, 0, p.GetProperty("yaw").GetSingle()), Scale = scale
            };
            r.Base.SetTo(donor.FormKey); cell.Temporary.Add(r);
        }
        if (added.Count == 0) throw new InvalidDataException("Empty woodland pass");
        return new { scope = "Measured passive woodland clusters and repair-frontage clearance", additions = added.Count,
            moves = plan.GetProperty("moves").GetArrayLength(), localGrassDensity = 4,
            native = "Pending actual visual and walking inspection; no navmesh or service changes" };
    }
}
