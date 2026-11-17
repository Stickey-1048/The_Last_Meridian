Scriptname TLM:MQ02BQuest extends Quest
{On TLM_MQ02B, "The Queen of Tellico": the Greenwater road of Chapter 2
(docs/design/GREENWATER_STORY_001.md and its order). The accepted writing is
assets/incoming/act1/story/quests/tlm_mq02b.json; which of its stages, flags
and guards became what here is in docs/design/GREENWATER_STORY_001_MAPPING.json.

This script is the road's RULES and nothing else: what has been earned, what
may happen next, and the one place where each fact is written down. It shows
no box and moves no scenery. TLM:GreenwaterWalk, on the greybox quest, shows
the lines and works the pieces, and asks this script before and after every
box.

What it keeps to:
  - A stage is what was actually done, never "everything below it". Winning
    at cards (41) is not the grain at the landing. Taking the share (44) is
    not the lie, and the lie is not her thanks (46).
  - One course, once. Claim is written, with no call into the game between
    the test and the writing, the moment a course becomes irreversible: the
    card win, the chain cut, the fire order, the share. A cut chain is an
    escape pending: from then on there are no cards, no share and no fire,
    only the pilot lever, however often it takes.
  - Nobody dead, absent or fighting speaks, receives a prisoner or hands
    anything over. Each action asks only for the people it needs; nothing
    here asks for all four to be alive.
  - Every one-time thing (200 caps, the letter, three small portions of food)
    is asked of the game once, with the intent written down first and the
    result read from the inventory. A request the game does not honour fails
    closed: nothing is claimed and nothing is asked again.
  - Nothing here runs on a timer, on start-up or on loading a game.

Stage 46 is this build's own: "the lie was told and heard". It carries the
accepted journal text of stage 44, which speaks of Opal's thanks; stage 44
itself carries the contract's interim text. Objectives 60 and 80 are this
build's own directions.

NOT COMPILED. NOT RUN IN THE GAME. It runs in the project's stand-in engine
(tools/papyrus_sim/test_greenwater.py) against tools/logic_model/greenwater_model.py.}

Group MainQuest
	Quest Property TLM_MQ01 Auto Const Mandatory
	{Read only.}
	GlobalVariable Property TLM_G_MQ01_Done Auto Const Mandatory
	{Read only.}
	ReferenceAlias Property Alias_MercySheriff Auto Const
	{SheriffPritchard of TLM_MQ01: whoever the first section cast as Owen
	Pritchard. Read only; he is never moved or put into an alias here.}
EndGroup

Group Cast
	ReferenceAlias Property Alias_Opal Auto Const Mandatory
	ReferenceAlias Property Alias_Hatcher Auto Const Mandatory
	ReferenceAlias Property Alias_Rafferty Auto Const Mandatory
	ReferenceAlias Property Alias_Belden Auto Const Mandatory
	ReferenceAlias Property Alias_Crew1 Auto Const
	ReferenceAlias Property Alias_Crew2 Auto Const
	ReferenceAlias Property Alias_Steeple Auto Const
	{Where Greenwater hangs a man: a marker.}
EndGroup

Group Facts
	GlobalVariable Property TLM_G_MQ02B_Outcome Auto Const Mandatory
	GlobalVariable Property TLM_G_MQ02B_Cargo Auto Const Mandatory
	GlobalVariable Property TLM_G_MQ02B_Recovered Auto Const Mandatory
	GlobalVariable Property TLM_G_MQ02B_Hatcher Auto Const Mandatory
	GlobalVariable Property TLM_G_MQ02B_GrainHome Auto Const Mandatory
	GlobalVariable Property TLM_G_MQ02B_GrainSold Auto Const Mandatory
	GlobalVariable Property TLM_G_MQ02B_QueenBurned Auto Const Mandatory
	GlobalVariable Property TLM_G_MQ02B_HatcherHanged Auto Const Mandatory
	GlobalVariable Property TLM_G_MQ02B_HatcherFriend Auto Const Mandatory
	GlobalVariable Property TLM_G_MQ02B_HatcherHunting Auto Const Mandatory
	GlobalVariable Property TLM_G_MQ02B_SilverRiver Auto Const Mandatory
	GlobalVariable Property TLM_G_MQ02B_Reported Auto Const Mandatory
