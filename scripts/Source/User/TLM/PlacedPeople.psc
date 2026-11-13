Scriptname TLM:PlacedPeople extends Quest
{Development only, attached to TLM_Trial beside TLM:PlacedTrial. Self-test
scenario 11: people the plugin places (docs/design/TLM_GRAYBOX_trial.md, part
two). It must be removed before any release, with its quest and the records
the builder marks "trial".

Scenario 10 showed that the game's settler, placed by the plugin and then
enabled, does not stay where it was put: a moment later it stood 489 units
away. A walk-through needs people who stand where the plugin puts them, and
who can be spoken to. This scenario asks the game two things, and scores them:

  - does a person on a base of the plugin's own stay? The base is a copy of
    the game's settler with nothing to go about: no packages and no script;
  - does activating that person reach a script on its alias? The alias
    carries TLM:MessageStageAlias, which shows a line and sets a stage: the
    walk-through's stand-in for talking to somebody. The player activates the
    person from where the scenario began, some 630 units off; if that sets
    no stage, the player is moved next to the person and tries again, as a
    player would.

The rest is reported, not scored, to find out why the settler moved:

  - a second person of the plugin's own, on the same spot, that does not
    even keep the list of packages the game's settler falls back on;
  - a second copy of the game's settler, on a spot known to be open floor;
  - the first settler again, where it was placed on 2026-11-13.

Each is enabled alone and watched for six seconds: where it is, what package
it runs, whether it sits or fights.

Last come experiments, which use functions this project has not called
before. An experiment that does not come back ends the scenario, with what
was found so far written down, so they follow everything that is scored:

  - for each person that did not stay: is it kept in place by moving it back,
    by restraining it, or by turning its AI off?
  - where the nearest spot on the navigation mesh is for each place a person
    was put (a person placed off the mesh could be moved onto it).

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
	{The game's settler again, on open floor.}
EndGroup

Group Forms
	Form Property MarkerBase Auto Const
	{The game's plain marker (XMarker), looked up in Fallout4.esm when the plugin
	is built. None if it was not found. Used to bring the player back, should
	the player have to be moved, and by the navigation mesh experiment.}
EndGroup

int STAGE_TALK = 30 Const
int STAGE_DONE = 100 Const

; How far from where it was placed, seen from above, a person may be and
; still count as having stayed. A person standing still shifts its feet.
; (The lines written to the log say "64 units" in words.)
float STAY_WITHIN = 64.0 Const

; How long a step that moves the player may take. On 2026-11-13 one such move
; took 38 seconds, where the others took one to eleven; why is not known.
float MOVE_SECONDS = 150.0 Const

; How far above where a person was placed the navigation mesh experiment
; starts from. If the answer comes back on the floor, the question was heard.
; (The lines written to the log say "150 units" in words.)
float PROBE_ABOVE = 150.0 Const

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
	; be activated from here, and is then brought back.
	ObjectReference home = None
	If MarkerBase
		home = playerRef.PlaceAtMe(MarkerBase)
	EndIf

	; ---- 2. Who is there, and where the plugin put them. All four are still
	; disabled, so each is where it was placed.
	akTest.Step("looking at the placed people")
	Actor own = Alias_PersonOwn.GetActorReference()
	Actor bare = Alias_PersonBare.GetActorReference()
	Actor onFloor = Alias_SettlerOnFloor.GetActorReference()
	Actor settler = Alias_Person.GetActorReference()
	akTest.CheckTrue("people: the PersonOwn alias holds an actor", own != None)
	akTest.Note("people: the other aliases hold an actor: PersonBare = " + (bare != None) + ", SettlerOnFloor = " + (onFloor != None) + ", Person = " + (settler != None))

	float ownX
	float ownY
	float ownZ
	float bareX
	float bareY
	float bareZ
	float floorX
	float floorY
	float floorZ
	float settlerX
	float settlerY
	float settlerZ
	bool ownStrayed = false
	bool bareStrayed = false
	bool floorStrayed = false
	bool settlerStrayed = false

	; ---- 3. The person of the plugin's own: does it stay, can it be spoken to?
	If own
		ownX = own.GetPositionX()
		ownY = own.GetPositionY()
		ownZ = own.GetPositionZ()
		akTest.CheckTrue("people: the person of the plugin's own starts disabled", own.IsDisabled())
		akTest.Note("people: the person of the plugin's own was placed at (" + ownX + ", " + ownY + ", " + ownZ + "), " + playerRef.GetDistance(own) + " from the player")
		float ownAway = Watch(akTest, own, "the person of the plugin's own", ownX, ownY, ownZ)
		akTest.CheckFalse("people: the person of the plugin's own is disabled after Enable", own.IsDisabled())
		akTest.CheckTrue("people: the person of the plugin's own is within 64 units of where it was placed, six seconds after it was enabled", ownAway <= STAY_WITHIN)
		ownStrayed = ownAway > STAY_WITHIN

		akTest.CheckFalse("people: stage 30 is set before the person has been activated", GetStageDone(STAGE_TALK))
		akTest.Step("having the player activate the person of the plugin's own")
		bool activated = own.Activate(playerRef)
		WaitForStage(STAGE_TALK)
		akTest.Note("people: Activate on the person from " + playerRef.GetDistance(own) + " away returned " + activated + "; stage 30 set = " + GetStageDone(STAGE_TALK))
		If !GetStageDone(STAGE_TALK)
			; Once more from close by, as a player would do it: that tells an
			; activation the game does not perform from afar from a script
			; that did not hear one.
			akTest.Step("moving the player next to the person of the plugin's own", MOVE_SECONDS)
			playerRef.MoveTo(own, 150.0, 0.0, 0.0)
			akTest.Step("having the player activate the person from close by")
			activated = own.Activate(playerRef)
			WaitForStage(STAGE_TALK)
			akTest.Note("people: Activate on the person from " + playerRef.GetDistance(own) + " away returned " + activated + "; stage 30 set = " + GetStageDone(STAGE_TALK))
			If home
				akTest.Step("moving the player back to where the scenario began", MOVE_SECONDS)
				playerRef.MoveTo(home)
				akTest.Note("people: the player is back at " + Where(playerRef))
			EndIf
		EndIf
		akTest.CheckTrue("people: activating the person sets stage 30 (TLM:MessageStageAlias on its alias)", GetStageDone(STAGE_TALK))
		Tell(akTest, own, "the person of the plugin's own", "after it was activated", ownX, ownY, ownZ, Utility.GetCurrentRealTime())
		akTest.Step("disabling the person of the plugin's own")
		own.Disable()
	EndIf

	If home
		home.Disable()
		home.Delete()
	EndIf

	; ---- 4. The others, one at a time. Reported, not scored.
	If bare
		bareX = bare.GetPositionX()
		bareY = bare.GetPositionY()
		bareZ = bare.GetPositionZ()
		akTest.Note("people: the person with no default package list was placed at (" + bareX + ", " + bareY + ", " + bareZ + "); disabled = " + bare.IsDisabled())
		bareStrayed = Watch(akTest, bare, "the person with no default package list", bareX, bareY, bareZ) > STAY_WITHIN
		akTest.Step("disabling the person with no default package list")
		bare.Disable()
	EndIf
	If onFloor
		floorX = onFloor.GetPositionX()
		floorY = onFloor.GetPositionY()
		floorZ = onFloor.GetPositionZ()
		akTest.Note("people: the game's settler on open floor was placed at (" + floorX + ", " + floorY + ", " + floorZ + "); disabled = " + onFloor.IsDisabled())
		floorStrayed = Watch(akTest, onFloor, "the game's settler on open floor", floorX, floorY, floorZ) > STAY_WITHIN
		akTest.Step("disabling the game's settler on open floor")
		onFloor.Disable()
	EndIf
	If settler
		settlerX = settler.GetPositionX()
		settlerY = settler.GetPositionY()
		settlerZ = settler.GetPositionZ()
		akTest.Note("people: the game's settler of scenario 10 was placed at (" + settlerX + ", " + settlerY + ", " + settlerZ + "); disabled = " + settler.IsDisabled())
		settlerStrayed = Watch(akTest, settler, "the game's settler of scenario 10", settlerX, settlerY, settlerZ) > STAY_WITHIN
		akTest.Step("disabling the game's settler of scenario 10")
		settler.Disable()
	EndIf
	akTest.Note("people: did not stay within 64 units: the person of the plugin's own = " + ownStrayed + ", the person with no default package list = " + bareStrayed + ", the game's settler on open floor = " + floorStrayed + ", the game's settler of scenario 10 = " + settlerStrayed)

	; ---- 5. The quest's last stage. Before the experiments: one of them may
	; not come back.
	akTest.Step("setting the trial quest's last stage")
	SetStage(STAGE_DONE)
	WaitForStage(STAGE_DONE)
	akTest.CheckTrue("people: the quest is completed by its last stage", IsCompleted())

	; ---- 6. Experiments, the most wanted first. What keeps in place a person
	; of the plugin's own, if it did not stay.
	If own && ownStrayed
		TryToKeep(akTest, own, "the person of the plugin's own", ownX, ownY, ownZ)
	EndIf
	If bare && bareStrayed
		TryToKeep(akTest, bare, "the person with no default package list", bareX, bareY, bareZ)
	EndIf

	; ---- 7. Experiments: the navigation mesh under each spot.
	If settler
		Probe(akTest, playerRef, "where the game's settler of scenario 10 was placed", settlerX, settlerY, settlerZ)
	EndIf
	If own
		Probe(akTest, playerRef, "where the person of the plugin's own was placed", ownX, ownY, ownZ)
	EndIf
	If onFloor
		Probe(akTest, playerRef, "where the game's settler on open floor was placed", floorX, floorY, floorZ)
	EndIf

	; ---- 8. Experiments: what keeps the game's settler in place.
	If onFloor && floorStrayed
		TryToKeep(akTest, onFloor, "the game's settler on open floor", floorX, floorY, floorZ)
	EndIf
	If settler && settlerStrayed
		TryToKeep(akTest, settler, "the game's settler of scenario 10", settlerX, settlerY, settlerZ)
	EndIf
	akTest.Step("finishing the scenario")
EndFunction

float Function Watch(TLM:SelfTest akTest, Actor akWho, string asName, float afX, float afY, float afZ)
	{Enables a placed person and says where it is at once, two seconds later
	and six seconds later. Returns how far it then is, seen from above, from
	where the plugin placed it.}
	akTest.Step("enabling " + asName)
	float before = Utility.GetCurrentRealTime()
	akWho.Enable()
	float since = Utility.GetCurrentRealTime()
	akTest.Note("people: " + asName + ": Enable took " + (since - before) + " seconds; disabled = " + akWho.IsDisabled() + ", 3D loaded = " + akWho.Is3DLoaded() + ", dead = " + akWho.IsDead() + ", in the player's cell = " + (akWho.GetParentCell() == Game.GetPlayer().GetParentCell()))
	Tell(akTest, akWho, asName, "at once", afX, afY, afZ, since)
	akTest.Step("watching " + asName + " for two seconds")
	Utility.Wait(2.0)
	Tell(akTest, akWho, asName, "two seconds later", afX, afY, afZ, since)
	akTest.Step("watching " + asName + " for four seconds more")
	Utility.Wait(4.0)
	Return Tell(akTest, akWho, asName, "six seconds later", afX, afY, afZ, since)
EndFunction

float Function Tell(TLM:SelfTest akTest, Actor akWho, string asName, string asWhen, float afX, float afY, float afZ, float afSince)
	{Writes down where a person is and what it is doing. Returns how far it
	is, seen from above, from the spot given.}
	float x = akWho.GetPositionX()
	float y = akWho.GetPositionY()
	float z = akWho.GetPositionZ()
	float away = Math.sqrt((x - afX) * (x - afX) + (y - afY) * (y - afY))
	akTest.Note("people: " + asName + ", " + asWhen + " (" + (Utility.GetCurrentRealTime() - afSince) + " s on the clock): at (" + x + ", " + y + ", " + z + "), " + away + " from where it was placed seen from above, " + (z - afZ) + " higher; package = " + akWho.GetCurrentPackage() + ", sit state = " + akWho.GetSitState() + ", in combat = " + akWho.IsInCombat())
	Return away
EndFunction

Function Probe(TLM:SelfTest akTest, Actor akPlayer, string asSpot, float afX, float afY, float afZ)
	{An experiment: sets a marker down above a spot and asks the game to move
	it to the nearest place on the navigation mesh.}
	If !MarkerBase
		akTest.Note("people: no marker base was found when the plugin was built, so the navigation mesh was not asked about " + asSpot)
		Return
	EndIf
	akTest.Step("making a marker for " + asSpot)
	ObjectReference spotMarker = akPlayer.PlaceAtMe(MarkerBase)
	If !spotMarker
		akTest.Note("people: no marker could be made for " + asSpot)
		Return
	EndIf
	akTest.Step("experiment: moving the marker to 150 units above " + asSpot, 30.0, true)
	spotMarker.SetPosition(afX, afY, afZ + PROBE_ABOVE)
	akTest.Note("people: the marker set down 150 units above " + asSpot + " says it is at " + Where(spotMarker))
	akTest.Step("experiment: moving the marker to the nearest place on the navigation mesh, from above " + asSpot, 30.0, true)
	spotMarker.MoveToNearestNavmeshLocation()
	float x = spotMarker.GetPositionX()
	float y = spotMarker.GetPositionY()
	float z = spotMarker.GetPositionZ()
	float away = Math.sqrt((x - afX) * (x - afX) + (y - afY) * (y - afY))
	akTest.Note("people: the nearest place on the navigation mesh, asked from 150 units above " + asSpot + ", is at (" + x + ", " + y + ", " + z + "): " + away + " from the spot seen from above, " + (z - afZ) + " higher than it")
	akTest.Step("removing the marker")
	spotMarker.Disable()
	spotMarker.Delete()
EndFunction

Function TryToKeep(TLM:SelfTest akTest, Actor akWho, string asName, float afX, float afY, float afZ)
	{Experiments, for a person that did not stay where it was placed: is it
	kept there once moved back, when restrained, with its AI off?}
	akTest.Step("enabling " + asName + " again")
	akWho.Enable()

	akTest.Step("experiment: moving " + asName + " back to where the plugin placed it", 30.0, true)
	float since = Utility.GetCurrentRealTime()
	akWho.MoveToMyEditorLocation()
	Tell(akTest, akWho, asName + ", moved back to where it was placed", "at once", afX, afY, afZ, since)
	Utility.Wait(3.0)
	Tell(akTest, akWho, asName + ", moved back to where it was placed", "three seconds later", afX, afY, afZ, since)

	akTest.Step("experiment: restraining " + asName + " and moving it back", 30.0, true)
	bool restrained = akWho.SetRestrained(true)
	since = Utility.GetCurrentRealTime()
	akWho.MoveToMyEditorLocation()
	akTest.Note("people: SetRestrained on " + asName + " returned " + restrained)
	Tell(akTest, akWho, asName + ", restrained and moved back", "at once", afX, afY, afZ, since)
	Utility.Wait(3.0)
	Tell(akTest, akWho, asName + ", restrained and moved back", "three seconds later", afX, afY, afZ, since)
	akWho.SetRestrained(false)

	akTest.Step("experiment: turning the AI of " + asName + " off and moving it back", 30.0, true)
	akWho.EnableAI(false)
	since = Utility.GetCurrentRealTime()
	akWho.MoveToMyEditorLocation()
	Tell(akTest, akWho, asName + ", its AI off and moved back", "at once", afX, afY, afZ, since)
	Utility.Wait(3.0)
	Tell(akTest, akWho, asName + ", its AI off and moved back", "three seconds later", afX, afY, afZ, since)
	akWho.EnableAI(true)

	akTest.Step("disabling " + asName)
	akWho.Disable()
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
