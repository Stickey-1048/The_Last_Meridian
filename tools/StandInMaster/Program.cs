// Builds a tiny stand-in "Fallout4.esm" holding only the vanilla records the
// plugin builder looks up. For testing the lookup code path; it is not game data.
//
//   StandInMaster <output path> [variant]
//
// Variants:
//   default          The player reference is spelled "PlayerREF". On the real
//                    master a lookup for "PlayerRef" failed until the lookup
//                    stopped depending on letter case; this keeps that covered.
//                    Also holds an actor "WorkshopNPC" and a static "XMarker",
//                    the two forms the self-test makes its stand-ins from, so
//                    a plugin built against this file has them wired as the
//                    one built on the game PC does. And a test room "QASmoke"
//                    with an arrival marker, a few collision layers, an empty
//                    trigger base and some box triggers in other rooms: what
//                    the builder needs to place references in a cell of the
//                    game. And what the first section's rough cut looks
//                    up: a list of settlers for a copy to take its looks
//                    from (three men, three women, one of no one sex; some
//                    plain, some who take their own looks from elsewhere),
//                    things with the names a player sees (two of them share
//                    a name, one has no model, one is missing altogether), a
//                    revolver and what it fires, a crate, a few notes, and
//                    the thing on the player's arm.
//                    All of it is invented here; none of it is the
//                    game's data, and the numbers are not the game's numbers.
//   localized        As default, but the master keeps its text apart, in strings
//                    files beside it, as the game's own master does. The test
//                    room's name then has to be read from those files.
//                    (run_checks.sh also builds against this master with the
//                    strings files taken away.)
//   plain-triggers   As default, but the master's own box triggers do not carry
//                    their reach a second time (as the reference's bound).
//                    The builder does as most of them do, so it must then
//                    write none either. Its settler is plainer too: it names
//                    no default package list and takes nothing from a
//                    template, so the builder's copies have none to keep.
//   bare-room        The test room exists, but with no arrival marker; and the
//                    master has no collision layers, no empty trigger base and
//                    no triggers of its own. The builder must still place what
//                    it can, from the origin, and say what it could not do.
//   unnamed-player   The player reference has no EditorID at all and sits at
//                    the conventional id 0x14. Exercises the builder's fallback.
//   wrong-player     Record 0x14 places some other actor. The builder must
//                    refuse to use it.
//   quest-evidence   No player reference record at all (what the library saw on
//                    the real master), but a dozen quests force 0x14 into an
//                    alias named "Player". The builder should accept 0x14.
//   weak-evidence    The same with only two such quests. The builder must refuse.
using Mutagen.Bethesda;
using Mutagen.Bethesda.Fallout4;
using Mutagen.Bethesda.Plugins;
using Noggog;

var path = args[0];
var variant = args.Length > 1 ? args[1] : "default";
var mod = new Fallout4Mod(ModKey.FromNameAndExtension("Fallout4.esm"), Fallout4Release.Fallout4);
FormKey Key(uint id) => new(mod.ModKey, id);

