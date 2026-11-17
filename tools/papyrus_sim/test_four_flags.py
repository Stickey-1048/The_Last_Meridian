"""Four Flags actual PSC driven through ordinary synthetic activations.
Synthetic master, native hooks and supplied load states are source evidence;
none certifies an installed game, unique-item receipt or native cast return.
"""
import json
import unittest
from greenwater_player import Player
from test_sim import PLUGIN,SCRIPTS

P='TLM_MSG_FF_'
R='TLM_REF_FF_'
Q='TLM_MQ03'


class Fair:
    def __init__(self,t,scripts=SCRIPTS,enter=True,finish=True,delay=0):
        self.t=t;self.a=Player(t,scripts=scripts,travel=False,finish=finish);self.s=self.a.s
        self.q=self.s.quests[Q]
        self.rules=next(i for i in self.q.scripts if i.script.name=='TLM:MQ03Quest')
        self.walk=next(i for i in self.q.scripts if i.script.name=='TLM:FourFlagsWalk')
        self.messages={m['EditorId']:m for m in json.loads(PLUGIN.read_text())['Messages']}
        self.originals=[self.s.placed['TLM_REF_A1_'+n] for n in ('Pritchard','Talbot','Pike')]+[self.s.placed['TLM_REF_GW_Belden']]
        self.before=[(a.cell,tuple(a.pos),a.disabled,dict(a.inventory),a.dead,a.protected_override,a.essential_override) for a in self.originals]
        self.s.native_delay=delay
        if enter:self.enter()
    def v(self,key):return self.rules.vars[key.lower()]
    def use(self,part,**answers):
        self.s.answers={n:[0]*40 for n,m in self.messages.items() if n.startswith(P) and len(m['Buttons'])==1}
        self.s.answers.update({P+k:([v] if not isinstance(v,list) else v) for k,v in answers.items()})
        target=('TLM_REF_A1_'+part) if part in ('Pritchard','Talbot','Pike') else 'TLM_REF_GW_Belden' if part=='Belden' else R+part
        at=len(self.s.messages_shown);self.s.walk_to(target);self.s.press_activate(target);self.a.p.pause(120 if self.s.native_delay else 4)
        return [n.removeprefix(P) for n in self.s.messages_shown[at:]]
    def enter(self):return self.use('Entry',Entry=1,NoReport=0,Travel=0)
    def scene(self,choice=None,**answers):
        if choice is not None:answers['S_brigg_demand_1']=choice
        return self.use('Ready',Ready=0,Shot=0,**answers)
    def choose(self,choice,**answers):return self.use('Response',S_brigg_demand_1=choice,**answers)
    def read(self,public=False):return self.use('CaseControl',Case=2 if public else 0,Public=0,S_pritchard_case_1=1,Solo=0)
    def hook(self,page,fn):self.s.on_box=lambda name:fn() if name==P+page else None
    def load_inside_native(self):
        result=list(self.s.call(self.walk,self.walk.script.functions['loaded'],[]))
        self.t.assertEqual(result,[],'default synthetic load handler is nonlatent')
    def old_history(self):
        return ({n:f.value for n,f in self.s.forms.items() if n.startswith('TLM_G_')},
                {n:(tuple(q.done),dict(q.displayed),dict(q.completed_objectives),q.completed) for n,q in self.s.quests.items() if n not in (Q,'TLM_FF_Entry')})


