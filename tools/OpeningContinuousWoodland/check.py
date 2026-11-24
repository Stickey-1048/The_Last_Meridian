"""Independent finite decoded field, operative surfaces and changed passive screen."""
from pathlib import Path
import sys,json,math,struct,copy,hashlib,unittest
R=Path(__file__).resolve().parents[2];HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(R/'tools/SheriffWorld'));from raw import records,decode,ground,pose,form,box
BASE=R.parent/'opening-authored-woodland-001/tools/OpeningAuthoredWoodland/build/woodland-005/TLMWorldSlice.esp';OUT=HERE/'build/continuous-005/TLMWorldSlice.esp'
OLD,ON=records(BASE);NOW,NN=records(OUT);S=json.loads((HERE/'footings.json').read_text());P={p['id']:p for p in S['poses']}
CS={struct.unpack_from('<ii',r['tags'][b'XCLC']):r for r in NOW.values()if r['type']=='CELL'and b'XCLC'in r['tags']};LS={xy:next(r for r in NOW.values()if r['type']=='LAND'and(6,c['id'])in r['parents'])for xy,c in CS.items()};PATCH={(0,0):0xf29b,(1,0):0xf29c,(0,1):0xf2bc,(1,1):0xf2bd};IDS={LS[xy]['id']for xy in PATCH}
NATIVE=Path('C:/Program Files (x86)/GOG Galaxy/Games/Fallout 4 GOTY/Data/Fallout4.esm');SRC,_=records(NATIVE,set(PATCH.values()));NH={fid:decode(r)for fid,r in SRC.items()};OH={xy:decode(OLD[r['id']])for xy,r in LS.items()}
MODELS={}
for path in S['modelInputs']:
 for a in json.loads((R/path).read_text())['assets'].values():
  if 'bottomBandBounds'in a.get('nif',{}):MODELS[int(a['id'],16)]=a
PADS=[(256,512,1024,1152),(1664,1792,2304,2304),(128,1536,1536,1920),(1024,1408,1280,1664),(2304,2432,3840,3968),(1536,2560,2176,3072),(1280,128,2944,896),(3564,2814,4076,3356)]
ROUTES=[[(448,640),(700,900),(1050,1133),(1900,1700),(2600,2200),(3048,2200),(3048,2432)],[(1200,1200),(2200,1000),(2700,1700),(2600,2200)],[(2600,2200),(2260,2200),(1880,2480),(1880,2560)],[(2260,2200),(2260,3558),(3050,3558),(3050,3572)]]
def route_distance(x,y):
 best=1e20
 for route in ROUTES:
  for(a,b),(c,d)in zip(route,route[1:]):
   t=max(0,min(1,((x-a)*(c-a)+(y-b)*(d-b))/((c-a)**2+(d-b)**2)));best=min(best,math.hypot(x-a-t*(c-a),y-b-t*(d-b)))
 return best
def protected(x,y):return x<=4096 and y<=4096 and(any(a<=x<=c and b<=y<=d for a,b,c,d in PADS)or route_distance(x,y)<=640+.0001)
ANCHORS=[(x*128,y*128,OH[0,0][y][x])for y in range(33)for x in range(33)if protected(x*128,y*128)]
def grids(rows):return{xy:decode(rows[r['id']])for xy,r in LS.items()}
def surface(h,x,y,f=False):cx,cy=math.floor(x/4096),math.floor(y/4096);return ground(h[cx,cy],x-cx*4096,y-cy*4096,f)
def preserve(rows):
 assert len(rows)==len(OLD)==790 and set(rows)==set(OLD)
 for fid,a in OLD.items():
  b=rows[fid];assert(a['type'],a['flags'],a['parents'],a['header'][16:])==(b['type'],b['flags'],b['parents'],b['header'][16:])
  skip={b'VHGT',b'VNML'}if fid in IDS else{b'DATA'}if a['name']in P else set()
  assert[(k,v)for k,v in a['ordered']if k not in skip]==[(k,v)for k,v in b['ordered']if k not in skip],('outside finite delta',a['name'])
  if not skip:assert a==b
  if a['name']in P:
   p=P[a['name']];assert pose(a)[:3]==p['oldXYZ']and max(abs(x-y)for x,y in zip(pose(b)[:3],p['xyz']))<.001 and pose(a)[3:]==pose(b)[3:]
def field(rows):
 h=grids(rows);nativeExact=0;changed=0
 for(cx,cy),fid in PATCH.items():
  for y in range(33):
   for x in range(33):
    wx,wy=cx*4096+x*128,cy*4096+y*128;old=OH[cx,cy][y][x];expected=old
    if not protected(wx,wy):
     cap=min(z+.4*math.hypot(wx-ax,wy-ay)for ax,ay,z in ANCHORS);target=min(NH[fid][y][x]-7000,cap);t=max(0,min(1,(min(wx,wy,8192-wx,8192-wy)-128)/896));t=t*t*(3-2*t);expected=round((old+(target-old)*t)/8)*8
    assert h[cx,cy][y][x]==expected,'independent signed native/operative envelope field'
    nativeExact+=h[cx,cy][y][x]==NH[fid][y][x]-7000;changed+=h[cx,cy][y][x]!=old
 return h,nativeExact,changed
