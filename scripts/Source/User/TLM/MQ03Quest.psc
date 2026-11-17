Scriptname TLM:MQ03Quest extends Quest
{Four Flags authoritative ledger. Source/synthetic candidate only. No global
calendar, auto-death, faction allegiance or older-road outcome setter.}

Quest Property TLM_MQ01 Auto Const Mandatory
Quest Property TLM_MQ02A Auto Const Mandatory
Quest Property TLM_MQ02B Auto Const Mandatory
Quest Property TLM_MQ02C Auto Const Mandatory
GlobalVariable Property FirstDone Auto Const Mandatory
GlobalVariable Property RailReported Auto Const Mandatory
GlobalVariable Property RiverReported Auto Const Mandatory
GlobalVariable Property HollowReported Auto Const Mandatory
ReferenceAlias Property Alias_Player Auto Const Mandatory
ReferenceAlias Property Alias_Arrival Auto Const Mandatory
ReferenceAlias Property Alias_OriginalCase Auto Const Mandatory
ReferenceAlias Property Alias_OriginalSilver Auto Const Mandatory
ReferenceAlias[] Property Cast Auto Const Mandatory
ReferenceAlias Property Alias_OccupationBoard Auto Const Mandatory

int generation = 0
int entryBasis = 0
int response = 0
int pendingCourse = 0
bool orderHeard = false
Actor orderIssuer = None
bool courierHeard = false
bool silverInspected = false
bool landingInspected = false
bool caseHistoricalRead = false
bool caseTaken = false
Actor publicCustodian = None
bool flintTalks = false
bool crowdSpared = false
bool sceneArmed = false
Actor sceneCourier = None
ObjectReference sceneCase = None
int effectPending = 0
ObjectReference effectReference = None
Actor effectActor = None
int effectEpoch = -1
bool effectIssued = false
bool effectUncertain = false
bool opportunitiesShown = false
ObjectReference originalCaseIdentity = None
ObjectReference originalSilverIdentity = None
Actor[] originalOwnCast
Actor playerIdentity = None

bool Function InitializeIdentities()
	{Captured once from the verified source aliases after successful Start.
	Later alias changes never nominate another original item or fair actor.}
	If originalCaseIdentity
		Return Alias_OriginalCase.GetReference() == originalCaseIdentity && Alias_OriginalSilver.GetReference() == originalSilverIdentity
	EndIf
	ObjectReference originalCase = Alias_OriginalCase.GetReference()
	ObjectReference originalSilver = Alias_OriginalSilver.GetReference()
	If !IsRunning() || !originalCase || !originalSilver || originalCase == originalSilver
		Return false
	EndIf
	Actor[] owned = new Actor[5]
	int i = 0
	While i < 5
		owned[i] = Cast[i + 4].GetActorReference()
		int j = 0
		While j < i
			If owned[i] && owned[i] == owned[j]
				Return false
			EndIf
			j += 1
		EndWhile
		i += 1
	EndWhile
	originalOwnCast = owned
	playerIdentity = Alias_Player.GetActorReference()
	originalCaseIdentity = originalCase
	originalSilverIdentity = originalSilver
	Return true
EndFunction

int Function Epoch()
	Return generation
EndFunction

Function Loaded()
	generation += 1
	If effectPending != 0
		effectUncertain = true
	EndIf
EndFunction

bool Function FirstComplete()
	Return TLM_MQ01.IsRunning() && TLM_MQ01.GetStageDone(100) && FirstDone.GetValueInt() == 1
EndFunction

bool Function RoadComplete(int which)
	If which == 0
		Return TLM_MQ02A.GetStageDone(100)
	ElseIf which == 1
		Return TLM_MQ02B.GetStageDone(100)
	ElseIf which == 2
		Return TLM_MQ02C.GetStageDone(100)
	EndIf
	Return false
EndFunction

