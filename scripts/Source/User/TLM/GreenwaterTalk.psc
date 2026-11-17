Scriptname TLM:GreenwaterTalk extends ReferenceAlias
{Development only, on the aliases of TLM_GW (the Greenwater greybox) that
hold a person or a piece a player uses. It tells TLM:GreenwaterWalk which of
them was used, entered, attacked or killed, by the number below, and decides
nothing itself.

NOT COMPILED. NOT RUN IN THE GAME.}

int Property Who Auto Const Mandatory
{The piece's number: the same in TLM:GreenwaterWalk and in tools/PluginBuilder/SpecGreenwater.cs.}

TLM:GreenwaterWalk Function Walk()
	Return GetOwningQuest() as TLM:GreenwaterWalk
EndFunction

Event OnActivate(ObjectReference akActionRef)
	If akActionRef == Game.GetPlayer()
		TLM:GreenwaterWalk greybox = Walk()
		If greybox
			greybox.Used(Who)
		EndIf
	EndIf
EndEvent

Event OnPlayerLoadGame()
	; The master relief quest's player alias alone forwards load invalidation.
	; Ordinary Greenwater aliases own no reserve and cannot reconcile inventory.
	TLM:GreenwaterRelief relief = GetOwningQuest() as TLM:GreenwaterRelief
	If relief
		relief.Loaded()
	EndIf
EndEvent

Event OnTriggerEnter(ObjectReference akActionRef)
	If akActionRef == Game.GetPlayer()
		TLM:GreenwaterWalk greybox = Walk()
		If greybox
			greybox.Entered(Who)
		EndIf
	EndIf
EndEvent

Event OnDeath(Actor akKiller)
	TLM:GreenwaterWalk greybox = Walk()
	If greybox
		greybox.Died(Who, akKiller == Game.GetPlayer())
	EndIf
EndEvent

Event OnCombatStateChanged(Actor akTarget, int aeCombatState)
	; aeCombatState: 0 not in combat, 1 in combat, 2 searching.
	If aeCombatState == 1 && akTarget == Game.GetPlayer()
		TLM:GreenwaterWalk greybox = Walk()
		If greybox
			greybox.Attacked(Who)
		EndIf
	EndIf
EndEvent
