Scriptname TLM:MQ05Quest extends Quest
{One Blackstone authority. Documents, attributed testimony, actual access and
arrival remain separate receipts. No player-origin/faction/companion outcomes.}
Quest Property TLM_MQ04 Auto Const Mandatory
ReferenceAlias Property Alias_Player Auto Const Mandatory
ReferenceAlias Property Alias_Mara Auto Const Mandatory
ObjectReference Property MaraIdentity Auto Const
ObjectReference[] Property DocumentIdentity Auto Const
ReferenceAlias[] Property Documents Auto Const Mandatory
Int[] Property DocumentPages Auto Const Mandatory
ReferenceAlias Property Alias_Mechanical Auto Const Mandatory
ReferenceAlias Property Alias_ServiceDoor Auto Const Mandatory
ReferenceAlias Property Alias_UpperArrival Auto Const Mandatory
ReferenceAlias Property Alias_LowerArrival Auto Const Mandatory
ReferenceAlias Property Alias_JunctionReturn Auto Const Mandatory
Int[] Property ChoiceCount Auto Const Mandatory
Int[] Property NextNode Auto Const Mandatory
Bool initialized = false
Actor originalPlayer = None
Actor originalMara = None
ObjectReference[] originalDocuments
ObjectReference originalUpper = None
ObjectReference originalLower = None
ObjectReference originalJunction = None
ObjectReference originalDoor = None
ObjectReference originalMechanical = None
Int generation = 0
Int readingDocument = -1
Int readingPage = 0
Int readingEpoch = -1
Int speakingNode = -1
Int speakingEpoch = -1
Int entryEpoch = -1
Bool metMara = false
Bool releaseObserved = false
Bool passInspected = false
Bool passAcknowledged = false
Bool passIssued = false
Bool passUncertain = false

Int Function Epoch()
    Return generation
EndFunction
Function Loaded()
    generation += 1
    readingDocument = -1
    readingEpoch = -1
    speakingNode = -1
    speakingEpoch = -1
    entryEpoch = -1
    If passIssued && !passAcknowledged
        passUncertain = true
    EndIf
EndFunction
Bool Function SourceKnown()
    TLM:MQ04Quest previous = TLM_MQ04 as TLM:MQ04Quest
    Return previous && previous.BlackstoneKnown()
EndFunction
Bool Function OpenLead()
    Actor playerActor = Game.GetPlayer()
    If !SourceKnown() || !playerActor || playerActor.IsDisabled() || playerActor.IsDead()
        Return false
    EndIf
    If !IsRunning()
        If !Start() || !IsRunning()
            Return false
        EndIf
    EndIf
    If !InitializeStation() || !Current(generation) || !SourceKnown()
        Return false
    EndIf
    If !GetStageDone(10)
        SetStage(10)
    EndIf
    Directions()
    Return true
EndFunction
Bool Function InitializeStation()
    If initialized
        Return Game.GetPlayer() == originalPlayer && Alias_Player.GetActorReference() == originalPlayer
    EndIf
    If !IsRunning() || !Documents || Documents.Length != 6 || !DocumentIdentity || DocumentIdentity.Length != 6 || !DocumentPages || DocumentPages.Length != 6 || ChoiceCount.Length != 25 || NextNode.Length != 100
        Return false
    EndIf
    Actor playerActor = Game.GetPlayer()
    Actor maraActor = MaraIdentity as Actor
    ObjectReference doorRef = Alias_ServiceDoor.GetReference()
    ObjectReference releaseRef = Alias_Mechanical.GetReference()
    If !playerActor || Alias_Player.GetActorReference() != playerActor || !doorRef || !releaseRef
        Return false
    EndIf
    ObjectReference[] originals = new ObjectReference[6]
    Int index = 0
    While index < 6
        ObjectReference itemRef = DocumentIdentity[index]
        If DocumentPages[index] < 1
            Return false
        EndIf
        Int prior = 0
        While prior < index
            If itemRef && originals[prior] == itemRef
                Return false
            EndIf
            prior += 1
        EndWhile
        originals[index] = itemRef
        index += 1
    EndWhile
    ObjectReference upperRef = Alias_UpperArrival.GetReference()
    ObjectReference lowerRef = Alias_LowerArrival.GetReference()
    ObjectReference junctionRef = Alias_JunctionReturn.GetReference()
    If !upperRef || !lowerRef || !junctionRef
        Return false
    EndIf
    originalPlayer = playerActor
    originalMara = maraActor
    originalDocuments = originals
    originalUpper = upperRef
    originalLower = lowerRef
    originalJunction = junctionRef
    originalDoor = doorRef
    originalMechanical = releaseRef
    initialized = true
    Int blockIndex = 0
    While blockIndex < 6
        If originalDocuments[blockIndex]
            originalDocuments[blockIndex].BlockActivation(true)
        EndIf
        blockIndex += 1
    EndWhile
    Return true
