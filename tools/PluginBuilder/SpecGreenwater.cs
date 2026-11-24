namespace Tlm.PluginBuilder;

// GREENWATER-STORY-001: Chapter 2's river road, "The Queen of Tellico"
// (docs/design/GREENWATER_STORY_001.md and its order). A CANDIDATE: not
// compiled, not built against the game's master, not run in the game.
//
// Two quests. TLM_MQ02B is the road: the accepted stages and objectives, the
// facts later chapters read, and TLM:MQ02BQuest, which holds every rule.
// TLM_GW is the greybox, DEVELOPMENT ONLY: the placed pieces in aliases of its
// own, the lines, and TLM:GreenwaterWalk, which shows them and works the
// pieces. The exterior builder clones TLM_GW into the owner's world, as it
// clones TLM_A1; TLM_MQ02B stays one record in this plugin.
//
// EVERY SPOKEN LINE, BUTTON, JOURNAL TEXT AND DOCUMENT IS COPIED from the
// accepted writing in assets/incoming/act1/story (as accepted at d142104): the
// constants below marked GENERATED were written out of the JSON by a script,
// not typed. Which field each record takes its text from, and what of the
// writing is deliberately not imported, is in
// docs/design/GREENWATER_STORY_001_MAPPING.json;
// tools/papyrus_sim/test_greenwater_projection.py compares the plugin as
// built with those fields, character by character. Change a line there first,
// by the writing's own process; never here.
//
// Text in square brackets is this build speaking: what is representation,
// what is not playable, what a test should write down. It is never put in a
// character's mouth.
//
// Nothing here may read a field of Spec that is not a constant (see Act1).
public static class Greenwater
{
    public const string QuestId = "TLM_MQ02B";
    public const string StageQuestId = "TLM_GW";
    public const string BookId = "TLM_BOOK_LetterOfHire";
    public const string MessagePrefix = "TLM_MSG_GW_";