def normals(rows,h):
 def H(gx,gy):
  v=[a[gy-cy*32][gx-cx*32]for(cx,cy),a in h.items()if cx*32<=gx<=cx*32+32 and cy*32<=gy<=cy*32+32];assert v and min(v)==max(v),'height seam';return v[0]
 for(cx,cy)in PATCH:
  n=rows[LS[cx,cy]['id']]['tags'][b'VNML']
  for y in range(33):
   for x in range(33):
    gx,gy=cx*32+x,cy*32+y;offset=(y*33+x)*3
    if min(gx*128,gy*128,8192-gx*128,8192-gy*128)<=128:assert n[offset:offset+3]==OLD[LS[cx,cy]['id']]['tags'][b'VNML'][offset:offset+3];continue
    dx=(H(gx+1,gy)-H(gx-1,gy))/256;dy=(H(gx,gy+1)-H(gx,gy-1))/256;l=math.sqrt(dx*dx+dy*dy+1);assert struct.unpack_from('<3b',n,offset)==tuple(round(v*127/l)for v in(-dx,-dy,1))
 for(cx,cy),a in h.items():
  for other,ap,bp in[((cx+1,cy),[(32,i)for i in range(33)],[(0,i)for i in range(33)]),((cx,cy+1),[(i,32)for i in range(33)],[(i,0)for i in range(33)])]:
   if other not in h:continue
   aa,bb=rows[LS[cx,cy]['id']]['tags'][b'VNML'],rows[LS[other]['id']]['tags'][b'VNML']
   for(ax,ay),(bx,by)in zip(ap,bp):
    assert a[ay][ax]==h[other][by][bx]
    na,nb=aa[(ay*33+ax)*3:(ay*33+ax)*3+3],bb[(by*33+bx)*3:(by*33+bx)*3+3]
    if na!=nb:assert na==OLD[LS[cx,cy]['id']]['tags'][b'VNML'][(ay*33+ax)*3:(ay*33+ax)*3+3]and nb==OLD[LS[other]['id']]['tags'][b'VNML'][(by*33+bx)*3:(by*33+bx)*3+3],'new normal seam'
def operative(h):
 sites=[pose(r)[:2]for r in OLD.values()if r['type']in('ACHR','REFR')and r['name'].startswith('TLM_WS_ST_')and 0<=pose(r)[0]<4096 and 0<=pose(r)[1]<4096]+[[740,840],[3212,2474]]
 for x,y in sites:
  for i in range(-4,5):
   for j in range(-4,5):
    for f in(False,True):assert abs(surface(h,x+i*32,y+j*32,f)-surface(OH,x+i*32,y+j*32,f))<.001,'operative128 footprint changed'
 return len(sites)
def feet(rows,h):
 worst=0
 for name,p in P.items():
  r=rows[ON[name]['id']];q=pose(r);a=MODELS[form(r['tags'][b'NAME'])];s=struct.unpack('<f',r['tags'].get(b'XSCL',struct.pack('<f',1)))[0];foot=[v*s for v in a['nif']['bottomBandBounds']];b=box(foot,q[:3],q[3:]);v=[surface(h,b[0]+(b[3]-b[0])*i/16,b[1]+(b[4]-b[1])*j/16,f)for i in range(17)for j in range(17)for f in(False,True)];limit=40 if q[0]<4096 and q[1]<4096 else 64;assert b[2]<=min(v)+.001 and max(v)-b[2]<=limit+.001,'passive footing air/embed';worst=max(worst,max(v)-b[2])
 return worst
def rays(h,x,y):
 result=[]
 for angle in(0,15,30,45,60,75,90):
  dx,dy=math.sin(math.radians(angle)),math.cos(math.radians(angle));times={0.,2400.}
  # Exact intersections with grid edges and BOTH possible triangle diagonals.
  for origin,direction in[(x,dx),(y,dy),(y-x,dy-dx),(x+y,dx+dy)]:
   if abs(direction)<1e-9:continue
   for k in range(-128,129):
    t=(k*128-origin)/direction
    if 0<t<2400:times.add(t)
  ts=sorted(times);allGrades=[];changedGrades=[];retainedGrades=[]
  for a,b in zip(ts,ts[1:]):
   for f in(False,True):
    va,vb=surface(h,x+dx*a,y+dy*a,f),surface(h,x+dx*b,y+dy*b,f);grade=(vb-va)/(b-a);allGrades.append(grade)
    olda,oldb=surface(OH,x+dx*a,y+dy*a,f),surface(OH,x+dx*b,y+dy*b,f)
    (retainedGrades if abs(va-olda)+abs(vb-oldb)<.001 else changedGrades).append(grade)
  result.append({'bearingFromNorth':angle,'maximumUphillGrade':max(allGrades),'maximumChangedUphillGrade':max(changedGrades,default=0),'maximumLiteralRetainedUphillGrade':max(retainedGrades,default=0)})
 return result
