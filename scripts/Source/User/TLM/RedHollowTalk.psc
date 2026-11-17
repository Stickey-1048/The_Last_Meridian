Scriptname TLM:RedHollowTalk extends ReferenceAlias
{Alias event forwarding only. Source candidate; no native acceptance.}

int Property Who Auto Const Mandatory
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
		greybox.Died(Who, akKiller == Game.GetPlayer())
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
