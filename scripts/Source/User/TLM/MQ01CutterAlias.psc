Scriptname TLM:MQ01CutterAlias extends ReferenceAlias
{On Alias_CutterLead / Alias_CutterA / B / C of TLM_MQ01.
COMPILES. RAN IN THE GAME on 2026-11-12 for an actor made at run time and
forced into the lead's alias: its death gave stage 31 (self-test scenarios 2,
5 and 8), and when it started a fight with the player the quest set stage 30
(scenario 5). Not run on the three unnamed Cutters' aliases
(docs/design/VERIFY_LOG.md).}

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
