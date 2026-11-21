"""Raw audition readback and selected native bindings. No game/native claims."""
from pathlib import Path
import struct,zlib,json,collections,hashlib,subprocess
ROOT=Path(__file__).resolve().parent
OUT=ROOT/'build/audition-003/TLMNpcPresentation.esp'
BASE=ROOT.parents[3]/'work/rh-return-account-build-f491eeb/build/licensed-return-account-skeleton-001/bundle'
MASTER=Path('C:/Program Files (x86)/GOG Galaxy/Games/Fallout 4 GOTY/Data/Fallout4.esm')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest().upper()
def subs(data):
 p=0;out=[];wide=None
 while p<len(data):
  k,n=struct.unpack_from('<4sH',data,p);p+=6
  if k==b'XXXX':wide=struct.unpack_from('<I',data,p)[0];p+=n;continue
  if wide is not None:n,wide=wide,None
  assert p+n<=len(data);out.append((k,data[p:p+n]));p+=n
 return out

def rows(data):
 out={}
 def walk(a,b,chain=()):
  while a<b:
   tag,n,flags,fid=struct.unpack_from('<4sIII',data,a)
   if tag==b'GRUP':assert n>=24 and a+n<=b;walk(a+24,a+n,chain+((fid,flags),));a+=n;continue
   assert a+24+n<=b;body=data[a+24:a+24+n];body=zlib.decompress(body[4:]) if flags&0x40000 else body
   assert(tag,fid)not in out;out[tag,fid]=(flags,body,chain);a+=24+n
  assert a==b
 walk(0,len(data));return out

def native(ids):
 out={}
 def walk(f,end):
  while f.tell()<end:
   start=f.tell();h=f.read(24);tag,n,flags,fid=struct.unpack('<4sIII',h[:16])
   if tag==b'GRUP':walk(f,start+n);continue
   if fid not in ids:f.seek(n,1);continue
   b=f.read(n);b=zlib.decompress(b[4:]) if flags&0x40000 else b;out[tag,fid]=dict(subs(b))
 with MASTER.open('rb')as f:walk(f,MASTER.stat().st_size)
 return out

def inputs():
 assert sha(BASE/'TheLastMeridian.esp')=='5C22EE73009BF1F6B75CFBD5C5E52A749B2086ABA847521B5B294E3ED66E81FF'
 assert sha(BASE/'TLMWorldSlice.esp')=='ACE5F0A233A1E8124555B15812FFC445FF1AB23DAAA4D672FCDEC231C1D93FAF'
 plan=json.loads((ROOT/'audition-plan.json').read_text());assets=json.loads((ROOT/'facegen-metadata.json').read_text())
 ids={0x24a024,0x113348,0x24a01b,0xb2d8d,0x1c26b9,0x178b68,0x1c4be8,0xb2d89,0x5e76b,0x178b67,0x1c4be9}
 return plan,assets,native(ids),rows((BASE/'TheLastMeridian.esp').read_bytes()),rows((BASE/'TLMWorldSlice.esp').read_bytes())

