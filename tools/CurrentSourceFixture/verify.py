"""Bounded coherent source068 proof; no build, fixture emission or owned input."""
import ast,hashlib,json,re,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];H=Path(__file__).resolve().parent
BASE='aef0d287637b08b4100775b2310c409995a4ebc3'
CHANGED={'tools/PluginBuilder/Builder.cs','tools/PluginBuilder/formkeys.txt','tools/WorldSliceBuilder/Program.cs','tools/StandInMaster/CurrentProducerFixture.cs','tools/StandInMaster/test_current060.py','tools/run_checks.sh'}
def git(*args):return subprocess.check_output(['git','-C',str(ROOT),*args])
def sha(b):return hashlib.sha256(b).hexdigest().upper()
def verify():
 p=json.loads((H/'provenance.json').read_text());prior=set(git('ls-tree','-r','--name-only',BASE).decode().splitlines())
 protected=sorted(prior-CHANGED);stream=subprocess.check_output(['git','-C',str(ROOT),'cat-file','--batch'],input=''.join(BASE+':'+n+'\n'for n in protected).encode());at=0
 for name in protected:
  end=stream.index(b'\n',at);size=int(stream[at:end].split()[-1]);blob=stream[end+1:end+1+size];at=end+size+2
  assert (ROOT/name).read_bytes().replace(b'\r\n',b'\n')==blob.replace(b'\r\n',b'\n'),name
 assert at==len(stream)
 for row in p['selected064']:
  name=row['path'];raw=(ROOT/name).read_bytes();normalized=raw if name.endswith('.json')else raw.replace(b'\r\n',b'\n')
  assert sha(normalized)==row['sha256'],name
  origin=ROOT.parent/'opening-current-art-source-064';blob=subprocess.check_output(['git','-C',str(origin),'show',p['source064']+':'+name]);assert blob==normalized
 builder=(ROOT/'tools/PluginBuilder/Builder.cs').read_text();parent=git('show',BASE+':tools/PluginBuilder/Builder.cs').decode()
 assert builder.replace('        BuildDunmoreWardrobe();\n','')==parent
 assert 'is not available in this build)'in builder
 current=(ROOT/'tools/StandInMaster/CurrentProducerFixture.cs').read_text()
 for s in ['0xA36BE,"ClothesResident4",0xA36BD','Clothes\\Residents\\4SuitM.nif','0x1C2691u,"SyntheticCurrentDunmoreInventory"','!preserveAbsence']:assert s in current,s
 assert (ROOT/'tools/StandInMaster/test_absence067.py').read_bytes().replace(b'\r\n',b'\n')==git('show',BASE+':tools/StandInMaster/test_absence067.py')
 normal=[n for n in prior if n.startswith('scripts/Source/User/TLM/')and n.endswith('.psc')];qa=[n for n in prior if n.startswith('scripts/Source/User/TLMQA/')and n.endswith('.psc')];assert (len(normal),len(qa))==(43,1)
 scanned=set(CHANGED)|{r['path']for r in p['selected064']}|{'tools/StandInMaster/test_wardrobe068.py','tools/CurrentSourceFixture/verify.py','tools/CurrentSourceFixture/provenance.json','tools/CurrentSourceFixture/HANDOFF.md'}
 for n in scanned:
  raw=(ROOT/n).read_bytes();raw.decode('utf-8-sig');assert b'\0'not in raw
  assert Path(n).suffix.lower()not in {'.esp','.esm','.pex','.wav','.nif','.dds','.ba2'}
  assert not re.search(rb'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY|gh[pousr]_[A-Za-z0-9]{30,}|sk-[A-Za-z0-9]{32,}',raw),n
  if n.endswith('.py'):ast.parse(raw.decode('utf-8-sig'))
 return {'scope':'source-only coherent068, not owned/native/cloud aggregate','selected064':8,'protected067Paths':len(protected),'normalPSCLiteral':43,'qaPSCLiteral':1,'textScanned':len(scanned),'wardrobeKey':3978,'absence067Preserved':True,'native':None}
if __name__=='__main__':print(json.dumps(verify(),indent=2))
