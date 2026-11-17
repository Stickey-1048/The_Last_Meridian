"""Independent-review regressions on actual PSC. Alias replacement, load and
native scheduling are explicitly SEEDED adverse inputs, not engine observations.
No save/native/controller acceptance is inferred from these source probes.
"""
import unittest
from test_greenwater_clarity import visit, use, meanwhile, G, R
from test_greenwater_relief import Relief, P, Q


VERDICTS = ((0, 'ConfirmHang'), (1, 'ConfirmCustody'), (2, 'ConfirmRelease'))


def won_unjudged(t,scripts=None):
    if scripts:
        from greenwater_player import Player
        a=Player(t,scripts=scripts,travel=False)
        a.press(R+'MercyTravel',{G+'AskTravel':[0]});a.press(R+'LandingSight',enter=True)
    else:a=visit(t)
    a.s.player_values['Charisma']=5.0
    a.box_returns(G+'HatcherLost',-1)
    use(a,'Table',HatcherTable=0,CardStakes=0)
    a.box_returns(None,None)
    use(a,'Pilot',AskPilotTow=0);a.press(R+'ReturnDock',enter=True)
    t.assertEqual((a.g('Cargo'),a.g('Hatcher')),(2,0));t.assertIn(41,a.road.done)
    return a


def judge(a,origin,choice,box,confirm=0):
    if origin=='opal':return use(a,'Opal',OpalAfterWon=choice,**{box:confirm})
    return use(a,'Table',HatcherLost=choice,**{box:confirm})


