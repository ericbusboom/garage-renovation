from pathlib import Path
import json, math
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon, Rectangle
R=Path(__file__).resolve().parent
p=json.loads((R.parent/'parameters.json').read_text())
W=p['width_east_west']; LG=p['length_north_south']; L=LG+6; YS=p['south_roof_start_y']; YB=L-78
H=p['wall_height']; B=H+8; F=B+.75; T=8; RUN=32
m=math.tan(math.radians(30))
def z(y):return B+T+m*(min(y,YB)-YS)+max(0,y-YB)/48
ink='#34434b'; dim='#326e8b'; wall='#dce2e5'
fig=plt.figure(figsize=(18,12));gs=fig.add_gridspec(2,2,height_ratios=[1,.52],width_ratios=[1.2,1],hspace=.35,wspace=.25)
a=fig.add_subplot(gs[0,0]);b=fig.add_subplot(gs[0,1]);c=fig.add_subplot(gs[1,0]);d=fig.add_subplot(gs[1,1]);d.axis('off')
def line(ax,pts,**kw):ax.plot(*zip(*pts),color=kw.pop('color',ink),lw=kw.pop('lw',1.2),**kw)
def rect(ax,x,y,w,h,fc='white',**kw):ax.add_patch(Rectangle((x,y),w,h,facecolor=fc,edgecolor=ink,lw=.9,**kw))
def label(ax,x,y,s,**kw):ax.text(x,y,s,fontsize=kw.pop('fontsize',9),color=kw.pop('color',ink),**kw)
def dx(ax,x1,x2,y,orig,s):
 for x in [x1,x2]:line(ax,[(x,orig),(x,y)],lw=.5,color=dim)
 ax.annotate('',(x1,y),(x2,y),arrowprops=dict(arrowstyle='|-|',color=dim,lw=.8));label(ax,(x1+x2)/2,y+5,s,ha='center',color=dim)
def dy(ax,y1,y2,x,orig,s):
 for y in [y1,y2]:line(ax,[(orig,y),(x,y)],lw=.5,color=dim)
 ax.annotate('',(x,y1),(x,y2),arrowprops=dict(arrowstyle='|-|',color=dim,lw=.8));label(ax,x-5,(y1+y2)/2,s,rotation=90,ha='right',va='center',color=dim)
def setup(ax,title,xlim,ylim):ax.set_aspect('equal');ax.set_xlim(*xlim);ax.set_ylim(*ylim);ax.axis('off');ax.set_title(title,loc='left',fontsize=13,pad=16)
def ft(v):
 n=round(v*4);f,n=divmod(n,48);i,q=divmod(n,4);return f'{f}′ {i}{["","¼","½","¾"][q]}″'
setup(a,'01  WEST ELEVATION · looking east',(-58,330),(-38,272))
rect(a,6,0,LG,H,wall)
a.add_patch(Polygon([(0,B),(L,B),(L,z(0)-T),(78,z(YB)-T),(0,z(L)-T)],facecolor=wall,edgecolor=ink,lw=1))
# upper horizontal siding stops at the roof underside
for h in range(114,220,6):
 end=min(L,L-(h-B)/m-YS)
 if h>z(YB)-T:end=78-(h-(z(YB)-T))*48
 if end>0:line(a,[(0,h),(end,h)],lw=.3,color='#aebbc1')
prof=[(0,z(L)),(78,z(YB)),(L-YS,z(YS))]
a.add_patch(Polygon(prof+[(x,y-T) for x,y in reversed(prof)],facecolor='white',edgecolor=ink,lw=1.3))
for y,w in [(73,28.5),(153.25,28.75)]:rect(a,L-y-w,48,w,24)
# Doors stand directly on shared walkway roof / balcony deck
rect(a,9,F,60,80)
for x in [12,42]:
 rect(a,x,F+22,24,54,'#e7f1f4');line(a,[(x+12,F+22),(x+12,F+76)],lw=.6)
 for yy in [F+40,F+58]:line(a,[(x,yy),(x+24,yy)],lw=.6)
