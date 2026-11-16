"""Exhaustive checks: every reachable state of the model, not sample paths."""
import random
import unittest

import invariants as inv
import tlm_model as m
from tlm_model import V01, V02

# SQ01 explored with the few MQ01 moves it depends on.
SQ_CONTEXT = {k: m.ALL_EVENTS[k] for k in ("start", "goto_wreck", "goto_town", "recovery")}
SQ_EVENTS = {**SQ_CONTEXT, **m.SQ01_EVENTS}


def finished(s):
    return s.done(100)


class MQ01Exhaustive(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.graph, cls.parent = m.explore(V02, m.MQ01_EVENTS)

    def test_state_space_is_explored(self):
        self.assertGreater(len(self.graph), 10_000)

    def test_no_invariant_violations(self):
        self.assertEqual(inv.collect(self.graph), {})

    def test_every_state_can_finish_on_the_shortest_path(self):
        """C6: from any reachable state the plain route (fetch the dispatch,
        walk to town, talk to Pritchard) still completes the quest."""
        stuck = inv.cannot_reach(self.graph, finished, only_events=m.MQ01_SPINE)
        stuck = [s for s in stuck if s.done(10)]
        if stuck:
            self.fail("soft-lock, e.g. after: %s" % m.path_to(self.parent, stuck[0]))

    def test_every_outcome_and_variant_is_reachable(self):
        outcomes = {s.outcome for s in self.graph}
        self.assertEqual(outcomes, {0, 1, 2, 3, 4})
        variants = {s.debrief_variant for s in self.graph if s.done(50)}
        self.assertEqual(
            variants,
            {m.V_SAVED, m.V_EVADED, m.V_WITNESS, m.V_NOWITNESS, m.V_MISSED, m.V_LOST},
        )
        reps = {s.rep for s in self.graph if s.done(50)}
        self.assertEqual(reps, {0, 1, 2})

    def test_no_dead_events(self):
        fired = {name for edges in self.graph.values() for name, _ in edges}
        by_design = {
            "npc_kills_lead",             # closed by A1 (Cutters are Protected)
            "walk_away_from_pritchard",   # harmless under A5 (conversation resumes)
            "pritchard_no_dispatch",      # available, but changes no state
        }
        self.assertEqual(set(m.MQ01_EVENTS) - fired, by_design)

    def test_completion_never_needs_the_caravan_or_the_revolver(self):
        done = [s for s in self.graph if s.done(100)]
        self.assertTrue(any(not s.has_revolver for s in done))
        self.assertTrue(any(not s.done(30) for s in done))


class SQ01Exhaustive(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.graph, cls.parent = m.explore(V02, SQ_EVENTS)

    def test_no_invariant_violations(self):
        self.assertEqual(inv.collect(self.graph), {})

    def test_every_outcome_is_reachable(self):
        self.assertEqual({s.sq_outcome for s in self.graph}, set(range(7)))

    def test_level_2_is_reachable_without_pike_and_without_the_journal(self):
        self.assertTrue(any(s.evidence_level == 2 and not s.pike_alive for s in self.graph))
        self.assertTrue(any(s.evidence_level == 2 and not s.e3 for s in self.graph))

    def test_no_dead_events(self):
        fired = {name for edges in self.graph.values() for name, _ in edges}
        self.assertEqual(set(SQ_EVENTS) - fired, set())


class Independence(unittest.TestCase):
    """C6: the optional quest cannot affect the main quest, and the reverse."""

    def test_sq01_events_never_touch_mq01_state(self):
        graph, _ = m.explore(V02, m.MQ01_EVENTS)
        for s in graph:
            for name, fn in m.SQ01_EVENTS.items():
                t = fn(s, V02)
                if t is None:
                    continue
                for f in inv.MQ_FIELDS:
                    if getattr(s, f) != getattr(t, f):
                        self.fail("%s changed MQ01 field %s" % (name, f))

    def test_mq01_events_never_touch_sq01_state(self):
        graph, _ = m.explore(V02, SQ_EVENTS)
        for s in graph:
            for name, fn in m.MQ01_EVENTS.items():
                if name in SQ_CONTEXT:
                    continue
                t = fn(s, V02)
                if t is None:
                    continue
                for f in inv.SQ_FIELDS:
                    if getattr(s, f) != getattr(t, f):
                        self.fail("%s changed SQ01 field %s" % (name, f))

    def test_random_joint_walks(self):
        """Both quests interleaved. The joint space is too large to enumerate,
        so this samples it; the two tests above are what make sampling enough."""
        rng = random.Random(2317)
        names = list(m.ALL_EVENTS)
        finished_runs = 0
        for _ in range(4000):
            s = m.State()
            for _step in range(60):
                options = [n for n in names if (m.ALL_EVENTS[n](s, V02) not in (None, s))]
                if not options:
                    break
                s = m.ALL_EVENTS[rng.choice(options)](s, V02)
                problems = inv.check_state(s)
                if problems:
                    self.fail(problems[0])
            # whatever happened, the plain route still finishes MQ01
            for n in ("start", "recovery", "goto_wreck", "take_dispatch", "goto_town",
                      "pritchard_handover", "pritchard_handoff"):
                t = m.ALL_EVENTS[n](s, V02)
                if t is not None:
                    s = t
            self.assertTrue(s.done(100))
            finished_runs += 1
        self.assertEqual(finished_runs, 4000)


class V01Draft(unittest.TestCase):
    """The v0.1 rules are expected to break. These tests pin down how, so the
    amendments in DESIGN_AMENDMENTS_v0.2.md are tied to something checkable."""

    @classmethod
    def setUpClass(cls):
        cls.graph, cls.parent = m.explore(V01, m.MQ01_EVENTS)
        cls.found = inv.collect(cls.graph)

    def test_v01_has_the_documented_holes(self):
        expected = {
            "stage 50 reached with no caravan outcome (Pritchard has no line)",
            "stage 50 reached with no debrief variant",
            "stage 50 without stage 40 (town failsafe never ran)",
            "player killed a caravan hand but the outcome is not Exploited",
            "caravan 'saved' by an NPC kill with no player action",
            "evade timer resolved Evaded while the player was in combat",
            "evade timer resolved Evaded while the player was talking to the Cutter lead",
        }
        self.assertTrue(expected <= set(self.found), set(expected) - set(self.found))

    def test_v01_can_soft_lock(self):
        stuck = [s for s in inv.cannot_reach(self.graph, finished) if s.done(10)]
        self.assertTrue(stuck)
        path = m.path_to(self.parent, stuck[0])
        self.assertIn("walk_away_from_pritchard", path)

    def test_v01_sq01_loses_early_evidence(self):
        graph, _ = m.explore(V01, SQ_EVENTS)
        lost = [s for s in graph if s.has_journal and s.sq_done(10) and not s.e3
                and s.sq_outcome == m.SQ_NONE]
        self.assertTrue(lost)


if __name__ == "__main__":
    unittest.main()
