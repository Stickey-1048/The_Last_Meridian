"""Workspace-only43-file UI candidate, all preflight before exclusive output."""
from pathlib import Path
import json
import verify_footer as v
R=v.REPO;Q=v.ROOT

def safe(p):
 for x in(p,*p.parents):
  if x.exists()or x.is_symlink():
   if x.is_symlink()or getattr(x.lstat(),'st_file_attributes',0)&1024:raise ValueError('Reparse ancestor')
 return p

def prepare():
 v.run();source=json.loads((Q/'source-receipt.json').read_text(encoding='utf-8'));old=v.OLD/'tools/Blackstone/build/package-001/receipt.json';assert v.sha(old)==source['oldPackageReceiptSha256'];m=json.loads(old.read_text(encoding='utf-8'));pins=dict(m['payloads']);pins['TheLastMeridian.esp']=source['masterSha256'];assert len(pins)==43
 paths={n:(Q/'build/master-001/TheLastMeridian.esp'if n=='TheLastMeridian.esp'else v.BUNDLE/n)for n in pins}
 for n,p in paths.items():assert v.sha(safe(p))==pins[n]
 compile=v.OLD/'tools/Blackstone/build/compile-custody-001/receipt.json';assert v.sha(compile)==source['unchangedRuntimeCompileReceiptSha256'];assert json.loads(compile.read_text(encoding='utf-8'))['logSummary']=='41 succeeded, 0 failed'
 out=safe(Q/'build/package-001');assert not out.exists(),'Never overwrite/adopt existing output';out.mkdir();bundle=out/'bundle';bundle.mkdir()
 for name,p in paths.items():
  target=safe(bundle/name);target.parent.mkdir(parents=True,exist_ok=True)
  with target.open('xb')as f:f.write(p.read_bytes())
  assert v.sha(target)==pins[name]
 receipt={'sourceReceiptSha256':v.sha(Q/'source-receipt.json'),'payloads':pins,'runtimePolicy':'ALL41runtime+world literal acceptededd, no new Papyrus compile; exact41PSC source pins verified','oldPackageReceiptSha256':v.sha(old),'carriedCompilerReceiptSha256':v.sha(compile),'noInstalledWrites':True,'rendererNativeAcceptance':None};(out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8',newline='\n');print('PASS43 workspace payloads; Hub-only UI mitigation, native untested')
if __name__=='__main__':prepare()
