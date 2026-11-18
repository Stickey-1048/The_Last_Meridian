"""Actual RH PSC on fresh synthetic source projection; no native sky/physics proof.
Explicit adverse native returns/events/positions below are seeded, not game facts.
"""
import copy,json,subprocess,tempfile,unittest
from pathlib import Path
from test_sim import ROOT,PLUGIN
from test_red_hollow import Hollow,P


def walk_call(a,name,*args):return a.s.invoke('TLM_RH',name,list(args))
def road_call(a,name,*args):return a.s.invoke('TLM_MQ02C',name,list(args))
def facts(a):return (a.g('Mine'),a.g('Court'),a.g('MinePending'),a.g('Survivors'),a.g('ObservedDeaths'),tuple(a.v('minerfates') or []),dict(a.s.player_values))


class RegionsAndPrime(unittest.TestCase):
    def test_all_four_regions_require_their_actual_anchor_cell(self):
        a=Hollow(self)
        for name,court,mine in [('GapArrival',True,False),('MouthArrival',False,True),('CageBelow',False,True),('GalleryArrival',False,True)]:
            with self.subTest(region=name):
                a.pos(name);self.assertTrue(walk_call(a,'Local'));self.assertEqual(walk_call(a,'CourtArea'),court);self.assertEqual(walk_call(a,'MineArea'),mine)
                actual=a.s.player.cell;a.s.player.cell=a.ref('MercyReturn').cell
                self.assertFalse(walk_call(a,'Local'));self.assertFalse(walk_call(a,'MineArea'));a.s.player.cell=actual
    def test_same_coordinates_in_other_cells_and_unapproved_bounds_are_closed(self):
        a=Hollow(self)
        for anchor,pos in [('GapArrival',(1800,256,16)),('MouthArrival',(3900,512,16)),('CageBelow',(2000,256,16)),('GalleryArrival',(11000,256,16))]:
            a.pos(anchor);a.s.player.pos=pos;self.assertFalse(walk_call(a,'Local'))
        a.pos('CageBelow');a.s.player.cell=a.s._cell('UnapprovedSameXYZ');self.assertFalse(walk_call(a,'Local'))
    def test_constant_reference_properties_are_the_existing_original_objects(self):
        a=Hollow(self)
        self.assertEqual(len(a.rules.props['rhsurfacereceipts']),11)
        for i in range(11):
            self.assertIs(a.rules.props['rhsurfacereceipts'][i],a.ref('Surface%02d'%(i+1)))
            self.assertIs(a.rules.props['rhoriginalminers'][i],a.ref('Miner%02d'%(i+1)))
        self.assertTrue(road_call(a,'DistinctRoster'))
        self.assertIsNot(a.ref('Surface01').cell,a.ref('Below01').cell)
        self.assertIs(a.ref('Blevins').cell,a.ref('FiringControl').cell)
        self.assertIs(a.ref('Dorn').cell,a.ref('DornWithdraw').cell)
    def test_move_invalidates_before_effect_and_after_receipt_reads(self):
        a=Hollow(self);a.mouth();a.walk.vars['lastsample']=100;a.walk.vars['lastarea']=2
        seen=[];old=a.s.n_objectreference_moveto;distance=a.s.n_objectreference_getdistance
        def effect(ref,ctx,*args):
            if ref is a.s.player:seen.append((a.walk.vars['lastsample'],a.walk.vars['lastarea']))
            return old(ref,ctx,*args)
        def receipt(ref,ctx,*args):
            result=distance(ref,ctx,*args)
            if ref is a.s.player:a.walk.vars.update(lastsample=999,lastarea=2)  # SEEDED intervening sample
            return result
        a.s.n_objectreference_moveto=effect;a.s.n_objectreference_getdistance=receipt
        before=facts(a);self.assertTrue(walk_call(a,'MovePlayer',a.ref('CageBelow')))
        self.assertEqual(seen,[(-1,0)]);self.assertEqual(a.walk.vars['lastsample'],-1);self.assertEqual(a.walk.vars['lastarea'],0);self.assertEqual(facts(a),before)
    def test_refused_or_missing_move_keeps_facts_and_clears_prime(self):
        a=Hollow(self);a.walk.vars.update(lastsample=100,lastarea=1);before=facts(a);position=a.s.player.pos
        a.refuse.add(('moveto',a.s._whom(a.s.player)))
        self.assertFalse(walk_call(a,'MovePlayer',a.ref('CageBelow')));self.assertEqual(a.s.player.pos,position)
        self.assertEqual(a.walk.vars['lastsample'],-1);self.assertEqual(a.walk.vars['lastarea'],0);self.assertEqual(facts(a),before)
        a.walk.vars.update(lastsample=100,lastarea=1);self.assertFalse(walk_call(a,'MovePlayer',None));self.assertEqual(a.walk.vars['lastarea'],0)
    def test_between_tick_round_trip_does_not_charge_deadline(self):
        a=Hollow(self);a.mouth();a.listen();a.warning();a.wait(3);left=a.v('deadlineSeconds')
        self.assertTrue(walk_call(a,'MovePlayer',a.ref('CageBelow')));self.assertTrue(walk_call(a,'MovePlayer',a.ref('MouthArrival')))
        a.s.now+=0.5;walk_call(a,'OnTimer',1);self.assertEqual(a.v('deadlineSeconds'),left);self.assertEqual(a.g('DeadlineArmed'),1)
    def test_actual_supported_player_cell_events_invalidate_only_prime(self):
        a=Hollow(self);a.mouth();a.listen();a.warning();before=facts(a);left=a.v('deadlineSeconds')
        for event,args in [('OnCellDetach',[]),('OnCellAttach',[]),('OnCellLoad',[]),('OnLocationChange',[None,None])]:
            a.walk.vars.update(lastsample=100,lastarea=2);a.s.ref_event(a.s.player,event,args,0);a.s.run(a.s.now)
            self.assertEqual(a.walk.vars['lastsample'],-1,event);self.assertEqual(a.walk.vars['lastarea'],0,event);self.assertEqual(a.v('deadlineSeconds'),left);self.assertEqual(facts(a),before)
    def test_nonplayer_cell_events_do_not_invalidate_player_prime(self):
        a=Hollow(self);a.walk.vars.update(lastsample=100,lastarea=2)
        a.s.ref_event(a.ref('Blevins'),'OnCellDetach',[],0);a.s.run(a.s.now)
        self.assertEqual(a.walk.vars['lastsample'],100);self.assertEqual(a.walk.vars['lastarea'],2)
    def test_load_and_short_registered_menu_preserve_warnings_and_fates(self):
        a=Hollow(self);a.mouth();a.listen();a.warning();a.wait(3);left=a.v('deadlineSeconds');before=facts(a)
        a.s.menu_event('PipboyMenu',True);a.s.run(a.s.now);a.s.now+=0.25;a.s.menu_event('PipboyMenu',False);a.s.run(a.s.now);walk_call(a,'OnTimer',1)
        self.assertEqual(a.v('deadlineSeconds'),left)
        a.walk.vars.update(lastsample=100,lastarea=2);walk_call(a,'Loaded');self.assertEqual(a.walk.vars['lastsample'],-1);self.assertEqual(a.walk.vars['lastarea'],0);self.assertEqual(facts(a),before);self.assertEqual(a.g('DeadlineArmed'),1)


