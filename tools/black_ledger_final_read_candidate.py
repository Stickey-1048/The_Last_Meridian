"""Exact F1/F2 successor to reviewed341; old Chapter4 guard/manifest remain frozen."""
import json,sys
from pathlib import Path
import black_ledger_candidate as prior
ROOT=Path(__file__).resolve().parents[1]
BASELINE='3419272995315a749a6539c1a2fcc8db507c84e8'
BASELINE_DIGEST='7891F1CC647FE2F7275D64EC6419FE9714B7517CED8C159572908F7A4BD3A3CE'
NAME='tools/win/black-ledger-final-read-candidate.json'
SELF='tools/black_ledger_final_read_candidate.py'
APPROVED={'scripts/Source/User/TLM/BlackLedgerWalk.psc': '7536F13F8CBD6C2B48CB053C21EDAFECF5F1EE847C278CBD3D164ACFCEED31F7', 'scripts/Source/User/TLM/MQ04Quest.psc': 'B81976F97B203E9552A262FCF5B27B923A9D4E127B2A7F88454F2998E2C3782E', 'tools/BlackLedger/FINAL_READ_REPAIR.md': 'BA7D984E8C5CF5AF0355F4A4FC7EBC5613EE13474BA59435C522F7CC1C26F675', 'tools/BlackLedger/final-read-baseline.json': '8E715E08A4B2460B30C5E96DF1A58D7DDA396B07D126D4C8D87D1B0419EAD1C8', 'tools/BlackLedger/final-read-package-inputs.json': '9786F610DA38A286AB1C8412C504F2CA5DED6370EE81D065E3B7E5E9C23A1F69', 'tools/BlackLedger/package_final_read.py': '9F1518E54D60BF92BDA59A2D9B2EAD0F7193785DCF4289B6775E0BB71561C0EE', 'tools/BlackLedger/test_final_read.py': '24D73EDE3F7304324ADCE35E2548FD6C376D3A6D6C11A9A24EA3B707AE7A85D4', 'tools/BlackLedger/test_final_read_candidate.py': '05AAA3B3AD0B386715AB8BAF7934FCC976852AD5A3ECA9277B9894F524FED0CF'}
OWN={'tools/BlackLedger/test_final_read_candidate.py', 'tools/BlackLedger/test_final_read.py', 'tools/BlackLedger/final-read-package-inputs.json', 'tools/BlackLedger/FINAL_READ_REPAIR.md', 'tools/BlackLedger/package_final_read.py', 'tools/BlackLedger/final-read-baseline.json', 'tools/black_ledger_final_read_candidate.py'}
pin=prior.pin;digest=prior.digest

def describe(root=ROOT):
 old=json.loads((root/prior.NAME).read_text(encoding='utf-8'))
 return {'sourceTextSha256':{p.name:pin(p) for p in sorted((root/'scripts/Source/User/TLM').glob('*.psc'))},'runtimeSelection':old['runtimeSelection']}
def problems(root=ROOT):
 out=[]
 try:
  m=json.loads((root/NAME).read_text(encoding='utf-8'));base=json.loads((root/'tools/BlackLedger/final-read-baseline.json').read_text(encoding='utf-8'))
  if (m.get('candidate'),m.get('baseline'),m.get('scripts'))!=('BLACK-LEDGER-FINAL-READ-FIX-001',BASELINE,38):out.append('Repair candidate identity changed')
  if digest(base)!=BASELINE_DIGEST or len(base)!=469:out.append('Exact full341 baseline changed')
  expected=dict(base);expected.update(APPROVED)
  for name,value in expected.items():
   if pin(root/name)!=value:out.append('Unapproved repair delta: '+name)
  names=set(base)|OWN|{NAME}
  if prior.inventory.current_names(root)!=names:out.append('Exact repair membership changed')
  if m.get('sourceFilesTextSha256')!={n:pin(root/n) for n in sorted(names-{NAME})}:out.append('Repair source pins differ')
  state=describe(root)
  for name,value in state.items():
   if m.get(name)!=value:out.append(name+' differs')
  old=json.loads((root/prior.NAME).read_text(encoding='utf-8'))
  changed={name for name,p in state['sourceTextSha256'].items() if p!=old['sourceTextSha256'].get(name)}
  if changed!={'MQ04Quest.psc','BlackLedgerWalk.psc'} or len(state['sourceTextSha256'])!=38:out.append('Changes exceed exact two runtime sources')
  if state['runtimeSelection']!=old['runtimeSelection']:out.append('Exact38 normal16/fresh22 selection changed')
  if m.get('measured')!={'compiler':None,'artifact':None,'native':None}:out.append('Source candidate cannot claim native/artifact measurement')
 except (OSError,ValueError,KeyError,TypeError) as error:out.append('Unreadable repair: '+str(error))
 return out
if __name__=='__main__':
 if sys.argv[1:]==['verify']:
  errors=problems();print('\n'.join(errors) if errors else 'Black Ledger final-read source candidate PASS; exact two runtime repairs; compiler/artifact/native separate.');sys.exit(bool(errors))
 print(json.dumps(describe(),indent=2))
