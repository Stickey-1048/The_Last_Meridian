namespace Tlm.PluginBuilder;

// NIGHT-MAIL-STORY-001: Chapter 2's rail road, "The Night Mail"
// (docs/design/NIGHT_MAIL_STORY_001.md and its order). A CANDIDATE: not
// compiled, not built against the game's master, not run in the game.
//
// Two quests and a cell. TLM_MQ02A is the road: the accepted stages and
// objectives, the facts later chapters read, and TLM:MQ02AQuest, which holds
// every rule. TLM_NM is the greybox, DEVELOPMENT ONLY: the placed pieces in
// aliases of its own, the lines, and TLM:NightMailWalk, which shows them and
// stages the scenes. TLM_CELL_NightMail is a cell of this plugin's own: five
// labelled zones on three floors of the game's floor tile. The exterior
// builder clones TLM_NM and gives the owner's world its own two Mercy pieces;
// everything else stays in this plugin's cell, and TLM_MQ02A stays one record.
//
// EVERY SPOKEN LINE, BUTTON, JOURNAL TEXT AND DOCUMENT IS COPIED from the
// accepted writing in assets/incoming/act1/story (as accepted at d142104): the
// constants below marked GENERATED were written out of the JSON by a script,
// not typed. Which field each record takes its text from, when it is shown,
// and what of the writing is deliberately not imported, is in
// docs/design/NIGHT_MAIL_STORY_001_MAPPING.json;
// tools/papyrus_sim/test_night_mail_projection.py compares the plugin as
// built with those fields, character by character. Change a line there first,
// by the writing's own process; never here.
//
// Text in square brackets is this build speaking: what is representation,
// what is not playable, what a test should write down. It is never put in a
// character's mouth.
//
// Nothing here may read a field of Spec that is not a constant (see Act1).
public static class NightMail
{
    public const string QuestId = "TLM_MQ02A";
    public const string StageQuestId = "TLM_NM";
    public const string CellId = "TLM_CELL_NightMail";
    public const string CellName = "Iron Junction (Night Mail greybox)";
    public const string BookId = "TLM_BOOK_HymnalFlyleaf";
    public const string StampId = "TLM_MISC_OstranderStamp";
    public const string MessagePrefix = "TLM_MSG_NM_";

