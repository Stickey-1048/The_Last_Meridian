"""One-field private visual experiment; no mesh-contact or activation claim."""
from pathlib import Path
import sys,hashlib,json,struct
R=Path(__file__).resolve().parents[2]; H=Path(__file__).resolve().parent
sys.path.insert(0,str(R/'tools/SheriffWorld'));from raw import records,pose
base=R.parent/'opening-visible-grove-005/tools/OpeningWoodlandDensity/build/density-visible-002/TLMWorldSlice.esp'
out=H/'build/contact-001/TLMWorldSlice.esp'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest().upper()
assert sha(base)=='E73F86C82142FF95C74C447828CD0856E30B15CFC31FB37F04DADFF60A44D13E'
a,_=records(base); b,_=records(out)
assert len(a)==len(b)==839 and a.keys()==b.keys()
for k,x in a.items():
 y=b[k]
 if k!=0x2000903:assert x==y,('Unapproved record change',x['name'])
 else:
  assert (x['header'],x['parents'])==(y['header'],y['parents'])
  assert [(k,v)for k,v in x['ordered']if k!=b'DATA']==[(k,v)for k,v in y['ordered']if k!=b'DATA']
  assert pose(x)==[850.,1000.,-180.,0.,0.,0.]
  assert y['tags'][b'DATA']==x['tags'][b'DATA'][:8]+struct.pack('<f',-191.95)+x['tags'][b'DATA'][12:]
x=a[0x2000903];y=b[0x2000903];before=base.read_bytes();after=out.read_bytes()
assert not x['flags']&0x40000 and before.count(x['header'])==1
offset=before.index(x['header']);end=offset+24+struct.unpack_from('<I',x['header'],4)[0]
record=before[offset:end];assert record.count(x['tags'][b'DATA'])==1
assert after==before[:offset]+record.replace(x['tags'][b'DATA'],y['tags'][b'DATA'])+before[end:],'Whole file must differ only by the single pose field'
receipt={'baseline':sha(base),'world':sha(out),'records':839,'delta':'Only REFR02000903 DATA.Z -180 -> -191.95; every other field/header/group/record literal',
 'status':'PRIVATE A/B; actual contact/visibility and ordinary activation not yet verified',
 'interpretation':'Flat-foot hypothesis predicts 0.05 above road; full-root alternative predicts about14.35 embed. GetHeight is not mesh contact.',
 'sourcePins':{str(p.relative_to(R)).replace('\\','/'):sha(p)for p in[R/'tools/WorldSliceBuilder/Program.cs',Path(__file__)]}}
(H/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
print('PASS839 records; exact sole903 Z float substitution, all remaining bytes/parents/headers literal; private native A/B pending')
