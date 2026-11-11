Scriptname TLM:MQ01CutterAlias extends ReferenceAlias
{On Alias_CutterLead / Alias_CutterA / B / C of TLM_MQ01.
UNTESTED SCAFFOLDING. Not compiled.}

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