EndFunction
Bool Function Current(Int capturedEpoch)
    Actor playerActor = Game.GetPlayer()
    Return originalPlayer && IsRunning() && SourceKnown() && playerActor && !playerActor.IsInScene() && !playerActor.IsDisabled() && playerActor.Is3DLoaded() && !playerActor.IsInCombat() && !playerActor.IsDead() && Alias_Player.GetActorReference() == playerActor && playerActor == originalPlayer && capturedEpoch == generation
EndFunction
Bool Function At(ObjectReference who, ObjectReference target, Float radius = 256.0)
    If !who || !target
        Return false
    EndIf
    WorldSpace outside = who.GetWorldSpace()
    If outside
        Return outside == target.GetWorldSpace() && who.GetDistance(target) <= radius
    EndIf
    Return who.GetParentCell() == target.GetParentCell() && who.GetDistance(target) <= radius
EndFunction
ObjectReference Function Document(Int kind)
    If kind < 0 || kind >= 6 || !originalDocuments
        Return None
    EndIf
    Return originalDocuments[kind]
EndFunction
Bool Function DocumentAccess(Int kind, Int capturedEpoch)
    ObjectReference itemRef = Document(kind)
    If !itemRef || !Current(capturedEpoch)
        Return false
    EndIf
    Bool onDesk = !itemRef.IsDisabled() && itemRef.Is3DLoaded() && At(originalPlayer,itemRef,256.0)
    ObjectReference aliasIdentity = Documents[kind].GetReference()
    Actor playerActor = Game.GetPlayer()
    ObjectReference holder = itemRef.GetContainer()
    Return (holder == originalPlayer || (!holder && onDesk)) && aliasIdentity == itemRef && playerActor == originalPlayer && capturedEpoch == generation
EndFunction
Bool Function DocumentPresent(Int kind, Int capturedEpoch)
    ObjectReference itemRef = Document(kind)
    If !itemRef || !Current(capturedEpoch)
        Return false
    EndIf
    Bool inRoom = !itemRef.IsDisabled() && At(originalPlayer,itemRef,1536.0)
    ObjectReference aliasIdentity = Documents[kind].GetReference()
    ObjectReference holder = itemRef.GetContainer()
    Return (holder == originalPlayer || (!holder && inRoom)) && aliasIdentity == itemRef && capturedEpoch == generation
EndFunction
Bool Function BeginDocument(Int kind, Int capturedEpoch)
    If !DocumentAccess(kind,capturedEpoch)
        Return false
    EndIf
    readingDocument = kind
    readingPage = 0
    readingEpoch = capturedEpoch
    Return true
EndFunction
Bool Function AckDocumentPage(Int kind, Int pageNumber, Int capturedEpoch)
    If kind != readingDocument || pageNumber != readingPage || readingEpoch != capturedEpoch || !DocumentAccess(kind,capturedEpoch)
        Return false
    EndIf
    If readingEpoch != capturedEpoch || generation != capturedEpoch || readingDocument != kind || pageNumber != readingPage
        Return false
    EndIf
    readingPage += 1
    If readingPage == DocumentPages[kind]
        Int receipt = 0
        If kind == 0
            receipt = 20
        ElseIf kind == 1
            receipt = 40
        ElseIf kind == 2
            receipt = 45
        ElseIf kind == 3
            receipt = 56
        ElseIf kind == 4 || kind == 5
            receipt = 60
        EndIf
        If receipt == 0
            Return false
        EndIf
        If !GetStageDone(receipt)
            SetStage(receipt)
        EndIf
        If kind == 5
            passInspected = true
        EndIf
        readingDocument = -1
        Directions()
    EndIf
    Return true
EndFunction
Bool Function SpeakerCurrent(Int capturedEpoch)
    If !Current(capturedEpoch) || !GetStageDone(30) || GetStageDone(100)
        Return false
    EndIf
    Actor speakerActor = Alias_Mara.GetActorReference()
    If !speakerActor || speakerActor != originalMara || speakerActor.IsInScene() || speakerActor.IsInDialogueWithPlayer() || speakerActor.IsTalking() || !At(originalPlayer,speakerActor,320.0)
        Return false
    EndIf
    Return speakerActor.Is3DLoaded() && !speakerActor.IsDisabled() && !speakerActor.IsInCombat() && !speakerActor.IsDead() && capturedEpoch == generation
