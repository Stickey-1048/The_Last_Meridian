Scriptname TLM:GreenwaterWalk extends Quest
{Development only, attached to TLM_GW: the Greenwater greybox of
GREENWATER-STORY-001 (docs/design/GREENWATER_STORY_001.md and its order). It
must be removed before any release, with its quest, TLM:GreenwaterTalk and
the records the builder marks "Greenwater".

The plugin places a travel point at Mercy Crossing and, switched off, three
connected greybox zones: the Greenwater landing and cook-shed, the Queen of
Tellico's deck with the barge lashed to her off side, and a short strip that
stands for Hangman's Chute and ends at the return dock. This script
  - puts each placed reference into the alias of TLM_MQ02B that is meant for
    it and switches the zones on, when the player first travels;
  - shows the lines of the accepted writing as boxes and works the pieces. A
    player uses a person or a piece, TLM:GreenwaterTalk on its alias calls
    Used, and what fits the road as it stands is shown;
  - asks TLM:MQ02BQuest before and after every box whether the thing chosen
    may still happen, and lets that script write down what did.

It decides nothing about the road itself. What a stage or a fact means, and
when it is earned, is TLM:MQ02BQuest's and is not repeated here.

Every spoken line, button and document page is copied from the accepted
writing; which field each comes from is in
docs/design/GREENWATER_STORY_001_MAPPING.json. Text in square brackets is
this build speaking, not a character.

What is representation and says so on the screen: the zones are flat
greybox; the skiff, the tow and the Chute are a move of the player and a
short walk; the fire is a marker and pieces switched off. Nobody's death is
counted that did not happen to an actor.

NOT COMPILED. NOT RUN IN THE GAME. It runs in the project's stand-in engine
(tools/papyrus_sim/test_greenwater.py).}

Group Quests
	Quest Property TLM_MQ02B Auto Const Mandatory
	Quest Property TLM_MQ01 Auto Const Mandatory
	{Read only.}
	GlobalVariable Property TLM_G_MQ01_Done Auto Const Mandatory
	{Read only.}
EndGroup

Group Placed
	ReferenceAlias[] Property ZoneOn Auto Const
	{The pieces switched on when the player first travels. Not the travel
	point, which is on from the start, nor what only an outcome brings.}
	ReferenceAlias[] Property CastFrom Auto Const
	{What is put where: the alias of this quest that holds the reference ...}
	ReferenceAlias[] Property CastInto Auto Const
	{... and the alias of TLM_MQ02B it is put into.}
	string[] Property CastNames Auto Const
	ReferenceAlias Property Alias_MercyTravel Auto Const Mandatory
	ReferenceAlias Property Alias_MercyReturn Auto Const Mandatory
	ReferenceAlias Property Alias_Arrival Auto Const Mandatory
	ReferenceAlias Property Alias_OffSideArrival Auto Const Mandatory
	ReferenceAlias Property Alias_ChuteStart Auto Const Mandatory
	ReferenceAlias Property Alias_Opal Auto Const Mandatory
	ReferenceAlias Property Alias_Hatcher Auto Const Mandatory
	ReferenceAlias Property Alias_Rafferty Auto Const Mandatory
	ReferenceAlias Property Alias_Belden Auto Const Mandatory
	ReferenceAlias Property Alias_Crew1 Auto Const Mandatory
	ReferenceAlias Property Alias_Crew2 Auto Const Mandatory
	ReferenceAlias Property Alias_CargoLashed Auto Const Mandatory
	ReferenceAlias Property Alias_CargoWhole Auto Const Mandatory
	ReferenceAlias Property Alias_CargoReduced Auto Const Mandatory
	ReferenceAlias Property Alias_Table Auto Const Mandatory
	ReferenceAlias Property Alias_Chain Auto Const Mandatory
	ReferenceAlias Property Alias_Pilot Auto Const Mandatory
	ReferenceAlias Property Alias_FireControl Auto Const Mandatory
	ReferenceAlias Property Alias_Burnt Auto Const Mandatory
EndGroup

