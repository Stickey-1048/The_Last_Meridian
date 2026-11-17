"""The Night Mail beside what was there before it (NIGHT-MAIL-STORY-001): the
side quest's real endings as Lockridge's greeting reads them, Pritchard's one
conversation with the side quest's report, the river report, the rail report
and the Mercy briefing in it, and the two roads played in one game in either
order. On the stand-in engine, through the real scripts.

Nothing here writes a fact of the side quest or of Greenwater to get a
greeting or a report: each is played to where it stands, as test_act1.py and
test_greenwater.py play it.

NONE OF THIS HAS BEEN SEEN IN THE GAME. Not a compile and not a game test.
"""
import unittest

from test_act1 import BRIEF_HUB, MSG, REF, need_act1_build
from greenwater_player import G as GW, Player
import night_mail_player
from night_mail_player import G, R, Rider, nm


def names(shown):
    return [m[len(G):] for m in shown if m.startswith(G)]


class Base(unittest.TestCase):
    def setUp(self):
        need_act1_build(self)


class LockridgesGreeting(Base):
    def test_nothing_of_the_side_quest(self):
        a = Rider(self)
        self.assertEqual((a.s.get_global("TLM_G_SQ01_Outcome"), a.s.get_global("TLM_G_SQ01_YardAlerted")), (0, 0))
        self.assertEqual(names(a.lockridge("no")), ["LockridgeGateA", "LockridgeGateB"])

    def test_reported_to_pritchard_the_yard_was_alerted(self):
        a = Rider(self, sq01="reported")
        self.assertEqual((a.s.get_global("TLM_G_SQ01_Outcome"), a.s.get_global("TLM_G_SQ01_YardAlerted")), (1, 1))
        self.assertEqual(names(a.lockridge("no")), ["LockridgeGateAlerted"])
        self.assertEqual(names(a.lockridge("rails")), ["LockridgeGateAlerted", "LockridgeRails"])
        a.hire()
        a.depart()

    def test_sold_to_vane(self):
        a = Rider(self, sq01="sold")
        self.assertEqual((a.s.get_global("TLM_G_SQ01_Outcome"), a.s.get_global("TLM_G_SQ01_YardAlerted")), (5, 0))
        self.assertEqual(names(a.lockridge("no")), ["LockridgeGateSold"])
        self.assertEqual(names(a.lockridge("hymns")), ["LockridgeGateSold", "LockridgeDole"])
        a.hire()

    def test_posted_in_public_is_not_the_yard_alerted(self):
        a = Rider(self, sq01="posted")
        self.assertEqual((a.s.get_global("TLM_G_SQ01_Outcome"), a.s.get_global("TLM_G_SQ01_YardAlerted")), (3, 0))
        self.assertEqual(names(a.lockridge("no")), ["LockridgeGateA", "LockridgeGateB"])

    def test_a_ledger_that_is_not_carried_is_not_a_sale(self):
        """SEEDED: the ledger is gone from the inventory with the side quest unsettled."""
        a = Rider(self, with_ledger=True, travel=False)
        ledger = a.s.forms["TLM_BOOK_RailMaintLedger"]
        self.assertEqual(a.count(ledger), 1)
        a.s.player.inventory[ledger] = 0
        a.before = a.world()
        a.travel()
        self.assertEqual(a.s.get_global("TLM_G_SQ01_Outcome"), 0)
        self.assertEqual(names(a.lockridge("no")), ["LockridgeGateA", "LockridgeGateB"])

    def test_the_greeting_reads_and_never_writes_the_side_quest(self):
        for sq01 in (None, "reported", "sold", "posted"):
            with self.subTest(sq01=sq01):
                a = Rider(self, sq01=sq01)
                side = (list(a.s.quests["TLM_SQ01"].done), a.s.get_global("TLM_G_SQ01_Outcome"),
                        a.s.get_global("TLM_G_SQ01_YardAlerted"), a.s.get_global("TLM_G_SQ01_VaneHasLedger"))
                a.lockridge("no")
                a.hire()
                a.depart()
                a.billie("back")
                a.leave()
                a.report()
                self.assertEqual((list(a.s.quests["TLM_SQ01"].done), a.s.get_global("TLM_G_SQ01_Outcome"),
                                  a.s.get_global("TLM_G_SQ01_YardAlerted"), a.s.get_global("TLM_G_SQ01_VaneHasLedger")), side)

    def test_reported_after_arriving_is_read_when_she_is_next_spoken_to(self):
        a = Rider(self, with_ledger=True)
        self.assertEqual(names(a.lockridge("no")), ["LockridgeGateA", "LockridgeGateB"])
        a.leave()
        a.p.press("Pritchard", {"PritchardAfterAndMore": [1], "PritchardReported": [0]}, ["sq_report"])
        a.m.yard_alerted, a.m.sq01_outcome = True, 1
        a.before = a.world()
        a.travel()
        self.assertEqual(names(a.lockridge("ride")), ["LockridgeGateAlerted", "LockridgeHired"])


