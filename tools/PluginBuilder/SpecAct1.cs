namespace Tlm.PluginBuilder;

// Act I, first section: a rough cut a person can walk through
// (docs/design/TLM_ACT1_first_section.md). DEVELOPMENT ONLY: the people are
// copies of the game's settler and stand in the game's own test room. It must
// not ship as it is.
//
// The two real quests are not touched by any of it. A development quest,
// TLM_A1, holds what is placed here in aliases of its own, and its script
// (TLM:Act1Walk) puts those references into the real quests' aliases while
// the game runs, as the test scenarios do with their stand-ins.
//
// Nothing here may read a field of Spec that is not a constant: Spec's own
// lists are built from these, so its fields are not there yet when these are.
//
// All text is PROVISIONAL. Lines marked "design" are from the two quest
// designs (TLM_MQ01 section 8, TLM_SQ01 sections 4 and 6); lines marked NEW
// were written for this cut. The player's part is a button, and the buttons
// are the short answers the designs list, or a plain word for "go on".
public static class Act1
{
    public const string QuestId = "TLM_A1";
    const string Cell = Spec.TrialCell;
    const string Settler = "WorkshopNPC";

    // ------------------------------------------------------------- people
    // Each a copy of the game's settler with nothing to go about: no packages,
    // no script, no default package list (what stood still on 2026-11-13),
    // in a faction of the plugin's own and in none of the game's, and with a
    // temper that starts no fight. The looks of each are those of one of the
    // settlers the game's own list offers, of the sex given: the first man
    // listed here gets the first, the second the second.
    const string Town = "TLM_Fac_MercyCrossing";
    const string Caravan = "TLM_Fac_Caravan";
    const string Cutters = "TLM_Fac_Cutters";

    static NpcSpec Person(string editorId, string name, string sex, string? faction, bool helpsItsOwn = false) =>
        new(editorId, name, CopyFrom: Settler, KeepDefaultPackageList: false, Sex: sex, Faction: faction, StandsBy: true, HelpsItsOwn: helpsItsOwn);

    public static readonly NpcSpec[] Npcs =
    {
        Person("TLM_NPC_SHERIFF_MERCY", "Owen Pritchard", "male", Town),
        Person("TLM_NPC_GUNSMITH_MERCY", "Ada Pike", "female", Town),
        Person("TLM_NPC_MERCHANT_MERCY", "Silas Vane", "male", Town),
        Person("TLM_NPC_PHYSICIAN_MERCY", "Miriam Keene", "female", Town),
        Person("TLM_NPC_DEPUTY_MERCY", "Jonah Talbot", "male", Town),
        Person("TLM_NPC_FREIGHT_MERCY", "Corwin Haskell", "male", Town),
        // Dead when the room loads. He keeps the settler's factions: he is
        // nobody's ally any more.
        Person("TLM_NPC_MARSHAL_DEAD", "Tobias Gantt", "male", null),
        Person("TLM_NPC_CARAVAN_MASTER", "Nell Fenwick", "female", Caravan),
        Person("TLM_NPC_CARAVAN_DROVER", "Abel Rudd", "male", Caravan),
        // The Cutters take each other's side: a fight with one is a fight with all.
        Person("TLM_NPC_CUTTER_LEAD", "Reese Dunmore", "male", Cutters, helpsItsOwn: true),
        Person("TLM_NPC_CUTTER_01", "Tellico Cutter", "male", Cutters, helpsItsOwn: true),
        Person("TLM_NPC_CUTTER_02", "Tellico Cutter", "female", Cutters, helpsItsOwn: true),
        Person("TLM_NPC_CUTTER_03", "Tellico Cutter", "male", Cutters, helpsItsOwn: true),
    };

    // ------------------------------------------------------------- things
    // Each looks like one of the game's own things, found by the name a
    // player sees (the first of the names that the game has); only the path
    // of the model is taken.
    public static readonly ActivatorSpec[] Activators =
    {
        new("TLM_TRIG_AmbushSight"),
        new("TLM_TRIG_TownGate"),
        new("TLM_ACTI_BrakeShoes", "Brake shoes", new[] { "Hubcap", "Gears" }, "Examine"),
        new("TLM_ACTI_DrawBar", "Draw-bar", new[] { "Connecting Rod", "Adjustable Wrench", "Wrench" }, "Examine"),
        new("TLM_ACTI_NoticeBoard", "Notice board", new[] { "Clipboard", "Folder" }, "Read"),
        new("TLM_ACTI_Stove", "Stove", new[] { "Hot Plate", "Cooking Pot" }, "Use"),
    };

