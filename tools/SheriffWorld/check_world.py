"""Strict six-anchor world composition readback. No build/native operations."""
from pathlib import Path
import raw as v
from vmad import vmad
import struct,json,hashlib
Q=Path(__file__).resolve().parent;R=Q.parents[3];BASE=R/'work/greenwater-composed-world-001/tools/GreenwaterRiver/build/composed-001/TLMWorldSlice.esp';OUT=Q/'build/composed-001/TLMWorldSlice.esp'
SITES={'HelpApproach':(1900,1664),'HelpWithdrawA':(1728,1152),'HelpWithdrawB':(1920,1152),'HelpWithdrawC':(2112,1152),'HelpWithdrawD':(1856,1408),'HelpHome':(3260,2530)}
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest().upper()
def blocks(row):
 result=[];current=None;core=[]
 for k,b in row['ordered']:
  if k==b'ALST':assert current is None;current=[(k,b)]
  elif current is not None:
   current.append((k,b))
   if k==b'ALED':result.append(current);current=None
  else:core.append((k,b))
 assert current is None
 return result,core
def named_aliases(row):
 bs,_=blocks(row);result={}
 for b in bs:
  t=dict(b);name=t[b'ALID'].rstrip(b'\0').decode();result[name]={'id':v.form(t[b'ALST']),'forced':v.form(t[b'ALFR'])}
 return result
def objects(raw):
 n=struct.unpack_from('<I',raw)[0];assert len(raw)==4+8*n
 return [struct.unpack_from('<HhI',raw,4+8*i)for i in range(n)]
