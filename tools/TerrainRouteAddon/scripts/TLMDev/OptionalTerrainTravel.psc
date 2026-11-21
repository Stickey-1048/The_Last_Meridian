Scriptname TLMDev:OptionalTerrainTravel extends ObjectReference
{Explicit optional development travel. No quest, inventory, health or actor outcome APIs are called.}
Message Property Prompt Auto Const Mandatory
ObjectReference Property Destination Auto Const Mandatory
WorldSpace Property SourceWorld Auto Const Mandatory
WorldSpace Property DestinationWorld Auto Const Mandatory
bool Property Outbound Auto Const
bool busy = false
int generation = 0

Event OnLoad()
	generation += 1
	busy = false
EndEvent

bool Function Context(Actor playerActor, int capturedGeneration)
	If !playerActor || playerActor != Game.GetPlayer() || !Destination || !Prompt || !SourceWorld || !DestinationWorld
		Return false
	EndIf
	If IsDisabled() || !Is3DLoaded() || Destination.IsDisabled() || playerActor.GetWorldSpace() != SourceWorld || GetWorldSpace() != SourceWorld || Destination.GetWorldSpace() != DestinationWorld || playerActor.GetDistance(Self) > 192.0
		Return false
	EndIf
	If playerActor.IsInScene() || IsInDialogueWithPlayer() || playerActor.IsDisabled() || !playerActor.Is3DLoaded() || playerActor.IsInCombat() || playerActor.IsDead()
		Return false
	EndIf
	Return playerActor == Game.GetPlayer() && capturedGeneration == generation
EndFunction

Function EndAttempt(int capturedGeneration)
	If capturedGeneration == generation
		busy = false
	EndIf
EndFunction

Event OnActivate(ObjectReference akActionRef)
	If busy
		Return
	EndIf
	; Claim the attempt before yielding context reads.
	busy = true
	Actor playerActor = Game.GetPlayer()
	int capturedGeneration = generation
	If akActionRef != playerActor || !Context(playerActor,capturedGeneration)
		EndAttempt(capturedGeneration)
		Return
	EndIf
	int answer = Prompt.Show()
	If answer != 0 || !Context(playerActor,capturedGeneration)
		EndAttempt(capturedGeneration)
		Return
	EndIf
	playerActor.MoveTo(Destination)
	If !playerActor.IsDead() && playerActor == Game.GetPlayer() && playerActor.GetWorldSpace() == DestinationWorld && playerActor.GetDistance(Destination) <= 128.0
		If Outbound
			Debug.Notification("Terrain preview: the return control is beside this arrival point.")
		Else
			Debug.Notification("Back at the Meridian road preview.")
		EndIf
	Else
		Debug.Notification("Travel could not be confirmed. This remains a development preview.")
	EndIf
	EndAttempt(capturedGeneration)
EndEvent
