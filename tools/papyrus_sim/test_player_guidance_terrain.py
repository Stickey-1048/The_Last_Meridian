"""Current composed source, including independent review guidance counterexamples."""
import unittest
from test_red_hollow import Hollow,P

class CurrentGuidance(unittest.TestCase):
    def shown(self,a,n):return a.s.n_quest_isobjectivedisplayed(a.w,None,n)
    def test_casualty_before_muster_leads_to_survivor_hoist_without_forcing45(self):
        a=Hollow(self);a.mouth();a.listen();a.use('CageControl',NoWarning=0,Descend=0)
        a.die('Miner03',True);a.use('Roster')
        self.assertTrue(a.s.invoke('TLM_MQ02C','ShiftFound',[]));self.assertNotIn(45,a.q.done)
        self.assertTrue(self.shown(a,40));self.assertFalse(self.shown(a,30));self.assertEqual(a.g('Mine'),0)
        a.rescue();self.assertEqual(a.g('Survivors'),10);self.assertEqual(a.g('ObservedDeaths'),1)
    def test_blast_and_unfinished_break_facts_name_the_right_next_action(self):
        a=Hollow(self);a.below();a.use('Gallery',StageTravel=0);a.use('Dorn',dorn_door=2)
        a.use('FromGallery',StageTravel=0);a.rescue();a.use('CageControl',Descend=0)
        a.refuse.add(('enable',a.s._whom(a.ref('BreakClosed'))));a.use('BreakControl',Blast=0)
        self.assertEqual(a.g('MinePending'),3);a.s.notifications.clear();a.s.invoke('TLM_RH','Facts',[])
        self.assertTrue(any('Inner-break charge control' in n for n in a.s.notifications))
        self.assertFalse(any('Return to the hoist' in n for n in a.s.notifications))
        a.refuse.clear();a.use('BreakControl',Blast=0);self.assertEqual(a.g('Mine'),52)
        a.s.notifications.clear();a.s.invoke('TLM_RH','Facts',[])
        self.assertTrue(any('Take the hoist back to the yard' in n for n in a.s.notifications));self.assertFalse(any('bring the surviving miners up' in n for n in a.s.notifications))
        self.assertEqual(a.g('Survivors'),11);self.assertTrue(self.shown(a,85))
    def test_mercy_report_target_persists_on_cancel_then_clears_only_on_real_ack(self):
        a=Hollow(self);a.below();a.rescue();a.finish57();a.exit()
        self.assertTrue(a.s.invoke('TLM_MQ02C','ReportDue',[]));self.assertTrue(self.shown(a,90))
        sheriff=a.s.placed['TLM_REF_A1_Pritchard'];self.assertIs(a.walk.props['alias_guidesheriff'].ref,sheriff)
        a.s.walk_to('TLM_REF_A1_Pritchard');a.answer(Report=1);a.s.answers['TLM_MSG_MB_Hub']=[3];a.s.press_activate('TLM_REF_A1_Pritchard');a.wait()
        self.assertTrue(self.shown(a,90));self.assertEqual(a.g('Reported'),0)
        a.answer(Report=0,pritchard_hears_pike_after_fair_unknown=0,ReportFacts=0,ReportEvidence=0,ReportLamp=0)
        a.s.press_activate('TLM_REF_A1_Pritchard');a.wait()
        self.assertEqual(a.g('Reported'),1);self.assertFalse(self.shown(a,90));self.assertEqual(a.g('Mine'),57)

if __name__=='__main__':unittest.main()
