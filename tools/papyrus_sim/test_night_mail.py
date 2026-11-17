"""The Iron Junction road, TLM_MQ02A "The Night Mail" (NIGHT-MAIL-STORY-001),
on the stand-in engine.

The real scripts (TLM:Act1Walk, TLM:MQ02AQuest, TLM:NightMailWalk,
TLM:NightMailTalk) are played as night_mail_player.py describes, against
tools/logic_model/night_mail_model.py, on the plugin as built against the
stand-in master.

What is played for real: the first section to its end (and, where a test
says so, the side quest to its report or its sale), the travel point, every
conversation and piece of the five labelled zones, each of the four courses
through to the way home, the stamp's three decisions, and the report to
Pritchard with the stamp handed over or kept.

What is SEEDED, and says so where it is done: somebody dead; a death that is
nobody's choice in a box; a call into the game that does nothing or comes
late; a box that comes back with no answer; the game not honouring a request
for caps, the hymnal or the stamp. The stand-in keeps no save: a script's
variables stay as they are, which is what a save does, and OnPlayerLoadGame
is sent as the game sends it.

The stand-in's rules these tests lean on, beyond those test_greenwater.py
lists: [assumed] that MoveTo by script into another interior cell puts the
player there before the script's next look, or within the looks the script
allows; that enabling and disabling a reference of a cell that is not loaded
takes effect; that a cell of the plugin's own with floor pieces and no
navmesh holds a player and standing actors up. None of that has been tried.

NONE OF THIS HAS BEEN SEEN IN THE GAME. Not a compile and not a game test.
"""
import json
import unittest

from test_sim import PLUGIN
from test_act1 import BRIEF_HUB, MSG, REF, need_act1_build
from night_mail_player import G, R, ROAD, STAGE, Rider, nm


class Base(unittest.TestCase):
    def setUp(self):
        need_act1_build(self)


def to_the_cut(a):
    a.hire()
    a.depart()


class GettingThere(Base):
    def test_the_travel_point_is_on_from_set_up_and_nothing_else_is(self):
        a = Rider(self, travel=False, finish=False)
        self.assertTrue(a.stage.running)
        self.assertFalse(a.road.running)
        self.assertTrue(a.on("MercyTravel"))
        for name, ref in a.s.placed.items():
            if name.startswith(R) and name != R + "MercyTravel" and "_Floor_" not in name:
                self.assertTrue(ref.disabled, name)

    def test_no_travel_before_the_chapter_is_over(self):
        a = Rider(self, travel=False, finish=False)
        a.m.main_over = False
        a.travel()
        self.assertFalse(a.road.running)
        self.assertEqual(a.where(), nm.MERCY)

    def test_travel_is_asked_and_declining_changes_nothing(self):
        a = Rider(self, travel=False)
        a.travel(go=False)
        self.assertFalse(a.road.running)
        self.assertEqual(a.where(), nm.MERCY)
        a.travel()
        self.assertTrue(a.road.running)
        self.assertEqual(a.where(), nm.YARD)
        self.assertTrue(a.player_at("YardArrival"))

    def test_requested_transit_is_not_arrival(self):
        """SEEDED: the move into the yard does nothing. The road is not begun and nothing is switched on as if
        the player were there."""
        a = Rider(self, travel=False)
        a.refuse_call("moveto", "player")
        said = a.press(R + "MercyTravel", {G + "AskTravel": [0]}, more=14.0)
        self.assertEqual(said, ["AskTravel", "NoteTravelFailed"])
        self.assertEqual(a.where(), nm.MERCY)
        self.assertNotIn(10, a.road.done)
        a.allow_calls()
        a.m.zones_up = True                       # the zone was switched on for the try and stays ready
        a.m.zones_up = a.walk.vars["zonesup"]
        a.travel()
        self.assertEqual(a.road.done.count(10), 1)

    def test_the_rules_and_the_labels_can_be_read_at_once(self):
        a = Rider(self)
        a.rules_read()
        a.act(R + "LabelYard", ["LabelYard"])
        a.board()
        a.cargo("CargoAboard")


