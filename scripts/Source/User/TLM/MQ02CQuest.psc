Scriptname TLM:MQ02CQuest extends Quest
{RED-HOLLOW-STORY-001. Persistent court, cohort, mine and evidence facts.
Requests are separate from observed results. No NPC dialogue or global clock.
Source candidate only; native compilation/geometry/hit/timer acceptance pending.}

Quest Property TLM_MQ01 Auto Const Mandatory
GlobalVariable Property TLM_G_MQ01_Done Auto Const Mandatory
Form Property DocketItem Auto Const Mandatory
Form Property LampItem Auto Const Mandatory
Form Property KeyItem Auto Const Mandatory
Form Property ReceiptItem Auto Const Mandatory
Form Property Caps Auto Const
ReferenceAlias Property Alias_Sheriff Auto Const Mandatory
ReferenceAlias Property Alias_Quill Auto Const Mandatory
ReferenceAlias Property Alias_Blevins Auto Const Mandatory
ReferenceAlias Property Alias_Roark Auto Const Mandatory
ReferenceAlias Property Alias_Dorn Auto Const Mandatory
ReferenceAlias Property Alias_Condemned Auto Const Mandatory
ReferenceAlias[] Property Miners Auto Const Mandatory
ObjectReference[] Property RHSurfaceReceipts Auto Const
ObjectReference[] Property RHOriginalMiners Auto Const
ObjectReference Property RHBelowAnchor Auto Const
ObjectReference Property RHBreakControl Auto Const
GlobalVariable Property TLM_G_MQ02C_Court Auto Const Mandatory
GlobalVariable Property TLM_G_MQ02C_Mine Auto Const Mandatory
GlobalVariable Property TLM_G_MQ02C_PrisonerRole Auto Const Mandatory
GlobalVariable Property TLM_G_MQ02C_Survivors Auto Const Mandatory
GlobalVariable Property TLM_G_MQ02C_ObservedDeaths Auto Const Mandatory
GlobalVariable Property TLM_G_MQ02C_Entombed Auto Const Mandatory
GlobalVariable Property TLM_G_MQ02C_Reported Auto Const Mandatory
GlobalVariable Property TLM_G_MQ02C_DeadlineArmed Auto Const Mandatory
GlobalVariable Property TLM_G_MQ02C_DeadlineRemaining Auto Const Mandatory
GlobalVariable Property TLM_G_MQ02C_MinePending Auto Const Mandatory
GlobalVariable Property TLM_G_MQ02C_RopeShot Auto Const Mandatory
GlobalVariable Property TLM_G_MQ02C_NeckOwed Auto Const Mandatory
GlobalVariable Property TLM_G_MQ02C_QuillShamed Auto Const Mandatory
GlobalVariable Property TLM_G_MQ02C_SilverRoad Auto Const Mandatory
GlobalVariable Property TLM_G_MQ02C_ShiftSaved Auto Const Mandatory
GlobalVariable Property TLM_G_MQ02C_HollowLine Auto Const Mandatory
GlobalVariable Property TLM_G_MQ02C_BreakBlown Auto Const Mandatory
GlobalVariable Property TLM_G_MQ02C_MouthShut Auto Const Mandatory
GlobalVariable Property TLM_G_MQ02C_LampTaken Auto Const Mandatory
GlobalVariable Property TLM_G_MQ02C_Docket2298Held Auto Const Mandatory
GlobalVariable Property TLM_G_MQ02C_SilverMine Auto Const Mandatory

; Court: 0 unsettled,1 bypassed,11 rope,12 fee,13 living review custody,14 actual execution.
int courtValue = 0
int courtIntent = 0
int prisonerRole = 0
bool prisonerStaged = false
bool shotObserved = false
bool ropeRecorded = false
bool ropeFinePaid = false
bool ropePaymentAsked = false
int ropePlayerBefore = 0
int ropeBoxBefore = 0
bool cohortFound = false
bool neckOwed = false
bool statementEstablished = false
bool roadSilver = false
bool referralPending = false
bool referralDone = false
bool feeAsked = false
bool feePaid = false
int feePlayerBefore = 0
int feeBoxBefore = 0
bool receiptAsked = false
bool receiptGiven = false
bool tollAsked = false
bool tollPaid = false
int tollPlayerBefore = 0
int tollBoxBefore = 0
bool executionAsked = false
bool executionObserved = false
bool courtWatching = false
float courtRemaining = 15.0

; Mine: 0 unsettled; terminal51/52/53/56/57/58. Pending1 descent,2 rescue,
; 3 inner break,4 player-order Mouth,5 deadline Mouth,6 ordinary return.
int mineValue = 0
int mineIntent = 0
bool rescueCommissioned = false
bool knockingHeard = false
bool warningAccepted = false
bool deadlineArmed = false
bool deadlineBlocked = false
float deadlineSeconds = 600.0
bool playerOrdered = false
bool pactAcknowledged = false
bool termsPending = false
bool termsAcknowledged = false
bool breakPlan = false
bool innerClosed = false
bool mouthClosed = false
bool dornWithdrawn = false
bool shiftEverSafe = false
bool keyAsked = false
bool keyGiven = false
bool lampAsked = false
int lampSource = 0
bool lampGiven = false
bool mineSilver = false
bool reported = false
int[] minerFates
; 1 supplied player, 2 supplied nonplayer killer, 3 unknown; inspection is not attribution.
int[] minerDeathCauses
int[] minerArrivedAlive
bool[] minerDeathEventSeen
Actor[] minerDeathEventActors

