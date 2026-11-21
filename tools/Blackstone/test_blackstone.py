from pathlib import Path
import sys,json,unittest,tempfile,shutil
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'tools/BlackLedger'));sys.path.insert(0,str(ROOT/'tools/papyrus_sim'))
from test_black_ledger import Chapter,SCRIPTS
P='TLM_MSG_BS_';R='TLM_REF_BS_'
class Station:
 def __init__(self,t,known=True,before_lead=None,scripts=SCRIPTS):
  self.t=t;self.a=Chapter(t,scripts=scripts);self.s=self.a.s;self.messages=self.a.messages
  previous=self.a.answers
  def answers(**values):
   previous(**values);self.s.answers[P+'MQ04Ready']=[0]*10
  self.a.answers=answers
  self.q=self.s.quests['TLM_MQ05'];self.rules=next(x for x in self.q.scripts if x.script.name=='TLM:MQ05Quest');self.walk=next(x for x in self.q.scripts if x.script.name=='TLM:BlackstoneWalk')
  if known:
   for action in ('warrant','enter','read','passage','leave'):getattr(self.a,action)()
   if before_lead:before_lead(self)
   self.a.public();self.a.use('Finish');self.t.assertIn(10,self.q.done)
 def use(self,role,nodes=None,**values):
  name=R+role;ref=self.s.placed[name];self.t.assertIs(self.s.player.cell,ref.cell,'ordinary walking never teleports across cells: '+role)
  self.s.answers={n:[0]*50 for n,m in self.messages.items() if n.startswith(P) and len(m['Buttons'])==1}
  self.s.answers.update({P+n:[v] for n,v in values.items()})
  for node,value in (nodes or {}).items():
   pages=sorted((n for n in self.messages if n.startswith(P+'N_'+str(node)+'_')),key=lambda n:int(n.rsplit('_',1)[1]))
   self.t.assertTrue(pages)
   for i,page_name in enumerate(pages):self.s.answers[page_name]=[value if i==len(pages)-1 else 0]
  self.s.walk_to(name);at=len(self.s.messages_shown);self.s.press_activate(name);self.a.f.a.p.pause(4);self.t.assertFalse([e for e in self.s.papyrus_log if e.startswith('error')]);return self.s.messages_shown[at:]
 def junction(self):
  point='TLM_REF_NM_MercyTravel';self.t.assertIs(self.s.player.cell,self.s.placed[point].cell);self.s.answers={'TLM_MSG_NM_AskTravel':[0]};self.s.walk_to(point);self.s.press_activate(point);self.a.f.a.p.pause(4);self.t.assertIs(self.s.player.cell,self.s.placed[R+'JunctionRoute'].cell)
 def upper(self):self.junction();return self.use('JunctionRoute',N_0_0=0)
 def service(self):self.upper();return self.use('UpperServiceDoor',ReturnPrompt=0)
class Ordinary(unittest.TestCase):
 def test_first_full_peaceful_documentary_route_without_mara_or_pass(self):
  a=Station(self);a.service();self.assertIn(30,a.q.done)
  a.s.placed[R+'Mara'].dead=True
  a.use('Freight',N_8_0=0);self.assertIn(40,a.q.done);a.use('RiderIndex',N_9_0=0);self.assertIn(45,a.q.done)
  a.use('Diagram',N_22_0=2);self.assertIn(60,a.q.done)
  a.use('MechanicalRelease',MechanicalPrompt=0);self.assertFalse(a.s.placed[R+'ServiceDoor'].locked)
  a.use('ServiceDoor',nodes={23:0,24:0});self.assertIn(70,a.q.done);self.assertIn(100,a.q.done);self.assertNotIn(50,a.q.done);self.assertNotIn(55,a.q.done);self.assertFalse(a.rules.vars['passacknowledged'])
  a.use('LowerReturn',ReturnPrompt=0);a.use('RoomExit',ReturnPrompt=0);a.use('UpperReturn',ReturnPrompt=0);self.assertIs(a.s.player.cell,a.s.placed[R+'JunctionRoute'].cell)

