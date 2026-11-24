"""Finite scriptless inquiry journal/9messages/10A1props append; raw old-world carry."""
from pathlib import Path
import struct,sys,json,hashlib,copy,unittest
H=Path(__file__).resolve().parent;R=H.parents[1];sys.path.insert(0,str(R/'tools/SheriffWorld'))
from raw import records
from vmad import vmad
BASE=R.parent/'gantt-prologue-roof-backing-020/build/roof-backing-world-001/TLMWorldSlice.esp';OUT=R/'build/first-brake-inquiry-world-001/TLMWorldSlice.esp';MASTER=R.parent/'ada-book-voice-master-001/build/ada-book-master-001/TheLastMeridian.esp'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest().upper()
assert sha(BASE)=='36E8D78D041892E60906F9356CFD19CB6182333BDA3E6BCFCD6C9CEC2024AF97'
assert sha(H/'contract.json')=='21DFB0BB760C6DAAB630E3B77FCD170BB07970AB8DA663A181E89B438F3E6EAE'
C=json.loads((H/'contract.json').read_text());OLD,ON=records(BASE);NOW,NN=records(OUT);QID=0x2000b6b;A1ID=0x20008fd;IDS=set(range(QID,QID+10));OLDVM=vmad(OLD[A1ID]['tags'][b'VMAD'])
def validate_props(data):
 v=vmad(data);assert v[0]==OLDVM[0]and v[2]==OLDVM[2]and len(v[1])==len(OLDVM[1])
 for (n,f,p),(on,of,op)in zip(v[1],OLDVM[1]):
  assert(n,f)==(on,of)
  if n!=b'TLM:Act1Walk':assert p==op;continue
  assert p[:-10]==op
  expected=[('FirstBrakeInquiry',QID)]+[(row['property'],QID+1+i)for i,row in enumerate(C['messages'])]
  assert p[-10:]==[(name.encode(),1,1,struct.pack('<HhI',0,-1,fid))for name,fid in expected]
def aliases(q):
 out=[];a=None
 for k,v in q['ordered']:
  if k==b'ALST':
   if a is not None:out.append(a)
   a={'id':struct.unpack('<I',v)[0]}
  elif a is not None and k in[b'ALID',b'FNAM',b'ALFR']:a[k.decode()]=v
 if a is not None:out.append(a)
 return out

def validate_journal(q):
 t=q['tags'];assert q['type']=='QUST'and q['flags']==0
 assert t[b'FULL'].rstrip(b'\0').decode()==C['quest']['title']and t[b'DNAM']==bytes.fromhex('00041e000000000000000000')
 assert b'VMAD'not in t and b'INDX'not in t and b'CTDA'not in t and t[b'NEXT']==b''
 aa=aliases(q);assert len(aa)==2
 for a,c,fid in zip(aa,C['quest']['aliases'],[0x2000911,0x2000910]):
  assert a=={'id':c['id'],'ALID':c['name'].encode()+b'\0','FNAM':struct.pack('<I',0x92),'ALFR':struct.pack('<I',fid)}
 objs=[];o=None
 for k,v in q['ordered']:
  if k==b'QOBJ':
   if o is not None:objs.append(o)
   o={'id':struct.unpack('<H',v)[0]}
  elif o is not None and k==b'NNAM':o['text']=v.rstrip(b'\0').decode()
  elif o is not None and k==b'QSTA':o['targetAlias']=struct.unpack('<I',v[:4])[0];assert v[4:]==bytes(8)
 if o is not None:objs.append(o)
 assert objs==C['quest']['objectives']

def validate_messages(rows):
 for i,c in enumerate(C['messages']):
  q=rows[QID+1+i];t=q['tags'];assert q['type']=='MESG'and q['flags']==0
  assert q['name']=='TLM_MSG_'+c['property']and t[b'DESC'].rstrip(b'\0').decode()==c['text']and len(c['text'])<=240
  assert [v.rstrip(b'\0').decode()for k,v in q['ordered']if k==b'ITXT']==c['buttons']
  assert t[b'DNAM']==struct.pack('<I',1)and b'CTDA'not in t and b'VMAD'not in t

def restored_file(data):
 before=BASE.read_bytes()
 def old_record(fid):
  h=OLD[fid]['header'];p=before.index(h);return before[p:p+24+struct.unpack_from('<I',h,4)[0]]
 def walk(at,end):
  parts=[]
  while at<end:
   h=data[at:at+24];n=struct.unpack_from('<I',h,4)[0]
   if h[:4]==b'GRUP':
    body=walk(at+24,at+n);hh=bytearray(h);struct.pack_into('<I',hh,4,len(body)+24);parts.append(bytes(hh)+body);at+=n
   else:
    fid=struct.unpack_from('<I',h,12)[0]
    if fid not in IDS:parts.append(old_record(fid)if fid in[0,A1ID]else data[at:at+24+n])
    at+=24+n
  assert at==end;return b''.join(parts)
 return walk(0,len(data))
