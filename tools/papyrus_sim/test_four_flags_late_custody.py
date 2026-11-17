"""R1: actual Enable effects at a changed original-custody boundary."""
import unittest
from test_four_flags import Fair,R
from test_four_flags_recovery import pickup,retry


def observe_late_pickup(a):
    """Same native-observation/effect ordering as Sam's unchanged saved probe."""
    original=a.s.placed[R+'OriginalCase']
    oldread=a.s.n_objectreference_getcontainer
    oldscene=a.s.n_actor_isinscene
    oldenable=a.s.n_objectreference_enable
    armed=[False];fired=[];enabled=[]
    def container(ref,context):
        result=oldread(ref,context)
        if ref is original and not fired:armed[0]=True
        return result
    def scene(ref,context):
        result=oldscene(ref,context)
        if armed[0] and not fired:
            fired.append(ref);a.s.n_objectreference_additem(a.s.player,None,original,1,True)
        return result
    def enable(ref,context,*args):
        if ref is original:enabled.append(original.container is a.s.player)
        return oldenable(ref,context,*args)
    a.s.n_objectreference_getcontainer=container
    a.s.n_actor_isinscene=scene
    a.s.n_objectreference_enable=enable
    retry(a)
    a.s.n_objectreference_getcontainer=oldread
    a.s.n_actor_isinscene=oldscene
    a.s.n_objectreference_enable=oldenable
    return original,fired,enabled


class LateCustodyBoundary(unittest.TestCase):
    def test_exact_late_pickup_observation_has_zero_held_enable_and_retry_recovers(self):
        a=Fair(self);a.use('Ready',Ready=0,Shot=1)
        original,fired,enabled=observe_late_pickup(a)
        self.assertEqual(len(fired),1);self.assertEqual(enabled,[])
        self.assertIs(original.container,a.s.player);self.assertNotIn(44,a.q.done)
        retry(a);self.assertIn(40,a.q.done)
        a.read();self.assertIn(100,a.q.done);self.assertNotIn(44,a.q.done)
        self.assertIs(original.container,a.s.player)

    def test_genuine_initial_ground_enable_occurs_once_and_scene_still_finishes(self):
        a=Fair(self);original=a.s.placed[R+'OriginalCase']
        self.assertTrue(original.disabled);old=a.s.n_objectreference_enable;calls=[]
        def enable(ref,context,*args):
            if ref is original:calls.append(original.container is a.s.player)
            return old(ref,context,*args)
        a.s.n_objectreference_enable=enable;retry(a)
        self.assertEqual(calls,[False]);self.assertFalse(original.disabled)
        self.assertIn(40,a.q.done);self.assertIsNone(original.container)

    def test_already_enabled_ground_retry_does_not_repeat_the_enable_effect(self):
        a=Fair(self);a.use('Ready',Ready=0,Shot=1)
        original=a.s.placed[R+'OriginalCase'];old=a.s.n_objectreference_enable;calls=[]
        def enable(ref,context,*args):
            if ref is original:calls.append(ref)
            return old(ref,context,*args)
        a.s.n_objectreference_enable=enable;retry(a)
        self.assertEqual(calls,[]);self.assertIn(40,a.q.done)

    def test_load_in_initial_container_observation_blocks_enable_then_ordinary_retry_works(self):
        a=Fair(self);original=a.s.placed[R+'OriginalCase']
        oldread=a.s.n_objectreference_getcontainer;oldenable=a.s.n_objectreference_enable
        fired=[];enabled=[]
        def container(ref,context):
            result=oldread(ref,context)
            if ref is original and not fired:fired.append(ref);a.load_inside_native()
            return result
        def enable(ref,context,*args):
            if ref is original:enabled.append(ref)
            return oldenable(ref,context,*args)
        a.s.n_objectreference_getcontainer=container;a.s.n_objectreference_enable=enable
        shown=retry(a)
        self.assertEqual(len(fired),1);self.assertEqual(enabled,[])
        self.assertTrue(original.disabled);self.assertNotIn('Shot',shown);self.assertNotIn(40,a.q.done)
        a.s.n_objectreference_getcontainer=oldread;retry(a)
        self.assertEqual(enabled,[original]);self.assertIn(40,a.q.done)


if __name__=='__main__':unittest.main()
