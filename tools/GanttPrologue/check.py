"""Finite existing-world carry/new contained scene proof, not playable/native certification."""
from pathlib import Path
import sys,json,struct,hashlib,unittest,subprocess,copy
H=Path(__file__).resolve().parent;R=H.parents[1]
sys.path.insert(0,str(R/'tools/SheriffWorld'))
from raw import records,pose
from vmad import vmad
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest().upper()
BASE=R.parent/'ada-book-voice-world-001/build/ada-book-world-001/TLMWorldSlice.esp';OUT=R/'build/prologue-world-005/TLMWorldSlice.esp'
MASTER=R.parent/'ada-book-voice-master-001/build/ada-book-master-001/TheLastMeridian.esp'
assert sha(BASE)=='8798E71A216CCD75426ED203F2287837DCCEF34A42EF9B9B81992F3FC22F3611'and sha(MASTER)=='B25C091E9208395B90F8D60995FE338FE62BDC26150F297373FC1B5889C083DD'
OLD,_=records(BASE);NOW,NAMES=records(OUT);COPY=json.loads((H/'dialogue.json').read_text());ROOM=json.loads((H/'room-metadata.json').read_text())
assert sha(H/'dialogue.json')=='B6D14D09CC926040E24CB5E4883AEC37C4BBD5988DE0EDC80CA7F4BCF77DA12B'
def serialized(path):
 b=path.read_bytes();out={}
 def scan(at,end):
  while at<end:
   k,n,flags,fid=struct.unpack_from('<4sIII',b,at)
   if k==b'GRUP':scan(at+24,at+n);at+=n
   else:out[fid]=b[at:at+24+n];at+=24+n
 scan(0,len(b));return out
def groups(path):
 b=path.read_bytes();count=0
 def scan(at,end):
  nonlocal count
  while at<end:
   k,n=struct.unpack_from('<4sI',b,at)
   if k==b'GRUP':count+=1;scan(at+24,at+n);at+=n
   else:at+=24+n
 scan(0,len(b));return count
