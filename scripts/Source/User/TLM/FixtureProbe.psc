Scriptname TLM:FixtureProbe extends Quest
{Development only, attached to TLM_Core next to TLM:Core and TLM:SelfTest.
Self-test scenarios 2 and 3. It must be removed before any release.

It finds out, in the game, whether the pieces a fuller test of the quest
needs can be made at run time, so that the test matrix does not have to wait
for a hand-built test cell.

  Scenario 2 (Run): an actor spawned from a base form, forced into a quest
  alias, killed, and noticed by the alias's script; a timer on a quest script.
  Scenario 3 (RunDistance): distance events between the player and a marker
  placed at run time, and the main quest's own "the player has left" watch.

Most of what it writes is reported, not scored: a line that begins INFO is a
fact about the game, not about the design. The scored checks are the ones the
quest's design already relies on.

COMPILES. RAN IN THE GAME on 2026-11-12: scenario 2 passed its 14 checks and
scenario 3 its 8 (docs/design/VERIFY_LOG.md). Scenario 3's first experiment
did not come back: MoveTo on a placed copy of this plugin's item, which has no
model, never returns. That is what had stopped an earlier version of scenario
2. The experiments after it have therefore never run.
Since that run one check was added to scenario 2, which now makes 15: that an
actor nobody is talking to is "not in dialogue with the player" (amendment
A25); and two reported lines about whether a kill by the player counts as a
fight. THOSE THREE LINES ARE NOT YET COMPILED.}

Quest Property TLM_MQ01 Auto Const Mandatory
Form Property TornTransitPass Auto Const Mandatory
{Any item of this plugin. It has no model yet; scenario 3 ends with an
experiment on what that does to a placed copy.}
Form Property FixtureActorBase Auto Const
{An actor base from the game to spawn: the generic settler, looked up in
Fallout4.esm when the plugin is built. None if it was not found.}
Form Property FixtureMarkerBase Auto Const
{The game's plain marker (XMarker), looked up in Fallout4.esm when the plugin
is built. None if it was not found.}

int TIMER_PROBE = 7 Const
bool timerFired = false
int distanceEvents = 0
float lastEventDistance = 0.0

; ------------------------------------------------------------- scenario 2