def verify(raw,plan,assets,stock,story,world):
 r=rows(raw);counts=collections.Counter(k[0].decode()for k in r);assert counts=={'TES4':1,'WRLD':1,'CELL':2,'REFR':24,'NPC_':3,'ACHR':3,'OTFT':3,'DOOR':2},'Wrong record topology'
 head=dict(subs(r[b'TES4',0][1]));assert [b.rstrip(b'\0').decode()for k,b in subs(r[b'TES4',0][1])if k==b'MAST']==['Fallout4.esm','TLMWorldSlice.esp']
 assert abs(struct.unpack('<f',head[b'HEDR'][:4])[0]-.95)<.00001
 assert {k for k in r if k[1]>>24!=2}=={(b'TES4',0),(b'WRLD',0x01000800),(b'CELL',0x01000801)},'Unexpected old override'
 for tag,key in [(b'WRLD',0x800),(b'CELL',0x801)]:assert r[tag,0x01000000+key][:2]==world[tag,0x02000000+key][:2],'Old header changed'
 cellId=int(plan['cell'].split(':')[0],16)|0x02000000;cell=dict(subs(r[b'CELL',cellId][1]));assert struct.unpack('<H',cell[b'DATA'])[0]&1
 assert cell[b'EDID'].rstrip(b'\0')==b'TLM_NPC_Audition' and b'XCLL'in cell
 entries={e['path'].lower():e for e in assets['entries']};assert len(entries)==11
 faces=[];actorPositions=[]
 faceTags={b'PNAM',b'HCLF',b'BCLF',b'NAM9',b'FTST',b'QNAM',b'MSDK',b'MSDV',b'FMRI',b'FMRS',b'TETI',b'TEND',b'TINC',b'TINV',b'TIRS',b'TIAS',b'TIAC'}
 for p in plan['actors']:
  key=int(p['prototype'].split(':')[0],16)|0x02000000;s=dict(subs(r[b'NPC_',key][1]));donor=int(p['traits'].split(':')[0],16);n=stock[b'NPC_',donor]
  assert struct.unpack_from('<H',s[b'ACBS'],14)[0]==1,'Traits-only inheritance lost/outfit inherited'
  assert struct.unpack('<I',s[b'TPLT'])[0]==donor and struct.unpack('<13I',s[b'TPTA'])==(donor,)+(0,)*12,'Wrong deterministic trait donor'
  assert not struct.unpack_from('<H',n[b'ACBS'],14)[0]&1 and struct.unpack('<I',n[b'RNAM'])[0]==0x13746,'Not terminal human donor'
  assert bool(struct.unpack_from('<I',n[b'ACBS'])[0]&1)==p['female']
  assert not any(k in s for k in [b'VMAD',b'PKID',b'SNAM',b'COCT',b'CNTO']),'Unexpected behavior/inventory'
  original=int(p['original'].split(':')[0],16)|0x01000000;o=dict(subs(story[b'NPC_',original][1]));assert [(k,b) for k,b in subs(r[b'NPC_',key][1])if k in faceTags]==[(k,b) for k,b in subs(story[b'NPC_',original][1])if k in faceTags],'Custom face payload introduced'
  outfit=int(p['outfit'].split(':')[0],16)|0x02000000;assert struct.unpack('<I',s[b'DOFT'])[0]==outfit,'Wrong explicit outfit'
  items=dict(subs(r[b'OTFT',outfit][1]))[b'INAM'];actual=struct.unpack('<'+'I'*(len(items)//4),items);armor=int(p['armor'].split(':')[0],16);assert actual==((armor,0x1c4be8)if p['Id']=='Miriam' else(armor,)),'Wrong clothing set'
  arm=stock[b'ARMO',armor];assert b'VMAD'not in arm;arma={0xb2d8d:0xb2d89,0x1c26b9:0x5e76b,0x178b68:0x178b67}[armor];aa=stock[b'ARMA',arma];assert aa[b'MOD3'if p['female']else b'MOD2'].rstrip(b'\0').decode()==p['armorModels'][0],'No sex-appropriate clothing model'
  face='meshes/actors/character/facegendata/facegeom/fallout4.esm/'+f'{donor:08x}.nif';e=entries[face];assert e['bytes']>300000 and len(e['sha256'])==64;faces.append(e['sha256'])
  placed=int(p['placed'].split(':')[0],16)|0x02000000;flags,b,parents=r[b'ACHR',placed];ss=dict(subs(b));assert flags==0x400 and struct.unpack('<I',ss[b'NAME'])[0]==key,'Prototype missing/not bound'
  assert parents[-2:]==((6,cellId),(8,cellId)),'Actor not placed persistently in audition cell'
  pose=struct.unpack('<6f',ss[b'DATA']);assert pose[:3]==tuple(p['position']) and abs(pose[5]-3.14159265)<.00001;actorPositions.append(pose)
 assert len(set(faces))==3,'FaceGeom assets not distinct'
 for i,p in enumerate(actorPositions):
  assert -640<=p[0]<=640 and 128<=p[1]<=640 and p[2]==16
  for q in actorPositions[:i]:assert abs(p[0]-q[0])>=384
 for piece in plan['room']:
  key=int(piece['key'].split(':')[0],16)|0x02000000;flags,b,parents=r[b'REFR',key];s=dict(subs(b));assert flags==0 and set(s)=={b'EDID',b'NAME',b'DATA'}
  assert struct.unpack('<I',s[b'NAME'])[0]==int(piece['donor'].split(':')[0],16)
  assert s[b'DATA']==struct.pack('<6f',*(piece['position']+[0,0,piece['yaw']])),'Room pose changed'
  assert parents[-2:]==((6,cellId),(9,cellId))
 for which,other in [('entry','exit'),('exit','entry')]:
  p=plan[which];key=int(p['key'].split(':')[0],16)|0x02000000;flags,b,parents=r[b'REFR',key];s=dict(subs(b));assert flags==0x400 and b'VMAD'not in s
  target=int(plan[other]['key'].split(':')[0],16)|0x02000000;tele=s[b'XTEL'];assert len(tele)==36 and struct.unpack('<I6f',tele[:28])==(target,*p['landing'],0,0,0),'Broken reciprocal teleport/landing'
  assert s[b'DATA']==struct.pack('<6f',*(p['at']+[0,0,0]))
  expected=0x01000801 if which=='entry' else cellId;assert parents[-2:]==((6,expected),(8,expected)),'Door wrong persistent cell'
 return {'status':'PASS','prototypesPlaced':3,'distinctNativeFaceGeomHashes':3,'explicitStockOutfits':3,'passiveRoomPieces':22,'reciprocalDoorRefs':2,'originalHeadersOnly':2,'customFaceMorphEdits':0,'nativeFaceRenderingOrDoorTravel':None}
def source_errors():
 receipt=json.loads((ROOT/'source-receipt.json').read_text());repo=ROOT.parents[1];base='f491eeb4e670d306530446b60f82785950dbb747';errors=[]
 inventory=subprocess.check_output(['git','ls-tree','-r',base],cwd=repo)
 if hashlib.sha256(inventory).hexdigest().upper()!=receipt['baselineInventorySha256']:errors.append('Baseline inventory differs')
 changed=subprocess.check_output(['git','diff','--name-only',base,'--'],cwd=repo,text=True).splitlines();untracked=subprocess.check_output(['git','ls-files','--others','--exclude-standard'],cwd=repo,text=True).splitlines()
 allowed={'tools/NpcPresentation/'+n for n in receipt['files']}|{'tools/NpcPresentation/source-receipt.json'}
 if set(changed+untracked)-allowed:errors.append('Change outside own appearance component')
 for name,h in receipt['files'].items():
  if not(ROOT/name).is_file()or sha(ROOT/name)!=h:errors.append('Source pin '+name)
 return errors
if __name__=='__main__':
 assert not source_errors(),source_errors()
 print(json.dumps(verify(OUT.read_bytes(),*inputs()),indent=2))
