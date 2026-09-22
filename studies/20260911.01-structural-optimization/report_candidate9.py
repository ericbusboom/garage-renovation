import os,json,csv,textwrap,math
from pathlib import Path
os.environ['MPLCONFIGDIR']='/private/tmp/garage-wall-preview-mpl'
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from matplotlib.patches import Rectangle
import numpy as np
P=Path(__file__).resolve().parent
r=json.loads((P/'candidate9_complete.json').read_text());stage=json.loads((P/'candidate9_roof_first.json').read_text());pin=json.loads((P/'candidate9_base_pinned.json').read_text());c=json.loads((P/'candidate9-candidate-geometry.json').read_text());mesh=json.loads((P/'candidate9-cad-mesh.json').read_text());sel=r['selection'];cat=json.loads((P/'iteration2-catalog.json').read_text());mm={m['id']:m for m in c['members']}
plt.rcParams.update({'font.size':10,'axes.spines.top':False,'axes.spines.right':False})
fig=plt.figure(figsize=(15,10),layout='constrained');ax=fig.add_subplot(121,projection='3d');plan=fig.add_subplot(122)
for o in mesh['objects']:
 v=np.array(o['vertices']);polys=[v[t] for t in o['triangles']];ax.add_collection3d(Poly3DCollection(polys,facecolors=o['color'],edgecolors='none',alpha=1))
for line in mesh.get('roof_lines',[]):ax.plot(*np.array(line).T,color='#697680',lw=.7)
for m in c['members']:
 if m['id']=='W2':continue
 a=np.array(m['a']);b=np.array(m['b']);col='#9252ae' if m['id'].startswith('BR-') else '#6e9e9d'
 if m['id'].startswith('BR-') or m['section_family'] in ['chord','Wbeam']:plan.plot([a[0],b[0]],[a[1],b[1]],color=col,lw=1.3 if m['id'].startswith('BR-R') else 2 if m['id'].startswith('BR-') else .9,linestyle='--' if m['id'].startswith('BR-R') else '-',alpha=.9)
 if m['axis_source'].get('ground_post'):
  plan.scatter([a[0]],[a[1]],color='#ad7442',s=50,zorder=5);plan.annotate(m['id'],a[:2],xytext=(-6,8),textcoords='offset points',ha='right',fontsize=9)
deck=np.array([[0,72,120],[222.25,72,120],[222.25,249,120],[0,249,120]])
ax.add_collection3d(Poly3DCollection([deck],facecolors='#dcc49b',alpha=.35))
plan.add_patch(Rectangle((0,72),222.25,177,facecolor='#ead9ba',alpha=.35,zorder=0))
plan.add_patch(Rectangle((0,0),249.5,249,fill=False,ls='--',lw=1,color='#7b8893'))
plan.scatter([-32],[69.75],facecolors='white',edgecolors='#c54845',marker='o',s=65);plan.text(-42,69.75,'W2 removed',ha='right',va='center',color='#b24742',fontsize=9)
plan.text(110,90,'LOFT: 18 ft 6¼ in × 14 ft 9 in\nFinished floor: 10 ft ¾ in',ha='center',fontsize=10,bbox=dict(facecolor='white',edgecolor='none',alpha=.9))
plan.text(110,213,'Overhead roof X-bracing',ha='center',color='#793d92',fontsize=9)
for yy,lab in [(69.75,'T1 rail'),(185,'B2')]:
 plan.plot([-32,224.25],[yy,yy],color='#3264a4',lw=2);plan.text(232,yy,lab,va='center',fontsize=9,color='#3264a4')
