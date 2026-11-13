Scriptname TLM:MQ01Quest extends Quest
{TLM_MQ01 "Six Rounds to Mercy". Owns all quest logic.

COMPILES. RAN IN THE GAME on 2026-11-12 in the development self-test, with
nobody at the keyboard (docs/design/VERIFY_LOG.md):
- by stages alone, every alias empty (scenario 1);
- with actors and markers made at run time in its aliases: the rows of the
  test matrix that need no built place, save or dialogue, 28 cases, compared
  with the logic model after every event (scenarios 101 to 128), and six
  hand-written cases before that (scenarios 4 to 9);
- with the guards of amendment A24 (ClaimEncounter, WaitForResolutions,
  LeadIsDown, ResolveUnattended and the counting at the top of OnStageSet):
  four cases that do two things at once (scenarios 129 to 132). The guard
  was seen to act in three of them. That was commit c1e6d48, which
  carries the tag mq01-logic-proof.
Every stage handler has run, and each left the state the logic model
predicts. In those runs a stage number stood in for every trigger, pickup
and conversation, and EvadeTimerElapsed was called directly. NOT run: the
90-second timer itself, the move to the caravan yard over a distance,
OnGameLoaded, dialogue, saving and loading, and anything in a built place.
Written without Fallout 4 or the Creation Kit.
This version, with the rule of amendment A25 (PlayerIsTalkingToLead: the
evade timer does not run out on a conversation with the Cutter lead) and two
lines that say in the script log what held the timer back, compiled and ran
on 2026-11-13: all 62 scenarios passed. In that run the question A25 asks
was only ever answered "no". A25 HAS NOT BEEN SEEN AT WORK: that needs a
conversation, and there is no dialogue yet.

Design: stages are the API. Anything that changes the quest sets a stage
(default scripts, dialogue, the console), and OnStageSet applies the effect.
There are no CK-generated stage fragments. The rules implemented here are the
ones proven in tools/logic_model (same function names where possible).}

; ---------------------------------------------------------------- properties

Group Globals
	GlobalVariable Property TLM_G_CaravanOutcome Auto Const Mandatory
	{0 none, 1 saved, 2 evaded, 3 exploited, 4 missed}
	GlobalVariable Property TLM_G_CaravanMethod Auto Const Mandatory
	{0 none, 1 deal, 2 betrayal (player killed a caravan hand)}
	GlobalVariable Property TLM_G_CaravanAliveAtMercy Auto Const Mandatory
	{1 if Nell Fenwick is alive when the dispatch is delivered}
	GlobalVariable Property TLM_G_Rep_MercyCrossing Auto Const Mandatory
	GlobalVariable Property TLM_G_MQ01_Done Auto Const Mandatory
	GlobalVariable Property TLM_G_MQ01_DebriefVariant Auto Const Mandatory
	{1 saved, 2 evaded, 3 witness, 4 no witness, 5 missed, 6 lost}
	GlobalVariable Property TLM_G_MQ01_DebriefAnswer Auto Const Mandatory
	{0 none, 1 admit, 2 deny, 3 confess, 4 blame, 5 "she's lying", 9 silent}
	GlobalVariable Property TLM_Truth Auto Const Mandatory
	GlobalVariable Property TLM_Accountability Auto Const Mandatory
	GlobalVariable Property TLM_MutualTrust Auto Const Mandatory
EndGroup

Group Aliases
	ReferenceAlias Property Alias_CaravanMaster Auto Const Mandatory
	ReferenceAlias Property Alias_CaravanDrover Auto Const Mandatory
	ReferenceAlias Property Alias_CaravanMasterInTown Auto Const Mandatory
	{Empty until stage 40. Flagged Essential in the plugin.}
	ReferenceAlias Property Alias_CaravanDroverInTown Auto Const Mandatory
	{Empty until stage 40. Flagged Essential in the plugin.}
	ReferenceAlias Property Alias_CutterLead Auto Const Mandatory
	ReferenceAlias Property Alias_CutterA Auto Const Mandatory
	ReferenceAlias Property Alias_CutterB Auto Const Mandatory
	ReferenceAlias Property Alias_CutterC Auto Const Mandatory
	ReferenceAlias Property Alias_Wagon Auto Const Mandatory
	ReferenceAlias Property Alias_AmbushCenter Auto Const Mandatory
	ReferenceAlias Property Alias_AmbushEnableMarker Auto Const Mandatory
	{Enable parent of the ambush actors. Disabled until stage 10.}
	ReferenceAlias Property Alias_WreckStart Auto Const Mandatory
	ReferenceAlias Property Alias_CaravanYard Auto Const Mandatory