class TheFourCourses(Base):
    def test_run_the_mail_through(self):
        a = Rider(self)
        to_the_cut(a)
        self.assertEqual(a.where(), nm.CUT)
        a.billie("run")
        self.assertEqual((a.g("Outcome"), a.g("Mail"), a.g("Engine"), a.g("Train")), (41, 1, 1, 2))
        self.assertEqual(a.where(), nm.PLATFORM)
        self.assertTrue(a.on("CargoDelivered") and a.on("EngineDamaged") and not a.on("EngineSound"))
        self.assertEqual(a.g("DoleLives"), 1)
        a.cargo("CargoDelivered")
        a.act(R + "EngineDamaged", ["LabelEngineDamaged"])
        a.billie()
        a.leave(at="PlatformExit")
        self.assertTrue(a.road.completed)
        a.report()
        self.assertEqual(a.g("Reported"), 1)

    def test_back_out_and_keep_the_mail(self):
        a = Rider(self)
        to_the_cut(a)
        a.billie("back")
        self.assertEqual((a.g("Outcome"), a.g("Mail"), a.g("Engine"), a.g("Train"), a.g("LineClosed")), (44, 2, 0, 0, 1))
        self.assertEqual(a.where(), nm.YARD)
        self.assertTrue(a.on("CargoRetained") and not a.on("CargoAboard"))
        self.assertEqual(a.g("DoleLives"), 0, "Dole was never met: nothing is said of him")
        a.cargo("CargoRetained")
        a.lockridge()
        a.leave()
        a.report()

    def test_sell_the_mail_to_dole(self):
        a = Rider(self)
        to_the_cut(a)
        a.dole("share", "done")
        self.assertEqual((a.g("Outcome"), a.g("Mail"), a.g("Train"), a.g("MailSold"), a.g("DoleLives")), (43, 3, 3, 1, 1))
        self.assertEqual(a.count(a.caps) - a.caps_before, 150)
        self.assertTrue(a.on("CargoSeized") and not a.on("CargoAtCut"))
        self.assertTrue(a.at("billie", "BillieWalk"))
        a.billie()
        a.dole()
        a.train()
        a.back()
        a.lockridge(morning=False)
        a.lockridge(morning=True)
        self.assertTrue(a.at("billie", "BillieYard"))
        a.lockridge()
        a.leave()
        a.report()
        self.assertEqual(a.count(a.caps) - a.caps_before, 150)

    def test_defeat_dole_and_take_the_train_forward(self):
        a = Rider(self)
        to_the_cut(a)
        a.dole("aside")
        self.assertTrue(a.fighting("dole"))
        a.kill("dole", by_player=True)
        self.assertEqual((a.g("Outcome"), a.g("Dole"), a.g("Mail"), a.g("Train")), (42, 1, 0, 1))
        self.assertIn(42, a.road.done)
        for n in (1, 2, 3):
            self.assertTrue(a.at("rifle%d" % n, "Retreat%d" % n), n)
            self.assertFalse(a.fighting("rifle%d" % n))
        a.train("forward")
        self.assertEqual((a.g("Mail"), a.g("Engine"), a.g("Train")), (1, 0, 2))
        self.assertTrue(a.on("EngineSound") and not a.on("EngineDamaged"))
        a.leave(at="PlatformExit")
        a.report()

    def test_defeat_dole_and_take_the_train_back(self):
        a = Rider(self)
        to_the_cut(a)
        a.dole("name", "aside")
        a.kill("dole", by_player=True)
        a.train("back")
        self.assertEqual((a.g("Mail"), a.g("Train"), a.g("LineClosed")), (2, 0, 0))
        self.assertEqual(a.where(), nm.YARD)
        a.lockridge()
        a.leave()
        a.report()

    def test_defeat_dole_and_leave_the_train_in_the_cut(self):
        a = Rider(self)
        to_the_cut(a)
        a.dole("share", "no")
        a.kill("dole", by_player=True)
        a.train("leave")
        a.train("leave", piece="Reverser")
        a.cargo("CargoAtCut")
        a.back()
        a.leave()
        self.assertEqual((a.g("Mail"), a.g("Train")), (0, 1))
        a.report()

    def test_killing_dole_is_not_delivering_medicine(self):
        a = Rider(self)
        to_the_cut(a)
        a.dole("aside")
        a.kill("dole", by_player=True)
        self.assertEqual((a.g("Mail"), a.g("MailThrough")), (0, 0))
        self.assertFalse(a.on("CargoDelivered"))
        a.back()
        a.leave()
        said = a.report()
        self.assertIn(G + "ReportMailAboard", said)
        self.assertNotIn(G + "ReportMailDelivered", said)

    def test_the_four_outcomes_exclude_one_another(self):
        """After each outcome every control that could settle the encounter is used again, from wherever it
        can be reached, and Dole is killed if he lives: the outcome and its one journal stay."""
        for first in ("run", "back", "sold", "defeat"):
            with self.subTest(first=first):
                a = Rider(self)
                to_the_cut(a)
                if first == "run":
                    a.billie("run")
                    a.billie()
                    a.back(at="BackFromPlatform")
                elif first == "back":
                    a.billie("back")
                    a.billie()
                elif first == "sold":
                    a.dole("share", "done")
                else:
                    a.dole("aside")
                    a.kill("dole", by_player=True)
                outcome, mail, train = a.g("Outcome"), a.g("Mail"), a.g("Train")
                if a.where() == nm.YARD:
                    a.depart()                                # on foot to the Cut: the train is not moved
                self.assertEqual(a.where(), nm.CUT)
                a.train()
                a.train(piece="Reverser")
                a.dole()
                a.billie() if a.at("billie", "BillieWalk") or a.at("billie", "BillieCut") else None
                if first == "defeat":
                    a.train("leave")
                elif not a.who["dole"].dead:
                    a.kill("dole", by_player=True)
                    a.train()
                self.assertEqual((a.g("Outcome"), a.g("Mail"), a.g("Train")), (outcome, mail, train))
                self.assertEqual(len([n for n in (41, 42, 43, 44, 46, 48, 49) if n in a.road.done]), 1)
                self.assertEqual(a.count(a.caps) - a.caps_before, 150 if first == "sold" else 0)


