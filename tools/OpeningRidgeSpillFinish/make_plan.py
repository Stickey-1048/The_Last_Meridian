"""Exact approved finite art033 plan, generated from immutable editorial geometry. No plugin writes."""
from pathlib import Path
import sys,math,json,struct,hashlib
H=Path(__file__).resolve().parent;R=H.parents[1];sys.path.insert(0,str(R/'tools/SheriffWorld'))
from raw import records,decode,ground,pose,box
BASE=R.parent/'opening-editorial-032/build/editorial-world-001/TLMWorldSlice.esp';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest().upper();assert sha(BASE)=='810272D866D51B697CB369FA362BF22222EA74AA14F3652285EC454AE0EAE05D'
ROWS,NAMES=records(BASE);GRIDS={fid:struct.unpack('<ii',q['tags'][b'XCLC'][:8])for fid,q in ROWS.items()if q['type']=='CELL'and b'XCLC'in q['tags']};LANDS={};OLD={}
for fid,q in ROWS.items():
 if q['type']=='LAND':
  grid=GRIDS[next(label for kind,label in q['parents']if kind==6)];LANDS[grid]=fid;OLD[grid]=decode(q)
def smooth(a,b,x):
 t=max(0,min(1,(x-a)/(b-a)));return t*t*(3-2*t)
def lift(x,y):
 # One extra unchanged derivative row makes the two outer normal rows truly unchanged.
 return 768*smooth(4352,5888,x)*(1-smooth(6784,7936,x))*smooth(2560,4608,y)*(1-smooth(6144,7936,y))
NEW={g:[[v+round(lift(g[0]*4096+x*128,g[1]*4096+y*128)/8)*8 if g in[(1,0),(1,1)]else v for x,v in enumerate(row)]for y,row in enumerate(h)]for g,h in OLD.items()}
def height(x,y,new=True,flip=False):
 field=NEW if new else OLD;g=(int(x//4096),int(y//4096));return ground(field[g],x-g[0]*4096,y-g[1]*4096,flip)
def extent(b,new=True):
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
 v=[height(x,y,new,f)for x,y in pts for f in[False,True]];return min(v),max(v),len(pts)
MODELS={}
for file in['tools/AppalachianRidges/models.json','tools/OpeningMountainStructure/models.json','tools/OpeningSceneDepth/models.json','tools/OpeningEnvironment/donors.json']:
 data=json.loads((R/file).read_text())['assets']
 for key,v in data.items():
  if 'nif'in v and v['nif'].get('bottomBandBounds'):MODELS[int(v['id'],16)]=(key,v)
def make():
 expected=json.loads((R.parents[1]/'work/reviews/nora-opening-visual-proposal-033-measurements.json').read_text())['affectedPassiveCandidates'];footings=[];selected={}
 for item in expected:
  fid=int(item['form'],16);r=ROWS[fid];p=pose(r);base=struct.unpack('<I',r['tags'][b'NAME'])[0];key,a=MODELS[base];scale=struct.unpack('<f',r['tags'].get(b'XSCL',struct.pack('<f',1)))[0];foot=[v*scale for v in a['nif']['bottomBandBounds']];b=box(foot,p[:3],p[3:]);lo,hi,n=extent(b);limit=110 if key=='RockPileL01'else 56
  assert hi-lo<=limit,(r['name'],'SUPPORTFAIL',hi-lo,limit)
  z=lo-foot[5]-3;assert hi-(z+foot[2])<=64,(r['name'],'CURRENT64EMBEDFAIL',hi-(z+foot[2]));footings.append({'id':r['name'],'localId':fid&0xffffff,'base':base,'oldPose':p,'pose':p[:2]+[z]+p[3:],'asset':key,'scale':scale,'groundMin':lo,'groundMax':hi,'supportRangeLimit':limit,'maximumEmbed':hi-(z+foot[2]),'criticalPoints':n});selected[key]=a
 cargo=json.loads((R.parents[1]/'work/reviews/nora-opening-visual-proposal-033-cargo.json').read_text())['moves'];moves=[]
 for item in cargo:
  r=NAMES[item['id']];base=struct.unpack('<I',r['tags'][b'NAME'])[0];key,a=MODELS[base];selected[key]=a;moves.append({'id':r['name'],'localId':r['id']&0xffffff,'base':base,'oldPose':pose(r),'pose':item['pose'],'asset':key})
 return {'scope':'No newforms/refs/assets/locations.3cargoDATA/4postflags/2backdropLAND+normals/30passiveZ/corepathpaint;4editorialDESCpreserved','baselineSha256':sha(BASE),'cargo':moves,'posts':[0x808,0x809,0x996,0x997],'footings':footings,'models':selected,'heightLiftMaximum':768,'derivativeGuard':'last3heightrowszeroDelta preservelast2height+normalrows; featherends7936vsproposal8064 onlyfornumericalderivativeguard','limits':'Currentown geometry only; nativevisual/Havok/foliageLOD pending; existingfootinglimits not relaxed'}
if __name__=='__main__':
 p=make()
 for name,data in[('plan.json',{k:v for k,v in p.items()if k!='models'}),('models.json',{'assets':p['models']})]:
  with(H/name).open('x')as f:json.dump(data,f,indent=2)
 print(json.dumps({'cargo':len(p['cargo']),'posts':len(p['posts']),'footings':len(p['footings']),'maxRange':max(f['groundMax']-f['groundMin']for f in p['footings'])},indent=2))