Function Run(TLM:SelfTest akTest)
	Actor player = Game.GetPlayer()
	TLM:MQ01Quest mq = TLM_MQ01 as TLM:MQ01Quest
	If !mq
		akTest.Fail("probe: TLM_MQ01 does not carry its quest script")
		Return
	EndIf

	; ---- a timer on a quest script, checked further down
	timerFired = false
	StartTimer(1.0, TIMER_PROBE)

	; ---- the main quest, as far as a live ambush
	akTest.Reach(TLM_MQ01, 10)
	akTest.Reach(TLM_MQ01, 20)
	akTest.Reach(TLM_MQ01, 30)
	akTest.CheckTrue("probe: the ambush is live", mq.IsLive())

	If !FixtureActorBase
		akTest.Fail("probe: no actor base was found in Fallout4.esm when the plugin was built, so no actor can be spawned")
		Return
	EndIf

	; ---- 1. A caravan hand who dies by someone else's hand.
	; The alias is flagged Protected. The quest's own KillByCutters clears that
	; on the actor before it kills; this shows whether it needs to.
	akTest.Step("spawning the drover")
	Actor abel = SpawnActor(player)
	akTest.CheckTrue("probe: an actor can be spawned at run time", abel != None)
	If !abel
		Return
	EndIf
	mq.Alias_CaravanDrover.ForceRefTo(abel)
	akTest.CheckTrue("probe: ForceRefTo fills the drover alias", mq.Alias_CaravanDrover.GetActorReference() == abel)
	akTest.CheckTrue("probe: the quest script sees the drover alive", mq.IsAliveAlias(mq.Alias_CaravanDrover))
	; Amendment A25 asks the game whether the Cutter lead is talking to the
	; player. There is no dialogue to make that true; this shows only that the
	; question can be asked and is answered "no" when nobody is talking.
	akTest.CheckFalse("probe: an actor nobody is talking to is not in dialogue with the player", abel.IsInDialogueWithPlayer())
	akTest.Note("probe: drover in a Protected alias: IsEssential = " + abel.IsEssential())
	akTest.Step("killing the drover with no killer")
	abel.Kill()
	Utility.Wait(1.5)
	akTest.Note("probe: drover after Kill() with no killer, protection not cleared: dead = " + abel.IsDead())
	If !abel.IsDead()
		akTest.Step("clearing the drover's protection and killing him")
		abel.SetProtected(false)
		abel.Kill()
		Utility.Wait(1.5)
		akTest.Note("probe: drover after SetProtected(false) and Kill(): dead = " + abel.IsDead())
	EndIf
	akTest.CheckTrue("probe: the drover can be killed by script", abel.IsDead())
	akTest.CheckFalse("probe: a hand's death not caused by the player is not a betrayal", TLM_MQ01.GetStageDone(35))
	akTest.CheckFalse("probe: the quest script no longer sees the drover alive", mq.IsAliveAlias(mq.Alias_CaravanDrover))

	; ---- 2. The Cutter lead killed by the player: the alias's script should
	; hear the death and resolve the encounter as "saved".
	akTest.Step("spawning the Cutter lead and killing him as the player")
	Actor lead = SpawnActor(player)
	If lead
		mq.Alias_CutterLead.ForceRefTo(lead)
		akTest.CheckTrue("probe: ForceRefTo fills the Cutter lead alias", mq.Alias_CutterLead.GetActorReference() == lead)
		lead.Kill(player)
		; Reported, not scored. In the run of 2026-11-12 a case showed, indirectly,
		; that the game takes a kill by the player for a fight, with three other
		; actors standing by. Here nobody else is alive.
		akTest.Note("probe: player in combat straight after Kill(player) on the Cutter lead, nobody standing by = " + player.IsInCombat())
		WaitForStage(31)
		akTest.Note("probe: Cutter lead after Kill(player): dead = " + lead.IsDead())
		akTest.Note("probe: player in combat once his death has been announced = " + player.IsInCombat())
		akTest.CheckTrue("probe: the Cutter alias script heard the death and set stage 31", TLM_MQ01.GetStageDone(31))
		akTest.CheckTrue("probe: the outcome is 'saved'", mq.Outcome() == 1)
	Else
		akTest.Fail("probe: a second actor could not be spawned")
	EndIf

	; ---- 3. The caravan master killed by the player after the rescue: the
	; hand alias's script should hear it, and betrayal should override "saved".
	akTest.Step("spawning the caravan master and killing her as the player")
	Actor nell = SpawnActor(player)
	If nell
		mq.Alias_CaravanMaster.ForceRefTo(nell)
		akTest.CheckTrue("probe: the quest script sees the caravan master alive", mq.IsAliveAlias(mq.Alias_CaravanMaster))
		nell.Kill(player)
		WaitForStage(35)
		akTest.Note("probe: caravan master after Kill(player): dead = " + nell.IsDead())
		akTest.CheckTrue("probe: the hand alias script heard the death and set stage 35", TLM_MQ01.GetStageDone(35))
		akTest.CheckTrue("probe: betrayal overrides the earlier outcome", mq.Outcome() == 3)
	Else
		akTest.Fail("probe: a third actor could not be spawned")
	EndIf

	; ---- 4. The timer started at the top.
	akTest.CheckTrue("probe: a timer on a quest script fires", timerFired)

	; ---- tidy up what was spawned
	akTest.Step("removing what was spawned")
	RemoveSpawned(abel)
	RemoveSpawned(lead)
	RemoveSpawned(nell)
EndFunction

; ------------------------------------------------------------- scenario 3

