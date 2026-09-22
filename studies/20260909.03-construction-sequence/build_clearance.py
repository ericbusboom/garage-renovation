"""Geometric screening only; no structural sizing or measured framing implied."""
from pathlib import Path
import json, math
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT=Path(__file__).resolve().parents[1]
OUT=Path(__file__).resolve().parent
p=json.loads((OUT/'existing-roof-parameters.json').read_text())
b=json.loads((ROOT/'structural-analysis-v5/inputs/garage-model.json').read_text())['basis']
W,L,H=p['width'],p['length'],p['wall_height']
def old(x,y):
    return H+p['roof_rise']*np.minimum.reduce([np.asarray(x)/ (W/2)+np.zeros_like(y), (W-np.asarray(x))/(W/2)+np.zeros_like(y),np.asarray(y)/((L-p['ridge_length'])/2)+np.zeros_like(x),(L-np.asarray(y))/((L-p['ridge_length'])/2)+np.zeros_like(x),np.ones(np.broadcast(np.asarray(x),np.asarray(y)).shape)])
def new(y):
    return np.minimum(b['roof_start_underside']+(np.asarray(y)-b['roof_start_y'])*math.tan(math.pi/6),b['roof_plateau_underside'])
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':11})
fig,axs=plt.subplots(2,1,figsize=(11,9))
fig.suptitle('Roof-first construction: where the current framing conflicts',fontsize=17,x=.07,ha='left')
for ax in axs:
    ax.set_ylim(78,244);ax.set_ylabel('Elevation above slab (in)')
    ax.spines[['top','right']].set_visible(False)
    ax.grid(axis='y',alpha=.17)
    ax.axhline(H,color='#56636a',lw=1,ls=':')
    ax.axhline(b['floor'],color='#56636a',lw=1,ls='--')
x=np.linspace(0,W,1001);y=69.75;z=old(x,y);hi=float(new(y))
ax=axs[0]
ax.fill_between(x,H,z,color='#cbd1d4',label='Existing roof envelope (not solid material)')
ax.plot(x,z,color='#58656d',lw=2)
ax.plot([0,224.25],[H,H],color='#bb643e',lw=3)
ax.plot([0,224.25],[hi,hi],color='#bb643e',lw=3)
for xx in np.linspace(0,224.25,7):ax.plot([xx,xx],[H,hi],color='#bb643e',lw=1.5)
ax.plot([0,W],[hi,hi],color='#267777',lw=2,label='Proposed roof underside')
ax.annotate('',(125,hi),(125,float(z.max())),arrowprops={'arrowstyle':'<->','color':'#222'})
ax.text(132,(hi+z.max())/2,f'{hi-z.max():.1f} in\ngeometric gap',va='center')
ax.text(8,220,'T1 crosses the old roof; its lower chord and webs cannot go in intact.',fontsize=11)
ax.set_xlim(-10,260);ax.set_title('T1 section · looking north · Y = 69.75 in',loc='left',fontsize=12)
ax.set_xlabel('West → east (in)')
y=np.linspace(0,L,1001);z=old(np.full_like(y,224.25),y)
ax=axs[1]
ax.fill_between(y,H,z,color='#cbd1d4');ax.plot(y,z,color='#58656d',lw=2)
yy=np.linspace(-63,253,500)
ax.plot(yy,new(yy),color='#267777',lw=2)
ax.plot([-63,253],[H,H],color='#bb643e',lw=3)
for v in [-63,-21.25,0,69.75,126,146.145,185,253]:ax.plot([v,v],[H,float(new(v))],color='#bb643e',lw=1.5)
ax.text(-55,218,'T-E sits 25¼ in inside the east wall.',fontsize=11)
ax.text(-55,201,'Old roof now extends north of the unchanged proposed frame.',fontsize=11)
ax.axvline(253,color='#bb643e',ls=':',lw=1)
ax.set_xlim(-70,L+10);ax.set_title('T-E section · looking west · X = 224.25 in',loc='left',fontsize=12)
ax.set_xlabel('South → north (in)')
from matplotlib.lines import Line2D
fig.legend(handles=[Line2D([0],[0],color='#58656d',lw=3,label='Existing roof surface'),Line2D([0],[0],color='#267777',lw=3,label='New roof underside'),Line2D([0],[0],color='#bb643e',lw=3,label='Current full-depth truss'),Line2D([0],[0],color='#56636a',ls='--',label='Future loft datum')],loc='lower center',ncol=2,bbox_to_anchor=(.5,.047),frameon=False)
fig.text(.07,.02,'Corrected pyramid • provisional 23 ft 10¼ in length • eaves, connections and working clearances excluded.',fontsize=10,color='#555')
fig.tight_layout(rect=(.02,.12,.98,.95),h_pad=2)
fig.savefig(OUT/'roof-clearance.png',dpi=170)
fig.savefig(OUT/'roof-clearance.pdf')
checks={'T1_old_roof_max_in':float(old(np.array([W/2]),np.array([69.75]))[0]),'T1_new_roof_underside_in':float(new(69.75)),'T1_geometric_gap_in':hi-float(old(np.array([W/2]),np.array([69.75]))[0]),'north_post_row_beyond_wall_in':253-L,'east_truss_inside_wall_in':W-224.25,'south_post_to_outer_beam_offset_in':-21.25-(-63)}
(OUT/'clearance-check.json').write_text(json.dumps(checks,indent=2)+'\n')
print(json.dumps(checks,indent=2))
