"""Finite raw seven-STAT append/decoded terrain contact and exact route/operative buffers."""
from pathlib import Path
import sys,json,hashlib,math,struct,copy,unittest
H=Path(__file__).resolve().parent;R=H.parents[1];sys.path.insert(0,str(R/'tools/SheriffWorld'))
from raw import records,pose,box,decode
sys.path.insert(0,str(H));import make_plan as m
BASE=m.BASE;OUT=R/'build/wreck-tableau-world-001/TLMWorldSlice.esp';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest().upper()
OLD,ON=records(BASE);NOW,NN=records(OUT);IDS=set(range(0x2000b78,0x2000b7f));PLAN=json.loads((H/'placements.json').read_text());MODELS=json.loads((H/'models.json').read_text())['assets'];HEIGHTS=decode(NOW[0x2000803])
def validate_pose(asset,p):
 rb=asset['nif']['renderBounds'];b=box(rb,p[:3],p[3:]);lo,hi,count=m.extents(HEIGHTS,b);bottom=p[2]+rb[2];limit=3 if asset['model'].startswith('SetDressing\\Rubble')else 10
 assert .49<=lo-bottom<=.51 and hi-bottom<=limit+.001,('footing',lo,hi,bottom,limit)
 op=min(m.pointbox(pose(NOW[i])[:2],b)for i in m.CONTROLS);rd=m.routeclear(b)
 assert op>=128 and rd>=96,('clearance',op,rd)
 return {'bounds':b,'groundMin':lo,'groundMax':hi,'minimumOperative':op,'minimumRoute':rd,'maximumBasePlaneEmbed':hi-bottom,'criticalPoints':count}
def restored(data):
 old=BASE.read_bytes();oldtes=old[:24+struct.unpack_from('<I',old,4)[0]]
 def walk(at,end):
  parts=[]
  while at<end:
   h=data[at:at+24];n=struct.unpack_from('<I',h,4)[0]
   if h[:4]==b'GRUP':
    body=walk(at+24,at+n);hh=bytearray(h);struct.pack_into('<I',hh,4,len(body)+24);parts.append(bytes(hh)+body);at+=n
   else:
    fid=struct.unpack_from('<I',h,12)[0]
    if fid not in IDS:parts.append(oldtes if fid==0 else data[at:at+24+n])
    at+=24+n
  assert at==end;return b''.join(parts)
 return walk(0,len(data))
class Checks(unittest.TestCase):
 def test_all_old_records_world_and_bindings_literal(self):
  assert set(NOW)==set(OLD)|IDS and len(NOW)==896 and restored(OUT.read_bytes())==BASE.read_bytes()
  for i,q in OLD.items():
   if i:assert NOW[i]==q,hex(i)
 def test_exact_seven_stat_refs_and_core_parent(self):
  assert len(PLAN['placements'])==7 and PLAN['baselineSha256']==sha(BASE)
  for fid,p in zip(sorted(IDS),PLAN['placements']):
   q=NOW[fid];assert q['type']=='REFR'and q['flags']==0 and q['name']==p['id']and q['parents'][-1]==(9,0x2000802)
   assert struct.unpack('<I',q['tags'][b'NAME'])[0]==int(p['donorId'],16)and b'VMAD'not in q['tags']and b'XSCL'not in q['tags']
   assert max(abs(a-b)for a,b in zip(pose(q),p['xyz']+[0,0,p['yaw']]))<1e-4
 def test_actual_serialized_footings_and_clearances(self):
  for fid,p in zip(sorted(IDS),PLAN['placements']):validate_pose(MODELS[p['asset']],pose(NOW[fid]))
 def test_selected_numeric_models_and_plan_reproduction(self):
  assert m.make()['placements']==PLAN['placements']and m.MODELS==MODELS
  original=json.loads((R/'tools/OpeningSceneDepth/models.json').read_text())['assets']
  for key,a in MODELS.items():assert a==original[key]and a['nif']['sha256']and a['nif']['renderBounds']
 def test_header_count_and_dependencies(self):
  assert struct.unpack('<fII',NOW[0]['tags'][b'HEDR'])[1:]==(944,2943)
  assert NOW[0]['header']==OLD[0]['header']and NOW[0]['tags'][b'HEDR'][:4]==OLD[0]['tags'][b'HEDR'][:4]
  assert[(k,v)for k,v in NOW[0]['ordered']if k!=b'HEDR']==[(k,v)for k,v in OLD[0]['ordered']if k!=b'HEDR']
  b=OUT.read_bytes();count=[0,0]
  def walk(at,end):
   while at<end:
    n=struct.unpack_from('<I',b,at+4)[0]
    if b[at:at+4]==b'GRUP':count[1]+=1;walk(at+24,at+n);at+=n
    else:count[0]+=1;at+=24+n
   assert at==end
  walk(0,len(b));assert count==[896,49]and sum(count)-1==944
 def test_raised_floater_blocked_clue_and_route_mutants(self):
  a=MODELS[PLAN['placements'][0]['asset']];p=pose(NOW[min(IDS)]);p[2]+=10
  with self.assertRaises(AssertionError):validate_pose(a,p)
  for x,y in[(740,1000),(1050,1133)]:
   b=m.box(a['nif']['renderBounds'],[x,y,0],[0,0,0]);lo,hi,_=m.extents(HEIGHTS,b);p=[x,y,lo-a['nif']['renderBounds'][2]-.5,0,0,0]
   with self.assertRaises(AssertionError):validate_pose(a,p)
if __name__=='__main__':
 res=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(Checks))
 if not res.wasSuccessful():raise SystemExit(1)
 numeric=[{'id':p['id'],'form':f'{fid:08X}','pose':pose(NOW[fid]),**validate_pose(MODELS[p['asset']],pose(NOW[fid]))}for fid,p in zip(sorted(IDS),PLAN['placements'])]
 rec={'scope':'Seven passive wreck cargo/timber refs only; no old record changes exceptTES4','baselineSha256':sha(BASE),'worldSha256':sha(OUT),'planSha256':sha(H/'placements.json'),'modelsSha256':sha(H/'models.json'),'majorRecords':896,'groups':49,'HEDR':944,'nextFormId':2943,'methods':res.testsRun,'placements':numeric,'sourcePins':{str(p.relative_to(R)).replace('\\','/'):sha(p)for p in[H/'make_plan.py',H/'check.py',H/'placements.json',H/'models.json',R/'tools/WorldSliceBuilder/OpeningWreckTableau.cs',R/'tools/WorldSliceBuilder/Program.cs']},'native':'UNTESTED full-render/base-plane proxies, not Havok/ordinarywalk/visualacceptance; no smoke/terrain/nav/quest/voice change'}
 (H/'receipt.json').write_text(json.dumps(rec,indent=2)+'\n');print(json.dumps({k:v for k,v in rec.items()if k not in['placements','sourcePins']},indent=2))
