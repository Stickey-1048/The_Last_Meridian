"""Explicit synthetic RH comparison; historical contexts and production untouched."""
import hashlib,json
from pathlib import Path
COMMON='5a2b373b3759e9e7cea8ad33d6835cf6a27cc588'
TERRAIN='f601820b7bc4bb1b9d658bd9c29c2053dfd7d11f'
FILES=('RedHollowTerrain.cs','RedHollowGeometryAudit.cs','RedHollowEnvironment.cs')
ACCESS=('        foreach(var support in RedHollowAccess.Supports)yield return support;\n','        BuildRedHollowAccess();\n')
def normalized(raw):return raw.decode('utf-8-sig').replace('\r\n','\n').replace('\r','\n')
def select(root,archive):
    common=archive(COMMON); accepted=archive(TERRAIN); current={}
    for name in FILES:
        path='tools/PluginBuilder/'+name
        text=normalized((root/path).read_bytes())
        if name=='RedHollowEnvironment.cs':
            for line in ACCESS:
                if text.count(line)!=1:raise AssertionError('Current access-only exclusion changed: '+line)
                text=text.replace(line,'')
        if text!=normalized(accepted[path]):raise AssertionError('Selected current RH terrain differs from accepted implementation: '+name)
        current[path]=text.encode()
    path='tools/PluginBuilder/formkeys.txt'
    old=normalized(common[path]); keys=normalized((root/path).read_bytes()).splitlines()
    pairs=list(zip(keys[::2],keys[1::2])); tail=[(n,k)for n,k in pairs if n.startswith('TLM_REF_RHE_T2_')]
    if len(tail)!=72 or len(set(n for n,k in tail))!=72:raise AssertionError('Current terrain allocation membership')
    allocation=old+''.join(n+'\n'+k+'\n'for n,k in tail)
    if allocation!=normalized(accepted[path]):raise AssertionError('Current terrain allocation prefix/tail changed')
    current[path]=allocation.encode()
    newer=dict(common);newer.update(current)
    for source in (common,newer):
        if any('BlackLedger' in n or 'Blackstone' in n for n in source):raise AssertionError('Unrelated later source in RH comparison')
    return common,newer,current

def prepare(root,master,archive,build):
    baseline,current,selected=select(root,archive)
    for label,source,output in [('rh-common-baseline',baseline,'baseline-projection'),('rh-common-current',current,'projection')]:
        target=root/'build/composed'/label;target.mkdir(parents=True,exist_ok=True)
        # Refuse stale unexpected source files instead of silently compiling them.
        existing={p.relative_to(target).as_posix() for p in target.rglob('*') if p.is_file() and not any(x in ('bin','obj','build') for x in p.relative_to(target).parts)}
        if existing-set(source):raise AssertionError('Unexpected comparison source files: '+repr(existing-set(source)))
        for name,data in source.items():
            path=target/name;path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(data)
        build(target,master,root/'build/terrain-002'/output,label)
    from rh_terrain_projection import verify,records
    a=(root/'build/terrain-002/projection/TheLastMeridian.esp').read_bytes();b=(root/'build/terrain-002/baseline-projection/TheLastMeridian.esp').read_bytes()
    result=verify(a,b)
    for raw in (a,b):
        _,names=records(raw)
        if any(n.startswith(('TLM_BL','TLM_BS','TLM_CELL_Black','TLM_WRLD_BS')) for n in names):raise AssertionError('Unrelated later emitted forms')
    return {'commonSource':COMMON,'acceptedTerrainSource':TERRAIN,'currentTerrainSelection':{n:hashlib.sha256(v).hexdigest().upper() for n,v in selected.items()},'strictProjection':result,'scope':'Symmetric synthetic RH-only comparison, not current full-producer or native proof'}
