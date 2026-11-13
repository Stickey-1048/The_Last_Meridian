Scriptname TLM:PlacedPeople extends Quest
{Development only, attached to TLM_Trial beside TLM:PlacedTrial. Self-test
scenario 11: people the plugin places (docs/design/TLM_GRAYBOX_trial.md, part
two). It must be removed before any release, with its quest and the records
the builder marks "trial".

Scenario 10 showed that the game's settler, placed by the plugin and then
enabled, does not stay where it was put: the next time the script looked it
stood 489 units away. A walk-through needs people who stand where the plugin
puts them, and who can be spoken to. This scenario asks the game two things,
and scores them first:

  - does a person on a base of the plugin's own stay? The base is a copy of
    the game's settler with nothing to go about: no packages and no script;
  - does activating that person reach a script on its alias? The alias
    carries TLM:MessageStageAlias, which shows a line and sets a stage: the
    walk-through's stand-in for talking to somebody. The player activates the
    person from where the scenario began, some 630 units off; if that sets
    no stage, the player is moved next to the person and tries again, as a
    player would.

Everything after the quest's last stage is reported, not scored, and is
there to find out why the settler moved. Each step of it is one the
self-test's watchdog writes down as a fact about the game if it does not
come back in its time, not as a failure; what was scored before stands.

  - A second person of the plugin's own, on the same spot, that does not
    even keep the settler's default package list; a second copy of the
    game's settler on that spot; and the first settler again, where it was
    placed on 2026-11-13. Each is enabled alone and looked at three times in
    six seconds: where it is, what package it runs, whether it sits or fights.
  - For each person that did not stay: is it kept in place when moved back,
    and when restrained and moved back?
  - Where the nearest place on the navigation mesh is for each spot a person
    was put (a person placed off the mesh could be moved onto it).
  - For each person that did not stay: is it kept in place with its AI off?
  - Did the settler go to a place in the room, or to a place near the
    player? It is enabled once more with the player standing elsewhere.

Nine functions are called here that this project has not called before. Four
only read something and are used in the scored part too (the clock, a square
root, the package a person runs, whether it sits). The five that move or
hold something are used only after it.

Lines that begin INFO are facts about the game, reported and not scored.

NOT YET COMPILED and NOT YET RUN IN THE GAME. On the stand-in engine
(tools/papyrus_sim) it runs to the end; what the stand-in does with a placed
person is partly a guess, and is marked so there.}

