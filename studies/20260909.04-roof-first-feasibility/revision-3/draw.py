"""T-E horizontal lower edge raised to owner-requested 112 in datum."""
from pathlib import Path
import os,json,math
os.environ['MPLCONFIGDIR']='/private/tmp/garage-sequence-mpl'
import numpy as np
import matplotlib;matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle,Polygon
P=Path(__file__).resolve().parent
W,L,H,R=249.5,249.,98.5,60.;XE=224.25;YT1=69.75;BOTTOM=112.;FLOOR=120.
def old(x,y):
 x,y=np.broadcast_arrays(np.asarray(x,float),np.asarray(y,float));return H+R*np.minimum.reduce([x/(W/2),(W-x)/(W/2),y/(L/2),(L-y)/(L/2),np.ones_like(x)])
def new(y):return np.minimum(106.5+(np.asarray(y)+63)*math.tan(math.pi/6),227.25)
plateau=-63+(227.25-106.5)/math.tan(math.pi/6)
ys=np.array([-21.25,0,69.75,126,plateau,185,253]);z=new(ys)
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10})
fig=plt.figure(figsize=(13,10),layout='constrained');gs=fig.add_gridspec(2,2,height_ratios=[1.8,1]);ax=fig.add_subplot(gs[0,:])
ax.add_patch(Rectangle((0,0),L,H,fc='#edefee',ec='#aaa',lw=1));ax.add_patch(Polygon([(0,H),(L/2,H+R),(L,H)],fc='#e2e7e9',ec='#596a73',lw=2.5))
y=np.linspace(0,L,1200);ax.plot(y,old(XE,y),color='#2e3840',lw=3.8,ls=(0,(1.2,2)),zorder=6)
ax.plot(ys,z,c='#258678',lw=3);ax.plot([-21.25,253],[BOTTOM,BOTTOM],c='#2476a8',lw=3,zorder=7)
for a,b,za,zb in zip(ys[:-1],ys[1:],z[:-1],z[1:]):ax.plot([a,b],[BOTTOM,zb],c='#258678',lw=1.5)
for y0,zz in zip(ys,z):ax.plot([y0,y0],[BOTTOM,zz],c='#258678',lw=1.5)
ax.fill_between([72,253],[BOTTOM,BOTTOM],[FLOOR,FLOOR],color='#edb849',alpha=.3,zorder=4);ax.plot([72,253],[FLOOR,FLOOR],c='#ad7c16',ls='--',lw=1.8,zorder=8)
for name,y0 in [('S2',-21.25),('S3',0),('N2',253)]:ax.plot([y0,y0],[0,BOTTOM],c='#4a6590',lw=4);ax.text(y0,-9,name,ha='center',color='#4a6590',weight='bold')
ax.scatter([YT1],[BOTTOM],s=65,c='#bc622c',zorder=9);ax.annotate('T1 connection station\nNo interior column',(YT1,BOTTOM),xytext=(15,194),arrowprops=dict(arrowstyle='->',color='#b05b26'),color='#b05b26')
ax.annotate('Old roof: full pyramid outline\n5 ft rise to central point',(124.5,158.5),xytext=(138,170),arrowprops=dict(arrowstyle='->',color='#596a73'),color='#596a73')
ax.text(173,237,'T-E: restored full-depth truss geometry',color='#258678',ha='center',weight='bold',fontsize=12)
ax.annotate('Bottom of loft / T-E lower edge\n112 in = 9 ft 4 in',(205,BOTTOM),xytext=(122,55),arrowprops=dict(arrowstyle='->',color='#2476a8'),color='#2476a8',weight='bold')
ax.annotate('Floor top: 120 in = 10 ft',(210,FLOOR),xytext=(162,88),arrowprops=dict(arrowstyle='->',color='#ad7c16'),color='#936b1c')
ax.annotate('Thick dotted line: old roof at T-E\n110.64 in = about 9 ft 2⅝ in',(42,float(old(XE,42))),xytext=(5,25),arrowprops=dict(arrowstyle='->',color='#2e3840'),color='#2e3840')
ax.annotate('',(277,BOTTOM),(277,227.25),arrowprops=dict(arrowstyle='<->'));ax.text(282,168,'115.25 in maximum truss depth',rotation=90,va='center')
ax.set(xlim=(-32,301),ylim=(-17,248),xlabel='North from south wall (in)',ylabel='Elevation above nominal slab (in)',title='East-side elevation • bottom chord horizontal; upper chord follows proposed roof');ax.grid(axis='y',alpha=.13);ax.spines[['top','right']].set_visible(False)
ax=fig.add_subplot(gs[1,0]);ax.axhline(BOTTOM,color='#2476a8',lw=2);ax.axhline(FLOOR,color='#ad7c16',lw=2,ls='--');ax.axhline(float(old(XE,L/2)),c='#2e3840',lw=3.5,ls=(0,(1.2,2)));ax.fill_between([0,1],BOTTOM,FLOOR,fc='#edb849',alpha=.2)
ax.text(.03,120.6,'Floor top: 120 in',color='#936b1c');ax.text(.03,112.4,'Loft underside: 112 in',color='#2476a8');ax.text(.03,108.6,'Old roof at T-E: 110.64 in',color='#2e3840');ax.annotate('',(.82,BOTTOM),(.82,FLOOR),arrowprops=dict(arrowstyle='<->'));ax.text(.86,116,'8 in',va='center');ax.annotate('',(.6,float(old(XE,L/2))),(.6,BOTTOM),arrowprops=dict(arrowstyle='<->'));ax.text(.65,110.9,'1.36 in',fontsize=9)
ax.set(xlim=(0,1),ylim=(107,123),ylabel='Elevation (in)',title='Floor levels and nominal line clearance');ax.set_xticks([]);ax.spines[['top','right','bottom']].set_visible(False)
ax=fig.add_subplot(gs[1,1]);x=np.linspace(XE-7,XE+7,300);zz=old(x,L/2);ax.plot(x-XE,zz,c='#2e3840',lw=3,ls=(0,(1.2,2)));ax.add_patch(Rectangle((-3,BOTTOM),6,6,fc='#bcd7e7',ec='#2476a8',lw=2));ax.axvline(0,ls=':',c='#aaa');ax.text(0,115,'Example 6-in-wide chord\nwidth check only',ha='center',fontsize=9);ax.annotate('Old roof at west edge:\n112.09 in',(-3,float(old(XE-3,L/2))),xytext=(-6.7,106.8),arrowprops=dict(arrowstyle='->'),fontsize=9)
ax.set(xlim=(-7,7),ylim=(105.5,120),xlabel='Offset from T-E: west ← → east (in)',ylabel='Elevation (in)',title='Actual member width can consume the gap');ax.spines[['top','right']].set_visible(False)
fig.suptitle('T-E with loft underside at 9 ft 4 in',fontsize=20,weight='bold');fig.supxlabel('Geometry revision only: member sizes and web/connection details require reanalysis. Footprint retained at 249.5 × 249 in.\nThe 1.36-in gap is at the T-E line, not a verified construction clearance. Floor-height T1 and the full loft still intersect the old roof elsewhere.',fontsize=10)
fig.savefig(P/'TE-raised-loft.png',dpi=160);fig.savefig(P/'TE-raised-loft.pdf')
(P/'basis.json').write_text(json.dumps(dict(units='inches',footprint=[W,L],old_roof_rise=R,old_roof_ridge=0,wall_top=H,TE_x=XE,TE_bottom=BOTTOM,floor_top=FLOOR,floor_zone=FLOOR-BOTTOM,TE_stations=ys.tolist(),TE_top=z.tolist(),TE_supports=['S2','S3','N2'],interior_post=False,nominal_clearance=BOTTOM-float(old(XE,L/2)),old_roof_at_TE=float(old(XE,L/2)),example_6in_chord_west_edge_roof=float(old(XE-3,L/2)),old_roof_at_T1_max=float(old(W/2,YT1)),notes='Restores earlier T-E horizontal-bottom, sloped-top panel layout between S2 and N2. Architectural lower edge is a surface datum, not an analytical section centroid. No previous section capacities are reaffirmed.'),indent=2))
print('Created raised-loft drawing and PDF')