# White offset support row and continuous horizontal walkway framing
for x in [2,89,178,275]:rect(a,x-3,0,6,H)
rect(a,0,H,L-YS,8);line(a,[(0,F),(78,F)],lw=2)
# flat horizontal members beyond balcony shown edge on, no diagonal lattice
for x in range(82,279,7):rect(a,x,B-2,1.5,2)
# white guard on rear balcony, drawing assumption 42 inches
for x in range(0,79,6):line(a,[(x,F),(x,F+42)],lw=.65)
rect(a,0,F+40,78,2);rect(a,0,F+6,78,2)
line(a,[(-10,F),(290,F)],ls=(0,(5,3)),lw=.8,color=dim)
label(a,105,F+8,'Shared balcony floor / walkway top',fontsize=9,color=dim)
dy(a,0,F,313,279,ft(F)+' shared floor')
dy(a,0,z(L),-35,0,ft(z(L))+' roof top')
dx(a,0,78,250,z(L),'6′ 6″ rear cap / balcony*')
label(a,155,185,'30° south-facing roof',rotation=-30)
label(a,18,235,'Shallow cap · ¼″ / ft',fontsize=9)
label(a,0,-20,'NORTH / GARAGE DOOR',fontsize=8);label(a,278,-20,'SOUTH',ha='right',fontsize=8)
setup(b,'02  SOUTH ELEVATION · looking north',(-85,300),(-38,272))
rect(b,0,0,W,H,wall)
base=json.loads((R.parent.parent/'model/scene.json').read_text())
for op in base['parameters']['openings']:
 if op['side']=='south':rect(b,W-op['offset']-op['width'],48 if op['type']=='window' else 0,op['width'],24 if op['type']=='window' else 80)
b.add_patch(Polygon([(0,z(YS)),(W,z(YS)),(W-36,z(L)),(0,z(L))],facecolor='#edf1f2',edgecolor=ink))
k=(z(L)-z(YS))/36;hipbreak=W-(z(YB)-z(YS))/k
line(b,[(0,z(YB)),(hipbreak,z(YB)),(W,z(YS))])
rect(b,0,z(YS)-8,W,8)
rect(b,-35,0,6,H);rect(b,-35,H,35,8);line(b,[(-35,F),(0,F)],lw=2)
rect(b,-35,F,3,42);line(b,[(-35,F+42),(0,F+42)],lw=1)
# railing is seen in projection at rear balcony
line(b,[(-32,F+7),(0,F+7)],lw=.8)
dx(b,-32,0,-23,0,'32″ to post CL')
dx(b,W-36,W,250,z(L),'3′ 0″ max east inset')
label(b,70,170,'30° solar roof',fontsize=11)
label(b,-44,160,'White balcony /\nwalkway structure',ha='center',fontsize=8)
dy(b,0,z(YS),280,W,ft(z(YS))+' south eave')
setup(c,'03  WEST WALKWAY / BALCONY SECTION · diagram',(-62,45),(65,210))
rect(c,0,65,6,143,wall);rect(c,-35,65,6,H-65);rect(c,-35,H,35,8);rect(c,-35,B,35,.75)
rect(c,-35,F,3,42);line(c,[(-32,F+42),(0,F+42)])
line(c,[(-10,F),(32,F)],ls='--',lw=.6,color=dim)
label(c,12,F+5,'Loft floor and\ndoor threshold',fontsize=8)
label(c,-17,82,'Walkway\nbelow',ha='center',fontsize=9)
label(c,-17,F+18,'Balcony\nabove',ha='center',fontsize=9)
dx(c,-32,0,180,F+42,'32″ post centerline offset')
label(c,-48,69,'WHITE finish',fontsize=8)
notes=['REVISION FOR REVIEW',
'• Rear flat-cap option retained; full-slope option dropped.',
'• No lattice rises from the walkway to the main roof.',
'• One west beam/post row: 32 inches from the existing wall.',
'• Walkway roof and balcony floor share the loft floor level.',
'• Balcony, fascia, posts and beam shown white.',
'• Horizontal members over the remaining walkway; solid',
'  walking surface beneath the balcony and French doors.',
'',
'* Provisional: balcony spans the 6 ft 6 in rear zone;',
'  French doors 5 ft × 6 ft 8 in; railing 42 in high.',
'Existing assumptions retained: 8 in beam + ¾ in deck.',
'Assembly thickness, drainage and connections need design.',
'No new east/south covered passage inferred in this sheet.']
for i,s in enumerate(notes):d.text(0,1-i*.073,s,fontsize=10 if i else 12,color=ink,va='top',fontweight='bold' if i==0 else 'normal')
fig.suptitle('Flat-cap garage · white walkway / balcony revision',x=.06,ha='left',fontsize=22,y=.97)
fig.text(.06,.925,'ELEVATIONS FIRST  /  Heights from garage ground datum  /  Concept dimensions, not construction details',fontsize=11,color=dim)
fig.subplots_adjust(top=.88,bottom=.05,left=.06,right=.95)
for ext in ['png','svg','pdf']:fig.savefig(R/f'west-balcony-elevations.{ext}',dpi=180,facecolor='white')
(R/'revision-parameters.json').write_text(json.dumps(dict(selected_roof='A',west_post_offset=32,shared_balcony_floor_walkway_top=F,finish='white',sloping_lattice=False,balcony_length_assumed=78,french_door_width_assumed=60,french_door_height_assumed=80,guard_height_assumed=42,roof_north_top=z(L)),indent=2))
print('Generated elevation PNG, SVG, PDF and revision parameters in',R)
