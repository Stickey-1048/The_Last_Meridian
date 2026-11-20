"""Exact accepted RH-TERRAIN-002 layout profile. Raw records, no native claim."""
import hashlib
from rh_terrain_projection import records,subs
EXPECTED_REFS={'TLM_REF_RHE_T2_ReleasedWaitingRoof': 3627, 'TLM_REF_RHE_T2_ReleasedWaitingPost896_128': 3628, 'TLM_REF_RHE_T2_ReleasedWaitingPost896_384': 3629, 'TLM_REF_RHE_T2_ReleasedWaitingPost1152_128': 3630, 'TLM_REF_RHE_T2_ReleasedWaitingPost1152_384': 3631, 'TLM_REF_RHE_T2_CabinFloor1024_2944': 3560, 'TLM_REF_RHE_T2_CabinRoof1024_2944': 3561, 'TLM_REF_RHE_T2_CabinFloor1024_3200': 3562, 'TLM_REF_RHE_T2_CabinRoof1024_3200': 3563, 'TLM_REF_RHE_T2_CabinFloor1280_2944': 3564, 'TLM_REF_RHE_T2_CabinRoof1280_2944': 3565, 'TLM_REF_RHE_T2_CabinFloor1280_3200': 3566, 'TLM_REF_RHE_T2_CabinRoof1280_3200': 3567, 'TLM_REF_RHE_T2_CabinFloor1536_2944': 3568, 'TLM_REF_RHE_T2_CabinRoof1536_2944': 3569, 'TLM_REF_RHE_T2_CabinFloor1536_3200': 3570, 'TLM_REF_RHE_T2_CabinRoof1536_3200': 3571, 'TLM_REF_RHE_T2_CabinBack1024': 3572, 'TLM_REF_RHE_T2_CabinBack1280': 3573, 'TLM_REF_RHE_T2_CabinBack1536': 3574, 'TLM_REF_RHE_T2_CabinWest2944': 3575, 'TLM_REF_RHE_T2_CabinEast2944': 3576, 'TLM_REF_RHE_T2_CabinWest3200': 3577, 'TLM_REF_RHE_T2_CabinEast3200': 3578, 'TLM_REF_RHE_T2_BedA': 3579, 'TLM_REF_RHE_T2_BedB': 3580, 'TLM_REF_RHE_T2_Couch': 3581, 'TLM_REF_RHE_T2_CabinEntryFloor': 3582, 'TLM_REF_RHE_T2_CampFence768': 3583, 'TLM_REF_RHE_T2_CampFence896': 3584, 'TLM_REF_RHE_T2_CampFence1024': 3585, 'TLM_REF_RHE_T2_CampFence1152': 3586, 'TLM_REF_RHE_T2_CampFence1280': 3587, 'TLM_REF_RHE_T2_CampFence1408': 3588, 'TLM_REF_RHE_T2_CampFence1536': 3589, 'TLM_REF_RHE_T2_CampFence1664': 3590, 'TLM_REF_RHE_T2_CampFence2304': 3591, 'TLM_REF_RHE_T2_CampFence2432': 3592, 'TLM_REF_RHE_T2_CampFence2560': 3593, 'TLM_REF_RHE_T2_CampFence2688': 3594, 'TLM_REF_RHE_T2_CampFence2816': 3595, 'TLM_REF_RHE_T2_CampFence2944': 3596, 'TLM_REF_RHE_T2_CampFence3072': 3597, 'TLM_REF_RHE_T2_CampFence3200': 3598, 'TLM_REF_RHE_T2_Tree384_2560': 3599, 'TLM_REF_RHE_T2_Tree640_2944': 3600, 'TLM_REF_RHE_T2_Tree512_3456': 3601, 'TLM_REF_RHE_T2_Tree768_3712': 3602, 'TLM_REF_RHE_T2_Tree1536_3840': 3603, 'TLM_REF_RHE_T2_Tree3072_2304': 3604, 'TLM_REF_RHE_T2_Tree3328_2688': 3605, 'TLM_REF_RHE_T2_Tree3584_3072': 3606, 'TLM_REF_RHE_T2_Tree3328_3712': 3607, 'TLM_REF_RHE_T2_Tree2944_3840': 3608, 'TLM_REF_RHE_T2_Rock768_2304': 3609, 'TLM_REF_RHE_T2_Rock1024_2432': 3610, 'TLM_REF_RHE_T2_Rock2944_2560': 3611, 'TLM_REF_RHE_T2_Rock3072_2816': 3612, 'TLM_REF_RHE_T2_Rock2944_3584': 3613, 'TLM_REF_RHE_T2_Rock1792_3712': 3614, 'TLM_REF_RHE_T2_RoutePost1792': 3615, 'TLM_REF_RHE_T2_RoutePost2304': 3616, 'TLM_REF_RHE_T2_WestBoundary1792': 3617, 'TLM_REF_RHE_T2_EastBoundary1792': 3618, 'TLM_REF_RHE_T2_WestBoundary2304': 3619, 'TLM_REF_RHE_T2_EastBoundary2304': 3620, 'TLM_REF_RHE_T2_WestBoundary2816': 3621, 'TLM_REF_RHE_T2_EastBoundary2816': 3622, 'TLM_REF_RHE_T2_WestBoundary3328': 3623, 'TLM_REF_RHE_T2_EastBoundary3328': 3624, 'TLM_REF_RHE_T2_WestBoundary3840': 3625, 'TLM_REF_RHE_T2_EastBoundary3840': 3626}
HEIGHT_SHA256='214F1740FFE0A0E4ABF57E369A1080E41A8EA044CDB4DC911CA2192C081C2666'
NORMAL_SHA256='5309760A0B4C3EC9340F7B42D08547A1666CD96852D9C2990A441A90507B943E'

def context(raw):
    rows,names=records(raw);found=[]
    for (kind,fid),(_,body,_) in rows.items():
        name=dict(subs(body)).get(b'EDID',b'').rstrip(b'\0').decode()
        if name.startswith('TLM_REF_RHE_T2_'):found.append((name,kind,fid&0xffffff))
    if not found:return False,[]
    if len(found)!=72 or len({n for n,_,_ in found})!=72 or {n:f for n,k,f in found if k==b'REFR'}!=EXPECTED_REFS:
        return False,['RH terrain successor exact72reference names/keys mismatch']
    return True,[]

def land_problems(height,normals):
    out=[]
    if hashlib.sha256(height).hexdigest().upper()!=HEIGHT_SHA256:out.append('RH exact accepted terrain height bytes mismatch')
    if hashlib.sha256(normals).hexdigest().upper()!=NORMAL_SHA256:out.append('RH exact accepted terrain normal bytes mismatch')
    return out
