from pathlib import Path
import sys,tempfile,shutil,json,unittest
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'tools'));sys.path.insert(0,str(ROOT/'tools/Blackstone'))
import blackstone_candidate as source
import package,audit
class Candidate(unittest.TestCase):
 def copy(self,parent):
  root=Path(parent)
  for name in source.expected_names():
   dest=root/name;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes((ROOT/name).read_bytes())
  return root
 def test_exact_current_source(self):self.assertEqual([],source.problems())
 def test_baseline_runtime_workflow_unknown_and_attempted_manifest_repin_rejected(self):
  for name in ('scripts/Source/User/TLM/MQ05Quest.psc','tools/win/black-ledger-final-read-candidate.json','.github/workflows/portable-checks.yml','unexpected-source.txt','tools/PluginBuilder/formkeys.txt'):
   with self.subTest(name=name),tempfile.TemporaryDirectory() as temp:
    root=self.copy(temp);p=root/name;old=p.read_bytes()if p.exists()else b'';p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(old+b'\nUNAPPROVED\n')
    self.assertTrue(source.problems(root));manifest=root/source.NAME;m=json.loads(manifest.read_text(encoding='utf-8'));m['sourceFilesTextSha256'][name]=source.pin(p);manifest.write_text(json.dumps(m),encoding='utf-8');self.assertTrue(source.problems(root))
 def test_actual_owned_prefix_preservation_and_new_poses(self):
  result=audit.run();self.assertTrue(result['TLMWorldSlice.esp']['literalFileEqual']);self.assertEqual(['TLM_MQ04'],result['TheLastMeridian.esp']['oldPayloadExceptions']);self.assertEqual(96,result['passiveLiteralPoses'])
 def test_corrupt_old_actor_record_is_not_an_allowed_old_payload_exception(self):
  parent=ROOT.parent/'black-ledger-final-read-fix-001/tools/BlackLedger/build/package-001/bundle/TheLastMeridian.esp';current=ROOT/'tools/Blackstone/build/licensed-master-002/TheLastMeridian.esp';data=current.read_bytes();self.assertIn(b'Dunmore',data)
  with tempfile.TemporaryDirectory()as temp:
   p=Path(temp)/'bad.esp';p.write_bytes(data.replace(b'Dunmore',b'Xunmore'))
   with self.assertRaises(AssertionError):audit.preservation(p,parent,True)
 def test_package_all_inputs_before_output_and_exact_runtime(self):
  meta,payload=package.inputs();self.assertEqual(43,len(payload));self.assertEqual(16,len(source.describe()['runtimeSelection']['reusedReviewedPex']));self.assertEqual(25,len(source.describe()['runtimeSelection']['freshPex']))
  for name in ('../bad','package-001/escape','package-9999'):
   with self.assertRaises(ValueError):package.package(name)
 def test_workspace_reparse_ancestor_guard(self):
  from unittest.mock import patch
  import types
  with tempfile.TemporaryDirectory()as temp:
   target=Path(temp)/'new';original=Path.lstat
   def altered(p,*a,**k):
    if p==Path(temp):return types.SimpleNamespace(st_mode=0o40755,st_file_attributes=0x400)
    return original(p,*a,**k)
   with patch.object(Path,'lstat',altered):
    with self.assertRaises(ValueError):package.safe(target)
if __name__=='__main__':unittest.main(verbosity=2)
