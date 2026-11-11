Scriptname TLM:MQ01PlayerAlias extends ReferenceAlias
{On Alias_Player of TLM_MQ01 (filled with the player).
COMPILES; NOT YET RUN IN THE GAME (docs/design/VERIFY_LOG.md).

OnPlayerLoadGame is sent only to the player actor; an alias pointing at the
player receives it because aliases receive their reference's events.}

Quest Property SideQuest Auto Const
{Optional. TLM_SQ01.}

Event OnPlayerLoadGame()
	TLM:MQ01Quest q = GetOwningQuest() as TLM:MQ01Quest
	If q
		q.OnGameLoaded()
	EndIf
	TLM:SQ01Quest sq = SideQuest as TLM:SQ01Quest
	If sq
		sq.OnGameLoaded()
	EndIf
EndEvent
