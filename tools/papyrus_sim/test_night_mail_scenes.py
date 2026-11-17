"""The Night Mail's scenes when the game does not carry them out, its boxes
when they are not answered, and its people when they are not there to speak
(NIGHT-MAIL-STORY-001), on the stand-in engine.

Every scene of this road is begun (an intent, kept by a save), carried out,
LOOKED AT, and only then recorded. These tests SEED the ways that can go
wrong: a call into the game that does nothing or does it late, a box that
comes back with no button a person can press, somebody dying or the road
changing while a box is open. Each is said where it is done. They are not
rules about the game: they are what the scripts must not take for a thing
having happened.

What must hold in every case: nothing is recorded that was not seen; what
was begun stays begun, alone, and no other course can be begun beside it;
it can be finished later from a control the player can reach where they
then stand; what was paid or given is paid or given once; and nothing that
was recorded is taken back.

NONE OF THIS HAS BEEN SEEN IN THE GAME. Not a compile and not a game test.
"""
import unittest

from sim import SimError
from test_act1 import BRIEF_HUB, MSG, REF, changed_scripts, need_act1_build
from night_mail_player import G, R, Rider, nm

NO_ANSWER = (-1, 7)
LONG = 14.0                                           # longer than the ten seconds a scene looks for an arrival


def while_open(a, box, do):
    """SEEDED: `do` happens once, while that box is open."""
    state = {"done": False}

    def meanwhile(message):
        if message == G + box and not state["done"]:
            state["done"] = True
            do()
    a.s.on_box = meanwhile


def closed(a):
    a.s.on_box = None
    a.box_returns(None, None)
    a.allow_calls()


def use(a, piece, answers=None, more=4.0, also=None):
    """Uses a piece with no model beside it; answers by the boxes' short names."""
    if also:
        while_open(a, *also)
    try:
        return a.press(piece if piece.startswith("TLM_") else R + piece,
                       {(k if k.startswith("TLM_") else G + k): v for k, v in (answers or {}).items()}, more=more)
    finally:
        a.s.on_box = None


def state(a):
    v = a.rules.vars
    return {"claim": v["claim"], "scene": v["scenepending"], "yard": v["yardpending"], "outcome": a.g("Outcome"),
            "mail": a.g("Mail"), "train": a.g("Train"), "engine": a.g("Engine")}


def free(t, a, what):
    t.assertFalse(a.walk.vars["talking"], "the walk still holds its claim after " + what)


def load(a):
    """As the game sends it on a load. The stand-in keeps a script's variables as they are, which is what a save does."""
    a.s.actor_event(a.s.player, "OnPlayerLoadGame", [], 0)
    a.p.pause(2.0)


def at_the_cut(t, **kw):
    a = Rider(t, **kw)
    a.hire()
    a.depart()
    return a


RUN = {"BillieInCut": [0], "AskRunScene": [0]}
BACK = {"BillieInCut": [2], "AskReverseScene": [0]}
SELL = {"DoleSermon": [1], "DoleShare": [0]}


class Base(unittest.TestCase):
    def setUp(self):
        need_act1_build(self)


