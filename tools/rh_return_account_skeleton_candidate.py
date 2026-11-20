"""Exact b93 successor: two optional const declarations, no gameplay/builder/checker waiver."""
import hashlib,json,sys
from pathlib import Path
import rh_return_account_candidate as prior
ROOT=Path(__file__).resolve().parent.parent
BASELINE='b93b79035ec97972243668bde0c0f796d4164c9c'
BASELINE_DIGEST='059AC8A7A7E8500B08649F974631052326368B9183D68D1D753D1BE6C1F2F0DD'
APPROVED={'scripts/Source/User/TLM/RedHollowWalk.psc': '641FB82667FABBF82717305CFDE635711DB65269527DAA42DCABD1D6F5DAD563', 'tools/composed_test_contexts.py': 'B073DC848CAB464218F0234FC5EDCC977B6C6057B54E23CD57B38DE47E8871F4', 'tools/run_composed_tests.py': '80A1734595DCC770606ED6104360D65F8CDF960D5441F2781F26E19990BA9ECC'}
NAME='tools/win/rh-return-account-skeleton-candidate.json'
MANIFEST=ROOT/NAME
OWN={'tools/rh_return_account_skeleton_candidate.py','tools/papyrus_sim/test_rh_return_account_skeleton.py','docs/design/RH_RETURN_ACCOUNT_SKELETON_FIX_001.md'}
def expected_names(base):return set(base)|OWN|{NAME}
def describe(root=ROOT):
    m=json.loads((root/NAME).read_text(encoding='utf-8'));runtime=prior.describe(root)
    return {'sourceTextSha256':runtime['sourceTextSha256'],'runtimeSelection':runtime['runtimeSelection'],'sourceFilesTextSha256':{n:prior.pin(root/n) for n in sorted(expected_names(m['baselineFiles'])-{NAME})}}
def problems(root=ROOT):
    out=[]
    try:
        m=json.loads((root/NAME).read_text(encoding='utf-8'));base=m['baselineFiles']
        if (m.get('schema'),m.get('candidate'),m.get('baseline'),m.get('scripts'))!=(1,'RH-RETURN-ACCOUNT-SKELETON-FIX-001',BASELINE,34):out.append('Skeleton successor identity changed')
        if prior.digest(base)!=BASELINE_DIGEST:out.append('Exact full b93 baseline changed')
        accepted=dict(base);accepted.update(APPROVED)
        for n,pin in accepted.items():
            if prior.pin(root/n)!=pin:out.append('Unapproved skeleton successor delta: '+n)
        if prior.prior.current_names(root)!=expected_names(base):out.append('Exact skeleton successor membership changed')
        source=(root/'scripts/Source/User/TLM/RedHollowWalk.psc').read_text(encoding='utf-8-sig').replace('\r\n','\n').replace('\r','\n')
        for who in ('Roark','Blevins'):
            line='ObjectReference Property RhaOriginal'+who+' Auto Const'
            if source.count(line+'\n')!=1:out.append('Exact optional declaration missing: '+who)
            source=source.replace(line+'\n',line+' Mandatory\n')
        if hashlib.sha256(source.encode()).hexdigest().upper()!=base['scripts/Source/User/TLM/RedHollowWalk.psc']:out.append('Changes exceed exact two optional markers')
        state=describe(root)
        for n,value in state.items():
            if m.get(n)!=value:out.append(n+' differs from current skeleton successor')
        old=json.loads((root/prior.NAME).read_text(encoding='utf-8'))
        if set(state['sourceTextSha256'])!=set(old['sourceTextSha256']) or len(state['sourceTextSha256'])!=34 or state['runtimeSelection']!=old['runtimeSelection']:out.append('Exact34sources16reviewed18fresh changed')
        if m.get('measured')!=old['measured'] or any(v is not None for v in m.get('measured',{}).values()):out.append('Source candidate cannot claim artifact/native measurements')
    except (OSError,ValueError,KeyError,TypeError) as e:out.append('Skeleton successor unreadable: '+str(e))
    return out

def main(args):
    if args==['verify']:
        found=problems()
        if found:print('\n'.join(found));return 1
        print('Red Hollow return/account skeleton source candidate PASS; exact two optional markers;34sources16reviewed18fresh; compiler/artifact/native separate.');return 0
    if args==['describe']:print(json.dumps(describe(),indent=2));return 0
    print(__doc__);return 2
if __name__=='__main__':sys.exit(main(sys.argv[1:]))
