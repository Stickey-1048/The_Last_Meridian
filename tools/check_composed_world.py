"""World composition gate: preserve accepted river except exact voice VMAD."""
from pathlib import Path
import importlib.util,struct
root=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('raw',root/'tools/GreenwaterRiver/raw.py')
raw=importlib.util.module_from_spec(spec);spec.loader.exec_module(raw)
old,names=raw.records(root.parent/'greenwater-river-environment-001/tools/GreenwaterRiver/build/river-011/TLMWorldSlice.esp')
new,newnames=raw.records(root/'tools/GreenwaterRiver/build/composed-001/TLMWorldSlice.esp')
voiced,voicenames=raw.records(root.parent/'quest-voices-001/build/quest-voices-world-001/TLMWorldSlice.esp')
assert set(old)==set(new) and len(new)==544
key=names['TLM_WS_RH']['id']
for fid,before in old.items():
    after=new[fid]
    assert before['name']==after['name'] and before['parents']==after['parents'] and before['flags']==after['flags']
    if fid!=key:assert before['ordered']==after['ordered'],('river or old world changed',before['name'])
    else:
        assert [(k,v)for k,v in before['ordered']if k!=b'VMAD']==[(k,v)for k,v in after['ordered']if k!=b'VMAD']
        reference=voicenames['TLM_WS_RH']['tags'][b'VMAD'];result=bytearray(reference)
        edits=[]
        for oldid in range(0x1000f6c,0x1000f71):
            needle=struct.pack('<I',oldid);start=0
            while (at:=reference.find(needle,start))>=0:edits.append((at,oldid+3));start=at+4
        assert len(edits)==2, 'Expected exactly the two optional Dinah bindings'
        for at,newid in edits:result[at:at+4]=struct.pack('<I',newid)
        assert after['tags'][b'VMAD']==bytes(result), 'Clone lost/remapped wrong sound or alias binding'
master,master_names=raw.records(root.parent/'playtest-fixes-integration-001/build/composed-voices-002/TheLastMeridian.esp')
assert raw.pose(master_names['TLM_REF_RH_Roster'])[:3]==[6144,640,56]
assert raw.pose(master_names['TLM_REF_RH_FiringControl'])[:3]==[2816,384,56]
for name in ['TLM_REF_RHE_AccessRosterDesk','TLM_REF_RHE_AccessFiringDesk']:
    assert name in master_names
print('PASS 544 world records: accepted terrain/water/controls and old IDs literal; sole RH VMAD equals accepted clone with exact two remapped sound bindings. Master-owned RH controls/supports verified.')