class TheDeparture(Base):
    def test_not_arrived_then_arrived(self):
        """SEEDED: the move to the Cut does nothing. Stage 30 says who drives; nothing says the train left."""
        a = Rider(self)
        a.hire()
        a.refuse_call("moveto", "player")
        self.assertEqual(use(a, "Depart", {"AskDepartScene": [0]}, more=LONG), ["AskDepartScene", "NoteSceneFailed"])
        self.assertEqual(state(a), {"claim": 0, "scene": 1, "yard": 0, "outcome": 0, "mail": 0, "train": 0, "engine": 0})
        self.assertIn(30, a.road.done)
        self.assertNotIn(40, a.road.done)
        self.assertEqual(a.where(), nm.YARD)
        self.assertTrue(a.at("billie", "BillieFootplate"), "she is not shown ahead of a journey nobody saw")
        free(self, a, "a departure not seen")
        # Everything of the train tries the same journey again; nothing else is begun, and nothing is asked again.
        for piece in ("Billie", "CargoAboard", "LabelFootplate"):
            self.assertEqual(use(a, piece, more=LONG), ["NoteSceneFailed"], piece)
        # The yard goes on: its master speaks, its drawer opens, and the way home is never shut.
        self.assertEqual(use(a, "Lockridge"), ["LockridgeDefault"])
        self.assertEqual(use(a, "Exit", {"AskLeaveUnresolved": [1]}), ["AskLeaveUnresolved"])
        load(a)
        self.assertEqual(state(a)["scene"], 1)
        a.allow_calls()
        self.assertEqual(use(a, "Depart", more=LONG), [])
        self.assertEqual(state(a)["scene"], 0)
        self.assertEqual((a.where(), a.g("Train"), a.road.done.count(30), a.road.done.count(40)), (nm.CUT, 1, 1, 1))
        a.m.use_depart()
        a.same("the departure, seen at the second try")
        a.billie("run")

    def lanterns_dark(self, a):
        """SEEDED: the lanterns are off and do not come on."""
        a.s.placed[R + "Lanterns"].disabled = True
        a.refuse_call("enable", "Lanterns")

    def test_the_lanterns_not_seen(self):
        """SEEDED: the lanterns do not come on. The player is in the Cut; the train is not recorded there."""
        a = Rider(self)
        a.hire()
        self.lanterns_dark(a)
        self.assertEqual(use(a, "Depart", {"AskDepartScene": [0]}, more=LONG), ["AskDepartScene", "NoteSceneFailed"])
        self.assertEqual((a.where(), state(a)["scene"], a.g("Train")), (nm.CUT, 1, 0))
        self.assertTrue(a.at("billie", "BillieFootplate"))
        # In the Cut nothing of the encounter can be begun: every control is the journey, tried again.
        for piece in ("Regulator", "Dole", "LabelCut"):
            self.assertEqual(use(a, piece, RUN, more=LONG), ["NoteSceneFailed"], piece)
        self.assertEqual(state(a)["claim"], 0)
        a.allow_calls()
        self.assertEqual(use(a, "LabelCut", more=LONG), [])
        a.m.use_depart()
        a.same("the lanterns, seen at the second try")
        self.assertTrue(a.at("billie", "BillieCut"))

    def test_a_scene_that_cannot_be_shown_keeps_nobody_in_the_cut(self):
        """The way back along the line and the road to Mercy are never shut. Leaving with a journey only
        begun completes nothing, and it is finished when the player comes back."""
        a = Rider(self)
        a.hire()
        self.lanterns_dark(a)
        use(a, "Depart", {"AskDepartScene": [0]}, more=LONG)
        self.assertEqual(use(a, "BackFromCut", {"AskBackToYard": [0]}), ["AskBackToYard"])
        self.assertEqual((a.where(), state(a)["scene"]), (nm.YARD, 1))
        self.assertEqual(use(a, "Exit", {"AskLeaveUnresolved": [0]}), ["AskLeaveUnresolved", "NoteLeftUnresolved"])
        self.assertEqual(a.where(), nm.MERCY)
        self.assertFalse(a.road.completed)
        self.assertEqual(use(a, REF + "Pritchard", {BRIEF_HUB: [3]}), [BRIEF_HUB], "nothing of the Night Mail is due")
        load(a)
        a.allow_calls()
        use(a, "MercyTravel", {"AskTravel": [0]})
        self.assertEqual(use(a, "Depart", more=LONG), [])
        self.assertEqual((a.where(), state(a)["scene"], a.g("Train")), (nm.CUT, 0, 1))
        a.m.use_depart()
        a.before = a.world()                                      # the Mercy briefing was begun by speaking to Pritchard
        a.same("the journey, finished after leaving and coming back")

    def test_not_confirmed_or_stale_begins_nothing(self):
        for value in NO_ANSWER + (1,):
            with self.subTest(answer=value):
                a = Rider(self)
                a.hire()
                a.box_returns(G + "AskDepartScene", value)
                self.assertEqual(use(a, "Depart"), ["AskDepartScene"])
                closed(a)
                self.assertEqual((state(a)["scene"], a.where()), (0, nm.YARD))
                self.assertNotIn(30, a.road.done)
                free(self, a, "a departure not confirmed")

    def test_the_notice_is_nobodys_line_and_goes_on_without_billie(self):
        """SEEDED: Billie dies while the departure's notice is open. The notice is this build's and names no
        driver: the journey is the one without her, and no line of hers is shown."""
        a = Rider(self)
        a.hire()
        said = use(a, "Depart", {"AskDepartScene": [0]}, more=LONG,
                   also=("AskDepartScene", lambda: a._kill(a.who["billie"], None, a.s.player)))
        self.assertEqual(said, ["AskDepartScene"])
        self.assertEqual((state(a)["scene"], a.where()), (0, nm.CUT))
        self.assertIn(31, a.road.done)
        self.assertNotIn(30, a.road.done)
        self.assertEqual(use(a, "Regulator", {"AskRegulator": [1]}), ["AskRegulator"])


