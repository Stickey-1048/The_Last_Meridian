"""Strict successor and carry checks; no native or installed writes."""
from pathlib import Path
import importlib.util,json,shutil,sys,tempfile,unittest
from unittest import mock
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'tools'))
import black_ledger_final_read_candidate as candidate
spec=importlib.util.spec_from_file_location('bl_final_package',ROOT/'tools/BlackLedger/package_final_read.py');package=importlib.util.module_from_spec(spec);spec.loader.exec_module(package)
class RepairCandidate(unittest.TestCase):
 def test_exact_current_successor_and_unchanged_original(self):
  self.assertEqual(candidate.problems(),[]);self.assertEqual(candidate.prior.problems(ROOT.parent/'black-ledger-runtime-001'),[])
 def test_old_guards_core_workflow_and_two_script_edits_cannot_be_rebound(self):
  manifest=json.loads((ROOT/candidate.NAME).read_text(encoding='utf-8'))
  with tempfile.TemporaryDirectory() as temp:
   root=Path(temp)
   for name in set(manifest['sourceFilesTextSha256'])|{candidate.NAME}:
    target=root/name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/name,target)
   self.assertEqual(candidate.problems(root),[])
   for name in ('tools/black_ledger_candidate.py','tools/win/black-ledger-candidate.json','scripts/Source/User/TLM/Core.psc','.github/workflows/portable-checks.yml','scripts/Source/User/TLM/MQ04Quest.psc'):
    with self.subTest(name=name):
     target=root/name;original=target.read_bytes();target.write_bytes(original+b'\n;unreviewed\n');receipt=(root/candidate.NAME).read_bytes();m=json.loads(receipt);m['sourceFilesTextSha256'][name]=candidate.pin(target);(root/candidate.NAME).write_text(json.dumps(m),encoding='utf-8');self.assertTrue(candidate.problems(root));target.write_bytes(original);(root/candidate.NAME).write_bytes(receipt)
 def test_actual40_payloads_full38_compile_and_literal_plugin_carry(self):
  meta,files=package.inputs();self.assertEqual(len(files),40);old=ROOT.parent/'black-ledger-runtime-001/tools/BlackLedger/build/package-002/bundle'
  for name in ('TheLastMeridian.esp','TLMWorldSlice.esp'):self.assertEqual(files[name].read_bytes(),(old/name).read_bytes())
  self.assertEqual(meta['payloads']['Scripts/TLM/Core.pex'],'BD7A9CBB30F5DCB3858EFA9556BE14B875332056A86B6B7816838E1577A8E4E3')
 def test_no_output_on_bad_name_or_existing_output(self):
  for name in ('../escape','C:/game','package-001/child'):
   with self.assertRaises(ValueError):package.package(name)
  with tempfile.TemporaryDirectory() as temp:
   task=Path(temp);existing=task/'build/package-999';existing.mkdir(parents=True);sentinel=existing/'keep.txt';sentinel.write_text('preserve',encoding='utf-8')
   with mock.patch.object(package,'TASK',task),self.assertRaises(ValueError):package.package('package-999')
   self.assertEqual(sentinel.read_text(encoding='utf-8'),'preserve');self.assertEqual(list(existing.iterdir()),[sentinel])
if __name__=='__main__':unittest.main(verbosity=2)
