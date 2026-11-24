Scriptname TLM:OpeningPrologue extends Quest
{One fresh contained journey. Owns only this scene; existing wreck quests retain authority.}
Quest Property Preview Auto Const Mandatory
Quest Property MainQuest Auto Const Mandatory
Quest Property SideQuest Auto Const Mandatory
Quest Property Section Auto Const Mandatory
Quest Property WreckEntry Auto Const Mandatory
Cell Property CarriageCell Auto Const Mandatory
Cell Property WreckCell Auto Const Mandatory
WorldSpace Property WreckWorld Auto Const Mandatory
Actor Property OriginalMarshal Auto Const Mandatory
ObjectReference Property SceneArrival Auto Const Mandatory
ObjectReference Property SceneMarshalMarker Auto Const Mandatory
ObjectReference Property ToolCase Auto Const Mandatory
ObjectReference Property ToolCaseSecuredMarker Auto Const Mandatory
ObjectReference Property DepartureControl Auto Const Mandatory
ObjectReference Property WreckMarshalMarker Auto Const Mandatory
ObjectReference Property WreckArrival Auto Const Mandatory
Message Property AskForCase Auto Const Mandatory
Message Property MotiveChoice Auto Const Mandatory
Message Property ReplyWork Auto Const Mandatory
Message Property ReplyTravel Auto Const Mandatory
Message Property ReplyWages Auto Const Mandatory
Message Property RequestChoice Auto Const Mandatory
Message Property WhoPritchard Auto Const Mandatory
Message Property AcceptReply Auto Const Mandatory
Message Property DeclineReply Auto Const Mandatory
Message Property ReadyDeparture Auto Const Mandatory
Message Property EarlyDeath Auto Const Mandatory
Sound Property RecordedGanttMotive Auto Const
Sound Property RecordedGanttWork Auto Const
Sound Property RecordedGanttRequest Auto Const
Sound Property RecordedGanttAccept Auto Const

bool used = false
int phase = 0
int epoch = 0
int polls = 0
bool busy = false
bool caseMoved = false
bool caseSecured = false
int motive = -1
bool heard = false
bool accepted = false
bool declined = false
bool requestFinished = false
bool marshalDiedEarly = false
bool handoffRetry = false
bool entryIssued = false
bool aliasesReleased = false
bool aliasesReleaseAttempted = false
bool fadeOwned = false
bool marshalBlockOwned = false
Actor player
int TIMER_SCENE = 74 Const
int TIMER_MOTIVE = 75 Const
int motiveHandle = -1
int motiveEpoch = -1
int motiveSerial = 0
bool motivePending = false
Actor motivePlayer
Actor motiveSpeaker
float motiveLeft = 0.0

bool Function HeardRequest()
 Return heard
EndFunction
bool Function AcceptedRequest()
 Return accepted
EndFunction
bool Function DeclinedRequest()
 Return declined
EndFunction
bool Function MarshalDiedBeforeWreck()
 Return marshalDiedEarly
EndFunction
bool Function HandoffCompleted()
 Return phase == 6
EndFunction

bool Function Bindings()
 Return Preview && MainQuest && SideQuest && Section && WreckEntry && CarriageCell && WreckCell && WreckWorld && OriginalMarshal && SceneArrival && SceneMarshalMarker && ToolCase && ToolCaseSecuredMarker && DepartureControl && WreckMarshalMarker && WreckArrival && AskForCase && MotiveChoice && ReplyWork && ReplyTravel && ReplyWages && RequestChoice && WhoPritchard && AcceptReply && DeclineReply && ReadyDeparture && EarlyDeath
EndFunction

bool Function OldQuestsFresh()
 Return !Preview.IsRunning() && !MainQuest.IsRunning() && !SideQuest.IsRunning() && !Section.IsRunning() && !WreckEntry.IsRunning() && MainQuest.GetCurrentStageID() == 0 && SideQuest.GetCurrentStageID() == 0
EndFunction

bool Function Pending(int generation, int expectedPhase)
 Return epoch == generation && phase == expectedPhase
EndFunction

bool Function CurrentPlayer(Cell place)
 Actor current = Game.GetPlayer()
 If !player || current != player || player.GetParentCell() != place || !player.Is3DLoaded() || player.IsDisabled() || player.IsInCombat() || player.IsDead()
  Return false
 EndIf
 Return true
EndFunction

