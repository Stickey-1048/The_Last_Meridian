"""The Greenwater road's state model (GREENWATER-STORY-001): four courses,
each exclusive of the others, and what each one does and does not earn.

These tests say what the model does. tools/papyrus_sim/test_greenwater.py
then holds the real scripts to the model, action by action.

Not a compile and not a game test.
"""
import copy
import unittest

import greenwater_model as gw
from greenwater_model import River


def aboard(**world):
    """Travelled, on the landing, heard Opal out, aboard by the gangway."""
    r = River(**world)
    r.travel()
    r.step_onto_landing()
    r.talk_opal(first="wants")
    r.board(gw.BOARD_GANGWAY)
    return r


class GettingThere(unittest.TestCase):
    def test_no_travel_before_the_chapter_is_over(self):
        r = River(main_over=False)
        self.assertEqual(r.travel(), ["NoteTravelNotYet"])
        self.assertFalse(r.zones_up)

    def test_declining_to_travel_sets_nothing_up(self):
        r = River()
        self.assertEqual(r.travel(go=False), ["AskTravel"])
        self.assertFalse(r.zones_up)

    def test_the_road_begins_on_the_landing_and_not_at_the_travel_point(self):
        r = River()
        r.travel()
        self.assertEqual(r.stages, set())
        r.step_onto_landing()
        self.assertEqual((r.stages, r.shown), ({10}, {10: True}))

    def test_hearing_opal_out_is_stage_20_and_promises_nothing(self):
        r = River()
        r.travel()
        r.step_onto_landing()
        self.assertEqual(r.talk_opal(first="guns"), ["OpalFirst", "OpalGuns"])
        self.assertNotIn(20, r.stages)
        self.assertEqual(r.talk_opal(first="wants"), ["OpalFirst", "OpalWants", "Goal", "Stakes"])
        self.assertEqual((r.stages, r.fate, r.outcome), ({10, 20}, gw.RV_H_FREE, gw.RV_NONE))

    def test_boarding_never_waits_on_opal(self):
        r = River(opal=False)
        r.travel()
        r.step_onto_landing()
        self.assertEqual(r.talk_opal(first="wants"), [])
        r.board(gw.BOARD_OFFSIDE)
        self.assertEqual(r.stages, {10, 30})
        self.assertEqual(r.shown.get(10), False)                 # no longer asked, and not ticked
        self.assertNotIn(10, r.ticked)


class Cards(unittest.TestCase):
    def test_a_loss_is_not_a_course_and_takes_nothing(self):
        r = aboard(charisma=4)
        self.assertEqual(r.use_table(["deal"], then="leave"), ["HatcherTable", "CardStakes", "HatcherWon"])
        self.assertEqual((r.claim, r.outcome, r.card, 45 in r.stages), (gw.RV_NONE, gw.RV_NONE, gw.RV_CARD_LOST, True))
        self.assertFalse(r.can_complete())
        # Another course is still open.
        self.assertEqual(r.use_chain("cut"), ["RaffertyChain", "NoteChainCut"])

    def test_a_win_yields_the_barge_and_does_not_deliver_it(self):
        r = aboard(charisma=5)
        self.assertEqual(r.use_table(["deal"], judge="release"), ["HatcherTable", "CardStakes", "HatcherLost", "ConfirmRelease"])
        self.assertEqual((r.cargo, r.grain_home, r.recovered), (gw.RV_CARGO_YIELDED, False, 0))
        self.assertFalse(r.can_complete())
        self.assertEqual(r.talk_opal(), ["OpalDefault"])        # nothing she says of it waits for anything but the barge
        self.assertEqual(r.use_pilot(), ["NoteTowScene"])
        self.assertEqual(r.reach_dock(), ["NoteHomeWhole"])
        self.assertEqual((r.cargo, r.grain_home, r.recovered), (gw.RV_CARGO_HOME_WHOLE, True, 12))
        self.assertTrue(r.can_complete())

    def test_the_three_judgments(self):
        hang = aboard(charisma=5)
        hang.use_table(["deal"], judge="hang")
        self.assertEqual((hang.fate, hang.hatcher, hang.hatcher_hanged, 60 in hang.stages), (gw.RV_H_HANGED, False, True, True))
        irons = aboard(charisma=5)
        irons.use_table(["deal"], judge="custody")
        self.assertEqual((irons.fate, irons.hatcher, 61 in irons.stages, irons.hatcher_friend), (gw.RV_H_CUSTODY, True, True, False))
        free = aboard(charisma=5)
        free.use_table(["deal"], judge="release")
        self.assertEqual((free.fate, free.hatcher_friend, free.stages & {60, 61}), (gw.RV_H_RELEASED, True, set()))

    def test_nobody_dead_is_offered_a_prisoner(self):
        r = aboard(charisma=5)
        r.opal = False
        self.assertEqual(r.use_table(["deal"], judge="hang"), ["HatcherTable", "CardStakes", "HatcherLostNoOpal"])
        self.assertEqual((r.fate, r.hatcher), (gw.RV_H_FREE, True))
        r = aboard(charisma=5, sheriff=False)
        self.assertEqual(r.use_table(["deal"], judge="custody"), ["HatcherTable", "CardStakes", "HatcherLostNoSheriff"])
        self.assertEqual(r.fate, gw.RV_H_FREE)
        r = aboard(charisma=5, sheriff=False)
        r.opal = False
        self.assertEqual(r.use_table(["deal"], judge="release"), ["HatcherTable", "CardStakes", "HatcherLostAlone", "ConfirmRelease"])
        self.assertEqual(r.fate, gw.RV_H_RELEASED)

    def test_opals_reactions_wait_for_the_barge(self):
        r = aboard(charisma=5)
        r.use_table(["deal"], judge="silent")
        self.assertEqual(r.talk_opal(judge="hang"), ["OpalDefault"])
        self.assertEqual(r.fate, gw.RV_H_FREE)
        r.use_pilot()
        r.reach_dock()
        self.assertEqual(r.talk_opal(judge="custody"), ["OpalAfterWon", "ConfirmCustody", "OpalDenied"])
        self.assertEqual(r.talk_opal(), ["OpalDefault"])


