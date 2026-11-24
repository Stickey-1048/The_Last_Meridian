"""Finite033 actual-byte/decoded geometry/NIF/paint checks; no builder/native or ancestor suites."""
from pathlib import Path
import sys,struct,json,math,hashlib,copy,unittest
H=Path(__file__).resolve().parent;R=H.parents[1];sys.path.insert(0,str(H));import make_plan as m,cargo_mesh as mesh
sys.path.insert(0,str(R/'tools/OpeningWreckTableau'));import make_plan as unused
# Name conflict avoided: route helpers loaded explicitly from previously accepted finite checker.
import importlib.util
sp=importlib.util.spec_from_file_location('Clearance028',R/'tools/OpeningWreckTableau/make_plan.py');clear=importlib.util.module_from_spec(sp);sp.loader.exec_module(clear)
from raw import records,pose,decode,box
BASE=m.BASE;OUT=R/'build/ridge-spill-finish-world-002/TLMWorldSlice.esp';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest().upper()
OLD,ON=records(BASE);NOW,NN=records(OUT);PLAN=json.loads((H/'plan.json').read_text());MODELS=json.loads((H/'models.json').read_text())['assets'];EXPECTED=copy.deepcopy(m.NEW)
ACTUAL={g:decode(NOW[fid])for g,fid in m.LANDS.items()};m.NEW=ACTUAL
DATA={0x2000000+p['localId']:p for p in PLAN['cargo']+PLAN['footings']};POSTS={0x2000000+i for i in PLAN['posts']};GEOM={m.LANDS[(1,0)],m.LANDS[(1,1)]};CORE=m.LANDS[(0,0)];ALLOWED=set(DATA)|POSTS|GEOM|{CORE}

def restore(data):
 old=BASE.read_bytes()
 def oldrecord(fid):
  h=OLD[fid]['header'];at=old.index(h);return old[at:at+24+struct.unpack_from('<I',h,4)[0]]
 def walk(at,end):
  parts=[]
  while at<end:
   h=data[at:at+24];n=struct.unpack_from('<I',h,4)[0]
   if h[:4]==b'GRUP':
    body=walk(at+24,at+n);hh=bytearray(h);struct.pack_into('<I',hh,4,len(body)+24);parts.append(bytes(hh)+body);at+=n
   else:
    fid=struct.unpack_from('<I',h,12)[0];parts.append(oldrecord(fid)if fid in ALLOWED else data[at:at+24+n]);at+=24+n
  assert at==end;return b''.join(parts)
 return walk(0,len(data))

def cargo_check(row,p):
 verts=mesh.transformed_vertices(row['asset'],p);z=min(v[2]for v in verts);feet=[v for v in verts if v[2]<z+1]
 errors=[v[2]-m.height(v[0],v[1],True,f)for v in feet for f in[False,True]]
 assert min(errors)>=-2 and max(errors)<=1,('NIF contact',row['id'],min(errors),max(errors))
 b=[min(v[i]for v in verts)for i in range(3)]+[max(v[i]for v in verts)for i in range(3)]
 road=clear.routeclear(b);op=min(clear.pointbox(pose(NOW[i])[:2],b)for i in clear.CONTROLS);assert road>=96 and op>=128
 return {'id':row['id'],'actualFootVertices':len(feet),'minContactError':min(errors),'maxContactError':max(errors),'route':road,'operative':op,'renderBounds':b}
def foot_check(row,p):
 a=MODELS[row['asset']];foot=[x*row['scale']for x in a['nif']['bottomBandBounds']];b=box(foot,p[:3],p[3:]);lo,hi,n=m.extent(b);assert hi-lo<=row['supportRangeLimit'];assert abs(p[2]-(lo-foot[5]-3))<1e-3;assert hi-(p[2]+foot[2])<=64+.001
 return {'id':row['id'],'range':hi-lo,'limit':row['supportRangeLimit'],'maximumEmbed':hi-p[2]-foot[2],'existingOuterEmbedLimit':64,'criticalPoints':n}
def hpoint(field,x,y):
 vals=[h[y-g[1]*32][x-g[0]*32]for g,h in field.items()if g[0]*32<=x<=g[0]*32+32 and g[1]*32<=y<=g[1]*32+32]
 assert vals and max(vals)==min(vals);return vals[0]
def alpha(row):
 out={};header=None
 for k,v in row['ordered']:
  if k==b'ATXT':header=struct.unpack('<IBBH',v)
  if k==b'VTXT':assert header is not None and len(v)==289*8;out[(header[1],header[3])]=[struct.unpack_from('<HHf',v,i*8)for i in range(289)]
 return out
