Scriptname TLM:MQ04Quest extends Quest
{Black Ledger authority. Existing roads remain independent. Permission, physical
original custody, public reading and source knowledge are separate receipts.}
Quest Property TLM_MQ03 Auto Const Mandatory
ReferenceAlias Property Alias_Player Auto Const Mandatory
ReferenceAlias Property Alias_SheriffSource Auto Const Mandatory
ReferenceAlias Property Alias_VaneSource Auto Const Mandatory
ReferenceAlias Property Alias_HaskellSource Auto Const Mandatory
ReferenceAlias Property Alias_Beckett Auto Const Mandatory
ReferenceAlias Property Alias_BlackBook Auto Const Mandatory
ReferenceAlias Property Alias_Warrant Auto Const Mandatory
ReferenceAlias Property Alias_Receipt Auto Const Mandatory
ReferenceAlias Property Alias_Counter Auto Const Mandatory
ReferenceAlias Property Alias_Porch Auto Const Mandatory
ReferenceAlias[] Property Witnesses Auto Const Mandatory
Int Property BookPageCount Auto Const Mandatory

Int generation = 0
Actor playerIdentity = None
Actor[] originalSources
Actor originalBeckett = None
Actor[] originalWitnesses
ObjectReference originalBook = None
ObjectReference originalWarrant = None
ObjectReference originalReceipt = None
Bool warrantRequested = false
Bool warrantAcknowledged = false
Bool receiptAcknowledged = false
Bool bookCustodyAcknowledged = false
Int pendingTransfer = 0
Int transferEpoch = -1
Bool transferIssued = false
Bool transferUncertain = false
Int readPage = 0
Int readingEpoch = -1
Int publicPage = 0
Int publicEpoch = -1
Int resolution = 0
Int blackstoneSource = 0

Function Loaded()
    generation += 1
    readingEpoch = -1
    publicEpoch = -1
    If pendingTransfer != 0
        transferUncertain = true
    EndIf
EndFunction

Int Function Epoch()
    Return generation
EndFunction

Actor Function SourceActor(Int role)
    If role == 0
        Return Alias_SheriffSource.GetActorReference()
    ElseIf role == 1
        Return Alias_VaneSource.GetActorReference()
    ElseIf role == 2
        Return Alias_HaskellSource.GetActorReference()
    EndIf
    Return None
EndFunction

Bool Function Initialize(Actor[] actualSources)
    If !IsRunning() || !actualSources || actualSources.Length != 3 || !Alias_Player.GetActorReference()
        Return false
    EndIf
    If originalBook
        Return actualSources[0] == originalSources[0] && actualSources[1] == originalSources[1] && actualSources[2] == originalSources[2]
    EndIf
    Int index = 0
    While index < 3
        If actualSources[index] != SourceActor(index)
            Return false
        EndIf
        Int prior = 0
        While prior < index
            If actualSources[index] && actualSources[index] == actualSources[prior]
                Return false
            EndIf
            prior += 1
        EndWhile
        index += 1
    EndWhile
    ObjectReference bookRef = Alias_BlackBook.GetReference()
    ObjectReference warrantRef = Alias_Warrant.GetReference()
    ObjectReference receiptRef = Alias_Receipt.GetReference()
    Actor beckettActor = Alias_Beckett.GetActorReference()
    If !bookRef || !warrantRef || !receiptRef || !beckettActor || bookRef == warrantRef || bookRef == receiptRef || warrantRef == receiptRef || !Witnesses || Witnesses.Length < 1
        Return false
    EndIf
    Actor[] crowd = new Actor[Witnesses.Length]
    index = 0
    While index < Witnesses.Length
        Actor witnessActor = Witnesses[index].GetActorReference()
        If !witnessActor || witnessActor == beckettActor || witnessActor == actualSources[0] || witnessActor == actualSources[1]
            Return false
        EndIf
        Int prior = 0
        While prior < index
            If crowd[prior] == witnessActor
                Return false
            EndIf
            prior += 1
        EndWhile
        crowd[index] = witnessActor
        index += 1
    EndWhile
    originalSources = actualSources
    originalWitnesses = crowd
    playerIdentity = Alias_Player.GetActorReference()
    originalBook = bookRef
    originalWarrant = warrantRef
    originalReceipt = receiptRef
    originalBeckett = beckettActor
    Return true
EndFunction

