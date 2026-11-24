import unittest,copy,struct
import check_river as c
class River(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.rows,cls.names=c.v.records(c.v.OUT/'TLMWorldSlice.esp')
 def changed(self,name=None,kind=None):
  rows=copy.deepcopy(self.rows);r=next(r for r in rows.values()if(name and r['name']==name)or(kind and r['type']==kind));return rows,r
 def tag(self,r,key,value):
  r['tags'][key]=value;r['ordered']=[(k,value if k==key else b)for k,b in r['ordered']]
 def test_actual_terrain_water_controls_and_proxy_routes(self):self.assertEqual(c.check(self.rows)['realControls'].__len__(),12)
 def test_no_water_flag_refused(self):
  rows,r=self.changed('TLM_GWR_Cell');self.tag(r,b'DATA',b'\0\0')
  with self.assertRaisesRegex(AssertionError,'Real CELL water'):c.check(rows)
 def test_flooded_arrival_water_level_refused(self):
  rows,r=self.changed('TLM_GWR_Cell');self.tag(r,b'XCLW',struct.pack('<f',128))
  with self.assertRaisesRegex(AssertionError,'Real CELL water'):c.check(rows)
 def test_wrong_native_water_type_refused(self):
  rows,r=self.changed('TLM_WS_Meridian');self.tag(r,b'NAM2',struct.pack('<I',0x18))
  with self.assertRaisesRegex(AssertionError,'river WATR'):c.check(rows)
 def test_southern_height_seam_refused(self):
  rows,r=self.changed('TLM_GWR_Cell');r=next(x for x in rows.values()if x['type']=='LAND'and any(label==r['id']for kind,label in x['parents']));b=bytearray(r['tags'][b'VHGT']);b[4]=1;self.tag(r,b'VHGT',bytes(b))
  with self.assertRaisesRegex(AssertionError,'Boundary height'):c.check(rows)
 def test_wrong_normals_refused(self):
  rows,r=self.changed('TLM_GWR_Cell');r=next(x for x in rows.values()if x['type']=='LAND'and any(label==r['id']for kind,label in x['parents']));b=bytearray(r['tags'][b'VNML']);b[0]=127;self.tag(r,b'VNML',bytes(b))
  with self.assertRaisesRegex(AssertionError,'Normal/height'):c.check(rows)
 def test_original_opening_actor_move_refused(self):
  rows,r=self.changed('TLM_WS_ST_Marshal');p=c.v.pose(r);p[2]+=8;self.tag(r,b'DATA',struct.pack('<6f',*p))
  with self.assertRaisesRegex(AssertionError,'Unapproved original'):c.check(rows)
 def test_working_control_model_mutation_refused(self):
  rows,r=self.changed('TLM_GWR_Control_Table');self.tag(r,b'MODL',b'wrong.nif\0')
  with self.assertRaisesRegex(AssertionError,'Genuine actual'):c.check(rows)
 def test_working_control_label_mutation_refused(self):
  rows,r=self.changed('TLM_GWR_Control_Table');self.tag(r,b'FULL',b'Wrong action\0')
  with self.assertRaisesRegex(AssertionError,'label/behavior'):c.check(rows)
 def test_raised_bridge_floor_refused(self):
  rows,r=self.changed('TLM_GWR_FarBankWalk3456');p=c.v.pose(r);p[2]+=64;self.tag(r,b'DATA',struct.pack('<6f',*p))
  with self.assertRaisesRegex(AssertionError,'Prop donor/pose'):c.check(rows)
if __name__=='__main__':unittest.main(verbosity=2)
