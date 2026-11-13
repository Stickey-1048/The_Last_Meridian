"""Tests of the stand-in engine (sim.py).

Three kinds:

  1. Replays. Every game run recorded in game_runs.json is replayed with the
     scripts as they were at that commit, and the stand-in must give the
     result the game gave: the same number of passes and failures, the same
     reported lines, the same number of stage events, and the same way of
     ending. This is what the stand-in's claim to resemble the game rests on.
  2. The scripts as they are now: every self-test scenario must pass.
  3. The stand-in's own rules, one by one, each with where the rule comes from.

They need a description of the plugin built against a master that holds the
settler and the marker. tools/run_checks.sh builds one into build/sim/.
"""
import json
import os
import re
import subprocess
import tempfile
import unittest
from pathlib import Path

from sim import FRAME, Actor, Session, SimError, run_scenario

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SCRIPTS = ROOT / "scripts" / "Source" / "User" / "TLM"
NATIVES = ROOT / "tools" / "papyrus_natives.json"
BUILD = Path(os.environ.get("TLM_SIM_BUILD", ROOT / "build" / "sim"))
PLUGIN = BUILD / "TheLastMeridian.json"
VANILLA = BUILD / "TheLastMeridian.vanilla.json"
GAME_RUNS = json.loads((HERE / "game_runs.json").read_text())["runs"]

# Scenarios that exist in the scripts as they are now.
CURRENT_SCENARIOS = list(range(1, 10))


def need_build(test):
    if not PLUGIN.exists() or not VANILLA.exists():
        test.fail("%s is missing. Run tools/run_checks.sh, which builds it." % PLUGIN)


_scripts_cache = {}


def scripts_at(commit, test):
    """The project's scripts as they were at a commit, in a folder of their own."""
    if commit in _scripts_cache:
        return _scripts_cache[commit]
    have = subprocess.run(["git", "-C", str(ROOT), "cat-file", "-e", commit + "^{commit}"], capture_output=True)
    if have.returncode != 0:
        test.skipTest("commit %s is not in this copy of the repository, so its run cannot be replayed" % commit)
    folder = Path(tempfile.mkdtemp(prefix="tlm-scripts-%s-" % commit))
    listing = subprocess.run(["git", "-C", str(ROOT), "ls-tree", "--name-only", commit, "scripts/Source/User/TLM/"],
                             capture_output=True, text=True, check=True).stdout.split()
    for name in listing:
        text = subprocess.run(["git", "-C", str(ROOT), "show", "%s:%s" % (commit, name)],
                              capture_output=True, text=True, check=True).stdout
        (folder / Path(name).name).write_text(text)
    _scripts_cache[commit] = folder
    return folder


def plugin_with(fault):
    if not fault:
        return PLUGIN
    data = json.loads(PLUGIN.read_text())
    if fault == "stages_without_items":
        for quest in data["Quests"]:
            for stage in quest["Stages"]:
                stage["Items"] = 0
    else:
        raise ValueError(fault)
    path = Path(tempfile.mkdtemp(prefix="tlm-plugin-")) / "TheLastMeridian.json"
    path.write_text(json.dumps(data))
    return path


def summary(session):
    lines = session.user_logs.get("TLM", [])
    fails = [l[len("FAIL"):].strip() for l in lines if l.startswith("FAIL")]
    overlap = [l.rsplit(": ", 1)[1] for l in lines if l.startswith("INFO") and "was still at work: " in l]
    return {
        # what the main quest's timing guards wrote to the script log (TLM_MQ01: A24 ..., A2 ..., A25 ...)
        "guard_lines": [l for l in session.papyrus_log if re.match(r"TLM_MQ01: A\d+ ", l)],
        # what a case that sets two things off at once noted about them: "True", "False", or None
        "overlap": overlap[-1] if overlap else None,
        "passed": sum(1 for l in lines if l.startswith("PASS")),
        "failed": len(fails),
        "first_failure": fails[0] if fails else None,
        "result_line": any("==== RESULT" in l for l in lines),
        "info": [l[len("INFO"):].strip() for l in lines if l.startswith("INFO")],
        "main_stage_events": sum(1 for l in session.papyrus_log if l.startswith("TLM_MQ01: stage")),
        "side_stage_events": sum(1 for l in session.papyrus_log if l.startswith("TLM_SQ01: stage")),
        "ends_by_itself": session.ended == "quit",
    }