plan.text(110,22,'OPEN SOUTH',ha='center',fontsize=11)
plan.text(110,-43,'South & east lower braced bays',ha='center',fontsize=9,color='#793d92')
plan.text(78,274,'North bracing remains west of main door opening',ha='center',fontsize=9,color='#793d92')
ax.set(xlim=(-45,260),ylim=(-70,275),zlim=(0,250),xlabel='East (in)',ylabel='North (in)',zlabel='Height (in)',title='Actual stock profiles • original garage hidden');ax.view_init(26,-126);ax.set_box_aspect((305,345,250))
plan.set(xlim=(-100,285),ylim=(-80,285),aspect='equal',xlabel='East (in)',ylabel='North (in)',title='Plan • purple = proposed bracing');plan.grid(alpha=.12)
fig.suptitle('Candidate 9 | Braced steel frame and renovated loft',fontsize=20)
fig.supxlabel('Separate CAD candidate. Purple bracing needs access/window review. Bearings, connections, secondary roof framing and foundations are not fabrication details.',fontsize=10)
fig.savefig(P/'candidate9-overview.png',dpi=150)
fig2,axs=plt.subplots(1,3,figsize=(15,5),layout='constrained')
axs[0].bar(['Initial gravity\nframe','Lighter gravity\nframe','Braced\ncandidate'],[10135,7885,r['steel_weight_lb']],color=['#94a4ac','#458d8a','#734e94']);axs[0].set(title='Primary steel only',ylabel='lb');axs[0].set_ylim(0,12500)
for cont in axs[0].containers:axs[0].bar_label(cont,fmt='%.0f',padding=4)
axs[1].bar(['Unbraced\nfinal stage','Braced\nfinal stage','Braced\nroof-first'],[5.395,r['results']['lateral_HX']['max_horizontal_displacement_in'],stage['results']['lateral_HX']['max_horizontal_displacement_in']],color=['#b87767','#734e94','#488f8a']);axs[1].set(title='Horizontal test response',ylabel='inches',ylim=(0,6.3))
for cont in axs[1].containers:axs[1].bar_label(cont,fmt='%.2f',padding=4)
vals=[r['max_screen_ratio'],stage['max_screen_ratio'],r['lower_chords_unbraced_ratio'],r['storage125_sensitivity_ratio']];axs[2].bar(['Final\nstage','Roof-first','Lower chords\nunbraced','125 psf\nstorage'],vals,color=['#448d86','#448d86','#448d86','#b56252']);axs[2].axhline(1,color='#222',ls='--');axs[2].set(title='Selected member checks',ylabel='Demand / screened capacity',ylim=(0,max(vals)*1.2))
for cont in axs[2].containers:axs[2].bar_label(cont,fmt='%.2f',padding=4)
fig2.suptitle('What changed — and what has not passed',fontsize=18);fig2.supxlabel('Horizontal tests are 10/20 psf equivalent roof-level forces, not site wind design. Check ratios exclude connection and other unverified limit states.',fontsize=10)
fig2.savefig(P/'candidate9-comparison.png',dpi=150)
# Truss elevations show the actual proposed section centerlines and added upper braces.
fig3,axes=plt.subplots(3,2,figsize=(15,11),layout='constrained')
for ax3,tr in zip(axes.flat,['TE','TW','TN','TS','T1']):
 selected=[m for m in c['members'] if m.get('truss')==tr or (tr=='TE' and m['id'].startswith('BR-E-upper')) or (tr=='TN' and m['id'].startswith('BR-N-upper')) or (tr=='T1' and (m['section_family']=='hanger' or m['id']=='T1 future floor beam'))]
 coord=1 if tr in ['TE','TW'] else 0
 for m in selected:
  a0=np.array(m['a']);b0=np.array(m['b']);color='#9551ad' if m['id'].startswith('BR-') else '#3264a4' if m['section_family'] in ['Wbeam','hanger'] else '#237d80'
  ax3.plot([a0[coord],b0[coord]],[a0[2],b0[2]],color=color,lw=2 if m['section_family'] in ['chord','Wbeam'] else 1)
 ax3.axhline(120.75,color='#bd9e68',ls='--',lw=.8);ax3.set(title=tr+' • member axes, dimensions in inches',xlabel='North station' if coord==1 else 'East station',ylabel='Height',ylim=(108,246));ax3.grid(alpha=.15)
axes.flat[-1].axis('off');axes.flat[-1].text(.03,.95,'Section summary\n\nB2: W8×24\nT1 suspended rail: W6×15\nTE top: HSS 6×6×¼\nTE bottom: HSS 4×4×½\nTE webs: HSS 3×3×¼\nTypical webs elsewhere: HSS 2×2×⅛\n\nPurple = additional upper-wall bracing\nBlue = future floor rail / hangers\nDashed tan = finished loft floor\n\nFull member sizes and force checks are in the CSV.',va='top',fontsize=12)
fig3.suptitle('Candidate truss layouts • roof outlines and floor level retained',fontsize=18)
fig3.savefig(P/'candidate9-truss-elevations.png',dpi=150)
# Every physical member has reproducible strength demand and capacity data.
with (P/'candidate9-member-checks.csv').open('w') as f:
 w=csv.writer(f);w.writerow(['member','section','governing_case','screen_ratio','compression_lb','tension_lb','moment_local_y_lbin','moment_local_z_lbin','compression_capacity_lb','effective_length_in'])
 for mid,v in r['member_checks'].items():w.writerow([mid,v['section'],v['case'],v['ratio'],v['demands']['compression'],v['demands']['tension'],v['demands']['My'],v['demands']['Mz'],v['capacities']['Pc'],v['capacities']['Lb']])
