"""Focused RH terrain/enclosure negatives; existing synthetic projections only."""
from pathlib import Path
import importlib.util,json,math,struct,subprocess,tempfile,unittest
ROOT=Path(__file__).resolve().parents[2]
def module(name):
 spec=importlib.util.spec_from_file_location(name,ROOT/'tools'/f'{name}.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
projection=module('rh_terrain_projection');candidate=module('rh_terrain_candidate')
class Terrain002(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.new=(ROOT/'build/terrain-002/projection/TheLastMeridian.esp').read_bytes();cls.old=(ROOT/'build/terrain-002/baseline-projection/TheLastMeridian.esp').read_bytes()
 def mutation(self,name,tag,change):
  raw=bytearray(self.new);found=False
  def walk(start,end):
   nonlocal found
   p=start
   while p<end:
    kind,n,flags,fid=struct.unpack_from('<4sIII',raw,p)
    if kind==b'GRUP':walk(p+24,p+n);p+=n;continue
    if flags&0x40000:p+=24+n;continue
    s=dict(projection.subs(raw[p+24:p+24+n]));ed=s.get(b'EDID',b'').rstrip(b'\0').decode()
    if ed==name or name=='LAND' and kind==b'LAND':
     q=p+24
     while q<p+24+n:
      st,sz=struct.unpack_from('<4sH',raw,q)
      if st==tag:change(raw,q+6,sz);found=True;return
      q+=6+sz
    p+=24+n
  walk(0,len(raw));self.assertTrue(found);return bytes(raw)
 def test_exact_projection_and_all_original_records(self):
  r=projection.verify(self.new,self.old);self.assertEqual(r['newDecorativeReferences'],72);self.assertTrue(r['oldUnrelatedPayloadsAndParentsExact'])
 def test_outward_native_wall_is_rejected(self):
  raw=self.mutation('TLM_REF_RHE_NineSouth6144',b'DATA',lambda b,p,n:struct.pack_into('<f',b,p+20,1.0))
  with self.assertRaisesRegex(AssertionError,'Outward mine face'):projection.verify(raw,self.old)
 def test_original_prisoner_destination_movement_rejected(self):
  raw=self.mutation('TLM_REF_RH_Released',b'DATA',lambda b,p,n:struct.pack_into('<f',b,p,1100))
  with self.assertRaisesRegex(AssertionError,'Unapproved old record'):projection.verify(raw,self.old)
 def test_story_pad_height_damage_rejected(self):
  raw=self.mutation('LAND',b'VHGT',lambda b,p,n:b.__setitem__(p+4+8*33+8,1))
  with self.assertRaises(AssertionError):projection.verify(raw,self.old)
 def test_land_normal_damage_rejected(self):
  raw=self.mutation('LAND',b'VNML',lambda b,p,n:b.__setitem__(p+3*(22*33+16),20))
  with self.assertRaisesRegex(AssertionError,'normal/height'):projection.verify(raw,self.old)
 def audit(self,edits):
  with tempfile.TemporaryDirectory(prefix='rh-terrain-fixture-') as d:
   p=Path(d)/'edit.json';p.write_text(json.dumps(edits));return subprocess.run(['dotnet','run','--no-build','--project','tools/PluginBuilder','--','--rh-environment-geometry-check',str(p)],cwd=ROOT,capture_output=True,text=True)
 def test_source_audit_nominal_and_wrong_face(self):
  self.assertEqual(self.audit([]).returncode,0)
  failed=self.audit([{'name':'NineEast0','yaw':-math.pi/2}]);self.assertNotEqual(failed.returncode,0);self.assertIn('face points away',failed.stderr)
 def test_source_audit_rejects_blocked_new_approach(self):
  failed=self.audit([{'name':'T2_Tree384_2560','x':2048,'y':2400,'z':7}]);self.assertNotEqual(failed.returncode,0);self.assertIn('new route obstructed',failed.stderr)
 def test_exact_source_candidate_and_frozen_negative(self):
  self.assertEqual(candidate.problems(),[])
  # A lightweight proxy redirects just one frozen file to a temporary damaged
  # copy; no author files or old manifests are mutated even briefly.
  with tempfile.TemporaryDirectory(prefix='rh-source-negative-') as d:
   bad=Path(d)/'frozen.json';bad.write_text('{}')
   class Proxy:
    def __truediv__(self,key):return bad if key=='tools/win/red-hollow-environment-candidate.json' else ROOT/key
   self.assertTrue(any('Unrelated frozen file' in s for s in candidate.problems(Proxy())))
 def test_original_allocation_prefix_and_tail_negatives(self):
  with tempfile.TemporaryDirectory(prefix='rh-allocation-negative-') as d:
   bad=Path(d)/'formkeys.txt';source=ROOT/'tools/PluginBuilder/formkeys.txt';bad.write_text(source.read_text().replace('TLM_REF_RHE_T2_BedA','UndeclaredDuplicate',1))
   class Proxy:
    def __truediv__(self,key):return bad if key=='tools/PluginBuilder/formkeys.txt' else ROOT/key
   result=candidate.problems(Proxy());self.assertTrue(any('allocation' in s for s in result))
if __name__=='__main__':unittest.main()

