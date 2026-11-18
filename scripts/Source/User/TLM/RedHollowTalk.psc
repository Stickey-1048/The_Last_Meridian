Scriptname TLM:RedHollowTalk extends ReferenceAlias
{Alias event forwarding only. Source candidate; no native acceptance.}

int Property Who Auto Const Mandatory
; Supported CK ReferenceAlias events; prime invalidation only. Actual delivery
; timing is a native gate, not inferred from explicit synthetic event probes.
Event OnCellAttach()
	InvalidatePlayerSample()
EndEvent

Event OnCellDetach()
	InvalidatePlayerSample()
EndEvent

Event OnCellLoad()
	InvalidatePlayerSample()
EndEvent

Event OnLocationChange(Location akOldLoc, Location akNewLoc)
	InvalidatePlayerSample()
EndEvent

Function InvalidatePlayerSample()
	If Who == -1
		TLM:RedHollowWalk controller = Walk()
		If controller
			controller.FairTransitGap()
		EndIf
	EndIf
EndFunction
TLM:RedHollowWalk Function Walk()
	Return GetOwningQuest() as TLM:RedHollowWalk
EndFunction

Event OnActivate(ObjectReference akActionRef)
	If akActionRef == Game.GetPlayer()
		TLM:RedHollowWalk greybox = Walk()
		If greybox
			greybox.Used(Who)
		EndIf
	EndIf
EndEvent

Event OnTriggerEnter(ObjectReference akActionRef)
	If akActionRef == Game.GetPlayer()
		TLM:RedHollowWalk greybox = Walk()
		If greybox
			greybox.Entered(Who)
		EndIf
	EndIf
EndEvent

Event OnDeath(Actor akKiller)
	TLM:RedHollowWalk greybox = Walk()
	If greybox
		int causeCode = 0
		If akKiller == Game.GetPlayer()
			causeCode = 1
		ElseIf akKiller
			causeCode = 2
		EndIf
		greybox.HollowActorDied(Who, causeCode, GetActorReference())
	EndIf
EndEvent

Event OnCombatStateChanged(Actor akTarget, int aeCombatState)
	; aeCombatState: 0 not in combat, 1 in combat, 2 searching.
	If aeCombatState == 1 && akTarget == Game.GetPlayer()
		TLM:RedHollowWalk greybox = Walk()
		If greybox
			greybox.Attacked(Who)
		EndIf
	EndIf
EndEvent

Event OnPlayerLoadGame()
	If Who == -1
		Walk().Loaded()
	EndIf
EndEvent