class RefusalAndLeaving(Base):
    def test_refusing_the_job_harms_nobody_and_leaves_the_road_open(self):
        a = Rider(self)
        a.lockridge("no")
        self.assertNotIn(20, a.road.done)
        for who in ("lockridge", "billie"):
            self.assertFalse(a.fighting(who) or a.who[who].dead)
        a.depart()
        a.leave(go=False)
        a.leave()
        self.assertFalse(a.road.completed)
        self.assertEqual(a.where(), nm.MERCY)
        a.report()
        a.travel()
        a.hire()
        a.depart()
        a.billie("back")
        a.leave()
        a.report()

    def test_she_can_be_asked_first_and_hired_after(self):
        a = Rider(self)
        a.lockridge("hymns")
        a.lockridge("rails")
        a.billie()
        a.hire()
        a.billie("cut")
        a.billie("on")
        a.depart(go=False)
        a.depart()
        self.assertIn(30, a.road.done)

    def test_walking_back_from_the_cut_settles_nothing_and_the_train_can_be_rejoined(self):
        a = Rider(self)
        to_the_cut(a)
        a.back(go=False)
        a.back()
        self.assertEqual((a.where(), a.g("Outcome"), a.g("Train")), (nm.YARD, 0, 1))
        a.lockridge()
        a.depart(go=False)
        a.depart()
        self.assertEqual(a.where(), nm.CUT)
        a.billie("run")

    def test_leaving_from_the_cut_unsettled_and_coming_back(self):
        a = Rider(self)
        to_the_cut(a)
        a.back()
        a.leave()
        self.assertFalse(a.road.completed)
        a.travel()
        a.depart()
        a.dole("share", "done")
        a.back()
        a.leave()
        self.assertTrue(a.road.completed)
        a.travel()
        a.leave()
        self.assertEqual(a.road.done.count(100), 1)

    def test_declining_each_scene_changes_nothing(self):
        a = Rider(self)
        to_the_cut(a)
        a.billie("run", confirm=False)
        a.billie("back", confirm=False)
        a.train("run", confirm=False)
        a.dole("share", "back")
        a.dole("back")
        self.assertEqual((a.g("Outcome"), a.rules.vars["claim"]), (0, 0))
        a.dole("aside")
        a.kill("dole", by_player=True)
        a.train("forward", confirm=False)
        a.train("back", confirm=False)
        self.assertEqual((a.g("Mail"), a.g("Train")), (0, 1))


