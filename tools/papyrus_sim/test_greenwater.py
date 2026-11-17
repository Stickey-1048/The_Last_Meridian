"""The Greenwater road, TLM_MQ02B "The Queen of Tellico" (GREENWATER-STORY-001),
on the stand-in engine.

The real scripts (TLM:Act1Walk, TLM:MQ02BQuest, TLM:GreenwaterWalk,
TLM:GreenwaterTalk) are played as greenwater_player.py describes, against
tools/logic_model/greenwater_model.py, on the plugin as built against the
stand-in master.

What is played for real: the first section to its end, the travel point, the
walk onto the landing and into each box, every conversation and piece, each
of the four courses through to the skiff home, and the report to Pritchard.

What is SEEDED, and says so where it is done: somebody dead, or dying or in a
fight while a box is open; a box that comes back with no answer; the game not
honouring a request for caps, the letter or food; a quest that will not
start. The stand-in keeps no save: a script's variables stay as they are,
which is what a save does, and OnPlayerLoadGame is sent as the game sends it.

The stand-in's rules these tests lean on, beyond those test_mercy_briefing.py
lists: [seen] the player moved by script into a box enters it; an actor moved
by script is where it was sent. [assumed] walking into a box sets it off for
a script of this plugin's on its alias as it does for the game's own; that
Kill by script kills an actor no alias protects; that StartCombat by script
starts a fight; that an actor value read for the player is the number a test
gives (the order says a fresh character has seven 4s; nobody measured it
here).

NONE OF THIS HAS BEEN SEEN IN THE GAME. Not a compile and not a game test.
"""
import re
import unittest
from unittest.mock import patch

from sim import SimError
from test_sim import PLUGIN, SCRIPTS
from test_act1 import BRIEF_HANDOFF, BRIEF_HUB, MSG, REF, Person, changed_plugin, changed_scripts, need_act1_build
from greenwater_player import G, R, ROAD, STAGE, Player, gw, snapshot

import json


class GettingThere(unittest.TestCase):
    def setUp(self):
        need_act1_build(self)

    def test_the_travel_point_is_on_from_set_up_and_nothing_else_is(self):
        a = Player(self, travel=False, finish=False)
        self.assertTrue(a.stage.running)
        self.assertFalse(a.road.running)
        self.assertTrue(a.on("MercyTravel"))
        self.assertTrue(a.on("ReliefSupply"))  # separate gated service; no relief initialized yet
        self.assertFalse(a.s.quests['TLM_GW_Relief'].scripts[0].vars['initialized'])
        for name, ref in a.s.placed.items():
            if name.startswith(R) and name not in (R + "MercyTravel", R + "ReliefSupply"):
                self.assertTrue(ref.disabled, name)

    def test_no_travel_before_the_chapter_is_over(self):
        a = Player(self, travel=False, finish=False)
        a.m.main_over = False
        a.travel()
        self.assertFalse(a.road.running)
        self.assertTrue(a.s.placed[R + "Opal"].disabled)
        # With the dispatch carried and not handed over, the same.
        a.p.press("Dispatch", events=["take_dispatch"])
        a.before = a.world()
        a.travel()
        self.assertFalse(a.road.running)

    def test_declining_sets_nothing_up_and_moves_nobody(self):
        a = Player(self, travel=False)
        a.travel(go=False)
        self.assertEqual((a.road.running, a.s.placed[R + "Opal"].disabled), (False, True))
        self.assertTrue(a.player_at(R + "MercyTravel", 100.0))

    def test_travelling_sets_the_zones_up_and_casts_the_road(self):
        a = Player(self, travel=False)
        a.travel()
        self.assertTrue(a.road.running)
        self.assertEqual(a.road.done, [])                          # the travel point is not the landing
        self.assertTrue(a.player_at(R + "Arrival", 10.0))
        cast = {al.name: al.ref for al in a.road.aliases.values()}
        self.assertEqual(sorted(cast), sorted(["Opal", "Hatcher", "Rafferty", "Belden", "Crew1", "Crew2", "Steeple", "Table", "Strongbox", "Pilot", "Exit"]))
        for name, ref in cast.items():
            self.assertIs(ref, a.s.placed[R + name], name)
        off = {"Belden", "CargoWhole", "CargoReduced", "Burnt"}
        for name, ref in a.s.placed.items():
            if name.startswith(R):
                self.assertEqual(ref.disabled, name[len(R):] in off, name)
        a.step_onto_landing()
        self.assertEqual(a.road.done, [10])

    def test_a_piece_used_before_the_landing_does_nothing_and_the_way_back_is_open(self):
        a = Player(self, travel=False)
        a.travel()
        self.assertEqual(a.press(R + "Table"), [])
        self.assertEqual(a.press(R + "Chain"), [])
        self.assertEqual(a.road.done, [])
        a.leave()
        self.assertTrue(a.player_at(R + "MercyReturn", 10.0))
        self.assertEqual(a.road.done, [])

    def test_the_first_section_and_the_briefing_are_as_they_were(self):
        a = Player(self)
        a.opal(first="wants")
        a.gangway()
        a.chain("cut")
        a.pilot()
        a.dock()
        a.leave()
        a.p.same("after the whole road")                           # TLM_MQ01 and TLM_SQ01 against their own model
        self.assertEqual(a.world(), a.before)


