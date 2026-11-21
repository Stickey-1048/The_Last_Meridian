"""Current strict-source/packaging negatives; never runs an installed launcher."""
from pathlib import Path
import importlib.util,json,shutil,sys,tempfile,unittest
from unittest import mock
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'tools'))
import black_ledger_candidate as candidate
spec=importlib.util.spec_from_file_location('blackledger_package',ROOT/'tools/BlackLedger/package.py');package=importlib.util.module_from_spec(spec);spec.loader.exec_module(package)
class Candidate(unittest.TestCase):
 def test_exact_current_source(self):self.assertEqual(candidate.problems(),[])
 def test_unrelated_runtime_workflow_and_allocation_edits_even_with_manifest_repin_rejected(self):
  m=json.loads((ROOT/candidate.NAME).read_text(encoding='utf-8'))
  with tempfile.TemporaryDirectory() as temp:
   root=Path(temp)
   for name in set(m['sourceFilesTextSha256'])|{candidate.NAME}:
    dest=root/name;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/name,dest)
   self.assertEqual(candidate.problems(root),[])
   for name in ('scripts/Source/User/TLM/Core.psc','.github/workflows/portable-checks.yml','tools/PluginBuilder/formkeys.txt','scripts/Source/User/TLM/MQ04Quest.psc'):
    with self.subTest(name=name):
     path=root/name;old=path.read_bytes();path.write_bytes(old+b'\n;unapproved\n');original=(root/candidate.NAME).read_bytes();changed=json.loads(original);changed['sourceFilesTextSha256'][name]=candidate.pin(path);(root/candidate.NAME).write_text(json.dumps(changed),encoding='utf-8')
     self.assertTrue(candidate.problems(root));path.write_bytes(old);(root/candidate.NAME).write_bytes(original)
   (root/'unreviewed.psc').write_text('Scriptname Unreviewed extends Quest',encoding='utf-8');self.assertIn('Exact successor source membership changed',candidate.problems(root))
 def test_new_output_only_and_ancestry_guard(self):
  for bad in ('../escape','package-001/child','other','C:/installed','package-01'):
   with self.subTest(name=bad),self.assertRaises(ValueError):package.package(bad)
  with mock.patch.object(Path,'is_symlink',return_value=True),self.assertRaises(ValueError):package.safe(ROOT)
 def test_normal_core_and_exact40_inputs(self):
  m,files=package.inputs();self.assertEqual(len(files),40);self.assertEqual(m['payloads']['Scripts/TLM/Core.pex'],'BD7A9CBB30F5DCB3858EFA9556BE14B875332056A86B6B7816838E1577A8E4E3');self.assertEqual(sum(n.endswith('.pex') for n in files),38)
 def test_owned_raw_preservation_and_flag_mutants(self):
  import struct,importlib.util
  spec=importlib.util.spec_from_file_location('bl_audit',ROOT/'tools/BlackLedger/audit.py');audit=importlib.util.module_from_spec(spec);spec.loader.exec_module(audit)
  parent=ROOT.parent/'rh-return-account-build-f491eeb/build/licensed-return-account-skeleton-001/bundle'
  for filename,current,section,kind in [('TheLastMeridian.esp','licensed-master-002','TLM_A1',b'ACHR'),('TLMWorldSlice.esp','licensed-world-005','TLM_WS_A1',b'LAND')]:
   old=(parent/filename).read_bytes();new=(ROOT/'tools/BlackLedger/build'/current/filename).read_bytes();audit.verify(new,old,section)
   original,_=audit.records(old);chosen=next(fid for tag,fid in original if tag==kind);damaged=bytearray(new);fired=[]
   def walk(start,end):
    pos=start
    while pos<end:
     tag,n,flags,fid=struct.unpack_from('<4sIII',damaged,pos)
     if tag==b'GRUP':walk(pos+24,pos+n);pos+=n;continue
     if tag==kind and fid==chosen:struct.pack_into('<I',damaged,pos+8,flags^0x800);fired.append(1)
     pos+=24+n
   walk(0,len(damaged));self.assertEqual(fired,[1])
   with self.assertRaises(AssertionError):audit.verify(bytes(damaged),old,section)
 def test_actual_owned_control_and_new_visitor_slot_clearance(self):
  import math
  report=json.loads((ROOT/'tools/BlackLedger/build/licensed-world-005/world-clearance.json').read_text(encoding='utf-8'));obstacles=[o for o in report['obstacles'] if 'Floor' not in o['id']]
  def distance(x,y):return min(math.hypot(max(o['minX']-x,0,x-o['maxX']),max(o['minY']-y,0,y-o['maxY'])) for o in obstacles)
  for x,y in ((3120,2540),(3560,2960),(3560,3010),(3560,3070),(3560,2850),(3560,3290),(3280,3350)):self.assertGreaterEqual(distance(x,y),96)
  self.assertLess(distance(3370,2510),96,'old trial entry must actually fail measured shell clearance')
if __name__=='__main__':unittest.main(verbosity=2)