bool Function PlayerAlive()
	Actor currentPlayer = Game.GetPlayer()
	Return currentPlayer && !currentPlayer.IsDead()
EndFunction

bool Function Commissioned()
	Return TLM_MQ01 && TLM_MQ01.GetStageDone(100) && TLM_G_MQ01_Done.GetValueInt() == 1 && PlayerAlive()
EndFunction

bool Function Open()
	Return IsRunning() && GetStageDone(10) && PlayerAlive()
EndFunction

Actor Function Person(ReferenceAlias a)
	If !a
		Return None
	EndIf
	Return a.GetActorReference()
EndFunction

bool Function Speaking(ReferenceAlias a)
	Actor whoActor = Person(a)
	Return whoActor && !whoActor.IsDead() && !whoActor.IsDisabled() && !whoActor.IsInCombat()
EndFunction

bool Function At(ObjectReference whoRef, ObjectReference placeRef, float reach = 128.0)
	Return whoRef && placeRef && !whoRef.IsDisabled() && whoRef.GetParentCell() == placeRef.GetParentCell() && whoRef.GetDistance(placeRef) <= reach
EndFunction

bool Function On(ObjectReference placedRef)
	Return placedRef && !placedRef.IsDisabled() && placedRef.Is3DLoaded()
EndFunction

bool Function Off(ObjectReference placedRef)
	Return placedRef && placedRef.IsDisabled()
EndFunction

Function EnsureRoster()
	If !minerFates
		minerFates = new int[11]
		minerDeathCauses = new int[11]
		minerArrivedAlive = new int[11]
		minerDeathEventSeen = new bool[11]
		minerDeathEventActors = new Actor[11]
	EndIf
EndFunction

Actor Function Miner(int minerIndex)
	If !Miners || Miners.Length != 11 || minerIndex < 0 || minerIndex >= 11 || !Miners[minerIndex]
		Return None
	EndIf
	Return Miners[minerIndex].GetActorReference()
EndFunction

bool Function DistinctRoster()
	If !Miners || Miners.Length != 11 || !RHOriginalMiners || RHOriginalMiners.Length != 11
		Return false
	EndIf
	int outerIndex = 0
	While outerIndex < 11
		Actor outerActor = Miner(outerIndex)
		If !outerActor || outerActor != RHOriginalMiners[outerIndex]
			Return false
		EndIf
		int innerIndex = 0
		While innerIndex < outerIndex
			If Miner(innerIndex) == outerActor
				Return false
			EndIf
			innerIndex += 1
		EndWhile
		outerIndex += 1
	EndWhile
	Return true
EndFunction

Function RecordDeathEvent(int minerIndex, Actor eventActor, int causeCode)
	EnsureRoster()
	If minerIndex < 0 || minerIndex >= 11 || !eventActor || eventActor != Miner(minerIndex) || !eventActor.IsDead()
		Return
	EndIf
	minerDeathEventSeen[minerIndex] = true
	minerDeathEventActors[minerIndex] = eventActor
	If causeCode == 1 || causeCode == 2
		minerDeathCauses[minerIndex] = causeCode
	ElseIf minerDeathCauses[minerIndex] == 0
		minerDeathCauses[minerIndex] = 3
	EndIf
EndFunction

bool Function ObserveDeliveredDeath(int minerIndex)
	EnsureRoster()
	Actor deadActor = Miner(minerIndex)
	If !deadActor || !minerDeathEventSeen[minerIndex] || minerDeathEventActors[minerIndex] != deadActor || !deadActor.IsDead()
		Return false
	EndIf
	ObserveDeath(minerIndex)
	Return Fate(minerIndex) == 4
EndFunction

Function ObserveDeath(int minerIndex, bool byPlayer = false)
	EnsureRoster()
	Actor deadActor = Miner(minerIndex)
	If deadActor && deadActor.IsDead()
		minerFates[minerIndex] = 4
		If byPlayer
			minerDeathCauses[minerIndex] = 1
		ElseIf minerDeathCauses[minerIndex] == 0
			; A corpse proves death, not a killer. Preserve any genuinely supplied cause.
			minerDeathCauses[minerIndex] = 3
		EndIf
	EndIf
EndFunction

int Function Fate(int minerIndex)
	EnsureRoster()
	Return minerFates[minerIndex]
EndFunction

bool Function ObserveAt(int minerIndex, ObjectReference slotRef, int newFate)
	EnsureRoster()
	Actor minerActor = Miner(minerIndex)
	If !minerActor || minerActor.IsDead() || !At(minerActor, slotRef)
		Return false
	EndIf
	minerFates[minerIndex] = newFate
	If newFate == 3
		minerArrivedAlive[minerIndex] = 1
	EndIf
	Return true
EndFunction

int Function DeathCount()
	EnsureRoster()
	int resultCount = 0
	int minerIndex = 0
	While minerIndex < 11
		If minerFates[minerIndex] == 4 && Miner(minerIndex) && Miner(minerIndex).IsDead()
			resultCount += 1
		EndIf
		minerIndex += 1
	EndWhile
	Return resultCount
EndFunction

int Function SafeCount(ReferenceAlias[] surfaceSlots)
	EnsureRoster()
	If !surfaceSlots || surfaceSlots.Length != 11 || !DistinctRoster()
		Return 0
	EndIf
	int resultCount = 0
	int minerIndex = 0
	While minerIndex < 11
		Actor minerActor = Miner(minerIndex)
		If minerActor && !minerActor.IsDead() && At(minerActor, surfaceSlots[minerIndex].GetReference())
			minerFates[minerIndex] = 3
			resultCount += 1
		EndIf
		minerIndex += 1
	EndWhile
	Return resultCount
