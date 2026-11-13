"""Tests of self-test scenario 10, the placed-content trial, and of the
stand-in's rules for what a plugin places in a cell of the game.

NOTHING HERE HAS BEEN SEEN IN THE GAME. Every other rule of the stand-in has
at least one game run behind it. These do not: they come from the Creation
Kit wiki (what a trigger is, what picking something up does, what the game's
two default alias scripts do) and, where the wiki is silent, from the
cautious reading, marked [assumed] in sim.py. So a pass here says three
things agree with each other: the scenario's script, the plugin the builder
writes, and those readings. It says nothing about the game. The first run of
scenario 10 on the PC is what that is for; when it has been made, record it
in game_runs.json and correct sim.py where the game differed.

What the tests are for meanwhile:
  - the scenario passes against the plugin as built, however the timing falls;
  - the scenario notices each thing it is there to notice: every test in
    WhatTheScenarioCatches breaks one thing in the plugin's description and
    names the check that must then fail;
  - the stand-in's new rules do what sim.py says they do.
"""
import json
import tempfile
import unittest
from pathlib import Path

from sim import ACTOR_HEIGHT, FRAME, Actor, Session, SimError, run_scenario
from test_sim import NATIVES, PLUGIN, ROOT, SCRIPTS, VANILLA, need_build, summary

ARRIVALS = PLUGIN.with_name("TheLastMeridian.arrivals.json")
# The plugin as built without the game's master: nothing is placed.
SKELETON = ROOT / "build" / "TheLastMeridian.json"

PERSON, TRIGGER, GAME_TRIGGER, OBJECT, ZONE_TRIGGER = ("TLM_REF_TrialPerson", "TLM_REF_TrialTrigger", "TLM_REF_TrialTriggerGameBase",
                                                       "TLM_REF_TrialObject", "TLM_REF_TrialTriggerActorZone")
CHECKS = 17


def changed_plugin(change):
    """The plugin's description with something changed, in a folder of its own
    with the other two files the stand-in reads beside it."""
    data = json.loads(PLUGIN.read_text())
    change(data)
    folder = Path(tempfile.mkdtemp(prefix="tlm-placed-"))
    (folder / "TheLastMeridian.json").write_text(json.dumps(data))
    (folder / "TheLastMeridian.arrivals.json").write_text(ARRIVALS.read_text())
    return folder / "TheLastMeridian.json"


def trial(data):
    return [q for q in data["Quests"] if q["EditorId"] == "TLM_Trial"][0]


def alias(data, name):
    return [a for a in trial(data)["Aliases"] if a["Name"] == name][0]


def placed(data, editor_id):
    return [p for c in data["Cells"] for p in c["Placed"] if p["EditorId"] == editor_id][0]


def arrival():
    return [a for a in json.loads(ARRIVALS.read_text()) if a["Cell"] == "QASmoke"][0]


def need_trial_build(test):
    need_build(test)
    if not ARRIVALS.exists() or not json.loads(PLUGIN.read_text()).get("Cells"):
        test.fail("%s holds no placed references. Run tools/run_checks.sh, which builds it against a master with the test room." % PLUGIN)


def errors(session):
    return [l for l in session.papyrus_log if l.startswith("error:")]


