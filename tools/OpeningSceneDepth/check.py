"""Actual appended-scene raw/ground/reach envelope screen; native Havok OPEN."""
from pathlib import Path
import sys,json,struct,math,hashlib,copy,unittest
R=Path(__file__).resolve().parents[2];HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(R/'tools/SheriffWorld'))
from raw import records,decode,ground,pose,box,form,overlap
BASE=R.parent/'mountain-final-world-composition-001/tools/MountainFinalWorld/build/composed-001/TLMWorldSlice.esp';OUT=HERE/'build/scene-003/TLMWorldSlice.esp'
OLD,ON=records(BASE);NOW,NN=records(OUT)
MODELS=json.loads((HERE/'models.json').read_text())['assets'];PLAN=json.loads((HERE/'placements.json').read_text());P={p['id']:p for p in PLAN['placements']};O=json.loads((HERE/'old-obstacles.json').read_text())
CORE=next(r for r in OLD.values()if r['type']=='CELL'and r['tags'].get(b'XCLC',b'')[:8]==struct.pack('<ii',0,0));LAND=next(r for r in OLD.values()if r['type']=='LAND'and(6,CORE['id'])in r['parents']);H=decode(LAND)
def route_distance(x,y):
 best=1e9
 for route in PLAN['routes']:
  for (ax,ay),(bx,by)in zip(route,route[1:]):
   t=max(0,min(1,((x-ax)*(bx-ax)+(y-ay)*(by-ay))/((bx-ax)**2+(by-ay)**2)));best=min(best,math.hypot(x-ax-t*(bx-ax),y-ay-t*(by-ay)))
 return best
def point_box_distance(x,y,b):return math.hypot(max(b[0]-x,0,x-b[3]),max(b[1]-y,0,y-b[4]))
def scene(rows):
 added={r['name']:r for fid,r in rows.items()if fid not in OLD};assert set(added)==set(P)and len(added)==61
 assert len(rows)==758 and min(r['id']for r in added.values())>max(OLD)
 for fid,a in OLD.items():
  b=rows[fid];assert(a['type'],a['flags'],a['parents'])==(b['type'],b['flags'],b['parents'])
  if a['type']=='TES4':
   assert[(k,v)for k,v in a['ordered']if k!=b'HEDR']==[(k,v)for k,v in b['ordered']if k!=b'HEDR']
   av,ac,an=struct.unpack('<fII',a['tags'][b'HEDR']);bv,bc,bn=struct.unpack('<fII',b['tags'][b'HEDR']);assert av==bv and bc-ac==61 and bn-an==61
  else:assert a['header']==b['header']and a['ordered']==b['ordered'],('old record changed',a['name'])
 bounds={};worstEmbed=0
 for name,row in added.items():
  p=P[name];a=MODELS[p['asset']];m=a['nif'];v=pose(row);scale=struct.unpack('<f',row['tags'][b'XSCL'])[0]
  assert row['type']=='REFR'and not row['flags'] and row['parents']==CORE['parents']+[(6,CORE['id']),(9,CORE['id'])],'exact enabled temporary core parent'
  assert form(row['tags'][b'NAME'])==int(a['id'],16)and b'VMAD'not in row['tags'],'actual passive donor'
  assert all(abs(x-y)<.0002 for x,y in zip(v,[p['x'],p['y'],p['z'],0,0,p['yaw']]))and abs(scale-p['scale'])<1e-6
  rb=[x*scale for x in m['renderBounds']];fb=[x*scale for x in m['bottomBandBounds']];b=box(rb,v[:3],v[3:]);bounds[name]=b;radius=max(v[0]-b[0],b[3]-v[0],v[1]-b[1],b[4]-v[1])
  assert route_distance(v[0],v[1])>=96+radius,'192-wide original approach'
  assert all(point_box_distance(q[0],q[1],b)>=128 for q in O['actors']+O['operative']),'actor/interactive exact AABB envelope'
  assert not any(overlap(b,oldb)for _,oldb in O['obstacles']),'old hard-prop envelope'
  if p['support']is not None:
   bottom=v[2]+fb[2];assert abs(bottom-p['support'])<.001
   if name=='TLM_DEPTH_CabinLantern':
    parent=added['TLM_DEPTH_CabinDetail1'];base=MODELS[P[parent['name']]['asset']]['nif'];top=pose(parent)[2]+base['renderBounds'][5]
    assert -.05<=bottom-top<=.05,'actual crate support'
   else:assert p['support']==144 and 2664<=b[0]and b[3]<=3432 and 2672<=b[1]and b[4]<=3184,'existing floor support footprint'
   continue
  foot=fb if p['vegetation']else[rb[0],rb[1],fb[2],rb[3],rb[4],fb[5]];lo=1e9;hi=-1e9;c,s=math.cos(v[5]),math.sin(v[5])
  for i in range(17):
   for j in range(17):
    x=foot[0]+(foot[3]-foot[0])*i/16;y=foot[1]+(foot[4]-foot[1])*j/16
    for flip in(False,True):
     g=ground(H,v[0]+x*c+y*s,v[1]+y*c-x*s,flip);lo=min(lo,g);hi=max(hi,g)
  topFoot=v[2]+fb[5];embed=hi-topFoot;worstEmbed=max(worstEmbed,embed)
  assert topFoot<=lo+.1,'dense both-surface airgap'
  assert embed<=40,'bounded footing embed'
 for name,b in bounds.items():
  for other,a in bounds.items():
   if other>=name or (P[name]['vegetation']and P[other]['vegetation']):continue
   assert not overlap(b,a),'new hard-prop envelope'
 return {'appendedRefs':len(added),'vegetation':sum(p['vegetation']for p in P.values()),'solidDetail':sum(not p['vegetation']for p in P.values()),'maximumDenseFootEmbed':worstEmbed}
