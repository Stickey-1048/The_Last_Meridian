#!/usr/bin/env python3
"""Greenwater clarity and winter relief SOURCE candidate: verify, describe, measure. No install or compile.

Old candidate verifiers/manifests stay frozen and reject this composed source.
Runtime selection reuses only source-identical Details files with recorded
compiled-byte pins; all other scripts come from a full fresh 30-script compile.
Measurements report observed inputs, never manufacture accepted artifact pins.
"""
import hashlib
import json
import sys
from pathlib import Path
from greenwater_story_candidate import text_digest, file_digest, pex, against

ROOT=Path(__file__).resolve().parent.parent
MANIFEST=ROOT/'tools/win/greenwater-relief-candidate.json'
BASELINE='1cdd4666b12e3b40f0c3bf5a3e877f561c7b8d83'
ATTR_LINE='docs/design/NIGHT_MAIL_STORY_001*.md text eol=lf\n'
FROZEN=('tools/win/red-hollow-story-candidate.json','tools/red_hollow_story_candidate.py','tools/win/Build-RedHollow.ps1',
        'tools/win/night-mail-story-candidate.json','tools/night_mail_story_candidate.py','tools/win/Build-NightMail.ps1',
        'docs/design/NIGHT_MAIL_STORY_001_MAPPING.json','tools/win/greenwater-story-candidate.json','tools/greenwater_story_candidate.py','tools/win/Build-Greenwater.ps1',
        'tools/win/mercy-briefing-candidate.json','tools/mercy_briefing_candidate.py',
        'tools/win/world-details-artifact.json','tools/win/world-natural-artifact.json','tools/win/world-story-artifact.json',
        'tools/WorldSliceBuilder/expanded-artifact.json','tools/win/Build-WorldDetails.ps1','tools/win/Build-WorldNatural.ps1',
        'tools/win/Stage-WorldDetails.ps1','tools/win/World-Story.psm1','tools/win/Play-WorldStory.ps1',
        '.github/workflows/portable-checks.yml')
SOURCE_GLOBS=('scripts/Source/User/TLM/*.psc','tools/PluginBuilder/*.cs','tools/PluginBuilder/*.csproj',
              'tools/PluginBuilder/formkeys.txt','tools/PluginBuilder/last-build.report.txt','tools/WorldSliceBuilder/*.cs','tools/WorldSliceBuilder/*.csproj',
              'tools/StandInMaster/*.cs','tools/StandInMaster/*.csproj','tools/logic_model/*.py',
              'tools/papyrus_sim/*.py',
              'tools/greenwater_relief_candidate.py','tools/run_checks.sh','tools/win/Build-GreenwaterRelief.ps1',
              'tools/win/tests/Test-GreenwaterReliefPackageSafety.ps1','tools/win/tests/Test-GreenwaterPackageSafety.ps1',
              'docs/design/RED_HOLLOW_STORY_001_MAPPING.json','docs/design/ACT1_RUNTIME_001_MAPPING.json',
              'docs/design/GREENWATER_STORY_001_MAPPING.json','docs/design/RED_HOLLOW_STORY_001*.md','docs/design/RED_HOLLOW_STORY_001*.json',
              'docs/design/GREENWATER_CLARITY_WINTER_RELIEF*.md','docs/design/GREENWATER_CLARITY_WINTER_RELIEF*.json',
              'docs/design/ACT1_CREATIVE_DECISIONS_2026-11-16.md','tools/papyrus_natives.json','assets/incoming/act1/story/*.json',
              'assets/incoming/act1/story/talk/*.json','assets/incoming/act1/story/quests/*.json')


def describe(root=ROOT):
    files=sorted({p.relative_to(root).as_posix() for glob in SOURCE_GLOBS for p in root.glob(glob) if p.is_file()})
    source={p.name:text_digest(p) for p in sorted((root/'scripts/Source/User/TLM').glob('*.psc'))}
    old=json.loads((root/'tools/win/world-details-artifact.json').read_text())
    reused={pex(n):old['runtime'][pex(n)] for n in sorted(source) if old['sourceTextSha256'].get(n)==source[n] and pex(n) in old['runtime']}
    fresh=sorted(pex(n) for n in source if pex(n) not in reused)
    return {'sourceTextSha256':source,'sourceFilesTextSha256':{n:text_digest(root/n) for n in files},
            'runtimeSelection':{'policy':'Reuse only unchanged source with measured Details PEX pins. Full fresh compile is separate proof; its reviewed 17 files are not bundled. No byte reproducibility assumption.',
                                'reusedReviewedPex':reused,'freshlyCompiled':fresh},
            'frozenTextSha256':{n:text_digest(root/n) for n in FROZEN}}