class TheTrialAsBuilt(unittest.TestCase):
    def test_it_passes(self):
        need_trial_build(self)
        s = run_scenario(10, SCRIPTS, PLUGIN, VANILLA, NATIVES, until=600.0)
        got = summary(s)
        self.assertEqual(got["failed"], 0, got["first_failure"])
        self.assertEqual(got["passed"], CHECKS)
        self.assertEqual(s.ended, "quit", "the scenario did not close the game by itself")
        self.assertEqual(errors(s), [])
        self.assertEqual(s.message_boxes, [])
        # the two comparison triggers, reported and not scored
        self.assertIn("trial: entering the trigger made on the game's own empty trigger: stage 11 set = True (it was False before)", got["info"])
        self.assertIn("trial: entering the trigger on the layer L_ACTORZONE: stage 12 set = True (it was False before)", got["info"])
        # the fallback for a pick-up that did not set the stage was not needed
        self.assertFalse([l for l in got["info"] if "AddItem" in l])
        # the two real quests were never touched
        self.assertEqual((got["main_stage_events"], got["side_stage_events"]), (0, 0))
        self.assertFalse(s.quests["TLM_MQ01"].running or s.quests["TLM_SQ01"].running)

    def test_the_player_begins_where_the_builder_says_the_player_arrives(self):
        need_trial_build(self)
        got = summary(run_scenario(10, SCRIPTS, PLUGIN, VANILLA, NATIVES, until=600.0))
        x, y, z = arrival()["Position"]
        self.assertEqual(got["info"][1], "trial: the player begins at (%f, %f, %f)" % (x, y, z))
        self.assertIn("trial: the player is back at (%f, %f, %f)" % (x, y, z), got["info"])

    def test_every_trigger_is_entered_the_same_way(self):
        """From where the scenario began, over the same distance, with nobody else about: or a
        difference between the three would say nothing about the one thing each differs in."""
        need_trial_build(self)
        s = run_scenario(10, SCRIPTS, PLUGIN, VANILLA, NATIVES, until=600.0)
        got = summary(s)
        before = [l for l in got["info"] if "things inside it before the move: " in l]
        after = [l for l in got["info"] if l.startswith("trial: after the move the player is at")]
        self.assertEqual((len(before), len(after)), (3, 3))
        distances = {l.split(", ")[3].split(" from the player")[0] for l in before}
        self.assertEqual(len(distances), 1, "the three triggers are not the same distance from where the player is moved from: %s" % distances)
        for l in before:
            self.assertTrue(l.endswith("things inside it before the move: 0"), l)
        for l in after:
            self.assertTrue(l.endswith("things inside it: 1, which is 1 more than before"), l)
        # the person is enabled only after the last trigger
        lines = s.user_logs["TLM"]
        enabled = lines.index("STEP  enabling the placed person")
        self.assertGreater(enabled, max(i for i, l in enumerate(lines) if l.startswith("STEP  moving the player into ")))

    def test_it_passes_however_the_timing_falls(self):
        need_trial_build(self)
        for how in [dict(native_delay=FRAME)] + [dict(shake=n) for n in range(25)]:
            with self.subTest(**how):
                s = run_scenario(10, SCRIPTS, PLUGIN, VANILLA, NATIVES, until=3000.0, **how)
                got = summary(s)
                self.assertEqual((got["failed"], got["passed"], s.ended), (0, CHECKS, "quit"), got["first_failure"])
                self.assertEqual(errors(s), [])

    def test_it_cannot_be_run_twice_in_a_session(self):
        """The quest runs once. A second go must say so and not report nonsense."""
        need_trial_build(self)
        s = Session(SCRIPTS, PLUGIN, VANILLA, NATIVES)
        s.enter_game()
        s.run(1.0)
        s.console_cqf("TLM_Core", "RunSelfTest", [10])
        s.run(100.0)
        self.assertEqual(summary(s)["passed"], CHECKS)
        s.console_cqf("TLM_Core", "RunSelfTest", [10])
        s.run(200.0)
        self.assertEqual(summary(s)["passed"], CHECKS)
        self.assertTrue([l for l in s.user_logs["TLM"] if l.startswith("ABORTED")])

    def test_the_other_scenarios_do_not_meet_what_is_placed(self):
        """The placed person starts disabled so that nobody new stands about:
        a bystander changes what the game makes of a killing. Scenario 2
        reports exactly that, and must report what it did before."""
        need_trial_build(self)
        got = summary(run_scenario(2, SCRIPTS, PLUGIN, VANILLA, NATIVES, until=600.0))
        self.assertEqual(got["failed"], 0, got["first_failure"])
        self.assertIn("probe: player in combat straight after Kill(player) on the Cutter lead, nobody standing by = False", got["info"])


