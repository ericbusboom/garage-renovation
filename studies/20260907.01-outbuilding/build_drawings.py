from pathlib import Path
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
R=Path(__file__).resolve().parent
# Local plan: x east, y north; garage west wall x=0, common south face y=0.
bench=27;depth=75;pillar=10;pd=48;span=137.25;total=bench+span+pillar
px=-total;bx=-bench;roofwest=px-10
# Display placeholders only, not measurements or model parameters.
H_draw=96;counter_draw=35;roof_draw=98
ink='#34434b';blue='#326e8b';muted='#697981';wood='#efe3cf';steel='#788a93'
fig,axes=plt.subplots(2,2,figsize=(18,13));fig.subplots_adjust(left=.055,right=.96,top=.88,bottom=.1,hspace=.4,wspace=.23)
def line(ax,pts,**kw):ax.plot(*zip(*pts),color=kw.pop('color',ink),lw=kw.pop('lw',1),**kw)
def rect(ax,x,y,w,h,fc='white',**kw):ax.add_patch(Rectangle((x,y),w,h,facecolor=fc,edgecolor=ink,lw=.9,**kw))
def text(ax,x,y,s,**kw):ax.text(x,y,s,fontsize=kw.pop('fontsize',9),color=kw.pop('color',ink),ha=kw.pop('ha','center'),va=kw.pop('va','center'),**kw)
def dx(ax,a,b,y,origin,label):
 for x in [a,b]:line(ax,[(x,origin),(x,y)],lw=.5,color=blue)
 ax.annotate('',(a,y),(b,y),arrowprops=dict(arrowstyle='|-|',color=blue,lw=.8));text(ax,(a+b)/2,y+4,label,color=blue,va='bottom',fontsize=9)
def dy(ax,a,b,x,origin,label):
 for y in [a,b]:line(ax,[(origin,y),(x,y)],lw=.5,color=blue)
 ax.annotate('',(x,a),(x,b),arrowprops=dict(arrowstyle='|-|',color=blue,lw=.8));text(ax,x-4,(a+b)/2,label,color=blue,rotation=90,fontsize=9)
def setup(ax,title,xx,yy):ax.set_title(title,loc='left',fontsize=13,pad=18);ax.set_xlim(*xx);ax.set_ylim(*yy);ax.set_aspect('equal');ax.axis('off')
a=axes[0,0];setup(a,'01  PLAN · north up',(-220,50),(-56,123))
rect(a,0,-8,8,92,'#dde2e4');text(a,17,35,'GARAGE WEST WALL',rotation=90,color=muted)
rect(a,bx,0,bench,depth,wood);text(a,-13.5,37.5,'WORKBENCH',rotation=90,fontsize=9)
rect(a,px,0,pillar,pd,wood);text(a,px+5,24,'PILLAR',rotation=90,fontsize=8)
rect(a,px+pillar,0,span,2.5,steel)
rect(a,roofwest,-10,-roofwest,95,'none',ls=(0,(5,3)))
line(a,[(px-8,75),(25,75)],ls=(0,(4,3)),color=blue,lw=.8);text(a,-100,79,'Garage north wall / workbench north end',fontsize=8,color=blue)
line(a,[(px-8,0),(3,0)],ls='--',color=blue,lw=.8)
text(a,-96,7,'COMMON SOUTH FACE / CONNECTING BEAM',fontsize=8)
text(a,-98,40,'Open covered work area',fontsize=11)
dx(a,px,px+10,-23,0,'10″');dx(a,px+10,bx,-23,0,'137¼″ beam*');dx(a,bx,0,-23,0,'27″')
dx(a,px,0,-44,0,'174¼″ overall*')
dy(a,0,75,34,0,'75″ workbench N–S')
dy(a,0,48,px-12,px,'48″ pillar N–S');dy(a,48,75,px-12,px,'27″ offset')
dy(a,75,85,13,0,'10″');dy(a,-10,0,13,0,'10″')
dx(a,roofwest,px,104,85,'10″');text(a,-65,107,'N ↑',fontsize=12)
a.annotate('Dashed: roof outline\n95″ N–S × 184¼″ E–W*',xy=(roofwest,60),xytext=(-125,98),fontsize=8,color=muted,arrowprops=dict(arrowstyle='-',color=muted))
b=axes[0,1];setup(b,'02  SOUTH / FRONT ELEVATION · looking north',(-210,42),(-32,131))
rect(b,0,0,8,98.5,'#dde2e4');text(b,19,48,'GARAGE',rotation=90,color=muted)
for x,w in [(px,10),(bx,27)]:
 rect(b,x,0,w,H_draw,wood)
 for yy in range(8,H_draw,8):line(b,[(x,yy),(x+w,yy)],lw=.4,color='#c8b799')
 for xx in [x,x+w-2.5]:rect(b,xx,0,2.5,H_draw,steel)
