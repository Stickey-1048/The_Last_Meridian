#!/usr/bin/env python3
"""CASE-READ-ACCESS-001 strict SOURCE successor; no compile/install/native proof."""
import hashlib,json,sys,re
from pathlib import Path
import red_hollow_environment_candidate as prior
from greenwater_story_candidate import text_digest
ROOT=Path(__file__).resolve().parent.parent
MANIFEST=ROOT/'tools/win/case-read-access-candidate.json'
BASELINE='5c5c82ea438f1f1730480cd8ccd3b4a2d086add3'
# Anchored from the actual accepted Git archive, not from current repinning.
BASELINE_FILES_SHA256='F7EC35979763DFE7B7AF2950F934B5B4B89F0DBF631B34C5D8CA693209D7F7F7'
# Sam signed physical CRLF03FC0450; identical normalized LF text8A432677.
AUTHORITY_PINS={'docs/design/CASE_READ_ACCESS_001_ORDER.md':'50B7B556F76F8FF3723DA10BF70E69A9DEDE9212040D17B0D4B3EE5FE0B76599','docs/design/CASE_READ_ACCESS_001_ADJUDICATION.md':'8A4326778D8FEE790854CED47D30C2B5BA6C3285DE82E194E9ECC8622C3EBFD6'}
BASELINE_MQ03_REMAINDER_SHA256='B91AE1CF5987ED60FECEAD99403AEAAD419C6DD87BFB26BDC458084AA64CD8E8'
ALLOWED_BASELINE_CHANGES=('scripts/Source/User/TLM/MQ03Quest.psc','tools/papyrus_sim/source_snapshot.py','tools/papyrus_sim/test_red_hollow_environment_candidate.py')
OWN_NAMES=('tools/case_read_access_candidate.py','tools/win/Build-CaseReadAccess.ps1','tools/win/tests/Test-CaseReadAccessPackageSafety.ps1','tools/papyrus_sim/test_case_read_access.py','tools/papyrus_sim/test_case_read_access_candidate.py','docs/design/CASE_READ_ACCESS_001_ORDER.md','docs/design/CASE_READ_ACCESS_001_ADJUDICATION.md','docs/design/CASE_READ_ACCESS_001_RECEIPT.md')
FROZEN=prior.FROZEN+('tools/red_hollow_environment_candidate.py','tools/win/red-hollow-environment-candidate.json','tools/win/Build-RedHollowEnvironment.ps1','tools/win/tests/Test-RedHollowEnvironmentPackageSafety.ps1')
SOURCE_GLOBS=prior.SOURCE_GLOBS+('tools/case_read_access_candidate.py','tools/win/Build-CaseReadAccess.ps1','tools/win/tests/Test-CaseReadAccessPackageSafety.ps1','docs/design/CASE_READ_ACCESS_001*.md')

def digest(value):return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':')).encode()).hexdigest().upper()
def content_digest(path):
    if not path.is_file():return None
    data=path.read_bytes()
    try:data=data.decode('utf-8').replace('\r\n','\n').replace('\r','\n').encode('utf-8')
    except UnicodeDecodeError:pass
    return hashlib.sha256(data).hexdigest().upper()
def approved_workflow_timeout(path, baseline_pin):
    # Owner approved ONLY the existing job budget20->40. All other bytes of
    # normalized workflow text must still match the anchored original file.
    try:text=path.read_text(encoding='utf-8').replace('\r\n','\n').replace('\r','\n')
    except (OSError,UnicodeError):return False
    approved='    timeout-minutes: 40\n'
    if text.count(approved)!=1:return False
    original=text.replace(approved,'    timeout-minutes: 20\n')
    return hashlib.sha256(original.encode()).hexdigest().upper()==baseline_pin

def mq03_remainder(text):
    # Freeze all other MQ03 functions/properties/history, especially real44.
    return re.sub(r'(?ms)^bool Function (?:FinalReadAccess|FinishRead)\([^\n]*\)\n.*?^EndFunction\n*','',text.replace('\r\n','\n').replace('\r','\n'))
