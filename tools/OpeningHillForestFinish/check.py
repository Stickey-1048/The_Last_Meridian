"""Finite042 actual-byte paint/padding/inverse/footing gate, no native claim."""
from pathlib import Path
import sys,json,struct,math,hashlib,copy,unittest,importlib.util
H=Path(__file__).resolve().parent;R=H.parents[1];sys.path.insert(0,str(R/'tools/SheriffWorld'));import raw,mesh
BASE=R.parent/'opening-private-voice-wreck-union-041/build/voice-wreck-union-041-001/TLMWorldSlice.esp';OUT=R/'build/hill-forest-finish-world-003/TLMWorldSlice.esp';OLD,ON=raw.records(BASE);NOW,NN=raw.records(OUT);PLAN=json.loads((H/'plan.json').read_text());MODELS=json.loads((H/'models.json').read_text())['assets'];IDS={int(v['form'],16)for v in PLAN['moves']};LAND=0x2000aaa;sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest().upper()
sp=importlib.util.spec_from_file_location('foot',R/'tools/OpeningRidgeSpillFinish/make_plan.py');m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);m.NEW={g:raw.decode(NOW[i])for g,i in m.LANDS.items()}
sp=importlib.util.spec_from_file_location('clear',R/'tools/OpeningWreckTableau/make_plan.py');clear=importlib.util.module_from_spec(sp);sp.loader.exec_module(clear)
def mask(x,y):
 def e(cx,cy,rx,ry):
  v=math.sqrt(math.pow((x-cx)/rx,2)+math.pow((y-cy)/ry,2));t=max(0,min(1,(v-.4)/.6));return 1-t*t*(3-2*t)
 return max(.7*e(5520,4864,640,512),.55*e(6320,5180,560,560)),max(.65*e(5600,4800,160,224),.6*e(6000,4850,192,256))
def layers(row):
 result={};head=None
 for k,b in row['ordered']:
  if k==b'ATXT':head=struct.unpack('<IBBh',b);result[(head[1],head[0])]={'header':b,'rows':{}}
  elif k==b'VTXT':
   d=result[(head[1],head[0])];d['rows']={struct.unpack_from('<H',b,j)[0]:b[j:j+8]for j in range(0,len(b),8)};assert list(d['rows'])==sorted(d['rows'])
 return result
