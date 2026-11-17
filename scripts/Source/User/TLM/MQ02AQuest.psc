Scriptname TLM:MQ02AQuest extends Quest
{The Night Mail (NIGHT-MAIL-STORY-001): the rules of the Iron Junction road.

Everything this road remembers is written here and nowhere else: its stages,
the facts later chapters read, and what is pending. It shows no box: the
greybox (TLM:NightMailWalk) shows them and calls in here, and Pritchard's
conversation in TLM:Act1Walk does the same for the report.

Rules, from the contract and its order:
  - asking for a scene is not its having happened. A scene is begun (its
    intent written), then carried out by the greybox, then LOOKED AT, and
    only then recorded. What is not seen stays pending under its own claim;
  - run, Dole defeated, sold and backed out exclude one another. Killing Dole
    delivers nothing: the mail is carried forward or back afterwards, and
    the outcome stays "Dole defeated";
  - nobody dead, gone or fighting speaks, countersigns, is paid or receives
    anything, and no action asks for anybody it does not need;
  - silver, the name, the stamp found, the stamp held, the decision about it
    and Pritchard having it are separate facts. Hearing is not holding;
  - every one-time thing is asked for once and fails closed.

A CANDIDATE: not compiled, not built against the game's master, not run in
the game.}

Group MainQuest
	Quest Property TLM_MQ01 Auto Const Mandatory
	{Read only.}
	GlobalVariable Property TLM_G_MQ01_Done Auto Const Mandatory
	{Read only.}
	ReferenceAlias Property Alias_MercySheriff Auto Const
	{SheriffPritchard of TLM_MQ01: whoever the first section cast as Owen
	Pritchard. Read, and handed the stamp; never moved or put into an alias.}
EndGroup

Group SideQuest
	GlobalVariable Property TLM_G_SQ01_Outcome Auto Const Mandatory
	{Read only: 5 is "sold to Vane".}
	GlobalVariable Property TLM_G_SQ01_YardAlerted Auto Const Mandatory
	{Read only: set by the reported outcome alone.}
EndGroup

Group Cast
	ReferenceAlias Property Alias_Lockridge Auto Const Mandatory
	ReferenceAlias Property Alias_Billie Auto Const Mandatory
	ReferenceAlias Property Alias_Dole Auto Const Mandatory
	ReferenceAlias Property Alias_Rifle1 Auto Const
	ReferenceAlias Property Alias_Rifle2 Auto Const
	ReferenceAlias Property Alias_Rifle3 Auto Const
EndGroup

Group Facts
	GlobalVariable Property TLM_G_MQ02A_Outcome Auto Const Mandatory
	GlobalVariable Property TLM_G_MQ02A_Mail Auto Const Mandatory
	GlobalVariable Property TLM_G_MQ02A_Engine Auto Const Mandatory
	GlobalVariable Property TLM_G_MQ02A_Train Auto Const Mandatory
	GlobalVariable Property TLM_G_MQ02A_Dole Auto Const Mandatory
	GlobalVariable Property TLM_G_MQ02A_Stamp Auto Const Mandatory
	GlobalVariable Property TLM_G_MQ02A_StampDelivered Auto Const Mandatory
	GlobalVariable Property TLM_G_MQ02A_YardAuthority Auto Const Mandatory
	GlobalVariable Property TLM_G_MQ02A_Reported Auto Const Mandatory
	GlobalVariable Property TLM_G_MQ02A_MailThrough Auto Const Mandatory
	GlobalVariable Property TLM_G_MQ02A_MailSold Auto Const Mandatory
	GlobalVariable Property TLM_G_MQ02A_LineClosed Auto Const Mandatory
	GlobalVariable Property TLM_G_MQ02A_DoleLives Auto Const Mandatory
	GlobalVariable Property TLM_G_MQ02A_SilverRail Auto Const Mandatory
	GlobalVariable Property TLM_G_MQ02A_OstranderKnown Auto Const Mandatory
	GlobalVariable Property TLM_G_MQ02A_LockridgeStamping Auto Const Mandatory
	GlobalVariable Property TLM_G_MQ02A_LockridgeSigned Auto Const Mandatory
	GlobalVariable Property TLM_G_MQ02A_LockridgeReported Auto Const Mandatory
EndGroup

Group Forms
	Form Property Caps Auto Const
	{Caps001 from Fallout4.esm. None if it was not found: no share can be paid, and none is offered.}
	Form Property HymnalBook Auto Const Mandatory
	{TLM_BOOK_HymnalFlyleaf}
	Form Property StampItem Auto Const Mandatory
	{TLM_MISC_OstranderStamp}
EndGroup

; ----------------------------------------------------------------- constants
; The same numbers as tools/logic_model/night_mail_model.py; a test compares them.

; TLM_G_MQ02A_Outcome, and Claim.
int NM_NONE = 0 Const
int NM_RUN = 41 Const
int NM_DEFEAT = 42 Const
int NM_SOLD = 43 Const
int NM_BACKED = 44 Const

; TLM_G_MQ02A_Mail.
int NM_MAIL_ABOARD = 0 Const
int NM_MAIL_DELIVERED = 1 Const
int NM_MAIL_RETAINED = 2 Const
int NM_MAIL_SEIZED = 3 Const

; TLM_G_MQ02A_Engine.
int NM_ENGINE_SOUND = 0 Const
int NM_ENGINE_DAMAGED = 1 Const

; TLM_G_MQ02A_Train: where Old Contrary stands.
int NM_TRAIN_YARD = 0 Const
int NM_TRAIN_CUT = 1 Const
int NM_TRAIN_PLATFORM = 2 Const
int NM_TRAIN_TAKEN = 3 Const

; TLM_G_MQ02A_Dole.
int NM_DOLE_ALIVE = 0 Const
int NM_DOLE_BY_PLAYER = 1 Const
int NM_DOLE_OTHERWISE = 2 Const

; TLM_G_MQ02A_Stamp: what was decided about the stamp.
int NM_STAMP_NONE = 0 Const
int NM_STAMP_KEPT = 61 Const
int NM_STAMP_SIGNED = 62 Const
int NM_STAMP_TAKEN = 63 Const

; TLM_G_MQ02A_YardAuthority.
int NM_YARD_HELD = 0 Const
int NM_YARD_WITHDRAWN = 1 Const
int NM_YARD_VACANT = 2 Const

; ScenePending: a scene of the train or the encounter, begun and not yet seen finished.
int NM_SCENE_NONE = 0 Const
int NM_SCENE_DEPART = 1 Const
int NM_SCENE_RUN = 2 Const
int NM_SCENE_FORWARD = 3 Const
int NM_SCENE_REVERSE = 4 Const
int NM_SCENE_RETURN = 5 Const
int NM_SCENE_SALE = 6 Const
int NM_SCENE_DEFEAT = 7 Const