class Adverse(unittest.TestCase):
 def ready(self,read=True):
  a=Station(self);a.service()
  if read:a.use('Freight',nodes={8:0});a.use('RiderIndex',nodes={9:0})
  return a
 def release(self,a):a.use('Diagram',nodes={22:2});a.use('MechanicalRelease',MechanicalPrompt=0)
 def test_fake_source_stage_never_opens_lead(self):
  a=Station(self,False);a.a.q.done.append(100);self.assertFalse(a.s.invoke('TLM_MQ05','OpenLead',[]));self.assertNotIn(10,a.q.done)
 def test_cancel_route_choice_retains_reading_without_arrival_then_retry(self):
  a=Station(self);a.junction();cell=a.s.player.cell;a.use('JunctionRoute',nodes={0:-1});self.assertIn(20,a.q.done);self.assertNotIn(30,a.q.done);self.assertIs(cell,a.s.player.cell)
  a.use('JunctionRoute',nodes={0:0});self.assertIn(30,a.q.done)
 def test_failed_move_cannot_claim_upper_arrival_and_retry_works(self):
  a=Station(self);a.junction();native=a.s.n_objectreference_moveto
  a.s.n_objectreference_moveto=lambda *args:None
  a.use('JunctionRoute',nodes={0:0});self.assertNotIn(30,a.q.done)
  a.s.n_objectreference_moveto=native;a.use('JunctionRoute',nodes={0:0});self.assertIn(30,a.q.done)
 def test_cancel_each_document_page_and_ack_is_no_read_receipt(self):
  for role,kind,stage,node in [('Freight',1,40,8),('RiderIndex',2,45,9),('MaraNote',3,56,21)]:
   a=self.ready(False);start=a.walk.props['documentstart'][kind];count=a.rules.props['documentpages'][kind]
   for page in range(count):
    with self.subTest(role=role,page=page):
     message=a.walk.props['documenttext'][start+page].editor_id
     a.use(role,**{message.removeprefix(P):-1});self.assertNotIn(stage,a.q.done)
   a.use(role,nodes={node:1});self.assertNotIn(stage,a.q.done)
   a.use(role,nodes={node:0});self.assertIn(stage,a.q.done);self.assertNotIn(50,a.q.done);self.assertNotIn(55,a.q.done)
 def test_load_during_last_document_ack_closes_then_retry(self):
  a=self.ready(False);fired=[]
  def hook(name):
   if name.startswith(P+'N_8_') and not fired:fired.append(name);list(a.s.call(a.rules,a.rules.script.functions['loaded'],[]))
  a.s.on_box=hook;a.use('Freight',nodes={8:0});self.assertTrue(fired);self.assertNotIn(40,a.q.done);self.assertFalse(a.walk.vars['busy'])
  a.s.on_box=None;a.use('Freight',nodes={8:0});self.assertIn(40,a.q.done)
 def test_original_document_loss_during_ack_suppresses_receipt_then_retry(self):
  a=self.ready(False);doc=a.s.placed[R+'Freight'];fired=[]
  def hook(name):
   if name.startswith(P+'N_8_') and not fired:fired.append(name);a.s._into_container(doc,a.s.placed[R+'Mara'])
  a.s.on_box=hook;a.use('Freight',nodes={8:0});self.assertTrue(fired);self.assertNotIn(40,a.q.done)
  a.s.on_box=None;a.s._into_container(doc,None);a.use('Freight',nodes={8:0});self.assertIn(40,a.q.done)
 def test_copies_and_alias_replacements_are_not_original_documents(self):
  a=self.ready(False);original=a.s.placed[R+'Freight'];alias=a.rules.props['documents'][1];old=alias.ref
  alias.ref=a.s.placed[R+'MaraNote'];a.s.player.inventory[original.base]=500
  a.use('Freight',nodes={8:0});self.assertNotIn(40,a.q.done)
  alias.ref=old;a.use('Freight',nodes={8:0});self.assertIn(40,a.q.done)
 def test_dead_disabled_fighting_or_missing_mara_does_not_block_document_route(self):
  for mode in ('dead','disabled','combat','missing'):
   with self.subTest(mode=mode):
    a=self.ready();actor=a.s.placed[R+'Mara']
    if mode=='missing':a.rules.props['alias_mara'].ref=None
    elif mode=='combat':actor.combat_target=a.s.placed['TLM_REF_A1_Vane']
    else:setattr(actor,mode,True)
    self.release(a);a.use('ServiceDoor',nodes={23:0,24:0});self.assertIn(100,a.q.done);self.assertNotIn(50,a.q.done);self.assertNotIn(55,a.q.done)
 def test_refusal_is_peaceful_and_reentry_requires_no_commitment(self):
  a=self.ready(False);mara=a.s.placed[R+'Mara'];shown=a.use('Mara',nodes={1:2,6:0});self.assertTrue(any('N_6_' in n for n in shown));self.assertIsNone(mara.combat_target);self.assertFalse(mara.dead);self.assertNotIn(50,a.q.done)
  shown=a.use('Mara',nodes={7:2});self.assertTrue(any('N_7_' in n for n in shown))
 def test_spoken_fifth_and_family_remain_separate_attributed_acknowledgments(self):
  a=self.ready();a.use('Mara',nodes={1:2,6:0});a.use('Mara',nodes={7:1,10:2,14:0,15:1,17:0});self.assertIn(50,a.q.done);self.assertIn(55,a.q.done);self.assertNotIn(56,a.q.done);self.assertNotIn(100,a.q.done)
 def test_no_index_no_hidden_fifth_even_forged_answer(self):
  a=self.ready(False);a.use('Mara',nodes={1:2,6:0});shown=a.use('Mara',nodes={7:2});self.assertEqual(-1,a.s.invoke('TLM_MQ05','AckChoice',[7,1,a.rules.vars['generation']]));self.assertNotIn(50,a.q.done);self.assertFalse(any('N_10_' in n for n in shown))
 def test_death_or_load_during_speech_ack_cannot_grant_testimony(self):
  for mode in ('dead','load'):
   a=self.ready();a.use('Mara',nodes={1:2,6:0});fired=[]
   def hook(name):
    if name.startswith(P+'N_10_') and not fired:
     fired.append(name)
     if mode=='dead':a.s.placed[R+'Mara'].dead=True
     else:list(a.s.call(a.rules,a.rules.script.functions['loaded'],[]))
   a.s.on_box=hook;a.use('Mara',nodes={7:1,10:3});self.assertTrue(fired);self.assertNotIn(50,a.q.done)
 def test_pass_inspection_and_cancel_are_not_custody(self):
  a=self.ready();a.use('ServicePass',PassPrompt=1);self.assertIn(60,a.q.done);self.assertFalse(a.rules.vars['passacknowledged']);self.assertIsNone(a.s.placed[R+'ServicePass'].container)
  a.use('ServicePass',PassPrompt=0);self.assertTrue(a.rules.vars['passacknowledged']);self.assertIs(a.s.player,a.s.placed[R+'ServicePass'].container)
 def test_failed_pass_transfer_load_never_reissues_or_fabricates_custody(self):
  a=self.ready();native=a.s.n_objectreference_additem;fired=[]
  def fail(ref,context,*args):
   if args and args[0] is a.s.placed[R+'ServicePass']:fired.append(1);list(a.s.call(a.rules,a.rules.script.functions['loaded'],[]));return None
   return native(ref,context,*args)
  a.s.n_objectreference_additem=fail;a.use('ServicePass',PassPrompt=0);self.assertEqual([1],fired);self.assertFalse(a.rules.vars['passacknowledged']);self.assertTrue(a.rules.vars['passuncertain'])
  a.s.n_objectreference_additem=native;a.use('ServicePass',PassPrompt=0);self.assertIsNone(a.s.placed[R+'ServicePass'].container);self.release(a);a.use('ServiceDoor',nodes={23:0,24:0});self.assertIn(100,a.q.done)
 def test_cancel_or_failed_mechanical_effect_does_not_unlock_or_enter(self):
  a=self.ready();a.use('Diagram',nodes={22:2});a.use('MechanicalRelease',MechanicalPrompt=-1);self.assertTrue(a.s.placed[R+'ServiceDoor'].locked)
  native=a.s.n_objectreference_lock;a.s.n_objectreference_lock=lambda *args:None;a.use('MechanicalRelease',MechanicalPrompt=0);self.assertFalse(a.rules.vars['releaseobserved']);a.use('ServiceDoor',nodes={23:0});self.assertNotIn(70,a.q.done)
  a.s.n_objectreference_lock=native;a.use('MechanicalRelease',MechanicalPrompt=0);self.assertTrue(a.rules.vars['releaseobserved'])
 def test_entry_cancel_is_not_intent_and_failed_arrival_is_not_completion(self):
  a=self.ready();self.release(a);a.use('ServiceDoor',nodes={23:-1});self.assertNotIn(70,a.q.done)
  native=a.s.n_objectreference_moveto;a.s.n_objectreference_moveto=lambda *args:None;a.use('ServiceDoor',nodes={23:0});self.assertIn(70,a.q.done);self.assertNotIn(100,a.q.done)
  a.s.n_objectreference_moveto=native;a.use('ServiceDoor',nodes={23:0,24:0});self.assertIn(100,a.q.done)
 def test_actual_lower_arrival_without_reading_is_not_completion_then_return_read_and_retry(self):
  a=self.ready(False);self.release(a);a.use('ServiceDoor',nodes={23:0});self.assertIn(70,a.q.done);self.assertNotIn(100,a.q.done);self.assertIs(a.s.player.cell,a.s.placed[R+'LowerArrival'].cell)
  a.use('LowerReturn',ReturnPrompt=0);a.use('Freight',nodes={8:0});a.use('RiderIndex',nodes={9:0});a.use('ServiceDoor',nodes={23:0,24:0});self.assertIn(100,a.q.done)
 def test_boundary_displays_all_pages_and_ordinary_return(self):
  a=self.ready();self.release(a);shown=a.use('ServiceDoor',nodes={23:0,24:1});pages=sorted(n for n in a.messages if n.startswith(P+'N_24_'));self.assertGreater(len(pages),1);self.assertEqual(pages,[n for n in shown if n.startswith(P+'N_24_')]);self.assertIs(a.s.player.cell,a.s.placed[R+'ServiceArrival'].cell)



