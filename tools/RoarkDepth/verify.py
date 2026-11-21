"""Exact new Roark successor. Historical verifiers/manifests stay frozen."""
from pathlib import Path
import json,hashlib,subprocess,sys
ROOT=Path(__file__).absolute().parent;REPO=ROOT.parents[1];BASE='f491eeb4e670d306530446b60f82785950dbb747'
OLD={'tools/papyrus_sim/test_rh_return_account.py','scripts/Source/User/TLM/RedHollowWalk.psc','tools/PluginBuilder/SpecRedHollow.cs','tools/PluginBuilder/formkeys.txt'}
NEW={'tools/RoarkDepth/'+n for n in ['.gitattributes','.gitignore','approved-nodes.json','compile-receipt.json','README.md','raw_records.py','pathguard.py','verify.py','package.py','test_roark_depth.py']}
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest().upper()
def textsha(p):return hashlib.sha256(Path(p).read_bytes().replace(b'\r\n',b'\n')).hexdigest().upper()
def problems():
 errors=[];m=json.loads((ROOT/'source-receipt.json').read_text(encoding='utf-8'))
 if m['baseline']!=BASE or set(m['files'])!=OLD|NEW:errors.append('Wrong exact successor membership')
 raw=subprocess.check_output(['git','ls-tree','-r',BASE],cwd=REPO)
 if hashlib.sha256(raw).hexdigest().upper()!=m['baselineInventorySha256'] or len(raw.splitlines())!=450:errors.append('Wrong frozen450inventory')
 changed=subprocess.check_output(['git','diff','--name-only',BASE,'--'],cwd=REPO,text=True).splitlines();untracked=subprocess.check_output(['git','ls-files','--others','--exclude-standard'],cwd=REPO,text=True).splitlines()
 if set(changed+untracked)-(OLD|NEW|{'tools/RoarkDepth/source-receipt.json'}):errors.append('Change outside exact reviewed successor')
 for n,h in m['files'].items():
  if not (REPO/n).is_file() or textsha(REPO/n)!=h:errors.append('Source pin '+n)
 original=subprocess.check_output(['git','show',BASE+':tools/PluginBuilder/formkeys.txt'],cwd=REPO).replace(b'\r\n',b'\n')
 appended=''.join('TLM_MSG_RH_'+n+'\n'+str(3664+i)+'\n' for i,n in enumerate(['RdcQuiet','RdcTired','RdcThanks','RdcTerms','RdcTermsAnswer'])).encode()
 if (REPO/'tools/PluginBuilder/formkeys.txt').read_bytes().replace(b'\r\n',b'\n')!=original+appended:errors.append('OldIDs not exact prefix / new allocation differs')
 scripts=REPO/'scripts/Source/User/TLM'
 if {p.stem+'.pex':textsha(p) for p in scripts.glob('*.psc')}!=m['sourceTextSha256']:errors.append('Canonical34source selection')
 return errors
def artifact_problems(main,world):
 from raw_records import records,subs
 errors=[];parent=ROOT.parents[3]/'work/rh-return-account-build-f491eeb/build/licensed-return-account-skeleton-001/bundle'
 def name(row):return dict(subs(row['data'])).get('EDID',b'').rstrip(b'\0').decode('utf-8')
 for kind,new in [('main',Path(main)),('world',Path(world))]:
  try:
   old={(r['tag'],r['id']):r for r in records((parent/new.name).read_bytes())};fresh={(r['tag'],r['id']):r for r in records(new.read_bytes())}
   added={('MESG',0x01000E50+i) for i in range(5)} if kind=='main' else set()
   if set(fresh)-set(old)!=added or set(old)-set(fresh):errors.append(kind+' unexpected added/removed identities')
   permitted={'','TLM_RH','TLM_MSG_RH_RhaRoarkAll','TLM_MSG_RH_RhaTerms'} if kind=='main' else {'TLM_WS_RH'}
   expected_changed={key for key,row in old.items() if name(row) in permitted}
   changed={key for key in set(old)&set(fresh) if (old[key]['data'],old[key]['flags'],old[key]['parents'])!=(fresh[key]['data'],fresh[key]['flags'],fresh[key]['parents'])}
   # TES4 '' is the ONLY blank EDID in this set; identify it explicitly.
   if kind=='main':expected_changed={key for key,row in old.items() if row['tag']=='TES4' or name(row) in permitted-{''}}
   if changed!=expected_changed:errors.append(kind+' unrelated record/geometry changed')
   for key in changed&expected_changed:
    before=old[key];after=fresh[key]
    if (before['flags'],before['parents'])!=(after['flags'],after['parents']):errors.append(kind+' original record flags/group changed')
    skip={'VMAD'} if key[0]=='QUST' else {'HEDR'} if key[0]=='TES4' else {'ITXT','CTDA'}
    if [(k,v) for k,v in subs(before['data']) if k not in skip]!=[(k,v) for k,v in subs(after['data']) if k not in skip]:errors.append(kind+' unrelated subrecord changed')
  except Exception as error:errors.append(kind+' malformed artifact: '+str(error))
 return errors
if __name__=='__main__':
 errors=problems()
 if len(sys.argv)==3:errors+=artifact_problems(sys.argv[1],sys.argv[2])
 print('\n'.join(errors) if errors else 'Roark character depth source candidate PASS');sys.exit(bool(errors))