class WhatTheScenarioCatches(unittest.TestCase):
    """One thing wrong in the plugin, and the check that has to fail for it."""

    def run_with(self, change, prepare=None, script_errors=0):
        need_trial_build(self)
        s = Session(SCRIPTS, changed_plugin(change), VANILLA, NATIVES)
        if prepare:
            prepare(s)
        s.set_global("TLM_G_DevScenario", 10)
        s.enter_game()
        s.run(600.0)
        self.assertEqual(s.ended, "quit", "the scenario did not close the game by itself")
        self.assertEqual(len(errors(s)), script_errors, "a scenario that fails must still not call anything on None: %s" % errors(s))
        got = summary(s)
        got["failures"] = [l[len("FAIL"):].strip() for l in s.user_logs["TLM"] if l.startswith("FAIL")]
        return got

    def test_a_person_who_starts_disabled_in_an_alias_that_does_not_allow_it(self):
        got = self.run_with(lambda d: alias(d, "Person")["Flags"].remove("AllowDisabled"))
        self.assertEqual(got["failures"], ["trial: the Person alias holds a reference: expected true, was false",
                                           "trial: the reference in the Person alias is an actor: expected true, was false"])

    def test_a_person_who_does_not_start_disabled(self):
        got = self.run_with(lambda d: placed(d, PERSON).update(InitiallyDisabled=False))
        self.assertEqual(got["failures"], ["trial: the placed person starts disabled: expected true, was false"])

    def test_an_alias_that_points_at_nothing(self):
        got = self.run_with(lambda d: alias(d, "Object").update(Fill="forced 000FFF:TheLastMeridian.esp"))
        self.assertEqual(got["failures"], ["trial: the Object alias holds a reference: expected true, was false"])

    def test_a_placed_object_of_another_item(self):
        got = self.run_with(lambda d: placed(d, OBJECT).update(Base="TLM_MISC_Dispatch"))
        self.assertEqual(got["failures"], ["trial: how many of the object the player has after picking it up = 0, expected 1"])

    def test_an_object_whose_alias_has_no_script(self):
        got = self.run_with(lambda d: alias(d, "Object").update(Scripts=[]))
        self.assertEqual(got["failures"], ["trial: picking the object up sets stage 20 (the game's own script on the alias): expected true, was false"])
        # and the second way of getting it to the player is tried, and reported
        self.assertIn("trial: after AddItem of the placed object: the player has 1, stage 20 set = False", got["info"])

    def test_a_pick_up_that_the_game_does_not_perform(self):
        def game_ignores_activate(s):
            s.activate_picks_up = False
        got = self.run_with(lambda d: None, game_ignores_activate)
        self.assertEqual(got["failures"], ["trial: how many of the object the player has after picking it up = 0, expected 1",
                                           "trial: picking the object up sets stage 20 (the game's own script on the alias): expected true, was false"])
        self.assertIn("trial: Activate on the placed object returned False", got["info"])
        # the second way works, which tells a pick-up that failed from a script that did not hear
        self.assertIn("trial: after AddItem of the placed object: the player has 1, stage 20 set = True", got["info"])

    def test_a_trigger_that_holds_the_spot_where_the_player_arrives(self):
        """Someone already inside never enters. The builder refuses to write
        such a plugin; this is what the game would make of one."""
        got = self.run_with(lambda d: placed(d, TRIGGER).update(Position=arrival()["Position"]))
        self.assertEqual(got["failures"], ["trial: entering the placed trigger sets stage 10 (the game's own script on the alias): expected true, was false"])
        self.assertTrue([l for l in got["info"] if l.endswith("inside it before the move: 1")])

    def test_a_trigger_whose_script_sets_another_stage(self):
        def other_stage(d):
            alias(d, "Trigger")["Scripts"][0]["Props"][0]["Value"] = 11
        got = self.run_with(other_stage)
        self.assertEqual(got["failures"], ["trial: entering the placed trigger sets stage 10 (the game's own script on the alias): expected true, was false"])

    def test_a_trigger_that_is_no_box(self):
        # Asking it how many are inside is an error in the script log, before the move and after:
        # [documented] "only works if this is actually a trigger and will error otherwise".
        got = self.run_with(lambda d: placed(d, TRIGGER).update(Primitive=None, Box=None, CollisionLayer=None), script_errors=2)
        self.assertEqual(got["failures"], ["trial: entering the placed trigger sets stage 10 (the game's own script on the alias): expected true, was false"])

    def test_a_comparison_trigger_that_does_not_work_is_reported_and_costs_nothing(self):
        """The comparisons are there to be read, not to be scored."""
        def no_script(d):
            alias(d, "TriggerActorZone").update(Scripts=[])
        got = self.run_with(no_script)
        self.assertEqual((got["failures"], got["passed"]), ([], CHECKS))
        self.assertIn("trial: entering the trigger on the layer L_ACTORZONE: stage 12 set = False (it was False before)", got["info"])

    def test_the_comparison_trigger_left_out_is_reported_and_costs_nothing(self):
        """What a build against a master without the game's empty trigger gives."""
        def left_out(d):
            for c in d["Cells"]:
                c["Placed"] = [p for p in c["Placed"] if p["EditorId"] != GAME_TRIGGER]
            alias(d, "TriggerGameBase")["Fill"] = None
        got = self.run_with(left_out)
        self.assertEqual((got["failures"], got["passed"]), ([], CHECKS))
        self.assertIn("trial: the trigger made on the game's own empty trigger is not in this build of the plugin, "
                      "or its alias is empty: nothing was tried", got["info"])

    def test_the_plugin_built_without_the_games_master(self):
        """Nothing is placed, so nothing can be found: said plainly, and the game still closes."""
        need_build(self)
        if not SKELETON.exists():
            self.fail("%s is missing. Run tools/run_checks.sh, which builds it." % SKELETON)
        s = run_scenario(10, SCRIPTS, SKELETON, None, NATIVES, until=600.0)
        failures = [l[len("FAIL"):].strip() for l in s.user_logs["TLM"] if l.startswith("FAIL")]
        self.assertEqual(failures, ["trial: the Person alias holds a reference: expected true, was false",
                                    "trial: the reference in the Person alias is an actor: expected true, was false",
                                    "trial: the Object alias holds a reference: expected true, was false",
                                    "trial: the alias of the placed trigger holds a reference: expected true, was false"])
        self.assertEqual(s.ended, "quit")
        self.assertEqual(errors(s), [])


