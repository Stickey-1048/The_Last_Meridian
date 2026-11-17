"""The repair of GREENWATER-STORY-001 after independent review of 7e05c6b
(docs/design/GREENWATER_STORY_001_REPAIR_RECEIPT.md), on the stand-in engine.

One class for each finding that is about the scripts. Every probe runs the
REAL scripts through the way the game reaches them: the player walks to a
piece and uses it, or walks into a trigger box, or uses Pritchard; a rule is
called directly only where the test says so.

What is SEEDED, and says so where it is done:
  - a box that comes back with -1 (no answer) or 7 (a button it does not have);
  - somebody dying, or entering a fight, while a box is open or just before a
    call into the game;
  - the road's state changing while a box is open;
  - a call into the game that does nothing (Enable, Disable, MoveTo, Kill),
    every time or once; a death that comes some time after Kill;
  - an alias with nothing in it.
None of those is a rule about the game. They are the ways a call could fail
to do what was asked, which the scripts must not take for its having been
done. Whether the game ever does any of them is not known here.

A probe is a function of its own, so that the last class can run it against
the scripts with the repair taken out again and require it to fail.

A simulated press is not a native pass. NONE OF THIS HAS BEEN SEEN IN THE
GAME. Not a compile and not a game test.
"""
import re
import unittest

from sim import SimError
from test_sim import SCRIPTS
from test_act1 import BRIEF_HUB, MSG, REF, changed_scripts, need_act1_build
from greenwater_player import G, R, ROAD, Player, gw, snapshot

NO_ANSWER = (-1, 7)


def where(ref):
    return (ref.cell, tuple(ref.pos))


def while_open(a, box, do):
    """SEEDED: `do` happens while that box is open."""
    def meanwhile(message):
        if message == G + box:
            do()
    a.s.on_box = meanwhile


def closed(a):
    a.s.on_box = None
    a.box_returns(None, None)
    a.allow_calls()


def free(t, a, what):
    """No box is held open and no judgment is under way: the next use is taken."""
    t.assertFalse(a.walk.vars["talking"], "the walk still holds its claim after " + what)
    t.assertFalse(a.rules.vars["judging"], "a judgment is still under way after " + what)
    t.assertNotIn(a.rules.vars["hangintent"], (1, 2), "a hanging is still under way after " + what)


# ============================================================ 1. scene notices

def skiff_not_confirmed(t, scripts=SCRIPTS):
    """The skiff's notice comes back with no button a person can press: nobody is moved."""
    for value in NO_ANSWER:
        a = Player(t, scripts=scripts)
        before, rafferty = snapshot(a), where(a.who["rafferty"])
        a.box_returns(G + "NoteSkiffScene", value)
        t.assertEqual(a.press(R + "Skiff"), ["NoteSkiffScene"])
        closed(a)
        t.assertFalse(a.player_at(R + "OffSideArrival"), "the player was set down at the off side on %d" % value)
        t.assertEqual(where(a.who["rafferty"]), rafferty, "Rafferty was moved on %d" % value)
        t.assertEqual(snapshot(a), before)
        free(t, a, "the skiff's notice unanswered")
        # And answered: both are set down at the off side.
        a.skiff()
        t.assertTrue(a.player_at(R + "OffSideArrival"))
        t.assertTrue(a.near("rafferty", "OffSideArrival"))


def skiff_after_something_changed(t, scripts=SCRIPTS):
    """The notice is answered, and by then the player is dead, or the road is not as it stood."""
    a = Player(t, scripts=scripts)
    rafferty = where(a.who["rafferty"])
    while_open(a, "NoteSkiffScene", lambda: setattr(a.s.player, "dead", True))
    t.assertEqual(a.press(R + "Skiff"), ["NoteSkiffScene"])
    closed(a)
    a.s.player.dead = False
    t.assertFalse(a.player_at(R + "OffSideArrival"), "a dead player was moved")
    t.assertEqual(where(a.who["rafferty"]), rafferty)

    def cut_meanwhile():
        a.rules.vars["claim"] = gw.RV_CHUTE                        # SEEDED: as if the chain were cut meanwhile
        a.rules.vars["escapepending"] = True
    while_open(a, "NoteSkiffScene", cut_meanwhile)
    t.assertEqual(a.press(R + "Skiff"), ["NoteSkiffScene"])
    closed(a)
    t.assertFalse(a.player_at(R + "OffSideArrival"), "moved though the road had changed under the notice")
    t.assertEqual(where(a.who["rafferty"]), rafferty)
    free(t, a, "a stale skiff")


def skiff_asked_of_rafferty(t, scripts=SCRIPTS):
    """Asked for through his line: the same notice, the same rule; and not at all if he dies under his own line."""
    a = Player(t, scripts=scripts)
    a.opal("wants")
    a.box_returns(G + "NoteSkiffScene", -1)
    t.assertEqual(a.press(R + "Rafferty", {G + "RaffertySkiff": [1]}), ["RaffertySkiff", "NoteSkiffScene"])
    closed(a)
    t.assertFalse(a.player_at(R + "OffSideArrival"))
    while_open(a, "RaffertySkiff", lambda: setattr(a.who["rafferty"], "dead", True))
    t.assertEqual(a.press(R + "Rafferty", {G + "RaffertySkiff": [1]}), ["RaffertySkiff"])
    closed(a)
    t.assertFalse(a.player_at(R + "OffSideArrival"), "taken across by a dead man")
    # The skiff itself still works without him.
    t.assertEqual(a.press(R + "Skiff"), ["NoteSkiffScene"])
    t.assertTrue(a.player_at(R + "OffSideArrival"))


def lever_not_confirmed(t, scripts=SCRIPTS):
    """The lever's notice comes back with no button: nobody is moved and no return is begun."""
    for value in NO_ANSWER:
        a = Player(t, scripts=scripts)
        a.gangway()
        a.chain("cut")
        before, player = snapshot(a), where(a.s.player)
        a.box_returns(G + "NoteChuteScene", value)
        t.assertEqual(a.press(R + "Pilot"), ["NoteChuteScene"])
        closed(a)
        t.assertEqual(where(a.s.player)[0], player[0])
        t.assertFalse(a.player_at(R + "ChuteStart"), "moved to the Chute on %d" % value)
        t.assertEqual(a.rules.vars["returnpending"], 0, "a return was begun on %d" % value)
        t.assertEqual(snapshot(a), before)
        free(t, a, "the lever's notice unanswered")
        # Nothing was begun, so the dock brings nothing home.
        t.assertEqual(a.press(R + "ReturnDock", enter=True), [])
        t.assertEqual((42 in a.road.done, a.g("Cargo"), a.rules.vars["escapepending"]), (False, gw.RV_CARGO_LASHED, True))
        # And answered: the run, once.
        a.pilot()
        t.assertTrue(a.player_at(R + "ChuteStart"))
        a.dock()
        t.assertEqual(a.road.done.count(42), 1)


def lever_after_something_changed(t, scripts=SCRIPTS):
    """Answered, and by then the player is dead, the head of the Chute is gone, or the road is not as it stood."""
    a = Player(t, scripts=scripts)
    a.gangway()
    a.chain("cut")
    before = snapshot(a)
    while_open(a, "NoteChuteScene", lambda: setattr(a.s.player, "dead", True))
    t.assertEqual(a.press(R + "Pilot"), ["NoteChuteScene"])
    closed(a)
    a.s.player.dead = False
    t.assertFalse(a.player_at(R + "ChuteStart"), "a dead player was moved")
    t.assertEqual(a.rules.vars["returnpending"], 0, "a return was begun for a dead player")
    t.assertEqual(snapshot(a), before)

    chute = a.alias("ChuteStart")
    marker = chute.ref
    while_open(a, "NoteChuteScene", lambda: setattr(chute, "ref", None))    # SEEDED: the marker is gone
    t.assertEqual(a.press(R + "Pilot"), ["NoteChuteScene"])
    closed(a)
    chute.ref = marker
    t.assertEqual(a.rules.vars["returnpending"], 0)

    while_open(a, "NoteChuteScene", lambda: a.rules.vars.__setitem__("burning", True))   # SEEDED: the road changed
    t.assertEqual(a.press(R + "Pilot"), ["NoteChuteScene"])
    closed(a)
    a.rules.vars["burning"] = False
    t.assertEqual(a.rules.vars["returnpending"], 0)
    t.assertFalse(a.player_at(R + "ChuteStart"))
    free(t, a, "a stale lever")
    a.pilot()
    a.dock()
    t.assertEqual(a.road.done.count(42), 1)