class AuthoredBranches(unittest.TestCase):
 def test_every_linked_mara_node_executes_without_origin_faction_or_reward_effect(self):
  observed=set()
  paths=[{1:1,2:0,3:0,4:1,5:0},{7:1,10:0,11:0,12:1,20:0},{7:1,10:1,13:1,18:0,19:0},{7:1,10:2,14:1,16:1,6:0},{7:1,10:2,14:3,17:1},{7:1,10:2,14:0,15:1,17:0}]
  for i,path in enumerate(paths):
   with self.subTest(path=i):
    a=Station(self);a.service();a.use('RiderIndex',nodes={9:0});before={k:g.value for k,g in a.s.forms.items() if g.kind=='Global'}
    if i:a.use('Mara',nodes={1:2,6:0})
    shown=a.use('Mara',nodes=path)
    for name in shown:
     if name.startswith(P+'N_'):observed.add(int(name.removeprefix(P+'N_').split('_')[0]))
    self.assertEqual(before,{k:g.value for k,g in a.s.forms.items() if g.kind=='Global'});self.assertNotIn(100,a.q.done);self.assertFalse(a.s.placed[R+'Mara'].dead);self.assertIsNone(a.s.placed[R+'Mara'].combat_target)
  self.assertEqual({1,2,3,4,5,6,7,10,11,12,13,14,15,16,17,18,19,20},observed)

