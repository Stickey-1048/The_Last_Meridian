"""Actual PSC adverse native receipts; no compiler/engine/native-load claim."""
import unittest
from test_red_hollow import Hollow
import test_red_hollow_environment as env_cases
road_call=env_cases.road_call

class FinalEffectContext(unittest.TestCase):
    prepared=env_cases.CrossCellBlast.prepared
    args=env_cases.CrossCellBlast.args
    def test_last_effect_receipt_context_loss_preserves_pending_and_recovers(self):
        for native in ('isdisabled','is3dloaded'):
            for mode in ('cell','distance','dead'):
                with self.subTest(native=native,mode=mode):
                    a=self.prepared();self.assertTrue(road_call(a,'BeginBreak',a.walk.props['surfaceslots']))
                    a.ref('BreakOpen').disabled=True;a.ref('BreakClosed').disabled=False
                    attr='n_objectreference_'+native;old=getattr(a.s,attr);fired=[]
                    def late(ref,context,*args):
                        value=old(ref,context,*args)
                        if ref is a.ref('BreakClosed') and not fired:
                            fired.append(True)
                            if mode=='cell':a.s.player.cell=a.ref('Surface01').cell
                            elif mode=='distance':a.s.player.pos=(a.s.player.pos[0]+1024,a.s.player.pos[1],a.s.player.pos[2])
                            else:a.s.player.dead=True
                        return value
                    setattr(a.s,attr,late);before=len(a.calls)
                    self.assertFalse(road_call(a,'FinishBreak',a.ref('BreakOpen'),a.ref('BreakClosed'),*self.args(a)))
                    self.assertTrue(fired);self.assertEqual(a.g('MinePending'),3);self.assertFalse(a.v('innerClosed'));self.assertEqual(a.g('Mine'),0)
                    self.assertTrue(a.ref('BreakOpen').disabled);self.assertFalse(a.ref('BreakClosed').disabled);self.assertEqual(a.g('Survivors'),11)
                    self.assertFalse([c for c in a.calls[before:] if c[0] in ('enable','disable')])
                    setattr(a.s,attr,old);a.s.player.dead=False
                    a.use('BreakControl',Blast=0);self.assertEqual(a.g('Mine'),52);self.assertEqual(a.g('MinePending'),0)

class OperatorObservation(unittest.TestCase):
    def warned(self):
        a=Hollow(self);a.below(warn=True);self.assertTrue(road_call(a,'Armed'));return a
    def test_operator_and_control_unload_pause_then_prime_and_resume_without_catchup(self):
        for name in ('Blevins','FiringControl'):
            with self.subTest(name=name):
                a=self.warned();before=a.v('deadlineSeconds');warnings=(a.v('warningAccepted'),a.v('rescueCommissioned'));fates=list(a.v('minerfates'))
                old=a.s.n_objectreference_is3dloaded
                a.s.n_objectreference_is3dloaded=lambda ref,ctx,*args:False if ref is a.ref(name) else old(ref,ctx,*args)
                a.wait(5);self.assertTrue(road_call(a,'Armed'));self.assertFalse(a.v('deadlineBlocked'));self.assertEqual(a.v('deadlineSeconds'),before)
                self.assertEqual(a.walk.vars['lastsample'],-1);self.assertEqual(a.walk.vars['lastarea'],0);self.assertEqual(a.g('MinePending'),0)
                self.assertEqual((a.v('warningAccepted'),a.v('rescueCommissioned')),warnings);self.assertEqual(a.v('minerfates'),fates)
                a.s.n_objectreference_is3dloaded=old;a.wait(1)
                self.assertEqual(a.v('deadlineSeconds'),before,'first restored sample must only prime')
                a.wait(2);self.assertEqual(a.v('deadlineSeconds'),before-2);self.assertTrue(road_call(a,'Armed'));self.assertEqual(a.g('Mine'),0)
    def test_true_operator_key_control_or_operative_loss_still_blocks(self):
        for mode in ('dead','key','combat','disabled','control','position','miner'):
            with self.subTest(mode=mode):
                a=self.warned();before=a.v('deadlineSeconds')
                if mode=='dead':a.ref('Blevins').dead=True
                elif mode=='key':a.ref('Blevins').inventory[a.rules.props['keyitem']]=0
                elif mode=='combat':a.ref('Blevins').combat_target=a.s.player
                elif mode=='disabled':a.ref('Blevins').disabled=True
                elif mode=='control':a.ref('FiringControl').disabled=True
                elif mode=='position':a.ref('Blevins').pos=(0,0,0)
                else:a.ref('Miner11').pos=(0,0,0)
                a.wait(3);self.assertTrue(a.v('deadlineBlocked'));self.assertFalse(road_call(a,'Armed'));self.assertEqual(a.v('deadlineSeconds'),before);self.assertEqual(a.g('Mine'),0)

if __name__=='__main__':unittest.main()