def check(rows):
 inputs=json.loads((Q/'inputs.json').read_text());assert inputs['accepted'],'Current coherent master review pending'
 assert sha(R/inputs['review'])==inputs['reviewSha256'],'Accepted master review hash'
 masterPath=R/inputs['master'];assert sha(masterPath)==inputs['masterSha256'],'Master input hash';master,mn=v.records(masterPath);old,on=v.records(BASE);assert sha(BASE)=='A942AC8726D866091DCF17E1130488B322D1493CB0B45CC353D47F6E30D273B6'
 names={r['name']:r for r in rows.values()};extra=set(rows)-set(old);assert len(extra)==6 and {rows[i]['name']for i in extra}=={'TLM_WS_ST_'+s for s in SITES},'Exactly six appended anchors'
 for i,r in old.items():
  n=rows[i];assert r['parents']==n['parents']and r['flags']==n['flags'],'Old identity/flags/parent'
  if r['name']=='TLM_WS_A1':assert r['header'][:4]+r['header'][8:]==n['header'][:4]+n['header'][8:],'A1 non-size header changed';continue
  assert r['header']==n['header'],'Old header changed'
  assert [(k,b)for k,b in r['ordered']if not(i==0 and k==b'HEDR')]==[(k,b)for k,b in n['ordered']if not(i==0 and k==b'HEDR')],'Old payload changed: '+r['name']
 oldq=on['TLM_WS_A1'];newq=names['TLM_WS_A1'];ba,ca=blocks(oldq);bb,cb=blocks(newq);assert len(ba)==29 and len(bb)==35 and bb[:29]==ba,'Original29 alias prefix changed'
 assert [(k,b)for k,b in ca if k not in{b'VMAD',b'ANAM'}]==[(k,b)for k,b in cb if k not in{b'VMAD',b'ANAM'}],'A1 non-alias metadata changed'
 amap=named_aliases(newq);assert [dict(b)[b'ALID'].rstrip(b'\0').decode()for b in bb[29:]]==list(SITES),'Six alias order'
 assert v.form(oldq['tags'][b'ANAM'])==36 and v.form(newq['tags'][b'ANAM'])==42==max(a['id']for a in amap.values())+1,'Next alias ID differs'
 land=next(r for r in old.values()if r['type']=='LAND'and any(label==on['TLM_WS_Clearing']['id']for kind,label in r['parents']));h=v.decode(land);heights=[]
 for name,(x,y)in SITES.items():
  marker=names['TLM_WS_ST_'+name];orig=mn['TLM_REF_A1_'+name];p=v.pose(marker);g1,g2=v.ground(h,x,y),v.ground(h,x,y,True);assert p[:2]==[x,y]and abs(p[2]-max(g1,g2)-16)<.0001 and p[3:]==v.pose(orig)[3:],'Anchor not actual upper LAND+16'
  assert marker['type']=='REFR'and marker['flags']==0xc00 and set(marker['tags'])=={b'EDID',b'NAME',b'DATA'},'Anchor gained behavior/visibility'
  assert marker['parents']==on['TLM_WS_ST_Marshal']['parents']and v.form(marker['tags'][b'NAME'])==v.form(orig['tags'][b'NAME'])==0x3b,'Anchor parent/base changed'
  assert amap[name]['forced']==marker['id'],'Alias not bound to exact new anchor';heights.append({'name':name,'position':p[:3],'firstTriangle':g1,'secondTriangle':g2,'sourceYawPreserved':p[5]})
 oh,os,ot=vmad(oldq['tags'][b'VMAD']);nh,ns,nt=vmad(newq['tags'][b'VMAD']);assert oh==nh and ot==nt and len(os)==len(ns)==1,'Old VMAD header/scripts/tail changed'
 oldname,oldstatus,op=os[0];newname,newstatus,np=ns[0];assert (oldname,oldstatus)==(newname,newstatus)
 oldprops={p[0].decode():p for p in op};newprops={p[0].decode():p for p in np};added={'HelpCast','HelpAnchors','SaySheriffWarning','RecordedSheriffWarning'};assert set(newprops)-set(oldprops)==added and set(oldprops)<=set(newprops),'Unexpected property union'
 for name,p in oldprops.items():
  n=newprops[name];assert p[:3]==n[:3],'Old property type/flags'
  if name=='Everything':assert objects(n[3])==objects(p[3])+[(0,amap[s]['id'],newq['id'])for s in SITES],'Everything order/objects'
  elif name=='EverythingNames':assert n[3]==struct.pack('<I',struct.unpack_from('<I',p[3])[0]+6)+p[3][4:]+b''.join(struct.pack('<H',len(s))+s.encode()for s in SITES),'EverythingNames changed beyond append'
  else:assert p==n,'Old property changed: '+name
 assert [p[0]for p in np if p[0].decode()not in added]==[p[0]for p in op],'Old property order'
 assert objects(newprops['HelpCast'][3])==[(0,amap[s]['id'],newq['id'])for s in ['Pritchard','Dunmore','Cutter1','Cutter2','Cutter3','Nell','Abel']],'HelpCast not original seven'
 assert objects(newprops['HelpAnchors'][3])==[(0,amap[s]['id'],newq['id'])for s in SITES],'HelpAnchors order/binding'
 mh,ms,mt=vmad(mn['TLM_A1']['tags'][b'VMAD']);mp={p[0].decode():p for script,status,props in ms for p in props}
 targets={}
 for name,kind in [('SaySheriffWarning','MESG'),('RecordedSheriffWarning','SNDR')]:
  assert newprops[name]==mp[name],'Current master warning pointer changed';pad,alias,fid=struct.unpack('<HhI',newprops[name][3]);assert pad==0 and alias==-1 and master[fid]['type']==kind,'Warning pointer wrong type';targets[name]={'form':hex(fid),'editorID':master[fid]['name']}
 return {'oldRecordsRetained':len(old),'newAnchors':heights,'oldAliasPrefix':29,'currentAliases':35,'currentWarningTargets':targets,'oldNPCPosesLiteral':sum(r['type']=='ACHR'for r in old.values()),'allOldTerrainWaterSceneryLiteral':True,'native':'OPEN: staged actor relocation/terrain collision/voice; source composition only. No new inspection marker/package.'}
if __name__=='__main__':
 rows,_=v.records(OUT);print(json.dumps(check(rows),indent=2))
