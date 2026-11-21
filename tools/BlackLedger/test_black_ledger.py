"""Chapter4 ordinary synthetic playthrough. No native scene/transfer proof."""
from pathlib import Path
import sys,json,unittest
ROOT=Path(__file__).resolve().parent;sys.path.insert(0,str(ROOT.parent/'papyrus_sim'))
from test_four_flags import Fair
P='TLM_MSG_BL_';R='TLM_REF_BL_'
class Chapter:
 def __init__(self,t,lead=True):
  self.t=t;self.f=Fair(t);self.s=self.f.s
  if lead:
   self.f.scene(2);self.f.read();self.f.use('Exit',Exit=0)
  self.q=self.s.quests['TLM_MQ04'];self.rules=next(i for i in self.q.scripts if i.script.name=='TLM:MQ04Quest');self.walk=next(i for i in self.q.scripts if i.script.name=='TLM:BlackLedgerWalk');self.messages=self.f.messages
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
if __name__=='__main__':unittest.main(verbosity=2)
