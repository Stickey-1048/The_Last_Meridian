"""Actual Red Hollow PSC/controller on synthetic engine, not native hit/geometry proof.
Opening is played using the established MQ01 driver. Failures/deaths/raw modal
results below are explicitly seeded adverse native responses, never accepted game facts.
"""
import json
import unittest
from test_act1 import Person
from test_sim import PLUGIN,SCRIPTS
SCRIPTS_NOW=SCRIPTS
from sim import Form
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"logic_model"))
from red_hollow_model import Observed

P = 'TLM_MSG_RH_'
R = 'TLM_REF_RH_'


class Hollow:
    def __init__(self, test, travel=True):
        self.t = test
        self.p = Person(test,scripts=SCRIPTS_NOW)
        self.s = self.p.s
        self.p.press('Dispatch', events=['take_dispatch'])
        self.p.to_town()
        self.p.hand_over('DebriefMissed')
        self.q = self.s.quests['TLM_MQ02C']
        self.w = self.s.quests['TLM_RH']
        self.rules = self.q.scripts[0]
        self.walk = self.w.scripts[0]
        self.messages = {m['EditorId']:m for m in json.loads(PLUGIN.read_text())['Messages']}
        self.calls = []
        self.refuse = set()
        self.before = {}
        self.raw = {}
        for native in ('moveto','enable','disable','additem','removeitem'):
            name = 'n_objectreference_' + native
            old = getattr(self.s,name)
            def wrapped(ref,context,*args,kind=native,fn=old):
                key=(kind,self.s._whom(ref))
                self.calls.append(key)
                if key in self.before:self.before[key]()
                if key in self.refuse:return None
                return fn(ref,context,*args)
            setattr(self.s,name,wrapped)
        oldshow = self.s.n_message_show
        def show(m,context,*args):
            if m.editor_id in self.raw:
                self.s.messages_shown.append(m.editor_id)
                if self.s.on_box:self.s.on_box(m.editor_id)
                return self.raw[m.editor_id]
            return oldshow(m,context,*args)
        self.s.n_message_show=show
        if travel:self.use('MercyTravel',Travel=0)

    def ref(self,name):return self.s.placed[R+name]
    def v(self,name):return self.rules.vars[name.lower()]
    def g(self,name):return self.s.get_global('TLM_G_MQ02C_'+name)
    def wait(self,seconds=2):self.s.run(self.s.now+seconds)
    def pos(self,name):self.s.walk_to(R+name)
    def answer(self,**choices):
        answers={}
        for name,choice in choices.items():
            if name in ('Travel','StageTravel','Descend','Rescue','Resolve','Blast','Seal','Final','Clock','NoOperator','NoWarning','Court','Watch','Drop','Referral','Receipt','Report','Status','Fine','HoistBelow','Knocking','Lamp','Silver','Exit','End','ReportFacts','ReportEvidence','ReportLamp','Prisoner','NoTranscript','Rope','PendingRescue'):
                answers[P+name]=[choice]
            else:
                pages=sorted((mid for mid in self.messages if mid.startswith(P+'S_'+name+'_')),key=lambda x:int(x.rsplit('_',1)[1]))
                self.t.assertTrue(pages,name)
                answers.update({mid:[choice if i==len(pages)-1 else 0] for i,mid in enumerate(pages)})
        self.s.answers=answers
    def use(self,name,**choices):
        self.answer(**choices);self.pos(name);self.s.press_activate(R+name);self.wait()
        self.t.assertEqual([x for x in self.s.papyrus_log if x.startswith('error')],[])
        self.compare_oracle()
    def mouth(self):self.use('ToMouth',StageTravel=0)
    def listen(self):self.use('Knocking',Knocking=0)
    def warning(self):self.use('Roark',roark_mouth=0,roark_deadline_warning=0,Clock=0)
    def below(self,warn=False):
        self.mouth();self.listen()
        if warn:self.warning()
        self.use('CageControl',**({'Descend':0} if warn else {'NoWarning':0,'Descend':0}))
        self.use('Roster')
    def rescue(self):self.use('BelowControl',HoistBelow=0,Rescue=0)
    def finish57(self):self.use('Resolve',Resolve=0)
    def exit(self):self.use('Exit',Exit=0,End=0)
    def return_report(self,known=False):
        self.exit();self.s.walk_to('TLM_REF_A1_Pritchard')
        self.answer(Report=0,**{('pritchard_hears_pike_after_fair' if known else 'pritchard_hears_pike_after_fair_unknown'):0},ReportFacts=0,ReportEvidence=0,ReportLamp=0)
        self.s.press_activate('TLM_REF_A1_Pritchard');self.wait()
    def shoot(self,projectile=True,attacker=None,bash=False):
        self.pos('Watch')
        self.s.hit_event(self.ref('Rope'),attacker or self.s.player,projectile=Form('SyntheticProjectile','Projectile') if projectile else None,bash=bash)
        self.wait()
    def die(self,name,by_player=False):
        actor=self.ref(name);actor.protected_override=False
        self.s.n_actor_kill(actor,None,self.s.player if by_player else None);self.wait()
    def compare_oracle(self):
        prisoner=self.walk.props['alias_condemned'].ref
        fates=[self.rules.vars['minerfates'][i] for i in range(11)] if self.rules.vars['minerfates'] else [0]*11
        o=Observed(int(self.g('Court')),int(self.g('Mine')),int(self.g('Survivors')),int(self.g('ObservedDeaths')),int(self.g('Entombed')),bool(self.v('shiftEverSafe')),bool(self.v('pactAcknowledged')),bool(self.v('innerClosed')),bool(self.v('mouthClosed')),bool(self.v('playerOrdered')),int(self.g('MinePending')),all(f in (3,4) for f in fates),bool(self.v('receiptGiven')),bool(self.v('feePaid')),bool(prisoner and prisoner.dead))
        self.t.assertEqual(o.problems(),[],o)
    def snapshot(self):
        return tuple(self.g(k) for k in ('Court','Mine','Survivors','ObservedDeaths','Entombed','ShiftSaved','QuillShamed','Reported'))


