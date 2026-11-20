"""Exact reviewed composition; standalone histories and module guards stay frozen."""
import hashlib,json,subprocess,sys
from pathlib import Path
import player_guidance_candidate as guidance
import rh_terrain_candidate as terrain
ROOT=Path(__file__).resolve().parent.parent
MANIFEST=ROOT/'tools/win/player-guidance-terrain-candidate.json'
BASELINE='fd7ed54181a23ff100b47ddad60caac802eb019c'
BASELINE_DIGEST='9C38382BD59BF25BC3DAD7829ECA538FD039C687B72A422E12E0D3B6D46B990D'
MODULE_PINS={'tools/PluginBuilder/Spec.cs': '8E820376204BAECE8DC46E826CEDFE1D09F57D1A7F0CF5E7A46A68444B2BB00C', 'docs/design/PLAYER_GUIDANCE_001_RECEIPT.md': '5FB26A0CE4AE56A006572CA8A7DF9F22782BF9243DAA9A5659F7B2B7C6BCF7D5', 'tools/PluginBuilder/SpecRedHollow.cs': '48294EFC917CE7342830DF98F481ACE660FA0EF92EDD92A1715905E7D39E58B5', 'tools/papyrus_sim/test_player_guidance_candidate.py': '8E49BFFC4C20268CBD567262DAF2C7F5321DE7A9EAAC738AC438444CE85549E9', 'scripts/Source/User/TLM/MessageStageAlias.psc': 'DA1694ADDFE269D16F769E41AA8322F78E288E11DA228A8BE790BB669FD3CC4F', 'tools/win/player-guidance-candidate.json': 'F0A8B6A6BCAC93711FFF830C8C23F4E786A4D72AF15F0C0C5F899CD89D84B2B5', 'scripts/Source/User/TLM/RedHollowWalk.psc': '71627DC361F768A9BECC79D7379454A9D6C758D28EAC4393C70C3D76D21F586F', 'tools/papyrus_sim/test_player_guidance.py': 'AF90F97F0BEF93DD4CC88CCCF0C87595860F1F0C171A393AB14542C4063B4C85', 'tools/player_guidance_candidate.py': 'A90AFF0E973F456B6C67738E5C1523C1B8C727713A4DF4A3C9A3A13B8442468F', 'docs/design/RH_TERRAIN_002_DONOR_METADATA.json': '76F8FFBB86A9C8CFCB5233156D4A5A0BD74D2D4D41AA3CC79F45F7BE8F018233', 'tools/rh_terrain_donor_probe.py': '32B3C77B835B8CD8A7E51B09E523B19C13CD27A883569C0B396270C5DA671879', 'tools/PluginBuilder/RedHollowTerrain.cs': 'BD62D5D7F9A42762DDD840DC3E0C31197B6865B115800F80952DA692ED5AE206', 'tools/win/rh-terrain-002-candidate.json': '4A6B79C64A44E296B7B5CE608E47FB2E731E4FF4BB0BB974EAD72EC260FE7A9C', 'tools/papyrus_sim/test_rh_terrain_002.py': '2A3139C27BC00915A16AE3B02B98A651CFD3504A27E1D8CC67A2A2220CCF5E0D', 'tools/PluginBuilder/RedHollowEnvironment.cs': '3FEA8E9E45C7E6F9A28C1EDD0E177B1D73B632BD0F2C94AAEC5CC401BAF417EB', 'docs/design/RH_TERRAIN_002.md': 'EFA7432F7C4C31A8C95CA982827B71759A838AA60BC9A1B64C300130C4C1D912', 'tools/rh_terrain_projection.py': '5F10C828DAC5A41BF5534F879026069788B3019053DB3CB2B1C37B63F2D73E0B', 'tools/rh_terrain_candidate.py': '97F6420CE20E18FDA6A7F07975ED6D1A2FD57E12F5F29102EF421D36706C1FE4', 'tools/PluginBuilder/formkeys.txt': 'A5EAAFD17FB307AE80010D7DFA809FEDA5763272F9E2643266352004318C8D92', 'tools/PluginBuilder/RedHollowGeometryAudit.cs': '9174BA2C328BB3B98F1C2E83B5006B0F3464F52D1C1612C4C23B7AEC2707BB2A'}
INTEGRATION_APPROVED={'scripts/Source/User/TLM/RedHollowWalk.psc': '58A0FC82DB46E74243AD8B2161F791CE1D68B8852D0AF050BC4071EC7B4D4F47', 'tools/PluginBuilder/SpecRedHollow.cs': '9C1F7001405EE7FD249EC64215AD6360CB06BC97814D26F88BF1E435C93C1A6E', 'tools/PluginBuilder/last-build.report.txt': 'A825F49E579C48D7CC54EF056689786C9FF1A0036619C3D37521B2D2E3EB1FFA', 'tools/WorldSliceBuilder/WorldRedHollow.cs': '7527FEDEB6CA3E61E12F136D803306DB2F37AD6858CE655B0D0BA56B134DB88F', 'tools/WorldSliceBuilder/WorldRedHollowEnvironment.cs': '1F1ABCDEA50D3D52BA1FFF11EE765500DF2D47F0ABD10E7E4728C1CBA9AF39DF', 'tools/WorldSliceBuilder/StoryCloneCheck.cs': 'B323650A8068297022E903EA41ACB3C28DE3F580DC6ACEF98743B4BE95C9C086', 'tools/check_plugin_layout.py': '3CE8F60C97F116C3A505C4DB79B306BC24E609868F37CD87A5E6AF170BF6BF86', 'tools/run_checks.sh': 'BF0A38F2C2FD0D06373C10232CAE70ADF4247F5CE33863D16983ECB544B9696D'}
OWN={'tools/player_guidance_terrain_candidate.py','tools/player_guidance_terrain_layout.py','tools/composed_test_contexts.py','tools/run_composed_tests.py','tools/papyrus_sim/test_composed_source.py','tools/papyrus_sim/test_player_guidance_terrain.py','docs/design/PLAYER_GUIDANCE_TERRAIN_001_RECEIPT.md'}
NAME='tools/win/player-guidance-terrain-candidate.json'
def pin(path):return guidance.content_digest(path)
def digest(value):return guidance.digest(value)
def expected_names(baseline):return set(baseline)|set(MODULE_PINS)|OWN|{NAME}
def current_names(root):
    if (root/'.git').exists():return set(subprocess.check_output(['git','ls-files','--cached','--others','--exclude-standard'],cwd=root,text=True).splitlines())
    return {p.relative_to(root).as_posix() for p in root.rglob('*') if p.is_file() and not any(n in ('build','bin','obj','.git','__pycache__') for n in p.relative_to(root).parts)}
