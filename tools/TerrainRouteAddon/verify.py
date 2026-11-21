"""Independent exact raw addon/header/link and numerical support audit; no native claim."""
from pathlib import Path
import collections,hashlib,json,math,struct,zlib
ROOT=Path(__file__).resolve().parent
WORKSPACE=ROOT.parents[3]
INPUTS={'TheLastMeridian.esp':(WORKSPACE/'work/rh-return-account-build-f491eeb/build/licensed-return-account-skeleton-001/bundle/TheLastMeridian.esp','5C22EE73009BF1F6B75CFBD5C5E52A749B2086ABA847521B5B294E3ED66E81FF'),'TLMWorldSlice.esp':(WORKSPACE/'work/rh-return-account-build-f491eeb/build/licensed-return-account-skeleton-001/bundle/TLMWorldSlice.esp','ACE5F0A233A1E8124555B15812FFC445FF1AB23DAAA4D672FCDEC231C1D93FAF'),'TLMSpectacleTerrainPrototype.esp':(WORKSPACE/'work/spectacle-route-landmarks-001/build/landmarks-002/TLMSpectacleTerrainPrototype.esp','6EB3A6167DE06353E39660180DE8858DBBBCBDEB793D3C84770BC7739AE6A81C')}
OUTPUT=ROOT/'build/connection-003/TLMOptionalTerrainRoute.esp'

def subs(data):
    out=[];p=0;extended=None
    while p<len(data):
        k,n=struct.unpack_from('<4sH',data,p);p+=6
        if k==b'XXXX':extended=struct.unpack_from('<I',data,p)[0];p+=n;continue
        if extended is not None:n,extended=extended,None
        out.append((k,data[p:p+n]));p+=n
    assert p==len(data) and extended is None;return out

def rows(raw):
    out={}
    def walk(start,end,chain=()):
        p=start
        while p<end:
            tag,n,flags,fid=struct.unpack_from('<4sIII',raw,p)
            if tag==b'GRUP':walk(p+24,p+n,chain+((fid,flags),));p+=n;continue
            body=raw[p+24:p+24+n]
            if flags&0x40000:body=zlib.decompress(body[4:])
            assert (tag,fid) not in out,'Duplicate record'
            out[tag,fid]=(flags,body,chain);p+=24+n
        assert p==end
    walk(0,len(raw));return out

def masters(r):return [v.rstrip(b'\0').decode() for k,v in subs(r[b'TES4',0][1]) if k==b'MAST']
def string(b):return b.rstrip(b'\0').decode()
def remap(fid,before,after):
    if fid==0:return 0
    index=fid>>24;assert index<len(before),'Undeclared source index'
    return (after.index(before[index])<<24)|(fid&0xffffff)
def header_payload(body,tag,before,after):
    allowed={b'EDID',b'FULL',b'CNAM',b'NAM2',b'DNAM',b'ONAM',b'DATA',b'NAM0',b'NAM9'} if tag==b'WRLD' else {b'EDID',b'DATA',b'LTMP'}
    result=[]
    for key,value in subs(body):
        assert key in allowed,'Unexpected header behavior'
        if key in (b'CNAM',b'NAM2',b'LTMP'):value=struct.pack('<I',remap(struct.unpack('<I',value)[0],before,after))
        result.append((key,value))
    return result

def vmad(body):
    p=0
    def num(fmt):
        nonlocal p
        value=struct.unpack_from('<'+fmt,body,p);p+=struct.calcsize('<'+fmt);return value[0] if len(value)==1 else value
    def text():
        nonlocal p
        n=num('H');value=body[p:p+n].decode();p+=n;return value
    assert num('HHH')==(6,2,1);name=text();assert num('B')==0;count=num('H');out={}
    for _ in range(count):
        key=text();kind=num('B');assert num('B')==1 and key not in out
        if kind==1:
            zero,alias,fid=num('HhI');assert zero==0 and alias==-1;out[key]=fid
        else:assert kind==5;out[key]=bool(num('B'))
    assert p==len(body);return name,out

