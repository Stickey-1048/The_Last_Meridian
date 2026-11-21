Scriptname TLM:BlackLedgerWalk extends Quest
{Finite lawful rough-cut presentation. No automatic hanging, hostility, timers,
road completion or unobserved transfer success. Original visitors are restored.}
Quest Property TLM_MQ04 Auto Const Mandatory
ReferenceAlias Property Alias_Arrival Auto Const Mandatory
ReferenceAlias Property Alias_Exit Auto Const Mandatory
ReferenceAlias[] Property RoomSlots Auto Const Mandatory
ReferenceAlias[] Property ReturnSlots Auto Const Mandatory
ReferenceAlias[] Property StageOn Auto Const Mandatory
ReferenceAlias[] Property PorchWitnessSlots Auto Const Mandatory
Message[] Property Speech Auto Const Mandatory
String[] Property SpeechNames Auto Const Mandatory
Int[] Property SpeechStart Auto Const Mandatory
Int[] Property SpeechSize Auto Const Mandatory
Int[] Property SpeechButtons Auto Const Mandatory
Message[] Property BookPages Auto Const Mandatory
Message Property Lead Auto Const Mandatory
Message Property Travel Auto Const Mandatory
Message Property ExitPrompt Auto Const Mandatory
Message Property PublicReady Auto Const Mandatory
Message Property PublicConfirm Auto Const Mandatory
Message Property EarlierChoice Auto Const Mandatory
Message Property Missing Auto Const Mandatory
Message Property Pending Auto Const Mandatory
Message Property SliceEnd Auto Const Mandatory
Message Property TaskBeckett Auto Const Mandatory
Message Property TaskPorch Auto Const Mandatory
Message Property TaskReturn Auto Const Mandatory
ReferenceAlias Property Alias_EntryGuide Auto Const Mandatory
Quest sourceOwner = None
ObjectReference entryPoint = None
ObjectReference mercyReturn = None
Bool busy = false
Bool[] saved
Bool[] visitPending
Bool[] staged
Actor[] visitors
Bool[] wasDisabled

TLM:MQ04Quest Function Road()
    Return TLM_MQ04 as TLM:MQ04Quest
EndFunction

Bool Function Bind(Quest actualSource, ObjectReference actualEntry, ObjectReference actualReturn)
    If !actualSource || !actualSource.IsRunning() || !actualEntry || !actualReturn || actualEntry == actualReturn
        Return false
    EndIf
    If sourceOwner && (sourceOwner != actualSource || entryPoint != actualEntry || mercyReturn != actualReturn)
        Return false
    EndIf
    sourceOwner = actualSource
    entryPoint = actualEntry
    mercyReturn = actualReturn
    actualEntry.Enable()
    Return true
EndFunction

Bool Function SetUp()
    If !Road().LeadKnown() || Road().GetStageDone(110)
        Return false
    EndIf
    If !IsRunning()
        If !Start() || !IsRunning()
            Return false
        EndIf
    EndIf
    TLM:Act1Walk first = sourceOwner as TLM:Act1Walk
    If !first || !Road().LeadKnown()
        Return false
    EndIf
    Actor[] actual = new Actor[3]
    Int index = 0
    While index < 3
        actual[index] = first.BlackLedgerActor(index)
        index += 1
    EndWhile
    If !Road().Initialize(actual)
        Return false
    EndIf
    Alias_EntryGuide.ForceRefTo(entryPoint)
    If !saved
        saved = new Bool[2]
        visitPending = new Bool[2]
        staged = new Bool[2]
        wasDisabled = new Bool[2]
        visitors = new Actor[2]
    EndIf
    Return true
EndFunction

Function Loaded()
    Road().Loaded()
    ClockGap()
    busy = false
EndFunction

Bool Function IsVisiting(Actor who)
    If !who || !visitors || !visitPending
        Return false
    EndIf
    Return (visitPending[0] && visitors[0] == who) || (visitPending[1] && visitors[1] == who)
EndFunction

Bool Function Role(Actor who, Int roleNumber, Int capturedEpoch)
    If roleNumber == 3
        Return Road().Beckett(who,capturedEpoch)
    EndIf
    Return Road().Speaker(who,roleNumber,capturedEpoch)
