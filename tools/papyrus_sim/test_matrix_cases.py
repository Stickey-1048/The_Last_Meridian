"""Tests of the generated matrix cases (tools/gen_matrix_cases.py).

The expected values in the cases are computed by the logic model, so there is
nothing to compare them with here. What is tested is the rest:

  - the files on disk are what the generator writes now;
  - every row of the two test matrices is either played by a case or listed
    with the reason it cannot be;
  - the stages the driver looks at are the plugin's stages;
  - every case passes when the real scripts run in the stand-in engine;
  - a rule changed in a quest script, and a number changed in a case, are
    each reported, with the case, the step and the thing that differs.
"""
import json
import re
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import gen_matrix_cases as gen                                   # noqa: E402
from sim import run_scenario                                     # noqa: E402
from test_sim import NATIVES, PLUGIN, SCRIPTS, VANILLA, need_build, summary   # noqa: E402

MATRIX_TESTS = [ROOT / "tools" / "logic_model" / "test_mq01_matrix.py",
                ROOT / "tools" / "logic_model" / "test_sq01_matrix.py"]


def matrix_rows():
    rows = set()
    for path in MATRIX_TESTS:
        rows |= set(re.findall(r"def test_([TS]\d+[a-z]?)_", path.read_text()))
    return rows


class TheGeneratedFiles(unittest.TestCase):
    def test_they_are_what_the_generator_writes_now(self):
        psc, data = gen.generate()
        self.assertEqual(gen.OUT_PSC.read_text(), psc, "run:  python3 tools/gen_matrix_cases.py")
        self.assertEqual(gen.OUT_JSON.read_text(), data, "run:  python3 tools/gen_matrix_cases.py")

    def test_every_row_of_the_matrices_is_played_or_has_a_reason(self):
        rows = matrix_rows()
        self.assertGreater(len(rows), 50)
        played = {label.split()[0] for _n, labels, _t, _s in gen.CASES for label in labels}
        self.assertEqual(played - rows, set(), "a case names a row the matrices do not have")
        self.assertEqual(set(gen.NOT_RUN) - rows, set(), "NOT_RUN names a row the matrices do not have")
        self.assertEqual(played & set(gen.NOT_RUN), set(), "a row is both played and listed as not run")
        self.assertEqual(rows - played - set(gen.NOT_RUN), set(), "rows with neither a case nor a reason")

    def test_scenario_numbers_do_not_collide_with_the_hand_written_ones(self):
        numbers = [n for n, _l, _t, _s in gen.CASES]
        self.assertEqual(len(numbers), len(set(numbers)))
        self.assertTrue(all(n >= 100 for n in numbers))

    def test_the_stages_the_driver_looks_at_are_the_plugins_stages(self):
        need_build(self)
        plugin = json.loads(PLUGIN.read_text())
        stages = {q["EditorId"]: [s["Index"] for s in q["Stages"]] for q in plugin["Quests"]}
        self.assertEqual(gen.MQ_STAGES, stages["TLM_MQ01"])
        self.assertEqual(gen.SQ_STAGES, stages["TLM_SQ01"])
        driver = (SCRIPTS / "CaseDriver.psc").read_text()
        self.assertEqual([int(n) for n in re.findall(r"StageWord\(TLM_MQ01, (\d+)\)", driver)], gen.MQ_STAGES)
        self.assertEqual([int(n) for n in re.findall(r"StageWord\(TLM_SQ01, (\d+)\)", driver)], gen.SQ_STAGES)

    def test_an_attempt_the_model_allows_is_refused(self):
        with self.assertRaises(gen.Bad):
            gen.build_case(900, ["T00"], "x", gen.steps("start", gen.attempt("take_dispatch")), 120, 3)

    def test_an_event_the_model_does_not_allow_is_refused(self):
        with self.assertRaises(gen.Bad):
            gen.build_case(900, ["T00"], "x", gen.steps("start", "pritchard_handover"), 120, 3)


