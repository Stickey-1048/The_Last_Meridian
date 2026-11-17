"""The Night Mail road's state model (NIGHT-MAIL-STORY-001): four exclusive
outcomes, the stamp's three decisions, and what each does and does not earn.

These tests say what the model does. tools/papyrus_sim/test_night_mail*.py
then hold the real scripts to the model, action by action.

Not a compile and not a game test.
"""
import copy
import unittest

import night_mail_model as nm
from night_mail_model import Line


def at_the_cut(**world):
    """Travelled, hired, on the footplate in the Cut."""
    a = Line(**world)
    a.travel()
    a.talk_lockridge(pick="ride")
    a.use_depart()
    return a


class GettingThere(unittest.TestCase):
    def test_no_travel_before_the_chapter_is_over(self):
        a = Line(main_over=False)
        self.assertEqual(a.travel(), ["NoteTravelNotYet"])
        self.assertFalse(a.zones_up)

    def test_declining_to_travel_sets_nothing_up(self):
        a = Line()
        self.assertEqual(a.travel(go=False), ["AskTravel"])
        self.assertEqual((a.zones_up, a.stages, a.where), (False, set(), nm.MERCY))

    def test_arriving_is_stage_10_and_only_arriving(self):
        a = Line()
        a.travel()
        self.assertEqual((a.stages, a.where, a.shown), ({10}, nm.YARD, {10: True}))

    def test_travel_again_after_the_road_is_complete_asks_the_other_question(self):
        a = at_the_cut()
        a.use_train("back")
        a.leave()
        self.assertIn(100, a.stages)
        self.assertEqual(a.travel(), ["AskTravelAgain"])


class TheJob(unittest.TestCase):
    def test_refusing_changes_nothing_and_harms_nobody(self):
        a = Line()
        a.travel()
        before = copy.deepcopy(a.__dict__)
        self.assertEqual(a.talk_lockridge(pick="no"), ["LockridgeGateA", "LockridgeGateB"])
        self.assertEqual(a.__dict__, before)
        self.assertEqual(a.talk_lockridge(pick="hymns"), ["LockridgeGateA", "LockridgeGateB", "LockridgeDole"])
        self.assertEqual(a.__dict__, before)

    def test_the_three_greetings_read_the_side_quest_and_nothing_else(self):
        for kwargs, want in (({}, "LockridgeGateB"), ({"yard_alerted": True}, "LockridgeGateAlerted"),
                             ({"sq01_outcome": nm.NM_SQ01_SOLD}, "LockridgeGateSold"), ({"sq01_outcome": 3}, "LockridgeGateB")):
            a = Line(**kwargs)
            a.travel()
            self.assertIn(want, a.talk_lockridge(pick="no"))

    def test_alerted_wins_over_sold(self):
        a = Line(yard_alerted=True, sq01_outcome=nm.NM_SQ01_SOLD)
        a.travel()
        self.assertEqual(a.greeting(), nm.NM_GREET_ALERTED)

    def test_hired_names_billie_only_if_she_is_there(self):
        a = Line()
        a.travel()
        self.assertIn("LockridgeHired", a.talk_lockridge(pick="ride"))
        b = Line(billie=False)
        b.travel()
        self.assertIn("NoteAssignedNoBillie", b.talk_lockridge(pick="ride"))
        self.assertIn(20, b.stages)

    def test_a_dead_lockridge_gives_no_job_and_the_footplate_is_boarded_unasked(self):
        a = Line(lockridge=False)
        a.travel()
        self.assertEqual(a.talk_lockridge(pick="ride"), [])
        self.assertEqual(a.use_depart(go=False), ["AskBoard"])
        a.use_depart()
        self.assertEqual((a.where, a.stages >= {21, 30, 40}, 20 in a.stages), (nm.CUT, True, False))

    def test_her_authority_withdrawn_shuts_the_job(self):
        a = Line(yard_authority=nm.NM_YARD_WITHDRAWN)
        a.travel()
        self.assertEqual(a.talk_lockridge(pick="ride"), ["NoteNoDispatch"])
        self.assertEqual(a.use_depart(go=False), ["AskBoard"])


