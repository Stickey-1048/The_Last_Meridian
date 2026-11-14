"""Act I, first section, on the stand-in engine: the rough cut a person can
walk through (docs/design/TLM_ACT1_first_section.md).

Two things are tested.

The unattended check, self-test scenario 12 (TLM:Act1Walk.Audit): that it
passes on the plugin as built, that it never opens a box (nobody is there to
answer one), and that it notices what it is there to notice.

And the section as a person plays it: the stand-in's person walks the player
somewhere, presses the button on somebody or something, and answers the box
that opens. Every road through the chapter is played that way and compared,
after every step, with what the logic model says the two quests should then
hold. The model is the reference: these tests do not say what should happen,
they say that the boxes and buttons do what the model's events do.

NONE OF THIS HAS BEEN SEEN IN THE GAME. The stand-in's rules for a person
pressing a button, for a box with buttons and for EnableNoWait are assumed
(sim.py says so where they are written). A pass here means the scripts, the
plugin and the logic model agree with each other.
"""
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

from sim import Session, SimError, run_scenario
from test_sim import NATIVES, PLUGIN, ROOT, SCRIPTS, VANILLA, need_build, summary

sys.path.insert(0, str(ROOT / "tools" / "logic_model"))
sys.path.insert(0, str(ROOT / "tools"))
import tlm_model as model                                         # noqa: E402
from gen_matrix_cases import ANSWER_CODE, ANSWER_LYING, VARIANT_CODE   # noqa: E402

# What scenario 12 scores on the plugin as built against the stand-in master.
CHECKS = 42
PLAY = 900                       # the scenario number that sets the section up for a person
REF = "TLM_REF_A1_"
MSG = "TLM_MSG_A1_"
PEOPLE = 13
# The stages the logic model keeps for each quest (it has no stage for a
# button that only records an answer).
MODEL_STAGES = (10, 15, 20, 30, 31, 32, 33, 34, 35, 40, 50, 60, 100)
MODEL_SQ_STAGES = (5, 10, 20, 25, 50, 100)


def need_act1_build(test):
    need_build(test)
    data = json.loads(PLUGIN.read_text())
    cells = [p for c in data.get("Cells", []) for p in c["Placed"] if (p["EditorId"] or "").startswith(REF)]
    if not cells:
        test.skipTest("the plugin description holds nothing placed for the first section: run tools/run_checks.sh first")
    return data


def changed_plugin(change):
    """A copy of the plugin description with something changed, beside copies
    of the two files that go with it."""
    data = json.loads(PLUGIN.read_text())
    change(data)
    folder = Path(tempfile.mkdtemp(prefix="tlm-act1-"))
    (folder / PLUGIN.name).write_text(json.dumps(data))
    for name in ("TheLastMeridian.vanilla.json", "TheLastMeridian.arrivals.json"):
        shutil.copy(PLUGIN.with_name(name), folder / name)
    return folder / PLUGIN.name, folder / "TheLastMeridian.vanilla.json"


def changed_scripts(file_name, old, new):
    """The scripts folder with one piece of one script changed."""
    folder = Path(tempfile.mkdtemp(prefix="tlm-act1-scripts-"))
    for f in SCRIPTS.glob("*.psc"):
        shutil.copy(f, folder / f.name)
    text = (folder / file_name).read_text()
    if text.count(old) != 1:
        raise AssertionError("%s: %r is there %d times" % (file_name, old, text.count(old)))
    (folder / file_name).write_text(text.replace(old, new))
    return folder


def failures(session):
    return [l for l in session.user_logs.get("TLM", []) if l.startswith("FAIL")]


def placed(data, name):
    return [p for c in data["Cells"] for p in c["Placed"] if p["EditorId"] == REF + name][0]


class TheAuditAsBuilt(unittest.TestCase):
    """Scenario 12 on the plugin as it is built."""

    def setUp(self):
        need_act1_build(self)

    def test_it_passes_and_scores_what_it_should(self):
        s = run_scenario(12, SCRIPTS, PLUGIN, VANILLA, NATIVES)
        got = summary(s)
        self.assertEqual((got["passed"], got["failed"], got["ends_by_itself"], got["result_line"]), (CHECKS, 0, True, True), failures(s))

    def test_it_opens_no_box(self):
        # A box that opened would have stopped the session with an error (and
        # in the game the run, for good). This says so in so many words.
        s = run_scenario(12, SCRIPTS, PLUGIN, VANILLA, NATIVES)
        boxes = {m["EditorId"] for m in s.plugin["Messages"] if m["Box"]}
        self.assertEqual([m for m in s.messages_shown if m in boxes], [])
        self.assertEqual(s.boxes_answered, [])

    def test_it_says_how_long_each_person_took(self):
        s = run_scenario(12, SCRIPTS, PLUGIN, VANILLA, NATIVES)
        lines = [l for l in s.user_logs["TLM"] if " was there after " in l]
        self.assertEqual(len(lines), PEOPLE)

    def test_with_every_call_taking_a_frame(self):
        s = run_scenario(12, SCRIPTS, PLUGIN, VANILLA, NATIVES, native_delay=1.0 / 60.0)
        self.assertEqual((summary(s)["passed"], summary(s)["failed"]), (CHECKS, 0), failures(s))


