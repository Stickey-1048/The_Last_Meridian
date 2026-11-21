"""Exact single-controller F1 successor; all a8 histories remain frozen."""
from pathlib import Path
import json,sys
import blackstone_candidate as prior
ROOT=Path(__file__).resolve().parents[1]
BASELINE='a8dc467cbc5e81bf7d48e2a22c206e6ce09a4d87'
BASELINE_DIGEST='AB9AD806C2FE015A61549AD0CBF3E75A6646BEC1F7EA9979354BC16E882D2069'
APPROVED={'scripts/Source/User/TLM/BlackstoneWalk.psc': 'C5A944AB43C1374FF5EB5B3BEFFEDC3EA7455EF6D320502F30DC45F6E5EF5FA4', 'tools/Blackstone/FINAL_EFFECTS_REPAIR.md': '059A1303FE78BDEEBDCD7EB66D55188460834C5E88637E49F89BF80DCD7FF7F8', 'tools/Blackstone/final-effects-baseline.json': 'CB2AE66E3DB44CE1BE4BF2DDECC664FF5B516B02FB95BE882FC48F970FE081C5', 'tools/Blackstone/final-effects-package-inputs.json': 'CDDD9E1D844EC0614C040816D12DF184C2632A3B5D9DD1B4BD5700D8C39415A9', 'tools/Blackstone/package_final_effects.py': 'D1606D2E7264AE0F7A7A09173E835A3112BA0AE48CF3E4A1B7E1905889636E50', 'tools/Blackstone/test_final_effects.py': '04358B41E6DD06C28E2FD046D1192B5BA3E1E417D62B633E086BA1D3B9127EE2', 'tools/Blackstone/test_final_effects_candidate.py': 'CDA3A62FAA0DE74A9F4FC9D78AD703CFF6B9D6AC8C757F9A06A54F6D3099F102'}
OWN={'tools/Blackstone/FINAL_EFFECTS_REPAIR.md', 'tools/Blackstone/final-effects-package-inputs.json', 'tools/blackstone_final_effects_candidate.py', 'tools/Blackstone/test_final_effects_candidate.py', 'tools/Blackstone/test_final_effects.py', 'tools/Blackstone/package_final_effects.py', 'tools/Blackstone/final-effects-baseline.json'}
NAME='tools/win/blackstone-final-effects-candidate.json'
pin=prior.pin;digest=prior.digest

def expected_names(root=ROOT):return set(json.loads((root/'tools/Blackstone/final-effects-baseline.json').read_text(encoding='utf-8')))|OWN|{NAME}
def describe(root=ROOT):return prior.describe(root)
def problems(root=ROOT):
 out=[]
 try:
  base=json.loads((root/'tools/Blackstone/final-effects-baseline.json').read_text(encoding='utf-8'));m=json.loads((root/NAME).read_text(encoding='utf-8'))
  if len(base)!=503 or digest(base)!=BASELINE_DIGEST:out.append('Exact503 a8 baseline changed')
  if (m.get('candidate'),m.get('baseline'),m.get('scripts'))!=('BLACKSTONE-FINAL-EFFECTS-FIX-001',BASELINE,41):out.append('Repair identity changed')
  expected=dict(base);expected.update(APPROVED)
  for name,value in expected.items():
   if pin(root/name)!=value:out.append('Unapproved repair delta: '+name)
  names=set(base)|OWN|{NAME}
  if prior.inventory.current_names(root)!=names:out.append('Exact repair membership changed')
  if m.get('sourceFilesTextSha256')!={n:pin(root/n)for n in sorted(names-{NAME})}:out.append('Repair source bindings differ')
  state=describe(root)
  for name,value in state.items():
   if m.get(name)!=value:out.append(name+' differs')
  old=json.loads((root/prior.NAME).read_text(encoding='utf-8'))
  if len(state['sourceTextSha256'])!=41 or {n for n,p in state['sourceTextSha256'].items()if p!=old['sourceTextSha256'].get(n)}!={'BlackstoneWalk.psc'}:out.append('Changes exceed one controller')
  if state['runtimeSelection']!=old['runtimeSelection']:out.append('Exact41 normal16/25 selection changed')
  if m.get('measured')!={'compiler':None,'artifact':None,'native':None}:out.append('No source-only artifact/native claims')
 except (OSError,ValueError,KeyError,TypeError)as error:out.append('Unreadable repair: '+str(error))
 return out
if __name__=='__main__':
 if sys.argv[1:]==['verify']:
  errors=problems();print('\n'.join(errors)if errors else 'Blackstone final-effects source repair PASS; exact single controller; native separate.');sys.exit(bool(errors))
 print(json.dumps(describe(),indent=2))