    // ------------------------------------------------- the accepted writing
    // GENERATED from assets/incoming/act1/story by copying, never retyped: characters.json,
    // quests/tlm_mq02b.json, talk/tlm_mq02b.json, talk/tlm_mq02.json, documents.json.
    public const string Opal = "Opal Starnes";
    public const string Hatcher = "Lyle Hatcher";
    public const string Rafferty = "Mose Rafferty";
    public const string Belden = "Tomas Belden";
    public const string QuestName = "The Queen of Tellico";
    // The accepted journal text of each stage, by number.
    static readonly Dictionary<int, string> Log = new()
    {
        [10] = "Greenwater is a town on stilts with a queue from the cook-shed to the water. Everybody in the queue is looking at the same boat.",
        [20] = "Opal Starnes has corn for nine days and a town for ninety. Her grain is on Lyle Hatcher's boat. She wants it back, and she wants him on the steeple.",
        [30] = "The Queen of Tellico has a band, a bar and a faro bank. The stake at the high table is a cup of Greenwater's own corn.",
        [40] = "Commodore Hatcher deals without looking at his hands. He says the barge is salvage, the law is on his side, and would you care for a card.",
        [41] = "You took the barge off Lyle Hatcher with his own deck. He stood the house a round and called it the best hand he ever lost.",
        [42] = "The grain barge reached Greenwater through Hangman's Chute. Some cargo was lost in the rapids.",
        [43] = "The occupied Queen burned with the grain lashed alongside. People tried to reach the water. The cargo is lost; the crew's account still needs witnesses.",
        [44] = "You told Greenwater the barge went down in the Chute. Hatcher counted your share onto the felt, and Opal Starnes thanked you for trying.",
        [45] = "Lyle Hatcher won your gun on the turn of a card and gave it back with a bow. He says you may still buy in.",
        [50] = "There is a letter in Hatcher's strongbox. He was paid in stamped silver to hold the grain past first frost. Selling it back was his own idea.",
        [60] = "Greenwater rang the steeple bell and hanged Lyle Hatcher from the mooring ring. Opal Starnes held the ladle the whole time.",
        [61] = "Lyle Hatcher left Greenwater in irons in the bottom of a skiff, still talking.",
    };
    static readonly Dictionary<int, string> Objective = new()
    {
        [10] = "Find who keeps the stores at Greenwater",
        [20] = "Get aboard the Queen of Tellico",
        [40] = "Get the grain barge off Commodore Hatcher, or get paid",
        [50] = "(Optional) Find out why a gambler wanted a town's corn",
    };
    // talk/tlm_mq02b.json: each node's text, by node id.
    static readonly Dictionary<string, string> Line = new()
    {
        ["starnes_default"] = "Back of the line, bless you. Everybody eats or nobody does.",
        ["starnes_first"] = "Pritchard sent you? Nine days of corn here, ninety till the dogwood. That barge beside Hatcher's Queen holds our winter grain. He sells it back by the cup. Start with me, child. Know whose supper you're handling.",
        ["starnes_wants"] = "Bring the grain to this landing. I want Lyle hanged from the steeple, too. I held him at his christening; I won't pretend that makes this easy. Mose has a skiff. Getting our food back needn't mean killing him.",
        ["starnes_guns"] = "Two swivel guns on his rail. Nine men here fit to stand. A hungry man shakes before he aims. I won't spend them on a charge just so I can say I tried. Find another way to the grain.",
        ["starnes_bowl"] = "That's a quarter cup short and I know it, so don't look at it like that. Eat. You'll want it. I'd tell you I've had mine, but the Lord's listening.",
        ["starnes_stay"] = "Leave for where? Up a ridge with empty packs? These planks are home. I know every bowl by its chipped rim. If we scatter, I stop seeing who's missing. That's what frightens me more than Hatcher.",
        ["starnes_after_grain"] = "We keep counting. A full barge buys time, not another harvest. Come back when your river work is done. The relief stores take corn. I'll tell you what's short; you decide what you can spare.",
        ["pruitt_default"] = "You watch the boat. I watch the water between us. That's how I got myself into this. Ask Granny what she needs; then ask me how to reach Hatcher's barge.",
        ["pruitt_skiff"] = "Front gangway takes you to Hatcher's card table. My skiff reaches the grain barge on the Queen's far side. The third chain link is rotten. I know because... well. I know that barge.",
        ["pruitt_confess"] = "I towed it out. One dollar for safe keeping, he said. I wanted Granny to see me bring wages home. Instead I took her winter. I'll run the Chute for you. I'm scared of it. I'm going anyway.",
        ["hatcher_default"] = "Welcome to the Queen. Warm light, dry cards, nobody asking what you were before you came aboard. First drink's mine. Mind what the next one costs you.",
        ["hatcher_table"] = "Lyle Hatcher. Opal wants her barge; I call it salvage. You're standing between a hungry town and a paying house. Play for the grain, hear my offer, or leave. Nobody needs to draw yet.",
        ["hatcher_lost"] = "Well, I will be eternally... Ladies! Gentlemen! The house stands a round, for I have just been skinned by an artist. She's yours, friend, every sack. Now. Do you mean to give me to Opal? She means it this year.",
        ["hatcher_won"] = "Ah. The lady turns, and she's mine. No, no, keep your iron, I've a drawer full. You have sand, friend, and I've a use for sand. There's a quarter of that barge in it if Greenwater hears she went down in the Chute.",
        ["hatcher_share"] = "Two hundred caps to tell Opal the Chute took it. You get paid; she gets no grain. Belden's soup may help today. It won't replace a winter's stores. Still want my share?",
        ["hatcher_paid"] = "Paid? ...You've been in my box. Or you're guessing, and I've told you. Ha! Yes. Silver, square mark: hold her till first frost, then turn her loose. But a man sees that much corn and that many hungry folk and thinks: Lyle, that's a market.",
        ["pruitt_chain"] = "One cut frees the barge for the Chute. Or burn the Queen. Thirty people are aboard - crew, cooks, the fiddler - and the winter grain is still lashed alongside. Fire can take them and the cargo. Say what you're ordering.",
        ["pruitt_ran"] = "Through! Don't cheer yet. Those sacks over the side were suppers. Granny will count what we brought home. I'll stand there while she does it. I helped put us here.",
        ["pruitt_burned"] = "The cook was still aboard. The fiddler too; she taught me to waltz. We knew they were there. I can hear them in the water. Don't tell me this was only a boat.",
        ["starnes_after_won"] = "You won the barge from Hatcher? Every sack? Then we'll count it home. Now tell me what you mean to do with him. I want him on the steeple, and you know what that means.",
        ["starnes_won_hatcher_dead"] = "The grain is ours. Hatcher is dead. I can count both those facts without calling them the same kind of victory.",
        ["starnes_denied"] = "You brought the corn and spared him. I can thank your hands and hate your judgment. Get off my planks for now. The relief stores are for the town; my anger doesn't get to own those.",
        ["starnes_after_chute"] = "Some grain home. Some gone. I'll stretch what you've brought; I won't call the winter settled. Finish your river journey, then come back to the relief stores with corn. Help can be more than one brave afternoon.",
        ["starnes_after_fire"] = "I asked for the grain and one man's answer. Now the cargo's burned and people are missing. Don't give me a number you haven't counted. Bring the living to the planks. We'll need every hand.",
        ["starnes_after_share"] = "The Chute. Yes. It had my husband and it had my daughter and now it's had the corn. You tried, child. Here. It's a short cup, but you earned it.",
        ["starnes_after_hanging"] = "It's done. I thought I'd feel fed. ...Fifty years ago I put a spoon in that boy's mouth. Go on, child. There's corn. There's corn for everybody.",
        ["belden_greenwater_relief"] = "Delegate Belden. The pot is for people who need it. We can discuss an agreement after supper, and you may refuse it. This wagon won't replace a winter's grain. It can keep people fed while they decide.",
        ["belden_greenwater_relief_fire"] = "Delegate Belden. The pot is for people who need it. We can discuss an agreement after supper, and you may refuse it. This wagon won't replace a winter's grain. It can keep people fed while they decide.",
        ["pritchard_hears_river_after_fair"] = "You have a hire-payment lead for Greenwater. Tell me its source. Going there isn't the only way to hear a claim, and hearing one doesn't prove it.",
        ["pritchard_hears_river_after_fair_unknown"] = "If you haven't been to Greenwater, ask me the way. If you have, tell me what became of the grain and how you learned it.",
    };
    // Each node's button labels, in the node's order.
    static readonly Dictionary<string, string[]> Labels = new()
    {
        ["starnes_first"] = new[] { "What do you want done?", "Why not take it back yourselves?", "(Take a bowl)", "Why not leave Greenwater?" },
        ["starnes_stay"] = new[] { "And after we get the grain?", "Back" },
        ["pruitt_skiff"] = new[] { "The gangway.", "The off side.", "How do you know the barge?" },
        ["hatcher_table"] = new[] { "Deal. The barge against my gun.", "Sell me a share, Commodore.", "Who paid you to hold it?", "(Leave the table)" },
        ["hatcher_lost"] = new[] { "He's yours, Opal.", "He goes to Pritchard, alive.", "Let him keep his boat." },
        ["hatcher_won"] = new[] { "Sell me a share, Commodore.", "(Leave the table)" },
        ["hatcher_share"] = new[] { "Done.", "No." },
        ["hatcher_paid"] = new[] { "Square mark. Go on." },
        ["pruitt_chain"] = new[] { "Cut the barge loose.", "Burn the occupied Queen.", "Not yet." },
        ["starnes_after_won"] = new[] { "He's yours, Opal.", "He goes to Pritchard, alive.", "Let him keep his boat." },
    };
    const string BoardTitle = "Ration Board, Greenwater";
    const string BoardText = "GREENWATER STORES\nO. Starnes keeps the count.\n\nMeal in the bin:        9 days\nDays to the dogwood:    90\nGrown:                  1 cup, morning\nUnder twelve:           1 cup, morning. 1/2 cup, night\nNursing:                as under twelve, and ask\nSick:                   ask\n\nNobody is fed twice. Nobody is fed first.\nIf you think the count is wrong, come and count it.\n\nThe grain barge is not lost.\nEverybody can see where it is.";
    const string LetterTitle = "A Letter of Hire";
    const string LetterText = "Commodore,\n\nEnclosed, forty. Count them.\n\nYou will take the Greenwater barge under tow on the night of\nthe new moon and hold it at your anchorage. You will say it\nwas adrift. You will hold it until first frost and then let it\nbe found.\n\nYou are not asked to sink it, sell it or open a sack.\nYou are asked for a delay.\n\nForty more on release.\n\nDo not write back. Do not ask the bearer who sends this.\nThe bearer does not know.\n\n(no signature. Pressed into the wax, a small plain square.)";

