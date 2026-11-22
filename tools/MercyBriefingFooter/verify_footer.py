"""Exact Hub-DESC UI successor, not a renderer or marker-state fix."""
from pathlib import Path
import sys,json,hashlib,subprocess
ROOT=Path(__file__).resolve().parent;REPO=ROOT.parents[1];sys.path.insert(0,str(REPO/'tools'))
from rh_terrain_projection import records,subs
BASE='edd0afd67cbdf97fa9ee8553cded99d755b6a073';OLD=REPO.parent/'blackstone-pass-custody-fix-001';BUNDLE=OLD/'tools/Blackstone/build/package-001/bundle'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest().upper()
def pin(p):return hashlib.sha256(p.read_text(encoding='utf-8').encode()).hexdigest().upper()
def source_errors():
 r=json.loads((ROOT/'source-receipt.json').read_text(encoding='utf-8'));errors=[]
 if r['baseline']!=BASE or hashlib.sha256(subprocess.check_output(['git','ls-tree','-r',BASE],cwd=REPO)).hexdigest().upper()!=r['baselineTreeSha256']:errors.append('Baseline changed')
 changed=subprocess.check_output(['git','diff','--name-only',BASE,'--'],cwd=REPO,text=True).splitlines();untracked=subprocess.check_output(['git','ls-files','--others','--exclude-standard'],cwd=REPO,text=True).splitlines();expected=set(r['files'])|{'tools/MercyBriefingFooter/source-receipt.json'}
 if set(changed+untracked)!=expected:errors.append('Changes exceed exact technical Hub UI union')
 for name,h in r['files'].items():
  if not(REPO/name).is_file()or pin(REPO/name)!=h:errors.append('Source pin '+name)
 old=json.loads((OLD/'tools/win/blackstone-pass-custody-candidate.json').read_text(encoding='utf-8'))['sourceTextSha256'];current={p.name:pin(p)for p in(REPO/'scripts/Source/User/TLM').glob('*.psc')}
 if current!=old or len(current)!=41:errors.append('Compiler carry requires all41 source-identical PSCs')
 return errors

def artifact(raw,original):
 a,names=records(raw);b,oldnames=records(original);assert set(a)==set(b)and len(a)==1896
 hub=oldnames['TLM_MSG_MB_Hub'];assert names['TLM_MSG_MB_Hub']==hub;assert a[hub][0]==b[hub][0]and a[hub][2]==b[hub][2]
 oldparts=subs(b[hub][1]);newparts=subs(a[hub][1]);oldtext=dict(oldparts)[b'DESC'];prefix=oldtext.split(b'\n\n[')[0];text=prefix+b'\n\n[Choose a road for directions.]\0';assert len(text)==136 and all(x<128 for x in text)and text.count(b'\0')==1
 assert newparts==[(k,text if k==b'DESC'else v)for k,v in oldparts],'Changes exceed footer-only DESC'
 assert all(a[k]==b[k]for k in a if k!=hub),'Another message/quest/objective/record changed'
 return {'status':'PASS','oldTextChars':183,'newTextChars':135,'onlyChangedRecord':'TLM_MSG_MB_Hub','onlyChangedField':'DESC technical footer','all1895OtherRecordsExact':True,'all41RuntimeSourcesUnchanged':True,'rendererRootCause':None,'native':None}
def run():
 assert source_errors()==[],source_errors();m=json.loads((ROOT/'source-receipt.json').read_text(encoding='utf-8'));p=ROOT/'build/master-001/TheLastMeridian.esp';assert sha(p)==m['masterSha256'];return artifact(p.read_bytes(),(BUNDLE/'TheLastMeridian.esp').read_bytes())
if __name__=='__main__':print(json.dumps(run(),indent=2))
