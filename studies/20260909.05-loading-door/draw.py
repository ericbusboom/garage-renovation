from pathlib import Path
import os, json
os.environ['MPLCONFIGDIR']='/private/tmp/garage-sequence-mpl'
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle,Polygon,Arc
P=Path(__file__).resolve().parent
W=249.5; west=56.25; east=west+96; pivot=np.array([west,-6.]); radius=96
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10})
fig,axs=plt.subplots(1,2,figsize=(18,10),layout='constrained',gridspec_kw={'width_ratios':[1,1.2]})
blue='#28678b';orange='#bc6b22';green='#2c8072';gray='#69767c'
def dim(ax,a,b,label,offset=(0,0)):
 ax.annotate('',a,b,arrowprops={'arrowstyle':'<->','color':'#40494d'})
 ax.text((a[0]+b[0])/2+offset[0],(a[1]+b[1])/2+offset[1],label,ha='center',va='center',fontsize=10)
ax=axs[0]
ax.add_patch(Rectangle((0,0),W,120,fc='#eef0ef',ec=gray,lw=1.5))
ax.add_patch(Rectangle((0,120),W,107.25,fc='#e3e9ea',ec=gray,lw=1.5))
ax.add_patch(Polygon([(-8,227.25),(W+8,227.25),(W/2+35,245.25),(W/2-35,245.25)],fc='#d1d8da',ec=gray,lw=2))
ax.add_patch(Rectangle((-8,222),W+16,5.25,fc='white',ec=gray))
# Ground door width deliberately retained as illustrative only.
ax.add_patch(Rectangle((56.25,0),96,96,fc='#dce1e1',ec=gray,lw=2))
ax.plot([104.25,104.25],[0,96],c=gray)
ax.text(104.25,47,'New ground-floor\nsliding garage doors\n22 in forward of upper wall\nwidth shown aligned to upper jambs',ha='center',fontsize=10)
ax.add_patch(Rectangle((west,120),96,84,fc='white',ec=blue,lw=2))
ax.text((west+east)/2,154,'Upper loading opening\n8 ft wide × 7 ft high*',ha='center',fontsize=10)
for x in [west-6,east]:
 ax.add_patch(Rectangle((x,0),6,227.25,fc=blue,alpha=.65))
ax.add_patch(Rectangle((east+1,120),96,84,fc='#bcd1d8',ec=blue,ls='--',alpha=.65))
ax.text(east+49,166,'8-ft leaf\nparked EAST\noutside wall',ha='center',fontsize=9)
ax.plot([west-4,W+1],[209,209],c=gray,lw=3)
ax.add_patch(Rectangle((west,112),96,8,fc='white',ec=blue,lw=2))
ax.text(110,107,'Loading ledge at floor level',ha='center',fontsize=9,color=blue)
ax.plot([west,west],[177,204],c=orange,lw=4)
ax.plot([west,east],[196,196],c=orange,lw=3)
ax.plot([west,east],[204,196],c=orange,lw=1.5)
ax.text(106,216,'Jib shown parallel to wall; mounting height TBD',ha='center',color=orange,fontsize=9)
dim(ax,(west,260),(east,260),'96 in clear opening',(0,4))
dim(ax,(-18,0),(-18,120),'Floor\n10 ft',(-17,0))
ax.annotate('6-in west jamb column\nfull height to roof\nsize is a placeholder',(west-3,65),xytext=(31,15),arrowprops={'arrowstyle':'->','color':blue},ha='center',fontsize=9,color=blue)
ax.text(W/2,-16,'EAST ←   Looking south at north wall   → WEST',ha='center',weight='bold')
ax.text(W/2,-34,'Upper wall stays at current north wall.\nLedge projects toward viewer; guard/loading gate not detailed.',ha='center',fontsize=10)
ax.set(xlim=(W+12,-55),ylim=(-43,280),title='NORTH ELEVATION — conceptual placement')
ax.set_aspect('equal');ax.axis('off')
ax=axs[1]
ax.add_patch(Rectangle((0,-140),W,140,fc='#edf0ef',ec=gray))
ax.add_patch(Rectangle((0,0),W,22,fc='#e7d6a8',ec=gray,lw=1.5))
ax.text(185,11,'22-in ledge / extension',ha='center',fontsize=9)
ax.plot([0,west],[0,0],c=blue,lw=5);ax.plot([east,W],[0,0],c=blue,lw=5)
ax.plot([0,W],[22,22],c=green,lw=2)
ax.axhline(82,c='#a14b46',lw=2)
ax.text(10,87,'PROPERTY LINE • street/curb position not surveyed',color='#a14b46',fontsize=10)
ax.text(10,28,'5-ft setback envelope: outer door / ledge / roof edge',color=green,fontsize=9)
ax.add_patch(Rectangle((east+1,2),96,3,fc='#bcd1d8',ec=blue,ls='--'))
ax.annotate('Exterior sliding leaf parks east\ntrack / end clearances to verify',(205,4),xytext=(183,-42),arrowprops={'arrowstyle':'->','color':blue},ha='center',color=blue,fontsize=9)
for x in [west-6,east]:
 ax.add_patch(Rectangle((x,-6),6,6,fc=blue))
 ax.add_patch(Rectangle((x,16),6,6,fc=green))
 ax.plot([x+3,x+3],[0,16],c=green,ls=':',lw=2)
