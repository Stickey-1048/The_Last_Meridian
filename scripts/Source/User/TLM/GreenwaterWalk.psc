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
	Quest Property TLM_Relief Auto Const
	Quest Property TLM_FourFlags Auto Const
	Quest Property TLM_MQ02B Auto Const Mandatory
	Quest Property TLM_MQ01 Auto Const Mandatory
	{Read only.}
	GlobalVariable Property TLM_G_MQ01_Done Auto Const Mandatory
	{Read only.}
EndGroup

Group Placed
	ReferenceAlias Property Alias_ReliefStores Auto Const
	ReferenceAlias Property Alias_ReliefSupply Auto Const
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
	Message Property ArrivalBrief Auto Const
	Message Property Goal Auto Const
	Message Property Stakes Auto Const
	Message Property ConfirmShare Auto Const
	Message Property NoteSharePaid Auto Const
	Message Property LabelShareHeld Auto Const
	Message Property LabelLandingLayout Auto Const
	Message Property CardStakes Auto Const
	Message Property ConfirmHang Auto Const
	Message Property ConfirmCustody Auto Const
	Message Property ConfirmRelease Auto Const
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
	Message Property NoteFireNoMarker Auto Const
	Message Property NoteFireStuck Auto Const
	Message Property NoteCargoFailed Auto Const
	Message Property NoteCargoStuck Auto Const
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
int GW_RELIEF_STORES = 26 Const
int GW_RELIEF_SUPPLY = 27 Const

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
int RV_RETURN_NONE = 0 Const
int RV_RETURN_ESCAPE = 1 Const
int RV_RETURN_TOW = 2 Const
int RV_HIRE_LETTER = 1 Const
int RV_HIRE_ADMISSION = 2 Const
int RV_GRANT_BOWL = 1 Const
int RV_GRANT_CUP = 2 Const
int RV_GRANT_RELIEF = 3 Const

float ARRIVE_REACH = 1500.0 Const
; How long a switched piece is looked for: twenty looks, a tenth of a second apart.
int SEEN_POLLS = 20 Const

; What OfferReport tells TLM:Act1Walk. The same numbers there; a test compares them.
int GW_REPORT_NONE = 0 Const
int GW_REPORT_GIVEN = 1 Const
int GW_REPORT_LATER = 2 Const
int GW_REPORT_CLOSED = 3 Const
int TABLE_ROUNDS = 3 Const

; ------------------------------------------------------------------- state

; The travel point is on. The zones are set up. A box is open: claimed with
; no call into the game between the test and the claim.
bool doorOpen = false
bool zonesUp = false
bool talking = false
bool ranSaid = false
bool burnedSaid = false
bool arrivalBriefRead = false
bool reliefActivation = false
int useGeneration = 0

; ================================================================== set-up

TLM:MQ02BQuest Function Road()
	Return TLM_MQ02B as TLM:MQ02BQuest
EndFunction

bool Function CanVisitFairBelden()
	Return !talking && Road().BeldenVisitSafe()
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
	If BindRelief()
		SwitchOn(Alias_ReliefSupply)
	EndIf
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
	If BindRelief()
		SwitchOn(Alias_ReliefStores)
	EndIf
	Debug.Trace("TLM_GW: Greenwater is set up; aliases of TLM_MQ02B left empty: " + unfilled)
	Return true
EndFunction

bool Function BindRelief()
	TLM:GreenwaterRelief ledger = TLM_Relief as TLM:GreenwaterRelief
	If !ledger
		Return false
	EndIf
	Return ledger.OpenControls(Self, Piece(Alias_ReliefStores), Piece(Alias_ReliefSupply))
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
	; A temporary relief startup refusal must not permanently hide its controls.
	If BindRelief()
		SwitchOn(Alias_ReliefStores)
		SwitchOn(Alias_ReliefSupply)
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
	If course == RV_FIRE
		; Recorded, and only then: the deck's working pieces are gone. The strongbox is not: what was in
		; it can still be read. A fire that was ordered and is not yet recorded leaves every piece where
		; it is, the firebox above all: using it again is how the fire is shown.
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

