from pathlib import Path
import sys, json, html, math
from PIL import Image, ImageDraw, ImageFont
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor
O=Path(__file__).resolve().parent
W,H=1600,1730
im=Image.new('RGB',(W*2,H*2),'white'); d=ImageDraw.Draw(im)
pdf=canvas.Canvas(str(O/'east-wall-study.pdf'),pagesize=(W,H))
svg=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}"><rect width="100%" height="100%" fill="white"/>']
ink='#233742'; muted='#657680'; old='#a9b0b3'; light='#f0f2f3'; blue='#246b91'; orange='#b56c2c'
font='/System/Library/Fonts/Supplemental/Arial.ttf'
def line(x,y,a,b,c=ink,w=1,dash=False):
 svg.append(f'<line x1="{x}" y1="{y}" x2="{a}" y2="{b}" stroke="{c}" stroke-width="{w}"'+(' stroke-dasharray="7 5"' if dash else '')+'/>')
 pdf.setStrokeColor(HexColor(c));pdf.setLineWidth(w);pdf.setDash([7,5] if dash else []);pdf.line(x,H-y,a,H-b)
 dist=math.hypot(a-x,b-y)
 if dash and dist:
  for k in range(0,int(dist),12):
   t=k/dist;u=min(k+7,dist)/dist;d.line((2*(x+(a-x)*t),2*(y+(b-y)*t),2*(x+(a-x)*u),2*(y+(b-y)*u)),fill=c,width=max(1,int(2*w)))
 else:d.line((2*x,2*y,2*a,2*b),fill=c,width=max(1,int(2*w)))
def rect(x,y,w,h,fill=None,c=ink,lw=1,dash=False):
 if fill:
  svg.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{fill}"/>');pdf.setFillColor(HexColor(fill));pdf.rect(x,H-y-h,w,h,stroke=0,fill=1);d.rectangle((x*2,y*2,(x+w)*2,(y+h)*2),fill=fill)
 for a,b,e,f in [(x,y,x+w,y),(x+w,y,x+w,y+h),(x+w,y+h,x,y+h),(x,y+h,x,y)]:line(a,b,e,f,c,lw,dash)
def text(x,y,s,size=16,c=ink):
 svg.append(f'<text x="{x}" y="{y}" fill="{c}" font-family="Arial, sans-serif" font-size="{size}">{html.escape(s)}</text>')
 pdf.setFillColor(HexColor(c));pdf.setFont('Helvetica',size);pdf.drawString(x,H-y,s);d.text((x*2,y*2),s,font=ImageFont.truetype(font,size*2),fill=c,anchor='ls')
def dim(x,a,y,label):
 line(x,y,a,y,muted)
 for q in (x,a):line(q-4,y+5,q+4,y-5,muted)
 text((x+a)/2-len(label)*3.6,y-9,label,14,muted)
def note(x,y,rows,c=muted,size=16):
 for i,s in enumerate(rows):text(x,y+i*23,s,size,c)
text(55,57,'EAST WALL STUDY',32)
text(55,89,'04 / Posts clear of the entire 12 in. setback     |     East elevation: looking west; south at left, north at right',18)
text(55,117,'September 15, 2026  •  Concept comparison only  •  No structural capacity or permit compliance established',15,muted)
line(55,137,1545,137,ink,1.5)
S=2.6;x=145;length=249*S;wh=98.5*S
for idx,base in enumerate([530,1005]):
 top=base-wh
 text(55,177 if idx==0 else 652,('A / POSTS AT SOUTH AND NORTH ENDS' if idx==0 else 'B / END POSTS + INSERTED MID-WALL POST'),23,blue)
 text(55,202 if idx==0 else 677,('Existing wall retained; beam or truss spans between new end supports.' if idx==0 else 'Center post concealed within the wall; local cutout plastered flush after installation.'),16,muted)
 rect(x,top,length,wh,light,old)
 for st in range(16,249,16):line(x+st*S,top+8,x+st*S,base-6,'#d0d5d8',1,True)
 # deliberately schematic beam depth / gap, not a sized structural member
 rect(x-4*S,top-35,length+8*S,25,'#e4eff5',blue,2)
 for st,tag in [(-4,'E-S'),(249,'E-N')]+([(122.5,'E-M')] if idx else []):
  xx=x+st*S
  if tag=='E-M':rect(xx-13,top,4*S+26,wh,'#fff1e4',orange,1,True)
  rect(xx,top-10,4*S,wh+10,None if tag=='E-M' else '#d2e7f1',blue,2,tag=='E-M')
  line(xx+2*S,base,xx+2*S,base+27,blue,2)
  rect(xx-18,base+27,4*S+36,36,None,blue,1.5,True)
  text(xx-9,base+87,tag,14,blue)
 line(x-30,base,x+length+30,base,ink,1.5)
 text(x+(25 if idx else 95),top+85,('EXISTING WALL' if idx else 'EXISTING EAST WALL RETAINED'),17 if idx else 19,muted)
 text(x+(25 if idx else 95),top+112,('6 in.; approx. 16 in. o.c.' if idx else '6 in. wall; studs approx. 16 in. o.c.'),15 if idx else 16,muted)
 text(x+(25 if idx else 95),top+137,('Studs diagrammatic.' if idx else 'Studs diagrammatic; no east openings in source plan.'),14,muted)
 dim(x,x+length,top-51,'20 ft 9 in. existing wall')
 if idx:dim(x-2*S,x+124.5*S,base+18,'10 ft 6 1/2 in. c/c');dim(x+124.5*S,x+251*S,base+18,'10 ft 6 1/2 in. c/c')
 else:dim(x-2*S,x+251*S,base+18,'21 ft 1 in. post c/c - assumed end placement')
 line(110,top,110,base,muted)
 for yy in (top,base):line(106,yy+4,114,yy-4,muted)
 text(58,top+80,'8 ft',14,muted);text(58,top+101,'2 1/2 in.',14,muted);text(58,top+124,'ref.',13,muted)
 
 if idx:text(x-8,base+111,'SOUTH',14);text(x+length-50,base+111,'NORTH',14)
 nx=900;ny=top-11
 if idx==0:
  note(nx,ny,['NEW FRAME / blue'],blue,19)
  note(nx,ny+32,['4 in. post envelope requested; section not selected.', 'End posts beyond south / north ends; east faces flush.', 'Beam/truss depth and elevation are schematic.', 'No new building load assigned to existing wall.'])
  note(nx,ny+150,['FOUNDATION / dashed boxes'],blue,19)
  note(nx,ny+181,['New supports require a verified foundation solution.', 'Boxes locate support points only; dimensions unresolved.', 'Existing slab is cracked; footing condition is unknown.'])
  note(nx,ny+270,['DISRUPTION / concept tradeoff'],ink,19)
  note(nx,ny+301,['Two support locations and no central wall opening.', 'Longer beam span; cost and lifting access remain unpriced.'])
 else:
  note(nx,ny,['INTERMEDIATE SUPPORT / E-M'],blue,19)
  note(nx,ny+32,['4 in. post WITHIN the existing 6 in. wall; see detail below.', 'Blue dashed = concealed post behind restored plaster.', 'Orange zone = local cutout, then plastered back flush.', 'Beam connection and foundation remain unresolved.'])
  note(nx,ny+150,['LOAD PATH / to be engineered'],blue,19)
  note(nx,ny+181,['Shorter spans, plus a third foundation and connection.', 'No existing-wall bearing credit is assumed in this sketch.', 'Gravity posts alone do not establish lateral resistance.'])
  note(nx,ny+270,['HARDY FRAME / alternate to develop'],ink,19)
  note(nx,ny+301,['A proprietary panel needs its own width, anchorage and', 'foundation layout; it is not represented by the 4 in. post.'])
