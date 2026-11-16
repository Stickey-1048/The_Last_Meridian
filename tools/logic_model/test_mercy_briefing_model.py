"""The Mercy briefing's state model (ACT1-RUNTIME-001): its gates, its one
objective, its one optional copy.

These tests say what the model does. tools/papyrus_sim/test_mercy_briefing.py
then holds the real scripts to the model, step by step.

Not a compile and not a game test.
"""
import itertools
import unittest
from dataclasses import replace

import mercy_briefing_model as mb
from mercy_briefing_model import Brief, Gates, Visit

OPEN = Gates()
# Every way the gates can be shut, one fact at a time.
SHUT = {
    "no delivery": replace(OPEN, delivered=False, acknowledged=False, stage60=False, stage100=False, done=False),
    "delivered, not acknowledged": replace(OPEN, acknowledged=False, stage60=False, stage100=False, done=False),
    "acknowledged, 60 absent": replace(OPEN, stage60=False, stage100=False, done=False),
    "60 set, its handler still at work": replace(OPEN, stage100=False, done=False),
    "100 without the Done global": replace(OPEN, done=False),
    "Done without 100": replace(OPEN, stage100=False),
    "Pritchard dead": replace(OPEN, briefer_alive=False),
    "Pritchard in a fight": replace(OPEN, briefer_fighting=True),
    "the player dead": replace(OPEN, player_alive=False),
    "not bound": replace(OPEN, bound=False),
    "its quest cannot be started": replace(OPEN, startable=False),
}

RAIL = Visit(hub=mb.HUB_RAIL)
RIVER = Visit(hub=mb.HUB_RIVER)
PIKE = Visit(hub=mb.HUB_PIKE)
NOT_NOW = Visit(hub=mb.HUB_NOT_NOW)
ASK = Visit(hub=mb.HUB_PIKE, pike=mb.PIKE_ASK_QUILL)
TAKE = Visit(hub=mb.HUB_PIKE, pike=mb.PIKE_ASK_QUILL, copy=mb.COPY_TAKE)
TAKE_FAILS = replace(TAKE, add=mb.ADD_FAILS)


def go(brief, *visits, gates=OPEN):
    shown = []
    for v in visits:
        brief, s, _ = mb.visit(brief, gates, v)
        shown.append(s)
    return brief, shown


class TheGates(unittest.TestCase):
    def test_only_the_final_acknowledged_state_opens_it(self):
        self.assertTrue(OPEN.open())
        for name, gates in SHUT.items():
            with self.subTest(name):
                self.assertFalse(gates.open())

    def test_shut_gates_change_nothing_and_show_nothing(self):
        for name, gates in SHUT.items():
            for v in (RAIL, RIVER, PIKE, NOT_NOW, ASK, TAKE):
                with self.subTest(name):
                    brief, shown, took = mb.visit(Brief(), gates, v)
                    self.assertEqual((brief, shown, took), (Brief(), [], False))

    def test_shut_gates_change_nothing_once_it_is_complete_either(self):
        done, _ = go(Brief(), TAKE)
        for name, gates in SHUT.items():
            with self.subTest(name):
                self.assertEqual(mb.visit(done, gates, TAKE), (done, [], False))