bool Function SceneContext(int generation)
 If !Pending(generation,2) || !CurrentPlayer(CarriageCell) || !OldQuestsFresh() || Utility.IsInMenuMode()
  Return false
 EndIf
 Return Pending(generation,2)
EndFunction

bool Function LivingGantt(int generation)
 If !SceneContext(generation) || OriginalMarshal.GetParentCell() != CarriageCell || !OriginalMarshal.Is3DLoaded() || OriginalMarshal.IsDisabled() || OriginalMarshal.IsInCombat() || OriginalMarshal.IsInScene() || OriginalMarshal.IsDead()
  Return false
 EndIf
 Return Pending(generation,2)
EndFunction

Function QueuePrologue()
 If used || !Bindings() || !OldQuestsFresh()
  Debug.Trace("TLM_PROLOGUE REFUSED used/missing/nonfresh; existing story unchanged")
  Return
 EndIf
 If !IsRunning()
  If !Start() || !IsRunning()
   Return
  EndIf
 EndIf
 If used
  Return
 EndIf
 If !OldQuestsFresh() || OriginalMarshal.IsDead()
  StopSafely("existing state/dead original after initialization; no revival")
  Return
 EndIf
 used = true
 epoch += 1
 phase = 1
 polls = 0
 player = Game.GetPlayer()
 If !player || !RegisterForRemoteEvent(player,"OnPlayerLoadGame")
  StopSafely("player/load binding unavailable")
  Return
 EndIf
 Debug.Trace("TLM_PROLOGUE queued fresh carriage only; old wreck entry not queued")
 If phase == 1
  StartTimer(0.5,TIMER_SCENE)
 EndIf
EndFunction

Event OnTimer(int aiTimerID)
 If aiTimerID == TIMER_MOTIVE
  WatchMotiveAudio()
  Return
 EndIf
 If aiTimerID != TIMER_SCENE
  Return
 EndIf
 int generation = epoch
 If phase == 1
  polls += 1
  If polls > 30 || !OldQuestsFresh()
   StopSafely("carriage startup interrupted")
   Return
  EndIf
  If !CurrentPlayer(CarriageCell) || Utility.IsInMenuMode()
   If Pending(generation,1)
    StartTimer(1.0,TIMER_SCENE)
   EndIf
   Return
  EndIf
  If OriginalMarshal.IsDead() || SceneMarshalMarker.GetParentCell() != CarriageCell || ToolCase.GetParentCell() != CarriageCell || ToolCaseSecuredMarker.GetParentCell() != CarriageCell || DepartureControl.GetParentCell() != CarriageCell
   StopSafely("original actor or carriage bindings unavailable")
   Return
  EndIf
  If OriginalMarshal.GetParentCell() != CarriageCell
   If !Pending(generation,1) || !OldQuestsFresh() || OriginalMarshal.IsDead()
    Return
   EndIf
   OriginalMarshal.MoveTo(SceneMarshalMarker)
  EndIf
  If !Pending(generation,1)
   Return
  EndIf
  If OriginalMarshal.GetParentCell() != CarriageCell || OriginalMarshal.GetDistance(SceneMarshalMarker) > 16.0 || OriginalMarshal.IsDead()
   StopSafely("Gantt did not reach the carriage")
   Return
  EndIf
  If OriginalMarshal.IsDisabled()
   OriginalMarshal.EnableNoWait()
  EndIf
  If !Pending(generation,1)
   Return
  EndIf
  If !OriginalMarshal.Is3DLoaded()
   StartTimer(0.5,TIMER_SCENE)
   Return
  EndIf
  If !OriginalMarshal.IsActivationBlocked()
   marshalBlockOwned = true
   OriginalMarshal.BlockActivation(true,false)
  EndIf
  If !Pending(generation,1)
   Return
  EndIf
  phase = 2
  SetObjectiveDisplayed(10)
  Debug.Trace("TLM_PROLOGUE carriage ready; original Gantt alive; dispatch remains unavailable until wreck")
 ElseIf phase == 4
  ; Await ordinary authored loading, never repeat the MoveTo.
  polls += 1
  If AtWreck() && !entryIssued
   BeginOldWreck(generation)
  ElseIf polls > 30 || !player || player != Game.GetPlayer() || player.IsDead()
   StopSafely("journey arrival incomplete")
  ElseIf Pending(generation,4)
   StartTimer(0.5,TIMER_SCENE)
  EndIf
 ElseIf phase == 5
  polls += 1
  If MainQuest.GetStageDone(10) && Section.IsRunning() && OriginalMarshal.IsDead()
   CompletePrologue()
  ElseIf polls > 30
   StopSafely("wreck preparation did not finish")
  ElseIf Pending(generation,5)
   StartTimer(0.5,TIMER_SCENE)
  EndIf
 EndIf
