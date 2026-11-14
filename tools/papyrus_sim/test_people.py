"""Tests of self-test scenario 11, people the plugin places, and of the
stand-in's rules for such people.

WHAT THE GAME HAS SHOWN, AND WHAT IT HAS NOT. One thing: on 2026-11-13 the
game's settler, placed by the plugin and then enabled, did not stay where it
was put (docs/design/VERIFY_LOG.md, the thirteenth run). Everything else the
stand-in does with a placed person is [documented] at best (activating
something sends OnActivate to the scripts on its alias) and otherwise
[assumed]: above all that a person of the plugin's own with no packages
stays. That is the very thing scenario 11 asks the game, so a pass here says
only that the scenario's script, the plugin the builder writes and those
readings agree with each other.

What the tests are for meanwhile:
  - the scenario runs to its end against the plugin as built, however the
    timing falls, and scores what it should;
  - the scenario notices each thing it is there to notice: every test in
    WhatTheScenarioCatches breaks one thing and names the check that must
    then fail;
  - everything scored is written before anything that is only reported: a
    call that never comes back, or comes back slowly, after the scored part
    leaves the eight checks standing and is written down as a fact;
  - the stand-in's rules for placed people do what sim.py says they do.

Nine functions are called by the scenario that the project had not called
before. Four only read something and are used in the scored part as well
(GetCurrentRealTime, sqrt, GetCurrentPackage, GetSitState). The five that
move or hold something come after it.
"""
import math
import re
import tempfile
import unittest
from pathlib import Path

from sim import ENABLE_SECONDS, FRAME, PUT_BACK_STEP, STRAY_BY, Actor, Session, run_scenario, to_string
from test_placed import SKELETON, alias, changed_plugin, errors, need_trial_build, placed, trial
from test_sim import NATIVES, PLUGIN, SCRIPTS, VANILLA, need_build, summary

OWN, BARE, ON_FLOOR, SETTLER = ("TLM_REF_TrialPersonOwn", "TLM_REF_TrialPersonBare", "TLM_REF_TrialSettlerOnFloor", "TLM_REF_TrialPerson")
CHECKS = 8
STRAY = math.dist((0.0, 0.0, 0.0), STRAY_BY)            # height included
STRAY_FLAT = math.hypot(STRAY_BY[0], STRAY_BY[1])
STEP = math.dist((0.0, 0.0, 0.0), PUT_BACK_STEP)       # how far a person put back has gone a second later

STAYED = ("people: stayed within 64 units of where it was placed for six seconds: the person of the plugin's own = Yes, "
          "the person with no default package list = Yes, the game's settler on the same spot = No, the game's settler of scenario 10 = No")
WITHIN = "people: the person of the plugin's own is within 64 units of where it was placed, six seconds after it was enabled: expected true, was false"
TALK = "people: activating the person sets stage 30 (TLM:MessageStageAlias on its alias): expected true, was false"
GONE = "this experiment did not come back, and the scenario was ended here: "


def failures(s):
    return [l[len("FAIL"):].strip() for l in s.user_logs["TLM"] if l.startswith("FAIL")]


def steps(s):
    return [l[len("STEP"):].strip() for l in s.user_logs["TLM"] if l.startswith("STEP")]


def play(prepare=None, change=None, until=1500.0):
    """Scenario 11 with something about the plugin or about the game's answers changed."""
    s = Session(SCRIPTS, changed_plugin(change) if change else PLUGIN, VANILLA, NATIVES)
    if prepare:
        prepare(s)
    s.set_global("TLM_G_DevScenario", 11)
    s.enter_game()
    s.run(until)
    return s


