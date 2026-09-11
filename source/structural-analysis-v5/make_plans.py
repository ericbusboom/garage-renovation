import os
os.environ['MPLCONFIGDIR']='/private/tmp/garage-mpl'
import json
from pathlib import Path
import matplotlib;matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
P=Path(__file__).resolve().parent
fig,axs=plt.subplots(1,2,figsize=(15,10),layout='constrained')
for ax,name,title in zip(axs,['single-161','two-equal'],['One repositioned B2','Two interior beams']):
 r=json.loads((P/'results'/f'{name}.json').read_text());ys=r['beam_y'];ax.add_patch(Rectangle((0,72),224.25,183,facecolor='#edf2f5'));ax.plot([0,249.5,249.5],[249,249,65],c='#b1b5b7',lw=3)
 for x,c,l in [(0,'#22816d','T-W TRUSS'),(224.25,'#824f97','T-E TRUSS')]:ax.plot([x,x],[69.75,253],color=c,lw=4);ax.text(x+(-9 if x==0 else 10),160,l,rotation=90,ha='center',va='center',color=c,weight='bold')
 for y,c,l in [(69.75,'#be6823','T1 TRUSS'),(253,'#af4459','T-N TRUSS — floor support')]:ax.plot([0,224.25],[y,y],color=c,lw=4);ax.text(112,y+4,l,ha='center',color=c,weight='bold',fontsize=10)
 for n,y in zip(r['beam_names'],ys):
  ax.plot([0,224.25],[y,y],c='#266b9b',lw=3);ax.text(112,y+4,f"{n} · {r['selection'][n+':beam']}",ha='center',color='#266b9b',weight='bold');ax.text(112,y-8,f'{y:.2f} in north of south wall',ha='center',fontsize=9)
 spans=r['supports']
 for a,b in zip(spans[:-1],spans[1:]):
  ax.annotate('',(270,a),(270,b),arrowprops=dict(arrowstyle='<->',color='#555'));ax.text(274,(a+b)/2,f'{b-a:.2f} in',va='center',fontsize=9)
  for x in [40,184]:ax.annotate('',(x,a+7),(x,b-8),arrowprops=dict(arrowstyle='<->',color='#8fa6b4'))
 ax.text(112,281,'NORTH ↑',ha='center',weight='bold');ax.annotate('',(0,53),(224.25,53),arrowprops=dict(arrowstyle='<->'));ax.text(112,47,'224.25 in between T-W and T-E',ha='center',fontsize=9);ax.set_title(title+f"\nPrimary steel + allowance: {r['steel_with_connections_lb']:,.0f} lb",fontsize=15);ax.set(xlim=(-30,315),ylim=(38,290));ax.set_aspect('equal');ax.axis('off')
fig.suptitle('B3 removed • north floor joists bear on T-N’s lower chord',fontsize=19,weight='bold');fig.supxlabel('Floor-support plan only. Existing columns remain fixed; O3 remains at y = 185 in.\nConditional gravity comparison: joint/seat details, bracing and trolley local checks remain unresolved.',fontsize=11);fig.savefig(P/'beam-position-comparison.png',dpi=150);print('Plan comparison created')