class Checks(unittest.TestCase):
 def test_finite_raw_inverse_and_all_other_records(self):
  assert set(NOW)==set(OLD)and len(NOW)==896 and len(DATA)==33 and len(POSTS)==4 and len(ALLOWED)==40
  assert restore(OUT.read_bytes())==BASE.read_bytes()and NOW[0]==OLD[0]
  for fid,old in OLD.items():
   q=NOW[fid]
   if fid not in ALLOWED:assert q==old,hex(fid);continue
   assert q['parents']==old['parents']and q['type']==old['type']
   if fid in POSTS:
    assert q['flags']==old['flags']|0x800 and q['ordered']==old['ordered']and q['header'][:8]+old['header'][8:12]+q['header'][12:]==old['header']
   else:
    tags={b'DATA'}if fid in DATA else{b'VHGT',b'VNML'}if fid in GEOM else{b'VTXT'}
    assert q['flags']==old['flags']and[(k,v)for k,v in q['ordered']if k not in tags]==[(k,v)for k,v in old['ordered']if k not in tags]
    assert q['header'][:4]+old['header'][4:8]+q['header'][8:]==old['header']
 def test_actual_heightmaps_exact_core_and_all_pads_literal(self):
  assert ACTUAL==EXPECTED
  assert NOW[CORE]['tags'][b'VHGT']==OLD[CORE]['tags'][b'VHGT']and NOW[CORE]['tags'][b'VNML']==OLD[CORE]['tags'][b'VNML']
  for fid,row in DATA.items():assert max(abs(a-b)for a,b in zip(pose(NOW[fid]),row['pose']))<1e-4
  assert all(NOW[i]==OLD[i]for i,q in OLD.items()if q['type']=='ACHR')
 def test_outer_rows_shared_seam_and_normals(self):
  for g in[(1,0),(1,1)]:
   old,new=m.OLD[g],ACTUAL[g];ob=OLD[m.LANDS[g]]['tags'][b'VNML'];nb=NOW[m.LANDS[g]]['tags'][b'VNML']
   for y in range(33):
    for x in range(33):
     gx,gy=g[0]*32+x,g[1]*32+y;at=(y*33+x)*3
     if gx<=33 or gx>=63 or gy<=1 or gy>=63:
      assert old[y][x]==new[y][x]and nb[at:at+3]==ob[at:at+3]
      # Every available central derivative neighbor is unchanged here; unowned outer world not certified.
      for dx,dy in[(-1,0),(1,0),(0,-1),(0,1)]:
       try:assert hpoint(ACTUAL,gx+dx,gy+dy)==hpoint(m.OLD,gx+dx,gy+dy)
       except AssertionError:
        if any(k[0]*32<=gx+dx<=k[0]*32+32 and k[1]*32<=gy+dy<=k[1]*32+32 for k in ACTUAL):raise
      continue
     dx=(hpoint(ACTUAL,gx+1,gy)-hpoint(ACTUAL,gx-1,gy))/256;dy=(hpoint(ACTUAL,gx,gy+1)-hpoint(ACTUAL,gx,gy-1))/256;l=math.sqrt(dx*dx+dy*dy+1);expected=bytes((round(a*127/l)&255)for a in[-dx,-dy,1]);assert nb[at:at+3]==expected,(g,x,y)
  a,b=NOW[m.LANDS[(1,0)]]['tags'][b'VNML'],NOW[m.LANDS[(1,1)]]['tags'][b'VNML'];assert a[32*33*3:]==b[:33*3]
 def test_thirty_existing_passive_feet_unchanged_limits(self):
  assert len(PLAN['footings'])==30 and {k:v for k,v in m.make().items()if k!='models'}==PLAN
  for row in PLAN['footings']:
   q=NOW[0x2000000+row['localId']];p=pose(q);assert p[:2]==row['oldPose'][:2]and p[3:]==row['oldPose'][3:];foot_check(row,p)
 def test_three_actual_nif_cargo_contacts_and_clearance(self):
  assert len(PLAN['cargo'])==3
  for row in PLAN['cargo']:
   assert mesh.assets[row['asset']]['nif']['sha256']==MODELS[row['asset']]['nif']['sha256'];cargo_check(row,pose(NOW[0x2000000+row['localId']]))
  # Explicit handed basis independent of bounding-box helper: +Y-pitch maps +Z to-X and +X to+Z.
  p=[0,0,0,0,math.pi/2,0];c,s=math.cos(p[4]),math.sin(p[4]);assert abs(c)<1e-10 and abs(s-1)<1e-10
 def test_paint_only_low_leaf_gravel_and_zero_worn_center(self):
  old,new=alpha(OLD[CORE]),alpha(NOW[CORE]);assert old.keys()==new.keys()and len(new)==12
  for q in range(4):
   for i in range(289):
    x=(i%17+(q&1)*16)*128;y=(i//17+(q>>1)*16)*128;d=clear.pointseg((x,y),clear.ROAD[0],clear.ROAD[1]);d=min(clear.pointseg((x,y),a,b)for a,b in zip(clear.ROAD,clear.ROAD[1:]));t=max(0,min(1,(d-96)/64));factor=t*t*(3-2*t)
    a,b,c=[old[(q,k)][i][2]for k in range(3)];v=[new[(q,k)][i][2]for k in range(3)]
    assert all(old[(q,k)][i][:2]==new[(q,k)][i][:2]for k in range(3))
    if x in[0,4096]or y in[0,4096]:assert v==[a,b,c];continue
    assert abs(v[0]-a*factor)<2e-6 and abs(v[1]-(b+(a-a*factor)*.55))<2e-6 and v[2]==c
    assert min(v)>=0 and sum(v)<=1.000002
    if d<96-.001:assert v[0]==0
 def test_four_editorial_desc_all_quests_audio_and_no_new_forms(self):
  for fid,q in OLD.items():
   if q['type']in['MESG','QUST','SNDR','NPC_','WRLD','CELL','GRAS','LTEX']:assert NOW[fid]==q
  assert struct.unpack('<fII',NOW[0]['tags'][b'HEDR'])[1:]==(944,2943)
 def test_support_and_floating_cargo_mutants_refused(self):
  row=PLAN['cargo'][0];p=pose(NOW[0x2000000+row['localId']]);p[2]+=12
  with self.assertRaises(AssertionError):cargo_check(row,p)
  row=PLAN['footings'][0];p=pose(NOW[0x2000000+row['localId']]);p[2]+=60
  with self.assertRaises(AssertionError):foot_check(row,p)
if __name__=='__main__':
 result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(Checks))
 if not result.wasSuccessful():raise SystemExit(1)
 rays=[]
 for deg in[35,40,45,50,56,60,65,70,75]:
  peaks=[]
  for new in[False,True]:
   points=[]
   for d in range(512,11265,64):
    x,y=448+math.sin(math.radians(deg))*d,640+math.cos(math.radians(deg))*d
    if(int(x//4096),int(y//4096))not in ACTUAL:continue
    z=max(m.height(x,y,new,f)for f in[False,True]);points.append({'distance':d,'xyz':[x,y,z],'degrees':math.degrees(math.atan2(z+64,d))})
   peaks.append(max(points,key=lambda p:p['degrees']))
  rays.append({'bearing':deg,'before':peaks[0],'after':peaks[1]})
 rec={'scope':'Approved finite art033 only; appearance/Havok/LOD stillopen','baselineSha256':sha(BASE),'worldSha256':sha(OUT),'methods':result.testsRun,'recordMembership':896,'allowedChangedRecords':sorted(hex(i)for i in ALLOWED),'cargo':[cargo_check(p,pose(NOW[0x2000000+p['localId']]))for p in PLAN['cargo']],'passiveFootings':[foot_check(p,pose(NOW[0x2000000+p['localId']]))for p in PLAN['footings']],'rays':rays,'camera':'sourceXY448,640/yaw45/configuredworldFOV70/assumedeyeZ-64; not runtimemeasured','derivativeGuard':'7936 endpoint adds one unchangedheightrow to preservetwoheight+normalrows; actualdecodednormals/seamchecked','sourcePins':{str(p.relative_to(R)).replace('\\','/'):sha(p)for p in[H/'plan.json',H/'models.json',H/'make_plan.py',H/'cargo_mesh.py',H/'check.py',R/'tools/WorldSliceBuilder/OpeningRidgeSpillFinish.cs',R/'tools/WorldSliceBuilder/Program.cs']},'native':'NONE; no assets/export/install/stage/game/GPU/audio'}
 with(H/'receipt.json').open('x')as f:json.dump(rec,f,indent=2)
 print(json.dumps({k:v for k,v in rec.items()if k not in['passiveFootings','sourcePins','rays','allowedChangedRecords']},indent=2))