class TheRun(Base):
    def test_the_cargo_not_seen_delivered(self):
        """SEEDED: the delivered cargo does not come on. The player is at the platform; no mail got through."""
        a = at_the_cut(self)
        a.refuse_call("enable", "CargoDelivered")
        self.assertEqual(use(a, "Billie", RUN, more=LONG), ["BillieInCut", "AskRunScene", "NoteSceneFailed"])
        self.assertEqual(state(a), {"claim": 41, "scene": 2, "yard": 0, "outcome": 0, "mail": 0, "train": 1, "engine": 0})
        self.assertEqual(a.where(), nm.PLATFORM)
        self.assertEqual((a.g("MailThrough"), a.on("CargoDelivered"), a.on("EngineDamaged"), a.on("CargoAtCut")), (0, False, False, True))
        self.assertFalse(any(n in a.road.done for n in (41, 46)))
        # Leaving now completes nothing: no course was carried through.
        self.assertEqual(use(a, "PlatformExit", {"AskLeaveUnresolved": [1]}), ["AskLeaveUnresolved"])
        load(a)
        self.assertTrue(a.at("billie", "BillieCut"), "she is with the engine where it is recorded to stand")
        self.assertEqual(use(a, "LabelPlatform", more=LONG), ["NoteSceneFailed"])
        self.assertEqual(state(a)["scene"], 2)
        a.allow_calls()
        self.assertEqual(use(a, "LabelPlatform", more=LONG), ["NoteRunDone", "BillieRan"])
        a.m.talk_billie("run")
        a.same("the run, seen at the second try")
        self.assertEqual(len([n for n in a.road.done if n in (41, 46)]), 1)

    def test_the_player_not_moved(self):
        """SEEDED: the move to the platform does nothing. Requested transit is not arrival."""
        a = at_the_cut(self)
        a.refuse_call("moveto", "player")
        self.assertEqual(use(a, "Regulator", RUN, more=LONG), ["BillieInCut", "AskRunScene", "NoteSceneFailed"])
        self.assertEqual((a.where(), state(a)["claim"], state(a)["scene"], a.g("Outcome"), a.g("Mail")), (nm.CUT, 41, 2, 0, 0))
        # The other three courses are closed by the one that was begun.
        self.assertEqual(use(a, "Reverser", BACK, more=LONG), ["NoteSceneFailed"])
        self.assertEqual(use(a, "Dole", SELL, more=LONG), ["NoteSceneFailed"])
        self.assertEqual((state(a)["claim"], a.count(a.caps) - a.caps_before), (41, 0))
        a.allow_calls()
        self.assertEqual(use(a, "CargoAtCut", more=LONG), ["NoteRunDone", "BillieRan"])
        a.m.talk_billie("run")
        a.same("the run, the player moved at the second try")

    def test_dole_killed_while_the_run_is_pending_is_not_the_outcome(self):
        a = at_the_cut(self)
        a.refuse_call("moveto", "player")
        use(a, "Regulator", RUN, more=LONG)
        a._kill(a.who["dole"], None, a.s.player)
        a.p.pause(3.0)
        self.assertEqual((state(a)["claim"], state(a)["scene"], a.g("Dole")), (41, 2, 2))
        self.assertNotIn(42, a.road.done)
        a.allow_calls()
        self.assertEqual(use(a, "Regulator", more=LONG), ["NoteRunDone", "BillieRan"])
        self.assertEqual((a.g("Outcome"), a.g("DoleLives"), a.g("Dole")), (41, 0, 2))
        a.m.talk_billie("run")
        a.m.dole_dies(True)
        a.before = a.world()
        a.same("the run, with Dole killed while it was pending")

    def test_billie_dead_before_it_is_seen_says_nothing(self):
        """She drove (stage 41: she was at the regulator when it was begun); a dead woman has no line."""
        a = at_the_cut(self)
        a.refuse_call("moveto", "player")
        use(a, "Regulator", RUN, more=LONG)
        a._kill(a.who["billie"], None, a.s.player)
        a.p.pause(2.0)
        a.allow_calls()
        self.assertEqual(use(a, "Regulator", more=LONG), ["NoteRunDone"])
        self.assertIn(41, a.road.done)
        self.assertFalse(a.walk.vars["ransaid"])

    def test_not_confirmed_or_stale_begins_nothing(self):
        for box in ("BillieInCut", "AskRunScene"):
            for value in NO_ANSWER:
                with self.subTest(box=box, answer=value):
                    a = at_the_cut(self)
                    a.box_returns(G + box, value)
                    use(a, "Billie", RUN)
                    closed(a)
                    self.assertEqual(state(a), {"claim": 0, "scene": 0, "yard": 0, "outcome": 0, "mail": 0, "train": 1, "engine": 0})
                    self.assertEqual(a.where(), nm.CUT)
                    free(self, a, "a run not confirmed")

    def test_her_question_is_answered_to_her(self):
        """SEEDED: Billie dies while her question is open. The answer runs nothing; the regulator still can."""
        a = at_the_cut(self)
        said = use(a, "Billie", RUN, also=("BillieInCut", lambda: a._kill(a.who["billie"], None, a.s.player)))
        self.assertEqual(said, ["BillieInCut"])
        self.assertEqual(state(a)["claim"], 0)
        self.assertEqual(use(a, "Regulator", {"AskRegulator": [0], "AskRunScene": [0]}, more=LONG), ["AskRegulator", "AskRunScene", "NoteRunDone"])
        self.assertIn(46, a.road.done)

    def test_dole_killed_under_the_scenes_notice_is_one_outcome_only(self):
        """SEEDED: Dole is killed while the run's notice is open. Whichever the scripts hear of first, there
        is one outcome: here the answer came first, so it is the run, past a dead man, and no kill is the
        encounter's outcome."""
        a = at_the_cut(self)
        said = use(a, "Billie", RUN, more=LONG, also=("AskRunScene", lambda: a._kill(a.who["dole"], None, a.s.player)))
        a.p.pause(3.0)
        self.assertEqual(said, ["BillieInCut", "AskRunScene", "NoteRunDone", "BillieRan"])
        self.assertEqual((a.g("Outcome"), state(a)["claim"], a.g("Dole"), a.g("DoleLives")), (41, 41, 2, 0))
        self.assertEqual(sorted(n for n in (41, 42, 43, 44, 46, 48, 49) if n in a.road.done), [41])


class TheReverse(Base):
    def test_the_cargo_not_seen_locked_up(self):
        a = at_the_cut(self)
        a.refuse_call("enable", "CargoRetained")
        self.assertEqual(use(a, "Billie", BACK, more=LONG), ["BillieInCut", "AskReverseScene", "NoteSceneFailed"])
        self.assertEqual(state(a), {"claim": 44, "scene": 4, "yard": 0, "outcome": 0, "mail": 0, "train": 1, "engine": 0})
        self.assertEqual((a.where(), a.g("LineClosed"), a.on("CargoRetained")), (nm.YARD, 0, False))
        # At the yard the departure control does not send the train out again: it is the reverse, tried again.
        self.assertEqual(use(a, "Depart", {"AskDepartScene": [0]}, more=LONG), ["NoteSceneFailed"])
        a.allow_calls()
        self.assertEqual(use(a, "Depart", more=LONG), ["NoteBackedOut", "BillieBacked"])
        a.m.talk_billie("back")
        a.same("the reverse, seen at the second try")

    def test_the_player_not_moved(self):
        a = at_the_cut(self)
        a.refuse_call("moveto", "player")
        self.assertEqual(use(a, "Reverser", BACK, more=LONG), ["BillieInCut", "AskReverseScene", "NoteSceneFailed"])
        self.assertEqual((a.where(), state(a)["claim"], a.g("Outcome")), (nm.CUT, 44, 0))
        self.assertEqual(use(a, "Regulator", RUN, more=LONG), ["NoteSceneFailed"])
        a.allow_calls()
        self.assertEqual(use(a, "Dole", more=LONG), ["NoteBackedOut", "BillieBacked"])
        a.m.talk_billie("back")
        a.same("the reverse, the player moved at the second try")

    def test_nobodys_dead_is_not_said_over_a_body(self):
        a = at_the_cut(self)
        a.kill("rifle1", by_player=False)
        a.billie("back")
        self.assertFalse(a.walk.vars["backedsaid"])
        a.billie()


