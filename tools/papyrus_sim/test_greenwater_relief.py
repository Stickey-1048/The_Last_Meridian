"""Actual relief PSC on the synthetic master. Seeded failures/load events are
adverse probes, not native engine observations or universal transaction proof.
"""
import json
import unittest
from greenwater_player import Player,R,G
from test_sim import PLUGIN

P='TLM_MSG_GR_'
Q='TLM_GW_Relief'


class Relief:
    def __init__(self,t,route='share',finish=True,scripts=None):
        self.t=t;self.a=a=Player(t,**({'scripts':scripts} if scripts else {}))
        self.s=a.s;self.q=self.s.quests[Q];self.ledger=self.q.scripts[0]
        self.corn=self.ledger.props.get('corn');self.caps=self.ledger.props.get('caps')
        self.messages={m['EditorId']:m for m in json.loads(PLUGIN.read_text())['Messages']}
        if finish:
            if route=='share':a.table(['share'])
            elif route=='whole':
                a.s.player_values['Charisma']=5.0;a.m.charisma=5.0
                a.table(['deal'],judge='release');a.pilot();a.dock()
            elif route in ('eight','six'):
                if route=='eight':a.rafferty('confess')
                else:a.kill('rafferty')  # explicit absent pilot, not a cargo-count seed
                a.chain('cut');a.pilot();a.dock()
            elif route=='fire':a.chain('burn');a.fire()
            else:raise AssertionError(route)
            a.leave()
            a.travel()
    def v(self,key):return self.ledger.vars[key.lower()]
    def count(self,form):return self.s.player.inventory.get(form,0)
    def give(self,form,count):self.s.n_objectreference_additem(self.s.player,None,form,count,True)
    def use(self,where='ReliefStores',**answers):
        self.s.answers={m:[0]*20 for m,v in self.messages.items() if len(v['Buttons'])==1}
        self.s.answers.update({P+'Blocked':[1],P+'StoresFinal':[2],P+'CompleteMenu':[1]})
        self.s.answers.update({P+k:[v] if not isinstance(v,list) else v for k,v in answers.items()})
        at=len(self.s.messages_shown);self.s.walk_to(R+where);self.s.press_activate(R+where);self.a.p.pause(3)
        return [m[len(P):] if m.startswith(P) else m for m in self.s.messages_shown[at:]]
    def donate(self,n=1,confirm=0):
        count=self.count(self.corn);box='DonateMany' if count>=10 else 'DonateFive' if count>=5 else 'DonateOne'
        pick={1:0,5:1,10:2}[n]
        return self.use(Stores=1,StoresFinal=1,ConfirmDonate=confirm,**{box:pick})
    def shop(self,confirm=0):return self.use('ReliefSupply',Supply=0,ConfirmPurchase=confirm)
    def step(self,confirm=0):return self.use(Stores=2,ConfirmStep=confirm)
    def hook(self,box,do):self.s.on_box=lambda name:do() if name==P+box else None
    def load_inside_native(self):
        # Execute the actual nonlatent Loaded PSC body without recursively
        # entering Session.run_ready while its caller generator is executing.
        # Healthy event forwarding is separately tested through the player alias.
        yielded=list(self.s.call(self.ledger,self.ledger.script.functions['loaded'],[]))
        self.t.assertEqual(yielded,[],'Loaded is expected to be nonlatent in this synthetic default session')


class Initialization(unittest.TestCase):
    def test_all_actual_completed_cargo_tuples_initialize_once(self):
        for route,start,cargo in (('whole',900,12),('eight',630,8),('six',495,6),('share',90,0),('fire',90,0)):
            with self.subTest(route=route):
                a=Relief(self,route);before=(a.a.g('Outcome'),a.a.g('Cargo'),a.a.g('Recovered'),a.a.g('GrainHome'),a.a.g('GrainSold'))
                self.assertIn('Status',a.use(Stores=0));self.assertEqual(a.v('startingReserve'),start)
                self.assertEqual(a.v('cargoUnitsAtStart'),cargo);self.assertEqual(a.q.done.count(10),1)
                a.s.invoke(Q,'Loaded',[]);a.use(Stores=0)
                self.assertEqual(a.v('startingReserve'),start);self.assertEqual(a.q.done.count(10),1)
                self.assertEqual((a.a.g('Outcome'),a.a.g('Cargo'),a.a.g('Recovered'),a.a.g('GrainHome'),a.a.g('GrainSold')),before)
    def test_incomplete_or_inconsistent_history_refuses_without_substitute_food(self):
        a=Relief(self,finish=False);self.assertEqual(a.use(Stores=0),['NotReady'])
        self.assertFalse(a.v('initialized'))
        for field,bad in (('Cargo',3),('Recovered',12),('GrainHome',1),('Outcome',43)):
            a=Relief(self);g=a.s.forms['TLM_G_MQ02B_'+field];g.value=bad
            self.assertEqual(a.use(Stores=0),['NotReady'],field);self.assertFalse(a.v('initialized'))
    def test_missing_strict_food_binding_blocks_feature(self):
        a=Relief(self);a.ledger.props['corn']=None
        self.assertEqual(a.use(Stores=0),['NotReady']);self.assertFalse(a.v('initialized'))