class FinalBoundaries(unittest.TestCase):
 def test_final_original_container_read_load_blocks_ack_and_allows_retry(self):
  from test_final_read import stacker
  a=Station(self);a.service();stack,call=stacker(a.a);native=a.s.n_objectreference_getcontainer;fired=[]
  def late(ref,context):
   result=native(ref,context)
   if ref is a.s.placed[R+'Freight'] and 'ackdocumentpage' in stack and a.rules.vars['readingpage']==a.rules.props['documentpages'][1]-1 and not fired:
    fired.append(1);list(call(a.rules,a.rules.script.functions['loaded'],[]))
   return result
  a.s.n_objectreference_getcontainer=late;a.use('Freight',nodes={8:0});self.assertEqual([1],fired);self.assertNotIn(40,a.q.done)
  a.s.n_objectreference_getcontainer=native;a.use('Freight',nodes={8:0});self.assertIn(40,a.q.done)
 def test_final_current_read_loses_original_before_fresh_container_observation(self):
  from test_final_read import stacker
  a=Station(self);a.service();stack,call=stacker(a.a);native=a.s.n_objectreference_is3dloaded;fired=[];doc=a.s.placed[R+'Freight']
  def late(ref,context):
   result=native(ref,context)
   if ref is a.s.player and 'ackdocumentpage' in stack and 'current' in stack and a.rules.vars['readingpage']==a.rules.props['documentpages'][1]-1 and not fired:
    fired.append(1);a.s._into_container(doc,a.s.placed[R+'Mara'])
   return result
  a.s.n_objectreference_is3dloaded=late;a.use('Freight',nodes={8:0});self.assertEqual([1],fired);self.assertNotIn(40,a.q.done)
 def custody_case(self,scripts=SCRIPTS):
  a=Station(self,scripts=scripts);a.service();fired=[]
  def hook(name):
   if name.startswith(P+'N_8_') and not fired:fired.append(1);a.s._into_container(a.s.placed[R+'Freight'],a.s.placed[R+'Mara'])
  a.s.on_box=hook;a.use('Freight',nodes={8:0});self.assertEqual([1],fired);return a
 def test_custody_guard_mutant_is_killed_by_actual_wrong_read_receipt(self):
  self.assertNotIn(40,self.custody_case().q.done)
  with tempfile.TemporaryDirectory() as name:
   scripts=Path(name)/'User';shutil.copytree(SCRIPTS,scripts)
   path=scripts/'MQ05Quest.psc';text=path.read_text(encoding='utf-8');old='(holder == originalPlayer || (!holder && onDesk))';self.assertEqual(1,text.count(old));path.write_text(text.replace(old,'true'),encoding='utf-8',newline='\n')
   self.assertIn(40,self.custody_case(scripts).q.done,'Mutant must produce the actual forbidden receipt, not a parser failure')
 def test_player_combat_disable_and_load_during_entry_confirmation_never_move(self):
  for mode in ('combat','disabled','load'):
   a=Station(self);a.service();a.use('Freight',nodes={8:0});a.use('RiderIndex',nodes={9:0});a.use('Diagram',nodes={22:2});a.use('MechanicalRelease',MechanicalPrompt=0);before=a.s.player.cell;fired=[]
   def hook(name):
    if name.startswith(P+'N_23_') and not fired:
     fired.append(1)
     if mode=='combat':a.s.placed[R+'Mara'].combat_target=a.s.player
     elif mode=='disabled':a.s.player.disabled=True
     else:list(a.s.call(a.rules,a.rules.script.functions['loaded'],[]))
   a.s.on_box=hook;a.use('ServiceDoor',nodes={23:0});self.assertEqual([1],fired);self.assertNotIn(70,a.q.done);self.assertNotIn(100,a.q.done);self.assertIs(before,a.s.player.cell)

if __name__=='__main__':unittest.main(verbosity=2)

