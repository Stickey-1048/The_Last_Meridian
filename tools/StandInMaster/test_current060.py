"""Synthetic-only typed fixture/strict-producer checks; no owned inputs."""
import json, re, struct, subprocess, unittest, zlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'build/standin-current060-tests'
def records(path):
 b=path.read_bytes();rows={}
 def walk(a,z):
  while a<z:
   k,n,flags,fid=struct.unpack_from('<4sIII',b,a)
   if k==b'GRUP':walk(a+24,a+n);a+=n;continue
   data=b[a+24:a+24+n];a+=24+n
   if flags&0x40000:data=zlib.decompress(data[4:])
   fields=[];p=0
   while p<len(data):
    tag,size=struct.unpack_from('<4sH',data,p);p+=6;fields.append((tag,data[p:p+size]));p+=size
   rows[fid]=(k,dict(fields),fields)
 walk(0,len(b));return rows
def run(variant):
 folder=OUT/variant;folder.mkdir(parents=True,exist_ok=True)
 command=['dotnet','run','--no-build','--project','tools/StandInMaster','--',str(folder/'Fallout4.esm'),variant]
 fixture=subprocess.run(command,cwd=ROOT,capture_output=True,text=True);(folder/'fixture.log').write_text(fixture.stdout+fixture.stderr)
 assert fixture.returncode==0,fixture.stderr
 producer=subprocess.run(['dotnet','run','--no-build','--project','tools/PluginBuilder','--','--out',str(folder/'out'),'--fallout4-esm',str(folder/'Fallout4.esm')],cwd=ROOT,capture_output=True,text=True)
 (folder/'producer.log').write_text(producer.stdout+producer.stderr)
 return producer,records(folder/'Fallout4.esm')
class CurrentFixture(unittest.TestCase):
 def test_default_typed_readback_and_producer(self):
  p,rows=run('default');self.assertEqual(p.returncode,0,p.stderr);self.assertIn('self-check: the file read back matches the spec',p.stdout)
  for key,kind in {0x517B0:b'LIGH',0x52576:b'DOOR',0x1A6E6A:b'STAT',0x23323:b'VTYP',0x3F23D:b'NPC_',0xB2D8D:b'ARMO',0xB2D89:b'ARMA',0x113340:b'NPC_',0x113346:b'NPC_',0x1643CA:b'SNDR',0x876BB:b'SNCT',0x64451:b'SNCT'}.items():self.assertEqual(rows[key][0],kind)
  edids=[tags.get(b'EDID') for kind,tags,_ in rows.values() if tags.get(b'EDID')];self.assertEqual(len(edids),len(set(edids)))
  self.assertIn('3 male, 3 female, 1 of no one sex',p.stdout);self.assertIn('StandInSettlerMale01',p.stdout);self.assertIn('StandInSettlerWomanAnyFace',p.stdout)
 def test_strict_missing_wrong_type_model_collision_and_audio(self):
  cases={'current-no-static':'Blackstone exact static missing: PipeAStraightHalf01','current-wrong-static-type':'Blackstone exact static missing: PipeAStraightHalf01','current-static-model':'Blackstone model/bounds changed: PipeAStraightHalf01','current-static-collision':'Sequence contains more than one matching element','current-no-sound':'Sequence contains no matching element','current-sound-shape':'Known single nonlooping dialogue sound shape changed'}
  for variant,why in cases.items():
   with self.subTest(variant=variant):
    p,_=run(variant);self.assertNotEqual(p.returncode,0);self.assertIn(why,p.stdout+p.stderr)
 def test_plain_npc_stays_plain_and_split_bound_variant(self):
  p,rows=run('plain-triggers');self.assertNotEqual(p.returncode,0)
  npc=next(tags for kind,tags,_ in rows.values() if tags.get(b'EDID')==b'WorkshopNPC\0')
  self.assertEqual(struct.unpack_from('<H',npc[b'ACBS'],14)[0],0);self.assertNotIn(b'TPTA',npc)
  self.assertIn('Sequence contains no matching element',p.stderr)
  p,_=run('plain-trigger-bounds');self.assertEqual(p.returncode,0,p.stderr)
  self.assertIn('this build does not write it, as most of them do not',p.stdout)
  report=(OUT/'plain-trigger-bounds/out/TheLastMeridian.report.txt').read_text()
  trial=next(line for line in report.splitlines() if 'TLM_REF_TrialTrigger  PlacedObject' in line)
  self.assertIn('Box (150, 150, 150)',trial);self.assertNotIn(' bound ',trial)
 def test_existing_player_and_environment_variant_authorities(self):
  for variant in ['unnamed-player','wrong-player','quest-evidence','weak-evidence','bare-room','rhe-no-light','rhe-static-model']:
   with self.subTest(variant=variant):
    p,rows=run(variant)
    if variant=='rhe-no-light':self.assertNotEqual(p.returncode,0);self.assertIn('RH real LIGH missing',p.stderr)
    elif variant=='rhe-static-model':self.assertNotEqual(p.returncode,0);self.assertIn('RH environment exact model/bounds changed',p.stderr)
    else:
     self.assertEqual(p.returncode,0,p.stderr)
     if variant=='wrong-player':self.assertIn("does not place the actor 'Player'",p.stdout)
     if variant=='weak-evidence':self.assertIn('only 2',p.stdout)
if __name__=='__main__':unittest.main()