def moved_clearance(rows):
 sites=[pose(r)[:2]for r in OLD.values()if r['type']in('ACHR','REFR')and r['name'].startswith('TLM_WS_ST_')and 0<=pose(r)[0]<4096 and 0<=pose(r)[1]<4096];minimum=1e20
 for name,p in P.items():
  if p['oldXYZ'][:2]==p['xyz'][:2]:continue
  r=rows[ON[name]['id']];q=pose(r);a=MODELS[form(r['tags'][b'NAME'])];scale=struct.unpack('<f',r['tags'].get(b'XSCL',struct.pack('<f',1)))[0];b=box([v*scale for v in a['nif']['renderBounds']],q[:3],q[3:])
  def point(v):return math.hypot(max(b[0]-v[0],v[0]-b[3],0),max(b[1]-v[1],v[1]-b[4],0))
  distance=min(point(v)for v in sites);assert distance>=128,'changed XY actor/control corner intrusion';minimum=min(minimum,distance)
  # Convex rectangle/segment separation, including crossing through the box.
  for route in ROUTES:
   for aa,bb in zip(route,route[1:]):
    lo,hi=0.,1.
    for i in range(2):
     d=bb[i]-aa[i]
     if abs(d)<1e-9:
      if aa[i]<b[i]or aa[i]>b[i+3]:lo,hi=1,0;break
     else:
      lower,upper=sorted(((b[i]-aa[i])/d,(b[i+3]-aa[i])/d));lo=max(lo,lower);hi=min(hi,upper)
    assert lo>hi,'changed XY crosses route'
    ds=[point(aa),point(bb)]
    for x in(b[0],b[3]):
     for y in(b[1],b[4]):
      dx,dy=bb[0]-aa[0],bb[1]-aa[1];t=max(0,min(1,((x-aa[0])*dx+(y-aa[1])*dy)/(dx*dx+dy*dy)));ds.append(math.hypot(x-aa[0]-t*dx,y-aa[1]-t*dy))
    assert min(ds)>=96,'changed XY narrows route'
 return minimum
class Checks(unittest.TestCase):
 def test_finite_literal_records_and_materials(self):preserve(NOW)
 def test_actual_vhgt_field_and_seam_normals(self):h,n,c=field(NOW);self.assertGreater(n,1000);self.assertGreater(c,1000);normals(NOW,h)
 def test_actual_operative_surfaces(self):operative(grids(NOW))
 def test_changed_passive_feet(self):feet(NOW,grids(NOW))
 def test_changed_xy_actor_control_and_route_clearance(self):moved_clearance(NOW)
 def test_seen_sheriff_wall_slopes(self):self.assertLessEqual(max(q['maximumChangedUphillGrade']for q in rays(grids(NOW),3212,2474)),.5)
 def test_refuse_changed_actor_or_material(self):
  for fid,key in[(next(r['id']for r in OLD.values()if r['type']=='ACHR'),b'DATA'),(LS[0,0]['id'],b'VTXT')]:
   bad=copy.deepcopy(NOW);bad[fid]['ordered']=[(k,v+b'X'if k==key else v)for k,v in bad[fid]['ordered']]
   with self.assertRaises(AssertionError):preserve(bad)
 def test_refuse_previous_cliff_field(self):
  with self.assertRaises(AssertionError):self.assertLessEqual(max(q['maximumUphillGrade']for q in rays(OH,3212,2474)),.5)
 def test_refuse_passive_float(self):
  bad=copy.deepcopy(NOW);p=next(iter(P.values()));r=bad[ON[p['id']]['id']];v=pose(r);v[2]+=100;r['tags'][b'DATA']=struct.pack('<6f',*v)
  with self.assertRaises(AssertionError):feet(bad,grids(NOW))
if __name__=='__main__':
 result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(Checks))
 if not result.wasSuccessful():sys.exit(1)
 sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest().upper();h,n,c=field(NOW)
 receipt={'scope':'Observed wall source repair; no native quality/Havok claim','world':sha(OUT),'baseline':sha(BASE),'records':len(NOW),'fixedCoreVertices':len(ANCHORS),'nativeExactVertices':n,'changedVertices':c,'operativeSurfaceSites':operative(h),'passivePoses':len(P),'xyChanges':sum(p['oldXYZ'][:2]!=p['xyz'][:2]for p in P.values()),'maximumFootEmbed':feet(NOW,h),'changedXYMinimumActorControlClearance':moved_clearance(NOW),'profilesY3200':[{'x':x,'before':surface(OH,x,3200),'after':surface(h,x,3200)}for x in range(3840,5377,128)],'sourceViewRays':{name:rays(h,*xy)for name,xy in{'Sheriff':(3212,2474),'Dispatch':(740,920),'Midroute':(2600,2200)}.items()},'nativeOpen':['actual terrain/silhouette/foliage','actual cabin entry/collision','retained operative gradients and remote inherited outer edges are not universal gentle slopes']}
 receipt['sourcePins']={str(p.relative_to(R)).replace('\\','/'):sha(p)for p in[Path(__file__),HERE/'footings.json',HERE/'make_footings.py',R/'tools/WorldSliceBuilder/OpeningContinuousWoodland.cs',R/'tools/WorldSliceBuilder/Program.cs']};(HERE/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt,indent=2))
