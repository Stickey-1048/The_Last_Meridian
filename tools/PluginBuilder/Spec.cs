namespace Tlm.PluginBuilder;

// Declarative description of the plugin's data records.
//
// This file is the single source for stage numbers, log text, objectives,
// aliases and script bindings. It mirrors docs/design (v0.2 amendments) and
// tools/logic_model. Player-facing text here is PROVISIONAL until the owner
// approves it; names follow docs/naming-registry.md and the provisional
// minor names in the MQ01 design (section 5.2).

public enum Fill
{
    // Filled later on the game machine (needs a placed reference or a vanilla
    // record). Until then the alias is flagged Optional so the quest can start.
    Pending,
    // Create Reference to Object, "in" another alias of the same quest.
    CreateIn,
    // Never filled by data; a script forces a reference in.
    ScriptFilled,
    // The player reference, resolved from Fallout4.esm by EditorID.
    Player,
    // A reference this plugin itself places in a cell of the game
    // (Spec.Placed). Without Fallout4.esm there is no cell to place it in,
    // and the alias stays Optional.
    Placed,
}

public sealed record ScriptBind(string Script, params Prop[] Props);

public abstract record Prop(string Name);
public sealed record IntProp(string Name, int Value) : Prop(Name);
public sealed record IntListProp(string Name, params int[] Values) : Prop(Name);
public sealed record BoolProp(string Name, bool Value) : Prop(Name);
// A record in this plugin, by EditorID.
public sealed record FormProp(string Name, string EditorId) : Prop(Name);
// An alias on the owning quest, by alias name.
public sealed record AliasProp(string Name, string Alias) : Prop(Name);
// A record in Fallout4.esm, by EditorID. Skipped (and reported) in skeleton mode.
// Kind names the record type to look in (see Builder.TypedLookups); null tries them all.
public sealed record VanillaProp(string Name, string EditorId, string? Kind = null) : Prop(Name);

public sealed record AliasSpec(
    string Name,
    Fill Fill = Fill.Pending,
    bool QuestObject = false,
    bool Essential = false,
    bool Protected = false,
    bool AllowDead = false,
    bool AllowDisabled = false,
    string? CreateItem = null,      // EditorID of the item, for Fill.CreateIn
    string? CreateInAlias = null,   // alias name, for Fill.CreateIn
    bool IsLocation = false,
    string? Note = null,
    string? Placed = null,          // EditorID of the placed reference, for Fill.Placed
    string? DisplayName = null,     // EditorID of a message whose title the reference is shown under
    params ScriptBind[] Scripts);

public sealed record StageSpec(int Index, string? Log = null, bool CompleteQuest = false, string? Note = null);

public sealed record ObjectiveSpec(int Index, string Text, string? TargetAlias = null);

public sealed record QuestSpec(
    string EditorId,
    string Name,
    string Type,                    // MainQuest | SideQuests | None
    byte Priority,
    bool StartGameEnabled,
    StageSpec[] Stages,
    ObjectiveSpec[] Objectives,
    AliasSpec[] Aliases,
    ScriptBind? Script,
    // Further scripts on the same quest (development helpers and the like).
    ScriptBind[]? ExtraScripts = null)
{
    public IEnumerable<ScriptBind> AllScripts()
    {
        if (Script != null) yield return Script;
        foreach (var s in ExtraScripts ?? Array.Empty<ScriptBind>()) yield return s;
    }
}

public sealed record ButtonSpec(string Text, params Cond[] Conditions);

// Condition on a message button. All conditions on a button are ANDed.
public abstract record Cond;
public sealed record StageDone(string Quest, int Stage, bool Done = true) : Cond;
public sealed record GlobalAtLeast(string Global, float Value) : Cond;
public sealed record GlobalEquals(string Global, float Value) : Cond;

public sealed record MessageSpec(string EditorId, string? Title, string Text, bool Box, params ButtonSpec[] Buttons);

public sealed record BookSpec(string EditorId, string Name, string Text);

/// <param name="ModelFrom">EditorID of an item in Fallout4.esm whose world model and bounds this item borrows.
/// Only the path is copied, into the plugin as built; no file of the game's is. Null: no world model.</param>
public sealed record MiscSpec(string EditorId, string Name, string? ModelFrom = null);

// An activator with no model. Placed with a box around it, it is a trigger.
public sealed record ActivatorSpec(string EditorId);

