Scriptname TLM:BlackstoneWalk extends Quest
{Ordinary bounded station interactions. Text acknowledgments are not native voice.
No outcome on refusal, no artificial actor rescue, no automatic road completion.}
Quest Property TLM_MQ05 Auto Const Mandatory
ReferenceAlias[] Property Controls Auto Const Mandatory
ReferenceAlias[] Property Destinations Auto Const Mandatory
ObjectReference[] Property ControlIdentity Auto Const
ObjectReference[] Property DestinationIdentity Auto Const
Message[] Property Speech Auto Const Mandatory
Int[] Property NodeStart Auto Const Mandatory
Int[] Property NodeSize Auto Const Mandatory
Message[] Property DocumentText Auto Const Mandatory
Int[] Property DocumentStart Auto Const Mandatory
Message Property MechanicalPrompt Auto Const Mandatory
Message Property PassPrompt Auto Const Mandatory
Message Property ReturnPrompt Auto Const Mandatory
Message Property MissingReading Auto Const Mandatory
Message Property UpperDirections Auto Const Mandatory
Message Property TravelFailed Auto Const Mandatory
Bool busy = false
Int busyEpoch = -1
ObjectReference[] originalControls
ObjectReference[] originalDestinations

TLM:MQ05Quest Function Road()
    Return TLM_MQ05 as TLM:MQ05Quest
EndFunction
Bool Function SetUp()
    If !Road().OpenLead()
        Return false
    EndIf
    If !originalControls
        If !Controls || Controls.Length != 7 || !Destinations || Destinations.Length != 7 || !ControlIdentity || ControlIdentity.Length != 7 || !DestinationIdentity || DestinationIdentity.Length != 7
            Return false
        EndIf
        ObjectReference[] controlsNow = new ObjectReference[7]
        ObjectReference[] destinationsNow = new ObjectReference[7]
        Int index = 0
        While index < 7
            controlsNow[index] = ControlIdentity[index]
            destinationsNow[index] = DestinationIdentity[index]
            If !controlsNow[index] || !destinationsNow[index] || Controls[index].GetReference() != controlsNow[index] || Destinations[index].GetReference() != destinationsNow[index]
                Return false
            EndIf
            index += 1
        EndWhile
        originalControls = controlsNow
        originalDestinations = destinationsNow
        index = 0
        While index < 7
            originalControls[index].BlockActivation(true)
            If index < 6
                ObjectReference docRef = Road().Document(index)
                If docRef
                    docRef.BlockActivation(true)
                EndIf
            EndIf
            index += 1
        EndWhile
    EndIf
    Return true
EndFunction
Function Loaded()
    Road().Loaded()
    busy = false
    busyEpoch = -1
EndFunction
Bool Function Claim()
    If busy || !SetUp()
        Return false
    EndIf
    busy = true
    busyEpoch = Road().Epoch()
    Return true
EndFunction
Function ReleaseActivation(Int capturedEpoch)
    If busyEpoch == capturedEpoch
        busy = false
        busyEpoch = -1
    EndIf
EndFunction
Bool Function TravelContext(Int route, Int capturedEpoch)
    If route < 0 || route >= 7 || !Road().Current(capturedEpoch)
        Return false
    EndIf
    ObjectReference controlRef = Controls[route].GetReference()
    ObjectReference destination = Destinations[route].GetReference()
    If controlRef != originalControls[route] || destination != originalDestinations[route] || controlRef.IsDisabled() || !controlRef.Is3DLoaded() || destination.IsDisabled() || !Road().At(Game.GetPlayer(),controlRef,192.0)
        Return false
    EndIf
    Return capturedEpoch == Road().Epoch()
EndFunction
Bool Function MovePlayer(Int route, Int capturedEpoch)
    If !TravelContext(route,capturedEpoch)
        Return false
    EndIf
    Actor playerActor = Game.GetPlayer()
    ObjectReference destination = originalDestinations[route]
    If capturedEpoch != Road().Epoch()
        Return false
    EndIf
    playerActor.MoveTo(destination)
    Return Road().Current(capturedEpoch) && Road().At(playerActor,destination,128.0) && playerActor == Game.GetPlayer() && capturedEpoch == Road().Epoch()
