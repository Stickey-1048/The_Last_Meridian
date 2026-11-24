"""Finite actual master/world/book bindings, not runtime or casting acceptance."""
from pathlib import Path
import sys,json,struct,hashlib,copy,unittest,wave
R=Path(__file__).resolve().parents[2];H=Path(__file__).resolve().parent;M=R.parent/'ada-book-voice-master-001'
sys.path.insert(0,str(R/'tools/SheriffWorld'))
from raw import records
from vmad import vmad
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest().upper()
BM=R.parent/'mercy-ada-workwear-002/build/ada-workwear-master-002/TheLastMeridian.esp'
BW=R.parent/'opening-clue-contact-006/tools/OpeningClueContact/build/contact-001/TLMWorldSlice.esp'
MP=M/'build/ada-book-master-001/TheLastMeridian.esp';WP=R/'build/ada-book-world-001/TLMWorldSlice.esp'
WAV=R.parent/'ada-opening-voice-001/ada_pikebook.wav'
assert sha(BM)=='FE1D44F9ABA0BA4EE93B25E643F63B8EB980B050AE526BD33EFD1F8608EF1BCB'
assert sha(BW)=='23F3731432DBC5FE8161AC55C1CAF458AB94A507A389E7930A411BDF8BE64C8D'
assert sha(WAV)=='AF275E763125750B0D216DB53F9646C74762E21FC774EA1957DDD036452C5BD8'
OLDM,_=records(BM);OLDW,_=records(BW);NOWM,MN=records(MP);NOWW,WN=records(WP)
ADDED={b'Alias_Pike',b'OpeningOriginalPike',b'RecordedPikeBook'}
def typed(q):return vmad(q['tags'][b'VMAD'])
def scalar(alias,fid):return struct.pack('<HhI',0,alias,fid)
def serialized(path):
 data=path.read_bytes();result={}
 def scan(a,z):
  while a<z:
   k,n,flags,fid=struct.unpack_from('<4sIII',data,a)
   if k==b'GRUP':scan(a+24,a+n);a+=n
   else:result[fid]=data[a:a+24+n];a+=24+n
 scan(0,len(data));return result
def verify_vm(before,after,own,pike):
 ah,ass,at=typed(before);bh,bss,bt=typed(after)
 assert ah==bh and at==bt and len(ass)==len(bss)==1,'VMAD header/whole alias scripts tail literal'
 assert ass[0][:2]==bss[0][:2] and bss[0][0]==b'TLM:Act1Walk'
 aps=ass[0][2];bps=bss[0][2];new=[p for p in bps if p[0]in ADDED]
 assert len(new)==3 and {p[0]for p in new}==ADDED,'exact3 optional properties'
 assert [p for p in bps if p[0]not in ADDED]==aps,'all old typed properties/order/arrays literal'
 expected={b'Alias_Pike':scalar(19,own),b'OpeningOriginalPike':scalar(-1,pike),b'RecordedPikeBook':scalar(-1,0x1000f89)}
 for name,kind,state,value in new:assert kind==state==1 and value==expected[name],('typed binding',name)
 assert [(k,v)for k,v in before['ordered']if k!=b'VMAD']==[(k,v)for k,v in after['ordered']if k!=b'VMAD'],'quest fields/objectives/alias records literal'
 assert before['header'][:4]==after['header'][:4]and before['header'][8:]==after['header'][8:]and before['parents']==after['parents'],'quest header identity/parent/flags'
def header(a,b,increment):
 assert a['header']==b['header']and a['parents']==b['parents']
 assert[(k,v)for k,v in a['ordered']if k!=b'HEDR']==[(k,v)for k,v in b['ordered']if k!=b'HEDR']
 av,ac,an=struct.unpack('<fII',a['tags'][b'HEDR']);bv,bc,bn=struct.unpack('<fII',b['tags'][b'HEDR'])
 assert bv==av and bc==ac+increment and bn==an+increment
def verify_master(rows):
 assert rows.keys()==OLDM.keys()|{0x1000f89},'one appended sound only'
 for fid,a in OLDM.items():
  b=rows[fid]
  if fid==0:header(a,b,1)
  elif fid==0x1000847:verify_vm(a,b,0x1000847,0x100088a)
  else:assert a==b,('old master record',a['name'])
 s=rows[0x1000f89];shape=rows[0x1000f84]
 assert s['type']=='SNDR'and s['name']=='TLM_SOUND_PikeBook'
 assert s['flags']==shape['flags'] and s['parents']==shape['parents'] and s['header'][16:]==shape['header'][16:]
 assert[(k,v)for k,v in s['ordered']if k not in(b'EDID',b'ANAM')]==[(k,v)for k,v in shape['ordered']if k not in(b'EDID',b'ANAM')],'entire tested sound descriptor shape/category'
 assert s['tags'][b'ANAM']==b'data\\Sound\\FX\\MeridianRecordings\\ada_pikebook.wav\0'
 assert s['tags'][b'GNAM']==struct.pack('<I',0x1000f6f)
