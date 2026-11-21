"""Independent raw preservation screen for the Chapter4 successor (no native claims)."""
from pathlib import Path
import json,struct,sys
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'tools'))
from rh_terrain_projection import records,subs
EXTRA={'TLM_BlackLedger','TLM_BlackLedgerEntry','BlackLedgerOriginalSheriff','BlackLedgerOriginalVane','BlackLedgerOriginalHaskell'}
def trim_vmad(data):
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
   if name=='TLM:Act1Walk' and prop in EXTRA:removed.append(prop)
   else:kept.append(data[start:pos])
  result+=title+status+struct.pack('<H',len(kept))+b''.join(kept)
 result+=data[pos:]
 assert set(removed)==EXTRA and len(removed)==5,removed
 return bytes(result)
def verify(new,old,section):
 now,names=records(new);before,bnames=records(old);assert set(before)<=set(now),'Original record removed'
 assert all(names[n]==key for n,key in bnames.items()),'Old EDID/FormID changed'
 changed=[]
 for key,original in before.items():
  actual=now[key]
  if actual==original:continue
  assert actual[0]==original[0] and actual[2]==original[2],('Old flags/parent changed',key)
  if key[0]==b'TES4':
   assert [(k,v) for k,v in subs(original[1]) if k!=b'HEDR']==[(k,v) for k,v in subs(actual[1]) if k!=b'HEDR'];continue
  assert key==bnames[section],('Unrelated record payload changed',key)
  oldsub=subs(original[1]);newsub=[(k,trim_vmad(v) if k==b'VMAD' else v) for k,v in subs(actual[1])]
  assert oldsub==newsub,'Changes exceed exact five attached properties'
  changed.append(section)
 assert changed==[section],changed
 return {'oldRecords':len(before),'newRecords':len(now)-len(before),'onlyOldPayloadChange':section+' exact5 VMAD properties','allOldLandActorsAndParentsExact':True}
if __name__=='__main__':
 here=ROOT/'tools/BlackLedger/build';parent=ROOT.parent/'rh-return-account-build-f491eeb/build/licensed-return-account-skeleton-001/bundle'
 result={}
 for plugin,current,section in [('TheLastMeridian.esp','licensed-master-002','TLM_A1'),('TLMWorldSlice.esp','licensed-world-005','TLM_WS_A1')]:result[plugin]=verify((here/current/plugin).read_bytes(),(parent/plugin).read_bytes(),section)
 print(json.dumps(result,indent=2))