class TravelCourt(unittest.TestCase):
    def test_explicit_travel_cancel_and_real_prisoner(self):
        a=Hollow(self,False);lead=a.s.placed['TLM_REF_A1_Dunmore'];old=lead
        a.use('MercyTravel',Travel=1);self.assertNotIn(10,a.q.done);self.assertTrue(a.ref('Quill').disabled)
        a.use('MercyTravel',Travel=0);self.assertIn(10,a.q.done)
        self.assertIs(next(x for x in a.w.aliases.values() if x.name=='Condemned').ref,old);self.assertFalse(old.dead)
        self.assertIs(next(x for x in a.s.quests['TLM_MQ01'].aliases.values() if x.name=='CutterLead').ref,old)
    def test_bypass_never_executes_and_mine_stays_open(self):
        a=Hollow(self);a.use('Bypass');self.assertEqual(a.g('Court'),1);a.mouth();a.wait(1000)
        self.assertFalse(next(x for x in a.w.aliases.values() if x.name=='Condemned').ref.dead);self.assertEqual(a.g('Mine'),0)
    def test_only_registered_player_projectile_releases(self):
        a=Hollow(self);a.use('Rope',Rope=0);self.assertEqual(a.g('Court'),0)
        a.shoot(False);self.assertEqual(a.g('Court'),0)
        a.shoot(True,bash=True);self.assertEqual(a.g('Court'),0)
        a.shoot(True,attacker=a.ref('Quill'));self.assertEqual(a.g('Court'),0)
        a.shoot();self.assertEqual(a.g('Court'),11);self.assertTrue(a.ref('Rope').disabled)
        self.assertEqual(a.g('RopeShot'),0);self.assertEqual(a.g('NeckOwed'),1)
        a.use('CourtRecord',Court=2,Fine=0);self.assertEqual(a.g('RopeShot'),1)
    def test_rope_partial_move_recovers_without_another_hit(self):
        a=Hollow(self);who=a.s._whom(next(x for x in a.w.aliases.values() if x.name=='Condemned').ref);a.refuse.add(('moveto',who))
        a.shoot();self.assertEqual(a.g('Court'),0);self.assertEqual(a.v('courtIntent'),11)
        a.refuse.clear();a.use('CourtRecord');self.assertEqual(a.g('Court'),11)
    def test_fine_actual_transfer_receipt_and_no_double_charge(self):
        a=Hollow(self);a.s.player.inventory[a.p.caps]=100
        a.use('Quill',quill_court=0,quill_fine=0,Receipt=0)
        self.assertEqual(a.g('Court'),12);self.assertEqual(a.p.has(a.p.caps),40)
        self.assertEqual(a.ref('TollBox').inventory.get(a.p.caps),60)
        self.assertEqual(a.p.has('TLM_MISC_RH_Receipt'),1)
        a.use('Quill',Status=0);self.assertEqual(a.p.has(a.p.caps),40)
    def test_refused_fee_does_not_release_or_repeat_transfer(self):
        a=Hollow(self);a.s.player.inventory[a.p.caps]=100;key=('removeitem',a.s._whom(a.s.player));a.refuse.add(key)
        a.use('Quill',quill_court=0,quill_fine=0);self.assertEqual(a.g('Court'),0)
        a.refuse.clear();a.use('Quill');self.assertEqual(a.g('Court'),0)
        self.assertEqual(a.calls.count(key),1);self.assertEqual(a.p.has(a.p.caps),100)
    def test_stale_fee_ack_keeps_paid_intent_and_later_valid_release(self):
        a=Hollow(self);a.s.player.inventory[a.p.caps]=100
        a.s.on_box=lambda mid:setattr(a.s.player,'dead',True) if mid==P+'Receipt' else None
        a.use('Quill',quill_court=0,quill_fine=0,Receipt=0);self.assertEqual(a.g('Court'),0)
        a.s.player.dead=False;a.s.on_box=None
        a.use('Quill',Receipt=0);self.assertEqual(a.g('Court'),12);self.assertEqual(a.p.has(a.p.caps),40)
    def test_toll_is_two_caps_separate_once_only(self):
        a=Hollow(self);a.s.player.inventory[a.p.caps]=100;a.use('TollBox');a.use('TollBox')
        self.assertEqual(a.p.has(a.p.caps),98);self.assertEqual(a.g('Court'),0)
    def test_no_prisoner_never_spawns_or_resurrects(self):
        a=Hollow(self,False)
        for alias in a.s.quests['TLM_MQ01'].aliases.values():
            if alias.name in ('CutterLead','CutterA','CutterB','CutterC'):alias.ref.dead=True
        a.use('MercyTravel',Travel=0);self.assertIsNone(next(x for x in a.w.aliases.values() if x.name=='Condemned').ref);a.use('Bypass');a.below();a.rescue();a.finish57();self.assertEqual(a.g('Mine'),57)


