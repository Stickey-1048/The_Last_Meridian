"""Independent raw three-cell/whitelist/low-grass projection. Not native art QA."""
from pathlib import Path
import sys,struct,json,math,hashlib,copy,unittest
R=Path(__file__).resolve().parents[2];HERE=Path(__file__).resolve().parent;sys.path.insert(0,str(R/'tools/SheriffWorld'))
from raw import records,pose,decode,ground,box,form
BASE=R.parent/'opening-production-finish-001/tools/OpeningProductionFinish/build/finish-002/TLMWorldSlice.esp';OUT=HERE/'build/structure-001/TLMWorldSlice.esp'
OLD,ON=records(BASE);NOW,NN=records(OUT);S=json.loads((HERE/'sculpt.json').read_text());MODELS=json.loads((HERE/'models.json').read_text())['assets'];P={p['id']:p for p in S['moved']};A={p['id']:p for p in S['added']};PATCH={(1,0),(0,1),(1,1)}
CELLS={struct.unpack_from('<ii',r['tags'][b'XCLC']):r for r in NOW.values()if r['type']=='CELL'and b'XCLC'in r['tags']};LANDS={xy:next(r for r in NOW.values()if r['type']=='LAND'and(6,c['id'])in r['parents'])for xy,c in CELLS.items()};OLDLANDS={xy:OLD[r['id']]for xy,r in LANDS.items()};HEIGHTS={xy:decode(r)for xy,r in LANDS.items()}
native,_=records(Path('C:/Program Files (x86)/GOG Galaxy/Games/Fallout 4 GOTY/Data/Fallout4.esm'),{0x3343c,0x1240f5})
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest().upper()
LEAF=NN['TLM_LTEX_OpeningLowLeafFloor'];GRASS=NN['TLM_GRAS_OpeningLowTufts'];PATCHIDS={LANDS[xy]['id']for xy in PATCH};CORE=LANDS[0,0]
def preserve(rows):
 assert len(rows)==789 and len(P)==38 and len(A)==6
 for fid,a in OLD.items():
  b=rows[fid];assert(a['type'],a['flags'],a['parents'],a['header'][16:])==(b['type'],b['flags'],b['parents'],b['header'][16:])
  if a['type']=='TES4':skip={b'HEDR'}
  elif fid in PATCHIDS:skip={b'VHGT',b'VNML',b'VTXT'}
  elif fid==CORE['id']:skip={b'ATXT',b'VTEX'}
  elif a['name']in P:skip={b'DATA'}
  elif a['name']=='TLM_WS_Opening':skip={b'DESC'}
  else:skip=set()
  assert[(k,v)for k,v in a['ordered']if k not in skip]==[(k,v)for k,v in b['ordered']if k not in skip],('unapproved old delta',a['name'],a['type'])
  if not skip:assert a['header']==b['header']
  if a['name']in P:assert pose(a)[3:]==pose(b)[3:],'passive rotations remain literal'
 assert rows[ON['TLM_WS_Opening']['id']]['tags'][b'DESC']==b"Find the marshal's dispatch beside the wreck. Follow the road uphill to Sheriff Pritchard's fenced cabin.\0"
def grass(rows):
 leaf=rows[LEAF['id']];g=rows[GRASS['id']]
 assert[(k,v)for k,v in leaf['ordered']if k not in(b'EDID',b'GNAM')]==[(k,v)for k,v in native[0x3343c]['ordered']if k not in(b'EDID',b'GNAM')],'entire stock leaf shader/material/friction'
 assert [form(v)for k,v in leaf['ordered']if k==b'GNAM']==[g['id']]
 assert[(k,v)for k,v in g['ordered']if k not in(b'EDID',b'DATA')]==[(k,v)for k,v in native[0x1240f5]['ordered']if k not in(b'EDID',b'DATA')]
 assert g['tags'][b'DATA'][0]==12 and g['tags'][b'DATA'][1:]==native[0x1240f5]['tags'][b'DATA'][1:],'only local density changes'
 nifs=json.loads((HERE/'landscape-donors.json').read_text())['assets'];assert nifs['PreWarLawnGrassObj03']['nif']['renderBounds'][5]<24
 c=rows[CORE['id']];old=OLD[CORE['id']];assert len(c['ordered'])==len(old['ordered'])
 for (k,v),(kk,vv)in zip(old['ordered'],c['ordered']):
  assert k==kk
  if k==b'ATXT'and form(v[:4])==0x3343c:assert vv==struct.pack('<I',leaf['id'])+v[4:]
  elif k==b'VTEX':assert vv==v.replace(struct.pack('<I',0x3343c),struct.pack('<I',leaf['id']))
  else:assert v==vv,'core weights/heights/normals literal'
