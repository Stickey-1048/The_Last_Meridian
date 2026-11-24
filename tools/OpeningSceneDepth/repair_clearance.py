"""Bounded three-pose repair; original8460 plan is immutable input."""
from pathlib import Path
import sys,json,math,struct,copy
R=Path(__file__).resolve().parents[2];HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(R/'tools/SheriffWorld'))
from raw import records,decode,ground,pose,box,overlap
ORIGINAL=R.parent/'opening-scene-depth-001/tools/OpeningSceneDepth/placements.json'
plan=json.loads(ORIGINAL.read_text());models=json.loads((HERE/'models.json').read_text())['assets'];obs=json.loads((HERE/'old-obstacles.json').read_text())
rows,names=records(R.parent/'mountain-final-world-composition-001/tools/MountainFinalWorld/build/composed-001/TLMWorldSlice.esp');cell=next(r for r in rows.values()if r['type']=='CELL'and r['tags'].get(b'XCLC',b'')[:8]==struct.pack('<ii',0,0));h=decode(next(r for r in rows.values()if r['type']=='LAND'and(6,cell['id'])in r['parents']))
targets={'TLM_DEPTH_Woodland4Sapling3','TLM_DEPTH_Woodland4Scrub4','TLM_DEPTH_ShoulderStone9'};deltas=[]
def distance(x,y,b):return math.hypot(max(b[0]-x,0,x-b[3]),max(b[1]-y,0,y-b[4]))
def route_distance(x,y):
 best=1e9
 for route in plan['routes']:
  for (ax,ay),(bx,by)in zip(route,route[1:]):
   t=max(0,min(1,((x-ax)*(bx-ax)+(y-ay)*(by-ay))/((bx-ax)**2+(by-ay)**2)));best=min(best,math.hypot(x-ax-t*(bx-ax),y-ay-t*(by-ay)))
 return best
for p in plan['placements']:
 if p['id']not in targets:continue
 old=copy.deepcopy(p);m=models[p['asset']]['nif'];scale=p['scale'];rb=[v*scale for v in m['renderBounds']];fb=[v*scale for v in m['bottomBandBounds']];best=None
 for dx in range(-160,161,20):
  for dy in range(-160,161,20):
   x,y=old['x']+dx,old['y']+dy;c,s=math.cos(p['yaw']),math.sin(p['yaw']);foot=fb if p['vegetation']else[rb[0],rb[1],fb[2],rb[3],rb[4],fb[5]];lo=1e9;hi=-1e9
   for i in range(17):
    for j in range(17):
     fx=foot[0]+(foot[3]-foot[0])*i/16;fy=foot[1]+(foot[4]-foot[1])*j/16
     for flip in(False,True):
      g=ground(h,x+fx*c+fy*s,y+fy*c-fx*s,flip);lo=min(lo,g);hi=max(hi,g)
   if hi-lo>36:continue
   z=lo-fb[5]-3;b=box(rb,[x,y,z],[0,0,p['yaw']]);radius=max(x-b[0],b[3]-x,y-b[1],b[4]-y)
   if min(b[0],b[1])<64 or max(b[3],b[4])>4032 or route_distance(x,y)<96+radius:continue
   if min(distance(q[0],q[1],b)for q in obs['actors']+obs['operative'])<128:continue
   if any(overlap(b,a)for _,a in obs['obstacles']):continue
   if any(overlap(b,a['bounds'])for a in plan['placements']if a['id']!=p['id']and not(p['vegetation']and a['vegetation'])):continue
   score=math.hypot(dx,dy)+(hi-lo)*.05
   if best is None or score<best[0]:best=(score,x,y,z,lo,hi,b)
 assert best is not None,p['id']
 _,p['x'],p['y'],p['z'],p['groundMin'],p['groundMax'],p['bounds']=best
 deltas.append({'id':p['id'],'oldXYZ':[old[k]for k in('x','y','z')],'newXYZ':[p[k]for k in('x','y','z')],'oldMinimumActorAABBDistance':min(distance(q[0],q[1],old['bounds'])for q in obs['actors']+obs['operative']),'newMinimumActorAABBDistance':min(distance(q[0],q[1],p['bounds'])for q in obs['actors']+obs['operative'])})
(HERE/'placements.json').write_text(json.dumps(plan,indent=2)+'\n');(HERE/'clearance-repair-deltas.json').write_text(json.dumps(deltas,indent=2)+'\n');print(json.dumps(deltas,indent=2))