    // Hatcher's admission is 239 characters; with his name it is 255, the length at which the game was seen to
    // cut a box short. It is shown as two boxes, cut between two of its own sentences.
    const string PaidCut = " But a man sees";
    static string PaidA => Line["hatcher_paid"][..Line["hatcher_paid"].IndexOf(PaidCut, StringComparison.Ordinal)];
    static string PaidB => Line["hatcher_paid"][(Line["hatcher_paid"].IndexOf(PaidCut, StringComparison.Ordinal) + 1)..];
    // With Opal dead or not there, his question about her is not put: only the approved prefix (order, item 8).
    const string LostPrefixEnd = "She's yours, friend, every sack.";
    static string LostPrefix => Line["hatcher_lost"][..(Line["hatcher_lost"].IndexOf(LostPrefixEnd, StringComparison.Ordinal) + LostPrefixEnd.Length)];

    // ------------------------------------------------------------------ UI
    // This build speaking, never a character. In square brackets on the screen.
    public const string UiTravelName = "Greenwater story test";
    // NIGHT-MAIL-STORY-001: in the composed candidate two roads are playable. The 016b source keeps the one-road wording.
    public const string UiOnlyGreenwater = "Three roads are playable. Four Flags entry is available after the first section.";
    public const string UiRoadComplete = "Greenwater road complete. The other roads and Four Flags entry remain available.";
    public const string UiShareInterim = "You accepted Hatcher's payment. The grain remains on his barge beside the Queen; Greenwater did not receive it.";
    public const string UiObjectiveReturn = "Use the barge's pilot lever and bring the grain to the landing";
    public const string UiObjectiveLeave = "Take the skiff back to Mercy Crossing";
    const string GoOn = "Continue";
    const string Silent = "(Say nothing)";
    const string Test = "[Greenwater story test]";
    const string Greybox = "[Greybox]";

    // The limit every displayed string is held to (see docs/design/ACT1_RUNTIME_001_MAPPING.json, "limit").
    public const int Limit = 240;

    // ------------------------------------------------------------- records
    public static readonly string[] Globals =
    {
        "TLM_G_MQ02B_Outcome", "TLM_G_MQ02B_Cargo", "TLM_G_MQ02B_Recovered", "TLM_G_MQ02B_Hatcher",
        "TLM_G_MQ02B_GrainHome", "TLM_G_MQ02B_GrainSold", "TLM_G_MQ02B_QueenBurned", "TLM_G_MQ02B_HatcherHanged",
        "TLM_G_MQ02B_HatcherFriend", "TLM_G_MQ02B_HatcherHunting", "TLM_G_MQ02B_SilverRiver", "TLM_G_MQ02B_Reported",
    };

    const string Town = "TLM_Fac_Greenwater";
    const string QueenCrew = "TLM_Fac_QueenCrew";
    public static readonly string[] Factions = { Town, QueenCrew };

    const string Settler = "WorkshopNPC";
    static NpcSpec Person(string editorId, string name, string sex, string faction, bool helpsItsOwn = false) =>
        new(editorId, name, CopyFrom: Settler, KeepDefaultPackageList: false, Sex: sex, Faction: faction, StandsBy: true, HelpsItsOwn: helpsItsOwn);

    // Four canonical people and two of the Queen's crew with no names of their own. Each a copy of the game's
    // settler with nothing to go about, as the first section's people are.
    public static readonly NpcSpec[] Npcs =
    {
        Person("TLM_NPC_WARDEN_GREENWATER", Opal, "female", Town),
        Person("TLM_NPC_PILOT_GREENWATER", Rafferty, "male", Town),
        Person("TLM_NPC_DELEGATE_COMMONWEALTH", Belden, "male", Town),
        // Hatcher and his crew take each other's side: a fight with one is a fight with all three.
        Person("TLM_NPC_COMMODORE_QUEEN", Hatcher, "male", QueenCrew, helpsItsOwn: true),
        Person("TLM_NPC_QUEEN_CREW_01", "Queen's crew", "male", QueenCrew, helpsItsOwn: true),
        Person("TLM_NPC_QUEEN_CREW_02", "Queen's crew", "female", QueenCrew, helpsItsOwn: true),
    };

    public static readonly BookSpec[] Books =
    {
        // Given to the player once the letter in the strongbox has been read through.
        new(BookId, LetterTitle, LetterText, LooksLikeANote: true),
    };

    // ---------------------------------------------------------------- pieces
    // One for each thing the greybox places. Where: in the owner's exterior (x, y, z), on free flat ground
    // south of the bypass road (tools/WorldSliceBuilder/WorldStory.cs carries the same table and a test
    // compares the two); in the game's test room for the development build, the same layout set down ahead
    // of the first section. Who: the number TLM:GreenwaterTalk carries. Into: the alias of TLM_MQ02B the
    // reference is put into.
    public sealed record Part(string Alias, string Name, string? Base, float X, float Y, float Z = 0, int Who = 0, string? Into = null,
        bool IsPerson = false, bool Protected = false, bool OnAtSetUp = true, float BoxHalf = 0, string? Label = null,
        string[]? LooksLike = null, string? Use = null);

    public const int WhoTravel = 1, WhoLanding = 2, WhoOpal = 3, WhoBoard = 4, WhoRafferty = 5, WhoSkiff = 6, WhoGangway = 7,
        WhoOffSide = 8, WhoHatcher = 9, WhoTable = 10, WhoStrongbox = 11, WhoChain = 12, WhoPilot = 13, WhoFire = 14,
        WhoDock = 15, WhoExit = 16, WhoBelden = 17, WhoCrew1 = 18, WhoCrew2 = 19, WhoLabelLanding = 20, WhoLabelQueen = 21,
        WhoLabelChute = 22, WhoCargo = 23, WhoSteeple = 24, WhoBurnt = 25, WhoReliefStores = 26, WhoReliefSupply = 27;

    static readonly string[] Paper = { "Clipboard", "Folder" };
    static readonly string[] Crate = { "Fertilizer Bag", "Bag of Cement", "Wooden Crate", "Folder" };