class AfterTheDefeat(Base):
    def defeated(self):
        a = at_the_cut(self)
        a.dole("aside")
        a.kill("dole", by_player=True)
        return a

    def test_forward_not_seen_then_seen(self):
        a = self.defeated()
        a.refuse_call("enable", "EngineSound")
        self.assertEqual(use(a, "Regulator", {"AskAfterDefeat": [0], "AskForwardScene": [0]}, more=LONG),
                         ["AskAfterDefeat", "AskForwardScene", "NoteSceneFailed"])
        self.assertEqual((state(a)["scene"], a.g("Mail"), a.g("MailThrough"), a.g("Outcome")), (3, 0, 0, 42))
        # The road is not complete by leaving now, whatever its outcome: a scene is under way.
        self.assertEqual(use(a, "PlatformExit", {"AskLeaveUnresolved": [1]}), ["AskLeaveUnresolved"])
        a.allow_calls()
        self.assertEqual(use(a, "LabelPlatform", more=LONG), ["NoteForwardDone"])
        a.m.use_train("forward")
        a.same("the delivery after the defeat, seen at the second try")

    def test_back_not_seen_then_seen(self):
        a = self.defeated()
        a.refuse_call("moveto", "player")
        self.assertEqual(use(a, "Reverser", {"AskAfterDefeat": [1], "AskCarryBackScene": [0]}, more=LONG),
                         ["AskAfterDefeat", "AskCarryBackScene", "NoteSceneFailed"])
        self.assertEqual((state(a)["scene"], a.g("Mail"), a.g("LineClosed")), (5, 0, 0))
        # Not the other way while this one is begun.
        self.assertEqual(use(a, "Regulator", {"AskAfterDefeat": [0], "AskForwardScene": [0]}, more=LONG), ["NoteSceneFailed"])
        a.allow_calls()
        self.assertEqual(use(a, "Regulator", more=LONG), ["NoteCarriedBack"])
        a.m.use_train("back")
        a.same("the return after the defeat, seen at the second try")

    def test_not_confirmed_or_stale(self):
        for box in ("AskAfterDefeat", "AskForwardScene"):
            for value in NO_ANSWER:
                with self.subTest(box=box, answer=value):
                    a = self.defeated()
                    a.box_returns(G + box, value)
                    use(a, "Regulator", {"AskAfterDefeat": [0], "AskForwardScene": [0]})
                    closed(a)
                    self.assertEqual((state(a)["scene"], a.g("Mail"), a.where()), (0, 0, nm.CUT))

    def test_the_black_rail_not_seen_gone(self):
        """SEEDED: one of the Black Rail cannot be moved. Dole is dead; the defeat is not recorded until each
        of them is seen dead or gone, and the other courses are closed meanwhile."""
        a = at_the_cut(self)
        a.dole("aside")
        a.refuse_call("moveto", a.s._whom(a.who["rifle2"]))
        a._kill(a.who["dole"], None, a.s.player)
        a.p.pause(3.0)
        self.assertEqual((state(a)["claim"], state(a)["scene"], a.g("Outcome"), a.g("Dole")), (42, 7, 0, 1))
        self.assertNotIn(42, a.road.done)
        self.assertNotIn(G + "NoteDefeat", a.s.messages_shown)
        self.assertEqual(use(a, "Regulator", RUN), ["NoteSceneFailed"])
        self.assertEqual(state(a)["claim"], 42)
        load(a)
        a.allow_calls()
        self.assertEqual(use(a, "Reverser"), ["NoteDefeat"])
        self.assertEqual((a.g("Outcome"), a.road.done.count(42)), (42, 1))
        a.m.dole_dies(True)
        a.before = a.world()
        a.same("the defeat, seen at the second try")

    def test_a_rifle_that_will_not_go_is_out_when_he_is_dead(self):
        a = at_the_cut(self)
        a.dole("aside")
        a.refuse_call("moveto", a.s._whom(a.who["rifle2"]))
        a._kill(a.who["dole"], None, a.s.player)
        a.p.pause(3.0)
        a._kill(a.who["rifle2"], None, a.s.player)
        a.p.pause(2.0)
        self.assertEqual(use(a, "Regulator", {"AskAfterDefeat": [2]}), ["NoteDefeat"])
        self.assertEqual(a.g("Outcome"), 42)

    def test_a_death_nobody_heard_of_is_found_at_the_next_control(self):
        """SEEDED: Dole is dead and his alias's death event never came."""
        a = at_the_cut(self)
        a.who["dole"].dead = True
        self.assertEqual(use(a, "Regulator", RUN), ["NoteDefeat"])
        self.assertEqual((a.g("Outcome"), a.g("Dole")), (42, 2))
        self.assertIn(47, a.road.done)
        self.assertNotIn(42, a.road.done, "nobody saw who killed him: no kill is credited to the player")


