Scriptname TLM:CaseDriver extends Quest
{Development only, attached to TLM_Core. It must be removed before any release.

The hands and eyes of the generated test cases (TLM:MatrixCases, self-test
scenarios 101 and up). A case is a list of events from the logic model. For
each event this script does the thing in the game that stands for it, and
then compares everything it can see of both quests with what the model
predicts after that event.

What stands for what:
  the wreck, the ambush and the town are not places. The caravan (two hands,
  the Cutter lead, three Cutters, the wagon) is settlers made next to the
  player and forced into the main quest's aliases; one more settler is
  Corwin Haskell for the side quest; two of the game's markers are the
  caravan yard and the centre of the ambush.
  A trigger, a pickup or a line of dialogue is the stage it would set.
  Picking up the dispatch, the ledger or the journal also gives the item.
  A kill by the player is Kill with the player named as the killer.
  The evade timer running out is a direct call of the function the timer
  calls. Leaving the ambush is moving its centre marker away from the player.

So a pass says the quest scripts keep to the model once those stages are set
and those deaths happen. It says nothing about triggers, pickups, dialogue
conditions, AI or a built place.

RAN IN THE GAME on 2026-11-12: it drove all 53 cases, 1,340 checks, 0 failed
(docs/design/VERIFY_LOG.md), the four included that do two things with no
time between them (DoKillLeadThenTimer, DoKillLeadThenLeave,
DoKillLeadThenTown, DoLeaveAndReachTownAtOnce). Since then
DoKillLeadThenTimer was changed, to make the kill a quiet one and to report
what the game says about the fight: THAT ACTION IS NOT YET COMPILED.}

Group Quests
	Quest Property TLM_MQ01 Auto Const Mandatory
	Quest Property TLM_SQ01 Auto Const Mandatory
EndGroup

Group Globals
	GlobalVariable Property TLM_G_CaravanMethod Auto Const Mandatory
	GlobalVariable Property TLM_G_CaravanAliveAtMercy Auto Const Mandatory
	GlobalVariable Property TLM_G_Rep_MercyCrossing Auto Const Mandatory
	GlobalVariable Property TLM_G_MQ01_Done Auto Const Mandatory
	GlobalVariable Property TLM_G_MQ01_DebriefVariant Auto Const Mandatory
	GlobalVariable Property TLM_G_MQ01_DebriefAnswer Auto Const Mandatory
	GlobalVariable Property TLM_Truth Auto Const Mandatory
	GlobalVariable Property TLM_Competence Auto Const Mandatory
	GlobalVariable Property TLM_Accountability Auto Const Mandatory
	GlobalVariable Property TLM_MutualTrust Auto Const Mandatory
	GlobalVariable Property TLM_G_SQ01_EvidenceCount Auto Const Mandatory
	GlobalVariable Property TLM_G_SQ01_EvidenceLevel Auto Const Mandatory
	GlobalVariable Property TLM_G_SQ01_Outcome Auto Const Mandatory
	GlobalVariable Property TLM_G_SQ01_YardAlerted Auto Const Mandatory
	GlobalVariable Property TLM_G_SQ01_VaneHasLedger Auto Const Mandatory
	GlobalVariable Property TLM_G_SQ01_HaskellScapegoated Auto Const Mandatory
EndGroup