class Contributions(unittest.TestCase):
    def test_actual_one_five_ten_consume_and_credit_once_without_old_history_change(self):
        a=Relief(self);a.give(a.corn,30);before=a.count(a.corn)
        history=(a.a.g('Outcome'),a.a.g('GrainSold'),a.a.g('Recovered'))
        for n in (1,5,10):self.assertIn('Donated',a.donate(n))
        self.assertEqual(a.count(a.corn),before-16);self.assertEqual(a.v('donatedUnits'),160)
        self.assertEqual(a.q.done.count(20),1);self.assertEqual(a.v('pendingOperation'),0)
        a.s.invoke(Q,'Loaded',[]);a.use(Stores=0)
        self.assertEqual(a.v('donatedUnits'),160)
        self.assertEqual((a.a.g('Outcome'),a.a.g('GrainSold'),a.a.g('Recovered')),history)
    def test_cancel_invalid_or_stale_confirmation_does_not_remove_food(self):
        for mode in ('cancel','invalid','dead','combat','distant','load','insufficient'):
            with self.subTest(mode=mode):
                a=Relief(self);a.give(a.corn,10)
                def alter():
                    if mode=='dead':a.s.player.dead=True
                    elif mode=='combat':a.a.who['hatcher'].combat_target=a.s.player
                    elif mode=='distant':a.s.player.pos=(99999,99999,0)
                    elif mode=='load':a.s.ref_event(a.s.player,'OnPlayerLoadGame',[],0)
                    elif mode=='insufficient':a.s.player.inventory[a.corn]=0
                if mode=='invalid':a.a.box_returns(P+'ConfirmDonate',7)
                a.hook('ConfirmDonate',alter);a.donate(10,1 if mode=='cancel' else 0)
                self.assertEqual(a.v('donatedUnits'),0);self.assertEqual(a.v('pendingOperation'),0)
                self.assertEqual(a.count(a.corn),0 if mode=='insufficient' else 10)
    def test_shortage_is_cleared_first_and_history_of_hunger_remains(self):
        a=Relief(self);a.step();self.assertEqual(a.v('stepIndex'),1);self.assertTrue(a.v('everShortfall'))
        self.assertEqual(a.s.invoke(Q,'Shortfall',[]),60)
        a.give(a.corn,10);a.donate(10)
        self.assertEqual(a.s.invoke(Q,'Shortfall',[]),0);self.assertEqual(a.s.invoke(Q,'Reserve',[]),40)
        self.assertTrue(a.v('everShortfall'));self.assertIn('PastHunger',a.use(Stores=0))


class SupplyAndSteps(unittest.TestCase):
    def test_three_real_purchases_then_stock_empty_and_no_direct_donation(self):
        a=Relief(self);a.give(a.caps,100);before=a.count(a.caps)
        for _ in range(3):self.assertIn('Purchased',a.shop())
        self.assertEqual(a.count(a.caps),before-60);self.assertEqual(a.count(a.corn),30)
        self.assertEqual(a.v('purchasedThisStep'),30);self.assertEqual(a.v('donatedUnits'),0)
        self.assertEqual(a.shop(),['Supply','NoStock'])
        a.s.invoke(Q,'Loaded',[]);self.assertEqual(a.shop(),['Supply','NoStock'])
    def test_six_explicit_steps_no_passive_time_and_no_seventh_restock(self):
        a=Relief(self,'whole');a.give(a.caps,200)
        a.use(Stores=0);a.a.p.pause(10000);a.s.invoke(Q,'Loaded',[])
        self.assertEqual(a.v('stepIndex'),0);self.assertEqual(a.s.invoke(Q,'Reserve',[]),900)
        for index in range(1,7):
            a.shop();self.assertEqual(a.v('purchasedThisStep'),10)
            a.step();self.assertEqual(a.v('stepIndex'),index)
            self.assertEqual(a.v('purchasedThisStep'),0 if index<6 else 10)
        self.assertEqual(a.s.invoke(Q,'Reserve',[]),0);self.assertEqual(a.s.invoke(Q,'Shortfall',[]),0)
        self.assertTrue(a.v('completionLatched'));self.assertEqual(a.q.done.count(90),1)
        self.assertEqual(a.step(),['CompleteMenu']);self.assertEqual(a.v('stepIndex'),6)
        self.assertEqual(a.v('purchasedThisStep'),10)
    def test_cancel_step_or_missing_funds_changes_nothing(self):
        a=Relief(self);a.s.player.inventory[a.caps]=0
        self.assertEqual(a.shop(),['Supply','NoStock']);self.assertEqual(a.count(a.corn),0)
        a.step(1);self.assertEqual(a.v('stepIndex'),0);self.assertEqual(a.s.invoke(Q,'Reserve',[]),90)


