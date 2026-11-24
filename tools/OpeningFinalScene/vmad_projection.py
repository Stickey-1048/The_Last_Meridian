"""Complete typed current-master VMAD projection for the final scene readback.

Prepared only; no master/output path selected and no candidate built.
One optional named reference remap may accompany the existing own-quest remap.
"""
import struct

def project(data,source_quest,exterior_quest,sheriff_pair=None):
 b=bytearray(data);pos=0;voice_hits=0
 def number(fmt):
  nonlocal pos
  n=struct.calcsize(fmt);assert pos+n<=len(b);v=struct.unpack_from(fmt,b,pos)[0];pos+=n;return v
 def string():
  nonlocal pos
  n=number('<H');assert pos+n<=len(b);v=bytes(b[pos:pos+n]);pos+=n;return v
 def obj(script=None,prop=None):
  nonlocal pos,voice_hits
  assert pos+8<=len(b);alias=struct.unpack_from('<h',b,pos+2)[0];fid=struct.unpack_from('<I',b,pos+4)[0]
  if fid==source_quest:struct.pack_into('<I',b,pos+4,exterior_quest)
  if script==b'TLM:RedHollowWalk'and prop==b'VoiceOriginalSheriff':
   assert sheriff_pair is not None and alias==-1 and fid==sheriff_pair[0],'exact source sheriff reference'
   struct.pack_into('<I',b,pos+4,sheriff_pair[1]);voice_hits+=1
  pos+=8
 def value(kind,script,prop):
  if kind==1:obj(script,prop)
  elif kind==2:string()
  elif kind in(3,4):number('<I')
  elif kind==5:number('<B')
  elif kind in(11,12,13,14,15):
   for _ in range(number('<I')):value(kind-10,script,prop)
  else:raise AssertionError(('unsupported actual VMAD kind',kind))
 def scripts():
  number('<H');assert number('<H')==2
  for _ in range(number('<H')):
   name=string();number('<B')
   for __ in range(number('<H')):
    prop=string();kind=number('<B');number('<B')
    if name==b'TLM:RedHollowWalk'and prop==b'VoiceOriginalSheriff':assert kind==1,'scalar sheriff only'
    value(kind,name,prop)
 scripts()
 assert number('<B')==3 and number('<H')==0,'actual current quests have no fragments'
 string()
 for _ in range(number('<H')):obj();scripts()
 assert pos==len(b),'whole alias tail consumed'
 assert voice_hits==(1 if sheriff_pair is not None else 0),'exact named sheriff binding count'
 return bytes(b)
