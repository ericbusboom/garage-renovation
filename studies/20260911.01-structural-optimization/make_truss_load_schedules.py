"""Make versioned exact nodal load packages and readable truss free-body diagrams."""
import os,json,csv,hashlib,textwrap
from pathlib import Path
os.environ['MPLCONFIGDIR']='/private/tmp/garage-wall-preview-mpl'
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
P=Path(__file__).resolve().parent;S=P/'truss-submodels';O=S/'point-loads';O.mkdir(exist_ok=True)
plt.rcParams.update({'font.size':9,'axes.spines.top':False,'axes.spines.right':False})
report=[]; datasets={}
for stage in ['complete','roof_first']:
 for group in ['TE','TW','TN','TS','T1']:
  stem=f'{group}-{stage}';meta=json.loads((S/(stem+'.json')).read_text());data=np.load(S/(stem+'.npz'))
  names=list(meta['nodes']);cases=list(meta['cases']);xyz=np.array(list(meta['nodes'].values()));F=data['F'].reshape(len(cases),len(names),6)
  boundary=set(meta['boundary_nodes']);positions={n:i for i,n in enumerate(names)}
  coord=1 if group in ['TE','TW'] else 0
  ordered=sorted(names,key=lambda n:(meta['nodes'][n][coord],meta['nodes'][n][2],n));labels={n:f'{group}-P{i+1:03d}' for i,n in enumerate(ordered)}
  nodes={labels[n]:dict(solver_node=n,xyz_CAD_in=meta['nodes'][n],kind='interface_action' if n in boundary else 'interior_applied_load',adjacent_members=meta['boundary_neighbors'].get(n,[])) for n in ordered}
  # Preserve full precision, all signs and all six components. No load rounding in solver inputs.
  loadcases={case:{labels[n]:F[ci,positions[n]].tolist() for n in ordered} for ci,case in enumerate(cases)}
  payload=dict(schema_version=1,truss=group,stage=stage,source_sha256=hashlib.sha256((S/(stem+'.npz')).read_bytes()).hexdigest(),force_order=['FX_lb','FY_lb','FZ_lb','MX_lb_in','MY_lb_in','MZ_lb_in'],solver_axes={'X':'east','Y':'up','Z':'north'},coordinate_order='CAD x east, y north, z up',nodes=nodes,combinations=meta['cases'],loads=loadcases,interface_displacements={case:{labels[n]:data['U'][ci,positions[n]*6:positions[n]*6+6].tolist() for n in ordered if n in boundary} for ci,case in enumerate(cases)},use='For current submodel: apply interior loads and prescribed interface displacements; interface actions are reaction targets, not additional applied loads. A force-driven free-body uses all vectors and needs correctly modeled boundary conditions without double counting reactions.',eligible_for_construction=False)
  (O/(stem+'-loads.json')).write_text(json.dumps(payload))
  with open(O/(stem+'-loads.csv'),'w') as f:
   w=csv.writer(f);w.writerow(['case','point','solver_node','kind','adjacent_members','x_east_in','y_north_in','z_up_in',*payload['force_order']])
   for ci,case in enumerate(cases):
    for n in ordered:
     v=F[ci,positions[n]]
     if np.max(np.abs(v))<.001:continue # CSV visibility filter only; JSON is unfiltered.
     w.writerow([case,labels[n],n,nodes[labels[n]]['kind'],'; '.join(meta['boundary_neighbors'].get(n,[])),*meta['nodes'][n],*v])
  # Check each complete free body, including lever arms and applied moments.
  force_res=F[:,:,:3].sum(axis=1);rsolver=xyz[:,[0,2,1]]
  moment_res=(F[:,:,3:]+np.cross(rsolver[None,:,:],F[:,:,:3])).sum(axis=1)
  force_norm=np.linalg.norm(F[:,:,:3],axis=2).sum(axis=1)
  moment_norm=(np.linalg.norm(F[:,:,3:],axis=2)+np.linalg.norm(np.cross(rsolver[None,:,:],F[:,:,:3]),axis=2)).sum(axis=1)
  relative=max(float(np.max(np.linalg.norm(force_res,axis=1)/np.maximum(1,force_norm))),float(np.max(np.linalg.norm(moment_res,axis=1)/np.maximum(1,moment_norm))))
  assert relative<1e-5,(stem,relative)
  # Recombine basic actions to establish independent load cases are reusable.
  comb_error=0
  for ci,case in enumerate(cases):
   rebuilt=sum((factor*F[cases.index('basic_'+basic)] for basic,factor in meta['cases'][case].items() if 'basic_'+basic in cases),start=np.zeros_like(F[ci]))
   comb_error=max(comb_error,float(np.max(np.abs(rebuilt-F[ci]))))
  assert comb_error<.1,(stem,comb_error)
  display_case='service_patches' if stage=='complete' else 'roof_first_service';ci=cases.index(display_case)
  down=float(-np.minimum(F[ci,:,1],0).sum());up=float(np.maximum(F[ci,:,1],0).sum())
  report.append(dict(truss=group,stage=stage,cases=len(cases),points=len(names),interfaces=len(boundary),max_free_body_relative_error=relative,max_combination_absolute_error=comb_error,display_case=display_case,sum_downward_equivalent_lb=down,sum_upward_equivalent_lb=up))
  datasets[stem]=(meta,F,cases,labels,ordered)