class TheSale(Base):
    def test_paid_and_the_cargo_not_seen_taken(self):
        """SEEDED: the seized cargo does not come on. Paid is paid, once; the sale is not recorded until seen."""
        a = at_the_cut(self)
        a.refuse_call("enable", "CargoSeized")
        self.assertEqual(use(a, "Dole", SELL, more=LONG), ["DoleSermon", "DoleShare", "NoteSalePending"])
        self.assertEqual(state(a), {"claim": 43, "scene": 6, "yard": 0, "outcome": 0, "mail": 0, "train": 1, "engine": 0})
        self.assertEqual((a.count(a.caps) - a.caps_before, a.asked["caps"], a.g("MailSold")), (150, 1, 0))
        self.assertFalse(any(n in a.road.done for n in (43, 48)))
        load(a)
        for piece, answers in (("Dole", SELL), ("Regulator", RUN), ("Billie", BACK), ("CargoAtCut", None)):
            self.assertEqual(use(a, piece, answers, more=LONG), ["NoteSalePending"], piece)
        self.assertEqual((a.count(a.caps) - a.caps_before, a.asked["caps"], state(a)["claim"]), (150, 1, 43))
        a.allow_calls()
        self.assertEqual(use(a, "Billie", more=LONG), ["NoteSold"])
        self.assertEqual((a.count(a.caps) - a.caps_before, a.asked["caps"]), (150, 1))
        a.m.talk_dole(["share", "done"])
        a.same("the sale, seen at the second try")

    def test_billie_not_seen_safe(self):
        """SEEDED: Billie cannot be moved to her walking marker. She was promised a walk home unharmed: the
        sale is not recorded until she is seen there."""
        a = at_the_cut(self)
        a.refuse_call("moveto", "billie")
        self.assertEqual(use(a, "Dole", SELL, more=LONG), ["DoleSermon", "DoleShare", "NoteSalePending"])
        self.assertEqual((state(a)["scene"], a.g("Outcome"), a.count(a.caps) - a.caps_before), (6, 0, 150))
        a.allow_calls()
        self.assertEqual(use(a, "Dole", more=LONG), ["NoteSold"])
        self.assertTrue(a.at("billie", "BillieWalk"))
        self.assertIn(43, a.road.done)

    def test_billie_dead_before_it_is_seen_is_a_sale_without_her(self):
        a = at_the_cut(self)
        a.refuse_call("enable", "CargoSeized")
        use(a, "Dole", SELL, more=LONG)
        a._kill(a.who["billie"], None, a.s.player)
        a.p.pause(2.0)
        a.allow_calls()
        self.assertEqual(use(a, "Dole", more=LONG), ["NoteSoldNoBillie"])
        self.assertIn(48, a.road.done)
        self.assertNotIn(43, a.road.done)
        self.assertFalse(a.rules.vars["billiereleased"])
        use(a, "BackFromCut", {"AskBackToYard": [0]})
        self.assertEqual(use(a, "Lockridge"), ["NoteSaleStatus"], "Billie walked nowhere and told nobody")

    def test_caps_the_game_does_not_give(self):
        """SEEDED: the request is not honoured. Asked once; the deal is off and never offered again; every
        other course stands."""
        a = at_the_cut(self, refuse=("caps",))
        a.dole("share", "done")
        self.assertEqual((a.asked["caps"], a.count(a.caps) - a.caps_before, state(a)["claim"], state(a)["scene"]), (1, 0, 0, 0))
        a.dole("share")
        a.dole("name", "share")
        self.assertEqual(a.asked["caps"], 1)
        a.billie("back")
        a.leave()
        a.report()

    def test_not_answered_or_stale_sells_nothing(self):
        for box in ("DoleSermon", "DoleShare"):
            for value in NO_ANSWER:
                with self.subTest(box=box, answer=value):
                    a = at_the_cut(self)
                    a.box_returns(G + box, value)
                    use(a, "Dole", SELL)
                    closed(a)
                    self.assertEqual((state(a)["claim"], a.count(a.caps) - a.caps_before, a.asked["caps"]), (0, 0, 0))
                    self.assertFalse(a.fighting("dole"))
                    free(self, a, "an offer not answered")

    def test_the_offer_is_answered_to_dole(self):
        """SEEDED: Dole dies while his offer is open. A dead man pays nobody."""
        a = at_the_cut(self)
        said = use(a, "Dole", SELL, also=("DoleShare", lambda: a._kill(a.who["dole"], None, None)))
        self.assertEqual(said[:2], ["DoleSermon", "DoleShare"])
        a.p.pause(3.0)
        self.assertEqual((a.count(a.caps) - a.caps_before, a.asked["caps"], a.g("MailSold")), (0, 0, 0))
        self.assertEqual(a.g("Outcome"), 42)

    def test_without_billie_the_offer_is_the_builds_own_and_her_walk_is_not_promised(self):
        a = at_the_cut(self)
        a.kill("billie")
        a.dole("share", "back")
        a.dole("share", "done")
        self.assertIn(48, a.road.done)


class Dole(Base):
    def test_walking_away_from_the_parley_starts_no_fight(self):
        a = at_the_cut(self)
        a.dole("back")
        a.dole("share", "back")
        for who in ("dole", "rifle1", "rifle2", "rifle3"):
            self.assertFalse(a.fighting(who), who)
        self.assertEqual(state(a)["claim"], 0)

    def test_the_fight_is_the_players_choice_and_only_then(self):
        for picks in (("aside",), ("share", "no"), ("name", "aside"), ("name", "silver", "aside")):
            with self.subTest(picks=picks):
                a = at_the_cut(self)
                a.dole(*picks)
                for who in ("dole", "rifle1", "rifle2", "rifle3"):
                    self.assertTrue(a.fighting(who), who)
                self.assertFalse(a.fighting("billie") or a.fighting("lockridge"))
                # A man in a fight has no lines and takes no payment.
                self.assertEqual(use(a, "Dole", SELL), [])

    def test_what_he_did_not_finish_saying_teaches_nothing(self):
        for box, stage, fact in (("DoleName", 56, "OstranderKnown"), ("DoleSilver", 51, "SilverRail")):
            for value in NO_ANSWER:
                with self.subTest(box=box, answer=value):
                    a = at_the_cut(self)
                    a.box_returns(G + box, value)
                    use(a, "Dole", {"DoleSermon": [2], "DoleName": [0], "DoleSilver": [1]})
                    closed(a)
                    self.assertNotIn(stage, a.road.done)
                    self.assertEqual(a.g(fact), 0)
            with self.subTest(box=box, dead=True):
                a = at_the_cut(self)
                use(a, "Dole", {"DoleSermon": [2], "DoleName": [0], "DoleSilver": [1]},
                    also=(box, lambda: a._kill(a.who["dole"], None, None)))
                self.assertNotIn(stage, a.road.done)
                self.assertEqual(a.g(fact), 0)

    def test_his_face_unanswered_is_no_fight(self):
        for value in NO_ANSWER:
            with self.subTest(answer=value):
                a = at_the_cut(self)
                a.box_returns(G + "DoleFace", value)
                use(a, "Dole", {"DoleSermon": [0]})
                closed(a)
                self.assertFalse(a.fighting("dole") or a.rules.vars["dolefaced"])

    def test_attacking_him_unprovoked_brings_the_black_rail_once(self):
        a = at_the_cut(self)
        a.s.n_actor_startcombat(a.s.player, None, a.who["rifle1"]) if False else None
        a.s.actor_event(a.who["rifle1"], "OnCombatStateChanged", [a.s.player, 1], 0)
        a.p.pause(2.0)
        for who in ("dole", "rifle1", "rifle2", "rifle3"):
            self.assertTrue(a.fighting(who), who)
            self.assertLessEqual(a.asked_of("startcombat", who), 1, who)
        self.assertFalse(a.fighting("billie") or a.fighting("lockridge"))

    def test_after_he_is_dead_the_black_rail_do_not_fight_on(self):
        a = at_the_cut(self)
        a.dole("aside")
        a.kill("dole", by_player=True)
        a.s.actor_event(a.who["rifle1"], "OnCombatStateChanged", [a.s.player, 1], 0)
        a.p.pause(2.0)
        for who in ("rifle2", "rifle3"):
            self.assertFalse(a.fighting(who), who)


