"""Broken actual PSC programs must fail the behavioral probes, not text-only
pattern assertions. Synthetic inventory hooks are labelled in each probe.
"""
import unittest
from sim import SimError
from test_act1 import changed_scripts
from test_greenwater_relief import Relief,Q
from test_greenwater_clarity import visit,share


class ReliefMutations(unittest.TestCase):
    def caught(self,file,old,new,probe):
        scripts=changed_scripts(file,old,new)
        try:probe(scripts)
        except (AssertionError,SimError):return
        self.fail('behavioral probe accepted the broken program: '+old)

    def test_irreversible_effect_and_accounting_mutations_are_detected(self):
        def donation(scripts):
            a=Relief(self,scripts=scripts);a.give(a.corn,10);a.donate(10)
            self.assertEqual(a.count(a.corn),0);self.assertEqual(a.v('donatedUnits'),100)
        self.caught('GreenwaterRelief.psc','\trequestActor.RemoveItem(Corn, quantity, true)\n','',donation)

        def refused_donation(scripts):
            a=Relief(self,scripts=scripts);a.give(a.corn,10)
            a.s.n_objectreference_removeitem=lambda *args:None  # SEEDED refusal
            a.donate(10);self.assertEqual(a.v('donatedUnits'),0);self.assertEqual(a.v('pendingOperation'),1)
        self.caught('GreenwaterRelief.psc','\tIf !RequestCurrent(1, 1) || foodAfter != beforeFood - quantity\n','\tIf false\n',refused_donation)

        def refused_debit(scripts):
            a=Relief(self,scripts=scripts);a.give(a.caps,60)
            a.s.n_objectreference_removeitem=lambda *args:None  # SEEDED refusal
            a.shop();self.assertEqual(a.count(a.corn),0);self.assertEqual(a.v('pendingOperation'),2)
        self.caught('GreenwaterRelief.psc','\tIf !RequestCurrent(2, 2) || capsAfter != beforeCaps - 20\n','\tIf false\n',refused_debit)

        def final_stock(scripts):
            a=Relief(self,'whole',scripts=scripts);a.give(a.caps,200)
            for _ in range(6):a.shop();a.step()
            self.assertEqual(a.v('purchasedThisStep'),10);self.assertEqual(a.v('stepIndex'),6)
        self.caught('GreenwaterRelief.psc','\tIf stepIndex < 6\n\t\tpurchasedThisStep = 0\n','\tIf stepIndex <= 6\n\t\tpurchasedThisStep = 0\n',final_stock)

        def historical_hunger(scripts):
            a=Relief(self,scripts=scripts);a.step();a.give(a.corn,10);a.donate(10)
            self.assertEqual(a.s.invoke(Q,'Shortfall',[]),0);self.assertTrue(a.v('everShortfall'))
        self.caught('GreenwaterRelief.psc','\t\teverShortfall = true\n','\t\teverShortfall = false\n',historical_hunger)

        def cargo_tuple(scripts):
            a=Relief(self,'eight',scripts=scripts);a.use(Stores=0)
            self.assertEqual(a.v('startingReserve'),630)
        self.caught('MQ02BQuest.psc','\t\tIf units == 8\n\t\t\tReturn 630\n','\t\tIf units == 8\n\t\t\tReturn 900\n',cargo_tuple)

        def distant(scripts):
            a=Relief(self,scripts=scripts);a.give(a.corn,10)
            a.hook('ConfirmDonate',lambda:setattr(a.s.player,'pos',(99999,99999,0)))
            a.donate(10);self.assertEqual(a.count(a.corn),10);self.assertEqual(a.v('donatedUnits'),0)
        self.caught('GreenwaterRelief.psc','\tReturn player.GetParentCell() == expected.GetParentCell() && player.GetDistance(expected) <= 256.0\n','\tReturn true\n',distant)

        def load_during_donation(scripts):
            a=Relief(self,scripts=scripts);a.give(a.corn,10);old=a.s.n_objectreference_removeitem
            def interrupted(ref,ctx,*args):
                result=old(ref,ctx,*args);a.load_inside_native();return result
            a.s.n_objectreference_removeitem=interrupted;a.donate(10)
            self.assertEqual(a.v('donatedUnits'),0);self.assertEqual(a.v('pendingOperation'),1)
        old='\tloadEpoch += 1\n\tmenuBusy = false\n\tIf pendingOperation != 0\n\t\tuncertain = true\n'
        new='\tloadEpoch += 0\n\tmenuBusy = false\n\tIf pendingOperation != 0\n\t\tuncertain = false\n'
        self.caught('GreenwaterRelief.psc',old,new,load_during_donation)

    def test_payment_confirmation_cannot_be_removed(self):
        def cancelled(scripts):
            from greenwater_player import Player,R,G
            a=Player(self,scripts=scripts,travel=False)
            a.press(R+'MercyTravel',{G+'AskTravel':[0]});a.press(R+'LandingSight',enter=True)
            share(a,1);self.assertEqual(a.asked['caps'],0);self.assertNotIn(44,a.road.done)
        self.caught('GreenwaterWalk.psc','\tIf ShowBox(ConfirmShare) != 0\n','\tIf false\n',cancelled)