EndFunction

Bool Function NodeCondition(String node, Int capturedEpoch)
    If node == "vickers_door" || node == "vickers_glove"
        Return Road().GetStageDone(30) && Road().Resolution() == 0 && Road().Current(capturedEpoch)
    EndIf
    If node == "pritchard_warrant_beckett" || node == "beckett_warrant_terms" || node == "pritchard_book_receipt"
        Return Road().GetStageDone(40) && Road().Resolution() == 0 && Road().Beckett(Road().Alias_Beckett.GetActorReference(),capturedEpoch) && Road().WarrantPresent(capturedEpoch)
    EndIf
    If node == "vane_porch" || node == "pritchard_porch"
        Return Road().GetStageDone(50) && Road().PorchContext(capturedEpoch)
    EndIf
    If node == "vane_after_read" || node == "vane_names"
        Return Road().GetStageDone(30) && Road().Resolution() == 61 && Road().Current(capturedEpoch)
    EndIf
    If node == "haskell_sheet" || node == "haskell_tells"
        Return Road().LeadKnown() && !Road().BlackstoneKnown() && Road().Current(capturedEpoch)
    EndIf
    Return Road().LeadKnown() && !Road().GetStageDone(30) && Road().Current(capturedEpoch)
EndFunction

Int Function Say(String node, Actor speakerActor, Int roleNumber, Int capturedEpoch)
    Int index = 0
    While index < SpeechNames.Length && SpeechNames[index] != node
        index += 1
    EndWhile
    If index == SpeechNames.Length
        Return -1
    EndIf
    Int page = 0
    Int answer = -1
    While page < SpeechSize[index]
        If !Role(speakerActor,roleNumber,capturedEpoch) || !NodeCondition(node,capturedEpoch)
            Return -1
        EndIf
        answer = Speech[SpeechStart[index] + page].Show()
        If !Role(speakerActor,roleNumber,capturedEpoch) || !NodeCondition(node,capturedEpoch)
            Return -1
        EndIf
        If page < SpeechSize[index] - 1 && answer != 0
            Return -1
        EndIf
        page += 1
    EndWhile
    If answer < 0 || answer >= SpeechButtons[index]
        Return -1
    EndIf
    Return answer
EndFunction

Bool Function OfferSheriff(Actor sheriffActor)
    If busy || !SetUp()
        Return false
    EndIf
    Int capturedEpoch = Road().Epoch()
    If !Role(sheriffActor,0,capturedEpoch)
        Return false
    EndIf
    If Road().GetStageDone(50)
        busy = true
        If Road().Resolution() == 0
            Say("pritchard_porch",sheriffActor,0,capturedEpoch)
        EndIf
        busy = false
        Return true
    EndIf
    busy = true
    If Road().GetStageDone(30)
        CurrentTask()
        busy = false
        Return true
    EndIf
    If !Road().GetStageDone(10)
        Int answer = Lead.Show()
        If answer != 0 || !Role(sheriffActor,0,capturedEpoch)
            busy = false
            Return true
        EndIf
    EndIf
    Int answer = Say("pritchard_warrant",sheriffActor,0,capturedEpoch)
    If answer >= 0 && Road().RecordOffer(sheriffActor,capturedEpoch)
        If answer == 0
            If Road().RequestWarrant(sheriffActor,capturedEpoch)
                Transfer(1,capturedEpoch)
            EndIf
        ElseIf answer == 2
            Say("pritchard_guilty",sheriffActor,0,capturedEpoch)
        ElseIf answer == 3
            Friendship(sheriffActor,capturedEpoch)
        EndIf
    EndIf
    busy = false
    Return true
EndFunction

Function Friendship(Actor sheriffActor, Int capturedEpoch)
    Int answer = Say("pritchard_friend",sheriffActor,0,capturedEpoch)
    If answer == 0
        answer = Say("pritchard_friend_answer",sheriffActor,0,capturedEpoch)
        If answer != 0
            Return
        EndIf
    ElseIf answer != 1
        Return
    EndIf
    answer = Say("pritchard_warrant_next",sheriffActor,0,capturedEpoch)
    If answer == 0 && Road().RequestWarrant(sheriffActor,capturedEpoch)
        Transfer(1,capturedEpoch)
    EndIf
