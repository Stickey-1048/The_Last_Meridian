"""Strict successor pins, immutable accepted baseline and source-only selection."""
import json,shutil,subprocess,sys,tempfile,unittest,hashlib
from pathlib import Path
from test_sim import ROOT
sys.path.insert(0,str(ROOT/'tools'))
import case_read_access_candidate as candidate

def source_copy():
    root=Path(tempfile.mkdtemp(prefix='tlm-case-source-'));m=json.loads(candidate.MANIFEST.read_text(encoding='utf-8'))
    for name in set(m['baselineFiles'])|set(m['sourceFilesTextSha256'])|{'tools/win/case-read-access-candidate.json'}:
        target=root/name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/name,target)
    return root

def repin(root):
    p=root/'tools/win/case-read-access-candidate.json';m=json.loads(p.read_text(encoding='utf-8'));m.update(candidate.describe(root));p.write_text(json.dumps(m));return m

class CaseReadCandidate(unittest.TestCase):
    def test_exact_successor_and_real_git_baseline_anchors(self):
        self.assertEqual(candidate.problems(),[]);m=json.loads(candidate.MANIFEST.read_text(encoding='utf-8'));self.assertEqual(len(m['baselineFiles']),411)
        for name in ('scripts/Source/User/TLM/MQ03Quest.psc','tools/PluginBuilder/formkeys.txt','tools/red_hollow_environment_candidate.py','tools/win/red-hollow-environment-candidate.json','.github/workflows/portable-checks.yml'):
            raw=subprocess.check_output(['git','show',candidate.BASELINE+':'+name],cwd=ROOT)
            with tempfile.TemporaryDirectory() as t:
                p=Path(t)/'file';p.write_bytes(raw);self.assertEqual(candidate.content_digest(p),m['baselineFiles'][name])
        self.assertTrue(all(v is None for v in m['measured'].values()));self.assertEqual((len(m['runtimeSelection']['reusedReviewedPex']),len(m['runtimeSelection']['freshlyCompiled'])),(17,17))
    def test_repin_cannot_change_any_unrelated_runtime_geometry_ids_canon_or_workflow(self):
        for name in ('scripts/Source/User/TLM/Core.psc','scripts/Source/User/TLM/RedHollowWalk.psc','scripts/Source/User/TLM/FourFlagsWalk.psc','tools/PluginBuilder/RedHollowEnvironment.cs','tools/WorldSliceBuilder/WorldFourFlags.cs','tools/PluginBuilder/formkeys.txt','docs/design/FOUR_FLAGS_STORY_001_CONTRACT.md','.github/workflows/portable-checks.yml','.gitattributes'):
            with self.subTest(file=name):
                root=source_copy();p=root/name;p.write_text(p.read_text(encoding='utf-8')+'\nunsupported mutation\n',encoding='utf-8');repin(root)
                self.assertIn('unrelated accepted baseline file altered: '+name,candidate.problems(root))
    def test_repin_cannot_waive_frozen_verifier_manifest_or_baseline_pins(self):
        for name in ('tools/red_hollow_environment_candidate.py','tools/win/red-hollow-environment-candidate.json','tools/win/Build-RedHollowEnvironment.ps1','tools/four_flags_candidate.py'):
            root=source_copy();p=root/name;p.write_text(p.read_text(encoding='utf-8')+'\n',encoding='utf-8');repin(root)
            self.assertIn('unrelated accepted baseline file altered: '+name,candidate.problems(root))
        root=source_copy();p=root/'tools/win/case-read-access-candidate.json';m=json.loads(p.read_text(encoding='utf-8'));m['baselineFiles']['tools/PluginBuilder/formkeys.txt']='0'*64;p.write_text(json.dumps(m))
        self.assertIn('accepted baseline file membership/pins altered',candidate.problems(root))
    def test_approved_order_and_adjudication_cannot_be_waived_by_repin(self):
        for name in candidate.AUTHORITY_PINS:
            root=source_copy();p=root/name;p.write_text(p.read_text(encoding='utf-8')+'\nchanged authority\n',encoding='utf-8');repin(root)
            self.assertIn('approved authority altered: '+name,candidate.problems(root))
    def test_mq03_historical_transfer_and_all_unrelated_bodies_are_frozen(self):
        root=source_copy();p=root/'scripts/Source/User/TLM/MQ03Quest.psc';text=p.read_text(encoding='utf-8');needle='\t\t\tcaseTaken = true';self.assertEqual(text.count(needle),1);p.write_text(text.replace(needle,'\t\t\tcaseTaken = false'),encoding='utf-8');repin(root)
        self.assertIn('unrelated MQ03 body altered outside final read boundary',candidate.problems(root))
    def test_new_runtime_or_unapproved_source_membership_is_rejected(self):
        root=source_copy();(root/'scripts/Source/User/TLM/Extra.psc').write_text('Scriptname TLM:Extra\n');repin(root)
        self.assertIn('exactly the existing34script membership required',candidate.problems(root))
        root=source_copy();(root/'tools/PluginBuilder/Unexpected.cs').write_text('// not authorized');repin(root)
        self.assertIn('unapproved source file membership',candidate.problems(root))
    def test_frozen_rhe_verifier_still_refuses_unrelated_mq03_successor(self):
        got=subprocess.run([sys.executable,'-B','tools/red_hollow_environment_candidate.py','verify'],cwd=ROOT,capture_output=True,text=True)
        self.assertEqual(got.returncode,1);self.assertIn('unrelated accepted source changed: MQ03Quest.psc',got.stdout)
    def test_full34_compile_selection_still_requires_current_mq03_and_preserves_reviewed_bytes(self):
        root=Path(tempfile.mkdtemp(prefix='tlm-case-dummy-'));bundle=root/'bundle';scripts=bundle/'Scripts/TLM';scripts.mkdir(parents=True);compiled=root/'compile';compiled.mkdir()
        m=json.loads(candidate.MANIFEST.read_text(encoding='utf-8'));pins={}
        for name in list(m['runtimeSelection']['reusedReviewedPex'])+m['runtimeSelection']['freshlyCompiled']:
            fresh=('synthetic fresh '+name).encode();reviewed=('synthetic reviewed '+name).encode();(compiled/name).write_bytes(fresh)
            if name in m['runtimeSelection']['reusedReviewedPex']:pins[name]=hashlib.sha256(reviewed).hexdigest().upper();(scripts/name).write_bytes(reviewed)
            else:(scripts/name).write_bytes(fresh)
        m['runtimeSelection']['reusedReviewedPex']=pins;manifest=root/'dummy.json';manifest.write_text(json.dumps(m))
        for name in ('TheLastMeridian.esp','TLMWorldSlice.esp'):(bundle/name).write_bytes(b'not a plugin')
        self.assertTrue(candidate.measure(bundle,compiled,manifest)['selectionOk']);self.assertFalse(candidate.measure(bundle,None,manifest)['selectionOk'])
        (scripts/'MQ03Quest.pex').write_bytes(b'earlier case runtime');self.assertIn('fresh bundle scripts differ from full compile',candidate.measure(bundle,compiled,manifest)['problems'])
        (scripts/'MQ03Quest.pex').write_bytes((compiled/'MQ03Quest.pex').read_bytes());(scripts/'Core.pex').write_bytes((compiled/'Core.pex').read_bytes())
        self.assertIn('reviewed byte pins mismatch',candidate.measure(bundle,compiled,manifest)['problems'])
        (compiled/'MQ03Quest.pex').unlink();self.assertIn('full fresh compile membership mismatch or absent',candidate.measure(bundle,compiled,manifest)['problems'])

if __name__=='__main__':unittest.main()
