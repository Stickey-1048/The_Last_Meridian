"""Owned static model metadata only; all mesh bytes remain in memory."""
from pathlib import Path
import struct,zlib,json,hashlib,collections,math
DATA=Path('C:/Program Files (x86)/GOG Galaxy/Games/Fallout 4 GOTY/Data')

def subs(d):
 p=0;over=None
 while p<len(d):
  k,n=struct.unpack_from('<4sH',d,p);p+=6
  if k==b'XXXX':over=struct.unpack_from('<I',d,p)[0];p+=n;continue
  if over is not None:n,over=over,None
  yield k,d[p:p+n];p+=n
assets={
'RRBoxcar01':{'id':'0005CA0B','model':'SetDressing\\Railroad\\RRBoxcar01.nif','bounds':[-113,-557,-2,113,557,328],'type':'STAT'},
'RRBoxcarDoor01Static':{'id':'0008EB6E','model':'SetDressing\\Railroad\\RRBoxcarDoor01.nif','bounds':[107,-100,73,113,100,274],'type':'STAT'},
'ToolCase':{'id':'0001930B','model':'SetDressing\\Toolbox\\Toolbox.nif','bounds':[-12,-25,0,11,25,22],'type':'CONT'},
'WoodCrate03':{'id':'000211F7','model':'SetDressing\\ConcMuseum\\WoodCrate03.nif','bounds':[-25,-52,0,25,52,29],'type':'STAT'},
'Lantern01':{'id':'0001D2C7','model':'SetDressing\\LightFixtures\\Lantern01.nif','bounds':[-6,-6,0,6,6,26],'type':'STAT'}}
assets={k:v for k,v in assets.items() if k=='RRBoxcarDoor01Static'}
fullsets={}
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'SheriffWorld'));from raw import records
models={v['model'].lower().replace('\\','/'):name for name,v in assets.items()}
with (DATA/'Fallout4 - Meshes.ba2').open('rb') as f:
 _,version,kind,count,offset=struct.unpack('<4sI4sIQ',f.read(24));assert version==1 and kind==b'GNRL'
 rows=[struct.unpack('<I4sIIQIII',f.read(36)) for _ in range(count)];f.seek(offset)
 for row in rows:
  name=f.read(struct.unpack('<H',f.read(2))[0]).decode().lower().replace('\\','/');model=name.removeprefix('meshes/')
  if model not in models:continue
  at=f.tell();f.seek(row[4]);d=f.read(row[5] or row[6]);d=zlib.decompress(d) if row[5] else d;f.seek(at)
  p=d.index(b'\n')+1;ver,endian,user,nb,bs=struct.unpack_from('<IBIII',d,p);p+=17;assert(ver,endian,user,bs)==(0x14020007,1,12,130)
  for _ in range(4):n=d[p];p+=1+n
  nt=struct.unpack_from('<H',d,p)[0];p+=2;types=[]
  for _ in range(nt):n=struct.unpack_from('<I',d,p)[0];p+=4;types.append(d[p:p+n].decode());p+=n
  ids=struct.unpack_from('<'+'H'*nb,d,p);p+=nb*2;sizes=struct.unpack_from('<'+'I'*nb,d,p);p+=nb*4
  ns,maxs=struct.unpack_from('<II',d,p);p+=8
  strings=[]
  for _ in range(ns):n=struct.unpack_from('<I',d,p)[0];p+=4;strings.append(d[p:p+n].decode());p+=n
  ng=struct.unpack_from('<I',d,p)[0];p+=4+4*ng;shapes=[];allv=[];identity_nodes=True;horizontal=collections.defaultdict(float);root_transform=None; transforms={}; parents={}; shapeverts={}; shapeindices={}; bi=-1
  for typ,size in zip(ids,sizes):
   block=d[p:p+size];p+=size;t=types[typ];bi+=1
   if t not in ('BSTriShape','BSSubIndexTriShape','BSMeshLODTriShape','NiNode','BSFadeNode','BSLeafAnimNode'):continue
   extra=struct.unpack_from('<I',block,4)[0];q=16+4*extra
   tr=struct.unpack_from('<3f',block,q);rot=struct.unpack_from('<9f',block,q+12);scale=struct.unpack_from('<f',block,q+48)[0]
   transforms[bi]=(tr,rot,scale)
   if t in ('NiNode','BSFadeNode','BSLeafAnimNode'):
    identity_nodes &= tr==(0,0,0) and rot==(1,0,0,0,1,0,0,0,1) and scale==1
    children=struct.unpack_from('<I',block,q+56)[0]
    assert children<10000 and q+60+children*4<=len(block)
    for child in struct.unpack_from('<'+'i'*children,block,q+60):
     if child>=0:assert child not in parents;parents[child]=bi
    continue
   off=100+4*extra;desc=struct.unpack_from('<Q',block,off)[0];stride=(desc&15)*4;nt,nv,length=struct.unpack_from('<IHI',block,off+8);begin=off+18
   if not stride or nv==0 or length<nv*stride:continue
   full=bool(desc&(1<<54));fmt='<3f' if full else '<3e';verts=[]
   for i in range(nv):
    v=struct.unpack_from(fmt,block,begin+i*stride);world=[tr[j]+scale*sum(rot[j*3+k]*v[k] for k in range(3)) for j in range(3)];verts.append(world)
   # Triangle winding is summarized numerically; no indices/vertices exported.
   facing=[0.,0.,0.];triStart=begin+nv*stride
   assert triStart+nt*6<=len(block)
   for ti in range(nt):
    ia,ib,ic=struct.unpack_from('<3H',block,triStart+ti*6);assert max(ia,ib,ic)<nv
    va,vb,vc=verts[ia],verts[ib],verts[ic];ab=[vb[k]-va[k]for k in range(3)];ac=[vc[k]-va[k]for k in range(3)]
    cross=[ab[1]*ac[2]-ab[2]*ac[1],ab[2]*ac[0]-ab[0]*ac[2],ab[0]*ac[1]-ab[1]*ac[0]];facing=[facing[k]+cross[k]/2 for k in range(3)]
   
    if cross[2]>0 and max(va[2],vb[2],vc[2])-min(va[2],vb[2],vc[2])<.05:horizontal[round((va[2]+vb[2]+vc[2])/3,1)]+=cross[2]/2
   shapeindices[bi]=[struct.unpack_from("<3H",block,triStart+ti*6)for ti in range(nt)];shapeverts[bi]=verts;shapes.append({'orientedAreaSum':facing,'name': strings[struct.unpack_from('<i',block,0)[0]] if struct.unpack_from('<i',block,0)[0]>=0 else '', 'localBounds':[min(v[j]for v in verts)for j in range(3)]+[max(v[j]for v in verts)for j in range(3)],'type':t,'vertices':nv,'triangles':nt,'stride':stride,'fullPrecisionPosition':full})
  worldplanes=collections.defaultdict(lambda:[0,[]]);wallcuts=[];fulltris=[]
  for shape,verts in shapeverts.items():
   parent=parents.get(shape);seen={shape}
   while parent is not None:
    assert parent not in seen;seen.add(parent)
    tr,rot,scale=transforms[parent];verts=[[tr[j]+scale*sum(rot[j*3+k]*v[k] for k in range(3)) for j in range(3)] for v in verts];parent=parents.get(parent)
   allv.extend(verts)
   for ia,ib,ic in shapeindices[shape]:
    a,b,c=verts[ia],verts[ib],verts[ic];fulltris.append([a,b,c]);ab=[b[k]-a[k]for k in range(3)];ac=[c[k]-a[k]for k in range(3)];cross=[ab[1]*ac[2]-ab[2]*ac[1],ab[2]*ac[0]-ab[0]*ac[2],ab[0]*ac[1]-ab[1]*ac[0]]
    if cross[2]>1 and max(a[2],b[2],c[2])-min(a[2],b[2],c[2])<.1:
     plane=worldplanes[round((a[2]+b[2]+c[2])/3,1)];plane[0]+=cross[2]/2;plane[1].extend([a,b,c])
   # Finite doorway slice: x-ranges of actual rendered wall triangles crossing z80 near south facade y=-256.
   for ia,ib,ic in shapeindices[shape]:
    tri=[verts[i]for i in(ia,ib,ic)]
    if min(v[2]for v in tri)<=80<=max(v[2]for v in tri) and min(v[1]for v in tri)<-200:
     wallcuts.append([min(v[0]for v in tri),max(v[0]for v in tri),min(v[1]for v in tri),max(v[1]for v in tri)])
  band=[]
  for a,b,c in fulltris:
   for lo,hi in[(-4,124)]:
    poly=[a,b,c]
    for z,sign in[(lo,1),(hi,-1)]:
     result=[]
     for i,p0 in enumerate(poly):
      p1=poly[(i+1)%len(poly)];inside0=(p0[2]-z)*sign>=0;inside1=(p1[2]-z)*sign>=0
      if inside0:result.append(p0)
      if inside0!=inside1:
       t=(z-p0[2])/(p1[2]-p0[2]);result.append([p0[k]+t*(p1[k]-p0[k])for k in range(3)])
     poly=result
     if not poly:break
    band.extend(poly)
  standingBounds=[min(v[k]for v in band)for k in range(3)]+[max(v[k]for v in band)for k in range(3)]if band else None
  doorBands=[]
  for a,b,c in fulltris:
   tri=[a,b,c]
   if max(v[0]for v in tri)-min(v[0]for v in tri)<5 and -135<sum(v[0]for v in tri)/3<-125 and min(v[2]for v in tri)<=80<=max(v[2]for v in tri):
    pts=[]
    for p0,p1 in[(a,b),(b,c),(c,a)]:
     if (p0[2]-80)*(p1[2]-80)<0:
      t=(80-p0[2])/(p1[2]-p0[2]);pts.append(p0[1]+t*(p1[1]-p0[1]))
    if pts:doorBands.append([min(pts),max(pts)])
  doorUnion=[]
  for lo,hi in sorted(doorBands):
   if doorUnion and lo<=doorUnion[-1][1]+.1:doorUnion[-1][1]=max(doorUnion[-1][1],hi)
   else:doorUnion.append([lo,hi])
  fullsets[models[model]]=fulltris
  a=assets[models[model]];a['nif']={'sha256':hashlib.sha256(d).hexdigest().upper(),'blocks':dict(collections.Counter(types[i] for i in ids)),'identityParentNodes':identity_nodes,'candidateHorizontalUpPlanes':sorted(horizontal.items(),key=lambda q:q[1],reverse=True)[:8],'materialStrings':[v for v in strings if any(e in v.lower()for e in ['.bgsm','.dds'])],'shapes':shapes,'renderBounds':[min(v[j] for v in allv) for j in range(3)]+[max(v[j] for v in allv) for j in range(3)] if allv else None,'standingBandBounds':standingBounds,'doorWallBandsAt80':doorUnion,'fullUpPlanes':[{'z':z,'area':v[0],'bounds':[min(q[j]for q in v[1])for j in range(3)]+[max(q[j]for q in v[1])for j in range(3)]}for z,v in sorted(worldplanes.items(),key=lambda t:t[1][0],reverse=True)[:12]],'limits':'Render metadata and collision block presence only; Havok/world collision not certified'}
  if allv:
   low=min(v[2] for v in allv);feet=[v for v in allv if v[2]<low+1];a['nif']['bottomBandBounds']=[min(v[j] for v in feet) for j in range(3)]+[max(v[j] for v in feet) for j in range(3)]