class TheFourCourses(unittest.TestCase):
    """Each course from the landing to Pritchard's desk, and what it leaves in the world."""

    def setUp(self):
        need_act1_build(self)

    def test_cut_and_run(self):
        a = Player(self)
        a.opal(first="guns")
        a.opal(first="wants")
        a.rafferty("confess")
        a.rafferty("offside")
        self.assertTrue(a.player_at(R + "OffSideArrival", 10.0))
        self.assertTrue(a.near("rafferty", "OffSideArrival"))     # he rowed
        self.assertNotIn(30, a.road.done)                          # set down beside her is not aboard her
        a.offside()
        self.assertEqual(a.rules.vars["approach"], gw.BOARD_OFFSIDE)
        a.chain("cut")
        self.assertEqual((a.g("Outcome"), a.g("Cargo"), a.on("CargoLashed")), (0, gw.RV_CARGO_LASHED, True))
        a.pilot()
        self.assertTrue(a.player_at(R + "ChuteStart", 10.0))
        self.assertNotIn(42, a.road.done)                          # the lever is not the run
        a.dock()
        self.assertEqual((a.g("Outcome"), a.g("Recovered"), a.g("GrainHome"), a.g("HatcherHunting")), (42, 8, 1, 1))
        self.assertEqual((a.on("CargoLashed"), a.on("CargoReduced"), a.on("CargoWhole")), (False, True, False))
        self.assertTrue(a.near("rafferty", "Arrival"))
        self.assertEqual(a.press(R + "CargoReduced"), ["LabelCargoPiloted"])
        a.opal()
        a.leave()
        self.assertTrue(a.road.completed)
        self.assertTrue(a.player_at(R + "MercyReturn", 10.0))
        a.report()
        self.assertEqual((a.g("Reported"), a.g("SilverRiver"), a.count(a.caps) - a.caps_before), (1, 0, 0))

    def test_cards_then_the_barge_home_and_each_judgment(self):
        for judge, fate, stage in (("hang", gw.RV_H_HANGED, 60), ("custody", gw.RV_H_CUSTODY, 61), ("release", gw.RV_H_RELEASED, None)):
            with self.subTest(judge):
                a = Player(self, charisma=5)
                a.opal(first="wants")
                a.rafferty("gangway")
                a.gangway()
                self.assertEqual(a.rules.vars["approach"], gw.BOARD_GANGWAY)
                a.table(["deal"], judge=judge)
                self.assertEqual((a.g("Outcome"), a.g("Cargo"), a.g("GrainHome"), a.g("Hatcher")), (41, gw.RV_CARGO_YIELDED, 0, fate))
                self.assertEqual((a.on("CargoLashed"), a.on("CargoWhole")), (True, False))
                a.opal()                                           # nothing of the barge until the barge is there
                a.leave(go=False)                                  # and no completion on the win alone
                self.assertFalse(a.m.can_complete())
                a.pilot()
                a.dock()
                self.assertEqual((a.g("Cargo"), a.g("Recovered"), a.g("GrainHome")), (gw.RV_CARGO_HOME_WHOLE, 12, 1))
                self.assertEqual((a.on("CargoLashed"), a.on("CargoWhole"), a.on("CargoReduced")), (False, True, False))
                a.opal()
                a.opal()
                hatcher = a.who["hatcher"]
                if judge == "hang":
                    self.assertTrue(hatcher.dead)
                    self.assertTrue(a.near("hatcher", "Steeple", 10.0))
                    self.assertEqual(a.g("HatcherHanged"), 1)
                elif judge == "custody":
                    self.assertFalse(hatcher.dead)
                    self.assertTrue(hatcher.restrained)
                    self.assertIs(hatcher.cell, a.who["sheriff"].cell)
                    self.assertEqual(a.press(R + "Table"), ["NoteHatcherCustody"])
                else:
                    self.assertFalse(hatcher.dead)
                    self.assertEqual((a.g("HatcherFriend"), a.g("HatcherHanged")), (1, 0))
                self.assertEqual(stage in a.road.done if stage else not ({60, 61} & set(a.road.done)), True)
                self.assertEqual(a.g("HatcherHunting"), 0)
                a.leave()
                a.report()

    def test_the_judgment_put_to_opal_once_the_barge_is_home(self):
        for judge in ("hang", "custody", "release"):
            with self.subTest(judge):
                a = Player(self, charisma=5, sheriff=judge != "hang")
                a.opal(first="wants")
                a.gangway()
                if judge == "hang":
                    # With no Pritchard to take him, that is not on the box, and the box has a way to say nothing.
                    self.assertIn(G + "HatcherLostNoSheriff", a.table(["deal"], judge="silent"))
                else:
                    a.win_and_say_nothing()
                self.assertEqual(a.g("Hatcher"), gw.RV_H_FREE)
                a.pilot()
                a.dock()
                a.opal(judge=judge)
                self.assertEqual(a.g("Hatcher"), {"hang": gw.RV_H_HANGED, "custody": gw.RV_H_CUSTODY, "release": gw.RV_H_RELEASED}[judge])
                a.opal()
                a.leave()

    def test_the_share_the_lie_and_her_thanks(self):
        a = Player(self)
        a.opal(first="wants")
        a.gangway()
        a.table(["share"], done=False)
        self.assertEqual(a.count(a.caps) - a.caps_before, 0)
        a.table(["share"])
        self.assertEqual((a.count(a.caps) - a.caps_before, a.g("Outcome"), a.g("Cargo"), a.g("GrainSold")), (200, 44, gw.RV_CARGO_LASHED, 0))
        self.assertEqual(a.road.stages[44]["Log"], "You accepted Hatcher's payment. The grain remains on his barge beside the Queen; Greenwater did not receive it.")
        self.assertTrue(a.on("CargoLashed") and a.on("Belden"))
        a.table()                                                  # the table again: nothing more to sell
        a.opal(lie=False)
        self.assertEqual((a.g("GrainSold"), 46 in a.road.done), (0, False))
        a.opal(lie=True)
        self.assertEqual((a.g("GrainSold"), 46 in a.road.done), (1, True))
        self.assertIn("Opal Starnes thanked you for trying", a.road.stages[46]["Log"])
        a.opal()
        a.belden()
        a.belden()
        self.assertEqual((a.count(a.meal), a.count(a.caps) - a.caps_before), (2, 200))
        a.leave()
        a.report()

    def test_the_share_with_no_lie_told_still_finishes(self):
        a = Player(self)
        a.gangway()
        a.table(["share"])
        a.opal(lie=False)
        a.leave()
        self.assertEqual((a.g("GrainSold"), a.road.completed, 46 in a.road.done), (0, True, False))
        a.report()

    def test_the_fire(self):
        a = Player(self)
        a.opal(first="wants")
        a.gangway()
        a.fire()                                                   # no warning yet: refused
        a.chain("notyet")
        a.chain("burn")
        self.assertEqual((a.g("Outcome"), a.on("Burnt")), (0, False))
        a.fire(confirm=False)
        self.assertEqual((a.g("Outcome"), a.on("Burnt")), (0, False))
        a.fire()
        self.assertEqual((a.g("Outcome"), a.g("Cargo"), a.g("Recovered"), a.g("QueenBurned"), a.g("GrainHome"), a.g("Hatcher")),
                         (43, gw.RV_CARGO_DESTROYED, 0, 1, 0, gw.RV_H_UNACCOUNTED))
        self.assertEqual((a.on("Burnt"), a.on("CargoLashed"), a.on("CargoWhole"), a.on("CargoReduced")), (True, False, False, False))
        for gone in ("Table", "Chain", "Pilot", "FireControl", "Hatcher", "Crew1", "Crew2"):
            self.assertFalse(a.on(gone), gone)
        # Nobody is dead who was not killed, and the evidence is still there to be read.
        self.assertFalse(any(a.who[w].dead for w in ("hatcher", "crew1", "crew2", "opal", "rafferty", "belden")))
        self.assertTrue(a.on("Strongbox") and a.on("Belden"))
        self.assertTrue(a.player_at(R + "Arrival", 10.0))
        a.strongbox()
        a.opal()
        a.rafferty()
        a.belden()
        a.leave()
        a.report()
        self.assertEqual((a.g("Reported"), a.g("SilverRiver")), (1, 1))


class CardsThatFail(unittest.TestCase):
    def setUp(self):
        need_act1_build(self)

    def test_a_lost_hand_takes_nothing_and_leaves_every_other_course(self):
        for course in ("cut", "share", "fire", "again"):
            with self.subTest(course):
                a = Player(self, charisma=4)
                a.gangway()
                carried = dict(a.s.player.inventory)
                a.table(["deal"], then="leave")
                self.assertEqual(dict(a.s.player.inventory), carried)       # the gun, and everything else, is where it was
                self.assertEqual((a.g("Outcome"), a.rules.vars["claim"], 45 in a.road.done), (0, 0, True))
                a.leave(go=False)
                if course == "cut":
                    a.chain("cut")
                    a.pilot()
                    a.dock()
                elif course == "share":
                    a.table(["deal"], then="share")
                elif course == "fire":
                    a.chain("burn")
                    a.fire()
                else:
                    a.table(["deal"], then="leave")                         # the same hand, lost again, once recorded
                    self.assertEqual(a.road.done.count(45), 1)
                    continue
                a.leave()
                self.assertTrue(a.road.completed)

    def test_the_threshold_is_five_and_what_was_read_is_written_down(self):
        for charisma, won in ((4, False), (4.9, False), (5, True), (9, True)):
            a = Player(self, charisma=charisma)
            a.gangway()
            a.table(["deal"], then="leave", judge="release")
            self.assertEqual(41 in a.road.done, won, charisma)
            said = [l for l in a.s.papyrus_log if "card check" in l]
            self.assertEqual(len(said), 1)
            self.assertIn("WON" if won else "LOST", said[0])
            self.assertIn("threshold 5", said[0])
            self.assertIn("current Charisma", said[0])
            self.assertIn("base", said[0])

    def test_current_and_not_base_charisma_is_played(self):
        a = Player(self, charisma=4)
        a.s.player_values["Charisma"] = 5.0                       # SEEDED: something worn or drunk
        a.m.charisma = 5.0
        a.gangway()
        a.table(["deal"], judge="release")
        self.assertIn(41, a.road.done)
        self.assertIn("current Charisma 5", [l for l in a.s.papyrus_log if "card check" in l][0])
        self.assertIn("(base 4", [l for l in a.s.papyrus_log if "card check" in l][0])


class Evidence(unittest.TestCase):
    def setUp(self):
        need_act1_build(self)

    def test_by_the_letter(self):
        a = Player(self)
        a.gangway()
        a.strongbox(read=False)
        self.assertEqual((a.g("SilverRiver"), a.count(a.letter)), (0, 0))
        a.strongbox()
        self.assertEqual((a.g("SilverRiver"), a.count(a.letter), a.rules.vars["hireread"], a.rules.vars["hireheard"]), (1, 1, True, False))
        a.strongbox()
        self.assertEqual((a.count(a.letter), a.asked["letter"]), (1, 1))
        # Knowing it is not carrying it.
        a.s.player.inventory[a.letter] = 0
        a.m.letters = 0
        a.chain("cut")
        a.pilot()
        a.dock()
        a.leave()
        self.assertEqual(a.report()[0], G + "ReportKnown")

    def test_by_his_admission(self):
        a = Player(self)
        a.gangway()
        a.table(["paid", "leave"])
        self.assertEqual((a.g("SilverRiver"), a.count(a.letter), a.rules.vars["hireread"], a.rules.vars["hireheard"]), (1, 0, False, True))

    def test_half_an_admission_is_not_one(self):
        for stale in ("HatcherPaidA", "HatcherPaidB"):
            a = Player(self)
            a.gangway()
            a.box_returns(G + stale, -1)                           # SEEDED
            a.press(R + "Table", {G + "HatcherTable": [2]})
            self.assertEqual((a.g("SilverRiver"), 50 in a.road.done), (0, False), stale)

    def test_not_at_all(self):
        a = Player(self)
        a.gangway()
        a.chain("cut")
        a.pilot()
        a.dock()
        a.leave()
        self.assertEqual(a.report()[0], G + "ReportUnknown")
        self.assertEqual((a.g("SilverRiver"), a.road.completed), (0, True))

    def test_the_ration_board_is_read_and_sets_nothing(self):
        a = Player(self)
        before = snapshot(a)
        pages = a.press(R + "RationBoard")
        self.assertEqual(pages, ["BoardPage%d" % (i + 1) for i in range(len(pages))])
        self.assertGreaterEqual(len(pages), 2)
        self.assertEqual(snapshot(a), before)


