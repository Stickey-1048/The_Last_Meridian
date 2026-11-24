using Mutagen.Bethesda;
using Mutagen.Bethesda.Fallout4;
using Mutagen.Bethesda.Plugins;
namespace Tlm.PluginBuilder;
public sealed partial class Builder
{
    void ApplyOpeningPresentation(Npc npc, NpcSpec spec)
    {
        if (spec.EditorId == "TLM_NPC_MARSHAL_DEAD")
        {
            // Native Kill(None) cannot kill a Protected settler. Only this
            // original corpse base must permit its uncredited loaded death.
            npc.Flags &= ~(Npc.Flag.Protected | Npc.Flag.Essential);
            // Workshop inventory inheritance can replace our outfit with a
            // leveled settler wardrobe. This corpse gets one known full outfit.
            var clothingKey = new FormKey(Fallout4Esm, 0x0B2D8D);
            if (!_vanilla!.TryResolve<IArmorGetter>(clothingKey, out var clothing)
                || clothing.EditorID != "Armor_Wastelander_Light"
                || clothing.VirtualMachineAdapter != null || clothing.Armatures.Count != 1)
                throw new InvalidDataException("Reviewed marshal clothing donor changed");
            var addon = clothing.Armatures[0].ArmorAddon.FormKey;
            if (!_vanilla.TryResolve<IArmorAddonGetter>(addon, out var model)
                || model.FormKey.ID != 0x0B2D89 || model.Race.FormKey.ID != 0x13746
                || model.WorldModel?.Male?.File?.ToString() != @"Armor\RaiderHeavy\MUnderArmor.nif")
                throw new InvalidDataException("Marshal clothing has no verified male human body model");
            var outfit = _mod.Outfits.AddNew("TLM_OUTFIT_OpeningMarshal");
            outfit.Items ??= new();
            outfit.Items.Add(new FormLink<IOutfitTargetGetter>(clothingKey));
            Track(outfit);
            npc.DefaultOutfit.SetTo(outfit.FormKey);
            npc.UseTemplateActors &= ~Npc.TemplateActorType.Inventory;
            npc.TemplateActors?.InventoryTemplate.Clear();
            return;
        }
        if (spec.EditorId != "TLM_NPC_SHERIFF_MERCY") return;
        var original = npc.TemplateActors!.TraitTemplate.FormKey;
        var seen = new HashSet<FormKey>();
        INpcGetter actor;
        while (true)
        {
            if (!seen.Add(original) || !_vanilla!.TryResolve<INpcGetter>(original, out actor!))
                throw new InvalidDataException("Pritchard original voice donor cannot be resolved");
            if (!actor.UseTemplateActors.HasFlag(Npc.TemplateActorType.Traits)) break;
            original = actor.TemplateActors != null && !actor.TemplateActors.TraitTemplate.IsNull
                ? actor.TemplateActors.TraitTemplate.FormKey : actor.DefaultTemplate.FormKey;
        }
        if (!_vanilla!.TryResolve<IVoiceTypeGetter>(actor.Voice.FormKey, out var voice))
            throw new InvalidDataException("Pritchard original effective voice is missing");
        if (voice.FormKey.ID != 0x23323 || voice.EditorID != "MaleBoston")
            throw new InvalidDataException("Pritchard original voice no longer matches the exact setup binding");
        var donorKey = new FormKey(Fallout4Esm, 0x3F23D);
        if (!_vanilla.TryResolve<INpcGetter>(donorKey, out var donor)
            || donor.EditorID != "AbrahamFinch" || donor.UseTemplateActors.HasFlag(Npc.TemplateActorType.Traits)
            || donor.Flags.HasFlag(Npc.Flag.Female) || donor.Race.FormKey.ID != 0x13746)
            throw new InvalidDataException("Reviewed intact older male face donor changed");
        npc.TemplateActors.TraitTemplate.SetTo(donorKey);
        LooksFrom[spec.EditorId] = donorKey.ToString();
        VanillaNotes.Add($"Opening Pritchard: intact Abraham Finch Traits {donorKey}; original effective voice {voice.FormKey} bound to original actor setup; AI/factions/inventory unchanged");
    }
    // Tail allocation: keep every existing form key and every other NPC literal.
    void BuildPritchardWardrobe()
    {
        if (_vanilla == null) return;
        var npc = _mod.Npcs.Single(n => n.EditorID == "TLM_NPC_SHERIFF_MERCY");
        if (npc.FormKey.ID != 0x83A || !npc.UseTemplateActors.HasFlag(Npc.TemplateActorType.Inventory)
            || npc.TemplateActors?.InventoryTemplate.FormKey != new FormKey(Fallout4Esm, 0x113340)
            || npc.DefaultOutfit.FormKey != new FormKey(Fallout4Esm, 0x1C269A))
            throw new InvalidDataException("Original Pritchard inventory baseline changed");
        var pieces = new[] {
            (Id: 0x0B3F4Cu, Name: "ClothesResident5", Addon: 0x0B3F49u, Model: @"Clothes\Residents\5SuitM.nif"),
            (Id: 0x0B3F4Du, Name: "ClothesResident5Hat", Addon: 0x0B3F4Au, Model: @"Clothes\Residents\5HatM.nif")
        };
        foreach (var piece in pieces)
        {
            var key = new FormKey(Fallout4Esm, piece.Id);
            if (!_vanilla.TryResolve<IArmorGetter>(key, out var armor) || armor.EditorID != piece.Name
                || armor.VirtualMachineAdapter != null || armor.Armatures.Count != 1
                || armor.Armatures[0].ArmorAddon.FormKey != new FormKey(Fallout4Esm, piece.Addon)
                || !_vanilla.TryResolve<IArmorAddonGetter>(armor.Armatures[0].ArmorAddon.FormKey, out var addon)
                || addon.Race.FormKey.ID != 0x13746 || addon.WorldModel?.Male?.File?.ToString() != piece.Model)
                throw new InvalidDataException("Verified sheriff wardrobe donor changed: " + piece.Name);
        }
        var outfit = _mod.Outfits.AddNew("TLM_OUTFIT_PritchardDeterministic");
        outfit.Items ??= new();
        foreach (var piece in pieces) outfit.Items.Add(new FormLink<IOutfitTargetGetter>(new FormKey(Fallout4Esm, piece.Id)));
        Track(outfit);
        npc.DefaultOutfit.SetTo(outfit.FormKey);
        npc.UseTemplateActors &= ~Npc.TemplateActorType.Inventory;
        npc.TemplateActors!.InventoryTemplate.Clear();
        VanillaNotes.Add("Opening Pritchard: fixed native ClothesResident5 + ClothesResident5Hat; only inherited Inventory/link and default outfit replaced; own pockets/weapon entries, Traits/voice/AI/factions/stats unchanged");
    }

}