class DeadPeople(Base):
    def test_lockridge_dead_before_the_job(self):
        """The grounded fallback: nobody assigns the job; the player boards it unasked."""
        a = Rider(self)
        a.kill("lockridge")
        a.lockridge()
        a.depart(go=False)
        self.assertNotIn(21, a.road.done)
        a.depart()
        self.assertIn(21, a.road.done)
        self.assertNotIn(20, a.road.done)
        a.billie("run")
        a.leave(at="PlatformExit")
        a.report()

    def test_lockridge_dead_after_the_job(self):
        a = Rider(self)
        a.hire()
        a.kill("lockridge")
        a.depart()
        a.billie("back")
        a.lockridge()
        a.drawer("take")
        self.assertIn(64, a.road.done)
        a.leave()
        a.report()
        self.assertEqual((a.g("YardAuthority"), a.g("LockridgeReported")), (2, 1))

    def test_billie_dead_before_the_job(self):
        """The player-regulator fallback."""
        a = Rider(self)
        a.kill("billie")
        a.hire()
        a.billie()
        a.depart()
        self.assertIn(31, a.road.done)
        self.assertNotIn(30, a.road.done)
        a.train("down")
        a.train("run")
        self.assertIn(46, a.road.done)
        a.leave(at="PlatformExit")
        a.report()

    def test_billie_dead_in_the_cut(self):
        for course in ("run", "back", "sold", "defeat"):
            with self.subTest(course=course):
                a = Rider(self)
                to_the_cut(a)
                a.kill("billie")
                if course == "run":
                    a.train("run", piece="Regulator")
                    self.assertIn(46, a.road.done)
                elif course == "back":
                    a.train("back", piece="Reverser")
                    self.assertIn(49, a.road.done)
                elif course == "sold":
                    a.dole("share", "done")
                    self.assertIn(48, a.road.done)
                    a.back()
                    a.lockridge()
                else:
                    a.dole("aside")
                    a.kill("dole", by_player=True)
                    a.train("forward")
                self.assertFalse(a.rules.vars["billiedrives"])

    def test_both_of_the_yard_dead(self):
        a = Rider(self)
        a.kill("lockridge")
        a.kill("billie")
        a.depart()
        self.assertEqual(sorted(n for n in (20, 21, 30, 31) if n in a.road.done), [21, 31])
        a.train("back")
        a.drawer("close")
        a.leave()
        a.report()

    def test_dole_dead_before_the_train_comes(self):
        """Not the player's outcome: nothing is offered of him, and the four courses less two remain."""
        a = Rider(self)
        a.hire()
        a.kill("dole", by_player=False)
        self.assertEqual((a.g("Outcome"), a.g("Dole")), (0, 2))
        a.depart()
        a.dole()
        a.billie("run")
        self.assertEqual((a.g("Outcome"), a.g("DoleLives")), (41, 0))
        a.lockridge() if a.where() == nm.YARD else None
        a.leave(at="PlatformExit")
        said = a.report()
        self.assertNotIn(G + "ReportDoleByYou", said)

    def test_dole_killed_by_somebody_else_in_the_cut(self):
        a = Rider(self)
        to_the_cut(a)
        a.kill("dole", by_player=False)
        self.assertEqual((a.g("Outcome"), a.g("Dole")), (42, 2))
        self.assertIn(47, a.road.done)
        self.assertNotIn(42, a.road.done)
        a.train("back")
        a.leave()
        said = a.report()
        self.assertIn(G + "ReportDoleDead", said)

    def test_dole_dead_after_another_outcome_is_only_his_death(self):
        a = Rider(self)
        to_the_cut(a)
        a.dole("back")
        a.billie("back")
        self.assertEqual(a.g("DoleLives"), 1)
        a.kill("dole", by_player=True)
        self.assertEqual((a.g("Outcome"), a.g("Dole"), a.g("DoleLives")), (44, 2, 0))
        self.assertNotIn(42, a.road.done)

    def test_a_rifle_dead_stays_where_it_fell(self):
        a = Rider(self)
        to_the_cut(a)
        a.dole("aside")
        a.kill("rifle2", by_player=True)
        a.kill("dole", by_player=True)
        self.assertFalse(a.at("rifle2", "Retreat2"))
        self.assertTrue(a.at("rifle1", "Retreat1") and a.at("rifle3", "Retreat3"))
        a.train("forward")

    def test_pritchard_dead(self):
        a = Rider(self, sheriff=False)
        to_the_cut(a)
        a.billie("back")
        a.drawer("take")
        a.leave()
        self.assertEqual(a.press(REF + "Pritchard"), [])
        self.assertEqual((a.g("Reported"), a.g("StampDelivered"), a.count(a.stampitem)), (0, 0, 1))