EndFunction

Bool Function Transfer(Int kind, Int capturedEpoch)
    If Road().TransferComplete(kind)
        Return true
    EndIf
    If Road().TransferPending() != 0
        ; Only acknowledgment of the same issued intent is attempted. No reissue.
        Return Road().AckTransfer(kind,capturedEpoch)
    EndIf
    If kind == 3 && Road().AcknowledgeHeldOriginal(capturedEpoch)
        Return true
    EndIf
    If !Road().BeginTransfer(kind,capturedEpoch)
        Return false
    EndIf
    ObjectReference itemRef = Road().TransferReference(kind)
    ObjectReference receiver = Road().TransferReceiver(kind)
    If !itemRef || !receiver || !Road().MarkTransferIssued(kind,capturedEpoch)
        Return false
    EndIf
    ObjectReference holder = itemRef.GetContainer()
    If holder || itemRef != Road().TransferReference(kind) || receiver != Road().TransferReceiver(kind) || !Road().Current(capturedEpoch)
        Return false
    EndIf
    If !Road().EffectParticipants(kind,capturedEpoch)
        Return false
    EndIf
    ; Physical source/recipient receipt follows the yielding participant reads.
    ObjectReference finalReceiver = Road().TransferReceiver(kind)
    ObjectReference finalReference = Road().TransferReference(kind)
    ObjectReference finalHolder = itemRef.GetContainer()
    If finalHolder || finalReceiver != receiver || finalReference != itemRef || capturedEpoch != Road().Epoch()
        Return false
    EndIf
    receiver.AddItem(itemRef,1,true)
    Return Road().AckTransfer(kind,capturedEpoch)
EndFunction

Function ClockGap()
    TLM:Act1Walk first = sourceOwner as TLM:Act1Walk
    If first && first.TLM_RedHollow
        (first.TLM_RedHollow as TLM:RedHollowWalk).FairTransitGap()
    EndIf
EndFunction

Bool Function EntryCurrent(Int capturedEpoch)
    TLM:Act1Walk first = sourceOwner as TLM:Act1Walk
    Return first && first.CanVisitFair() && entryPoint && Road().At(Game.GetPlayer(),entryPoint,384.0) && Road().Current(capturedEpoch)
EndFunction

Bool Function StageOriginals(Int capturedEpoch)
    TLM:Act1Walk first = sourceOwner as TLM:Act1Walk
    Int index = 0
    While index < 2
        Actor who = Road().OriginalActor(index)
        ObjectReference anchor = RoomSlots[index].GetReference()
        ObjectReference home = ReturnSlots[index].GetReference()
        Bool eligible = who && first && first.BlackLedgerActor(index) == who && !who.IsDead() && !who.IsDisabled() && !who.IsInCombat() && !who.IsInScene() && !who.IsInDialogueWithPlayer() && anchor && home && Road().Current(capturedEpoch)
        If index == 0
            If !visitPending[index]
                eligible = eligible && first.FairActorAvailable(who)
            EndIf
            If first.TLM_FourFlags && (first.TLM_FourFlags as TLM:FourFlagsWalk).IsVisiting(who)
                eligible = false
            EndIf
        EndIf
        If !eligible
            Return false
        EndIf
        If !saved[index]
            home.Enable()
            If home.IsDisabled() || !home.Is3DLoaded()
                Return false
            EndIf
            home.MoveTo(who)
            If !Road().At(home,who,16.0) || !Road().Current(capturedEpoch) || first.BlackLedgerActor(index) != who
                Return false
            EndIf
            visitors[index] = who
            wasDisabled[index] = who.IsDisabled()
            saved[index] = true
        EndIf
        If visitors[index] != who
            Return false
        EndIf
        ; Saved-state/native context reads can invalidate an initially eligible
        ; actor. Observe its current original identity/readiness before moving.
        If !Road().Current(capturedEpoch) || first.BlackLedgerActor(index) != who || who.IsInScene() || who.IsInDialogueWithPlayer() || who.IsTalking() || who.IsDisabled() || who.IsInCombat() || who.IsDead() || capturedEpoch != Road().Epoch()
            Return false
        EndIf
        visitPending[index] = true
        who.MoveTo(anchor)
        If !Road().At(who,anchor,96.0) || !Road().Current(capturedEpoch) || first.BlackLedgerActor(index) != who
            Return false
        EndIf
        staged[index] = true
        index += 1
    EndWhile
    Return true