/// <summary>
/// A reference this plugin places in a cell of the game. Where it goes is given
/// from the cell's arrival marker (the spot where the console command "coc"
/// puts the player, and the way the player then faces), which the builder
/// reads from the cell itself: so many units ahead of it, to its right, and up.
/// </summary>
/// <param name="Base">EditorID of what is placed.</param>
/// <param name="VanillaKind">Null: Base is a record of this plugin. Otherwise the kind of game record to look Base up as;
/// if the game has no such record the reference is left out and reported.</param>
/// <param name="BoxHalfExtents">For a trigger: half the size of the box, in game units, on each axis.</param>
/// <param name="CollisionLayer">For a trigger: EditorID of the game's collision layer that decides what sets it off.</param>
public sealed record PlacedSpec(
    string EditorId,
    string Cell,
    string Base,
    string? VanillaKind,
    float Ahead, float Right, float Up,
    bool InitiallyDisabled = false,
    float[]? BoxHalfExtents = null,
    string? CollisionLayer = null);

public static class Spec
{
    public const string PluginName = "TheLastMeridian.esp";

    // ------------------------------------------------------------ globals
    // All short, default 0. TLM_Truth etc. are the hidden metrics named by
    // docs/doctrine-of-the-open-ledger.md.
    public static readonly string[] Globals =
    {
        "TLM_G_DataVersion",
        "TLM_G_CaravanOutcome",
        "TLM_G_CaravanMethod",
        "TLM_G_CaravanAliveAtMercy",
        "TLM_G_Rep_MercyCrossing",
        "TLM_G_MQ01_Done",
        "TLM_G_MQ01_DebriefVariant",
        "TLM_G_MQ01_DebriefAnswer",
        "TLM_Truth",
        "TLM_Competence",
        "TLM_Accountability",
        "TLM_MutualTrust",
        "TLM_G_SQ01_EvidenceCount",
        "TLM_G_SQ01_EvidenceLevel",
        "TLM_G_SQ01_Outcome",
        "TLM_G_SQ01_YardAlerted",
        "TLM_G_SQ01_VaneHasLedger",
        "TLM_G_SQ01_HaskellScapegoated",
        // Development only. 0 in every build. The unattended test runner
        // (tools/win/Run-Scenarios.ps1) writes a scenario number into the
        // installed copy of the plugin; TLM:Core then runs that scenario of
        // the self-test by itself and closes the game. Remove before release.
        "TLM_G_DevScenario",
    };

    public static readonly string[] Factions =
    {
        "TLM_Fac_Cutters",
        "TLM_Fac_Caravan",
        "TLM_Fac_MercyCrossing",
    };

    public static readonly MiscSpec[] MiscItems =
    {
        new("TLM_MISC_Dispatch", "Sealed Rail Dispatch"),
        // Kept without a world model on purpose: self-test scenario 3 ends with
        // an experiment on what the game does with a placed item that has none.
        new("TLM_MISC_TornTransitPass", "Torn Transit Pass"),
        // Development only (the placed-content trial). Looks like a bottle cap.
        new("TLM_MISC_TrialObject", "Trial Object", ModelFrom: "Caps001"),
    };

    public static readonly ActivatorSpec[] Activators =
    {
        // Development only (the placed-content trial).
        new("TLM_ACTI_TrialTrigger"),
    };

    // ------------------------------------------------- placed references
    // Development only: the placed-content trial (docs/design/TLM_GRAYBOX_trial.md).
    // References in the game's own test room, which the plugin overrides for
    // the purpose: a person, a trigger and an object; and two more triggers for
    // comparison.
    //
    // Seen in the game on 2026-11-13: a box on an activator of the plugin's
    // and one on the game's own empty trigger, on the layers L_TRIGGER and
    // L_ACTORZONE, each set its stage when the player was moved into it. The
    // same build found that the game's own box triggers carry no layer at all
    // (405 of 407 looked at). So the two comparisons now leave the layer out,
    // one on each activator: if they work, a trigger needs nothing but its box.
    //
    // The person starts disabled, so that nobody new stands about in the other
    // scenarios: a bystander changes what the game makes of a killing
    // (docs/design/VERIFY_LOG.md, the twelfth run).
    //
    // The triggers must not hold the spot where the player arrives: someone
    // already inside when the quest starts never "enters". TrialTriggerHalf and
    // the distances below keep them well clear, and the builder checks it.
    public const string TrialCell = "QASmoke";
    public const float TrialTriggerHalf = 150f;
    // "Typically L_TRIGGER", and actors set such a trigger off: the Creation
    // Kit wiki's page on OnTriggerEnter. Which layers the game's own triggers
    // name, the build output counts: on 2026-11-13, none.
    public const string TriggerLayer = "L_TRIGGER";

