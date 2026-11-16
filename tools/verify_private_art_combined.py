"""Composition of the two accepted read-only audits; no native acceptance."""
import argparse
import json
from pathlib import Path
from verify_private_fence_ab import audit as fence_audit
from verify_private_shelter_detail import audit as detail_audit, read


def audit(control,fence,detail,combined):
    fa=fence_audit(control,fence)
    da=detail_audit(control,detail)
    ca=detail_audit(fence,combined)
    assert fa['controlSha256']=='B056F66D23D18BA7D156177C64B67552B10B2A74234C78139FBDCD5AED660723'
    assert fa['specimenSha256']=='9EED4A7984AE1DFCCEEE6B44D623E0CE92EF73613DACBCB311DEACC904BBC37C'
    assert da['candidateSha256']=='E1279E42DAA19D94A628F1270D285EB8A175EE21579924C0DE51B017C25F5965'
    _,base=read(control/'TLMWorldSlice.esp');_,f=read(fence/'TLMWorldSlice.esp')
    _,d=read(detail/'TLMWorldSlice.esp');_,c=read(combined/'TLMWorldSlice.esp')
    assert d.keys()==c.keys() and f.keys()==base.keys()
    added=d.keys()-base.keys();assert len(added)==6
    assert all(d[key]==c[key] for key in added), 'new props differ from accepted detail bytes'
    assert d['TES4',0]==c['TES4',0], 'combined allocation/header differs from detail'
    changed={key for key in base if key!=('TES4',0) and base[key]!=c[key]}
    fence_changes={key for key in base if key!=('TES4',0) and base[key]!=f[key]}
    assert changed==fence_changes and len(changed)==16
    assert all(c[key]==f[key] for key in changed), 'fence bytes differ from accepted fence'
    assert all(base[key]==c[key] for key in base if key!=('TES4',0) and key not in changed)
    for filename in ('private-fence-comparison.json','world-story.json','world-expansion.json'):
        assert (fence/filename).read_bytes()==(combined/filename).read_bytes(),filename
    assert (detail/'private-shelter-details.json').read_bytes()==(combined/'private-shelter-details.json').read_bytes()
    return dict(mode='PRIVATE explicit composition;not owner adoption/native approval',
                controlSha256=fa['controlSha256'],fenceSha256=fa['specimenSha256'],detailSha256=da['candidateSha256'],combinedSha256=ca['candidateSha256'],
                oldMajorRecords=len(base),combinedMajorRecords=len(c),onlyExistingReferenceChanges='exact accepted16NAME links',
                unchangedExistingNonheaderRecords=len(base)-17,newOwnReferences=6,
                newReferenceBytesIdenticalToDetail=True,fenceReferenceBytesIdenticalToFence=True,
                headerBytesIdenticalToDetail=True,all29StoryRefsAndLandGatewayPreserved=True,
                routeSamples=ca['originalRouteSamples'],minimumRouteDistance=ca['minimumOriginalRouteDistance'],
                interiorAisleSamples=ca['newInteriorAisleSamples'],minimumInteriorAisleDistance=ca['minimumInteriorAisleDistance'],
                storyAnchors=ca['protectedStoryPoints'],minimumNewPropStandingDistance=ca['minimumNewPropStandingDistance'],
                minimumChangedFenceStandingDistance=fa['minimumChangedFenceStandingDistance'],northSupplyGroundMargin=fa['northSupplyGroundObstacleMargin'],
                requiredRouteRadius=96,requiredStandingRadius=128,highestNewPropTop=ca['highestNewPropTop'],roofUnderside=214,
                nativeProof='No engine/appearance/darker/support/collision/walking/containment/navmesh or service acceptance')


if __name__=='__main__':
    p=argparse.ArgumentParser()
    for name in ('control','fence','detail','combined'):p.add_argument(name,type=Path)
    a=p.parse_args();print(json.dumps(audit(a.control,a.fence,a.detail,a.combined),indent=2))
