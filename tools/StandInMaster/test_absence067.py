"""Original absent donors vs explicitly lighting-positive synthetic inputs."""
import struct,sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from test_current060 import run,OUT,records
ORIGINALS=('unnamed-player','wrong-player','quest-evidence','weak-evidence')
def absence(rows):
 edids={fields.get(b'EDID') for _,fields,_ in rows.values()}
 assert b'QASmoke\0' not in edids and b'WorkshopNPC\0' not in edids
 return edids
def inventory(report):
 return {line.split()[1] for line in report.splitlines() if line.startswith('Cell ')}
class AbsenceContracts(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.data={v:run(v) for n in ORIGINALS for v in (n,n+"-with-lighting")}
 def test_four_original_absences_and_exact_first_missing_donor(self):
  for name in ORIGINALS:
   with self.subTest(name=name):
    p,rows=self.data[name];absence(rows)
    self.assertEqual(rows[0xF][1][b'EDID'],b'Caps001\0');self.assertEqual(rows[7][1][b'EDID'],b'Player\0')
    self.assertNotEqual(p.returncode,0);self.assertIn('Sequence contains no matching element',p.stderr)
    self.assertIn('CompleteBlackstoneEnvironment()',p.stderr)
    self.assertNotIn('BuildPritchardWardrobe()',p.stderr)
    if name in ('unnamed-player','wrong-player'):
     self.assertEqual(rows[0x14][0],b'ACHR');self.assertEqual(rows[0x14][1][b'NAME'],struct.pack('<I',7 if name=='unnamed-player'else 0x800))
    else:
     self.assertNotIn(0x14,rows)
     quests=[r for r in rows.values()if r[1].get(b'EDID',b'').startswith(b'StandInQuest')]
     self.assertEqual(len(quests),12 if name=='quest-evidence'else 2)
     self.assertEqual(sum(v==struct.pack('<I',0x14)for _,_,fields in quests for k,v in fields if k==b'ALFR'),len(quests))
 def test_four_lighting_variants_preserve_player_bytes_and_full_authority(self):
  expected={'QASmoke','TLM_CELL_NightMail','TLM_CELL_RedHollow','TLM_CELL_FourFlags','TLM_CELL_BlackLedger','TLM_CELL_BS_Service','TLM_CELL_BS_Lower','TLM_CELL_RH_SurfacePersistent','TLM_CELL_RH_Surface','TLM_CELL_BS_UpperPersistent','TLM_CELL_BS_Upper'}
  for name in ORIGINALS:
   with self.subTest(name=name):
    p,rows=self.data[name+'-with-lighting'];self.assertEqual(p.returncode,0,p.stderr)
    orig=self.data[name][1]
    for fid,row in orig.items():
     if fid in (7,0xF,0x14) or row[1].get(b'EDID',b'').startswith(b'StandInQuest'):
      self.assertEqual(rows[fid],row)
    report=(OUT/(name+'-with-lighting')/'out/TheLastMeridian.report.txt').read_text()
    self.assertEqual(inventory(report),expected)
    player=next(line for line in report.splitlines()if 'alias  0 Player  (reference)'in line)
    if name in ('unnamed-player','quest-evidence'):
     self.assertIn('[]  fill: forced 000014:Fallout4.esm',player)
    else:
     self.assertIn('[Optional]',player);self.assertNotIn('fill: forced',player)
    if name=='weak-evidence':self.assertIn('only 2',p.stdout)
 def test_default_and_existing_rh_negative_remain_exact(self):
  p,_=run('default');self.assertEqual(p.returncode,0,p.stderr)
  for name,why in [('rhe-no-light','RH real LIGH missing'),('rhe-static-model','RH environment exact model/bounds changed')]:
   p,_=run(name);self.assertNotEqual(p.returncode,0);self.assertIn(why,p.stderr)
if __name__=='__main__':unittest.main()