EndFunction

Function ReturnOriginals(Int capturedEpoch)
    Int index = 0
    While index < 2
        If visitPending && visitPending[index]
            Actor who = visitors[index]
            ObjectReference home = ReturnSlots[index].GetReference()
            If who && who.IsDead()
                visitPending[index] = false
                staged[index] = false
                saved[index] = false
            ElseIf who && home && Road().Current(capturedEpoch) && who == Road().OriginalActor(index) && !who.IsInScene() && !who.IsInDialogueWithPlayer() && !who.IsTalking() && !who.IsDisabled() && !who.IsInCombat() && !who.IsDead() && capturedEpoch == Road().Epoch()
                who.MoveTo(home)
                If Road().At(who,home,96.0) && Road().Current(capturedEpoch) && who == Road().OriginalActor(index)
                    If wasDisabled[index]
                        who.Disable()
                    EndIf
                    visitPending[index] = false
                    staged[index] = false
                EndIf
            EndIf
        EndIf
        index += 1
    EndWhile
EndFunction

Function EnterRoom()
    If busy || !SetUp()
        Return
    EndIf
    busy = true
    Int capturedEpoch = Road().Epoch()
    If !EntryCurrent(capturedEpoch) || !Road().WarrantRequested() || !Road().WarrantPresent(capturedEpoch)
        Missing.Show()
        busy = false
        Return
    EndIf
    Int answer = Travel.Show()
    If answer != 0 || !EntryCurrent(capturedEpoch) || !Road().WarrantPresent(capturedEpoch)
        busy = false
        Return
    EndIf
    ClockGap()
    Int index = 0
    While index < StageOn.Length
        StageOn[index].GetReference().Enable()
        index += 1
    EndWhile
    ObjectReference arrival = Alias_Arrival.GetReference()
    If !arrival || !Road().Current(capturedEpoch)
        busy = false
        Return
    EndIf
    Game.GetPlayer().MoveTo(arrival)
    ClockGap()
    If Road().At(Game.GetPlayer(),arrival,128.0)
        If !StageOriginals(capturedEpoch) || !Road().RecordLawfulAccess(capturedEpoch)
            Pending.Show()
        EndIf
    EndIf
    busy = false
EndFunction

Function PreparePorch(Int capturedEpoch)
    ObjectReference porchRef = Road().Alias_Porch.GetReference()
    ObjectReference home = ReturnSlots[1].GetReference()
    If !porchRef || !home || !saved[1] || !Road().Current(capturedEpoch)
        Return
    EndIf
    porchRef.MoveTo(home)
    If !Road().At(porchRef,home,16.0) || !Road().Current(capturedEpoch)
        Return
    EndIf
    Int visitorIndex = 0
    While visitorIndex < 2
        Actor who = visitors[visitorIndex]
        If !who || who != Road().OriginalActor(visitorIndex) || who.IsDead() || who.IsInCombat() || !Road().Current(capturedEpoch)
            Return
        EndIf
        ObjectReference anchor = RoomSlots[visitorIndex].GetReference()
        If visitorIndex == 0
            anchor.MoveTo(porchRef,60.0,-280.0,16.0)
        Else
            anchor.MoveTo(porchRef)
        EndIf
        If !Road().Current(capturedEpoch) || who != Road().OriginalActor(visitorIndex) || who.IsInScene() || who.IsInDialogueWithPlayer() || who.IsTalking() || who.IsDisabled() || who.IsInCombat() || who.IsDead() || capturedEpoch != Road().Epoch()
            Return
        EndIf
        who.MoveTo(anchor)
        If !Road().At(who,anchor,96.0) || !Road().Current(capturedEpoch)
            Return
        EndIf
        visitorIndex += 1
    EndWhile
    Int index = 0
    While index < Road().Witnesses.Length
        Actor witnessActor = Road().Witnesses[index].GetActorReference()
        ObjectReference anchor = PorchWitnessSlots[index].GetReference()
        If !witnessActor || witnessActor.IsDead() || !anchor || !Road().Current(capturedEpoch)
            Return
        EndIf
        If index == 0
            anchor.MoveTo(porchRef,60.0,160.0,16.0)
        Else
            anchor.MoveTo(porchRef,-220.0,220.0,16.0)
        EndIf
        witnessActor.Enable()
        If !Road().Current(capturedEpoch) || Road().Witnesses[index].GetActorReference() != witnessActor || witnessActor.IsInScene() || witnessActor.IsInDialogueWithPlayer() || witnessActor.IsTalking() || witnessActor.IsDisabled() || witnessActor.IsInCombat() || witnessActor.IsDead() || capturedEpoch != Road().Epoch()
            Return
        EndIf
        witnessActor.MoveTo(anchor)
        If !Road().At(witnessActor,anchor,96.0) || !Road().Current(capturedEpoch)
            Return
        EndIf
        index += 1
    EndWhile
