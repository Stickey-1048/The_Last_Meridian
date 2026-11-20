"""Read selected owned-stock metadata/NIF faces IN MEMORY; never writes assets.
Usage: python tools/rh_terrain_donor_probe.py GAME_DATA receipt.json
"""
from pathlib import Path
import hashlib,json,math,struct,sys,zlib

def subrecords(d):
 p=0;extended=None
 while p<len(d):
  tag,n=struct.unpack_from('<4sH',d,p);p+=6
  if tag==b'XXXX':extended=struct.unpack_from('<I',d,p)[0];p+=n;continue
  if extended is not None:n,extended=extended,None
  yield tag,d[p:p+n];p+=n
 assert p==len(d)

def selected_metadata(master):
 wanted={'workshop_ShackMidFloor01B','NpcBedWoodLay01Static','NPCCouchModernDomesticSit01Static','FenceWoodStr01','RockPileM01','QryCubeWall01'};result={};pair={}
 def walk(f,end):
  while f.tell()<end:
   at=f.tell();h=f.read(24);tag=h[:4];n,flags,fid=struct.unpack_from('<III',h,4)
   if tag==b'GRUP':walk(f,at+n);continue
   if tag!=b'STAT' and fid not in (0x4CBE9,0x4CBEA):f.seek(n,1);continue
   d=f.read(n);d=zlib.decompress(d[4:]) if flags&0x40000 else d;s=dict(subrecords(d));name=s.get(b'EDID',b'').rstrip(b'\0').decode()
   if name in wanted:
    assert not any(k in s for k in (b'VMAD',b'DEST'))
    result[name]={'key':f'{fid:08X}','model':s[b'MODL'].rstrip(b'\0').decode(),'bounds':list(struct.unpack('<6h',s[b'OBND'])),'passive':True}
   if fid in (0x4CBE9,0x4CBEA):pair[f'{fid:08X}']={'base':f'{struct.unpack("<I",s[b"NAME"])[0]:08X}','positionRotation':list(struct.unpack('<6f',s[b'DATA']))}
 with master.open('rb') as f:walk(f,master.stat().st_size)
 assert set(result)==wanted and len(pair)==2
 return result,pair

def mesh(archive,suffix):
 with archive.open('rb') as f:
  magic,version,kind,count,names=struct.unpack('<4sI4sIQ',f.read(24));assert (magic,version,kind)==(b'BTDX',1,b'GNRL')
  rows=[struct.unpack('<I4sIIQIII',f.read(36)) for _ in range(count)];f.seek(names)
  for row in rows:
   path=f.read(struct.unpack('<H',f.read(2))[0]).decode()
   if path.lower().replace('\\','/')!=suffix.lower().replace('\\','/'):continue
   f.seek(row[4]);data=f.read(row[5] or row[6]);data=zlib.decompress(data) if row[5] else data;assert len(data)==row[6]
   return data
 raise ValueError('Exact selected mesh missing')

def wall_faces(data):
 p=data.index(b'\n')+1;version,endian,user,n,bs=struct.unpack_from('<IBIII',data,p);p+=17
 assert (version,endian,user,bs)==(0x14020007,1,12,130)
 for _ in range(4):size=data[p];p+=1+size
 nt=struct.unpack_from('<H',data,p)[0];p+=2;types=[]
 for _ in range(nt):size=struct.unpack_from('<I',data,p)[0];p+=4;types.append(data[p:p+size].decode());p+=size
 ids=struct.unpack_from('<'+'H'*n,data,p);p+=2*n;sizes=struct.unpack_from('<'+'I'*n,data,p);p+=4*n
 ns,ml=struct.unpack_from('<II',data,p);p+=8
 for _ in range(ns):size=struct.unpack_from('<I',data,p)[0];p+=4+size
 groups=struct.unpack_from('<I',data,p)[0];p+=4+4*groups;shapes=[]
 for blocktype,size in zip(ids,sizes):
  d=data[p:p+size];p+=size
  if types[blocktype]!='BSTriShape':continue
  # Exact small passive selected wall format, refuse unknown layout rather
  # than heuristically decoding arbitrary NIFs. Do not export vertex/tri bytes.
  assert size==210
  triangles,vertices,length=struct.unpack_from('<IHI',d,108);assert (triangles,vertices,length)==(2,4,92)
  v=[struct.unpack_from('<3e',d,118+i*20) for i in range(vertices)];normals=[]
  for i in range(triangles):
   a,b,c=[v[j] for j in struct.unpack_from('<3H',d,198+i*6)];u=[b[j]-a[j] for j in range(3)];w=[c[j]-a[j] for j in range(3)];cross=[u[1]*w[2]-u[2]*w[1],u[2]*w[0]-u[0]*w[2],u[0]*w[1]-u[1]*w[0]];length=math.sqrt(sum(x*x for x in cross));normals.append([round(x/length,6) for x in cross])
  assert normals==[[0,-1,0],[0,-1,0]]
  # Packed vertex normals corroborate the triangle winding.
  assert all(d[118+i*20+12:118+i*20+15]==bytes((127,0,127)) for i in range(vertices))
  shapes.append({'triangles':triangles,'vertices':vertices,'localFaceNormal':[0,-1,0],'packedNormalsAgree':True})
 assert len(shapes)==1 and p+4<=len(data)
 return {'sha256':hashlib.sha256(data).hexdigest().upper(),'shapes':shapes,'collisionBlockPresent':b'bhkPhysicsSystem' in data,'limits':'Face direction and block presence only; material sidedness, Havok and native visibility not certified'}

if __name__=='__main__':
 data=Path(sys.argv[1]);assets,pair=selected_metadata(data/'Fallout4.esm');faces=wall_faces(mesh(data/'Fallout4 - Meshes.ba2',r'Meshes\Architecture\Quarry\QryCubeWall01.nif'))
 floor,wall=pair['0004CBE9'],pair['0004CBEA'];assert floor['base']=='0002CBD6' and wall['base']=='0002CBDC'
 assert abs(wall['positionRotation'][5]-1.5*math.pi)<1e-5 and floor['positionRotation'][0]-wall['positionRotation'][0]==256
 result={'scope':'Owned-stock selected numerical metadata only; no assets copied','assets':assets,'wallMesh':faces,'nativeDonorPair':pair,'rotationEvidence':'Wall at west edge of adjacent floor has yaw-PI/2; local-Y face points+X with clockwise native yaw. Perimeter desired SouthPI/North0/West-PI/2/East+PI/2. GallerySeal+PI/2 already faces west.'}
 Path(sys.argv[2]).write_text(json.dumps(result,indent=2)+'\n');print('Selected6passiveSTAT and one wall face/donor pair read; metadata receipt written. No native validation.')