class Evidence(Base):
    def test_the_plate_the_flyleaf_and_the_chalk(self):
        a = Rider(self)
        to_the_cut(a)
        a.plate()
        a.plate()
        self.assertEqual((a.g("SilverRail"), a.road.done.count(50)), (1, 1))
        a.chalk()
        a.hymnal_read()
        self.assertEqual((a.g("OstranderKnown"), a.count(a.hymnal)), (1, 1))
        a.hymnal_read()
        self.assertEqual((a.count(a.hymnal), a.asked["hymnal"]), (1, 1))

    def test_oral_identity_is_not_holding_or_reading_a_book(self):
        a = Rider(self)
        to_the_cut(a)
        a.dole("name", "silver", "share", "back")
        self.assertEqual((a.g("OstranderKnown"), a.g("SilverRail")), (1, 1))
        self.assertEqual(sorted(n for n in (50, 51, 55, 56) if n in a.road.done), [51, 56])
        self.assertEqual(a.count(a.hymnal), 0)
        a.billie("back")
        # She is told nothing by a name the player only heard: there is no book to show.
        a.lockridge()
        self.assertNotIn(60, a.road.done)
        self.assertFalse(a.rules.vars["hymnalshown"])

    def test_evidence_in_either_order_and_after_each_outcome(self):
        """The siding is walked back to after a run or a back-out, and is at hand after a sale or a fight."""
        for course in ("run", "back", "sold", "defeat"):
            for first in ("plate", "hymnal"):
                with self.subTest(course=course, first=first):
                    a = Rider(self)
                    to_the_cut(a)
                    if course == "run":
                        a.billie("run")
                        a.back(at="BackFromPlatform")
                        a.depart()
                    elif course == "back":
                        a.billie("back")
                        a.depart(go=False)
                        a.depart()
                    elif course == "sold":
                        a.dole("share", "done")
                    else:
                        a.dole("aside")
                        a.kill("dole", by_player=True)
                    self.assertEqual(a.where(), nm.CUT)
                    outcome, mail, train = a.g("Outcome"), a.g("Mail"), a.g("Train")
                    for what in ((a.plate, a.hymnal_read) if first == "plate" else (a.hymnal_read, a.plate)):
                        what()
                    self.assertEqual((a.g("SilverRail"), a.g("OstranderKnown")), (1, 1))
                    self.assertEqual((a.g("Outcome"), a.g("Mail"), a.g("Train")), (outcome, mail, train))
                    a.back()
                    a.leave()
                    said = a.report()
                    self.assertIn(G + "ReportKnowBoth", said)

    def test_evidence_before_the_outcome_is_kept_through_it(self):
        for course in ("run", "back", "sold", "defeat"):
            with self.subTest(course=course):
                a = Rider(self)
                to_the_cut(a)
                a.plate()
                a.hymnal_read()
                if course == "run":
                    a.billie("run")
                elif course == "back":
                    a.billie("back")
                elif course == "sold":
                    a.dole("share", "done")
                else:
                    a.dole("aside")
                    a.kill("dole", by_player=True)
                self.assertEqual((a.g("SilverRail"), a.g("OstranderKnown"), a.count(a.hymnal)), (1, 1, 1))

    def test_the_hymnal_shown_opens_the_drawer(self):
        a = Rider(self)
        to_the_cut(a)
        a.hymnal_read()
        a.back()
        a.lockridge(show=False)
        self.assertNotIn(60, a.road.done)
        a.lockridge(show=True, stamp="close")
        self.assertIn(60, a.road.done)
        self.assertEqual(a.count(a.hymnal), 1, "showing it is not giving it away")
        a.lockridge()

    def test_the_hymnal_is_not_shown_after_dole_is_dead_or_the_stamp_decided(self):
        a = Rider(self)
        to_the_cut(a)
        a.hymnal_read()
        a.dole("aside")
        a.kill("dole", by_player=True)
        a.train("back")
        a.lockridge()
        self.assertFalse(a.rules.vars["hymnalshown"])

    def test_a_hymnal_the_game_does_not_give_is_asked_for_once(self):
        """SEEDED: the request is not honoured. The flyleaf was still read; no book is claimed."""
        a = Rider(self, refuse=("hymnal",))
        to_the_cut(a)
        a.hymnal_read()
        a.hymnal_read()
        self.assertEqual((a.count(a.hymnal), a.asked["hymnal"], a.g("OstranderKnown")), (0, 1, 1))
        a.back()
        a.lockridge()
        self.assertNotIn(60, a.road.done)


