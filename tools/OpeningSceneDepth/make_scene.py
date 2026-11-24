"""Original authored scene placement projection onto accepted, decoded LAND."""
from pathlib import Path
import sys,json,math,struct
R=Path(__file__).resolve().parents[2];HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(R/'tools/SheriffWorld'))
from raw import records,decode,ground,pose,box,form,overlap
BASE=R.parent/'mountain-final-world-composition-001/tools/MountainFinalWorld/build/composed-001/TLMWorldSlice.esp'
rows,names=records(BASE);land=next(r for r in rows.values()if r['type']=='LAND'and(6,names['TLM_WS_Cell']['id'])in r['parents']) if 'TLM_WS_Cell'in names else None
if land is None:
 cell=next(r for r in rows.values()if r['type']=='CELL'and r['tags'].get(b'XCLC',b'')[:8]==struct.pack('<ii',0,0));land=next(r for r in rows.values()if r['type']=='LAND'and(6,cell['id'])in r['parents'])
h=decode(land)
models={}
for p in [R/'tools/OpeningEnvironment/donors.json',R/'tools/AppalachianRidges/models.json',HERE/'landscape-donors.json']:models.update(json.loads(p.read_text())['assets'])
# Bind only selected existing stock assets; all mesh bytes remain owned/local.
selected=['TreeMaplePreWar03Gr','TreeMaplePreWar06Gr','TreeMaplePreWar05Gr','TreeCedarShrub01','Marshshrub01','DeadShrub04','RockBoulder03','TreeStumpGS01','TreeStumpSMarsh02','WoodCrate01','WoodCrate02','WoodBarrel01','MetalBarrelStatic01','Lantern01','DebrisWoodPileSm01','DebrisWoodPileRoad01Trash']
models={k:models[k]for k in selected}
(HERE/'models.json').write_text(json.dumps({'scope':'Exact selected native STAT/model numerical metadata; no mesh payload','assets':models},indent=2)+'\n')
routes=[[(448,640),(700,900),(1050,1133),(1900,1700),(2600,2200),(3048,2200),(3048,2432),(3048,2900)],[(1200,1200),(2200,1000),(2700,1700),(2600,2200)],[(2600,2200),(2260,2200),(1880,2480),(1880,2560)],[(2260,2200),(2260,3558),(3050,3558),(3050,3572)]]
def distance(x,y):
 result=1e9
 for route in routes:
  for (ax,ay),(bx,by)in zip(route,route[1:]):
   t=max(0,min(1,((x-ax)*(bx-ax)+(y-ay)*(by-ay))/((bx-ax)**2+(by-ay)**2)));result=min(result,math.hypot(x-ax-t*(bx-ax),y-ay-t*(by-ay)))
 return result
def point_box_distance(x,y,b):return math.hypot(max(b[0]-x,0,x-b[3]),max(b[1]-y,0,y-b[4]))
actor=[pose(r)for r in rows.values()if r['type']=='ACHR' and pose(r)[1]>=0]
operative=[pose(r)for r in rows.values()if r['type']=='REFR'and r['name'].startswith('TLM_WS_ST_')and pose(r)[1]>=0]
# Current exact baseline ref/base envelopes, state independent. Ignore vegetation
# canopy overlaps for woodland clusters; all hard props remain conservative.
refs=[r for r in rows.values()if r['type']=='REFR'and b'NAME'in r['tags']and pose(r)[1]>=0 and not r['flags']&0x800]
ids={form(r['tags'][b'NAME'])for r in refs}
native,_=records(Path('C:/Program Files (x86)/GOG Galaxy/Games/Fallout 4 GOTY/Data/Fallout4.esm'),ids)
master,_=records(R.parent/'roark-depth-current-001/build/roark-current-master-002/TheLastMeridian.esp',ids)
bases={**native,**master};obstacles=[]
for r in refs:
 a=bases.get(form(r['tags'][b'NAME']))
 if not a or b'OBND'not in a['tags']or b'DATA'not in r['tags']:continue
 if any(s in a['name'].lower()for s in ['tree','shrub','grass','stump','flower']):continue
 p=pose(r);scale=struct.unpack('<f',r['tags'].get(b'XSCL',struct.pack('<f',1)))[0];b=[v*scale for v in struct.unpack('<6h',a['tags'][b'OBND'])];obstacles.append((r['name'],box(b,p[:3],p[3:])))