Function Notice(Message akLine)
	{A notice from a trigger box, which is not inside a use: shown only if no
	box is open, and claimed while it is.}
	If talking
		Return
	EndIf
	talking = true
	ShowBox(akLine)
	talking = false
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
	If aiWho == GW_BELDEN && TLM_FourFlags && (TLM_FourFlags as TLM:FourFlagsWalk).IsVisiting(Alias_Belden.GetActorReference())
		Return
	EndIf
	; Nothing between the test and the claim calls into the game, so two
	; activations cannot both pass.
	If talking
		Return
	EndIf
	talking = true
	int activationGeneration = useGeneration
	TLM:MQ02BQuest river = Road()
	If !river
		Debug.Trace("TLM_GW: TLM_MQ02B does not carry TLM:MQ02BQuest; nothing can be used", 2)
	ElseIf aiWho == GW_TRAVEL
		Travel(river)
	ElseIf aiWho == GW_RELIEF_STORES || aiWho == GW_RELIEF_SUPPLY
		reliefActivation = true
		If BindRelief()
			TLM:GreenwaterRelief ledger = TLM_Relief as TLM:GreenwaterRelief
			If aiWho == GW_RELIEF_STORES
				ledger.Use(1, Piece(Alias_ReliefStores))
			Else
				ledger.Use(2, Piece(Alias_ReliefSupply))
			EndIf
		EndIf
	ElseIf !zonesUp
		; A piece of Greenwater that the player was never sent to: nothing.
	ElseIf aiWho == GW_EXIT
		; The way back is never shut, whatever has or has not been stepped on.
		Leave(river)
	ElseIf !river.RoadOpen()
		; Before the landing was stepped onto, or with the player dead: the label and nothing else.
		If aiWho == GW_LABEL_LANDING
			LandingOverview(river)
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
		LandingOverview(river)
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
	If activationGeneration == useGeneration
		talking = false
		reliefActivation = false
	EndIf
EndFunction

