"""Dimensioned concept sections. inches; elevations coordinated to existing study floor."""
from pathlib import Path
import math,json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle,Polygon
from matplotlib.backends.backend_pdf import PdfPages
OUT=Path(__file__).parent
plt.rcParams.update({'font.family':'DejaVu Sans','svg.fonttype':'none'})
WALL=98.5;DECK=.75;BEAM_DEPTH=8;BT=WALL+BEAM_DEPTH;F=BT+DECK;YS=-63;YN=255;RISE=120;ROOFT=8
K=math.tan(math.pi/6);BREAK=YS+(F+RISE-BT)/K
blue='#285f7b';orange='#a25b32';red='#b7333c';grey='#869298';green='#397765'
def roof(y):return min(BT+(y-YS)*K,F+RISE)
def ft(v):
 q=round(abs(v)*4);feet=q//48;r=q%48;whole=r//4;fraction=['','¼','½','¾'][r%4]
 return ('−' if v<0 else '')+f'{feet}′ {whole}{fraction}″'
def dim(ax,x1,y1,x2,y2,label,dx=0,dy=0,color='#586872',rot=0):
 ax.annotate('',xy=(x1,y1),xytext=(x2,y2),arrowprops=dict(arrowstyle='<->',lw=.8,color=color))
 ax.text((x1+x2)/2+dx,(y1+y2)/2+dy,label,ha='center',va='center',fontsize=9,color=color,rotation=rot,bbox=dict(fc='white',ec='none',pad=1.5))
def panel_truss(ax,a,b,z,depth=24,panels=6,rect=False):
 ax.plot([a,b,b,a,a],[z,z,z+depth,z+depth,z],color=orange,lw=2.5)
 xs=[a+(b-a)*i/panels for i in range(panels+1)]
 for x in xs[1:-1]:ax.plot([x,x],[z,z+depth],color=orange,lw=1.8)
 for i,(x1,x2) in enumerate(zip(xs[:-1],xs[1:])):
  if not rect or i in [0,panels-1]:ax.plot([x1,x2],[z,z+depth] if i%2==0 else [z+depth,z],color=orange,lw=1.4)
def finish(fig,name):
 fig.savefig(OUT/(name+'.png'),dpi=170);fig.savefig(OUT/(name+'.svg'));return fig
figs=[]
# WEST CUT: south left, north right; clearances are vertical to underside.
fig,ax=plt.subplots(figsize=(16,10));fig.subplots_adjust(left=.07,right=.96,top=.85,bottom=.23)
ax.add_patch(Rectangle((0,0),249,WALL,fc='#f0f1ef',ec='#b9c0c1',lw=1))
ax.text(118,45,'EXISTING GARAGE BELOW',ha='center',color=grey,fontsize=11)
ax.plot([72,255],[F,F],color=blue,lw=2);ax.text(108,F-8,'LOFT FLOOR',color=blue,fontsize=9)
poly=[(YS,roof(YS)),(BREAK,roof(BREAK)),(YN,roof(YN)),(YN,roof(YN)+ROOFT),(BREAK,roof(BREAK)+ROOFT),(YS,roof(YS)+ROOFT)]
ax.add_patch(Polygon(poly,fc='#ccd8dd',ec=blue,lw=2))
ax.text(25,roof(25)+15,'30° ROOF',rotation=-30,fontsize=12,color=blue)
# Shallow hip cap projected into this west section; ceiling datum remains level.
cap0=BREAK-8;cap1=YN+8;capmid=(cap0+cap1)/2;capeave=F+RISE+ROOFT;capridge=capeave+18
ax.add_patch(Polygon([(cap0,F+RISE),(cap1,F+RISE),(cap1,capeave),(capmid,capridge),(cap0,capeave)],fc='#dee9e1',ec=green,lw=1.5,zorder=3))
ax.plot([cap0,cap1],[capeave,capeave],color=green,lw=.8)
ax.text(capmid,capridge+12,'SHALLOW HIP CAP',ha='center',fontsize=10,color=green)
dim(ax,capmid, capeave,capmid,capridge,'18″ rise',dx=-27,color=green)
ax.annotate('8″ overhang + white soffit / fascia',xy=(cap1,F+RISE+4),xytext=(310,276),ha='center',fontsize=8,color=green,arrowprops=dict(arrowstyle='-',color=green))
ax.plot([BREAK,BREAK],[F-3,F+RISE],ls=':',color=grey,lw=1)
# Cut sections of cross members. Widths symbolic, depth actual trial dimension.
parts=[('T-SO',YS,WALL,8,blue),('T-S',0,WALL,roof(0)-WALL,orange),('T1',69.75,WALL,roof(69.75)-WALL,orange),('B2',185,WALL,8,blue),('B3',249,WALL,8,blue)]
for name,y,z,d,c in parts:
 ax.add_patch(Rectangle((y-2,z),4,d,fc=c,alpha=.95,zorder=7))
 offset={'T-SO':(-29,-15),'T-S':(-12,-28),'T1':(-20,-34),'B2':(-5,-30),'B3':(24,-30)}[name]
 ax.annotate(name,xy=(y,z+d/2),xytext=(y+offset[0],z+offset[1]),fontsize=10,color=c,fontweight='bold',arrowprops=dict(arrowstyle='-',color=c),ha='center')
