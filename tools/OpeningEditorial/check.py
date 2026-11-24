"""Four DESC replacements and full-file inverse only; no world/native suite."""
from pathlib import Path
import sys,struct,json,hashlib,unittest
R=Path(__file__).resolve().parents[2];H=Path(__file__).resolve().parent
sys.path.insert(0,str(R/'tools/SheriffWorld'));from raw import records
BASE=R.parent/'opening-wreck-tableau-028/build/wreck-tableau-world-001/TLMWorldSlice.esp';OUT=R/'build/editorial-world-001/TLMWorldSlice.esp'
COPY=json.loads((H/'copy.json').read_text());OLD,_=records(BASE);NOW,_=records(OUT);IDS={0x2000000+r['localId']for r in COPY['messages']}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest().upper()
def serialized(data):
 rows={}
 def walk(at,end):
  while at<end:
   tag,n=struct.unpack_from('<4sI',data,at)
   if tag==b'GRUP':walk(at+24,at+n);at+=n
   else:rows[struct.unpack_from('<I',data,at+12)[0]]=data[at:at+24+n];at+=24+n
  assert at==end
 walk(0,len(data));return rows
def restored(data):
 source=serialized(BASE.read_bytes())
 def walk(at,end):
  output=[]
  while at<end:
   tag,n=struct.unpack_from('<4sI',data,at)
   if tag==b'GRUP':
    children=walk(at+24,at+n);output.append(data[at:at+4]+struct.pack('<I',24+len(children))+data[at+8:at+24]+children);at+=n
   else:
    fid=struct.unpack_from('<I',data,at+12)[0];output.append(source[fid]if fid in IDS else data[at:at+24+n]);at+=24+n
  assert at==end;return b''.join(output)
 return walk(0,len(data))
class Checks(unittest.TestCase):
 def test_exact_four_existing_desc_changes_and_full_binary_inverse(self):
  self.assertEqual(sha(BASE),COPY['baseline']);self.assertEqual(set(OLD),set(NOW));self.assertEqual(len(NOW),896);self.assertEqual(restored(OUT.read_bytes()),BASE.read_bytes())
  for fid,row in OLD.items():
   if fid not in IDS:self.assertEqual(NOW[fid],row,hex(fid))
  for copy in COPY['messages']:
   fid=0x2000000+copy['localId'];before=OLD[fid];after=NOW[fid];self.assertEqual(after['type'],'MESG');self.assertEqual(after['name'],copy['editorId']);self.assertEqual(before['tags'][b'DESC'].rstrip(b'\0').decode(),copy['old']);self.assertEqual(after['tags'][b'DESC'],copy['new'].encode()+b'\0');self.assertEqual([(k,v)for k,v in before['ordered']if k!=b'DESC'],[(k,v)for k,v in after['ordered']if k!=b'DESC'])
 def test_budgets_unvoiced_calls_and_unchanged_voice_sources(self):
  self.assertEqual(IDS,{0x2000B5F,0x2000B6C,0x2000B6D,0x2000B73})
  for c in COPY['messages']:self.assertLessEqual(len(c['new']),240);self.assertEqual(len(c['new']),c['characters']);self.assertTrue(c['new'].isascii())
  prologue=(R.parent/'gantt-prologue-batch-runtime-025/scripts/Source/User/TLM/OpeningPrologue.psc').read_text();act1=(R.parent/'first-brake-inquiry-registration-024/scripts/Source/User/TLM/Act1Walk.psc').read_text()
  self.assertIn('WhoPritchard.Show()',prologue);self.assertNotIn('ShowGanttRecording(WhoPritchard',prologue);self.assertIn('int answer = offer.Show()',act1);self.assertIn('int afterReport = SayInquiryReported.Show()',act1)
  for name in ['SayInquiryOffer','SayInquiryOfferDead','SayInquiryReported']:self.assertNotIn('ShowOpeningRecording('+name,act1)
  self.assertIn('If SayBegin\n\t\tSayBegin.Show()',act1) # Existing unconditional page excluded from dead-only rewrite.
if __name__=='__main__':unittest.main(verbosity=2)
