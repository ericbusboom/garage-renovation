"""Editable SVG/PDF/PNG framing plan; dimensions inches, north up."""
from pathlib import Path
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
OUT=Path(__file__).parent
plt.rcParams.update({'font.family':'DejaVu Sans','svg.fonttype':'none'})
fig=plt.figure(figsize=(17,12),facecolor='white')
ax=fig.add_axes([.04,.18,.63,.68]);key=fig.add_axes([.71,.17,.27,.70]);key.axis('off')
blue='#255d79';orange='#a75a2a';red='#b32e36';grey='#8a9498';purple='#73527c'
W=249.5;L=249
# Existing walls, projected floor, first six feet open.
ax.add_patch(Rectangle((0,72),224.25,183,fc='#edf3f5',ec='none'))
ax.add_patch(Rectangle((0,0),W,72,fc='#fff4df',ec='none'))
for x,y,w,h in [(0,0,W,6),(0,0,7.5,L),(W-6,0,6,L),(0,L-8,56.25,8),(221.25,L-8,28.25,8)]:ax.add_patch(Rectangle((x,y),w,h,fc='#c3c9ca',ec='#aab1b3',lw=.5))
ax.plot([56.25,221.25],[249,249],color=grey,lw=1,ls=':')
ax.text(137,232,'EXISTING GARAGE DOOR BELOW',ha='center',fontsize=8,color='#657177')
# Cabinets, not supports.
ax.add_patch(Rectangle((213.25,55.5),30,148,fc='#e6d7c4',ec='#bba78b',lw=.8))
for y in [56,105,154,203]:ax.plot([213.25,243.25],[y,y],color='#bba78b',lw=.8)
ax.text(228,130,'CABINETS · NONSTRUCTURAL',rotation=90,ha='center',va='center',fontsize=8,color='#665642')
# Existing outbuilding, schematic reference footprint / front beam.
ax.add_patch(Rectangle((-174.25,174),10,48,fc='#d8d9d8',ec=grey,lw=.7))
ax.add_patch(Rectangle((-27,174),27,75,fc='#f1eee8',ec=grey,lw=.7))
ax.add_patch(Rectangle((-184.25,164),184.25,95,fill=False,ec='#b6babc',ls='--',lw=.7))
ax.plot([-164.25,-27],[174,174],color='#6b7378',lw=3)
ax.text(-98,183,'OB1 · EXISTING',ha='center',fontsize=8,color='#596268')
ax.text(-118,223,'Existing shelter\n(reference only)',ha='center',fontsize=9,color='#7c8488')
# Current hip-cap roof projection, dashed to distinguish it from framing.
import math
cap0=-63+(107.25+120-106.5)/math.tan(math.pi/6)-8
cap1=263;cx0=-8;cx1=W+8;cy=(cap0+cap1)/2;inset=(cap1-cap0)/2
for a,b in [((cx0,cap0),(cx1,cap0)),((cx1,cap0),(cx1,cap1)),((cx1,cap1),(cx0,cap1)),((cx0,cap1),(cx0,cap0)),((cx0,cap0),(cx0+inset,cy)),((cx0,cap1),(cx0+inset,cy)),((cx1,cap0),(cx1-inset,cy)),((cx1,cap1),(cx1-inset,cy)),((cx0+inset,cy),(cx1-inset,cy))]:
 ax.plot([a[0],b[0]],[a[1],b[1]],color='#397765',ls='--',lw=1,zorder=4)
ax.text(118,157,'HIP CAP · 18″ RISE / 8″ OVERHANG',ha='center',fontsize=7,color='#397765',bbox=dict(fc='white',ec='none',alpha=.85))
# Main members; wall lines explicit, original exterior frame retained.
members=[
 ('T-SO',(-32,-63),(249.5,-63),'South outer BEAM; bottom at 98.5-in wall-top datum',blue),
 ('T-S',(0,0),(246.5,0),'Truss bottom at common wall-top datum, extending to roof; column supported',orange),
 ('T-W',(0,-63),(0,253),'Truss over existing WEST wall',orange),
 ('T-E',(224.25,-63),(224.25,253),'East truss aligned above S2 and N2',orange),
 ('B3',(0,249),(246.5,249),'Beam above NORTH wall, below loft floor',blue),
 ('T-N',(-32,253),(249.5,253),'North wall-forming truss with loft door opening',orange),
 ('B-WO',(-32,-63),(-32,253),'West outer beam on existing proposed post row',blue),
 ('T1',(0,69.75),(224.25,69.75),'Truss from common wall-top bottom datum to roof underside',orange),
 ('B2',(0,185),(224.25,185),'Main loft beam; maximum 8-inch overall depth',blue),
 ('O2',(-32,69.75),(0,69.75),'West transfer / outrigger at T1',purple),
 ('O3',(-32,185),(0,185),'West transfer / outrigger at B2',purple),
]
for name,a,b,desc,c in members:
 ax.plot([a[0],b[0]],[a[1],b[1]],color=c,lw=2.8 if name!='B2' else 4,ls='-',zorder=5)
