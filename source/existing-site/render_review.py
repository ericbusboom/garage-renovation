from pathlib import Path
import json,math,html
import numpy as np
from PIL import Image,ImageDraw,ImageFont
from reportlab.pdfgen import canvas
R=Path(__file__).resolve().parent
parts=json.loads((R/'site-scene.json').read_text())['parts']
fontpath='/System/Library/Fonts/Helvetica.ttc'
def render(name,az,el,omit,top=False):
 w,h=1500,1700
 center=np.array([-1,-5,1.0]);right=np.array([math.cos(az),-math.sin(az),0]);up=np.array([math.sin(az)*math.sin(el),math.cos(az)*math.sin(el),math.cos(el)]);depth=np.cross(right,up)*-1
 # Match the viewer: increasing depth points away from camera.
 depth=np.array([math.sin(az)*math.cos(el),math.cos(az)*math.cos(el),-math.sin(el)])
 scale=39 if top else 41
 pix=np.empty((h,w,3),dtype=np.uint8);pix[:]=[247,247,242];zbuf=np.full((h,w),np.inf,dtype=np.float32)
 for p in parts:
  if p['group'] in omit:continue
  v=np.array(p['vertices']);q=v-center;screen=np.stack([w/2+q@right*scale,800-q@up*scale,q@depth],axis=1)
  for ids in p['triangles']:
   a,b,c=screen[ids];den=(b[1]-c[1])*(a[0]-c[0])+(c[0]-b[0])*(a[1]-c[1])
   if abs(den)<1e-8:continue
   x0=max(0,int(min(a[0],b[0],c[0])));x1=min(w-1,int(max(a[0],b[0],c[0]))+1);y0=max(0,int(min(a[1],b[1],c[1])));y1=min(h-1,int(max(a[1],b[1],c[1]))+1)
   if x0>x1 or y0>y1:continue
   xx,yy=np.meshgrid(np.arange(x0,x1+1)+.5,np.arange(y0,y1+1)+.5)
   u=((b[1]-c[1])*(xx-c[0])+(c[0]-b[0])*(yy-c[1]))/den;vv=((c[1]-a[1])*(xx-c[0])+(a[0]-c[0])*(yy-c[1]))/den;tt=1-u-vv;z=u*a[2]+vv*b[2]+tt*c[2]
   view=zbuf[y0:y1+1,x0:x1+1];mask=(u>=-1e-6)&(vv>=-1e-6)&(tt>=-1e-6)&(z<view);view[mask]=z[mask]
   t=v[ids];n=np.cross(t[1]-t[0],t[2]-t[0]);ln=np.linalg.norm(n);lum=.73+.27*abs(n@np.array([.3,-.4,.85]))/max(ln,1e-10)
   pix[y0:y1+1,x0:x1+1][mask]=np.array(p['color'])*255*lum
 image=Image.fromarray(pix);d=ImageDraw.Draw(image);F=lambda s:ImageFont.truetype(fontpath,s)
 d.text((85,55),'BACKYARD / EXISTING CONDITIONS',font=F(35),fill='#293b3d');d.text((85,106),'01  /  '+('SITE PLAN — CANOPIES OMITTED FOR CLARITY' if top else 'PHOTO-INFORMED 3D MASSING'),font=F(19),fill='#677575')
 d.text((85,1550),'Garage geometry from existing measured model. Yard layout and heights are estimated.',font=F(21),fill='#435655')
 d.text((85,1587),'Current garage + work shelter + Airstream + flagstone + planting + rear house context',font=F(19),fill='#677575')
 if top:
  labels=[('EXISTING GARAGE',(3,3)),('WORK SHELTER',(-2.3,5.3)),('AIRSTREAM',(-7,1.3)),('WORK PATIO',(-4,6.4)),('JUNGLE / WOOD CHIPS',(.45,-4.1)),('LOW SOUTH GARDEN',(.65,-10.4)),('DIVIDING FENCE',(.1,-7.15)),('REAR PATIO',(-5,-12)),('CONVERSATION AREA',(-5.4,-3.2)),('FIRE PIT',(-5.25,-4.75)),('HOUSE / CONTEXT',(-1,-18.3)),('WHITE PERGOLA',(3.5,-2.5)),('TRIANGULAR BAY',(-.9,-14.7))]
  for label,(x,y) in labels:
   u,v=w/2+(x+1)*scale,800-(y+5)*scale;bb=d.textbbox((0,0),label,font=F(16));tw=bb[2];d.rectangle((u-tw/2-8,v-12,u+tw/2+8,v+15),fill='#f7f7f2');d.text((u-tw/2,v-9),label,font=F(16),fill='#273d3c')
  d.text((1230,240),'N',font=F(26),fill='#293b3d');d.line((1240,238,1240,195),fill='#293b3d',width=3);d.polygon([(1240,187),(1234,199),(1246,199)],fill='#293b3d');d.line((1110,1380,1305,1380),fill='#293b3d',width=4);d.text((1150,1395),'5 m (estimated)',font=F(17),fill='#293b3d')
 image.save(R/(name+'.png'))
render('site-overview',.5,.90,{'canopy','pergola_foliage'})
render('house-and-pergola',3.55,.85,{'canopy','pergola_foliage'})
render('site-with-trees',.5,.90,set())
render('site-plan',0,math.pi/2,{'canopy','pergola_foliage'},True)
# Printable review sheet contains a plan and two views, all from identical geometry.
c=canvas.Canvas(str(R/'site-review.pdf'),pagesize=(750,850))
for name in ['site-plan','site-overview','house-and-pergola','site-with-trees']:
 c.drawImage(str(R/(name+'.png')),0,0,width=750,height=850);c.showPage()
c.save()
print('Rendered plan, two axonometrics, four-page review PDF')