class CrossCellBlast(unittest.TestCase):
    def prepared(self):
        a=Hollow(self);a.below();a.use('Gallery',StageTravel=0);a.use('Dorn',dorn_door=2);a.use('FromGallery',StageTravel=0);a.rescue();a.use('CageControl',Descend=0);a.pos('BreakControl')
        self.assertEqual(a.g('Survivors'),11)
        return a
    def args(self,a):return [a.ref('BreakClosed'),a.walk.props['surfaceslots'],a.ref('BreakControl'),a.ref('CageBelow')]
    def test_all11_genuine_surface_receipts_clear_and_actual_controller_can_finish52(self):
        a=self.prepared();self.assertTrue(road_call(a,'ClearBlastArea',*self.args(a)));a.use('BreakControl',Blast=0)
        self.assertEqual(a.g('Mine'),52);self.assertTrue(a.v('innerClosed'));self.assertEqual(a.g('Survivors'),11)
    def test_each_original_current_fate_and_slot_must_be_known(self):
        for index in range(11):
            with self.subTest(index=index):
                a=self.prepared();a.rules.vars['minerfates'][index]=0
                self.assertFalse(road_call(a,'ClearBlastArea',*self.args(a)));self.assertEqual(a.g('ObservedDeaths'),0)
    def test_missing_wrong_cell_offslot_and_substituted_miner_are_closed(self):
        for mode in ('missing','wrong-cell','off-slot','replacement','unknown-dead'):
            with self.subTest(mode=mode):
                a=self.prepared();miner=a.ref('Miner01')
                if mode=='missing':a.rules.props['miners'][0].ref=None
                elif mode=='wrong-cell':miner.cell=a.s._cell('OtherAtSameXYZ')
                elif mode=='off-slot':miner.pos=(miner.pos[0]+1000,miner.pos[1],miner.pos[2])
                elif mode=='replacement':
                    other=a.ref('Roark');other.cell=miner.cell;other.pos=miner.pos;a.rules.props['miners'][0].ref=other
                else:miner.dead=True  # SEEDED corpse, no observed fate
                self.assertFalse(road_call(a,'ClearBlastArea',*self.args(a)));self.assertFalse(a.v('innerClosed'))
    def test_wrong_surface_slot_control_anchor_and_player_cell_are_closed(self):
        for mode in ('slot','control','anchor','player'):
            a=self.prepared();args=self.args(a)
            if mode=='slot':args[1]=list(args[1]);args[1][0]=args[1][1]
            elif mode=='control':args[2]=a.ref('Roster');args[2].pos=a.ref('BreakControl').pos
            elif mode=='anchor':args[3]=a.ref('GalleryArrival')
            else:a.s.player.cell=a.ref('Surface01').cell
            self.assertFalse(road_call(a,'ClearBlastArea',*args),mode)
    def test_final_predicate_rechecks_current_receipts_after_intent(self):
        a=self.prepared();self.assertTrue(road_call(a,'BeginBreak',a.walk.props['surfaceslots']))
        a.ref('Miner11').cell=a.s._cell('ChangedAfterIntent')
        args=[a.ref('BreakOpen'),a.ref('BreakClosed')]+self.args(a)[:2]+self.args(a)[2:]
        self.assertFalse(road_call(a,'FinishBreak',*args));self.assertEqual(a.g('MinePending'),3);self.assertFalse(a.v('innerClosed'))
    def test_final_predicate_blocks_wrong_player_cell_with_all11_still_safe(self):
        a=self.prepared();self.assertTrue(road_call(a,'BeginBreak',a.walk.props['surfaceslots']))
        a.ref('BreakOpen').disabled=True;a.ref('BreakClosed').disabled=False  # SEEDED actual effect receipts
        a.s.player.cell=a.ref('Surface01').cell
        self.assertTrue(road_call(a,'KnownSafeSurvivors',a.walk.props['surfaceslots']))
        args=[a.ref('BreakOpen'),a.ref('BreakClosed')]+self.args(a)
        self.assertFalse(road_call(a,'FinishBreak',*args));self.assertEqual(a.g('MinePending'),3);self.assertFalse(a.v('innerClosed'))
    def test_precommit_guard_blocks_any_effect_for_wrong_but_nearby_slot_alias(self):
        a=self.prepared();a.walk.props['surfaceslots'][0]=a.walk.props['surfaceslots'][1]
        # Neighbouring128-spaced slots satisfy legacy proximity; exact receipt
        # identity still must close before the world effect or pending intent.
        self.assertTrue(road_call(a,'KnownSafeSurvivors',a.walk.props['surfaceslots']))
        before=len(a.calls);a.use('BreakControl',Blast=0)
        effects=[c for c in a.calls[before:] if c[0] in ('enable','disable') and c[1] in (a.s._whom(a.ref('BreakOpen')),a.s._whom(a.ref('BreakClosed')))]
        self.assertEqual(effects,[]);self.assertEqual(a.g('MinePending'),0);self.assertFalse(a.v('innerClosed'))
    def test_warning_page_change_blocks_then_true_restored_context_recovers(self):
        a=self.prepared();miner=a.ref('Miner03');original=miner.cell
        a.s.on_box=lambda m:setattr(miner,'cell',a.s._cell('ChangedAtWarning')) if m==P+'Blast' else None
        a.use('BreakControl',Blast=0);self.assertFalse(a.v('innerClosed'));self.assertEqual(a.g('MinePending'),0)
        a.s.on_box=None;miner.cell=original;a.use('BreakControl',Blast=0);self.assertEqual(a.g('Mine'),52)
    def test_known_actual_dead_identity_preserved_and_same_blast_cell_requires512(self):
        a=self.prepared();miner=a.ref('Miner01');miner.dead=True;road_call(a,'ObserveDeath',0)
        self.assertEqual(a.v('minerfates')[0],4);self.assertTrue(road_call(a,'ClearBlastArea',*self.args(a)))
        miner.cell=a.ref('BreakClosed').cell;miner.pos=a.ref('BreakClosed').pos
        self.assertFalse(road_call(a,'ClearBlastArea',*self.args(a)))
        miner.pos=(miner.pos[0]-600,miner.pos[1],miner.pos[2]);self.assertTrue(road_call(a,'ClearBlastArea',*self.args(a)))


