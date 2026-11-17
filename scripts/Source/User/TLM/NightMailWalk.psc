Scriptname TLM:NightMailWalk extends Quest
{The Night Mail greybox (NIGHT-MAIL-STORY-001): DEVELOPMENT ONLY.

Five labelled zones in a cell of this plugin's own (the yard, the footplate,
Sawtooth Cut, the tabernacle siding, the valley platform) and two pieces at
Mercy. This script shows the lines and the notices, works the pieces and
stages the scenes. It keeps no fact of the road: TLM:MQ02AQuest does, and
every commitment is asked of it.

A staged scene here is: a notice with its buttons; on its one button, and
only then, everything the scene needs asked for again; the road told that
it is begun; the moves and the switched pieces; a LOOK at each; and the
road told that it is finished, handing it what was looked at so that it can
look itself. What is not seen is not recorded, stays pending, and is tried
again from a control that still works. Nothing here moves a train, makes it
jump, or tests driving.

Text in square brackets on the screen is this build speaking, never a
character.

A CANDIDATE: not compiled, not built against the game's master, not run in
the game.}

Group Quests
	Quest Property TLM_MQ02A Auto Const Mandatory
	Quest Property TLM_MQ01 Auto Const Mandatory
	{Read only.}
	GlobalVariable Property TLM_G_MQ01_Done Auto Const Mandatory
	{Read only.}
EndGroup

Group Placed
	ReferenceAlias[] Property ZoneOn Auto Const
	{What is switched on when the player first travels.}
	ReferenceAlias[] Property CastFrom Auto Const
	ReferenceAlias[] Property CastInto Auto Const
	{This quest's placed references, and the aliases of TLM_MQ02A each is put into.}
	String[] Property CastNames Auto Const
	ReferenceAlias Property Alias_MercyTravel Auto Const
	ReferenceAlias Property Alias_MercyReturn Auto Const
	ReferenceAlias Property Alias_YardArrival Auto Const
	ReferenceAlias Property Alias_YardFootplate Auto Const
	ReferenceAlias Property Alias_CutArrival Auto Const
	ReferenceAlias Property Alias_PlatformArrival Auto Const
	ReferenceAlias Property Alias_BillieFootplate Auto Const
	ReferenceAlias Property Alias_BillieCut Auto Const
	ReferenceAlias Property Alias_BilliePlatform Auto Const
	ReferenceAlias Property Alias_BillieWalk Auto Const
	ReferenceAlias Property Alias_BillieYard Auto Const
	ReferenceAlias Property Alias_Retreat1 Auto Const
	ReferenceAlias Property Alias_Retreat2 Auto Const
	ReferenceAlias Property Alias_Retreat3 Auto Const
	ReferenceAlias Property Alias_Lockridge Auto Const
	ReferenceAlias Property Alias_Billie Auto Const
	ReferenceAlias Property Alias_Dole Auto Const
	ReferenceAlias Property Alias_Rifle1 Auto Const
	ReferenceAlias Property Alias_Rifle2 Auto Const
	ReferenceAlias Property Alias_Rifle3 Auto Const
	ReferenceAlias Property Alias_CargoAboard Auto Const
	ReferenceAlias Property Alias_CargoAtCut Auto Const
	ReferenceAlias Property Alias_CargoDelivered Auto Const
	ReferenceAlias Property Alias_CargoRetained Auto Const
	ReferenceAlias Property Alias_CargoSeized Auto Const
	ReferenceAlias Property Alias_EngineSound Auto Const
	ReferenceAlias Property Alias_EngineDamaged Auto Const
	ReferenceAlias Property Alias_Lanterns Auto Const
	ReferenceAlias Property Alias_StampInDrawer Auto Const
	ReferenceAlias Property Alias_BoardStamped Auto Const
	ReferenceAlias Property Alias_BoardSigned Auto Const
	ReferenceAlias Property Alias_BoardClosed Auto Const
	ReferenceAlias Property Alias_HeldStock Auto Const
EndGroup

Group Speech
	Message Property SayLockridgeDefault Auto Const
	Message Property SayLockridgeGateA Auto Const
	Message Property SayLockridgeGateB Auto Const
	Message Property SayLockridgeGateAlerted Auto Const
	Message Property SayLockridgeGateSold Auto Const
	Message Property SayLockridgeDole Auto Const
	Message Property SayLockridgeRails Auto Const
	Message Property SayLockridgeHired Auto Const
	Message Property SayLockridgeAfterRan Auto Const
	Message Property SayLockridgeAfterDole Auto Const
	Message Property SayLockridgeAfterSold Auto Const
	Message Property SayLockridgeHymnal Auto Const
	Message Property SayLockridgeStamp Auto Const
	Message Property SayBillieDefault Auto Const
	Message Property SayBillieFootplate Auto Const
	Message Property SayBillieCutBefore Auto Const
	Message Property SayBillieInCut Auto Const
	Message Property SayBillieRan Auto Const
	Message Property SayBillieBacked Auto Const
	Message Property SayBillieWalking Auto Const
	Message Property SayDoleDefault Auto Const
	Message Property SayDoleSermon Auto Const
	Message Property SayDoleName Auto Const
	Message Property SayDoleSilver Auto Const
	Message Property SayDoleShare Auto Const
	Message Property SayDoleShareNoBillie Auto Const
	Message Property SayDoleFace Auto Const
	Message Property SayReportKnown Auto Const
	Message Property SayReportUnknown Auto Const
EndGroup

Group Pages
	Message Property RulesPage1 Auto Const
	Message Property RulesPage2 Auto Const
	Message Property RulesPage3 Auto Const
	Message Property RulesPage4 Auto Const
	Message Property ChalkPage1 Auto Const
	Message Property ChalkPage2 Auto Const
	Message Property FlyleafPage1 Auto Const
	Message Property FlyleafPage2 Auto Const
	Message Property FlyleafPage3 Auto Const
	Message Property FlyleafPage4 Auto Const
EndGroup

Group Technical
	Message Property AskTravel Auto Const
	Message Property AskTravelAgain Auto Const
	Message Property NoteTravelNotYet Auto Const
	Message Property NoteTravelFailed Auto Const
	Message Property NoteNotAssigned Auto Const
	Message Property AskBoard Auto Const
	Message Property NoteAssignedNoBillie Auto Const
	Message Property AskDepartScene Auto Const
	Message Property AskRejoin Auto Const
	Message Property AskWalkToCut Auto Const
	Message Property NoteTrainNothing Auto Const
	Message Property AskRegulator Auto Const
	Message Property AskRunScene Auto Const
	Message Property AskReverseScene Auto Const
	Message Property AskAfterDefeat Auto Const
	Message Property AskForwardScene Auto Const
	Message Property AskCarryBackScene Auto Const
	Message Property NoteSceneFailed Auto Const
	Message Property NoteSceneStuck Auto Const
	Message Property NoteRunDone Auto Const
	Message Property NoteForwardDone Auto Const
	Message Property NoteBackedOut Auto Const
	Message Property NoteCarriedBack Auto Const
	Message Property NoteDefeat Auto Const
	Message Property AskShareOffer Auto Const
	Message Property NoteShareFailed Auto Const
	Message Property NoteSold Auto Const
	Message Property NoteSoldNoBillie Auto Const
	Message Property NoteSalePending Auto Const
	Message Property NotePlate Auto Const
	Message Property NoteDrawer Auto Const
	Message Property AskStampAlone Auto Const
	Message Property NoteStampKept Auto Const
	Message Property AskCountersignScene Auto Const
	Message Property NoteCountersigned Auto Const
	Message Property NoteStampTaken Auto Const
	Message Property NoteStampFailed Auto Const
	Message Property NoteDecisionFailed Auto Const
	Message Property NoteDrawerKept Auto Const
	Message Property NoteDrawerSigned Auto Const
	Message Property NoteDrawerGone Auto Const
	Message Property AskShowHymnal Auto Const
	Message Property NoteNoDispatch Auto Const
	Message Property NoteSaleStatus Auto Const
	Message Property AskBillieReport Auto Const
	Message Property AskBackToYard Auto Const
	Message Property AskLeaveResolved Auto Const
	Message Property AskLeaveUnresolved Auto Const
	Message Property AskLeaveAgain Auto Const
	Message Property NoteRoadComplete Auto Const
	Message Property NoteLeftUnresolved Auto Const
	Message Property NoteFall Auto Const
	Message Property LabelYard Auto Const
	Message Property LabelFootplate Auto Const
	Message Property LabelCut Auto Const
	Message Property LabelSiding Auto Const
	Message Property LabelPlatform Auto Const
	Message Property LabelLanterns Auto Const
	Message Property LabelCargoAboard Auto Const
	Message Property LabelCargoDelivered Auto Const
	Message Property LabelCargoRetained Auto Const
	Message Property LabelCargoSeized Auto Const
	Message Property LabelEngineSound Auto Const
	Message Property LabelEngineDamaged Auto Const
	Message Property LabelBoardStamped Auto Const
	Message Property LabelBoardSigned Auto Const
	Message Property LabelBoardClosed Auto Const
	Message Property LabelHeldStock Auto Const
	Message Property ReportMailDelivered Auto Const
	Message Property ReportMailRetained Auto Const
	Message Property ReportMailSeized Auto Const
	Message Property ReportMailAboard Auto Const
	Message Property ReportRan Auto Const
	Message Property ReportDoleByYou Auto Const
	Message Property ReportDoleDead Auto Const
	Message Property ReportSold Auto Const
	Message Property ReportBacked Auto Const
	Message Property ReportKnowBoth Auto Const
	Message Property ReportKnowSilver Auto Const
	Message Property ReportKnowName Auto Const
	Message Property ReportKnowNeither Auto Const
	Message Property ReportEnd Auto Const
	Message Property AskHandOver Auto Const
	Message Property NoteStampDelivered Auto Const
	Message Property NoteHandoverFailed Auto Const
	Message Property NoteAuthorityWithdrawn Auto Const
	Message Property NoteAuthorityVacant Auto Const
	Message Property NoteAuthorityFailed Auto Const
EndGroup

; ----------------------------------------------------------------- constants

; What TLM:NightMailTalk carries: who or what was used. The same numbers as
; tools/PluginBuilder/SpecNightMail.cs; a test compares them.
int NW_TRAVEL = 1 Const
int NW_RULES = 3 Const
int NW_LABEL_YARD = 4 Const
int NW_LOCKRIDGE = 5 Const
int NW_DRAWER = 6 Const
int NW_BOARD = 7 Const
int NW_HELD = 8 Const
int NW_EXIT = 9 Const
int NW_CARGO = 10 Const
int NW_LABEL_FOOTPLATE = 11 Const
int NW_BILLIE = 12 Const
int NW_DEPART = 13 Const
int NW_LABEL_CUT = 14 Const
int NW_REGULATOR = 15 Const
int NW_REVERSER = 16 Const
int NW_LANTERNS = 17 Const
int NW_DOLE = 18 Const
int NW_RIFLE1 = 19 Const
int NW_RIFLE2 = 20 Const
int NW_RIFLE3 = 21 Const
int NW_BACK = 22 Const
int NW_LABEL_SIDING = 23 Const
int NW_HYMNAL = 24 Const
int NW_PLATE = 25 Const
int NW_CHALK = 26 Const
int NW_LABEL_PLATFORM = 27 Const
int NW_ENGINE = 28 Const
int NW_FALL = 31 Const

; Where the player was last set down by a scene: which floor a fall puts them back on.
int NW_ZONE_MERCY = 0 Const
int NW_ZONE_YARD = 1 Const
int NW_ZONE_CUT = 3 Const
int NW_ZONE_PLATFORM = 5 Const

; TLM:MQ02AQuest's numbers that this script reads. The same there; a test compares them.
int NM_NONE = 0 Const
int NM_RUN = 41 Const
int NM_DEFEAT = 42 Const
int NM_SOLD = 43 Const
int NM_BACKED = 44 Const
int NM_MAIL_ABOARD = 0 Const
int NM_MAIL_DELIVERED = 1 Const
int NM_MAIL_RETAINED = 2 Const
int NM_MAIL_SEIZED = 3 Const
int NM_ENGINE_SOUND = 0 Const
int NM_ENGINE_DAMAGED = 1 Const
int NM_TRAIN_YARD = 0 Const
int NM_TRAIN_CUT = 1 Const
int NM_TRAIN_PLATFORM = 2 Const
int NM_DOLE_BY_PLAYER = 1 Const
int NM_DOLE_OTHERWISE = 2 Const
int NM_STAMP_NONE = 0 Const
int NM_STAMP_KEPT = 61 Const
int NM_STAMP_SIGNED = 62 Const
int NM_STAMP_TAKEN = 63 Const
int NM_YARD_HELD = 0 Const
int NM_SCENE_NONE = 0 Const
int NM_SCENE_DEPART = 1 Const
int NM_SCENE_RUN = 2 Const
int NM_SCENE_FORWARD = 3 Const
int NM_SCENE_REVERSE = 4 Const
int NM_SCENE_RETURN = 5 Const
int NM_SCENE_SALE = 6 Const
int NM_SCENE_DEFEAT = 7 Const
int NM_YARD_NONE = 0 Const
int NM_YARD_COUNTERSIGN = 1 Const
int NM_YARD_AUTHORITY = 2 Const
int NM_GO_NONE = 0 Const
int NM_GO_DEPART = 1 Const
int NM_GO_REJOIN = 2 Const
int NM_GO_WALK = 3 Const
int NM_AT_OPEN = 1 Const
int NM_AT_CLEAR = 2 Const
int NM_HOW_SEEN = 1 Const
int NM_HOW_TOLD = 2 Const
int NM_GREET_NONE = 0 Const
int NM_GREET_GATE = 1 Const
int NM_GREET_ALERTED = 2 Const
int NM_GREET_SOLD = 3 Const

; What OfferReport tells TLM:Act1Walk. The same numbers there; a test compares them.
int NW_REPORT_NONE = 0 Const
int NW_REPORT_GIVEN = 1 Const
int NW_REPORT_LATER = 2 Const
int NW_REPORT_CLOSED = 3 Const

; What became of a scene that needs its notice answered as well as its pieces seen.
int NW_SHOWN_UNSEEN = 0 Const
int NW_SHOWN_DONE = 1 Const
int NW_SHOWN_UNANSWERED = 2 Const

; How long a switched piece is looked for: twenty looks, a tenth of a second apart.
int SEEN_POLLS = 20 Const
; How long the player is looked for at a marker after being sent there: a hundred looks. A cell may
; have to be loaded first; nobody has measured how long that takes here.
int ARRIVE_POLLS = 100 Const

; ------------------------------------------------------------------- state

; The travel point is on. The zones are set up. A box is open: claimed with
; no call into the game between the test and the claim.
bool doorOpen = false
bool zonesUp = false
bool talking = false
int zone = 0
bool ranSaid = false
bool backedSaid = false

; ================================================================== set-up

TLM:MQ02AQuest Function Road()
	Return TLM_MQ02A as TLM:MQ02AQuest
EndFunction

ObjectReference Function Piece(ReferenceAlias akAlias)
	If !akAlias
		Return None
	EndIf
	Return akAlias.GetReference()
EndFunction

Function OpenDoor()
	{Called by TLM:Act1Walk when the first section is set up: this quest runs
	and the Mercy travel point is switched on. Nothing of Iron Junction is.}
	If doorOpen
		Return
	EndIf
	If !IsRunning()
		bool started = Start()
		bool running = IsRunning()
		If !started || !running
			Debug.Trace("TLM_NM: its quest is not running and could not be started (Start returned " + started + ", running " + running + "); there is no travel point", 2)
			Return
		EndIf
	EndIf
	ObjectReference point = Piece(Alias_MercyTravel)
	If !point
		Debug.Trace("TLM_NM: the Mercy travel point is not placed; Iron Junction cannot be reached", 2)
		Return
	EndIf
	point.EnableNoWait()
	doorOpen = true
	Debug.Trace("TLM_NM: the Mercy travel point is on")
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
	reference is in the alias of TLM_MQ02A meant for it, and the zones are on.}
	If zonesUp
		Return true
	EndIf
	TLM:MQ02AQuest river = Road()
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
			Debug.Trace("TLM_NM: not put where it belongs: " + CastNames[i])
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
	Debug.Trace("TLM_NM: Iron Junction is set up; aliases of TLM_MQ02A left empty: " + unfilled)
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