var room = variant is "default" or "localized" or "plain-triggers" or "bare-room";
if (variant == "localized") mod.UsingLocalization = true;
var lowIds = !room;
var caps = new MiscItem(lowIds ? Key(0xF) : mod.GetNextFormKey(), Fallout4Release.Fallout4) { EditorID = "Caps001", Name = "Bottlecap" };
// An invented path, so that the builder has a world model to borrow.
caps.Model = new Model { File = @"StandIn\Cap.nif" };
caps.ObjectBounds = new ObjectBounds { First = new P3Int16(-2, -2, 0), Second = new P3Int16(2, 2, 1) };
mod.MiscItems.Add(caps);
var player = new Npc(lowIds ? Key(0x7) : mod.GetNextFormKey(), Fallout4Release.Fallout4) { EditorID = "Player" };
mod.Npcs.Add(player);
var someoneElse = mod.Npcs.AddNew("SomeoneElse");
string fixtures = "";
var cells = new List<Cell>();
if (room)
{
    var settler = mod.Npcs.AddNew("WorkshopNPC");
    // Like the game's settler in the ways the builder cares about: it has
    // things to go about (packages, a default package list, a script) and
    // takes some of what it is from a template. A copy made by the builder
    // has to come out without the first three, and still with its looks.
    settler.Name = "Settler";
    var sandbox = mod.Packages.AddNew("StandInSandbox");
    var patrol = mod.Packages.AddNew("StandInPatrol");
    // Two whose names read like the game's all-purpose packages, for the
    // builder's list of packages that might keep somebody in one place.
    mod.Packages.AddNew("DefaultStandInHoldPosition");
    mod.Packages.AddNew("DefaultStandInSandboxNearSelf");
    settler.Packages.Add(sandbox.ToLink<IPackageGetter>());
    settler.Packages.Add(patrol.ToLink<IPackageGetter>());
    settler.VirtualMachineAdapter = new VirtualMachineAdapter();
    settler.VirtualMachineAdapter.Scripts.Add(new ScriptEntry { Name = "StandInWorkshopScript" });
    if (variant == "plain-triggers")
    {
        // A plainer settler too: it names no default package list and takes
        // nothing from a template, so a copy has none to keep.
    }
    else
    {
        var defaults = mod.FormLists.AddNew("StandInDefaultPackages");
        defaults.Items.Add(sandbox.ToLink<IFallout4MajorRecordGetter>());
        settler.DefaultPackageList.SetTo(defaults);
        var inCombat = mod.FormLists.AddNew("StandInCombatPackages");
        inCombat.Items.Add(patrol.ToLink<IFallout4MajorRecordGetter>());
        settler.CombatOverridePackageList.SetTo(inCombat);
        settler.UseTemplateActors = Npc.TemplateActorType.Traits | Npc.TemplateActorType.AiPackages | Npc.TemplateActorType.Script
            | Npc.TemplateActorType.Inventory | Npc.TemplateActorType.DefPackList;
        // It names an actor for each of those, as the game's records do: a
        // flag taken away is not enough if the actor named for it stays.
        var looks = mod.LeveledNpcs.AddNew("StandInLCharSettler");
        settler.DefaultTemplate.SetTo(looks);
        settler.TemplateActors = new TemplateActors();
        settler.TemplateActors.TraitTemplate.SetTo(looks);
        settler.TemplateActors.AiPackagesTemplate.SetTo(looks);
        settler.TemplateActors.ScriptTemplate.SetTo(looks);
        settler.TemplateActors.InventoryTemplate.SetTo(looks);
        settler.TemplateActors.DefPackListTemplate.SetTo(looks);
        // Who it is, for the builder's account of it.
        var faction = mod.Factions.AddNew("StandInSettlerFaction");
        settler.Factions.Add(new RankPlacement { Faction = faction.ToLink<IFactionGetter>(), Rank = 0 });
        var keyword = mod.Keywords.AddNew("StandInActorTypeSettler");
        settler.Keywords = new Noggog.ExtendedList<IFormLinkGetter<IKeywordGetter>> { keyword.ToLink<IKeywordGetter>() };
        settler.Voice.SetTo(mod.VoiceTypes.AddNew("StandInSettlerVoice"));
        // And its record is compressed, as large records of the game's are.
        settler.IsCompressed = true;

        // Whom the list offers. A copy that is to be a man or a woman is
        // pointed at one of these, so the builder has to tell which is which:
        // by the actor's own flag, by the actor it takes its looks from, or,
        // where those come from a list again, by whether everybody in that
        // list is of one sex.
        Npc Settler(string id, bool female, IFormLinkGetter<INpcSpawnGetter>? looksFrom = null)
        {
            var one = mod.Npcs.AddNew(id);
            if (female) one.Flags |= Npc.Flag.Female;
            if (looksFrom != null)
            {
                one.UseTemplateActors = Npc.TemplateActorType.Traits;
                one.TemplateActors = new TemplateActors();
                one.TemplateActors.TraitTemplate.SetTo(looksFrom.FormKey);
            }
            return one;
        }
        void Offer(LeveledNpc list, IFormLinkGetter<INpcSpawnGetter> who)
        {
            list.Entries ??= new ExtendedList<LeveledNpcEntry>();
            list.Entries.Add(new LeveledNpcEntry { Data = new LeveledNpcEntryData { Reference = new FormLink<INpcSpawnGetter>(who.FormKey), Level = 1, Count = 1 } });
        }
        // Put in out of order: the builder goes by the ids.
        var woman1 = Settler("StandInSettlerFemale01", female: true);
        var man1 = Settler("StandInSettlerMale01", female: false);
        // His own flag says nothing: his looks are another man's.
        var faceOfMan2 = Settler("StandInFaceMale02", female: false);
        var man2 = Settler("StandInSettlerMale02", female: true, looksFrom: faceOfMan2.ToLink<INpcSpawnGetter>());
        var more = mod.LeveledNpcs.AddNew("StandInLCharSettlerMore");
        Offer(more, Settler("StandInSettlerFemale02", female: true).ToLink<INpcSpawnGetter>());
        Offer(more, Settler("StandInSettlerMale03", female: false).ToLink<INpcSpawnGetter>());
        // Looks drawn again from a list: of both sexes for the one, of women only for the other.
        var anyFace = mod.LeveledNpcs.AddNew("StandInLCharFaces");
        Offer(anyFace, Settler("StandInFaceMale", female: false).ToLink<INpcSpawnGetter>());
        Offer(anyFace, Settler("StandInFaceFemale", female: true).ToLink<INpcSpawnGetter>());
        var womensFaces = mod.LeveledNpcs.AddNew("StandInLCharFacesFemale");
        Offer(womensFaces, Settler("StandInFaceFemaleA", female: true).ToLink<INpcSpawnGetter>());
        Offer(womensFaces, Settler("StandInFaceFemaleB", female: true).ToLink<INpcSpawnGetter>());
        var either = Settler("StandInSettlerAnyFace", female: false, looksFrom: anyFace.ToLink<INpcSpawnGetter>());
        var woman3 = Settler("StandInSettlerWomanAnyFace", female: false, looksFrom: womensFaces.ToLink<INpcSpawnGetter>());
        Offer(looks, man2.ToLink<INpcSpawnGetter>());
        Offer(looks, more.ToLink<INpcSpawnGetter>());
        Offer(looks, woman1.ToLink<INpcSpawnGetter>());
        Offer(looks, either.ToLink<INpcSpawnGetter>());
        Offer(looks, man1.ToLink<INpcSpawnGetter>());
        Offer(looks, woman3.ToLink<INpcSpawnGetter>());
        // And the list names itself, as a careless list might: the builder must not go round for ever.
        Offer(more, looks.ToLink<INpcSpawnGetter>());
    }

    // Things with the names a player sees. The paths are invented.
    MiscItem Thing(string id, string name, string? model)
    {
        var thing = mod.MiscItems.AddNew(id);
        thing.Name = name;
        if (model != null)
        {
            thing.Model = new Model { File = model };
            thing.ObjectBounds = new ObjectBounds { First = new P3Int16(-8, -8, 0), Second = new P3Int16(8, 8, 4) };
        }
        return thing;
    }
    Thing("StandInFolder", "Folder", @"StandIn\Folder.nif");
    // Two things with one name: the builder takes the one with the lower id.
    Thing("StandInHubcapFirst", "Hubcap", @"StandIn\HubcapFirst.nif");
    Thing("StandInHubcapSecond", "Hubcap", @"StandIn\HubcapSecond.nif");
    Thing("StandInHotPlate", "Hot Plate", @"StandIn\HotPlate.nif");
    // Named, and nothing to look like: the builder has to go on to the next name.
    Thing("StandInClipboard", "Clipboard", null);
    // (Nothing here is called Connecting Rod, Adjustable Wrench or Wrench: what
    // is to look like one of those falls back on the bottle cap.)
    var rounds = mod.Ammunitions.AddNew("StandInAmmo44");
    rounds.Name = ".44 Round";
    var revolver = mod.Weapons.AddNew("StandIn44");
    revolver.Name = ".44 Pistol";
    revolver.Model = new Model { File = @"StandIn\Revolver.nif" };
    revolver.Ammo.SetTo(rounds);
    var crate = mod.Containers.AddNew("StandInCrate");
    crate.Name = "Wooden Crate";
    crate.Model = new Model { File = @"StandIn\Crate.nif" };
    crate.ObjectBounds = new ObjectBounds { First = new P3Int16(-30, -20, 0), Second = new P3Int16(30, 20, 25) };
    // Books: three lie in the world as one model (the notes), one as another,
    // one as nothing. Of the notes the first does something when read, which
    // the plugin's papers must not take after.
    var paper = mod.Statics.AddNew("StandInNotePaper");
    Book Paper(string id, string? model, bool scripted = false)
    {
        var book = mod.Books.AddNew(id);
        book.Name = id;
        if (model != null)
        {
            book.Model = new Model { File = model };
            book.ObjectBounds = new ObjectBounds { First = new P3Int16(-5, -7, 0), Second = new P3Int16(5, 7, 1) };
            book.InventoryArt.SetTo(paper);
        }
        if (scripted)
        {
            book.VirtualMachineAdapter = new VirtualMachineAdapter();
            book.VirtualMachineAdapter.Scripts.Add(new ScriptEntry { Name = "StandInNoteScript" });
        }
        return book;
    }
    Paper("StandInNoteScripted", @"StandIn\Note.nif", scripted: true);
    Paper("StandInNotePlain", @"StandIn\Note.nif");
    Paper("StandInNoteOther", @"StandIn\Note.nif");
    Paper("StandInMagazine", @"StandIn\Magazine.nif");
    Paper("StandInBookNoModel", null);
    mod.Armors.AddNew("Pipboy");

    var marker = mod.Statics.AddNew("XMarker");
    fixtures = $" WorkshopNPC={settler.FormKey} XMarker={marker.FormKey}";

    // The test room. Something of the game's own lies in each of its two
    // lists: the builder's copy of the cell must not bring either along.
    var qaSmoke = new Cell(mod.GetNextFormKey(), Fallout4Release.Fallout4) { EditorID = "QASmoke" };
    // The bare room has no name, as a cell may.
    if (variant != "bare-room") qaSmoke.Name = "Stand-In Test Room";
    var clutter = mod.Statics.AddNew("StandInClutter");
    PlacedObject Put(IFormLinkGetter<IPlaceableObjectGetter> what, float x, float y, float z, float headingDegrees = 0)
    {
        var placedObject = new PlacedObject(mod.GetNextFormKey(), Fallout4Release.Fallout4)
        {
            Position = new P3Float(x, y, z),
            Rotation = new P3Float(0, 0, headingDegrees * MathF.PI / 180),
        };
        placedObject.Base.SetTo(what.FormKey);
        return placedObject;
    }
    qaSmoke.Temporary.Add(Put(clutter.ToLink(), 10, 20, 0));
    qaSmoke.Persistent.Add(Put(clutter.ToLink(), -300, 40, 0));
    cells.Add(qaSmoke);

    if (variant is "default" or "localized" or "plain-triggers")
    {
        // Two more things in far corners, so that the room is large enough to
        // hold what the builder places in it.
        qaSmoke.Temporary.Add(Put(clutter.ToLink(), -500, -2000, 0));
        qaSmoke.Temporary.Add(Put(clutter.ToLink(), 3000, 500, 300));
        // Where "coc qasmoke" puts the player: off the origin and turned, so
        // that a mistake in the builder's arithmetic shows.
        var cocMarker = mod.Statics.AddNew("COCMarkerHeading");
        qaSmoke.Temporary.Add(Put(cocMarker.ToLink(), 1200, -800, 64, headingDegrees: 90));

        // Collision layers. The index is what a placed trigger stores.
        foreach (var (id, index) in new[] { ("L_UNIDENTIFIED", 0u), ("L_STATIC", 1u), ("L_TRIGGER", 12u), ("L_ACTORZONE", 22u) })
        {
            var layer = mod.CollisionLayers.AddNew(id);
            layer.Index = index;
        }

        // The game's empty trigger, and box triggers in two other rooms.
        var emptyTrigger = mod.Activators.AddNew("DefaultEmptyTrigger");
        var otherTrigger = mod.Activators.AddNew("StandInScriptedTrigger");
        for (var c = 0; c < 2; c++)
        {
            var otherRoom = new Cell(mod.GetNextFormKey(), Fallout4Release.Fallout4) { EditorID = $"StandInRoom{c}" };
            for (var i = 0; i < 5; i++)
            {
                var trigger = Put((i % 2 == 0 ? emptyTrigger : otherTrigger).ToLink(), 100 * i, 0, 0);
                trigger.Primitive = new PlacedPrimitive
                {
                    Bounds = new P3Float(64 + i, 96, 128),
                    Color = System.Drawing.Color.FromArgb(10, 200, 30),
                    Unknown = 0.25f,
                    Type = PlacedPrimitive.TypeEnum.Box,
                };
                // As the editor writes a box: its reach once more, as the reference's bound. One has none.
                if (i != 4 && variant != "plain-triggers") trigger.BoundHalfExtents = new P3Float((64 + i) / 2f, 48, 64);
                // Most on L_TRIGGER, some on L_ACTORZONE, one with none.
                if (i < 3) trigger.CollisionLayer = 12;
                else if (i == 3) trigger.CollisionLayer = 22;
                otherRoom.Temporary.Add(trigger);
            }
            // A sphere, and a box around something that is not an activator: neither is a box trigger.
            var sphere = Put(emptyTrigger.ToLink(), 0, 500, 0);
            sphere.Primitive = new PlacedPrimitive { Bounds = new P3Float(50, 50, 50), Type = PlacedPrimitive.TypeEnum.Sphere };
            otherRoom.Temporary.Add(sphere);
            var boxedStatic = Put(clutter.ToLink(), 0, 900, 0);
            boxedStatic.Primitive = new PlacedPrimitive { Bounds = new P3Float(50, 50, 50), Type = PlacedPrimitive.TypeEnum.Box };
            otherRoom.Temporary.Add(boxedStatic);
            cells.Add(otherRoom);
        }
    }
}