class TheShare(unittest.TestCase):
    def test_payment_the_lie_and_her_thanks_are_three_things(self):
        r = aboard()
        self.assertEqual(r.use_table(["share"]), ["HatcherTable", "HatcherShare", "ConfirmShare", "NoteSharePaid"])
        self.assertEqual((r.caps, r.share_paid, 44 in r.stages, 46 in r.stages, r.grain_sold, r.lie_told), (200, True, True, False, False, False))
        self.assertEqual(r.talk_opal(lie=False), ["AskLie"])
        self.assertEqual((r.lie_told, r.grain_sold), (False, False))
        self.assertEqual(r.talk_opal(lie=True), ["AskLie", "OpalAfterShare"])
        self.assertEqual((r.lie_told, r.lie_heard, r.grain_sold, 46 in r.stages, r.food), (True, True, True, True, 1))
        self.assertEqual(r.talk_opal(lie=True), ["OpalDefault"])

    def test_with_opal_dead_the_deal_stands_and_no_thanks_is_made_up(self):
        r = aboard()
        r.use_table(["share"])
        r.opal = False
        self.assertEqual(r.talk_opal(lie=True), [])
        self.assertEqual((r.lie_told, r.grain_sold, 46 in r.stages), (False, False, False))
        self.assertTrue(r.can_complete())

    def test_paid_once(self):
        r = aboard()
        r.use_table(["share"])
        r.use_table(["share"])
        self.assertEqual((r.caps, r.asked["caps"]), (200, 1))

    def test_a_payment_the_game_does_not_honour_is_no_deal(self):
        r = aboard(refused={"caps"})
        self.assertEqual(r.use_table(["share"]), ["HatcherTable", "HatcherShare", "ConfirmShare", "NoteShareFailed"])
        self.assertEqual((r.caps, r.share_paid, r.share_pending, r.claim, 44 in r.stages), (0, False, True, gw.RV_NONE, False))
        self.assertEqual(r.use_table(["share"]), ["HatcherTableNoShare"])       # never offered again
        self.assertEqual(r.asked["caps"], 1)
        self.assertEqual(r.use_chain("cut"), ["RaffertyChain", "NoteChainCut"])  # another course is open