class Checks(unittest.TestCase):
 def test_full_world_finite_carry(self):
  assert set(NOW)==set(OLD)|IDS and len(NOW)==886 and restored_file(OUT.read_bytes())==BASE.read_bytes()
  for fid,q in OLD.items():
   if fid not in[0,A1ID]:assert q==NOW[fid],hex(fid)
  q=copy.deepcopy(NOW[A1ID]);q['tags'][b'VMAD']=OLD[A1ID]['tags'][b'VMAD'];assert[(k,v)for k,v in q['ordered']if k!=b'VMAD']==[(k,v)for k,v in OLD[A1ID]['ordered']if k!=b'VMAD']
  assert q['parents']==OLD[A1ID]['parents']and q['flags']==OLD[A1ID]['flags']
  nh=NOW[A1ID]['header'];oh=OLD[A1ID]['header'];assert nh[:4]+oh[4:8]+nh[8:]==oh
 def test_ten_typed_props_old_alias_tail_literal(self):validate_props(NOW[A1ID]['tags'][b'VMAD'])
 def test_scriptless_non_autostart_journal_and_original_actors(self):
  validate_journal(NOW[QID]);aa=aliases(OLD[A1ID])
  for aliasId,fid in[(19,0x2000911),(18,0x2000910)]:assert next(a for a in aa if a['id']==aliasId)['ALFR']==struct.pack('<I',fid)
 def test_exact_nine_messages_order_and_buttons(self):validate_messages(NOW)
 def test_header_and_allocation(self):
  assert struct.unpack('<fII',NOW[0]['tags'][b'HEDR'])[1:]==(934,2933)
  assert NOW[0]['header']==OLD[0]['header']and NOW[0]['tags'][b'HEDR'][:4]==OLD[0]['tags'][b'HEDR'][:4]
  assert[(k,v)for k,v in NOW[0]['ordered']if k!=b'HEDR']==[(k,v)for k,v in OLD[0]['ordered']if k!=b'HEDR']
  b=OUT.read_bytes();count=[0,0]
  def walk(at,end):
   while at<end:
    n=struct.unpack_from('<I',b,at+4)[0]
    if b[at:at+4]==b'GRUP':count[1]+=1;walk(at+24,at+n);at+=n
    else:count[0]+=1;at+=24+n
   assert at==end
  walk(0,len(b));assert count==[886,49]and sum(count)-1==934
 def test_wrong_actor_objective_and_start_flag_refused(self):
  for key,bad in[(b'ALFR',struct.pack('<I',0x100088a)),(b'QSTA',bytes(12)),(b'DNAM',bytes.fromhex('01041e000000000000000000'))]:
   q=copy.deepcopy(NOW[QID]);hit=False;new=[]
   for k,v in q['ordered']:
    if k==key and not hit and(key!=b'QSTA'or v[0]==1):v=bad;hit=True
    new.append((k,v))
   q['ordered']=new;q['tags']={k:v for k,v in new};assert hit
   with self.assertRaises(AssertionError):validate_journal(q)
 def test_missing_or_wrong_property_and_button_refused(self):
  b=NOW[A1ID]['tags'][b'VMAD'];new=struct.pack('<HhI',0,-1,QID);assert b.count(new)==1
  with self.assertRaises(AssertionError):validate_props(b.replace(new,struct.pack('<HhI',0,-1,0x100081a)))
  with self.assertRaises(AssertionError):validate_props(OLD[A1ID]['tags'][b'VMAD'])
  rows=copy.deepcopy(NOW);q=rows[QID+1];it=[v for k,v in q['ordered']if k==b'ITXT'];q['ordered']=[(k,(it[1]if v==it[0]else it[0])if k==b'ITXT'else v)for k,v in q['ordered']]
  with self.assertRaises(AssertionError):validate_messages(rows)
if __name__=='__main__':
 res=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(Checks))
 if not res.wasSuccessful():raise SystemExit(1)
 rec={'scope':'Local scriptless inquiry journal+9messages+10existingA1props; no runtime/native claim','baselineSha256':sha(BASE),'worldSha256':sha(OUT),'masterSha256':sha(MASTER),'contractSha256':sha(H/'contract.json'),'newQuest':'02000B6B','messages':{r['property']:f'{QID+1+i:08X}'for i,r in enumerate(C['messages'])},'originalPike':'02000911','originalPritchard':'02000910','majorRecords':886,'groups':49,'HEDR':934,'nextFormId':2933,'oldVMADPropertyCount':len(OLDVM[1][0][2]),'methods':res.testsRun,'sourcePins':{str(p.relative_to(R)).replace('\\','/'):sha(p)for p in[H/'contract.json',H/'check.py',R/'tools/WorldSliceBuilder/FirstBrakeInquiry.cs',R/'tools/WorldSliceBuilder/Program.cs']},'native':'UNTESTED; requires compatible separately reviewed runtime023, no candidate/staging/install'}
 (H/'receipt.json').write_text(json.dumps(rec,indent=2)+'\n');print(json.dumps(rec,indent=2))
