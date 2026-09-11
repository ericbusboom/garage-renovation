#!/usr/bin/env python3
"""Native parametric existing roof prototype. Assumptions documented in roof README.
Run once with bundled FreeCAD Python. Refuses to add a second roof.
"""
import os,sys,json,math,hashlib,shutil,traceback
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parent
os.environ.setdefault('QT_QPA_PLATFORM','offscreen')
os.environ.setdefault('FONTCONFIG_FILE','/etc/fonts/fonts.conf')
sys.path.insert(0,'/opt/freecad-1.1.3/usr/lib')
import FreeCAD as A, FreeCADGui as G, Part
from roof_tail_tools import apply_tail_cuts, validate_tail_cuts
I=25.4
RESULT={'request_id':'EXISTING-ROOF-FRAMING-001','status':'failed','timestamp_utc':datetime.now(timezone.utc).isoformat(),'errors':[],'artifact_paths':[]}

def digest(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def near(a,b): return math.isclose(a,b,rel_tol=1e-8,abs_tol=1e-4)
def save_json(name,obj):
 p=ROOT/name; p.write_text(json.dumps(obj,indent=2)+'\n'); assert json.loads(p.read_text())==obj

def global_shape(o):
 s=o.Shape.copy(); s.Placement=o.getGlobalPlacement(); return s

def camera():
 rot=A.Rotation(0.4247082002778669,0.1759198966061612,0.3398511429799874,0.8204732385702833)
 center=A.Vector(249.5*I/2,249*I/2,158.5*I/2); pos=center+rot.multVec(A.Vector(0,0,18000)); axis=rot.Axis
 G.activeDocument().activeView().setCamera(f'#Inventor V2.1 ascii\nOrthographicCamera {{ position {pos.x} {pos.y} {pos.z} orientation {axis.x} {axis.y} {axis.z} {rot.Angle} nearDistance 100 farDistance 36000 focalDistance 18000 height 12500 }}')

try:
 original_hashes={n:digest(ROOT/n) for n in ['Existing-Garage.FCStd','Proposed-Garage.FCStd']}
 G.showMainWindow(); d=A.openDocument(str(ROOT/'Existing-Garage.FCStd')); A.setActiveDocument(d.Name)
 if d.getObject('RoofPrototype'): raise RuntimeError('Existing model already has RoofPrototype; refusing duplicate generation.')
 oldvalidation=json.loads((ROOT/'validation.json').read_text())
 wall_names=oldvalidation['documents']['Existing-Garage.FCStd']['final_visible_objects']
 wall_outputs=[d.getObject(n) for n in wall_names]
 wall_before={o.Name:global_shape(o) for o in wall_outputs}
 wallvol=sum(s.Volume for s in wall_before.values())
 backup=ROOT/'backups'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ'); backup.mkdir(parents=True,exist_ok=False)
 for n,h in original_hashes.items():
  shutil.copy2(ROOT/n,backup/n); assert digest(backup/n)==h
 save_json('roof-progress.txt',{'request_id':RESULT['request_id'],'status':'building','backup_directory':str(backup),'original_hashes':original_hashes})
 (backup/'sha256.json').write_text(json.dumps(original_hashes,indent=2)+'\n')
 params=json.loads((ROOT/'roof-parameters.json').read_text())
 params.update(status='prototype_assumptions_applied',board_thickness=1.5,board_orientation='on_edge',member_face_width_assignment='5.5 inches throughout; 5 inch stock locations unknown',hip_and_ridge_section_confirmation='same 1.5 x 5.5 inch placeholder section',soffit_thickness=.75,eave_projection_reference_face='outer stucco face',ridge_peak_upper_envelope=158.5,soffit_bottom=97.75,fascia_top=101.25,fascia_bottom=97.75,eave_framing_upper_envelope=101.25,fascia_outer_offset_from_core=4.75,cover_reference_offset_from_core=5.75)
 params['tail_clearance']={'underside_trim':'horizontal at wall/soffit top across every entire jack/hip member, including over walls','fascia_trim':'inside faces','request_id':'RAFTER-GLOBAL-DATUM-003'}
 params['notes']=['All jack/hip undersides are globally clipped at soffit top, including over walls; no member shifts, and tails terminate at fascia inside faces; no soffit/fascia penetration.','Owner confirmed framing thickness 1.5 inches ON EDGE. Uniform 5.5 inch depth and 0.75 inch soffit remain assumptions.','All stock is flat rectangular 1.5 x 5.5 inch ON EDGE, including ridge and hips; depth assignment assumed; no invented T&G or alternating stock.','Upper top-center edges define the roof envelope: fascia top at eaves, wall top +60 inches at ridge.','Member end trims are schematic vertical planes. Hip/jack lateral intersections may overlap; no exact joinery or bearing/notch fit is claimed.','Roof faces have differing slopes because the centered north-south ridge is 18 inches long.','No roof cladding is modeled. Hidden planar cover perimeter is a footprint reference only.','Soffit top at wall top, 0.75 inch thickness placeholder; fascia starts at soffit underside.','Soffit projects 3.5 inches from stucco outer face; fascia is 0.75 inch farther out; cover reference another 1 inch out.','Station offsets remain measured along core wall edges, even though framing extends to fascia outside edges.']
 root=d.addObject('App::DocumentObjectGroup','RoofPrototype'); root.Label='Existing roof — assumed sections, schematic joints'
 root.addProperty('App::PropertyString','PrototypeNotes'); root.PrototypeNotes='1.5 x 5.5 in ON EDGE assumed. Bearings/notches and exact joints unresolved. No cladding.'
 sheet=d.addObject('Spreadsheet::Sheet','RoofParameters'); sheet.Label='Roof dimensions — ASSUMPTIONS'; d.getObject('Dimensions').addObject(sheet)
 sheet.set('A1','Roof dimension');sheet.set('B1','Inches');sheet.set('C1','Basis / assumption');sheet.setStyle('A1:C1','bold','add')
 sheet.setColumnWidth('A',250);sheet.setColumnWidth('B',160);sheet.setColumnWidth('C',600)
 row=2;cells={}
 def cell(alias,label,value,note=''):
  global row
  c=f'B{row}';sheet.set(f'A{row}',label);sheet.set(c,f'{value} in' if isinstance(value,(float,int)) else '='+value);sheet.setAlias(c,alias);sheet.set(f'C{row}',note);cells[alias]=c;row+=1
 for alias,label,val,note in [
 ('CoreWidth','Core width','Parameters.Width','Linked to wall dimensions'),('CoreLength','Core length','Parameters.Length','Linked to wall dimensions'),('WallTop','Wall top','Parameters.Height','Linked to wall dimensions'),('Stucco','Stucco thickness','Parameters.Stucco','Linked to wall dimensions'),
 ('Rise','Approximate ridge rise',60,'Upper envelope above wall top'),('RidgeLength','North-south ridge length',18,'Owner restored short ridge'),('BoardThickness','Board thickness',1.5,'OWNER CONFIRMED on edge'),('BoardDepth','On-edge face depth',5.5,'ASSUMED throughout; 5-inch locations unknown'),('SoffitProjection','Soffit outboard projection',3.5,'From outer stucco face'),('SoffitThickness','Soffit thickness',.75,'PLACEHOLDER'),('FasciaHeight','Fascia height',3.5,'Extends upward from soffit underside'),('FasciaThickness','Fascia thickness',.75,''),('CoverOverhang','Cover reference beyond fascia',1,'Hidden footprint line only'),('First','First rafter from wall corner',16,'Symmetric fixed-count layout'),('Spacing','Rafter spacing',24,'Symmetric from both ends')]: cell(alias,label,val,note)
 for alias,label,expr,note in [
 ('SoffitOffset','Soffit edge from core','Stucco + SoffitProjection',''),('EaveOffset','Fascia outer edge from core','SoffitOffset + FasciaThickness','Framing top-edge datum'),('CoverOffset','Cover footprint from core','EaveOffset + CoverOverhang',''),('FasciaBottom','Fascia / soffit underside','WallTop - SoffitThickness',''),('EaveZ','Framing eave upper envelope','FasciaBottom + FasciaHeight',''),('PeakZ','Ridge upper envelope','WallTop + Rise',''),('RidgeSouthY','South ridge end','(CoreLength - RidgeLength)/2',''),('RidgeNorthY','North ridge end','(CoreLength + RidgeLength)/2',''),('SouthRun','South/north horizontal run','RidgeSouthY + EaveOffset',''),('SideRun','East/west horizontal run','CoreWidth/2 + EaveOffset',''),('RoofDelta','Roof upper-envelope rise','PeakZ - EaveZ',''),('CentralBayX','North/south residual central bay','CoreWidth - 2*(First + 4*Spacing)','5 stations from each corner'),('CentralBayY','East/west residual central bay','CoreLength - 2*(First + 4*Spacing)','5 stations from each corner')]: cell(alias,label,expr,note)
 def q(s):
  import re
  return re.sub(r'\b('+ '|'.join(sorted(cells,key=len,reverse=True))+r')\b',lambda m:'RoofParameters.'+m[0],s)
 groups={}
 for name,label in [('Soffit','Soffit — 0.75 in placeholder'),('Fascia','Fascia'),('HipRafters','Hip rafters'),('Ridge','Ridge'),('CommonJackRafters','Common and jack rafters'),('CoverReference','Cover edge — hidden reference only')]:
  g=d.addObject('App::DocumentObjectGroup',name);g.Label=label;root.addObject(g);groups[name]=g
 roof_outputs=[];hidden=[];member_info=[];assemblies=[]
 def box(name,group,size,pos,label,color):
  o=d.addObject('Part::Box',name);group.addObject(o);o.Label=label
  for prop,value in zip(['Length','Width','Height','Placement.Base.x','Placement.Base.y','Placement.Base.z'],size+pos): o.setExpression(prop,q(value))
  o.ViewObject.ShapeColor=color;roof_outputs.append(o);return o
 for side,size,pos in [
 ('South',['CoreWidth+2*SoffitOffset','SoffitProjection','SoffitThickness'],['-SoffitOffset','-SoffitOffset','FasciaBottom']),('North',['CoreWidth+2*SoffitOffset','SoffitProjection','SoffitThickness'],['-SoffitOffset','CoreLength+Stucco','FasciaBottom']),('West',['SoffitProjection','CoreLength+2*Stucco','SoffitThickness'],['-SoffitOffset','-Stucco','FasciaBottom']),('East',['SoffitProjection','CoreLength+2*Stucco','SoffitThickness'],['CoreWidth+Stucco','-Stucco','FasciaBottom'])]: box('Soffit'+side,groups['Soffit'],size,pos,side+' soffit — thickness placeholder',(.75,.69,.55))
 for side,size,pos in [
 ('South',['CoreWidth+2*EaveOffset','FasciaThickness','FasciaHeight'],['-EaveOffset','-EaveOffset','FasciaBottom']),('North',['CoreWidth+2*EaveOffset','FasciaThickness','FasciaHeight'],['-EaveOffset','CoreLength+SoffitOffset','FasciaBottom']),('West',['FasciaThickness','CoreLength+2*SoffitOffset','FasciaHeight'],['-EaveOffset','-SoffitOffset','FasciaBottom']),('East',['FasciaThickness','CoreLength+2*SoffitOffset','FasciaHeight'],['CoreWidth+SoffitOffset','-SoffitOffset','FasciaBottom'])]: box('Fascia'+side,groups['Fascia'],size,pos,side+' fascia',(.63,.48,.32))
 def member(name,label,group,start,end,kind,station=None):
  a=d.addObject('App::Part',name);a.Label=label+' — editable axis';group.addObject(a);assemblies.append(a)
  axis=d.addObject('App::DocumentObject',name+'Axis'); axis.Label=label+' axis dimensions'; d.getObject('Dimensions').addObject(axis)
  for prop in ['Start','End']: axis.addProperty('App::PropertyVector',prop,'Layout')
  for prop in ['Run','Rise']: axis.addProperty('App::PropertyLength',prop,'Layout')
  for prop in ['Pitch','Yaw']: axis.addProperty('App::PropertyAngle',prop,'Layout')
  a.addProperty('App::PropertyString','JointCaveat','Layout');a.JointCaveat='Schematic vertical end trims only. Joint overlap and bearing/notches unresolved.'
  for k in range(3):
   axis.setExpression('Start.'+'xyz'[k],q(start[k]));axis.setExpression('End.'+'xyz'[k],q(end[k]));a.setExpression('Placement.Base.'+'xyz'[k],name+'Axis.Start.'+'xyz'[k])
  axis.setExpression('Run','sqrt((End.x-Start.x)^2+(End.y-Start.y)^2)');axis.setExpression('Rise','End.z-Start.z')
  axis.setExpression('Pitch','atan2(Rise; Run)');axis.setExpression('Yaw','atan2(End.y-Start.y; End.x-Start.x)')
  a.Placement.Rotation=A.Rotation(A.Vector(0,0,1),0);a.setExpression('Placement.Rotation.Angle',name+'Axis.Yaw')
  raw=d.addObject('Part::Box',name+'Stock');a.addObject(raw);raw.Label='Rectangular stock — hidden source'
  raw.setExpression('Length',f'sqrt({name}Axis.Run^2+{name}Axis.Rise^2)+2*RoofParameters.BoardDepth')
  raw.setExpression('Width','RoofParameters.BoardThickness');raw.setExpression('Height','RoofParameters.BoardDepth')
  raw.Placement.Rotation=A.Rotation(A.Vector(0,1,0),0);raw.setExpression('Placement.Rotation.Angle',f'-{name}Axis.Pitch')
  raw.setExpression('Placement.Base.x',f'(sin({name}Axis.Pitch)-cos({name}Axis.Pitch))*RoofParameters.BoardDepth')
  raw.setExpression('Placement.Base.y','-RoofParameters.BoardThickness/2')
  raw.setExpression('Placement.Base.z',f'-(cos({name}Axis.Pitch)+sin({name}Axis.Pitch))*RoofParameters.BoardDepth')
  trim=d.addObject('Part::Box',name+'Trim');a.addObject(trim);trim.Label='Schematic vertical trim — hidden'
  trim.setExpression('Length',f'{name}Axis.Run');trim.setExpression('Width','RoofParameters.BoardThickness+2 mm');trim.setExpression('Height',f'{name}Axis.Rise+2*RoofParameters.BoardDepth+2 mm')
  trim.setExpression('Placement.Base.y','-(RoofParameters.BoardThickness+2 mm)/2');trim.setExpression('Placement.Base.z','-RoofParameters.BoardDepth-1 mm')
  out=d.addObject('Part::Common',name+'Output');a.addObject(out);out.Base=raw;out.Tool=trim;out.Refine=True;out.Label=label+' — schematic end trims'
  out.ViewObject.ShapeColor=(.58,.36,.18) if kind=='hip' else (.72,.49,.27) if kind=='ridge' else (.82,.62,.38)
  roof_outputs.append(out);hidden.extend([raw,trim]);member_info.append({'name':name,'kind':kind,'station_inches':station,'output':out.Name})
 member('RidgeBoard','18-inch N–S ridge',groups['Ridge'],['CoreWidth/2','RidgeSouthY','PeakZ'],['CoreWidth/2','RidgeNorthY','PeakZ'],'ridge')
 for suffix,x,y,ry in [('SW','-EaveOffset','-EaveOffset','RidgeSouthY'),('SE','CoreWidth+EaveOffset','-EaveOffset','RidgeSouthY'),('NW','-EaveOffset','CoreLength+EaveOffset','RidgeNorthY'),('NE','CoreWidth+EaveOffset','CoreLength+EaveOffset','RidgeNorthY')]:
  member('Hip'+suffix,'Hip '+suffix,groups['HipRafters'],[x,y,'EaveZ'],['CoreWidth/2',ry,'PeakZ'],'hip')
 # Fixed topology: five stations from each wall end; explicit central residual.
 for side in ['South','North','West','East']:
  for opposite in [False,True]:
   for k in range(5):
    span='CoreWidth' if side in ['South','North'] else 'CoreLength'; station=f'(First+{k}*Spacing)';s=f'({span}-{station})' if opposite else station
    sv=(249.5 if span=='CoreWidth' else 249)-(16+k*24) if opposite else 16+k*24
    if side in ['South','North']:
     frac=f'({station}+EaveOffset)/SideRun'; yy=f'(-EaveOffset+SouthRun*({frac}))' if side=='South' else f'(CoreLength+EaveOffset-SouthRun*({frac}))'
     start=[s,'-EaveOffset' if side=='South' else 'CoreLength+EaveOffset','EaveZ'];end=[s,yy,f'EaveZ+RoofDelta*({frac})'];kind='jack'
    else:
     frac=f'({station}+EaveOffset)/SouthRun'
     xx=f'(-EaveOffset+SideRun*({frac}))' if side=='West' else f'(CoreWidth+EaveOffset-SideRun*({frac}))'
     start=['-EaveOffset' if side=='West' else 'CoreWidth+EaveOffset',s,'EaveZ'];end=[xx,s,f'EaveZ+RoofDelta*({frac})'];kind='jack'
    member(side+('Far' if opposite else 'Near')+str(k+1),f'{side} jack at {sv:g} in',groups['CommonJackRafters'],start,end,kind,sv)
 d.recompute()
 # Native line features are deliberately hidden; no covering sheet or support infill.
 off=float(sheet.get('B'+str(int(cells['CoverOffset'][1:]))).split()[0]) if False else 5.75*I
 ref=d.addObject('Part::Feature','CoverFootprint');groups['CoverReference'].addObject(ref);ref.Label='Cover edge 1 inch beyond fascia — plan reference only'
 pts=[A.Vector(-off,-off,101.25*I),A.Vector(249.5*I+off,-off,101.25*I),A.Vector(249.5*I+off,249*I+off,101.25*I),A.Vector(-off,249*I+off,101.25*I)]
 ref.Shape=Part.makePolygon(pts+[pts[0]]);ref.addProperty('App::PropertyString','ReferenceOnly');ref.ReferenceOnly='Hidden plan perimeter. Not a roof surface; regenerate reference if global footprint changes.';hidden.append(ref)
 for o in roof_outputs: o.ViewObject.Visibility=True
 for o in hidden: o.ViewObject.Visibility=False
 groups['CoverReference'].ViewObject.Visibility=False;sheet.ViewObject.Visibility=False
 d.recompute()
 tail_replacements,tail_hidden=apply_tail_cuts(A,d,member_info)
 roof_outputs=[tail_replacements.get(o.Name,o) for o in roof_outputs]
 hidden.extend(tail_hidden)
 def validate():
  checks=[]
  for o in roof_outputs:
   s=global_shape(o);assert s.isValid() and len(s.Solids)==1,(o.Name,'invalid')
   assert o.ViewObject.Visibility,(o.Name,'invisible')
   checks.append({'name':o.Name,'label':o.Label,'volume_mm3':s.Volume,'valid':True,'solids':1,'visible':True,'view_provider':o.ViewObject.TypeId})
  for name,old in wall_before.items():
   now=global_shape(d.getObject(name));assert near(now.Volume,old.Volume)
   assert now.cut(old).Volume<1e-3 and old.cut(now).Volume<1e-3,name+' wall changed'
  assert all(not o.ViewObject.Visibility for o in hidden)
  assert near(max(global_shape(o).BoundBox.ZMax for o in roof_outputs),158.5*I)
  assert near(global_shape(d.getObject('FasciaSouth')).BoundBox.ZMax,101.25*I)
  assert near(global_shape(d.getObject('SoffitSouth')).BoundBox.ZMax,98.5*I)
  for info in member_info:
   a=d.getObject(info['name']+'Axis');info.update(start_mm=list(a.Start),end_mm=list(a.End),pitch_degrees=a.Pitch.Value,run_mm=a.Run.Value)
  validate_tail_cuts(d,member_info)
  return checks
 checks=validate()
 # Exercise cross-section and roof-rise expressions, then restore before saving.
 oldvol=global_shape(d.getObject('HipSWOutput')).Volume
 sheet.set(cells['BoardThickness'],'1.625 in');d.recompute()
 assert global_shape(d.getObject('HipSWOutput')).Volume>oldvol
 sheet.set(cells['BoardThickness'],'1.5 in');d.recompute()
 oldpitch=d.getObject('HipSWAxis').Pitch.Value
 sheet.set(cells['Rise'],'61 in');d.recompute()
 assert d.getObject('HipSWAxis').Pitch.Value>oldpitch
 assert near(global_shape(d.getObject('RidgeBoardOutput')).BoundBox.ZMax,159.5*I)
 sheet.set(cells['Rise'],'60 in');d.recompute();checks=validate()
 for o in wall_outputs: o.ViewObject.Visibility=True
 camera();d.recompute();d.save()
 all_outputs=wall_outputs+roof_outputs
 compound=Part.makeCompound([global_shape(o) for o in all_outputs]);compound.exportStep(str(ROOT/'Existing-Garage-roof.step'))
 mesh={'units':'mm','objects':[]}
 for o in all_outputs:
  vs,ts=global_shape(o).tessellate(.5)
  mesh['objects'].append({'name':o.Name,'label':o.Label,'color':list(o.ViewObject.ShapeColor),'vertices':[[v.x,v.y,v.z] for v in vs],'triangles':[list(t) for t in ts]})
 save_json('visible-mesh-roof.json',mesh)
 output_names=[o.Name for o in roof_outputs];hidden_names=[o.Name for o in hidden]
 A.closeDocument(d.Name);d=A.openDocument(str(ROOT/'Existing-Garage.FCStd'));A.setActiveDocument(d.Name)
 roof_outputs=[d.getObject(n) for n in output_names];hidden=[d.getObject(n) for n in hidden_names];checks=validate()
 tail_report=validate_tail_cuts(d,member_info)
 cam=G.activeDocument().activeView().getCamera();assert 'height 12500' in cam
 assert digest(ROOT/'Proposed-Garage.FCStd')==original_hashes['Proposed-Garage.FCStd']
 step=Part.Shape();step.read(str(ROOT/'Existing-Garage-roof.step'));assert step.isValid() and len(step.Solids)==61
 slopes={'south_north_degrees':math.degrees(math.atan2(57.25,120.25)),'east_west_degrees':math.degrees(math.atan2(57.25,129.5))}
 params.update(roof_pitch=slopes,central_residual_bays_inches={'south_north':25.5,'east_west':25},member_counts={'ridge':1,'hips':4,'jacks':40,'commons':0},bearing_notes={'wall_top_inches':98.5,'eave_upper_inches':101.25,'peak_upper_inches':158.5,'exact_bearing_elevation':'Unresolved: no birdsmouth/notch. All jack/hip undersides globally cut at soffit top, including over walls; fascia inside-face trims applied. Wall bearing/notches remain schematic.'})
 save_json('roof-parameters.json',params)
 validation={'request_id':RESULT['request_id'],'freecad_version':A.Version(),'native_reopen_success':True,'gui_visibility':True,'camera':cam,'walls_unchanged_geometrically':True,'proposed_file_hash_unchanged':True,'original_sha256':original_hashes,'backup_directory':str(backup),'tail_clearance':tail_report,'roof_objects':checks,'member_layout':member_info,'parameter_edit_checks':{'board_thickness_1_625_in_changed_volume':True,'rise_61_in_updated_pitch_and_peak':True,'restored_before_save':True},'step_valid':True,'step_solid_count':len(step.Solids),'mesh_object_count':len(mesh['objects']),'pitch':slopes,'limitations':['Offscreen OpenGL cannot render a verified screenshot; visible mesh exported.','Global horizontal wall-top underside datum and fascia inside-face tail trims applied; other lateral joints and bearing/notches unresolved.','Framing thickness 1.5 inches and on-edge orientation confirmed; 5.5 inch depth assignment and soffit thickness remain assumptions.','Rafter station count is fixed at five from each end; major spacing/footprint changes need regeneration.','Cover footprint is static native wire, hidden; regenerate if footprint changes.']}
 save_json('roof-validation.json',validation)
 artifact_names=['Existing-Garage.FCStd','Proposed-Garage.FCStd','roof-generator.py','roof_tail_tools.py','roof-parameters.json','roof-validation.json','Existing-Garage-roof.step','visible-mesh-roof.json','ROOF-README.md']
 for n in artifact_names:assert (ROOT/n).stat().st_size>0,n
 RESULT.update(status='complete',summary='Existing garage now includes assumed on-edge rectangular roof framing, soffit and fascia. Walls preserved; Proposed unchanged. Native reopen, visibility, shape and restored expression checks passed.',artifact_paths=[str(ROOT/n) for n in artifact_names]+[str(backup)],confirmed=['1.5 inch framing thickness, ON EDGE'],assumptions=['5.5 inch depth throughout','0.75 inch soffit thickness'],counts={'roof_solids':53,'wall_and_stucco_solids':8,'total':61},limitations=validation['limitations'])
 A.closeDocument(d.Name)
except Exception:
 RESULT['errors'].append(traceback.format_exc())
finally:
 save_json('roof-agent-result.json',RESULT)
 save_json('roof-progress.txt',RESULT)
 print(json.dumps(RESULT,indent=2),flush=True);sys.stdout.flush();sys.stderr.flush();os._exit(0 if RESULT['status']=='complete' else 1)
