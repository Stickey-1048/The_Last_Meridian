"""Tests of amendment A25 (owner decision D9): the evade timer does not run
out on a conversation with the Cutter lead.

The plugin has no dialogue yet, so the game cannot be asked. The stand-in
engine has a switch on an actor, "is talking to the player"
(sim.ObjectReference.talking_to_player), that stands for a person talking to
him, and these tests flip it.

What they show: the quest script obeys the rule as the logic model states it,
with the real 90-second timer and not only the function it calls; nothing but
the timer is held back; and the script as it was before the rule loses the
deal, which is the fault the rule is there for.

What they do not show: that the game's IsInDialogueWithPlayer is true when it
should be. That needs a conversation in the game.
"""
import sys
import unittest

from sim import Session
from test_overlap import scripts_with_the_quest_at
from test_sim import NATIVES, PLUGIN, ROOT, SCRIPTS, VANILLA, need_build

sys.path.insert(0, str(ROOT / "tools" / "logic_model"))
import tlm_model as model                                         # noqa: E402

BEFORE_THE_RULE = "c1e6d48"
TO_THE_AMBUSH = ["start", "take_dispatch", "goto_ambush"]

# What the quest script writes to the script log when it holds the timer back
# or steps in. In the game these lines are the only sign of which rule acted.
HELD_BY_A_FIGHT = "TLM_MQ01: A2 the evade timer ran out during a fight: it starts over"
HELD_BY_THE_CONVERSATION = ("TLM_MQ01: A25 the evade timer ran out during the conversation with the Cutter lead: "
                            "it starts over")
ALREADY_DEAD = "TLM_MQ01: A24 the Cutter lead is already dead: a rescue, not an evasion"


def said(session):
    return [l for l in session.papyrus_log if l.startswith("TLM_MQ01: A")]