    // ------------------------------------------------- the accepted writing
    // GENERATED from assets/incoming/act1/story by copying, never retyped: characters.json,
    // quests/tlm_mq02a.json, talk/tlm_mq02a.json, talk/tlm_mq02.json, documents.json.
    public const string Lockridge = "Augusta Lockridge";
    public const string Billie = "Wilhelmina Tupper";
    public const string Dole = "Ezekiel Dole";
    public const string QuestName = "The Night Mail";
    // The accepted journal text of each stage, by number.
    static readonly Dictionary<int, string> Log = new()
    {
        [10] = "Iron Junction is a roundhouse with a wall round it and a woman on the turntable who points her office at whoever is coming.",
        [20] = "Gussie Lockridge has lost four trains in a month. Tonight's carries the payroll and the valley's fever medicine. She wants a gun on the footplate and is not asking twice.",
        [30] = "Old Contrary is under steam. Billie Tupper drives as if the dark owed her money.",
        [40] = "Lanterns across the track. A rail pulled out of true. A tall man on a flatcar with a hymnal, and thirty rifles for a choir.",
        [41] = "Billie put the regulator through the roof. Old Contrary took the gap in the air and came down on the rails, more or less.",
        [42] = "Preacher Dole is lying across the rail he pulled. His congregation went up the hill without singing.",
        [43] = "You sold the Night Mail. The payroll and the fever medicine went up the hill on the Black Rail's shoulders, and Billie Tupper was put off to walk home.",
        [44] = "Billie backed her out of the Cut in the dark. The mail is safe and no use to anybody, and the line is shut.",
        [50] = "The preacher's collection plate is full of silver slugs. Each is stamped with a small square mark.",
        [55] = "The name written in the front of the preacher's hymnal is R. Ostrander, Inspector of Way.",
        [60] = "The dead inspector's stamp is in Gussie Lockridge's drawer. The pad is still wet.",
        [61] = "You left the stamp where it was. The trains will run, and Ostrander will go on passing them.",
        [62] = "Gussie Lockridge signed her own name under every entry for a year back. It took her until morning.",
        [63] = "You took the stamp. Gussie Lockridge watched you carry it out and did not turn her office to follow.",
    };
    static readonly Dictionary<int, string> Objective = new()
    {
        [10] = "Find the yardmaster at Iron Junction",
        [20] = "Ride the footplate of the Night Mail",
        [40] = "Get the Night Mail through Sawtooth Cut, or do not",
        [55] = "(Optional) Find out who has been signing for a dead man",
    };
    // talk/tlm_mq02a.json: each line's text, by its id; and the text only of Pritchard's two rail lines.
    static readonly Dictionary<string, string> Line = new()
    {
        ["lockridge_default"] = "Honey, if it has wheels I can talk about it all day. If it hasn't, see my clerk.",
        ["lockridge_gate"] = "Well now. Owen Pritchard's sent me a gun with legs. Sit. Four trains in a month, honey, and a hymn chalked on every boiler. Tonight I send the payroll and the fever physic through Sawtooth Cut. I want you on the footplate.",
        ["lockridge_gate_alerted"] = "So you're the one sent Pritchard a page of my Line 14. I've had the inspector's desk nailed shut since, and no, you may not see in it. Sit down anyway. I need a gun more than I need to like you.",
        ["lockridge_gate_sold"] = "Silas Vane wrote me. A certain book has come into his keeping, he says, and no inquiry need ever trouble me. Now who sold him that, I wonder. Sit down, honey. Let's see what else you'll do for money.",
        ["lockridge_dole"] = "Preacher Dole. He lifts a rail, lets the Lord and the grade do the rest, and holds a service on what's left. Thirty rifles say amen. I'd admire to see him answer for it. I'd admire it more to see my mail get through.",
        ["lockridge_rails"] = "Every car on this line is passed by the Inspector of Way, and stamped. You want to read stamps, read stamps. The train leaves at dark whether you can read or not.",
        ["lockridge_hired"] = "Billie drives. Do what she says about the engine and nothing she says about anything else. And honey? If it comes down to the mail or the girl, you bring me the girl.",
        ["tarrow_default"] = "If it's about the brakes, I know. If it's about a bet, I'm listening.",
        ["tarrow_footplate"] = "You're the gun? You don't look like much. Neither does she. Old Contrary: eleven tons, nine of them spite. Hold that. Not that, that comes off. Bet you a day's pay you're sick before the Cut.",
        ["tarrow_cut_before"] = "Rail's spread on the left hand, about so much. Not gone. Spread. Anything heavy lies down on its side. Anything light, going like the devil had a mortgage on it... well. Nobody's tried. Don't tell Gussie I said that.",
        ["tarrow_in_cut"] = "Lanterns. That's him. That's all of them. Rail's out just where I said. I can stop her, I can back her, or I can find out something nobody knows about this engine. Your gun, your say. QUICK.",
        ["dole_default"] = "The service is at dusk, traveller, wherever the rail gives out. All are welcome. Most arrive suddenly.",
        ["dole_sermon"] = "Evening, traveller. The text tonight is four foot eight and one half. I measured this rail nineteen years, and they signed my name to it after I was in the ground. Step down off her lie and hear the rest.",
        ["dole_name"] = "Ostrander. Inspector of Way. I condemned the Greenwater trestle and they ran a train over it that same week. Then the fever, and a pest-house, and a hymn. Somebody in that yard still stamps my name on scrap iron. Ask who.",
        ["dole_silver"] = "Comes by a man who comes by a man. A square mark on every piece. It buys powder. I'd lift these rails for love, traveller. I take the silver so the Lord is not left out of pocket.",
        ["dole_share"] = "A third of the pay-chest, and the girl walks home unharmed. The physic goes up the hill: my people have the fever too, and nobody ever sent them a train. Say done and step off the footplate.",
        ["dole_face"] = "Then here endeth the lesson. I will count three for you, which is three more than the yard gave anybody on the morning train. One.",
        ["tarrow_ran"] = "HA! Did you... we were in the AIR! She's bent, she's a little bit on fire, I think I bit my tongue through. You owe me a day's pay. No. I owe you. Oh, Gussie's going to skin me.",
        ["tarrow_backed"] = "Well. Nobody's dead. That's the best I can say for it. You want to tell her, or shall I? ...I'll tell her. You'd only make it sound sensible.",
        ["tarrow_walking"] = "Don't. Don't say one word to me. It's eleven miles and I know every tie. There are children in that valley with the fever and I was going to drive it to them. You think of that when you spend it.",
        ["lockridge_after_ran"] = "You jumped my engine over a hole. She's a wreck. The physic's in the valley and the payroll's in my safe and I have not been this happy since I was a bride. Ask me for something.",
        ["lockridge_after_dole"] = "Dole's dead? ...You'll think me foolish. Six years back I read at a funeral for a man who used to stand right where you are and tell me no. I'd have liked to hear no again. Well. The line's open.",
        ["lockridge_after_sold"] = "Billie walked in at four this morning. Eleven miles. She told me what you did, and then she asked me not to have you shot. So I'm asking you nicely, honey. Get out of my yard.",
        ["lockridge_hymnal"] = "That's his hand. That's Reuben's own hand. He's ALIVE? ...Top drawer, honey. Go on. You'd find it anyway. Nobody would come out to inspect a line that kills inspectors. So Reuben went on inspecting.",
        ["lockridge_stamp"] = "Every stamp was a train that ran. Physic, seed corn, coal. I never did the other sum and I'll thank you not to do it for me. Well? You've the drawer open. What becomes of an old woman and a dead man's name?",
        ["pritchard_hears_rail_after_fair"] = "You have a rail-payment lead. Tell me how you learned it. If you travelled the line, separate what you saw from what somebody told you.",
        ["pritchard_hears_rail_after_fair_unknown"] = "If you haven't taken the rail, ask about Iron Junction. If you have, tell me what you saw. Don't name a payer unless you've learned who paid.",
    };
    // Each line's button labels, in the line's order.
    static readonly Dictionary<string, string[]> Labels = new()
    {
        ["lockridge_gate"] = new[] { "I'll ride your mail.", "Who chalks the hymns?", "Who passes your trains as sound?", "Not tonight." },
        ["lockridge_gate_alerted"] = new[] { "I'll ride your mail.", "Who signed that page?", "Not tonight." },
        ["lockridge_gate_sold"] = new[] { "I'll ride your mail.", "Who chalks the hymns?", "Not tonight." },
        ["tarrow_footplate"] = new[] { "You're on.", "What's in the Cut?", "Just drive." },
        ["tarrow_in_cut"] = new[] { "Stoke her. Run the gap.", "Stop her. I'm getting down.", "Back her out." },
        ["dole_sermon"] = new[] { "Stand aside, Preacher.", "What's my share?", "They buried you. Who are you?", "(Go back to the footplate)" },
        ["dole_name"] = new[] { "And the silver in your plate?", "Stand aside.", "What's my share?" },
        ["dole_silver"] = new[] { "Stand aside.", "What's my share?" },
        ["dole_share"] = new[] { "Done.", "No.", "(Go back to the footplate)" },
        ["lockridge_after_ran"] = new[] { "Whose hand is on your inspections?", "Nothing. Good night." },
        ["lockridge_hymnal"] = new[] { "(Open the drawer)" },
        ["lockridge_stamp"] = new[] { "Keep stamping. Trains have to run.", "Sign your own name from now on.", "Pritchard gets the stamp." },
    };
    const string RulesTitle = "Rules of the Yard";
    const string RulesText = "IRON JUNCTION\nA. LOCKRIDGE, YARDMASTER\n\n1. This is a railway. Everything else is somebody's opinion.\n2. Arms are worn outside the gate or handed to the gateman.\n   The gateman has a list. Do not be on it.\n3. No car leaves this yard that has not been passed and\n   stamped by the Inspector of Way.\n4. No man, woman or child rides for nothing. Brahmin by weight.\n5. The yardmaster's office turns to face trouble.\n   If it is facing you, consider your position.\n6. Trains leave on time. If you are not aboard,\n   that was your decision.";
    const string ChalkTitle = "Chalk on a Boiler";
    const string ChalkText = "No. 212\n\nThere is power in the blood.\n\nGauge at point of failure: 4 ft 9 3/4 in.\nPassed as sound, stamped, on the 3rd inst.\nWho signed?";
    const string FlyleafTitle = "Flyleaf of a Hymnal";
    const string FlyleafText = "This book the property of\nR. OSTRANDER\nInspector of Way, Corridor Line\nIron Junction\n\nPresented by the yardmaster and hands\non the completion of ten years' service.\nMay he find us always in good order.\n\n(below, in pencil, in another hand)\n\nReuben. You were right about the trestle.\nI ran it anyway. A.";

    // Lockridge's plain gate greeting is 222 characters; with her name it is 243, over the limit every
    // displayed string is held to. It is shown as two boxes, cut between two of its own sentences, with its
    // buttons on the second.
    const string GateCut = " Tonight I send";
    static string GateA => Line["lockridge_gate"][..Line["lockridge_gate"].IndexOf(GateCut, StringComparison.Ordinal)];
    static string GateB => Line["lockridge_gate"][(Line["lockridge_gate"].IndexOf(GateCut, StringComparison.Ordinal) + 1)..];
    // With Billie dead or not there, Dole's promise that she walks home unharmed is not made: only the rest of
    // his offer, from this sentence to its end (the contract's two exact dead-Billie context projections).
    const string ShareRestStart = "The physic goes up the hill:";
    static string ShareRest => Line["dole_share"][Line["dole_share"].IndexOf(ShareRestStart, StringComparison.Ordinal)..];

    // ------------------------------------------------------------------ UI
    // This build speaking, never a character. In square brackets on the screen.
    public const string UiTravelName = "Iron Junction story test";
    public const string UiBothRoads = "Greenwater and Iron Junction are playable in this candidate; Red Hollow and the fair are not.";
    public const string UiRoadComplete = "Night Mail road complete. Greenwater remains playable; Red Hollow and the fair are not.";
    // The contract's neutral journal text, each on a stage of this build's own (never on an accepted one's number
    // except 62, whose accepted text claims a night that is not shown).
    public const string UiJob = "You agreed to ride the Night Mail with the payroll and fever medicine.";
    public const string UiBoarded = "You boarded Old Contrary. The regulator is ready.";
    public const string UiRanAlone = "The Night Mail got through. The medicine and payroll arrived; the engine is damaged.";
    public const string UiDoleDead = "Preacher Dole is dead. His death does not erase the yard's inspection records.";
    public const string UiSaleStatus = "You accepted Dole's share. The payroll and medicine were taken from the train.";
    public const string UiReturned = "The train returned with its cargo undelivered. The obstruction at Sawtooth Cut remains.";
    public const string UiSilverTold = "Dole described square-marked silver paying for pulled rails.";
    public const string UiNameTold = "Preacher Dole identified himself as Ostrander, Inspector of Way.";
    public const string UiCountersigned = "Lockridge countersigned the reviewed entries in her own name. Suspect stock is held from dispatch.";
    public const string UiStampTaken = "You took the inspector's stamp as evidence. It has not yet been delivered to Pritchard.";
    public const string UiAssigned = "Assignment accepted. Board the Night Mail.";
    public const string UiOffer = "Offer: 150 caps.";
    public const string UiObjectiveCarry = "Take the mail through, or take the train back to the yard";
    public const string UiObjectiveLeave = "Leave Iron Junction for Mercy Crossing";
    public const string UiObjectiveStamp = "Bring the inspector's stamp to Sheriff Pritchard";
    const string GoOn = "Continue";
    const string Test = "[Iron Junction story test]";
    const string Scene = "[Scene]";
    const string Greybox = "[Greybox]";