    public static readonly Part[] Parts =
    {
        // ---- Mercy Crossing: the one way there, and where the skiff sets the player down again.
        new("MercyTravel", "the Mercy travel point", "TLM_ACTI_GW_Travel", 3150, 2620, 12, WhoTravel, OnAtSetUp: false,
            Label: UiTravelName, LooksLike: Paper, Use: "Travel"),
        // Z 32, not 0: in the owner's exterior (3150, 2700) lies inside the footprint of the cabin's floor tiles
        // (x 2664 to 3432, y 2672 to 3184), whose surface the exterior builder gives as Z 16. 16 units above it,
        // to settle: the height that builder's own arrival marker uses. Not seen in the game.
        new("MercyReturn", "where the skiff from Greenwater lands", "XMarker", 3150, 2700, 32),
        // ---- The Chute: a short strip, west of the landing, ending at the return dock.
        new("ChuteStart", "the head of the Chute", "XMarker", 1300, 480),
        new("LabelChute", "the Chute's label", "TLM_ACTI_GW_LabelChute", 1380, 580, 12, WhoLabelChute,
            Label: "Greybox: Hangman's Chute", LooksLike: Paper, Use: "Read"),
        new("ReturnDock", "the return dock", "TLM_TRIG_GW_ReturnDock", 1640, 480, 100, WhoDock, BoxHalf: 80),
        // ---- The landing and the cook-shed.
        new("Exit", "the skiff to Mercy", "TLM_ACTI_GW_Exit", 1760, 380, 12, WhoExit, Into: "Exit",
            Label: "Skiff to Mercy", LooksLike: Paper, Use: "Leave"),
        new("Arrival", "where the player is set down at Greenwater", "XMarker", 1800, 300),
        new("LandingSight", "the landing", "TLM_TRIG_GW_Landing", 1900, 440, 100, WhoLanding, BoxHalf: 100),
        new("LabelLanding", "the landing's label", "TLM_ACTI_GW_LabelLanding", 1880, 580, 12, WhoLabelLanding,
            Label: "Greenwater landing - find Opal", LooksLike: Paper, Use: "Read"),
        new("CargoWhole", "the whole cargo at the landing", "TLM_ACTI_GW_CargoWhole", 1960, 650, 12, WhoCargo, OnAtSetUp: false,
            Label: "Grain barge (whole, at the landing)", LooksLike: Crate, Use: "Examine"),
        new("CargoReduced", "the reduced cargo at the landing", "TLM_ACTI_GW_CargoReduced", 2040, 650, 12, WhoCargo, OnAtSetUp: false,
            Label: "Grain barge (part of its cargo, at the landing)", LooksLike: Crate, Use: "Examine"),
        new("Steeple", "the steeple's mooring ring", "TLM_ACTI_GW_Steeple", 2000, 300, 12, WhoSteeple, Into: "Steeple",
            Label: "Greybox: steeple mooring ring", LooksLike: Paper, Use: "Read"),
        new("Opal", Opal, "TLM_NPC_WARDEN_GREENWATER", 2100, 560, 0, WhoOpal, Into: "Opal", IsPerson: true, Protected: true),
        new("RationBoard", "the ration board", "TLM_ACTI_GW_RationBoard", 2180, 620, 12, WhoBoard,
            Label: BoardTitle, LooksLike: Paper, Use: "Read"),
        new("Belden", Belden, "TLM_NPC_DELEGATE_COMMONWEALTH", 2200, 400, 0, WhoBelden, Into: "Belden", IsPerson: true, Protected: true, OnAtSetUp: false),
        new("Rafferty", Rafferty, "TLM_NPC_PILOT_GREENWATER", 2280, 360, 0, WhoRafferty, Into: "Rafferty", IsPerson: true, Protected: true),
        new("Skiff", "Rafferty's skiff", "TLM_ACTI_GW_Skiff", 2330, 300, 12, WhoSkiff,
            Label: "Rafferty's skiff (to the Queen's off side)", LooksLike: Paper, Use: "Board"),
        // ---- The Queen of Tellico: her deck, and the barge on her off side.
        new("GangwaySight", "the gangway", "TLM_TRIG_GW_Gangway", 2450, 500, 100, WhoGangway, BoxHalf: 80),
        new("LabelQueen", "the Queen's label", "TLM_ACTI_GW_LabelQueen", 2520, 600, 12, WhoLabelQueen,
            Label: "Queen gambling boat - Hatcher and crew", LooksLike: Paper, Use: "Read"),
        new("Table", "the faro table", "TLM_ACTI_GW_Table", 2600, 540, 12, WhoTable, Into: "Table",
            Label: "Hatcher's card table - grain or payment", LooksLike: new[] { "Deck of Cards", "Playing Card", "Folder" }, Use: "Sit"),
        new("Hatcher", Hatcher, "TLM_NPC_COMMODORE_QUEEN", 2650, 600, 0, WhoHatcher, Into: "Hatcher", IsPerson: true),
        new("Strongbox", "Hatcher's strongbox", "TLM_ACTI_GW_Strongbox", 2700, 520, 12, WhoStrongbox, Into: "Strongbox",
            Label: "Hatcher's strongbox", LooksLike: new[] { "Toolbox", "Cigar Box", "Folder" }, Use: "Open"),
        new("Crew1", "one of the Queen's crew", "TLM_NPC_QUEEN_CREW_01", 2560, 660, 0, WhoCrew1, Into: "Crew1", IsPerson: true),
        new("Crew2", "another of the Queen's crew", "TLM_NPC_QUEEN_CREW_02", 2740, 660, 0, WhoCrew2, Into: "Crew2", IsPerson: true),
        new("FireControl", "the boiler firebox", "TLM_ACTI_GW_FireControl", 2760, 440, 12, WhoFire,
            Label: "Boiler firebox", LooksLike: new[] { "Hot Plate", "Oil Can", "Folder" }, Use: "Light"),
        new("Burnt", "the burned Queen's marker", "TLM_ACTI_GW_Burnt", 2620, 440, 12, WhoBurnt, OnAtSetUp: false,
            Label: "Greybox: the Queen, burned", LooksLike: Paper, Use: "Read"),
        new("OffSideArrival", "where the skiff sets the player down by the barge", "XMarker", 2560, 230),
        new("OffSideSight", "the off side", "TLM_TRIG_GW_OffSide", 2620, 370, 100, WhoOffSide, BoxHalf: 70),
        new("CargoLashed", "the cargo lashed to the Queen", "TLM_ACTI_GW_CargoLashed", 2680, 300, 12, WhoCargo,
            Label: "Opal's grain barge - tied to the Queen", LooksLike: Crate, Use: "Examine"),
        new("Chain", "the anchor chain", "TLM_ACTI_GW_Chain", 2740, 300, 12, WhoChain,
            Label: "Grain barge lashing - inspect choices", LooksLike: new[] { "Chain", "Adjustable Wrench", "Wrench", "Folder" }, Use: "Examine"),
        new("Pilot", "the barge's pilot lever", "TLM_ACTI_GW_Pilot", 2790, 340, 12, WhoPilot, Into: "Pilot",
            Label: "Grain barge pilot - move freed cargo", LooksLike: new[] { "Connecting Rod", "Wrench", "Folder" }, Use: "Take"),
        // Own new IDs/aliases appended. Exterior refs are allocated only after
        // all accepted scenery; no old reference is moved or renumbered.
        new("ReliefStores", "current relief stores", "TLM_ACTI_GW_ReliefStores", 2180, 850, 12, WhoReliefStores, OnAtSetUp: false,
            Label: "Greenwater winter relief - stores", LooksLike: Paper, Use: "Inspect"),
        new("ReliefSupply", "Mercy relief food supply", "TLM_ACTI_Mercy_ReliefSupply", 3050, 3620, 12, WhoReliefSupply, OnAtSetUp: false,
            Label: "Greenwater relief food - 10 Corn for 20 caps", LooksLike: Paper, Use: "Inspect"),
    };

