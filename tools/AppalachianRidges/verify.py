"""Finite independent raw projection screen; no native rendering/collision claim."""
from raw import *
import unittest,copy
BASE=ROOT.parents[2]/'sheriff-greenwater-world-composition-001/tools/SheriffWorld/build/composed-001/TLMWorldSlice.esp'
CURRENT=ROOT/'build/ridges-002/TLMWorldSlice.esp'
OLD,_=records(BASE); NEW,NAMES=records(CURRENT)
MODELS=json.loads((ROOT/'models.json').read_text())['assets']
CELLS={struct.unpack_from('<ii',r['tags'][b'XCLC']):r for r in NEW.values() if r['type']=='CELL' and b'XCLC'in r['tags']}
LANDS={xy:next(r for r in NEW.values() if r['type']=='LAND' and (6,c['id'])in r['parents']) for xy,c in CELLS.items()}
HEIGHTS={xy:decode(r)for xy,r in LANDS.items()}
def height(x,y):
 cx=min(1,max(-1,math.floor(x/4096)));cy=min(1,max(-2,math.floor(y/4096)));h=HEIGHTS[cx,cy]
 return [ground(h,x-cx*4096,y-cy*4096,f)for f in (False,True)]
def preservation(rows):
 assert len(OLD)==550
 for fid,a in OLD.items():
  b=rows[fid];assert (a['type'],a['flags'],a['parents'])==(b['type'],b['flags'],b['parents'])
  skip={b'HEDR'}if a['type']=='TES4'else {b'NAM0',b'NAM9'}if a['type']=='WRLD'else set()
  assert [(k,v)for k,v in a['ordered']if k not in skip]==[(k,v)for k,v in b['ordered']if k not in skip],a['name']
def seams():
 count=0
 for (x,y),h in HEIGHTS.items():
  for other,axis in [((x+1,y),0),((x,y+1),1)]:
   if other not in HEIGHTS:continue
   n=HEIGHTS[other];a=LANDS[x,y]['tags'][b'VNML'];b=LANDS[other]['tags'][b'VNML']
   for i in range(33):
    p,q=((i*33+32,i*33)if axis==0 else(32*33+i,i))
    assert (h[i][32]if axis==0 else h[32][i])==(n[i][0]if axis==0 else n[0][i])
    if {(x,y),other}!={(0,0),(0,-1)}:assert a[p*3:p*3+3]==b[q*3:q*3+3]
   count+=1
 assert count==17