EndGroup

Group Forms
	Form Property Caps Auto Const
	{Caps001 from Fallout4.esm. None if it was not found: no share can be paid, and none is offered.}
	ActorValue Property Charisma Auto Const
	{From Fallout4.esm. None if it was not found: no card is played.}
	Form Property Meal Auto Const
	{A food item of the game's. None if none was found: nothing is given and nothing is said to have been.}
	Form Property HireLetter Auto Const Mandatory
	{TLM_BOOK_LetterOfHire}
EndGroup

; ----------------------------------------------------------------- constants
; The same numbers as tools/logic_model/greenwater_model.py; a test compares them.

; TLM_G_MQ02B_Outcome, and Claim.
int RV_NONE = 0 Const
int RV_CARDS = 41 Const
int RV_CHUTE = 42 Const
int RV_FIRE = 43 Const
int RV_SHARE = 44 Const

; TLM_G_MQ02B_Cargo.
int RV_CARGO_LASHED = 0 Const
int RV_CARGO_YIELDED = 1 Const
int RV_CARGO_HOME_WHOLE = 2 Const
int RV_CARGO_HOME_REDUCED = 3 Const
int RV_CARGO_DESTROYED = 4 Const

; TLM_G_MQ02B_Hatcher.
int RV_H_FREE = 0 Const
int RV_H_RELEASED = 1 Const
int RV_H_CUSTODY = 2 Const
int RV_H_HANGED = 3 Const
int RV_H_DEAD = 4 Const
int RV_H_UNACCOUNTED = 5 Const

int RV_CARD_NONE = 0 Const
int RV_CARD_LOST = 1 Const
int RV_CARD_WON = 2 Const

; A prototype's tuning, not canon: the card is won with current Charisma of
; this much or more. Written to the script log with what was read.
int RV_CARD_THRESHOLD = 5 Const

; Bookkeeping only; no sack count is canon. A whole barge is twelve units; the
; Chute takes a third with Rafferty piloting and half without him.
int RV_UNITS_WHOLE = 12 Const
int RV_UNITS_PILOTED = 8 Const
int RV_UNITS_ALONE = 6 Const

int RV_SHARE_CAPS = 200 Const

; Which return the pilot lever has begun.
int RV_RETURN_NONE = 0 Const
int RV_RETURN_ESCAPE = 1 Const
int RV_RETURN_TOW = 2 Const

; How the hire was learned.
int RV_HIRE_LETTER = 1 Const
int RV_HIRE_ADMISSION = 2 Const

; The three small portions.
int RV_GRANT_BOWL = 1 Const
int RV_GRANT_CUP = 2 Const
int RV_GRANT_RELIEF = 3 Const

int RV_ACK_POLLS = 10 Const
float RV_CUSTODY_REACH = 1500.0 Const

; ------------------------------------------------------------------- state
; Kept by a save as they are. Nothing sets them back.

; The course that can no longer be exchanged for another: 0, or one of
; RV_CARDS, RV_CHUTE (from the moment the chain is cut), RV_FIRE, RV_SHARE.
int Claim = 0
int CardResult = 0
bool EscapePending = false
int ReturnPending = 0
bool FireWarned = false
bool SharePending = false
bool SharePaid = false
bool LieTold = false
bool LieHeard = false
bool DeniedSaid = false
bool Judging = false
bool Burning = false
int Approach = 0
bool HireRead = false
bool HireHeard = false
bool LetterPending = false
bool LetterGiven = false
bool BowlPending = false
bool BowlGiven = false
bool CupPending = false
bool CupGiven = false
bool ReliefPending = false
bool ReliefGiven = false

Event OnStageSet(int auiStageID, int auiItemID)
	; One line per stage event in the game's script log, as TLM_MQ01 writes.
	Debug.Trace("TLM_MQ02B: stage " + auiStageID + " item " + auiItemID)
EndEvent

; ================================================================ who is there

Actor Function Person(ReferenceAlias akAlias)
	If !akAlias
		Return None
	EndIf
	Return akAlias.GetActorReference()
EndFunction

bool Function IsThere(ReferenceAlias akAlias)
	{Alive and present. Fighting or not.}
	Actor who = Person(akAlias)
	If !who
		Return false
	EndIf
	Return !who.IsDead() && !who.IsDisabled()
EndFunction

bool Function CanSpeak(ReferenceAlias akAlias)
	{Alive, present and in no fight: can say a line, take a prisoner, hand something over.}
	Actor who = Person(akAlias)
	If !who
		Return false
	EndIf
	Return !who.IsDead() && !who.IsDisabled() && !who.IsInCombat()
EndFunction

bool Function PlayerIsAlive()
	Actor player = Game.GetPlayer()
	If !player
		Return false
	EndIf
	Return !player.IsDead()
EndFunction

bool Function OpalCanSpeak()
	Return CanSpeak(Alias_Opal)
EndFunction

bool Function RaffertyCanSpeak()
	Return CanSpeak(Alias_Rafferty)
EndFunction

bool Function RaffertyIsThere()
	Return IsThere(Alias_Rafferty)
EndFunction

bool Function BeldenCanSpeak()
	Return CanSpeak(Alias_Belden)
EndFunction

bool Function SheriffCanReceive()
	{Owen Pritchard, alive, present and in no fight, wherever the first section put him.}
	Return CanSpeak(Alias_MercySheriff)
EndFunction

int Function HatcherState()
	{What has become of Lyle Hatcher. A free or released man found dead is dead otherwise, whether or not his death was heard of.}
	int fate = TLM_G_MQ02B_Hatcher.GetValueInt()
	If fate == RV_H_FREE || fate == RV_H_RELEASED
		Actor hatcher = Person(Alias_Hatcher)
		If hatcher && hatcher.IsDead()
			Return RV_H_DEAD
		EndIf
	EndIf
	Return fate
EndFunction

bool Function HatcherAtTable()
	{He can deal, sell and talk: alive, present, in no fight, and nobody's prisoner.}
	If !CanSpeak(Alias_Hatcher)
		Return false
	EndIf
	int fate = TLM_G_MQ02B_Hatcher.GetValueInt()
	Return fate == RV_H_FREE || fate == RV_H_RELEASED
EndFunction

bool Function HatcherToJudge()
	{Beaten at cards, alive, present and still free: there is something to decide.}
	If !GetStageDone(41) || !IsThere(Alias_Hatcher)
		Return false
	EndIf
	Return TLM_G_MQ02B_Hatcher.GetValueInt() == RV_H_FREE
EndFunction

; ================================================================ what stands

bool Function RoadOpen()
	{The road was begun, its quest is running, and the player is alive.}
	Return IsRunning() && GetStageDone(10) && PlayerIsAlive()
EndFunction

int Function Outcome()
	Return TLM_G_MQ02B_Outcome.GetValueInt()
EndFunction

int Function Cargo()
	Return TLM_G_MQ02B_Cargo.GetValueInt()
EndFunction

int Function Recovered()
	Return TLM_G_MQ02B_Recovered.GetValueInt()
EndFunction

bool Function Unsettled()
	{No course has been taken and none is under way.}
	Return Claim == RV_NONE
EndFunction

bool Function IsEscapePending()
	Return EscapePending
EndFunction

bool Function IsFireWarned()
	Return FireWarned
EndFunction

bool Function IsBurning()
	{The fire was ordered and its outcome is not yet recorded.}
	Return Burning
EndFunction

bool Function IsSharePaid()
	Return SharePaid
EndFunction

bool Function IsShareOffered()
	{Hatcher's share can still be taken: never paid and never asked for.}
	Return Claim == RV_NONE && !SharePaid && !SharePending && Caps != None
EndFunction

bool Function IsLieTold()
	Return LieTold
EndFunction

bool Function IsLieHeard()
	Return LieHeard
EndFunction

bool Function IsDeniedSaid()
	Return DeniedSaid
EndFunction

bool Function KnowsHire()
	Return GetStageDone(50)
EndFunction

bool Function IsReported()
	Return TLM_G_MQ02B_Reported.GetValueInt() == 1
EndFunction

int Function LastCard()
	Return CardResult
EndFunction

bool Function CanComplete()
	{One course was carried through to what it does: the Chute run, the fire,
	the paid share, or the barge won at cards AND brought home.}
	If GetStageDone(42) || GetStageDone(43)
		Return true
	EndIf
	If GetStageDone(44) && SharePaid
		Return true
	EndIf
	Return GetStageDone(41) && Cargo() == RV_CARGO_HOME_WHOLE
EndFunction

; ================================================================== objectives

Function ShowObjective(int aiObjective)
	If !IsObjectiveDisplayed(aiObjective) && !IsObjectiveCompleted(aiObjective)
		SetObjectiveDisplayed(aiObjective)
	EndIf
EndFunction

Function FinishObjective(int aiObjective)
	If !IsObjectiveCompleted(aiObjective)
		SetObjectiveCompleted(aiObjective)
	EndIf
EndFunction

Function RetireObjective(int aiObjective)
	{No longer asked, and not done: taken off the list without being ticked.}
	If IsObjectiveDisplayed(aiObjective) && !IsObjectiveCompleted(aiObjective)
		SetObjectiveDisplayed(aiObjective, false)
	EndIf
EndFunction

Function CourseTaken()
	FinishObjective(40)
	If CanComplete()
		FinishObjective(60)
		ShowObjective(80)
	EndIf
EndFunction

; ====================================================================== the road

bool Function Begin()
	{The road's quest is running. Started if need be; both Start's word and
	the running state are required. Sets no stage.}
	If IsRunning()
		Return true
	EndIf
	bool started = Start()
	bool running = IsRunning()
	If !started || !running
		Debug.Trace("TLM_MQ02B: its quest is not running and could not be started (Start returned " + started + ", running " + running + "); nothing was changed", 2)
		Return false
	EndIf
	Return true
EndFunction

bool Function Arrive()
	{The player stepped onto the Greenwater landing.}
	If !IsRunning() || !PlayerIsAlive()
		Return false
	EndIf
	If !GetStageDone(10)
		SetStage(10)
		ShowObjective(10)
	EndIf
	Return true
EndFunction

bool Function HearOpal()
	{Opal's account of what she wants was delivered and answered.}
	If !RoadOpen() || !CanSpeak(Alias_Opal)
		Return false
	EndIf
	If !GetStageDone(20)
		SetStage(20)
		FinishObjective(10)
		If !GetStageDone(30)
			ShowObjective(20)
		EndIf
	EndIf
	Return true
EndFunction

bool Function Board(int aiApproach)
	{The player is aboard the Queen: 1 by the gangway, 2 over the off side,
	3 by reaching a piece of the deck (the greybox has no hull). Never refused
	for want of stage 20 or of anybody living.}
	If !RoadOpen()
		Return false
	EndIf
	If !GetStageDone(30)
		Approach = aiApproach
		SetStage(30)
		; Not heard out (she is dead, or was walked past): no longer asked, and not ticked.
		RetireObjective(10)
		If IsObjectiveDisplayed(20)
			FinishObjective(20)
		EndIf
		If Claim == RV_NONE
			ShowObjective(40)
		EndIf
		If !GetStageDone(50)
			ShowObjective(50)
		EndIf
	EndIf
	Return true
EndFunction

bool Function SitDown()
	{The player is at Hatcher's table with Hatcher at it.}
	If !RoadOpen() || !GetStageDone(30) || !HatcherAtTable()
		Return false
	EndIf
	If !GetStageDone(40)
		SetStage(40)
	EndIf
	Return true
EndFunction

; ---------------------------------------------------------------------- cards

int Function PlayCards()
	{One hand: the barge against the player's gun. RV_CARD_WON, RV_CARD_LOST,
	or RV_CARD_NONE if no hand could be played. Nothing is taken on a loss.}
	If !RoadOpen() || !GetStageDone(30) || !HatcherAtTable()
		Return RV_CARD_NONE
	EndIf
	If !Charisma
		Debug.Trace("TLM_MQ02B: no card is played: the Charisma actor value is not bound", 2)
		Return RV_CARD_NONE
	EndIf
	Actor player = Game.GetPlayer()
	float current = player.GetValue(Charisma)
	float born = player.GetBaseValue(Charisma)
	; No call into the game between this test and the claim.
	If Claim != RV_NONE
		Return RV_CARD_NONE
	EndIf
	If current >= RV_CARD_THRESHOLD
		Claim = RV_CARDS
		CardResult = RV_CARD_WON
		Debug.Trace("TLM_MQ02B: card check WON: current Charisma " + current + " (base " + born + ") against threshold " + RV_CARD_THRESHOLD)
		TLM_G_MQ02B_Outcome.SetValueInt(RV_CARDS)
		TLM_G_MQ02B_Cargo.SetValueInt(RV_CARGO_YIELDED)
		SetStage(41)
		FinishObjective(40)
		ShowObjective(60)
		Return RV_CARD_WON
	EndIf
	CardResult = RV_CARD_LOST
	Debug.Trace("TLM_MQ02B: card check LOST: current Charisma " + current + " (base " + born + ") against threshold " + RV_CARD_THRESHOLD)
	If !GetStageDone(45)
		SetStage(45)
	EndIf
	Return RV_CARD_LOST
EndFunction

; ---------------------------------------------------------------------- share

bool Function TakeShare()
	{"Done." Two hundred caps, once, and the grain stays with the Queen.}
	If !RoadOpen() || !GetStageDone(30) || !HatcherAtTable()
		Return false
	EndIf
	If !Caps
		Debug.Trace("TLM_MQ02B: no share is paid: Caps is not bound", 2)
		Return false
	EndIf
	Actor player = Game.GetPlayer()
	int before = player.GetItemCount(Caps)
	; No call into the game between this test and the claim.
	If Claim != RV_NONE || SharePending || SharePaid
		Return false
	EndIf
	Claim = RV_SHARE
	SharePending = true
	player.AddItem(Caps, RV_SHARE_CAPS, false)
	; Asked once. Then only looked at, for a second at the most.
	int polls = 0
	While polls < RV_ACK_POLLS && player.GetItemCount(Caps) < before + RV_SHARE_CAPS
		Utility.Wait(0.1)
		polls += 1
	EndWhile
	If player.GetItemCount(Caps) < before + RV_SHARE_CAPS
		; Fails closed: the deal is off, nothing is recorded as paid, and it is never asked for again.
		Claim = RV_NONE
		Debug.Trace("TLM_MQ02B: FAIL CLOSED: the share was asked for once and the caps did not arrive (had " + before + ", have " + player.GetItemCount(Caps) + "). The deal is off; it is not offered or asked for again. SharePending stays set. Report this line.", 2)
		Return false
	EndIf
	SharePaid = true
	SharePending = false
	TLM_G_MQ02B_Outcome.SetValueInt(RV_SHARE)
	SetStage(44)
	CourseTaken()
	Return true
EndFunction

bool Function TellLie()
	{The player chose to tell Opal the Chute took the barge. Her answer is another matter.}
	If !RoadOpen() || !GetStageDone(44) || !SharePaid || !CanSpeak(Alias_Opal)
		Return false
	EndIf
	LieTold = true
	Return true
EndFunction

bool Function LieWasHeard()
	{Opal's answer to the lie was delivered. Only now is the accepted journal true.}
	If !RoadOpen() || !LieTold
		Return false
	EndIf
	If !LieHeard
		LieHeard = true
		TLM_G_MQ02B_GrainSold.SetValueInt(1)
		SetStage(46)
	EndIf
	Return true
EndFunction

; ------------------------------------------------------------------- evidence

bool Function LearnHire(int aiHow)
	{The letter was read through, or Hatcher's admission was heard to its end.}
	If !RoadOpen()
		Return false
	EndIf
	If aiHow == RV_HIRE_LETTER
		HireRead = true
	ElseIf aiHow == RV_HIRE_ADMISSION
		HireHeard = true
	Else
		Return false
	EndIf
	If !GetStageDone(50)
		TLM_G_MQ02B_SilverRiver.SetValueInt(1)
		SetStage(50)
		; Shown or not, it is done. An objective completed without having been displayed reads as completed.
		FinishObjective(50)
	EndIf
	Return true
EndFunction

; ---------------------------------------------------------------- cut and run

bool Function CutChain()
	{The chain is cut. From here there is only the pilot lever.}
	If !RoadOpen() || !GetStageDone(30)
		Return false
	EndIf
	; No call into the game between this test and the claim.
	If Claim != RV_NONE
		Return false
	EndIf
	Claim = RV_CHUTE
	EscapePending = true
	Debug.Trace("TLM_MQ02B: the chain is cut; escape pending. No cards, no share and no fire from here; the pilot lever only")
	FinishObjective(40)
	ShowObjective(60)
	Return true
EndFunction

int Function BeginReturn()
	{The pilot lever. RV_RETURN_ESCAPE with a cut chain, RV_RETURN_TOW with a barge
	won at cards and not yet home, otherwise RV_RETURN_NONE. May be begun again.}
	If !RoadOpen()
		Return RV_RETURN_NONE
	EndIf
	If EscapePending && !GetStageDone(42)
		ReturnPending = RV_RETURN_ESCAPE
	ElseIf Claim == RV_CARDS && Cargo() == RV_CARGO_YIELDED
		ReturnPending = RV_RETURN_TOW
	Else
		Return RV_RETURN_NONE
	EndIf
	Return ReturnPending
EndFunction

int Function CompleteReturn()
	{The player reached the return dock. What arrived with them: RV_RETURN_ESCAPE
	(the Chute was run, stage 42), RV_RETURN_TOW (the whole barge), or RV_RETURN_NONE.}
	If !RoadOpen()
		Return RV_RETURN_NONE
	EndIf
	bool piloted = IsThere(Alias_Rafferty)
	bool hunted = TLM_G_MQ02B_Hatcher.GetValueInt() == RV_H_FREE && IsThere(Alias_Hatcher)
	int lashing = Cargo()
	; No call into the game between these tests and the writing down.
	If ReturnPending == RV_RETURN_ESCAPE && EscapePending
		ReturnPending = RV_RETURN_NONE
		EscapePending = false
		int units = RV_UNITS_ALONE
		If piloted
			units = RV_UNITS_PILOTED
		EndIf
		TLM_G_MQ02B_Recovered.SetValueInt(units)
		TLM_G_MQ02B_Cargo.SetValueInt(RV_CARGO_HOME_REDUCED)
		TLM_G_MQ02B_GrainHome.SetValueInt(1)
		TLM_G_MQ02B_Outcome.SetValueInt(RV_CHUTE)
		If hunted
			TLM_G_MQ02B_HatcherHunting.SetValueInt(1)
		EndIf
		SetStage(42)
		CourseTaken()
		Return RV_RETURN_ESCAPE
	EndIf
	If ReturnPending == RV_RETURN_TOW && lashing == RV_CARGO_YIELDED
		ReturnPending = RV_RETURN_NONE
		TLM_G_MQ02B_Recovered.SetValueInt(RV_UNITS_WHOLE)
		TLM_G_MQ02B_Cargo.SetValueInt(RV_CARGO_HOME_WHOLE)
		TLM_G_MQ02B_GrainHome.SetValueInt(1)
		Debug.Trace("TLM_MQ02B: the barge won at cards is at the landing, whole")
		CourseTaken()
		Return RV_RETURN_TOW
	EndIf
	Return RV_RETURN_NONE
EndFunction

; ----------------------------------------------------------------------- fire

bool Function WarnOfFire()
	{Who and what is aboard was said, by Rafferty or by the action's own text.}
	If !RoadOpen() || !GetStageDone(30) || Claim != RV_NONE
		Return false
	EndIf
	FireWarned = true
	Return true
EndFunction

bool Function OrderFire()
	{The explicit confirmation at the fire control. The order cannot be taken back; the outcome is recorded by FireDone.}
	If !RoadOpen() || !GetStageDone(30) || !FireWarned
		Return false
	EndIf
	; No call into the game between this test and the claim.
	If Claim != RV_NONE
		Return false
	EndIf
	Claim = RV_FIRE
	Burning = true
	Return true
EndFunction

bool Function FireDone()
	{The fire was staged and seen: the occupied Queen and the cargo lashed to her are lost.}
	If !IsRunning() || Claim != RV_FIRE || !Burning
		Return false
	EndIf
	Burning = false
	TLM_G_MQ02B_Cargo.SetValueInt(RV_CARGO_DESTROYED)
	TLM_G_MQ02B_Recovered.SetValueInt(0)
	TLM_G_MQ02B_QueenBurned.SetValueInt(1)
	TLM_G_MQ02B_Outcome.SetValueInt(RV_FIRE)
	; A man who was aboard and alive is not counted dead: he is not accounted for.
	If TLM_G_MQ02B_Hatcher.GetValueInt() == RV_H_FREE && HatcherState() == RV_H_FREE
		TLM_G_MQ02B_Hatcher.SetValueInt(RV_H_UNACCOUNTED)
	EndIf
	SetStage(43)
	CourseTaken()
	Return true
EndFunction

; ------------------------------------------------------------------ judgments

bool Function Hang()
	{"He's yours, Opal." Hatcher alive and free, Opal alive and there: he is
	taken to the steeple and hanged. Recorded only if he is then dead.}
	If !RoadOpen() || !HatcherToJudge() || !CanSpeak(Alias_Opal)
		Return false
	EndIf
	Actor hatcher = Person(Alias_Hatcher)
	ObjectReference ring = None
	If Alias_Steeple
		ring = Alias_Steeple.GetReference()
	EndIf
	; No call into the game between this test and the claim.
	If Judging || TLM_G_MQ02B_Hatcher.GetValueInt() != RV_H_FREE
		Return false
	EndIf
	Judging = true
	If ring
		hatcher.MoveTo(ring)
	EndIf
	hatcher.Kill()
	If !hatcher.IsDead()
		Judging = false
		Debug.Trace("TLM_MQ02B: the hanging was ordered and Hatcher is not dead; nothing is recorded", 2)
		Return false
	EndIf
	TLM_G_MQ02B_Hatcher.SetValueInt(RV_H_HANGED)
	TLM_G_MQ02B_HatcherHanged.SetValueInt(1)
	SetStage(60)
	Judging = false
	Return true
EndFunction

bool Function Custody()
	{"He goes to Pritchard, alive." Hatcher alive and free, Pritchard alive and
	there: Hatcher is taken to him. Recorded only if he is then alive beside him.}
	If !RoadOpen() || !HatcherToJudge() || !SheriffCanReceive()
		Return false
	EndIf
	Actor hatcher = Person(Alias_Hatcher)
	Actor sheriff = Person(Alias_MercySheriff)
	; No call into the game between this test and the claim.
	If Judging || TLM_G_MQ02B_Hatcher.GetValueInt() != RV_H_FREE
		Return false
	EndIf
	Judging = true
	hatcher.MoveTo(sheriff, 96.0, 96.0, 0.0)
	bool arrived = !hatcher.IsDead() && !sheriff.IsDead() && hatcher.GetParentCell() == sheriff.GetParentCell() && hatcher.GetDistance(sheriff) < RV_CUSTODY_REACH
	If !arrived
		Judging = false
		Debug.Trace("TLM_MQ02B: Hatcher was sent to Pritchard and is not alive beside him; nothing is recorded", 2)
		Return false
	EndIf
	hatcher.SetRestrained(true)
	TLM_G_MQ02B_Hatcher.SetValueInt(RV_H_CUSTODY)
	SetStage(61)
	Judging = false
	Return true
EndFunction

bool Function Release()
	{"Let him keep his boat." Hatcher alive and free.}
	If !RoadOpen() || !HatcherToJudge()
		Return false
	EndIf
	; No call into the game between this test and the claim.
	If Judging || TLM_G_MQ02B_Hatcher.GetValueInt() != RV_H_FREE
		Return false
	EndIf
	TLM_G_MQ02B_Hatcher.SetValueInt(RV_H_RELEASED)
	TLM_G_MQ02B_HatcherFriend.SetValueInt(1)
	Return true
EndFunction

Function HatcherDied()
	{Heard from his alias. Not the hanging, which writes its own record.}
	If Judging
		Return
	EndIf
	int fate = TLM_G_MQ02B_Hatcher.GetValueInt()
	If fate == RV_H_FREE || fate == RV_H_RELEASED
		TLM_G_MQ02B_Hatcher.SetValueInt(RV_H_DEAD)
	EndIf
EndFunction

Function MarkDenied()
	DeniedSaid = true
EndFunction

; ------------------------------------------------------------------- leaving

bool Function Complete()
	{The player has left Greenwater with one course carried through.}
	If !IsRunning() || !CanComplete()
		Return false
	EndIf
	If !GetStageDone(100)
		FinishObjective(80)
		SetStage(100)
	EndIf
	Return true
EndFunction

bool Function GiveReport()
	{Pritchard was told what became of the grain.}
	If !GetStageDone(100)
		Return false
	EndIf
	TLM_G_MQ02B_Reported.SetValueInt(1)
	Return true
EndFunction

; ============================================================ one-time things

bool Function GiveOne(Form akWhat)
	{One of something into the player's inventory, seen to have arrived.}
	Actor player = Game.GetPlayer()
	int before = player.GetItemCount(akWhat)
	player.AddItem(akWhat, 1, false)
	int polls = 0
	While polls < RV_ACK_POLLS && player.GetItemCount(akWhat) <= before
		Utility.Wait(0.1)
		polls += 1
	EndWhile
	Return player.GetItemCount(akWhat) > before
EndFunction

bool Function GiveLetter()
	{The letter of hire, read through, goes with the player: once.}
	If !RoadOpen() || !HireLetter
		Return false
	EndIf
	If LetterGiven || LetterPending
		Return false
	EndIf
	LetterPending = true
	If GiveOne(HireLetter)
		LetterGiven = true
		LetterPending = false
		Return true
	EndIf
	Debug.Trace("TLM_MQ02B: FAIL CLOSED: the letter of hire was asked for once and is not in the inventory. It is not asked for again. What was read is still known. Report this line.", 2)
	Return false
EndFunction

bool Function GivePortion(int aiWhich)
	{One of the three small portions of food, from somebody alive and there to
	give it: once each. False, with nothing given, if there is no food item in
	this build, if it was given or asked for before, or if the game did not
	honour the request.}
	If !RoadOpen() || !Meal
		Return false
	EndIf
	If aiWhich == RV_GRANT_BOWL
		If BowlGiven || BowlPending || !CanSpeak(Alias_Opal)
			Return false
		EndIf
		BowlPending = true
		If GiveOne(Meal)
			BowlGiven = true
			BowlPending = false
			Return true
		EndIf
	ElseIf aiWhich == RV_GRANT_CUP
		If CupGiven || CupPending || !LieHeard || !CanSpeak(Alias_Opal)
			Return false
		EndIf
		CupPending = true
		If GiveOne(Meal)
			CupGiven = true
			CupPending = false
			Return true
		EndIf
	ElseIf aiWhich == RV_GRANT_RELIEF
		If ReliefGiven || ReliefPending || !CanSpeak(Alias_Belden)
			Return false
		EndIf
		If !GetStageDone(43) && !GetStageDone(44)
			Return false
		EndIf
		ReliefPending = true
		If GiveOne(Meal)
			ReliefGiven = true
			ReliefPending = false
			Return true
		EndIf
	Else
		Return false
	EndIf
	Debug.Trace("TLM_MQ02B: FAIL CLOSED: portion " + aiWhich + " was asked for once and is not in the inventory. It is not asked for again and is not said to have been given. Report this line.", 2)
	Return false
EndFunction

bool Function HasMeal()
	{There is a food item in this build to give.}
	Return Meal != None
EndFunction

Function TraceState()
	{One line in the script log. From the console: cqf TLM_MQ02B TraceState}
	Debug.Trace("TLM_MQ02B: outcome=" + Outcome() + " claim=" + Claim + " cargo=" + Cargo() + " recovered=" + Recovered() + " hatcher=" + HatcherState() + " card=" + CardResult + " escapePending=" + EscapePending + " returnPending=" + ReturnPending + " fireWarned=" + FireWarned + " sharePaid=" + SharePaid + " sharePending=" + SharePending + " lieTold=" + LieTold + " lieHeard=" + LieHeard + " knowsHire=" + GetStageDone(50) + " hireRead=" + HireRead + " hireHeard=" + HireHeard + " approach=" + Approach + " complete=" + GetStageDone(100) + " reported=" + IsReported())
EndFunction
