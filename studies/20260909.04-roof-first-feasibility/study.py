"""Envelope feasibility only. No member sizing or erection-load rating."""
from pathlib import Path
import json,math,os
os.environ['MPLCONFIGDIR']='/private/tmp/garage-sequence-mpl'
import numpy as np
import matplotlib;matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
P=Path(__file__).resolve().parent
H=98.5;W=249.5;Y=69.75;END=224.25;WEST=-32.;DEPTH=36.
def new(y):return np.minimum(106.5+(np.asarray(y)+63)*math.tan(math.pi/6),227.25)
def old(x,y,L,R,ridge):
 x,y=np.broadcast_arrays(np.asarray(x,dtype=float),np.asarray(y,dtype=float));return H+R*np.minimum.reduce([x/(W/2),(W-x)/(W/2),y/((L-ridge)/2),(L-y)/((L-ridge)/2),np.ones_like(x)])
cases=[dict(name='Earlier wall footprint + 18-in ridge',L=249.,R=58.,ridge=18.),dict(name='Linked-task provisional pyramid',L=286.25,R=58.,ridge=0.),dict(name='Earlier 60-in roof rise sensitivity',L=249.,R=60.,ridge=18.)]
xx=np.linspace(0,W,3001);top=float(new(Y));bottom=top-DEPTH;checks=[]
for c in cases:
 peak=float(old(xx,Y,c['L'],c['R'],c['ridge']).max());checks.append(dict(**c,T1_old_roof_max=peak,new_roof_underside=top,total_gap=top-peak,roof_truss_bottom=bottom,remaining_vertical_gap=bottom-peak,TN_outside_wall=253-c['L']))
(P/'checks.json').write_text(json.dumps(dict(units='inches',wall_top=H,T1_y=Y,new_truss_overall_depth=DEPTH,assumed_interior_post_x=END,assumed_west_post_x=WEST,span=END-WEST,cases=checks),indent=2))
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10})
fig,axs=plt.subplots(2,1,figsize=(13,10),layout='constrained');c=cases[0];z=old(xx,Y,c['L'],c['R'],c['ridge']);ax=axs[0]
ax.fill_between(xx,0,H,color='#e4e7e7');ax.fill_between(xx,H,z,color='#c1c9cc');ax.plot(xx,z,c='#5e6d74',lw=2)
# The envelope, rather than these arbitrary schematic diagonals, is the test geometry.
ax.add_patch(Rectangle((WEST,bottom),END-WEST,DEPTH,fill=False,ec='#207f78',lw=3));cuts=np.linspace(WEST,END,7)
for i in range(6):ax.plot([cuts[i],cuts[i+1]],[bottom if i%2==0 else top,top if i%2==0 else bottom],c='#207f78',lw=1.5)
for x in [WEST,END]:
 ax.plot([x,x],[0,bottom],c='#4a698f',lw=5);ax.add_patch(Rectangle((x-9,-12),18,12,fc='#b5a696',ec='#716354'))
ax.scatter([END],[float(old(END,Y,c['L'],c['R'],c['ridge']))],s=140,fc='none',ec='#c35d32',lw=2,zorder=9)
ax.text(END-4,70,'Interior post*\nthrough local roof opening',ha='right',color='#365b82');ax.text(WEST-3,65,'Existing west\ncolumn line',ha='right',color='#365b82');ax.plot([0,END],[H,H],c='#c66a38',ls='--',lw=2);ax.text(40,H-9,'Future floor / trolley framing — install later',color='#aa5129')
ax.annotate('',(125,bottom),(125,float(z.max())),arrowprops=dict(arrowstyle='<->'));ax.text(133,(bottom+z.max())/2,f"{checks[0]['remaining_vertical_gap']:.1f} in\nnominal clearance",va='center');ax.text(90,top+6,'Roof-first T1-R: COMPLETE 36-in-deep truss',ha='center',color='#207f78',weight='bold');ax.text(100,bottom+12,'All chords and web members above retained roof',ha='center',fontsize=9,color='#207f78')
ax.set(xlim=(-78,275),ylim=(-20,205),xlabel='East from west wall (in)',ylabel='Elevation above nominal slab (in)',title='T1 section looking north · y = 69.75 in');ax.grid(alpha=.1)
ax=axs[1];ys=np.linspace(0,249,1501);zz=old(W/2,ys,249,58,18);ax.fill_between(ys,H,zz,color='#c1c9cc');ax.plot(ys,zz,c='#5e6d74',lw=2);yny=np.linspace(-63,253,1500);ax.plot(yny,new(yny),c='#207f78',lw=3);ax.plot(yny,new(yny)-36,c='#207f78',ls=':',lw=1)
ax.plot([Y,Y],[bottom,top],c='#247b92',lw=7);ax.plot([-10,-10],[H,float(new(-10))],c='#b27731',lw=4);ax.plot([253,253],[H,227.25],c='#ad5269',lw=4)
ax.text(Y+5,top+6,'T1-R raised above old roof',color='#247b92');ax.text(-15,170,'T-S may move\noutside old eaves',ha='center',fontsize=9,color='#9c6b28');ax.text(253,235,'T-N*',ha='center',color='#ad5269');ax.text(122,120,'Old roof retained during roof construction',ha='center',color='#56636a');ax.axhline(H,c='#777',ls='--',lw=1)
ax.set(xlim=(-70,285),ylim=(80,248),xlabel='North from south wall (in)',ylabel='Elevation (in)',title='North–south section · earlier 249-in wall footprint shown');ax.grid(alpha=.1)
fig.suptitle('Build the roof first: a raised roof truss, then the loft',fontsize=19,weight='bold');fig.supxlabel('*Interior post position is an illustration, not a selected footing location. T-N at y=253 is exterior only with the 249-in wall footprint.\nEaves, thickness, connection projections, movement and erection workspace are not surveyed. No steel sizes are assigned.',fontsize=10)
fig.savefig(P/'roof-first-concept.png',dpi=160);fig.savefig(P/'roof-first-sections.pdf');print(json.dumps(checks,indent=2))