class AmbiguousInventory(unittest.TestCase):
    def test_paced_native_receipt_load_is_checked_after_native_reads(self):
        for phase in ('donation','debit','delivery'):
            with self.subTest(phase=phase):
                a=Relief(self);a.give(a.corn,10);a.give(a.caps,60)
                a.s.native_delay=1.0/60.0
                old=a.s.n_objectreference_getitemcount;fired=[]
                def load_after_receipt_count(ref,ctx,form,*args):
                    result=old(ref,ctx,form,*args)
                    ready=a.v('removalAsked') and (phase!='delivery' or a.v('deliveryAsked'))
                    wanted=a.caps if phase=='debit' else a.corn
                    if ref is a.s.player and form is wanted and ready and not fired:
                        fired.append(True)
                        a.s.ref_event(a.s.player,'OnPlayerLoadGame',[],0)
                    return result
                a.s.n_objectreference_getitemcount=load_after_receipt_count
                if phase=='donation':a.donate(10)
                else:a.shop()
                self.assertEqual(fired,[True]);self.assertTrue(a.v('uncertain'))
                self.assertEqual(a.v('pendingOperation'),1 if phase=='donation' else 2)
                self.assertEqual(a.v('donatedUnits'),0);self.assertEqual(a.v('purchasedThisStep'),0)
                self.assertFalse(a.a.walk.vars['talking']);self.assertFalse(a.v('menuBusy'))
                a.s.native_delay=0;a.use(Blocked=0)
                self.assertEqual(a.v('stepIndex'),0)

    def test_load_at_each_issued_phase_preserves_hold_and_never_reissues(self):
        for phase in ('donation','debit','delivery'):
            with self.subTest(phase=phase):
                a=Relief(self);a.give(a.corn,10);a.give(a.caps,60)
                oldremove=a.s.n_objectreference_removeitem;oldadd=a.s.n_objectreference_additem;calls=[]
                def remove(ref,ctx,*args):
                    calls.append('remove');result=oldremove(ref,ctx,*args)
                    if phase in ('donation','debit'):a.load_inside_native()
                    return result
                def add(ref,ctx,*args):
                    calls.append('add');result=oldadd(ref,ctx,*args)
                    if phase=='delivery':a.load_inside_native()
                    return result
                a.s.n_objectreference_removeitem=remove;a.s.n_objectreference_additem=add
                if phase=='donation':a.donate(10)
                else:a.shop()
                expected=['remove','add'] if phase=='delivery' else ['remove']
                self.assertEqual(calls,expected);self.assertTrue(a.v('uncertain'))
                self.assertEqual(a.v('pendingOperation'),1 if phase=='donation' else 2)
                self.assertEqual(a.v('donatedUnits'),0);self.assertEqual(a.v('purchasedThisStep'),0)
                a.use(Blocked=0);a.shop();a.step()
                self.assertEqual(calls,expected);self.assertEqual(a.v('stepIndex'),0)

    def test_delayed_native_donation_after_immediate_hold_never_creates_late_credit(self):
        a=Relief(self);a.give(a.corn,10);old=a.s.n_objectreference_removeitem;calls=[]
        def delayed(ref,ctx,*args):
            calls.append(args)
            def later():
                old(ref,ctx,*args)
                return
                yield
            a.s.later(1.0,'SEEDED delayed RemoveItem',later)
        a.s.n_objectreference_removeitem=delayed;a.donate(10)
        self.assertEqual(a.count(a.corn),0);self.assertEqual(a.v('donatedUnits'),0)
        self.assertEqual(a.v('pendingOperation'),1);self.assertEqual(len(calls),1)
        a.s.ref_event(a.s.player,'OnPlayerLoadGame',[],0);a.a.p.pause(2)
        a.use(Blocked=0);self.assertEqual(a.v('donatedUnits'),0);self.assertEqual(len(calls),1)

    def test_refused_donation_is_held_and_unrelated_later_count_cannot_credit_it(self):
        a=Relief(self);a.give(a.corn,10);old=a.s.n_objectreference_removeitem;calls=[]
        def refuse(ref,ctx,form,*args):calls.append(form);return None
        a.s.n_objectreference_removeitem=refuse;a.donate(10)
        self.assertEqual(len(calls),1);self.assertEqual(a.v('pendingOperation'),1)
        self.assertTrue(a.v('uncertain'));self.assertEqual(a.v('donatedUnits'),0)
        a.s.n_objectreference_removeitem=old;a.s.player.inventory[a.corn]=0
        a.s.invoke(Q,'Loaded',[]);a.use(Blocked=1);a.step();a.shop()
        self.assertEqual(a.v('donatedUnits'),0);self.assertEqual(a.v('stepIndex'),0)
        self.assertEqual(a.v('pendingOperation'),1);self.assertEqual(len(calls),1)
    def test_refused_purchase_debit_never_delivers_and_refused_delivery_never_reissues(self):
        for phase in ('debit','delivery'):
            with self.subTest(phase=phase):
                a=Relief(self);a.give(a.caps,50);oldremove=a.s.n_objectreference_removeitem;oldadd=a.s.n_objectreference_additem;calls=[]
                def remove(ref,ctx,*args):
                    calls.append('remove')
                    if phase=='debit':return None
                    return oldremove(ref,ctx,*args)
                def add(ref,ctx,*args):calls.append('add');return None
                a.s.n_objectreference_removeitem=remove;a.s.n_objectreference_additem=add
                a.shop();self.assertEqual(calls,['remove'] if phase=='debit' else ['remove','add'])
                self.assertEqual(a.v('pendingOperation'),2);self.assertTrue(a.v('uncertain'))
                self.assertEqual(a.v('purchasedThisStep'),0);self.assertEqual(a.count(a.corn),0)
                a.s.invoke(Q,'Loaded',[]);a.shop();a.step()
                self.assertEqual(calls,['remove'] if phase=='debit' else ['remove','add'])
                self.assertEqual(a.v('stepIndex'),0);self.assertEqual(a.v('donatedUnits'),0)