# North wall truss, end-on section: open door region then 24-inch header.
ax.add_patch(Rectangle((251,WALL),4,F+120-WALL,fc=orange,ec=orange,lw=0))
ax.annotate('T-N\nWHOLE WALL TRUSS',xy=(253,F+108),xytext=(296,F+111),fontsize=10,color=orange,ha='center',arrowprops=dict(arrowstyle='-',color=orange))
ax.axhline(WALL,color=grey,lw=1,ls='--')
ax.text(85,WALL-14,'COMMON BOTTOM EDGE · 8 ft 2½ in',ha='center',fontsize=9,color=grey)
ax.annotate('T-S reaches roof',xy=(0,(WALL+roof(0))/2),xytext=(-36,153),fontsize=9,color=orange,arrowprops=dict(arrowstyle='-',color=orange))
dim(ax,84,WALL,84,roof(69.75),ft(roof(69.75)-WALL)+' T1 height',dx=12,color=orange)
# Clearances above floor/beam top.
for y in [185]:
 top=BT
 x=y+12
 dim(ax,x,top,x,roof(y),ft(roof(y)-top),dx=12,color=green)
 ax.plot([y,x],[roof(y),roof(y)],color=green,lw=.6)
dim(ax,276,F,276,F+120,'10′ 0″ clear',dx=9,rot=90,color=green)
dim(ax,-83,0,-83,WALL,ft(WALL)+' wall',dx=-9,rot=90)
dim(ax,315,0,315,F,ft(F)+' loft floor',dx=10,rot=90)
# Dimension chains along base.
dim(ax,YS,-28,0,-28,'63″')
dim(ax,0,-28,69.75,-28,'69¾″')
dim(ax,69.75,-28,185,-28,'115¼″')
dim(ax,185,-28,253,-28,'68″')
dim(ax,YS,-53,BREAK,-53,ft(BREAK-YS)+' sloping run')
dim(ax,BREAK,-53,255,-53,ft(255-BREAK)+' cap base run')
ax.text(BREAK,F-16,'Break at '+ft(BREAK)+' north of south wall',ha='center',fontsize=8,color=grey)
ax.set(xlim=(345,-110),ylim=(-67,293),aspect='equal');ax.axis('off')
fig.suptitle('WEST SECTION · ROOF AND FRAMING CLEARANCES',x=.06,ha='left',fontsize=19,y=.95)
fig.text(.06,.90,'Looking east · north at left · vertical dimensions to ROOF UNDERSIDE · conceptual member elevations',fontsize=11,color=grey)
fig.text(.06,.16,'Datum: loft floor = 8′ 11¼″ above ground. Roof underside starts at T-SO top = 8′ 10½″; it rises to 10′ 0″ above loft floor.',fontsize=10)
fig.text(.06,.125,'ALL beam and truss bottoms = wall top, 8′ 2½″. Columns carry the loads; existing walls are not assigned new gravity load.\nTrial beam depths: T-SO / B2 / B3 = 8 in. T-S and T1 extend from wall-top datum to roof underside. Loft floor is ¾ in above the 8-in beams. Roof band = 8 in, provisional.',fontsize=10,linespacing=1.5)
fig.text(.06,.065,'Longitudinal T-W / T-E and B-WO are outside this interior cut; their BOTTOM edges share the same wall-top datum. Depths remain to be designed.\nHip cap: 18-in rise above eaves, 8-in overhang and fascia; rear ceiling datum unchanged. North wall edge = 255 in; cap eave = 263 in.',fontsize=9,color=grey,linespacing=1.5)
figs.append(finish(fig,'west-roof-section'))
# T1 frontal framing elevation.
fig,ax=plt.subplots(figsize=(14,8));fig.subplots_adjust(left=.07,right=.96,bottom=.28,top=.8)
T1H=roof(69.75)-WALL
panel_truss(ax,0,224.25,0,T1H,6,True)
ax.plot([0,224.25],[0,0],color=blue,lw=1)
ax.add_patch(Polygon([(-4,-5),(4,-5),(0,0)],fc=blue));ax.add_patch(Polygon([(220.25,-5),(228.25,-5),(224.25,0)],fc=blue))
ax.text(0,-11,'Column-supported bearing',ha='center',fontsize=10,color=blue);ax.text(224.25,-11,'Column-supported bearing',ha='center',fontsize=10,color=blue)
dim(ax,0,-26,224.25,-26,'18′ 8¼″ · bearing-center span')
dim(ax,244,0,244,T1H,ft(T1H)+'\nwall top to roof',dx=19)
for a,b in zip([0,37.375,74.75,112.125,149.5,186.875],[37.375,74.75,112.125,149.5,186.875,224.25]):dim(ax,a,T1H+14,b,T1H+14,'37⅜″',dy=0)
# Keep web lines unobscured; storage-bay explanation is in sheet notes.
ax.set(xlim=(-12,280),ylim=(-32,T1H+26),aspect='equal');ax.axis('off')
fig.suptitle('T1 · DIMENSIONED TRUSS CONCEPT',x=.06,ha='left',fontsize=19,y=.94)
fig.text(.06,.86,'View from south looking north · west at left · T1 terminates at T-E · bottom edge at common wall-top datum · column-supported framing',fontsize=11,color=grey)
fig.text(.06,.16,'Height is set by the roof underside. Six equal panel bays are a drawing assumption. Panel dimensions are centerline spacing, not clear cabinet openings.\nRectangular central bays require designed moment connections / Vierendeel action; end diagonals alone are not a complete truss design.',fontsize=10,linespacing=1.6)
fig.text(.06,.07,'T1 bottom edge = 8 ft 2½ in; top edge = '+ft(roof(69.75))+' above ground, at the roof underside. No gap above T1. Loads go to column-supported framing.\nMember widths, welds, bearing seats, lateral bracing and cabinet loads remain to be designed.',fontsize=9,color=grey,linespacing=1.5)
figs.append(finish(fig,'T1-dimensioned'))
# T-N upper wall elevation, with 7-foot door and independent floor beam indicated.
fig,ax=plt.subplots(figsize=(15,9));fig.subplots_adjust(left=.06,right=.95,top=.84,bottom=.22)
a=-32;b=249.5;DC=97.5;DW=32;NB=WALL-F
panel_truss(ax,a,b,96,24,8)
for x in [a,53.25,DC-DW/2,DC+DW/2,224.25,b]:ax.plot([x,x],[NB,96],color=orange,lw=2)
ax.plot([a,b],[NB,NB],color=orange,lw=2)
ax.plot([a,b],[0,0],color=grey,lw=.8,ls='--')
ax.text(-27,3,'LOFT FLOOR',fontsize=8,color=grey)
# Door opening kept clear; non-door bays intentionally no unverified web layout.
ax.add_patch(Rectangle((DC-DW/2,0),DW,84,fc='white',ec=blue,lw=2,zorder=5))
ax.plot([DC,DC],[0,130],color=grey,ls=':',lw=.8)
ax.text(DC,41,'LOFT\nDOOR',ha='center',fontsize=11,color=blue)
ax.add_patch(Rectangle((0,NB),246.5,8,fc=blue,alpha=.18,ec=blue,lw=1))
ax.text(137,-24,'B3 · 8-in trial beam · same bottom datum as T-N',ha='center',fontsize=9,color=blue)
for name,x in [('W4',-32),('N1',53.25),('N2',224.25)]:ax.add_patch(Polygon([(x-3,NB-4),(x+3,NB-4),(x,NB)],fc=blue));ax.text(x,NB-9,name,fontsize=9,ha='center',color=blue)
dim(ax,a,-43,b,-43,'23′ 5½″ · overall T-N framing line')
dim(ax,a,139,53.25,139,'7′ 1¼″')
dim(ax,53.25,139,224.25,139,'14′ 3″')
dim(ax,224.25,139,b,139,'25¼″')
dim(ax,DC-DW/2,89,DC+DW/2,89,'32″ door¹')
dim(ax,DC+25,0,DC+25,84,'7′ 0″',dx=9,rot=90,color=blue)
dim(ax,272,0,272,120,'10′ 0″ floor to roof underside',dx=10,rot=90)
dim(ax,294,96,294,120,'24″\nheader',dx=18)
dim(ax,-42,NB,-42,120,ft(120-NB)+' overall',dx=-10,rot=90)
ax.text(DC,127,'Door CL = 97½″ from west garage exterior face',ha='center',fontsize=9,color=grey)
ax.text(3,48,'Side framing / windows\nto be coordinated',fontsize=9,ha='center',color=grey)
ax.text(189,48,'Side framing / windows\nto be coordinated',fontsize=9,ha='center',color=grey)
ax.set(xlim=(-70,332),ylim=(-52,150),aspect='equal');ax.axis('off')
fig.suptitle('T-N · NORTH WALL / DOOR TRUSS CONCEPT',x=.06,ha='left',fontsize=19,y=.94)
fig.text(.06,.87,'View from inside looking north · west at left · loft floor is the zero datum',fontsize=11,color=grey)
fig.text(.06,.145,'Seven-foot door retained under a trial 24-in trussed header. Header underside is 8 ft above floor: 12 in above nominal door top.\n¹32-in door width retained from earlier drawing; actual rough opening and connection allowances are not yet specified.',fontsize=10,linespacing=1.6)
fig.text(.06,.07,'T-N overall height = 10 ft 8¾ in, from common wall-top datum to roof underside; loft floor is 8¾ in above that datum.\nColumn-supported structure. Door threshold is at loft floor. Side-frame webs, windows, connections and beam depths remain conceptual.',fontsize=9,color=grey,linespacing=1.5)
figs.append(finish(fig,'TN-dimensioned'))
with PdfPages(OUT/'dimensioned-trusses-and-west-section.pdf') as pdf:
 for fig in figs:pdf.savefig(fig)
for fig in figs:plt.close(fig)
data={'datum':'inches above ground; all member bottoms at wall top; column supported','common_member_bottom':WALL,'north_truss_overall_height':F+120-WALL,'floor':F,'wall_top':WALL,'roof_start_y':YS,'roof_start_underside':BT,'roof_plateau_underside':F+120,'break_y_from_south_wall':BREAK,'sloped_run':BREAK-YS,'flat_run_to_y255':255-BREAK,'hip_cap':{'rise_inches':18,'overhang_inches':8,'fascia_inches':8,'ridge_elevation_inches':F+RISE+ROOFT+18},'depth_assumptions':{'TSO':8,'TS':roof(0)-WALL,'T1':roof(69.75)-WALL,'B2':8,'B3':8,'TN_header':24},'clearance_above_loft_floor':{n:roof(y)-F for n,y in [('TS',0),('T1',69.75),('B2',185),('B3',249)]},'clearance_above_member_top':{n:roof(y)-top for n,y,top in [('TS',0,roof(0)),('T1',69.75,roof(69.75)),('B2',185,BT),('B3',249,BT)]}}
(OUT/'section-dimensions.json').write_text(json.dumps(data,indent=2));print(json.dumps(data,indent=2))
