"""Check the actual emitted delta, including every carried story/terrain record."""
from pathlib import Path
import hashlib,json,struct,sys,math
R=Path(__file__).resolve().parents[2]; H=Path(__file__).resolve().parent
sys.path.insert(0,str(R/'tools/SheriffWorld'))
from raw import records,pose,form,box,decode,ground
base=R.parent/'opening-working-yard-003/tools/OpeningWorkingYard/build/yard-composed-002/TLMWorldSlice.esp'
out=H/'build/density-visible-002/TLMWorldSlice.esp'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest().upper()
plan=json.loads((H/'placements.json').read_text())
assert sha(base)==plan['baselineSha256']=='CD5F78A7BF98FAEE71827D732C1292FFEE3DA4DF19A5B1D73E62B5A6F4FEB56B'
old,on=records(base); new,nn=records(out)
moves={p['id']:p for p in plan['moves']}; adds={p['id']:p for p in plan['additions']}
cells={struct.unpack_from('<ii',r['tags'][b'XCLC']):r for r in new.values()if r['type']=='CELL'and b'XCLC'in r['tags']}
assert len(old)==801 and len(new)==801+len(adds) and set(old)<=set(new)
assert {new[k]['name']for k in set(new)-set(old)}==set(adds)
for fid,a in old.items():
 b=new[fid]
 assert (a['type'],a['flags'],a['header'][16:])==(b['type'],b['flags'],b['header'][16:])
 if a['name']not in moves:assert a['parents']==b['parents']
 if fid==0:
  assert [(k,v)for k,v in a['ordered']if k!=b'HEDR']==[(k,v)for k,v in b['ordered']if k!=b'HEDR']
 elif a['name']=='TLM_GRAS_OpeningLowTufts':
  assert a['type']=='GRAS' and a['tags'][b'DATA'][0]==12 and b['tags'][b'DATA'][0]==4
  assert a['tags'][b'DATA'][1:]==b['tags'][b'DATA'][1:]
  assert [(k,v)for k,v in a['ordered']if k!=b'DATA']==[(k,v)for k,v in b['ordered']if k!=b'DATA']
 elif a['name'] in moves:
  p=moves[a['name']]
  assert a['id']&0xffffff==p['localId'] and form(a['tags'][b'NAME'])==p['baseId']
  assert pose(a)==p['oldPose'] and max(abs(x-y)for x,y in zip(pose(b),p['pose']))<.001
  cell=cells[math.floor(p['pose'][0]/4096),math.floor(p['pose'][1]/4096)]
  assert b['parents']==[(k,cell['id']if k in(6,9)else v)for k,v in a['parents']],'Moved temporary reference belongs in its actual destination cell'
  assert [(k,v)for k,v in a['ordered']if k!=b'DATA']==[(k,v)for k,v in b['ordered']if k!=b'DATA']
 else: assert a==b,('Unapproved old-record change',a['name'],a['type'])
before=struct.unpack('<fII',old[0]['tags'][b'HEDR']); after=struct.unpack('<fII',new[0]['tags'][b'HEDR'])
assert after==(before[0],before[1]+len(adds),before[2]+len(adds))
models=json.loads((H/'models.json').read_text())['assets']
grids={xy:decode(next(r for r in new.values()if r['type']=='LAND'and(6,c['id'])in r['parents']))for xy,c in cells.items()}
sites=[pose(r)[:2]for r in old.values()if r['type']in('ACHR','REFR')and r['name'].startswith('TLM_WS_ST_')]
def height(x,y,f):
 cx,cy=math.floor(x/4096),math.floor(y/4096)
 return ground(grids[cx,cy],x-cx*4096,y-cy*4096,f)
