from pathlib import Path
import struct,sys,hashlib,json,unittest
R=Path(__file__).resolve().parents[2];H=Path(__file__).resolve().parent;W=R.parent;sys.path.insert(0,str(R/'tools/SheriffWorld'));from raw import records
VOICE=W/'dunmore-talbot-private-voice-world-038/build/private-road-voice-world-002/TLMWorldSlice.esp';ART=W/'opening-wreck-derailment-038/build/wreck-derailment-world-002/TLMWorldSlice.esp';OUT=R/'build/voice-wreck-union-041-001/TLMWorldSlice.esp';V,_=records(VOICE);A,_=records(ART);N,_=records(OUT);CAP={0x1000849,0x1000874};SOUND={0x2000B7F,0x2000B80};POSE={0x2000943,0x2000944};sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest().upper()
def serialized(path,row):
 data=path.read_bytes();h=row['header'];i=data.index(h);return data[i:i+24+struct.unpack_from('<I',h,4)[0]]
def reconstruct(target,rows,replaced,removed=set()):
 data=OUT.read_bytes()
 def walk(at,end):
  parts=[]
  while at<end:
   h=data[at:at+24];n=struct.unpack_from('<I',h,4)[0]
   if h[:4]==b'GRUP':
    body=walk(at+24,at+n);hh=bytearray(h);struct.pack_into('<I',hh,4,len(body)+24);parts.append(bytes(hh)+body);at+=n
   else:
    fid=struct.unpack_from('<I',h,12)[0]
    if fid not in removed:parts.append(serialized(target,rows[fid])if fid in replaced else data[at:at+24+n])
    at+=24+n
  assert at==end;return b''.join(parts)
 return walk(0,len(data))
class Checks(unittest.TestCase):
 def test_restore_two_poses_reconstructs_entire_voice_world(self):
  self.assertEqual(len(N),900);self.assertEqual(set(N),set(V));self.assertEqual(reconstruct(VOICE,V,POSE),VOICE.read_bytes())
  for fid,row in V.items():
   self.assertEqual(serialized(OUT,N[fid]),serialized(ART,A[fid])if fid in POSE else serialized(VOICE,row),hex(fid))
 def test_remove_voice_component_reconstructs_entire_contact_world(self):
  self.assertEqual(reconstruct(ART,A,{0,0x20008FD},CAP|SOUND),ART.read_bytes());self.assertEqual(set(N)-set(A),CAP|SOUND)
 def test_exact_guarded_source_component_and_hook_only(self):
  other=W/'opening-wreck-derailment-038';self.assertEqual((R/'tools/WorldSliceBuilder/OpeningWreckDerailment.cs').read_bytes(),(other/'tools/WorldSliceBuilder/OpeningWreckDerailment.cs').read_bytes());self.assertEqual((R/'tools/OpeningWreckDerailment/plan.json').read_bytes(),(other/'tools/OpeningWreckDerailment/plan.json').read_bytes());self.assertEqual(sha(R/'tools/OpeningWreckDerailment/plan.json'),'C23C19DC4AF60DF6963BCEBF271B4EF775AF7187DDC49FED48626BF55B9A9414')
  a=(R/'tools/WorldSliceBuilder/Program.cs').read_text();b=(W/'dunmore-talbot-private-voice-world-038/tools/WorldSliceBuilder/Program.cs').read_text();hook='if(prologue!=null)File.WriteAllText(Path.Combine(output,"opening-wreck-derailment.json"),JsonSerializer.Serialize(OpeningWreckDerailment.Apply(mod,world),new JsonSerializerOptions{WriteIndented=true}));\n';self.assertEqual(a.count(hook),1);self.assertEqual(a.replace(hook,''),b)
 def test_current_accepted_input_pins_and_master_literal(self):
  self.assertEqual(sha(VOICE),'08B7D759219D05C6B779EF3101FDC36AD5D2D94EA8D68D3028A4CA57E68082DC');self.assertEqual(sha(ART),'0C91034673974D5B0A759B386BA82B5B5BAFDD1441C6C83095B81968452AC2F4');self.assertEqual(sha(W/'ada-book-voice-master-001/build/ada-book-master-001/TheLastMeridian.esp'),'B25C091E9208395B90F8D60995FE338FE62BDC26150F297373FC1B5889C083DD')
if __name__=='__main__':unittest.main(verbosity=2)