EndFunction
Bool Function ReadPages(Int kind, Int capturedEpoch)
    If kind == 4
        Road().AnchorDiagram(Road().Document(4))
    EndIf
    If !Road().BeginDocument(kind,capturedEpoch)
        Return false
    EndIf
    Int index = 0
    While index < Road().DocumentPages[kind]
        If !Road().DocumentAccess(kind,capturedEpoch) || DocumentText[DocumentStart[kind] + index].Show() != 0
            Return false
        EndIf
        If index == Road().DocumentPages[kind] - 1
            Int acknowledgment = -1
            If kind == 1
                acknowledgment = 8
            ElseIf kind == 2
                acknowledgment = 9
            ElseIf kind == 3
                acknowledgment = 21
            EndIf
            If acknowledgment >= 0 && Panel(acknowledgment,capturedEpoch) != 0
                Return false
            EndIf
        EndIf
        If !Road().AckDocumentPage(kind,index,capturedEpoch)
            Return false
        EndIf
        index += 1
    EndWhile
    Return capturedEpoch == Road().Epoch()
EndFunction
Function ReadDocument(Int kind)
    If !Claim()
        Return
    EndIf
    Int capturedEpoch = busyEpoch
    If ReadPages(kind,capturedEpoch)
        If kind == 0
            If TravelContext(0,capturedEpoch) && Panel(0,capturedEpoch) == 0 && Road().GetStageDone(20)
                If MovePlayer(0,capturedEpoch)
                    If Road().AcknowledgeUpper(capturedEpoch)
                        UpperDirections.Show()
                    EndIf
                ElseIf capturedEpoch == Road().Epoch()
                    TravelFailed.Show()
                EndIf
            EndIf
        ElseIf kind == 5
            If Road().DocumentAccess(5,capturedEpoch) && PassPrompt.Show() == 0 && Road().BeginPassIssue(capturedEpoch)
                ObjectReference passRef = Road().Document(5)
                Actor playerActor = Game.GetPlayer()
                If Road().Current(capturedEpoch) && Road().DocumentAccess(5,capturedEpoch)
                    ObjectReference holder = passRef.GetContainer()
                    If !holder && playerActor == Game.GetPlayer() && capturedEpoch == Road().Epoch()
                        playerActor.AddItem(passRef,1,true)
                        Road().AckPassIssue(capturedEpoch)
                    EndIf
                EndIf
            EndIf
        ElseIf kind == 4
            Int answer = Panel(22,capturedEpoch)
            If Road().DocumentAccess(4,capturedEpoch)
                If answer == 0
                    If ReadPages(5,capturedEpoch)
                        If Road().DocumentAccess(5,capturedEpoch) && PassPrompt.Show() == 0
                            TakePass(capturedEpoch)
                        EndIf
                    EndIf
                ElseIf answer == 1
                    Mechanical(capturedEpoch)
                EndIf
            EndIf
        EndIf
    EndIf
    ReleaseActivation(capturedEpoch)
EndFunction
Function TakePass(Int capturedEpoch)
    If !Road().BeginPassIssue(capturedEpoch) || !Road().Current(capturedEpoch) || !Road().DocumentAccess(5,capturedEpoch)
        Return
    EndIf
    ObjectReference passRef = Road().Document(5)
    Actor playerActor = Game.GetPlayer()
    ObjectReference holder = passRef.GetContainer()
    If !holder && playerActor == Game.GetPlayer() && capturedEpoch == Road().Epoch()
        playerActor.AddItem(passRef,1,true)
        Road().AckPassIssue(capturedEpoch)
    EndIf
EndFunction
Function Talk(Actor speakerActor)
    If !Claim()
        Return
    EndIf
    Int capturedEpoch = busyEpoch
    If speakerActor != Road().Alias_Mara.GetActorReference()
        ReleaseActivation(capturedEpoch)
        Return
    EndIf
    Int node = Road().BeginTalk(capturedEpoch)
    While node >= 0
        Int page = 0
        Int answer = -1
        While page < NodeSize[node]
            If !Road().CanShowNode(node,capturedEpoch)
                ReleaseActivation(capturedEpoch)
                Return
            EndIf
            answer = Speech[NodeStart[node] + page].Show()
            If !Road().CanShowNode(node,capturedEpoch) || (page < NodeSize[node] - 1 && answer != 0)
                ReleaseActivation(capturedEpoch)
                Return
            EndIf
            page += 1
        EndWhile
        node = Road().AckChoice(node,answer,capturedEpoch)
    EndWhile
    ReleaseActivation(capturedEpoch)
EndFunction
Function Mechanical(Int capturedEpoch)
    If !Road().MechanicalContext(capturedEpoch)
        Debug.Notification("The mechanical release is beside the lower service door. Walk over to its control.")
        Return
    EndIf
    If MechanicalPrompt.Show() != 0 || !Road().MechanicalContext(capturedEpoch)
        Return
    EndIf
    ObjectReference doorRef = Road().DoorReference()
    If capturedEpoch != Road().Epoch()
        Return
    EndIf
    doorRef.Lock(false)
    If Road().AcknowledgeRelease(capturedEpoch)
        UpperDirections.Show()
    EndIf
