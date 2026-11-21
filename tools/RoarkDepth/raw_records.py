import struct,zlib
def records(data):
 out=[]
 def walk(a,b,parents):
  while a<b:
   if a+24>b:raise ValueError('Truncated record')
   tag=data[a:a+4].decode('ascii');n=struct.unpack_from('<I',data,a+4)[0]
   if tag=='GRUP':
    if n<24 or a+n>b:raise ValueError('Bad group')
    label,kind=struct.unpack_from('<Ii',data,a+8);walk(a+24,a+n,parents+[(label,kind)]);a+=n;continue
   if a+24+n>b:raise ValueError('Truncated payload')
   flags,id=struct.unpack_from('<II',data,a+8);payload=data[a+24:a+24+n]
   if flags&0x40000:payload=zlib.decompress(payload[4:])
   out.append({'tag':tag,'flags':flags,'id':id,'data':payload,'parents':parents});a+=24+n
 walk(0,len(data),[]);return out
def subs(payload):
 out=[];p=0;wide=None
 while p<len(payload):
  tag=payload[p:p+4].decode('ascii');n=struct.unpack_from('<H',payload,p+4)[0];p+=6
  if tag=='XXXX':wide=struct.unpack_from('<I',payload,p)[0];p+=n;continue
  if wide is not None:n=wide;wide=None
  if p+n>len(payload):raise ValueError('Bad subrecord')
  out.append((tag,payload[p:p+n]));p+=n
 return out
