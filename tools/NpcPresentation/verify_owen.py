"""Owen-only successor raw/provenance checks, not native appearance approval."""
from pathlib import Path
import hashlib,json,struct,subprocess,zlib
import verify as prior
ROOT=Path(__file__).resolve().parent;REPO=ROOT.parents[1];BASE='9f490b38da8f448bd89f1e072a30c3944a01e263'
def pin(p):return hashlib.sha256(p.read_text(encoding='utf-8').replace('\r\n','\n').replace('\r','\n').encode()).hexdigest().upper()
def source_errors():
 r=json.loads((ROOT/'owen-source-receipt.json').read_text(encoding='utf-8'));out=[]
 if r['baseline']!=BASE or hashlib.sha256(subprocess.check_output(['git','ls-tree','-r',BASE],cwd=REPO)).hexdigest().upper()!=r['baselineTreeSha256']:out.append('Baseline changed')
 changed=subprocess.check_output(['git','diff','--name-only',BASE,'--'],cwd=REPO,text=True).splitlines();untracked=subprocess.check_output(['git','ls-files','--others','--exclude-standard'],cwd=REPO,text=True).splitlines();allowed={'tools/NpcPresentation/'+n for n in r['files']}|{'tools/NpcPresentation/owen-source-receipt.json'}
 if set(changed+untracked)!=allowed:out.append('Changes exceed exact Owen-only source delta')
 for n,h in r['files'].items():
  if not(ROOT/n).is_file()or pin(ROOT/n)!=h:out.append('Source pin '+n)
 return out

def native_ordered(ids):
 out={}
 with prior.MASTER.open('rb')as f:
  def walk(end):
   while f.tell()<end:
    at=f.tell();h=f.read(24);tag,n,flags,fid=struct.unpack('<4sIII',h[:16])
    if tag==b'GRUP':walk(at+n);continue
    if fid not in ids:f.seek(n,1);continue
    b=f.read(n);b=zlib.decompress(b[4:])if flags&0x40000 else b;out[tag,fid]=prior.subs(b)
  walk(prior.MASTER.stat().st_size)
 return out

def artifact(raw,old):
 a=prior.rows(old);b=prior.rows(raw);assert set(a)==set(b)and len(a)==121,'Record identities/topology changed'
 key=b'NPC_',0x02000818;oldparts=prior.subs(a[key][1]);newparts=prior.subs(b[key][1]);expected=[]
 for tag,value in oldparts:
  if tag==b'TPLT':assert value==struct.pack('<I',0x399dd);value=struct.pack('<I',0x3f23d)
  elif tag==b'TPTA':assert value==struct.pack('<13I',0x399dd,*([0]*12));value=struct.pack('<13I',0x3f23d,*([0]*12))
  expected.append((tag,value))
 assert newparts==expected,'Owen differs beyond two exact trait links';assert a[key][0]==b[key][0]and a[key][2]==b[key][2]
 assert all(a[k]==b[k]for k in a if k!=key),'Another subject/room/actor/outfit/header changed'
 s=dict(newparts);assert struct.unpack_from('<H',s[b'ACBS'],14)[0]==1 and s[b'EDID']==b'TLM_NPC_STUDY_Owen\0'
 stock=native_ordered({0x3f23d,0x1ed508,0x1ed507,0x128c59,0x19ee5d});npc=dict(stock[b'NPC_',0x3f23d]);assert npc[b'EDID']==b'AbrahamFinch\0';assert not struct.unpack_from('<H',npc[b'ACBS'],14)[0]&1;assert not struct.unpack_from('<I',npc[b'ACBS'])[0]&1;assert struct.unpack('<I',npc[b'RNAM'])[0]==0x13746
 parts=[struct.unpack('<I',v)[0]for k,v in stock[b'NPC_',0x3f23d]if k==b'PNAM'];assert len(parts)==11 and {0x1ed508,0x1ed507}<=set(parts)
 assert struct.unpack('<I',npc[b'FTST'])[0]==0x128c59 and struct.unpack('<I',npc[b'HCLF'])[0]==0x19ee5d
 assert dict(stock[b'TXST',0x128c59])[b'EDID']==b'SkinHeadOldMale\0';assert dict(stock[b'CLFM',0x19ee5d])[b'EDID']==b'HairColor10SteelGray\0'
 for k,name in [(0x1ed508,b'BigBeard16\0'),(0x1ed507,b'BigBeard16_Hairline\0')]:assert dict(stock[b'HDPT',k])[b'EDID']==name
 assets=json.loads((ROOT/'facegen-metadata.json').read_text(encoding='utf-8'));textures=json.loads((ROOT/'texture-metadata.json').read_text(encoding='utf-8'));assert len(assets['entries'])==11 and len(textures['entries'])==86 and textures['missing']==[]
 face='meshes/actors/character/facegendata/facegeom/fallout4.esm/0003f23d.nif';assert face in{e['path']for e in assets['entries']}
 for suffix in('_d.dds','_msn.dds','_s.dds'):assert 'textures/actors/character/facecustomization/fallout4.esm/0003f23d'+suffix in{e['path']for e in textures['entries']}
 return {'status':'PASS','records':121,'onlyChangedNpc':'02000818:TLMNpcPresentation.esp','onlyChangedFields':['TPLT','TPTA[first]'],'all120OtherRecordsExact':True,'actualOldSkin':0x128c59,'actualFullBeard':0x1ed508,'matchingFaceGeomAndTextures':True,'customCaricatureSculpt':False,'native':None}
def run():
 assert source_errors()==[],source_errors();r=json.loads((ROOT/'owen-source-receipt.json').read_text(encoding='utf-8'));path=ROOT/'build/owen-face-001/TLMNpcPresentation.esp';old=REPO.parent/'npc-presentation-007/tools/NpcPresentation/build/photo-001/TLMNpcPresentation.esp';assert prior.sha(path)==r['measuredPluginSha256'];assert prior.sha(ROOT/'build/owen-face-001/audition-receipt.json')==r['measuredBuildReceiptSha256'];assert prior.sha(old)=='031F5CB0E88971D7E84ACFA9573FF32ECB7F852AE50126D81DE3DCD831D7AD72';return artifact(path.read_bytes(),old.read_bytes())
if __name__=='__main__':print(json.dumps(run(),indent=2))