    static readonly float[] TrialBox = { TrialTriggerHalf, TrialTriggerHalf, TrialTriggerHalf };

    public static readonly PlacedSpec[] Placed =
    {
        new("TLM_REF_TrialPerson", TrialCell, "WorkshopNPC", "Npc", Ahead: 300, Right: 150, Up: 0, InitiallyDisabled: true),
        new("TLM_REF_TrialTrigger", TrialCell, "TLM_ACTI_TrialTrigger", null, Ahead: 600, Right: -200, Up: 100,
            BoxHalfExtents: TrialBox, CollisionLayer: TriggerLayer),
        new("TLM_REF_TrialTriggerGameBase", TrialCell, "DefaultEmptyTrigger", "Activator", Ahead: 600, Right: 200, Up: 100,
            BoxHalfExtents: TrialBox),
        new("TLM_REF_TrialObject", TrialCell, "TLM_MISC_TrialObject", null, Ahead: 150, Right: -60, Up: 20),
        // As far from the arrival point as the other two, so that the player
        // is moved the same distance into each. (On 2026-11-13 a box stood at
        // 200 ahead, 600 to the right, and the player came down on top of
        // something there. This one is on the other side, nearer the first
        // box, where the floor was open.)
        new("TLM_REF_TrialTriggerNoLayer", TrialCell, "TLM_ACTI_TrialTrigger", null, Ahead: 360, Right: -520, Up: 100,
            BoxHalfExtents: TrialBox),
    };

    public static readonly BookSpec[] Books =
    {
        new("TLM_BOOK_RailMaintLedger", "Maintenance Ledger, Line 14",
            "LINE 14 - LOCO/CAR MAINTENANCE - IRON JUNCTION YARD\n\n" +
            "Entry  Item                 Action     Result  Signed\n" +
            " 41    Brake shoes, car 3   Renewed    Good    R. Ostrander\n" +
            " 42    Draw-bar, car 3      Inspected  Sound   R. Ostrander\n" +
            " 43    Brake shoes, car 5   Renewed    Good    R. Ostrander\n" +
            " 44    Journal box, car 5   Inspected  Sound   R. Ostrander\n"),
        new("TLM_BOOK_MarshalLog", "Rail Marshal's Journal",
            "Greenwater. Ostrander took ill on the 9th. By the 14th he was gone. I carried " +
            "the line's word to the yard the same week. Last I saw, no one had been sent in his place.\n\n" +
            "Odd, then, that every car I rode on this trip came up on the list as \"signed clean\".\n\n" +
            "Pritchard will want to see this in person."),
    };

    // ----------------------------------------------------------- messages
    public static readonly MessageSpec[] Messages =
    {
        new("TLM_MSG_Tut_Wake", null, "Search the wreck. Take what you can carry.", Box: false),
        new("TLM_MSG_Tut_SixRounds", null, "Six rounds in the cylinder. Count them.", Box: false),
        new("TLM_MSG_E1", "Brake shoes", "The shoes are ground to the rivets.", Box: true,
            new ButtonSpec("Step back")),
        new("TLM_MSG_E2", "Draw-bar", "The draw-bar is cracked through. The break is dark with old rust.", Box: true,
            new ButtonSpec("Step back")),
        new("TLM_MSG_PublishChoice", "Notice board", "Post the ledger pages where the town can read them?", Box: true,
            // Button order is the contract with TLM:MessageStageAlias.ButtonStages.
            new ButtonSpec("Post the pages, no name"),
            new ButtonSpec("Name the Yard Office", new GlobalAtLeast("TLM_G_SQ01_EvidenceLevel", 2)),
            // TODO on the game machine: hide this button with GetDead on Haskell's reference.
            new ButtonSpec("Name Corwin Haskell"),
            new ButtonSpec("Leave it")),
        new("TLM_MSG_BurnLedger", "Stove", "Burn the ledger?", Box: true,
            new ButtonSpec("Burn it"),
            new ButtonSpec("Keep it")),
        // Development only (the placed-content trial): its title is the name
        // the placed person is shown under. A placeholder, not a character.
        new("TLM_MSG_TrialPersonName", "Trial Settler", "", Box: false),
    };