class TheStamp(Base):
    def found(self, course="back"):
        a = Rider(self)
        to_the_cut(a)
        if course == "run":
            a.billie("run")
            a.back(at="BackFromPlatform")
        else:
            a.billie("back")
        return a

    def test_she_keeps_stamping(self):
        a = self.found()
        a.drawer("close")
        a.drawer("keep")
        self.assertEqual((a.g("Stamp"), a.g("LockridgeStamping"), a.count(a.stampitem)), (61, 1, 0))
        a.drawer()
        a.board()
        a.lockridge()
        a.leave()
        a.report()
        self.assertEqual((a.g("YardAuthority"), a.g("LockridgeReported")), (0, 0))

    def test_she_countersigns(self):
        a = self.found()
        a.drawer("sign", confirm=False)
        self.assertEqual(a.g("Stamp"), 0)
        a.drawer("sign")
        self.assertEqual((a.g("Stamp"), a.g("LockridgeSigned")), (62, 1))
        self.assertTrue(a.on("BoardSigned") and a.on("HeldStock") and not a.on("BoardStamped"))
        a.board()
        a.drawer()
        a.leave()
        a.report()
        self.assertEqual(a.g("YardAuthority"), 0)

    def test_taken_is_not_delivered(self):
        a = self.found()
        a.drawer("take")
        self.assertEqual((a.g("Stamp"), a.g("StampDelivered"), a.count(a.stampitem), a.g("LockridgeReported")), (63, 0, 1, 0))
        self.assertFalse(a.on("StampInDrawer"))
        self.assertTrue(a.on("BoardStamped"), "she still holds the yard: nobody has been told anything")
        a.drawer()
        a.lockridge()
        a.leave()
        a.report(hand=False)
        self.assertEqual((a.g("Reported"), a.g("StampDelivered"), a.g("YardAuthority")), (1, 0, 0))
        a.report(hand=True)
        self.assertEqual((a.g("StampDelivered"), a.g("YardAuthority"), a.g("LockridgeReported")), (1, 1, 1))
        self.assertEqual((a.count(a.stampitem), a.count(a.stampitem, a.who["sheriff"])), (0, 1))
        a.report()
        a.travel()
        self.assertTrue(a.on("BoardClosed") and not a.on("BoardStamped"))
        a.board()
        a.lockridge()
        a.depart()

    def test_the_stamp_reported_before_the_road_is_complete(self):
        a = self.found()
        a.drawer("take")
        a.leave(go=False)
        a.m.where = nm.YARD
        # Out by the exit with the road complete, then the stamp alone: the report first, then the stamp.
        a.leave()
        a.report(give=False, hand=True)
        self.assertEqual((a.g("Reported"), a.g("StampDelivered")), (0, 1))
        a.report(give=True)

    def test_each_decision_is_final(self):
        for first in ("keep", "sign", "take"):
            with self.subTest(first=first):
                a = self.found()
                a.drawer(first)
                before = (a.g("Stamp"), a.count(a.stampitem))
                a.drawer()
                a.lockridge()
                self.assertEqual((a.g("Stamp"), a.count(a.stampitem)), before)
                self.assertEqual(len([n for n in (61, 62, 63, 64) if n in a.road.done]), 1)

    def test_a_stamp_the_game_does_not_give_is_not_taken(self):
        """SEEDED: the request is not honoured. Asked once; the decision stays open; nothing is delivered."""
        a = Rider(self, refuse=("stamp",))
        to_the_cut(a)
        a.billie("back")
        a.drawer("take")
        self.assertEqual((a.g("Stamp"), a.count(a.stampitem), a.asked["stamp"]), (0, 0, 1))
        self.assertTrue(a.on("StampInDrawer"))

    def test_the_stamp_before_any_outcome_and_with_the_job_refused(self):
        """The forgery never needs a route, and a route never needs the forgery: with her authority withdrawn
        the job is boarded unasked, as when she is dead."""
        a = Rider(self)
        a.lockridge("no")
        a.drawer("take")
        a.leave()
        a.report(hand=True)
        self.assertEqual((a.g("StampDelivered"), a.g("YardAuthority"), a.g("Outcome")), (1, 1, 0))
        a.travel()
        a.lockridge()
        a.depart()
        self.assertIn(21, a.road.done)
        a.billie("run")
        a.leave(at="PlatformExit")
        a.report()

    def test_the_handover_that_does_not_leave_the_player_is_not_delivered(self):
        """SEEDED: RemoveItem does nothing. Pritchard has no stamp, so nothing is said to have been delivered."""
        a = self.found()
        a.drawer("take")
        a.leave()
        a.refuse.add("handover")
        said = a.press(REF + "Pritchard", {G + "ReportUnknown": [0], G + "AskHandOver": [0]}, more=6.0)
        self.assertIn("NoteHandoverFailed", said)
        self.assertEqual((a.g("StampDelivered"), a.g("YardAuthority"), a.count(a.stampitem)), (0, 0, 1))
        a.refuse.discard("handover")
        a.m.reported = True
        a.report(hand=True)
        self.assertEqual((a.g("StampDelivered"), a.count(a.stampitem, a.who["sheriff"])), (1, 1))


class Greetings(Base):
    def test_the_plain_gate(self):
        a = Rider(self)
        self.assertEqual(a.rules.Greeting(), 1) if hasattr(a.rules, "Greeting") else None
        a.lockridge("rails")

    def test_the_yard_was_alerted_by_the_real_report(self):
        a = Rider(self, sq01="reported")
        self.assertEqual((a.s.get_global("TLM_G_SQ01_Outcome"), a.s.get_global("TLM_G_SQ01_YardAlerted")), (1, 1))
        said = a.lockridge("rails")
        self.assertEqual([m[len(G):] for m in said if m.startswith(G)], ["LockridgeGateAlerted", "LockridgeRails"])
        a.hire()

    def test_the_ledger_was_really_sold_to_vane(self):
        a = Rider(self, sq01="sold")
        self.assertEqual(a.s.get_global("TLM_G_SQ01_Outcome"), 5)
        said = a.lockridge("hymns")
        self.assertEqual([m[len(G):] for m in said if m.startswith(G)], ["LockridgeGateSold", "LockridgeDole"])
        a.lockridge("no")
        a.hire()


if __name__ == "__main__":
    unittest.main()