class RegionFalls(unittest.TestCase):
    def place_fall(self,a,name,pos):a.s.player.cell=a.ref(name).cell;a.s.player.pos=pos
    def test_all_actual_region_triggers_move_only_player_and_preserve_facts(self):
        for name,pos,target in [('Fall',(6912,384,-700),'CageBelow'),('SurfaceFall',(500,512,-700),'GapArrival'),('SurfaceFall',(2500,512,-700),'MouthArrival'),('GalleryFall',(9984,512,-700),'GalleryArrival')]:
            a=Hollow(self);a.s.player_values['Health']=37;self.place_fall(a,name,pos);before=facts(a)
            a.s.ref_event(a.ref(name),'OnTriggerEnter',[a.s.player],0);a.s.run(a.s.now)
            self.assertEqual(a.s.player.pos,a.ref(target).pos,name);self.assertEqual(facts(a),before);self.assertEqual(a.walk.vars['lastsample'],-1)
    def test_wrong_cell_nonfall_other_actor_and_dead_player_do_not_recover(self):
        for mode in ('cell','height','other','dead'):
            a=Hollow(self);self.place_fall(a,'SurfaceFall',(500,512,-700));entered=a.s.player
            if mode=='cell':a.s.player.cell=a.s._cell('WrongSurface')
            elif mode=='height':a.s.player.pos=(500,512,16)
            elif mode=='other':entered=a.ref('Quill')
            else:a.s.player.dead=True
            before=(a.s.player.cell,a.s.player.pos,facts(a));a.s.ref_event(a.ref('SurfaceFall'),'OnTriggerEnter',[entered],0);a.s.run(a.s.now)
            self.assertEqual((a.s.player.cell,a.s.player.pos,facts(a)),before,mode)
    def test_failed_transfer_has_an_ordinary_timer_retry_without_healing(self):
        a=Hollow(self);a.s.player_values['Health']=37;self.place_fall(a,'Fall',(6912,384,-700));before=facts(a)
        a.refuse.add(('moveto',a.s._whom(a.s.player)));a.s.ref_event(a.ref('Fall'),'OnTriggerEnter',[a.s.player],0);a.s.run(a.s.now)
        self.assertEqual(a.s.player.pos,(6912,384,-700));self.assertEqual(facts(a),before)
        a.refuse.clear();a.wait(1.1);self.assertEqual(a.s.player.pos,a.ref('CageBelow').pos);self.assertEqual(facts(a),before)