    // The limit every displayed string is held to (see docs/design/ACT1_RUNTIME_001_MAPPING.json, "limit").
    public const int Limit = 240;

    // ------------------------------------------------------------- records
    public static readonly string[] Globals =
    {
        "TLM_G_MQ02A_Outcome", "TLM_G_MQ02A_Mail", "TLM_G_MQ02A_Engine", "TLM_G_MQ02A_Train", "TLM_G_MQ02A_Dole",
        "TLM_G_MQ02A_Stamp", "TLM_G_MQ02A_StampDelivered", "TLM_G_MQ02A_YardAuthority", "TLM_G_MQ02A_Reported",
        "TLM_G_MQ02A_MailThrough", "TLM_G_MQ02A_MailSold", "TLM_G_MQ02A_LineClosed", "TLM_G_MQ02A_DoleLives",
        "TLM_G_MQ02A_SilverRail", "TLM_G_MQ02A_OstranderKnown", "TLM_G_MQ02A_LockridgeStamping",
        "TLM_G_MQ02A_LockridgeSigned", "TLM_G_MQ02A_LockridgeReported",
    };

    const string Yard = "TLM_Fac_IronJunction";
    const string BlackRail = "TLM_Fac_BlackRail";
    public static readonly string[] Factions = { Yard, BlackRail };

    const string Settler = "WorkshopNPC";
    static NpcSpec Person(string editorId, string name, string sex, string faction, bool helpsItsOwn = false) =>
        new(editorId, name, CopyFrom: Settler, KeepDefaultPackageList: false, Sex: sex, Faction: faction, StandsBy: true, HelpsItsOwn: helpsItsOwn);

    // Three canonical people and three of the Black Rail with no names of their own. Each a copy of the game's
    // settler with nothing to go about, as the first section's and Greenwater's people are. Dole is one actor
    // with one name on the screen throughout: what he is called in law is learned, in the journal.
    public static readonly NpcSpec[] Npcs =
    {
        Person("TLM_NPC_YARDMASTER_IRONJUNCTION", Lockridge, "female", Yard),
        Person("TLM_NPC_DRIVER_NIGHTMAIL", Billie, "female", Yard),
        // Dole and his people take each other's side: a fight with one is a fight with all four.
        Person("TLM_NPC_PREACHER_BLACKRAIL", Dole, "male", BlackRail, helpsItsOwn: true),
        Person("TLM_NPC_BLACKRAIL_01", "Black Rail rifle", "male", BlackRail, helpsItsOwn: true),
        Person("TLM_NPC_BLACKRAIL_02", "Black Rail rifle", "female", BlackRail, helpsItsOwn: true),
        Person("TLM_NPC_BLACKRAIL_03", "Black Rail rifle", "male", BlackRail, helpsItsOwn: true),
    };

    public static readonly BookSpec[] Books =
    {
        // Given to the player once the flyleaf on the siding has been read through.
        new(BookId, FlyleafTitle, FlyleafText, LooksLikeANote: true),
    };

    public static readonly MiscSpec[] MiscItems =
    {
        // In Lockridge's drawer until it is taken; then in the player's inventory; then in Pritchard's.
        new(StampId, "Inspector's Stamp", LooksLike: new[] { "Pencil", "Clipboard", "Folder" }),
    };

    // The cell of this plugin's own that holds the five zones.
    public static readonly OwnCellSpec[] Cells = { new(CellId, CellName) };

    // ---------------------------------------------------------------- pieces
    // One for each thing the greybox places. Where: in the cell of this plugin's own, by the cell's own
    // coordinates (x east, y north, z up, from its origin); the two Mercy pieces in the owner's exterior
    // (tools/WorldSliceBuilder/WorldStory.cs carries the same two and a test compares them) and, for the
    // development build, in the game's test room beside the first section. Who: the number
    // TLM:NightMailTalk carries. Into: the alias of TLM_MQ02A the reference is put into.
    public sealed record Piece(string Alias, string Name, string? Base, float X, float Y, float Z = 0, int Who = 0, string? Into = null,
        bool IsPerson = false, bool Protected = false, bool OnAtSetUp = true, float[]? Box = null, string? Label = null,
        string[]? LooksLike = null, string? Use = null, bool AtMercy = false);

    public const int WhoTravel = 1, WhoRules = 3, WhoLabelYard = 4, WhoLockridge = 5, WhoDrawer = 6, WhoBoard = 7, WhoHeld = 8,
        WhoExit = 9, WhoCargo = 10, WhoLabelFootplate = 11, WhoBillie = 12, WhoDepart = 13, WhoLabelCut = 14, WhoRegulator = 15,
        WhoReverser = 16, WhoLanterns = 17, WhoDole = 18, WhoRifle1 = 19, WhoRifle2 = 20, WhoRifle3 = 21, WhoBack = 22,
        WhoLabelSiding = 23, WhoHymnal = 24, WhoPlate = 25, WhoChalk = 26, WhoLabelPlatform = 27, WhoEngine = 28, WhoFall = 31;

    static readonly string[] Paper = { "Clipboard", "Folder" };
    static readonly string[] Crate = { "Fertilizer Bag", "Bag of Cement", "Wooden Crate", "Folder" };

    // Heights above the floor tiles' surface (Z 0): people and markers 16 to settle, things to use 12, as the
    // exterior's stand above its ground.
    const float Stand = 16, Use = 12;

