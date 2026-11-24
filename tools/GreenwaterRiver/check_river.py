"""Finite independent serialized terrain/water/control/route screen. Not native proof."""
import raw as v
import math,struct,json,collections,hashlib
OLD=v.ROOT.parents[2]/'opening-landscape-003/tools/OpeningEnvironment/build/landscape-repair-001/TLMWorldSlice.esp'
CONTROL={'Exit','RationBoard','Skiff','Table','Strongbox','FireControl','Chain','Pilot','LabelChute','LabelLanding','LabelQueen','ReliefStores'}
CARGO={'CargoWhole','CargoReduced','CargoLashed','Burnt'}
def check(rows):
 names={r['name']:r for r in rows.values()};old,_=v.records(OLD);scene=json.loads((v.OUT/'greenwater-river.json').read_text());models=json.loads((v.ROOT/'scene-models.json').read_text())['assets']
 cell=names['TLM_GWR_Cell'];assert struct.unpack('<iiI',cell['tags'][b'XCLC'])[:2]==(0,-1),'Southern grid';assert struct.unpack('<H',cell['tags'][b'DATA'])[0]==2 and struct.unpack('<f',cell['tags'][b'XCLW'])[0]==-64,'Real CELL water'
 world=names['TLM_WS_Meridian'];assert v.form(world['tags'][b'NAM2'])==0x1c358e,'Native river WATR';assert struct.unpack('<2f',world['tags'][b'NAM0'])==(0,-4096)and struct.unpack('<2f',world['tags'][b'NAM9'])==(4096,4096),'World extent'
 land=next(r for r in rows.values()if r['type']=='LAND'and any(label==cell['id']for kind,label in r['parents']));h=v.decode(land);assert all(h[0][i]==h[32][i]==h[i][0]==h[i][32]==0 for i in range(33)),'Boundary height';opening=next(r for r in old.values()if r['type']=='LAND');oh=v.decode(opening);assert h[32]==oh[0],'Opening shared edge'
 assert all(struct.unpack_from('<3b',land['tags'][b'VNML'],(y*33+x)*3)[2]>0 for y in range(33)for x in range(33)),'Normals must face up'
 for y in range(33):
  for x in range(33):
   dx=(h[y][min(x+1,32)]-h[y][max(0,x-1)])/(128 if x in(0,32)else 256);dy=(h[min(y+1,32)][x]-h[max(0,y-1)][x])/(128 if y in(0,32)else 256);length=math.sqrt(1+dx*dx+dy*dy);a=struct.unpack_from('<3b',land['tags'][b'VNML'],(y*33+x)*3);assert max(abs(a-b)for a,b in zip(a,[round(-dx/length*127),round(-dy/length*127),round(127/length)]))<=1,'Normal/height mismatch'
 dry=gentle=wet=0
 for y in range(32):
  for x in range(32):
   a,b,c,d=h[y][x],h[y][x+1],h[y+1][x],h[y+1][x+1]
   if min(a,b,c,d)>-64:
    dry+=16384
    if max(math.hypot(b-a,d-b),math.hypot(d-c,c-a),math.hypot(b-a,c-a),math.hypot(d-c,d-b))/128<=.35:gentle+=16384
   if max(a,b,c,d)<-64:wet+=16384
 assert 5.7<=gentle/(1664*768)<=7,'Usable dry gentle area outside approximate6x target'
 assert wet>2000000,'No real carved wet stream'
 # Old IDs, all original opening geometry/LAND and quests remain literal.
 moved={p['id']:p for p in scene['moved']};assert len(moved)==len(set(moved))
 for fid,r in old.items():
  n=rows[fid];assert r['parents']==n['parents'] and r['flags']==n['flags'],'Original record identity/parent/flags'
  skip={b'HEDR'}if fid==0 else {b'NAM0',b'NAM9',b'NAM2'}if r['type']=='WRLD'else {b'DATA'}if r['name']in moved else set()
  alias=r['name'].removeprefix('TLM_WS_ST_GW_')
  if alias in CONTROL|CARGO:skip|={b'NAME',b'XSCL'}
  assert [(k,b)for k,b in r['ordered']if k not in skip]==[(k,b)for k,b in n['ordered']if k not in skip],'Unapproved original record delta: '+r['name']
  if r['name']in moved:
   p=moved[r['name']];assert max(abs(a-b)for a,b in zip(v.pose(n),[p['x'],p['y'],p['z'],*v.pose(r)[3:]]))<.0001,'Emitted GW pose';assert 0<p['x']<4096 and -4096<p['y']<0,'Operative reference crossed cell'
 # Full original VTXT native weights and seamless quadrant ownership.
 weights={};pending=None;nb=na=0
 for tag,b in land['ordered']:
  if tag==b'BTXT':nb+=1;assert struct.unpack('<IBBh',b)[0]==0x125c6c,'Soil base'
  elif tag==b'ATXT':pending=struct.unpack('<IBBh',b);na+=1;assert pending[0]==(0x3343c if pending[3]==0 else 135990),'Material donor'
  elif tag==b'VTXT':
   assert len(b)==2312 and pending is not None,'Native alpha size';tex,q,pad,layer=pending
   for i in range(289):
    idx,pad,w=struct.unpack_from('<HHf',b,i*8);assert idx==i and pad==0 and math.isfinite(w)and 0<=w<=1,'Native alpha entry';key=(layer,i%17+(q&1)*16,i//17+(q>>1)*16);assert key not in weights or abs(weights[key]-w)<1e-6,'Material seam';weights[key]=w
 assert nb==4 and na==8 and len(weights)==2178,'Material membership'
 def ground(x,y,flip=False):return v.ground(h,x,y+4096,flip)
 boxes=[];floors=[];footings=[]
 for p in scene['props']:
  r=names[p['id']];a=models[p['asset']];assert v.form(r['tags'][b'NAME'])==int(a['id'],16) and max(abs(a-b)for a,b in zip(v.pose(r),[p['x'],p['y'],p['z'],0,0,p['yaw']]))<.0001,'Prop donor/pose';assert any(label==cell['id']for kind,label in r['parents']),'Prop parent'
  scale=p.get('scale',1);assert abs(struct.unpack('<f',r['tags'].get(b'XSCL',struct.pack('<f',1)))[0]-scale)<1e-6,'Prop scale';b=v.box([x*scale for x in a['nif']['renderBounds']],[p['x'],p['y'],p['z']],[0,0,p['yaw']]);boxes.append((p['id'],b))
  if p['asset']=='workshop_ShackMidFloor01B':assert abs(b[5]-96)<.001,'Real plank surface differs';floors.append(b)
  if p['id'].startswith(('TLM_GWR_Tree','TLM_GWR_Rock','TLM_GWR_Understory')):
   b=v.box(a['nif']['bottomBandBounds'],[p['x'],p['y'],p['z']],[0,0,p['yaw']]);xs=[b[0]+(b[3]-b[0])*i/max(1,math.ceil((b[3]-b[0])/16))for i in range(max(1,math.ceil((b[3]-b[0])/16))+1)];ys=[b[1]+(b[4]-b[1])*i/max(1,math.ceil((b[4]-b[1])/16))for i in range(max(1,math.ceil((b[4]-b[1])/16))+1)];values=[ground(x,y,flip)for x in xs for y in ys for flip in[False,True]];assert b[2]<=min(values)+.1 and max(values)-b[2]<=64,'Ground prop floats/overembeds';footings.append(p['id'])
 def supported(x,y,radius=32):
  for dx,dy in[(0,0),(-radius,0),(radius,0),(0,-radius),(0,radius)]:
   if not any(b[0]-.001<=x+dx<=b[3]+.001 and b[1]-.001<=y+dy<=b[4]+.001 for b in floors):return False
  return True
 source,_=v.records(v.ROOT.parents[2]/'opening-actor-presentation-001/build/opening-actors-003/TheLastMeridian.esp')
 actors=[(r['name'],v.pose(r)[:3])for r in rows.values()if r['type']=='ACHR'and r['name'].startswith('TLM_WS_ST_GW_')]
 actors.extend([('Rafferty'+role,[v.pose(names['TLM_WS_ST_GW_'+alias])[0]+64,v.pose(names['TLM_WS_ST_GW_'+alias])[1]+64,112])for role,alias in [('Offside','OffSideArrival'),('Chute','ChuteStart'),('Landing','Arrival')]]);actors.append(('HatcherSteeple',v.pose(names['TLM_WS_ST_GW_Steeple'])[:3]))
 obstacles=[(name,b)for name,b in boxes if b[5]>104 and b[2]<288]
 for alias in CARGO:
  r=names['TLM_WS_ST_GW_'+alias];b=models['CrateLargeGrayRusty']['nif']['renderBounds'];obstacles.append((alias,v.box([x*.35 for x in b],v.pose(r)[:3],v.pose(r)[3:])))
 def clear(x,y,radius,skip=None,physical=False):
  for name,b in obstacles:
   if name==skip:continue
   dx=max(b[0]-x,x-b[3],0);dy=max(b[1]-y,y-b[4],0)
   if dx*dx+dy*dy<(radius-.001)**2:return False,name
  for name,p in actors:
   if name==skip:continue
   if math.hypot(x-p[0],y-p[1])<radius+(32 if physical else 64):return False,name
  return True,None
 buttonProof=[]
 assert {b['alias']for b in scene['buttons']}==CONTROL,'Working button membership'
 for b in scene['buttons']:
  r=names['TLM_WS_ST_GW_'+b['alias']];act=rows[v.form(r['tags'][b'NAME'])];assert act['type']=='ACTI'and act['tags'][b'MODL'].rstrip(b'\0').decode()==models['BobbleHead_Speech']['model'],'Genuine actual own activator'
  original=source[v.form(old[r['id']]['tags'][b'NAME'])];assert act['flags']==original['flags']and [(k,b)for k,b in act['ordered']if k not in{b'EDID',b'OBND',b'MODL',b'MODT'}]==[(k,b)for k,b in original['ordered']if k not in{b'EDID',b'OBND',b'MODL',b'MODT'}],'Control label/behavior changed'
  scale=struct.unpack('<f',r['tags'][b'XSCL'])[0];assert scale==4,'Large control scale';bb=v.box([x*scale for x in models['BobbleHead_Speech']['nif']['renderBounds']],v.pose(r)[:3],v.pose(r)[3:]);desk=next(box for name,box in boxes if name=='TLM_GWR_ControlDesk'+b['alias']);assert abs(bb[2]-desk[5])<.001 and bb[0]>desk[0]and bb[3]<desk[3]and bb[1]>desk[1]and bb[4]<desk[4],'Marker/table support'
  x,y,z=b['stance'];assert supported(x,y,96),'192wide stance unsupported: '+b['alias'];ok,blocked=clear(x,y,96);assert ok,'192wide stance obstructed: '+b['alias']+' / '+str(blocked);assert math.dist(b['stance'],v.pose(r)[:3])<192,'Normal activation reach';buttonProof.append(b['alias'])
 # Conservative32-radius128-high capsule proxy graph across the actual96 deck.
 def valid(x,y):return supported(x,y,32)and clear(x,y,32,physical=True)[0]
 for alias in ['Arrival','ChuteStart','OffSideArrival']:
  p=v.pose(names['TLM_WS_ST_GW_'+alias]);assert supported(*p[:2],32)and 96<=p[2]<=128 and clear(*p[:2],32,physical=True)[0],'Unsafe/submerged arrival '+alias
 for name,p in actors:assert supported(*p[:2],32)and clear(*p[:2],32,skip=name,physical=True)[0],'Actor or scripted landing blocked: '+name
 start=(1800,-2260);assert valid(*start),'Arrival capsule blocked';queue=collections.deque([start]);seen={start}
 while queue:
  x,y=queue.popleft()
  for dx,dy in[(-16,0),(16,0),(0,-16),(0,16)]:
   q=(x+dx,y+dy)
   if q not in seen and 1280<=q[0]<=3840 and -2560<=q[1]<=-1536 and valid(*q):seen.add(q);queue.append(q)
 targets={b['alias']:b['stance'][:2]for b in scene['buttons']};targets.update({name:p[:2]for name,p in actors if name.startswith('TLM_WS_ST_GW_')})
 for name,p in targets.items():assert any(math.hypot(x-p[0],y-p[1])<=(192 if name.startswith('TLM_WS_ST_GW_')else 32)for x,y in seen),'Capsule proxy route cannot reach '+name
 return {'baselineSupportedArea':1277952,'newDryGentleLandArea':gentle,'dryLandRatio':gentle/1277952,'fullyWetQuadArea':wet,'oldRecordsRetained':len(old),'heights':1089,'sharedHeightEdge':33,'props':len(scene['props']),'footings':len(footings),'realControls':buttonProof,'capsuleProxyReachableGridNodes':len(seen),'capsuleProxy':'radius32/height128 body proxy with NPC32; separate192wide stance usesNPC64 activity buffer; NOT actual native capsules/Havok traversal','native':'OPEN: WATER rendering/current/swimming, bankwalk/physics/navmesh/visibility/questtravel'}
if __name__=='__main__':
 rows,_=v.records(v.OUT/'TLMWorldSlice.esp');print(json.dumps(check(rows),indent=2))
