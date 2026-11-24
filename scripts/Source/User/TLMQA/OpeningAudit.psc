Scriptname TLMQA:OpeningAudit extends Quest
{TEAM ONLY. Explicit opt-in actual-activation/audio diagnostic. No story setters.}

Quest Property Section Auto Const Mandatory
Quest Property MainQuest Auto Const Mandatory
Quest Property Preview Auto Const Mandatory
WorldSpace Property OpeningWorld Auto Const Mandatory
ObjectReference Property Dispatch Auto Const Mandatory
Actor Property Sheriff Auto Const Mandatory
Form Property DispatchItem Auto Const Mandatory
ReferenceAlias Property SectionDispatch Auto Const Mandatory
ReferenceAlias Property SectionSheriff Auto Const Mandatory
ReferenceAlias Property MainDispatch Auto Const Mandatory
ReferenceAlias Property MainSheriff Auto Const Mandatory
float Property DispatchX Auto Const
float Property DispatchY Auto Const
float Property DispatchZ Auto Const
float Property SheriffX Auto Const
float Property SheriffY Auto Const
float Property SheriffZ Auto Const
Sound[] Property Clips Auto Const
float[] Property ClipSeconds Auto Const
string[] Property ClipLabels Auto Const

int mode = 0
int phase = 0
int polls = 0
int clip = 0
int requestEpoch = 0
bool usedConversation = false
bool usedSound = false
Actor capturedPlayer
float nextClip = 0.0
float readySince = -1.0
int TIMER_AUDIT = 81 Const
int MAX_POLLS = 90 Const
bool readOnlySnapshotUsed = false
int TIMER_READONLY_SNAPSHOT = 90 Const
bool remoteBrakeUsed = false
int remoteBrakePhase = 0
int remoteBrakeEpoch = 0
int remoteBrakePolls = 0
int remoteBrakeInventoryCount = 0
int remoteBrakeInventoryValue = 0
Actor remoteBrakePlayer
ObjectReference remoteBrakeClue
Quest remoteBrakeQuest
GlobalVariable remoteBrakeOutcome
GlobalVariable remoteBrakeEvidenceCount
GlobalVariable remoteBrakeEvidenceLevel
int TIMER_REMOTE_BRAKE = 91 Const
bool adaBookUsed = false
int adaBookPhase = 0
int adaBookEpoch = 0
int adaBookPolls = 0
int adaBookInventoryCount = 0
int adaBookInventoryValue = 0
Actor adaBookPlayer
Actor adaBookActor
ObjectReference adaBookLedger
Form adaBookItem
Quest adaBookQuest
GlobalVariable adaBookOutcome
GlobalVariable adaBookScapegoat
int TIMER_ADA_BOOK = 92 Const
bool ganttUsed = false
int ganttPhase = 0
int ganttEpoch = 0
int ganttPolls = 0
int ganttInventoryCount = 0
int ganttInventoryValue = 0
Form ganttStartingPipboy
int ganttStartingPipboyCount = 0
bool ganttInventoryObserving = false
bool ganttAddedRegistered = false
bool ganttRemovedRegistered = false
bool ganttInventoryFilter = false
bool ganttInventoryHold = false
int ganttInventoryEvents = 0
int ganttInventorySettle = 0
Form[] ganttObservedForms
int ganttObservedFormCount = 0
bool ganttMenuRegistered = false
Actor ganttPlayer
Actor ganttActor
Quest ganttQuest
Quest ganttSideQuest
Cell ganttCell
Cell ganttWreckCell
ObjectReference ganttCase
ObjectReference ganttSecured
ObjectReference ganttDeparture
TLM:OpeningPrologue ganttController
int TIMER_GANTT = 93 Const



; Private REMOTE local inquiry only; no production state/property changes.
bool localInquiryUsed = false
int localInquiryPhase = 0
int localInquiryEpoch = 0
int localInquiryPolls = 0
Actor localInquiryPlayer
Actor localInquiryAda
Quest localInquiryJournal
Quest localInquirySide
Cell localInquiryCell
bool localInquiryPhase4EntrySampled = false
bool localInquiryPhase4WaitSampled = false
float localInquiryPhase4SampleAt = -1.0
int TIMER_LOCAL_INQUIRY = 94 Const

; One private remote actor audition per fresh helper session, never walking proof.
bool roadVoiceUsed = false
int roadVoicePhase = 0
int roadVoiceEpoch = 0
int roadVoicePolls = 0
int roadVoiceRole = 0
Actor roadVoicePlayer
Actor roadVoiceActor
Quest roadVoiceSide
Cell roadVoiceCell
int TIMER_ROAD_VOICE = 95 Const

Function Trace(string text)
 Debug.Trace("TLM_QA_OPENING t=" + Utility.GetCurrentRealTime() + " " + text)
EndFunction

bool Function PlayerContext()
 Return capturedPlayer && capturedPlayer == Game.GetPlayer() && !capturedPlayer.IsDead() && !capturedPlayer.IsInCombat() && capturedPlayer.GetWorldSpace() == OpeningWorld && capturedPlayer.Is3DLoaded()
EndFunction

bool Function SameParticipants()
 Return SectionDispatch.GetReference() == Dispatch && MainDispatch.GetReference() == Dispatch && SectionSheriff.GetActorReference() == Sheriff && MainSheriff.GetActorReference() == Sheriff
EndFunction

bool Function SheriffContext()
 Return SameParticipants() && Sheriff && !Sheriff.IsDead() && !Sheriff.IsDisabled() && !Sheriff.IsInCombat() && Sheriff.GetWorldSpace() == OpeningWorld
EndFunction

bool Function SourcePose(ObjectReference target, float x, float y, float z, float zTolerance)
 If !target
  Return false
 EndIf
 ; Each native coordinate getter can yield: these are sequential samples.
 float observedX = target.GetPositionX()
 float observedY = target.GetPositionY()
 float observedZ = target.GetPositionZ()
 float dx = observedX - x
 float dy = observedY - y
 float dz = observedZ - z
 bool okay = dx * dx + dy * dy <= 4.0 && dz >= -zTolerance && dz <= zTolerance
 If !okay
  string label = "other"
  If target == Dispatch
   label = "Dispatch"
  ElseIf target == Sheriff
   label = "Sheriff"
  EndIf
  Trace("SOURCE_POSE_REFUSED " + label + " observedXYZ=(" + observedX + "," + observedY + "," + observedZ + ") reviewedXYZ=(" + x + "," + y + "," + z + ") XYradius=2 Ztolerance=" + zTolerance + "; sequential native samples")
 EndIf
 Return okay
EndFunction

; Only the existing core exterior cell is eligible for this remote pickup diagnostic.
; The QA-only COC marker override supplies arrival; this helper never moves the player.
bool Function CoreCellContext()
 If !PlayerContext() || capturedPlayer.IsDisabled() || !Sheriff || capturedPlayer.GetParentCell() != Sheriff.GetParentCell()
  Return false
 EndIf
 float x = capturedPlayer.GetPositionX()
 float y = capturedPlayer.GetPositionY()
 Return x >= 0.0 && x < 4096.0 && y >= 0.0 && y < 4096.0
EndFunction

Function Abort(string reason)
 requestEpoch += 1
 mode = 0
 Trace("ABORT " + reason + "; no rollback of real pickup/quest effects")
 CancelTimer(TIMER_AUDIT)
 UnregisterForMenuOpenCloseEvent("LoadingMenu")
EndFunction

Function QueueFirstConversation()
 Trace("ENTRY QueueFirstConversation")
 If !EnsureAuditRunning("conversation")
  Return
 EndIf
 If mode != 0 || usedConversation
  Trace("REFUSED repeated/busy conversation queue")
  Return
 EndIf
 usedConversation = true
 requestEpoch += 1
 int generation = requestEpoch
 capturedPlayer = Game.GetPlayer()
 If !capturedPlayer || !Section || !MainQuest || !Preview || !Dispatch || !Sheriff
  Abort("missing exact participants")
  Return
 EndIf
 If Preview.IsRunning() || MainQuest.GetStageDone(20) || (MainQuest.GetCurrentStageID() != 0 && MainQuest.GetCurrentStageID() != 10)
  Abort("not a fresh first-dispatch state")
  Return
 EndIf
 If requestEpoch != generation
  Trace("REFUSED conversation invalidated before queue publication")
  Return
 EndIf
 mode = 1
 phase = 0
 readySince = -1.0
 polls = 0
 Trace("QUEUED real fresh entry wait; no Begin/SetStage/alias/inventory writes")
 StartTimer(1.0, TIMER_AUDIT)
EndFunction

Function QueueSoundCheck()
 Trace("ENTRY QueueSoundCheck")
 If !EnsureAuditRunning("sound")
  Return
 EndIf
 If mode != 0 || usedSound
  Trace("REFUSED repeated/busy sound queue")
  Return
 EndIf
 usedSound = true
 requestEpoch += 1
 int generation = requestEpoch
 capturedPlayer = Game.GetPlayer()
 If !Clips || !ClipSeconds || !ClipLabels || Clips.Length == 0 || Clips.Length > 12 || Clips.Length != ClipSeconds.Length || Clips.Length != ClipLabels.Length
  Abort("no exact declared sound inventory")
  Return
 EndIf
 int i = 0
 While i < Clips.Length
  If !Clips[i] || ClipSeconds[i] <= 0.0 || ClipSeconds[i] > 120.0
   Abort("invalid declared clip/duration")
   Return
  EndIf
  i += 1
 EndWhile
 If requestEpoch != generation
  Trace("REFUSED sound request invalidated before queue publication")
  Return
 EndIf
 mode = 2
 polls = 0
 clip = 0
 nextClip = 0.0
 Trace("QUEUED exact SNDR inventory at player; playback handle is not hearing proof")
 StartTimer(1.0, TIMER_AUDIT)
EndFunction

Function CancelAudit()
 Abort("explicit team cancellation")
EndFunction

Event OnMenuOpenCloseEvent(string asMenuName, bool abOpening)
 If asMenuName == "LoadingMenu" && abOpening && roadVoicePhase != 0
  EndRoadVoice("INCOMPLETE loading; pending UI preserved")
  Return
 EndIf
 If asMenuName == "LoadingMenu" && abOpening && localInquiryPhase != 0
  EndLocalInquiry("INCOMPLETE loading; earned state and pending UI preserved")
  Return
 EndIf
 If asMenuName == "LoadingMenu" && abOpening && ganttPhase != 0
  If ganttPhase == 5
   Trace("GANTT observing authored departure LoadingMenu; no further QA effects")
  Else
   EndGantt("INCOMPLETE unexpected loading before departure; pending UI preserved")
  EndIf
  Return
 EndIf
 If asMenuName == "LoadingMenu" && abOpening && adaBookPhase != 0
  EndAdaBook("INCOMPLETE loading transition; pending UI left untouched")
 EndIf
 If asMenuName == "LoadingMenu" && abOpening && remoteBrakePhase != 0
  EndRemoteBrake("INCOMPLETE loading transition; pending caption left untouched")
 EndIf
 If asMenuName == "LoadingMenu" && abOpening && mode != 0
  Abort("loading transition after readiness")
 EndIf
EndEvent