def lever_resumed(t, scripts=SCRIPTS):
    """A return already begun stays begun whatever a later notice comes back with; it is never another kind,
    and it is not completed by the lever."""
    a = Player(t, scripts=scripts)
    a.gangway()
    a.chain("cut")
    a.pilot()
    t.assertEqual(a.rules.vars["returnpending"], gw.RV_RETURN_ESCAPE)
    a.s.walk_to(R + "Table")
    there = where(a.s.player)
    for value in NO_ANSWER:
        a.box_returns(G + "NoteChuteScene", value)
        t.assertEqual(a.press(R + "Pilot"), ["NoteChuteScene"])
        closed(a)
        t.assertEqual((a.rules.vars["returnpending"], a.rules.vars["escapepending"], 42 in a.road.done), (gw.RV_RETURN_ESCAPE, True, False))
        t.assertFalse(a.player_at(R + "ChuteStart"))
    # Begun again, as often as wanted; then done once at the dock.
    t.assertEqual(a.press(R + "Pilot"), ["NoteChuteScene"])
    t.assertTrue(a.player_at(R + "ChuteStart"))
    t.assertNotEqual(where(a.s.player), there)
    t.assertNotIn(42, a.road.done)
    a.dock()
    a.same("the run resumed and done")
    t.assertEqual(a.road.done.count(42), 1)


def tow_not_confirmed(t, scripts=SCRIPTS):
    a = Player(t, scripts=scripts, charisma=5)
    a.gangway()
    a.table(["deal"], judge="release")
    for value in NO_ANSWER:
        a.box_returns(G + "NoteTowScene", value)
        t.assertEqual(a.press(R + "Pilot"), ["NoteTowScene"])
        closed(a)
        t.assertEqual((a.rules.vars["returnpending"], a.g("Cargo"), a.g("GrainHome")), (0, gw.RV_CARGO_YIELDED, 0))
        t.assertFalse(a.player_at(R + "ChuteStart"))
    a.pilot()
    t.assertEqual(a.rules.vars["returnpending"], gw.RV_RETURN_TOW)
    a.dock()
    t.assertEqual((a.g("Cargo"), a.g("GrainHome")), (gw.RV_CARGO_HOME_WHOLE, 1))


def fire_notice_not_confirmed(t, scripts=SCRIPTS):
    """The fire is recorded once it is seen. Its closing notice unanswered moves nobody; the record stands."""
    a = Player(t, scripts=scripts)
    a.gangway()
    a.chain("burn")
    player = where(a.s.player)
    a.box_returns(G + "NoteFireScene", -1)
    shown = a.press(R + "FireControl", {G + "AskFire": [0]})
    closed(a)
    t.assertEqual(shown, ["AskFire", "NoteFireScene"])
    t.assertEqual((a.road.done.count(43), a.g("Outcome"), a.g("Cargo")), (1, gw.RV_FIRE, gw.RV_CARGO_DESTROYED))
    t.assertFalse(a.player_at(R + "Arrival"), "moved to the landing with the notice unanswered")
    t.assertEqual(where(a.s.player)[0], player[0])
    free(t, a, "the fire's notice unanswered")
    # Rafferty says his line when he is next spoken to, once.
    t.assertEqual(a.press(R + "Rafferty"), ["RaffertyBurned"])
    t.assertEqual(a.press(R + "Rafferty"), ["RaffertyDefault"])


class SceneNotices(unittest.TestCase):
    """Finding 1. Only the notice's one button goes on; after it everything it needs is asked for again."""

    def setUp(self):
        need_act1_build(self)

    def test_the_skiffs_notice_unanswered_moves_nobody(self):
        skiff_not_confirmed(self)

    def test_the_skiff_after_the_player_died_or_the_road_changed(self):
        skiff_after_something_changed(self)

    def test_the_skiff_asked_of_rafferty(self):
        skiff_asked_of_rafferty(self)

    def test_the_levers_notice_unanswered_moves_nobody_and_begins_nothing(self):
        lever_not_confirmed(self)

    def test_the_lever_after_the_player_died_the_marker_went_or_the_road_changed(self):
        lever_after_something_changed(self)

    def test_a_return_already_begun_is_kept_and_begun_again(self):
        lever_resumed(self)

    def test_the_tows_notice_unanswered(self):
        tow_not_confirmed(self)

    def test_the_fires_closing_notice_unanswered(self):
        fire_notice_not_confirmed(self)


# ================================================================== 2. hanging

def beaten(t, scripts=SCRIPTS, **kw):
    a = Player(t, scripts=scripts, charisma=5, **kw)
    a.gangway()
    return a


def choose_hanging(a, more=4.0):
    """The hand is dealt and won at his table and the steeple is chosen. What was then shown."""
    at = len(a.s.messages_shown)
    a.press(R + "Table", {G + "HatcherTable": [0], G + "HatcherLost": [0]})
    a.p.pause(more)
    return [m[len(G):] for m in a.s.messages_shown[at:] if m.startswith(G)]


def not_hanged(t, a, alive=True, what=""):
    t.assertEqual(not a.who["hatcher"].dead, alive, what)
    t.assertEqual((60 in a.road.done, a.g("HatcherHanged"), a.rules.vars["hangintent"]), (False, 0, 0), what)
    free(t, a, what)


def hanging_as_chosen(t, scripts=SCRIPTS):
    a = beaten(t, scripts)
    shown = choose_hanging(a)
    t.assertEqual(shown, ["HatcherTable", "CardStakes", "HatcherLost", "ConfirmHang"])
    t.assertTrue(a.who["hatcher"].dead)
    t.assertTrue(a.near("hatcher", "Steeple", 256.0), "he was not hanged at the steeple")
    t.assertEqual((a.road.done.count(60), a.g("Hatcher"), a.g("HatcherHanged"), a.rules.vars["hangintent"]), (1, gw.RV_H_HANGED, 1, 3))
    t.assertEqual((a.asked_of("moveto", "hatcher"), a.asked_of("kill", "hatcher")), (1, 1))
    free(t, a, "a hanging")
    a.p.pause(5.0)                                                 # his alias's death event comes and changes nothing
    t.assertEqual((a.road.done.count(60), a.g("Hatcher"), a.s.invoke(ROAD, "HatcherState", [])), (1, gw.RV_H_HANGED, gw.RV_H_HANGED))


def no_ring_no_hanging(t, scripts=SCRIPTS):
    """The ring missing, or switched off: nothing is done to him, at his table or anywhere."""
    for how in ("missing", "switched off"):
        a = beaten(t, scripts)
        at_table = where(a.who["hatcher"])
        if how == "missing":
            a.alias("Steeple", a.road).ref = None                  # SEEDED
        else:
            a.s.placed[R + "Steeple"].disabled = True              # SEEDED
        shown = choose_hanging(a)
        t.assertEqual(shown, ["HatcherTable", "CardStakes", "HatcherLost"], how)
        not_hanged(t, a, what="the ring " + how)
        t.assertEqual(where(a.who["hatcher"]), at_table, "he was moved with the ring " + how)
        t.assertEqual((a.asked_of("moveto", "hatcher"), a.asked_of("kill", "hatcher")), (0, 0), how)
        t.assertEqual(a.g("Hatcher"), gw.RV_H_FREE)
        # The other two judgments, and the grain, are as they were.
        t.assertEqual(a.press(R + "Table", {G + "HatcherLost": [1]}), ["HatcherLost", "ConfirmCustody"])
        t.assertEqual((61 in a.road.done, a.g("Hatcher")), (True, gw.RV_H_CUSTODY))
        a.press(R + "Pilot")
        a.press(R + "ReturnDock", enter=True)
        t.assertEqual((a.g("Cargo"), a.g("GrainHome")), (gw.RV_CARGO_HOME_WHOLE, 1))


def not_at_the_ring_no_kill(t, scripts=SCRIPTS):
    """The move does nothing: he is still at his table, and is not killed there."""
    a = beaten(t, scripts)
    at_table = where(a.who["hatcher"])
    a.refuse_call("moveto", "hatcher")                             # SEEDED
    shown = choose_hanging(a)
    t.assertEqual(shown[-1], "NoteJudgmentFailed")
    not_hanged(t, a, what="a move that did nothing")
    t.assertEqual(where(a.who["hatcher"]), at_table)
    t.assertEqual((a.asked_of("moveto", "hatcher"), a.asked_of("kill", "hatcher")), (1, 0))
    closed(a)
    # Chosen again with the move working: carried out.
    t.assertEqual(a.press(R + "Table", {G + "HatcherLost": [0]}), ["HatcherLost", "ConfirmHang"])
    t.assertEqual((a.road.done.count(60), a.g("Hatcher"), a.asked_of("kill", "hatcher")), (1, gw.RV_H_HANGED, 1))


def somebody_gone_before_the_kill(t, scripts=SCRIPTS):
    """Between the choice and the rope: Opal dies, or he starts a fight. He is taken to the ring and no further."""
    for who, what in (("opal", "dead"), ("hatcher", "fighting")):
        a = beaten(t, scripts)

        def meanwhile(who=who, what=what, a=a):
            if what == "dead":
                a.who[who].dead = True                             # SEEDED
            else:
                a.who[who].combat_target = a.who["crew1"]          # SEEDED
        a.just_before("moveto", "hatcher", meanwhile)
        shown = choose_hanging(a)
        t.assertEqual(shown[-1], "ConfirmHang", who)
        not_hanged(t, a, what="%s %s before the kill" % (who, what))
        t.assertEqual(a.asked_of("kill", "hatcher"), 0, who)
        t.assertEqual(a.g("Hatcher"), gw.RV_H_FREE)
        closed(a)


