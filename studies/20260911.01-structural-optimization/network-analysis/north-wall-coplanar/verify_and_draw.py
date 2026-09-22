"""Replay the unique whole-frame network; native PyNite views are filtered global model views."""
import os,json,copy,csv
from pathlib import Path
os.environ.setdefault('MPLCONFIGDIR','/private/tmp/garage-network-mpl')
import numpy as np
from Pynite import FEModel3D
P=Path(__file__).resolve().parent

def build(d):
 m=FEModel3D();m.add_material('steel',29e6,29e6/2.6,.3,0,50000)
 for k,s in d['sections'].items():m.add_section(k,**s)
 for k,v in d['nodes'].items():m.add_node(k,*v)
 for e in d['elements']:
  m.add_member(e['id'],e['i'],e['j'],'steel',e['section'])
  if any(e['releases']):m.def_releases(e['id'],*e['releases'])
 for n,v in d['supports'].items():m.def_support(n,*v)
 for n,loads in d['nodal_loads'].items():
  for direction,value,case in loads:m.add_node_load(n,direction,value,case)
 for k,v in d['combinations'].items():m.add_load_combo(k,v)
 m.analyze_linear(check_stability=True)
 return m

def verify(m,d):
 du=0.;force_error=0.;moment_error=0.;normalized=0.
 for case,ref in d['reference'].items():
  for n,u in ref['displacements'].items():du=max(du,max(abs(getattr(m.nodes[n],key)[case]-v) for key,v in zip(['DX','DY','DZ','RX','RY','RZ'],u)))
  # Use separate case-wide force/moment scales so a near-zero component from
  # cancellation is not tested relative to itself. Displacements remain absolute.
  force_scale=max(abs(v) for row in ref['reactions'].values() for v in row[:3])
  moment_scale=max(abs(v) for row in ref['reactions'].values() for v in row[3:])
  for n,row in ref['reactions'].items():
   for i,(key,v) in enumerate(zip(['RxnFX','RxnFY','RxnFZ','RxnMX','RxnMY','RxnMZ'],row)):
    err=abs(getattr(m.nodes[n],key)[case]-v)
    if i<3:force_error=max(force_error,err);tol=.001+1e-4*force_scale
    else:moment_error=max(moment_error,err);tol=.01+1e-4*moment_scale
    normalized=max(normalized,err/tol)
 assert du<1e-5 and normalized<1,(du,force_error,moment_error,normalized)
 return dict(cases=len(d['combinations']),max_displacement_error=float(du),max_force_error_lb=float(force_error),max_moment_error_lb_in=float(moment_error),max_normalized_error=float(normalized),tolerance='Displacements1e-5; forces0.001+1e-4*case force scale; moments0.01+1e-4*case moment scale')

