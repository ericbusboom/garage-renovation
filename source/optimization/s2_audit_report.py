import os,json
from pathlib import Path
os.environ['MPLCONFIGDIR']='/private/tmp/garage-wall-preview-mpl'
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
P=Path(__file__).resolve().parent
r=json.loads((P/'s2-investigation.json').read_text()); c=json.loads((P/'cad-analytical-members.json').read_text())
a=r[0]['results'];b=r[1]['results']
old=sum(v['reactions_lb']['S2'] for v in a.values());new=sum(v['reactions_lb']['S2'] for v in b.values())
# Classical three-moment equation for constant EI, two spans, all-span uniform load.
l1,l2,w=63,253,1
mb=-w*(l1**3+l2**3)/(8*(l1+l2))
ra=w*l1/2+mb/l1;rc=w*l2/2+mb/l2;rb=w*(l1+l2)-ra-rc
simple=json.loads((P/'s2-independent-beam.json').read_text())
assert max(abs(simple['reactions_lb'][k]-v) for k,v in zip(['A','B','C'],[ra,rb,rc]))<1e-8
fig,(ax,bx)=plt.subplots(2,1,figsize=(12,9),layout='constrained',gridspec_kw={'height_ratios':[1.6,1]})
for m in c['members']:
 if m.get('truss')=='TE' or m['id'] in ['T-E','S2','S3','N2']:
  y=[m['a'][1]/12,m['b'][1]/12];z=[m['a'][2]/12,m['b'][2]/12]
  ax.plot(y,z,color='#277c86' if m['id'] not in ['S2','S3','N2'] else '#ad7546',lw=2)
ax.plot([-63/12,253/12],[115/12,115/12],color='#164657',lw=3)
for y,n in [(-63,'S2'),(0,'S3'),(253,'N2')]:ax.text(y/12,-.65,n,ha='center',fontsize=13,fontweight='bold')
for y0,y1,label in [(-63,0,'5 ft 3 in'),(0,253,'21 ft 1 in')]:
 ax.annotate('',(y0/12,2),(y1/12,2),arrowprops=dict(arrowstyle='<->',color='#364955'));ax.text((y0+y1)/24,2.4,label,ha='center',bbox=dict(facecolor='white',edgecolor='none'))
ax.text(10,8.7,'Bottom chord is horizontal and continuous through S3',ha='center',fontsize=11)
ax.set(xlim=(-7,23),ylim=(-1.5,22),ylabel='Height (ft)',title='Actual analytical geometry • east frame viewed from the side');ax.set_aspect('equal',adjustable='box');ax.set_xticks([]);ax.spines[['top','right','bottom']].set_visible(False)
labels=['Steel weight','Floor dead','Roof dead','Wall dead','Floor live','Roof live'];keys=['Dsteel','Dfloor','Droof','Dwall','L40','R20']
vals=[a[k]['reactions_lb']['S2']/1000 for k in keys];bars=bx.barh(labels,vals,color='#b3574d');bx.bar_label(bars,fmt='%.2f',padding=5);bx.set(xlim=(-4.7,.2),xlabel='S2 reaction (kip); negative means hold-down required by the model',title='Every gravity-load group contributes to the modeled S2 uplift');bx.axvline(0,color='#667777',lw=.8);bx.spines[['top','right']].set_visible(False)
fig.suptitle('S2 audit | Continuous framing, unequal spans',fontsize=18)
fig.supxlabel('This explains the assumed analytical model. It does not establish the connection or foundation design.',fontsize=10)
fig.savefig(P/'s2-load-path-audit.png',dpi=150);fig.savefig(P/'S2-load-path-audit.pdf')
text=f'''# S2 reaction audit

The bottom chord is horizontal. There is no unsupported end overhang needed to generate this reaction. My earlier seesaw/cantilever explanation was incomplete: the relevant mechanism in this model is a continuous, three-support frame with strongly unequal adjacent spans.

## What was checked

- S2 at y=-63 in, S3 at y=0, N2 at y=253 in. The bottom chord is at z=115 in along its whole length.
- S2 connects to TE bottom chord, TE top chord and T-SO. S3 connects to both TE chords and TS. N2 connects to both TE chords and TN with an explicit 4-inch north offset.
- The model assumes continuity through S3 and connections capable of transmitting the modeled forces. Those details were not yet engineered.
- Load directions use global vertical FY, with CAD height mapped to solver Y. Reaction signs and global force/moment equilibrium were checked.
- Gravity loads were run separately. S2 contribution (lb): { {k:round(a[k]['reactions_lb']['S2'],1) for k in keys} }.
- Sum: {old:,.1f} lb at S2, reproducing the prior service40 result.
- Removing S3 as a diagnostic, while retaining the remaining geometry and loads apart from its own weight, changes S2 to {new:,.1f} lb downward bearing. This is not a proposal to remove S3 and no CAD columns were removed.
- Releasing column-base rotations or web-end bending leaves the uplift present. Those releases do not interrupt the continuous chords through S3.

## Independent check

A completely flat, constant-stiffness beam on three supports, with 63-inch and 253-inch spans and no overhang, also develops an upward-pull demand at its first support under uniform downward loading. At 1 lb/in, the classical three-moment equation gives reactions {ra:.3f}, {rb:.3f}, {rc:.3f} lb. The independent PyNite beam reproduces those numbers to better than 1e-8 lb.

For two separate simply supported spans instead, the same loads give 31.5, 158 and 126.5 lb: all downward-bearing loads on the foundations. This is a different connection/continuity arrangement, not a solver setting to change merely to remove an undesirable result.

## Conclusion

I did not find a flipped load, sloping bottom chord, or required cantilever that explains away the reaction. The reaction is reproducible within the continuous-frame assumption. Its magnitude is not established for the intended construction until the TE/S3 connection arrangement is settled. Treat the 11.4 kip as a conditional analytical result, not a footing design requirement.

The next meaningful comparison is a deliberately detailed TE arrangement that either preserves continuity through S3 or divides the structural action into independent spans. Releasing an individual web or column base is not equivalent to that change.

Solver API conventions checked against [PyNite documentation](https://pynite.readthedocs.io/en/latest/FEModel3D.html). All numerical results above are calculations in this project, not values from that documentation.
'''
(P/'S2-audit.md').write_text(text)
print('Audit confirmed; S2 without S3 =',new)
