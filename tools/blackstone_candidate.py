"""Strict full3374 successor; historical guards/manifests remain byte-frozen."""
from pathlib import Path
import hashlib,json,sys
import player_guidance_terrain_candidate as inventory
ROOT=Path(__file__).resolve().parents[1]
BASELINE='3374f81312b6d69fc9e839eeff6348a925af361e'
BASELINE_DIGEST='F6A0A0733036CA72C5C69D6F5675860E9265F69E8EC772F5DF22E868740B6441'
APPROVED={'scripts/Source/User/TLM/BlackLedgerWalk.psc': '15B96A7C042176F5876175E9099A921BB6E7D91B03B0785F69FE6E1E742191C5', 'scripts/Source/User/TLM/BlackstoneTalk.psc': '60361EFE575409BC154A7F74278E3FF2E3F491A58E6B0AD83902B07853995B53', 'scripts/Source/User/TLM/BlackstoneWalk.psc': '658E855616C9988378C9A9BE5AFE723020A92B68E21262852DC2034066F7A83F', 'scripts/Source/User/TLM/MQ04Quest.psc': '9FD8957F531695AF9E47C2A599CEC1A1117C1214C133F4E21D6ED243A44C7E44', 'scripts/Source/User/TLM/MQ05Quest.psc': '6109BD0E9CFE0247FDCE2B463610BFE2055918A829CB2697CA2963612E6A7DC9', 'tools/Blackstone/.gitattributes': 'F5894147FE62EF51657A3A31B6C380B782FE35D9A92643BBBC022EF665855307', 'tools/Blackstone/.gitignore': '166A67D2AD7184FC83F29998CF8077D368B502D266E2EC0ECA9399F0254961DC', 'tools/Blackstone/HANDOFF.md': '2EB22FE477DE1A860B39E774317099F96937F8F5DDC5E4EFDB71EF06612DCF12', 'tools/Blackstone/README.md': 'C9A7B758A4B08963109DB02893CBB97495570DACCA25AF935D519A94D777B18E', 'tools/Blackstone/audit.py': '5C032B72F4D25E145A67991C9F55671A5AD6F8767CABD69844F5418F4EFE77B8', 'tools/Blackstone/baseline-inventory.json': 'DEAE779FF3D9EE6E2F4E66C9A0B4851F659FC8A36C41EC04E3AE95C6D857B99A', 'tools/Blackstone/layout-integration.json': 'D718278D16AB5DB3739A58BD659553A950D3BC38AA9504D8F778851FD76BB6CF', 'tools/Blackstone/layout-light.json': '80A8886D0129199F9723B51EF3A4B659F85D7F6DC2E84508CA74DD05CC6219DF', 'tools/Blackstone/layout-models.json': 'DC471FEDB269E5EA8B899F768F4CC194C801E5E84F4242FB8C4727C10F1A079D', 'tools/Blackstone/layout-placements.json': '934FEFCA3784D13DEFBCC38838982D90677654E03F89CA8533C16E93DF03C13B', 'tools/Blackstone/layout-provenance.json': '4C6FBC7E63B42C7924E041490989F612E8372F7FB40F9F332227635F968113D3', 'tools/Blackstone/layout-repair-evidence.json': '68B91085A742243FD4E02F6F5891ED5AF1BA59D6AFC9F24D4A769A0956CDE31F', 'tools/Blackstone/package-inputs.json': '99F080FD1A2822947AA92EA028A4F8DD7E1C702932022CA74E09F937F39B505E', 'tools/Blackstone/package.py': '02863FED95E48C48F401D72FE5707907DBFDBC44BB93FCF49A26013B1966A1AC', 'tools/Blackstone/packet.json': '03A6602563415321BD1B8DB6BDD3342E5D8259442B7AAC8BE33A93991C533571', 'tools/Blackstone/test_blackstone.py': 'F261BE4B02ECD8512794516BA05BB988F9B36123D826436C40E5C7D463628C95', 'tools/Blackstone/test_candidate.py': '152AD07371FC20A6D89F0D1FEAA66227B497DBB5F4A39843BC8705973927694A', 'tools/Blackstone/test_mq04_current.py': '67A1895C3F71A625F784B18CF7851D4DF9069A819E1A346F1CD5C42EA9BC0A74', 'tools/PluginBuilder/BlackstoneEnvironment.cs': '96AD608019BA73437624DBC06A7E68F76328F4F40FC39A269EF4ADB558B98060', 'tools/PluginBuilder/Builder.cs': '48B808F76AFE8CEEC4DD2492536411595B38EF804B6BC77E2339A2EB25E10C56', 'tools/PluginBuilder/Program.cs': '67FE463841BF62A187FBA10D0D5A84BF498A825750A0C2BD5CF3D05B431C26D3', 'tools/PluginBuilder/Report.cs': '4083F0A1ADEE7AB121FE478E9E28A1C2509B3984E1FB3DA576B7ACD4D051F57A', 'tools/PluginBuilder/SelfCheck.cs': 'F4774FD6786EB471A76F41DC14700B31EEACDCC4684001BA3B362D4EAE85A888', 'tools/PluginBuilder/Spec.cs': '34C05962D5227A1493A8E5DDF37EEAA60EA0D2AA7EECC14F2353DD29AE29944C', 'tools/PluginBuilder/SpecBlackLedger.cs': 'FB731120C0D45564ED7B7F3A691A07B9566562636BE8623CD19832949079594A', 'tools/PluginBuilder/SpecBlackstone.cs': 'B8534F7BF4DF09D9CE2D9B321B03BE661F7BDFD920DE8D59DEED887DCF3F07D0', 'tools/PluginBuilder/formkeys.txt': 'E28B3B152A2FB3F6D5867E78DC5D7D30CDA479EA45041B578806953846421ACC', 'tools/StandInMaster/BlackstoneFixture.cs': 'D935355D73533D1FF9ED287663B3226A93ED4830414CC76A0D86ED35C6869502', 'tools/StandInMaster/Program.cs': '618E61FD1BF96EC7EF7D5CF771BED9F6C98AA62D3EE7ECC90AB76F080BD396DE', 'tools/papyrus_natives.json': 'A34FE193821AFBAEE6A9D7CA9EFBDC8EE2C3DE7B30F25DE38DE25E20864E1116', 'tools/papyrus_sim/sim.py': '57D68E97A0C2FF3863A996BC1B73C576DF50112610A23440D1584378AF3F730D'}
OWN={'tools/Blackstone/layout-placements.json', 'tools/Blackstone/layout-models.json', 'tools/Blackstone/package-inputs.json', 'tools/blackstone_candidate.py', 'scripts/Source/User/TLM/BlackstoneTalk.psc', 'tools/Blackstone/layout-repair-evidence.json', 'tools/PluginBuilder/SpecBlackstone.cs', 'tools/Blackstone/baseline-inventory.json', 'tools/Blackstone/packet.json', 'tools/Blackstone/layout-provenance.json', 'tools/Blackstone/.gitattributes', 'tools/Blackstone/HANDOFF.md', 'tools/Blackstone/.gitignore', 'tools/PluginBuilder/BlackstoneEnvironment.cs', 'tools/Blackstone/package.py', 'tools/StandInMaster/BlackstoneFixture.cs', 'tools/Blackstone/layout-light.json', 'tools/Blackstone/test_mq04_current.py', 'tools/Blackstone/test_blackstone.py', 'tools/Blackstone/test_candidate.py', 'tools/Blackstone/README.md', 'tools/Blackstone/audit.py', 'tools/Blackstone/layout-integration.json', 'scripts/Source/User/TLM/MQ05Quest.psc', 'scripts/Source/User/TLM/BlackstoneWalk.psc'}
NAME='tools/win/blackstone-candidate.json'
pin=inventory.pin;digest=inventory.digest