EndFunction

Function LeaveRoom()
    If busy || !Road().Current(Road().Epoch())
        Return
    EndIf
    busy = true
    Int capturedEpoch = Road().Epoch()
    Int answer = ExitPrompt.Show()
    If answer == 0 && Road().Current(capturedEpoch)
        ClockGap()
        Bool preparePublic = Road().BookHeld() && Road().GetStageDone(43) && Road().Resolution() == 0
        If !preparePublic
            ReturnOriginals(capturedEpoch)
        EndIf
        Actor playerActor = Game.GetPlayer()
        If mercyReturn && Road().Current(capturedEpoch)
            playerActor.MoveTo(mercyReturn)
            ClockGap()
            If preparePublic && Road().At(playerActor,mercyReturn,128.0)
                PreparePorch(capturedEpoch)
            EndIf
        EndIf
    EndIf
    busy = false
EndFunction

Function ReadBook()
    If busy
        Return
    EndIf
    Int capturedEpoch = Road().Epoch()
    ObjectReference bookRef = Road().TransferReference(3)
    If !Road().BeginRead(bookRef,capturedEpoch)
        Return
    EndIf
    busy = true
    Int index = 0
    While index < BookPages.Length
        If !Road().BookAccess(bookRef,capturedEpoch) || BookPages[index].Show() != 0 || !Road().AckReadPage(bookRef,index,capturedEpoch)
            busy = false
            Return
        EndIf
        index += 1
    EndWhile
    busy = false
EndFunction

Function BeckettTalk(Actor beckettActor)
    If busy
        Return
    EndIf
    Int capturedEpoch = Road().Epoch()
    If !Road().RecordDoorway(beckettActor,capturedEpoch)
        Return
    EndIf
    busy = true
    Int answer = 0
    If !Road().GetStageDone(43)
        answer = Say("vickers_door",beckettActor,3,capturedEpoch)
    EndIf
    If answer == 1
        Say("vickers_glove",beckettActor,3,capturedEpoch)
    ElseIf answer == 0
        Actor sheriffActor = Road().OriginalActor(0)
        If Road().WarrantPresent(capturedEpoch) && Say("pritchard_warrant_beckett",sheriffActor,0,capturedEpoch) == 0
            answer = Say("beckett_warrant_terms",beckettActor,3,capturedEpoch)
            If answer == 0
                Road().AllowInspection(beckettActor,capturedEpoch)
            ElseIf answer == 1
                answer = Say("pritchard_book_receipt",sheriffActor,0,capturedEpoch)
                If (answer == 0 || answer == 1) && Road().AllowInspection(beckettActor,capturedEpoch)
                    If answer == 0
                        If Transfer(2,capturedEpoch)
                            Transfer(3,capturedEpoch)
                        Else
                            Pending.Show()
                        EndIf
                    EndIf
                EndIf
            EndIf
        EndIf
    EndIf
    busy = false
EndFunction

