#!/usr/bin/env python3
"""PLAYER-GUIDANCE-001 strict source successor; no artifact/native readiness."""
import hashlib,json,sys
from pathlib import Path
import case_read_access_candidate as prior
ROOT=Path(__file__).resolve().parent.parent
MANIFEST=ROOT/'tools/win/player-guidance-candidate.json'
BASELINE='fd7ed54181a23ff100b47ddad60caac802eb019c'
BASELINE_FILES_SHA256='9C38382BD59BF25BC3DAD7829ECA538FD039C687B72A422E12E0D3B6D46B990D'
# Exact bounded reviewed delta: a current-manifest repin cannot waive it.
APPROVED={'scripts/Source/User/TLM/MessageStageAlias.psc': 'DA1694ADDFE269D16F769E41AA8322F78E288E11DA228A8BE790BB669FD3CC4F', 'scripts/Source/User/TLM/RedHollowWalk.psc': '71627DC361F768A9BECC79D7379454A9D6C758D28EAC4393C70C3D76D21F586F', 'tools/PluginBuilder/Spec.cs': '8E820376204BAECE8DC46E826CEDFE1D09F57D1A7F0CF5E7A46A68444B2BB00C', 'tools/PluginBuilder/SpecRedHollow.cs': '48294EFC917CE7342830DF98F481ACE660FA0EF92EDD92A1715905E7D39E58B5'}
OWN=('tools/player_guidance_candidate.py','tools/papyrus_sim/test_player_guidance.py','tools/papyrus_sim/test_player_guidance_candidate.py','docs/design/PLAYER_GUIDANCE_001_RECEIPT.md')
SOURCE_GLOBS=prior.SOURCE_GLOBS+('tools/player_guidance_candidate.py','docs/design/PLAYER_GUIDANCE_001*.md')

def digest(value):return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':')).encode()).hexdigest().upper()
def content_digest(path):return prior.content_digest(path)
def describe(root=ROOT):
    value=prior.describe(root)
    names=sorted({p.relative_to(root).as_posix() for pattern in SOURCE_GLOBS for p in root.glob(pattern) if p.is_file()})
    value['sourceFilesTextSha256']={n:content_digest(root/n) for n in names}
    return value

def problems(root=ROOT,manifest_path=None):
    m=json.loads((manifest_path or root/'tools/win/player-guidance-candidate.json').read_text(encoding='utf-8'));out=[]
    if (m.get('schema'),m.get('candidate'),m.get('baseline'),m.get('scripts'))!=(1,'PLAYER-GUIDANCE-001',BASELINE,34):out.append('schema/candidate/baseline/script membership mismatch')
    baseline=m.get('baselineFiles',{})
    if digest(baseline)!=BASELINE_FILES_SHA256:out.append('full accepted fd7 baseline membership/pins altered')
    for name,pin in baseline.items():
        if content_digest(root/name)!=(APPROVED.get(name) or pin):out.append('unapproved source delta: '+name)
    github={p.relative_to(root).as_posix() for p in (root/'.github').rglob('*') if p.is_file()}
    if github!={n for n in baseline if n.startswith('.github/')}:out.append('unapproved GitHub file membership')
    for name,pin in APPROVED.items():
        if content_digest(root/name)!=pin:out.append('approved guidance delta altered: '+name)
    now=describe(root)
    for name,value in now.items():
        if m.get(name)!=value:out.append(name+' differs from current source')
    try:old=json.loads((root/'tools/win/case-read-access-candidate.json').read_text(encoding='utf-8'))
    except (OSError,ValueError):return out+['accepted CASE manifest unreadable']
    if set(now['sourceFilesTextSha256'])!=set(old['sourceFilesTextSha256'])|set(OWN):out.append('unapproved source membership')
    if len(now['sourceTextSha256'])!=34 or set(now['sourceTextSha256'])!=set(old['sourceTextSha256']):out.append('exact existing34scripts required')
    selection=now['runtimeSelection'];before=old['runtimeSelection']
    expected=dict(before['reusedReviewedPex']);expected.pop('MessageStageAlias.pex')
    if selection['reusedReviewedPex']!=expected or selection['freshlyCompiled']!=sorted(before['freshlyCompiled']+['MessageStageAlias.pex']):out.append('exact16reviewed18fresh selection required')
    if set(m.get('measured',{}))!={'masterSha256','worldSha256','runtime','runtimeManifestSha256','freshCompile','measuredBy','measuredFrom','nativeAcceptance'} or any(v is not None for v in m.get('measured',{}).values()):out.append('source-only candidate cannot claim artifact/native measurements')
    return out

def main(args):
    if args==['verify']:
        found=problems()
        if found:print('\n'.join(found));return 1
        print('Player guidance source candidate PASS;34sources,16reviewed18fresh; artifact/native gates pending.');return 0
    if args==['describe']:print(json.dumps(describe(),indent=2));return 0
    print(__doc__);return 2
if __name__=='__main__':sys.exit(main(sys.argv[1:]))
