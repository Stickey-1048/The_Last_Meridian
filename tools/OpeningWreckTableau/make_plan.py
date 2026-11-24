"""Finite selected-stock wreck spill. Existing LAND decoded; numeric metadata only."""
from pathlib import Path
import sys,json,math,hashlib
H=Path(__file__).resolve().parent;R=H.parents[1];sys.path.insert(0,str(R/'tools/SheriffWorld'))
from raw import records,decode,ground,box,pose
BASE=R.parent/'gantt-opening-batch-voice-world-024/build/gantt-batch-voice-world-001/TLMWorldSlice.esp';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest().upper()
assert sha(BASE)=='B504DC2DF636F282FDC7DB605605A51BA74493C25B19076E7295362C1290792F'
ALL=json.loads((R/'tools/OpeningSceneDepth/models.json').read_text())['assets'];MODELS={k:ALL[k]for k in['WoodCrate01','WoodCrate02','WoodBarrel01','DebrisWoodPileSm01']}
ROWS,NAMES=records(BASE);HEIGHTS=decode(ROWS[0x2000803])
ROAD=[(448,640),(700,900),(1050,1133),(1900,1700),(2600,2200),(3048,2200),(3048,2432)]
BYPASS=[(1200,1200),(2200,1000),(2700,1700),(2600,2200)]
CONTROLS=[0x2000804,*range(0x20008fe,0x2000905),0x2000918]

def extents(h,b):
 # Exact extrema over BOTH piecewise-linear diagonal choices on enclosing full-render XY box.
 pts={(b[0],b[1]),(b[0],b[4]),(b[3],b[1]),(b[3],b[4])}
 for gx in range(int(b[0]//128),int(b[3]//128)+1):
  for gy in range(int(b[1]//128),int(b[4]//128)+1):
   x0,x1=max(b[0],gx*128),min(b[3],(gx+1)*128);y0,y1=max(b[1],gy*128),min(b[4],(gy+1)*128)
   if x1<x0 or y1<y0:continue
   pts.update([(x0,y0),(x1,y0),(x0,y1),(x1,y1)])
   for x in[x0,x1]:
    for y in[gy*128+x-gx*128,gy*128+128-x+gx*128]:
     if y0<=y<=y1:pts.add((x,y))
   for y in[y0,y1]:
    for x in[gx*128+y-gy*128,gx*128+128-y+gy*128]:
     if x0<=x<=x1:pts.add((x,y))
 values=[ground(h,x,y,f)for x,y in pts for f in[False,True]]
 return min(values),max(values),len(pts)

def pointbox(p,b):return math.hypot(max(b[0]-p[0],p[0]-b[3],0),max(b[1]-p[1],p[1]-b[4],0))
def pointseg(p,a,b):
 dx,dy=b[0]-a[0],b[1]-a[1];t=max(0,min(1,((p[0]-a[0])*dx+(p[1]-a[1])*dy)/(dx*dx+dy*dy)));return math.hypot(p[0]-a[0]-dx*t,p[1]-a[1]-dy*t)
def segmentbox(a,b,bb):
 lo,hi=0.,1.
 for i in range(2):
  d=b[i]-a[i]
  if abs(d)<1e-12:
   if not bb[i]<=a[i]<=bb[i+3]:break
  else:
   t0,t1=sorted(((bb[i]-a[i])/d,(bb[i+3]-a[i])/d));lo=max(lo,t0);hi=min(hi,t1)
   if lo>hi:break
 else:return 0.
 corners=[(x,y)for x in[bb[0],bb[3]]for y in[bb[1],bb[4]]]
 return min(pointbox(a,bb),pointbox(b,bb),*(pointseg(p,a,b)for p in corners))
def routeclear(b):return min(segmentbox(a,z,b)for route in[ROAD,BYPASS]for a,z in zip(route,route[1:]))
CANDIDATES=[('LeftTallCrate','WoodCrate01',560,1550,.15),('LeftLowCrate','WoodCrate02',650,1570,-.2),('LeftBarrel','WoodBarrel01',745,1550,.1),('ForegroundBrokenTimbers','DebrisWoodPileSm01',390,1050,.1),('RightTallCrate','WoodCrate01',1390,1560,.4),('RightLowCrate','WoodCrate02',1470,1620,-.15),('EndBrokenTimbers','DebrisWoodPileSm01',1430,1780,.04)]
def make():
 out=[]
 for name,key,x,y,yaw in CANDIDATES:
  asset=MODELS[key];rb=asset['nif']['renderBounds'];bounds=box(rb,[x,y,0],[0,0,yaw]);lo,hi,count=extents(HEIGHTS,bounds);embed=.5;z=lo-rb[2]-embed;actual=box(rb,[x,y,z],[0,0,yaw]);operative=min((pointbox(pose(ROWS[i])[:2],actual),ROWS[i]['name'])for i in CONTROLS);route=routeclear(actual)
  limit=3 if key.startswith('Debris')else 10
  assert hi-lo+embed<=limit,(name,'footing',hi-lo+embed)
  assert operative[0]>=128 and route>=96,(name,'clearance',operative,route)
  out.append({'id':'TLM_WRECK_'+name,'asset':key,'donorId':asset['id'],'model':asset['model'],'xyz':[x,y,z],'yaw':yaw,'scale':1,'renderBounds':actual,'footing':{'groundMin':lo,'groundMax':hi,'criticalPoints':count,'baseEmbed':embed,'maximumBasePlaneEmbed':hi-lo+embed,'limit':limit,'surface':'actual decoded coreLAND803; both triangle orientations over full-render enclosingXY'},'clearance':{'minimumOperative':operative[0],'nearestOperative':operative[1],'minimumRoad':route}})
 return {'baselineSha256':sha(BASE),'scope':'Seven passive cargo/timber refs only; no smoke, terrain, actor, quest, voice or oldref changes','placements':out,'models':MODELS,'limits':'Full-render and base-plane contact proxies; native Havok/access/visual judgment pending. Debris may contact existing wreck rubble/hull edge intentionally, not certified collision mesh union.'}
if __name__=='__main__':
 p=make()
 for n,data in[('placements.json',{k:v for k,v in p.items()if k!='models'}),('models.json',{'scope':'Carried selected accepted numericmetadata only; no mesh bytes','assets':p['models']})]:
  with(H/n).open('x')as f:json.dump(data,f,indent=2)
 print(json.dumps({'placements':len(p['placements']),'minRoute':min(x['clearance']['minimumRoad']for x in p['placements']),'minOperative':min(x['clearance']['minimumOperative']for x in p['placements']),'maximumEmbed':max(x['footing']['maximumBasePlaneEmbed']for x in p['placements'])},indent=2))

