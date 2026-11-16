"""Keeps the in-game self-test honest.

scripts/Source/User/TLM/SelfTest.psc runs inside Fallout 4 and compares the
game's globals with fixed numbers. Those numbers are predictions. This test
replays the same scenario in the logic model and fails if any number in the
Papyrus file differs from what the model says, so a failure seen in the game
means the game disagrees with the design, not that the expectation was typed
wrong.
"""
import re
import unittest
from pathlib import Path

import tlm_model as m
from tlm_model import V02, run

PSC = Path(__file__).resolve().parents[2] / "scripts" / "Source" / "User" / "TLM" / "SelfTest.psc"

# Numbers the scripts use for values the model keeps as names.
VARIANT_CODE = {m.V_SAVED: 1, m.V_EVADED: 2, m.V_WITNESS: 3, m.V_NOWITNESS: 4, m.V_MISSED: 5, m.V_LOST: 6}
ANSWER_CODE = {None: 0, "admit": 1, "deny": 2, "confess": 3, "blame": 4, "silent": 9}


def papyrus_expectations():
    """name -> expected int, from every CheckInt("name", <expr>, <int>) line."""
    found = {}
    for line in PSC.read_text().splitlines():
        hit = re.match(r'\s*CheckInt\("([^"]+)",\s*.+,\s*(-?\d+)\)\s*$', line)
        if hit:
            name = hit.group(1)
            assert name not in found, "duplicate check name: %s" % name
            found[name] = int(hit.group(2))
    return found


class SelfTestMatchesModel(unittest.TestCase):
    def test_every_number_in_the_self_test_is_what_the_model_predicts(self):
        want = {}

        # ---- TLM_MQ01, as the plugin stands: no caravan actors exist, which
        # the model expresses as Nell Fenwick dead by a non-player cause.
        s = run(["start"])
        want["MQ01 outcome after the start"] = s.outcome
        s = run(["take_dispatch", "goto_ambush"], start=s)
        want["MQ01 outcome while the ambush is live"] = s.outcome
        s = run(["player_kills_lead"], start=s)
        want["MQ01 outcome after saving"] = s.outcome
        want["MQ01 method after saving"] = s.method
        # A second resolution (the evade timer) is not available once saved.
        self.assertNotIn("evade_timer", m.available(s))
        want["MQ01 outcome after a second resolution"] = s.outcome
        s = run(["nell_dies_other", "goto_town_bypass_gate", "pritchard_handover"], start=s)
        self.assertTrue(s.done(40), "the hand-over must run the town stage itself")
        want["MQ01 reputation"] = s.rep
        want["MQ01 debrief variant"] = VARIANT_CODE[s.debrief_variant]
        want["MQ01 caravan alive at Mercy"] = s.alive_at_mercy
        want["MQ01 truth after delivery"] = s.truth
        want["MQ01 accountability after delivery"] = s.accountability
        want["MQ01 mutual trust after delivery"] = s.mutual_trust
        # No debrief answer is offered for this variant.
        for answer in ("debrief_admit", "debrief_deny", "debrief_confess", "debrief_blame"):
            self.assertNotIn(answer, m.available(s))
        want["MQ01 debrief answer after an answer not offered"] = ANSWER_CODE[s.debrief_answer]
        want["MQ01 truth after an answer not offered"] = s.truth
        s = run(["pritchard_handoff"], start=s)
        self.assertTrue(s.done(100))
        want["MQ01 done"] = s.mq01_done
        want["MQ01 debrief answer after the hand-off"] = ANSWER_CODE[s.debrief_answer]
        want["MQ01 reputation after the hand-off"] = s.rep

        # ---- TLM_SQ01, in the same session.
        s = run(["goto_wreck", "examine_e1"], start=s)
        self.assertFalse(s.sq_done(20))
        want["SQ01 evidence count before the ledger"] = s.evidence_count
        want["SQ01 evidence level before the ledger"] = s.evidence_level
        s = run(["take_ledger"], start=s)
        self.assertTrue(s.sq_done(20) and not s.sq_done(25))
        s = run(["take_journal"], start=s)
        self.assertTrue(s.sq_done(25))
        want["SQ01 evidence count with the journal"] = s.evidence_count
        want["SQ01 evidence level with the journal"] = s.evidence_level
        s = run(["goto_town", "sq_post_yard"], start=s)
        want["SQ01 outcome"] = s.sq_outcome
        want["total truth"] = s.truth
        want["total competence"] = s.competence
        want["total accountability"] = s.accountability
        want["total mutual trust"] = s.mutual_trust
        want["SQ01 Yard alerted"] = s.yard_alerted
        self.assertNotIn("sq_post_haskell", m.available(s))
        want["SQ01 outcome after a second decision"] = s.sq_outcome
        want["SQ01 Haskell scapegoated"] = s.haskell_scapegoated
        want["total truth after a second decision"] = s.truth

        # Checks that are about the plugin, not the model.
        fixed = {"core data version": 1, "torn transit pass given at the start": 1}

        got = papyrus_expectations()
        self.assertEqual(set(got) - set(fixed), set(want), "the self-test and this test name different checks")
        for name, value in sorted(want.items()):
            with self.subTest(name):
                self.assertEqual(got[name], value)
        for name, value in fixed.items():
            self.assertEqual(got[name], value)


if __name__ == "__main__":
    unittest.main()