class ThePeopleScenarioAsBuilt(unittest.TestCase):
    def test_it_passes(self):
        need_trial_build(self)
        s = run_scenario(11, SCRIPTS, PLUGIN, VANILLA, NATIVES, until=900.0)
        got = summary(s)
        self.assertEqual(got["failed"], 0, got["first_failure"])
        self.assertEqual(got["passed"], CHECKS)
        self.assertEqual(s.ended, "quit", "the scenario did not close the game by itself")
        self.assertEqual(errors(s), [])
        self.assertEqual(s.message_boxes, [])
        # the line a person shows when spoken to, once
        self.assertEqual(s.messages_shown, ["TLM_MSG_TrialTalk"])
        self.assertIn(STAYED, got["info"])
        # the two real quests were never touched
        self.assertEqual((got["main_stage_events"], got["side_stage_events"]), (0, 0))
        self.assertFalse(s.quests["TLM_MQ01"].running or s.quests["TLM_SQ01"].running)
        # nobody is left standing about
        self.assertTrue(all(s.placed[x].disabled for x in (OWN, BARE, ON_FLOOR, SETTLER)))

    def test_it_passes_however_the_timing_falls(self):
        need_trial_build(self)
        for how in [dict(native_delay=FRAME)] + [dict(shake=n) for n in range(25)]:
            with self.subTest(**how):
                s = run_scenario(11, SCRIPTS, PLUGIN, VANILLA, NATIVES, until=3000.0, **how)
                got = summary(s)
                self.assertEqual((got["failed"], got["passed"], s.ended), (0, CHECKS, "quit"), got["first_failure"])
                self.assertEqual(errors(s), [])

    def test_each_person_is_watched_alone(self):
        """One at a time, or what one does could be put down to another. Three
        of the four share a spot, so that they differ in the actor and in
        nothing else, and must never be there together."""
        need_trial_build(self)
        s = run_scenario(11, SCRIPTS, PLUGIN, VANILLA, NATIVES, until=900.0)
        about = []
        for step in steps(s):
            if step.startswith("enabling "):
                self.assertEqual(about, [], "%s while somebody else is still enabled" % step)
                about.append(step[len("enabling "):].replace(" again", "").replace(", with the player standing elsewhere", ""))
            elif step.startswith("disabling "):
                self.assertEqual(about, [step[len("disabling "):]])
                about = []
        self.assertEqual(about, [])
        own, bare, floor, settler = (s.placed[x] for x in (OWN, BARE, ON_FLOOR, SETTLER))
        self.assertEqual(own.editor_pos, bare.editor_pos)
        self.assertEqual(own.editor_pos, floor.editor_pos)
        self.assertNotEqual(own.editor_pos, settler.editor_pos)

    def test_everything_scored_is_written_before_anything_that_is_only_reported(self):
        need_trial_build(self)
        s = run_scenario(11, SCRIPTS, PLUGIN, VANILLA, NATIVES, until=900.0)
        lines = s.user_logs["TLM"]
        last = max(i for i, l in enumerate(lines) if l.startswith(("PASS", "FAIL")))
        self.assertEqual(lines[last], "PASS  people: the quest is completed by its last stage")
        self.assertEqual(sum(1 for l in lines[:last + 1] if l.startswith("PASS")), CHECKS)
        # before it: only the person of the plugin's own was ever enabled
        self.assertEqual([l for l in lines[:last] if l.startswith("STEP  enabling ")], ["STEP  enabling the person of the plugin's own"])
        # after it: the other three, and every step that calls one of the five functions that move or hold something
        after = [l[len("STEP  "):] for l in lines[last:] if l.startswith("STEP  ")]
        self.assertEqual(sum(1 for x in after if x.startswith("enabling ")), 3 + 2 + 2 + 1)
        self.assertEqual(sum(1 for x in after if x.startswith("experiment: ")), 2 * 2 + 2 * 4 + 2 * 1 + 1)
        self.assertFalse([l for l in lines[:last] if l.startswith("STEP  experiment: ")])

    def test_every_step_after_the_scored_part_is_one_that_may_not_come_back(self):
        """Read from the script itself: after the line that says nothing below
        is scored, and in the functions only called from there, every Step is
        told that it is one the watchdog reports as a fact. Watch, which is
        used on both sides of the line, is told by whoever calls it."""
        text = (SCRIPTS / "PlacedPeople.psc").read_text()
        run = text[text.index("Function Run("):text.index("EndFunction", text.index("Function Run("))]
        self.assertEqual(run.count("; ==== Nothing below is scored."), 1)
        before, after = run.split("; ==== Nothing below is scored.")
        rest = [after]
        for name in ("PutBack", "WithoutAI", "Probe"):
            start = text.index("Function %s(" % name)
            rest.append(text[start:text.index("EndFunction", start)])
        unflagged = [l.strip() for part in rest for l in part.splitlines() if "akTest.Step(" in l and not l.rstrip().endswith(", true)")]
        self.assertEqual(unflagged, [])
        watched_after = [l for l in after.splitlines() if "Watch(akTest" in l]
        watched_before = [l for l in before.splitlines() if "Watch(akTest" in l]
        self.assertEqual((len(watched_before), len(watched_after)), (1, 4))
        self.assertTrue(all(re.search(r"Watch\(akTest, [^()]*, true\)", l) for l in watched_after), watched_after)
        self.assertTrue(all(re.search(r"Watch\(akTest, [^()]*, false\)", l) for l in watched_before), watched_before)
        self.assertFalse([l for l in after.splitlines() if "akTest.Check" in l])
        watch = text[text.index("float Function Watch("):text.index("EndFunction", text.index("float Function Watch("))]
        self.assertTrue(all("abAfterScoring)" in l for l in watch.splitlines() if "akTest.Step(" in l))

    def test_a_call_that_never_comes_back_after_the_scored_part_leaves_the_eight_standing(self):
        """Whichever it is. The watchdog writes it down as a fact about the game, and the result is still written."""
        need_trial_build(self)

        def reach(s):
            s.activate_reach = 300.0           # so that the player is moved, and has to be brought back
        cases = [
            ("the first Enable of the person with no default package list", {("enable", BARE): None}, {}, None,
             "enabling the person with no default package list"),
            ("the second Enable of the game's settler", {("enable", ON_FLOOR): None}, {("enable", ON_FLOOR): 2}, None,
             "enabling the game's settler on the same spot again"),
            ("moving a person back", {("movetomyeditorlocation", ON_FLOOR): None}, {}, None,
             "experiment: moving the game's settler on the same spot back to where the plugin placed it"),
            ("moving a restrained person back", {("movetomyeditorlocation", ON_FLOOR): None}, {("movetomyeditorlocation", ON_FLOOR): 2}, None,
             "experiment: restraining the game's settler on the same spot and moving it back"),
            ("moving a person back with its AI off", {("movetomyeditorlocation", ON_FLOOR): None}, {("movetomyeditorlocation", ON_FLOOR): 3}, None,
             "experiment: turning the AI of the game's settler on the same spot off and moving it back"),
            ("setting a marker down", {("setposition", "made at run time"): None}, {}, None,
             "experiment: moving the marker to where the game's settler of scenario 10 was placed"),
            ("asking for the navigation mesh", {("movetonearestnavmeshlocation", "made at run time"): None}, {}, None,
             "experiment: moving the marker to the nearest place on the navigation mesh, from where the game's settler of scenario 10 was placed"),
            ("setting the player down elsewhere", {("setposition", "player"): None}, {}, None,
             "experiment: moving the player to where the person of the plugin's own was placed"),
            ("bringing the player back", {("moveto", "player"): None}, {("moveto", "player"): 2}, reach,
             "moving the player back to where the scenario began"),
        ]
        for name, slow, from_call, more, step in cases:
            with self.subTest(name):
                def prepare(s):
                    s.slow_calls.update(slow)
                    s.slow_from_call.update(from_call)
                    if more:
                        more(s)
                s = play(prepare)
                got = summary(s)
                self.assertEqual((got["failed"], got["passed"], s.ended), (0, CHECKS, "quit"), got["first_failure"])
                self.assertTrue(got["result_line"])
                self.assertIn(GONE + step, got["info"])
                self.assertEqual(steps(s)[-1], step)

    def test_a_marker_that_cannot_be_moved_at_all(self):
        """Should moving a marker never return in the game, as moving an item with no model did."""
        need_trial_build(self)

        def no_model(s):
            [f for f in s.by_formkey.values() if getattr(f, "editor_id", "") == "XMarker"][0].has_model = False
        got = summary(play(no_model))
        self.assertEqual((got["failed"], got["passed"]), (0, CHECKS))
        self.assertIn(GONE + "experiment: moving the marker to where the game's settler of scenario 10 was placed", got["info"])

    def test_a_slow_call_is_waited_for(self):
        """One move of the player took 38 seconds in the game. A step that moves somebody is given 150."""
        need_trial_build(self)
        s = play(lambda s: s.slow_calls.update({("movetomyeditorlocation", ON_FLOOR): 38.0, ("setposition", "made at run time"): 38.0}))
        got = summary(s)
        self.assertEqual((got["failed"], got["passed"], s.ended), (0, CHECKS, "quit"))
        self.assertFalse([l for l in got["info"] if l.startswith(GONE[:30])])
        self.assertEqual(steps(s)[-1], "finishing the scenario")

    def test_the_other_scenarios_do_not_meet_the_people(self):
        """All four start disabled. Scenario 10 enables one of them and must
        report what it did before the other three were added; scenario 2's
        killing must still be no fight."""
        need_trial_build(self)
        ten = run_scenario(10, SCRIPTS, PLUGIN, VANILLA, NATIVES, until=600.0)
        self.assertEqual((summary(ten)["failed"], summary(ten)["passed"]), (0, 17))
        self.assertTrue(all(ten.placed[x].disabled for x in (OWN, BARE, ON_FLOOR)))
        two = summary(run_scenario(2, SCRIPTS, PLUGIN, VANILLA, NATIVES, until=600.0))
        self.assertEqual(two["failed"], 0, two["first_failure"])
        self.assertIn("probe: player in combat straight after Kill(player) on the Cutter lead, nobody standing by = False", two["info"])

    def test_it_cannot_follow_scenario_10_in_one_session(self):
        """Both use the trial's quest, which runs once."""
        need_trial_build(self)
        s = Session(SCRIPTS, PLUGIN, VANILLA, NATIVES)
        s.enter_game()
        s.run(1.0)
        s.console_cqf("TLM_Core", "RunSelfTest", [10])
        s.run(100.0)
        self.assertEqual(summary(s)["passed"], 17)
        s.console_cqf("TLM_Core", "RunSelfTest", [11])
        s.run(300.0)
        self.assertEqual(summary(s)["passed"], 17)
        self.assertTrue([l for l in s.user_logs["TLM"] if l.startswith("ABORTED")])


