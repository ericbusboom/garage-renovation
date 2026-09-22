import os
os.environ['MPLCONFIGDIR']='/private/tmp/garage-mpl'
import matplotlib;matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import json
from pathlib import Path
p=Path(__file__).resolve().parent;r=json.loads((p/'results.json').read_text());m=json.loads((p/'analysis-model.json').read_text())
fig,ax=plt.subplots(figsize=(8.8,7.1));ax.add_patch(Rectangle((0,0),249.5,249,fill=False,edgecolor='#888',lw=3));ax.add_patch(Rectangle((0,72),224.25,183,facecolor='#e2edf1',alpha=.7));
for e in m['elements']:
 a,b=[m['nodes'][i] for i in e['ij']]
 if abs(a[2]-98.5)<.01 and abs(b[2]-98.5)<.01:ax.plot([a[0],b[0]],[a[1],b[1]],color='#344f60',lw=1.2)
for name,i in m['bases'].items():
 x,y,_=m['nodes'][i];v=r['cases']['service storage bands']['columns'][name]['P_lb'];ax.scatter([x],[y],color='#a64f27' if name=='S1' else '#126080',s=45,zorder=5);ax.annotate(f'{name}: {v/1000:.2f} kip', (x,y),xytext=(5,7 if name not in ['W4','N1','N2'] else -15),textcoords='offset points',fontsize=9)
for name,y in [('T-SO',-63),('T-S',0),('T1',69.75),('B2',185),('B3',249),('T-N',253)]:
 if name not in ['B3','T-N']:ax.text(70,y+5,name,fontsize=9)
ax.text(85,130,'LOFT FLOOR',color='#456');ax.text(100,277,'NORTH ↑',weight='bold');ax.set(xlim=(-80,315),ylim=(-85,295),xlabel='East from west wall (inches)',ylabel='North from south wall (inches)',title='Service column reactions • perimeter storage case');ax.set_aspect('equal');ax.grid(alpha=.15);fig.tight_layout();fig.savefig(p/'reaction-plan.png',dpi=160)