line(55,1145,1545,1145,ink,1)
text(55,1180,'END POSTS — SETBACK KEPT CLEAR',21)
# inset x scaled relative to upper edge at 213.5; y symbolic
xx=100;sc=5
for val,label,c in [(213.5,'Upper steel edge',blue),(261.5,'Property line',orange)]:
 a=xx+(val-213.5)*sc;line(a,1230,a,1350,c,1.5,True);text(a-40,1374,label,13,c)
wx=xx+36*sc
rect(wx-6*sc,1260,6*sc,60,light,old)
rect(wx-4*sc,1240,4*sc,4*sc,'#d2e7f1',blue,2)
rect(wx-4*sc,1320,4*sc,4*sc,'#d2e7f1',blue,2)
line(wx,1230,wx,1350,ink,1,True)
dim(xx,wx,1220,'36 in.');dim(wx,xx+48*sc,1200,'12 in.')
text(380,1230,'VIEW FROM ABOVE / both wall ends',16,blue)
text(380,1255,'6 in. wall; length shortened in this detail',15,muted)
text(380,1284,'Full 12 in. strip to property line: NO POSTS',15,blue)
text(380,1313,'End posts shown beyond wall ends, east faces flush.',13,muted)
text(380,1342,'End placement assumed for study; center post shown below.',13,muted)
note(900,1182,['COORDINATION BEFORE CODE REVIEW'],ink,19)
note(900,1213,['The plan places the upper steel edge 36 in. inward of this wall.', 'Load transfer to this new support line has not been designed.', 'Confirm wall height, roof geometry, loads and soil / footings.', 'Entire one-foot setback strip remains clear of all posts.', 'Setback, fire separation and construction access remain to check.', 'Staging and temporary support must be planned before opening.'],size=15)

line(55,1400,1545,1400,ink,1)
text(55,1440,'CENTER POST — INSIDE WALL',21,blue)
text(55,1470,'VIEW FROM ABOVE / E-M only; post concealed within existing wall.',15,muted)
# Six-inch wall runs north-south horizontally on this local detail.
rect(100,1530,600,90,light,old)
rect(340,1530,120,90,'#fff1e4',orange,1,True)
rect(370,1545,60,60,'#d2e7f1',blue,2)
line(100,1530,700,1530,ink,2)
line(100,1620,700,1620,ink,2)
text(100,1515,'GARAGE INTERIOR / WEST',14,muted)
text(100,1647,'EXTERIOR / EAST — 1 ft setback strip begins beyond this wall face',14,muted)
line(730,1530,730,1620,muted)
line(725,1530,735,1530,muted);line(725,1620,735,1620,muted)
text(745,1580,'6 in.',15,muted)
note(900,1498,['CONCEALED CENTER SUPPORT'],blue,19)
note(900,1532,['Cut out a local section of the existing wall.', 'Set the 4 in. post inside the wall thickness.', 'Reinstate the wall finish and plaster flush.', 'Post centering and cutout width shown schematically.', 'Finish buildup, beam connection and footing to be detailed.'],size=15)

text(55,1700,'Basis: floor-plan-setbacks revision 07 + model/parameters.json. Height from model; wall thickness / spacing from user. Roof profile omitted: unconfirmed.',13,muted)
svg.append('</svg>');(O/'east-wall-study.svg').write_text('\n'.join(svg));pdf.save();im.resize((W,H),Image.Resampling.LANCZOS).save(O/'east-wall-study.png')
