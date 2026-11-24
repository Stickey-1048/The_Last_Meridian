"""Current SQ01 physical-comparison regressions; no plugin or native inputs."""
import itertools
import json
from pathlib import Path
import re
import sys
import unittest
from dataclasses import replace

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools/logic_model'))
sys.path.insert(0, str(ROOT / 'tools'))
import tlm_model as m
import gen_matrix_cases as gen


class PhysicalComparison(unittest.TestCase):
    def test_both_paper_orders_keep_comparison_objective(self):
        for order in [('take_ledger', 'take_journal'), ('take_journal', 'take_ledger')]:
            s = m.run(['start', *order])
            self.assertEqual((s.evidence_count, s.evidence_level), (1, 1))
            self.assertFalse(s.sq_done(20) or s.sq_done(25))
            self.assertEqual((s.sq_o10, s.sq_o20), (m.SHOWN, m.HIDDEN))
            for clue in ['examine_e1', 'examine_e2']:
                compared = m.apply(s, clue)
                self.assertTrue(compared.sq_done(20) and compared.sq_done(25))
                self.assertEqual((compared.sq_o10, compared.sq_o20), (m.COMPLETE, m.SHOWN))

    def test_papers_book_and_repeat_do_not_substitute_for_a_part(self):
        for papers in [[], ['take_journal']]:
            s = m.run(['start', 'take_ledger', *papers, 'goto_town', 'pike_parts_book'])
            self.assertGreaterEqual(s.evidence_level, 1)
            self.assertFalse(s.sq_done(20) or s.sq_done(25))
            for decision in ['sq_report', 'sq_post', 'sq_post_yard', 'sq_post_haskell', 'sq_sell']:
                with self.assertRaises(m.NotAvailable):
                    m.apply(s, decision)
            self.assertEqual(m._sq_recompute(s), s)
            self.assertEqual(m._sq_recompute(m._sq_recompute(s)), s)
            with self.assertRaises(m.NotAvailable):
                m.apply(s, 'pike_parts_book')
            self.assertEqual(m.apply(s, 'sq_destroy').sq_outcome, m.SQ_DESTROYED)

    def test_either_part_without_papers_then_later_journal(self):
        for clue in ['examine_e1', 'examine_e2']:
            s = m.run(['start', 'take_ledger', clue])
            self.assertTrue(s.sq_done(20))
            self.assertFalse(s.sq_done(25))
            self.assertEqual(s.evidence_level, 1)
            with self.assertRaises(m.NotAvailable):
                m.apply(s, clue)
            self.assertEqual(m._sq_recompute(s), s)
            s = m.apply(s, 'take_journal')
            self.assertTrue(s.sq_done(25))
            self.assertEqual(s.evidence_level, 2)

    def test_all_clue_combinations_match_existing_quest_gate_and_repair(self):
        # Exhaust the four independently recorded facts, including an older stage20
        # whose objective presentation has not yet been repaired.
        for flags in itertools.product([False, True], repeat=4):
            for old20 in [False, True]:
                stages = frozenset([10, 20] if old20 else [10])
                s = replace(m.State(), sq_stages=stages, e1=flags[0], e2=flags[1],
                            e3=flags[2], e4=flags[3], sq_o10=m.SHOWN, sq_o20=m.HIDDEN)
                r = m._sq_recompute(s)
                if not any(flags[:2]):
                    self.assertEqual(r, s)
                else:
                    self.assertTrue(r.sq_done(20))
                    self.assertEqual(r.sq_done(25), s.evidence_level >= 2)
                    self.assertEqual((r.sq_o10, r.sq_o20), (m.COMPLETE, m.SHOWN))
                self.assertEqual(m._sq_recompute(r), r)

    def test_no_ledger_or_decided_outcome_is_reopened(self):
        for stages in [frozenset(), frozenset([20])]:
            s = replace(m.State(), sq_stages=stages, e1=True, e3=True)
            self.assertEqual(m._sq_recompute(s), s)
        for outcome in range(1, 7):
            s = replace(m.State(), sq_stages=frozenset([10, 20]), e1=True, e3=True,
                        sq_outcome=outcome, sq_o10=m.HIDDEN, sq_o20=m.COMPLETE)
            self.assertEqual(m._sq_recompute(s), s)
        reported = m.run(['start', 'take_ledger', 'examine_e2', 'goto_town', 'sq_report'])
        self.assertEqual(reported.sq_outcome, m.SQ_REPORTED)
        with self.assertRaises(m.NotAvailable):
            m.apply(reported, 'sq_sell')

    def test_generation_is_identical_and_keeps_case_structure(self):
        first = gen.generate()
        self.assertEqual(first, gen.generate())
        self.assertEqual(first[0], gen.OUT_PSC.read_text())
        self.assertEqual(first[1], gen.OUT_JSON.read_text())
        cases = json.loads(first[1])['cases']
        self.assertEqual((len(cases), sum(len(c['steps']) for c in cases),
                          sum(c['checks'] for c in cases)), (53, 335, 1340))
        self.assertEqual(len(re.findall(r'^Function ', first[0], re.M)), 54)
        for number in [204, 216]:
            body = first[0].split('Function Case%d(' % number, 1)[1].split('EndFunction', 1)[0]
            self.assertIn('caseDriver.ExpectSide(" 5 10 13", 1, 1, 0, 0, 0, 0, 1, 0, 1, 1, 0, 0)', body)


if __name__ == '__main__':
    unittest.main()