class TheStampScenes(Base):
    def at_the_drawer(self, **kw):
        a = at_the_cut(self, **kw)
        a.billie("back")
        return a

    def test_the_countersigning_not_seen_then_seen(self):
        a = self.at_the_drawer()
        a.refuse_call("enable", "BoardSigned")
        said = use(a, "Drawer", {"LockridgeStamp": [1], "AskCountersignScene": [0]}, more=LONG)
        self.assertEqual(said, ["NoteDrawer", "LockridgeStamp", "AskCountersignScene", "NoteSceneFailed"])
        self.assertEqual((state(a)["yard"], a.g("Stamp"), a.g("LockridgeSigned")), (1, 0, 0))
        self.assertNotIn(62, a.road.done)
        self.assertTrue(a.on("BoardStamped") and not a.on("BoardSigned") and not a.on("HeldStock"))
        # Nothing else is decided about the stamp while this is begun.
        self.assertEqual(use(a, "Drawer", {"LockridgeStamp": [2]}, more=LONG), ["NoteSceneFailed"])
        self.assertEqual((a.count(a.stampitem), a.asked["stamp"]), (0, 0))
        load(a)
        a.allow_calls()
        self.assertEqual(use(a, "BoardStamped", more=LONG), ["NoteCountersigned"])
        a.m.use_drawer("sign")
        a.same("the countersigning, seen at the second try")

    def test_a_dead_woman_countersigns_nothing(self):
        """SEEDED: she dies with her countersigning confirmed and not yet seen. Nothing was signed; the
        request is dropped, and the drawer is open to whoever is left."""
        a = self.at_the_drawer()
        a.refuse_call("enable", "BoardSigned")
        use(a, "Drawer", {"LockridgeStamp": [1], "AskCountersignScene": [0]}, more=LONG)
        a._kill(a.who["lockridge"], None, a.s.player)
        a.p.pause(2.0)
        a.allow_calls()
        self.assertEqual(use(a, "Drawer", more=LONG), ["NoteDecisionFailed"])
        self.assertEqual((state(a)["yard"], a.g("Stamp"), a.g("LockridgeSigned")), (0, 0, 0))
        self.assertNotIn(62, a.road.done)
        self.assertTrue(a.on("BoardStamped") and not a.on("BoardSigned") and not a.on("HeldStock"))
        self.assertEqual(use(a, "Drawer", {"AskStampAlone": [0]}), ["AskStampAlone", "NoteStampTaken"])
        self.assertIn(64, a.road.done)

    def test_her_question_is_answered_to_her(self):
        for pick in (0, 1, 2):
            with self.subTest(pick=pick):
                a = self.at_the_drawer()
                said = use(a, "Drawer", {"LockridgeStamp": [pick], "AskCountersignScene": [0]},
                           also=("LockridgeStamp", lambda: a._kill(a.who["lockridge"], None, a.s.player)))
                self.assertEqual(said, ["NoteDrawer", "LockridgeStamp"])
                self.assertEqual((a.g("Stamp"), a.count(a.stampitem), state(a)["yard"]), (0, 0, 0))
                self.assertFalse(any(n in a.road.done for n in (61, 62, 63, 64)))

    def test_not_answered_or_stale_decides_nothing(self):
        for box in ("LockridgeStamp", "AskCountersignScene"):
            for value in NO_ANSWER:
                with self.subTest(box=box, answer=value):
                    a = self.at_the_drawer()
                    a.box_returns(G + box, value)
                    use(a, "Drawer", {"LockridgeStamp": [1], "AskCountersignScene": [0]})
                    closed(a)
                    self.assertEqual((a.g("Stamp"), state(a)["yard"], a.count(a.stampitem)), (0, 0, 0))
                    free(self, a, "a decision not made")

    def test_taken_and_the_drawer_not_seen_empty(self):
        """SEEDED: the drawer's stamp does not switch off. The player holds the stamp; it is not recorded
        taken until the drawer is seen without it, and nothing else can be decided meanwhile."""
        a = self.at_the_drawer()
        a.refuse_call("disable", "StampInDrawer")
        said = use(a, "Drawer", {"LockridgeStamp": [2]}, more=LONG)
        self.assertEqual(said, ["NoteDrawer", "LockridgeStamp", "NoteSceneFailed"])
        self.assertEqual((a.g("Stamp"), a.count(a.stampitem), a.asked["stamp"]), (0, 1, 1))
        self.assertFalse(any(n in a.road.done for n in (63, 64)))
        self.assertEqual(use(a, "Drawer", {"LockridgeStamp": [0]}, more=LONG), ["NoteSceneFailed"])
        self.assertEqual(use(a, "Lockridge"), ["LockridgeDefault"])
        self.assertEqual((a.g("Stamp"), a.asked["stamp"]), (0, 1))
        a.allow_calls()
        self.assertEqual(use(a, "BoardStamped", more=LONG), ["NoteStampTaken"])
        self.assertEqual((a.g("Stamp"), a.count(a.stampitem), a.asked["stamp"]), (63, 1, 1))
        a.m.use_drawer("take")
        a.same("the stamp, the drawer seen empty at the second try")

    def test_a_stamp_not_given_leaves_her_other_answers_open(self):
        """SEEDED: the request is not honoured. Nothing was taken, so she can still keep it or sign; it is
        never asked for again."""
        a = self.at_the_drawer(refuse=("stamp",))
        a.drawer("take")
        a.drawer("take")
        self.assertEqual((a.asked["stamp"], a.g("Stamp"), a.on("StampInDrawer")), (1, 0, True))
        a.drawer("sign")
        self.assertEqual(a.g("Stamp"), 62)

    def test_a_stamp_that_arrives_late_is_the_taking_when_next_chosen(self):
        """SEEDED: the stamp is not in the inventory within the second it is looked for, and is there later."""
        a = self.at_the_drawer(refuse=("stamp",))
        a.drawer("take")
        a.s.player.inventory[a.stampitem] = 1                    # SEEDED: it arrived after all
        self.assertEqual(use(a, "Drawer", {"LockridgeStamp": [0]}), ["LockridgeStamp", "NoteDecisionFailed"],
                         "she cannot keep stamping with a stamp that is in the player's pocket")
        self.assertEqual(use(a, "Drawer", {"LockridgeStamp": [2]}), ["LockridgeStamp", "NoteStampTaken"])
        self.assertEqual((a.g("Stamp"), a.count(a.stampitem), a.asked["stamp"]), (63, 1, 1))

    def test_dropped_and_picked_up_it_is_still_one_decision_and_custody_is_what_is_held(self):
        """SEEDED: the stamp leaves the inventory (dropped) and comes back (picked up)."""
        a = self.at_the_drawer()
        a.drawer("take")
        a.leave()
        a.s.player.inventory[a.stampitem] = 0
        said = use(a, REF + "Pritchard", {"ReportUnknown": [1], BRIEF_HUB: [3]})
        self.assertNotIn("AskHandOver", said)
        self.assertEqual(a.g("StampDelivered"), 0)
        a.s.player.inventory[a.stampitem] = 1
        a.report(give=False, hand=True)
        self.assertEqual((a.g("StampDelivered"), a.g("Stamp")), (1, 63))
        a.travel()
        a.drawer()
        self.assertEqual(len([n for n in (61, 62, 63, 64) if n in a.road.done]), 1)