def fighting_when_the_verdict_is_given(t, scripts=SCRIPTS):
    """He starts a fight while his own question is open: nothing is carried out on him, whatever was pressed."""
    for pick in (0, 1, 2):
        a = beaten(t, scripts)
        at_table = where(a.who["hatcher"])
        while_open(a, "HatcherLost", lambda a=a: setattr(a.who["hatcher"], "combat_target", a.who["crew1"]))
        at = len(a.s.messages_shown)
        a.press(R + "Table", {G + "HatcherTable": [0], G + "HatcherLost": [pick]})
        closed(a)
        t.assertEqual([m[len(G):] for m in a.s.messages_shown[at:]], ["HatcherTable", "CardStakes", "HatcherLost"], pick)
        not_hanged(t, a, what="a fight under his question, button %d" % pick)
        t.assertEqual((a.g("Hatcher"), 61 in a.road.done, a.g("HatcherFriend"), where(a.who["hatcher"])), (gw.RV_H_FREE, False, 0, at_table), pick)
        t.assertEqual((a.asked_of("moveto", "hatcher"), a.asked_of("kill", "hatcher")), (0, 0))


def the_kill_refused(t, scripts=SCRIPTS):
    """Kill does nothing. Asked once, waited for, nothing recorded; and a death long afterwards is no hanging."""
    a = beaten(t, scripts)
    a.refuse_call("kill", "hatcher")                               # SEEDED
    shown = choose_hanging(a)
    t.assertEqual(shown[-1], "NoteJudgmentFailed")
    not_hanged(t, a, what="a kill that did nothing")
    t.assertTrue(a.near("hatcher", "Steeple", 256.0))
    t.assertEqual((a.asked_of("kill", "hatcher"), a.g("Hatcher")), (1, gw.RV_H_FREE))
    closed(a)
    a.kill("hatcher", by_player=True)                              # an unrelated death, later
    a.p.pause(5.0)
    t.assertEqual((60 in a.road.done, a.g("HatcherHanged"), a.g("Hatcher"), a.s.invoke(ROAD, "HatcherState", [])),
                  (False, 0, gw.RV_H_DEAD, gw.RV_H_DEAD))
    # She is told what is true: he is dead, and not by her rope.
    a.press(R + "Pilot")
    a.press(R + "ReturnDock", enter=True)
    t.assertEqual(a.press(R + "Opal"), ["OpalWonHatcherDead"])


def the_death_comes_late(t, scripts=SCRIPTS):
    """Kill takes half a second to take effect. It is still the hanging, by one Kill, however it is heard of."""
    a = beaten(t, scripts)
    a.dies_late("hatcher", 0.5)                                    # SEEDED
    shown = choose_hanging(a)
    t.assertEqual(shown, ["HatcherTable", "CardStakes", "HatcherLost", "ConfirmHang"])
    t.assertTrue(a.who["hatcher"].dead)
    t.assertEqual((a.road.done.count(60), a.g("Hatcher"), a.g("HatcherHanged"), a.asked_of("kill", "hatcher")), (1, gw.RV_H_HANGED, 1, 1))
    free(t, a, "a late death")
    a.p.pause(5.0)
    t.assertEqual((a.road.done.count(60), a.g("Hatcher"), a.s.invoke(ROAD, "HatcherState", [])), (1, gw.RV_H_HANGED, gw.RV_H_HANGED))


def the_death_comes_after_the_wait(t, scripts=SCRIPTS):
    """The declared bound. A death ten seconds after the one Kill is outside it: recorded as a death otherwise,
    consistently, and never as a hanging that the wait had already given up."""
    a = beaten(t, scripts)
    a.dies_late("hatcher", 10.0)                                   # SEEDED
    shown = choose_hanging(a)
    t.assertEqual(shown[-1], "NoteJudgmentFailed")
    not_hanged(t, a, what="still alive when the wait ended")
    a.p.pause(12.0)
    t.assertTrue(a.who["hatcher"].dead)
    t.assertEqual((60 in a.road.done, a.g("HatcherHanged"), a.g("Hatcher"), a.s.invoke(ROAD, "HatcherState", []), a.asked_of("kill", "hatcher")),
                  (False, 0, gw.RV_H_DEAD, gw.RV_H_DEAD, 1))


def the_event_and_the_wait_agree(t, scripts=SCRIPTS):
    """His alias's death event, heard while an execution is under way, writes the same record the wait would;
    heard with none under way, a death otherwise; and with him alive, nothing."""
    a = beaten(t, scripts)
    a.win_and_say_nothing()                                        # won; his question left
    t.assertFalse(a.s.invoke(ROAD, "RecordHanging", []))
    a.rules.vars["hangintent"] = 2                                 # SEEDED: an execution under way
    a.rules.vars["hangactor"] = a.who["hatcher"]                   # SEEDED exact intended actor, not whichever alias is later present
    t.assertFalse(a.s.invoke(ROAD, "RecordHanging", []), "recorded with him alive")
    a.s.invoke(ROAD, "HatcherDied", [a.who["hatcher"]])
    t.assertEqual((60 in a.road.done, a.g("Hatcher")), (False, gw.RV_H_FREE), "an event with him alive recorded something")
    a.who["hatcher"].dead = True                                   # SEEDED
    a.s.invoke(ROAD, "HatcherDied", [a.who["hatcher"]])
    t.assertEqual((a.road.done.count(60), a.g("Hatcher"), a.g("HatcherHanged"), a.rules.vars["hangintent"]), (1, gw.RV_H_HANGED, 1, 3))
    a.s.invoke(ROAD, "HatcherDied", [a.who["hatcher"]])
    t.assertTrue(a.s.invoke(ROAD, "RecordHanging", []))
    t.assertEqual((a.road.done.count(60), a.g("Hatcher")), (1, gw.RV_H_HANGED))

    b = beaten(t, scripts)
    b.win_and_say_nothing()
    b.who["hatcher"].dead = True                                   # SEEDED: no execution under way
    b.s.invoke(ROAD, "HatcherDied", [b.who["hatcher"]])
    t.assertEqual((60 in b.road.done, b.g("HatcherHanged"), b.g("Hatcher")), (False, 0, gw.RV_H_DEAD))


class Hanging(unittest.TestCase):
    """Finding 2. Nobody is killed who was not seen at the ring; one Kill; a hanging only when he is seen dead
    within the wait, by the wait or by the event."""

    def setUp(self):
        need_act1_build(self)

    def test_chosen_and_carried_out(self):
        hanging_as_chosen(self)

    def test_no_ring_no_hanging_and_the_other_judgments_stand(self):
        no_ring_no_hanging(self)

    def test_not_seen_at_the_ring_not_killed(self):
        not_at_the_ring_no_kill(self)

    def test_opal_dead_or_hatcher_fighting_before_the_kill(self):
        somebody_gone_before_the_kill(self)

    def test_a_fight_under_his_question_and_nothing_is_carried_out(self):
        fighting_when_the_verdict_is_given(self)

    def test_the_kill_refused_and_a_later_death_is_no_hanging(self):
        the_kill_refused(self)

    def test_a_death_half_a_second_late_is_the_hanging(self):
        the_death_comes_late(self)

    def test_a_death_after_the_wait_is_a_death_otherwise(self):
        the_death_comes_after_the_wait(self)

    def test_the_death_event_and_the_wait_write_the_same_record(self):
        the_event_and_the_wait_agree(self)

    def test_with_opal_dead_the_approved_prefix_and_no_hanging_offered(self):
        a = beaten(self)
        a.kill("opal")
        a.before = a.world()
        a.table(["deal"], judge="custody")
        self.assertEqual((61 in a.road.done, 60 in a.road.done, a.asked_of("kill", "hatcher")), (True, False, 0))


# ===================================================================== 3. fire

def warned(t, scripts=SCRIPTS):
    a = Player(t, scripts=scripts)
    a.gangway()
    a.chain("burn")
    return a


