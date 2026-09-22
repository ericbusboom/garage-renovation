import os
os.environ['MPLCONFIGDIR']='/private/tmp/garage-mpl'
from pathlib import Path
import json
import matplotlib;matplotlib.use('Agg')
import matplotlib.pyplot as plt
P=Path(__file__).resolve().parent
rows=json.loads((P/'split-web.json').read_text());base=json.loads((P.parent/'structural-analysis-v3/results.json').read_text());optA=next(x for x in rows if x['lower']=='W6X16' and x['upper']=='HSS4x4x0.188');optB=next(x for x in rows if x['lower']=='W6X16' and x['upper']=='W6X20')
fig,axs=plt.subplots(2,1,figsize=(13,9),layout='constrained')
for ax,o,title in zip(axs,[optA,optB],['A • lower weight, square-tube upper chord','B • W beams on both chords']):
 xs=[224.25*i/6 for i in range(7)];h=84.643
 ax.plot([0,224.25],[0,0],color='#256d9c',lw=5);ax.plot([0,224.25],[h,h],color='#b66624',lw=6)
 for x in xs:ax.plot([x,x],[0,h],color='#59957a',lw=2)
 ax.plot([0,xs[1]],[0,h],color='#635b7d',lw=3);ax.plot([xs[-2],224.25],[h,0],color='#635b7d',lw=3)
 ax.text(112,h+5,'Upper: '+('HSS 4 × 4 × 3/16' if title.startswith('A') else 'W6×20'),ha='center',weight='bold',color='#99521a');ax.text(112,-9,'Lower / trolley rail: W6×16 — actual depth 6.28 in',ha='center',color='#256d9c',weight='bold');ax.text(112,h*.48,'Verticals: HSS 2 × 2 × 1/8\nEnd diagonals: HSS 2½ × 2½ × 1/8',ha='center',bbox=dict(fc='white',ec='none',alpha=.9));ax.annotate('',(-9,0),(-9,h),arrowprops=dict(arrowstyle='<->'));ax.text(-15,h/2,'84.64 in',rotation=90,va='center');ax.annotate('',(0,-20),(224.25,-20),arrowprops=dict(arrowstyle='<->'));ax.text(112,-26,'224.25 in overall span',ha='center')
 ax.set(xlim=(-25,240),ylim=(-32,101));ax.set_aspect('equal');ax.axis('off');ax.set_title(title+f" | T1 ≈ {o['T1_weight']:.0f} lb",loc='left',fontsize=14,weight='bold')
fig.suptitle('T1: stronger upper chord, shallower lower chord, lighter verticals',fontsize=17,weight='bold');fig.supxlabel('Analytical geometry only. Weight includes 10% connection allowance. Both options require O3 to increase to HSS 3 × 3 × 3/16.\nNo connection, bracing or trolley flange design is established by these gravity screens.',fontsize=10);fig.savefig(P/'T1-comparison.png',dpi=160)
(P/'selected-options.json').write_text(json.dumps({'A':optA,'B':optB},indent=2));print('Comparison image created')