Event OnTimer(int aiTimerID)
 If aiTimerID == TIMER_ROAD_VOICE
  RoadVoiceTimer()
  Return
 EndIf
 If aiTimerID == TIMER_LOCAL_INQUIRY
  LocalInquiryTimer()
  Return
 EndIf
 If aiTimerID == TIMER_GANTT
  GanttTimer()
  Return
 EndIf
 If aiTimerID == TIMER_ADA_BOOK
  AdaBookTimer()
  Return
 EndIf
 If aiTimerID == TIMER_REMOTE_BRAKE
  RemoteBrakeTimer()
  Return
 EndIf
 If aiTimerID == TIMER_READONLY_SNAPSHOT
  If readOnlySnapshotUsed
   ReadOnlySnapshot()
  EndIf
  Return
 EndIf
 If aiTimerID != TIMER_AUDIT || mode == 0
  Return
 EndIf
 int generation = requestEpoch
 int timerMode = mode
 polls += 1
 If polls > MAX_POLLS || !capturedPlayer || capturedPlayer != Game.GetPlayer()
  Abort("bounded deadline/player changed")
  Return
 EndIf
 If mode == 2
  If !PlayerContext() || Utility.IsInMenuMode()
   If clip > 0
    Abort("sound context changed")
   Else
    StartTimer(1.0, TIMER_AUDIT)
   EndIf
   Return
  EndIf
  If clip >= Clips.Length
   Trace("SOUND END declared inventory; no quest state touched")
   mode = 0
   Return
  EndIf
  If Utility.GetCurrentRealTime() < nextClip
   StartTimer(0.5, TIMER_AUDIT)
   Return
  EndIf
  If requestEpoch != generation || mode != timerMode
   Return
  EndIf
  int handle = Clips[clip].Play(capturedPlayer)
  Trace("SOUND index=" + clip + " label=" + ClipLabels[clip] + " seconds=" + ClipSeconds[clip] + " handle=" + handle)
  If requestEpoch != generation || mode != timerMode
   Return
  EndIf
  If handle < 0
   Abort("native Sound.Play refused")
   Return
  EndIf
  nextClip = Utility.GetCurrentRealTime() + ClipSeconds[clip] + 0.75
  clip += 1
  StartTimer(ClipSeconds[clip - 1] + 0.75, TIMER_AUDIT)
  Return
 EndIf
 If Preview.IsRunning() || MainQuest.GetStageDone(30) || MainQuest.GetStageDone(50)
  Abort("preview/later story state")
  Return
 EndIf
 If phase == 0
  If MainQuest.GetCurrentStageID() != 0 && MainQuest.GetCurrentStageID() != 10
   Abort("fresh-entry stage changed")
   Return
  EndIf
  If !PlayerContext() || Utility.IsInMenuMode() || !Section.IsRunning() || !MainQuest.IsRunning() || !MainQuest.GetStageDone(10) || !SheriffContext() || Dispatch.IsDisabled() || !Dispatch.Is3DLoaded()
   readySince = -1.0
   StartTimer(1.0, TIMER_AUDIT)
   Return
  EndIf
  If capturedPlayer.GetItemCount(DispatchItem) != 0
   Abort("dispatch already held before activation")
   Return
  EndIf
  If !SourcePose(Dispatch,DispatchX,DispatchY,DispatchZ,16.0) || !SourcePose(Sheriff,SheriffX,SheriffY,SheriffZ,8.0)
   Abort("source pose drift exceeds reviewed relocation footprint")
   Return
  EndIf
  If readySince < 0.0
   RegisterForMenuOpenCloseEvent("LoadingMenu")
   If requestEpoch != generation || mode != timerMode
    Return
   EndIf
   readySince = Utility.GetCurrentRealTime()
   Trace("READY dwell begins; continuously rechecking normal entry for four seconds")
  EndIf
  If Utility.GetCurrentRealTime() - readySince < 4.0
   StartTimer(1.0, TIMER_AUDIT)
   Return
  EndIf
  phase = 1
  Trace("REMOTE DISPATCH diagnostic from original COC sheriff pad; no player relocation")
  If !CoreCellContext()
   Abort("remote dispatch activation requires the current core cell")
   Return
  EndIf
  If requestEpoch != generation || mode != timerMode || phase != 1
   Return
  EndIf
  If requestEpoch != generation || mode != timerMode
   Return
  EndIf
  StartTimer(1.0, TIMER_AUDIT)
  Return
 EndIf
 If !PlayerContext() || !SheriffContext()
  Abort("participants/player changed after readiness")
  Return
 EndIf
 If phase == 1
  If Utility.IsInMenuMode() || Dispatch.IsDisabled() || !Dispatch.Is3DLoaded() || MainQuest.GetStageDone(20) || !SourcePose(Dispatch,DispatchX,DispatchY,DispatchZ,16.0)
   Abort("dispatch activation context lost")
   Return
  EndIf
  phase = 2
  Trace("DISPATCH Activate actual original reference")
  If requestEpoch != generation || mode != timerMode || phase != 2
   Return
  EndIf
  bool accepted = Dispatch.Activate(capturedPlayer)
  If requestEpoch != generation || mode != timerMode
   Return
  EndIf
  Trace("DISPATCH Activate returned=" + accepted + "; awaiting actual stage20 receipt")
  If !accepted
   Abort("native dispatch activation refused")
   Return
  EndIf
  StartTimer(1.0, TIMER_AUDIT)
  Return
 EndIf
 If phase == 2
  If !MainQuest.GetStageDone(20) || capturedPlayer.GetItemCount(DispatchItem) <= 0 || Dispatch.GetContainer() != capturedPlayer || Utility.IsInMenuMode()
   StartTimer(1.0, TIMER_AUDIT)
   Return
  EndIf
  If !SourcePose(Sheriff,SheriffX,SheriffY,SheriffZ,8.0)
   Abort("sheriff wandered outside reviewed relocation footprint")
   Return
  EndIf
  phase = 3
  Trace("RECEIPT actual stage20+dispatch container; player remains at sheriff COC pad")
  If !CoreCellContext()
   Abort("sheriff activation requires the current core cell")
   Return
  EndIf
  If requestEpoch != generation || mode != timerMode || phase != 3
   Return
  EndIf
  If requestEpoch != generation || mode != timerMode
   Return
  EndIf
  StartTimer(1.0, TIMER_AUDIT)
  Return
 EndIf
 If phase == 3 || phase == 4
  If Utility.IsInMenuMode() || !Sheriff.Is3DLoaded() || Sheriff.IsTalking() || capturedPlayer.GetDistance(Sheriff) > 192.0 || !MainQuest.GetStageDone(20) || MainQuest.GetStageDone(30) || !SourcePose(Sheriff,SheriffX,SheriffY,SheriffZ,8.0)
   Abort("first sheriff activation context lost")
   Return
  EndIf
  If phase == 3
   phase = 4
   Debug.Trace("TLM_OPENQA: CAPTURE_READY t=" + Utility.GetCurrentRealTime())
   If requestEpoch != generation || mode != timerMode
    Return
   EndIf
   StartTimer(10.0, TIMER_AUDIT)
   Return
  EndIf
  Trace("SHERIFF Activate actual exterior Pritchard; ordinary dialogue/buttons belong to native story")
  Debug.Trace("TLM_OPENQA: ACTIVATING_SHERIFF t=" + Utility.GetCurrentRealTime())
  If requestEpoch != generation || mode != timerMode || phase != 4
   Return
  EndIf
  bool sheriffAccepted = Sheriff.Activate(capturedPlayer)
  If requestEpoch != generation || mode != timerMode
   Return
  EndIf
  mode = 0
  UnregisterForMenuOpenCloseEvent("LoadingMenu")
  Trace("SHERIFF Activate returned=" + sheriffAccepted + "; no dialogue choice/hearing/outcome asserted")
 EndIf
EndEvent

; Initialize the QA-only quest BEFORE any once-only/token/player request fields.
; This is robust even if native Start initializes script member defaults.
bool Function EnsureAuditRunning(string caller)
 If !IsRunning()
  Trace("BEFORE_START " + caller)
  bool started = Start()
  bool running = IsRunning()
  Trace("AFTER_START " + caller + " result=" + started + " running=" + running)
  If !started || !running
   Trace("REFUSED " + caller + ": QA-only quest did not start")
   Return false
  EndIf
 EndIf
 Return true
EndFunction

; Explicit diagnostic only. Starts this private quest, never a story quest.
; Claim the once-only flag AFTER Start initializes member defaults.
Function QueueReadOnlySnapshot()
 Trace("ENTRY QueueReadOnlySnapshot")
 If !EnsureAuditRunning("readonly snapshot")
  Return
 EndIf
 If readOnlySnapshotUsed
  Trace("REFUSED repeated readonly snapshot queue")
  Return
 EndIf
 readOnlySnapshotUsed = true
 Trace("QUEUED readonly snapshot after25s; no activation/input/control/story effects")
 StartTimer(25.0, TIMER_READONLY_SNAPSHOT)
EndFunction

Function ReadOnlySnapshot()
 Debug.Trace("TLM_CONTROL_SNAPSHOT ENTRY t=" + Utility.GetCurrentRealTime())
 Actor player = Game.GetPlayer()
 ObjectReference clue = Game.GetFormFromFile(0x00000903, "TLMWorldSlice.esp") as ObjectReference
 Debug.Trace("TLM_CONTROL_SNAPSHOT movement=" + Game.IsMovementControlsEnabled() + " look=" + Game.IsLookingControlsEnabled() + " activate=" + Game.IsActivateControlsEnabled() + " menus=" + Game.IsMenuControlsEnabled() + " menuMode=" + Utility.IsInMenuMode())
 Debug.Trace("TLM_CONTROL_SNAPSHOT player=" + player)
 If player
  Debug.Trace("TLM_CONTROL_SNAPSHOT player world=" + player.GetWorldSpace() + " cell=" + player.GetParentCell() + " loaded=" + player.Is3DLoaded())
  Debug.Trace("TLM_CONTROL_SNAPSHOT player xyz=" + player.GetPositionX() + "," + player.GetPositionY() + "," + player.GetPositionZ() + " angles=" + player.GetAngleX() + "," + player.GetAngleY() + "," + player.GetAngleZ())
 EndIf
 Debug.Trace("TLM_CONTROL_SNAPSHOT clue903=" + clue)
 If clue
  Debug.Trace("TLM_CONTROL_SNAPSHOT clue903 world=" + clue.GetWorldSpace() + " cell=" + clue.GetParentCell() + " loaded=" + clue.Is3DLoaded() + " disabled=" + clue.IsDisabled() + " height=" + clue.GetHeight())
  Debug.Trace("TLM_CONTROL_SNAPSHOT clue903 xyz=" + clue.GetPositionX() + "," + clue.GetPositionY() + "," + clue.GetPositionZ() + " angles=" + clue.GetAngleX() + "," + clue.GetAngleY() + "," + clue.GetAngleZ())
 EndIf
 Debug.Trace("TLM_CONTROL_SNAPSHOT END samePlayer=" + (player == Game.GetPlayer()) + "; sequential native samples; reference Z is not mesh contact")
EndFunction