class GeometryAndTypedLight(unittest.TestCase):
    def test_production_geometry_guard_rejects_floor_ceiling_cohort_route_and_rope_damage(self):
        cases=[([],None),([{'name':'NineRoof6144_0','z':-200}],'obstruction'),([{'name':'NineFloor6144_0','z':40}],'unsupported'),([{'name':'CourtGatePost128','y':256}],'obstruction'),([{'name':'HoistPost2704_624','x':2688,'y':768}],'obstruction'),([{'name':'CourtGatePost128','x':768,'y':368}],'projectile')]
        for edits,word in cases:
            with self.subTest(edits=edits),tempfile.TemporaryDirectory() as t:
                p=Path(t)/'metadata.json';p.write_text(json.dumps(edits),encoding='utf-8')
                got=subprocess.run(['dotnet','run','--project','tools/PluginBuilder','--','--rh-environment-geometry-check',str(p)],cwd=ROOT,capture_output=True,text=True)
                self.assertEqual(got.returncode,1 if word else 0,got.stdout+got.stderr)
                if word:self.assertIn(word,got.stderr)
                else:self.assertGreaterEqual(json.loads(got.stdout[got.stdout.index('{'):])['minimumHeadroom'],128)
    def test_real_typed_emitter_and_passive_metadata_are_required_before_output(self):
        cases={'rhe-no-light':'real LIGH missing','rhe-decorative-only':'real LIGH missing','rhe-light-radius':'emitter metadata','rhe-light-off':'emitter metadata','rhe-light-script':'emitter metadata','rhe-light-color':'emitter metadata','rhe-template':'template settings','rhe-room-template':'room/template inheritance','rhe-static-model':'model/bounds','rhe-floor-height':'model/bounds','rhe-no-climate':'climate absent'}
        for variant,word in cases.items():
            with self.subTest(variant=variant),tempfile.TemporaryDirectory() as t:
                master=Path(t)/'Fallout4.esm';out=Path(t)/'out'
                made=subprocess.run(['dotnet','run','--project','tools/StandInMaster','--',str(master),variant],cwd=ROOT,capture_output=True,text=True);self.assertEqual(made.returncode,0,made.stdout+made.stderr)
                got=subprocess.run(['dotnet','run','--project','tools/PluginBuilder','--','--out',str(out),'--fallout4-esm',str(master)],cwd=ROOT,capture_output=True,text=True)
                self.assertNotEqual(got.returncode,0);self.assertIn(word,got.stderr);self.assertFalse((out/'TheLastMeridian.esp').exists())


if __name__=='__main__':unittest.main()
