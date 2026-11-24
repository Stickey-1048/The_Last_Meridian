from pathlib import Path
import struct,sys,hashlib,unittest,copy
R=Path(__file__).resolve().parents[2];W=R.parent;sys.path.insert(0,str(R/'tools/SheriffWorld'));from raw import records
BASE=W/'opening-visible-slope-finish-047/build/visible-slope-finish-world-001/TLMWorldSlice.esp';OUT=R/'build/dunmore-safe-choices-world-050-002/TLMWorldSlice.esp';OLD,_=records(BASE);NOW,_=records(OUT);ID=0x1000849;sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest().upper();LABELS=["[Call for help] Sheriff! Over here!","[Leave the caravan] I'm walking away.","What kind of share?","[Risk combat] Pritchard hangs road-takers. Leave.","[Fight] Let them go."]
def serialized(path,row):
 b=path.read_bytes();h=row['header'];i=b.index(h);return b[i:i+24+struct.unpack_from('<I',h,4)[0]]
def restore():
 b=OUT.read_bytes()
 def walk(at,end):
  p=[]
  while at<end:
   h=b[at:at+24];n=struct.unpack_from('<I',h,4)[0]
   if h[:4]==b'GRUP':body=walk(at+24,at+n);hh=bytearray(h);struct.pack_into('<I',hh,4,len(body)+24);p.append(bytes(hh)+body);at+=n
   else:
    fid=struct.unpack_from('<I',h,12)[0];p.append(serialized(BASE,OLD[ID])if fid==ID else b[at:at+24+n]);at+=24+n
  assert at==end;return b''.join(p)
 return walk(0,len(b))
def check_message(q):
 assert q['type']=='MESG'and q['name']=='TLM_MSG_A1_DunmoreHold';assert q['tags'][b'DESC']==OLD[ID]['tags'][b'DESC'];assert[v.rstrip(b'\0').decode()for k,v in q['ordered']if k==b'ITXT']==LABELS
 assert[(k,v)for k,v in q['ordered']if k!=b'ITXT']==[(k,v)for k,v in OLD[ID]['ordered']if k!=b'ITXT'];assert b'CTDA'not in q['tags']
class Checks(unittest.TestCase):
 def test_entire_inverse_and_only849_changed(self):
  self.assertEqual(len(NOW),900);self.assertEqual(set(NOW),set(OLD));self.assertEqual(restore(),BASE.read_bytes())
  for fid,q in OLD.items():
   if fid!=ID:self.assertEqual(serialized(OUT,NOW[fid]),serialized(BASE,q),hex(fid))
 def test_actual_order_only_leave_copy_and_recordedcaption_literal(self):
  q=NOW[ID];check_message(q);self.assertEqual(q['parents'],OLD[ID]['parents']);self.assertEqual(q['header'][:4]+OLD[ID]['header'][4:8]+q['header'][8:],OLD[ID]['header']);self.assertEqual([len(x)for x in LABELS],[35,37,19,49,20]);self.assertLessEqual(len(LABELS[1]),48);self.assertEqual(struct.unpack('<fII',NOW[0]['tags'][b'HEDR'])[1:],(948,2945))
 def test_wrong_order_or_voicedcaption_mutants_refused(self):
  for mode in('order','caption'):
   q=copy.deepcopy(NOW[ID])
   if mode=='order':items=[i for i,(k,v)in enumerate(q['ordered'])if k==b'ITXT'];q['ordered'][items[0]],q['ordered'][items[1]]=q['ordered'][items[1]],q['ordered'][items[0]]
   else:q['tags'][b'DESC']=b'wrong recorded words\0'
   with self.assertRaises(AssertionError):check_message(q)
 def test_exact_base_pin_and_single_production_hook(self):
  self.assertEqual(sha(BASE),'B6258F8ADF28019D5ADAB2FCACB85DCEA3452B9202CAC46B6E284BD5CAC27E50');hook='if(prologue!=null)File.WriteAllText(Path.Combine(output,"dunmore-safe-choices.json"),JsonSerializer.Serialize(DunmoreSafeChoices.Apply(mod),new JsonSerializerOptions{WriteIndented=true}));\n';s=(R/'tools/WorldSliceBuilder/Program.cs').read_text();self.assertEqual(s.count(hook),1);self.assertEqual(s.replace(hook,''),(W/'opening-visible-slope-finish-047/tools/WorldSliceBuilder/Program.cs').read_text())
if __name__=='__main__':unittest.main(verbosity=2)