class ReplaysOfGameRuns(unittest.TestCase):
    """The stand-in gives what the game gave, for every run the game has made."""

    def test_every_recorded_run(self):
        need_build(self)
        replayed = 0
        for run in GAME_RUNS:
            folder = scripts_at(run["commit"], self)
            plugin = plugin_with(run.get("plugin_fault"))
            for number, want in sorted(run["scenarios"].items()):
                with self.subTest(run=run["name"], scenario=number):
                    if run["how"] == "console":
                        s = Session(folder, plugin, VANILLA, NATIVES, older_scripts=True)
                        s.enter_game()
                        s.run(20.0)
                        s.console_cqf("TLM_Core", "RunSelfTest", [])
                        s.run(400.0)
                    else:
                        # The game overlapped two handlers here. The ordinary mode cannot.
                        frame = FRAME if want.get("stand_in_mode") == "calls take a frame" else 0.0
                        s = run_scenario(int(number), folder, plugin, VANILLA, NATIVES, until=400.0, older_scripts=True,
                                         native_delay=frame)
                    got = summary(s)
                    for key, value in want.items():
                        if key.startswith("stand_in_"):
                            continue                # an instruction to this replay, not something the game reported
                        have = got[key]
                        if key == "guard_lines" and frame:
                            # that mode provokes overlaps; how long one lasts in it is not a prediction
                            have = [re.sub(r"waited \d+ tenths", "waited N tenths", l) for l in have]
                            value = [re.sub(r"waited \d+ tenths", "waited N tenths", l) for l in value]
                        self.assertEqual(have, value, "%s, scenario %s: %s" % (run["name"], number, key))
                    replayed += 1
        self.assertEqual(replayed, sum(len(r["scenarios"]) for r in GAME_RUNS))


class TheScriptsAsTheyAreNow(unittest.TestCase):
    def test_every_scenario_passes(self):
        need_build(self)
        for n in CURRENT_SCENARIOS:
            with self.subTest(scenario=n):
                s = run_scenario(n, SCRIPTS, PLUGIN, VANILLA, NATIVES, until=600.0)
                got = summary(s)
                self.assertEqual(s.ended, "quit", "the scenario did not close the game by itself")
                self.assertEqual(got["failed"], 0, got["first_failure"])
                self.assertTrue(got["result_line"])
                self.assertGreater(got["passed"], 0)
                self.assertEqual([l for l in s.papyrus_log if l.startswith("error:")], [])
                self.assertEqual(s.message_boxes, [], "a message box opened with nobody there")

    def test_a_scenario_number_that_does_not_exist_fails(self):
        need_build(self)
        s = run_scenario(99, SCRIPTS, PLUGIN, VANILLA, NATIVES, until=600.0)
        got = summary(s)
        self.assertEqual(got["failed"], 1)
        self.assertIn("no scenario 99", got["first_failure"])

    def test_a_wrong_expectation_is_reported(self):
        """The stand-in is no use if it passes whatever the script says."""
        need_build(self)
        folder = Path(tempfile.mkdtemp(prefix="tlm-wrong-"))
        for p in SCRIPTS.glob("*.psc"):
            text = p.read_text()
            if p.name == "WorldCases.psc":
                old = 'test.CheckInt("C5 reputation after the hand-over", TLM_G_Rep_MercyCrossing.GetValueInt(), 2)'
                self.assertEqual(text.count(old), 1)
                text = text.replace(old, old[:-2] + "3)")
            (folder / p.name).write_text(text)
        got = summary(run_scenario(5, folder, PLUGIN, VANILLA, NATIVES))
        self.assertEqual(got["failed"], 1)
        self.assertEqual(got["first_failure"], "C5 reputation after the hand-over = 2, expected 3")

    def test_a_broken_rule_in_the_quest_script_is_reported(self):
        need_build(self)
        folder = Path(tempfile.mkdtemp(prefix="tlm-broken-"))
        for p in SCRIPTS.glob("*.psc"):
            text = p.read_text()
            if p.name == "MQ01Quest.psc":
                old = "\t\trep += 1\n"
                self.assertEqual(text.count(old), 1)
                text = text.replace(old, "\t\trep += 2\n")
            (folder / p.name).write_text(text)
        got = summary(run_scenario(5, folder, PLUGIN, VANILLA, NATIVES))
        self.assertGreaterEqual(got["failed"], 1)
        self.assertIn("reputation", got["first_failure"])


# ------------------------------------------------- the stand-in's own rules

