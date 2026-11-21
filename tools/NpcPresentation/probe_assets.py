from pathlib import Path
import struct,zlib,hashlib,json
D=Path('C:/Program Files (x86)/GOG Galaxy/Games/Fallout 4 GOTY/Data')
paths=['actors/character/facegendata/facegeom/fallout4.esm/0024a024.nif','actors/character/facegendata/facegeom/fallout4.esm/00113348.nif','actors/character/facegendata/facegeom/fallout4.esm/0024a01b.nif','armor/raiderheavy/munderarmor.nif','clothes/redrocketjumpsuit/redrocketjumpsuitf.nif','clothes/vaulttecscientist/vtscientistfvariant.nif','clothes/shortsleeves/fglasses.nif','architecture/quarry/qryfloor01.nif','architecture/quarry/qrycubewall01.nif','interiors/cave/rooms/cavermceiling512v01.nif','architecture/shacks/shackdoor01.nif'];wanted={'meshes/'+p for p in paths};found=[]
for archive in [D/'Fallout4 - Meshes.ba2',D/'Fallout4 - MeshesExtra.ba2']:
 with archive.open('rb') as f:
  magic,ver,kind,n,offset=struct.unpack('<4sI4sIQ',f.read(24));assert(magic,ver,kind)==(b'BTDX',1,b'GNRL');rows=[struct.unpack('<I4sIIQIII',f.read(36)) for _ in range(n)];f.seek(offset)
  for i in range(n):
   name=f.read(struct.unpack('<H',f.read(2))[0]).decode().lower().replace('\\','/')
   if name not in wanted:continue
   here=f.tell();r=rows[i];f.seek(r[4]);b=f.read(r[5] or r[6]);b=zlib.decompress(b) if r[5] else b;f.seek(here)
   found.append({'path':name,'archive':archive.name,'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest().upper(),'collisionBlockNamesPresent':b'bhkNPCollisionObject' in b and b'bhkPhysicsSystem' in b,'payloadExported':False})
assert {a['path'] for a in found}==wanted
P=Path(__file__).resolve().parent/'facegen-metadata.json';P.write_text(json.dumps({'scope':'Selected owned NIF metadata only; no original bytes exported. FaceGeom and worn clothing NIFs are present; native inherited skin/tint rendering remains a gate.','entries':found},indent=2)+'\n');print('Selected11 actual owned model/FaceGen hashes verified:',len(found));print([(p['path'],p['bytes']) for p in found[:3]])