class TheCasesInTheStandIn(unittest.TestCase):
    def test_every_case_passes_and_makes_all_its_checks(self):
        need_build(self)
        cases = json.loads(gen.OUT_JSON.read_text())["cases"]
        self.assertEqual(len(cases), len(gen.CASES))
        for case in cases:
            with self.subTest(scenario=case["scenario"]):
                s = run_scenario(case["scenario"], SCRIPTS, PLUGIN, VANILLA, NATIVES, until=900.0)
                got = summary(s)
                self.assertEqual(s.ended, "quit")
                self.assertEqual(got["failed"], 0, got["first_failure"])
                self.assertEqual(got["passed"], case["checks"])
                self.assertEqual([l for l in s.papyrus_log if l.startswith("error:")], [])
                self.assertEqual(s.message_boxes, [])

    def changed(self, file_name, old, new):
        folder = Path(tempfile.mkdtemp(prefix="tlm-changed-"))
        for p in SCRIPTS.glob("*.psc"):
            text = p.read_text()
            if p.name == file_name:
                self.assertGreaterEqual(text.count(old), 1, "the text to change is no longer in %s" % file_name)
                text = text.replace(old, new, 1)
            (folder / p.name).write_text(text)
        return folder

    def test_a_rule_changed_in_the_side_quest_is_reported(self):
        need_build(self)
        folder = self.changed("SQ01Quest.psc", "\t\tTLM_MutualTrust.Mod(1)\n\tElseIf aiOutcome == SQ_POSTED_HASKELL",
                              "\tElseIf aiOutcome == SQ_POSTED_HASKELL")
        got = summary(run_scenario(209, folder, PLUGIN, VANILLA, NATIVES))
        self.assertEqual(got["failed"], 1)
        self.assertEqual(got["first_failure"], "C209 #6 sq_post_yard: the four counters: mutual trust = 0, expected 1;")

    def test_a_rule_changed_in_the_main_quest_is_reported(self):
        need_build(self)
        folder = self.changed(
            "MQ01Quest.psc",
            "\tTLM_G_CaravanOutcome.SetValueInt(OUT_EXPLOITED)\n\tTLM_G_CaravanMethod.SetValueInt(METHOD_BETRAYAL)\n\tIf firstResolution",
            "\tIf firstResolution\n\t\tTLM_G_CaravanOutcome.SetValueInt(OUT_EXPLOITED)\n\t\tTLM_G_CaravanMethod.SetValueInt(METHOD_BETRAYAL)\n\tEndIf\n\tIf firstResolution")
        got = summary(run_scenario(117, folder, PLUGIN, VANILLA, NATIVES))
        self.assertGreaterEqual(got["failed"], 1)
        self.assertEqual(got["first_failure"], "C117 #5 player_kills_nell: main quest: outcome = 1, expected 3; method = 0, expected 2;")

    def test_a_stage_the_model_does_not_expect_is_reported(self):
        """What the model used to say about the hand-over, put into the script:
        the comparison of stages shows it."""
        need_build(self)
        folder = self.changed(
            "MQ01Quest.psc",
            "\tIf player.GetItemCount(DispatchItem) > 0\n\t\tplayer.RemoveItem(DispatchItem, 1, true)\n\tEndIf\n\tSetObjectiveCompleted(20)",
            "\tIf player.GetItemCount(DispatchItem) > 0\n\t\tplayer.RemoveItem(DispatchItem, 1, true)\n\tElse\n\t\tSetStage(900)\n\tEndIf\n\tSetObjectiveCompleted(20)")
        got = summary(run_scenario(126, folder, PLUGIN, VANILLA, NATIVES))
        self.assertEqual(got["failed"], 1)
        self.assertEqual(got["first_failure"],
                         "C126 #5 pritchard_handover: main quest: stages = 10 20 34 40 50 900, expected 10 20 34 40 50;")

    def test_a_counter_that_should_go_below_zero_is_checked(self):
        """Blaming the Cutters costs truth. An earlier driver took every
        negative expectation to mean "not looked at", so this was never seen."""
        need_build(self)
        folder = self.changed("MQ01Quest.psc", "\t\tElseIf aiAnswer == ANS_BLAME\n\t\t\tTLM_Truth.Mod(-1)",
                              "\t\tElseIf aiAnswer == ANS_BLAME\n\t\t\tTLM_Truth.Mod(0)")
        got = summary(run_scenario(113, folder, PLUGIN, VANILLA, NATIVES))
        self.assertGreaterEqual(got["failed"], 1)
        self.assertEqual(got["first_failure"], "C113 #7 debrief_blame: the four counters: truth = 0, expected -1;")

    def test_the_sign_for_not_looked_at_is_the_drivers(self):
        driver = (SCRIPTS / "CaseDriver.psc").read_text()
        self.assertIn("int SKIP = %d Const" % gen.SKIP, driver)
        self.assertLess(gen.SKIP, -100)

    def test_every_expected_value_is_really_compared(self):
        """Each number and each list of stages in a case's last step is changed
        in turn; each change must make the case fail. A check that compared
        nothing would pass here with the wrong number."""
        need_build(self)
        source = (SCRIPTS / "MatrixCases.psc").read_text()
        tried = 0
        for scenario, calls in ((112, ("ExpectMain", "ExpectWorld", "ExpectMetrics")), (212, ("ExpectSide",)),
                                (119, ("ExpectWorld",))):
            start = source.index("Function Case%d(" % scenario)
            end = source.index("EndFunction", start)
            body = source[start:end]
            for call in calls:
                # the last such check of the case; for scenario 119 the last
                # one that looks at everything, combat included
                wanted = [l for l in body.split("\n") if l.startswith("\tcaseDriver.%s(" % call)]
                whole = [l for l in wanted if str(gen.SKIP) not in l]
                line = (whole if scenario == 119 else wanted)[-1]
                at = body.rindex(line)
                args = line[line.index("(") + 1:-1].split(", ")
                for i, arg in enumerate(args):
                    if arg == str(gen.SKIP):
                        continue
                    changed = list(args)
                    changed[i] = arg[:-1] + ' 999"' if arg.startswith('"') else str(int(arg) + 1)
                    new_line = line[:line.index("(") + 1] + ", ".join(changed) + ")"
                    new_body = body[:at] + new_line + body[at + len(line):]
                    folder = Path(tempfile.mkdtemp(prefix="tlm-arg-"))
                    for p in SCRIPTS.glob("*.psc"):
                        text = p.read_text()
                        if p.name == "MatrixCases.psc":
                            text = source[:start] + new_body + source[end:]
                        (folder / p.name).write_text(text)
                    got = summary(run_scenario(scenario, folder, PLUGIN, VANILLA, NATIVES))
                    self.assertEqual(got["failed"], 1, "scenario %d, %s, value %d (%s): the change was not noticed"
                                     % (scenario, call, i + 1, arg))
                    tried += 1
        self.assertEqual(tried, 10 + 9 + 4 + 13 + 10)

    def test_a_number_changed_in_a_case_is_reported(self):
        need_build(self)
        folder = self.changed("MatrixCases.psc", "caseDriver.ExpectMetrics(0, 0, 0, 1)", "caseDriver.ExpectMetrics(0, 0, 0, 2)")
        got = summary(run_scenario(104, folder, PLUGIN, VANILLA, NATIVES))
        self.assertEqual(got["failed"], 1)
        self.assertEqual(got["first_failure"], "C104 #6 pritchard_handover: the four counters: mutual trust = 1, expected 2;")


if __name__ == "__main__":
    unittest.main()
