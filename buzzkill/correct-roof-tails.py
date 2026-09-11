#!/usr/bin/env python3
"""Apply the owner-requested tail correction once to the existing roof model."""
import os,sys,json,hashlib,traceback
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parent
os.environ.setdefault('QT_QPA_PLATFORM','offscreen');os.environ.setdefault('FONTCONFIG_FILE','/etc/fonts/fonts.conf')
sys.path.insert(0,'/opt/freecad-1.1.3/usr/lib')
import FreeCAD as A, FreeCADGui as G, Part
from roof_tail_tools import apply_tail_cuts,validate_tail_cuts,global_shape
R={'request_id':'RAFTER-SOFFIT-CLEARANCE-002','status':'failed','timestamp_utc':datetime.now(timezone.utc).isoformat(),'errors':[],'artifact_paths':[]}
def put(name,data):
 p=ROOT/name;p.write_text(json.dumps(data,indent=2)+'\n');assert json.loads(p.read_text())==data
try:
 progress=json.loads((ROOT/'roof-progress.txt').read_text());backup=Path(progress.get('backup_directory','/proj/garage/backups/20260909T215621559492Z-tail-clearance'));R['backup_directory']=str(backup)
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
 replacements,hidden=apply_tail_cuts(A,d,members)
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
 v.update(request_id=R['request_id'],tail_clearance=report,roof_objects=newchecks,member_layout=members,tail_correction_backup_directory=str(backup),native_reopen_success=True,gui_visibility=True,soffit_fascia_ridge_unchanged=True,step_valid=True,step_solid_count=61,mesh_object_count=61,proposed_file_hash_unchanged=True)
 v['parameter_edit_checks']['tail_cut_1_625_in_thickness_clearance_checked_and_restored']=True
 v['limitations']=[x.replace('Schematic vertical trims only; lateral joint intersections and bearing/notches unresolved.','Horizontal underside trims in eave zone and fascia inside-face trims applied. Other joint overlaps and bearing/notches remain schematic.') for x in v['limitations']]
 put('roof-validation.json',v)
 params=json.loads((ROOT/'roof-parameters.json').read_text());params['request_id']=R['request_id'];params['tail_clearance']={'horizontal_underside_trim_z_inches':98.5,'zone':'eave only, through core outside-face planes; hip corner union included','fascia_termination':'inside faces, preserving roof upper slope reference','changed_members':44,'hips':4,'jacks':40,'measured_maximum_soffit_intersection_mm3':report['maximum_soffit_intersection_mm3'],'measured_maximum_fascia_intersection_mm3':report['maximum_fascia_intersection_mm3'],'minimum_soffit_clearance_mm':report['minimum_soffit_clearance_mm']}
 params['notes'].append('Owner correction: every perimeter hip/jack tail underside cut horizontally at soffit top in the eave zone; tail ends clipped to fascia inside faces. Zero measured material intersection with soffit/fascia.')
 params['bearing_notes']['exact_bearing_elevation']='Soffit-top underside cut at 98.5 inches through eave only. Fascia inside-face termination. Remaining wall seat/notches and joints schematic.'
 put('roof-parameters.json',params)
 names=['Existing-Garage.FCStd','roof-generator.py','roof_tail_tools.py','correct-roof-tails.py','Existing-Garage-roof.step','visible-mesh-roof.json','roof-validation.json','roof-parameters.json','ROOF-README.md']
 for n in names:assert (ROOT/n).stat().st_size>0
 R.update(status='complete',summary='44 tails corrected: 40 jacks and 4 hips. Native horizontal soffit-top underside cuts and fascia inside-face terminations; no measured soffit/fascia volume penetration. Walls, soffit, fascia, ridge and Proposed preserved.',changed_member_count=44,measured_clearance={k:report[k] for k in ['maximum_soffit_intersection_mm3','maximum_fascia_intersection_mm3','minimum_soffit_clearance_mm']},artifact_paths=[str(ROOT/n) for n in names],backup_directory=str(backup),native_reopen_success=True,parameter_edit_check_restored=True)
 A.closeDocument(d.Name)
except Exception:R['errors'].append(traceback.format_exc())
finally:
 put('roof-agent-result.json',R);put('roof-progress.txt',R);print(json.dumps(R,indent=2),flush=True);sys.stdout.flush();sys.stderr.flush();os._exit(0 if R['status']=='complete' else 1)
