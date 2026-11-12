"""Tests of amendment A24: the quest script when the game does not keep to the
logic model's "one event at a time".

In the logic model an event is over before the next begins. In the game

  - a death is announced about a second after it happens, so the timer, the
    distance watch or the town stage can arrive in between; and
  - every handler runs on a thread of its own and gives other threads a turn
    at each call it makes into the game, so two handlers can be at work at
    once.

The second cannot happen in the stand-in engine's ordinary mode, where nothing
takes time. These tests use its other mode, in which every call out of a
script takes one frame (sim.Session, native_delay). That mode is a way of
provoking overlaps; it is not a measurement of the game.

Each test is run twice: with the quest script as it is, which must come out
where the logic model does, and with the quest script as it was when the whole
matrix passed in the game (commit 499104e, before the guards), which must NOT.
The second half is what shows that the cases can see the fault.
"""
import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from sim import Session, run_scenario
from test_sim import NATIVES, PLUGIN, ROOT, SCRIPTS, VANILLA, need_build, summary

FRAME = 1.0 / 60.0
BEFORE_THE_GUARDS = "499104e"


def scripts_with_the_old_quest(test):
    have = subprocess.run(["git", "-C", str(ROOT), "cat-file", "-e", BEFORE_THE_GUARDS + "^{commit}"], capture_output=True)
    if have.returncode != 0:
        test.skipTest("commit %s is not in this copy of the repository" % BEFORE_THE_GUARDS)
    folder = Path(tempfile.mkdtemp(prefix="tlm-noguards-"))
    for p in SCRIPTS.glob("*.psc"):
        text = p.read_text()
        if p.name == "MQ01Quest.psc":
            text = subprocess.run(["git", "-C", str(ROOT), "show", BEFORE_THE_GUARDS + ":scripts/Source/User/TLM/MQ01Quest.psc"],
                                  capture_output=True, text=True, check=True).stdout
        (folder / p.name).write_text(text)
    return folder


def overlap_reported(session):
    lines = [l for l in session.user_logs.get("TLM", []) if "was still at work" in l]
    return lines[-1].rsplit(": ", 1)[1] if lines else None


class ADeathAnnouncedLate(unittest.TestCase):
    """Cases 129 to 131: the Cutter lead is dead, and something that would
    resolve the ambush as "evaded" arrives before OnDeath does."""

    def test_with_the_guards_it_is_a_rescue(self):
        need_build(self)
        for n in (129, 130, 131):
            for delay in (0.0, FRAME):
                with self.subTest(scenario=n, delay=delay):
                    got = summary(run_scenario(n, SCRIPTS, PLUGIN, VANILLA, NATIVES, native_delay=delay))
                    self.assertEqual(got["failed"], 0, got["first_failure"])
                    self.assertTrue(got["result_line"])

    def test_without_the_guards_it_was_recorded_as_evaded(self):
        need_build(self)
        old = scripts_with_the_old_quest(self)
        for n in (129, 130, 131):
            with self.subTest(scenario=n):
                got = summary(run_scenario(n, old, PLUGIN, VANILLA, NATIVES))
                self.assertGreater(got["failed"], 0)
                self.assertIn("outcome = 2, expected 1", got["first_failure"])


class TwoHandlersAtOnce(unittest.TestCase):
    """Case 132: the town stage is set while the evade stage is being handled."""

    def test_the_overlap_is_only_provoked_when_calls_take_time(self):
        need_build(self)
        self.assertEqual(overlap_reported(run_scenario(132, SCRIPTS, PLUGIN, VANILLA, NATIVES)), "False")
        self.assertEqual(overlap_reported(run_scenario(132, SCRIPTS, PLUGIN, VANILLA, NATIVES, native_delay=FRAME)), "True")

    def test_with_the_guards_the_drover_is_dead_and_not_in_town(self):
        need_build(self)
        for delay in (FRAME, 1.0 / 30.0, 1.0 / 144.0):
            with self.subTest(delay=delay):
                s = run_scenario(132, SCRIPTS, PLUGIN, VANILLA, NATIVES, native_delay=delay)
                got = summary(s)
                self.assertEqual(overlap_reported(s), "True")
                self.assertEqual(got["failed"], 0, got["first_failure"])

    def test_without_the_guards_the_drover_lived_on_in_town(self):
        need_build(self)
        s = run_scenario(132, scripts_with_the_old_quest(self), PLUGIN, VANILLA, NATIVES, native_delay=FRAME)
        got = summary(s)
        self.assertEqual(overlap_reported(s), "True")
        self.assertIn("drover alive = 1, expected 0; drover in the town alias = 1, expected 0", got["first_failure"])


