from pathlib import Path
import sys,struct,json,hashlib,wave,unittest
H=Path(__file__).resolve().parent;R=H.parents[1];W=R.parent;sys.path.insert(0,str(R/'tools/SheriffWorld'));from raw import records
from vmad import vmad
BASE=W/'opening-ridge-spill-finish-033/build/ridge-spill-finish-world-002/TLMWorldSlice.esp';OUT=R/'build/private-road-voice-world-002/TLMWorldSlice.esp';MASTER=W/'ada-book-voice-master-001/build/ada-book-master-001/TheLastMeridian.esp';OLD,_=records(BASE);NOW,_=records(OUT);M,_=records(MASTER);MAP=json.loads((H/'audio-map.json').read_text());NEW={0x2000B7F,0x2000B80,0x1000849,0x1000874};sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest().upper()
def serialized(p,row):
 b=p.read_bytes();h=row['header'];a=b.index(h);return b[a:a+24+struct.unpack_from('<I',h,4)[0]]
def inverse():
 data=OUT.read_bytes()
 def walk(at,end):
  parts=[]
  while at<end:
   h=data[at:at+24];n=struct.unpack_from('<I',h,4)[0]
   if h[:4]==b'GRUP':
    body=walk(at+24,at+n);hh=bytearray(h);struct.pack_into('<I',hh,4,len(body)+24);parts.append(bytes(hh)+body);at+=n
   else:
    fid=struct.unpack_from('<I',h,12)[0]
    if fid not in NEW:parts.append(serialized(BASE,OLD[fid])if fid in(0,0x20008FD)else data[at:at+24+n])
    at+=24+n
  assert at==end;return b''.join(parts)
 return walk(0,len(data))
class Checks(unittest.TestCase):
 def test_full_inverse_and_literal_old_records(self):
  self.assertEqual(set(NOW)-set(OLD),NEW);self.assertEqual(len(NOW),900);self.assertEqual(inverse(),BASE.read_bytes())
  for fid,row in OLD.items():
   if fid not in(0,0x20008FD):self.assertEqual(serialized(OUT,NOW[fid]),serialized(BASE,row),hex(fid))
 def test_exact_caption_override_only_DESC_and_sound_shape(self):
  for row in MAP['lines']:
   fid=0x1000000+row['messageId'];new=NOW[fid];old=M[fid];self.assertEqual(new['type'],'MESG');self.assertEqual(new['name'],row['messageEdid']);self.assertEqual([(k,v)for k,v in new['ordered']if k!=b'DESC'],[(k,v)for k,v in old['ordered']if k!=b'DESC']);caption=row['speaker']+': "'+row['text']+'"';self.assertEqual(new['tags'][b'DESC'],caption.encode()+b'\0');self.assertLessEqual(len(caption),240)
   q=NOW[0x2000000+row['newSoundId']];shape=M[0x1000F84];self.assertEqual(q['type'],'SNDR');self.assertEqual([(k,v)for k,v in q['ordered']if k not in(b'EDID',b'ANAM')],[(k,v)for k,v in shape['ordered']if k not in(b'EDID',b'ANAM')]);self.assertEqual(q['tags'][b'ANAM'],('data\\'+row['target'].replace('/','\\')).encode()+b'\0');self.assertEqual(q['tags'][b'GNAM'],struct.pack('<I',0x1000F6F))
 def test_five_typed_properties_current_originals_and_no_other_bindings(self):
  old=vmad(OLD[0x20008FD]['tags'][b'VMAD']);new=vmad(NOW[0x20008FD]['tags'][b'VMAD']);self.assertEqual(old[0],new[0]);self.assertEqual(old[2],new[2]);self.assertEqual(len(old[1]),len(new[1]));o=next(s for s in old[1]if s[0]==b'TLM:Act1Walk');n=next(s for s in new[1]if s[0]==b'TLM:Act1Walk');self.assertEqual(n[2][:116],o[2]);self.assertEqual(len(n[2]),121);props={p[0].decode():p for p in n[2][116:]};expected={'RecordedDunmoreHold':(-1,0x2000B7F),'OpeningOriginalDunmore':(-1,0x200090A),'RecordedTalbotGate':(-1,0x2000B80),'OpeningOriginalTalbot':(-1,0x200090F),'Alias_Talbot':(17,0x20008FD)}
  for name,(alias,fid)in expected.items():p=props[name];self.assertEqual(p[1:3],(1,1));self.assertEqual(p[3],struct.pack('<HhI',0,alias,fid))
  self.assertEqual([(k,v)for k,v in NOW[0x20008FD]['ordered']if k!=b'VMAD'],[(k,v)for k,v in OLD[0x20008FD]['ordered']if k!=b'VMAD'])
 def test_actual_private_PCM_exact_text_durations_and_source_hashes(self):
  for row in MAP['lines']:
   p=Path(row['waveSource']);self.assertEqual(sha(p),row['waveSha256'])
   with wave.open(str(p),'rb')as f:self.assertEqual((f.getnchannels(),f.getsampwidth(),f.getframerate()),(1,2,24000));self.assertEqual(f.getnframes()/24000,row['duration'])
  self.assertEqual([len(r['text'])for r in MAP['lines']],[80,89]);self.assertEqual(sha(MASTER),'B25C091E9208395B90F8D60995FE338FE62BDC26150F297373FC1B5889C083DD')
if __name__=='__main__':unittest.main(verbosity=2)