def verify_world(rows):
 assert rows.keys()==OLDW.keys()and len(rows)==839,'no world allocation'
 for fid,a in OLDW.items():
  b=rows[fid]
  if fid==0x20008fd:verify_vm(a,b,0x20008fd,0x2000911)
  else:assert a==b,('old world record',a['name'])
 # Compare all three newly mapped properties with the actual current master.
 mp={p[0]:p for p in typed(NOWM[0x1000847])[1][0][2]if p[0]in ADDED}
 wp={p[0]:p for p in typed(rows[0x20008fd])[1][0][2]if p[0]in ADDED}
 assert wp[b'RecordedPikeBook']==mp[b'RecordedPikeBook']
 assert rows[0x2000911]['type']=='ACHR'and struct.unpack('<I',rows[0x2000911]['tags'][b'NAME'])[0]==0x100083b
def tag(r,k,v):r['tags'][k]=v;r['ordered']=[(a,v if a==k else b)for a,b in r['ordered']]
def mutate_binding(rows,qid,name,value):
 q=rows[qid];b=q['tags'][b'VMAD'];p=next(p for p in typed(q)[1][0][2]if p[0]==name);assert b.count(p[3])>=1
 at=b.index(name)+len(name)+2;tag(q,b'VMAD',b[:at]+value+b[at+8:])
class Checks(unittest.TestCase):
 def test_actual_master(self):
  verify_master(NOWM);a,b=serialized(BM),serialized(MP)
  assert{k for k in a if a[k]!=b[k]}=={0,0x1000847},'whole serialized master records'
 def test_actual_world(self):
  verify_world(NOWW);a,b=serialized(BW),serialized(WP)
  assert{k for k in a if a[k]!=b[k]}=={0x20008fd},'whole serialized world records'
 def test_actual_clip(self):
  with wave.open(str(WAV))as w:assert(w.getnchannels(),w.getsampwidth(),w.getframerate(),w.getnframes())==(1,2,24000,195840)
 def test_wrong_master_actor(self):
  x=copy.deepcopy(NOWM);mutate_binding(x,0x1000847,b'OpeningOriginalPike',scalar(-1,0x1000889))
  with self.assertRaises(AssertionError):verify_master(x)
 def test_wrong_exterior_actor(self):
  x=copy.deepcopy(NOWW);mutate_binding(x,0x20008fd,b'OpeningOriginalPike',scalar(-1,0x2000910))
  with self.assertRaises(AssertionError):verify_world(x)
 def test_unremapped_alias(self):
  x=copy.deepcopy(NOWW);mutate_binding(x,0x20008fd,b'Alias_Pike',scalar(19,0x1000847))
  with self.assertRaises(AssertionError):verify_world(x)
 def test_wrong_sound(self):
  x=copy.deepcopy(NOWW);mutate_binding(x,0x20008fd,b'RecordedPikeBook',scalar(-1,0x1000f84))
  with self.assertRaises(AssertionError):verify_world(x)
 def test_missing_property(self):
  x=copy.deepcopy(NOWW);q=x[0x20008fd];tag(q,b'VMAD',q['tags'][b'VMAD'].replace(b'RecordedPikeBook',b'RecordedPikeBad!'))
  with self.assertRaises(AssertionError):verify_world(x)
 def test_changed_terrain(self):
  x=copy.deepcopy(NOWW);q=next(q for q in x.values()if q['type']=='LAND');b=bytearray(q['tags'][b'VHGT']);b[5]^=1;tag(q,b'VHGT',bytes(b))
  with self.assertRaises(AssertionError):verify_world(x)
 def test_changed_original_ada(self):
  x=copy.deepcopy(NOWW);q=x[0x2000911];b=bytearray(q['tags'][b'DATA']);b[4]^=1;tag(q,b'DATA',bytes(b))
  with self.assertRaises(AssertionError):verify_world(x)
 def test_old_message_changed(self):
  x=copy.deepcopy(NOWM);q=next(q for q in x.values()if q['name']=='TLM_MSG_A1_PikeBook');tag(q,b'DESC',b'Changed words\0')
  with self.assertRaises(AssertionError):verify_master(x)
if __name__=='__main__':
 result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(Checks))
 if not result.wasSuccessful():raise SystemExit(1)
 receipt={'masterBaselineSha256':sha(BM),'masterSha256':sha(MP),'worldBaselineSha256':sha(BW),'worldSha256':sha(WP),'sound':'01000F89','masterPike':'0100088A','worldPike':'02000911','alias':19,'wavSha256':sha(WAV),'clipSeconds':8.16,'methods':result.testsRun,'worldRecords':len(NOWW),'masterRecords':len(NOWM),'masterDelta':'TES4 bookkeeping +3 optionalA1properties +1 tailSNDR3977; all other records literal','worldDelta':'3 optionalA1properties only; all other839record fields/IDs/groups literal','runtime':'Not edited or compiled; root-owned integration pending','status':'Internal source/artifact; both greetings HOLD, casting/native OPEN; private cap903 pose remains unpromoted','sourcePins':{str(p.relative_to(R)):sha(p)for p in[Path(__file__),R/'tools/WorldSliceBuilder/WorldStory.cs']},'masterSourcePins':{str(p.relative_to(M)):sha(p)for p in[M/'tools/PluginBuilder/Builder.cs',M/'tools/PluginBuilder/SpecAct1.cs',M/'tools/PluginBuilder/AdaBookRecording.cs',M/'tools/PluginBuilder/formkeys.txt']}}
 for folder in [H,M/'tools/AdaBookVoice']:(folder/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
 print(json.dumps(receipt,indent=2))