(O/'validation.json').write_text(json.dumps(report,indent=2))

def draw(group,stage,fig):
 meta,F,cases,labels,ordered=datasets[f'{group}-{stage}'];names=list(meta['nodes']);ix={n:i for i,n in enumerate(names)};boundary=set(meta['boundary_nodes']);coord=1 if group in ['TE','TW'] else 0
 case='service_patches' if stage=='complete' else 'roof_first_service';V=F[cases.index(case)]
 ax=fig.add_axes([.08,.55,.85,.32]);ax.set_title(f'{group} | {"Completed loft" if stage=="complete" else "Roof-first stage"} | {case}',fontsize=15,pad=16)
 for e in meta['elements']:
  if e['member'].startswith('@'):continue
  a,b=[meta['nodes'][n] for n in e['nodes']];ax.plot([a[coord],b[coord]],[a[2],b[2]],color='#657885',lw=1.25,zorder=1)
 label_nodes=set(sorted(boundary,key=lambda n:abs(V[ix[n],1]),reverse=True)[:6])
 for n in names:
  x,y=meta['nodes'][n][coord],meta['nodes'][n][2];fy=V[ix[n],1]
  if abs(fy)<20:continue
  color='#b3483d' if fy<0 else '#287968';height=np.clip(abs(fy)/450,2,20);start=y-height if fy>0 else y+height
  ax.annotate('',xy=(x,y),xytext=(x,start),arrowprops=dict(arrowstyle='->',color=color,lw=1 if n in boundary else .5,alpha=1 if n in boundary else .4))
  if n in label_nodes and abs(fy)>=1000:ax.annotate(f'{labels[n]}\n{abs(fy):,.0f} lb',xy=(x,start),xytext=(2,4 if fy<0 else -9),textcoords='offset points',fontsize=6,color=color)
 ax.set_xlabel('North station from south wall (in)' if coord==1 else 'East station from west wall (in)');ax.set_ylabel('Height above datum (in)');ax.grid(alpha=.15);ax.margins(.08,.3)
 rows=[]
 for n in ordered:
  if n not in boundary:continue
  v=V[ix[n]];neighbors=', '.join(meta['boundary_neighbors'].get(n,[]));p=meta['nodes'][n]
  rows.append([labels[n],f'{p[coord]:.2f}',f'{p[2]:.2f}',textwrap.shorten(neighbors,36,placeholder='…'),f'{v[1]:,.0f}',f'{v[0]:,.0f}',f'{v[2]:,.0f}'])
 tax=fig.add_axes([.05,.065,.9,.39]);tax.axis('off');table=tax.table(cellText=rows,colLabels=['Point','Station in','Height in','Connected to','FY lb','FX lb','FZ lb'],cellLoc='left',colWidths=[.13,.10,.10,.33,.12,.11,.11],bbox=[0,0,1,1]);table.auto_set_font_size(False);table.set_fontsize(6.3 if len(rows)>30 else 7)
 for (r,c),cell in table.get_celld().items():
  cell.set_linewidth(.2)
  if r==0:cell.set_facecolor('#dde8ed')
  elif r%2==0:cell.set_facecolor('#f3f6f7')
 fig.text(.06,.47,'Interface actions: +FY upward, −FY downward. FX east; FZ north. Vertical arrows only; six largest interface forces labeled.\nMoments and exact vectors are in the CSV/JSON. Interior loads are also included there. Rounded labels are for reading only.',fontsize=8)
 fig.text(.06,.02,'PRELIMINARY • Candidate 9, W2 removed • No old-wall capacity credited • Linear reference; refresh after stiffness changes.',fontsize=8,color='#59636a')

