"""Read-only finite048 source/protected-parent/excluded-payload inventory, no aggregate claim."""
from pathlib import Path
import json,hashlib,subprocess,re
R=Path(__file__).resolve().parents[2];H=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest().upper()
def check():
 p=json.loads((H/'patch-provenance.json').read_text())
 for path,h in p['changedAndTestFiles'].items():assert sha(R/path)==h,path
 base={s.split('\t',1)[1]:s.split()[2]for s in subprocess.check_output(['git','-C',str(R),'ls-tree','-r',p['parent']]).decode().splitlines()}
 changed={'tools/check_consistency.py','tools/papyrus_natives.json'};protected=0
 for path,blob in base.items():
  if path in changed:continue
  raw=subprocess.check_output(['git','-C',str(R),'hash-object','--no-filters',str(R/path)]).decode().strip()
  actual=raw if raw==blob else subprocess.check_output(['git','-C',str(R),'hash-object','--path',path,str(R/path)]).decode().strip()
  assert actual==blob,path;protected+=1
 paths=set(subprocess.check_output(['git','-C',str(R),'ls-files','--cached','--others','--exclude-standard']).decode().splitlines());new=paths-set(base)
 assert all(v.startswith('tools/SourcePortability/')for v in new),new
 for path in new|changed:
  b=(R/path).read_bytes();assert b'\0'not in b; b.decode('utf-8-sig');assert Path(path).suffix in {'.py','.json','.md'}
  assert not re.search(rb'(?:AKIA[0-9A-Z]{16}|gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{30,}|-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----)',b),path
 return {'parent':p['parent'],'protectedParentFiles':protected,'changedParentFiles':sorted(changed),'newTextFiles':len(new),'payloadOrCredentialFindings':0,'scope':'SOURCE inventory only, not portable aggregate/native acceptance'}
if __name__=='__main__':print(json.dumps(check(),indent=2))