DOOR=fullsets['RRBoxcarDoor01Static']
# Declared clockwise Y basis: +localZ -> world-X; +localX -> world+Z.
# Native front/back exposure still requires a render; source proof uses actual full-parent triangles.
def transform(v,p):
 import math
 c,s=math.cos(p[4]),math.sin(p[4]);x,y,z=v
 return[p[0]+c*x-s*z,p[1]+y,p[2]+s*x+c*z]
def panels(poses):return [[transform(v,p)for v in t]for p in poses for t in DOOR]
def down_hits(tris,x,y):
 out=[]
 for a,b,c in tris:
  den=(b[1]-c[1])*(a[0]-c[0])+(c[0]-b[0])*(a[1]-c[1])
  # A negative XY determinant is a triangle whose front faces downward, toward actors.
  if den>=-1e-7:continue
  u=((b[1]-c[1])*(x-c[0])+(c[0]-b[0])*(y-c[1]))/den
  v=((c[1]-a[1])*(x-c[0])+(a[0]-c[0])*(y-c[1]))/den
  if min(u,v,1-u-v)>=-1e-7:out.append(u*a[2]+v*b[2]+(1-u-v)*c[2])
 return out

def coverage(poses):
 tris=panels(poses)
 down=[]
 for t in tris:
  a,b,c=t;det=(b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0])
  if det<-.00001:down.append(t)
 # Planar arrangement: all projected edges, all endpoint/crossing X coordinates.
 # Between these abscissae the edge order is invariant and each interval endpoint is linear.
 edges=[(a,b)for t in down for a,b in zip(t,t[1:]+t[:1])]
 xs={-75.,75.}
 for a,b in edges:
  for x in[a[0],b[0]]:
   if -75<x<75:xs.add(x)
 for i,(a,b)in enumerate(edges):
  ux,uy=b[0]-a[0],b[1]-a[1]
  for c,d in edges[i+1:]:
   vx,vy=d[0]-c[0],d[1]-c[1];den=ux*vy-uy*vx
   if abs(den)<1e-10:continue
   wx,wy=c[0]-a[0],c[1]-a[1];t=(wx*vy-wy*vx)/den;s=(wx*uy-wy*ux)/den
   if -1e-8<=t<=1+1e-8 and -1e-8<=s<=1+1e-8:
    x=a[0]+t*ux
    if -75<x<75:xs.add(x)
 xs=sorted(xs);probes=xs+[(a+b)/2 for a,b in zip(xs,xs[1:])if b-a>1e-8]
 for x in probes:
  spans=[]
  for tri in down:
   yy=[]
   for a,b in zip(tri,tri[1:]+tri[:1]):
    if min(a[0],b[0])-1e-6<=x<=max(a[0],b[0])+1e-6:
     if abs(b[0]-a[0])<1e-8:
      if abs(x-a[0])<1e-6:yy.extend([a[1],b[1]])
     else:
      t=(x-a[0])/(b[0]-a[0]);yy.append(a[1]+t*(b[1]-a[1]))
   if len(yy)>=2:spans.append((min(yy),max(yy)))
  reach=-508.
  for lo,hi in sorted(spans):
   if hi<reach:continue
   if lo>reach+1e-5:break
   reach=max(reach,hi)
  assert reach>=508-1e-5,('roof gap',x,reach)
 return {'downFacingTriangles':len(down),'arrangementCriticalX':len(xs),'verifiedSections':len(probes),'coveredRectangle':[-75,-508,75,508],'renderZ':[min(v[2]for t in tris for v in t),max(v[2]for t in tris for v in t)],'basis':'clockwise Y: +Z->-X,+X->+Z; only one rotation component, no Euler order assumption'}