bool Function AnyRoadComplete()
	Return RoadComplete(0) || RoadComplete(1) || RoadComplete(2)
EndFunction

bool Function AnyReportedComplete()
	Return (RoadComplete(0) && RailReported.GetValueInt() == 1) || (RoadComplete(1) && RiverReported.GetValueInt() == 1) || (RoadComplete(2) && HollowReported.GetValueInt() == 1)
EndFunction

bool Function Qualify(int basis, int capturedEpoch)
	{1 actual reported completed road; 2 acknowledged unreported road;
	3 explicit standalone no-report request; 4 full handbill acknowledgment.}
	bool valid = FirstComplete()
	If basis == 1
		valid = valid && AnyReportedComplete()
	ElseIf basis == 2
		valid = valid && AnyRoadComplete()
	ElseIf basis != 3 && basis != 4
		valid = false
	EndIf
	If !valid || capturedEpoch != generation
		Return false
	EndIf
	If entryBasis == 0
		entryBasis = basis
	EndIf
	Return true
EndFunction

int Function EntryKind()
	Return entryBasis
EndFunction

Actor Function Person(int role)
	If role < 0 || role >= Cast.Length || !Cast[role]
		Return None
	EndIf
	Actor who = Cast[role].GetActorReference()
	If role >= 4 && (!originalOwnCast || who != originalOwnCast[role - 4])
		Return None
	EndIf
	If role < 4 && who != (Self as TLM:FourFlagsWalk).OriginalVisitor(role)
		Return None
	EndIf
	Return who
EndFunction

bool Function Alive(Actor who)
	Return who && !who.IsDead() && !who.IsDisabled() && !who.IsInCombat() && !who.IsInDialogueWithPlayer() && !who.IsInScene()
EndFunction

bool Function At(ObjectReference who, ObjectReference where, float reach = 128.0)
	Return who && where && who.GetParentCell() == where.GetParentCell() && who.GetDistance(where) <= reach
EndFunction

bool Function Local()
	Actor player = Game.GetPlayer()
	Return IsRunning() && entryBasis > 0 && FirstComplete() && player && player == playerIdentity && Alive(player) && Alias_Player.GetReference() == player && Alias_Arrival.GetReference() && player.GetParentCell() == Alias_Arrival.GetReference().GetParentCell()
EndFunction

bool Function Current(int capturedEpoch)
	bool eligible = Local()
	Return eligible && capturedEpoch == generation
EndFunction

bool Function TravelCurrent(int capturedEpoch)
	Actor player = Game.GetPlayer()
	bool eligible = IsRunning() && entryBasis > 0 && FirstComplete() && player && player == playerIdentity && Alive(player) && Alias_Player.GetReference() == player
	Return eligible && capturedEpoch == generation
EndFunction

bool Function Speaker(Actor who, int role, int capturedEpoch)
	bool eligible = Local() && Alive(who) && At(Game.GetPlayer(),who,2048.0)
	bool authority = (Self as TLM:FourFlagsWalk).SourceIdentity(role,who)
	Actor currentActor = Person(role)
	Return eligible && authority && currentActor == who && capturedEpoch == generation
EndFunction

bool Function RecordFairArrival(int capturedEpoch)
	bool here = Local() && At(Game.GetPlayer(),Alias_Arrival.GetReference(),256.0)
	If !here || capturedEpoch != generation
		Return false
	EndIf
	If !GetStageDone(10)
		SetStage(10)
		SetObjectiveDisplayed(10)
	EndIf
	Return true
EndFunction

bool Function ChoicesOpen()
	Return GetStageDone(40) && response == 0 && pendingCourse == 0 && !GetStageDone(70) && !GetStageDone(100)
EndFunction