class FourFlagsNormal(unittest.TestCase):
    def test_four_exact_faction_offers_do_not_choose_allegiance_or_start_scene(self):
        a=Fair(self);history=a.old_history()
        for part,node in (('Whitcomb','whitcomb_offer'),('Brigg','brigg_offer'),('Belden','belden_offer'),('Grey','grey_offer')):
            shown=a.use(part,**{n.removeprefix(P):0 for n in a.messages if n.startswith(P+'S_'+node+'_')})
            self.assertIn('S_'+node+'_1',shown)
            self.assertNotIn(40,a.q.done);self.assertEqual(a.v('response'),0)
        self.assertEqual(a.old_history(),history);self.assertEqual(a.q.done,[10])

    def test_original_talbot_full_quorum_concession_after_pritchard_death(self):
        a=Fair(self);a.originals[0].dead=True
        shown=a.scene(None,S_brigg_demand_talbot_1=2)
        self.assertIn('S_talbot_truce_1',shown)
        self.assertIn('S_brigg_truce_concession_talbot_1',shown)
        self.assertIn(43,a.q.done);self.assertNotIn(70,a.q.done)
        self.assertTrue(a.originals[0].dead);self.assertEqual(a.v('response'),43)

    def test_all_four_courses_and_original_returns_with_each_native_taking_a_frame(self):
        for choice,course in ((0,41),(1,42),(2,43),(3,44)):
            with self.subTest(course=course):
                a=Fair(self,delay=1.0/60.0);history=a.old_history()
                a.scene(choice,Occupation=0,OccupationSeen=0,Take=0)
                self.assertEqual(a.v('response'),course)
                self.assertEqual(70 in a.q.done,course!=43)
                a.read();self.assertIn(100,a.q.done)
                a.use('Exit',Exit=0);self.assertFalse(any(a.walk.vars['visitorpending']))
                self.assertEqual(a.old_history(),history)

    def test_explicit_no_report_arrival_preserves_old_history_and_original_cast(self):
        a=Fair(self,enter=False);before=a.old_history()
        shown=a.enter()
        self.assertEqual(shown,['Entry','NoReport','Travel','Layout','LayoutLimits'])
        self.assertEqual(a.v('entryBasis'),3);self.assertEqual(a.q.done,[10]);self.assertEqual(a.old_history(),before)
        self.assertFalse(a.s.quests['TLM_MQ02B'].running,'unvisited Greenwater must not start to obtain Belden')
        self.assertEqual(a.walk.vars['visitors'],a.originals)
        self.assertEqual(a.walk.vars['visitorwasdisabled'],[False,False,False,True])
        self.assertTrue(all(a.walk.vars['visitorstaged']))
        self.assertFalse(a.v('sceneArmed'));self.assertFalse(a.v('courierHeard'))

    def test_all_four_real_courses_and_solo_endpoint(self):
        for choice,course in ((0,41),(1,42),(2,43),(3,44)):
            with self.subTest(course=course):
                a=Fair(self);history=a.old_history()
                shown=a.scene(choice,Occupation=0,OccupationSeen=0,Take=0)
                self.assertEqual(a.v('response'),course,shown);self.assertIn(course,a.q.done)
                self.assertIn(40,a.q.done);self.assertIn(46,a.q.done)
                self.assertEqual(70 in a.q.done,course!=43)
                self.assertEqual(a.v('crowdSpared'),course==43)
                self.assertEqual(a.v('courierHeard'),course==42)
                self.assertFalse(a.s.placed[R+'Juno'].dead)
                if course==44:self.assertIs(a.s.placed[R+'OriginalCase'].container,a.s.player)
                if course==43:
                    self.assertIn('S_brigg_truce_concession_pritchard_1',shown)
                    self.assertIn('S_brigg_rifles_1',shown)
                a.read();self.assertIn(60,a.q.done);self.assertIn(100,a.q.done);self.assertNotIn(101,a.q.done)
                self.assertEqual(a.old_history(),history)

    def test_public_endpoint_requires_original_physical_delivery_and_exact_reaction(self):
        a=Fair(self);a.scene(0,Occupation=0,OccupationSeen=0)
        shown=a.read(public=True)
        self.assertIs(a.s.placed[R+'OriginalCase'].container,a.originals[0])
        self.assertIs(a.v('publicCustodian'),a.originals[0]);self.assertIn(100,a.q.done);self.assertIn(101,a.q.done)
        self.assertIn('S_pritchard_case_1',shown)

    def test_silver_inspection_and_original_transfer_are_separate_real_facts(self):
        a=Fair(self);a.scene(0,Occupation=0,OccupationSeen=0)
        shown=a.use('Firing',Silver=0,GiveSilver=1)
        self.assertIn(50,a.q.done);self.assertNotIn(51,a.q.done);self.assertTrue(a.v('silverInspected'))
        self.assertIsNone(a.s.placed[R+'OriginalSilver'].container);self.assertFalse(a.v('flintTalks'))
        self.assertNotIn('S_flint_roof_1',shown)
        a.use('Firing',GiveSilver=0,S_flint_roof_1=0)
        self.assertIn(51,a.q.done);self.assertTrue(a.v('flintTalks'))
        self.assertIs(a.s.placed[R+'OriginalSilver'].container,a.s.placed[R+'Flint'])

    def test_original_visit_returns_verified_location_state_without_quest_reset(self):
        a=Fair(self);history=a.old_history()
        shown=a.use('Exit',Exit=0)
        self.assertNotIn('ReturnsPending',shown)
        for actor,before in zip(a.originals,a.before):
            self.assertEqual((actor.cell,tuple(actor.pos),actor.disabled,dict(actor.inventory),actor.dead,actor.protected_override,actor.essential_override),before)
        self.assertFalse(any(a.walk.vars['visitorpending']));self.assertEqual(a.old_history(),history)


