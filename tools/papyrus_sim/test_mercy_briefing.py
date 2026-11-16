"""The Mercy briefing (ACT1-RUNTIME-001) on the stand-in engine.

The real scripts, TLM:Act1Walk and TLM:MercyBriefing, driven the way the game
drives them: the stand-in's person walks up to Owen Pritchard and presses the
button on him, TLM:Act1Talk on his alias calls Spoken, and the boxes that open
are answered by the place of a button. After every visit the briefing as the
stand-in holds it is compared with tools/logic_model/mercy_briefing_model.py,
and the two real quests with their own model, as test_act1.py does.

What is played for real: the chapter up to its end (the dispatch picked up,
the walk to town, the hand-over, the debrief, the hand-off), every visit to
Pritchard after it, and the book going into the inventory.

What is SEEDED, and says so where it is done: states of the main quest that
no single press reaches (a stage's handler still at work; a delivery not
acknowledged), somebody dead or in a fight while a box is open, the game not
honouring a request for the book, and a save that kept an intent and lost its
acknowledgment. The stand-in does not write or read a save: a script's
variables simply stay as they are, which is [documented] of a save and is all
that is claimed. OnPlayerLoadGame is sent, as the game sends it on a load.

The stand-in's rules these tests lean on, by how well each is known:
  [seen]       a quest whose stage completes it goes on running and its
               scripts go on answering (TLM_MQ01, in the game);
               SetStage starts a quest that is not running;
               an objective completed reads as completed.
  [documented] Message.Show returns the place of the button pressed, and -1
               at once for a message that is not a box;
               AddItem(form, 1) adds one; GetItemCount counts.
  [assumed]    a box's button place is its place in the plugin, also for a
               box of this quest; activating a living person reaches the
               script on his alias; AddItem is in the inventory by the time
               GetItemCount is next asked (if it is not, the script waits a
               second and then fails closed: see the tests of that).

NONE OF THIS HAS BEEN SEEN IN THE GAME. Not a compile and not a game test.
"""
import json
import sys
import unittest
from dataclasses import replace
from unittest.mock import patch

from sim import Actor, GlobalVariable, SimError, unwrap
from test_sim import ROOT, SCRIPTS
from test_act1 import BRIEF_HANDOFF, BRIEF_HUB, MSG, REF, Person, changed_plugin, changed_scripts, need_act1_build

sys.path.insert(0, str(ROOT / "tools" / "logic_model"))
import mercy_briefing_model as mb                                  # noqa: E402
from mercy_briefing_model import Brief, Gates, Visit               # noqa: E402

MB = "TLM_MSG_MB_"
QUEST = "TLM_MercyBriefing"
BOOK = "TLM_BOOK_Docket2298"
WHO_PRITCHARD = 5

OPEN = Gates()
RAIL = Visit(hub=mb.HUB_RAIL)
RIVER = Visit(hub=mb.HUB_RIVER)
PIKE = Visit(hub=mb.HUB_PIKE)
NOT_NOW = Visit(hub=mb.HUB_NOT_NOW)
ASK = Visit(hub=mb.HUB_PIKE, pike=mb.PIKE_ASK_QUILL)
TAKE = Visit(hub=mb.HUB_PIKE, pike=mb.PIKE_ASK_QUILL, copy=mb.COPY_TAKE)
TAKE_FAILS = replace(TAKE, add=mb.ADD_FAILS)
DEAD = replace(OPEN, briefer_alive=False)
FIGHTING = replace(OPEN, briefer_fighting=True)
PLAYER_DEAD = replace(OPEN, player_alive=False)

# Which button answers each box of a visit.
BUTTON = {mb.HUB: lambda v: v.hub, mb.PIKE: lambda v: v.pike, mb.DOCKET: lambda v: v.copy,
          mb.RAIL: lambda v: 0, mb.RIVER: lambda v: 0, mb.DOCKET_ISSUED: lambda v: 0}