with (P/'candidate9-foundation-reactions.csv').open('w') as f:
 w=csv.writer(f);w.writerow(['case','column','vertical_reaction_lb','note'])
 for case,v in r['results'].items():
  for col,force in v['reactions_lb'].items():w.writerow([case,col,force,'Positive upward on frame / downward bearing on footing. Negative requires hold-down. Lateral cases are sensitivity loads.'])
L=109;I=1.5*7.25**3/12;S=1.5*7.25**2/6;spacing=16/12
floorfb=(75+12)*spacing/12*L**2/8/S;floorE=5*(75*spacing/12)*L**4/(384*I*(L/360))
roofL=256.25;roofw=20*4/12;roofI=5*roofw*roofL**4/(384*29e6*(roofL/240));roofS=(1.2*9.5/math.cos(math.pi/6)+1.6*20)*4/12*roofL**2/8/(.9*50000)
checks={'wood_joists':{'actual_section_in':[1.5,7.25],'spacing_in':16,'span_in':L,'uniform_live_psf':75,'dead_psf':12,'required_adjusted_Fb_psi':floorfb,'required_E_psi_live_L360':floorE,'note':'Required properties only; wood species/grade, bearing, hangers and plywood local loads not selected/checked.'},'roof_purlin':{'span_in':roofL,'trial_spacing_in':48,'minimum_I_in4_live_L240':roofI,'elastic_yield_S_in3_lower_bound':roofS,'note':'Preliminary demand target, NOT a cold-formed member selection; local/distortional buckling, restraints, suction and connections require supplier/AISI design.'}}
(P/'candidate9-secondary-framing.json').write_text(json.dumps(checks,indent=2))
clearfile=P/'candidate9-clearance-check.json';clear=json.loads(clearfile.read_text()) if clearfile.exists() else {}
clashes=clear.get('roof_first_solid_intersections',[]);clashmembers=sorted({q['new_member'] for q in clashes})
roofsource='https://metlspan.com/wp-content/uploads/2022/11/PSF-Panel-Weights_2019.pdf';pvsource='https://www.recgroup.com/sites/default/files/2025-04/Web_DS_REC%20Alpha%20Pure-RX_EN%20US_042025.pdf'
text=f'''# Candidate 9 — garage structural study

**Recommendation:** carry forward this braced steel scheme as the next design candidate. It supports the studied loft and roof without assigning vertical capacity to the old walls or slab. It is not a permitted or fabrication-ready design, and is not a proven global cost minimum.

## Main choices

- Remove W2; retain the other nine ground columns. Strengthen TW diagonals to compensate.
- B2: W8×24. T1 future suspended floor beam: W6×15. T-SO: W6×15.
- TE upper chord: HSS 6×6×1/4. TE lower chord: HSS 4×4×1/2, centerline raised from 115 to 120 in to clear old rafters while retaining the floor and roof elevations.
- TE webs: HSS 3×3×1/4. Most other webs remain HSS 2×2×1/8. TW diagonals: HSS 3×3×1/8.
- TW lower chord: HSS 4×4×1/4; upper: HSS 4×4×5/16. The heavier bottom chord avoids relying on the future loft for its roof-first lateral restraint.
- Typical posts: HSS 4×4×1/4. W4 and N2: HSS 4×4×3/8. N1/U-W retains its 6×6×1/4 candidate section. The CSV records all remaining sections.
- Add 16 diagonal bracing members: four lower perimeter bays, two upper-wall bays and two roof-plane bays. The north lower braces move 4 in north for eave clearance; their offset connections need design.

## What the computations establish

Primary steel: {r['steel_weight_lb']:,.0f} lb, plus a separate assumed 10% connection dead-weight reserve of {r.get('connection_allowance_lb',0):,.0f} lb. This includes primary beams, trusses, posts and the explicit new braces. Secondary roof framing is included only as part of the roof assembly weight allowance. Earlier lighter gravity-only candidates omitted this bracing and are not equivalent completed designs.

Maximum screened member ratio: {r['max_screen_ratio']:.2f} in the completed stage and {stage['max_screen_ratio']:.2f} in the roof-first stage. Values below 1 pass the implemented checks; they are not safety factors or proof of every limit state. The additional full-length lower-chord buckling check gives {stage['lower_chords_unbraced_ratio']:.2f} for roof-first construction. Upper chords and trolley rails still require designed lateral/torsional restraint at no more than 72 in.

Maximum main floor-support movement under dead, storage-band and roof live loads: {r['results']['service_patches']['max_floor_abs_DY_in']:.2f} in. B2 live-only deflection relative to its moving supports: {r['relative_floor_deflection']['live_only']['B2 future floor beam']:.2f} in versus a 256.25/360 = 0.71 in comparison. Midspan B2 hoist-case relative deflection: {r['relative_floor_deflection']['HB0.5']['B2 future floor beam']:.2f} in. These are steel-support results, not plywood or joist deflections.

The 10 psf equivalent horizontal-force test gives {r['results']['lateral_HX']['max_horizontal_displacement_in']:.2f} in in the east–west direction and {r['results']['lateral_HZ']['max_horizontal_displacement_in']:.2f} in north–south. Roof-first results are {stage['results']['lateral_HX']['max_horizontal_displacement_in']:.2f} and {stage['results']['lateral_HZ']['max_horizontal_displacement_in']:.2f} in. Pinned-base tests give {pin['results']['lateral_HX']['max_horizontal_displacement_in']:.2f} and {pin['results']['lateral_HZ']['max_horizontal_displacement_in']:.2f} in, so these results no longer depend strongly on fixed bases. Tests in both directions at twice the lateral force are included in member checks.

These lateral loads are diagnostic roof-level horizontal forces derived from 10/20 psf times a projected rectangle, not a code wind-pressure distribution. They are not San Diego wind or seismic design loads. The completed candidate uses P–Delta analysis; release/base sensitivities use separate cases. Global force balance, linear moment balance, a closed-form beam benchmark and an axial-force sign check were used. Explicit offset links use finite high stiffness, with a lower-stiffness sensitivity. Coordinates are rounded to 0.001 in to avoid spurious microscopic elements.

## Loads and lightweight envelope

The clear deck is 273.18 ft² after trimming 2 in from its east edge against the raised TE chord. Loads conservatively retain the earlier 275.64 ft² footprint. TE projects 1.25 in above the finished deck at the wall edge; its cladding/guard detail requires review. Uniform 40 psf live load is 11,026 lb. The storage case raises 36-in bands along the north and east edges to 75 psf. One 200-lb machine case is also applied over the general floor load. The hoist is 1,000 lb rated, with 25% assumed impact plus 100 lb assumed equipment weight, tested at three trolley positions on each rail. One hoist operates at a time. The separate exterior jib crane, landing ledge and a 1,000-lb concentrated load on plywood are not approved by this trolley analysis.

Dead-load ledger for the candidate:

- Primary steel plus connection allowance: {r['load_ledger_lb']['Dsteel']:,.0f} lb.
- Loft joists/deck allowance: {r['load_ledger_lb']['Dfloor']:,.0f} lb (12 psf).
- Roof assembly allowance: {r['load_ledger_lb']['Droof']:,.0f} lb (9.5 psf main sloped surface; 6.6 psf cap).
- Lightweight wall allowance: {r['load_ledger_lb']['Dwall']:,.0f} lb (4 psf gross wall surface).

A representative REC module weighs 50 lb over 22.4 ft², about 2.23 psf ([manufacturer data]({pvsource})). Metl-Span lists roughly 2.1–3.2 psf for the shown 2-in insulated metal-panel configurations ([panel weights]({roofsource})). These support retaining a lightweight assembly: solar above waterproof metal, foam insulation and metal interior skin. The remaining roof allowance covers secondary framing, fasteners, flashings and reserve. Product attachment, ventilation and the complete roof fire/waterproofing assembly remain to be specified.

The 125 psf storage sensitivity does NOT pass: maximum screened ratio {r['storage125_sensitivity_ratio']:.2f}. The owner’s 40 psf target is not a determination of the legally applicable occupancy load. Confirm that classification under [San Diego's adopted codes](https://www.sandiego.gov/development-services/codes-regulations) before treating these sizes as the design basis. Existing walls do not justify reducing the required load or safety factors.

## Foundations and existing walls

Uplift remains a structural design issue that can be addressed with an engineered load path through connections, anchors, reinforced foundations and soil. It has not been eliminated by assumption. In the service40 case S2 is {r['results']['service40']['reactions_lb']['S2']/1000:+.2f} kip and SW0 is {r['results']['service40']['reactions_lb']['SW0']/1000:+.2f} kip. Bracing redistributes forces. The reaction CSV includes the larger lateral-test demands; those are not final foundation design loads.

No footing dimensions have been approved. The old estimated 18-in by 36-in piers cannot be assumed adequate for uplift, overturning or soil bearing. New connections to the old walls must account for actual stiffness and differential movement; a rigid connection can transfer weight into an old wall even when its capacity is not credited in calculations. Do not use the previous 20 years of performance as a quantified reserve capacity.

## Build-around-existing check

The candidate is saved separately as Garage-Candidate-9.FCStd. The original Proposed-Garage.FCStd remains unchanged. CAD was reopened and all {clear.get('reopened_valid_members','pending')} candidate steel solids validated. The existing roof is unclad in that model; field clearances and cladding thickness still matter.

TE now clears the modeled old roof framing by a minimum of {clear.get('TE_min_distance_to_modeled_roof_framing_in',0):.2f} in. This does not include old roof cladding or erection tolerance; field measurement is required before accepting roof-first clearance.

Remaining modeled intersections involve: {', '.join(clashmembers) if clashes else 'none recorded in the available clearance check'}. See candidate9-clearance-check.json for each existing component. These require planned local openings or adjustment before erection; do not cut loaded existing framing based on this model. Roof-first means the complete tested braced frame and secondary roof restraint are installed, not that any partially erected sequence is stable.

The braced bays must be reviewed against windows, the covered walkway, the outbuilding and access. The main north garage-door opening is left clear. Upper north bracing may affect the adjacent window treatment.

## Secondary framing and remaining design

For the modeled approximately 109-in joist span at 16-in centers, a 1.5×7.25-in wood joist needs approximately {floorfb:,.0f} psi adjusted bending strength and {floorE/1e6:.2f} million psi modulus to meet the simple 75 psf live + 12 psf dead checks used here. This is a demand specification; species/grade, adjustments, hangers, bearing and plywood point-load capacity still need selection.

At a trial 48-in spacing and 256.25-in span, an E–W roof purlin needs roughly I = {roofI:.1f} in⁴ for the provisional roof-live L/240 comparison, and elastic section modulus at least {roofS:.1f} in³ for the stated factored gravity load. These are lower-bound property targets, not a cold-formed section design. A supplier/AISI check must include local/distortional buckling, continuity, uplift and bracing. Roof fasteners alone are not an automatically adequate diaphragm.

Still needed before fabrication: actual joint and HSS face checks; welds/bolts/gussets; member torsion/warping and complete applicable code interaction checks; rail flange/wheel contact and hoist side loads; site wind/seismic load cases and combinations; foundation/soil design; fire and property-line requirements; and erection-stage sequencing. A California structural engineer should verify and complete that design.

## Cost and reproducibility

This is the best-performing candidate tested in this study, not proof of the cheapest possible structure. W2 removal requires stronger TW diagonals; its earlier net steel saving was only about 150 lb, so avoided foundation work is the main potential benefit. Whether welding or bolting is cheaper depends on the connection details and shop/erection quotes. A hybrid with shop-fabricated truss sections and site connections is a pricing option, not an established winner.

Files include the Python model, stock catalog, geometry, load basis, member checks and every case reaction. Run candidate9.py with PyNiteFEA 3.0.0 after installing requirements.txt to repeat this candidate from the supplied prior selection input. Change design-basis.json for loads, re-export geometry when CAD changes, and compare all cases before accepting a revision. The historical trials have different scope/assumptions; candidate9 results are the current reference.

Compression uses the AISC E3 column curve; W bending screening includes lateral-torsional buckling with Cb=1. Axial/biaxial demands are combined conservatively with elastic capacities. These partial checks are not an automatic AISC compliance engine. [AISC specification formula reference](https://www.aisc.org/globalassets/aisc/publications/standards/a360-16-spec-and-commentary_march-2021.pdf), [Atlas HSS section properties](https://www.atlastube.com/wp-content/uploads/2018/04/A500-Square-Current.pdf), [PyNite analysis API](https://pynite.readthedocs.io/en/latest/FEModel3D.html).
'''
(P/'CANDIDATE-9-RESULTS.md').write_text(text)
with PdfPages(P/'Garage-Candidate-9-Results.pdf') as pdf:
 pdf.savefig(fig);pdf.savefig(fig2);pdf.savefig(fig3)
 lines=[]
 for line in text.splitlines():
  # Keep source URLs in the PDF as text; markdown report has clickable source links.
  lines.extend(textwrap.wrap(line.replace('**',''),112) or [''])
 for start in range(0,len(lines),48):
  f=plt.figure(figsize=(11.7,8.3));f.text(.045,.96,'\n'.join(lines[start:start+48]),va='top',fontsize=9.2,linespacing=1.22);pdf.savefig(f);plt.close(f)
plt.close('all')
print('Report and figures written')
