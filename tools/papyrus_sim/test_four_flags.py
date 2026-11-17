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
    def __init__(self,t,scripts=SCRIPTS,enter=True):
        self.t=t;self.a=Player(t,scripts=scripts,travel=False);self.s=self.a.s
        self.q=self.s.quests[Q]
        self.rules=next(i for i in self.q.scripts if i.script.name=='TLM:MQ03Quest')
        self.walk=next(i for i in self.q.scripts if i.script.name=='TLM:FourFlagsWalk')
        self.messages={m['EditorId']:m for m in json.loads(PLUGIN.read_text())['Messages']}
        self.originals=[self.s.placed['TLM_REF_A1_'+n] for n in ('Pritchard','Talbot','Pike')]+[self.s.placed['TLM_REF_GW_Belden']]
        self.before=[(a.cell,tuple(a.pos),a.disabled,dict(a.inventory),a.dead,a.protected_override,a.essential_override) for a in self.originals]
        if enter:self.enter()
    def v(self,key):return self.rules.vars[key.lower()]
    def use(self,part,**answers):
        self.s.answers={n:[0]*40 for n,m in self.messages.items() if n.startswith(P) and len(m['Buttons'])==1}
        self.s.answers.update({P+k:([v] if not isinstance(v,list) else v) for k,v in answers.items()})
        at=len(self.s.messages_shown);self.s.walk_to(R+part);self.s.press_activate(R+part);self.a.p.pause(4)
        return [n.removeprefix(P) for n in self.s.messages_shown[at:]]
    def enter(self):return self.use('Entry',Entry=1,NoReport=0,Travel=0)
    def scene(self,choice=None,**answers):
        if choice is not None:answers['S_brigg_demand_1']=choice
        return self.use('Ready',Ready=0,Shot=0,**answers)
    def choose(self,choice,**answers):return self.use('Response',S_brigg_demand_1=choice,**answers)
    def read(self,public=False):return self.use('CaseControl',Case=2 if public else 0,Public=0,S_pritchard_case_1=1,Solo=0)
    def old_history(self):
        return ({n:f.value for n,f in self.s.forms.items() if n.startswith('TLM_G_')},
                {n:(tuple(q.done),dict(q.displayed),dict(q.completed_objectives),q.completed) for n,q in self.s.quests.items() if n not in (Q,'TLM_FF_Entry')})


class FourFlagsNormal(unittest.TestCase):
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
