"""Strict lawful Chapter4 successor. Historical verifiers/manifests remain immutable."""
import hashlib,json,subprocess,sys
from pathlib import Path
import player_guidance_terrain_candidate as inventory
ROOT=Path(__file__).resolve().parents[1]
BASELINE='f491eeb4e670d306530446b60f82785950dbb747'
BASELINE_DIGEST='D47519A650B9DAB75C5F617399C09CAE41E07CDED904520850F331CA58BFBC6E'
NAME='tools/win/black-ledger-candidate.json'
SELF='tools/black_ledger_candidate.py'
APPROVED={'scripts/Source/User/TLM/Act1Walk.psc': 'C99C3401537F62DA62CA4B0792BCDDEABDDD84C8B187A60DAAD1DD31AA87590D', 'scripts/Source/User/TLM/BlackLedgerEntry.psc': '4A2B04186B9382C2BE154771AA330AC6FBE887CDDBAF7EA939213C4F1F012C25', 'scripts/Source/User/TLM/BlackLedgerTalk.psc': 'BA610D8518E9D8A6152D18F991BB045E879D0360B0D708A5B7A160A0C14A3091', 'scripts/Source/User/TLM/BlackLedgerWalk.psc': 'CA2CD0D727F51AE521CAE3B8E4D5DAC429799B104F5957120B8FE6C22307DB00', 'scripts/Source/User/TLM/MQ03Quest.psc': 'B27BC82DD2C9A47491690F335614387B5381B9CA2AAA48CA9923675C3A3812AF', 'scripts/Source/User/TLM/MQ04Quest.psc': '0855F3F2C8F48A1E30758557E9CC89E9647717882A4ED877E35CE6FBE697D0C8', 'tools/BlackLedger/.gitattributes': 'A79691A93B46E49CE460C26EF22AFCC03D6ECA1E63BF2EDBC20E96159510F6C9', 'tools/BlackLedger/.gitignore': 'B1FA99D1D88D2D127898EF374F03AEAA4B96188D9239DB3D0912CC18DD306574', 'tools/BlackLedger/README.md': '497B77B3A92E382594D17EE64DAD1FA5A7D0E20BD5712488AC3399F73EDABF10', 'tools/BlackLedger/audit.py': '47DDE542BEF6B7AF02406EA71319A668E62AAFDA41E8569F4717EA2BE215CDF0', 'tools/BlackLedger/baseline-inventory.json': '27C7CFA23FC851725130372AD2775C94FD4CEDF52533595F77D25D80B5EC9371', 'tools/BlackLedger/beckett-lawful.json': 'ED4C164A489E7C18B53EE8304FA9A04C477E9720BE488540FC5894D816F2EC1D', 'tools/BlackLedger/character-nodes.json': '861E76868E39A4FFA1A172364176EF3E0FE4FC1079F5181CF40B88904DF1D995', 'tools/BlackLedger/package-inputs.json': 'DB28046A96E20C9A42EE1AA33A4FAB9FEA391A46AA093F881FA2A3BD0D2DFF15', 'tools/BlackLedger/package.py': '300638DA2F2BD0F561606D06E131D4FF3400895E669995481FFF4411426676BC', 'tools/BlackLedger/test_black_ledger.py': '9DF56C7C8623F8A27ABE8FDDF3CAC2349569AFD4B0E4448F2D6237C78CFBA22C', 'tools/BlackLedger/test_candidate.py': 'EA99B29499D5C0F3570E8BF7CBB5DCE610D38EB14AF8647A775FD8C5377ED0BC', 'tools/PluginBuilder/Builder.cs': '1B91B0DFDA63BE9BAE4FA4081057CFA8EA378AD25429F30B80C5471EEBE5E670', 'tools/PluginBuilder/Spec.cs': '1630E8798BF8B4108F66C3E6C4DE24AB456CF9A1862CA261D2D75FFFB1C69C77', 'tools/PluginBuilder/SpecAct1.cs': 'E4545A8727A16C37478F8DF6281A67163E5078F756646077C3A3B2784BF88562', 'tools/PluginBuilder/SpecBlackLedger.cs': '7F27FB5CEB27EC12286C8A9031259F56AB6ACB9472C85C9010EB555EA8E89134', 'tools/PluginBuilder/formkeys.txt': 'CD92602C4571E9465696954BCB8D2C2333F3EB65C860BF84C26699E7DB9008A7', 'tools/WorldSliceBuilder/Program.cs': '61C5905436E0252DACA6811338B1AB60A2C35BD180654BB0A0B86931DDC36963', 'tools/WorldSliceBuilder/WorldBlackLedger.cs': '3F868C8EA32A1EB84F754398DF60416F93F68DE92B511D1EE36916A2A70C9CE0', 'tools/WorldSliceBuilder/WorldStory.cs': '0262FA206D8867276EE2B516C31BE818CA138BFEB732C6ABD32B794DDE83AFFA', 'tools/papyrus_natives.json': 'BBD41AFAA70F31CBDED8E619B072C7503D069428D2D48A5142846BAB0914C83D', 'tools/papyrus_sim/sim.py': 'FE8469022FBBC90B9E0884E5D5D3A4D45E2E72D91C078D554CF1C50B63080DA3'}
OWN={'tools/BlackLedger/package.py', 'scripts/Source/User/TLM/BlackLedgerTalk.psc', 'scripts/Source/User/TLM/BlackLedgerWalk.psc', 'scripts/Source/User/TLM/BlackLedgerEntry.psc', 'tools/BlackLedger/test_candidate.py', 'tools/BlackLedger/.gitignore', 'tools/BlackLedger/README.md', 'scripts/Source/User/TLM/MQ04Quest.psc', 'tools/BlackLedger/baseline-inventory.json', 'tools/BlackLedger/beckett-lawful.json', 'tools/BlackLedger/character-nodes.json', 'tools/black_ledger_candidate.py', 'tools/PluginBuilder/SpecBlackLedger.cs', 'tools/BlackLedger/.gitattributes', 'tools/BlackLedger/package-inputs.json', 'tools/BlackLedger/audit.py', 'tools/WorldSliceBuilder/WorldBlackLedger.cs', 'tools/BlackLedger/test_black_ledger.py'}

