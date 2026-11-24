"""Finite single existing light-pose correction, not native exposure acceptance."""
from pathlib import Path
import sys,hashlib,json,struct,math,copy,unittest
H=Path(__file__).resolve().parent;R=H.parents[1]
sys.path.insert(0,str(R/'tools/SheriffWorld'))
from raw import records,pose
BASE=R.parent/'gantt-prologue-voice-world-015/build/prologue-voice-world-002/TLMWorldSlice.esp';OUT=R/'build/face-light-world-001/TLMWorldSlice.esp'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest().upper()
assert sha(BASE)=='940D5B497C810E38FB38F6C2BFE8554CD2ECAA02546B41C6F509643CE12AE54A'
OLD,_=records(BASE);NOW,NAMES=records(OUT);FID=0x2000b4e
def verify(data):
 a=OLD[FID];old=struct.pack('<6f',0,180,160,0,0,0);new=struct.pack('<6f',0,20,160,0,0,0)
 assert a['name']=='TLM_PROLOGUE_WarmGanttLight'and a['tags'][b'DATA']==old
 before=BASE.read_bytes();assert before.count(old)==1
 assert data==before.replace(old,new),'wholefile must differ only by existinglight DATA.Y180to20'
def serialized_counts(data):
 major=0;groups=0
 def walk(at,end):
  nonlocal major,groups
  while at<end:
   tag,size=struct.unpack_from('<4sI',data,at)
   if tag==b'GRUP':groups+=1;walk(at+24,at+size);at+=size
   else:major+=1;at+=24+size
 walk(0,len(data));return major,groups
class Checks(unittest.TestCase):
 def test_wholefile_single_pose_float_only(self):
  verify(OUT.read_bytes());assert NOW.keys()==OLD.keys()and len(NOW)==870
  for fid,a in OLD.items():
   b=NOW[fid]
   if fid!=FID:assert a==b,(a['name'],'mustremainliteral')
   else:
    assert a['header']==b['header']and a['parents']==b['parents']
    assert[(k,v)for k,v in a['ordered']if k!=b'DATA']==[(k,v)for k,v in b['ordered']if k!=b'DATA']
    assert b['tags'][b'DATA']==a['tags'][b'DATA'][:4]+struct.pack('<f',20)+a['tags'][b'DATA'][8:]
 def test_exact_unchanged_correct_header_count(self):
  major,groups=serialized_counts(OUT.read_bytes());version,count,nextid=struct.unpack('<fII',NOW[0]['tags'][b'HEDR'])
  assert(major,groups,count,nextid)==(870,49,918,2917)and count==major-1+groups
  assert NOW[0]==OLD[0],'noTES4changepermitted'
 def test_nominal_frontal_fill_inside_room(self):
  actor=pose(NAMES['TLM_PROLOGUE_MarshalMarker']);light=pose(NOW[FID]);before=pose(OLD[FID]);assert actor[:3]==[0.,100.,16.]
  forward=(math.sin(actor[5]),math.cos(actor[5]));dot=lambda p:(p[0]-actor[0])*forward[0]+(p[1]-actor[1])*forward[1]
  assert dot(light)>79.99 and dot(before)<-79.99,'newfront/oldrear basis'
  assert abs(light[0])<100 and abs(light[1])<508 and 0<light[2]<192,'within proven room floor/roof inner volume'
  assert math.hypot(light[0]-actor[0],light[1]-actor[1])>38,'not inside nominal actorXYcapsule'
  # Diagnostic nominal head-height band, not a measured native head bone or exposure prediction.
  assert max(math.dist(light[:3],[actor[0],actor[1],z])for z in[96,144])<103<256
  assert NOW[FID]['tags'][b'NAME']==struct.pack('<I',0x560dc),'same native warm256 light, no donor edit'
 def test_old_rear_pose_refused(self):
  with self.assertRaises(AssertionError):verify(BASE.read_bytes())
 def test_other_record_or_light_axis_change_refused(self):
  b=OUT.read_bytes();poseBytes=NOW[FID]['tags'][b'DATA'];bad=struct.pack('<6f',1,20,160,0,0,0)
  with self.assertRaises(AssertionError):verify(b.replace(poseBytes,bad))
  x=bytearray(b);x[-1]^=1
  with self.assertRaises(AssertionError):verify(bytes(x))
if __name__=='__main__':
 result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(Checks))
 if not result.wasSuccessful():raise SystemExit(1)
 receipt={'scope':'Single existing Gantt warm light DATA.Y180to20 only','baselineSha256':sha(BASE),'worldSha256':sha(OUT),'ref':'02000B4E','unchangedNativeLight':'000560DC:Fallout4.esm/radius256','oldPose':pose(OLD[FID]),'newPose':pose(NOW[FID]),'counts':{'majorIncludingTES4':870,'groups':49,'HEDR':918,'nextID':2917},'methods':result.testsRun,'native':'Both actual016captures inspected: Ganttalive/roomreadable/face dark; newnativefaceilluminationNOTyetobserved. No GPU/game action. Nominalmarkerfrontlight is a source placement hypothesis, not native actor bone/collision/exposure proof.','sourcePins':{str(p.relative_to(R)).replace('\\','/'):sha(p)for p in[R/'tools/WorldSliceBuilder/GanttPrologue.cs',Path(__file__)]}}
 (H/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt,indent=2))
