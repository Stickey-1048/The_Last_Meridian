Scriptname TLM:MQ01CaravanHandAlias extends ReferenceAlias
{On Alias_CaravanMaster / Alias_CaravanDrover of TLM_MQ01.
UNTESTED SCAFFOLDING. Not compiled.}

Event OnDeath(Actor akKiller)
	; Scripted deaths pass a Cutter (or None) as the killer, so only a real
	; player kill reaches the quest.
	If akKiller == Game.GetPlayer()
		TLM:MQ01Quest q = GetOwningQuest() as TLM:MQ01Quest
		If q
			q.CaravanHandKilledByPlayer(Self)
		EndIf
	EndIf
EndEvent
