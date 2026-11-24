"""One owned NIF in-memory shader/alpha association; no mesh/texture export."""
from pathlib import Path
import struct,zlib,json,hashlib
DATA=Path('C:/Program Files (x86)/GOG Galaxy/Games/Fallout 4 GOTY/Data')
model='meshes/setdressing/railroad/rrboxcar01.nif'
with (DATA/'Fallout4 - Meshes.ba2').open('rb') as f:
 _,version,kind,count,offset=struct.unpack('<4sI4sIQ',f.read(24));assert version==1 and kind==b'GNRL'
 rows=[struct.unpack('<I4sIIQIII',f.read(36))for _ in range(count)];f.seek(offset)
 for row in rows:
  name=f.read(struct.unpack('<H',f.read(2))[0]).decode().lower().replace('\\','/')
  if name!=model:continue
  f.seek(row[4]);d=f.read(row[5]or row[6]);d=zlib.decompress(d)if row[5]else d;break
 else:raise AssertionError('Owned hull absent')
p=d.index(b'\n')+1;ver,endian,user,nb,bs=struct.unpack_from('<IBIII',d,p);p+=17
assert(ver,endian,user,bs)==(0x14020007,1,12,130)
for _ in range(4):n=d[p];p+=1+n
nt=struct.unpack_from('<H',d,p)[0];p+=2;types=[]
for _ in range(nt):n=struct.unpack_from('<I',d,p)[0];p+=4;types.append(d[p:p+n].decode());p+=n
ids=struct.unpack_from('<'+'H'*nb,d,p);p+=nb*2;sizes=struct.unpack_from('<'+'I'*nb,d,p);p+=nb*4
ns,maxs=struct.unpack_from('<II',d,p);p+=8;strings=[]
for _ in range(ns):n=struct.unpack_from('<I',d,p)[0];p+=4;strings.append(d[p:p+n].decode());p+=n
ng=struct.unpack_from('<I',d,p)[0];p+=4+4*ng;blocks=[]
for typ,size in zip(ids,sizes):blocks.append((types[typ],d[p:p+size]));p+=size
name=lambda b: strings[struct.unpack_from('<i',b,0)[0]] if 0<=struct.unpack_from('<i',b,0)[0]<len(strings) else None
out=[]
for i,(t,b)in enumerate(blocks):
 if t not in('BSTriShape','BSSubIndexTriShape','BSMeshLODTriShape'):continue
 extra=struct.unpack_from('<I',b,4)[0];q=16+extra*4
 sh,al=struct.unpack_from('<ii',b,q+76)
 assert sh>=0 and blocks[sh][0]=='BSLightingShaderProperty',(i,sh,al)
 alpha=None
 if al>=0:
  at,ab=blocks[al];assert at=='NiAlphaProperty';ae=struct.unpack_from('<I',ab,4)[0];flags,threshold=struct.unpack_from('<HB',ab,12+ae*4)
  alpha={'block':al,'flags':flags,'threshold':threshold}
 out.append({'block':i,'shape':name(b),'shaderBlock':sh,'shaderMaterialName':strings[struct.unpack_from('<i',blocks[sh][1],4)[0]],'alphaProperty':alpha})
result={'model':model,'nifSha256':hashlib.sha256(d).hexdigest().upper(),'shapes':out,'limits':'Material names/alpha property association only. No alpha texture decoding, active native shader path or Havok proof; no extracted payload written.'}
Path(__file__).with_name('roof-metadata.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