def write_scripts(sources):
    folder = Path(tempfile.mkdtemp(prefix="tlm-mini-"))
    for name, text in sources.items():
        (folder / name).write_text(text)
    return folder


def mini_plugin(quests, records=()):
    data = {"Records": [{"Type": t, "EditorId": e, "FormKey": "", "Name": None} for t, e in records],
            "Messages": [], "Quests": quests}
    path = Path(tempfile.mkdtemp(prefix="tlm-mini-")) / "plugin.json"
    path.write_text(json.dumps(data))
    return path


def quest(editor_id, script, stages=(), aliases=(), flags=()):
    return {"EditorId": editor_id, "Flags": list(flags),
            "Stages": [{"Index": i, "CompleteQuest": False, "Items": items} for i, items in stages],
            "Objectives": [], "Aliases": list(aliases),
            "Scripts": [{"Name": script, "Props": []}]}


LANGUAGE = """Scriptname Mini:Lang extends Quest

int Property Seven = 7 Auto Const
float Property Half = 0.5 Auto Const
int counter = 0
int LIMIT = 3 Const

int Function Add(int a, int b = 10)
	Return a + b
EndFunction

int Function Loop()
	int total = 0
	int i = 0
	While i < LIMIT
		total += Seven
		i += 1
	EndWhile
	Return total
EndFunction

string Function Text()
	Return "n=" + 3 + " f=" + Half + " b=" + (1 == 1) + " none=" + None
EndFunction

int Function IntDivision()
	Return 7 / 2
EndFunction

float Function FloatDivision()
	Return 7 / 2.0
EndFunction

bool Function ShortCircuit()
	Quest nothing = None
	Return nothing && nothing.IsRunning()
EndFunction

int Function Count()
	counter += 1
	Return counter
EndFunction

bool Function CallOnNone()
	Quest nothing = None
	Return nothing.IsRunning()
EndFunction

int Function Branch(int x)
	If x < 0
		Return -1
	ElseIf x == 0
		Return 0
	Else
		Return 1
	EndIf
EndFunction

Mini:Lang Function Me()
	Return (Self as Quest) as Mini:Lang
EndFunction

Function Forever()
	While true
		Utility.Wait(1.0)
	EndWhile
EndFunction
"""


class TheLanguage(unittest.TestCase):
    def setUp(self):
        self.s = Session(write_scripts({"Lang.psc": LANGUAGE}), mini_plugin([quest("Q", "Mini:Lang")]), None, NATIVES)

    def call(self, name, *args):
        return self.s.invoke("Q", name, list(args))

    def test_arithmetic_defaults_and_loops(self):
        self.assertEqual(self.call("Add", 1, 2), 3)
        self.assertEqual(self.call("Add", 1), 11)
        self.assertEqual(self.call("Loop"), 21)
        self.assertEqual(self.call("IntDivision"), 3)
        self.assertEqual(self.call("FloatDivision"), 3.5)
        self.assertEqual([self.call("Branch", x) for x in (-5, 0, 5)], [-1, 0, 1])

    def test_values_as_text_look_as_they_do_in_the_games_log(self):
        # [seen] "dead = False", "2000.000000" in the self-test's log on 2026-11-12
        self.assertEqual(self.call("Text"), "n=3 f=0.500000 b=True none=None")

    def test_script_variables_keep_their_value_between_calls(self):
        self.assertEqual([self.call("Count"), self.call("Count")], [1, 2])

    def test_and_does_not_evaluate_its_right_side_when_the_left_is_false(self):
        self.assertIs(self.call("ShortCircuit"), False)
        self.assertEqual(self.s.papyrus_log, [])

    def test_a_call_on_none_is_logged_and_gives_a_zero_value(self):
        # [documented] "Cannot call X() on a None object, aborting function call"
        self.assertIs(self.call("CallOnNone"), False)
        self.assertEqual(len(self.s.papyrus_log), 1)
        self.assertIn("Cannot call IsRunning() on a None object", self.s.papyrus_log[0])

    def test_a_script_cast_from_its_quest_is_the_same_script(self):
        inst = self.call("Me")
        self.assertEqual(inst.script.name, "Mini:Lang")

    def test_a_function_that_never_comes_back_is_noticed(self):
        with self.assertRaises(SimError):
            self.s.invoke("Q", "Forever", [], until=30.0)

    def test_a_native_the_project_has_not_documented_stops_the_session(self):
        folder = write_scripts({"Lang.psc": "Scriptname Mini:Lang extends Quest\nFunction F()\n\tReset()\nEndFunction\n"})
        s = Session(folder, mini_plugin([quest("Q", "Mini:Lang")]), None, NATIVES)
        with self.assertRaises(SimError):
            s.invoke("Q", "F", [])

    def test_a_wrong_number_of_arguments_to_a_native_stops_the_session(self):
        folder = write_scripts({"Lang.psc": "Scriptname Mini:Lang extends Quest\nFunction F()\n\tSetStage(1, 2, 3)\nEndFunction\n"})
        s = Session(folder, mini_plugin([quest("Q", "Mini:Lang", stages=[(1, 1)])]), None, NATIVES)
        with self.assertRaises(SimError):
            s.invoke("Q", "F", [])


