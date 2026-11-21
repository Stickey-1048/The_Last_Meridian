"""Chapter4 ordinary synthetic playthrough. No native scene/transfer proof."""
from pathlib import Path
import sys,json,unittest,tempfile,shutil
ROOT=Path(__file__).resolve().parent;sys.path.insert(0,str(ROOT.parent/'papyrus_sim'))
from test_four_flags import Fair
from test_sim import SCRIPTS
P='TLM_MSG_BL_';R='TLM_REF_BL_'
class Chapter:
 def __init__(self,t,lead=True,scripts=SCRIPTS,course=2):
  self.t=t;self.f=Fair(t,scripts=scripts);self.s=self.f.s
  if lead:
   self.f.scene(course,Occupation=0,OccupationSeen=0,Take=0);self.f.read();self.f.use('Exit',Exit=0)
  self.q=self.s.quests['TLM_MQ04'];self.rules=next(i for i in self.q.scripts if i.script.name=='TLM:MQ04Quest');self.walk=next(i for i in self.q.scripts if i.script.name=='TLM:BlackLedgerWalk');self.messages=self.f.messages
  original_show=self.s.n_message_show
  def allow_cancel(message,context,*args):
   queued=self.s.answers.get(message.editor_id)
   if queued and queued[0]==-1:
    queued.pop(0);self.s.messages_shown.append(message.editor_id)
    if self.s.on_box:self.s.on_box(message.editor_id)
    return self.s._after_a_frame(-1)
   return original_show(message,context,*args)
  self.s.n_message_show=allow_cancel
 def answers(self,**values):
  self.s.answers={n:[0]*40 for n,m in self.messages.items() if n.startswith(P) and len(m['Buttons'])==1}
  for name,value in values.items():
   if P+name in self.messages:self.s.answers[P+name]=[value];continue
   pages=sorted((n for n in self.messages if n.startswith(P+'S_'+name+'_')),key=lambda n:int(n.rsplit('_',1)[1]));self.t.assertTrue(pages,name)
   for i,page in enumerate(pages):self.s.answers[page]=[value if i==len(pages)-1 else 0]
 def use(self,name,**values):
  self.answers(**values);target='TLM_REF_A1_'+name if name in ('Pritchard','Vane','Haskell') else R+name;self.s.walk_to(target);at=len(self.s.messages_shown);self.s.press_activate(target);self.f.a.p.pause(4);errors=[e for e in self.s.papyrus_log if e.startswith('error')];self.t.assertFalse(errors,errors);return [n.removeprefix(P) for n in self.s.messages_shown[at:] if n.startswith(P)]
 def warrant(self):return self.use('Pritchard',Lead=0,pritchard_warrant=0)
 def enter(self):return self.use('Entry',Travel=0)
 def read(self):return self.use('Read')
 def passage(self):return self.use('Beckett',vickers_door=0,pritchard_warrant_beckett=0,beckett_warrant_terms=1,pritchard_book_receipt=0)
 def leave(self):return self.use('Exit',ExitPrompt=0)
 def public(self):return self.use('Public',PublicReady=0,vane_porch=0,PublicConfirm=0,vane_after_read=0,vane_names=0)
class Lawful(unittest.TestCase):
 def test_first_full_lawful_nonlethal_path(self):
  a=Chapter(self);print('WARRANT',a.warrant());self.assertIn(10,a.q.done);self.assertNotIn(21,a.q.done)
  print('ENTER',a.enter());self.assertIn(21,a.q.done)
  print('READ',a.read());self.assertIn(30,a.q.done)
  print('PASSAGE',a.passage());self.assertIn(43,a.q.done);self.assertNotIn(42,a.q.done);self.assertTrue(a.s.invoke('TLM_MQ04','BookHeld',[]))
  print('LEAVE',a.leave());print('PUBLIC',a.public());self.assertIn(61,a.q.done);self.assertIn(100,a.q.done);self.assertTrue(a.s.invoke('TLM_MQ04','BlackstoneKnown',[]));self.assertTrue(all(not a.s.placed['TLM_REF_A1_'+n].dead for n in ('Vane','Pritchard')));a.use('Finish');self.assertIn(110,a.q.done)
