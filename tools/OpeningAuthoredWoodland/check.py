"""Finite emitted-record/native-donor/physical screens; not native collision or art acceptance."""
from pathlib import Path
import sys,json,struct,math,hashlib,unittest,copy
R=Path(__file__).resolve().parents[2];HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(R/'tools/SheriffWorld'));from raw import records,pose,decode,ground,box,form
BASE=R.parent/'opening-mountain-structure-001/tools/OpeningMountainStructure/build/structure-001/TLMWorldSlice.esp'
OUT=HERE/'build/woodland-005/TLMWorldSlice.esp';NATIVE=Path('C:/Program Files (x86)/GOG Galaxy/Games/Fallout 4 GOTY/Data/Fallout4.esm')
OLD,ON=records(BASE);NOW,NN=records(OUT);DONORS={(1,0):0xf29c,(0,1):0xf2bc,(1,1):0xf2bd};SRC,_=records(NATIVE,set(DONORS.values())|{0x19dde8})
PLAN=json.loads((HERE/'placements.json').read_text());POSES={p['id']:p for p in PLAN['poses']};DISABLED={p['id']:p for p in PLAN['disabled']};FIT=json.loads((HERE/'cabin-fit.json').read_text());CABIN=NN[PLAN['cabin']['id']]
cells={struct.unpack_from('<ii',r['tags'][b'XCLC']):r for r in NOW.values()if r['type']=='CELL'and b'XCLC'in r['tags']}
lands={xy:next(r for r in NOW.values()if r['type']=='LAND'and(6,c['id'])in r['parents'])for xy,c in cells.items()};PATCHIDS={lands[k]['id']for k in DONORS}
models=json.loads((R/'tools/AppalachianRidges/models.json').read_text())['assets'];BYBASE={int(a['id'],16):a for a in models.values()}
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest().upper()
def preserve(rows):
 assert len(OLD)==789 and len(rows)==790 and set(rows)==set(OLD)|{CABIN['id']}
 for fid,a in OLD.items():
  b=rows[fid];assert(a['type'],a['parents'],a['header'][16:])==(b['type'],b['parents'],b['header'][16:])
  assert b['flags']==a['flags']|(0x800 if a['name']in DISABLED else 0),'flags outside explicit panel whitelist'
  skip={b'HEDR'}if a['type']=='TES4'else{b'VHGT',b'VNML',b'BTXT',b'ATXT',b'VTXT',b'VTEX'}if fid in PATCHIDS else{b'DATA'}if a['name']in POSES else set()
  assert[(k,v)for k,v in a['ordered']if k not in skip]==[(k,v)for k,v in b['ordered']if k not in skip],('unapproved source record delta',a['name'],a['type'])
  if a['name']in POSES:
   p=POSES[a['name']];assert pose(a)[:3]==p['oldXYZ'];assert max(abs(x-y)for x,y in zip(pose(b)[:3],p['xyz']))<.001;assert pose(a)[3:]==pose(b)[3:]
  elif fid not in PATCHIDS and a['type']!='TES4':assert a['ordered']==b['ordered']
 # Explicit entire serialized actor/controller/VMAD/QOBJ carry, not just new props.
 for fid,a in OLD.items():
  if a['type']in('ACHR','QUST'):assert a==rows[fid],'actor/controller literal'
def distance(x,y):
 p=[(4096,0),(8192,0),(8192,8192),(0,8192),(0,4096),(4096,4096)]
 def seg(a,b):
  dx,dy=b[0]-a[0],b[1]-a[1];t=max(0,min(1,((x-a[0])*dx+(y-a[1])*dy)/(dx*dx+dy*dy)));return math.hypot(x-a[0]-t*dx,y-a[1]-t*dy)
 return min(seg(p[i],p[(i+1)%6])for i in range(6))
