from pathlib import Path
import os,json,math
os.environ['MPLCONFIGDIR']='/private/tmp/garage-sequence-mpl'
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
P=Path(__file__).resolve().parent
W,L,H,R=249.5,249.,98.5,60.
XW,XE,Y=-32.,224.25,69.75
TOP=106.5+(Y+63)*math.tan(math.pi/6)
DEPTH=36.; LOW=TOP-DEPTH
def old(x):
 return H+R*np.minimum.reduce([x/(W/2),(W-x)/(W/2),np.full_like(x,Y/(L/2)),np.full_like(x,(L-Y)/(L/2))])
xs=np.linspace(0,W,600);roof=old(xs)
nodes=np.linspace(XW,XE,5)
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10})
fig,axs=plt.subplots(2,1,figsize=(14,11),layout='constrained')
for stage,ax in enumerate(axs,1):
 ax.set(xlim=(-55,294),ylim=(88,204),xlabel='East from west garage wall (in)',ylabel='Elevation above nominal slab (in)')
 ax.spines[['top','right']].set_visible(False)
 ax.axhline(H,c='#aaa',lw=1);ax.text(252,H,'Wall top\n98.5 in',fontsize=9,va='center')
 ax.plot([0,W/2,W],[H,H+R,H],color='#9aa4aa',ls='--',lw=1)
 if stage==1:
  ax.fill_between(xs,H,roof,color='#e2e5e7');ax.plot(xs,roof,color='#3d4850',ls=(0,(1,1.7)),lw=3.5)
  ax.annotate('Actual old roof at T1 station\nmaximum 132.11 in = 11 ft 0.11 in',(105,132.114),xytext=(5,114),arrowprops={'arrowstyle':'->'},fontsize=10)
  ax.text(72,161,'Thin dashed outline: full old-roof silhouette',color='#7f898f',fontsize=9)
 else:
  ax.plot(xs,roof,color='#bbb',ls=':',lw=1);ax.text(64,131,'Old roof removed',color='#888')
  ax.add_patch(Rectangle((0,112),XE,8,facecolor='#efbd55',alpha=.2))
  ax.plot([XW,XE],[112,112],c='#246e9c',lw=4)
  ax.plot([0,XE],[120,120],c='#b17d16',lw=1.5,ls='--')
  for xx in nodes:
   ax.plot([xx,xx],[112,LOW],c='#b26d2c',lw=2)
   ax.scatter([xx],[LOW],c='#b26d2c',s=25,zorder=5)
  ax.text(15,104,'Later: suspended W floor / trolley beam • underside 112 in (9 ft 4 in)',color='#246e9c')
  ax.annotate('Floor top 120 in (10 ft)\n8-in total floor zone',(190,120),xytext=(182,91),arrowprops={'arrowstyle':'->'},color='#9d7119',fontsize=9)
  ax.annotate('Hangers connect at upper-truss panel points\nW section depth and hanger connections TBD',(32,140),xytext=(-45,192),arrowprops={'arrowstyle':'->','color':'#b26d2c'},color='#995921')
 for xx,name in [(XW,'T-W'),(XE,'T-E')]:
  ax.plot([xx,xx],[98.5,TOP],c='#8296a1',lw=8,alpha=.35)
  ax.text(xx,89,name+'\nside truss',ha='center',fontsize=9)
 for zz in [LOW,TOP]:ax.plot([XW,XE],[zz,zz],c='#238473',lw=3)
 for xx in nodes:ax.plot([xx,xx],[LOW,TOP],c='#238473',lw=1.7)
 for i in range(4):
  ax.plot(nodes[i:i+2],[TOP,LOW] if i<2 else [LOW,TOP],c='#238473',lw=1.7)
 ax.annotate('',(240,LOW),(240,TOP),arrowprops={'arrowstyle':'<->'})
 ax.text(245,(LOW+TOP)/2,'36 in\nconcept depth',va='center',fontsize=9)
 ax.annotate('',(XW,200),(XE,200),arrowprops={'arrowstyle':'<->'})
 ax.text((XW+XE)/2,201,'T1 span: 256.25 in = 21 ft 4¼ in',ha='center',fontsize=10)
 if stage==1:
  ax.text(-45,190,'Roof underside / upper envelope: 183.14 in (15 ft 3.14 in)',fontsize=10,color='#238473')
  ax.annotate('',(143,roof.max()),(143,LOW),arrowprops={'arrowstyle':'<->'})
  ax.text(149,139,'15.03 in nominal clearance',fontsize=9)
  ax.text(2,LOW+3,'Upper truss lower envelope: 147.14 in (12 ft 3.14 in)',color='#238473',fontsize=9)
 ax.set_title(('STAGE 1 — Complete upper T1 truss supports roof; old roof remains' if stage==1 else 'STAGE 2 — Keep upper T1; add hangers and lower floor beam after roof removal'),loc='left',weight='bold',pad=22)
 ax.grid(axis='y',alpha=.1)
fig.suptitle('T1: permanent upper truss + later suspended loft beam',fontsize=20,weight='bold')
fig.supxlabel('Concept geometry, not member sizing. Chord lines show envelopes; web layout is schematic. No interior post.\nUpper truss and T-E/T-W connections must carry final roof + loft + trolley loads; check each erection stage separately.\nPermanent upper lower chord sits 27.14 in above the loft surface at T1: this remains an obstruction across the loft.',fontsize=10)
fig.savefig(P/'T1-two-stage.png',dpi=150);fig.savefig(P/'T1-two-stage.pdf')
(P/'basis.json').write_text(json.dumps(dict(units='inches',T1_y=Y,span=XE-XW,upper_envelope=TOP,lower_envelope=LOW,concept_depth=DEPTH,old_roof_max=float(roof.max()),nominal_clearance=LOW-float(roof.max()),floor_bottom=112,floor_top=120,permanent_obstruction_above_floor=LOW-120,member_sizes_verified=False),indent=2))
print('Generated T1 two-stage concept')