class Asker:
    """Somebody who has played the chapter to its end and stands by Pritchard,
    and the briefing's model keeping step."""

    def __init__(self, test, with_ledger=False, finish=True, scripts=SCRIPTS):
        self.test = test
        self.p = Person(test, scripts=scripts)
        self.s = self.p.s
        self.quest = self.s.quests.get(QUEST)
        self.inst = self.quest.scripts[0] if self.quest and self.quest.scripts else None
        self.book = self.s.forms.get(BOOK)
        self.pritchard = self.s.placed[REF + "Pritchard"]
        self.brief = Brief()
        self.with_ledger = with_ledger
        self.add_fails = False
        self.calls = {"objective shown": 0, "objective completed": 0, "book asked for": 0, "book asked how": []}
        self._count()
        if finish:
            self.finish()
        self.before = self.world()

    # ---- the chapter, played
    def finish(self):
        """The shortest road: the dispatch, the walk to town past an ambush never met, the hand-over."""
        p = self.p
        p.press("Dispatch", events=["take_dispatch"])
        if self.with_ledger:
            # The side quest's case is then there to be reported: "There's something else from that train."
            p.press("Ledger", events=["take_ledger"])
            p.press("BrakeShoes", boxes={"TLM_MSG_E1": [0]}, events=["examine_e1"])
        p.to_town()
        shown = p.hand_over("DebriefMissed", more=self.with_ledger)
        self.test.assertEqual(p.g("TLM_G_MQ01_Done"), 1)
        self.test.assertIn(100, self.s.quests["TLM_MQ01"].done)
        return shown

    # ---- counting what the scripts ask of the game
    def _count(self):
        s = self.s
        shown, completed, add = s.n_quest_setobjectivedisplayed, s.n_quest_setobjectivecompleted, s.n_objectreference_additem

        def count_shown(quest, context, index, displayed=True, force=False):
            if quest.editor_id == QUEST:
                self.calls["objective shown"] += 1
            return shown(quest, context, index, displayed, force)

        def count_completed(quest, context, index, done=True):
            if quest.editor_id == QUEST:
                self.calls["objective completed"] += 1
            return completed(quest, context, index, done)

        def count_add(ref, context, form, count=1, silent=False):
            if unwrap(form) is self.book:
                self.calls["book asked for"] += 1
                self.calls["book asked how"].append((ref is s.player, int(count), bool(silent)))
                if self.add_fails:
                    return None            # SEEDED: the game does not honour the request
            return add(ref, context, form, count, silent)

        s.n_quest_setobjectivedisplayed = count_shown
        s.n_quest_setobjectivecompleted = count_completed
        s.n_objectreference_additem = count_add

    # ---- what the game holds
    def held(self):
        return self.s.player.inventory.get(self.book, 0)

    def state(self):
        q, v = self.quest, self.inst.vars
        return {"begun": 10 in q.done, "done": 20 in q.done, "objective shown": q.displayed.get(10, False),
                "objective complete": q.completed_objectives.get(10, False), "issued": bool(v["copyissued"]),
                "pending": bool(v["copygrantpending"]), "held": self.held(), "busy": bool(v["busy"]),
                "times shown": self.calls["objective shown"], "times completed": self.calls["objective completed"],
                "asked for": self.calls["book asked for"]}

    def model_state(self):
        b = self.brief
        return {"begun": b.begun, "done": b.done, "objective shown": b.objective_shown, "objective complete": b.objective_complete,
                "issued": b.copy_issued, "pending": b.copy_pending, "held": b.copies_held, "busy": False,
                "times shown": b.times_objective_shown, "times completed": b.times_completed, "asked for": b.add_requests}

    def world(self):
        """Everything the briefing must leave alone."""
        s = self.s
        return {
            "globals": {k: f.value for k, f in s.forms.items() if isinstance(f, GlobalVariable)},
            "stages": {q.editor_id: list(q.done) for q in s.quests.values() if q.editor_id != QUEST},
            "objectives": {q.editor_id: (dict(q.displayed), dict(q.completed_objectives)) for q in s.quests.values() if q.editor_id != QUEST},
            "completed": {q.editor_id: (q.running, q.completed) for q in s.quests.values() if q.editor_id != QUEST},
            "people": {k: (r.dead, r.disabled, r.pos, r.combat_target) for k, r in s.placed.items() if isinstance(r, Actor)},
            "carried": {getattr(f, "editor_id", repr(f)): n for f, n in s.player.inventory.items() if n and f is not self.book},
        }

    def same(self, where):
        t = self.test
        t.assertEqual(self.state(), self.model_state(), "the briefing against its model (game, model) after: " + where)
        t.assertEqual(mb.problems(self.brief), [], where)
        t.assertEqual(self.world(), self.before, "something outside the briefing changed after: " + where)
        t.assertEqual([l for l in self.s.papyrus_log if l.startswith("error")], [], where)
        self.p.same(where)                 # TLM_MQ01 and TLM_SQ01 against their own model

    # ---- seeding what no press reaches
    def gates(self):
        s, mq = self.s, self.s.quests["TLM_MQ01"]
        main = mq.scripts[0]
        acknowledged = s.invoke("TLM_MQ01", "DeliveryAcknowledged", [])
        return Gates(delivered=50 in mq.done, acknowledged=bool(acknowledged), stage60=60 in mq.done, stage100=100 in mq.done,
                     done=s.get_global("TLM_G_MQ01_Done") == 1, briefer_alive=not self.pritchard.dead,
                     briefer_fighting=self.pritchard.combat_target is not None, player_alive=not s.player.dead,
                     bound=self.inst is not None and main is not None)

    def seed(self, gates):
        """SEEDED: somebody dead or in a fight, as the gates say."""
        self.pritchard.dead = not gates.briefer_alive
        self.pritchard.combat_target = self.s.placed[REF + "Talbot"] if gates.briefer_fighting else None
        self.s.player.dead = not gates.player_alive

    # ---- a visit
    def ask(self, v, first=None, where=None):
        """Walks up to Pritchard, presses the button on him and answers as the
        visit says. Returns the briefing's messages shown, in order. What is
        shown and what the briefing then holds must be what the model says."""
        gates = self.gates()
        want, shown, took = mb.visit(self.brief, gates, v)
        answers = dict(first or {})
        for m in shown:
            if m in BUTTON:
                answers.setdefault(MB + m, []).append(BUTTON[m](v))
        if not took and first is None:
            answers[MSG + "PritchardAfter"] = [0]              # the first section's own ending
        self.add_fails = v.add == mb.ADD_FAILS

        def meanwhile(message):
            for box, after in v.after:
                if message == MB + box:
                    self.seed(after)                            # SEEDED, while that box is open
        s = self.s
        s.on_box = meanwhile if v.after else None
        s.answers = {m: list(b) for m, b in answers.items()}
        at = len(s.messages_shown)
        s.walk_to(REF + "Pritchard")
        s.press_activate(REF + "Pritchard")
        self.p.pause(3.0)
        s.on_box = None
        self.test.assertEqual({m: b for m, b in s.answers.items() if b}, {}, "boxes expected and never seen")
        got = [m[len(MB):] for m in s.messages_shown[at:] if m.startswith(MB)]
        self.test.assertEqual(got, shown, "what was shown, against the model")
        self.brief = want
        if not v.after:
            self.same(where or "a visit: %r" % (v,))
        else:
            self.test.assertEqual(self.state(), self.model_state(), "after an interrupted visit")
        return got

    def offer(self, actor=None):
        """Calls the briefing directly, as the console or another script could. For the gates no press reaches."""
        at = len(self.s.messages_shown)
        took = self.s.invoke(QUEST, "Offer", [actor if actor is not None else self.pritchard])
        return bool(took), self.s.messages_shown[at:]


class TheHandOff(unittest.TestCase):
    def setUp(self):
        need_act1_build(self)

    def test_the_hand_off_says_he_can_be_asked_again(self):
        a = Asker(self, finish=False)
        shown = a.finish()
        self.assertNotIn("PritchardHandOff", shown)
        self.assertIn(BRIEF_HANDOFF, a.s.messages_shown)
        self.assertEqual(a.s.messages_shown.count(BRIEF_HANDOFF), 1)
        # The hand-off itself begins nothing of the briefing.
        self.assertFalse(a.quest.running)
        self.assertEqual(a.state(), a.model_state())
        self.assertEqual(a.held(), 0)

    def test_the_chapter_ends_as_it_did(self):
        a = Asker(self)
        mq = a.s.quests["TLM_MQ01"]
        self.assertEqual([x for x in (50, 60, 100) if x in mq.done], [50, 60, 100])
        self.assertEqual((a.p.g("TLM_G_MQ01_Done"), a.p.g("TLM_G_Rep_MercyCrossing"), a.p.g("TLM_G_MQ01_DebriefVariant")), (1, 1, 5))
        a.p.same("the chapter's end")