Bool Function OfferActor(Actor actorRef, Int roleNumber)
    If busy || !SetUp() || !Role(actorRef,roleNumber,Road().Epoch())
        Return false
    EndIf
    If roleNumber == 1 && !Road().GetStageDone(10)
        Return false
    EndIf
    Int capturedEpoch = Road().Epoch()
    busy = true
    Int answer = EarlierChoice.Show()
    If answer == 1
        Bool stillCurrent = Role(actorRef,roleNumber,capturedEpoch)
        busy = false
        Return !stillCurrent
    EndIf
    If answer != 0 || !Role(actorRef,roleNumber,capturedEpoch)
        busy = false
        Return true
    EndIf
    If roleNumber == 1
        If Road().Resolution() == 61
            answer = Say("vane_after_read",actorRef,1,capturedEpoch)
            If answer == 0 && Say("vane_names",actorRef,1,capturedEpoch) == 0
                If Road().LearnBlackstone(actorRef,1,capturedEpoch)
                    SliceEnd.Show()
                EndIf
            EndIf
        ElseIf !Road().GetStageDone(30)
            answer = Say("vane_two_books",actorRef,1,capturedEpoch)
            If answer == 0
                Say("vane_refuses",actorRef,1,capturedEpoch)
            ElseIf answer == 1
                Say("vane_silver_early",actorRef,1,capturedEpoch)
            EndIf
        Else
            CurrentTask()
        EndIf
    ElseIf roleNumber == 2
        answer = Say("haskell_sheet",actorRef,2,capturedEpoch)
        If answer == 0 && Say("haskell_tells",actorRef,2,capturedEpoch) == 0
            If Road().LearnBlackstone(actorRef,2,capturedEpoch)
                SliceEnd.Show()
            EndIf
        EndIf
    EndIf
    busy = false
    Return true
EndFunction

Function PublicReading()
    If busy
        Return
    EndIf
    Int capturedEpoch = Road().Epoch()
    If !Road().PorchContext(capturedEpoch)
        Missing.Show()
        Return
    EndIf
    busy = true
    If PublicReady.Show() != 0 || !Road().BeginPorch(capturedEpoch)
        busy = false
        Return
    EndIf
    Actor vaneActor = Road().OriginalActor(1)
    If Say("vane_porch",vaneActor,1,capturedEpoch) != 0 || !Road().PorchContext(capturedEpoch) || PublicConfirm.Show() != 0 || !Road().BeginPublicRead(capturedEpoch)
        busy = false
        Return
    EndIf
    Int index = 0
    While index < BookPages.Length
        If !Road().PorchContext(capturedEpoch) || BookPages[index].Show() != 0 || !Road().AckPublicPage(index,capturedEpoch)
            busy = false
            Return
        EndIf
        index += 1
    EndWhile
    If Road().CommitPublicRead(capturedEpoch)
        ; This remains the actual original Vane; earlier committed roads stay untouched.
        Int answer = Say("vane_after_read",vaneActor,1,capturedEpoch)
        If answer == 0 && Say("vane_names",vaneActor,1,capturedEpoch) == 0
            If Road().LearnBlackstone(vaneActor,1,capturedEpoch)
                SliceEnd.Show()
            EndIf
        EndIf
    EndIf
    busy = false
EndFunction

Function RetryAccess()
    If busy || !Road().Current(Road().Epoch()) || !Road().At(Game.GetPlayer(),Alias_Arrival.GetReference(),512.0)
        Return
    EndIf
    busy = true
    Int capturedEpoch = Road().Epoch()
    If !StageOriginals(capturedEpoch) || !Road().RecordLawfulAccess(capturedEpoch)
        Pending.Show()
    EndIf
    busy = false
EndFunction

Function FinishEncounter()
    If busy || !Road().Current(Road().Epoch())
        Return
    EndIf
    busy = true
    ReturnOriginals(Road().Epoch())
    If !visitPending[0] && !visitPending[1]
        If Road().CompleteChapter(Road().Epoch())
            SliceEnd.Show()
        EndIf
    EndIf
    busy = false
EndFunction

Function CurrentTask()
    If Road().Resolution() == 61
        TaskReturn.Show()
    ElseIf Road().GetStageDone(43) && Road().BookHeld()
        TaskPorch.Show()
    Else
        TaskBeckett.Show()
    EndIf
EndFunction