EndEvent

Function Interact(ObjectReference akActivator, ObjectReference target, int role)
 If busy || phase != 2 || akActivator != Game.GetPlayer() || akActivator != player
  Return
 EndIf
 int generation = epoch
 If !SceneContext(generation)
  Return
 EndIf
 busy = true
 If role == 1 && target == ToolCase
  SecureCase(generation)
 ElseIf role == 2 && target == OriginalMarshal
  TalkGantt(generation)
 ElseIf role == 3 && target == DepartureControl
  Depart(generation)
 EndIf
 If generation == epoch
  busy = false
 EndIf
EndFunction

bool Function ActualCaseSecured()
 Return ToolCase.GetParentCell() == CarriageCell && ToolCase.GetDistance(ToolCaseSecuredMarker) <= 8.0
EndFunction

Function SecureCase(int generation)
 If !SceneContext(generation) || (caseSecured && ActualCaseSecured())
  Return
 EndIf
 caseSecured = false
 caseMoved = true
 ToolCase.MoveTo(ToolCaseSecuredMarker)
 If !Pending(generation,2) || !ActualCaseSecured() || !CurrentPlayer(CarriageCell)
  Return
 EndIf
 caseSecured = true
 SetObjectiveCompleted(10)
 If OriginalMarshal.IsDead()
  marshalDiedEarly = true
 EndIf
 If marshalDiedEarly || requestFinished
  SetObjectiveCompleted(20)
  SetObjectiveDisplayed(30)
 Else
  SetObjectiveDisplayed(20)
 EndIf
EndFunction

Function TalkGantt(int generation)
 If !SceneContext(generation)
  Return
 EndIf
 If OriginalMarshal.IsDead()
  marshalDiedEarly = true
  EarlyDeath.Show()
  Return
 EndIf
 If !LivingGantt(generation)
  Return
 EndIf
 If !caseSecured || !ActualCaseSecured()
  AskForCase.Show()
  Return
 EndIf
 If motive < 0
  int choice = ShowMotiveChoice(generation)
  If !LivingGantt(generation) || choice < 0 || choice > 2
   Return
  EndIf
  motive = choice
 EndIf
 If !requestFinished && !accepted && !declined
  int acknowledged = -1
  If motive == 0
   acknowledged = ShowGanttRecording(ReplyWork,RecordedGanttWork,6.72,generation)
  ElseIf motive == 1
   acknowledged = ReplyTravel.Show()
  Else
   acknowledged = ReplyWages.Show()
  EndIf
  If !LivingGantt(generation) || acknowledged != 0
   Return
  EndIf
  RequestDuty(generation)
 ElseIf !requestFinished
  FinishReply(generation)
 EndIf
EndFunction

Function RequestDuty(int generation)
 int choice = ShowGanttRecording(RequestChoice,RecordedGanttRequest,15.281,generation)
 If !LivingGantt(generation) || choice < 0 || choice > 2
  Return
 EndIf
 heard = true
 If choice == 2
  If WhoPritchard.Show() != 0 || !LivingGantt(generation)
   Return
  EndIf
  ; One reoffer per ordinary activation, never an automatic infinite question loop.
  choice = ShowGanttRecording(RequestChoice,RecordedGanttRequest,15.281,generation)
  If !LivingGantt(generation) || choice < 0 || choice > 2
   Return
  EndIf
  If choice == 2
   WhoPritchard.Show()
   Return
  EndIf
 EndIf
 If choice == 0
  accepted = true
  declined = false
 ElseIf choice == 1
  declined = true
  accepted = false
 EndIf
 FinishReply(generation)
EndFunction

Function FinishReply(int generation)
 If !LivingGantt(generation)
  Return
 EndIf
 int answer = -1
 If accepted
  answer = ShowGanttRecording(AcceptReply,RecordedGanttAccept,8.64,generation)
 ElseIf declined
  answer = DeclineReply.Show()
 EndIf
 If answer == 0 && LivingGantt(generation)
  requestFinished = true
  SetObjectiveCompleted(20)
  SetObjectiveDisplayed(30)
 EndIf
EndFunction