class WhatTheAuditCatches(unittest.TestCase):
    def setUp(self):
        need_act1_build(self)

    def run_with(self, change=None, prepare=None, scripts=SCRIPTS, until=900.0):
        plugin, vanilla = changed_plugin(change) if change else (PLUGIN, VANILLA)
        s = Session(scripts, plugin, vanilla, NATIVES)
        if prepare:
            prepare(s)
        s.set_global("TLM_G_DevScenario", 12)
        s.enter_game()
        s.run(until)
        return s

    def assert_fails_on(self, s, *words):
        failed = failures(s)
        self.assertTrue(failed, "nothing failed")
        for word in words:
            self.assertTrue(any(word in f for f in failed), "%r is in none of: %s" % (word, failed))

    def test_a_marshal_who_is_alive(self):
        def alive(data):
            placed(data, "Marshal")["StartsDead"] = False
        s = self.run_with(alive)
        self.assert_fails_on(s, "the marshal is dead")
        # ... and the scenario kills him and goes on to the end.
        self.assertTrue(summary(s)["ends_by_itself"])
        self.assertEqual(summary(s)["failed"], 1, failures(s))

    def test_somebody_who_walks_off(self):
        s = self.run_with(prepare=lambda s: s.stray_override.update({REF + "Pike": True}))
        self.assert_fails_on(s, "more than 64 units from where they were placed")
        self.assertTrue(any("Ada Pike is " in l for l in s.user_logs["TLM"]))

    def test_somebody_who_never_appears(self):
        s = self.run_with(prepare=lambda s: s.never_arrives.add(REF + "Talbot"))
        self.assert_fails_on(s, "not there once everything has been switched on", "still switched off")
        self.assertTrue(any("Jonah Talbot was not there after" in l for l in s.user_logs["TLM"]))
        # It waited its seven minutes and no longer, and the watchdog did not have to end it.
        self.assertTrue(summary(s)["ends_by_itself"])
        self.assertFalse(any("did not come back" in l for l in s.user_logs["TLM"]))

    def test_a_reference_that_is_not_placed(self):
        def unplaced(data):
            ref = placed(data, "Dispatch")
            for q in data["Quests"]:
                for a in q["Aliases"]:
                    if a["Fill"] == "forced " + ref["FormKey"]:
                        a["Fill"] = None
        s = self.run_with(unplaced)
        self.assert_fails_on(s, "this quest does not hold", "do not hold what was put into them", "sets stage 20")

    def test_no_revolver_in_the_game_is_no_failure(self):
        def none(data):
            ref = placed(data, "Revolver")
            for c in data["Cells"]:
                c["Placed"] = [p for p in c["Placed"] if p is not ref]
            for q in data["Quests"]:
                for a in q["Aliases"]:
                    if a["Fill"] == "forced " + ref["FormKey"]:
                        a["Fill"] = None
        s = self.run_with(none)
        self.assertEqual(failures(s), [])
        self.assertEqual(summary(s)["passed"], CHECKS - 2)       # the stage and the rounds
        self.assertTrue(any("no revolver by any of the names" in l for l in s.user_logs["TLM"]))

    def test_a_trigger_put_into_the_wrong_alias(self):
        def swapped(data):
            a1 = [q for q in data["Quests"] if q["EditorId"] == "TLM_A1"][0]
            into = [p for p in a1["Scripts"][0]["Props"] if p["Name"] == "CastInto"][0]["Value"]
            mq = [q for q in data["Quests"] if q["EditorId"] == "TLM_MQ01"][0]
            gate = [a["Id"] for a in mq["Aliases"] if a["Name"] == "TownGate"][0]
            sight = [a["Id"] for a in mq["Aliases"] if a["Name"] == "AmbushTrigger"][0]
            for o in into:
                if o["Target"] == "TLM_MQ01" and o["Alias"] in (gate, sight):
                    o["Alias"] = gate if o["Alias"] == sight else sight
        s = self.run_with(swapped)
        self.assert_fails_on(s, "stage 40 is set before the player has entered the town gate")

    def test_a_script_that_activates_a_book_is_stopped(self):
        # Activating a book opens it to be read. The audit moves the papers
        # by script for that reason; if it ever activates one, this says so.
        scripts = changed_scripts("Act1Walk.psc", "\t\takPlayer.AddItem(paper)\n", "\t\tpaper.Activate(akPlayer)\n")
        with self.assertRaises(SimError) as raised:
            self.run_with(scripts=scripts)
        self.assertIn("a book opens to be read", str(raised.exception))

    def test_a_box_in_the_audit_is_stopped(self):
        scripts = changed_scripts("Act1Walk.psc", "Function Audit(TLM:SelfTest akTest)\n\tquiet = true\n",
                                  "Function Audit(TLM:SelfTest akTest)\n\tquiet = true\n\tShowLine(SayHaskell)\n")
        with self.assertRaises(SimError) as raised:
            self.run_with(scripts=scripts)
        self.assertIn("nobody is there to answer it", str(raised.exception))


# ------------------------------------------------------------ a person plays