def verify(rows):
 assert len(rows)==869 and set(rows)-set(OLD)==set(range(0x2000b46,0x2000b64)),'exact30tail membership'
 for fid,a in OLD.items():
  b=rows[fid]
  if fid==0:
   assert a['header']==b['header']
   assert[(k,v)for k,v in a['ordered']if k!=b'HEDR']==[(k,v)for k,v in b['ordered']if k!=b'HEDR']
   av,ac,an=struct.unpack('<fII',a['tags'][b'HEDR']);bv,bc,bn=struct.unpack('<fII',b['tags'][b'HEDR']);assert av==bv and bn==an+30
   assert(ac,len(OLD),groups(BASE))==(884,839,42),'frozen inherited count discrepancy remains disclosed'
   assert bc==len(rows)-1+groups(OUT)==916 and groups(OUT)==groups(BASE)+6,'new exact serialized record/group count'
  else:assert a==b,('old world record changed',a['name'])
 q=rows[0x2000b58];h,ss,tail=vmad(q['tags'][b'VMAD']);assert h==(6,2)and len(ss)==1 and ss[0][0]==b'TLM:OpeningPrologue'
 props={n.decode():(k,f,v)for n,k,f,v in ss[0][2]};assert len(props)==27
 expected={'Preview':0x1000847,'MainQuest':0x100081a,'SideQuest':0x100081b,'Section':0x20008fd,'WreckEntry':NAMES['TLM_WS_Entry']['id'],'CarriageCell':0x2000b46,'WreckCell':0x2000802,'WreckWorld':0x2000800,'OriginalMarshal':0x20008fe,'SceneArrival':0x2000b54,'SceneMarshalMarker':0x2000b55,'ToolCase':0x2000b52,'ToolCaseSecuredMarker':0x2000b56,'DepartureControl':0x2000b53,'WreckMarshalMarker':0x2000b57,'WreckArrival':0x2000804}
 expected.update({x['property']:0x2000b59+i for i,x in enumerate(COPY['messages'])})
 assert set(props)==set(expected)
 for name,fid in expected.items():assert props[name]==(1,1,struct.pack('<HhI',0,-1,fid)),('binding',name)
 # Consume the entire VMAD fragment/alias tail: exact owned quest, exact adapter/Role per alias.
 at=0
 def take(n):
  nonlocal at
  b=tail[at:at+n];at+=n;assert len(b)==n;return b
 def string():return take(struct.unpack('<H',take(2))[0])
 assert take(3)==b'\x03\x00\x00'and string()==b''and struct.unpack('<H',take(2))[0]==3
 for alias,role in[(0,1),(1,2),(2,3)]:
  assert struct.unpack('<HhI',take(8))==(0,alias,q['id'])
  assert struct.unpack('<HHH',take(6))==(6,2,1)and string()==b'TLM:OpeningPrologueInteract'
  assert take(1)==b'\0'and struct.unpack('<H',take(2))[0]==1
  assert string()==b'Role'and take(2)==b'\x03\x01'and struct.unpack('<i',take(4))[0]==role
 assert at==len(tail),'entire three alias scripts tail consumed'
 assert struct.unpack_from('<H',q['tags'][b'DNAM'])[0]==0x500 and b'NEXT'in q['tags'],'canonical unstartedRunOnce/no automatic startup'
 # All three alias references/flags and objective target indices, including originalGantt.
 aliases=[];a=None
 for k,v in q['ordered']:
  if k==b'ALST':a={'id':struct.unpack('<I',v)[0]};aliases.append(a)
  elif a is not None and k in(b'ALID',b'FNAM',b'ALFR'):a[k.decode()]=v
 assert[(a['id'],a['ALID'],struct.unpack('<I',a['FNAM'])[0],struct.unpack('<I',a['ALFR'])[0])for a in aliases]==[(0,b'ToolCase\0',0x80,0x2000b52),(1,b'Gantt\0',0x90,0x20008fe),(2,b'Departure\0',0x80,0x2000b53)]
 assert[struct.unpack('<H',v)[0]for k,v in q['ordered']if k==b'QOBJ']==[10,20,30]
 assert[struct.unpack_from('<I',v)[0]for k,v in q['ordered']if k==b'QSTA']==[0,1,2]
 for i,item in enumerate(COPY['messages']):
  m=rows[0x2000b59+i];assert m['type']=='MESG'and m['name']=='TLM_PROLOGUE_MSG_'+item['property']
  assert m['tags'][b'DESC'].rstrip(b'\0').decode()==item['text']and len(item['text'])<=240
  assert[v.rstrip(b'\0').decode()for k,v in m['ordered']if k==b'ITXT']==item['buttons']
 c=rows[0x2000b46];assert c['type']=='CELL'and c['name']=='TLM_PROLOGUE_Carriage'and struct.unpack('<H',c['tags'][b'DATA'])[0]==1
 assert all((r['id']in OLD or r['type']not in('NPC_','ACHR','BOOK','MISC','LAND','WRLD','NAVM','SNDR'))for r in rows.values()),'no new canonicalactor/dispatch/terrain/navmesh/voice'
 assert pose(rows[0x2000b57])==pose(rows[0x20008fe]),'wreckmarker copied final actual oldGantt pose'
 assert pose(rows[0x2000b54])==[0.,-200.,16.,0.,0.,0.]and pose(rows[0x2000b55])[:3]==[0.,100.,16.]
 assert all(rows[i]['flags']&0x400 for i in range(0x2000b52,0x2000b58)),'all new operative markers/references persistent'