    // The development build sets the same layout down in the game's test room: so many units ahead of the
    // arrival point and to its right. Mercy's two pieces stand by the first section's Pritchard there.
    static (float Ahead, float Right) InTestRoom(Part p) => p.Alias switch
    {
        "MercyTravel" => (560, 60),
        "MercyReturn" => (520, 100),
        "ReliefSupply" => (660, 180),
        _ => (p.X - 1250 + 1400, p.Y - 480),
    };

    public static readonly ActivatorSpec[] Activators = Parts.Where(p => p.Base != null && p.Base.StartsWith("TLM_"))
        .Where(p => !p.IsPerson)
        .Select(p => p.BoxHalf > 0 ? new ActivatorSpec(p.Base!) : new ActivatorSpec(p.Base!, p.Label, p.LooksLike, p.Use)).ToArray();

    public static readonly PlacedSpec[] Placed = Parts.Select(p =>
    {
        var (ahead, right) = InTestRoom(p);
        var id = "TLM_REF_GW_" + p.Alias;
        if (p.Base == "XMarker") return new PlacedSpec(id, Spec.TrialCell, "XMarker", "Static", ahead, right, p.Z, InitiallyDisabled: true);
        if (p.BoxHalf > 0)
            return new PlacedSpec(id, Spec.TrialCell, p.Base!, null, ahead, right, p.Z, InitiallyDisabled: true,
                BoxHalfExtents: new[] { p.BoxHalf, p.BoxHalf, 100f });
        return new PlacedSpec(id, Spec.TrialCell, p.Base!, null, ahead, right, p.Z, InitiallyDisabled: true);
    }).ToArray();

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

    /// <summary>
    /// A document shown page by page. It is cut only at its own line breaks, a blank line for preference;
    /// what stands on the pages, put together with the line breaks they were cut at, is the document.
    /// </summary>
    public static List<string> Pages(string text, int room)
    {
        var pages = new List<string>();
        var rest = text;
        while (rest.Length > room)
        {
            var cut = rest.LastIndexOf("\n\n", room, StringComparison.Ordinal);
            if (cut <= 0) cut = rest.LastIndexOf('\n', room);
            if (cut <= 0) throw new InvalidOperationException("a document has a line longer than a page");
            pages.Add(rest[..cut]);
            rest = rest[cut..].TrimStart('\n');
        }
        pages.Add(rest);
        return pages;
    }

    static string PageHeading(string title, int page, int of) => $"[{title}, page {page} of {of}]";

    static IEnumerable<MessageSpec> Document(string id, string title, string text)
    {
        // Room for the heading, which is at its longest on any page of a document of up to nine.
        var room = Limit - (PageHeading(title, 9, 9).Length + 2);
        var pages = Pages(text, room);
        if (pages.Count > 4) throw new InvalidOperationException($"{title} needs {pages.Count} pages; TLM:GreenwaterWalk shows four at the most");
        for (var i = 0; i < pages.Count; i++)
            yield return Ui($"{id}Page{i + 1}", PageHeading(title, i + 1, pages.Count), pages[i]);
    }