bool Function CaseAccess(ObjectReference original)
	If !original || original != originalCaseIdentity || Alias_OriginalCase.GetReference() != original
		Return false
	EndIf
	ObjectReference holder = original.GetContainer()
	If holder == Game.GetPlayer()
		Return Local()
	ElseIf holder && holder == Person(0)
		Return Local() && Alive(Person(0)) && At(Game.GetPlayer(),holder,2048.0)
	ElseIf !holder
		Return Local() && At(Game.GetPlayer(),original,256.0) && !original.IsDisabled()
	EndIf
	Return false
EndFunction

bool Function Held()
	ObjectReference original = originalCaseIdentity
	Return original && original.GetContainer() == Game.GetPlayer()
EndFunction

Actor Function PublicHolder()
	ObjectReference original = originalCaseIdentity
	If !original
		Return None
	EndIf
	ObjectReference holder = original.GetContainer()
	Actor sheriff = Person(0)
	If holder == sheriff && Alive(sheriff)
		Return sheriff
	EndIf
	Return None
EndFunction

bool Function AcknowledgeHeldTake(ObjectReference original, int capturedEpoch)
	bool eligible = effectPending == 0 && !effectUncertain && pendingCourse == 44 && response == 0 && original && original.GetContainer() == Game.GetPlayer() && Local()
	If !eligible || Alias_OriginalCase.GetReference() != original || !Current(capturedEpoch)
		Return false
	EndIf
	caseTaken = true
	response = 44
	pendingCourse = 0
	SetStage(44)
	SetObjectiveCompleted(40)
	Return true
EndFunction

int Function ResponseKind()
	Return response
EndFunction

int Function PendingResponse()
	Return pendingCourse
EndFunction

Actor Function OrderActor()
	Return orderIssuer
EndFunction

int Function PendingEffect()
	Return effectPending
EndFunction

bool Function ReadBefore()
	Return caseHistoricalRead
EndFunction

bool Function HeardBefore()
	Return courierHeard
EndFunction

bool Function SilverBefore()
	Return silverInspected
EndFunction

bool Function FlintBefore()
	Return flintTalks
EndFunction

ObjectReference Function SilverObject()
	Return originalSilverIdentity
EndFunction

bool Function RecordOpportunities(int capturedEpoch)
	If !GetStageDone(10) || !Current(capturedEpoch)
		Return false
	EndIf
	opportunitiesShown = true
	Return true
EndFunction

bool Function BeginEncounter(Actor courier, ObjectReference original, int capturedEpoch)
	bool eligible = GetStageDone(10) && !GetStageDone(40) && opportunitiesShown && courier && original && !courier.IsInCombat() && !courier.IsInDialogueWithPlayer() && !courier.IsInScene() && Local() && At(Game.GetPlayer(),courier,2048.0)
	If !eligible || original != originalCaseIdentity || Person(8) != courier || Alias_OriginalCase.GetReference() != original || capturedEpoch != generation
		Return false
	EndIf
	If sceneArmed
		Return sceneCourier == courier && sceneCase == original
	EndIf
	sceneArmed = true
	sceneCourier = courier
	sceneCase = original
	Return true
EndFunction

bool Function FinishEncounter(Actor courier, ObjectReference original, bool foundDead, int capturedEpoch)
	bool eligible = sceneArmed && !GetStageDone(40) && Local() && courier && original && !courier.IsDisabled() && !courier.IsInCombat() && !courier.IsInDialogueWithPlayer() && !courier.IsInScene() && courier.IsDead() == foundDead && !original.IsDisabled() && At(Game.GetPlayer(),courier,2048.0) && At(original,courier,128.0) && !original.GetContainer()
	If !eligible || courier != sceneCourier || original != sceneCase || Person(8) != courier || Alias_OriginalCase.GetReference() != original || capturedEpoch != generation
		Return false
	EndIf
	SetStage(40)
	If foundDead
		SetStage(45)
	Else
		SetStage(46)
	EndIf
	SetObjectiveCompleted(10)
	SetObjectiveDisplayed(40)
	SetObjectiveDisplayed(60)
	Return true
EndFunction