class TheCastThatIsNotThere(unittest.TestCase):
    """Each action asks only for the people it needs."""

    def setUp(self):
        need_act1_build(self)

    def test_opal_dead_before_she_was_heard(self):
        a = Player(self)
        a.kill("opal")
        a.before = a.world()
        self.assertEqual(a.press(R + "Opal"), [])
        a.rafferty()                                               # he was not sent by her: his plain line, and no skiff talk
        a.skiff()                                                  # the skiff is there to be used all the same
        a.offside()
        self.assertEqual((a.road.done, a.road.displayed.get(10), a.road.completed_objectives.get(10, False)), ([10, 30], False, False))
        a.chain("cut")
        a.pilot()
        a.dock()
        a.leave()
        self.assertTrue(a.road.completed)
        self.assertEqual([m for m in a.s.messages_shown if m.startswith(G + "Opal")], [])
        self.assertEqual({20, 60} & set(a.road.done), set())

    def test_opal_dead_and_the_other_three_courses(self):
        for course in ("cards", "share", "fire"):
            with self.subTest(course):
                a = Player(self, charisma=5)
                a.kill("opal")
                a.before = a.world()
                a.gangway()
                if course == "cards":
                    shown = a.table(["deal"], judge="custody")
                    # His question about her is not put: the approved prefix only.
                    lost = json.loads(PLUGIN.read_text())
                    text = [m["Text"] for m in lost["Messages"] if m["EditorId"] == G + "HatcherLostNoOpal"][0]
                    self.assertTrue(text.endswith("She's yours, friend, every sack.\""), text)
                    self.assertNotIn("Opal", text)
                    self.assertIn(G + "HatcherLostNoOpal", shown)
                    a.pilot()
                    a.dock()
                elif course == "share":
                    a.table(["share"])
                    self.assertEqual(a.press(R + "Opal"), [])
                    self.assertEqual((a.rules.vars["lietold"], a.g("GrainSold")), (False, 0))
                    a.belden()
                else:
                    a.chain("burn")
                    a.fire()
                a.leave()
                self.assertTrue(a.road.completed)
                self.assertEqual({60, 46} & set(a.road.done), set())
                a.report()

    def test_rafferty_dead_before_boarding(self):
        a = Player(self)
        a.opal(first="wants")
        a.kill("rafferty")
        a.before = a.world()
        self.assertEqual(a.press(R + "Rafferty"), [])
        a.gangway()
        shown = a.chain("cut")
        self.assertIn(G + "AskChain", shown)
        self.assertNotIn(G + "RaffertyChain", shown)
        a.pilot()
        a.dock()
        self.assertEqual((a.g("Recovered"), a.g("Cargo")), (6, gw.RV_CARGO_HOME_REDUCED))
        self.assertEqual(a.press(R + "CargoReduced"), ["LabelCargoAlone"])
        self.assertEqual([m for m in a.s.messages_shown if m.startswith(G + "Rafferty")], [])
        a.opal()
        a.leave()

    def test_rafferty_dead_and_the_fire_is_still_warned_of(self):
        a = Player(self)
        a.kill("rafferty")
        a.before = a.world()
        a.gangway()
        a.fire()                                                   # refused: nobody has said who is aboard
        shown = a.chain("burn")
        text = [m["Text"] for m in json.loads(PLUGIN.read_text())["Messages"] if m["EditorId"] == G + "AskChain"][0]
        self.assertIn("Thirty people are aboard", text)
        self.assertFalse(text.startswith("Mose Rafferty"))
        self.assertIn(G + "AskChain", shown)
        a.fire()
        self.assertEqual(a.g("QueenBurned"), 1)
        self.assertEqual([m for m in a.s.messages_shown if m.startswith(G + "Rafferty")], [])

    def test_hatcher_dead_at_his_table(self):
        a = Player(self, charisma=9)
        a.gangway()
        a.kill("hatcher")                                          # SEEDED: by another hand
        a.before = a.world()
        a.table()
        self.assertEqual((a.g("Outcome"), 40 in a.road.done, a.g("Hatcher")), (0, False, gw.RV_H_DEAD))
        a.strongbox()                                              # his box is open to anybody aboard
        a.chain("cut")
        a.pilot()
        a.dock()
        self.assertEqual((a.g("HatcherHunting"), a.g("Outcome")), (0, 42))
        a.leave()

    def test_hatcher_dead_and_the_fire(self):
        a = Player(self)
        a.gangway()
        a.kill("hatcher")
        a.before = a.world()
        a.chain("burn")
        a.fire()
        self.assertEqual((a.g("Hatcher"), a.g("QueenBurned")), (gw.RV_H_DEAD, 1))   # dead is dead, not "not accounted for"
        self.assertTrue(a.on("Hatcher"))                                              # and his body is where it fell

    def test_hatcher_dead_after_the_barge_was_won(self):
        a = Player(self, charisma=5)
        a.opal(first="wants")
        a.gangway()
        a.win_and_say_nothing()
        a.kill("hatcher")
        a.before = a.world()
        a.pilot()
        a.dock()
        shown = a.opal()
        self.assertEqual(shown, [G + "OpalWonHatcherDead"])
        self.assertEqual({60, 61} & set(a.road.done), set())
        self.assertEqual((a.g("Hatcher"), a.g("HatcherHanged")), (gw.RV_H_DEAD, 0))
        a.leave()

    def test_belden_dead_feeds_nobody_and_blocks_nothing(self):
        a = Player(self)
        a.kill("belden")
        a.before = a.world()
        a.gangway()
        a.table(["share"])
        self.assertFalse(a.on("Belden"))                           # no wagon comes, and nobody is there to be spoken to
        a.leave()
        self.assertEqual((a.road.completed, a.count(a.meal)), (True, 0))

    def test_no_pritchard_no_custody(self):
        a = Player(self, charisma=5, sheriff=False)
        a.opal(first="wants")
        a.gangway()
        shown = a.table(["deal"], judge="silent")
        self.assertIn(G + "HatcherLostNoSheriff", shown)
        self.assertEqual(a.g("Hatcher"), gw.RV_H_FREE)
        a.pilot()
        a.dock()
        self.assertEqual(a.opal(judge="release"), [G + "OpalAfterWonNoSheriff", G + "ConfirmRelease", G + "OpalDenied"])
        a.leave()
        self.assertTrue(a.road.completed)
        self.assertEqual(a.press(REF + "Pritchard"), [])           # a dead man hears no report
        self.assertEqual(a.g("Reported"), 0)

    def test_nobody_but_hatcher_left(self):
        a = Player(self, charisma=5, sheriff=False)
        a.kill("opal")
        a.kill("rafferty")
        a.kill("belden")
        a.before = a.world()
        a.gangway()
        shown = a.table(["deal"], judge="silent")
        self.assertIn(G + "HatcherLostAlone", shown)
        a.table(judge="release")
        a.pilot()
        a.dock()
        a.leave()
        self.assertEqual((a.road.completed, a.g("Cargo"), a.g("HatcherFriend")), (True, gw.RV_CARGO_HOME_WHOLE, 1))