    public static readonly ContainerSpec[] Containers =
    {
        new("TLM_CONT_WagonCargo", "Fenwick's Cargo", new[] { "Wooden Crate", "Crate", "Steamer Trunk", "Trunk", "Suitcase", "Toolbox" },
            HoldsVanillaItem: "Caps001", Count: 40),
    };

    /// <summary>What the dispatch looks like (the item itself is in Spec.MiscItems, where the quests' scripts know it).</summary>
    public static readonly string[] DispatchLooksLike = { "Folder", "Clipboard" };

    /// <summary>The marshal's revolver: the game's own, by the name a player sees.</summary>
    public static readonly string[] RevolverNames = { ".44 Pistol", "Pipe Revolver", "10mm Pistol" };
    public const int RevolverRounds = 6;

    // ------------------------------------------------- where things stand
    // From the test room's arrival point: so many units ahead, to the right,
    // and up. The wreck to the left, the road ahead, the town to the right.
    // Everything starts disabled, so that the room is as it was for every
    // other scenario until TLM:Act1Walk switches it on.
    public const float BoxHalf = 100f;
    static readonly float[] Box = { BoxHalf, BoxHalf, BoxHalf };

    static PlacedSpec Own(string what, string baseId, float ahead, float right, float up = 0, bool dead = false) =>
        new("TLM_REF_A1_" + what, Cell, baseId, null, ahead, right, up, InitiallyDisabled: true, StartsDead: dead);

    public static readonly PlacedSpec[] Placed =
    {
        // The wreck.
        Own("Marshal", "TLM_NPC_MARSHAL_DEAD", 230, -420, dead: true),
        Own("Dispatch", "TLM_MISC_Dispatch", 190, -360, 10),
        new("TLM_REF_A1_Revolver", Cell, "the marshal's revolver", "Weapon", 260, -340, 10, InitiallyDisabled: true, BaseNames: RevolverNames),
        Own("Journal", "TLM_BOOK_MarshalLog", 200, -470, 10),
        Own("Ledger", "TLM_BOOK_RailMaintLedger", 330, -600, 10),
        Own("BrakeShoes", "TLM_ACTI_BrakeShoes", 360, -520, 12),
        Own("DrawBar", "TLM_ACTI_DrawBar", 450, -480, 12),
        // The road.
        new("TLM_REF_A1_AmbushSight", Cell, "TLM_TRIG_AmbushSight", null, 300, -150, 100, InitiallyDisabled: true, BoxHalfExtents: Box),
        new("TLM_REF_A1_AmbushCenter", Cell, "XMarker", "Static", 540, -200, 0, InitiallyDisabled: true),
        Own("Wagon", "TLM_CONT_WagonCargo", 520, -330),
        Own("Nell", "TLM_NPC_CARAVAN_MASTER", 600, -200),
        Own("Abel", "TLM_NPC_CARAVAN_DROVER", 640, -320),
        Own("Dunmore", "TLM_NPC_CUTTER_LEAD", 480, -180),
        Own("Cutter1", "TLM_NPC_CUTTER_01", 520, -80),
        Own("Cutter2", "TLM_NPC_CUTTER_02", 420, -60),
        Own("Cutter3", "TLM_NPC_CUTTER_03", 560, -260),
        // The town.
        new("TLM_REF_A1_TownGate", Cell, "TLM_TRIG_TownGate", null, 300, 150, 100, InitiallyDisabled: true, BoxHalfExtents: Box),
        Own("Talbot", "TLM_NPC_DEPUTY_MERCY", 380, 260),
        Own("Pritchard", "TLM_NPC_SHERIFF_MERCY", 600, 200),
        Own("Pike", "TLM_NPC_GUNSMITH_MERCY", 700, 300),
        Own("Vane", "TLM_NPC_MERCHANT_MERCY", 700, 120),
        Own("Keene", "TLM_NPC_PHYSICIAN_MERCY", 520, 330),
        Own("Haskell", "TLM_NPC_FREIGHT_MERCY", 460, 420),
        Own("NoticeBoard", "TLM_ACTI_NoticeBoard", 480, 180, 12),
        Own("Stove", "TLM_ACTI_Stove", 600, 400, 12),
        new("TLM_REF_A1_CaravanYard", Cell, "XMarker", "Static", 620, 320, 0, InitiallyDisabled: true),
    };

