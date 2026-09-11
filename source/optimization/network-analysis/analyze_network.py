"""Read explicit network JSON, solve with PyNite, render that same model natively."""
import os,json,argparse,time
from pathlib import Path
os.environ.setdefault('MPLCONFIGDIR','/private/tmp/garage-network-mpl')
import numpy as np
from Pynite import FEModel3D
P=Path(__file__).resolve().parent

def model_from_file(d,case):
 m=FEModel3D()
 for name,p in d['materials'].items():m.add_material(name,p['E'],p['G'],p['nu'],p['rho'],p['Fy'])
 for name,p in d['sections'].items():m.add_section(name,p['A'],p['Iy'],p['Iz'],p['J'])
 for name,xyz in d['nodes'].items():m.add_node(name,*xyz)
 for e in d['elements']:
  m.add_member(e['id'],e['i'],e['j'],e['material'],e['section'])
  if any(e['releases']):m.def_releases(e['id'],*e['releases'])
 for n in d['boundary_nodes']:
  m.def_support(n,True,True,True,True,True,True)
  for direction,v in zip(['DX','DY','DZ','RX','RY','RZ'],d['reference'][case]['displacements'][n]):m.def_node_disp(n,direction,v)
 for n,values in d['loads'][case].items():
  for direction,v in zip(['FX','FY','FZ','MX','MY','MZ'],values):
   if v:m.add_node_load(n,direction,v,'input')
 m.add_load_combo(case,{'input':1.})
 m.analyze_linear(check_stability=True)
 # No undocumented internal splits or hidden connectivity in this explicit mesh.
 assert all(len(member.sub_members)==1 for member in m.members.values()),'Unexpected implicit member subdivision'
 return m

def render(m,d,case,stem,modes=None):
 import pyvista as pv
 pv.OFF_SCREEN=True
 from Pynite.Rendering import Renderer
 r=Renderer(m);r.theme='print';r.combo_name=case;r.annotation_size=.55;r.show_labels=False;r.render_nodes=True;r.render_loads=False
 r.plotter.window_size=[2000,1000]
 xyz=np.array(list(d['nodes'].values()));center=(xyz.min(0)+xyz.max(0))/2
 axis=np.array([-1,0,0]) if d['truss'] in ['TE','TW'] else np.array([0,0,1])
 def decorate(plotter):
  plotter.camera_position=[(center+axis*1000).tolist(),center.tolist(),[0,1,0]]
  plotter.enable_parallel_projection();plotter.reset_camera()
  station=2 if d['truss'] in ['TE','TW'] else 0
  plotter.camera.parallel_scale=max(np.ptp(xyz[:,1])/2,np.ptp(xyz[:,station])/4)*1.22
  plotter.add_text(d['truss']+' | '+d['stage']+' | '+('Corrected connection candidate' if 'proposed_connection_changes' in d else 'PyNite solved network'),position='upper_left',font_size=16,color='#203344')
  plotter.add_text('All physical members AND connection-offset elements shown. Nodes are real solver nodes.\nBoundary glyphs represent imposed global-frame movements, not additional ground supports.',position='lower_left',font_size=10,color='#42515c')
 r.post_update_callbacks.append(decorate)
 for mode in (modes or ['network','deformed','loads']):
  r.deformed_shape=mode=='deformed';r.deformed_scale=20;r.render_loads=mode=='loads'
  r.update(reset_camera=False,off_screen=True)
  if mode=='deformed':r.plotter.add_text('RED: displacement x20 | '+case,position='upper_right',font_size=12,color='#c0392b')
  if mode=='loads':r.plotter.add_text('Applied interior nodal loads | '+case,position='upper_right',font_size=12,color='#203344')
  r.plotter.screenshot(str(P/(stem+'-'+mode+'.png')))
  if mode=='network' and d['stage']=='complete':r.plotter.trame.export_html(str(P/(stem+'-interactive.html')))
 r.plotter.close()

