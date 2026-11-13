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

The first version of the guards passed all of that and still had three gaps,
which a second reader found. The classes Shaken and AnyTwoThingsAtOnce are the
answer to that: they use the engine's third mode, in which the timing is
different for every seed (sim.Session, shake), run each question hundreds of
ways, and take each later correction out again to show that some run then
ends wrong.
"""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from sim import FRAME, Session, run_scenario
from test_sim import CURRENT_SCENARIOS, NATIVES, PLUGIN, ROOT, SCRIPTS, VANILLA, need_build, summary

sys.path.insert(0, str(ROOT / "tools" / "logic_model"))
import tlm_model as model                                         # noqa: E402

BEFORE_THE_GUARDS = "499104e"
# The guards as first written. An independent read found three gaps in them.
FIRST_GUARDS = "8b94566"


def guard_lines(session):
    """What the guards wrote to the script log: the only sign that one acted."""
    return [l for l in session.papyrus_log if l.startswith("TLM_MQ01: A24")]


_folders = {}


def scripts_with_quest(text, key):
    """The scripts as they are, with another text for the main quest's script."""
    if key not in _folders:
        folder = Path(tempfile.mkdtemp(prefix="tlm-quest-"))
        for p in SCRIPTS.glob("*.psc"):
            (folder / p.name).write_text(text if p.name == "MQ01Quest.psc" else p.read_text())
        _folders[key] = folder
    return _folders[key]


def scripts_with_the_quest_at(commit, test):
    have = subprocess.run(["git", "-C", str(ROOT), "cat-file", "-e", commit + "^{commit}"], capture_output=True)
    if have.returncode != 0:
        test.skipTest("commit %s is not in this copy of the repository" % commit)
    text = subprocess.run(["git", "-C", str(ROOT), "show", commit + ":scripts/Source/User/TLM/MQ01Quest.psc"],
                          capture_output=True, text=True, check=True).stdout
    return scripts_with_quest(text, commit)


def scripts_with_the_old_quest(test):
    return scripts_with_the_quest_at(BEFORE_THE_GUARDS, test)


def scripts_without(test, name, old, new):
    """The scripts as they are, with one of the later fixes taken out again."""
    text = (SCRIPTS / "MQ01Quest.psc").read_text()
    test.assertEqual(text.count(old), 1, "the text of the fix '%s' is no longer in MQ01Quest.psc; bring this test up to date" % name)
    return scripts_with_quest(text.replace(old, new), name)


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
                    s = run_scenario(n, SCRIPTS, PLUGIN, VANILLA, NATIVES, native_delay=delay)
                    got = summary(s)
                    self.assertEqual(got["failed"], 0, got["first_failure"])
                    self.assertTrue(got["result_line"])
                    # ... and it was the guard that made it one, not the death arriving first
                    self.assertEqual(guard_lines(s), ["TLM_MQ01: A24 the Cutter lead is already dead: a rescue, not an evasion"])

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
                self.assertEqual(len(guard_lines(s)), 1)
                self.assertIn("tenths of a second for another resolution to finish", guard_lines(s)[0])

    def test_without_the_guards_the_drover_lived_on_in_town(self):
        need_build(self)
        s = run_scenario(132, scripts_with_the_old_quest(self), PLUGIN, VANILLA, NATIVES, native_delay=FRAME)
        got = summary(s)
        self.assertEqual(overlap_reported(s), "True")
        self.assertIn("drover alive = 1, expected 0; drover in the town alias = 1, expected 0", got["first_failure"])


