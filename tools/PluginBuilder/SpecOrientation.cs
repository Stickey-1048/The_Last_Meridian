namespace Tlm.PluginBuilder;

// DEMO-ORIENT-002: sparse, development-only silhouettes. Exact Static IDs were
// read from the owner's Fallout4.esm; these are references, never bundled meshes.
// No existing actor, pickup, marker or trigger moves. Names here describe the
// build report, not lettering rendered onto the models. Visual acceptance is pending.
public static class Orientation
{
    public sealed record Decor(string Alias, string Name, string Base, float Ahead, float Right, float Up = 0);
    public static readonly Decor[] Pieces =
    {
        // Ragged low boundary outside the evidence. The first schematic sites
        // overlapped the ledger's vicinity, so only NEW debris was moved outward.
        // Earlier schematic sites also overlapped the room's cooking spit.
        // These two sites passed a transformed vanilla-object bounds survey.
        new("DecorWreckOuter", "wreck outer rubble", "StoneWallOldRubble", 500, -750),
        new("DecorWreckRear", "wreck rear debris", "ExtRubble_BricksLrg_Clump01", 575, -625),
        // Model bottom -56: raise it to the floor. Narrow 104-unit road markers.
        new("DecorRoadLeft", "road left marker", "FenceWIBollardPost01", 410, -390, 56),
        new("DecorRoadRight", "road right marker", "FenceWIBollardPost01", 410, -30, 56),
        // Model bottom -64: full 240-unit timber posts, no overhead beam.
        new("DecorMercyLeft", "Mercy left gatepost", "FenceWoodPost01", 300, 20, 64),
        new("DecorMercyRight", "Mercy right gatepost", "FenceWoodPost01", 300, 280, 64),
        new("DecorMercyCounter", "Mercy rear table", "ModernDomesticTableLrg01", 828, 210),
    };
    public static readonly PlacedSpec[] Placed = Pieces.Select(p =>
        new PlacedSpec("TLM_REF_A1_" + p.Alias, Spec.TrialCell, p.Base, "Static",
            p.Ahead, p.Right, p.Up, InitiallyDisabled: true)).ToArray();
    public static readonly AliasSpec[] Aliases = Pieces.Select(p =>
        new AliasSpec(p.Alias, Fill.Placed, AllowDisabled: true, Placed: "TLM_REF_A1_" + p.Alias)).ToArray();
}