EndGroup

Group Forms
	Form Property DispatchItem Auto Const Mandatory
	{TLM_MISC_Dispatch}
	Form Property TornTransitPass Auto Const
	{Optional. TLM_MISC_TornTransitPass (design question Q6).}
	Form Property CargoShare Auto Const
	{Optional. What the player receives for the deal.}
	Faction Property TLM_Fac_Cutters Auto Const Mandatory
	Quest Property TLM_SQ01 Auto Const
	{Optional. Started silently at stage 10 so its clue scripts are live.}
	Message Property TutWake Auto Const
	Message Property TutSixRounds Auto Const
	Message Property TutDispatch Auto Const
EndGroup

Group Tuning
	float Property EvadeSeconds = 90.0 Auto Const
	{Starting value only. Tune in playtest.}
	float Property EvadeDistance = 4000.0 Auto Const
	{Starting value only. Tune in playtest.}
	bool Property MovePlayerOnStart = true Auto Const
	{False when the player is already placed (dev start by coc).}
EndGroup

; ----------------------------------------------------------------- constants

int TIMER_EVADE = 1 Const

int OUT_NONE = 0 Const
int OUT_SAVED = 1 Const
int OUT_EVADED = 2 Const
int OUT_EXPLOITED = 3 Const
int OUT_MISSED = 4 Const

int METHOD_DEAL = 1 Const
int METHOD_BETRAYAL = 2 Const

int V_SAVED = 1 Const
int V_EVADED = 2 Const
int V_WITNESS = 3 Const
int V_NOWITNESS = 4 Const
int V_MISSED = 5 Const
int V_LOST = 6 Const

int ANS_ADMIT = 1 Const
int ANS_DENY = 2 Const
int ANS_CONFESS = 3 Const
int ANS_BLAME = 4 Const
int ANS_LYING = 5 Const
int ANS_SILENT = 9 Const

; The only mutable script state. Not authoritative: stages and globals are.
int handsKilledByPlayer = 0
; Development aid, read through StageEventsHandled().
int handledCount = 0

; Handlers on different threads (amendment A24). The game runs each event on
; a thread of its own, and a handler gives other threads a turn at every call
; it makes into the game. A resolution of the encounter (stages 31 to 35) is
; many such calls: it stops the fight, kills, loots. These three keep two
; handlers from tripping over each other.
; Resolution handlers that have begun and not finished.
int resolutionsAtWork = 0
; Resolution handlers that have begun, ever. A stage reads as done before its
; handler has begun, so "more stages set than handlers begun" means one is
; still to come.
int resolutionsBegun = 0
; A first resolution has gone ahead. Only one may.
bool encounterClaimed = false

; ------------------------------------------------------------ stage dispatch

