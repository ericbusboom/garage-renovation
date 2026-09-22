"""Owner-corrected roof projection and no-interior-post support concept."""
from pathlib import Path
import os,json,math
os.environ['MPLCONFIGDIR']='/private/tmp/garage-sequence-mpl'
import numpy as np
import matplotlib;matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon,Rectangle
from matplotlib.lines import Line2D
P=Path(__file__).resolve().parent
W,L,H,R=249.5,249.,98.5,60.;XE=224.25;YT1=69.75;depth=36.
def roof(x,y):
 x,y=np.broadcast_arrays(np.asarray(x,float),np.asarray(y,float));return H+R*np.minimum.reduce([x/(W/2),(W-x)/(W/2),y/(L/2),(L-y)/(L/2),np.ones_like(x)])
def new(y):return np.minimum(106.5+(np.asarray(y)+63)*math.tan(math.pi/6),227.25)
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':11})
fig,axs=plt.subplots(2,1,figsize=(13,11),gridspec_kw={'height_ratios':[1.35,1]},layout='constrained')
ax=axs[0];ax.add_patch(Rectangle((0,0),L,H,facecolor='#eceeed',edgecolor='#9aa4a5',lw=1));ax.add_patch(Polygon([(0,H),(L/2,H+R),(L,H)],fc='#d4dcdf',ec='#4b5b63',lw=2.5,zorder=2))
y=np.linspace(0,L,2001);z=roof(XE,y);ax.plot(y,z,c='#242f39',lw=4,ls=(0,(1.2,2)),zorder=5)
ys=np.array([-21.25,0,35,69.75,110,146.145,185,220,253]);top=new(ys);bot=top-depth
ax.plot(ys,top,c='#19796e',lw=3);ax.plot(ys,bot,c='#19796e',lw=3)
for i in range(len(ys)-1):ax.plot([ys[i],ys[i+1]],[bot[i] if i%2==0 else top[i],top[i+1] if i%2==0 else bot[i+1]],c='#19796e',lw=1.3)
for label,y0 in [('S2',-21.25),('S3',0),('N2',253)]:
 b=float(new(y0)-depth);ax.plot([y0,y0],[0,b],c='#365e87',lw=5,zorder=6);ax.text(y0,-10,label,ha='center',color='#365e87',weight='bold');ax.add_patch(Rectangle((y0-5,-4),10,4,fc='#aaa094',ec='none'))
zjoin=float(new(YT1)-depth);ax.scatter([YT1],[zjoin],s=85,c='#c2682d',zorder=7);ax.annotate('T1 joins T-E here\nNo column below this joint',(YT1,zjoin),xytext=(36,210),arrowprops=dict(arrowstyle='->',color='#a35524'),color='#a35524',fontsize=11)
ax.annotate('Existing roof: central peak\n5 ft above wall tops',(L/2,H+R),xytext=(139,170),arrowprops=dict(arrowstyle='->',color='#4b5b63'),fontsize=10,color='#4b5b63')
ax.annotate('Thick dotted line: actual old-roof\nheight along T-E at x = 224.25 in',(190,float(roof(XE,190))),xytext=(92,65),arrowprops=dict(arrowstyle='->',color='#242f39'),fontsize=10,color='#242f39')
te_height=float(roof(XE,L/2))
ax.annotate('',(205,H),(205,te_height),arrowprops=dict(arrowstyle='<->',color='#242f39'),zorder=9)
ax.annotate(f'Old roof at T-E: {te_height:.2f} in above slab\n9 ft 2⅝ in approx. · {te_height-H:.2f} in above walls',(205,te_height),xytext=(112,35),arrowprops=dict(arrowstyle='->',color='#242f39'),fontsize=10,color='#242f39',bbox=dict(fc='white',ec='none',alpha=.9))
ax.text(182,234,'T-E roof-first truss',ha='center',color='#19796e',weight='bold');ax.annotate('',(273,H),(273,H+R),arrowprops=dict(arrowstyle='<->'));ax.text(280,H+R/2,'60 in roof rise',rotation=90,va='center',fontsize=10)
ax.set(xlim=(-35,300),ylim=(-18,244),xlabel='North from south wall (inches)',ylabel='Height above nominal slab (inches)',title='Looking west at the east side • full existing roof outline, with T-E section dotted');ax.spines[['top','right']].set_visible(False);ax.grid(axis='y',alpha=.12)
ax=axs[1];corners=[(0,0),(W,0),(W,L),(0,L)];ax.add_patch(Rectangle((0,0),W,L,fc='#edf0f1',ec='#59666e',lw=2))
for x,y in corners:ax.plot([x,W/2],[y,L/2],c='#98a5aa',lw=1)
ax.scatter([W/2],[L/2],s=30,c='#59666e');ax.text(W/2-8,L/2+8,'Old roof peak',ha='right',fontsize=10,color='#59666e')
ax.plot([XE,XE],[-21.25,253],c='#19796e',lw=4);ax.text(XE+8,170,'T-E · continuous S2–S3–N2',rotation=90,va='center',color='#19796e',fontsize=10,weight='bold')
ax.plot([-32,XE],[YT1,YT1],c='#c2682d',lw=3);ax.text(95,YT1+9,'T1 · roof-level connection to T-E',ha='center',color='#a35524',fontsize=10,weight='bold')
for label,x,y in [('S2',XE,-21.25),('S3',XE,0),('N2',XE,253),('W2',-32,YT1)]:
 ax.scatter([x],[y],c='#365e87',s=75,zorder=5,marker='s');ax.annotate(label,(x,y),xytext=(-28,0) if label=='W2' else (8,-10 if label=='S2' else 6),textcoords='offset points',color='#365e87',weight='bold',fontsize=10)
ax.scatter([XE],[YT1],s=80,fc='white',ec='#c2682d',lw=2,zorder=6);ax.annotate('Connection only',(XE,YT1),xytext=(260,55),arrowprops=dict(arrowstyle='->',color='#a35524'),fontsize=10,color='#a35524')
ax.text(110,277,'NORTH ↑',ha='center',weight='bold');ax.set(xlim=(-70,355),ylim=(-45,290));ax.set_aspect('equal');ax.axis('off');ax.set_title('Plan • no new interior post under T1',loc='left')
fig.suptitle('Corrected roof shape and T-E support arrangement',fontsize=20,weight='bold');fig.supxlabel('Existing roof: single-point pyramid, no ridge segment. Footprint retained at 249.5 × 249 in pending dimension reconciliation.\nGreen truss uses the earlier 36-in envelope for illustration only; it has not been sized for T1’s transferred load. Eaves remain unmeasured.',fontsize=10)
fig.savefig(P/'roof-and-TE-corrected.png',dpi=160);fig.savefig(P/'roof-and-TE-corrected.pdf')
(P/'basis.json').write_text(json.dumps(dict(units='inches',existing_roof=dict(width=W,length=L,wall_height=H,rise=R,ridge_length=0),TE=dict(x=XE,y_start=-21.25,y_end=253,supports=['S2','S3','N2'],illustrative_depth=depth),T1=dict(y=YT1,west_support='W2',east_support='connection to T-E',interior_post=False),checks=dict(old_roof_peak=H+R,old_roof_height_along_TE_max=float(roof(XE,L/2)),T1_joint_elevation=zjoin,TE_support_distance_S3_N2=253)),indent=2))
print('Corrected diagram and PDF created')