def draw(m,d,group,cols,extras=(),iso=False):
 import pyvista as pv
 from Pynite.Rendering import Renderer
 pv.OFF_SCREEN=True
 physical={x['id']:x for x in d['physical_members']};groups=['TE','TW','T1'] if group=='T1' else ['TN'] if group=='NORTH' else [group]
 selected={k for k,v in physical.items() if v.get('truss') in groups or k in cols or any(k.startswith(e) for e in extras)}
 if group=='ALL':selected=set(physical)
 links={c['id'] for c in d['connections'] if all(c[s]['member_id'] in selected for s in ['from','to'])}
 elems=[e for e in d['elements'] if e['physical_member'] in selected or e['connection_id'] in links]
 keys={e['id'] for e in elems};nodes={e[s] for e in elems for s in ['i','j']}
 # Rendering subset only: its displacements/forces come from the solved whole frame.
 view=copy.deepcopy(m);view.members={k:v for k,v in view.members.items() if k in keys};view.nodes={k:v for k,v in view.nodes.items() if k in nodes}
 r=Renderer(view);r.theme='print';r.show_labels=False;r.annotation_size=.7;r.render_loads=False;r.render_nodes=True;r.combo_name='service_patches';r.plotter.window_size=[2100,1500]
 xyz=np.array([d['nodes'][n] for n in nodes]);center=(xyz.min(0)+xyz.max(0))/2
 axis=np.array([-1,.5,1]) if iso else np.array([-1,0,0]) if group in ['TE','TW'] else np.array([0,0,1])
 r.update(reset_camera=False,off_screen=True)
 pl=r.plotter;pl.camera_position=[(center+axis*1000).tolist(),center.tolist(),[0,1,0]];pl.enable_parallel_projection();pl.reset_camera();pl.camera.zoom(.80)
 pl.add_text(group+' | '+('Support path' if iso else 'Corrected wall elevation'),position='upper_left',font_size=23,color='#203344')
 notes='Entire north-wall frame aligned at north coordinate 253 in; joints share nodes.\nPreliminary fixed-base model; connection and foundation design remains.'
 if group=='T1':notes='T1 bears on TE and TW; those trusses transfer its load to the ground columns.\nNo new posts beneath T1. This is a filtered 3D view of the globally solved frame.'
 pl.add_text(notes,position='lower_left',font_size=13,color='#34495e')
 labels=[];points=[]
 for mid in cols:
  if mid not in physical:continue
  a=physical[mid]['a'];points.append([a[0],-12,a[1]]);labels.append(mid.replace(' / ','/'))
 if points:pl.add_point_labels(points,labels,font_size=18,point_size=0,shape_opacity=.85,always_visible=True)
 if group=='TN':
  pl.add_point_labels([[155.25,148,253]],['Upper jamb only'],font_size=16,point_size=4,always_visible=True)
  pl.add_text('Flat upper chord axis: 18 ft 8 1/4 in\nLower chord axis: 9 ft 7 in\nOverall chord run: 23 ft 5 1/2 in',position='upper_right',font_size=14,color='#34495e')
 pl.screenshot(str(P/(group+'-wall.png')));pl.trame.export_html(str(P/(group+'-interactive.html')));pl.close()
 if group=='TN':
  detail=Renderer(view);detail.theme='print';detail.show_labels=False;detail.annotation_size=.5;detail.render_nodes=True;detail.render_loads=False;detail.combo_name='service_patches';detail.plotter.window_size=[2100,850]
  detail.update(reset_camera=False,off_screen=True);dp=detail.plotter;dp.camera_position=[[104.25,215.625,1253],[104.25,215.625,253],[0,1,0]];dp.enable_parallel_projection();dp.camera.parallel_scale=32
  dp.add_text('TN | Corrected over-door mini-truss',position='upper_left',font_size=23,color='#203344')
  dp.add_text('4 equal panels x 25 1/2 in = 8 ft 6 in between support axes | Chord-axis depth: 17 1/4 in',position='lower_left',font_size=15,color='#34495e')
  dp.screenshot(str(P/'TN-door-detail.png'));dp.close()

if __name__=='__main__':
 validation={}
 for stage in ['complete','roof_first']:
  d=json.loads((P/(stage+'.network.json')).read_text());m=build(d);validation[stage]=verify(m,d);print(stage,validation[stage],flush=True)
  if stage!='complete':continue
  for g,cols,extras,iso in [
   ('TN',['W4','N1 / U-W','N2'],['BR-N-'],False),
   ('NORTH',['W4','N1 / U-W','N2'],['BR-N-'],True),
   ('ALL',['SW0','W1','W3','W4','S1','S2','S3','N2','N1 / U-W'],[],True)]:
   draw(m,d,g,cols,extras,iso);print('Rendered',g,flush=True)
  with open(P/'column-reactions.csv','w') as f:
   w=csv.writer(f);w.writerow(['column','case','Fx_lb','vertical_Fy_lb','Fz_lb','Mx_lb_in','My_lb_in','Mz_lb_in'])
   for member in d['physical_members']:
    if not member.get('axis_source',{}).get('ground_post'):continue
    a=member['a'];n=min(d['supports'],key=lambda n:np.linalg.norm(np.array(d['nodes'][n])-[a[0],a[2],a[1]]))
    assert np.linalg.norm(np.array(d['nodes'][n])-[a[0],a[2],a[1]])<.01
    for case in d['combinations']:w.writerow([member['id'],case,*d['reference'][case]['reactions'][n]])
 (P/'validation.json').write_text(json.dumps(validation,indent=2))