def distance(a,b):return math.hypot(max(a[0]-b[3],b[0]-a[3],0),max(a[1]-b[4],b[1]-a[4],0))
bench=json.loads((R/'tools/OpeningWorkingYard/stations.json').read_text())['benchUse']['worldAnimationMarkerBounds']
def physical_screen(p,m,q,scale):
 rb=box([v*scale for v in m['renderBounds']],q[:3],q[3:])
 fb=box([v*scale for v in m['footBounds']],q[:3],q[3:])
 samples=[height(fb[0]+(fb[3]-fb[0])*i/16,fb[1]+(fb[4]-fb[1])*j/16,f)for i in range(17)for j in range(17)for f in(False,True)]
 assert fb[2]<=min(samples)+.02 and max(samples)-fb[2]<=40.02,('foot support',p['id'])
 assert min(distance(rb,[x,y,0,x,y,0])for x,y in sites)>=127.98,('operative clearance',p['id'])
 assert distance(rb,bench)>=127.98,('repair use clearance',p['id'])
 return rb,fb
for name,p in adds.items():
 r=nn[name]; q=pose(r); m=models[p['asset']]; scale=p['scale']
 assert r['type']=='REFR' and r['flags']==0 and set(r['tags'])=={b'EDID',b'NAME',b'XSCL',b'DATA'}
 assert form(r['tags'][b'NAME'])==int(p['donorId'],16)==int(m['donorId'],16)
 assert m['model']==p['model'] and .5<=scale<=1.5
 assert max(abs(x-y)for x,y in zip(q,p['xyz']+[0,0,p['yaw']]))<.001
 assert abs(struct.unpack('<f',r['tags'][b'XSCL'])[0]-scale)<.000001
 cell=cells[math.floor(q[0]/4096),math.floor(q[1]/4096)]
 assert (6,cell['id'])in r['parents'] and (9,cell['id'])in r['parents']
 b,fb=physical_screen(p,m,q,scale)
 assert max(abs(x-y)for x,y in zip(b,p['renderBounds']))<.02
 assert max(abs(x-y)for x,y in zip(fb,p['footBounds']))<.02
for name,p in moves.items():
 r=nn[name];m=next(a for a in models.values()if int(a['donorId'],16)==p['baseId'])
 physical_screen(p,m,pose(r),struct.unpack('<f',r['tags'].get(b'XSCL',struct.pack('<f',1)))[0])
assert all(old[k]==new[k]for k in old if old[k]['type']in('ACHR','QUST','LAND','WRLD','CELL'))
prior_path=R.parent/'opening-woodland-density-004/tools/OpeningWoodlandDensity/build/density-001/TLMWorldSlice.esp'
assert sha(prior_path)=='7EEA4009F43F9AFC8BE2CB15B0F74C19B35441618DF9BED0DC536B643158132F'
prior,_=records(prior_path)
assert len(prior)==831 and set(prior)<=set(new)
assert all(prior[k]==new[k]for k in prior if k!=0),'Visible grove must carry every previous object/terrain/story record literally'
supplement=json.loads((H/'visible-placements.json').read_text())
assert supplement['baselineSha256']==sha(prior_path) and not supplement['moves']
assert len(supplement['additions'])==8 and len(new)==839
assert plan['additions'][-8:]==supplement['additions']
assert {new[k]['name']for k in set(new)-set(prior)}=={p['id']for p in supplement['additions']}
receipt={'baseline':sha(base),'world':sha(out),'oldRecordsLiteralExceptNamedPassiveMovesLocalGrassDensityAndHeader':len(old),
 'passiveMoves':list(moves),'newPassiveReferences':len(adds),'localGrassDensity':[12,4],'terrainAndStoryRecords':'literal',
 'previousWorld':sha(prior_path),'previousRecordsLiteralExceptHeader':len(prior),
 'native':'Pending actual appearance, collision and traversal; no navmesh claim',
 'sources':{str(p.relative_to(R)).replace('\\','/'):sha(p)for p in[H/'placements.json',H/'models.json',H/'measurements.json',H/'visible-placements.json',H/'visible-models.json',H/'visible-measurements.json',Path(__file__),R/'tools/WorldSliceBuilder/OpeningWoodlandDensity.cs',R/'tools/WorldSliceBuilder/Program.cs']}}
(H/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
print('PASS: actual emitted delta, preserved terrain/story, passive donor/pose/model bounds; native inspection remains required')