class Person:
    """Somebody at the keyboard, and the logic model keeping step."""

    def __init__(self, test, coin=None, scripts=SCRIPTS):
        self.test = test
        s = Session(scripts, PLUGIN, VANILLA, NATIVES)
        s.enable_seconds = {}            # nobody waits for the people in these tests
        s.random_int = coin
        s.set_global("TLM_G_DevScenario", PLAY)
        s.enter_game()
        s.run(10.0)
        self.s = s
        self.state = model.run(["start"])
        self.caps = [f for f in s.by_formkey.values() if getattr(f, "editor_id", "") == "Caps001"][0]
        self.same("the section set up")

    # ---- what the person does
    def pause(self, seconds=2.0):
        self.s.run(self.s.now + seconds)
        if self.s.ended == "quit":
            raise AssertionError("the game was closed")

    def then(self, *events):
        for e in events:
            self.state = model.apply(self.state, e)

    def go(self, where, *events):
        self.s.walk_to(REF + where)
        self.pause()
        self.then(*events)
        self.same("walked to " + where)

    def press(self, what, answers=None, events=(), boxes=None):
        """Walks up to something, presses the button on it, and answers the
        boxes that open: answers are for the first section's own lines
        (without their prefix), boxes for any other message by its full id."""
        waiting = {MSG + m: list(b) for m, b in (answers or {}).items()}
        waiting.update({m: list(b) for m, b in (boxes or {}).items()})
        self.s.answers = waiting
        before = len(self.s.boxes_answered)
        self.s.walk_to(REF + what)
        self.s.press_activate(REF + what)
        self.pause()
        unanswered = {m: b for m, b in waiting.items() if b}
        self.test.assertEqual(unanswered, {}, "boxes the person expected and never saw, at " + what)
        self.then(*events)
        self.same("pressed " + what)
        return [m.replace(MSG, "") for m, _ in self.s.boxes_answered[before:]]

    def kill(self, who, *events, unprotect=False, by_player=True):
        actor = self.s.placed[REF + who]
        if unprotect:
            actor.protected_override = False
        self.s.n_actor_kill(actor, None, self.s.player if by_player else None)
        self.pause()
        self.test.assertTrue(actor.dead, who + " did not die")
        self.then(*events)
        self.same("killed " + who)

    def wait(self, seconds, *events):
        self.pause(seconds)
        self.then(*events)
        self.same("waited %d seconds" % seconds)

    # ---- what the game then holds
    def g(self, name):
        return self.s.get_global(name)

    def has(self, form_or_id):
        form = self.s.forms.get(form_or_id, form_or_id) if isinstance(form_or_id, str) else form_or_id
        return self.s.player.inventory.get(form, 0)

    def shown(self):
        return [m.replace(MSG, "") for m in self.s.messages_shown if m.startswith(MSG)]

    def same(self, where):
        """The two quests as the stand-in holds them, against the model."""
        s, m, t = self.s, self.state, self.test
        mq, sq = s.quests["TLM_MQ01"], s.quests["TLM_SQ01"]
        got = {
            "stages": [x for x in MODEL_STAGES if x in mq.done],
            "outcome": self.g("TLM_G_CaravanOutcome"), "method": self.g("TLM_G_CaravanMethod"),
            "alive at Mercy": self.g("TLM_G_CaravanAliveAtMercy"), "regard": self.g("TLM_G_Rep_MercyCrossing"),
            "done": self.g("TLM_G_MQ01_Done"), "variant": self.g("TLM_G_MQ01_DebriefVariant"),
            "answer": self.g("TLM_G_MQ01_DebriefAnswer"),
            "truth": self.g("TLM_Truth"), "competence": self.g("TLM_Competence"),
            "accountability": self.g("TLM_Accountability"), "mutual trust": self.g("TLM_MutualTrust"),
            "side stages": [x for x in MODEL_SQ_STAGES if x in sq.done],
            "evidence": [e for e, st in (("e1", 11), ("e2", 12), ("e3", 13), ("e4", 14)) if st in sq.done],
            "side outcome": self.g("TLM_G_SQ01_Outcome"), "yard alerted": self.g("TLM_G_SQ01_YardAlerted"),
            "Vane has it": self.g("TLM_G_SQ01_VaneHasLedger"), "Haskell blamed": self.g("TLM_G_SQ01_HaskellScapegoated"),
            "in a fight": s.player_in_combat(),
            "Nell alive": not s.placed[REF + "Nell"].dead, "Abel alive": not s.placed[REF + "Abel"].dead,
            "dispatch in hand": self.has("TLM_MISC_Dispatch") > 0,
        }
        answer = ANSWER_CODE[m.debrief_answer]
        if m.debrief_answer == "deny" and m.debrief_variant == model.V_WITNESS:
            answer = ANSWER_LYING
        want = {
            "stages": [x for x in MODEL_STAGES if m.done(x)],
            "outcome": m.outcome, "method": m.method, "alive at Mercy": m.alive_at_mercy, "regard": m.rep,
            "done": m.mq01_done, "variant": VARIANT_CODE[m.debrief_variant], "answer": answer,
            "truth": m.truth, "competence": m.competence, "accountability": m.accountability, "mutual trust": m.mutual_trust,
            "side stages": [x for x in MODEL_SQ_STAGES if m.sq_done(x)],
            "evidence": [e for e in ("e1", "e2", "e3", "e4") if getattr(m, e)],
            "side outcome": m.sq_outcome, "yard alerted": m.yard_alerted, "Vane has it": m.vane_has_ledger,
            "Haskell blamed": m.haskell_scapegoated,
            "in a fight": m.in_combat, "Nell alive": m.nell_alive, "Abel alive": m.abel_alive,
            "dispatch in hand": m.has_dispatch,
        }
        differ = {k: (got[k], want[k]) for k in got if got[k] != want[k]}
        t.assertEqual(differ, {}, "the game against the model (game, model) after: " + where)
        t.assertEqual([l for l in s.papyrus_log if l.startswith("error")], [], "after: " + where)

    # ---- pieces of road
    def to_the_ambush(self):
        self.press("Dispatch", events=["take_dispatch"])
        self.go("AmbushSight", "goto_ambush")

    def to_town(self):
        self.go("TownGate", "goto_town")

    def hand_over(self, debrief, button=0, answer_event=None, more=False):
        """The dispatch to Pritchard, what he makes of the road, and the three towns."""
        events = ["pritchard_handover"] + ([answer_event] if answer_event else []) + ["pritchard_handoff"]
        case = "PritchardCaseAndMore" if more else "PritchardCase"
        return self.press("Pritchard", {case: [0], debrief: [button], "PritchardHandOff": [0]}, events)