class PritchardsConversation(Base):
    def settled(self, **kw):
        a = Rider(self, **kw)
        a.hire()
        a.depart()
        a.billie("back")
        a.leave()
        return a

    def test_nothing_due_goes_straight_to_the_briefing(self):
        a = Rider(self)
        a.lockridge("no")
        a.leave()
        self.assertEqual(a.press(REF + "Pritchard", {BRIEF_HUB: [3]}), [BRIEF_HUB])

    def test_before_any_travel_the_rail_adds_nothing(self):
        a = Rider(self, travel=False)
        self.assertEqual(a.press(REF + "Pritchard", {BRIEF_HUB: [3]}), [BRIEF_HUB])
        self.assertFalse(a.road.running)

    def test_the_rail_report_given_is_the_whole_conversation(self):
        a = self.settled()
        shown = a.press(REF + "Pritchard", {G + "ReportUnknown": [0]})
        self.assertEqual(shown[0], "ReportUnknown")
        self.assertEqual(shown[-1], "ReportEnd")
        self.assertNotIn(BRIEF_HUB, shown)
        # And the next one is the briefing, with nothing of the rail in it.
        self.assertEqual(a.press(REF + "Pritchard", {BRIEF_HUB: [3]}), [BRIEF_HUB])

    def test_the_side_quests_report_keeps_its_own_button(self):
        """With the ledger carried and the side quest unsettled: his own box first; "Continue" leads to the
        rail report, and his report button is still the side quest's."""
        a = self.settled(with_ledger=True)
        shown = a.report(more=0)
        self.assertEqual(a.s.messages_shown[-len(shown):][0], MSG + "PritchardAfterAndMore")
        self.assertEqual((a.g("Reported"), a.s.get_global("TLM_G_SQ01_Outcome")), (1, 0))
        a.p.press("Pritchard", {"PritchardAfterAndMore": [1], "PritchardReported": [0]}, ["sq_report"])
        self.assertEqual((a.s.get_global("TLM_G_SQ01_Outcome"), a.s.get_global("TLM_G_SQ01_YardAlerted"), a.g("Reported")), (1, 1, 1))

    def test_the_side_quest_reported_first_leaves_the_rail_report_due(self):
        a = self.settled(with_ledger=True)
        a.p.press("Pritchard", {"PritchardAfterAndMore": [1], "PritchardReported": [0]}, ["sq_report"])
        self.assertEqual(a.g("Reported"), 0)
        a.before = a.world()
        a.report()
        self.assertEqual(a.g("Reported"), 1)

    def test_the_briefing_is_still_there_after_everything(self):
        a = self.settled()
        a.report()
        shown = a.press(REF + "Pritchard", {BRIEF_HUB: [0, 3], "TLM_MSG_MB_Rail": [0] * 4})
        self.assertEqual(shown[:2], [BRIEF_HUB, "TLM_MSG_MB_Rail"])
        self.assertFalse([m for m in shown if not m.startswith("TLM_MSG_MB_")], "nothing of the Night Mail is in the briefing")
        self.assertTrue(a.s.quests["TLM_MercyBriefing"].running)