class TheHandover(Base):
    def carrying(self, **kw):
        a = at_the_cut(self, **kw)
        a.billie("back")
        a.drawer("take")
        a.leave()
        return a

    def test_not_seen_with_pritchard_is_not_delivered(self):
        """SEEDED: RemoveItem does nothing. Nothing is delivered, the yard is not touched, and he can be asked again."""
        a = self.carrying()
        a.refuse.add("handover")
        said = use(a, REF + "Pritchard", {"ReportUnknown": [0], "AskHandOver": [0]}, more=6.0)
        self.assertEqual(said[-2:], ["AskHandOver", "NoteHandoverFailed"])
        self.assertEqual((a.g("StampDelivered"), a.g("YardAuthority"), a.g("LockridgeReported"), a.count(a.stampitem)), (0, 0, 0, 1))
        self.assertTrue(a.rules.vars["handoverpending"])
        a.refuse.discard("handover")
        a.m.reported = True
        a.report(hand=True)
        self.assertEqual((a.g("StampDelivered"), a.g("YardAuthority"), a.count(a.stampitem, a.who["sheriff"])), (1, 1, 1))

    def test_a_handover_that_arrived_late_is_seen_at_the_next_conversation(self):
        """SEEDED: the stamp reaches Pritchard after the second it is looked for."""
        a = self.carrying()
        a.refuse.add("handover")
        use(a, REF + "Pritchard", {"ReportUnknown": [0], "AskHandOver": [0]}, more=6.0)
        a.refuse.discard("handover")
        a.s.player.inventory[a.stampitem] = 0                    # SEEDED: it arrived after all
        a.who["sheriff"].inventory[a.stampitem] = 1
        said = use(a, REF + "Pritchard", more=6.0)
        self.assertEqual(said, ["NoteAuthorityWithdrawn"])
        self.assertEqual((a.g("StampDelivered"), a.g("YardAuthority"), a.g("LockridgeReported")), (1, 1, 1))

    def test_not_answered_or_stale_hands_nothing_over(self):
        for value in NO_ANSWER:
            with self.subTest(answer=value):
                a = self.carrying()
                a.box_returns(G + "AskHandOver", value)
                said = use(a, REF + "Pritchard", {"ReportUnknown": [0]}, more=6.0)
                closed(a)
                self.assertEqual(said[-1], "AskHandOver")
                self.assertEqual((a.g("StampDelivered"), a.count(a.stampitem), a.g("Reported")), (0, 1, 1))
                free(self, a, "a handover not answered")

    def test_a_dead_pritchard_receives_nothing(self):
        """SEEDED: he dies while the question is open."""
        a = self.carrying()

        def dies():
            a.who["sheriff"].dead = True
        said = use(a, REF + "Pritchard", {"ReportUnknown": [1], "AskHandOver": [0]}, also=("AskHandOver", dies))
        self.assertEqual(said[-1], "AskHandOver")
        self.assertEqual((a.g("StampDelivered"), a.count(a.stampitem), a.count(a.stampitem, a.who["sheriff"])), (0, 1, 0))

    def test_the_yards_change_not_seen_then_seen_at_the_yard(self):
        """SEEDED: the closed board does not come on. The stamp is delivered; the yard's change is not
        recorded, and Lockridge still dispatches, until it is seen."""
        a = self.carrying()
        a.refuse_call("enable", "BoardClosed")
        said = use(a, REF + "Pritchard", {"ReportUnknown": [0], "AskHandOver": [0]}, more=LONG)
        self.assertEqual(said[-2:], ["NoteStampDelivered", "NoteAuthorityFailed"])
        self.assertEqual((a.g("StampDelivered"), a.g("YardAuthority"), a.g("LockridgeReported"), state(a)["yard"]), (1, 0, 0, 2))
        load(a)
        a.allow_calls()
        use(a, "MercyTravel", {"AskTravelAgain": [0]})
        self.assertEqual(a.where(), nm.YARD)
        self.assertEqual(use(a, "Lockridge"), ["LockridgeDefault"], "nothing has been shown to have changed: she still runs the yard")
        self.assertEqual(use(a, "BoardStamped", more=LONG), ["NoteAuthorityWithdrawn"])
        self.assertEqual((a.g("YardAuthority"), a.g("LockridgeReported"), state(a)["yard"]), (1, 1, 0))
        self.assertTrue(a.on("BoardClosed") and not a.on("BoardStamped"))
        self.assertEqual(use(a, "Lockridge"), ["NoteNoDispatch"])

    def test_the_yards_notice_unanswered_is_not_recorded_and_comes_again(self):
        for value in NO_ANSWER:
            with self.subTest(answer=value):
                a = self.carrying()
                a.box_returns(G + "NoteAuthorityWithdrawn", value)
                said = use(a, REF + "Pritchard", {"ReportUnknown": [0], "AskHandOver": [0]}, more=6.0)
                closed(a)
                self.assertEqual(said[-1], "NoteAuthorityWithdrawn")
                self.assertEqual((a.g("StampDelivered"), a.g("YardAuthority"), a.g("LockridgeReported")), (1, 0, 0))
                self.assertTrue(a.on("BoardStamped") and not a.on("BoardClosed"), "the boards are as the facts stand")
                self.assertEqual(use(a, REF + "Pritchard", more=6.0), ["NoteAuthorityWithdrawn"])
                self.assertEqual((a.g("YardAuthority"), a.g("LockridgeReported")), (1, 1))

    def test_lockridge_is_not_harmed_moved_or_switched_off_by_it(self):
        a = self.carrying()
        before = (a.who["lockridge"].dead, a.who["lockridge"].disabled, tuple(a.who["lockridge"].pos))
        a.report(hand=True)
        self.assertEqual((a.who["lockridge"].dead, a.who["lockridge"].disabled, tuple(a.who["lockridge"].pos)), before)
        self.assertFalse(a.fighting("lockridge"))