; Explicit REMOTE real-reference handler test; never physical targeting proof.
Function QueueRemoteBrakeInspection()
 Trace("ENTRY QueueRemoteBrakeInspection REMOTE")
 If !EnsureAuditRunning("remote brake inspection")
  Return
 EndIf
 If remoteBrakeUsed || mode != 0
  Trace("REFUSED repeated/busy remote brake queue")
  Return
 EndIf
 remoteBrakeUsed = true
 remoteBrakeEpoch += 1
 int generation = remoteBrakeEpoch
 remoteBrakePhase = 1
 remoteBrakePolls = 0
 remoteBrakePlayer = Game.GetPlayer()
 remoteBrakeClue = Game.GetFormFromFile(0x00000903, "TLMWorldSlice.esp") as ObjectReference
 remoteBrakeQuest = Game.GetFormFromFile(0x0000081B, "TheLastMeridian.esp") as Quest
 remoteBrakeOutcome = Game.GetFormFromFile(0x0000080E, "TheLastMeridian.esp") as GlobalVariable
 remoteBrakeEvidenceCount = Game.GetFormFromFile(0x0000080C, "TheLastMeridian.esp") as GlobalVariable
 remoteBrakeEvidenceLevel = Game.GetFormFromFile(0x0000080D, "TheLastMeridian.esp") as GlobalVariable
 If !remoteBrakePlayer || !remoteBrakeClue || !remoteBrakeQuest || !remoteBrakeOutcome || !remoteBrakeEvidenceCount || !remoteBrakeEvidenceLevel
  EndRemoteBrake("INCOMPLETE missing exact original forms")
  Return
 EndIf
 RegisterForMenuOpenCloseEvent("LoadingMenu")
 bool registeredLoad = RegisterForRemoteEvent(remoteBrakePlayer, "OnPlayerLoadGame")
 If !registeredLoad
  EndRemoteBrake("INCOMPLETE player-load registration refused; no remote activation scheduled")
  Return
 EndIf
 If !RemoteBrakePending(generation,1)
  Return
 EndIf
 Trace("QUEUED REMOTE original903.Activate test after25s; no forced answers/items/stages/positions")
 If RemoteBrakePending(generation,1)
  StartTimer(25.0, TIMER_REMOTE_BRAKE)
 EndIf
EndFunction

bool Function RemoteBrakePending(int generation, int expectedPhase)
 Return remoteBrakeEpoch == generation && remoteBrakePhase == expectedPhase && mode == 0
EndFunction

bool Function RemoteBrakeContext()
 If !remoteBrakePlayer || !remoteBrakeClue || !remoteBrakeQuest || !OpeningWorld
  Return false
 EndIf
 ReferenceAlias actualAlias = remoteBrakeQuest.GetAlias(4) as ReferenceAlias
 If !actualAlias || remoteBrakePlayer.GetWorldSpace() != OpeningWorld || remoteBrakeClue.GetWorldSpace() != OpeningWorld || remoteBrakePlayer.GetParentCell() != remoteBrakeClue.GetParentCell() || remoteBrakePlayer.IsInCombat() || remoteBrakeClue.IsActivationBlocked()
  Return false
 EndIf
 Actor currentPlayer = Game.GetPlayer()
 If actualAlias.GetReference() != remoteBrakeClue || remoteBrakeClue.IsDisabled() || !remoteBrakeClue.Is3DLoaded() || !remoteBrakePlayer.Is3DLoaded() || remoteBrakePlayer.IsDisabled() || remoteBrakePlayer.IsDead()
  Return false
 EndIf
 Return currentPlayer == remoteBrakePlayer
EndFunction

bool Function RemoteBrakeFresh()
 Return remoteBrakeOutcome.GetValueInt() == 0 && !remoteBrakeQuest.GetStageDone(10) && !remoteBrakeQuest.GetStageDone(11) && !remoteBrakeQuest.GetStageDone(12) && !remoteBrakeQuest.GetStageDone(13) && !remoteBrakeQuest.GetStageDone(14) && !remoteBrakeQuest.GetStageDone(20) && !remoteBrakeQuest.GetStageDone(25) && !remoteBrakeQuest.GetStageDone(50)
EndFunction

Function RemoteBrakeTimer()
 If remoteBrakePhase == 0
  Return
 EndIf
 int generation = remoteBrakeEpoch
 int currentPhase = remoteBrakePhase
 remoteBrakePolls += 1
 If remoteBrakePolls > 90
  EndRemoteBrake("INCOMPLETE bounded timeout; any pending caption left untouched")
  Return
 EndIf
 If currentPhase == 1
  If !Section.IsRunning() || !MainQuest.GetStageDone(10) || !remoteBrakeQuest.IsRunning() || !remoteBrakeQuest.GetStageDone(5) || Utility.IsInMenuMode()
   If RemoteBrakePending(generation,1)
    StartTimer(1.0,TIMER_REMOTE_BRAKE)
   EndIf
   Return
  EndIf
  If !RemoteBrakeFresh()
   EndRemoteBrake("INCOMPLETE not a fresh physical-first/no-outcome state")
   Return
  EndIf
  remoteBrakeInventoryCount = remoteBrakePlayer.GetItemCount(None)
  remoteBrakeInventoryValue = remoteBrakePlayer.GetInventoryValue()
  Trace("REMOTE invoking original903 only; capture actual brake caption/Step back; Activate return alone is not inspection proof")
  If !RemoteBrakeFresh() || !RemoteBrakeContext()
   EndRemoteBrake("INCOMPLETE context/fresh state lost before activation")
   Return
  EndIf
  If !RemoteBrakePending(generation,1)
   Return
  EndIf
  remoteBrakePhase = 2
  bool accepted = remoteBrakeClue.Activate(remoteBrakePlayer,false)
  If !RemoteBrakePending(generation,2)
   Return
  EndIf
  Trace("REMOTE Activate returned=" + accepted + "; waiting for genuine post-dismissal stage11; no forced answer")
  If RemoteBrakePending(generation,2)
   StartTimer(1.0,TIMER_REMOTE_BRAKE)
  EndIf
  Return
 EndIf
 If !RemoteBrakeContext()
  EndRemoteBrake("INCOMPLETE current player/original alias/clue context lost")
  Return
 EndIf
 If remoteBrakeOutcome.GetValueInt() != 0 || remoteBrakeQuest.GetStageDone(10) || remoteBrakeQuest.GetStageDone(12) || remoteBrakeQuest.GetStageDone(13) || remoteBrakeQuest.GetStageDone(14) || remoteBrakeQuest.GetStageDone(20) || remoteBrakeQuest.GetStageDone(25) || remoteBrakeQuest.GetStageDone(50) || remoteBrakePlayer.GetItemCount(None) != remoteBrakeInventoryCount || remoteBrakePlayer.GetInventoryValue() != remoteBrakeInventoryValue
  EndRemoteBrake("INCOMPLETE other clue/outcome or aggregate inventory changed; no rollback")
  Return
 EndIf
 If remoteBrakeQuest.GetStageDone(11) && remoteBrakeEvidenceCount.GetValueInt() == 1 && remoteBrakeEvidenceLevel.GetValueInt() == 1 && !Utility.IsInMenuMode()
  If !RemoteBrakePending(generation,2)
   Return
  EndIf
  EndRemoteBrake("RECEIPT genuine stage11/count1/level1/no20/outcome0 and aggregate inventory unchanged; actual caption/normal dismissal needs native visual evidence; REMOTE not crosshair/walking proof")
  Return
 EndIf
 If RemoteBrakePending(generation,2)
  StartTimer(1.0,TIMER_REMOTE_BRAKE)
 EndIf
EndFunction

Function EndRemoteBrake(string reason)
 remoteBrakeEpoch += 1
 remoteBrakePhase = 0
 CancelTimer(TIMER_REMOTE_BRAKE)
 If remoteBrakePlayer
  UnregisterForRemoteEvent(remoteBrakePlayer,"OnPlayerLoadGame")
 EndIf
 If mode == 0
  UnregisterForMenuOpenCloseEvent("LoadingMenu")
 EndIf
 Trace("REMOTE_BRAKE " + reason)
EndFunction

Function CancelRemoteBrakeInspection()
 EndRemoteBrake("INCOMPLETE explicit private cancellation; pending caption left untouched")
EndFunction

Event Actor.OnPlayerLoadGame(Actor akSender)
 If roadVoicePhase != 0 && akSender == roadVoicePlayer
  EndRoadVoice("INCOMPLETE actual player load; no future activation")
 EndIf
 If localInquiryPhase != 0 && akSender == localInquiryPlayer
  EndLocalInquiry("INCOMPLETE actual player load; no future remote activations")
 EndIf
 If ganttPhase != 0 && akSender == ganttPlayer
  EndGantt("INCOMPLETE actual saved-player load; future QA effects cancelled")
 EndIf
 If adaBookPhase != 0 && akSender == adaBookPlayer
  EndAdaBook("INCOMPLETE actual player load; no stale activation or forced answer")
 EndIf
 If remoteBrakePhase != 0 && akSender == remoteBrakePlayer
  EndRemoteBrake("INCOMPLETE actual player load; no stale activation/forced answer")
 EndIf
EndEvent

; Explicit REMOTE ledger-handler then near-original-Ada interaction diagnostic.
Function QueueAdaBookInspection()
 Trace("ENTRY QueueAdaBookInspection REMOTE ledger/near-Ada; no scripted pickup or answers")
 If !EnsureAuditRunning("Ada book inspection")
  Return
 EndIf
 If adaBookUsed || mode != 0 || remoteBrakePhase != 0
  Trace("REFUSED repeated/busy Ada book queue")
  Return
 EndIf
 adaBookUsed = true
 adaBookEpoch += 1
 int generation = adaBookEpoch
 adaBookPhase = 1
 adaBookPolls = 0
 adaBookPlayer = Game.GetPlayer()
 adaBookLedger = Game.GetFormFromFile(0x00000902,"TLMWorldSlice.esp") as ObjectReference
 adaBookActor = Game.GetFormFromFile(0x00000911,"TLMWorldSlice.esp") as Actor
 adaBookItem = Game.GetFormFromFile(0x00000817,"TheLastMeridian.esp")
 adaBookQuest = Game.GetFormFromFile(0x0000081B,"TheLastMeridian.esp") as Quest
 adaBookOutcome = Game.GetFormFromFile(0x0000080E,"TheLastMeridian.esp") as GlobalVariable
 adaBookScapegoat = Game.GetFormFromFile(0x00000811,"TheLastMeridian.esp") as GlobalVariable
 If !adaBookPlayer || !adaBookLedger || !adaBookActor || !adaBookItem || !adaBookQuest || !adaBookOutcome || !adaBookScapegoat
  EndAdaBook("INCOMPLETE missing exact original forms")
  Return
 EndIf
 RegisterForMenuOpenCloseEvent("LoadingMenu")
 bool registered = RegisterForRemoteEvent(adaBookPlayer,"OnPlayerLoadGame")
 If !registered
  EndAdaBook("INCOMPLETE player-load registration refused; no timer or activation")
  Return
 EndIf
 If !AdaBookPending(generation,1)
  Return
 EndIf
 Trace("QUEUED Ada book after25s normal setup; normal native ledger Take required")
 If AdaBookPending(generation,1)
  StartTimer(25.0,TIMER_ADA_BOOK)
 EndIf
EndFunction