class Adverse(unittest.TestCase):
 def chapter(self,through=''):
  a=Chapter(self)
  for name in ('warrant','enter','read','passage','leave'):
   if not through:break
   getattr(a,name)()
   if name==through:break
  return a
 def test_no_actual_case_read_no_chapter(self):
  a=Chapter(self,False);a.q.done.extend([100]);self.assertFalse(a.s.invoke('TLM_MQ04','LeadKnown',[]));a.s.invoke('TLM_MQ04','SetUp',[])
  self.assertNotIn(10,a.q.done);self.assertFalse(a.q.running)
 def test_cancel_initial_lead_does_not_request_or_move_anyone(self):
  a=self.chapter();before=[tuple(a.s.placed['TLM_REF_A1_'+n].pos) for n in ('Pritchard','Vane')]
  a.use('Pritchard',Lead=-1);self.assertNotIn(10,a.q.done);self.assertFalse(a.rules.vars['warrantrequested'])
  self.assertEqual(before,[tuple(a.s.placed['TLM_REF_A1_'+n].pos) for n in ('Pritchard','Vane')])
 def test_request_is_not_access_and_cancel_travel_preserves_originals(self):
  a=self.chapter('warrant');before=[(x.cell,tuple(x.pos)) for x in [a.s.placed['TLM_REF_A1_'+n] for n in ('Pritchard','Vane')]]
  a.use('Entry',Travel=-1);self.assertNotIn(21,a.q.done)
  self.assertEqual(before,[(x.cell,tuple(x.pos)) for x in [a.s.placed['TLM_REF_A1_'+n] for n in ('Pritchard','Vane')]])
 def test_missing_actual_warrant_blocks_arrival(self):
  a=self.chapter('warrant');a.s._into_container(a.s.placed[R+'Warrant'],a.s.player)
  a.enter();self.assertNotIn(21,a.q.done)
 def test_cancel_each_book_page_then_ordinary_recovery(self):
  for page in range(4):
   with self.subTest(page=page):
    a=self.chapter('enter');a.use('Read',**{'Book'+str(page):-1});self.assertNotIn(30,a.q.done)
    a.read();self.assertIn(30,a.q.done);self.assertNotIn(100,a.q.done)
 def test_each_lawful_dialogue_cancel_never_grants_permission_or_custody(self):
  for node in ('vickers_door','pritchard_warrant_beckett','beckett_warrant_terms','pritchard_book_receipt'):
   with self.subTest(node=node):
    a=self.chapter('read');values=dict(vickers_door=0,pritchard_warrant_beckett=0,beckett_warrant_terms=1,pritchard_book_receipt=0);values[node]=-1
    a.use('Beckett',**values);self.assertNotIn(43,a.q.done);self.assertFalse(a.rules.vars['bookcustodyacknowledged'])
 def test_inspection_permission_does_not_make_signed_receipt_or_book_custody(self):
  a=self.chapter('read');a.use('Beckett',vickers_door=0,pritchard_warrant_beckett=0,beckett_warrant_terms=0)
  self.assertIn(43,a.q.done);self.assertFalse(a.rules.vars['receiptacknowledged']);self.assertFalse(a.rules.vars['bookcustodyacknowledged']);self.assertIsNone(a.s.placed[R+'BlackBook'].container)
 def test_will_is_never_required_or_granted(self):
  a=self.chapter('passage');self.assertIn(43,a.q.done);self.assertNotIn(42,a.q.done)
  self.assertTrue(a.s.invoke('TLM_MQ04','BookHeld',[]))
 def test_fake_base_book_is_not_original_custody(self):
  a=self.chapter('passage');original=a.s.placed[R+'BlackBook'];a.s._into_container(original,None)
  a.s.player.inventory[original.base]=25
  self.assertFalse(a.s.invoke('TLM_MQ04','BookHeld',[]));a.leave();a.public();self.assertNotIn(61,a.q.done)
 def test_cancel_public_ready_confirmation_and_each_page_never_resolves(self):
  for key in ('PublicReady','PublicConfirm','Book0','Book1','Book2','Book3'):
   with self.subTest(key=key):
    a=self.chapter('leave');values=dict(PublicReady=0,vane_porch=0,PublicConfirm=0,vane_after_read=0,vane_names=0);values[key]=-1
    a.use('Public',**values);self.assertNotIn(61,a.q.done);self.assertNotIn(100,a.q.done)
    a.public();self.assertIn(61,a.q.done)
 def test_dead_or_disabled_original_witness_blocks_public_read(self):
  for field in ('dead','disabled'):
   a=self.chapter('leave');setattr(a.s.placed[R+'Witness0'],field,True);a.public();self.assertNotIn(61,a.q.done)
 def test_cancel_source_ack_preserves_genuine_public_history_then_retry(self):
  a=self.chapter('leave');a.use('Public',PublicReady=0,vane_porch=0,PublicConfirm=0,vane_after_read=0,vane_names=-1)
  self.assertIn(61,a.q.done);self.assertNotIn(100,a.q.done)
  a.use('Vane',EarlierChoice=0,vane_after_read=0,vane_names=0);self.assertIn(100,a.q.done)
 def test_haskell_is_independent_source_not_a_public_resolution(self):
  a=self.chapter();a.use('Haskell',EarlierChoice=0,haskell_sheet=0,haskell_tells=0)
  self.assertIn(100,a.q.done);self.assertNotIn(61,a.q.done);self.assertNotIn(110,a.q.done)
 def test_load_during_issued_warrant_never_reissues(self):
  a=self.chapter();original=a.s.n_objectreference_additem;count=[]
  def interrupted(ref,context,form,*args):
   result=original(ref,context,form,*args)
   if form is a.s.placed[R+'Warrant']:
    count.append(1);list(a.s.call(a.rules,a.rules.script.functions['loaded'],[]))
   return result
  a.s.n_objectreference_additem=interrupted;a.warrant();a.warrant()
  self.assertEqual(count,[1]);self.assertEqual(a.rules.vars['pendingtransfer'],1);self.assertTrue(a.rules.vars['transferuncertain']);self.assertNotIn(21,a.q.done)
 def test_partial_page_load_invalidates_ack_and_retry_is_ordinary(self):
  a=self.chapter('enter');fired=[]
  def hook(name):
   if name==P+'Book2' and not fired:fired.append(1);list(a.s.call(a.rules,a.rules.script.functions['loaded'],[]))
  a.s.on_box=hook;a.read();self.assertEqual(fired,[1]);self.assertNotIn(30,a.q.done)
  a.s.on_box=None;a.read();self.assertIn(30,a.q.done)
 def test_original_visitor_move_failure_retains_retry_then_verified_return(self):
  a=self.chapter('warrant');original=a.s.n_objectreference_moveto;fired=[];sheriff=a.s.placed['TLM_REF_A1_Pritchard'];before=(sheriff.cell,tuple(sheriff.pos))
  def fail(ref,context,target,*args):
   if ref is sheriff and target is a.s.placed[R+'SheriffAnchor'] and not fired:fired.append(1);return None
   return original(ref,context,target,*args)
  a.s.n_objectreference_moveto=fail;a.enter();self.assertEqual(fired,[1]);self.assertNotIn(21,a.q.done)
  a.use('Retry');self.assertIn(21,a.q.done);a.leave();self.assertEqual((sheriff.cell,tuple(sheriff.pos)),before);self.assertFalse(any(a.walk.vars['visitpending']))
 def test_late_page_speaker_death_keeps_read_history_no_permission(self):
  a=self.chapter('read');fired=[]
  def hook(name):
   if name.startswith(P+'S_pritchard_warrant_beckett_'):
    fired.append(1);a.s.placed['TLM_REF_A1_Pritchard'].dead=True
  a.s.on_box=hook;a.passage();self.assertTrue(fired);self.assertIn(30,a.q.done);self.assertNotIn(43,a.q.done)
 def test_earlier_roads_and_relief_never_change_through_lawful_route(self):
  a=self.chapter();names=('TLM_MQ01','TLM_SQ01','TLM_MQ02A','TLM_MQ02B','TLM_MQ02C','TLM_MQ03');before={n:(list(a.s.quests[n].done),dict(a.s.quests[n].displayed)) for n in names}
  for action in ('warrant','enter','read','passage','leave','public'):getattr(a,action)()
  a.use('Finish');self.assertEqual(before,{n:(list(a.s.quests[n].done),dict(a.s.quests[n].displayed)) for n in names})
