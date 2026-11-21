"""Actual new Roark activation continuation on current PSC, synthetic natives only."""
from pathlib import Path
import sys,json,unittest,tempfile
ROOT=Path(__file__).resolve().parent;sys.path.insert(0,str(ROOT.parent/'papyrus_sim'))
from test_red_hollow import Hollow,P
from sim import SimError
class RoarkDepth(unittest.TestCase):
 def settle(self,terms=False):
  a=Hollow(self);a.below()
  if terms:
   a.use('Gallery',StageTravel=0);a.use('Dorn',dorn_door=0,dorn_terms=0,dorn_sworn=0);a.use('FromGallery',StageTravel=0)
  a.rescue()
  if not terms:a.finish57()
  return a
 def say(self,a,**answers):
  a.raw[P+'RhaRoarkPartial10']=0
  if a.ref('Roark').disabled:
   start=len(a.s.messages_shown)
   with self.assertRaises(SimError):a.s.press_activate(a.ref('Roark').editor_id)
   a.s.invoke('TLM_RH','RoarkTalk',[]);return a.s.messages_shown[start:]
  a.pos('Roark');a.s.answers={P+k:[v] for k,v in answers.items()};start=len(a.s.messages_shown);a.s.press_activate(a.ref('Roark').editor_id);a.wait();self.assertFalse([e for e in a.s.papyrus_log if e.startswith('error')]);return a.s.messages_shown[start:]
 def branch(self,a,choice=0):return self.say(a,RhaRoarkAll=1,RdcQuiet=choice,RdcTired=0,RdcThanks=0)
 def test_normal_original_activation_opens_optional_quiet_and_both_continuations(self):
  for choice,end in [(0,'RdcTired'),(1,'RdcThanks')]:
   a=self.settle();before=a.snapshot();inventory=dict(a.s.player.inventory);stages=list(a.q.done);shown=self.branch(a,choice)
   self.assertEqual([x for x in shown if x.startswith(P+'Rdc')],[P+'RdcQuiet',P+end]);self.assertEqual(a.snapshot(),before);self.assertEqual(a.s.player.inventory,inventory);self.assertEqual(a.q.done,stages);self.assertEqual(a.g('Reported'),0)
 def test_actual_terms_delivery_entry_and_linked_answer(self):
  a=self.settle(True);self.assertFalse(a.v('termsAcknowledged'));before=a.snapshot();shown=self.say(a,RhaRoarkAll=0,RhaTerms=1,RdcTerms=1,RdcTermsAnswer=0)
  self.assertTrue(a.v('termsAcknowledged'));self.assertEqual([x for x in shown if x.startswith(P+'Rdc')],[P+'RdcTerms',P+'RdcTermsAnswer']);self.assertEqual(a.snapshot(),before);self.assertEqual(a.g('Reported'),0)
 def test_existing_continue_and_close_choices_do_not_force_new_character_pages(self):
  a=self.settle();shown=self.say(a,RhaRoarkAll=0,RhaOpen=0);self.assertFalse(any(x.startswith(P+'Rdc') for x in shown))
  for answer in (-1,2,7):
   a=self.settle();a.raw[P+'RdcQuiet']=answer;shown=self.branch(a);self.assertEqual([x for x in shown if x.startswith(P+'Rdc')],[P+'RdcQuiet'])
 def test_current_miners_missing_disabled_displaced_dead_and_replaced_never_quiet(self):
  for mode in ('missing','disabled','displaced','dead','replaced'):
   a=self.settle()
   if mode=='missing':a.rules.props['miners'][2].ref=None
   if mode=='disabled':a.ref('Miner03').disabled=True
   if mode=='displaced':a.ref('Miner03').pos=(99999,0,0)
   if mode=='dead':a.die('Miner03',True)
   if mode=='replaced':a.rules.props['miners'][2].ref=a.ref('Blevins')
   shown=self.branch(a);self.assertFalse(any(x.startswith(P+'Rdc') for x in shown),mode)
 def test_post_quiet_cancel_context_loss_and_load_never_continue_or_commit(self):
  for mode in ('death','disable','playercombat','speaker','load','pending','terms'):
   a=self.settle();before=a.snapshot()
   def change(mid):
    if mid!=P+'RdcQuiet':return
    if mode=='death':a.ref('Miner03').dead=True
    if mode=='disable':a.ref('Miner03').disabled=True
    if mode=='playercombat':a.ref('Blevins').combat_target=a.s.player
    if mode=='speaker':a.walk.props['alias_roark'].ref=a.ref('Blevins')
    if mode=='load':a.s.spawn(a.s.call(a.walk,a.walk.script.functions['loaded'],[]),'load interruption')
    if mode=='pending':a.rules.vars['mineintent']=3
    if mode=='terms':a.rules.vars['breakplan']=True
   a.s.on_box=change;shown=self.branch(a);self.assertIn(P+'RdcQuiet',shown);self.assertNotIn(P+'RdcTired',shown,mode);self.assertEqual(a.g('Reported'),0)
 def test_original_speaker_and_current_player_required(self):
  for mode in ('dead','disabled','alias','original','far'):
   a=self.settle()
   if mode=='dead':a.ref('Roark').dead=True
   if mode=='disabled':a.ref('Roark').disabled=True
   if mode=='alias':a.walk.props['alias_roark'].ref=a.ref('Blevins')
   if mode=='original':a.walk.props['rhaoriginalroark']=a.ref('Blevins')
   # Reposition via callback AFTER ordinary helper position to preserve adverse distance.
   if mode=='far':a.s.on_box=lambda mid:setattr(a.s.player,'pos',(99999,0,0))
   shown=self.branch(a);self.assertFalse(any(x.startswith(P+'Rdc') for x in shown),mode)
 def test_late_context_cohort_loss_fires_then_blocks_first_character_page(self):
  a=self.settle();old=a.s.n_objectreference_isindialoguewithplayer;fired=[]
  def late(ref,ctx):
   value=old(ref,ctx)
   if ref is a.ref('Roark') and P+'RhaRoarkAll' in a.s.messages_shown and not fired:fired.append(True);a.ref('Miner03').disabled=True
   return value
  a.s.n_objectreference_isindialoguewithplayer=late;shown=self.branch(a);self.assertEqual(fired,[True]);self.assertFalse(any(x.startswith(P+'Rdc') for x in shown))
 def test_reentry_is_explicit_and_no_repeat_reward(self):
  a=self.settle();before=a.snapshot();inv=dict(a.s.player.inventory);self.branch(a);self.branch(a,1);self.assertEqual(a.snapshot(),before);self.assertEqual(a.s.player.inventory,inv)
 def test_exact_all_five_approved_speech_and_choice_limits(self):
  packet=json.loads((ROOT/'approved-nodes.json').read_text(encoding='utf-8'));names=['RdcQuiet','RdcTired','RdcThanks','RdcTerms','RdcTermsAnswer'];a=self.settle()
  for name,node in zip(names,packet['nodes']):
   message=a.messages[P+name];self.assertEqual(message['Text'],'[Roark]\n\n'+node['text']);self.assertEqual([b['Text'] for b in message['Buttons']],[c['label'] for c in node['choices']]);self.assertLessEqual(len(node['text']),240);self.assertTrue(all(len(c['label'])<=48 for c in node['choices']))
 def test_all_eleven_slots_individually_protect_quiet_scene(self):
  for index in range(1,12):
   a=self.settle();a.ref('Miner%02d'%index).disabled=True;shown=self.branch(a);self.assertFalse(any(x.startswith(P+'Rdc') for x in shown),index)
 def test_terms_receipt_lost_during_optional_page_closes_without_answer(self):
  a=self.settle(True)
  def change(mid):
   if mid==P+'RdcTerms':a.rules.vars['termsacknowledged']=False
  a.s.on_box=change;shown=self.say(a,RhaRoarkAll=0,RhaTerms=1,RdcTerms=1,RdcTermsAnswer=0);self.assertIn(P+'RdcTerms',shown);self.assertNotIn(P+'RdcTermsAnswer',shown);self.assertTrue(a.s.invoke('TLM_MQ02C','PactMade',[]));self.assertEqual(a.g('Reported'),0)
 def late_depth(self,a):
  stack=[];fired=[];oldcall=a.s.call;old=a.s.n_objectreference_isindialoguewithplayer
  def call(inst,fn,args,named=None):
   stack.append(fn.name.lower())
   try:return (yield from oldcall(inst,fn,args,named))
   finally:stack.pop()
  def late(ref,ctx):
   value=old(ref,ctx)
   if 'roarkdepthcontext' in stack and ref is a.ref('Roark') and not fired:fired.append(True);a.ref('Miner03').disabled=True
   return value
  a.s.call=call;a.s.n_objectreference_isindialoguewithplayer=late;return fired
 def test_actual_new_context_late_cohort_callback_fires_before_new_page(self):
  a=self.settle();fired=self.late_depth(a);shown=self.branch(a);self.assertEqual(fired,[True]);self.assertFalse(any(x.startswith(P+'Rdc') for x in shown))
 def test_new_context_cohort_guard_mutant_exposes_false_all_eleven_page(self):
  import shutil,test_red_hollow
  with tempfile.TemporaryDirectory() as folder:
   source=Path(folder);original=test_red_hollow.SCRIPTS_NOW
   for p in original.glob('*.psc'):shutil.copyfile(p,source/p.name)
   p=source/'RedHollowWalk.psc';text=p.read_text(encoding='utf-8-sig');old='Return AftermathRow() == 11 && AftermathMark() == before';self.assertEqual(text.count(old),1);p.write_text(text.replace(old,'Return true'),encoding='utf-8')
   test_red_hollow.SCRIPTS_NOW=source
   try:
    a=self.settle();fired=self.late_depth(a);shown=self.branch(a);self.assertEqual(fired,[True]);self.assertIn(P+'RdcQuiet',shown)
   finally:test_red_hollow.SCRIPTS_NOW=original
 def test_exact_owned_artifact_preservation_and_old_missing_new_rejection(self):
  import verify
  main=ROOT/'build/licensed-master-001/TheLastMeridian.esp';world=ROOT/'build/licensed-world-003/TLMWorldSlice.esp';self.assertEqual(verify.artifact_problems(main,world),[])
  old=ROOT.parents[3]/'work/rh-return-account-build-f491eeb/build/licensed-return-account-skeleton-001/bundle/TheLastMeridian.esp';self.assertTrue(verify.artifact_problems(old,world))
  data=world.read_bytes();original=b'TLM_WS_BoundaryEast21';self.assertIn(original,data)
  with tempfile.TemporaryDirectory() as folder:
   bad=Path(folder)/'TLMWorldSlice.esp';bad.write_bytes(data.replace(original,b'TLM_WS_BoundaryEastXX',1));self.assertTrue(verify.artifact_problems(main,bad))
 def test_successor_source_guard_nominal_and_unauthorized_workflow_negative(self):
  import verify
  from unittest.mock import patch
  self.assertEqual(verify.problems(),[]);native=verify.subprocess.check_output
  def changed(args,**kwargs):
   value=native(args,**kwargs)
   if args[:3]==['git','diff','--name-only']:return value+'.github/workflows/portable-checks.yml\n'
   return value
  with patch.object(verify.subprocess,'check_output',changed):self.assertIn('Change outside exact reviewed successor',verify.problems())
if __name__=='__main__':unittest.main(verbosity=2)
