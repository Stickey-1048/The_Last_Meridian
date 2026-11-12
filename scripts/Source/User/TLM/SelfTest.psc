Scriptname TLM:SelfTest extends Quest
{Development self-test, attached to TLM_Core next to TLM:Core. It is not part of
the story and must be removed before any release.

It drives TLM_MQ01 and TLM_SQ01 through one scenario by setting stages, then
checks stages, objectives and globals against the values the logic model
predicts. tools/logic_model/test_selftest_expectations.py reads the CheckInt
lines below and fails if they drift from the model.

Run it once per game session, from the console:   cqf TLM_Core RunSelfTest
Results go to Documents\My Games\Fallout4\Logs\Script\User\TLM.0.log (Papyrus
logging has to be on), to the Papyrus log, and to a message box.

Scenarios: 1 here; 2 and 3 in TLM:FixtureProbe; 4 to 9 in TLM:WorldCases;
101 and up in TLM:MatrixCases, which is generated from the logic model.
A number after the function name picks one:   cqf TLM_Core RunSelfTest 4
One fresh game session per scenario: the quests run once.

COMPILES. RAN IN THE GAME on 2026-11-12 with nobody at the keyboard: all 58
scenarios passed, 1,456 checks, 0 failed (docs/design/VERIFY_LOG.md). The
watchdog was seen to work: it ends scenario 3 inside an experiment that does
not come back, and the result is still written. Scenario 1 also ran from the
console. (An earlier run of scenario 1 reported 26 passed, 34 failed, because
no OnStageSet event reached the quest scripts; that was a fault in the
generated plugin.)}

Group Quests
	Quest Property TLM_MQ01 Auto Const Mandatory
	Quest Property TLM_SQ01 Auto Const Mandatory
EndGroup

Group Globals
	GlobalVariable Property TLM_G_DataVersion Auto Const Mandatory
	GlobalVariable Property TLM_G_CaravanOutcome Auto Const Mandatory
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
	GlobalVariable Property TLM_G_SQ01_HaskellScapegoated Auto Const Mandatory
EndGroup

Group Forms
	Form Property TornTransitPass Auto Const Mandatory
	{TLM_MISC_TornTransitPass. MQ01 stage 10 gives the player one.}
EndGroup

int passed = 0
int failed = 0
string firstFailure = ""
bool busy = false
; How often a stage's handler had already finished when SetStage returned.
; The quest scripts rely on that order wherever a handler sets another stage
; and then reads what it changed. Reported, not scored.
int reaches = 0
int handledBeforeReturn = 0
; True when TLM:Core started the run for the unattended runner: no message
; boxes, and the game is closed at the end.
bool unattended = false
; The watchdog of an unattended run. A scenario that calls something which
; never comes back would otherwise sit there until the runner on the PC gives
; up, with no result written. Every Step() names what the scenario is about to
; do and gives it a number of seconds; if the next Step() or the end of the
; scenario has not come by then, the watchdog writes where it stopped and
; closes the game.
int TIMER_WATCHDOG = 9 Const
string currentStep = ""
bool currentStepIsExperiment = false
bool finished = false

; ------------------------------------------------------------------- entry

Function RunUnattended(int aiScenario)
	{Called by TLM:Core when the installed plugin carries a scenario number
	(tools/win/Run-Scenarios.ps1 puts it there). Runs that scenario, makes sure
	the results are on disk, and closes the game: the runner on the PC is
	waiting for the game to end.}
	unattended = true
	finished = false
	currentStep = "starting the scenario"
	currentStepIsExperiment = false
	StartTimer(90.0, TIMER_WATCHDOG)
	RunSelfTest(aiScenario)
	If finished
		; The watchdog has already written the result and is closing the game.
		Return
	EndIf
	finished = true
	CancelTimer(TIMER_WATCHDOG)
	Debug.CloseUserLog("TLM")
	Utility.Wait(3.0)
	Debug.QuitGame()
EndFunction

