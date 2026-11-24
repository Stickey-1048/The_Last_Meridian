"""Independent emitted-VHGT/normal/footprint screen; no native certificate."""
from pathlib import Path
import struct,zlib,json,math,hashlib
ROOT=Path(__file__).resolve().parent
OUT=ROOT/'build/landscape-005'
def subs(b):
 p=0;over=None
 while p<len(b):
  k,n=struct.unpack_from('<4sH',b,p);p+=6
  if k==b'XXXX':over=struct.unpack_from('<I',b,p)[0];p+=n;continue
  if over is not None:n,over=over,None
  yield k,b[p:p+n];p+=n
 assert p==len(b)

def records(path,wanted=None):
 rows={};names={}
 with path.open('rb')as f:
  def walk(end,parents):
   while f.tell()<end:
    at=f.tell();h=f.read(24);assert len(h)==24;k,n,flags,fid=struct.unpack_from('<4sIII',h)
    if k==b'GRUP':
     label,kind=struct.unpack_from('<Ii',h,8);walk(at+n,parents+[(kind,label)]);continue
    if wanted is not None and fid not in wanted:f.seek(n,1);continue
    b=f.read(n);b=zlib.decompress(b[4:])if flags&0x40000 else b;ss=list(subs(b));s=dict(ss);name=s.get(b'EDID',b'').rstrip(b'\0').decode();row={'type':k.decode(),'flags':flags,'id':fid,'name':name,'parents':parents,'tags':s,'ordered':ss};rows[fid]=row
    if name:names[name]=row
  walk(path.stat().st_size,[])
 return rows,names

def form(b):return struct.unpack('<I',b)[0]

def pose(r):return list(struct.unpack('<6f',r['tags'][b'DATA']))

def box(b,p,rot):
 # Intrinsic yaw only for current passive objects; no imported helper.
 assert abs(rot[0])+abs(rot[1])<.00001
 c,s=math.cos(rot[2]),math.sin(rot[2]);v=[(p[0]+x*c+y*s,p[1]+y*c-x*s,p[2]+z)for x in(b[0],b[3])for y in(b[1],b[4])for z in(b[2],b[5])];return [min(q[i]for q in v)for i in range(3)]+[max(q[i]for q in v)for i in range(3)]

def overlap(a,b):return all(min(a[i+3],b[i+3])-max(a[i],b[i])>.01 for i in range(3))
def decode(land):
 b=land['tags'][b'VHGT'];h=[];prev=struct.unpack_from('<f',b)[0]*8
 for y in range(33):
  row=[];value=prev
  for x in range(33):value+=struct.unpack_from('<b',b,4+y*33+x)[0]*8;row.append(value)
  h.append(row);prev=row[0]
 return h
