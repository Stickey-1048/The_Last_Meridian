from pathlib import Path
import unittest,struct,json
import verify_owen as v
class Owen(unittest.TestCase):
 def inputs(self):return(v.ROOT/'build/owen-face-001/TLMNpcPresentation.esp').read_bytes(),(v.REPO.parent/'npc-presentation-007/tools/NpcPresentation/build/photo-001/TLMNpcPresentation.esp').read_bytes()
 def test_current_actual_source_asset_and_owen_only_artifact(self):self.assertEqual('PASS',v.run()['status'])
 def test_wrong_donor_is_rejected(self):
  raw,old=self.inputs();needle=b'TPLT\x04\0'+struct.pack('<I',0x3f23d);self.assertEqual(1,raw.count(needle))
  with self.assertRaises(AssertionError):v.artifact(raw.replace(needle,b'TPLT\x04\0'+struct.pack('<I',0x399dd)),old)
 def test_unrelated_subject_change_is_rejected(self):
  raw,old=self.inputs();self.assertIn(b'TLM_NPC_STUDY_Ada\0',raw)
  with self.assertRaises(AssertionError):v.artifact(raw.replace(b'TLM_NPC_STUDY_Ada\0',b'TLM_NPC_STUDY_Adx\0'),old)
 def test_asset_delta_is_only_new_owen_dependency_union(self):
  original=v.REPO.parent/'npc-presentation-007/tools/NpcPresentation'
  for filename,removed,added in [('facegen-metadata.json',1,1),('texture-metadata.json',7,7)]:
   a={e['path']:e for e in json.loads((original/filename).read_text(encoding='utf-8'))['entries']};b={e['path']:e for e in json.loads((v.ROOT/filename).read_text(encoding='utf-8'))['entries']};self.assertEqual(removed,len(a.keys()-b.keys()));self.assertEqual(added,len(b.keys()-a.keys()));self.assertTrue(all(a[p]==b[p]for p in a.keys()&b.keys()))
if __name__=='__main__':unittest.main(verbosity=2)
