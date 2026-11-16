Scriptname TLM:SQ01Quest extends Quest
{TLM_SQ01 "Signed Clean". Owns all quest logic.

COMPILES. RAN IN THE GAME on 2026-11-12 in the development self-test, with
nobody at the keyboard (docs/design/VERIFY_LOG.md): by stages alone with
every alias empty (scenario 1), and the rows of the test matrix that need no
built place, save or dialogue, 21 cases compared with the logic model after
every event (scenarios 201 to 221), with a settler made at run time as
Haskell. Every stage handler and all six outcomes have run and left the state
the logic model predicts. In those runs a stage number stood in for every
pickup, examined clue, notice board, stove and conversation. NOT run: the
clue objects and their message boxes, OnGameLoaded, dialogue, saving and
loading. Written without Fallout 4 or the Creation Kit.

Stages are the API (same pattern as TLM:MQ01Quest):
   5  running, hidden (set by MQ01 stage 10)
  10  ledger found (E0)
  11  E1 brake shoes examined     12  E2 draw-bar examined
  13  E3 marshal's journal taken  14  E4 Ada Pike's parts book seen
  20  case presentable (ledger + evidence level 1)
  25  falsification established (evidence level 2)
  41  reported   42 posted, no name   43 posted, Yard Office
  44  posted, Haskell   45 sold   46 destroyed
  50  resolved  100 completed
Evidence stages can arrive in any order, before or after the ledger.}

Group Globals
	GlobalVariable Property TLM_G_SQ01_EvidenceCount Auto Const Mandatory
	GlobalVariable Property TLM_G_SQ01_EvidenceLevel Auto Const Mandatory
	{0, 1 "the ledger is wrong", 2 "the ledger was falsified". Never names a person.}
	GlobalVariable Property TLM_G_SQ01_Outcome Auto Const Mandatory
	{0 none, 1 reported, 2 posted, 3 posted Yard Office, 4 posted Haskell, 5 sold, 6 destroyed}
	GlobalVariable Property TLM_G_SQ01_YardAlerted Auto Const Mandatory
	GlobalVariable Property TLM_G_SQ01_VaneHasLedger Auto Const Mandatory
	GlobalVariable Property TLM_G_SQ01_HaskellScapegoated Auto Const Mandatory
	GlobalVariable Property TLM_Truth Auto Const Mandatory
	GlobalVariable Property TLM_Competence Auto Const Mandatory
	GlobalVariable Property TLM_Accountability Auto Const Mandatory
	GlobalVariable Property TLM_MutualTrust Auto Const Mandatory
EndGroup

Group Aliases
	ReferenceAlias Property Alias_Haskell Auto Const Mandatory
EndGroup

Group Forms
	Form Property LedgerItem Auto Const Mandatory
	{TLM_BOOK_RailMaintLedger}
	Form Property JournalItem Auto Const Mandatory
	{TLM_BOOK_MarshalLog}
	Form Property Caps Auto Const
	{Caps001 from Fallout4.esm. Optional: no payment if empty.}
	int Property SalePrice = 120 Auto Const
	{Starting value only.}
EndGroup

int SQ_REPORTED = 1 Const
int SQ_POSTED = 2 Const
int SQ_POSTED_YARD = 3 Const
int SQ_POSTED_HASKELL = 4 Const
int SQ_SOLD = 5 Const
int SQ_DESTROYED = 6 Const

; Development aid, read through StageEventsHandled().
int handledCount = 0

Event OnStageSet(int auiStageID, int auiItemID)
	; One line per stage event in the game's script log (see TLM:MQ01Quest).
	Debug.Trace("TLM_SQ01: stage " + auiStageID + " item " + auiItemID)
	If auiStageID == 10
		SetObjectiveDisplayed(10)
		RecomputeEvidence()
	ElseIf auiStageID >= 11 && auiStageID <= 14
		RecomputeEvidence()
	ElseIf auiStageID == 20
		SetObjectiveCompleted(10)
		SetObjectiveDisplayed(20)
	ElseIf auiStageID >= 41 && auiStageID <= 46
		ApplyOutcome(auiStageID - 40)
	ElseIf auiStageID == 900
		Recover()
	EndIf
	handledCount += 1
EndEvent

int Function StageEventsHandled()
	{Development aid for the self-test: how many stage events this script has
	finished handling.}
	Return handledCount
EndFunction