Function RunDistance(TLM:SelfTest akTest)
	Actor player = Game.GetPlayer()
	TLM:MQ01Quest mq = TLM_MQ01 as TLM:MQ01Quest
	If !mq
		akTest.Fail("probe: TLM_MQ01 does not carry its quest script")
		Return
	EndIf
	If !FixtureMarkerBase
		akTest.Fail("probe: no marker base was found in Fallout4.esm when the plugin was built, so no marker can be placed")
		Return
	EndIf

	; ---- 1. A distance event between the player and a marker.
	akTest.Step("placing a marker at the player")
	ObjectReference marker = player.PlaceAtMe(FixtureMarkerBase)
	akTest.CheckTrue("probe: a marker can be placed at run time", marker != None)
	If !marker
		Return
	EndIf
	akTest.Note("probe: distance to the new marker = " + player.GetDistance(marker))
	distanceEvents = 0
	akTest.Step("registering for a distance event while the two are close")
	RegisterForDistanceGreaterThanEvent(player, marker, 500.0)
	Utility.Wait(1.0)
	akTest.CheckTrue("probe: no distance event while the two are close", distanceEvents == 0)
	akTest.Step("moving the marker 2000 units away")
	marker.MoveTo(player, 2000.0, 0.0, 0.0)
	akTest.Step("waiting for the distance event")
	WaitForDistanceEvents(1)
	akTest.Note("probe: distance to the marker after moving it = " + player.GetDistance(marker) + "; the event reported " + lastEventDistance)
	akTest.CheckTrue("probe: one distance event arrives once the two are far enough apart", distanceEvents == 1)

	; ---- 2. Registering when the two are already apart. The quest re-arms its
	; watch after a load, when the player may already be far away.
	distanceEvents = 0
	akTest.Step("registering for a distance event while the two are already apart")
	RegisterForDistanceGreaterThanEvent(player, marker, 500.0)
	WaitForDistanceEvents(1)
	akTest.CheckTrue("probe: registering while already apart sends the event", distanceEvents == 1)
	UnregisterForDistanceEvents(player, marker)

	; ---- 3. The quest's own watch: leaving a live ambush resolves it as "evaded".
	akTest.Reach(TLM_MQ01, 10)
	akTest.Reach(TLM_MQ01, 20)
	akTest.Step("placing the ambush centre at the player")
	ObjectReference center = player.PlaceAtMe(FixtureMarkerBase)
	If center
		mq.Alias_AmbushCenter.ForceRefTo(center)
		akTest.CheckTrue("probe: ForceRefTo fills the ambush centre alias", mq.Alias_AmbushCenter.GetReference() == center)
		akTest.Reach(TLM_MQ01, 30)
		Utility.Wait(1.0)
		akTest.CheckTrue("probe: the ambush stays live while the player is near its centre", mq.IsLive())
		akTest.Step("moving the ambush centre beyond the evade distance")
		center.MoveTo(player, mq.EvadeDistance + 1000.0, 0.0, 0.0)
		akTest.Step("waiting for the quest to notice that the player has left")
		WaitForStage(32)
		akTest.Note("probe: distance to the ambush centre = " + player.GetDistance(center) + "; the quest's evade distance is " + mq.EvadeDistance)
		akTest.CheckTrue("probe: leaving a live ambush sets stage 32", TLM_MQ01.GetStageDone(32))
		akTest.CheckTrue("probe: the outcome is 'evaded'", mq.Outcome() == 2)
	Else
		akTest.Fail("probe: a second marker could not be placed")
	EndIf

	akTest.Step("removing the markers")
	marker.Disable()
	marker.Delete()
	If center
		center.Disable()
		center.Delete()
	EndIf

	; ---- 4. Experiments, last because they may not come back. In the run of
	; 2026-11-12 the script stopped after placing a copy of this plugin's item
	; (which has no model) and never returned from what followed: registering a
	; distance event on it and moving it 3000 units. These steps repeat that,
	; apart and in order, to show which call it was.
	akTest.Step("EXPERIMENT: moving a placed item that has no model by 300 units", 20.0, true)
	ObjectReference placedItem = player.PlaceAtMe(TornTransitPass)
	If placedItem
		akTest.Note("probe: the item with no model was placed; Is3DLoaded = " + placedItem.Is3DLoaded())
		placedItem.MoveTo(player, 300.0, 0.0, 0.0)
		akTest.Note("probe: MoveTo by 300 units on the item with no model came back; distance now " + player.GetDistance(placedItem))
		akTest.Step("EXPERIMENT: a distance event on the item with no model, then moving it 3000 units", 20.0, true)
		distanceEvents = 0
		RegisterForDistanceGreaterThanEvent(player, placedItem, 400.0)
		placedItem.MoveTo(player, 3000.0, 0.0, 0.0)
		akTest.Note("probe: MoveTo by 3000 units on the item with no model came back")
		WaitForDistanceEvents(1)
		akTest.Note("probe: distance events for the item with no model: " + distanceEvents)
		UnregisterForDistanceEvents(player, placedItem)
		akTest.Step("EXPERIMENT: removing the item with no model", 20.0, true)
		placedItem.Disable()
		placedItem.Delete()
		akTest.Note("probe: the item with no model was removed")
	Else
		akTest.Note("probe: the item with no model could not be placed this time")
	EndIf
EndFunction

; ---------------------------------------------------------------- helpers

Actor Function SpawnActor(Actor akNear)
	ObjectReference placed = akNear.PlaceAtMe(FixtureActorBase)
	Return placed as Actor
EndFunction

Function RemoveSpawned(Actor akActor)
	If akActor
		akActor.Disable()
		akActor.Delete()
	EndIf
EndFunction

Function WaitForStage(int aiStage)
	{Waits until the main quest reports the stage, or eight seconds. A death is
	announced when the actor has finished dying, which takes a moment.}
	int tries = 0
	While !TLM_MQ01.GetStageDone(aiStage) && tries < 16
		Utility.Wait(0.5)
		tries += 1
	EndWhile
EndFunction

Function WaitForDistanceEvents(int aiCount)
	{Waits until that many distance events have arrived, or five seconds.}
	int tries = 0
	While distanceEvents < aiCount && tries < 10
		Utility.Wait(0.5)
		tries += 1
	EndWhile
EndFunction

Event OnTimer(int aiTimerID)
	If aiTimerID == TIMER_PROBE
		timerFired = true
	EndIf
EndEvent

Event OnDistanceGreaterThan(ObjectReference akObj1, ObjectReference akObj2, float afDistance)
	distanceEvents += 1
	lastEventDistance = afDistance
EndEvent