class TheTimerAndTheConversation(unittest.TestCase):
    def live(self, scripts=SCRIPTS):
        """A live ambush, and the moment its evade timer will run out."""
        s = Session(scripts, PLUGIN, VANILLA, NATIVES)
        s.enter_game()
        s.run(1.0)
        selftest = [i for i in s.quests["TLM_Core"].scripts if i.script.name == "TLM:SelfTest"][0]
        self.assertTrue(s.invoke("TLM_Core", "CaseBegin", [selftest, "X", "the conversation"]))
        for step in ("DoStart", "DoTakeDispatch", "DoEnterAmbush"):
            s.invoke("TLM_Core", step, [])
        driver = [i for i in s.quests["TLM_Core"].scripts if i.script.name == "TLM:CaseDriver"][0]
        return s, driver, s.quests["TLM_MQ01"], self.timer_due(s)

    def timer_due(self, s):
        due = [d for (_inst, number), (d, inst) in s.timers.items()
               if inst.script.name == "TLM:MQ01Quest" and number == 1]
        self.assertEqual(len(due), 1, "the evade timer is not running")
        return due[0]

    def seen(self, s, driver, mq):
        alias = {a.name: a for a in mq.aliases.values()}
        v = driver.vars
        return (s.get_global("TLM_G_CaravanOutcome"), s.get_global("TLM_G_CaravanMethod"),
                int(not v["nell"].dead), int(not v["abel"].dead), sum(v["wagonstandin"].inventory.values()),
                int(alias["CaravanMasterInTown"].ref is v["nell"]), int(alias["CaravanDroverInTown"].ref is v["abel"]),
                s.get_global("TLM_G_CaravanAliveAtMercy"))

    def in_the_model(self, events):
        st = model.run(TO_THE_AMBUSH + events)
        self.assertFalse(st.done(40))
        return (st.outcome, st.method, int(st.nell_alive), int(st.abel_alive), 3 if st.cargo == "intact" else 0,
                0, 0, st.alive_at_mercy)

    def set_stage(self, s, mq, stage):
        s.spawn(s.n_quest_setstage(mq, None, stage), "stage %d" % stage)
        s.run(s.now + 5.0)

    def test_with_nobody_talking_the_timer_runs_out_as_before(self):
        need_build(self)
        s, driver, mq, due = self.live()
        s.run(due - 1.0)
        self.assertEqual(self.seen(s, driver, mq), self.in_the_model([]))
        s.run(due + 1.0)
        self.assertEqual(self.seen(s, driver, mq), self.in_the_model(["evade_timer"]))
        self.assertEqual(said(s), [])

    def test_with_no_lead_at_all_the_timer_runs_out(self):
        """The alias empty, as it is when the quest is played by stages alone:
        the question about the conversation must not be put to nobody."""
        need_build(self)
        s = Session(SCRIPTS, PLUGIN, VANILLA, NATIVES)
        s.enter_game()
        s.run(1.0)
        mq = s.quests["TLM_MQ01"]
        for stage in (10, 20, 30):
            self.set_stage(s, mq, stage)
        self.assertEqual(s.get_global("TLM_G_CaravanOutcome"), model.OUT_NONE)
        s.run(self.timer_due(s) + 1.0)
        self.assertEqual(s.get_global("TLM_G_CaravanOutcome"), model.OUT_EVADED)
        self.assertEqual([l for l in s.papyrus_log if l.startswith("error:")], [])
        self.assertEqual(s.calls_on_none, 0)

    def test_a_fight_holds_it_back_and_the_script_says_which(self):
        need_build(self)
        s, driver, mq, due = self.live()
        s.n_actor_startcombat(driver.vars["lead"], None, s.player)
        s.run(due + 1.0)
        self.assertEqual(self.seen(s, driver, mq)[0], model.OUT_NONE)
        self.assertEqual(said(s), [HELD_BY_A_FIGHT])
        # a fight and a conversation at once: the fight is what is reported
        driver.vars["lead"].talking_to_player = True
        s.run(due + 91.0)
        self.assertEqual(said(s), [HELD_BY_A_FIGHT, HELD_BY_A_FIGHT])

    def test_it_does_not_run_out_on_the_conversation(self):
        need_build(self)
        s, driver, mq, due = self.live()
        driver.vars["lead"].talking_to_player = True
        s.run(due + 1.0)
        self.assertEqual(self.seen(s, driver, mq), self.in_the_model(["dunmore_talk"]))
        self.assertEqual(said(s), [HELD_BY_THE_CONVERSATION])
        with self.assertRaises(model.NotAvailable):
            model.run(TO_THE_AMBUSH + ["dunmore_talk", "evade_timer"])
        # it has started over, with its whole length
        self.assertAlmostEqual(self.timer_due(s), due + 90.0, delta=0.1)
        # and a deal taken now is a deal
        self.set_stage(s, mq, 33)
        self.assertEqual(self.seen(s, driver, mq), self.in_the_model(["dunmore_talk", "dunmore_deal"]))
        self.assertEqual(self.seen(s, driver, mq)[:2], (model.OUT_EXPLOITED, model.METHOD_DEAL))

    def test_when_the_conversation_is_left_the_timer_runs_out_on_its_next_turn(self):
        need_build(self)
        s, driver, mq, due = self.live()
        driver.vars["lead"].talking_to_player = True
        s.run(due + 10.0)
        driver.vars["lead"].talking_to_player = False
        s.run(due + 89.0)
        self.assertEqual(self.seen(s, driver, mq)[0], model.OUT_NONE)
        s.run(due + 91.0)
        self.assertEqual(self.seen(s, driver, mq),
                         self.in_the_model(["dunmore_talk", "walk_away_from_dunmore", "evade_timer"]))

    def test_a_conversation_as_long_as_you_like(self):
        need_build(self)
        s, driver, mq, due = self.live()
        driver.vars["lead"].talking_to_player = True
        s.run(due + 600.0)
        self.assertEqual(self.seen(s, driver, mq), self.in_the_model(["dunmore_talk"]))
        self.assertEqual([l for l in s.papyrus_log if l.startswith("error:")], [])

    def test_only_the_timer_is_held_back(self):
        need_build(self)
        # leaving
        s, driver, mq, _due = self.live()
        driver.vars["lead"].talking_to_player = True
        driver.vars["center"].pos = (6000.0, 0.0, 0.0)
        s.check_distances()
        s.run(s.now + 5.0)
        self.assertEqual(self.seen(s, driver, mq), self.in_the_model(["dunmore_talk", "goto_wreck"]))
        # each line of the conversation. The third changes nothing that is
        # compared above: it starts a fight, so that is compared as well.
        for stage, line in ((31, "dunmore_speech_success"), (33, "dunmore_deal"), (37, "dunmore_speech_fail")):
            with self.subTest(line=line):
                s, driver, mq, _due = self.live()
                driver.vars["lead"].talking_to_player = True
                self.set_stage(s, mq, stage)
                self.assertEqual(self.seen(s, driver, mq), self.in_the_model(["dunmore_talk", line]))
                self.assertEqual(s.player_in_combat(),
                                 model.run(TO_THE_AMBUSH + ["dunmore_talk", line]).in_combat)
        self.assertTrue(model.run(TO_THE_AMBUSH + ["dunmore_talk", "dunmore_speech_fail"]).in_combat)
        # a killing
        s, driver, mq, _due = self.live()
        driver.vars["lead"].talking_to_player = True
        s.n_actor_kill(driver.vars["nell"], None, s.player)
        s.run(s.now + 5.0)
        self.assertEqual(self.seen(s, driver, mq), self.in_the_model(["dunmore_talk", "player_kills_nell"]))

    def test_killing_him_in_mid_conversation_is_a_rescue(self):
        """The timer runs out between his death and the news of it (amendment
        A24), with the conversation never closed by anyone. It has to come out
        a rescue, by whichever rule gets there first."""
        need_build(self)
        # Killed by the player: the game takes that for a fight, and the fight holds the timer back.
        s, driver, mq, due = self.live()
        driver.vars["lead"].talking_to_player = True
        s.run(due - 0.3)
        self.assertAlmostEqual(s.now, due - 0.3)
        s.n_actor_kill(driver.vars["lead"], None, s.player)
        s.run(due + 5.0)
        self.assertEqual(self.seen(s, driver, mq), self.in_the_model(["dunmore_talk", "player_kills_lead"]))
        self.assertEqual(self.seen(s, driver, mq)[0], model.OUT_SAVED)
        self.assertEqual(said(s), [HELD_BY_A_FIGHT])
        # Dead by nobody's hand, so no fight: the timer finds him dead and the ambush still live.
        s, driver, mq, due = self.live()
        driver.vars["lead"].talking_to_player = True
        s.run(due - 0.3)
        s.n_actor_setprotected(driver.vars["lead"], None, False)
        s.n_actor_kill(driver.vars["lead"], None, None)
        self.assertTrue(driver.vars["lead"].dead)
        s.run(due + 5.0)
        self.assertEqual(self.seen(s, driver, mq)[0], model.OUT_SAVED)
        self.assertEqual(said(s), [ALREADY_DEAD])

    def test_before_the_rule_the_deal_was_lost(self):
        """What the owner's decision D9 is about: the ambush resolved under the
        conversation, and the deal taken afterwards silently refused."""
        need_build(self)
        s, driver, mq, due = self.live(scripts_with_the_quest_at(BEFORE_THE_RULE, self))
        driver.vars["lead"].talking_to_player = True
        s.run(due + 1.0)
        self.assertEqual(self.seen(s, driver, mq)[0], model.OUT_EVADED)
        self.set_stage(s, mq, 33)
        self.assertEqual(self.seen(s, driver, mq)[:2], (model.OUT_EVADED, model.METHOD_NONE))
        # the same in the logic model under the v0.1 rules
        old = model.run(TO_THE_AMBUSH + ["dunmore_talk", "evade_timer"], rules=model.V01)
        self.assertEqual(old.outcome, model.OUT_EVADED)


if __name__ == "__main__":
    unittest.main()
