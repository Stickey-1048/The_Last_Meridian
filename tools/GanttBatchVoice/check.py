"""Three optional Gantt sound bindings; exact old-world and tested descriptor-shape carry."""
from pathlib import Path
import sys,struct,json,hashlib,wave,copy,unittest
H=Path(__file__).resolve().parent;R=H.parents[1];W=R.parents[1];sys.path.insert(0,str(R/'tools/SheriffWorld'))
from raw import records
from vmad import vmad
BASE=R.parent/'first-brake-inquiry-world-023/build/first-brake-inquiry-world-001/TLMWorldSlice.esp';OUT=R/'build/gantt-batch-voice-world-001/TLMWorldSlice.esp'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest().upper()
assert sha(BASE)=='856800D4A6E97B8D8A2272FBF75D83F31D7270E2CA32992D34D707003B7D2068'
assert sha(H/'audio-map.json')=='794244B9F19CB8E43CF671B23E628A745FED482E89B3421C07AD3D0F9C395A60'
M=json.loads((H/'audio-map.json').read_text());OLD,ON=records(BASE);NOW,NN=records(OUT);QID=0x2000b58;IDS=set(range(0x2000b75,0x2000b78));OV=vmad(OLD[QID]['tags'][b'VMAD'])
def props(data):
 v=vmad(data);assert v[0]==OV[0]and v[2]==OV[2]and len(v[1])==len(OV[1])
 for(n,f,p),(on,of,op)in zip(v[1],OV[1]):
  assert(n,f)==(on,of)
  if n!=b'TLM:OpeningPrologue':assert p==op;continue
  assert len(op)==28 and len(p)==31 and p[:-3]==op
  assert p[-3:]==[(row['property'].encode(),1,1,struct.pack('<HhI',0,-1,fid))for row,fid in zip(M['lines'],sorted(IDS))]
def sounds(rows):
 donor=OLD[0x2000b64]
 for row,fid in zip(M['lines'],sorted(IDS)):
  q=rows[fid];assert q['type']=='SNDR'and q['flags']==donor['flags']and q['parents']==donor['parents']
  assert q['header'][:12]+q['header'][16:]==donor['header'][:4]+q['header'][4:8]+donor['header'][8:12]+donor['header'][16:]
  expect=[(k,('TLM_PROLOGUE_SOUND_'+row['property']).encode()+b'\0'if k==b'EDID'else row['descriptorPath'].encode()+b'\0'if k==b'ANAM'else v)for k,v in donor['ordered']]
  assert q['ordered']==expect,'All non-name/path descriptor/category/attenuation/loop/condition bytes must be exact motive'
def restored(data):
 old=BASE.read_bytes()
 def record(fid):
  h=OLD[fid]['header'];at=old.index(h);return old[at:at+24+struct.unpack_from('<I',h,4)[0]]
 def walk(at,end):
  parts=[]
  while at<end:
   h=data[at:at+24];n=struct.unpack_from('<I',h,4)[0]
   if h[:4]==b'GRUP':
    body=walk(at+24,at+n);hh=bytearray(h);struct.pack_into('<I',hh,4,len(body)+24);parts.append(bytes(hh)+body);at+=n
   else:
    fid=struct.unpack_from('<I',h,12)[0]
    if fid not in IDS:parts.append(record(fid)if fid in[0,QID]else data[at:at+24+n])
    at+=24+n
  assert at==end;return b''.join(parts)
 return walk(0,len(data))
