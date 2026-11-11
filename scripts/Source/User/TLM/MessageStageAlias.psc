Scriptname TLM:MessageStageAlias extends ReferenceAlias
{Generic: when the player activates this alias's reference, show a message
and set a stage on the owning quest according to the button pressed.
Used for the SQ01 clues (E1, E2), the notice board and the stove.
COMPILES; NOT YET RUN IN THE GAME (docs/design/VERIFY_LOG.md).

Button availability belongs in the Message form's button conditions, not here.}

Message Property MessageToShow Auto Const Mandatory

int[] Property ButtonStages Auto Const
{Stage to set for each button index. 0 (or no entry) means "do nothing",
e.g. for Cancel.}

int Property StageAlways = 0 Auto Const
{If above 0, this stage is set after the message whatever was pressed.
Use it for one-button observation messages.}

int Property RequireStageDone = 0 Auto Const
{If above 0, nothing happens until the owning quest has this stage done.}

int Property BlockIfStageDone = 0 Auto Const
{If above 0, nothing happens once the owning quest has this stage done.}

Event OnActivate(ObjectReference akActionRef)
	If akActionRef != Game.GetPlayer()
		Return
	EndIf
	Quest q = GetOwningQuest()
	If RequireStageDone > 0 && !q.GetStageDone(RequireStageDone)
		Return
	EndIf
	If BlockIfStageDone > 0 && q.GetStageDone(BlockIfStageDone)
		Return
	EndIf
	int button = MessageToShow.Show()
	If ButtonStages && button >= 0 && button < ButtonStages.Length
		If ButtonStages[button] > 0
			q.SetStage(ButtonStages[button])
		EndIf
	EndIf
	If StageAlways > 0
		q.SetStage(StageAlways)
	EndIf
EndEvent