class MineRoutes(unittest.TestCase):
    def test_normal_unpledged_rescue_requires_explicit57_then_report(self):
        a=Hollow(self);a.below();self.assertEqual(len({id(a.ref('Miner%02d'%i)) for i in range(1,12)}),11)
        a.rescue();self.assertEqual(a.g('ShiftSaved'),1);self.assertEqual(a.g('Mine'),0)
        self.assertEqual(a.g('Survivors'),11);a.finish57();self.assertEqual(a.g('Mine'),57)
        a.return_report();self.assertEqual(a.g('Reported'),1)
    def test_pledge_plus_physical_rescue51_not_choice_only(self):
        a=Hollow(self);a.below();a.use('Gallery',StageTravel=0)
        a.use('Dorn',dorn_door=0,dorn_terms=0,dorn_sworn=0)
        self.assertEqual(a.g('HollowLine'),1);self.assertEqual(a.g('Mine'),0)
        a.use('FromGallery',StageTravel=0);a.rescue();self.assertEqual(a.g('Mine'),51)
    def test_break_plan_survives_rescue_and_only_actual_collapse52(self):
        a=Hollow(self);a.below();a.use('Gallery',StageTravel=0);a.use('Dorn',dorn_door=2)
        a.use('FromGallery',StageTravel=0);a.rescue();self.assertEqual(a.g('Mine'),0)
        a.use('CageControl',Descend=0);a.use('BreakControl',Blast=0)
        self.assertEqual(a.g('Mine'),52);self.assertTrue(a.ref('BreakOpen').disabled);self.assertFalse(a.ref('BreakClosed').disabled)
    def test_informed_player_order53_is_not_timeout_and_not_corpse_count(self):
        a=Hollow(self);a.mouth();a.listen();a.warning();a.use('FiringControl',Seal=0)
        self.assertEqual(a.g('Mine'),53);self.assertTrue(a.v('playerOrdered'))
        self.assertEqual(a.g('Entombed'),11);self.assertEqual(a.g('ObservedDeaths'),0)
        self.assertTrue(all(not a.ref('Miner%02d'%i).dead and not a.ref('Miner%02d'%i).disabled for i in range(1,12)))
    def test_questions_do_not_arm_and_actual_warned_timeout56(self):
        a=Hollow(self);a.mouth();a.listen();a.use('Roark',roark_mouth=1,roark_why=0)
        self.assertEqual(a.g('DeadlineArmed'),0);a.warning();a.answer(Final=0);a.wait(605)
        self.assertEqual(a.g('Mine'),56);self.assertFalse(a.v('playerOrdered'));self.assertEqual(a.g('ObservedDeaths'),0)
    def test_observed_casualty_survivors_safe58_never_full_rescue(self):
        a=Hollow(self);a.below();a.die('Miner03',True);a.rescue();self.assertEqual(a.g('Mine'),0)
        self.assertEqual(a.g('Survivors'),10);self.assertEqual(a.g('ObservedDeaths'),1);self.assertEqual(a.g('ShiftSaved'),0)
        a.use('Resolve',Resolve=2);self.assertEqual(a.g('Mine'),58);self.assertNotIn(57,a.q.done)
    def test_partial_batch_retains_arrivals_no_timeout_then_retries(self):
        a=Hollow(self);a.below(True);key=('moveto',a.s._whom(a.ref('Miner06')));a.refuse.add(key)
        a.rescue();self.assertEqual(a.g('MinePending'),2);self.assertEqual(a.g('Mine'),0)
        first=a.ref('Miner01').pos;a.wait(700);self.assertEqual(a.g('Mine'),0)
        a.refuse.clear();a.use('BelowControl',HoistBelow=0,Rescue=0);self.assertEqual(a.g('Survivors'),11)
        self.assertNotEqual(first,a.ref('Miner01').pos);self.assertEqual(a.g('MinePending'),0)
    def test_missing_or_disabled_miner_is_not_death_or_success(self):
        for missing in (False,True):
            a=Hollow(self);a.below()
            if missing:next(x for x in a.q.aliases.values() if x.name=='Miner07').ref=None
            else:a.ref('Miner07').disabled=True
            a.rescue();self.assertEqual(a.g('ShiftSaved'),0);self.assertEqual(a.g('ObservedDeaths'),0);self.assertEqual(a.g('MinePending'),0 if missing else 2)
    def test_dead_roark_both_bypass_operator_and_rescue_remain_available(self):
        a=Hollow(self);a.mouth();a.listen();a.die('Roark');a.die('Blevins')
        a.use('CageControl',NoOperator=0,Descend=0);a.use('Roster');a.rescue();a.finish57();self.assertEqual(a.g('Mine'),57);self.assertEqual(a.g('DeadlineArmed'),0)
    def test_lamp_origins_and_silver_are_separate(self):
        a=Hollow(self);a.mouth();a.use('CotLamp',Lamp=0);self.assertEqual(a.v('lampSource'),2)
        self.assertEqual(a.g('SilverMine'),0);self.assertFalse(any('dorn_lamp' in m for m in a.s.messages_shown))
        a.use('Silver',Silver=0);self.assertEqual(a.g('SilverMine'),1)
        a.s.player.inventory[a.s.forms['TLM_MISC_RH_Lamp']]=0;a.wait();self.assertEqual(a.g('LampTaken'),0)


