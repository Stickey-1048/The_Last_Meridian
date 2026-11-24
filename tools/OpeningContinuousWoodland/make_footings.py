"""Finite same-ID passive grounding from actual local emitted terrain, no assets."""
from pathlib import Path
import sys,struct,json,math
R=Path(__file__).resolve().parents[2];HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(R/'tools/SheriffWorld'));from raw import records,pose,decode,ground,box,form
BASE=R.parent/'opening-authored-woodland-001/tools/OpeningAuthoredWoodland/build/woodland-005/TLMWorldSlice.esp'
OLD,NAMES=records(BASE);NEW,_=records(HERE/'build/continuous-004/TLMWorldSlice.esp')
cells={struct.unpack_from('<ii',r['tags'][b'XCLC']):r for r in NEW.values()if r['type']=='CELL'and b'XCLC'in r['tags']};lands={xy:next(r for r in NEW.values()if r['type']=='LAND'and(6,c['id'])in r['parents'])for xy,c in cells.items()};nh={xy:decode(r)for xy,r in lands.items()};oh={xy:decode(OLD[r['id']])for xy,r in lands.items()}
models={};paths=['tools/AppalachianRidges/models.json','tools/OpeningEnvironment/donors.json','tools/OpeningSceneDepth/models.json','tools/OpeningProductionFinish/models.json']
for path in paths:
 for name,a in json.loads((R/path).read_text())['assets'].items():
  if 'bottomBandBounds'in a.get('nif',{}):models[int(a['id'],16)]=a
def height(h,x,y,f):cx,cy=math.floor(x/4096),math.floor(y/4096);return ground(h[cx,cy],x-cx*4096,y-cy*4096,f)
def samples(h,b):return[height(h,b[0]+(b[3]-b[0])*i/16,b[1]+(b[4]-b[1])*j/16,f)for i in range(17)for j in range(17)for f in(False,True)]
sites=[pose(r)[:2]for r in OLD.values()if r['type']in('ACHR','REFR')and r['name'].startswith('TLM_WS_ST_')and 0<=pose(r)[0]<4096 and 0<=pose(r)[1]<4096]
routes=[[(448,640),(700,900),(1050,1133),(1900,1700),(2600,2200),(3048,2200),(3048,2432)],[(1200,1200),(2200,1000),(2700,1700),(2600,2200)],[(2600,2200),(2260,2200),(1880,2480),(1880,2560)],[(2260,2200),(2260,3558),(3050,3558),(3050,3572)]]
def clear_move(a,x,y,rot,scale):
 b=box([v*scale for v in a['nif']['renderBounds']],[x,y,0],rot)
 def point(q):return math.hypot(max(b[0]-q[0],q[0]-b[3],0),max(b[1]-q[1],q[1]-b[4],0))
 if any(point(q)<128 for q in sites):return False
 for route in routes:
  for aa,bb in zip(route,route[1:]):
   low,high=0,1
   for i in range(2):
    d=bb[i]-aa[i]
    if abs(d)<1e-10:
     if aa[i]<b[i]or aa[i]>b[i+3]:low,high=1,0;break
    else:
     lo,hi=sorted([(b[i]-aa[i])/d,(b[i+3]-aa[i])/d]);low=max(low,lo);high=min(high,hi)
   if low<=high:return False
   distances=[point(aa),point(bb)]
   for xx in(b[0],b[3]):
    for yy in(b[1],b[4]):
     dx,dy=bb[0]-aa[0],bb[1]-aa[1];t=max(0,min(1,((xx-aa[0])*dx+(yy-aa[1])*dy)/(dx*dx+dy*dy)));distances.append(math.hypot(xx-aa[0]-t*dx,yy-aa[1]-t*dy))
   if min(distances)<96:return False
 return True
poses=[]
for fid,r in OLD.items():
 if r['type']!='REFR'or r['flags']&0x800:continue
 p=pose(r);xy=math.floor(p[0]/4096),math.floor(p[1]/4096)
 if xy not in[(0,0),(1,0),(0,1),(1,1)]:continue
 base=form(r['tags'][b'NAME']);a=models.get(base)
 if not a:
  assert abs(height(nh,p[0],p[1],False)-height(oh,p[0],p[1],False))<.001,('Unmeasured affected reference',r['name']);continue
 scale=struct.unpack('<f',r['tags'].get(b'XSCL',struct.pack('<f',1)))[0];foot=[v*scale for v in a['nif']['bottomBandBounds']];b=box(foot,p[:3],p[3:]);prior=samples(oh,b);actual=samples(nh,b)
 if max(abs(x-y)for x,y in zip(prior,actual))<.001:continue
 assert a.get('passive',True) and r['name'].startswith(('TLM_RIDGE_','TLM_STRUCTURE_','TLM_WS_','TLM_OPEN_','TLM_DEPTH_','TLM_FINISH_'))
 # Preserve XY unless actual measured feet cannot be supported on new terrain.
 chosen=None
 for dx,dy in[(0,0)]+[(dx,dy)for radius in(128,256,384,512)for dx,dy in[(radius,0),(-radius,0),(0,radius),(0,-radius),(radius,radius),(-radius,radius),(radius,-radius),(-radius,-radius)]]:
  x,y=p[0]+dx,p[1]+dy
  if(math.floor(x/4096),math.floor(y/4096))!=xy:continue
  if(dx or dy)and not clear_move(a,x,y,p[3:],scale):continue
  bb=box(foot,[x,y,0],p[3:]);vals=samples(nh,bb);embed=max(vals)-min(vals)+4
  if embed<=(40 if xy==(0,0)else 64):chosen=(x,y,min(vals)-foot[2]-4,embed);break
 if chosen is None:raise ValueError(('No finite measured footing',r['name']))
 x,y,z,embed=chosen;poses.append({'id':r['name'],'localId':fid&0xffffff,'base':base,'oldXYZ':p[:3],'xyz':[x,y,z],'embed':embed})
(HERE/'footings.json').write_text(json.dumps({'scope':'Only existing passive refs affected by four-LAND correction','poses':poses,'modelInputs':paths},indent=2)+'\n');print({'changedPassivePoses':len(poses),'changedXY':sum(p['oldXYZ'][:2]!=p['xyz'][:2]for p in poses),'maxEmbed':max(p['embed']for p in poses)})
