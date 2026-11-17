namespace Tlm.PluginBuilder;

// ACT1-RUNTIME-001: the Mercy briefing and the optional review copy
// (docs/design/ACT1_RUNTIME_001.md). DEVELOPMENT PREVIEW.
//
// After the main quest's debrief Owen Pritchard can be asked about the three
// roads, and about the pike he offers his 2298 review copy, a book. That is
// all of it. The quest below is a utility task of its own: it is NOT TLM_MQ02,
// its stages 10 and 20 are NOT that quest's stages, and no record here starts,
// finishes or pays for a road. The three destinations are not built.
//
// EVERY SPOKEN LINE, BUTTON, TITLE AND THE BOOK'S TEXT IS COPIED WORD FOR WORD
// from the accepted writing in assets/incoming/act1/story (as accepted at
// d142104). Nothing here is new speech. Which field each string comes from is
// in docs/design/ACT1_RUNTIME_001_MAPPING.json, and
// tools/papyrus_sim/test_mercy_briefing.py compares the plugin as built with
// those fields, character by character. Change a line there first, by the
// writing's own process; never here.
//
// The strings marked UI are product-availability text, not fiction: they say
// what this build does not contain. They stand outside the quoted speech.
//
// Nothing here may read a field of Spec that is not a constant (see Act1).
public static class MercyBriefing
{
    public const string QuestId = "TLM_MercyBriefing";
    public const string BookId = "TLM_BOOK_Docket2298";
    public const string MessagePrefix = "TLM_MSG_MB_";

    const string Pritchard = "Owen Pritchard";
    // The first section's own word for "go on" (Act1.GoOn); the writing's
    // nodes without buttons have an implicit Continue.
    const string GoOn = "Continue";

    // ------------------------------------------------------------------ UI
    // Product-availability text. Not said by anybody.
    // GREENWATER-STORY-001 (order, item 1): in this candidate Greenwater is playable, so the three strings below
    // no longer say that no destination is. The a8 source and its package keep the earlier wording.
    public const string UiBriefingOnly = "Mercy briefing. Three roads and the qualified Four Flags entry are available.";
    public const string UiHandOffFooter = "Opening complete. Ask for briefings or use a story test point.";
    public const string UiJournalComplete = "Mercy briefing complete. Three roads and qualified Four Flags entry remain available.";
    public const string UiObjective = "Ask Pritchard about the three roads.";
    public const string UiCopyIssued = "One review copy only. No second copy is given.";
    public const string UiCopyPending = "Review copy hand-over unconfirmed. None is given again. Report this to the tester.";
    public const string UiQuestName = "Mercy briefing";

    // ------------------------------------------------- the accepted writing
    // talk/tlm_mq02.json, by node id. The hub's question is reused as a
    // preview message; that node's condition (mq02 done 100) and its three
    // targets are deliberately NOT imported.
    const string HubText = "Which road do you want to ask about? Tell me what you know, or ask what to look for.";
    static readonly string[] HubLabels = { "The rail.", "The river.", "Red Hollow.", "Not now." };
    const string RailText = "Iron Junction. Ask for Gussie Lockridge and don't let her feed you. She's lost four trains and blames the weather, and Gussie has never been wrong about weather in her life.";
    const string RiverText = "Greenwater. The woman with the ladle is Opal Starnes. Do what she says until you understand why, and after that use your own judgment. There's a boy with a skiff at the landing.";
    const string PikeText = "Red Hollow, by the pike. You'll pass Brigg's gate at the gap. Ask what evidence Esther Quill has heard before you pay for a pardon. A bench on a wagon isn't proof of a fair hearing.";
    static readonly string[] PikeLabels = { "What should I ask Quill?", GoOn };
    // The Take button's effect in the writing (mq02c set 16) is deliberately
    // NOT imported: TLM_MQ02c is not built.
    const string DocketText = "In 2298 I hanged an innocent man. Quill had the counter-evidence before the drop. I checked too late. Take my review copy if you mean to ask for a hearing. It doesn't prove the man on her wagon innocent.";
    static readonly string[] DocketLabels = { "Take the review copy.", "Leave the copy." };
    // The first section's design line for the hand-off (TLM_MQ01 section 8.3),
    // as Act1.Messages has it in TLM_MSG_A1_PritchardHandOff. Not from the
    // writing intake; unchanged here.
    const string HandOffText = "Greenwater's food has gone short. Red Hollow's sealed the mine. Iron Junction's rails are being cut. Pick one. I don't have the people for all three.";

