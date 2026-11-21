"""NEW workspace-only four-payload addon packaging. No installed targets or cleanup."""
from pathlib import Path
import hashlib,json,sys
import verify
from pathguard import check_output,check_ancestry
ROOT=Path(__file__).absolute().parent
if len(sys.argv)!=2:raise SystemExit('package.py NEW-NAME')
name=sys.argv[1]
if not name or name in ('.','..') or any(c not in 'abcdefghijklmnopqrstuvwxyz0123456789-' for c in name):raise SystemExit('Unsafe new package name')
output=ROOT/'build'/name
check_output(ROOT,output)
errors=verify.source_problems()
if errors:raise SystemExit(errors)
source=ROOT/'build/pilot-002'
check_ancestry(source/'voice-mapping.json');check_ancestry(source/'TLMVoiceNativePilot.esp')
if verify.sha(source/'voice-mapping.json')!='144638F378D6BC4D820678A9E5F1311B2593DA83F79213D10416C84C283F7389' or verify.sha(source/'TLMVoiceNativePilot.esp')!='D1CAB85562A365892D62423A9A0C68C124055DCA8666300691418BF8E0FFD0B4':raise SystemExit('Frozen builder mapping/plugin mismatch')
mapping=json.loads((source/'voice-mapping.json').read_text(encoding='utf-8'));base=ROOT.parents[3]/'work/rh-return-account-build-f491eeb/build/licensed-return-account-skeleton-001/bundle/TheLastMeridian.esp'
errors=verify.artifact_problems(source/'TLMVoiceNativePilot.esp',mapping,base)
if errors:raise SystemExit(errors)
compile=ROOT/'build/compile-005';log=(compile/'compiler.txt').read_text(encoding='utf-8-sig')
if '1 succeeded, 0 failed' not in log:raise SystemExit('Compiler gate not clear')
pex=compile/'Scripts/TLMDev/VoicePilot.pex'
compiled=json.loads((ROOT/'compile-receipt.json').read_text())
if compiled['sourceSha256']!=verify.sha(ROOT/'scripts/TLMDev/VoicePilot.psc') or compiled['pexSha256']!=verify.sha(pex) or compiled['compilerLogSha256']!=verify.sha(compile/'compiler.txt') or compiled['ppjSha256']!=verify.sha(compile/'VoicePilot.ppj'):raise SystemExit('Exact compiler/source binding failed')
files={'TLMVoiceNativePilot.esp':source/'TLMVoiceNativePilot.esp','Scripts/TLMDev/VoicePilot.pex':pex}
for row in mapping['rows']:
 f=Path(row['sourceFuz'])
 if verify.sha(f)!=row['fuzSha256']:raise SystemExit('Original FUZ hash mismatch')
 files[row['relativePath']]=f
expected={'TLMVoiceNativePilot.esp','Scripts/TLMDev/VoicePilot.pex','Sound/Voice/TLMVoiceNativePilot.esp/MaleRough/00000802_1.fuz','Sound/Voice/TLMVoiceNativePilot.esp/FemaleEvenToned/00000808_1.fuz'}
if set(files)!=expected:raise SystemExit('Wrong exact payload set')
check_output(ROOT,output)
output.mkdir() # exclusive, never adopts an existing directory
for relative,file in files.items():
 check_ancestry(file)
 dest=output/'bundle'/relative;check_ancestry(dest);dest.parent.mkdir(parents=True,exist_ok=True);check_ancestry(dest)
 with dest.open('xb') as handle:handle.write(file.read_bytes())
 if verify.sha(dest)!=verify.sha(file):raise SystemExit('Copied payload readback mismatch')
receipt={'scope':'Workspace-only opt-in voice addon; NO install/native/listening/accent approval','payloads':{k:verify.sha(v) for k,v in files.items()},'compiledSourceSha256':verify.sha(ROOT/'scripts/TLMDev/VoicePilot.psc'),'compilerLogSha256':verify.sha(compile/'compiler.txt'),'ppjSha256':verify.sha(compile/'VoicePilot.ppj'),'mappingSha256':verify.sha(source/'voice-mapping.json'),'baseSource':'f491eeb4e670d306530446b60f82785950dbb747','basePlugin':verify.sha(base),'nativeAcceptance':None}
with (output/'package-receipt.json').open('x',encoding='utf-8') as f:json.dump(receipt,f,indent=2);f.write('\n')
print(json.dumps(receipt,indent=2))