class TheReport(Base):
    def done(self, **kw):
        a = at_the_cut(self, **kw)
        a.billie("back")
        a.leave()
        return a

    def test_unanswered_it_closes_the_conversation_and_reports_nothing(self):
        for value in NO_ANSWER:
            with self.subTest(answer=value):
                a = self.done()
                a.box_returns(G + "ReportUnknown", value)
                said = use(a, REF + "Pritchard")
                closed(a)
                self.assertEqual(said, ["ReportUnknown"], "nothing else of his is shown after a box nobody answered")
                self.assertEqual(a.g("Reported"), 0)
                free(self, a, "a report not answered")
                a.report()

    def test_later_goes_on_to_the_rest_of_his_conversation(self):
        a = self.done()
        said = use(a, REF + "Pritchard", {"ReportUnknown": [1], BRIEF_HUB: [3]})
        self.assertEqual(said, ["ReportUnknown", BRIEF_HUB])
        self.assertEqual(a.g("Reported"), 0)
        a.report()
        self.assertEqual(a.g("Reported"), 1)
        a.report()

    def test_what_is_reported_is_what_is_held(self):
        for course, want in (("run", ["ReportMailDelivered", "ReportRan"]), ("back", ["ReportMailRetained", "ReportBacked"]),
                             ("sold", ["ReportMailSeized", "ReportSold"]), ("defeat", ["ReportMailAboard", "ReportDoleByYou"])):
            with self.subTest(course=course):
                a = at_the_cut(self)
                if course == "run":
                    a.billie("run")
                    a.leave(at="PlatformExit")
                elif course == "back":
                    a.billie("back")
                    a.leave()
                elif course == "sold":
                    a.dole("share", "done")
                    a.back()
                    a.leave()
                else:
                    a.dole("aside")
                    a.kill("dole", by_player=True)
                    a.back()
                    a.leave()
                said = [m[len(G):] for m in a.report() if m.startswith(G)]
                self.assertEqual(said[1:3], want)
                self.assertEqual(said[-1], "ReportEnd")


class Idempotency(Base):
    def test_every_stage_is_set_once_through_every_course_used_twice(self):
        for course in ("run", "back", "sold", "defeat"):
            with self.subTest(course=course):
                a = at_the_cut(self)
                a.plate()
                a.plate()
                a.hymnal_read()
                a.hymnal_read()
                if course == "run":
                    a.billie("run")
                    a.back(at="BackFromPlatform")
                elif course == "back":
                    a.billie("back")
                elif course == "sold":
                    a.dole("share", "done")
                    a.dole()
                    a.back()
                else:
                    a.dole("aside")
                    a.kill("dole", by_player=True)
                    a.train("back")
                a.drawer("take")
                a.drawer()
                a.leave()
                a.report()
                a.report()
                a.travel()
                a.leave()
                a.report()
                self.assertEqual(sorted(n for n in set(a.road.done) if a.road.done.count(n) > 1), [])
                self.assertEqual((a.count(a.hymnal), a.count(a.stampitem) + a.count(a.stampitem, a.who["sheriff"])), (1, 1))

    def test_the_load_event_changes_nothing_anywhere(self):
        a = Rider(self)
        steps = [lambda: a.hire(), lambda: a.depart(), lambda: a.plate(), lambda: a.dole("name", "silver", "share", "back"),
                 lambda: a.billie("back"), lambda: a.drawer("sign"), lambda: a.leave(), lambda: a.report()]
        for step in steps:
            step()
            before = (a.facts(), a.pieces())
            load(a)
            self.assertEqual((a.facts(), a.pieces()), before)
            a.same("a load")

    def test_two_uses_at_once_are_one(self):
        """SEEDED: a second activation arrives while the first one's box is open."""
        a = at_the_cut(self)
        said = use(a, "Dole", SELL, also=("DoleShare", lambda: a.s.press_activate(R + "Regulator")))
        self.assertEqual(said[:3], ["DoleSermon", "DoleShare", "NoteSold"])
        # The second one is either dropped (the first still held the claim) or taken after it, when there is
        # nothing left to do with the train. It never runs beside the first.
        self.assertIn(said[3:], ([], ["NoteTrainNothing"]))
        self.assertEqual((a.count(a.caps) - a.caps_before, a.asked["caps"], a.g("Outcome")), (150, 1, 43))


if __name__ == "__main__":
    unittest.main()
