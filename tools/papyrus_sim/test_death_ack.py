"""Adversarial deferred/suppressed death model, NOT a claim about engine internals.

Historical replay semantics remain unchanged. Only this subclass defers the
native death commit and suppresses it if town Essential promotion wins first.
"""
import unittest
from unittest.mock import patch
from sim import Session, SimError, unwrap
from test_act1 import Person, REF, need_act1_build
from test_overlap import scripts_with_the_quest_at, scripts_without

class DeferredDeath(Session):
    delay=.5
    def __init__(self,*a,**kw):
        super().__init__(*a,**kw)
        self.kill_requests=0;self.bad_promotions=[];self.pending_commit=None
    def n_actor_kill(self,actor,context,killer=None):
        if actor.editor_id != REF+'Abel':
            return super().n_actor_kill(actor,context,killer)
        self.kill_requests+=1
        def commit():
            Session.n_actor_kill(self,actor,context,killer)
            yield from ()
        self.pending_commit=commit
        if self.delay is not None:self.later(self.delay,'adversarial deferred death',commit,exact=True)
    def n_alias_forcerefto(self,alias,context,ref):
        actor=unwrap(ref)
        if alias.name=='CaravanDroverInTown' and actor and not actor.dead:self.bad_promotions.append(actor)
        return super().n_alias_forcerefto(alias,context,ref)