class TheTask(unittest.TestCase):
    def test_not_now_begins_it_and_finishes_nothing(self):
        brief, shown = go(Brief(), NOT_NOW)
        self.assertEqual(shown, [[mb.HUB]])
        self.assertTrue(brief.begun and brief.objective_shown)
        self.assertFalse(brief.done or brief.objective_complete)
        self.assertEqual(brief.copies_held, 0)

    def test_each_road_shows_its_own_brief_and_completes_the_task(self):
        for v, leaf in ((RAIL, mb.RAIL), (RIVER, mb.RIVER), (PIKE, mb.PIKE)):
            with self.subTest(leaf):
                brief, shown = go(Brief(), v)
                self.assertEqual(shown, [[mb.HUB, leaf]])
                self.assertTrue(brief.done and brief.objective_complete)
                self.assertEqual((brief.times_objective_shown, brief.times_completed), (1, 1))

    def test_it_begins_once_and_completes_once_however_often_he_is_asked(self):
        brief, shown = go(Brief(), NOT_NOW, RAIL, RIVER, PIKE, NOT_NOW, RAIL)
        self.assertEqual((brief.times_objective_shown, brief.times_completed), (1, 1))
        self.assertEqual(shown[-1], [mb.HUB, mb.RAIL])      # still answered after completion

    def test_a_visit_shows_one_road_and_no_more(self):
        for v in (RAIL, RIVER, PIKE, ASK, TAKE, NOT_NOW):
            _, shown = go(Brief(), v)
            self.assertLessEqual(sum(1 for m in shown[0] if m in (mb.RAIL, mb.RIVER, mb.PIKE)), 1)
            self.assertEqual(shown[0].count(mb.HUB), 1)

    def test_somebody_dying_while_the_hub_is_open_stops_it_there(self):
        for name in ("Pritchard dead", "Pritchard in a fight", "the player dead"):
            with self.subTest(name):
                v = replace(RAIL, after=((mb.HUB, SHUT[name]),))
                brief, shown, took = mb.visit(Brief(), OPEN, v)
                self.assertEqual(shown, [mb.HUB])
                self.assertTrue(took and brief.begun)
                self.assertFalse(brief.done)

    def test_somebody_dying_while_a_brief_is_open_leaves_the_task_unfinished(self):
        v = replace(RAIL, after=((mb.RAIL, SHUT["Pritchard dead"]),))
        brief, shown, _ = mb.visit(Brief(), OPEN, v)
        self.assertEqual(shown, [mb.HUB, mb.RAIL])
        self.assertFalse(brief.done)
        again, _ = go(brief, RAIL)
        self.assertTrue(again.done)                          # asked again, with him alive


class TheCopy(unittest.TestCase):
    def test_none_without_the_explicit_take(self):
        for v in (NOT_NOW, RAIL, RIVER, PIKE, ASK):
            brief, _ = go(Brief(), v)
            self.assertEqual((brief.copies_held, brief.add_requests, brief.copy_issued, brief.copy_pending), (0, 0, False, False))

    def test_taking_it_gives_one(self):
        brief, shown = go(Brief(), TAKE)
        self.assertEqual(shown, [[mb.HUB, mb.PIKE, mb.DOCKET]])
        self.assertEqual((brief.copies_held, brief.copies_given, brief.add_requests), (1, 1, 1))
        self.assertTrue(brief.copy_issued and not brief.copy_pending and brief.has_review_copy())

    def test_the_task_is_complete_whether_or_not_it_is_taken(self):
        for v in (PIKE, ASK, TAKE, TAKE_FAILS):
            self.assertTrue(go(Brief(), v)[0].done)

    def test_asking_again_offers_no_second_copy(self):
        brief, shown = go(Brief(), TAKE, TAKE, TAKE)
        self.assertEqual(shown[1], [mb.HUB, mb.PIKE, mb.DOCKET_ISSUED, mb.NOTE_ISSUED])
        self.assertEqual((brief.copies_held, brief.copies_given, brief.add_requests), (1, 1, 1))

    def test_dropped_it_is_not_held_and_is_not_given_again(self):
        brief, _ = go(Brief(), TAKE)
        brief = mb.drop(brief)
        self.assertFalse(brief.has_review_copy())
        self.assertTrue(brief.copy_issued)
        brief, shown = go(brief, TAKE)
        self.assertEqual(shown, [[mb.HUB, mb.PIKE, mb.DOCKET_ISSUED, mb.NOTE_ISSUED]])
        self.assertEqual((brief.copies_held, brief.copies_given, brief.add_requests), (0, 1, 1))
        self.assertTrue(mb.retrieve(brief).has_review_copy())

    def test_holding_it_is_never_read_from_progress_or_history(self):
        brief = mb.drop(go(Brief(), TAKE)[0])
        self.assertTrue(brief.done and brief.copy_issued)
        self.assertFalse(brief.has_review_copy())

    def test_a_request_the_game_does_not_honour_fails_closed(self):
        brief, shown = go(Brief(), TAKE_FAILS)
        self.assertEqual(shown, [[mb.HUB, mb.PIKE, mb.DOCKET, mb.NOTE_PENDING]])
        self.assertEqual((brief.copies_held, brief.copies_given, brief.add_requests), (0, 0, 1))
        self.assertTrue(brief.copy_pending and not brief.copy_issued)
        brief, shown = go(brief, TAKE, TAKE)
        self.assertEqual(shown[0], [mb.HUB, mb.PIKE, mb.DOCKET_ISSUED, mb.NOTE_PENDING])
        self.assertEqual((brief.copies_held, brief.add_requests), (0, 1))
        self.assertTrue(brief.copy_pending)

    def test_the_briefs_still_work_while_an_intent_is_pending(self):
        brief, _ = go(Brief(), TAKE_FAILS)
        _, shown = go(brief, RAIL, RIVER, PIKE)
        self.assertEqual(shown, [[mb.HUB, mb.RAIL], [mb.HUB, mb.RIVER], [mb.HUB, mb.PIKE]])

    def test_a_copy_that_arrived_after_all_is_acknowledged_and_not_doubled(self):
        brief, _ = go(Brief(), TAKE_FAILS)
        brief = mb.late_arrival(brief)
        self.assertTrue(brief.has_review_copy() and brief.copy_pending)
        brief, shown = go(brief, TAKE)
        self.assertEqual(shown, [[mb.HUB, mb.PIKE, mb.DOCKET_ISSUED, mb.NOTE_ISSUED]])
        self.assertTrue(brief.copy_issued and not brief.copy_pending)
        self.assertEqual((brief.copies_held, brief.copies_given, brief.add_requests), (1, 1, 1))

    def test_somebody_dying_while_the_copy_is_offered_gives_none(self):
        for name in ("Pritchard dead", "Pritchard in a fight", "the player dead"):
            with self.subTest(name):
                v = replace(TAKE, after=((mb.DOCKET, SHUT[name]),))
                brief, _, _ = mb.visit(Brief(), OPEN, v)
                self.assertEqual((brief.copies_held, brief.add_requests, brief.copy_pending), (0, 0, False))
                self.assertFalse(brief.done)


