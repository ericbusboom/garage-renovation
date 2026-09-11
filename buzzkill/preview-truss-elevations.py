import os,json,pathlib
os.environ['MPLCONFIGDIR']='/private/tmp/garage-wall-preview-mpl'
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection
P=pathlib.Path('/Volumes/Proj/Buzzkill-Proj/garage')
d=json.loads((P/'proposed-overlay-new.json').read_text())
fig,axs=plt.subplots(3,2,figsize=(16,13),layout='constrained')
for ax,(tid,axis,needle) in zip(axs.flat,[('T-W',1,'TW'),('T-E',1,'TE'),('T-S',0,'TS'),('T-N',0,'TN'),('T1',0,'T1')]):
 count=0
 for o in d['objects']:
  name=o['name']; label=o.get('label','')
  match=(tid in label or name.startswith('Proposed'+needle) or name.startswith('Full'+needle))
  if tid=='T-S' and ('TSO' in name or 'T-SO' in label):match=False
  if not match or not o.get('triangles'):continue
  vs=[[p[axis]/25.4,p[2]/25.4] for p in o['vertices']]
  polys=[[vs[i] for i in t] for t in o['triangles']]
  ax.add_collection(PolyCollection(polys,facecolors=[o.get('color',[.2,.6,.6])[:3]],edgecolors='#346068',linewidths=.12));count+=1
 ax.autoscale();ax.set_aspect('equal');ax.set_title(tid+' • '+str(count)+' members');ax.set_xlabel(('North from south wall' if axis else 'East from west wall')+' (in)');ax.set_ylabel('Height (in)');ax.grid(alpha=.12)
axs.flat[-1].axis('off');axs.flat[-1].text(.05,.9,'Primary framing layout\n\nTop chords, bottom chords and webs\nare shown for review.\n\nSizes, connections and open panels\nrequire structural design.\n\nAmber: later floor beam / hangers.',va='top',fontsize=15)
fig.suptitle('Renovation trusses • individual elevations',fontsize=22)
fig.savefig('/private/tmp/Proposed-Garage-truss-elevations.png',dpi=150)
fig.savefig('/private/tmp/Proposed-Garage-truss-elevations.pdf')
