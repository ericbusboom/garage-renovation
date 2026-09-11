"""Generate the final report from solved results; no analysis or geometry changes."""
import json,csv,textwrap,shutil
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
P=Path(__file__).resolve().parent
read=lambda f:json.loads((P/f).read_text())
s=read('selected-summary.json'); rows=read('member-schedule.json'); baseline=read('audited-original.json'); result=read('global-complete-PDelta.json'); basis=read('load-basis.json')
web=read('web-pinned.json'); base=read('base-pinned-confirmation.json')
# Preserve primary-envelope utilization and expose separate connection sensitivities.
for r in rows:
 for tag,d in [('web_pinned',web),('base_pinned',base)]:
  r[tag+'_utilization']=d['member_screen'][r['member']]['ratio']
with (P/'member-schedule.csv').open('w') as f:
 w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
(P/'member-schedule.json').write_text(json.dumps(rows,indent=2))
shutil.copyfile(P.parent/'north-wall-coplanar/geometry.json',P/'geometry.json')
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.spines.top':False,'axes.spines.right':False})
fig,axs=plt.subplots(1,2,figsize=(12,5),gridspec_kw={'width_ratios':[1,1.4]})
weights=[baseline['steel_weight_lb'],s['steel_lb']]
axs[0].bar(['Starting frame','Selected candidate'],weights,color=['#95a4b2','#147b85'])
for i,v in enumerate(weights):axs[0].text(i,v+110,f'{v:,.0f} lb',ha='center',weight='bold')
axs[0].set_ylim(0,10000);axs[0].set_ylabel('Primary member steel (lb)');axs[0].set_title('38% less primary steel')
labels=['Main load envelope','Pinned webs*','Pinned bases*','125 psf storage','No chord restraint']
vals=[s['strength_ratio'],web['max_screen_ratio'],base['max_screen_ratio'],1.5997188281,8.4415535715]
axs[1].barh(labels,vals,color=['#147b85']*3+['#b95332']*2);axs[1].invert_yaxis();axs[1].axvline(1,color='#273b4a',linestyle='--');axs[1].set_xlabel('Member demand / screened capacity (limit = 1.0)')
for i,v in enumerate(vals):axs[1].text(v+.08,i,f'{v:.2f}',va='center')
axs[1].set_xlim(0,9.3);axs[1].set_title('Conditions matter as much as section size')
fig.suptitle('Garage — fixed-geometry member sizing',fontsize=18,weight='bold');fig.text(.04,.025,'*Separate sensitivity runs. Requires chord restraint at ≤6 ft. Preliminary sizing, not a fabrication design.',fontsize=10)
fig.tight_layout(rect=[0,.07,1,.94]);fig.savefig(P/'Sizing-Summary.png',dpi=180)
pdf=PdfPages(P/'Fixed-Geometry-Member-Sizing.pdf');pdf.savefig(fig);plt.close(fig)
page=1

def sheet(title, paragraphs=(), table=None, widths=None):
 global page
 page+=1;f=plt.figure(figsize=(11,8.5));f.text(.06,.93,title,fontsize=20,weight='bold',color='#203749');y=.87
 for para in paragraphs:
  lines=textwrap.wrap(para,125);f.text(.06,y,'\n'.join(lines),va='top',fontsize=10.5,linespacing=1.5);y-=.028*len(lines)+.025
 if table:
  headers,data=table;ax=f.add_axes([.055,.095,.89,max(.12,y-.11)]);ax.axis('off');t=ax.table(cellText=data,colLabels=headers,loc='upper center',cellLoc='left',colLoc='left',colWidths=widths);t.auto_set_font_size(False);t.set_fontsize(8.7);t.scale(1,1.5)
  for (i,j),cell in t.get_celld().items():
   cell.set_edgecolor('#d8e0e5')
   if i==0:cell.set_facecolor('#203749');cell.set_text_props(color='white',weight='bold')
 f.text(.06,.035,f'Garage | Fixed geometry | 10 September 2026 | Preliminary analytical study | {page}',fontsize=8,color='#52616c');pdf.savefig(f);plt.close(f)