Function Depart(int generation)
 If !SceneContext(generation)
  Return
 EndIf
 If !caseSecured || !ActualCaseSecured()
  If OriginalMarshal.IsDead()
   marshalDiedEarly = true
   EarlyDeath.Show()
  ElseIf LivingGantt(generation)
   AskForCase.Show()
  EndIf
  Return
 EndIf
 If OriginalMarshal.IsDead()
  marshalDiedEarly = true
  If EarlyDeath.Show() != 0 || !SceneContext(generation)
   Return
  EndIf
 ElseIf !requestFinished && !handoffRetry
  TalkGantt(generation)
  Return
 EndIf
 If ReadyDeparture.Show() != 0 || !SceneContext(generation) || !ActualCaseSecured()
  Return
 EndIf
 Handoff(generation)
EndFunction

Function Handoff(int generation)
 If !SceneContext(generation) || !ActualCaseSecured() || !OldQuestsFresh()
  Return
 EndIf
 phase = 3
 fadeOwned = true
 Game.FadeOutGame(true,true,0.0,0.5,true)
 Utility.WaitMenuMode(0.6)
 If !Pending(generation,3) || !CurrentPlayer(CarriageCell) || !OldQuestsFresh()
  If Pending(generation,3)
   StopSafely("departure context changed before the wreck")
  Else
   RestoreFade()
  EndIf
  Return
 EndIf
 ; Returning the same actor (living or already observed dead) never resurrects him.
 If OriginalMarshal.GetWorldSpace() != WreckWorld || OriginalMarshal.GetDistance(WreckMarshalMarker) > 16.0
  OriginalMarshal.MoveTo(WreckMarshalMarker)
 EndIf
 If !Pending(generation,3)
  Return
 EndIf
 If OriginalMarshal.GetWorldSpace() != WreckWorld || OriginalMarshal.GetDistance(WreckMarshalMarker) > 16.0
  StopSafely("Gantt did not reach the wreck")
  Return
 EndIf
 ReleaseMarshalBlock()
 If !Pending(generation,3) || !CurrentPlayer(CarriageCell) || !OldQuestsFresh()
  If Pending(generation,3)
   StopSafely("departure context changed before arrival")
  Else
   RestoreFade()
  EndIf
  Return
 EndIf
 phase = 4
 polls = 0
 player.MoveTo(WreckArrival)
 If !Pending(generation,4)
  Return
 EndIf
 If !AtWreck()
  StartTimer(0.5,TIMER_SCENE)
  Return
 EndIf
 BeginOldWreck(generation)
EndFunction

bool Function AtWreck()
 Return player && player == Game.GetPlayer() && player.GetParentCell() == WreckCell && player.GetWorldSpace() == WreckWorld && player.Is3DLoaded() && !player.IsDead() && OriginalMarshal.GetWorldSpace() == WreckWorld && OriginalMarshal.GetDistance(WreckMarshalMarker) <= 16.0
EndFunction

bool Function ReleaseAliases()
 int i = 0
 If !aliasesReleaseAttempted
  ; Publish before native calls; a saved interruption must not blindly repeat Clear.
  aliasesReleaseAttempted = true
  While i < 3
   ReferenceAlias owned = GetAlias(i) as ReferenceAlias
   If owned
    owned.Clear()
   EndIf
   i += 1
  EndWhile
 EndIf
 bool empty = true
 i = 0
 While i < 3
  ReferenceAlias ownAlias = GetAlias(i) as ReferenceAlias
  If !ownAlias || ownAlias.GetReference()
   empty = false
  EndIf
  i += 1
 EndWhile
 aliasesReleased = empty
 Return empty
EndFunction

Function BeginOldWreck(int generation)
 If entryIssued || !Pending(generation,4) || !AtWreck() || !OldQuestsFresh()
  Return
 EndIf
 If !ReleaseAliases()
  If Pending(generation,4)
   StopSafely("scene alias release could not be verified; wreck entry not issued")
  Else
   RestoreFade()
  EndIf
  Return
 EndIf
 If !Pending(generation,4) || !AtWreck() || !OldQuestsFresh()
  If Pending(generation,4)
   StopSafely("wreck context changed after releasing scene aliases")
  Else
   RestoreFade()
  EndIf
  Return
 EndIf
 TLM:WorldEntry entry = WreckEntry as TLM:WorldEntry
 If !entry
  StopSafely("wreck entry binding unavailable")
  Return
 EndIf
 entryIssued = true
 phase = 5
 polls = 0
 Debug.Trace("TLM_PROLOGUE actual wreck arrival; own aliases released; existing guarded Begin once")
 entry.Begin()
 If Pending(generation,5)
  StartTimer(0.5,TIMER_SCENE)
 EndIf