    // --------------------------------------------------------------- core
    public static readonly QuestSpec Core = new(
        "TLM_Core", "The Last Meridian (core)", "None", 50, StartGameEnabled: true,
        Stages: Array.Empty<StageSpec>(),
        Objectives: Array.Empty<ObjectiveSpec>(),
        Aliases: Array.Empty<AliasSpec>(),
        Script: new ScriptBind("TLM:Core",
            new FormProp("TLM_G_DataVersion", "TLM_G_DataVersion"),
            new FormProp("TLM_MQ01", "TLM_MQ01"),
            new FormProp("TLM_G_DevScenario", "TLM_G_DevScenario")),
        // Development only: the in-game self-test (console: cqf TLM_Core RunSelfTest).
        // Remove this binding, and scripts/Source/User/TLM/SelfTest.psc, before any release.
        ExtraScripts: new[]
        {
            new ScriptBind("TLM:SelfTest",
                new FormProp("TLM_MQ01", "TLM_MQ01"),
                new FormProp("TLM_SQ01", "TLM_SQ01"),
                new FormProp("TLM_G_DataVersion", "TLM_G_DataVersion"),
                new FormProp("TLM_G_CaravanOutcome", "TLM_G_CaravanOutcome"),
                new FormProp("TLM_G_CaravanMethod", "TLM_G_CaravanMethod"),
                new FormProp("TLM_G_CaravanAliveAtMercy", "TLM_G_CaravanAliveAtMercy"),
                new FormProp("TLM_G_Rep_MercyCrossing", "TLM_G_Rep_MercyCrossing"),
                new FormProp("TLM_G_MQ01_Done", "TLM_G_MQ01_Done"),
                new FormProp("TLM_G_MQ01_DebriefVariant", "TLM_G_MQ01_DebriefVariant"),
                new FormProp("TLM_G_MQ01_DebriefAnswer", "TLM_G_MQ01_DebriefAnswer"),
                new FormProp("TLM_Truth", "TLM_Truth"),
                new FormProp("TLM_Competence", "TLM_Competence"),
                new FormProp("TLM_Accountability", "TLM_Accountability"),
                new FormProp("TLM_MutualTrust", "TLM_MutualTrust"),
                new FormProp("TLM_G_SQ01_EvidenceCount", "TLM_G_SQ01_EvidenceCount"),
                new FormProp("TLM_G_SQ01_EvidenceLevel", "TLM_G_SQ01_EvidenceLevel"),
                new FormProp("TLM_G_SQ01_Outcome", "TLM_G_SQ01_Outcome"),
                new FormProp("TLM_G_SQ01_YardAlerted", "TLM_G_SQ01_YardAlerted"),
                new FormProp("TLM_G_SQ01_HaskellScapegoated", "TLM_G_SQ01_HaskellScapegoated"),
                new FormProp("TornTransitPass", "TLM_MISC_TornTransitPass"),
                new FormProp("TLM_Trial", "TLM_Trial")),
            // Development only: self-test scenarios 2 and 3. Finds out in the
            // game whether actors and markers can be made at run time and put
            // into the quest's aliases, so that the test matrix can be run
            // without a hand-built test cell. The actor base is the game's
            // generic settler and the marker is the game's plain marker, both
            // looked up when the plugin is built; without Fallout4.esm they
            // stay unset.
            new ScriptBind("TLM:FixtureProbe",
                new FormProp("TLM_MQ01", "TLM_MQ01"),
                new FormProp("TornTransitPass", "TLM_MISC_TornTransitPass"),
                new VanillaProp("FixtureActorBase", "WorkshopNPC", "Npc"),
                new VanillaProp("FixtureMarkerBase", "XMarker", "Static")),
            // Development only: self-test scenarios 4 to 9. Plays the main
            // quest with a caravan made at run time from the same two forms.
            new ScriptBind("TLM:WorldCases",
                new FormProp("TLM_MQ01", "TLM_MQ01"),
                new FormProp("TLM_G_CaravanMethod", "TLM_G_CaravanMethod"),
                new FormProp("TLM_G_CaravanAliveAtMercy", "TLM_G_CaravanAliveAtMercy"),
                new FormProp("TLM_G_Rep_MercyCrossing", "TLM_G_Rep_MercyCrossing"),
                new FormProp("TLM_G_MQ01_Done", "TLM_G_MQ01_Done"),
                new FormProp("TLM_G_MQ01_DebriefVariant", "TLM_G_MQ01_DebriefVariant"),
                new FormProp("TLM_G_MQ01_DebriefAnswer", "TLM_G_MQ01_DebriefAnswer"),
                new FormProp("TLM_Truth", "TLM_Truth"),
                new FormProp("TLM_Accountability", "TLM_Accountability"),
                new FormProp("TLM_MutualTrust", "TLM_MutualTrust"),
                new FormProp("TornTransitPass", "TLM_MISC_TornTransitPass"),
                new VanillaProp("FixtureActorBase", "WorkshopNPC", "Npc"),
                new VanillaProp("FixtureMarkerBase", "XMarker", "Static")),
            // Development only: self-test scenarios 101 and up, the rows of
            // the test matrices. TLM:MatrixCases is generated from the logic
            // model (tools/gen_matrix_cases.py); TLM:CaseDriver does in the
            // game what stands for each of the model's events and compares
            // both quests with the model after every one.
            new ScriptBind("TLM:CaseDriver",
                new FormProp("TLM_MQ01", "TLM_MQ01"),
                new FormProp("TLM_SQ01", "TLM_SQ01"),
                new FormProp("TLM_G_CaravanMethod", "TLM_G_CaravanMethod"),
                new FormProp("TLM_G_CaravanAliveAtMercy", "TLM_G_CaravanAliveAtMercy"),
                new FormProp("TLM_G_Rep_MercyCrossing", "TLM_G_Rep_MercyCrossing"),
                new FormProp("TLM_G_MQ01_Done", "TLM_G_MQ01_Done"),
                new FormProp("TLM_G_MQ01_DebriefVariant", "TLM_G_MQ01_DebriefVariant"),
                new FormProp("TLM_G_MQ01_DebriefAnswer", "TLM_G_MQ01_DebriefAnswer"),
                new FormProp("TLM_Truth", "TLM_Truth"),
                new FormProp("TLM_Competence", "TLM_Competence"),
                new FormProp("TLM_Accountability", "TLM_Accountability"),
                new FormProp("TLM_MutualTrust", "TLM_MutualTrust"),
                new FormProp("TLM_G_SQ01_EvidenceCount", "TLM_G_SQ01_EvidenceCount"),
                new FormProp("TLM_G_SQ01_EvidenceLevel", "TLM_G_SQ01_EvidenceLevel"),
                new FormProp("TLM_G_SQ01_Outcome", "TLM_G_SQ01_Outcome"),
                new FormProp("TLM_G_SQ01_YardAlerted", "TLM_G_SQ01_YardAlerted"),
                new FormProp("TLM_G_SQ01_VaneHasLedger", "TLM_G_SQ01_VaneHasLedger"),
                new FormProp("TLM_G_SQ01_HaskellScapegoated", "TLM_G_SQ01_HaskellScapegoated"),
                new FormProp("DispatchItem", "TLM_MISC_Dispatch"),
                new FormProp("LedgerItem", "TLM_BOOK_RailMaintLedger"),
                new FormProp("JournalItem", "TLM_BOOK_MarshalLog"),
                new FormProp("TornTransitPass", "TLM_MISC_TornTransitPass"),
                new VanillaProp("Caps", "Caps001", "MiscItem"),
                new VanillaProp("FixtureActorBase", "WorkshopNPC", "Npc"),
                new VanillaProp("FixtureMarkerBase", "XMarker", "Static")),
            new ScriptBind("TLM:MatrixCases"),
        });