    // ------------------------------------------------------------- the talk
    // Who is who to TLM:Act1Talk (the number on each speaker's alias) and to
    // TLM:Act1Walk, which holds the lines. The two scripts carry the same
    // numbers; tools/check_consistency.py compares them.
    public const int WhoDunmore = 1, WhoNell = 2, WhoAbel = 3, WhoCutter = 4, WhoPritchard = 5,
        WhoPike = 6, WhoVane = 7, WhoKeene = 8, WhoTalbot = 9, WhoHaskell = 10, WhoRevolver = 20;

    const string GoOn = "Continue";
    const string Silent = "(Say nothing)";
    const string More = "There's something else from that train.";      // design (TLM_SQ01 section 6, A)
    const string Marshals = "The line keeps losing marshals. ";         // design: how every debrief begins

    static MessageSpec Says(string id, string who, string line, params string[] buttons) =>
        new("TLM_MSG_A1_" + id, who, who + ": \"" + line + "\"", Box: true,
            (buttons.Length == 0 ? new[] { GoOn } : buttons).Select(b => new ButtonSpec(b)).ToArray());

    const string Dunmore = "Reese Dunmore", Nell = "Nell Fenwick", Abel = "Abel Rudd", Cutter = "Tellico Cutter",
        Pritchard = "Owen Pritchard", Pike = "Ada Pike", Vane = "Silas Vane", Keene = "Miriam Keene",
        Talbot = "Jonah Talbot", Haskell = "Corwin Haskell";