Bool Function Alive(Actor who)
    Return who && !who.IsDead() && !who.IsDisabled() && who.Is3DLoaded() && !who.IsInCombat()
EndFunction

Bool Function At(ObjectReference who, ObjectReference target, Float radius = 320.0)
    Return who && target && who.GetParentCell() == target.GetParentCell() && who.GetDistance(target) <= radius
EndFunction

Bool Function Current(Int capturedEpoch)
    Actor playerActor = Game.GetPlayer()
    Return IsRunning() && originalBook && Alive(playerActor) && playerActor == playerIdentity && Alias_Player.GetActorReference() == playerActor && capturedEpoch == generation
EndFunction

Bool Function LeadKnown()
    TLM:MQ03Quest fair = TLM_MQ03 as TLM:MQ03Quest
    Return fair && fair.HasReadLead()
EndFunction

Actor Function OriginalActor(Int role)
    If !originalSources || role < 0 || role >= 3 || SourceActor(role) != originalSources[role]
        Return None
    EndIf
    Return originalSources[role]
EndFunction

Bool Function Speaker(Actor who, Int role, Int capturedEpoch)
    Actor expected = OriginalActor(role)
    If !who || !expected || who != expected || who.IsInScene() || who.IsInDialogueWithPlayer() || who.IsTalking()
        Return false
    EndIf
    Return Alive(who) && At(Game.GetPlayer(),who) && who == SourceActor(role) && Current(capturedEpoch)
EndFunction

Bool Function Beckett(Actor who, Int capturedEpoch)
    If !who || who.IsInScene() || who.IsInDialogueWithPlayer() || who.IsTalking()
        Return false
    EndIf
    Return who == originalBeckett && who == Alias_Beckett.GetActorReference() && Alive(who) && At(Game.GetPlayer(),who) && Current(capturedEpoch)
EndFunction

Bool Function RecordOffer(Actor sheriffActor, Int capturedEpoch)
    If !LeadKnown() || !Speaker(sheriffActor,0,capturedEpoch)
        Return false
    EndIf
    If !GetStageDone(10)
        SetStage(10)
        SetObjectiveDisplayed(10)
    EndIf
    Return true
EndFunction

Bool Function RequestWarrant(Actor sheriffActor, Int capturedEpoch)
    If !GetStageDone(10) || !LeadKnown() || !Speaker(sheriffActor,0,capturedEpoch)
        Return false
    EndIf
    warrantRequested = true
    SetObjectiveDisplayed(11)
    Return true
EndFunction

Bool Function WarrantRequested()
    Return warrantRequested
EndFunction

ObjectReference Function TransferReference(Int kind)
    If kind == 1
        Return originalWarrant
    ElseIf kind == 2
        Return originalReceipt
    ElseIf kind == 3
        Return originalBook
    EndIf
    Return None
EndFunction

ObjectReference Function TransferReceiver(Int kind)
    If kind == 1
        Return OriginalActor(0)
    ElseIf kind == 2 || kind == 3
        Return playerIdentity
    EndIf
    Return None
EndFunction

Bool Function TransferEligible(Int kind, Int capturedEpoch)
    Actor sheriffActor = OriginalActor(0)
    If !Current(capturedEpoch) || !LeadKnown() || !Speaker(sheriffActor,0,capturedEpoch)
        Return false
    EndIf
    If kind == 1
        Return warrantRequested && !warrantAcknowledged && Alias_Warrant.GetReference() == originalWarrant
    EndIf
    If !GetStageDone(43) || resolution != 0 || !Beckett(originalBeckett,capturedEpoch)
        Return false
    EndIf
    If kind == 2
        Return !receiptAcknowledged && Alias_Receipt.GetReference() == originalReceipt
    ElseIf kind == 3
        Return receiptAcknowledged && originalReceipt.GetContainer() == playerIdentity && !bookCustodyAcknowledged && Alias_BlackBook.GetReference() == originalBook
    EndIf
    Return false
EndFunction

Bool Function BeginTransfer(Int kind, Int capturedEpoch)
    ObjectReference sourceRef = TransferReference(kind)
    If pendingTransfer != 0 || !sourceRef || sourceRef.GetContainer() || !TransferEligible(kind,capturedEpoch)
        Return false
    EndIf
    pendingTransfer = kind
    transferEpoch = capturedEpoch
    transferIssued = false
    transferUncertain = false
    Return true
EndFunction