class TheFourOutcomes(unittest.TestCase):
    def test_run(self):
        a = at_the_cut()
        a.talk_billie(pick="run")
        self.assertEqual((a.outcome, a.mail, a.engine, a.train, a.mail_through, a.where), (nm.NM_RUN, nm.NM_MAIL_DELIVERED, nm.NM_ENGINE_DAMAGED, nm.NM_TRAIN_PLATFORM, True, nm.PLATFORM))
        self.assertEqual(a.problems(), [])

    def test_back_out(self):
        a = at_the_cut()
        a.talk_billie(pick="back")
        self.assertEqual((a.outcome, a.mail, a.train, a.line_closed, a.where), (nm.NM_BACKED, nm.NM_MAIL_RETAINED, nm.NM_TRAIN_YARD, True, nm.YARD))
        self.assertEqual((a.engine, a.mail_through), (nm.NM_ENGINE_SOUND, False))
        self.assertEqual(a.problems(), [])

    def test_sale_pays_once_and_seizes_the_mail(self):
        a = at_the_cut()
        a.talk_dole(["share", "done"])
        self.assertEqual((a.outcome, a.mail, a.caps, a.mail_sold, a.train, a.billie_released), (nm.NM_SOLD, nm.NM_MAIL_SEIZED, 150, True, nm.NM_TRAIN_TAKEN, True))
        self.assertEqual(a.talk_dole(["share", "done"]), ["DoleDefault"])
        self.assertEqual(a.caps, 150)
        self.assertEqual(a.problems(), [])

    def test_defeat_is_not_delivery(self):
        a = at_the_cut()
        a.talk_dole(["aside"])
        self.assertEqual(a.dole_dies(True), ["NoteDefeat"])
        self.assertEqual((a.outcome, a.mail, a.mail_through, a.dole_fate, 42 in a.stages), (nm.NM_DEFEAT, nm.NM_MAIL_ABOARD, False, nm.NM_DOLE_BY_PLAYER, True))
        self.assertEqual(a.problems(), [])

    def test_defeat_by_somebody_else_is_47_and_credits_nobody(self):
        a = at_the_cut()
        a.dole_dies(False)
        self.assertEqual((a.outcome, a.dole_fate, 42 in a.stages, 47 in a.stages), (nm.NM_DEFEAT, nm.NM_DOLE_OTHERWISE, False, True))

    def test_after_the_defeat_the_mail_goes_forward_or_back_and_the_outcome_stays(self):
        a = at_the_cut()
        a.dole_dies(True)
        a.use_train("forward")
        self.assertEqual((a.outcome, a.mail, a.mail_through, a.line_closed, a.engine), (nm.NM_DEFEAT, nm.NM_MAIL_DELIVERED, True, False, nm.NM_ENGINE_SOUND))
        b = at_the_cut()
        b.dole_dies(True)
        b.use_train("back")
        self.assertEqual((b.outcome, b.mail, b.mail_through, b.line_closed), (nm.NM_DEFEAT, nm.NM_MAIL_RETAINED, False, False))
        self.assertEqual((a.problems(), b.problems()), ([], []))

    def test_one_outcome_only(self):
        for first in ("run", "back", "sold"):
            a = at_the_cut()
            if first == "run":
                a.talk_billie(pick="run")
            elif first == "back":
                a.talk_billie(pick="back")
            else:
                a.talk_dole(["share", "done"])
            outcome = a.outcome
            a.use_train("run")
            a.use_train("back")
            a.talk_billie(pick="run")
            a.talk_dole(["share", "done"])
            self.assertEqual(a.outcome, outcome)
            self.assertEqual(a.caps, 150 if first == "sold" else 0)

    def test_dole_alive_and_known_is_a_fact_of_how_it_ended(self):
        a = at_the_cut()
        a.talk_billie(pick="run")
        self.assertTrue(a.dole_lives)
        b = at_the_cut()
        b.talk_billie(pick="back")
        self.assertFalse(b.dole_lives, "never met")
        c = at_the_cut()
        c.talk_dole(["back"])
        c.talk_billie(pick="back")
        self.assertTrue(c.dole_lives)

    def test_a_walk_away_from_the_parley_is_no_fight_and_the_fight_is_chosen(self):
        a = at_the_cut()
        a.talk_dole(["share", "back"])
        a.talk_dole(["back"])
        self.assertFalse(a.fight)
        a.talk_dole(["aside"])
        self.assertTrue(a.fight)
        self.assertEqual(a.talk_dole(["share", "done"]), [], "a man in a fight takes no payment")

    def test_the_fallbacks_say_no_one_who_is_not_there(self):
        a = at_the_cut(billie=False)
        self.assertIn(31, a.stages)
        a.talk_billie()
        a.use_train("run")
        self.assertIn(46, a.stages)
        self.assertFalse(a.billie_drives)
        b = at_the_cut(billie=False)
        b.talk_dole(["share", "done"])
        self.assertIn(48, b.stages)
        self.assertFalse(b.billie_released)