sheet('Result and scope',[
 f'The lightest candidate found in this discrete stock search weighs {s["steel_lb"]:,.0f} lb, compared with {baseline["steel_weight_lb"]:,.0f} lb of starting primary steel: a reduction of {baseline["steel_weight_lb"]-s["steel_lb"]:,.0f} lb (38%). This is a local search result, not proof of the absolute minimum. Geometry, supports and truss arrangement were held fixed.',
 'The audited starting frame exceeds the member screen at W3 (1.065 utilization). Downsizing therefore was not applied uniformly: W3 needs a thicker wall while other members can become lighter. The nine-column layout retains the previously accepted removal of W2; no column was removed in this sizing round.',
 'Main completed and roof-first load envelopes reach 0.951 utilization. Separate pinned-web and pinned-base completed-stage runs reach 0.986 and 0.987. These checks are separate, not a combined pinned-web/pinned-base model. A utilization below 1 means only that the implemented member screen passes.',
 'The result requires positive lateral restraint of chords/rails at no more than 6 ft. Without that restraint the capacity screen fails (8.44). The 125 psf storage sensitivity also fails (1.60). Occupancy classification and the applicable code live load remain unresolved.',
 'Weight excludes secondary roof/floor framing, cladding, PV, actual connection steel and foundations. Their dead loads are budgeted separately. Connections, chord restraint, trolley flange loading, foundations and site-specific wind/seismic design are not complete; these sizes are not a purchase or fabrication schedule.'
])
sheet('Audited gravity-load basis',[
 'Main loft: 18 ft 8 1/4 in east-west by 14 ft 9 in north-south = 275.64 sq ft. No support capacity is credited to the old walls or slab. Existing garage weight is not assigned to the new independent frame.',
 'Assembly weights below are provisional budgets informed by manufacturer weights, not a completed material takeoff. A product or load-path change requires another solve.'
],(['Item','Basis','Applied load / qualification'],[
 ['Main solar roof','10 psf, actual slope area','3 PV/glass + 3 skin + 3 secondary steel + 1 reserve'],
 ['Rear hip cap','7 psf, actual surface area','3 insulated skin + 3 secondary frame + 1 trim'],
 ['All roof dead load','Combined surfaces','6,393 lb'],
 ['Roof live load','20 psf, horizontal projection','13,388 lb; final site requirements pending'],
 ['Upper metal walls','4 psf, gross surface','2,331 lb; includes panel/girt allowance'],
 ['Loft floor dead','12 psf, excluding primary steel','3,308 lb; plywood/joists/hardware/reserve'],
 ['Loft live','40 psf general','11,026 lb'],
 ['Heavier storage bands','75 psf in approximately 3 ft N/E bands','14,141 lb total floor live in this case'],
 ['West balcony','13.33 sq ft; 12 dead + 100 live psf','160 lb dead + 1,333 lb live; eccentric onto TW'],
 ['Machine case','Additional 200 lb','Strength case with the storage-band loading'],
 ['Moving hoist','1,000 lb rated, one hoist at a time','1.25 impact + 100 lb equipment = 1,350 lb'],
 ['Primary steel + joints','Catalog weight + 10% allowance','5,819 lb; recomputed at every sizing iteration'],
 ['Total new dead load','All above dead components','18,011 lb, including connection allowance']
]),[.21,.29,.50])
sheet('Analysis and optimization method',[
 'PyNite 3D frame elements retain axial, bending, shear and torsion behavior. Shared columns are modeled once in the global system; support reactions are not arbitrarily divided in half between trusses. North-wall members and W4/N1/N2 remain coplanar at north coordinate 253 in.',
 'Roof surface loads transfer to TE/TW through assumed east-west purlins at approximately 4 ft plan stations, with force and first moment preserved. The rear cap frame is a separate lightweight allowance. Those secondary members and their restraint connections still require design. Loft reactions transfer through the retained floor-beam/truss layout.',
 'A 66-section AISC v16 catalog supplies published weight and geometric properties. B2 and the T1 floor rail remain W shapes at no more than 8 in depth. Existing 4 in column envelopes and the 6 in N1 envelope are retained. Thin HSS walls outside the compact-wall screening range are rejected.',
 'For each candidate, section self-weight and global stiffness are updated, demands are recomputed, and strength/serviceability failures are rejected. The completed structure uses second-order P-delta analysis; the roof-first stage is linear and is not a complete erection-stability assessment.',
 'The capacity routine screens axial compression buckling, tension, elastic biaxial bending, W-section lateral-torsional buckling and shear. HSS uses an additional conservative linear normal/bending/shear/torsion interaction. K=1 and a 72 in maximum restrained chord length are assumptions. This is a partial AISC-based screening routine, not a complete AISC 360 compliance engine.',
 'Independent JSON reconstruction reproduced all 76 exported linear cases (56 complete, 20 roof-first). Maximum replay displacement difference was 8.24e-7 in/radian; force difference 0.016 lb and moment difference 0.045 lb-in. A simple-beam benchmark matches its closed-form deflection. These validate implementation/replay, not the physical connection assumptions.'
])
sheet('Serviceability and unresolved design checks',[
 'These are primary-frame study targets, not approval of the full floor, roof or hoist system. Floor joists, deck, vibration, glazing support and rail-manufacturer limits require their own checks.',
 'The first pinned-base run tripped a near-zero-load equilibrium tolerance by 0.000037 lb. Repeating the actual service/strength combinations without the zero-total-gravity basic lateral cases solved successfully. It was not evidence of physical instability.'
],(['Check','Calculated','Study limit / outcome'],[
 ['Floor movement, live with bands','0.494 in','0.712 in (span/360)'],
 ['Floor movement, total with hoist','0.749 in','1.068 in (span/240)'],
 ['B2 incremental hoist movement','0.145 in','0.569 in study target'],
 ['T1 incremental hoist movement','0.049 in','0.569 in study target'],
 ['Roof total movement','0.240 in','1.054 in study target'],
 ['Separate pinned-web screen','0.986 utilization','Passes implemented member screen'],
 ['Separate pinned-base screen','0.987 utilization','Passes implemented member screen'],
 ['Unrestrained chord sensitivity','8.44 utilization','FAIL: real chord restraint is necessary'],
 ['125 psf storage sensitivity','1.60 utilization','FAIL: selected sizes do not cover this use'],
 ['Wind, seismic, uplift','Sensitivity loads only','Site design and connections unresolved'],
 ['Hoist and external jib crane','Vertical traveling hoist modeled','Rail flange/wheels unverified; jib not designed'],
 ['Footings and connections','Not sized','No construction release']
]),[.38,.24,.38])
for group in ['TN','TE','TW','TS','T1','ALL']:
 page+=1;f=plt.figure(figsize=(11,8.5));ax=f.add_axes([.025,.055,.95,.90]);ax.imshow(plt.imread(P/(group+'-wall.png')));ax.axis('off');f.text(.04,.02,f'Native PyNite network view | Primary member sizes follow | Page {page}',fontsize=8);pdf.savefig(f);plt.close(f)
 chosen=[r for r in rows if r['truss']==group] if group!='ALL' else [r for r in rows if r['truss']=='columns/beams']
 for k in range(0,len(chosen),21):
  sheet(group+' — member sizes'+(' (continued)' if k else ''),['Utilization is the main completed/roof-first/P-delta envelope. Separate connection-sensitivity values are included in the CSV. Member labels identify physical pieces; lengths are centerline lengths, not cutting dimensions.'],(['Member','Section','Length ft','Weight lb','Util.'],[[r['member'],r['section'],f'{r["length_ft"]:.2f}',f'{r["weight_lb"]:.1f}',f'{r["utilization"]:.3f}'] for r in chosen[k:k+21]]),[.41,.27,.10,.11,.11])