class EveryScenarioWhenCallsTakeTime(unittest.TestCase):
    def test_all_of_them_pass(self):
        need_build(self)
        numbers = list(range(1, 10)) + [c["scenario"] for c in json.loads((ROOT / "tools" / "matrix_cases.json").read_text())["cases"]]
        for n in numbers:
            with self.subTest(scenario=n):
                s = run_scenario(n, SCRIPTS, PLUGIN, VANILLA, NATIVES, until=2000.0, native_delay=FRAME)
                got = summary(s)
                self.assertEqual(s.ended, "quit")
                self.assertEqual(got["failed"], 0, got["first_failure"])
                self.assertTrue(got["result_line"])


class TwoResolutionsAtOnce(unittest.TestCase):
    """Driven from here: a live ambush, then two things that each resolve it,
    a few frames apart, with every call taking a frame."""

    def live_ambush(self, scripts, newest_first=False):
        s = Session(scripts, PLUGIN, VANILLA, NATIVES, native_delay=FRAME)
        s.newest_first = newest_first
        s.enter_game()
        s.run(1.0)
        selftest = [i for i in s.quests["TLM_Core"].scripts if i.script.name == "TLM:SelfTest"][0]
        self.assertTrue(s.invoke("TLM_Core", "CaseBegin", [selftest, "X", "two resolutions at once"]))
        for step in ("DoStart", "DoTakeDispatch", "DoEnterAmbush"):
            s.invoke("TLM_Core", step, [])
        driver = [i for i in s.quests["TLM_Core"].scripts if i.script.name == "TLM:CaseDriver"][0]
        return s, driver, s.quests["TLM_MQ01"]

    def state(self, s, driver):
        cargo = driver.vars["wagonstandin"]
        return {
            "outcome": s.get_global("TLM_G_CaravanOutcome"),
            "method": s.get_global("TLM_G_CaravanMethod"),
            "drover alive": not driver.vars["abel"].dead,
            "cargo": sum(cargo.inventory.values()),
        }

    def saved_and_evaded(self, scripts, frames_apart, saved_first, newest_first=False):
        s, driver, mq = self.live_ambush(scripts, newest_first)
        first, second = (31, 32) if saved_first else (32, 31)
        s.spawn(s.n_quest_setstage(mq, None, first), "first")
        s.later(frames_apart * FRAME, "second", lambda: s.n_quest_setstage(mq, None, second))
        s.run(s.now + 20.0)
        return self.state(s, driver)

    WHOLE = ({"outcome": 1, "method": 0, "drover alive": True, "cargo": 3},     # saved
             {"outcome": 2, "method": 0, "drover alive": False, "cargo": 0})    # evaded

    def test_saved_and_evaded_at_once_end_as_one_or_the_other(self):
        need_build(self)
        for frames in range(0, 25):
            for saved_first in (True, False):
                for newest_first in (False, True):
                    with self.subTest(frames_apart=frames, saved_first=saved_first, newest_first=newest_first):
                        self.assertIn(self.saved_and_evaded(SCRIPTS, frames, saved_first, newest_first), self.WHOLE)

    def test_without_the_guards_they_could_end_as_a_mixture(self):
        need_build(self)
        old = scripts_with_the_old_quest(self)
        mixtures = 0
        for frames in range(0, 25):
            for saved_first in (True, False):
                for newest_first in (False, True):
                    if self.saved_and_evaded(old, frames, saved_first, newest_first) not in self.WHOLE:
                        mixtures += 1
        self.assertGreater(mixtures, 0, "the old script never mixed the two; this test shows nothing")

    def betrayal_and_evaded(self, scripts, frames, newest_first=False):
        """The caravan master is killed by the player; the evade timer's
        function is called `frames` frames after the kill. The death is
        announced 0.7 s (42 frames) after it."""
        s, driver, mq = self.live_ambush(scripts, newest_first)
        s.n_actor_kill(driver.vars["nell"], None, s.player)
        quest_script = [i for i in mq.scripts if i.script.name == "TLM:MQ01Quest"][0]
        fn = quest_script.script.functions["evadetimerelapsed"]
        s.later(frames * FRAME, "timer", lambda: s.call(quest_script, fn, []))
        s.run(s.now + 20.0)
        return self.state(s, driver)

    BETRAYED = {"outcome": 3, "method": 2, "drover alive": False, "cargo": 0}

    def test_a_betrayal_and_the_timer_at_once_end_as_betrayal(self):
        need_build(self)
        for frames in range(20, 70):
            for newest_first in (False, True):
                with self.subTest(frames_after_the_kill=frames, newest_first=newest_first):
                    self.assertEqual(self.betrayal_and_evaded(SCRIPTS, frames, newest_first), self.BETRAYED)

    def test_without_the_guards_the_betrayal_could_be_lost(self):
        need_build(self)
        old = scripts_with_the_old_quest(self)
        lost = sum(1 for frames in range(20, 70) for newest_first in (False, True)
                   if self.betrayal_and_evaded(old, frames, newest_first) != self.BETRAYED)
        self.assertGreater(lost, 0, "the old script never lost the betrayal; this test shows nothing")


if __name__ == "__main__":
    unittest.main()