def ordered_and_not_seen(t, a, shown, what):
    """The fire is ordered, not recorded, exclusive, and can be tried again at the firebox."""
    t.assertEqual(shown, ["AskFire", "NoteFireFailed"], what)
    t.assertEqual((a.rules.vars["burning"], a.rules.vars["claim"], 43 in a.road.done, a.g("Outcome"), a.g("Cargo"), a.g("QueenBurned")),
                  (True, gw.RV_FIRE, False, 0, gw.RV_CARGO_LASHED, 0), what)
    t.assertEqual((a.on("FireControl"), a.on("Burnt"), a.on("CargoLashed"), a.on("Table"), a.on("Chain"), a.on("Pilot")),
                  (True, False, True, True, True, True), what)
    free(t, a, what)
    # No other course, and nothing complete.
    t.assertEqual(a.press(R + "Chain"), ["NoteChainNothing"], what)
    t.assertEqual(a.press(R + "Pilot"), ["NotePilotNothing"], what)
    t.assertNotIn("HatcherTable", a.press(R + "Table"), what)
    t.assertFalse(a.s.invoke(ROAD, "CanComplete", []), what)
    t.assertEqual((a.rules.vars["claim"], a.g("Outcome"), 41 in a.road.done, 44 in a.road.done, a.rules.vars["escapepending"]),
                  (gw.RV_FIRE, 0, False, False, False), what)


def fire_not_seen_then_tried_again(t, scripts=SCRIPTS):
    for kind, piece in (("enable", "Burnt"), ("disable", "CargoLashed")):
        a = warned(t, scripts)
        a.refuse_call(kind, piece, times=1)                        # SEEDED: once
        ordered_and_not_seen(t, a, a.press(R + "FireControl", {G + "AskFire": [0]}), "%s of %s refused" % (kind, piece))
        # Again, by using the firebox: staged, not ordered again.
        again = a.press(R + "FireControl", {G + "AskFire": [0]})
        t.assertEqual(again, ["NoteFireScene", "RaffertyBurned"], piece)
        a.m.use_fire(True)
        a.same("the fire shown at the second try", world=True)
        t.assertEqual((a.road.done.count(43), a.on("Burnt"), a.on("CargoLashed"), a.on("FireControl")), (1, True, False, False))
        # A third time: the firebox is switched off now, so it cannot be used at all; and nothing happened twice.
        with t.assertRaises(SimError):
            a.press(R + "FireControl", {G + "AskFire": [0]})
        t.assertEqual((a.road.done.count(43), a.g("QueenBurned")), (1, 1))


def fire_left_and_come_back_to(t, scripts=SCRIPTS):
    """Ordered and not seen; the player goes to Mercy and comes back: the firebox is still how it is tried."""
    a = warned(t, scripts)
    a.refuse_call("enable", "Burnt", times=1)
    ordered_and_not_seen(t, a, a.press(R + "FireControl", {G + "AskFire": [0]}), "before leaving")
    t.assertEqual(a.press(R + "Exit", {G + "AskLeaveUnresolved": [0]}), ["AskLeaveUnresolved", "NoteLeftUnresolved"])
    t.assertNotIn(100, a.road.done)
    a.press(R + "MercyTravel", {G + "AskTravel": [0]})
    t.assertTrue(a.on("FireControl"))
    t.assertEqual(a.press(R + "FireControl"), ["NoteFireScene", "RaffertyBurned"])
    t.assertEqual(a.road.done.count(43), 1)


def no_marker_no_order(t, scripts=SCRIPTS):
    """The burned Queen's marker is not there: no order is taken, and every other course stays open."""
    a = warned(t, scripts)
    a.alias("Burnt").ref = None                                    # SEEDED
    before = snapshot(a)
    t.assertEqual(a.press(R + "FireControl", {G + "AskFire": [0]}), ["NoteFireNoMarker"])
    t.assertEqual(snapshot(a), before)
    t.assertEqual((a.rules.vars["burning"], a.rules.vars["claim"]), (False, 0))
    a.chain("cut")
    a.pilot()
    a.dock()
    t.assertEqual(a.road.done.count(42), 1)


def ordered_and_cannot_be_shown(t, scripts=SCRIPTS):
    """Ordered, not seen, and then the marker is gone, or the firebox cannot be had: an exact statement, and no
    instruction to use what cannot be used."""
    a = warned(t, scripts)
    a.refuse_call("enable", "Burnt", times=1)
    a.press(R + "FireControl", {G + "AskFire": [0]})
    a.alias("Burnt").ref = None                                    # SEEDED: gone after the order
    t.assertEqual(a.press(R + "FireControl"), ["NoteFireStuck"])
    t.assertEqual((a.rules.vars["burning"], 43 in a.road.done, a.g("Outcome")), (True, False, 0))
    free(t, a, "a fire that cannot be shown")

    b = warned(t, scripts)
    b.refuse_call("enable", "Burnt")                               # SEEDED: every time
    b.refuse_call("enable", "FireControl")
    while_open(b, "AskFire", lambda: setattr(b.s.placed[R + "FireControl"], "disabled", True))   # SEEDED
    at = len(b.s.messages_shown)
    b.press(R + "FireControl", {G + "AskFire": [0]})
    b.p.pause(3.0)                                                 # two looks of two seconds each: the marker, then the firebox
    closed(b)
    shown = [m[len(G):] for m in b.s.messages_shown[at:]]
    t.assertEqual(shown, ["AskFire", "NoteFireStuck"])
    t.assertNotIn("NoteFireFailed", shown)
    t.assertEqual((b.rules.vars["burning"], 43 in b.road.done, b.on("FireControl")), (True, False, False))


def fire_not_confirmed_or_stale(t, scripts=SCRIPTS):
    a = warned(t, scripts)
    before = snapshot(a)
    for value in NO_ANSWER + (1,):
        a.box_returns(G + "AskFire", value)
        t.assertEqual(a.press(R + "FireControl"), ["AskFire"])
        closed(a)
        t.assertEqual(snapshot(a), before, value)

    def cut_meanwhile():
        a.rules.vars["claim"] = gw.RV_CHUTE                        # SEEDED: the chain cut while the box is open
        a.rules.vars["escapepending"] = True
    while_open(a, "AskFire", cut_meanwhile)
    t.assertEqual(a.press(R + "FireControl", {G + "AskFire": [0]}), ["AskFire"])
    closed(a)
    t.assertEqual((a.rules.vars["burning"], a.rules.vars["claim"], 43 in a.road.done, a.on("Burnt")), (False, gw.RV_CHUTE, False, False))


def the_road_records_no_fire_it_does_not_see(t, scripts=SCRIPTS):
    """The rule itself, asked directly: with no marker, the marker off, or the cargo still lashed, nothing."""
    a = warned(t, scripts)
    a.s.invoke(ROAD, "OrderFire", [])
    marker, lashed = a.s.placed[R + "Burnt"], a.s.placed[R + "CargoLashed"]
    for burnt, cargo in ((None, None), (marker, lashed), (marker, None)):
        t.assertFalse(a.s.invoke(ROAD, "FireDone", [burnt, cargo]))
        t.assertEqual((a.rules.vars["burning"], 43 in a.road.done, a.g("Cargo")), (True, False, gw.RV_CARGO_LASHED))
    marker.disabled = False                                        # SEEDED
    t.assertFalse(a.s.invoke(ROAD, "FireDone", [marker, lashed]), "recorded with the cargo still lashed")
    lashed.disabled = True
    t.assertTrue(a.s.invoke(ROAD, "FireDone", [marker, lashed]))
    t.assertFalse(a.s.invoke(ROAD, "FireDone", [marker, lashed]))
    t.assertEqual(a.road.done.count(43), 1)


class Fire(unittest.TestCase):
    """Finding 3. A fire that was ordered and could not be shown can be tried again where the text says."""

    def setUp(self):
        need_act1_build(self)

    def test_not_seen_at_first_then_shown_by_using_the_firebox_again(self):
        fire_not_seen_then_tried_again(self)

    def test_ordered_left_and_come_back_to(self):
        fire_left_and_come_back_to(self)

    def test_no_marker_no_order(self):
        no_marker_no_order(self)

    def test_ordered_and_cannot_be_shown_says_exactly_that(self):
        ordered_and_cannot_be_shown(self)

    def test_not_confirmed_or_stale_orders_nothing(self):
        fire_not_confirmed_or_stale(self)

    def test_the_road_records_no_fire_it_does_not_see(self):
        the_road_records_no_fire_it_does_not_see(self)


# ============================================== 5. between pages, before commitments

def admission_interrupted(t, scripts=SCRIPTS):
    """Hatcher dies, or starts a fight, under either half of his admission: the hire is not learned by it."""
    for box, want in (("HatcherPaidA", ["HatcherTable", "HatcherPaidA"]), ("HatcherPaidB", ["HatcherTable", "HatcherPaidA", "HatcherPaidB"])):
        for what in ("dead", "fighting"):
            a = Player(t, scripts=scripts)
            a.gangway()

            def meanwhile(a=a, what=what):
                if what == "dead":
                    a.who["hatcher"].dead = True                   # SEEDED
                else:
                    a.who["hatcher"].combat_target = a.who["crew1"]
            while_open(a, box, meanwhile)
            shown = a.press(R + "Table", {G + "HatcherTable": [2, 3]})
            closed(a)
            t.assertEqual(shown, want, "%s under %s" % (what, box))
            t.assertEqual((50 in a.road.done, a.g("SilverRiver"), a.rules.vars["hireheard"]), (False, 0, False), "%s under %s" % (what, box))
            free(t, a, "an admission interrupted")
            # The letter is another way, and does not need him.
            t.assertEqual(a.press(R + "Strongbox")[:1], ["LetterPage1"])
            t.assertEqual((50 in a.road.done, a.g("SilverRiver"), a.rules.vars["hireread"], a.rules.vars["hireheard"]), (True, 1, True, False))