EndFunction

bool Function KnownSafeSurvivors(ReferenceAlias[] surfaceSlots)
	EnsureRoster()
	If !surfaceSlots || surfaceSlots.Length != 11 || !DistinctRoster()
		Return false
	EndIf
	int minerIndex = 0
	While minerIndex < 11
		Actor minerActor = Miner(minerIndex)
		If minerFates[minerIndex] == 4
			If !minerActor || !minerActor.IsDead()
				Return false
			EndIf
		ElseIf !minerActor || minerActor.IsDead() || !At(minerActor, surfaceSlots[minerIndex].GetReference())
			Return false
		EndIf
		minerIndex += 1
	EndWhile
	Return true
EndFunction

bool Function AllBelow(ReferenceAlias[] belowSlots, ReferenceAlias[] cageSlots)
	If !belowSlots || !cageSlots || belowSlots.Length != 11 || cageSlots.Length != 11 || !DistinctRoster()
		Return false
	EndIf
	int minerIndex = 0
	While minerIndex < 11
		Actor minerActor = Miner(minerIndex)
		If !At(minerActor, belowSlots[minerIndex].GetReference(), 160.0) && !At(minerActor, cageSlots[minerIndex].GetReference(), 160.0)
			Return false
		EndIf
		minerIndex += 1
	EndWhile
	Return true
EndFunction

bool Function AllAliveBelow(ReferenceAlias[] belowSlots)
	If !DistinctRoster() || !belowSlots || belowSlots.Length != 11
		Return false
	EndIf
	int minerIndex = 0
	While minerIndex < 11
		Actor minerActor = Miner(minerIndex)
		If minerActor.IsDead() || !At(minerActor, belowSlots[minerIndex].GetReference(), 192.0)
			Return false
		EndIf
		minerIndex += 1
	EndWhile
	Return true
EndFunction

Function RefreshEvidence(TLM:MercyBriefing briefingScript)
	Actor currentPlayer = Game.GetPlayer()
	If !currentPlayer
		Return
	EndIf
	bool needsHistory = briefingScript && briefingScript.WasCopyIssued() && !GetStageDone(16)
	If needsHistory && !IsRunning()
		If !Start() || !IsRunning()
			Return
		EndIf
	EndIf
	TLM_G_MQ02C_Docket2298Held.SetValueInt((currentPlayer.GetItemCount(DocketItem) > 0) as int)
	TLM_G_MQ02C_LampTaken.SetValueInt((currentPlayer.GetItemCount(LampItem) > 0) as int)
	If needsHistory && IsRunning()
		SetStage(16)
	EndIf
EndFunction

bool Function HoldsDocket()
	Return Game.GetPlayer() && Game.GetPlayer().GetItemCount(DocketItem) > 0
EndFunction

bool Function ArriveAtGap(ObjectReference gapRef)
	If !Commissioned() || !At(Game.GetPlayer(), gapRef)
		Return false
	EndIf
	EnsureRoster()
	SetStage(10)
	Publish()
	Return true
EndFunction

bool Function BindPrisoner(Actor prisonerActor, int originalRole, ObjectReference gallowsRef)
	If prisonerStaged
		Return Person(Alias_Condemned) == prisonerActor
	EndIf
	TLM:MQ01Quest earlierQuest = TLM_MQ01 as TLM:MQ01Quest
	If !IsRunning() || courtValue != 0 || courtIntent != 0 || !earlierQuest || !Commissioned() || !prisonerActor || prisonerActor.IsDead() || prisonerActor.IsInCombat()
		Return false
	EndIf
	If prisonerActor != earlierQuest.Alias_CutterLead.GetActorReference() && prisonerActor != earlierQuest.Alias_CutterA.GetActorReference() && prisonerActor != earlierQuest.Alias_CutterB.GetActorReference() && prisonerActor != earlierQuest.Alias_CutterC.GetActorReference()
		Return false
	EndIf
	If !At(prisonerActor, gallowsRef)
		Return false
	EndIf
	Alias_Condemned.ForceRefTo(prisonerActor)
	If Person(Alias_Condemned) != prisonerActor
		Return false
	EndIf
	prisonerRole = originalRole
	prisonerStaged = true
	Publish()
	Return true
EndFunction

int Function PrisonerIdentity()
	Return prisonerRole
EndFunction

bool Function CourtOpen()
	Return Open() && courtValue == 0 && prisonerStaged && Speaking(Alias_Condemned)
EndFunction

int Function CourtMark()
	Return courtValue + courtIntent * 100 + prisonerRole * 1000
EndFunction

int Function CourtOutcome()
	Return courtValue
EndFunction

int Function CourtPending()
	Return courtIntent
EndFunction

Function Bypass()
	If Open() && courtValue == 0 && courtIntent == 0
		courtValue = 1
		courtWatching = false
		Publish()
	EndIf
EndFunction

bool Function StartRope(ObjectReference ropeRef, bool eligibleProjectile)
	If !CourtOpen() || courtIntent != 0 || !eligibleProjectile || !On(ropeRef)
		Return false
	EndIf
	courtIntent = 11
	shotObserved = true
	courtWatching = false
	Return true
EndFunction

