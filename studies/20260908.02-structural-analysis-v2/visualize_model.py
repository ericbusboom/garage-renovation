"""Plots from the saved finite-element model and its solved displacements."""
import os
os.environ['MPLCONFIGDIR']='/private/tmp/garage-mpl'
import json
from pathlib import Path
import numpy as np
import matplotlib;matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Rectangle
P=Path(__file__).resolve().parent;m=json.loads((P/'analysis-model.json').read_text());r=json.loads((P/'results.json').read_text());N=np.array(m['nodes']);es=m['elements'];u=np.array(r['cases']['service storage bands']['u']).reshape(-1,6)
C={'T1':'#c05c13','T-E':'#8c48a0','T-W':'#259074','T-S':'#b29a27','T-N':'#bd435e'}
def color(e):return C.get(e['group'],'#326aa8' if e['kind']=='beam' else '#555c68')
plt.rcParams.update({'font.size':11,'axes.spines.top':False,'axes.spines.right':False})
fig=plt.figure(figsize=(15,10));ax=fig.add_subplot(111,projection='3d')
for e in es:
 a,b=N[e['ij']]/12;ax.plot(*np.array([a,b]).T,color=color(e),lw=1.5 if e['kind']!='column' else 2)
for label,pos in [('T1 — TRUSS',(105,69.75,195)),('T-E — TRUSS',(224.25,105,185)),('T-W — TRUSS',(0,130,222)),('B2 — BEAM',(100,185,94)),('T-N — TRUSS',(130,253,238)),('T-S — TRUSS',(105,0,151)),('B3 — BEAM',(155,249,90)),('T-SO — BEAM',(90,-63,94))]:ax.text(*(np.array(pos)/12),label,fontsize=10,color=C.get(label.split(' —')[0],'#245889'),bbox=dict(facecolor='white',edgecolor='none',alpha=.85,pad=2))
ax.set(xlabel='East (ft)',ylabel='North (ft)',zlabel='Height (ft)');ax.view_init(elev=24,azim=-125);ax.set_box_aspect((1,1.25,.85));fig.suptitle('The connected Python frame model',fontsize=22,weight='bold');fig.text(.5,.91,'T1, T-E and T-W contain upper chords, lower chords and webs — not standalone beams.',ha='center');fig.text(.5,.045,'Saved HSS baseline • W-section trolley revision is not yet calculated • hip-cap rafters are not modeled',ha='center',fontsize=11);fig.savefig(P/'model-3d.png',dpi=150);plt.close(fig)
fig,axs=plt.subplots(3,1,figsize=(15,12),layout='constrained')
for ax,g,dim,title in zip(axs,['T1','T-E','T-W'],[0,1,1],['T1 — transverse TRUSS','T-E — east longitudinal TRUSS','T-W — west longitudinal TRUSS']):
 for e in es:
  if e['group']!=g:continue
  ids=e['ij'];a=N[ids];b=a+20*u[ids,:3];ax.plot(a[:,dim]/12,(a[:,2]-98.5)/12,color=C[g],lw=2);ax.plot(b[:,dim]/12,(b[:,2]-98.5)/12,color='#222',lw=1,ls='--',alpha=.8)
 ax.set_aspect('equal',adjustable='datalim');ax.set_title(title,loc='left',color=C[g],weight='bold');ax.set_ylabel('Above wall top (ft)');ax.grid(alpha=.15);ax.set_xlabel('East from west wall (ft)' if dim==0 else 'North from south wall (ft)')
 ax.legend([Line2D([0],[0],color=C[g],lw=2),Line2D([0],[0],color='#222',ls='--')],['Original geometry','Deflected shape ×20'],loc='upper left',fontsize=9)
fig.suptitle('Actual truss geometry and calculated movement',fontsize=21,weight='bold');fig.supxlabel('Perimeter-storage service case • global maximum vertical movement 0.644 in • rigid-joint HSS baseline',fontsize=11);fig.savefig(P/'truss-deformation.png',dpi=150);plt.close(fig)
fig,ax=plt.subplots(figsize=(12,12));ax.add_patch(Rectangle((0,0),249.5,249,fill=False,ec='#999',lw=5));ax.add_patch(Rectangle((0,72),224.25,183,fc='#e5edf3',alpha=.65));
for e in es:
 a=N[e['ij']]
 if np.all(abs(a[:,2]-98.5)<.01):ax.plot(a[:,0],a[:,1],color=color(e),lw=3 if e['group'] in C else 2)
for txt,x,y,rot in [('T-E · TRUSS',231,112,90),('T-W · TRUSS',-12,112,90),('T1 · TRUSS',100,78,0),('B2 · BEAM',100,190,0),('T-S · TRUSS',100,5,0),('T-N · TRUSS',118,266,0),('B3 · BEAM',112,236,0),('T-SO · BEAM',100,-58,0),('B-WO · BEAM',-42,115,90)]:ax.text(x,y,txt,rotation=rot,ha='center',fontsize=11,weight='bold',bbox=dict(fc='white',ec='none',alpha=.85,pad=2))
for name,i in m['bases'].items():
 x,y,z=N[i];ax.scatter(x,y,s=55,c='#ab4b24' if name=='S1' else '#333',zorder=5);ax.annotate(name,(x,y),xytext=(5,8 if name not in ['N1','N2','W4'] else -16),textcoords='offset points',fontsize=10)
# Diagrammatic floor joist direction, not extra FE elements.
for x in [55,155]:
 for lo,hi in [(95,161),(204,225)]:ax.annotate('',(x,hi),(x,lo),arrowprops=dict(arrowstyle='<->',color='#6e87a0',lw=1.6))
ax.text(106,143,'Floor joists span N–S\nto T1 / B2 / B3',ha='center',color='#516a80');ax.text(112,285,'NORTH ↑',ha='center',weight='bold');ax.set(xlim=(-65,280),ylim=(-80,300),xlabel='East from west wall (in)',ylabel='North from south wall (in)');ax.set_aspect('equal');ax.grid(alpha=.1);fig.suptitle('Framing plan — corrected member labels',fontsize=21,weight='bold');fig.text(.5,.025,'Colored truss lines represent complete vertical trusses shown on the elevation sheet.\nGray outline = existing walls; no added wall support credited. S1 currently disconnected; S3 assumed present.',ha='center',fontsize=10);fig.savefig(P/'framing-labelled.png',dpi=150);plt.close(fig)
print('Generated three model visualizations')
