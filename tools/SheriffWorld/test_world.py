import unittest,copy,struct
import check_world as c
class World(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.rows,_=c.v.records(c.OUT)
 def change(self,name):
  rows=copy.deepcopy(self.rows);return rows,next(r for r in rows.values()if r['name']==name)
 def tag(self,r,k,b):r['tags'][k]=b;r['ordered']=[(t,b if t==k else v)for t,v in r['ordered']]
 def test_actual_six_anchor_current_master_composition(self):self.assertEqual(c.check(self.rows)['currentAliases'],35)
 def test_lowered_anchor_refused(self):
  rows,r=self.change('TLM_WS_ST_HelpApproach');p=c.v.pose(r);p[2]-=16;self.tag(r,b'DATA',struct.pack('<6f',*p))
  with self.assertRaisesRegex(AssertionError,'actual upper LAND'):c.check(rows)
 def test_enabled_anchor_refused(self):
  rows,r=self.change('TLM_WS_ST_HelpHome');r['flags']&=~0x800
  with self.assertRaisesRegex(AssertionError,'behavior/visibility'):c.check(rows)
 def test_old_actor_pose_change_refused(self):
  rows,r=self.change('TLM_WS_ST_Pritchard');p=c.v.pose(r);p[2]+=8;self.tag(r,b'DATA',struct.pack('<6f',*p))
  with self.assertRaisesRegex(AssertionError,'Old payload changed'):c.check(rows)
 def test_new_alias_redirect_refused(self):
  rows,r=self.change('TLM_WS_A1');mode=False
  for i,(k,b)in enumerate(r['ordered']):
   if k==b'ALID':mode=b.rstrip(b'\0')==b'HelpHome'
   if mode and k==b'ALFR':r['ordered'][i]=(k,struct.pack('<I',0));break
  with self.assertRaisesRegex(AssertionError,'exact new anchor'):c.check(rows)
 def test_missing_anchor_refused(self):
  rows,r=self.change('TLM_WS_ST_HelpWithdrawA');del rows[r['id']]
  with self.assertRaisesRegex(AssertionError,'six appended'):c.check(rows)
if __name__=='__main__':unittest.main(verbosity=2)
