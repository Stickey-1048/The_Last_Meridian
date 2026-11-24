"""Read-only052 source inventory, exact component copies and coupled-index proof."""
from pathlib import Path
import json,subprocess,hashlib,re,ast
R=Path(__file__).resolve().parents[2];H=Path(__file__).resolve().parent
sha=lambda b:hashlib.sha256(b).hexdigest().upper()
def oid(b):return hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()
def check():
 p=json.loads((H/'refresh-provenance.json').read_text());selected={r['path']:r for r in p['files']};assert len(selected)==18
 for path,row in selected.items():assert sha((R/path).read_bytes())==row['gitBlobSha256'],path
 parent={line.split('\t',1)[1]:line.split()[2]for line in subprocess.check_output(['git','-C',str(R),'ls-tree','-r',p['parent']]).decode().splitlines()};protected=0
 for path,blob in parent.items():
  if path in selected:continue
  b=(R/path).read_bytes();assert blob in {oid(b),oid(b.replace(b'\r\n',b'\n'))},path;protected+=1
 paths=set(subprocess.check_output(['git','-C',str(R),'ls-files','--cached','--others','--exclude-standard']).decode().splitlines());new=paths-set(parent)
 assert all(path in selected or path.startswith('tools/SourceRefresh/')for path in new),new
 forbidden={'.wav','.xwm','.lip','.fuz','.esp','.esm','.esl','.pex','.nif','.dds','.ba2','.bsa','.safetensors','.onnx','.pt','.pth','.bin','.dll','.exe','.log','.dmp','.fos','.png','.jpg','.jpeg'}
 py=0
 for path in set(selected)|new:
  b=(R/path).read_bytes();assert Path(path).suffix.lower()not in forbidden and b'\0'not in b,path;b.decode('utf-8-sig')
  assert not re.search(rb'(?:AKIA[0-9A-Z]{16}|gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{30,}|sk-(?:proj-)?[A-Za-z0-9_-]{24,}|-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----)',b),path
  if path.endswith('.py'):ast.parse(b.decode('utf-8-sig'),filename=path);py+=1
 normal=list((R/'scripts/Source/User/TLM').glob('*.psc'));assert len(normal)==43 and len(list((R/'scripts/Source/User/TLMQA').glob('*.psc')))==1
 text=(R/'scripts/Source/User/TLM/Act1Walk.psc').read_text();start=text.index('Function TalkDunmore(');end=text.index('\nEndFunction',start);part=text[start:end]
 for marker in ['If answer == 3\n\t\t; "[Risk combat]','ElseIf answer == 4\n\t\t; "[Fight]','ElseIf answer == 2','ElseIf answer == 0\n\t\tCallSheriffHelp()','ElseIf answer == 1 && HelpRoad().SheriffHelpPending']:assert marker in part,marker
 for a,b in [('If answer == 3','If answer == 0'),('ElseIf answer == 4','ElseIf answer == 1'),('ElseIf answer == 0\n\t\tCallSheriffHelp()','ElseIf answer == 4\n\t\tCallSheriffHelp()'),('ElseIf answer == 1 && HelpRoad().SheriffHelpPending','ElseIf answer == 3 && HelpRoad().SheriffHelpPending'),('; "[Leave the caravan] I\'m walking away.":','; "[Leave] I\'m walking away.":')]:assert part.count(a)==1;part=part.replace(a,b)
 old=subprocess.check_output(['git','-C',str(R),'show',p['parent']+':scripts/Source/User/TLM/Act1Walk.psc']).decode().replace('\r\n','\n');assert text[:start]+part+text[end:]==old
 module=(R/'tools/WorldSliceBuilder/DunmoreSafeChoices.cs').read_text();assert 'int[] order={4,3,2,0,1}'in module and '0x849'in module and 'TLM_MSG_A1_DunmoreHold'in module and '[Leave the caravan]'in module
 program=(R/'tools/WorldSliceBuilder/Program.cs').read_text();hooks=['OpeningHillForestFinish.Apply','OpeningVisibleSlopeFinish.Apply','DunmoreSafeChoices.Apply'];assert all(program.count(v)==1 for v in hooks);assert [program.index(v)for v in hooks]==sorted(program.index(v)for v in hooks);assert program.index(hooks[-1])<program.index('mod.BeginWrite.ToPath(plugin)')
 oldprogram=subprocess.check_output(['git','-C',str(R),'show',p['parent']+':tools/WorldSliceBuilder/Program.cs']).decode().replace('\r\n','\n');inverse=''.join(line for line in program.splitlines(True)if not any(hook in line for hook in hooks));assert inverse==oldprogram
 for folder,mod in [('OpeningHillForestFinish','OpeningHillForestFinish.cs'),('OpeningVisibleSlopeFinish','OpeningVisibleSlopeFinish.cs')]:assert sha((R/'tools'/folder/'plan.json').read_bytes())in(R/'tools/WorldSliceBuilder'/mod).read_text()
 return {'parent':p['parent'],'exactComponentSourceFiles':18,'protectedParentFiles':protected,'normalPSC':43,'otherNormalPSCUnchanged':42,'QAUnchanged':True,'pythonParsed':py,'newOrSelectedTextFilesScanned':len(set(selected)|new),'coupling':'0help/1leave/2share/3risk/4fight; world order4,3,2,0,1; exact runtime/program inverse','payloadOrCredentialFindings':0,'scope':'SOURCE syntax/copy/coupling only; not build/portableaggregate/native pass'}
if __name__=='__main__':print(json.dumps(check(),indent=2))
