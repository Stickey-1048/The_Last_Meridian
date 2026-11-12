"""Keeps the in-game world cases honest.

scripts/Source/User/TLM/WorldCases.psc plays TLM_MQ01 inside Fallout 4 with a
caravan made at run time (self-test scenarios 4 to 9) and compares what the
game holds with fixed numbers and fixed yes/no answers. Those are predictions.
This test replays the same event sequences in the logic model and fails if

  * a number in a CheckInt line differs from what the model says;
  * a CheckTrue line claims something the model says is false, or a
    CheckFalse line something the model says is true;
  * the script contains a scored check this test does not know about;
  * the sequence named in a case's description is not the one replayed here;
  * the stages a case sets do not add up to the stages the model reaches.

So a failure seen in the game means the game disagrees with the design, not
that an expectation was typed wrong.
"""
import re
import unittest
from pathlib import Path

import tlm_model as m
from tlm_model import available, run

SCRIPTS = Path(__file__).resolve().parents[2] / "scripts" / "Source" / "User" / "TLM"
PSC = SCRIPTS / "WorldCases.psc"

# Numbers the scripts use for values the model keeps as names.
VARIANT_CODE = {m.V_SAVED: 1, m.V_EVADED: 2, m.V_WITNESS: 3, m.V_NOWITNESS: 4, m.V_MISSED: 5, m.V_LOST: 6}
ANSWER_CODE = {None: 0, "admit": 1, "deny": 2, "confess": 3, "blame": 4, "silent": 9}
ANSWER_EVENTS = ("debrief_admit", "debrief_deny", "debrief_confess", "debrief_blame")

SEQUENCES = {
    "CaseEvaded": ["start", "take_dispatch", "goto_ambush", "evade_timer", "goto_town",
                   "pritchard_handover", "debrief_admit", "pritchard_handoff"],
    "CaseFightSaved": ["start", "take_dispatch", "goto_ambush", "attack_cutter", "player_kills_lead",
                       "goto_town", "pritchard_handover", "pritchard_handoff"],
    "CaseMissed": ["start", "take_dispatch", "goto_town", "pritchard_handover", "pritchard_handoff"],
    "CaseRoadBetrayal": ["start", "take_dispatch", "goto_ambush", "player_kills_nell", "goto_town",
                         "pritchard_handover", "pritchard_handoff"],
    "CaseMurderAfterSaving": ["start", "take_dispatch", "goto_ambush", "player_kills_lead", "player_kills_nell",
                              "goto_town", "pritchard_handover", "debrief_confess", "pritchard_handoff"],
    "CaseDeal": ["start", "take_dispatch", "goto_ambush", "dunmore_deal", "goto_town",
                 "pritchard_handover", "debrief_blame", "pritchard_handoff"],
}


def cargo_left(s):
    """What the stand-in wagon holds: its full load while intact, nothing once looted or split."""
    return cargo_count_const() if s.cargo == "intact" else 0


def source():
    return PSC.read_text()


def cargo_count_const():
    hit = re.search(r"^int\s+CARGO_COUNT\s*=\s*(\d+)\s+Const", source(), re.M)
    assert hit, "WorldCases.psc no longer declares CARGO_COUNT"
    return int(hit.group(1))


def function_body(name):
    hit = re.search(r"^Function\s+%s\(.*?^EndFunction" % re.escape(name), source(), re.M | re.S)
    assert hit, "WorldCases.psc has no function %s" % name
    return hit.group(0)


def checks(body):
    """(ints, trues, falses) of one case: name -> expected int, and two sets of names."""
    ints, trues, falses = {}, set(), set()
    for line in body.splitlines():
        hit = re.match(r'\s*test\.CheckInt\("([^"]+)",\s*.+,\s*(-?\d+)\)\s*$', line)
        if hit:
            assert hit.group(1) not in ints, "duplicate check name: %s" % hit.group(1)
            ints[hit.group(1)] = int(hit.group(2))
            continue
        hit = re.match(r'\s*test\.Check(True|False)\("([^"]+)",', line)
        if hit:
            names = trues if hit.group(1) == "True" else falses
            assert hit.group(2) not in trues | falses, "duplicate check name: %s" % hit.group(2)
            names.add(hit.group(2))
            continue
        assert "test.Check" not in line, "a check this test cannot read: %s" % line.strip()
    return ints, trues, falses