def terrain(rows):
 hs={xy:decode(rows[r['id']])for xy,r in lands.items()};nativeCount=0
 for xy,fid in DONORS.items():
  a=decode(OLD[lands[xy]['id']]);s=decode(SRC[fid]);h=hs[xy]
  for y in range(33):
   for x in range(33):
    d=distance(xy[0]*4096+x*128,xy[1]*4096+y*128);t=max(0,min(1,(d-128)/896));t=t*t*(3-2*t);expected=round((a[y][x]*(1-t)+(s[y][x]-7000)*t)/8)*8
    assert h[y][x]==expected,'native common datum/collar height'
    if t==1:nativeCount+=1
    if d<=128:assert rows[lands[xy]['id']]['tags'][b'VNML'][(y*33+x)*3:(y*33+x)*3+3]==OLD[lands[xy]['id']]['tags'][b'VNML'][(y*33+x)*3:(y*33+x)*3+3]
 for(x,y),h in hs.items():
  for other,aa,bb in[((x+1,y),[r[32]for r in h],[r[0]for r in hs.get((x+1,y),h)]),((x,y+1),h[32],hs.get((x,y+1),h)[0])]:
   if other in hs:assert aa==bb,'actual emitted height seam'
 return hs,nativeCount
def normals(rows,hs):
 def height(gx,gy):
  vals=[h[gy-cy*32][gx-cx*32]for(cx,cy),h in hs.items()if cx*32<=gx<=cx*32+32 and cy*32<=gy<=cy*32+32];assert vals and max(vals)==min(vals);return vals[0]
 for(cx,cy)in DONORS:
  n=rows[lands[cx,cy]['id']]['tags'][b'VNML']
  for y in range(33):
   for x in range(33):
    gx,gy=cx*32+x,cy*32+y
    if distance(gx*128,gy*128)<=128:continue
    dx=(height(gx+1,gy)-height(gx-1,gy))/256;dy=(height(gx,gy+1)-height(gx,gy-1))/256;length=math.sqrt(dx*dx+dy*dy+1);expect=tuple(round(v*127/length)for v in(-dx,-dy,1));assert struct.unpack_from('<3b',n,(y*33+x)*3)==expect,'actual gradient normal'
def layers(rows):
 tags={b'BTXT',b'ATXT',b'VTXT',b'VTEX'};stats=[]
 for xy,fid in DONORS.items():
  actual=[(k,v)for k,v in rows[lands[xy]['id']]['ordered']if k in tags];source=[(k,v)for k,v in SRC[fid]['ordered']if k in tags];assert actual==source,'literal native sparse layers/default header/unused bytes'
  entries=[struct.unpack_from('<HHf',v,o)for k,v in actual if k==b'VTXT'for o in range(0,len(v),8)];assert all(i<=288 and math.isfinite(w)and 0<=w<=1 for i,p,w in entries)
  stats.append({'land':f'{fid:08X}','entries':len(entries),'nonzeroUnused':sum(p!=0 for i,p,w in entries),'missingBaseQuadrants':4-sum(k==b'BTXT'for k,v in actual),'nullTextureHeaders':sum(k in(b'BTXT',b'ATXT')and form(v[:4])==0 for k,v in actual)})
 return stats
def feet(rows,hs):
 def h(x,y,f):cx,cy=math.floor(x/4096),math.floor(y/4096);return ground(hs[cx,cy],x-cx*4096,y-cy*4096,f)
 maxEmbed=0
 for name,p in POSES.items():
  if p['kind']!='passive-grounding':continue
  r=rows[ON[name]['id']];q=pose(r);a=BYBASE[form(r['tags'][b'NAME'])];scale=struct.unpack('<f',r['tags'].get(b'XSCL',struct.pack('<f',1)))[0];foot=[v*scale for v in a['nif']['bottomBandBounds']];b=box(foot,q[:3],q[3:]);v=[h(b[0]+(b[3]-b[0])*ix/16,b[1]+(b[4]-b[1])*iy/16,f)for iy in range(17)for ix in range(17)for f in(False,True)];assert b[2]<=min(v)+.01 and max(v)-b[2]<=64,'whole passive foot air/embed';maxEmbed=max(maxEmbed,max(v)-b[2])
 return maxEmbed
