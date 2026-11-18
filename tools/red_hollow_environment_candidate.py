#!/usr/bin/env python3
"""Red Hollow Environment SOURCE candidate: verify, describe, measure.
No install/compiler/native execution. Prior source verifiers remain frozen.
"""
import hashlib,json,sys
from pathlib import Path
import four_flags_candidate as prior
from greenwater_story_candidate import text_digest,file_digest,pex

ROOT=Path(__file__).resolve().parent.parent
MANIFEST=ROOT/'tools/win/red-hollow-environment-candidate.json'
BASELINE='d43bd336fde2837c9c499b273c4becdee3f4cef9'
ATTR_LINE=prior.ATTR_LINE
FROZEN=tuple(dict.fromkeys(prior.FROZEN+(
    'tools/win/four-flags-candidate.json','tools/four_flags_candidate.py','tools/win/Build-FourFlags.ps1','tools/win/tests/Test-FourFlagsPackageSafety.ps1',
    'tools/PluginBuilder/SpecFourFlags.cs','tools/WorldSliceBuilder/WorldFourFlags.cs')+
    tuple(p.relative_to(ROOT).as_posix() for p in sorted((ROOT/'docs/design').glob('FOUR_FLAGS_STORY_001*')) if p.is_file())))
SOURCE_GLOBS=prior.SOURCE_GLOBS+('tools/red_hollow_environment_candidate.py','tools/win/Build-RedHollowEnvironment.ps1',
    'tools/check_plugin_layout.py',
    'tools/win/tests/Test-RedHollowEnvironmentPackageSafety.ps1','docs/design/RED_HOLLOW_ENVIRONMENT_001*.md','docs/design/RED_HOLLOW_ENVIRONMENT_001*.json')
CONTRACT_PINS={
    'docs/design/RED_HOLLOW_ENVIRONMENT_001_CONTRACT.md':'F2CD5E066395A3E1ACA9854D33AEC20DA13FC5D7BC02EBCBD9AC52CAE3B2CFA2',
    # Signed raw CRLF receipt6E034CAA; this is its identical logical LF text.
    'docs/design/RED_HOLLOW_ENVIRONMENT_001_SAM_REVIEW.md':'236BF144A67BBE36C0C4C3CD8F0670D8E31FC9516A9D2FFEA95FA30A170F8BF9',
    'docs/design/RED_HOLLOW_ENVIRONMENT_001_ORDER.md':'830DEF3D9F6FD6308EDFD98F2D3268CBD4294291F3A0724F47084DDD1F039479'}
# Filled from the actual accepted Git baseline, never from a current repin.
BASELINE_IDS_SHA256='C211FF6B295CA95B8EF6CEF517CF93C2011AAEEE269D395D443A2729F26E4481'
BASELINE_FROZEN_SHA256='33AB0B21A613D0F2EE9ED3A04292623704440539C6E30D44B901631890091931'


def digest(value):return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':')).encode()).hexdigest().upper()
def describe(root=ROOT):
    source={p.name:text_digest(p) for p in sorted((root/'scripts/Source/User/TLM').glob('*.psc'))}
    details=json.loads((root/'tools/win/world-details-artifact.json').read_text())
    reused={pex(n):details['runtime'][pex(n)] for n in sorted(source) if details['sourceTextSha256'].get(n)==source[n] and pex(n) in details['runtime']}
    files=sorted({p.relative_to(root).as_posix() for pattern in SOURCE_GLOBS for p in root.glob(pattern) if p.is_file()})
    return {'sourceTextSha256':source,'sourceFilesTextSha256':{n:text_digest(root/n) for n in files},
        'runtimeSelection':{'policy':'Measured source membership: source-identical pinned Details PEX only; every other PEX from the full fresh current compile. Fresh reviewed variants are proof only, never substituted.',
            'reusedReviewedPex':reused,'freshlyCompiled':sorted(pex(n) for n in source if pex(n) not in reused)},
        'frozenTextSha256':{n:text_digest(root/n) for n in FROZEN}}