def describe(root=ROOT):
    state=guidance.describe(root)
    baseline=json.loads((root/'tools/win/player-guidance-candidate.json').read_text(encoding='utf-8'))['baselineFiles']
    state['sourceFilesTextSha256']={n:pin(root/n) for n in sorted(expected_names(baseline)-{NAME})}
    return state
def problems(root=ROOT):
    out=[]
    try:m=json.loads((root/NAME).read_text(encoding='utf-8'))
    except (OSError,ValueError) as e:return ['Combined manifest unreadable: '+str(e)]
    if (m.get('schema'),m.get('candidate'),m.get('baseline'),m.get('scripts'))!=(1,'PLAYER-GUIDANCE-TERRAIN-001',BASELINE,34):out.append('Combined candidate identity altered')
    baseline=m.get('baselineFiles',{})
    if digest(baseline)!=BASELINE_DIGEST:out.append('Full420fd7 baseline anchor altered')
    approved=dict(baseline);approved.update(MODULE_PINS);approved.update(INTEGRATION_APPROVED)
    for n,value in approved.items():
        if pin(root/n)!=value:out.append('Exact accepted/composed source altered: '+n)
    if current_names(root)!=expected_names(baseline):out.append('Exact composed source membership altered')
    try:
        out.extend(terrain.environment_problems(root))
        state=describe(root)
        for n,value in state.items():
            if m.get(n)!=value:out.append(n+' differs from exact current composition')
        if set(state['sourceTextSha256'])!=set(json.loads((root/'tools/win/player-guidance-candidate.json').read_text())['sourceTextSha256']) or len(state['sourceTextSha256'])!=34:out.append('Exact34runtime source membership required')
        if state['runtimeSelection']!=json.loads((root/'tools/win/player-guidance-candidate.json').read_text())['runtimeSelection']:out.append('Exact16reviewed18fresh runtime selection required')
    except (OSError,ValueError,KeyError) as e:out.append('Composed inputs unreadable: '+str(e))
    if set(m.get('measured',{}))!={'masterSha256','worldSha256','runtime','runtimeManifestSha256','freshCompile','measuredBy','measuredFrom','nativeAcceptance'} or any(v is not None for v in m.get('measured',{}).values()):out.append('Source composition cannot claim artifact/native measurements')
    return out
def main(args):
    if args==['verify']:
        found=problems()
        if found:print('\n'.join(found));return 1
        print('Player guidance + terrain source candidate PASS;34sources16reviewed18fresh; compiler/artifact/native acceptance separate.');return 0
    if args==['describe']:print(json.dumps(describe(),indent=2));return 0
    print(__doc__);return 2
if __name__=='__main__':sys.exit(main(sys.argv[1:]))
