"""Finite actual047 five-record inverse/coverage/packing/F32geometry regressions."""
from pathlib import Path
import geometry as g,json,struct,math,hashlib,copy,unittest
H=g.H;R=g.R;BASE=g.BASE;OUT=R/'build/visible-slope-finish-world-001/TLMWorldSlice.esp';OLD=g.OLD;NOW,NN=g.raw.records(OUT);PLAN=g.PLAN;IDS={int(v['form'],16)for v in PLAN['moves']};LAND=0x2000aaa;sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest().upper()
def mask(x,y):
 def e(cx,cy,rx,ry):
  r=math.sqrt(math.pow((x-cx)/rx,2)+math.pow((y-cy)/ry,2));t=max(0,min(1,(r-.4)/.6));return 1-t*t*(3-2*t)
 c=.85*max(e(4970,5260,480,608),.8*e(5290,4880,448,448));return c,min(c,.55*e(5140,5420,224,240))
def layers(row):
 result={};head=None
 for k,b in row['ordered']:
  if k==b'ATXT':head=struct.unpack('<IBBh',b);result[(head[1],head[0])]={'header':b,'rows':{}}
  if k==b'VTXT':
   d=result[(head[1],head[0])];d['rows']={struct.unpack_from('<H',b,j)[0]:b[j:j+8]for j in range(0,len(b),8)};assert list(d['rows'])==sorted(d['rows'])
 return result