def expected_names(root=ROOT):return set(json.loads((root/'tools/Blackstone/baseline-inventory.json').read_text(encoding='utf-8')))|OWN|{NAME}
def describe(root=ROOT):
 meta=json.loads((root/'tools/Blackstone/package-inputs.json').read_text(encoding='utf-8'))
 return {'sourceTextSha256':{p.name:pin(p)for p in sorted((root/'scripts/Source/User/TLM').glob('*.psc'))},'runtimeSelection':meta['selection']}
def problems(root=ROOT):
 out=[]
 try:
  base=json.loads((root/'tools/Blackstone/baseline-inventory.json').read_text(encoding='utf-8'));m=json.loads((root/NAME).read_text(encoding='utf-8'))
  if len(base)!=477 or digest(base)!=BASELINE_DIGEST:out.append('Exact full477 baseline changed')
  if (m.get('candidate'),m.get('baseline'),m.get('scripts'))!=('BLACKSTONE-RUNTIME-001',BASELINE,41):out.append('Candidate identity changed')
  expected=dict(base);expected.update(APPROVED)
  for name,value in expected.items():
   if pin(root/name)!=value:out.append('Unapproved source delta: '+name)
  names=set(base)|OWN|{NAME}
  if inventory.current_names(root)!=names:out.append('Exact source membership changed')
  if m.get('sourceFilesTextSha256')!={n:pin(root/n)for n in sorted(names-{NAME})}:out.append('Source manifest bindings differ')
  state=describe(root)
  for name,value in state.items():
   if m.get(name)!=value:out.append(name+' differs')
  old=json.loads((root/'tools/win/black-ledger-final-read-candidate.json').read_text(encoding='utf-8'));reused=state['runtimeSelection']['reusedReviewedPex'];fresh=state['runtimeSelection']['freshPex']
  if reused!=old['runtimeSelection']['reusedReviewedPex'] or len(reused)!=16 or len(fresh)!=25:out.append('Exact normal16/fresh25 selection changed')
  if len(state['sourceTextSha256'])!=41 or set(state['sourceTextSha256'])!={n.removesuffix('.pex')+'.psc'for n in set(reused)|set(fresh)}:out.append('Exact41 runtime membership changed')
  changed={n for n,v in old['sourceTextSha256'].items()if state['sourceTextSha256'].get(n)!=v}
  if changed!={'MQ04Quest.psc','BlackLedgerWalk.psc'}:out.append('Prior runtime changes exceed exact MQ04 handoff')
  for name in reused:
   src=name.removesuffix('.pex')+'.psc'
   if state['sourceTextSha256'][src]!=old['sourceTextSha256'][src]:out.append('Reused source changed: '+src)
  lines=(root/'tools/PluginBuilder/formkeys.txt').read_text(encoding='utf-8-sig').splitlines(keepends=True)
  if hashlib.sha256(''.join(lines[:3428]).encode()).hexdigest().upper()!=base['tools/PluginBuilder/formkeys.txt']:out.append('Original full FormID prefix changed')
  if len(lines)%2 or len(set(lines[::2]))!=len(lines)//2 or len(set(lines[1::2]))!=len(lines)//2:out.append('Malformed/duplicate FormIDs')
  if m.get('measured')!={'compiler':None,'artifact':None,'native':None}:out.append('Source manifest cannot claim native/artifact acceptance')
 except (OSError,ValueError,KeyError,TypeError)as error:out.append('Unreadable candidate: '+str(error))
 return out
if __name__=='__main__':
 if sys.argv[1:]==['verify']:
  errors=problems();print('\n'.join(errors)if errors else 'Blackstone source candidate PASS;41normal sources16reviewed25fresh; native separate.');sys.exit(bool(errors))
 print(json.dumps(describe(),indent=2))