def heights(body):
    b=dict(subs(body))[b'VHGT'];first=struct.unpack_from('<f',b)[0];out=[]
    for y in range(33):
        row=[];value=first
        for x in range(33):value+=struct.unpack_from('<b',b,4+y*33+x)[0];row.append(value*8)
        first=row[0]/8;out.append(row)
    return out

def verify(raw=None):
    incoming={}
    for name,(path,pin) in INPUTS.items():
        assert hashlib.sha256(path.read_bytes()).hexdigest().upper()==pin,'Frozen dependency changed: '+name
        incoming[name]=rows(path.read_bytes())
    r=rows(raw if raw is not None else OUTPUT.read_bytes())
    expected_masters=['Fallout4.esm','TLMSpectacleTerrainPrototype.esp','TLMWorldSlice.esp']
    assert masters(r)==expected_masters,'Exact direct dependencies/order differ'
    full=expected_masters+['TLMOptionalTerrainRoute.esp'];own=len(expected_masters)<<24
    assert collections.Counter(k[0] for k in r)=={b'TES4':1,b'ACTI':2,b'MESG':2,b'WRLD':2,b'CELL':2,b'REFR':3},'Unexpected behavior/old record copied'
    for name in ('TLMWorldSlice.esp','TLMSpectacleTerrainPrototype.esp'):
        old=incoming[name];before=masters(old)+[name];i=before.index(name);j=full.index(name)
        for tag,local in ((b'WRLD',0x800),(b'CELL',0x801)):
            source=old[tag,(i<<24)|local];target=r[tag,(j<<24)|local]
            assert source[0]==target[0],'Header flags changed'
            assert header_payload(source[1],tag,before,full)==subs(target[1]),'Header payload changed beyond FormKey remap'
    a=own|0x800;b=own|0x801;go=own|0x802;ret=own|0x803;anchor=own|0x804;outbound=own|0x805;back=own|0x806
    for key,name in ((a,'[Development] Visit terrain preview'),(b,'[Development] Return to Meridian preview')):
        flags,body,chain=r[b'ACTI',key];s=dict(subs(body))
        assert flags==0 and len(s)==len(subs(body)) and set(s)=={b'EDID',b'OBND',b'FULL',b'MODL',b'MODT',b'ATTX'}
        assert string(s[b'FULL'])==name and string(s[b'MODL'])=='Props\\Clipboard_Prewar.nif'
        assert struct.unpack('<6h',s[b'OBND'])==(-8,-11,0,8,12,1)
    for key in (go,ret):
        flags,body,chain=r[b'MESG',key];s=subs(body)
        assert flags==0 and len(s)==7 and set(k for k,v in s)=={b'EDID',b'DESC',b'FULL',b'INAM',b'DNAM',b'ITXT'}
        assert [string(v) for k,v in s if k==b'ITXT']==['Travel','Stay here']
        assert struct.unpack('<I',dict(s)[b'DNAM'])[0]&1,'Confirmation is not a message box'
    desired={anchor:('TLM_DEV_REF_MeridianReturnAnchor',2,(448,640,32),None),outbound:('TLM_DEV_REF_VisitTerrain',2,(256,512,0),{'Prompt':go,'Destination':(1<<24)|0x806,'SourceWorld':(2<<24)|0x800,'DestinationWorld':(1<<24)|0x800,'Outbound':True}),back:('TLM_DEV_REF_ReturnMeridian',1,(3184,1104,576),{'Prompt':ret,'Destination':anchor,'SourceWorld':(1<<24)|0x800,'DestinationWorld':(2<<24)|0x800,'Outbound':False})}
    for key,(name,index,pose,properties) in desired.items():
        flags,body,chain=r[b'REFR',key];s=dict(subs(body));assert len(s)==len(subs(body));world=(index<<24)|0x800;cell=(index<<24)|0x801
        assert flags==0x400 and string(s[b'EDID'])==name,'Own reference identity/persistence changed'
        assert chain==((0,int.from_bytes(b'WRLD','little')),(1,world),(6,cell),(8,cell)),'Wrong persistent parent'
        assert set(s)==({b'EDID',b'NAME',b'DATA',b'VMAD'} if properties else {b'EDID',b'NAME',b'DATA'})
        xyz=struct.unpack('<6f',s[b'DATA']);assert xyz[:3]==pose,'Control/anchor pose changed'
        if properties:
            assert vmad(s[b'VMAD'])==('TLMDev:OptionalTerrainTravel',properties),'Wrong script/destination/confirmation/world binding'
            assert struct.unpack('<I',s[b'NAME'])[0]==(a if key==outbound else b)
        else:
            source=dict(subs(incoming['TLMWorldSlice.esp'][b'REFR',(2<<24)|0x804][1]))
            assert s[b'NAME']==source[b'NAME'] and s[b'DATA']==source[b'DATA'],'Return anchor is not the reviewed spawn pose'
    # Two tiny ground placards, not barriers: outside original spawn/trail center footprint.
    assert math.hypot(256-448,512-640)>192 and 112<math.hypot(3184-3072,1104-1024)<192
    grid=heights(incoming['TLMSpectacleTerrainPrototype.esp'][b'LAND',(1<<24)|0x803][1])
    assert all(grid[y][x]==576 for x in (24,25) for y in (8,9)),"Return control footprint is not on a flat dry LAND patch"
    trail_file=WORKSPACE/'work/spectacle-route-landmarks-001/trail-metadata.json'
    trail_bytes=trail_file.read_bytes()
    assert hashlib.sha256(trail_bytes).hexdigest().upper()=='FBFE762F7F1C28E46DF9A2E66EE28C375B18881B9E3388DB1DEF6BF4ABFB61BB','Reviewed57point trail changed'
    trail=json.loads(trail_bytes)['newLocalXYRoute'];assert len(trail)==57
    box=(3176,1093,3192,1116);clearance=math.inf
    for first,last in zip(trail,trail[1:]):
        if first[1]==last[1]:dx=max(box[0]-max(first[0],last[0]),min(first[0],last[0])-box[2],0);dy=max(box[1]-first[1],first[1]-box[3],0)
        else:
            assert first[0]==last[0]
            dx=max(box[0]-first[0],first[0]-box[2],0);dy=max(box[1]-max(first[1],last[1]),min(first[1],last[1])-box[3],0)
        clearance=min(clearance,math.hypot(dx,dy))
    assert clearance>112,'New ground control narrows the reviewed192wide terrain trail'
    return {'records':len(r),'ownPersistentReferences':3,'headerOverrides':4,'returnControlTrailClearance':clearance,'directMasters':expected_masters,'transitiveStoryMaster':'TheLastMeridian.esp','terrainDestination':'000806:TLMSpectacleTerrainPrototype.esp','returnAnchor':'000804:TLMOptionalTerrainRoute.esp','nativeAcceptance':None}


def verify_source():
    import subprocess
    manifest=json.loads((ROOT/'source-receipt.json').read_text(encoding='utf-8'))
    for name,pin in manifest['sourceFilesSha256'].items():
        assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest().upper()==pin,'Component source changed: '+name
    source=set(manifest['sourceFilesSha256'])|{'source-receipt.json'}
    files={p.relative_to(ROOT).as_posix() for p in ROOT.rglob('*') if p.is_file() and not any(n in ('build','bin','obj','__pycache__') for n in p.relative_to(ROOT).parts)}
    assert source==files,'Undeclared component source'
    tree=ROOT.parents[1]
    changed=subprocess.check_output(['git','diff','--name-only','f491eeb4e670d306530446b60f82785950dbb747'],cwd=tree,text=True).splitlines()
    assert all(n.startswith('tools/TerrainRouteAddon/') for n in changed),'Frozen f491 source outside addon changed'
    assert manifest['nativeAcceptance'] is None
    return {'source':'PASS','base':manifest['baseSource'],'nativeAcceptance':None}

if __name__=='__main__':
    import sys
    assert sys.argv[1:] in ([],['--source']),'Unsupported check arguments'
    print(json.dumps(verify_source() if sys.argv[1:] else verify(),indent=2))
