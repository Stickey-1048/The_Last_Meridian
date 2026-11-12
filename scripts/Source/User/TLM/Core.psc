Scriptname TLM:Core extends Quest
{TLM_Core: start-game-enabled utility quest. No story logic.
COMPILES. Ran in the game on 2026-11-12: the quest started and OnQuestInit ran
(its line is in the script log). Whether the on-screen line appeared was not
reported (docs/design/VERIFY_LOG.md).}

GlobalVariable Property TLM_G_DataVersion Auto Const Mandatory
Quest Property TLM_MQ01 Auto Const Mandatory

int DATA_VERSION = 1 Const

; Development only: a few seconds after the quest starts, a line appears in the
; top-left corner of the screen. Seeing it means the plugin is loaded and this
; script is running, without opening the console. Remove before any release.
int TIMER_HELLO = 1 Const

Event OnQuestInit()
	TLM_G_DataVersion.SetValueInt(DATA_VERSION)
	; If this line is in the game's script log, the plugin loaded, this script
	; was found and bound, and the quest started.
	Debug.Trace("TLM_Core: started, data version " + DATA_VERSION)
	StartTimer(6.0, TIMER_HELLO)
EndEvent

Event OnTimer(int aiTimerID)
	If aiTimerID == TIMER_HELLO
		Debug.Notification("The Last Meridian test build is loaded.")
	EndIf
EndEvent

Function DevStart()
	{Development entry point (design decision T1, option a).
	Console: cqf TLM_Core DevStart}
	If !TLM_MQ01.GetStageDone(10)
		TLM_MQ01.SetStage(10)
	EndIf
EndFunction