OL,NL=layers(OLD[LAND]),layers(NOW[LAND])
def expected(key):
 result=dict(OL[key]['rows']);q,tex=key
 if q!=0:return result
 for i in range(289):
  c,r=mask(4096+(i%17)*128,4096+(i//17)*128)
  if c==0:continue
  old=struct.unpack_from('<f',result[i],4)[0]if i in result else 0;value=(1-c)*old+((c-r)if tex==0x3343c else 0)+(r if tex==0xc55f3 else 0);value=struct.unpack('<f',struct.pack('<f',value))[0]
  if value!=old:result[i]=(result[i][:4]if i in result else struct.pack('<HH',i,0))+struct.pack('<f',value)
 return result

def inverse(blob):
 original=BASE.read_bytes()
 def oldrecord(i):
  h=OLD[i]['header'];at=original.index(h);return original[at:at+24+struct.unpack_from('<I',h,4)[0]]
 def walk(at,end):
  parts=[]
  while at<end:
   h=blob[at:at+24];n=struct.unpack_from('<I',h,4)[0]
   if h[:4]==b'GRUP':
    b=walk(at+24,at+n);head=bytearray(h);struct.pack_into('<I',head,4,len(b)+24);parts.append(bytes(head)+b);at+=n
   else:
    fid=struct.unpack_from('<I',h,12)[0];parts.append(oldrecord(fid)if fid in IDS|{LAND}else blob[at:at+24+n]);at+=24+n
  assert at==end;return b''.join(parts)
 return walk(0,len(blob))
class Checks(unittest.TestCase):
 def test_01_exact_five_records_and_whole_inverse(self):
  self.assertEqual(sha(BASE),PLAN['baselineWorldSha256']);self.assertEqual(set(OLD),set(NOW));self.assertEqual(len(NOW),900);changed={i for i in OLD if OLD[i]['header']!=NOW[i]['header']or OLD[i]['ordered']!=NOW[i]['ordered']};self.assertEqual(changed,IDS|{LAND});self.assertEqual(inverse(OUT.read_bytes()),BASE.read_bytes());self.assertEqual(NOW[0],OLD[0])
 def test_02_four_actual_poses_and_original_payloads(self):
  for row in PLAN['moves']:
   i=int(row['form'],16);self.assertEqual(NOW[i]['tags'][b'DATA'],struct.pack('<6f',*row['proposedPose']));self.assertEqual(OLD[i]['header'],NOW[i]['header']);self.assertEqual(OLD[i]['parents'],NOW[i]['parents']);self.assertEqual([(k,b)for k,b in OLD[i]['ordered']if k!=b'DATA'],[(k,b)for k,b in NOW[i]['ordered']if k!=b'DATA'])
 def test_03_only_q0_vtxt_exactweight_padding_order(self):
  self.assertEqual(set(OL),set(NL));self.assertEqual([(k,b)for k,b in OLD[LAND]['ordered']if k!=b'VTXT'],[(k,b)for k,b in NOW[LAND]['ordered']if k!=b'VTXT']);self.assertEqual(OLD[LAND]['header'][8:],NOW[LAND]['header'][8:])
  for key,v in NL.items():self.assertEqual(v['rows'],expected(key));self.assertEqual(v['header'],OL[key]['header'])
 def test_04_coverage_zero_gaps_explicit_sum_and_borders(self):
  zeros=affected=0
  for i in range(289):
   c,r=mask(4096+(i%17)*128,4096+(i//17)*128);oldsum=sum(struct.unpack_from('<f',v['rows'][i],4)[0]for(q,t),v in OL.items()if q==0 and i in v['rows']);newsum=sum(struct.unpack_from('<f',v['rows'][i],4)[0]for(q,t),v in NL.items()if q==0 and i in v['rows']);self.assertAlmostEqual(newsum,oldsum+(1-oldsum)*c,places=6);self.assertLessEqual(newsum,1.000001)
   if c>0:affected+=1
   if c>0 and oldsum==0:zeros+=1;self.assertGreater(newsum,0)
   if i%17 in[0,16]or i//17 in[0,16]:self.assertEqual(c,0)
  self.assertEqual((affected,zeros),(76,10))
 def test_05_actualF32_feet_trunks_and_originalpreflight(self):
  result=g.prove(NOW);self.assertEqual(result,json.loads((H/'preflight.json').read_text()));cedar=next(v for v in result['footings']if'G2E'in v['id']);self.assertEqual(cedar['bothDiagonalCriticalPoints'],1);self.assertIn('NOT area',cedar['supportLimit'])
 def test_06_wrong_padding_and_coverage_mutants(self):
  key=(0,0x3343c);i=next(i for i,b in NL[key]['rows'].items()if i in OL[key]['rows']);bad=copy.deepcopy(NL[key]['rows']);row=bytearray(bad[i]);row[2]^=1;bad[i]=bytes(row);self.assertNotEqual(bad,expected(key))
  # The oldsum-preserving transfer fails on one actual previouslyzero vertex.
  i=next(i for i in range(289)if mask(4096+(i%17)*128,4096+(i//17)*128)[0]>0 and not any(i in v['rows']and struct.unpack_from('<f',v['rows'][i],4)[0]for(q,t),v in OL.items()if q==0));self.assertGreater(sum(struct.unpack_from('<f',v['rows'][i],4)[0]for(q,t),v in NL.items()if q==0 and i in v['rows']),0)
 def test_07_actual_raisedfoot_refused(self):
  bad=copy.deepcopy(NOW);i=next(iter(IDS));p=g.raw.pose(bad[i]);p[2]+=100;bad[i]['tags'][b'DATA']=struct.pack('<6f',*p)
  with self.assertRaises(AssertionError):g.prove(bad)
 def test_08_sourcepins_knownassets_tailhook(self):
  source=(R/'tools/WorldSliceBuilder/OpeningVisibleSlopeFinish.cs').read_text();self.assertIn(sha(H/'plan.json'),source)
  for name,v in g.MODELS.items():self.assertEqual(g.mesh.assets[name]['nif']['sha256'],v['nif']['sha256'])
  p=(R/'tools/WorldSliceBuilder/Program.cs').read_text();self.assertEqual(p.count('OpeningVisibleSlopeFinish.Apply'),1);self.assertLess(p.index('OpeningHillForestFinish.Apply'),p.index('OpeningVisibleSlopeFinish.Apply'));self.assertLess(p.index('OpeningVisibleSlopeFinish.Apply'),p.index('mod.BeginWrite.ToPath(plugin)'))
if __name__=='__main__':unittest.main(verbosity=2)
