"""Finite758-record current-master/existing-sheriff composition proof."""
from pathlib import Path
import sys,hashlib,json,struct,copy,unittest
HERE=Path(__file__).resolve().parent;R=HERE.parents[1];sys.path.insert(0,str(R/'tools/SheriffWorld'))
from raw import records,pose
from vmad import vmad
from vmad_projection import project
BASE=R.parent/'opening-scene-depth-002/tools/OpeningSceneDepth/build/scene-003/TLMWorldSlice.esp'
MASTER=R.parent/'first-act-opening-voices-009/build/opening-voices-master-002/TheLastMeridian.esp'
OLDMASTER=R.parent/'roark-depth-current-001/build/roark-current-master-002/TheLastMeridian.esp'
OUT=HERE/'build/composed-001/TLMWorldSlice.esp'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest().upper()
assert sha(BASE)=='CBB64C6FE540CC8099C933175551899BD7D4190197E8A8104917079504D08119'
assert sha(MASTER)=='E1DEBF17FA2697B8884F29037176C8EADD955E880F942DF4998F978E393F6858'
assert sha(OLDMASTER)=='350F01178F390DC33BD07A97EFE15E40F36950ED695C6FBD129A88A4DE07245F'
OLD,ON=records(BASE);NOW,NN=records(OUT);MR,MN=records(MASTER);_,OM=records(OLDMASTER)
def aliases(q):
 result={};name=None
 for k,v in q['ordered']:
  if k==b'ALID':name=v.rstrip(b'\0').decode()
  if k==b'ALFR':result[name]=struct.unpack('<I',v)[0]
 return result
SOURCE_SHERIFF=aliases(MN['TLM_A1'])['Pritchard'];EXTERIOR_SHERIFF=aliases(ON['TLM_WS_A1'])['Pritchard']
def objective_parts(q):
 rows=q['ordered'];start=next(i for i,(k,v)in enumerate(rows)if k==b'QOBJ');end=next(i for i in range(start,len(rows))if rows[i][0]in(b'ANAM',b'ALST'))
 return rows[:start],rows[start:end],rows[end:]
def props(q):return {p[0]:p for _,_,ps in vmad(q['tags'][b'VMAD'])[1]for p in ps}
def verify(rows):
 assert len(rows)==758 and rows.keys()==OLD.keys(),'exact758 membership'
 changed=[]
 for fid,a in OLD.items():
  b=rows[fid];allowed=a['name']in('TLM_WS_A1','TLM_WS_RH')
  assert(a['type'],a['flags'],a['parents'],a['header'][16:])==(b['type'],b['flags'],b['parents'],b['header'][16:]),'identity/flags/parent/header'
  if not allowed:assert a['header']==b['header']and a['ordered']==b['ordered'],('literal old record',a['name'])
  else:
   if a['name']=='TLM_WS_RH':
    ap,ao,at=objective_parts(a);bp,bo,bt=objective_parts(b)
    assert at==bt,'entire original alias records/tail'
    assert [(k,v)for k,v in ap if k!=b'VMAD']==[(k,v)for k,v in bp if k!=b'VMAD'],'RH nonVMAD/nonobjective prefix'
    assert bo==objective_parts(MN['TLM_RH'])[1],'complete exact current-master QOBJ blocks'
   else:assert[(k,v)for k,v in a['ordered']if k!=b'VMAD']==[(k,v)for k,v in b['ordered']if k!=b'VMAD'],'A1 nonVMAD literal'
  if a['ordered']!=b['ordered']:changed.append(a['name'])
 assert set(changed)=={'TLM_WS_A1','TLM_WS_RH'}
 rh=rows[ON['TLM_WS_RH']['id']];source=MN['TLM_RH']
 assert rh['tags'][b'VMAD']==project(source['tags'][b'VMAD'],source['id'],rh['id'],(SOURCE_SHERIFF,EXTERIOR_SHERIFF)),'whole current RH typed VMAD projection'
 oh,os,ot=vmad(ON['TLM_WS_RH']['tags'][b'VMAD']);nh,ns,nt=vmad(rh['tags'][b'VMAD']);assert oh==nh and ot==nt
 rp=props(rh);oldrp=props(ON['TLM_WS_RH']);assert set(rp)-set(oldrp)=={b'MineMouthKnocks',b'RecordedMineReport',b'VoiceOriginalSheriff'}
 assert all(rp[k]==v for k,v in oldrp.items()),'existing RH props/arrays'
 voice=rp[b'VoiceOriginalSheriff'];assert voice[1]==1 and struct.unpack('<HhI',voice[3])[1:]==(-1,EXTERIOR_SHERIFF)
 assert rows[EXTERIOR_SHERIFF]['type']=='ACHR'and rows[EXTERIOR_SHERIFF]['name']=='TLM_WS_ST_Pritchard'and rows[EXTERIOR_SHERIFF]['ordered']==OLD[EXTERIOR_SHERIFF]['ordered'],'original existing actor'
 # A1's established exterior transform also trims seven original source aliases
 # and marks its three guide scripts Exterior. Preserve that WHOLE accepted
 # projection, then append only the two actual current-master scalar messages.
 a1=rows[ON['TLM_WS_A1']['id']];oh,os,ot=vmad(ON['TLM_WS_A1']['tags'][b'VMAD']);nh,ns,nt=vmad(a1['tags'][b'VMAD']);assert oh==nh and ot==nt and len(os)==len(ns)==1
 mh,ms,mt=vmad(MN['TLM_A1']['tags'][b'VMAD']);bh,bs,bt=vmad(OM['TLM_A1']['tags'][b'VMAD']);assert mh==bh and mt==bt and ms[0][:2]==bs[0][:2]
 additions=[p for p in ms[0][2]if p[0]in(b'RecordedDispatchCase',b'RecordedRoadHandOff')];assert len(additions)==2
 assert [p for p in ms[0][2]if p not in additions]==bs[0][2],'entire original source A1 properties/arrays retained'
 assert ns[0][:2]==os[0][:2]and ns[0][2]==os[0][2]+additions,'complete accepted exterior A1 projection + exact2 current props'
 gw=rows[ON['TLM_WS_GW']['id']];assert gw['tags'][b'VMAD']==project(MN['TLM_GW']['tags'][b'VMAD'],MN['TLM_GW']['id'],gw['id']),'full GW current-master carry'
 return changed