rect(b,px+10,H_draw-18,span,18,wood)
rect(b,px+10,H_draw-18,span,2.5,steel);rect(b,px+10,H_draw-2.5,span,2.5,steel)
line(b,[(roofwest,roof_draw),(0,roof_draw)],lw=3,color='#4d7271')
line(b,[(roofwest,roof_draw-.75),(0,roof_draw-.75)],lw=.8)
line(b,[(px-6,0),(8,0)],lw=.8)
dx(b,px+10,bx,118,H_draw,'137¼″ beam length*');dy(b,H_draw-18,H_draw,-9,bx,'18″ beam')
dx(b,px,0,-20,0,'174¼″ overall*')
b.annotate('Beam bottom height: TBD',xy=(-110,H_draw-18),xytext=(-117,57),fontsize=9,color=blue,ha='center',arrowprops=dict(arrowstyle='-',color=blue))
text(b,-91,32,'Opening shown clear for clarity;\nloose cabinets and equipment omitted.',fontsize=9,color=muted)
text(b,-95,106,'Corrugated plastic on ¾″ steel tube roof framing',fontsize=8)
c=axes[1,0];setup(c,'03  WEST ELEVATION · looking east',(-30,137),(-30,125))
# North at left. Workbench full width 75, pillar projects in front of south48.
rect(c,0,0,75,H_draw,wood)
rect(c,2.5,counter_draw,70,2,wood)
line(c,[(2.5,68),(72.5,68)],lw=2,color='#c0a17c')
for x in [0,72.5]:rect(c,x,0,2.5,H_draw,steel)
rect(c,27,0,48,H_draw,'#ede0c9')
for yy in range(8,H_draw,8):line(c,[(27,yy),(75,yy)],lw=.4,color='#c8b799')
rect(c,27,0,2.5,H_draw,steel);rect(c,72.5,0,2.5,H_draw,steel)
line(c,[(-10,roof_draw),(85,roof_draw)],lw=3,color='#4d7271')
line(c,[(0,0),(0,H_draw+8)],ls=(0,(4,3)),color=blue,lw=.7)
dx(c,0,27,-16,0,'27″');dx(c,27,75,-16,0,'48″ pillar')
dx(c,-10,0,115,roof_draw,'10″');dx(c,0,75,115,roof_draw,'75″');dx(c,75,85,115,roof_draw,'10″')
text(c,0,-26,'NORTH',fontsize=8);text(c,75,-26,'SOUTH',fontsize=8)
c.annotate('Workbench beyond pillar',xy=(15,55),xytext=(97,63),fontsize=8,color=muted,arrowprops=dict(arrowstyle='-',color=muted))
c.annotate('Workbench top: TBD',xy=(10,counter_draw+2),xytext=(97,40),fontsize=8,color=blue,arrowprops=dict(arrowstyle='-',color=blue))
text(c,40,105,'Roof pitch / fall direction: TBD',fontsize=8,color=blue)
d=axes[1,1];d.axis('off')
notes=[('MEASURED / USER-SUPPLIED',True),('Workbench: 27″ E–W × 75″ N–S, against garage west wall.',False),('Workbench north end aligns with garage north wall.',False),('Electrical pillar: 10″ E–W × 48″ N–S; south faces align.',False),('Connecting beam: 137¼″ long × 18″ high × 2½″ deep.',False),('Beam frame: 2½″ × 2½″ tube; tube wall thickness unknown.',False),('Other main supports: 2½″ × 2½″ × ¼″ steel angle.',False),('Roof framing: ¾″ rectangular steel tube; other section',False),('dimension / wall thickness / spacing not supplied.',False),('Roof panels: corrugated plastic; three 10″ overhangs.',False),('',False),('CHECK BEFORE COMBINING WITH GARAGE',True),('* Beam drawn between inner faces of the two supports.',False),('   Result: 174¼″ overall width; 184¼″ roof width.',False),('Roof east edge drawn meeting garage wall; confirm.',False),('Overall height, beam-bottom height, bench-top height',False),('and roof pitch are unmeasured. Vertical positions are',False),('schematic; only the 18″ beam height is dimensioned.',False),('Beam south face taken flush with both support faces.',False)]
for i,(t,bold) in enumerate(notes):d.text(0,1-i*.051,t,fontsize=10,color=ink,va='top',fontweight='bold' if bold else 'normal')
fig.suptitle('Existing outbuilding · dimension check',x=.055,y=.975,ha='left',fontsize=23)
fig.text(.055,.93,'PLAN + ELEVATIONS  /  Dimensions in inches  /  Standalone survey draft for review',fontsize=12,color=blue)
fig.text(.055,.045,'Heights are schematic, not measured from photos. Derived dimensions marked * depend on the beam-end interpretation. No garage proposal geometry changed.',fontsize=10,color=muted)
for ext in ['png','svg','pdf']:fig.savefig(R/f'outbuilding-dimension-check.{ext}',dpi=180,facecolor='white')
data={'units':'inches','origin':'garage west wall x=0; common south support face y=0; east +x, north +y','workbench':{'x':-27,'y':0,'width_EW':27,'length_NS':75,'top_height':None},'electrical_pillar':{'x_assumed':px,'y':0,'width_EW':10,'length_NS':48},'beam':{'length':137.25,'height':18,'depth_NS':2.5,'bottom_height':None,'end_interpretation':'PROVISIONAL clear between support inner faces','tube_outer': [2.5,2.5],'tube_wall':None},'main_angle':{'legs':[2.5,2.5],'thickness':.25},'roof':{'north_overhang':10,'south_overhang':10,'west_overhang':10,'east_edge':'assumed meets garage wall','framing_stated_size':.75,'framing_other_dimension':None,'pitch':None,'material':'corrugated plastic'},'derived_provisional':{'overall_EW':total,'roof_EW':total+10,'roof_NS':95,'pillar_north_offset_from_garage':27},'vertical_drawing':'Schematic placeholders only; not calibrated dimensions'}
(R/'parameters.json').write_text(json.dumps(data,indent=2))
print('Saved PNG, SVG, PDF and parameters.json')