class EveryScenarioWhenCallsTakeTime(unittest.TestCase):
    def test_all_of_them_pass(self):
        need_build(self)
        numbers = CURRENT_SCENARIOS + [c["scenario"] for c in json.loads((ROOT / "tools" / "matrix_cases.json").read_text())["cases"]]
        for n in numbers:
            with self.subTest(scenario=n):
                s = run_scenario(n, SCRIPTS, PLUGIN, VANILLA, NATIVES, until=2000.0, native_delay=FRAME)
                got = summary(s)
                self.assertEqual(s.ended, "quit")
                self.assertEqual(got["failed"], 0, got["first_failure"])
                self.assertTrue(got["result_line"])

    def test_the_guards_do_nothing_where_one_thing_happens_at_a_time(self):
        """Ordinary play must be what it was before the guards: outside the
        four cases written to provoke them, no guard changes anything, whether
        calls take time or not."""
        need_build(self)
        numbers = CURRENT_SCENARIOS + [c["scenario"] for c in json.loads((ROOT / "tools" / "matrix_cases.json").read_text())["cases"]]
        for delay in (0.0, FRAME):
            acted = [n for n in numbers
                     if guard_lines(run_scenario(n, SCRIPTS, PLUGIN, VANILLA, NATIVES, until=2000.0, native_delay=delay))]
            self.assertEqual(acted, [129, 130, 131] + ([132] if delay else []))


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


