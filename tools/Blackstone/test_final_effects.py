"""F1 actual last preparation-read injections; every callback must fire."""
from pathlib import Path
import sys,unittest,tempfile,shutil
ROOT=Path(__file__).resolve().parents[2];sys.path[:0]=[str(ROOT/'tools/Blackstone'),str(ROOT/'tools/BlackLedger')]
from test_blackstone import Station,R,SCRIPTS
from test_final_read import stacker

def travel(t,mode,scripts=SCRIPTS):
 a=Station(t,scripts=scripts);a.junction();stack,call=stacker(a.a);control=a.s.placed[R+'JunctionRoute'];dest=a.s.placed[R+'UpperArrival'];native=a.s.n_objectreference_isdisabled;move=a.s.n_objectreference_moveto;fired=[];effects=[]
 def late(ref,ctx):
  value=native(ref,ctx)
  if ref is dest and 'moveplayer'in stack and 'travelcontext'in stack and not fired:
   fired.append(1)
   if mode=='player-dead':a.s.player.dead=True
   else:control.disabled=True
  return value
 def effect(ref,ctx,*args):effects.append((a.s.player.dead,control.disabled));return move(ref,ctx,*args)
 a.s.n_objectreference_isdisabled=late;a.s.n_objectreference_moveto=effect;a.use('JunctionRoute',nodes={0:0});t.assertEqual([1],fired);return a,effects,native,move
class EffectBoundary(unittest.TestCase):
 def test_original_final_travel_read_player_death_and_control_loss_no_effect_then_retry(self):
  for mode in ('player-dead','control-disabled'):
   with self.subTest(mode=mode):
    a,effects,native,move=travel(self,mode);self.assertEqual([],effects);self.assertNotIn(30,a.q.done)
    a.s.n_objectreference_isdisabled=native;a.s.player.dead=False;a.s.placed[R+'JunctionRoute'].disabled=False;a.use('JunctionRoute',nodes={0:0});self.assertIn(30,a.q.done)
 def test_original_final_direct_pass_container_read_player_death_no_transfer(self):
  a=Station(self);a.service();stack,call=stacker(a.a);doc=a.s.placed[R+'ServicePass'];native=a.s.n_objectreference_getcontainer;add=a.s.n_objectreference_additem;fired=[];effects=[]
  def late(ref,ctx):
   value=native(ref,ctx)
   if ref is doc and stack[-1]=='readdocument' and a.rules.vars['passissued'] and not fired:fired.append(1);a.s.player.dead=True
   return value
  def effect(ref,ctx,*args):effects.append(1);return add(ref,ctx,*args)
  a.s.n_objectreference_getcontainer=late;a.s.n_objectreference_additem=effect;a.use('ServicePass',PassPrompt=0);self.assertEqual([1],fired);self.assertEqual([],effects);self.assertIsNone(doc.container);self.assertTrue(a.rules.vars['passissued']);self.assertFalse(a.rules.vars['passacknowledged'])
  a.s.player.dead=False;a.s.n_objectreference_getcontainer=native;a.use('ServicePass',PassPrompt=0);self.assertEqual([],effects,'No replay/reissue after issued intent')
 def test_helper_pass_actual_final_read_load_and_death_are_fired_and_suppressed(self):
  for mode in ('load','dead'):
   a=Station(self);a.service();a.use('ServicePass',PassPrompt=1);stack,call=stacker(a.a);doc=a.s.placed[R+'ServicePass'];native=a.s.n_objectreference_getcontainer;add=a.s.n_objectreference_additem;fired=[];effects=[]
   def late(ref,ctx):
    value=native(ref,ctx)
    if ref is doc and stack[-1]=='takepass' and a.rules.vars['passissued'] and not fired:
     fired.append(1)
     if mode=='load':list(call(a.rules,a.rules.script.functions['loaded'],[]))
     else:a.s.player.dead=True
    return value
   def effect(ref,ctx,*args):effects.append(1);return add(ref,ctx,*args)
   a.s.n_objectreference_getcontainer=late;a.s.n_objectreference_additem=effect
   # Exercise the second helper with genuine inspected original and real local
   # stance. This is a method-level probe, not a claimed ordinary diagram jump.
   a.s.invoke('TLM_MQ05','TakePass',[a.rules.vars['generation']])
   self.assertEqual([1],fired);self.assertEqual([],effects);self.assertIsNone(doc.container);self.assertFalse(a.rules.vars['passacknowledged'])
 def test_mechanical_and_pass_unlock_final_native_player_loss_never_lock(self):
  for mechanical in (True,False):
   a=Station(self);a.service();a.use('Freight',nodes={8:0});a.use('RiderIndex',nodes={9:0})
   if mechanical:a.use('Diagram',nodes={22:2})
   else:a.use('ServicePass',PassPrompt=0)
   stack,call=stacker(a.a);door=a.s.placed[R+'ServiceDoor'];native=a.s.n_objectreference_is3dloaded;lock=a.s.n_objectreference_lock;fired=[];effects=[]
   def late(ref,ctx):
    value=native(ref,ctx)
    if ref is door and 'dooreffectready'in stack and not fired:fired.append(1);a.s.player.dead=True
    return value
   def effect(ref,ctx,*args):effects.append(1);return lock(ref,ctx,*args)
   a.s.n_objectreference_is3dloaded=late;a.s.n_objectreference_lock=effect
   if mechanical:a.use('MechanicalRelease',MechanicalPrompt=0)
   else:a.use('ServiceDoor',nodes={23:0})
   self.assertEqual([1],fired);self.assertEqual([],effects);self.assertTrue(door.locked);self.assertNotIn(70,a.q.done)
   a.s.player.dead=False;a.s.n_objectreference_is3dloaded=native
   if mechanical:a.use('MechanicalRelease',MechanicalPrompt=0);self.assertFalse(door.locked)
   else:a.use('ServiceDoor',nodes={23:0,24:0});self.assertIn(100,a.q.done)
 def test_old_travel_effect_order_mutant_produces_actual_forbidden_move(self):
  with tempfile.TemporaryDirectory()as temp:
   scripts=Path(temp)/'TLM';shutil.copytree(SCRIPTS,scripts);p=scripts/'BlackstoneWalk.psc';s=p.read_text(encoding='utf-8');old='If !TravelEffectReady(route,playerActor,destination,capturedEpoch)';self.assertEqual(1,s.count(old));p.write_text(s.replace(old,'If capturedEpoch != Road().Epoch()'),encoding='utf-8',newline='\n')
   a,effects,_,_=travel(self,'control-disabled',scripts);self.assertEqual([(False,True)],effects);self.assertIn(30,a.q.done,'Forbidden real effect/receipt, not parse failure')
if __name__=='__main__':unittest.main(verbosity=2)