def cabin(rows):
 r=rows[CABIN['id']];p=pose(r);assert form(r['tags'][b'NAME'])==0x19dde8 and max(abs(a-b)for a,b in zip(p[:3],PLAN['cabin']['xyz']))<.001 and abs(p[5]+math.pi/2)<1e-6;assert(6,cells[0,0]['id'])in r['parents']and not r['flags']&0x800
 assert len(DISABLED)==27 and len(POSES)==54 and sum(p['kind']=='passive-grounding'for p in POSES.values())==44
 b=box(FIT['standingBandBounds'],p[:3],p[3:]);clear={}
 for name,xy in {'Sheriff':(3260,2530),'Pike':(2550,2920),'Vane':(3500,3130),'Keene':(3500,2900),'QA':(3212,2474)}.items():
  d=math.hypot(max(b[0]-xy[0],xy[0]-b[3],0),max(b[1]-xy[1],xy[1]-b[4],0));assert d>=128 if name!='QA'else d>=38;clear[name]=d
 # Actual native door gap remains96 at torso height; source floor support was
 # sampled against full-parent mesh triangles, not inferred from OBND alone.
 assert FIT['doorWidthAt80']==96
 for f in FIT['floorSupport']:assert f['samples']==81 and f['maxAir']<=.01 and f['maxEmbed']<=4
 return clear
class TestFinite(unittest.TestCase):
 def test_literal_membership_and_operative_carry(self):preserve(NOW)
 def test_actual_signed_heights_and_normals(self):h,n=terrain(NOW);self.assertGreater(n,900);normals(NOW,h)
 def test_native_sparse_masks(self):layers(NOW)
 def test_passive_feet(self):feet(NOW,terrain(NOW)[0])
 def test_cabin_actual_fit_and_original_actors(self):cabin(NOW)
 def test_refuse_core_and_actor_corruption(self):
  for fid,key in[(lands[0,0]['id'],b'VHGT'),(next(r['id']for r in OLD.values()if r['type']=='ACHR'),b'DATA')]:
   bad=copy.deepcopy(NOW);bad[fid]['ordered']=[(k,v+b'X'if k==key else v)for k,v in bad[fid]['ordered']]
   with self.assertRaises(AssertionError):preserve(bad)
 def test_refuse_native_paint_mutation(self):
  bad=copy.deepcopy(NOW);fid=lands[1,0]['id'];seen=False
  for i,(k,v)in enumerate(bad[fid]['ordered']):
   if k==b'VTXT':bad[fid]['ordered'][i]=(k,struct.pack('<H',289)+v[2:]);seen=True;break
  self.assertTrue(seen)
  with self.assertRaises(AssertionError):layers(bad)
 def test_refuse_floating_passive(self):
  bad=copy.deepcopy(NOW);p=next(p for p in POSES.values()if p['kind']=='passive-grounding');r=bad[ON[p['id']]['id']];v=pose(r);v[2]+=100;r['tags'][b'DATA']=struct.pack('<6f',*v)
  with self.assertRaises(AssertionError):feet(bad,terrain(NOW)[0])
if __name__=='__main__':
 result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(TestFinite))
 if not result.wasSuccessful():sys.exit(1)
 h,n=terrain(NOW);receipt={'scope':'Source/raw/native-donor projection only; not native collision/visual certification','world':sha(OUT),'baseline':sha(BASE),'master':sha(R.parent/'first-act-opening-voices-009/build/opening-voices-master-002/TheLastMeridian.esp'),'ownedMaster':sha(NATIVE),'records':len(NOW),'nativeExactInteriorVertices':n,'commonDatum':-7000,'collar':1024,'sparsePaint':layers(NOW),'maxPassiveEmbed':feet(NOW,h),'cabinClearances':cabin(NOW),'changedOldPoses':len(POSES),'disabledOldPanels':len(DISABLED),'nativeOpen':['full cabin collision/doorway/stairs','woodland silhouette and sparse texture appearance','paint transition at unmodified neighbors; no global shader-continuity claim']}
 receipt['sourcePins']={str(p.relative_to(R)).replace('\\','/'):sha(p)for p in[Path(__file__),HERE/'placements.json',HERE/'cabin-fit.json',HERE/'probe_cabins.py',HERE/'landscape-donors.json',HERE/'make_placements.py',R/'tools/WorldSliceBuilder/OpeningAuthoredWoodland.cs',R/'tools/WorldSliceBuilder/Program.cs']};(HERE/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt,indent=2))