    public static readonly Piece[] Pieces =
    {
        // ---- Mercy Crossing: the one way there, and where the road back sets the player down.
        new("MercyTravel", "the Mercy travel point", "TLM_ACTI_NM_Travel", 2950, 2640, 12, WhoTravel, OnAtSetUp: false,
            Label: UiTravelName, LooksLike: Paper, Use: "Travel", AtMercy: true),
        new("MercyReturn", "where the road from Iron Junction comes in", "XMarker", 2780, 2650, 0, AtMercy: true),

        // ---- Zone 1, floor A: Iron Junction yard.
        new("YardArrival", "the yard gate", "XMarker", 256, 160, Stand),
        new("Rules", "the rules of the yard", "TLM_ACTI_NM_Rules", 400, 60, Use, WhoRules,
            Label: "Rules of the Yard", LooksLike: Paper, Use: "Read"),
        new("LabelYard", "the yard's label", "TLM_ACTI_NM_LabelYard", 120, 60, Use, WhoLabelYard,
            Label: "Greybox: Iron Junction yard", LooksLike: Paper, Use: "Read"),
        new("Exit", "the road to Mercy from the yard", "TLM_ACTI_NM_Exit", 20, 300, Use, WhoExit, Into: "Exit",
            Label: "Road to Mercy Crossing", LooksLike: Paper, Use: "Leave"),
        new("Lockridge", Lockridge, "TLM_NPC_YARDMASTER_IRONJUNCTION", 256, 420, Stand, WhoLockridge, Into: "Lockridge", IsPerson: true, Protected: true),
        new("Drawer", "the top drawer of the yardmaster's desk", "TLM_ACTI_NM_Drawer", 120, 500, Use, WhoDrawer,
            Label: "Top Drawer of the Yardmaster's Desk", LooksLike: Crate, Use: "Open"),
        new("StampInDrawer", "the stamp, in the drawer", "TLM_ACTI_NM_StampInDrawer", 60, 500, Use, WhoDrawer,
            Label: "Inspector's Stamp (in the drawer)", LooksLike: Paper, Use: "Open"),
        new("BoardStamped", "the dispatch board, stamped", "TLM_ACTI_NM_BoardStamped", 400, 520, Use, WhoBoard,
            Label: "Dispatch Board", LooksLike: Paper, Use: "Read"),
        new("BoardSigned", "the dispatch board, countersigned", "TLM_ACTI_NM_BoardSigned", 400, 520, Use, WhoBoard, OnAtSetUp: false,
            Label: "Dispatch Board (countersigned)", LooksLike: Paper, Use: "Read"),
        new("BoardClosed", "the dispatch board, closed", "TLM_ACTI_NM_BoardClosed", 400, 520, Use, WhoBoard, OnAtSetUp: false,
            Label: "Dispatch Board (closed)", LooksLike: Paper, Use: "Read"),
        new("HeldStock", "the stock held from dispatch", "TLM_ACTI_NM_HeldStock", 560, 520, Use, WhoHeld, OnAtSetUp: false,
            Label: "Held from Dispatch", LooksLike: Crate, Use: "Look"),
        new("CargoRetained", "the cargo locked in the yard", "TLM_ACTI_NM_CargoRetained", 600, 300, Use, WhoCargo, OnAtSetUp: false,
            Label: "Mail Car (locked in the yard)", LooksLike: Crate, Use: "Look"),
        new("BillieYard", "where Billie stands when she has walked home", "XMarker", 400, 300, Stand),
        new("BillieFootplate", "where Billie stands on the footplate in the yard", "XMarker", 1040, 400, Stand),

        // ---- Zone 2, floor A: Old Contrary's footplate as it stands in the yard.
        new("LabelFootplate", "the footplate's label", "TLM_ACTI_NM_LabelFootplate", 760, 60, Use, WhoLabelFootplate,
            Label: "Greybox: Old Contrary's footplate, in the yard", LooksLike: Paper, Use: "Read"),
        new("YardFootplate", "the footplate in the yard", "XMarker", 880, 256, Stand),
        new("Billie", Billie, "TLM_NPC_DRIVER_NIGHTMAIL", 1040, 400, Stand, WhoBillie, Into: "Billie", IsPerson: true, Protected: true),
        new("Depart", "the departure control", "TLM_ACTI_NM_Depart", 1040, 120, Use, WhoDepart, Into: "Depart",
            Label: "Old Contrary: Departure", LooksLike: Crate, Use: "Use"),
        new("CargoAboard", "the cargo aboard in the yard", "TLM_ACTI_NM_CargoAboard", 760, 480, Use, WhoCargo,
            Label: "Mail Car", LooksLike: Crate, Use: "Look"),

        // ---- Zone 3, floor B: Sawtooth Cut. The footplate as it stands at the lanterns; the parley ground.
        new("CutArrival", "the footplate in the Cut", "XMarker", 3200, 256, Stand),
        new("LabelCut", "the Cut's label", "TLM_ACTI_NM_LabelCut", 3060, 60, Use, WhoLabelCut,
            Label: "Greybox: Sawtooth Cut", LooksLike: Paper, Use: "Read"),
        new("BillieCut", "where Billie stands on the footplate in the Cut", "XMarker", 3340, 400, Stand),
        new("Regulator", "the regulator", "TLM_ACTI_NM_Regulator", 3340, 120, Use, WhoRegulator, Into: "Regulator",
            Label: "Regulator", LooksLike: Crate, Use: "Use"),
        new("Reverser", "the reverser", "TLM_ACTI_NM_Reverser", 3200, 120, Use, WhoReverser,
            Label: "Reverser", LooksLike: Crate, Use: "Use"),
        new("CargoAtCut", "the cargo aboard in the Cut", "TLM_ACTI_NM_CargoAtCut", 3060, 400, Use, WhoCargo, OnAtSetUp: false,
            Label: "Mail Car", LooksLike: Crate, Use: "Look"),
        new("BackFromCut", "the track back to the yard", "TLM_ACTI_NM_BackFromCut", 2990, 256, Use, WhoBack,
            Label: "Track Back to Iron Junction", LooksLike: Paper, Use: "Walk"),
        new("BillieWalk", "where Billie is put off to walk home", "XMarker", 3000, 540, Stand),
        new("Lanterns", "the lanterns and the spread rail", "TLM_ACTI_NM_Lanterns", 3560, 256, Use, WhoLanterns,
            Label: "Lanterns Across the Track", LooksLike: Paper, Use: "Look"),
        new("Dole", Dole, "TLM_NPC_PREACHER_BLACKRAIL", 3800, 256, Stand, WhoDole, Into: "Dole", IsPerson: true),
        new("Rifle1", "one of the Black Rail", "TLM_NPC_BLACKRAIL_01", 3940, 120, Stand, WhoRifle1, Into: "Rifle1", IsPerson: true),
        new("Rifle2", "another of the Black Rail", "TLM_NPC_BLACKRAIL_02", 3940, 400, Stand, WhoRifle2, Into: "Rifle2", IsPerson: true),
        new("Rifle3", "a third of the Black Rail", "TLM_NPC_BLACKRAIL_03", 3980, 256, Stand, WhoRifle3, Into: "Rifle3", IsPerson: true),
        new("CargoSeized", "the cargo taken from the train", "TLM_ACTI_NM_CargoSeized", 3700, 500, Use, WhoCargo, OnAtSetUp: false,
            Label: "Mail Car (emptied)", LooksLike: Crate, Use: "Look"),
        // Up the hill: where the Black Rail go when Dole is dead.
        new("Retreat1", "the first retreat marker", "XMarker", 4640, 40, Stand),
        new("Retreat2", "the second retreat marker", "XMarker", 4640, 256, Stand),
        new("Retreat3", "the third retreat marker", "XMarker", 4640, 480, Stand),

        // ---- Zone 4, floor B: the boxcar tabernacle, on a dead siding.
        new("LabelSiding", "the siding's label", "TLM_ACTI_NM_LabelSiding", 4160, 60, Use, WhoLabelSiding,
            Label: "Greybox: the boxcar tabernacle", LooksLike: Paper, Use: "Read"),
        new("Hymnal", "the hymnal", "TLM_ACTI_NM_Hymnal", 4200, 520, Use, WhoHymnal,
            Label: "Hymnal", LooksLike: Paper, Use: "Read"),
        new("Plate", "the collection plate", "TLM_ACTI_NM_Plate", 4340, 520, Use, WhoPlate,
            Label: "Collection Plate", LooksLike: Crate, Use: "Look"),
        new("Chalk", "the chalked boiler", "TLM_ACTI_NM_Chalk", 4400, 120, Use, WhoChalk,
            Label: "Chalk on a Boiler", LooksLike: Paper, Use: "Read"),

        // ---- Zone 5, floor C: the valley platform.
        new("PlatformArrival", "the valley platform", "XMarker", 6272, 256, Stand),
        new("LabelPlatform", "the platform's label", "TLM_ACTI_NM_LabelPlatform", 6130, 60, Use, WhoLabelPlatform,
            Label: "Greybox: the valley platform", LooksLike: Paper, Use: "Read"),
        new("BilliePlatform", "where Billie stands at the platform", "XMarker", 6420, 400, Stand),
        new("CargoDelivered", "the cargo delivered", "TLM_ACTI_NM_CargoDelivered", 6560, 500, Use, WhoCargo, OnAtSetUp: false,
            Label: "Mail Car (unloaded at the platform)", LooksLike: Crate, Use: "Look"),
        new("EngineSound", "the engine, sound", "TLM_ACTI_NM_EngineSound", 6420, 120, Use, WhoEngine, OnAtSetUp: false,
            Label: "Old Contrary", LooksLike: Crate, Use: "Look"),
        new("EngineDamaged", "the engine, damaged", "TLM_ACTI_NM_EngineDamaged", 6420, 120, Use, WhoEngine, OnAtSetUp: false,
            Label: "Old Contrary (damaged)", LooksLike: Crate, Use: "Look"),
        new("PlatformExit", "the road to Mercy from the platform", "TLM_ACTI_NM_PlatformExit", 6700, 300, Use, WhoExit,
            Label: "Road to Mercy Crossing", LooksLike: Paper, Use: "Leave"),
        new("BackFromPlatform", "the line back to the yard", "TLM_ACTI_NM_BackFromPlatform", 6130, 480, Use, WhoBack,
            Label: "Line Back to Iron Junction", LooksLike: Paper, Use: "Walk"),

        // ---- Under all three floors: a player who steps off an edge is set back.
        new("Fall", "the box under the floors", "TLM_TRIG_NM_Fall", 3328, 256, -700, WhoFall, Box: new[] { 4400f, 1400f, 150f }),
    };