class Checks(unittest.TestCase):
 def test_whole_old_world_except_three_props_header_literal(self):
  assert set(NOW)==set(OLD)|IDS and len(NOW)==889 and restored(OUT.read_bytes())==BASE.read_bytes()
  for fid,q in OLD.items():
   if fid not in[0,QID]:assert NOW[fid]==q,hex(fid)
  old,new=OLD[QID],NOW[QID];assert old['parents']==new['parents']and new['header'][:4]+old['header'][4:8]+new['header'][8:]==old['header']
  assert[(k,v)for k,v in old['ordered']if k!=b'VMAD']==[(k,v)for k,v in new['ordered']if k!=b'VMAD']
 def test_only_three_exact_optional_sound_props(self):props(NOW[QID]['tags'][b'VMAD'])
 def test_descriptor_shapes_category_and_safe_paths(self):
  sounds(NOW)
  for r in M['lines']:
   p=r['descriptorPath'].removeprefix('data\\').replace('\\','/');assert p.startswith('Sound/FX/MeridianRecordings/')and'..'not in p and p.endswith('.wav')
 def test_actual_wav_frames_format_text_and_eligibility_pins(self):
  assert sha(W/M['eligibilityReview']['path'])==M['eligibilityReview']['sha256']
  b=W/'work/gantt-opening-voice-batch-002';assert sha(b/'receipt.json')==M['receiptSha256']and sha(b/'asr-advisory.json')==M['asrSha256']
  rec=json.loads((b/'receipt.json').read_text(encoding='utf-8'));packet=json.loads((R/'tools/GanttPrologue/dialogue.json').read_text())
  for row in M['lines']:
   p=W/row['source'];assert sha(p)==row['sha256']
   with wave.open(str(p))as f:assert(f.getframerate(),f.getnchannels(),f.getsampwidth(),f.getnframes())==(24000,1,2,row['frames'])
   assert row['durationSeconds']==row['frames']/24000
   text=next(x['text']for x in packet['messages']if x['property']==row['message']).removeprefix('Gantt: ')
   assert next(x['text']for x in rec['lines']if x['id']==row['message'])==text
  assert M['lines'][1]['frames']==366721 and M['lines'][1]['futureConservativeSeconds']==15.281
 def test_exact_serialized_header(self):
  assert struct.unpack('<fII',NOW[0]['tags'][b'HEDR'])[1:]==(937,2936)
  assert NOW[0]['header']==OLD[0]['header']and NOW[0]['tags'][b'HEDR'][:4]==OLD[0]['tags'][b'HEDR'][:4]
  assert[(k,v)for k,v in NOW[0]['ordered']if k!=b'HEDR']==[(k,v)for k,v in OLD[0]['ordered']if k!=b'HEDR']
  b=OUT.read_bytes();count=[0,0]
  def walk(at,end):
   while at<end:
    n=struct.unpack_from('<I',b,at+4)[0]
    if b[at:at+4]==b'GRUP':count[1]+=1;walk(at+24,at+n);at+=n
    else:count[0]+=1;at+=24+n
   assert at==end
  walk(0,len(b));assert count==[889,49]and sum(count)-1==937
 def test_wrong_binding_missing_props_and_changed_shape_refused(self):
  b=NOW[QID]['tags'][b'VMAD'];obj=struct.pack('<HhI',0,-1,0x2000b76);assert b.count(obj)==1
  with self.assertRaises(AssertionError):props(b.replace(obj,struct.pack('<HhI',0,-1,0x2000b64)))
  with self.assertRaises(AssertionError):props(OLD[QID]['tags'][b'VMAD'])
  for tag,value in[(b'ANAM',b'data\\Sound\\FX\\MeridianRecordings\\gantt_motive.wav\0'),(b'GNAM',bytes(4))]:
   rows=copy.deepcopy(NOW);q=rows[0x2000b75];assert tag in q['tags'];q['ordered']=[(k,value if k==tag else v)for k,v in q['ordered']]
   with self.assertRaises(AssertionError):sounds(rows)
if __name__=='__main__':
 result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(Checks))
 if not result.wasSuccessful():raise SystemExit(1)
 rec={'scope':'Three private eligible batch002 sound descriptors+optional prologue props; no runtime/native acceptance','baselineSha256':sha(BASE),'worldSha256':sha(OUT),'mapSha256':sha(H/'audio-map.json'),'newSounds':dict(zip([r['property']for r in M['lines']],[f'{i:08X}'for i in sorted(IDS)])),'oldPrologueProperties':28,'newPrologueProperties':31,'majorRecords':889,'groups':49,'HEDR':937,'nextFormId':2936,'methods':result.testsRun,'eligibilityReview':M['eligibilityReview'],'advisory':M['advisory'],'sourcePins':{str(p.relative_to(R)).replace('\\','/'):sha(p)for p in[H/'audio-map.json',H/'check.py',R/'tools/WorldSliceBuilder/GanttBatchVoice.cs',R/'tools/WorldSliceBuilder/Program.cs']},'native':'NONE; no candidate/stage/audio playback or generation'}
 (H/'receipt.json').write_text(json.dumps(rec,indent=2)+'\n');print(json.dumps(rec,indent=2))
