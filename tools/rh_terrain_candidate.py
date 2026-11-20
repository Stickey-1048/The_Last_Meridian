"""RH-TERRAIN-002 strict SOURCE successor. No old verifier/manifest rewriting.
Frozen fd7 membership is anchored; only declared environment deltas are allowed.
"""
from pathlib import Path
import hashlib,json,sys,subprocess
ROOT=Path(__file__).resolve().parent.parent
BASE='fd7ed54181a23ff100b47ddad60caac802eb019c'
BASELINE_DIGEST='9C38382BD59BF25BC3DAD7829ECA538FD039C687B72A422E12E0D3B6D46B990D'
CHANGED={'tools/PluginBuilder/RedHollowEnvironment.cs','tools/PluginBuilder/RedHollowGeometryAudit.cs','tools/PluginBuilder/formkeys.txt'}
OWN={'tools/PluginBuilder/RedHollowTerrain.cs','tools/rh_terrain_candidate.py','tools/rh_terrain_projection.py','tools/rh_terrain_donor_probe.py','tools/papyrus_sim/test_rh_terrain_002.py','docs/design/RH_TERRAIN_002.md','docs/design/RH_TERRAIN_002_DONOR_METADATA.json'}
MANIFEST='tools/win/rh-terrain-002-candidate.json'
def sha(data):return hashlib.sha256(data).hexdigest().upper()
def pin(path):
 data=path.read_bytes()
 try:data=data.decode('utf-8-sig').replace('\r\n','\n').replace('\r','\n').encode()
 except UnicodeDecodeError:pass
 return sha(data)
def digest(value):return sha(json.dumps(value,sort_keys=True,separators=(',',':')).encode())
def environment_problems(root=ROOT):
 out=[]
 try:m=json.loads((root/MANIFEST).read_text(encoding='utf-8-sig'))
 except (OSError,ValueError) as exc:return ['Manifest unreadable: '+str(exc)]
 if m.get('baseline')!=BASE or m.get('candidate')!='RH-TERRAIN-002' or m.get('schema')!=1:out.append('Candidate identity altered')
 baseline=m.get('baselineFiles',{})
 if digest(baseline)!=BASELINE_DIGEST:return out+['Frozen fd7 baseline membership/pins altered']
 inputs=CHANGED|OWN
 if set(m.get('sourcePins',{}))!=inputs:out.append('Successor input membership altered')
 for name in inputs:
  if not(root/name).is_file() or pin(root/name)!=m.get('sourcePins',{}).get(name):out.append('Successor source pin mismatch: '+name)
 # Exact original allocations plus only72declared decorative placements.
 lines=(root/'tools/PluginBuilder/formkeys.txt').read_text().splitlines();prefix=m.get('baselineFormkeysLines',0)
 if sha(('\n'.join(lines[:prefix])+'\n').encode())!=baseline['tools/PluginBuilder/formkeys.txt']:out.append('Original allocation prefix altered')
 tail=lines[prefix:]
 if len(tail)!=144 or any(not n.startswith('TLM_REF_RHE_T2_') for n in tail[::2]) or len(set(tail[::2]))!=72:out.append('Unapproved allocation tail')
 if any(int(tail[i+1])!=3560+i//2 for i in range(0,len(tail),2)):out.append('Nonappend allocation IDs')
 if m.get('measured')!={'licensedArtifact':None,'papyrusCompile':None,'nativeAcceptance':None}:out.append('Source manifest cannot assert native/artifact/compiler acceptance')
 return out
def problems(root=ROOT):
 out=environment_problems(root)
 if out:return out
 m=json.loads((root/MANIFEST).read_text(encoding='utf-8-sig'));baseline=m['baselineFiles']
 for name,old in baseline.items():
  if name not in CHANGED and (not(root/name).is_file() or pin(root/name)!=old):out.append('Unrelated frozen file altered: '+name)
 if root is ROOT:
  actual=set(subprocess.check_output(['git','ls-files','--cached','--others','--exclude-standard'],cwd=root,text=True).splitlines())
  if actual!=set(baseline)|OWN|{MANIFEST}:out.append('Undeclared current source membership')
 return out

if __name__=='__main__':
 issues=problems()
 print('\n'.join(issues) if issues else 'RH-TERRAIN-002 exact source provenance verified; artifact/native acceptance remain open.')
 raise SystemExit(bool(issues))
