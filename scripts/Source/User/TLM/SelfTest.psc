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

COMPILES. Ran in the game on 2026-11-12 from the console: 60 passed, 0 failed,
once the plugin's stages had been given items. (The run before reported 26
passed, 34 failed, because no OnStageSet event reached the quest scripts;
docs/design/VERIFY_LOG.md.)}

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

; ------------------------------------------------------------------- entry

Function RunSelfTest(int aiScenario = 0)
	{aiScenario is reserved. The console passes 0 when no number is given.}
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
	Debug.OpenUserLog("TLM")
	Log("==== The Last Meridian self-test: scenario 1 (saved, delivered, posted) ====")

	If TLM_MQ01.GetStageDone(10) || TLM_SQ01.GetStageDone(10)
		Log("ABORTED: the quests were already started in this session.")
		Log("Quit to the main menu, start a fresh session, and run the test once.")
		Debug.MessageBox("The Last Meridian self-test\n\nNot run: the quests were already started in this session. Quit to the main menu and try again in a fresh session.")
		busy = false
		Return
	EndIf

	Debug.Notification("TLM self-test running")
	CheckInt("core data version", TLM_G_DataVersion.GetValueInt(), 1)
	TestMainQuest()
	TestSideQuest()

	Log("INFO  stage handlers already finished when SetStage returned: " + handledBeforeReturn + " of " + reaches)
	Log("==== RESULT: " + passed + " passed, " + failed + " failed ====")
	string summary = "The Last Meridian self-test\n\n" + passed + " passed, " + failed + " failed."
	If failed > 0
		summary += "\n\nFirst failure:\n" + firstFailure
	EndIf
	Debug.MessageBox(summary)
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

Function Fail(string asWhat)
	failed += 1
	Log("FAIL  " + asWhat)
	If firstFailure == ""
		firstFailure = asWhat
	EndIf
EndFunction

Function Log(string asLine)
	Debug.TraceUser("TLM", asLine)
	Debug.Trace("TLM_SelfTest: " + asLine)
EndFunction
