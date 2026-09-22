"""Generate transparent first-iteration engineering plots and PDF from solver JSON."""
import os,json,textwrap
from pathlib import Path
os.environ['MPLCONFIGDIR']='/private/tmp/garage-wall-preview-mpl'
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import numpy as np
P=Path(__file__).resolve().parent
R=json.loads((P/'results.json').read_text()); M=json.loads((P/'analysis-model.json').read_text()); B=json.loads((P/'design-basis.json').read_text());C=json.loads((P/'cad-analytical-members.json').read_text())
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.spines.top':False,'axes.spines.right':False})
base=R[0];cases=R[:4];colors=['#235b72','#248b85','#d18b2f','#ae5348']
fig=plt.figure(figsize=(15,9),layout='constrained');ax=fig.add_subplot(121,projection='3d');plan=fig.add_subplot(122)
for e in M['elements']:
 a=np.array(M['nodes'][e['a']])/12;b=np.array(M['nodes'][e['b']])/12
 ax.plot(*np.array([a,b]).T,color='#9ba9b1',lw=.6,alpha=.6)
 da=np.array(M['displacements_service40'][e['a']])*30/12;db=np.array(M['displacements_service40'][e['b']])*30/12
 ax.plot(*np.array([a+da,b+db]).T,color='#257e8e',lw=.7)
 plan.plot([a[0],b[0]],[a[1],b[1]],color='#b5c1c7',lw=.65)
for name,node in M['bases'].items():
 x,y,z=np.array(M['nodes'][node])/12;r=base['results']['service40']['reactions_lb'][name]/1000
 col='#ae5348' if r<0 else '#235b72';plan.scatter([x],[y],s=60,color=col,zorder=4)
 dx=-1.0 if x<0 else .45;dy=.8 if name in ['S1','N1 / U-W','N2','SW0'] else -.7
 plan.annotate(f'{name}\n{r:+.1f} kip',(x,y),xytext=(x+dx,y+dy),ha='right' if x<0 else 'left',fontsize=8,color=col,arrowprops=dict(arrowstyle='-',color=col,lw=.5))
ax.set(xlabel='East (ft)',ylabel='North (ft)',zlabel='Height (ft)',title='Elastic FE model • deformation enlarged 30×');ax.view_init(24,-125);ax.set_box_aspect((1,1.15,.85))
plan.set(xlabel='East (ft)',ylabel='North (ft)',title='Baseline vertical base reactions • 1 kip = 1,000 lb',aspect='equal',xlim=(-7,25),ylim=(-9,25));plan.grid(alpha=.12)
fig.suptitle('Renovated garage | First structural iteration',fontsize=20)
fig.supxlabel('40 psf floor live + preliminary dead loads + 20 psf roof live. Negative reaction = required hold-down. Conditional joint/base assumptions.',fontsize=10)
fig.savefig(P/'frame-and-reactions.png',dpi=160)
fig2,aa=plt.subplots(1,3,figsize=(15,6),layout='constrained');names=['All columns','Remove W2','Remove W3','Remove both']
for a,vals,title,unit in [(aa[0],[r['results']['service40']['max_floor_abs_DY_in'] for r in cases],'Total floor displacement','inches'),(aa[1],[max(0,-min(r['results']['service40']['reactions_lb'].values()))/1000 for r in cases],'Largest required hold-down','kip'),(aa[2],[(base['steel_weight_lb']-r['steel_weight_lb']) for r in cases],'Column steel removed','lb')]:
 bars=a.bar(names,vals,color=colors);a.set(title=title,ylabel=unit);a.tick_params(axis='x',rotation=25);a.bar_label(bars,fmt='%.2f' if unit=='inches' else '%.0f',padding=4);a.set_ylim(0,max(vals)*1.25)
fig2.suptitle('Column removal: a material saving can increase foundation demands',fontsize=18)
fig2.supxlabel('Same candidate sections and idealized joints in every case. These are comparisons, not approved configurations.',fontsize=11)
fig2.savefig(P/'column-comparison.png',dpi=160)
# Quantities and editable procurement calculator: null rates prevent fabricated quotes.
quantities=[]
for r in cases:
 quantities.append({'case':r['case'],'primary_steel_lb':r['steel_weight_lb'],'steel_saved_lb':base['steel_weight_lb']-r['steel_weight_lb'],'columns_removed':len(r['removed_columns']),'foundation_savings_unverified':True})