def tag(row,key,value):row['tags'][key]=value;row['ordered']=[(k,value if k==key else v)for k,v in row['ordered']]
class Checks(unittest.TestCase):
 def test_exact_old_serialized_carry_and_new_contract(self):
  verify(NOW);a,b=serialized(BASE),serialized(OUT);assert{i for i in a if a[i]!=b[i]}=={0}
 def test_room_native_mesh_floor_roof_and_ports(self):
  assert len(ROOM['floorSamples'])==len(ROOM['roofSamples'])==27 and len(ROOM['sideWallSamples'])==28 and len(ROOM['endWallSamples'])==12
  assert all(abs(v[2])+abs(v[3])<1e-6 for v in ROOM['floorSamples'])
  assert all(v[2]>192 for v in ROOM['roofSamples'])
  assert all(v[2]<-70 and v[3]>70 for v in ROOM['sideWallSamples'])
  assert all(v[2]<-480 and v[3]>480 for v in ROOM['endWallSamples'])
  assert ROOM['assets']['RRBoxcar01']['nif']['blocks']['bhkNPCollisionObject']==1
 def test_proven_lighting_copy(self):
  native,_=records(Path('C:/Program Files (x86)/GOG Galaxy/Games/Fallout 4 GOTY/Data/Fallout4.esm'),{0x1f7a9,0x560dc});c=NOW[0x2000b46]
  for k in[b'XCLL',b'LTMP',b'XCIM']:assert c['tags'][k]==native[0x1f7a9]['tags'][k]
  assert all(NOW[i]['tags'][b'NAME']==struct.pack('<I',0x560dc)for i in[0x2000b4d,0x2000b4e,0x2000b4f])
 def test_new_standing_and_route_proxy_clearance(self):
  # Hull innerfloorX±100/Y±508 actualrender; exclude enclosing shell planes from propAABBs.
  props=[[-0,400,0,82,44,63],[60,-320,0,25,52,29],[-60,-430,0,25,52,55],[0,-40,0,12,25,22]]
  for x,y in[(0,-200),(0,100),(0,-120)]:
   assert abs(x)+38<100 and abs(y)+38<508
   for px,py,z,hx,hy,hz in props:assert max(abs(x-px)-hx,0)**2+max(abs(y-py)-hy,0)**2>=38**2
  # Straight carriage aisle toward Gantt passes case only after genuine secure action.
  for y in range(-200,101,10):
   for px,py,z,hx,hy,hz in props[:3]:assert max(abs(px)-hx,0)**2+max(abs(y-py)-hy,0)**2>=38**2
 def test_wrong_originalGantt_refused(self):
  rows=copy.deepcopy(NOW);q=rows[0x2000b58];b=q['tags'][b'VMAD'];name=b'OriginalMarshal';at=b.index(name)+len(name)+2;tag(q,b'VMAD',b[:at]+struct.pack('<HhI',0,-1,0x2000911)+b[at+8:])
  with self.assertRaises(AssertionError):verify(rows)
 def test_old_dispatch_or_terrain_change_refused(self):
  for fid,k in[(0x20008ff,b'DATA'),(0x2000803,b'VHGT')]:
   rows=copy.deepcopy(NOW);q=rows[fid];b=bytearray(q['tags'][k]);b[-1]^=1;tag(q,k,bytes(b))
   with self.assertRaises(AssertionError):verify(rows)
 def test_actual_CSharp_cell_guard_refuses_other_interiors(self):
  dll=R/'tools/WorldSliceBuilder/bin/Debug/net8.0/WorldSliceBuilder.dll'
  for damage in['none','extra-cell','fair-cell','wrong-carriage-id']:
   p=subprocess.run(['dotnet',str(dll),'--prologue-cell-guard-check',str(OUT),damage],capture_output=True,text=True);assert p.returncode==0,(damage,p.stdout,p.stderr)
 def test_old_entry_and_clue_scripts_untouched(self):
  assert subprocess.check_output(['git','diff','--name-only','7717dc59','--','scripts'],cwd=R,text=True)==''
  assert NOW[NAMES['TLM_WS_Entry']['id']]==OLD[NAMES['TLM_WS_Entry']['id']]
 def test_only_new_header_normalized(self):
  old=R/'build/prologue-world-004/TLMWorldSlice.esp';proof=json.loads((OUT.parent/'prologue-header-normalization.json').read_text());a=old.read_bytes();b=OUT.read_bytes();at=proof['countByteOffset']
  assert sha(old)==proof['beforeSha256']and sha(OUT)==proof['afterSha256']
  assert(proof['emitted'],proof['normalized'],proof['majorIncludingTES4'],proof['groups'])==(921,916,869,48)
  assert b==a[:at]+struct.pack('<I',916)+a[at+4:],'exact sole four-byte newHEDRNumRecords correction'
if __name__=='__main__':
 result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(Checks))
 if not result.wasSuccessful():raise SystemExit(1)
 review=R.parents[1]/'work/reviews/sam-gantt-opening-dialogue-014-review.md';assert sha(review)=='CCD34439C7571EF9E2F6168FF3EF2635611D0C5F397B7DE8322C4C622A6191F3'
 receipt={'scope':'Contained furnished static carriage source/world only; controller/runtime and all native acceptance separate','baseSource':'7717dc59eef534ec630682e07b239a3fe95a6b6d','masterSha256':sha(MASTER),'baselineWorldSha256':sha(BASE),'worldSha256':sha(OUT),'records':869,'appendCount':30,'oldDelta':'TES4HEDRbookkeeping only; all838other oldserializedrecords literal','newCell':'02000B46','newQuest':'02000B58','originalGantt':'020008FE/base01000840','newActors':0,'scriptProps':27,'aliasRoles':{'0':'ToolCase/Role1','1':'OriginalGantt/Role2','2':'Departure/Role3'},'copySha256':sha(H/'dialogue.json'),'editorialReviewSha256':sha(review),'meshProofSha256':sha(H/'room-metadata.json'),'methods':result.testsRun,'native':'No launch/UI/install; floorHavok/navmesh/ordinaryinteraction/hearing/movingtrainunproved','sourcePins':{str(p.relative_to(R)).replace('\\','/'):sha(p)for p in[R/'tools/WorldSliceBuilder/Program.cs',R/'tools/WorldSliceBuilder/GanttPrologue.cs',R/'tools/WorldSliceBuilder/WorldFourFlags.cs',H/'check.py',H/'probe_room.py',H/'room-metadata.json',H/'dialogue.json']}}
 (H/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt,indent=2))