Group Speech
	Message Property SayOpalDefault Auto Const
	Message Property SayOpalFirst Auto Const
	{Buttons: what do you want done, why not take it back, take a bowl.}
	Message Property SayOpalWants Auto Const
	Message Property SayOpalGuns Auto Const
	Message Property SayOpalBowl Auto Const
	Message Property SayOpalAfterWon Auto Const
	{Buttons: he's yours, he goes to Pritchard, let him keep his boat.}
	Message Property SayOpalAfterWonNoSheriff Auto Const
	{Buttons: he's yours, let him keep his boat.}
	Message Property SayOpalWonHatcherDead Auto Const
	Message Property SayOpalDenied Auto Const
	Message Property SayOpalAfterChute Auto Const
	Message Property SayOpalAfterFire Auto Const
	Message Property SayOpalAfterShare Auto Const
	Message Property SayOpalAfterHanging Auto Const
	Message Property SayRaffertyDefault Auto Const
	Message Property SayRaffertySkiff Auto Const
	{Buttons: the gangway, the off side, how do you know the barge.}
	Message Property SayRaffertyConfess Auto Const
	Message Property SayRaffertyChain Auto Const
	{Buttons: cut the barge loose, burn the occupied Queen, not yet.}
	Message Property SayRaffertyRan Auto Const
	Message Property SayRaffertyBurned Auto Const
	Message Property SayHatcherDefault Auto Const
	Message Property SayHatcherTable Auto Const
	{Buttons: deal, sell me a share, who paid you, leave the table.}
	Message Property SayHatcherTableNoShare Auto Const
	{Buttons: deal, who paid you, leave the table.}
	Message Property SayHatcherLost Auto Const
	{Buttons: he's yours Opal, he goes to Pritchard, let him keep his boat.}
	Message Property SayHatcherLostNoSheriff Auto Const
	{Buttons: he's yours Opal, let him keep his boat, say nothing.}
	Message Property SayHatcherLostNoOpal Auto Const
	{The approved prefix only. Buttons: he goes to Pritchard, let him keep his boat, say nothing.}
	Message Property SayHatcherLostAlone Auto Const
	{The approved prefix only. Buttons: let him keep his boat, say nothing.}
	Message Property SayHatcherWon Auto Const
	{Buttons: sell me a share, leave the table.}
	Message Property SayHatcherWonNoShare Auto Const
	{Button: leave the table.}
	Message Property SayHatcherShare Auto Const
	{Buttons: done, no.}
	Message Property SayHatcherPaidA Auto Const
	Message Property SayHatcherPaidB Auto Const
	{Button: square mark, go on.}
	Message Property SayBeldenRelief Auto Const
	Message Property SayReportKnown Auto Const
	{Pritchard. Buttons: report, later.}
	Message Property SayReportUnknown Auto Const
EndGroup

Group Pages
	Message Property BoardPage1 Auto Const
	Message Property BoardPage2 Auto Const
	Message Property BoardPage3 Auto Const
	Message Property BoardPage4 Auto Const
	Message Property LetterPage1 Auto Const
	Message Property LetterPage2 Auto Const
	Message Property LetterPage3 Auto Const
	Message Property LetterPage4 Auto Const
EndGroup

Group Technical
	Message Property AskTravel Auto Const
	{Buttons: travel, not now.}
	Message Property AskTravelAgain Auto Const
	Message Property NoteTravelNotYet Auto Const
	Message Property NoteTravelFailed Auto Const
	Message Property AskChain Auto Const
	{The occupancy warning as labelled action text, when Rafferty cannot say it. Buttons as SayRaffertyChain.}
	Message Property NoteChainCut Auto Const
	Message Property NoteChainNothing Auto Const
	Message Property NoteFireNotWarned Auto Const
	Message Property NoteFireWarned Auto Const
	Message Property AskFire Auto Const
	{Buttons: burn the occupied Queen, not yet.}
	Message Property NoteFireScene Auto Const
	Message Property NoteFireFailed Auto Const
	Message Property NotePilotNothing Auto Const
	Message Property NoteChuteScene Auto Const
	Message Property NoteTowScene Auto Const
	Message Property NoteSkiffScene Auto Const
	Message Property NoteHomeWhole Auto Const
	Message Property NoteHomePiloted Auto Const
	Message Property NoteHomeAlone Auto Const
	Message Property AskLie Auto Const
	{Buttons: tell her the Chute took the barge, say nothing of it.}
	Message Property NoteShareFailed Auto Const
	Message Property NoteTableEmpty Auto Const
	Message Property NoteHatcherCustody Auto Const
	Message Property NoteNoMeal Auto Const
	Message Property NoteJudgmentFailed Auto Const
	Message Property AskLeaveResolved Auto Const
	{Buttons: leave for Mercy, stay.}
	Message Property AskLeaveUnresolved Auto Const
	Message Property AskLeaveAgain Auto Const
	Message Property NoteRoadComplete Auto Const
	Message Property NoteLeftUnresolved Auto Const
	Message Property ReportWhole Auto Const
	Message Property ReportReduced Auto Const
	Message Property ReportDestroyed Auto Const
	Message Property ReportSold Auto Const
	Message Property ReportEndKnown Auto Const
	Message Property ReportEndUnknown Auto Const
	Message Property LabelLanding Auto Const
	Message Property LabelQueen Auto Const
	Message Property LabelChute Auto Const
	Message Property LabelSteeple Auto Const
	Message Property LabelBurnt Auto Const
	Message Property LabelCargoLashed Auto Const
	Message Property LabelCargoWhole Auto Const
	Message Property LabelCargoPiloted Auto Const
	Message Property LabelCargoAlone Auto Const
EndGroup

; ----------------------------------------------------------------- constants

; Who is who: the numbers TLM:GreenwaterTalk carries on each alias.
int GW_TRAVEL = 1 Const
int GW_LANDING = 2 Const
int GW_OPAL = 3 Const
int GW_BOARD = 4 Const
int GW_RAFFERTY = 5 Const
int GW_SKIFF = 6 Const
int GW_GANGWAY = 7 Const
int GW_OFFSIDE = 8 Const
int GW_HATCHER = 9 Const
int GW_TABLE = 10 Const
int GW_STRONGBOX = 11 Const
int GW_CHAIN = 12 Const
int GW_PILOT = 13 Const
int GW_FIRE = 14 Const
int GW_DOCK = 15 Const
int GW_EXIT = 16 Const
int GW_BELDEN = 17 Const
int GW_CREW1 = 18 Const
int GW_CREW2 = 19 Const
int GW_LABEL_LANDING = 20 Const
int GW_LABEL_QUEEN = 21 Const
int GW_LABEL_CHUTE = 22 Const
int GW_CARGO = 23 Const
int GW_STEEPLE = 24 Const
int GW_BURNT = 25 Const

; How the Queen was boarded (TLM:MQ02BQuest.Board).
int BOARD_GANGWAY = 1 Const
int BOARD_OFFSIDE = 2 Const
int BOARD_DECK = 3 Const

; The same numbers as TLM:MQ02BQuest; a test compares the two scripts.
int RV_NONE = 0 Const
int RV_CARDS = 41 Const
int RV_CHUTE = 42 Const
int RV_FIRE = 43 Const
int RV_SHARE = 44 Const
int RV_CARGO_LASHED = 0 Const
int RV_CARGO_YIELDED = 1 Const
int RV_CARGO_HOME_WHOLE = 2 Const
int RV_CARGO_HOME_REDUCED = 3 Const
int RV_CARGO_DESTROYED = 4 Const
int RV_H_FREE = 0 Const
int RV_H_RELEASED = 1 Const
int RV_H_CUSTODY = 2 Const
int RV_H_HANGED = 3 Const
int RV_H_DEAD = 4 Const
int RV_H_UNACCOUNTED = 5 Const
int RV_CARD_WON = 2 Const
int RV_CARD_LOST = 1 Const
int RV_UNITS_PILOTED = 8 Const
int RV_RETURN_ESCAPE = 1 Const
int RV_RETURN_TOW = 2 Const
int RV_HIRE_LETTER = 1 Const
int RV_HIRE_ADMISSION = 2 Const
int RV_GRANT_BOWL = 1 Const
int RV_GRANT_CUP = 2 Const
int RV_GRANT_RELIEF = 3 Const

float ARRIVE_REACH = 1500.0 Const
int TABLE_ROUNDS = 3 Const

; ------------------------------------------------------------------- state

; The travel point is on. The zones are set up. A box is open: claimed with
; no call into the game between the test and the claim.
bool doorOpen = false
bool zonesUp = false
bool talking = false
bool ranSaid = false
bool burnedSaid = false

; ================================================================== set-up

TLM:MQ02BQuest Function Road()
	Return TLM_MQ02B as TLM:MQ02BQuest
EndFunction

ObjectReference Function Piece(ReferenceAlias akAlias)
	If !akAlias
		Return None
	EndIf
	Return akAlias.GetReference()
EndFunction

Function OpenDoor()
	{Called by TLM:Act1Walk when the first section is set up: this quest runs
	and the Mercy travel point is switched on. Nothing of Greenwater is.}
	If doorOpen
		Return
	EndIf
	If !IsRunning()
		bool started = Start()
		bool running = IsRunning()
		If !started || !running
			Debug.Trace("TLM_GW: its quest is not running and could not be started (Start returned " + started + ", running " + running + "); there is no travel point", 2)
			Return
		EndIf
	EndIf
	ObjectReference point = Piece(Alias_MercyTravel)
	If !point
		Debug.Trace("TLM_GW: the Mercy travel point is not placed; Greenwater cannot be reached", 2)
		Return
	EndIf
	point.EnableNoWait()
	doorOpen = true
	Debug.Trace("TLM_GW: the Mercy travel point is on")
EndFunction

bool Function MainQuestOver()
	{The dispatch was delivered, the delivery acknowledged and the debrief ended.}
	If !TLM_MQ01.GetStageDone(50) || !TLM_MQ01.GetStageDone(60) || !TLM_MQ01.GetStageDone(100)
		Return false
	EndIf
	If TLM_G_MQ01_Done.GetValueInt() != 1
		Return false
	EndIf
	TLM:MQ01Quest mainScript = TLM_MQ01 as TLM:MQ01Quest
	If !mainScript
		Return false
	EndIf
	Return mainScript.DeliveryAcknowledged()
EndFunction

bool Function SetUp()
	{Once, at the first travel: the road's quest is running, each placed
	reference is in the alias of TLM_MQ02B meant for it, and the zones are on.}
	If zonesUp
		Return true
	EndIf
	TLM:MQ02BQuest river = Road()
	If !river || !river.Begin()
		Return false
	EndIf
	int unfilled = 0
	int i = 0
	While i < CastFrom.Length
		ObjectReference placedRef = CastFrom[i].GetReference()
		If placedRef
			CastInto[i].ForceRefTo(placedRef)
		EndIf
		If !placedRef || CastInto[i].GetReference() != placedRef
			unfilled += 1
			Debug.Trace("TLM_GW: not put where it belongs: " + CastNames[i])
		EndIf
		i += 1
	EndWhile
	i = 0
	While i < ZoneOn.Length
		ObjectReference thing = ZoneOn[i].GetReference()
		If thing
			thing.EnableNoWait()
		EndIf
		i += 1
	EndWhile
	zonesUp = true
	Debug.Trace("TLM_GW: Greenwater is set up; aliases of TLM_MQ02B left empty: " + unfilled)
	Return true
EndFunction

Function SwitchOn(ReferenceAlias akAlias)
	ObjectReference thing = Piece(akAlias)
	If thing && thing.IsDisabled()
		thing.EnableNoWait()
	EndIf
EndFunction

Function SwitchOff(ReferenceAlias akAlias)
	ObjectReference thing = Piece(akAlias)
	If thing && !thing.IsDisabled()
		thing.Disable()
	EndIf
EndFunction

Function Refresh()
	{The pieces as the road's facts say they stand. Reads the facts; writes none.
	Called on arrival and after anything is settled, so that coming back finds
	what was left.}
	TLM:MQ02BQuest river = Road()
	If !river || !zonesUp
		Return
	EndIf
	int lashing = river.Cargo()
	If lashing == RV_CARGO_LASHED || lashing == RV_CARGO_YIELDED
		SwitchOn(Alias_CargoLashed)
		SwitchOff(Alias_CargoWhole)
		SwitchOff(Alias_CargoReduced)
	ElseIf lashing == RV_CARGO_HOME_WHOLE
		SwitchOff(Alias_CargoLashed)
		SwitchOn(Alias_CargoWhole)
		SwitchOff(Alias_CargoReduced)
	ElseIf lashing == RV_CARGO_HOME_REDUCED
		SwitchOff(Alias_CargoLashed)
		SwitchOff(Alias_CargoWhole)
		SwitchOn(Alias_CargoReduced)
	Else
		SwitchOff(Alias_CargoLashed)
		SwitchOff(Alias_CargoWhole)
		SwitchOff(Alias_CargoReduced)
	EndIf
	int course = river.Outcome()
	If course == RV_FIRE || river.IsBurning()
		; The deck's working pieces are gone. The strongbox is not: what was in it can still be read.
		SwitchOn(Alias_Burnt)
		SwitchOff(Alias_Table)
		SwitchOff(Alias_Chain)
		SwitchOff(Alias_Pilot)
		SwitchOff(Alias_FireControl)
		SwitchOff(Alias_Crew1)
		SwitchOff(Alias_Crew2)
		int fate = river.HatcherState()
		If fate == RV_H_FREE || fate == RV_H_UNACCOUNTED
			SwitchOff(Alias_Hatcher)
		EndIf
	EndIf
	If course == RV_FIRE || course == RV_SHARE
		; Delegate Belden's wagon comes when the grain is not coming.
		Actor belden = Alias_Belden.GetActorReference()
		If belden && !belden.IsDead()
			SwitchOn(Alias_Belden)
		EndIf
	EndIf
EndFunction

; ==================================================================== lines

int Function ShowBox(Message akLine)
	{Shows a line. The button pressed; -1 if there was no line or it was not a box.}
	If !akLine
		Return -1
	EndIf
	Return akLine.Show()
EndFunction

bool Function Said(Message akLine)
	{A line with one button was shown and answered.}
	Return ShowBox(akLine) == 0
EndFunction

bool Function ReadPages(Message akOne, Message akTwo, Message akThree, Message akFour)
	{A document, page by page. True only if every page there is was shown and answered.}
	If !akOne || ShowBox(akOne) != 0
		Return false
	EndIf
	If akTwo
		If ShowBox(akTwo) != 0
			Return false
		EndIf
	EndIf
	If akThree
		If ShowBox(akThree) != 0
			Return false
		EndIf
	EndIf
	If akFour
		If ShowBox(akFour) != 0
			Return false
		EndIf
	EndIf
	Return true
EndFunction

; ================================================================ what is used

Function Used(int aiWho)
	{Called by TLM:GreenwaterTalk when the player uses a person or a piece.}
	; Nothing between the test and the claim calls into the game, so two
	; activations cannot both pass.
	If talking
		Return
	EndIf
	talking = true
	TLM:MQ02BQuest river = Road()
	If !river
		Debug.Trace("TLM_GW: TLM_MQ02B does not carry TLM:MQ02BQuest; nothing can be used", 2)
	ElseIf aiWho == GW_TRAVEL
		Travel(river)
	ElseIf !zonesUp
		; A piece of Greenwater that the player was never sent to: nothing.
	ElseIf aiWho == GW_EXIT
		; The way back is never shut, whatever has or has not been stepped on.
		Leave(river)
	ElseIf !river.RoadOpen()
		; Before the landing was stepped onto, or with the player dead: the label and nothing else.
		If aiWho == GW_LABEL_LANDING
			ShowBox(LabelLanding)
		EndIf
	ElseIf aiWho == GW_OPAL
		TalkOpal(river)
	ElseIf aiWho == GW_BOARD
		ReadPages(BoardPage1, BoardPage2, BoardPage3, BoardPage4)
	ElseIf aiWho == GW_RAFFERTY
		TalkRafferty(river)
	ElseIf aiWho == GW_SKIFF
		TakeSkiff(river)
	ElseIf aiWho == GW_HATCHER || aiWho == GW_TABLE
		AtTable(river)
	ElseIf aiWho == GW_STRONGBOX
		OpenStrongbox(river)
	ElseIf aiWho == GW_CHAIN
		AtChain(river)
	ElseIf aiWho == GW_PILOT
		AtPilot(river)
	ElseIf aiWho == GW_FIRE
		AtFire(river)
	ElseIf aiWho == GW_BELDEN
		TalkBelden(river)
	ElseIf aiWho == GW_LABEL_LANDING
		ShowBox(LabelLanding)
	ElseIf aiWho == GW_LABEL_QUEEN
		ShowBox(LabelQueen)
	ElseIf aiWho == GW_LABEL_CHUTE
		ShowBox(LabelChute)
	ElseIf aiWho == GW_STEEPLE
		ShowBox(LabelSteeple)
	ElseIf aiWho == GW_BURNT
		ShowBox(LabelBurnt)
	ElseIf aiWho == GW_CARGO
		LookAtCargo(river)
	EndIf
	talking = false
EndFunction

Function Entered(int aiWho)
	{Called by TLM:GreenwaterTalk when the player walks into one of the boxes.}
	TLM:MQ02BQuest river = Road()
	If !river || !zonesUp
		Return
	EndIf
	If aiWho == GW_LANDING
		river.Arrive()
	ElseIf aiWho == GW_GANGWAY
		Boarded(river, BOARD_GANGWAY)
	ElseIf aiWho == GW_OFFSIDE
		Boarded(river, BOARD_OFFSIDE)
	ElseIf aiWho == GW_DOCK
		ReachedDock(river)
	EndIf
EndFunction

Function Died(int aiWho, bool abByPlayer)
	{Called by TLM:GreenwaterTalk when one of the people dies.}
	TLM:MQ02BQuest river = Road()
	If !river
		Return
	EndIf
	If aiWho == GW_HATCHER
		river.HatcherDied()
	EndIf
	If abByPlayer
		Attacked(aiWho)
	EndIf
EndFunction

Function Attacked(int aiWho)
	{The player attacked Hatcher or one of the Queen's crew: those of them who
	live fight back. Nobody else does, and declining anything is not an attack.}
	If aiWho != GW_HATCHER && aiWho != GW_CREW1 && aiWho != GW_CREW2
		Return
	EndIf
	TLM:MQ02BQuest river = Road()
	If river
		; A man in Pritchard's irons, or hanged, has no crew to call on.
		int fate = river.HatcherState()
		If fate == RV_H_CUSTODY || fate == RV_H_HANGED
			Return
		EndIf
	EndIf
	Actor player = Game.GetPlayer()
	FightBack(Alias_Hatcher, player)
	FightBack(Alias_Crew1, player)
	FightBack(Alias_Crew2, player)
EndFunction

Function FightBack(ReferenceAlias akAlias, Actor akTarget)
	Actor who = akAlias.GetActorReference()
	If who && !who.IsDead() && !who.IsDisabled()
		who.StartCombat(akTarget)
	EndIf
EndFunction

; =================================================================== travel

Function Travel(TLM:MQ02BQuest akRiver)
	{The Mercy travel point: the explicit way to Greenwater, and nothing else.}
	If !MainQuestOver()
		ShowBox(NoteTravelNotYet)
		Return
	EndIf
	int pick = -1
	If akRiver.GetStageDone(100)
		pick = ShowBox(AskTravelAgain)
	Else
		pick = ShowBox(AskTravel)
	EndIf
	If pick != 0
		Return
	EndIf
	Actor player = Game.GetPlayer()
	If !MainQuestOver() || !player || player.IsDead()
		Return
	EndIf
	ObjectReference arrival = Piece(Alias_Arrival)
	If !arrival || !SetUp()
		ShowBox(NoteTravelFailed)
		Return
	EndIf
	Refresh()
	player.MoveTo(arrival)
EndFunction

Function Leave(TLM:MQ02BQuest akRiver)
	{The skiff to Mercy. Leaving with nothing settled settles nothing.}
	bool resolved = akRiver.CanComplete()
	int pick = -1
	If akRiver.GetStageDone(100)
		pick = ShowBox(AskLeaveAgain)
	ElseIf resolved
		pick = ShowBox(AskLeaveResolved)
	Else
		pick = ShowBox(AskLeaveUnresolved)
	EndIf
	If pick != 0
		Return
	EndIf
	Actor player = Game.GetPlayer()
	ObjectReference back = Piece(Alias_MercyReturn)
	If !player || player.IsDead() || !back
		Return
	EndIf
	player.MoveTo(back)
	; Only a player who is seen to have arrived has left.
	If player.GetParentCell() != back.GetParentCell() || player.GetDistance(back) > ARRIVE_REACH
		Debug.Trace("TLM_GW: the player was sent to Mercy and is not there; the road is not completed by it", 2)
		Return
	EndIf
	If akRiver.GetStageDone(100)
		Return
	EndIf
	If akRiver.CanComplete()
		If akRiver.Complete()
			ShowBox(NoteRoadComplete)
		EndIf
	Else
		ShowBox(NoteLeftUnresolved)
	EndIf
EndFunction

; ============================================================== Opal Starnes

Function TalkOpal(TLM:MQ02BQuest akRiver)
	If !akRiver.OpalCanSpeak()
		Return
	EndIf
	int course = akRiver.Outcome()
	int lashing = akRiver.Cargo()
	int fate = akRiver.HatcherState()
	If course == RV_CARDS && lashing == RV_CARGO_HOME_WHOLE
		; Everything she says of the barge won at cards waits for the barge.
		If fate == RV_H_HANGED && akRiver.GetStageDone(60)
			ShowBox(SayOpalAfterHanging)
		ElseIf fate == RV_H_FREE && akRiver.HatcherToJudge()
			JudgeBeforeOpal(akRiver)
		ElseIf fate == RV_H_DEAD
			ShowBox(SayOpalWonHatcherDead)
		ElseIf (fate == RV_H_RELEASED || fate == RV_H_CUSTODY) && !akRiver.IsDeniedSaid()
			Deny(akRiver)
		Else
			ShowBox(SayOpalDefault)
		EndIf
	ElseIf course == RV_CHUTE && akRiver.GetStageDone(42) && lashing == RV_CARGO_HOME_REDUCED && akRiver.Recovered() > 0
		ShowBox(SayOpalAfterChute)
	ElseIf course == RV_FIRE && akRiver.GetStageDone(43) && lashing == RV_CARGO_DESTROYED
		ShowBox(SayOpalAfterFire)
	ElseIf course == RV_SHARE && akRiver.GetStageDone(44) && akRiver.IsSharePaid()
		AfterShare(akRiver)
	ElseIf course == RV_NONE && !akRiver.GetStageDone(20) && !akRiver.IsEscapePending()
		FirstMeeting(akRiver)
	Else
		ShowBox(SayOpalDefault)
	EndIf
EndFunction

Function FirstMeeting(TLM:MQ02BQuest akRiver)
	int pick = ShowBox(SayOpalFirst)
	If !akRiver.OpalCanSpeak()
		Return
	EndIf
	If pick == 0
		; Heard out: the stage is hers to have said, and the player's to have answered.
		If Said(SayOpalWants)
			akRiver.HearOpal()
		EndIf
	ElseIf pick == 1
		ShowBox(SayOpalGuns)
	ElseIf pick == 2
		If Said(SayOpalBowl)
			Portion(akRiver, RV_GRANT_BOWL)
		EndIf
	EndIf
EndFunction

Function JudgeBeforeOpal(TLM:MQ02BQuest akRiver)
	{The barge is home, Hatcher lives and is free, and she asks what is to be done with him.}
	bool sheriff = akRiver.SheriffCanReceive()
	int pick = -1
	If sheriff
		pick = ShowBox(SayOpalAfterWon)
	Else
		pick = ShowBox(SayOpalAfterWonNoSheriff)
		If pick == 1
			pick = 2
		EndIf
	EndIf
	If pick == 0
		Judge(akRiver, 60)
	ElseIf pick == 1
		If Judge(akRiver, 61)
			Deny(akRiver)
		EndIf
	ElseIf pick == 2
		If Judge(akRiver, 1)
			Deny(akRiver)
		EndIf
	EndIf
EndFunction

Function Deny(TLM:MQ02BQuest akRiver)
	If !akRiver.OpalCanSpeak() || akRiver.IsDeniedSaid()
		Return
	EndIf
	If Said(SayOpalDenied)
		akRiver.MarkDenied()
	EndIf
EndFunction

Function AfterShare(TLM:MQ02BQuest akRiver)
	{The share is paid. Whether she is lied to is the player's to choose here, and only here.}
	If akRiver.IsLieHeard()
		ShowBox(SayOpalDefault)
		Return
	EndIf
	If !akRiver.IsLieTold()
		If ShowBox(AskLie) != 0
			Return
		EndIf
		If !akRiver.TellLie()
			Return
		EndIf
	EndIf
	; Told. Her answer, and only then what the journal says of it.
	If !akRiver.OpalCanSpeak()
		Return
	EndIf
	If Said(SayOpalAfterShare)
		If akRiver.LieWasHeard()
			Portion(akRiver, RV_GRANT_CUP)
		EndIf
	EndIf
EndFunction

Function Portion(TLM:MQ02BQuest akRiver, int aiWhich)
	{A real item, or the plain statement that there is none.}
	If !akRiver.HasMeal()
		ShowBox(NoteNoMeal)
		Return
	EndIf
	akRiver.GivePortion(aiWhich)
EndFunction

; ============================================================ Mose Rafferty

Function TalkRafferty(TLM:MQ02BQuest akRiver)
	If !akRiver.RaffertyCanSpeak()
		Return
	EndIf
	If akRiver.GetStageDone(43) && !burnedSaid
		If Said(SayRaffertyBurned)
			burnedSaid = true
		EndIf
	ElseIf akRiver.GetStageDone(30) && akRiver.Unsettled()
		AtChain(akRiver)
	ElseIf akRiver.GetStageDone(20) && !akRiver.GetStageDone(30) && akRiver.Unsettled()
		int pick = ShowBox(SayRaffertySkiff)
		If pick == 1
			TakeSkiff(akRiver)
		ElseIf pick == 2
			ShowBox(SayRaffertyConfess)
		EndIf
	Else
		ShowBox(SayRaffertyDefault)
	EndIf
EndFunction

Function TakeSkiff(TLM:MQ02BQuest akRiver)
	{The skiff to the Queen's off side: a move of the player, and of Rafferty if
	he lives to row. Boarding is crossing the box there, not this.}
	Actor player = Game.GetPlayer()
	ObjectReference side = Piece(Alias_OffSideArrival)
	If !player || player.IsDead() || !side
		Return
	EndIf
	ShowBox(NoteSkiffScene)
	BringRafferty(akRiver, side)
	player.MoveTo(side)
EndFunction

Function BringRafferty(TLM:MQ02BQuest akRiver, ObjectReference akWhere)
	{Rafferty, alive and present, is where his skiff is.}
	If !akWhere || !akRiver.RaffertyIsThere()
		Return
	EndIf
	Actor rafferty = Alias_Rafferty.GetActorReference()
	If rafferty && !rafferty.IsInCombat()
		rafferty.MoveTo(akWhere, 64.0, 64.0, 0.0)
	EndIf
EndFunction

Function Boarded(TLM:MQ02BQuest akRiver, int aiApproach)
	bool first = !akRiver.GetStageDone(30)
	If akRiver.Board(aiApproach) && first
		; He brings the skiff round to the barge: that is where the chain is.
		BringRafferty(akRiver, Piece(Alias_OffSideArrival))
	EndIf
EndFunction

; ============================================================== Lyle Hatcher

Function AtTable(TLM:MQ02BQuest akRiver)
	If !akRiver.GetStageDone(30)
		Boarded(akRiver, BOARD_DECK)
	EndIf
	int fate = akRiver.HatcherState()
	If fate == RV_H_CUSTODY
		ShowBox(NoteHatcherCustody)
		Return
	EndIf
	If !akRiver.HatcherAtTable()
		ShowBox(NoteTableEmpty)
		Return
	EndIf
	If akRiver.Unsettled()
		If akRiver.SitDown()
			TableTalk(akRiver)
		EndIf
	ElseIf akRiver.HatcherToJudge()
		JudgeAtTable(akRiver)
	Else
		ShowBox(SayHatcherDefault)
	EndIf
EndFunction

Function TableTalk(TLM:MQ02BQuest akRiver)
	{His offer, and back to it after his admission as the writing has it. Never more than a few rounds.}
	int rounds = 0
	While rounds < TABLE_ROUNDS
		rounds += 1
		bool share = akRiver.IsShareOffered()
		int pick = -1
		If share
			pick = ShowBox(SayHatcherTable)
		Else
			; No share to be had: no button offers one. The places of the others are put back.
			pick = ShowBox(SayHatcherTableNoShare)
			If pick >= 1
				pick += 1
			EndIf
		EndIf
		If !akRiver.HatcherAtTable() || !akRiver.Unsettled()
			Return
		EndIf
		If pick == 0
			DealCards(akRiver)
			Return
		ElseIf pick == 1
			BuyShare(akRiver)
			Return
		ElseIf pick == 2
			If !Said(SayHatcherPaidA)
				Return
			EndIf
			If ShowBox(SayHatcherPaidB) != 0
				Return
			EndIf
			; Heard to its end.
			akRiver.LearnHire(RV_HIRE_ADMISSION)
			If !akRiver.HatcherAtTable() || !akRiver.Unsettled()
				Return
			EndIf
		Else
			Return
		EndIf
	EndWhile
EndFunction

Function DealCards(TLM:MQ02BQuest akRiver)
	int hand = akRiver.PlayCards()
	If hand == RV_CARD_WON
		Refresh()
		JudgeAtTable(akRiver)
	ElseIf hand == RV_CARD_LOST
		If !akRiver.HatcherAtTable()
			Return
		EndIf
		If akRiver.IsShareOffered()
			If ShowBox(SayHatcherWon) == 0
				If akRiver.HatcherAtTable() && akRiver.Unsettled()
					BuyShare(akRiver)
				EndIf
			EndIf
		Else
			ShowBox(SayHatcherWonNoShare)
		EndIf
	EndIf
EndFunction

Function BuyShare(TLM:MQ02BQuest akRiver)
	If ShowBox(SayHatcherShare) != 0
		Return
	EndIf
	If !akRiver.HatcherAtTable() || !akRiver.Unsettled()
		Return
	EndIf
	If akRiver.TakeShare()
		Refresh()
	Else
		ShowBox(NoteShareFailed)
	EndIf
EndFunction

Function JudgeAtTable(TLM:MQ02BQuest akRiver)
	{Beaten, he asks what is to become of him. Only what can be done is offered:
	nobody dead or absent is handed a prisoner, and with Opal not there his
	question about her is not put.}
	If !akRiver.HatcherAtTable() || !akRiver.HatcherToJudge()
		Return
	EndIf
	bool opal = akRiver.OpalCanSpeak()
	bool sheriff = akRiver.SheriffCanReceive()
	int verdict = 0
	If opal && sheriff
		int pick = ShowBox(SayHatcherLost)
		If pick == 0
			verdict = 60
		ElseIf pick == 1
			verdict = 61
		ElseIf pick == 2
			verdict = 1
		EndIf
	ElseIf opal
		int pick = ShowBox(SayHatcherLostNoSheriff)
		If pick == 0
			verdict = 60
		ElseIf pick == 1
			verdict = 1
		EndIf
	ElseIf sheriff
		int pick = ShowBox(SayHatcherLostNoOpal)
		If pick == 0
			verdict = 61
		ElseIf pick == 1
			verdict = 1
		EndIf
	Else
		If ShowBox(SayHatcherLostAlone) == 0
			verdict = 1
		EndIf
	EndIf
	If verdict != 0
		Judge(akRiver, verdict)
	EndIf
EndFunction

bool Function Judge(TLM:MQ02BQuest akRiver, int aiVerdict)
	{60 the steeple, 61 Pritchard, 1 his boat. Whoever it needs is asked for again by the road itself.}
	bool done = false
	If aiVerdict == 60
		done = akRiver.Hang()
	ElseIf aiVerdict == 61
		done = akRiver.Custody()
	ElseIf aiVerdict == 1
		done = akRiver.Release()
	EndIf
	If !done
		ShowBox(NoteJudgmentFailed)
	EndIf
	Return done
EndFunction

Function OpenStrongbox(TLM:MQ02BQuest akRiver)
	{The letter of hire, read through. Open to anybody aboard, whoever lives.}
	If !akRiver.GetStageDone(30)
		Boarded(akRiver, BOARD_DECK)
	EndIf
	If !ReadPages(LetterPage1, LetterPage2, LetterPage3, LetterPage4)
		Return
	EndIf
	If akRiver.LearnHire(RV_HIRE_LETTER)
		akRiver.GiveLetter()
	EndIf
EndFunction

; ======================================================= chain, pilot, fire

Function AtChain(TLM:MQ02BQuest akRiver)
	If !akRiver.GetStageDone(30)
		Boarded(akRiver, BOARD_DECK)
	EndIf
	If akRiver.IsEscapePending()
		ShowBox(NoteChainCut)
		Return
	EndIf
	If !akRiver.Unsettled()
		ShowBox(NoteChainNothing)
		Return
	EndIf
	; Who and what is aboard: Rafferty says it if he can; if he cannot, this build does, and says that it is.
	int pick = -1
	If akRiver.RaffertyCanSpeak()
		pick = ShowBox(SayRaffertyChain)
	Else
		pick = ShowBox(AskChain)
	EndIf
	If pick == 0
		If akRiver.CutChain()
			ShowBox(NoteChainCut)
		EndIf
	ElseIf pick == 1
		If akRiver.WarnOfFire()
			ShowBox(NoteFireWarned)
		EndIf
	EndIf
EndFunction

Function AtPilot(TLM:MQ02BQuest akRiver)
	If !akRiver.GetStageDone(30)
		Boarded(akRiver, BOARD_DECK)
	EndIf
	Actor player = Game.GetPlayer()
	ObjectReference chute = Piece(Alias_ChuteStart)
	If !chute
		Return
	EndIf
	int kind = akRiver.BeginReturn()
	If kind == RV_RETURN_ESCAPE
		ShowBox(NoteChuteScene)
	ElseIf kind == RV_RETURN_TOW
		ShowBox(NoteTowScene)
	Else
		ShowBox(NotePilotNothing)
		Return
	EndIf
	; The run itself is the walk from here to the return dock. Nothing is settled by this move.
	player.MoveTo(chute)
EndFunction

Function ReachedDock(TLM:MQ02BQuest akRiver)
	int arrived = akRiver.CompleteReturn()
	If arrived != RV_RETURN_ESCAPE && arrived != RV_RETURN_TOW
		Return
	EndIf
	Refresh()
	ObjectReference landing = Piece(Alias_Arrival)
	If arrived == RV_RETURN_ESCAPE
		BringRafferty(akRiver, landing)
	EndIf
	If talking
		Return
	EndIf
	talking = true
	If arrived == RV_RETURN_TOW
		ShowBox(NoteHomeWhole)
	ElseIf akRiver.Recovered() == RV_UNITS_PILOTED
		ShowBox(NoteHomePiloted)
		If !ranSaid && akRiver.RaffertyCanSpeak()
			If Said(SayRaffertyRan)
				ranSaid = true
			EndIf
		EndIf
	Else
		ShowBox(NoteHomeAlone)
	EndIf
	talking = false
EndFunction

Function AtFire(TLM:MQ02BQuest akRiver)
	If !akRiver.GetStageDone(30)
		Boarded(akRiver, BOARD_DECK)
	EndIf
	If akRiver.IsBurning()
		; Ordered before, and its outcome never recorded: staged again, not ordered again.
		StageFire(akRiver)
		Return
	EndIf
	If !akRiver.Unsettled()
		ShowBox(NoteChainNothing)
		Return
	EndIf
	If !akRiver.IsFireWarned()
		ShowBox(NoteFireNotWarned)
		Return
	EndIf
	If ShowBox(AskFire) != 0
		Return
	EndIf
	If akRiver.OrderFire()
		StageFire(akRiver)
	EndIf
EndFunction

Function StageFire(TLM:MQ02BQuest akRiver)
	{The fire, as this greybox can show it: the burned marker on, the lashed cargo
	and the deck's working pieces off, the people who were aboard not there. It
	is recorded only if the marker is seen on and the cargo seen gone.}
	Refresh()
	SwitchOff(Alias_CargoLashed)
	ObjectReference marker = Piece(Alias_Burnt)
	ObjectReference lashed = Piece(Alias_CargoLashed)
	int tries = 0
	While tries < 20 && marker && marker.IsDisabled()
		Utility.Wait(0.1)
		tries += 1
	EndWhile
	If !marker || marker.IsDisabled() || (lashed && !lashed.IsDisabled())
		Debug.Trace("TLM_GW: the fire was ordered and is not seen (the burned marker is off or the lashed cargo is still there); nothing is recorded. Use the firebox again.", 2)
		ShowBox(NoteFireFailed)
		Return
	EndIf
	If !akRiver.FireDone()
		Return
	EndIf
	Refresh()
	ShowBox(NoteFireScene)
	Actor player = Game.GetPlayer()
	ObjectReference landing = Piece(Alias_Arrival)
	If landing
		BringRafferty(akRiver, landing)
		If player && !player.IsDead()
			player.MoveTo(landing)
		EndIf
	EndIf
	If !burnedSaid && akRiver.RaffertyCanSpeak()
		If Said(SayRaffertyBurned)
			burnedSaid = true
		EndIf
	EndIf
EndFunction

; ============================================================== Tomas Belden

Function TalkBelden(TLM:MQ02BQuest akRiver)
	If !akRiver.BeldenCanSpeak()
		Return
	EndIf
	If !akRiver.GetStageDone(43) && !akRiver.GetStageDone(44)
		Return
	EndIf
	If Said(SayBeldenRelief)
		Portion(akRiver, RV_GRANT_RELIEF)
	EndIf
EndFunction

; ==================================================================== labels

Function LookAtCargo(TLM:MQ02BQuest akRiver)
	int lashing = akRiver.Cargo()
	If lashing == RV_CARGO_HOME_WHOLE
		ShowBox(LabelCargoWhole)
	ElseIf lashing == RV_CARGO_HOME_REDUCED
		If akRiver.Recovered() == RV_UNITS_PILOTED
			ShowBox(LabelCargoPiloted)
		Else
			ShowBox(LabelCargoAlone)
		EndIf
	ElseIf lashing == RV_CARGO_LASHED || lashing == RV_CARGO_YIELDED
		ShowBox(LabelCargoLashed)
	EndIf
EndFunction

; ============================================================ the river report

bool Function OfferReport(Actor akSheriff)
	{Called by TLM:Act1Walk, inside its own claim on Pritchard's conversation,
	when he is activated after the chapter. True if the report took this
	activation. False, with nothing changed, if there is nothing to report, it
	was reported before, or the player chose to leave it for later.}
	TLM:MQ02BQuest river = Road()
	If !river || !akSheriff || akSheriff.IsDead() || akSheriff.IsInCombat()
		Return false
	EndIf
	If !river.GetStageDone(100) || river.IsReported()
		Return false
	EndIf
	int pick = -1
	bool known = river.KnowsHire()
	If known
		pick = ShowBox(SayReportKnown)
	Else
		pick = ShowBox(SayReportUnknown)
	EndIf
	If pick != 0
		Return false
	EndIf
	Actor player = Game.GetPlayer()
	If akSheriff.IsDead() || akSheriff.IsInCombat() || !player || player.IsDead()
		Return false
	EndIf
	If !river.GiveReport()
		Return false
	EndIf
	; What is reported is what the road holds, said by this build and not put in his mouth.
	int lashing = river.Cargo()
	If lashing == RV_CARGO_HOME_WHOLE
		ShowBox(ReportWhole)
	ElseIf lashing == RV_CARGO_HOME_REDUCED
		ShowBox(ReportReduced)
	ElseIf lashing == RV_CARGO_DESTROYED
		ShowBox(ReportDestroyed)
	Else
		ShowBox(ReportSold)
	EndIf
	If known
		ShowBox(ReportEndKnown)
	Else
		ShowBox(ReportEndUnknown)
	EndIf
	Return true
EndFunction