    public static readonly MessageSpec[] Messages = new MessageSpec[]
    {
        // ---- Opal Starnes.
        Node("OpalDefault", Opal, "starnes_default"),
        Node("OpalFirst", Opal, "starnes_first"),
        Node("OpalWants", Opal, "starnes_wants"),
        Node("OpalStay", Opal, "starnes_stay"),
        Node("OpalAfterGrain", Opal, "starnes_after_grain"),
        Node("OpalGuns", Opal, "starnes_guns"),
        Node("OpalBowl", Opal, "starnes_bowl"),
        Node("OpalAfterWon", Opal, "starnes_after_won"),
        // With no Pritchard alive and there to take a prisoner, that button is not offered.
        Says("OpalAfterWonNoSheriff", Opal, Line["starnes_after_won"], Labels["starnes_after_won"][0], Labels["starnes_after_won"][2]),
        Node("OpalWonHatcherDead", Opal, "starnes_won_hatcher_dead"),
        Node("OpalDenied", Opal, "starnes_denied"),
        Node("OpalAfterChute", Opal, "starnes_after_chute"),
        Node("OpalAfterFire", Opal, "starnes_after_fire"),
        Node("OpalAfterShare", Opal, "starnes_after_share"),
        Node("OpalAfterHanging", Opal, "starnes_after_hanging"),
        // ---- Mose Rafferty.
        Node("RaffertyDefault", Rafferty, "pruitt_default"),
        Node("RaffertySkiff", Rafferty, "pruitt_skiff"),
        Node("RaffertyConfess", Rafferty, "pruitt_confess"),
        Node("RaffertyChain", Rafferty, "pruitt_chain"),
        Node("RaffertyRan", Rafferty, "pruitt_ran"),
        Node("RaffertyBurned", Rafferty, "pruitt_burned"),
        // ---- Lyle Hatcher.
        Node("HatcherDefault", Hatcher, "hatcher_default"),
        Node("HatcherTable", Hatcher, "hatcher_table"),
        // With no share to be had, no button offers one.
        Says("HatcherTableNoShare", Hatcher, Line["hatcher_table"], Labels["hatcher_table"][0], Labels["hatcher_table"][2], Labels["hatcher_table"][3]),
        Node("HatcherLost", Hatcher, "hatcher_lost"),
        Says("HatcherLostNoSheriff", Hatcher, Line["hatcher_lost"], Labels["hatcher_lost"][0], Labels["hatcher_lost"][2], Silent),
        // Opal dead or not there: the approved prefix only, and nobody is offered her.
        Says("HatcherLostNoOpal", Hatcher, LostPrefix, Labels["hatcher_lost"][1], Labels["hatcher_lost"][2], Silent),
        Says("HatcherLostAlone", Hatcher, LostPrefix, Labels["hatcher_lost"][2], Silent),
        Node("HatcherWon", Hatcher, "hatcher_won"),
        Says("HatcherWonNoShare", Hatcher, Line["hatcher_won"], Labels["hatcher_won"][1]),
        Node("HatcherShare", Hatcher, "hatcher_share"),
        Says("HatcherPaidA", Hatcher, PaidA),
        Says("HatcherPaidB", Hatcher, PaidB, Labels["hatcher_paid"][0]),
        // ---- Tomas Belden. One record for the writing's two nodes, whose text is the same.
        Node("BeldenRelief", Belden, "belden_greenwater_relief"),
        // ---- Owen Pritchard, at Mercy: the text only of the two post-fair nodes; their condition is not imported.
        Says("ReportKnown", "Owen Pritchard", Line["pritchard_hears_river_after_fair"], "[Report on Greenwater]", "[Later]"),
        Says("ReportUnknown", "Owen Pritchard", Line["pritchard_hears_river_after_fair_unknown"], "[Report on Greenwater]", "[Later]"),

        // ---- This build speaking.
        Ui("ArrivalBrief", "[Greenwater: your task]", "Opal Starnes needs the town's winter grain back. Find her at the landing. Hatcher holds the grain barge beside the Queen, his occupied gambling boat. The Queen is NOT the grain barge. Signs identify both areas.", "Find Opal at the landing"),
        Ui("Goal", "[Your choices concern the grain]", "Opal needs the grain beside the Queen. The card table is on the occupied boat; the separate barge is by chain and pilot lever. Taking Hatcher's money leaves the grain with him. This note chooses no route."),
        Ui("Stakes", "[Who is affected]", "Greenwater needs grain for winter. Hatcher's payment helps you; he keeps the grain. The Chute risks cargo loss. Burning the Queen endangers people and grain. Hatcher's fate is a separate decision if you win.", "I understand the stakes"),
        Ui("ConfirmShare", "[Accept Hatcher's deal?]", "Receive 200 caps and leave the grain aboard Hatcher's barge. This settles your cargo choice; Greenwater does not get its grain back through this deal. Telling Opal a false story remains a separate choice.", "Accept 200 caps; leave the grain", "Cancel; make no deal"),
        Ui("NoteSharePaid", "[Hatcher's payment]", "200 caps received. The grain remains with Hatcher. You have not told Opal anything yet."),
        Ui("LabelShareHeld", "[Greenwater grain: Hatcher retained it]", "You accepted Hatcher's payment. Greenwater did not receive the grain through that deal; the original barge remains beside the Queen."),
        Ui("LabelLandingLayout", "[Greenwater landing]", "The food stores and Mercy return point are here. The Queen is Hatcher's gambling boat; its separate grain-barge area is beside the chain and pilot lever. These are staged areas, not moving boats."),
        Ui("CardStakes", "[Play for the grain barge?]", "The stake is the grain barge. Winning gives you a chance to bring Greenwater's winter food home; delivery still requires the pilot lever and return dock. A lost hand is not a death sentence or an automatic deal.", "Play the hand", "Cancel"),
        Ui("ConfirmHang", "[Give Hatcher to Opal?]", "This hands the living Hatcher over for hanging at the steeple. It is an execution decision, separate from bringing the grain home.", "Confirm hanging", "Cancel"),
        Ui("ConfirmCustody", "[Deliver Hatcher alive?]", "Place the living Hatcher in Sheriff Pritchard's custody. This is a living-prisoner transfer, separate from the grain.", "Confirm living custody", "Cancel"),
        Ui("ConfirmRelease", "[Release Hatcher?]", "Let the living Hatcher keep his boat. This releases him; it does not promise future friendliness or change the grain's location.", "Confirm release", "Cancel"),
        Ui("AskTravel", Test, UiOnlyGreenwater + " It is a greybox: flat ground and labelled stand-ins. Travel there now?", "Travel to Greenwater", "Not now"),
        Ui("AskTravelAgain", Test, "The Greenwater road is complete. You can go back: what was settled stays settled.", "Travel to Greenwater", "Not now"),
        Ui("NoteTravelNotYet", Test, "Not yet. Deliver the marshal's dispatch to Sheriff Pritchard and hear him out first."),
        Ui("NoteTravelFailed", Test, "Greenwater could not be set up. Nothing was changed. See the script log."),
        // The occupancy warning when Rafferty cannot say it: his line's own words, as this build's text, and its own three buttons.
        Ui("AskChain", "[Anchor chain]", Line["pruitt_chain"], Labels["pruitt_chain"]),
        Ui("NoteChainCut", "[Anchor chain]", "The chain is cut. From here there are no cards, no share and no fire: use the barge's pilot lever to run the Chute."),
        Ui("NoteChainNothing", Test, "There is nothing more to do here."),
        Ui("NoteFireNotWarned", "[Boiler firebox]", "Not yet. Find out who and what is aboard first: the anchor chain, where the barge is lashed."),
        Ui("NoteFireWarned", Test, "Nothing is burning. The order is given at the boiler firebox on the Queen's deck, and cannot be taken back."),
        Ui("AskFire", "[Burn the occupied Queen?]", "Thirty people are aboard the Queen, and Greenwater's grain is tied beside it. Fire endangers them and destroys the cargo. This cannot be undone.", Labels["pruitt_chain"][1], Labels["pruitt_chain"][2]),
        Ui("NoteFireScene", Greybox, "The occupied Queen burns with the grain lashed alongside. The fire is shown by the marker on her deck. People were endangered; this build has not established an exact death toll."),
        Ui("NoteFireFailed", Test, "The fire could not be shown, so nothing is recorded. Use the firebox again."),
        Ui("NoteFireNoMarker", Test, "The fire cannot be shown in this build: its marker is missing. No order was given and nothing is changed. Report this to the tester."),
        Ui("NoteFireStuck", Test, "The fire was ordered and cannot be shown: a piece of this build is missing or cannot be switched on. Nothing is recorded and no other course is open. Report this to the tester."),
        Ui("NoteCargoFailed", Test, "The cargo could not be shown at the landing, so nothing is recorded. Use the barge's pilot lever again, then walk to the return dock."),
        Ui("NoteCargoStuck", Test, "The cargo cannot be shown at the landing: a piece of this build is missing. Nothing is recorded. Report this to the tester."),
        Ui("NotePilotNothing", "[Barge pilot lever]", "The barge is still lashed to the Queen."),
        Ui("NoteChuteScene", Greybox, "Hangman's Chute is a short walk in this build. Walk to the return dock: the run counts when you reach it."),
        Ui("NoteTowScene", Greybox, "The barge you won is brought round to the landing. Walk to the return dock: the grain is home when you reach it."),
        Ui("NoteSkiffScene", Greybox, "Rafferty's skiff sets you down at the Queen's off side, by the barge. Walk aboard from there."),
        Ui("NoteHomeWhole", Test, "The whole barge is at the landing: 12 of 12 measures. The count is this build's bookkeeping."),
        Ui("NoteHomePiloted", Test, "Part of the cargo came through the Chute: 8 of 12 measures. The count is this build's bookkeeping."),
        Ui("NoteHomeAlone", Test, "Part of the cargo came through the Chute: 6 of 12 measures. The count is this build's bookkeeping."),
        Ui("AskLie", "[Lie to Opal?]", "The grain is still aboard Hatcher's barge. Tell Opal it was lost in the Chute instead?", "[Lie] Say the Chute took it", "Do not tell that story"),
        Ui("NoteShareFailed", Test, "No share was paid and no deal was made. See the script log."),
        Ui("NoteTableEmpty", "[Faro table]", "Nobody is dealing here."),
        Ui("NoteHatcherCustody", Test, "Lyle Hatcher is in Sheriff Pritchard's custody."),
        Ui("NoteNoMeal", Test, "No food item is built into this candidate. Nothing was given."),
        Ui("NoteJudgmentFailed", Test, "That could not be carried out. Nothing is recorded."),
        Ui("AskLeaveResolved", "[Skiff to Mercy]", "Leave Greenwater? The road is complete once you are back at Mercy Crossing.", "Leave for Mercy", "Stay"),
        Ui("AskLeaveUnresolved", "[Skiff to Mercy]", "Nothing is settled at Greenwater. Leaving settles nothing; you can come back.", "Leave for Mercy", "Stay"),
        Ui("AskLeaveAgain", "[Skiff to Mercy]", "Leave Greenwater?", "Leave for Mercy", "Stay"),
        Ui("NoteRoadComplete", Test, "The Greenwater road is complete. Sheriff Pritchard will hear what became of the grain."),
        Ui("NoteLeftUnresolved", Test, "You left Greenwater with nothing settled. The road is still open."),
        Ui("ReportWhole", "[River report]", "The whole grain barge reached Greenwater."),
        Ui("ReportReduced", "[River report]", "Part of the grain reached Greenwater through Hangman's Chute."),
        Ui("ReportDestroyed", "[River report]", "The occupied Queen burned with the grain lashed alongside. None of it was recovered."),
        Ui("ReportSold", "[River report]", UiShareInterim),
        Ui("ReportEndKnown", "[River report]", "You learned that Hatcher was paid in stamped silver to hold the grain. Who paid is not known.\n\n" + UiRoadComplete),
        Ui("ReportEndUnknown", "[River report]", "You did not learn why Hatcher held the grain.\n\n" + UiRoadComplete),
        Ui("LabelLanding", "[Greenwater landing]", "Opal Starnes keeps the food stores here. Her winter grain is held beside Hatcher's Queen, not at this landing. Speak to Opal, then to Mose Rafferty about reaching the boats. The Mercy return point is nearby."),
        Ui("LabelQueen", "[Queen of Tellico - occupied boat]", "This area stands for Hatcher's gambling boat: the card table, strongbox and firebox. The separate grain barge is off this deck, beside the chain and pilot lever. Fire threatens both people and grain."),
        Ui("LabelChute", "[Greybox: Hangman's Chute]", "A short strip stands for the fast water. The return dock is at its end."),
        Ui("LabelSteeple", "[Greybox: the steeple's mooring ring]", "The steeple stands out of the lake here. Boats tie up to its ring."),
        Ui("LabelBurnt", "[Greybox: the Queen, burned]", "This marker stands for the burned boat."),
        Ui("LabelCargoLashed", "[Grain barge - separate cargo boat]", "These crates stand for Greenwater's winter grain aboard the barge tied beside the Queen. This is the cargo Opal needs. It is separate from Hatcher's occupied gambling boat."),
        Ui("LabelCargoWhole", "[Original grain delivery]", "The whole barge reached the landing: 12 of 12 measures. This is cargo history. Complete the river journey, then inspect current reserves at the separate winter-relief stores."),
        Ui("LabelCargoPiloted", "[Original grain delivery]", "Part of the cargo reached the landing: 8 of 12 measures. This is cargo history. Complete the river journey, then inspect current reserves at the separate winter-relief stores."),
        Ui("LabelCargoAlone", "[Original grain delivery]", "Part of the cargo reached the landing: 6 of 12 measures. This is cargo history. Complete the river journey, then inspect current reserves at the separate winter-relief stores."),
    }.Concat(Document("Board", BoardTitle, BoardText)).Concat(Document("Letter", LetterTitle, LetterText)).ToArray();

