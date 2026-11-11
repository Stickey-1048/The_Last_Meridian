"""SQ01 test matrix (S01-S17, plus cases added by the v0.2 amendments)."""
import unittest

import tlm_model as m
from tlm_model import NotAvailable, V01, V02, apply, available, run

DECISIONS = ("sq_report", "sq_post", "sq_post_yard", "sq_post_haskell", "sq_sell")
LEDGER = ["start", "take_ledger"]
LEVEL1 = LEDGER + ["examine_e1", "goto_town"]
LEVEL2 = LEDGER + ["examine_e1", "take_journal", "goto_town"]


def metrics(s):
    return (s.truth, s.competence, s.accountability, s.mutual_trust)


class SQ01Matrix(unittest.TestCase):
    def test_S01_ledger_only(self):
        s = run(LEDGER + ["goto_town"])
        self.assertTrue(s.sq_done(10))
        self.assertEqual(s.sq_o10, m.SHOWN)
        self.assertEqual(s.evidence_level, 0)
        self.assertFalse(s.sq_done(20))
        for d in DECISIONS:
            with self.assertRaises(NotAvailable):
                apply(s, d)

    def test_S02_clue_examined_before_the_ledger(self):
        s = run(["start", "examine_e1", "take_ledger"])
        self.assertEqual(s.evidence_level, 1)
        self.assertTrue(s.sq_done(20))
        old = run(["start", "examine_e1", "take_ledger"], rules=V01)
        self.assertEqual(old.evidence_level, 0)              # v0.1: clue not recorded

    def test_S03_ledger_plus_one(self):
        s = run(LEDGER + ["examine_e1"])
        self.assertEqual(s.evidence_level, 1)
        self.assertEqual(s.sq_o10, m.COMPLETE)
        self.assertEqual(s.sq_o20, m.SHOWN)

    def test_S04_journal_plus_one_is_level_2(self):
        s = run(LEDGER + ["take_journal", "examine_e1"])
        self.assertEqual(s.evidence_level, 2)
        self.assertTrue(s.sq_done(25))

    def test_S04b_journal_alone_is_level_1(self):
        s = run(LEDGER + ["take_journal"])
        self.assertEqual(s.evidence_level, 1)

    def test_S05_three_without_the_journal_is_level_2(self):
        s = run(LEDGER + ["examine_e1", "examine_e2", "goto_town", "pike_parts_book"])
        self.assertEqual(s.evidence_level, 2)

    def test_S05b_two_physical_clues_are_level_1(self):
        s = run(LEDGER + ["examine_e1", "examine_e2"])
        self.assertEqual(s.evidence_level, 1)

    def test_S06_report(self):
        s = run(LEVEL1 + ["sq_report"])
        self.assertEqual(s.sq_outcome, m.SQ_REPORTED)
        self.assertEqual(s.yard_alerted, 1)
        self.assertEqual(metrics(s), (1, 1, 0, 0))
        self.assertTrue(s.has_ledger)                        # Pritchard takes copies
        self.assertTrue(s.sq_done(100))

    def test_S07_post_no_name(self):
        s = run(LEVEL1 + ["sq_post"])
        self.assertEqual(s.sq_outcome, m.SQ_POSTED)
        self.assertEqual(metrics(s), (1, 0, 0, 0))

    def test_S08_yard_office_not_offered_at_level_1(self):
        s = run(LEVEL1)
        with self.assertRaises(NotAvailable):
            apply(s, "sq_post_yard")

    def test_S09_yard_office_at_level_2(self):
        s = run(LEVEL2 + ["sq_post_yard"])
        self.assertEqual(s.sq_outcome, m.SQ_POSTED_YARD)
        self.assertEqual(metrics(s), (1, 1, 0, 1))

    def test_S10_scapegoat(self):
        s = run(LEVEL1 + ["sq_post_haskell"])
        self.assertEqual(s.sq_outcome, m.SQ_POSTED_HASKELL)
        self.assertEqual(s.haskell, "gone")
        self.assertEqual(s.haskell_scapegoated, 1)
        self.assertEqual(metrics(s), (-1, -1, -1, -1))

    def test_S10b_scapegoat_is_offered_even_with_full_evidence(self):
        """Level 2 proves fraud, never an author. The trap stays open."""
        s = run(LEVEL2)
        self.assertIn("sq_post_haskell", available(s))

    def test_S11_sell(self):
        s = run(LEVEL2 + ["sq_sell"])
        self.assertEqual(s.sq_outcome, m.SQ_SOLD)
        self.assertTrue(s.sold_for_caps)
        self.assertFalse(s.has_ledger or s.has_journal)
        self.assertEqual(s.vane_has_ledger, 1)
        self.assertEqual(metrics(s), (0, 0, 0, 0))

    def test_S12_destroy(self):
        s = run(LEDGER + ["sq_destroy"])
        self.assertEqual(s.sq_outcome, m.SQ_DESTROYED)
        self.assertFalse(s.has_ledger)
        self.assertEqual(metrics(s), (-1, 0, 0, 0))

    def test_S13_do_nothing(self):
        s = run(LEVEL1 + ["goto_wreck", "goto_town"])
        self.assertTrue(s.sq_done(20))
        self.assertEqual(s.sq_outcome, m.SQ_NONE)
        self.assertIn("sq_report", available(s))

    def test_S14_pike_dead(self):
        s = run(LEDGER + ["pike_dies", "examine_e1", "take_journal"])
        self.assertEqual(s.evidence_level, 2)
        with self.assertRaises(NotAvailable):
            apply(run(["goto_town"], start=s), "pike_parts_book")

    def test_S15_skip_sq01(self):
        s = run(["start", "take_dispatch", "goto_town", "pritchard_handover", "pritchard_handoff"])
        self.assertTrue(s.done(100))
        self.assertFalse(s.sq_done(10))

    @unittest.skip("covered by test_invariants (stages and globals are the whole state); "
                   "alias refill after load is engine behaviour")
    def test_S16_reload(self):
        pass

    def test_S17_one_outcome_only(self):
        s = run(LEVEL2 + ["sq_post"])
        for d in DECISIONS + ("sq_destroy",):
            with self.subTest(d):
                with self.assertRaises(NotAvailable):
                    apply(s, d)

    # ---- added by the v0.2 amendments ----

    def test_S18_journal_taken_before_the_ledger(self):
        seq = ["start", "take_journal", "take_ledger", "examine_e1"]
        self.assertEqual(run(seq).evidence_level, 2)
        self.assertEqual(run(seq, rules=V01).evidence_level, 1)   # v0.1: E3 lost for good

    def test_S19_haskell_dead_hides_the_button(self):
        s = run(LEVEL1 + ["haskell_dies"])
        with self.assertRaises(NotAvailable):
            apply(s, "sq_post_haskell")
        self.assertIn("sq_post", available(s))

    def test_S20_vane_dead_hides_the_sale(self):
        s = run(LEVEL1 + ["vane_dies"])
        with self.assertRaises(NotAvailable):
            apply(s, "sq_sell")

    def test_S21_ledger_lost_and_recovered(self):
        s = run(LEVEL1 + ["ledger_vanishes"])
        with self.assertRaises(NotAvailable):
            apply(s, "sq_report")
        s = apply(s, "recovery")
        self.assertTrue(s.has_ledger)
        self.assertEqual(apply(s, "sq_report").sq_outcome, m.SQ_REPORTED)

    def test_S22_report_before_the_dispatch_is_delivered(self):
        """Amendment: the report topic must not depend on holding the dispatch."""
        s = run(LEVEL1)
        self.assertFalse(s.has_dispatch)
        self.assertEqual(apply(s, "sq_report").sq_outcome, m.SQ_REPORTED)

    def test_S23_report_after_mq01_is_finished(self):
        s = run(["start", "take_dispatch", "take_ledger", "examine_e1", "goto_town",
                 "pritchard_handover", "pritchard_handoff", "sq_report"])
        self.assertTrue(s.done(100))
        self.assertEqual(s.sq_outcome, m.SQ_REPORTED)

    def test_S24_evidence_frozen_after_outcome(self):
        s = run(LEVEL1 + ["sq_sell", "goto_wreck"])
        self.assertEqual(apply(s, "examine_e2") if "examine_e2" in available(s) else s, s)


if __name__ == "__main__":
    unittest.main()
