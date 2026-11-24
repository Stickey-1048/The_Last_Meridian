using Mutagen.Bethesda;
using Mutagen.Bethesda.Fallout4;
using Mutagen.Bethesda.Plugins;

namespace Tlm.PluginBuilder;

public sealed partial class Builder
{
    // Tail allocation keeps all current quest, sound and original actor IDs stable.
    void BuildAdaWorkwear()
    {
        if (_vanilla == null) return;
        var npc = _mod.Npcs.Single(n => n.EditorID == "TLM_NPC_GUNSMITH_MERCY");
        if (npc.FormKey.ID != 0x83B || !npc.UseTemplateActors.HasFlag(Npc.TemplateActorType.Inventory)
            || npc.TemplateActors?.InventoryTemplate.FormKey != new FormKey(Fallout4Esm, 0x113346)
            || npc.DefaultOutfit.FormKey != new FormKey(Fallout4Esm, 0x1C269A))
            throw new InvalidDataException("Original Ada inventory baseline changed");

        var clothing = new FormKey(Fallout4Esm, 0x1C26B9);
        var addonKey = new FormKey(Fallout4Esm, 0x5E76B);
        if (!_vanilla.TryResolve<IArmorGetter>(clothing, out var armor)
            || armor.EditorID != "ClothesGenericJumpsuit" || armor.VirtualMachineAdapter != null
            || armor.Armatures.Count != 1 || armor.Armatures[0].ArmorAddon.FormKey != addonKey
            || !_vanilla.TryResolve<IArmorAddonGetter>(addonKey, out var addon)
            || addon.Race.FormKey != new FormKey(Fallout4Esm, 0x13746)
            || addon.WorldModel?.Female?.File?.ToString() != @"Clothes\RedRocketJumpsuit\RedRocketJumpsuitF.nif")
            throw new InvalidDataException("Verified native mechanic clothing donor changed");

        var outfit = _mod.Outfits.AddNew("TLM_OUTFIT_AdaMechanic");
        if (outfit.FormKey.ID != 0xF88) throw new InvalidDataException("Ada outfit must append after existing F87");
        outfit.Items ??= new();
        outfit.Items.Add(new FormLink<IOutfitTargetGetter>(clothing));
        Track(outfit);
        npc.DefaultOutfit.SetTo(outfit.FormKey);
        npc.UseTemplateActors &= ~Npc.TemplateActorType.Inventory;
        npc.TemplateActors!.InventoryTemplate.Clear();
        VanillaNotes.Add("Ada Pike: fixed native ClothesGenericJumpsuit workwear; original inventory entries and Traits retained");
    }
}