class TheGates(unittest.TestCase):
    """Only the final acknowledged state opens it."""

    def setUp(self):
        need_act1_build(self)

    def nothing_of_the_briefing(self, a):
        # (Its quest record may be running, if the briefing was called at all: that sets no stage and shows nothing.)
        self.assertEqual([m for m in a.s.messages_shown if m.startswith(MB) and m != BRIEF_HANDOFF], [])
        self.assertEqual((a.quest.done, a.quest.displayed, a.quest.completed_objectives, a.quest.completed), ([], {}, {}, False))
        self.assertIsNone(a.quest.aliases[0].ref)
        self.assertEqual((a.held(), a.calls["book asked for"], a.calls["objective shown"]), (0, 0, 0))

    def test_no_dispatch(self):
        a = Asker(self, finish=False)
        a.p.to_town()
        a.p.press("Pritchard", {"PritchardNoCase": [0], "PritchardMark": [0]})
        self.nothing_of_the_briefing(a)
        self.assertEqual(a.offer(), (False, []))
        self.nothing_of_the_briefing(a)

    def test_the_dispatch_carried_and_not_handed_over(self):
        a = Asker(self, finish=False)
        a.p.press("Dispatch", events=["take_dispatch"])
        a.p.to_town()
        a.p.press("Pritchard", {"PritchardCase": [1]})          # "Not yet."
        self.nothing_of_the_briefing(a)
        self.assertEqual(a.offer(), (False, []))
        self.nothing_of_the_briefing(a)

    def test_delivered_and_acknowledged_with_60_absent(self):
        # Real: asked while the debrief box, and then the hand-off box, is open. 50 is set and
        # acknowledged by then; 60 is not.
        a = Asker(self, finish=False)
        a.p.press("Dispatch", events=["take_dispatch"])
        a.p.to_town()
        seen = []

        def meanwhile(message):
            mq = a.s.quests["TLM_MQ01"]
            fn = a.inst.script.functions["offer"]

            def asked():
                took = yield from a.s.call(a.inst, fn, [a.pritchard])
                seen.append((message, 50 in mq.done, 60 in mq.done, bool(took)))
            a.s.spawn(asked(), "asked while %s is open" % message)
        a.s.on_box = meanwhile
        a.p.hand_over("DebriefMissed")
        a.s.on_box = None
        self.assertEqual(seen, [(MSG + "PritchardCase", False, False, False), (MSG + "DebriefMissed", True, False, False),
                                (BRIEF_HANDOFF, True, False, False)])
        self.nothing_of_the_briefing(a)

    def seeded(self, change):
        a = Asker(self)
        change(a)
        self.assertFalse(a.gates().open())
        self.assertEqual(a.offer(), (False, []))
        self.assertEqual(a.s.invoke("TLM_A1", "OfferBriefing", [a.pritchard]), False)
        self.nothing_of_the_briefing(a)
        return a

    def test_delivered_and_not_acknowledged(self):
        def change(a):                      # SEEDED: stage 50 with its handler's work not finished
            mq = a.s.quests["TLM_MQ01"]
            mq.done.remove(60)
            mq.done.remove(100)
            a.s.set_global("TLM_G_MQ01_Done", 0)
            mq.completed_objectives[20] = False
            mq.scripts[0].vars["deliveryfinished"] = False
        a = self.seeded(change)
        self.assertEqual((a.gates().delivered, a.gates().acknowledged), (True, False))

    def test_60_set_and_its_handler_still_at_work(self):
        def change(a):                      # SEEDED: 60 is set; 100 and the Done global are not yet
            a.s.quests["TLM_MQ01"].done.remove(100)
            a.s.set_global("TLM_G_MQ01_Done", 0)
        a = self.seeded(change)
        self.assertEqual((a.gates().stage60, a.gates().stage100, a.gates().done), (True, False, False))

    def test_100_without_the_done_global_and_the_other_way_round(self):
        self.seeded(lambda a: a.s.set_global("TLM_G_MQ01_Done", 0))
        self.seeded(lambda a: a.s.quests["TLM_MQ01"].done.remove(100))

    def test_in_those_states_he_says_what_he_always_said(self):
        # SEEDED as above: 60 set, 100 and Done not. Pressed for real: the first section's own ending.
        a = Asker(self)
        a.s.quests["TLM_MQ01"].done.remove(100)
        a.s.set_global("TLM_G_MQ01_Done", 0)
        a.s.answers = {MSG + "PritchardAfter": [0]}
        a.s.walk_to(REF + "Pritchard")
        a.s.press_activate(REF + "Pritchard")
        a.p.pause()
        self.assertEqual(a.s.messages_shown[-1], MSG + "PritchardAfter")
        self.nothing_of_the_briefing(a)

    def test_pritchard_dead(self):
        a = self.seeded(lambda a: a.seed(DEAD))
        # Through the first section's own door as well: Spoken turns a dead man away.
        at = len(a.s.messages_shown)
        a.s.invoke("TLM_A1", "Spoken", [WHO_PRITCHARD, a.pritchard])
        self.assertEqual(a.s.messages_shown[at:], [])

    def test_pritchard_in_a_fight(self):
        a = self.seeded(lambda a: a.seed(FIGHTING))
        at = len(a.s.messages_shown)
        a.s.invoke("TLM_A1", "Spoken", [WHO_PRITCHARD, a.pritchard])
        self.assertEqual(a.s.messages_shown[at:], [])

    def test_the_player_dead(self):
        self.seeded(lambda a: a.seed(PLAYER_DEAD))

    def test_nobody_passed_on(self):
        a = Asker(self)
        self.assertEqual(a.offer(actor=False), (False, []))      # None
        # TalkPritchard called as it always was, with nobody: the first section's own ending.
        a.s.answers = {MSG + "PritchardAfter": [0]}
        a.s.invoke("TLM_A1", "TalkPritchard", [])
        self.assertEqual(a.s.messages_shown[-1], MSG + "PritchardAfter")
        self.nothing_of_the_briefing(a)

    def test_somebody_else_is_not_pritchard_but_whoever_is_activated_is_who_briefs(self):
        # The briefing takes whoever the first section passes on; it does not look for a test-room actor.
        a = Asker(self)
        a.ask(NOT_NOW)
        self.assertIs(a.quest.aliases[0].ref, a.pritchard)

    def test_the_final_state_opens_it(self):
        a = Asker(self)
        self.assertTrue(a.gates().open())
        self.assertEqual(a.ask(NOT_NOW), [mb.HUB])


class Interrupted(unittest.TestCase):
    """Somebody dies, or a fight begins, while a box is open (SEEDED while it
    is open). What was shown stays shown; nothing after it is set or given."""

    def setUp(self):
        need_act1_build(self)

    def test_while_the_hub_is_open(self):
        for gates in (DEAD, FIGHTING, PLAYER_DEAD):
            for v in (RAIL, PIKE, TAKE):
                with self.subTest(gates=gates, v=v):
                    a = Asker(self)
                    self.assertEqual(a.ask(replace(v, after=((mb.HUB, gates),))), [mb.HUB])
                    self.assertEqual((a.state()["begun"], a.state()["done"], a.held()), (True, False, 0))

    def test_while_a_brief_is_open(self):
        for gates in (DEAD, FIGHTING, PLAYER_DEAD):
            a = Asker(self)
            self.assertEqual(a.ask(replace(RAIL, after=((mb.RAIL, gates),))), [mb.HUB, mb.RAIL])
            self.assertFalse(a.state()["done"])
            self.assertEqual(a.calls["objective completed"], 0)

    def test_while_the_pike_brief_is_open_the_copy_is_not_even_discussed(self):
        a = Asker(self)
        self.assertEqual(a.ask(replace(TAKE, after=((mb.PIKE, DEAD),))), [mb.HUB, mb.PIKE])
        self.assertEqual((a.held(), a.calls["book asked for"], a.state()["done"]), (0, 0, False))

    def test_while_the_copy_is_offered_none_is_given(self):
        for gates in (DEAD, FIGHTING, PLAYER_DEAD):
            a = Asker(self)
            self.assertEqual(a.ask(replace(TAKE, after=((mb.DOCKET, gates),))), [mb.HUB, mb.PIKE, mb.DOCKET])
            self.assertEqual((a.held(), a.calls["book asked for"]), (0, 0))
            self.assertEqual((a.state()["issued"], a.state()["pending"], a.state()["done"]), (False, False, False))

    def test_asked_again_afterwards_it_goes_on_from_where_it_was(self):
        a = Asker(self)
        a.ask(replace(RAIL, after=((mb.RAIL, FIGHTING),)))
        a.seed(OPEN)                                             # SEEDED: the fight is over
        a.before = a.world()
        self.assertEqual(a.ask(RAIL), [mb.HUB, mb.RAIL])
        self.assertTrue(a.state()["done"])
        self.assertEqual((a.calls["objective shown"], a.calls["objective completed"]), (1, 1))

    def test_a_box_that_gives_no_answer(self):
        # SEEDED: Show comes back with -1, as [documented] for a message that is not shown as a box.
        for stale, want_done in ((MB + mb.HUB, False), (MB + mb.RAIL, False), (MB + mb.PIKE, False)):
            with self.subTest(stale):
                a = Asker(self)
                show = a.s.n_message_show

                def no_answer(m, context, *floats, stale=stale, show=show):
                    if m.editor_id == stale:
                        a.s.messages_shown.append(m.editor_id)
                        return -1
                    return show(m, context, *floats)
                a.s.n_message_show = no_answer
                a.s.answers = {BRIEF_HUB: [mb.HUB_PIKE if stale.endswith("Pike") else mb.HUB_RAIL]}
                if stale == BRIEF_HUB:
                    a.s.answers = {}
                a.s.walk_to(REF + "Pritchard")
                a.s.press_activate(REF + "Pritchard")
                a.p.pause()
                self.assertEqual(a.state()["done"], want_done)
                self.assertEqual((a.held(), a.calls["book asked for"], a.calls["objective completed"]), (0, 0, 0))
                self.assertFalse(a.state()["busy"])


