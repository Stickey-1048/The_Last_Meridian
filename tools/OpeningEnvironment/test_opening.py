import unittest,copy,struct
import verify as v
class Opening(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.rows,_=v.records(v.OUT/'TLMWorldSlice.esp')
 def change(self,name=None,kind=None):
  rows=copy.deepcopy(self.rows);r=next(r for r in rows.values()if (name and r['name']==name)or(kind and r['type']==kind));return rows,r
 def test_actual_decoded_terrain_and_footprints(self):self.assertEqual(v.verify(self.rows)['heightSamples'],1089)
 def test_cell_edge_height_corruption_refused(self):
  rows,r=self.change(kind='LAND');b=bytearray(r['tags'][b'VHGT']);b[4]=1;r['tags'][b'VHGT']=bytes(b)
  with self.assertRaisesRegex(AssertionError,'C0 cell boundary'):v.verify(rows)
 def test_wrong_normals_refused(self):
  rows,r=self.change(kind='LAND');b=bytearray(r['tags'][b'VNML']);b[0]=127;r['tags'][b'VNML']=bytes(b)
  with self.assertRaisesRegex(AssertionError,'normals disagree'):v.verify(rows)
 def test_raised_cabin_floor_refused(self):
  rows,r=self.change('TLM_WS_CabinFloor00');at=v.pose(r);at[2]+=8;r['tags'][b'DATA']=struct.pack('<6f',*at)
  with self.assertRaisesRegex(AssertionError,'floor deck'):v.verify(rows)
 def test_dispatch_identity_xy_move_refused(self):
  rows,r=self.change('TLM_WS_ST_Dispatch');at=v.pose(r);at[0]+=16;r['tags'][b'DATA']=struct.pack('<6f',*at)
  with self.assertRaisesRegex(AssertionError,'Original ref XY'):v.verify(rows)
 def test_missing_foundation_refused(self):
  rows,r=self.change('TLM_OPEN_CabinFoundation2792_2800');del rows[r['id']]
  with self.assertRaisesRegex(AssertionError,'scene prop membership'):v.verify(rows)
if __name__=='__main__':unittest.main(verbosity=2)