var cell = new Cell(mod.GetNextFormKey(), Fallout4Release.Fallout4) { EditorID = "StandInCell" };
cells.Add(cell);

// A second placed actor, so a lookup cannot succeed just by being the only one.
var other = new PlacedNpc(mod.GetNextFormKey(), Fallout4Release.Fallout4) { EditorID = "SomeoneElseRef" };
other.Base.SetTo(someoneElse);
cell.Persistent.Add(other);

PlacedNpc? placed = null;
switch (variant)
{
    case "quest-evidence":
    case "weak-evidence":
        for (var i = 0; i < (variant == "quest-evidence" ? 12 : 2); i++)
        {
            var quest = mod.Quests.AddNew($"StandInQuest{i:00}");
            quest.Aliases = new ExtendedList<AQuestAlias>
            {
                new QuestReferenceAlias { ID = 0, Name = i % 3 == 0 ? "PlayerRef" : "Player", ForcedReference = new FormLinkNullable<IPlacedGetter>(Key(0x14)) },
                new QuestReferenceAlias { ID = 1, Name = "SomeoneElse", ForcedReference = new FormLinkNullable<IPlacedGetter>(other.FormKey) },
            };
        }
        break;
    case "default":
    case "localized":
    case "plain-triggers":
    case "bare-room":
        placed = new PlacedNpc(mod.GetNextFormKey(), Fallout4Release.Fallout4) { EditorID = "PlayerREF" };
        placed.Base.SetTo(player);
        break;
    case "unnamed-player":
        placed = new PlacedNpc(Key(0x14), Fallout4Release.Fallout4);
        placed.Base.SetTo(player);
        break;
    case "wrong-player":
        placed = new PlacedNpc(Key(0x14), Fallout4Release.Fallout4);
        placed.Base.SetTo(someoneElse);
        break;
    default:
        Console.Error.WriteLine($"unknown variant: {variant}");
        return 2;
}
if (placed != null) cell.Persistent.Add(placed);