; YardPending: a scene of the yard, independent of the mail.
int NM_YARD_NONE = 0 Const
int NM_YARD_COUNTERSIGN = 1 Const
int NM_YARD_AUTHORITY = 2 Const

; What the departure control can begin.
int NM_GO_NONE = 0 Const
int NM_GO_DEPART = 1 Const
int NM_GO_REJOIN = 2 Const

; What the regulator and the reverser can begin at the Cut.
int NM_AT_NOTHING = 0 Const
int NM_AT_OPEN = 1 Const
int NM_AT_CLEAR = 2 Const

; How something was learned.
int NM_HOW_SEEN = 1 Const
int NM_HOW_TOLD = 2 Const

; Which gate greeting is Lockridge's.
int NM_GREET_NONE = 0 Const
int NM_GREET_GATE = 1 Const
int NM_GREET_ALERTED = 2 Const
int NM_GREET_SOLD = 3 Const

; TLM_G_SQ01_Outcome's "sold to Vane" (TLM:SQ01Quest, SQ_SOLD). Read, never written.
int NM_SQ01_SOLD = 5 Const

; The accepted grant on Dole's share. No wider economy value is claimed.
int NM_SHARE_CAPS = 150 Const

; How long an item is looked for after it was asked for: ten looks, a tenth of a second apart.
int NM_ACK_POLLS = 10 Const
; How far from a marker the player sent to it may stand and be at it: a zone's arrival spot, with room to
; have taken a step. The zones' arrival spots are further apart than this.
float NM_REACH = 512.0 Const
; How far from a spot one of the cast sent to it may stand and have gone there. Billie's two spots in the
; Cut are some 350 apart, so the player's reach would take her footplate for the walk home.
float NM_STAND = 128.0 Const

; ------------------------------------------------------------------- state
; Kept by a save as they are. Nothing sets them back.

; The encounter's course that can no longer be exchanged for another: 0, or
; NM_RUN, NM_DEFEAT, NM_SOLD, NM_BACKED from the moment it is begun.
int Claim = 0
int ScenePending = 0
int YardPending = 0
bool BillieDrives = false
bool DefeatByPlayer = false
bool DoleMet = false
bool DoleFaced = false
bool SharePending = false
bool SharePaid = false
bool BillieReleased = false
bool BillieReported = false
bool SilverSeen = false
bool SilverTold = false
bool NameRead = false
bool NameTold = false
bool HymnalPending = false
bool HymnalGiven = false
bool HymnalShown = false
bool StampPending = false
bool StampGiven = false
bool HandoverPending = false

Event OnStageSet(int auiStageID, int auiItemID)
	; One line per stage event in the game's script log, as TLM_MQ01 writes.
	Debug.Trace("TLM_MQ02A: stage " + auiStageID + " item " + auiItemID)
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
	{Alive, present and in no fight: can say a line, be paid, countersign, receive something.}
	Actor who = Person(akAlias)
	If !who
		Return false
	EndIf
	Return !who.IsDead() && !who.IsDisabled() && !who.IsInCombat()
EndFunction

bool Function SeenDead(ReferenceAlias akAlias)
	{Seen dead. Somebody who is not there at all is not seen dead.}
	Actor who = Person(akAlias)
	If !who
		Return false
	EndIf
	Return who.IsDead()
EndFunction

bool Function PlayerIsAlive()
	Actor player = Game.GetPlayer()
	If !player
		Return false
	EndIf
	Return !player.IsDead()
EndFunction

bool Function LockridgeCanSpeak()
	Return CanSpeak(Alias_Lockridge)
EndFunction

bool Function LockridgeIsDead()
	Return SeenDead(Alias_Lockridge)
EndFunction

bool Function BillieCanSpeak()
	Return CanSpeak(Alias_Billie)
EndFunction

bool Function BillieIsThere()
	Return IsThere(Alias_Billie)
EndFunction

bool Function DoleCanSpeak()
	Return CanSpeak(Alias_Dole)
EndFunction

bool Function DoleIsThere()
	Return IsThere(Alias_Dole)
EndFunction

bool Function DoleIsDead()
	Return SeenDead(Alias_Dole)
EndFunction

bool Function SheriffCanReceive()
	{Owen Pritchard, alive, present and in no fight, wherever the first section put him.}
	Return CanSpeak(Alias_MercySheriff)
EndFunction

bool Function AnybodyDead()
	{Somebody of this road is seen dead: a named person or one of the Black Rail.}
	Return SeenDead(Alias_Lockridge) || SeenDead(Alias_Billie) || SeenDead(Alias_Dole) || SeenDead(Alias_Rifle1) || SeenDead(Alias_Rifle2) || SeenDead(Alias_Rifle3)
EndFunction

; ================================================================ what stands

bool Function RoadOpen()
	{The road was begun, its quest is running, and the player is alive.}
	Return IsRunning() && GetStageDone(10) && PlayerIsAlive()
EndFunction

bool Function Assigned()
	{The job was given by Lockridge (20), or taken on at the footplate with nobody to give it (21).}
	Return GetStageDone(20) || GetStageDone(21)
EndFunction

int Function Outcome()
	Return TLM_G_MQ02A_Outcome.GetValueInt()
EndFunction

int Function Mail()
	Return TLM_G_MQ02A_Mail.GetValueInt()
EndFunction

int Function Engine()
	Return TLM_G_MQ02A_Engine.GetValueInt()
EndFunction

int Function Train()
	Return TLM_G_MQ02A_Train.GetValueInt()
EndFunction