bool Function FinishRelease(ObjectReference releaseRef, ObjectReference ropeRef, ObjectReference brokenRef)
	Actor prisonerActor = Person(Alias_Condemned)
	If !Open() || !prisonerActor || prisonerActor.IsDead() || !At(prisonerActor, releaseRef)
		Return false
	EndIf
	If courtIntent == 11
		If !shotObserved || !Off(ropeRef) || !On(brokenRef)
			Return false
		EndIf
		courtValue = 11
		SetStage(11)
	ElseIf courtIntent == 12
		If !feePaid || !receiptGiven || !Speaking(Alias_Quill)
			Return false
		EndIf
		courtValue = 12
		SetStage(12)
	Else
		Return false
	EndIf
	courtIntent = 0
	neckOwed = true
	Publish()
	Return true
EndFunction

bool Function ObserveFee(ObjectReference paymentBox)
	If feePaid
		Return true
	EndIf
	If feeAsked && paymentBox && Game.GetPlayer().GetItemCount(Caps) <= feePlayerBefore - 60 && paymentBox.GetItemCount(Caps) >= feeBoxBefore + 60
		feePaid = true
	EndIf
	Return feePaid
EndFunction

bool Function StartFine(ObjectReference paymentBox)
	If courtIntent == 12
		Return ObserveFee(paymentBox)
	EndIf
	If !CourtOpen() || courtIntent != 0 || !Speaking(Alias_Quill) || !paymentBox || !Caps || Game.GetPlayer().GetItemCount(Caps) < 60 || feeAsked
		Return false
	EndIf
	courtIntent = 12
	feeAsked = true
	feePlayerBefore = Game.GetPlayer().GetItemCount(Caps)
	feeBoxBefore = paymentBox.GetItemCount(Caps)
	Game.GetPlayer().RemoveItem(Caps, 60, true, paymentBox)
	Return ObserveFee(paymentBox)
EndFunction

bool Function GiveReceipt()
	If !feePaid || !PlayerAlive() || !Speaking(Alias_Quill)
		Return false
	EndIf
	If Game.GetPlayer().GetItemCount(ReceiptItem) > 0
		receiptGiven = true
		Return true
	EndIf
	If !receiptAsked
		receiptAsked = true
		Game.GetPlayer().AddItem(ReceiptItem, 1, true)
	EndIf
	receiptGiven = Game.GetPlayer().GetItemCount(ReceiptItem) > 0
	Return receiptGiven && PlayerAlive() && Speaking(Alias_Quill)
EndFunction

bool Function PayToll(ObjectReference paymentBox)
	If tollPaid
		Return true
	EndIf
	If tollAsked
		tollPaid = paymentBox && Game.GetPlayer().GetItemCount(Caps) <= tollPlayerBefore - 2 && paymentBox.GetItemCount(Caps) >= tollBoxBefore + 2
		Return tollPaid
	EndIf
	If !Open() || !paymentBox || !Caps || Game.GetPlayer().GetItemCount(Caps) < 2
		Return false
	EndIf
	tollAsked = true
	tollPlayerBefore = Game.GetPlayer().GetItemCount(Caps)
	tollBoxBefore = paymentBox.GetItemCount(Caps)
	Game.GetPlayer().RemoveItem(Caps, 2, true, paymentBox)
	Return PayToll(paymentBox)
EndFunction

bool Function StartAdjournment()
	If !CourtOpen() || courtIntent != 0 || !Speaking(Alias_Quill) || !HoldsDocket()
		Return false
	EndIf
	courtIntent = 13
	courtWatching = false
	Return true
EndFunction

bool Function FinishAdjournment(ObjectReference custodyRef)
	If !Open() || courtIntent != 13 || !HoldsDocket() || !Speaking(Alias_Quill) || !Speaking(Alias_Condemned) || !At(Person(Alias_Condemned), custodyRef)
		Return false
	EndIf
	courtValue = 13
	courtIntent = 0
	referralPending = true
	SetStage(13)
	Publish()
	Return true
EndFunction

bool Function ReferralDue()
	Return courtValue == 13 && referralPending && !referralDone
EndFunction

bool Function FinishReferral(ObjectReference referredRecord)
	If !Open() || !ReferralDue() || !Speaking(Alias_Quill) || !Speaking(Alias_Condemned) || !HoldsDocket() || !On(referredRecord)
		Return false
	EndIf
	referralDone = true
	referralPending = false
	Publish()
	Return true
EndFunction

bool Function RecordRope(ObjectReference recordRef)
	If !Open() || courtValue != 11 || !shotObserved || !Speaking(Alias_Quill) || !On(recordRef)
		Return false
	EndIf
	ropeRecorded = true
	Publish()
	Return true
EndFunction

bool Function PayRope(ObjectReference paymentBox)
	If ropeFinePaid
		Return true
	EndIf
	If !Open() || !ropeRecorded || !Speaking(Alias_Quill) || !paymentBox || !Caps
		Return false
	EndIf
	If !ropePaymentAsked
		If Game.GetPlayer().GetItemCount(Caps) < 4
			Return false
		EndIf
		ropePaymentAsked = true
		ropePlayerBefore = Game.GetPlayer().GetItemCount(Caps)
		ropeBoxBefore = paymentBox.GetItemCount(Caps)
		Game.GetPlayer().RemoveItem(Caps, 4, true, paymentBox)
	EndIf
	ropeFinePaid = Game.GetPlayer().GetItemCount(Caps) <= ropePlayerBefore - 4 && paymentBox.GetItemCount(Caps) >= ropeBoxBefore + 4
	Return ropeFinePaid
EndFunction

