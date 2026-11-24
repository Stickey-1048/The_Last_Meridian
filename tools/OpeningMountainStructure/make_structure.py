"""Three original ridge-cell sculpt + explicit passive poses; never game control."""
from pathlib import Path
import sys,json,struct,math,copy
R=Path(__file__).resolve().parents[2];HERE=Path(__file__).resolve().parent;sys.path.insert(0,str(R/'tools/SheriffWorld'))
from raw import records,decode,ground,pose,form,box
BASE=R.parent/'opening-production-finish-001/tools/OpeningProductionFinish/build/finish-002/TLMWorldSlice.esp';rows,names=records(BASE)
PATCH={(1,0),(0,1),(1,1)};cells={struct.unpack_from('<ii',r['tags'][b'XCLC']):r for r in rows.values()if r['type']=='CELL'and b'XCLC'in r['tags']};lands={xy:next(r for r in rows.values()if r['type']=='LAND'and(6,c['id'])in r['parents'])for xy,c in cells.items()};grids={xy:decode(r)for xy,r in lands.items()};oldH={};anchors={};oldW={}
for (cx,cy),h in grids.items():
 for y in range(33):
  for x in range(33):
   key=(cx*32+x,cy*32+y);oldH.setdefault(key,h[y][x])
   if(cx,cy)not in PATCH:anchors.setdefault(key,list(struct.unpack_from('<3b',lands[cx,cy]['tags'][b'VNML'],(y*33+x)*3)))
