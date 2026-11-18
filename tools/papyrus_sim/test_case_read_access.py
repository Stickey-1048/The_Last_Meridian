"""Actual MQ03 PSC final access boundary, seeded native changes; not game proof."""
import io,tempfile,unittest,shutil
from pathlib import Path
from test_sim import SCRIPTS
from test_four_flags import Fair,R,Q

class CurrentReadAccess(unittest.TestCase):
    def prepared(self,held=True,scripts=SCRIPTS):
        a=Fair(self,scripts=scripts);a.scene(3 if held else 0,Occupation=0,OccupationSeen=0,Take=0);return a
    def final_hook(self,a,action,when='context'):
        original=a.s.placed[R+'OriginalCase'];oldcall=a.s.call;oldread=a.s.n_objectreference_getcontainer;oldscene=a.s.n_actor_isinscene
        inside=[];reads=[];fired=[]
        def call(inst,fn,args,named=None):
            if fn.name.lower()=='finishread':
                inside.append(True)
                try:return (yield from oldcall(inst,fn,args,named))
                finally:inside.pop()
            return (yield from oldcall(inst,fn,args,named))
        def read(ref,ctx):
            result=oldread(ref,ctx)
            if inside and ref is original:
                reads.append(True)
                if when=='final-container' and len(reads)==2 and not fired:fired.append(True);action()
            return result
        def scene(ref,ctx):
            result=oldscene(ref,ctx)
            if inside and reads and when=='context' and not fired:fired.append(True);action()
            return result
        a.s.call=call;a.s.n_objectreference_getcontainer=read;a.s.n_actor_isinscene=scene
        def restore():a.s.call=oldcall;a.s.n_objectreference_getcontainer=oldread;a.s.n_actor_isinscene=oldscene
        return fired,restore
    def intact_history(self,a):
        self.assertTrue(a.v('caseHistoricalRead'));self.assertTrue(a.v('caseTaken'));self.assertEqual(a.v('response'),44)
        for stage in (44,60,70):self.assertIn(stage,a.q.done)
        self.assertNotIn(100,a.q.done);self.assertNotIn(101,a.q.done)
    def test_late_current_custody_loss_refuses_solo_and_public_and_recovers(self):
        for public in (False,True):
            a=self.prepared();original=a.s.placed[R+'OriginalCase'];outsider=a.s.placed[R+'Flint']
            fired,restore=self.final_hook(a,lambda:a.s.n_objectreference_additem(outsider,None,original,1,True));a.read(public)
            self.assertEqual(len(fired),1);self.assertIs(original.container,outsider);self.intact_history(a)
            self.assertFalse(a.s.invoke(Q,'Held',[]));restore()
            # SEEDED distinct genuine return, never automatic product recovery.
            recipient=a.originals[0] if public else a.s.player;a.s.n_objectreference_additem(recipient,None,original,1,True)
            a.read(public);self.assertIn(100,a.q.done);self.assertEqual(101 in a.q.done,public);self.assertIs(original.container,recipient)
    def test_late_alias_player_participant_and_context_failures_keep_history(self):
        for public,mode in ((False,'alias'),(False,'missing'),(False,'player'),(False,'dead'),(False,'remote'),(False,'load'),(True,'speaker'),(True,'speaker-dead')):
            with self.subTest(public=public,mode=mode):
                a=self.prepared();original=a.s.placed[R+'OriginalCase'];sheriff=a.originals[0]
                def change():
                    if mode=='alias':a.rules.props['alias_originalcase'].ref=a.s.placed[R+'OriginalSilver']
                    elif mode=='missing':a.rules.props['alias_originalcase'].ref=None
                    elif mode=='player':a.rules.props['alias_player'].ref=a.s.placed[R+'Flint']
                    elif mode=='dead':a.s.player.dead=True
                    elif mode=='remote':a.s.player.cell=a.s._cell('UnrelatedLateCell')
                    elif mode=='load':a.load_inside_native()
                    elif mode=='speaker':a.rules.props['cast'][0].ref=a.s.placed[R+'Flint']
                    else:sheriff.dead=True
                fired,restore=self.final_hook(a,change);a.read(public);self.assertEqual(len(fired),1);self.intact_history(a);restore()
                self.assertIs(original.container,sheriff if public else a.s.player)
    def test_generation_is_checked_after_final_native_container_read(self):
        for public in (False,True):
            a=self.prepared();old=a.v('generation');fired,restore=self.final_hook(a,a.load_inside_native,'final-container');a.read(public)
            self.assertEqual(len(fired),1);self.assertGreater(a.v('generation'),old);self.intact_history(a);restore()
            a.read(public);self.assertIn(100,a.q.done);self.assertEqual(101 in a.q.done,public)
    def test_valid_player_ground_public_and_solo_original_sheriff_access(self):
        for mode in ('held','ground','public','sheriff-solo'):
            with self.subTest(mode=mode):
                a=self.prepared(held=mode=='held');original=a.s.placed[R+'OriginalCase']
                if mode=='sheriff-solo':a.s.n_objectreference_additem(a.originals[0],None,original,1,True)
                a.read(mode=='public');self.assertIn(60,a.q.done);self.assertIn(100,a.q.done);self.assertEqual(101 in a.q.done,mode=='public')
    def test_ground_disabled_or_distant_after_context_refuses_endpoint(self):
        for mode in ('disabled','distance'):
            a=self.prepared(False);original=a.s.placed[R+'OriginalCase']
            def change():
                if mode=='disabled':original.disabled=True
                else:original.pos=(90000,90000,16)
            fired,restore=self.final_hook(a,change);a.read();self.assertEqual(len(fired),1)
            self.assertIn(60,a.q.done);self.assertNotIn(100,a.q.done);self.assertIsNone(original.container);restore()
    def test_historical44_is_not_rolled_back_by_later_real_loss(self):
        a=Fair(self);original=a.s.placed[R+'OriginalCase'];outsider=a.s.placed[R+'Flint'];oldadd=a.s.n_objectreference_additem;oldread=a.s.n_objectreference_getcontainer;oldscene=a.s.n_actor_isinscene
        issued=[];observed=[];moved=[]
        def add(ref,ctx,form,*args):
            result=oldadd(ref,ctx,form,*args)
            if ref is a.s.player and form is original:issued.append(True)
            return result
        def read(ref,ctx):
            result=oldread(ref,ctx)
            if issued and ref is original and result is a.s.player:observed.append(True)
            return result
        def scene(ref,ctx):
            result=oldscene(ref,ctx)
            if observed and not moved:moved.append(True);oldadd(outsider,None,original,1,True)
            return result
        a.s.n_objectreference_additem=add;a.s.n_objectreference_getcontainer=read;a.s.n_actor_isinscene=scene;a.scene(3,Occupation=0,OccupationSeen=0,Take=0)
        self.assertEqual((len(issued),len(moved)),(1,1));self.assertTrue(observed);self.assertIs(original.container,outsider)
        self.assertTrue(a.v('caseTaken'));self.assertEqual(a.v('response'),44);self.assertEqual(a.v('effectPending'),0);self.assertFalse(a.v('effectUncertain'));self.assertFalse(a.s.invoke(Q,'Held',[]))
        a.s.n_objectreference_additem=oldadd;a.s.n_objectreference_getcontainer=oldread;a.s.n_actor_isinscene=oldscene;a.read();self.assertNotIn(100,a.q.done)

class AccessMutants(unittest.TestCase):
    def test_current_custody_and_final_generation_mutants_are_behaviorally_detected(self):
        trials=[('currentHolder == expectedHolder','true','test_late_current_custody_loss_refuses_solo_and_public_and_recovers'),('&& capturedEpoch == generation\nEndFunction\n\nbool Function FinishRead','\nEndFunction\n\nbool Function FinishRead','test_generation_is_checked_after_final_native_container_read')]
        for needle,replacement,method in trials:
            with self.subTest(guard=needle),tempfile.TemporaryDirectory() as t:
                folder=Path(t)
                for p in SCRIPTS.glob('*.psc'):shutil.copyfile(p,folder/p.name)
                p=folder/'MQ03Quest.psc';text=p.read_text();self.assertEqual(text.count(needle),1);p.write_text(text.replace(needle,replacement))
                case=CurrentReadAccess(method);original=case.prepared
                case.prepared=lambda held=True:original(held=held,scripts=folder)
                stream=io.StringIO();r=unittest.TextTestRunner(stream=stream).run(unittest.TestSuite([case]))
                self.assertEqual(r.errors,[],stream.getvalue());self.assertTrue(r.failures,stream.getvalue())

if __name__=='__main__':unittest.main()
