"""Exact source-only six-file union; never builds or imports owned inputs."""
import ast,hashlib,json,re,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];HERE=Path(__file__).resolve().parent
BASE='01833b9de56b0ca91bef8468575bbec06f13f014'
def git(*args):return subprocess.check_output(['git','-C',str(ROOT),*args])
def verify():
 p=json.loads((HERE/'provenance.json').read_text(encoding='utf-8'));copied={x['path'] for x in p['copies']}
 for row in p['copies']:
  raw=(ROOT/row['path']).read_bytes();assert hashlib.sha256(raw).hexdigest().upper()==row['sha256'],row['path']
  original=subprocess.check_output(['git','-C',str(ROOT.parent/'opening-cloud-guidance-fixture-fix-071'),'show',p['source071']+':'+row['path']]);assert raw==original,row['path']
 prior=git('ls-tree','-r','--name-only',BASE).decode().splitlines();protected=[n for n in prior if n not in copied]
 stream=git_batch(protected);at=0
 for name in protected:
  end=stream.index(b'\n',at);size=int(stream[at:end].split()[-1]);blob=stream[end+1:end+1+size];at=end+size+2
  assert (ROOT/name).read_bytes().replace(b'\r\n',b'\n')==blob.replace(b'\r\n',b'\n'),name
 assert at==len(stream)
 new=copied|{x.relative_to(ROOT).as_posix() for x in HERE.iterdir() if x.is_file()}
 for name in new:
  raw=(ROOT/name).read_bytes();raw.decode('utf-8-sig');assert b'\0'not in raw
  assert Path(name).suffix in {'.py','.json','.md'}
  assert not re.search(rb'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY|gh[pousr]_[A-Za-z0-9]{30,}|sk-[A-Za-z0-9]{32,}',raw),name
  if name.endswith('.py'):ast.parse(raw.decode('utf-8-sig'))
 normal=[n for n in prior if n.startswith('scripts/Source/User/TLM/')and n.endswith('.psc')];qa=[n for n in prior if n.startswith('scripts/Source/User/TLMQA/')and n.endswith('.psc')];assert (len(normal),len(qa))==(43,1)
 selected=json.loads((ROOT/'tools/CurrentSourceFixture/provenance.json').read_text(encoding='utf-8'))['selected064'];assert len(selected)==8
 return {'scope':'Source-only finite copy073, no combined build/cloud/native claim','copies071':len(copied),'protected068':len(protected),'normalPSC':43,'qaPSC':1,'source064PathsLiteral':8,'textScanned':len(new)}
def git_batch(names):
 return subprocess.check_output(['git','-C',str(ROOT),'cat-file','--batch'],input=''.join(BASE+':'+n+'\n'for n in names).encode())
if __name__=='__main__':print(json.dumps(verify(),indent=2))
