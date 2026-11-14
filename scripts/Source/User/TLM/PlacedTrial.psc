Scriptname TLM:PlacedTrial extends Quest
{Development only, attached to TLM_Trial. Self-test scenario 10: the
placed-content trial (docs/design/TLM_GRAYBOX_trial.md). It must be removed
before any release, with its quest and the records the builder marks "trial".

Every earlier scenario makes what it needs at run time. A place a player can
walk through needs things that are in the plugin itself: people, triggers and
objects placed in a cell, and quest aliases that point at them. The builder
writes a few of those into the game's own test room (QASmoke). This scenario
asks the game whether they work there:

  - the quest starts, and its aliases hold the references the plugin placed;
  - the placed object, which borrows the world model of one of the game's
    items, can be picked up, and the game's own script on its alias
    (DefaultAliasOnContainerChangedTo) then sets a stage;
  - the placed trigger sets a stage when the player enters it, through the
    game's own script on its alias (DefaultAliasOnTriggerEnter). Two more
    triggers are tried for comparison and reported, not scored;
  - the placed person is there, starts disabled, and can be enabled (done
    last, so that nobody stands near the triggers while they are tried).

The three triggers are the same distance from where the scenario begins, and
the player is brought back there before each, so that each is entered the
same way.

Lines that begin INFO are facts about the game, reported and not scored.

What it cannot check: the name the placed person is shown under. The plugin
gives the alias a display name, but a script can only read it with a script
extender, which this project does not use. A person has to look.

COMPILES. RAN IN THE GAME on 2026-11-13, unattended, twice: 17 of 17 both
times (docs/design/VERIFY_LOG.md, the thirteenth and fourteenth runs). In the
first run the comparisons were a box on the game's own empty trigger and a
box on the layer L_ACTORZONE. In the second they named no collision layer at
all, as the game's own triggers do, one on the game's activator and one on
the plugin's: both set their stages. A trigger needs nothing but its box.

What the runs showed besides: the settler, once enabled, does not stand where
the plugin put it. Scenario 11 (TLM:PlacedPeople, on the same quest) found
out why: its sandbox package puts it on a seat of the room at once.
Changed since the second run and NOT YET COMPILED: the step that enables the
person is given 150 seconds.}

Group Aliases
	ReferenceAlias Property Alias_Person Auto Const Mandatory
	ReferenceAlias Property Alias_Trigger Auto Const Mandatory
	ReferenceAlias Property Alias_TriggerGameBase Auto Const Mandatory
	ReferenceAlias Property Alias_Object Auto Const Mandatory
	ReferenceAlias Property Alias_TriggerNoLayer Auto Const Mandatory
EndGroup

Group Forms
	Form Property TrialObject Auto Const Mandatory
	{TLM_MISC_TrialObject, the item the placed object is a copy of.}
	Form Property MarkerBase Auto Const
	{The game's plain marker (XMarker), looked up in Fallout4.esm when the plugin
	is built. None if it was not found. Used to bring the player back to where
	the scenario began.}
EndGroup

int STAGE_TRIGGER = 10 Const
int STAGE_TRIGGER_GAME_BASE = 11 Const
int STAGE_TRIGGER_NO_LAYER = 12 Const

; How long a step that moves the player may take. On 2026-11-13 one such move
; took 38 seconds, where the others took one to eleven; why is not known.
float MOVE_SECONDS = 150.0 Const
int STAGE_OBJECT = 20 Const
int STAGE_DONE = 100 Const

; -------------------------------------------------------------- scenario 10