Event OnTimer(int aiTimerID)
	If aiTimerID == TIMER_WATCHDOG && unattended && !finished
		; The scenario is inside a call that has not come back. Say where,
		; write what there is, and close the game.
		finished = true
		If currentStepIsExperiment
			Note("this experiment did not come back, and the scenario was ended here: " + currentStep)
		Else
			Fail("the scenario did not come back from: " + currentStep)
		EndIf
		WriteResult()
		Debug.CloseUserLog("TLM")
		Utility.Wait(2.0)
		Debug.QuitGame()
	EndIf
EndEvent

Function Step(string asWhat, float afSeconds = 45.0, bool abExperiment = false)
	{Names what the scenario is about to do and how long it may take. Written
	to the log, so the last STEP line of a run that stopped shows where. An
	experiment is a step that is allowed not to come back: the watchdog then
	reports it as a fact about the game and not as a failure. Nothing can
	follow an experiment that did not come back, so experiments go last.}
	currentStep = asWhat
	currentStepIsExperiment = abExperiment
	Log("STEP  " + asWhat)
	If unattended && !finished
		StartTimer(afSeconds, TIMER_WATCHDOG)
	EndIf
EndFunction

Function WriteResult()
	Log("INFO  stage handlers already finished when SetStage returned: " + handledBeforeReturn + " of " + reaches)
	Log("==== RESULT: " + passed + " passed, " + failed + " failed ====")
EndFunction

Function RunSelfTest(int aiScenario = 0)
	{Scenario 1 (also what the console gets when no number is given): the main
	and side quest by stages alone. 2: actors made at run time and put into the
	quest's aliases. 3: distance events. 4 to 9: the main quest played with a
	caravan made at run time, one case for each way the encounter can end
	(TLM:WorldCases). 101 and up: the test matrix, generated from the logic
	model (TLM:MatrixCases, with TLM:CaseDriver).}
	If busy
		Debug.Notification("TLM self-test is already running")
		Return
	EndIf
	busy = true
	passed = 0
	failed = 0
	firstFailure = ""
	reaches = 0
	handledBeforeReturn = 0
	int scenario = aiScenario
	If scenario < 1
		scenario = 1
	EndIf
	Debug.OpenUserLog("TLM")
	If scenario == 1
		Log("==== The Last Meridian self-test: scenario 1 (saved, delivered, posted) ====")
	Else
		Log("==== The Last Meridian self-test: scenario " + scenario + " ====")
	EndIf
	If unattended
		Log("INFO  unattended run: the game closes itself when the scenario has finished")
	EndIf

	If TLM_MQ01.GetStageDone(10) || TLM_SQ01.GetStageDone(10)
		Log("ABORTED: the quests were already started in this session.")
		Log("Quit to the main menu, start a fresh session, and run the test once.")
		If !unattended
			Debug.MessageBox("The Last Meridian self-test\n\nNot run: the quests were already started in this session. Quit to the main menu and try again in a fresh session.")
		EndIf
		busy = false
		Return
	EndIf

	Debug.Notification("TLM self-test running")
	If scenario == 1
		CheckInt("core data version", TLM_G_DataVersion.GetValueInt(), 1)
		TestMainQuest()
		TestSideQuest()
	ElseIf scenario == 2 || scenario == 3
		TLM:FixtureProbe probe = (Self as Quest) as TLM:FixtureProbe
		If !probe
			Fail("the fixture probe script is not attached to this quest")
		ElseIf scenario == 2
			probe.Run(Self)
		Else
			probe.RunDistance(Self)
		EndIf
	ElseIf scenario >= 4 && scenario <= 9
		TLM:WorldCases worldCases = (Self as Quest) as TLM:WorldCases
		If !worldCases
			Fail("the world cases script is not attached to this quest")
		ElseIf scenario == 4
			worldCases.CaseEvaded(Self)
		ElseIf scenario == 5
			worldCases.CaseFightSaved(Self)
		ElseIf scenario == 6
			worldCases.CaseMissed(Self)
		ElseIf scenario == 7
			worldCases.CaseRoadBetrayal(Self)
		ElseIf scenario == 8
			worldCases.CaseMurderAfterSaving(Self)
		Else
			worldCases.CaseDeal(Self)
		EndIf
	ElseIf scenario >= 100
		TLM:MatrixCases matrixCases = (Self as Quest) as TLM:MatrixCases
		If !matrixCases
			Fail("the generated cases script is not attached to this quest")
		Else
			matrixCases.RunCase(scenario, Self)
		EndIf
	Else
		Fail("there is no scenario " + scenario)
	EndIf

	If finished
		; Unattended, and the watchdog has already reported.
		busy = false
		Return
	EndIf
	WriteResult()
	string summary = "The Last Meridian self-test\n\n" + passed + " passed, " + failed + " failed."
	If failed > 0
		summary += "\n\nFirst failure:\n" + firstFailure
	EndIf
	If !unattended
		Debug.MessageBox(summary)
	EndIf
	busy = false
