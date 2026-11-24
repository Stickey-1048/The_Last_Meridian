import unittest,copy,struct
import verify_stake_repair as r
class Repair(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.rows,_=r.v.records(r.OUT/'TLMWorldSlice.esp')
 def test_actual_only_two_stakes_grounded(self):self.assertEqual(len(r.check(self.rows)),2)
 def test_original_floating_offsets_refused(self):
  old,_=r.v.records(r.OLD/'TLMWorldSlice.esp')
  with self.assertRaisesRegex(AssertionError,'Scaled old stake floats'):r.check(old)
 def test_each_post_raised_refused(self):
  for name in r.IDS:
   with self.subTest(name=name):
    rows=copy.deepcopy(self.rows);p=next(x for x in rows.values()if x['name']==name);at=r.v.pose(p);at[2]+=36;p['tags'][b'DATA']=struct.pack('<6f',*at);p['ordered']=[(k,p['tags'][k]if k==b'DATA'else b)for k,b in p['ordered']]
    with self.assertRaisesRegex(AssertionError,'Scaled old stake floats'):r.check(rows)
 def test_unrelated_pose_delta_refused(self):
  rows=copy.deepcopy(self.rows);p=next(x for x in rows.values()if x['name']=='TLM_WS_ST_Dispatch');p['ordered'].append((b'XXXX',b''))
  with self.assertRaisesRegex(AssertionError,'outside two stakes'):r.check(rows)
if __name__=='__main__':unittest.main(verbosity=2)