placements=[];omitted=[]
def put(role,asset,x,y,scale=1,yaw=0,support=None,search=160):
 a=models[asset];m=a['nif'];rb=[v*scale for v in m['renderBounds']];fb=[v*scale for v in m['bottomBandBounds']]
 vegetation=asset.startswith(('Tree','Marsh','Dead'));flat=asset.startswith(('Debris','Wood','Metal','Lantern'))
 best=None
 for dx in [0,-40,40,-80,80,-160,160][:7 if search else 1]:
  for dy in [0,-40,40,-80,80,-160,160][:7 if search else 1]:
   xx,yy=x+dx,y+dy;bounds=box(rb,[xx,yy,0],[0,0,yaw]);radius=max(xx-bounds[0],bounds[3]-xx,yy-bounds[1],bounds[4]-yy)
   if min(bounds[0],bounds[1])<64 or max(bounds[3],bounds[4])>4032:continue
   if distance(xx,yy)<96+radius:continue
   if any(point_box_distance(p[0],p[1],bounds)<128 for p in actor+operative):continue
   lo=1e9;hi=-1e9;c,s=math.cos(yaw),math.sin(yaw)
   # Broad support for irregular rubble/rocks, trunk only for trees.
   foot=fb if vegetation else[rb[0],rb[1],fb[2],rb[3],rb[4],fb[5]]
   for i in range(9):
    for j in range(9):
     fx=foot[0]+(foot[3]-foot[0])*i/8;fy=foot[1]+(foot[4]-foot[1])*j/8
     for flip in(False,True):
      g=ground(h,xx+fx*c+fy*s,yy+fy*c-fx*s,flip);lo=min(lo,g);hi=max(hi,g)
   if support is None and hi-lo>(2 if flat else 36):continue
   zz=(support-fb[2])if support is not None else lo-fb[5]-(.3 if flat else 3)
   bounds=box(rb,[xx,yy,zz],[0,0,yaw])
   if any(overlap(bounds,b)for _,b in obstacles):continue
   if any(overlap(bounds,p['bounds'])for p in placements if not(vegetation and p['vegetation'])):continue
   score=math.hypot(dx,dy)+(hi-lo)*2
   if best is None or score<best[0]:best=(score,xx,yy,zz,lo,hi,bounds)
 if best is None:omitted.append(role);return
 _,xx,yy,zz,lo,hi,bounds=best
 placements.append(dict(id='TLM_DEPTH_'+role,asset=asset,x=xx,y=yy,z=zz,yaw=yaw,scale=scale,vegetation=vegetation,support=support,groundMin=lo,groundMax=hi,bounds=bounds))
# Unequal near-field groups, not an evenly spaced perimeter ring.
for group,(x,y)in enumerate([(480,2460),(1120,3050),(3430,1380),(3670,2920),(1360,2140)]):
 put(f'Woodland{group}Canopy','TreeMaplePreWar06Gr',x,y,.9,group*.7)
 for i,(dx,dy)in enumerate([(-140,-120),(130,100),(-80,240),(260,-60)]):put(f'Woodland{group}Sapling{i}','TreeMaplePreWar05Gr',x+dx,y+dy,.5+(i%3)*.15,i*.8)
 for i,(dx,dy)in enumerate([(-220,60),(80,-180),(230,180),(-180,280),(300,40)]):put(f'Woodland{group}Scrub{i}','TreeCedarShrub01'if i%2 else'Marshshrub01',x+dx,y+dy,.8+(i%2)*.25,i*.5)
 put(f'Woodland{group}Stone','RockBoulder03',x+180,y+280,1.1,group*.6)
for i,(x,y)in enumerate([(300,780),(250,1100),(1050,2040),(1260,1920),(1480,2280),(1540,2440),(3130,1450),(3480,1840),(3640,2150),(3600,2380),(1260,3300),(1300,3600)]):
 put('ShoulderStone'+str(i),'RockBoulder03',x,y,.8+(i%3)*.25,i*.63)
for i,(x,y)in enumerate([(360,560),(300,1340),(1280,1800),(1460,2440),(1120,2840),(3620,1980)]):put('Stump'+str(i),'TreeStumpSMarsh02'if i%2 else'TreeStumpGS01',x,y,.8,i*.8)
# Wreck salvage and roadside wear are outside the dispatch/body approach.
for i,(asset,x,y,yaw)in enumerate([('WoodCrate01',350,1960,.2),('WoodCrate02',400,2010,.6),('MetalBarrelStatic01',270,2060,0),('DebrisWoodPileSm01',650,1950,.3),('WoodCrate01',1160,1940,1),('DebrisWoodPileRoad01Trash',1320,1550,.6),('DebrisWoodPileSm01',270,650,.5),('WoodBarrel01',2490,2850,0),('WoodCrate02',2470,2940,.2),('WoodCrate01',3510,3250,.3),('WoodBarrel01',3570,3320,0)]):put('Salvage'+str(i),asset,x,y,1,yaw)
# Modest cabin/rest detail. Solid floor144, avoid center entrance and old bed/couch.
for i,(asset,x,y,support)in enumerate([('WoodCrate02',3250,2780,144),('WoodCrate01',3310,2860,144),('WoodBarrel01',2740,3140,144)]):put('CabinDetail'+str(i),asset,x,y,1,0,support,0)
if any(p['id']=='TLM_DEPTH_CabinDetail1'for p in placements):put('CabinLantern','Lantern01',3310,2860,1,0,195.65625,0)
for i,(x,y)in enumerate([(450,1100),(300,650),(1150,1950)]):put('WreckSplinters'+str(i),'DebrisWoodPileSm01',x,y,.45,i*.7)
(HERE/'placements.json').write_text(json.dumps({'scope':'Original passive opening detail; explicit omitted unsafe sites','baseline':str(BASE),'routeRadius':96,'actorAndOperativeRadius':128,'routes':routes,'placements':placements,'omitted':omitted},indent=2)+'\n')
(HERE/'old-obstacles.json').write_text(json.dumps({'scope':'Actual baseline state-independent enabled hard-prop OBND screen; native Havok OPEN','obstacles':obstacles,'actors':actor,'operative':operative},indent=2)+'\n')
print('placements',len(placements),'omitted',omitted)
