"""Actual PSC guidance on synthetic native responses; no native visibility claim."""
import io,json,unittest
from test_red_hollow import Hollow,P
from test_sim import PLUGIN

class Guidance(unittest.TestCase):
    def shown(self,a,n):return bool(a.s.n_quest_isobjectivedisplayed(a.w,None,n))
    def releases(self,a):return [m for m in a.s.notifications if m.startswith('Freed prisoner:')]
    def test_sheriff_delivery_opens_visible_road_target_without_forcing_travel(self):
        a=Hollow(self,False);self.assertTrue(self.shown(a,5));self.assertNotIn(10,a.q.done)
        info=json.loads(PLUGIN.read_text());q=next(q for q in info['Quests'] if q['EditorId']=='TLM_RH')
        obj=next(o for o in q['Objectives'] if o['Index']==5)
        self.assertIn('road to Red Hollow',obj['Text']);self.assertTrue(obj['TargetAliases'])
        a.use('MercyTravel',Travel=1);self.assertTrue(self.shown(a,5));self.assertNotIn(10,a.q.done)
        a.use('MercyTravel',Travel=0);self.assertFalse(self.shown(a,5));self.assertTrue(self.shown(a,10))
    def test_muster_rescue_result_and_return_guidance_follow_actual_state(self):
        a=Hollow(self);a.mouth();a.listen();self.assertTrue(self.shown(a,20))
        a.use('CageControl',NoWarning=0,Descend=0);self.assertTrue(self.shown(a,30))
        a.use('Roster');self.assertTrue(self.shown(a,40));a.rescue();self.assertTrue(self.shown(a,50));self.assertEqual(a.g('Mine'),0)
        a.finish57();self.assertEqual(a.g('Mine'),57);self.assertTrue(self.shown(a,60));a.exit()
        self.assertFalse(any(self.shown(a,n) for n in (5,10,20,30,40,50,55,60,80)))
        self.assertTrue(any('Tell Sheriff Pritchard' in x for x in a.s.notifications))
    def test_partial_rescue_has_retry_target_and_no_invented_completion(self):
        a=Hollow(self);a.below();old=a.s.n_objectreference_moveto
        def refuse_one_surface(ref,ctx,*args):
            if ref is a.ref('Miner06') and args[0] is a.ref('Surface06'):return None
            return old(ref,ctx,*args)
        a.s.n_objectreference_moveto=refuse_one_surface
        a.rescue();self.assertEqual(a.g('MinePending'),2);self.assertEqual(a.g('Mine'),0)
        self.assertTrue(self.shown(a,20));self.assertFalse(self.shown(a,60));self.assertEqual(a.s.invoke('TLM_MQ02C','SafeCount',[a.walk.props['surfaceslots']]),5)
        a.s.n_objectreference_moveto=old;a.use('CageControl',PendingRescue=0,Rescue=0);self.assertTrue(self.shown(a,50));self.assertEqual(a.g('Mine'),0)
    def test_return_alone_does_not_claim_rescue_or_result(self):
        a=Hollow(self);a.below();a.use('BelowControl',HoistBelow=1)
        self.assertTrue(self.shown(a,20));self.assertEqual(a.g('Survivors'),0);self.assertEqual(a.g('Mine'),0)
    def test_gallery_has_actual_return_control_target(self):
        a=Hollow(self);a.below();a.use('Gallery',StageTravel=0);self.assertTrue(self.shown(a,80));self.assertFalse(self.shown(a,60))
    def test_blast_result_below_directs_return_alone_not_another_rescue(self):
        a=Hollow(self);a.below();a.use('Gallery',StageTravel=0);a.use('Dorn',dorn_door=2)
        a.use('FromGallery',StageTravel=0);a.rescue();a.use('CageControl',Descend=0);a.use('BreakControl',Blast=0)
        self.assertEqual(a.g('Mine'),52);self.assertTrue(self.shown(a,85));self.assertFalse(self.shown(a,40))
        a.use('BelowControl',HoistBelow=1);self.assertTrue(self.shown(a,60));self.assertEqual(a.g('Survivors'),11)
    def test_timeout_and_casualty_results_have_return_guidance_without_fabricated_rescues(self):
        a=Hollow(self);a.mouth();a.listen();a.warning();a.answer(Final=0);a.wait(605)
        self.assertEqual(a.g('Mine'),56);self.assertTrue(self.shown(a,60));self.assertEqual(a.g('Survivors'),0)
        a=Hollow(self);a.below();a.die('Miner03',True);a.rescue();a.use('Resolve',Resolve=2)
        self.assertEqual(a.g('Mine'),58);self.assertTrue(self.shown(a,60));self.assertEqual(a.g('Survivors'),10);self.assertNotIn(57,a.q.done)
    def test_load_recomputes_directions_without_changing_story_receipts(self):
        a=Hollow(self);a.below();before=a.snapshot();a.w.displayed.clear()
        a.s.invoke('TLM_RH','Loaded',[]);self.assertTrue(self.shown(a,40));self.assertEqual(a.snapshot(),before)
    def test_rope_release_acknowledges_same_living_original_and_marks_destination(self):
        a=Hollow(self);original=a.walk.props['alias_condemned'].ref;a.shoot()
        self.assertEqual(a.g('Court'),11);self.assertEqual(len(self.releases(a)),1);self.assertTrue(self.shown(a,70))
        self.assertIs(a.walk.props['alias_condemned'].ref,original);self.assertFalse(original.dead)
        self.assertIn("I'm clear of the rope.",self.releases(a)[0]);self.assertTrue(any('beside the court' in x for x in a.s.notifications))
        a.mouth();self.assertFalse(self.shown(a,70))
    def test_freed_prisoner_uses_approved_acknowledgment_not_old_hanging_speech(self):
        a=Hollow(self);a.shoot();ref=a.walk.props['alias_condemned'].ref
        a.s.player.cell=ref.cell;a.s.player.pos=ref.pos;before=len(a.s.messages_shown)
        a.s.press_activate(ref.editor_id);a.wait()
        self.assertIn("Freed prisoner: I'm clear of the rope.",a.s.message_boxes)
        self.assertEqual(a.s.messages_shown[before:],[])
    def test_paid_release_acknowledges_only_actual_arrival_and_preserves_once_payment(self):
        a=Hollow(self);a.s.player.inventory[a.p.caps]=100
        a.use('Quill',quill_court=0,quill_fine=0,Receipt=0)
        self.assertEqual(a.g('Court'),12);self.assertEqual(len(self.releases(a)),1);self.assertTrue(self.shown(a,70))
        self.assertEqual(a.p.has(a.p.caps),40);a.use('Quill',Status=0);self.assertEqual(a.p.has(a.p.caps),40);self.assertEqual(len(self.releases(a)),1)
    def test_failed_release_move_says_nothing_then_valid_retry_acknowledges(self):
        a=Hollow(self);original=a.walk.props['alias_condemned'].ref;key=('moveto',a.s._whom(original));a.refuse.add(key)
        a.shoot();self.assertEqual(self.releases(a),[]);self.assertFalse(self.shown(a,70));self.assertEqual(a.g('Court'),0)
        a.refuse.clear();a.use('CourtRecord');self.assertEqual(a.g('Court'),11);self.assertEqual(len(self.releases(a)),1)
    def test_dead_or_replaced_release_actor_cannot_get_success_notice(self):
        for dead in (True,False):
            a=Hollow(self);original=a.walk.props['alias_condemned'].ref;a.shoot();a.s.notifications.clear()
            if dead:original.dead=True
            else:a.walk.props['alias_condemned'].ref=a.ref('Quill')
            a.s.invoke('TLM_RH','AcknowledgeRelease',[original]);self.assertEqual(self.releases(a),[])
    def test_release_actor_moved_away_does_not_get_arrival_announcement(self):
        a=Hollow(self);original=a.walk.props['alias_condemned'].ref;a.shoot();a.s.notifications.clear()
        original.pos=(4000,4000,16)
        a.s.invoke('TLM_RH','AcknowledgeRelease',[original]);self.assertEqual(self.releases(a),[])
    def test_resolved_board_and_stove_explain_without_stage_or_inventory_changes(self):
        a=Hollow(self,False);q=a.s.quests['TLM_SQ01'];q.done.append(50) # explicit resolved-without-old-prerequisite adverse fixture
        for alias,phrase in (('NoticeBoard','nothing further to post'),('Stove','not a cooking station')):
            ref=next(x.ref for x in q.aliases.values() if x.name==alias)
            before=(set(q.done),dict(a.s.player.inventory));a.s.player.cell=ref.cell;a.s.player.pos=ref.pos
            a.s.press_activate(ref.editor_id);a.wait();self.assertTrue(any(phrase in x for x in a.s.message_boxes))
            self.assertEqual(before,(set(q.done),dict(a.s.player.inventory)))
    def test_passive_opening_and_operative_hoist_are_distinguished(self):
        a=Hollow(self);data=json.loads(PLUGIN.read_text());opening=next(x for x in data['Records'] if x['EditorId']=='TLM_ACTI_RH_MouthOpen');self.assertIn('use the hoist control',opening['Name'].lower())
        text=a.messages[P+'LabelNine']['Text'];self.assertIn('muster',text);self.assertIn('return alone',text)
        self.assertIn('only a marker',a.messages[P+'LabelCage']['Text'])

class MutationProof(unittest.TestCase):
    def test_removed_arrival_or_commission_guidance_guards_are_caught(self):
        import test_red_hollow as module
        from test_act1 import changed_scripts
        cases=[(' || !Road().At(releasedActor,Ref(Alias_Released))','',
                'test_release_actor_moved_away_does_not_get_arrival_announcement'),
               ('If !busy && !Road().HasArrived() && !IsObjectiveDisplayed(5)','If false',
                'test_sheriff_delivery_opens_visible_road_target_without_forcing_travel')]
        for old,new,method in cases:
            with self.subTest(method=method):
                previous=module.SCRIPTS_NOW
                try:
                    module.SCRIPTS_NOW=changed_scripts('RedHollowWalk.psc',old,new)
                    result=unittest.TextTestRunner(stream=io.StringIO()).run(Guidance(method))
                    self.assertEqual(len(result.errors),0)
                    self.assertEqual(len(result.failures),1)
                finally:module.SCRIPTS_NOW=previous

if __name__=='__main__':unittest.main()
