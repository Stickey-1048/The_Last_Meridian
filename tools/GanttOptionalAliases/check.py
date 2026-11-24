"""Finite exact three Optional flag changes after native non-optional Clear failures."""
from pathlib import Path
import sys,struct,json,hashlib,copy,unittest
H=Path(__file__).resolve().parent;R=H.parents[1]
sys.path.insert(0,str(R/'tools/SheriffWorld'))
from raw import records
BASE=R.parent/'gantt-prologue-face-light-016/build/face-light-world-001/TLMWorldSlice.esp';OUT=R/'build/optional-aliases-world-001/TLMWorldSlice.esp'
SDK=Path('F:/SteamLibrary/steamapps/common/Fallout 4/Data/Scripts/Source/Base/ReferenceAlias.psc')
LOG=R.parents[1]/'work/gantt-prologue-voiced-native-018/native-papyrus-018.log'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest().upper()
assert sha(BASE)=='7343F3B5CED7BE2E52B63F1D38759A2E0F18DCAA85951B84EE72090F7299BD82'
OLD,_=records(BASE);NOW,_=records(OUT);QID=0x2000b58
def flags(row):
 a=None;out=[]
 for k,v in row['ordered']:
  if k==b'ALST':a=struct.unpack('<I',v)[0]
  elif k==b'FNAM'and a is not None:out.append((a,struct.unpack('<I',v)[0]))
 return out
def expected_file():
 before=BASE.read_bytes();q=OLD[QID];parts=[];alias=None;changed=[]
 for k,v in q['ordered']:
  if k==b'ALST':alias=struct.unpack('<I',v)[0]
  if k==b'FNAM'and alias in[0,1,2]:
   old=struct.unpack('<I',v)[0];assert old=={0:0x80,1:0x90,2:0x80}[alias];v=struct.pack('<I',old|2);changed.append(alias)
  parts.append(struct.pack('<4sH',k,len(v))+v)
 assert changed==[0,1,2]
 at=before.index(q['header']);size=struct.unpack_from('<I',q['header'],4)[0];body=b''.join(parts);assert len(body)==size
 return before[:at]+q['header']+body+before[at+24+size:]
def verify(data):assert data==expected_file(),'wholefile must change ONLY3ownaliasFNAM Optionalbits'
class Checks(unittest.TestCase):
 def test_exact_wholefile_three_optional_flags(self):
  verify(OUT.read_bytes());assert NOW.keys()==OLD.keys()and len(NOW)==870
  assert flags(OLD[QID])==[(0,0x80),(1,0x90),(2,0x80)]and flags(NOW[QID])==[(0,0x82),(1,0x92),(2,0x82)]
  for fid,q in OLD.items():
   if fid!=QID:assert q==NOW[fid]
  assert OLD[QID]['header']==NOW[QID]['header']and OLD[QID]['parents']==NOW[QID]['parents']
  assert OLD[QID]['tags'][b'VMAD']==NOW[QID]['tags'][b'VMAD'],'all28props/aliasRoleadapters unaffected'
  assert sum(a!=b for a,b in zip(BASE.read_bytes(),OUT.read_bytes()))==3
 def test_native_failure_and_real_sdk_signature(self):
  log=LOG.read_text(errors='replace')
  for name in['ToolCase','Gantt','Departure']:assert 'error: alias '+name+' on quest TLM_OpeningPrologue (08000B58): Cannot clear a non-optional alias.'in log
  sdk=SDK.read_text();assert 'Function Clear() native'in sdk or 'Function Clear() Native'in sdk
 def test_no_alias_safety_or_ref_change(self):
  old=OLD[QID]['ordered'];new=NOW[QID]['ordered'];assert len(old)==len(new)
  for(k,a),(l,b)in zip(old,new):
   assert k==l
   if k!=b'FNAM':assert a==b
   elif a!=b:assert struct.unpack('<I',b)[0]==struct.unpack('<I',a)[0]|2
 def test_header_count_and_membership_unchanged(self):
  assert NOW[0]==OLD[0]and struct.unpack('<fII',NOW[0]['tags'][b'HEDR'])[1:]==(918,2917)
 def test_missing_one_optional_or_unrelated_change_refused(self):
  bad=BASE.read_bytes()
  with self.assertRaises(AssertionError):verify(bad)
  q=NOW[QID];b=OUT.read_bytes();at=b.index(q['header'])+24;cursor=at;alias=None
  for k,v in q['ordered']:
   if k==b'ALST':alias=struct.unpack('<I',v)[0]
   if k==b'FNAM'and alias==1:
    bad=bytearray(b);bad[cursor+6]&=0xFD
    with self.assertRaises(AssertionError):verify(bytes(bad))
    break
   cursor+=6+len(v)
  bad=bytearray(b);bad[-1]^=1
  with self.assertRaises(AssertionError):verify(bytes(bad))
if __name__=='__main__':
 result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(Checks))
 if not result.wasSuccessful():raise SystemExit(1)
 receipt={'scope':'OnlythreeownprologuealiasOptionalbits; no roof/runtime/room/actor/audiochange','baselineSha256':sha(BASE),'worldSha256':sha(OUT),'quest':'02000B58','oldFlags':flags(OLD[QID]),'newFlags':flags(NOW[QID]),'optionalBit':2,'wholeFileChangedBytes':3,'records':870,'headerUnchanged':True,'methods':result.testsRun,'nativeLogSha256':sha(LOG),'referenceAliasSdkSha256':sha(SDK),'native':'Fix targets observednativeClearfailure; newnativehandoff/actualemptyreadbackstillunproved. No Papyrus edit/compile needed for a recordflag correction.','sourcePins':{str(p.relative_to(R)).replace('\\','/'):sha(p)for p in[R/'tools/WorldSliceBuilder/GanttPrologue.cs',Path(__file__)]}}
 (H/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt,indent=2))