Function Run(TLM:SelfTest akTest)
	Actor playerRef = Game.GetPlayer()
	akTest.Note("trial: the player begins at " + Where(playerRef))

	; ---- 1. The quest starts. (That it was not running before is not checked
	; here: the self-test does not get this far if it was.)
	akTest.Step("starting the trial quest")
	bool started = Start()
	akTest.Note("trial: Start returned " + started)
	akTest.CheckTrue("trial: the quest runs once it has been started", IsRunning())

	; Where the scenario began: the player is brought back here before each
	; trigger, so that each is entered the same way, and at the end.
	ObjectReference homeMarker = None
	If MarkerBase
		homeMarker = playerRef.PlaceAtMe(MarkerBase)
	Else
		akTest.Note("trial: no marker base was found when the plugin was built, so the player cannot be brought back between the triggers: each is entered from the one before")
	EndIf

	; ---- 2. The placed person, as the plugin leaves it: disabled. It stays so
	; until the triggers are done: an actor standing near a box could be
	; counted among the things inside it.
	akTest.Step("looking at the placed person")
	ObjectReference personRef = Alias_Person.GetReference()
	Actor placedPerson = Alias_Person.GetActorReference()
	akTest.CheckTrue("trial: the Person alias holds a reference", personRef != None)
	akTest.CheckTrue("trial: the reference in the Person alias is an actor", placedPerson != None)
	If placedPerson
		akTest.CheckTrue("trial: the placed person starts disabled", placedPerson.IsDisabled())
		akTest.CheckFalse("trial: the placed person is dead", placedPerson.IsDead())
		; Which cell a disabled reference says it is in is not known, so that is
		; reported here and scored once the person is enabled.
		akTest.Note("trial: the placed person, still disabled, is at " + Where(placedPerson) + ", " + playerRef.GetDistance(placedPerson) + " from the player; in the player's cell = " + (placedPerson.GetParentCell() == playerRef.GetParentCell()))
	EndIf

	; ---- 3. The placed object.
	akTest.Step("looking at the placed object")
	ObjectReference placedObject = Alias_Object.GetReference()
	akTest.CheckTrue("trial: the Object alias holds a reference", placedObject != None)
	If placedObject
		akTest.CheckTrue("trial: the placed object is in the cell the player is in", placedObject.GetParentCell() == playerRef.GetParentCell())
		akTest.Note("trial: the placed object is at " + Where(placedObject) + ", " + playerRef.GetDistance(placedObject) + " from the player; 3D loaded = " + placedObject.Is3DLoaded())
		akTest.CheckInt("trial: how many of the object the player has before picking it up", playerRef.GetItemCount(TrialObject), 0)
		akTest.CheckFalse("trial: stage 20 is set before the object has been picked up", GetStageDone(STAGE_OBJECT))
		akTest.Step("having the player pick the placed object up")
		bool activated = placedObject.Activate(playerRef)
		WaitForStage(STAGE_OBJECT)
		akTest.Note("trial: Activate on the placed object returned " + activated)
		akTest.CheckInt("trial: how many of the object the player has after picking it up", playerRef.GetItemCount(TrialObject), 1)
		akTest.CheckTrue("trial: picking the object up sets stage 20 (the game's own script on the alias)", GetStageDone(STAGE_OBJECT))
		If !GetStageDone(STAGE_OBJECT)
			; Reported, not scored: another way for the reference to reach the
			; player, to tell a pick-up that failed from a script that did not hear it.
			akTest.Step("moving the placed object into the player's inventory by script")
			playerRef.AddItem(placedObject)
			WaitForStage(STAGE_OBJECT)
			akTest.Note("trial: after AddItem of the placed object: the player has " + playerRef.GetItemCount(TrialObject) + ", stage 20 set = " + GetStageDone(STAGE_OBJECT))
		EndIf
	EndIf

	; ---- 4. The placed trigger, and the two that each differ from it in one
	; thing. All three are the same distance from where the scenario began.
	EnterTrigger(akTest, playerRef, homeMarker, Alias_Trigger, STAGE_TRIGGER, "the placed trigger", true)
	EnterTrigger(akTest, playerRef, homeMarker, Alias_TriggerGameBase, STAGE_TRIGGER_GAME_BASE, "the trigger made on the game's own empty trigger, with no layer", false)
	EnterTrigger(akTest, playerRef, homeMarker, Alias_TriggerNoLayer, STAGE_TRIGGER_NO_LAYER, "the trigger of the plugin's own with no layer", false)

	; ---- 5. Back to where the scenario began.
	If homeMarker
		akTest.Step("moving the player back to where the scenario began", MOVE_SECONDS)
		playerRef.MoveTo(homeMarker)
		akTest.Note("trial: the player is back at " + Where(playerRef))
		homeMarker.Disable()
		homeMarker.Delete()
	EndIf

	; ---- 6. The placed person, enabled.
	If placedPerson
		akTest.Step("enabling the placed person", MOVE_SECONDS)
		placedPerson.Enable()
		WaitFor3D(placedPerson)
		akTest.CheckFalse("trial: the placed person is disabled after Enable", placedPerson.IsDisabled())
		akTest.CheckTrue("trial: the placed person is in the cell the player is in", placedPerson.GetParentCell() == playerRef.GetParentCell())
		akTest.Note("trial: the placed person once enabled: 3D loaded = " + placedPerson.Is3DLoaded() + ", at " + Where(placedPerson) + ", " + playerRef.GetDistance(placedPerson) + " from the player")
	EndIf

	; ---- 7. The quest's last stage.
	akTest.Step("setting the trial quest's last stage")
	SetStage(STAGE_DONE)
	WaitForStage(STAGE_DONE)
	akTest.CheckTrue("trial: the quest is completed by its last stage", IsCompleted())
