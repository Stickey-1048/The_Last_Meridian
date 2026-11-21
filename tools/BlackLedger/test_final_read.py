"""Late-read/effect regressions seeded at the reviewer's actual final native reads."""
from pathlib import Path
import shutil,tempfile,unittest
from test_black_ledger import Chapter,R,SCRIPTS

def stacker(a):
 stack=[];original=a.s.call
 def call(inst,fn,args,named=None):
  stack.append(fn.name.lower())
  try:return(yield from original(inst,fn,args,named))
  finally:stack.pop()
 a.s.call=call;return stack,original

def prepare(t,through,scripts=SCRIPTS):
 a=Chapter(t,scripts=scripts)
 for name in ('warrant','enter','read','passage','leave'):
  getattr(a,name)()
  if name==through:break
 return a

def receipt_loss(t,scripts=SCRIPTS):
 a=prepare(t,'read',scripts);stack,call=stacker(a);native=a.s.n_objectreference_is3dloaded;add=a.s.n_objectreference_additem;fired=[];issued=[];beckett=a.s.placed[R+'Beckett']
 def late(ref,context):
  result=native(ref,context)
  if ref is a.s.player and 'transfer' in stack and 'current' in stack and not any(n in stack for n in ('transfereligible','marktransferissued','speaker','beckett')) and a.rules.vars['pendingtransfer']==2 and a.rules.vars['transferissued'] and not fired:fired.append(1);beckett.dead=True
  return result
 def effect(ref,context,form,*args):
  if form is a.s.placed[R+'Receipt']:issued.append(beckett.dead)
  return add(ref,context,form,*args)
 a.s.n_objectreference_is3dloaded=late;a.s.n_objectreference_additem=effect;a.passage()
 return a,fired,issued

