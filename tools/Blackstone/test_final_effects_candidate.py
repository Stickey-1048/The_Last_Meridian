from pathlib import Path
import sys,unittest,tempfile,json
ROOT=Path(__file__).resolve().parents[2];sys.path[:0]=[str(ROOT/'tools'),str(ROOT/'tools/Blackstone')]
import blackstone_final_effects_candidate as source
import blackstone_candidate as prior
import package_final_effects as package
class RepairCandidate(unittest.TestCase):
 def test_exact_successor_and_actual_frozen_original(self):
  self.assertEqual([],source.problems());self.assertEqual([],prior.problems(ROOT.parent/'blackstone-runtime-001'))
 def test_runtime_frozen_workflow_and_unknown_mutation_repin_refused(self):
  for name in ('scripts/Source/User/TLM/BlackstoneWalk.psc','tools/win/blackstone-candidate.json','.github/workflows/portable-checks.yml','unapproved.txt'):
   with self.subTest(name=name),tempfile.TemporaryDirectory()as temp:
    root=Path(temp)
    for n in source.expected_names():
     p=root/n;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes((ROOT/n).read_bytes())
    p=root/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes((p.read_bytes()if p.exists()else b'')+b'\nUNAPPROVED\n');self.assertTrue(source.problems(root));m=json.loads((root/source.NAME).read_text(encoding='utf-8'));m['sourceFilesTextSha256'][name]=source.pin(p);(root/source.NAME).write_text(json.dumps(m),encoding='utf-8');self.assertTrue(source.problems(root))
 def test_actual43_payload_inputs_two_plugins_literal_old_and_41source_compile_binding(self):
  meta,payload=package.inputs();self.assertEqual(43,len(payload));old=ROOT.parent/'blackstone-runtime-001/tools/Blackstone/build/package-002/bundle'
  for name in ('TheLastMeridian.esp','TLMWorldSlice.esp'):self.assertEqual((old/name).read_bytes(),payload[name].read_bytes())
  self.assertEqual(16,len(source.describe()['runtimeSelection']['reusedReviewedPex']));self.assertEqual(25,len(source.describe()['runtimeSelection']['freshPex']))
  for name in ('../escape','package-001/escape','package-0001'):
   with self.assertRaises(ValueError):package.package(name)
if __name__=='__main__':unittest.main(verbosity=2)