Group Forms
	Form Property DispatchItem Auto Const Mandatory
	{TLM_MISC_Dispatch}
	Form Property LedgerItem Auto Const Mandatory
	{TLM_BOOK_RailMaintLedger}
	Form Property JournalItem Auto Const Mandatory
	{TLM_BOOK_MarshalLog}
	Form Property TornTransitPass Auto Const Mandatory
	{Any item of this plugin. Copies of it are the wagon's cargo.}
	Form Property Caps Auto Const
	{Caps001 from Fallout4.esm. Without it the sale's payment is not checked.}
	Form Property FixtureActorBase Auto Const
	{The generic settler, looked up in Fallout4.esm when the plugin is built.}
	Form Property FixtureMarkerBase Auto Const
	{The game's plain marker (XMarker), looked up the same way.}
EndGroup

; How many items the stand-in wagon carries while its cargo is intact.
int CARGO_COUNT = 3 Const
; An expected number that means "not looked at in this step". Not -1: the
; four counters really do go below zero.
int SKIP = -999 Const

TLM:SelfTest test
TLM:MQ01Quest mq
TLM:SQ01Quest sideQuestScript
Actor player
Actor nell
Actor abel
Actor lead
Actor cutterA
Actor cutterB
Actor cutterC
Actor wagonStandIn
Actor haskellStandIn
ObjectReference yard
ObjectReference center
string caseName = ""
string stepLabel = ""
int capsAtStart = 0
bool fixturesReady = false

; ------------------------------------------------------------- lifecycle

bool Function CaseBegin(TLM:SelfTest akTest, string asCase, string asTitle)
	test = akTest
	caseName = asCase
	stepLabel = asCase
	fixturesReady = false
	player = Game.GetPlayer()
	mq = TLM_MQ01 as TLM:MQ01Quest
	sideQuestScript = TLM_SQ01 as TLM:SQ01Quest
	test.Note(asCase + ": " + asTitle)
	If !mq || !sideQuestScript
		test.Fail(asCase + ": a quest does not carry its script")
		Return false
	EndIf
	If !FixtureActorBase || !FixtureMarkerBase
		test.Fail(asCase + ": the settler or the marker was not found in Fallout4.esm when the plugin was built, so the caravan cannot be made")
		Return false
	EndIf
	; Nobody is at the controls, and the stand-ins carry guns.
	Debug.SetGodMode(true)
	Return true
EndFunction

Function CaseEnd()
	test.Step(caseName + ": removing the stand-ins")
	RemoveFixture(nell)
	RemoveFixture(abel)
	RemoveFixture(lead)
	RemoveFixture(cutterA)
	RemoveFixture(cutterB)
	RemoveFixture(cutterC)
	RemoveFixture(wagonStandIn)
	RemoveFixture(haskellStandIn)
	RemoveFixture(yard)
	RemoveFixture(center)
	Debug.SetGodMode(false)
EndFunction

Function Mark(int aiStep, string asWhat)
	{Names the step that follows, for the log, the watchdog and the checks.}
	stepLabel = caseName + " #" + aiStep + " " + asWhat
	test.Step(stepLabel)
EndFunction

; ---------------------------------------------------- main quest: events

Function DoStart()
	{start: the quest begins (stage 10), and the caravan is stood up.}
	test.Reach(TLM_MQ01, 10)
	test.Step(stepLabel + ": making the stand-ins")
	nell = SpawnFixture()
	abel = SpawnFixture()
	lead = SpawnFixture()
	cutterA = SpawnFixture()
	cutterB = SpawnFixture()
	cutterC = SpawnFixture()
	wagonStandIn = SpawnFixture()
	haskellStandIn = SpawnFixture()
	yard = player.PlaceAtMe(FixtureMarkerBase)
	center = player.PlaceAtMe(FixtureMarkerBase)
	If !nell || !abel || !lead || !cutterA || !cutterB || !cutterC || !wagonStandIn || !haskellStandIn || !yard || !center
		test.Fail(caseName + ": a stand-in could not be made")
		Return
	EndIf
	test.Step(stepLabel + ": putting the stand-ins into the quests' aliases")
	mq.Alias_CaravanMaster.ForceRefTo(nell)
	mq.Alias_CaravanDrover.ForceRefTo(abel)
	mq.Alias_CutterLead.ForceRefTo(lead)
	mq.Alias_CutterA.ForceRefTo(cutterA)
	mq.Alias_CutterB.ForceRefTo(cutterB)
	mq.Alias_CutterC.ForceRefTo(cutterC)
	mq.Alias_Wagon.ForceRefTo(wagonStandIn)
	mq.Alias_CaravanYard.ForceRefTo(yard)
	mq.Alias_AmbushCenter.ForceRefTo(center)
	sideQuestScript.Alias_Haskell.ForceRefTo(haskellStandIn)
	; The caravan and the Cutters are kept alive by their aliases' flags. These
	; two have none, and settlers who have just seen one of their own killed
	; may start shooting. Haskell lives in town; the wagon is a wagon.
	wagonStandIn.SetProtected(true)
	haskellStandIn.SetProtected(true)
	wagonStandIn.AddItem(TornTransitPass, CARGO_COUNT, true)
	capsAtStart = 0
	If Caps
		capsAtStart = player.GetItemCount(Caps)
	EndIf
	Utility.Wait(1.0)
	fixturesReady = true
EndFunction

Function DoTakeRevolver()
	{take_revolver: the pickup sets stage 15.}
	test.Reach(TLM_MQ01, 15)
EndFunction

Function DoTakeDispatch()
	{take_dispatch: the item, and the stage its pickup sets.}
	player.AddItem(DispatchItem, 1, true)
	test.Reach(TLM_MQ01, 20)
EndFunction

Function DoEnterAmbush()
	{goto_ambush: the sight trigger sets stage 30.}
	test.Reach(TLM_MQ01, 30)
EndFunction

Function DoLeaveAmbush()
	{Leaving a live ambush: its centre is moved beyond the evade distance, and
	the quest's own distance watch is expected to set stage 32.

	The stage is set by the quest on a thread of its own, and a stage reads as
	done while its handler is still at work: the handler kills the drover and
	empties the wagon last. So this waits for the handler to have finished,
	not only for the stage. Otherwise the next step could reach the town
	stage first and find the drover still alive.}
	int handledBefore = mq.StageEventsHandled()
	center.MoveTo(player, mq.EvadeDistance + 1000.0, 0.0, 0.0)
	WaitStage(32)
	int tries = 0
	While mq.StageEventsHandled() <= handledBefore && tries < 16
		Utility.Wait(0.5)
		tries += 1
	EndWhile
EndFunction

Function DoLeaveAndReachTownAtOnce()
	{goto_town from a live ambush with no time between the two things it is
	made of (amendment A24). The centre is moved away, and the town stage is
	set the instant the evade stage reads as done, while its handler may still
	be at work on another thread. Whether it was is reported, not scored.}
	int handledBefore = mq.StageEventsHandled()
	center.MoveTo(player, mq.EvadeDistance + 1000.0, 0.0, 0.0)
	int tries = 0
	While !TLM_MQ01.GetStageDone(32) && tries < 800
		Utility.Wait(0.01)
		tries += 1
	EndWhile
	bool atWork = mq.StageEventsHandled() == handledBefore
	TLM_MQ01.SetStage(40)
	test.Note(stepLabel + ": the town stage was set while the evade stage's handler was still at work: " + atWork)
	; both handlers have to be through before anything is compared
	tries = 0
	While mq.StageEventsHandled() < handledBefore + 2 && tries < 20
		Utility.Wait(0.5)
		tries += 1
	EndWhile
EndFunction

Function DoKillLeadThenTimer()
	{player_kills_lead, with the evade timer running out before the death has
	been announced (amendment A24). He is dead at once; OnDeath comes about a
	second later.

	In the run of 2026-11-12 the game took the kill itself for a fight: the
	timer's function found the player in combat and started over, so the
	guard this case is for never acted. The kill is therefore made a quiet
	one: the three Cutters still standing are told to stand down and the
	alarm against the player is ended, as after break_combat. Whether that
	is enough in the game is reported, not scored: the case passes either
	way, and the report's "Timing" part says which rule decided it.}
	lead.Kill(player)
	test.Note(stepLabel + ": player in combat straight after the kill: " + player.IsInCombat())
	cutterA.StopCombat()
	cutterB.StopCombat()
	cutterC.StopCombat()
	player.StopCombatAlarm()
	test.Note(stepLabel + ": player in combat after the Cutters were told to stand down: " + player.IsInCombat())
	mq.EvadeTimerElapsed()
	WaitStage(31)
	Utility.Wait(2.0)
EndFunction

Function DoKillLeadThenLeave()
	{player_kills_lead, with the player beyond the evade distance before the
	death has been announced (amendment A24).}
	lead.Kill(player)
	center.MoveTo(player, mq.EvadeDistance + 1000.0, 0.0, 0.0)
	WaitStage(31)
	Utility.Wait(2.0)
EndFunction

Function DoKillLeadThenTown()
	{player_kills_lead, with the town stage before the death has been
	announced (amendment A24).}
	lead.Kill(player)
	test.Reach(TLM_MQ01, 40)
	Utility.Wait(2.0)
EndFunction

Function DoReachTown()
	{goto_town: the gate trigger sets stage 40.}
	test.Reach(TLM_MQ01, 40)
EndFunction

Function DoEvadeTimer(bool abResolves)
	{evade_timer: the function the timer calls, called directly.}
	mq.EvadeTimerElapsed()
	If abResolves
		WaitStage(32)
	EndIf
EndFunction

Function DoAttackCutter()
	{attack_cutter: a fight between the Cutter lead and the player begins.}
	lead.StartCombat(player)
	WaitCombat(true)
EndFunction

Function DoBreakCombat()
	{break_combat: the fight ends without anyone leaving. The Cutters are told
	to stop, and so is anyone else who has joined in against the player.}
	lead.StopCombat()
	cutterA.StopCombat()
	cutterB.StopCombat()
	cutterC.StopCombat()
	player.StopCombatAlarm()
	WaitCombat(false)
EndFunction

Function DoKillLead(bool abSaves)
	{player_kills_lead}
	lead.Kill(player)
	If abSaves
		WaitStage(31)
	EndIf
	Utility.Wait(1.0)
EndFunction

Function DoKillCutter()
	{player_kills_cutter: the next of the three still standing.}
	If !cutterA.IsDead()
		cutterA.Kill(player)
	ElseIf !cutterB.IsDead()
		cutterB.Kill(player)
	Else
		cutterC.Kill(player)
	EndIf
	Utility.Wait(1.5)
EndFunction

Function DoSpeechSuccess()
	{dunmore_speech_success: the line that talks the Cutters down sets stage 31.}
	test.Reach(TLM_MQ01, 31)
EndFunction

Function DoSpeechFail()
	{dunmore_speech_fail and dunmore_refuse: the line sets stage 37.}
	test.Reach(TLM_MQ01, 37)
	WaitCombat(true)
EndFunction

Function DoDeal()
	{dunmore_deal: the line sets stage 33.}
	test.Reach(TLM_MQ01, 33)
EndFunction

Function DoKillHand(Actor akHand, bool abBetrays)
	{player_kills_nell, player_kills_abel. When the model says nothing follows
	(a hand in town), the wait gives a death that should not happen time to show.}
	akHand.Kill(player)
	If abBetrays
		WaitStage(35)
		Utility.Wait(1.0)
	Else
		Utility.Wait(2.5)
	EndIf
EndFunction

Function DoKillNell(bool abBetrays)
	DoKillHand(nell, abBetrays)
EndFunction

Function DoKillAbel(bool abBetrays)
	DoKillHand(abel, abBetrays)
EndFunction

Function DoNellDiesOther()
	{nell_dies_other: dead with nobody named as the killer.}
	nell.SetProtected(false)
	nell.Kill()
	Utility.Wait(1.5)
EndFunction

Function DoDispatchVanishes()
	{dispatch_vanishes}
	player.RemoveItem(DispatchItem, 1, true)
EndFunction

Function DoRecovery()
	{recovery: stage 900 the first time, the function after that, on both quests.}
	If !TLM_MQ01.GetStageDone(900)
		test.Reach(TLM_MQ01, 900)
	Else
		mq.Recover()
	EndIf
	If !TLM_SQ01.GetStageDone(900)
		test.Reach(TLM_SQ01, 900)
	Else
		sideQuestScript.Recover()
	EndIf
EndFunction

Function DoHandover()
	{pritchard_handover: the line sets stage 50.}
	test.Reach(TLM_MQ01, 50)
EndFunction

Function DoAnswer(int aiStage)
	{debrief_admit 51, debrief_deny 52 (55 when a witness accuses),
	debrief_confess 53, debrief_blame 54.}
	test.Reach(TLM_MQ01, aiStage)
EndFunction

Function DoHandoff()
	{pritchard_handoff: the line sets stage 60.}
	test.Reach(TLM_MQ01, 60)
EndFunction

; ---------------------------------------------------- side quest: events

Function DoTakeLedger()
	{take_ledger: the item, and the stage its pickup sets.}
	player.AddItem(LedgerItem, 1, true)
	test.Reach(TLM_SQ01, 10)
EndFunction

Function DoExamine(int aiStage)
	{examine_e1 11, examine_e2 12: the stage the clue's message sets.}
	test.Reach(TLM_SQ01, aiStage)
EndFunction

Function DoTakeJournal()
	{take_journal: the item, and stage 13.}
	player.AddItem(JournalItem, 1, true)
	test.Reach(TLM_SQ01, 13)
EndFunction

Function DoPartsBook()
	{pike_parts_book: the line sets stage 14.}
	test.Reach(TLM_SQ01, 14)
EndFunction

Function DoDecide(int aiStage)
	{sq_report 41, sq_post 42, sq_post_yard 43, sq_post_haskell 44, sq_sell 45,
	sq_destroy 46.}
	test.Reach(TLM_SQ01, aiStage)
EndFunction

Function DoHaskellDies()
	{haskell_dies: dead with nobody named as the killer.}
	haskellStandIn.SetProtected(false)
	haskellStandIn.Kill()
	Utility.Wait(1.5)
EndFunction

Function DoLedgerVanishes()
	{ledger_vanishes}
	player.RemoveItem(LedgerItem, 1, true)
EndFunction

; ----------------------------------------------------------------- checks
; SKIP (-999) for a number means "not looked at in this step".

Function ExpectMain(string asStages, int aiOutcome, int aiMethod, int aiAliveAtMercy, int aiRep, int aiVariant, int aiAnswer, int aiDone, int aiObjective10, int aiObjective20)
	string differences = ""
	differences += DiffText("stages", MainStages(), asStages)
	differences += DiffInt("outcome", mq.Outcome(), aiOutcome)
	differences += DiffInt("method", TLM_G_CaravanMethod.GetValueInt(), aiMethod)
	differences += DiffInt("caravan alive at Mercy", TLM_G_CaravanAliveAtMercy.GetValueInt(), aiAliveAtMercy)
	differences += DiffInt("reputation", TLM_G_Rep_MercyCrossing.GetValueInt(), aiRep)
	differences += DiffInt("debrief variant", TLM_G_MQ01_DebriefVariant.GetValueInt(), aiVariant)
	differences += DiffInt("debrief answer", TLM_G_MQ01_DebriefAnswer.GetValueInt(), aiAnswer)
	differences += DiffInt("done", TLM_G_MQ01_Done.GetValueInt(), aiDone)
	differences += DiffInt("objective 10", ObjectiveState(TLM_MQ01, 10), aiObjective10)
	differences += DiffInt("objective 20", ObjectiveState(TLM_MQ01, 20), aiObjective20)
	Report("main quest", differences)
EndFunction

Function ExpectWorld(int aiNell, int aiAbel, int aiLead, int aiCutters, int aiCargo, int aiMasterInTown, int aiDroverInTown, int aiCuttersDisabled, int aiDispatch, int aiInCombat)
	If !fixturesReady
		test.Fail(stepLabel + ": the world: the stand-ins were never made")
		Return
	EndIf
	string differences = ""
	differences += DiffInt("caravan master alive", Alive(nell), aiNell)
	differences += DiffInt("drover alive", Alive(abel), aiAbel)
	differences += DiffInt("Cutter lead alive", Alive(lead), aiLead)
	differences += DiffInt("unnamed Cutters alive", Alive(cutterA) + Alive(cutterB) + Alive(cutterC), aiCutters)
	differences += DiffInt("cargo on the wagon", wagonStandIn.GetItemCount(TornTransitPass), aiCargo)
	differences += DiffInt("caravan master in the town alias", Holds(mq.Alias_CaravanMasterInTown, nell), aiMasterInTown)
	differences += DiffInt("drover in the town alias", Holds(mq.Alias_CaravanDroverInTown, abel), aiDroverInTown)
	differences += DiffInt("Cutters disabled", Disabled(lead) + Disabled(cutterA) + Disabled(cutterB) + Disabled(cutterC), aiCuttersDisabled)
	differences += DiffInt("dispatch carried", player.GetItemCount(DispatchItem), aiDispatch)
	If aiInCombat != SKIP
		differences += DiffInt("player in combat", Flag(player.IsInCombat()), aiInCombat)
	EndIf
	Report("the world", differences)
EndFunction

Function ExpectMetrics(int aiTruth, int aiCompetence, int aiAccountability, int aiMutualTrust)
	string differences = ""
	differences += DiffInt("truth", TLM_Truth.GetValueInt(), aiTruth)
	differences += DiffInt("competence", TLM_Competence.GetValueInt(), aiCompetence)
	differences += DiffInt("accountability", TLM_Accountability.GetValueInt(), aiAccountability)
	differences += DiffInt("mutual trust", TLM_MutualTrust.GetValueInt(), aiMutualTrust)
	Report("the four counters", differences)
EndFunction

Function ExpectSide(string asStages, int aiCount, int aiLevel, int aiOutcome, int aiYardAlerted, int aiVaneHasLedger, int aiScapegoated, int aiObjective10, int aiObjective20, int aiLedger, int aiJournal, int aiHaskell, int aiCapsGained)
	string differences = ""
	differences += DiffText("stages", SideStages(), asStages)
	differences += DiffInt("evidence count", TLM_G_SQ01_EvidenceCount.GetValueInt(), aiCount)
	differences += DiffInt("evidence level", TLM_G_SQ01_EvidenceLevel.GetValueInt(), aiLevel)
	differences += DiffInt("outcome", TLM_G_SQ01_Outcome.GetValueInt(), aiOutcome)
	differences += DiffInt("Yard alerted", TLM_G_SQ01_YardAlerted.GetValueInt(), aiYardAlerted)
	differences += DiffInt("Vane has the ledger", TLM_G_SQ01_VaneHasLedger.GetValueInt(), aiVaneHasLedger)
	differences += DiffInt("Haskell scapegoated", TLM_G_SQ01_HaskellScapegoated.GetValueInt(), aiScapegoated)
	differences += DiffInt("objective 10", ObjectiveState(TLM_SQ01, 10), aiObjective10)
	differences += DiffInt("objective 20", ObjectiveState(TLM_SQ01, 20), aiObjective20)
	differences += DiffInt("ledger carried", player.GetItemCount(LedgerItem), aiLedger)
	differences += DiffInt("journal carried", player.GetItemCount(JournalItem), aiJournal)
	If fixturesReady
		differences += DiffInt("Haskell (0 there, 1 gone, 2 dead)", HaskellState(), aiHaskell)
	EndIf
	If Caps
		differences += DiffInt("caps gained", player.GetItemCount(Caps) - capsAtStart, aiCapsGained)
	EndIf
	Report("side quest", differences)
EndFunction

Function Report(string asPart, string asDiff)
	If asDiff == ""
		test.Pass(stepLabel + ": " + asPart)
	Else
		test.Fail(stepLabel + ": " + asPart + ":" + asDiff)
	EndIf
EndFunction

string Function DiffInt(string asName, int aiActual, int aiExpected)
	If aiExpected == SKIP || aiActual == aiExpected
		Return ""
	EndIf
	Return " " + asName + " = " + aiActual + ", expected " + aiExpected + ";"
EndFunction

string Function DiffText(string asName, string asActual, string asExpected)
	If asActual == asExpected
		Return ""
	EndIf
	Return " " + asName + " =" + asActual + ", expected" + asExpected + ";"
EndFunction

; ------------------------------------------------------ what can be seen

string Function MainStages()
	{The stages of TLM_MQ01 that are done, in order, each after a space.}
	string stagesText = ""
	stagesText += StageWord(TLM_MQ01, 10)
	stagesText += StageWord(TLM_MQ01, 15)
	stagesText += StageWord(TLM_MQ01, 20)
	stagesText += StageWord(TLM_MQ01, 30)
	stagesText += StageWord(TLM_MQ01, 31)
	stagesText += StageWord(TLM_MQ01, 32)
	stagesText += StageWord(TLM_MQ01, 33)
	stagesText += StageWord(TLM_MQ01, 34)
	stagesText += StageWord(TLM_MQ01, 35)
	stagesText += StageWord(TLM_MQ01, 37)
	stagesText += StageWord(TLM_MQ01, 40)
	stagesText += StageWord(TLM_MQ01, 50)
	stagesText += StageWord(TLM_MQ01, 51)
	stagesText += StageWord(TLM_MQ01, 52)
	stagesText += StageWord(TLM_MQ01, 53)
	stagesText += StageWord(TLM_MQ01, 54)
	stagesText += StageWord(TLM_MQ01, 55)
	stagesText += StageWord(TLM_MQ01, 60)
	stagesText += StageWord(TLM_MQ01, 100)
	stagesText += StageWord(TLM_MQ01, 900)
	Return stagesText
EndFunction

string Function SideStages()
	{The same for TLM_SQ01.}
	string stagesText = ""
	stagesText += StageWord(TLM_SQ01, 5)
	stagesText += StageWord(TLM_SQ01, 10)
	stagesText += StageWord(TLM_SQ01, 11)
	stagesText += StageWord(TLM_SQ01, 12)
	stagesText += StageWord(TLM_SQ01, 13)
	stagesText += StageWord(TLM_SQ01, 14)
	stagesText += StageWord(TLM_SQ01, 20)
	stagesText += StageWord(TLM_SQ01, 25)
	stagesText += StageWord(TLM_SQ01, 41)
	stagesText += StageWord(TLM_SQ01, 42)
	stagesText += StageWord(TLM_SQ01, 43)
	stagesText += StageWord(TLM_SQ01, 44)
	stagesText += StageWord(TLM_SQ01, 45)
	stagesText += StageWord(TLM_SQ01, 46)
	stagesText += StageWord(TLM_SQ01, 50)
	stagesText += StageWord(TLM_SQ01, 100)
	stagesText += StageWord(TLM_SQ01, 900)
	Return stagesText
EndFunction

string Function StageWord(Quest akQuest, int aiStage)
	If akQuest.GetStageDone(aiStage)
		Return " " + aiStage
	EndIf
	Return ""
EndFunction

int Function ObjectiveState(Quest akQuest, int aiObjective)
	{0 hidden, 1 shown, 2 completed: the logic model's three states.}
	If akQuest.IsObjectiveCompleted(aiObjective)
		Return 2
	EndIf
	If akQuest.IsObjectiveDisplayed(aiObjective)
		Return 1
	EndIf
	Return 0
EndFunction

int Function Flag(bool abValue)
	If abValue
		Return 1
	EndIf
	Return 0
EndFunction

int Function Alive(Actor akActor)
	Return Flag(!akActor.IsDead())
EndFunction

int Function Disabled(Actor akActor)
	Return Flag(akActor.IsDisabled())
EndFunction

int Function Holds(ReferenceAlias akAlias, Actor akActor)
	Return Flag(akAlias.GetActorReference() == akActor)
EndFunction

int Function HaskellState()
	If haskellStandIn.IsDead()
		Return 2
	EndIf
	If haskellStandIn.IsDisabled()
		Return 1
	EndIf
	Return 0
EndFunction

; ---------------------------------------------------------------- helpers

Actor Function SpawnFixture()
	ObjectReference placed = player.PlaceAtMe(FixtureActorBase)
	Return placed as Actor
EndFunction

Function RemoveFixture(ObjectReference akRef)
	If akRef
		akRef.Disable()
		akRef.Delete()
	EndIf
EndFunction

Function WaitStage(int aiStage)
	{Waits until the main quest reports the stage, or eight seconds. A death is
	announced when the actor has finished dying, which takes a moment.}
	int tries = 0
	While !TLM_MQ01.GetStageDone(aiStage) && tries < 16
		Utility.Wait(0.5)
		tries += 1
	EndWhile
EndFunction

Function WaitCombat(bool abInCombat)
	{Waits until the player is, or is no longer, in combat, or eight seconds.}
	int tries = 0
	While player.IsInCombat() != abInCombat && tries < 16
		Utility.Wait(0.5)
		tries += 1
	EndWhile
EndFunction