def admission_heard_and_evidence_kept(t, scripts=SCRIPTS):
    a = Player(t, scripts=scripts)
    a.gangway()
    a.strongbox()
    t.assertEqual((a.g("SilverRiver"), a.rules.vars["hireread"]), (1, True))
    while_open(a, "HatcherPaidB", lambda: setattr(a.who["hatcher"], "dead", True))
    a.press(R + "Table", {G + "HatcherTable": [2, 3]})
    closed(a)
    t.assertEqual((50 in a.road.done, a.g("SilverRiver"), a.rules.vars["hireread"], a.rules.vars["hireheard"]), (True, 1, True, False))
    # And heard to its end from a living man: learned by it.
    b = Player(t, scripts=scripts)
    b.gangway()
    b.table(["paid", "leave"])
    t.assertEqual((50 in b.road.done, b.g("SilverRiver"), b.rules.vars["hireheard"]), (True, 1, True))
    # The rule itself: no admission from a man who is not at his table.
    c = Player(t, scripts=scripts)
    c.gangway()
    c.who["hatcher"].combat_target = c.who["crew1"]                # SEEDED
    t.assertFalse(c.s.invoke(ROAD, "LearnHire", [gw.RV_HIRE_ADMISSION]))
    t.assertTrue(c.s.invoke(ROAD, "LearnHire", [gw.RV_HIRE_LETTER]))


def paid(t, scripts=SCRIPTS):
    a = Player(t, scripts=scripts)
    a.gangway()
    a.table(["share"])
    return a


def the_lie_delivered_is_kept(t, scripts=SCRIPTS):
    """The lie is told to her alive: grain_sold from then on. Her answer cancelled, or she dies under it: her
    thanks, stage 46 and her cup wait, and nothing told is taken back."""
    for value in NO_ANSWER:
        a = paid(t, scripts)
        a.box_returns(G + "OpalAfterShare", value)
        t.assertEqual(a.press(R + "Opal", {G + "AskLie": [0]}), ["AskLie", "OpalAfterShare"])
        closed(a)
        t.assertEqual((a.rules.vars["lietold"], a.g("GrainSold"), a.rules.vars["lieheard"], 46 in a.road.done, a.count(a.meal)),
                      (True, 1, False, False, 0), value)
        free(t, a, "her answer unanswered")
        # Spoken to again: not asked again whether to lie; her answer, then the journal and her cup.
        t.assertEqual(a.press(R + "Opal"), ["OpalAfterShare"])
        t.assertEqual((a.g("GrainSold"), a.rules.vars["lieheard"], a.road.done.count(46), a.count(a.meal)), (1, True, 1, 1))
        t.assertEqual(a.press(R + "Opal"), ["OpalDefault"])
        t.assertEqual((a.road.done.count(46), a.count(a.meal)), (1, 1))

    for what in ("dead", "fighting"):
        b = paid(t, scripts)

        def meanwhile(b=b, what=what):
            if what == "dead":
                b.who["opal"].dead = True                          # SEEDED
            else:
                b.who["opal"].combat_target = b.who["crew1"]
        while_open(b, "OpalAfterShare", meanwhile)
        t.assertEqual(b.press(R + "Opal", {G + "AskLie": [0]}), ["AskLie", "OpalAfterShare"])
        closed(b)
        t.assertEqual((b.rules.vars["lietold"], b.g("GrainSold"), b.rules.vars["lieheard"], 46 in b.road.done, b.count(b.meal)),
                      (True, 1, False, False, 0), what)
        # The road is still finished by the paid deal, with what was earned and no more.
        t.assertEqual(b.press(R + "Exit", {G + "AskLeaveResolved": [0]}), ["AskLeaveResolved", "NoteRoadComplete"])
        t.assertEqual((b.g("GrainSold"), 46 in b.road.done), (1, False))


def no_lie_to_nobody(t, scripts=SCRIPTS):
    """She is dead, or fighting, before the lie is told: no lie was told, and none is recorded."""
    for what in ("dead", "fighting"):
        a = paid(t, scripts)

        def meanwhile(a=a, what=what):
            if what == "dead":
                a.who["opal"].dead = True                          # SEEDED
            else:
                a.who["opal"].combat_target = a.who["crew1"]
        while_open(a, "AskLie", meanwhile)
        t.assertEqual(a.press(R + "Opal", {G + "AskLie": [0]}), ["AskLie"])
        closed(a)
        t.assertEqual((a.rules.vars["lietold"], a.g("GrainSold"), a.rules.vars["lieheard"], 46 in a.road.done), (False, 0, False, False), what)
    # Declined, or the question unanswered: the same.
    b = paid(t, scripts)
    for value in NO_ANSWER + (1,):
        b.box_returns(G + "AskLie", value)
        t.assertEqual(b.press(R + "Opal"), ["AskLie"])
        closed(b)
        t.assertEqual((b.rules.vars["lietold"], b.g("GrainSold")), (False, 0), value)
    # The rules themselves: payment alone earns nothing; her answer is not heard from a dead woman.
    t.assertFalse(b.s.invoke(ROAD, "LieWasHeard", []))
    t.assertTrue(b.s.invoke(ROAD, "TellLie", []))
    b.who["opal"].dead = True                                      # SEEDED
    t.assertFalse(b.s.invoke(ROAD, "LieWasHeard", []))
    t.assertEqual((b.g("GrainSold"), b.rules.vars["lieheard"], 46 in b.road.done), (1, False, False))


def her_question_answered_to_her(t, scripts=SCRIPTS):
    """The barge is home and she asks what is to be done with him; she dies under her own question: nothing."""
    for pick in (0, 1, 2):
        a = Player(t, scripts=scripts, charisma=5)
        a.gangway()
        a.win_and_say_nothing()
        a.pilot()
        a.dock()
        while_open(a, "OpalAfterWon", lambda a=a: setattr(a.who["opal"], "dead", True))
        t.assertEqual(a.press(R + "Opal", {G + "OpalAfterWon": [pick]}), ["OpalAfterWon"], pick)
        closed(a)
        t.assertEqual((a.g("Hatcher"), 60 in a.road.done, 61 in a.road.done, a.g("HatcherFriend"), a.who["hatcher"].dead), (gw.RV_H_FREE, False, False, 0, False), pick)
        free(t, a, "her question unanswered to her")
        # At his table what can still be done is done: Pritchard, alive.
        t.assertEqual(a.press(R + "Table", {G + "HatcherLostNoOpal": [0]}), ["HatcherLostNoOpal", "ConfirmCustody"])
        t.assertEqual((61 in a.road.done, a.g("Hatcher")), (True, gw.RV_H_CUSTODY))


def raffertys_chain_answered_to_rafferty(t, scripts=SCRIPTS):
    a = Player(t, scripts=scripts)
    a.gangway()
    while_open(a, "RaffertyChain", lambda: setattr(a.who["rafferty"], "dead", True))
    t.assertEqual(a.press(R + "Chain", {G + "RaffertyChain": [0]}), ["RaffertyChain"])
    closed(a)
    t.assertEqual((a.rules.vars["claim"], a.rules.vars["escapepending"]), (0, False))
    # Without him the chain says so itself, and can be cut.
    t.assertEqual(a.press(R + "Chain", {G + "AskChain": [0]}), ["AskChain", "NoteChainCut"])
    t.assertEqual((a.rules.vars["claim"], a.rules.vars["escapepending"]), (gw.RV_CHUTE, True))


class BetweenPagesAndBeforeCommitments(unittest.TestCase):
    """Finding 5. Whoever a line or a commitment needs is asked for again after every box that leads to it."""

    def setUp(self):
        need_act1_build(self)

    def test_an_admission_interrupted_teaches_nothing_and_the_letter_still_does(self):
        admission_interrupted(self)

    def test_an_admission_heard_and_evidence_already_earned(self):
        admission_heard_and_evidence_kept(self)

    def test_the_lie_delivered_is_kept_and_her_thanks_wait_for_her(self):
        the_lie_delivered_is_kept(self)

    def test_no_lie_is_recorded_that_was_told_to_nobody(self):
        no_lie_to_nobody(self)

    def test_opals_question_is_answered_to_opal(self):
        her_question_answered_to_her(self)

    def test_raffertys_line_is_answered_to_rafferty(self):
        raffertys_chain_answered_to_rafferty(self)


# =================================================================== 6. report

def finished(t, scripts=SCRIPTS, letter=False, **kw):
    a = Player(t, scripts=scripts, **kw)
    a.gangway()
    if letter:
        a.strongbox()
    a.chain("cut")
    a.pilot()
    a.dock()
    a.leave()
    return a


