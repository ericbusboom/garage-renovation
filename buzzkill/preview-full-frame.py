import os,json
from pathlib import Path
os.environ['MPLCONFIGDIR']='/tmp/fullframe-mpl'
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection
from matplotlib.patches import Rectangle
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
P=Path(__file__).resolve().parent
D=json.loads((P/'proposed-overlay-full.json').read_text())['objects']; reg=json.loads((P/'proposed-overlay-member-register.json').read_text());newnames={r['object'] for r in reg['members']}
fig=plt.figure(figsize=(19,15),layout='constrained');ax=fig.add_subplot(231,projection='3d')
for o in D:
 v=[[x/25.4 for x in p] for p in o.get('vertices',[])];tris=o.get('triangles',[]);old=o['name'] not in newnames
 if tris:ax.add_collection3d(Poly3DCollection([[v[i] for i in t] for t in tris],facecolors='#acb0b7' if old else o['color'][:3],alpha=.12 if old else 1,edgecolors='none'))
 for line in o.get('lines',[]):ax.plot(*zip(*[[v/25.4 for v in pt] for pt in line]),color='#536777',lw=.45,alpha=.7)
ax.set(xlim=(-45,260),ylim=(-70,275),zlim=(0,250),xlabel='East (in)',ylabel='North (in)',zlabel='Height (in)',title='Full proposed frame over existing garage');ax.set_box_aspect((305,345,250));ax.view_init(24,-125)
supports={'TS':['ProposedColumnW1','ProposedColumnS3'],'T1':['ProposedColumnW2','ProposedT1Future']+[f'FutureT1Hanger{i}' for i in range(1,6)],'TW':['ProposedColumn'+s for s in ['SW0','W1','W2','W3','W4']]+['TWBalconyHeader'],'TE':['ProposedColumn'+s for s in ['S2','S3','N2']],'TN':['ProposedColumnW4','ProposedNorthPostUW','ProposedColumnN2','TNUpperEastJamb','TNLoadingHeader']}
for index,k in enumerate(['TS','T1','TW','TE','TN'],2):
 a=fig.add_subplot(2,3,index);meta=reg['trusses'][k];chosen=set(supports[k]+[meta['bottom_object']]);column=0 if meta['axis']=='x' else 1
 for o in D:
  n=o['name'];take=n in chosen or n.startswith('Frame'+k+'Web') or n=='TopChord'+k or n=='Top'+k+'Patch1'
  if not take:continue
  v=[[p[column]/25.4,p[2]/25.4] for p in o.get('vertices',[])];tris=o.get('triangles',[])
  a.add_collection(PolyCollection([[v[i] for i in t] for t in tris],facecolors=[o['color'][:3]],edgecolors='none'))
 if k in ['TN','TW']:
  lo,hi=(56.25,152.25) if k=='TN' else (186,246)
  a.add_patch(Rectangle((lo,120),hi-lo,84,fill=False,edgecolor='#c83240',linestyle='--',lw=1.2));a.text((lo+hi)/2,158,'CLEAR\n96 × 84 in' if k=='TN' else 'APPROX.\nBALCONY',ha='center',va='center',fontsize=9,color='#ac2233')
 start,end=meta['span_inches'];a.set(xlim=(start-7,end+7),ylim=(0,253),aspect='equal',xlabel=('East' if column==0 else 'North')+' (in)',ylabel='Height (in)',title={'TS':'T-S · six panels','T1':'T1 · four panels + future hangers','TW':'T-W · west elevation','TE':'T-E · east elevation','TN':'T-N · loading opening'}[k]);a.grid(alpha=.15)
fig.suptitle('Proposed primary frame · native editable geometry',fontsize=22)
fig.supxlabel('Sections are visual placeholders. Amber = future stage after existing roof removal. Connections and stability remain unresolved.',fontsize=12)
fig.savefig(P/'Proposed-Garage-full-frame.png',dpi=135)
# Refresh the established preview path so it cannot show the former U-E / optional posts.
fig.savefig(P/'Proposed-Garage-overlay.png',dpi=135)