; Explicit REMOTE actual case/Gantt/departure handlers. Never walking or forced dialogue proof.
Function QueueGanttOpeningInspection()
 Trace("ENTRY QueueGanttOpeningInspection REMOTE actual handlers; ordinary choices remain player-owned")
 If !EnsureAuditRunning("Gantt opening inspection")
  Return
 EndIf
 If ganttUsed || mode != 0 || adaBookPhase != 0 || remoteBrakePhase != 0
  Trace("REFUSED repeated/busy Gantt queue")
  Return
 EndIf
 ganttUsed = true
 ganttEpoch += 1
 int generation = ganttEpoch
 ganttPhase = 1
 mode = 6
 ganttPolls = 0
 ganttPlayer = Game.GetPlayer()
 ganttActor = Game.GetFormFromFile(0x8FE,"TLMWorldSlice.esp") as Actor
 ganttQuest = Game.GetFormFromFile(0xB58,"TLMWorldSlice.esp") as Quest
 ganttController = ganttQuest as TLM:OpeningPrologue
 ganttSideQuest = Game.GetFormFromFile(0x81B,"TheLastMeridian.esp") as Quest
 ganttCell = Game.GetFormFromFile(0xB46,"TLMWorldSlice.esp") as Cell
 ganttWreckCell = Game.GetFormFromFile(0x802,"TLMWorldSlice.esp") as Cell
 ganttCase = Game.GetFormFromFile(0xB52,"TLMWorldSlice.esp") as ObjectReference
 ganttSecured = Game.GetFormFromFile(0xB56,"TLMWorldSlice.esp") as ObjectReference
 ganttDeparture = Game.GetFormFromFile(0xB53,"TLMWorldSlice.esp") as ObjectReference
 ganttStartingPipboy = Game.GetFormFromFile(0x21B3B,"Fallout4.esm")
 If !ganttPlayer || !ganttActor || !ganttController || !ganttSideQuest || !ganttCell || !ganttWreckCell || !ganttCase || !ganttSecured || !ganttDeparture || !MainQuest || !Section || !Preview || !Dispatch || !DispatchItem || !ganttStartingPipboy
  EndGantt("INCOMPLETE exact current prologue bindings missing")
  Return
 EndIf
 bool registered = RegisterForRemoteEvent(ganttPlayer,"OnPlayerLoadGame")
 If !registered
  EndGantt("INCOMPLETE player-load registration refused; no timer/activation")
  Return
 EndIf
 If GanttPending(generation,1)
  StartTimer(2.0,TIMER_GANTT)
 EndIf
EndFunction

bool Function GanttPending(int generation, int expectedPhase)
 Return ganttEpoch == generation && ganttPhase == expectedPhase && mode == 6
EndFunction

bool Function GanttFresh()
 Return !Preview.IsRunning() && !MainQuest.IsRunning() && !ganttSideQuest.IsRunning() && !Section.IsRunning() && MainQuest.GetCurrentStageID() == 0 && ganttSideQuest.GetCurrentStageID() == 0
EndFunction

bool Function GanttIdentity()
 ReferenceAlias caseAlias = ganttQuest.GetAlias(0) as ReferenceAlias
 ReferenceAlias actorAlias = ganttQuest.GetAlias(1) as ReferenceAlias
 ReferenceAlias departureAlias = ganttQuest.GetAlias(2) as ReferenceAlias
 Return caseAlias && actorAlias && departureAlias && caseAlias.GetReference() == ganttCase && actorAlias.GetActorReference() == ganttActor && departureAlias.GetReference() == ganttDeparture
EndFunction

bool Function GanttLocal()
 Actor current = Game.GetPlayer()
 If !ganttPlayer || current != ganttPlayer || !ganttActor || ganttPlayer.GetParentCell() != ganttCell || ganttActor.GetParentCell() != ganttCell || ganttPlayer.GetDistance(ganttActor) > 320.0
  Return false
 EndIf
 If !ganttPlayer.Is3DLoaded() || !ganttActor.Is3DLoaded() || ganttPlayer.IsDisabled() || ganttActor.IsDisabled() || ganttPlayer.IsInCombat() || ganttActor.IsInCombat() || ganttPlayer.IsInScene() || ganttActor.IsInScene() || ganttPlayer.IsDead() || ganttActor.IsDead()
  Return false
 EndIf
 Return current == ganttPlayer
EndFunction

bool Function GanttNoDispatch()
 Return !MainQuest.GetStageDone(20) && ganttPlayer.GetItemCount(DispatchItem) == 0 && Dispatch.GetContainer() != ganttPlayer
EndFunction

bool Function GanttInventorySame()
 Return GanttNoDispatch() && ganttPlayer.GetItemCount(None) == ganttInventoryCount && ganttPlayer.GetInventoryValue() == ganttInventoryValue
EndFunction

bool Function GanttCaseSecured()
 Return ganttCase.GetParentCell() == ganttCell && ganttCase.GetDistance(ganttSecured) <= 8.0 && ganttQuest.IsObjectiveCompleted(10) && ganttQuest.IsObjectiveDisplayed(20)
EndFunction

Function GanttTimer()
 If ganttPhase == 0
  Return
 EndIf
 int generation = ganttEpoch
 int phaseNow = ganttPhase
 ganttPolls += 1
 If ganttPolls > 180 || mode != 6
  EndGantt("INCOMPLETE bounded deadline/cancellation; pending caption and earned state preserved")
  Return
 EndIf
 If phaseNow == 1
  If !ganttQuest.IsRunning() || !ganttQuest.IsObjectiveDisplayed(10) || Utility.IsInMenuMode()
   If GanttPending(generation,1)
    StartTimer(1.0,TIMER_GANTT)
   EndIf
   Return
  EndIf
  If !GanttFresh() || !GanttNoDispatch() || ganttQuest.IsObjectiveCompleted(10) || !GanttIdentity() || ganttCase.GetParentCell() != ganttCell || ganttCase.IsDisabled() || !ganttCase.Is3DLoaded() || !GanttLocal()
   EndGantt("INCOMPLETE fresh original carriage/case context refused")
   Return
  EndIf
  If !StartGanttInventoryObservation(generation)
   Return
  EndIf
  ganttInventoryCount = ganttPlayer.GetItemCount(None)
  ganttInventoryValue = ganttPlayer.GetInventoryValue()
  ganttStartingPipboyCount = ganttPlayer.GetItemCount(ganttStartingPipboy)
  int baselineDispatch = ganttPlayer.GetItemCount(DispatchItem)
  If baselineDispatch != 0 || !GanttNoDispatch() || !GanttPending(generation,1)
   If GanttPending(generation,1)
    EndGantt("INCOMPLETE dispatch/state changed during observer registration; no activation")
   EndIf
   Return
  EndIf
  Trace("GANTT inventory baseline total=" + ganttInventoryCount + " value=" + ganttInventoryValue + " Pipboy=" + ganttStartingPipboyCount + " dispatch=" + baselineDispatch + "; sequential samples after observer registration")
  RegisterForMenuOpenCloseEvent("LoadingMenu")
  ganttMenuRegistered = true
  If !GanttIdentity() || !GanttLocal() || !GanttPending(generation,1)
   If GanttPending(generation,1)
    EndGantt("INCOMPLETE case context lost before activation")
   EndIf
   Return
  EndIf
  ganttPhase = 2
  bool caseAccepted = ganttCase.Activate(ganttPlayer,false)
  Trace("GANTT REMOTE tool-case Activate returned=" + caseAccepted + "; wait real physical/objective receipt")
 ElseIf phaseNow == 2
  If !GanttFresh() || !GanttInventorySame() || !GanttIdentity() || !GanttLocal()
   EndGantt("INCOMPLETE case receipt participant/state loss")
   Return
  EndIf
  If GanttCaseSecured() && !Utility.IsInMenuMode() && GanttPending(generation,2)
   ganttPhase = 3
   Debug.Trace("TLM_GANTT_QA017 CAPTURE_READY; genuine secured-case/objective receipt; original Gantt activation after3s; ordinary choices only")
   If GanttPending(generation,3)
    StartTimer(3.0,TIMER_GANTT)
   EndIf
   Return
  EndIf
 ElseIf phaseNow == 3
  If !GanttFresh() || !GanttInventorySame() || !GanttCaseSecured() || Utility.IsInMenuMode() || !GanttIdentity() || ganttActor.IsTalking() || ganttActor.IsInDialogueWithPlayer() || !GanttLocal()
   EndGantt("INCOMPLETE original Gantt context lost after capture delay")
   Return
  EndIf
  If !GanttPending(generation,3)
   Return
  EndIf
  ganttPhase = 4
  bool actorAccepted = ganttActor.Activate(ganttPlayer,false)
  Trace("GANTT REMOTE original8FE Activate returned=" + actorAccepted + "; blocked-default False can still run actual caption; no forced answer")
 ElseIf phaseNow == 4
  If !GanttFresh() || !GanttInventorySame() || !GanttIdentity() || !GanttLocal()
   EndGantt("INCOMPLETE ordinary Gantt conversation context lost")
   Return
  EndIf
  If !ganttQuest.IsObjectiveDisplayed(30) || !ganttQuest.IsObjectiveCompleted(20) || !ganttController.HeardRequest() || (!ganttController.AcceptedRequest() && !ganttController.DeclinedRequest()) || Utility.IsInMenuMode()
   If GanttPending(generation,4)
    StartTimer(1.0,TIMER_GANTT)
   EndIf
   Return
  EndIf
  If !GanttIdentity() || ganttDeparture.GetParentCell() != ganttCell || ganttDeparture.IsDisabled() || !ganttDeparture.Is3DLoaded() || !GanttLocal() || !GanttPending(generation,4)
   If GanttPending(generation,4)
    EndGantt("INCOMPLETE departure context lost before activation")
   EndIf
   Return
  EndIf
  ganttPhase = 5
  bool departureAccepted = ganttDeparture.Activate(ganttPlayer,false)
  Trace("GANTT REMOTE departure Activate returned=" + departureAccepted + "; root owns normal confirmation; observe authored travel only")
 ElseIf phaseNow == 5
  ; No further activation or eligibility demanding a living Gantt during the authored wreck.
  If ganttPlayer != Game.GetPlayer() || ganttPlayer.IsDead()
   EndGantt("INCOMPLETE observation player lost; no rollback")
   Return
  EndIf
  bool inventorySame = GanttWreckInventorySame()
  If !GanttPending(generation,5)
   Return
  EndIf
  If !inventorySame
   If !ganttInventoryHold
    ganttInventoryHold = true
    Trace("GANTT HOLD inventory predicate refused; no further activations; bounded read-only settling")
   EndIf
  EndIf
  If ganttInventoryHold
   ganttInventorySettle += 1
   If ganttInventorySettle > 10
    EndGantt("HOLD inventory mismatch retained; read-only settling deadline; no PASS")
    Return
   EndIf
  EndIf
  If ganttController.HandoffCompleted() && MainQuest.GetStageDone(10) && ganttSideQuest.GetStageDone(5) && Section.IsRunning() && ganttActor.IsDead() && ganttActor.GetWorldSpace() == OpeningWorld && ganttPlayer.GetParentCell() == ganttWreckCell && ganttPlayer.GetWorldSpace() == OpeningWorld && ganttPlayer.Is3DLoaded() && !Utility.IsInMenuMode()
   If GanttPending(generation,5)
    If ganttInventoryHold
     EndGantt("HOLD inventory mismatch retained; actual setup complete; observation only, no PASS")
    Else
     EndGantt("RECEIPT authored wreck arrival/original Gantt dead/Main10/SQ5/Section/prologue complete; no dispatch acquisition; only documented starting Pipboy addition permitted; physical walk/hearing require separate evidence")
    EndIf
   EndIf
   Return
  EndIf
 EndIf
 If GanttPending(generation,ganttPhase)
  StartTimer(1.0,TIMER_GANTT)
 EndIf
EndFunction