    // The three floors, by the middles of their 256-unit tiles (the game's workshop_ShackMidFloor01B, the tile the
    // exterior builder stands a cabin on), laid with their surface at Z 0. A: the yard and the footplate.
    // B: the Cut, its retreat path and the siding. C: the platform. Between the floors there is nothing.
    public const string FloorTile = "workshop_ShackMidFloor01B";
    public const float Tile = 256;
    public static readonly (string Name, float FromX, int Columns)[] Floors = { ("A", 0, 5), ("B", 3072, 7), ("C", 6144, 3) };
    public const int FloorRows = 3;

    static IEnumerable<PlacedSpec> FloorTiles() =>
        from floor in Floors
        from column in Enumerable.Range(0, floor.Columns)
        from row in Enumerable.Range(0, FloorRows)
        select new PlacedSpec($"TLM_REF_NM_Floor_{floor.Name}{column}{row}", CellId, FloorTile, "Static",
            Ahead: row * Tile, Right: floor.FromX + column * Tile, Up: 0);

    // Where the two Mercy pieces stand in the game's test room, for the development build: so far ahead of the
    // room's arrival point and so far to its right, beside Greenwater's two.
    static (float Ahead, float Right) InTestRoom(Piece p) => p.Alias switch
    {
        "MercyTravel" => (560, -60),
        "MercyReturn" => (520, -100),
        _ => throw new InvalidOperationException($"{p.Alias} is not a piece at Mercy"),
    };

    public static readonly ActivatorSpec[] Activators = Pieces.Where(p => p.Base != null && p.Base.StartsWith("TLM_"))
        .Where(p => !p.IsPerson)
        .Select(p => p.Box != null ? new ActivatorSpec(p.Base!) : new ActivatorSpec(p.Base!, p.Label, p.LooksLike, p.Use)).ToArray();

    public static readonly PlacedSpec[] Placed = Pieces.Select(p =>
    {
        var id = "TLM_REF_NM_" + p.Alias;
        // At Mercy: in the game's test room, from its arrival point. Everything else: in this plugin's own cell,
        // by the cell's own coordinates (ahead is north, right is east).
        var (cell, ahead, right) = p.AtMercy ? (Spec.TrialCell, InTestRoom(p).Ahead, InTestRoom(p).Right) : (CellId, p.Y, p.X);
        if (p.Base == "XMarker") return new PlacedSpec(id, cell, "XMarker", "Static", ahead, right, p.Z, InitiallyDisabled: true);
        if (p.Box != null) return new PlacedSpec(id, cell, p.Base!, null, ahead, right, p.Z, InitiallyDisabled: true, BoxHalfExtents: p.Box);
        return new PlacedSpec(id, cell, p.Base!, null, ahead, right, p.Z, InitiallyDisabled: true);
    }).Concat(FloorTiles()).ToArray();

    // ------------------------------------------------------------- messages
    static MessageSpec Says(string id, string who, string line, params string[] buttons) =>
        new(MessagePrefix + id, who, MercyBriefing.Spoken(who, line), Box: true,
            (buttons.Length == 0 ? new[] { GoOn } : buttons).Select(b => new ButtonSpec(b)).ToArray());

    static MessageSpec Node(string id, string who, string node) =>
        Labels.TryGetValue(node, out var labels) ? Says(id, who, Line[node], labels) : Says(id, who, Line[node]);

    /// <summary>This build speaking: a box with a bracketed heading and one or more buttons.</summary>
    static MessageSpec Ui(string id, string heading, string text, params string[] buttons) =>
        new(MessagePrefix + id, null, heading + "\n\n" + text, Box: true,
            (buttons.Length == 0 ? new[] { GoOn } : buttons).Select(b => new ButtonSpec(b)).ToArray());

    static string PageHeading(string title, int page, int of) => $"[{title}, page {page} of {of}]";

    /// <summary>A document shown page by page, cut only at its own line breaks (Greenwater.Pages).</summary>
    static IEnumerable<MessageSpec> Document(string id, string title, string text, int most)
    {
        var room = Limit - (PageHeading(title, 9, 9).Length + 2);
        var pages = Greenwater.Pages(text, room);
        if (pages.Count > most) throw new InvalidOperationException($"{title} needs {pages.Count} pages; TLM:NightMailWalk shows {most} at the most");
        for (var i = 0; i < pages.Count; i++)
            yield return Ui($"{id}Page{i + 1}", PageHeading(title, i + 1, pages.Count), pages[i]);
    }

    const string NotYet = "Not yet";
    const string NotNow = "Not now";

