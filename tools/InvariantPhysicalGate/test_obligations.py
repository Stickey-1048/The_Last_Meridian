"""SQ01 obligations remain strict after an actual physical comparison."""
from dataclasses import replace
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools/logic_model'))
import invariants as inv
import tlm_model as m

MISSING20 = 'evidence level >= 1 with the ledger found, but stage 20 was never set'
MISSING25 = 'evidence level 2 with the ledger found, but stage 25 was never set'


class PhysicalGateObligations(unittest.TestCase):
    def test_reachable_paper_only_states_are_valid_in_both_orders(self):
        for order in [('take_ledger', 'take_journal'), ('take_journal', 'take_ledger')]:
            s = m.run(['start', *order])
            self.assertEqual(s.evidence_level, 1)
            self.assertEqual(inv.check_sq01_state(s), [])
            s = m.run(['goto_town', 'pike_parts_book'], start=s)
            self.assertEqual(s.evidence_level, 2)
            self.assertFalse(s.e1 or s.e2 or s.sq_done(20) or s.sq_done(25))
            self.assertEqual(inv.check_sq01_state(s), [])

    def test_each_physical_clue_still_requires_20_and_level2_requires_25(self):
        for clue in ['examine_e1', 'examine_e2']:
            level1 = m.run(['start', 'take_ledger', clue])
            self.assertEqual(inv.check_sq01_state(level1), [])
            corrupt = replace(level1, sq_stages=level1.sq_stages - {20})
            self.assertIn(MISSING20, inv.check_sq01_state(corrupt))
            self.assertNotIn(MISSING25, inv.check_sq01_state(corrupt))
            level2 = m.apply(level1, 'take_journal')
            self.assertEqual(inv.check_sq01_state(level2), [])
            for removed in [{20}, {25}, {20, 25}]:
                violations = inv.check_sq01_state(replace(level2, sq_stages=level2.sq_stages - removed))
                self.assertEqual(MISSING20 in violations, 20 in removed)
                self.assertEqual(MISSING25 in violations, 25 in removed)

    def test_all_other_rejection_messages_remain_active(self):
        # Independent corruptions exercise the adjacent reverse obligations and
        # outcome/custody assertions, rather than merely counting conditions.
        cases = [
            (replace(m.State(), sq_stages=frozenset([20])), 'SQ01 stage 20 without the ledger and one piece of evidence'),
            (replace(m.State(), sq_stages=frozenset([25])), 'SQ01 stage 25 below evidence level 2'),
            (replace(m.State(), has_ledger=True), 'ledger held but SQ01 stage 10 not set'),
            (replace(m.State(), sq_outcome=m.SQ_SOLD, has_ledger=True), 'ledger still held after being sold or destroyed'),
            (replace(m.State(), sq_o20=m.COMPLETE), 'SQ01 objective O20 completion disagrees with the outcome'),
            (replace(m.State(), sq_o20=m.SHOWN), 'SQ01 objective O20 shown before the ledger was found'),
        ]
        for state, expected in cases:
            with self.subTest(expected=expected):
                self.assertIn(expected, inv.check_sq01_state(state))

    def test_exact_two_condition_inverse_preserves_every_other_assertion(self):
        source = (ROOT / 'tools/logic_model/invariants.py').read_text()
        current = 's.sq_done(10) and (s.e1 or s.e2) and s.evidence_level >='
        self.assertEqual(source.count(current), 2)
        old = source.replace(current, 's.sq_done(10) and s.evidence_level >=')
        # The immutable baseline digest covers all other invariants and messages.
        import hashlib
        self.assertEqual(hashlib.sha256(old.encode()).hexdigest(),
                         'a230679414c61942c62aa71a078bdf6a0468fdea407ba09e5789d807a8979a33')


if __name__ == '__main__':
    unittest.main()
