namespace Tlm.PluginBuilder;

// DEMO-GUIDE-003: help objects, never evidence. Existing records/aliases stay
// in their previous order; these three append after the 33-place A1 prefix.
// Borrowed clipboard/folder models are not signs with rendered lettering.
public static class Guide
{
    public sealed record Point(string Alias, string Name, int Place, float Ahead, float Right);
    public static readonly Point[] Points =
    {
        new("GuideWreck", "Demo guide - Wreck directions", 1, 100, -320),
        new("GuideRoad", "Demo guide - Caravan road directions", 2, 220, -310),
        new("GuideMercy", "Demo guide - Mercy Crossing directions", 3, 380, 420),
    };
    public static readonly ActivatorSpec[] Activators = Points.Select(p =>
        new ActivatorSpec("TLM_ACTI_" + p.Alias, p.Name, new[] { "Clipboard", "Folder" }, "Directions")).ToArray();
    public static readonly PlacedSpec[] Placed = Points.Select(p =>
        new PlacedSpec("TLM_REF_A1_" + p.Alias, Spec.TrialCell, "TLM_ACTI_" + p.Alias, null,
            p.Ahead, p.Right, 12, InitiallyDisabled: true)).ToArray();
    public static readonly AliasSpec[] Aliases = Points.Select(p =>
        new AliasSpec(p.Alias, Fill.Placed, AllowDisabled: true, Placed: "TLM_REF_A1_" + p.Alias,
            Scripts: new[] { new ScriptBind("TLM:Act1Guide", new FormProp("TLM_MQ01", "TLM_MQ01"), new IntProp("Place", p.Place)) })).ToArray();
}