class FourFlagsEntryAndScene(unittest.TestCase):
    def test_entry_and_master_start_failures_have_no_stage_or_cast_effect_and_retry(self):
        for quest_name in ('TLM_FF_Entry',Q):
            for result in (False,True):
                with self.subTest(quest=quest_name,return_value=result):
                    a=Fair(self,enter=False);q=a.s.quests[quest_name];q.running=False
                    source=a.walk.vars['sourceowner'];old=a.s.n_quest_start
                    def fail_start(quest,context):
                        if quest is q:return result  # SEEDED refusal or true-without-running
                        return old(quest,context)
                    a.s.n_quest_start=fail_start
                    self.assertFalse(a.s.invoke('TLM_FF_Entry','OpenFrom',[source]))
                    self.assertFalse(q.running);self.assertEqual(a.q.done,[])
                    self.assertFalse(any(a.walk.vars['visitorpending']))
                    for actor,before in zip(a.originals,a.before):self.assertEqual((actor.cell,tuple(actor.pos),actor.disabled),before[:3])
                    a.s.n_quest_start=old
                    self.assertTrue(a.s.invoke('TLM_FF_Entry','OpenFrom',[source]))
                    a.enter();self.assertIn(10,a.q.done)

    def test_all_entry_paths_keep_completed_first_section_prerequisite(self):
        for choice in (0,1,2):
            with self.subTest(entry=choice):
                a=Fair(self,enter=False,finish=False);before=a.old_history()
                self.assertEqual(a.use('Entry',Entry=choice,NoReport=0,Travel=0),['Unavailable'])
                self.assertEqual(a.v('entryBasis'),0);self.assertEqual(a.q.done,[]);self.assertEqual(a.old_history(),before)

    def test_unreported_completed_road_asks_without_inventing_report(self):
        a=Fair(self,enter=False);a.a.travel();a.a.step_onto_landing();a.a.table(['share']);a.a.leave()
        self.assertEqual(a.a.g('Reported'),0);before=a.old_history()
        shown=a.use('Entry',Entry=0,NoReport=1)
        self.assertEqual(shown,['Entry','NoReport']);self.assertEqual(a.v('entryBasis'),0);self.assertEqual(a.old_history(),before)
        shown=a.use('Entry',Entry=0,NoReport=0,Travel=0)
        self.assertEqual(a.v('entryBasis'),2);self.assertIn('Travel',shown);self.assertEqual(a.old_history(),before)

    def test_actual_reported_road_and_dead_sheriff_handbill_remain_distinct(self):
        a=Fair(self,enter=False);a.a.travel();a.a.step_onto_landing();a.a.table(['share']);a.a.leave();a.a.report()
        before=a.old_history();shown=a.use('Entry',Entry=0,Travel=0)
        self.assertNotIn('NoReport',shown);self.assertEqual(a.v('entryBasis'),1);self.assertEqual(a.old_history(),before)
        b=Fair(self,enter=False);b.originals[0].dead=True  # SEEDED unavailable authority, no resurrection
        before=b.old_history();shown=b.use('Entry',Entry=2,Travel=0)
        self.assertEqual(b.v('entryBasis'),4);self.assertIn('D_fair_handbill_1',shown);self.assertEqual(b.old_history(),before)
        self.assertFalse(b.walk.vars['visitorpending'][0]);self.assertTrue(b.originals[0].dead)

    def test_readiness_cancel_does_not_encounter_shoot_kill_or_occupy(self):
        a=Fair(self);before=a.old_history()
        self.assertEqual(a.use('Ready',Ready=1),['Ready'])
        self.assertNotIn(40,a.q.done);self.assertNotIn(70,a.q.done);self.assertFalse(a.v('sceneArmed'))
        self.assertTrue(a.s.placed[R+'OriginalCase'].disabled);self.assertTrue(a.s.placed[R+'Juno'].disabled)
        self.assertFalse(a.s.placed[R+'Juno'].dead);self.assertEqual(a.old_history(),before)

    def test_actual_dead_juno_uses_dead_encounter_and_no_stay_option(self):
        a=Fair(self);a.s.placed[R+'Juno'].dead=True  # SEEDED already dead before readiness
        shown=a.scene(None,DeadCourier=0,S_brigg_demand_courier_dead_1=0,Occupation=0,OccupationSeen=0)
        self.assertIn('DeadCourier',shown);self.assertNotIn('Shot',shown)
        self.assertIn(40,a.q.done);self.assertIn(45,a.q.done);self.assertNotIn(46,a.q.done)
        self.assertEqual(a.v('response'),41);self.assertFalse(a.v('courierHeard'))
        self.assertTrue(a.s.placed[R+'Juno'].dead)

    def test_interrupted_original_courier_case_or_epoch_never_acknowledges_scene(self):
        for mutation in ('courier_rebound','case_rebound','courier_combat','player_dead','load','cancel'):
            with self.subTest(mutation=mutation):
                a=Fair(self)
                def alter():
                    if mutation=='courier_rebound':a.rules.props['cast'][8].ref=a.s.placed[R+'Grey']
                    elif mutation=='case_rebound':a.rules.props['alias_originalcase'].ref=a.s.placed[R+'OriginalSilver']
                    elif mutation=='courier_combat':a.s.placed[R+'Juno'].combat_target=a.s.player
                    elif mutation=='player_dead':a.s.player.dead=True
                    elif mutation=='load':a.s.ref_event(a.s.player,'OnPlayerLoadGame',[],0)
                a.hook('Shot',alter)
                if mutation=='cancel':a.use('Ready',Ready=0,Shot=1)
                else:a.scene(None)
                self.assertNotIn(40,a.q.done);self.assertNotIn(70,a.q.done);self.assertEqual(a.v('response'),0)
                self.assertFalse(a.s.placed[R+'Juno'].dead)