class TheMenu(unittest.TestCase):
    """Every button, by its place."""

    def setUp(self):
        need_act1_build(self)

    def test_the_script_and_the_model_number_the_buttons_alike(self):
        a = Asker(self, finish=False)
        for name in ("HUB_RAIL", "HUB_RIVER", "HUB_PIKE", "HUB_NOT_NOW", "PIKE_ASK_QUILL", "PIKE_CONTINUE", "COPY_TAKE", "COPY_LEAVE"):
            self.assertEqual(a.inst.vars[name.lower()], getattr(mb, name), name)
        plugin = json.loads(__import__("test_sim").PLUGIN.read_text())
        buttons = {m["EditorId"]: [b["Text"] for b in m["Buttons"]] for m in plugin["Messages"]}
        self.assertEqual(buttons[MB + "Hub"][mb.HUB_RAIL], "The rail.")
        self.assertEqual(buttons[MB + "Hub"][mb.HUB_RIVER], "The river.")
        self.assertEqual(buttons[MB + "Hub"][mb.HUB_PIKE], "Red Hollow.")
        self.assertEqual(buttons[MB + "Hub"][mb.HUB_NOT_NOW], "Not now.")
        self.assertEqual(buttons[MB + "Pike"][mb.PIKE_ASK_QUILL], "What should I ask Quill?")
        self.assertEqual(buttons[MB + "Pike"][mb.PIKE_CONTINUE], "Continue")
        self.assertEqual(buttons[MB + "Docket"][mb.COPY_TAKE], "Take the review copy.")
        self.assertEqual(buttons[MB + "Docket"][mb.COPY_LEAVE], "Leave the copy.")

    def test_not_now(self):
        a = Asker(self)
        self.assertEqual(a.ask(NOT_NOW), [mb.HUB])
        self.assertEqual((a.state()["begun"], a.state()["done"]), (True, False))

    def test_the_three_briefs_each_by_its_own_button(self):
        for v, leaf in ((RAIL, mb.RAIL), (RIVER, mb.RIVER), (PIKE, mb.PIKE)):
            with self.subTest(leaf):
                a = Asker(self)
                self.assertEqual(a.ask(v), [mb.HUB, leaf])
                self.assertTrue(a.state()["done"])
                self.assertEqual(a.held(), 0)

    def test_the_pike_and_what_to_ask_quill(self):
        a = Asker(self)
        self.assertEqual(a.ask(ASK), [mb.HUB, mb.PIKE, mb.DOCKET])           # "Leave the copy."
        self.assertEqual(a.held(), 0)
        self.assertEqual(a.ask(ASK), [mb.HUB, mb.PIKE, mb.DOCKET])           # still offered: none was taken
        self.assertEqual(a.ask(TAKE), [mb.HUB, mb.PIKE, mb.DOCKET])
        self.assertEqual(a.held(), 1)

    def test_a_visit_is_one_road_and_then_it_is_over(self):
        a = Asker(self)
        for v in (RAIL, RIVER, PIKE, ASK, TAKE, NOT_NOW):
            shown = a.ask(v)
            self.assertEqual(shown.count(mb.HUB), 1)
            self.assertLessEqual(len([m for m in shown if m in (mb.RAIL, mb.RIVER, mb.PIKE)]), 1)
            self.assertLessEqual(len(shown), 4)

    def test_he_can_be_asked_as_often_as_one_likes(self):
        a = Asker(self)
        for _ in range(3):
            for v in (NOT_NOW, RAIL, RIVER, PIKE, ASK):
                a.ask(v)
        self.assertEqual((a.calls["objective shown"], a.calls["objective completed"]), (1, 1))
        self.assertEqual(a.quest.done, [10, 20])
        self.assertTrue(a.quest.completed and a.quest.running)

    def test_the_report_keeps_its_button_and_its_place(self):
        a = Asker(self, with_ledger=True)
        after = MSG + "PritchardAfterAndMore"
        # Continue: on to the briefing. The side quest is as it was.
        self.assertEqual(a.ask(RAIL, first={after: [0]}), [mb.HUB, mb.RAIL])
        self.assertEqual(a.p.g("TLM_G_SQ01_Outcome"), 0)
        self.assertEqual(a.ask(NOT_NOW, first={after: [0]}), [mb.HUB])
        # "There's something else from that train.": the report, and no briefing in that visit.
        at = len(a.s.messages_shown)
        a.p.press("Pritchard", {"PritchardAfterAndMore": [1], "PritchardReported": [0]}, ["sq_report"])
        self.assertEqual(a.s.messages_shown[at:], [after, MSG + "PritchardReported"])
        self.assertEqual(a.p.g("TLM_G_SQ01_Outcome"), 1)
        # With the case reported there is nothing more to report: the briefing comes at once.
        a.before = a.world()
        at = len(a.s.messages_shown)
        self.assertEqual(a.ask(PIKE), [mb.HUB, mb.PIKE])
        self.assertNotIn(after, a.s.messages_shown[at:])

    def test_the_report_is_there_before_and_after_the_briefing_is_complete(self):
        a = Asker(self, with_ledger=True)
        after = MSG + "PritchardAfterAndMore"
        a.ask(TAKE, first={after: [0]})
        self.assertTrue(a.state()["done"])
        a.p.press("Pritchard", {"PritchardAfterAndMore": [1], "PritchardReported": [0]}, ["sq_report"])
        self.assertEqual(a.p.g("TLM_G_SQ01_Outcome"), 1)

    def test_the_boxes_have_no_more_than_four_buttons_and_none_is_conditional(self):
        plugin = json.loads(__import__("test_sim").PLUGIN.read_text())
        for m in plugin["Messages"]:
            if m["EditorId"].startswith(MB) and m["Box"]:
                self.assertTrue(1 <= len(m["Buttons"]) <= 4, m["EditorId"])
                self.assertTrue(all(not b["Conditions"] for b in m["Buttons"]), m["EditorId"])