ax.scatter(*pivot,c=orange,s=65,zorder=8)
angles=np.linspace(-np.pi/2,np.pi/2,250)
arc=pivot[:,None]+radius*np.array([np.cos(angles),np.sin(angles)])
ax.plot(*arc,c=orange,ls='--',lw=2)
for angle,label in [(-np.pi/2,'Stowed inside'),(0,'Through doorway'),(np.pi/2,'Outward reach')]:
 end=pivot+radius*np.array([np.cos(angle),np.sin(angle)])
 ax.plot([pivot[0],end[0]],[pivot[1],end[1]],c=orange,lw=2.5)
 ax.scatter(*end,c=orange,s=22)
ax.text(48,-100,'Stowed\ninside',ha='right',color=orange)
ax.text(97,-17,'8-ft arm • 180° swing',color=orange,ha='center',fontsize=10)
ax.annotate('Pivot at upper WEST jamb\nshown 6 in inside wall; bracket offset TBD',pivot,xytext=(-34,-57),arrowprops={'arrowstyle':'->','color':orange},fontsize=9,color=orange)
ax.annotate('Full-height upper jamb posts (blue)\nOuter supports (green) are 22 in north\nConnection between frames TBD',(east+3,18),xytext=(172,-85),arrowprops={'arrowstyle':'->'},ha='center',fontsize=9)
dim(ax,(268,0),(268,22),'22 in',(16,0))
dim(ax,(268,22),(268,82),'60 in\n5 ft',(16,0))
dim(ax,(-18,0),(-18,82),'82 in\n6 ft 10 in',(-19,0))
dim(ax,(west,-127),(east,-127),'8-ft upper doorway',(0,-6))
ax.text(180,-115,'UPPER SHOP / LOFT',ha='center',color=gray,weight='bold')
ax.text(124,107,'8-ft radius from inset pivot reaches 8 in beyond property line\nReach shown geometrically; truck access and permitted swing unverified.',ha='center',fontsize=9,color='#a14b46')
ax.annotate('N',xy=(245,110),xytext=(245,94),arrowprops={'arrowstyle':'->'},ha='center',weight='bold')
ax.set(xlim=(-48,302),ylim=(-143,119),title='UPPER-FLOOR PLAN — north up, west left')
ax.set_aspect('equal');ax.axis('off')
fig.suptitle('North loading-door extension + column-mounted swing jib',fontsize=22,weight='bold')
fig.supxlabel('Placement study only. Owner-supplied 5-ft setback assumed, not verified. 82 − 60 = 22 in gross ledge depth; a 24-in ledge needs upper wall inset another 2 in.\n*7-ft upper opening height retained as a sketch assumption. Crane/hoist clearance, guards, sliding-door hardware, column/foundation forces and roof framing remain to design.\nLow hip cap retained schematically: 18-in rise above 227.25-in roof datum. North edge ends at setback envelope; no additional north eave beyond it.',fontsize=10)
fig.savefig(P/'north-loading-jib.png',dpi=145);fig.savefig(P/'north-loading-jib.pdf')
(P/'basis.json').write_text(json.dumps(dict(units='inches',existing_setback=82,assumed_required_setback=60,extension=22,upper_wall_north_offset=0,outer_edge_north_offset=22,pivot=[float(x) for x in pivot],boom_radius=96,opening_west=west,opening_east=east,opening_height_assumed=84,column_width_placeholder=6,structural_design=False),indent=2))
print('Created schematic PNG and PDF')