def tag(r,k,v):r['tags'][k]=v;r['ordered']=[(t,v if t==k else b)for t,b in r['ordered']]
class Checks(unittest.TestCase):
 def test_complete_current_master_clone_projection(self):verify(NOW)
 def test_original_master_sheriff_not_exterior_refused(self):
  rows=copy.deepcopy(NOW);r=rows[NN['TLM_WS_RH']['id']];b=bytearray(r['tags'][b'VMAD']);at=b.index(b'VoiceOriginalSheriff')+len(b'VoiceOriginalSheriff')+6;struct.pack_into('<I',b,at,SOURCE_SHERIFF);tag(r,b'VMAD',bytes(b))
  with self.assertRaises(AssertionError):verify(rows)
 def test_different_existing_actor_refused(self):
  rows=copy.deepcopy(NOW);r=rows[NN['TLM_WS_RH']['id']];b=bytearray(r['tags'][b'VMAD']);at=b.index(b'VoiceOriginalSheriff')+len(b'VoiceOriginalSheriff')+6;struct.pack_into('<I',b,at,next(x['id']for x in rows.values()if x['type']=='ACHR'and x['id']!=EXTERIOR_SHERIFF));tag(r,b'VMAD',bytes(b))
  with self.assertRaises(AssertionError):verify(rows)
 def test_missing_new_audio_refused(self):
  rows=copy.deepcopy(NOW);r=rows[NN['TLM_WS_A1']['id']];tag(r,b'VMAD',r['tags'][b'VMAD'].replace(b'RecordedDispatchCase',b'RecordedDispatchBad!'))
  with self.assertRaises(AssertionError):verify(rows)
 def test_objective_target_refused(self):
  rows=copy.deepcopy(NOW);r=rows[NN['TLM_WS_RH']['id']];i=next(i for i,(k,v)in enumerate(r['ordered'])if k==b'QSTA');k,v=r['ordered'][i];r['ordered'][i]=(k,struct.pack('<I',0xffffffff)+v[4:])
  with self.assertRaises(AssertionError):verify(rows)
 def test_terrain_refused(self):
  rows=copy.deepcopy(NOW);r=next(r for r in rows.values()if r['type']=='LAND');b=bytearray(r['tags'][b'VHGT']);b[4]^=1;tag(r,b'VHGT',bytes(b))
  with self.assertRaises(AssertionError):verify(rows)
 def test_actor_pose_refused(self):
  rows=copy.deepcopy(NOW);r=rows[EXTERIOR_SHERIFF];p=pose(r);p[2]+=8;tag(r,b'DATA',struct.pack('<6f',*p))
  with self.assertRaises(AssertionError):verify(rows)
if __name__=='__main__':
 result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(Checks))
 if not result.wasSuccessful():raise SystemExit(1)
 receipt={'scope':'Provisional source/world composition only; pending runtime repair not carried','sourceParent':'7343ae9338ff12a722d79e96153888206c90b851','masterAndWriterSource':'91de92e6f5ee94227ec909d924cd3371b2781af7','baselineSha256':sha(BASE),'masterSha256':sha(MASTER),'outputSha256':sha(OUT),'records':758,'changedRecords':verify(NOW),'sourceSheriff':hex(SOURCE_SHERIFF),'existingExteriorSheriff':hex(EXTERIOR_SHERIFF),'RHobjectiveIDs':[int.from_bytes(v,'little')for k,v in objective_parts(NN['TLM_WS_RH'])[1]if k==b'QOBJ'],'methods':result.testsRun,'sourcePins':{str(p.relative_to(R)).replace('\\','/'):sha(p)for p in[HERE/'check.py',HERE/'vmad_projection.py',R/'tools/WorldSliceBuilder/WorldRedHollow.cs',R/'tools/WorldSliceBuilder/Program.cs',R/'tools/WorldSliceBuilder/OpeningSceneDepth.cs',R/'tools/OpeningSceneDepth/placements.json']},'native':'No stage/install/game/UI action; final runtime acceptance separate'}
 (HERE/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt,indent=2))