class TheTask(unittest.TestCase):
    def setUp(self):
        need_act1_build(self)

    def test_it_starts_on_the_first_hub_and_not_before(self):
        a = Asker(self)
        self.assertFalse(a.quest.running)                         # the whole chapter was played, and nothing of it yet
        self.assertEqual((a.quest.done, a.quest.displayed), ([], {}))
        a.ask(NOT_NOW)
        self.assertTrue(a.quest.running)
        self.assertEqual((a.quest.done, a.quest.displayed, a.quest.completed), ([10], {10: True}, False))
        a.ask(NOT_NOW)
        self.assertEqual(a.calls["objective shown"], 1)

    def test_it_completes_only_after_a_brief_was_shown(self):
        a = Asker(self)
        a.ask(NOT_NOW)
        a.ask(NOT_NOW)
        self.assertEqual((a.quest.done, a.calls["objective completed"]), ([10], 0))
        a.ask(RIVER)
        self.assertEqual((a.quest.done, a.quest.completed, a.quest.completed_objectives), ([10, 20], True, {10: True}))

    def test_it_stays_complete_and_goes_on_answering(self):
        a = Asker(self)
        a.ask(RAIL)
        for v in (RIVER, NOT_NOW, PIKE, TAKE, RAIL):
            a.ask(v)
        self.assertEqual((a.quest.done, a.calls["objective shown"], a.calls["objective completed"]), ([10, 20], 1, 1))
        self.assertTrue(a.quest.running)

    def test_it_is_not_a_later_quest_and_sets_nothing_on_the_two_real_ones(self):
        a = Asker(self)
        for v in (NOT_NOW, RAIL, RIVER, PIKE, ASK, TAKE, TAKE):
            a.ask(v)                       # each compares the whole world outside the briefing with what it was
        self.assertEqual(sorted(a.s.quests), ["TLM_A1", "TLM_Core", "TLM_MQ01", "TLM_MercyBriefing", "TLM_SQ01", "TLM_Trial"])
        self.assertEqual(a.p.has("Caps001") if "Caps001" in a.s.forms else a.p.has(a.p.caps), a.before["carried"].get("Caps001", 0))
        source = (SCRIPTS / "MercyBriefing.psc").read_text()
        code = "\n".join(l.split(";")[0] for l in source.split("}", 1)[1].splitlines())
        for forbidden in ("SetValue", ".Mod(", "RemoveItem", "TLM_MQ01.SetStage", "TLM_SQ01", "Kill(", "MoveTo", "StartTimer",
                          "RegisterFor", "OnInit", "OnPlayerLoadGame", "OnQuestInit", "Enable", "Disable", "Stop()", "Reset()"):
            self.assertNotIn(forbidden, code, forbidden)

    def test_the_load_event_changes_nothing(self):
        a = Asker(self)
        a.ask(TAKE)
        before, world = a.state(), a.world()
        a.s.actor_event(a.s.player, "OnPlayerLoadGame", [], 0)       # as the game sends it on a load
        a.p.pause()
        self.assertEqual(a.state(), before)
        self.assertEqual(a.world(), world)
        a.ask(TAKE)
        self.assertEqual((a.held(), a.calls["book asked for"]), (1, 1))


class TheCopy(unittest.TestCase):
    def setUp(self):
        need_act1_build(self)

    def test_none_without_the_explicit_take(self):
        a = Asker(self)
        for v in (NOT_NOW, RAIL, RIVER, PIKE, ASK):
            a.ask(v)
            self.assertEqual((a.held(), a.calls["book asked for"]), (0, 0))
        self.assertFalse(a.s.invoke(QUEST, "HasReviewCopy", []))

    def test_take_gives_exactly_one_to_the_player(self):
        a = Asker(self)
        self.assertEqual(a.held(), 0)
        self.assertEqual(a.ask(TAKE), [mb.HUB, mb.PIKE, mb.DOCKET])
        self.assertEqual(a.held(), 1)
        self.assertEqual(a.calls["book asked how"], [(True, 1, False)])
        self.assertTrue(a.s.invoke(QUEST, "HasReviewCopy", []))
        self.assertTrue(a.s.invoke(QUEST, "WasCopyIssued", []))
        self.assertFalse(a.s.invoke(QUEST, "IsCopyGrantPending", []))

    def test_no_second_copy_however_often_it_is_asked_for(self):
        a = Asker(self)
        a.ask(TAKE)
        for _ in range(3):
            self.assertEqual(a.ask(TAKE), [mb.HUB, mb.PIKE, mb.DOCKET_ISSUED, mb.NOTE_ISSUED])
        self.assertEqual((a.held(), a.calls["book asked for"]), (1, 1))

    def test_a_second_activation_while_a_box_is_open_gives_nothing_more(self):
        a = Asker(self)
        extra = []

        def meanwhile(message):
            # While each box is open: the first section's door is tried again (Spoken, as a second
            # activation would), and the briefing is called directly (as the console could).
            walk = a.s.quests["TLM_A1"].scripts[0]
            spoken, offer = walk.script.functions["spoken"], a.inst.script.functions["offer"]

            def again():
                yield from a.s.call(walk, spoken, [WHO_PRITCHARD, a.pritchard])
                extra.append((message, bool((yield from a.s.call(a.inst, offer, [a.pritchard])))))
            a.s.spawn(again(), "a second call while %s is open" % message)
        a.s.on_box = meanwhile
        a.s.answers = {BRIEF_HUB: [mb.HUB_PIKE], MB + mb.PIKE: [mb.PIKE_ASK_QUILL], MB + mb.DOCKET: [mb.COPY_TAKE]}
        a.s.walk_to(REF + "Pritchard")
        a.s.press_activate(REF + "Pritchard")
        a.p.pause(3.0)
        a.s.on_box = None
        self.assertEqual([m[len(MB):] for m in a.s.messages_shown if m.startswith(MB) and m != BRIEF_HANDOFF], [mb.HUB, mb.PIKE, mb.DOCKET])
        self.assertEqual(extra, [(BRIEF_HUB, True), (MB + mb.PIKE, True), (MB + mb.DOCKET, True)])   # taken, and nothing done
        self.assertEqual((a.held(), a.calls["book asked for"], a.calls["objective shown"], a.calls["objective completed"]), (1, 1, 1, 1))
        self.assertFalse(a.state()["busy"])

    def test_dropped_stored_or_removed_it_is_not_held_and_is_not_given_again(self):
        a = Asker(self)
        a.ask(TAKE)
        crate = a.s.placed[REF + "Wagon"]
        # Put into a container: out of the inventory.
        a.s.n_objectreference_removeitem(a.s.player, None, a.book, 1, True, crate)
        a.brief = mb.drop(a.brief)
        self.assertEqual(a.held(), 0)
        self.assertFalse(a.s.invoke(QUEST, "HasReviewCopy", []))
        self.assertTrue(a.s.invoke(QUEST, "WasCopyIssued", []))
        self.assertTrue(a.state()["done"])
        self.assertEqual(a.ask(TAKE), [mb.HUB, mb.PIKE, mb.DOCKET_ISSUED, mb.NOTE_ISSUED])
        self.assertEqual((a.held(), a.calls["book asked for"]), (0, 1))
        # Taken out again: held.
        a.s.n_objectreference_removeitem(crate, None, a.book, 1, True, a.s.player)
        a.brief = mb.retrieve(a.brief)
        self.assertEqual(a.held(), 1)
        self.assertTrue(a.s.invoke(QUEST, "HasReviewCopy", []))
        self.assertEqual(a.ask(TAKE), [mb.HUB, mb.PIKE, mb.DOCKET_ISSUED, mb.NOTE_ISSUED])
        self.assertEqual((a.held(), a.calls["book asked for"]), (1, 1))

    def test_holding_it_is_read_from_the_inventory_and_from_nothing_else(self):
        a = Asker(self)
        a.ask(TAKE)
        a.s.player.inventory[a.book] = 0                          # removed from the inventory
        a.brief = mb.drop(a.brief)
        self.assertEqual((a.state()["done"], a.state()["issued"]), (True, True))
        self.assertFalse(a.s.invoke(QUEST, "HasReviewCopy", []))

    def test_a_copy_already_carried_means_none_is_offered(self):
        # SEEDED: a copy in the inventory that the briefing never gave (the console, say).
        a = Asker(self)
        a.s.player.inventory[a.book] = 1
        a.s.answers = {BRIEF_HUB: [mb.HUB_PIKE], MB + mb.PIKE: [mb.PIKE_ASK_QUILL], MB + mb.DOCKET_ISSUED: [0]}
        a.s.walk_to(REF + "Pritchard")
        a.s.press_activate(REF + "Pritchard")
        a.p.pause()
        self.assertEqual(a.s.messages_shown[-2:], [MB + mb.DOCKET_ISSUED, MB + mb.NOTE_ISSUED])
        self.assertEqual((a.held(), a.calls["book asked for"]), (1, 0))

    def test_the_task_never_waits_on_the_copy(self):
        for v in (PIKE, ASK, TAKE, TAKE_FAILS):
            a = Asker(self)
            a.ask(v)
            self.assertTrue(a.state()["done"])