; Only after authored handoff: old Act1Walk.WearPipBoy supplies native zero-value Pipboy if absent.
bool Function GanttWreckInventorySame()
 int dispatchCount = ganttPlayer.GetItemCount(DispatchItem)
 ObjectReference dispatchContainer = Dispatch.GetContainer()
 bool pickup20 = MainQuest.GetStageDone(20)
 int countNow = ganttPlayer.GetItemCount(None)
 int valueNow = ganttPlayer.GetInventoryValue()
 int pipboyNow = ganttPlayer.GetItemCount(ganttStartingPipboy)
 bool main10 = MainQuest.GetStageDone(10)
 bool sectionRunning = Section.IsRunning()
 bool noDispatch = dispatchCount == 0 && !dispatchContainer && !pickup20
 bool unchanged = countNow == ganttInventoryCount && valueNow == ganttInventoryValue && pipboyNow == ganttStartingPipboyCount
 bool allowedPipboy = main10 && sectionRunning && ganttStartingPipboyCount == 0 && pipboyNow == 1 && countNow == ganttInventoryCount + 1 && valueNow == ganttInventoryValue && ganttStartingPipboy.GetGoldValue() == 0
 Trace("GANTT post-handoff samples dispatchCount=" + dispatchCount + " container=" + dispatchContainer + " pickup20=" + pickup20 + " inventoryCount=" + countNow + " baselineCount=" + ganttInventoryCount + " inventoryValue=" + valueNow + " baselineValue=" + ganttInventoryValue + " pipboyCount=" + pipboyNow + " baselinePipboy=" + ganttStartingPipboyCount + " Main10=" + main10 + " SectionRunning=" + sectionRunning + " noDispatch=" + noDispatch + " unchanged=" + unchanged + " allowedStartingPipboy=" + allowedPipboy + "; sequential non-atomic samples")
 Return noDispatch && (unchanged || allowedPipboy)
EndFunction

Function EndGantt(string reason)
 ganttEpoch += 1
 ganttPhase = 0
 If mode == 6
  mode = 0
 EndIf
 CancelTimer(TIMER_GANTT)
 FinishGanttInventoryObservation()
 If ganttPlayer
  UnregisterForRemoteEvent(ganttPlayer,"OnPlayerLoadGame")
 EndIf
 If ganttMenuRegistered
  ganttMenuRegistered = false
  UnregisterForMenuOpenCloseEvent("LoadingMenu")
 EndIf
 Trace("GANTT " + reason)
EndFunction

; Bounded SDK item-event observation only; no inventory writes or inferred unknown pre-counts.
bool Function GanttObservationCurrent(int generation)
 Return ganttInventoryObserving && ganttEpoch == generation && ganttPhase > 0 && mode == 6
EndFunction

bool Function StartGanttInventoryObservation(int generation)
 If ganttInventoryObserving
  Return GanttObservationCurrent(generation)
 EndIf
 ganttInventoryObserving = true
 ganttInventoryHold = false
 ganttInventoryEvents = 0
 ganttInventorySettle = 0
 ganttObservedForms = new Form[16]
 ganttObservedFormCount = 0
 ganttInventoryFilter = true
 AddInventoryEventFilter(None)
 If !GanttObservationCurrent(generation)
  ; Add can finish after cancellation removed its earlier filter. Never touch a newer owner.
  If !ganttInventoryObserving && !ganttInventoryFilter
   RemoveInventoryEventFilter(None)
  EndIf
  Return false
 EndIf
 ganttAddedRegistered = true
 bool added = RegisterForRemoteEvent(ganttPlayer,"OnItemAdded")
 If !GanttObservationCurrent(generation)
  ; Registration may finish after a yielding load/cancel cleanup.
  If added
   UnregisterForRemoteEvent(ganttPlayer,"OnItemAdded")
  EndIf
  ganttAddedRegistered = false
  Return false
 EndIf
 If !added
  EndGantt("INCOMPLETE item-added registration refused; no activation")
  Return false
 EndIf
 ganttRemovedRegistered = true
 bool removed = RegisterForRemoteEvent(ganttPlayer,"OnItemRemoved")
 If !GanttObservationCurrent(generation)
  If removed
   UnregisterForRemoteEvent(ganttPlayer,"OnItemRemoved")
  EndIf
  ganttRemovedRegistered = false
  Return false
 EndIf
 If !removed
  EndGantt("INCOMPLETE item-removed registration refused; no activation")
  Return false
 EndIf
 Trace("GANTT inventory observer armed before baseline; exact known Pipboy/dispatch counts follow; unknown types have no invented baseline")
 Return GanttObservationCurrent(generation)
EndFunction

Event ObjectReference.OnItemAdded(ObjectReference akSender, Form akBaseItem, int aiItemCount, ObjectReference akItemReference, ObjectReference akSourceContainer)
 ObserveGanttInventory(akSender,akBaseItem,aiItemCount,akItemReference,akSourceContainer,true)
EndEvent

Event ObjectReference.OnItemRemoved(ObjectReference akSender, Form akBaseItem, int aiItemCount, ObjectReference akItemReference, ObjectReference akDestContainer)
 ObserveGanttInventory(akSender,akBaseItem,aiItemCount,akItemReference,akDestContainer,false)
EndEvent

Function ObserveGanttInventory(ObjectReference sender, Form item, int count, ObjectReference itemReference, ObjectReference otherContainer, bool added)
 int generation = ganttEpoch
 If !GanttObservationCurrent(generation) || sender != ganttPlayer
  Return
 EndIf
 If !item || count <= 0 || ganttInventoryEvents >= 32
  EndGantt("INCOMPLETE inventory event invalid/cap32; no PASS")
  Return
 EndIf
 ganttInventoryEvents += 1
 If ganttObservedForms.Find(item) < 0
  If ganttObservedFormCount >= 16
   EndGantt("INCOMPLETE distinct inventory form cap16; no PASS")
   Return
  EndIf
  ganttObservedForms[ganttObservedFormCount] = item
  ganttObservedFormCount += 1
 EndIf
 int itemID = item.GetFormID()
 int countNow = ganttPlayer.GetItemCount(item)
 int gold = item.GetGoldValue()
 bool main10 = MainQuest.GetStageDone(10)
 bool sectionRunning = Section.IsRunning()
 If !GanttObservationCurrent(generation) || sender != ganttPlayer
  Return
 EndIf
 Trace("GANTT inventory event added=" + added + " base=" + item + " formID=" + itemID + " deltaCount=" + count + " persistentRef=" + itemReference + " sourceOrDestination=" + otherContainer + " countNow=" + countNow + " goldValue=" + gold + " Main10=" + main10 + " SectionRunning=" + sectionRunning + "; sequential event samples; unknown pre-count not inferred")
EndFunction

Function FinishGanttInventoryObservation()
 bool wasObserving = ganttInventoryObserving
 ganttInventoryObserving = false
 If ganttAddedRegistered
  ganttAddedRegistered = false
  UnregisterForRemoteEvent(ganttPlayer,"OnItemAdded")
 EndIf
 If ganttRemovedRegistered
  ganttRemovedRegistered = false
  UnregisterForRemoteEvent(ganttPlayer,"OnItemRemoved")
 EndIf
 If ganttInventoryFilter
  ganttInventoryFilter = false
  RemoveInventoryEventFilter(None)
 EndIf
 If !wasObserving || !ganttPlayer
  Return
 EndIf
 int pipboyNow = ganttPlayer.GetItemCount(ganttStartingPipboy)
 int dispatchNow = ganttPlayer.GetItemCount(DispatchItem)
 Trace("GANTT inventory final known Pipboy=" + pipboyNow + " baselinePipboy=" + ganttStartingPipboyCount + " dispatch=" + dispatchNow + " baselineDispatch=0; events=" + ganttInventoryEvents + " held=" + ganttInventoryHold)
 int i = 0
 While i < ganttObservedFormCount && i < 16
  Form item = ganttObservedForms[i]
  int itemID = item.GetFormID()
  int countNow = ganttPlayer.GetItemCount(item)
  Trace("GANTT inventory final encountered base=" + item + " formID=" + itemID + " countNow=" + countNow + "; no unknown initial-count claim")
  i += 1
 EndWhile
EndFunction

Function CancelGanttOpeningInspection()
 EndGantt("INCOMPLETE explicit cancellation; actual UI and production state preserved")
EndFunction

bool Function AdaBookPending(int generation, int expectedPhase)
 Return adaBookEpoch == generation && adaBookPhase == expectedPhase && mode == 0 && remoteBrakePhase == 0
EndFunction

bool Function AdaBookIdentity()
 If !adaBookPlayer || !adaBookLedger || !adaBookActor || !adaBookQuest || !Section || !OpeningWorld
  Return false
 EndIf
 ReferenceAlias ledgerAlias = adaBookQuest.GetAlias(1) as ReferenceAlias
 ReferenceAlias actorAlias = Section.GetAlias(19) as ReferenceAlias
 If !ledgerAlias || !actorAlias || ledgerAlias.GetReference() != adaBookLedger || actorAlias.GetActorReference() != adaBookActor || adaBookLedger.GetBaseObject() != adaBookItem
  Return false
 EndIf
 Actor current = Game.GetPlayer()
 If adaBookPlayer.GetWorldSpace() != OpeningWorld || adaBookActor.GetWorldSpace() != OpeningWorld || adaBookPlayer.GetParentCell() != adaBookActor.GetParentCell() || adaBookPlayer.GetDistance(adaBookActor) > 320.0 || adaBookPlayer.IsInScene() || adaBookActor.IsInScene() || adaBookActor.IsInCombat() || adaBookPlayer.IsInCombat() || adaBookActor.IsTalking() || adaBookActor.IsInDialogueWithPlayer()
  Return false
 EndIf
 If !adaBookPlayer.Is3DLoaded() || !adaBookActor.Is3DLoaded() || adaBookActor.IsDisabled() || adaBookActor.IsDead() || adaBookPlayer.IsDisabled() || adaBookPlayer.IsDead()
  Return false
 EndIf
 float finalDistance = adaBookPlayer.GetDistance(adaBookActor)
 Return current == adaBookPlayer && finalDistance <= 320.0
EndFunction

bool Function AdaBookBranchFresh()
 Return adaBookOutcome.GetValueInt() == 0 && adaBookScapegoat.GetValueInt() == 0 && !adaBookQuest.GetStageDone(11) && !adaBookQuest.GetStageDone(12) && !adaBookQuest.GetStageDone(13) && !adaBookQuest.GetStageDone(14) && !adaBookQuest.GetStageDone(20) && !adaBookQuest.GetStageDone(25) && !adaBookQuest.GetStageDone(50)
EndFunction

bool Function AdaBookLedgerHeld()
 Return adaBookQuest.GetStageDone(10) && adaBookPlayer.GetItemCount(adaBookItem) > 0 && adaBookLedger.GetContainer() == adaBookPlayer
EndFunction