// An interior cell is filed under the last decimal digit of its id (the
// block) and the one before it (the sub-block).
foreach (var c in cells)
{
    var (blockNumber, subNumber) = ((int)(c.FormKey.ID % 10), (int)(c.FormKey.ID / 10 % 10));
    var block = mod.Cells.Records.FirstOrDefault(b => b.BlockNumber == blockNumber);
    if (block == null)
    {
        block = new CellBlock { BlockNumber = blockNumber, GroupType = GroupTypeEnum.InteriorCellBlock };
        mod.Cells.Records.Add(block);
    }
    var sub = block.SubBlocks.FirstOrDefault(s => s.BlockNumber == subNumber);
    if (sub == null)
    {
        sub = new CellSubBlock { BlockNumber = subNumber, GroupType = GroupTypeEnum.InteriorCellSubBlock };
        block.SubBlocks.Add(sub);
    }
    sub.Cells.Add(c);
}

Directory.CreateDirectory(Path.GetDirectoryName(Path.GetFullPath(path))!);
// Real masters use ids below 0x800; a stand-in may too.
mod.BeginWrite.ToPath(path).WithNoLoadOrder().NoCheckIfLowerRangeDisallowed().Write();
Console.WriteLine($"wrote stand-in master ({variant}): Caps001={caps.FormKey} player reference={(placed == null ? "none" : $"{placed.FormKey} EditorID='{placed.EditorID}'")}{fixtures}");
return 0;