class BothRoads(Base):
    def river(self, g):
        g.gangway()
        g.chain("cut")
        g.pilot()
        g.dock()
        g.leave()

    def rail(self, a):
        a.travel()
        a.hire()
        a.depart()
        a.billie("run")
        a.leave(at="PlatformExit")

    def test_greenwater_then_the_night_mail(self):
        g = Player(self, scripts=night_mail_player.SCRIPTS_NOW)
        a = Rider(self, person=g.p, travel=False)
        self.river(g)
        g.report()
        river = g.facts()
        a.before = a.world()
        self.rail(a)
        a.report()
        self.assertEqual(g.facts(), river, "the Night Mail changed something of Greenwater")
        g.before = g.world()
        g.same("Greenwater, after the Night Mail was played and reported")

    def test_the_night_mail_then_greenwater(self):
        g = Player(self, scripts=night_mail_player.SCRIPTS_NOW, travel=False)
        a = Rider(self, person=g.p, travel=False)
        self.rail(a)
        a.report()
        rail = a.facts()
        g.before = g.world()
        g.travel()
        self.river(g)
        g.report()
        self.assertEqual(a.facts(), rail, "Greenwater changed something of the Night Mail")
        a.before = a.world()
        a.same("the Night Mail, after Greenwater was played and reported")

    def test_both_reports_due_are_two_conversations_the_river_first(self):
        g = Player(self, scripts=night_mail_player.SCRIPTS_NOW)
        a = Rider(self, person=g.p, travel=False)
        self.river(g)
        a.before = a.world()
        self.rail(a)
        g.before = g.world()
        g.report()
        self.assertEqual((g.g("Reported"), a.g("Reported")), (1, 0))
        a.before = a.world()
        a.report()
        self.assertEqual((g.g("Reported"), a.g("Reported")), (1, 1))

    def test_the_river_left_for_later_goes_on_to_the_rail_in_the_same_conversation(self):
        g = Player(self, scripts=night_mail_player.SCRIPTS_NOW)
        a = Rider(self, person=g.p, travel=False)
        self.river(g)
        a.before = a.world()
        self.rail(a)
        box = GW + ("ReportKnown" if g.m.report(None) == ["ReportKnown"] else "ReportUnknown")
        shown = a.press(REF + "Pritchard", {box: [1], G + "ReportUnknown": [0]})
        self.assertEqual(shown[0], box)
        self.assertEqual(shown[1], "ReportUnknown")
        self.assertEqual((g.g("Reported"), a.g("Reported")), (0, 1))
        # Both left for later: the briefing, as before either road existed.
        g2 = Player(self, scripts=night_mail_player.SCRIPTS_NOW)
        a2 = Rider(self, person=g2.p, travel=False)
        self.river(g2)
        a2.before = a2.world()
        self.rail(a2)
        shown = a2.press(REF + "Pritchard", {box: [1], G + "ReportUnknown": [1], BRIEF_HUB: [3]})
        self.assertEqual(shown, [box, "ReportUnknown", BRIEF_HUB])
        self.assertEqual((g2.g("Reported"), a2.g("Reported")), (0, 0))

    def test_the_two_travel_points_are_two_roads(self):
        g = Player(self, scripts=night_mail_player.SCRIPTS_NOW, travel=False)
        a = Rider(self, person=g.p, travel=False)
        a.travel()
        self.assertFalse(g.road.running)
        self.assertEqual(a.where(), nm.YARD)
        a.leave()
        g.before = g.world()
        g.travel()
        self.assertTrue(g.road.running)
        self.assertNotIn(20, a.road.done)


if __name__ == "__main__":
    unittest.main()
