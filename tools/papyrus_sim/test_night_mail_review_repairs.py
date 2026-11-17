"""Seven independently reviewed context defects: actual PSC regressions/recovery.

Deaths, combat changes, dropped inventory and invalid modal results are seeded
stand-in adversarial events. Restoring a seed is test recovery, not resurrection
or any claim about native scheduling. Ordinary setup always plays the real road.
"""
import json
import unittest
from test_act1 import REF, need_act1_build
from test_sim import PLUGIN
from night_mail_player import Rider, G, R, STAGE, nm
from test_night_mail_scenes import use, while_open, closed, at_the_cut, LONG


def carrying(t):
    a=at_the_cut(t);a.billie('back');a.drawer('take');a.leave()
    return a


class ReviewRepairs(unittest.TestCase):
    def setUp(self):need_act1_build(self)

    def test_every_report_page_closes_on_cancel_or_unsupported_answer_and_retains_earned_report(self):
        pages=['ReportMailRetained','ReportBacked','ReportKnowNeither','ReportEnd']
        for page in pages:
            for answer in (-1,7):
                with self.subTest(page=page,answer=answer):
                    a=carrying(self);a.box_returns(G+page,answer)
                    shown=use(a,REF+'Pritchard',{'ReportUnknown':[0],'AskHandOver':[0]})
                    self.assertEqual(shown,['ReportUnknown']+pages[:pages.index(page)+1])
                    self.assertEqual((a.g('Reported'),a.g('StampDelivered'),a.g('LockridgeReported')),(1,0,0))
                    self.assertEqual((a.count(a.stampitem),a.count(a.stampitem,a.who['sheriff'])),(1,0))
                    closed(a)
                    retry=use(a,REF+'Pritchard',{'AskHandOver':[0]})
                    self.assertEqual(retry,['AskHandOver','NoteStampDelivered','NoteAuthorityWithdrawn'])
                    self.assertEqual((a.g('StampDelivered'),a.g('LockridgeReported')),(1,1))
                    self.assertEqual(a.asked['stamp'],1)

    def test_each_report_page_rechecks_current_participants_before_any_later_modal(self):
        pages=['ReportMailRetained','ReportBacked','ReportKnowNeither','ReportEnd']
        for page in pages:
            for lost in ('player','sheriff','disabled','combat'):
                with self.subTest(page=page,lost=lost):
                    a=carrying(self)
                    def fail():
                        if lost=='player':a.s.player.dead=True
                        elif lost=='sheriff':a.who['sheriff'].dead=True
                        elif lost=='disabled':a.who['sheriff'].disabled=True
                        else:a.who['sheriff'].combat_target=a.who['lockridge']
                    while_open(a,page,fail)
                    shown=a.press(REF+'Pritchard',{G+'ReportUnknown':[0],G+'AskHandOver':[0]})
                    self.assertEqual(shown,['ReportUnknown']+pages[:pages.index(page)+1])
                    self.assertEqual((a.g('Reported'),a.g('StampDelivered')),(1,0))
                    closed(a);a.s.player.dead=False;a.who['sheriff'].dead=False
                    a.who['sheriff'].disabled=False;a.who['sheriff'].combat_target=None
                    self.assertEqual(use(a,REF+'Pritchard',{'AskHandOver':[0]}),['AskHandOver','NoteStampDelivered','NoteAuthorityWithdrawn'])

    def test_authority_modal_loss_preserves_real_receipt_and_only_retries_unfinished_yard(self):
        for vacant in (False,True):
            for lost in ('player','sheriff'):
                with self.subTest(vacant=vacant,lost=lost):
                    a=carrying(self)
                    if vacant:a.who['lockridge'].dead=True
                    notice='NoteAuthorityVacant' if vacant else 'NoteAuthorityWithdrawn'
                    while_open(a,notice,lambda:setattr(a.s.player if lost=='player' else a.who['sheriff'],'dead',True))
                    shown=a.press(REF+'Pritchard',{G+'ReportUnknown':[0],G+'AskHandOver':[0]})
                    self.assertEqual(shown[-1],notice)
                    self.assertEqual((a.g('StampDelivered'),a.g('YardAuthority'),a.g('LockridgeReported'),a.rules.vars['yardpending']),(1,0,0,2))
                    self.assertEqual((a.count(a.stampitem),a.count(a.stampitem,a.who['sheriff']),a.asked['stamp']),(0,1,1))
                    closed(a);a.s.player.dead=False
                    # A separate yard retry does not require the dead/absent sheriff at the yard.
                    use(a,'MercyTravel',{'AskTravelAgain':[0]})
                    self.assertEqual(use(a,'BoardStamped'),[notice])
                    self.assertEqual((a.g('YardAuthority'),a.g('LockridgeReported'),a.rules.vars['yardpending']),(2 if vacant else 1,1,0))
                    self.assertEqual((a.count(a.stampitem,a.who['sheriff']),a.asked['stamp']),(1,1))

    def test_receipt_notice_close_preserves_transfer_and_defers_authority_only(self):
        for lost in (-1,7,'player','sheriff'):
            with self.subTest(lost=lost):
                a=carrying(self)
                if isinstance(lost,int):a.box_returns(G+'NoteStampDelivered',lost)
                else:while_open(a,'NoteStampDelivered',lambda:setattr(a.s.player if lost=='player' else a.who['sheriff'],'dead',True))
                shown=a.press(REF+'Pritchard',{G+'ReportUnknown':[0],G+'AskHandOver':[0]})
                self.assertEqual(shown[-1],'NoteStampDelivered')
                self.assertEqual((a.g('Reported'),a.g('StampDelivered'),a.g('YardAuthority'),a.g('LockridgeReported')),(1,1,0,0))
                self.assertEqual((a.count(a.stampitem),a.count(a.stampitem,a.who['sheriff']),a.asked['stamp']),(0,1,1))
                closed(a);a.s.player.dead=False;a.who['sheriff'].dead=False
                self.assertEqual(use(a,REF+'Pritchard'),['NoteAuthorityWithdrawn'])
                self.assertEqual((a.g('StampDelivered'),a.g('LockridgeReported'),a.asked['stamp']),(1,1,1))

    def test_countersign_effect_hook_cannot_commit_dead_observer_or_fighting_operator(self):
        for lost in ('player','combat'):
            with self.subTest(lost=lost):
                a=at_the_cut(self);a.billie('back')
                def fail():
                    if lost=='player':a.s.player.dead=True
                    else:a.who['lockridge'].combat_target=a.s.player
                a.just_before('enable','BoardSigned',fail)
                shown=use(a,'Drawer',{'LockridgeStamp':[1],'AskCountersignScene':[0]})
                self.assertNotIn('NoteCountersigned',shown)
                self.assertEqual((a.g('Stamp'),a.g('LockridgeSigned'),a.rules.vars['yardpending']),(0,0,1))
                self.assertNotIn(62,a.road.done)
                closed(a);a.s.player.dead=False;a.who['lockridge'].combat_target=None
                self.assertEqual(use(a,'BoardStamped'),['NoteCountersigned'])
                self.assertEqual((a.g('Stamp'),a.g('LockridgeSigned'),a.rules.vars['yardpending']),(62,1,0))
                self.assertTrue(a.on('BoardSigned') and a.on('HeldStock') and not a.on('BoardStamped'))

    def test_countersign_pending_execution_rechecks_context_before_installing_effects(self):
        for lost in ('player','combat'):
            a=at_the_cut(self);a.billie('back');a.refuse_call('enable','BoardSigned')
            use(a,'Drawer',{'LockridgeStamp':[1],'AskCountersignScene':[0]},more=LONG);closed(a)
            before=a.asked_of('enable','BoardSigned')
            if lost=='player':a.s.player.dead=True
            else:a.who['lockridge'].combat_target=a.s.player
            # Directly exercise the actual pending-scene function, beyond the outer activation guard.
            a.s.invoke(STAGE,'CarryOutCountersign',[a.rules])
            self.assertEqual(a.asked_of('enable','BoardSigned'),before)
            self.assertEqual((a.g('Stamp'),a.rules.vars['yardpending']),(0,1))
            a.s.player.dead=False;a.who['lockridge'].combat_target=None
            self.assertEqual(use(a,'BoardStamped'),['NoteCountersigned'])

    def test_hymnal_offer_and_ack_both_require_current_living_dole_and_held_book(self):
        for box in ('AskShowHymnal','LockridgeHymnal'):
            for lost in ('dole','book'):
                with self.subTest(box=box,lost=lost):
                    a=at_the_cut(self);a.hymnal_read();a.back()
                    def fail():
                        if lost=='dole':a.who['dole'].dead=True
                        else:a.s.player.inventory[a.hymnal]=0
                    while_open(a,box,fail)
                    shown=a.press(R+'Lockridge',{G+'AskShowHymnal':[0]})
                    self.assertEqual(shown,['AskShowHymnal']+(['LockridgeHymnal'] if box=='LockridgeHymnal' else []))
                    self.assertFalse(a.rules.vars['hymnalshown']);self.assertNotIn(60,a.road.done)
                    closed(a);a.who['dole'].dead=False;a.s.player.inventory[a.hymnal]=1
                    self.assertEqual(use(a,'Lockridge',{'AskShowHymnal':[0],'LockridgeStamp':[3]}),['AskShowHymnal','LockridgeHymnal','LockridgeStamp'])
                    self.assertTrue(a.rules.vars['hymnalshown']);self.assertIn(60,a.road.done)

    def test_confrontation_checks_captured_phase_and_noncombat_dole_then_recovers(self):
        for lost in ('combat','phase'):
            with self.subTest(lost=lost):
                a=at_the_cut(self)
                def fail():
                    if lost=='combat':a.who['dole'].combat_target=a.who['rifle1']
                    else:a.rules.vars['claim']=nm.NM_RUN
                use(a,'Dole',{'DoleSermon':[0]},also=('DoleFace',fail))
                self.assertFalse(a.rules.vars['dolefaced'])
                self.assertFalse(a.fighting('rifle2'))
                closed(a);a.who['dole'].combat_target=None;a.rules.vars['claim']=0
                self.assertEqual(use(a,'Dole',{'DoleSermon':[0]}),['DoleSermon','DoleFace'])
                self.assertTrue(a.rules.vars['dolefaced'])
                self.assertTrue(all(a.fighting(n) for n in ('dole','rifle1','rifle2','rifle3')))

    def test_stale_hymnal_offer_closes_even_when_not_now_is_selected(self):
        for lost in ('dole','book'):
            a=at_the_cut(self);a.hymnal_read();a.back()
            def fail():
                if lost=='dole':a.who['dole'].dead=True
                else:a.s.player.inventory[a.hymnal]=0
            use_shown=use(a,'Lockridge',{'AskShowHymnal':[1]},also=('AskShowHymnal',fail))
            self.assertEqual(use_shown,['AskShowHymnal'])
            self.assertFalse(a.rules.vars['hymnalshown']);self.assertNotIn(60,a.road.done)

    def test_run_quote_is_withheld_but_drawer_and_neutral_labels_stay_available(self):
        a=at_the_cut(self);a.billie('run');a.back(at='BackFromPlatform')
        self.assertEqual(use(a,'Lockridge',{'LockridgeAfterRan':[1]}),['LockridgeDefault'])
        self.assertEqual(use(a,'Drawer',{'LockridgeStamp':[3]}),['NoteDrawer','LockridgeStamp'])
        messages={m['EditorId']:m for m in json.loads(PLUGIN.read_text())['Messages']}
        self.assertNotIn('Billie Tupper drives',messages[G+'LabelFootplate']['Text'])
        self.assertNotIn('runs the yard',messages[G+'LabelYard']['Text'])
        self.assertIn('current status',messages[G+'LabelYard']['Text'])


if __name__=='__main__':unittest.main()