class SomebodyChangesWhileABoxIsOpen(unittest.TestCase):
    """SEEDED while the box is open. What was chosen is not carried out on somebody who is no longer there."""

    def setUp(self):
        need_act1_build(self)

    def dies(self, a, who, box):
        def meanwhile(message):
            if message == G + box:
                a.who[who].dead = True
        return meanwhile

    def test_hatcher_dies_while_his_share_is_on_the_table(self):
        a = Player(self)
        a.gangway()
        a.s.on_box = self.dies(a, "hatcher", "HatcherShare")
        a.press(R + "Table", {G + "HatcherTable": [1], G + "HatcherShare": [0]})
        a.s.on_box = None
        self.assertEqual((a.count(a.caps) - a.caps_before, a.asked["caps"], a.g("Outcome"), a.rules.vars["claim"]), (0, 0, 0, 0))

    def test_hatcher_dies_while_the_cards_are_offered(self):
        a = Player(self, charisma=9)
        a.gangway()
        a.s.on_box = self.dies(a, "hatcher", "HatcherTable")
        a.press(R + "Table", {G + "HatcherTable": [0]})
        a.s.on_box = None
        self.assertEqual((a.g("Outcome"), 41 in a.road.done, a.g("Cargo")), (0, False, gw.RV_CARGO_LASHED))

    def test_opal_dies_while_he_asks_whether_she_is_to_have_him(self):
        a = Player(self, charisma=5)
        a.gangway()
        a.s.on_box = self.dies(a, "opal", "HatcherLost")
        shown = a.press(R + "Table", {G + "HatcherTable": [0], G + "HatcherLost": [0]})
        a.s.on_box = None
        self.assertEqual(shown[-1], "HatcherLost")  # stale recipient: no confirmation or transfer
        self.assertFalse(a.who["hatcher"].dead)
        self.assertEqual((a.g("Hatcher"), 60 in a.road.done, a.g("HatcherHanged")), (gw.RV_H_FREE, False, 0))

    def test_pritchard_dies_while_custody_is_chosen(self):
        a = Player(self, charisma=5)
        a.gangway()
        a.s.on_box = self.dies(a, "sheriff", "HatcherLost")
        shown = a.press(R + "Table", {G + "HatcherTable": [0], G + "HatcherLost": [1]})
        a.s.on_box = None
        self.assertEqual(shown[-1], "HatcherLost")  # stale recipient: no confirmation or transfer
        self.assertEqual((a.g("Hatcher"), 61 in a.road.done), (gw.RV_H_FREE, False))
        self.assertTrue(a.near("hatcher", "Hatcher", 1.0))        # he was not sent anywhere

    def test_opal_dies_while_the_lie_is_being_chosen(self):
        a = Player(self)
        a.gangway()
        a.table(["share"])
        a.s.on_box = self.dies(a, "opal", "AskLie")
        shown = a.press(R + "Opal", {G + "AskLie": [0]})
        a.s.on_box = None
        self.assertEqual(shown, ["AskLie"])
        self.assertEqual((a.rules.vars["lietold"], a.g("GrainSold"), 46 in a.road.done, a.count(a.meal)), (False, 0, False, 0))

    def test_opal_dies_while_she_is_first_spoken_to(self):
        a = Player(self)
        a.s.on_box = self.dies(a, "opal", "OpalFirst")
        self.assertEqual(a.press(R + "Opal", {G + "OpalFirst": [0]}), ["OpalFirst"])
        a.s.on_box = None
        self.assertNotIn(20, a.road.done)

    def test_somebody_in_a_fight_says_nothing(self):
        a = Player(self)
        for who, piece in (("opal", "Opal"), ("rafferty", "Rafferty")):
            a.who[who].combat_target = a.who["crew1"]              # SEEDED
            self.assertEqual(a.press(R + piece), [], who)
            a.who[who].combat_target = None
        a.gangway()
        a.who["hatcher"].combat_target = a.who["crew1"]
        self.assertEqual(a.press(R + "Table"), ["NoteTableEmpty"])
        self.assertNotIn(40, a.road.done)

    def test_the_player_dead_changes_nothing(self):
        a = Player(self)
        a.gangway()
        a.s.player.dead = True                                     # SEEDED
        before = snapshot(a)
        for piece in ("Table", "Chain", "Pilot", "FireControl", "Strongbox", "Opal"):
            self.assertEqual(a.press(R + piece), [], piece)
        self.assertEqual(snapshot(a), before)


class BoxesThatGiveNoAnswer(unittest.TestCase):
    """SEEDED: a box comes back with -1, or with a number that is none of its buttons. Nothing is settled by it."""

    def setUp(self):
        need_act1_build(self)

    def test_at_every_choice_that_settles_something(self):
        cases = (
            ("AskTravel", lambda a: a.press(R + "MercyTravel"), dict(travel=False)),
            ("HatcherTable", lambda a: a.press(R + "Table"), {}),
            ("HatcherShare", lambda a: a.press(R + "Table", {G + "HatcherTable": [1]}), {}),
            ("HatcherLost", lambda a: a.press(R + "Table", {G + "HatcherTable": [0]}), dict(charisma=5)),
            ("RaffertyChain", lambda a: a.press(R + "Chain"), {}),
            ("AskFire", lambda a: (a.chain("burn"), a.press(R + "FireControl")), {}),
            ("AskLie", lambda a: (a.table(["share"]), a.press(R + "Opal")), {}),
            ("AskLeaveUnresolved", lambda a: a.press(R + "Exit"), {}),
        )
        for box, use, world in cases:
            for value in (-1, 9, 4):
                with self.subTest(box=box, value=value):
                    a = Player(self, **world)
                    if world.get("travel", True):
                        a.gangway()
                    a.box_returns(G + box, value)
                    use(a)
                    v = a.rules.vars
                    if box == "HatcherLost":
                        self.assertEqual((a.g("Outcome"), a.g("Hatcher")), (41, gw.RV_H_FREE))      # the hand was won; nothing was judged
                    elif box == "AskLie":
                        self.assertEqual((v["lietold"], a.g("GrainSold")), (False, 0))
                    elif box == "AskFire":
                        self.assertEqual((v["claim"], a.g("QueenBurned"), a.on("Burnt")), (0, 0, False))
                    elif box == "AskTravel":
                        self.assertFalse(a.road.running)
                    else:
                        self.assertEqual((v["claim"], a.g("Outcome"), a.count(a.caps) - a.caps_before, a.road.completed), (0, 0, 0, False))
                    self.assertFalse(a.walk.vars["talking"])

    def test_the_report_left_for_later_or_not_answered_is_not_given(self):
        a = Player(self)
        a.gangway()
        a.chain("cut")
        a.pilot()
        a.dock()
        a.leave()
        a.report(give=False)
        self.assertEqual(a.g("Reported"), 0)
        for value in (-1, 7):
            a.box_returns(G + "ReportUnknown", value)
            # Shown and not answered: not given, and nothing else is shown in that conversation
            # (test_greenwater_repair.py, Report, has the rest).
            self.assertEqual(a.press(REF + "Pritchard", {BRIEF_HUB: [3]}), ["ReportUnknown"])
            a.box_returns(None, None)
            self.assertEqual(a.g("Reported"), 0)
        a.report()
        self.assertEqual(a.g("Reported"), 1)


class LeavingAndComingBack(unittest.TestCase):
    def setUp(self):
        need_act1_build(self)

    def test_leaving_with_nothing_settled_settles_nothing(self):
        a = Player(self)
        a.opal(first="wants")
        a.gangway()
        a.leave(go=False)
        before = snapshot(a)
        a.leave()
        self.assertEqual(snapshot(a), before)
        self.assertTrue(a.player_at(R + "MercyReturn", 10.0))
        self.assertFalse(a.road.completed)
        a.report()                                                 # nothing to report: the Mercy briefing, as before
        # Back again: what was left is what is found.
        a.travel()
        self.assertEqual(a.facts(), before[0])
        a.table(["leave"])
        a.chain("cut")
        a.pilot()
        a.dock()
        a.leave()
        self.assertTrue(a.road.completed)

    def test_an_escape_pending_goes_with_the_player_and_comes_back(self):
        a = Player(self, charisma=9)
        a.gangway()
        a.chain("burn")                                            # warned of the fire, and then the chain is cut
        a.chain("cut")
        a.leave()
        self.assertFalse(a.road.completed)
        a.s.actor_event(a.s.player, "OnPlayerLoadGame", [], 0)    # as the game sends it on a load
        a.p.pause()
        a.travel()
        self.assertTrue(a.rules.vars["escapepending"])
        # No cut-then-burn, no cards, no share: only the lever.
        a.fire()
        a.table(["deal"])
        a.chain("burn")
        self.assertEqual((a.g("QueenBurned"), a.g("Outcome"), a.count(a.caps) - a.caps_before, a.on("Burnt")), (0, 0, 0, False))
        a.pilot()
        a.dock()
        self.assertEqual((a.g("Outcome"), a.g("QueenBurned")), (42, 0))

    def test_the_run_interrupted_is_begun_again_and_done_once(self):
        a = Player(self)
        a.gangway()
        a.chain("cut")
        a.dock()                                                   # the dock without the lever: nothing
        self.assertNotIn(42, a.road.done)
        a.pilot()
        a.leave()                                                  # walked off the Chute and went home
        self.assertFalse(a.road.completed)
        a.travel()
        a.dock()                                                   # the lever was used before leaving: reaching the dock still counts
        self.assertIn(42, a.road.done)
        a.pilot()                                                  # and the lever now moves nothing
        a.dock()
        self.assertEqual((a.road.done.count(42), a.g("Recovered")), (1, 8))

    def test_coming_back_after_the_road_is_complete_changes_no_outcome(self):
        a = Player(self, charisma=5)
        a.opal(first="wants")
        a.gangway()
        a.table(["deal"], judge="release")
        a.pilot()
        a.dock()
        a.leave()
        a.report()
        outcome = (a.g("Outcome"), a.g("Cargo"), a.g("Recovered"), a.g("Hatcher"))
        a.travel()
        a.chain("cut")
        a.fire()
        a.table(["share"])
        a.pilot()
        a.dock()
        a.strongbox()                                              # the letter can still be read
        a.opal()
        a.leave()
        self.assertEqual((a.g("Outcome"), a.g("Cargo"), a.g("Recovered"), a.g("Hatcher")), outcome)
        self.assertEqual((a.road.done.count(100), a.g("SilverRiver"), a.count(a.caps) - a.caps_before), (1, 1, 0))
        a.report()                                                 # reported once

    def test_the_load_event_changes_nothing(self):
        for build in ("share", "pending"):
            a = Player(self)
            a.gangway()
            if build == "share":
                a.table(["share"])
            else:
                a.chain("cut")
                a.pilot()
            before = snapshot(a)
            a.s.actor_event(a.s.player, "OnPlayerLoadGame", [], 0)
            a.p.pause()
            self.assertEqual(snapshot(a), before, build)


