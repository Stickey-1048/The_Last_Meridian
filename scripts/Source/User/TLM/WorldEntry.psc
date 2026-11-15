Scriptname TLM:WorldEntry extends Quest
{Explicit exterior development entry. Reuses the existing first-section
controller; never resets or rebinds an already-started preview/main/side quest.}

Quest Property Preview Auto Const Mandatory
Quest Property MainQuest Auto Const Mandatory
Quest Property SideQuest Auto Const Mandatory
Quest Property Section Auto Const Mandatory
Cell Property Clearing Auto Const Mandatory

bool queued = false
bool consumed = false
bool starting = false
bool loadCancelled = false
int attempts = 0
int TIMER_ENTRY = 71 Const
int MAX_ATTEMPTS = 30 Const

bool Function FreshQuestState()
	Return !Preview.IsRunning() && !MainQuest.IsRunning() && !SideQuest.IsRunning() && MainQuest.GetCurrentStageID() == 0 && SideQuest.GetCurrentStageID() == 0 && !Section.IsRunning()
EndFunction

Function QueueFreshEntry()
	{Called only by the fresh-main-menu startup batch. Never an automatic load hook.}
	If queued || consumed || starting || loadCancelled
		Return
	EndIf
	queued = true
	attempts = 0
	If !FreshQuestState()
		CancelFreshEntry()
		Return
	EndIf
	; Start this wrapper so its player alias receives saved-game load events.
	If !IsRunning()
		If !Start()
			CancelFreshEntry()
			Return
		EndIf
	EndIf
	If loadCancelled
		Return
	EndIf
	Debug.Trace("TLM_WORLD_ENTRY: fresh startup queued; readiness deadline 30 timer polls")
	StartTimer(1.0, TIMER_ENTRY)
EndFunction

Function CancelFreshEntry()
	queued = false
	loadCancelled = true
	CancelTimer(TIMER_ENTRY)
	Debug.Trace("TLM_WORLD_ENTRY: pending startup cancelled; no quest reset or rebind")
EndFunction

Event OnTimer(int aiTimerID)
	If aiTimerID != TIMER_ENTRY || !queued || consumed || starting || loadCancelled
		Return
	EndIf
	attempts += 1
	If !FreshQuestState()
		CancelFreshEntry()
		Return
	EndIf
	Actor player = Game.GetPlayer()
	If !player || Utility.IsInMenuMode() || !player.Is3DLoaded() || player.GetParentCell() != Clearing
		If attempts >= MAX_ATTEMPTS
			Debug.Notification("Exterior story setup timed out. Quit without saving and retry the fresh launcher.")
			CancelFreshEntry()
		Else
			StartTimer(1.0, TIMER_ENTRY)
		EndIf
		Return
	EndIf
	queued = false
	Begin()
EndEvent

Function Begin()
	If consumed || starting || loadCancelled
		Return
	EndIf
	starting = true
	If Game.GetPlayer().GetParentCell() != Clearing
		Debug.Notification("Exterior story refused: enter the prototype clearing first.")
		Debug.Trace("TLM_WORLD_ENTRY: refused outside explicit exterior cell")
		starting = false
		Return
	EndIf
	If Preview.IsRunning() || MainQuest.IsRunning() || SideQuest.IsRunning() || MainQuest.GetCurrentStageID() != 0 || SideQuest.GetCurrentStageID() != 0
		Debug.Notification("Exterior story refused: use a fresh development session with no active preview or Meridian quests.")
		Debug.Trace("TLM_WORLD_ENTRY: refused existing quest/preview state; nothing reset or rebound")
		starting = false
		Return
	EndIf
	If Section.IsRunning()
		Debug.Trace("TLM_WORLD_ENTRY: section already running; no rebind")
		starting = false
		Return
	EndIf
	TLM:Act1Walk walk = Section as TLM:Act1Walk
	If !walk
		Debug.Trace("TLM_WORLD_ENTRY: missing first-section controller; stop")
		starting = false
		Return
	EndIf
	If loadCancelled
		starting = false
		Return
	EndIf
	consumed = true
	queued = false
	CancelTimer(TIMER_ENTRY)
	Debug.Trace("TLM_WORLD_ENTRY: explicit fresh exterior first-section setup")
	walk.Begin()
	starting = false
EndFunction
