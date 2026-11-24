"""Finite raw climate/paint/furnishing proof; native exposure/collision OPEN."""
from pathlib import Path
import sys,json,struct,math,hashlib,copy,unittest
R=Path(__file__).resolve().parents[2];HERE=Path(__file__).resolve().parent;sys.path.insert(0,str(R/'tools/SheriffWorld'))
from raw import records,pose,decode,ground,box,form,overlap
BASE=R.parent/'opening-final-scene-composition-001/tools/OpeningFinalScene/build/composed-001/TLMWorldSlice.esp';OUT=HERE/'build/finish-002/TLMWorldSlice.esp'
OLD,ON=records(BASE);NOW,NN=records(OUT);PLAN=json.loads((HERE/'placements.json').read_text());P={p['id']:p for p in PLAN['placements']};MODELS=json.loads((HERE/'models.json').read_text())['assets'];O=json.loads((HERE/'obstacles.json').read_text());NATIVE=Path('C:/Program Files (x86)/GOG Galaxy/Games/Fallout 4 GOTY/Data/Fallout4.esm')
native,_=records(NATIVE,{0x15f,0x560dc,0x2b52a,0x1d670e,0x1c8556,0xc55fc,0x3343c,0x21336,0x125c6c})
CORE=next(r for r in OLD.values()if r['type']=='CELL'and r['tags'].get(b'XCLC',b'')[:8]==struct.pack('<ii',0,0));LAND=next(r for r in OLD.values()if r['type']=='LAND'and(6,CORE['id'])in r['parents']);H=decode(LAND)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest().upper()
def distance(x,y,b):return math.hypot(max(b[0]-x,0,x-b[3]),max(b[1]-y,0,y-b[4]))
def segment_box(a,b,r):
 # Independent exact planar segment/AABB distance, including diagonal corners.
 ax,ay=a;bx,by=b;dx,dy=bx-ax,by-ay;lo,hi=0.,1.
 for p,q in[(-dx,ax-r[0]),(dx,r[3]-ax),(-dy,ay-r[1]),(dy,r[4]-ay)]:
  if abs(p)<1e-12:
   if q<0:lo,hi=1.,0.;break
  elif p<0:lo=max(lo,q/p)
  else:hi=min(hi,q/p)
 if lo<=hi:return 0.
 def pd(x,y):
  t=max(0,min(1,((x-ax)*dx+(y-ay)*dy)/(dx*dx+dy*dy)));return math.hypot(x-ax-t*dx,y-ay-t*dy)
 return min(distance(ax,ay,r),distance(bx,by,r),*(pd(x,y)for x in(r[0],r[3])for y in(r[1],r[4])))
