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
    def __init__(self,t,route='share',finish=True):
        self.t=t;self.a=a=Player(t)
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
        self.s.answers.update({P+'Blocked':[1],P+'StoresFinal':[2]})
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
        self.assertEqual(a.step(),['StoresFinal']);self.assertEqual(a.v('stepIndex'),6)
        self.assertEqual(a.v('purchasedThisStep'),10)
    def test_cancel_step_or_missing_funds_changes_nothing(self):
        a=Relief(self);a.s.player.inventory[a.caps]=0
        self.assertEqual(a.shop(),['Supply','NoStock']);self.assertEqual(a.count(a.corn),0)
        a.step(1);self.assertEqual(a.v('stepIndex'),0);self.assertEqual(a.s.invoke(Q,'Reserve',[]),90)


class AmbiguousInventory(unittest.TestCase):
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