class TheChute(unittest.TestCase):
    def test_a_cut_chain_is_not_yet_the_chute(self):
        r = aboard()
        r.use_chain("cut")
        self.assertEqual((r.escape_pending, r.outcome, 42 in r.stages, r.cargo), (True, gw.RV_NONE, False, gw.RV_CARGO_LASHED))
        self.assertFalse(r.can_complete())

    def test_from_the_cut_there_is_only_the_pilot_lever(self):
        r = aboard(charisma=9)
        r.use_chain("burn")                                      # warned of the fire first, then cuts
        r.use_chain("cut")
        self.assertEqual(r.use_fire(), ["NoteChainNothing"])
        self.assertEqual(r.use_table(["deal"]), ["HatcherDefault"])
        self.assertEqual(r.use_table(["share"]), ["HatcherDefault"])
        self.assertEqual(r.use_chain("burn"), ["NoteChainCut"])
        self.assertEqual((r.stages & {41, 43, 44}, r.caps, r.queen_burned), (set(), 0, False))

    def test_the_run_can_be_begun_again_and_is_done_once(self):
        r = aboard()
        r.use_chain("cut")
        self.assertEqual(r.reach_dock(), [])                     # the dock without the lever: nothing
        self.assertEqual(r.use_pilot(), ["NoteChuteScene"])
        self.assertEqual(r.use_pilot(), ["NoteChuteScene"])
        self.assertEqual(r.reach_dock(), ["NoteHomePiloted", "RaffertyRan"])
        self.assertEqual(r.reach_dock(), [])
        self.assertEqual((r.recovered, r.cargo, r.grain_home, r.hatcher_hunting), (8, gw.RV_CARGO_HOME_REDUCED, True, True))

    def test_alone_it_costs_half_and_a_dead_pilot_says_nothing(self):
        r = aboard()
        r.rafferty = False
        self.assertEqual(r.use_chain("cut"), ["AskChain", "NoteChainCut"])
        r.use_pilot()
        self.assertEqual(r.reach_dock(), ["NoteHomeAlone"])
        self.assertEqual(r.recovered, 6)

    def test_a_dead_hatcher_hunts_nobody(self):
        r = aboard()
        r.hatcher_dies()
        r.use_chain("cut")
        r.use_pilot()
        r.reach_dock()
        self.assertFalse(r.hatcher_hunting)
        self.assertEqual((r.hatcher_state(), r.fate), (gw.RV_H_DEAD, gw.RV_H_DEAD))


class TheFire(unittest.TestCase):
    def test_no_fire_without_the_warning_and_the_confirmation(self):
        r = aboard()
        self.assertEqual(r.use_fire(), ["NoteFireNotWarned"])
        self.assertEqual(r.use_chain("burn"), ["RaffertyChain", "NoteFireWarned"])
        self.assertEqual((r.claim, r.queen_burned), (gw.RV_NONE, False))
        self.assertEqual(r.use_fire(confirm=False), ["AskFire"])
        self.assertFalse(r.queen_burned)
        self.assertEqual(r.use_fire(), ["AskFire", "NoteFireScene", "RaffertyBurned"])
        self.assertEqual((r.cargo, r.recovered, r.grain_home, r.queen_burned, r.fate), (gw.RV_CARGO_DESTROYED, 0, False, True, gw.RV_H_UNACCOUNTED))

    def test_without_rafferty_the_warning_is_the_builds_own_text(self):
        r = aboard()
        r.rafferty = False
        self.assertEqual(r.use_chain("burn"), ["AskChain", "NoteFireWarned"])
        self.assertEqual(r.use_fire(), ["AskFire", "NoteFireScene"])

    def test_belden_feeds_once_and_only_when_the_grain_is_not_coming(self):
        r = aboard()
        self.assertEqual(r.talk_belden(), [])
        r.use_chain("burn")
        r.use_fire()
        self.assertEqual(r.talk_belden(), ["BeldenRelief"])
        self.assertEqual(r.talk_belden(), ["BeldenRelief"])
        self.assertEqual((r.food, r.asked["relief"]), (1, 1))


class Evidence(unittest.TestCase):
    def test_by_letter_by_admission_or_not_at_all(self):
        r = aboard()
        self.assertEqual(r.open_strongbox(read=False), ["LetterPage1"])
        self.assertFalse(r.silver_river)
        self.assertEqual(r.open_strongbox(), ["LetterPage1", "LetterPage2", "LetterPage3"])
        self.assertEqual((r.silver_river, r.hire_read, r.hire_heard, r.letters), (True, True, False, 1))
        r.open_strongbox()
        self.assertEqual(r.letters, 1)
        r = aboard()
        self.assertEqual(r.use_table(["paid", "leave"]), ["HatcherTable", "HatcherPaidA", "HatcherPaidB", "HatcherTable"])
        self.assertEqual((r.silver_river, r.hire_read, r.hire_heard, r.letters), (True, False, True, 0))
        r = aboard()
        r.use_chain("cut")
        r.use_pilot()
        r.reach_dock()
        self.assertEqual(r.leave(), ["AskLeaveResolved", "NoteRoadComplete"])
        self.assertEqual(r.report(), ["ReportUnknown", "ReportReduced", "ReportEndUnknown"])