class FourFlagsResponseGuards(unittest.TestCase):
    def test_occupation_cancel_drops_only_uncommitted_course_and_retry_works(self):
        a=Fair(self);shown=a.scene(0,Occupation=1)
        self.assertIn('Occupation',shown);self.assertEqual(a.v('pendingCourse'),0)
        self.assertEqual(a.v('response'),0);self.assertNotIn(70,a.q.done);self.assertNotIn(41,a.q.done)
        a.choose(1,Occupation=0,OccupationSeen=0)
        self.assertEqual(a.v('response'),42);self.assertTrue(a.v('courierHeard'))

    def test_cancelled_visible_occupation_is_pending_not_committed_or_new_default(self):
        a=Fair(self);a.scene(0,Occupation=0,OccupationSeen=1)
        self.assertEqual(a.v('pendingCourse'),41);self.assertEqual(a.v('response'),0);self.assertNotIn(70,a.q.done)
        self.assertFalse(a.s.placed[R+'OccupationBoard'].disabled)
        a.use('Response',PendingOrder=1)
        self.assertEqual(a.v('pendingCourse'),0);self.assertNotIn(70,a.q.done)

    def test_truce_cancellation_never_defaults_to_occupation(self):
        for page in ('S_whitcomb_truce_1','S_belden_truce_1','S_grey_truce_1','S_pritchard_truce_1','S_brigg_truce_concession_pritchard_1'):
            with self.subTest(page=page):
                a=Fair(self);old=a.s.n_message_show
                def cancel(message,context,*args):
                    if message.editor_id==P+page:
                        a.s.messages_shown.append(message.editor_id);return -1  # SEEDED engine cancellation
                    return old(message,context,*args)
                a.s.n_message_show=cancel;a.scene(2)
                self.assertNotIn(43,a.q.done);self.assertNotIn(70,a.q.done);self.assertEqual(a.v('response'),0)
                self.assertFalse(a.v('crowdSpared'));self.assertFalse(a.walk.vars['busy'])

    def test_each_quorum_member_loss_or_substitution_closes_before_concession_commit(self):
        for role in (0,3,4,5,6):
            for change in ('dead','combat','rebound','load'):
                with self.subTest(role=role,change=change):
                    a=Fair(self);actor=a.s.invoke(Q,'Person',[role])
                    def alter():
                        if change=='dead':actor.dead=True
                        elif change=='combat':actor.combat_target=a.s.player
                        elif change=='rebound':a.rules.props['cast'][role].ref=a.s.placed[R+'Flint']
                        else:a.s.ref_event(a.s.player,'OnPlayerLoadGame',[],0)
                    a.hook('S_brigg_truce_concession_pritchard_1',alter);a.scene(2)
                    self.assertNotIn(43,a.q.done);self.assertNotIn(70,a.q.done);self.assertFalse(a.v('crowdSpared'))

    def test_dead_brigg_uses_existing_carrier_hierarchy_and_never_occupation(self):
        for absent,carrier in (((),0),((0,),1),((0,1),7)):
            with self.subTest(carrier=carrier):
                a=Fair(self);a.s.placed[R+'Brigg'].dead=True
                for role in absent:a.originals[role].dead=True
                name=('pritchard','talbot','flint')[(0,1,7).index(carrier)]
                shown=a.scene(None,**{'S_'+name+'_courier_no_brigg_living_1':0})
                self.assertIn('S_'+name+'_courier_no_brigg_living_1',shown)
                self.assertEqual(a.v('response'),41);self.assertNotIn(70,a.q.done);self.assertFalse(a.v('orderHeard'))

    def test_all_carriers_missing_preserves_physical_solo_endpoint_without_course(self):
        a=Fair(self)
        for actor in (a.originals[0],a.originals[1],a.s.placed[R+'Brigg'],a.s.placed[R+'Flint']):actor.dead=True
        shown=a.scene(None)
        self.assertIn('NoCarrier',shown);self.assertEqual(a.v('response'),0);self.assertNotIn(70,a.q.done)
        a.read();self.assertIn(100,a.q.done);self.assertNotIn(101,a.q.done)