    public static readonly MessageSpec[] Messages =
    {
        // Said once, on the screen's edge, when the first section has been set up.
        new("TLM_MSG_A1_Begin", null, "Act I, first section. The wreck is to your left, the road ahead, Mercy Crossing to your right.", Box: false),

        // ---- Reese Dunmore, at the wagon (design 8.1). The button order is
        // the contract with TLM:Act1Walk.TalkDunmore.
        Says("DunmoreHold", Dunmore, "Keep walking. Or stay and pick up a share.",
            "Pritchard hangs road-takers. Leave.", "Let them go.", "What kind of share?", "Not my business."),
        Says("DunmoreShare", Dunmore, "Half the cargo. The drover won't be a problem.", "Done.", "No."),
        Says("DunmoreBreaks", Dunmore, "Not for one wagon. We're gone."),                           // NEW
        Says("DunmoreTurns", Dunmore, "Then you're in the way."),                                   // NEW
        Says("DunmoreDeal", Dunmore, "Smart. Stand clear."),                                        // NEW
        Says("DunmoreAfter", Dunmore, "We're done here. Walk on."),                                 // NEW

        // ---- Nell Fenwick (design 8.2).
        Says("NellLive", Nell, "They want the wagon. Don't make it worse."),                        // NEW
        Says("NellSaved", Nell, "They'd have had the wagon and Abel both. Take this. It's what I can spare.",   // NEW
            "Take it.", "Keep it.", "Who hit you?"),
        Says("NellWho", Nell, "Tellico Cutters. Reese Dunmore's lot."),                             // NEW
        Says("NellOffer", Nell, "Take this. It's what I can spare.", "Take it.", "Keep it."),       // NEW
        Says("NellSavedAfter", Nell, "We'll be at the yard in Mercy Crossing. I won't forget it."), // NEW
        Says("NellEvaded", Nell, "You watched. You kept walking.", "I couldn't.", "Not my fight.", Silent),   // design
        // She refuses to talk (design). Not a box: there is nothing to answer.
        new("TLM_MSG_A1_NellSilent", Nell, "Nell Fenwick looks through you and says nothing.", Box: false),
        Says("NellMissed", Nell, "They took the wagon and they killed Abel. Nobody came."),         // NEW

        // ---- Abel Rudd and the three Cutters.
        Says("AbelLive", Abel, "Don't look at me. Look at them."),                                  // NEW
        Says("AbelSaved", Abel, "Thought that was the end of me. Obliged."),                        // NEW
        Says("CutterLive", Cutter, "Talk to Dunmore."),                                             // NEW

        // ---- Sheriff Owen Pritchard (design 8.3).
        Says("PritchardNoCase", Pritchard, "Gantt's train never reached us. Where's his case?",
            "I haven't looked.", "Lost it.", "I'll go back for it."),
        Says("PritchardNoCaseAndMore", Pritchard, "Gantt's train never reached us. Where's his case?",
            "I haven't looked.", "Lost it.", "I'll go back for it.", More),
        Says("PritchardMark", Pritchard, "Six hours east at the wreck. I'll mark it."),
        Says("PritchardCase", Pritchard, "Off the Tellico wreck. That's Tobias Gantt's case you're carrying.",
            "Hand over the dispatch", "Not yet."),
        Says("PritchardCaseAndMore", Pritchard, "Off the Tellico wreck. That's Tobias Gantt's case you're carrying.",
            "Hand over the dispatch", "Not yet.", More),
        Says("PritchardReported", Pritchard, "Show me. I'll take copies and send word up the line."),   // NEW
        Says("DebriefSaved", Pritchard, Marshals + "Word is Nell Fenwick's wagon got through. Obliged."),
        Says("DebriefEvaded", Pritchard, Marshals + "Abel Rudd's dead on the Tellico road. Nell Fenwick says someone watched it happen.",
            "I watched.", "I never saw it.", Silent),
        Says("DebriefWitness", Pritchard, Marshals + "Nell Fenwick's at Miriam Keene's clinic. Her account is different from the one you'll give me.",
            "I took a share.", "The Cutters forced it.", "She's lying.", Silent),
        // NEW: the design's line names Nell Fenwick; this is for when the one left to speak is Abel Rudd.
        Says("DebriefWitnessAbel", Pritchard, Marshals + "Abel Rudd's at Miriam Keene's clinic. His account is different from the one you'll give me.",
            "I took a share.", "The Cutters forced it.", "He's lying.", Silent),
        Says("DebriefNoWitness", Pritchard, Marshals + "Two dead on the Tellico road and no one to say how."),
        Says("DebriefMissed", Pritchard, Marshals + "Fenwick's wagon was hit on the Tellico road, and you came in by it."),   // NEW
        Says("DebriefLost", Pritchard, Marshals + "Nell Fenwick's wagon never came in."),                                  // NEW
        Says("PritchardHandOff", Pritchard, "Greenwater's food has gone short. Red Hollow's sealed the mine. Iron Junction's rails are being cut. Pick one. I don't have the people for all three."),
        Says("PritchardAfter", Pritchard, "Greenwater, Red Hollow or Iron Junction. Pick one."),    // NEW
        Says("PritchardAfterAndMore", Pritchard, "Greenwater, Red Hollow or Iron Junction. Pick one.", GoOn, More),   // NEW

        // ---- The town.
        Says("PikeHello", Pike, "Pike. I fix what shoots. Forty-fours are scarce, so make yours count."),   // NEW
        Says("PikeBook", Pike, "They used to buy shoes off me every season. Haven't taken a pair since spring. I kept the count. Here, look.",   // design
            "Look at her parts book", "Leave it"),
        Says("PikeAfter", Pike, "The count's the count. I don't know who wrote yours."),            // NEW
        Says("PikeHaskell", Pike, "Corwin signed for freight. That's all he did."),                 // design
        Says("VaneHello", Vane, "Vane. If it came down the line, I can price it."),                 // NEW
        Says("VaneOffer", Vane, "Paper like this makes trouble for everyone. I'll take it off your hands.",   // design
            "Sell him the ledger and the journal", "Keep them"),
        Says("VanePaid", Vane, "Paid in full. Good day to you."),                                   // NEW
        Says("KeeneHello", Keene, "Clinic's open. If you're bleeding, sit. If you're not, don't touch anything."),   // NEW
        Says("KeeneNell", Keene, "Nell Fenwick's on the cot. She'll mend. Leave her be."),          // NEW
        Says("KeeneHaskell", Keene, "Corwin signed for freight. That's all he did."),               // design
        Says("TalbotGate", Talbot, "Deputy Talbot. Keep your iron holstered inside the posts."),    // NEW
        Says("TalbotAfter", Talbot, "Sheriff's got your paper. He'll want a word more, I'd reckon."),   // NEW
        Says("Haskell", Haskell, "Freight's signed for at the shed. Line 14's run nothing since the wreck."),   // NEW
    };

