Scriptname TLM:GreenwaterRelief extends Quest
{One master-owned local relief ledger. Technical prototype, not a global
calendar or population simulation. Source/synthetic evidence only.
An uncertain native inventory call stays blocked; no retry/refund or later
inventory-count reconciliation is claimed safe.}

Quest Property TLM_MQ02B Auto Const Mandatory
ReferenceAlias Property Alias_Stores Auto Const Mandatory
ReferenceAlias Property Alias_Supply Auto Const Mandatory
Form Property Corn Auto Const
Form Property Caps Auto Const
Message Property NotReady Auto Const
Message Property Unavailable Auto Const
Message Property Blocked Auto Const
Message Property Stores Auto Const
Message Property StoresFinal Auto Const
Message Property Supply Auto Const
Message Property Status Auto Const
Message Property ForecastCovered Auto Const
Message Property ForecastNeeded Auto Const
Message Property PastHunger Auto Const
Message Property DonateMany Auto Const
Message Property DonateFive Auto Const
Message Property DonateOne Auto Const
Message Property NoFood Auto Const
Message Property ConfirmDonate Auto Const
Message Property Donated Auto Const
Message Property ConfirmPurchase Auto Const
Message Property Purchased Auto Const
Message Property NoStock Auto Const
Message Property ConfirmStep Auto Const
Message Property StepDone Auto Const
Message Property CompleteNotice Auto Const

bool initialized = false
int cargoUnitsAtStart = -1
int startingReserve = 0
int donatedUnits = 0
int stepIndex = 0
int purchasedThisStep = 0
bool everShortfall = false
bool completionLatched = false
Quest controlsOwner = None
bool menuBusy = false
int pendingOperation = 0
int requestNonce = 0
int committedNonce = 0
int loadEpoch = 0
int requestEpoch = 0
int requestStep = 0
int requestQuantity = 0
int beforeFood = 0
int beforeCaps = 0
Actor requestActor = None
ObjectReference requestControl = None
bool removalAsked = false
bool deliveryAsked = false
bool uncertain = false
int LIMIT_UNITS = 100000 Const

bool Function OpenControls(Quest akOwner, ObjectReference akStores, ObjectReference akSupply)
	{Only the actually opened controller binds this one ledger. No clone owns
	a reserve. Failed Start or anomalous true-without-running binds nothing.}
	If !akOwner || !akOwner.IsRunning() || !akStores || !akSupply || akStores == akSupply
		Return false
	EndIf
	If !IsRunning()
		bool started = Start()
		If !started || !IsRunning()
			Return false
		EndIf
	EndIf
	If controlsOwner && controlsOwner != akOwner
		Return false
	EndIf
	If controlsOwner
		Return Alias_Stores.GetReference() == akStores && Alias_Supply.GetReference() == akSupply
	EndIf
	Alias_Stores.ForceRefTo(akStores)
	Alias_Supply.ForceRefTo(akSupply)
	If Alias_Stores.GetReference() != akStores || Alias_Supply.GetReference() != akSupply
		Return false
	EndIf
	controlsOwner = akOwner
	Return true
EndFunction

bool Function LocalControl(int aiKind, ObjectReference akControl)
	Actor player = Game.GetPlayer()
	ObjectReference expected = None
	If aiKind == 1
		expected = Alias_Stores.GetReference()
	ElseIf aiKind == 2
		expected = Alias_Supply.GetReference()
	EndIf
	If !IsRunning() || !controlsOwner || !controlsOwner.IsRunning() || !expected || expected != akControl || expected.IsDisabled() || !player || player.IsDead() || player.IsInCombat()
		Return false
	EndIf
	Return player.GetParentCell() == expected.GetParentCell() && player.GetDistance(expected) <= 256.0
EndFunction

bool Function Initialize()
	If initialized
		Return true
	EndIf
	If !IsRunning() || !Corn || !Caps
		Return false
	EndIf
	TLM:MQ02BQuest river = TLM_MQ02B as TLM:MQ02BQuest
	If !river
		Return false
	EndIf
	int reserve = river.ReliefStartingReserve()
	If reserve != 900 && reserve != 630 && reserve != 495 && reserve != 90
		Return false
	EndIf
	startingReserve = reserve
	cargoUnitsAtStart = river.Recovered()
	initialized = true
	SetStage(10)
	Return true
EndFunction

int Function Balance()
	Return startingReserve + donatedUnits - 150 * stepIndex
EndFunction

int Function Reserve()
	int value = Balance()
	If value < 0
		Return 0
	EndIf
	Return value
EndFunction

int Function Shortfall()
	int value = Balance()
	If value < 0
		Return -value
	EndIf
	Return 0
EndFunction

int Function RemainingDemand()
	Return 150 * (6 - stepIndex)
EndFunction

bool Function IsCovered()
	Return initialized && Balance() >= RemainingDemand()
EndFunction