class Leaving(unittest.TestCase):
    def test_leaving_with_nothing_settled_settles_nothing(self):
        r = aboard()
        before = copy.deepcopy(r)
        self.assertEqual(r.leave(), ["AskLeaveUnresolved", "NoteLeftUnresolved"])
        self.assertEqual(r, before)
        r.use_chain("cut")
        self.assertEqual(r.leave(), ["AskLeaveUnresolved", "NoteLeftUnresolved"])
        self.assertTrue(r.escape_pending)                        # the lock goes with the player and comes back
        self.assertEqual(r.report(), [])

    def test_complete_once_and_reported_once(self):
        r = aboard()
        r.use_table(["share"])
        self.assertEqual(r.leave(), ["AskLeaveResolved", "NoteRoadComplete"])
        self.assertEqual(r.leave(), ["AskLeaveAgain"])
        self.assertEqual(r.report(give=False), ["ReportUnknown"])
        self.assertFalse(r.reported)
        self.assertEqual(r.report(), ["ReportUnknown", "ReportSold", "ReportEndUnknown"])
        self.assertEqual(r.report(), [])


class WhateverIsDone(unittest.TestCase):
    """Every sequence of seven things a player can do aboard, in three worlds:
    nothing that must hold of the road is ever broken."""

    STEPS = {
        "opal": lambda r: r.talk_opal(first="wants", judge="hang", lie=True),
        "opal, releasing": lambda r: r.talk_opal(judge="release", lie=False),
        "deal, hang": lambda r: r.use_table(["deal"], then="share", judge="hang"),
        "deal, custody": lambda r: r.use_table(["deal"], then="leave", judge="custody"),
        "deal, silent": lambda r: r.use_table(["deal"], judge="silent"),
        "share": lambda r: r.use_table(["share"]),
        "admission": lambda r: r.use_table(["paid", "leave"]),
        "letter": lambda r: r.open_strongbox(),
        "cut": lambda r: r.use_chain("cut"),
        "warn": lambda r: r.use_chain("burn"),
        "pilot": lambda r: r.use_pilot(),
        "dock": lambda r: r.reach_dock(),
        "fire": lambda r: r.use_fire(),
        "belden": lambda r: r.talk_belden(),
        "leave": lambda r: r.leave(),
        "report": lambda r: r.report(),
        "hatcher dies": lambda r: r.hatcher_dies() if r.fate in (gw.RV_H_FREE, gw.RV_H_RELEASED) and not r.queen_burned else None,
        "opal dies": lambda r: setattr(r, "opal", False),
        "rafferty dies": lambda r: setattr(r, "rafferty", False),
    }

    def key(self, r):
        return repr(r)

    def test_no_sequence_breaks_it(self):
        reached = {"cards home": False, "chute": False, "fire": False, "share lied": False, "share unheard": False,
                   "hanged": False, "custody": False, "friend": False, "complete": False}
        for world in ({"charisma": 5}, {"charisma": 4}, {"charisma": 5, "refused": {"caps", "letter"}}):
            start = aboard(**world)
            seen, frontier = {self.key(start)}, [start]
            for _ in range(7):
                nxt = []
                for r in frontier:
                    for name, step in self.STEPS.items():
                        after = copy.deepcopy(r)
                        step(after)
                        self.assertEqual(after.problems(), [], "%s from %r" % (name, r))
                        k = self.key(after)
                        if k not in seen:
                            seen.add(k)
                            nxt.append(after)
                            reached["cards home"] |= after.cargo == gw.RV_CARGO_HOME_WHOLE
                            reached["chute"] |= 42 in after.stages
                            reached["fire"] |= 43 in after.stages
                            reached["share lied"] |= 46 in after.stages
                            reached["share unheard"] |= 100 in after.stages and 44 in after.stages and not after.lie_told
                            reached["hanged"] |= 60 in after.stages
                            reached["custody"] |= 61 in after.stages
                            reached["friend"] |= after.hatcher_friend
                            reached["complete"] |= 100 in after.stages
                frontier = nxt
        self.assertEqual([k for k, v in reached.items() if not v], [])

    def test_the_check_itself_notices_a_broken_road(self):
        for broken in (River(stages={10, 41, 42}, outcome=42, cargo=gw.RV_CARGO_HOME_REDUCED, recovered=8, grain_home=True),
                       River(stages={10, 100}),
                       River(stages={10, 44}, share_paid=True, caps=400, asked={"caps": 2}),
                       River(stages={10, 30, 60}, fate=gw.RV_H_HANGED, hatcher=False, hatcher_hanged=True),
                       River(stages={10, 44, 46}, share_paid=True, caps=200, grain_sold=True),
                       River(stages={10}, grain_home=True),
                       River(stages={10, 42}, outcome=42, cargo=gw.RV_CARGO_HOME_WHOLE, recovered=12, grain_home=True),
                       River(stages={10}, claim=gw.RV_FIRE, escape_pending=True),
                       River(stages={10}, hatcher_hunting=True),
                       River(stages={10, 50}, silver_river=True)):
            self.assertNotEqual(broken.problems(), [], repr(broken))


if __name__ == "__main__":
    unittest.main()