EndFunction

; ------------------------------------------------------------- scenario 1

Function TestMainQuest()
	{TLM_MQ01 with the plugin as it is now: no actors or markers exist yet, so
	every alias is empty. That is why the debrief variant is 6 ("lost": no
	Nell Fenwick alive) and not 1, exactly as the model's case T21 predicts.}
	Actor player = Game.GetPlayer()

	Log("-- MQ01: start")
	CheckFalse("MQ01 running before the start", TLM_MQ01.IsRunning())
	Reach(TLM_MQ01, 10)
	CheckTrue("MQ01 stage 10 set", TLM_MQ01.GetStageDone(10))
	CheckTrue("MQ01 running", TLM_MQ01.IsRunning())
	CheckTrue("MQ01 objective 10 displayed", TLM_MQ01.IsObjectiveDisplayed(10))
	CheckFalse("MQ01 objective 20 displayed before the dispatch", TLM_MQ01.IsObjectiveDisplayed(20))
	CheckTrue("SQ01 stage 5 set by the MQ01 start", TLM_SQ01.GetStageDone(5))
	CheckTrue("SQ01 running", TLM_SQ01.IsRunning())
	CheckInt("torn transit pass given at the start", player.GetItemCount(TornTransitPass), 1)
	CheckInt("MQ01 outcome after the start", TLM_G_CaravanOutcome.GetValueInt(), 0)

	Log("-- MQ01: dispatch taken")
	Reach(TLM_MQ01, 20)
	CheckTrue("MQ01 stage 20 set", TLM_MQ01.GetStageDone(20))
	CheckTrue("MQ01 objective 10 completed", TLM_MQ01.IsObjectiveCompleted(10))
	CheckTrue("MQ01 objective 20 displayed", TLM_MQ01.IsObjectiveDisplayed(20))

	Log("-- MQ01: ambush live, then saved")
	Reach(TLM_MQ01, 30)
	CheckTrue("MQ01 stage 30 set", TLM_MQ01.GetStageDone(30))
	CheckInt("MQ01 outcome while the ambush is live", TLM_G_CaravanOutcome.GetValueInt(), 0)
	Reach(TLM_MQ01, 31)
	CheckTrue("MQ01 stage 31 set", TLM_MQ01.GetStageDone(31))
	CheckInt("MQ01 outcome after saving", TLM_G_CaravanOutcome.GetValueInt(), 1)
	CheckInt("MQ01 method after saving", TLM_G_CaravanMethod.GetValueInt(), 0)

	Log("-- MQ01: an outcome that arrives second is ignored")
	Reach(TLM_MQ01, 32)
	CheckInt("MQ01 outcome after a second resolution", TLM_G_CaravanOutcome.GetValueInt(), 1)

	Log("-- MQ01: delivered without ever crossing the town gate")
	Reach(TLM_MQ01, 50)
	CheckTrue("MQ01 stage 50 set", TLM_MQ01.GetStageDone(50))
	CheckTrue("MQ01 stage 40 forced by the delivery", TLM_MQ01.GetStageDone(40))
	CheckTrue("MQ01 objective 20 completed", TLM_MQ01.IsObjectiveCompleted(20))
	CheckInt("MQ01 reputation", TLM_G_Rep_MercyCrossing.GetValueInt(), 2)
	CheckInt("MQ01 debrief variant", TLM_G_MQ01_DebriefVariant.GetValueInt(), 6)
	CheckInt("MQ01 caravan alive at Mercy", TLM_G_CaravanAliveAtMercy.GetValueInt(), 0)
	CheckInt("MQ01 truth after delivery", TLM_Truth.GetValueInt(), 0)
	CheckInt("MQ01 accountability after delivery", TLM_Accountability.GetValueInt(), 0)
	CheckInt("MQ01 mutual trust after delivery", TLM_MutualTrust.GetValueInt(), 0)

	Log("-- MQ01: a debrief answer this variant does not offer is ignored")
	Reach(TLM_MQ01, 52)
	CheckInt("MQ01 debrief answer after an answer not offered", TLM_G_MQ01_DebriefAnswer.GetValueInt(), 0)
	CheckInt("MQ01 truth after an answer not offered", TLM_Truth.GetValueInt(), 0)

	Log("-- MQ01: hand-off")
	Reach(TLM_MQ01, 60)
	CheckTrue("MQ01 stage 60 set", TLM_MQ01.GetStageDone(60))
	CheckTrue("MQ01 stage 100 set", TLM_MQ01.GetStageDone(100))
	CheckInt("MQ01 done", TLM_G_MQ01_Done.GetValueInt(), 1)
	CheckInt("MQ01 debrief answer after the hand-off", TLM_G_MQ01_DebriefAnswer.GetValueInt(), 9)
	CheckTrue("MQ01 completed", TLM_MQ01.IsCompleted())
	CheckInt("MQ01 reputation after the hand-off", TLM_G_Rep_MercyCrossing.GetValueInt(), 2)
EndFunction

Function TestSideQuest()
	{TLM_SQ01: a clue found before the ledger must count once the ledger is
	found (amendment A8), and only one outcome may ever be recorded.}
	Log("-- SQ01: a clue examined before the ledger")
	Reach(TLM_SQ01, 11)
	CheckTrue("SQ01 stage 11 set", TLM_SQ01.GetStageDone(11))
	CheckInt("SQ01 evidence count before the ledger", TLM_G_SQ01_EvidenceCount.GetValueInt(), 1)
	CheckInt("SQ01 evidence level before the ledger", TLM_G_SQ01_EvidenceLevel.GetValueInt(), 1)
	CheckFalse("SQ01 stage 20 before the ledger", TLM_SQ01.GetStageDone(20))

	Log("-- SQ01: ledger found")
	Reach(TLM_SQ01, 10)
	CheckTrue("SQ01 stage 10 set", TLM_SQ01.GetStageDone(10))
	CheckTrue("SQ01 stage 20 set once the ledger is found", TLM_SQ01.GetStageDone(20))
	CheckTrue("SQ01 objective 10 completed", TLM_SQ01.IsObjectiveCompleted(10))
	CheckTrue("SQ01 objective 20 displayed", TLM_SQ01.IsObjectiveDisplayed(20))
	CheckFalse("SQ01 stage 25 at evidence level 1", TLM_SQ01.GetStageDone(25))

	Log("-- SQ01: the marshal's journal")
	Reach(TLM_SQ01, 13)
	CheckInt("SQ01 evidence count with the journal", TLM_G_SQ01_EvidenceCount.GetValueInt(), 2)
	CheckInt("SQ01 evidence level with the journal", TLM_G_SQ01_EvidenceLevel.GetValueInt(), 2)
	CheckTrue("SQ01 stage 25 set at evidence level 2", TLM_SQ01.GetStageDone(25))

	Log("-- SQ01: posted, naming the Yard Office")
	Reach(TLM_SQ01, 43)
	CheckInt("SQ01 outcome", TLM_G_SQ01_Outcome.GetValueInt(), 3)
	CheckInt("total truth", TLM_Truth.GetValueInt(), 1)
	CheckInt("total competence", TLM_Competence.GetValueInt(), 1)
	CheckInt("total accountability", TLM_Accountability.GetValueInt(), 0)
	CheckInt("total mutual trust", TLM_MutualTrust.GetValueInt(), 1)
	CheckInt("SQ01 Yard alerted", TLM_G_SQ01_YardAlerted.GetValueInt(), 0)
	CheckTrue("SQ01 stage 50 set", TLM_SQ01.GetStageDone(50))
	CheckTrue("SQ01 stage 100 set", TLM_SQ01.GetStageDone(100))
	CheckTrue("SQ01 completed", TLM_SQ01.IsCompleted())

	Log("-- SQ01: a second decision is ignored")
	Reach(TLM_SQ01, 44)
	CheckInt("SQ01 outcome after a second decision", TLM_G_SQ01_Outcome.GetValueInt(), 3)
	CheckInt("SQ01 Haskell scapegoated", TLM_G_SQ01_HaskellScapegoated.GetValueInt(), 0)
	CheckInt("total truth after a second decision", TLM_Truth.GetValueInt(), 1)
EndFunction

; ----------------------------------------------------------------- helpers

Function Reach(Quest akQuest, int aiStage)
	{Sets a stage and waits until the quest reports it done. SetStage itself
	returns only after the stage's handlers have finished; the short waits are
	a margin, and they count time while the console is open.}
	If akQuest == TLM_SQ01
		Step("setting stage " + aiStage + " of the side quest")
	Else
		Step("setting stage " + aiStage + " of the main quest")
	EndIf
	int before = HandledCount(akQuest)
	akQuest.SetStage(aiStage)
	reaches += 1
	If HandledCount(akQuest) > before
		handledBeforeReturn += 1
	EndIf
	int tries = 0
	While !akQuest.GetStageDone(aiStage) && tries < 50
		Utility.WaitMenuMode(0.1)
		tries += 1
	EndWhile
	Utility.WaitMenuMode(0.25)
EndFunction

int Function HandledCount(Quest akQuest)
	{How many stage events the quest's own script has finished handling.}
	TLM:MQ01Quest mq = akQuest as TLM:MQ01Quest
	If mq
		Return mq.StageEventsHandled()
	EndIf
	TLM:SQ01Quest sq = akQuest as TLM:SQ01Quest
	If sq
		Return sq.StageEventsHandled()
	EndIf
	Return 0
EndFunction

Function CheckInt(string asName, int aiActual, int aiExpected)
	If aiActual == aiExpected
		passed += 1
		Log("PASS  " + asName + " = " + aiActual)
	Else
		Fail(asName + " = " + aiActual + ", expected " + aiExpected)
	EndIf
EndFunction

Function CheckTrue(string asName, bool abActual)
	If abActual
		passed += 1
		Log("PASS  " + asName)
	Else
		Fail(asName + ": expected true, was false")
	EndIf
EndFunction

Function CheckFalse(string asName, bool abActual)
	If !abActual
		passed += 1
		Log("PASS  not: " + asName)
	Else
		Fail(asName + ": expected false, was true")
	EndIf
EndFunction

Function Pass(string asName)
	{For a check that compares several things itself and reports once.}
	passed += 1
	Log("PASS  " + asName)
EndFunction

Function Fail(string asWhat)
	failed += 1
	Log("FAIL  " + asWhat)
	If firstFailure == ""
		firstFailure = asWhat
	EndIf
EndFunction

Function Note(string asLine)
	{A fact about the game that is reported, not scored.}
	Log("INFO  " + asLine)
EndFunction

Function Log(string asLine)
	Debug.TraceUser("TLM", asLine)
	Debug.Trace("TLM_SelfTest: " + asLine)
EndFunction