EndFunction
Bool Function NodeAllowed(Int node, Int capturedEpoch)
    If node < 1 || node >= 21 || node == 8 || node == 9 || !SpeakerCurrent(capturedEpoch)
        Return false
    EndIf
    If node == 1
        Return !metMara
    ElseIf node == 7
        Return metMara
    ElseIf node == 10
        Return GetStageDone(45)
    ElseIf node == 11 || node == 12 || node == 13 || node == 14
        Return GetStageDone(50)
    ElseIf node == 15 || node == 16 || node == 17
        Return GetStageDone(55) || node == 17
    ElseIf node == 3
        Return DocumentPresent(1,capturedEpoch) && DocumentPresent(2,capturedEpoch) && SpeakerCurrent(capturedEpoch)
    ElseIf node == 4
        Return DocumentPresent(2,capturedEpoch) && SpeakerCurrent(capturedEpoch)
    EndIf
    Return capturedEpoch == generation
EndFunction
Int Function BeginTalk(Int capturedEpoch)
    Int node = 1
    If metMara
        node = 7
    EndIf
    If !NodeAllowed(node,capturedEpoch)
        Return -1
    EndIf
    speakingNode = node
    speakingEpoch = capturedEpoch
    Return node
EndFunction
Bool Function CanShowNode(Int node, Int capturedEpoch)
    Return speakingNode == node && speakingEpoch == capturedEpoch && NodeAllowed(node,capturedEpoch) && capturedEpoch == generation
EndFunction
Int Function AckChoice(Int node, Int answer, Int capturedEpoch)
    If !CanShowNode(node,capturedEpoch) || answer < 0 || answer >= ChoiceCount[node]
        Return -1
    EndIf
    If node == 7 && answer == 1 && !GetStageDone(45)
        Return -1
    EndIf
    If speakingEpoch != capturedEpoch || speakingNode != node || capturedEpoch != generation
        Return -1
    EndIf
    If node == 1
        metMara = true
    ElseIf node == 10
        If !GetStageDone(50)
            SetStage(50)
        EndIf
    ElseIf node == 14
        If !GetStageDone(55)
            SetStage(55)
        EndIf
    EndIf
    Int target = NextNode[node * 4 + answer]
    If target < 0
        speakingNode = -1
        Return -1
    EndIf
    If !NodeAllowed(target,capturedEpoch) || capturedEpoch != generation
        speakingNode = -1
        Return -1
    EndIf
    speakingNode = target
    Return target
EndFunction
Bool Function MechanicalContext(Int capturedEpoch)
    If !GetStageDone(60) || !Current(capturedEpoch)
        Return false
    EndIf
    ObjectReference releaseRef = Alias_Mechanical.GetReference()
    ObjectReference doorRef = Alias_ServiceDoor.GetReference()
    If releaseRef != originalMechanical || doorRef != originalDoor || releaseRef.IsDisabled() || doorRef.IsDisabled() || !At(originalPlayer,releaseRef,192.0)
        Return false
    EndIf
    Return originalPlayer == Game.GetPlayer() && capturedEpoch == generation
EndFunction
Bool Function AcknowledgeRelease(Int capturedEpoch)
    If !MechanicalContext(capturedEpoch)
        Return false
    EndIf
    Bool stillLocked = originalDoor.IsLocked()
    If stillLocked || capturedEpoch != generation
        Return false
    EndIf
    releaseObserved = true
    Return true
EndFunction
Bool Function PassHeld()
    ObjectReference passRef = Document(5)
    Return passAcknowledged && passRef && Documents[5].GetReference() == passRef && passRef.GetContainer() == originalPlayer
EndFunction
Bool Function BeginPassIssue(Int capturedEpoch)
    If passIssued || passAcknowledged || !passInspected || !GetStageDone(60) || !DocumentAccess(5,capturedEpoch)
        Return false
    EndIf
    ObjectReference holder = Document(5).GetContainer()
    If holder || capturedEpoch != generation
        Return false
    EndIf
    passIssued = true
    passUncertain = false
    Return true
