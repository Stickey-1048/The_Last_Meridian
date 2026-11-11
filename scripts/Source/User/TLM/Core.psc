Scriptname TLM:Core extends Quest
{TLM_Core: start-game-enabled utility quest. No story logic.
UNTESTED SCAFFOLDING. Not compiled.}

GlobalVariable Property TLM_G_DataVersion Auto Const Mandatory
Quest Property TLM_MQ01 Auto Const Mandatory

int DATA_VERSION = 1 Const

Event OnQuestInit()
	TLM_G_DataVersion.SetValueInt(DATA_VERSION)
EndEvent

Function DevStart()
	{Development entry point (design decision T1, option a).
	Console: cqf TLM_Core DevStart}
	If !TLM_MQ01.GetStageDone(10)
		TLM_MQ01.SetStage(10)
	EndIf
EndFunction
