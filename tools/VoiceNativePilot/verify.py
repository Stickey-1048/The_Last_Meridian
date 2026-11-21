"""Strict new opt-in addon source/artifact checks. No old verifier or baseline is changed."""
from pathlib import Path
import hashlib,json,struct,zlib,subprocess,sys,collections
ROOT=Path(__file__).resolve().parent
BASE='f491eeb4e670d306530446b60f82785950dbb747'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest().upper()
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
def artifact_problems(plugin,mapping,baseline):
 errors=[]
 try:
  rr=records(Path(plugin).read_bytes());counts=collections.Counter(r['tag'] for r in rr)
  if counts!={'TES4':1,'WRLD':1,'CELL':1,'QUST':1,'DIAL':2,'INFO':2,'MESG':4,'ACTI':2,'REFR':2}:errors.append('Unexpected records/topology')
  byid={r['id']:r for r in rr};base={r['id']:r for r in records(Path(baseline).read_bytes())}
  head=subs(rr[0]['data']);masters=[v.rstrip(b'\0').decode() for k,v in head if k=='MAST']
  if masters!=['Fallout4.esm','TheLastMeridian.esp']:errors.append('Wrong masters')
  if abs(struct.unpack('<f',dict(head)['HEDR'][:4])[0]-.95)>.00001:errors.append('Wrong GOG header')
  for id in [0x01000CF7,0x01000CF8]:
   if byid[id]['data']!=base[id]['data']:errors.append('Original header payload changed')
  for row in mapping['rows']:
   info=byid[0x02000000+int(row['info'].split(':')[0],16)];ss=dict(subs(info['data']))
   if ss['NAM1'].rstrip(b'\0').decode()!=row['subtitle'] or struct.unpack('<I',ss['ANAM'])[0]!=0x01000000+int(row['npc'].split(':')[0],16):errors.append('Wrong INFO speaker/subtitle')
   if 'VMAD' in ss or 'SCHR' in ss or 'QSTA' in ss:errors.append('INFO effect fragment')
   if info['parents'][-1]!=(0x02000000+int(row['topic'].split(':')[0],16),7):errors.append('Wrong INFO topic group')
   ref=byid[0x02000000+int(row['control'].split(':')[0],16)];fields=dict(subs(ref['data']))
   if ref['flags']!=0x400 or ref['parents'][-1]!=(0x01000CF8,8) or tuple(struct.unpack('<6f',fields['DATA'])[:3])!=tuple(row['position']):errors.append('Wrong persistent control')
   if b'TLMDev:VoicePilot' not in fields['VMAD']:errors.append('Missing runtime script')
   for name in ['OriginalSpeaker','ExpectedBase','ExpectedVoice','LineTopic','PilotQuest','Prompt','TextFallback']:
    if name.encode() not in fields['VMAD']:errors.append('Missing '+name)
 except Exception as e:errors.append('Malformed artifact: '+str(e))
 return errors
def source_problems():
 errors=[];receipt=json.loads((ROOT/'source-receipt.json').read_text(encoding='utf-8'));repo=ROOT.parents[1]
 if receipt['baseline']!=BASE:errors.append('Wrong baseline')
 baseline=subprocess.check_output(['git','ls-tree','-r',BASE],cwd=repo)
 if hashlib.sha256(baseline).hexdigest().upper()!=receipt['baselineInventorySha256']:errors.append('Baseline inventory changed')
 changed=subprocess.check_output(['git','diff','--name-only',BASE,'--'],cwd=repo,text=True).splitlines()
 untracked=subprocess.check_output(['git','ls-files','--others','--exclude-standard'],cwd=repo,text=True).splitlines()
 allowed={'tools/VoiceNativePilot/'+n for n in receipt['files']}|{'tools/VoiceNativePilot/source-receipt.json'}
 if set(changed+untracked)-allowed:errors.append('Change outside exact new addon union')
 for n,h in receipt['files'].items():
  if not (ROOT/n).is_file() or sha(ROOT/n)!=h:errors.append('Source pin '+n)
 return errors
if __name__=='__main__':
 errors=source_problems()
 if len(sys.argv)==4:errors+=artifact_problems(sys.argv[1],json.loads(Path(sys.argv[2]).read_text()),sys.argv[3])
 print('\n'.join(errors) if errors else 'Voice native pilot source/artifact PASS')
 sys.exit(bool(errors))