def weights(row):
 result={};last=None
 for k,v in row['ordered']:
  if k==b'ATXT':last=struct.unpack('<IBBH',v);assert last[2]==0
  if k==b'VTXT':
   tex,q,_,layer=last;assert len(v)==2312
   for i in range(289):
    ix,pad,w=struct.unpack_from('<HHf',v,i*8);assert ix==i and pad==0 and math.isfinite(w)and 0<=w<=1
    key=(i%17+(q&1)*16,i//17+(q>>1)*16,tex)
    if key in result:assert abs(result[key]-w)<1e-7
    result[key]=w
 return result
def materials():
 shared={}
 for (cx,cy),r in LANDS.items():
  w=weights(r)
  for y in range(33):
   for x in range(33):
    vals={tex:v for (xx,yy,tex),v in w.items()if xx==x and yy==y};assert sum(vals.values())<=1.000001
    if x in(0,32)or y in(0,32):
     key=(cx*32+x,cy*32+y);vec=[vals.get(t,0)for t in(0x3343c,0x21336,0xc55fc)]
     # The frozen cores already disagree along y=0, including its two corners.
     # Preservation above independently binds every original byte. No new interior seam is exempt.
     if key in shared and not(key[1]==0 and 0<=key[0]<=32):assert all(abs(a-b)<1e-7 for a,b in zip(vec,shared[key]))
     shared[key]=vec
def footing(row):
 asset=next(k for k,v in MODELS.items()if int(v['id'],16)==form(row['tags'][b'NAME']));m=MODELS[asset]['nif'];p=pose(row);scale=struct.unpack('<f',row['tags'][b'XSCL'])[0]
 foot=[v*scale for v in m['bottomBandBounds']];render=box([v*scale for v in m['renderBounds']],p[:3],p[3:]);cx,cy=next(xy for xy,c in CELLS.items()if(6,c['id'])in row['parents'])
 assert (cx,cy)not in((0,0),(0,-1));assert render[0]>=cx*4096+128 and render[3]<=(cx+1)*4096-128 and render[1]>=cy*4096+128 and render[4]<=(cy+1)*4096-128
 c,s=math.cos(p[5]),math.sin(p[5]);lo=1e9;hi=-1e9
 for i in range(17):
  for j in range(17):
   x=foot[0]+(foot[3]-foot[0])*i/16;y=foot[1]+(foot[4]-foot[1])*j/16;hs=height(p[0]+x*c+y*s,p[1]+y*c-x*s);lo=min(lo,*hs);hi=max(hi,*hs)
 assert p[2]+foot[5]<=lo+.1,(row['name'],'airgap',p[2]+foot[5]-lo)
 assert hi-(p[2]+foot[5])<=(120 if asset=='RockPileL01'else 65),(row['name'],'embed',hi-(p[2]+foot[5]))
 return hi-lo
def horizon():
 report=[]
 for name,x,y,z in [('wreck',700,1050,-64),('encounter',1900,1900,112),('cabin',3260,2800,256),('landing',1800,-2260,224),('queen',2906,-1960,224)]:
  angles=[]
  for deg in range(0,360,5):
   dx,dy=math.cos(math.radians(deg)),math.sin(math.radians(deg));angle=-90
   for distance in range(128,17000,64):
    xx,yy=x+dx*distance,y+dy*distance
    if not(-4096<=xx<=8192 and -8192<=yy<=8192):break
    # Only appended landscape contributes, so the original steep bowl cannot inflate this screen.
    if 0<=xx<=4096 and -4096<=yy<=4096:continue
    angle=max(angle,math.degrees(math.atan2(min(height(xx,yy))-z,distance)))
   angles.append(angle)
  report.append(dict(view=name,minimumDegrees=min(angles),maximumDegrees=max(angles),rays=len(angles)))
 return report
PROPS=[r for r in NEW.values()if r['name'].startswith('TLM_RIDGE_')and r['type']=='REFR']
class Checks(unittest.TestCase):
 def test_original550(self):preservation(NEW)
 def test_cells_and_types(self):
  self.assertEqual(set(CELLS),{(x,y)for x in range(-1,2)for y in range(-2,2)})
  self.assertEqual(len(NEW)-len(OLD),20+len(PROPS));self.assertTrue(80<=len(PROPS)<=130)
  self.assertTrue(all(r['type']in('CELL','LAND','REFR')for fid,r in NEW.items()if fid not in OLD))
 def test_seams_normals(self):seams()
 def test_materials(self):materials()
 def test_outer_default(self):
  for (cx,cy),h in HEIGHTS.items():
   for y in range(33):
    for x in range(33):
     gx,gy=cx*32+x,cy*32+y
     if gx in(-32,-31,63,64)or gy in(-64,-63,63,64):self.assertEqual(h[y][x],0)
 def test_props(self):
  for r in PROPS:footing(r)
 def test_old_pose_mutant(self):
  rows=copy.deepcopy(NEW);r=next(r for fid,r in rows.items()if fid in OLD and r['type']=='ACHR');r['ordered'].append((b'DATA',b'broken'))
  with self.assertRaises(AssertionError):preservation(rows)
 def test_floating_mutant(self):
  r=copy.deepcopy(PROPS[0]);p=pose(r);p[2]+=200;r['tags'][b'DATA']=struct.pack('<6f',*p)
  with self.assertRaises(AssertionError):footing(r)
 def test_seam_height_mutant(self):
  old=HEIGHTS[-1,-2][4][32];HEIGHTS[-1,-2][4][32]+=8
  try:
   with self.assertRaises(AssertionError):seams()
  finally:HEIGHTS[-1,-2][4][32]=old
 def test_alpha_mutant(self):
  r=copy.deepcopy(LANDS[-1,-2]);i=next(i for i,(k,v)in enumerate(r['ordered'])if k==b'VTXT');b=bytearray(r['ordered'][i][1]);struct.pack_into('<f',b,4,1.5);r['ordered'][i]=(b'VTXT',bytes(b))
  with self.assertRaises(AssertionError):weights(r)
if __name__=='__main__':
 suite=unittest.defaultTestLoader.loadTestsFromTestCase(Checks);result=unittest.TextTestRunner(verbosity=2).run(suite)
 if not result.wasSuccessful():raise SystemExit(1)
 (ROOT/'decoded-grids.json').write_text(json.dumps({'scope':'Actual emitted VHGT decoded heights; grid coordinates in cells, vertex spacing128','cells':[{'grid':list(xy),'heights':h}for xy,h in sorted(HEIGHTS.items())]},indent=2)+'\n')
 report={'scope':'Independent decoded raw geometry screen; native residency/LOD/visibility/collision OPEN','inheritedSeam':'Original (0,-1)/(0,0) normals and material weights differ along y=0; preserved literally, including material discontinuity at two three-cell corner junctions. Heights continuous. No new interior seam exemption.','baselineSha256':hashlib.sha256(BASE.read_bytes()).hexdigest().upper(),'worldSha256':hashlib.sha256(CURRENT.read_bytes()).hexdigest().upper(),'oldRecords':len(OLD),'newRecords':len(NEW),'landCells':len(LANDS),'newProps':len(PROPS),'heightRange':[min(v for h in HEIGHTS.values()for row in h for v in row),max(v for h in HEIGHTS.values()for row in h for v in row)],'horizonTerrainOnly':horizon(),'methods':result.testsRun}
 (ROOT/'receipt.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
