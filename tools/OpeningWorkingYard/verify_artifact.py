"""Audit emitted scene changes and measured placement; no native/Havok claim."""
from pathlib import Path
import sys,json,struct,math,hashlib
R=Path(__file__).resolve().parents[2];H=Path(__file__).resolve().parent
sys.path.insert(0,str(R/'tools/SheriffWorld'));from raw import records,pose,form,box,decode,ground
BASE=R.parent/'opening-continuous-woodland-002/tools/OpeningContinuousWoodland/build/continuous-005/TLMWorldSlice.esp'
OUT=H/'build/yard-composed-002/TLMWorldSlice.esp'
old,on=records(BASE);now,nn=records(OUT)
f=json.loads((H/'fences.json').read_text());papers=json.loads((H/'papers.json').read_text());stations=json.loads((H/'stations.json').read_text())['props']
selected={p['name']:p for p in f['selected']};disabled={p['name']:p for p in f['disableOtherwise']};paper={p['name']:p for p in papers}
models={int(a['id'],16):a for a in json.loads((H/'models.json').read_text())['assets'].values()}
added=set(now)-set(old);assert len(old)==790 and len(now)==801 and len(added)==11 and set(old)<=set(now)
assert {now[k]['name']for k in added}=={p['id']for p in stations}
for fid,a in old.items():
 b=now[fid];name=a['name'];is_disabled=name in disabled
 assert (a['type'],a['parents'],a['header'][16:])==(b['type'],b['parents'],b['header'][16:])
 assert b['flags']==a['flags']|(0x800 if is_disabled else 0),'unapproved flags'
 skip={b'HEDR'}if fid==0 else{b'NAME',b'DATA'}if name in selected else{b'DATA'}if name in paper else set()
 assert [(k,v)for k,v in a['ordered']if k not in skip]==[(k,v)for k,v in b['ordered']if k not in skip],('unapproved field change',name)
 if name in selected:
  p=selected[name];assert pose(a)==p['oldPose'] and form(a['tags'][b'NAME'])==0x125c67 and form(b['tags'][b'NAME'])==0x118f79
  assert max(abs(x-y)for x,y in zip(pose(b),p['proposedPose']))<.001 and a['tags'][b'DATA'][12:]==b['tags'][b'DATA'][12:]
 elif name in paper:
  p=paper[name];assert pose(a)[:3]==p['oldXYZ'] and a['tags'][b'DATA'][:8]==b['tags'][b'DATA'][:8] and a['tags'][b'DATA'][12:]==b['tags'][b'DATA'][12:]
  assert abs(pose(b)[2]-p['newZ'])<.00002
 elif fid!=0:assert a['ordered']==b['ordered']
ah,bh=struct.unpack('<fII',old[0]['tags'][b'HEDR']),struct.unpack('<fII',now[0]['tags'][b'HEDR']);assert bh==(ah[0],ah[1]+11,ah[2]+11)
grids={}
for r in now.values():
 if r['type']=='CELL'and b'XCLC'in r['tags']:
  xy=struct.unpack_from('<ii',r['tags'][b'XCLC']);land=next(v for v in now.values()if v['type']=='LAND'and(6,r['id'])in v['parents']);grids[xy]=decode(land)
def height(x,y,flip=False):
 cx,cy=math.floor(x/4096),math.floor(y/4096);return ground(grids[cx,cy],x-cx*4096,y-cy*4096,flip)
for p in papers:
 r=nn[p['name']];q=pose(r);assert abs(q[2]+p['localRenderMinZ']-height(q[0],q[1])-.05)<.00002,'paper foot not on actual terrain'
sites=[pose(r)[:2]for r in old.values()if r['type']in('ACHR','REFR')and r['name'].startswith('TLM_WS_ST_')and 0<=pose(r)[0]<4096 and 0<=pose(r)[1]<4096]
def clearance(bounds):return min(math.hypot(max(bounds[0]-x,x-bounds[3],0),max(bounds[1]-y,y-bounds[4],0))for x,y in sites)
for p in selected.values():
 r=nn[p['name']];q=pose(r);m=models[0x118f79]['nif'];b=box(m['renderBounds'],q[:3],q[3:]);assert max(abs(x-y)for x,y in zip(b,p['worldBounds']))<.01
 assert clearance(b)>=128
 foot=box(m['bottomBandBounds'],q[:3],q[3:]);samples=[height(foot[0]+(foot[3]-foot[0])*i/8,foot[1]+(foot[4]-foot[1])*j/8,t)for i in range(9)for j in range(9)for t in(False,True)]
 assert foot[2]<=min(samples)+.01 and max(samples)-foot[2]<=9
for p in stations:
 r=nn[p['id']];q=pose(r);base=int(p['donorId'],16);assert r['id']in added and r['type']=='REFR' and r['flags']==0
 assert (6,0x02000802)in r['parents'] and form(r['tags'][b'NAME'])==base
 assert set(r['tags'])=={b'EDID',b'NAME',b'XSCL',b'DATA'} and struct.unpack('<f',r['tags'][b'XSCL'])[0]==1
 assert max(abs(x-y)for x,y in zip(q,p['position']+p['rotation']))<.001
 m=models[base]['nif'];assert m['sha256']==p['nifSha256']
 b=box(m['renderBounds'],q[:3],q[3:]);assert max(abs(x-y)for x,y in zip(b,p['renderBounds']))<.01
 assert clearance(p['testedBodyBounds'])>=128
# The actual clinical cot ends before the facade and leaves the96-unit doorway;
# full source model support/marker samples are preserved in the artist contract.
frame=next(p for p in stations if p['id']=='TLM_YARD_ClinicFrame')['renderBounds'];assert frame[4]<2920 and frame[3]<2896
bench=next(p for p in stations if p['id']=='TLM_YARD_RepairBench');assert bench['kind']=='FURN'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest().upper()
assert sha(BASE)=='FABEB6EB772F768408F696788C8AFADE49629768EE8F281CA0C53DB9783F3900'
receipt={'scope':'Finite artifact, measured source placement and binding preservation; not native use/collision/visual approval','baseline':sha(BASE),'world':sha(OUT),'oldRecords':len(old),'newReferences':len(added),'timberSegments':7,'retiredWhiteSegments':27,'groundedPapers':3,'oldActorControllerTerrainMaterialRecords':'literal','nativeOpen':['new scene materials/appearance','paper visibility/physics','bench/chair use and all traversal'],'sourcePins':{str(p.relative_to(R)).replace('\\','/'):sha(p)for p in[Path(__file__),H/'prepare_metadata.py',H/'fences.json',H/'papers.json',H/'stations.json',H/'models.json',R/'tools/WorldSliceBuilder/OpeningWorkingYard.cs',R/'tools/WorldSliceBuilder/Program.cs']}}
(H/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
print('PASS801records/11newrefs; exact37old-reference edits+header only; alloldactors/controllers/terrain/materials literal; paper feet, timber bounds/support, station placements/clearance and doorway screen')
