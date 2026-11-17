"""Owner scene/choice clarity: actual PSC, synthetic master and adverse hooks.
Explicit button indices exercise reachable activations. No native readability,
licensed compiler or live game acceptance is implied.
"""
import json
import unittest
from greenwater_player import Player, G, R
from test_sim import PLUGIN


def visit(t, travel=True):
    a=Player(t,travel=False)
    if travel:
        a.press(R+'MercyTravel',{G+'AskTravel':[0]})
        a.press(R+'LandingSight',enter=True)
    return a


def use(a,part,**answers):
    return a.press(R+part,{G+k:[v] for k,v in answers.items()})


def share(a,confirm=0):
    return use(a,'Table',HatcherTable=1,HatcherShare=0,ConfirmShare=confirm)


def meanwhile(a,box,fn):
    a.s.on_box=lambda name: fn() if name==G+box else None


class Clarity(unittest.TestCase):
    def test_explicit_payment_is_once_only_and_neither_lie_nor_cargo_recovery(self):
        a=visit(self);shown=share(a)
        self.assertEqual(shown,['HatcherTable','HatcherShare','ConfirmShare','NoteSharePaid'])
        self.assertEqual(a.asked['caps'],1);self.assertEqual(a.g('Outcome'),44)
        self.assertEqual(a.s.player.inventory.get(a.caps,0)-a.caps_before,200)
        self.assertEqual(a.g('GrainHome'),0);self.assertEqual(a.g('GrainSold'),0)
        self.assertFalse(a.rules.vars['lietold']);self.assertNotIn(46,a.road.done)
        self.assertNotIn('ConfirmShare',share(a));self.assertEqual(a.asked['caps'],1)

    def test_cancel_invalid_confirmation_never_pays_claims_or_stages_and_retry_works(self):
        for pick in (1,-1,7):
            with self.subTest(button=pick):
                a=visit(self)
                if pick<0 or pick>1:a.box_returns(G+'ConfirmShare',pick)
                shown=share(a,pick);a.box_returns(None,None)
                self.assertEqual(shown,['HatcherTable','HatcherShare','ConfirmShare'])
                self.assertEqual(a.asked['caps'],0);self.assertEqual(a.g('Outcome'),0)
                self.assertNotIn(44,a.road.done);self.assertEqual(a.rules.vars['claim'],0)
                self.assertFalse(a.walk.vars['talking'])
                self.assertIn('NoteSharePaid',share(a));self.assertEqual(a.asked['caps'],1)

    def test_stale_context_after_each_payment_page_never_transfers(self):
        for box in ('HatcherShare','ConfirmShare'):
            for mutation in ('dead','combat','disabled','missing','replaced','distant','player_dead','claim'):
                with self.subTest(page=box,mutation=mutation):
                    a=visit(self);h=a.who['hatcher'];alias=a.walk.props['alias_hatcher']
                    def alter():
                        if mutation=='dead':h.dead=True
                        elif mutation=='combat':h.combat_target=a.s.player
                        elif mutation=='disabled':h.disabled=True
                        elif mutation=='missing':alias.ref=None
                        elif mutation=='replaced':alias.ref=a.who['crew1']
                        elif mutation=='distant':h.pos=(99999,99999,0)
                        elif mutation=='player_dead':a.s.player.dead=True
                        else:a.rules.vars['claim']=43
                    meanwhile(a,box,alter);shown=share(a);a.s.on_box=None
                    self.assertEqual(a.asked['caps'],0);self.assertNotIn(44,a.road.done)
                    self.assertNotIn('NoteSharePaid',shown);self.assertFalse(a.walk.vars['talking'])
                    if box=='HatcherShare':self.assertNotIn('ConfirmShare',shown)

    def test_lie_is_separate_explicit_and_reply_commit_is_separate(self):
        a=visit(self);share(a)
        self.assertEqual(use(a,'Opal',AskLie=1),['AskLie'])
        self.assertFalse(a.rules.vars['lietold']);self.assertEqual(a.g('GrainSold'),0)
        a.box_returns(G+'OpalAfterShare',-1)
        self.assertEqual(use(a,'Opal',AskLie=0),['AskLie','OpalAfterShare'])
        a.box_returns(None,None)
        self.assertTrue(a.rules.vars['lietold']);self.assertEqual(a.g('GrainSold'),1)
        self.assertFalse(a.rules.vars['lieheard']);self.assertNotIn(46,a.road.done)
        self.assertIn('OpalAfterShare',use(a,'Opal'));self.assertIn(46,a.road.done)
        self.assertEqual(a.asked['caps'],1)

    def test_stale_opal_or_player_closes_lie_without_commit(self):
        for mutation in ('dead','combat','missing','replaced','distant','player_dead'):
            with self.subTest(mutation=mutation):
                a=visit(self);share(a)
                def alter():
                    if mutation=='dead':a.who['opal'].dead=True
                    elif mutation=='combat':a.who['opal'].combat_target=a.s.player
                    elif mutation=='missing':a.walk.props['alias_opal'].ref=None
                    elif mutation=='replaced':a.walk.props['alias_opal'].ref=a.who['rafferty']
                    elif mutation=='distant':a.who['opal'].pos=(99999,99999,0)
                    else:a.s.player.dead=True
                meanwhile(a,'AskLie',alter)
                self.assertEqual(use(a,'Opal',AskLie=0),['AskLie'])
                self.assertFalse(a.rules.vars['lietold']);self.assertEqual(a.g('GrainSold'),0)
                self.assertNotIn(46,a.road.done);self.assertEqual(a.asked['caps'],1)

    def test_arrival_is_initial_only_and_label_updates_after_paid_route(self):
        a=visit(self,False)
        self.assertEqual(use(a,'MercyTravel',AskTravel=0),['AskTravel','ArrivalBrief'])
        self.assertEqual(a.road.done,[]);a.press(R+'LandingSight',enter=True)
        self.assertEqual(use(a,'LabelLanding'),['LabelLanding'])
        share(a);self.assertEqual(use(a,'LabelLanding'),['LabelShareHeld'])
        self.assertEqual(use(a,'CargoLashed'),['LabelShareHeld'])
        use(a,'Exit',AskLeaveResolved=0)
        self.assertEqual(use(a,'MercyTravel',AskTravelAgain=0),['AskTravelAgain'])
        self.assertEqual(use(a,'LabelLanding'),['LabelShareHeld'])

    def test_goal_and_stakes_are_information_not_route_consent(self):
        a=visit(self)
        self.assertEqual(use(a,'Opal',OpalFirst=0),['OpalFirst','OpalWants','Goal','Stakes'])
        self.assertIn(20,a.road.done);self.assertEqual(a.g('Outcome'),0)
        self.assertEqual(a.asked['caps'],0);self.assertEqual(a.g('GrainHome'),0)
        self.assertEqual(use(a,'Opal'),['OpalDefault'])

    def test_goal_cancel_or_stale_actor_does_not_show_later_stakes(self):
        for mode in ('cancel','dead','combat','player_dead'):
            with self.subTest(mode=mode):
                a=visit(self)
                if mode=='cancel':a.box_returns(G+'Goal',-1)
                else:
                    def alter():
                        if mode=='dead':a.who['opal'].dead=True
                        elif mode=='combat':a.who['opal'].combat_target=a.s.player
                        else:a.s.player.dead=True
                    meanwhile(a,'Goal',alter)
                self.assertNotIn('Stakes',use(a,'Opal',OpalFirst=0))
                self.assertEqual(a.g('Outcome'),0);self.assertFalse(a.walk.vars['talking'])

    def test_no_initial_ghost_task_when_opal_unavailable(self):
        a=visit(self,False);a.who['opal'].dead=True
        self.assertNotIn('ArrivalBrief',use(a,'MercyTravel',AskTravel=0))
        self.assertEqual(use(a,'LabelLanding'),['LabelLandingLayout'])

    def test_missing_pilot_gets_neutral_layout_not_a_direction_to_speak_to_him(self):
        a=visit(self);a.who['rafferty'].dead=True  # SEEDED unavailable participant
        self.assertEqual(use(a,'LabelLanding'),['LabelLandingLayout'])
        shown=use(a,'Opal',OpalFirst=0)
        self.assertEqual(shown,['OpalFirst','OpalWants','Goal','Stakes'])
        msgs={m['EditorId']:m for m in json.loads(PLUGIN.read_text())['Messages']}
        self.assertNotIn('with Rafferty',msgs[G+'Goal']['Text'])

    def test_failed_outward_move_shows_no_arrival_claim_and_later_travel_recovers(self):
        a=visit(self,False);old=a.s.n_objectreference_moveto
        def refuse_player(ref,ctx,*args):
            if ref is a.s.player:return None  # SEEDED failed native movement
            return old(ref,ctx,*args)
        a.s.n_objectreference_moveto=refuse_player
        self.assertEqual(use(a,'MercyTravel',AskTravel=0),['AskTravel'])
        self.assertFalse(a.walk.vars['arrivalbriefread']);self.assertEqual(a.road.done,[])
        a.s.n_objectreference_moveto=old
        self.assertEqual(use(a,'MercyTravel',AskTravel=0),['AskTravel','ArrivalBrief'])

    def test_cancelled_arrival_never_forces_landing_stage_and_does_not_overlap_use(self):
        a=visit(self,False);a.box_returns(G+'ArrivalBrief',-1)
        meanwhile(a,'ArrivalBrief',lambda: a.s.press_activate(R+'Table'))
        self.assertEqual(use(a,'MercyTravel',AskTravel=0),['AskTravel','ArrivalBrief'])
        self.assertEqual(a.road.done,[]);self.assertFalse(a.walk.vars['arrivalbriefread'])
        self.assertFalse(a.walk.vars['talking']);self.assertEqual(a.asked['caps'],0)

    def test_stale_judgment_confirmation_closes_without_transfer_or_later_notice(self):
        for choice,box in ((0,'ConfirmHang'),(1,'ConfirmCustody'),(2,'ConfirmRelease')):
            for who in ('hatcher','player'):
                with self.subTest(verdict=box,who=who):
                    a=visit(self);a.s.player_values['Charisma']=9.0
                    def alter():
                        if who=='player':a.s.player.dead=True
                        else:a.who['hatcher'].combat_target=a.s.player
                    meanwhile(a,box,alter)
                    self.assertEqual(use(a,'Table',HatcherTable=0,CardStakes=0,HatcherLost=choice,**{box:0}),['HatcherTable','CardStakes','HatcherLost',box])
                    self.assertEqual(a.g('Hatcher'),0);self.assertNotIn(60,a.road.done);self.assertNotIn(61,a.road.done)
                    self.assertFalse(a.who['hatcher'].dead);self.assertFalse(a.walk.vars['talking'])

    def test_card_and_judgment_have_local_confirmation_and_cancel_recovers(self):
        a=visit(self);a.s.player_values['Charisma']=9.0
        self.assertEqual(use(a,'Table',HatcherTable=0,CardStakes=1),['HatcherTable','CardStakes'])
        self.assertNotIn(41,a.road.done);self.assertNotIn(45,a.road.done)
        self.assertEqual(use(a,'Table',HatcherTable=0,CardStakes=0,HatcherLost=0,ConfirmHang=1),['HatcherTable','CardStakes','HatcherLost','ConfirmHang'])
        self.assertIn(41,a.road.done);self.assertFalse(a.who['hatcher'].dead)
        self.assertNotIn(60,a.road.done)
        self.assertEqual(use(a,'Table',HatcherLost=2,ConfirmRelease=0),['HatcherLost','ConfirmRelease'])
        self.assertEqual(a.g('Hatcher'),1);self.assertFalse(a.who['hatcher'].dead)

    def test_all_current_technical_messages_are_short_readable_and_explicit(self):
        d=json.loads(PLUGIN.read_text());msgs={m['EditorId']:m for m in d['Messages']}
        for name,m in msgs.items():
            if name.startswith(G):
                self.assertLessEqual(len(m['Text']),240,name)
                self.assertLessEqual(len(m['Buttons']),4,name)
                for button in m['Buttons']:self.assertLessEqual(len(button['Text']),48,name)
        self.assertIn('NOT the grain barge',msgs[G+'ArrivalBrief']['Text'])
        self.assertIn('200 caps',msgs[G+'ConfirmShare']['Text'])
        self.assertEqual(msgs[G+'AskLie']['Buttons'][0]['Text'],'[Lie] Say the Chute took it')
        self.assertIn('exact death toll',msgs[G+'NoteFireScene']['Text'])
