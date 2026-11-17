"""Held original after an interrupted staged scene: actual PSC, synthetic only."""
import unittest
from test_four_flags import Fair,P,R,Q


def pickup(a):
    original=a.s.placed[R+'OriginalCase']
    a.s.n_objectreference_additem(a.s.player,None,original,1,True)
    return original


def retry(a,dead=False):
    answers={'Ready':0,'DeadCourier' if dead else 'Shot':0,'Occupation':1,
             'S_brigg_demand_courier_dead_1' if dead else 'S_brigg_demand_1':0}
    return a.use('Ready',**answers)


class HeldOriginalRecovery(unittest.TestCase):
    def interrupted(self,kind='pause',dead=False,scripts=None):
        a=Fair(self,**({'scripts':scripts} if scripts else {}))
        if dead:a.s.placed[R+'Juno'].dead=True
        notice='DeadCourier' if dead else 'Shot'
        old=a.s.n_message_show
        if kind in ('invalid','close'):
            def raw(message,context,*args):
                if message.editor_id==P+notice:
                    a.s.messages_shown.append(message.editor_id)
                    return 7 if kind=='invalid' else -1  # SEEDED native acknowledgement
                return old(message,context,*args)
            a.s.n_message_show=raw
        elif kind=='load':a.hook(notice,a.load_inside_native)
        a.use('Ready',Ready=0,**{notice:0 if kind=='load' else 1})
        a.s.n_message_show=old;a.s.on_box=None
        self.assertEqual(a.q.done,[10]);self.assertFalse(a.s.placed[R+'OriginalCase'].disabled)
        return a

    def test_pause_invalid_close_or_load_then_original_pickup_retry_and_full_read(self):
        for interruption in ('pause','invalid','close','load'):
            with self.subTest(interruption=interruption):
                a=self.interrupted(interruption);history=a.old_history();original=pickup(a)
                self.assertEqual(a.q.done,[10]);self.assertIs(original.container,a.s.player)
                retry(a)
                self.assertIn(40,a.q.done);self.assertIn(46,a.q.done)
                self.assertTrue(all(n not in a.q.done for n in (41,42,43,44,60,70)))
                self.assertIs(original.container,a.s.player);self.assertEqual(a.v('effectPending'),0)
                a.read();self.assertIn(60,a.q.done);self.assertIn(100,a.q.done);self.assertNotIn(44,a.q.done)
                self.assertIs(original.container,a.s.player);self.assertEqual(a.old_history(),history)

    def test_dead_found_original_can_remain_held_without_resurrection_or_acquisition_credit(self):
        a=self.interrupted(dead=True);original=pickup(a);shown=retry(a,dead=True)
        self.assertIn('DeadCourier',shown);self.assertNotIn('Shot',shown)
        self.assertIn(40,a.q.done);self.assertIn(45,a.q.done);self.assertNotIn(46,a.q.done)
        self.assertTrue(a.s.placed[R+'Juno'].dead);self.assertNotIn(44,a.q.done)
        self.assertIs(original.container,a.s.player);a.read();self.assertIn(100,a.q.done)

    def test_retry_does_not_enable_or_transfer_an_inventory_original(self):
        a=self.interrupted();original=pickup(a);original.disabled=True
        old=a.s.n_objectreference_enable;calls=[]
        def enable(ref,context,*args):
            if ref is original:calls.append(ref)
            return old(ref,context,*args)
        a.s.n_objectreference_enable=enable;retry(a)
        self.assertEqual(calls,[]);self.assertIs(original.container,a.s.player)
        self.assertTrue(original.disabled);self.assertIn(40,a.q.done)

    def test_ground_original_still_requires_explicit_scene_acknowledgement(self):
        a=self.interrupted();original=a.s.placed[R+'OriginalCase']
        self.assertIsNone(original.container);a.use('Ready',Ready=1)
        self.assertNotIn(40,a.q.done);retry(a);self.assertIn(40,a.q.done)
        self.assertIsNone(original.container);self.assertNotIn(44,a.q.done)

    def test_other_holder_base_copy_or_rebound_original_cannot_recover_the_scene(self):
        for change in ('other_holder','base_copy','case_alias','courier_alias','player_alias'):
            with self.subTest(change=change):
                a=self.interrupted();original=a.s.placed[R+'OriginalCase']
                if change=='other_holder':a.s.n_objectreference_additem(a.originals[0],None,original,1,True)
                elif change=='base_copy':
                    original.pos=(90000,90000,16)
                    a.s.n_objectreference_additem(a.s.player,None,original.base,1,True)
                else:
                    pickup(a)
                    if change=='case_alias':a.rules.props['alias_originalcase'].ref=a.s.placed[R+'OriginalSilver']
                    elif change=='courier_alias':a.rules.props['cast'][8].ref=a.s.placed[R+'Grey']
                    else:a.rules.props['alias_player'].ref=a.originals[0]
                shown=retry(a);self.assertNotIn('Shot',shown);self.assertNotIn(40,a.q.done)
                self.assertNotIn(44,a.q.done);self.assertNotIn(60,a.q.done)
                if change=='other_holder':self.assertIs(original.container,a.originals[0])

    def test_holder_actor_player_or_epoch_loss_on_ack_closes_without_new_progress(self):
        for change in ('holder','case_alias','courier_alias','player_alias','player_dead','player_combat','player_scene','courier_dead','courier_combat','courier_dialogue','courier_scene','load'):
            with self.subTest(change=change):
                a=self.interrupted();original=pickup(a);courier=a.s.placed[R+'Juno']
                def interrupt():
                    if change=='holder':a.s.n_objectreference_additem(a.originals[0],None,original,1,True)
                    elif change=='case_alias':a.rules.props['alias_originalcase'].ref=a.s.placed[R+'OriginalSilver']
                    elif change=='courier_alias':a.rules.props['cast'][8].ref=a.s.placed[R+'Grey']
                    elif change=='player_alias':a.rules.props['alias_player'].ref=a.originals[0]
                    elif change=='player_dead':a.s.player.dead=True
                    elif change=='player_combat':a.s.placed[R+'Grey'].combat_target=a.s.player
                    elif change=='player_scene':a.s.player.in_scene=True
                    elif change=='courier_dead':courier.dead=True
                    elif change=='courier_combat':courier.combat_target=a.s.player
                    elif change=='courier_dialogue':courier.talking_to_player=True
                    elif change=='courier_scene':courier.in_scene=True
                    else:a.load_inside_native()
                a.hook('Shot',interrupt);shown=retry(a)
                self.assertIn('Shot',shown);self.assertNotIn('S_brigg_demand_1',shown)
                self.assertNotIn(40,a.q.done);self.assertNotIn(44,a.q.done);self.assertNotIn(60,a.q.done)

    def test_load_during_container_read_before_display_or_commit_closes_then_retry_recovers(self):
        for boundary in ('display','commit'):
            with self.subTest(boundary=boundary):
                a=self.interrupted();original=pickup(a);old=a.s.n_objectreference_getcontainer
                armed=[boundary=='display'];fired=[]
                if boundary=='commit':a.hook('Shot',lambda:armed.__setitem__(0,True))
                def read(ref,context):
                    result=old(ref,context)
                    if ref is original and armed[0] and not fired:
                        fired.append(ref);a.load_inside_native()
                    return result
                a.s.n_objectreference_getcontainer=read;shown=retry(a)
                self.assertEqual(len(fired),1);self.assertNotIn(40,a.q.done)
                if boundary=='display':self.assertNotIn('Shot',shown)
                a.s.n_objectreference_getcontainer=old;a.s.on_box=None
                retry(a);self.assertIn(40,a.q.done);self.assertIs(original.container,a.s.player)

    def test_custody_is_checked_after_yielding_courier_context_reads(self):
        a=self.interrupted();original=pickup(a);old=a.s.n_actor_isinscene;armed=[False];fired=[]
        a.hook('Shot',lambda:armed.__setitem__(0,True))
        def context(ref,caller):
            result=old(ref,caller)
            if armed[0] and ref is a.s.placed[R+'Juno'] and not fired:
                fired.append(ref);a.s.n_objectreference_additem(a.originals[0],None,original,1,True)
            return result
        a.s.n_actor_isinscene=context;retry(a)
        self.assertEqual(len(fired),1);self.assertNotIn(40,a.q.done)
        self.assertIs(original.container,a.originals[0]);self.assertNotIn(44,a.q.done)


if __name__=='__main__':unittest.main()
