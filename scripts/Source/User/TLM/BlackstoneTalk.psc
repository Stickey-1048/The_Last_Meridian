Scriptname TLM:BlackstoneTalk extends ReferenceAlias
Quest Property TLM_MQ05 Auto Const Mandatory
Int Property Who Auto Const Mandatory
Event OnActivate(ObjectReference akActionRef)
    If akActionRef != Game.GetPlayer()
        Return
    EndIf
    TLM:BlackstoneWalk walk = TLM_MQ05 as TLM:BlackstoneWalk
    If Who >= 0 && Who < 6
        walk.ReadDocument(Who)
    ElseIf Who == 10
        walk.Talk(GetActorReference())
    ElseIf Who == 11
        walk.UseMechanical()
    ElseIf Who == 12
        walk.ReadSign(GetReference())
    ElseIf Who >= 20 && Who < 26
        walk.Travel(Who - 20)
    EndIf
EndEvent
Event OnPlayerLoadGame()
    If Who == -1
        (TLM_MQ05 as TLM:BlackstoneWalk).Loaded()
    EndIf
EndEvent
