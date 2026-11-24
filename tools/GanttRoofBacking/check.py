"""Finite roof append-only/raw/front-facing triangle coverage proof; no native claim."""
from pathlib import Path
import sys,struct,hashlib,json,unittest,math,copy
H=Path(__file__).resolve().parent;R=H.parents[1]
sys.path.insert(0,str(R/'tools/SheriffWorld'));from raw import records,pose
sys.path.insert(0,str(H));import geometry as g
BASE=R.parent/'gantt-prologue-optional-aliases-019/build/optional-aliases-world-001/TLMWorldSlice.esp'
OUT=R/'build/roof-backing-world-001/TLMWorldSlice.esp';MASTER=R.parent/'ada-book-voice-master-001/build/ada-book-master-001/TheLastMeridian.esp'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest().upper()
assert sha(BASE)=='A1670A40020130F45B2580AB5D6E20D173ED486CDCAD050C8B976836BE1AA63C'
OLD,ON=records(BASE);NOW,NN=records(OUT);IDS=set(range(0x2000b65,0x2000b6b));ROWS=[NOW[i]for i in sorted(IDS)];POSES=[pose(q)for q in ROWS]
def geometry_check(poses):
 c=g.coverage(poses);assert 241<c['renderZ'][0]<247 and c['renderZ'][1]<253
 return c

def strip_new(data):
 def walk(at,end):
  out=[]
  while at<end:
   h=data[at:at+24];n=struct.unpack_from('<I',h,4)[0]
   if h[:4]==b'GRUP':
    body=walk(at+24,at+n);hh=bytearray(h);struct.pack_into('<I',hh,4,len(body)+24);out.append(bytes(hh)+body);at+=n
   else:
    fid=struct.unpack_from('<I',h,12)[0];full=data[at:at+24+n]
    if fid not in IDS:
     if fid==0:
      b=BASE.read_bytes();full=b[:24+struct.unpack_from('<I',b,4)[0]]
     out.append(full)
    at+=24+n
  assert at==end;return b''.join(out)
 return walk(0,len(data))
class Checks(unittest.TestCase):
 def test_all_old_world_literal_after_tail_strip(self):
  assert set(NOW)==set(OLD)|IDS and len(NOW)==876
  assert strip_new(OUT.read_bytes())==BASE.read_bytes()
  for i in OLD:
   if i:assert NOW[i]==OLD[i],hex(i)
 def test_six_exact_stock_placements_and_parent(self):
  for j,q in enumerate(ROWS):
   assert q['type']=='REFR'and q['flags']==0 and q['parents'][-1]==(9,0x2000b46)
   assert struct.unpack('<I',q['tags'][b'NAME'])[0]==0x8eb6e
   assert b'VMAD'not in q['tags']and b'XSCL'not in q['tags']
   p=POSES[j];assert max(abs(a-b)for a,b in zip(p,[174.098388671875,[-475,-285,-95,95,285,475][j],139,0,math.pi/2,0]))<1e-5
 def test_actual_triangle_frontface_coverage_and_headroom(self):
  c=geometry_check(POSES);assert c['downFacingTriangles']>0 and c['verifiedSections']>=3
  # Actual roof overlay X+/-72.375,Y+/-508,Z226.125..240.875 stays underneath these backers.
  assert c['coveredRectangle']==[-75,-508,75,508]
 def test_opaque_donor_actual_nif_ancestry(self):
  n=g.assets['RRBoxcarDoor01Static']['nif'];assert n['sha256']=='CCA7441418B4CAE330EB47AA89E17F76549CCA869C9E3D2CC57189AECBC620AE'
  assert 'NiAlphaProperty'not in n['blocks']and n['materialStrings']==['materials\\SetDressing\\Railroad\\Boxcar02Blue.BGSM']
  assert len(g.DOOR)==60 and n['renderBounds'][2]>73
 def test_serialized_header_count(self):
  assert struct.unpack('<fII',NOW[0]['tags'][b'HEDR'])[1:]==(924,2923)
  b=OUT.read_bytes();counts=[0,0]
  def walk(at,end):
   while at<end:
    n=struct.unpack_from('<I',b,at+4)[0]
    if b[at:at+4]==b'GRUP':counts[1]+=1;walk(at+24,at+n);at+=n
    else:counts[0]+=1;at+=24+n
   assert at==end
  walk(0,len(b));assert counts==[876,49]and sum(counts)-1==924
 def test_gap_reverse_frontface_and_low_panel_mutants(self):
  p=copy.deepcopy(POSES);p[2][1]+=50
  with self.assertRaises(AssertionError):geometry_check(p)
  p=copy.deepcopy(POSES)
  for q in p:q[4]=-q[4]
  with self.assertRaises(AssertionError):geometry_check(p)
  p=copy.deepcopy(POSES)
  for q in p:q[2]-=80
  with self.assertRaises(AssertionError):geometry_check(p)
  original=g.DOOR
  try:
   # Remove all originally downward faces, retaining upward/boundary faces: bounds alone still pass.
   g.DOOR=[t for t in original if (t[1][1]-t[0][1])*(t[2][2]-t[0][2])-(t[1][2]-t[0][2])*(t[2][1]-t[0][1])>=-1e-7]
   with self.assertRaises(AssertionError):geometry_check(POSES)
  finally:g.DOOR=original
if __name__=='__main__':
 result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(Checks))
 if not result.wasSuccessful():raise SystemExit(1)
 rec={'scope':'Six static opaque roof backers only; full old world literal exceptTES4 bookkeeping','baselineSha256':sha(BASE),'worldSha256':sha(OUT),'masterSha256':sha(MASTER),'newRefs':[hex(i)for i in sorted(IDS)],'donor':'0008EB6E','coverage':geometry_check(POSES),'poses':POSES,'donorMetadata':g.assets['RRBoxcarDoor01Static'],'methods':result.testsRun,'sourcePins':{str(p.relative_to(R)).replace('\\','/'):sha(p)for p in[H/'geometry.py',H/'check.py',R/'tools/WorldSliceBuilder/GanttRoofBacking.cs',R/'tools/WorldSliceBuilder/Program.cs']},'limits':'Actual selected NIF full-parent triangles under declared clockwise Y basis; no native opacity/Havok/collision/finished-scene guarantee. Existing room/actor/light/quest/audio literal.'}
 (H/'receipt.json').write_text(json.dumps(rec,indent=2)+'\n');print(json.dumps({k:v for k,v in rec.items()if k not in['donorMetadata','sourcePins','poses']},indent=2))