Function AdaBookTimer()
 If adaBookPhase == 0
  Return
 EndIf
 int generation = adaBookEpoch
 int phaseNow = adaBookPhase
 adaBookPolls += 1
 If adaBookPolls > 90
  EndAdaBook("INCOMPLETE bounded deadline; pending ledger/book caption left untouched; no forced Take/answer")
  Return
 EndIf
 If phaseNow == 1
  If !Section.IsRunning() || !MainQuest.GetStageDone(10) || !adaBookQuest.IsRunning() || !adaBookQuest.GetStageDone(5) || Utility.IsInMenuMode()
   If AdaBookPending(generation,1)
    StartTimer(1.0,TIMER_ADA_BOOK)
   EndIf
   Return
  EndIf
  If !AdaBookBranchFresh() || adaBookQuest.GetStageDone(10) || adaBookPlayer.GetItemCount(adaBookItem) != 0 || adaBookLedger.GetContainer() || adaBookLedger.IsDisabled() || !adaBookLedger.Is3DLoaded() || adaBookLedger.GetWorldSpace() != OpeningWorld
   EndAdaBook("INCOMPLETE not fresh original ledger acquisition context")
   Return
  EndIf
  Trace("REMOTE original902 BOOK activation only; root must use normal native Take; reading/Activate bool is not acquisition")
  If !AdaBookBranchFresh() || !AdaBookIdentity() || adaBookLedger.IsDisabled() || !adaBookLedger.Is3DLoaded()
   EndAdaBook("INCOMPLETE original ledger/player/Ada context lost before activation")
   Return
  EndIf
  If !AdaBookPending(generation,1)
   Return
  EndIf
  adaBookPhase = 2
  bool ledgerAccepted = adaBookLedger.Activate(adaBookPlayer,false)
  If !AdaBookPending(generation,2)
   Return
  EndIf
  Trace("REMOTE ledger Activate returned=" + ledgerAccepted + "; wait genuine SQ10+817 count+original container, no AddItem fallback")
  If AdaBookPending(generation,2)
   StartTimer(1.0,TIMER_ADA_BOOK)
  EndIf
  Return
 EndIf
 If phaseNow == 2
  If !AdaBookBranchFresh() || !AdaBookIdentity()
   EndAdaBook("INCOMPLETE changed original participant or fresh Book branch")
   Return
  EndIf
  If !AdaBookLedgerHeld() || Utility.IsInMenuMode()
   If AdaBookPending(generation,2)
    StartTimer(1.0,TIMER_ADA_BOOK)
   EndIf
   Return
  EndIf
  adaBookInventoryCount = adaBookPlayer.GetItemCount(None)
  adaBookInventoryValue = adaBookPlayer.GetInventoryValue()
  If !AdaBookPending(generation,2)
   Return
  EndIf
  adaBookPhase = 3
  Debug.Trace("TLM_ADA_BOOK_QA013 CAPTURE_READY; genuine ledger pickup receipt; arm original8.16s render capture before3s delayed Ada activation")
  If AdaBookPending(generation,3)
   StartTimer(3.0,TIMER_ADA_BOOK)
  EndIf
  Return
 EndIf
 If phaseNow == 3
  If !AdaBookBranchFresh() || !AdaBookLedgerHeld() || Utility.IsInMenuMode() || !adaBookActor.IsActivationBlocked() || !AdaBookIdentity()
   EndAdaBook("INCOMPLETE original near-Ada/ledger/audio context lost after capture delay")
   Return
  EndIf
  If !AdaBookPending(generation,3)
   Return
  EndIf
  adaBookPhase = 4
  bool actorAccepted = adaBookActor.Activate(adaBookPlayer,false)
  If !AdaBookPending(generation,4)
   Return
  EndIf
  Trace("ADA Activate returned=" + actorAccepted + "; False may be expected with blocked default; capture actual BOOK caption/render; no forced choice")
  If AdaBookPending(generation,4)
   StartTimer(1.0,TIMER_ADA_BOOK)
  EndIf
  Return
 EndIf
 ; Observe only while actual production caption owns the answer and sound.
 If !AdaBookLedgerHeld() || adaBookOutcome.GetValueInt() != 0 || adaBookScapegoat.GetValueInt() != 0 || adaBookQuest.GetStageDone(20) || adaBookQuest.GetStageDone(25) || adaBookPlayer.GetItemCount(None) != adaBookInventoryCount || adaBookPlayer.GetInventoryValue() != adaBookInventoryValue
  EndAdaBook("INCOMPLETE ledger/outcome/aggregate inventory changed; no rollback")
  Return
 EndIf
 If adaBookQuest.GetStageDone(14) && !Utility.IsInMenuMode()
  If !AdaBookPending(generation,4)
   Return
  EndIf
  EndAdaBook("RECEIPT genuine Ada14 after ordinary choice; ledger still held/outcome0/no20; actual caption/8.16s rendered voice requires native evidence")
  Return
 EndIf
 If AdaBookPending(generation,4)
  StartTimer(1.0,TIMER_ADA_BOOK)
 EndIf
EndFunction

Function EndAdaBook(string reason)
 adaBookEpoch += 1
 adaBookPhase = 0
 CancelTimer(TIMER_ADA_BOOK)
 If adaBookPlayer
  UnregisterForRemoteEvent(adaBookPlayer,"OnPlayerLoadGame")
 EndIf
 If mode == 0 && remoteBrakePhase == 0
  UnregisterForMenuOpenCloseEvent("LoadingMenu")
 EndIf
 Trace("ADA_BOOK " + reason)
EndFunction

Function CancelAdaBookInspection()
 EndAdaBook("INCOMPLETE explicit private cancellation; UI and earned production effects left untouched")
EndFunction

; Opt-in REMOTE actual dispatch / sheriff / Ada / sheriff handlers, never walking proof.
Function QueueLocalBrakeInquiry()
 Trace("ENTRY QueueLocalBrakeInquiry REMOTE handlers; ordinary answers remain player-owned")
 If !EnsureAuditRunning("local brake inquiry")
  Return
 EndIf
 If localInquiryUsed || mode != 0 || remoteBrakePhase != 0 || adaBookPhase != 0 || ganttPhase != 0
  Trace("LOCAL_INQUIRY REFUSED repeated or busy")
  Return
 EndIf
 localInquiryUsed = true
 localInquiryEpoch += 1
 int generation = localInquiryEpoch
 localInquiryPhase = 1
 mode = 7
 localInquiryPolls = 0
 localInquiryPlayer = Game.GetPlayer()
 Actor listener = localInquiryPlayer
 localInquiryAda = Game.GetFormFromFile(0x911,"TLMWorldSlice.esp") as Actor
 localInquiryJournal = Game.GetFormFromFile(0xB6B,"TLMWorldSlice.esp") as Quest
 localInquirySide = Game.GetFormFromFile(0x81B,"TheLastMeridian.esp") as Quest
 localInquiryCell = Game.GetFormFromFile(0x802,"TLMWorldSlice.esp") as Cell
 If !LocalInquiryPending(generation,1)
  Return
 EndIf
 If !listener || !localInquiryAda || !localInquiryJournal || !localInquirySide || !localInquiryCell || !Section || !MainQuest || !Dispatch || !DispatchItem || !Sheriff || !OpeningWorld
  EndLocalInquiry("INCOMPLETE missing actual bindings")
  Return
 EndIf
 If MainQuest.GetStageDone(20) || MainQuest.GetStageDone(50) || localInquiryJournal.IsRunning() || localInquiryJournal.IsCompleted()
  EndLocalInquiry("INCOMPLETE not fresh pickup/inquiry")
  Return
 EndIf
 ; Claim own mode before yielding registration. Actual load invalidates this phase even without a handle.
 If !LocalInquiryPending(generation,1)
  Return
 EndIf
 bool registered = RegisterForRemoteEvent(listener,"OnPlayerLoadGame")
 If !LocalInquiryPending(generation,1)
  If registered
   UnregisterForRemoteEvent(listener,"OnPlayerLoadGame")
  EndIf
  Return
 EndIf
 If !registered
  EndLocalInquiry("INCOMPLETE player-load registration refused")
  Return
 EndIf
 RegisterForMenuOpenCloseEvent("LoadingMenu")
 If LocalInquiryPending(generation,1)
  Trace("LOCAL_INQUIRY queued25s; no prologue, answers, movement or stage setters")
  If LocalInquiryPending(generation,1)
   StartTimer(25.0,TIMER_LOCAL_INQUIRY)
  EndIf
 Else
  UnregisterForMenuOpenCloseEvent("LoadingMenu")
 EndIf
EndFunction

bool Function LocalInquiryPending(int generation, int expectedPhase)
 Return localInquiryEpoch == generation && localInquiryPhase == expectedPhase
EndFunction

bool Function LocalInquiryContext(int generation, int expectedPhase)
 Actor listener = localInquiryPlayer
 Actor ada = localInquiryAda
 If !listener || !ada || !Sheriff || !localInquiryCell || !OpeningWorld || !Section || !MainQuest || !localInquirySide || !localInquiryJournal
  Return false
 EndIf
 If listener.IsDead() || listener.IsDisabled() || !listener.Is3DLoaded() || listener.IsInCombat() || listener.IsInScene() || listener.GetWorldSpace() != OpeningWorld || listener.GetParentCell() != localInquiryCell
  Return false
 EndIf
 If ada.IsDead() || ada.IsDisabled() || !ada.Is3DLoaded() || ada.IsInCombat() || ada.IsInScene() || Sheriff.IsDead() || Sheriff.IsDisabled() || !Sheriff.Is3DLoaded() || Sheriff.IsInCombat() || Sheriff.IsInScene()
  Return false
 EndIf
 If ada.GetParentCell() != localInquiryCell || Sheriff.GetParentCell() != localInquiryCell || listener.GetDistance(ada) > 320.0 || listener.GetDistance(Sheriff) > 320.0
  Return false
 EndIf
 ; Eligibility first, current original aliases/identities next, then pure owned phase/epoch tail.
 Actor originalAda = Game.GetFormFromFile(0x911,"TLMWorldSlice.esp") as Actor
 Actor originalSheriff = Game.GetFormFromFile(0x910,"TLMWorldSlice.esp") as Actor
 ; The consumable dispatch is authoritative through the pre-sheriff effect only.
 ; Phase3 means sheriff Activate was issued once after real20/container/count1.
 bool dispatchIdentity = false
 If expectedPhase <= 2
  ObjectReference originalDispatch = Game.GetFormFromFile(0x8FF,"TLMWorldSlice.esp") as ObjectReference
  ReferenceAlias dispatchAlias = Section.GetAlias(1) as ReferenceAlias
  If Dispatch && originalDispatch && dispatchAlias
   dispatchIdentity = dispatchAlias.GetReference() == Dispatch && Dispatch == originalDispatch
  EndIf
 Else
  dispatchIdentity = MainQuest.GetStageDone(20)
 EndIf
 ReferenceAlias adaAlias = Section.GetAlias(19) as ReferenceAlias
 ReferenceAlias sheriffAlias = Section.GetAlias(18) as ReferenceAlias
 Actor currentAda = None
 Actor currentSheriff = None
 If adaAlias && sheriffAlias
  currentAda = adaAlias.GetActorReference()
  currentSheriff = sheriffAlias.GetActorReference()
 EndIf
 Actor currentPlayer = Game.GetPlayer()
 Return currentAda == ada && ada == originalAda && currentSheriff == Sheriff && Sheriff == originalSheriff && dispatchIdentity && currentPlayer == listener && LocalInquiryPending(generation,expectedPhase) && mode == 7
EndFunction

bool Function LocalInquiryMarkers()
 ReferenceAlias journalAda = localInquiryJournal.GetAlias(0) as ReferenceAlias
 ReferenceAlias journalSheriff = localInquiryJournal.GetAlias(1) as ReferenceAlias
 Return journalAda && journalSheriff && journalAda.GetActorReference() == localInquiryAda && journalSheriff.GetActorReference() == Sheriff