def run(path,make_images=True):
 d=json.loads(path.read_text());stem=path.name.replace('.network.json','');results={};start=time.time()
 for case in d['loads']:
  m=model_from_file(d,case)
  U={n:[getattr(p,k)[case] for k in ['DX','DY','DZ','RX','RY','RZ']] for n,p in m.nodes.items()}
  du=max(abs(U[n][i]-d['reference'][case]['displacements'][n][i]) for n in U for i in range(6))
  rx={n:[getattr(m.nodes[n],k)[case] for k in ['RxnFX','RxnFY','RxnFZ','RxnMX','RxnMY','RxnMZ']] for n in d['boundary_nodes']}
  dr=max(abs(rx[n][i]-d['reference'][case]['interface_actions'][n][i]) for n in rx for i in range(6))
  if not d.get('proposed_connection_changes'):
   assert du<1e-5,(stem,case,'displacement mismatch',du)
   assert dr<.1,(stem,case,'reaction mismatch',dr)
  total=np.zeros(6);norms=np.zeros(2)
  for n,xyz0 in d['nodes'].items():
   action=np.array(d['loads'][case].get(n,[0.]*6))+np.array(rx.get(n,[0.]*6))
   total[:3]+=action[:3];total[3:]+=action[3:]+np.cross(xyz0,action[:3])
   norms[0]+=np.linalg.norm(action[:3]);norms[1]+=np.linalg.norm(action[3:])+np.linalg.norm(np.cross(xyz0,action[:3]))
  equilibrium=max(np.linalg.norm(total[:3])/max(norms[0],1),np.linalg.norm(total[3:])/max(norms[1],1))
  assert equilibrium<1e-5,(stem,case,'equilibrium',equilibrium)
  forces={}
  for e in d['elements']:
   mm=m.members[e['id']];forces[e['id']]=dict(physical_member=e['physical_member'],kind=e['kind'],global_end_actions=next(iter(mm.sub_members.values())).F(case).ravel().tolist(),axial_mid_lb=mm.axial(mm.L()/2,case),My_mid_lb_in=mm.moment('My',mm.L()/2,case),Mz_mid_lb_in=mm.moment('Mz',mm.L()/2,case))
  results[case]=dict(global_equilibrium_relative_error=float(equilibrium),max_reference_displacement_error=du,max_reference_action_error=dr,max_vertical_displacement_in=max(abs(v[1]) for v in U.values()),node_displacements=U,interface_reactions=rx,element_forces=forces)
  if make_images and case==('service_patches' if d['stage']=='complete' else 'roof_first_service'):render(m,d,case,stem)
  print(stem,case,'solved corrected candidate' if d.get('proposed_connection_changes') else 'verified',flush=True)
 result=dict(solver='PyNiteFEA 3.0.0',input_network=path.name,audit=d['audit'],analysis='Linear 3D frame elements; imposed global interface movements',eligible_for_construction=False,proposed_connection_changes=d.get('proposed_connection_changes',[]),cases=results,elapsed_seconds=time.time()-start)
 (P/(stem+'-results.json')).write_text(json.dumps(result))
 return dict(model=stem,cases=len(results),max_displacement_error=max(x['max_reference_displacement_error'] for x in results.values()),max_action_error=max(x['max_reference_action_error'] for x in results.values()),audit=d['audit'])
if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('network',nargs='?');parser.add_argument('--no-images',action='store_true');parser.add_argument('--images-only',action='store_true');args=parser.parse_args()
 paths=[Path(args.network)] if args.network else sorted(P.glob('*.network.json'))
 if args.images_only:
  for path in paths:
   d=json.loads(path.read_text());case='service_patches' if d['stage']=='complete' else 'roof_first_service'
   render(model_from_file(d,case),d,case,path.name.replace('.network.json',''),modes=['network','deformed'])
  raise SystemExit(0)
 reports=[run(path,not args.no_images) for path in paths]
 (P/'run-validation.json').write_text(json.dumps(reports,indent=2))