    // --------------------------------------------------------------- MQ01
    // The game's own scripts. Seen in the game on 2026-11-13, on aliases
    // filled with references this plugin places: each set its stage.
    // (Their ShowTraces property, "Set to TRUE if you want the traces in this
    // script to show up in the log", was tried in that run: the game took it
    // without complaint and wrote nothing. It is not set any more.)
    static ScriptBind SetStageOnPickup(int stage) =>
        new("DefaultAliasOnContainerChangedTo", new IntProp("StageToSet", stage));

    static ScriptBind SetStageOnTrigger(int stage) =>
        new("DefaultAliasOnTriggerEnter", new IntProp("StageToSet", stage));

    static readonly ScriptBind CutterScript = new("TLM:MQ01CutterAlias");
    static readonly ScriptBind HandScript = new("TLM:MQ01CaravanHandAlias");

    public static readonly QuestSpec MQ01 = new(
        "TLM_MQ01", "Six Rounds to Mercy", "MainQuest", 60, StartGameEnabled: false,
        Stages: new StageSpec[]
        {
            new(10, "The train is a ruin and you're alive. Whoever carried the line's mail didn't make it."),
            new(15, "Six rounds in the cylinder. Count them."),
            new(20, "The marshal's dispatch is sealed to the Sheriff of Mercy Crossing."),
            new(30, Note: "Ambush live"),
            new(31, "You turned the Cutters off the wagon."),
            new(32, "You kept walking."),
            new(33, "You took a share."),
            new(34, Note: "Caravan missed: the player never met the ambush"),
            new(35, "You turned your gun on the wagon's own."),
            new(37, Note: "Cutters turn on the player (speech failed or deal refused)"),
            new(40, "Mercy Crossing."),
            new(50, "Delivered to Sheriff Pritchard."),
            new(51, Note: "Debrief: admit (evaded)"),
            new(52, Note: "Debrief: deny (evaded)"),
            new(53, Note: "Debrief: confess (witness)"),
            new(54, Note: "Debrief: blame the Cutters (witness)"),
            new(55, Note: "Debrief: 'She's lying.' (witness)"),
            new(60, "Pritchard has more for you."),
            new(100, CompleteQuest: true, Note: "Completed"),
            new(900, Note: "Recovery"),
        },
        Objectives: new ObjectiveSpec[]
        {
            new(10, "Find the marshal's dispatch case", "Marshal"),
            new(20, "Take the dispatch to Sheriff Owen Pritchard in Mercy Crossing", "SheriffPritchard"),
        },
        Aliases: new AliasSpec[]
        {
            new("Player", Fill.Player, Scripts: new ScriptBind("TLM:MQ01PlayerAlias", new FormProp("SideQuest", "TLM_SQ01"))),
            new("Marshal", AllowDead: true, Note: "Dead Rail Marshal Tobias Gantt (TLM_NPC_MARSHAL_DEAD)"),
            new("Dispatch", Fill.CreateIn, QuestObject: true, CreateItem: "TLM_MISC_Dispatch", CreateInAlias: "Marshal",
                Scripts: SetStageOnPickup(20)),
            new("Revolver", Note: "Placed revolver. Not a quest object: the player may sell or drop it.",
                Scripts: SetStageOnPickup(15)),
            new("SheriffPritchard", Essential: true, Note: "Unique actor TLM_NPC_SHERIFF_MERCY"),
            new("CaravanMaster", Protected: true, AllowDisabled: true, Note: "Nell Fenwick", Scripts: HandScript),
            new("CaravanDrover", Protected: true, AllowDisabled: true, Note: "Abel Rudd", Scripts: HandScript),
            new("CaravanMasterInTown", Fill.ScriptFilled, Essential: true, Note: "Forced at stage 40"),
            new("CaravanDroverInTown", Fill.ScriptFilled, Essential: true, Note: "Forced at stage 40"),
            new("CutterLead", Protected: true, AllowDead: true, AllowDisabled: true, Note: "Reese Dunmore", Scripts: CutterScript),
            new("CutterA", Protected: true, AllowDead: true, AllowDisabled: true, Scripts: CutterScript),
            new("CutterB", Protected: true, AllowDead: true, AllowDisabled: true, Scripts: CutterScript),
            new("CutterC", Protected: true, AllowDead: true, AllowDisabled: true, Scripts: CutterScript),
            new("Wagon", Note: "TLM_CONT_WagonCargo, owned by TLM_Fac_Caravan"),
            new("AmbushTrigger", Note: "TLM_TRIG_AmbushSight", Scripts: SetStageOnTrigger(30)),
            new("AmbushCenter", Note: "TLM_MARK_AmbushCenter"),
            new("AmbushEnableMarker", AllowDisabled: true, Note: "Enable parent of the ambush actors; starts disabled"),
            new("WreckStart", Note: "TLM_MARK_WreckStart"),
            new("TownGate", Note: "TLM_TRIG_TownGate", Scripts: SetStageOnTrigger(40)),
            new("CaravanYard", Note: "TLM_MARK_CaravanYard"),
            new("MercyCrossingLoc", IsLocation: true, Note: "TLM_Loc_MercyCrossing"),
        },
        Script: new ScriptBind("TLM:MQ01Quest",
            new FormProp("TLM_G_CaravanOutcome", "TLM_G_CaravanOutcome"),
            new FormProp("TLM_G_CaravanMethod", "TLM_G_CaravanMethod"),
            new FormProp("TLM_G_CaravanAliveAtMercy", "TLM_G_CaravanAliveAtMercy"),
            new FormProp("TLM_G_Rep_MercyCrossing", "TLM_G_Rep_MercyCrossing"),
            new FormProp("TLM_G_MQ01_Done", "TLM_G_MQ01_Done"),
            new FormProp("TLM_G_MQ01_DebriefVariant", "TLM_G_MQ01_DebriefVariant"),
            new FormProp("TLM_G_MQ01_DebriefAnswer", "TLM_G_MQ01_DebriefAnswer"),
            new FormProp("TLM_Truth", "TLM_Truth"),
            new FormProp("TLM_Accountability", "TLM_Accountability"),
            new FormProp("TLM_MutualTrust", "TLM_MutualTrust"),
            new AliasProp("Alias_CaravanMaster", "CaravanMaster"),
            new AliasProp("Alias_CaravanDrover", "CaravanDrover"),
            new AliasProp("Alias_CaravanMasterInTown", "CaravanMasterInTown"),
            new AliasProp("Alias_CaravanDroverInTown", "CaravanDroverInTown"),
            new AliasProp("Alias_CutterLead", "CutterLead"),
            new AliasProp("Alias_CutterA", "CutterA"),
            new AliasProp("Alias_CutterB", "CutterB"),
            new AliasProp("Alias_CutterC", "CutterC"),
            new AliasProp("Alias_Wagon", "Wagon"),
            new AliasProp("Alias_AmbushCenter", "AmbushCenter"),
            new AliasProp("Alias_AmbushEnableMarker", "AmbushEnableMarker"),
            new AliasProp("Alias_WreckStart", "WreckStart"),
            new AliasProp("Alias_CaravanYard", "CaravanYard"),
            new FormProp("DispatchItem", "TLM_MISC_Dispatch"),
            new FormProp("TornTransitPass", "TLM_MISC_TornTransitPass"),
            new FormProp("TLM_Fac_Cutters", "TLM_Fac_Cutters"),
            new FormProp("TLM_SQ01", "TLM_SQ01"),
            new FormProp("TutWake", "TLM_MSG_Tut_Wake"),
            new FormProp("TutSixRounds", "TLM_MSG_Tut_SixRounds"),
            // Dev start (decision T1, option a): the tester is already at the wreck.
            new BoolProp("MovePlayerOnStart", false)));