def tag(r,k,v):r['tags'][k]=v;r['ordered']=[(t,v if t==k else b)for t,b in r['ordered']]
class Checks(unittest.TestCase):
 def test_actual_append_ground_support_routes(self):scene(NOW)
 def test_only_three_parent_DATA_changes(self):
  before,_=records(R.parent/'opening-scene-depth-001/tools/OpeningSceneDepth/build/scene-002/TLMWorldSlice.esp');changed=[]
  self.assertEqual(before.keys(),NOW.keys())
  for fid,a in before.items():
   b=NOW[fid];self.assertEqual(a['header'],b['header']);self.assertEqual(a['parents'],b['parents'])
   if a['ordered']==b['ordered']:continue
   changed.append(a['name']);self.assertEqual([(k,v)for k,v in a['ordered']if k!=b'DATA'],[(k,v)for k,v in b['ordered']if k!=b'DATA'])
   self.assertEqual(pose(a)[3:],pose(b)[3:])
  self.assertEqual(set(changed),{'TLM_DEPTH_Woodland4Sapling3','TLM_DEPTH_Woodland4Scrub4','TLM_DEPTH_ShoulderStone9'})
 def test_floating_refused(self):
  rows=copy.deepcopy(NOW);r=rows[NN['TLM_DEPTH_ShoulderStone0']['id']];p=pose(r);p[2]+=100;tag(r,b'DATA',struct.pack('<6f',*p))
  original=P[r['name']]['z'];P[r['name']]['z']=p[2]
  try:
   with self.assertRaisesRegex(AssertionError,'airgap'):scene(rows)
  finally:P[r['name']]['z']=original
 def test_route_block_refused(self):
  rows=copy.deepcopy(NOW);r=rows[NN['TLM_DEPTH_Salvage0']['id']];p=pose(r);p[0:2]=[700,900];tag(r,b'DATA',struct.pack('<6f',*p))
  original=(P[r['name']]['x'],P[r['name']]['y']);P[r['name']]['x'],P[r['name']]['y']=p[:2]
  try:
   with self.assertRaisesRegex(AssertionError,'192-wide'):scene(rows)
  finally:P[r['name']]['x'],P[r['name']]['y']=original
 def test_old_quest_mutation_refused(self):
  rows=copy.deepcopy(NOW);r=rows[ON['TLM_WS_A1']['id']];tag(r,b'VMAD',r['tags'][b'VMAD']+b'bad')
  with self.assertRaises(AssertionError):scene(rows)
 def test_old_land_mutation_refused(self):
  rows=copy.deepcopy(NOW);r=rows[LAND['id']];b=bytearray(r['tags'][b'VHGT']);b[4]^=1;tag(r,b'VHGT',bytes(b))
  with self.assertRaises(AssertionError):scene(rows)
 def test_donor_mutation_refused(self):
  rows=copy.deepcopy(NOW);r=rows[NN['TLM_DEPTH_CabinDetail1']['id']];tag(r,b'NAME',struct.pack('<I',0))
  with self.assertRaises(AssertionError):scene(rows)
 def test_reported_diagonal_corner_regression(self):
  frozen=R.parent/'opening-scene-depth-001/tools/OpeningSceneDepth/placements.json';old={p['id']:p for p in json.loads(frozen.read_text())['placements']}
  for name in('TLM_DEPTH_Woodland4Sapling3','TLM_DEPTH_Woodland4Scrub4','TLM_DEPTH_ShoulderStone9'):
   b=old[name]['bounds'];x,y=old[name]['x'],old[name]['y'];radius=max(x-b[0],b[3]-x,y-b[1],b[4]-y)
   self.assertTrue(all(math.hypot(x-q[0],y-q[1])>=128+radius for q in O['actors']+O['operative']))
   self.assertLess(min(point_box_distance(q[0],q[1],b)for q in O['actors']+O['operative']),128)
if __name__=='__main__':
 result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(Checks))
 if not result.wasSuccessful():raise SystemExit(1)
 sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest().upper()
 receipt={'scope':'Source/local artifact three-pose clearance repair; native visual/collision OPEN','baseline':str(BASE),'baselineSha256':sha(BASE),'masterSha256':'350F01178F390DC33BD07A97EFE15E40F36950ED695C6FBD129A88A4DE07245F','output':str(OUT.relative_to(R)).replace('\\','/'),'outputSha256':sha(OUT),'oldRecordsPreserved':697,'totalRecords':len(NOW),'geometryScreen':scene(NOW),'methods':result.testsRun,'inputs':{str(p.relative_to(R)).replace('\\','/'):sha(p)for p in[HERE/'models.json',HERE/'placements.json',HERE/'old-obstacles.json',HERE/'make_scene.py',HERE/'repair_clearance.py',HERE/'clearance-repair-deltas.json',HERE/'check.py',R/'tools/WorldSliceBuilder/OpeningSceneDepth.cs',R/'tools/WorldSliceBuilder/Program.cs']}}
 (HERE/'receipt-repair.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt,indent=2))