def briefing_state(a):
    q = a.s.quests["TLM_MercyBriefing"]
    return (q.running, list(q.done), dict(q.displayed), dict(q.completed_objectives))


def report_not_answered_closes(t, scripts=SCRIPTS):
    """Through Pritchard himself: the report is shown and comes back with no button. Nothing else is shown in
    that conversation: no briefing, no other line."""
    for letter, box in ((False, "ReportUnknown"), (True, "ReportKnown")):
        for value in NO_ANSWER:
            a = finished(t, scripts, letter=letter)
            before = briefing_state(a)
            a.box_returns(G + box, value)
            shown = a.press(REF + "Pritchard", {BRIEF_HUB: [3]})
            closed(a)
            t.assertEqual(shown, [box], "%s came back %d" % (box, value))
            t.assertEqual((a.g("Reported"), briefing_state(a)), (0, before))
            t.assertFalse(a.s.quests["TLM_A1"].scripts[0].vars["talking"], "the first section still holds Pritchard's conversation")
            # He can be asked again, and then told.
            a.report()
            t.assertEqual(a.g("Reported"), 1)


def report_stale_closes(t, scripts=SCRIPTS):
    """Shown, and by the time it is answered Pritchard is dead or fighting, or the player is dead: closed,
    whichever button was pressed."""
    for pick in (0, 1):
        for who, what in (("sheriff", "dead"), ("sheriff", "fighting"), ("player", "dead")):
            a = finished(t, scripts)
            before = briefing_state(a)

            def meanwhile(a=a, who=who, what=what):
                actor = a.s.player if who == "player" else a.who[who]
                if what == "dead":
                    actor.dead = True                              # SEEDED
                else:
                    actor.combat_target = a.who["crew1"]
            while_open(a, "ReportUnknown", meanwhile)
            shown = a.press(REF + "Pritchard", {G + "ReportUnknown": [pick], BRIEF_HUB: [3]})
            closed(a)
            t.assertEqual(shown, ["ReportUnknown"], "%s %s, button %d" % (who, what, pick))
            t.assertEqual((a.g("Reported"), briefing_state(a)), (0, before))


def report_later_and_given(t, scripts=SCRIPTS):
    """The documented second button: left for later, and the briefing follows as before. The first: given."""
    a = finished(t, scripts)
    shown = a.press(REF + "Pritchard", {G + "ReportUnknown": [1], BRIEF_HUB: [3]})
    t.assertEqual(shown, ["ReportUnknown", BRIEF_HUB])
    t.assertEqual(a.g("Reported"), 0)
    shown = a.press(REF + "Pritchard", {G + "ReportUnknown": [0], BRIEF_HUB: [3]})
    t.assertEqual(shown, ["ReportUnknown", "ReportReduced", "ReportEndUnknown"])
    t.assertEqual(a.g("Reported"), 1)
    # Reported: nothing more is offered, and the briefing is his conversation again.
    t.assertEqual(a.press(REF + "Pritchard", {BRIEF_HUB: [3]}), [BRIEF_HUB])


class Report(unittest.TestCase):
    """Finding 6. A report that was shown and not validly answered ends the conversation."""

    def setUp(self):
        need_act1_build(self)

    def test_unanswered_it_closes_the_conversation(self):
        report_not_answered_closes(self)

    def test_stale_it_closes_the_conversation(self):
        report_stale_closes(self)

    def test_later_leads_on_and_report_is_given(self):
        report_later_and_given(self)

    def test_with_the_side_quests_report_still_to_make(self):
        a = finished(self, with_ledger=True)
        a.box_returns(G + "ReportUnknown", -1)
        shown = a.press(REF + "Pritchard", {MSG + "PritchardAfterAndMore": [0], BRIEF_HUB: [3]})
        closed(a)
        self.assertEqual(shown, [MSG + "PritchardAfterAndMore", "ReportUnknown"])
        self.assertEqual((a.g("Reported"), a.p.g("TLM_G_SQ01_Outcome")), (0, 0))

    def test_the_two_scripts_use_the_same_four_answers(self):
        walk = (SCRIPTS / "GreenwaterWalk.psc").read_text()
        act1 = (SCRIPTS / "Act1Walk.psc").read_text()
        for name, value in (("NONE", 0), ("GIVEN", 1), ("LATER", 2), ("CLOSED", 3)):
            self.assertIn("int GW_REPORT_%s = %d Const" % (name, value), walk)
            self.assertIn("int RIVER_REPORT_%s = %d Const" % (name, value), act1)
        # Every way out of OfferReport names one of the four.
        body = walk.split("int Function OfferReport(Actor akSheriff)")[1].split("EndFunction")[0]
        returns = re.findall(r"^\s*Return (.*)$", body, re.M)
        self.assertEqual(sorted(set(returns)), ["GW_REPORT_CLOSED", "GW_REPORT_GIVEN", "GW_REPORT_LATER", "GW_REPORT_NONE"])


# ==================================================================== 7. cargo

def escape_begun(t, scripts=SCRIPTS):
    a = Player(t, scripts=scripts)
    a.gangway()
    a.chain("cut")
    a.pilot()
    return a


def cargo_not_seen(t, a, shown, home, what):
    t.assertEqual(shown, ["NoteCargoFailed"], what)
    t.assertEqual((a.g("GrainHome"), a.g("Recovered"), 42 in a.road.done, 100 in a.road.done), (0, 0, False, False), what)
    t.assertEqual((a.on(home), a.on("CargoLashed")), (False, True), what)
    free(t, a, what)


def reduced_cargo_not_seen_then_seen(t, scripts=SCRIPTS):
    for kind, piece in (("enable", "CargoReduced"), ("disable", "CargoLashed")):
        a = escape_begun(t, scripts)
        a.refuse_call(kind, piece, times=1)                        # SEEDED: once
        cargo_not_seen(t, a, a.press(R + "ReturnDock", enter=True), "CargoReduced", "%s of %s refused" % (kind, piece))
        t.assertEqual((a.g("Cargo"), a.g("Outcome"), a.rules.vars["escapepending"], a.rules.vars["returnpending"], a.rules.vars["claim"], a.g("HatcherHunting")),
                      (gw.RV_CARGO_LASHED, 0, True, gw.RV_RETURN_ESCAPE, gw.RV_CHUTE, 0))
        # The chain lock holds: no cards, no share, no fire. And the road is not complete.
        t.assertNotIn("HatcherTable", a.press(R + "Table"))
        t.assertEqual(a.press(R + "FireControl"), ["NoteChainNothing"])
        t.assertFalse(a.s.invoke(ROAD, "CanComplete", []))
        t.assertEqual(a.press(R + "Exit", {G + "AskLeaveUnresolved": [1]}), ["AskLeaveUnresolved"])
        # Again, as the text says: the lever, then the dock.
        t.assertEqual(a.press(R + "Pilot"), ["NoteChuteScene"])
        t.assertEqual(a.press(R + "ReturnDock", enter=True), ["NoteHomePiloted", "RaffertyRan"])
        a.m.reach_dock()
        a.same("the reduced cargo seen at the second try")
        t.assertEqual((a.road.done.count(42), a.on("CargoReduced"), a.on("CargoLashed"), a.g("Recovered")), (1, True, False, 8))
        # A third arrival brings nothing more.
        a.s.walk_to(R + "Arrival")
        t.assertEqual(a.press(R + "ReturnDock", enter=True), [])
        t.assertEqual(a.road.done.count(42), 1)


def whole_cargo_not_seen_then_seen(t, scripts=SCRIPTS):
    a = Player(t, scripts=scripts, charisma=5)
    a.gangway()
    a.table(["deal"], judge="release")
    a.pilot()
    a.refuse_call("enable", "CargoWhole", times=1)                 # SEEDED: once
    cargo_not_seen(t, a, a.press(R + "ReturnDock", enter=True), "CargoWhole", "the whole cargo's piece refused")
    t.assertEqual((a.g("Cargo"), a.rules.vars["returnpending"]), (gw.RV_CARGO_YIELDED, gw.RV_RETURN_TOW))
    t.assertFalse(a.s.invoke(ROAD, "CanComplete", []))
    t.assertEqual(a.press(R + "Exit", {G + "AskLeaveUnresolved": [0]}), ["AskLeaveUnresolved", "NoteLeftUnresolved"])
    t.assertNotIn(100, a.road.done)
    # Back, and to the dock again without the lever: the return is still pending.
    a.press(R + "MercyTravel", {G + "AskTravel": [0]})
    t.assertEqual(a.press(R + "ReturnDock", enter=True), ["NoteHomeWhole"])
    t.assertEqual((a.g("Cargo"), a.g("GrainHome"), a.g("Recovered"), a.on("CargoWhole"), a.on("CargoLashed")), (gw.RV_CARGO_HOME_WHOLE, 1, 12, True, False))
    t.assertEqual(a.press(R + "Exit", {G + "AskLeaveResolved": [0]}), ["AskLeaveResolved", "NoteRoadComplete"])
    t.assertEqual(a.road.done.count(100), 1)


