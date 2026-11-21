"""NEWworkspace-only36payload candidate, no installed profile/save operation."""
from pathlib import Path
import json,sys
import verify
from pathguard import check_output,check_ancestry
ROOT=Path(__file__).absolute().parent
if len(sys.argv)!=2:raise SystemExit('package.py NEW-package-name')
output=ROOT/'build'/sys.argv[1];check_output(ROOT,output)
errors=verify.problems()
if errors:raise SystemExit(errors)
workspace=ROOT.parents[3];parent=workspace/'work/rh-return-account-build-f491eeb/build/licensed-return-account-skeleton-001';measured=parent/'measured.json';check_ancestry(measured)
if verify.sha(measured)!='BBB41B1F1E95AFD299EED2D0B2E72E9B7B40D913D862076A402D3FA27FB9866B':raise SystemExit('Frozen parent measurement mismatch')
old=json.loads(measured.read_text(encoding='utf-8'));manifest=json.loads((ROOT/'source-receipt.json').read_text(encoding='utf-8'));compiled=json.loads((ROOT/'compile-receipt.json').read_text(encoding='utf-8'))
compile=ROOT/'build/compile-002';pex=compile/'Scripts/TLM/RedHollowWalk.pex';script=verify.REPO/'scripts/Source/User/TLM/RedHollowWalk.psc'
if verify.sha(script)!=compiled['sourceSha256'] or verify.sha(pex)!=compiled['pexSha256'] or verify.sha(compile/'compiler.txt')!=compiled['logSha256'] or verify.sha(compile/'RedHollowWalk.ppj')!=compiled['ppjSha256']:raise SystemExit('Fresh controller compiler binding mismatch')
files={}
for name,h in old['runtime'].items():
 p=parent/'bundle/Scripts/TLM'/name;check_ancestry(p)
 if verify.sha(p)!=h:raise SystemExit('Frozen parent runtime mismatch')
 files['Scripts/TLM/'+name]=pex if name=='RedHollowWalk.pex' else p
if len(files)!=34 or set(files)!={'Scripts/TLM/'+n for n in manifest['sourceTextSha256']}:raise SystemExit('Runtime whitelist mismatch')
files.update({'TheLastMeridian.esp':ROOT/'build/licensed-master-001/TheLastMeridian.esp','TLMWorldSlice.esp':ROOT/'build/licensed-world-003/TLMWorldSlice.esp'})
for n,p in files.items():
 check_ancestry(p)
 if n.endswith('.esp') and verify.sha(p)!=manifest['artifacts'][n]:raise SystemExit('Unreviewed plugin bytes')
errors=verify.artifact_problems(files['TheLastMeridian.esp'],files['TLMWorldSlice.esp'])
if errors:raise SystemExit(errors)
check_output(ROOT,output);output.mkdir()
for name,p in files.items():
 target=output/'bundle'/name;check_ancestry(target);target.parent.mkdir(parents=True,exist_ok=True);check_ancestry(target)
 with target.open('xb') as f:f.write(p.read_bytes())
 if verify.sha(target)!=verify.sha(p):raise SystemExit('Copied byte mismatch')
receipt={'scope':'Measured local candidate; not independent artifact/native acceptance','payloadCount':36,'runtimeCount':34,'runtimeSelection':'33exact acceptedf491carry +1freshcompile002 RedHollowWalk; normalCore unchanged','sourceManifestSha256':verify.sha(ROOT/'source-receipt.json'),'compilerReceiptSha256':verify.sha(ROOT/'compile-receipt.json'),'payloads':{n:verify.sha(p) for n,p in files.items()},'nativeAcceptance':None}
with (output/'package-receipt.json').open('x',encoding='utf-8') as f:json.dump(receipt,f,indent=2);f.write('\n')
print(json.dumps(receipt,indent=2))
