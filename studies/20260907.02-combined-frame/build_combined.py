from pathlib import Path
import json,math
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon,Rectangle
from matplotlib.backends.backend_pdf import PdfPages
from PIL import Image
R=Path(__file__).resolve().parent
# Reuse the tested deterministic software renderer, without running prior studies.
s={ '__file__':str(R.parent/'roof-studies/build_studies.py') }
exec((R.parent/'roof-studies/build_studies.py').read_text().split("with PdfPages(ROOT/")[0],s)
W=249.5;L=255;LG=249;H=98.5;B=106.5;F=107.25;YS=-23.25;YB=177;T=8
h,k,xhip,z=s['profiles']('A');P=[]
COL={'wall':'#c6d0d5','trim':'#ffffff','wood':'#bc966c','steel':'#647b85','roof':'#3b505f','glass':'#a9cdd9','shed':'#557f79'}
def poly(v,c,n):P.append(dict(vertices=[[float(q) for q in a] for a in v],color=c,name=n))
def box(x,y,z0,dx,dy,dz,c,n):
 v=[[x,y,z0],[x+dx,y,z0],[x+dx,y+dy,z0],[x,y+dy,z0],[x,y,z0+dz],[x+dx,y,z0+dz],[x+dx,y+dy,z0+dz],[x,y+dy,z0+dz]]
 for ids in [[0,3,2,1],[4,5,6,7],[0,1,5,4],[1,2,6,5],[2,3,7,6],[3,0,4,7]]:poly([v[i] for i in ids],c,n)
# Measured existing garage lower walls/openings, excluding its original roof.
for part in s['base']['parts']:
 if part['group'] not in ['existing','infill']:continue
 c=COL['glass'] if part['group']=='infill' and 'window' in part['name'].lower() else COL['wall']
 if part['group']=='infill' and 'door' in part['name'].lower():c=COL['trim']
 for tri in part['triangles']:poly([part['vertices'][i] for i in tri],c,part['name'])
box(0,0,H,W,2,8,COL['trim'],'South floor rim')
box(0,LG-2,H,W,8,8,COL['trim'],'North floor rim')
poly([(0,0,F),(W,0,F),(W,0,z(W,0)-8),(xhip(0),0,z(0,0)-8),(0,0,z(0,0)-8)],COL['wall'],'South upper infill')
# Continuous south solar roof, and steep eastern face.
main=[(0,YS,z(0,YS)),(W,YS,z(W,YS)),(xhip(YB),YB,z(0,YB)),(0,YB,z(0,YB))]
poly(main,COL['roof'],'Integrated solar field / matching infill')
poly([(W,YS,z(W,YS)),(W,L,z(W,L)),(W-36,L,z(0,L)),(xhip(YB),YB,z(0,YB))],COL['roof'],'Steep east roof')
# Module faces left flush with dark infill field; no standoffs, no cut active modules.
for yy in np.arange(YS+3,YB-24,30):
 for xx in np.arange(3,W-24,30):
  if xx+27>xhip(yy+27)-2:continue
  poly([(xx,yy,z(xx,yy)+.08),(xx+27,yy,z(xx+27,yy)+.08),(xx+27,yy+27,z(xx+27,yy+27)+.08),(xx,yy+27,z(xx,yy+27)+.08)],'#465d6d','Active PV module (illustrative)')
# Main roof white edge fascia, no raised sloping lattice.
poly([(0,YS,z(0,YS)),(0,YB,z(0,YB)),(0,YB,z(0,YB)-8),(0,YS,z(0,YS)-8)],COL['trim'],'Solar roof west fascia')
box(0,YS,B,W,1,8,COL['trim'],'South fascia')
# Rear cap: 16-in north/west projection, no extra east projection.
# Low hip ridge runs N-S to preserve the selected west silhouette.
x0=-16;x1=W-36;y0=YB-16;y1=L+16;ec=z(0,L)+2;peak=ec+8;xm=(x0+x1)/2;ra=y0+34;rb=y1-34
corners=[(x0,y0,ec),(x1,y0,ec),(x1,y1,ec),(x0,y1,ec)]
poly([corners[0],corners[1],(xm,ra,peak)],'#85949c','Hip south')
poly([corners[1],corners[2],(xm,rb,peak),(xm,ra,peak)],'#8e9ca3','Hip east')
poly([corners[2],corners[3],(xm,rb,peak)],'#82929a','Hip north')
poly([corners[3],corners[0],(xm,ra,peak),(xm,rb,peak)],'#91a0a6','Hip west')
for a,b in zip(corners,corners[1:]+corners[:1]):
 poly([a,b,(b[0],b[1],ec-8),(a[0],a[1],ec-8)],COL['trim'],'Hip cap fascia')
