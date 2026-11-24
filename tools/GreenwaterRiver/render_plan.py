"""Original numerical engineering source plan, not native imagery."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import raw as v,json
rows,names=v.records(v.OUT/'TLMWorldSlice.esp');cell=names['TLM_GWR_Cell'];land=next(r for r in rows.values()if r['type']=='LAND'and any(label==cell['id']for kind,label in r['parents']));h=v.decode(land);scene=json.loads((v.OUT/'greenwater-river.json').read_text())
im=Image.new('RGB',(1800,1100),'#f3f0e8');d=ImageDraw.Draw(im);font=lambda n:ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',n)
d.text((50,24),'GREENWATER - SOURCE PLAN, NOT A GAME SCREENSHOT',font=font(34),fill='#202a22')
for panel,bounds in [((50,130,810,890),(0,-4096,4096,0)),((900,220,1750,750),(1240,-2670,3870,-1470))]:
 left,top,right,bottom=panel;x0,y0,x1,y1=bounds
 def point(x,y):return (left+(x-x0)/(x1-x0)*(right-left),bottom-(y-y0)/(y1-y0)*(bottom-top))
 def rect(xa,ya,xb,yb,color,outline=None):
  a,b=point(xa,yb),point(xb,ya)
  if b[0]<left or a[0]>right or b[1]<top or a[1]>bottom:return
  d.rectangle((max(left,a[0]),max(top,a[1]),min(right,b[0]),min(bottom,b[1])),fill=color,outline=outline)
 for y in range(32):
  for x in range(32):
   z=sum([h[y][x],h[y][x+1],h[y+1][x],h[y+1][x+1]])/4;color='#477e9a'if z< -64 else '#c4b68e'if z<0 else '#a2af7e'if z<128 else '#6e855e'if z<256 else '#475f47';rect(x*128,y*128-4096,(x+1)*128,(y+1)*128-4096,color)
 for p in scene['props']:
  if p['asset']=='workshop_ShackMidFloor01B':rect(p['x']-128,p['y']-128,p['x']+128,p['y']+128,'#ae855a','#775538')
 for i,p in enumerate(scene['buttons'],1):
  x,y=point(p['x'],p['y'])
  if left<x<right and top<y<bottom:d.ellipse((x-7,y-7,x+7,y+7),fill='#f6d44b',outline='#332d16');d.text((x+9,y-12),str(i),font=font(18),fill='#1c221b')
 d.rectangle(panel,outline='#25382c',width=2)
d.text((50,93),'Whole new cell: actual decoded terrain / submerged bed',font=font(23),fill='#263328');d.text((900,175),'Landing / Queen / supported far-bank walk',font=font(23),fill='#263328')
for i,p in enumerate(scene['buttons']):d.text((900+(i%2)*395,790+(i//2)*29),str(i+1)+'. '+p['alias'],font=font(23),fill='#263328')
d.text((50,930),'Blue: submerged terrain. Brown: stock floor positions.',font=font(24),fill='#263328');d.text((50,972),'Yellow: working activators; original numerical source data.',font=font(24),fill='#263328');d.text((50,1020),'Native rendering, collision and walking remain OPEN.',font=font(26),fill='#263328')
out=Path(__file__).resolve().parents[4]/'output/greenwater-source-plan-001.png';out.parent.mkdir(parents=True,exist_ok=True);im.save(out);print(out)
