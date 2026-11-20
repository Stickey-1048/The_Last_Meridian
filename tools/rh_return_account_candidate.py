"""Strict RH-RETURN-ACCOUNT-001 successor, preserving all accepted13c sources outside the exact delta."""
import hashlib,json,sys
from pathlib import Path
import player_guidance_terrain_candidate as prior
ROOT=Path(__file__).resolve().parent.parent
BASELINE='13c8f26209ed022ff23ba38e10a4134bc6e58ba1'
BASELINE_DIGEST='555AFD359E1A94D4D08CC14EDA4627E12C6CBE75AFD0CC01238C6B5A8E0A0F0E'
APPROVED={'scripts/Source/User/TLM/RedHollowWalk.psc': 'A0D987D2D636381B8F83C46B875EF4AF6DA5AEC6D0751523766F3C0F1033D039', 'tools/PluginBuilder/SpecRedHollow.cs': '6EEF70EAE0ED717BDCD2CD54840836350F59010D5C39E93D1FE6E6E3E9D6B56A', 'tools/PluginBuilder/formkeys.txt': '2B2514CB6219852B0D45815FEDCAF408BF2A672F8FB6B814AC55B927414AD490', 'tools/PluginBuilder/last-build.report.txt': 'C253B9A6074192D2093DA94F7961126606512059E9C434DE5D2AEEBDA184A953', 'tools/papyrus_sim/test_red_hollow.py': '61B2BC75C8CF3DC9BBE304E81B034CDA94B8CEC715EB0B0A91333B3C6524AED6', 'tools/composed_test_contexts.py': '150F26E0D5B3482EB35CDC1A26F042E2F5786E01672DDC4831C4C7C3D38F7D9F', 'tools/run_composed_tests.py': '7D4890883BC04E238CEF7009ABED49D159733134C19FF3641B59A5F41671D00E'}
NAME='tools/win/rh-return-account-candidate.json'
OWN={'tools/rh_return_account_candidate.py','tools/papyrus_sim/test_rh_return_account.py','tools/papyrus_sim/test_rh_return_account_candidate.py','docs/design/RH_RETURN_ACCOUNT_001_RECEIPT.md'}
MANIFEST=ROOT/NAME

def pin(path):return prior.pin(path)
def digest(value):return prior.digest(value)
def expected_names(baseline):return set(baseline)|OWN|{NAME}
def describe(root=ROOT):
    old=json.loads((root/prior.NAME).read_text(encoding='utf-8'))
    runtime=prior.describe(root)
    baseline=json.loads((root/NAME).read_text(encoding='utf-8'))['baselineFiles']
    return {'sourceTextSha256':runtime['sourceTextSha256'],'runtimeSelection':runtime['runtimeSelection'],'sourceFilesTextSha256':{n:pin(root/n) for n in sorted(expected_names(baseline)-{NAME})}}
def problems(root=ROOT):
    out=[]
    try:
        m=json.loads((root/NAME).read_text(encoding='utf-8'));base=m['baselineFiles']
        if (m.get('schema'),m.get('candidate'),m.get('baseline'),m.get('scripts'))!=(1,'RH-RETURN-ACCOUNT-001',BASELINE,34):out.append('Return/account candidate identity changed')
        if digest(base)!=BASELINE_DIGEST:out.append('Full13c baseline anchor changed')
        expected=dict(base);expected.update(APPROVED)
        for n,value in expected.items():
            if pin(root/n)!=value:out.append('Unapproved successor source: '+n)
        if prior.current_names(root)!=expected_names(base):out.append('Exact return/account source membership changed')
        state=describe(root)
        for n,value in state.items():
            if m.get(n)!=value:out.append(n+' differs from current successor')
        old=json.loads((root/prior.NAME).read_text(encoding='utf-8'))
        if len(state['sourceTextSha256'])!=34 or set(state['sourceTextSha256'])!=set(old['sourceTextSha256']):out.append('Exact34runtime membership changed')
        if state['runtimeSelection']!=old['runtimeSelection']:out.append('Exact16reviewed18fresh selection changed')
        if m.get('measured')!=old['measured'] or any(v is not None for v in m.get('measured',{}).values()):out.append('Source candidate cannot claim artifact/native measurements')
        lines=(root/'tools/PluginBuilder/formkeys.txt').read_text(encoding='utf-8-sig').splitlines(keepends=True)
        suffix=''.join(lines[-64:]);prefix=''.join(lines[:-64]).replace('\r\n','\n')
        if hashlib.sha256(prefix.encode()).hexdigest().upper()!=base['tools/PluginBuilder/formkeys.txt']:out.append('Old allocation prefix changed')
        names=['TLM_MSG_RH_Rha'+w+n for w in ('Roark','Blevins') for n in ['Ordered','Deadline','All','None']+['Partial'+str(i) for i in range(1,11)]]+['TLM_MSG_RH_Rha'+n for n in ('Terms','Break','Open','Report')]
        if suffix!=''.join(n+'\n'+str(3632+i)+'\n' for i,n in enumerate(names)):out.append('Exact32append-only Message allocations changed')
    except (OSError,ValueError,KeyError,TypeError) as e:out.append('Successor inputs unreadable: '+str(e))
    return out

def main(args):
    if args==['verify']:
        found=problems()
        if found:print('\n'.join(found));return 1
        print('Red Hollow return/account source candidate PASS;34sources16reviewed18fresh; compiler/artifact/native gates separate.');return 0
    if args==['describe']:print(json.dumps(describe(),indent=2));return 0
    print(__doc__);return 2
if __name__=='__main__':sys.exit(main(sys.argv[1:]))