    // --------------------------------------------------------------- SQ01
    static ScriptBind Examine(string message, int stage) =>
        new("TLM:MessageStageAlias", new FormProp("MessageToShow", message), new IntProp("StageAlways", stage));

    public static readonly QuestSpec SQ01 = new(
        "TLM_SQ01", "Signed Clean", "SideQuests", 40, StartGameEnabled: false,
        Stages: new StageSpec[]
        {
            new(5, Note: "Running, hidden. Set by MQ01 stage 10."),
            new(10, "The train's maintenance ledger says the brakes and couplers were inspected and sound."),
            new(11, Note: "E1 brake shoes examined"),
            new(12, Note: "E2 draw-bar examined"),
            new(13, Note: "E3 marshal's journal taken"),
            new(14, Note: "E4 Ada Pike's parts book seen"),
            new(20, "The ledger and the wreck don't agree."),
            new(25, "Whoever kept this ledger wrote down work that was never done."),
            new(41, Note: "Reported to Pritchard"),
            new(42, Note: "Posted, no name"),
            new(43, Note: "Posted, Yard Office named"),
            new(44, Note: "Posted, Haskell named"),
            new(45, Note: "Sold to Vane"),
            new(46, Note: "Destroyed"),
            new(50, Note: "Resolved"),
            new(100, CompleteQuest: true, Note: "Completed"),
            new(900, Note: "Recovery"),
        },
        Objectives: new ObjectiveSpec[]
        {
            new(10, "Compare the ledger to the wreck"),
            new(20, "Decide what to do with the evidence"),
        },
        Aliases: new AliasSpec[]
        {
            new("CabLockbox", Note: "TLM_CONT_CabLockbox in the locomotive cab"),
            new("Ledger", Fill.CreateIn, QuestObject: true, CreateItem: "TLM_BOOK_RailMaintLedger", CreateInAlias: "CabLockbox",
                Scripts: SetStageOnPickup(10)),
            new("Marshal", AllowDead: true, Note: "Same reference as TLM_MQ01's Marshal alias"),
            new("Journal", Fill.CreateIn, QuestObject: true, CreateItem: "TLM_BOOK_MarshalLog", CreateInAlias: "Marshal",
                Scripts: SetStageOnPickup(13)),
            new("BrakeShoes", Note: "Examinable activator", Scripts: Examine("TLM_MSG_E1", 11)),
            new("DrawBar", Note: "Examinable activator", Scripts: Examine("TLM_MSG_E2", 12)),
            new("Pike", Note: "Unique actor TLM_NPC_GUNSMITH_MERCY"),
            new("Pritchard", Note: "Unique actor TLM_NPC_SHERIFF_MERCY"),
            new("Vane", Note: "Unique actor TLM_NPC_MERCHANT_MERCY"),
            new("Haskell", Note: "Unique actor TLM_NPC_FREIGHT_MERCY"),
            new("NoticeBoard", Note: "TLM_ACTI_NoticeBoard",
                Scripts: new ScriptBind("TLM:MessageStageAlias",
                    new FormProp("MessageToShow", "TLM_MSG_PublishChoice"),
                    new IntListProp("ButtonStages", 42, 43, 44, 0),
                    new IntProp("RequireStageDone", 20),
                    new IntProp("BlockIfStageDone", 50))),
            new("Stove", Note: "Any stove or the wreck fire",
                Scripts: new ScriptBind("TLM:MessageStageAlias",
                    new FormProp("MessageToShow", "TLM_MSG_BurnLedger"),
                    new IntListProp("ButtonStages", 46, 0),
                    new IntProp("RequireStageDone", 10),
                    new IntProp("BlockIfStageDone", 50))),
        },
        Script: new ScriptBind("TLM:SQ01Quest",
            new FormProp("TLM_G_SQ01_EvidenceCount", "TLM_G_SQ01_EvidenceCount"),
            new FormProp("TLM_G_SQ01_EvidenceLevel", "TLM_G_SQ01_EvidenceLevel"),
            new FormProp("TLM_G_SQ01_Outcome", "TLM_G_SQ01_Outcome"),
            new FormProp("TLM_G_SQ01_YardAlerted", "TLM_G_SQ01_YardAlerted"),
            new FormProp("TLM_G_SQ01_VaneHasLedger", "TLM_G_SQ01_VaneHasLedger"),
            new FormProp("TLM_G_SQ01_HaskellScapegoated", "TLM_G_SQ01_HaskellScapegoated"),
            new FormProp("TLM_Truth", "TLM_Truth"),
            new FormProp("TLM_Competence", "TLM_Competence"),
            new FormProp("TLM_Accountability", "TLM_Accountability"),
            new FormProp("TLM_MutualTrust", "TLM_MutualTrust"),
            new AliasProp("Alias_Haskell", "Haskell"),
            new FormProp("LedgerItem", "TLM_BOOK_RailMaintLedger"),
            new FormProp("JournalItem", "TLM_BOOK_MarshalLog"),
            new VanillaProp("Caps", "Caps001", "MiscItem")));