bool Function RecordStatement(bool readTranscript = false)
	If !Open() || !prisonerStaged
		Return false
	EndIf
	If readTranscript
		If !statementEstablished
			Return false
		EndIf
	ElseIf !Speaking(Alias_Condemned)
		Return false
	EndIf
	statementEstablished = true
	roadSilver = true
	SetStage(15)
	Publish()
	Return true
EndFunction

bool Function HasStatement()
	Return statementEstablished
EndFunction

bool Function BeginWatch()
	If !CourtOpen() || courtIntent != 0 || !Speaking(Alias_Quill)
		Return false
	EndIf
	courtWatching = true
	courtRemaining = 15.0
	Return true
EndFunction

bool Function Watching()
	Return courtWatching
EndFunction

float Function CourtSeconds()
	Return courtRemaining
EndFunction

bool Function TickCourt(float elapsedSeconds)
	If !CourtOpen() || !Speaking(Alias_Quill) || courtIntent != 0 || !courtWatching
		Return false
	EndIf
	courtRemaining -= elapsedSeconds
	Return courtRemaining <= 0.0
EndFunction

bool Function BeginExecution()
	If !CourtOpen() || !Speaking(Alias_Quill) || !courtWatching || courtRemaining > 0.0 || courtIntent != 0
		Return false
	EndIf
	courtIntent = 14
	courtWatching = false
	Return true
EndFunction

bool Function RequestExecution()
	If !Open() || courtIntent != 14 || !Speaking(Alias_Quill) || !Speaking(Alias_Condemned)
		Return false
	EndIf
	executionAsked = true
	; All four actual MQ01 candidates are Protected aliases. This single
	; acknowledged sentence can release actor protection, never its old alias.
	Actor condemnedActor = Person(Alias_Condemned)
	condemnedActor.SetProtected(false)
	condemnedActor.Kill(Person(Alias_Quill))
	If !condemnedActor.IsDead()
		condemnedActor.SetProtected(true)
	EndIf
	Return true
EndFunction

bool Function FinishExecution(ObjectReference gallowsRef)
	Actor prisonerActor = Person(Alias_Condemned)
	If !Open() || courtIntent != 14 || !executionAsked || !prisonerActor || !prisonerActor.IsDead() || !At(prisonerActor,gallowsRef) || !Speaking(Alias_Quill)
		Return false
	EndIf
	executionObserved = true
	courtValue = 14
	courtIntent = 0
	SetStage(14)
	Publish()
	Return true
EndFunction

int Function MineOutcome()
	Return mineValue
EndFunction

int Function MinePending()
	Return mineIntent
EndFunction

int Function MineMark()
	Return mineValue + mineIntent * 100 + (pactAcknowledged as int) * 1000 + (breakPlan as int) * 10000
EndFunction

bool Function RescueAccepted()
	Return rescueCommissioned
EndFunction

bool Function PactMade()
	Return pactAcknowledged
EndFunction

bool Function BreakPlanned()
	Return breakPlan
EndFunction

bool Function OperatorReady(ObjectReference controlRef)
	Actor operatorActor = Person(Alias_Blevins)
	Return Open() && On(controlRef) && Speaking(Alias_Blevins) && operatorActor.Is3DLoaded() && At(operatorActor,controlRef,192.0) && operatorActor.GetItemCount(KeyItem) > 0
EndFunction

bool Function GiveKey()
	Actor operatorActor = Person(Alias_Blevins)
	If !operatorActor || operatorActor.IsDead()
		Return false
	EndIf
	If operatorActor.GetItemCount(KeyItem) > 0
		keyGiven = true
		Return true
	EndIf
	If !keyAsked
		keyAsked = true
		operatorActor.AddItem(KeyItem,1,true)
	EndIf
	keyGiven = operatorActor.GetItemCount(KeyItem) > 0
	Return keyGiven
EndFunction

bool Function TakeBodyKey()
	Actor operatorActor = Person(Alias_Blevins)
	If !Open() || !operatorActor || !operatorActor.IsDead() || operatorActor.GetItemCount(KeyItem) < 1
		Return false
	EndIf
	operatorActor.RemoveItem(KeyItem,1,true,Game.GetPlayer())
	Return Game.GetPlayer().GetItemCount(KeyItem) > 0 && operatorActor.GetItemCount(KeyItem) == 0
EndFunction

bool Function HearKnocking()
	If !Open() || mineValue != 0 || mouthClosed
		Return false
	EndIf
	knockingHeard = true
	If !GetStageDone(20)
		SetStage(20)
	EndIf
	Return true
EndFunction

bool Function HeardKnocking()
	Return knockingHeard
EndFunction

bool Function AcceptRescue(bool armDeadline, ObjectReference controlRef)
	If !Open() || !knockingHeard || mineValue != 0 || mineIntent != 0
		Return false
	EndIf
	If armDeadline && !OperatorReady(controlRef)
		Return false
	EndIf
	rescueCommissioned = true
	If armDeadline
		warningAccepted = true
		deadlineArmed = true
		deadlineBlocked = false
		If deadlineSeconds <= 0.0
			deadlineSeconds = 30.0
		EndIf
		SetStage(30)
	EndIf
	Publish()
	Return true
EndFunction

bool Function Armed()
	Return deadlineArmed && !deadlineBlocked && mineValue == 0
EndFunction

float Function SecondsLeft()
	Return deadlineSeconds
EndFunction

