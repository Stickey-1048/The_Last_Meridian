Scriptname TLM:Act1Walk extends Quest
{Development only, attached to TLM_A1: Act I, first section, as a rough cut a
person can walk through (docs/design/TLM_ACT1_first_section.md). It must be
removed before any release, with its quest, TLM:Act1Talk and the records the
builder marks "Act1".

The plugin places thirteen people and what lies about them in the game's
test room, all switched off. This script
  - sets the section up: starts the main quest, puts each placed reference
    into the alias of the real quests that is meant for it (as the test
    scenarios do with their stand-ins), and switches everything on;
  - holds what people say. The player activates somebody, TLM:Act1Talk on
    that person's alias calls Spoken, and the line that fits where the two
    quests stand is shown as a box. A button sets a stage of TLM_MQ01 or
    TLM_SQ01 and nothing else: what a stage may do is decided by those
    quests' own scripts, as it always was;
  - carries the unattended check of all that, self-test scenario 12 (Audit).
    Nobody is there to press a button, so it checks what is placed and then
    walks one road through the chapter by doing what the buttons would do.

The two quests' rules are not changed and not repeated here. Three small
things are given by this script and are not known to the quests: Nell
Fenwick's thanks (caps, once), the share of a deal with Reese Dunmore
(caps), and six rounds with the marshal's revolver.

Lines that begin INFO are facts about the game, reported and not scored.

COMPILES (2026-11-14). The unattended check (Audit) RAN IN THE GAME that
day: 39 of 42 in the fifteenth run, 42 of 42 in the sixteenth and again in
the seventeenth, the run of all 65 scenarios (docs/design/VERIFY_LOG.md).
Seen at work there: properties that are lists of aliases and of text, arrays
made with "new", EnableNoWait, ForceRefTo for a thing, a placed actor that
starts dead, a placed weapon picked up, and the books and the container the
plugin places (held and, the books, taken; none read or opened).
Begin RAN IN THE GAME once, on 2026-11-14, with an agent watching and nobody
playing: the section was set up in 38 seconds, no alias empty and nobody
missing, the main quest's start and its first objective came up on the
screen and people stood in the room. Whether the Pip-Boy was on the arm
(EquipItem) and whether the opening notice showed was not looked at.
NOT RUN IN THE GAME: everything a person does after that. Every box
(Message.Show with buttons), Utility.RandomInt, Spoken and all that people
say, the debrief. Nobody has played the section: no key the agent sent
reached the game.}

bool marshalDeathIssued = false
VoiceType Property PritchardOriginalVoice Auto Const
ReferenceAlias[] Property HelpCast Auto Const
ReferenceAlias[] Property HelpAnchors Auto Const
Message Property SaySheriffWarning Auto Const
Sound Property RecordedSheriffWarning Auto Const
Sound Property RecordedDispatchCase Auto Const
Sound Property RecordedRoadHandOff Auto Const
Sound Property RecordedPikeBook Auto Const
Sound Property RecordedDunmoreHold Auto Const
Sound Property RecordedTalbotGate Auto Const
ObjectReference Property OpeningOriginalDunmore Auto Const
ObjectReference Property OpeningOriginalTalbot Auto Const
ReferenceAlias Property Alias_Talbot Auto Const
Actor helpPlayer
Actor[] helpActors
int helpEpoch = -1
bool helpReturnDue = false

ReferenceAlias Property Alias_Pritchard Auto Const
ReferenceAlias Property Alias_Pike Auto Const
ObjectReference Property OpeningOriginalPike Auto Const
Quest Property FirstBrakeInquiry Auto Const
Message Property SayInquiryOffer Auto Const
Message Property SayInquiryOfferDead Auto Const
Message Property SayInquirySheriffMenu Auto Const
Message Property SayInquiryPending Auto Const
Message Property SayInquiryAdaMenu Auto Const
Message Property SayInquiryHistory Auto Const
Message Property SayInquiryReport Auto Const
Message Property SayInquiryReported Auto Const
Message Property SayInquiryUnavailable Auto Const
int inquiryState = 0
int inquiryEpoch = 0
int inquiryRegisterEpoch = -1
bool inquiryBusy = false
Actor inquiryPlayer
Actor inquirySpeaker

Group Quests
	Quest Property TLM_MQ01 Auto Const Mandatory
	Quest Property TLM_SQ01 Auto Const Mandatory
	Quest Property TLM_FourFlags Auto Const
	Quest Property TLM_FourFlagsEntry Auto Const
	Quest Property TLM_BlackLedger Auto Const
	Quest Property TLM_BlackLedgerEntry Auto Const
	ObjectReference Property BlackLedgerOriginalSheriff Auto Const
	ObjectReference Property BlackLedgerOriginalVane Auto Const
	ObjectReference Property BlackLedgerOriginalHaskell Auto Const
EndGroup

Group Globals
	GlobalVariable Property TLM_G_CaravanOutcome Auto Const Mandatory
	GlobalVariable Property TLM_G_CaravanMethod Auto Const Mandatory
	GlobalVariable Property TLM_G_CaravanAliveAtMercy Auto Const Mandatory
	GlobalVariable Property TLM_G_Rep_MercyCrossing Auto Const Mandatory
	GlobalVariable Property TLM_G_MQ01_Done Auto Const Mandatory
	GlobalVariable Property TLM_G_MQ01_DebriefVariant Auto Const Mandatory
	GlobalVariable Property TLM_G_SQ01_EvidenceLevel Auto Const Mandatory
	GlobalVariable Property TLM_G_SQ01_Outcome Auto Const Mandatory
	GlobalVariable Property TLM_G_SQ01_YardAlerted Auto Const Mandatory
	GlobalVariable Property TLM_G_SQ01_VaneHasLedger Auto Const Mandatory
	GlobalVariable Property TLM_G_SQ01_HaskellScapegoated Auto Const Mandatory
EndGroup

Group Placed
	ReferenceAlias[] Property Everything Auto Const
	{Every alias of this quest: one for each reference the plugin places.}
	string[] Property EverythingNames Auto Const
	ReferenceAlias[] Property People Auto Const
	{The thirteen people among them.}
	string[] Property PeopleNames Auto Const
	ReferenceAlias[] Property CastFrom Auto Const
	{What is put where: the alias of this quest that holds the reference ...}
	ReferenceAlias[] Property CastInto Auto Const
	{... and the alias of TLM_MQ01 or TLM_SQ01 it is put into.}
	string[] Property CastNames Auto Const
	ReferenceAlias Property Alias_Marshal Auto Const Mandatory
	ReferenceAlias Property Alias_Dispatch Auto Const Mandatory
	ReferenceAlias Property Alias_Revolver Auto Const Mandatory
	ReferenceAlias Property Alias_Journal Auto Const Mandatory
	ReferenceAlias Property Alias_Ledger Auto Const Mandatory
	ReferenceAlias Property Alias_AmbushSight Auto Const Mandatory
	ReferenceAlias Property Alias_TownGate Auto Const Mandatory
	ReferenceAlias Property Alias_Nell Auto Const Mandatory
	ReferenceAlias Property Alias_Abel Auto Const Mandatory
	ReferenceAlias Property Alias_Dunmore Auto Const Mandatory
EndGroup