class LifecycleAndCompletion(unittest.TestCase):
    def test_actual_lie_reply_report_and_all_old_history_survive_later_relief(self):
        a=Relief(self);a.a.opal(lie=True);a.a.leave();a.a.report();a.a.travel()
        def history():
            return ({n:f.value for n,f in a.s.forms.items() if n.startswith('TLM_G_MQ02B_')},
                    dict(a.a.rules.vars),
                    {n:(tuple(q.done),dict(q.displayed),dict(q.completed_objectives),q.completed) for n,q in a.s.quests.items() if n!=Q})
        before=history();self.assertEqual(a.a.g('GrainSold'),1);self.assertTrue(a.a.rules.vars['lieheard'])
        self.assertEqual(a.a.g('Reported'),1)
        a.give(a.corn,10);a.donate(10);a.shop();a.step();a.s.ref_event(a.s.player,'OnPlayerLoadGame',[],0);a.a.p.pause(1)
        self.assertEqual(history(),before)

    def test_start_refusal_or_true_without_running_never_binds_or_enables_and_retries(self):
        for returned in (False,True):
            with self.subTest(start_result=returned):
                from sim import Session
                from unittest.mock import patch
                saved=[]
                def seeded_session(*args,**kwargs):
                    s=Session(*args,**kwargs);old=s.n_quest_start;saved.append(old)
                    def gate(q,ctx):
                        if q.editor_id==Q:return returned  # SEEDED no running postcondition
                        return old(q,ctx)
                    s.n_quest_start=gate
                    return s
                with patch('test_act1.Session',seeded_session):a=Player(self,travel=False,finish=False)
                s=a.s;a.finish_chapter();a.before=a.world()
                q=s.quests[Q];ledger=q.scripts[0]
                self.assertFalse(q.running);self.assertIsNone(ledger.props['alias_stores'].ref)
                self.assertIsNone(ledger.props['alias_supply'].ref)
                self.assertTrue(s.placed[R+'ReliefSupply'].disabled)
                s.n_quest_start=saved[0]
                before=a.world()
                a.press(R+'MercyTravel',{G+'AskTravel':[0]})
                before['completed'][Q]=(True,False)
                self.assertEqual(a.world(),before,'only the relief startup may change outside the river controller')
                self.assertTrue(q.running)
                self.assertIs(ledger.props['alias_stores'].ref,s.placed[R+'ReliefStores'])
                self.assertFalse(s.placed[R+'ReliefStores'].disabled);self.assertFalse(s.placed[R+'ReliefSupply'].disabled)

    def test_actual_local_operations_match_independent_finite_accounting(self):
        import sys
        from test_sim import ROOT
        sys.path.insert(0,str(ROOT/'tools/logic_model'))
        from greenwater_relief_model import ReliefLedger
        for route,start in (('whole',900),('share',90),('eight',630),('six',495)):
            with self.subTest(route=route):
                a=Relief(self,route);m=ReliefLedger(start);a.give(a.corn,80);a.give(a.caps,100)
                for action in ('step','donate','buy','step','donate','step','step','donate','step','buy','step'):
                    if action=='step':a.step();m.advance()
                    elif action=='donate':a.donate(10);m.donate(10)
                    else:a.shop();m.purchase()
                    self.assertEqual((a.v('stepIndex'),a.v('donatedUnits'),a.v('purchasedThisStep'),a.v('everShortfall')),(m.step,m.donated,m.bought,m.hunger))
                    self.assertEqual((a.s.invoke(Q,'Reserve',[]),a.s.invoke(Q,'Shortfall',[]),a.s.invoke(Q,'IsCovered',[])),(m.reserve,m.debt,m.covered))

    def test_dead_opal_does_not_block_real_contribution_or_create_ghost_speech(self):
        a=Relief(self);a.a.kill('opal');a.give(a.corn,5)
        self.assertEqual(a.donate(5),['Stores','DonateFive','ConfirmDonate','Donated'])
        self.assertEqual(a.v('donatedUnits'),50)

    def test_six_short_steps_allow_later_food_to_clear_debt_without_erasing_hunger(self):
        a=Relief(self)
        for _ in range(6):a.step()
        self.assertEqual(a.s.invoke(Q,'Shortfall',[]),810);self.assertFalse(a.v('completionLatched'))
        a.give(a.corn,81)
        for _ in range(8):a.donate(10)
        self.assertEqual(a.s.invoke(Q,'Shortfall',[]),10)
        self.assertIn('CompleteNotice',a.donate(1));self.assertEqual(a.q.done.count(90),1)
        self.assertTrue(a.v('everShortfall'));self.assertEqual(a.s.invoke(Q,'Shortfall',[]),0)

    def test_real_player_load_alias_preserves_healthy_committed_balance_and_stock(self):
        a=Relief(self);a.give(a.corn,5);a.donate(5);a.shop()
        before=(a.v('donatedUnits'),a.v('purchasedThisStep'),a.v('stepIndex'),a.v('requestNonce'),a.v('committedNonce'))
        epoch=a.v('loadEpoch');a.s.ref_event(a.s.player,'OnPlayerLoadGame',[],0);a.a.p.pause(1)
        self.assertEqual(a.v('loadEpoch'),epoch+1)
        self.assertEqual((a.v('donatedUnits'),a.v('purchasedThisStep'),a.v('stepIndex'),a.v('requestNonce'),a.v('committedNonce')),before)
        self.assertEqual(a.v('pendingOperation'),0);self.assertFalse(a.v('uncertain'))

    def test_another_controller_cannot_rebind_the_one_master_ledger(self):
        a=Relief(self);owner=a.v('controlsOwner');stores=a.ledger.props['alias_stores'].ref
        self.assertFalse(a.s.invoke(Q,'OpenControls',[a.s.quests['TLM_A1'],stores,a.ledger.props['alias_supply'].ref]))
        self.assertIs(a.v('controlsOwner'),owner);self.assertIs(a.ledger.props['alias_stores'].ref,stores)

    def test_recursive_activation_under_donation_page_has_only_one_operation(self):
        a=Relief(self);a.give(a.corn,10)
        def concurrent_use():
            fn=a.a.walk.script.functions['used']
            a.s.spawn(a.s.call(a.a.walk,fn,[26]),'actual second Used while confirmation open')
        a.hook('ConfirmDonate',concurrent_use)
        self.assertEqual(a.donate(10),['Stores','DonateMany','ConfirmDonate','Donated'])
        self.assertEqual(a.v('requestNonce'),1);self.assertEqual(a.v('committedNonce'),1)
        self.assertEqual(a.v('donatedUnits'),100);self.assertEqual(a.count(a.corn),0)
