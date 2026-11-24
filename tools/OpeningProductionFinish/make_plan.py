"""Small deliberate opening furniture/greenery plan on immutable BB6F."""
from pathlib import Path
import json,sys,math,struct
R=Path(__file__).resolve().parents[2];HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(R/'tools/SheriffWorld'));from raw import records,decode,ground,pose,box,form,overlap
BASE=R.parent/'opening-final-scene-composition-001/tools/OpeningFinalScene/build/composed-001/TLMWorldSlice.esp';rows,names=records(BASE)
cell=next(r for r in rows.values()if r['type']=='CELL'and r['tags'].get(b'XCLC',b'')[:8]==struct.pack('<ii',0,0));h=decode(next(r for r in rows.values()if r['type']=='LAND'and(6,cell['id'])in r['parents']))
models=json.loads((R/'tools/OpeningSceneDepth/models.json').read_text())['assets'];models.update(json.loads((HERE/'landscape-donors.json').read_text())['assets'])
models['defaultLightWarm01NS']={'id':'000560DC','type':'LIGH','radius':256,'rgb':[228,203,182],'model':None}
for a in models.values():a.setdefault('type','STAT')
oldplan=json.loads((R/'tools/OpeningSceneDepth/placements.json').read_text());routes=oldplan['routes'];refs=[r for r in rows.values()if r['type']=='REFR'and pose(r)[1]>=0 and (not r['flags']&0x800 or r['name'].startswith('TLM_WS_ST_'))]
ids={form(r['tags'][b'NAME'])for r in refs};native,_=records(Path('C:/Program Files (x86)/GOG Galaxy/Games/Fallout 4 GOTY/Data/Fallout4.esm'),ids);master,_=records(R.parent/'first-act-opening-voices-009/build/opening-voices-master-002/TheLastMeridian.esp',ids);bases={**native,**master};obstacles=[]
for r in refs:
 a=bases.get(form(r['tags'][b'NAME']))
 if not a or b'OBND'not in a['tags']or a['type']not in('STAT','FURN','CONT'):continue
 if any(s in a['name'].lower()for s in('tree','shrub','grass','xmarker')):continue
 p=pose(r);scale=struct.unpack('<f',r['tags'].get(b'XSCL',struct.pack('<f',1)))[0];bounds=box([v*scale for v in struct.unpack('<6h',a['tags'][b'OBND'])],p[:3],p[3:]);obstacles.append((r['name'],bounds))
actors=[pose(r)for r in rows.values()if r['type']=='ACHR'and pose(r)[1]>=0];controls=[pose(r)for r in rows.values()if r['type']=='REFR'and r['name'].startswith('TLM_WS_ST_')and pose(r)[1]>=0];qa=[(740,920),(3212,2474)]
def point_distance(x,y,b):return math.hypot(max(b[0]-x,0,x-b[3]),max(b[1]-y,0,y-b[4]))
def route_distance(x,y):
 best=1e9
 for route in routes:
  for (ax,ay),(bx,by)in zip(route,route[1:]):
   t=max(0,min(1,((x-ax)*(bx-ax)+(y-ay)*(by-ay))/((bx-ax)**2+(by-ay)**2)));best=min(best,math.hypot(x-ax-t*(bx-ax),y-ay-t*(by-ay)))
 return best
plan=[];omitted=[]
def put(role,asset,x,y,support=None,yaw=0,scale=1,parent=None,low=False):
 a=models[asset]
 if a['type']=='LIGH':plan.append(dict(id='TLM_FINISH_'+role,asset=asset,x=x,y=y,z=support,yaw=0,scale=1,kind='LIGH',support=None,parent=None));return
 rb=[v*scale for v in a['nif']['renderBounds']];fb=[v*scale for v in a['nif']['bottomBandBounds']];vegetation=asset.startswith(('Tree','Marsh'))
 lo=1e9;hi=-1e9;c,s=math.cos(yaw),math.sin(yaw)
 for i in range(17):
  for j in range(17):
   fx=fb[0]+(fb[3]-fb[0])*i/16;fy=fb[1]+(fb[4]-fb[1])*j/16
   for diagonal in(False,True):g=ground(h,x+fx*c+fy*s,y+fy*c-fx*s,diagonal);lo=min(lo,g);hi=max(hi,g)
 if support is None and hi-lo>32:omitted.append((role,'slope'));return
 z=support-fb[2]if support is not None else lo-fb[5]-3;b=box(rb,[x,y,z],[0,0,yaw]);radius=max(x-b[0],b[3]-x,y-b[1],b[4]-y)
 if min(b[0],b[1])<64 or max(b[3],b[4])>4032:omitted.append((role,'cell'));return
 if not low and route_distance(x,y)<96+radius:omitted.append((role,'route'));return
 if any(point_distance(p[0],p[1],b)<128 for p in actors+controls):omitted.append((role,'actor/control'));return
 if any(point_distance(xx,yy,b)<38 for xx,yy in qa):omitted.append((role,'QA'));return
 ignored={parent}if parent else set()
 collision=b
 if vegetation:
  collision=box([fb[0],fb[1],rb[2],fb[3],fb[4],rb[5]],[x,y,z],[0,0,yaw]) # trunk/root column; leaf canopy may overhang rocks
 if not low and any(overlap(collision,q)for name,q in obstacles if name not in ignored):omitted.append((role,'existing prop'));return
 if any(overlap(b,p['bounds'])for p in plan if 'bounds'in p and p['id']!=parent and not(vegetation and p.get('vegetation'))):omitted.append((role,'new prop'));return
 plan.append(dict(id='TLM_FINISH_'+role,asset=asset,x=x,y=y,z=z,yaw=yaw,scale=scale,kind=a['type'],support=support,parent=parent,lowFloorCover=low,vegetation=vegetation,groundRange=[lo,hi],bounds=b))