def declared_sequence(body):
    """The event list a case's description gives after 'logic model:'."""
    doc = re.search(r"\{(.*?)\}", body, re.S)
    assert doc, "the case has no description"
    hit = re.search(r"logic\s+model:\s*(.*?)\.\s*$", doc.group(1), re.S)
    assert hit, "the case's description does not name its sequence in the logic model"
    return [w for w in re.split(r"[,\s]+", hit.group(1)) if w]


def stages_reached(body):
    return {int(n) for n in re.findall(r"\bReach\(TLM_MQ01,\s*(\d+)\)", body)}


def answer_stages():
    """Debrief answer -> the stage that gives it, read from the quest script."""
    text = (SCRIPTS / "MQ01Quest.psc").read_text()
    found = {}
    for stage, answer in re.findall(r"auiStageID\s*==\s*(\d+)\s*\n\s*ApplyDebriefAnswer\(ANS_(\w+)\)", text):
        found[answer.lower()] = int(stage)
    assert {"admit", "deny", "confess", "blame"} <= set(found), "could not read the answer stages from MQ01Quest.psc"
    return found


class WorldCasesMatchModel(unittest.TestCase):
    def compare(self, case, want_int, want_bool, fixture_checks, set_by_handlers, without_effect, final):
        """without_effect: stages the case sets to show that they change nothing."""
        body = function_body(case)
        self.assertEqual(declared_sequence(body), SEQUENCES[case],
                         "%s describes a different sequence from the one replayed here" % case)
        ints, trues, falses = checks(body)
        self.assertEqual(set(ints), set(want_int), "%s and this test name different CheckInt checks" % case)
        for name, value in sorted(want_int.items()):
            with self.subTest(name):
                self.assertEqual(ints[name], value)
        self.assertEqual((trues | falses) - fixture_checks, set(want_bool),
                         "%s and this test name different yes/no checks" % case)
        self.assertLessEqual(fixture_checks, trues, "fixture checks are CheckTrue lines")
        for name, value in sorted(want_bool.items()):
            with self.subTest(name):
                self.assertEqual(name in trues, value,
                                 "the model says %r; the script checks for the opposite" % value)
        # Stage numbers: what the case sets itself, plus what the quest's own
        # handlers set, is exactly what the model reaches. Two kinds of stage
        # are outside that sum: a debrief answer, which the model keeps as a
        # value and the game gives through a stage, and stages the case sets
        # to show that they change nothing.
        reached = stages_reached(body)
        answers = answer_stages()
        given = {answers[e[len("debrief_"):]] for e in SEQUENCES[case] if e.startswith("debrief_")}
        self.assertLessEqual(given, reached, "%s does not set the stage of the answer its sequence gives" % case)
        self.assertLessEqual(without_effect, reached)
        self.assertFalse(without_effect & given)
        self.assertFalse(without_effect & set(final.stages))
        self.assertEqual((reached - without_effect - given) | set_by_handlers, set(final.stages),
                         "%s sets stages that do not add up to the model's" % case)

    def test_scenario_4_evaded(self):
        seq = SEQUENCES["CaseEvaded"]
        p = "C4 "
        want, yes = {}, {}

        s = run(seq[:3])
        yes[p + "the ambush is live"] = s.caravan_state == m.LIVE
        s = run(["evade_timer"], start=s)
        yes[p + "stage 32 set when the evade timer runs out"] = s.done(32)
        want[p + "outcome after evading"] = s.outcome
        want[p + "method after evading"] = s.method
        yes[p + "the drover is dead once the Cutters have the wagon"] = not s.abel_alive
        yes[p + "the caravan master is dead"] = not s.nell_alive
        yes[p + "the drover's death at the Cutters' hands counts as a betrayal"] = s.done(35)
        self.assertEqual(s.cargo, "looted")
        want[p + "cargo left on the wagon after evading"] = cargo_left(s)

        s = run(["goto_town"], start=s)
        want[p + "caravan alive at Mercy on reaching town"] = s.alive_at_mercy
        yes[p + "the caravan master is in the town alias"] = s.hands_in_town and s.nell_alive
        yes[p + "the dead drover is not in the town alias"] = not (s.hands_in_town and s.abel_alive)
        yes[p + "the Cutter lead is disabled once the player is in town"] = s.cutters_gone
        # Amendment A10: in town a caravan hand cannot be killed. The script
        # tries it after the hand-over; the aliases are the same from the town
        # stage on, so the model is asked here, where a kill could still matter.
        yes[p + "the caravan master in the town alias can be killed"] = "player_kills_nell" in available(s)

        s = run(["pritchard_handover"], start=s)
        want[p + "reputation after the hand-over"] = s.rep
        want[p + "debrief variant"] = VARIANT_CODE[s.debrief_variant]
        want[p + "caravan alive at Mercy after the hand-over"] = s.alive_at_mercy
        want[p + "mutual trust after the hand-over"] = s.mutual_trust

        s = run(["debrief_admit"], start=s)
        want[p + "debrief answer after admitting"] = ANSWER_CODE[s.debrief_answer]
        want[p + "truth after admitting"] = s.truth
        want[p + "accountability after admitting"] = s.accountability
        for answer in ANSWER_EVENTS:
            self.assertNotIn(answer, available(s))
        want[p + "debrief answer after a second answer"] = ANSWER_CODE[s.debrief_answer]
        want[p + "truth after a second answer"] = s.truth

        s = run(["pritchard_handoff"], start=s)
        yes[p + "stage 100 set by the hand-off"] = s.done(100)
        want[p + "done"] = s.mq01_done
        want[p + "debrief answer after the hand-off"] = ANSWER_CODE[s.debrief_answer]
        want[p + "reputation after the hand-off"] = s.rep

        self.compare(
            "CaseEvaded", want, yes,
            fixture_checks={p + "the caravan and the Cutter lead stand in the quest's aliases"},
            set_by_handlers={32, 100},      # the evade timer's handler; the hand-off
            without_effect={52},            # a second debrief answer
            final=s)

    def test_scenario_5_fight_saved(self):
        seq = SEQUENCES["CaseFightSaved"]
        p = "C5 "
        want, yes = {}, {}

        s = run(seq[:4])
        yes[p + "the ambush is live"] = s.caravan_state == m.LIVE
        self.assertTrue(s.in_combat)
        s = run(["player_kills_lead"], start=s)
        yes[p + "stage 31 set by the lead's death"] = s.done(31)
        want[p + "outcome after the lead's death"] = s.outcome
        want[p + "method after the lead's death"] = s.method
        yes[p + "the caravan master is dead"] = not s.nell_alive
        yes[p + "the drover is dead"] = not s.abel_alive
        self.assertEqual(s.cargo, "intact")
        want[p + "cargo left on the wagon after the rescue"] = cargo_left(s)

        s = run(["goto_town"], start=s)
        want[p + "caravan alive at Mercy on reaching town"] = s.alive_at_mercy
        yes[p + "the caravan master is in the town alias"] = s.hands_in_town and s.nell_alive
        yes[p + "the drover is in the town alias"] = s.hands_in_town and s.abel_alive
        yes[p + "the dead Cutter lead is disabled once the player is in town"] = s.cutters_gone

        s = run(["pritchard_handover"], start=s)
        want[p + "reputation after the hand-over"] = s.rep
        want[p + "debrief variant"] = VARIANT_CODE[s.debrief_variant]
        want[p + "mutual trust after the hand-over"] = s.mutual_trust
        want[p + "truth after the hand-over"] = s.truth
        want[p + "accountability after the hand-over"] = s.accountability
        for answer in ANSWER_EVENTS:
            self.assertNotIn(answer, available(s))
        want[p + "debrief answer after an answer not offered"] = ANSWER_CODE[s.debrief_answer]
        want[p + "truth after an answer not offered"] = s.truth

        s = run(["pritchard_handoff"], start=s)
        yes[p + "stage 100 set by the hand-off"] = s.done(100)
        want[p + "done"] = s.mq01_done
        want[p + "debrief answer after the hand-off"] = ANSWER_CODE[s.debrief_answer]
        want[p + "reputation after the hand-off"] = s.rep
        want[p + "mutual trust after the hand-off"] = s.mutual_trust

        self.compare(
            "CaseFightSaved", want, yes,
            fixture_checks={p + "the caravan and the Cutter lead stand in the quest's aliases"},
            # 30: by the fight, or set by the case if the fight does not set it
            # (the Reach(30) in the script is that fallback); 31: the lead's
            # death; 100: the hand-off.
            set_by_handlers={30, 31, 100},
            without_effect={51},            # an answer this variant does not offer
            final=s)

    def test_scenario_6_missed(self):
        seq = SEQUENCES["CaseMissed"]
        p = "C6 "
        want, yes = {}, {}

        s = run(seq[:2])
        yes[p + "the ambush is armed and has not been met"] = s.caravan_state == m.ARMED
        s = run(["goto_town"], start=s)
        yes[p + "stage 34 set on reaching town"] = s.done(34)
        want[p + "outcome on reaching town"] = s.outcome
        want[p + "method on reaching town"] = s.method
        want[p + "caravan alive at Mercy on reaching town"] = s.alive_at_mercy
        yes[p + "the caravan master is in the town alias"] = s.hands_in_town and s.nell_alive
        yes[p + "the dead drover is not in the town alias"] = not (s.hands_in_town and s.abel_alive)
        yes[p + "the Cutter lead is disabled once the player is in town"] = s.cutters_gone
        yes[p + "the drover is dead once the Cutters have the wagon"] = not s.abel_alive
        yes[p + "the caravan master is dead"] = not s.nell_alive
        yes[p + "the drover's death at the Cutters' hands counts as a betrayal"] = s.done(35)
        want[p + "cargo left on the wagon"] = cargo_left(s)

        s = run(["pritchard_handover"], start=s)
        want[p + "reputation after the hand-over"] = s.rep
        want[p + "debrief variant"] = VARIANT_CODE[s.debrief_variant]
        want[p + "mutual trust after the hand-over"] = s.mutual_trust
        for answer in ANSWER_EVENTS:
            self.assertNotIn(answer, available(s))
        want[p + "debrief answer after an answer not offered"] = ANSWER_CODE[s.debrief_answer]
        want[p + "truth after an answer not offered"] = s.truth

        s = run(["pritchard_handoff"], start=s)
        yes[p + "stage 100 set by the hand-off"] = s.done(100)
        want[p + "done"] = s.mq01_done
        want[p + "debrief answer after the hand-off"] = ANSWER_CODE[s.debrief_answer]
        want[p + "reputation after the hand-off"] = s.rep

        self.compare(
            "CaseMissed", want, yes,
            fixture_checks={p + "the caravan and the Cutter lead stand in the quest's aliases"},
            set_by_handlers={34, 100},      # the town stage resolving the ambush; the hand-off
            without_effect={51},
            final=s)

    def test_scenario_7_betrayal_on_the_road(self):
        seq = SEQUENCES["CaseRoadBetrayal"]
        p = "C7 "
        want, yes = {}, {}

        s = run(seq[:3])
        yes[p + "the ambush is live"] = s.caravan_state == m.LIVE
        s = run(["player_kills_nell"], start=s)
        yes[p + "stage 35 set by the caravan master's death"] = s.done(35)
        want[p + "outcome after the killing"] = s.outcome
        want[p + "method after the killing"] = s.method
        yes[p + "the caravan master is dead"] = not s.nell_alive
        yes[p + "the drover is dead once the Cutters overrun the wagon"] = not s.abel_alive
        want[p + "cargo left on the wagon after the killing"] = cargo_left(s)

        s = run(["goto_town"], start=s)
        want[p + "caravan alive at Mercy on reaching town"] = s.alive_at_mercy
        yes[p + "the dead caravan master is not in the town alias"] = not (s.hands_in_town and s.nell_alive)
        yes[p + "the dead drover is not in the town alias"] = not (s.hands_in_town and s.abel_alive)
        yes[p + "the Cutter lead is disabled once the player is in town"] = s.cutters_gone

        s = run(["pritchard_handover"], start=s)
        want[p + "reputation after the hand-over"] = s.rep
        want[p + "debrief variant"] = VARIANT_CODE[s.debrief_variant]
        want[p + "caravan alive at Mercy after the hand-over"] = s.alive_at_mercy
        want[p + "mutual trust after the hand-over"] = s.mutual_trust
        for answer in ANSWER_EVENTS:
            self.assertNotIn(answer, available(s))
        want[p + "debrief answer after an answer not offered"] = ANSWER_CODE[s.debrief_answer]
        want[p + "truth after an answer not offered"] = s.truth

        s = run(["pritchard_handoff"], start=s)
        yes[p + "stage 100 set by the hand-off"] = s.done(100)
        want[p + "done"] = s.mq01_done
        want[p + "debrief answer after the hand-off"] = ANSWER_CODE[s.debrief_answer]
        want[p + "reputation after the hand-off"] = s.rep

        self.compare(
            "CaseRoadBetrayal", want, yes,
            fixture_checks={p + "the caravan and the Cutter lead stand in the quest's aliases"},
            set_by_handlers={35, 100},      # the caravan master's death; the hand-off
            without_effect={53},
            final=s)

    def test_scenario_8_murder_after_saving(self):
        seq = SEQUENCES["CaseMurderAfterSaving"]
        p = "C8 "
        want, yes = {}, {}

        s = run(seq[:4])
        yes[p + "stage 31 set by the lead's death"] = s.done(31)
        want[p + "outcome after the lead's death"] = s.outcome
        s = run(["player_kills_nell"], start=s)
        yes[p + "stage 35 set by the caravan master's death"] = s.done(35)
        want[p + "outcome after the murder"] = s.outcome
        want[p + "method after the murder"] = s.method
        yes[p + "the caravan master is dead"] = not s.nell_alive
        yes[p + "the drover is dead"] = not s.abel_alive
        want[p + "cargo left on the wagon after the murder"] = cargo_left(s)

        s = run(["goto_town"], start=s)
        want[p + "caravan alive at Mercy on reaching town"] = s.alive_at_mercy
        yes[p + "the drover is in the town alias"] = s.hands_in_town and s.abel_alive
        yes[p + "the dead caravan master is not in the town alias"] = not (s.hands_in_town and s.nell_alive)

        s = run(["pritchard_handover"], start=s)
        want[p + "reputation after the hand-over"] = s.rep
        want[p + "debrief variant"] = VARIANT_CODE[s.debrief_variant]
        want[p + "mutual trust after the hand-over"] = s.mutual_trust

        s = run(["debrief_confess"], start=s)
        want[p + "debrief answer after confessing"] = ANSWER_CODE[s.debrief_answer]
        want[p + "truth after confessing"] = s.truth
        want[p + "accountability after confessing"] = s.accountability

        s = run(["pritchard_handoff"], start=s)
        yes[p + "stage 100 set by the hand-off"] = s.done(100)
        want[p + "done"] = s.mq01_done
        want[p + "debrief answer after the hand-off"] = ANSWER_CODE[s.debrief_answer]
        want[p + "reputation after the hand-off"] = s.rep

        self.compare(
            "CaseMurderAfterSaving", want, yes,
            fixture_checks={p + "the caravan and the Cutter lead stand in the quest's aliases"},
            set_by_handlers={31, 35, 100},  # the two deaths; the hand-off
            without_effect=set(),
            final=s)

    def test_scenario_9_deal(self):
        seq = SEQUENCES["CaseDeal"]
        p = "C9 "
        want, yes = {}, {}

        s = run(seq[:3])
        yes[p + "the ambush is live"] = s.caravan_state == m.LIVE
        s = run(["dunmore_deal"], start=s)
        self.assertTrue(s.done(33))
        want[p + "outcome after the deal"] = s.outcome
        want[p + "method after the deal"] = s.method
        yes[p + "the drover is dead after the deal"] = not s.abel_alive
        yes[p + "the caravan master is dead"] = not s.nell_alive
        yes[p + "the deal counts as a killing by the player"] = s.done(35)
        want[p + "cargo left on the wagon after the deal"] = cargo_left(s)

        s = run(["goto_town"], start=s)
        want[p + "caravan alive at Mercy on reaching town"] = s.alive_at_mercy
        yes[p + "the caravan master is in the town alias"] = s.hands_in_town and s.nell_alive
        yes[p + "the dead drover is not in the town alias"] = not (s.hands_in_town and s.abel_alive)

        s = run(["pritchard_handover"], start=s)
        want[p + "reputation after the hand-over"] = s.rep
        want[p + "debrief variant"] = VARIANT_CODE[s.debrief_variant]
        want[p + "mutual trust after the hand-over"] = s.mutual_trust

        s = run(["debrief_blame"], start=s)
        want[p + "debrief answer after blaming the Cutters"] = ANSWER_CODE[s.debrief_answer]
        want[p + "truth after blaming the Cutters"] = s.truth
        want[p + "accountability after blaming the Cutters"] = s.accountability

        s = run(["pritchard_handoff"], start=s)
        yes[p + "stage 100 set by the hand-off"] = s.done(100)
        want[p + "done"] = s.mq01_done
        want[p + "debrief answer after the hand-off"] = ANSWER_CODE[s.debrief_answer]
        want[p + "reputation after the hand-off"] = s.rep

        self.compare(
            "CaseDeal", want, yes,
            fixture_checks={p + "the caravan and the Cutter lead stand in the quest's aliases"},
            set_by_handlers={100},          # the deal's stage is set by the case, as the dialogue would
            without_effect=set(),
            final=s)

    def test_the_model_events_exist(self):
        for case, seq in SEQUENCES.items():
            for name in seq:
                self.assertIn(name, m.ALL_EVENTS, "%s: unknown event %s" % (case, name))


if __name__ == "__main__":
    unittest.main()