    public static readonly MessageSpec[] Messages = new MessageSpec[]
    {
        // ---- Augusta Lockridge.
        Node("LockridgeDefault", Lockridge, "lockridge_default"),
        Says("LockridgeGateA", Lockridge, GateA),
        Says("LockridgeGateB", Lockridge, GateB, Labels["lockridge_gate"]),
        Node("LockridgeGateAlerted", Lockridge, "lockridge_gate_alerted"),
        Node("LockridgeGateSold", Lockridge, "lockridge_gate_sold"),
        Node("LockridgeDole", Lockridge, "lockridge_dole"),
        Node("LockridgeRails", Lockridge, "lockridge_rails"),
        Node("LockridgeHired", Lockridge, "lockridge_hired"),
        Node("LockridgeAfterRan", Lockridge, "lockridge_after_ran"),
        Node("LockridgeAfterDole", Lockridge, "lockridge_after_dole"),
        Node("LockridgeAfterSold", Lockridge, "lockridge_after_sold"),
        Node("LockridgeHymnal", Lockridge, "lockridge_hymnal"),
        // Her three answers, and a way to close the drawer without giving one.
        Says("LockridgeStamp", Lockridge, Line["lockridge_stamp"], Labels["lockridge_stamp"][0], Labels["lockridge_stamp"][1], Labels["lockridge_stamp"][2], "(Close the drawer)"),
        // ---- Billie Tupper.
        Node("BillieDefault", Billie, "tarrow_default"),
        Node("BillieFootplate", Billie, "tarrow_footplate"),
        Node("BillieCutBefore", Billie, "tarrow_cut_before"),
        Node("BillieInCut", Billie, "tarrow_in_cut"),
        Node("BillieRan", Billie, "tarrow_ran"),
        Node("BillieBacked", Billie, "tarrow_backed"),
        Node("BillieWalking", Billie, "tarrow_walking"),
        // ---- Ezekiel Dole.
        Node("DoleDefault", Dole, "dole_default"),
        Node("DoleSermon", Dole, "dole_sermon"),
        Node("DoleName", Dole, "dole_name"),
        Node("DoleSilver", Dole, "dole_silver"),
        Node("DoleShare", Dole, "dole_share"),
        // Billie dead or not there: the rest of his offer only; the offer itself and its buttons follow as this build's own box.
        Says("DoleShareNoBillie", Dole, ShareRest),
        Node("DoleFace", Dole, "dole_face"),
        // ---- Owen Pritchard, at Mercy: the text only of the two post-fair lines; their condition is not imported.
        Says("ReportKnown", "Owen Pritchard", Line["pritchard_hears_rail_after_fair"], "[Report on Iron Junction]", "[Later]"),
        Says("ReportUnknown", "Owen Pritchard", Line["pritchard_hears_rail_after_fair_unknown"], "[Report on Iron Junction]", "[Later]"),

        // ---- This build: travel.
        Ui("AskTravel", Test, UiBothRoads + " It is a greybox: floors and labelled stand-ins. Travel there now?", "Travel to Iron Junction", NotNow),
        Ui("AskTravelAgain", Test, "The Night Mail road is complete. You can go back: what was settled stays settled.", "Travel to Iron Junction", NotNow),
        Ui("NoteTravelNotYet", Test, "Not yet. Deliver the marshal's dispatch to Sheriff Pritchard and hear him out first."),
        Ui("NoteTravelFailed", Test, "Iron Junction could not be reached, so no arrival is recorded. Nothing else was changed. See the script log."),
        // ---- The job and the journey.
        Ui("NoteNotAssigned", "[Old Contrary]", "The yardmaster has not given you the footplate. Speak to Augusta Lockridge at her desk."),
        Ui("AskBoard", "[Old Contrary]", "Nobody at the yard is giving out this run. The payroll and the fever medicine are aboard.", "Board the Night Mail", NotNow),
        Ui("NoteAssignedNoBillie", Test, UiAssigned),
        Ui("AskDepartScene", Scene, "The Night Mail leaves the yard for Sawtooth Cut. The eleven miles are not shown: you are set down on her footplate where she stops at the lanterns. No moving engine is simulated.", GoOn, NotYet),
        Ui("AskRejoin", Scene, "The Night Mail is standing in Sawtooth Cut. You walk the line back to her.", GoOn, NotNow),
        Ui("AskWalkToCut", Scene, "You walk the line out to Sawtooth Cut on foot. The train is not there, and no train is moved.", GoOn, NotNow),
        Ui("NoteTrainNothing", "[Old Contrary]", "There is nothing to do with her here."),
        // ---- At the lanterns.
        Ui("AskRegulator", "[Regulator]", "Nobody is at the regulator. It is a lever.", Labels["tarrow_in_cut"]),
        Ui("AskRunScene", Scene, "The run at the spread rail is shown as a staged scene: you are set down at the valley platform with what arrives. No moving engine, jump or damage is simulated.", GoOn, NotYet),
        Ui("AskReverseScene", Scene, "Old Contrary backs out of the Cut to the yard with her cargo. Shown as a staged scene: you are set down on her footplate in the yard.", GoOn, NotYet),
        Ui("AskAfterDefeat", "[Regulator]", "The line through the Cut is clear. The payroll and the fever medicine are still aboard.", "Take the mail through", "Take the train back to the yard", "(Leave the regulator)"),
        Ui("AskForwardScene", Scene, "The Night Mail goes on through the Cut to the valley. Shown as a staged scene: you are set down at the valley platform.", GoOn, NotYet),
        Ui("AskCarryBackScene", Scene, "The Night Mail goes back to the yard with her cargo. Shown as a staged scene: you are set down on her footplate in the yard.", GoOn, NotYet),
        Ui("NoteSceneFailed", Test, "That could not be shown, so nothing is recorded. Use the same control again, or one where you now stand."),
        Ui("NoteSceneStuck", Test, "That cannot be shown in this build: a piece of it is missing. Nothing is recorded. Report this to the tester."),
        Ui("NoteRunDone", Test, "The Night Mail got through. The payroll and the fever medicine are at the valley platform; Old Contrary is damaged."),
        Ui("NoteForwardDone", Test, "The payroll and the fever medicine are at the valley platform."),
        Ui("NoteBackedOut", Test, "The train is back at Iron Junction with its cargo undelivered. The obstruction at Sawtooth Cut remains."),
        Ui("NoteCarriedBack", Test, "The train is back at Iron Junction. The payroll and the fever medicine are locked in the yard, undelivered. The line through the Cut is clear."),
        Ui("NoteDefeat", Test, "Preacher Dole is dead. The Black Rail have gone up the hill and the line is clear. The payroll and the fever medicine are still aboard."),
        // ---- The share.
        Ui("AskShareOffer", "[Offer]", UiOffer, Labels["dole_share"]),
        Ui("NoteShareFailed", Test, "No share was paid and no deal was made. See the script log."),
        Ui("NoteSold", Test, "You accepted Dole's share: 150 caps. The payroll and the fever medicine were taken from the train. Billie Tupper was put off to walk home."),
        Ui("NoteSoldNoBillie", Test, "You accepted Dole's share: 150 caps. The payroll and the fever medicine were taken from the train."),
        Ui("NoteSalePending", Test, "The share is paid. The rest of the sale could not be shown, so it is not recorded yet. Use Dole, a control or the mail car again. Nothing is paid twice."),
        // ---- Evidence.
        Ui("NotePlate", "[Collection plate]", "The plate is full of silver slugs. Each is stamped with a small square mark."),
        Ui("NoteDrawer", "[Top drawer]", "The inspector's stamp is in the drawer. The pad is still wet."),
        Ui("AskStampAlone", "[Top drawer]", "Nobody at the desk answers for the stamp.", Labels["lockridge_stamp"][2], "(Close the drawer)"),
        Ui("NoteStampKept", Test, "The stamp stays in the drawer, in use. Every car is still passed in the inspector's name, and suspect stock is still dispatched."),
        Ui("AskCountersignScene", Scene, "Lockridge goes through the entries and countersigns them in her own name. Shown as a staged scene; no night passes.", GoOn, NotYet),
        Ui("NoteCountersigned", Test, UiCountersigned),
        Ui("NoteStampTaken", Test, UiStampTaken),
        Ui("NoteStampFailed", Test, "The stamp could not be taken. Nothing is recorded and nothing else is decided about it. See the script log."),
        Ui("NoteDecisionFailed", Test, "That could not be done. Nothing is recorded."),
        Ui("NoteDrawerKept", "[Top drawer]", "The stamp is in the drawer, in use."),
        Ui("NoteDrawerSigned", "[Top drawer]", "The stamp is in the drawer. Lockridge signs in her own name now."),
        Ui("NoteDrawerGone", "[Top drawer]", "The drawer is empty. You took the stamp."),
        Ui("AskShowHymnal", "[Hymnal]", "You are carrying the hymnal from the tabernacle.", "(Show her the flyleaf)", "(Not now)"),
        Ui("NoteNoDispatch", "[Iron Junction]", "Augusta Lockridge no longer dispatches trains from this yard."),
        Ui("NoteSaleStatus", Test, UiSaleStatus),
        Ui("AskBillieReport", Scene, "By this scene's clock it is the next morning. Billie Tupper has walked the eleven miles in and told the yardmaster what happened in the Cut. No game time passes.", GoOn, NotNow),
        // ---- Leaving.
        Ui("AskBackToYard", Scene, "You go back along the line to Iron Junction yard on foot. The train stays where it is.", GoOn, NotNow),
        Ui("AskLeaveResolved", "[Road to Mercy]", "Leave Iron Junction? The road is complete once you are back at Mercy Crossing.", "Leave for Mercy", "Stay"),
        Ui("AskLeaveUnresolved", "[Road to Mercy]", "The Night Mail is not settled. Leaving settles nothing; you can come back.", "Leave for Mercy", "Stay"),
        Ui("AskLeaveAgain", "[Road to Mercy]", "Leave Iron Junction?", "Leave for Mercy", "Stay"),
        Ui("NoteRoadComplete", Test, UiRoadComplete + " Sheriff Pritchard will hear what became of the Night Mail."),
        Ui("NoteLeftUnresolved", Test, "You left Iron Junction with the Night Mail unsettled. The road is still open."),
        Ui("NoteFall", Greybox, "You stepped off the greybox floor and were set back on it."),
        // ---- Labels.
        Ui("LabelYard", "[Greybox: Iron Junction yard]", "Augusta Lockridge runs the yard from her desk. The rules are on the gate; the dispatch board and her desk drawer are here. Old Contrary stands on the next part of this floor."),
        Ui("LabelFootplate", "[Greybox: Old Contrary's footplate, in the yard]", "Flat floor stands for the engine. Billie Tupper drives. The departure control is here, and the mail car behind."),
        Ui("LabelCut", "[Greybox: Sawtooth Cut]", "The footplate as it stands at the lanterns, with the regulator and the reverser. Ahead: the spread rail and Preacher Dole. The tabernacle siding is beyond him."),
        Ui("LabelSiding", "[Greybox: the boxcar tabernacle]", "Dole's chapel on a dead siding: a hymnal, a collection plate, and a boiler somebody has chalked."),
        Ui("LabelPlatform", "[Greybox: the valley platform]", "Where the Night Mail arrives if she gets through."),
        Ui("LabelLanterns", "[Sawtooth Cut]", "Lanterns across the track. The left-hand rail is spread, not gone."),
        Ui("LabelCargoAboard", "[Mail car]", "The payroll and the valley's fever medicine, aboard the Night Mail."),
        Ui("LabelCargoDelivered", "[Mail car]", "The payroll and the fever medicine, delivered."),
        Ui("LabelCargoRetained", "[Mail car]", "The payroll and the fever medicine, locked in the yard. Not delivered."),
        Ui("LabelCargoSeized", "[Mail car]", "Empty. The payroll and the fever medicine were taken up the hill."),
        Ui("LabelEngineSound", "[Old Contrary]", "At the valley platform, sound."),
        Ui("LabelEngineDamaged", "[Old Contrary]", "At the valley platform, bent and scorched from the gap."),
        Ui("LabelBoardStamped", "[Dispatch board]", "Every car is passed and stamped in the name of R. Ostrander, Inspector of Way. All stock is dispatched."),
        Ui("LabelBoardSigned", "[Dispatch board]", "Entries countersigned A. Lockridge. Suspect stock is held from dispatch."),
        Ui("LabelBoardClosed", "[Dispatch board]", "Closed by order of the sheriff of Mercy Crossing. No car is dispatched and nobody signs."),
        Ui("LabelHeldStock", "[Held stock]", "Cars held from dispatch until they are inspected."),
        // ---- The report at Mercy.
        Ui("ReportMailDelivered", "[Rail report]", "The payroll and the fever medicine reached the valley."),
        Ui("ReportMailRetained", "[Rail report]", "The payroll and the fever medicine are locked in the yard at Iron Junction, undelivered."),
        Ui("ReportMailSeized", "[Rail report]", "The payroll and the fever medicine were taken from the train by the Black Rail."),
        Ui("ReportMailAboard", "[Rail report]", "The payroll and the fever medicine are still aboard the Night Mail in Sawtooth Cut."),
        Ui("ReportRan", "[Rail report]", "The Night Mail ran the spread rail. The engine is damaged."),
        Ui("ReportDoleByYou", "[Rail report]", "You killed Preacher Dole in the Cut. His death does not erase the yard's inspection records."),
        Ui("ReportDoleDead", "[Rail report]", UiDoleDead),
        Ui("ReportSold", "[Rail report]", UiSaleStatus),
        Ui("ReportBacked", "[Rail report]", UiReturned),
        Ui("ReportKnowBoth", "[Rail report]", "You learned that square-marked silver pays for the pulled rails, and that Preacher Dole is Ostrander, Inspector of Way. Who pays is not known."),
        Ui("ReportKnowSilver", "[Rail report]", "You learned that square-marked silver pays for the pulled rails. Who pays is not known."),
        Ui("ReportKnowName", "[Rail report]", "You learned that Preacher Dole is Ostrander, Inspector of Way."),
        Ui("ReportKnowNeither", "[Rail report]", "You did not learn who Preacher Dole is or what he is paid in."),
        Ui("ReportEnd", "[Rail report]", UiRoadComplete),
        // ---- The stamp at Mercy.
        Ui("AskHandOver", "[Inspector's stamp]", "You are carrying the stamp from Lockridge's drawer.", "[Hand the stamp to Pritchard]", "[Keep it for now]"),
        Ui("NoteStampDelivered", Test, "Sheriff Pritchard has the inspector's stamp."),
        Ui("NoteHandoverFailed", Test, "The stamp was not seen to reach Sheriff Pritchard. It is not recorded delivered. Speak to him again."),
        Ui("NoteAuthorityWithdrawn", "[Iron Junction]", "By the sheriff's order the dispatch board at Iron Junction is closed. Augusta Lockridge signs and dispatches nothing. The yard has no master. This is shown at the yard."),
        Ui("NoteAuthorityVacant", "[Iron Junction]", "Augusta Lockridge is dead. The dispatch board at Iron Junction is closed and nobody signs. The yard has no master. This is shown at the yard."),
        Ui("NoteAuthorityFailed", Test, "Sheriff Pritchard has the stamp. The change at the yard could not be shown, so it is not recorded yet. Speak to him again, or use the dispatch board."),
    }.Concat(Document("Rules", RulesTitle, RulesText, 4)).Concat(Document("Chalk", ChalkTitle, ChalkText, 2)).Concat(Document("Flyleaf", FlyleafTitle, FlyleafText, 4)).ToArray();

