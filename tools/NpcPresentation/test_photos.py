import unittest,json
import verify_photos as p
import test_lighting_delta as oldtests
class PhotoAppend(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.raw=p.OUT.read_bytes();cls.plan=json.loads((p.ROOT/'audition-plan.json').read_text())
 mutation=oldtests.LightingDelta.mutation
 def test_all005records_preserved_and_three_real_portrait_cells(self):
  result=p.verify_photos(self.raw);self.assertEqual(result['newRecords'],78);self.assertEqual(result['nativeCocMarkers'],3)
 def test_old_record_subject_base_and_arrival_mutations_refused(self):
  own=lambda k:int(k.split(':')[0],16)|0x02000000;photo=self.plan['photos'][0]
  for key,tag,offset in [(0x02000818,b'DOFT',0),(own(photo['actor']),b'NAME',0),(own(photo['arrival']),b'NAME',0),(own(photo['actor']),b'DATA',4)]:
   with self.assertRaises(AssertionError):p.verify_photos(self.mutation(key,tag,offset))
if __name__=='__main__':unittest.main()