Event OnStageSet(int auiStageID, int auiItemID)
	bool resolution = auiStageID >= 31 && auiStageID <= 35
	If resolution
		; Counted before anything here calls into the game, so that no other
		; thread finds a resolution's stage set and nobody at work on it.
		resolutionsBegun += 1
		resolutionsAtWork += 1
	EndIf
	; One line per stage event in the game's script log. Without it, "the
	; event never arrived" and "the handler ran and did nothing" look the same.
	Debug.Trace("TLM_MQ01: stage " + auiStageID + " item " + auiItemID)
	If auiStageID == 10
		ApplyStart()
	ElseIf auiStageID == 15
		ShowHint(TutSixRounds)
	ElseIf auiStageID == 20
		ApplyDispatchTaken()
	ElseIf auiStageID == 30
		ApplyLive()
	ElseIf auiStageID == 31
		ApplySaved()
	ElseIf auiStageID == 32
		ApplyEvaded()
	ElseIf auiStageID == 33
		ApplyDeal()
	ElseIf auiStageID == 34
		ApplyMissed()
	ElseIf auiStageID == 35
		ApplyBetrayal()
	ElseIf auiStageID == 37
		TurnCuttersOnPlayer()
	ElseIf auiStageID == 40
		ApplyTown()
	ElseIf auiStageID == 50
		ApplyDelivered()
	ElseIf auiStageID == 51
		ApplyDebriefAnswer(ANS_ADMIT)
	ElseIf auiStageID == 52
		ApplyDebriefAnswer(ANS_DENY)
	ElseIf auiStageID == 53
		ApplyDebriefAnswer(ANS_CONFESS)
	ElseIf auiStageID == 54
		ApplyDebriefAnswer(ANS_BLAME)
	ElseIf auiStageID == 55
		ApplyDebriefAnswer(ANS_LYING)
	ElseIf auiStageID == 60
		ApplyDebriefDone()
	ElseIf auiStageID == 900
		Recover()
	EndIf
	If resolution
		resolutionsAtWork -= 1
	EndIf
	handledCount += 1
EndEvent

; ------------------------------------------------- handlers on other threads

bool Function ClaimEncounter()
	{True for the one first resolution that may go ahead. Nothing between the
	test and the claim calls into the game, so two threads cannot both pass.}
	If encounterClaimed
		Return false
	EndIf
	encounterClaimed = true
	Return true
EndFunction

int Function ResolutionStagesSet()
	int n = 0
	If GetStageDone(31)
		n += 1
	EndIf
	If GetStageDone(32)
		n += 1
	EndIf
	If GetStageDone(33)
		n += 1
	EndIf
	If GetStageDone(34)
		n += 1
	EndIf
	If GetStageDone(35)
		n += 1
	EndIf
	Return n
EndFunction

Function WaitForResolutions(int aiMine)
	{Comes back when no resolution of the encounter is half done on another
	thread: none whose handler is at work, and none whose stage is set while
	its handler has yet to begin. aiMine is 1 when the caller is itself a
	resolution's handler, otherwise 0. Never waits longer than five seconds.

	The count of handlers at work is read last, with no call into the game
	after it. Read first, a handler could begin during the calls that follow
	and be missed: no longer "yet to begin", and not counted as at work.}
	int tries = 0
	While tries < 50 && ((Outcome() == OUT_NONE && ResolutionStagesSet() > resolutionsBegun) || resolutionsAtWork > aiMine)
		Utility.Wait(0.1)
		tries += 1
	EndWhile
	If tries > 0
		; For the test runs: the only sign that this guard did something.
		Debug.Trace("TLM_MQ01: A24 waited " + tries + " tenths of a second for another resolution to finish")
	EndIf
EndFunction

bool Function LeadIsDown()
	{The Cutter lead is there and dead. He is Protected, so only the player can
	have killed him; and his death is announced when he has finished dying, a
	moment after he is dead.}
	Actor a = Alias_CutterLead.GetActorReference()
	Return a && a.IsDead()
EndFunction

Function ResolveUnattended()
	{The ambush is live and the player is not going to settle it: the timer
	has run out, or the player has left or reached town. If the Cutter lead is
	already dead this is a rescue whose news has not arrived yet, not an
	evasion.}
	If LeadIsDown()
		; For the test runs: the only sign that this guard did something.
		Debug.Trace("TLM_MQ01: A24 the Cutter lead is already dead: a rescue, not an evasion")
		SetStage(31)
	Else
		SetStage(32)
	EndIf
EndFunction

int Function StageEventsHandled()
	{Development aid for the self-test: how many stage events this script has
	finished handling.}
	Return handledCount
EndFunction

; ------------------------------------------------------------ state helpers

int Function Outcome()
	Return TLM_G_CaravanOutcome.GetValueInt()
EndFunction