class Boundaries(unittest.TestCase):
 def test_every_actual_fair_course_allows_same_lawful_road_without_pledge(self):
  for course in range(4):
   with self.subTest(course=course):
    a=Chapter(self,course=course);a.warrant();a.enter();a.read();a.passage();self.assertIn(43,a.q.done);self.assertNotIn(42,a.q.done)
 def test_late_public_page_loses_book_or_witness_no_false_resolution(self):
  for lost in ('book','witness','player'):
   a=Chapter(self)
   for action in ('warrant','enter','read','passage','leave'):getattr(a,action)()
   fired=[]
   def hook(name):
    if name==P+'Book3' and not fired:
     fired.append(1)
     if lost=='book':a.s._into_container(a.s.placed[R+'BlackBook'],None)
     elif lost=='witness':a.s.placed[R+'Witness1'].dead=True
     else:a.s.player.dead=True
   a.s.on_box=hook;a.public();self.assertEqual(fired,[1]);self.assertNotIn(61,a.q.done);self.assertNotIn(100,a.q.done)
 def test_late_source_death_never_reverses_true_public_reading(self):
  a=Chapter(self)
  for action in ('warrant','enter','read','passage','leave'):getattr(a,action)()
  fired=[]
  def hook(name):
   if name==P+'S_vane_names_1':fired.append(1);a.s.placed['TLM_REF_A1_Vane'].dead=True
  a.s.on_box=hook;a.public();self.assertEqual(fired,[1]);self.assertIn(61,a.q.done);self.assertNotIn(100,a.q.done);self.assertEqual(a.rules.vars['resolution'],61)
 def test_original_dead_visitor_is_not_resurrected_or_moved_home(self):
  a=Chapter(self);a.warrant();a.enter();vane=a.s.placed['TLM_REF_A1_Vane'];vane.dead=True;before=(vane.cell,tuple(vane.pos));a.leave()
  self.assertTrue(vane.dead);self.assertEqual(before,(vane.cell,tuple(vane.pos)));self.assertFalse(a.walk.vars['visitpending'][1]);self.assertNotIn(61,a.q.done)
 def test_actual_authoritative_alias_replacement_never_becomes_original(self):
  a=Chapter(self);a.warrant();original=a.rules.props['alias_sheriffsource'];replacement=a.s.placed['TLM_REF_A1_Haskell'];original.ref=replacement
  self.assertIsNone(a.s.invoke('TLM_MQ04','OriginalActor',[0]));a.enter();self.assertNotIn(21,a.q.done)
 def test_reentry_preserves_read_and_custody_history_without_duplicate_papers(self):
  a=Chapter(self);a.warrant();a.enter();a.read();a.leave();a.enter();self.assertIn(30,a.q.done)
  self.assertEqual(a.q.done.count(21),1);self.assertEqual(a.q.done.count(30),1);a.passage();self.assertTrue(a.s.invoke('TLM_MQ04','BookHeld',[]))
 def test_cancel_guard_mutant_is_detected_by_real_page_regression(self):
  with tempfile.TemporaryDirectory() as temp:
   root=Path(temp)/'User';shutil.copytree(SCRIPTS,root)
   path=root/'BlackLedgerWalk.psc';text=path.read_text(encoding='utf-8')
   old='BookPages[index].Show() != 0 || !Road().AckReadPage';self.assertEqual(text.count(old),1)
   path.write_text(text.replace(old,'BookPages[index].Show() == 999 || !Road().AckReadPage'),encoding='utf-8')
   a=Chapter(self,scripts=root);a.warrant();a.enter();a.use('Read',Book2=-1)
   self.assertIn(30,a.q.done,'mutant must actually grant the forbidden read receipt')
if __name__=='__main__':unittest.main(verbosity=2)
