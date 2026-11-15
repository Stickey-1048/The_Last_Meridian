Scriptname TLM:WorldEntry extends Quest
{Explicit exterior development entry. Reuses the existing first-section
controller; never resets or rebinds an already-started preview/main/side quest.}

Quest Property Preview Auto Const Mandatory
Quest Property MainQuest Auto Const Mandatory
Quest Property SideQuest Auto Const Mandatory
Quest Property Section Auto Const Mandatory
Cell Property Clearing Auto Const Mandatory

Function Begin()
	If Game.GetPlayer().GetParentCell() != Clearing
		Debug.Notification("Exterior story refused: enter the prototype clearing first.")
		Debug.Trace("TLM_WORLD_ENTRY: refused outside explicit exterior cell")
		Return
	EndIf
	If Preview.IsRunning() || MainQuest.IsRunning() || SideQuest.IsRunning() || MainQuest.GetCurrentStageID() != 0 || SideQuest.GetCurrentStageID() != 0
		Debug.Notification("Exterior story refused: use a fresh development session with no active preview or Meridian quests.")
		Debug.Trace("TLM_WORLD_ENTRY: refused existing quest/preview state; nothing reset or rebound")
		Return
	EndIf
	If Section.IsRunning()
		Debug.Trace("TLM_WORLD_ENTRY: section already running; no rebind")
		Return
	EndIf
	TLM:Act1Walk walk = Section as TLM:Act1Walk
	If !walk
		Debug.Trace("TLM_WORLD_ENTRY: missing first-section controller; stop")
		Return
	EndIf
	Debug.Trace("TLM_WORLD_ENTRY: explicit fresh exterior first-section setup")
	walk.Begin()
EndFunction