STAGES = """Scriptname Mini:Stages extends Quest

int seen = 0
int order = 0

Event OnStageSet(int auiStageID, int auiItemID)
	If auiStageID == 10
		SetStage(20)
		order = order * 10 + 1
	ElseIf auiStageID == 20
		order = order * 10 + 2
	EndIf
	seen += 1
EndEvent

int Function Set(int aiStage)
	SetStage(aiStage)
	Return seen
EndFunction

int Function Order()
	Return order
EndFunction
"""


class Stages(unittest.TestCase):
    def setUp(self):
        self.s = Session(write_scripts({"Stages.psc": STAGES}),
                         mini_plugin([quest("Q", "Mini:Stages", stages=[(10, 1), (20, 1), (30, 0), (40, 2)])]), None, NATIVES)
        self.q = self.s.quests["Q"]

    def test_setting_a_stage_starts_a_stopped_quest(self):
        # [seen] 2026-11-12
        self.assertFalse(self.q.running)
        self.s.invoke("Q", "Set", [20])
        self.assertTrue(self.q.running)

    def test_the_handler_has_finished_when_setstage_returns_also_when_nested(self):
        # [seen] 61 of 61 cases on 2026-11-12, including stages set inside a handler
        self.assertEqual(self.s.invoke("Q", "Set", [10]), 2)
        self.assertEqual(self.s.invoke("Q", "Order", []), 21)       # 20's handler ran inside 10's
        self.assertEqual(self.q.done, [10, 20])

    def test_a_stage_without_an_item_is_set_but_the_script_is_not_told(self):
        # [seen] the fifth run, 2026-11-12
        self.assertEqual(self.s.invoke("Q", "Set", [30]), 0)
        self.assertIn(30, self.q.done)

    def test_the_script_is_told_once_per_item(self):
        self.assertEqual(self.s.invoke("Q", "Set", [40]), 2)

    def test_a_stage_is_set_once(self):
        # [documented] "SetStage has no effect after it is called the first time"
        self.s.invoke("Q", "Set", [20])
        self.assertEqual(self.s.invoke("Q", "Set", [20]), 1)

    def test_a_stage_the_quest_does_not_have_is_an_error_in_the_log(self):
        self.s.invoke("Q", "Set", [99])
        self.assertTrue(any("no stage 99" in l for l in self.s.papyrus_log))