    // ------------------------------------------------------------ the quests
    static Prop Fact(string name) => new FormProp(name, name);

    public static readonly QuestSpec Road = new(
        QuestId, QuestName, "MainQuest", 55, StartGameEnabled: false,
        Stages: new StageSpec[]
        {
            new(10, Log[10]),
            new(20, Log[20]),
            new(30, Log[30]),
            new(40, Log[40]),
            new(41, Log[41], Note: "Card win. The barge is yielded, not delivered"),
            new(42, Log[42], Note: "The Chute was run to the return dock"),
            new(43, Log[43], Note: "The fire was ordered at the fire control and staged"),
            // The accepted text of 44 speaks of Opal's thanks, which payment does not earn: it is on 46.
            new(44, UiShareInterim, Note: "The share was paid. Interim text; the accepted text of this stage is on 46"),
            new(45, Log[45], Note: "Card loss. Not a resolution"),
            new(46, Log[44], Note: "NATIVE ONLY: the lie was told and Opal's answer heard. Carries the accepted text of 44"),
            new(50, Log[50], Note: "The letter was read through, or the admission heard to its end"),
            new(60, Log[60]),
            new(61, Log[61]),
            new(100, CompleteQuest: true, Note: "Left Greenwater with one course carried through"),
        },
        Objectives: new ObjectiveSpec[]
        {
            new(10, Objective[10], TargetAlias: "Opal"),
            new(20, Objective[20], TargetAlias: "Table"),
            new(40, Objective[40], TargetAlias: "Table"),
            new(50, Objective[50], TargetAlias: "Strongbox"),
            // This build's own directions.
            new(60, UiObjectiveReturn, TargetAlias: "Pilot"),
            new(80, UiObjectiveLeave, TargetAlias: "Exit"),
        },
        // Filled by TLM:GreenwaterWalk when the player first travels. None has a flag.
        Aliases: new[] { "Opal", "Hatcher", "Rafferty", "Belden", "Crew1", "Crew2", "Steeple", "Table", "Strongbox", "Pilot", "Exit" }
            .Select(a => new AliasSpec(a, Fill.ScriptFilled, Note: "put in by TLM:GreenwaterWalk at the first travel")).ToArray(),
        Script: new ScriptBind("TLM:MQ02BQuest", new Prop[]
        {
            new FormProp("TLM_MQ01", "TLM_MQ01"),
            new FormProp("TLM_G_MQ01_Done", "TLM_G_MQ01_Done"),
            // Whoever the first section cast as Owen Pritchard. Read only.
            new AliasProp("Alias_MercySheriff", "SheriffPritchard", "TLM_MQ01"),
            new AliasProp("Alias_Opal", "Opal"), new AliasProp("Alias_Hatcher", "Hatcher"), new AliasProp("Alias_Rafferty", "Rafferty"),
            new AliasProp("Alias_Belden", "Belden"), new AliasProp("Alias_Crew1", "Crew1"), new AliasProp("Alias_Crew2", "Crew2"),
            new AliasProp("Alias_Steeple", "Steeple"),
        }.Concat(Globals.Select(Fact)).Concat(new Prop[]
        {
            new VanillaProp("Caps", "Caps001", "MiscItem"),
            new VanillaProp("Charisma", "Charisma", "ActorValue"),
            // A food item of the game's, by the name a player sees. None of them found: no meal is given, and the script says so.
            new VanillaNamedProp("Meal", "Ingestible", "Corn", "Vegetable Soup", "Noodle Cup", "Tato", "Mutfruit"),
            new FormProp("HireLetter", BookId),
        }).ToArray()));

