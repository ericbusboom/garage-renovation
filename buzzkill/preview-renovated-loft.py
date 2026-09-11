import os,json
from pathlib import Path
os.environ['MPLCONFIGDIR']='/tmp/renovated-loft-mpl'
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection
from matplotlib.patches import Rectangle
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
P=Path(__file__).resolve().parent;data=json.loads((P/'renovated-loft-mesh.json').read_text())['objects']
fig=plt.figure(figsize=(18,11),layout='constrained');ax=fig.add_subplot(121,projection='3d');plan=fig.add_subplot(122)
for o in data:
 v=[[x/25.4 for x in p] for p in o.get('vertices',[])];t=o.get('triangles',[])
 if t:ax.add_collection3d(Poly3DCollection([[v[i] for i in tri] for tri in t],facecolors=o['color'][:3],alpha=o.get('opacity',1),edgecolors='none'))
 for line in o.get('lines',[]):ax.plot(*zip(*[[x/25.4 for x in p] for p in line]),color='#536979',lw=.55,alpha=.6)
 n=o['name']
 if t and (n.startswith('Renovated') or n in ['ProposedT1Future','ProposedB2Future','ProposedTN','ProposedTW','ProposedTE']):
  plan.add_collection(PolyCollection([[[v[i][0],v[i][1]] for i in tri] for tri in t],facecolors=o['color'][:3],alpha=o.get('opacity',1),edgecolors='none'))
plan.add_patch(Rectangle((0,0),224.25,72,facecolor='#f1f3f5',edgecolor='#84929e',linestyle='--',lw=1))
plan.text(112,36,'OPEN SOUTH\nFirst 6 ft',ha='center',va='center',fontsize=14,color='#526570')
plan.text(112,137,'MAIN LOFT DECK\nFinished floor 120.75 in',ha='center',va='center',fontsize=12,bbox=dict(facecolor='white',alpha=.8,edgecolor='none'))
plan.text(-16,135,'WEST WALKWAY DISTINCT · NO DECK',rotation=90,ha='center',va='center',fontsize=10,color='#526570')
plan.text(112,258,'Optional loading ledge hidden',ha='center',fontsize=10,color='#526570')
for y,text in [(69.75,'T1 future beam'),(185,'B2 future beam'),(249,'T-N')]:plan.text(230,y,text,ha='left',va='center',fontsize=10)
ax.set(xlim=(-45,260),ylim=(-70,275),zlim=(0,253),xlabel='East (in)',ylabel='North (in)',zlabel='Height (in)',title='Proposed frame and renovated loft · existing hidden');ax.set_box_aspect((305,345,253));ax.view_init(29,-122)
plan.set(xlim=(-45,300),ylim=(-10,275),aspect='equal',xlabel='East (in)',ylabel='North (in)',title='Loft plan · 30 north–south joists');plan.grid(alpha=.15)
fig.suptitle('Renovated loft · native editable CAD',fontsize=22)
fig.supxlabel('0.75in deck shown 60% transparent · 2×8 nominal joists at 16in centers · steel retained · joist connections and optional ledge support unresolved',fontsize=12)
fig.savefig(P/'Proposed-Garage-renovated-loft.png',dpi=140);fig.savefig(P/'Proposed-Garage-overlay.png',dpi=140)