    // documents.json, docket_2298.
    const string DocketTitle = "Mercy Road Case: 2298 Review Copy";
    const string DocketBody =
        "MERCY ROAD CASE: SPRING 2298\n" +
        "Retained review copy. Not a pardon in any current case.\n\n" +
        "The carrier's dated receipt and two sworn accounts place the condemned man away from the road at the hour alleged. " +
        "Copies were entered with Magistrate Esther Quill before sentence was carried out.\n\n" +
        "I received the warrant and carried it out. I later checked the accounts against the receiving ledger. " +
        "We hanged an innocent man. I have kept the rope; it is not an answer. " +
        "The finding should have gone into the court record then. I am making this copy available now.\n\n" +
        "Owen Pritchard, Sheriff\n" +
        "Attached: entry receipt bearing E. Quill's court mark.";

    // ------------------------------------------------------------- records
    /// <summary>A box of somebody's speech, as the first section writes one: the name, then the line in quotes.</summary>
    public static string Spoken(string who, string line) => who + ": \"" + line + "\"";

    /// <summary>UI text set under a spoken line, apart from it.</summary>
    public static string WithUi(string spoken, string ui) => spoken + "\n\n[" + ui + "]";

    static MessageSpec Says(string id, string line, params string[] buttons) =>
        new(MessagePrefix + id, Pritchard, Spoken(Pritchard, line), Box: true, buttons.Select(b => new ButtonSpec(b)).ToArray());

    static MessageSpec Ui(MessageSpec message, string ui) => message with { Text = WithUi(message.Text, ui) };

    public static readonly BookSpec[] Books =
    {
        // Takes after one of the game's notes, as the first section's two papers do.
        new(BookId, DocketTitle, DocketBody, LooksLikeANote: true),
    };

    // The order of the buttons is the contract with TLM:MercyBriefing and with
    // tools/logic_model/mercy_briefing_model.py.
    public static readonly MessageSpec[] Messages =
    {
        Ui(Says("Hub", HubText, HubLabels), UiBriefingOnly),
        Says("Rail", RailText, GoOn),
        Says("River", RiverText, GoOn),
        Says("Pike", PikeText, PikeLabels),
        Says("Docket", DocketText, DocketLabels),
        // The same speech when no copy can be given: no button promises one.
        Says("DocketIssued", DocketText, GoOn),
        // UI, on the screen's edge; not boxes.
        new(MessagePrefix + "CopyIssuedNote", null, UiCopyIssued, Box: false),
        new(MessagePrefix + "CopyPendingNote", null, UiCopyPending, Box: false),
        // The hand-off at stage 60, with a footer that says he can be asked again.
        Ui(Says("HandOff", HandOffText, GoOn), UiHandOffFooter),
    };

    static Prop Line(string property, string id) => new FormProp(property, MessagePrefix + id);

    public static readonly QuestSpec Quest = new(
        QuestId, UiQuestName, "SideQuests", 35, StartGameEnabled: false,
        Stages: new StageSpec[]
        {
            new(10, UiBriefingOnly, Note: "Briefing begun. Preview utility task; not a stage of TLM_MQ02"),
            new(20, UiJournalComplete, CompleteQuest: true, Note: "A road's brief was shown; the utility task is complete. Not TLM_MQ02"),
        },
        Objectives: new ObjectiveSpec[]
        {
            new(10, UiObjective, TargetAlias: "Briefer"),
        },
        Aliases: new AliasSpec[]
        {
            // Whoever was asked. No flag: it protects nobody and keeps nothing.
            new("Briefer", Fill.ScriptFilled, Note: "whoever was asked; put in by TLM:MercyBriefing at the first hub"),
        },
        Script: new ScriptBind("TLM:MercyBriefing",
            new FormProp("TLM_MQ01", "TLM_MQ01"),
            new FormProp("TLM_G_MQ01_Done", "TLM_G_MQ01_Done"),
            new AliasProp("Alias_Briefer", "Briefer"),
            new FormProp("ReviewCopy", BookId),
            Line("HubLine", "Hub"),
            Line("RailLine", "Rail"),
            Line("RiverLine", "River"),
            Line("PikeLine", "Pike"),
            Line("DocketLine", "Docket"),
            Line("DocketIssuedLine", "DocketIssued"),
            Line("CopyIssuedNote", "CopyIssuedNote"),
            Line("CopyPendingNote", "CopyPendingNote"),
            Line("HandOffLine", "HandOff")));
}