    // ------------------------------------------------------------ the quest
    // One alias for every reference placed above, in the order they are
    // placed; and which alias of the real quests each is put into.
    static ScriptBind Talk(int who) => new("TLM:Act1Talk", new IntProp("Who", who));

    sealed record Part(string Alias, string Name, bool IsPerson = false, bool AllowDead = false, bool Protected = false, int Who = 0,
        string[]? Into = null);

    // "TLM_MQ01:Marshal" reads: the alias Marshal of TLM_MQ01.
    static readonly Part[] Parts =
    {
        new("Marshal", "Tobias Gantt", IsPerson: true, AllowDead: true, Into: new[] { "TLM_MQ01:Marshal", "TLM_SQ01:Marshal" }),
        new("Dispatch", "the sealed dispatch", Into: new[] { "TLM_MQ01:Dispatch" }),
        new("Revolver", "the marshal's revolver", Who: WhoRevolver, Into: new[] { "TLM_MQ01:Revolver" }),
        new("Journal", "the marshal's journal", Into: new[] { "TLM_SQ01:Journal" }),
        new("Ledger", "the maintenance ledger", Into: new[] { "TLM_SQ01:Ledger" }),
        new("BrakeShoes", "the brake shoes", Into: new[] { "TLM_SQ01:BrakeShoes" }),
        new("DrawBar", "the draw-bar", Into: new[] { "TLM_SQ01:DrawBar" }),
        new("AmbushSight", "the place the ambush is seen from", Into: new[] { "TLM_MQ01:AmbushTrigger" }),
        new("AmbushCenter", "the middle of the ambush", Into: new[] { "TLM_MQ01:AmbushCenter" }),
        new("Wagon", "the wagon's cargo", Into: new[] { "TLM_MQ01:Wagon" }),
        new("Nell", "Nell Fenwick", IsPerson: true, Who: WhoNell, Into: new[] { "TLM_MQ01:CaravanMaster" }),
        new("Abel", "Abel Rudd", IsPerson: true, Who: WhoAbel, Into: new[] { "TLM_MQ01:CaravanDrover" }),
        new("Dunmore", "Reese Dunmore", IsPerson: true, Who: WhoDunmore, Into: new[] { "TLM_MQ01:CutterLead" }),
        new("Cutter1", "the first Cutter", IsPerson: true, Who: WhoCutter, Into: new[] { "TLM_MQ01:CutterA" }),
        new("Cutter2", "the second Cutter", IsPerson: true, Who: WhoCutter, Into: new[] { "TLM_MQ01:CutterB" }),
        new("Cutter3", "the third Cutter", IsPerson: true, Who: WhoCutter, Into: new[] { "TLM_MQ01:CutterC" }),
        new("TownGate", "the town gate", Into: new[] { "TLM_MQ01:TownGate" }),
        // The townsfolk the real quests hold in no alias, or in one without a
        // flag, are Protected here: only the player can kill them.
        new("Talbot", "Jonah Talbot", IsPerson: true, Protected: true, Who: WhoTalbot),
        new("Pritchard", "Owen Pritchard", IsPerson: true, Who: WhoPritchard, Into: new[] { "TLM_MQ01:SheriffPritchard", "TLM_SQ01:Pritchard" }),
        new("Pike", "Ada Pike", IsPerson: true, Protected: true, Who: WhoPike, Into: new[] { "TLM_SQ01:Pike" }),
        new("Vane", "Silas Vane", IsPerson: true, Protected: true, Who: WhoVane, Into: new[] { "TLM_SQ01:Vane" }),
        new("Keene", "Miriam Keene", IsPerson: true, Protected: true, Who: WhoKeene),
        new("Haskell", "Corwin Haskell", IsPerson: true, Protected: true, Who: WhoHaskell, Into: new[] { "TLM_SQ01:Haskell" }),
        new("NoticeBoard", "the notice board", Into: new[] { "TLM_SQ01:NoticeBoard" }),
        new("Stove", "the stove", Into: new[] { "TLM_SQ01:Stove" }),
        new("CaravanYard", "the caravan yard", Into: new[] { "TLM_MQ01:CaravanYard" }),
    };

    static (string Quest, string Alias) Split(string into)
    {
        var at = into.IndexOf(':');
        return (into[..at], into[(at + 1)..]);
    }

    static IEnumerable<(Part Part, string Into)> Casts => Parts.SelectMany(p => (p.Into ?? Array.Empty<string>()).Select(i => (p, i)));