bool Function IsArmed()
	{The ambush exists and the player has not met it.}
	Return GetStageDone(10) && !GetStageDone(30) && Outcome() == OUT_NONE
EndFunction

bool Function IsLive()
	{The ambush is under way and nothing has resolved it.}
	Return GetStageDone(30) && Outcome() == OUT_NONE
EndFunction

bool Function IsAliveAlias(ReferenceAlias akAlias)
	Actor a = akAlias.GetActorReference()
	Return a && !a.IsDead()
EndFunction

; ------------------------------------------------------------------ stage 10

Function ApplyStart()
	Actor player = Game.GetPlayer()
	ObjectReference startMarker = Alias_WreckStart.GetReference()
	If MovePlayerOnStart && startMarker
		player.MoveTo(startMarker)
	EndIf
	If TornTransitPass
		player.AddItem(TornTransitPass, 1, true)
	EndIf
	ObjectReference enableMarker = Alias_AmbushEnableMarker.GetReference()
	If enableMarker
		enableMarker.Enable()
	EndIf
	SetObjectiveDisplayed(10)
	If TLM_SQ01 && !TLM_SQ01.GetStageDone(5)
		TLM_SQ01.SetStage(5)
	EndIf
	ShowHint(TutWake)
EndFunction

Function ShowHint(Message akHint)
	If akHint
		akHint.Show()
	EndIf
EndFunction

; ------------------------------------------------------------------ stage 20

Function ApplyDispatchTaken()
	SetObjectiveCompleted(10)
	SetObjectiveDisplayed(20)
	ShowHint(TutDispatch)
EndFunction

; ---------------------------------------------------------- caravan encounter

Function PlayerEngaged()
	{Called by a Cutter alias when the player becomes its combat target.}
	If IsArmed()
		SetStage(30)
	EndIf
EndFunction

Function ApplyLive()
	ArmEvadeWatch()
EndFunction

Function ArmEvadeWatch()
	{Also called after a load: timer and distance registrations are re-armed
	rather than trusted to survive the save.}
	StartTimer(EvadeSeconds, TIMER_EVADE)
	ObjectReference center = Alias_AmbushCenter.GetReference()
	If center
		RegisterForDistanceGreaterThanEvent(Game.GetPlayer(), center, EvadeDistance)
	EndIf
EndFunction

Event OnTimer(int aiTimerID)
	If aiTimerID == TIMER_EVADE
		EvadeTimerElapsed()
	EndIf
EndEvent

bool Function PlayerIsTalkingToLead()
	{The hold-up conversation with the Cutter lead is open (amendment A25).
	Asked of the game each time rather than kept as a flag, so that nothing
	needs putting right after a load, or after a conversation that ends in a
	way nobody planned for.
	NOT SEEN TRUE IN THE GAME: there is no dialogue yet. Whether it reads true
	for the whole of a conversation, the player's turn to choose included, has
	to be seen once there is one (docs/design/VERIFY_LOG.md).}
	Actor a = Alias_CutterLead.GetActorReference()
	Return a && a.IsInDialogueWithPlayer()
EndFunction