int Function DoleFate()
	{What is known of Dole's death. A man found dead whose death was not heard of is dead otherwise.}
	int fate = TLM_G_MQ02A_Dole.GetValueInt()
	If fate == NM_DOLE_ALIVE && SeenDead(Alias_Dole)
		Return NM_DOLE_OTHERWISE
	EndIf
	Return fate
EndFunction

int Function StampDecision()
	Return TLM_G_MQ02A_Stamp.GetValueInt()
EndFunction

bool Function IsStampDelivered()
	Return TLM_G_MQ02A_StampDelivered.GetValueInt() == 1
EndFunction

int Function YardAuthority()
	Return TLM_G_MQ02A_YardAuthority.GetValueInt()
EndFunction

bool Function IsReported()
	Return TLM_G_MQ02A_Reported.GetValueInt() == 1
EndFunction

bool Function Unsettled()
	{No course of the encounter has been taken and none is under way.}
	Return Claim == NM_NONE
EndFunction

int Function Pending()
	{The train's or the encounter's scene that was begun and is not yet seen finished.}
	Return ScenePending
EndFunction

int Function PendingAtYard()
	Return YardPending
EndFunction

int Function Mark()
	{The road's exclusive state as one number: the course claimed and recorded,
	the mail, the train, what is pending, whether the road is complete. Read
	before a box and again after it: two readings that differ mean that
	something was begun, settled or ended while the box was open, and what the
	box offered is stale. Nobody's life is in it: each action asks for the
	people it needs itself.}
	int sum = Claim + 100 * Outcome() + 10000 * Mail() + 100000 * Train() + 1000000 * ScenePending + 10000000 * YardPending
	If GetStageDone(100)
		sum += 100000000
	EndIf
	Return sum
EndFunction

int Function StampMark()
	{The same for the stamp: what was decided, whether it is being taken, whether it is delivered.}
	int sum = StampDecision()
	If StampPending
		sum += 100
	EndIf
	If IsStampDelivered()
		sum += 200
	EndIf
	If GetStageDone(60)
		sum += 400
	EndIf
	Return sum
EndFunction

bool Function IsDoleMet()
	Return DoleMet
EndFunction

bool Function IsDoleFaced()
	Return DoleFaced
EndFunction

bool Function IsSharePaid()
	Return SharePaid
EndFunction

bool Function IsBillieReleased()
	Return BillieReleased
EndFunction

bool Function IsBillieReported()
	Return BillieReported
EndFunction

bool Function KnowsSilver()
	Return TLM_G_MQ02A_SilverRail.GetValueInt() == 1
EndFunction

bool Function KnowsName()
	Return TLM_G_MQ02A_OstranderKnown.GetValueInt() == 1
EndFunction

bool Function IsHymnalShown()
	Return HymnalShown
EndFunction

bool Function LockridgeDispatches()
	{She still runs the yard: its authority was not withdrawn and she is not dead.}
	Return YardAuthority() == NM_YARD_HELD
EndFunction

bool Function CanComplete()
	{One course of the encounter was carried through and seen, and no scene of the train is half done.}
	Return Outcome() != NM_NONE && ScenePending == NM_SCENE_NONE
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
	{An outcome is recorded: the Cut is no longer asked for, and leaving is.}
	FinishObjective(40)
	RetireObjective(20)
	If Outcome() == NM_DEFEAT && Mail() == NM_MAIL_ABOARD
		ShowObjective(70)
	EndIf
	ShowObjective(80)
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
		Debug.Trace("TLM_MQ02A: its quest is not running and could not be started (Start returned " + started + ", running " + running + "); nothing was changed", 2)
		Return false
	EndIf
	Return true
EndFunction

bool Function SeenAt(ObjectReference akWho, ObjectReference akWhere)
	{That reference is in that marker's cell, within reach of it. The marker's own 3D is not asked for.}
	If !akWho || !akWhere
		Return false
	EndIf
	If akWho.GetParentCell() != akWhere.GetParentCell()
		Return false
	EndIf
	Return akWho.GetDistance(akWhere) <= NM_REACH
EndFunction

bool Function StandsAt(ObjectReference akWho, ObjectReference akWhere)
	{One of the cast is at the spot they were sent to: the same cell, and close.}
	If !akWho || !akWhere
		Return false
	EndIf
	If akWho.GetParentCell() != akWhere.GetParentCell()
		Return false
	EndIf
	Return akWho.GetDistance(akWhere) <= NM_STAND
EndFunction

bool Function IsOn(ObjectReference akPiece)
	If !akPiece
		Return false
	EndIf
	Return !akPiece.IsDisabled()
EndFunction

bool Function IsOff(ObjectReference akPiece)
	{Switched off. A piece that is not placed at all is not showing anything either.}
	If !akPiece
		Return true
	EndIf
	Return akPiece.IsDisabled()
EndFunction

bool Function ArriveAtYard(ObjectReference akGate)
	{The player is SEEN at the yard's gate marker. A journey asked for is not an arrival.}
	If !IsRunning() || !PlayerIsAlive()
		Return false
	EndIf
	If !SeenAt(Game.GetPlayer(), akGate)
		Return false
	EndIf
	If !GetStageDone(10)
		SetStage(10)
		ShowObjective(10)
	EndIf
	Return true
EndFunction

; ---------------------------------------------------------------- the yard job

int Function Greeting()
	{Which of Lockridge's three gate greetings is hers to give: none unless the
	player is at the gate with no job taken and no course begun. The two that
	depend on the side quest read what it recorded: the yard was alerted by its
	REPORTED outcome; "sold" is its sold outcome. Neither is written here.}
	If !RoadOpen() || Assigned() || Claim != NM_NONE || Outcome() != NM_NONE || !LockridgeDispatches()
		Return NM_GREET_NONE
	EndIf
	If TLM_G_SQ01_YardAlerted.GetValueInt() == 1
		Return NM_GREET_ALERTED
	EndIf
	If TLM_G_SQ01_Outcome.GetValueInt() == NM_SQ01_SOLD
		Return NM_GREET_SOLD
	EndIf
	Return NM_GREET_GATE
EndFunction

bool Function AcceptJob()
	{"I'll ride your mail.", and her answer to it delivered: Lockridge alive, present and in no fight.}
	If !RoadOpen() || Assigned() || !CanSpeak(Alias_Lockridge) || !LockridgeDispatches()
		Return false
	EndIf
	If Claim != NM_NONE || Outcome() != NM_NONE
		Return false
	EndIf
	SetStage(20)
	FinishObjective(10)
	ShowObjective(20)
	Return true
EndFunction

bool Function BoardUnassigned()
	{The labelled "Board the Night Mail": the job taken on at the footplate when
	nobody at the yard can give it (Lockridge dead, gone, fighting, or no
	longer dispatching). No conversation with her is claimed.}
	If !RoadOpen() || Assigned()
		Return false
	EndIf
	If CanSpeak(Alias_Lockridge) && LockridgeDispatches()
		Return false
	EndIf
	If Claim != NM_NONE || Outcome() != NM_NONE
		Return false
	EndIf
	SetStage(21)
	RetireObjective(10)
	ShowObjective(20)
	Return true
EndFunction

; ------------------------------------------------------------------ departure

int Function GoOffered()
	{What the departure control can begin now. NM_GO_DEPART: the Night Mail
	leaves the yard for the Cut (the job taken, the train in the yard with
	its mail, nothing begun). NM_GO_REJOIN: the train stands in the Cut and
	the player walks the line back to it. Reads only.}
	If !RoadOpen()
		Return NM_GO_NONE
	EndIf
	If ScenePending == NM_SCENE_DEPART
		Return NM_GO_DEPART
	EndIf
	If ScenePending != NM_SCENE_NONE
		Return NM_GO_NONE
	EndIf
	If Train() == NM_TRAIN_CUT
		Return NM_GO_REJOIN
	EndIf
	If Assigned() && Train() == NM_TRAIN_YARD && Mail() == NM_MAIL_ABOARD && Claim == NM_NONE && Outcome() == NM_NONE
		Return NM_GO_DEPART
	EndIf
	Return NM_GO_NONE
EndFunction

bool Function BeginDepart()
	{The departure, confirmed on the footplate. Stage 30 with Billie alive and
	present to drive, 31 without her. Nothing is arrived at by this.}
	If GoOffered() != NM_GO_DEPART
		Return false
	EndIf
	bool drives = IsThere(Alias_Billie)
	; No call into the game between this test and the claim.
	If ScenePending == NM_SCENE_DEPART
		Return true
	EndIf
	If ScenePending != NM_SCENE_NONE
		Return false
	EndIf
	ScenePending = NM_SCENE_DEPART
	If drives
		If !GetStageDone(30) && !GetStageDone(31)
			SetStage(30)
		EndIf
	ElseIf !GetStageDone(30) && !GetStageDone(31)
		SetStage(31)
	EndIf
	FinishObjective(20)
	Return true
EndFunction

bool Function FinishDepart(ObjectReference akCutMarker, ObjectReference akLanterns)
	{The player is SEEN on the footplate where it stands in the Cut, and the
	lanterns and the spread rail are SEEN there. Only then is the train in the
	Cut (stage 40).}
	If !IsRunning() || !PlayerIsAlive()
		Return false
	EndIf
	If !SeenAt(Game.GetPlayer(), akCutMarker) || !IsOn(akLanterns)
		Debug.Trace("TLM_MQ02A: the arrival in the Cut is not recorded: the player or the lanterns are not seen there. The departure stays pending", 2)
		Return false
	EndIf
	; No call into the game between this test and the claim.
	If ScenePending != NM_SCENE_DEPART
		Return false
	EndIf
	ScenePending = NM_SCENE_NONE
	TLM_G_MQ02A_Train.SetValueInt(NM_TRAIN_CUT)
	If !GetStageDone(40)
		SetStage(40)
		ShowObjective(40)
		ShowObjective(55)
	EndIf
	Return true
EndFunction

; ------------------------------------------------------------------ the Cut

bool Function AtTheCut()
	{The train stands in the Cut with the encounter there.}
	Return GetStageDone(40) && Train() == NM_TRAIN_CUT
EndFunction

int Function TrainOffered()
	{What the regulator and the reverser can begin at the Cut. NM_AT_OPEN: the
	encounter is unsettled, so the run or the reverse. NM_AT_CLEAR: Dole is
	defeated and the mail still aboard, so forward or back. Reads only.}
	If !RoadOpen() || !AtTheCut() || ScenePending != NM_SCENE_NONE || Mail() != NM_MAIL_ABOARD
		Return NM_AT_NOTHING
	EndIf
	If Outcome() == NM_NONE && Claim == NM_NONE
		Return NM_AT_OPEN
	EndIf
	If Outcome() == NM_DEFEAT
		Return NM_AT_CLEAR
	EndIf
	Return NM_AT_NOTHING
EndFunction

bool Function MeetDole()
	{His sermon was delivered: he has seen the player's face.}
	If !RoadOpen() || !CanSpeak(Alias_Dole)
		Return false
	EndIf
	DoleMet = true
	Return true
EndFunction

bool Function FaceDole()
	{"Stand aside" was said and his answer delivered: the player chose the fight.}
	If !RoadOpen() || !AtTheCut() || !IsThere(Alias_Dole)
		Return false
	EndIf
	DoleFaced = true
	Return true
EndFunction

; ---------------------------------------------------------------------- the run

bool Function BeginRun()
	{"Stoke her. Run the gap.", confirmed. The course is claimed; nothing has arrived.}
	If TrainOffered() != NM_AT_OPEN
		Return false
	EndIf
	bool drives = CanSpeak(Alias_Billie)
	; No call into the game between this test and the claim.
	If Claim != NM_NONE || ScenePending != NM_SCENE_NONE
		Return false
	EndIf
	Claim = NM_RUN
	ScenePending = NM_SCENE_RUN
	BillieDrives = drives
	Return true
EndFunction

bool Function FinishRun(ObjectReference akPlatform, ObjectReference akDelivered, ObjectReference akAboard, ObjectReference akDamaged)
	{The run is SEEN finished: the player at the platform, the cargo there and
	no longer aboard, the engine damaged. Only then did the mail get through.}
	If !IsRunning() || !PlayerIsAlive()
		Return false
	EndIf
	If !SeenAt(Game.GetPlayer(), akPlatform) || !IsOn(akDelivered) || !IsOff(akAboard) || !IsOn(akDamaged)
		Debug.Trace("TLM_MQ02A: the run is not recorded: the player, the delivered cargo or the damaged engine is not seen at the platform. The run stays pending", 2)
		Return false
	EndIf
	bool lives = IsThere(Alias_Dole)
	; No call into the game between this test and the claim.
	If Claim != NM_RUN || ScenePending != NM_SCENE_RUN
		Return false
	EndIf
	ScenePending = NM_SCENE_NONE
	TLM_G_MQ02A_Outcome.SetValueInt(NM_RUN)
	TLM_G_MQ02A_Mail.SetValueInt(NM_MAIL_DELIVERED)
	TLM_G_MQ02A_MailThrough.SetValueInt(1)
	TLM_G_MQ02A_Engine.SetValueInt(NM_ENGINE_DAMAGED)
	TLM_G_MQ02A_Train.SetValueInt(NM_TRAIN_PLATFORM)
	If lives
		; He watched the engine go past him.
		TLM_G_MQ02A_DoleLives.SetValueInt(1)
	EndIf
	If BillieDrives
		SetStage(41)
	Else
		SetStage(46)
	EndIf
	CourseTaken()
	Return true
EndFunction

; ------------------------------------------------------------------ the reverse

bool Function BeginReverse()
	{"Back her out.", confirmed.}
	If TrainOffered() != NM_AT_OPEN
		Return false
	EndIf
	bool drives = CanSpeak(Alias_Billie)
	; No call into the game between this test and the claim.
	If Claim != NM_NONE || ScenePending != NM_SCENE_NONE
		Return false
	EndIf
	Claim = NM_BACKED
	ScenePending = NM_SCENE_REVERSE
	BillieDrives = drives
	Return true
EndFunction

bool Function FinishReverse(ObjectReference akYard, ObjectReference akRetained, ObjectReference akAboard)
	{The reverse is SEEN finished: the player back at the yard, the cargo
	locked up there and no longer aboard. The mail is withheld and the line shut.}
	If !IsRunning() || !PlayerIsAlive()
		Return false
	EndIf
	If !SeenAt(Game.GetPlayer(), akYard) || !IsOn(akRetained) || !IsOff(akAboard)
		Debug.Trace("TLM_MQ02A: the reverse is not recorded: the player or the retained cargo is not seen at the yard. It stays pending", 2)
		Return false
	EndIf
	bool lives = IsThere(Alias_Dole)
	; No call into the game between this test and the claim.
	If Claim != NM_BACKED || ScenePending != NM_SCENE_REVERSE
		Return false
	EndIf
	ScenePending = NM_SCENE_NONE
	TLM_G_MQ02A_Outcome.SetValueInt(NM_BACKED)
	TLM_G_MQ02A_Mail.SetValueInt(NM_MAIL_RETAINED)
	TLM_G_MQ02A_LineClosed.SetValueInt(1)
	TLM_G_MQ02A_Train.SetValueInt(NM_TRAIN_YARD)
	If lives && DoleMet
		TLM_G_MQ02A_DoleLives.SetValueInt(1)
	EndIf
	If BillieDrives
		SetStage(44)
	Else
		SetStage(49)
	EndIf
	CourseTaken()
	Return true
EndFunction

; ---------------------------------------------------------------------- the sale

bool Function ShareOffered()
	{Dole's share can still be taken: the encounter unsettled, the mail aboard
	in the Cut, Dole alive, present and in no fight, never paid and never asked for.}
	If TrainOffered() != NM_AT_OPEN || !CanSpeak(Alias_Dole)
		Return false
	EndIf
	Return !SharePaid && !SharePending && Caps != None
EndFunction

bool Function TakeShare()
	{"Done." One hundred and fifty caps, once. The sale is claimed and paid;
	it is not finished until FinishSale sees the rest.}
	If !ShareOffered()
		Return false
	EndIf
	Actor player = Game.GetPlayer()
	int before = player.GetItemCount(Caps)
	; No call into the game between this test and the claim.
	If Claim != NM_NONE || ScenePending != NM_SCENE_NONE || SharePending || SharePaid
		Return false
	EndIf
	Claim = NM_SOLD
	ScenePending = NM_SCENE_SALE
	SharePending = true
	player.AddItem(Caps, NM_SHARE_CAPS, false)
	; Asked once. Then only looked at, for a second at the most.
	int polls = 0
	While polls < NM_ACK_POLLS && player.GetItemCount(Caps) < before + NM_SHARE_CAPS
		Utility.Wait(0.1)
		polls += 1
	EndWhile
	If player.GetItemCount(Caps) < before + NM_SHARE_CAPS
		; Fails closed: the deal is off, nothing is recorded as paid, and it is never asked for again.
		Claim = NM_NONE
		ScenePending = NM_SCENE_NONE
		Debug.Trace("TLM_MQ02A: FAIL CLOSED: the share was asked for once and the caps did not arrive (had " + before + ", have " + player.GetItemCount(Caps) + "). The deal is off; it is not offered or asked for again. SharePending stays set. Report this line.", 2)
		Return false
	EndIf
	SharePaid = true
	SharePending = false
	Return true
EndFunction

bool Function FinishSale(ObjectReference akSeized, ObjectReference akAboard, ObjectReference akWalk)
	{The sale is SEEN finished: the cargo taken off the train, and Billie, if
	she lives, safe at her walking marker and in no fight. Paid is paid: this
	is asked again as often as it takes and never pays twice.}
	If !IsRunning()
		Return false
	EndIf
	If !IsOn(akSeized) || !IsOff(akAboard)
		Debug.Trace("TLM_MQ02A: the sale is not recorded: the cargo is not seen taken from the train. It stays pending, paid", 2)
		Return false
	EndIf
	Actor billie = Person(Alias_Billie)
	bool released = false
	If billie
		If !billie.IsDead()
			If billie.IsDisabled() || billie.IsInCombat() || !StandsAt(billie, akWalk)
				Debug.Trace("TLM_MQ02A: the sale is not recorded: Billie Tupper lives and is not seen safe at her walking marker. It stays pending, paid", 2)
				Return false
			EndIf
			released = true
		EndIf
	EndIf
	bool lives = IsThere(Alias_Dole)
	; No call into the game between this test and the claim.
	If Claim != NM_SOLD || ScenePending != NM_SCENE_SALE || !SharePaid
		Return false
	EndIf
	ScenePending = NM_SCENE_NONE
	BillieReleased = released
	TLM_G_MQ02A_Outcome.SetValueInt(NM_SOLD)
	TLM_G_MQ02A_Mail.SetValueInt(NM_MAIL_SEIZED)
	TLM_G_MQ02A_MailSold.SetValueInt(1)
	TLM_G_MQ02A_Train.SetValueInt(NM_TRAIN_TAKEN)
	If lives
		TLM_G_MQ02A_DoleLives.SetValueInt(1)
	EndIf
	If released
		SetStage(43)
	Else
		SetStage(48)
	EndIf
	CourseTaken()
	Return true
EndFunction

; ------------------------------------------------------------------ Dole's death

Function DoleDied(bool abByPlayer)
	{Heard from his alias, or found by the greybox. In the unsettled encounter
	it claims the course "Dole defeated", which is recorded once the Black Rail
	are seen out of the fight (FinishDefeat). After another course was begun
	or recorded it changes nothing of that course: he is dead, and that is all.}
	Actor dole = Person(Alias_Dole)
	bool dead = false
	If dole
		dead = dole.IsDead()
	EndIf
	bool here = AtTheCut()
	int fate = TLM_G_MQ02A_Dole.GetValueInt()
	int course = Outcome()
	bool noted = GetStageDone(42) || GetStageDone(47)
	If !dead || fate != NM_DOLE_ALIVE
		Return
	EndIf
	; No call into the game between this test and the claim.
	If here && Claim == NM_NONE && course == NM_NONE
		Claim = NM_DEFEAT
		ScenePending = NM_SCENE_DEFEAT
		DefeatByPlayer = abByPlayer
		TLM_G_MQ02A_DoleLives.SetValueInt(0)
		If abByPlayer
			TLM_G_MQ02A_Dole.SetValueInt(NM_DOLE_BY_PLAYER)
		Else
			TLM_G_MQ02A_Dole.SetValueInt(NM_DOLE_OTHERWISE)
		EndIf
		Return
	EndIf
	; Not this encounter's outcome: no kill is credited as one, whoever made it.
	TLM_G_MQ02A_DoleLives.SetValueInt(0)
	TLM_G_MQ02A_Dole.SetValueInt(NM_DOLE_OTHERWISE)
	If !noted
		SetStage(47)
	EndIf
EndFunction

bool Function RifleOut(ReferenceAlias akAlias, ObjectReference akRetreat)
	{One of the Black Rail is out of it: dead, not there, or in no fight at his retreat marker.}
	Actor who = Person(akAlias)
	If !who
		Return true
	EndIf
	If who.IsDead() || who.IsDisabled()
		Return true
	EndIf
	Return !who.IsInCombat() && StandsAt(who, akRetreat)
EndFunction

bool Function FinishDefeat(ObjectReference akRetreat1, ObjectReference akRetreat2, ObjectReference akRetreat3)
	{Dole is dead and each of the Black Rail is SEEN dead or gone up the hill.
	Only then is the encounter "Dole defeated". The mail is where it was.}
	If !IsRunning()
		Return false
	EndIf
	If !SeenDead(Alias_Dole)
		Return false
	EndIf
	If !RifleOut(Alias_Rifle1, akRetreat1) || !RifleOut(Alias_Rifle2, akRetreat2) || !RifleOut(Alias_Rifle3, akRetreat3)
		Return false
	EndIf
	; No call into the game between this test and the claim.
	If Claim != NM_DEFEAT || ScenePending != NM_SCENE_DEFEAT
		Return false
	EndIf
	ScenePending = NM_SCENE_NONE
	TLM_G_MQ02A_Outcome.SetValueInt(NM_DEFEAT)
	If DefeatByPlayer
		SetStage(42)
	Else
		SetStage(47)
	EndIf
	CourseTaken()
	Return true
EndFunction

; ---------------------------------------------------- the mail after the defeat

bool Function BeginForward()
	{The line is clear and the regulator is opened: the mail goes through. The outcome stays "Dole defeated".}
	If TrainOffered() != NM_AT_CLEAR
		Return false
	EndIf
	bool drives = CanSpeak(Alias_Billie)
	If ScenePending != NM_SCENE_NONE
		Return false
	EndIf
	ScenePending = NM_SCENE_FORWARD
	BillieDrives = drives
	Return true
EndFunction

bool Function FinishForward(ObjectReference akPlatform, ObjectReference akDelivered, ObjectReference akAboard, ObjectReference akSound)
	If !IsRunning() || !PlayerIsAlive()
		Return false
	EndIf
	If !SeenAt(Game.GetPlayer(), akPlatform) || !IsOn(akDelivered) || !IsOff(akAboard) || !IsOn(akSound)
		Debug.Trace("TLM_MQ02A: the delivery is not recorded: the player, the delivered cargo or the engine is not seen at the platform. It stays pending", 2)
		Return false
	EndIf
	; No call into the game between this test and the claim.
	If ScenePending != NM_SCENE_FORWARD
		Return false
	EndIf
	ScenePending = NM_SCENE_NONE
	TLM_G_MQ02A_Mail.SetValueInt(NM_MAIL_DELIVERED)
	TLM_G_MQ02A_MailThrough.SetValueInt(1)
	TLM_G_MQ02A_Train.SetValueInt(NM_TRAIN_PLATFORM)
	FinishObjective(70)
	Return true
EndFunction

bool Function BeginCarryBack()
	{The line is clear and the train is taken back to the yard with its cargo. Not a back-out: nothing is shut.}
	If TrainOffered() != NM_AT_CLEAR
		Return false
	EndIf
	bool drives = CanSpeak(Alias_Billie)
	If ScenePending != NM_SCENE_NONE
		Return false
	EndIf
	ScenePending = NM_SCENE_RETURN
	BillieDrives = drives
	Return true
EndFunction

bool Function FinishCarryBack(ObjectReference akYard, ObjectReference akRetained, ObjectReference akAboard)
	If !IsRunning() || !PlayerIsAlive()
		Return false
	EndIf
	If !SeenAt(Game.GetPlayer(), akYard) || !IsOn(akRetained) || !IsOff(akAboard)
		Debug.Trace("TLM_MQ02A: the return is not recorded: the player or the retained cargo is not seen at the yard. It stays pending", 2)
		Return false
	EndIf
	; No call into the game between this test and the claim.
	If ScenePending != NM_SCENE_RETURN
		Return false
	EndIf
	ScenePending = NM_SCENE_NONE
	TLM_G_MQ02A_Mail.SetValueInt(NM_MAIL_RETAINED)
	TLM_G_MQ02A_Train.SetValueInt(NM_TRAIN_YARD)
	FinishObjective(70)
	Return true
EndFunction

bool Function DidBillieDrive()
	{She was at the regulator, alive, present and in no fight, when the last scene of the train was begun.}
	Return BillieDrives
EndFunction

; ------------------------------------------------------------------- evidence

bool Function LearnSilver(int aiHow)
	{NM_HOW_SEEN: the collection plate was looked into. NM_HOW_TOLD: Dole said
	it, and is alive, present and in no fight to have said it. Two ways, two
	journal entries; the knowledge is one.}
	If !RoadOpen()
		Return false
	EndIf
	If aiHow == NM_HOW_SEEN
		SilverSeen = true
		If !GetStageDone(50)
			SetStage(50)
		EndIf
	ElseIf aiHow == NM_HOW_TOLD
		If !CanSpeak(Alias_Dole)
			Return false
		EndIf
		SilverTold = true
		If !GetStageDone(51)
			SetStage(51)
		EndIf
	Else
		Return false
	EndIf
	TLM_G_MQ02A_SilverRail.SetValueInt(1)
	Return true
EndFunction

bool Function LearnName(int aiHow)
	{NM_HOW_SEEN: the flyleaf was read through. NM_HOW_TOLD: Dole named himself.
	Being told gives no book and reads none.}
	If !RoadOpen()
		Return false
	EndIf
	If aiHow == NM_HOW_SEEN
		NameRead = true
		If !GetStageDone(55)
			SetStage(55)
		EndIf
	ElseIf aiHow == NM_HOW_TOLD
		If !CanSpeak(Alias_Dole)
			Return false
		EndIf
		NameTold = true
		If !GetStageDone(56)
			SetStage(56)
		EndIf
	Else
		Return false
	EndIf
	TLM_G_MQ02A_OstranderKnown.SetValueInt(1)
	Return true
EndFunction

bool Function GiveOne(Form akWhat)
	{One of something into the player's inventory, seen to have arrived.}
	Actor player = Game.GetPlayer()
	int before = player.GetItemCount(akWhat)
	player.AddItem(akWhat, 1, false)
	int polls = 0
	While polls < NM_ACK_POLLS && player.GetItemCount(akWhat) <= before
		Utility.Wait(0.1)
		polls += 1
	EndWhile
	Return player.GetItemCount(akWhat) > before
EndFunction

bool Function GiveHymnal()
	{The hymnal, its flyleaf read through, goes with the player: once.}
	If !RoadOpen() || !NameRead
		Return false
	EndIf
	If HymnalGiven || HymnalPending
		Return false
	EndIf
	HymnalPending = true
	If GiveOne(HymnalBook)
		HymnalGiven = true
		HymnalPending = false
		Return true
	EndIf
	Debug.Trace("TLM_MQ02A: FAIL CLOSED: the hymnal was asked for once and is not in the inventory. It is not asked for again. What was read is still known. Report this line.", 2)
	Return false
EndFunction

bool Function HoldsHymnal()
	{The book itself is in the player's inventory now.}
	Actor player = Game.GetPlayer()
	If !player
		Return false
	EndIf
	Return player.GetItemCount(HymnalBook) > 0
EndFunction

bool Function CanShowHymnal()
	{The real book in hand, Lockridge alive, present and in no fight, Dole alive,
	nothing yet decided about the stamp, and not shown before.}
	If !RoadOpen() || HymnalShown || !HoldsHymnal() || !CanSpeak(Alias_Lockridge) || !LockridgeDispatches()
		Return false
	EndIf
	If SeenDead(Alias_Dole) || Person(Alias_Dole) == None
		Return false
	EndIf
	Return StampDecision() == NM_STAMP_NONE && !StampPending && YardPending == NM_YARD_NONE
EndFunction

bool Function ShowHymnal()
	{Her answer to the book was delivered.}
	If !CanShowHymnal()
		Return false
	EndIf
	HymnalShown = true
	Return true
EndFunction

; ------------------------------------------------------------------- the stamp

bool Function FindStamp()
	{The drawer was opened and looked into.}
	If !RoadOpen()
		Return false
	EndIf
	If !GetStageDone(60)
		SetStage(60)
		FinishObjective(55)
	EndIf
	Return true
EndFunction

bool Function StampUndecided()
	{Found, and nothing decided or being decided about it.}
	Return GetStageDone(60) && StampDecision() == NM_STAMP_NONE && !StampPending && YardPending == NM_YARD_NONE
EndFunction

bool Function HoldsStamp()
	{The stamp itself is in the player's inventory now.}
	Actor player = Game.GetPlayer()
	If !player
		Return false
	EndIf
	Return player.GetItemCount(StampItem) > 0
EndFunction

bool Function KeepStamping(ObjectReference akInDrawer)
	{"Keep stamping. Trains have to run." Lockridge alive, present, in no fight
	and still running the yard; the stamp SEEN still in her drawer.}
	If !RoadOpen() || !StampUndecided() || !CanSpeak(Alias_Lockridge) || !LockridgeDispatches()
		Return false
	EndIf
	If !IsOn(akInDrawer) || HoldsStamp()
		Return false
	EndIf
	; No call into the game between this test and the claim.
	If StampPending || YardPending != NM_YARD_NONE
		Return false
	EndIf
	TLM_G_MQ02A_Stamp.SetValueInt(NM_STAMP_KEPT)
	TLM_G_MQ02A_LockridgeStamping.SetValueInt(1)
	SetStage(61)
	Return true
EndFunction

bool Function BeginCountersign(ObjectReference akInDrawer)
	{"Sign your own name from now on.", confirmed. Nothing is signed by this.}
	If !RoadOpen() || !StampUndecided() || !CanSpeak(Alias_Lockridge) || !LockridgeDispatches()
		Return false
	EndIf
	If !IsOn(akInDrawer) || HoldsStamp()
		Return false
	EndIf
	; No call into the game between this test and the claim.
	If StampPending || YardPending != NM_YARD_NONE
		Return false
	EndIf
	YardPending = NM_YARD_COUNTERSIGN
	Return true
EndFunction

bool Function FinishCountersign(ObjectReference akSigned, ObjectReference akStamped, ObjectReference akHeld)
	{The countersigning is SEEN: the board shows her own name and no longer the
	inspector's, the suspect stock stands held, and she is alive and present
	to have done it.}
	If !IsRunning()
		Return false
	EndIf
	If !IsOn(akSigned) || !IsOff(akStamped) || !IsOn(akHeld) || !IsThere(Alias_Lockridge)
		Debug.Trace("TLM_MQ02A: the countersigning is not recorded: the board, the held stock or Lockridge is not seen as it needs. It stays pending", 2)
		Return false
	EndIf
	; No call into the game between this test and the claim.
	If YardPending != NM_YARD_COUNTERSIGN
		Return false
	EndIf
	YardPending = NM_YARD_NONE
	TLM_G_MQ02A_Stamp.SetValueInt(NM_STAMP_SIGNED)
	TLM_G_MQ02A_LockridgeSigned.SetValueInt(1)
	SetStage(62)
	Return true
EndFunction

bool Function TakeStamp(ObjectReference akInDrawer)
	{"Pritchard gets the stamp." The stamp, seen in the drawer, is asked into
	the player's inventory once. It is not yet recorded taken.}
	If !RoadOpen() || !StampUndecided() || !IsOn(akInDrawer)
		Return false
	EndIf
	If StampGiven
		Return false
	EndIf
	; No call into the game between this test and the claim.
	If StampPending || YardPending != NM_YARD_NONE
		Return false
	EndIf
	StampPending = true
	If GiveOne(StampItem)
		StampGiven = true
		Return true
	EndIf
	Debug.Trace("TLM_MQ02A: FAIL CLOSED: the stamp was asked for once and is not in the inventory. It is not asked for again, and nothing else is decided about it. Report this line.", 2)
	Return false
EndFunction

bool Function ConfirmStampTaken(ObjectReference akInDrawer)
	{The taking is SEEN: the stamp was given and the drawer no longer shows it.
	Stage 63 if Lockridge is alive, present and in no fight to watch; 64 if not.
	This is custody, not delivery.}
	If !IsRunning()
		Return false
	EndIf
	If !IsOff(akInDrawer)
		Return false
	EndIf
	bool watched = CanSpeak(Alias_Lockridge)
	; No call into the game between this test and the claim.
	If !StampPending || !StampGiven || StampDecision() != NM_STAMP_NONE
		Return false
	EndIf
	StampPending = false
	TLM_G_MQ02A_Stamp.SetValueInt(NM_STAMP_TAKEN)
	If watched
		SetStage(63)
	Else
		SetStage(64)
	EndIf
	ShowObjective(90)
	Return true
EndFunction

bool Function IsStampBeingTaken()
	{Given to the player and not yet seen gone from the drawer.}
	Return StampPending && StampGiven
EndFunction

bool Function CanHandOver()
	{The stamp was taken for the report, is in the player's hands now, is not
	yet delivered, and Pritchard is alive, present and in no fight to take it.}
	Return StampDecision() == NM_STAMP_TAKEN && !IsStampDelivered() && HoldsStamp() && SheriffCanReceive()
EndFunction

bool Function HandOver()
	{The stamp passes from the player to Pritchard. Recorded only if it is
	SEEN to have left the one and reached the other. A move cannot make a
	second stamp, so an unseen handover may be asked again.}
	If !CanHandOver() || !PlayerIsAlive()
		Return false
	EndIf
	Actor player = Game.GetPlayer()
	Actor sheriff = Person(Alias_MercySheriff)
	int mine = player.GetItemCount(StampItem)
	int his = sheriff.GetItemCount(StampItem)
	HandoverPending = true
	player.RemoveItem(StampItem, 1, true, sheriff)
	int polls = 0
	While polls < NM_ACK_POLLS && (player.GetItemCount(StampItem) >= mine || sheriff.GetItemCount(StampItem) <= his)
		Utility.Wait(0.1)
		polls += 1
	EndWhile
	If player.GetItemCount(StampItem) >= mine || sheriff.GetItemCount(StampItem) <= his
		Debug.Trace("TLM_MQ02A: the stamp was handed over and is not seen with Pritchard (the player has " + player.GetItemCount(StampItem) + ", he has " + sheriff.GetItemCount(StampItem) + "); it is not recorded delivered", 2)
		Return false
	EndIf
	HandoverPending = false
	TLM_G_MQ02A_StampDelivered.SetValueInt(1)
	FinishObjective(90)
	Return true
EndFunction

bool Function HandoverSeen()
	{A handover that was asked and not seen at the time: if Pritchard is now
	seen to hold the stamp, it was delivered. Nothing is moved by this.}
	If IsStampDelivered()
		Return true
	EndIf
	If !HandoverPending || StampDecision() != NM_STAMP_TAKEN
		Return false
	EndIf
	Actor sheriff = Person(Alias_MercySheriff)
	If !sheriff
		Return false
	EndIf
	If sheriff.GetItemCount(StampItem) < 1
		Return false
	EndIf
	HandoverPending = false
	TLM_G_MQ02A_StampDelivered.SetValueInt(1)
	FinishObjective(90)
	Return true
EndFunction

; ------------------------------------------------------- the yard's authority

bool Function AuthorityDue()
	{Pritchard has the stamp and the yard is not yet shown without a master.}
	Return IsStampDelivered() && YardAuthority() == NM_YARD_HELD
EndFunction

bool Function BeginAuthority()
	If !AuthorityDue()
		Return false
	EndIf
	If YardPending == NM_YARD_AUTHORITY
		Return true
	EndIf
	If YardPending != NM_YARD_NONE
		Return false
	EndIf
	YardPending = NM_YARD_AUTHORITY
	Return true
EndFunction

bool Function FinishAuthority(ObjectReference akClosed, ObjectReference akStamped, ObjectReference akSigned)
	{The yard is SEEN without a master: its dispatch board closed, and neither
	of the boards that passed cars showing. With Lockridge alive that is her
	authority withdrawn; with Lockridge dead it is a yard left vacant, which
	is a different fact and is recorded as one. Only now, with the stamp
	delivered, is lockridge_reported true.}
	If !IsRunning()
		Return false
	EndIf
	If !IsOn(akClosed) || !IsOff(akStamped) || !IsOff(akSigned)
		Debug.Trace("TLM_MQ02A: the yard's change is not recorded: its closed board is not seen, or another board still shows. The stamp stays delivered; this stays pending", 2)
		Return false
	EndIf
	bool dead = SeenDead(Alias_Lockridge)
	; No call into the game between this test and the claim.
	If YardPending != NM_YARD_AUTHORITY || !IsStampDelivered() || YardAuthority() != NM_YARD_HELD
		Return false
	EndIf
	YardPending = NM_YARD_NONE
	If dead
		TLM_G_MQ02A_YardAuthority.SetValueInt(NM_YARD_VACANT)
	Else
		TLM_G_MQ02A_YardAuthority.SetValueInt(NM_YARD_WITHDRAWN)
	EndIf
	TLM_G_MQ02A_LockridgeReported.SetValueInt(1)
	Return true
EndFunction

; --------------------------------------------------- Billie's return and report

bool Function BillieReportDue()
	{After a sale in which Billie was put off alive: her walk home and what she
	told the yardmaster have not been shown yet, and both are alive to show it.}
	If Outcome() != NM_SOLD || !BillieReleased || BillieReported
		Return false
	EndIf
	Return IsThere(Alias_Billie) && CanSpeak(Alias_Lockridge) && LockridgeDispatches()
EndFunction

bool Function FinishBillieReport(ObjectReference akYardSpot)
	{The scene was shown and Billie is SEEN alive at the yard, in no fight.}
	If !BillieReportDue()
		Return false
	EndIf
	Actor billie = Person(Alias_Billie)
	If billie.IsInCombat() || !StandsAt(billie, akYardSpot)
		Return false
	EndIf
	BillieReported = true
	Return true
EndFunction

; ------------------------------------------------------------------- leaving

bool Function Complete()
	{The player has left for Mercy with one course of the encounter carried through.}
	If !IsRunning() || !CanComplete()
		Return false
	EndIf
	If !GetStageDone(100)
		FinishObjective(80)
		RetireObjective(70)
		SetStage(100)
	EndIf
	Return true
EndFunction

bool Function ReportDue()
	Return GetStageDone(100) && !IsReported()
EndFunction

bool Function GiveReport()
	{Pritchard was told what became of the Night Mail.}
	If !GetStageDone(100)
		Return false
	EndIf
	TLM_G_MQ02A_Reported.SetValueInt(1)
	Return true
EndFunction

Function TraceState()
	{One line in the script log. From the console: cqf TLM_MQ02A TraceState}
	Debug.Trace("TLM_MQ02A: outcome=" + Outcome() + " claim=" + Claim + " scene=" + ScenePending + " yardScene=" + YardPending + " mail=" + Mail() + " engine=" + Engine() + " train=" + Train() + " dole=" + DoleFate() + " doleMet=" + DoleMet + " doleFaced=" + DoleFaced + " sharePaid=" + SharePaid + " sharePending=" + SharePending + " billieDrives=" + BillieDrives + " billieReleased=" + BillieReleased + " billieReported=" + BillieReported + " silver=" + KnowsSilver() + " name=" + KnowsName() + " stamp=" + StampDecision() + " stampPending=" + StampPending + " stampGiven=" + StampGiven + " delivered=" + IsStampDelivered() + " yard=" + YardAuthority() + " complete=" + GetStageDone(100) + " reported=" + IsReported())
EndFunction