poly([(x0,y0,ec-8),(x1,y0,ec-8),(x1,y1,ec-8),(x0,y1,ec-8)],'#f1f1ed','Projecting soffit')
# Loft west enclosure with true rectangular openings.
# Door x in west elevation 9..69 => global y186..246; window94..124 => y131..161.
opens=[(186,246,F,F+80,'French doors'),(131,161,F+30,F+66,'West loft window')]
def top(yy):return (ec-8 if yy>=YB else z(0,yy)-T)
cuts=sorted(set([0,YB,L]+[q for o in opens for q in o[:2]]))
for a,b in zip(cuts,cuts[1:]):
 op=next((o for o in opens if o[0]<=a and b<=o[1]),None)
 if op:
  if op[2]>F:poly([(0,a,F),(0,b,F),(0,b,op[2]),(0,a,op[2])],COL['wall'],'West loft wall')
  poly([(0,a,op[3]),(0,b,op[3]),(0,b,top(b)),(0,a,top(a))],COL['wall'],'West loft wall')
  poly([(-.2,a,op[2]),(-.2,b,op[2]),(-.2,b,op[3]),(-.2,a,op[3])],COL['glass'],op[4])
  for yy in [a,b]:box(-.8,yy-1,op[2]-1,1,2,op[3]-op[2]+2,COL['trim'],'Opening trim')
  for zz in [op[2],op[3]]:box(-.8,a,zz-1,1,b-a,2,COL['trim'],'Opening trim')
  box(-.9,(a+b)/2-.5,op[2],1,1,op[3]-op[2],COL['trim'],'Opening mullion')
 else:poly([(0,a,F),(0,b,F),(0,b,top(b)),(0,a,top(a))],COL['wall'],'West loft wall')
poly([(0,L,F),(W,L,F),(W,L,z(W,L)-8),(W-36,L,ec-8),(0,L,ec-8)],COL['wall'],'North loft wall')
# North cap transition / east margin conceptual filler.
poly([(x1,YB,z(0,YB)),(x1,L,ec-8),(W,L,z(W,L)),(xhip(YB),YB,z(0,YB))],COL['roof'],'East transition infill')
# High-level room vent, separate from roof cavity.
box(-1,189,205,1,54,9,'#ffffff','Loft vent frame')
for zz in [207,209,211]:box(-1.2,191,zz,.3,50,.6,COL['steel'],'Loft vent slat')
# White walkway row and flat canopy, balcony over northernmost78in.
for yy in [-20,77,166,253]:box(-35,yy-3,0,6,6,H,COL['trim'],'White walkway post')
box(-35,YS,H,6,L-YS,8,COL['trim'],'White walkway beam')
for yy in np.arange(YS,YB,7):box(-35,yy,B-2,35,1.5,2,COL['trim'],'Horizontal walkway member')
box(-35,YB,B,35,L-YB,.75,COL['trim'],'Balcony floor / walkway roof')
for yy in np.arange(YB,L+.1,6):box(-35,yy-.5,F,1,1,42,COL['trim'],'Balcony baluster')
box(-35,YB,F+40,2,78,2,COL['trim'],'Balcony top rail')
for yy in [YB,L-1]:
 box(-35,yy,F+40,35,1,2,COL['trim'],'Balcony return rail')
# Existing outbuilding. Global y174..249; same approximate elevations accepted.
oy=LG-75;px=-174.25
box(-27,oy,0,27,2.5,96,COL['wood'],'Workbench south enclosure')
box(-27,LG-2.5,0,27,2.5,96,COL['wood'],'Workbench north enclosure')
box(-27,oy,35,27,75,2,COL['wood'],'Workbench top')
box(-27,oy,68,27,75,2,COL['wood'],'Workbench shelf')
box(px,oy,0,10,48,96,COL['wood'],'Electrical pillar')
for xx,yy in [(px,oy),(px,oy+45.5),(-27,oy),(-27,LG-2.5)]:box(xx,yy,0,2.5,2.5,96,COL['steel'],'Existing steel support')
box(px+10,oy,78,137.25,2.5,18,COL['wood'],'Existing connecting beam')
for zz in [78,93.5]:box(px+10,oy-.1,zz,137.25,2.5,2.5,COL['steel'],'Beam tube chord')
box(px-10,oy-10,97.25,184.25,95,.75,COL['shed'],'Existing corrugated plastic roof')
# Corrugation indicated with sparse line-like strips, spacing only illustrative.
for xx in np.arange(px-10,0,5):box(xx,oy-10,98,.3,95,.15,'#648f88','Roof corrugation')
(R/'scene.json').write_text(json.dumps(P))
s['perspective'](P,R/'southwest-perspective.png')
ink='#34434b';dim='#326e8b'
def project(ax,kind):
 # Orthographic faces painted from far to near, with outlines on architectural parts.
 if kind=='plan':u,v,dep=0,1,2;sg=1
 elif kind=='south':u,v,dep=0,2,1;sg=-1
 elif kind=='west':u,v,dep=1,2,0;sg=-1
 else:u,v,dep=0,2,1;sg=1
 for face in sorted(P,key=lambda f:sg*np.mean(np.array(f['vertices'])[:,dep])+(10000 if kind in ['plan','south'] and f['name'].startswith('Active PV') else 0)):
  q=np.array(face['vertices']);pts=q[:,[u,v]].copy()
  if kind=='west':pts[:,0]=L-pts[:,0]
  if kind=='north':pts[:,0]=W-pts[:,0]
  area=abs(np.sum(pts[:,0]*np.roll(pts[:,1],1)-pts[:,1]*np.roll(pts[:,0],1)))
  if area<.001:continue
  ax.add_patch(Polygon(pts,facecolor=face['color'],edgecolor=('none' if len(face['vertices'])==3 else ink),lw=.22))
 ax.set_aspect('equal');ax.axis('off')
