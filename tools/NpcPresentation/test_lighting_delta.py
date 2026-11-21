from pathlib import Path
import unittest,struct
import verify as v
OLD=v.ROOT.parents[3]/'work/npc-presentation-004/tools/NpcPresentation/build/resolved-001/TLMNpcPresentation.esp'
class LightingDelta(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.raw=v.OUT.read_bytes();cls.old=v.rows(OLD.read_bytes());cls.plan=__import__('json').loads((v.ROOT/'audition-plan.json').read_text());cls.qa=v.native({0x1f7a9})[b'CELL',0x1f7a9];cls.light=v.native({0x517b0})[b'LIGH',0x517b0]
 def check(self,raw):
  now=v.rows(raw);fill=int(self.plan['lighting']['fill'].split(':')[0],16)|0x02000000;refids=[int(k.split(':')[0],16)|0x02000000 for k in self.plan['lighting']['refs']];self.assertEqual(set(now)-set(self.old),{(b'LIGH',fill)}|{(b'REFR',k)for k in refids})
  for key,row in self.old.items():
   if key==(b'TES4',0):self.assertEqual([(k,b)for k,b in v.subs(row[1])if k!=b'HEDR'],[(k,b)for k,b in v.subs(now[key][1])if k!=b'HEDR']);continue
   if key==(b'CELL',0x02000800):
    self.assertEqual(row[0],now[key][0]);self.assertEqual(row[2],now[key][2]);self.assertEqual([(k,b)for k,b in v.subs(row[1])if k not in[b'XCLL',b'LTMP',b'XCIM']],[(k,b)for k,b in v.subs(now[key][1])if k not in[b'XCLL',b'LTMP',b'XCIM']]);continue
   self.assertEqual(row,now[key],'Existing actor/face/outfit/geometry/header changed')
  cell=dict(v.subs(now[b'CELL',0x02000800][1]));self.assertEqual({k:cell[k]for k in[b'XCLL',b'LTMP',b'XCIM']},{k:self.qa[k]for k in[b'XCLL',b'LTMP',b'XCIM']})
  light=dict(v.subs(now[b'LIGH',fill][1]));data=bytearray(self.light[b'DATA']);struct.pack_into('<I',data,4,512);self.assertEqual(light[b'DATA'],bytes(data))
  for rid,x in zip(refids,[-384,0,384]):
   flags,b,chain=now[b'REFR',rid];s=dict(v.subs(b));self.assertEqual(flags,0);self.assertEqual(struct.unpack('<I',s[b'NAME'])[0],fill);self.assertEqual(struct.unpack('<6f',s[b'DATA']),(x,256,160,0,0,0));self.assertEqual(chain[-2:],((6,0x02000800),(9,0x02000800)))
 def mutation(self,fid,tag,offset):
  b=bytearray(self.raw)
  def walk(a,end):
   while a<end:
    t,n,flags,k=struct.unpack_from('<4sIII',b,a)
    if t==b'GRUP':
     if walk(a+24,a+n):return True
     a+=n;continue
    if k==fid:
     p=a+24
     while p<a+24+n:
      st,size=struct.unpack_from('<4sH',b,p);p+=6
      if st==tag:b[p+offset]^=1;return True
      p+=size
    a+=24+n
   return False
  self.assertTrue(walk(0,len(b)));return bytes(b)
 def test_actual_complete_lighting_and_only_four_append_records(self):self.check(self.raw)
 def test_incomplete_ambient_radius_and_fill_pose_refused(self):
  fill=int(self.plan['lighting']['fill'].split(':')[0],16)|0x02000000;ref=int(self.plan['lighting']['refs'][0].split(':')[0],16)|0x02000000
  for fid,tag,offset in [(0x02000800,b'XCLL',0),(fill,b'DATA',4),(ref,b'DATA',5)]:
   with self.assertRaises(AssertionError):self.check(self.mutation(fid,tag,offset))
if __name__=='__main__':unittest.main()
