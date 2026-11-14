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

NOT COMPILED. NOT RUN IN THE GAME. New to this project, and so not seen at
work in the game: properties that are lists of aliases and of text, arrays
made with "new", Utility.RandomInt, EnableNoWait, EquipItem, a message box
with buttons, ForceRefTo for a thing (it has run for actors), a placed
actor that starts dead, a book, a weapon and a container placed by the
plugin.}

Group Quests
	Quest Property TLM_MQ01 Auto Const Mandatory
	Quest Property TLM_SQ01 Auto Const Mandatory
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
; plugin's own; here there are thirteen.
float PEOPLE_SECONDS = 300.0 Const
float PEOPLE_STEP_SECONDS = 400.0 Const
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
	int unfilled = CastAll()
	SwitchOn()
	int missing = WaitForPeople(PEOPLE_SECONDS, None)
	Actor marshal = Alias_Marshal.GetActorReference()
	If marshal && !marshal.IsDead()
		; The plugin places him dead. If the game did not take that, he dies here.
		marshal.Kill()
	EndIf
	OpenTheRoad()
	WearPipBoy()
	Debug.Trace("TLM_A1: the first section is set up; aliases left empty: " + unfilled + ", people not there: " + missing)
	If SayBegin
		SayBegin.Show()
	EndIf
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
	; Nothing between the test and the claim calls into the game, so two
	; activations cannot both pass.
	If quiet || talking
		Return
	EndIf
	talking = true
	If akWho && !akWho.IsDead() && !akWho.IsInCombat() && TLM_MQ01.GetStageDone(10)
		If aiWho == WHO_DUNMORE
			TalkDunmore()
		ElseIf aiWho == WHO_NELL
			TalkNell()
		ElseIf aiWho == WHO_ABEL
			TalkAbel()
		ElseIf aiWho == WHO_CUTTER
			TalkCutter()
		ElseIf aiWho == WHO_PRITCHARD
			TalkPritchard()
		ElseIf aiWho == WHO_PIKE
			TalkPike()
		ElseIf aiWho == WHO_VANE
			TalkVane()
		ElseIf aiWho == WHO_KEENE
			TalkKeene()
		ElseIf aiWho == WHO_TALBOT
			TalkTalbot()
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

Function TalkDunmore()
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
	int answer = ShowLine(SayDunmoreHold)
	If answer == 0
		; "Pritchard hangs road-takers. Leave."
		If Coin()
			ShowLine(SayDunmoreBreaks)
			TLM_MQ01.SetStage(31)
		Else
			ShowLine(SayDunmoreTurns)
			TLM_MQ01.SetStage(37)
		EndIf
	ElseIf answer == 1
		; "Let them go."
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
		Else
			ShowLine(SayDunmoreTurns)
			TLM_MQ01.SetStage(37)
		EndIf
	EndIf
	; "Not my business.": nothing. The quest's own rules for walking on apply.
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

Function TalkPritchard()
	{Design 8.3: the dispatch, then what he makes of the road, then the three
	towns. Reporting the ledger to him is the side quest's route A.}
	bool more = CanDecide()
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
			second = ShowLine(SayPritchardCaseAndMore)
		Else
			second = ShowLine(SayPritchardCase)
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
	If !TLM_MQ01.GetStageDone(50)
		Return
	EndIf
	If !TLM_MQ01.GetStageDone(60)
		Debrief()
		ShowLine(SayPritchardHandOff)
		TLM_MQ01.SetStage(60)
		Return
	EndIf
	If more
		If ShowLine(SayPritchardAfterAndMore) == 1
			Report()
		EndIf
	Else
		ShowLine(SayPritchardAfter)
	EndIf
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

Function TalkPike()
	If TLM_G_SQ01_HaskellScapegoated.GetValueInt() == 1
		ShowLine(SayPikeHaskell)
	ElseIf TLM_SQ01.GetStageDone(14)
		ShowLine(SayPikeAfter)
	ElseIf TLM_SQ01.GetStageDone(10) && TLM_G_SQ01_Outcome.GetValueInt() == 0
		If ShowLine(SayPikeBook) == 0
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

Function TalkTalbot()
	If TLM_MQ01.GetStageDone(50)
		ShowLine(SayTalbotAfter)
	Else
		ShowLine(SayTalbotGate)
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
	akTest.CheckTrue("act1: the marshal is dead when the section has been set up (the plugin places him dead)", marshal && marshal.IsDead())
	If marshal && !marshal.IsDead()
		akTest.Step("killing the marshal, whom the plugin was to place dead")
		marshal.Kill()
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
		bool took = dispatch.Activate(playerRef)
		WaitForStage(TLM_MQ01, 20)
		akTest.Note("act1: Activate on the dispatch from " + playerRef.GetDistance(dispatch) + " away returned " + took + "; the player has " + playerRef.GetItemCount(DispatchItem) + ", stage 20 set = " + TLM_MQ01.GetStageDone(20))
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
	WaitForStage(TLM_SQ01, 20)
	akTest.CheckInt("act1: the evidence level with the ledger and the journal", TLM_G_SQ01_EvidenceLevel.GetValueInt(), 1)
	akTest.CheckTrue("act1: the side quest's case can be presented (its stage 20)", TLM_SQ01.GetStageDone(20))

	ObjectReference revolver = Alias_Revolver.GetReference()
	If revolver
		akTest.Step("having the player pick the revolver up")
		bool tookRevolver = revolver.Activate(playerRef)
		WaitForStage(TLM_MQ01, 15)
		akTest.Note("act1: Activate on the revolver returned " + tookRevolver)
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