class TheSectionSetUpForAPerson(unittest.TestCase):
    def setUp(self):
        need_act1_build(self)

    def test_everything_is_there_and_cast(self):
        p = Person(self)
        s = p.s
        self.assertEqual([e for e, r in s.placed.items() if e.startswith(REF) and r.disabled], [])
        self.assertTrue(s.placed[REF + "Marshal"].dead)
        mq, sq = s.quests["TLM_MQ01"], s.quests["TLM_SQ01"]
        held = {a.name: a.ref.editor_id for q in (mq, sq) for a in q.aliases.values() if a.ref is not None and a.ref is not s.player}
        self.assertEqual(held["CutterLead"], REF + "Dunmore")
        self.assertEqual(held["SheriffPritchard"], REF + "Pritchard")
        self.assertEqual(held["AmbushTrigger"], REF + "AmbushSight")
        self.assertEqual(held["Ledger"], REF + "Ledger")
        self.assertEqual(len(held), 25)      # 26 puts; the marshal is in two aliases of one name
        self.assertEqual(s.notifications, ["The Last Meridian test build is loaded."])
        self.assertEqual(p.shown(), ["Begin"])
        self.assertNotEqual(s.ended, "quit")  # the game is still open
        self.assertEqual(len(s.player.equipped), 1)

    def test_setting_it_up_twice_does_nothing_more(self):
        p = Person(self)
        p.s.invoke("TLM_A1", "Begin", [])
        self.assertEqual(p.shown(), ["Begin"])

    def test_it_is_not_set_up_in_any_other_scenario(self):
        s = run_scenario(11, SCRIPTS, PLUGIN, VANILLA, NATIVES)
        self.assertFalse(s.quests["TLM_A1"].running)
        self.assertEqual([e for e, r in s.placed.items() if e.startswith(REF) and not r.disabled], [])

    def test_the_people_take_their_time_and_are_then_there(self):
        s = Session(SCRIPTS, PLUGIN, VANILLA, NATIVES)
        s.set_global("TLM_G_DevScenario", PLAY)
        s.enter_game()
        s.run(20.0)
        self.assertTrue(s.placed[REF + "Pritchard"].disabled)
        s.run(40.0)
        self.assertFalse(s.placed[REF + "Pritchard"].disabled)
        self.assertEqual([m for m in s.messages_shown if m == MSG + "Begin"], [MSG + "Begin"])


    def test_the_two_boxes_come_on_last(self):
        # A player who wanders into the place the ambush is seen from before
        # there is an ambush must not start its clock.
        s = Session(SCRIPTS, PLUGIN, VANILLA, NATIVES)
        s.set_global("TLM_G_DevScenario", PLAY)
        s.enter_game()
        s.run(15.0)
        self.assertFalse(s.placed[REF + "Dispatch"].disabled)
        self.assertTrue(s.placed[REF + "AmbushSight"].disabled)
        self.assertTrue(s.placed[REF + "TownGate"].disabled)
        s.walk_to(REF + "AmbushSight")
        s.run(20.0)
        self.assertNotIn(30, s.quests["TLM_MQ01"].done)
        s.player.pos = (0.0, 0.0, s.player.pos[2])
        s.run(40.0)
        self.assertFalse(s.placed[REF + "AmbushSight"].disabled)
        self.assertFalse(s.placed[REF + "TownGate"].disabled)
        self.assertNotIn(30, s.quests["TLM_MQ01"].done)