class TheEvidence(unittest.TestCase):
    def test_oral_identity_is_not_holding_or_reading_a_book(self):
        a = at_the_cut()
        a.talk_dole(["name", "silver", "share", "back"])
        self.assertEqual((a.ostrander_known, a.silver_rail, a.hymnals, 55 in a.stages, 56 in a.stages), (True, True, 0, False, True))
        self.assertFalse(a.can_show_hymnal())

    def test_the_flyleaf_gives_the_book_once_and_it_can_be_shown(self):
        a = at_the_cut()
        a.read_hymnal()
        a.read_hymnal()
        self.assertEqual((a.hymnals, a.asked["hymnal"]), (1, 1))
        a.use_train("run") if False else None
        a.where = nm.YARD
        self.assertTrue(a.can_show_hymnal())
        shown = a.talk_lockridge(show=True, stamp="close")
        self.assertEqual(shown[:2], ["AskShowHymnal", "LockridgeHymnal"])
        self.assertTrue(a.hymnal_shown)
        self.assertIn(60, a.stages)

    def test_a_hymnal_the_game_refuses_is_asked_for_once_and_claimed_never(self):
        a = at_the_cut(refused={"hymnal"})
        a.read_hymnal()
        a.read_hymnal()
        self.assertEqual((a.hymnals, a.asked["hymnal"], a.ostrander_known), (0, 1, True))

    def test_evidence_before_or_after_any_outcome_changes_no_outcome(self):
        for first in ("evidence", "outcome"):
            a = at_the_cut()
            if first == "evidence":
                a.use_plate()
                a.read_hymnal()
            a.talk_billie(pick="back")
            if first == "outcome":
                a.use_plate()
                a.read_hymnal()
            self.assertEqual((a.outcome, a.silver_rail, a.ostrander_known), (nm.NM_BACKED, True, True))