class TheHandOverFails(unittest.TestCase):
    """The game does not honour the request, or the acknowledgment is lost."""

    def setUp(self):
        need_act1_build(self)

    def test_a_request_not_honoured_fails_closed(self):
        a = Asker(self)
        self.assertEqual(a.ask(TAKE_FAILS), [mb.HUB, mb.PIKE, mb.DOCKET, mb.NOTE_PENDING])
        self.assertEqual((a.held(), a.calls["book asked for"]), (0, 1))
        self.assertEqual((a.state()["issued"], a.state()["pending"]), (False, True))
        self.assertFalse(a.s.invoke(QUEST, "HasReviewCopy", []))
        self.assertFalse(a.s.invoke(QUEST, "WasCopyIssued", []))
        said = [l for l in a.s.papyrus_log if "FAIL CLOSED" in l]
        self.assertEqual(len(said), 1)
        self.assertIn("is not asked for again", said[0])
        self.assertIn("CopyGrantPending=True", said[0].replace("true", "True"))

    def test_it_is_never_asked_for_again(self):
        a = Asker(self)
        a.ask(TAKE_FAILS)
        for _ in range(3):
            self.assertEqual(a.ask(TAKE), [mb.HUB, mb.PIKE, mb.DOCKET_ISSUED, mb.NOTE_PENDING])
        self.assertEqual((a.held(), a.calls["book asked for"]), (0, 1))
        self.assertTrue(a.state()["pending"])

    def test_the_three_briefs_still_work(self):
        a = Asker(self)
        a.ask(TAKE_FAILS)
        self.assertEqual([a.ask(v) for v in (RAIL, RIVER, PIKE, NOT_NOW)], [[mb.HUB, mb.RAIL], [mb.HUB, mb.RIVER], [mb.HUB, mb.PIKE], [mb.HUB]])

    def test_a_copy_that_was_delivered_after_all_is_acknowledged_and_not_doubled(self):
        a = Asker(self)
        a.ask(TAKE_FAILS)
        a.s.player.inventory[a.book] = 1          # SEEDED: the one book asked for is in the inventory after all
        a.brief = mb.late_arrival(a.brief)
        self.assertTrue(a.s.invoke(QUEST, "HasReviewCopy", []))
        self.assertEqual(a.ask(TAKE), [mb.HUB, mb.PIKE, mb.DOCKET_ISSUED, mb.NOTE_ISSUED])
        self.assertEqual((a.held(), a.calls["book asked for"]), (1, 1))
        self.assertEqual((a.state()["issued"], a.state()["pending"]), (True, False))

    def test_a_save_between_the_intent_and_its_acknowledgment(self):
        # SEEDED: what a save holds if it was made after the intent was written down and the
        # script never got to read the count: CopyGrantPending, nothing issued, nobody busy.
        for delivered in (False, True):
            with self.subTest(delivered=delivered):
                a = Asker(self)
                a.ask(RAIL)
                a.inst.vars["copygrantpending"] = True
                a.calls["book asked for"] = 1
                a.brief = replace(a.brief, copy_pending=True, add_requests=1)
                if delivered:
                    a.s.player.inventory[a.book] = 1
                    a.brief = mb.late_arrival(a.brief)
                a.s.actor_event(a.s.player, "OnPlayerLoadGame", [], 0)
                a.p.pause()
                self.assertTrue(a.state()["pending"])                # loading settles nothing by itself
                shown = a.ask(TAKE)
                if delivered:
                    self.assertEqual(shown, [mb.HUB, mb.PIKE, mb.DOCKET_ISSUED, mb.NOTE_ISSUED])
                    self.assertEqual((a.held(), a.state()["issued"], a.state()["pending"]), (1, True, False))
                else:
                    self.assertEqual(shown, [mb.HUB, mb.PIKE, mb.DOCKET_ISSUED, mb.NOTE_PENDING])
                    self.assertEqual((a.held(), a.state()["issued"], a.state()["pending"]), (0, False, True))
                self.assertEqual(a.calls["book asked for"], 1)

    def test_a_book_that_arrives_late_is_waited_for_a_second_and_no_longer(self):
        # SEEDED: the game puts the book into the inventory half a second after it was asked for.
        a = Asker(self)
        add = a.s.n_objectreference_additem

        def late(ref, context, form, count=1, silent=False):
            if unwrap(form) is a.book:
                a.calls["book asked for"] += 1
                a.s.later(0.5, "the book arrives", lambda: iter(()) if a.s.player.inventory.__setitem__(a.book, 1) else iter(()))
                return None
            return add(ref, context, form, count, silent)
        a.s.n_objectreference_additem = late
        started = a.s.now
        a.s.answers = {BRIEF_HUB: [mb.HUB_PIKE], MB + mb.PIKE: [mb.PIKE_ASK_QUILL], MB + mb.DOCKET: [mb.COPY_TAKE]}
        a.s.walk_to(REF + "Pritchard")
        a.s.press_activate(REF + "Pritchard")
        a.p.pause(3.0)
        self.assertEqual((a.held(), a.calls["book asked for"]), (1, 1))
        self.assertEqual((a.state()["issued"], a.state()["pending"]), (True, False))
        self.assertNotIn(MB + mb.NOTE_PENDING, a.s.messages_shown)
        self.assertLess(a.s.now - started, 3.5)