Group Forms
	Form Property DispatchItem Auto Const Mandatory
	{TLM_MISC_Dispatch}
	Form Property LedgerItem Auto Const Mandatory
	{TLM_BOOK_RailMaintLedger}
	Form Property JournalItem Auto Const Mandatory
	{TLM_BOOK_MarshalLog}
	Form Property Caps Auto Const
	{Caps001 from Fallout4.esm. None if it was not found: nothing is paid.}
	Form Property MarkerBase Auto Const
	{The game's plain marker. None if it was not found.}
	Form Property PipBoy Auto Const
	{The thing on the player's arm. A game started in the test room has none,
	and without it nothing picked up can be read. None if it was not found.}
	Form Property RevolverRounds Auto Const
	{What the marshal's revolver fires. None if no revolver was found.}
EndGroup

Group Lines
	Message Property SayBegin Auto Const
	Message Property SayDunmoreHold Auto Const
	Message Property SayDunmoreShare Auto Const
	Message Property SayDunmoreBreaks Auto Const
	Message Property SayDunmoreTurns Auto Const
	Message Property SayDunmoreDeal Auto Const
	Message Property SayDunmoreAfter Auto Const
	Message Property SayNellLive Auto Const
	Message Property SayNellSaved Auto Const
	Message Property SayNellWho Auto Const
	Message Property SayNellOffer Auto Const
	Message Property SayNellSavedAfter Auto Const
	Message Property SayNellEvaded Auto Const
	Message Property SayNellSilent Auto Const
	Message Property SayNellMissed Auto Const
	Message Property SayAbelLive Auto Const
	Message Property SayAbelSaved Auto Const
	Message Property SayCutterLive Auto Const
	Message Property SayPritchardNoCase Auto Const
	Message Property SayPritchardNoCaseAndMore Auto Const
	Message Property SayPritchardMark Auto Const
	Message Property SayPritchardCase Auto Const
	Message Property SayPritchardCaseAndMore Auto Const
	Message Property SayPritchardReported Auto Const
	Message Property SayDebriefSaved Auto Const
	Message Property SayDebriefEvaded Auto Const
	Message Property SayDebriefWitness Auto Const
	Message Property SayDebriefWitnessAbel Auto Const
	Message Property SayDebriefNoWitness Auto Const
	Message Property SayDebriefMissed Auto Const
	Message Property SayDebriefLost Auto Const
	Message Property SayPritchardHandOff Auto Const
	Message Property SayPritchardAfter Auto Const
	Message Property SayPritchardAfterAndMore Auto Const
	Message Property SayPikeHello Auto Const
	Message Property SayPikeBook Auto Const
	Message Property SayPikeAfter Auto Const
	Message Property SayPikeHaskell Auto Const
	Message Property SayVaneHello Auto Const
	Message Property SayVaneOffer Auto Const
	Message Property SayVanePaid Auto Const
	Message Property SayKeeneHello Auto Const
	Message Property SayKeeneNell Auto Const
	Message Property SayKeeneHaskell Auto Const
	Message Property SayTalbotGate Auto Const
	Message Property SayTalbotAfter Auto Const
	Message Property SayHaskell Auto Const
EndGroup

Group Preview
	Quest Property TLM_MercyBriefing Auto Const
	{TLM_MercyBriefing, with TLM:MercyBriefing on it: the optional Mercy
	briefing (ACT1-RUNTIME-001). None, or not that script: the section ends
	as it always did.}
	Quest Property TLM_Greenwater Auto Const
	{TLM_GW, with TLM:GreenwaterWalk on it: the Greenwater greybox
	(GREENWATER-STORY-001). None, or not that script: there is no travel
	point and no river report, and nothing else changes.}
	Quest Property TLM_RedHollow Auto Const
	Quest Property TLM_NightMail Auto Const
	{TLM_NM, with TLM:NightMailWalk on it: the Night Mail greybox
	(NIGHT-MAIL-STORY-001). None, or not that script: there is no travel
	point to Iron Junction and no rail report, and nothing else changes.}
EndGroup

; ----------------------------------------------------------------- constants

; Who is who: the numbers TLM:Act1Talk carries on each alias.
int WHO_DUNMORE = 1 Const
int WHO_NELL = 2 Const
int WHO_ABEL = 3 Const
int WHO_CUTTER = 4 Const
int WHO_PRITCHARD = 5 Const
int WHO_PIKE = 6 Const
int WHO_VANE = 7 Const
int WHO_KEENE = 8 Const
int WHO_TALBOT = 9 Const
int WHO_HASKELL = 10 Const
int WHO_REVOLVER = 20 Const

; As in TLM:MQ01Quest.
int OUT_NONE = 0 Const
int OUT_SAVED = 1 Const
int OUT_EVADED = 2 Const
int OUT_EXPLOITED = 3 Const
int METHOD_DEAL = 1 Const
int V_SAVED = 1 Const
int V_EVADED = 2 Const
int V_WITNESS = 3 Const
int V_NOWITNESS = 4 Const
int V_MISSED = 5 Const

; What this script gives, and the quests know nothing of.
int NELL_THANKS = 30 Const
int DEAL_SHARE = 20 Const
int ROUNDS = 6 Const

; How far from where it was placed a person may be and still count as having
; stayed. (The lines written to the log say "64 units" in words.)
float STAY_WITHIN = 64.0 Const
; How long the people may take to appear, and how long the step that waits for
; them may take before the self-test's watchdog ends the scenario. On
; 2026-11-13 Enable took 18 and 20 seconds to come back for a person of the
; plugin's own; here there are thirteen, and whether the game brings them
; in side by side or one after another is not known: thirteen times twenty
; seconds is four and a half minutes, so they are given seven.
float PEOPLE_SECONDS = 420.0 Const
float PEOPLE_STEP_SECONDS = 520.0 Const
; How long a step that moves the player may take (one took 38 seconds).
float MOVE_SECONDS = 150.0 Const
; How far above a spot the navigation mesh is asked about it.
; (The lines written to the log say "150 units" in words.)
float PROBE_ABOVE = 150.0 Const

; -------------------------------------------------------------------- state

; The section has been set up for a person.
bool begun = false
; A conversation is open: a second one must not start beside it.
bool talking = false
; The audit is running: no box may open, because nobody is there to answer it.
bool quiet = false
bool nellThanked = false
bool roundsGiven = false
bool departureShown = false

; ================================================================== set-up

Function Begin()
	{For a person: sets the first section up and leaves the game to them.
	Called by TLM:Core when the runner on the PC asks for it
	(tools\win\Play-Act1.ps1). From the console, in the test room:
	cqf TLM_A1 Begin}
	If begun
		Return
	EndIf
	begun = true
	Debug.Trace("TLM_A1: setting up the first section")
	If !IsRunning()
		Start()
	EndIf
	If !TLM_MQ01.GetStageDone(10)
		TLM_MQ01.SetStage(10)
	EndIf
	TLM:MQ01Quest questScript = TLM_MQ01 as TLM:MQ01Quest
	If questScript
		questScript.RegisterDemoPresentation(Self)
	EndIf
	int unfilled = CastAll()
	ConfigurePritchardActivation()
	ConfigurePikeActivation()
 ConfigureRoadVoiceActivation()
	SwitchOn()
	int missing = WaitForPeople(PEOPLE_SECONDS, None)
	SettleMarshal()
	PreservePritchardVoice()
	OpenTheRoad()
	WearPipBoy()
	OpenGreenwater()
	OpenNightMail()
	OpenRedHollow()
	OpenFourFlags()
	OpenBlackLedger()
	Debug.Trace("TLM_A1: the first section is set up; aliases left empty: " + unfilled + ", people not there: " + missing)
	If SayBegin
		SayBegin.Show()
	EndIf
EndFunction

bool Function CanReadGuide()
	{Explicit help only during a manual demo, never during the unattended audit.}
	Return begun && !quiet && !talking
EndFunction

Function CuttersDeparted(int aiLivingGone)
	{A nonmodal manual-demo cue after MQ01 verifies actual living-gang cleanup.
	Never a death cue, audit box, encounter resolution or extra stage.}
	If !begun || quiet || departureShown || aiLivingGone <= 0
		Return
	EndIf
	departureShown = true
	If aiLivingGone == 1
		Debug.Notification("The surviving Cutter has left the caravan road.")
	Else
		Debug.Notification("The surviving Cutters have left the caravan road.")
	EndIf
	Debug.Trace("TLM_A1: town cleanup verified living Cutters gone: " + aiLivingGone)
EndFunction

; The owned original Pritchard uses this section's custom activation dialogue.
; Keep the prompt/OnActivate event, but suppress generic native dialogue startup.
Function ConfigurePritchardActivation()
 If !Alias_Pritchard || !BlackLedgerOriginalSheriff
  Debug.Trace("TLM_A1: Pritchard activation unchanged: missing original binding")
  Return
 EndIf
 Actor sheriff = Alias_Pritchard.GetActorReference()
 If !sheriff || sheriff != BlackLedgerOriginalSheriff || sheriff.IsDead()
  Debug.Trace("TLM_A1: Pritchard activation unchanged: original alias/living check failed")
  Return
 EndIf
 sheriff.BlockActivation(true,false)
 Debug.Trace("TLM_A1: Pritchard custom activation blocked=" + sheriff.IsActivationBlocked() + "; prompt and OnActivate retained")
EndFunction

; Optional book recording: reserve only the original Ada's custom activation.
Function ConfigurePikeActivation()
 If !RecordedPikeBook || !Alias_Pike || !OpeningOriginalPike
  Return
 EndIf
 Actor pike = Alias_Pike.GetActorReference()
 If !pike || pike != OpeningOriginalPike || pike.IsDead()
  Debug.Trace("TLM_A1: Pike activation unchanged: original alias/living check failed")
  Return
 EndIf
 pike.BlockActivation(true,false)
 Debug.Trace("TLM_A1: Pike custom activation blocked=" + pike.IsActivationBlocked() + "; prompt and OnActivate retained")
EndFunction

int Function CastAll()
	{Puts each placed reference into the alias of the real quests that is
	meant for it. Returns how many of those aliases do not hold it afterwards.}
	int unfilled = 0
	int i = 0
	While i < CastFrom.Length
		ObjectReference placedRef = CastFrom[i].GetReference()
		If placedRef
			CastInto[i].ForceRefTo(placedRef)
		EndIf
		If !placedRef || CastInto[i].GetReference() != placedRef
			unfilled += 1
			Debug.Trace("TLM_A1: not put where it belongs: " + CastNames[i])
		EndIf
		i += 1
	EndWhile
	Return unfilled
EndFunction

Function SwitchOn()
	{Switches on the people and the things the plugin placed for the section,
	and does not wait for them. The two boxes stay off until the people are
	there (OpenTheRoad): a player who wandered into the place the ambush is
	seen from before there was an ambush would start its clock for nothing.}
	int i = 0
	While i < Everything.Length
		If Everything[i] != Alias_AmbushSight && Everything[i] != Alias_TownGate
			ObjectReference thing = Everything[i].GetReference()
			If thing
				thing.EnableNoWait()
			EndIf
		EndIf
		i += 1
	EndWhile
EndFunction

Function OpenTheRoad()
	{Switches on the two boxes: the place the ambush is seen from, and the town
	gate. Comes back when both are on, or after five seconds.}
	ObjectReference sight = Alias_AmbushSight.GetReference()
	ObjectReference gate = Alias_TownGate.GetReference()
	If sight
		sight.EnableNoWait()
	EndIf
	If gate
		gate.EnableNoWait()
	EndIf
	int tries = 0
	While tries < 20 && ((sight && sight.IsDisabled()) || (gate && gate.IsDisabled()))
		Utility.Wait(0.25)
		tries += 1
	EndWhile
EndFunction

int Function WaitForPeople(float afSeconds, float[] afSeenAfter)
	{Waits until every person is switched on and can be seen, or for so many
	seconds. Returns how many are still not there. If it is given an array as
	long as the list of people, it writes into it after how many seconds each
	was first there (-1: never).}
	float began = Utility.GetCurrentRealTime()
	bool timing = afSeenAfter && afSeenAfter.Length == People.Length
	int i = 0
	If timing
		While i < People.Length
			afSeenAfter[i] = -1.0
			i += 1
		EndWhile
	EndIf
	int missing = People.Length
	While missing > 0 && Utility.GetCurrentRealTime() - began < afSeconds
		missing = 0
		i = 0
		While i < People.Length
			ObjectReference person = People[i].GetReference()
			If !person || person.IsDisabled() || !person.Is3DLoaded()
				missing += 1
			ElseIf person == Alias_Marshal.GetReference()
				SettleMarshal()
				If timing && afSeenAfter[i] < 0.0
					afSeenAfter[i] = Utility.GetCurrentRealTime() - began
				EndIf
			ElseIf timing && afSeenAfter[i] < 0.0
				afSeenAfter[i] = Utility.GetCurrentRealTime() - began
			EndIf
			i += 1
		EndWhile
		If missing > 0
			Utility.Wait(1.0)
		EndIf
	EndWhile
	Return missing
EndFunction

Function WearPipBoy()
	{A game started in the test room has nothing on the player's arm, and
	without it the quest's entries and anything picked up cannot be read.}
	Actor player = Game.GetPlayer()
	If PipBoy && player.GetItemCount(PipBoy) == 0
		player.AddItem(PipBoy, 1, true)
		player.EquipItem(PipBoy, false, true)
	EndIf
EndFunction

; ==================================================================== talk

Function Spoken(int aiWho, Actor akWho)
	{Called by TLM:Act1Talk when the player activates somebody.}
	If TLM_FourFlags && (TLM_FourFlags as TLM:FourFlagsWalk).IsVisiting(akWho)
		Return
	EndIf
	; The same living earlier-road actor can be staged at Red Hollow. Its new
	; alias owns that activation there; neither old encounter nor alias is reset.
	If TLM_RedHollow && (TLM_RedHollow as TLM:RedHollowWalk).BorrowsActor(akWho)
		Return
	EndIf
	If TLM_BlackLedger
		TLM:BlackLedgerWalk ledger = TLM_BlackLedger as TLM:BlackLedgerWalk
		If ledger && ledger.IsVisiting(akWho)
			If aiWho == WHO_PRITCHARD
				ledger.OfferSheriff(akWho)
			ElseIf aiWho == WHO_VANE
				ledger.OfferActor(akWho,1)
			EndIf
			Return
		EndIf
		If ledger && (aiWho == WHO_VANE || aiWho == WHO_HASKELL)
			int ledgerRole = 1
			If aiWho == WHO_HASKELL
				ledgerRole = 2
			EndIf
			If ledger.OfferActor(akWho,ledgerRole)
				Return
			EndIf
		EndIf
	EndIf
	; Nothing between the test and the claim calls into the game, so two
	; activations cannot both pass.
	If quiet || talking
		Return
	EndIf
	talking = true
	If akWho && !akWho.IsDead() && !akWho.IsInCombat() && TLM_MQ01.GetStageDone(10)
		If aiWho == WHO_DUNMORE
			TalkDunmore(akWho)
		ElseIf aiWho == WHO_NELL
			TalkNell()
		ElseIf aiWho == WHO_ABEL
			TalkAbel()
		ElseIf aiWho == WHO_CUTTER
			TalkCutter()
		ElseIf aiWho == WHO_PRITCHARD
			TalkPritchard(akWho)
		ElseIf aiWho == WHO_PIKE
			TalkPike(akWho)
		ElseIf aiWho == WHO_VANE
			TalkVane()
		ElseIf aiWho == WHO_KEENE
			TalkKeene()
		ElseIf aiWho == WHO_TALBOT
			TalkTalbot(akWho)
		ElseIf aiWho == WHO_HASKELL
			ShowLine(SayHaskell)
		EndIf
	EndIf
	talking = false
EndFunction

Function Taken(int aiWhat)
	{Called by TLM:Act1Talk when the player picks something up.}
	If aiWhat == WHO_REVOLVER && !roundsGiven
		roundsGiven = true
		; Six rounds with the marshal's revolver, whatever the game put in it.
		If RevolverRounds
			Actor player = Game.GetPlayer()
			int have = player.GetItemCount(RevolverRounds)
			If have < ROUNDS
				player.AddItem(RevolverRounds, ROUNDS - have)
			EndIf
		EndIf
	EndIf
EndFunction

int Function ShowLine(Message akLine)
	{Shows a line. Returns the button pressed; -1 if there was no line to show
	or it was not a box.}
	If !akLine
		Return -1
	EndIf
	Return akLine.Show()
EndFunction

bool Function Coin()
	{Stands for the speech check, whose difficulty the design leaves to the editor.}
	Return Utility.RandomInt(0, 1) == 1
EndFunction

int Function Outcome()
	Return TLM_G_CaravanOutcome.GetValueInt()
EndFunction

bool Function NellLives()
	Actor nell = Alias_Nell.GetActorReference()
	Return nell && !nell.IsDead()
EndFunction

bool Function CanDecide()
	{The side quest's case can be presented and nothing has been done with it:
	what its own script asks before it lets an outcome stand.}
	Return TLM_SQ01.GetStageDone(20) && TLM_G_SQ01_Outcome.GetValueInt() == 0
EndFunction

; ------------------------------------------------------------ Reese Dunmore

Function TalkDunmore(Actor speakerActor = None)
	{Design 8.1. The order of the buttons is the order in the plugin's message.}
	If Outcome() != OUT_NONE
		ShowLine(SayDunmoreAfter)
		Return
	EndIf
	If TLM_MQ01.GetStageDone(37)
		; The talking is over.
		Return
	EndIf
	If !TLM_MQ01.GetStageDone(30)
		; Speaking to him is meeting the ambush, however the player came at it.
		TLM_MQ01.SetStage(30)
	EndIf
	int answer = ShowOpeningRecording(SayDunmoreHold,speakerActor,RecordedDunmoreHold,4.88,WHO_DUNMORE)
	If answer == 0
		; "[Risk combat] Pritchard hangs road-takers. Leave."
		If Coin()
			ShowLine(SayDunmoreBreaks)
			TLM_MQ01.SetStage(31)
		Else
			ShowLine(SayDunmoreTurns)
			TLM_MQ01.SetStage(37)
		EndIf
	ElseIf answer == 1
		; "[Fight] Let them go."
		ShowLine(SayDunmoreTurns)
		TLM_MQ01.SetStage(37)
	ElseIf answer == 2
		; "What kind of share?"
		If ShowLine(SayDunmoreShare) == 0
			ShowLine(SayDunmoreDeal)
			TLM_MQ01.SetStage(33)
			; The share, if the deal is what the quest then made of it.
			If Caps && Outcome() == OUT_EXPLOITED && TLM_G_CaravanMethod.GetValueInt() == METHOD_DEAL
				Game.GetPlayer().AddItem(Caps, DEAL_SHARE)
			EndIf
		EndIf
		; A27: "[Leave] No deal. I'm leaving." closes this menu without
		; a stage, a share or hostility. The live hold-up still has its timer.
	ElseIf answer == 4
		CallSheriffHelp()
 ElseIf answer == 3 && HelpRoad().SheriffHelpPending
  HelpRoad().EndSheriffHelp()
	EndIf
	; "[Leave] I'm walking away.": the same non-escalating exit.
EndFunction

; ------------------------------------------------- the caravan and the gang

Function TalkNell()
	{Design 8.2.}
	int result = Outcome()
	If result == OUT_NONE
		ShowLine(SayNellLive)
	ElseIf result == OUT_SAVED
		If nellThanked
			ShowLine(SayNellSavedAfter)
		Else
			int answer = ShowLine(SayNellSaved)
			If answer == 2
				; "Who hit you?"
				ShowLine(SayNellWho)
				answer = ShowLine(SayNellOffer)
			EndIf
			If answer == 0 || answer == 1
				nellThanked = true
				If answer == 0 && Caps
					Game.GetPlayer().AddItem(Caps, NELL_THANKS)
				EndIf
			EndIf
		EndIf
	ElseIf result == OUT_EVADED
		; Whatever is answered changes nothing, as designed.
		ShowLine(SayNellEvaded)
	ElseIf result == OUT_EXPLOITED
		ShowLine(SayNellSilent)
	Else
		ShowLine(SayNellMissed)
	EndIf
EndFunction

Function TalkAbel()
	int result = Outcome()
	If result == OUT_NONE
		ShowLine(SayAbelLive)
	ElseIf result == OUT_SAVED
		ShowLine(SayAbelSaved)
	EndIf
EndFunction

Function TalkCutter()
	If Outcome() == OUT_NONE && !TLM_MQ01.GetStageDone(37)
		ShowLine(SayCutterLive)
	EndIf
EndFunction

; ---------------------------------------------------------- Owen Pritchard

Function TalkPritchard(Actor akWho = None)
	{Design 8.3: the dispatch, then what he makes of the road, then the three
	towns. Reporting the ledger to him is the side quest's route A.
	akWho is whoever was activated, passed on by Spoken; only the Mercy
	briefing after the chapter uses it. Called without it, this does what it
	always did.}
 If helpReturnDue
  If !ReturnHelpSheriff()
   Debug.Notification("Pritchard couldn't return to Mercy. Speak to him again when the road is clear.")
  EndIf
  Return
 EndIf

	bool more = CanDecide()
	TLM:MQ01Quest mainScript = TLM_MQ01 as TLM:MQ01Quest
	If mainScript
		mainScript.ResumeCaravanConsequences()
	EndIf
	If !TLM_MQ01.GetStageDone(20)
		int first = 0
		If more
			first = ShowLine(SayPritchardNoCaseAndMore)
		Else
			first = ShowLine(SayPritchardNoCase)
		EndIf
		If first == 3
			Report()
		Else
			ShowLine(SayPritchardMark)
		EndIf
		Return
	EndIf
	If !TLM_MQ01.GetStageDone(50)
		int second = 0
		If more
			second = ShowOpeningRecording(SayPritchardCaseAndMore,akWho,RecordedDispatchCase,9.5)
		Else
			second = ShowOpeningRecording(SayPritchardCase,akWho,RecordedDispatchCase,9.5)
		EndIf
		If second == 2
			Report()
			Return
		ElseIf second != 0
			; "Not yet."
			Return
		EndIf
		TLM_MQ01.SetStage(50)
	EndIf
	If !mainScript || !mainScript.WaitForDeliveryAcknowledgment()
		Debug.Notification("The caravan handover has not finished. Try again shortly; if it persists, restart this demo.")
		Return
	EndIf
	If !TLM_MQ01.GetStageDone(50)
		Return
	EndIf
 ; Acknowledged delivery is no longer an active target, even if the local offer is deferred.
 TLM_MQ01.SetObjectiveDisplayed(20,false)
	If !TLM_MQ01.GetStageDone(60)
		Debrief()
  If !OfferFirstBrakeInquiry(akWho,true)
   ShowOpeningRecording(HandOffLine(),akWho,RecordedRoadHandOff,12.5)
  EndIf
		TLM_MQ01.SetStage(60)
		Return
	EndIf
 If OfferFirstBrakeInquiry(akWho)
  Return
 EndIf
	If more
		; The side quest's report keeps its button and its place: 1. Only
		; an explicit Continue, 0, goes on to the briefing. No answer (-1)
		; and any other number close here, as they always did.
		int after = ShowLine(SayPritchardAfterAndMore)
		If after == 1
			Report()
		ElseIf after == 0
			AfterTheChapter(akWho)
		EndIf
	ElseIf !AfterTheChapter(akWho)
		ShowLine(SayPritchardAfter)
	EndIf
EndFunction

bool Function AfterTheChapter(Actor akWho)
	{What Pritchard has for the player once the chapter is over: the river
	report if Greenwater was finished and not yet reported, then what is owed
	of the Night Mail, otherwise the Mercy briefing. One conversation, inside this script's own claim on it.
	True if either took this activation.}
	int river = OfferRiverReport(akWho)
	If river == RIVER_REPORT_GIVEN || river == RIVER_REPORT_CLOSED
		; Given, or shown and come back with no valid answer: either way this conversation was the
		; report's. Nothing else is said in it.
		Return true
	EndIf
	; Nothing of the river was offered, or it was explicitly left for later: the rail, on the same terms.
	int rail = OfferRailReport(akWho)
	If rail == RIVER_REPORT_GIVEN || rail == RIVER_REPORT_CLOSED
		Return true
	EndIf
	int hollow = OfferHollowReport(akWho)
	If hollow == RIVER_REPORT_GIVEN || hollow == RIVER_REPORT_CLOSED
		Return true
	EndIf
	If TLM_BlackLedger
		TLM:BlackLedgerWalk ledger = TLM_BlackLedger as TLM:BlackLedgerWalk
		If ledger && ledger.OfferSheriff(akWho)
			Return true
		EndIf
	EndIf
	; Nothing was offered, or each was explicitly left for later: the briefing, as before.
	Return OfferBriefing(akWho)
EndFunction

bool Function CanVisitFair()
	Return begun && IsRunning() && !quiet && !talking
EndFunction

Actor Function FairActor(int role)
	int index = 18
	If role == 1
		index = 17
	ElseIf role == 2
		index = 19
	ElseIf role != 0
		Return None
	EndIf
	If !Everything || Everything.Length <= index || !Everything[index]
		Return None
	EndIf
	Return Everything[index].GetActorReference()
EndFunction

bool Function FairActorAvailable(Actor who)
	If !CanVisitFair() || !who
		Return false
	EndIf
	If TLM_BlackLedger && (TLM_BlackLedger as TLM:BlackLedgerWalk).IsVisiting(who)
		Return false
	EndIf
	If who == FairActor(0)
		TLM:GreenwaterWalk river = Greenwater()
		If river && !river.Road().SheriffVisitSafe()
			Return false
		EndIf
		If TLM_RedHollow
			TLM:RedHollowWalk hollow = TLM_RedHollow as TLM:RedHollowWalk
			If hollow && hollow.Road().CourtPending() != 0
				Return false
			EndIf
		EndIf
	EndIf
	Return true
EndFunction

Function OpenFourFlags()
	TLM:FourFlagsEntry adapter = TLM_FourFlagsEntry as TLM:FourFlagsEntry
	If adapter
		adapter.OpenFrom(Self)
	EndIf
EndFunction

TLM:GreenwaterWalk Function Greenwater()
	{The Greenwater greybox's script, if it is bound. None otherwise.}
	If !TLM_Greenwater
		Return None
	EndIf
	Return TLM_Greenwater as TLM:GreenwaterWalk
EndFunction

Function OpenGreenwater()
	{At set-up: the Mercy travel point is switched on. Nothing of Greenwater is.}
	TLM:GreenwaterWalk greybox = Greenwater()
	If greybox
		greybox.OpenDoor()
	EndIf
EndFunction

TLM:NightMailWalk Function NightMail()
	{The Night Mail greybox's script, if it is bound. None otherwise.}
	If !TLM_NightMail
		Return None
	EndIf
	Return TLM_NightMail as TLM:NightMailWalk
EndFunction

Function OpenNightMail()
	{At set-up: the Mercy travel point to Iron Junction is switched on. Nothing of Iron Junction is.}
	TLM:NightMailWalk greybox = NightMail()
	If greybox
		greybox.OpenDoor()
	EndIf
EndFunction

int Function OfferRailReport(Actor akWho)
	{After the chapter: what Pritchard is owed of the Night Mail
	(NIGHT-MAIL-STORY-001): the report of the road, the inspector's stamp, the
	yard's change. The same four answers as the river report, and the same
	numbers. RIVER_REPORT_NONE, with nothing shown or changed, if the greybox
	is not bound, nobody was passed on, or the main quest is not complete.}
	If !akWho
		Return RIVER_REPORT_NONE
	EndIf
	If !TLM_MQ01.GetStageDone(100) || TLM_G_MQ01_Done.GetValueInt() != 1
		Return RIVER_REPORT_NONE
	EndIf
	TLM:NightMailWalk greybox = NightMail()
	If !greybox
		Return RIVER_REPORT_NONE
	EndIf
	Return greybox.OfferReport(akWho)
EndFunction

; What TLM:GreenwaterWalk.OfferReport answers. The same numbers as there; a test compares them.
int RIVER_REPORT_NONE = 0 Const
int RIVER_REPORT_GIVEN = 1 Const
int RIVER_REPORT_LATER = 2 Const
int RIVER_REPORT_CLOSED = 3 Const

int Function OfferRiverReport(Actor akWho)
	{After the chapter and after the Greenwater road: Pritchard hears what
	became of the grain (GREENWATER-STORY-001). RIVER_REPORT_NONE, with nothing
	shown or changed, if the greybox is not bound, nobody was passed on, the
	main quest is not complete, or there is nothing to report. Otherwise what
	the greybox says became of the offer: given, explicitly left for later, or
	shown and closed with no valid answer.}
	If !akWho
		Return RIVER_REPORT_NONE
	EndIf
	If !TLM_MQ01.GetStageDone(100) || TLM_G_MQ01_Done.GetValueInt() != 1
		Return RIVER_REPORT_NONE
	EndIf
	TLM:GreenwaterWalk greybox = Greenwater()
	If !greybox
		Return RIVER_REPORT_NONE
	EndIf
	Return greybox.OfferReport(akWho)
EndFunction

TLM:MercyBriefing Function Briefing()
	{The Mercy briefing's script, if it is bound. None otherwise.}
	If !TLM_MercyBriefing
		Return None
	EndIf
	Return TLM_MercyBriefing as TLM:MercyBriefing
EndFunction

Message Function HandOffLine()
	{The hand-off, with the briefing's footer if the briefing is bound.}
	TLM:MercyBriefing brief = Briefing()
	If brief
		Return brief.HandOffLineOr(SayPritchardHandOff)
	EndIf
	Return SayPritchardHandOff
EndFunction

bool Function OfferBriefing(Actor akWho)
	{After the chapter: the Mercy briefing (ACT1-RUNTIME-001), given by
	whoever was activated. True if it took this activation. False, with
	nothing shown or changed, if it is not bound, nobody was passed on, or
	the main quest is not complete with its delivery acknowledged; what
	exactly it requires is the briefing's own script's to decide, and it
	reads all of it again itself.}
	If !akWho
		Return false
	EndIf
	If !TLM_MQ01.GetStageDone(100) || TLM_G_MQ01_Done.GetValueInt() != 1
		Return false
	EndIf
	TLM:MercyBriefing brief = Briefing()
	If !brief
		Return false
	EndIf
	Return brief.Offer(akWho)
EndFunction

Function Debrief()
	{What Pritchard makes of the road, by the variant the main quest worked
	out at the delivery, and the answer if he asks for one. Saying nothing is
	always allowed: the quest then records silence.}
	int variant = TLM_G_MQ01_DebriefVariant.GetValueInt()
	If variant == V_SAVED
		ShowLine(SayDebriefSaved)
	ElseIf variant == V_EVADED
		int watched = ShowLine(SayDebriefEvaded)
		If watched == 0
			TLM_MQ01.SetStage(51)
		ElseIf watched == 1
			TLM_MQ01.SetStage(52)
		EndIf
	ElseIf variant == V_WITNESS
		int told = 0
		If NellLives()
			told = ShowLine(SayDebriefWitness)
		Else
			; The one left to speak is Abel Rudd.
			told = ShowLine(SayDebriefWitnessAbel)
		EndIf
		If told == 0
			TLM_MQ01.SetStage(53)
		ElseIf told == 1
			TLM_MQ01.SetStage(54)
		ElseIf told == 2
			TLM_MQ01.SetStage(55)
		EndIf
	ElseIf variant == V_NOWITNESS
		ShowLine(SayDebriefNoWitness)
	ElseIf variant == V_MISSED
		ShowLine(SayDebriefMissed)
	Else
		ShowLine(SayDebriefLost)
	EndIf
EndFunction

Function Report()
	TLM_SQ01.SetStage(41)
	If TLM_G_SQ01_Outcome.GetValueInt() == 1
		ShowLine(SayPritchardReported)
	EndIf
EndFunction

; ---------------------------------------------------------------- the town

Function TalkPike(Actor speakerActor = None)
 If OfferAdaBrakeInquiry(speakerActor)
  Return
 EndIf
 TalkPikeExisting(speakerActor)
EndFunction

Function TalkPikeExisting(Actor speakerActor = None)
	If TLM_G_SQ01_HaskellScapegoated.GetValueInt() == 1
		ShowLine(SayPikeHaskell)
	ElseIf TLM_SQ01.GetStageDone(14)
		ShowLine(SayPikeAfter)
	ElseIf TLM_SQ01.GetStageDone(10) && TLM_G_SQ01_Outcome.GetValueInt() == 0
		If ShowOpeningRecording(SayPikeBook,speakerActor,RecordedPikeBook,8.16,WHO_PIKE) == 0
			TLM_SQ01.SetStage(14)
		EndIf
	Else
		ShowLine(SayPikeHello)
	EndIf
EndFunction

Function TalkVane()
	If TLM_G_SQ01_VaneHasLedger.GetValueInt() == 1
		ShowLine(SayVanePaid)
	ElseIf CanDecide()
		If ShowLine(SayVaneOffer) == 0
			TLM_SQ01.SetStage(45)
		EndIf
	Else
		ShowLine(SayVaneHello)
	EndIf
EndFunction

Function TalkKeene()
	int result = Outcome()
	If TLM_G_SQ01_HaskellScapegoated.GetValueInt() == 1
		ShowLine(SayKeeneHaskell)
	ElseIf TLM_MQ01.GetStageDone(40) && result != OUT_NONE && result != OUT_SAVED && NellLives()
		ShowLine(SayKeeneNell)
	Else
		ShowLine(SayKeeneHello)
	EndIf
EndFunction

Function TalkTalbot(Actor speakerActor = None)
	If TLM_MQ01.GetStageDone(50)
		ShowLine(SayTalbotAfter)
	Else
		ShowOpeningRecording(SayTalbotGate,speakerActor,RecordedTalbotGate,5.12,WHO_TALBOT)
	EndIf
EndFunction

; ============================================================== scenario 12

Function Audit(TLM:SelfTest akTest)
	quiet = true
	Actor playerRef = Game.GetPlayer()
	akTest.Note("act1: the player begins at " + Where(playerRef))

	; ---- 1. This quest starts and holds what the plugin placed.
	akTest.Step("starting the first section's quest")
	bool started = Start()
	akTest.Note("act1: Start returned " + started)
	akTest.CheckTrue("act1: the first section's quest runs once it has been started", IsRunning())
	bool hasRevolver = Alias_Revolver.GetReference() != None
	int absent = 0
	int i = 0
	While i < Everything.Length
		If !Everything[i].GetReference() && Everything[i] != Alias_Revolver
			absent += 1
			akTest.Note("act1: nothing is placed for " + EverythingNames[i])
		EndIf
		i += 1
	EndWhile
	akTest.CheckInt("act1: how many of the " + Everything.Length + " things and people placed for the section this quest does not hold (the revolver aside)", absent, 0)
	If !hasRevolver
		akTest.Note("act1: the game has no revolver by any of the names the build looked for, so none is placed, and stage 15 is never set: the chapter allows that")
	EndIf

	; Where the plugin put each person: all are still switched off.
	float[] placedX = new float[People.Length]
	float[] placedY = new float[People.Length]
	float[] placedZ = new float[People.Length]
	int stillOn = 0
	i = 0
	While i < People.Length
		ObjectReference person = People[i].GetReference()
		If person
			placedX[i] = person.GetPositionX()
			placedY[i] = person.GetPositionY()
			placedZ[i] = person.GetPositionZ()
			If !person.IsDisabled()
				stillOn += 1
			EndIf
		EndIf
		i += 1
	EndWhile
	akTest.CheckInt("act1: how many of the people are switched on before the section is set up", stillOn, 0)

	; ---- 2. The main quest starts, and what is placed is put into the two
	; quests' aliases.
	akTest.Reach(TLM_MQ01, 10)
	akTest.CheckTrue("act1: the main quest runs", TLM_MQ01.IsRunning())
	akTest.CheckTrue("act1: the side quest runs", TLM_SQ01.IsRunning())
	akTest.Step("putting what is placed into the two quests' aliases")
	int unfilled = CastAll()
	int allowed = 0
	If !hasRevolver
		allowed = 1
	EndIf
	akTest.CheckInt("act1: how many of the " + CastFrom.Length + " aliases of the two quests do not hold what was put into them (the revolver's aside)", unfilled - allowed, 0)

	; ---- 3. Everything is switched on.
	akTest.Step("switching on what is placed, and waiting for the people", PEOPLE_STEP_SECONDS)
	float[] seenAfter = new float[People.Length]
	SwitchOn()
	int missing = WaitForPeople(PEOPLE_SECONDS, seenAfter)
	i = 0
	While i < People.Length
		If seenAfter[i] < 0.0
			akTest.Note("act1: " + PeopleNames[i] + " was not there after " + PEOPLE_SECONDS + " seconds")
		Else
			akTest.Note("act1: " + PeopleNames[i] + " was there after " + seenAfter[i] + " seconds")
		EndIf
		i += 1
	EndWhile
	akTest.CheckInt("act1: how many of the thirteen people are not there once everything has been switched on", missing, 0)
	akTest.Step("switching on the two boxes, now that the people are there")
	OpenTheRoad()
	int thingsOff = 0
	i = 0
	While i < Everything.Length
		ObjectReference thing = Everything[i].GetReference()
		If thing && thing.IsDisabled()
			thingsOff += 1
			akTest.Note("act1: still switched off: " + EverythingNames[i])
		EndIf
		i += 1
	EndWhile
	akTest.CheckInt("act1: how many of the things and people are still switched off", thingsOff, 0)

	Actor marshal = Alias_Marshal.GetActorReference()
	akTest.CheckTrue("act1: the marshal is dead when the loaded section has been set up", marshal && marshal.IsDead())
	If marshal && !marshal.IsDead()
		akTest.Step("marshal death setup did not finish; not issuing a second death transition")
	EndIf
	int dead = 0
	i = 0
	While i < People.Length
		Actor one = People[i].GetActorReference()
		If one && one != marshal && one.IsDead()
			dead += 1
			akTest.Note("act1: dead when the section has been set up: " + PeopleNames[i])
		EndIf
		i += 1
	EndWhile
	akTest.CheckInt("act1: how many of the other twelve are dead", dead, 0)

	; ---- 4. Six seconds on, the living stand where the plugin put them.
	akTest.Step("watching the people for six seconds")
	Utility.Wait(6.0)
	int strayed = 0
	i = 0
	While i < People.Length
		Actor who = People[i].GetActorReference()
		If who && !who.IsDead()
			float off = Away(who, placedX[i], placedY[i], placedZ[i])
			If off > STAY_WITHIN
				strayed += 1
				akTest.Note("act1: " + PeopleNames[i] + " is " + off + " from where it was placed, at " + Where(who) + "; package " + who.GetCurrentPackage() + ", sit state " + who.GetSitState() + ", in combat = " + who.IsInCombat())
			EndIf
		EndIf
		i += 1
	EndWhile
	akTest.CheckInt("act1: how many of the living are more than 64 units from where they were placed, six seconds on", strayed, 0)
	akTest.Note("act1: the player is in combat once everybody is there = " + playerRef.IsInCombat())

	; ---- 5. What can be picked up.
	akTest.CheckFalse("act1: stage 20 is set before the dispatch has been picked up", TLM_MQ01.GetStageDone(20))
	ObjectReference dispatch = Alias_Dispatch.GetReference()
	If dispatch
		akTest.Step("having the player pick the dispatch up")
		; Asked before it is picked up: something in a pocket is nowhere.
		float dispatchAway = playerRef.GetDistance(dispatch)
		bool took = dispatch.Activate(playerRef)
		WaitForStage(TLM_MQ01, 20)
		akTest.Note("act1: Activate on the dispatch from " + dispatchAway + " away returned " + took + "; the player has " + playerRef.GetItemCount(DispatchItem) + ", stage 20 set = " + TLM_MQ01.GetStageDone(20))
		If !TLM_MQ01.GetStageDone(20)
			; Another way for it to reach the player, to tell a pick-up that
			; failed from a script that did not hear one.
			akTest.Step("moving the dispatch into the player's inventory by script")
			playerRef.AddItem(dispatch)
			WaitForStage(TLM_MQ01, 20)
			akTest.Note("act1: after AddItem of the dispatch: the player has " + playerRef.GetItemCount(DispatchItem) + ", stage 20 set = " + TLM_MQ01.GetStageDone(20))
		EndIf
	EndIf
	akTest.CheckTrue("act1: the dispatch, picked up, sets stage 20 of the main quest (the game's own script on the alias)", TLM_MQ01.GetStageDone(20))
	akTest.CheckInt("act1: how many dispatches the player carries", playerRef.GetItemCount(DispatchItem), 1)
	akTest.CheckTrue("act1: the objective to take the dispatch to Pritchard is displayed", TLM_MQ01.IsObjectiveDisplayed(20))

	; The two papers go into the player's inventory by script. Activating a
	; book opens it to be read, and nobody is there to close it.
	TakePaper(akTest, playerRef, Alias_Ledger, LedgerItem, 10, "the maintenance ledger")
	TakePaper(akTest, playerRef, Alias_Journal, JournalItem, 13, "the marshal's journal")
	akTest.CheckInt("act1: the evidence level with the ledger and the journal", TLM_G_SQ01_EvidenceLevel.GetValueInt(), 1)
	akTest.CheckFalse("act1: papers alone do not finish the wreck comparison", TLM_SQ01.GetStageDone(20))
	; Simulated physical observation, not native inspection proof.
	akTest.Reach(TLM_SQ01, 11)
	WaitForStage(TLM_SQ01, 20)
	akTest.CheckTrue("act1: the side quest's case can be presented (its stage 20)", TLM_SQ01.GetStageDone(20))

	ObjectReference revolver = Alias_Revolver.GetReference()
	If revolver
		akTest.Step("having the player pick the revolver up")
		bool tookRevolver = revolver.Activate(playerRef)
		WaitForStage(TLM_MQ01, 15)
		akTest.Note("act1: Activate on the revolver returned " + tookRevolver + "; stage 15 set = " + TLM_MQ01.GetStageDone(15))
		If !TLM_MQ01.GetStageDone(15)
			; As for the dispatch: another way for it to reach the player, to
			; tell a pick-up that failed from a script that did not hear one.
			akTest.Step("moving the revolver into the player's inventory by script")
			playerRef.AddItem(revolver)
			WaitForStage(TLM_MQ01, 15)
			akTest.Note("act1: after AddItem of the revolver: stage 15 set = " + TLM_MQ01.GetStageDone(15))
		EndIf
		akTest.CheckTrue("act1: the revolver, picked up, sets stage 15 of the main quest", TLM_MQ01.GetStageDone(15))
		Utility.Wait(1.0)
		If RevolverRounds
			akTest.CheckTrue("act1: the player has six rounds or more for the revolver", playerRef.GetItemCount(RevolverRounds) >= ROUNDS)
			akTest.Note("act1: rounds for the revolver the player has: " + playerRef.GetItemCount(RevolverRounds))
		Else
			akTest.Note("act1: what the revolver fires was not found when the plugin was built, so no rounds are given with it")
		EndIf
	EndIf

	; ---- 6. The ambush.
	EnterBox(akTest, playerRef, Alias_AmbushSight, 30, "the place the ambush is seen from")
	akTest.CheckInt("act1: the outcome while the ambush is live", Outcome(), 0)

	; ---- 7. The Cutter lead, killed by the player.
	Actor lead = Alias_Dunmore.GetActorReference()
	If lead
		akTest.Step("killing the Cutter lead, with the player as the killer")
		lead.Kill(playerRef)
		WaitForStage(TLM_MQ01, 31)
		WaitForGlobal(TLM_G_CaravanOutcome, OUT_SAVED)
	EndIf
	akTest.CheckTrue("act1: the Cutter lead's death sets stage 31", TLM_MQ01.GetStageDone(31))
	akTest.CheckInt("act1: the outcome after the lead's death (1 is the wagon saved)", Outcome(), 1)
	akTest.Note("act1: the player is in combat after the killing = " + playerRef.IsInCombat())

	; ---- 8. The town gate.
	EnterBox(akTest, playerRef, Alias_TownGate, 40, "the town gate")
	WaitForGlobal(TLM_G_CaravanAliveAtMercy, 1)
	akTest.CheckInt("act1: Nell Fenwick counted alive at Mercy Crossing", TLM_G_CaravanAliveAtMercy.GetValueInt(), 1)
	int cuttersLeft = 0
	TLM:MQ01Quest mainQuest = TLM_MQ01 as TLM:MQ01Quest
	If mainQuest
		cuttersLeft = StillThere(mainQuest.Alias_CutterLead) + StillThere(mainQuest.Alias_CutterA) + StillThere(mainQuest.Alias_CutterB) + StillThere(mainQuest.Alias_CutterC)
	Else
		akTest.Fail("act1: the main quest's script is not on the main quest")
	EndIf
	akTest.CheckInt("act1: how many of the four Cutters are still there after the town gate", cuttersLeft, 0)
	akTest.Note("act1: the player is in combat at the town gate = " + playerRef.IsInCombat())

	; ---- 9. The delivery and the hand-off, as Pritchard's buttons set them.
	akTest.Reach(TLM_MQ01, 50)
	akTest.CheckTrue("act1: the objective is completed by the delivery", TLM_MQ01.IsObjectiveCompleted(20))
	akTest.CheckInt("act1: how many dispatches the player carries after the delivery", playerRef.GetItemCount(DispatchItem), 0)
	akTest.CheckInt("act1: the town's regard after the delivery", TLM_G_Rep_MercyCrossing.GetValueInt(), 2)
	akTest.CheckInt("act1: which debrief Pritchard gives (1 is the wagon saved)", TLM_G_MQ01_DebriefVariant.GetValueInt(), 1)
	akTest.Reach(TLM_MQ01, 60)
	akTest.CheckTrue("act1: the chapter is completed", TLM_MQ01.IsCompleted())
	akTest.CheckInt("act1: the chapter is marked done", TLM_G_MQ01_Done.GetValueInt(), 1)

	; ---- 10. The side quest: Ada Pike's parts book, then reported.
	akTest.Reach(TLM_SQ01, 14)
	akTest.CheckInt("act1: the evidence level with Pike's parts book as well", TLM_G_SQ01_EvidenceLevel.GetValueInt(), 2)
	akTest.Reach(TLM_SQ01, 41)
	akTest.CheckInt("act1: the side quest's outcome (1 is reported)", TLM_G_SQ01_Outcome.GetValueInt(), 1)
	akTest.CheckInt("act1: the yard alerted", TLM_G_SQ01_YardAlerted.GetValueInt(), 1)
	akTest.CheckTrue("act1: the side quest is completed", TLM_SQ01.IsCompleted())

	; ==== Nothing below is scored. Every step from here on is one that the
	; watchdog reports as a fact about the game if it does not come back.

	; ---- 11. Where the navigation mesh says each person's spot is.
	If MarkerBase
		akTest.Step("making a marker to ask the navigation mesh with", 45.0, true)
		ObjectReference probe = playerRef.PlaceAtMe(MarkerBase)
		i = 0
		While i < People.Length && probe
			If People[i].GetReference()
				akTest.Step("asking the navigation mesh about the spot of " + PeopleNames[i], MOVE_SECONDS, true)
				probe.SetPosition(placedX[i], placedY[i], placedZ[i] + PROBE_ABOVE)
				probe.MoveToNearestNavmeshLocation()
				float offX = probe.GetPositionX() - placedX[i]
				float offY = probe.GetPositionY() - placedY[i]
				akTest.Note("act1: the navigation mesh, asked from 150 units above the spot of " + PeopleNames[i] + ", answers " + Math.sqrt(offX * offX + offY * offY) + " to the side of it and " + (probe.GetPositionZ() - placedZ[i]) + " above it")
			EndIf
			i += 1
		EndWhile
		If probe
			akTest.Step("removing the marker", 45.0, true)
			probe.Disable()
			probe.Delete()
		EndIf
	Else
		akTest.Note("act1: no marker base was found when the plugin was built, so the navigation mesh was not asked about the spots")
	EndIf
EndFunction

Function TakePaper(TLM:SelfTest akTest, Actor akPlayer, ReferenceAlias akPaper, Form akItem, int aiStage, string asName)
	{Moves a placed paper into the player's inventory and waits for the stage
	of the side quest that the game's own script on its alias should set.}
	ObjectReference paper = akPaper.GetReference()
	akTest.CheckFalse("act1: stage " + aiStage + " of the side quest is set before the player has " + asName, TLM_SQ01.GetStageDone(aiStage))
	If paper
		akTest.Step("moving " + asName + " into the player's inventory")
		akPlayer.AddItem(paper)
		WaitForStage(TLM_SQ01, aiStage)
		akTest.Note("act1: with " + asName + " moved to the player, the player has " + akPlayer.GetItemCount(akItem))
	EndIf
	akTest.CheckTrue("act1: " + asName + ", in the player's hands, sets stage " + aiStage + " of the side quest (the game's own script on the alias)", TLM_SQ01.GetStageDone(aiStage))
EndFunction

Function EnterBox(TLM:SelfTest akTest, Actor akPlayer, ReferenceAlias akBox, int aiStage, string asName)
	{Moves the player into the middle of a placed box and waits for the stage
	of the main quest that the game's own script on its alias should set.}
	ObjectReference box = akBox.GetReference()
	akTest.CheckFalse("act1: stage " + aiStage + " is set before the player has entered " + asName, TLM_MQ01.GetStageDone(aiStage))
	If box
		akTest.Step("moving the player into " + asName, MOVE_SECONDS)
		akPlayer.MoveTo(box)
		WaitForStage(TLM_MQ01, aiStage)
		akTest.Note("act1: after the move the player is at " + Where(akPlayer) + ", " + akPlayer.GetDistance(box) + " from the middle of " + asName)
	EndIf
	akTest.CheckTrue("act1: entering " + asName + " sets stage " + aiStage + " of the main quest (the game's own script on the alias)", TLM_MQ01.GetStageDone(aiStage))
EndFunction

; ----------------------------------------------------------------- helpers

int Function StillThere(ReferenceAlias akWho)
	{1 if the alias holds somebody who is not switched off, otherwise 0.}
	ObjectReference who = akWho.GetReference()
	If who && !who.IsDisabled()
		Return 1
	EndIf
	Return 0
EndFunction

float Function Away(ObjectReference akRef, float afX, float afY, float afZ)
	float dx = akRef.GetPositionX() - afX
	float dy = akRef.GetPositionY() - afY
	float dz = akRef.GetPositionZ() - afZ
	Return Math.sqrt(dx * dx + dy * dy + dz * dz)
EndFunction

string Function Where(ObjectReference akRef)
	Return "(" + akRef.GetPositionX() + ", " + akRef.GetPositionY() + ", " + akRef.GetPositionZ() + ")"
EndFunction

Function WaitForStage(Quest akQuest, int aiStage)
	{Waits until the quest reports the stage, or five seconds.}
	int tries = 0
	While !akQuest.GetStageDone(aiStage) && tries < 20
		Utility.Wait(0.25)
		tries += 1
	EndWhile
EndFunction

Function WaitForGlobal(GlobalVariable akGlobal, int aiValue)
	{Waits until the global holds the value, or five seconds: a stage reads as
	set before its handler has written what it writes.}
	int tries = 0
	While akGlobal.GetValueInt() != aiValue && tries < 20
		Utility.Wait(0.25)
		tries += 1
	EndWhile
EndFunction

Function OpenRedHollow()
	If TLM_RedHollow
		(TLM_RedHollow as TLM:RedHollowWalk).OpenDoor()
	EndIf
EndFunction

int Function OfferHollowReport(Actor akWho)
	If !akWho || !TLM_RedHollow || !TLM_MQ01.GetStageDone(100) || TLM_G_MQ01_Done.GetValueInt() != 1
		Return RIVER_REPORT_NONE
	EndIf
	If !(TLM_RedHollow as TLM:RedHollowWalk).OpenDoor()
		Return RIVER_REPORT_NONE
	EndIf
	Return (TLM_RedHollow as TLM:RedHollowWalk).OfferReport(akWho)
EndFunction

Actor Function BlackLedgerActor(int role)
	ObjectReference original = BlackLedgerOriginalSheriff
	int index = 18
	If role == 1
		original = BlackLedgerOriginalVane
		index = 20
	ElseIf role == 2
		original = BlackLedgerOriginalHaskell
		index = 22
	ElseIf role != 0
		Return None
	EndIf
	If !original || !Everything || Everything.Length <= index || !Everything[index] || Everything[index].GetReference() != original
		Return None
	EndIf
	Return original as Actor
EndFunction

Function OpenBlackLedger()
	TLM:BlackLedgerEntry adapter = TLM_BlackLedgerEntry as TLM:BlackLedgerEntry
	If adapter
		adapter.OpenFrom(Self)
	EndIf
EndFunction

Function PreservePritchardVoice()
	Actor sheriff = Alias_Pritchard.GetActorReference()
	If sheriff && PritchardOriginalVoice
		sheriff.SetOverrideVoiceType(PritchardOriginalVoice)
		If sheriff.GetVoiceType() != PritchardOriginalVoice
			Debug.Trace("TLM_A1: Pritchard voice override did not read back")
		EndIf
	EndIf
EndFunction

Function SettleMarshal()
	Actor body = Alias_Marshal.GetActorReference()
	If !marshalDeathIssued && body && !body.IsDisabled() && body.Is3DLoaded()
		marshalDeathIssued = true
		If !body.IsDead()
			body.Kill()
		EndIf
	EndIf
EndFunction

; ------------------------------------------------ explicit staged sheriff rescue
; This is a disclosed fade-staged entrance/departure, never continuous walking.
TLM:MQ01Quest Function HelpRoad()
 Return TLM_MQ01 as TLM:MQ01Quest
EndFunction

bool Function HelpAlive(Actor who)
 Return who && !who.IsDead() && !who.IsDisabled() && who.Is3DLoaded() && !who.IsInCombat() && !who.IsInScene()
EndFunction

bool Function HelpContext(int capturedEpoch)
 If !helpPlayer || !helpActors || helpActors.Length != 7 || !HelpCast || HelpCast.Length != 7 || !HelpAnchors || HelpAnchors.Length != 6
  Return false
 EndIf
 Actor currentPlayer = Game.GetPlayer()
 int currentOutcome = Outcome()
 bool alreadyFighting = TLM_MQ01.GetStageDone(37)
 ObjectReference center = Alias_AmbushSight.GetReference()
 If !center || !HelpAlive(helpPlayer) || helpPlayer.GetParentCell() != center.GetParentCell() || helpPlayer.GetDistance(center) > 1600.0
  Return false
 EndIf
 int i = 0
 While i < 7
  If !HelpAlive(helpActors[i]) || helpActors[i].GetParentCell() != helpPlayer.GetParentCell()
   Return false
  EndIf
  i += 1
 EndWhile
 ; Snapshot original identities after native participant observations.
 i = 0
 While i < 7
  If HelpCast[i].GetActorReference() != helpActors[i]
   Return false
  EndIf
  i += 1
 EndWhile
 Return currentPlayer == helpPlayer && HelpRoad().SheriffHelpEpoch == capturedEpoch && helpEpoch == capturedEpoch && currentOutcome == OUT_NONE && !alreadyFighting
EndFunction

bool Function HelpMove(int actorIndex,int anchorIndex,int capturedEpoch)
 ObjectReference target = HelpAnchors[anchorIndex].GetReference()
 If !target || target.IsDisabled() || target.GetParentCell() != helpPlayer.GetParentCell()
  Return false
 EndIf
 If !HelpContext(capturedEpoch)
  Return false
 EndIf
 Actor original = helpActors[actorIndex]
 Actor currentPlayer = Game.GetPlayer()
 Actor currentOriginal = HelpCast[actorIndex].GetActorReference()
 ObjectReference currentTarget = HelpAnchors[anchorIndex].GetReference()
 ; Finish yielded identity observations before the finite living-effect tail.
 ; Final destination observation, then finite actor readiness and pure identity tail.
 If target.IsDisabled() || !HelpAlive(original) || !HelpAlive(helpPlayer)
  Return false
 EndIf
 If currentOriginal != original || currentTarget != target || currentPlayer != helpPlayer || HelpRoad().SheriffHelpEpoch != capturedEpoch || helpEpoch != capturedEpoch
  Return false
 EndIf
 original.MoveTo(target)
 Return !original.IsDead() && !original.IsDisabled() && original.GetParentCell() == target.GetParentCell() && original.GetDistance(target) <= 64.0 && HelpRoad().SheriffHelpEpoch == capturedEpoch
EndFunction

Function HelpFade(bool outwards)
 Game.FadeOutGame(outwards,true,0.0,0.25)
 Utility.Wait(0.3)
EndFunction

bool Function ReturnHelpSheriff()
 If !helpReturnDue || !helpActors || !HelpAnchors || HelpAnchors.Length != 6
  Return false
 EndIf
 Actor sheriff = helpActors[0]
 ObjectReference home = HelpAnchors[5].GetReference()
 Actor playerActor = Game.GetPlayer()
 int returnEpoch = HelpRoad().SheriffHelpEpoch
 If !home || home.IsDisabled() || !HelpAlive(sheriff) || !HelpAlive(playerActor) || sheriff.GetParentCell() != playerActor.GetParentCell() || sheriff.GetDistance(playerActor) > 1600.0
  Return false
 EndIf
 If HelpCast[0].GetActorReference() != sheriff || HelpAnchors[5].GetReference() != home || !HelpAlive(sheriff) || !HelpAlive(playerActor)
  Return false
 EndIf
 HelpFade(true)
 Actor currentPlayer = Game.GetPlayer()
 Actor currentSheriff = HelpCast[0].GetActorReference()
 ObjectReference currentHome = HelpAnchors[5].GetReference()
 bool readyToReturn = !home.IsDisabled() && HelpAlive(sheriff) && HelpAlive(playerActor)
 If readyToReturn && currentSheriff == sheriff && currentHome == home && currentPlayer == playerActor && HelpRoad().SheriffHelpEpoch == returnEpoch
  sheriff.MoveTo(home)
 EndIf
 HelpFade(false)
 If !sheriff.IsDead() && !sheriff.IsDisabled() && sheriff.GetParentCell() == home.GetParentCell() && sheriff.GetDistance(home) <= 64.0 && HelpRoad().SheriffHelpEpoch == returnEpoch
  helpReturnDue = false
  HelpRoad().EndSheriffHelp()
  Return true
 EndIf
 Return false
EndFunction

Function CallSheriffHelp()
 If !HelpRoad() || !HelpCast || HelpCast.Length != 7 || !HelpAnchors || HelpAnchors.Length != 6
  Debug.Notification("Pritchard cannot reach the wagon from here.")
  Return
 EndIf
 If !helpActors
  helpActors = new Actor[7]
  int i = 0
  While i < 7
   helpActors[i] = HelpCast[i].GetActorReference()
   i += 1
  EndWhile
 EndIf
 helpPlayer = Game.GetPlayer()
 helpEpoch = HelpRoad().SheriffHelpEpoch
 int capturedEpoch = helpEpoch
 If !HelpContext(capturedEpoch)
  Debug.Notification("The road isn't clear enough to call Pritchard. Try again when everyone is out of danger.")
  Return
 EndIf
 ; This explicit choice pauses the unattended hold-up deadline. Load invalidates
 ; this activation without moving anyone; another deliberate call may retry.
 HelpRoad().PauseForSheriffHelp()
 Debug.Notification("You call toward Mercy. Pritchard comes to the wagon.")
 HelpFade(true)
 helpReturnDue = true
 bool arrived = HelpMove(0,0,capturedEpoch)
 HelpFade(false)
 If !arrived || !HelpContext(capturedEpoch)
  Debug.Notification("Pritchard couldn't complete his approach. Call again, or speak to him to send him home.")
  Return
 EndIf
 int handle = -1
 If RecordedSheriffWarning && HelpContext(capturedEpoch)
  Actor currentPlayer = Game.GetPlayer()
  Actor currentSheriff = HelpCast[0].GetActorReference()
  bool warningReady = HelpAlive(helpActors[0]) && HelpAlive(helpPlayer) && !helpActors[0].IsTalking() && !helpActors[0].IsInDialogueWithPlayer()
  If warningReady && currentPlayer == helpPlayer && HelpRoad().SheriffHelpEpoch == capturedEpoch && currentSheriff == helpActors[0]
   handle = RecordedSheriffWarning.Play(helpActors[0])
  EndIf
 EndIf
 If !HelpContext(capturedEpoch)
  If handle >= 0 && HelpRoad().SheriffHelpEpoch == capturedEpoch
   Sound.StopInstance(handle)
  EndIf
  Return
 EndIf
 int acknowledged = ShowLine(SaySheriffWarning)
 If handle >= 0 && HelpRoad().SheriffHelpEpoch == capturedEpoch
  Sound.StopInstance(handle)
 EndIf
 If acknowledged != 0 || !HelpContext(capturedEpoch)
  Debug.Notification("The wagon is still held. Call again when you're ready, or speak to Pritchard to send him home.")
  Return
 EndIf
 HelpFade(true)
 int moved = 0
 While moved < 4 && HelpMove(moved+1,moved+1,capturedEpoch)
  moved += 1
 EndWhile
 HelpFade(false)
 If moved != 4 || !HelpContext(capturedEpoch)
  Debug.Notification("The Cutters haven't all left the wagon. Call again when the road is clear.")
  Return
 EndIf
 int j = 0
 While j < 4
  ObjectReference withdrawn = HelpAnchors[j+1].GetReference()
  If !withdrawn || helpActors[j+1].GetDistance(withdrawn) > 64.0
   Return
  EndIf
  j += 1
 EndWhile
 If !HelpContext(capturedEpoch)
  Return
 EndIf
 ; Final physical receipts AFTER the last yielding context/alias observations.
 ; The preliminary pass above is retained as an explicit separate observation;
 ; neither pass grants an outcome. There is no context/position retry loop.
 j = 0
 While j < 4
  ObjectReference finalAnchor = HelpAnchors[j+1].GetReference()
  If !finalAnchor || helpActors[j+1].GetParentCell() != finalAnchor.GetParentCell() || helpActors[j+1].GetDistance(finalAnchor) > 64.0
   Return
  EndIf
  j += 1
 EndWhile
 If HelpRoad().SheriffHelpEpoch != capturedEpoch || helpEpoch != capturedEpoch
  Return
 EndIf
 ; Only the existing MQ01 authority records the saved outcome, after arrival,
 ; warning acknowledgment and all four verified original departures.
 TLM_MQ01.SetStage(31)
 If Outcome() == OUT_SAVED
  Debug.Notification("The Cutters have left. Take Gantt's dispatch to Pritchard in Mercy.")
  ReturnHelpSheriff()
 EndIf
EndFunction

; Exact opening captions share one sound owner with an explicit original actor.
int openingVoiceEpoch = 0
int openingVoiceInstance = -1
bool openingVoicePending = false
Actor openingVoicePlayer
Actor openingVoiceSpeaker
float openingVoiceLeft = 0.0
int openingVoiceWho = 5

bool Function OpeningVoiceContext(Actor speakerActor, Actor playerActor, int generation, int voiceWho = 5)
 If !speakerActor || !playerActor
  Debug.Trace("TLM_OPENVOICE REFUSED missing actor/binding")
  Return false
 EndIf
 Actor currentPlayer = Game.GetPlayer()
 Actor currentSpeaker = None
 ObjectReference originalSpeaker = None
 If voiceWho == WHO_PRITCHARD && Alias_Pritchard
  currentSpeaker = Alias_Pritchard.GetActorReference()
  originalSpeaker = BlackLedgerOriginalSheriff
 ElseIf voiceWho == WHO_PIKE && Alias_Pike
  currentSpeaker = Alias_Pike.GetActorReference()
  originalSpeaker = OpeningOriginalPike
 ElseIf voiceWho == WHO_DUNMORE && Alias_Dunmore
  currentSpeaker = Alias_Dunmore.GetActorReference()
  originalSpeaker = OpeningOriginalDunmore
 ElseIf voiceWho == WHO_TALBOT && Alias_Talbot
  currentSpeaker = Alias_Talbot.GetActorReference()
  originalSpeaker = OpeningOriginalTalbot
 EndIf
 If !currentSpeaker || !originalSpeaker
  Debug.Trace("TLM_OPENVOICE REFUSED missing actor/binding")
  Return false
 EndIf
 If speakerActor != originalSpeaker || speakerActor != currentSpeaker || playerActor != currentPlayer
  Debug.Trace("TLM_OPENVOICE REFUSED original actor/player identity")
  Return false
 EndIf
 If playerActor.GetParentCell() != speakerActor.GetParentCell() || playerActor.GetDistance(speakerActor) > 320.0
  Debug.Trace("TLM_OPENVOICE REFUSED cell/range")
  Return false
 EndIf
 If playerActor.IsInScene() || speakerActor.IsInScene() || speakerActor.IsTalking() || speakerActor.IsInDialogueWithPlayer()
  Debug.Trace("TLM_OPENVOICE REFUSED native scene/talking/dialogue busy")
  Return false
 EndIf
 If playerActor.IsDead() || playerActor.IsDisabled() || !playerActor.Is3DLoaded() || playerActor.IsInCombat() || speakerActor.IsDead() || speakerActor.IsDisabled() || !speakerActor.Is3DLoaded() || speakerActor.IsInCombat()
  Debug.Trace("TLM_OPENVOICE REFUSED dead/disabled/unloaded/combat")
  Return false
 EndIf
 ; New private road recordings observe current original identities after native eligibility reads.
 If voiceWho == WHO_DUNMORE
  currentSpeaker = Alias_Dunmore.GetActorReference()
  currentPlayer = Game.GetPlayer()
 ElseIf voiceWho == WHO_TALBOT
  currentSpeaker = Alias_Talbot.GetActorReference()
  currentPlayer = Game.GetPlayer()
 EndIf
 Return generation == openingVoiceEpoch && playerActor == currentPlayer && speakerActor == currentSpeaker && speakerActor == originalSpeaker
EndFunction

int Function ShowOpeningRecording(Message lineMessage, Actor speakerActor, Sound recording, float duration, int voiceWho = 5)
 If !lineMessage
  Return -1
 EndIf
 Debug.Trace("TLM_OPENVOICE REQUEST caption=" + lineMessage + " recording=" + recording + " speaker=" + speakerActor)
 Actor playerActor = Game.GetPlayer()
 int generation = openingVoiceEpoch
 int instance = -1
 bool claimed = false
 If recording && openingVoiceInstance < 0 && !openingVoicePending && OpeningVoiceContext(speakerActor,playerActor,generation,voiceWho)
  ; Publish the in-flight owner BEFORE registration or Play can yield.
  openingVoicePending = true
  openingVoicePlayer = playerActor
  openingVoiceSpeaker = speakerActor
  openingVoiceWho = voiceWho
  claimed = true
  bool registered = RegisterForRemoteEvent(playerActor,"OnPlayerLoadGame")
  Debug.Trace("TLM_OPENVOICE REGISTER result=" + registered)
  If generation != openingVoiceEpoch
   ; A native TRUE registration can finish after load cleanup. Do not remove a newer same-player owner.
   If registered && (!openingVoicePending || openingVoicePlayer != playerActor)
    UnregisterForRemoteEvent(playerActor,"OnPlayerLoadGame")
   EndIf
   Return -1
  EndIf
  If registered && OpeningVoiceContext(speakerActor,playerActor,generation,voiceWho)
   instance = recording.Play(speakerActor)
   If instance >= 0 && generation != openingVoiceEpoch
    ; Only THIS call's returned handle is known to belong to this dispatch.
    Sound.StopInstance(instance)
    Return -1
   EndIf
   If generation == openingVoiceEpoch && instance >= 0
    openingVoiceInstance = instance
    openingVoiceLeft = duration
    StartTimer(0.25,9009)
    Debug.Trace("TLM_OPENVOICE PLAY handle=" + instance + " seconds=" + duration)
   EndIf
  EndIf
 EndIf
 If claimed && generation != openingVoiceEpoch
  Return -1
 EndIf
 If instance >= 0 && !OpeningVoiceContext(speakerActor,playerActor,generation,voiceWho)
  StopOpeningRecording(instance,generation)
  FinishOpeningVoiceRequest(generation)
  Return -1
 EndIf
 int answer = lineMessage.Show()
 StopOpeningRecording(instance,generation)
 If claimed && generation != openingVoiceEpoch
  Return -1
 EndIf
 If instance >= 0 && !OpeningVoiceContext(speakerActor,playerActor,generation,voiceWho)
  FinishOpeningVoiceRequest(generation)
  Return -1
 EndIf
 If claimed
  FinishOpeningVoiceRequest(generation)
  ; Unregister itself yields: the final answer belongs to this generation only.
  If generation != openingVoiceEpoch
   Return -1
  EndIf
 EndIf
 Return answer
EndFunction

Function FinishOpeningVoiceRequest(int generation)
 If generation == openingVoiceEpoch && openingVoicePending
  Actor playerActor = openingVoicePlayer
  If playerActor
   UnregisterForRemoteEvent(playerActor,"OnPlayerLoadGame")
  EndIf
  If generation == openingVoiceEpoch
   openingVoicePending = false
   openingVoicePlayer = None
   openingVoiceSpeaker = None
  EndIf
 EndIf
EndFunction

Function StopOpeningRecording(int instance, int generation)
 If instance >= 0 && instance == openingVoiceInstance && generation == openingVoiceEpoch
  openingVoiceInstance = -1
  openingVoiceLeft = 0.0
  CancelTimer(9009)
  Sound.StopInstance(instance)
 EndIf
EndFunction

Function OpeningVoiceLoaded()
 int instance = openingVoiceInstance
 Actor playerActor = openingVoicePlayer
 openingVoiceInstance = -1
 openingVoicePending = false
 openingVoicePlayer = None
 openingVoiceSpeaker = None
 openingVoiceEpoch += 1
 openingVoiceLeft = 0.0
 If instance >= 0
  CancelTimer(9009)
  Sound.StopInstance(instance)
 EndIf
 If playerActor
  UnregisterForRemoteEvent(playerActor,"OnPlayerLoadGame")
 EndIf
EndFunction

Event Actor.OnPlayerLoadGame(Actor akSender)
 If inquiryBusy && akSender == inquiryPlayer
  FinishInquiry(inquiryEpoch)
  talking = false
  ReconcileInquiryObjectives()
 EndIf
 If (openingVoicePending || openingVoiceInstance >= 0) && akSender == openingVoicePlayer
  OpeningVoiceLoaded()
 EndIf
EndEvent

; Optional local inquiry: one journal, state on this existing section, no evidence/outcome authority.
bool Function InquiryBindings()
 Return FirstBrakeInquiry && SayInquiryOffer && SayInquiryOfferDead && SayInquirySheriffMenu && SayInquiryPending && SayInquiryAdaMenu && SayInquiryHistory && SayInquiryReport && SayInquiryReported && SayInquiryUnavailable && Alias_Pritchard && Alias_Pike && BlackLedgerOriginalSheriff && OpeningOriginalPike
EndFunction

Actor Function InquiryActor(int role)
 If role == 0 && Alias_Pritchard
  Actor sheriff = Alias_Pritchard.GetActorReference()
  If sheriff == BlackLedgerOriginalSheriff
   Return sheriff
  EndIf
 ElseIf role == 1 && Alias_Pike
  Actor pike = Alias_Pike.GetActorReference()
  If pike == OpeningOriginalPike
   Return pike
  EndIf
 EndIf
 Return None
EndFunction

bool Function InquiryActorAvailable(int role)
 Actor person = InquiryActor(role)
 Return person && !person.IsDead() && !person.IsDisabled() && person.Is3DLoaded()
EndFunction

bool Function InquiryMarkerBindings()
 ReferenceAlias pike = FirstBrakeInquiry.GetAlias(0) as ReferenceAlias
 ReferenceAlias sheriff = FirstBrakeInquiry.GetAlias(1) as ReferenceAlias
 Return pike && sheriff && pike.GetActorReference() == OpeningOriginalPike && sheriff.GetActorReference() == BlackLedgerOriginalSheriff
EndFunction

bool Function InquiryContext(Actor speakerActor, int role, int generation)
 If !inquiryBusy || generation != inquiryEpoch || speakerActor != inquirySpeaker || !InquiryParticipants(speakerActor,role,inquiryPlayer)
  Return false
 EndIf
 Return inquiryBusy && generation == inquiryEpoch && speakerActor == inquirySpeaker
EndFunction

bool Function InquiryParticipants(Actor speakerActor, int role, Actor listener)
 If !listener || !speakerActor
  Return false
 EndIf
 If speakerActor.GetParentCell() != listener.GetParentCell() || speakerActor.GetDistance(listener) > 320.0 || speakerActor.IsDead() || listener.IsDead() || speakerActor.IsDisabled() || listener.IsDisabled() || !speakerActor.Is3DLoaded() || !listener.Is3DLoaded() || speakerActor.IsInCombat() || listener.IsInCombat() || speakerActor.IsInScene() || listener.IsInScene() || speakerActor.IsTalking() || speakerActor.IsInDialogueWithPlayer()
  Return false
 EndIf
 ; Eligibility natives can yield: observe current identities/markers afterwards, then pure tail.
 bool markers = true
 If FirstBrakeInquiry.IsRunning()
  markers = InquiryMarkerBindings()
 EndIf
 Actor currentPlayer = Game.GetPlayer()
 Actor currentSpeaker = InquiryActor(role)
 Return markers && listener == currentPlayer && speakerActor == currentSpeaker
EndFunction

int Function BeginInquiry(Actor speakerActor, int role)
 If inquiryBusy || inquiryRegisterEpoch >= 0 || !InquiryBindings() || !speakerActor
  Return -1
 EndIf
 inquiryEpoch += 1
 int generation = inquiryEpoch
 inquiryBusy = true
 inquiryPlayer = Game.GetPlayer()
 inquirySpeaker = speakerActor
 Actor listener = inquiryPlayer
 bool registered = false
 If listener
  inquiryRegisterEpoch = generation
  registered = RegisterForRemoteEvent(listener,"OnPlayerLoadGame")
  If !inquiryBusy || inquiryEpoch != generation || inquiryPlayer != listener
   ; A true registration may become active after a cancellation callback already unregistered.
   ; Only clean the captured listener when it is not owned by a newer same-listener request.
   If registered && (!inquiryBusy || inquiryPlayer != listener)
    UnregisterForRemoteEvent(listener,"OnPlayerLoadGame")
   EndIf
   If inquiryRegisterEpoch == generation
    inquiryRegisterEpoch = -1
   EndIf
   Return -1
  EndIf
  If inquiryRegisterEpoch == generation
   inquiryRegisterEpoch = -1
  EndIf
 EndIf
 If !registered || !InquiryContext(speakerActor,role,generation)
  FinishInquiry(generation)
  Debug.Notification("The inquiry is unresolved. Speak again when the person is available.")
  Return -1
 EndIf
 Return generation
EndFunction

Function FinishInquiry(int generation)
 If inquiryBusy && generation == inquiryEpoch
  Actor listener = inquiryPlayer
  inquiryEpoch += 1
  int cleanupEpoch = inquiryEpoch
  ; Retain listener ownership through yielding unregister so actual load invalidates delegation.
  If listener
   UnregisterForRemoteEvent(listener,"OnPlayerLoadGame")
  EndIf
  If inquiryEpoch == cleanupEpoch && inquiryBusy
   inquiryBusy = false
   inquiryPlayer = None
   inquirySpeaker = None
  EndIf
 EndIf
EndFunction

Function ReconcileInquiryObjectives()
 If !FirstBrakeInquiry || !FirstBrakeInquiry.IsRunning()
  Return
 EndIf
 If inquiryState == 2
  Actor pike = InquiryActor(1)
  FirstBrakeInquiry.SetObjectiveCompleted(10,false)
  FirstBrakeInquiry.SetObjectiveDisplayed(10,pike && !pike.IsDead() && !pike.IsDisabled())
  FirstBrakeInquiry.SetObjectiveDisplayed(20,false)
 ElseIf inquiryState == 3
  Actor sheriff = InquiryActor(0)
  FirstBrakeInquiry.SetObjectiveDisplayed(10,false)
  FirstBrakeInquiry.SetObjectiveCompleted(10)
  FirstBrakeInquiry.SetObjectiveDisplayed(20,sheriff && !sheriff.IsDead() && !sheriff.IsDisabled())
 ElseIf inquiryState == 4
  FirstBrakeInquiry.SetObjectiveDisplayed(10,false)
  FirstBrakeInquiry.SetObjectiveDisplayed(20,false)
  FirstBrakeInquiry.SetObjectiveCompleted(10)
  FirstBrakeInquiry.SetObjectiveCompleted(20)
  FirstBrakeInquiry.CompleteQuest()
 EndIf
EndFunction

bool Function OfferFirstBrakeInquiry(Actor speakerActor, bool initial = false)
 If !InquiryBindings() || inquiryState == 4
  Return false
 EndIf
 int generation = BeginInquiry(speakerActor,0)
 If generation < 0
  Return true
 EndIf
 bool reportOldLedger = false
 bool roads = false
 bool proceed = true
 bool hasLedger = CanDecide()
 If !InquiryContext(speakerActor,0,generation)
  FinishInquiry(generation)
  Return true
 EndIf
 If !initial && hasLedger
  int menu = SayInquirySheriffMenu.Show()
  If !InquiryContext(speakerActor,0,generation)
   FinishInquiry(generation)
   Return true
  EndIf
  reportOldLedger = menu == 1
  proceed = menu == 0
 EndIf
 If proceed
  If inquiryState < 2
   inquiryState = 1
   Message offer = SayInquiryOffer
   If Alias_Marshal
    Actor marshal = Alias_Marshal.GetActorReference()
    If marshal && marshal.IsDead()
     offer = SayInquiryOfferDead
    EndIf
   EndIf
   If !InquiryContext(speakerActor,0,generation)
    FinishInquiry(generation)
    Return true
   EndIf
   int answer = offer.Show()
   If InquiryContext(speakerActor,0,generation) && answer == 0
    bool adaAvailable = InquiryActorAvailable(1)
    If !InquiryContext(speakerActor,0,generation)
     FinishInquiry(generation)
     Return true
    EndIf
    If !adaAvailable
     SayInquiryUnavailable.Show()
    Else
     bool journalReady = FirstBrakeInquiry.IsRunning()
     If !journalReady
      journalReady = FirstBrakeInquiry.Start()
     EndIf
     If journalReady && FirstBrakeInquiry.IsRunning() && InquiryMarkerBindings() && InquiryActorAvailable(1) && InquiryContext(speakerActor,0,generation)
      inquiryState = 2
      ReconcileInquiryObjectives()
     ElseIf InquiryContext(speakerActor,0,generation)
      SayInquiryUnavailable.Show()
     EndIf
    EndIf
   EndIf
  ElseIf inquiryState == 2
   ReconcileInquiryObjectives()
   bool adaAvailable = InquiryActorAvailable(1)
   If InquiryContext(speakerActor,0,generation)
    If adaAvailable
     SayInquiryPending.Show()
    Else
     SayInquiryUnavailable.Show()
    EndIf
   EndIf
  ElseIf inquiryState == 3
   int report = SayInquiryReport.Show()
   If report == 0 && InquiryContext(speakerActor,0,generation)
    inquiryState = 4
    ReconcileInquiryObjectives()
    If InquiryContext(speakerActor,0,generation)
     int afterReport = SayInquiryReported.Show()
     roads = afterReport == 0 && InquiryContext(speakerActor,0,generation)
    EndIf
   EndIf
  EndIf
 EndIf
 Actor listener = inquiryPlayer
 FinishInquiry(generation)
 bool current = inquiryEpoch == generation + 1 && InquiryParticipants(speakerActor,0,listener) && inquiryEpoch == generation + 1
 If reportOldLedger && current
  Report()
 ElseIf roads && current
  ShowOpeningRecording(HandOffLine(),speakerActor,RecordedRoadHandOff,12.5)
 EndIf
 Return true
EndFunction

bool Function OfferAdaBrakeInquiry(Actor speakerActor)
 If !InquiryBindings() || inquiryState < 2 || inquiryState > 3
  Return false
 EndIf
 int generation = BeginInquiry(speakerActor,1)
 If generation < 0
  Return true
 EndIf
 int choice = SayInquiryAdaMenu.Show()
 bool oldBusiness = false
 If InquiryContext(speakerActor,1,generation)
  If choice == 1
   oldBusiness = true
  ElseIf choice == 0
   int acknowledged = SayInquiryHistory.Show()
   If acknowledged == 0 && InquiryContext(speakerActor,1,generation)
    inquiryState = 3
    ReconcileInquiryObjectives()
    bool sheriffAvailable = InquiryActorAvailable(0)
    If !sheriffAvailable && InquiryContext(speakerActor,1,generation)
     SayInquiryUnavailable.Show()
    EndIf
   EndIf
  EndIf
 EndIf
 Actor listener = inquiryPlayer
 FinishInquiry(generation)
 If oldBusiness && inquiryEpoch == generation + 1 && InquiryParticipants(speakerActor,1,listener) && inquiryEpoch == generation + 1
  TalkPikeExisting(speakerActor)
 EndIf
 Return true
EndFunction

Event OnTimer(int aiTimerID)
 If aiTimerID != 9009 || openingVoiceInstance < 0
  Return
 EndIf
 int instance = openingVoiceInstance
 int generation = openingVoiceEpoch
 openingVoiceLeft -= 0.25
 If openingVoiceLeft <= 0.0 || !OpeningVoiceContext(openingVoiceSpeaker,openingVoicePlayer,generation,openingVoiceWho)
  StopOpeningRecording(instance,generation)
 Else
  StartTimer(0.25,9009)
 EndIf
EndEvent

; Only the two correctly bound living originals get custom-UI default activation suppression.
Function ConfigureRoadVoiceActivation()
 Actor dunmore = None
 Actor talbot = None
 If RecordedDunmoreHold && Alias_Dunmore && OpeningOriginalDunmore
  dunmore = Alias_Dunmore.GetActorReference()
  If dunmore && dunmore == OpeningOriginalDunmore && !dunmore.IsDead()
   dunmore.BlockActivation(true,false)
  EndIf
 EndIf
 If RecordedTalbotGate && Alias_Talbot && OpeningOriginalTalbot
  talbot = Alias_Talbot.GetActorReference()
  If talbot && talbot == OpeningOriginalTalbot && !talbot.IsDead()
   talbot.BlockActivation(true,false)
  EndIf
 EndIf
EndFunction
