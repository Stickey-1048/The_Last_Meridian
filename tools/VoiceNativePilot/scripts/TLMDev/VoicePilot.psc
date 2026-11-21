Scriptname TLMDev:VoicePilot extends ObjectReference
Actor Property OriginalSpeaker Auto Const Mandatory
ActorBase Property ExpectedBase Auto Const Mandatory
VoiceType Property ExpectedVoice Auto Const Mandatory
Topic Property LineTopic Auto Const Mandatory
Quest Property PilotQuest Auto Const Mandatory
Message Property Prompt Auto Const Mandatory
Message Property TextFallback Auto Const Mandatory
Bool busy = false
Int generation = 0

Event OnLoad()
    generation += 1
    busy = false
EndEvent

Event OnTimer(Int aiTimerID)
    ; This is a debounce only, never evidence that Say completed or was heard.
    If aiTimerID == generation
        busy = false
    EndIf
EndEvent

Bool Function Context(Actor playerActor, Actor speaker, Int capturedGeneration)
    ; Finish potentially yielding scene/dialogue observations before final state.
    If !playerActor || !speaker || playerActor.IsInScene() || speaker.IsInScene() || speaker.IsTalking() || speaker.IsInDialogueWithPlayer()
        Return false
    EndIf
    Return EligibleState(playerActor,speaker,capturedGeneration)
EndFunction

Bool Function EligibleState(Actor playerActor, Actor speaker, Int capturedGeneration)
    If IsDisabled() || !Is3DLoaded() || playerActor.IsDead() || playerActor.IsInCombat() || speaker.IsDead() || speaker.IsDisabled() || !speaker.Is3DLoaded() || speaker.IsInCombat()
        Return false
    EndIf
    If playerActor.GetParentCell() != GetParentCell() || speaker.GetParentCell() != GetParentCell() || playerActor.GetDistance(Self) > 384.0 || speaker.GetDistance(Self) > 512.0
        Return false
    EndIf
    Return speaker.GetActorBase() == ExpectedBase && speaker == OriginalSpeaker && playerActor == Game.GetPlayer() && capturedGeneration == generation && busy
EndFunction

Event OnActivate(ObjectReference akActionRef)
    Actor playerActor = Game.GetPlayer()
    Actor speaker = OriginalSpeaker
    If busy || akActionRef != playerActor
        Return
    EndIf
    busy = true
    generation += 1
    Int capturedGeneration = generation
    If !Context(playerActor,speaker,capturedGeneration)
        Debug.Notification("Voice audition unavailable. Stand near the living speaker outside combat.")
        Release(capturedGeneration)
        Return
    EndIf
    Int answer = Prompt.Show()
    If answer != 0 && answer != 1
        Release(capturedGeneration)
        Return
    EndIf
    If !Context(playerActor,speaker,capturedGeneration)
        Release(capturedGeneration)
        Return
    EndIf
    If answer == 1
        TextFallback.Show()
        Release(capturedGeneration)
        Return
    EndIf
    If !PilotQuest.IsRunning()
        If !PilotQuest.Start() || !PilotQuest.IsRunning()
            If Context(playerActor,speaker,capturedGeneration)
                TextFallback.Show()
            EndIf
            Release(capturedGeneration)
            Return
        EndIf
    EndIf
    ; No SetOverrideVoiceType or NPC mutation. Existing runtime type must match files.
    VoiceType observedVoice = speaker.GetVoiceType()
    If !Context(playerActor,speaker,capturedGeneration)
        Release(capturedGeneration)
        Return
    EndIf
    Bool voiceAvailable = LineTopic && ExpectedVoice && observedVoice == ExpectedVoice && speaker.GetVoiceType() == ExpectedVoice
    ; Finite identity/state tail after all yielding native eligibility observations.
    If !EligibleState(playerActor,speaker,capturedGeneration)
        Release(capturedGeneration)
        Return
    EndIf
    If !voiceAvailable
        TextFallback.Show()
        Release(capturedGeneration)
        Return
    EndIf
    speaker.Say(LineTopic,None,false,playerActor)
    Debug.Notification("Recording requested. Use the audition control's Read text option if it is silent.")
    ; No outcome, reward or completion acknowledgment follows Say.
    StartTimer(3.0,capturedGeneration)
EndEvent

Function Release(Int capturedGeneration)
    If generation == capturedGeneration
        busy = false
    EndIf
EndFunction


