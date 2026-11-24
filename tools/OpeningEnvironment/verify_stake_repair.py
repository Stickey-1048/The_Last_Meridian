"""Finite actual two-stake repair against held06c; no native certificate."""
import verify_landscape as v
import json,struct,math,hashlib
OUT=v.ROOT/'build/landscape-repair-001'
OLD=v.ROOT.parents[2]/'opening-landscape-002/tools/OpeningEnvironment/build/landscape-005'
IDS=('TLM_WS_RoadMarkerLeft','TLM_WS_RoadMarkerRight')
def check(rows):
 old,_=v.records(OLD/'TLMWorldSlice.esp');names={r['name']:r for r in rows.values()};h=v.decode(next(r for r in rows.values()if r['type']=='LAND'));b=json.loads((v.ROOT/'donors.json').read_text())['assets']['FenceWoodPost01']['nif']['bottomBandBounds'];proof=[]
 assert set(rows)==set(old),'Record membership'
 for fid,r in old.items():
  n=rows[fid];assert r['parents']==n['parents'] and r['flags']==n['flags'],'Parent/flags changed'
  if r['name']not in IDS:assert r['ordered']==n['ordered'],'Record changed outside two stakes'
  else:
   assert [(k,b)for k,b in r['ordered']if k!=b'DATA']==[(k,b)for k,b in n['ordered']if k!=b'DATA'],'Stake bindings changed'
   a,p=v.pose(r),v.pose(n);assert a[:2]==p[:2]and a[3:]==p[3:],'Stake XY/rotation changed'
   scale=struct.unpack('<f',n['tags'][b'XSCL'])[0];assert abs(scale-.4)<1e-6
   bounds=v.box([x*scale for x in b],p[:3],p[3:]);values=[]
   for ix in range(9):
    for iy in range(9):
     x=bounds[0]+(bounds[3]-bounds[0])*ix/8;y=bounds[1]+(bounds[4]-bounds[1])*iy/8;values.extend([v.ground(h,x,y),v.ground(h,x,y,True)])
   assert bounds[2]<=min(values)+1 and max(values)-bounds[2]<=16,'Scaled old stake floats or overembeds'
   proof.append({'id':r['name'],'oldZ':a[2],'newZ':p[2],'actualFootBottom':bounds[2],'decodedGroundMin':min(values),'decodedGroundMax':max(values)})
 return proof
if __name__=='__main__':
 rows,_=v.records(OUT/'TLMWorldSlice.esp');print(json.dumps(check(rows),indent=2))