class AdverseContexts(unittest.TestCase):
    def test_all_menus_absence_and_load_gap_pause_deadline(self):
        a=Hollow(self);a.mouth();a.listen();a.warning();a.wait(3)
        left=a.v('deadlineSeconds');a.s.menu_mode=True;a.wait(900);self.assertEqual(a.v('deadlineSeconds'),left)
        a.s.menu_mode=False;a.pos('MercyReturn');a.wait(900);self.assertEqual(a.v('deadlineSeconds'),left)
        a.pos('MouthArrival');a.s.now+=5000;a.s.ref_event(a.s.player,'OnPlayerLoadGame',[],0);a.wait(2)
        self.assertGreaterEqual(a.v('deadlineSeconds'),left-2.1);self.assertEqual(a.g('Mine'),0)
    def test_cancel_or_unsupported_final_call_blocks_until_renewed_warning(self):
        for raw in (-1,7,1):
            a=Hollow(self);a.mouth();a.listen();a.warning();a.raw[P+'Final']=raw;a.wait(605)
            self.assertEqual(a.g('Mine'),0);self.assertEqual(a.g('DeadlineArmed'),0)
            a.raw.clear();a.wait(900);self.assertEqual(a.g('Mine'),0)
            a.warning();self.assertEqual(a.g('DeadlineArmed'),1)
            self.assertGreater(a.v('deadlineSeconds'),0)
    def test_operator_death_or_combat_during_final_ack_does_not_fire(self):
        for dead in (True,False):
            a=Hollow(self);a.mouth();a.listen();a.warning();a.answer(Final=0)
            def hook(mid):
                if mid==P+'Final':
                    if dead:a.ref('Blevins').dead=True
                    else:setattr(a.ref('Blevins'),'combat_target',a.s.player)
            a.s.on_box=hook;a.wait(605);self.assertEqual(a.g('Mine'),0);self.assertFalse(a.ref('MouthOpen').disabled)
    def test_cancelled_or_dead_player_rescue_ack_moves_nobody(self):
        for raw in (-1,7):
            a=Hollow(self);a.below();a.raw[P+'Rescue']=raw;a.use('BelowControl',HoistBelow=0)
            self.assertEqual(a.g('MinePending'),0);self.assertEqual(a.g('ShiftSaved'),0)
        a=Hollow(self);a.below();a.s.on_box=lambda m:setattr(a.s.player,'dead',True) if m==P+'Rescue' else None
        a.rescue();self.assertEqual(a.g('MinePending'),0);self.assertEqual(a.g('ShiftSaved'),0)
    def test_refused_collapse_is_pending_and_recoverable(self):
        a=Hollow(self);a.below();a.rescue();a.use('Resolve',Resolve=1);a.use('CageControl',Descend=0)
        key=('disable',a.s._whom(a.ref('BreakOpen')));a.refuse.add(key);a.use('BreakControl',Blast=0)
        self.assertEqual(a.g('Mine'),0);self.assertEqual(a.g('MinePending'),3)
        a.refuse.clear();a.use('BreakControl',Blast=0);self.assertEqual(a.g('Mine'),52)