class EveryRoadThroughTheChapter(unittest.TestCase):
    """Each test is one road. After every step the two quests are compared
    with the logic model (Person.same)."""

    def setUp(self):
        need_act1_build(self)

    # ---- the wagon saved
    def test_talked_down(self):
        p = Person(self, coin=1)
        p.press("Revolver", events=["take_revolver"])
        self.assertEqual(p.has([f for f in p.s.by_formkey.values() if getattr(f, "kind", "") == "Ammunition"][0]), 6)
        p.to_the_ambush()
        said = p.press("Dunmore", {"DunmoreHold": [0], "DunmoreBreaks": [0]}, ["dunmore_speech_success"])
        self.assertEqual(said, ["DunmoreHold", "DunmoreBreaks"])
        self.assertEqual(p.g("TLM_G_CaravanOutcome"), 1)
        # Her thanks: who hit them, then the caps, once.
        p.press("Nell", {"NellSaved": [2], "NellWho": [0], "NellOffer": [0]}, ["nell_reward"])
        self.assertEqual(p.has(p.caps), 30)
        p.press("Nell", {"NellSavedAfter": [0]})
        self.assertEqual(p.has(p.caps), 30)
        p.press("Abel", {"AbelSaved": [0]})
        p.press("Dunmore", {"DunmoreAfter": [0]})
        p.to_town()
        p.press("Talbot", {"TalbotGate": [0]})
        p.hand_over("DebriefSaved")
        self.assertEqual((p.g("TLM_G_Rep_MercyCrossing"), p.g("TLM_G_MQ01_Done")), (2, 1))
        p.press("Talbot", {"TalbotAfter": [0]})
        p.press("Pritchard", {"PritchardAfter": [0]})
        p.press("Keene", {"KeeneHello": [0]})

    def test_her_thanks_can_be_turned_down_once(self):
        p = Person(self, coin=1)
        p.to_the_ambush()
        p.press("Dunmore", {"DunmoreHold": [0], "DunmoreBreaks": [0]}, ["dunmore_speech_success"])
        p.press("Nell", {"NellSaved": [1]}, ["nell_reward"])
        self.assertEqual(p.has(p.caps), 0)
        p.press("Nell", {"NellSavedAfter": [0]})

    def test_the_speech_fails_and_it_is_a_fight(self):
        p = Person(self, coin=0)
        p.to_the_ambush()
        p.press("Dunmore", {"DunmoreHold": [0], "DunmoreTurns": [0]}, ["dunmore_speech_fail"])
        self.assertTrue(p.s.player_in_combat())
        # He does not talk while he fights.
        p.press("Dunmore")
        p.kill("Dunmore", "player_kills_lead")
        self.assertEqual(p.g("TLM_G_CaravanOutcome"), 1)
        p.to_town()
        p.hand_over("DebriefSaved")

    def test_let_them_go_is_a_fight(self):
        p = Person(self)
        p.to_the_ambush()
        p.press("Dunmore", {"DunmoreHold": [1], "DunmoreTurns": [0]}, ["attack_cutter"])
        p.kill("Dunmore", "player_kills_lead")
        p.to_town()
        p.hand_over("DebriefSaved")

    def test_shooting_first(self):
        p = Person(self)
        p.to_the_ambush()
        p.press("Cutter1", {"CutterLive": [0]})
        p.press("Nell", {"NellLive": [0]})
        p.press("Abel", {"AbelLive": [0]})
        p.kill("Dunmore", "player_kills_lead")
        p.to_town()
        p.hand_over("DebriefSaved")

    # ---- a share taken
    def deal(self, coin=None):
        p = Person(self, coin=coin)
        p.to_the_ambush()
        p.press("Dunmore", {"DunmoreHold": [2], "DunmoreShare": [0], "DunmoreDeal": [0]}, ["dunmore_deal"])
        self.assertEqual((p.g("TLM_G_CaravanOutcome"), p.g("TLM_G_CaravanMethod")), (3, 1))
        self.assertEqual(p.has(p.caps), 20)
        self.assertEqual(p.s.placed[REF + "Wagon"].inventory, {})
        return p

    def test_a_deal_and_a_confession(self):
        p = self.deal()
        # She looks through the player: a line on the screen's edge, no box.
        p.press("Nell")
        self.assertEqual(p.shown()[-1], "NellSilent")
        p.to_town()
        p.press("Keene", {"KeeneNell": [0]})
        p.hand_over("DebriefWitness", 0, "debrief_confess")
        self.assertEqual(p.g("TLM_G_MQ01_DebriefAnswer"), 3)

    def test_a_deal_and_the_blame_on_the_cutters(self):
        p = self.deal()
        p.to_town()
        p.hand_over("DebriefWitness", 1, "debrief_blame")
        self.assertEqual(p.g("TLM_G_MQ01_DebriefAnswer"), 4)

    def test_a_deal_and_she_is_lying(self):
        p = self.deal()
        p.to_town()
        p.hand_over("DebriefWitness", 2, "debrief_deny")
        self.assertEqual(p.g("TLM_G_MQ01_DebriefAnswer"), 5)

    def test_a_deal_and_nothing_said(self):
        p = self.deal()
        p.to_town()
        p.hand_over("DebriefWitness", 3)
        self.assertEqual(p.g("TLM_G_MQ01_DebriefAnswer"), 9)

    def test_the_deal_refused_is_a_fight(self):
        p = Person(self)
        p.to_the_ambush()
        p.press("Dunmore", {"DunmoreHold": [2], "DunmoreShare": [1], "DunmoreTurns": [0]}, ["dunmore_refuse"])
        self.assertEqual(p.has(p.caps), 0)
        p.kill("Dunmore", "player_kills_lead")
        p.to_town()
        p.hand_over("DebriefSaved")

    # ---- walked past
    def walked_past(self):
        p = Person(self)
        p.to_the_ambush()
        p.press("Dunmore", {"DunmoreHold": [3]}, ["dunmore_talk", "walk_away_from_dunmore"])
        self.assertEqual(p.g("TLM_G_CaravanOutcome"), 0)
        p.wait(95, "evade_timer")
        self.assertEqual(p.g("TLM_G_CaravanOutcome"), 2)
        p.press("Nell", {"NellEvaded": [1]})
        p.to_town()
        return p

    def test_walked_past_and_admitted(self):
        p = self.walked_past()
        p.hand_over("DebriefEvaded", 0, "debrief_admit")
        self.assertEqual(p.g("TLM_G_MQ01_DebriefAnswer"), 1)

    def test_walked_past_and_denied(self):
        p = self.walked_past()
        p.hand_over("DebriefEvaded", 1, "debrief_deny")
        self.assertEqual(p.g("TLM_G_MQ01_DebriefAnswer"), 2)

    def test_walked_past_and_nothing_said(self):
        p = self.walked_past()
        p.hand_over("DebriefEvaded", 2)
        self.assertEqual(p.g("TLM_G_MQ01_DebriefAnswer"), 9)

    def test_walking_on_to_town_is_walking_past(self):
        p = Person(self)
        p.to_the_ambush()
        p.to_town()
        self.assertEqual(p.g("TLM_G_CaravanOutcome"), 2)
        p.hand_over("DebriefEvaded", 2)

    # ---- never met, lost, nobody left
    def test_the_ambush_never_met(self):
        p = Person(self)
        p.press("Dispatch", events=["take_dispatch"])
        p.to_town()
        self.assertEqual(p.g("TLM_G_CaravanOutcome"), 4)
        p.press("Nell", {"NellMissed": [0]})
        p.hand_over("DebriefMissed")

    def test_the_wagon_saved_and_its_owner_lost(self):
        p = Person(self, coin=1)
        p.to_the_ambush()
        p.press("Dunmore", {"DunmoreHold": [0], "DunmoreBreaks": [0]}, ["dunmore_speech_success"])
        p.kill("Nell", "nell_dies_other", unprotect=True, by_player=False)
        p.to_town()
        p.hand_over("DebriefLost")

    def test_the_player_shoots_the_caravan_and_nobody_is_left(self):
        p = Person(self)
        p.to_the_ambush()
        p.kill("Nell", "player_kills_nell")
        self.assertEqual((p.g("TLM_G_CaravanOutcome"), p.g("TLM_G_CaravanMethod")), (3, 2))
        p.to_town()
        p.hand_over("DebriefNoWitness")

    def test_the_one_left_to_speak_is_abel(self):
        p = Person(self, coin=1)
        p.to_the_ambush()
        p.press("Dunmore", {"DunmoreHold": [0], "DunmoreBreaks": [0]}, ["dunmore_speech_success"])
        p.kill("Nell", "player_kills_nell")
        p.to_town()
        said = p.hand_over("DebriefWitnessAbel", 2, "debrief_deny")
        self.assertNotIn("DebriefWitness", said)
        self.assertEqual(p.g("TLM_G_MQ01_DebriefAnswer"), 5)

    # ---- Pritchard before the dispatch
    def test_pritchard_before_the_dispatch_changes_nothing(self):
        p = Person(self)
        p.to_town()
        p.press("Pritchard", {"PritchardNoCase": [1], "PritchardMark": [0]}, ["pritchard_no_dispatch"])
        p.press("Pritchard", {"PritchardNoCase": [2], "PritchardMark": [0]}, ["pritchard_no_dispatch"])
        self.assertFalse(p.s.quests["TLM_MQ01"].completed)

    def test_not_yet(self):
        p = Person(self)
        p.press("Dispatch", events=["take_dispatch"])
        p.to_town()
        p.press("Pritchard", {"PritchardCase": [1]})
        self.assertNotIn(50, p.s.quests["TLM_MQ01"].done)
        p.hand_over("DebriefMissed")

    # ---- Signed Clean
    def with_the_ledger(self, p):
        p.press("Ledger", events=["take_ledger"])
        return p

    def test_the_evidence_one_piece_at_a_time(self):
        p = Person(self)
        p.press("Pike", {"PikeHello": [0]})
        p.press("Vane", {"VaneHello": [0]})
        p.press("BrakeShoes", boxes={"TLM_MSG_E1": [0]}, events=["examine_e1"])
        self.with_the_ledger(p)
        self.assertEqual(p.g("TLM_G_SQ01_EvidenceLevel"), 1)
        p.press("DrawBar", boxes={"TLM_MSG_E2": [0]}, events=["examine_e2"])
        p.press("Journal", events=["take_journal"])
        self.assertEqual(p.g("TLM_G_SQ01_EvidenceLevel"), 2)
        p.to_town()
        p.press("Pike", {"PikeBook": [1]})
        self.assertNotIn(14, p.s.quests["TLM_SQ01"].done)
        p.press("Pike", {"PikeBook": [0]}, ["pike_parts_book"])
        p.press("Pike", {"PikeAfter": [0]})

    def test_reported_while_carrying_the_dispatch(self):
        p = Person(self)
        p.press("Dispatch", events=["take_dispatch"])
        self.with_the_ledger(p)
        p.press("Journal", events=["take_journal"])
        p.to_town()
        said = p.press("Pritchard", {"PritchardCaseAndMore": [2], "PritchardReported": [0]}, ["sq_report"])
        self.assertEqual(said, ["PritchardCaseAndMore", "PritchardReported"])
        self.assertEqual((p.g("TLM_G_SQ01_Outcome"), p.g("TLM_G_SQ01_YardAlerted")), (1, 1))
        # Nothing more to report: the plain box again.
        p.hand_over("DebriefMissed")

    def test_reported_before_the_dispatch_and_after_the_chapter(self):
        p = Person(self)
        self.with_the_ledger(p)
        p.press("Journal", events=["take_journal"])
        p.to_town()
        p.press("Pritchard", {"PritchardNoCaseAndMore": [3], "PritchardReported": [0]}, ["sq_report"])
        self.assertEqual(p.g("TLM_G_SQ01_Outcome"), 1)

        q = Person(self)
        q.press("Dispatch", events=["take_dispatch"])
        self.with_the_ledger(q)
        q.press("BrakeShoes", boxes={"TLM_MSG_E1": [0]}, events=["examine_e1"])
        q.to_town()
        q.hand_over("DebriefMissed", more=True)
        q.press("Pritchard", {"PritchardAfterAndMore": [0]})
        self.assertEqual(q.g("TLM_G_SQ01_Outcome"), 0)
        q.press("Pritchard", {"PritchardAfterAndMore": [1], "PritchardReported": [0]}, ["sq_report"])
        self.assertEqual(q.g("TLM_G_SQ01_Outcome"), 1)

    def test_sold_to_vane(self):
        p = Person(self)
        self.with_the_ledger(p)
        p.press("Journal", events=["take_journal"])
        p.to_town()
        p.press("Vane", {"VaneOffer": [1]})
        self.assertEqual(p.g("TLM_G_SQ01_Outcome"), 0)
        p.press("Vane", {"VaneOffer": [0]}, ["sq_sell"])
        self.assertEqual((p.g("TLM_G_SQ01_Outcome"), p.g("TLM_G_SQ01_VaneHasLedger"), p.has(p.caps)), (5, 1, 120))
        self.assertEqual((p.has("TLM_BOOK_RailMaintLedger"), p.has("TLM_BOOK_MarshalLog")), (0, 0))
        p.press("Vane", {"VanePaid": [0]})

    def test_posted_naming_the_yard_office(self):
        p = Person(self)
        self.with_the_ledger(p)
        p.press("Journal", events=["take_journal"])
        p.to_town()
        p.press("Pike", {"PikeBook": [0]}, ["pike_parts_book"])
        p.press("NoticeBoard", boxes={"TLM_MSG_PublishChoice": [3]})
        self.assertEqual(p.g("TLM_G_SQ01_Outcome"), 0)
        p.press("NoticeBoard", boxes={"TLM_MSG_PublishChoice": [1]}, events=["sq_post_yard"])
        self.assertEqual(p.g("TLM_G_SQ01_Outcome"), 3)
        # And the board has nothing more to offer.
        p.press("NoticeBoard")

    def test_the_yard_office_cannot_be_named_on_thin_evidence(self):
        p = Person(self)
        self.with_the_ledger(p)
        p.press("BrakeShoes", boxes={"TLM_MSG_E1": [0]}, events=["examine_e1"])
        p.to_town()
        with self.assertRaises(SimError) as raised:
            p.press("NoticeBoard", boxes={"TLM_MSG_PublishChoice": [1]})
        self.assertIn("not shown as things stand", str(raised.exception))

    def test_posted_naming_haskell(self):
        p = Person(self)
        self.with_the_ledger(p)
        p.press("BrakeShoes", boxes={"TLM_MSG_E1": [0]}, events=["examine_e1"])
        p.to_town()
        p.press("Haskell", {"Haskell": [0]})
        p.press("NoticeBoard", boxes={"TLM_MSG_PublishChoice": [2]}, events=["sq_post_haskell"])
        self.assertEqual((p.g("TLM_G_SQ01_Outcome"), p.g("TLM_G_SQ01_HaskellScapegoated")), (4, 1))
        self.assertTrue(p.s.placed[REF + "Haskell"].disabled)
        p.press("Pike", {"PikeHaskell": [0]})
        p.press("Keene", {"KeeneHaskell": [0]})

    def test_posted_with_no_name(self):
        p = Person(self)
        self.with_the_ledger(p)
        p.press("DrawBar", boxes={"TLM_MSG_E2": [0]}, events=["examine_e2"])
        p.to_town()
        p.press("NoticeBoard", boxes={"TLM_MSG_PublishChoice": [0]}, events=["sq_post"])
        self.assertEqual(p.g("TLM_G_SQ01_Outcome"), 2)

    def test_burned(self):
        p = Person(self)
        # The stove does nothing for somebody without the ledger.
        p.press("Stove")
        self.with_the_ledger(p)
        p.to_town()
        p.press("Stove", boxes={"TLM_MSG_BurnLedger": [1]})
        self.assertEqual(p.g("TLM_G_SQ01_Outcome"), 0)
        p.press("Stove", boxes={"TLM_MSG_BurnLedger": [0]}, events=["sq_destroy"])
        self.assertEqual((p.g("TLM_G_SQ01_Outcome"), p.has("TLM_BOOK_RailMaintLedger")), (6, 0))