int Function EvidenceLevel()
	{Design section 3.2.}
	bool e1 = GetStageDone(11)
	bool e2 = GetStageDone(12)
	bool e3 = GetStageDone(13)
	bool e4 = GetStageDone(14)
	int n = 0
	If e1
		n += 1
	EndIf
	If e2
		n += 1
	EndIf
	If e3
		n += 1
	EndIf
	If e4
		n += 1
	EndIf
	TLM_G_SQ01_EvidenceCount.SetValueInt(n)
	If n == 0
		Return 0
	EndIf
	If (e3 && n >= 2) || (e1 && e2 && e4)
		Return 2
	EndIf
	Return 1
EndFunction

Function RecomputeEvidence()
	If TLM_G_SQ01_Outcome.GetValueInt() != 0
		Return
	EndIf
	int level = EvidenceLevel()
	TLM_G_SQ01_EvidenceLevel.SetValueInt(level)
	If !GetStageDone(10)
		Return
	EndIf
	If level >= 1 && !GetStageDone(20)
		SetStage(20)
	EndIf
	If level >= 2 && !GetStageDone(25)
		SetStage(25)
	EndIf
EndFunction

Function ApplyOutcome(int aiOutcome)
	{One outcome, ever. Conditions on the dialogue and message buttons are the
	first guard; these checks are the second.}
	If TLM_G_SQ01_Outcome.GetValueInt() != 0
		Return
	EndIf
	Actor player = Game.GetPlayer()
	; Keyed on stages, not on holding the item: stage 10 is the proof the
	; player found the ledger. Removing the item below is best effort.
	If !GetStageDone(10)
		Return
	EndIf
	If aiOutcome != SQ_DESTROYED && !GetStageDone(20)
		Return
	EndIf
	If aiOutcome == SQ_POSTED_YARD && TLM_G_SQ01_EvidenceLevel.GetValueInt() < 2
		Return
	EndIf
	If aiOutcome == SQ_POSTED_HASKELL
		Actor target = Alias_Haskell.GetActorReference()
		If !target || target.IsDead()
			; Nobody left to run out of town: the pages go up with no name.
			Debug.Trace("TLM_SQ01: Haskell unavailable; posting without a name")
			aiOutcome = SQ_POSTED
		EndIf
	EndIf

	If aiOutcome == SQ_REPORTED
		TLM_G_SQ01_YardAlerted.SetValueInt(1)
		TLM_Truth.Mod(1)
		TLM_Competence.Mod(1)
	ElseIf aiOutcome == SQ_POSTED
		TLM_Truth.Mod(1)
	ElseIf aiOutcome == SQ_POSTED_YARD
		TLM_Truth.Mod(1)
		TLM_Competence.Mod(1)
		TLM_MutualTrust.Mod(1)
	ElseIf aiOutcome == SQ_POSTED_HASKELL
		Alias_Haskell.GetActorReference().Disable()
		TLM_G_SQ01_HaskellScapegoated.SetValueInt(1)
		TLM_Truth.Mod(-1)
		TLM_Competence.Mod(-1)
		TLM_Accountability.Mod(-1)
		TLM_MutualTrust.Mod(-1)
	ElseIf aiOutcome == SQ_SOLD
		If player.GetItemCount(LedgerItem) > 0
			player.RemoveItem(LedgerItem, 1, true)
		EndIf
		If player.GetItemCount(JournalItem) > 0
			player.RemoveItem(JournalItem, 1, true)
		EndIf
		If Caps
			player.AddItem(Caps, SalePrice)
		EndIf
		TLM_G_SQ01_VaneHasLedger.SetValueInt(1)
	ElseIf aiOutcome == SQ_DESTROYED
		If player.GetItemCount(LedgerItem) > 0
			player.RemoveItem(LedgerItem, 1, true)
		EndIf
		TLM_Truth.Mod(-1)
	Else
		Return
	EndIf

	TLM_G_SQ01_Outcome.SetValueInt(aiOutcome)
	SetObjectiveCompleted(10)
	SetObjectiveCompleted(20)
	SetStage(50)
	SetStage(100)
EndFunction

Function OnGameLoaded()
	If IsRunning()
		Recover()
	EndIf
EndFunction

Function Recover()
	{Re-grants the ledger if it has gone missing before a decision.
	Stage 900 calls this once; after that use: cqf TLM_SQ01 Recover}
	Actor player = Game.GetPlayer()
	If GetStageDone(10) && TLM_G_SQ01_Outcome.GetValueInt() == 0 && player.GetItemCount(LedgerItem) == 0
		player.AddItem(LedgerItem, 1, true)
		Debug.Trace("TLM_SQ01: ledger was missing; replaced")
	EndIf
	RecomputeEvidence()
EndFunction