class RulesAboutActors(unittest.TestCase):
    """Driven from Python against the real plugin's aliases."""

    def setUp(self):
        need_build(self)
        self.s = Session(SCRIPTS, PLUGIN, VANILLA, NATIVES)
        self.mq = self.s.quests["TLM_MQ01"]
        self.s.start_quest(self.mq)
        self.alias = {a.name: a for a in self.mq.aliases.values()}
        self.settler = self.s.by_formkey[[v["FormKey"] for v in self.s.vanilla if v["EditorId"] == "WorkshopNPC"][0]]

    def actor(self, alias_name=None):
        a = self.s.n_objectreference_placeatme(self.s.player, None, self.settler)
        self.assertIsInstance(a, Actor)
        if alias_name:
            self.s.n_alias_forcerefto(self.alias[alias_name], None, a)
        return a

    def test_the_player_alias_holds_the_player(self):
        # [seen] it received OnPlayerLoadGame
        self.assertIs(self.alias["Player"].ref, self.s.player)

    def test_an_actor_in_a_protected_alias(self):
        # [seen] scenario 2, twice
        a = self.actor("CaravanDrover")
        self.assertFalse(self.s.is_essential(a))
        self.s.n_actor_kill(a, None)
        self.assertFalse(a.dead, "Kill with no killer")
        other = self.actor()
        self.s.n_actor_kill(a, None, other)
        self.assertFalse(a.dead, "Kill by someone who is not the player [documented]")
        self.s.n_actor_setprotected(a, None, False)
        self.s.n_actor_kill(a, None)
        self.assertTrue(a.dead, "after SetProtected(false)")
        b = self.actor("CaravanMaster")
        self.s.n_actor_kill(b, None, self.s.player)
        self.assertTrue(b.dead, "Kill by the player")

    def test_an_actor_in_an_essential_alias_is_not_killed_by_the_player(self):
        # [seen] scenario 4
        a = self.actor("CaravanMaster")
        self.s.n_alias_forcerefto(self.alias["CaravanMasterInTown"], None, a)
        self.assertTrue(self.s.is_essential(a))
        self.s.n_actor_kill(a, None, self.s.player)
        self.assertFalse(a.dead)

    def test_an_actor_in_no_alias_dies(self):
        a = self.actor()
        self.s.n_actor_kill(a, None)
        self.assertTrue(a.dead)

    def test_the_death_is_announced_later_and_to_the_alias_script(self):
        # [seen] IsDead true at once (scenario 6); [documented] OnDeath when the actor has finished dying
        a = self.actor("CutterLead")
        for st in (10, 20, 30):
            self.s.spawn(self.s.n_quest_setstage(self.mq, None, st), "stage")
            self.s.run(self.s.now)
        self.s.n_actor_kill(a, None, self.s.player)
        self.assertTrue(a.dead)
        self.assertNotIn(31, self.mq.done)
        self.s.run(self.s.now + 5.0)
        self.assertIn(31, self.mq.done)
        self.assertEqual(self.s.get_global("TLM_G_CaravanOutcome"), 1)

    def test_combat_with_the_player(self):
        # [seen] scenario 5: in combat once StartCombat is called, out of it two seconds after the kill
        a = self.actor("CutterLead")
        self.assertFalse(self.s.player_in_combat())
        self.s.n_actor_startcombat(a, None, self.s.player)
        self.assertTrue(self.s.player_in_combat())
        self.s.n_actor_kill(a, None, self.s.player)
        self.s.run(self.s.now + 2.0)
        self.assertFalse(self.s.player_in_combat())

    def test_a_kill_by_the_player_is_a_fight_until_it_is_announced(self):
        # [seen], indirectly: in the eleventh run (case 129) the evade timer's
        # function, called straight after Kill(player), found the player in
        # combat. [assumed]: until the death is announced and no longer; and
        # that StopCombatAlarm ends it, as the wiki says it ends all combat.
        a = self.actor("CutterLead")
        self.s.n_actor_kill(a, None, self.s.player)
        self.assertTrue(self.s.player_in_combat())
        self.s.run(self.s.now + 0.5)
        self.assertTrue(self.s.player_in_combat())
        self.s.run(self.s.now + 0.5)
        self.assertFalse(self.s.player_in_combat())
        b = self.actor("CutterA")
        self.s.n_actor_kill(b, None, self.s.player)
        self.assertTrue(self.s.player_in_combat())
        self.s.n_actor_stopcombatalarm(self.s.player, None)
        self.assertFalse(self.s.player_in_combat())
        # a death by nobody's hand is nobody's fight
        c = self.actor()
        self.s.n_actor_kill(c, None, None)
        self.assertTrue(c.dead)
        self.assertFalse(self.s.player_in_combat())

    def test_moveto_on_a_reference_with_no_model_never_comes_back(self):
        # [seen] twice on 2026-11-12
        item = self.s.n_objectreference_placeatme(self.s.player, None, self.s.forms["TLM_MISC_TornTransitPass"])
        self.assertFalse(item.has_3d())
        th = self.s.spawn(self.s.n_objectreference_moveto(item, None, self.s.player, 300.0), "move")
        self.s.run(self.s.now + 100.0)
        self.assertTrue(th.blocked)
        self.assertEqual(item.pos, self.s.player.pos)

    def test_moveto_on_the_games_marker_comes_back(self):
        # [seen] scenario 3
        marker = self.s.n_objectreference_placeatme(self.s.player, None,
                                                    self.s.by_formkey[[v["FormKey"] for v in self.s.vanilla if v["EditorId"] == "XMarker"][0]])
        th = self.s.spawn(self.s.n_objectreference_moveto(marker, None, self.s.player, 2000.0), "move")
        self.s.run(self.s.now)
        self.assertTrue(th.done)
        self.assertEqual(self.s.n_objectreference_getdistance(marker, None, self.s.player), 2000.0)


if __name__ == "__main__":
    unittest.main()