def tag(t,x,y,c=blue,rotation=0):
 ax.text(x,y,t,ha='center',va='center',color=c,fontsize=10,fontweight='bold',rotation=rotation,bbox=dict(fc='white',ec='none',alpha=.95,pad=1.7),zorder=8)
tag('T-SO · BEAM',108,-63,blue);tag('T-S · TRUSS',108,0,orange)
tag('T1 · TRUSS',108,69.75,orange);tag('B2 · 8 in MAX',105,185,blue)
tag('T-W',0,117,orange,90);tag('T-E',224.25,151,orange,90);tag('B-WO',-32,116,blue,90)
tag('O2',-16,69.75,purple);tag('O3',-16,185,purple)
# Close north lines separated by color, pattern and leaders (actual geometry retained).
ax.annotate('B3 · BEAM UNDER LOFT FLOOR',xy=(75,249),xytext=(14,287),fontsize=9,color=blue,arrowprops=dict(arrowstyle='-',color=blue,lw=1),zorder=9)
ax.annotate('T-N · WHOLE UPPER WALL',xy=(180,253),xytext=(153,271),fontsize=9,color=orange,arrowprops=dict(arrowstyle='-',color=orange,lw=1),zorder=9)
posts=[('W1',-32,-21.25),('W2',-32,69.75),('W3',-32,185),('W4',-32,253),('S1',148.5,-21.25),('S2',224.25,-21.25),('N1',53.25,253),('N2',224.25,253),('S3',224.25,0)]
for name,x,y in posts:
 ax.add_patch(Rectangle((x-2,y-2),4,4,fc='white' if name=='S3' else '#253744',ec=red if name=='S3' else 'white',lw=1.5 if name=='S3' else .4,zorder=10))
 if name.startswith('W'):ax.text(x-8,y-7,name,fontsize=8,ha='right',color='#253744')
 elif name=='S3':ax.annotate('S3 · OPTIONAL POST',xy=(x,y),xytext=(262,17),fontsize=9,color=red,arrowprops=dict(arrowstyle='-',color=red))
 elif name.startswith('S'):ax.text(x,y-10,name,fontsize=8,ha='center')
 elif name.startswith('N'):ax.text(x+5,y+5,name,fontsize=8)
 else:ax.annotate('E1 · NEW COLUMN',xy=(x,y),xytext=(267,122),fontsize=9,color=red,arrowprops=dict(arrowstyle='-',color=red))
ax.plot([0,W],[72,72],color='#bc9b50',ls=':',lw=1)
ax.text(111,35,'OPEN BELOW\nFirst 6 ft · no loft floor',ha='center',va='center',fontsize=11,color='#75613a')
ax.text(110,132,'LOFT FLOOR',ha='center',fontsize=12,color='#788d96')
ax.annotate('',xy=(120,176),xytext=(120,150),arrowprops=dict(arrowstyle='<->',color='#8ba0a8'))
ax.text(120,145,'N–S floor joists',ha='center',fontsize=8,color='#788d96')
# Dimension the actual modeled plywood edge, not the full north truss width.
ax.add_patch(Rectangle((0,72),224.25,183,fill=False,ec='#397765',lw=1.5,zorder=6))
ax.annotate('',xy=(0,119),xytext=(224.25,119),arrowprops=dict(arrowstyle='<->',lw=1.2,color='#397765'))
ax.text(108,119,'18′ 8¼″ LOFT WIDTH',ha='center',va='center',fontsize=10,color='#397765',bbox=dict(fc='white',ec='none'))
ax.annotate('',xy=(-62,72),xytext=(-62,255),arrowprops=dict(arrowstyle='<->',lw=1.2,color='#397765'))
for yy in [72,255]:ax.plot([-65,0],[yy,yy],color='#397765',lw=.7)
ax.text(-69,139,'15′ 3″ LOFT LENGTH',rotation=90,ha='center',fontsize=10,color='#397765',bbox=dict(fc='white',ec='none'))
ax.text(108,92,'Main deck ≈ 285 sq ft · balcony separate',ha='center',fontsize=8,color='#397765',bbox=dict(fc='white',ec='none'))
# Dimensions.
def dim(x1,y1,x2,y2,label,tx,ty):
 ax.annotate('',xy=(x1,y1),xytext=(x2,y2),arrowprops=dict(arrowstyle='<->',lw=.8,color='#68747b'))
 ax.text(tx,ty,label,fontsize=9,color='#53616a',ha='center',va='center',bbox=dict(fc='white',ec='none',pad=1))