class OnceAndOnlyOnce(unittest.TestCase):
    def setUp(self):
        need_act1_build(self)

    def test_the_share_is_paid_once_however_it_is_asked_for(self):
        a = Player(self)
        a.gangway()
        a.table(["share"])
        for _ in range(3):
            a.table(["share"])
            a.rules_take = a.s.invoke(ROAD, "TakeShare", [])
            self.assertFalse(a.rules_take)
        self.assertEqual((a.count(a.caps) - a.caps_before, a.asked["caps"]), (200, 1))

    def test_a_second_use_while_a_box_is_open_does_nothing(self):
        a = Player(self)
        a.gangway()
        extra = []

        def meanwhile(message):
            # While each box is open: the table used again, and the firebox, as a second activation would.
            used = a.walk.script.functions["used"]

            def again():
                yield from a.s.call(a.walk, used, [10])
                yield from a.s.call(a.walk, used, [14])
                extra.append(message)
            a.s.spawn(again(), "a second use while %s is open" % message)
        a.s.on_box = meanwhile
        shown = a.press(R + "Table", {G + "HatcherTable": [1], G + "HatcherShare": [0]})
        a.s.on_box = None
        self.assertEqual(shown, ["HatcherTable", "HatcherShare", "ConfirmShare", "NoteSharePaid"])
        self.assertEqual(extra, [G + "HatcherTable", G + "HatcherShare", G + "ConfirmShare", G + "NoteSharePaid"])
        self.assertEqual((a.count(a.caps) - a.caps_before, a.asked["caps"], a.g("Outcome")), (200, 1, 44))
        self.assertFalse(a.s.invoke(ROAD, "TakeShare", []))        # and asked for directly afterwards: no
        self.assertEqual((a.count(a.caps) - a.caps_before, a.asked["caps"]), (200, 1))

    def test_each_portion_and_the_letter_once(self):
        a = Player(self)
        a.opal(first="bowl")
        a.opal(first="bowl")
        a.gangway()
        a.strongbox()
        a.strongbox()
        a.table(["share"])
        a.belden()
        a.belden()
        a.opal(lie=True)
        a.opal()
        self.assertEqual((a.count(a.meal), a.asked["food"], a.count(a.letter), a.asked["letter"]), (3, 3, 1, 1))

    def test_complete_and_reported_once(self):
        a = Player(self)
        a.gangway()
        a.chain("cut")
        a.pilot()
        a.dock()
        a.leave()
        a.travel()
        a.leave()
        a.report()
        a.report()
        self.assertEqual((a.road.done.count(100), a.g("Reported")), (1, 1))
        self.assertEqual(a.s.messages_shown.count(G + "ReportEndUnknown"), 1)


class WhatTheGameDoesNotHonour(unittest.TestCase):
    """SEEDED: the game is asked for an item and it does not arrive. Nothing is claimed and nothing is asked again."""

    def setUp(self):
        need_act1_build(self)

    def test_the_caps(self):
        a = Player(self, refuse={"caps"})
        a.gangway()
        a.table(["share"])
        self.assertEqual((a.count(a.caps) - a.caps_before, a.g("Outcome"), 44 in a.road.done, a.rules.vars["sharepending"]), (0, 0, False, True))
        said = [l for l in a.s.papyrus_log if "FAIL CLOSED" in l]
        self.assertEqual(len(said), 1)
        self.assertIn("not offered or asked for again", said[0])
        self.assertIn(G + "HatcherTableNoShare", a.table(["leave"]))        # no share on the box any more
        self.assertIn(G + "HatcherWonNoShare", a.table(["deal"], then="leave"))
        self.assertEqual(a.asked["caps"], 1)
        a.chain("cut")                                             # the road is not shut by it
        a.pilot()
        a.dock()
        a.leave()
        self.assertTrue(a.road.completed)

    def test_the_letter(self):
        a = Player(self, refuse={"letter"})
        a.gangway()
        a.strongbox()
        self.assertEqual((a.g("SilverRiver"), a.count(a.letter)), (1, 0))            # what was read is known
        a.strongbox()
        self.assertEqual(a.asked["letter"], 1)

    def test_the_food(self):
        a = Player(self, refuse={"food"})
        a.opal(first="bowl")
        a.opal(first="bowl")
        a.gangway()
        a.table(["share"])
        a.belden()
        a.belden()
        a.opal(lie=True)
        self.assertEqual((a.count(a.meal), a.asked["food"]), (0, 3))
        self.assertEqual(len([l for l in a.s.papyrus_log if "FAIL CLOSED: portion" in l]), 3)
        a.leave()
        self.assertTrue(a.road.completed)

    def test_the_roads_quest_will_not_start(self):
        for does in ((False, False), (True, False), (False, True)):
            a = Player(self, travel=False)
            start = a.s.n_quest_start

            def refuse(quest, context, does=does, start=start):
                if quest.editor_id != ROAD:
                    return start(quest, context)
                if does[1]:
                    a.s.start_quest(quest)
                return does[0]
            a.s.n_quest_start = refuse
            shown = a.press(R + "MercyTravel", {G + "AskTravel": [0]})
            self.assertEqual(shown, ["AskTravel", "NoteTravelFailed"], does)
            self.assertEqual((a.road.done, a.s.placed[R + "Opal"].disabled), ([], True))
            self.assertTrue(a.player_at(R + "MercyTravel", 100.0))
            self.assertEqual(len([l for l in a.s.papyrus_log if "TLM_MQ02B: its quest is not running and could not be started" in l]), 1)


class NothingBound(unittest.TestCase):
    """A build in which the game's records were not found, or a binding is missing."""

    def setUp(self):
        need_act1_build(self)

    def player(self, change, **kw):
        plugin, vanilla = changed_plugin(change)
        with patch("test_act1.PLUGIN", plugin), patch("test_act1.VANILLA", vanilla), patch("greenwater_player.PLUGIN", plugin):
            return Player(self, **kw)

    def without(self, quest, name):
        def change(data):
            script = [q for q in data["Quests"] if q["EditorId"] == quest][0]["Scripts"][0]
            script["Props"] = [p for p in script["Props"] if p["Name"] != name]
        return change

    def test_no_charisma_no_cards(self):
        a = self.player(self.without(ROAD, "Charisma"), charisma=9)
        a.gangway()
        a.table(["deal"])
        self.assertEqual((a.g("Outcome"), 41 in a.road.done, 45 in a.road.done), (0, False, False))
        self.assertTrue(any("the Charisma actor value is not bound" in l for l in a.s.papyrus_log))

    def test_no_caps_no_share_is_offered(self):
        a = self.player(self.without(ROAD, "Caps"))
        a.gangway()
        shown = a.table(["deal"], then="share")
        self.assertIn(G + "HatcherTableNoShare", shown)
        self.assertIn(G + "HatcherWonNoShare", shown)
        self.assertEqual(a.g("Outcome"), 0)

    def test_no_food_and_the_build_says_so(self):
        a = self.player(self.without(ROAD, "Meal"))
        shown = a.opal(first="bowl")
        self.assertEqual(shown[-1], G + "NoteNoMeal")
        a.gangway()
        a.table(["share"])
        self.assertEqual(a.belden()[-1], G + "NoteNoMeal")
        self.assertEqual(a.opal(lie=True)[-1], G + "NoteNoMeal")
        self.assertEqual(a.g("GrainSold"), 1)                      # the lie and her answer stand; only the cup is not there

    def test_the_first_section_without_the_greybox_is_as_it_was(self):
        def unbound(data):
            walk = [q for q in data["Quests"] if q["EditorId"] == "TLM_A1"][0]["Scripts"][0]
            walk["Props"] = [p for p in walk["Props"] if p["Name"] != "TLM_Greenwater"]
        plugin, vanilla = changed_plugin(unbound)
        with patch("test_act1.PLUGIN", plugin), patch("test_act1.VANILLA", vanilla):
            p = Person(self)
        self.assertFalse(p.s.quests[STAGE].running)
        self.assertTrue(p.s.placed[R + "MercyTravel"].disabled)
        p.press("Dispatch", events=["take_dispatch"])
        p.to_town()
        p.hand_over("DebriefMissed")
        p.press("Pritchard", boxes={BRIEF_HUB: [3]})
        self.assertEqual([m for m in p.s.messages_shown if m.startswith(G)], [])


