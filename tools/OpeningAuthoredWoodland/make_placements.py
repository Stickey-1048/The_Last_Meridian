"""Original finite placement plan from local emitted LAND; no native mesh/data export."""
from pathlib import Path
import sys,json,struct,math
R=Path(__file__).resolve().parents[2];HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(R/'tools/SheriffWorld'));from raw import records,pose,decode,ground,box,form
old,names=records(R.parent/'opening-mountain-structure-001/tools/OpeningMountainStructure/build/structure-001/TLMWorldSlice.esp')
new,_=records(HERE/'build/woodland-002/TLMWorldSlice.esp')
cells={struct.unpack_from('<ii',r['tags'][b'XCLC']):r for r in new.values()if r['type']=='CELL'and b'XCLC'in r['tags']}
grids={xy:decode(next(r for r in new.values()if r['type']=='LAND'and(6,c['id'])in r['parents']))for xy,c in cells.items()}
assets=json.loads((R/'tools/AppalachianRidges/models.json').read_text())['assets'];byid={int(a['id'],16):a for a in assets.values()}
def height(x,y,flip):
 cx,cy=math.floor(x/4096),math.floor(y/4096);return ground(grids[cx,cy],x-cx*4096,y-cy*4096,flip)
def support(a,x,y,yaw,scale):
 foot=[v*scale for v in a['nif']['bottomBandBounds']];b=box(foot,[x,y,0],[0,0,yaw]);values=[height(b[0]+(b[3]-b[0])*ix/16,b[1]+(b[4]-b[1])*iy/16,f)for iy in range(17)for ix in range(17)for f in(False,True)]
 return min(values)-foot[2]-4,max(values)-min(values)+4,b
poses=[]
for fid,r in old.items():
 if r['type']!='REFR' or not r['name'].startswith(('TLM_RIDGE_','TLM_STRUCTURE_')):continue
 p=pose(r);xy=math.floor(p[0]/4096),math.floor(p[1]/4096)
 if xy not in[(1,0),(0,1),(1,1)]:continue
 a=byid[form(r['tags'][b'NAME'])];scale=struct.unpack('<f',r['tags'].get(b'XSCL',struct.pack('<f',1)))[0];candidates=[]
 for dx,dy in[(0,0)]+[(dx,dy)for radius in(128,256,384,512)for dx,dy in[(radius,0),(-radius,0),(0,radius),(0,-radius),(radius,radius),(-radius,radius),(radius,-radius),(-radius,-radius)]]:
  x,y=p[0]+dx,p[1]+dy;z,embed,b=support(a,x,y,p[5],scale)
  if embed<=64 and all(xy[i]*4096+64<=b[i]and b[i+3]<=(xy[i]+1)*4096-64 for i in range(2)):
   candidates.append((dx*dx+dy*dy,embed,x,y,z));break
 if not candidates:raise ValueError(('No bounded support for passive',r['name']))
 _,embed,x,y,z=candidates[0];poses.append({'id':r['name'],'localId':fid&0xffffff,'base':form(r['tags'][b'NAME']),'oldXYZ':p[:3],'xyz':[x,y,z],'embed':embed,'kind':'passive-grounding'})
furniture={
 'TLM_OPEN_CabinDesk':(2790,2990),'TLM_OPEN_CabinLamp':(2790,2990),'TLM_OPEN_CabinLocker':(2720,3180),
}
for name,r in names.items():
 if r['type']!='REFR':continue
 p=pose(r);base=form(r['tags'][b'NAME'])
 # Exactly identified existing furniture; all narrative refs/actors remain fixed.
 if name in furniture:x,y=furniture[name]
 elif name=='TLM_WS_Bed':x,y=2780,3300
 elif name=='TLM_WS_Couch':x,y=3060,3280
 elif name=='TLM_FINISH_DeskChair':x,y=2790,3060
 elif name.startswith('TLM_FINISH_Pantry'):x,y=p[0],p[1]+240
 else:continue
 poses.append({'id':name,'localId':r['id']&0xffffff,'base':base,'oldXYZ':p[:3],'xyz':[x,y,p[2]+4],'kind':'cabin-furniture'})
# Native plank floors are slightly warped. Put each actual lowest rendered foot
# half a unit below the lowest sampled native floor, rather than floating it.
fitpath=HERE/'cabin-fit.json'
if fitpath.exists():
 models={}
 for path in[HERE/'landscape-donors.json',R/'tools/OpeningEnvironment/donors.json',R/'tools/OpeningProductionFinish/models.json']:
  for a in json.loads(path.read_text())['assets'].values():models[int(a['id'],16)]=a
 fit=json.loads(fitpath.read_text());byname={p['id']:p for p in poses}
 for f in fit['floorSupport']:
  p=byname[f['id']];p['xyz'][2]=f['floorRange'][0]-models[p['base']]['nif']['renderBounds'][2]-.5
 byname['TLM_OPEN_CabinLamp']['xyz'][2]=byname['TLM_OPEN_CabinDesk']['xyz'][2]+pose(names['TLM_OPEN_CabinLamp'])[2]-pose(names['TLM_OPEN_CabinDesk'])[2]
disabled=[{'id':r['name'],'localId':fid&0xffffff,'base':form(r['tags'][b'NAME'])}for fid,r in old.items()if r['type']=='REFR'and(r['name'].startswith(('TLM_WS_CabinFloor','TLM_WS_CabinRoof','TLM_WS_CabinBackWall','TLM_WS_CabinFrontWall','TLM_WS_CabinLeftWall','TLM_WS_CabinRightWall','TLM_OPEN_CabinFoundation')))]
plan={'scope':'Original explicit passive/furniture placement corrections; old prefab-panel IDs retained disabled','poses':poses,'disabled':disabled,'cabin':{'id':'TLM_WOODLAND_SheriffCabin','base':0x19dde8,'model':'Architecture\\Unique\\Cabins\\Cabin01NoFence.nif','xyz':[2944,3050,148],'yaw':-math.pi/2,'scale':1}}
(HERE/'placements.json').write_text(json.dumps(plan,indent=2)+'\n');print({'poses':len(poses),'passive':sum(p['kind']=='passive-grounding'for p in poses),'disabled':len(disabled),'maxEmbed':max(p.get('embed',0)for p in poses)})