    // ------------------------------------------------------------ the quests
    static Prop Fact(string name) => new FormProp(name, name);

    public static readonly QuestSpec Road = new(
        QuestId, QuestName, "MainQuest", 56, StartGameEnabled: false,
        Stages: new StageSpec[]
        {
            new(10, Log[10]),
            new(20, Log[20], Note: "Lockridge's assignment delivered and acknowledged, Lockridge alive"),
            new(21, UiJob, Note: "NATIVE ONLY: the job taken on at the footplate with nobody to give it"),
            new(30, Log[30], Note: "The departure confirmed with Billie alive and present to drive"),
            new(31, UiBoarded, Note: "NATIVE ONLY: the same without her"),
            new(40, Log[40], Note: "Arrival in the Cut seen"),
            new(41, Log[41], Note: "The run seen finished, Billie driving"),
            new(42, Log[42], Note: "Dole dead by the player's hand in the unsettled encounter, the Black Rail seen out of it"),
            new(43, Log[43], Note: "The sale seen finished, Billie alive and released"),
            new(44, Log[44], Note: "The reverse seen finished, Billie driving"),
            new(46, UiRanAlone, Note: "NATIVE ONLY: the run with the player at the regulator"),
            new(47, UiDoleDead, Note: "NATIVE ONLY: Dole dead otherwise"),
            new(48, UiSaleStatus, Note: "NATIVE ONLY: the sale with no living Billie released"),
            new(49, UiReturned, Note: "NATIVE ONLY: the reverse without Billie driving"),
            new(50, Log[50], Note: "The collection plate inspected"),
            new(51, UiSilverTold, Note: "NATIVE ONLY: Dole's admission delivered"),
            new(55, Log[55], Note: "The flyleaf read through"),
            new(56, UiNameTold, Note: "NATIVE ONLY: Dole named himself"),
            new(60, Log[60], Note: "The drawer opened"),
            new(61, Log[61], Note: "Keep stamping: Lockridge alive, the stamp in her drawer"),
            // The accepted text of 62 says it took her until morning; no night is shown. The contract's text.
            new(62, UiCountersigned, Note: "The countersigning scene seen finished. The accepted log is not imported"),
            new(63, Log[63], Note: "The stamp taken with a living Lockridge to watch. Custody, not delivery"),
            new(64, UiStampTaken, Note: "NATIVE ONLY: the stamp taken without her"),
            new(100, CompleteQuest: true, Note: "Left for Mercy with an outcome of the encounter recorded"),
        },
        Objectives: new ObjectiveSpec[]
        {
            new(10, Objective[10], TargetAlias: "Lockridge"),
            new(20, Objective[20], TargetAlias: "Depart"),
            new(40, Objective[40], TargetAlias: "Regulator"),
            new(55, Objective[55]),
            // This build's own directions.
            new(70, UiObjectiveCarry, TargetAlias: "Regulator"),
            new(80, UiObjectiveLeave, TargetAlias: "Exit"),
            new(90, UiObjectiveStamp),
        },
        // Filled by TLM:NightMailWalk when the player first travels. None has a flag.
        Aliases: new[] { "Lockridge", "Billie", "Dole", "Rifle1", "Rifle2", "Rifle3", "Depart", "Regulator", "Exit" }
            .Select(a => new AliasSpec(a, Fill.ScriptFilled, Note: "put in by TLM:NightMailWalk at the first travel")).ToArray(),
        Script: new ScriptBind("TLM:MQ02AQuest", new Prop[]
        {
            new FormProp("TLM_MQ01", "TLM_MQ01"),
            new FormProp("TLM_G_MQ01_Done", "TLM_G_MQ01_Done"),
            // Whoever the first section cast as Owen Pritchard. Read, and handed the stamp.
            new AliasProp("Alias_MercySheriff", "SheriffPritchard", "TLM_MQ01"),
            // The side quest's own record of how it ended. Read only: Lockridge's greeting depends on it.
            new FormProp("TLM_G_SQ01_Outcome", "TLM_G_SQ01_Outcome"),
            new FormProp("TLM_G_SQ01_YardAlerted", "TLM_G_SQ01_YardAlerted"),
            new AliasProp("Alias_Lockridge", "Lockridge"), new AliasProp("Alias_Billie", "Billie"), new AliasProp("Alias_Dole", "Dole"),
            new AliasProp("Alias_Rifle1", "Rifle1"), new AliasProp("Alias_Rifle2", "Rifle2"), new AliasProp("Alias_Rifle3", "Rifle3"),
        }.Concat(Globals.Select(Fact)).Concat(new Prop[]
        {
            new VanillaProp("Caps", "Caps001", "MiscItem"),
            new FormProp("HymnalBook", BookId),
            new FormProp("StampItem", StampId),
        }).ToArray()));