bool Function TickDeadline(float elapsedSeconds)
	If !Armed() || mineIntent != 0 || !warningAccepted || !rescueCommissioned || elapsedSeconds <= 0.0 || elapsedSeconds > 2.5
		Return false
	EndIf
	deadlineSeconds -= elapsedSeconds
	Publish()
	Return deadlineSeconds <= 0.0
EndFunction

Function BlockDeadline()
	deadlineBlocked = true
	Publish()
EndFunction

bool Function BeginDescent()
	If !Open() || !rescueCommissioned || mineValue != 0 || mineIntent != 0 || mouthClosed
		Return false
	EndIf
	mineIntent = 1
	Publish()
	Return true
EndFunction

bool Function FinishDescent(ObjectReference belowRef)
	If !Open() || mineIntent != 1 || !At(Game.GetPlayer(),belowRef)
		Return false
	EndIf
	mineIntent = 0
	SetStage(40)
	Publish()
	Return true
EndFunction

bool Function FindShift(ReferenceAlias[] belowSlots)
	If !Open() || !GetStageDone(40) || !DistinctRoster() || !belowSlots || belowSlots.Length != 11
		Return false
	EndIf
	int minerIndex = 0
	While minerIndex < 11
		Actor minerActor = Miner(minerIndex)
		If minerActor.IsDead()
			If Fate(minerIndex) != 4
				Return false
			EndIf
		ElseIf !At(minerActor,belowSlots[minerIndex].GetReference())
			Return false
		EndIf
		minerIndex += 1
	EndWhile
	cohortFound = true
	If AllAliveBelow(belowSlots)
		SetStage(45)
	EndIf
	Return true
EndFunction

bool Function ShiftFound()
	Return cohortFound
EndFunction

bool Function BeginRescue()
	If !Open() || !rescueCommissioned || !cohortFound || mouthClosed || mineValue != 0 || !DistinctRoster()
		Return false
	EndIf
	If mineIntent == 2
		Return true
	EndIf
	If mineIntent != 0
		Return false
	EndIf
	mineIntent = 2
	Publish()
	Return true
EndFunction

bool Function FinishRescue(ReferenceAlias[] surfaceSlots)
	If !Open() || mineIntent != 2 || !KnownSafeSurvivors(surfaceSlots)
		Return false
	EndIf
	mineIntent = 0
	If SafeCount(surfaceSlots) == 11
		shiftEverSafe = true
		If pactAcknowledged && !breakPlan
			mineValue = 51
			SetStage(51)
		EndIf
	EndIf
	Publish()
	Return true
EndFunction

bool Function MakePact()
	If !Open() || !Speaking(Alias_Dorn) || dornWithdrawn || mineValue != 0 || mineIntent != 0 || !GetStageDone(50)
		Return false
	EndIf
	pactAcknowledged = true
	termsPending = true
	breakPlan = false
	Publish()
	Return true
EndFunction

bool Function PlanBreak()
	If !Open() || mineValue != 0 || mineIntent != 0 || pactAcknowledged
		Return false
	EndIf
	breakPlan = true
	Return true
EndFunction

bool Function ResolveRescue(ReferenceAlias[] surfaceSlots, bool abandonBreak)
	If !Open() || mineValue != 0 || mineIntent != 0 || !shiftEverSafe || !KnownSafeSurvivors(surfaceSlots) || pactAcknowledged
		Return false
	EndIf
	If breakPlan && !abandonBreak
		Return false
	EndIf
	breakPlan = false
	mineValue = 57
	SetStage(57)
	Publish()
	Return true
EndFunction

bool Function ResolveCasualties(ReferenceAlias[] surfaceSlots)
	If !Open() || mineValue != 0 || mineIntent != 0 || shiftEverSafe || DeathCount() < 1 || !KnownSafeSurvivors(surfaceSlots)
		Return false
	EndIf
	mineValue = 58
	breakPlan = false
	SetStage(58)
	Publish()
	Return true
EndFunction

bool Function BeginBreak(ReferenceAlias[] surfaceSlots)
	If !Open() || mineIntent != 0 || !KnownSafeSurvivors(surfaceSlots) || (mineValue != 0 && mineValue != 58)
		Return false
	EndIf
	If mineValue == 0 && (!breakPlan || !shiftEverSafe)
		Return false
	EndIf
	mineIntent = 3
	Publish()
	Return true
EndFunction

