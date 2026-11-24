"""Synthetic-only strict outfit graph; current producer checks remain unchanged."""
import struct,sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from test_current060 import run,records,OUT
class WardrobeGraph(unittest.TestCase):
 def test_default_fixed_donor_authority_and_direct_outfit(self):
  p,rows=run('default');self.assertEqual(p.returncode,0,p.stderr)
  self.assertEqual(rows[0xA36BE][0],b'ARMO');self.assertEqual(rows[0xA36BD][0],b'ARMA')
  self.assertEqual(rows[0xA36BE][1][b'EDID'],b'ClothesResident4\0')
  self.assertEqual(rows[0xA36BD][1][b'RNAM'],struct.pack('<I',0x13746))
  self.assertEqual(rows[0xA36BD][1][b'MOD2'],b'Clothes\\Residents\\4SuitM.nif\0')
  self.assertNotIn(b'VMAD',rows[0xA36BE][1])
  self.assertEqual(rows[0x1C2691][1][b'EDID'],b'SyntheticCurrentDunmoreInventory\0')
  self.assertIn('11 actor(s): 7 male, 3 female, 1 of no one sex',p.stdout)
  self.assertIn('1 of 20 name one',p.stdout)
  self.assertIn('looks: those of SyntheticCurrentDunmoreInventory (1C2691:Fallout4.esm), male, number 7 of 7',p.stdout)
  self.assertIn('looks: those of StandInSettlerMale01 (113340:Fallout4.esm), male, number 1 of 7',p.stdout)
  emitted=records(OUT/'default/out/TheLastMeridian.esp');d=emitted[0x01000843][1]
  self.assertFalse(struct.unpack_from('<H',d[b'ACBS'],14)[0]&0x100)
  self.assertEqual(struct.unpack_from('<I',d[b'TPTA'],32)[0],0)
  self.assertEqual(d[b'DOFT'],struct.pack('<I',0x01000F8A))
  self.assertEqual(emitted[0x01000F8A][0],b'OTFT')
  self.assertEqual([v for k,v in emitted[0x01000F8A][2]if k==b'INAM'],[struct.pack('<I',0xA36BE)])
 def test_each_wrong_typed_graph_and_wrong_inventory_authority_refuses(self):
  for variant in ['wardrobe-missing','wardrobe-wrong-type','wardrobe-wrong-model','wardrobe-wrong-race','wardrobe-extra-armature','wardrobe-wrong-template']:
   with self.subTest(variant=variant):
    p,_=run(variant);self.assertNotEqual(p.returncode,0)
    reason='Original Dunmore inventory authority changed'if variant=='wardrobe-wrong-template'else'Verified native patched suit donor changed'
    self.assertIn(reason,p.stderr)
if __name__=='__main__':unittest.main()