class WhatTheScenarioCatches(unittest.TestCase):
    """One thing wrong, and the check that has to fail for it."""

    def run_with(self, change=None, prepare=None, script_errors=0):
        need_trial_build(self)
        s = play(prepare, change)
        self.assertEqual(s.ended, "quit", "the scenario did not close the game by itself")
        self.assertEqual(len(errors(s)), script_errors, "a scenario that fails must still not call anything on None: %s" % errors(s))
        got = summary(s)
        got["failures"] = failures(s)
        got["steps"] = steps(s)
        got["session"] = s
        return got

    def told(self, got, who, when):
        lines = [l for l in got["info"] if l.startswith("people: %s, %s (" % (who, when))]
        self.assertEqual(len(lines), 1, (who, when))
        return lines[0]

    def test_a_person_of_the_plugins_own_that_walks_off(self):
        """What the scenario is for. It fails, and then tries what might keep the person in place."""
        got = self.run_with(prepare=lambda s: s.stray_override.update({OWN: True}))
        self.assertEqual(got["failures"], [WITHIN])
        self.assertEqual(got["passed"], CHECKS - 1)
        own = "the person of the plugin's own"
        self.assertEqual(self.told(got, own, "at once"),
                         "people: the person of the plugin's own, at once (0.000000 s on the clock): at (2137.000000, -246.000000, 77.000000), "
                         "%f from where it was placed (%f seen from above, 13.000000 higher), 1088.601856 from the player; "
                         "package = [Package < (00023331)>], sit state = 3, in combat = False" % (STRAY, STRAY_FLAT))
        self.assertIn("the person of the plugin's own = No,", [l for l in got["info"] if l.startswith("people: stayed within")][0])
        # put back, it takes a step; restrained, or with its AI off, it stays
        for how, away in (("moved back to where it was placed", STEP), ("restrained and moved back", 0.0), ("its AI off and moved back", 0.0)):
            self.assertIn(" %f from where it was placed (" % away, self.told(got, own + ", " + how, "three seconds later"))
        # the person of the plugin's own comes first among the experiments, and its AI is tried only after the navigation mesh
        experiments = [x for x in got["steps"] if x.startswith("experiment: ")]
        self.assertEqual(experiments[0], "experiment: moving the person of the plugin's own back to where the plugin placed it")
        first_ai = min(i for i, x in enumerate(experiments) if "turning the AI" in x)
        self.assertGreater(first_ai, max(i for i, x in enumerate(experiments) if "navigation mesh" in x))
        self.assertGreater(first_ai, max(i for i, x in enumerate(experiments) if "restraining" in x))

    def test_a_person_that_walks_off_slowly(self):
        """Gone by the sixth second, though it stood there at first: one look straight after Enable would have missed it."""
        def slow(s):
            s.stray_override[OWN] = True
            s.stray_after = 3.0
        got = self.run_with(prepare=slow)
        self.assertEqual(got["failures"], [WITHIN])
        own = "the person of the plugin's own"
        self.assertIn(" 0.000000 from where it was placed (", self.told(got, own, "at once"))
        self.assertIn(" 0.000000 from where it was placed (", self.told(got, own, "two seconds later"))
        self.assertIn(" %f from where it was placed (" % STRAY, self.told(got, own, "six seconds later"))

    def test_a_person_that_ends_up_under_the_floor(self):
        """Seen from above it has not moved. Height counts."""
        def down(s):
            s.stray_override[OWN] = True
            s.stray_by = (0.0, 0.0, -5000.0)
        got = self.run_with(prepare=down)
        self.assertEqual(got["failures"], [WITHIN])
        self.assertIn(" 5000.000000 from where it was placed (0.000000 seen from above, -5000.000000 higher)",
                      self.told(got, "the person of the plugin's own", "six seconds later"))

    def test_only_the_person_with_no_default_package_list_walks_off(self):
        """Reported, not scored: the run passes, and says which recipe held."""
        got = self.run_with(prepare=lambda s: s.stray_override.update({BARE: True}))
        self.assertEqual((got["failures"], got["passed"]), ([], CHECKS))
        self.assertIn(STAYED.replace("the person with no default package list = Yes", "the person with no default package list = No"), got["info"])
        self.assertIn("experiment: moving the person with no default package list back to where the plugin placed it", got["steps"])

    def test_a_settler_that_stays_after_all(self):
        """Should the game's settler stay on that spot: reported, and nothing is tried on it."""
        got = self.run_with(prepare=lambda s: s.stray_override.update({ON_FLOOR: False}))
        self.assertEqual((got["failures"], got["passed"]), ([], CHECKS))
        self.assertIn(STAYED.replace("the game's settler on the same spot = No", "the game's settler on the same spot = Yes"), got["info"])
        self.assertFalse([x for x in got["steps"] if "the game's settler on the same spot back" in x])

    def test_nobody_walks_off(self):
        """Then nothing is tried on anybody, the player is left where the player is, and only the navigation mesh is asked."""
        got = self.run_with(prepare=lambda s: s.stray_override.update({ON_FLOOR: False, SETTLER: False}))
        self.assertEqual((got["failures"], got["passed"]), ([], CHECKS))
        experiments = [x for x in got["steps"] if x.startswith("experiment: ")]
        self.assertEqual(len(experiments), 8)
        self.assertTrue(all("the marker" in x for x in experiments))
        self.assertFalse([x for x in got["steps"] if "again" in x or "moving the player" in x])

    def test_the_settler_is_looked_at_again_with_the_player_elsewhere(self):
        """A place in the room, or a place near the player? The lines say how far from the player it stood both times."""
        got = self.run_with()
        s = got["session"]
        spot = s.placed[OWN].editor_pos
        self.assertIn("people: the player now stands at (%f, %f, %f)" % spot, got["info"])
        first = self.told(got, "the game's settler of scenario 10", "six seconds later")
        again = self.told(got, "the game's settler of scenario 10, with the player standing elsewhere", "six seconds later")
        near = re.compile(r"\), ([0-9.]+) from the player;")
        self.assertNotEqual(near.search(first).group(1), near.search(again).group(1))

    def test_an_alias_with_no_script_to_hear_the_activation(self):
        got = self.run_with(lambda d: alias(d, "PersonOwn").update(Scripts=[]))
        self.assertEqual(got["failures"], [TALK])
        # it was tried from afar and then from close by, and the game performed both
        self.assertIn("people: the first try: Activate on the person from 632.455532 away returned True; stage 30 set = False", got["info"])
        self.assertIn("people: the second try: Activate on the person from 100.000000 away returned True; stage 30 set = False", got["info"])
        # the check is written before the player is brought back, and the player is brought back all the same
        lines = got["session"].user_logs["TLM"]
        self.assertLess(lines.index("FAIL  " + TALK), lines.index("STEP  moving the player back to where the scenario began"))

    def test_an_activation_the_game_does_not_perform_from_afar(self):
        """Not a fault of the plugin: a player stands next to whoever they speak to. The scenario goes there, passes, and says so."""
        got = self.run_with(prepare=lambda s: setattr(s, "activate_reach", 300.0))
        s = got["session"]
        self.assertEqual((got["failures"], got["passed"]), ([], CHECKS))
        self.assertIn("people: the first try: Activate on the person from 632.455532 away returned False; stage 30 set = False", got["info"])
        self.assertIn("people: the second try: Activate on the person from 100.000000 away returned True; stage 30 set = True", got["info"])
        # and the player is brought back, so that the people watched afterwards are watched as the first was
        x, y, z = [a for a in s.arrivals if a["Cell"] == "QASmoke"][0]["Position"]
        self.assertIn("people: the player is back at (%f, %f, %f)" % (x, y, z), got["info"])
        lines = s.user_logs["TLM"]
        self.assertLess(lines.index("INFO  people: the player is back at (%f, %f, %f)" % (x, y, z)),
                        lines.index("STEP  enabling the person with no default package list"))

    def test_an_activation_that_is_heard_late(self):
        """Performed at the first try and heard seven seconds later, while the player was being moved: said so, and not tried twice."""
        def late(s):
            s.activate_event_delay = 7.0
            s.slow_calls[("moveto", "player")] = 3.0
        got = self.run_with(prepare=late)
        self.assertEqual((got["failures"], got["passed"]), ([], CHECKS))
        self.assertIn("people: the first try: Activate on the person from 632.455532 away returned True; stage 30 set = False", got["info"])
        self.assertIn("people: stage 30 was set while the player was being moved: the first try was heard late, and there is no second", got["info"])
        self.assertFalse([l for l in got["info"] if l.startswith("people: the second try")])
        self.assertEqual(got["session"].messages_shown, ["TLM_MSG_TrialTalk"])

    def test_the_player_is_not_moved_when_the_first_activation_works(self):
        got = self.run_with(prepare=lambda s: s.stray_override.update({SETTLER: False}))
        self.assertEqual((got["failures"], got["passed"]), ([], CHECKS))
        self.assertFalse([x for x in got["steps"] if "moving the player" in x])

    def test_the_player_cannot_be_brought_back_without_a_marker(self):
        """A build that did not find the game's marker: the player stays next to the person, and the report says so."""
        def no_marker(d):
            for bind in trial(d)["Scripts"]:
                if bind["Name"] == "TLM:PlacedPeople":
                    bind["Props"] = [p for p in bind["Props"] if p["Name"] != "MarkerBase"]
        got = self.run_with(no_marker, prepare=lambda s: setattr(s, "activate_reach", 300.0))
        self.assertEqual((got["failures"], got["passed"]), ([], CHECKS))
        x, y, z = got["session"].placed[OWN].editor_pos
        self.assertIn("people: no marker base was found when the plugin was built, so the player was not brought back and stands at "
                      "(%f, %f, %f) for the rest of the scenario" % (x + 100.0, y, z), got["info"])
        self.assertEqual(len([l for l in got["info"] if "so the navigation mesh was not asked about" in l]), 2)

    def test_a_script_that_sets_another_stage(self):
        def other_stage(d):
            for p in alias(d, "PersonOwn")["Scripts"][0]["Props"]:
                if p["Name"] == "StageAlways":
                    p["Value"] = 20
        got = self.run_with(other_stage)
        self.assertEqual(got["failures"], [TALK])

    def test_a_person_who_starts_disabled_in_an_alias_that_does_not_allow_it(self):
        got = self.run_with(lambda d: alias(d, "PersonOwn")["Flags"].remove("AllowDisabled"))
        self.assertEqual(got["failures"], ["people: the PersonOwn alias holds an actor: expected true, was false"])
        # the quest's last stage is still scored, the others are still looked at, and the line says who was not there
        self.assertEqual(got["passed"], 2)
        self.assertIn(STAYED.replace("the person of the plugin's own = Yes", "the person of the plugin's own = not there"), got["info"])

    def test_a_person_who_does_not_start_disabled(self):
        got = self.run_with(lambda d: placed(d, OWN).update(InitiallyDisabled=False))
        self.assertEqual(got["failures"], ["people: the person of the plugin's own starts disabled: expected true, was false"])

    def test_a_person_placed_as_a_thing(self):
        """An actor has to be placed with a record of its own kind. Written as an object, there is no actor in the alias."""
        got = self.run_with(lambda d: placed(d, OWN).update(Kind="PlacedObject"))
        self.assertEqual(got["failures"], ["people: the PersonOwn alias holds an actor: expected true, was false"])

    def test_the_other_persons_left_out(self):
        """A build that could not make or place one of the others: said plainly, and the rest still runs."""
        def left_out(d):
            for c in d["Cells"]:
                c["Placed"] = [p for p in c["Placed"] if p["EditorId"] not in (BARE, ON_FLOOR)]
            alias(d, "PersonBare")["Fill"] = None
            alias(d, "SettlerOnFloor")["Fill"] = None
        got = self.run_with(left_out)
        self.assertEqual((got["failures"], got["passed"]), ([], CHECKS))
        self.assertIn("people: the other aliases hold an actor: PersonBare = False, SettlerOnFloor = False, Person = True", got["info"])
        self.assertIn("people: stayed within 64 units of where it was placed for six seconds: the person of the plugin's own = Yes, "
                      "the person with no default package list = not there, the game's settler on the same spot = not there, "
                      "the game's settler of scenario 10 = No", got["info"])

    def test_the_plugin_built_without_the_games_master(self):
        """Nothing is placed, so nobody can be found: said plainly, and the game still closes."""
        need_build(self)
        if not SKELETON.exists():
            self.fail("%s is missing. Run tools/run_checks.sh, which builds it." % SKELETON)
        s = run_scenario(11, SCRIPTS, SKELETON, None, NATIVES, until=600.0)
        self.assertEqual(failures(s), ["people: the PersonOwn alias holds an actor: expected true, was false"])
        self.assertEqual(s.ended, "quit")
        self.assertEqual(errors(s), [])
        self.assertTrue([l for l in s.user_logs["TLM"] if l.endswith("the person of the plugin's own = not there, the person with no default package list = not there, "
                                                                     "the game's settler on the same spot = not there, the game's settler of scenario 10 = not there")])