def problems(root=ROOT,manifest_path=None):
    m=json.loads((manifest_path or root/'tools/win/red-hollow-environment-candidate.json').read_text());now=describe(root);out=[]
    if m.get('schema')!=1 or m.get('candidate')!='RED-HOLLOW-ENVIRONMENT-001' or m.get('baseline')!=BASELINE:out.append('schema/candidate/baseline mismatch')
    for key in now:
        if m.get(key)!=now[key]:out.append(key+' differs from the source manifest')
    old=json.loads((root/'tools/win/four-flags-candidate.json').read_text())
    if m.get('baselineSourceTextSha256')!=old['sourceTextSha256']:out.append('baseline script pins altered')
    if m.get('scripts')!=34 or len(now['sourceTextSha256'])!=34 or set(now['sourceTextSha256'])!=set(old['sourceTextSha256']):out.append('exactly 34 existing script sources required')
    for name,pin in old['sourceTextSha256'].items():
        if name not in ('MQ02CQuest.psc','RedHollowWalk.psc','RedHollowTalk.psc') and now['sourceTextSha256'].get(name)!=pin:out.append('unrelated accepted source changed: '+name)
    selection=now['runtimeSelection'];baseline_selection=old['runtimeSelection']
    if selection['reusedReviewedPex']!=baseline_selection['reusedReviewedPex'] or selection['freshlyCompiled']!=baseline_selection['freshlyCompiled']:out.append('runtime membership/pinned reviewed selection changed')
    frozen=m.get('baselineFrozenTextSha256',{})
    if digest(frozen)!=BASELINE_FROZEN_SHA256 or sorted(frozen)!=sorted(FROZEN):out.append('frozen baseline membership/pins altered')
    for name,pin in now['frozenTextSha256'].items():
        if pin!=frozen.get(name):out.append('frozen baseline altered: '+name)
    for name,pin in CONTRACT_PINS.items():
        if text_digest(root/name)!=pin:out.append('approved environment contract altered: '+name)
    attrs=(root/'.gitattributes').read_text(encoding='utf-8')
    if m.get('baselineAttributes')!=old['baselineAttributes']:out.append('baseline attribute pins altered')
    if attrs not in (m['baselineAttributes'],m['baselineAttributes']+ATTR_LINE):out.append('frozen attributes altered beyond baseline or exact approved Night Mail LF append')
    ids=(root/'tools/PluginBuilder/formkeys.txt').read_text().splitlines();before=m.get('baselineIds',[])
    if digest(before)!=BASELINE_IDS_SHA256:out.append('baseline allocation pins altered')
    if ids[:len(before)]!=before:out.append('earlier form allocation changed')
    try:
        pairs={ids[i]:int(ids[i+1]) for i in range(0,len(ids),2)}
        if len(pairs)*2!=len(ids) or len(set(pairs.values()))!=len(pairs):out.append('duplicate form allocation')
        new=ids[len(before):];numbers=[int(new[i+1]) for i in range(0,len(new),2)]
        if numbers!=list(range(int(before[-1])+1,int(before[-1])+1+len(numbers))):out.append('new allocations are not a contiguous append')
    except(ValueError,IndexError):out.append('malformed form allocation')
    if set(m.get('measured',{}))!={'masterSha256','worldSha256','runtime','runtimeManifestSha256','freshCompile','measuredBy','measuredFrom','nativeAcceptance'} or any(v is not None for v in m.get('measured',{}).values()):out.append('source candidate contains absent or unsupported artifact/native measurements')
    return out


def measure(bundle,fresh_compile=None,manifest_path=MANIFEST):return prior.measure(bundle,fresh_compile,manifest_path)
def main(args):
    if args==['verify']:
        found=problems()
        if found:print('\n'.join(found));return 1
        print('Red Hollow Environment source candidate: the checkout is the source its manifest describes (34 scripts; actual reviewed/fresh selection measured). Source only; native acceptance pending.');return 0
    if args==['describe']:print(json.dumps(describe(),indent=2));return 0
    if len(args) in(2,4) and args[0]=='measure' and(len(args)==2 or args[2]=='--fresh-compile'):
        result=measure(Path(args[1]),Path(args[3]) if len(args)==4 else None);print(json.dumps(result,indent=2));return 0 if result['selectionOk'] else 1
    print(__doc__);return 2
if __name__=='__main__':sys.exit(main(sys.argv[1:]))