class JudgmentIdentity(unittest.TestCase):
    def unchanged(self,a,original,replacement):
        self.assertFalse(original.dead);self.assertFalse(replacement.dead)
        self.assertEqual(a.g('Hatcher'),0);self.assertNotIn(60,a.road.done);self.assertNotIn(61,a.road.done)
        self.assertFalse(a.walk.vars['talking']);self.assertFalse(a.rules.vars['judging'])
        self.assertEqual(a.g('Cargo'),2);self.assertIn(41,a.road.done)

    def test_all_opal_and_table_verdicts_retain_target_before_choice_and_confirmation(self):
        for origin in ('opal','table'):
            for choice,box in VERDICTS:
                for page in (('OpalAfterWon' if origin=='opal' else 'HatcherLost'),box):
                    for change in ('replace','missing','dead','disabled','combat','stale','cancel'):
                        with self.subTest(origin=origin,verdict=box,page=page,change=change):
                            a=won_unjudged(self);original=a.who['hatcher'];other=a.who['crew1']
                            old_pos=(original.cell,tuple(original.pos));other_pos=(other.cell,tuple(other.pos))
                            def alter():
                                if change=='replace':a.rules.props['alias_hatcher'].ref=other
                                elif change=='missing':a.rules.props['alias_hatcher'].ref=None
                                elif change=='dead':original.dead=True
                                elif change=='disabled':original.disabled=True
                                elif change=='combat':original.combat_target=a.s.player
                                elif change=='stale':a.rules.vars['claim']=43
                            meanwhile(a,page,alter)
                            if change=='cancel':a.box_returns(G+page,-1)
                            shown=judge(a,origin,choice,box)
                            self.assertEqual(a.g('Hatcher'),0);self.assertNotIn(60,a.road.done);self.assertNotIn(61,a.road.done)
                            self.assertEqual((original.cell,tuple(original.pos)),old_pos)
                            self.assertEqual((other.cell,tuple(other.pos)),other_pos);self.assertFalse(other.dead)
                            self.assertNotIn('OpalDenied',shown);self.assertFalse(a.walk.vars['talking'])
                            if page!=box:self.assertNotIn(box,shown)

    def test_required_recipients_and_ring_cannot_change_during_either_choice(self):
        for origin in ('opal','table'):
            for choice,box in VERDICTS[:2]:
                aliases=('alias_opal','alias_steeple') if choice==0 else ('alias_mercysheriff',)
                for alias in aliases:
                    for page in (('OpalAfterWon' if origin=='opal' else 'HatcherLost'),box):
                        for change in ('replace','missing','dead_or_disabled','combat'):
                            with self.subTest(origin=origin,box=box,alias=alias,page=page,change=change):
                                a=won_unjudged(self);target=a.who['hatcher'];other=a.who['crew1']
                                ref=a.rules.props[alias].ref
                                def alter():
                                    if change=='replace':a.rules.props[alias].ref=other
                                    elif change=='missing':a.rules.props[alias].ref=None
                                    elif alias=='alias_steeple':ref.disabled=True
                                    elif change=='combat':ref.combat_target=a.s.player
                                    else:ref.dead=True
                                meanwhile(a,page,alter);shown=judge(a,origin,choice,box)
                                self.unchanged(a,target,other);self.assertNotIn('OpalDenied',shown)

    def test_original_participants_succeed_and_cancel_allows_ordinary_retry(self):
        for origin in ('opal','table'):
            for choice,box in VERDICTS:
                with self.subTest(origin=origin,verdict=box):
                    a=won_unjudged(self);judge(a,origin,choice,box,1)
                    self.assertEqual(a.g('Hatcher'),0)
                    judge(a,origin,choice,box)
                    self.assertEqual(a.g('Hatcher'),(3,2,1)[choice])
                    self.assertEqual(a.who['hatcher'].dead,choice==0)
                    if choice==0:self.assertEqual(a.road.done.count(60),1)
                    elif choice==1:self.assertEqual(a.road.done.count(61),1)

    def test_yielded_move_receipts_reject_rebound_target_and_recipients(self):
        for choice,box in VERDICTS[:2]:
            for alias in ('alias_hatcher',('alias_opal' if choice==0 else 'alias_mercysheriff'),'alias_steeple'):
                if choice==1 and alias=='alias_steeple':continue
                with self.subTest(verdict=box,alias=alias):
                    a=won_unjudged(self);target=a.who['hatcher'];other=a.who['crew1'];old=a.s.n_objectreference_moveto;fired=[]
                    other_pos=(other.cell,tuple(other.pos))
                    def moved(ref,ctx,*args):
                        result=old(ref,ctx,*args)
                        if ref is target and not fired:
                            fired.append(True);a.rules.props[alias].ref=other  # SEEDED during yielding effect
                        return result
                    a.s.n_objectreference_moveto=moved;judge(a,'opal',choice,box)
                    self.assertEqual(fired,[True]);self.unchanged(a,target,other)
                    self.assertEqual((other.cell,tuple(other.pos)),other_pos)

    def test_custody_restraint_receipt_revalidates_actual_recipient(self):
        a=won_unjudged(self);target=a.who['hatcher'];other=a.who['crew1'];old=a.s.n_actor_setrestrained;fired=[]
        def restrained(ref,ctx,*args):
            result=old(ref,ctx,*args)
            if ref is target:
                fired.append(True);a.rules.props['alias_mercysheriff'].ref=other
            return result
        a.s.n_actor_setrestrained=restrained;judge(a,'opal',1,'ConfirmCustody')
        self.assertEqual(fired,[True]);self.unchanged(a,target,other)
        self.assertTrue(target.restrained,'the actual issued restraint is retained, not silently rolled back')

    def test_hanging_observes_its_actual_actor_not_dead_replacement(self):
        for original_dies in (False,True):
            with self.subTest(original_dies=original_dies):
                a=won_unjudged(self);target=a.who['hatcher'];other=a.who['crew1'];old=a.s.n_actor_kill;calls=[]
                def killed(ref,ctx,*args):
                    calls.append(ref)
                    if original_dies:old(ref,ctx,*args)
                    other.dead=True;a.rules.props['alias_hatcher'].ref=other
                a.s.n_actor_kill=killed;judge(a,'opal',0,'ConfirmHang')
                self.assertEqual(calls,[target]);self.assertEqual(target.dead,original_dies)
                self.assertEqual(60 in a.road.done,original_dies)
                self.assertEqual(a.g('HatcherHanged'),int(original_dies))
                self.assertIs(a.rules.vars['hangactor'],target)