class CustodyAndReports(unittest.TestCase):
    def held_copy(self,a):
        # Existing helper delivers the actual same 2298 book, not a new quest identity.
        a.s.walk_to('TLM_REF_A1_Pritchard')
        a.s.answers={'TLM_MSG_MB_Hub':[2],'TLM_MSG_MB_Pike':[0],'TLM_MSG_MB_Docket':[0]}
        a.s.press_activate('TLM_REF_A1_Pritchard');a.wait()
        self.assertEqual(a.p.has('TLM_BOOK_Docket2298'),1)
    def test_existing_copy_and_adjournment_do_not_earn_referral_until_observed(self):
        a=Hollow(self,False);self.held_copy(a);a.use('MercyTravel',Travel=0)
        self.assertIn(16,a.q.done);a.use('Quill',quill_court_docket=1,quill_shamed=0,Referral=1)
        self.assertEqual(a.g('Court'),13);self.assertEqual(a.g('QuillShamed'),0)
        self.assertFalse(next(x for x in a.w.aliases.values() if x.name=='Condemned').ref.dead)
        a.use('Quill',Referral=0);self.assertEqual(a.g('QuillShamed'),1)
        self.assertEqual(a.p.has('TLM_BOOK_Docket2298'),1)
    def test_drop_copy_during_ack_never_adjourns_or_refills(self):
        a=Hollow(self,False);self.held_copy(a);a.use('MercyTravel',Travel=0)
        a.s.on_box=lambda mid:a.s.player.inventory.update({a.s.forms['TLM_BOOK_Docket2298']:0}) if 'S_quill_shamed_' in mid else None
        a.use('Quill',quill_court_docket=1,quill_shamed=0)
        self.assertEqual(a.g('Court'),0);self.assertEqual(a.p.has('TLM_BOOK_Docket2298'),0);self.assertIn(16,a.q.done)
        self.assertEqual(a.g('Docket2298Held'),0)
    def test_testimony_is_established_before_record_can_be_read(self):
        a=Hollow(self);a.use('Transcript',NoTranscript=0);self.assertEqual(a.g('SilverRoad'),0)
        a.s.answers={};prisoner=next(x for x in a.w.aliases.values() if x.name=='Condemned').ref
        a.s.player.pos=prisoner.pos;a.s.answers={P+'S_dunmore_rope_missed_1':[0]}
        # Missed line is split at the exact accepted word boundary.
        pages=[m for m in a.messages if m.startswith(P+'S_dunmore_rope_missed_')]
        a.s.answers={m:[0] for m in pages};a.s.press_activate(a.s._whom(prisoner));a.wait()
        self.assertEqual(a.g('SilverRoad'),1)
        a.pos('Transcript');a.s.answers={m:[0] for m in a.messages if m.startswith(P+'T_dunmore_tells_')}
        a.s.press_activate(R+'Transcript');a.wait();self.assertIn(15,a.q.done)
    def test_acknowledged_local_execution_is_actual_death(self):
        a=Hollow(self);a.use('Watch',Court=1,Watch=0);a.answer(Drop=0);a.wait(18)
        self.assertEqual(a.g('Court'),14);self.assertTrue(next(x for x in a.w.aliases.values() if x.name=='Condemned').ref.dead)
        self.assertFalse(any('quill_after_drop' in m for m in a.s.messages_shown))
    def test_declined_or_stale_execution_ack_does_not_kill(self):
        for raw in (-1,7,1):
            a=Hollow(self);a.use('Watch',Court=1,Watch=0);a.raw[P+'Drop']=raw;a.wait(18)
            self.assertEqual(a.g('Court'),0);self.assertFalse(next(x for x in a.w.aliases.values() if x.name=='Condemned').ref.dead)
    def test_report_each_detail_page_closes_on_invalid_or_participant_loss(self):
        for page in ('ReportFacts','ReportEvidence','ReportLamp'):
            for raw in (-1,7):
                a=Hollow(self);a.below();a.rescue();a.finish57();a.exit()
                a.s.walk_to('TLM_REF_A1_Pritchard');a.raw[P+page]=raw
                a.answer(Report=0,pritchard_hears_pike_after_fair_unknown=0,ReportFacts=0,ReportEvidence=0,ReportLamp=0)
                a.s.press_activate('TLM_REF_A1_Pritchard');a.wait()
                self.assertEqual(a.g('Reported'),0)
                shown=a.s.messages_shown;at=shown.index(P+page)
                self.assertFalse(any(m.startswith('TLM_MSG_MB_') for m in shown[at:]))
                order=['ReportFacts','ReportEvidence','ReportLamp'];self.assertFalse(any(P+x in shown[at+1:] for x in order[order.index(page)+1:]))
    def test_all_eleven_observed_dead_is_zero_survivor58(self):
        a=Hollow(self);a.below()
        for i in range(1,12):a.die('Miner%02d'%i)
        a.rescue();a.use('Resolve',Resolve=2)
        self.assertEqual(a.g('Mine'),58);self.assertEqual(a.g('ObservedDeaths'),11);self.assertEqual(a.g('Survivors'),0);self.assertEqual(a.g('ShiftSaved'),0)
    def test_death_before_finding_cohort_still_has_honest_adverse_exit(self):
        a=Hollow(self);a.mouth();a.listen();a.use('CageControl',NoWarning=0,Descend=0)
        a.die('Miner01');a.use('Roster');self.assertNotIn(45,a.q.done)
        a.rescue();a.use('Resolve',Resolve=2);self.assertEqual(a.g('Mine'),58)
    def test_stale_dorn_death_never_sworn_or_lamp_speech(self):
        a=Hollow(self);a.below();a.use('Gallery',StageTravel=0)
        a.s.on_box=lambda mid:setattr(a.ref('Dorn'),'dead',True) if 'S_dorn_terms_' in mid else None
        a.use('Dorn',dorn_door=0,dorn_terms=0);self.assertEqual(a.g('HollowLine'),0)
        self.assertFalse(any('dorn_sworn' in m for m in a.s.messages_shown))
    def test_player_dies_during_rescue_effect_stops_remaining_moves(self):
        a=Hollow(self);a.below();key=('moveto',a.s._whom(a.ref('Miner03')))
        a.before[key]=lambda:setattr(a.s.player,'dead',True)
        a.rescue();self.assertEqual(a.g('ShiftSaved'),0);self.assertEqual(a.g('MinePending'),2)
        self.assertNotIn(('moveto',a.s._whom(a.ref('Miner04'))),a.calls)
        a.s.player.dead=False;a.before.clear();a.rescue();self.assertEqual(a.g('Survivors'),11)


