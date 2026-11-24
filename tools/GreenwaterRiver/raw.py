"""Independent emitted-VHGT/normal/footprint screen; no native certificate."""
from pathlib import Path
import struct,zlib,json,math,hashlib
ROOT=Path(__file__).resolve().parent
OUT=ROOT/'build/river-011'
def subs(b):
 p=0;over=None
 while p<len(b):
  k,n=struct.unpack_from('<4sH',b,p);p+=6
  if k==b'XXXX':over=struct.unpack_from('<I',b,p)[0];p+=n;continue
  if over is not None:n,over=over,None
  yield k,b[p:p+n];p+=n
 assert p==len(b)

def records(path,wanted=None):
 rows={};names={}
 with path.open('rb')as f:
  def walk(end,parents):
   while f.tell()<end:
    at=f.tell();h=f.read(24);assert len(h)==24;k,n,flags,fid=struct.unpack_from('<4sIII',h)
    if k==b'GRUP':
     label,kind=struct.unpack_from('<Ii',h,8);walk(at+n,parents+[(kind,label)]);continue
    if wanted is not None and fid not in wanted:f.seek(n,1);continue
    b=f.read(n);b=zlib.decompress(b[4:])if flags&0x40000 else b;ss=list(subs(b));s=dict(ss);name=s.get(b'EDID',b'').rstrip(b'\0').decode();row={'type':k.decode(),'flags':flags,'id':fid,'name':name,'parents':parents,'tags':s,'ordered':ss};rows[fid]=row
    if name:names[name]=row
  walk(path.stat().st_size,[])
 return rows,names

def form(b):return struct.unpack('<I',b)[0]

def pose(r):return list(struct.unpack('<6f',r['tags'][b'DATA']))

def box(b,p,rot):
 # Intrinsic yaw only for current passive objects; no imported helper.
 assert abs(rot[0])+abs(rot[1])<.00001
 c,s=math.cos(rot[2]),math.sin(rot[2]);v=[(p[0]+x*c+y*s,p[1]+y*c-x*s,p[2]+z)for x in(b[0],b[3])for y in(b[1],b[4])for z in(b[2],b[5])];return [min(q[i]for q in v)for i in range(3)]+[max(q[i]for q in v)for i in range(3)]

def overlap(a,b):return all(min(a[i+3],b[i+3])-max(a[i],b[i])>.01 for i in range(3))
def decode(land):
 b=land['tags'][b'VHGT'];h=[];prev=struct.unpack_from('<f',b)[0]*8
 for y in range(33):
  row=[];value=prev
  for x in range(33):value+=struct.unpack_from('<b',b,4+y*33+x)[0]*8;row.append(value)
  h.append(row);prev=row[0]
 return h
def ground(h,x,y,flip=False):
 ix=min(31,max(0,int(x//128)));iy=min(31,max(0,int(y//128)));u=(x-ix*128)/128;v=(y-iy*128)/128;a,b,c,d=h[iy][ix],h[iy][ix+1],h[iy+1][ix],h[iy+1][ix+1]
 if flip:return a+(b-a)*u+(c-a)*v if u+v<=1 else d+(c-d)*(1-u)+(b-d)*(1-v)
 return a+(b-a)*u+(d-b)*v if v<=u else a+(d-c)*u+(c-a)*v