Bool Function MarkTransferIssued(Int kind, Int capturedEpoch)
    If pendingTransfer != kind || transferEpoch != capturedEpoch || transferIssued || transferUncertain || !TransferEligible(kind,capturedEpoch)
        Return false
    EndIf
    transferIssued = true
    Return true
EndFunction

Bool Function AckTransfer(Int kind, Int capturedEpoch)
    ObjectReference sourceRef = TransferReference(kind)
    ObjectReference receiver = TransferReceiver(kind)
    If pendingTransfer != kind || transferEpoch != capturedEpoch || !transferIssued || transferUncertain || !sourceRef || !receiver || !TransferEligible(kind,capturedEpoch)
        Return false
    EndIf
    ObjectReference holder = sourceRef.GetContainer()
    If holder != receiver || !Current(capturedEpoch) || sourceRef != TransferReference(kind) || receiver != TransferReceiver(kind)
        Return false
    EndIf
    If kind == 1
        warrantAcknowledged = true
    ElseIf kind == 2
        receiptAcknowledged = true
    ElseIf kind == 3
        bookCustodyAcknowledged = true
    EndIf
    pendingTransfer = 0
    transferIssued = false
    transferEpoch = -1
    Return true
EndFunction

Int Function TransferPending()
    Return pendingTransfer
EndFunction

Bool Function WarrantPresent(Int capturedEpoch)
    Actor sheriffActor = OriginalActor(0)
    Return warrantAcknowledged && originalWarrant == Alias_Warrant.GetReference() && originalWarrant.GetContainer() == sheriffActor && Speaker(sheriffActor,0,capturedEpoch)
EndFunction

Bool Function RecordLawfulAccess(Int capturedEpoch)
    If !GetStageDone(10) || !warrantRequested || !WarrantPresent(capturedEpoch) || !Speaker(OriginalActor(1),1,capturedEpoch) || !At(Game.GetPlayer(),Alias_Counter.GetReference()) || !At(OriginalActor(0),Alias_Counter.GetReference())
        Return false
    EndIf
    SetStage(21)
    SetObjectiveCompleted(10)
    SetObjectiveCompleted(11)
    SetObjectiveDisplayed(30)
    Return true
EndFunction

Bool Function BookAccess(ObjectReference bookRef, Int capturedEpoch)
    If !GetStageDone(21) || !bookRef || bookRef != originalBook || bookRef != Alias_BlackBook.GetReference() || !Current(capturedEpoch)
        Return false
    EndIf
    ObjectReference holder = bookRef.GetContainer()
    If holder
        Return holder == playerIdentity && Current(capturedEpoch)
    EndIf
    Return !bookRef.IsDisabled() && At(Game.GetPlayer(),bookRef,256.0) && Current(capturedEpoch)
EndFunction

Bool Function BeginRead(ObjectReference bookRef, Int capturedEpoch)
    If !BookAccess(bookRef,capturedEpoch) || BookPageCount < 1
        Return false
    EndIf
    readPage = 0
    readingEpoch = capturedEpoch
    Return true
EndFunction

Bool Function AckReadPage(ObjectReference bookRef, Int pageNumber, Int capturedEpoch)
    If readingEpoch != capturedEpoch || pageNumber != readPage || !BookAccess(bookRef,capturedEpoch)
        Return false
    EndIf
    readPage += 1
    If readPage == BookPageCount
        SetStage(30)
        SetObjectiveCompleted(30)
        SetObjectiveDisplayed(40)
    EndIf
    Return true
EndFunction

Bool Function RecordDoorway(Actor beckettActor, Int capturedEpoch)
    If !GetStageDone(30) || resolution != 0 || !Beckett(beckettActor,capturedEpoch)
        Return false
    EndIf
    SetStage(40)
    Return true
EndFunction

Bool Function AllowInspection(Actor beckettActor, Int capturedEpoch)
    If !GetStageDone(40) || resolution != 0 || !WarrantPresent(capturedEpoch) || !Beckett(beckettActor,capturedEpoch)
        Return false
    EndIf
    SetStage(43)
    SetObjectiveCompleted(40)
    SetObjectiveDisplayed(43)
    Return true
EndFunction

Bool Function BookHeld()
    Return bookCustodyAcknowledged && originalBook && originalBook == Alias_BlackBook.GetReference() && originalBook.GetContainer() == playerIdentity
EndFunction

