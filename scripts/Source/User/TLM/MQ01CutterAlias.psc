Scriptname TLM:MQ01CutterAlias extends ReferenceAlias
{On Alias_CutterLead / Alias_CutterA / B / C of TLM_MQ01.
COMPILES. OnDeath RAN IN THE GAME on 2026-11-12 for an actor made at run time
and forced into the lead's alias (self-test scenario 2): the quest set stage
31. OnCombatStateChanged has NOT run (docs/design/VERIFY_LOG.md).}

Event OnDeath(Actor akKiller)
	TLM:MQ01Quest q = GetOwningQuest() as TLM:MQ01Quest
	If q
		q.CutterDown(Self)
	EndIf
EndEvent

Event OnCombatStateChanged(Actor akTarget, int aeCombatState)
	; aeCombatState: 0 not in combat, 1 in combat, 2 searching.
	If aeCombatState == 1 && akTarget == Game.GetPlayer()
		TLM:MQ01Quest q = GetOwningQuest() as TLM:MQ01Quest
		If q
			q.PlayerEngaged()
		EndIf
	EndIf
EndEvent
