"""Finite optional sound delta only; no room/runtime/native/casting requalification."""
from pathlib import Path
import sys,json,struct,hashlib,wave,unittest,copy
H=Path(__file__).resolve().parent;R=H.parents[1]
sys.path.insert(0,str(R/'tools/SheriffWorld'))
from raw import records
from vmad import vmad
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest().upper()
BASE=R.parent/'gantt-prologue-world-014/build/prologue-world-005/TLMWorldSlice.esp';OUT=R/'build/prologue-voice-world-002/TLMWorldSlice.esp'
MASTER=R.parent/'ada-book-voice-master-001/build/ada-book-master-001/TheLastMeridian.esp';WAV=R.parent/'gantt-opening-voice-001/gantt_motive_anchor.wav'
assert sha(BASE)=='BD89EFF8176015731BB02F7E3B104A48B569B044351557DD6D9057076B58D991'
assert sha(MASTER)=='B25C091E9208395B90F8D60995FE338FE62BDC26150F297373FC1B5889C083DD'
assert sha(WAV)=='DE1F1997A4CA512E8CDC179282B9152D10FE00DDABC5B5CCF3453B84AC0A53F8'
OLD,_=records(BASE);NOW,NAMES=records(OUT);MR,MN=records(MASTER)
def full(path):
 b=path.read_bytes();out={};groups=0
 def walk(at,end):
  nonlocal groups
  while at<end:
   k,n,flags,fid=struct.unpack_from('<4sIII',b,at)
   if k==b'GRUP':groups+=1;walk(at+24,at+n);at+=n
   else:out[fid]=b[at:at+24+n];at+=24+n
 walk(0,len(b));return out,groups
def verify(rows):
 assert rows.keys()==OLD.keys()|{0x2000b64}and len(rows)==870
 for fid,a in OLD.items():
  b=rows[fid]
  if fid==0:
   assert a['header']==b['header']and[(k,v)for k,v in a['ordered']if k!=b'HEDR']==[(k,v)for k,v in b['ordered']if k!=b'HEDR']
   av,ac,an=struct.unpack('<fII',a['tags'][b'HEDR']);bv,bc,bn=struct.unpack('<fII',b['tags'][b'HEDR']);assert av==bv and(ac,bc,an,bn)==(916,918,2916,2917)
  elif fid==0x2000b58:
   assert a['header'][:4]==b['header'][:4]and a['header'][8:]==b['header'][8:]and a['parents']==b['parents']
   assert[(k,v)for k,v in a['ordered']if k!=b'VMAD']==[(k,v)for k,v in b['ordered']if k!=b'VMAD']
   ah,ass,at=vmad(a['tags'][b'VMAD']);bh,bss,bt=vmad(b['tags'][b'VMAD']);assert ah==bh and at==bt and len(ass)==len(bss)==1
   assert ass[0][:2]==bss[0][:2]and bss[0][2]==ass[0][2]+[(b'RecordedGanttMotive',1,1,struct.pack('<HhI',0,-1,0x2000b64))]
  else:assert a==b,('old record changed',a['name'])
 sound=rows[0x2000b64];shape=MN['TLM_SOUND_PritchardDispatch']
 assert sound['type']=='SNDR'and sound['name']=='TLM_PROLOGUE_SOUND_GanttMotive'
 assert sound['flags']==shape['flags']and sound['parents']==shape['parents']and sound['header'][16:]==shape['header'][16:]
 assert[(k,v)for k,v in sound['ordered']if k not in(b'EDID',b'ANAM')]==[(k,v)for k,v in shape['ordered']if k not in(b'EDID',b'ANAM')]
 assert sound['tags'][b'ANAM']==b'data\\Sound\\FX\\MeridianRecordings\\gantt_motive.wav\0'and sound['tags'][b'GNAM']==struct.pack('<I',0x1000f6f)
def tag(r,k,v):r['tags'][k]=v;r['ordered']=[(a,v if a==k else b)for a,b in r['ordered']]
class Checks(unittest.TestCase):
 def test_exact_optional_delta_and_serialized_carry(self):
  verify(NOW);a,ga=full(BASE);b,gb=full(OUT);assert{k for k in a if a[k]!=b[k]}=={0,0x2000b58}and gb==ga+1==49
 def test_actual_original_clip(self):
  with wave.open(str(WAV))as f:assert(f.getnchannels(),f.getsampwidth(),f.getframerate(),f.getnframes())==(1,2,24000,126720)
 def test_wrong_soundbinding_refused(self):
  x=copy.deepcopy(NOW);r=x[0x2000b58];b=r['tags'][b'VMAD'];name=b'RecordedGanttMotive';at=b.index(name)+len(name)+2;tag(r,b'VMAD',b[:at]+struct.pack('<HhI',0,-1,0x1000f84)+b[at+8:])
  with self.assertRaises(AssertionError):verify(x)
 def test_missing_optionalbinding_refused(self):
  x=copy.deepcopy(NOW);tag(x[0x2000b58],b'VMAD',OLD[0x2000b58]['tags'][b'VMAD'])
  with self.assertRaises(AssertionError):verify(x)
 def test_wrong_wavpath_refused(self):
  x=copy.deepcopy(NOW);tag(x[0x2000b64],b'ANAM',b'data\\Sound\\FX\\MeridianRecordings\\pritchard_dispatch_case.wav\0')
  with self.assertRaises(AssertionError):verify(x)
 def test_room_or_caption_change_refused(self):
  for fid,k in[(0x2000b46,b'XCLL'),(0x2000b5a,b'DESC')]:
   x=copy.deepcopy(NOW);v=bytearray(x[fid]['tags'][k]);v[-1]^=1;tag(x[fid],k,bytes(v))
   with self.assertRaises(AssertionError):verify(x)
 def test_actor_change_refused(self):
  x=copy.deepcopy(NOW);v=bytearray(x[0x20008fe]['tags'][b'DATA']);v[4]^=1;tag(x[0x20008fe],b'DATA',bytes(v))
  with self.assertRaises(AssertionError):verify(x)
if __name__=='__main__':
 result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(Checks))
 if not result.wasSuccessful():raise SystemExit(1)
 receipt={'scope':'Private original Gantt Motive sound binding only; room/master/runtime/visual016 frozen untouched','baselineSha256':sha(BASE),'worldSha256':sha(OUT),'masterSha256':sha(MASTER),'recordCount':870,'newSound':'02000B64','newProperty':'RecordedGanttMotive','oldDelta':'OnlyTES4bookkeeping/ownprologueVMAD +1tailSNDR; allotheroldserializedrecords literalBD89','wavSource':'work/gantt-opening-voice-001/gantt_motive_anchor.wav','wavTarget':'Sound/FX/MeridianRecordings/gantt_motive.wav','wavSha256':sha(WAV),'seconds':5.28,'methods':result.testsRun,'advisory':'OriginalASR You->Youre mismatch preserved; acting/accent/nativehearingUNAPPROVED; onlyrootprivateintegrationauthorized','native':None,'sourcePins':{str(p.relative_to(R)).replace('\\','/'):sha(p)for p in[R/'tools/WorldSliceBuilder/Program.cs',R/'tools/WorldSliceBuilder/GanttPrologueVoice.cs',Path(__file__)]},'originalVoiceReceiptSha256':sha(R.parent/'gantt-opening-voice-001/receipt.json'),'originalAsrSha256':sha(R.parent/'gantt-opening-voice-001/asr-advisory.json')}
 (H/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt,indent=2))