    // -------------------------------------------------------------- trial
    // Development only: the placed-content trial, self-test scenario 10
    // (docs/design/TLM_GRAYBOX_trial.md). A quest of its own, so that nothing
    // about it can touch the two real quests: one alias for each placed
    // reference, the game's own default scripts on the triggers and the
    // object, and a stage for each of those scripts to set. It is started by
    // the test only. Every alias is Optional, so that one that stays empty is
    // reported by name and does not keep the quest from starting.
    // Remove it, the records above marked "trial" and
    // scripts/Source/User/TLM/PlacedTrial.psc before any release.
    public static readonly QuestSpec Trial = new(
        "TLM_Trial", "The Last Meridian (placed-content trial)", "None", 30, StartGameEnabled: false,
        Stages: new StageSpec[]
        {
            new(10, Note: "The player entered the trigger"),
            new(11, Note: "The player entered the trigger made on the game's own empty trigger, with no layer"),
            new(12, Note: "The player entered the trigger of the plugin's own with no layer"),
            new(20, Note: "The player picked the object up"),
            new(100, CompleteQuest: true, Note: "Trial finished"),
        },
        Objectives: Array.Empty<ObjectiveSpec>(),
        Aliases: new AliasSpec[]
        {
            new("Person", Fill.Placed, AllowDisabled: true, Placed: "TLM_REF_TrialPerson", DisplayName: "TLM_MSG_TrialPersonName"),
            new("Trigger", Fill.Placed, Placed: "TLM_REF_TrialTrigger", Scripts: SetStageOnTrigger(10)),
            new("TriggerGameBase", Fill.Placed, Placed: "TLM_REF_TrialTriggerGameBase", Scripts: SetStageOnTrigger(11)),
            new("Object", Fill.Placed, Placed: "TLM_REF_TrialObject", Scripts: SetStageOnPickup(20)),
            new("TriggerNoLayer", Fill.Placed, Placed: "TLM_REF_TrialTriggerNoLayer", Scripts: SetStageOnTrigger(12)),
        },
        Script: new ScriptBind("TLM:PlacedTrial",
            new AliasProp("Alias_Person", "Person"),
            new AliasProp("Alias_Trigger", "Trigger"),
            new AliasProp("Alias_TriggerGameBase", "TriggerGameBase"),
            new AliasProp("Alias_Object", "Object"),
            new AliasProp("Alias_TriggerNoLayer", "TriggerNoLayer"),
            new FormProp("TrialObject", "TLM_MISC_TrialObject"),
            new VanillaProp("MarkerBase", "XMarker", "Static")));

    public static readonly QuestSpec[] Quests = { Core, MQ01, SQ01, Trial };
}