class NotBound(unittest.TestCase):
    """A plugin without the binding, or without the helper's records: the
    first section ends as it always did, and says what is missing."""

    def setUp(self):
        need_act1_build(self)

    def person(self, change):
        plugin, vanilla = changed_plugin(change)
        with patch("test_act1.PLUGIN", plugin), patch("test_act1.VANILLA", vanilla):
            p = Person(self)
        return p

    def play(self, p):
        p.press("Dispatch", events=["take_dispatch"])
        p.to_town()
        return p.press("Pritchard", {"PritchardCase": [0], "DebriefMissed": [0], "PritchardHandOff": [0]}, ["pritchard_handover", "pritchard_handoff"])

    def test_the_walk_without_its_property(self):
        def unbound(data):
            walk = [q for q in data["Quests"] if q["EditorId"] == "TLM_A1"][0]["Scripts"][0]
            walk["Props"] = [p for p in walk["Props"] if p["Name"] != "TLM_MercyBriefing"]
        p = self.person(unbound)
        self.assertEqual(self.play(p)[-1], "PritchardHandOff")
        self.assertEqual(p.g("TLM_G_MQ01_Done"), 1)
        p.press("Pritchard", {"PritchardAfter": [0]})
        self.assertEqual([m for m in p.s.messages_shown if m.startswith(MB)], [])
        self.assertFalse(p.s.quests[QUEST].running)

    def test_the_property_pointing_at_a_quest_without_the_script(self):
        def wrong(data):
            walk = [q for q in data["Quests"] if q["EditorId"] == "TLM_A1"][0]["Scripts"][0]
            for prop in walk["Props"]:
                if prop["Name"] == "TLM_MercyBriefing":
                    prop["Target"] = "TLM_SQ01"
        p = self.person(wrong)
        self.assertEqual(self.play(p)[-1], "PritchardHandOff")
        p.press("Pritchard", {"PritchardAfter": [0]})
        self.assertEqual([m for m in p.s.messages_shown if m.startswith(MB)], [])

    def test_the_helper_without_one_of_its_records_says_which(self):
        for missing, word in (("ReviewCopy", "ReviewCopy"), ("HubLine", "HubLine"), ("DocketIssuedLine", "DocketIssuedLine"),
                              ("TLM_G_MQ01_Done", "TLM_G_MQ01_Done")):
            with self.subTest(missing):
                def unbound(data, missing=missing):
                    helper = [q for q in data["Quests"] if q["EditorId"] == QUEST][0]["Scripts"][0]
                    helper["Props"] = [p for p in helper["Props"] if p["Name"] != missing]
                p = self.person(unbound)
                self.assertEqual(self.play(p)[-1], "PritchardHandOff")
                p.press("Pritchard", {"PritchardAfter": [0]})
                self.assertEqual([m for m in p.s.messages_shown if m.startswith(MB)], [])
                self.assertTrue(any("TLM_MercyBriefing: not bound:" in l and word in l for l in p.s.papyrus_log), p.s.papyrus_log[-5:])
                self.assertEqual(p.s.player.inventory.get(p.s.forms.get(BOOK), 0), 0)

    def test_without_the_alias_the_briefing_still_works(self):
        def unbound(data):
            helper = [q for q in data["Quests"] if q["EditorId"] == QUEST][0]["Scripts"][0]
            helper["Props"] = [p for p in helper["Props"] if p["Name"] != "Alias_Briefer"]
        p = self.person(unbound)
        p.press("Dispatch", events=["take_dispatch"])
        p.to_town()
        p.hand_over("DebriefMissed")
        p.press("Pritchard", boxes={BRIEF_HUB: [mb.HUB_RAIL], MB + mb.RAIL: [0]})
        self.assertEqual(p.s.quests[QUEST].done, [10, 20])
        self.assertIsNone(p.s.quests[QUEST].aliases[0].ref)