def describe(root=ROOT):
    previous=prior.describe(root)
    names=sorted({p.relative_to(root).as_posix() for pattern in SOURCE_GLOBS for p in root.glob(pattern) if p.is_file()})
    return {'sourceTextSha256':previous['sourceTextSha256'],'runtimeSelection':previous['runtimeSelection'],
        'sourceFilesTextSha256':{name:text_digest(root/name) for name in names},'frozenTextSha256':{name:text_digest(root/name) for name in FROZEN}}
def problems(root=ROOT,manifest_path=None):
    m=json.loads((manifest_path or root/'tools/win/case-read-access-candidate.json').read_text(encoding='utf-8'));out=[]
    if (m.get('schema'),m.get('candidate'),m.get('baseline'),m.get('scripts'))!=(1,'CASE-READ-ACCESS-001',BASELINE,34):out.append('schema/candidate/baseline/script count altered')
    baseline=m.get('baselineFiles',{})
    if digest(baseline)!=BASELINE_FILES_SHA256:out.append('accepted baseline file membership/pins altered')
    for name,pin in AUTHORITY_PINS.items():
        if content_digest(root/name)!=pin:out.append('approved authority altered: '+name)
    for name,pin in baseline.items():
        if name in ALLOWED_BASELINE_CHANGES or content_digest(root/name)==pin:continue
        if name=='.github/workflows/portable-checks.yml' and approved_workflow_timeout(root/name,pin):continue
        out.append('unrelated accepted baseline file altered: '+name)
    try:now=describe(root)
    except (OSError,ValueError) as exc:return out+['source inputs unreadable: '+str(exc)]
    for key,value in now.items():
        if m.get(key)!=value:out.append(key+' differs from source manifest')
    remainder=mq03_remainder((root/'scripts/Source/User/TLM/MQ03Quest.psc').read_text(encoding='utf-8'))
    if hashlib.sha256(remainder.encode()).hexdigest().upper()!=BASELINE_MQ03_REMAINDER_SHA256:out.append('unrelated MQ03 body altered outside final read boundary')
    old=json.loads((root/'tools/win/red-hollow-environment-candidate.json').read_text(encoding='utf-8'))
    if m.get('baselineSourceTextSha256')!=old['sourceTextSha256']:out.append('baseline runtime source pins altered')
    if len(now['sourceTextSha256'])!=34 or set(now['sourceTextSha256'])!=set(old['sourceTextSha256']):out.append('exactly the existing34script membership required')
    for name,pin in old['sourceTextSha256'].items():
        if name!='MQ03Quest.psc' and now['sourceTextSha256'].get(name)!=pin:out.append('unrelated runtime script altered: '+name)
    if now['runtimeSelection']!=old['runtimeSelection']:out.append('reviewed/fresh runtime membership or selection altered')
    expected=set(old['sourceFilesTextSha256'])|set(OWN_NAMES)
    if set(now['sourceFilesTextSha256'])!=expected:out.append('unapproved source file membership')
    if set(m.get('measured',{}))!={'masterSha256','worldSha256','runtime','runtimeManifestSha256','freshCompile','measuredBy','measuredFrom','nativeAcceptance'} or any(v is not None for v in m.get('measured',{}).values()):out.append('source candidate cannot claim artifact/native measurements')
    return out

def measure(bundle,fresh_compile=None,manifest_path=MANIFEST):return prior.measure(bundle,fresh_compile,manifest_path)
def main(args):
    if args==['verify']:
        found=problems()
        if found:print('\n'.join(found));return 1
        print('Case Read Access source candidate: the checkout is the source its manifest describes (MQ03-only runtime delta; all accepted baseline files guarded). Source only, native acceptance pending.');return 0
    if args==['describe']:print(json.dumps(describe(),indent=2));return 0
    if len(args) in (2,4) and args[0]=='measure' and (len(args)==2 or args[2]=='--fresh-compile'):
        value=measure(Path(args[1]),Path(args[3]) if len(args)==4 else None);print(json.dumps(value,indent=2));return 0 if value['selectionOk'] else 1
    print(__doc__);return 2
if __name__=='__main__':sys.exit(main(sys.argv[1:]))
