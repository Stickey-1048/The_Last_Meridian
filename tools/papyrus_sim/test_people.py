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
  - nothing scored comes after an experiment, and an experiment that does not
    come back still leaves a result;
  - the stand-in's rules for placed people do what sim.py says they do.
"""
import math
import tempfile
import unittest
from pathlib import Path

from sim import FRAME, STRAY_BY, Actor, Session, run_scenario
from test_placed import SKELETON, alias, changed_plugin, errors, need_trial_build, placed
from test_sim import NATIVES, PLUGIN, SCRIPTS, VANILLA, need_build, summary

OWN, BARE, ON_FLOOR, SETTLER = ("TLM_REF_TrialPersonOwn", "TLM_REF_TrialPersonBare", "TLM_REF_TrialSettlerOnFloor", "TLM_REF_TrialPerson")
CHECKS = 8
STRAY = math.hypot(STRAY_BY[0], STRAY_BY[1])

STAYED = ("people: did not stay within 64 units: the person of the plugin's own = False, the person with no default package list = False, "
          "the game's settler on open floor = True, the game's settler of scenario 10 = True")


def failures(s):
    return [l[len("FAIL"):].strip() for l in s.user_logs["TLM"] if l.startswith("FAIL")]


def steps(s):
    return [l[len("STEP"):].strip() for l in s.user_logs["TLM"] if l.startswith("STEP")]


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
        """One at a time, or what one does could be put down to another. The
        two persons of the plugin's own share a spot, and must never be
        there together."""
        need_trial_build(self)
        s = run_scenario(11, SCRIPTS, PLUGIN, VANILLA, NATIVES, until=900.0)
        about = []
        for step in steps(s):
            if step.startswith("enabling "):
                self.assertEqual(about, [], "%s while somebody else is still enabled" % step)
                about.append(step[len("enabling "):].replace(" again", ""))
            elif step.startswith("disabling "):
                self.assertEqual(about, [step[len("disabling "):]])
                about = []
        self.assertEqual(about, [])
        own, bare, floor, settler = (s.placed[x] for x in (OWN, BARE, ON_FLOOR, SETTLER))
        self.assertEqual(own.editor_pos, bare.editor_pos)
        self.assertEqual(len({own.editor_pos, floor.editor_pos, settler.editor_pos}), 3)

    def test_what_is_scored_comes_before_any_experiment(self):
        """An experiment may not come back. Nothing that counts may wait behind one."""
        need_trial_build(self)
        s = run_scenario(11, SCRIPTS, PLUGIN, VANILLA, NATIVES, until=900.0)
        lines = s.user_logs["TLM"]
        first = min(i for i, l in enumerate(lines) if l.startswith("STEP  experiment: "))
        self.assertFalse([l for l in lines[first:] if l.startswith(("PASS", "FAIL"))])
        self.assertEqual(sum(1 for l in lines[:first] if l.startswith("PASS")), CHECKS)
        # every step that calls something this project has not called before says it is an experiment
        self.assertEqual(sum(1 for step in steps(s) if step.startswith("experiment: ")), 3 * 2 + 2 * 3)

    def test_an_experiment_that_does_not_come_back_still_leaves_a_result(self):
        """Should moving a marker never return in the game, as moving an item
        with no model did: the watchdog ends the scenario there, and what was
        scored before stands."""
        need_trial_build(self)
        s = Session(SCRIPTS, PLUGIN, VANILLA, NATIVES)
        marker = [f for f in s.by_formkey.values() if getattr(f, "editor_id", "") == "XMarker"][0]
        marker.has_model = False
        s.set_global("TLM_G_DevScenario", 11)
        s.enter_game()
        s.run(900.0)
        got = summary(s)
        self.assertEqual((got["failed"], got["passed"], s.ended), (0, CHECKS, "quit"), got["first_failure"])
        self.assertTrue(got["result_line"])
        self.assertIn("this experiment did not come back, and the scenario was ended here: experiment: moving the marker to 150 units above "
                      "where the game's settler of scenario 10 was placed", got["info"])

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
        s = Session(SCRIPTS, changed_plugin(change or (lambda d: None)), VANILLA, NATIVES)
        if prepare:
            prepare(s)
        s.set_global("TLM_G_DevScenario", 11)
        s.enter_game()
        s.run(900.0)
        self.assertEqual(s.ended, "quit", "the scenario did not close the game by itself")
        self.assertEqual(len(errors(s)), script_errors, "a scenario that fails must still not call anything on None: %s" % errors(s))
        got = summary(s)
        got["failures"] = failures(s)
        got["steps"] = steps(s)
        return got

    WITHIN = "people: the person of the plugin's own is within 64 units of where it was placed, six seconds after it was enabled: expected true, was false"

    def test_a_person_of_the_plugins_own_that_walks_off(self):
        """What the scenario is for. It fails, and then tries what might keep the person in place."""
        got = self.run_with(prepare=lambda s: s.stray_override.update({OWN: True}))
        self.assertEqual(got["failures"], [self.WITHIN])
        self.assertEqual(got["passed"], CHECKS - 1)
        self.assertIn("people: the person of the plugin's own, at once (0.000000 s on the clock): at (2137.000000, -246.000000, 77.000000), "
                      "%f from where it was placed seen from above, 13.000000 higher; package = [Package <a package of the game's>], sit state = 0, in combat = False" % STRAY,
                      got["info"])
        told = [l for l in got["info"] if l.startswith("people: the person of the plugin's own, ")]
        for how, away in (("moved back to where it was placed", STRAY), ("restrained and moved back", 0.0), ("its AI off and moved back", 0.0)):
            line = [l for l in told if l.startswith("people: the person of the plugin's own, %s, three seconds later" % how)]
            self.assertEqual(len(line), 1, how)
            self.assertIn("%f from where it was placed seen from above" % away, line[0])
        # the person of the plugin's own comes first among the experiments
        experiments = [x for x in got["steps"] if x.startswith("experiment: ")]
        self.assertEqual(experiments[0], "experiment: moving the person of the plugin's own back to where the plugin placed it")

    def test_a_person_that_walks_off_slowly(self):
        """Gone by the sixth second, though it stood there at first: one look straight after Enable would have missed it."""
        def slow(s):
            s.stray_override[OWN] = True
            s.stray_after = 3.0
        got = self.run_with(prepare=slow)
        self.assertEqual(got["failures"], [self.WITHIN])
        at = {when: [l for l in got["info"] if l.startswith("people: the person of the plugin's own, %s (" % when)][0]
              for when in ("at once", "two seconds later", "six seconds later")}
        self.assertIn(" 0.000000 from where it was placed", at["at once"])
        self.assertIn(" 0.000000 from where it was placed", at["two seconds later"])
        self.assertIn(" %f from where it was placed" % STRAY, at["six seconds later"])

    def test_only_the_person_with_no_default_package_list_walks_off(self):
        """Reported, not scored: the run passes, and says which recipe held."""
        got = self.run_with(prepare=lambda s: s.stray_override.update({BARE: True}))
        self.assertEqual((got["failures"], got["passed"]), ([], CHECKS))
        self.assertIn(STAYED.replace("the person with no default package list = False", "the person with no default package list = True"), got["info"])
        self.assertIn("experiment: moving the person with no default package list back to where the plugin placed it", got["steps"])

    def test_a_settler_that_stays_after_all(self):
        """Should the game's settler stay on open floor: reported, and nothing is tried on it."""
        got = self.run_with(prepare=lambda s: s.stray_override.update({ON_FLOOR: False}))
        self.assertEqual((got["failures"], got["passed"]), ([], CHECKS))
        self.assertIn(STAYED.replace("the game's settler on open floor = True", "the game's settler on open floor = False"), got["info"])
        self.assertFalse([x for x in got["steps"] if "the game's settler on open floor back" in x])

    def test_an_alias_with_no_script_to_hear_the_activation(self):
        got = self.run_with(lambda d: alias(d, "PersonOwn").update(Scripts=[]))
        self.assertEqual(got["failures"], ["people: activating the person sets stage 30 (TLM:MessageStageAlias on its alias): expected true, was false"])
        # it was tried from afar and then from close by, and the game performed both
        self.assertIn("people: Activate on the person from 632.455532 away returned True; stage 30 set = False", got["info"])
        self.assertIn("people: Activate on the person from 150.000000 away returned True; stage 30 set = False", got["info"])
        self.assertIn("moving the player back to where the scenario began", got["steps"])

    def test_an_activation_the_game_does_not_perform_from_afar(self):
        """Not a fault of the plugin: a player stands next to whoever they speak to. The scenario goes there, passes, and says so."""
        home = []

        def short_reach(s):
            s.activate_reach = 300.0
            home.append(s)
        got = self.run_with(prepare=short_reach)
        self.assertEqual((got["failures"], got["passed"]), ([], CHECKS))
        self.assertIn("people: Activate on the person from 632.455532 away returned False; stage 30 set = False", got["info"])
        self.assertIn("people: Activate on the person from 150.000000 away returned True; stage 30 set = True", got["info"])
        # and the player is brought back, so that the people watched afterwards are watched as the first was
        x, y, z = [a for a in home[0].arrivals if a["Cell"] == "QASmoke"][0]["Position"]
        self.assertIn("people: the player is back at (%f, %f, %f)" % (x, y, z), got["info"])
        self.assertEqual(home[0].player.pos, (x, y, z))

    def test_the_player_is_not_moved_when_the_first_activation_works(self):
        got = self.run_with()
        self.assertEqual((got["failures"], got["passed"]), ([], CHECKS))
        self.assertFalse([x for x in got["steps"] if "moving the player" in x])

    def test_a_script_that_sets_another_stage(self):
        def other_stage(d):
            for p in alias(d, "PersonOwn")["Scripts"][0]["Props"]:
                if p["Name"] == "StageAlways":
                    p["Value"] = 20
        got = self.run_with(other_stage)
        self.assertEqual(got["failures"], ["people: activating the person sets stage 30 (TLM:MessageStageAlias on its alias): expected true, was false"])

    def test_a_person_who_starts_disabled_in_an_alias_that_does_not_allow_it(self):
        got = self.run_with(lambda d: alias(d, "PersonOwn")["Flags"].remove("AllowDisabled"))
        self.assertEqual(got["failures"], ["people: the PersonOwn alias holds an actor: expected true, was false"])
        # the others are still looked at
        self.assertIn(STAYED, got["info"])

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

    def test_the_plugin_built_without_the_games_master(self):
        """Nothing is placed, so nobody can be found: said plainly, and the game still closes."""
        need_build(self)
        if not SKELETON.exists():
            self.fail("%s is missing. Run tools/run_checks.sh, which builds it." % SKELETON)
        s = run_scenario(11, SCRIPTS, SKELETON, None, NATIVES, until=600.0)
        self.assertEqual(failures(s), ["people: the PersonOwn alias holds an actor: expected true, was false"])
        self.assertEqual(s.ended, "quit")
        self.assertEqual(errors(s), [])


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
        s.enter_game()
        s.run(1.0)
        return s

    def do(self, s, call):
        """Runs something that may take the game a while, as a script would."""
        out = []

        def thread():
            result = call()
            if hasattr(result, "send"):
                result = yield from result
            out.append(result)
        s.spawn(thread(), "a call")
        s.run(s.now + 1.0)
        return out[0] if out else "never came back"

    def away(self, ref):
        return math.dist(ref.pos, ref.editor_pos)

    def heard(self, quest, alias_name):
        a = [a for a in quest.aliases.values() if a.name == alias_name][0]
        return [i for i in a.scripts if i.script.name == "Mini:PersonListener"][0].vars

    def test_the_games_settler_walks_off_when_it_is_enabled(self):
        """[seen] once: 489 units, and 13 up, by the time the script looked."""
        s = self.session()
        for name in (SETTLER, ON_FLOOR):
            person = s.placed[name]
            self.assertTrue(person.disabled)
            self.assertEqual(person.pos, person.editor_pos)
            s.n_objectreference_enable(person, None)
            self.assertEqual(person.pos, tuple(a + b for a, b in zip(person.editor_pos, STRAY_BY)))
            self.assertAlmostEqual(self.away(person), 488.93, places=1)
            self.assertIs(s.n_actor_getcurrentpackage(person, None), s.some_package)

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
            self.assertIsNone(s.n_actor_getcurrentpackage(person, None))
            self.assertTrue(person.has_3d())

    def test_a_person_of_the_plugins_own_with_packages_would_walk_off(self):
        def with_packages(d):
            for n in d["Npcs"]:
                n["Packages"] = 2
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

    def test_put_back_it_walks_off_again_unless_it_is_held(self):
        s = self.session()
        person = s.placed[ON_FLOOR]
        s.n_objectreference_enable(person, None)
        self.do(s, lambda: s.n_objectreference_movetomyeditorlocation(person, None))
        self.assertAlmostEqual(self.away(person), 488.93, places=1)
        self.assertTrue(s.n_actor_setrestrained(person, None, True))
        self.do(s, lambda: s.n_objectreference_movetomyeditorlocation(person, None))
        self.assertEqual(person.pos, person.editor_pos)
        s.n_actor_setrestrained(person, None, False)
        self.assertAlmostEqual(self.away(person), 488.93, places=1)
        s.n_actor_enableai(person, None, False)
        self.do(s, lambda: s.n_objectreference_movetomyeditorlocation(person, None))
        self.assertEqual(person.pos, person.editor_pos)
        self.assertIsNone(s.n_actor_getcurrentpackage(person, None))
        s.n_actor_enableai(person, None, True)
        self.assertAlmostEqual(self.away(person), 488.93, places=1)

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
        thing = s.n_objectreference_placeatme(s.player, None, s.forms["TLM_MISC_Dispatch"])
        self.assertFalse(thing.has_3d())
        for call in (lambda: s.n_objectreference_setposition(thing, None, 1.0, 2.0, 3.0),
                     lambda: s.n_objectreference_movetomyeditorlocation(thing, None),
                     lambda: s.n_objectreference_movetonearestnavmeshlocation(thing, None)):
            self.assertEqual(self.do(s, call), "never came back")
            self.assertEqual(thing.pos, s.player.pos)

    def test_the_clock_and_the_square_root(self):
        s = self.session()
        before = s.g_utility_getcurrentrealtime()
        s.run(s.now + 2.5)
        self.assertAlmostEqual(s.g_utility_getcurrentrealtime() - before, 2.5)
        self.assertEqual(s.g_math_sqrt(1024.0), 32.0)


if __name__ == "__main__":
    unittest.main()