def weights(row):
 out={};last=None
 for k,v in row['ordered']:
  if k==b'ATXT':last=struct.unpack('<IBBH',v);assert last[2]==0
  if k==b'VTXT':
   tex,q,_,layer=last;assert tex in(0x3343c,0x21336,0xc55fc)and layer==(0 if tex==0x3343c else 1 if tex==0x21336 else 2);assert len(v)==2312
   for i in range(289):
    ix,pad,w=struct.unpack_from('<HHf',v,i*8);assert ix==i and pad==0 and math.isfinite(w)and 0<=w<=1
    key=(i%17+(q&1)*16,i//17+(q>>1)*16,tex)
    if key in out:assert abs(out[key]-w)<1e-7
    out[key]=w
 return out
def preservation(rows):
 assert len(rows)==781 and len(P)==22
 for fid,a in OLD.items():
  b=rows[fid];assert(a['type'],a['flags'],a['parents'],a['header'][16:])==(b['type'],b['flags'],b['parents'],b['header'][16:])
  skip={b'HEDR'}if a['type']=='TES4'else{b'CNAM'}if a['type']=='WRLD'else{b'BTXT',b'ATXT',b'VTXT',b'VTEX'}if fid==LAND['id']else set()
  assert[(k,v)for k,v in a['ordered']if k not in skip]==[(k,v)for k,v in b['ordered']if k not in skip],('old payload',a['name'],a['type'])
  if not skip:assert a['header']==b['header']
 a,b=OLD[0]['tags'][b'HEDR'],rows[0]['tags'][b'HEDR'];av,ac,an=struct.unpack('<fII',a);bv,bc,bn=struct.unpack('<fII',b);assert av==bv and bc-ac==24 and bn-an==23 # one new CLMT group
def climate(rows):
 q=next(r for r in rows.values()if r['type']=='CLMT');assert q['name']=='TLM_CLMT_OpeningReadable'
 assert rows[ON['TLM_WS_Meridian']['id']]['tags'][b'CNAM']==struct.pack('<I',q['id'])
 assert[(k,v)for k,v in q['ordered']if k not in(b'EDID',b'WLST')]==[(k,v)for k,v in native[0x15f]['ordered']if k not in(b'EDID',b'WLST')],'sun/stars/timings/volatility literal native'
 b=q['tags'][b'WLST'];assert len(b)==36;actual=[struct.unpack_from('<III',b,i)for i in range(0,36,12)];assert actual==[(0x2b52a,84,0),(0x1d670e,8,0),(0x1c8556,8,0)],'exact readable whitelist; no rad/fog/rain'
 return actual
def paint(rows):
 new=rows[LAND['id']];w=weights(new);old=weights(LAND);assert sum(k==b'BTXT'for k,v in new['ordered'])==4 and sum(k==b'ATXT'for k,v in new['ordered'])==12
 assert struct.unpack('<4I',new['tags'][b'VTEX'])==(0x125c6c,0x3343c,0x21336,0xc55fc)
 for y in range(33):
  for x in range(33):
   assert sum(w[x,y,t]for t in(0x3343c,0x21336,0xc55fc))<=1.000001
   if x in(0,32)or y in(0,32):assert all(w[x,y,t]==old.get((x,y,t),0)for t in(0x3343c,0x21336,0xc55fc)),'exact old mountain/GW border'
 yard=[w[x,y,0x21336]for y in range(33)for x in range(33)if 2390<=x*128<=3740 and 2380<=y*128<=3490]
 assert sum(v>.9 for v in yard)<20 and sum(yard)/len(yard)<.55,'yard no longer full gravel rectangle'
 return {'yardSamples':len(yard),'yardGravelMean':sum(yard)/len(yard),'yardGravelAbove90Percent':sum(v>.9 for v in yard),'rockVertices':sum(w[x,y,0xc55fc]>.1 for y in range(33)for x in range(33))}
def props(rows):
 added=[r for fid,r in rows.items()if fid not in OLD and r['type']=='REFR'];assert {r['name']for r in added}==P.keys()
 boxes={};worst=0;qaMin=1e9;routeMin=1e9
 for row in added:
  p=P[row['name']];a=MODELS[p['asset']];v=pose(row);scale=struct.unpack('<f',row['tags'][b'XSCL'])[0];assert form(row['tags'][b'NAME'])==int(a['id'],16)and b'VMAD'not in row['tags']
  assert row['parents']==CORE['parents']+[(6,CORE['id']),(9,CORE['id'])]and not row['flags'];assert all(abs(x-y)<.0003 for x,y in zip(v,[p['x'],p['y'],p['z'],0,0,p['yaw']]))and abs(scale-p['scale'])<1e-6
  if p['kind']=='LIGH':assert form(row['tags'][b'NAME'])==0x560dc and struct.unpack_from('<I',native[0x560dc]['tags'][b'DATA'],4)[0]==256 and list(native[0x560dc]['tags'][b'DATA'][8:11])==[228,203,182];continue
  m=a['nif'];rb=[x*scale for x in m['renderBounds']];fb=[x*scale for x in m['bottomBandBounds']];b=box(rb,v[:3],v[3:]);boxes[row['name']]=b
  assert all(distance(q[0],q[1],b)>=128 for q in O['actors']+O['controls'])
  qaMin=min(qaMin,*(distance(x,y,b)for x,y in PLAN['qaPads']));assert all(distance(x,y,b)>=38 for x,y in PLAN['qaPads'])
  if not p.get('lowFloorCover'):
   routeMin=min(routeMin,*(segment_box(a,z,b)for route in PLAN['routes']for a,z in zip(route,route[1:])));assert routeMin>=96,'actual192-wide route/diagonal corners'
  else:assert p['support']==144 and b[5]<=148,'floor rug is low, not route obstacle'
  if p.get('wallMount'):
   assert abs(b[4]-3180)<.001 and 2668<=b[0]and b[3]<=3428 and abs(v[2]-220)<.001,'actual north-wall mounting basis'
  elif p['support']is not None:
   assert abs(v[2]+fb[2]-p['support'])<.001
   if p.get('parent'):
    parent=p['parent'];pr=next((r for r in added if r['name']==parent),None)
    if pr:
     pp=P[parent];pm=MODELS[pp['asset']]['nif'];pb=box(pm['renderBounds'],pose(pr)[:3],pose(pr)[3:]);assert abs((v[2]+fb[2])-pb[5])<.001 and pb[0]-.01<=b[0]and b[3]<=pb[3]+.01 and pb[1]-.01<=b[1]and b[4]<=pb[4]+.01,'entire shelf pickup support'
   else:assert p['support']==144 and 2664<=b[0]and b[3]<=3432 and 2672<=b[1]and b[4]<=3184,'existing full cabin floor'
  else:
   lo=1e9;hi=-1e9;c,s=math.cos(v[5]),math.sin(v[5])
   for i in range(17):
    for j in range(17):
     x=fb[0]+(fb[3]-fb[0])*i/16;y=fb[1]+(fb[4]-fb[1])*j/16
     for diagonal in(False,True):g=ground(H,v[0]+x*c+y*s,v[1]+y*c-x*s,diagonal);lo=min(lo,g);hi=max(hi,g)
   assert v[2]+fb[5]<=lo+.1 and hi-(v[2]+fb[5])<=36;worst=max(worst,hi-(v[2]+fb[5]))
  if not p.get('lowFloorCover'):
   collision=box([fb[0],fb[1],rb[2],fb[3],fb[4],rb[5]],v[:3],v[3:])if p.get('vegetation')else b
   assert not any(overlap(collision,a)for name,a in O['obstacles']if name!=p.get('parent')),'existing solid/trunk clearance'
 for name,b in boxes.items():
  for other,a in boxes.items():
   if other>=name or P[name].get('parent')==other or P[other].get('parent')==name or(P[name].get('vegetation')and P[other].get('vegetation')):continue
   assert not overlap(b,a),'new solid item overlap'
 return {'newProps':len(added),'maxDenseGroundEmbed':worst,'minimumNewPropToQAPad':qaMin,'minimumExactRouteDistance':routeMin}
class Checks(unittest.TestCase):
 def test_exact_old758_preserved_except_climate_paint(self):preservation(NOW)
 def test_readable_native_climate(self):climate(NOW)
 def test_native_material_masks_border(self):paint(NOW)
 def test_furnishing_planting_and_QA(self):props(NOW)
 def test_radstorm_mutant(self):
  rows=copy.deepcopy(NOW);q=next(r for r in rows.values()if r['type']=='CLMT');b=bytearray(q['tags'][b'WLST']);struct.pack_into('<I',b,0,0x1c3d5e);q['tags'][b'WLST']=bytes(b)
  with self.assertRaises(AssertionError):climate(rows)
 def test_old_actor_mutant(self):
  rows=copy.deepcopy(NOW);q=rows[ON['TLM_WS_ST_Pritchard']['id']];q['ordered'].append((b'DATA',b'bad'))
  with self.assertRaises(AssertionError):preservation(rows)
 def test_border_mask_mutant(self):
  rows=copy.deepcopy(NOW);q=rows[LAND['id']];i=next(i for i,(k,v)in enumerate(q['ordered'])if k==b'VTXT');k,v=q['ordered'][i];b=bytearray(v);struct.pack_into('<f',b,4,.123);q['ordered'][i]=(k,bytes(b))
  with self.assertRaises(AssertionError):paint(rows)
if __name__=='__main__':
 result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(Checks))
 if not result.wasSuccessful():raise SystemExit(1)
 receipt={'scope':'Production opening climate/paint/furnishing source+local artifact; native view OPEN','baseSource':'99fb422288e1489e4a6f913c08521a4dbdcb507d','baseWorldSha256':sha(BASE),'masterSha256':'E1DEBF17FA2697B8884F29037176C8EADD955E880F942DF4998F978E393F6858','output':'tools/OpeningProductionFinish/build/finish-002/TLMWorldSlice.esp','outputSha256':sha(OUT),'records':len(NOW),'oldRecordCount':758,'addedRefs':22,'newCLMT':1,'weatherWhitelist':climate(NOW),'materials':paint(NOW),'geometry':props(NOW),'checks':result.testsRun,'native':'Not installed/launched; ownCLMT does not prove native currentweather reset/transition; NPCwalking/Havok/light/color require rootview','sourcePins':{str(p.relative_to(R)).replace('\\','/'):sha(p)for p in[HERE/'models.json',HERE/'placements.json',HERE/'obstacles.json',HERE/'check.py',HERE/'make_plan.py',R/'tools/WorldSliceBuilder/OpeningFinish.cs',R/'tools/WorldSliceBuilder/Program.cs']}}
 (HERE/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');(HERE/'qa-relocation-carry.json').write_text(json.dumps({'scope':'Two prior QA pads retain all old geometry/heights/ref poses; new props checked above38','worldSha256':sha(OUT),'oldWorldSha256':sha(BASE),'oldProofSha256':sha(R.parent/'native-opening-audit-001/tools/NativeOpeningAudit/inputs/relocation-proof-001.json'),'pads':PLAN['qaPads'],'minimumNewPropDistance':props(NOW)['minimumNewPropToQAPad'],'physicalTerrainBytePreservation':True,'native':'Proxy capsule/OBND carry only, not navigation/Havok'},indent=2)+'\n');print(json.dumps(receipt,indent=2))