class FourFlagsPhysicalIdentity(unittest.TestCase):
    def test_busy_dead_or_unsafe_originals_are_not_borrowed(self):
        for role in range(4):
            for state in ('dead','combat','dialogue','scene'):
                with self.subTest(role=role,state=state):
                    a=Fair(self,enter=False);actor=a.originals[role]
                    if state=='dead':actor.dead=True
                    elif state=='combat':actor.combat_target=a.s.player
                    elif state=='dialogue':
                        actor.disabled=False  # an active conversation needs an enabled actor
                        actor.talking_to_player=True
                    else:actor.in_scene=True
                    before=(actor.cell,tuple(actor.pos),actor.disabled)
                    a.enter()
                    self.assertFalse(a.walk.vars['visitorpending'][role])
                    self.assertFalse(a.walk.vars['visitorstaged'][role])
                    self.assertEqual((actor.cell,tuple(actor.pos),actor.disabled),before)
                    self.assertIsNone(a.rules.props['cast'][role].ref)

    def test_base_item_copy_does_not_supply_missing_original_case_access(self):
        a=Fair(self);a.scene(0,Occupation=0,OccupationSeen=0)
        original=a.s.placed[R+'OriginalCase'];original.pos=(90000,90000,16)
        a.s.n_objectreference_additem(a.s.player,None,original.base,1,True)
        shown=a.read();self.assertNotIn('Case',shown)
        self.assertNotIn(60,a.q.done);self.assertNotIn(100,a.q.done)
        self.assertIsNone(original.container);self.assertFalse(a.s.invoke('TLM_MQ03','Held',[]))

    def test_fair_transit_invalidates_only_red_hollow_clock_prime(self):
        a=Fair(self,enter=False)
        rules=a.s.quests['TLM_MQ02C'].scripts[0];walk=a.s.quests['TLM_RH'].scripts[0]
        # SEEDED already warned/partly consumed local deadline and pending work.
        rules.vars.update(deadlinearmed=True,warningaccepted=True,deadlineseconds=137.5,mineintent=2,courtremaining=8.5,courtwatching=True)
        before=dict(rules.vars);walk.vars.update(lastsample=a.s.now,lastarea=2)
        a.enter()
        self.assertEqual((walk.vars['lastsample'],walk.vars['lastarea']),(-1,0))
        self.assertEqual(rules.vars,before)
        walk.vars.update(lastsample=a.s.now,lastarea=1)
        a.use('Exit',Exit=0)
        self.assertEqual((walk.vars['lastsample'],walk.vars['lastarea']),(-1,0))
        self.assertEqual(rules.vars,before)

    def test_load_during_native_case_context_read_closes_old_activation(self):
        a=Fair(self);a.scene(0,Occupation=0,OccupationSeen=0)
        original=a.s.placed[R+'OriginalCase'];old=a.s.n_objectreference_getcontainer;calls=[]
        def load_at_context(ref,context):
            result=old(ref,context)
            if ref is original and not calls:
                calls.append(ref);a.load_inside_native()
            return result
        a.s.n_objectreference_getcontainer=load_at_context
        shown=a.read()
        self.assertEqual(len(calls),1);self.assertNotIn('Case',shown)
        self.assertNotIn(60,a.q.done);self.assertNotIn(100,a.q.done)
        self.assertFalse(a.walk.vars['busy'])
        a.s.n_objectreference_getcontainer=old;a.read();self.assertIn(100,a.q.done)

    def test_silver_load_after_effect_holds_one_transfer_without_ghost_quote(self):
        a=Fair(self);a.scene(0,Occupation=0,OccupationSeen=0)
        silver=a.s.placed[R+'OriginalSilver'];old=a.s.n_objectreference_additem;calls=[]
        def load_after_effect(ref,context,form,*args):
            result=old(ref,context,form,*args)
            if form is silver:calls.append(ref);a.load_inside_native()
            return result
        a.s.n_objectreference_additem=load_after_effect
        shown=a.use('Firing',Silver=0,GiveSilver=0)
        self.assertEqual(calls,[a.s.placed[R+'Flint']]);self.assertIs(silver.container,calls[0])
        self.assertIn(50,a.q.done);self.assertNotIn(51,a.q.done)
        self.assertEqual(a.v('effectPending'),3);self.assertTrue(a.v('effectUncertain'))
        self.assertNotIn('S_flint_roof_1',shown)
        a.use('Firing',GiveSilver=0);self.assertEqual(len(calls),1)

    def test_pike_comparison_is_explicit_original_silver_aside_not_competition(self):
        a=Fair(self);a.scene(0,Occupation=0,OccupationSeen=0)
        a.use('Firing',Silver=0,GiveSilver=1)
        shown=a.use('Pike',PikeCompare=0)
        self.assertIn('PikeUnavailable',shown);self.assertNotIn('A_pike_mould_aside',shown)
        silver=a.s.placed[R+'OriginalSilver']
        a.s.n_objectreference_additem(a.s.player,None,silver,1,True)
        before=(list(a.q.done),a.old_history())
        shown=a.use('Pike',PikeCompare=0)
        self.assertEqual(shown,['PikeCompare','A_pike_mould_aside'])
        self.assertEqual((a.q.done,a.old_history()),before)
        self.assertTrue(all(stage not in a.q.done for stage in (20,21,22)))

    def test_pike_aside_decline_or_loss_at_confirmation_has_no_protected_quote(self):
        for change in ('cancel','dead','combat','dialogue','drop','alias','load'):
            with self.subTest(change=change):
                a=Fair(self);a.scene(0,Occupation=0,OccupationSeen=0)
                a.use('Firing',Silver=0,GiveSilver=1)
                silver=a.s.placed[R+'OriginalSilver'];a.s.n_objectreference_additem(a.s.player,None,silver,1,True)
                def interrupt():
                    if change=='dead':a.originals[2].dead=True
                    elif change=='combat':a.originals[2].combat_target=a.s.player
                    elif change=='dialogue':a.originals[2].talking_to_player=True
                    elif change=='drop':silver.container=None
                    elif change=='alias':a.rules.props['alias_originalsilver'].ref=a.s.placed[R+'OriginalCase']
                    elif change=='load':a.load_inside_native()
                a.hook('PikeCompare',interrupt)
                shown=a.use('Pike',PikeCompare=1 if change=='cancel' else 0)
                self.assertNotIn('A_pike_mould_aside',shown)

    def test_public_transfer_load_is_held_but_actual_original_has_fresh_read_access(self):
        a=Fair(self);a.scene(0,Occupation=0,OccupationSeen=0)
        original=a.s.placed[R+'OriginalCase'];old=a.s.n_objectreference_additem;calls=[]
        def load_after_effect(ref,context,form,*args):
            result=old(ref,context,form,*args)
            if form is original:calls.append((ref,form));a.load_inside_native()
            return result
        a.s.n_objectreference_additem=load_after_effect
        a.read(public=True)
        self.assertEqual(len(calls),1);self.assertIs(original.container,a.originals[0])
        self.assertEqual(a.v('effectPending'),2);self.assertTrue(a.v('effectUncertain'))
        self.assertIsNone(a.v('publicCustodian'));self.assertNotIn(100,a.q.done)
        shown=a.read(public=True)
        self.assertIn('S_pritchard_case_1',shown);self.assertIn(100,a.q.done);self.assertIn(101,a.q.done)
        self.assertEqual(len(calls),1);self.assertEqual(a.v('effectPending'),2)
        self.assertTrue(a.v('effectUncertain'));self.assertIsNone(a.v('publicCustodian'))

    def test_public_recipient_rebound_at_effect_does_not_credit_replacement(self):
        a=Fair(self);a.scene(0,Occupation=0,OccupationSeen=0)
        original=a.s.placed[R+'OriginalCase'];old=a.s.n_objectreference_additem;calls=[]
        def rebound(ref,context,form,*args):
            result=old(ref,context,form,*args)
            if form is original:
                calls.append(ref);a.rules.props['cast'][0].ref=a.originals[1]
            return result
        a.s.n_objectreference_additem=rebound;a.read(public=True)
        self.assertEqual(calls,[a.originals[0]]);self.assertIs(original.container,a.originals[0])
        self.assertTrue(a.v('effectUncertain'));self.assertEqual(a.v('effectPending'),2)
        self.assertNotIn(100,a.q.done);self.assertNotIn(101,a.q.done)
        self.assertIsNone(a.v('publicCustodian'))

    def test_original_read_pages_cancel_loss_or_load_do_not_finish(self):
        for page in ('D_courier_card_1','D_courier_card_2','D_courier_card_3','Solo'):
            for change in ('cancel','alias','dead','load'):
                with self.subTest(page=page,change=change):
                    a=Fair(self);a.scene(0,Occupation=0,OccupationSeen=0)
                    def interrupt():
                        if change=='alias':a.rules.props['alias_originalcase'].ref=a.s.placed[R+'OriginalSilver']
                        elif change=='dead':a.s.player.dead=True
                        elif change=='load':a.load_inside_native()
                    a.hook(page,interrupt)
                    answers={'Case':0,'Solo':0}
                    if change=='cancel':
                        old=a.s.n_message_show
                        def cancel(message,context,*args):
                            result=old(message,context,*args)
                            return -1 if message.editor_id==P+page else result  # SEEDED native close
                        a.s.n_message_show=cancel
                    shown=a.use('CaseControl',**answers)
                    self.assertNotIn(100,a.q.done,shown);self.assertNotIn(101,a.q.done)

    def test_preexisting_original_alias_substitution_never_redefines_case(self):
        a=Fair(self);a.rules.props['alias_originalcase'].ref=a.s.placed[R+'OriginalSilver']
        shown=a.scene(None)
        self.assertNotIn(40,a.q.done);self.assertNotIn('Shot',shown)
        self.assertIs(a.v('originalCaseIdentity'),a.s.placed[R+'OriginalCase'])

    def test_refused_case_transfer_keeps_real_occupation_and_no_case_acquisition(self):
        a=Fair(self);original=a.s.placed[R+'OriginalCase'];old=a.s.n_objectreference_additem;calls=[]
        def refuse(ref,context,form,*args):
            if form is original:calls.append((ref,form));return None  # SEEDED refusal
            return old(ref,context,form,*args)
        a.s.n_objectreference_additem=refuse;a.scene(3,Occupation=0,OccupationSeen=0,Take=0)
        self.assertEqual(len(calls),1);self.assertIn(70,a.q.done);self.assertNotIn(44,a.q.done)
        self.assertEqual(a.v('response'),0);self.assertEqual(a.v('pendingCourse'),44)
        self.assertEqual(a.v('effectPending'),1);self.assertTrue(a.v('effectUncertain'))
        self.assertIsNone(original.container)
        a.use('Response');self.assertEqual(len(calls),1)

    def test_staging_failure_is_not_a_present_delegate_and_exit_still_restores(self):
        a=Fair(self,enter=False);target=a.originals[0];old=a.s.n_objectreference_moveto
        def refuse(ref,context,*args):
            if ref is target:return None  # SEEDED original's failed stage movement
            return old(ref,context,*args)
        a.s.n_objectreference_moveto=refuse;a.enter()
        self.assertFalse(a.walk.vars['visitorstaged'][0]);self.assertTrue(a.walk.vars['visitorpending'][0])
        self.assertFalse(a.s.invoke(Q,'Usable',[0]))
        a.s.n_objectreference_moveto=old;a.use('Exit',Exit=0)
        self.assertFalse(any(a.walk.vars['visitorpending']))
        self.assertEqual((target.cell,tuple(target.pos),target.disabled),a.before[0][:3])

    def test_failed_original_return_does_not_block_player_exit_or_reset_saved_state(self):
        a=Fair(self);target=a.originals[0];saved=a.s.placed[R+'PritchardReturn'];old=a.s.n_objectreference_moveto;calls=[]
        def refuse(ref,context,destination,*args):
            if ref is target and destination is saved:calls.append(ref);return None
            return old(ref,context,destination,*args)
        a.s.n_objectreference_moveto=refuse;shown=a.use('Exit',Exit=0)
        self.assertEqual(len(calls),3);self.assertIn('ReturnsPending',shown)
        self.assertTrue(a.walk.vars['visitorpending'][0]);self.assertNotEqual(a.s.player.cell,a.q.aliases[2].ref.cell)
        a.s.ref_event(a.s.player,'OnPlayerLoadGame',[],0);a.a.p.pause(1)
        self.assertTrue(a.walk.vars['visitorpending'][0]);self.assertIs(a.walk.vars['visitors'][0],target)
        a.s.n_objectreference_moveto=old;a.use('Entry',Travel=1)
        self.assertFalse(any(a.walk.vars['visitorpending']))
        self.assertEqual((target.cell,tuple(target.pos),target.disabled),a.before[0][:3])