bool Function ClearBlastArea(ObjectReference blastRef, ReferenceAlias[] surfaceSlots, ObjectReference controlRef, ObjectReference belowRef)
	If !blastRef || !controlRef || !belowRef || !surfaceSlots || surfaceSlots.Length != 11 || !RHSurfaceReceipts || RHSurfaceReceipts.Length != 11 || !DistinctRoster() || !PlayerAlive()
		Return false
	EndIf
	If belowRef != RHBelowAnchor || controlRef != RHBreakControl || !RHSurfaceReceipts[0] || RHSurfaceReceipts[0].GetParentCell() == belowRef.GetParentCell() || blastRef.GetParentCell() != belowRef.GetParentCell() || controlRef.GetParentCell() != belowRef.GetParentCell() || !At(Game.GetPlayer(),controlRef,256.0)
		Return false
	EndIf
	int minerIndex = 0
	While minerIndex < 11
		Actor minerActor = Miner(minerIndex)
		If !minerActor || minerActor.IsDisabled() || !surfaceSlots[minerIndex]
			Return false
		EndIf
		ObjectReference safeSlot = surfaceSlots[minerIndex].GetReference()
		If !safeSlot || safeSlot != RHSurfaceReceipts[minerIndex] || !RHSurfaceReceipts[0] || safeSlot.GetParentCell() != RHSurfaceReceipts[0].GetParentCell()
			Return false
		EndIf
		If (Fate(minerIndex) != 3 && Fate(minerIndex) != 4) || (Fate(minerIndex) == 3 && (minerActor.IsDead() || !At(minerActor,safeSlot))) || (Fate(minerIndex) == 4 && !minerActor.IsDead())
			Return false
		EndIf
		If minerActor.GetParentCell() == blastRef.GetParentCell()
			If minerActor.GetDistance(blastRef) < 512.0
				Return false
			EndIf
		ElseIf safeSlot.GetParentCell() == blastRef.GetParentCell() || !At(minerActor,safeSlot) || (Fate(minerIndex) != 3 && Fate(minerIndex) != 4) || (Fate(minerIndex) == 3 && minerActor.IsDead()) || (Fate(minerIndex) == 4 && !minerActor.IsDead())
			Return false
		EndIf
		minerIndex += 1
	EndWhile
	If Game.GetPlayer().GetDistance(blastRef) < 512.0
		Return false
	EndIf
	; The eleven native receipt reads can yield. Revalidate the current
	; underground operator context after them, before any caller's effect.
	Return blastRef.GetParentCell() == belowRef.GetParentCell() && controlRef.GetParentCell() == belowRef.GetParentCell() && At(Game.GetPlayer(),controlRef,256.0) && PlayerAlive()
EndFunction

bool Function FinishBreak(ObjectReference openRef, ObjectReference closedRef, ObjectReference blastRef, ReferenceAlias[] surfaceSlots, ObjectReference controlRef, ObjectReference belowRef)
	If !Open() || mineIntent != 3 || !KnownSafeSurvivors(surfaceSlots) || !ClearBlastArea(blastRef,surfaceSlots,controlRef,belowRef) || !Off(openRef) || !On(closedRef)
		Return false
	EndIf
	innerClosed = true
	mineIntent = 0
	If mineValue != 58
		mineValue = 52
		SetStage(52)
	EndIf
	Publish()
	Return true
EndFunction

bool Function BeginFire(bool ordered, ObjectReference controlRef, ReferenceAlias[] belowSlots, ReferenceAlias[] cageSlots, ObjectReference openRef, ObjectReference closedRef)
	If !Open() || !On(openRef) || !Off(closedRef) || !knockingHeard || !warningAccepted || !OperatorReady(controlRef) || mineValue != 0 || mineIntent != 0 || !AllBelow(belowSlots,cageSlots)
		Return false
	EndIf
	If !ordered && (!Armed() || deadlineSeconds > 0.0)
		Return false
	EndIf
	If ordered
		mineIntent = 4
	Else
		mineIntent = 5
	EndIf
	playerOrdered = ordered
	Publish()
	Return true
EndFunction

bool Function FinishFire(ObjectReference controlRef, ObjectReference openRef, ObjectReference closedRef, ObjectReference safePlayerRef, ReferenceAlias[] belowSlots, ReferenceAlias[] cageSlots)
	If !Open() || (mineIntent != 4 && mineIntent != 5) || !OperatorReady(controlRef) || !AllBelow(belowSlots,cageSlots) || !At(Game.GetPlayer(),safePlayerRef) || !Off(openRef) || !On(closedRef)
		Return false
	EndIf
	mouthClosed = true
	If mineIntent == 4
		mineValue = 53
	Else
		mineValue = 56
	EndIf
	mineIntent = 0
	deadlineArmed = false
	EnsureRoster()
	int minerIndex = 0
	While minerIndex < 11
		If minerFates[minerIndex] != 4
			minerFates[minerIndex] = 5
		EndIf
		minerIndex += 1
	EndWhile
	SetStage(mineValue)
	Publish()
	Return true
EndFunction

Function AbortDisabledFire(ObjectReference controlRef)
	If (mineIntent == 4 || mineIntent == 5) && !OperatorReady(controlRef)
		mineIntent = 0
		deadlineBlocked = true
		Publish()
	EndIf
EndFunction

bool Function VisitGallery(ObjectReference galleryRef)
	If !Open() || !GetStageDone(40) || innerClosed || mouthClosed || !At(Game.GetPlayer(),galleryRef)
		Return false
	EndIf
	SetStage(50)
	Return true
EndFunction

Function WithdrawDorn()
	dornWithdrawn = true
EndFunction

bool Function DornAvailable()
	Return Open() && Speaking(Alias_Dorn) && !dornWithdrawn && !innerClosed
EndFunction

bool Function GiveLamp(int originCode)
	If !Open() || (originCode != 1 && originCode != 2)
		Return false
	EndIf
	If lampAsked
		If lampGiven
			Return false
		EndIf
		If Game.GetPlayer().GetItemCount(LampItem) > 0
			lampGiven = true
			SetStage(54)
			Publish()
			Return true
		EndIf
		Return false
	EndIf
	lampAsked = true
	lampSource = originCode
	Game.GetPlayer().AddItem(LampItem,1,true)
	If !PlayerAlive()
		Return false
	EndIf
	lampGiven = Game.GetPlayer().GetItemCount(LampItem) > 0
	If lampGiven
		SetStage(54)
		Publish()
	EndIf
	Return lampGiven
EndFunction

int Function LampOrigin()
	Return lampSource
EndFunction

bool Function LearnMineSilver()
	If !Open()
		Return false
	EndIf
	mineSilver = true
	SetStage(60)
	Publish()
	Return true
