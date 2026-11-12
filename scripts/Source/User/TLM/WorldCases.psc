Scriptname TLM:WorldCases extends Quest
{Development only, attached to TLM_Core next to TLM:Core, TLM:SelfTest and
TLM:FixtureProbe. Self-test scenarios 4 to 9: one case for each way the
caravan encounter can end. It must be removed before any release.

Each case plays TLM_MQ01 from its start to the hand-off with a caravan made at
run time: settlers spawned next to the player stand in for Nell Fenwick, Abel
Rudd and the Cutter lead, a fourth settler's pockets stand in for the wagon's
cargo, and two of the game's plain markers stand in for the caravan yard and
the centre of the ambush. They are forced into the quest's aliases, so the
quest's own scripts act on them.

What a case does NOT show: the player walking into a trigger, picking up the
dispatch or talking to anyone (those steps are stage numbers set from here),
AI behaviour, and anything about a placed, built world.

Every number in a CheckInt line is what the logic model predicts for the same
sequence of events; tools/logic_model/test_worldcases_expectations.py replays
the sequences and fails if a number here differs. So a failure in the game
means the game disagrees with the design, not that the number was typed wrong.

NOT YET COMPILED. NOT YET RUN IN THE GAME.}

Group Quests
	Quest Property TLM_MQ01 Auto Const Mandatory
EndGroup

Group Globals
	GlobalVariable Property TLM_G_CaravanMethod Auto Const Mandatory
	GlobalVariable Property TLM_G_CaravanAliveAtMercy Auto Const Mandatory
	GlobalVariable Property TLM_G_Rep_MercyCrossing Auto Const Mandatory
	GlobalVariable Property TLM_G_MQ01_Done Auto Const Mandatory
	GlobalVariable Property TLM_G_MQ01_DebriefVariant Auto Const Mandatory
	GlobalVariable Property TLM_G_MQ01_DebriefAnswer Auto Const Mandatory
	GlobalVariable Property TLM_Truth Auto Const Mandatory
	GlobalVariable Property TLM_Accountability Auto Const Mandatory
	GlobalVariable Property TLM_MutualTrust Auto Const Mandatory
EndGroup