for (cx,cy),land in lands.items():
 last=None
 for k,v in land['ordered']:
  if k==b'ATXT':last=struct.unpack('<IBBH',v)
  if k==b'VTXT':
   tex,q,_,_=last
   for i in range(289):oldW.setdefault((cx*32+(q&1)*16+i%17,cy*32+(q>>1)*16+i//17),{})[tex]=struct.unpack_from('<f',v,i*8+4)[0]
def smooth(x):x=max(0,min(1,x));return x*x*(3-2*x)
def target(x,y):
 east=2100*math.exp(-((x-6850)/1050)**2-((y-5600)/1450)**2)
 north=2200*math.exp(-((x-3000)/1350)**2-((y-7000)/850)**2)
 shoulderE=950*math.exp(-((x-4940-180*math.sin(y/620))/750)**2)*(.6+.4*math.sin(y/970+.5)**2)
 shoulderN=1100*math.exp(-((y-5120-260*math.sin(x/1150))/820)**2)*(.65+.35*math.cos(x/850)**2)
 spur=500*math.exp(-((x-5250)/1050)**2-((y-6500)/900)**2)
 return max(east,north,shoulderE,shoulderN,spur)+80*math.sin(x/340+y/510)*math.sin(y/620)
def H(gx,gy):
 old=oldH.get((gx,gy),0);x,y=gx*128,gy*128
 if not any(cx*32<=gx<=cx*32+32 and cy*32<=gy<=cy*32+32 for cx,cy in PATCH):return old
 d=math.hypot(max(0,x-4096),max(0,y-4096));edge=min(x,y,8192-x,8192-y,d);blend=smooth((edge-128)/512)
 return round((old+(target(x,y)-old)*blend)/8)*8
def normal(gx,gy):
 if(gx,gy)in anchors:return anchors[gx,gy]
 dx=(H(gx+1,gy)-H(gx-1,gy))/256;dy=(H(gx,gy+1)-H(gx,gy-1))/256;n=math.sqrt(1+dx*dx+dy*dy)
 return[round(-dx/n*127),round(-dy/n*127),round(1/n*127)]
newGrids={xy:[[H(xy[0]*32+x,xy[1]*32+y)for x in range(33)]for y in range(33)]for xy in PATCH}
def surface(x,y,upper=False):
 cx,cy=math.floor(x/4096),math.floor(y/4096);h=newGrids.get((cx,cy),grids[cx,cy]);a=ground(h,x-cx*4096,y-cy*4096,False);b=ground(h,x-cx*4096,y-cy*4096,True);return max(a,b)if upper else min(a,b)
def weight(gx,gy):
 if(gx,gy)in anchors:return[oldW[gx,gy].get(t,0)for t in(0x3343c,0x21336,0xc55fc)]
 x,y=gx*128,gy*128;dx=(H(gx+1,gy)-H(gx-1,gy))/256;dy=(H(gx,gy+1)-H(gx,gy-1))/256;slope=math.hypot(dx,dy);rock=min(.65,max(0,(slope-.55)*.6));gravel=.025;forest=(1-rock-gravel)*(.86+.08*math.sin(x/450+y/620));return[forest,gravel,rock]
models=json.loads((R/'tools/AppalachianRidges/models.json').read_text())['assets'];byid={int(a['id'],16):n for n,a in models.items()};moved=[];added=[]
clusters={(1,0):(5000,2600),(0,1):(3000,5000),(1,1):(6500,5600)}
offsets=[(-260,-160),(80,120),(-90,260),(280,-100),(-320,160),(180,320),(-180,-340),(320,80),(-40,420),(390,-240)]
def place(asset,x,y,yaw,scale,cell):
 a=models[asset]['nif'];fb=[v*scale for v in a['bottomBandBounds']];rb=[v*scale for v in a['renderBounds']];best=None
 for dx in(0,-64,64,-128,128,-256,256,-512,512):
  for dy in(0,-64,64,-128,128,-256,256,-512,512):
   xx,yy=x+dx,y+dy;bounds=box(rb,[xx,yy,0],[0,0,yaw]);cx,cy=cell
   if bounds[0]<cx*4096+64 or bounds[3]>(cx+1)*4096-64 or bounds[1]<cy*4096+64 or bounds[4]>(cy+1)*4096-64:continue
   lo=1e9;hi=-1e9;c,s=math.cos(yaw),math.sin(yaw)
   for i in range(9):
    for j in range(9):
     fx=fb[0]+(fb[3]-fb[0])*i/8;fy=fb[1]+(fb[4]-fb[1])*j/8;lo=min(lo,surface(xx+fx*c+fy*s,yy+fy*c-fx*s));hi=max(hi,surface(xx+fx*c+fy*s,yy+fy*c-fx*s,True))
   if hi-lo>56:continue
   score=math.hypot(dx,dy)+2*(hi-lo)
   if best is None or score<best[0]:best=(score,xx,yy,lo-fb[5]-3,lo,hi)
 assert best is not None,(asset,cell,x,y)
 return best[1:]
for xy in sorted(PATCH):
 c=cells[xy];refs=[r for r in rows.values()if r['type']=='REFR'and(6,c['id'])in r['parents']];ti=0;large=0
 for r in refs:
  asset=byid[form(r['tags'][b'NAME'])];p=pose(r);scale=struct.unpack('<f',r['tags'][b'XSCL'])[0];x,y=p[:2]
  if asset.startswith('Tree'):
   ox,oy=offsets[ti];ti+=1;x,y=clusters[xy][0]+ox,clusters[xy][1]+oy
   if asset=='TreeMaplePreWar03Gr':
    ox,oy=[(-100,0),(100,160),(-220,160),(260,80)][large];large+=1;x,y=clusters[xy][0]+ox,clusters[xy][1]+oy
  xx,yy,z,lo,hi=place(asset,x,y,p[5],scale,xy)
  moved.append({'id':r['name'],'localId':r['id']&0xffffff,'asset':asset,'oldXYZ':p[:3],'x':xx,'y':yy,'z':z,'yaw':p[5],'scale':scale,'grid':list(xy),'groundRange':[lo,hi]})
# Six bounded outcrops reuse measured native models. No additional trees needed:
# thirty existing ridge trees are deliberately clustered on visible shoulders.
for i,(xy,x,y,scale)in enumerate([((1,0),4800,3300,2),((1,0),5200,1800,2.2),((0,1),2100,5100,2),((0,1),3550,5350,2.1),((1,1),6250,6100,2),((1,1),7000,5600,2.2)]):
 yaw=i*.71;asset='RockBoulder03';xx,yy,z,lo,hi=place(asset,x,y,yaw,scale,xy);added.append({'id':'TLM_STRUCTURE_Outcrop'+str(i),'asset':asset,'x':xx,'y':yy,'z':z,'yaw':yaw,'scale':scale,'grid':list(xy),'groundRange':[lo,hi]})
cellsOut=[{'grid':list(xy),'localId':lands[xy]['id']&0xffffff,'heights':newGrids[xy],'normals':[[normal(xy[0]*32+x,xy[1]*32+y)for x in range(33)]for y in range(33)],'weights':[[weight(xy[0]*32+x,xy[1]*32+y)for x in range(33)]for y in range(33)]}for xy in sorted(PATCH)]
def rays(fields):
 result=[]
 for name,x,y,z in[('dispatch',740,920,-46),('sheriff',3212,2474,264),('midroute',2600,2200,184)]:
  angles=[]
  for deg in(0,15,30,39,45,55,65,75,90):
   maximum=(-90,0,0,0)
   for d in range(256,12000,32):
    xx,yy=x+math.cos(math.radians(deg))*d,y+math.sin(math.radians(deg))*d;xy=(math.floor(xx/4096),math.floor(yy/4096))
    if xy not in grids:break
    h=fields.get(xy,grids[xy]);hh=ground(h,xx-xy[0]*4096,yy-xy[1]*4096);a=math.degrees(math.atan2(hh-z,d))
    if a>maximum[0]:maximum=(a,d,hh,xy)
   angles.append({'bearingDegrees':deg,'maximumAngle':maximum[0],'distance':maximum[1],'height':maximum[2],'cell':maximum[3]})
  result.append({'view':name,'eyeXYZ':[x,y,z],'rays':angles})
 return result
data={'scope':'Only three original outer ridge cells; core physical data unchanged','cells':cellsOut,'moved':moved,'added':added,'sourceRays':rays({}),'sculptedRays':rays(newGrids)}
(HERE/'sculpt.json').write_text(json.dumps(data,indent=2)+'\n');(HERE/'models.json').write_text(json.dumps({'assets':models},indent=2)+'\n');print('cells',len(cellsOut),'explicit moves',len(moved),'new outcrops',len(added));print([(q['view'],[(v['bearingDegrees'],round(v['maximumAngle'],1))for v in q['rays']])for q in data['sculptedRays']])