Function Put(ReferenceAlias akAlias, bool abOn)
	If abOn
		SwitchOn(akAlias)
	Else
		SwitchOff(akAlias)
	EndIf
EndFunction

bool Function SeenOn(ObjectReference akPiece)
	{The piece is placed and switched on. Looked for, for two seconds at the most.}
	If !akPiece
		Return false
	EndIf
	int tries = 0
	While tries < SEEN_POLLS && akPiece.IsDisabled()
		Utility.Wait(0.1)
		tries += 1
	EndWhile
	Return !akPiece.IsDisabled()
EndFunction

bool Function SeenOff(ObjectReference akPiece)
	{The piece is switched off, or is not placed at all and so shows nothing.}
	If !akPiece
		Return true
	EndIf
	int tries = 0
	While tries < SEEN_POLLS && !akPiece.IsDisabled()
		Utility.Wait(0.1)
		tries += 1
	EndWhile
	Return akPiece.IsDisabled()
EndFunction

bool Function Arrived(TLM:MQ02AQuest akRiver, ObjectReference akMarker)
	{The player is in the marker's cell, within reach of it. Looked for, for ten
	seconds at the most: the marker may be in a cell that has to be loaded.
	The marker's own 3D is never asked for.}
	Actor player = Game.GetPlayer()
	If !player || !akMarker
		Return false
	EndIf
	int tries = 0
	While tries < ARRIVE_POLLS && !akRiver.SeenAt(player, akMarker)
		Utility.Wait(0.1)
		tries += 1
	EndWhile
	Return akRiver.SeenAt(player, akMarker)
EndFunction

Function Refresh()
	{The pieces as the road's facts say they stand. Reads the facts; writes none.
	Called on arrival, after anything is recorded, and after a scene that was
	not seen, so that what shows is never ahead of what is recorded.}
	TLM:MQ02AQuest river = Road()
	If !river || !zonesUp
		Return
	EndIf
	int mail = river.Mail()
	int train = river.Train()
	Put(Alias_CargoAboard, mail == NM_MAIL_ABOARD && train == NM_TRAIN_YARD)
	Put(Alias_CargoAtCut, mail == NM_MAIL_ABOARD && train == NM_TRAIN_CUT)
	Put(Alias_CargoDelivered, mail == NM_MAIL_DELIVERED)
	Put(Alias_CargoRetained, mail == NM_MAIL_RETAINED)
	Put(Alias_CargoSeized, mail == NM_MAIL_SEIZED)
	bool there = train == NM_TRAIN_PLATFORM
	Put(Alias_EngineDamaged, there && river.Engine() == NM_ENGINE_DAMAGED)
	Put(Alias_EngineSound, there && river.Engine() == NM_ENGINE_SOUND)
	int decided = river.StampDecision()
	bool held = river.YardAuthority() == NM_YARD_HELD
	Put(Alias_BoardClosed, !held)
	Put(Alias_BoardSigned, held && decided == NM_STAMP_SIGNED)
	Put(Alias_BoardStamped, held && decided != NM_STAMP_SIGNED)
	Put(Alias_HeldStock, decided == NM_STAMP_SIGNED)
	Put(Alias_StampInDrawer, decided != NM_STAMP_TAKEN && !river.IsStampBeingTaken())
	PlaceBillie(river)
EndFunction

bool Function PlaceBillie(TLM:MQ02AQuest akRiver)
	{Billie where the road's facts say the engine's driver is: on the footplate
	where the train is recorded to stand, or, put off after a sale, at her
	walking marker until her return was shown and at the yard after it. She is
	never ahead of what is recorded. True if she is alive, present, in no
	fight and seen there.}
	ReferenceAlias spot = Alias_BillieFootplate
	int train = akRiver.Train()
	If akRiver.Outcome() == NM_SOLD
		If !akRiver.IsBillieReleased()
			Return false
		EndIf
		spot = Alias_BillieWalk
		If akRiver.IsBillieReported()
			spot = Alias_BillieYard
		EndIf
	ElseIf train == NM_TRAIN_CUT
		spot = Alias_BillieCut
	ElseIf train == NM_TRAIN_PLATFORM
		spot = Alias_BilliePlatform
	EndIf
	Return MoveBillie(akRiver, spot)
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

Function Notice(Message akLine)
	{A notice from an event that is not a use (a box entered, a death): shown
	only if no box is open, and claimed while it is.}
	If talking
		Return
	EndIf
	talking = true
	ShowBox(akLine)
	talking = false
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
	{Called by TLM:NightMailTalk when the player uses a person or a piece.}
	; Nothing between the test and the claim calls into the game, so two
	; activations cannot both pass.
	If talking
		Return
	EndIf
	talking = true
	TLM:MQ02AQuest river = Road()
	If !river
		Debug.Trace("TLM_NM: TLM_MQ02A does not carry TLM:MQ02AQuest; nothing can be used", 2)
	ElseIf aiWho == NW_TRAVEL
		Travel(river)
	ElseIf !zonesUp
		; A piece of Iron Junction that the player was never sent to: nothing.
	ElseIf aiWho == NW_EXIT
		; The way back is never shut, whatever has or has not been done.
		Leave(river)
	Else
		If !river.GetStageDone(10)
			; Sent here and not seen to arrive at the time: using something at the yard is being there.
			river.ArriveAtYard(Piece(Alias_YardArrival))
		EndIf
		If river.RoadOpen()
			UsedOnTheRoad(river, aiWho)
		ElseIf aiWho == NW_LABEL_YARD
			ShowBox(LabelYard)
		EndIf
	EndIf
	talking = false
EndFunction

Function UsedOnTheRoad(TLM:MQ02AQuest akRiver, int aiWho)
	; Documents and notices that begin nothing.
	If aiWho == NW_RULES
		ReadPages(RulesPage1, RulesPage2, RulesPage3, RulesPage4)
	ElseIf aiWho == NW_CHALK
		ReadPages(ChalkPage1, ChalkPage2, None, None)
	ElseIf aiWho == NW_HELD
		ShowBox(LabelHeldStock)
	ElseIf aiWho == NW_HYMNAL
		ReadHymnal(akRiver)
	ElseIf aiWho == NW_PLATE
		LookAtPlate(akRiver)
	ElseIf aiWho == NW_DRAWER
		AtDrawer(akRiver)
	ElseIf aiWho == NW_BOARD
		AtBoard(akRiver)
	ElseIf aiWho == NW_LOCKRIDGE
		TalkLockridge(akRiver)
	ElseIf aiWho == NW_RIFLE1 || aiWho == NW_RIFLE2 || aiWho == NW_RIFLE3
		; The Black Rail have no lines.
	ElseIf aiWho == NW_BACK
		; The way back along the line is never shut, whatever was begun and not seen: walking settles
		; nothing, and a scene that cannot be shown must not keep anybody in the Cut.
		BackToYard(akRiver)
	ElseIf Resume(akRiver)
		; A scene of the train was begun and not seen finished: it was tried again, and nothing else is done.
	ElseIf aiWho == NW_LABEL_YARD
		ShowBox(LabelYard)
	ElseIf aiWho == NW_LABEL_FOOTPLATE
		ShowBox(LabelFootplate)
	ElseIf aiWho == NW_LABEL_CUT
		ShowBox(LabelCut)
	ElseIf aiWho == NW_LABEL_SIDING
		ShowBox(LabelSiding)
	ElseIf aiWho == NW_LABEL_PLATFORM
		ShowBox(LabelPlatform)
	ElseIf aiWho == NW_LANTERNS
		ShowBox(LabelLanterns)
	ElseIf aiWho == NW_CARGO
		LookAtCargo(akRiver)
	ElseIf aiWho == NW_ENGINE
		LookAtEngine(akRiver)
	ElseIf aiWho == NW_BILLIE
		TalkBillie(akRiver)
	ElseIf aiWho == NW_DEPART
		AtDepart(akRiver)
	ElseIf aiWho == NW_REGULATOR || aiWho == NW_REVERSER
		AtTrain(akRiver)
	ElseIf aiWho == NW_DOLE
		TalkDole(akRiver)
	EndIf
EndFunction

Function Entered(int aiWho)
	{Called by TLM:NightMailTalk when the player enters a box. The only box is
	the one under the floors: a player who stepped off an edge is set back on
	the floor a scene last put them on. Nothing is recorded by it.}
	If aiWho != NW_FALL || !zonesUp
		Return
	EndIf
	Actor player = Game.GetPlayer()
	ObjectReference back = Piece(Alias_YardArrival)
	If zone == NW_ZONE_CUT
		back = Piece(Alias_CutArrival)
	ElseIf zone == NW_ZONE_PLATFORM
		back = Piece(Alias_PlatformArrival)
	EndIf
	If !player || player.IsDead() || !back
		Return
	EndIf
	player.MoveTo(back)
	Notice(NoteFall)
EndFunction

Function Died(int aiWho, bool abByPlayer)
	{Called by TLM:NightMailTalk when one of the people dies.}
	TLM:MQ02AQuest river = Road()
	If !river
		Return
	EndIf
	If aiWho == NW_DOLE
		river.DoleDied(abByPlayer)
		If river.Pending() == NM_SCENE_DEFEAT
			CarryOutDefeat(river, false)
		EndIf
	EndIf
	If abByPlayer
		Attacked(aiWho)
	EndIf
EndFunction

Function Attacked(int aiWho)
	{The player attacked Dole or one of the Black Rail: those of them who live
	and are not already fighting fight back. Nobody else does. Refusing a job,
	declining a share, walking away from the parley and cancelling a box are
	none of them an attack. Once Dole is dead the Black Rail do not fight on.}
	If aiWho != NW_DOLE && aiWho != NW_RIFLE1 && aiWho != NW_RIFLE2 && aiWho != NW_RIFLE3
		Return
	EndIf
	TLM:MQ02AQuest river = Road()
	If river
		If river.DoleIsDead()
			Return
		EndIf
	EndIf
	Rouse()
EndFunction

Function Rouse()
	Actor player = Game.GetPlayer()
	FightBack(Alias_Dole, player)
	FightBack(Alias_Rifle1, player)
	FightBack(Alias_Rifle2, player)
	FightBack(Alias_Rifle3, player)
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

Function Travel(TLM:MQ02AQuest akRiver)
	{The Mercy travel point: the explicit way to Iron Junction, and nothing else.}
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
	; The destination is this quest's own gate marker, by its alias: which marker it is is known before
	; anybody is sent to it. Whether its cell is loaded is not asked.
	ObjectReference yardGate = Piece(Alias_YardArrival)
	If !yardGate || !SetUp()
		ShowBox(NoteTravelFailed)
		Return
	EndIf
	Refresh()
	player.MoveTo(yardGate)
	If !Arrived(akRiver, yardGate)
		Debug.Trace("TLM_NM: the player was sent to Iron Junction and is not seen there; no arrival is recorded", 2)
		ShowBox(NoteTravelFailed)
		Return
	EndIf
	zone = NW_ZONE_YARD
	akRiver.ArriveAtYard(yardGate)
EndFunction

Function Leave(TLM:MQ02AQuest akRiver)
	{The road to Mercy. Leaving with nothing settled settles nothing.}
	int pick = -1
	If akRiver.GetStageDone(100)
		pick = ShowBox(AskLeaveAgain)
	ElseIf akRiver.CanComplete()
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
	If !Arrived(akRiver, back)
		Debug.Trace("TLM_NM: the player was sent to Mercy and is not seen there; the road is not completed by it", 2)
		Return
	EndIf
	zone = NW_ZONE_MERCY
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

Function BackToYard(TLM:MQ02AQuest akRiver)
	{On foot along the line to the yard, from the Cut or the platform. A move of the player; the train
	and everything aboard stay where they are and nothing is settled.}
	ObjectReference yard = Piece(Alias_YardArrival)
	If !yard
		Return
	EndIf
	int mark = akRiver.RoadMark()
	If ShowBox(AskBackToYard) != 0
		Return
	EndIf
	Actor player = Game.GetPlayer()
	yard = Piece(Alias_YardArrival)
	If !player || !yard || !akRiver.RoadOpen() || akRiver.RoadMark() != mark
		Return
	EndIf
	player.MoveTo(yard)
	If Arrived(akRiver, yard)
		zone = NW_ZONE_YARD
	EndIf
EndFunction

; ========================================================== Augusta Lockridge

Function TalkLockridge(TLM:MQ02AQuest akRiver)
	If !akRiver.LockridgeCanSpeak()
		Return
	EndIf
	If !akRiver.LockridgeDispatches()
		; Her dispatching was withdrawn: she gives no job, shows no stamp and signs nothing.
		ShowBox(NoteNoDispatch)
		Return
	EndIf
	If akRiver.Outcome() == NM_SOLD
		AfterSale(akRiver)
		Return
	EndIf
	If akRiver.CanShowHymnal()
		int show = ShowBox(AskShowHymnal)
		If !akRiver.CanShowHymnal()
			Return
		EndIf
		If show == 0
			ShowHymnal(akRiver)
			Return
		EndIf
		; Only the explicit "Not now" goes on to what she would otherwise say.
		If show != 1 || !akRiver.RoadOpen() || !akRiver.LockridgeCanSpeak()
			Return
		EndIf
	EndIf
	int greet = akRiver.Greeting()
	If greet != NM_GREET_NONE
		Gate(akRiver, greet)
		Return
	EndIf
	int course = akRiver.Outcome()
	; The full after-run quotation claims payroll in her safe. This greybox
	; represents both cargoes at the valley and has no such custody fact.
	; Withhold that compound quotation; the independent drawer stays usable.
	If course == NM_DEFEAT && akRiver.DoleIsDead() && !akRiver.KnowsName()
		ShowBox(SayLockridgeAfterDole)
	Else
		ShowBox(SayLockridgeDefault)
	EndIf
EndFunction

Function Gate(TLM:MQ02AQuest akRiver, int aiGreet)
	{Her gate greeting and the job. Its buttons are put back into the places of
	the plain greeting's: 0 the job, 1 who chalks the hymns, 2 who passes the
	trains, 3 not tonight.}
	int mark = akRiver.RoadMark()
	int pick = -1
	If aiGreet == NM_GREET_ALERTED
		pick = ShowBox(SayLockridgeGateAlerted)
		If pick >= 1
			pick += 1
		EndIf
	ElseIf aiGreet == NM_GREET_SOLD
		pick = ShowBox(SayLockridgeGateSold)
		If pick == 2
			pick = 3
		EndIf
	Else
		If !Said(SayLockridgeGateA)
			Return
		EndIf
		If !akRiver.RoadOpen() || akRiver.RoadMark() != mark || !akRiver.LockridgeCanSpeak()
			Return
		EndIf
		pick = ShowBox(SayLockridgeGateB)
	EndIf
	; Her question is answered to her: alive, present and in no fight after it as before it.
	If !akRiver.RoadOpen() || akRiver.RoadMark() != mark || !akRiver.LockridgeCanSpeak()
		Return
	EndIf
	If pick == 0
		Hire(akRiver)
	ElseIf pick == 1
		ShowBox(SayLockridgeDole)
	ElseIf pick == 2
		ShowBox(SayLockridgeRails)
	EndIf
	; 3, "Not tonight.", and anything else: nothing. Refusing starts no fight and loses nothing.
EndFunction

Function Hire(TLM:MQ02AQuest akRiver)
	{"I'll ride your mail." Her answer names Billie as the driver, so it is hers
	to give only with Billie alive and present; otherwise the assignment is
	acknowledged by this build's own notice. The job is taken once it is answered.}
	If akRiver.BillieIsThere()
		If !Said(SayLockridgeHired)
			Return
		EndIf
	ElseIf !Said(NoteAssignedNoBillie)
		Return
	EndIf
	If !akRiver.RoadOpen() || !akRiver.LockridgeCanSpeak()
		Return
	EndIf
	akRiver.AcceptJob()
EndFunction

Function AfterSale(TLM:MQ02AQuest akRiver)
	{What she says of the sale is that Billie walked in at four this morning and
	told her. That is hers to say only once Billie's return and report, and the
	morning it happened in, have been shown. Until then: this build's own status.}
	If akRiver.IsBillieReported()
		ShowBox(SayLockridgeAfterSold)
		Return
	EndIf
	If !akRiver.BillieReportDue()
		ShowBox(NoteSaleStatus)
		Return
	EndIf
	ObjectReference spot = Piece(Alias_BillieYard)
	If !spot
		ShowBox(NoteSaleStatus)
		Return
	EndIf
	int mark = akRiver.RoadMark()
	int pick = ShowBox(AskBillieReport)
	If pick != 0
		If pick == 1
			ShowBox(NoteSaleStatus)
		EndIf
		Return
	EndIf
	If !akRiver.RoadOpen() || akRiver.RoadMark() != mark || !akRiver.BillieReportDue()
		Return
	EndIf
	MoveBillie(akRiver, Alias_BillieYard)
	If !akRiver.FinishBillieReport(spot)
		Debug.Trace("TLM_NM: Billie Tupper's return to the yard was shown and she is not seen there; what Lockridge says of it is not said", 2)
		ShowBox(NoteSceneFailed)
		Return
	EndIf
	If akRiver.LockridgeCanSpeak()
		ShowBox(SayLockridgeAfterSold)
	EndIf
EndFunction

Function ShowHymnal(TLM:MQ02AQuest akRiver)
	{The real book, shown to a living Lockridge with Dole alive: her answer, and
	then the drawer she tells the player to open.}
	If !akRiver.CanShowHymnal()
		Return
	EndIf
	If ShowBox(SayLockridgeHymnal) != 0
		Return
	EndIf
	If !akRiver.CanShowHymnal()
		Return
	EndIf
	If !akRiver.ShowHymnal()
		Return
	EndIf
	If akRiver.FindStamp()
		Decide(akRiver)
	EndIf
EndFunction

; ================================================================ the drawer

Function AtDrawer(TLM:MQ02AQuest akRiver)
	{The top drawer of her desk. Open to anybody at the yard, whoever lives.}
	If ResumeYard(akRiver)
		Return
	EndIf
	If !akRiver.GetStageDone(60)
		If ShowBox(NoteDrawer) != 0
			Return
		EndIf
		If !akRiver.RoadOpen() || !akRiver.FindStamp()
			Return
		EndIf
	EndIf
	Decide(akRiver)
EndFunction

Function Decide(TLM:MQ02AQuest akRiver)
	{What becomes of the stamp. Her question, with her three answers and a way
	to close the drawer, if she is alive, present, in no fight and still runs
	the yard; without her, only what does not need her: take it, or leave it.}
	int decided = akRiver.StampDecision()
	If decided == NM_STAMP_KEPT
		ShowBox(NoteDrawerKept)
		Return
	ElseIf decided == NM_STAMP_SIGNED
		ShowBox(NoteDrawerSigned)
		Return
	ElseIf decided == NM_STAMP_TAKEN
		ShowBox(NoteDrawerGone)
		Return
	EndIf
	If !akRiver.StampUndecided()
		Return
	EndIf
	If !Piece(Alias_StampInDrawer)
		Debug.Trace("TLM_NM: the stamp's piece in the drawer is not placed; nothing can be decided about it", 2)
		ShowBox(NoteSceneStuck)
		Return
	EndIf
	int mark = akRiver.StampMark()
	bool hers = akRiver.LockridgeCanSpeak() && akRiver.LockridgeDispatches()
	int pick = -1
	If hers
		pick = ShowBox(SayLockridgeStamp)
	Else
		pick = ShowBox(AskStampAlone)
		; Its two buttons are her third answer and the way to close the drawer.
		If pick == 0
			pick = 2
		ElseIf pick == 1
			pick = 3
		EndIf
	EndIf
	If !akRiver.RoadOpen() || akRiver.StampMark() != mark
		Return
	EndIf
	If hers && !akRiver.LockridgeCanSpeak()
		; Her question is answered to her. The drawer can be opened again without her.
		Return
	EndIf
	If pick == 0
		If akRiver.KeepStamping(Piece(Alias_StampInDrawer))
			ShowBox(NoteStampKept)
		Else
			ShowBox(NoteDecisionFailed)
		EndIf
	ElseIf pick == 1
		Countersign(akRiver)
	ElseIf pick == 2
		Take(akRiver)
	EndIf
	; 3, closing the drawer, and anything else: nothing is decided.
EndFunction

Function Countersign(TLM:MQ02AQuest akRiver)
	int mark = akRiver.StampMark()
	If ShowBox(AskCountersignScene) != 0
		Return
	EndIf
	If !akRiver.RoadOpen() || akRiver.StampMark() != mark || !akRiver.LockridgeCanSpeak()
		Return
	EndIf
	If !akRiver.BeginCountersign(Piece(Alias_StampInDrawer))
		ShowBox(NoteDecisionFailed)
		Return
	EndIf
	CarryOutCountersign(akRiver)
EndFunction

Function CarryOutCountersign(TLM:MQ02AQuest akRiver)
	If akRiver.AbandonCountersign()
		; She is dead or gone before it could be shown: a dead woman countersigns nothing.
		Refresh()
		ShowBox(NoteDecisionFailed)
		Return
	EndIf
	; A temporary loss of the observer or eligible signatory preserves intent.
	If !akRiver.PlayerIsAlive() || !akRiver.LockridgeCanSpeak()
		Refresh()
		Return
	EndIf
	ObjectReference signed = Piece(Alias_BoardSigned)
	ObjectReference stamped = Piece(Alias_BoardStamped)
	ObjectReference held = Piece(Alias_HeldStock)
	If !signed || !held
		Debug.Trace("TLM_NM: the countersigned board or the held stock is not placed: the countersigning cannot be shown or recorded. Report this line.", 2)
		ShowBox(NoteSceneStuck)
		Return
	EndIf
	SwitchOn(Alias_BoardSigned)
	SwitchOff(Alias_BoardStamped)
	SwitchOn(Alias_HeldStock)
	bool done = false
	If SeenOn(signed) && SeenOff(stamped) && SeenOn(held)
		done = akRiver.FinishCountersign(signed, stamped, held)
	EndIf
	Refresh()
	If done
		ShowBox(NoteCountersigned)
	Else
		Debug.Trace("TLM_NM: the countersigning was not seen; nothing is recorded. Use the drawer or the dispatch board again.", 2)
		ShowBox(NoteSceneFailed)
	EndIf
EndFunction

Function Take(TLM:MQ02AQuest akRiver)
	If !akRiver.TakeStamp(Piece(Alias_StampInDrawer))
		ShowBox(NoteStampFailed)
		Return
	EndIf
	CarryOutTake(akRiver)
EndFunction

Function CarryOutTake(TLM:MQ02AQuest akRiver)
	{The stamp is with the player. The drawer is shown without it, and only then is it recorded taken.}
	ObjectReference inDrawer = Piece(Alias_StampInDrawer)
	SwitchOff(Alias_StampInDrawer)
	If SeenOff(inDrawer) && akRiver.ConfirmStampTaken(inDrawer)
		ShowBox(NoteStampTaken)
		Return
	EndIf
	Debug.Trace("TLM_NM: the stamp is in the inventory and the drawer still shows it; the taking is not recorded yet. Use the drawer again.", 2)
	ShowBox(NoteSceneFailed)
EndFunction

bool Function ResumeYard(TLM:MQ02AQuest akRiver)
	{A scene of the yard was begun and not seen finished: it is tried again. True if there was one.}
	int scene = akRiver.PendingAtYard()
	If scene == NM_YARD_COUNTERSIGN
		CarryOutCountersign(akRiver)
		Return true
	ElseIf scene == NM_YARD_AUTHORITY
		If CarryOutAuthority(akRiver) == NW_SHOWN_UNSEEN
			ShowBox(NoteAuthorityFailed)
		EndIf
		Return true
	ElseIf akRiver.IsStampBeingTaken()
		CarryOutTake(akRiver)
		Return true
	EndIf
	Return false
EndFunction

Function AtBoard(TLM:MQ02AQuest akRiver)
	{The dispatch board: what the yard's inspections stand as.}
	If ResumeYard(akRiver)
		Return
	EndIf
	If akRiver.YardAuthority() != NM_YARD_HELD
		ShowBox(LabelBoardClosed)
	ElseIf akRiver.StampDecision() == NM_STAMP_SIGNED
		ShowBox(LabelBoardSigned)
	Else
		ShowBox(LabelBoardStamped)
	EndIf
EndFunction

int Function CarryOutAuthority(TLM:MQ02AQuest akRiver, Actor akSheriff = None)
	{The yard without a master: its dispatch board closed and the other two
	off, LOOKED AT, then acknowledged, then recorded. NW_SHOWN_DONE if it is
	recorded; NW_SHOWN_UNSEEN if the boards could not be seen so;
	NW_SHOWN_UNANSWERED if they were and its notice was not answered.
	Lockridge is not moved, switched off or harmed: what stops is what she
	does (TalkLockridge, Decide). If she is dead already that is said, and no
	withdrawal is shown.}
	ObjectReference closed = Piece(Alias_BoardClosed)
	ObjectReference stamped = Piece(Alias_BoardStamped)
	ObjectReference signed = Piece(Alias_BoardSigned)
	If !closed
		Debug.Trace("TLM_NM: the closed dispatch board is not placed: the yard's change cannot be shown or recorded. The stamp stays delivered. Report this line.", 2)
		Return NW_SHOWN_UNSEEN
	EndIf
	SwitchOn(Alias_BoardClosed)
	SwitchOff(Alias_BoardStamped)
	SwitchOff(Alias_BoardSigned)
	int shown = NW_SHOWN_UNSEEN
	If SeenOn(closed) && SeenOff(stamped) && SeenOff(signed)
		shown = NW_SHOWN_UNANSWERED
		int pick = -1
		If akRiver.LockridgeIsDead()
			pick = ShowBox(NoteAuthorityVacant)
		Else
			pick = ShowBox(NoteAuthorityWithdrawn)
		EndIf
		; A yard-board retry has no recipient. Inside his conversation, however,
		; the current sheriff must still be eligible before this new commitment.
		If !akRiver.PlayerIsAlive() || (akSheriff && !StillHere(akSheriff, Game.GetPlayer()))
			Refresh()
			Return NW_SHOWN_UNANSWERED
		EndIf
		If pick == 0
			If akRiver.FinishAuthority(closed, stamped, signed)
				shown = NW_SHOWN_DONE
			Else
				shown = NW_SHOWN_UNSEEN
			EndIf
		EndIf
	EndIf
	; The boards as the facts now stand: closed if it was recorded, as they were if it was not.
	Refresh()
	Return shown
EndFunction

; ============================================================== Billie Tupper

bool Function MoveBillie(TLM:MQ02AQuest akRiver, ReferenceAlias akWhere)
	{Billie, alive, present and in no fight, is set at that marker unless she
	stands there already. Nobody else is moved by it. True if she is seen there.}
	ObjectReference where = Piece(akWhere)
	If !where || !akRiver.BillieCanSpeak()
		Return false
	EndIf
	Actor billie = Alias_Billie.GetActorReference()
	If !billie
		Return false
	EndIf
	If !akRiver.StandsAt(billie, where)
		billie.MoveTo(where)
	EndIf
	Return akRiver.StandsAt(billie, where)
EndFunction

Function TalkBillie(TLM:MQ02AQuest akRiver)
	If !akRiver.BillieCanSpeak()
		Return
	EndIf
	int course = akRiver.Outcome()
	If course == NM_SOLD && akRiver.IsBillieReleased()
		ShowBox(SayBillieWalking)
	ElseIf akRiver.TrainOffered() == NM_AT_OPEN
		InCut(akRiver, true)
	ElseIf course == NM_RUN && akRiver.DidBillieDrive() && !ranSaid
		If Said(SayBillieRan)
			ranSaid = true
		EndIf
	ElseIf course == NM_BACKED && akRiver.DidBillieDrive() && !backedSaid && !akRiver.AnybodyDead()
		If Said(SayBillieBacked)
			backedSaid = true
		EndIf
	ElseIf akRiver.Assigned() && !akRiver.GetStageDone(40) && akRiver.Train() == NM_TRAIN_YARD && course == NM_NONE
		int pick = ShowBox(SayBillieFootplate)
		If pick == 1 && akRiver.RoadOpen() && akRiver.BillieCanSpeak()
			ShowBox(SayBillieCutBefore)
		EndIf
	Else
		ShowBox(SayBillieDefault)
	EndIf
EndFunction

; ==================================================================== the train

Function AtDepart(TLM:MQ02AQuest akRiver)
	{The departure control on the footplate in the yard.}
	int go = akRiver.GoOffered()
	If go == NM_GO_NONE
		If akRiver.Assigned() || akRiver.Train() != NM_TRAIN_YARD || akRiver.Outcome() != NM_NONE || !akRiver.Unsettled()
			ShowBox(NoteTrainNothing)
			Return
		EndIf
		If akRiver.LockridgeCanSpeak() && akRiver.LockridgeDispatches()
			; The job is hers to give.
			ShowBox(NoteNotAssigned)
			Return
		EndIf
		; Nobody at the yard can give it: the labelled way to take it on.
		int mark = akRiver.RoadMark()
		If ShowBox(AskBoard) != 0
			Return
		EndIf
		If !akRiver.RoadOpen() || akRiver.RoadMark() != mark || !akRiver.BoardUnassigned()
			Return
		EndIf
		go = akRiver.GoOffered()
	EndIf
	If go == NM_GO_REJOIN
		Rejoin(akRiver, AskRejoin)
	ElseIf go == NM_GO_WALK
		Rejoin(akRiver, AskWalkToCut)
	ElseIf go == NM_GO_DEPART
		Depart(akRiver)
	EndIf
EndFunction

Function Depart(TLM:MQ02AQuest akRiver)
	If !Piece(Alias_CutArrival) || !Piece(Alias_Lanterns)
		Debug.Trace("TLM_NM: the Cut's footplate marker or its lanterns are not placed: the journey cannot be shown. Report this line.", 2)
		ShowBox(NoteSceneStuck)
		Return
	EndIf
	If akRiver.Pending() != NM_SCENE_DEPART
		int mark = akRiver.RoadMark()
		If ShowBox(AskDepartScene) != 0
			Return
		EndIf
		If !akRiver.RoadOpen() || akRiver.RoadMark() != mark || !Piece(Alias_CutArrival) || !Piece(Alias_Lanterns)
			Return
		EndIf
		If !akRiver.BeginDepart()
			Return
		EndIf
	EndIf
	CarryOutDepart(akRiver)
EndFunction

Function CarryOutDepart(TLM:MQ02AQuest akRiver)
	Actor player = Game.GetPlayer()
	ObjectReference cut = Piece(Alias_CutArrival)
	ObjectReference lanterns = Piece(Alias_Lanterns)
	bool done = false
	If cut && lanterns && player && akRiver.PlayerIsAlive()
		SwitchOn(Alias_Lanterns)
		player.MoveTo(cut)
		If Arrived(akRiver, cut)
			zone = NW_ZONE_CUT
			If SeenOn(lanterns)
				done = akRiver.FinishDepart(cut, lanterns)
			EndIf
		EndIf
	EndIf
	Refresh()
	If !done
		Debug.Trace("TLM_NM: the journey to the Cut was not seen; nothing is recorded. Use the departure control, or a control where you stand, again.", 2)
		ShowBox(NoteSceneFailed)
	EndIf
EndFunction

Function Rejoin(TLM:MQ02AQuest akRiver, Message akAsk)
	{On foot along the line to the Cut: back to the train that stands there, or, when it has gone on, been
	taken or gone home, to the siding it left. Nothing is settled and no train is moved.}
	ObjectReference cut = Piece(Alias_CutArrival)
	If !cut
		Return
	EndIf
	int mark = akRiver.RoadMark()
	If ShowBox(akAsk) != 0
		Return
	EndIf
	Actor player = Game.GetPlayer()
	cut = Piece(Alias_CutArrival)
	If !player || !cut || !akRiver.RoadOpen() || akRiver.RoadMark() != mark
		Return
	EndIf
	player.MoveTo(cut)
	If Arrived(akRiver, cut)
		zone = NW_ZONE_CUT
	EndIf
EndFunction

bool Function Resume(TLM:MQ02AQuest akRiver)
	{A scene of the train or the encounter was begun and not seen finished: it
	is carried out again, as far as it is not done, and looked at again. True
	if there was one. No scene is begun by this and none becomes another.}
	int scene = akRiver.Pending()
	If scene == NM_SCENE_NONE
		; A death that was never heard of is found here.
		If akRiver.DoleIsDead()
			akRiver.DoleDied(false)
			scene = akRiver.Pending()
		EndIf
		If scene == NM_SCENE_NONE
			Return false
		EndIf
	EndIf
	If scene == NM_SCENE_DEPART
		CarryOutDepart(akRiver)
	ElseIf scene == NM_SCENE_RUN
		CarryOutRun(akRiver)
	ElseIf scene == NM_SCENE_FORWARD
		CarryOutForward(akRiver)
	ElseIf scene == NM_SCENE_REVERSE
		CarryOutReverse(akRiver)
	ElseIf scene == NM_SCENE_RETURN
		CarryOutCarryBack(akRiver)
	ElseIf scene == NM_SCENE_SALE
		CarryOutSale(akRiver)
	ElseIf scene == NM_SCENE_DEFEAT
		CarryOutDefeat(akRiver, true)
	EndIf
	Return true
EndFunction

Function AtTrain(TLM:MQ02AQuest akRiver)
	{The regulator and the reverser where the footplate stands in the Cut.}
	int at = akRiver.TrainOffered()
	If at == NM_AT_OPEN
		InCut(akRiver, akRiver.BillieCanSpeak())
	ElseIf at == NM_AT_CLEAR
		int mark = akRiver.RoadMark()
		int pick = ShowBox(AskAfterDefeat)
		If !akRiver.RoadOpen() || akRiver.RoadMark() != mark
			Return
		EndIf
		If pick == 0
			Forward(akRiver)
		ElseIf pick == 1
			CarryBack(akRiver)
		EndIf
	Else
		ShowBox(NoteTrainNothing)
	EndIf
EndFunction

Function InCut(TLM:MQ02AQuest akRiver, bool abHers)
	{At the lanterns: run, get down, or back out. Billie's line if she is alive,
	present and in no fight to say it; if not, this build's own box at the
	regulator with the same three answers.}
	int mark = akRiver.RoadMark()
	int pick = -1
	If abHers
		pick = ShowBox(SayBillieInCut)
	Else
		pick = ShowBox(AskRegulator)
	EndIf
	If !akRiver.RoadOpen() || akRiver.RoadMark() != mark
		Return
	EndIf
	If abHers && !akRiver.BillieCanSpeak()
		; Her question is answered to her. The regulator can be used again without her.
		Return
	EndIf
	If pick == 0
		Run(akRiver)
	ElseIf pick == 2
		Reverse(akRiver)
	EndIf
	; 1, "Stop her. I'm getting down.": the train is standing. The player walks down to Dole.
EndFunction

; ---------------------------------------------------------------------- the run

Function Run(TLM:MQ02AQuest akRiver)
	If !Piece(Alias_PlatformArrival) || !Piece(Alias_CargoDelivered) || !Piece(Alias_EngineDamaged)
		Debug.Trace("TLM_NM: the platform's marker, its cargo or the damaged engine is not placed: the run cannot be shown. Report this line.", 2)
		ShowBox(NoteSceneStuck)
		Return
	EndIf
	int mark = akRiver.RoadMark()
	If ShowBox(AskRunScene) != 0
		Return
	EndIf
	If !akRiver.RoadOpen() || akRiver.RoadMark() != mark || !Piece(Alias_PlatformArrival)
		Return
	EndIf
	If !akRiver.BeginRun()
		Return
	EndIf
	CarryOutRun(akRiver)
EndFunction

Function CarryOutRun(TLM:MQ02AQuest akRiver)
	Actor player = Game.GetPlayer()
	ObjectReference platform = Piece(Alias_PlatformArrival)
	ObjectReference delivered = Piece(Alias_CargoDelivered)
	ObjectReference aboard = Piece(Alias_CargoAtCut)
	ObjectReference damaged = Piece(Alias_EngineDamaged)
	bool done = false
	If platform && delivered && damaged && player && akRiver.PlayerIsAlive()
		SwitchOn(Alias_CargoDelivered)
		SwitchOff(Alias_CargoAtCut)
		SwitchOn(Alias_EngineDamaged)
		SwitchOff(Alias_EngineSound)
		player.MoveTo(platform)
		If Arrived(akRiver, platform)
			zone = NW_ZONE_PLATFORM
			If SeenOn(delivered) && SeenOff(aboard) && SeenOn(damaged)
				done = akRiver.FinishRun(platform, delivered, aboard, damaged)
			EndIf
		EndIf
	EndIf
	Refresh()
	If !done
		Debug.Trace("TLM_NM: the run was not seen finished; nothing is recorded and it stays begun. Use a control where you stand again.", 2)
		ShowBox(NoteSceneFailed)
		Return
	EndIf
	ShowBox(NoteRunDone)
	; Hers to say if she drove and is seen at the platform with the engine.
	If akRiver.DidBillieDrive() && !ranSaid && PlaceBillie(akRiver)
		If Said(SayBillieRan)
			ranSaid = true
		EndIf
	EndIf
EndFunction

; ------------------------------------------------------------------ the reverse

Function Reverse(TLM:MQ02AQuest akRiver)
	If !Piece(Alias_YardFootplate) || !Piece(Alias_CargoRetained)
		Debug.Trace("TLM_NM: the yard's footplate marker or its retained cargo is not placed: the reverse cannot be shown. Report this line.", 2)
		ShowBox(NoteSceneStuck)
		Return
	EndIf
	int mark = akRiver.RoadMark()
	If ShowBox(AskReverseScene) != 0
		Return
	EndIf
	If !akRiver.RoadOpen() || akRiver.RoadMark() != mark || !Piece(Alias_YardFootplate)
		Return
	EndIf
	If !akRiver.BeginReverse()
		Return
	EndIf
	CarryOutReverse(akRiver)
EndFunction

bool Function BackAtTheYard(TLM:MQ02AQuest akRiver)
	{The train's cargo locked up at the yard and the player on the yard's footplate: shown, and looked at.}
	Actor player = Game.GetPlayer()
	ObjectReference yard = Piece(Alias_YardFootplate)
	ObjectReference retained = Piece(Alias_CargoRetained)
	ObjectReference aboard = Piece(Alias_CargoAtCut)
	If !yard || !retained || !player || !akRiver.PlayerIsAlive()
		Return false
	EndIf
	SwitchOn(Alias_CargoRetained)
	SwitchOff(Alias_CargoAtCut)
	player.MoveTo(yard)
	If !Arrived(akRiver, yard)
		Return false
	EndIf
	zone = NW_ZONE_YARD
	Return SeenOn(retained) && SeenOff(aboard)
EndFunction

Function CarryOutReverse(TLM:MQ02AQuest akRiver)
	bool done = false
	If BackAtTheYard(akRiver)
		done = akRiver.FinishReverse(Piece(Alias_YardFootplate), Piece(Alias_CargoRetained), Piece(Alias_CargoAtCut))
	EndIf
	Refresh()
	If !done
		Debug.Trace("TLM_NM: the reverse was not seen finished; nothing is recorded and it stays begun. Use a control where you stand again.", 2)
		ShowBox(NoteSceneFailed)
		Return
	EndIf
	ShowBox(NoteBackedOut)
	; "Nobody's dead" is hers to say only if she drove, and nobody is.
	If akRiver.DidBillieDrive() && !akRiver.AnybodyDead() && !backedSaid && PlaceBillie(akRiver)
		If Said(SayBillieBacked)
			backedSaid = true
		EndIf
	EndIf
EndFunction

; ---------------------------------------------------- the mail after the defeat

Function Forward(TLM:MQ02AQuest akRiver)
	If !Piece(Alias_PlatformArrival) || !Piece(Alias_CargoDelivered) || !Piece(Alias_EngineSound)
		Debug.Trace("TLM_NM: the platform's marker, its cargo or the engine is not placed: the delivery cannot be shown. Report this line.", 2)
		ShowBox(NoteSceneStuck)
		Return
	EndIf
	int mark = akRiver.RoadMark()
	If ShowBox(AskForwardScene) != 0
		Return
	EndIf
	If !akRiver.RoadOpen() || akRiver.RoadMark() != mark || !Piece(Alias_PlatformArrival)
		Return
	EndIf
	If !akRiver.BeginForward()
		Return
	EndIf
	CarryOutForward(akRiver)
EndFunction

Function CarryOutForward(TLM:MQ02AQuest akRiver)
	Actor player = Game.GetPlayer()
	ObjectReference platform = Piece(Alias_PlatformArrival)
	ObjectReference delivered = Piece(Alias_CargoDelivered)
	ObjectReference aboard = Piece(Alias_CargoAtCut)
	ObjectReference sound = Piece(Alias_EngineSound)
	bool done = false
	If platform && delivered && sound && player && akRiver.PlayerIsAlive()
		SwitchOn(Alias_CargoDelivered)
		SwitchOff(Alias_CargoAtCut)
		SwitchOn(Alias_EngineSound)
		SwitchOff(Alias_EngineDamaged)
		player.MoveTo(platform)
		If Arrived(akRiver, platform)
			zone = NW_ZONE_PLATFORM
			If SeenOn(delivered) && SeenOff(aboard) && SeenOn(sound)
				done = akRiver.FinishForward(platform, delivered, aboard, sound)
			EndIf
		EndIf
	EndIf
	Refresh()
	If done
		ShowBox(NoteForwardDone)
	Else
		Debug.Trace("TLM_NM: the delivery was not seen finished; nothing is recorded and it stays begun. Use a control where you stand again.", 2)
		ShowBox(NoteSceneFailed)
	EndIf
EndFunction

Function CarryBack(TLM:MQ02AQuest akRiver)
	If !Piece(Alias_YardFootplate) || !Piece(Alias_CargoRetained)
		Debug.Trace("TLM_NM: the yard's footplate marker or its retained cargo is not placed: the return cannot be shown. Report this line.", 2)
		ShowBox(NoteSceneStuck)
		Return
	EndIf
	int mark = akRiver.RoadMark()
	If ShowBox(AskCarryBackScene) != 0
		Return
	EndIf
	If !akRiver.RoadOpen() || akRiver.RoadMark() != mark || !Piece(Alias_YardFootplate)
		Return
	EndIf
	If !akRiver.BeginCarryBack()
		Return
	EndIf
	CarryOutCarryBack(akRiver)
EndFunction

Function CarryOutCarryBack(TLM:MQ02AQuest akRiver)
	bool done = false
	If BackAtTheYard(akRiver)
		done = akRiver.FinishCarryBack(Piece(Alias_YardFootplate), Piece(Alias_CargoRetained), Piece(Alias_CargoAtCut))
	EndIf
	Refresh()
	If done
		ShowBox(NoteCarriedBack)
	Else
		Debug.Trace("TLM_NM: the return was not seen finished; nothing is recorded and it stays begun. Use a control where you stand again.", 2)
		ShowBox(NoteSceneFailed)
	EndIf
EndFunction

; ================================================================ Ezekiel Dole

Function TalkDole(TLM:MQ02AQuest akRiver)
	If !akRiver.DoleCanSpeak()
		Return
	EndIf
	If akRiver.TrainOffered() == NM_AT_OPEN
		Sermon(akRiver)
	Else
		ShowBox(SayDoleDefault)
	EndIf
EndFunction

bool Function StillHis(TLM:MQ02AQuest akRiver, int aiMark)
	{After one of Dole's boxes: the player alive on a road that stands as it stood, and Dole alive,
	present and in no fight to have said it.}
	Return akRiver.RoadOpen() && akRiver.RoadMark() == aiMark && akRiver.DoleCanSpeak()
EndFunction

Function Sermon(TLM:MQ02AQuest akRiver)
	int mark = akRiver.RoadMark()
	int pick = ShowBox(SayDoleSermon)
	If pick < 0 || pick > 3 || !StillHis(akRiver, mark)
		Return
	EndIf
	akRiver.MeetDole()
	If pick == 0
		Face(akRiver, mark)
	ElseIf pick == 1
		Share(akRiver, mark)
	ElseIf pick == 2
		HisName(akRiver, mark)
	EndIf
	; 3, "(Go back to the footplate)": nothing. Walking away from the parley starts no fight.
EndFunction

Function HisName(TLM:MQ02AQuest akRiver, int aiMark)
	int pick = ShowBox(SayDoleName)
	If pick < 0 || pick > 2 || !StillHis(akRiver, aiMark)
		; Not answered, or he is not there to have said it: nothing is learned by it.
		Return
	EndIf
	akRiver.LearnName(NM_HOW_TOLD)
	If pick == 0
		HisSilver(akRiver, aiMark)
	ElseIf pick == 1
		Face(akRiver, aiMark)
	Else
		Share(akRiver, aiMark)
	EndIf
EndFunction

Function HisSilver(TLM:MQ02AQuest akRiver, int aiMark)
	int pick = ShowBox(SayDoleSilver)
	If pick < 0 || pick > 1 || !StillHis(akRiver, aiMark)
		Return
	EndIf
	akRiver.LearnSilver(NM_HOW_TOLD)
	If pick == 0
		Face(akRiver, aiMark)
	Else
		Share(akRiver, aiMark)
	EndIf
EndFunction

Function Face(TLM:MQ02AQuest akRiver, int aiMark)
	{"Stand aside." His answer; and once it is answered, the fight the player chose.}
	If !StillHis(akRiver, aiMark) || akRiver.TrainOffered() != NM_AT_OPEN
		Return
	EndIf
	If !Said(SayDoleFace)
		Return
	EndIf
	If !StillHis(akRiver, aiMark) || !akRiver.FaceDole(aiMark)
		Return
	EndIf
	Rouse()
EndFunction

Function Share(TLM:MQ02AQuest akRiver, int aiMark)
	{His offer. His whole line promises that Billie walks home unharmed, so it is
	his to say only with Billie alive and present; without her, the rest of it,
	and the offer itself as this build's own text. "No." is, as the writing has
	it, the confrontation; walking back to the footplate is not.}
	If !akRiver.ShareOffered()
		ShowBox(NoteShareFailed)
		Return
	EndIf
	int pick = -1
	If akRiver.BillieIsThere()
		pick = ShowBox(SayDoleShare)
	Else
		If !Said(SayDoleShareNoBillie)
			Return
		EndIf
		If !StillHis(akRiver, aiMark)
			Return
		EndIf
		pick = ShowBox(AskShareOffer)
	EndIf
	If !StillHis(akRiver, aiMark)
		Return
	EndIf
	If pick == 0
		Sell(akRiver)
	ElseIf pick == 1
		Face(akRiver, aiMark)
	EndIf
EndFunction

Function Sell(TLM:MQ02AQuest akRiver)
	If !Piece(Alias_CargoSeized)
		Debug.Trace("TLM_NM: the seized cargo's piece is not placed: a sale cannot be shown, and none is made. Report this line.", 2)
		ShowBox(NoteSceneStuck)
		Return
	EndIf
	If !akRiver.TakeShare()
		ShowBox(NoteShareFailed)
		Return
	EndIf
	CarryOutSale(akRiver)
EndFunction

Function CarryOutSale(TLM:MQ02AQuest akRiver)
	{Paid. The cargo off the train and Billie, if she lives, safe at her walking
	marker: shown, looked at, and only then is the mail sold.}
	ObjectReference seized = Piece(Alias_CargoSeized)
	ObjectReference aboard = Piece(Alias_CargoAtCut)
	ObjectReference walk = Piece(Alias_BillieWalk)
	bool done = false
	If seized
		SwitchOn(Alias_CargoSeized)
		SwitchOff(Alias_CargoAtCut)
		MoveBillie(akRiver, Alias_BillieWalk)
		If SeenOn(seized) && SeenOff(aboard)
			done = akRiver.FinishSale(seized, aboard, walk)
		EndIf
	EndIf
	Refresh()
	If !done
		Debug.Trace("TLM_NM: the sale is paid and was not seen finished; it is not recorded and stays begun. Use Dole, a control or the mail car again. Nothing is paid again.", 2)
		ShowBox(NoteSalePending)
		Return
	EndIf
	If akRiver.IsBillieReleased()
		ShowBox(NoteSold)
	Else
		ShowBox(NoteSoldNoBillie)
	EndIf
EndFunction

; ------------------------------------------------------------------ his death

Function Retreat(ReferenceAlias akWho, ReferenceAlias akWhere)
	{One of the Black Rail who lives is taken out of the fight and set at his retreat marker.}
	Actor who = akWho.GetActorReference()
	ObjectReference where = Piece(akWhere)
	If who && where
		If !who.IsDead() && !who.IsDisabled()
			who.StopCombat()
			who.MoveTo(where)
		EndIf
	EndIf
EndFunction

Function CarryOutDefeat(TLM:MQ02AQuest akRiver, bool abInAUse)
	{Dole is dead in the unsettled encounter. The Black Rail go up the hill,
	shown as each of them out of the fight at a retreat marker; and only when
	each is seen dead or there is the encounter "Dole defeated".}
	Retreat(Alias_Rifle1, Alias_Retreat1)
	Retreat(Alias_Rifle2, Alias_Retreat2)
	Retreat(Alias_Rifle3, Alias_Retreat3)
	bool done = akRiver.FinishDefeat(Piece(Alias_Retreat1), Piece(Alias_Retreat2), Piece(Alias_Retreat3))
	Refresh()
	If !done
		Debug.Trace("TLM_NM: Dole is dead and the Black Rail are not all seen out of the fight; the defeat is not recorded yet. Use a control at the Cut again.", 2)
		If abInAUse
			ShowBox(NoteSceneFailed)
		EndIf
	ElseIf abInAUse
		ShowBox(NoteDefeat)
	Else
		Notice(NoteDefeat)
	EndIf
EndFunction

; =================================================================== evidence

Function LookAtPlate(TLM:MQ02AQuest akRiver)
	{The collection plate, looked into. Open to anybody, whoever lives.}
	If ShowBox(NotePlate) != 0
		Return
	EndIf
	If akRiver.RoadOpen()
		akRiver.LearnSilver(NM_HOW_SEEN)
	EndIf
EndFunction

Function ReadHymnal(TLM:MQ02AQuest akRiver)
	{The flyleaf, read through. Then the book itself goes with the player, once.}
	If !ReadPages(FlyleafPage1, FlyleafPage2, FlyleafPage3, FlyleafPage4)
		Return
	EndIf
	If akRiver.LearnName(NM_HOW_SEEN)
		akRiver.GiveHymnal()
	EndIf
EndFunction

Function LookAtCargo(TLM:MQ02AQuest akRiver)
	int mail = akRiver.Mail()
	If mail == NM_MAIL_DELIVERED
		ShowBox(LabelCargoDelivered)
	ElseIf mail == NM_MAIL_RETAINED
		ShowBox(LabelCargoRetained)
	ElseIf mail == NM_MAIL_SEIZED
		ShowBox(LabelCargoSeized)
	Else
		ShowBox(LabelCargoAboard)
	EndIf
EndFunction

Function LookAtEngine(TLM:MQ02AQuest akRiver)
	If akRiver.Engine() == NM_ENGINE_DAMAGED
		ShowBox(LabelEngineDamaged)
	Else
		ShowBox(LabelEngineSound)
	EndIf
EndFunction

; ============================================================== the rail report

int Function OfferReport(Actor akSheriff)
	{Called by TLM:Act1Walk, inside its own claim on Pritchard's conversation,
	when he is activated after the chapter. Three things may be due, in this
	order: the report of the road (once it is complete), the stamp (if it was
	taken for him and is in the player's hands now), and the yard's change
	(if he has the stamp and it has not been shown). What became of this
	activation:
	NW_REPORT_NONE    nothing was due: nothing was shown and the conversation goes on;
	NW_REPORT_GIVEN   something that was due was done;
	NW_REPORT_LATER   everything offered was explicitly left for later, by its
	                  second button: the conversation goes on;
	NW_REPORT_CLOSED  something was shown and came back with no button a
	                  person can press, or by then Pritchard, the player or
	                  the road was not as it needed. Nothing more is shown in
	                  this conversation.}
	TLM:MQ02AQuest river = Road()
	Actor player = Game.GetPlayer()
	If !river || !akSheriff || !player || akSheriff.IsDead() || akSheriff.IsInCombat() || player.IsDead()
		Return NW_REPORT_NONE
	EndIf
	If !river.GetStageDone(10)
		Return NW_REPORT_NONE
	EndIf
	; A handover that was asked for before and not seen then: looked at now. Nothing is moved.
	river.HandoverSeen()
	bool any = false
	If river.ReportDue()
		int pick = -1
		bool known = river.KnowsSilver()
		If known
			pick = ShowBox(SayReportKnown)
		Else
			pick = ShowBox(SayReportUnknown)
		EndIf
		If !StillHere(akSheriff, player) || !river.ReportDue() || river.KnowsSilver() != known
			Return NW_REPORT_CLOSED
		EndIf
		If pick == 0
			If !river.GiveReport()
				Return NW_REPORT_CLOSED
			EndIf
			any = true
			If !TellReport(river, akSheriff, player)
				Return NW_REPORT_CLOSED
			EndIf
		ElseIf pick != 1
			Return NW_REPORT_CLOSED
		EndIf
	EndIf
	If river.CanHandOver()
		If !StillHere(akSheriff, player)
			Return NW_REPORT_CLOSED
		EndIf
		int mark = river.StampMark()
		int hand = ShowBox(AskHandOver)
		If !StillHere(akSheriff, player) || river.StampMark() != mark || !river.CanHandOver()
			Return NW_REPORT_CLOSED
		EndIf
		If hand == 0
			If !river.HandOver()
				ShowBox(NoteHandoverFailed)
				Return NW_REPORT_CLOSED
			EndIf
			any = true
			int received = ShowBox(NoteStampDelivered)
			If received != 0 || !StillHere(akSheriff, player)
				Return NW_REPORT_CLOSED
			EndIf
		ElseIf hand != 1
			Return NW_REPORT_CLOSED
		EndIf
	EndIf
	If river.AuthorityDue()
		If !StillHere(akSheriff, player)
			Return NW_REPORT_CLOSED
		EndIf
		If !river.BeginAuthority()
			Return NW_REPORT_CLOSED
		EndIf
		int shown = CarryOutAuthority(river, akSheriff)
		If shown == NW_SHOWN_UNSEEN
			; The stamp is his. The yard's change could not be shown, and is tried again when he is next spoken to.
			ShowBox(NoteAuthorityFailed)
			Return NW_REPORT_CLOSED
		ElseIf shown != NW_SHOWN_DONE
			; Shown, and its notice not answered: nothing more in this conversation.
			Return NW_REPORT_CLOSED
		EndIf
		any = true
	EndIf
	If any
		Return NW_REPORT_GIVEN
	EndIf
	If river.ReportDue() || river.CanHandOver()
		Return NW_REPORT_LATER
	EndIf
	Return NW_REPORT_NONE
EndFunction

bool Function StillHere(Actor akSheriff, Actor akPlayer)
	Return !akSheriff.IsDead() && !akSheriff.IsDisabled() && !akSheriff.IsInCombat() && !akPlayer.IsDead()
EndFunction

bool Function TellReport(TLM:MQ02AQuest akRiver, Actor akSheriff, Actor akPlayer)
	{What is reported is what the road holds, said by this build and not put in his mouth.}
	int mark = akRiver.RoadMark()
	int mail = akRiver.Mail()
	If mail == NM_MAIL_DELIVERED
		If !ReportPage(akRiver, akSheriff, akPlayer, ReportMailDelivered, mark)
			Return false
		EndIf
	ElseIf mail == NM_MAIL_RETAINED
		If !ReportPage(akRiver, akSheriff, akPlayer, ReportMailRetained, mark)
			Return false
		EndIf
	ElseIf mail == NM_MAIL_SEIZED
		If !ReportPage(akRiver, akSheriff, akPlayer, ReportMailSeized, mark)
			Return false
		EndIf
	Else
		If !ReportPage(akRiver, akSheriff, akPlayer, ReportMailAboard, mark)
			Return false
		EndIf
	EndIf
	int course = akRiver.Outcome()
	If course == NM_RUN
		If !ReportPage(akRiver, akSheriff, akPlayer, ReportRan, mark)
			Return false
		EndIf
	ElseIf course == NM_SOLD
		If !ReportPage(akRiver, akSheriff, akPlayer, ReportSold, mark)
			Return false
		EndIf
	ElseIf course == NM_BACKED
		If !ReportPage(akRiver, akSheriff, akPlayer, ReportBacked, mark)
			Return false
		EndIf
	ElseIf akRiver.DoleFate() == NM_DOLE_BY_PLAYER
		If !ReportPage(akRiver, akSheriff, akPlayer, ReportDoleByYou, mark)
			Return false
		EndIf
	Else
		If !ReportPage(akRiver, akSheriff, akPlayer, ReportDoleDead, mark)
			Return false
		EndIf
	EndIf
	bool silver = akRiver.KnowsSilver()
	bool name = akRiver.KnowsName()
	If silver && name
		If !ReportPage(akRiver, akSheriff, akPlayer, ReportKnowBoth, mark)
			Return false
		EndIf
	ElseIf silver
		If !ReportPage(akRiver, akSheriff, akPlayer, ReportKnowSilver, mark)
			Return false
		EndIf
	ElseIf name
		If !ReportPage(akRiver, akSheriff, akPlayer, ReportKnowName, mark)
			Return false
		EndIf
	Else
		If !ReportPage(akRiver, akSheriff, akPlayer, ReportKnowNeither, mark)
			Return false
		EndIf
	EndIf
	If !ReportPage(akRiver, akSheriff, akPlayer, ReportEnd, mark)
		Return false
	EndIf
	Return true
EndFunction

bool Function ReportPage(TLM:MQ02AQuest akRiver, Actor akSheriff, Actor akPlayer, Message akPage, int aiMark)
	{Only an exact Continue under the same current participants permits another page or offer.}
	If !StillHere(akSheriff, akPlayer) || !akRiver.GetStageDone(100) || akRiver.RoadMark() != aiMark
		Return false
	EndIf
	int pick = ShowBox(akPage)
	Return pick == 0 && StillHere(akSheriff, akPlayer) && akRiver.GetStageDone(100) && akRiver.RoadMark() == aiMark
EndFunction