class FurtherRefusals(unittest.TestCase):
    def test_receipt_effect_refusal_never_releases_or_requests_a_second(self):
        a=Hollow(self);a.s.player.inventory[a.p.caps]=100
        key=('additem',a.s._whom(a.s.player));a.refuse.add(key)
        a.use('Quill',quill_court=0,quill_fine=0);self.assertEqual(a.g('Court'),0);self.assertEqual(a.p.has(a.p.caps),40)
        before=a.calls.count(key);a.refuse.clear();a.use('Quill');self.assertEqual(a.g('Court'),0);self.assertEqual(a.calls.count(key),before)
    def test_duplicate_cohort_is_neither_eleven_saved_nor_a_death(self):
        a=Hollow(self);a.below()
        aliases=a.q.aliases.values();six=next(x for x in aliases if x.name=='Miner06');seven=next(x for x in a.q.aliases.values() if x.name=='Miner07');seven.ref=six.ref
        a.rescue();self.assertEqual(a.g('ShiftSaved'),0);self.assertEqual(a.g('ObservedDeaths'),0)
    def test_incomplete_batch_cannot_resolve58_or_interleave_a_seal(self):
        a=Hollow(self);a.below(True);a.die('Miner02')
        a.refuse.add(('moveto',a.s._whom(a.ref('Miner09'))));a.rescue()
        # A source/native failure remains pending, even if a test walks back to another control.
        a.use('Resolve',Resolve=2);self.assertEqual(a.g('Mine'),0);self.assertEqual(a.g('MinePending'),2)
        a.use('FiringControl');self.assertEqual(a.g('Mine'),0)
    def test_four_cap_payment_is_observed_once_not_repeated(self):
        a=Hollow(self);a.s.player.inventory[a.p.caps]=20;a.shoot();a.use('CourtRecord',Court=2,Fine=0)
        a.use('CourtRecord',Court=2,Fine=1);a.use('CourtRecord',Court=2,Fine=1)
        self.assertEqual(a.p.has(a.p.caps),16);self.assertEqual(a.ref('TollBox').inventory.get(a.p.caps),4)
    def test_cancelled_execution_is_not_reoffered_without_new_watch(self):
        a=Hollow(self);a.use('Watch',Court=1,Watch=0);a.answer(Drop=1);a.wait(18)
        count=a.s.messages_shown.count(P+'Drop');a.s.answers={};a.wait(30)
        self.assertEqual(a.s.messages_shown.count(P+'Drop'),count);self.assertEqual(a.g('Court'),0)


