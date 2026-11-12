Scriptname TLM:FixtureProbe extends Quest
{Development only, attached to TLM_Core next to TLM:Core and TLM:SelfTest.
Self-test scenario 2. It must be removed before any release.

It finds out, in the game, whether the pieces a fuller test of the quest
needs can be made at run time, so that the test matrix does not have to wait
for a hand-built test cell: an actor spawned from a base form, forced into a
quest alias, killed, and noticed by the alias's script; a timer on a quest
script; a distance event.

Most of what it writes is reported, not scored: a line that begins INFO is a
fact about the game, not about the design. The scored checks are the ones the
quest's design already relies on.

NOT YET COMPILED. NOT YET RUN IN THE GAME.}

Quest Property TLM_MQ01 Auto Const Mandatory
Form Property TornTransitPass Auto Const Mandatory
{Any item of this plugin. One is placed in the world as a stand-in for a marker.}
Form Property FixtureActorBase Auto Const
{An actor base from the game to spawn: the generic settler, looked up in
Fallout4.esm when the plugin is built. None if it was not found.}

int TIMER_PROBE = 7 Const
bool timerFired = false
bool distanceFired = false

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
	Actor abel = SpawnActor(player)
	akTest.CheckTrue("probe: an actor can be spawned at run time", abel != None)
	If !abel
		Return
	EndIf
	mq.Alias_CaravanDrover.ForceRefTo(abel)
	akTest.CheckTrue("probe: ForceRefTo fills the drover alias", mq.Alias_CaravanDrover.GetActorReference() == abel)
	akTest.CheckTrue("probe: the quest script sees the drover alive", mq.IsAliveAlias(mq.Alias_CaravanDrover))
	akTest.Note("probe: drover in a Protected alias: IsEssential = " + abel.IsEssential())
	abel.Kill()
	Utility.Wait(1.5)
	akTest.Note("probe: drover after Kill() with no killer, protection not cleared: dead = " + abel.IsDead())
	If !abel.IsDead()
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
	Actor lead = SpawnActor(player)
	If lead
		mq.Alias_CutterLead.ForceRefTo(lead)
		akTest.CheckTrue("probe: ForceRefTo fills the Cutter lead alias", mq.Alias_CutterLead.GetActorReference() == lead)
		lead.Kill(player)
		WaitForStage(31)
		akTest.Note("probe: Cutter lead after Kill(player): dead = " + lead.IsDead())
		akTest.CheckTrue("probe: the Cutter alias script heard the death and set stage 31", TLM_MQ01.GetStageDone(31))
		akTest.CheckTrue("probe: the outcome is 'saved'", mq.Outcome() == 1)
	Else
		akTest.Fail("probe: a second actor could not be spawned")
	EndIf

	; ---- 3. The caravan master killed by the player after the rescue: the
	; hand alias's script should hear it, and betrayal should override "saved".
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

	; ---- 5. A distance event, as the quest's evade watch uses.
	ObjectReference marker = player.PlaceAtMe(TornTransitPass)
	akTest.CheckTrue("probe: an item can be placed in the world as a marker", marker != None)
	If marker
		distanceFired = false
		RegisterForDistanceGreaterThanEvent(player, marker, 400.0)
		marker.MoveTo(player, 3000.0, 0.0, 0.0)
		Utility.Wait(3.0)
		akTest.Note("probe: distance to the marker after moving it away = " + player.GetDistance(marker))
		akTest.CheckTrue("probe: a distance event fires when the two references are far apart", distanceFired)
		UnregisterForDistanceEvents(player, marker)
		marker.Disable()
		marker.Delete()
	EndIf

	; ---- tidy up what was spawned
	RemoveSpawned(abel)
	RemoveSpawned(lead)
	RemoveSpawned(nell)
EndFunction

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

Event OnTimer(int aiTimerID)
	If aiTimerID == TIMER_PROBE
		timerFired = true
	EndIf
EndEvent

Event OnDistanceGreaterThan(ObjectReference akObj1, ObjectReference akObj2, float afDistance)
	distanceFired = true
EndEvent