EndFunction

Function LocalInquiryTimer()
 int generation = localInquiryEpoch
 int observedPhase = localInquiryPhase
 If observedPhase == 0 || mode != 7
  Return
 EndIf
 localInquiryPolls += 1
 If localInquiryPolls > 180
  EndLocalInquiry("INCOMPLETE bounded timeout; pending UI preserved, no retries")
  Return
 EndIf
 If !LocalInquiryContext(generation,observedPhase)
  LocalInquiryDiagnostic(generation,observedPhase)
  If LocalInquiryPending(generation,observedPhase)
   EndLocalInquiry("INCOMPLETE current player/original actors/cell/range/aliases lost")
  EndIf
  Return
 EndIf
 If localInquirySide.GetStageDone(10) || localInquirySide.GetStageDone(14)
  EndLocalInquiry("INCOMPLETE unexpected ledger/BOOK progress; no local-task bypass")
  Return
 EndIf
 ; Observation only, before any later phase4 final effect guard.
 If observedPhase == 4 && localInquiryPhase4EntrySampled && !localInquiryPhase4WaitSampled
  float sampledNow = Utility.GetCurrentRealTime()
  If sampledNow - localInquiryPhase4SampleAt >= 5.0 && LocalInquiryPending(generation,4)
   localInquiryPhase4WaitSampled = true
   LocalInquiryPhase4Sample("DELAYED_WAIT",generation)
  EndIf
  If !LocalInquiryPending(generation,4)
   Return
  EndIf
 EndIf
 If Utility.IsInMenuMode()
  If LocalInquiryPending(generation,observedPhase)
   StartTimer(1.0,TIMER_LOCAL_INQUIRY)
  EndIf
  Return
 EndIf
 If observedPhase == 1
  If !MainQuest.GetStageDone(10) || !localInquirySide.GetStageDone(5) || !Section.IsRunning()
   If LocalInquiryPending(generation,1)
    StartTimer(1.0,TIMER_LOCAL_INQUIRY)
   EndIf
   Return
  EndIf
  If MainQuest.GetStageDone(20) || Dispatch.GetContainer() || localInquiryPlayer.GetItemCount(DispatchItem) != 0 || !MainDispatch || MainDispatch.GetReference() != Dispatch
   EndLocalInquiry("INCOMPLETE pickup is not fresh/original")
   Return
  EndIf
  Trace("LOCAL_INQUIRY REMOTE actual dispatch Activate ONCE; return is not pickup proof")
  If !LocalInquiryContext(generation,1)
   LocalInquiryDiagnostic(generation,1)
   If LocalInquiryPending(generation,1)
    EndLocalInquiry("INCOMPLETE final pickup context lost; owned request closed")
   EndIf
   Return
  EndIf
  localInquiryPhase = 2
  If !LocalInquiryPending(generation,2)
   Return
  EndIf
  Dispatch.Activate(localInquiryPlayer,false)
 ElseIf observedPhase == 2
  If !MainQuest.GetStageDone(20) || Dispatch.GetContainer() != localInquiryPlayer || localInquiryPlayer.GetItemCount(DispatchItem) != 1
   If LocalInquiryPending(generation,2)
    StartTimer(1.0,TIMER_LOCAL_INQUIRY)
   EndIf
   Return
  EndIf
  Trace("LOCAL_INQUIRY receipt real20/container/count1; original sheriff Activate ONCE for ordinary delivery/debrief/offer")
  If Sheriff.IsTalking() || Sheriff.IsInDialogueWithPlayer() || !LocalInquiryContext(generation,2)
   If LocalInquiryPending(generation,2)
    StartTimer(1.0,TIMER_LOCAL_INQUIRY)
   EndIf
   Return
  EndIf
  localInquiryPhase = 3
  If LocalInquiryPending(generation,3)
   Sheriff.Activate(localInquiryPlayer,false)
  EndIf
 ElseIf observedPhase == 3
  If !MainQuest.GetStageDone(50) || MainQuest.IsObjectiveDisplayed(20) || !localInquiryJournal.IsRunning() || !localInquiryJournal.IsObjectiveDisplayed(10) || localInquiryJournal.IsObjectiveCompleted(10) || localInquiryJournal.IsObjectiveDisplayed(20) || !LocalInquiryMarkers()
   If LocalInquiryPending(generation,3)
    StartTimer(1.0,TIMER_LOCAL_INQUIRY)
   EndIf
   Return
  EndIf
  Trace("LOCAL_INQUIRY receipt journal10/MQ20hidden; original Ada Activate ONCE; ordinary question/history only")
  If localInquiryAda.IsTalking() || localInquiryAda.IsInDialogueWithPlayer() || !LocalInquiryContext(generation,3)
   If LocalInquiryPending(generation,3)
    StartTimer(1.0,TIMER_LOCAL_INQUIRY)
   EndIf
   Return
  EndIf
  localInquiryPhase = 4
  If LocalInquiryPending(generation,4)
   localInquiryAda.Activate(localInquiryPlayer,false)
   ; Safe placement: native effect already returned; never sample between eligibility and Activate.
   If LocalInquiryPending(generation,4) && !localInquiryPhase4EntrySampled
    localInquiryPhase4EntrySampled = true
    localInquiryPhase4SampleAt = Utility.GetCurrentRealTime()
    LocalInquiryPhase4Sample("ENTRY_ADA_ACTIVATE_RETURNED",generation)
   EndIf
  EndIf
 ElseIf observedPhase == 4
  If !localInquiryJournal.IsObjectiveCompleted(10) || !localInquiryJournal.IsObjectiveDisplayed(20) || localInquiryJournal.IsCompleted() || !LocalInquiryMarkers()
   If LocalInquiryPending(generation,4)
    StartTimer(1.0,TIMER_LOCAL_INQUIRY)
   EndIf
   Return
  EndIf
  Trace("LOCAL_INQUIRY receipt attributed account/objective20; original sheriff Activate ONCE for normal report")
  If Sheriff.IsTalking() || Sheriff.IsInDialogueWithPlayer() || !LocalInquiryContext(generation,4)
   If LocalInquiryPending(generation,4)
    StartTimer(1.0,TIMER_LOCAL_INQUIRY)
   EndIf
   Return
  EndIf
  localInquiryPhase = 5
  If LocalInquiryPending(generation,5)
   Sheriff.Activate(localInquiryPlayer,false)
  EndIf
 ElseIf observedPhase == 5
  If localInquiryJournal.IsCompleted() && localInquiryJournal.IsObjectiveCompleted(20) && !localInquiryJournal.IsObjectiveDisplayed(20) && LocalInquiryMarkers() && LocalInquiryContext(generation,5)
   Trace("LOCAL_INQUIRY RECEIPT completed actual local report; no walking/BOOK/audio/outcome assertion")
   If LocalInquiryPending(generation,5)
    EndLocalInquiry("COMPLETE actual handlers and ordinary answers observed")
   EndIf
   Return
  EndIf
 EndIf
 If LocalInquiryPending(generation,localInquiryPhase) && mode == 7 && localInquiryPhase != 0
  StartTimer(1.0,TIMER_LOCAL_INQUIRY)
 EndIf
EndFunction

Function EndLocalInquiry(string reason)
 Actor listener = localInquiryPlayer
 localInquiryEpoch += 1
 localInquiryPhase = 0
 If mode == 7
  mode = 0
 EndIf
 CancelTimer(TIMER_LOCAL_INQUIRY)
 If listener
  UnregisterForRemoteEvent(listener,"OnPlayerLoadGame")
 EndIf
 UnregisterForMenuOpenCloseEvent("LoadingMenu")
 Trace("LOCAL_INQUIRY " + reason + "; no rollback or pending UI dismissal")
EndFunction

Function CancelLocalBrakeInquiry()
 EndLocalInquiry("INCOMPLETE explicit cancellation")
EndFunction

; Refusal-only read-only samples. Sequential native observations are not an atomic cause proof.
Function LocalInquiryDiagnostic(int generation, int expectedPhase)
 Trace("LOCAL_INQUIRY SAMPLE sequential/not-atomic phase=" + expectedPhase + " epoch=" + generation + " currentEpoch=" + localInquiryEpoch + "; no activation after this refusal sample")
 Actor sampledPlayer = Game.GetPlayer()
 If localInquiryPlayer
  Trace("LOCAL_INQUIRY SAMPLE PLAYER identity=" + (sampledPlayer == localInquiryPlayer) + " dead=" + localInquiryPlayer.IsDead() + " disabled=" + localInquiryPlayer.IsDisabled() + " loaded=" + localInquiryPlayer.Is3DLoaded() + " combat=" + localInquiryPlayer.IsInCombat() + " scene=" + localInquiryPlayer.IsInScene())
  Trace("LOCAL_INQUIRY SAMPLE SPACE playerWorld=" + localInquiryPlayer.GetWorldSpace() + " playerCell=" + localInquiryPlayer.GetParentCell() + " expectedWorld=" + OpeningWorld + " expectedCell=" + localInquiryCell + " XYZ=" + localInquiryPlayer.GetPositionX() + "," + localInquiryPlayer.GetPositionY() + "," + localInquiryPlayer.GetPositionZ())
 EndIf
 If Sheriff && localInquiryAda && localInquiryPlayer
  Trace("LOCAL_INQUIRY SAMPLE SHERIFF actor=" + Sheriff + " dead=" + Sheriff.IsDead() + " disabled=" + Sheriff.IsDisabled() + " loaded=" + Sheriff.Is3DLoaded() + " combat=" + Sheriff.IsInCombat() + " scene=" + Sheriff.IsInScene() + " cell=" + Sheriff.GetParentCell() + " range=" + localInquiryPlayer.GetDistance(Sheriff))
  Trace("LOCAL_INQUIRY SAMPLE ADA actor=" + localInquiryAda + " dead=" + localInquiryAda.IsDead() + " disabled=" + localInquiryAda.IsDisabled() + " loaded=" + localInquiryAda.Is3DLoaded() + " combat=" + localInquiryAda.IsInCombat() + " scene=" + localInquiryAda.IsInScene() + " cell=" + localInquiryAda.GetParentCell() + " range=" + localInquiryPlayer.GetDistance(localInquiryAda))
 EndIf
 If Section
  ReferenceAlias sampledAda = Section.GetAlias(19) as ReferenceAlias
  ReferenceAlias sampledSheriff = Section.GetAlias(18) as ReferenceAlias
  ReferenceAlias sampledDispatch = Section.GetAlias(1) as ReferenceAlias
  If sampledAda && sampledSheriff && sampledDispatch
   Trace("LOCAL_INQUIRY SAMPLE ALIASES ada=" + sampledAda.GetReference() + " sheriff=" + sampledSheriff.GetReference() + " dispatch=" + sampledDispatch.GetReference())
  EndIf
 EndIf
 ObjectReference sampledOriginalDispatch = Game.GetFormFromFile(0x8FF,"TLMWorldSlice.esp") as ObjectReference
 Trace("LOCAL_INQUIRY SAMPLE DISPATCH bound=" + Dispatch + " currentLookup=" + sampledOriginalDispatch + "; identity required only before sheriff effect")
 If Dispatch
  Trace("LOCAL_INQUIRY SAMPLE DISPATCH_CONTAINER bound=" + Dispatch.GetContainer())
 EndIf
 If localInquiryPlayer && DispatchItem
  Trace("LOCAL_INQUIRY SAMPLE DISPATCH_COUNT count=" + localInquiryPlayer.GetItemCount(DispatchItem))
 EndIf
 If MainQuest && localInquirySide && localInquiryJournal
  Trace("LOCAL_INQUIRY SAMPLE QUEST main20=" + MainQuest.GetStageDone(20) + " main50=" + MainQuest.GetStageDone(50) + " main60=" + MainQuest.GetStageDone(60) + " main100=" + MainQuest.GetStageDone(100) + " MQ20shown=" + MainQuest.IsObjectiveDisplayed(20) + " SQ10=" + localInquirySide.GetStageDone(10) + " SQ14=" + localInquirySide.GetStageDone(14))
  Trace("LOCAL_INQUIRY SAMPLE JOURNAL running=" + localInquiryJournal.IsRunning() + " complete=" + localInquiryJournal.IsCompleted() + " obj10shown=" + localInquiryJournal.IsObjectiveDisplayed(10) + " obj10done=" + localInquiryJournal.IsObjectiveCompleted(10) + " obj20shown=" + localInquiryJournal.IsObjectiveDisplayed(20) + " obj20done=" + localInquiryJournal.IsObjectiveCompleted(20))
 EndIf