put('DeskChair','NpcChairHighTechOfficeChairDirtySit01',2840,2850,144,math.pi)
put('LivingRug','PlayerHouse_Ruin_Rug01',3070,3120,144,scale=1.6,low=True)
put('PantryShelf','WorkshopWallShelfWood02',3048,3180,220,-math.pi/2) # source pivot, not floor support
if plan and plan[-1]['id']=='TLM_FINISH_PantryShelf':
 # Shelf is wall-mounted: preserve the exact original NIF pivot height220.
 p=plan[-1];dz=220-p['z'];p['z']=220;p['bounds'][2]+=dz;p['bounds'][5]+=dz;p['support']=None;p['mount']='north inner wall Y3180';p['wallMount']=True
 put('PantryWaterA','WaterPurified',3020,3168,221,parent='TLM_FINISH_PantryShelf')
 put('PantryWaterB','WaterPurified',3040,3168,221,parent='TLM_FINISH_PantryShelf')
 put('PantryFood','FancyLadSnackCakes_PreWar',3080,3168,221,parent='TLM_FINISH_PantryShelf')
put('DeskCup','CoffeeCup01',2880,2794,200,parent='TLM_OPEN_CabinDesk')
put('DeskRation','FancyLadSnackCakes_PreWar',2788,2790,200,parent='TLM_OPEN_CabinDesk')
put('RestWater','WaterPurified',3295,2872,195.638794,parent='TLM_DEPTH_CabinDetail1')
put('WashPot','CookingPot01',2740,3140,210.1875,parent='TLM_DEPTH_CabinDetail2')
put('DeskWarmLight','defaultLightWarm01NS',2820,2780,246)
put('YardWorkCrate','WoodCrate01',2480,3320)
put('YardWaterBarrel','WoodBarrel01',3600,3380)
for i,(x,y,scale)in enumerate([(1420,800,.65),(1510,880,.55),(1580,740,.75),(580,2110,.70),(300,2200,.80),(3310,1690,.65),(3380,1810,.75),(3290,1880,.60),(1700,2600,.45),(1600,2470,.45),(1570,2700,.50)]):put('GreenSapling'+str(i),'TreeMaplePreWar05Gr',x,y,yaw=i*.57,scale=scale)
put('HollowCanopy','TreeMaplePreWar06Gr',420,2050,yaw=.6,scale=.65)
put('CutShoulderGreenA','TreeMaplePreWar05Gr',3160,1420,yaw=.4,scale=.70)
put('CutShoulderGreenB','TreeMaplePreWar05Gr',3070,1600,yaw=1.4,scale=.55)
assert any(p['id']=='TLM_FINISH_DeskChair'for p in plan),'desk chair must be usable-source placement'
used={p['asset']for p in plan};(HERE/'models.json').write_text(json.dumps({'scope':'Measured stock donor metadata; no mesh bytes','assets':{n:models[n]for n in used}},indent=2)+'\n')
(HERE/'placements.json').write_text(json.dumps({'scope':'Deliberate working/living/pantry/yard zones; existing furniture retained','placements':plan,'omitted':omitted,'routes':routes,'qaPads':qa},indent=2)+'\n');(HERE/'obstacles.json').write_text(json.dumps({'obstacles':obstacles,'actors':actors,'controls':controls},indent=2)+'\n')
print('actual',len(plan),'omitted',omitted);print([(p['id'],p['asset'],p['x'],p['y'])for p in plan])
