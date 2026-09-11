#!/usr/bin/env python3
"""Apply a global wall-top underside datum to all jack and hip rafters."""
import os,sys,json,hashlib,traceback
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parent
os.environ.setdefault('QT_QPA_PLATFORM','offscreen');os.environ.setdefault('FONTCONFIG_FILE','/etc/fonts/fonts.conf')
sys.path.insert(0,'/opt/freecad-1.1.3/usr/lib')
import FreeCAD as A, FreeCADGui as G, Part
from roof_tail_tools import apply_global_datum,validate_tail_cuts,global_shape
R={'request_id':'RAFTER-GLOBAL-DATUM-003','status':'failed','timestamp_utc':datetime.now(timezone.utc).isoformat(),'errors':[],'artifact_paths':[]}
def put(name,data):
 p=ROOT/name;p.write_text(json.dumps(data,indent=2)+'\n');assert json.loads(p.read_text())==data
try:
 progress=json.loads((ROOT/'roof-progress.txt').read_text());backup=Path(progress.get('backup_directory','/proj/garage/backups/20260909T222413228616Z-global-datum'));R['backup_directory']=str(backup)
 assert (backup/'Existing-Garage.FCStd').is_file()
 original_hash=json.loads((backup/'sha256.json').read_text())
 assert hashlib.sha256((ROOT/'Existing-Garage.FCStd').read_bytes()).hexdigest()==original_hash['Existing-Garage.FCStd']
 v=json.loads((ROOT/'roof-validation.json').read_text());members=v['member_layout']
 G.showMainWindow();d=A.openDocument(str(ROOT/'Existing-Garage.FCStd'));A.setActiveDocument(d.Name)
 camera=G.activeDocument().activeView().getCamera()
 wallnames=json.loads((ROOT/'validation.json').read_text())['documents']['Existing-Garage.FCStd']['final_visible_objects']
 roofnames=[x['name'] for x in v['roof_objects']]
 fixednames=wallnames+['Soffit'+s for s in ['South','North','West','East']]+['Fascia'+s for s in ['South','North','West','East']]+['RidgeBoardOutput']
 fixed={n:global_shape(d.getObject(n)) for n in fixednames}
 axis_snapshot={m['name']:(list(d.getObject(m['name']+'Axis').Start),list(d.getObject(m['name']+'Axis').End),str(d.getObject(m['name']).Placement)) for m in members}
 previous_member_shapes={m['name']:global_shape(d.getObject(m['output'])) for m in members if m['kind']!='ridge'}
 replacements,hidden=apply_global_datum(A,d,members)
 roofnames=[replacements[n].Name if n in replacements else n for n in roofnames]
 def check_fixed():
  for n,old in fixed.items():
   now=global_shape(d.getObject(n))
   assert abs(now.Volume-old.Volume)<1e-3 and now.cut(old).Volume<1e-4 and old.cut(now).Volume<1e-4,n+' unexpectedly changed'
 def check():
  report=validate_tail_cuts(d,members);check_fixed()
  for n in roofnames+wallnames:
   o=d.getObject(n);assert o.ViewObject.Visibility and global_shape(o).isValid(),n
  assert len(replacements)==44
  for m in members:
   assert axis_snapshot[m['name']]==(list(d.getObject(m['name']+'Axis').Start),list(d.getObject(m['name']+'Axis').End),str(d.getObject(m['name']).Placement)),m['name']+' shifted'
   if m['kind']!='ridge':
    before=previous_member_shapes[m['name']];now=global_shape(d.getObject(m['output']))
    assert abs(now.BoundBox.ZMax-before.BoundBox.ZMax)<1e-6,m['name']+' upper envelope changed'
    assert now.cut(before).Volume<1e-4,m['name']+' added material'

  assert abs(max(global_shape(d.getObject(n)).BoundBox.ZMax for n in roofnames)-158.5*25.4)<1e-5
  return report
 report=check()
 sheet=d.getObject('RoofParameters');cell=sheet.getCellFromAlias('BoardThickness')
 before=global_shape(d.getObject(members[1]['output'])).Volume
 sheet.set(cell,'1.625 in');d.recompute()
 assert global_shape(d.getObject(members[1]['output'])).Volume>before
 edited=validate_tail_cuts(d,members)
 sheet.set(cell,'1.5 in');d.recompute();report=check()
 for o in hidden:o.ViewObject.Visibility=False
 G.activeDocument().activeView().setCamera(camera);d.recompute();d.save()
 A.closeDocument(d.Name);d=A.openDocument(str(ROOT/'Existing-Garage.FCStd'));A.setActiveDocument(d.Name);report=check()
 outputs=[d.getObject(n) for n in wallnames+roofnames]
 compound=Part.makeCompound([global_shape(o) for o in outputs]);compound.exportStep(str(ROOT/'Existing-Garage-roof.step'))
 mesh={'units':'mm','objects':[]}
 for o in outputs:
  verts,tris=global_shape(o).tessellate(.5)
  mesh['objects'].append({'name':o.Name,'label':o.Label,'color':list(o.ViewObject.ShapeColor),'vertices':[[a.x,a.y,a.z] for a in verts],'triangles':[list(t) for t in tris]})
 put('visible-mesh-roof.json',mesh)
 st=Part.Shape();st.read(str(ROOT/'Existing-Garage-roof.step'));assert st.isValid() and len(st.Solids)==61
 proposed_hash=hashlib.sha256((ROOT/'Proposed-Garage.FCStd').read_bytes()).hexdigest();assert proposed_hash==original_hash['Proposed-Garage.FCStd']
 assert len(mesh['objects'])==61
 newchecks=[]
 for n in roofnames:
  o=d.getObject(n);s=global_shape(o);newchecks.append({'name':n,'label':o.Label,'volume_mm3':s.Volume,'valid':s.isValid(),'solids':len(s.Solids),'visible':o.ViewObject.Visibility,'view_provider':o.ViewObject.TypeId})
 v.pop('generator_reproduction_check',None)
 v.update(member_axes_and_positions_unchanged=True,all_member_upper_envelopes_unchanged=True,request_id=R['request_id'],tail_clearance=report,roof_objects=newchecks,member_layout=members,tail_correction_backup_directory=str(backup),native_reopen_success=True,gui_visibility=True,soffit_fascia_ridge_unchanged=True,step_valid=True,step_solid_count=61,mesh_object_count=61,proposed_file_hash_unchanged=True)
 v['parameter_edit_checks']['global_datum_1_625_in_thickness_checked_and_restored']=True
 v['limitations']=[x.replace('Schematic vertical trims only; lateral joint intersections and bearing/notches unresolved.','Horizontal underside trims in eave zone and fascia inside-face trims applied. Other joint overlaps and bearing/notches remain schematic.') for x in v['limitations']]
 v['global_datum']=report
 put('roof-validation.json',v)
 params=json.loads((ROOT/'roof-parameters.json').read_text());params['request_id']=R['request_id'];params['tail_clearance']={'horizontal_underside_trim_z_inches':98.5,'zone':'entire member footprint, including over walls; no member shift','fascia_termination':'inside faces, preserving roof upper slope reference','changed_members':44,'hips':4,'jacks':40,'measured_maximum_soffit_intersection_mm3':report['maximum_soffit_intersection_mm3'],'measured_maximum_fascia_intersection_mm3':report['maximum_fascia_intersection_mm3'],'minimum_soffit_clearance_mm':report['minimum_soffit_clearance_mm']}
 params['notes'].append('Owner correction RAFTER-GLOBAL-DATUM-003 supersedes the eave-only underside limit: all jack/hip material below 98.5 inches is removed globally, including over walls. Member positions and upper roof slopes unchanged. Fascia inside-face termination retained.')
 params['bearing_notes']['exact_bearing_elevation']='Global horizontal underside datum at 98.5 inches across all jack/hip material including over walls, without shifting members. Fascia inside-face termination retained. Other joinery remains schematic.'
 params['global_underside_datum']={'height_inches':98.5,'height_mm':98.5*25.4,'all_jacks_and_hips':True,'member_shift_inches':0,'minimum_final_global_z_mm':report['minimum_global_z_mm'],'maximum_volume_below_datum_mm3':report['maximum_below_datum_volume_mm3']}
 put('roof-parameters.json',params)
 names=['Existing-Garage.FCStd','roof-generator.py','roof_tail_tools.py','correct-global-roof-datum.py','Existing-Garage-roof.step','visible-mesh-roof.json','roof-validation.json','roof-parameters.json','ROOF-README.md']
 for n in names:assert (ROOT/n).stat().st_size>0
 R.update(status='complete',summary='All 40 jacks and 4 hips globally clipped at 98.5 inches, including over-wall portions. No material below datum or soffit/fascia intersections. Member positions, upper envelopes, walls, soffit, fascia, ridge and Proposed preserved.',changed_member_count=44,measured_clearance={k:report[k] for k in ['maximum_soffit_intersection_mm3','maximum_fascia_intersection_mm3','minimum_soffit_clearance_mm','minimum_global_z_mm','maximum_below_datum_volume_mm3','global_datum_mm']},artifact_paths=[str(ROOT/n) for n in names],backup_directory=str(backup),native_reopen_success=True,parameter_edit_check_restored=True)
 A.closeDocument(d.Name)
except Exception:R['errors'].append(traceback.format_exc())
finally:
 put('roof-agent-result.json',R);put('roof-progress.txt',R);print(json.dumps(R,indent=2),flush=True);sys.stdout.flush();sys.stderr.flush();os._exit(0 if R['status']=='complete' else 1)
