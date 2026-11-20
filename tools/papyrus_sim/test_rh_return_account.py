"""Approved return/account copy on actual PSC + synthetic native responses only."""
import unittest
from test_red_hollow import Hollow,P

class ReturnAccount(unittest.TestCase):
    def settle(self):
        a=Hollow(self);a.below();a.rescue();a.finish57();return a
    def say(self,a,who='Roark',**answers):
        a.pos(who);a.s.answers={P+k:[v] for k,v in answers.items()}
        before=len(a.s.messages_shown);a.s.press_activate(a.ref(who).editor_id);a.wait()
        self.assertEqual([x for x in a.s.papyrus_log if x.startswith('error')],[])
        return a.s.messages_shown[before:]
    def test_all_eleven_actual_originals_and_single_optional_sentence(self):
        a=self.settle();before=a.snapshot();shown=self.say(a,RhaRoarkAll=0,RhaOpen=0)
        self.assertEqual([x for x in shown if 'Rha' in x],[P+'RhaRoarkAll',P+'RhaOpen']);self.assertEqual(a.snapshot(),before)
        shown=self.say(a,'Blevins',RhaBlevinsAll=0);self.assertEqual([x for x in shown if 'Rha' in x],[P+'RhaBlevinsAll'])
    def test_disabled_missing_replaced_displaced_and_later_death_never_all_eleven(self):
        for kind in ('disabled','missing','replaced','displaced','death'):
            with self.subTest(kind=kind):
                a=self.settle();miner=a.ref('Miner03');alias=a.rules.props['miners'][2]
                if kind=='disabled':miner.disabled=True
                elif kind=='missing':alias.ref=None
                elif kind=='replaced':alias.ref=a.ref('Roark')
                elif kind=='displaced':miner.pos=(99999,0,0)
                else:a.die('Miner03',True)
                shown=self.say(a,RhaRoarkPartial10=0)
                self.assertNotIn(P+'RhaRoarkAll',shown);self.assertNotIn(P+'RhaOpen',shown)
                if kind=='death':self.assertIn(P+'RhaRoarkPartial10',shown)
    def test_observed_partial_and_none_dead_are_separate_counts(self):
        for dead in (1,11):
            with self.subTest(dead=dead):
                a=Hollow(self);a.below()
                for i in range(1,dead+1):a.die('Miner%02d'%i,True)
                a.rescue();a.use('Resolve',Resolve=2);self.assertEqual(a.g('Mine'),58)
                name='RhaRoarkNone' if dead==11 else 'RhaRoarkPartial10'
                shown=self.say(a,**{name:0});self.assertIn(P+name,shown);self.assertNotIn(P+'RhaBreak',shown)
    def test_pending_unsupported_stage_and_original_speaker_guards(self):
        for kind in ('pending','stage','speaker'):
            a=self.settle()
            if kind=='pending':a.rules.vars['mineintent']=3
            elif kind=='stage':a.q.done.remove(57)
            else:a.walk.props['rhaoriginalroark']=a.ref('Blevins')
            shown=self.say(a);self.assertFalse(any('Rha' in x for x in shown))
    def test_cancel_or_changed_context_suppresses_second_sentence_and_recovers(self):
        for change in ('cancel','death','load','playercombat','speaker'):
            a=self.settle()
            def mutate(mid):
                if mid!=P+'RhaRoarkAll':return
                if change=='death':a.ref('Miner01').dead=True;a.rules.vars['minerfates'][0]=4
                elif change=='load':a.s.spawn(a.s.call(a.walk,a.walk.script.functions['loaded'],[]),'test load interruption')
                elif change=='playercombat':a.ref('Blevins').combat_target=a.s.player
                elif change=='speaker':a.walk.props['alias_roark'].ref=a.ref('Blevins')
            a.s.on_box=mutate
            if change=='cancel':a.raw[P+'RhaRoarkAll']=-1
            shown=self.say(a,RhaRoarkAll=0);self.assertNotIn(P+'RhaOpen',shown)
            if change=='cancel':
                a.s.on_box=None;a.raw.clear();self.assertIn(P+'RhaOpen',self.say(a,RhaRoarkAll=0,RhaOpen=0))
    def test_order_and_timeout_speech_do_not_call_entombment_death(self):
        for ordered in (True,False):
            a=Hollow(self);a.mouth();a.listen()
            if ordered:a.warning();a.use('FiringControl',Seal=0)
            else:a.warning();a.answer(Final=0);a.wait(605)
            self.assertEqual(a.g('Mine'),53 if ordered else 56)
            name='RhaRoarkOrdered' if ordered else 'RhaRoarkDeadline'
            shown=self.say(a,**{name:0});self.assertEqual([x for x in shown if 'Rha' in x],[P+name]);self.assertEqual(a.g('ObservedDeaths'),0)
    def test_report_success_ack_only_once_and_no_reward_replay(self):
        a=self.settle();a.raw[P+'RhaReport']=0;a.return_report();self.assertEqual(a.g('Reported'),1)
        self.assertEqual(a.s.messages_shown.count(P+'RhaReport'),1);before=dict(a.s.player.inventory)
        self.assertEqual(a.s.invoke('TLM_RH','OfferReport',[a.s.placed['TLM_REF_A1_Pritchard']]),0)
        self.assertEqual(a.s.messages_shown.count(P+'RhaReport'),1);self.assertEqual(a.s.player.inventory,before)
    def test_report_cancel_and_stale_page_keep_report_due_without_ack(self):
        for mode in ('cancel','stale','load'):
            a=self.settle();a.exit();a.s.walk_to('TLM_REF_A1_Pritchard')
            a.answer(Report=0,pritchard_hears_pike_after_fair_unknown=0,ReportFacts=0,ReportEvidence=0,ReportLamp=0)
            if mode=='cancel':a.raw[P+'ReportFacts']=-1
            else:
                def mutate(mid):
                    if mid==P+'ReportFacts':
                        if mode=='stale':a.s.player.dead=True
                        else:a.s.spawn(a.s.call(a.walk,a.walk.script.functions['loaded'],[]),'test load interruption')
                a.s.on_box=mutate
            a.s.press_activate('TLM_REF_A1_Pritchard');a.wait()
            self.assertEqual(a.g('Reported'),0);self.assertNotIn(P+'RhaReport',a.s.messages_shown)
            self.assertTrue(a.s.invoke('TLM_MQ02C','ReportDue',[]))

    def test_terms_only_after_delivery_and_break_neutral_closure(self):
        a=Hollow(self);a.below();a.use('Gallery',StageTravel=0)
        a.use('Dorn',dorn_door=0,dorn_terms=0,dorn_sworn=0)
        a.use('FromGallery',StageTravel=0);a.rescue();self.assertEqual(a.g('Mine'),51)
        self.assertFalse(a.v('termsAcknowledged'))
        shown=self.say(a,RhaRoarkAll=0,RhaTerms=0)
        self.assertTrue(a.v('termsAcknowledged'));self.assertIn(P+'RhaTerms',shown)
        a=Hollow(self);a.below();a.use('Gallery',StageTravel=0);a.use('Dorn',dorn_door=2)
        a.use('FromGallery',StageTravel=0);a.rescue();a.use('CageControl',Descend=0);a.use('BreakControl',Blast=0)
        a.use('BelowControl',HoistBelow=1);self.assertEqual(a.g('Mine'),52)
        shown=self.say(a,RhaRoarkAll=0,RhaBreak=0);self.assertIn(P+'RhaBreak',shown)
        self.assertEqual(a.messages[P+'RhaBreak']['Text'],'[Roark]\n\nThe break is shut.')
    def test_zero_living_after_52_is_no_evacuation_claim_and_58_break_stays_58(self):
        a=Hollow(self);a.below();a.use('Gallery',StageTravel=0);a.use('Dorn',dorn_door=2)
        a.use('FromGallery',StageTravel=0);a.rescue()
        for i in range(1,12):a.die('Miner%02d'%i)
        # Refresh the existing diagnostic global after later deaths; no fate is seeded.
        a.s.invoke('TLM_MQ02C','PublishSurvivors',[a.walk.props['surfaceslots']])
        a.use('CageControl',Descend=0);a.use('BreakControl',Blast=0);a.use('BelowControl',HoistBelow=1)
        self.assertEqual(a.g('Mine'),52);shown=self.say(a,RhaRoarkNone=0,RhaBreak=0)
        self.assertIn(P+'RhaRoarkNone',shown);self.assertIn(P+'RhaBreak',shown)
        a=Hollow(self);a.below();a.die('Miner01');a.rescue();a.use('Resolve',Resolve=2)
        a.pos('BreakControl');a.s.answers={P+'Blast':[0]};a.s.press_activate(a.ref('BreakControl').editor_id);a.wait()
        self.assertEqual(a.g('Mine'),58);self.assertEqual(a.g('BreakBlown'),1)
        shown=self.say(a,RhaRoarkPartial10=0);self.assertNotIn(P+'RhaBreak',shown)
    def test_in_progress_conversation_suppresses_new_speech(self):
        for attr in ('talking_to_player','in_scene'):
            a=self.settle();setattr(a.ref('Roark'),attr,True)
            self.assertFalse(any('Rha' in x for x in self.say(a)))
    def test_canceled_lead_mutant_is_detected_by_actual_controller(self):
        import tempfile,shutil
        from pathlib import Path
        import test_red_hollow as rh
        original=rh.SCRIPTS_NOW
        with tempfile.TemporaryDirectory() as folder:
            copy=Path(folder)/'TLM';shutil.copytree(original,copy)
            path=copy/'RedHollowWalk.psc';text=path.read_text(encoding='utf-8')
            start=text.index('bool Function Aftermath(Actor')
            tail=text[start:];old='If answer != 0 || AftermathRow() != row'
            self.assertEqual(tail.count(old),2)
            tail=tail.replace(old,'If false || AftermathRow() != row',1)
            path.write_text(text[:start]+tail,encoding='utf-8')
            try:
                rh.SCRIPTS_NOW=copy;a=self.settle();a.raw[P+'RhaRoarkAll']=-1
                shown=self.say(a,RhaOpen=0);self.assertIn(P+'RhaOpen',shown)
            finally:rh.SCRIPTS_NOW=original

    def test_nora_late_dialogue_context_death_disable_combat_and_alias_loss_close(self):
        for mode in ('dead','disabled','combat','alias'):
            a=self.settle();roark=a.ref('Roark');fired=[]
            old=a.s.n_objectreference_isindialoguewithplayer
            def late(ref,context,*args):
                value=old(ref,context,*args)
                if ref is roark and not fired:
                    fired.append(True)
                    if mode=='dead':roark.dead=True
                    elif mode=='disabled':roark.disabled=True
                    elif mode=='combat':roark.combat_target=a.s.player
                    else:a.walk.props['alias_roark'].ref=a.ref('Blevins')
                return value
            a.s.n_objectreference_isindialoguewithplayer=late
            shown=self.say(a);self.assertEqual(fired,[True]);self.assertFalse(any('Rha' in x for x in shown))
    def test_nora_post_real_report_late_inventory_context_loss_suppresses_only_speech(self):
        for mode in ('dead','disabled','combat','alias'):
            a=self.settle();sheriff=a.s.placed['TLM_REF_A1_Pritchard'];fired=[]
            old=a.s.n_objectreference_getitemcount
            def late(ref,context,*args):
                value=old(ref,context,*args)
                if a.g('Reported')==1 and ref is a.s.player and not fired:
                    fired.append(True)
                    if mode=='dead':sheriff.dead=True
                    elif mode=='disabled':sheriff.disabled=True
                    elif mode=='combat':sheriff.combat_target=a.s.player
                    else:a.rules.props['alias_sheriff'].ref=a.ref('Roark')
                return value
            a.s.n_objectreference_getitemcount=late;a.return_report()
            self.assertEqual(fired,[True]);self.assertEqual(a.g('Reported'),1)
            self.assertNotIn(P+'RhaReport',a.s.messages_shown)
            self.assertEqual(a.s.invoke('TLM_RH','OfferReport',[sheriff]),0)
    def test_report_ack_requires_original_captured_player(self):
        a=self.settle();a.return_report();before=a.s.invoke('TLM_RH','ReportMark',[])
        player=a.s.player;generation=a.walk.vars['aftermathepoch']
        a.s.player=a.ref('Roark')
        try:
            self.assertFalse(a.s.invoke('TLM_RH','ReportReceiptContext',[a.s.placed['TLM_REF_A1_Pritchard'],before,generation,player]))
        finally:a.s.player=player

if __name__=='__main__':unittest.main()
