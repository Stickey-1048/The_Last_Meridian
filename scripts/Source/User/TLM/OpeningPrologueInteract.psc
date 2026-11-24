Scriptname TLM:OpeningPrologueInteract extends ReferenceAlias
{Only the new prologue's three ordinary interactions. No story rules here.}
int Property Role Auto Const Mandatory
Event OnActivate(ObjectReference akActionRef)
 TLM:OpeningPrologue controller = GetOwningQuest() as TLM:OpeningPrologue
 If controller
  controller.Interact(akActionRef,GetReference(),Role)
 EndIf
EndEvent
Event OnDeath(Actor akKiller)
 If Role == 2
  TLM:OpeningPrologue controller = GetOwningQuest() as TLM:OpeningPrologue
  If controller
   controller.MarshalDied(GetActorReference())
  EndIf
 EndIf
EndEvent