Function ReliefLoaded()
	{Only a relief activation may release its interrupted outer claim.
	A resumed older activation cannot release a newer conversation's claim.}
	If reliefActivation
		useGeneration += 1
		reliefActivation = false
		talking = false
	EndIf
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
		river.HatcherDied(Alias_Hatcher.GetActorReference())
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
	{Somebody alive, present and not already fighting is set on the target. Not
	somebody already in a fight: this is called from every one of their combat
	events, and a fight started again from the event that the last start
	raised would never end.}
	Actor who = akAlias.GetActorReference()
	If who && !who.IsDead() && !who.IsDisabled() && !who.IsInCombat()
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
	If !player || player.IsDead() || player.GetParentCell() != arrival.GetParentCell() || player.GetDistance(arrival) > 256.0
		Return
	EndIf
	If !arrivalBriefRead && akRiver.Outcome() == RV_NONE && !akRiver.GetStageDone(20) && akRiver.OpalCanSpeak()
		If ShowBox(ArrivalBrief) != 0
			Return
		EndIf
		If player.IsDead() || player.GetParentCell() != arrival.GetParentCell() || player.GetDistance(arrival) > 256.0 || akRiver.Outcome() != RV_NONE || !akRiver.OpalCanSpeak()
			Return
		EndIf
		arrivalBriefRead = true
	EndIf
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
	Actor opal = Alias_Opal.GetActorReference()
	If !LocalSpeaker(opal, Alias_Opal)
		Return
	EndIf
	int pick = ShowBox(SayOpalFirst)
	If !akRiver.RoadOpen() || !akRiver.OpalCanSpeak() || !LocalSpeaker(opal, Alias_Opal)
		Return
	EndIf
	If pick == 0
		; Heard out: the stage is hers to have said, and the player's to have answered.
		If Said(SayOpalWants)
			If LocalSpeaker(opal, Alias_Opal) && akRiver.HearOpal() && akRiver.RoadOpen() && akRiver.OpalCanSpeak()
				If ShowBox(Goal) != 0
					Return
				EndIf
				If akRiver.RoadOpen() && akRiver.OpalCanSpeak() && LocalSpeaker(opal, Alias_Opal) && akRiver.Outcome() == RV_NONE
					ShowBox(Stakes)
				EndIf
			EndIf
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
	Actor opal = Alias_Opal.GetActorReference()
	Actor hatcher = Alias_Hatcher.GetActorReference()
	Actor recipient = akRiver.Person(akRiver.Alias_MercySheriff)
	ObjectReference ring = Piece(akRiver.Alias_Steeple)
	int mark = akRiver.Stamp()
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
	; Her question is answered to her: alive, present and in no fight after it as before it.
	If !akRiver.RoadOpen() || !akRiver.OpalCanSpeak()
		Return
	EndIf
	If !LocalSpeaker(opal, Alias_Opal)
		Return
	EndIf
	If pick == 0
		Judge(akRiver, 60, hatcher, opal, ring, opal, Alias_Opal, mark)
	ElseIf pick == 1
		If Judge(akRiver, 61, hatcher, recipient, None, opal, Alias_Opal, mark)
			Deny(akRiver, opal)
		EndIf
	ElseIf pick == 2
		If Judge(akRiver, 1, hatcher, None, None, opal, Alias_Opal, mark)
			Deny(akRiver, opal)
		EndIf
	EndIf
EndFunction

Function Deny(TLM:MQ02BQuest akRiver, Actor akOpal = None)
	If !akOpal
		akOpal = Alias_Opal.GetActorReference()
	EndIf
	If !LocalSpeaker(akOpal, Alias_Opal) || akRiver.Person(akRiver.Alias_Opal) != akOpal || !akRiver.OpalCanSpeak() || akRiver.IsDeniedSaid()
		Return
	EndIf
	If Said(SayOpalDenied)
		If LocalSpeaker(akOpal, Alias_Opal) && akRiver.Person(akRiver.Alias_Opal) == akOpal && akRiver.OpalCanSpeak()
			akRiver.MarkDenied()
		EndIf
	EndIf
EndFunction

Function AfterShare(TLM:MQ02BQuest akRiver)
	{The share is paid. Whether she is lied to is the player's to choose here, and only here.}
	Actor opal = Alias_Opal.GetActorReference()
	If !akRiver.RoadOpen() || !akRiver.IsSharePaid() || !LocalSpeaker(opal, Alias_Opal)
		Return
	EndIf
	If akRiver.IsLieHeard()
		ShowBox(SayOpalDefault)
		Return
	EndIf
	If !akRiver.IsLieTold()
		If ShowBox(AskLie) != 0
			Return
		EndIf
		If !akRiver.RoadOpen() || !LocalSpeaker(opal, Alias_Opal)
			Return
		EndIf
		If !akRiver.TellLie()
			Return
		EndIf
	EndIf
	; Told: that much is earned and kept. Her answer is hers to give, alive, present and in no fight,
	; now or when she is next spoken to; only then what the journal says of it, and her cup.
	If !akRiver.OpalCanSpeak() || !LocalSpeaker(opal, Alias_Opal)
		Return
	EndIf
	If !Said(SayOpalAfterShare)
		Return
	EndIf
	If LocalSpeaker(opal, Alias_Opal) && akRiver.LieWasHeard()
		Portion(akRiver, RV_GRANT_CUP)
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
		If !akRiver.RoadOpen() || !akRiver.RaffertyCanSpeak()
			Return
		EndIf
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
	he lives to row. Boarding is crossing the box there, not this. Nobody is
	moved unless the notice was answered with its one button and, after it,
	the player is alive on a road that stands as it stood.}
	If !akRiver.RoadOpen() || !Piece(Alias_OffSideArrival)
		Return
	EndIf
	int stamp = akRiver.Stamp()
	If ShowBox(NoteSkiffScene) != 0
		Return
	EndIf
	Actor player = Game.GetPlayer()
	ObjectReference side = Piece(Alias_OffSideArrival)
	If !player || !side || !akRiver.RoadOpen() || akRiver.Stamp() != stamp
		Return
	EndIf
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
	Actor hatcher = Alias_Hatcher.GetActorReference()
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
		If !akRiver.RoadOpen() || !akRiver.HatcherAtTable() || !akRiver.Unsettled()
			Return
		EndIf
		If !LocalSpeaker(hatcher, Alias_Hatcher)
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
			; His admission is his to finish: alive, present, in no fight and at his table between its two halves.
			If !akRiver.RoadOpen() || !akRiver.HatcherAtTable() || !akRiver.Unsettled()
				Return
			EndIf
			If ShowBox(SayHatcherPaidB) != 0
				Return
			EndIf
			; Heard to its end, from a man still there to have said it. The road asks for him again itself.
			If !akRiver.LearnHire(RV_HIRE_ADMISSION)
				Return
			EndIf
			If !akRiver.RoadOpen() || !akRiver.HatcherAtTable() || !akRiver.Unsettled()
				Return
			EndIf
		Else
			Return
		EndIf
	EndWhile
EndFunction

Function DealCards(TLM:MQ02BQuest akRiver)
	Actor hatcher = Alias_Hatcher.GetActorReference()
	If ShowBox(CardStakes) != 0
		Return
	EndIf
	If !akRiver.RoadOpen() || !akRiver.HatcherAtTable() || !LocalSpeaker(hatcher, Alias_Hatcher) || !akRiver.Unsettled()
		Return
	EndIf
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
				If akRiver.RoadOpen() && akRiver.HatcherAtTable() && akRiver.Unsettled()
					BuyShare(akRiver)
				EndIf
			EndIf
		Else
			ShowBox(SayHatcherWonNoShare)
		EndIf
	EndIf
EndFunction

Function BuyShare(TLM:MQ02BQuest akRiver)
	Actor hatcher = Alias_Hatcher.GetActorReference()
	int roadStamp = akRiver.Stamp()
	If !ShareContext(akRiver, hatcher, roadStamp)
		Return
	EndIf
	If ShowBox(SayHatcherShare) != 0
		Return
	EndIf
	If !ShareContext(akRiver, hatcher, roadStamp)
		Return
	EndIf
	If ShowBox(ConfirmShare) != 0
		Return
	EndIf
	If !ShareContext(akRiver, hatcher, roadStamp)
		Return
	EndIf
	If akRiver.TakeShare()
		Refresh()
		If akRiver.RoadOpen() && !akRiver.IsLieTold()
			ShowBox(NoteSharePaid)
		EndIf
	Else
		ShowBox(NoteShareFailed)
	EndIf
EndFunction

bool Function LocalSpeaker(Actor akSpeaker, ReferenceAlias akAlias)
	{The same living participant remains close enough for this activation.}
	Actor player = Game.GetPlayer()
	If !player || player.IsDead() || !akSpeaker || !akAlias || akAlias.GetActorReference() != akSpeaker
		Return false
	EndIf
	Return !akSpeaker.IsDead() && !akSpeaker.IsDisabled() && !akSpeaker.IsInCombat() && player.GetParentCell() == akSpeaker.GetParentCell() && player.GetDistance(akSpeaker) <= 2048.0
EndFunction

bool Function ShareContext(TLM:MQ02BQuest akRiver, Actor akHatcher, int aiStamp)
	Return akRiver.RoadOpen() && akRiver.Stamp() == aiStamp && LocalSpeaker(akHatcher, Alias_Hatcher) && akRiver.HatcherAtTable() && akRiver.Unsettled() && akRiver.IsShareOffered()
EndFunction

Function JudgeAtTable(TLM:MQ02BQuest akRiver)
	{Beaten, he asks what is to become of him. Only what can be done is offered:
	nobody dead or absent is handed a prisoner, and with Opal not there his
	question about her is not put.}
	Actor hatcher = Alias_Hatcher.GetActorReference()
	Actor opalRecipient = Alias_Opal.GetActorReference()
	Actor sheriffRecipient = akRiver.Person(akRiver.Alias_MercySheriff)
	ObjectReference ring = Piece(akRiver.Alias_Steeple)
	int mark = akRiver.Stamp()
	If !akRiver.HatcherAtTable() || !akRiver.HatcherCanBeJudged()
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
	If verdict == 0
		Return
	EndIf
	; His question is answered to him: alive, present, in no fight and unjudged after it as before it.
	; If he is not, nothing is carried out and nothing more is said. The road asks again for whoever
	; the verdict itself needs.
	If !akRiver.RoadOpen() || !akRiver.HatcherAtTable() || !akRiver.HatcherCanBeJudged()
		Return
	EndIf
	If !LocalSpeaker(hatcher, Alias_Hatcher)
		Return
	EndIf
	Actor recipient = None
	If verdict == 60
		recipient = opalRecipient
	ElseIf verdict == 61
		recipient = sheriffRecipient
	EndIf
	Judge(akRiver, verdict, hatcher, recipient, ring, hatcher, Alias_Hatcher, mark)
EndFunction

bool Function Judge(TLM:MQ02BQuest akRiver, int aiVerdict, Actor akHatcher, Actor akRecipient, ObjectReference akRing, Actor akSpeaker, ReferenceAlias akSpeakerAlias, int aiStamp)
	{The original choice's participants survive the confirmation and actual effect.}
	If !LocalSpeaker(akSpeaker, akSpeakerAlias) || !akRiver.JudgmentContext(aiVerdict, akHatcher, akRecipient, akRing, akSpeaker, akSpeakerAlias, aiStamp)
		Return false
	EndIf
	int confirmed = -1
	If aiVerdict == 60 && akRiver.OpalCanSpeak()
		confirmed = ShowBox(ConfirmHang)
	ElseIf aiVerdict == 61 && akRiver.SheriffCanReceive()
		confirmed = ShowBox(ConfirmCustody)
	ElseIf aiVerdict == 1
		confirmed = ShowBox(ConfirmRelease)
	EndIf
	If confirmed != 0 || !LocalSpeaker(akSpeaker, akSpeakerAlias) || !akRiver.JudgmentContext(aiVerdict, akHatcher, akRecipient, akRing, akSpeaker, akSpeakerAlias, aiStamp)
		Return false
	EndIf
	bool done = false
	If aiVerdict == 60
		done = akRiver.Hang(akHatcher, akRecipient, akRing, akSpeaker, akSpeakerAlias, aiStamp)
	ElseIf aiVerdict == 61
		done = akRiver.Custody(akHatcher, akRecipient, akSpeaker, akSpeakerAlias, aiStamp)
	ElseIf aiVerdict == 1
		done = akRiver.Release(akHatcher, akSpeaker, akSpeakerAlias, aiStamp)
	EndIf
	If !done && LocalSpeaker(akSpeaker, akSpeakerAlias) && akRiver.JudgmentContext(aiVerdict, akHatcher, akRecipient, akRing, akSpeaker, akSpeakerAlias, aiStamp)
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
	bool his = akRiver.RaffertyCanSpeak()
	If his
		pick = ShowBox(SayRaffertyChain)
	Else
		pick = ShowBox(AskChain)
	EndIf
	; If it was Rafferty who said it, it is answered to Rafferty. The chain can be used again without him.
	If !akRiver.RoadOpen() || (his && !akRiver.RaffertyCanSpeak())
		Return
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
	{The barge's pilot lever. What it can begin is read first and written only
	after its notice was answered with its one button and, after that, the
	player is alive on a road that stands as it stood. A return already
	pending stays pending whatever the notice comes back with.}
	If !akRiver.GetStageDone(30)
		Boarded(akRiver, BOARD_DECK)
	EndIf
	int kind = akRiver.ReturnOffered()
	If kind != RV_RETURN_ESCAPE && kind != RV_RETURN_TOW
		ShowBox(NotePilotNothing)
		Return
	EndIf
	If !Piece(Alias_ChuteStart)
		Debug.Trace("TLM_GW: the head of the Chute is not placed; the pilot lever begins nothing", 2)
		Return
	EndIf
	int stamp = akRiver.Stamp()
	int pick = -1
	If kind == RV_RETURN_ESCAPE
		pick = ShowBox(NoteChuteScene)
	Else
		pick = ShowBox(NoteTowScene)
	EndIf
	If pick != 0
		Return
	EndIf
	Actor player = Game.GetPlayer()
	ObjectReference chute = Piece(Alias_ChuteStart)
	If !player || !chute || !akRiver.RoadOpen() || akRiver.Stamp() != stamp
		Return
	EndIf
	If akRiver.BeginReturn(kind) != kind
		Return
	EndIf
	; The run itself is the walk from here to the return dock. Nothing is settled by this move.
	player.MoveTo(chute)
EndFunction

bool Function Seen(ObjectReference akOn, ObjectReference akOff)
	{akOn is switched on and akOff (if there is one) is not. Looked for, for two seconds at the most.}
	If !akOn
		Return false
	EndIf
	int tries = 0
	While tries < SEEN_POLLS && (akOn.IsDisabled() || (akOff && !akOff.IsDisabled()))
		Utility.Wait(0.1)
		tries += 1
	EndWhile
	If akOn.IsDisabled()
		Return false
	EndIf
	If akOff
		Return akOff.IsDisabled()
	EndIf
	Return true
EndFunction

Function ReachedDock(TLM:MQ02BQuest akRiver)
	{The player walked onto the return dock. The cargo is put at the landing
	and LOOKED AT before anything is recorded: the road writes nothing unless
	the home piece is on and the lashed one off. If they are not, the pieces
	are put back as the facts stand, the return stays pending, and the lever
	and this dock can be used again.}
	int kind = akRiver.ReturnArriving()
	If kind != RV_RETURN_ESCAPE && kind != RV_RETURN_TOW
		Return
	EndIf
	ReferenceAlias homeAlias = Alias_CargoReduced
	If kind == RV_RETURN_TOW
		homeAlias = Alias_CargoWhole
	EndIf
	ObjectReference home = Piece(homeAlias)
	ObjectReference lashed = Piece(Alias_CargoLashed)
	If !home
		Debug.Trace("TLM_GW: the cargo's piece at the landing is not placed; the return cannot be shown and is not recorded. It stays pending", 2)
		Notice(NoteCargoStuck)
		Return
	EndIf
	SwitchOn(homeAlias)
	SwitchOff(Alias_CargoLashed)
	int arrived = RV_RETURN_NONE
	If Seen(home, lashed)
		arrived = akRiver.CompleteReturn(kind, home, lashed)
	EndIf
	; The pieces as the facts now stand: at the landing if it was recorded, lashed again if it was not.
	Refresh()
	If arrived != kind
		If akRiver.ReturnArriving() == kind
			Debug.Trace("TLM_GW: the cargo was not seen at the landing; nothing is recorded and the return stays pending. Use the pilot lever again and walk to the return dock.", 2)
			Notice(NoteCargoFailed)
		EndIf
		; Otherwise it was brought home by another arrival at this dock, which says so itself.
		Return
	EndIf
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
	; Nothing is ordered that cannot be shown.
	If !Piece(Alias_Burnt)
		Debug.Trace("TLM_GW: the burned Queen's marker is not placed; no fire is ordered", 2)
		ShowBox(NoteFireNoMarker)
		Return
	EndIf
	int stamp = akRiver.Stamp()
	If ShowBox(AskFire) != 0
		Return
	EndIf
	If !akRiver.RoadOpen() || akRiver.Stamp() != stamp || !Piece(Alias_Burnt)
		Return
	EndIf
	If akRiver.OrderFire()
		StageFire(akRiver)
	EndIf
EndFunction

Function StageFire(TLM:MQ02BQuest akRiver)
	{The fire, as this greybox can show it: the burned marker on and the lashed
	cargo off, and both LOOKED AT; the road records it only if it sees them so
	itself, and only then is the deck cleared. If they are not seen, the
	pieces are put back as the facts stand and the firebox, which stays on
	while a fire is ordered and not recorded, is how it is tried again.}
	ObjectReference marker = Piece(Alias_Burnt)
	ObjectReference lashed = Piece(Alias_CargoLashed)
	If !marker
		Debug.Trace("TLM_GW: the fire was ordered and its marker is not placed: it cannot be shown or recorded, and no other course is open. Report this line.", 2)
		ShowBox(NoteFireStuck)
		Return
	EndIf
	SwitchOn(Alias_Burnt)
	SwitchOff(Alias_CargoLashed)
	bool done = false
	If Seen(marker, lashed)
		done = akRiver.FireDone(marker, lashed)
	EndIf
	If !done
		If akRiver.IsBurning()
			; Not shown. Nothing burned: the marker off again, the cargo as the facts have it.
			SwitchOff(Alias_Burnt)
			Refresh()
			SwitchOn(Alias_FireControl)
			ObjectReference control = Piece(Alias_FireControl)
			If control && Seen(control, None)
				Debug.Trace("TLM_GW: the fire was ordered and is not seen (the burned marker is off or the lashed cargo is still there); nothing is recorded. Use the firebox again.", 2)
				ShowBox(NoteFireFailed)
			Else
				Debug.Trace("TLM_GW: the fire was ordered and is not seen, and the firebox is missing or cannot be switched on: it cannot be tried again here, and no other course is open. Report this line.", 2)
				ShowBox(NoteFireStuck)
			EndIf
		EndIf
		Return
	EndIf
	Refresh()
	; The notice, and only on its one button the move to the landing.
	If ShowBox(NoteFireScene) != 0
		Return
	EndIf
	Actor player = Game.GetPlayer()
	ObjectReference landing = Piece(Alias_Arrival)
	If !player || !landing || !akRiver.RoadOpen()
		Return
	EndIf
	BringRafferty(akRiver, landing)
	player.MoveTo(landing)
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

Function LandingOverview(TLM:MQ02BQuest akRiver)
	If !Game.GetPlayer() || Game.GetPlayer().IsDead()
		Return
	EndIf
	If akRiver.Cargo() == RV_CARGO_DESTROYED
		ShowBox(LabelBurnt)
	ElseIf akRiver.Outcome() == RV_SHARE && akRiver.IsSharePaid()
		ShowBox(LabelShareHeld)
	ElseIf akRiver.Cargo() == RV_CARGO_HOME_WHOLE || akRiver.Cargo() == RV_CARGO_HOME_REDUCED
		LookAtCargo(akRiver)
	ElseIf akRiver.OpalCanSpeak() && akRiver.RaffertyCanSpeak() && akRiver.Outcome() == RV_NONE
		ShowBox(LabelLanding)
	Else
		ShowBox(LabelLandingLayout)
	EndIf
EndFunction

Function LookAtCargo(TLM:MQ02BQuest akRiver)
	int lashing = akRiver.Cargo()
	If lashing == RV_CARGO_DESTROYED
		ShowBox(LabelBurnt)
	ElseIf akRiver.Outcome() == RV_SHARE && akRiver.IsSharePaid()
		ShowBox(LabelShareHeld)
	ElseIf lashing == RV_CARGO_HOME_WHOLE
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

int Function OfferReport(Actor akSheriff)
	{Called by TLM:Act1Walk, inside its own claim on Pritchard's conversation,
	when he is activated after the chapter. What became of this activation:
	GW_REPORT_NONE    nothing was offered (nothing to report, or reported
	                  before): nothing was shown and the conversation goes on;
	GW_REPORT_GIVEN   the report was offered, chosen and given;
	GW_REPORT_LATER   it was offered and explicitly left for later, by its
	                  second button: the conversation goes on;
	GW_REPORT_CLOSED  it was offered and came back with no button a person can
	                  press, or by the time it was answered Pritchard, the
	                  player or the road was not as the offer needed. Nothing
	                  is recorded and this conversation is over: no briefing
	                  and no other line follows it.}
	TLM:MQ02BQuest river = Road()
	Actor player = Game.GetPlayer()
	If !river || !akSheriff || !player || akSheriff.IsDead() || akSheriff.IsInCombat() || player.IsDead()
		Return GW_REPORT_NONE
	EndIf
	If !river.GetStageDone(100) || river.IsReported()
		Return GW_REPORT_NONE
	EndIf
	int pick = -1
	bool known = river.KnowsHire()
	If known
		pick = ShowBox(SayReportKnown)
	Else
		pick = ShowBox(SayReportUnknown)
	EndIf
	; Shown. From here this conversation is the report's, unless it is explicitly left for later.
	If akSheriff.IsDead() || akSheriff.IsDisabled() || akSheriff.IsInCombat() || player.IsDead()
		Return GW_REPORT_CLOSED
	EndIf
	If !river.GetStageDone(100) || river.IsReported() || river.KnowsHire() != known
		Return GW_REPORT_CLOSED
	EndIf
	If pick == 1
		Return GW_REPORT_LATER
	EndIf
	If pick != 0
		Return GW_REPORT_CLOSED
	EndIf
	If !river.GiveReport()
		Return GW_REPORT_CLOSED
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
	Return GW_REPORT_GIVEN
EndFunction
