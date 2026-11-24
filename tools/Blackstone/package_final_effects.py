"""Workspace-only packaging of a source-verified, fully measured lawful MQ04 candidate."""
from pathlib import Path
import hashlib,json,re,sys,os
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools'))
import blackstone_final_effects_candidate as source
TASK=ROOT/'tools/Blackstone'

def raw(path):return hashlib.sha256(path.read_bytes()).hexdigest().upper()
def safe(path):
 for item in (path,*path.parents):
  if item.exists() or item.is_symlink():
   info=item.lstat()
   if item.is_symlink() or getattr(info,'st_file_attributes',0)&0x400:raise ValueError('Reparse/symlink ancestor: '+str(item))
 return path

def inputs():
 errors=source.problems()
 if errors:raise ValueError('\n'.join(errors))
 meta=json.loads((TASK/'final-effects-package-inputs.json').read_text(encoding='utf-8'))
 compile=TASK/'build/compile-repair-001';receipt=compile/'receipt.json'
 if raw(receipt)!=meta['compileReceipt']:raise ValueError('Compile receipt changed')
 data=json.loads(receipt.read_text(encoding='utf-8'))
 if data['logSummary']!='41 succeeded, 0 failed' or len(data['sources'])!=41 or len(data['compiled'])!=41:raise ValueError('Full41 compile missing')
 if raw(compile/'compiler.txt')!=data['compilerLog']:raise ValueError('Actual compiler log changed')
 for name,pin in data['sources'].items():
  if source.pin(ROOT/'scripts/Source/User/TLM'/name)!=pin:raise ValueError('Compiled source stale: '+name)
 for name,pin in data['compiled'].items():
  if raw(compile/'Scripts'/name)!=pin:raise ValueError('Compiled artifact changed: '+name)
 parent=ROOT.parent/'rh-return-account-build-f491eeb/build/licensed-return-account-skeleton-001/bundle'
 payload={name:(TASK/path) for name,path in meta['plugins'].items()}
 selection=source.describe()['runtimeSelection']
 for name,pin in selection['reusedReviewedPex'].items():
  path=parent/'Scripts/TLM'/name
  if raw(path)!=pin:raise ValueError('Reviewed normal runtime changed: '+name)
  payload['Scripts/TLM/'+name]=path
 for name in selection['freshPex']:payload['Scripts/TLM/'+name]=compile/'Scripts/TLM'/name
 if set(payload)!=set(meta['payloads']) or len(payload)!=43:raise ValueError('Exact43 payload membership required')
 for name,path in payload.items():
  safe(path)
  if raw(path)!=meta['payloads'][name]:raise ValueError('Payload input changed: '+name)
 return meta,payload

def package(name):
 if not re.fullmatch(r'package-[0-9]{3}',name):raise ValueError('Output name must be package-NNN')
 target=safe(TASK/'build'/name)
 if target.exists():raise ValueError('Output already exists')
 meta,payload=inputs() # complete validation before any output creation
 target.mkdir(exist_ok=False);bundle=target/'bundle';bundle.mkdir(exist_ok=False)
 for name,path in payload.items():
  dest=safe(bundle/name);dest.parent.mkdir(parents=True,exist_ok=True)
  with dest.open('xb') as out:out.write(path.read_bytes())
  if raw(dest)!=meta['payloads'][name]:raise ValueError('Copied payload mismatch')
 result={'source':source.describe(),'payloads':meta['payloads'],'compileReceipt':meta['compileReceipt'],'policy':'16 source-identical reviewed normal runtime +25 fresh repair compile001. Two current owned plugins. No installed writes.','native':None}
 (target/'receipt.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8',newline='\n')
 print('Blackstone final-effects repair workspace package PASS:43 payloads; native untested; '+str(target))
 return target
if __name__=='__main__':
 try:
  if len(sys.argv)!=2:raise ValueError('Expected package-NNN')
  package(sys.argv[1])
 except (ValueError,OSError,KeyError) as error:print('REFUSED: '+str(error));sys.exit(1)