def ground(h,x,y,flip=False):
 ix=min(31,max(0,int(x//128)));iy=min(31,max(0,int(y//128)));u=(x-ix*128)/128;v=(y-iy*128)/128;a,b,c,d=h[iy][ix],h[iy][ix+1],h[iy+1][ix],h[iy+1][ix+1]
 if flip:return a+(b-a)*u+(c-a)*v if u+v<=1 else d+(c-d)*(1-u)+(b-d)*(1-v)
 return a+(b-a)*u+(d-b)*v if v<=u else a+(d-c)*u+(c-a)*v
MAIN=[(448,640),(700,900),(1900,1700),(2600,2200),(3048,2200),(3048,2432)]
BYPASS=[(1200,1200),(2200,1000),(2700,1700),(2600,2200)]
def verify(rows):
 names={r['name']:r for r in rows.values()if r['name']};land=next(r for r in rows.values()if r['type']=='LAND');h=decode(land);assert len(h)==33 and all(len(r)==33 for r in h)
 assert all(h[0][i]==h[32][i]==h[i][0]==h[i][32]==0 for i in range(33)),'C0 cell boundary differs from default0'
 normals=land['tags'][b'VNML'];assert len(normals)==3267
 maxNormalError=0
 for y in range(33):
  for x in range(33):
   dx=(h[y][min(x+1,32)]-h[y][max(0,x-1)])/(128 if x in(0,32)else 256);dy=(h[min(y+1,32)][x]-h[max(0,y-1)][x])/(128 if y in(0,32)else 256);length=math.sqrt(1+dx*dx+dy*dy);expected=[round(-dx/length*127),round(-dy/length*127),round(127/length)];actual=struct.unpack_from('<3b',normals,(y*33+x)*3);maxNormalError=max(maxNormalError,max(abs(a-b)for a,b in zip(expected,actual)))
 assert maxNormalError<=1,'Decoded normals disagree with heights'
 routeProof=[]
 for route in [MAIN,BYPASS]:
  along=cross=error=0
  for a,b in zip(route,route[1:]):
   dx,dy=b[0]-a[0],b[1]-a[1];length=math.hypot(dx,dy);steps=math.ceil(length/16);previous=[None,None]
   for i in range(steps+1):
    x=a[0]+dx*i/steps;y=a[1]+dy*i/steps
    for flip in [False,True]:
     left=ground(h,x-dy/length*96,y+dx/length*96,flip);right=ground(h,x+dy/length*96,y-dx/length*96,flip);cross=max(cross,abs(right-left)/192);z=ground(h,x,y,flip)
     if previous[flip]is not None:along=max(along,abs(z-previous[flip])/(length/steps))
     previous[flip]=z
    error=max(error,abs(ground(h,x,y)-ground(h,x,y,True)))
  routeProof.append({'maxAlongGrade':along,'maxCrossGrade192':cross,'maxDiagonalDifference':error})
 assert all(p['maxAlongGrade']<=.35 and p['maxCrossGrade192']<=.25 for p in routeProof),'Route grade exceeds bounded walkability screen'
 # Full original floor tile footprints, not merely center pivots.
 floors=[]
 for r in rows.values():
  if r['type']!='REFR'or not r['name'].startswith(('TLM_WS_CabinFloor','TLM_WS_EX_FreightFloor','TLM_WS_EX_SupplyFloor')):continue
  x,y,z,*_=pose(r);samples=[]
  for dx in range(-128,129,16):
   for dy in range(-128,129,16):samples.extend([ground(h,x+dx,y+dy),ground(h,x+dx,y+dy,True)])
  assert min(samples)==max(samples)==128,'Foundation footprint is not one flat bench';assert z==144,'Original floor deck not ground+16';floors.append(r['name'])
 assert len(floors)==10,'Missing original cabin/annex floor'
 assert ground(h,700,1050)==-192 and ground(h,448,640)==-192,'Wreck hollow not physical'
 assert ground(h,3048,2800)==128,'Cabin bench height differs'
 extra=[r for r in rows.values()if r['name'].startswith('TLM_OPEN_')];assert len(extra)==49,'New scene prop membership'
 # Actual new prop footprints against independently decoded BOTH surfaces.
 models=json.loads((ROOT/'donors.json').read_text())['assets'];scene=json.loads((OUT/'opening-environment.json').read_text());supportProof=[]
 for p in scene['newProps']:
  r=names[p['id']];at=pose(r);a=models[p['asset']];assert form(r['tags'][b'NAME'])==int(a['id'],16),'New donor differs';assert max(abs(x-y)for x,y in zip(at,[p['x'],p['y'],p['z'],0,0,p['yaw']]))<.0001,'New actual prop pose differs'
  scale=p.get('scale',1);assert abs(struct.unpack('<f',r['tags'].get(b'XSCL',struct.pack('<f',1)))[0]-scale)<.00001,'Scale differs';b=[v*scale for v in a['nif']['bottomBandBounds']];bounds=box(b,at[:3],at[3:]);values=[]
  nx=max(1,math.ceil((bounds[3]-bounds[0])/16));ny=max(1,math.ceil((bounds[4]-bounds[1])/16))
  for ix in range(nx+1):
   for iy in range(ny+1):
    x=bounds[0]+(bounds[3]-bounds[0])*ix/nx;y=bounds[1]+(bounds[4]-bounds[1])*iy/ny;values.extend([ground(h,x,y),ground(h,x,y,True)])
  if p['asset']=='workshop_ShackMidFloor01Foundation':assert bounds[2]<min(values)and at[2]>=max(values)and at[2]==142,'Cabin foundation does not support deck'
  elif p['support']is not None:assert abs(bounds[2]-p['support'])<.001,'Furniture support bottom differs'
  else:assert bounds[2]<=min(values)+1 and max(values)-bounds[2]<=65,'New scene prop floats or overembeds beyond declared bound'
  supportProof.append({'id':p['id'],'actualBottom':bounds[2],'decodedGroundRange':[min(values),max(values)]})
 # Exact successor boundary against accepted native-tested009.
 oldRows,_=records(ROOT.parents[2]/'opening-environment-001/tools/OpeningEnvironment/build/world-009/TLMWorldSlice.esp')
 oldRefCount=0
 oldWorld=next(r for r in oldRows.values()if r['type']=='WRLD');assert rows[oldWorld['id']]['tags'][b'DATA']==bytes([oldWorld['tags'][b'DATA'][0]&~0x80]),'World NoGrass delta'
 for fid,r in oldRows.items():
  n=rows[fid];assert r['parents']==n['parents'],'Parent changed'
  if r['type']in('REFR','ACHR'):
   oldRefCount+=1;assert (r['name'].startswith('TLM_OPEN_')or pose(r)[:2]==pose(n)[:2]) and pose(r)[3:]==pose(n)[3:],'Original ref XY/orientation changed'
   flags=r['flags']|0x800 if r['name'].startswith('TLM_WS_Boundary')else r['flags'];assert n['flags']==flags,'Unapproved flags'
   skip={b'DATA'}
   if r['name']in('TLM_WS_RoadMarkerLeft','TLM_WS_RoadMarkerRight','TLM_OPEN_HollowRoutePost','TLM_OPEN_ShoulderRoutePost'):skip.add(b'XSCL')
   if r['name']in('TLM_OPEN_RidgeTree2','TLM_OPEN_RidgeTree4','TLM_OPEN_RidgeTree6'):skip.add(b'NAME')
   assert [(k,v)for k,v in r['ordered']if k not in skip]==[(k,v)for k,v in n['ordered']if k not in skip],'Unapproved reference payload'
  else:
   skip={b'HEDR'}if fid==0 else {b'VHGT',b'VNML',b'BTXT',b'ATXT',b'VTXT',b'VTEX'}if r['type']=='LAND'else {b'DATA'}if r['type']=='WRLD'else set()
   assert r['flags']==n['flags'] and [(k,v)for k,v in r['ordered']if k not in skip]==[(k,v)for k,v in n['ordered']if k not in skip],'Unapproved nonreference payload'
 # Shared quadrant edges compare authored GLOBAL weights, not independent stripes.
 masks={};pending=None;bases=[]
 for k,b in land['ordered']:
  if k==b'BTXT':bases.append(struct.unpack('<IBBh',b))
  if k==b'ATXT':pending=struct.unpack('<IBBh',b)
  if k==b'VTXT':
   assert pending is not None and len(b)==2312,'Alpha mask length'
   tex,q,_,layer=pending;assert layer in(0,1)and q in range(4),'Alpha header';values={}
   for i in range(289):
    idx,pad,w=struct.unpack_from('<HHf',b,i*8);assert idx==i and pad==0 and math.isfinite(w) and 0<=w<=1,'Invalid alpha vertex';values[(i%17+(q&1)*16,i//17+(q>>1)*16)]=w
   assert tex==(0x3343c if layer==0 else 135990),'Material binding'
   for point,w in values.items():
    key=(layer,*point);assert key not in masks or abs(masks[key]-w)<1e-6,'Quadrant seam';masks[key]=w
 assert len(bases)==4 and all(t==0x125c6c and layer==-1 for t,q,pad,layer in bases),'Base soil'
 assert len(masks)==2178,'Full masks missing'
 assert min(w for (l,x,y),w in masks.items()if l==1)<.01 and max(w for (l,x,y),w in masks.items()if l==1)>.99,'No real material variation'
 assert sum(r['name'].startswith('TLM_WS_Boundary') and bool(r['flags']&0x800)for r in rows.values())==120,'Skyline fence not disabled'
 return {'heightSamples':1089,'heightMin':min(map(min,h)),'heightMax':max(map(max,h)),'normalMaxQuantizationError':maxNormalError,'heightBoundary':'C0 all four edges0; normal-C1/occlusion/native edge not certified','routes':routeProof,'wholeFlatFloorFootprints':floors,'newProps':len(extra),'newPropFootprints':supportProof,'oldRefIDsRetained':oldRefCount,'originalPreOpeningRefXYRetained':363,'worldHeaderLiteralCarry':False,'materialGlobalVertices':len(masks),'profile':[[x,y,ground(h,x,y),ground(h,x,y,True)]for x,y in MAIN],'native':'OPEN: traversal, skyline, collisions, materials, actor/corpse/rendering'}
if __name__=='__main__':
 rows,_=records(OUT/'TLMWorldSlice.esp');result=verify(rows);result['worldSha256']=hashlib.sha256((OUT/'TLMWorldSlice.esp').read_bytes()).hexdigest().upper();(ROOT/'build/landscape-decoded-proof.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))