def dimx(ax,a,b,y,origin,label):
 for xx in [a,b]:ax.plot([xx,xx],[origin,y],color=dim,lw=.5)
 ax.annotate('',(a,y),(b,y),arrowprops=dict(arrowstyle='|-|',color=dim,lw=.8));ax.text((a+b)/2,y+5,label,ha='center',fontsize=9,color=dim)
def note(ax,x,y,t):ax.text(x,y,t,fontsize=9,color=dim)
fig,axs=plt.subplots(2,2,figsize=(18,15));fig.subplots_adjust(left=.045,right=.95,top=.89,bottom=.1,wspace=.2,hspace=.25)
axs[0,0].imshow(Image.open(R/'southwest-perspective.png'));axs[0,0].axis('off');axs[0,0].set_title('01  Southwest orthographic perspective',loc='left',fontsize=13)
a=axs[0,1];project(a,'plan');a.set_xlim(-210,280);a.set_ylim(-68,310);a.set_title('02  Roof plan · north up',loc='left',fontsize=13)
dimx(a,-174.25,0,295,259,'174¼″ existing outbuilding*');dimx(a,-16,0,145,161,'16″ west cap projection')
note(a,25,280,'N ↑  ·  cap projects 16″ north');note(a,50,80,'30° fall SOUTH ↓');note(a,-183,115,'Existing outbuilding roof')
a=axs[1,0];project(a,'south');a.set_xlim(-210,290);a.set_ylim(-35,280);a.set_title('03  South elevation · looking north',loc='left',fontsize=13)
dimx(a,-174.25,0,-22,0,'174¼″ outbuilding*');note(a,10,260,'Low hip high point ≈ 20′ 1¾″*')
a=axs[1,1];project(a,'west');a.set_xlim(-40,310);a.set_ylim(-35,280);a.set_title('04  West elevation · looking east',loc='left',fontsize=13)
note(a,0,-23,'NORTH');note(a,252,-23,'SOUTH');note(a,106,120,'Shared balcony / loft floor 8′ 11¼″')
fig.suptitle('Garage + outbuilding · low hip cap / one window',x=.045,ha='left',fontsize=23,y=.97)
fig.text(.045,.93,'16″ north / west cap projection · white balcony / walkway · integrated solar with matching non-active infill',fontsize=12,color=dim)
fig.text(.045,.055,'* Study geometry: outbuilding heights/grade remain approximate. Hip rise 8″, ridge and roof junctions are provisional; east edge has no added overhang.',fontsize=10,color=dim)
fig.text(.045,.032,'Solar joints and infill are illustrative. Existing outbuilding roof remains below the balcony; separation and connections are not verified.',fontsize=10,color=dim)
for ext in ['png','svg']:fig.savefig(R/f'combined-four-views.{ext}',dpi=180,facecolor='white')
f2,ax=plt.subplots(figsize=(16,9));project(ax,'north');ax.set_xlim(-40,470);ax.set_ylim(-35,285);ax.set_title('05  North elevation · looking south',loc='left',fontsize=17)
f2.suptitle('Garage + outbuilding · third elevation',fontsize=22,x=.1,ha='left')
f2.text(.1,.08,'North garage-door opening retained. Low hip / east-face transition is a concept pending detailed roof development.',fontsize=11,color=dim)
f2.savefig(R/'north-elevation.png',dpi=180,facecolor='white');f2.savefig(R/'north-elevation.svg',facecolor='white')
with PdfPages(R/'combined-review.pdf') as pdf:pdf.savefig(fig);pdf.savefig(f2)
(R/'README.md').write_text('''# Combined low-hip garage and existing outbuilding

Four-view sheet: southwest orthographic perspective, roof plan, south elevation, west elevation. Additional north elevation supplies a third elevation. One 30 x 36 inch west loft window, 16-inch north/west cap overhang, white shared balcony/walkway structure. Integrated solar field with matching dark non-active infill at edges.

Approximate outbuilding dimensions and vertical placeholders retained per user acceptance. No CAD files changed. Low cap: north-south ridge, 8-inch rise, 16-inch projection north/west; no added east overhang. Projection at south cap junction is a concept requiring flashing design. Capeave is 2 inches higher than previous shallow cap maximum, so peak is about20ft1.75in. Balcony floor107.25in.

Existing outbuilding roof at approximately98in is not a measured clearance datum. Intersections, support connections, roof waterproofing and grade require later design; these are appearance and layout review drawings.
''')
print('Combined scene and five views saved.')