def problems(root=ROOT,manifest_path=None):
    m=json.loads((manifest_path or root/'tools/win/greenwater-relief-candidate.json').read_text())
    now=describe(root); out=[]
    if m.get('schema')!=1 or m.get('baseline')!=BASELINE:out.append('schema/baseline mismatch')
    for key in now:
        if m.get(key)!=now[key]:out.append(key+' differs from the source manifest')
    if m.get('scripts')!=len(now['sourceTextSha256']) or len(now['sourceTextSha256'])!=30:out.append('exactly 30 script sources required')
    baseline=m.get('baselineSourceTextSha256',{})
    if len(baseline)!=29 or set(now['sourceTextSha256'])!=set(baseline)|{'GreenwaterRelief.psc'}:out.append('accepted 29-script baseline membership changed')
    for name,digest in baseline.items():
        if name not in ('GreenwaterTalk.psc','GreenwaterWalk.psc','MQ02BQuest.psc') and now['sourceTextSha256'].get(name)!=digest:out.append('unrelated accepted source changed: '+name)
    chosen=now['runtimeSelection']; reused=chosen['reusedReviewedPex']; fresh=chosen['freshlyCompiled']
    expected=['Act1Guide.pex','Act1Walk.pex','GreenwaterRelief.pex','GreenwaterTalk.pex','GreenwaterWalk.pex','MQ02AQuest.pex','MQ02BQuest.pex','MQ02CQuest.pex','MercyBriefing.pex','NightMailTalk.pex','NightMailWalk.pex','RedHollowTalk.pex','RedHollowWalk.pex']
    if len(reused)!=17 or fresh!=expected:out.append('runtime selection is not 17 reviewed plus the thirteen required fresh scripts')
    for n,digest in m.get('frozenTextSha256',{}).items():
        if digest!=m.get('baselineFrozenTextSha256',{}).get(n):out.append('frozen baseline altered: '+n)
    if sorted(m.get('baselineFrozenTextSha256',{}))!=sorted(FROZEN):out.append('frozen baseline membership altered')
    attrs=(root/'.gitattributes').read_text(encoding='utf-8')
    if attrs not in (m['baselineAttributes'],m['baselineAttributes']+ATTR_LINE):out.append('frozen attributes altered beyond baseline or exact approved Night Mail LF append')
    ids=(root/'tools/PluginBuilder/formkeys.txt').read_text().splitlines(); before=m['baselineIds']
    if ids[:len(before)]!=before:out.append('earlier form allocation changed')
    try:
        pairs={ids[i]:int(ids[i+1]) for i in range(0,len(ids),2)}
        if len(pairs)*2!=len(ids) or len(set(pairs.values()))!=len(pairs):out.append('duplicate form allocation')
        new=ids[len(before):]; numbers=[int(new[i+1]) for i in range(0,len(new),2)]
        if numbers!=list(range(int(before[-1])+1,int(before[-1])+1+len(numbers))):out.append('new allocations are not a contiguous append')
    except (ValueError,IndexError):out.append('malformed form allocation')
    if any(value is not None for value in m['measured'].values()):out.append('source candidate contains unsupported built/native measurements')
    return out


def measure(bundle,fresh_compile=None,manifest_path=MANIFEST):
    m=json.loads(manifest_path.read_text());chosen=m['runtimeSelection']; pins=chosen['reusedReviewedPex'];fresh=chosen['freshlyCompiled']
    expected=set(pins)|set(fresh)
    runtime={p.name:file_digest(p) for p in sorted((bundle/'Scripts/TLM').glob('*.pex'))}
    compiled={p.name:file_digest(p) for p in sorted(fresh_compile.glob('*.pex'))} if fresh_compile else {}
    failures=[]
    if set(runtime)!=expected:failures.append('runtime membership mismatch')
    if any(runtime.get(n)!=d for n,d in pins.items()):failures.append('reviewed byte pins mismatch')
    if set(compiled)!=expected:failures.append('full fresh compile membership mismatch or absent')
    if any(n not in compiled or runtime.get(n)!=compiled[n] for n in fresh):failures.append('fresh bundle scripts differ from full compile')
    for name in ('TheLastMeridian.esp','TLMWorldSlice.esp'):
        if not (bundle/name).is_file():failures.append('missing '+name)
    return {'what':'MEASURED ONLY; not a native acceptance or new artifact pin','sourceManifestSha256':file_digest(manifest_path),
            'plugins':{n:file_digest(bundle/n) if (bundle/n).is_file() else None for n in ('TheLastMeridian.esp','TLMWorldSlice.esp')},
            'runtime':runtime,'fullFreshCompile':compiled,'runtimeManifestSha256':hashlib.sha256(''.join(n+' '+runtime[n]+'\n' for n in sorted(runtime)).encode()).hexdigest().upper(),
            'selectionOk':not failures,'problems':failures}


def main(args):
    if args==['verify']:
        found=problems()
        if found:
            print('\n'.join(found));return 1
        print('Greenwater relief source candidate: the checkout is the source its manifest describes (30 scripts; 17 reviewed and thirteen fresh). Source only; native acceptance pending.');return 0
    if args==['describe']:print(json.dumps(describe(),indent=2));return 0
    if len(args) in (2,4) and args[0]=='measure' and (len(args)==2 or args[2]=='--fresh-compile'):
        result=measure(Path(args[1]),Path(args[3]) if len(args)==4 else None);print(json.dumps(result,indent=2));return 0 if result['selectionOk'] else 1
    print(__doc__);return 2


if __name__=='__main__':sys.exit(main(sys.argv[1:]))