bool Function AcknowledgeOrder(Actor issuer, int capturedEpoch)
	If !ChoicesOpen() || !Speaker(issuer,5,capturedEpoch)
		Return false
	EndIf
	orderIssuer = issuer
	orderHeard = true
	Return true
EndFunction

bool Function PlanCourse(int course, Actor carrier, int carrierRole, int capturedEpoch)
	If course != 41 && course != 42 && course != 44
		Return false
	EndIf
	bool eligible = ChoicesOpen() && Speaker(carrier,carrierRole,capturedEpoch)
	If course == 42
		eligible = eligible && Alive(Person(8))
	EndIf
	If !eligible || !Current(capturedEpoch)
		Return false
	EndIf
	If carrierRole == 5
		If !orderHeard || orderIssuer != carrier
			Return false
		EndIf
	EndIf
	pendingCourse = course
	Return true
EndFunction

Function DropUncommittedCourse(int capturedEpoch)
	If capturedEpoch == generation && !GetStageDone(70) && effectPending == 0 && response == 0
		pendingCourse = 0
	EndIf
EndFunction

bool Function RecordOccupation(Actor issuer, ObjectReference board, int capturedEpoch)
	bool visible = board && !board.IsDisabled() && Local() && At(Game.GetPlayer(),board,2048.0)
	bool eligible = pendingCourse != 0 && response == 0 && !GetStageDone(43) && !GetStageDone(70) && orderHeard && issuer == orderIssuer && Speaker(issuer,5,capturedEpoch)
	If !visible || !eligible || Alias_OccupationBoard.GetReference() != board || !Current(capturedEpoch)
		Return false
	EndIf
	SetStage(70)
	Return true
EndFunction

bool Function CommitPlanned(int capturedEpoch)
	If response != 0 || (pendingCourse != 41 && pendingCourse != 42) || !Current(capturedEpoch)
		Return false
	EndIf
	response = pendingCourse
	pendingCourse = 0
	SetStage(response)
	SetObjectiveCompleted(40)
	Return true
EndFunction

bool Function Quorum(Actor[] captured, int officer, int capturedEpoch)
	If !ChoicesOpen() || captured.Length != 9 || (officer != 0 && officer != 1)
		Return false
	EndIf
	bool eligible = true
	int role = 3
	While role <= 6
		eligible = eligible && Speaker(captured[role],role,capturedEpoch)
		role += 1
	EndWhile
	eligible = eligible && Speaker(captured[officer],officer,capturedEpoch)
	If officer == 1
		Actor pritchard = Person(0)
		eligible = eligible && (!pritchard || pritchard.IsDead() || pritchard.IsDisabled() || !At(Game.GetPlayer(),pritchard,2048.0))
	EndIf
	Return eligible && capturedEpoch == generation
EndFunction

bool Function Concede(Actor[] captured, int officer, int capturedEpoch)
	If !Quorum(captured,officer,capturedEpoch)
		Return false
	EndIf
	response = 43
	crowdSpared = true
	SetStage(43)
	SetObjectiveCompleted(40)
	Return true
EndFunction

bool Function RecordCourierWords(Actor courier, int capturedEpoch)
	If response != 42 || GetStageDone(100) || !Speaker(courier,8,capturedEpoch)
		Return false
	EndIf
	courierHeard = true
	Return true
EndFunction

bool Function InspectSilver(ObjectReference original, int capturedEpoch)
	bool eligible = GetStageDone(40) && Local() && original && !original.IsDisabled() && At(Game.GetPlayer(),original,256.0) && !original.GetContainer()
	If !eligible || original != originalSilverIdentity || Alias_OriginalSilver.GetReference() != original || capturedEpoch != generation
		Return false
	EndIf
	silverInspected = true
	If !GetStageDone(50)
		SetStage(50)
	EndIf
	Return true
EndFunction

