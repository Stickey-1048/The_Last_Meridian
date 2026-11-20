"""Actual no-master consistency, original binding and optional-reference safety; no native claim."""
import json,shutil,subprocess,sys,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools'))

def walk_props(path):
    q=next(q for q in json.loads(path.read_text(encoding='utf-8'))['Quests'] if q['EditorId']=='TLM_RH')
    return {p['Name']:p for s in q['Scripts'] if s['Name']=='TLM:RedHollowWalk' for p in s['Props']}
def consistency(root):return subprocess.run([sys.executable,str(root/'tools/check_consistency.py')],cwd=root,capture_output=True,text=True)

class SkeletonBinding(unittest.TestCase):
    def test_current_skeleton_stays_honest_and_consistency_has_no_missing_mandatory(self):
        props=walk_props(ROOT/'build/TheLastMeridian.json')
        self.assertNotIn('RhaOriginalRoark',props);self.assertNotIn('RhaOriginalBlevins',props)
        source=(ROOT/'scripts/Source/User/TLM/RedHollowWalk.psc').read_text(encoding='utf-8')
        for name in ('RhaOriginalRoark','RhaOriginalBlevins'):
            self.assertIn('ObjectReference Property '+name+' Auto Const\n',source)
        result=consistency(ROOT);self.assertEqual(result.returncode,0,result.stdout+result.stderr)
        self.assertIn('no problems found',result.stdout)
    def test_standin_master_keeps_both_existing_actor_bindings_exact(self):
        props=walk_props(ROOT/'build/sim/TheLastMeridian.json')
        for who in ('Roark','Blevins'):
            prop=props['RhaOriginal'+who]
            self.assertEqual((prop['Kind'],prop['Target'],prop['Alias']),('object','TLM_REF_RH_'+who,None))
    def test_missing_optional_originals_block_speech_then_existing_binding_recovers(self):
        import test_rh_return_account as r
        for who in ('Roark','Blevins'):
            helper=r.ReturnAccount();a=helper.settle();name='rhaoriginal'+who.lower();original=a.walk.props[name]
            before=a.snapshot();a.walk.props[name]=None
            self.assertFalse(any('Rha' in mid for mid in helper.say(a,who)))
            self.assertEqual(a.snapshot(),before)
            a.walk.props[name]=original
            answers={'Rha'+who+'All':0}
            if who=='Roark':answers['RhaOpen']=0
            self.assertIn(r.P+'Rha'+who+'All',helper.say(a,who,**answers))
            self.assertEqual(a.snapshot(),before)
    def test_restoring_either_mandatory_marker_reproduces_the_real_skeleton_failure(self):
        for name in ('RhaOriginalRoark','RhaOriginalBlevins'):
            with self.subTest(name=name),tempfile.TemporaryDirectory() as folder:
                root=Path(folder)
                for relative in ('tools/check_consistency.py','tools/papyrus_natives.json','tools/logic_model/tlm_model.py','build/TheLastMeridian.json'):
                    p=root/relative;p.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/relative,p)
                shutil.copytree(ROOT/'scripts',root/'scripts')
                p=root/'scripts/Source/User/TLM/RedHollowWalk.psc';source=p.read_text(encoding='utf-8');needle='ObjectReference Property '+name+' Auto Const'
                self.assertEqual(source.count(needle+'\n'),1);p.write_text(source.replace(needle+'\n',needle+' Mandatory\n'),encoding='utf-8')
                result=consistency(root);self.assertEqual(result.returncode,1,result.stdout+result.stderr)
                self.assertIn('mandatory property TLM:RedHollowWalk.'+name+' is not filled',result.stdout)
                self.assertIn('1 problem(s)',result.stdout)

class SkeletonCandidate(unittest.TestCase):
    def test_current_successor_and_two_line_inverse_are_exact(self):
        import rh_return_account_skeleton_candidate as c
        self.assertEqual(c.problems(),[])
        import run_composed_tests as dispatch
        from composed_test_contexts import SKELETON_BASE
        expected={'test_rh_return_account_candidate.ReturnAccountCandidate.test_added_workflow_and_allocation_shift_are_rejected','test_rh_return_account_candidate.ReturnAccountCandidate.test_current_successor_nominal_and_runtime_selection','test_rh_return_account_candidate.ReturnAccountCandidate.test_only_four_exact_old_provenance_methods_move_to_real13c_context','test_rh_return_account_candidate.ReturnAccountCandidate.test_repin_cannot_waive_runtime_old_guard_workflow_or_approved_message_mutations'}
        self.assertEqual({n for n,r in dispatch.EXACT.items() if r==SKELETON_BASE},expected)
        self.assertNotIn('test_rh_return_account_candidate',dispatch.WHOLE)
        self.assertNotIn('test_rh_return_account',dispatch.WHOLE)
        self.assertFalse(any(n.startswith('test_rh_return_account_skeleton.') for n in dispatch.EXACT))
    def test_current_repin_cannot_waive_function_binding_checker_or_workflow_mutations(self):
        import rh_return_account_skeleton_candidate as c
        m=json.loads(c.MANIFEST.read_text(encoding='utf-8'))
        for name in ('scripts/Source/User/TLM/RedHollowWalk.psc','tools/PluginBuilder/SpecRedHollow.cs','tools/check_consistency.py','.github/workflows/portable-checks.yml'):
            with self.subTest(name=name),tempfile.TemporaryDirectory() as folder:
                root=Path(folder)
                for n in c.expected_names(m['baselineFiles']):
                    p=root/n;p.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/n,p)
                p=root/name;p.write_text(p.read_text(encoding='utf-8-sig')+'\n# unapproved mutation\n',encoding='utf-8')
                path=root/c.NAME;current=json.loads(path.read_text(encoding='utf-8'));current.update(c.describe(root));path.write_text(json.dumps(current),encoding='utf-8')
                self.assertTrue(c.problems(root))
if __name__=='__main__':unittest.main()