class TheQueensCrew(unittest.TestCase):
    """Two of them, with no names. They fight the player who attacks Hatcher or one of them, and nobody else does."""

    def setUp(self):
        need_act1_build(self)

    def fighting(self, a):
        return sorted(w for w, actor in a.who.items() if actor.combat_target is a.s.player and not actor.dead)

    def test_killing_hatcher_at_his_table_brings_his_crew_and_nobody_else(self):
        a = Player(self)
        a.opal(first="wants")
        a.gangway()
        a.s.n_actor_kill(a.who["hatcher"], None, a.s.player)
        a.p.pause()
        self.assertTrue(a.who["hatcher"].dead)
        self.assertEqual(self.fighting(a), ["crew1", "crew2"])
        self.assertEqual(a.g("Hatcher"), gw.RV_H_DEAD)
        # The barge can still be cut loose, or burned.
        a.m.hatcher = False
        for crew in ("crew1", "crew2"):
            a.s.n_actor_kill(a.who[crew], None, a.s.player)
        a.p.pause(8.0)
        shown = a.press(R + "Chain", {G + "RaffertyChain": [0]})
        self.assertEqual(shown[-1], "NoteChainCut")
        self.assertTrue(a.rules.vars["escapepending"])

    def test_attacking_one_of_the_crew_brings_the_other_and_hatcher(self):
        a = Player(self)
        a.gangway()
        a.who["crew1"].combat_target = a.s.player                  # SEEDED: the player attacked him
        a.s.actor_event(a.who["crew1"], "OnCombatStateChanged", [a.s.player, 1], 0)
        a.p.pause()
        self.assertEqual(self.fighting(a), ["crew1", "crew2", "hatcher"])

    def test_declining_everything_is_not_an_attack(self):
        a = Player(self)
        a.opal(first="wants")
        a.gangway()
        a.table(["deal"], then="leave")
        a.table(["share"], done=False)
        a.table(["leave"])
        a.chain("notyet")
        a.leave()
        self.assertEqual(self.fighting(a), [])
        self.assertFalse(a.s.player_in_combat())

    def test_killing_opal_turns_nobody_on_the_player(self):
        a = Player(self)
        a.kill("opal")
        self.assertEqual(self.fighting(a), [])
        self.assertFalse(a.s.player_in_combat())

    def test_a_hanged_man_has_no_crew_to_call_on(self):
        a = Player(self, charisma=5)
        a.gangway()
        a.table(["deal"], judge="hang")
        self.assertTrue(a.who["hatcher"].dead)
        self.assertEqual(self.fighting(a), [])


class AtMercy(unittest.TestCase):
    """Pritchard keeps one conversation: the side quest's report, the river report, the briefing."""

    def setUp(self):
        need_act1_build(self)

    def finished(self, **kw):
        a = Player(self, **kw)
        a.gangway()
        a.strongbox()
        a.chain("cut")
        a.pilot()
        a.dock()
        a.leave()
        return a

    def test_the_side_quests_report_keeps_its_button(self):
        a = self.finished(with_ledger=True)
        after = MSG + "PritchardAfterAndMore"
        # 1: the side quest's report, and nothing of the river.
        got = a.p.press("Pritchard", {"PritchardAfterAndMore": [1], "PritchardReported": [0]}, ["sq_report"])
        self.assertEqual(got, ["PritchardAfterAndMore", "PritchardReported"])
        self.assertEqual((a.p.g("TLM_G_SQ01_Outcome"), a.g("Reported")), (1, 0))
        # No answer: closed, nothing given.
        b = self.finished(with_ledger=True)
        b.box_returns(after, -1)
        self.assertEqual(b.press(REF + "Pritchard"), [after])
        self.assertEqual(b.g("Reported"), 0)
        b.box_returns(None, None)
        # 0: on to the river report.
        b.report(more=0)
        self.assertEqual((b.g("Reported"), b.p.g("TLM_G_SQ01_Outcome")), (1, 0))

    def test_after_the_report_he_gives_the_briefing_as_before(self):
        a = self.finished()
        a.report()
        shown = a.press(REF + "Pritchard", {BRIEF_HUB: [1], "TLM_MSG_MB_River": [0]})
        self.assertEqual(shown, [BRIEF_HUB, "TLM_MSG_MB_River"])
        self.assertEqual(a.s.quests["TLM_MercyBriefing"].done, [10, 20])

    def test_the_report_says_what_the_road_holds(self):
        a = self.finished()
        shown = a.report()
        self.assertEqual(shown, [G + "ReportKnown", G + "ReportReduced", G + "ReportEndKnown"])
        texts = {m["EditorId"]: m["Text"] for m in json.loads(PLUGIN.read_text())["Messages"]}
        self.assertTrue(texts[G + "ReportEndKnown"].endswith("Greenwater road complete. The other roads and Four Flags entry remain available."))
        self.assertIn("Who paid is not known", texts[G + "ReportEndKnown"])
        self.assertNotIn("fair", texts[G + "ReportKnown"])
        # He is not moved, not put into an alias of the road, and the two earlier quests are as they were.
        self.assertFalse(any(al.ref is a.who["sheriff"] for al in a.road.aliases.values()))
        a.p.same("after the river report")

    def test_availability_text_tells_the_new_truth(self):
        texts = {m["EditorId"]: m["Text"] for m in json.loads(PLUGIN.read_text())["Messages"]}
        stale = ("three destinations", "roads unbuilt", "Destinations are not playable", "Later routes are not playable",
                 "First-section demo complete")
        for name, text in texts.items():
            for phrase in stale:
                self.assertNotIn(phrase, text, name)
        self.assertTrue(texts["TLM_MSG_MB_Hub"].endswith("[Mercy briefing. Three roads and the qualified Four Flags entry are available.]"))
        self.assertTrue(texts["TLM_MSG_MB_HandOff"].endswith("[Opening complete. Ask for briefings or use a story test point.]"))
        self.assertTrue(texts[MSG + "PritchardAfter"].endswith("[Opening complete. Three roads and Four Flags entry are available.]"))
        self.assertIn("Three roads are playable. Four Flags entry is available after the first section.", texts[G + "AskTravel"])
        briefing = [q for q in json.loads(PLUGIN.read_text())["Quests"] if q["EditorId"] == "TLM_MercyBriefing"][0]
        self.assertEqual([s["Log"] for s in briefing["Stages"]],
                         ["Mercy briefing. Three roads and the qualified Four Flags entry are available.",
                          "Mercy briefing complete. Three roads and qualified Four Flags entry remain available."])
        guide = (SCRIPTS / "Act1Guide.psc").read_text()
        self.assertIn("Greenwater, Iron Junction and Red Hollow are available at their story test points. Use the Four Flags entry point to qualify for the camp-ground.", guide)
        self.assertNotIn("are not implemented here", guide)

    def test_scenario_twelve_meets_none_of_it(self):
        from sim import run_scenario
        from test_sim import NATIVES, VANILLA
        s = run_scenario(12, SCRIPTS, PLUGIN, VANILLA, NATIVES)
        self.assertEqual(s.ended, "quit")
        self.assertEqual([m for m in s.messages_shown if m.startswith(G)], [])
        self.assertEqual(s.message_boxes, [])
        self.assertFalse(s.quests[ROAD].running)