class DeathAcknowledgment(unittest.TestCase):
    def setUp(self):need_act1_build(self)
    def person(self,delay=.5,scripts=None):
        class Model(DeferredDeath):pass
        Model.delay=delay
        with patch('test_act1.Session',Model):
            p=Person(self,**({'scripts':scripts} if scripts else {}))
        p.press('Dispatch',events=['take_dispatch'])
        return p
    def stage(self,p,n):
        q=p.s.quests['TLM_MQ01'];p.s.spawn(p.s.n_quest_setstage(q,None,n),'test native stage request')
    def rapid(self,p):
        self.stage(p,30);p.s.run(p.s.now+.01)
        self.stage(p,40);p.s.run(p.s.now+12)
    def inst(self,p):return p.s.quests['TLM_MQ01'].scripts[0]
    def test_old_source_exhibits_adversarial_promotion_gap(self):
        p=self.person(scripts=scripts_with_the_quest_at('f26e5be',self));self.rapid(p)
        self.assertFalse(p.s.placed[REF+'Abel'].dead)
        self.assertEqual(len(p.s.bad_promotions),1)
    def test_delayed_ack_precedes_any_town_promotion_with_one_kill(self):
        for delay in (.1,.5,2):
            with self.subTest(delay=delay):
                p=self.person(delay);self.rapid(p)
                self.assertTrue(p.s.placed[REF+'Abel'].dead)
                self.assertEqual(p.s.kill_requests,1)
                self.assertEqual(p.s.bad_promotions,[])
                self.assertTrue(self.inst(p).vars['townfinished'])
                self.assertEqual(p.g('TLM_G_CaravanOutcome'),2)
    def test_suppressed_death_is_bounded_and_blocks_delivery_and_fiction(self):
        p=self.person(None);self.rapid(p)
        self.assertEqual(p.s.kill_requests,1);self.assertEqual(p.s.bad_promotions,[])
        self.assertTrue(self.inst(p).vars['deathunacknowledged'])
        self.assertFalse(self.inst(p).vars['townfinished'])
        before=p.g('TLM_G_Rep_MercyCrossing');boxes=len(p.s.message_boxes)
        self.stage(p,50);p.s.run(p.s.now+7)
        p.s.invoke('TLM_A1','TalkPritchard',[])
        self.assertEqual(len(p.s.message_boxes),boxes)
        self.assertEqual(p.g('TLM_G_MQ01_DebriefVariant'),0)
        self.assertEqual(p.g('TLM_G_MQ01_Done'),0)
        self.assertEqual(p.g('TLM_G_Rep_MercyCrossing'),before)
        self.assertEqual(p.has(p.s.forms['TLM_MISC_Dispatch']),1)
        self.assertFalse(p.s.quests['TLM_MQ01'].completed_objectives.get(20,False))
        for _ in range(3):p.s.invoke('TLM_MQ01','Recover',[])
        self.assertEqual(p.s.kill_requests,1)
    def test_late_engine_ack_resumes_only_owned_deferred_delivery_once(self):
        p=self.person(None);self.rapid(p);self.stage(p,50);p.s.run(p.s.now+6)
        before=p.g('TLM_G_Rep_MercyCrossing')
        p.s.spawn(p.s.pending_commit(),'late completion of ORIGINAL request');p.s.run(p.s.now+.1)
        for _ in range(3):p.s.invoke('TLM_MQ01','Recover',[])
        self.assertTrue(p.s.placed[REF+'Abel'].dead)
        self.assertTrue(p.s.invoke('TLM_MQ01','DeliveryAcknowledged',[]))
        self.assertEqual(p.s.kill_requests,1)
        self.assertEqual(p.g('TLM_G_Rep_MercyCrossing'),before+1)
        self.assertEqual(p.has(p.s.forms['TLM_MISC_Dispatch']),0)
    def test_busy_handler_barrier_returns_false_within_existing_five_seconds(self):
        p=self.person();self.inst(p).vars['resolutionsatwork']=1
        t=p.s.now
        self.assertFalse(p.s.invoke('TLM_MQ01','WaitForResolutions',[0]))
        self.assertLessEqual(p.s.now-t,5.01)
        p.s.invoke('TLM_MQ01','ApplyTown',[])
        self.assertEqual(p.s.bad_promotions,[])
        self.assertTrue(self.inst(p).vars['towndeferred'])

    def test_read_last_barrier_catches_handler_beginning_during_native_queries(self):
        mutant=scripts_without(self,'current count-read-first barrier',
            '((Outcome() == OUT_NONE && ResolutionStagesSet() > resolutionsBegun) || resolutionsAtWork > aiMine)',
            '(resolutionsAtWork > aiMine || (Outcome() == OUT_NONE && ResolutionStagesSet() > resolutionsBegun))')
        for scripts,expected in ((None,False),(mutant,True)):
            with self.subTest(current=scripts is None):
                p=self.person(scripts=scripts);s=p.s;i=self.inst(p)
                s.native_delay=.01
                def begin():
                    i.vars['resolutionsatwork']=1;i.vars['resolutionsbegun']=1
                    s.quests['TLM_MQ01'].done.append(31)
                    yield from ()
                s.later(.005,'model handler starts during first native query',begin,exact=True)
                self.assertEqual(s.invoke('TLM_MQ01','WaitForResolutions',[0]),expected)
    def test_old_completed50_and60_are_read_only_no_reward_replay(self):
        for done60 in (False,True):
            with self.subTest(done60=done60):
                p=self.person();q=p.s.quests['TLM_MQ01'];q.done.append(50)
                q.completed_objectives[20]=True;p.s.set_global('TLM_G_MQ01_DebriefVariant',2)
                if done60:q.done.extend([60,100]);p.s.set_global('TLM_G_MQ01_Done',1)
                p.s.set_global('TLM_G_Rep_MercyCrossing',7)
                for _ in range(2):
                    p.s.invoke('TLM_MQ01','Recover',[]);p.s.invoke('TLM_MQ01','ApplyDelivered',[])
                self.assertEqual(p.g('TLM_G_Rep_MercyCrossing'),7)
                self.assertTrue(p.s.invoke('TLM_MQ01','DeliveryAcknowledged',[]))

    def test_betrayal_wait_timeout_defers_instead_of_losing_intended_consequence(self):
        p=self.person();self.stage(p,30);p.s.run(p.s.now+.01)
        self.inst(p).vars['resolutionsatwork']=1
        self.stage(p,35);p.s.run(p.s.now+6)
        self.assertTrue(self.inst(p).vars['betrayaldeferred'])
        self.assertEqual(p.g('TLM_G_CaravanMethod'),0)
        self.inst(p).vars['resolutionsatwork']=0
        p.s.invoke('TLM_MQ01','ResumeCaravanConsequences',[])
        self.assertFalse(self.inst(p).vars['betrayaldeferred'])
        self.assertEqual(p.g('TLM_G_CaravanOutcome'),3)
        self.assertEqual(p.g('TLM_G_CaravanMethod'),2)

    def test_betrayal_after_unacknowledged_death_is_not_replaced_by_delivery(self):
        p=self.person(None);self.rapid(p)
        self.stage(p,35);p.s.run(p.s.now+6)
        self.assertEqual(p.g('TLM_G_CaravanOutcome'),3)
        self.assertEqual(p.g('TLM_G_CaravanMethod'),2)
        self.stage(p,50);p.s.run(p.s.now+6)
        self.assertEqual(p.g('TLM_G_MQ01_DebriefVariant'),0)
        self.assertTrue(self.inst(p).vars['deathunacknowledged'])
    def test_old_partial50_is_not_automatically_replayed(self):
        p=self.person();p.s.quests['TLM_MQ01'].done.append(50)
        p.s.set_global('TLM_G_Rep_MercyCrossing',7)
        p.s.invoke('TLM_MQ01','Recover',[]);p.s.invoke('TLM_A1','TalkPritchard',[])
        p.s.invoke('TLM_MQ01','ApplyDelivered',[])
        self.assertEqual(p.g('TLM_G_Rep_MercyCrossing'),7)
        self.assertEqual(p.g('TLM_G_MQ01_DebriefVariant'),0)
        self.assertFalse(p.s.invoke('TLM_MQ01','DeliveryAcknowledged',[]))

    def test_old_completed40_before50_can_deliver_once_with_default_new_fields(self):
        for branch,reward in (('saved',2),('evaded',1),('bypassed',1)):
            with self.subTest(branch=branch):
                p=self.person();i=self.inst(p)
                if branch=='evaded':self.rapid(p)
                else:
                    if branch=='saved':
                        self.stage(p,30);p.s.run(p.s.now+.1)
                        self.stage(p,31);p.s.run(p.s.now+1)
                    self.stage(p,40);p.s.run(p.s.now+12)
                dead=p.s.placed[REF+'Abel'].dead;kills=p.s.kill_requests
                for name in ('deathunacknowledged','townapplying','towndeferred','townfinished',
                             'deliveryapplying','deliverydeferred','deliveryfinished','deliveryrequestedhere','betrayaldeferred'):
                    i.vars[name]=False
                i.vars['requesteddeath']=None
                before=p.g('TLM_G_Rep_MercyCrossing')
                self.stage(p,50);p.s.run(p.s.now+8)
                for _ in range(2):p.s.invoke('TLM_MQ01','Recover',[])
                self.assertTrue(p.s.invoke('TLM_MQ01','DeliveryAcknowledged',[]))
                self.assertEqual(p.g('TLM_G_Rep_MercyCrossing'),before+reward)
                self.assertEqual(p.has(p.s.forms['TLM_MISC_Dispatch']),0)
                self.assertTrue(i.vars['townfinished'])
                self.assertEqual(p.s.placed[REF+'Abel'].dead,dead)
                self.assertEqual(p.s.kill_requests,kills)
    def test_already_dead_target_does_not_request_another_kill(self):
        p=self.person();p.s.placed[REF+'Abel'].dead=True
        p.s.invoke('TLM_MQ01','KillByCutters',[next(a for a in p.s.quests['TLM_MQ01'].aliases.values() if a.name=='CaravanDrover')])
        self.assertEqual(p.s.kill_requests,0)

    def test_partial_new_delivery_never_replays_committed_reward(self):
        p=self.person();self.rapid(p);before=p.g('TLM_G_Rep_MercyCrossing')
        original=p.s.n_globalvariable_mod
        def interrupted(value,context,amount):
            original(value,context,amount)
            if value.editor_id=='TLM_G_Rep_MercyCrossing':raise SimError('injected interruption after reward')
        p.s.n_globalvariable_mod=interrupted
        self.stage(p,50)
        with self.assertRaisesRegex(SimError,'injected interruption'):p.s.run(p.s.now+8)
        p.s.n_globalvariable_mod=original
        for _ in range(2):
            p.s.invoke('TLM_MQ01','Recover',[]);p.s.invoke('TLM_MQ01','ApplyDelivered',[])
        self.assertEqual(p.g('TLM_G_Rep_MercyCrossing'),before+1)
        self.assertFalse(p.s.invoke('TLM_MQ01','DeliveryAcknowledged',[]))

    def test_overlapping_owned_delivery_calls_commit_reward_once(self):
        p=self.person();self.rapid(p);s=p.s;i=self.inst(p)
        before=p.g('TLM_G_Rep_MercyCrossing')
        i.vars['deliveryrequestedhere']=True;s.quests['TLM_MQ01'].done.append(50)
        s.native_delay=.01
        for _ in range(3):s.spawn(s.call(i,i.script.functions['applydelivered'],[]),'overlapping owned delivery')
        s.run(s.now+15)
        self.assertEqual(p.g('TLM_G_Rep_MercyCrossing'),before+1)
        self.assertEqual(p.has(s.forms['TLM_MISC_Dispatch']),0)
        self.assertTrue(s.invoke('TLM_MQ01','DeliveryAcknowledged',[]))

    def test_late_ack_of_replaced_actor_does_not_resume_wrong_caravan(self):
        p=self.person(None);self.rapid(p)
        q=p.s.quests['TLM_MQ01'];next(a for a in q.aliases.values() if a.name=='CaravanDrover').ref=None
        p.s.spawn(p.s.pending_commit(),'late original death');p.s.run(p.s.now+.1)
        p.s.invoke('TLM_MQ01','Recover',[])
        self.assertFalse(self.inst(p).vars['townfinished'])
        self.assertTrue(self.inst(p).vars['deathunacknowledged'])
        self.assertEqual(p.s.kill_requests,1)

if __name__=='__main__':unittest.main()