class WhatTheseTestsCatch(unittest.TestCase):
    """The scripts with one thing put wrong at a time. Each has to be noticed
    by a test above; here, by the same comparison those tests make."""

    def setUp(self):
        need_act1_build(self)

    def broken(self, file_name, old, new, visits, first=None):
        scripts = changed_scripts(file_name, old, new)
        try:
            a = Asker(self, scripts=scripts)
            for v in visits:
                a.ask(v, first=first)
        except (AssertionError, SimError):
            # SimError: a box opened that the model did not expect, and the stand-in stopped the session.
            return True
        return False

    def test_the_scripts_as_they_are_pass(self):
        a = Asker(self)
        for v in (NOT_NOW, RAIL, TAKE, TAKE, TAKE_FAILS):
            a.ask(v)

    def test_a_second_copy_on_asking_again(self):
        self.assertTrue(self.broken("MercyBriefing.psc", "	If CopyIssued || CopyGrantPending || player.GetItemCount(ReviewCopy) > 0\n",
                                    "	If false\n", (TAKE, TAKE)))

    def test_no_guard_on_the_count_or_the_history(self):
        self.assertTrue(self.broken("MercyBriefing.psc",
                                    "	If CopyIssued || CopyGrantPending || player.GetItemCount(ReviewCopy) > 0\n", "	If CopyGrantPending\n", (TAKE, TAKE)))

    def test_two_books_for_one_take(self):
        self.assertTrue(self.broken("MercyBriefing.psc", "akPlayer.AddItem(ReviewCopy, 1, false)", "akPlayer.AddItem(ReviewCopy, 2, false)", (TAKE,)))

    def test_a_copy_without_the_take(self):
        self.assertTrue(self.broken("MercyBriefing.psc", "	If DocketLine.Show() != COPY_TAKE\n		Return\n	EndIf\n", "	DocketLine.Show()\n", (ASK,)))

    def test_a_failed_request_claimed_as_given(self):
        self.assertTrue(self.broken("MercyBriefing.psc", "	If akPlayer.GetItemCount(ReviewCopy) > 0\n		CopyIssued = true\n		CopyGrantPending = false\n		Debug.Trace(\"TLM_MercyBriefing: review copy given",
                                    "	If true\n		CopyIssued = true\n		CopyGrantPending = false\n		Debug.Trace(\"TLM_MercyBriefing: review copy given", (TAKE_FAILS,)))

    def test_one_of_the_two_guards_gone_is_still_safe(self):
        # The claim's own guard removed: the test before the offer still keeps a second request out.
        self.assertFalse(self.broken("MercyBriefing.psc", "	If CopyIssued || CopyGrantPending\n		Return\n	EndIf\n	CopyGrantPending = true\n",
                                     "	CopyGrantPending = true\n", (TAKE_FAILS, TAKE, TAKE)))

    def test_a_failed_request_made_again_with_both_guards_gone(self):
        scripts = changed_scripts("MercyBriefing.psc", "	If CopyIssued || CopyGrantPending\n		Return\n	EndIf\n	CopyGrantPending = true\n", "	CopyGrantPending = true\n")
        text = (scripts / "MercyBriefing.psc").read_text()
        old = "	If CopyIssued || CopyGrantPending || player.GetItemCount(ReviewCopy) > 0\n"
        self.assertEqual(text.count(old), 1)
        (scripts / "MercyBriefing.psc").write_text(text.replace(old, "	If CopyIssued || player.GetItemCount(ReviewCopy) > 0\n"))
        with self.assertRaises((AssertionError, SimError)):
            a = Asker(self, scripts=scripts)
            a.ask(TAKE_FAILS)
            a.ask(TAKE)

    def test_complete_on_not_now(self):
        self.assertTrue(self.broken("MercyBriefing.psc", "		; \"Not now.\", or no answer.\n		Return\n", "		presented = true\n", (NOT_NOW,)))

    def test_complete_twice(self):
        self.assertTrue(self.broken("MercyBriefing.psc", "	If GetStageDone(20)\n		Return\n	EndIf\n	SetObjectiveCompleted(10)\n", "	SetObjectiveCompleted(10)\n", (RAIL, RIVER)))

    def test_the_objective_shown_at_every_visit(self):
        self.assertTrue(self.broken("MercyBriefing.psc", "	If !GetStageDone(10)\n		SetStage(10)\n		SetObjectiveDisplayed(10)\n	EndIf\n",
                                    "	If !GetStageDone(10)\n		SetStage(10)\n	EndIf\n	SetObjectiveDisplayed(10)\n", (NOT_NOW, NOT_NOW)))

    def test_two_buttons_the_wrong_way_round(self):
        self.assertTrue(self.broken("MercyBriefing.psc", "int HUB_RAIL = 0 Const\nint HUB_RIVER = 1 Const", "int HUB_RAIL = 1 Const\nint HUB_RIVER = 0 Const", (RAIL,)))
        self.assertTrue(self.broken("MercyBriefing.psc", "int COPY_TAKE = 0 Const\nint COPY_LEAVE = 1 Const", "int COPY_TAKE = 1 Const\nint COPY_LEAVE = 0 Const", (ASK,)))

    def test_a_menu_that_goes_round_again(self):
        self.assertTrue(self.broken("MercyBriefing.psc", "	If presented\n		If IsOpen(akBriefer)\n			Finish()\n",
                                    "	If presented\n		If IsOpen(akBriefer)\n			Finish()\n			HubLine.Show()\n", (RAIL,)))

    def test_no_look_at_who_is_alive_before_the_copy(self):
        v = replace(TAKE, after=((mb.DOCKET, DEAD),))
        self.assertTrue(self.broken("MercyBriefing.psc", "	If !IsOpen(akBriefer)\n		Debug.Trace(\"TLM_MercyBriefing: no longer to be had when the copy was taken; none is given\")\n		Return\n	EndIf\n", "", (v,)))

    def test_no_look_at_who_is_alive_before_completing(self):
        v = replace(RAIL, after=((mb.RAIL, DEAD),))
        self.assertTrue(self.broken("MercyBriefing.psc", "	If presented\n		If IsOpen(akBriefer)\n			Finish()\n		Else\n", "	If presented\n		If true\n			Finish()\n		Else\n", (v,)))

    def test_a_gate_left_out(self):
        for old, new in (("	If TLM_G_MQ01_Done.GetValueInt() != 1\n		Return false\n	EndIf\n	TLM:MQ01Quest mainScript", "	TLM:MQ01Quest mainScript"),
                         (" || !TLM_MQ01.GetStageDone(100)\n", "\n"),
                         ("	Return mainScript.DeliveryAcknowledged()\n", "	Return true\n")):
            with self.subTest(old):
                scripts = changed_scripts("MercyBriefing.psc", old, new)
                a = Asker(self, scripts=scripts)
                mq = a.s.quests["TLM_MQ01"]
                mq.done.remove(60)
                mq.done.remove(100)
                a.s.set_global("TLM_G_MQ01_Done", 0)
                mq.completed_objectives[20] = False
                mq.scripts[0].vars["deliveryfinished"] = False
                if "GetValueInt" in old:
                    mq.done.extend([60, 100])                    # every stage there; only the global is not
                    mq.scripts[0].vars["deliveryfinished"] = True
                if "GetStageDone(100)" in old:
                    mq.done.append(60)
                    a.s.set_global("TLM_G_MQ01_Done", 1)
                    mq.scripts[0].vars["deliveryfinished"] = True
                if "DeliveryAcknowledged" in old:
                    mq.done.extend([60, 100])
                    a.s.set_global("TLM_G_MQ01_Done", 1)
                    mq.scripts[0].vars["deliveryapplying"] = True   # the delivery's handler is at work
                a.s.answers = {BRIEF_HUB: [mb.HUB_NOT_NOW]}
                took, shown = a.offer()
                self.assertTrue(took, "the mutation was to let this through")
                good = Asker(self)
                gq = good.s.quests["TLM_MQ01"]
                gq.done[:] = list(mq.done)
                good.s.set_global("TLM_G_MQ01_Done", a.s.get_global("TLM_G_MQ01_Done"))
                gq.completed_objectives[20] = mq.completed_objectives.get(20, False)
                for var in ("deliveryfinished", "deliveryapplying"):
                    gq.scripts[0].vars[var] = mq.scripts[0].vars[var]
                self.assertEqual(good.offer(), (False, []))

    def test_the_report_button_taken_for_continue(self):
        scripts = changed_scripts("Act1Walk.psc", "		If ShowLine(SayPritchardAfterAndMore) == 1\n			Report()\n		Else\n			OfferBriefing(akWho)\n		EndIf\n",
                                  "		ShowLine(SayPritchardAfterAndMore)\n		OfferBriefing(akWho)\n")
        with self.assertRaises((AssertionError, SimError)):
            a = Asker(self, with_ledger=True, scripts=scripts)
            a.p.press("Pritchard", {"PritchardAfterAndMore": [1], "PritchardReported": [0]}, ["sq_report"])

    def test_the_briefing_offered_before_the_chapter_is_over(self):
        scripts = changed_scripts("Act1Walk.psc", "	If !TLM_MQ01.GetStageDone(100) || TLM_G_MQ01_Done.GetValueInt() != 1\n		Return false\n	EndIf\n	TLM:MercyBriefing brief = Briefing()\n	If !brief\n		Return false\n	EndIf\n	Return brief.Offer(akWho)\n",
                                  "	TLM:MercyBriefing brief = Briefing()\n	If !brief\n		Return false\n	EndIf\n	Return brief.Offer(akWho)\n")
        # The walk's own gate gone: the briefing's script still reads everything itself, so nothing gets through.
        a = Asker(self, scripts=scripts)
        a.s.quests["TLM_MQ01"].done.remove(100)
        a.s.set_global("TLM_G_MQ01_Done", 0)
        self.assertEqual(a.s.invoke("TLM_A1", "OfferBriefing", [a.pritchard]), False)


if __name__ == "__main__":
    unittest.main()