class FinalBoundary(unittest.TestCase):
 def test_second_final_public_book_read_load_refuses_then_ordinary_retry(self):
  a=prepare(self,'leave');stack,call=stacker(a);old=a.s.n_objectreference_getcontainer;fired=[];reads=[]
  def late(ref,context):
   result=old(ref,context)
   if ref is a.s.placed[R+'BlackBook'] and 'commitpublicread' in stack and 'bookheld' in stack and not fired:
    reads.append(1)
    if len(reads)==2:fired.append(1);list(call(a.rules,a.rules.script.functions['loaded'],[]))
   return result
  a.s.n_objectreference_getcontainer=late;a.public();self.assertEqual(fired,[1]);self.assertEqual(reads,[1,1]);self.assertEqual(a.rules.vars['generation'],1);self.assertEqual(a.rules.vars['publicepoch'],-1);self.assertNotIn(61,a.q.done);self.assertNotIn(100,a.q.done)
  a.s.n_objectreference_getcontainer=old;a.public();self.assertIn(61,a.q.done);self.assertIn(100,a.q.done)
 def test_second_final_private_context_actual_book_loss_refuses_then_return_recovery(self):
  a=prepare(self,'enter');book=a.s.placed[R+'BlackBook'];a.s.n_objectreference_additem(a.s.player,None,book,1,True);stack,call=stacker(a);old=a.s.n_objectreference_is3dloaded;fired=[];reads=[]
  def late(ref,context):
   result=old(ref,context)
   if ref is a.s.player and 'ackreadpage' in stack and 'bookaccess' in stack and 'current' in stack and a.rules.vars['readpage']==3 and not fired:
    reads.append(1)
    if len(reads)==2:fired.append(1);a.s._into_container(book,a.s.placed['TLM_REF_A1_Haskell'])
   return result
  a.s.n_objectreference_is3dloaded=late;a.read();self.assertEqual(fired,[1]);self.assertEqual(reads,[1,1]);self.assertNotIn(30,a.q.done);self.assertIs(book.container,a.s.placed['TLM_REF_A1_Haskell'])
  a.s.n_objectreference_is3dloaded=old;a.s._into_container(book,a.s.player);a.read();self.assertIn(30,a.q.done)
 def test_late_saved_disabled_read_death_never_moves_corpse(self):
  a=Chapter(self);a.warrant();sheriff=a.s.placed['TLM_REF_A1_Pritchard'];before=(sheriff.cell,tuple(sheriff.pos));stack,call=stacker(a);old=a.s.n_objectreference_isdisabled;move=a.s.n_objectreference_moveto;reads=[];fired=[];moves=[]
  def late(ref,context):
   result=old(ref,context)
   if ref is sheriff and 'stageoriginals' in stack and not fired:
    reads.append(1)
    if len(reads)==2:fired.append(1);sheriff.dead=True
   return result
  def effect(ref,context,target,*args):
   if ref is sheriff:moves.append(sheriff.dead)
   return move(ref,context,target,*args)
  a.s.n_objectreference_isdisabled=late;a.s.n_objectreference_moveto=effect;a.enter();self.assertEqual(fired,[1]);self.assertEqual(moves,[]);self.assertEqual(before,(sheriff.cell,tuple(sheriff.pos)));self.assertTrue(sheriff.dead);self.assertNotIn(21,a.q.done);a.leave();self.assertNotIn(110,a.q.done)
 def test_late_beckett_death_no_receipt_issue_and_no_false_ack(self):
  a,fired,issued=receipt_loss(self);self.assertEqual(fired,[1]);self.assertEqual(issued,[]);self.assertIsNone(a.s.placed[R+'Receipt'].container);self.assertEqual(a.rules.vars['pendingtransfer'],2);self.assertFalse(a.rules.vars['receiptacknowledged']);self.assertNotIn(61,a.q.done)
 def test_receipt_effect_guard_mutant_reproduces_forbidden_actual_issue(self):
  with tempfile.TemporaryDirectory() as temp:
   root=Path(temp)/'TLM';shutil.copytree(SCRIPTS,root);path=root/'BlackLedgerWalk.psc';text=path.read_text(encoding='utf-8');line='If !Road().EffectParticipants(kind,capturedEpoch)';self.assertEqual(text.count(line),1);path.write_text(text.replace(line,'If false'),encoding='utf-8')
   a,fired,issued=receipt_loss(self,root);self.assertEqual(fired,[1]);self.assertEqual(issued,[True]);self.assertIs(a.s.placed[R+'Receipt'].container,a.s.player);self.assertFalse(a.rules.vars['receiptacknowledged'])
 def test_late_return_context_death_never_moves_original_corpse(self):
  a=prepare(self,'enter');sheriff=a.s.placed['TLM_REF_A1_Pritchard'];before=(sheriff.cell,tuple(sheriff.pos));stack,call=stacker(a);old=a.s.n_objectreference_is3dloaded;move=a.s.n_objectreference_moveto;fired=[];moves=[]
  def late(ref,context):
   result=old(ref,context)
   if ref is a.s.player and 'returnoriginals' in stack and 'current' in stack and not fired:fired.append(1);sheriff.dead=True
   return result
  def effect(ref,context,target,*args):
   if ref is sheriff:moves.append(sheriff.dead)
   return move(ref,context,target,*args)
  a.s.n_objectreference_is3dloaded=late;a.s.n_objectreference_moveto=effect;a.leave();self.assertEqual(fired,[1]);self.assertEqual(moves,[]);self.assertEqual(before,(sheriff.cell,tuple(sheriff.pos)));self.assertNotIn(110,a.q.done)
 def test_porch_anchor_preparation_death_never_moves_original_corpse(self):
  a=prepare(self,'passage');sheriff=a.s.placed['TLM_REF_A1_Pritchard'];stack,call=stacker(a);old=a.s.n_objectreference_moveto;fired=[];moves=[]
  def effect(ref,context,target,*args):
   result=old(ref,context,target,*args)
   if 'prepareporch' in stack and ref is a.s.placed[R+'SheriffAnchor'] and not fired:fired.append(1);sheriff.dead=True
   if 'prepareporch' in stack and ref is sheriff:moves.append(sheriff.dead)
   return result
  a.s.n_objectreference_moveto=effect;a.leave();self.assertEqual(fired,[1]);self.assertEqual(moves,[]);self.assertTrue(sheriff.dead);self.assertNotIn(61,a.q.done)
 def test_witness_enable_death_never_moves_own_witness_corpse(self):
  a=prepare(self,'passage');witness=a.s.placed[R+'Witness0'];stack,call=stacker(a);old=a.s.n_objectreference_enable;move=a.s.n_objectreference_moveto;fired=[];moves=[]
  def late(ref,context,*args):
   result=old(ref,context,*args)
   if ref is witness and 'prepareporch' in stack and not fired:fired.append(1);witness.dead=True
   return result
  def effect(ref,context,target,*args):
   if ref is witness and 'prepareporch' in stack:moves.append(witness.dead)
   return move(ref,context,target,*args)
  a.s.n_objectreference_enable=late;a.s.n_objectreference_moveto=effect;a.leave();self.assertEqual(fired,[1]);self.assertEqual(moves,[]);self.assertNotIn(61,a.q.done)
if __name__=='__main__':unittest.main(verbosity=2)