dim(0,-86,W,-86,'20 ft 9½ in · existing width',W/2,-86)
dim(-32,-106,0,-106,'32 in',-16,-106)
dim(276,0,276,-63,'63 in',294,-35)
ax.text(260,-66,'Roof start',fontsize=8,color='#53616a')
ax.text(258,94,'T-E support axis\n25¼ in from east\nexterior wall face',fontsize=8,color=orange)
ax.annotate('',xy=(224.25,110),xytext=(255,110),arrowprops=dict(arrowstyle='-',color=orange))
ax.text(10,204,'B2 bearing span: 18 ft 8¼ in',fontsize=9,color=blue)
ax.annotate('N',xy=(-165,295),xytext=(-165,270),ha='center',fontsize=14,arrowprops=dict(arrowstyle='-|>',color='#253744',lw=1.5))
ax.set(xlim=(-195,326),ylim=(-117,305),aspect='equal');ax.axis('off')
# Member legend, compact and comprehensive.
key.text(0,1,'MEMBER REGISTER',fontsize=14,fontweight='bold',color='#253744',va='top')
entries=[('T-S','Wall-top datum truss · reaches roof'),('T-E','East truss · aligned S2 / S3 / N2'),('T-W','West wall truss'),('B3','North wall BEAM · under loft floor'),('T-SO','Southernmost BEAM · common datum'),('T1','Truss · wall-top datum to roof'),('B2','Main loft beam · 8 in max depth'),('T-N','North wall truss · includes loft door'),('B-WO','West outer longitudinal beam'),('O2 / O3','Transfers from west wall to outer posts'),('OB1','Existing shelter front beam')]
for i,(n,desc) in enumerate(entries):
 y=.94-i*.055
 key.text(0,y,n,fontsize=10,fontweight='bold',color=blue if n=='B2' else orange if n in ('T-S','T-E','T-W','T1','T-N') else blue,va='top')
 key.text(.23,y,desc,fontsize=9.5,va='top',wrap=True)
key.text(0,.22,'DRAWING BASIS',fontsize=11,fontweight='bold',color='#253744')
key.text(0,.19,'• S2 moved east 12¾ in to align with N2.\n• Gray = existing walls; brown fill = cabinets.\n• Hollow red S3 = optional 4-inch post.\n• Solid orange = truss; B-S removed.\n• Truss depth is vertical, not plan width.\n• All bottoms = wall top; columns carry loads.',fontsize=9,va='top',linespacing=1.8)
fig.text(.05,.94,'GARAGE · REVISED FRAMING PLAN',fontsize=22,fontweight='bold',color='#253744')
fig.text(.05,.904,'Roof removed · north up · every primary member labeled',fontsize=13,color='#68747b')
fig.text(.05,.112,'Every beam / truss bottom is at 8 ft 2½ in, aligned with the wall tops. Loads go to columns, not the old walls.',fontsize=11)
fig.text(.05,.081,'Concept only: T-SO is 63 in south of T-S. B-S removed; south support-row / T-SO bearing details remain unresolved.\nThe previous east-wall trial post E1 is omitted from this option; it no longer aligns with T-E. Cabinets remain nonstructural. Beam sizes and transfers require reanalysis.',fontsize=9,color='#68747b',linespacing=1.6)
fig.savefig(OUT/'labeled-framing-plan.png',dpi=180);fig.savefig(OUT/'labeled-framing-plan.svg');fig.savefig(OUT/'labeled-framing-plan.pdf');plt.close(fig)
(OUT/'framing-member-register.json').write_text(json.dumps({'units':'inches','origin':'SW exterior corner','members':[{'id':n,'start':a,'end':b,'description':d,'bottom_elevation':98.5,'support_basis':'columns; aligned with wall tops'} for n,a,b,d,c in members],'existing_shelter_beam':{'id':'OB1','start':[-164.25,174],'end':[-27,174]},'posts':[{'id':n,'x':x,'y':y,'status':'optional' if n=='S3' else 'proposed'} for n,x,y in posts],'note':'B-S removed; S1 south support needs revised connection/load path. Concept centerlines; wall framing elevated independently; B3 beam below loft floor; T-N upper-wall truss with door opening. Exact elevations unresolved.'},indent=2))