EndFunction

Function MarshalDied(Actor whom)
 If whom == OriginalMarshal && phase == 2 && OriginalMarshal.IsDead()
  marshalDiedEarly = true
  epoch += 1
  busy = false
  StopMotiveAudio()
  SetObjectiveCompleted(20)
  If caseSecured && ActualCaseSecured()
   SetObjectiveDisplayed(30)
  Else
   SetObjectiveDisplayed(10)
  EndIf
 EndIf
EndFunction

Function ReleaseMarshalBlock()
 If marshalBlockOwned && OriginalMarshal
  marshalBlockOwned = false
  OriginalMarshal.BlockActivation(false,false)
 EndIf
EndFunction

Function RestoreFade()
 If fadeOwned
  fadeOwned = false
  Game.FadeOutGame(false,true,0.0,0.5)
 EndIf
EndFunction

Function CompletePrologue()
 phase = 6
 epoch += 1
 busy = false
 StopMotiveAudio()
 CancelTimer(TIMER_SCENE)
 RestoreFade()
 ReleaseMarshalBlock()
 SetObjectiveCompleted(30)
 If player
  UnregisterForRemoteEvent(player,"OnPlayerLoadGame")
 EndIf
 Debug.Trace("TLM_PROLOGUE complete: real wreck setup/dead original; dispatch remains ordinary postwreck pickup")
 Stop()
EndFunction

Function StopSafely(string reason)
 used = true
 epoch += 1
 phase = 7
 busy = false
 StopMotiveAudio()
 CancelTimer(TIMER_SCENE)
 RestoreFade()
 ReleaseMarshalBlock()
 ReleaseAliases()
 If player
  UnregisterForRemoteEvent(player,"OnPlayerLoadGame")
 EndIf
 Debug.Trace("TLM_PROLOGUE interrupted: " + reason + "; no revival/reset/dispatch grant/forced quest stage")
 Debug.Notification("The journey was interrupted. Return to the main menu and begin a new journey.")
 Stop()
EndFunction

Event Actor.OnPlayerLoadGame(Actor akSender)
 If !used || phase == 0 || phase == 6 || phase == 7 || akSender != player
  Return
 EndIf
 epoch += 1
 busy = false
 StopMotiveAudio()
 If phase == 1
  int generation = epoch
  ; A valid saved startup resumes readiness, not transport. Keep its existing deadline.
  ; 3D may still be loading here: the ordinary timer waits before any actor effect.
  If player && player == Game.GetPlayer() && player.GetParentCell() == CarriageCell && !player.IsDead() && !player.IsDisabled() && OldQuestsFresh() && !OriginalMarshal.IsDead() && Pending(generation,1)
   StartTimer(0.5,TIMER_SCENE)
   Return
  EndIf
 EndIf
 If phase == 2 && CurrentPlayer(CarriageCell) && OldQuestsFresh()
  If caseMoved && ActualCaseSecured()
   caseSecured = true
   SetObjectiveCompleted(10)
   If OriginalMarshal.IsDead() || requestFinished
    SetObjectiveCompleted(20)
    SetObjectiveDisplayed(30)
   Else
    SetObjectiveDisplayed(20)
   EndIf
  Else
   caseSecured = false
   SetObjectiveCompleted(10,false)
   SetObjectiveDisplayed(10)
   SetObjectiveDisplayed(20,false)
   SetObjectiveDisplayed(30,false)
  EndIf
  RestoreFade()
  Return
 EndIf
 If phase == 5 && AtWreck()
  ; Observe the saved in-flight old Begin. Never issue it again or move anybody.
  polls = 0
  StartTimer(0.5,TIMER_SCENE)
 ElseIf (phase == 3 || phase == 4) && AtWreck() && !entryIssued && OldQuestsFresh()
  phase = 4
  StartTimer(0.5,TIMER_SCENE)
 ElseIf (phase == 3 || phase == 4) && CurrentPlayer(CarriageCell) && !entryIssued && OldQuestsFresh()
  phase = 2
  handoffRetry = true
  RestoreFade()
 Else
  StopSafely("saved journey context could not be resumed")
 EndIf
EndEvent