def cargo_piece_missing(t, scripts=SCRIPTS):
    a = escape_begun(t, scripts)
    a.alias("CargoReduced").ref = None                             # SEEDED
    t.assertEqual(a.press(R + "ReturnDock", enter=True), ["NoteCargoStuck"])
    t.assertEqual((a.g("Cargo"), a.g("GrainHome"), 42 in a.road.done, a.rules.vars["escapepending"], a.rules.vars["returnpending"], a.on("CargoLashed")),
                  (gw.RV_CARGO_LASHED, 0, False, True, gw.RV_RETURN_ESCAPE, True))
    t.assertFalse(a.s.invoke(ROAD, "CanComplete", []))


def the_road_records_no_cargo_it_does_not_see(t, scripts=SCRIPTS):
    """The rule itself, asked directly: no piece, the piece off, the cargo still lashed, or another kind of
    return than the one pending: nothing."""
    a = escape_begun(t, scripts)
    home, lashed, whole = a.s.placed[R + "CargoReduced"], a.s.placed[R + "CargoLashed"], a.s.placed[R + "CargoWhole"]
    for args in ([1, None, None], [1, home, lashed], [1, home, None]):
        t.assertEqual(a.s.invoke(ROAD, "CompleteReturn", args), 0)
    home.disabled = False                                          # SEEDED
    t.assertEqual(a.s.invoke(ROAD, "CompleteReturn", [1, home, lashed]), 0, "recorded with the cargo still lashed")
    lashed.disabled = True
    whole.disabled = False
    t.assertEqual(a.s.invoke(ROAD, "CompleteReturn", [2, whole, lashed]), 0, "a tow recorded for an escape")
    t.assertEqual((a.g("Cargo"), 42 in a.road.done, a.rules.vars["escapepending"]), (gw.RV_CARGO_LASHED, False, True))
    t.assertEqual(a.s.invoke(ROAD, "CompleteReturn", [1, home, lashed]), 1)
    t.assertEqual(a.s.invoke(ROAD, "CompleteReturn", [1, home, lashed]), 0)
    t.assertEqual(a.road.done.count(42), 1)


class Cargo(unittest.TestCase):
    """Finding 7. Nothing is home that is not seen at the landing."""

    def setUp(self):
        need_act1_build(self)

    def test_the_reduced_cargo_not_seen_then_seen(self):
        reduced_cargo_not_seen_then_seen(self)

    def test_the_whole_cargo_not_seen_then_seen_and_no_completion_before(self):
        whole_cargo_not_seen_then_seen(self)

    def test_a_missing_piece_says_so(self):
        cargo_piece_missing(self)

    def test_the_road_records_no_cargo_it_does_not_see(self):
        the_road_records_no_cargo_it_does_not_see(self)


# ============================================ found while writing these probes

def the_crew_is_roused_once(t, scripts=SCRIPTS):
    """Hatcher is killed by the player. Each of his crew who lives is set on the player once, not once for
    every combat event that setting them on raises."""
    a = Player(t, scripts=scripts)
    a.gangway()
    a.kill("hatcher", by_player=True)
    a.p.pause(1.0)
    crew = sorted([a.s._whom(a.who["crew1"]), a.s._whom(a.who["crew2"])])
    # Looked at early as well as late: if the starts were multiplying, waiting longer would never end.
    t.assertEqual(sorted(c[1] for c in a.calls if c[0] == "startcombat"), crew, "who was set on the player, and how often, soon after")
    a.p.pause(20.0)
    t.assertEqual(sorted(c[1] for c in a.calls if c[0] == "startcombat"), crew, "who was set on the player, and how often")
    t.assertTrue(a.who["crew1"].combat_target is a.s.player and a.who["crew2"].combat_target is a.s.player)
    t.assertIsNone(a.who["opal"].combat_target)
    t.assertLess(len(a.s.threads) + len(a.s.pending), 50, "combat events are still multiplying twenty seconds later")


class Crew(unittest.TestCase):
    """Not one of the review's findings: found here, when a probe that kills Hatcher late would not end.
    FightBack started a fight again for people already fighting, from every combat event, and every start
    raises such an event on the stand-in. Whether the game raises one for a fight already under way is not
    known; the script no longer depends on it."""

    def setUp(self):
        need_act1_build(self)

    def test_each_of_the_crew_is_set_on_the_player_once(self):
        the_crew_is_roused_once(self)

    def test_attacking_one_brings_the_others_once(self):
        a = Player(self)
        a.gangway()
        a.s.n_actor_startcombat(a.who["crew1"], None, a.s.player)   # SEEDED: the player attacks one of the crew
        a.p.pause(20.0)
        starts = sorted(c[1] for c in a.calls if c[0] == "startcombat")
        self.assertEqual(starts, sorted(a.s._whom(a.who[w]) for w in ("crew1", "crew2", "hatcher")))
        self.assertIsNone(a.who["opal"].combat_target)


# ====================================================== what these probes catch

