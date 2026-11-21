import unittest,copy,struct,subprocess
import verify as v
class AuditionProof(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.raw=v.OUT.read_bytes();cls.plan,cls.assets,cls.stock,cls.story,cls.world=v.inputs()
 def check(self,raw=None,plan=None,assets=None):return v.verify(raw or self.raw,plan or self.plan,assets or self.assets,self.stock,self.story,self.world)
 def mutate(self,fid,sub,action):
  b=bytearray(self.raw);found=False
  def walk(a,end):
   nonlocal found
   while a<end:
    tag,n,flags,id=struct.unpack_from('<4sIII',b,a)
    if tag==b'GRUP':walk(a+24,a+n);a+=n;continue
    if id==fid:
     assert not flags&0x40000;p=a+24
     while p<a+24+n:
      k,size=struct.unpack_from('<4sH',b,p);p+=6
      if k==sub:action(b,p,size);found=True;return
      p+=size
    a+=24+n
  walk(0,len(b));self.assertTrue(found);return bytes(b)
 def key(self,field,index=0):return int(self.plan['actors'][index][field].split(':')[0],16)|0x02000000
 def test_three_actual_placed_stock_studies(self):
  r=self.check();self.assertEqual(r['prototypesPlaced'],3);self.assertEqual(r['distinctNativeFaceGeomHashes'],3);self.assertEqual(r['reciprocalDoorRefs'],2);self.assertEqual(r['customFaceMorphEdits'],0)
 def test_missing_traits_and_inherited_inventory_refused(self):
  for flags in (0,257):
   raw=self.mutate(self.key('prototype'),b'ACBS',lambda b,p,n:struct.pack_into('<H',b,p+14,flags))
   with self.assertRaisesRegex(AssertionError,'Traits-only'):self.check(raw)
 def test_wrong_face_donor_and_wrong_outfit_refused(self):
  for sub in (b'TPLT',b'TPTA'):
   raw=self.mutate(self.key('prototype'),sub,lambda b,p,n:struct.pack_into('<I',b,p,0x113340))
   with self.assertRaisesRegex(AssertionError,'trait donor'):self.check(raw)
  raw=self.mutate(self.key('prototype'),b'DOFT',lambda b,p,n:struct.pack_into('<I',b,p,0))
  with self.assertRaisesRegex(AssertionError,'outfit'):self.check(raw)
 def test_unbound_actor_and_injected_custom_morph_refused(self):
  raw=self.mutate(self.key('placed'),b'NAME',lambda b,p,n:struct.pack_into('<I',b,p,0))
  with self.assertRaisesRegex(AssertionError,'Prototype missing'):self.check(raw)
  raw=self.mutate(self.key('prototype'),b'FMRS',lambda b,p,n:b.__setitem__(p,b[p]^1))
  with self.assertRaisesRegex(AssertionError,'Custom face'):self.check(raw)
 def test_broken_return_and_wrong_landing_refused(self):
  key=int(self.plan['exit']['key'].split(':')[0],16)|0x02000000
  for offset in (0,4):
   raw=self.mutate(key,b'XTEL',lambda b,p,n:struct.pack_into('<I',b,p+offset,0))
   with self.assertRaisesRegex(AssertionError,'teleport/landing'):self.check(raw)
 def test_room_and_old_header_mutations_refused(self):
  key=int(self.plan['room'][0]['key'].split(':')[0],16)|0x02000000
  raw=self.mutate(key,b'DATA',lambda b,p,n:struct.pack_into('<f',b,p+8,80))
  with self.assertRaisesRegex(AssertionError,'Room pose'):self.check(raw)
  raw=self.mutate(0x01000800,b'EDID',lambda b,p,n:b.__setitem__(p,ord('X')))
  with self.assertRaisesRegex(AssertionError,'Old header'):self.check(raw)
 def test_duplicate_face_asset_hashes_refused(self):
  assets=copy.deepcopy(self.assets)
  for a in assets['entries']:
   if '/facegeom/'in a['path']:a['sha256']='A'*64
  with self.assertRaisesRegex(AssertionError,'not distinct'):self.check(assets=assets)
 def test_existing_output_refused_without_changing_artifact(self):
  before=v.sha(v.OUT);binary=v.ROOT/'bin/Debug/net8.0/NpcPresentation.dll'
  r=subprocess.run(['dotnet',str(binary),str(v.MASTER),str(v.OUT.parent.relative_to(v.ROOT))],capture_output=True,text=True)
  self.assertNotEqual(r.returncode,0);self.assertIn('REFUSED',r.stderr);self.assertEqual(v.sha(v.OUT),before)
  assets=copy.deepcopy(self.assets);assets['textureProof']['entries']=[e for e in assets['textureProof']['entries']if not e['path'].endswith('/000399dd_d.dds')]
  with self.assertRaisesRegex(AssertionError,'Texture'):self.check(assets=assets)
if __name__=='__main__':unittest.main()