class TheNumbers(unittest.TestCase):
    def setUp(self):
        self.data = need_act1_build(self)

    def constants(self, name):
        return {k: int(v) for k, v in re.findall(r"^int (\w+) = (-?\d+) Const", (SCRIPTS / name).read_text(), re.M)}

    def test_the_two_scripts_and_the_model_use_the_same_numbers(self):
        rules, walk = self.constants("MQ02BQuest.psc"), self.constants("GreenwaterWalk.psc")
        for name, value in rules.items():
            if hasattr(gw, name):
                self.assertEqual(value, getattr(gw, name), name)
            if name in walk:
                self.assertEqual(walk[name], value, name)
        for name in ("RV_NONE", "RV_CARDS", "RV_CHUTE", "RV_FIRE", "RV_SHARE", "RV_CARD_THRESHOLD", "RV_UNITS_WHOLE", "RV_UNITS_PILOTED",
                     "RV_UNITS_ALONE", "RV_SHARE_CAPS", "RV_H_UNACCOUNTED", "RV_CARGO_DESTROYED"):
            self.assertEqual(rules[name], getattr(gw, name), name)
        for name in ("BOARD_GANGWAY", "BOARD_OFFSIDE", "BOARD_DECK"):
            self.assertEqual(walk[name], getattr(gw, name), name)

    def test_the_spec_and_the_walk_agree_on_who_is_who(self):
        walk = {k[3:]: v for k, v in self.constants("GreenwaterWalk.psc").items() if k.startswith("GW_")}
        stage = [q for q in self.data["Quests"] if q["EditorId"] == STAGE][0]
        on_aliases = {a["Name"]: s["Props"][0]["Value"] for a in stage["Aliases"] for s in a["Scripts"] if s["Name"] == "TLM:GreenwaterTalk"}
        want = {"MercyTravel": "TRAVEL", "LandingSight": "LANDING", "Opal": "OPAL", "RationBoard": "BOARD", "Rafferty": "RAFFERTY",
                "Skiff": "SKIFF", "GangwaySight": "GANGWAY", "OffSideSight": "OFFSIDE", "Hatcher": "HATCHER", "Table": "TABLE",
                "Strongbox": "STRONGBOX", "Chain": "CHAIN", "Pilot": "PILOT", "FireControl": "FIRE", "ReturnDock": "DOCK", "Exit": "EXIT",
                "Belden": "BELDEN", "Crew1": "CREW1", "Crew2": "CREW2", "LabelLanding": "LABEL_LANDING", "LabelQueen": "LABEL_QUEEN",
                "LabelChute": "LABEL_CHUTE", "CargoLashed": "CARGO", "CargoWhole": "CARGO", "CargoReduced": "CARGO", "Steeple": "STEEPLE",
                "Burnt": "BURNT", "ReliefStores": "RELIEF_STORES", "ReliefSupply": "RELIEF_SUPPLY"}
        self.assertEqual(on_aliases, {alias: walk[who] for alias, who in want.items()})

    def test_every_message_is_bound_and_used(self):
        stage = [q for q in self.data["Quests"] if q["EditorId"] == STAGE][0]
        props = {p["Name"]: p["Target"] for p in stage["Scripts"][0]["Props"] if p["Kind"] == "object" and (p["Target"] or "").startswith(G)}
        built = sorted(m["EditorId"] for m in self.data["Messages"] if m["EditorId"].startswith(G))
        self.assertEqual(sorted(props.values()), built)
        source = (SCRIPTS / "GreenwaterWalk.psc").read_text()
        body = source.split("; ================================================================== set-up")[1]
        for name in props:
            self.assertIn(name, body, "%s is bound and never shown" % name)

    def test_no_box_has_more_than_four_buttons_and_none_is_conditional(self):
        for m in self.data["Messages"]:
            if m["EditorId"].startswith(G):
                self.assertTrue(m["Box"], m["EditorId"])
                self.assertTrue(1 <= len(m["Buttons"]) <= 4, m["EditorId"])
                self.assertTrue(all(not b["Conditions"] for b in m["Buttons"]), m["EditorId"])

    def test_the_road_is_one_quest_with_the_accepted_stages(self):
        road = [q for q in self.data["Quests"] if q["EditorId"] == ROAD][0]
        self.assertEqual([s["Index"] for s in road["Stages"]], [10, 20, 30, 40, 41, 42, 43, 44, 45, 46, 50, 60, 61, 100])
        self.assertEqual([s["Index"] for s in road["Stages"] if s["CompleteQuest"]], [100])
        self.assertNotIn("StartGameEnabled", road["Flags"])
        self.assertEqual([a["Flags"] for a in road["Aliases"]], [["Optional"]] * 11)
        self.assertEqual(sorted(q["EditorId"] for q in self.data["Quests"]),
                         sorted(["TLM_Core", "TLM_MQ01", "TLM_SQ01", "TLM_Trial", "TLM_A1", "TLM_MercyBriefing", ROAD, STAGE, "TLM_MQ02A", "TLM_NM", "TLM_MQ02C", "TLM_RH", "TLM_GW_Relief", "TLM_MQ03", "TLM_FF_Entry"]))
        for other in ("TLM_MQ02", "TLM_MQ04", "TLM_MQ05"):
            self.assertNotIn(other, [q["EditorId"] for q in self.data["Quests"]])

    def test_every_name_a_script_uses_is_one_it_declares(self):
        """A constant, an alias or a message used in a script and declared in another one is a compile error the
        consistency check does not see (found in this repair: the walk used RV_RETURN_NONE, which only the road
        declared). Each of the road's scripts must declare every such name it uses."""
        for name in ("MQ02BQuest.psc", "GreenwaterWalk.psc", "GreenwaterTalk.psc", "Act1Walk.psc"):
            text = re.sub(r"\{[^}]*\}", "", (SCRIPTS / name).read_text())      # documentation first: it may hold a semicolon
            text = "\n".join(line.split(";")[0] for line in text.splitlines())
            text = re.sub(r'"[^"\n]*"', '""', text)
            declared = {m.lower() for m in re.findall(r"^\s*(?:int|float|bool|string)\s+(\w+)\s*=", text, re.M)}
            declared |= {m.lower() for m in re.findall(r"\bProperty\s+(\w+)", text)}
            # Not a name reached through another script's object (mainScript.Alias_CutterA): that one is the other's.
            used = set(re.findall(r"(?<![.\w])((?:RV|GW|BOARD|RIVER|TABLE|ARRIVE|SEEN)_[A-Z0-9_]+|Alias_\w+|(?:Say|Note|Ask|Label|Report|BoardPage|LetterPage)[A-Z]\w*)\b", text))
            functions = {m.lower() for m in re.findall(r"\bFunction\s+(\w+)", text)}
            missing = sorted(u for u in used if u.lower() not in declared and u.lower() not in functions)
            self.assertEqual(missing, [], name + " uses names it does not declare")

    def test_the_rules_script_shows_nothing_and_resets_nothing(self):
        code = "\n".join(l.split(";")[0] for l in (SCRIPTS / "MQ02BQuest.psc").read_text().split("}", 1)[1].splitlines())
        for forbidden in (".Show(", "StartTimer", "RegisterFor", "OnInit", "OnPlayerLoadGame", "OnQuestInit", "Stop()", "Reset()",
                          "TLM_MQ01.SetStage", "TLM_SQ01", "RemoveItem", ".Enable", ".Disable"):
            self.assertNotIn(forbidden, code, forbidden)
        walk = "\n".join(l.split(";")[0] for l in (SCRIPTS / "GreenwaterWalk.psc").read_text().split("}", 1)[1].splitlines())
        for forbidden in ("SetStage(", "SetValue", "AddItem", "RemoveItem", "StartTimer", "OnPlayerLoadGame", "Stop()", "Reset()", "TLM_SQ01"):
            self.assertNotIn(forbidden, walk, forbidden)