; One optional private recording. No menu-mode refusal: its caption may remain open.
bool Function MotiveAudioContext(Actor listener, Actor speakerActor, int generation)
 If !listener || !speakerActor || listener != player || speakerActor != OriginalMarshal || listener != Game.GetPlayer()
  Return false
 EndIf
 If listener.GetParentCell() != CarriageCell || speakerActor.GetParentCell() != CarriageCell || listener.GetDistance(speakerActor) > 320.0
  Return false
 EndIf
 If !listener.Is3DLoaded() || !speakerActor.Is3DLoaded() || listener.IsDisabled() || speakerActor.IsDisabled() || listener.IsInCombat() || speakerActor.IsInCombat() || listener.IsInScene() || speakerActor.IsInScene() || speakerActor.IsTalking() || speakerActor.IsInDialogueWithPlayer() || listener.IsDead() || speakerActor.IsDead()
  Return false
 EndIf
 Return Pending(generation,2) && listener == player && speakerActor == OriginalMarshal
EndFunction

int Function ShowMotiveChoice(int generation)
 Return ShowGanttRecording(MotiveChoice,RecordedGanttMotive,5.28,generation)
EndFunction

int Function ShowGanttRecording(Message lineMessage, Sound recording, float duration, int generation)
 If !lineMessage
  Return -1
 EndIf
 Actor listener = player
 Actor speakerActor = OriginalMarshal
 int instance = -1
 int serial = -1
 If recording && !motivePending && MotiveAudioContext(listener,speakerActor,generation)
  ; Publish pending ownership before native Play can yield or deliver the existing load event.
  motivePending = true
  motiveEpoch = generation
  motivePlayer = listener
  motiveSpeaker = speakerActor
  motiveSerial += 1
  serial = motiveSerial
  instance = recording.Play(speakerActor)
  If !Pending(generation,2) || !motivePending || motiveEpoch != generation || motiveSerial != serial
   If instance >= 0
    Sound.StopInstance(instance)
   EndIf
   Return -1
  EndIf
  If instance >= 0
   motiveHandle = instance
   motiveLeft = duration
   StartTimer(0.25,TIMER_MOTIVE)
   Debug.Trace("TLM_PROLOGUE_VOICE PLAY caption=" + lineMessage + " handle=" + instance + " seconds=" + duration)
   If !MotiveAudioContext(listener,speakerActor,generation)
    StopGanttRecordingIfOwned(instance,generation,serial)
    Return -1
   EndIf
  Else
   StopGanttRecordingIfOwned(instance,generation,serial)
  EndIf
 EndIf
 If !Pending(generation,2) || !LivingGantt(generation)
  Return -1
 EndIf
 int answer = lineMessage.Show()
 StopGanttRecordingIfOwned(instance,generation,serial)
 If !Pending(generation,2)
  Return -1
 EndIf
 If instance >= 0 && !MotiveAudioContext(listener,speakerActor,generation)
  Return -1
 EndIf
 Return answer
EndFunction

Function StopGanttRecordingIfOwned(int instance, int generation, int serial)
 If motivePending && motiveEpoch == generation && motiveSerial == serial && motiveHandle == instance
  StopMotiveAudio()
 EndIf
EndFunction

Function StopMotiveAudio()
 int instance = motiveHandle
 motiveHandle = -1
 motiveEpoch = -1
 motivePending = false
 motiveSerial += 1
 motivePlayer = None
 motiveSpeaker = None
 motiveLeft = 0.0
 CancelTimer(TIMER_MOTIVE)
 If instance >= 0
  Sound.StopInstance(instance)
 EndIf
EndFunction

Function WatchMotiveAudio()
 If !motivePending || motiveHandle < 0
  Return
 EndIf
 int generation = motiveEpoch
 int serial = motiveSerial
 int instance = motiveHandle
 bool current = MotiveAudioContext(motivePlayer,motiveSpeaker,generation)
 If !motivePending || motiveEpoch != generation || motiveSerial != serial || motiveHandle != instance
  Return
 EndIf
 If !current
  If Pending(generation,2)
   epoch += 1
   busy = false
  EndIf
  StopGanttRecordingIfOwned(instance,generation,serial)
  Return
 EndIf
 motiveLeft -= 0.25
 If motiveLeft <= 0.0
  StopGanttRecordingIfOwned(instance,generation,serial)
 ElseIf Pending(generation,2) && motivePending && motiveEpoch == generation && motiveSerial == serial && motiveHandle == instance
  StartTimer(0.25,TIMER_MOTIVE)
 EndIf
EndFunction