class ActiveAreaAndLateEffects(unittest.TestCase):
    def test_unloaded_and_unlabelled_gaps_are_not_active_mine_time(self):
        a=Hollow(self);a.mouth();a.listen();a.warning()
        for pos in ((5200,256,16),(3500,4000,16),(8000,512,16)):
            a.s.player.pos=pos;left=a.v('deadlineSeconds');a.wait(700)
            self.assertEqual(a.v('deadlineSeconds'),left);self.assertEqual(a.g('Mine'),0)
    def test_delayed_lamp_is_observed_without_a_second_item_request(self):
        a=Hollow(self);a.mouth();key=('additem',a.s._whom(a.s.player));a.refuse.add(key)
        a.use('CotLamp',Lamp=0);self.assertNotIn(54,a.q.done);calls=a.calls.count(key)
        a.refuse.clear();a.s.player.inventory[a.s.forms['TLM_MISC_RH_Lamp']]=1
        a.use('CotLamp',Lamp=0);self.assertIn(54,a.q.done);self.assertEqual(a.calls.count(key),calls);self.assertTrue(a.ref('CotLamp').disabled)


class MissingCurrency(unittest.TestCase):
    def test_unbound_currency_never_pays_or_releases(self):
        a=Hollow(self);a.rules.props['caps']=None;a.s.player.inventory[a.p.caps]=100
        a.use('Quill',quill_court=0,quill_fine=0);self.assertEqual(a.g('Court'),0);self.assertEqual(a.p.has(a.p.caps),100)
        a.use('TollBox');self.assertEqual(a.p.has(a.p.caps),100)