EndFunction
Function UseMechanical()
    If !Claim()
        Return
    EndIf
    Int capturedEpoch = busyEpoch
    If !Road().GetStageDone(60)
        ReadPages(4,capturedEpoch)
    EndIf
    Mechanical(capturedEpoch)
    ReleaseActivation(capturedEpoch)
EndFunction
Function UseLowerDoor()
    If !Claim()
        Return
    EndIf
    Int capturedEpoch = busyEpoch
    If TravelContext(4,capturedEpoch) && Road().PassDoorContext(capturedEpoch)
        ObjectReference doorRef = Road().DoorReference()
        If capturedEpoch == Road().Epoch()
            doorRef.Lock(false)
        EndIf
    EndIf
    If Road().DoorContext(capturedEpoch) && Panel(23,capturedEpoch) == 0 && Road().BeginEntry(capturedEpoch)
        If MovePlayer(4,capturedEpoch)
            If Road().CompleteAtLower(capturedEpoch)
                Boundary(capturedEpoch)
            ElseIf Road().Current(capturedEpoch)
                MissingReading.Show()
            EndIf
        ElseIf Road().Current(capturedEpoch)
            TravelFailed.Show()
        EndIf
    EndIf
    ReleaseActivation(capturedEpoch)
EndFunction
Function Boundary(Int capturedEpoch)
    If !Road().GetStageDone(100) || !Road().Current(capturedEpoch) || !Road().At(Game.GetPlayer(),Road().Alias_LowerArrival.GetReference(),384.0)
        Return
    EndIf
    Int answer = Panel(24,capturedEpoch)
    If answer == 1 && Road().Current(capturedEpoch)
        MovePlayer(6,capturedEpoch)
    EndIf
EndFunction
Function Travel(Int route)
    If route == 4
        UseLowerDoor()
        Return
    EndIf
    If !Claim()
        Return
    EndIf
    Int capturedEpoch = busyEpoch
    If route == 6
        If Road().CompleteAtLower(capturedEpoch)
            Boundary(capturedEpoch)
        Else
            MissingReading.Show()
        EndIf
        ReleaseActivation(capturedEpoch)
        Return
    EndIf
    If route == 0
        ; The original sheet, not a separate free travel menu, owns the journey.
        ReleaseActivation(capturedEpoch)
        ReadDocument(0)
        Return
    EndIf
    If TravelContext(route,capturedEpoch) && ReturnPrompt.Show() == 0 && MovePlayer(route,capturedEpoch)
        If route == 2
            UpperDirections.Show()
        EndIf
    EndIf
    ReleaseActivation(capturedEpoch)
EndFunction

Function ReadSign(ObjectReference signRef)
    If !Claim()
        Return
    EndIf
    Int capturedEpoch = busyEpoch
    If Road().Current(capturedEpoch) && Road().At(Game.GetPlayer(),signRef,192.0)
        UpperDirections.Show()
    EndIf
    ReleaseActivation(capturedEpoch)
EndFunction

Bool Function PanelCurrent(Int node, Int capturedEpoch)
    If !Road().Current(capturedEpoch)
        Return false
    EndIf
    If node == 0
        Return Road().GetStageDone(20) && TravelContext(0,capturedEpoch)
    ElseIf node == 8
        Return Road().DocumentAccess(1,capturedEpoch)
    ElseIf node == 9
        Return Road().DocumentAccess(2,capturedEpoch)
    ElseIf node == 21
        Return Road().DocumentAccess(3,capturedEpoch)
    ElseIf node == 22
        Return Road().GetStageDone(60) && Road().DocumentAccess(4,capturedEpoch)
    ElseIf node == 23
        Return Road().DoorContext(capturedEpoch)
    ElseIf node == 24
        Return Road().GetStageDone(100) && Road().At(Game.GetPlayer(),Road().LowerReference(),384.0) && capturedEpoch == Road().Epoch()
    EndIf
    Return false
EndFunction
Int Function Panel(Int node, Int capturedEpoch)
    Int page = 0
    Int answer = -1
    While page < NodeSize[node]
        If !PanelCurrent(node,capturedEpoch)
            Return -1
        EndIf
        answer = Speech[NodeStart[node] + page].Show()
        If !PanelCurrent(node,capturedEpoch) || (page < NodeSize[node] - 1 && answer != 0)
            Return -1
        EndIf
        page += 1
    EndWhile
    If answer < 0 || answer >= Road().ChoiceCount[node]
        Return -1
    EndIf
    Return answer
EndFunction
