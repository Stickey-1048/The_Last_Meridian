"""Do the Night Mail's tests notice? (NIGHT-MAIL-STORY-001)

Each guard the scripts keep is taken out of a copy of them, one at a time
(or, where the greybox and the rules each keep the same guard, both at
once), and a test that is there to protect it is run against the copy, as it
is written. It must fail. A guard whose removal no test notices is a guard
nobody would miss.

These are trials of the tests on the stand-in engine. NONE OF THIS HAS BEEN
SEEN IN THE GAME. Not a compile and not a game test.
"""
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import night_mail_player
from test_act1 import need_act1_build

WALK, RULES = "NightMailWalk.psc", "MQ02AQuest.psc"

# (what is taken out, [(file, old, new) or (file, old, new, how many times it is there), ...], the test that must then fail)
TRIALS = [
    ("an arrival at the yard taken on trust",
     [(WALK, "	If !Arrived(akRiver, yardGate)\n", "	If false\n"),
      (RULES, "	If !SeenAt(Game.GetPlayer(), akGate)\n", "	If false\n")],
     "test_night_mail.GettingThere.test_requested_transit_is_not_arrival"),
    ("a journey to the Cut recorded unseen",
     [(WALK, "		If Arrived(akRiver, cut)\n			zone = NW_ZONE_CUT\n			If SeenOn(lanterns)\n", "		If true\n			zone = NW_ZONE_CUT\n			If true\n"),
      (RULES, "	If !SeenAt(Game.GetPlayer(), akCutMarker) || !IsOn(akLanterns)\n", "	If false\n")],
     "test_night_mail_scenes.TheDeparture.test_not_arrived_then_arrived"),
    ("the lanterns not looked at",
     [(WALK, "			If SeenOn(lanterns)\n", "			If true\n"),
      (RULES, "	If !SeenAt(Game.GetPlayer(), akCutMarker) || !IsOn(akLanterns)\n", "	If !SeenAt(Game.GetPlayer(), akCutMarker)\n")],
     "test_night_mail_scenes.TheDeparture.test_the_lanterns_not_seen"),
    ("the way back along the line shut by a scene that cannot be shown",
     [(WALK, "	ElseIf aiWho == NW_BACK\n		; The way back along the line is never shut", "	ElseIf false\n		; The way back along the line is never shut"),
      (WALK, "	ElseIf aiWho == NW_DOLE\n		TalkDole(akRiver)\n	EndIf", "	ElseIf aiWho == NW_DOLE\n		TalkDole(akRiver)\n	ElseIf aiWho == NW_BACK\n		BackToYard(akRiver)\n	EndIf")],
     "test_night_mail_scenes.TheDeparture.test_a_scene_that_cannot_be_shown_keeps_nobody_in_the_cut"),
    ("a run recorded with its cargo unseen",
     [(WALK, "			If SeenOn(delivered) && SeenOff(aboard) && SeenOn(damaged)\n", "			If true\n"),
      (RULES, "	If !SeenAt(Game.GetPlayer(), akPlatform) || !IsOn(akDelivered) || !IsOff(akAboard) || !IsOn(akDamaged)\n", "	If false\n")],
     "test_night_mail_scenes.TheRun.test_the_cargo_not_seen_delivered"),
    ("a run recorded with the player where they were",
     [(WALK, "		If Arrived(akRiver, platform)\n			zone = NW_ZONE_PLATFORM\n			If SeenOn(delivered) && SeenOff(aboard) && SeenOn(damaged)\n",
       "		If true\n			zone = NW_ZONE_PLATFORM\n			If SeenOn(delivered) && SeenOff(aboard) && SeenOn(damaged)\n"),
      (RULES, "	If !SeenAt(Game.GetPlayer(), akPlatform) || !IsOn(akDelivered) || !IsOff(akAboard) || !IsOn(akDamaged)\n", "	If false\n")],
     "test_night_mail_scenes.TheRun.test_the_player_not_moved"),
    ("the pieces left ahead of the record after a run not seen",
     [(WALK, "	Refresh()\n	If !done\n		Debug.Trace(\"TLM_NM: the run was not seen finished", "	If !done\n		Debug.Trace(\"TLM_NM: the run was not seen finished")],
     "test_night_mail_scenes.TheRun.test_the_cargo_not_seen_delivered"),
    ("a scene begun and not seen is not tried again",
     [(WALK, "	ElseIf Resume(akRiver)\n", "	ElseIf false\n")],
     "test_night_mail_scenes.TheRun.test_the_player_not_moved"),
    ("another course begun beside one that is pending",
     [(WALK, "	ElseIf Resume(akRiver)\n", "	ElseIf false\n"),
      (RULES, "	If !RoadOpen() || !AtTheCut() || ScenePending != NM_SCENE_NONE || Mail() != NM_MAIL_ABOARD\n", "	If !RoadOpen() || !AtTheCut() || Mail() != NM_MAIL_ABOARD\n"),
      (RULES, "	Claim = NM_BACKED\n", "	Claim = NM_BACKED\n	TLM_G_MQ02A_LineClosed.SetValueInt(1)\n"),
      (RULES, "	If TrainOffered() != NM_AT_OPEN\n		Return false\n	EndIf\n	bool drives = CanSpeak(Alias_Billie)\n	; No call into the game between this test and the claim.\n	If Claim != NM_NONE || ScenePending != NM_SCENE_NONE\n		Return false\n	EndIf\n	Claim = NM_BACKED",
       "	bool drives = CanSpeak(Alias_Billie)\n	Claim = NM_BACKED")],
     "test_night_mail_scenes.TheRun.test_the_player_not_moved"),
    ("Dole's death taken for the outcome whatever was begun",
     [(RULES, "	If here && Claim == NM_NONE && course == NM_NONE\n", "	If here\n")],
     "test_night_mail_scenes.TheRun.test_dole_killed_while_the_run_is_pending_is_not_the_outcome"),
    ("Billie's question answered after her",
     [(WALK, "	If abHers && !akRiver.BillieCanSpeak()\n", "	If false\n")],
     "test_night_mail_scenes.TheRun.test_her_question_is_answered_to_her"),
    ("a run begun by a box nobody answered",
     [(WALK, "	If ShowBox(AskRunScene) != 0\n", "	If ShowBox(AskRunScene) == 1\n")],
     "test_night_mail_scenes.TheRun.test_not_confirmed_or_stale_begins_nothing"),
    ("a line of Billie's from a dead woman",
     [(WALK, "	If akRiver.DidBillieDrive() && !ranSaid && PlaceBillie(akRiver)\n", "	If akRiver.DidBillieDrive() && !ranSaid\n")],
     "test_night_mail_scenes.TheRun.test_billie_dead_before_it_is_seen_says_nothing"),
    ("nobody's dead, said over a body",
     [(WALK, "	If akRiver.DidBillieDrive() && !akRiver.AnybodyDead() && !backedSaid && PlaceBillie(akRiver)\n", "	If akRiver.DidBillieDrive() && !backedSaid && PlaceBillie(akRiver)\n"),
      (WALK, "	ElseIf course == NM_BACKED && akRiver.DidBillieDrive() && !backedSaid && !akRiver.AnybodyDead()\n", "	ElseIf course == NM_BACKED && akRiver.DidBillieDrive() && !backedSaid\n")],
     "test_night_mail_scenes.TheReverse.test_nobodys_dead_is_not_said_over_a_body"),
    ("a reverse recorded with its cargo unseen",
     [(WALK, "	Return SeenOn(retained) && SeenOff(aboard)\n", "	Return true\n"),
      (RULES, "	If !SeenAt(Game.GetPlayer(), akYard) || !IsOn(akRetained) || !IsOff(akAboard)\n		Debug.Trace(\"TLM_MQ02A: the reverse is not recorded", "	If false\n		Debug.Trace(\"TLM_MQ02A: the reverse is not recorded")],
     "test_night_mail_scenes.TheReverse.test_the_cargo_not_seen_locked_up"),
    ("a delivery after the defeat recorded unseen",
     [(WALK, "			If SeenOn(delivered) && SeenOff(aboard) && SeenOn(sound)\n", "			If true\n"),
      (RULES, "	If !SeenAt(Game.GetPlayer(), akPlatform) || !IsOn(akDelivered) || !IsOff(akAboard) || !IsOn(akSound)\n", "	If false\n")],
     "test_night_mail_scenes.AfterTheDefeat.test_forward_not_seen_then_seen"),
    ("a road complete with a scene half done",
     [(RULES, "	Return Outcome() != NM_NONE && ScenePending == NM_SCENE_NONE\n", "	Return Outcome() != NM_NONE\n")],
     "test_night_mail_scenes.AfterTheDefeat.test_forward_not_seen_then_seen"),
    ("the defeat recorded with the Black Rail still there",
     [(RULES, "	Return !who.IsInCombat() && StandsAt(who, akRetreat)\n", "	Return true\n")],
     "test_night_mail_scenes.AfterTheDefeat.test_the_black_rail_not_seen_gone"),
    ("a death nobody heard of is never found",
     [(WALK, "		If akRiver.DoleIsDead()\n			akRiver.DoleDied(false)\n", "		If false\n			akRiver.DoleDied(false)\n")],
     "test_night_mail_scenes.AfterTheDefeat.test_a_death_nobody_heard_of_is_found_at_the_next_control"),
    ("killing Dole delivers the medicine",
     [(RULES, "	TLM_G_MQ02A_Outcome.SetValueInt(NM_DEFEAT)\n", "	TLM_G_MQ02A_Outcome.SetValueInt(NM_DEFEAT)\n	TLM_G_MQ02A_Mail.SetValueInt(NM_MAIL_DELIVERED)\n	TLM_G_MQ02A_MailThrough.SetValueInt(1)\n")],
     "test_night_mail.TheFourCourses.test_killing_dole_is_not_delivering_medicine"),
    ("a sale recorded with its cargo unseen",
     [(WALK, "		If SeenOn(seized) && SeenOff(aboard)\n", "		If true\n"),
      (RULES, "	If !IsOn(akSeized) || !IsOff(akAboard)\n", "	If false\n")],
     "test_night_mail_scenes.TheSale.test_paid_and_the_cargo_not_seen_taken"),
    ("a sale recorded with Billie not seen safe",
     [(RULES, "			If billie.IsDisabled() || billie.IsInCombat() || !StandsAt(billie, akWalk)\n", "			If false\n")],
     "test_night_mail_scenes.TheSale.test_billie_not_seen_safe"),
    ("the share asked for again after it was not given",
     [(RULES, "	Return !SharePaid && !SharePending && Caps != None\n", "	Return !SharePaid && Caps != None\n"),
      (RULES, "	If Claim != NM_NONE || ScenePending != NM_SCENE_NONE || SharePending || SharePaid\n", "	If Claim != NM_NONE || ScenePending != NM_SCENE_NONE || SharePaid\n")],
     "test_night_mail_scenes.TheSale.test_caps_the_game_does_not_give"),
    ("a sale recorded though the caps never came",
     [(RULES, "	If player.GetItemCount(Caps) < before + NM_SHARE_CAPS\n		; Fails closed", "	If false\n		; Fails closed")],
     "test_night_mail_scenes.TheSale.test_caps_the_game_does_not_give"),
    ("Dole's offer answered after him",
     [(WALK, "	If !StillHis(akRiver, aiMark)\n		Return\n	EndIf\n	If pick == 0\n		Sell(akRiver)\n", "	If pick == 0\n		Sell(akRiver)\n"),
      (RULES, "	If TrainOffered() != NM_AT_OPEN || !CanSpeak(Alias_Dole)\n", "	If TrainOffered() != NM_AT_OPEN && Claim != NM_DEFEAT\n")],
     "test_night_mail_scenes.TheSale.test_the_offer_is_answered_to_dole"),
    ("walking away from the parley is a fight",
     [(WALK, "	; 3, \"(Go back to the footplate)\": nothing. Walking away from the parley starts no fight.\n", "	If pick == 3\n		Rouse()\n	EndIf\n")],
     "test_night_mail_scenes.Dole.test_walking_away_from_the_parley_starts_no_fight"),
    ("refusing the job is a fight",
     [(WALK, "	; 3, \"Not tonight.\", and anything else: nothing. Refusing starts no fight and loses nothing.\n", "	If pick == 3\n		Alias_Lockridge.GetActorReference().StartCombat(Game.GetPlayer())\n	EndIf\n")],
     "test_night_mail.RefusalAndLeaving.test_refusing_the_job_harms_nobody_and_leaves_the_road_open"),
    ("a name he did not finish saying",
     [(WALK, "	If pick < 0 || pick > 2 || !StillHis(akRiver, aiMark)\n", "	If false\n")],
     "test_night_mail_scenes.Dole.test_what_he_did_not_finish_saying_teaches_nothing"),
    ("silver he did not finish saying",
     [(WALK, "	If pick < 0 || pick > 1 || !StillHis(akRiver, aiMark)\n", "	If false\n")],
     "test_night_mail_scenes.Dole.test_what_he_did_not_finish_saying_teaches_nothing"),
    ("a fight from an answer of his nobody heard out",
     [(WALK, "	If !Said(SayDoleFace)\n		Return\n	EndIf\n", "	Said(SayDoleFace)\n")],
     "test_night_mail_scenes.Dole.test_his_face_unanswered_is_no_fight"),
    ("the Black Rail set on the player again by every combat event",
     [(WALK, "	If who && !who.IsDead() && !who.IsDisabled() && !who.IsInCombat()\n", "	If who && !who.IsDead() && !who.IsDisabled()\n")],
     "test_night_mail_scenes.Dole.test_attacking_him_unprovoked_brings_the_black_rail_once"),
    ("the Black Rail fighting on for a dead man",
     [(WALK, "		If river.DoleIsDead()\n			Return\n		EndIf\n", "")],
     "test_night_mail_scenes.Dole.test_after_he_is_dead_the_black_rail_do_not_fight_on"),
    ("the book taken for shown because a name was heard",
     [(RULES, "	If !RoadOpen() || HymnalShown || !HoldsHymnal() || !CanSpeak(Alias_Lockridge) || !LockridgeDispatches()\n", "	If !RoadOpen() || HymnalShown || !KnowsName() || !CanSpeak(Alias_Lockridge) || !LockridgeDispatches()\n")],
     "test_night_mail.Evidence.test_oral_identity_is_not_holding_or_reading_a_book"),
    ("a hymnal asked for twice",
     [(RULES, "	If HymnalGiven || HymnalPending\n", "	If HymnalGiven\n")],
     "test_night_mail.Evidence.test_a_hymnal_the_game_does_not_give_is_asked_for_once"),
    ("a countersigning recorded unseen",
     [(WALK, "	If SeenOn(signed) && SeenOff(stamped) && SeenOn(held)\n", "	If true\n"),
      (RULES, "	If !IsOn(akSigned) || !IsOff(akStamped) || !IsOn(akHeld) || !CanSpeak(Alias_Lockridge) || !PlayerIsAlive()\n", "	If !CanSpeak(Alias_Lockridge) || !PlayerIsAlive()\n")],
     "test_night_mail_scenes.TheStampScenes.test_the_countersigning_not_seen_then_seen"),
    ("a countersigning by a dead woman",
     [(WALK, "	If akRiver.AbandonCountersign()\n", "	If false\n"),
      (WALK, "	If !akRiver.PlayerIsAlive() || !akRiver.LockridgeCanSpeak()\n		Refresh()\n		Return\n	EndIf\n", ""),
      (RULES, "	If !IsOn(akSigned) || !IsOff(akStamped) || !IsOn(akHeld) || !CanSpeak(Alias_Lockridge) || !PlayerIsAlive()\n", "	If !IsOn(akSigned) || !IsOff(akStamped) || !IsOn(akHeld)\n")],
     "test_night_mail_scenes.TheStampScenes.test_a_dead_woman_countersigns_nothing"),
    ("a countersigning nobody can finish left pending for ever",
     [(WALK, "	If akRiver.AbandonCountersign()\n", "	If false\n")],
     "test_night_mail_scenes.TheStampScenes.test_a_dead_woman_countersigns_nothing"),
    ("Lockridge's question about the stamp answered after her",
     [(WALK, "	If hers && !akRiver.LockridgeCanSpeak()\n", "	If false\n"),
      (RULES, "	If !RoadOpen() || !StampUndecided() || !CanSpeak(Alias_Lockridge) || !LockridgeDispatches()\n", "	If !RoadOpen() || !StampUndecided()\n", 2)],
     "test_night_mail_scenes.TheStampScenes.test_her_question_is_answered_to_her"),
    ("the stamp recorded taken with the drawer still showing it",
     [(WALK, "	If SeenOff(inDrawer) && akRiver.ConfirmStampTaken(inDrawer)\n", "	If akRiver.ConfirmStampTaken(inDrawer)\n"),
      (RULES, "	If !IsOff(akInDrawer)\n		Return false\n	EndIf\n	bool watched", "	bool watched")],
     "test_night_mail_scenes.TheStampScenes.test_taken_and_the_drawer_not_seen_empty"),
    ("the stamp asked for twice",
     [(RULES, "	If StampAsked\n		If !holds\n			Return false\n		EndIf\n		StampPending = true\n		StampGiven = true\n		Return true\n	EndIf\n", "")],
     "test_night_mail_scenes.TheStampScenes.test_a_stamp_not_given_leaves_her_other_answers_open"),
    ("a stamp not given shuts her other answers",
     [(RULES, "	StampPending = false\n	Debug.Trace(\"TLM_MQ02A: FAIL CLOSED: the stamp was asked for once", "	Debug.Trace(\"TLM_MQ02A: FAIL CLOSED: the stamp was asked for once")],
     "test_night_mail_scenes.TheStampScenes.test_a_stamp_not_given_leaves_her_other_answers_open"),
    ("the stamp kept in use while it is in the player's pocket",
     [(RULES, "	If !IsOn(akInDrawer) || HoldsStamp()\n		Return false\n	EndIf\n	; No call into the game between this test and the claim.\n	If StampPending || YardPending != NM_YARD_NONE\n		Return false\n	EndIf\n	TLM_G_MQ02A_Stamp.SetValueInt(NM_STAMP_KEPT)",
       "	If !IsOn(akInDrawer)\n		Return false\n	EndIf\n	If StampPending || YardPending != NM_YARD_NONE\n		Return false\n	EndIf\n	TLM_G_MQ02A_Stamp.SetValueInt(NM_STAMP_KEPT)")],
     "test_night_mail_scenes.TheStampScenes.test_a_stamp_that_arrives_late_is_the_taking_when_next_chosen"),
    ("a stamp taken is a stamp delivered",
     [(RULES, "	TLM_G_MQ02A_Stamp.SetValueInt(NM_STAMP_TAKEN)\n", "	TLM_G_MQ02A_Stamp.SetValueInt(NM_STAMP_TAKEN)\n	TLM_G_MQ02A_StampDelivered.SetValueInt(1)\n")],
     "test_night_mail.TheStamp.test_taken_is_not_delivered"),
    ("a stamp handed over that the player does not hold",
     [(RULES, "	Return StampDecision() == NM_STAMP_TAKEN && !IsStampDelivered() && HoldsStamp() && SheriffCanReceive()\n", "	Return StampDecision() == NM_STAMP_TAKEN && !IsStampDelivered() && SheriffCanReceive()\n")],
     "test_night_mail_scenes.TheStampScenes.test_dropped_and_picked_up_it_is_still_one_decision_and_custody_is_what_is_held"),
    ("a handover recorded unseen",
     [(RULES, "	If player.GetItemCount(StampItem) >= mine || sheriff.GetItemCount(StampItem) <= his\n		Debug.Trace", "	If false\n		Debug.Trace")],
     "test_night_mail_scenes.TheHandover.test_not_seen_with_pritchard_is_not_delivered"),
    ("a handover that arrived late never seen",
     [(WALK, "	river.HandoverSeen()\n", "")],
     "test_night_mail_scenes.TheHandover.test_a_handover_that_arrived_late_is_seen_at_the_next_conversation"),
    ("a stamp handed to a dead man",
     [(WALK, "		If !StillHere(akSheriff, player) || river.StampMark() != mark || !river.CanHandOver()\n", "		If false\n"),
      (RULES, "	If !CanHandOver() || !PlayerIsAlive()\n", "	If !PlayerIsAlive()\n")],
     "test_night_mail_scenes.TheHandover.test_a_dead_pritchard_receives_nothing"),
    ("a handover by a box nobody answered",
     [(WALK, "		ElseIf hand != 1\n			Return NW_REPORT_CLOSED\n", "		ElseIf hand != 1\n			river.HandOver()\n			Return NW_REPORT_CLOSED\n")],
     "test_night_mail_scenes.TheHandover.test_not_answered_or_stale_hands_nothing_over"),
    ("the yard's change recorded unseen",
     [(WALK, "	If SeenOn(closed) && SeenOff(stamped) && SeenOff(signed)\n", "	If true\n"),
      (RULES, "	If !IsOn(akClosed) || !IsOff(akStamped) || !IsOff(akSigned)\n", "	If false\n")],
     "test_night_mail_scenes.TheHandover.test_the_yards_change_not_seen_then_seen_at_the_yard"),
    ("the yard's change recorded with its notice unanswered",
     [(WALK, "		If pick == 0\n			If akRiver.FinishAuthority(closed, stamped, signed)\n", "		If true\n			If akRiver.FinishAuthority(closed, stamped, signed)\n")],
     "test_night_mail_scenes.TheHandover.test_the_yards_notice_unanswered_is_not_recorded_and_comes_again"),
    ("a report nobody answered falling through to the rest of the conversation",
     [(WALK, "		ElseIf pick != 1\n			Return NW_REPORT_CLOSED\n", "		ElseIf false\n			Return NW_REPORT_CLOSED\n")],
     "test_night_mail_scenes.TheReport.test_unanswered_it_closes_the_conversation_and_reports_nothing"),
    ("a road completed by asking to leave",
     [(WALK, "	If !Arrived(akRiver, back)\n", "	If false\n")],
     "test_night_mail_scenes.TheWayHome.test_not_arrived_at_mercy_completes_nothing"),
    ("two uses at once",
     [(WALK, "	If talking\n		Return\n	EndIf\n	talking = true\n	TLM:MQ02AQuest river = Road()\n", "	talking = true\n	TLM:MQ02AQuest river = Road()\n")],
     "test_night_mail_scenes.Idempotency.test_two_uses_at_once_are_one"),
    ("posted in public taken for the yard alerted",
     [(RULES, "	If TLM_G_SQ01_YardAlerted.GetValueInt() == 1\n", "	If TLM_G_SQ01_Outcome.GetValueInt() == 1 || TLM_G_SQ01_Outcome.GetValueInt() == 3\n")],
     "test_night_mail_router.LockridgesGreeting.test_posted_in_public_is_not_the_yard_alerted"),
    ("the rail report taking the river's turn",
     [("Act1Walk.psc", "	int river = OfferRiverReport(akWho)\n	If river == RIVER_REPORT_GIVEN || river == RIVER_REPORT_CLOSED\n", "	int river = OfferRailReport(akWho)\n	If river == RIVER_REPORT_GIVEN || river == RIVER_REPORT_CLOSED\n")],
     "test_night_mail_router.BothRoads.test_both_reports_due_are_two_conversations_the_river_first"),
    ("a second outcome after the first",
     [(RULES, "	If Outcome() == NM_DEFEAT\n		Return NM_AT_CLEAR\n", "	If Outcome() == NM_DEFEAT\n		Return NM_AT_OPEN\n"),
      (RULES, "	If Claim != NM_NONE || ScenePending != NM_SCENE_NONE\n		Return false\n	EndIf\n	Claim = NM_RUN\n", "	Claim = NM_RUN\n")],
     "test_night_mail.TheFourCourses.test_the_four_outcomes_exclude_one_another"),
]


