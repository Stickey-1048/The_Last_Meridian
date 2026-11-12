"""MQ01 test matrix (T01-T28) run against the logic model.

Cases that depend on the engine (AI, crime, time of day, plugin loading)
cannot be modelled and are skipped with the reason. They still have to be
run in the game.
"""
import unittest

import tlm_model as m
from tlm_model import NotAvailable, V01, V02, apply, available, run

ENGINE_ONLY = "engine behaviour; must be tested in Fallout 4"

TO_AMBUSH = ["start", "take_dispatch", "goto_ambush"]
FINISH = ["goto_town", "pritchard_handover", "pritchard_handoff"]


class MQ01Matrix(unittest.TestCase):
    def test_T01_clean_dev_start(self):
        s = run(["start"])
        self.assertTrue(s.done(10))
        self.assertEqual(s.o10, m.SHOWN)
        self.assertEqual(s.loc, m.WRECK)
        self.assertFalse(s.has_revolver)
        self.assertEqual(s.caravan_state, m.ARMED)

    def test_T02_dispatch_pickup(self):
        s = run(["start", "take_dispatch"])
        self.assertTrue(s.done(20))
        self.assertEqual(s.o10, m.COMPLETE)
        self.assertEqual(s.o20, m.SHOWN)

    def test_T03_revolver_hint_once(self):
        s = run(["start", "take_revolver"])
        self.assertTrue(s.done(15))
        with self.assertRaises(NotAvailable):
            apply(s, "take_revolver")

    def test_T04_skip_revolver(self):
        s = run(["start", "take_dispatch"] + FINISH)
        self.assertFalse(s.has_revolver)
        self.assertTrue(s.done(100))

    def test_T05_saved_by_fight(self):
        s = run(TO_AMBUSH + ["player_kills_cutter"] * 3 + ["player_kills_lead"])
        self.assertTrue(s.done(31))
        self.assertEqual(s.outcome, m.OUT_SAVED)
        self.assertTrue(s.nell_alive and s.abel_alive)
        self.assertEqual(s.cargo, "intact")

    def test_T05b_three_cutters_dead_is_not_saved(self):
        s = run(TO_AMBUSH + ["player_kills_cutter"] * 3)
        self.assertEqual(s.outcome, m.OUT_NONE)
        self.assertEqual(s.caravan_state, m.LIVE)

    def test_T06_saved_by_lead_kill(self):
        s = run(TO_AMBUSH + ["player_kills_lead"])
        self.assertEqual(s.outcome, m.OUT_SAVED)
        self.assertEqual(s.cutters_alive, 3)
        self.assertTrue(s.cutters_gone)

    def test_T07_saved_by_speech(self):
        s = run(TO_AMBUSH + ["dunmore_speech_success"])
        self.assertEqual(s.outcome, m.OUT_SAVED)
        self.assertTrue(s.lead_alive)

    def test_T08_speech_fail_still_resolvable(self):
        s = run(TO_AMBUSH + ["dunmore_speech_fail"])
        self.assertTrue(s.in_combat)
        self.assertEqual(s.outcome, m.OUT_NONE)
        self.assertEqual(apply(s, "player_kills_lead").outcome, m.OUT_SAVED)
        with self.assertRaises(NotAvailable):
            apply(s, "dunmore_deal")           # the deal is off once combat starts

    def test_T09_evade_by_timer(self):
        s = run(TO_AMBUSH + ["evade_timer"])
        self.assertTrue(s.done(32))
        self.assertEqual(s.outcome, m.OUT_EVADED)
        self.assertFalse(s.abel_alive)
        self.assertTrue(s.nell_alive)
        self.assertEqual(s.cargo, "looted")

    def test_T09b_evade_by_distance(self):
        s = run(TO_AMBUSH + ["goto_town"])
        self.assertEqual(s.outcome, m.OUT_EVADED)

    def test_T10a_sneak_within_sight_is_evaded(self):
        s = run(TO_AMBUSH + ["goto_wreck"])
        self.assertEqual(s.outcome, m.OUT_EVADED)

    def test_T10b_never_met_the_ambush_is_missed(self):
        """Amendment A4: reaching town without entering the sight trigger."""
        s = run(["start", "take_dispatch", "goto_town"])
        self.assertTrue(s.done(34))
        self.assertEqual(s.outcome, m.OUT_MISSED)
        s = run(["pritchard_handover"], start=s)
        self.assertEqual(s.debrief_variant, m.V_MISSED)
        self.assertEqual(available(s, events={k: m.ALL_EVENTS[k] for k in (
            "debrief_admit", "debrief_deny", "debrief_confess", "debrief_blame")}), [])

    def test_T11_deal(self):
        s = run(TO_AMBUSH + ["dunmore_deal"])
        self.assertTrue(s.done(33))
        self.assertEqual((s.outcome, s.method), (m.OUT_EXPLOITED, m.METHOD_DEAL))
        self.assertEqual(s.cargo, "split")
        self.assertTrue(s.nell_alive)
        self.assertFalse(s.abel_alive)

    def test_T12_betrayal_both_dead_no_witness(self):
        s = run(TO_AMBUSH + ["player_kills_nell"] + FINISH[:2])
        self.assertTrue(s.done(35) and not s.done(33))
        self.assertEqual((s.outcome, s.method), (m.OUT_EXPLOITED, m.METHOD_BETRAYAL))
        self.assertFalse(s.nell_alive or s.abel_alive)
        self.assertEqual(s.debrief_variant, m.V_NOWITNESS)
        self.assertEqual(s.alive_at_mercy, 0)

    def test_T12b_betrayal_abel_only_leaves_a_witness(self):
        s = run(TO_AMBUSH + ["player_kills_abel"] + FINISH[:2])
        self.assertEqual((s.outcome, s.method), (m.OUT_EXPLOITED, m.METHOD_BETRAYAL))
        self.assertTrue(s.nell_alive)
        self.assertEqual(s.debrief_variant, m.V_WITNESS)
        self.assertEqual(s.rep, 0)

    def test_T12c_murder_after_saving_is_not_rewarded(self):
        """Amendment A3: v0.1 ignored kills after the first resolution."""
        seq = TO_AMBUSH + ["player_kills_lead", "player_kills_nell"] + FINISH[:2]
        s = run(seq)
        self.assertEqual((s.outcome, s.method), (m.OUT_EXPLOITED, m.METHOD_BETRAYAL))
        self.assertEqual(s.debrief_variant, m.V_WITNESS)     # Abel saw it
        self.assertEqual(s.mutual_trust, 0)
        old = run(seq, rules=V01)
        self.assertEqual(old.outcome, m.OUT_SAVED)           # v0.1: "Obliged."
        self.assertEqual(old.rep, 2)

    @unittest.skip(ENGINE_ONLY + " (ownership and theft)")
    def test_T13_take_cargo_after_saved(self):
        pass

    def test_T14_no_premature_evade_while_fighting(self):
        s = run(TO_AMBUSH + ["attack_cutter"])
        with self.assertRaises(NotAvailable):
            apply(s, "evade_timer")
        self.assertEqual(apply(s, "evade_timer", V01).outcome, m.OUT_EVADED)   # v0.1 hole

    def test_T14b_fight_then_leave_is_evaded(self):
        s = run(TO_AMBUSH + ["attack_cutter", "goto_town"])
        self.assertEqual(s.outcome, m.OUT_EVADED)

    def test_T14c_fight_then_hide_then_timer(self):
        s = run(TO_AMBUSH + ["attack_cutter", "break_combat", "evade_timer"])
        self.assertEqual(s.outcome, m.OUT_EVADED)

    @unittest.skip("covered by test_invariants (state is derivable from stages + globals); "
                   "timer restart after load is " + ENGINE_ONLY)
    def test_T15_reload_mid_encounter(self):
        pass

    @unittest.skip("covered by test_invariants; alias refill after load is " + ENGINE_ONLY)
    def test_T16_reload_at_each_stage(self):
        pass

    def test_T17_town_first(self):
        s = run(["start", "goto_ambush", "goto_town", "pritchard_no_dispatch"])
        self.assertFalse(s.done(20))
        self.assertEqual(s.o10, m.SHOWN)
        self.assertEqual(s.o20, m.HIDDEN)
        with self.assertRaises(NotAvailable):
            apply(s, "pritchard_handover")

    def test_T18_dispatch_taken_late(self):
        s = run(["start", "goto_ambush", "goto_town", "pritchard_no_dispatch",
                 "goto_wreck", "take_dispatch"] + FINISH)
        self.assertTrue(s.done(100))
        self.assertEqual(s.outcome, m.OUT_EVADED)

    def test_T19_dispatch_lost_and_recovered(self):
        s = run(["start", "take_dispatch", "dispatch_vanishes"])
        self.assertFalse(s.has_dispatch)
        s = apply(s, "recovery")
        self.assertTrue(s.has_dispatch and s.done(900))
        with self.assertRaises(NotAvailable):
            apply(s, "recovery")               # grants nothing twice
        self.assertTrue(run(FINISH, start=s).done(100))

    def test_T19c_handover_stands_without_the_dispatch(self):
        """Amendment A9: Pritchard's greeting is keyed on stage 20. The delivery
        stands; the recovery stage is not set by it (the script never did, and
        until 2026-11-12 this model wrongly said it was)."""
        s = run(["start", "take_dispatch", "dispatch_vanishes", "goto_town", "pritchard_handover"])
        self.assertTrue(s.done(50))
        self.assertFalse(s.done(900))
        self.assertFalse(s.has_dispatch)
        self.assertEqual(s.rep, 1)
        old = run(["start", "take_dispatch", "dispatch_vanishes", "goto_town"], rules=V01)
        with self.assertRaises(NotAvailable):
            apply(old, "pritchard_handover", V01)            # v0.1: no greeting fits

    def test_T12d_hands_cannot_be_killed_in_town(self):
        """Amendment A10."""
        s = run(TO_AMBUSH + ["player_kills_lead", "goto_town"])
        with self.assertRaises(NotAvailable):
            apply(s, "player_kills_nell")

    def test_T19b_recovery_grants_nothing_unearned(self):
        s = run(["start"])
        with self.assertRaises(NotAvailable):
            apply(s, "recovery")

    @unittest.skip(ENGINE_ONLY + " (Essential flag)")
    def test_T20_pritchard_essential(self):
        pass

    def test_T21_nell_dead_by_other_cause(self):
        s = run(TO_AMBUSH + ["player_kills_lead", "nell_dies_other"] + FINISH[:2])
        self.assertEqual(s.debrief_variant, m.V_LOST)
        self.assertEqual(s.alive_at_mercy, 0)
        self.assertEqual(s.mutual_trust, 0)
        self.assertTrue(apply(s, "pritchard_handoff").done(100))

    @unittest.skip(ENGINE_ONLY + " (packages and time of day)")
    def test_T22_night_arrival(self):
        pass

    def test_T23_reputation(self):
        cases = {
            "saved": (TO_AMBUSH + ["player_kills_lead"], 2),
            "evaded": (TO_AMBUSH + ["evade_timer"], 1),
            "deal, witness": (TO_AMBUSH + ["dunmore_deal"], 0),
            "betrayal, Nell witness": (TO_AMBUSH + ["player_kills_abel"], 0),
            "betrayal, no witness": (TO_AMBUSH + ["player_kills_nell"], 1),
            "missed": (["start", "take_dispatch"], 1),
        }
        for name, (seq, want) in cases.items():
            with self.subTest(name):
                s = run(seq + FINISH[:2])
                self.assertEqual(s.rep, want)

    def test_T24_metrics(self):
        m_ = lambda s: (s.truth, s.competence, s.accountability, s.mutual_trust)
        evaded = run(TO_AMBUSH + ["evade_timer"] + FINISH[:2])
        deal = run(TO_AMBUSH + ["dunmore_deal"] + FINISH[:2])
        saved = run(TO_AMBUSH + ["player_kills_lead"] + FINISH[:2])
        self.assertEqual(m_(saved), (0, 0, 0, 1))
        self.assertEqual(m_(apply(evaded, "debrief_admit")), (1, 0, 1, 0))
        self.assertEqual(m_(apply(evaded, "debrief_deny")), (-1, 0, 0, 0))
        self.assertEqual(m_(apply(evaded, "pritchard_handoff")), (0, 0, 0, 0))
        self.assertEqual(m_(apply(deal, "debrief_confess")), (1, 0, 1, 0))
        self.assertEqual(m_(apply(deal, "debrief_blame")), (-1, 0, 0, 0))
        self.assertEqual(m_(apply(deal, "debrief_deny")), (-1, 0, 0, -1))

    def test_T25_confess_or_deny_changes_only_metrics(self):
        deal = run(TO_AMBUSH + ["dunmore_deal"] + FINISH[:2])
        for choice in ("debrief_confess", "debrief_blame", "debrief_deny"):
            with self.subTest(choice):
                s = apply(deal, choice)
                self.assertEqual((s.rep, s.outcome, s.stages), (deal.rep, deal.outcome, deal.stages))
                with self.assertRaises(NotAvailable):
                    apply(s, choice)           # one answer only
                self.assertTrue(apply(s, "pritchard_handoff").done(100))

    def test_T26_completion(self):
        s = run(TO_AMBUSH + ["player_kills_lead"] + FINISH)
        self.assertTrue(s.done(60) and s.done(100))
        self.assertEqual(s.mq01_done, 1)

    def test_T26b_conversation_can_be_resumed(self):
        """Amendment A5: leaving between P1 and P2 must not strand the quest."""
        s = run(TO_AMBUSH + ["evade_timer"] + FINISH[:2])
        s2 = run(["goto_wreck", "goto_town", "pritchard_handoff"], start=s)
        self.assertTrue(s2.done(100))
        old = run(TO_AMBUSH + ["evade_timer"] + FINISH[:2] + ["walk_away_from_pritchard"], rules=V01)
        with self.assertRaises(NotAvailable):
            apply(old, "pritchard_handoff", V01)             # v0.1 soft-lock

    def test_T26c_gate_trigger_bypassed(self):
        """Amendment A7: the hand-over runs the stage 40 failsafe itself."""
        s = run(TO_AMBUSH + ["player_kills_lead", "goto_town_bypass_gate", "pritchard_handover"])
        self.assertTrue(s.done(40))
        self.assertTrue(s.hands_in_town)

    @unittest.skip(ENGINE_ONLY + " (plugin load and logs)")
    def test_T27_clean_plugin_load(self):
        pass

    @unittest.skip(ENGINE_ONLY + " (save compatibility)")
    def test_T28_unrelated_saves(self):
        pass


if __name__ == "__main__":
    unittest.main()