braces=[r for r in rows if r['truss'].startswith('BR-')]
sheet('Bracing — member sizes',['These physical braces are included in primary steel weight. Chord lateral restraint at 6 ft remains an additional required secondary system, not implied by the presence of these braces.'],(['Member','Section','Length ft','Weight lb','Util.'],[[r['member'],r['section'],f'{r["length_ft"]:.2f}',f'{r["weight_lb"]:.1f}',f'{r["utilization"]:.3f}'] for r in braces]),[.41,.27,.10,.11,.11])
sheet('Sources and how to use this study',[
 'Canadian Solar TOPHiKu6 CS6.1-54TM-H datasheet (2026): 50.7 lb over about 21.96 sq ft, or about 2.31 psf for the module alone. The study reserves 3 psf for PV or matching infill glass; actual cut/infill panels may differ.',
 'Metl-Span CF/PIR and CFR panel weight tables inform the 3 psf insulated metal-skin budget. Profile, gauge, insulation and attachment choices must be confirmed. The floor and secondary-steel allowances are preliminary engineering budgets.',
 'Sources are linked below and recorded as full URLs in load-basis.json. San Diego occupancy classification and site lateral/environmental loads must be resolved before the selected sizes can become a construction design.',
 'Use member-schedule.csv for each member and column; column-reactions.csv for exported linear load-case base actions; global-complete-PDelta.json for second-order results; complete.network.json and roof_first.network.json for a rebuildable analysis model. Interactive HTML views are native solver scenes.',
 'Next phase: first establish physical chord restraint, connections and trolley compatibility; then compare alternative layouts and fabrication cost. A lighter primary member can require heavier secondary bracing or more fabrication, so lowest primary weight is not necessarily lowest installed cost.'
])
# Add a compact linked sources page.
f=plt.figure(figsize=(11,8.5));f.text(.06,.92,'Primary references',fontsize=20,weight='bold')
for i,(name,url) in enumerate(basis['sources'].items()):
 f.text(.07,.82-i*.12,name.upper(),fontsize=12,weight='bold');f.text(.07,.78-i*.12,'Open official source',fontsize=11,color='#147b85',url=url)
f.text(.07,.13,'AISC capacity implementation: partial preliminary screen; see optimize.py and iterate_design.py.',fontsize=10)
pdf.savefig(f);plt.close(f);pdf.close()
print('Wrote PDF, summary PNG and updated schedule')