class WhatTheRepairProbesCatch(unittest.TestCase):
    """Each repair taken out again, one at a time. The probe written for it must then fail."""

    def setUp(self):
        need_act1_build(self)

    def caught(self, probe, file_name, old, new, also=None):
        """What the probe says of the scripts with that one piece changed (and, with `also`, a second piece of
        another script: where the walk and the road each keep a guard, both have to go for the fault to show)."""
        scripts = changed_scripts(file_name, old, new)
        if also:
            for change in (also if isinstance(also,list) else [also]):
                path = scripts / change[0]
                text = path.read_text()
                if text.count(change[1]) != 1:
                    raise AssertionError("%s: %r is there %d times" % (change[0], change[1], text.count(change[1])))
                path.write_text(text.replace(change[1], change[2]))
        try:
            probe(self, scripts)
        except (AssertionError, SimError) as e:
            return str(e) or "failed"
        return None

    def test_the_probes_pass_on_the_scripts_as_they_are(self):
        skiff_not_confirmed(self)

    def test_the_skiffs_answer_ignored(self):
        self.assertIsNotNone(self.caught(skiff_not_confirmed, "GreenwaterWalk.psc",
                                         "	If ShowBox(NoteSkiffScene) != 0\n		Return\n	EndIf\n", "	ShowBox(NoteSkiffScene)\n"))

    def test_the_skiff_not_asked_again_after_its_notice(self):
        self.assertIsNotNone(self.caught(skiff_after_something_changed, "GreenwaterWalk.psc",
                                         "	If !player || !side || !akRiver.RoadOpen() || akRiver.Stamp() != stamp\n", "	If !player || !side\n"))

    def test_the_levers_answer_ignored(self):
        self.assertIsNotNone(self.caught(lever_not_confirmed, "GreenwaterWalk.psc",
                                         "		pick = ShowBox(NoteTowScene)\n	EndIf\n	If pick != 0\n		Return\n	EndIf\n", "		pick = ShowBox(NoteTowScene)\n	EndIf\n"))

    def test_the_return_begun_before_its_notice(self):
        self.assertIsNotNone(self.caught(lever_not_confirmed, "GreenwaterWalk.psc",
                                         "	int stamp = akRiver.Stamp()\n	int pick = -1\n	If kind == RV_RETURN_ESCAPE\n",
                                         "	akRiver.BeginReturn(kind)\n	int stamp = akRiver.Stamp()\n	int pick = -1\n	If kind == RV_RETURN_ESCAPE\n"))

    def test_the_lever_not_asked_again_after_its_notice(self):
        self.assertIsNotNone(self.caught(lever_after_something_changed, "GreenwaterWalk.psc",
                                         "	If !player || !chute || !akRiver.RoadOpen() || akRiver.Stamp() != stamp\n", "	If !player || !chute\n"))

    def test_the_crew_roused_again_by_every_combat_event(self):
        self.assertIsNotNone(self.caught(the_crew_is_roused_once, "GreenwaterWalk.psc",
                                         "	If who && !who.IsDead() && !who.IsDisabled() && !who.IsInCombat()\n		who.StartCombat(akTarget)\n",
                                         "	If who && !who.IsDead() && !who.IsDisabled()\n		who.StartCombat(akTarget)\n"))

    def test_killed_without_a_ring(self):
        # Current independent guards must all go before a disabled ring permits
        # a real kill. Original missing-ring cases remain frozen historically.
        def probe(t,scripts=SCRIPTS):
            a=beaten(t,scripts);a.s.placed[R+'Steeple'].disabled=True
            choose_hanging(a);t.assertFalse(a.who['hatcher'].dead);t.assertNotIn(60,a.road.done)
        probe(self)
        self.assertIsNotNone(self.caught(probe, "MQ02BQuest.psc",
            "\tIf !ring || ring.IsDisabled()\n", "\tIf false\n",
            also=('MQ02BQuest.psc',' || akRing.IsDisabled()\n','\n')))

    def test_killed_where_he_stood(self):
        for probe in (not_at_the_ring_no_kill, somebody_gone_before_the_kill):
            self.assertIsNotNone(self.caught(probe, "MQ02BQuest.psc", "	If !there || !still\n		HangIntent = RV_HANG_NONE\n", "	If false\n		HangIntent = RV_HANG_NONE\n"))

    def test_a_fighting_man_judged(self):
        # The original pre-question mutant is also exercised unchanged on the
        # accepted Git export. This current probe covers the added local page.
        def probe(t, scripts=SCRIPTS):
            a = beaten(t, scripts)
            while_open(a, "ConfirmHang", lambda: setattr(a.who["hatcher"], "combat_target", a.who["crew1"]))
            shown = choose_hanging(a)
            t.assertEqual(shown, ["HatcherTable", "CardStakes", "HatcherLost", "ConfirmHang"])
            not_hanged(t, a)
        probe(self)
        old = '\tIf confirmed != 0 || !LocalSpeaker(akSpeaker, akSpeakerAlias) || !akRiver.JudgmentContext(aiVerdict, akHatcher, akRecipient, akRing, akSpeaker, akSpeakerAlias, aiStamp)\n'
        self.assertIsNotNone(self.caught(probe, "GreenwaterWalk.psc", old,
            '\tIf confirmed != 0\n',also=[
                ('MQ02BQuest.psc',' || !HatcherCanBeJudged()\n','\n'),
                ('MQ02BQuest.psc','\tIf akHatcher.IsDead() || akHatcher.IsDisabled() || akHatcher.IsInCombat() || akSpeaker.IsDead() || akSpeaker.IsDisabled() || akSpeaker.IsInCombat()\n',
                 '\tIf akHatcher.IsDead() || akHatcher.IsDisabled() || akSpeaker.IsDead() || akSpeaker.IsDisabled()\n')]))

    def test_a_death_looked_for_once(self):
        self.assertIsNotNone(self.caught(the_death_comes_late, "MQ02BQuest.psc", "int RV_DEATH_POLLS = 30 Const", "int RV_DEATH_POLLS = 0 Const"))

    def test_any_later_death_taken_for_the_hanging(self):
        old = "		If HangIntent == RV_HANG_EXECUTING\n			HangIntent = RV_HANG_NONE\n		EndIf\n"
        for probe in (the_kill_refused, the_death_comes_after_the_wait):
            self.assertIsNotNone(self.caught(probe, "MQ02BQuest.psc", old, ""))

    def test_the_firebox_switched_off_while_the_fire_is_only_ordered(self):
        self.assertIsNotNone(self.caught(fire_not_seen_then_tried_again, "GreenwaterWalk.psc",
                                         "	int course = river.Outcome()\n	If course == RV_FIRE\n", "	int course = river.Outcome()\n	If course == RV_FIRE || river.IsBurning()\n"))

    def test_a_fire_recorded_unseen(self):
        # The walk looks, and the road looks again itself. With the road's look gone a direct call records a fire
        # nobody saw; with both gone, so does using the firebox.
        rule = ("MQ02BQuest.psc", "	If !akBurnt || akBurnt.IsDisabled()\n", "	If !akBurnt\n")
        self.assertIsNotNone(self.caught(the_road_records_no_fire_it_does_not_see, *rule))
        self.assertIsNotNone(self.caught(fire_not_seen_then_tried_again, "GreenwaterWalk.psc",
                                         "	bool done = false\n	If Seen(marker, lashed)\n		done = akRiver.FireDone(marker, lashed)\n	EndIf\n",
                                         "	bool done = akRiver.FireDone(marker, lashed)\n", also=rule))

    def test_a_fire_ordered_with_no_marker(self):
        self.assertIsNotNone(self.caught(no_marker_no_order, "GreenwaterWalk.psc",
                                         "	If !Piece(Alias_Burnt)\n		Debug.Trace(\"TLM_GW: the burned Queen's marker is not placed; no fire is ordered\", 2)\n",
                                         "	If false\n		Debug.Trace(\"TLM_GW: the burned Queen's marker is not placed; no fire is ordered\", 2)\n"))

    def test_the_second_half_of_his_admission_from_a_dead_man(self):
        old = ("			If !akRiver.RoadOpen() || !akRiver.HatcherAtTable() || !akRiver.Unsettled()\n				Return\n			EndIf\n"
               "			If ShowBox(SayHatcherPaidB) != 0\n")
        self.assertIsNotNone(self.caught(admission_interrupted, "GreenwaterWalk.psc", old, "			If ShowBox(SayHatcherPaidB) != 0\n"))
        self.assertIsNotNone(self.caught(admission_interrupted, "MQ02BQuest.psc",
                                         "		If !HatcherAtTable()\n			Return false\n		EndIf\n		HireHeard = true\n", "		HireHeard = true\n"))

    def test_the_lie_delivered_not_kept(self):
        self.assertIsNotNone(self.caught(the_lie_delivered_is_kept, "MQ02BQuest.psc",
                                         "		LieTold = true\n		TLM_G_MQ02B_GrainSold.SetValueInt(1)\n", "		LieTold = true\n"))

    def test_her_thanks_from_a_dead_woman(self):
        # Both independent boundaries must be removed for the old bad reply
        # commit to return. The original single mutation remains historical.
        self.assertIsNotNone(self.caught(the_lie_delivered_is_kept, "MQ02BQuest.psc",
                                         "\tIf !RoadOpen() || !LieTold || !CanSpeak(Alias_Opal)\n", "\tIf !RoadOpen() || !LieTold\n",
                                         also=("GreenwaterWalk.psc", "\tIf LocalSpeaker(opal, Alias_Opal) && akRiver.LieWasHeard()\n", "\tIf akRiver.LieWasHeard()\n")))

    def test_her_question_answered_after_her(self):
        old = ("	; Her question is answered to her: alive, present and in no fight after it as before it.\n"
               "	If !akRiver.RoadOpen() || !akRiver.OpalCanSpeak()\n		Return\n	EndIf\n")
        old += "\tIf !LocalSpeaker(opal, Alias_Opal)\n\t\tReturn\n\tEndIf\n"
        self.assertIsNotNone(self.caught(her_question_answered_to_her, "GreenwaterWalk.psc", old, "",
                                         also=("GreenwaterWalk.psc", "\tIf !LocalSpeaker(akSpeaker, akSpeakerAlias) || !akRiver.JudgmentContext(aiVerdict, akHatcher, akRecipient, akRing, akSpeaker, akSpeakerAlias, aiStamp)\n", "\tIf false\n")))

    def test_a_report_not_answered_falling_through(self):
        self.assertIsNotNone(self.caught(report_not_answered_closes, "GreenwaterWalk.psc",
                                         "	If pick != 0\n		Return GW_REPORT_CLOSED\n	EndIf\n	If !river.GiveReport()\n",
                                         "	If pick != 0\n		Return GW_REPORT_LATER\n	EndIf\n	If !river.GiveReport()\n"))
        self.assertIsNotNone(self.caught(report_not_answered_closes, "Act1Walk.psc",
                                         "	If river == RIVER_REPORT_GIVEN || river == RIVER_REPORT_CLOSED\n", "	If river == RIVER_REPORT_GIVEN\n"))

    def test_a_stale_report_going_on(self):
        old = ("	If akSheriff.IsDead() || akSheriff.IsDisabled() || akSheriff.IsInCombat() || player.IsDead()\n"
               "		Return GW_REPORT_CLOSED\n	EndIf\n")
        self.assertIsNotNone(self.caught(report_stale_closes, "GreenwaterWalk.psc", old, ""))

    def test_cargo_recorded_unseen(self):
        rule = ("MQ02BQuest.psc", "	If !akHome || akHome.IsDisabled()\n", "	If !akHome\n")
        self.assertIsNotNone(self.caught(the_road_records_no_cargo_it_does_not_see, *rule))
        walk = ("	int arrived = RV_RETURN_NONE\n	If Seen(home, lashed)\n		arrived = akRiver.CompleteReturn(kind, home, lashed)\n	EndIf\n",
                "	int arrived = akRiver.CompleteReturn(kind, home, lashed)\n")
        for probe in (reduced_cargo_not_seen_then_seen, whole_cargo_not_seen_then_seen):
            self.assertIsNotNone(self.caught(probe, "GreenwaterWalk.psc", walk[0], walk[1], also=rule))
        # The cargo still lashed and the home piece on: the road's second look.
        self.assertIsNotNone(self.caught(the_road_records_no_cargo_it_does_not_see, "MQ02BQuest.psc",
                                         "		If !akLashed.IsDisabled()\n			Debug.Trace(\"TLM_MQ02B: the return is not recorded: the cargo is still seen lashed",
                                         "		If false\n			Debug.Trace(\"TLM_MQ02B: the return is not recorded: the cargo is still seen lashed"))

if __name__ == "__main__":
    unittest.main()