with PdfPages(O/'Truss-Point-Loads.pdf') as pdf:
 fig=plt.figure(figsize=(11,8.5));fig.text(.08,.91,'Truss point-load schedules',fontsize=23);fig.text(.08,.85,'Candidate 9 • Preliminary independent-analysis inputs',fontsize=13)
 text='''Load basis retained from the agreed study:\n• Loft: 40 psf live; 75 psf in north/east storage bands; 12 psf floor dead load.\n• Roof: 9.5 psf sloped assembly, 6.6 psf cap; roof live load 20 psf in plan.\n• Metal walls: 4 psf. Actual modeled steel weight plus 10% connection allowance.\n• Hoist: 1,000 lb lifted + 25% impact + 100 lb equipment = 1,350 lb point action.\n  Quarter, half and three-quarter span positions on B2 and T1; one hoist at a time.\n\nEach truss receives only its own nodal loads and transferred connection actions.\nThere are separate basic-load cases, service combinations and strength combinations.\nDiagnostic lateral/uplift and 125 psf storage cases are retained separately, not approved loads.\n\nUse the interior loads with the exported interface movements for baseline replay.\nAt those restrained interfaces, listed actions are comparison reactions, NOT extra loads.\nFor optimization, model the surrounding stiffness or refresh the global model each iteration.\n\nThe following pages show the completed storage case and roof-first service case.\nEvery signed 3D force and moment, load case and exact point location is in the CSV/JSON.\nFloor/roof load stations are not shifted to panel joints: doing that could hide chord bending.\n\nThese schedules are a starting load set, not final building-code or construction approval.\nRoof framing distribution, joints, bracing, site wind/seismic, occupancy and foundations\nremain design inputs to verify. Existing garage walls provide no assumed capacity.'''
 fig.text(.08,.78,text,fontsize=11,va='top',linespacing=1.45);pdf.savefig(fig);plt.close(fig)
 for group in ['TE','TW','TN','TS','T1']:
  for stage in ['complete','roof_first']:
   fig=plt.figure(figsize=(11,11));draw(group,stage,fig);pdf.savefig(fig)
   if stage=='complete':fig.savefig(O/(group+'-point-loads.png'),dpi=140)
   plt.close(fig)
md='''# Truss point-load schedules

[Open the PDF](Truss-Point-Loads.pdf)

The five trusses each have a full-precision JSON and a CSV for completed and roof-first stages. JSON contains every case and point; CSV omits only rows whose six components are all below 0.001 in their respective units. Point labels are stage-specific, with original solver node IDs retained. Coordinates and six component units are explicitly labeled.

Basic cases (`basic_Droof`, `basic_Dfloor`, `basic_Dsteel`, `basic_Dwall`, live-load and individual hoist cases) can be combined linearly using the included factors. The basic actions include the whole frame's response to each source, not just direct loads. Keep signed forces and moments together. Do not add service and strength cases together or double-count the basic cases.

**Boundary actions include the required restraint reactions and any directly applied load at the shared node.** Use interior actions as applied loads and interface movements as the boundary conditions for the existing local replay programs. The interface forces are verification targets. They cannot all be applied as extra loads at fixed supports. For free-body analysis the complete vectors balance; boundary modeling for an optimized truss must be updated as discussed in the parent README.

These loads use Candidate 9 with W2 removed and the existing agreed load allowances. The PDF explains those allowances. Actual steel self-weight must be updated when sections change. One operating hoist is modeled, not two simultaneous hoists. The 75 psf storage case and hoist service cases are separate; strength hoist cases combine storage and the hoist. No arbitrary safety factor has been added to already factored cases.

The JSON contains both applied nodal forces and moments, consistent with [PyNite's nodal-load interface](https://pynite.readthedocs.io/en/latest/node.html). Keep the supplied solver axes for forces, rotations and moments.

## Verification

All load combinations were reconstructed from the basic load cases, and each individual truss free body was checked for force and moment equilibrium. Numerical results are in `validation.json`. The independent linear submodel replay is also rerun for all ten models. This verifies extraction/replay, not structural adequacy or final load selection.
'''
(O/'README.md').write_text(md)
print(json.dumps(report,indent=2))
