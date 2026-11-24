using Mutagen.Bethesda;
using Mutagen.Bethesda.Fallout4;
using Mutagen.Bethesda.Plugins;

namespace Tlm.PluginBuilder;

public sealed partial class Builder
{
    // Append after all accepted master forms; preserve the original actor and pockets.
    void BuildDunmoreWardrobe()
    {
        if (_vanilla == null) return;
        var npc = _mod.Npcs.Single(n => n.EditorID == "TLM_NPC_CUTTER_LEAD");
        if (npc.FormKey.ID != 0x843 || !npc.UseTemplateActors.HasFlag(Npc.TemplateActorType.Inventory)
            || npc.TemplateActors?.InventoryTemplate.FormKey != new FormKey(Fallout4Esm, 0x1C2691)
            || npc.DefaultOutfit.FormKey != new FormKey(Fallout4Esm, 0x1C269A))
            throw new InvalidDataException("Original Dunmore inventory authority changed");

        var clothing = new FormKey(Fallout4Esm, 0xA36BE);
        var addonKey = new FormKey(Fallout4Esm, 0xA36BD);
        if (!_vanilla.TryResolve<IArmorGetter>(clothing, out var armor)
            || armor.EditorID != "ClothesResident4" || armor.VirtualMachineAdapter != null
            || armor.Armatures.Count != 1 || armor.Armatures[0].ArmorAddon.FormKey != addonKey
            || !_vanilla.TryResolve<IArmorAddonGetter>(addonKey, out var addon)
            || addon.Race.FormKey != new FormKey(Fallout4Esm, 0x13746)
            || addon.WorldModel?.Male?.File?.ToString() != @"Clothes\Residents\4SuitM.nif")
            throw new InvalidDataException("Verified native patched suit donor changed");

        var outfit = _mod.Outfits.AddNew("TLM_OUTFIT_DunmorePatchedSuit");
        outfit.Items ??= new();
        outfit.Items.Add(new FormLink<IOutfitTargetGetter>(clothing));
        Track(outfit);
        npc.DefaultOutfit.SetTo(outfit.FormKey);
        npc.UseTemplateActors &= ~Npc.TemplateActorType.Inventory;
        npc.TemplateActors!.InventoryTemplate.Clear();
        VanillaNotes.Add("Dunmore: fixed native Patched Three-Piece Suit, bare head; only Inventory inheritance/link and default outfit replaced; original pockets/Traits/voice/AI/factions retained");
    }
}