class ReliefActivationEpoch(unittest.TestCase):
    def interrupt(self,a,ready,next_answers,control='ReliefStores'):
        old=a.s.g_game_getplayer;fired=[]
        def native_read():
            if ready() and not fired:
                fired.append(True);a.load_inside_native()
                def ordinary_later_activation():
                    a.s.answers.update({P+k:[v] for k,v in next_answers.items()})
                    a.s.press_activate(R+control)
                    return
                    yield
                a.s.later(.01,'SEEDED post-load ordinary relief activation',ordinary_later_activation,exact=True)
                def resumed_native():
                    yield ('sleep',1.0)
                    return old()
                return resumed_native()
            return old()
        a.s.g_game_getplayer=native_read
        return fired

    def test_postcommit_load_and_new_request_never_reopens_old_result_page(self):
        for operation,result in (('donation','Donated'),('purchase','Purchased'),('step','StepDone')):
            with self.subTest(operation=operation):
                a=Relief(self);a.give(a.corn,20);a.give(a.caps,100)
                next_answers={'Stores':1,'DonateMany':0,'ConfirmDonate':0}
                where='ReliefStores'
                if operation=='purchase':next_answers={'Supply':0,'ConfirmPurchase':0};where='ReliefSupply'
                elif operation=='step':next_answers={'Stores':2,'ConfirmStep':0}
                fired=self.interrupt(a,lambda:a.v('committedNonce')==1 and a.v('pendingOperation')==0,next_answers,where)
                start=len(a.s.messages_shown)
                if operation=='donation':a.donate(10)
                elif operation=='purchase':a.shop()
                else:a.step()
                a.a.p.pause(30);shown=a.s.messages_shown[start:]
                self.assertEqual(fired,[True]);self.assertEqual(shown.count(P+result),1,shown)
                self.assertEqual(a.v('requestNonce'),2);self.assertEqual(a.v('committedNonce'),2)
                self.assertEqual(a.v('pendingOperation'),0);self.assertFalse(a.v('uncertain'))
                if operation=='donation':self.assertEqual((a.v('donatedUnits'),a.count(a.corn)),(110,9))
                elif operation=='purchase':self.assertEqual((a.v('purchasedThisStep'),a.count(a.corn)),(20,40))
                else:self.assertEqual((a.v('stepIndex'),a.s.invoke(Q,'Shortfall',[])),(2,210))

    def test_status_forecast_hunger_and_completion_chains_keep_originating_epoch(self):
        for page,forbidden in (('Stores','Status'),('Status','ForecastNeeded'),('ForecastNeeded','PastHunger'),('StepDone','CompleteNotice'),('CompleteMenu','Status'),('Blocked','Status')):
            with self.subTest(page=page):
                a=Relief(self,'whole' if page in ('StepDone','CompleteMenu') else 'share')
                if page in ('Stores','Status','ForecastNeeded'):a.step()
                if page=='StepDone':
                    for _ in range(5):a.step()
                elif page=='CompleteMenu':
                    for _ in range(6):a.step()
                elif page=='Blocked':
                    a.give(a.corn,1);a.s.n_objectreference_removeitem=lambda *args:None;a.donate(1)
                start=len(a.s.messages_shown)
                fired=self.interrupt(a,lambda:len(a.s.messages_shown)>start and a.s.messages_shown[-1]==P+page,{'Stores':3,'CompleteMenu':1,'Blocked':1})
                if page=='StepDone':a.step()
                else:a.use(Stores=0,CompleteMenu=0,Blocked=0)
                a.a.p.pause(30);shown=a.s.messages_shown[start:]
                self.assertEqual(fired,[True]);self.assertNotIn(P+forbidden,shown,shown)
                self.assertFalse(a.v('menuBusy'));self.assertFalse(a.a.walk.vars['talking'])
                if page in ('StepDone','CompleteMenu'):
                    self.assertEqual(a.v('stepIndex'),6);self.assertTrue(a.v('completionLatched'));self.assertEqual(a.q.done.count(90),1)
                elif page=='Blocked':self.assertEqual(a.v('pendingOperation'),1);self.assertEqual(a.v('donatedUnits'),0)


class ReviewMutationDetection(unittest.TestCase):
    def test_removing_actual_authoritative_target_guard_is_detected(self):
        from test_act1 import changed_scripts
        scripts=changed_scripts('MQ02BQuest.psc',
            ' && Person(Alias_Hatcher) == akHatcher && Stamp() == aiStamp',
            ' && Stamp() == aiStamp')
        a=won_unjudged(self,scripts);target=a.who['hatcher']
        meanwhile(a,'ConfirmHang',lambda:setattr(a.rules.props['alias_hatcher'],'ref',a.who['crew1']))
        judge(a,'opal',0,'ConfirmHang')
        self.assertTrue(target.dead,'broken program must violate close-without-effect invariant')
        self.assertIn(60,a.road.done)

    def test_removing_captured_epoch_after_native_reads_is_detected(self):
        from test_act1 import changed_scripts
        scripts=changed_scripts('GreenwaterRelief.psc','\tReturn local && aiEpoch == loadEpoch\n','\tReturn local\n')
        a=Relief(self,scripts=scripts);a.give(a.corn,20)
        fired=ReliefActivationEpoch.interrupt(self,a,
            lambda:a.v('committedNonce')==1 and a.v('pendingOperation')==0,
            {'Stores':1,'DonateMany':0,'ConfirmDonate':0})
        start=len(a.s.messages_shown);a.donate(10);a.a.p.pause(30)
        self.assertEqual(fired,[True]);self.assertEqual(a.v('donatedUnits'),110)
        self.assertEqual(a.s.messages_shown[start:].count(P+'Donated'),2,'broken program must reproduce stale older result')