class WhateverIsDone(unittest.TestCase):
    """Every sequence of six things a person can do, from the start: nothing
    that must hold of the briefing is ever broken."""

    def test_no_sequence_breaks_it(self):
        dead = SHUT["Pritchard dead"]
        steps = {
            "not now": lambda b: mb.visit(b, OPEN, NOT_NOW)[0],
            "rail": lambda b: mb.visit(b, OPEN, RAIL)[0],
            "pike": lambda b: mb.visit(b, OPEN, PIKE)[0],
            "ask": lambda b: mb.visit(b, OPEN, ASK)[0],
            "take": lambda b: mb.visit(b, OPEN, TAKE)[0],
            "take, refused by the game": lambda b: mb.visit(b, OPEN, TAKE_FAILS)[0],
            "take, he dies first": lambda b: mb.visit(b, OPEN, replace(TAKE, after=((mb.DOCKET, dead),)))[0],
            "take, gates shut": lambda b: mb.visit(b, SHUT["60 set, its handler still at work"], TAKE)[0],
            "drop": mb.drop,
            "retrieve": mb.retrieve,
            "late arrival": mb.late_arrival,
        }
        seen, frontier = {Brief()}, {Brief()}
        for _ in range(6):
            nxt = set()
            for b in frontier:
                for name, step in steps.items():
                    after = step(b)
                    self.assertEqual(mb.problems(after), [], "%s from %r" % (name, b))
                    if after not in seen:
                        seen.add(after)
                        nxt.add(after)
            frontier = nxt
        self.assertGreaterEqual(len(seen), 6)
        # Reached, among the rest: issued and held; issued and not held; pending with none.
        self.assertTrue(any(b.copy_issued and b.has_review_copy() for b in seen))
        self.assertTrue(any(b.copy_issued and not b.has_review_copy() for b in seen))
        self.assertTrue(any(b.copy_pending and not b.has_review_copy() for b in seen))

    def test_the_check_itself_notices_a_broken_briefing(self):
        for broken in (Brief(begun=True, done=True, objective_complete=True, times_completed=2),
                       Brief(copies_held=2, copies_given=2, add_requests=1, copy_issued=True),
                       Brief(copies_held=1),
                       Brief(done=True),
                       Brief(copy_issued=True, copy_pending=True, copies_given=1, add_requests=1),
                       Brief(add_requests=2, copy_pending=True)):
            self.assertNotEqual(mb.problems(broken), [], repr(broken))


if __name__ == "__main__":
    unittest.main()
