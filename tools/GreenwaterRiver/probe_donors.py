"""Owned static model metadata only; all mesh bytes remain in memory."""
from pathlib import Path
import struct,zlib,json,hashlib,collections
DATA=Path('C:/Program Files (x86)/GOG Galaxy/Games/Fallout 4 GOTY/Data')
def subs(d):
 p=0;over=None
 while p<len(d):
  k,n=struct.unpack_from('<4sH',d,p);p+=6
  if k==b'XXXX':over=struct.unpack_from('<I',d,p)[0];p+=n;continue
  if over is not None:n,over=over,None
  yield k,d[p:p+n];p+=n
assets={'PowerLiftButton01': {'id': '000EEFBD', 'model': 'Interiors\\HighTech\\Animated\\PowerLift\\PowerLiftButton\\PowerLiftButton01.nif', 'bounds': [-4, 84, 16, 4, 90, 98], 'passive': False}, 'Barge_01_MidSide': {'id': '00112026', 'model': 'SetDressing\\Boats\\Barge_01_MidSide.nif', 'bounds': [-384, -225, -150, 384, 192, 16], 'passive': True}, 'Barge_01_Mid': {'id': '00112025', 'model': 'SetDressing\\Boats\\Barge_01_Mid.nif', 'bounds': [-384, -192, -150, 384, 192, 3], 'passive': True}, 'Rowboat01': {'id': '000A0F1D', 'model': 'SetDressing\\Rowboat\\Rowboat01.nif', 'bounds': [-89, -283, -59, 89, 300, 37], 'passive': True}}
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
  ng=struct.unpack_from('<I',d,p)[0];p+=4+4*ng;shapes=[];allv=[];identity_nodes=True;root_transform=None; transforms={}; parents={}; shapeverts={}; bi=-1
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
   shapeverts[bi]=verts;shapes.append({'orientedAreaSum':facing,'name': strings[struct.unpack_from('<i',block,0)[0]] if struct.unpack_from('<i',block,0)[0]>=0 else '', 'localBounds':[min(v[j]for v in verts)for j in range(3)]+[max(v[j]for v in verts)for j in range(3)],'type':t,'vertices':nv,'triangles':nt,'stride':stride,'fullPrecisionPosition':full})
  for shape,verts in shapeverts.items():
   parent=parents.get(shape);seen={shape}
   while parent is not None:
    assert parent not in seen;seen.add(parent)
    tr,rot,scale=transforms[parent];verts=[[tr[j]+scale*sum(rot[j*3+k]*v[k] for k in range(3)) for j in range(3)] for v in verts];parent=parents.get(parent)
   allv.extend(verts)
  a=assets[models[model]];a['nif']={'sha256':hashlib.sha256(d).hexdigest().upper(),'blocks':dict(collections.Counter(types[i] for i in ids)),'identityParentNodes':identity_nodes,'shapes':shapes,'renderBounds':[min(v[j] for v in allv) for j in range(3)]+[max(v[j] for v in allv) for j in range(3)] if allv else None,'limits':'Render metadata and collision block presence only; Havok/world collision not certified'}
  if allv:
   low=min(v[2] for v in allv);feet=[v for v in allv if v[2]<low+1];a['nif']['bottomBandBounds']=[min(v[j] for v in feet) for j in range(3)]+[max(v[j] for v in feet) for j in range(3)]
assert len(assets)==4 and all('nif'in a for a in assets.values())
(Path(__file__).resolve().parent/'new-donor-metadata.json').write_text(json.dumps({'scope':'Selected owned numerical metadata only; no mesh bytes/vertices exported','assets':assets},indent=2)+'\n')
print(json.dumps(assets,indent=2))