def changed(pieces):
    """A copy of the scripts with those pieces changed, each of them there exactly as often as the trial says
    (once, unless it says otherwise)."""
    folder = None
    for piece in pieces:
        name, old, new = piece[:3]
        times = piece[3] if len(piece) > 3 else 1
        if folder is None:
            folder = Path(tempfile.mkdtemp(prefix="tlm-nm-trial-"))
            for f in night_mail_player.SCRIPTS.glob("*.psc"):
                shutil.copy(f, folder / f.name)
        path = folder / name
        text = path.read_text()
        if text.count(old) != times:
            raise AssertionError("%s: %r is there %d times, not %d" % (name, old, text.count(old), times))
        path.write_text(text.replace(old, new))
    return folder


def run_against(scripts, test_id):
    """What that test, as it is written, says of those scripts: the failures and errors, as text."""
    suite = unittest.defaultTestLoader.loadTestsFromName(test_id)
    result = unittest.TestResult()
    with patch.object(night_mail_player, "SCRIPTS_NOW", scripts):
        suite.run(result)
    if result.testsRun == 0:
        raise AssertionError("no such test: " + test_id)
    return [text for _, text in result.failures + result.errors]


class EachGuardTakenOut(unittest.TestCase):
    def setUp(self):
        need_act1_build(self)

    def test_every_named_test_passes_on_the_scripts_as_they_are(self):
        for test_id in sorted({t[2] for t in TRIALS}):
            with self.subTest(test=test_id):
                self.assertEqual(run_against(night_mail_player.SCRIPTS, test_id), [])

    def test_each_guard_taken_out_is_noticed(self):
        for what, pieces, test_id in TRIALS:
            with self.subTest(what=what):
                said = run_against(changed(pieces), test_id)
                self.assertTrue(said, "%s: %s still passes" % (what, test_id))

    def test_the_trials_are_many_and_each_names_a_different_fault(self):
        self.assertGreaterEqual(len(TRIALS), 50)
        self.assertEqual(len({t[0] for t in TRIALS}), len(TRIALS))


if __name__ == "__main__":
    unittest.main()