EndFunction

; At most entry + one delayed phase4 sample. Read-only sequential observations, not atomic proof.
Function LocalInquiryPhase4Sample(string label, int generation)
 bool menu = Utility.IsInMenuMode()
 Trace("LOCAL_INQUIRY PHASE4_SAMPLE " + label + " sequential/not-atomic phase=" + localInquiryPhase + " polls=" + localInquiryPolls + " capturedEpoch=" + generation + " epoch=" + localInquiryEpoch + " mode=" + mode + " menu=" + menu)
 If localInquiryJournal
  Trace("LOCAL_INQUIRY PHASE4_JOURNAL running=" + localInquiryJournal.IsRunning() + " completed=" + localInquiryJournal.IsCompleted() + " obj10shown=" + localInquiryJournal.IsObjectiveDisplayed(10) + " obj10done=" + localInquiryJournal.IsObjectiveCompleted(10) + " obj20shown=" + localInquiryJournal.IsObjectiveDisplayed(20) + " obj20done=" + localInquiryJournal.IsObjectiveCompleted(20))
  ReferenceAlias markerAda = localInquiryJournal.GetAlias(0) as ReferenceAlias
  ReferenceAlias markerSheriff = localInquiryJournal.GetAlias(1) as ReferenceAlias
  Actor targetAda = None
  Actor targetSheriff = None
  If markerAda
   targetAda = markerAda.GetActorReference()
  EndIf
  If markerSheriff
   targetSheriff = markerSheriff.GetActorReference()
  EndIf
  Trace("LOCAL_INQUIRY PHASE4_MARKERS ada=" + targetAda + " sheriff=" + targetSheriff + " expectedAda=" + localInquiryAda + " expectedSheriff=" + Sheriff)
 EndIf
 If Sheriff && localInquiryPlayer
  Trace("LOCAL_INQUIRY PHASE4_SHERIFF actor=" + Sheriff + " dead=" + Sheriff.IsDead() + " disabled=" + Sheriff.IsDisabled() + " loaded=" + Sheriff.Is3DLoaded() + " talking=" + Sheriff.IsTalking() + " dialogue=" + Sheriff.IsInDialogueWithPlayer() + " cell=" + Sheriff.GetParentCell() + " playerCell=" + localInquiryPlayer.GetParentCell() + " range=" + localInquiryPlayer.GetDistance(Sheriff))
 EndIf
 If Section
  ReferenceAlias originalAlias = Section.GetAlias(18) as ReferenceAlias
  Actor currentSheriff = None
  If originalAlias
   currentSheriff = originalAlias.GetActorReference()
  EndIf
  Trace("LOCAL_INQUIRY PHASE4_IDENTITY currentSheriff=" + currentSheriff + " exactOriginal=" + (currentSheriff == Sheriff) + " actualPlayer=" + Game.GetPlayer() + " capturedPlayer=" + localInquiryPlayer)
 EndIf
EndFunction

; Private REMOTE actual actor handler, no direct dialogue/audio calls or answers.
Function QueueRoadVoice(int who)
 Trace("ENTRY QueueRoadVoice REMOTE actor audition role=" + who)
 If who != 1 && who != 9
  Trace("ROAD_VOICE REFUSED only role1 Dunmore or role9 Talbot")
  Return
 EndIf
 If !EnsureAuditRunning("road voice")
  Return
 EndIf
 If roadVoiceUsed || mode != 0 || remoteBrakePhase != 0 || adaBookPhase != 0 || ganttPhase != 0 || localInquiryPhase != 0
  Trace("ROAD_VOICE REFUSED repeated or busy")
  Return
 EndIf
 roadVoiceUsed = true
 roadVoiceEpoch += 1
 int generation = roadVoiceEpoch
 roadVoicePhase = 1
 mode = 8
 roadVoiceRole = who
 roadVoicePolls = 0
 roadVoicePlayer = Game.GetPlayer()
 Actor listener = roadVoicePlayer
 If who == 1
  roadVoiceActor = Game.GetFormFromFile(0x90A,"TLMWorldSlice.esp") as Actor
 Else
  roadVoiceActor = Game.GetFormFromFile(0x90F,"TLMWorldSlice.esp") as Actor
 EndIf
 roadVoiceSide = Game.GetFormFromFile(0x81B,"TheLastMeridian.esp") as Quest
 roadVoiceCell = Game.GetFormFromFile(0x802,"TLMWorldSlice.esp") as Cell
 If !RoadVoicePending(generation,1)
  Return
 EndIf
 If !listener || !roadVoiceActor || !roadVoiceSide || !roadVoiceCell || !Section || !MainQuest || !OpeningWorld || !DispatchItem
  EndRoadVoice("INCOMPLETE missing actual bindings")
  Return
 EndIf
 bool registered = RegisterForRemoteEvent(listener,"OnPlayerLoadGame")
 If !RoadVoicePending(generation,1)
  ; A late TRUE must not uninstall another active mode's player listener.
  If registered && mode == 0 && remoteBrakePhase == 0 && adaBookPhase == 0 && ganttPhase == 0 && localInquiryPhase == 0 && roadVoicePhase == 0
   UnregisterForRemoteEvent(listener,"OnPlayerLoadGame")
  EndIf
  Return
 EndIf
 If !registered
  EndRoadVoice("INCOMPLETE load registration refused")
  Return
 EndIf
 RegisterForMenuOpenCloseEvent("LoadingMenu")
 If RoadVoicePending(generation,1)
  StartTimer(25.0,TIMER_ROAD_VOICE)
 ElseIf mode == 0 && remoteBrakePhase == 0 && adaBookPhase == 0 && ganttPhase == 0 && localInquiryPhase == 0 && roadVoicePhase == 0
  ; A late menu registration must not remove a newer mode's shared filter.
  UnregisterForMenuOpenCloseEvent("LoadingMenu")
 EndIf
EndFunction

bool Function RoadVoicePending(int generation, int expectedPhase)
 Return roadVoiceEpoch == generation && roadVoicePhase == expectedPhase && mode == 8
EndFunction

bool Function RoadVoiceContext(int generation)
 Actor listener = roadVoicePlayer
 Actor speaker = roadVoiceActor
 If !listener || !speaker || !roadVoiceSide || !roadVoiceCell || !Section || !MainQuest || !OpeningWorld || !DispatchItem
  Return false
 EndIf
 If !Section.IsRunning() || !MainQuest.GetStageDone(10) || !roadVoiceSide.GetStageDone(5) || MainQuest.GetStageDone(20) || MainQuest.GetStageDone(50) || roadVoiceSide.GetStageDone(10) || roadVoiceSide.GetStageDone(14)
  Return false
 EndIf
 If listener.GetItemCount(DispatchItem) != 0 || listener.IsDead() || listener.IsDisabled() || !listener.Is3DLoaded() || listener.IsInCombat() || listener.IsInScene()
  Return false
 EndIf
 If speaker.IsDead() || speaker.IsDisabled() || !speaker.Is3DLoaded() || speaker.IsInCombat() || speaker.IsInScene() || speaker.IsTalking() || speaker.IsInDialogueWithPlayer()
  Return false
 EndIf
 If listener.GetWorldSpace() != OpeningWorld || listener.GetParentCell() != roadVoiceCell || speaker.GetParentCell() != roadVoiceCell || listener.GetDistance(speaker) > 320.0 || Utility.IsInMenuMode()
  Return false
 EndIf
 int aliasId = 12
 int actorId = 0x90A
 If roadVoiceRole == 9
  aliasId = 17
  actorId = 0x90F
 EndIf
 Actor original = Game.GetFormFromFile(actorId,"TLMWorldSlice.esp") as Actor
 ReferenceAlias roleAlias = Section.GetAlias(aliasId) as ReferenceAlias
 Actor currentSpeaker = None
 If roleAlias
  currentSpeaker = roleAlias.GetActorReference()
 EndIf
 Actor currentPlayer = Game.GetPlayer()
 Return original == speaker && currentSpeaker == speaker && currentPlayer == listener && RoadVoicePending(generation,1)
EndFunction

Function RoadVoiceTimer()
 int generation = roadVoiceEpoch
 If !RoadVoicePending(generation,1)
  Return
 EndIf
 roadVoicePolls += 1
 If roadVoicePolls > 90
  EndRoadVoice("INCOMPLETE bounded readiness timeout; no retry")
  Return
 EndIf
 If !Section.IsRunning() || !MainQuest.GetStageDone(10) || !roadVoiceSide.GetStageDone(5) || !roadVoicePlayer.Is3DLoaded() || !roadVoiceActor.Is3DLoaded() || Utility.IsInMenuMode()
  If RoadVoicePending(generation,1)
   StartTimer(1.0,TIMER_ROAD_VOICE)
  EndIf
  Return
 EndIf
 Trace("TLM_ROAD_VOICE_QA039 CAPTURE_READY role=" + roadVoiceRole + "; REMOTE original actor; return is not PLAY/hearing proof")
 If !RoadVoiceContext(generation)
  If RoadVoicePending(generation,1)
   EndRoadVoice("INCOMPLETE final actor/player/context refusal")
  EndIf
  Return
 EndIf
 If RoadVoicePending(generation,1)
  roadVoicePhase = 2
  bool accepted = roadVoiceActor.Activate(roadVoicePlayer,false)
  Trace("ROAD_VOICE actual Activate returned=" + accepted + "; no automatic answers or further activations")
  If RoadVoicePending(generation,2)
   EndRoadVoice("ISSUED once; pending caption remains player-owned; native playback proof required")
  EndIf
 EndIf
EndFunction

Function EndRoadVoice(string reason)
 Actor listener = roadVoicePlayer
 roadVoiceEpoch += 1
 roadVoicePhase = 0
 roadVoicePlayer = None
 roadVoiceActor = None
 If mode == 8
  mode = 0
 EndIf
 CancelTimer(TIMER_ROAD_VOICE)
 If listener
  UnregisterForRemoteEvent(listener,"OnPlayerLoadGame")
 EndIf
 UnregisterForMenuOpenCloseEvent("LoadingMenu")
 Trace("ROAD_VOICE " + reason)
EndFunction

Function CancelRoadVoice()
 If roadVoicePhase != 0
  EndRoadVoice("INCOMPLETE explicit cancellation; UI preserved")
 EndIf
EndFunction