    static Prop Line(string id) => new FormProp("Say" + id, "TLM_MSG_A1_" + id);
    static Prop Mine(string alias) => new AliasProp("Alias_" + alias, alias);

    public static readonly QuestSpec Quest = new(
        QuestId, "The Last Meridian (Act I, first section: rough cut)", "None", 30, StartGameEnabled: false,
        Stages: Array.Empty<StageSpec>(),
        Objectives: Array.Empty<ObjectiveSpec>(),
        Aliases: Parts.Select(p => new AliasSpec(p.Alias, Fill.Placed, AllowDisabled: true, AllowDead: p.AllowDead, Protected: p.Protected,
            Placed: "TLM_REF_A1_" + p.Alias,
            Scripts: p.Who == 0 ? Array.Empty<ScriptBind>() : new[] { Talk(p.Who) })).ToArray(),
        Script: new ScriptBind("TLM:Act1Walk", new Prop[]
        {
            new FormProp("TLM_MQ01", "TLM_MQ01"),
            new FormProp("TLM_SQ01", "TLM_SQ01"),
            new FormProp("TLM_G_CaravanOutcome", "TLM_G_CaravanOutcome"),
            new FormProp("TLM_G_CaravanMethod", "TLM_G_CaravanMethod"),
            new FormProp("TLM_G_CaravanAliveAtMercy", "TLM_G_CaravanAliveAtMercy"),
            new FormProp("TLM_G_Rep_MercyCrossing", "TLM_G_Rep_MercyCrossing"),
            new FormProp("TLM_G_MQ01_Done", "TLM_G_MQ01_Done"),
            new FormProp("TLM_G_MQ01_DebriefVariant", "TLM_G_MQ01_DebriefVariant"),
            new FormProp("TLM_G_SQ01_EvidenceLevel", "TLM_G_SQ01_EvidenceLevel"),
            new FormProp("TLM_G_SQ01_Outcome", "TLM_G_SQ01_Outcome"),
            new FormProp("TLM_G_SQ01_YardAlerted", "TLM_G_SQ01_YardAlerted"),
            new FormProp("TLM_G_SQ01_VaneHasLedger", "TLM_G_SQ01_VaneHasLedger"),
            new FormProp("TLM_G_SQ01_HaskellScapegoated", "TLM_G_SQ01_HaskellScapegoated"),
            // Everything placed, to switch on; the people among it; and what is put where.
            new AliasListProp("Everything", Parts.Select(p => (QuestId, p.Alias)).ToArray()),
            new StringListProp("EverythingNames", Parts.Select(p => p.Name).ToArray()),
            new AliasListProp("People", Parts.Where(p => p.IsPerson).Select(p => (QuestId, p.Alias)).ToArray()),
            new StringListProp("PeopleNames", Parts.Where(p => p.IsPerson).Select(p => p.Name).ToArray()),
            new AliasListProp("CastFrom", Casts.Select(c => (QuestId, c.Part.Alias)).ToArray()),
            new AliasListProp("CastInto", Casts.Select(c => Split(c.Into)).ToArray()),
            new StringListProp("CastNames", Casts.Select(c => $"{c.Part.Name} as {Split(c.Into).Alias} of {(Split(c.Into).Quest == "TLM_MQ01" ? "the main quest" : "the side quest")}").ToArray()),
            Mine("Marshal"), Mine("Dispatch"), Mine("Revolver"), Mine("Journal"), Mine("Ledger"),
            Mine("AmbushSight"), Mine("TownGate"), Mine("Nell"), Mine("Abel"), Mine("Dunmore"),
            new FormProp("DispatchItem", "TLM_MISC_Dispatch"),
            new FormProp("LedgerItem", "TLM_BOOK_RailMaintLedger"),
            new FormProp("JournalItem", "TLM_BOOK_MarshalLog"),
            new VanillaProp("Caps", "Caps001", "MiscItem"),
            new VanillaProp("MarkerBase", "XMarker", "Static"),
            // The thing on the player's arm. A game started in the test room
            // has none, and without it nothing picked up can be read.
            new VanillaProp("PipBoy", "Pipboy", "Armor"),
            new AmmoOfWeaponNamedProp("RevolverRounds", RevolverNames),
        }.Concat(Messages.Select(m => Line(m.EditorId["TLM_MSG_A1_".Length..]))).ToArray()));
}