cost={'currency':'USD','rates_not_quotes':{'steel_delivered_per_lb':None,'shop_per_hour':None,'field_per_hour':None,'foundation_per_column':None,'crane_per_hour':None},'quantities':quantities,'total_formula':'steel_lb * steel_delivered_per_lb + shop_hours * shop_per_hour + field_hours * field_per_hour + foundation_cost + lifting_transport_cost','decision':'No cost winner until connection labor and revised foundation quantities are estimated. Compare shop-weld/site-bolt versus site-weld with the same load requirements.'}
(P/'cost-inputs.json').write_text(json.dumps(cost,indent=2))
lines=['# Renovated garage — structural iteration 1','',
'**Status: preliminary conditional model, not a fabrication design.** The original garage is hidden in the separate renovation CAD group. No column has been removed from the CAD baseline. No load capacity is credited to the original walls or slab.','',
'## Load basis','',
'The 1,000 lb rated hoist is modeled as a 1,350 lb vertical point action: 1,000 × 1.25 assumed impact + 100 lb assumed hoist/trolley weight. It is tested separately on B2 and the future T1 floor beam at quarter, middle and three-quarter span; simultaneous hoists are not assumed. Real trolley travel limits, local flange bending, side loads and crane-post action remain to be checked.',
'','The 275.64 ft² loft uses 40 psf live load (11,026 lb), a 30 psf use case, and 75 psf local bands at the north and east edges. The 125 psf case is a sensitivity only; applicable occupancy and code minimum are not yet determined. A 200 lb machine is also tested in addition to the 40 psf case. The joists and plywood still need local load checks.','',
'Dead-load allowances: floor 12 psf excluding primary steel; sloped roof 9.5 psf of surface; cap 6.6 psf of surface; insulated metal walls 4 psf. Candidate primary steel self-weight is computed from member lengths. These assembly allowances require a manufacturer/material takeoff. Roof live load is a provisional 20 psf plan-area case. A 20 psf uplift sensitivity is not a site wind design.','',
'## First comparison','',
'| Layout | Primary steel (lb) | Total floor movement (in) | Largest hold-down (kip) |','|---|---:|---:|---:|']
for r,n in zip(cases,names):
 v=r['results']['service40'];lines.append(f"| {n} | {r['steel_weight_lb']:,.0f} | {v['max_floor_abs_DY_in']:.3f} | {max(0,-min(v['reactions_lb'].values()))/1000:.1f} |")
lines += ['', 'Movement is absolute displacement of the main floor-support members under dead + floor live + roof live loads. It is not joist or deck deflection, and it is not directly interchangeable with a span-relative L/360 criterion.','',
'W2 removal is the better candidate for further study of the two intermediate west columns: floor displacement changes little, while W3 removal increases it appreciably. This does not establish that W2 can be removed. All cases show large east-side compression/hold-down demands. Removing both also transfers about 11 kip of hold-down demand to SW0.','',
'Hoist cases: peak modeled floor-support displacement is %.3f in with all columns, %.3f in without W2, %.3f in without W3 and %.3f in without both. These cases include dead load, 40 psf floor live load and one hoist; the 20 psf roof live case is separate.' % tuple(max(v['max_floor_abs_DY_in'] for k,v in r['results'].items() if k.startswith(('HB','HT'))) for r in cases),'','## Modeling and checks','',
'CAD centerlines and explicitly identified connection offsets feed a 3D PyNite frame model. Roof load is provisionally carried east–west to TE and TW. Steel beams and trusses share load through the modeled joints; each truss is not assigned the entire building load. The future T1 floor beam and hangers are active in this final-stage analysis. The roof-first construction stage has not yet been checked.','',
'Candidate sections are HSS 6×6×1/4 chords, HSS 2×2×1/8 webs, HSS 4×4×1/4 typical posts and W8×31 floor beams. They are stiffness-study candidates, not optimized selections. This roughly 10,100 lb steel baseline is not claimed to meet the minimum-weight goal.','',
'A simply supported beam benchmark reproduces its closed-form deflection. Linear cases check global force and moment balance. Sensitivity runs change web-end bending releases, base fixity and numerical offset-link stiffness; a P–Delta baseline is also included. Convergence and force balance verify solver behavior, not connection realism. Open rectangular truss bays still rely on frame action and need actual joint design.','',
'## Cost optimization and next design gate','',
'Use cost-inputs.json for quantity comparisons and editable rates. Rates are deliberately blank until quotes or stated planning assumptions are supplied. Removing a post saves its steel and potentially one footing, but added reinforcement, hold-downs and connection work can exceed that saving. Compare shop welding with site bolting against site welding after detailing comparable joints.','',
'The next design iteration must resolve the TE/S2/S3 load path and foundation hold-downs, member buckling and lateral restraint, connection capacities, the lateral system, roof seams, hoist flange checks and temporary erection bracing. Only then should stock sections be reduced and cost-ranked as feasible candidates. A California structural engineer needs to review these items before fabrication.','',
'## Reproduce','',
'Install the packages in requirements.txt, then run `python run_analysis.py` and `python make_report.py` from this directory. Edit design-basis.json for the exposed load inputs. Geometry and connectivity come from cad-analytical-members.json; geometry changes require a fresh CAD export. See results.json for every load case and assumption.','',
'## References','',
'- [San Diego adopted codes](https://www.sandiego.gov/development-services/codes-regulations): establish governing requirements before final design.',
'- [PyNite stability documentation](https://pynite.readthedocs.io/en/latest/stability.html): solver stability is distinct from structural design adequacy.',
'- [AISC cost guidance](https://www.aisc.org/architecture-center/resources/the-steel-advantage/cost/): fabrication and erection matter alongside material weight.',
'- [Steel Tube Institute: fabricator considerations](https://steeltubeinstitute.org/resources/fabricator-wishes-knew-hss/): connection detailing and fabrication affect economical HSS designs.']
(P/'README.md').write_text('\n'.join(lines)+'\n')
with PdfPages(P/'Garage-structural-iteration-1.pdf') as pdf:
 pdf.savefig(fig);pdf.savefig(fig2)
 textlines=[]
 for line in lines:
  if line.startswith('- ['):continue
  textlines.extend(textwrap.wrap(line.replace('**','').replace('`',''),105) or [''])
 for i in range(0,len(textlines),49):
  f=plt.figure(figsize=(11.7,8.3));f.text(.055,.95,'\n'.join(textlines[i:i+49]),ha='left',va='top',fontsize=9.4,family='DejaVu Sans',linespacing=1.28);pdf.savefig(f);plt.close(f)
plt.close('all')
print('Wrote figures, PDF, README and cost-inputs.json')