    static IEnumerable<(Piece Piece, string Into)> Casts => Pieces.Where(p => p.Into != null).Select(p => (p, p.Into!));
    static Prop Say(string id) => new FormProp("Say" + id, MessagePrefix + id);
    static Prop Plain(string id) => new FormProp(id, MessagePrefix + id);
    static Prop Mine(string alias) => new AliasProp("Alias_" + alias, alias);

    public static readonly QuestSpec Stage = new(
        StageQuestId, "The Last Meridian (Night Mail greybox: development)", "None", 30, StartGameEnabled: false,
        Stages: Array.Empty<StageSpec>(),
        Objectives: Array.Empty<ObjectiveSpec>(),
        Aliases: Pieces.Select(p => new AliasSpec(p.Alias, Fill.Placed, AllowDisabled: true, Protected: p.Protected,
            Placed: "TLM_REF_NM_" + p.Alias,
            Scripts: p.Who == 0 ? Array.Empty<ScriptBind>() : new[] { new ScriptBind("TLM:NightMailTalk", new IntProp("Who", p.Who)) })).ToArray(),
        Script: new ScriptBind("TLM:NightMailWalk", new Prop[]
        {
            new FormProp("TLM_MQ02A", QuestId),
            new FormProp("TLM_MQ01", "TLM_MQ01"),
            new FormProp("TLM_G_MQ01_Done", "TLM_G_MQ01_Done"),
            new AliasListProp("ZoneOn", Pieces.Where(p => p.OnAtSetUp && !p.AtMercy).Select(p => (StageQuestId, p.Alias)).ToArray()),
            new AliasListProp("CastFrom", Casts.Select(c => (StageQuestId, c.Piece.Alias)).ToArray()),
            new AliasListProp("CastInto", Casts.Select(c => (QuestId, c.Into)).ToArray()),
            new StringListProp("CastNames", Casts.Select(c => $"{c.Piece.Name} as {c.Into} of {QuestId}").ToArray()),
            Mine("MercyTravel"), Mine("MercyReturn"), Mine("YardArrival"), Mine("YardFootplate"), Mine("CutArrival"), Mine("PlatformArrival"),
            Mine("BillieFootplate"), Mine("BillieCut"), Mine("BilliePlatform"), Mine("BillieWalk"), Mine("BillieYard"),
            Mine("Retreat1"), Mine("Retreat2"), Mine("Retreat3"),
            Mine("Lockridge"), Mine("Billie"), Mine("Dole"), Mine("Rifle1"), Mine("Rifle2"), Mine("Rifle3"),
            Mine("CargoAboard"), Mine("CargoAtCut"), Mine("CargoDelivered"), Mine("CargoRetained"), Mine("CargoSeized"),
            Mine("EngineSound"), Mine("EngineDamaged"), Mine("Lanterns"), Mine("StampInDrawer"),
            Mine("BoardStamped"), Mine("BoardSigned"), Mine("BoardClosed"), Mine("HeldStock"),
        }.Concat(Messages.Select(m => m.EditorId[MessagePrefix.Length..]).Select(id =>
            id.StartsWith("Lockridge") || id.StartsWith("Billie") || id.StartsWith("Dole") || id is "ReportKnown" or "ReportUnknown"
                ? Say(id)
                : Plain(id))).ToArray()));
}
