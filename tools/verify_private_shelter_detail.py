"""Read-only six-ref preservation/rotated-bound screen, not native proof."""
import argparse
import hashlib
import json
import math
from pathlib import Path
import struct
import zlib
from check_plugin_layout import records, subrecords


def read(path):
    buf=path.read_bytes();result={}
    for kind,off,size,form,flags in records(buf,0,len(buf)):
        data=buf[off:off+size]
        if flags&0x40000:data=zlib.decompress(data[4:])
        result[kind,form]=(buf[off-24:off+size],list(subrecords(data)))
    return buf,result


def distance(x,y,p):
    return math.hypot(max(p['minX']-x,0,x-p['maxX']),max(p['minY']-y,0,y-p['maxY']))


def audit(control,candidate):
    a,old=read(control/'TLMWorldSlice.esp');b,new=read(candidate/'TLMWorldSlice.esp')
    assert old.keys()<=new.keys() and len(new)-len(old)==6
    for key in old:
        if key!=('TES4',0):assert old[key][0]==new[key][0],key
    before,after=old['TES4',0],new['TES4',0]
    assert before[0][:24]==after[0][:24]
    assert [p for p in before[1] if p[0]!='HEDR']==[p for p in after[1] if p[0]!='HEDR']
    oh=struct.unpack('<fII',next(v for k,v in before[1] if k=='HEDR'))
    nh=struct.unpack('<fII',next(v for k,v in after[1] if k=='HEDR'))
    assert nh==(oh[0],oh[1]+6,oh[2]+6)
    detail=json.loads((candidate/'private-shelter-details.json').read_text())['detail']
    rows={p['name']:p for p in detail['assetsAndPlacements']};assert len(rows)==6
    for key in new.keys()-old.keys():
        assert key[0]=='REFR'
        parts=dict(new[key][1]);name=parts['EDID'].rstrip(b'\0').decode();row=rows[name]
        assert parts['NAME']==struct.pack('<I',int(row['form'].split(':')[0],16))
        at=struct.unpack('<6f',parts['DATA'])
        assert all(abs(x-y)<.001 for x,y in zip(at,(row['x'],row['y'],16,0,0,row['yaw'])))
    ac=json.loads((control/'world-slice.json').read_text());bc=json.loads((candidate/'world-slice.json').read_text())
    assert len(bc['placements'])==len(ac['placements'])+6==291
    assert bc['placements'][:285]==ac['placements']
    assert ac['mainRoute']==bc['mainRoute'] and ac['bypassRoute']==bc['bypassRoute']
    for file in ('world-story.json','world-expansion.json'):
        assert (control/file).read_bytes()==(candidate/file).read_bytes(),file
    clearance=json.loads((candidate/'world-clearance.json').read_text());obstacles=clearance['obstacles']
    selected=[p for p in obstacles if p['id'].startswith('EX_DETAIL_')];assert len(selected)==6
    for box in selected:
        r=rows['TLM_WS_'+box['id']]
        corners=[(r['x']+x*math.cos(r['yaw'])+y*math.sin(r['yaw']),r['y']+y*math.cos(r['yaw'])-x*math.sin(r['yaw'])) for x in (r['min'][0],r['max'][0]) for y in (r['min'][1],r['max'][1])]
        for field,value in [('minX',min(x for x,y in corners)),('maxX',max(x for x,y in corners)),('minY',min(y for x,y in corners)),('maxY',max(y for x,y in corners))]:assert abs(box[field]-value)<.001
        assert r['min'][2]==0 and r['z']==16 and r['top']<214
    expansion=json.loads((candidate/'world-expansion.json').read_text())
    routes=[bc['mainRoute'],bc['bypassRoute']]+[r['points'] for r in expansion['routes']]
    minimum=math.inf;samples=0
    for route in routes:
        for p,q in zip(route,route[1:]):
            for tick in range(101):
                t=tick/100;x=p['x']*(1-t)+q['x']*t;y=p['y']*(1-t)+q['y']*t
                minimum=min(minimum,*(distance(x,y,o) for o in obstacles));samples+=1
    assert minimum>=96
    aisle_min=math.inf
    for aisle in detail['aisles']:
        for tick in range(101):
            y=aisle['startY']+(aisle['endY']-aisle['startY'])*tick/100
            aisle_min=min(aisle_min,*(distance(aisle['x'],y,o) for o in obstacles if 'Floor' not in o['id']))
    assert aisle_min>=96
    standing=min(distance(p['x'],p['y'],o) for p in clearance['protectedPoints'] for o in selected)
    assert standing>=128
    return dict(controlSha256=hashlib.sha256(a).hexdigest().upper(),candidateSha256=hashlib.sha256(b).hexdigest().upper(),oldMajorRecords=len(old),newMajorRecords=len(new),unchangedOldMajorRecords=len(old)-1,headerOnly='HEDR recordcount/nextFormID both+6;version/otherheaderdata unchanged',newOwnStaticRefs=6,oldShellRefsByteEqual=285,oldStoryRefsByteEqual=29,oldLandAndGatewayByteEqual=True,originalRouteSamples=samples,minimumOriginalRouteDistance=minimum,requiredRadius=96,newInteriorAisleSamples=202,minimumInteriorAisleDistance=aisle_min,aisleFloorExclusion='Only existing walk-support floors atZ16 excluded;not upright obstacles',protectedStoryPoints=len(clearance['protectedPoints']),minimumNewPropStandingDistance=standing,lowestNewPropBase=16,highestNewPropTop=max(r['top'] for r in rows.values()),roofUnderside=214,nativeProof='Not installed;no appearance/support/collision/interaction/navigation/service proof',newProps=list(rows.values()))


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('control',type=Path);parser.add_argument('candidate',type=Path);a=parser.parse_args()
    print(json.dumps(audit(a.control,a.candidate),indent=2))
