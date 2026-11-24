"""Exact late Current custody change regression; physical observation is last."""
from pathlib import Path
import sys,unittest,tempfile,shutil
ROOT=Path(__file__).resolve().parents[2];sys.path[:0]=[str(ROOT/'tools/Blackstone'),str(ROOT/'tools/BlackLedger')]
from test_blackstone import Station,R,SCRIPTS
from test_final_read import stacker
NEW='''    Bool playerReady = EffectPlayerReady(playerActor,capturedEpoch)
    ObjectReference currentPass = Road().Documents[5].GetReference()
    Actor currentPlayer = Game.GetPlayer()
    ObjectReference holder = passRef.GetContainer()'''
OLD='''    ObjectReference currentPass = Road().Documents[5].GetReference()
    Actor currentPlayer = Game.GetPlayer()
    ObjectReference holder = passRef.GetContainer()
    Bool playerReady = EffectPlayerReady(playerActor,capturedEpoch)'''
def custody(t,scripts=SCRIPTS,mode='holder'):
 a=Station(t,scripts=scripts);a.service();stack,call=stacker(a.a);doc=a.s.placed[R+'ServicePass'];mara=a.s.placed[R+'Mara'];native=a.s.n_objectreference_is3dloaded;add=a.s.n_objectreference_additem;fired=[];effects=[]
 def late(ref,ctx):
  value=native(ref,ctx)
  if ref is a.s.player and 'passeffectready'in stack and 'effectplayerready'in stack and 'current'in stack and not fired:
   fired.append(1)
   if mode=='holder':a.s._into_container(doc,mara)
   elif mode=='alias':a.rules.props['documents'][5].ref=a.s.placed[R+'MaraNote']
   else:list(call(a.rules,a.rules.script.functions['loaded'],[]))
  return value
 def effect(ref,ctx,*args):effects.append({'holderWasMara':doc.container is mara,'actualOriginal':args[0]is doc});return add(ref,ctx,*args)
 a.s.n_objectreference_is3dloaded=late;a.s.n_objectreference_additem=effect;a.use('ServicePass',PassPrompt=0);t.assertEqual([1],fired);return a,doc,mara,effects
class FinalPassCustody(unittest.TestCase):
 def test_exact_sam_late_current_custody_change_never_steals_or_acknowledges(self):
  a,doc,mara,effects=custody(self);self.assertEqual([],effects);self.assertIs(mara,doc.container);self.assertTrue(a.rules.vars['passissued']);self.assertFalse(a.rules.vars['passacknowledged'])
  a.s._into_container(doc,None);a.use('ServicePass',PassPrompt=0);self.assertEqual([],effects);self.assertIsNone(doc.container,'Issued ambiguity cannot reissue')
 def test_current_alias_replacement_and_load_fire_and_refuse_transfer(self):
  for mode in ('alias','load'):
   with self.subTest(mode=mode):
    a,doc,mara,effects=custody(self,mode=mode);self.assertEqual([],effects);self.assertIsNone(doc.container);self.assertFalse(a.rules.vars['passacknowledged'])
 def test_genuine_original_transfer_and_pure_intent_once_only(self):
  a=Station(self);a.service();epoch=a.rules.vars['generation'];self.assertFalse(a.s.invoke('TLM_MQ05','PassIssuePending',[epoch]));a.use('ServicePass',PassPrompt=0);self.assertIs(a.s.player,a.s.placed[R+'ServicePass'].container);self.assertTrue(a.rules.vars['passacknowledged']);self.assertFalse(a.s.invoke('TLM_MQ05','PassIssuePending',[epoch]))
 def test_old_observation_order_mutant_performs_actual_forbidden_transfer(self):
  with tempfile.TemporaryDirectory()as temp:
   scripts=Path(temp)/'TLM';shutil.copytree(SCRIPTS,scripts);p=scripts/'BlackstoneWalk.psc';s=p.read_text(encoding='utf-8');self.assertEqual(1,s.count(NEW));p.write_text(s.replace(NEW,OLD),encoding='utf-8',newline='\n')
   a,doc,mara,effects=custody(self,scripts);self.assertEqual([{'holderWasMara':True,'actualOriginal':True}],effects);self.assertIs(a.s.player,doc.container);self.assertTrue(a.rules.vars['passacknowledged'],'Mutant proves real forbidden transfer, not parser failure or unfired hook')
if __name__=='__main__':unittest.main(verbosity=2)