EndFunction

Function EnterTrigger(TLM:SelfTest akTest, Actor akPlayer, ObjectReference akHome, ReferenceAlias akAlias, int aiStage, string asName, bool abScored)
	{Brings the player back to where the scenario began, moves the player into
	the middle of a placed trigger, and waits for the stage that the game's own
	script on the trigger's alias should set.}
	akTest.Step("looking at " + asName)
	ObjectReference triggerRef = akAlias.GetReference()
	If abScored
		akTest.CheckTrue("trial: the alias of " + asName + " holds a reference", triggerRef != None)
	EndIf
	If !triggerRef
		If !abScored
			akTest.Note("trial: " + asName + " is not in this build of the plugin, or its alias is empty: nothing was tried")
		EndIf
		Return
	EndIf
	If akHome
		akTest.Step("moving the player back to where the scenario began, before " + asName, MOVE_SECONDS)
		akPlayer.MoveTo(akHome)
	EndIf
	bool before = GetStageDone(aiStage)
	If abScored
		akTest.CheckFalse("trial: stage " + aiStage + " is set before the player has entered " + asName, before)
	EndIf
	; How many things the trigger counts inside itself. It counts things of any
	; kind its layer lets in, not only the player, so what matters is the change.
	int insideBefore = triggerRef.GetTriggerObjectCount()
	akTest.Note("trial: " + asName + " is at " + Where(triggerRef) + ", " + akPlayer.GetDistance(triggerRef) + " from the player; things inside it before the move: " + insideBefore)
	akTest.Step("moving the player into " + asName, MOVE_SECONDS)
	akPlayer.MoveTo(triggerRef)
	WaitForStage(aiStage)
	int insideAfter = triggerRef.GetTriggerObjectCount()
	akTest.Note("trial: after the move the player is at " + Where(akPlayer) + ", " + akPlayer.GetDistance(triggerRef) + " from the middle of " + asName + "; things inside it: " + insideAfter + ", which is " + (insideAfter - insideBefore) + " more than before")
	If abScored
		akTest.CheckTrue("trial: entering " + asName + " sets stage " + aiStage + " (the game's own script on the alias)", GetStageDone(aiStage))
	Else
		akTest.Note("trial: entering " + asName + ": stage " + aiStage + " set = " + GetStageDone(aiStage) + " (it was " + before + " before)")
	EndIf
EndFunction

; ----------------------------------------------------------------- helpers

string Function Where(ObjectReference akRef)
	Return "(" + akRef.GetPositionX() + ", " + akRef.GetPositionY() + ", " + akRef.GetPositionZ() + ")"
EndFunction

Function WaitForStage(int aiStage)
	{Waits until this quest reports the stage, or five seconds.}
	int tries = 0
	While !GetStageDone(aiStage) && tries < 20
		Utility.Wait(0.25)
		tries += 1
	EndWhile
EndFunction

Function WaitFor3D(ObjectReference akRef)
	{Waits until the reference's 3D is loaded, or five seconds. Not the game's
	own WaitFor3DLoad: a wait of this script's can be counted on to end.}
	int tries = 0
	While !akRef.Is3DLoaded() && tries < 20
		Utility.Wait(0.25)
		tries += 1
	EndWhile
EndFunction