PERSON_LISTENER = """Scriptname Mini:PersonListener extends ReferenceAlias

int activations = 0
ObjectReference lastBy

Event OnActivate(ObjectReference akActionRef)
	activations += 1
	lastBy = akActionRef
EndEvent
"""


class TheStandInsRulesForPlacedPeople(unittest.TestCase):
    """Each rule as sim.py states it. Only the first has been seen in the game."""

    def session(self, change=None, listen_on=()):
        need_trial_build(self)

        def with_listeners(d):
            for name in listen_on:
                alias(d, name)["Scripts"].append({"Name": "Mini:PersonListener", "Props": []})
            if change:
                change(d)
        folder = Path(tempfile.mkdtemp(prefix="tlm-people-"))
        for p in SCRIPTS.glob("*.psc"):
            (folder / p.name).write_text(p.read_text())
        (folder / "PersonListener.psc").write_text(PERSON_LISTENER)
        s = Session(folder, changed_plugin(with_listeners), VANILLA, NATIVES)
        s.enable_seconds = {}           # one rule at a time: Enable comes back at once here
        s.enter_game()
        s.run(1.0)
        return s

    def do(self, s, call, wait=1.0):
        """Runs something that may take the game a while, as a script would."""
        out = []

        def thread():
            result = call()
            if hasattr(result, "send"):
                result = yield from result
            out.append(result)
        s.spawn(thread(), "a call")
        s.run(s.now + wait)
        return out[0] if out else "never came back"

    def away(self, ref):
        return math.dist(ref.pos, ref.editor_pos)

    def heard(self, quest, alias_name):
        a = [a for a in quest.aliases.values() if a.name == alias_name][0]
        return [i for i in a.scripts if i.script.name == "Mini:PersonListener"][0].vars

    def test_the_games_settler_walks_off_when_it_is_enabled(self):
        """[seen] once: 489 units, and 13 up, the next time the script looked."""
        s = self.session()
        for name in (SETTLER, ON_FLOOR):
            person = s.placed[name]
            self.assertTrue(person.disabled)
            self.assertEqual(person.pos, person.editor_pos)
            s.n_objectreference_enable(person, None)
            self.assertEqual(person.pos, tuple(a + b for a, b in zip(person.editor_pos, STRAY_BY)))
            self.assertAlmostEqual(self.away(person), 488.93, places=1)
            self.assertIs(s.n_actor_getcurrentpackage(person, None), s.some_package)
            # [seen]: it is sitting when the script first looks, and has stood up two seconds later
            self.assertEqual(s.n_actor_getsitstate(person, None), 3)
            s.run(s.now + 2.0)
            self.assertEqual(s.n_actor_getsitstate(person, None), 0)
            self.assertEqual(to_string(s.n_actor_getcurrentpackage(person, None)), "[Package < (00023331)>]")

    def test_a_person_of_the_plugins_own_stays(self):
        """[assumed], with or without a default package list: what scenario 11 asks the game."""
        s = self.session()
        self.assertTrue(s.npc_info["TLM_NPC_TrialPerson"]["HasDefaultPackageList"])
        self.assertFalse(s.npc_info["TLM_NPC_TrialPersonBare"]["HasDefaultPackageList"])
        for name in (OWN, BARE):
            person = s.placed[name]
            self.assertIsInstance(person, Actor)
            self.assertEqual(s.npc_info[person.base.editor_id]["Packages"], 0)
            s.n_objectreference_enable(person, None)
            s.run(s.now + 10.0)
            self.assertEqual(person.pos, person.editor_pos)
            # [seen]: it runs a package all the same, one the game gives it, and does not sit
            self.assertIs(s.n_actor_getcurrentpackage(person, None), s.idle_package)
            self.assertEqual(s.n_actor_getsitstate(person, None), 0)
            self.assertTrue(person.has_3d())
            s.n_objectreference_disable(person, None)

    def test_a_person_of_the_plugins_own_with_packages_would_walk_off(self):
        for what in ("Packages", "TemplateFlags"):
            with self.subTest(what):
                def with_packages(d):
                    for n in d["Npcs"]:
                        if what == "Packages":
                            n["Packages"] = 2
                        else:
                            n["TemplateFlags"].append("AiPackages")
                s = self.session(with_packages)
                person = s.placed[OWN]
                s.n_objectreference_enable(person, None)
                self.assertAlmostEqual(self.away(person), 488.93, places=1)

    def test_a_person_made_while_the_game_runs_is_left_alone(self):
        """The rule is about people the plugin places. A settler made by a script stays where it is made, as before."""
        s = self.session()
        made = s.n_objectreference_placeatme(s.player, None, s.placed[SETTLER].base)
        s.run(s.now + 10.0)
        self.assertEqual(made.pos, s.player.pos)
        self.assertIsNone(made.editor_pos)
        self.do(s, lambda: s.n_objectreference_movetomyeditorlocation(made, None))
        self.assertEqual(made.pos, s.player.pos)

    def test_put_back_it_takes_a_step_unless_it_is_held(self):
        """[seen]: put back, the settler is at its spot at once, with no
        package and still "sitting", and some 30 units off three seconds
        later; with its AI off it stays. Restrained: [seen] once that it
        stays and once that it does not; the stand-in lets restraint hold."""
        s = self.session()
        person = s.placed[ON_FLOOR]
        s.n_objectreference_enable(person, None)
        self.do(s, lambda: s.n_objectreference_movetomyeditorlocation(person, None), wait=0.1)
        self.assertEqual(person.pos, person.editor_pos)
        self.assertIsNone(s.n_actor_getcurrentpackage(person, None))
        self.assertEqual(s.n_actor_getsitstate(person, None), 3)
        s.run(s.now + 3.0)
        self.assertAlmostEqual(self.away(person), STEP, places=3)
        self.assertIs(s.n_actor_getcurrentpackage(person, None), s.some_package)
        self.assertTrue(s.n_actor_setrestrained(person, None, True))
        self.do(s, lambda: s.n_objectreference_movetomyeditorlocation(person, None), wait=3.0)
        self.assertEqual(person.pos, person.editor_pos)
        s.n_actor_setrestrained(person, None, False)
        s.run(s.now + 3.0)
        self.assertAlmostEqual(self.away(person), STEP, places=3)
        s.n_actor_enableai(person, None, False)
        self.do(s, lambda: s.n_objectreference_movetomyeditorlocation(person, None), wait=3.0)
        self.assertEqual(person.pos, person.editor_pos)
        self.assertIsNone(s.n_actor_getcurrentpackage(person, None))
        self.assertEqual(s.n_actor_getsitstate(person, None), 1)
        s.n_actor_enableai(person, None, True)
        s.run(s.now + 3.0)
        self.assertAlmostEqual(self.away(person), STEP, places=3)

    def test_enable_takes_as_long_as_the_game_took(self):
        """[seen]: about 19 seconds for a person of the plugin's own, about two for the game's settler."""
        s = self.session()
        s.enable_seconds = dict(ENABLE_SECONDS)
        own, settler = s.placed[OWN], s.placed[SETTLER]
        self.assertEqual(self.do(s, lambda: s.n_objectreference_enable(own, None), wait=18.0), "never came back")
        self.assertTrue(own.disabled)
        s.run(s.now + 2.0)
        self.assertFalse(own.disabled)
        self.assertEqual(self.do(s, lambda: s.n_objectreference_enable(settler, None), wait=1.0), "never came back")
        s.run(s.now + 2.0)
        self.assertFalse(settler.disabled)
        # a second Enable of somebody already enabled comes back at once
        self.assertIsNone(self.do(s, lambda: s.n_objectreference_enable(own, None), wait=0.1))

    def test_a_walk_arranged_before_the_person_was_disabled_does_not_happen_after(self):
        s = self.session()
        s.stray_after = 2.0
        person = s.placed[ON_FLOOR]
        s.n_objectreference_enable(person, None)
        s.run(s.now + 1.0)
        s.n_objectreference_disable(person, None)
        s.run(s.now + 5.0)
        self.assertEqual(person.pos, person.editor_pos)
        s.n_objectreference_enable(person, None)
        s.run(s.now + 1.0)
        self.assertEqual(person.pos, person.editor_pos)
        s.run(s.now + 2.0)
        self.assertAlmostEqual(self.away(person), 488.93, places=1)

    def test_a_dead_person_cannot_be_restrained(self):
        s = self.session()
        person = s.placed[OWN]
        s.n_objectreference_enable(person, None)
        person.dead = True
        self.assertFalse(s.n_actor_setrestrained(person, None, True))

    def test_activating_a_person_tells_the_scripts_on_its_alias(self):
        """[documented]. What the game then does of its own accord with the person is not played."""
        s = self.session(listen_on=("PersonOwn", "SettlerOnFloor"))
        quest = s.quests["TLM_Trial"]
        s.start_quest(quest)
        s.run(s.now + 1.0)
        own, other = s.placed[OWN], s.placed[ON_FLOOR]
        # nobody there yet
        self.assertFalse(s.n_objectreference_activate(own, None, s.player))
        s.run(s.now + 1.0)
        self.assertEqual(self.heard(quest, "PersonOwn")["activations"], 0)
        s.n_objectreference_enable(own, None)
        self.assertTrue(s.n_objectreference_activate(own, None, s.player))
        s.run(s.now + 1.0)
        self.assertEqual(self.heard(quest, "PersonOwn")["activations"], 1)
        self.assertIs(self.heard(quest, "PersonOwn")["lastby"], s.player)
        self.assertEqual(self.heard(quest, "SettlerOnFloor")["activations"], 0)
        # and the project's own script on the alias showed its line and set its stage
        self.assertEqual(s.messages_shown, ["TLM_MSG_TrialTalk"])
        self.assertIn(30, quest.done)
        self.assertIs(other.disabled, True)

    def test_activated_by_somebody_else_the_project_s_script_does_nothing(self):
        s = self.session(listen_on=("PersonOwn",))
        quest = s.quests["TLM_Trial"]
        s.start_quest(quest)
        s.run(s.now + 1.0)
        own = s.placed[OWN]
        s.n_objectreference_enable(own, None)
        somebody = s.n_objectreference_placeatme(s.player, None, s.placed[SETTLER].base)
        self.assertTrue(s.n_objectreference_activate(own, None, somebody))
        s.run(s.now + 1.0)
        self.assertEqual(self.heard(quest, "PersonOwn")["activations"], 1)
        self.assertEqual(s.messages_shown, [])
        self.assertNotIn(30, quest.done)

    def test_an_activation_has_a_reach_only_when_a_test_gives_it_one(self):
        s = self.session(listen_on=("PersonOwn",))
        quest = s.quests["TLM_Trial"]
        s.start_quest(quest)
        s.run(s.now + 1.0)
        own = s.placed[OWN]
        s.n_objectreference_enable(own, None)
        far = math.dist(own.pos, s.player.pos)
        s.activate_reach = far - 1.0
        self.assertFalse(s.n_objectreference_activate(own, None, s.player))
        s.run(s.now + 1.0)
        self.assertEqual(self.heard(quest, "PersonOwn")["activations"], 0)
        s.activate_reach = far + 1.0
        self.assertTrue(s.n_objectreference_activate(own, None, s.player))
        s.run(s.now + 1.0)
        self.assertEqual(self.heard(quest, "PersonOwn")["activations"], 1)

    def test_the_navigation_mesh_is_taken_to_be_the_floor(self):
        """[assumed]: the stand-in has no mesh. A marker comes straight down onto the level the player arrives on."""
        s = self.session()
        marker_base = [f for f in s.by_formkey.values() if getattr(f, "editor_id", "") == "XMarker"][0]
        marker = s.n_objectreference_placeatme(s.player, None, marker_base)
        x, y, z = s.placed[SETTLER].editor_pos
        self.assertIsNone(self.do(s, lambda: s.n_objectreference_setposition(marker, None, x, y, z + 150.0)))
        self.assertEqual(marker.pos, (x, y, z + 150.0))
        self.do(s, lambda: s.n_objectreference_movetonearestnavmeshlocation(marker, None))
        self.assertEqual(marker.pos, (x, y, s.player.pos[2]))

    def test_moving_something_with_no_model_never_comes_back(self):
        """[seen] for MoveTo; [assumed] for the three functions that are new here."""
        s = self.session()
        thing = s.n_objectreference_placeatme(s.player, None, s.forms["TLM_MISC_TornTransitPass"])
        self.assertFalse(thing.has_3d())
        for call in (lambda: s.n_objectreference_setposition(thing, None, 1.0, 2.0, 3.0),
                     lambda: s.n_objectreference_movetomyeditorlocation(thing, None),
                     lambda: s.n_objectreference_movetonearestnavmeshlocation(thing, None)):
            self.assertEqual(self.do(s, call), "never came back")
            self.assertEqual(thing.pos, s.player.pos)

    def test_a_call_takes_as_long_as_a_test_says(self):
        """Only when a test says so: for the scenario's own time limits."""
        s = self.session()
        person = s.placed[OWN]
        s.slow_calls[("enable", OWN)] = 5.0
        self.assertEqual(self.do(s, lambda: s.n_objectreference_enable(person, None), wait=4.0), "never came back")
        self.assertTrue(person.disabled)
        s.run(s.now + 2.0)
        self.assertFalse(person.disabled)
        # from the second call on, and never
        s.n_objectreference_disable(person, None)
        s.slow_calls[("enable", OWN)] = None
        s.slow_from_call[("enable", OWN)] = 3
        self.assertIsNone(self.do(s, lambda: s.n_objectreference_enable(person, None)))
        self.assertFalse(person.disabled)
        s.n_objectreference_disable(person, None)
        self.assertEqual(self.do(s, lambda: s.n_objectreference_enable(person, None), wait=500.0), "never came back")
        self.assertTrue(person.disabled)

    def test_the_clock_and_the_square_root(self):
        s = self.session()
        before = s.g_utility_getcurrentrealtime()
        s.run(s.now + 2.5)
        self.assertAlmostEqual(s.g_utility_getcurrentrealtime() - before, 2.5)
        self.assertEqual(s.g_math_sqrt(1024.0), 32.0)


if __name__ == "__main__":
    unittest.main()