int Function Box(Message akMessage)
	If !akMessage
		Return -1
	EndIf
	Return akMessage.Show()
EndFunction

Function Use(int aiKind, ObjectReference akControl)
	If menuBusy || !LocalControl(aiKind, akControl)
		Return
	EndIf
	menuBusy = true
	int useEpoch = loadEpoch
	If !Initialize()
		Box(NotReady)
	ElseIf useEpoch != loadEpoch
		; A pre-load activation cannot become fresh consent after resumption.
		menuBusy = false
	ElseIf pendingOperation != 0
		; Status is safe even when no new inventory/step request is allowed.
		If Box(Blocked) == 0 && LocalControl(aiKind, akControl)
			ShowStatus(aiKind, akControl)
		EndIf
	ElseIf aiKind == 2
		Shop(akControl)
	Else
		int pick = -1
		If stepIndex < 6
			pick = Box(Stores)
		Else
			pick = Box(StoresFinal)
		EndIf
		If useEpoch == loadEpoch && LocalControl(1, akControl) && pendingOperation == 0
			If pick == 0
				ShowStatus(1, akControl)
			ElseIf pick == 1 && !completionLatched
				Donate(akControl)
			ElseIf pick == 2 && stepIndex < 6
				Advance(akControl)
			EndIf
		EndIf
	EndIf
	menuBusy = false
EndFunction

Function ShowStatus(int aiKind, ObjectReference akControl)
	If !LocalControl(aiKind, akControl)
		Return
	EndIf
	If !Status || Status.Show(stepIndex, Reserve(), Shortfall(), RemainingDemand(), donatedUnits) != 0
		Return
	EndIf
	If !LocalControl(aiKind, akControl)
		Return
	EndIf
	int pick = -1
	If IsCovered()
		pick = Box(ForecastCovered)
	Else
		pick = Box(ForecastNeeded)
	EndIf
	If pick == 0 && LocalControl(aiKind, akControl) && everShortfall
		Box(PastHunger)
	EndIf
EndFunction

bool Function BeginRequest(int aiOperation, int aiKind, ObjectReference akControl, int aiQuantity)
	{Single operation owner; intent and exact snapshots precede effects.}
	If pendingOperation != 0 || uncertain || !initialized || !LocalControl(aiKind, akControl) || requestNonce >= 1000000
		Return false
	EndIf
	pendingOperation = aiOperation
	requestNonce += 1
	requestEpoch = loadEpoch
	requestStep = stepIndex
	requestQuantity = aiQuantity
	requestActor = Game.GetPlayer()
	requestControl = akControl
	beforeFood = requestActor.GetItemCount(Corn)
	beforeCaps = requestActor.GetItemCount(Caps)
	removalAsked = false
	deliveryAsked = false
	If !RequestCurrent(aiOperation, aiKind)
		BlockRequest()
		Return false
	EndIf
	Return true
EndFunction

bool Function RequestCurrent(int aiOperation, int aiKind)
	Return pendingOperation == aiOperation && !uncertain && requestEpoch == loadEpoch && requestStep == stepIndex && requestActor == Game.GetPlayer() && LocalControl(aiKind, requestControl)
EndFunction

Function BlockRequest()
	uncertain = true
	Debug.Trace("TLM_GW_Relief: BLOCKED request=" + requestNonce + " kind=" + pendingOperation + " step=" + requestStep + " quantity=" + requestQuantity + " beforeCorn=" + beforeFood + " beforeCaps=" + beforeCaps + " removalAsked=" + removalAsked + " deliveryAsked=" + deliveryAsked, 2)
	If Game.GetPlayer() && !Game.GetPlayer().IsDead()
		Box(Unavailable)
	EndIf
EndFunction

Function CommitRequest()
	committedNonce = requestNonce
	pendingOperation = 0
EndFunction