Group Fixtures
	Form Property TornTransitPass Auto Const Mandatory
	{Any item of this plugin. Copies of it are the wagon's cargo.}
	Form Property FixtureActorBase Auto Const
	{The generic settler, looked up in Fallout4.esm when the plugin is built.}
	Form Property FixtureMarkerBase Auto Const
	{The game's plain marker (XMarker), looked up the same way.}
EndGroup

; How many items the stand-in wagon carries while its cargo is intact.
int CARGO_COUNT = 3 Const

TLM:SelfTest test
TLM:MQ01Quest mq
Actor player
Actor nell
Actor abel
Actor lead
Actor cargo
ObjectReference yard
ObjectReference center

; ------------------------------------------------------------- scenario 4

Function CaseEvaded(TLM:SelfTest akTest)
	{The player meets the ambush, does nothing, and goes on to town. In the
	logic model: start, take_dispatch, goto_ambush, evade_timer, goto_town,
	pritchard_handover, debrief_admit, pritchard_handoff.}
	If !BeginCase(akTest, "C4")
		Return
	EndIf
	test.Reach(TLM_MQ01, 10)
	If !MakeCaravan("C4")
		EndCase()
		Return
	EndIf
	test.CheckTrue("C4 the caravan and the Cutter lead stand in the quest's aliases", CaravanStands())
	test.Reach(TLM_MQ01, 20)
	test.Reach(TLM_MQ01, 30)
	test.CheckTrue("C4 the ambush is live", mq.IsLive())

	; ---- evade_timer: the watch runs out and there is no fight
	test.Note("C4: player in combat before the evade timer runs out: " + player.IsInCombat())
	test.Step("C4: the evade timer runs out (its handler is called directly; the 90 seconds are not waited for)")
	mq.OnTimer(1)
	AwaitStage(32)
	Utility.Wait(1.5)
	test.CheckTrue("C4 stage 32 set when the evade timer runs out", TLM_MQ01.GetStageDone(32))
	test.CheckInt("C4 outcome after evading", mq.Outcome(), 2)
	test.CheckInt("C4 method after evading", TLM_G_CaravanMethod.GetValueInt(), 0)
	test.CheckTrue("C4 the drover is dead once the Cutters have the wagon", abel.IsDead())
	test.CheckFalse("C4 the caravan master is dead", nell.IsDead())
	test.CheckFalse("C4 the drover's death at the Cutters' hands counts as a betrayal", TLM_MQ01.GetStageDone(35))
	test.CheckInt("C4 cargo left on the wagon after evading", cargo.GetItemCount(TornTransitPass), 0)

	; ---- goto_town
	test.Reach(TLM_MQ01, 40)
	test.CheckInt("C4 caravan alive at Mercy on reaching town", TLM_G_CaravanAliveAtMercy.GetValueInt(), 1)
	test.CheckTrue("C4 the caravan master is in the town alias", mq.Alias_CaravanMasterInTown.GetActorReference() == nell)
	test.CheckTrue("C4 the dead drover is not in the town alias", mq.Alias_CaravanDroverInTown.GetActorReference() == None)
	test.CheckTrue("C4 the Cutter lead is disabled once the player is in town", lead.IsDisabled())
	test.Note("C4: caravan master in the town alias, which is flagged Essential: IsEssential = " + nell.IsEssential())

	; ---- pritchard_handover
	test.Reach(TLM_MQ01, 50)
	test.CheckInt("C4 reputation after the hand-over", TLM_G_Rep_MercyCrossing.GetValueInt(), 1)
	test.CheckInt("C4 debrief variant", TLM_G_MQ01_DebriefVariant.GetValueInt(), 2)
	test.CheckInt("C4 caravan alive at Mercy after the hand-over", TLM_G_CaravanAliveAtMercy.GetValueInt(), 1)
	test.CheckInt("C4 mutual trust after the hand-over", TLM_MutualTrust.GetValueInt(), 0)

	; ---- debrief_admit
	test.Reach(TLM_MQ01, 51)
	test.CheckInt("C4 debrief answer after admitting", TLM_G_MQ01_DebriefAnswer.GetValueInt(), 1)
	test.CheckInt("C4 truth after admitting", TLM_Truth.GetValueInt(), 1)
	test.CheckInt("C4 accountability after admitting", TLM_Accountability.GetValueInt(), 1)
	; Only one answer is taken: the model offers none once one has been given.
	test.Reach(TLM_MQ01, 52)
	test.CheckInt("C4 debrief answer after a second answer", TLM_G_MQ01_DebriefAnswer.GetValueInt(), 1)
	test.CheckInt("C4 truth after a second answer", TLM_Truth.GetValueInt(), 1)

	; ---- A caravan hand in town cannot be killed (amendment A10: the town
	; alias is flagged Essential). Tried here, after the hand-over, where a
	; death could no longer change the outcome, so a surprise spoils one check
	; and not the rest of the case.
	test.Step("C4: trying to kill the caravan master in town, with the player as the killer")
	nell.Kill(player)
	Utility.Wait(2.5)
	test.CheckFalse("C4 the caravan master in the town alias can be killed", nell.IsDead())

	; ---- pritchard_handoff
	test.Reach(TLM_MQ01, 60)
	test.CheckTrue("C4 stage 100 set by the hand-off", TLM_MQ01.GetStageDone(100))
	test.CheckInt("C4 done", TLM_G_MQ01_Done.GetValueInt(), 1)
	test.CheckInt("C4 debrief answer after the hand-off", TLM_G_MQ01_DebriefAnswer.GetValueInt(), 1)
	test.CheckInt("C4 reputation after the hand-off", TLM_G_Rep_MercyCrossing.GetValueInt(), 1)
	EndCase()
EndFunction

; ------------------------------------------------------------- scenario 5

Function CaseFightSaved(TLM:SelfTest akTest)
	{A fight starts, the player kills the Cutter lead, and the caravan reaches
	town. In the logic model: start, take_dispatch, goto_ambush, attack_cutter,
	player_kills_lead, goto_town, pritchard_handover, pritchard_handoff.}
	If !BeginCase(akTest, "C5")
		Return
	EndIf
	test.Reach(TLM_MQ01, 10)
	If !MakeCaravan("C5")
		EndCase()
		Return
	EndIf
	test.CheckTrue("C5 the caravan and the Cutter lead stand in the quest's aliases", CaravanStands())
	test.Reach(TLM_MQ01, 20)

	; ---- goto_ambush, attack_cutter. In the world the sight trigger sets
	; stage 30 before anyone can fight. Here the fight comes first, to see
	; whether a Cutter who turns on the player makes the ambush live by himself
	; (the Cutter alias script's fallback). What happens is reported; if the
	; stage does not come, it is set from here and the case goes on.
	test.Step("C5: the Cutter lead starts a fight with the player")
	lead.StartCombat(player)
	AwaitStage(30)
	test.Note("C5: after StartCombat on the Cutter lead: stage 30 set = " + TLM_MQ01.GetStageDone(30) + ", lead in combat = " + lead.IsInCombat() + ", player in combat = " + player.IsInCombat())
	If !TLM_MQ01.GetStageDone(30)
		test.Reach(TLM_MQ01, 30)
	EndIf
	test.CheckTrue("C5 the ambush is live", mq.IsLive())

	; ---- player_kills_lead
	test.Step("C5: the Cutter lead dies, with the player as the killer")
	lead.Kill(player)
	AwaitStage(31)
	Utility.Wait(1.0)
	test.CheckTrue("C5 stage 31 set by the lead's death", TLM_MQ01.GetStageDone(31))
	test.CheckInt("C5 outcome after the lead's death", mq.Outcome(), 1)
	test.CheckInt("C5 method after the lead's death", TLM_G_CaravanMethod.GetValueInt(), 0)
	test.CheckFalse("C5 the caravan master is dead", nell.IsDead())
	test.CheckFalse("C5 the drover is dead", abel.IsDead())
	test.CheckInt("C5 cargo left on the wagon after the rescue", cargo.GetItemCount(TornTransitPass), 3)
	test.Note("C5: player in combat after the rescue: " + player.IsInCombat())

	; ---- goto_town
	test.Reach(TLM_MQ01, 40)
	test.CheckInt("C5 caravan alive at Mercy on reaching town", TLM_G_CaravanAliveAtMercy.GetValueInt(), 1)
	test.CheckTrue("C5 the caravan master is in the town alias", mq.Alias_CaravanMasterInTown.GetActorReference() == nell)
	test.CheckTrue("C5 the drover is in the town alias", mq.Alias_CaravanDroverInTown.GetActorReference() == abel)
	test.CheckTrue("C5 the dead Cutter lead is disabled once the player is in town", lead.IsDisabled())

	; ---- pritchard_handover
	test.Reach(TLM_MQ01, 50)
	test.CheckInt("C5 reputation after the hand-over", TLM_G_Rep_MercyCrossing.GetValueInt(), 2)
	test.CheckInt("C5 debrief variant", TLM_G_MQ01_DebriefVariant.GetValueInt(), 1)
	test.CheckInt("C5 mutual trust after the hand-over", TLM_MutualTrust.GetValueInt(), 1)
	test.CheckInt("C5 truth after the hand-over", TLM_Truth.GetValueInt(), 0)
	test.CheckInt("C5 accountability after the hand-over", TLM_Accountability.GetValueInt(), 0)
	; No answer is offered for this variant.
	test.Reach(TLM_MQ01, 51)
	test.CheckInt("C5 debrief answer after an answer not offered", TLM_G_MQ01_DebriefAnswer.GetValueInt(), 0)
	test.CheckInt("C5 truth after an answer not offered", TLM_Truth.GetValueInt(), 0)

	; ---- pritchard_handoff
	test.Reach(TLM_MQ01, 60)
	test.CheckTrue("C5 stage 100 set by the hand-off", TLM_MQ01.GetStageDone(100))
	test.CheckInt("C5 done", TLM_G_MQ01_Done.GetValueInt(), 1)
	test.CheckInt("C5 debrief answer after the hand-off", TLM_G_MQ01_DebriefAnswer.GetValueInt(), 9)
	test.CheckInt("C5 reputation after the hand-off", TLM_G_Rep_MercyCrossing.GetValueInt(), 2)
	test.CheckInt("C5 mutual trust after the hand-off", TLM_MutualTrust.GetValueInt(), 1)
	EndCase()
EndFunction

; ------------------------------------------------------------- scenario 6

Function CaseMissed(TLM:SelfTest akTest)
	{The player never meets the ambush and walks into town. In the logic
	model: start, take_dispatch, goto_town, pritchard_handover,
	pritchard_handoff.}
	If !BeginCase(akTest, "C6")
		Return
	EndIf
	test.Reach(TLM_MQ01, 10)
	If !MakeCaravan("C6")
		EndCase()
		Return
	EndIf
	test.CheckTrue("C6 the caravan and the Cutter lead stand in the quest's aliases", CaravanStands())
	test.Reach(TLM_MQ01, 20)
	test.CheckTrue("C6 the ambush is armed and has not been met", mq.IsArmed())

	; ---- goto_town: the town stage resolves the ambush nobody came to. The
	; quest kills the drover and, in the same breath, decides who goes to the
	; caravan yard, so a death that took a moment to count would show here.
	test.Reach(TLM_MQ01, 40)
	test.Note("C6: drover straight after the town stage: dead = " + abel.IsDead())
	test.CheckTrue("C6 stage 34 set on reaching town", TLM_MQ01.GetStageDone(34))
	test.CheckInt("C6 outcome on reaching town", mq.Outcome(), 4)
	test.CheckInt("C6 method on reaching town", TLM_G_CaravanMethod.GetValueInt(), 0)
	test.CheckInt("C6 caravan alive at Mercy on reaching town", TLM_G_CaravanAliveAtMercy.GetValueInt(), 1)
	test.CheckTrue("C6 the caravan master is in the town alias", mq.Alias_CaravanMasterInTown.GetActorReference() == nell)
	test.CheckTrue("C6 the dead drover is not in the town alias", mq.Alias_CaravanDroverInTown.GetActorReference() == None)
	test.CheckTrue("C6 the Cutter lead is disabled once the player is in town", lead.IsDisabled())
	Utility.Wait(1.5)
	test.CheckTrue("C6 the drover is dead once the Cutters have the wagon", abel.IsDead())
	test.CheckFalse("C6 the caravan master is dead", nell.IsDead())
	test.CheckFalse("C6 the drover's death at the Cutters' hands counts as a betrayal", TLM_MQ01.GetStageDone(35))
	test.CheckInt("C6 cargo left on the wagon", cargo.GetItemCount(TornTransitPass), 0)

	; ---- pritchard_handover
	test.Reach(TLM_MQ01, 50)
	test.CheckInt("C6 reputation after the hand-over", TLM_G_Rep_MercyCrossing.GetValueInt(), 1)
	test.CheckInt("C6 debrief variant", TLM_G_MQ01_DebriefVariant.GetValueInt(), 5)
	test.CheckInt("C6 mutual trust after the hand-over", TLM_MutualTrust.GetValueInt(), 0)
	; No answer is offered for this variant.
	test.Reach(TLM_MQ01, 51)
	test.CheckInt("C6 debrief answer after an answer not offered", TLM_G_MQ01_DebriefAnswer.GetValueInt(), 0)
	test.CheckInt("C6 truth after an answer not offered", TLM_Truth.GetValueInt(), 0)

	; ---- pritchard_handoff
	test.Reach(TLM_MQ01, 60)
	test.CheckTrue("C6 stage 100 set by the hand-off", TLM_MQ01.GetStageDone(100))
	test.CheckInt("C6 done", TLM_G_MQ01_Done.GetValueInt(), 1)
	test.CheckInt("C6 debrief answer after the hand-off", TLM_G_MQ01_DebriefAnswer.GetValueInt(), 9)
	test.CheckInt("C6 reputation after the hand-off", TLM_G_Rep_MercyCrossing.GetValueInt(), 1)
	EndCase()
EndFunction

; ------------------------------------------------------------- scenario 7

Function CaseRoadBetrayal(TLM:SelfTest akTest)
	{The player kills the caravan master at the ambush, and the Cutters finish
	the drover: nobody is left to tell. In the logic model: start,
	take_dispatch, goto_ambush, player_kills_nell, goto_town,
	pritchard_handover, pritchard_handoff.}
	If !BeginCase(akTest, "C7")
		Return
	EndIf
	test.Reach(TLM_MQ01, 10)
	If !MakeCaravan("C7")
		EndCase()
		Return
	EndIf
	test.CheckTrue("C7 the caravan and the Cutter lead stand in the quest's aliases", CaravanStands())
	test.Reach(TLM_MQ01, 20)
	test.Reach(TLM_MQ01, 30)
	test.CheckTrue("C7 the ambush is live", mq.IsLive())

	; ---- player_kills_nell
	test.Step("C7: the caravan master dies, with the player as the killer")
	nell.Kill(player)
	AwaitStage(35)
	Utility.Wait(1.5)
	test.CheckTrue("C7 stage 35 set by the caravan master's death", TLM_MQ01.GetStageDone(35))
	test.CheckInt("C7 outcome after the killing", mq.Outcome(), 3)
	test.CheckInt("C7 method after the killing", TLM_G_CaravanMethod.GetValueInt(), 2)
	test.CheckTrue("C7 the caravan master is dead", nell.IsDead())
	test.CheckTrue("C7 the drover is dead once the Cutters overrun the wagon", abel.IsDead())
	test.CheckInt("C7 cargo left on the wagon after the killing", cargo.GetItemCount(TornTransitPass), 0)

	; ---- goto_town
	test.Reach(TLM_MQ01, 40)
	test.CheckInt("C7 caravan alive at Mercy on reaching town", TLM_G_CaravanAliveAtMercy.GetValueInt(), 0)
	test.CheckTrue("C7 the dead caravan master is not in the town alias", mq.Alias_CaravanMasterInTown.GetActorReference() == None)
	test.CheckTrue("C7 the dead drover is not in the town alias", mq.Alias_CaravanDroverInTown.GetActorReference() == None)
	test.CheckTrue("C7 the Cutter lead is disabled once the player is in town", lead.IsDisabled())

	; ---- pritchard_handover
	test.Reach(TLM_MQ01, 50)
	test.CheckInt("C7 reputation after the hand-over", TLM_G_Rep_MercyCrossing.GetValueInt(), 1)
	test.CheckInt("C7 debrief variant", TLM_G_MQ01_DebriefVariant.GetValueInt(), 4)
	test.CheckInt("C7 caravan alive at Mercy after the hand-over", TLM_G_CaravanAliveAtMercy.GetValueInt(), 0)
	test.CheckInt("C7 mutual trust after the hand-over", TLM_MutualTrust.GetValueInt(), 0)
	; No answer is offered for this variant.
	test.Reach(TLM_MQ01, 53)
	test.CheckInt("C7 debrief answer after an answer not offered", TLM_G_MQ01_DebriefAnswer.GetValueInt(), 0)
	test.CheckInt("C7 truth after an answer not offered", TLM_Truth.GetValueInt(), 0)

	; ---- pritchard_handoff
	test.Reach(TLM_MQ01, 60)
	test.CheckTrue("C7 stage 100 set by the hand-off", TLM_MQ01.GetStageDone(100))
	test.CheckInt("C7 done", TLM_G_MQ01_Done.GetValueInt(), 1)
	test.CheckInt("C7 debrief answer after the hand-off", TLM_G_MQ01_DebriefAnswer.GetValueInt(), 9)
	test.CheckInt("C7 reputation after the hand-off", TLM_G_Rep_MercyCrossing.GetValueInt(), 1)
	EndCase()
EndFunction

; ------------------------------------------------------------- scenario 8

Function CaseMurderAfterSaving(TLM:SelfTest akTest)
	{The player saves the caravan and then kills the caravan master; the
	drover lives to tell. In the logic model: start, take_dispatch,
	goto_ambush, player_kills_lead, player_kills_nell, goto_town,
	pritchard_handover, debrief_confess, pritchard_handoff.}
	If !BeginCase(akTest, "C8")
		Return
	EndIf
	test.Reach(TLM_MQ01, 10)
	If !MakeCaravan("C8")
		EndCase()
		Return
	EndIf
	test.CheckTrue("C8 the caravan and the Cutter lead stand in the quest's aliases", CaravanStands())
	test.Reach(TLM_MQ01, 20)
	test.Reach(TLM_MQ01, 30)

	; ---- player_kills_lead
	test.Step("C8: the Cutter lead dies, with the player as the killer")
	lead.Kill(player)
	AwaitStage(31)
	Utility.Wait(1.0)
	test.CheckTrue("C8 stage 31 set by the lead's death", TLM_MQ01.GetStageDone(31))
	test.CheckInt("C8 outcome after the lead's death", mq.Outcome(), 1)

	; ---- player_kills_nell: after the rescue (amendment A3)
	test.Step("C8: the caravan master dies, with the player as the killer")
	nell.Kill(player)
	AwaitStage(35)
	Utility.Wait(1.5)
	test.CheckTrue("C8 stage 35 set by the caravan master's death", TLM_MQ01.GetStageDone(35))
	test.CheckInt("C8 outcome after the murder", mq.Outcome(), 3)
	test.CheckInt("C8 method after the murder", TLM_G_CaravanMethod.GetValueInt(), 2)
	test.CheckTrue("C8 the caravan master is dead", nell.IsDead())
	test.CheckFalse("C8 the drover is dead", abel.IsDead())
	test.CheckInt("C8 cargo left on the wagon after the murder", cargo.GetItemCount(TornTransitPass), 3)

	; ---- goto_town
	test.Reach(TLM_MQ01, 40)
	test.CheckInt("C8 caravan alive at Mercy on reaching town", TLM_G_CaravanAliveAtMercy.GetValueInt(), 0)
	test.CheckTrue("C8 the drover is in the town alias", mq.Alias_CaravanDroverInTown.GetActorReference() == abel)
	test.CheckTrue("C8 the dead caravan master is not in the town alias", mq.Alias_CaravanMasterInTown.GetActorReference() == None)

	; ---- pritchard_handover
	test.Reach(TLM_MQ01, 50)
	test.CheckInt("C8 reputation after the hand-over", TLM_G_Rep_MercyCrossing.GetValueInt(), 0)
	test.CheckInt("C8 debrief variant", TLM_G_MQ01_DebriefVariant.GetValueInt(), 3)
	test.CheckInt("C8 mutual trust after the hand-over", TLM_MutualTrust.GetValueInt(), 0)

	; ---- debrief_confess
	test.Reach(TLM_MQ01, 53)
	test.CheckInt("C8 debrief answer after confessing", TLM_G_MQ01_DebriefAnswer.GetValueInt(), 3)
	test.CheckInt("C8 truth after confessing", TLM_Truth.GetValueInt(), 1)
	test.CheckInt("C8 accountability after confessing", TLM_Accountability.GetValueInt(), 1)

	; ---- pritchard_handoff
	test.Reach(TLM_MQ01, 60)
	test.CheckTrue("C8 stage 100 set by the hand-off", TLM_MQ01.GetStageDone(100))
	test.CheckInt("C8 done", TLM_G_MQ01_Done.GetValueInt(), 1)
	test.CheckInt("C8 debrief answer after the hand-off", TLM_G_MQ01_DebriefAnswer.GetValueInt(), 3)
	test.CheckInt("C8 reputation after the hand-off", TLM_G_Rep_MercyCrossing.GetValueInt(), 0)
	EndCase()
EndFunction

; ------------------------------------------------------------- scenario 9

Function CaseDeal(TLM:SelfTest akTest)
	{The player takes the Cutter lead's offer. In the logic model: start,
	take_dispatch, goto_ambush, dunmore_deal, goto_town, pritchard_handover,
	debrief_blame, pritchard_handoff.}
	If !BeginCase(akTest, "C9")
		Return
	EndIf
	test.Reach(TLM_MQ01, 10)
	If !MakeCaravan("C9")
		EndCase()
		Return
	EndIf
	test.CheckTrue("C9 the caravan and the Cutter lead stand in the quest's aliases", CaravanStands())
	test.Reach(TLM_MQ01, 20)
	test.Reach(TLM_MQ01, 30)
	test.CheckTrue("C9 the ambush is live", mq.IsLive())

	; ---- dunmore_deal: in the world the talk with the Cutter lead sets stage 33
	test.Reach(TLM_MQ01, 33)
	Utility.Wait(1.5)
	test.CheckInt("C9 outcome after the deal", mq.Outcome(), 3)
	test.CheckInt("C9 method after the deal", TLM_G_CaravanMethod.GetValueInt(), 1)
	test.CheckTrue("C9 the drover is dead after the deal", abel.IsDead())
	test.CheckFalse("C9 the caravan master is dead", nell.IsDead())
	test.CheckFalse("C9 the deal counts as a killing by the player", TLM_MQ01.GetStageDone(35))
	test.CheckInt("C9 cargo left on the wagon after the deal", cargo.GetItemCount(TornTransitPass), 0)

	; ---- goto_town
	test.Reach(TLM_MQ01, 40)
	test.CheckInt("C9 caravan alive at Mercy on reaching town", TLM_G_CaravanAliveAtMercy.GetValueInt(), 1)
	test.CheckTrue("C9 the caravan master is in the town alias", mq.Alias_CaravanMasterInTown.GetActorReference() == nell)
	test.CheckTrue("C9 the dead drover is not in the town alias", mq.Alias_CaravanDroverInTown.GetActorReference() == None)

	; ---- pritchard_handover
	test.Reach(TLM_MQ01, 50)
	test.CheckInt("C9 reputation after the hand-over", TLM_G_Rep_MercyCrossing.GetValueInt(), 0)
	test.CheckInt("C9 debrief variant", TLM_G_MQ01_DebriefVariant.GetValueInt(), 3)
	test.CheckInt("C9 mutual trust after the hand-over", TLM_MutualTrust.GetValueInt(), 0)

	; ---- debrief_blame
	test.Reach(TLM_MQ01, 54)
	test.CheckInt("C9 debrief answer after blaming the Cutters", TLM_G_MQ01_DebriefAnswer.GetValueInt(), 4)
	test.CheckInt("C9 truth after blaming the Cutters", TLM_Truth.GetValueInt(), -1)
	test.CheckInt("C9 accountability after blaming the Cutters", TLM_Accountability.GetValueInt(), 0)

	; ---- pritchard_handoff
	test.Reach(TLM_MQ01, 60)
	test.CheckTrue("C9 stage 100 set by the hand-off", TLM_MQ01.GetStageDone(100))
	test.CheckInt("C9 done", TLM_G_MQ01_Done.GetValueInt(), 1)
	test.CheckInt("C9 debrief answer after the hand-off", TLM_G_MQ01_DebriefAnswer.GetValueInt(), 4)
	test.CheckInt("C9 reputation after the hand-off", TLM_G_Rep_MercyCrossing.GetValueInt(), 0)
	EndCase()
EndFunction

; ---------------------------------------------------------------- helpers

bool Function BeginCase(TLM:SelfTest akTest, string asName)
	test = akTest
	player = Game.GetPlayer()
	mq = TLM_MQ01 as TLM:MQ01Quest
	If !mq
		test.Fail(asName + ": TLM_MQ01 does not carry its quest script")
		Return false
	EndIf
	If !FixtureActorBase || !FixtureMarkerBase
		test.Fail(asName + ": the settler or the marker was not found in Fallout4.esm when the plugin was built, so the caravan cannot be made")
		Return false
	EndIf
	; Nobody is at the controls, and the stand-ins carry guns.
	Debug.SetGodMode(true)
	Return true
EndFunction

bool Function MakeCaravan(string asName)
	{Stands the caravan up around the player and puts it into the main
	quest's aliases. The quest has to be running: call it after stage 10.}
	test.Step(asName + ": making the caravan, the Cutter lead and the markers")
	nell = SpawnFixture()
	abel = SpawnFixture()
	lead = SpawnFixture()
	cargo = SpawnFixture()
	yard = player.PlaceAtMe(FixtureMarkerBase)
	center = player.PlaceAtMe(FixtureMarkerBase)
	If !nell || !abel || !lead || !cargo || !yard || !center
		test.Fail(asName + ": a stand-in could not be made")
		Return false
	EndIf
	test.Step(asName + ": putting the stand-ins into the quest's aliases")
	mq.Alias_CaravanMaster.ForceRefTo(nell)
	mq.Alias_CaravanDrover.ForceRefTo(abel)
	mq.Alias_CutterLead.ForceRefTo(lead)
	mq.Alias_Wagon.ForceRefTo(cargo)
	mq.Alias_CaravanYard.ForceRefTo(yard)
	mq.Alias_AmbushCenter.ForceRefTo(center)
	cargo.AddItem(TornTransitPass, CARGO_COUNT, true)
	Utility.Wait(1.0)
	Return true
EndFunction

bool Function CaravanStands()
	If mq.Alias_CaravanMaster.GetActorReference() != nell || nell.IsDead()
		Return false
	EndIf
	If mq.Alias_CaravanDrover.GetActorReference() != abel || abel.IsDead()
		Return false
	EndIf
	If mq.Alias_CutterLead.GetActorReference() != lead || lead.IsDead()
		Return false
	EndIf
	If mq.Alias_Wagon.GetReference() != cargo
		Return false
	EndIf
	If mq.Alias_CaravanYard.GetReference() != yard
		Return false
	EndIf
	If mq.Alias_AmbushCenter.GetReference() != center
		Return false
	EndIf
	Return cargo.GetItemCount(TornTransitPass) == CARGO_COUNT
EndFunction

Function EndCase()
	test.Step("removing the stand-ins")
	RemoveFixture(nell)
	RemoveFixture(abel)
	RemoveFixture(lead)
	RemoveFixture(cargo)
	RemoveFixture(yard)
	RemoveFixture(center)
	Debug.SetGodMode(false)
EndFunction

Actor Function SpawnFixture()
	ObjectReference placed = player.PlaceAtMe(FixtureActorBase)
	Return placed as Actor
EndFunction

Function RemoveFixture(ObjectReference akRef)
	If akRef
		akRef.Disable()
		akRef.Delete()
	EndIf
EndFunction

Function AwaitStage(int aiStage)
	{Waits until the main quest reports the stage, or eight seconds. A death is
	announced when the actor has finished dying, which takes a moment.}
	int tries = 0
	While !TLM_MQ01.GetStageDone(aiStage) && tries < 16
		Utility.Wait(0.5)
		tries += 1
	EndWhile
EndFunction