def pin(path):return inventory.pin(path)
def digest(value):return inventory.digest(value)
def expected_names(base):return set(base)|OWN|{NAME}
def describe(root=ROOT):
 inputs=json.loads((root/'tools/BlackLedger/package-inputs.json').read_text(encoding='utf-8'))
 return {'sourceTextSha256':{p.name:pin(p) for p in sorted((root/'scripts/Source/User/TLM').glob('*.psc'))},'runtimeSelection':inputs['selection']}
def problems(root=ROOT):
 out=[]
 try:
  m=json.loads((root/NAME).read_text(encoding='utf-8'));base=json.loads((root/'tools/BlackLedger/baseline-inventory.json').read_text(encoding='utf-8'))
  if (m.get('candidate'),m.get('baseline'),m.get('scripts'))!=('BLACK-LEDGER-RUNTIME-001',BASELINE,38):out.append('Candidate identity changed')
  if digest(base)!=BASELINE_DIGEST:out.append('Exact450 baseline inventory changed')
  expected=dict(base);expected.update(APPROVED)
  for n,value in expected.items():
   if pin(root/n)!=value:out.append('Unapproved source delta: '+n)
  if inventory.current_names(root)!=expected_names(base):out.append('Exact successor source membership changed')
  if m.get('sourceFilesTextSha256')!={n:pin(root/n) for n in sorted(expected_names(base)-{NAME})}:out.append('Manifest source bindings differ')
  state=describe(root)
  for n,value in state.items():
   if m.get(n)!=value:out.append(n+' differs')
  old=json.loads((root/'tools/win/rh-return-account-skeleton-candidate.json').read_text(encoding='utf-8'))
  reused=state['runtimeSelection']['reusedReviewedPex'];fresh=state['runtimeSelection']['freshPex']
  if reused!=old['runtimeSelection']['reusedReviewedPex'] or len(reused)!=16 or len(fresh)!=22:out.append('Normal16/fresh22 selection changed')
  if set(state['sourceTextSha256'])!={n.removesuffix('.pex')+'.psc' for n in set(reused)|set(fresh)} or len(state['sourceTextSha256'])!=38:out.append('Exact38 runtime membership changed')
  for name in reused:
   if state['sourceTextSha256'][name.removesuffix('.pex')+'.psc']!=old['sourceTextSha256'][name.removesuffix('.pex')+'.psc']:out.append('Reused runtime source changed: '+name)
  lines=(root/'tools/PluginBuilder/formkeys.txt').read_text(encoding='utf-8-sig').splitlines(keepends=True)
  prefix=''.join(lines[:3232]);key='tools/PluginBuilder/formkeys.txt'
  if hashlib.sha256(prefix.encode()).hexdigest().upper()!=base[key]:out.append('Original FormID prefix changed')
  if len(lines)%2 or len(set(lines[::2]))!=len(lines)//2 or len(set(lines[1::2]))!=len(lines)//2:out.append('Duplicate/malformed FormID allocation')
  if m.get('measured')!={'compiler':None,'artifact':None,'native':None}:out.append('Source manifest cannot claim runtime measurements')
 except (OSError,ValueError,KeyError,TypeError) as error:out.append('Unreadable candidate: '+str(error))
 return out
if __name__=='__main__':
 if sys.argv[1:]==['verify']:
  errors=problems();print('\n'.join(errors) if errors else 'Black Ledger source candidate PASS;38 sources16 reviewed22 fresh; native separate.');sys.exit(bool(errors))
 print(json.dumps(describe(),indent=2))