ALIAS_LISTENER = """Scriptname Mini:Listener extends ReferenceAlias

int entered = 0
int left = 0
int moved = 0
ObjectReference lastFrom

Event OnTriggerEnter(ObjectReference akActionRef)
	entered += 1
EndEvent

Event OnTriggerLeave(ObjectReference akActionRef)
	left += 1
EndEvent

Event OnContainerChanged(ObjectReference akNewContainer, ObjectReference akOldContainer)
	moved += 1
	lastFrom = akOldContainer
EndEvent
"""


class TheStandInsRulesForPlacedThings(unittest.TestCase):
    """Each rule as sim.py states it. None of them has been seen in the game."""

    def session(self, change=None, listen_on=()):
        need_trial_build(self)

        def with_listeners(d):
            for name in listen_on:
                alias(d, name)["Scripts"].append({"Name": "Mini:Listener", "Props": []})
            if change:
                change(d)
        folder = Path(tempfile.mkdtemp(prefix="tlm-listener-"))
        for p in SCRIPTS.glob("*.psc"):
            (folder / p.name).write_text(p.read_text())
        (folder / "Listener.psc").write_text(ALIAS_LISTENER)
        s = Session(folder, changed_plugin(with_listeners), VANILLA, NATIVES)
        s.enter_game()
        s.run(1.0)
        return s

    def started(self, **kw):
        s = self.session(**kw)
        s.start_quest(s.quests["TLM_Trial"])
        s.run(s.now + 1.0)
        return s, s.quests["TLM_Trial"]

    def move(self, s, ref, to, dx=0.0, dy=0.0, dz=0.0):
        s.spawn(s.n_objectreference_moveto(ref, None, to, dx, dy, dz), "a move")
        s.run(s.now + 1.0)

    def heard(self, quest, alias_name):
        a = [a for a in quest.aliases.values() if a.name == alias_name][0]
        return [i for i in a.scripts if i.script.name == "Mini:Listener"][0].vars

    def an_actor(self, s):
        made = s.n_objectreference_placeatme(s.player, None, s.placed[PERSON].base)
        self.assertIsInstance(made, Actor)
        return made

    def test_an_alias_is_empty_until_its_quest_starts(self):
        s = self.session()
        quest = s.quests["TLM_Trial"]
        self.assertFalse(quest.running)
        self.assertEqual([a.ref for a in quest.aliases.values()], [None] * 5)
        self.assertTrue(s.n_quest_start(quest, None))
        self.assertEqual([a.ref for a in quest.aliases.values()], [s.placed[x] for x in (PERSON, TRIGGER, GAME_TRIGGER, OBJECT, ZONE_TRIGGER)])

    def test_what_is_placed_is_where_and_how_the_plugin_says(self):
        s = self.session()
        person, trigger, thing = s.placed[PERSON], s.placed[TRIGGER], s.placed[OBJECT]
        self.assertIsInstance(person, Actor)
        self.assertTrue(person.disabled)
        self.assertFalse(trigger.disabled or thing.disabled)
        self.assertEqual(trigger.box, (150.0, 150.0, 150.0))
        self.assertIs(person.cell, s.player.cell)
        self.assertEqual(s.player.pos, tuple(arrival()["Position"]))
        self.assertFalse(person.has_3d())          # disabled
        self.assertTrue(thing.has_3d())            # it borrows a model
        self.assertFalse(trigger.has_3d())         # a box, no model

    def test_entering_a_trigger_tells_the_scripts_on_its_alias_once(self):
        s, quest = self.started(listen_on=["Trigger"])
        trigger = s.placed[TRIGGER]
        self.move(s, s.player, trigger)
        self.assertEqual((self.heard(quest, "Trigger")["entered"], self.heard(quest, "Trigger")["left"]), (1, 0))
        self.assertIn(10, quest.done)
        # moving about inside is not entering again
        self.move(s, s.player, trigger, 20.0, 20.0)
        self.assertEqual(self.heard(quest, "Trigger")["entered"], 1)
        # leaving, and coming back
        self.move(s, s.player, trigger, 0.0, 0.0, 1000.0)
        self.assertEqual(self.heard(quest, "Trigger")["left"], 1)
        self.move(s, s.player, trigger)
        self.assertEqual(self.heard(quest, "Trigger")["entered"], 2)
        self.assertEqual(s.n_objectreference_gettriggerobjectcount(trigger, None), 1)

    def test_nobody_is_told_while_the_quest_is_not_running(self):
        s = self.session(listen_on=["Trigger"])
        quest = s.quests["TLM_Trial"]
        self.move(s, s.player, s.placed[TRIGGER])
        self.assertEqual(self.heard(quest, "Trigger")["entered"], 0)
        self.assertEqual(quest.done, [])
        # and starting the quest with the player already inside tells nobody either
        s.start_quest(quest)
        s.run(s.now + 2.0)
        self.assertEqual(quest.done, [])

    def test_the_games_script_acts_for_the_player_only(self):
        s, quest = self.started(listen_on=["Trigger"])
        someone = self.an_actor(s)
        self.move(s, someone, s.placed[TRIGGER])
        self.assertEqual(self.heard(quest, "Trigger")["entered"], 1)      # the alias hears it
        self.assertNotIn(10, quest.done)                                    # the game's script lets it pass
        self.move(s, s.player, s.placed[TRIGGER])
        self.assertIn(10, quest.done)

    def test_the_box_turns_with_the_reference(self):
        def narrow(d):
            placed(d, TRIGGER).update(Box=[50.0, 300.0, 50.0], Rotation=[0.0, 0.0, 1.5707964])
        s, quest = self.started(change=narrow)
        trigger = s.placed[TRIGGER]
        # turned a quarter to the east, the long side lies east-west
        self.move(s, s.player, trigger, 0.0, 200.0)
        self.assertNotIn(10, quest.done)
        self.move(s, s.player, trigger, 200.0, 0.0)
        self.assertIn(10, quest.done)

    def test_an_actor_counts_from_its_feet_up(self):
        s, quest = self.started()
        trigger = s.placed[TRIGGER]
        below = -(trigger.box[2] + ACTOR_HEIGHT)
        self.move(s, s.player, trigger, 0.0, 0.0, below - 1.0)       # the head just under the box
        self.assertNotIn(10, quest.done)
        self.move(s, s.player, trigger, 0.0, 0.0, below + 1.0)       # the head just inside it
        self.assertIn(10, quest.done)

    def test_a_disabled_trigger_and_a_disabled_actor_do_nothing(self):
        s, quest = self.started()
        trigger = s.placed[TRIGGER]
        trigger.disabled = True
        self.move(s, s.player, trigger)
        self.assertNotIn(10, quest.done)
        # enabling it with the player inside: the player is then in it
        s.n_objectreference_enable(trigger, None)
        s.run(s.now + 1.0)
        self.assertIn(10, quest.done)

    def test_a_box_without_a_collision_layer_is_not_guessed_at(self):
        """What the builder writes when the master has no such layer. What the
        game makes of it is not known, so the stand-in stops and does not invent."""
        s, _quest = self.started(change=lambda d: placed(d, TRIGGER).update(CollisionLayer=None))
        with self.assertRaises(SimError):
            self.move(s, s.player, s.placed[TRIGGER])

    def test_only_the_property_the_plugin_sets_today_is_played(self):
        def more(d):
            alias(d, "Trigger")["Scripts"][0]["Props"].append({"Name": "PlayerTriggerOnly", "Kind": "bool", "Target": None, "Alias": None, "Value": False})
        s, _quest = self.started(change=more)
        with self.assertRaises(SimError):
            self.move(s, s.player, s.placed[TRIGGER])

    def test_picking_something_up(self):
        s, quest = self.started(listen_on=["Object"])
        thing = s.placed[OBJECT]
        self.assertIs(s.n_objectreference_activate(thing, None, s.player), True)
        s.run(s.now + 1.0)
        self.assertEqual(s.player.inventory[thing.base], 1)
        self.assertIs(thing.container, s.player)
        self.assertEqual(self.heard(quest, "Object")["moved"], 1)
        self.assertIsNone(self.heard(quest, "Object")["lastfrom"])        # picked up from the world
        self.assertIn(20, quest.done)
        # it is no longer lying there
        self.assertIs(s.n_objectreference_activate(thing, None, s.player), False)
        self.assertEqual(s.player.inventory[thing.base], 1)

    def test_somebody_else_picking_it_up_sets_no_stage(self):
        s, quest = self.started(listen_on=["Object"])
        someone = self.an_actor(s)
        self.assertIs(s.n_objectreference_activate(s.placed[OBJECT], None, someone), True)
        s.run(s.now + 1.0)
        self.assertEqual(self.heard(quest, "Object")["moved"], 1)
        self.assertNotIn(20, quest.done)
        # handed on to the player by script: now it does, and the script hears whom it came from
        s.n_objectreference_additem(s.player, None, s.placed[OBJECT])
        s.run(s.now + 1.0)
        self.assertIn(20, quest.done)
        self.assertIs(self.heard(quest, "Object")["lastfrom"], someone)
        self.assertEqual((someone.inventory[s.placed[OBJECT].base], s.player.inventory[s.placed[OBJECT].base]), (0, 1))

    def test_only_picking_up_an_item_is_modelled(self):
        s, _quest = self.started()
        with self.assertRaises(SimError):
            s.n_objectreference_activate(s.placed[TRIGGER], None, s.player)
        with self.assertRaises(SimError):
            s.n_objectreference_activate(s.placed[OBJECT], None, s.placed[TRIGGER])

    def test_asking_something_that_is_no_trigger_how_many_are_inside_is_an_error(self):
        s, _quest = self.started()
        self.assertEqual(s.n_objectreference_gettriggerobjectcount(s.placed[OBJECT], None), 0)
        self.assertEqual(len(errors(s)), 1)

    def test_the_placed_person_is_a_bystander_only_once_enabled(self):
        """Why the person starts disabled: [seen] a kill by the player is a
        fight only while somebody else stands by."""
        s, _quest = self.started()
        person = s.placed[PERSON]
        first = self.an_actor(s)
        s.n_actor_kill(first, None, s.player)
        self.assertFalse(s.player_in_combat())
        s.n_objectreference_enable(person, None)
        second = self.an_actor(s)
        s.n_actor_kill(second, None, s.player)
        self.assertTrue(s.player_in_combat())


if __name__ == "__main__":
    unittest.main()