OL=layers(OLD[LAND]);NL=layers(NOW[LAND])
def expected_layer(q,tex):
 old=OL.get((q,tex));result={}if old is None else dict(old['rows']);keys=[k for k in OL if k[0]==q]
 for i in range(289):
  f,r=mask(4096+(q&1)*2048+(i%17)*128,4096+(i//17)*128)
  if f==r==0:continue
  total=sum(struct.unpack_from('<f',OL[k]['rows'][i],4)[0]if i in OL[k]['rows']else 0 for k in keys);before=struct.unpack_from('<f',result[i],4)[0]if i in result else 0;value=(1-f)*(1-r)*before+(total*f*(1-r)if tex==0x3343c else 0)+(total*r if tex==0xc55f3 else 0);value=struct.unpack('<f',struct.pack('<f',value))[0]
  if value==before:continue
  result[i]=(result[i][:4]if i in result else struct.pack('<HH',i,0))+struct.pack('<f',value)
 return result

def inverse(blob):
 original=BASE.read_bytes()
 def oldrecord(i):
  h=OLD[i]['header'];at=original.index(h);return original[at:at+24+struct.unpack_from('<I',h,4)[0]]
 def walk(at,end):
  out=[]
  while at<end:
   h=blob[at:at+24];n=struct.unpack_from('<I',h,4)[0]
   if h[:4]==b'GRUP':
    b=walk(at+24,at+n);header=bytearray(h);struct.pack_into('<I',header,4,len(b)+24);out.append(bytes(header)+b);at+=n
   else:
    fid=struct.unpack_from('<I',h,12)[0];out.append(oldrecord(fid)if fid in IDS|{LAND}else blob[at:at+24+n]);at+=24+n
  assert at==end;return b''.join(out)
 return walk(0,len(blob))
def worldbox(b,r):
 s=struct.unpack('<f',r['tags'].get(b'XSCL',struct.pack('<f',1)))[0];p=raw.pose(r);return raw.box([v*s for v in b],p[:3],p[3:])
def footprint(row):
 r=NOW[int(row['form'],16)];model=MODELS[row['asset']];foot=worldbox(model['nif']['bottomBandBounds'],r);lo,hi,num=m.extent(foot);render=worldbox(model['nif']['renderBounds'],r);actors=[q for q in NOW.values()if q['type']=='ACHR'];op=min(clear.pointbox(raw.pose(q)[:2],render)for q in actors+[NOW[i]for i in clear.CONTROLS]);road=clear.routeclear(render)
 return {'id':r['name'],'groundMin':lo,'groundMax':hi,'wholeFootRange':hi-lo,'maximumEmbed':hi-foot[2],'topFootBelowLowGround':lo-foot[5],'footBox':foot,'renderBox':render,'bothDiagonalCriticalPoints':num,'routeGap':road,'operativeGap':op}
def lowtrunk(row,records=NOW):
 r=records[int(row['form'],16)];p=raw.pose(r);s=row['scale'];tris=mesh.fullsets[row['asset']];lo=MODELS[row['asset']]['nif']['bottomBandBounds'][2];hi=lo+128/s;vertices=[]
 for tri in tris:
  poly=[list(v)for v in tri]
  for z,sign in[(lo,1),(hi,-1)]:
   out=[]
   for a,b in zip(poly,poly[1:]+poly[:1]):
    da,db=(a[2]-z)*sign,(b[2]-z)*sign
    if da>=0:out.append(a)
    if(da>=0)!=(db>=0):out.append([a[k]+(b[k]-a[k])*da/(da-db)for k in range(3)])
   poly=out
   if not poly:break
  vertices.extend(poly)
 b=[min(v[j]for v in vertices)for j in range(3)]+[max(v[j]for v in vertices)for j in range(3)];return worldbox(b,r)
class Checks(unittest.TestCase):
 def test_01_membership_five_records_wholeinverse(self):
  self.assertEqual(sha(BASE),PLAN['baselineWorldSha256']);self.assertEqual(set(OLD),set(NOW));self.assertEqual(len(NOW),900);changed={i for i in OLD if OLD[i]['header']!=NOW[i]['header']or OLD[i]['ordered']!=NOW[i]['ordered']};self.assertEqual(changed,IDS|{LAND});self.assertEqual(inverse(OUT.read_bytes()),BASE.read_bytes());self.assertEqual(OLD[0],NOW[0])
 def test_02_exact_four_data_scope(self):
  for row in PLAN['moves']:
   i=int(row['form'],16);self.assertEqual(NOW[i]['tags'][b'DATA'],struct.pack('<6f',*row['proposedPose']));self.assertEqual(OLD[i]['header'],NOW[i]['header']);self.assertEqual(OLD[i]['parents'],NOW[i]['parents']);self.assertEqual([(k,b)for k,b in OLD[i]['ordered']if k!=b'DATA'],[(k,b)for k,b in NOW[i]['ordered']if k!=b'DATA']);self.assertEqual(OLD[i]['tags'][b'DATA'][12:],NOW[i]['tags'][b'DATA'][12:])
 def test_03_exact_native_layers_weights_rows_padding(self):
  self.assertEqual(set(NL),set(OL)|{(0,0xc55f3),(1,0xc55f3)})
  oldheaders=[b for k,b in OLD[LAND]['ordered']if k==b'ATXT'];newheaders=[b for k,b in NOW[LAND]['ordered']if k==b'ATXT'and not(struct.unpack_from('<I',b)[0]==0xc55f3 and b[4]in[0,1])];self.assertEqual(oldheaders,newheaders);self.assertEqual(OLD[LAND]['header'][8:],NOW[LAND]['header'][8:])
  for key,layer in NL.items():
   q,tex=key
   if q not in[0,1]:self.assertEqual(layer,OL[key]);continue
   self.assertEqual(layer['rows'],expected_layer(q,tex))
   if key in OL:self.assertEqual(layer['header'],OL[key]['header'])
   else:self.assertEqual(layer['header'],struct.pack('<IBBh',0xc55f3,q,0,5 if q==0 else 4))
  # All unrelated LANDsubrecords, BTXT, normals/heights and padding remain literal.
  self.assertEqual([(k,b)for k,b in OLD[LAND]['ordered']if k not in[b'ATXT',b'VTXT']],[(k,b)for k,b in NOW[LAND]['ordered']if k not in[b'ATXT',b'VTXT']])
 def test_04_explicit_sum_implicitbase_borders_seam(self):
  oldmax=newmax=0.
  for q in[0,1]:
   for i in range(289):
    oldsum=sum(struct.unpack_from('<f',v['rows'][i],4)[0]for(k,t),v in OL.items()if k==q and i in v['rows']);newsum=sum(struct.unpack_from('<f',v['rows'][i],4)[0]for(k,t),v in NL.items()if k==q and i in v['rows']);self.assertAlmostEqual(oldsum,newsum,places=6);self.assertLessEqual(newsum,1.000001)
  for j in range(17):
   for field,label in[(OL,'old'),(NL,'new')]:
    left={t:struct.unpack_from('<f',v['rows'][j*17+16],4)[0]for(q,t),v in field.items()if q==0 and j*17+16 in v['rows']};right={t:struct.unpack_from('<f',v['rows'][j*17],4)[0]for(q,t),v in field.items()if q==1 and j*17 in v['rows']};gap=max(abs(left.get(k,0)-right.get(k,0))for k in left.keys()|right.keys())if left or right else 0
    if label=='old':oldmax=max(oldmax,gap)
    else:newmax=max(newmax,gap)
  self.assertLessEqual(newmax,oldmax+1e-6)
 def test_05_actualF32_wholefeet_and_operatives(self):
  for row in PLAN['moves']:
   v=footprint(row);self.assertLessEqual(v['wholeFootRange'],56);self.assertLessEqual(v['maximumEmbed'],64);self.assertGreaterEqual(v['topFootBelowLowGround'],2.99);self.assertGreaterEqual(v['routeGap'],96);self.assertGreaterEqual(v['operativeGap'],128)
 def test_06_lowerTrunks_clear_rockBodies(self):
  trees=[r for r in PLAN['moves']if r['asset'].startswith('Tree')];rocks=[r for r in NOW.values()if r['type']=='REFR'and raw.form(r['tags'][b'NAME'])==0x2f79b]
  for tree in trees:
   trunk=lowtrunk(tree)
   for rock in rocks:self.assertFalse(raw.overlap(trunk,worldbox(MODELS['RockBoulder03']['nif']['renderBounds'],rock)),(tree['id'],rock['name']))
 def test_07_badmaterial_scope_and_badfoot_mutants(self):
  held,_=raw.records(R/'build/hill-forest-finish-world-002/TLMWorldSlice.esp');approved=json.loads((H/'approved-plan.json').read_text())
  for tree,rock in[(approved['moves'][0],approved['moves'][2]),(approved['moves'][1],approved['moves'][3])]:self.assertTrue(raw.overlap(lowtrunk(tree,held),worldbox(MODELS['RockBoulder03']['nif']['renderBounds'],held[int(rock['form'],16)])))
  key=(0,0x3343c);bad=copy.deepcopy(NL[key]['rows']);i=next(iter(bad));bad[i]=bad[i][:4]+struct.pack('<f',1.01);self.assertNotEqual(bad,expected_layer(*key));r=copy.deepcopy(NOW[next(iter(IDS))]);r['tags'][b'DATA']=r['tags'][b'DATA'][:8]+struct.pack('<f',raw.pose(r)[2]+100)+r['tags'][b'DATA'][12:];row=next(p for p in PLAN['moves']if int(p['form'],16)==r['id']);b=worldbox(MODELS[row['asset']]['nif']['bottomBandBounds'],r);lo,hi,_=m.extent(b);self.assertLess(lo-b[5],0)
 def test_08_sourceguards_and_measured_models(self):
  s=(R/'tools/WorldSliceBuilder/OpeningHillForestFinish.cs').read_text();self.assertIn(sha(H/'plan.json'),s);self.assertIn('ReferenceEqualityComparer.Instance',s)
  for name,v in MODELS.items():self.assertEqual(mesh.assets[name]['nif']['sha256'],v['nif']['sha256'])
  p=(R/'tools/WorldSliceBuilder/Program.cs').read_text();self.assertEqual(p.count('OpeningHillForestFinish.Apply'),1);self.assertLess(p.index('OpeningWreckDerailment.Apply'),p.index('OpeningHillForestFinish.Apply'));self.assertLess(p.index('OpeningHillForestFinish.Apply'),p.index('mod.BeginWrite.ToPath(plugin)'))
if __name__=='__main__':unittest.main(verbosity=2)