Function Donate(ObjectReference akControl)
	int useEpoch = loadEpoch
	Actor player = Game.GetPlayer()
	int count = player.GetItemCount(Corn)
	int pick = -1
	int quantity = 0
	If count >= 10
		pick = Box(DonateMany)
		If pick == 0
			quantity = 1
		ElseIf pick == 1
			quantity = 5
		ElseIf pick == 2
			quantity = 10
		EndIf
	ElseIf count >= 5
		pick = Box(DonateFive)
		If pick == 0
			quantity = 1
		ElseIf pick == 1
			quantity = 5
		EndIf
	ElseIf count >= 1
		If Box(DonateOne) == 0
			quantity = 1
		EndIf
	Else
		Box(NoFood)
		Return
	EndIf
	If quantity == 0 || useEpoch != loadEpoch || !LocalControl(1, akControl) || pendingOperation != 0 || donatedUnits > LIMIT_UNITS - 10 * quantity
		Return
	EndIf
	int clearDebt = 10 * quantity
	If clearDebt > Shortfall()
		clearDebt = Shortfall()
	EndIf
	int oldStep = stepIndex
	If !ConfirmDonate || ConfirmDonate.Show(quantity, clearDebt, 10 * quantity - clearDebt) != 0
		Return
	EndIf
	If useEpoch != loadEpoch || stepIndex != oldStep || completionLatched || !LocalControl(1, akControl) || player != Game.GetPlayer() || player.GetItemCount(Corn) < quantity || donatedUnits > LIMIT_UNITS - 10 * quantity || !BeginRequest(1, 1, akControl, quantity)
		Return
	EndIf
	If beforeFood < quantity
		pendingOperation = 0
		Return
	EndIf
	removalAsked = true
	requestActor.RemoveItem(Corn, quantity, true)
	; Immediate bounded active-request receipt only: no poll/wait, later count
	; inference, reissue or automatic load reconciliation.
	If !RequestCurrent(1, 1) || requestActor.GetItemCount(Corn) != beforeFood - quantity
		BlockRequest()
		Return
	EndIf
	donatedUnits += 10 * quantity
	CommitRequest()
	If !GetStageDone(20)
		SetStage(20)
	EndIf
	MaybeComplete()
	If LocalControl(1, akControl)
		If Box(Donated) == 0 && completionLatched && LocalControl(1, akControl)
			Box(CompleteNotice)
		EndIf
	EndIf
EndFunction

Function Shop(ObjectReference akControl)
	int useEpoch = loadEpoch
	If !Supply
		Return
	EndIf
	int pick = Supply.Show(30 - purchasedThisStep)
	If useEpoch != loadEpoch || !LocalControl(2, akControl)
		Return
	EndIf
	If pick == 1
		ShowStatus(2, akControl)
		Return
	ElseIf pick != 0
		Return
	EndIf
	Actor player = Game.GetPlayer()
	If !LocalControl(2, akControl) || pendingOperation != 0
		Return
	EndIf
	If purchasedThisStep > 20 || player.GetItemCount(Caps) < 20
		Box(NoStock)
		Return
	EndIf
	int oldStep = stepIndex
	If Box(ConfirmPurchase) != 0
		Return
	EndIf
	If useEpoch != loadEpoch || stepIndex != oldStep || !LocalControl(2, akControl) || player != Game.GetPlayer() || purchasedThisStep > 20 || player.GetItemCount(Caps) < 20 || !BeginRequest(2, 2, akControl, 10)
		Return
	EndIf
	If beforeCaps < 20
		pendingOperation = 0
		Return
	EndIf
	removalAsked = true
	requestActor.RemoveItem(Caps, 20, true)
	If !RequestCurrent(2, 2) || requestActor.GetItemCount(Caps) != beforeCaps - 20
		BlockRequest()
		Return
	EndIf
	deliveryAsked = true
	requestActor.AddItem(Corn, 10, true)
	If !RequestCurrent(2, 2) || requestActor.GetItemCount(Corn) != beforeFood + 10
		BlockRequest()
		Return
	EndIf
	purchasedThisStep += 10
	CommitRequest()
	If LocalControl(2, akControl)
		Box(Purchased)
	EndIf
EndFunction

Function Advance(ObjectReference akControl)
	int useEpoch = loadEpoch
	If stepIndex >= 6 || pendingOperation != 0 || !LocalControl(1, akControl)
		Return
	EndIf
	int projected = Balance() - 150
	int nextReserve = projected
	int nextDebt = 0
	If projected < 0
		nextReserve = 0
		nextDebt = -projected
	EndIf
	int oldStep = stepIndex
	If !ConfirmStep || ConfirmStep.Show(nextReserve, nextDebt) != 0
		Return
	EndIf
	If useEpoch != loadEpoch || stepIndex != oldStep || stepIndex >= 6 || !BeginRequest(3, 1, akControl, 150)
		Return
	EndIf
	If !RequestCurrent(3, 1)
		BlockRequest()
		Return
	EndIf
	stepIndex += 1
	If Balance() < 0
		everShortfall = true
	EndIf
	If stepIndex < 6
		purchasedThisStep = 0
	EndIf
	CommitRequest()
	If !GetStageDone(30)
		SetStage(30)
	EndIf
	MaybeComplete()
	If LocalControl(1, akControl)
		If Box(StepDone) == 0 && completionLatched && LocalControl(1, akControl)
			Box(CompleteNotice)
		EndIf
	EndIf
EndFunction

Function MaybeComplete()
	If initialized && stepIndex == 6 && Shortfall() == 0 && !completionLatched && pendingOperation == 0
		completionLatched = true
		SetStage(90)
	EndIf
EndFunction

Function Loaded()
	{Persisted in-flight effects remain unavailable. Never retry/reconcile.}
	loadEpoch += 1
	menuBusy = false
	If pendingOperation != 0
		uncertain = true
		Debug.Trace("TLM_GW_Relief: load preserved blocked request " + requestNonce, 2)
	EndIf
EndFunction