class Shaken(unittest.TestCase):
    """The same questions with the timing shaken (sim.Session, shake): every
    call into the game takes 0 to 3 frames, a stage's handler begins 0 to 3
    frames after its stage reads as set, events come late, and ready threads
    run in any order; a different shake for every number. Harsher than the
    game, and still the script as it is must never end wrong.

    The first version of the guards passed everything above and was wrong in
    three places, which an independent read found and these shakes show. Each
    of the three later fixes is taken out again in turn, and each time some
    shake must end wrong: otherwise this test would not notice it missing."""

    def live(self, scripts, shake):
        s = Session(scripts, PLUGIN, VANILLA, NATIVES, shake=shake)
        s.enter_game()
        s.run(1.0)
        selftest = [i for i in s.quests["TLM_Core"].scripts if i.script.name == "TLM:SelfTest"][0]
        self.assertTrue(s.invoke("TLM_Core", "CaseBegin", [selftest, "X", "shaken"]))
        for step in ("DoStart", "DoTakeDispatch", "DoEnterAmbush"):
            s.invoke("TLM_Core", step, [])
        driver = [i for i in s.quests["TLM_Core"].scripts if i.script.name == "TLM:CaseDriver"][0]
        return s, driver, s.quests["TLM_MQ01"]

    def end(self, s, driver, mq):
        s.run(s.now + 30.0)
        alias = {a.name: a for a in mq.aliases.values()}
        return {
            "outcome": s.get_global("TLM_G_CaravanOutcome"),
            "method": s.get_global("TLM_G_CaravanMethod"),
            "drover alive": not driver.vars["abel"].dead,
            "drover in town": alias["CaravanDroverInTown"].ref is driver.vars["abel"],
            "cargo": sum(driver.vars["wagonstandin"].inventory.values()),
        }

    # Each of these returns True when the end is what the logic model says.

    def leaving_and_the_gate(self, scripts, shake, frames):
        """The player is beyond the evade distance, and the town stage is set
        `frames` frames around the moment the distance event arrives."""
        s, driver, mq = self.live(scripts, shake)
        driver.vars["center"].pos = (6000.0, 0.0, 0.0)
        s.check_distances()
        s.later(0.1 + frames * FRAME, "gate", lambda: s.n_quest_setstage(mq, None, 40), exact=True)
        got = self.end(s, driver, mq)
        return (got["outcome"], got["drover alive"], got["drover in town"], got["cargo"]) == (2, False, False, 0)

    def saved_and_evaded(self, scripts, shake, frames):
        s, driver, mq = self.live(scripts, shake)
        s.spawn(s.n_quest_setstage(mq, None, 31), "saved")
        s.later(frames * FRAME, "evaded", lambda: s.n_quest_setstage(mq, None, 32), exact=True)
        got = self.end(s, driver, mq)
        return (got["outcome"], got["drover alive"], got["cargo"]) in ((1, True, 3), (2, False, 0))

    def a_betrayal_and_the_timer(self, scripts, shake, frames):
        s, driver, mq = self.live(scripts, shake)
        s.n_actor_kill(driver.vars["nell"], None, s.player)
        quest_script = [i for i in mq.scripts if i.script.name == "TLM:MQ01Quest"][0]
        fn = quest_script.script.functions["evadetimerelapsed"]
        s.later(0.7 + frames * FRAME, "timer", lambda: s.call(quest_script, fn, []), exact=True)
        got = self.end(s, driver, mq)
        return (got["outcome"], got["method"], got["drover alive"], got["cargo"]) == (3, 2, False, 0)

    def the_lead_dead_and_the_gate(self, scripts, shake, frames):
        s, driver, mq = self.live(scripts, shake)
        s.n_actor_kill(driver.vars["lead"], None, s.player)
        s.later(frames * FRAME, "gate", lambda: s.n_quest_setstage(mq, None, 40), exact=True)
        got = self.end(s, driver, mq)
        return (got["outcome"], got["drover alive"], got["cargo"]) == (1, True, 3)

    def wrong(self, question, scripts, shakes, frames):
        return sum(1 for shake in shakes for f in frames if not question(scripts, shake, f))

    def test_the_script_as_it_is_never_ends_wrong(self):
        need_build(self)
        self.assertEqual(self.wrong(self.leaving_and_the_gate, SCRIPTS, range(40), range(-6, 13)), 0)
        self.assertEqual(self.wrong(self.saved_and_evaded, SCRIPTS, range(20), range(0, 12)), 0)
        self.assertEqual(self.wrong(self.a_betrayal_and_the_timer, SCRIPTS, range(200), range(0, 13)), 0)
        self.assertEqual(self.wrong(self.the_lead_dead_and_the_gate, SCRIPTS, range(20), range(0, 6)), 0)

    def test_every_scenario_passes_however_it_is_shaken(self):
        need_build(self)
        numbers = CURRENT_SCENARIOS + [c["scenario"] for c in json.loads((ROOT / "tools" / "matrix_cases.json").read_text())["cases"]]
        for shake in range(3):
            for n in numbers:
                with self.subTest(scenario=n, shake=shake):
                    s = run_scenario(n, SCRIPTS, PLUGIN, VANILLA, NATIVES, until=3000.0, shake=shake)
                    got = summary(s)
                    self.assertEqual(s.ended, "quit")
                    self.assertEqual(got["failed"], 0, got["first_failure"])

    def test_without_any_guard_all_four_end_wrong(self):
        need_build(self)
        old = scripts_with_the_old_quest(self)
        self.assertGreater(self.wrong(self.leaving_and_the_gate, old, range(10), range(-6, 13)), 0)
        self.assertGreater(self.wrong(self.saved_and_evaded, old, range(20), range(0, 12)), 0)
        self.assertGreater(self.wrong(self.a_betrayal_and_the_timer, old, range(20), range(0, 13)), 0)
        self.assertGreater(self.wrong(self.the_lead_dead_and_the_gate, old, range(5), range(0, 6)), 0)

    def test_the_first_version_of_the_guards_was_not_enough(self):
        need_build(self)
        first = scripts_with_the_quest_at(FIRST_GUARDS, self)
        self.assertGreater(self.wrong(self.leaving_and_the_gate, first, range(10), range(-6, 13)), 0)
        self.assertGreater(self.wrong(self.a_betrayal_and_the_timer, first, range(40), range(0, 13)), 0)

    def test_the_count_of_handlers_at_work_has_to_be_read_last(self):
        need_build(self)
        scripts = scripts_without(
            self, "the count read last",
            "((Outcome() == OUT_NONE && ResolutionStagesSet() > resolutionsBegun) || resolutionsAtWork > aiMine)",
            "(resolutionsAtWork > aiMine || (Outcome() == OUT_NONE && ResolutionStagesSet() > resolutionsBegun))")
        self.assertGreater(self.wrong(self.leaving_and_the_gate, scripts, range(60), range(-6, 13)), 0,
                           "taking this fix out changed nothing in these shakes: this test would not notice it missing")

    def test_the_town_stage_has_to_wait_again_after_its_own_resolution(self):
        need_build(self)
        scripts = scripts_without(
            self, "the second wait in the town stage",
            "\tWaitForResolutions(0)\n\tMoveHandToTown(Alias_CaravanMaster, Alias_CaravanMasterInTown)",
            "\tMoveHandToTown(Alias_CaravanMaster, Alias_CaravanMasterInTown)")
        self.assertGreater(self.wrong(self.leaving_and_the_gate, scripts, range(10), range(-6, 13)), 0,
                           "taking this fix out changed nothing in these shakes: this test would not notice it missing")

    def test_a_betrayal_that_is_not_first_has_to_wait_again(self):
        need_build(self)
        scripts = scripts_without(
            self, "the betrayal's second wait",
            "\tIf !firstResolution\n"
            "\t\t; Another resolution claimed the encounter while the outcome was being\n"
            "\t\t; read just now. It writes its outcome when it gets there; this one\n"
            "\t\t; has to write after it.\n"
            "\t\tWaitForResolutions(1)\n"
            "\tEndIf\n",
            "")
        self.assertGreater(self.wrong(self.a_betrayal_and_the_timer, scripts, range(200), range(0, 13)), 0,
                           "taking this fix out changed nothing in these shakes: this test would not notice it missing")