Group Aliases
	ReferenceAlias Property Alias_Person Auto Const Mandatory
	{The game's settler of scenario 10.}
	ReferenceAlias Property Alias_PersonOwn Auto Const Mandatory
	{A person on a base of the plugin's own: no packages, no script.}
	ReferenceAlias Property Alias_PersonBare Auto Const Mandatory
	{The same, and no default package list either.}
	ReferenceAlias Property Alias_SettlerOnFloor Auto Const Mandatory
	{The game's settler again, on the spot of the two above.}
EndGroup

Group Forms
	Form Property MarkerBase Auto Const
	{The game's plain marker (XMarker), looked up in Fallout4.esm when the plugin
	is built. None if it was not found. Used to bring the player back, should
	the player have to be moved, and by the navigation mesh experiment.}
EndGroup

int STAGE_TALK = 30 Const
int STAGE_DONE = 100 Const

; How far from where it was placed a person may be and still count as having
; stayed. A person standing still shifts its feet.
; (The lines written to the log say "64 units" in words.)
float STAY_WITHIN = 64.0 Const

; How long a step that moves somebody or something may take. On 2026-11-13
; one move of the player took 38 seconds, where the others took one to
; eleven; why is not known.
float MOVE_SECONDS = 150.0 Const

; How far above a spot the navigation mesh is asked about a second time. If
; that answer comes back on the floor, the question was heard.
; (The lines written to the log say "150 units" in words.)
float PROBE_ABOVE = 150.0 Const

; How close the player is put to a person for the second try at activating it.
float NEXT_TO = 100.0 Const

; When the clock in the lines about a person was started: when Enable came
; back, or when the person was last put back.
float clockFrom = 0.0

; -------------------------------------------------------------- scenario 11

Function Run(TLM:SelfTest akTest)
	Actor playerRef = Game.GetPlayer()
	akTest.Note("people: the player begins at " + Where(playerRef))

	; ---- 1. The quest starts.
	akTest.Step("starting the trial quest")
	bool started = Start()
	akTest.Note("people: Start returned " + started)
	akTest.CheckTrue("people: the quest runs once it has been started", IsRunning())

	; Where the scenario began. The player is moved only if the person cannot
	; be activated from here, and is brought back afterwards.
	ObjectReference homeMarker = None
	If MarkerBase
		homeMarker = playerRef.PlaceAtMe(MarkerBase)
	EndIf

	; ---- 2. Who is there, and where the plugin put them. All four are still
	; disabled, so each is where it was placed.
	akTest.Step("looking at the placed people")
	Actor ownPerson = Alias_PersonOwn.GetActorReference()
	Actor barePerson = Alias_PersonBare.GetActorReference()
	Actor floorSettler = Alias_SettlerOnFloor.GetActorReference()
	Actor firstSettler = Alias_Person.GetActorReference()
	akTest.CheckTrue("people: the PersonOwn alias holds an actor", ownPerson != None)
	akTest.Note("people: the other aliases hold an actor: PersonBare = " + (barePerson != None) + ", SettlerOnFloor = " + (floorSettler != None) + ", Person = " + (firstSettler != None))

	float ownX = 0.0
	float ownY = 0.0
	float ownZ = 0.0
	float bareX = 0.0
	float bareY = 0.0
	float bareZ = 0.0
	float floorX = 0.0
	float floorY = 0.0
	float floorZ = 0.0
	float settlerX = 0.0
	float settlerY = 0.0
	float settlerZ = 0.0
	If ownPerson
		ownX = ownPerson.GetPositionX()
		ownY = ownPerson.GetPositionY()
		ownZ = ownPerson.GetPositionZ()
		akTest.Note("people: the person of the plugin's own was placed at (" + ownX + ", " + ownY + ", " + ownZ + "), " + playerRef.GetDistance(ownPerson) + " from the player")
	EndIf
	If barePerson
		bareX = barePerson.GetPositionX()
		bareY = barePerson.GetPositionY()
		bareZ = barePerson.GetPositionZ()
		akTest.Note("people: the person with no default package list was placed at (" + bareX + ", " + bareY + ", " + bareZ + "); disabled = " + barePerson.IsDisabled())
	EndIf
	If floorSettler
		floorX = floorSettler.GetPositionX()
		floorY = floorSettler.GetPositionY()
		floorZ = floorSettler.GetPositionZ()
		akTest.Note("people: the game's settler on the same spot was placed at (" + floorX + ", " + floorY + ", " + floorZ + "); disabled = " + floorSettler.IsDisabled())
	EndIf
	If firstSettler
		settlerX = firstSettler.GetPositionX()
		settlerY = firstSettler.GetPositionY()
		settlerZ = firstSettler.GetPositionZ()
		akTest.Note("people: the game's settler of scenario 10 was placed at (" + settlerX + ", " + settlerY + ", " + settlerZ + "); disabled = " + firstSettler.IsDisabled())
	EndIf

	; What became of each: "not there" until it has been watched.
	string ownStayed = "not there"
	string bareStayed = "not there"
	string floorStayed = "not there"
	string settlerStayed = "not there"
	bool ownStrayed = false
	bool bareStrayed = false
	bool floorStrayed = false
	bool settlerStrayed = false
	bool movedPlayer = false
	float ownEnabledAt = 0.0

	; ---- 3. The person of the plugin's own: does it stay, can it be spoken to?
	If ownPerson
		akTest.CheckTrue("people: the person of the plugin's own starts disabled", ownPerson.IsDisabled())
		float ownAway = Watch(akTest, ownPerson, "the person of the plugin's own", ownX, ownY, ownZ, false)
		ownEnabledAt = clockFrom
		akTest.CheckFalse("people: the person of the plugin's own is disabled after Enable", ownPerson.IsDisabled())
		akTest.CheckTrue("people: the person of the plugin's own is within 64 units of where it was placed, six seconds after it was enabled", ownAway <= STAY_WITHIN)
		ownStrayed = ownAway > STAY_WITHIN
		ownStayed = YesNo(!ownStrayed)

		akTest.CheckFalse("people: stage 30 is set before the person has been activated", GetStageDone(STAGE_TALK))
		akTest.Step("having the player activate the person of the plugin's own")
		bool firstTry = ownPerson.Activate(playerRef)
		WaitForStage(STAGE_TALK)
		akTest.Note("people: the first try: Activate on the person from " + playerRef.GetDistance(ownPerson) + " away returned " + firstTry + "; stage 30 set = " + GetStageDone(STAGE_TALK))
		If !GetStageDone(STAGE_TALK)
			; Once more from close by, as a player would do it: that tells an
			; activation the game does not perform from afar from a script
			; that did not hear one.
			akTest.Step("moving the player next to the person of the plugin's own", MOVE_SECONDS)
			playerRef.MoveTo(ownPerson, NEXT_TO, 0.0, 0.0)
			movedPlayer = true
			If GetStageDone(STAGE_TALK)
				; The first activation was only slow to be heard.
				akTest.Note("people: stage 30 was set while the player was being moved: the first try was heard late, and there is no second")
			Else
				akTest.Step("having the player activate the person from close by")
				bool secondTry = ownPerson.Activate(playerRef)
				WaitForStage(STAGE_TALK)
				akTest.Note("people: the second try: Activate on the person from " + playerRef.GetDistance(ownPerson) + " away returned " + secondTry + "; stage 30 set = " + GetStageDone(STAGE_TALK))
			EndIf
		EndIf
		akTest.CheckTrue("people: activating the person sets stage 30 (TLM:MessageStageAlias on its alias)", GetStageDone(STAGE_TALK))
	EndIf

	; ---- 4. The quest's last stage: the last thing that is scored.
	akTest.Step("setting the trial quest's last stage")
	SetStage(STAGE_DONE)
	WaitForStage(STAGE_DONE)
	akTest.CheckTrue("people: the quest is completed by its last stage", IsCompleted())

	; ==== Nothing below is scored. Every step from here on is one that the
	; watchdog reports as a fact about the game if it does not come back.

	; ---- 5. Tidying up after the scored part.
	If movedPlayer
		If homeMarker
			akTest.Step("moving the player back to where the scenario began", MOVE_SECONDS, true)
			playerRef.MoveTo(homeMarker)
			akTest.Note("people: the player is back at " + Where(playerRef))
		Else
			akTest.Note("people: no marker base was found when the plugin was built, so the player was not brought back and stands at " + Where(playerRef) + " for the rest of the scenario")
		EndIf
	EndIf
	If homeMarker
		akTest.Step("removing the marker of where the scenario began", 45.0, true)
		homeMarker.Disable()
		homeMarker.Delete()
	EndIf
	If ownPerson
		clockFrom = ownEnabledAt
		Tell(akTest, ownPerson, "the person of the plugin's own", "after it was activated", ownX, ownY, ownZ)
		akTest.Step("disabling the person of the plugin's own", 45.0, true)
		ownPerson.Disable()
	EndIf

	; ---- 6. The others, one at a time.
	If barePerson
		bareStrayed = Watch(akTest, barePerson, "the person with no default package list", bareX, bareY, bareZ, true) > STAY_WITHIN
		bareStayed = YesNo(!bareStrayed)
		akTest.Step("disabling the person with no default package list", 45.0, true)
		barePerson.Disable()
	EndIf
	If floorSettler
		floorStrayed = Watch(akTest, floorSettler, "the game's settler on the same spot", floorX, floorY, floorZ, true) > STAY_WITHIN
		floorStayed = YesNo(!floorStrayed)
		akTest.Step("disabling the game's settler on the same spot", 45.0, true)
		floorSettler.Disable()
	EndIf
	If firstSettler
		settlerStrayed = Watch(akTest, firstSettler, "the game's settler of scenario 10", settlerX, settlerY, settlerZ, true) > STAY_WITHIN
		settlerStayed = YesNo(!settlerStrayed)
		akTest.Step("disabling the game's settler of scenario 10", 45.0, true)
		firstSettler.Disable()
	EndIf
	akTest.Note("people: stayed within 64 units of where it was placed for six seconds: the person of the plugin's own = " + ownStayed + ", the person with no default package list = " + bareStayed + ", the game's settler on the same spot = " + floorStayed + ", the game's settler of scenario 10 = " + settlerStayed)

	; ---- 7. What keeps in place a person that did not stay: moved back, and
	; restrained. The person of the plugin's own first.
	If ownPerson && ownStrayed
		PutBack(akTest, ownPerson, "the person of the plugin's own", ownX, ownY, ownZ)
	EndIf
	If barePerson && bareStrayed
		PutBack(akTest, barePerson, "the person with no default package list", bareX, bareY, bareZ)
	EndIf
	If floorSettler && floorStrayed
		PutBack(akTest, floorSettler, "the game's settler on the same spot", floorX, floorY, floorZ)
	EndIf
	If firstSettler && settlerStrayed
		PutBack(akTest, firstSettler, "the game's settler of scenario 10", settlerX, settlerY, settlerZ)
	EndIf

	; ---- 8. The navigation mesh under the two spots.
	If firstSettler
		Probe(akTest, playerRef, "where the game's settler of scenario 10 was placed", settlerX, settlerY, settlerZ)
	EndIf
	If ownPerson
		Probe(akTest, playerRef, "where the person of the plugin's own was placed", ownX, ownY, ownZ)
	EndIf

	; ---- 9. The same people with their AI off. Kept apart and late: of all
	; the experiments it is the one least sure to come back.
	If ownPerson && ownStrayed
		WithoutAI(akTest, ownPerson, "the person of the plugin's own", ownX, ownY, ownZ)
	EndIf
	If barePerson && bareStrayed
		WithoutAI(akTest, barePerson, "the person with no default package list", bareX, bareY, bareZ)
	EndIf
	If floorSettler && floorStrayed
		WithoutAI(akTest, floorSettler, "the game's settler on the same spot", floorX, floorY, floorZ)
	EndIf
	If firstSettler && settlerStrayed
		WithoutAI(akTest, firstSettler, "the game's settler of scenario 10", settlerX, settlerY, settlerZ)
	EndIf

	; ---- 10. A place in the room, or a place near the player? The player
	; has stood in one spot all along. Now the player stands where the
	; person of the plugin's own was placed, and the settler is enabled again.
	If firstSettler && settlerStrayed && ownPerson
		akTest.Step("experiment: moving the player to where the person of the plugin's own was placed", MOVE_SECONDS, true)
		playerRef.SetPosition(ownX, ownY, ownZ)
		akTest.Note("people: the player now stands at " + Where(playerRef))
		Watch(akTest, firstSettler, "the game's settler of scenario 10, with the player standing elsewhere", settlerX, settlerY, settlerZ, true)
		akTest.Step("disabling the game's settler of scenario 10", 45.0, true)
		firstSettler.Disable()
	EndIf
	akTest.Step("finishing the scenario", 45.0, true)
EndFunction

float Function Watch(TLM:SelfTest akTest, Actor akWho, string asName, float afX, float afY, float afZ, bool abAfterScoring)
	{Enables a placed person and says where it is at once, two seconds later
	and six seconds later. Returns how far it then is from where the plugin
	placed it. abAfterScoring: the steps are ones the watchdog reports as a
	fact, not as a failure.}
	akTest.Step("enabling " + asName, 45.0, abAfterScoring)
	float before = Utility.GetCurrentRealTime()
	akWho.Enable()
	clockFrom = Utility.GetCurrentRealTime()
	akTest.Note("people: " + asName + ": Enable took " + (clockFrom - before) + " seconds; disabled = " + akWho.IsDisabled() + ", 3D loaded = " + akWho.Is3DLoaded() + ", dead = " + akWho.IsDead() + ", in the player's cell = " + (akWho.GetParentCell() == Game.GetPlayer().GetParentCell()))
	Tell(akTest, akWho, asName, "at once", afX, afY, afZ)
	akTest.Step("watching " + asName + " for two seconds", 45.0, abAfterScoring)
	Utility.Wait(2.0)
	Tell(akTest, akWho, asName, "two seconds later", afX, afY, afZ)
	akTest.Step("watching " + asName + " for four seconds more", 45.0, abAfterScoring)
	Utility.Wait(4.0)
	Return Tell(akTest, akWho, asName, "six seconds later", afX, afY, afZ)
EndFunction

float Function Tell(TLM:SelfTest akTest, Actor akWho, string asName, string asWhen, float afX, float afY, float afZ)
	{Writes down where a person is and what it is doing. Returns how far it
	is from the spot given, height included.}
	float x = akWho.GetPositionX()
	float y = akWho.GetPositionY()
	float z = akWho.GetPositionZ()
	float flatAway = Math.sqrt((x - afX) * (x - afX) + (y - afY) * (y - afY))
	float awayNow = Math.sqrt((x - afX) * (x - afX) + (y - afY) * (y - afY) + (z - afZ) * (z - afZ))
	akTest.Note("people: " + asName + ", " + asWhen + " (" + (Utility.GetCurrentRealTime() - clockFrom) + " s on the clock): at (" + x + ", " + y + ", " + z + "), " + awayNow + " from where it was placed (" + flatAway + " seen from above, " + (z - afZ) + " higher), " + akWho.GetDistance(Game.GetPlayer()) + " from the player; package = " + akWho.GetCurrentPackage() + ", sit state = " + akWho.GetSitState() + ", in combat = " + akWho.IsInCombat())
	Return awayNow
EndFunction

Function PutBack(TLM:SelfTest akTest, Actor akWho, string asName, float afX, float afY, float afZ)
	{For a person that did not stay where it was placed: is it kept there
	once moved back, and when restrained and moved back?}
	akTest.Step("enabling " + asName + " again", 45.0, true)
	akWho.Enable()

	akTest.Step("experiment: moving " + asName + " back to where the plugin placed it", MOVE_SECONDS, true)
	akWho.MoveToMyEditorLocation()
	clockFrom = Utility.GetCurrentRealTime()
	Tell(akTest, akWho, asName + ", moved back to where it was placed", "at once", afX, afY, afZ)
	Utility.Wait(3.0)
	Tell(akTest, akWho, asName + ", moved back to where it was placed", "three seconds later", afX, afY, afZ)

	akTest.Step("experiment: restraining " + asName + " and moving it back", MOVE_SECONDS, true)
	bool restrained = akWho.SetRestrained(true)
	akWho.MoveToMyEditorLocation()
	clockFrom = Utility.GetCurrentRealTime()
	akTest.Note("people: SetRestrained on " + asName + " returned " + restrained)
	Tell(akTest, akWho, asName + ", restrained and moved back", "at once", afX, afY, afZ)
	Utility.Wait(3.0)
	Tell(akTest, akWho, asName + ", restrained and moved back", "three seconds later", afX, afY, afZ)
	akWho.SetRestrained(false)

	akTest.Step("disabling " + asName, 45.0, true)
	akWho.Disable()
EndFunction

Function WithoutAI(TLM:SelfTest akTest, Actor akWho, string asName, float afX, float afY, float afZ)
	{For a person that did not stay where it was placed: is it kept there
	with its AI off?}
	akTest.Step("enabling " + asName + " again", 45.0, true)
	akWho.Enable()

	akTest.Step("experiment: turning the AI of " + asName + " off and moving it back", MOVE_SECONDS, true)
	akWho.EnableAI(false)
	akWho.MoveToMyEditorLocation()
	clockFrom = Utility.GetCurrentRealTime()
	Tell(akTest, akWho, asName + ", its AI off and moved back", "at once", afX, afY, afZ)
	Utility.Wait(3.0)
	Tell(akTest, akWho, asName + ", its AI off and moved back", "three seconds later", afX, afY, afZ)
	akWho.EnableAI(true)

	akTest.Step("disabling " + asName, 45.0, true)
	akWho.Disable()
EndFunction

Function Probe(TLM:SelfTest akTest, Actor akPlayer, string asSpot, float afX, float afY, float afZ)
	{Asks the game for the place on the navigation mesh nearest to a spot:
	once from the spot itself, and once from above it.}
	If !MarkerBase
		akTest.Note("people: no marker base was found when the plugin was built, so the navigation mesh was not asked about " + asSpot)
		Return
	EndIf
	akTest.Step("making a marker for " + asSpot, 45.0, true)
	ObjectReference spotMarker = akPlayer.PlaceAtMe(MarkerBase)
	If !spotMarker
		akTest.Note("people: no marker could be made for " + asSpot)
		Return
	EndIf
	akTest.Step("experiment: moving the marker to " + asSpot, MOVE_SECONDS, true)
	spotMarker.SetPosition(afX, afY, afZ)
	akTest.Note("people: the marker set down " + asSpot + " says it is at " + Where(spotMarker))
	akTest.Step("experiment: moving the marker to the nearest place on the navigation mesh, from " + asSpot, MOVE_SECONDS, true)
	spotMarker.MoveToNearestNavmeshLocation()
	TellMesh(akTest, spotMarker, "from " + asSpot, afX, afY, afZ)

	akTest.Step("experiment: moving the marker to 150 units above " + asSpot, MOVE_SECONDS, true)
	spotMarker.SetPosition(afX, afY, afZ + PROBE_ABOVE)
	akTest.Step("experiment: moving the marker to the nearest place on the navigation mesh, from 150 units above " + asSpot, MOVE_SECONDS, true)
	spotMarker.MoveToNearestNavmeshLocation()
	TellMesh(akTest, spotMarker, "from 150 units above " + asSpot, afX, afY, afZ)

	akTest.Step("removing the marker", 45.0, true)
	spotMarker.Disable()
	spotMarker.Delete()
EndFunction

Function TellMesh(TLM:SelfTest akTest, ObjectReference akMarker, string asFrom, float afX, float afY, float afZ)
	float x = akMarker.GetPositionX()
	float y = akMarker.GetPositionY()
	float z = akMarker.GetPositionZ()
	float flatAway = Math.sqrt((x - afX) * (x - afX) + (y - afY) * (y - afY))
	akTest.Note("people: the nearest place on the navigation mesh, asked " + asFrom + ", is at (" + x + ", " + y + ", " + z + "): " + flatAway + " from the spot seen from above, " + (z - afZ) + " higher than it")
EndFunction

; ----------------------------------------------------------------- helpers

string Function Where(ObjectReference akRef)
	Return "(" + akRef.GetPositionX() + ", " + akRef.GetPositionY() + ", " + akRef.GetPositionZ() + ")"
EndFunction

string Function YesNo(bool abValue)
	If abValue
		Return "yes"
	EndIf
	Return "no"
EndFunction

Function WaitForStage(int aiStage)
	{Waits until this quest reports the stage, or five seconds.}
	int tries = 0
	While !GetStageDone(aiStage) && tries < 20
		Utility.Wait(0.25)
		tries += 1
	EndWhile
EndFunction
