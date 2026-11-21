"""Exact physical-custody F1 successor; all a8 histories remain frozen."""
from pathlib import Path
import json,sys
import blackstone_final_effects_candidate as prior
ROOT=Path(__file__).resolve().parents[1]
BASELINE='59b85e8bf868d9c42ed44dfd24a9a64eba3fca9e'
BASELINE_DIGEST='232AD12D34D310733FB9345F56009686959C42AFACFA3DD3DC344EB8433B9B14'
APPROVED={'scripts/Source/User/TLM/BlackstoneWalk.psc': 'D3ED2BE90CA0A1411E89D003BF95556786E6F5879C6FEF1FDD367897B4646340', 'scripts/Source/User/TLM/MQ05Quest.psc': 'EFB75CFE6710BB3EA808B32EB1B95ADD7DF86E34754FBF9CA5CD6A80CE41ADC4', 'tools/Blackstone/PASS_CUSTODY_REPAIR.md': 'AA68FC37006867244BAD73D9E4B3CE54B6FD14E2F27BF0F9057A3DC82BBD40CA', 'tools/Blackstone/package_pass_custody.py': 'EEDD5AC50A933BFE17B9AA6753B7802634ECF9EDA7C846463488244436CF1FD4', 'tools/Blackstone/pass-custody-baseline.json': '11F31F7990D58B693C4D783BACFB34562216D8AFBFB32A0DEC7D303501B29A54', 'tools/Blackstone/pass-custody-package-inputs.json': '642D977E87BF9C7CFA0F385D9FD8386174C83EF72F8401E05FB5A3338BF0D3F3', 'tools/Blackstone/test_pass_custody.py': 'AF080017CB7FEE1F6FE2377195404002A49B142415150D2172C7C3CB3DD71ADE', 'tools/Blackstone/test_pass_custody_candidate.py': '41470D095AFFBB228A5CD3FC0B7C187E79E8A55C41D486EAD2496A204060B7A1'}
OWN={'tools/Blackstone/PASS_CUSTODY_REPAIR.md', 'tools/Blackstone/test_pass_custody.py', 'tools/Blackstone/test_pass_custody_candidate.py', 'tools/blackstone_pass_custody_candidate.py', 'tools/Blackstone/pass-custody-baseline.json', 'tools/Blackstone/package_pass_custody.py', 'tools/Blackstone/pass-custody-package-inputs.json'}
NAME='tools/win/blackstone-pass-custody-candidate.json'
pin=prior.pin;digest=prior.digest

def expected_names(root=ROOT):return set(json.loads((root/'tools/Blackstone/pass-custody-baseline.json').read_text(encoding='utf-8')))|OWN|{NAME}
def describe(root=ROOT):return prior.describe(root)
def problems(root=ROOT):
 out=[]
 try:
  base=json.loads((root/'tools/Blackstone/pass-custody-baseline.json').read_text(encoding='utf-8'));m=json.loads((root/NAME).read_text(encoding='utf-8'))
  if len(base)!=511 or digest(base)!=BASELINE_DIGEST:out.append('Exact511 59b baseline changed')
  if (m.get('candidate'),m.get('baseline'),m.get('scripts'))!=('BLACKSTONE-PASS-CUSTODY-FIX-001',BASELINE,41):out.append('Repair identity changed')
  expected=dict(base);expected.update(APPROVED)
  for name,value in expected.items():
   if pin(root/name)!=value:out.append('Unapproved repair delta: '+name)
  names=set(base)|OWN|{NAME}
  if prior.prior.inventory.current_names(root)!=names:out.append('Exact repair membership changed')
  if m.get('sourceFilesTextSha256')!={n:pin(root/n)for n in sorted(names-{NAME})}:out.append('Repair source bindings differ')
  state=describe(root)
  for name,value in state.items():
   if m.get(name)!=value:out.append(name+' differs')
  old=json.loads((root/prior.NAME).read_text(encoding='utf-8'))
  if len(state['sourceTextSha256'])!=41 or {n for n,p in state['sourceTextSha256'].items()if p!=old['sourceTextSha256'].get(n)}!={'BlackstoneWalk.psc','MQ05Quest.psc'}:out.append('Changes exceed exact two runtime sources')
  if state['runtimeSelection']!=old['runtimeSelection']:out.append('Exact41 normal16/25 selection changed')
  if m.get('measured')!={'compiler':None,'artifact':None,'native':None}:out.append('No source-only artifact/native claims')
 except (OSError,ValueError,KeyError,TypeError)as error:out.append('Unreadable repair: '+str(error))
 return out
if __name__=='__main__':
 if sys.argv[1:]==['verify']:
  errors=problems();print('\n'.join(errors)if errors else 'Blackstone pass-custody source repair PASS; exact two runtime sources; native separate.');sys.exit(bool(errors))
 print(json.dumps(describe(),indent=2))