Function EvadeTimerElapsed()
	{The evade timer has run out (the logic model's evade_timer). A function of
	its own so that the development self-test can call it without waiting.}
	If IsLive()
		; Never resolve "evaded" over the top of a fight (A2), or of the
		; conversation with the Cutter lead (A25). Check again later: the timer
		; starts over with its whole length. The two lines written here are for
		; the test runs: the only sign of which of the two held it back.
		If Game.GetPlayer().IsInCombat()
			Debug.Trace("TLM_MQ01: A2 the evade timer ran out during a fight: it starts over")
			StartTimer(EvadeSeconds, TIMER_EVADE)
		ElseIf PlayerIsTalkingToLead()
			Debug.Trace("TLM_MQ01: A25 the evade timer ran out during the conversation with the Cutter lead: it starts over")
			StartTimer(EvadeSeconds, TIMER_EVADE)
		Else
			ResolveUnattended()
		EndIf
	EndIf
EndFunction

Event OnDistanceGreaterThan(ObjectReference akObj1, ObjectReference akObj2, float afDistance)
	; The player has left, fight or no fight.
	If IsLive()
		ResolveUnattended()
	EndIf
EndEvent

Function CutterDown(ReferenceAlias akWhich)
	{Called by a Cutter alias on death. Cutters are Protected, so the killer
	is the player.}
	If Outcome() != OUT_NONE
		Return
	EndIf
	If IsArmed()
		SetStage(30)
	EndIf
	If akWhich == Alias_CutterLead && IsLive()
		SetStage(31)
	EndIf
EndFunction

Function CaravanHandKilledByPlayer(ReferenceAlias akWhich)
	{Called by a caravan hand alias on death when the killer is the player.}
	handsKilledByPlayer += 1
	If GetStageDone(50)
		Return
	EndIf
	If IsArmed()
		SetStage(30)
	EndIf
	If !GetStageDone(35)
		SetStage(35)
	EndIf
EndFunction

Function ApplySaved()
	If Outcome() != OUT_NONE || !ClaimEncounter()
		Return
	EndIf
	TLM_G_CaravanOutcome.SetValueInt(OUT_SAVED)
	EndEncounter()
EndFunction

Function ApplyEvaded()
	If Outcome() != OUT_NONE || !ClaimEncounter()
		Return
	EndIf
	TLM_G_CaravanOutcome.SetValueInt(OUT_EVADED)
	EndEncounter()
	KillByCutters(Alias_CaravanDrover)
	LootWagon()
EndFunction

Function ApplyDeal()
	If Outcome() != OUT_NONE || !ClaimEncounter()
		Return
	EndIf
	TLM_G_CaravanOutcome.SetValueInt(OUT_EXPLOITED)
	TLM_G_CaravanMethod.SetValueInt(METHOD_DEAL)
	EndEncounter()
	KillByCutters(Alias_CaravanDrover)
	LootWagon()
	If CargoShare
		Game.GetPlayer().AddItem(CargoShare, 1)
	EndIf
EndFunction

Function ApplyMissed()
	If Outcome() != OUT_NONE || !ClaimEncounter()
		Return
	EndIf
	TLM_G_CaravanOutcome.SetValueInt(OUT_MISSED)
	EndEncounter()
	KillByCutters(Alias_CaravanDrover)
	LootWagon()
EndFunction

Function ApplyBetrayal()
	{The player killed a caravan hand before the debrief. This always wins,
	even over an earlier Saved or Evaded.}
	; If another resolution is half done on another thread, let it finish:
	; this one then replaces its outcome instead of being overwritten by it.
	WaitForResolutions(1)
	bool firstResolution = (Outcome() == OUT_NONE) && ClaimEncounter()
	If !firstResolution
		; Another resolution claimed the encounter while the outcome was being
		; read just now. It writes its outcome when it gets there; this one
		; has to write after it.
		WaitForResolutions(1)
	EndIf
	TLM_G_CaravanOutcome.SetValueInt(OUT_EXPLOITED)
	TLM_G_CaravanMethod.SetValueInt(METHOD_BETRAYAL)
	If firstResolution
		EndEncounter()
		LootWagon()
		If !IsAliveAlias(Alias_CaravanMaster)
			; Nell is dead and the wagon is overrun: the Cutters finish the drover.
			KillByCutters(Alias_CaravanDrover)
		EndIf
	EndIf
EndFunction

Function TurnCuttersOnPlayer()
	{Stage 37: the speech check failed or the deal was refused.}
	If Outcome() != OUT_NONE
		Return
	EndIf
	If IsArmed()
		SetStage(30)
	EndIf
	TLM_Fac_Cutters.SetPlayerEnemy(true)
	Actor player = Game.GetPlayer()
	StartCombatIfAlive(Alias_CutterLead, player)
	StartCombatIfAlive(Alias_CutterA, player)
	StartCombatIfAlive(Alias_CutterB, player)
	StartCombatIfAlive(Alias_CutterC, player)
EndFunction

Function StartCombatIfAlive(ReferenceAlias akAlias, Actor akTarget)
	Actor a = akAlias.GetActorReference()
	If a && !a.IsDead()
		a.StartCombat(akTarget)
	EndIf
EndFunction

Function EndEncounter()
	CancelTimer(TIMER_EVADE)
	ObjectReference center = Alias_AmbushCenter.GetReference()
	If center
		UnregisterForDistanceEvents(Game.GetPlayer(), center)
	EndIf
	; The Cutters' "withdraw" package is data, conditioned on the outcome
	; global. Here they only need to stop fighting and re-read their packages.
	Alias_CutterLead.TryToStopCombat()
	Alias_CutterA.TryToStopCombat()
	Alias_CutterB.TryToStopCombat()
	Alias_CutterC.TryToStopCombat()
	Alias_CutterLead.TryToEvaluatePackage()
	Alias_CutterA.TryToEvaluatePackage()
	Alias_CutterB.TryToEvaluatePackage()
	Alias_CutterC.TryToEvaluatePackage()
	Alias_CaravanMaster.TryToEvaluatePackage()
	Alias_CaravanDrover.TryToEvaluatePackage()
EndFunction

Function KillByCutters(ReferenceAlias akHand)
	{Deterministic for the logic proof. Staging this as visible AI is a later
	presentation pass.}
	Actor hand = akHand.GetActorReference()
	If !hand || hand.IsDead()
		Return
	EndIf
	Actor killer = Alias_CutterLead.GetActorReference()
	If killer && killer.IsDead()
		killer = None
	EndIf
	hand.SetProtected(false)
	hand.Kill(killer)
EndFunction

Function LootWagon()
	ObjectReference wagon = Alias_Wagon.GetReference()
	If wagon
		wagon.RemoveAllItems()
	EndIf
EndFunction

; ------------------------------------------------------------------ stage 40

Function ApplyTown()
	; A resolution may be half done on another thread: the player left the
	; ambush and reached the gate in the same breath. Let it finish, because
	; what follows asks who is alive.
	WaitForResolutions(0)
	; An encounter the player never resolved is resolved now.
	If IsArmed()
		SetStage(34)
	ElseIf IsLive()
		ResolveUnattended()
	EndIf
	; And again: the resolution this stage has just asked for may be another
	; thread's. If its stage had been set a moment earlier, SetStage above came
	; straight back; if another resolution claimed the encounter first, the
	; handler above stood aside. Either way someone else is still at work.
	WaitForResolutions(0)
	MoveHandToTown(Alias_CaravanMaster, Alias_CaravanMasterInTown)
	MoveHandToTown(Alias_CaravanDrover, Alias_CaravanDroverInTown)
	Alias_CutterLead.TryToDisable()
	Alias_CutterA.TryToDisable()
	Alias_CutterB.TryToDisable()
	Alias_CutterC.TryToDisable()
	UpdateAliveAtMercy()
EndFunction

Function MoveHandToTown(ReferenceAlias akHand, ReferenceAlias akTownAlias)
	Actor hand = akHand.GetActorReference()
	ObjectReference yard = Alias_CaravanYard.GetReference()
	If !hand || hand.IsDead() || !yard
		Return
	EndIf
	If hand.GetDistance(yard) > 1500.0
		hand.MoveTo(yard)
	EndIf
	; In town the hands are Essential, so "no witness" can only follow a
	; killing on the road.
	akTownAlias.ForceRefTo(hand)
EndFunction

Function UpdateAliveAtMercy()
	If IsAliveAlias(Alias_CaravanMaster)
		TLM_G_CaravanAliveAtMercy.SetValueInt(1)
	Else
		TLM_G_CaravanAliveAtMercy.SetValueInt(0)
	EndIf
EndFunction

; ------------------------------------------------------------------ stage 50

Function ApplyDelivered()
	Actor player = Game.GetPlayer()
	If !GetStageDone(20)
		Debug.Trace("TLM_MQ01: stage 50 set without stage 20; ignored")
		Return
	EndIf
	If !GetStageDone(40)
		SetStage(40)
	EndIf
	; Take the dispatch if the player still has it. If it has gone missing
	; the delivery stands: stage 20 is the proof they earned it.
	If player.GetItemCount(DispatchItem) > 0
		player.RemoveItem(DispatchItem, 1, true)
	EndIf
	SetObjectiveCompleted(20)

	int result = Outcome()
	bool nellAlive = IsAliveAlias(Alias_CaravanMaster)
	bool witness = nellAlive || IsAliveAlias(Alias_CaravanDrover)
	UpdateAliveAtMercy()

	int variant = V_LOST
	If result == OUT_EXPLOITED
		If witness
			variant = V_WITNESS
		Else
			variant = V_NOWITNESS
		EndIf
	ElseIf !nellAlive
		variant = V_LOST
	ElseIf result == OUT_SAVED
		variant = V_SAVED
	ElseIf result == OUT_EVADED
		variant = V_EVADED
	ElseIf result == OUT_MISSED
		variant = V_MISSED
	EndIf
	TLM_G_MQ01_DebriefVariant.SetValueInt(variant)

	; Reputation (design section 9.1), applied once.
	int rep = 1
	If result == OUT_SAVED
		rep += 1
	EndIf
	If result == OUT_EXPLOITED && witness
		rep -= 1
	EndIf
	TLM_G_Rep_MercyCrossing.Mod(rep)

	If variant == V_SAVED
		TLM_MutualTrust.Mod(1)
	EndIf
EndFunction

Function ApplyDebriefAnswer(int aiAnswer)
	If !GetStageDone(50) || GetStageDone(60)
		Return
	EndIf
	If TLM_G_MQ01_DebriefAnswer.GetValueInt() != 0
		Return
	EndIf
	int variant = TLM_G_MQ01_DebriefVariant.GetValueInt()
	If variant == V_EVADED
		If aiAnswer == ANS_ADMIT
			TLM_Truth.Mod(1)
			TLM_Accountability.Mod(1)
		ElseIf aiAnswer == ANS_DENY
			TLM_Truth.Mod(-1)
		Else
			Return
		EndIf
	ElseIf variant == V_WITNESS
		If aiAnswer == ANS_CONFESS
			TLM_Truth.Mod(1)
			TLM_Accountability.Mod(1)
		ElseIf aiAnswer == ANS_BLAME
			TLM_Truth.Mod(-1)
		ElseIf aiAnswer == ANS_LYING
			TLM_Truth.Mod(-1)
			TLM_MutualTrust.Mod(-1)
		Else
			Return
		EndIf
	Else
		Return
	EndIf
	TLM_G_MQ01_DebriefAnswer.SetValueInt(aiAnswer)
EndFunction

Function ApplyDebriefDone()
	If TLM_G_MQ01_DebriefAnswer.GetValueInt() == 0
		TLM_G_MQ01_DebriefAnswer.SetValueInt(ANS_SILENT)
	EndIf
	TLM_G_MQ01_Done.SetValueInt(1)
	SetStage(100)
EndFunction

; ------------------------------------------------------------ load / recovery

Function OnGameLoaded()
	{Called by TLM:MQ01PlayerAlias on OnPlayerLoadGame.}
	If !IsRunning()
		Return
	EndIf
	If IsLive()
		ArmEvadeWatch()
	EndIf
	Recover()
EndFunction

Function Recover()
	{Repairs state. Grants nothing the player has not already earned.
	Stage 900 calls this once; after that use: cqf TLM_MQ01 Recover}
	Actor player = Game.GetPlayer()
	If GetStageDone(20) && !GetStageDone(50) && player.GetItemCount(DispatchItem) == 0
		player.AddItem(DispatchItem, 1, true)
		Debug.Trace("TLM_MQ01: dispatch was missing; replaced")
	EndIf
	If GetStageDone(10) && !GetStageDone(20)
		SetObjectiveDisplayed(10, true, true)
	ElseIf GetStageDone(20) && !GetStageDone(50)
		SetObjectiveDisplayed(20, true, true)
	EndIf
EndFunction