Bool Function PorchContext(Int capturedEpoch)
    If !GetStageDone(43) || !GetStageDone(30) || resolution != 0 || !BookHeld() || !At(Game.GetPlayer(),Alias_Porch.GetReference()) || !Speaker(OriginalActor(0),0,capturedEpoch) || !Speaker(OriginalActor(1),1,capturedEpoch)
        Return false
    EndIf
    Int index = 0
    While index < Witnesses.Length
        Actor witnessActor = Witnesses[index].GetActorReference()
        If witnessActor != originalWitnesses[index] || !Alive(witnessActor) || !At(witnessActor,Alias_Porch.GetReference(),512.0)
            Return false
        EndIf
        index += 1
    EndWhile
    Return Current(capturedEpoch) && BookHeld()
EndFunction

Bool Function BeginPorch(Int capturedEpoch)
    If !PorchContext(capturedEpoch)
        Return false
    EndIf
    SetStage(50)
    SetObjectiveCompleted(43)
    SetObjectiveDisplayed(50)
    Return true
EndFunction

Bool Function BeginPublicRead(Int capturedEpoch)
    If !GetStageDone(50) || !PorchContext(capturedEpoch)
        Return false
    EndIf
    publicEpoch = capturedEpoch
    publicPage = 0
    Return true
EndFunction

Bool Function AckPublicPage(Int pageNumber, Int capturedEpoch)
    If publicEpoch != capturedEpoch || publicPage != pageNumber || !PorchContext(capturedEpoch)
        Return false
    EndIf
    publicPage += 1
    Return true
EndFunction

Bool Function CommitPublicRead(Int capturedEpoch)
    If publicEpoch != capturedEpoch || publicPage != BookPageCount || !PorchContext(capturedEpoch)
        Return false
    EndIf
    resolution = 61
    SetStage(61)
    SetObjectiveCompleted(50)
    If blackstoneSource == 0
        SetObjectiveDisplayed(61)
    EndIf
    Return true
EndFunction

Int Function Resolution()
    Return resolution
EndFunction

Bool Function LearnBlackstone(Actor sourceActor, Int sourceKind, Int capturedEpoch)
    ; 1: actually heard Vane's names line after public reading. 2: Haskell's exact account.
    If !LeadKnown() || !Current(capturedEpoch)
        Return false
    EndIf
    If sourceKind == 1
        If resolution != 61 || !Speaker(sourceActor,1,capturedEpoch)
            Return false
        EndIf
    ElseIf sourceKind == 2
        If !Speaker(sourceActor,2,capturedEpoch)
            Return false
        EndIf
    Else
        Return false
    EndIf
    blackstoneSource = sourceKind
    SetStage(100)
    SetObjectiveCompleted(61)
    SetObjectiveDisplayed(100)
    ; Knowledge does not resolve an outstanding porch scene or any earlier road.
    Return true
EndFunction

Bool Function BlackstoneKnown()
    Return blackstoneSource != 0 && GetStageDone(100)
EndFunction

Bool Function TransferComplete(Int kind)
    ObjectReference itemRef = TransferReference(kind)
    Bool historical = warrantAcknowledged
    If kind == 2
        historical = receiptAcknowledged
    ElseIf kind == 3
        historical = bookCustodyAcknowledged
    ElseIf kind != 1
        Return false
    EndIf
    Return historical && itemRef && itemRef.GetContainer() == TransferReceiver(kind)
EndFunction

Bool Function AcknowledgeHeldOriginal(Int capturedEpoch)
    ; Ordinary pickup of this SAME original is genuine custody, never a base copy.
    If pendingTransfer != 0 || !GetStageDone(43) || !receiptAcknowledged || originalReceipt.GetContainer() != playerIdentity || !Speaker(OriginalActor(0),0,capturedEpoch) || !Beckett(originalBeckett,capturedEpoch)
        Return false
    EndIf
    ObjectReference holder = originalBook.GetContainer()
    If holder != playerIdentity || Alias_BlackBook.GetReference() != originalBook || !Current(capturedEpoch)
        Return false
    EndIf
    bookCustodyAcknowledged = true
    Return true
EndFunction

Bool Function CompleteChapter(Int capturedEpoch)
    If resolution != 61 || !BlackstoneKnown() || !Current(capturedEpoch)
        Return false
    EndIf
    SetStage(110)
    Return true
EndFunction
