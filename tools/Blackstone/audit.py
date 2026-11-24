"""Owned numeric/raw Blackstone readback; never certifies native rendering or movement."""
from pathlib import Path
import hashlib,json,struct,sys,math
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'tools'))
from rh_terrain_projection import records,subs
TASK=ROOT/'tools/Blackstone'

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest().upper()
def strip_bridge(data):
 pos=6;result=bytearray(data[:6]);removed=[]
 def string():
  nonlocal pos
  n=struct.unpack_from('<H',data,pos)[0];start=pos;pos+=2+n;return data[start:pos],data[start+2:pos].decode()
 def value(kind):
  nonlocal pos
  if kind>=11:
   n=struct.unpack_from('<I',data,pos)[0];pos+=4
   for _ in range(n):value(kind-10)
  elif kind==2:string()
  else:pos+={1:8,3:4,4:4,5:1}[kind]
 for _ in range(struct.unpack_from('<H',data,4)[0]):
  title,name=string();status=data[pos:pos+1];pos+=1;count=struct.unpack_from('<H',data,pos)[0];pos+=2;kept=[]
  for _ in range(count):
   start=pos;_,prop=string();kind=data[pos];pos+=2;value(kind)
   if (name,prop) in {('TLM:MQ04Quest','TLM_MQ05'),('TLM:BlackLedgerWalk','BlackstoneReady')}:removed.append((name,prop))
   else:kept.append(data[start:pos])
  result+=title+status+struct.pack('<H',len(kept))+b''.join(kept)
 result+=data[pos:]
 assert set(removed)=={('TLM:MQ04Quest','TLM_MQ05'),('TLM:BlackLedgerWalk','BlackstoneReady')} and len(removed)==2,removed
 return bytes(result)
def preservation(new,old,master):
 now,names=records(new.read_bytes());before,bnames=records(old.read_bytes());assert set(before)<=set(now)
 assert all(names.get(n)==k for n,k in bnames.items()),'Original EDID/FormID altered'
 changed=[]
 for key,prior in before.items():
  actual=now[key]
  if actual==prior:continue
  assert actual[0]==prior[0] and actual[2]==prior[2],('Old flags/parent changed',key)
  if key[0]==b'TES4':assert [(k,v)for k,v in subs(prior[1])if k!=b'HEDR']==[(k,v)for k,v in subs(actual[1])if k!=b'HEDR'];continue
  assert master and key==bnames['TLM_MQ04'],('Unrelated payload changed',key)
  aa=subs(actual[1]);bb=subs(prior[1]);clean=[];textchanges=[]
  for tag,body in aa:
   if tag==b'VMAD':body=strip_bridge(body)
   elif tag==b'NNAM' and body==b"Finish at Vane's counter, then read Blackstone's route sheet at Iron Junction\0":
    oldwords=[v for k,v in bb if k==b'NNAM' and v==b"Finish the encounter beside Vane's counter; Blackstone is the next lead\0"];assert len(oldwords)==1;body=oldwords[0];textchanges.append(100)
   clean.append((tag,body))
  assert bb==clean,'Changes exceed exact two optional bindings/objective100'
  assert textchanges==[100];changed.append('TLM_MQ04')
 assert changed==(['TLM_MQ04']if master else[]),changed
 return {'oldRecords':len(before),'newRecords':len(now)-len(before),'oldPayloadExceptions':changed,'oldFlagsAndParentsExact':True,'literalFileEqual':new.read_bytes()==old.read_bytes()}
def run():
 baseline=ROOT.parent/'black-ledger-final-read-fix-001/tools/BlackLedger/build/package-001/bundle'
 master=TASK/'build/licensed-master-002/TheLastMeridian.esp';world=TASK/'build/licensed-world-002/TLMWorldSlice.esp'
 result={n:preservation(path,baseline/n,n=='TheLastMeridian.esp')for n,path in [('TheLastMeridian.esp',master),('TLMWorldSlice.esp',world)]}
 now,names=records(master.read_bytes());get=lambda n:dict(subs(now[names[n]][1]));pose=lambda n:struct.unpack('<6f',get(n)[b'DATA'])
 layout=json.loads((TASK/'layout-placements.json').read_text(encoding='utf-8'));parents={n:get(n) for n in ('TLM_BS_ServiceRoom','TLM_BS_LowerVestibule') if n in names}
 for row in layout['placements']:
  p=pose(row['symbol']);expected=row['position']+row['rotationRadians'];assert all(abs(a-b)<.0002 for a,b in zip(p,expected)),row['symbol']
  actual=now[names[row['symbol']]];assert (b'XSCL',struct.pack('<f',row['scale'])) in subs(actual[1])
 assert pose('TLM_REF_BS_JunctionReturn')[:3]==(560,192,16)
 d=pose('TLM_REF_BS_Diagram');assert abs(d[0]-754.1392822266)<.0001 and d[1:3]==(512,128) and abs(d[4]-math.pi/2)<.00001 and abs(d[3])+abs(d[5])<.00001
 meta=json.loads((TASK/'build/licensed-master-002/blackstone-environment.json').read_text(encoding='utf-8'));assert len(meta['decor'])==96 and len(meta['papers'])==5;assert all(p['bottom']==56 for p in meta['papers']);assert meta['mara']=={'essential':False,'protectedFlag':False}
 assert get('TLM_REF_BS_ServiceDoor')[b'XLOC'][0]==255
 result.update({'passiveLiteralPoses':96,'papersAtSupport56':5,'return':[560,192,16],'diagram':{'pose':d,'declaredBasis':'CW Y; source geometry only, native front face/exposure unverified'},'pluginHashes':{'TheLastMeridian.esp':sha(master),'TLMWorldSlice.esp':sha(world)},'native':None})
 return result
if __name__=='__main__':print(json.dumps(run(),indent=2))