EndFunction

bool Function KnowsMineSilver()
	Return mineSilver
EndFunction

bool Function DeliverTerms()
	If !Open() || !pactAcknowledged || !termsPending || !Speaking(Alias_Roark)
		Return false
	EndIf
	termsPending = false
	termsAcknowledged = true
	Return true
EndFunction

bool Function TermsDelivered()
	Return termsAcknowledged
EndFunction

bool Function CompleteAtMercy(ObjectReference mercyRef)
	If !Open() || mineValue == 0 || mineIntent != 0 || !At(Game.GetPlayer(),mercyRef)
		Return false
	EndIf
	SetStage(100)
	Return true
EndFunction

bool Function ReportDue()
	Return GetStageDone(100) && !reported
EndFunction

bool Function RecordHollowReport(Actor sheriffActor)
	If !ReportDue() || !PlayerAlive() || sheriffActor != Person(Alias_Sheriff) || !Speaking(Alias_Sheriff)
		Return false
	EndIf
	reported = true
	Publish()
	Return true
EndFunction

Function Publish()
	TLM_G_MQ02C_Court.SetValueInt(courtValue)
	TLM_G_MQ02C_Mine.SetValueInt(mineValue)
	TLM_G_MQ02C_PrisonerRole.SetValueInt(prisonerRole)
	TLM_G_MQ02C_MinePending.SetValueInt(mineIntent)
	TLM_G_MQ02C_Reported.SetValueInt(reported as int)
	TLM_G_MQ02C_DeadlineArmed.SetValueInt(Armed() as int)
	TLM_G_MQ02C_DeadlineRemaining.SetValueInt(deadlineSeconds as int)
	TLM_G_MQ02C_RopeShot.SetValueInt((shotObserved && ropeRecorded) as int)
	TLM_G_MQ02C_NeckOwed.SetValueInt(neckOwed as int)
	TLM_G_MQ02C_QuillShamed.SetValueInt((courtValue == 13 && referralDone) as int)
	TLM_G_MQ02C_SilverRoad.SetValueInt(roadSilver as int)
	TLM_G_MQ02C_ShiftSaved.SetValueInt(shiftEverSafe as int)
	TLM_G_MQ02C_HollowLine.SetValueInt(pactAcknowledged as int)
	TLM_G_MQ02C_BreakBlown.SetValueInt(innerClosed as int)
	TLM_G_MQ02C_MouthShut.SetValueInt(mouthClosed as int)
	TLM_G_MQ02C_SilverMine.SetValueInt(mineSilver as int)
	TLM_G_MQ02C_ObservedDeaths.SetValueInt(DeathCount())
	int entombedCount = 0
	int minerIndex = 0
	While minerIndex < 11
		If minerFates[minerIndex] == 5
			entombedCount += 1
		EndIf
		minerIndex += 1
	EndWhile
	TLM_G_MQ02C_Entombed.SetValueInt(entombedCount)
EndFunction

Function PublishSurvivors(ReferenceAlias[] surfaceSlots)
	TLM_G_MQ02C_Survivors.SetValueInt(SafeCount(surfaceSlots))
	Publish()
EndFunction


bool Function HasArrived()
	Return GetStageDone(10)
EndFunction

bool Function AtGallery()
	Return GetStageDone(50)
EndFunction


Event OnStageSet(int auiStageID, int auiItemID)
	Debug.Trace("TLM_MQ02C: stage " + auiStageID + " item " + auiItemID)
	If auiStageID == 10
		SetObjectiveDisplayed(10,true)
	ElseIf auiStageID == 20
		SetObjectiveCompleted(10,true)
		SetObjectiveDisplayed(20,true)
	ElseIf auiStageID == 30
		SetObjectiveCompleted(20,true)
		SetObjectiveDisplayed(30,true)
	ElseIf auiStageID == 45
		SetObjectiveDisplayed(45,true)
	ElseIf auiStageID == 50
		SetObjectiveCompleted(45,true)
	ElseIf auiStageID == 51 || auiStageID == 52 || auiStageID == 53 || auiStageID == 56 || auiStageID == 57 || auiStageID == 58
		SetObjectiveCompleted(20,true)
		SetObjectiveCompleted(30,true)
		; The optional gallery question is retired, not falsely solved, if not visited.
		If !GetStageDone(50)
			SetObjectiveDisplayed(45,false)
		EndIf
	EndIf
EndEvent


Function StopWatching()
	courtWatching = false
EndFunction


bool Function LampPending(int originCode)
	Return lampAsked && !lampGiven && lampSource == originCode
EndFunction


int Function DeathCauseCount(int causeCode)
	EnsureRoster()
	int resultCount = 0
	int minerIndex = 0
	While minerIndex < 11
		If minerFates[minerIndex] == 4 && minerDeathCauses[minerIndex] == causeCode && Miner(minerIndex) && Miner(minerIndex).IsDead()
			resultCount += 1
		EndIf
		minerIndex += 1
	EndWhile
	Return resultCount
EndFunction


Function AbortFiring()
	If mineValue == 0 && (mineIntent == 0 || mineIntent == 4 || mineIntent == 5)
		mineIntent = 0
		playerOrdered = false
		deadlineBlocked = true
		Publish()
	EndIf
EndFunction


bool Function GalleryOpen()
	Return Open() && GetStageDone(40) && !innerClosed && !mouthClosed
EndFunction


bool Function HasPrisoner()
	Return prisonerStaged
EndFunction