def masks(land):
 result={};head=None
 for k,v in land['ordered']:
  if k==b'ATXT':head=struct.unpack('<IBBH',v)
  if k==b'VTXT':
   tex,q,_,layer=head;tex=0x3343c if tex==LEAF['id']else tex;assert len(v)==2312
   for i in range(289):
    n,pad,w=struct.unpack_from('<HHf',v,i*8);assert n==i and pad==0 and math.isfinite(w)and 0<=w<=1
    key=(i%17+(q&1)*16,i//17+(q>>1)*16,tex)
    if key in result:assert abs(result[key]-w)<1e-7
    result[key]=w
 return result
def seams():
 count=0
 for(x,y),h in HEIGHTS.items():
  for other,axis in[((x+1,y),0),((x,y+1),1)]:
   if other not in HEIGHTS:continue
   a=LANDS[x,y];b=LANDS[other];am,bm=masks(a),masks(b);ao,bo=masks(OLDLANDS[x,y]),masks(OLDLANDS[other])
   for i in range(33):
    ax,ay,bx,by=(32,i,0,i)if axis==0 else(i,32,i,0);assert h[ay][ax]==HEIGHTS[other][by][bx],'shared heights'
    na=a['tags'][b'VNML'][(ay*33+ax)*3:(ay*33+ax)*3+3];nb=b['tags'][b'VNML'][(by*33+bx)*3:(by*33+bx)*3+3]
    if na!=nb:assert na==OLDLANDS[x,y]['tags'][b'VNML'][(ay*33+ax)*3:(ay*33+ax)*3+3]and nb==OLDLANDS[other]['tags'][b'VNML'][(by*33+bx)*3:(by*33+bx)*3+3],'no NEW normal mismatch'
    for tex in(0x3343c,0x21336,0xc55fc):
     aa,bb=am.get((ax,ay,tex),0),bm.get((bx,by,tex),0)
     if abs(aa-bb)>1e-7:assert aa==ao.get((ax,ay,tex),0)and bb==bo.get((bx,by,tex),0),'no NEW shader-weight mismatch'
   count+=1
 assert count==17
def surface(x,y,upper=False):
 xy=math.floor(x/4096),math.floor(y/4096);h=HEIGHTS[xy];a=ground(h,x-xy[0]*4096,y-xy[1]*4096,False);b=ground(h,x-xy[0]*4096,y-xy[1]*4096,True);return max(a,b)if upper else min(a,b)
def footing(rows):
 maximum=0
 for name,p in{**P,**A}.items():
  row=next(r for r in rows.values()if r['name']==name);v=pose(row);scale=struct.unpack('<f',row['tags'][b'XSCL'])[0];a=MODELS[p['asset']];assert form(row['tags'][b'NAME'])==int(a['id'],16)
  assert all(abs(x-y)<.0003 for x,y in zip(v[:3],[p['x'],p['y'],p['z']]))and abs(scale-p['scale'])<1e-6
  xy=tuple(p['grid']);assert xy in PATCH and (6,CELLS[xy]['id'])in row['parents']
  fb=[x*scale for x in a['nif']['bottomBandBounds']];rb=box([x*scale for x in a['nif']['renderBounds']],v[:3],v[3:]);assert rb[0]>=xy[0]*4096+64 and rb[3]<=(xy[0]+1)*4096-64 and rb[1]>=xy[1]*4096+64 and rb[4]<=(xy[1]+1)*4096-64,'entire canopy outside operative core'
  low=1e9;high=-1e9;c,s=math.cos(v[5]),math.sin(v[5])
  for i in range(17):
   for j in range(17):
    x=fb[0]+(fb[3]-fb[0])*i/16;y=fb[1]+(fb[4]-fb[1])*j/16;low=min(low,surface(v[0]+x*c+y*s,v[1]+y*c-x*s));high=max(high,surface(v[0]+x*c+y*s,v[1]+y*c-x*s,True))
  assert v[2]+fb[5]<=low+.1,(name,'airgap',v[2]+fb[5]-low)
  embed=high-v[2]-fb[5];maximum=max(maximum,embed);assert embed<=64,(name,'embed',embed)
 return maximum
def normals():
 points={};anchors=set();count=0
 for xy,h in HEIGHTS.items():
  for y in range(33):
   for x in range(33):
    key=xy[0]*32+x,xy[1]*32+y;points[key]=h[y][x]
    if xy not in PATCH:anchors.add(key)
 for xy in PATCH:
  for y in range(33):
   for x in range(33):
    gx,gy=xy[0]*32+x,xy[1]*32+y
    if(gx,gy)in anchors:continue
    dx=(points.get((gx+1,gy),0)-points.get((gx-1,gy),0))/256;dy=(points.get((gx,gy+1),0)-points.get((gx,gy-1),0))/256;n=math.sqrt(1+dx*dx+dy*dy);expected=[round(-dx/n*127),round(-dy/n*127),round(1/n*127)];actual=struct.unpack_from('<3b',LANDS[xy]['tags'][b'VNML'],(y*33+x)*3);assert all(abs(a-b)<=1 for a,b in zip(actual,expected));count+=1
 return count
class Checks(unittest.TestCase):
 def test_explicit_delta_preservation(self):preserve(NOW)
 def test_low_grass_and_unchanged_core(self):grass(NOW)
 def test_all_shared_borders(self):seams()
 def test_actual_reprojected_feet(self):footing(NOW)
 def test_sculpt_masks_and_signed_readback(self):
  for row in S['cells']:
   xy=tuple(row['grid']);self.assertEqual(HEIGHTS[xy],row['heights']);m=masks(LANDS[xy])
   for y in range(33):
    for x in range(33):self.assertLessEqual(sum(m.get((x,y,t),0)for t in(0x3343c,0x21336,0xc55fc)),1.000001)
  self.assertGreater(normals(),2800)
  self.assertEqual(sorted(r['type']for fid,r in NOW.items()if fid not in OLD),['GRAS','LTEX']+['REFR']*6)
 def test_operative_actor_mutant(self):
  rows=copy.deepcopy(NOW);rows[ON['TLM_WS_ST_Pritchard']['id']]['ordered'].append((b'DATA',b'bad'))
  with self.assertRaises(AssertionError):preserve(rows)
 def test_wrong_tall_grass_mutant(self):
  rows=copy.deepcopy(NOW);rows[GRASS['id']]['tags'][b'DATA']=native[0x1240f5]['tags'][b'DATA']
  with self.assertRaises(AssertionError):grass(rows)
 def test_floating_passive_geometry_mutant(self):
  rows=copy.deepcopy(NOW);name=next(iter(P));row=rows[ON[name]['id']];v=pose(row);v[2]+=100;row['tags'][b'DATA']=struct.pack('<6f',*v);old=P[name]['z'];P[name]['z']=v[2]
  try:
   with self.assertRaises(AssertionError):footing(rows)
  finally:P[name]['z']=old
if __name__=='__main__':
 result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(Checks))
 if not result.wasSuccessful():raise SystemExit(1)
 receipt={'scope':'Three-cell original sculpt/passive whitelist/local lowGRAS, native quality OPEN','baseSource':'4de07099e251ccb4e6326f62fc784f0d7b0a75cf','baseWorldSha256':sha(BASE),'worldSha256':sha(OUT),'records':len(NOW),'changedOuterCells':[list(xy)for xy in sorted(PATCH)],'passiveWhitelist':len(P),'newOutcrops':len(A),'maxDenseFootEmbed':footing(NOW),'corePhysical':'all core heights/normals/actors/routes/QA/cabin literal; only forestLTEXpointer changes','seams':'17sharedheightedges; no newnormal/shaderweight mismatch; inheritedcore/GW conflict preserved','sourceRays':S['sourceRays'],'sculptedRays':S['sculptedRays'],'tests':result.testsRun,'native':'No install/launch; terrain rays/proxyfooting not native visual/Havok/LOD guarantee','sourcePins':{str(p.relative_to(R)).replace('\\','/'):sha(p)for p in[HERE/'sculpt.json',HERE/'make_structure.py',HERE/'landscape-donors.json',HERE/'check.py',R/'tools/WorldSliceBuilder/OpeningMountainStructure.cs',R/'tools/WorldSliceBuilder/WorldStory.cs',R/'tools/WorldSliceBuilder/Program.cs']}}
 (HERE/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print('PASS',receipt['worldSha256'],len(NOW),'maxEmbed',receipt['maxDenseFootEmbed'])
