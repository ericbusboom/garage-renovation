#!/usr/bin/env python3
"""Native renovated loft and analysis-geometry export, from current full-frame snapshot."""
import os,sys,json,math,hashlib,traceback,importlib.util
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parent
os.environ.setdefault('QT_QPA_PLATFORM','offscreen');os.environ.setdefault('FONTCONFIG_FILE','/etc/fonts/fonts.conf')
sys.path.insert(0,'/opt/freecad-1.1.3/usr/lib')
import FreeCAD as A,FreeCADGui as G,Part
I=25.4;RID='RENOVATED-LOFT-001';R={'request_id':RID,'status':'running','started_utc':datetime.now(timezone.utc).isoformat()}
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(n,j):(ROOT/n).write_text(json.dumps(j,indent=2)+'\n')
def progress(t):(ROOT/'loft-progress.txt').write_text(datetime.now(timezone.utc).isoformat()+' '+RID+' '+t+'\n')
def shape(o):
 s=o.Shape.copy();s.Placement=o.getGlobalPlacement();return s

def bounds(s):
 b=s.BoundBox;return [b.XMin,b.YMin,b.ZMin,b.XMax,b.YMax,b.ZMax]
try:
 put('loft-result.json',R);inp=json.loads((ROOT/'renovated-loft-input.json').read_text());backup=ROOT/inp['base_directory'];R['backup_directory']=str(backup)
 assert sha(backup/'Proposed-Garage.FCStd')==inp['base_model_sha256'],'Immutable full-frame base changed'
 oldhash=sha(ROOT/'Existing-Garage.FCStd');reg=json.loads((backup/'proposed-overlay-member-register.json').read_text());steel_names=[r['object'] for r in reg['members']]
 fullmesh=json.loads((backup/'proposed-overlay-full.json').read_text());oldnames=[o['name'] for o in fullmesh['objects'] if o.get('triangles') and o['name'] not in steel_names];assert len(oldnames)==107
 wire_names=[o['name'] for o in fullmesh['objects'] if o.get('lines')]
 progress('Opening full-frame snapshot; preserving all steel and native existing geometry.')
 G.showMainWindow();d=A.openDocument(str(backup/'Proposed-Garage.FCStd'));A.setActiveDocument(d.Name)
 preserved={n:shape(d.getObject(n)) for n in steel_names+oldnames};types={n:d.getObject(n).TypeId for n in preserved}
 d.getObject('ExistingGarage').ViewObject.Visibility=False
 loft=d.addObject('App::DocumentObjectGroup','RenovatedLoft');loft.Label='Renovated loft — deck and wood joists; connections unresolved';d.getObject('ProposedStructure').addObject(loft)
 def group(n,label,parent):
  g=d.addObject('App::DocumentObjectGroup',n);g.Label=label;parent.addObject(g);return g
 deckgroup=group('RenovatedMainDeck','Main deck — separately toggleable,60% transparent',loft)
 joistgroup=group('RenovatedWoodJoists','Nominal2x8 joists — actual1.5x7.25,16in centers',loft)
 ledgegroup=group('OptionalNorthLoadingLedge','OPTIONAL north loading ledge — hidden, support unresolved',loft)
 notesgroup=group('RenovatedLoftNotes','Dimensions and unresolved details',loft)
 s=d.addObject('Spreadsheet::Sheet','RenovatedLoftParameters');notesgroup.addObject(s);s.set('A1','Renovated loft — geometry only');s.setColumnWidth('A',320);s.setColumnWidth('B',160)
 params={'DeckWest':0,'DeckEast':224.25,'DeckSouth':72,'DeckNorth':249,'DeckBottom':120,'DeckThickness':.75,'JoistWidth':1.5,'JoistDepth':7.25,'JoistTop':120,'JoistSpacing':16,'Bay1Start':72.75,'Bay1End':182,'Bay2Start':188,'Bay2End':246,'LedgeWest':56.25,'LedgeEast':152.25,'LedgeNorth':271}
 for i,(key,value) in enumerate(params.items(),2):s.set('A'+str(i),key);s.set('B'+str(i),'='+str(value)+' in');s.setAlias('B'+str(i),key)
 def box(name,label,parent,expressions,color,transparency=0):
  o=d.addObject('Part::Box',name);parent.addObject(o);o.Label=label
  for prop,exp in zip(['Length','Width','Height','Placement.Base.x','Placement.Base.y','Placement.Base.z'],expressions):o.setExpression(prop,exp)
  o.ViewObject.ShapeColor=color;o.ViewObject.Transparency=transparency;o.ViewObject.Visibility=True;return o
 def p(k):return 'RenovatedLoftParameters.'+k
 deck=box('RenovatedDeck','Main loft deck — finished top120.75in',deckgroup,[p('DeckEast')+'-'+p('DeckWest'),p('DeckNorth')+'-'+p('DeckSouth'),p('DeckThickness'),p('DeckWest'),p('DeckSouth'),p('DeckBottom')],(.82,.72,.52),60)
 deck.addProperty('App::PropertyString','Stage');deck.Stage='future_after_existing_roof_removal'
 centers=[];x=inp['joists']['first_center_x']
 while x<=inp['joists']['last_edge_center_x']+1e-9:centers.append(x);x+=16
 if abs(centers[-1]-inp['joists']['last_edge_center_x'])>1e-9:centers.append(inp['joists']['last_edge_center_x'])
 joists=[];wood_records=[]
 for bay,(start,end) in enumerate(inp['joists']['bays_y'],1):
  for i,x in enumerate(centers,1):
   name=f'RenovatedJoistB{bay}J{i:02d}'
   o=box(name,f'Loft joist bay{bay} #{i} — 2x8 nominal,16in centers',joistgroup,[p('JoistWidth'),p(f'Bay{bay}End')+'-'+p(f'Bay{bay}Start'),p('JoistDepth'),str(x)+' in-'+p('JoistWidth')+'/2',p(f'Bay{bay}Start'),p('JoistTop')+'-'+p('JoistDepth')],(.67,.45,.24))
   o.addProperty('App::PropertyString','Stage');o.Stage='future_after_existing_roof_removal';joists.append(o)
   wood_records.append({'id':name,'object':name,'bay':bay,'a':[x,start,116.375],'b':[x,end,116.375],'section_family':'wood_joist','actual_section_inches':[1.5,7.25],'nominal_section':'2x8','top_z_inches':120,'stage':'future_after_existing_roof_removal','end_connection':'Ends flush to steel beam faces; hanger/bearing detail unresolved; no invented bearing.','support_objects':['ProposedT1Future','ProposedB2Future'] if bay==1 else ['ProposedB2Future','ProposedTN']})
 ledge=box('OptionalNorthLedgeDeck','Optional north loading ledge deck — support NOT resolved',ledgegroup,[p('LedgeEast')+'-'+p('LedgeWest'),p('LedgeNorth')+'-'+p('DeckNorth'),p('DeckThickness'),p('LedgeWest'),p('DeckNorth'),p('DeckBottom')],(.82,.72,.52),60)
 ledgegroup.ViewObject.Visibility=False;ledge.ViewObject.Visibility=False
 notes=[
 ('FinishedFloor','Deck bottom120, thickness0.75, finished floor120.75. This is0.75 above previous120 reference; unchanged loading header bottom204 gives83.25in finished clear height.'),
 ('FrontEdge','Specified deck south edge y72 is2.25in north of T1 center y69.75, and0.75in south of joist ends/steel north face y72.75. These exact coordinates are retained; a2.25in free cantilever is not asserted.'),
 ('JoistConnections','Joist top120, bottom112.75. Bay ends72.75..182 and188..246 meet steel beam faces. Hangers, bearing, notches and fasteners unresolved; none invented.'),
 ('JoistSpacing','Centers begin x0.75 at16in increments; a last closure joist at220.5 ends flush against T-E west face221.25, with11.75in last spacing. Joists run north-south.'),
 ('OpenSouth','Main deck covers x0..224.25, y72..249. First72in of existing garage remain open. West walkway region x-32..0 remains distinct and is not decked.'),
 ('DeckNotches','Deck is the requested rectangular0.75in placeholder. Exact intersections with steel webs/jambs are listed as required deck notches in renovated-loft-parameters.json; notches/edge blocking are not detailed. East closure joist ends atx221.25,3in inside deck edge224.25.'),
 ('LoadingLedge','Optional deck x56.25..152.25, y249..271 is hidden. No support members or new columns added.'),
 ('AnalysisScope','Only intended member axes and explicit connection offsets exported. No capacity, joist design, material strength, loads, solver or cost optimization run.')]
 for name,value in notes:
  o=d.addObject('App::DocumentObject','LoftNote'+name);notesgroup.addObject(o);o.Label=name;o.addProperty('App::PropertyString','Explanation');o.Explanation=value
 newnames=[deck.Name]+[o.Name for o in joists]+[ledge.Name];visible_new=[deck.Name]+[o.Name for o in joists]
 d.recompute()
 def validate():
  global deck_required_notches
  deck_required_notches=[]
  for n,old in preserved.items():
   o=d.getObject(n);ss=shape(o);assert o.TypeId==types[n] and abs(ss.Volume-old.Volume)<1e-5,(n,'changed')
   assert ss.cut(old).Volume<1e-4 and old.cut(ss).Volume<1e-4,(n,'geometry changed')
  checks=[]
  for n in newnames:
   o=d.getObject(n);ss=shape(o);assert ss.isValid() and len(ss.Solids)==1 and ss.Volume>1e-4,n
   checks.append({'object':n,'native_type':o.TypeId,'valid':True,'volume_mm3':ss.Volume,'bounds_inches':[v/I for v in bounds(ss)],'visible':bool(o.ViewObject.Visibility)})
  assert not d.getObject('ExistingGarage').ViewObject.Visibility
  assert not d.getObject('OptionalNorthLoadingLedge').ViewObject.Visibility
  assert d.getObject('RenovatedDeck').ViewObject.Transparency==60
  for r in wood_records:
   b=bounds(shape(d.getObject(r['object'])));assert abs(b[5]/I-120)<1e-7 and abs(b[2]/I-112.75)<1e-7
   for target in r['support_objects']:assert shape(d.getObject(r['object'])).common(shape(d.getObject(target))).Volume<1e-4,(r['object'],target,'overlap')
  def overlaps(a,b):return all(min(a[i+3],b[i+3])-max(a[i],b[i])>1e-7 for i in range(3))
  steelshapes={n:shape(d.getObject(n)) for n in steel_names}
  for record in wood_records:
   joist=shape(d.getObject(record['object']));jb=bounds(joist)
   for n,steel in steelshapes.items():
    if overlaps(jb,bounds(steel)):
     assert joist.common(steel).Volume<1e-4,(record['object'],n,'wood overlaps steel')
  deckshape=shape(d.getObject('RenovatedDeck'));db=bounds(deckshape)
  for n,steel in steelshapes.items():
   if overlaps(db,bounds(steel)):
    volume=deckshape.common(steel).Volume
    if volume>1e-4:deck_required_notches.append({'steel_object':n,'intersection_in3':volume/I**3,'status':'Deck notch unresolved; rectangular deck placeholder retained.'})
  return checks
 checks=validate();progress('Loft geometry validated: deck and30 joists created; existing group and optional ledge hidden. Saving and reopening.')
 d.Label='Proposed renovated loft and primary frame — geometry only';d.recompute();d.saveAs(str(ROOT/'Proposed-Garage.FCStd'));A.closeDocument(d.Name)
 d=A.openDocument(str(ROOT/'Proposed-Garage.FCStd'));A.setActiveDocument(d.Name);checks=validate();assert sha(ROOT/'Existing-Garage.FCStd')==oldhash
 group_records=[];paths={}
 def scan(g,path):
  current=path+[g.Name];group_records.append({'name':g.Name,'label':g.Label,'path':current,'visible':bool(g.ViewObject.Visibility),'children':[o.Name for o in g.Group]})
  for o in g.Group:
   paths.setdefault(o.Name,[]).append(current)
   if o.TypeId=='App::DocumentObjectGroup':scan(o,current)
 scan(d.getObject('ExistingGarage'),[]);scan(d.getObject('ProposedStructure'),[])
 def mesh(names,wnames=[],reference=False):
  data={'units':'mm','request_id':RID,'objects':[],'groups':group_records,'existing_group_hidden':True,'analysis_reference_only':reference}
  for n in names:
   o=d.getObject(n);vs,ts=shape(o).tessellate(.5);trans=o.ViewObject.Transparency
   data['objects'].append({'name':n,'label':o.Label,'color':list(o.ViewObject.ShapeColor),'transparency_percent':trans,'opacity':1-trans/100,'visible':bool(o.ViewObject.Visibility),'group_paths':paths.get(n,[]),'vertices':[[v.x,v.y,v.z] for v in vs],'triangles':[list(t) for t in ts]})
  for n in wnames:
   o=d.getObject(n)
   if not o.ViewObject.Visibility:continue
   lines=[]
   for e in o.Shape.Edges:
    ps=e.discretize(Number=65) if o.TypeId=='Part::Circle' else [e.Vertexes[0].Point,e.Vertexes[-1].Point];lines.append([[p.x,p.y,p.z] for p in ps])
   data['objects'].append({'name':n,'label':o.Label,'color':list(o.ViewObject.LineColor),'visible':True,'group_paths':paths.get(n,[]),'vertices':[],'triangles':[],'lines':lines})
  return data
 visible=steel_names+visible_new;defaultmesh=mesh(visible,wire_names)
 for name in ['renovated-loft-mesh.json','proposed-overlay-full.json','proposed-overlay-new.json']:put(name,defaultmesh)
 put('existing-garage-analysis-mesh.json',mesh(oldnames,reference=True));put('renovated-loft-only-mesh.json',mesh(visible_new));put('optional-loading-ledge-mesh.json',mesh(['OptionalNorthLedgeDeck'],reference=True))
 Part.makeCompound([shape(d.getObject(n)) for n in visible]).exportStep(str(ROOT/'Proposed-Garage-overlay.step'))
 step=Part.Shape();step.read(str(ROOT/'Proposed-Garage-overlay.step'));assert step.isValid() and len(step.Solids)==len(visible)
 loft_data={'units':'inches','deck':dict(inp['deck'],object='RenovatedDeck',area_square_feet=224.25*177/144,finished_floor_elevation_inches=120.75),'joists':wood_records,'joist_centers_x_inches':centers,'spacing_inches':16,'edge_closure_spacing_inches':centers[-1]-centers[-2],'bay_y_extents_inches':inp['joists']['bays_y'],'open_south_depth_inches':72,'west_walkway_x_inches':[-32,0],'west_walkway_decked':False,'optional_north_loading_ledge':dict(inp['optional_loading_ledge'],object='OptionalNorthLedgeDeck',supports_resolved=False),'notes':[v for _,v in notes],'loads_or_strength_selected':False,'wood_steel_intersections':[],'deck_required_notches':deck_required_notches}
 put('renovated-loft-parameters.json',loft_data)
 progress('Saved and reopened loft. Exporting intended native member axes and explicit joint offsets; no solver is being run.')
 spec=importlib.util.spec_from_file_location('cad_analytical_export',ROOT/'cad-analytical-export.py');mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod);analytical=mod.export_analytical(d,reg,ROOT,loft_data)
 # Keep the100 steel-member register intact, adding wood/deck as a separate domain.
 reg.update(request_id=RID,renovated_loft=loft_data,analytical_geometry_file=str(ROOT/'optimization/cad-analytical-members.json'),existing_group_visible=False)
 put('proposed-overlay-member-register.json',reg)
 params=json.loads((backup/'proposed-overlay-parameters.json').read_text());params.update(request_id=RID,renovated_loft=loft_data,existing_group_visible=False,default_mesh_scope='Visible proposed steel + renovated joists/deck + roof/reference lines; existing excluded.')
 put('proposed-overlay-parameters.json',params)
 validation={'request_id':RID,'native_reopen_success':True,'existing_sha256_before':oldhash,'existing_sha256_after':sha(ROOT/'Existing-Garage.FCStd'),'authoritative_existing_unchanged':True,'native_existing_copy_preserved':True,'all100_steel_solids_preserved':True,'existing_group_hidden':True,'optional_ledge_hidden':True,'deck_transparency_percent':60,'new_loft_solid_count':len(newnames),'visible_loft_solid_count':len(visible_new),'wood_joist_count':len(joists),'default_visible_solid_count':len(visible),'step_solid_count':len(step.Solids),'loft_objects':checks,'analytical_native_object_count':analytical['native_structural_object_count'],'analytical_segment_count':analytical['analytical_segment_count'],'explicit_connection_count':len(analytical['connectivity']['intended_connections']),'mesh_axes_inferred':False,'wood_steel_intersections':[],'deck_required_notches':deck_required_notches,'automatic_node_snapping':False,'strength_analysis_run':False,'geometry_snapshot_sha256':sha(ROOT/'Proposed-Garage.FCStd')}
 put('renovated-loft-validation.json',validation)
 (ROOT/'RENOVATED-LOFT-README.md').write_text('# Renovated loft geometry\n\nExistingGarage is hidden as a group. All existing native geometry and all100 steel solids remain unchanged; Existing-Garage.FCStd is untouched.\n\n'+ '\n\n'.join(v for _,v in notes)+'\n\nThe default full/new mesh exports now contain only visible proposed steel, renovated loft deck/joists and reference lines. existing-garage-analysis-mesh.json preserves the107 existing final solids separately. Mesh objects carry group paths, transparency percent and opacity. The optional ledge is isolated in optional-loading-ledge-mesh.json and hidden in CAD.\n\noptimization/cad-analytical-members.json contains exact native construction axes in INCHES. Web endpoints come from original Sketcher profile cap pairs, not mesh PCA. Top chords split where generator roof planes change. All named connections retain their axis offsets; no global snapping or fictitious zero-gap joints. Main/cap axis steps are reported explicitly. Wood joists and floor area are separate from steel members.\n\nRun renovated-loft-generator.py with bundled FreeCAD Python to reproduce from the immutable pre-loft full-frame snapshot; active proposed-overlay-generator.py routes here. No earlier frame generation or structural analysis is executed.\n')
 files=['Proposed-Garage.FCStd','Proposed-Garage-overlay.step','renovated-loft-mesh.json','renovated-loft-only-mesh.json','existing-garage-analysis-mesh.json','optional-loading-ledge-mesh.json','optimization/cad-analytical-members.json','renovated-loft-parameters.json','renovated-loft-validation.json','RENOVATED-LOFT-README.md','renovated-loft-generator.py','renovated-loft-input.json','cad-analytical-export.py','proposed-overlay-generator.py','proposed-overlay-full.json','proposed-overlay-new.json','proposed-overlay-parameters.json','proposed-overlay-member-register.json']
 R.update(status='complete',completed_utc=datetime.now(timezone.utc).isoformat(),artifact_paths=[str(ROOT/n) for n in files],artifact_sha256={n:sha(ROOT/n) for n in files},existing_unchanged=True,steel_unchanged=True,native_reopen_success=True,wood_joists=len(joists),new_loft_solids=len(newnames),default_visible_solids=len(visible),existing_hidden=True,optional_ledge_hidden=True,analytical_native_objects=analytical['native_structural_object_count'],analytical_segments=analytical['analytical_segment_count'],explicit_connections=len(analytical['connectivity']['intended_connections']),geometry_snapshot_sha256=sha(ROOT/'Proposed-Garage.FCStd'),strength_analysis_run=False,deck_required_notches=deck_required_notches,notes=[v for _,v in notes])
 put('loft-result.json',R);progress('COMPLETE: updated native loft saved and reopened; default meshes and analytical axes exported. See loft-result.json.')
except Exception as e:
 R.update(status='failed',error=str(e),traceback=traceback.format_exc());put('loft-result.json',R);progress('FAILED: '+str(e)+'; see loft-result.json.')
finally:
 Path('/home/ros/Documents/Codex/2026-09-09/oh/garage-agent-result.json').write_text(json.dumps(R,indent=2)+'\n');sys.stdout.flush();sys.stderr.flush();os._exit(0 if R['status']=='complete' else 1)
