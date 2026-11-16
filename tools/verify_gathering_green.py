"""Independent raw/bounds screen for the five-ref green; no engine proof."""
import argparse,json,math,struct,hashlib
from pathlib import Path
from verify_private_shelter_detail import read,distance

ASSETS={0xDF45A:((-82,-43,0),(82,12,62)),0x6356D:((-46,-49,3),(49,51,36)),0x2F79B:((-60,-46,-59),(78,69,30))}


def screen(routes,obstacles):
    minimum=math.inf;count=0
    for route in routes:
        for a,b in zip(route,route[1:]):
            for tick in range(101):
                t=tick/100;x=a['x']*(1-t)+b['x']*t;y=a['y']*(1-t)+b['y']*t
                minimum=min(minimum,*(distance(x,y,p) for p in obstacles));count+=1
    return dict(samples=count,minimum=minimum)


def audit(control,candidate):
    a,old=read(control/'TLMWorldSlice.esp');b,new=read(candidate/'TLMWorldSlice.esp')
    assert len(old)==328 and len(new)==333 and old.keys()<=new.keys()
    for key in old:
        if key!=('TES4',0):assert old[key]==new[key],key
    before,after=old['TES4',0],new['TES4',0]
    assert before[0][:24]==after[0][:24]
    assert [p for p in before[1] if p[0]!='HEDR']==[p for p in after[1] if p[0]!='HEDR']
    oh=struct.unpack('<fII',next(v for k,v in before[1] if k=='HEDR'))
    nh=struct.unpack('<fII',next(v for k,v in after[1] if k=='HEDR'))
    assert nh==(oh[0],oh[1]+5,oh[2]+5)
    green=json.loads((candidate/'private-gathering-green.json').read_text())['green']
    rows={r['id']:r for r in green['placements']};assert len(rows)==5
    for key in new.keys()-old.keys():
        raw,parts=new[key];parts=dict(parts)
        assert key[0]=='REFR' and struct.unpack_from('<I',raw,8)[0]==0
        assert set(parts)=={'EDID','NAME','DATA'},'no scripts/ownership/extra flags on newrefs'
        name=parts['EDID'].rstrip(b'\0').decode();r=rows[name]
        assert key[1]&0xFFFFFF in range(0x947,0x94C)
        assert parts['NAME']==struct.pack('<I',int(r['base'].split(':')[0],16))
        at=struct.unpack('<6f',parts['DATA'])
        assert all(abs(x-y)<.001 for x,y in zip(at,(r['x'],r['y'],r['z'],0,0,r['yaw'])))
    ac=json.loads((control/'world-slice.json').read_text());bc=json.loads((candidate/'world-slice.json').read_text())
    assert len(ac['placements'])==291 and len(bc['placements'])==296 and bc['placements'][:291]==ac['placements']
    assert ac['mainRoute']==bc['mainRoute'] and ac['bypassRoute']==bc['bypassRoute']
    for file in ('world-story.json','world-expansion.json','private-shelter-details.json'):
        assert (control/file).read_bytes()==(candidate/file).read_bytes(),file
    clearance=json.loads((candidate/'world-clearance.json').read_text())
    oldclear=json.loads((control/'world-clearance.json').read_text())
    assert oldclear['protectedPoints']==clearance['protectedPoints']
    obstacles=clearance['obstacles'];selected=[p for p in obstacles if p['id'].startswith('EX_GREEN_')];assert len(selected)==5
    for box in selected:
        r=rows['TLM_WS_'+box['id']];lo,hi=ASSETS[int(r['base'].split(':')[0],16)]
        corners=[(r['x']+x*math.cos(r['yaw'])+y*math.sin(r['yaw']),r['y']+y*math.cos(r['yaw'])-x*math.sin(r['yaw']))for x in(lo[0],hi[0])for y in(lo[1],hi[1])]
        for field,value in [('minX',min(x for x,y in corners)),('maxX',max(x for x,y in corners)),('minY',min(y for x,y in corners)),('maxY',max(y for x,y in corners))]:assert abs(box[field]-value)<.001
        assert r['z']+lo[2]==0 and r['z']+hi[2]<=89
    expansion=json.loads((candidate/'world-expansion.json').read_text())
    oldroutes=[bc['mainRoute'],bc['bypassRoute']]+[r['points']for r in expansion['routes']]
    oldscreen=screen(oldroutes,obstacles);greenscreen=screen([r['points']for r in green['routes']],obstacles)
    assert oldscreen['minimum']>=96 and greenscreen['minimum']>=96
    # New approach joins the existing west street; all new branches meet loop vertices.
    routes={r['name']:r['points']for r in green['routes']}
    assert routes['Green approach'][0]=={'x':2260,'y':3455}
    assert routes['Green approach'][1]=={'x':2080,'y':3455}
    assert routes['Green walk loop'][0]==routes['Green walk loop'][-1]
    assert routes['Green approach'][1]['x']==routes['Green walk loop'][0]['x']
    assert 3303<=routes['Green approach'][1]['y']<=3607
    assert all(r['points'][0] in routes['Green walk loop']for r in green['routes']if 'bench' in r['name'])
    standing=min(distance(p['x'],p['y'],o)for p in green['standing']for o in obstacles if 'TLM_WS_'+o['id']!=p['bench'])
    story=min(distance(p['x'],p['y'],o)for p in clearance['protectedPoints']for o in selected)
    assert standing>=128 and story>=128
    return dict(controlSha256=hashlib.sha256(a).hexdigest().upper(),candidateSha256=hashlib.sha256(b).hexdigest().upper(),oldRecords=328,newRecords=333,all327OldNonheaderRecordsByteEqual=True,all291E127ShellAnd29StoryReferencesByteEqual=True,landGatewayAllFencesQuestsScriptsUnchanged=True,headerOnly='HEDR count/nextID+5',newRefs='947..94B;2FURNbasebenches+3STATbasehearth/rocks;newREFR records only',originalRoutes=oldscreen,newConnectedSpurLoopSideApproaches=greenscreen,benchStandingPoints=4,minimumOtherObstacleStandingDistance=standing,storyAnchors=27,minimumNewPropStoryDistance=story,terrainZ=0,benchAudit=green['benchAudit'],nativeAcceptance='UNTESTED playereligibility/markers/orientation/groundcontact/sit/stand/walking/collision;noNPC/services/owneradoption')


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('control',type=Path);p.add_argument('candidate',type=Path);a=p.parse_args()
    print(json.dumps(audit(a.control,a.candidate),indent=2))
