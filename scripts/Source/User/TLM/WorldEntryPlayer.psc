Scriptname TLM:WorldEntryPlayer extends ReferenceAlias
{Only cancels a pending fresh-start request after loading a saved game.
Never starts/resets a quest, moves the player or changes character stats.}

Event OnPlayerLoadGame()
	TLM:WorldEntry entry = GetOwningQuest() as TLM:WorldEntry
	If entry
		entry.CancelFreshEntry()
	EndIf
EndEvent
