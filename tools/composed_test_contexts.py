"""Explicit source-pinned test contexts and fresh synthetic fixtures; no native IO."""
import hashlib,io,json,os,shutil,subprocess,sys,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
FD7='fd7ed54181a23ff100b47ddad60caac802eb019c'
GUIDANCE='5a2b373b3759e9e7cea8ad33d6835cf6a27cc588'
TERRAIN='f601820b7bc4bb1b9d658bd9c29c2053dfd7d11f'
AFTERMATH_BASE='13c8f26209ed022ff23ba38e10a4134bc6e58ba1'
SKELETON_BASE='b93b79035ec97972243668bde0c0f796d4164c9c'
CONTEXT_DIGESTS={SKELETON_BASE:'059AC8A7A7E8500B08649F974631052326368B9183D68D1D753D1BE6C1F2F0DD',AFTERMATH_BASE:'555AFD359E1A94D4D08CC14EDA4627E12C6CBE75AFD0CC01238C6B5A8E0A0F0E','fd7ed54181a23ff100b47ddad60caac802eb019c': '9C38382BD59BF25BC3DAD7829ECA538FD039C687B72A422E12E0D3B6D46B990D', '5a2b373b3759e9e7cea8ad33d6835cf6a27cc588': '0BA58ECE56E59F7E4AF0B8C8C8AF1F4FF72FEDD95BC5E6DAC372FA85B3570356', 'f601820b7bc4bb1b9d658bd9c29c2053dfd7d11f': '18F1895D85895C5943A6A35476542FA9CF0EDF3472B76CC1097AD72A42992C75'}

def digest(data):return hashlib.sha256(data).hexdigest().upper()
def text_digest(data):
    try:data=data.decode('utf-8-sig').replace('\r\n','\n').replace('\r','\n').encode()
    except UnicodeDecodeError:pass
    return digest(data)
def inventory(files):return digest(json.dumps(files,sort_keys=True,separators=(',',':')).encode())
def archive(revision):
    data=subprocess.check_output(['git','archive','--format=zip',revision],cwd=ROOT)
    with zipfile.ZipFile(io.BytesIO(data)) as z:return {n:z.read(n) for n in z.namelist() if not n.endswith('/')}
def execute(args,cwd,log):
    result=subprocess.run([str(a) for a in args],cwd=cwd,capture_output=True,text=True)
    log.parent.mkdir(parents=True,exist_ok=True);log.write_text(result.stdout+result.stderr,encoding='utf-8')
    if result.returncode:raise AssertionError('Command failed '+repr(args)+'; complete log '+str(log)+'\n'+result.stdout+result.stderr)
    return result
def context(revision):
    if revision not in CONTEXT_DIGESTS:raise ValueError('Unapproved historical source revision')
    source=archive(revision);pins={n:text_digest(v) for n,v in source.items()}
    if inventory(pins)!=CONTEXT_DIGESTS[revision]:raise AssertionError('Historical Git archive inventory mismatch')
    target=ROOT/'build/composed/contexts'/revision[:8]
    if not target.exists():
        target.parent.mkdir(parents=True,exist_ok=True)
        execute(['git','worktree','add','--detach',target,revision],ROOT,ROOT/'build/composed'/('context-'+revision[:8]+'.txt'))
    if subprocess.check_output(['git','rev-parse','HEAD'],cwd=target,text=True).strip()!=revision:raise AssertionError('Historical context HEAD changed')
    actual=set(subprocess.check_output(['git','ls-files','--cached','--others','--exclude-standard'],cwd=target,text=True).splitlines())
    if actual!=set(source):raise AssertionError('Historical context source membership changed')
    for name,pin in pins.items():
        if text_digest((target/name).read_bytes())!=pin:raise AssertionError('Historical context source changed: '+name)
    return target
def build(root,master,output,label):
    execute(['dotnet','run','--project','tools/PluginBuilder','--','--out',output,'--fallout4-esm',master],root,ROOT/'build/composed'/('fixture-'+label+'.txt'))
def ordinary_master(revision):
    root=context(revision);master=root/'build/composed-own/Fallout4.esm'
    execute(['dotnet','run','--project','tools/StandInMaster','--',master,'default'],root,ROOT/'build/composed'/('historical-master-'+revision[:8]+'.txt'))
    return master
def check_ordinary_fixture(revision,master,description):
    root=context(revision)
    if master!=root/'build/composed-own/Fallout4.esm':raise AssertionError('Historical ordinary fixture borrowed another source master')
    if description!=root/'build/sim/TheLastMeridian.json' or not description.is_file():raise AssertionError('Historical ordinary build/sim JSON absent or wrong-context')
    if not master.is_file():raise AssertionError('Historical own-source master absent')
    return {'generationSource':revision,'master':str(master),'masterSha256':digest(master.read_bytes()),'description':str(description),'descriptionSha256':digest(description.read_bytes())}
def prepare():
    """Always construct BOTH current and comparison inputs from source this run."""
    for revision in CONTEXT_DIGESTS:context(revision)
    master=ROOT/'build/composed/Fallout4.esm'
    execute(['dotnet','run','--project','tools/StandInMaster','--',master,'default'],ROOT,ROOT/'build/composed/fixture-master.txt')
    build(ROOT,master,ROOT/'build/composed/full-current-projection','current')
    # Full current producer remains separate from the symmetric RH-only pair.
    from rh_terrain_comparison import prepare as prepare_rh_comparison
    comparison=prepare_rh_comparison(ROOT,master,archive,build)
    # Standalone provenance/preservation tests run their actual accepted source,
    # never an environment override of current behavioral tests.
    ordinary={};masters={}
    for revision in CONTEXT_DIGESTS:
        own_master=ordinary_master(revision);masters[revision]=own_master
        description=context(revision)/'build/sim/TheLastMeridian.json'
        build(context(revision),own_master,description.parent,'ordinary-'+revision[:8])
        ordinary[revision]=check_ordinary_fixture(revision,own_master,description)
    # The frozen terrain comparison also needs a same-master pair. Its own
    # accepted generator supplies that master; ordinary fd7/5a identity tests
    # above never consume this different source's synthetic identities.
    build(context(TERRAIN),masters[TERRAIN],context(TERRAIN)/'build/terrain-002/projection','terrain-accepted')
    build(context(FD7),masters[TERRAIN],context(TERRAIN)/'build/terrain-002/baseline-projection','terrain-baseline-pair')
    stamp={'scope':'Fresh synthetic same-master current comparison and separate own-source historical ordinary fixtures; no owned master/native claim','masterSha256':digest(master.read_bytes()),'historicalContextDigests':CONTEXT_DIGESTS,'historicalOrdinary':ordinary,'terrainHistoricalComparisonMasterSource':TERRAIN,'symmetricRhComparison':comparison}
    (ROOT/'build/composed/fixture-provenance.json').write_text(json.dumps(stamp,indent=2)+'\n',encoding='utf-8')

if __name__=='__main__':prepare()
