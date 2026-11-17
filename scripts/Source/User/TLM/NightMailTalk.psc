Scriptname TLM:NightMailTalk extends ReferenceAlias
{Development only, on the aliases of TLM_NM (the Night Mail greybox) that
hold a person or a piece a player uses. It tells TLM:NightMailWalk which of
them was used, entered, attacked or killed, by the number below, and decides
nothing itself.

These four events are every hook the Night Mail has into the game. Nothing
of it hears a book being read, or an item being picked up, dropped or moved
between containers: reading is the pages TLM:NightMailWalk shows, and who
holds a thing is counted when it matters.

A CANDIDATE: not compiled, not built against the game's master, not run in
the game.}

int Property Who Auto Const Mandatory
{The piece's number: the same in TLM:NightMailWalk and in tools/PluginBuilder/SpecNightMail.cs.}

TLM:NightMailWalk Function Walk()
	Return GetOwningQuest() as TLM:NightMailWalk
EndFunction

Event OnActivate(ObjectReference akActionRef)
	If akActionRef == Game.GetPlayer()
		TLM:NightMailWalk greybox = Walk()
		If greybox
			greybox.Used(Who)
		EndIf
	EndIf
EndEvent

Event OnTriggerEnter(ObjectReference akActionRef)
	If akActionRef == Game.GetPlayer()
		TLM:NightMailWalk greybox = Walk()
		If greybox
			greybox.Entered(Who)
		EndIf
	EndIf
EndEvent

Event OnDeath(Actor akKiller)
	TLM:NightMailWalk greybox = Walk()
	If greybox
		greybox.Died(Who, akKiller == Game.GetPlayer())
	EndIf
EndEvent

Event OnCombatStateChanged(Actor akTarget, int aeCombatState)
	; aeCombatState: 0 not in combat, 1 in combat, 2 searching.
	If aeCombatState == 1 && akTarget == Game.GetPlayer()
		TLM:NightMailWalk greybox = Walk()
		If greybox
			greybox.Attacked(Who)
		EndIf
	EndIf
EndEvent