class InterruptedFiring(unittest.TestCase):
    def test_lost_operator_during_effect_restores_uncommitted_displays_and_rescue(self):
        a=Hollow(self);a.mouth();a.listen();a.warning()
        key=('disable',a.s._whom(a.ref('MouthOpen')));a.before[key]=lambda:setattr(a.ref('Blevins'),'dead',True)
        a.use('FiringControl',Seal=0);self.assertEqual(a.g('Mine'),0);self.assertEqual(a.g('MinePending'),0)
        self.assertFalse(a.ref('MouthOpen').disabled);self.assertTrue(a.ref('MouthClosed').disabled)
        a.before.clear();a.use('CageControl',Descend=0);a.use('Roster');a.rescue();a.finish57();self.assertEqual(a.g('Mine'),57)
    def test_failed_safe_player_move_is_retried_from_below_with_new_ack(self):
        a=Hollow(self);a.below(True);key=('moveto',a.s._whom(a.s.player));a.refuse.add(key)
        # Expiry while below cannot fabricate a safe surface arrival.
        a.answer(Final=0);a.wait(605);self.assertEqual(a.g('Mine'),0);self.assertEqual(a.g('MinePending'),5)
        self.assertFalse(a.ref('MouthOpen').disabled);a.refuse.clear()
        a.use('BelowControl',Final=0);self.assertEqual(a.g('Mine'),56)
    def test_cancelled_persistent_firing_retry_leaves_rescue_available(self):
        a=Hollow(self);a.below(True);key=('moveto',a.s._whom(a.s.player));a.refuse.add(key);a.answer(Final=0);a.wait(605)
        a.refuse.clear();a.use('BelowControl',Final=1);self.assertEqual(a.g('Mine'),0);self.assertEqual(a.g('MinePending'),0)
        a.rescue();a.finish57();self.assertEqual(a.g('Mine'),57)


class ClosedBreak(unittest.TestCase):
    def test_actual_inner_break_prevents_gallery_travel_after52(self):
        a=Hollow(self);a.below();a.rescue();a.use('Resolve',Resolve=1);a.use('CageControl',Descend=0);a.use('BreakControl',Blast=0)
        self.assertEqual(a.g('Mine'),52);before=a.s.player.pos
        a.use('Gallery');self.assertNotEqual(a.s.player.pos,a.ref('GalleryArrival').pos)
        a.use('BelowControl',HoistBelow=1);self.assertEqual(a.s.player.pos,a.ref('CageSurface').pos)
