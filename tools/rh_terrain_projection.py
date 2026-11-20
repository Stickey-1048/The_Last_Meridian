"""RH-TERRAIN-002 independent focused raw projection screens. No build/native IO.
Usage: python tools/rh_terrain_projection.py NEW.esp BASELINE.esp
Both projections must use the SAME stand-in master for raw equality.
"""
import json,math,struct,sys,zlib
from pathlib import Path

def subs(data):
 p=0;out=[];over=None
 while p<len(data):
  kind,n=struct.unpack_from('<4sH',data,p);p+=6
  if kind==b'XXXX':over=struct.unpack_from('<I',data,p)[0];p+=n;continue
  if over is not None:n,over=over,None
  out.append((kind,data[p:p+n]));p+=n
 assert p==len(data)
 return out

def records(data):
 result={};names={}
 def walk(start,end,chain=()):
  p=start
  while p<end:
   kind,n,flags,fid=struct.unpack_from('<4sIII',data,p)
   if kind==b'GRUP':walk(p+24,p+n,chain+((flags,fid),));p+=n;continue
   body=data[p+24:p+24+n];body=zlib.decompress(body[4:]) if flags&0x40000 else body
   key=(kind,fid);assert key not in result;result[key]=(flags,body,chain)
   name=dict(subs(body)).get(b'EDID',b'').rstrip(b'\0').decode()
   if name:names[name]=key
   p+=24+n
  assert p==end
 walk(0,len(data));return result,names

def land_grid(record):
 s=dict(subs(record[1]));d=s[b'VHGT'];assert len(d)==1096
 offset=struct.unpack_from('<f',d)[0];height=[];first=offset
 for y in range(33):
  row=[];value=first
  for x in range(33):
   value+=struct.unpack_from('<b',d,4+y*33+x)[0];row.append(value*8)
  first=row[0]/8;height.append(row)
 return height,s[b'VNML']

def allowed_changes():
 names=set()
 for room,lo,hi in [('Nine',5888,7936),('Gallery',8960,11008)]:
  names.update('TLM_REF_RHE_'+room+side+str(x) for x in range(lo+256,hi,512) for side in ('South','North'))
  names.update('TLM_REF_RHE_'+room+side+str(y) for y in range(0,1536,512) for side in ('West','East'))
 names.update('TLM_REF_RHE_'+side+str(x) for x in range(256,4096,512) for side in ('North','South','Trees'))
 names.update('TLM_REF_RHE_'+side+str(y) for y in range(256,1792,512) for side in ('West','East'))
 return names

def verify(raw,baseline):
 now,names=records(raw);old,on=records(baseline);changed=[];land_changes=0
 assert set(old)<=set(now),'Original record removed'
 assert all(names[n]==key for n,key in on.items()),'Original EDID/FormID changed'
 allowed=allowed_changes()
 for key,row in old.items():
  current=now[key]
  if key[0]==b'TES4':
   assert [(k,v) for k,v in subs(row[1]) if k!=b'HEDR']==[(k,v) for k,v in subs(current[1]) if k!=b'HEDR'];continue
  if row==current:continue
  name=next((n for n,k in on.items() if k==key),'')
  assert row[0]==current[0] and row[2]==current[2],'Original flags/parent changed: '+name
  if key[0]==b'LAND':
   a,b=dict(subs(row[1])),dict(subs(current[1]));assert {k:v for k,v in a.items() if k not in (b'VHGT',b'VNML')}=={k:v for k,v in b.items() if k not in (b'VHGT',b'VNML')};land_changes+=1;continue
  assert name in allowed,'Unapproved old record delta: '+name
  a,b=dict(subs(row[1])),dict(subs(current[1]));aa,bb=struct.unpack('<6f',a.pop(b'DATA')),struct.unpack('<6f',b.pop(b'DATA'));assert a==b,'Old payload changed outside transform: '+name
  assert abs(aa[0]-bb[0])<1e-4
  if name.startswith('TLM_REF_RHE_North'):
   assert bb[1]==4096 and bb[2]>=576 and bb[3:]==(0,0,0)
  elif name.startswith('TLM_REF_RHE_Trees'):
   assert aa[1]==bb[1] and aa[3:]==bb[3:] and bb[2]>aa[2]
  else:
   assert aa[:3]==bb[:3] and aa[3:5]==bb[3:5]
  changed.append(name)
 assert set(changed)==allowed,('Allowed delta membership differs',set(changed)^allowed)
 assert land_changes==1
 newkeys=set(now)-set(old);assert len(newkeys)==72
 assert all(k[0]==b'REFR' and next(n for n,key in names.items() if key==k).startswith('TLM_REF_RHE_T2_') for k in newkeys),'New records outside decorative refs'
 # Every perimeter renders toward the room under measured native convention.
 wall_count=0
 for name,key in names.items():
  if not name.startswith('TLM_REF_RHE_') or not any(name.startswith('TLM_REF_RHE_'+r+s) for r in ('Nine','Gallery') for s in ('South','North','West','East','Seal')):continue
  d=dict(subs(now[key][1]));x,y,z,rx,ry,yaw=struct.unpack('<6f',d[b'DATA']);assert rx==ry==0
  cx=6912 if 'Nine' in name else 9984
  dot=-math.sin(yaw)*(cx-x)-math.cos(yaw)*(512-y);assert dot>0,'Outward mine face: '+name;wall_count+=1
 assert wall_count==31
 land=next(v for k,v in now.items() if k[0]==b'LAND');height,normals=land_grid(land)
 assert all(v==0 for row in height[:17] for v in row),'Protected story ground changed'
 assert height[22][16]==128 and height[26][16]==128 and height[32][16]==320
 assert max(max(r) for r in height)==416 and min(min(r) for r in height)==0
 assert len(normals)==3267 and normals[:17*33*3]!=bytes((0,0,127))*(17*33) # gradient begins at protected edge; heights still0
 assert normals[:15*33*3]==bytes((0,0,127))*(15*33)
 # Each encoded normal agrees with an independently computed height derivative.
 for y in range(33):
  for x in range(33):
   dx=(height[y][min(x+1,32)]-height[y][max(x-1,0)])/(128 if x in (0,32) else 256)
   dy=(height[min(y+1,32)][x]-height[max(y-1,0)][x])/(128 if y in (0,32) else 256)
   length=math.sqrt(1+dx*dx+dy*dy);expected=[round(-dx/length*127),round(-dy/length*127),round(1/length*127)]
   assert list(struct.unpack_from('<3b',normals,(y*33+x)*3))==expected,'LAND normal/height mismatch'
 # The entire old story content and all quest/alias records were covered by
 # the byte-preservation loop, not just coordinates or selected aliases.
 return {'newDecorativeReferences':72,'changedDecorativeTransforms':len(changed),'inwardMinePanels':31,'heightRange':[0,416],'storyPad':[0,4096,0,2048,0],'oldUnrelatedPayloadsAndParentsExact':True,'scope':'Synthetic raw projection only; no native collision/visibility proof'}

if __name__=='__main__':
 print(json.dumps(verify(Path(sys.argv[1]).read_bytes(),Path(sys.argv[2]).read_bytes()),indent=2))