class WhatTheseTestsCatch(unittest.TestCase):
    """The scripts with one thing put wrong at a time. Each is noticed by the comparison the tests above make."""

    def setUp(self):
        need_act1_build(self)

    def broken(self, file_name, old, new, play, **world):
        scripts = changed_scripts(file_name, old, new)
        try:
            a = Player(self, scripts=scripts, **world)
            play(a)
        except (AssertionError, SimError) as e:
            return str(e)
        return None

    def chute(self, a):
        a.gangway()
        a.chain("cut")
        a.pilot()
        a.dock()
        a.leave()

    def test_the_scripts_as_they_are_pass(self):
        self.chute(Player(self))

    def test_cut_then_burn(self):
        def play(a):
            a.gangway()
            a.chain("burn")
            a.chain("cut")
            a.fire()
        why = self.broken("MQ02BQuest.psc", "	If Claim != RV_NONE\n		Return false\n	EndIf\n	Claim = RV_FIRE\n", "	Claim = RV_FIRE\n", play)
        self.assertIsNone(why, "the fire control's own test of what stands keeps this out by itself")
        scripts = changed_scripts("MQ02BQuest.psc", "	If Claim != RV_NONE\n		Return false\n	EndIf\n	Claim = RV_FIRE\n", "	Claim = RV_FIRE\n")
        text = (scripts / "GreenwaterWalk.psc").read_text()
        guard = "	If !akRiver.Unsettled()\n		ShowBox(NoteChainNothing)\n		Return\n	EndIf\n	If !akRiver.IsFireWarned()\n"
        self.assertEqual(text.count(guard), 1)
        (scripts / "GreenwaterWalk.psc").write_text(text.replace(guard, "	If !akRiver.IsFireWarned()\n"))
        with self.assertRaises((AssertionError, SimError)):
            play(Player(self, scripts=scripts))

    def test_the_card_win_taken_for_the_grain_at_home(self):
        def play(a):
            a.gangway()
            a.table(["deal"], judge="release")
        self.assertIsNotNone(self.broken("MQ02BQuest.psc", "		TLM_G_MQ02B_Cargo.SetValueInt(RV_CARGO_YIELDED)\n",
                                         "		TLM_G_MQ02B_Cargo.SetValueInt(RV_CARGO_HOME_WHOLE)\n		TLM_G_MQ02B_GrainHome.SetValueInt(1)\n", play, charisma=5))

    def test_her_thanks_on_payment_alone(self):
        def play(a):
            a.gangway()
            a.table(["share"])
        self.assertIsNotNone(self.broken("MQ02BQuest.psc", "	TLM_G_MQ02B_Outcome.SetValueInt(RV_SHARE)\n	SetStage(44)\n",
                                         "	TLM_G_MQ02B_Outcome.SetValueInt(RV_SHARE)\n	SetStage(44)\n	TLM_G_MQ02B_GrainSold.SetValueInt(1)\n	SetStage(46)\n", play))

    def test_the_lie_told_for_the_player(self):
        def play(a):
            a.gangway()
            a.table(["share"])
            a.opal(lie=False)
        self.assertIsNotNone(self.broken("GreenwaterWalk.psc", "		If ShowBox(AskLie) != 0\n			Return\n		EndIf\n", "		ShowBox(AskLie)\n", play))

    def test_paid_twice(self):
        def play(a):
            a.gangway()
            a.table(["share"])
            self.assertFalse(a.s.invoke(ROAD, "TakeShare", []))
            a.same("asked again directly")
        self.assertIsNotNone(self.broken("MQ02BQuest.psc", "	If Claim != RV_NONE || SharePending || SharePaid\n		Return false\n	EndIf\n	Claim = RV_SHARE\n",
                                         "	Claim = RV_SHARE\n", play))

    def test_a_payment_that_did_not_arrive_recorded_as_paid(self):
        def play(a):
            a.gangway()
            a.table(["share"])
        self.assertIsNotNone(self.broken("MQ02BQuest.psc", "	If player.GetItemCount(Caps) < before + RV_SHARE_CAPS\n		; Fails closed",
                                         "	If false\n		; Fails closed", play, refuse={"caps"}))

    def test_the_run_recorded_at_the_lever(self):
        def play(a):
            a.gangway()
            a.chain("cut")
            a.pilot()
        self.assertIsNotNone(self.broken("MQ02BQuest.psc", "	ReturnPending = aiKind\n	Return aiKind\n",
                                         "	ReturnPending = aiKind\n	SetStage(42)\n	Return aiKind\n", play))

    def test_the_whole_cargo_after_the_chute(self):
        self.assertIsNotNone(self.broken("MQ02BQuest.psc", "		int units = RV_UNITS_ALONE\n", "		int units = RV_UNITS_WHOLE\n",
                                         lambda a: (a.kill("rafferty"), setattr(a, "before", a.world()), self.chute(a))))

    def test_a_dead_pilot_counted_as_piloting(self):
        self.assertIsNotNone(self.broken("MQ02BQuest.psc", "	bool piloted = IsThere(Alias_Rafferty)\n", "	bool piloted = true\n",
                                         lambda a: (a.kill("rafferty"), setattr(a, "before", a.world()), self.chute(a))))

    def test_a_dead_hatcher_hunting(self):
        self.assertIsNotNone(self.broken("MQ02BQuest.psc", "	bool hunted = TLM_G_MQ02B_Hatcher.GetValueInt() == RV_H_FREE && IsThere(Alias_Hatcher)\n",
                                         "	bool hunted = true\n", lambda a: (a.kill("hatcher"), setattr(a, "before", a.world()), self.chute(a))))

    def test_a_hanging_nobody_chose(self):
        def play(a):
            a.gangway()
            a.table(["deal"], judge="release")
            a.pilot()
            a.dock()
            a.opal()
        self.assertIsNotNone(self.broken("MQ02BQuest.psc", "		TLM_G_MQ02B_Cargo.SetValueInt(RV_CARGO_HOME_WHOLE)\n",
                                         "		TLM_G_MQ02B_Cargo.SetValueInt(RV_CARGO_HOME_WHOLE)\n		SetStage(60)\n", play, charisma=5))

    def test_a_dead_opal_handed_a_prisoner(self):
        def play(a):
            a.kill("opal")
            a.before = a.world()
            a.gangway()
            a.table(["deal"], judge="custody")
        self.assertIsNotNone(self.broken("GreenwaterWalk.psc", "	bool opal = akRiver.OpalCanSpeak()\n	bool sheriff = akRiver.SheriffCanReceive()\n	int verdict = 0\n",
                                         "	bool opal = true\n	bool sheriff = akRiver.SheriffCanReceive()\n	int verdict = 0\n", play, charisma=5))

    def test_a_dead_opal_speaking(self):
        def play(a):
            a.gangway()
            a.chain("cut")
            a.pilot()
            a.dock()
            a.who["opal"].combat_target = a.who["crew1"]           # SEEDED: she is in a fight
            self.assertEqual(a.press(R + "Opal"), [])
        self.assertIsNotNone(self.broken("GreenwaterWalk.psc", "Function TalkOpal(TLM:MQ02BQuest akRiver)\n	If !akRiver.OpalCanSpeak()\n		Return\n	EndIf\n",
                                         "Function TalkOpal(TLM:MQ02BQuest akRiver)\n", play))

    def test_boarding_locked_behind_opal(self):
        def play(a):
            a.kill("opal")
            a.before = a.world()
            a.gangway()
        self.assertIsNotNone(self.broken("MQ02BQuest.psc", "	3 by reaching a piece of the deck (the greybox has no hull). Never refused\n	for want of stage 20 or of anybody living.}\n	If !RoadOpen()\n",
                                         "	3 by reaching a piece of the deck (the greybox has no hull). Never refused\n	for want of stage 20 or of anybody living.}\n	If !RoadOpen() || !GetStageDone(20)\n", play))

    def test_complete_on_leaving_with_nothing_settled(self):
        def play(a):
            a.gangway()
            a.leave()
        self.assertIsNotNone(self.broken("MQ02BQuest.psc", "	If !IsRunning() || !CanComplete()\n		Return false\n	EndIf\n	If !GetStageDone(100)\n",
                                         "	If !IsRunning()\n		Return false\n	EndIf\n	If !GetStageDone(100)\n", lambda a: (a.gangway(), a.s.invoke(ROAD, "Complete", []), a.same("completed directly"))))
        self.assertIsNotNone(self.broken("GreenwaterWalk.psc", "	If akRiver.CanComplete()\n		If akRiver.Complete()\n			ShowBox(NoteRoadComplete)\n		EndIf\n	Else\n		ShowBox(NoteLeftUnresolved)\n	EndIf\n",
                                         "	ShowBox(NoteRoadComplete)\n", play))

    def test_the_hire_learned_by_opening_the_box(self):
        def play(a):
            a.gangway()
            a.strongbox(read=False)
        self.assertIsNotNone(self.broken("GreenwaterWalk.psc", "	If !ReadPages(LetterPage1, LetterPage2, LetterPage3, LetterPage4)\n		Return\n	EndIf\n",
                                         "	ReadPages(LetterPage1, LetterPage2, LetterPage3, LetterPage4)\n", play))

    def test_a_friend_who_was_not_released(self):
        def play(a):
            a.gangway()
            a.table(["deal"], judge="custody")
        self.assertIsNotNone(self.broken("MQ02BQuest.psc", "	TLM_G_MQ02B_Hatcher.SetValueInt(RV_H_CUSTODY)\n",
                                         "	TLM_G_MQ02B_Hatcher.SetValueInt(RV_H_CUSTODY)\n	TLM_G_MQ02B_HatcherFriend.SetValueInt(1)\n", play, charisma=5))

    def test_two_buttons_the_wrong_way_round(self):
        def play(a):
            a.gangway()
            a.chain("cut")
        self.assertIsNotNone(self.broken("GreenwaterWalk.psc", "	If pick == 0\n		If akRiver.CutChain()\n", "	If pick == 1\n		If akRiver.CutChain()\n", play))

    def test_the_report_given_without_being_chosen(self):
        def play(a):
            self.chute(a)
            a.report(give=False)
        self.assertIsNotNone(self.broken("GreenwaterWalk.psc",
                                         "	If pick == 1\n		Return GW_REPORT_LATER\n	EndIf\n	If pick != 0\n		Return GW_REPORT_CLOSED\n	EndIf\n	If !river.GiveReport()",
                                         "	If !river.GiveReport()", play))


if __name__ == "__main__":
    unittest.main()
