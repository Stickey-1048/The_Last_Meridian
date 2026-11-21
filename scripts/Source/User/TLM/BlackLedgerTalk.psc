Scriptname TLM:BlackLedgerTalk extends ReferenceAlias
{Owned control/Beckett/player events only. Visiting originals keep their existing Act1Talk.}
Int Property Who Auto Const Mandatory
Quest Property MainQuest Auto Const
TLM:BlackLedgerWalk Function Walk()
    Quest owner = MainQuest
    If !owner
        owner = GetOwningQuest()
    EndIf
    Return owner as TLM:BlackLedgerWalk
EndFunction
Event OnActivate(ObjectReference akActionRef)
    If akActionRef != Game.GetPlayer()
        Return
    EndIf
    TLM:BlackLedgerWalk chapter = Walk()
    If !chapter
        Return
    EndIf
    If Who == 1
        chapter.EnterRoom()
    ElseIf Who == 2
        chapter.LeaveRoom()
    ElseIf Who == 3
        chapter.ReadBook()
    ElseIf Who == 4
        chapter.BeckettTalk(GetActorReference())
    ElseIf Who == 5
        chapter.PublicReading()
    ElseIf Who == 6
        chapter.RetryAccess()
    ElseIf Who == 8
        chapter.FinishEncounter()
    EndIf
EndEvent
Event OnPlayerLoadGame()
    If Who == -1
        TLM:BlackLedgerWalk chapter = Walk()
        If chapter
            chapter.Loaded()
        EndIf
    EndIf
EndEvent