EndFunction
Bool Function AckPassIssue(Int capturedEpoch)
    If !passIssued || passUncertain || !Current(capturedEpoch)
        Return false
    EndIf
    ObjectReference passRef = Documents[5].GetReference()
    ObjectReference holder = Document(5).GetContainer()
    If passRef != Document(5) || holder != originalPlayer || capturedEpoch != generation
        Return false
    EndIf
    passAcknowledged = true
    Return true
EndFunction
Bool Function DoorContext(Int capturedEpoch)
    If !GetStageDone(60) || !Current(capturedEpoch) || (!releaseObserved && !PassHeld())
        Return false
    EndIf
    ObjectReference doorRef = Alias_ServiceDoor.GetReference()
    If doorRef != originalDoor || doorRef.IsDisabled() || !At(originalPlayer,doorRef,192.0)
        Return false
    EndIf
    Bool stillLocked = doorRef.IsLocked()
    Return !stillLocked && originalPlayer == Game.GetPlayer() && capturedEpoch == generation
EndFunction
Bool Function BeginEntry(Int capturedEpoch)
    If !DoorContext(capturedEpoch) || capturedEpoch != generation
        Return false
    EndIf
    entryEpoch = capturedEpoch
    If !GetStageDone(70)
        SetStage(70)
    EndIf
    Return true
EndFunction
Bool Function AcknowledgeUpper(Int capturedEpoch)
    If !GetStageDone(20) || !Current(capturedEpoch) || Alias_UpperArrival.GetReference() != originalUpper || !At(originalPlayer,originalUpper,128.0) || capturedEpoch != generation
        Return false
    EndIf
    If !GetStageDone(30)
        SetStage(30)
    EndIf
    Directions()
    Return true
EndFunction
Bool Function CompleteAtLower(Int capturedEpoch)
    If entryEpoch != capturedEpoch || !GetStageDone(40) || !GetStageDone(45) || !GetStageDone(70) || !Current(capturedEpoch) || Alias_LowerArrival.GetReference() != originalLower || !At(originalPlayer,originalLower,128.0)
        Return false
    EndIf
    If entryEpoch != capturedEpoch || capturedEpoch != generation || originalPlayer != Game.GetPlayer()
        Return false
    EndIf
    If !GetStageDone(100)
        SetStage(100)
    EndIf
    Directions()
    Return true
EndFunction
Function Directions()
    SetObjectiveDisplayed(10,false)
    SetObjectiveDisplayed(20,false)
    SetObjectiveDisplayed(30,false)
    SetObjectiveDisplayed(40,false)
    SetObjectiveDisplayed(45,false)
    SetObjectiveDisplayed(60,false)
    If GetStageDone(100)
        Return
    ElseIf !GetStageDone(20)
        SetObjectiveDisplayed(10)
    ElseIf !GetStageDone(30)
        SetObjectiveDisplayed(20)
    ElseIf !GetStageDone(40)
        SetObjectiveDisplayed(30)
    ElseIf !GetStageDone(45)
        SetObjectiveDisplayed(40)
    ElseIf !GetStageDone(60)
        SetObjectiveDisplayed(45)
    Else
        SetObjectiveDisplayed(60)
    EndIf
EndFunction

Bool Function RouteReady()
    Return initialized && GetStageDone(10) && Current(generation)
EndFunction

ObjectReference Function DoorReference()
    Return originalDoor
EndFunction
Bool Function PassDoorContext(Int capturedEpoch)
    If !Current(capturedEpoch) || !GetStageDone(60) || !passAcknowledged
        Return false
    EndIf
    ObjectReference doorRef = Alias_ServiceDoor.GetReference()
    If doorRef != originalDoor || doorRef.IsDisabled() || !At(originalPlayer,doorRef,192.0)
        Return false
    EndIf
    Bool heldOriginal = PassHeld()
    Return heldOriginal && capturedEpoch == generation
EndFunction
Function AnchorDiagram(ObjectReference itemRef)
    ; SDK Motion_Keyframed is2. Only this immutable new poster is affected;
    ; this request is not native physics/support acceptance or a quest receipt.
    If !initialized || !itemRef || itemRef != Document(4) || Documents[4].GetReference() != itemRef || itemRef.IsDisabled() || !itemRef.Is3DLoaded() || itemRef.GetContainer()
        Return
    EndIf
    itemRef.SetMotionType(2)
EndFunction

ObjectReference Function LowerReference()
    Return originalLower
EndFunction

Bool Function PassIssuePending(Int capturedEpoch)
    ; Pure single-authority intent tail. No yielding native/context read.
    Return passIssued && !passUncertain && !passAcknowledged && capturedEpoch == generation
EndFunction
