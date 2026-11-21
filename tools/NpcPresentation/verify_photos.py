from pathlib import Path
import struct,json,hashlib
import verify as v
ROOT=Path(__file__).resolve().parent;OUT=ROOT/'build/photo-001/TLMNpcPresentation.esp';OLD=ROOT.parents[3]/'work/npc-presentation-005/tools/NpcPresentation/build/lit-001/TLMNpcPresentation.esp'
def verify_photos(raw):
 old=v.rows(OLD.read_bytes());now=v.rows(raw);plan=json.loads((ROOT/'audition-plan.json').read_text());own=lambda key:int(key.split(':')[0],16)|0x02000000
 for k,row in old.items():
  if k==(b'TES4',0):assert[(a,b)for a,b in v.subs(row[1])if a!=b'HEDR']==[(a,b)for a,b in v.subs(now[k][1])if a!=b'HEDR']
  else:assert row==now[k],'Old005record changed'
 assert len(plan['photos'])==3;expected=set();sourceCell=dict(v.subs(old[b'CELL',0x02000800][1]));bases={p['Id']:own(p['prototype'])for p in plan['actors']};fill=own(plan['lighting']['fill']);markerRecords=v.native({int(p['arrivalBase'].split(':')[0],16)for p in plan['photos']})
 for photo,subject in zip(plan['photos'],['Owen','Ada','Miriam']):
  assert photo['subject']==subject and photo['EditorID']=='TLM_NPC_Photo_'+subject;cell=own(photo['cell']);expected.add((b'CELL',cell));flags,b,parent=now[b'CELL',cell];ss=dict(v.subs(b));assert flags==old[b'CELL',0x02000800][0]
  assert ss[b'EDID'].rstrip(b'\0').decode()==photo['EditorID'];assert[(k,b)for k,b in v.subs(b)if k not in[b'EDID',b'FULL']]==[(k,b)for k,b in v.subs(old[b'CELL',0x02000800][1])if k not in[b'EDID',b'FULL']],'Portrait lighting/header changed'
  for ref,original in zip(photo['geometry'],plan['room']):
   key=own(ref);expected.add((b'REFR',key));f,b,chain=now[b'REFR',key];oldf,oldb,_=old[b'REFR',own(original['key'])];assert f==oldf and[(k,b)for k,b in v.subs(b)if k!=b'EDID']==[(k,b)for k,b in v.subs(oldb)if k!=b'EDID'];assert chain[-2:]==((6,cell),(9,cell))
  assert len(photo['geometry'])==22
  key=own(photo['actor']);expected.add((b'ACHR',key));f,b,chain=now[b'ACHR',key];s=dict(v.subs(b));assert f==0x400 and struct.unpack('<I',s[b'NAME'])[0]==bases[subject] and struct.unpack('<6f',s[b'DATA'])==struct.unpack('<6f',struct.pack('<6f',0,120,16,0,0,3.141592653589793)),'Wrong portrait actor/base/pose';assert chain[-2:]==((6,cell),(8,cell))
  key=own(photo['light']);expected.add((b'REFR',key));f,b,chain=now[b'REFR',key];s=dict(v.subs(b));assert f==0 and struct.unpack('<I',s[b'NAME'])[0]==fill and struct.unpack('<6f',s[b'DATA'])==(0,0,160,0,0,0);assert chain[-2:]==((6,cell),(9,cell))
  key=own(photo['arrival']);expected.add((b'REFR',key));f,b,chain=now[b'REFR',key];s=dict(v.subs(b));marker=int(photo['arrivalBase'].split(':')[0],16);native=markerRecords[b'STAT',marker];assert native[b'EDID'].rstrip(b'\0')==b'COCMarkerHeading';assert f==0x400 and struct.unpack('<I',s[b'NAME'])[0]==marker and struct.unpack('<6f',s[b'DATA'])==(0,0,16,0,0,0);assert chain[-2:]==((6,cell),(8,cell))
 assert set(now)-set(old)==expected and len(expected)==78,'Non-append-only portrait delta'
 return {'status':'PASS','old005recordsExactExceptHedr':42,'newCells':3,'sharedExistingNpcBases':3,'copiedKitRefs':66,'fillRefs':3,'nativeCocMarkers':3,'newRecords':78,'nativeFraming':'OPEN'}
if __name__=='__main__':print(json.dumps(verify_photos(OUT.read_bytes()),indent=2))