class WhatThePlayCatches(unittest.TestCase):
    """Faults put into TLM:Act1Walk on purpose: the comparison with the logic
    model, or a count of what the player was given, has to notice each."""

    def setUp(self):
        need_act1_build(self)

    def road(self, scripts, coin=1):
        p = Person(self, coin=coin, scripts=scripts)
        p.to_the_ambush()
        return p

    def test_two_answers_the_wrong_way_round(self):
        scripts = changed_scripts("Act1Walk.psc", "If told == 0\n\t\t\tTLM_MQ01.SetStage(53)", "If told == 0\n\t\t\tTLM_MQ01.SetStage(54)")
        p = self.road(scripts)
        p.press("Dunmore", {"DunmoreHold": [2], "DunmoreShare": [0], "DunmoreDeal": [0]}, ["dunmore_deal"])
        p.to_town()
        with self.assertRaises(AssertionError):
            p.hand_over("DebriefWitness", 0, "debrief_confess")

    def test_a_coin_that_always_falls_one_way(self):
        scripts = changed_scripts("Act1Walk.psc", "Return Utility.RandomInt(0, 1) == 1", "Return true")
        p = self.road(scripts, coin=0)
        # The coin fell tails and he breaks all the same: a box the person did not expect.
        with self.assertRaises((AssertionError, SimError)):
            p.press("Dunmore", {"DunmoreHold": [0], "DunmoreTurns": [0]}, ["dunmore_speech_fail"])

    def test_walking_on_that_settles_something(self):
        scripts = changed_scripts("Act1Walk.psc", "\t; \"Not my business.\": nothing.", "\tIf answer == 3\n\t\tTLM_MQ01.SetStage(32)\n\tEndIf\n\t; \"Not my business.\": nothing.")
        p = self.road(scripts)
        with self.assertRaises(AssertionError):
            p.press("Dunmore", {"DunmoreHold": [3]}, ["dunmore_talk", "walk_away_from_dunmore"])

    def test_a_share_paid_whatever_became_of_the_deal(self):
        # The player says "Done.", and before the deal is struck the wagon is
        # saved some other way (here: by a stage set while the last box is
        # open). The quest lets the first resolution stand, so there is no
        # deal and no share. The fault pays one all the same.
        def played(scripts):
            p = self.road(scripts)
            mq = p.s.quests["TLM_MQ01"]

            def meanwhile(message):
                if message == MSG + "DunmoreDeal":
                    p.s.spawn(p.s.n_quest_setstage(mq, None, 31), "the wagon is saved meanwhile")
            p.s.on_box = meanwhile
            p.s.answers = {MSG + "DunmoreHold": [2], MSG + "DunmoreShare": [0], MSG + "DunmoreDeal": [0]}
            p.s.walk_to(REF + "Dunmore")
            p.s.press_activate(REF + "Dunmore")
            p.pause()
            self.assertEqual((p.g("TLM_G_CaravanOutcome"), p.g("TLM_G_CaravanMethod")), (1, 0))
            return p.has(p.caps)
        fault = changed_scripts("Act1Walk.psc", "If Caps && Outcome() == OUT_EXPLOITED && TLM_G_CaravanMethod.GetValueInt() == METHOD_DEAL", "If Caps")
        self.assertEqual(played(fault), 20, "the fault was not put in")
        self.assertEqual(played(SCRIPTS), 0)

    def test_thanks_given_twice(self):
        scripts = changed_scripts("Act1Walk.psc", "\t\t\t\tnellThanked = true\n", "")
        p = self.road(scripts)
        p.press("Dunmore", {"DunmoreHold": [0], "DunmoreBreaks": [0]}, ["dunmore_speech_success"])
        p.press("Nell", {"NellSaved": [0]}, ["nell_reward"])
        p.press("Nell", {"NellSaved": [0]})
        self.assertEqual(p.has(p.caps), 60, "the fault was not put in")

    def test_a_line_shown_to_somebody_dead(self):
        scripts = changed_scripts("Act1Walk.psc", "If akWho && !akWho.IsDead() && !akWho.IsInCombat()", "If akWho && !akWho.IsInCombat()")
        p = self.road(scripts)
        p.kill("Dunmore", "player_kills_lead")
        # The stand-in's person does not press the button on the dead (their
        # pockets open), so the call is made as the alias's script would make it.
        p.s.answers = {MSG + "DunmoreAfter": [0]}
        p.s.invoke("TLM_A1", "Spoken", [1, p.s.placed[REF + "Dunmore"]])
        self.assertEqual(p.shown()[-1], "DunmoreAfter", "the fault was not put in")
        q = self.road(SCRIPTS)
        q.kill("Dunmore", "player_kills_lead")
        q.s.invoke("TLM_A1", "Spoken", [1, q.s.placed[REF + "Dunmore"]])
        self.assertNotIn("DunmoreAfter", q.shown())


