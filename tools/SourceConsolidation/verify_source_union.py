"""Read-only source snapshot/protected-base/excluded-payload scan; not a build gate."""
from pathlib import Path
import json,hashlib,subprocess,re,ast
R=Path(__file__).resolve().parents[2];H=Path(__file__).resolve().parent
sha=lambda b:hashlib.sha256(b).hexdigest().upper()
def git(*args):return subprocess.check_output(['git','-C',str(R),*args])
def check():
 m=json.loads((H/'selected-source-map.json').read_text());selected={x['path']:x for x in m['files']};assert len(selected)==len(m['files'])
 for path,row in selected.items():assert sha((R/path).read_bytes())==row['gitBlobSha256'],path
 base={line.split('\t',1)[1]:line.split()[2]for line in git('ls-tree','-r',m['base']).decode().splitlines()}
 protected=0
 for path,blob in base.items():
  if path in selected:continue
  p=R/path;assert p.is_file(),path
  actual=git('hash-object','--path',path,str(p)).decode().strip();assert actual==blob,('Unrelated base content changed',path);protected+=1
 tracked=set(git('ls-files').decode().splitlines());untracked=set(git('ls-files','--others','--exclude-standard').decode().splitlines());paths=tracked|untracked
 additions=paths-set(base);assert all(p in selected or p.startswith('tools/SourceConsolidation/')for p in additions),sorted(additions-set(selected))
 forbidden={'.wav','.xwm','.lip','.fuz','.esp','.esm','.esl','.pex','.nif','.dds','.ba2','.bsa','.safetensors','.onnx','.pt','.pth','.bin','.dll','.exe','.log','.dmp','.fos'}
 patterns=[rb'AKIA[0-9A-Z]{16}',rb'gh[pousr]_[A-Za-z0-9]{30,}',rb'github_pat_[A-Za-z0-9_]{30,}',rb'sk-(?:proj-)?[A-Za-z0-9_-]{24,}',rb'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----']
 scanned=0;py=0
 for path in sorted(set(selected)|additions):
  p=R/path;assert p.suffix.lower()not in forbidden,('Forbidden payload',path);data=p.read_bytes();assert b'\0'not in data,('Binary content',path);text=data.decode('utf-8-sig')
  assert not any(re.search(pattern,data)for pattern in patterns),('Potential credential',path)
  if p.suffix=='.py':ast.parse(text,filename=path);py+=1
  scanned+=1
 assert len([p for p in selected if p.startswith('scripts/Source/User/TLM/')and p.endswith('.psc')])==43
 assert [p for p in selected if p.startswith('scripts/Source/User/TLMQA/')]==['scripts/Source/User/TLMQA/OpeningAudit.psc']
 for path in base:
  if path.startswith('.github/')or path=='tools/papyrus_sim/game_runs.json':assert path not in selected
 return {'base':m['base'],'selectedSourceFiles':len(selected),'normalPSC':43,'qaPSC':1,'unrelatedBaseFilesUnchanged':protected,'newOrSelectedTextFilesScanned':scanned,'selectedPythonAST':py,'excludedPayloadOrCredentialFindings':0,'scope':'Finite source/payload scan only; not aggregate/cloud/native pass'}
if __name__=='__main__':print(json.dumps(check(),indent=2))