    static IEnumerable<(Part Part, string Into)> Casts => Parts.Where(p => p.Into != null).Select(p => (p, p.Into!));
    static Prop Say(string id) => new FormProp("Say" + id, MessagePrefix + id);
    static Prop Plain(string id) => new FormProp(id, MessagePrefix + id);
    static Prop Mine(string alias) => new AliasProp("Alias_" + alias, alias);

    public static readonly QuestSpec Stage = new(
        StageQuestId, "The Last Meridian (Greenwater greybox: development)", "None", 30, StartGameEnabled: false,
        Stages: Array.Empty<StageSpec>(),
        Objectives: Array.Empty<ObjectiveSpec>(),
        Aliases: Parts.Select(p => new AliasSpec(p.Alias, Fill.Placed, AllowDisabled: true, Protected: p.Protected,
            Placed: "TLM_REF_GW_" + p.Alias,
            Scripts: p.Who == 0 ? Array.Empty<ScriptBind>() : new[] { new ScriptBind("TLM:GreenwaterTalk", new IntProp("Who", p.Who)) })).ToArray(),
        Script: new ScriptBind("TLM:GreenwaterWalk", new Prop[]
        {
            new FormProp("TLM_Relief", GreenwaterRelief.QuestId),
            new FormProp("TLM_FourFlags", FourFlags.QuestId),
            new FormProp("TLM_MQ02B", QuestId),
            new FormProp("TLM_MQ01", "TLM_MQ01"),
            new FormProp("TLM_G_MQ01_Done", "TLM_G_MQ01_Done"),
            new AliasListProp("ZoneOn", Parts.Where(p => p.OnAtSetUp).Select(p => (StageQuestId, p.Alias)).ToArray()),
            new AliasListProp("CastFrom", Casts.Select(c => (StageQuestId, c.Part.Alias)).ToArray()),
            new AliasListProp("CastInto", Casts.Select(c => (QuestId, c.Into)).ToArray()),
            new StringListProp("CastNames", Casts.Select(c => $"{c.Part.Name} as {c.Into} of {QuestId}").ToArray()),
            Mine("MercyTravel"), Mine("MercyReturn"), Mine("Arrival"), Mine("OffSideArrival"), Mine("ChuteStart"),
            Mine("Opal"), Mine("Hatcher"), Mine("Rafferty"), Mine("Belden"), Mine("Crew1"), Mine("Crew2"),
            Mine("CargoLashed"), Mine("CargoWhole"), Mine("CargoReduced"), Mine("Table"), Mine("Chain"), Mine("Pilot"),
            Mine("FireControl"), Mine("Burnt"),
            Mine("ReliefStores"), Mine("ReliefSupply"),
        }.Concat(Messages.Select(m => m.EditorId[MessagePrefix.Length..]).Select(id =>
            id.StartsWith("Opal") || id.StartsWith("Rafferty") || id.StartsWith("Hatcher") || id.StartsWith("Belden")
                ? Say(id)
                : id is "ReportKnown" or "ReportUnknown" ? Say(id) : Plain(id))).ToArray()));
}