bool Function InspectLanding(ObjectReference station, int capturedEpoch)
	If !GetStageDone(40) || !At(Game.GetPlayer(),station,256.0) || !Current(capturedEpoch)
		Return false
	EndIf
	landingInspected = true
	Return true
EndFunction

bool Function TransferOriginal(int kind, ObjectReference original, Actor recipient, int capturedEpoch)
	{One original-reference effect, immediate original-container receipt only.
	Failure/load is held, never a base-form copy or later-count recovery.}
	bool eligible = effectPending == 0 && !effectUncertain && GetStageDone(40) && Local() && original && Alive(recipient)
	If kind == 1
		eligible = eligible && original == Alias_OriginalCase.GetReference() && recipient == Game.GetPlayer() && CaseAccess(original) && !Held()
	ElseIf kind == 2
		eligible = eligible && original == Alias_OriginalCase.GetReference() && CaseAccess(original) && Speaker(recipient,0,capturedEpoch)
	ElseIf kind == 3
		eligible = eligible && silverInspected && original == originalSilverIdentity && original == Alias_OriginalSilver.GetReference() && !original.GetContainer() && At(Game.GetPlayer(),original,2048.0) && Speaker(recipient,7,capturedEpoch)
	Else
		Return false
	EndIf
	If !eligible || !Current(capturedEpoch)
		Return false
	EndIf
	; No native call between testing and claiming the sole transfer owner.
	If effectPending != 0 || effectUncertain || capturedEpoch != generation
		Return false
	EndIf
	effectPending = kind
	effectReference = original
	effectActor = recipient
	effectEpoch = capturedEpoch
	effectIssued = true
	recipient.AddItem(original,1,true)
	ObjectReference holder = original.GetContainer()
	bool currentRecipient = kind == 1 && recipient == Game.GetPlayer()
	If kind == 2
		currentRecipient = Speaker(recipient,0,capturedEpoch)
	ElseIf kind == 3
		currentRecipient = Speaker(recipient,7,capturedEpoch)
	EndIf
	bool currentObject = original == Alias_OriginalCase.GetReference()
	If kind == 3
		currentObject = original == Alias_OriginalSilver.GetReference()
	EndIf
	bool currentContext = Current(capturedEpoch)
	If holder != recipient || !currentRecipient || !currentObject || !currentContext || capturedEpoch != generation || effectEpoch != capturedEpoch || effectReference != original || effectActor != recipient || effectPending != kind || effectUncertain
		effectUncertain = true
		Return false
	EndIf
	effectPending = 0
	If kind == 1
		If pendingCourse == 44 && response == 0
			caseTaken = true
			response = 44
			pendingCourse = 0
			SetStage(44)
			SetObjectiveCompleted(40)
		EndIf
	ElseIf kind == 2
		publicCustodian = recipient
	Else
		flintTalks = true
		SetStage(51)
	EndIf
	Return true
EndFunction

bool Function RecordCaseRead(ObjectReference original, int capturedEpoch)
	bool accessible = GetStageDone(40) && CaseAccess(original)
	If !accessible || Alias_OriginalCase.GetReference() != original || !Current(capturedEpoch)
		Return false
	EndIf
	caseHistoricalRead = true
	If !GetStageDone(60)
		SetStage(60)
		SetObjectiveCompleted(60)
	EndIf
	Return true
EndFunction

bool Function FinishRead(ObjectReference original, Actor speakerActor, int capturedEpoch)
	bool eligible = caseHistoricalRead && GetStageDone(60) && !GetStageDone(100) && CaseAccess(original)
	If speakerActor
		eligible = eligible && original.GetContainer() == speakerActor && Speaker(speakerActor,0,capturedEpoch)
	EndIf
	If !eligible || Alias_OriginalCase.GetReference() != original || !Current(capturedEpoch)
		Return false
	EndIf
	SetStage(100)
	If speakerActor
		SetStage(101)
	EndIf
	Return true
EndFunction
