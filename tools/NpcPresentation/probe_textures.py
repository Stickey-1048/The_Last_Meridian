from pathlib import Path
import json,struct,zlib,hashlib,sys
ROOT=Path(__file__).resolve().parent;D=Path('C:/Program Files (x86)/GOG Galaxy/Games/Fallout 4 GOTY/Data')
from nif_metadata import nif
meta=json.loads((ROOT/'facegen-metadata.json').read_text());wanted={e['path']for e in meta['entries']};references={}
for archive in {e['archive']for e in meta['entries']}:
 with (D/archive).open('rb')as f:
  _,_,_,n,offset=struct.unpack('<4sI4sIQ',f.read(24));rows=[struct.unpack('<I4sIIQIII',f.read(36))for _ in range(n)];f.seek(offset)
  for i in range(n):
   name=f.read(struct.unpack('<H',f.read(2))[0]).decode().lower().replace('\\','/')
   if name not in wanted:continue
   here=f.tell();row=rows[i];f.seek(row[4]);b=f.read(row[5]or row[6]);b=zlib.decompress(b)if row[5]else b;f.seek(here);refs=set()
   for typ,block in nif(b)[0]:
    if typ!='BSShaderTextureSet':continue
    q=4
    for _ in range(struct.unpack_from('<I',block,0)[0]):
     size=struct.unpack_from('<I',block,q)[0];q+=4;s=block[q:q+size].decode().lower().replace('\\','/');q+=size
     if not s:continue
     if s.startswith('data/'):s=s[5:]
     if not s.startswith('textures/'):s='textures/'+s
     refs.add(s)
   references[name]=sorted(refs)
needed={p for paths in references.values()for p in paths};found={}
for archive in D.glob('Fallout4 - Textures*.ba2'):
 with archive.open('rb')as f:
  _,_,kind,n,offset=struct.unpack('<4sI4sIQ',f.read(24));assert kind==b'DX10';f.seek(offset);selected={}
  for i in range(n):
   path=f.read(struct.unpack('<H',f.read(2))[0]).decode('ascii','replace').lower().replace('\\','/')
   if path in needed:selected[i]=path
  if not selected:continue
  f.seek(24)
  for i in range(max(selected)+1):
   r=struct.unpack('<I4sIBBHHHBBH',f.read(24));chunks=[struct.unpack('<QIIHHI',f.read(24))for _ in range(r[4])]
   if i not in selected:continue
   here=f.tell();hasher=hashlib.sha256();length=0
   for c in chunks:
    f.seek(c[0]);b=f.read(c[1]or c[2]);b=zlib.decompress(b)if c[1]else b;assert len(b)==c[2];hasher.update(b);length+=len(b)
   f.seek(here);found[selected[i]]={'path':selected[i],'archive':archive.name,'width':r[7],'height':r[6],'mips':r[8],'dxgiFormat':r[9],'chunks':len(chunks),'unpackedBytes':length,'unpackedSha256':hasher.hexdigest().upper()}
missing=sorted(needed-set(found));result={'scope':'All selected NIF BSShaderTextureSet paths; owned DDS chunk hashes only, no licensed payload export','references':references,'entries':list(found.values()),'missing':missing};(ROOT/'texture-metadata.json').write_text(json.dumps(result,indent=2)+'\n');print('Needed',len(needed),'located',len(found),'missing',missing)
