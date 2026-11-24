"""Selected known assets/actualF32 feet and lower trunk screens; numeric results only."""
from pathlib import Path
import sys,json,struct,math,copy,importlib.util
H=Path(__file__).resolve().parent;R=H.parents[1];sys.path.insert(0,str(R/'tools/SheriffWorld'));import raw,mesh
BASE=R.parent/'opening-hill-forest-finish-042/build/hill-forest-finish-world-003/TLMWorldSlice.esp';OLD,ON=raw.records(BASE);PLAN=json.loads((H/'plan.json').read_text());MODELS=json.loads((H/'models.json').read_text())['assets'];PROPOSED=copy.deepcopy(OLD)
for row in PLAN['moves']:PROPOSED[int(row['form'],16)]['tags'][b'DATA']=struct.pack('<6f',*row['proposedPose'])
sp=importlib.util.spec_from_file_location('heights',R/'tools/OpeningRidgeSpillFinish/make_plan.py');m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);m.NEW={g:raw.decode(OLD[i])for g,i in m.LANDS.items()}
sp=importlib.util.spec_from_file_location('clear',R/'tools/OpeningWreckTableau/make_plan.py');clear=importlib.util.module_from_spec(sp);sp.loader.exec_module(clear)
def worldbox(b,r):
 scale=struct.unpack('<f',r['tags'].get(b'XSCL',struct.pack('<f',1)))[0];p=raw.pose(r);return raw.box([v*scale for v in b],p[:3],p[3:])
def lowerband(row,records):
 r=records[int(row['form'],16)];s=row['scale'];lo=MODELS[row['asset']]['nif']['bottomBandBounds'][2];hi=lo+128/s;verts=[]
 for tri in mesh.fullsets[row['asset']]:
  poly=[list(v)for v in tri]
  for z,sign in[(lo,1),(hi,-1)]:
   clipped=[]
   for a,b in zip(poly,poly[1:]+poly[:1]):
    da,db=(a[2]-z)*sign,(b[2]-z)*sign
    if da>=0:clipped.append(a)
    if(da>=0)!=(db>=0):clipped.append([a[k]+(b[k]-a[k])*da/(da-db)for k in range(3)])
   poly=clipped
   if not poly:break
  verts.extend(poly)
 assert verts,('No actual lower-band render triangles',row['asset'])
 return worldbox([min(v[j]for v in verts)for j in range(3)]+[max(v[j]for v in verts)for j in range(3)],r)
def prove(records):
 feet=[];bands=[];rock=MODELS['RockBoulder03'];rocks=[r for r in records.values()if r['type']=='REFR'and raw.form(r['tags'][b'NAME'])==int(rock['id'],16)]
 for row in PLAN['moves']:
  r=records[int(row['form'],16)];model=MODELS[row['asset']];foot=worldbox(model['nif']['bottomBandBounds'],r);lo,hi,n=m.extent(foot);render=worldbox(model['nif']['renderBounds'],r);road=clear.routeclear(render);op=min(clear.pointbox(raw.pose(q)[:2],render)for q in list(records.values())if q['type']=='ACHR');op=min(op,min(clear.pointbox(raw.pose(records[i])[:2],render)for i in clear.CONTROLS))
  entry={'id':row['id'],'poseF32':raw.pose(r),'range':hi-lo,'maxEmbed':hi-foot[2],'footTopBelowLowGround':lo-foot[5],'bothDiagonalCriticalPoints':n,'footBox':foot,'renderBox':render,'routeGap':road,'operativeGap':op,'supportLimit':'Cedar lowest-band is a singlepoint proxy, NOT area support proof'if row['asset']=='TreeCedarShrub01'else'Finite existing bottom-band proxy; not Havok'};feet.append(entry)
  assert entry['range']<=56 and entry['maxEmbed']<=64 and entry['footTopBelowLowGround']>=2.99 and road>=96 and op>=128,entry
  if row['asset'].startswith('Tree'):
   b=lowerband(row,records);hits=[q['name']for q in rocks if raw.overlap(b,worldbox(rock['nif']['renderBounds'],q))];bands.append({'id':row['id'],'lower128WorldBox':b,'rockHits':hits});assert not hits,bands[-1]
 return {'footings':feet,'lower128BandRockChecks':bands,'scope':'FouractualF32poses/decodedbothdiagonal/knownlowertrunkbounds; canopies/understory overlap intentional, no native/Havok certificate'}
if __name__=='__main__':
 result=prove(PROPOSED)
 with(H/'preflight.json').open('x')as f:json.dump(result,f,indent=2);f.write('\n')
 print(json.dumps(result))