class TheStamp(unittest.TestCase):
    def drawer(self, **world):
        a = at_the_cut(**world)
        a.talk_billie(pick="back")
        return a

    def test_each_decision_and_only_one(self):
        for pick, stage, stamp in (("keep", 61, nm.NM_STAMP_KEPT), ("sign", 62, nm.NM_STAMP_SIGNED), ("take", 63, nm.NM_STAMP_TAKEN)):
            a = self.drawer()
            a.use_drawer(pick)
            self.assertEqual((a.stamp, stage in a.stages), (stamp, True), pick)
            before = copy.deepcopy(a.__dict__)
            a.use_drawer("take")
            a.use_drawer("keep")
            self.assertEqual(a.stamps + a.stamps_with_sheriff, 1 if pick == "take" else 0)
            self.assertEqual(a.stamp, stamp)
            self.assertEqual(a.problems(), [])

    def test_a_cancelled_countersigning_decides_nothing(self):
        a = self.drawer()
        a.use_drawer("sign", confirm=False)
        self.assertEqual((a.stamp, a.lockridge_signed), (nm.NM_STAMP_NONE, False))
        a.use_drawer("sign")
        self.assertEqual(a.stamp, nm.NM_STAMP_SIGNED)

    def test_taken_is_not_delivered_and_the_yard_is_not_touched(self):
        a = self.drawer()
        a.use_drawer("take")
        self.assertEqual((a.stamp_delivered, a.lockridge_reported, a.yard_authority), (False, False, nm.NM_YARD_HELD))
        self.assertEqual(a.use_board(), ["LabelBoardStamped"])

    def test_delivery_is_the_stamp_seen_with_the_sheriff_and_changes_the_yard(self):
        a = self.drawer()
        a.use_drawer("take")
        a.leave()
        a.report(give=True, hand=True)
        self.assertEqual((a.stamp_delivered, a.stamps, a.stamps_with_sheriff, a.yard_authority, a.lockridge_reported),
                         (True, 0, 1, nm.NM_YARD_WITHDRAWN, True))
        self.assertEqual(a.use_board(), ["LabelBoardClosed"])
        self.assertEqual(a.talk_lockridge(), ["NoteNoDispatch"])
        self.assertEqual(a.problems(), [])

    def test_the_yards_change_waits_for_its_acknowledgment(self):
        a = self.drawer()
        a.use_drawer("take")
        a.leave()
        shown = a.report(give=True, hand=True, acknowledge=False)
        self.assertEqual(shown[-1], "NoteAuthorityWithdrawn")
        self.assertEqual((a.stamp_delivered, a.yard_authority, a.lockridge_reported), (True, nm.NM_YARD_HELD, False))
        a.report(give=True, hand=True, acknowledge=True)
        self.assertEqual((a.yard_authority, a.lockridge_reported), (nm.NM_YARD_WITHDRAWN, True))

    def test_a_dead_lockridge_leaves_a_vacant_yard_not_a_withdrawal(self):
        a = self.drawer(lockridge=False)
        a.use_drawer("take")
        self.assertIn(64, a.stages)
        a.leave()
        a.report()
        self.assertEqual((a.yard_authority, a.lockridge_reported), (nm.NM_YARD_VACANT, True))

    def test_a_stamp_the_game_refuses_is_asked_for_once_and_nothing_is_decided(self):
        a = self.drawer(refused={"stamp"})
        a.use_drawer("take")
        a.use_drawer("take")
        self.assertEqual((a.asked["stamp"], a.stamp, a.stamps), (1, nm.NM_STAMP_NONE, 0))
        a.use_drawer("sign")
        self.assertEqual(a.stamp, nm.NM_STAMP_SIGNED)

    def test_a_dead_pritchard_receives_nothing(self):
        a = self.drawer(sheriff=False)
        a.use_drawer("take")
        a.leave()
        self.assertEqual(a.report(), [])
        self.assertEqual((a.stamp_delivered, a.stamps), (False, 1))


class TheReport(unittest.TestCase):
    def test_what_is_reported_is_what_is_held(self):
        for course, want in (("run", ["ReportMailDelivered", "ReportRan"]), ("back", ["ReportMailRetained", "ReportBacked"]),
                             ("sold", ["ReportMailSeized", "ReportSold"])):
            a = at_the_cut()
            if course == "run":
                a.talk_billie(pick="run")
                a.leave()
            elif course == "back":
                a.talk_billie(pick="back")
                a.leave()
            else:
                a.talk_dole(["share", "done"])
                a.where = nm.YARD
                a.leave()
            shown = a.report()
            self.assertEqual(shown[1:3], want, course)
            self.assertEqual(shown[0], "ReportUnknown")

    def test_a_report_left_for_later_is_not_given(self):
        a = at_the_cut()
        a.talk_billie(pick="back")
        a.leave()
        a.report(give=False)
        self.assertFalse(a.reported)
        a.report()
        self.assertTrue(a.reported)
        self.assertEqual(a.report(), [])

    def test_nothing_is_due_before_the_road_is_complete(self):
        a = at_the_cut()
        self.assertEqual(a.report(), [])
        a.talk_billie(pick="back")
        self.assertEqual(a.report(), [])


class TheWayHome(unittest.TestCase):
    def test_leaving_unresolved_completes_nothing_and_can_be_repeated(self):
        a = at_the_cut()
        a.back_to_yard()
        self.assertEqual(a.leave(), ["AskLeaveUnresolved", "NoteLeftUnresolved"])
        self.assertNotIn(100, a.stages)
        a.travel()
        a.use_depart()
        a.talk_billie(pick="back")
        self.assertEqual(a.leave()[0], "AskLeaveResolved")
        self.assertIn(100, a.stages)

    def test_the_way_back_never_settles_anything(self):
        a = at_the_cut()
        before = (a.outcome, a.mail, a.train, a.claim)
        a.back_to_yard()
        self.assertEqual((a.outcome, a.mail, a.train, a.claim), before)
        self.assertEqual(a.where, nm.YARD)
        a.use_depart()
        self.assertEqual(a.where, nm.CUT)


if __name__ == "__main__":
    unittest.main()
