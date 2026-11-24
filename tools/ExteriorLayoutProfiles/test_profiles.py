"""Read-only strict exterior mutations against an explicit existing synthetic plugin."""
import argparse,ast,hashlib,inspect,struct,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'tools'))
import check_plugin_layout as c
PLUGIN=None

def rewrite(buf, remove_ids=(), remove_groups=(), duplicate_id=None):
 def walk(a,z):
  out=bytearray()
  while a<z:
   k=buf[a:a+4];n=struct.unpack_from('<I',buf,a+4)[0]
   if k==b'GRUP':
    label,gtype=struct.unpack_from('<II',buf,a+8)
    if(gtype,label)not in remove_groups:
     body=walk(a+24,a+n);head=bytearray(buf[a:a+24]);struct.pack_into('<I',head,4,len(body)+24);out.extend(head+body)
    a+=n
   else:
    fid=struct.unpack_from('<I',buf,a+12)[0];record=buf[a:a+24+n]
    if fid not in remove_ids:
     out.extend(record)
     if fid==duplicate_id:out.extend(record)
    a+=24+n
  return bytes(out)
 return walk(0,len(buf))

class ExteriorProfiles(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.buf=PLUGIN.read_bytes();cls.described=c.placed_from_json(str(PLUGIN.with_suffix('.json')));assert cls.described is not None
  cls.m=c.master_count(cls.buf);cls.own=lambda self,n:self.m<<24|n
 def problems(self,b):return c.check_cells(b,self.described)[0]
 def test_accepted_current_default_and_all_existing_self_tests(self):
  self.assertEqual(self.problems(self.buf),[])
  npc=c.npcs_from_json(str(PLUGIN.with_suffix('.json')));ids=c.own_ids_from_json(str(PLUGIN.with_suffix('.json')))
  problems,cells,_=c.check_cells(self.buf,self.described);problems,npcs=c.check_npcs(self.buf,npc,ids)
  unseen,tried=c.self_test(self.buf,self.described,cells,npcs,npc,ids)
  self.assertEqual(unseen,[]);self.assertEqual(tried,56)
 def test_every_exterior_mutation_is_a_real_semantic_refusal(self):
  damages=c.exterior_damage(self.buf);self.assertEqual(len(damages),17)
  for name,b in damages:
   with self.subTest(name=name):
    errors=self.problems(b) # parse exceptions are failures here, not an accepted rejection
    self.assertTrue(errors,name)
    self.assertTrue(any(('RH'if name.startswith('RH')else'BS')in e or 'world'in e or 'colliding'in e for e in errors),errors)
 def test_missing_entire_bs_world_and_duplicate_world_or_cell(self):
  removed=rewrite(self.buf,remove_ids={self.own(3820)},remove_groups={(1,self.own(3820))})
  self.assertIn('BS declared exterior world missing',self.problems(removed))
  dupe=rewrite(self.buf,duplicate_id=self.own(3820))
  self.assertIn('Duplicate/colliding exterior world',self.problems(dupe))
  dupe=rewrite(self.buf,duplicate_id=self.own(3822))
  self.assertIn('Duplicate/colliding exterior CELL',self.problems(dupe))
 def test_bs_references_still_use_shared_base_checks(self):
  target=None
  def walk(a,z,bs=False):
   nonlocal target
   for row in c.items(self.buf,a,z):
    if row[0]=='group':walk(row[3],row[4],bs or(row[1]==6 and struct.unpack('<I',row[2])[0]==self.own(3821)))
    elif bs and row[1]in('REFR','ACHR')and target is None:target=row[2]
  walk(0,len(self.buf));self.assertIsNotNone(target)
  for kind,off,size,fid,flags in c.records(self.buf,0,len(self.buf)):
   if fid==target:
    at=self.buf.index(b'NAME',off,off+size)+6;bad=c.patch(self.buf,at,struct.pack('<I',0xff000001));break
  self.assertTrue(any('belongs to a file the plugin does not name'in e for e in self.problems(bad)))
 def test_profile_ids_are_actual_declared_producer_keys(self):
  lines=(ROOT/'tools/PluginBuilder/formkeys.txt').read_text().splitlines();keys={lines[i]:int(lines[i+1])for i in range(0,len(lines),2)}
  fn=ast.parse(inspect.getsource(c.check_cells));assignment=next(n for n in ast.walk(fn)if isinstance(n,ast.Assign)and any(isinstance(v,ast.Name)and v.id=='profiles'for v in n.targets));profiles=ast.literal_eval(assignment.value)
  self.assertEqual(set(profiles),{'TLM_WRLD_RH_Surface','TLM_WRLD_BS_Upper'})
  for name,profile in profiles.items():
   self.assertEqual(profile[1],keys[name]);self.assertEqual(profile[3],keys[profile[2]]);self.assertEqual(profile[5],keys[profile[4]])
  self.assertEqual(profiles['TLM_WRLD_RH_Surface'][6],keys['TLM_LAND_RH_Surface']);self.assertEqual(profiles['TLM_WRLD_BS_Upper'][6],keys['TLM_LAND_BS_Upper'])
  self.assertEqual(hashlib.sha256((ROOT/'tools/player_guidance_terrain_layout.py').read_bytes().replace(b'\r\n',b'\n')).hexdigest(),'6449783a5d637090b605e1d7e60e631e7a2cc7a638df51d650ef6f11a7181588')

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--plugin',type=Path,required=True);a,rest=p.parse_known_args();PLUGIN=a.plugin.resolve();unittest.main(argv=[sys.argv[0]]+rest)