class TheLinesAndTheScript(unittest.TestCase):
    """The plugin's messages for the section, the script that shows them and
    the numbers the two scripts share."""

    def setUp(self):
        self.data = need_act1_build(self)
        self.source = (SCRIPTS / "Act1Walk.psc").read_text()
        self.a1 = [q for q in self.data["Quests"] if q["EditorId"] == "TLM_A1"][0]

    def test_every_line_is_a_property_and_is_shown_somewhere(self):
        props = {p["Name"]: p["Target"] for p in self.a1["Scripts"][0]["Props"] if p["Kind"] == "object" and (p["Target"] or "").startswith(MSG)}
        lines = [m["EditorId"] for m in self.data["Messages"] if m["EditorId"].startswith(MSG)]
        self.assertEqual(sorted(props.values()), sorted(lines))
        body = self.source.split("; ================================================================== set-up")[1]
        for name, target in props.items():
            self.assertEqual(name, "Say" + target[len(MSG):])
            self.assertIn(name, body, "%s is never shown" % name)

    def test_every_road_played_here_shows_every_line(self):
        # Kept by hand: the lines no test above brings up. None.
        tests = Path(__file__).read_text()
        for m in self.data["Messages"]:
            if m["EditorId"].startswith(MSG):
                name = m["EditorId"][len(MSG):]
                self.assertIn('"%s"' % name, tests, "no test here brings up the line %s" % name)

    def test_the_two_scripts_agree_on_who_is_who(self):
        import re
        numbers = dict(re.findall(r"int WHO_(\w+) = (\d+) Const", self.source))
        on_aliases = {a["Name"]: s["Props"][0]["Value"] for a in self.a1["Aliases"] for s in a["Scripts"] if s["Name"] == "TLM:Act1Talk"}
        want = {"Dunmore": "DUNMORE", "Nell": "NELL", "Abel": "ABEL", "Cutter1": "CUTTER", "Cutter2": "CUTTER", "Cutter3": "CUTTER",
                "Pritchard": "PRITCHARD", "Pike": "PIKE", "Vane": "VANE", "Keene": "KEENE", "Talbot": "TALBOT", "Haskell": "HASKELL",
                "Revolver": "REVOLVER"}
        self.assertEqual(on_aliases, {alias: int(numbers[who]) for alias, who in want.items()})

    def test_no_line_names_what_act_one_does_not_know(self):
        # CANON: nobody in Act I knows of the Deep or of MERIDIAN.
        for m in self.data["Messages"]:
            if m["EditorId"].startswith(MSG):
                for word in ("Deep", "Meridian", "MERIDIAN", "Rider", "Charter", "Open Ledger", "vault", "Vault", "%"):
                    self.assertNotIn(word, m["Text"], m["EditorId"])

    def test_the_boxes_have_no_more_than_four_buttons(self):
        for m in self.data["Messages"]:
            if m["EditorId"].startswith(MSG) and m["Box"]:
                self.assertTrue(1 <= len(m["Buttons"]) <= 4, m["EditorId"])
                self.assertTrue(all(not b["Conditions"] for b in m["Buttons"]), m["EditorId"])


if __name__ == "__main__":
    unittest.main()