class AnyTwoThingsAtOnce(unittest.TestCase):
    """Every pair of thirteen things that can happen at a live ambush, the
    second a few frames after the first, with the timing shaken.

    What is asked is less than in the classes above and asked of far more: the
    end has to be one that the logic model gives for the two events in one
    order or the other (an event the model does not allow at its turn is left
    out of that order). So it does not say which of two near-simultaneous
    things should win; it says the result may never be a mixture of both, and
    a betrayal may never be lost.

    Compared: the outcome, the method, whether each caravan hand is alive and
    in the town alias, the cargo, and the "alive at Mercy" global. The stage
    flags are not: two resolution stages set in the same instant both read as
    set afterwards, though one was applied (amendment A24 says why that is
    left)."""

    TO_THE_AMBUSH = ["start", "take_dispatch", "goto_ambush"]
    EVENTS = ["player_kills_lead", "player_kills_cutter", "player_kills_nell", "player_kills_abel", "nell_dies_other",
              "evade_timer", "goto_wreck", "goto_town", "dunmore_talk", "dunmore_speech_success", "dunmore_deal",
              "dunmore_speech_fail", "attack_cutter"]

    def happens(self, event, s, driver, mq):
        """What the game does when the event happens, as a thread to start."""
        v = driver.vars

        def at_once(fn):
            def thread():
                fn()
                return
                yield
            return thread

        def nobody_kills_nell():
            s.n_actor_setprotected(v["nell"], None, False)
            s.n_actor_kill(v["nell"], None, None)

        def the_player_is_far_away():
            v["center"].pos = (6000.0, 0.0, 0.0)
            s.check_distances()

        quest_script = [i for i in mq.scripts if i.script.name == "TLM:MQ01Quest"][0]
        stage = {"goto_town": 40, "dunmore_speech_success": 31, "dunmore_deal": 33, "dunmore_speech_fail": 37}
        if event in stage:
            return lambda: s.n_quest_setstage(mq, None, stage[event])
        if event == "evade_timer":
            return lambda: s.call(quest_script, quest_script.script.functions["evadetimerelapsed"], [])
        return at_once({
            "player_kills_lead": lambda: s.n_actor_kill(v["lead"], None, s.player),
            "player_kills_cutter": lambda: s.n_actor_kill(v["cuttera"], None, s.player),
            "player_kills_nell": lambda: s.n_actor_kill(v["nell"], None, s.player),
            "player_kills_abel": lambda: s.n_actor_kill(v["abel"], None, s.player),
            "nell_dies_other": nobody_kills_nell,
            "goto_wreck": the_player_is_far_away,
            "dunmore_talk": lambda: setattr(v["lead"], "talking_to_player", True),
            "attack_cutter": lambda: s.n_actor_startcombat(v["lead"], None, s.player),
        }[event])

    def in_the_model(self, events):
        st = model.run(self.TO_THE_AMBUSH)
        in_town = (0, 0)
        for e in events:
            try:
                after = model.apply(st, e)
            except model.NotAvailable:
                continue
            if after.done(40) and not st.done(40):
                in_town = (int(after.nell_alive), int(after.abel_alive))
            st = after
        return (st.outcome, st.method, int(st.nell_alive), int(st.abel_alive), 3 if st.cargo == "intact" else 0,
                in_town[0], in_town[1], st.alive_at_mercy)

    def in_the_stand_in(self, scripts, shake, first, second, frames):
        s = Session(scripts, PLUGIN, VANILLA, NATIVES, shake=shake)
        s.enter_game()
        s.run(1.0)
        selftest = [i for i in s.quests["TLM_Core"].scripts if i.script.name == "TLM:SelfTest"][0]
        self.assertTrue(s.invoke("TLM_Core", "CaseBegin", [selftest, "X", "two things at once"]))
        for step in ("DoStart", "DoTakeDispatch", "DoEnterAmbush"):
            s.invoke("TLM_Core", step, [])
        driver = [i for i in s.quests["TLM_Core"].scripts if i.script.name == "TLM:CaseDriver"][0]
        mq = s.quests["TLM_MQ01"]
        s.later(0.0, first, self.happens(first, s, driver, mq), exact=True)
        s.later(frames * FRAME, second, self.happens(second, s, driver, mq), exact=True)
        s.run(s.now + 40.0)
        self.assertEqual([l for l in s.papyrus_log if l.startswith("error:")], [])
        alias = {a.name: a for a in mq.aliases.values()}
        v = driver.vars
        return (s.get_global("TLM_G_CaravanOutcome"), s.get_global("TLM_G_CaravanMethod"),
                int(not v["nell"].dead), int(not v["abel"].dead), sum(v["wagonstandin"].inventory.values()),
                int(alias["CaravanMasterInTown"].ref is v["nell"]), int(alias["CaravanDroverInTown"].ref is v["abel"]),
                s.get_global("TLM_G_CaravanAliveAtMercy"))

    def neither_order(self, scripts, shakes, frames):
        """The pairs that ended, at least once, as neither order ends in the model."""
        found = {}
        for first in self.EVENTS:
            for second in self.EVENTS:
                if first == second:
                    continue
                allowed = {self.in_the_model([first, second]), self.in_the_model([second, first])}
                for shake in shakes:
                    for f in frames:
                        got = self.in_the_stand_in(scripts, shake, first, second, f)
                        if got not in allowed:
                            found.setdefault((first, second), []).append((shake, f, got))
        return found

    def test_the_end_is_always_what_one_of_the_two_orders_gives(self):
        need_build(self)
        found = self.neither_order(SCRIPTS, range(4), range(0, 5))
        self.assertEqual(found, {})

    def test_before_the_guards_it_was_not(self):
        need_build(self)
        found = self.neither_order(scripts_with_the_old_quest(self), range(2), range(0, 3))
        # the drover alive in town, and a rescue with the wagon looted, among others
        self.assertIn(("goto_wreck", "goto_town"), found)
        self.assertIn(("dunmore_deal", "dunmore_speech_success"), found)

    def test_nor_with_the_guards_as_first_written(self):
        need_build(self)
        found = self.neither_order(scripts_with_the_quest_at(FIRST_GUARDS, self), range(2), range(0, 3))
        self.assertIn(("goto_wreck", "goto_town"), found)


if __name__ == "__main__":
    unittest.main()
