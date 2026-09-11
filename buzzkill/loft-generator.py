#!/usr/bin/env python3
"""Add three native existing lofts to a roof-inclusive garage; no external proxies."""
import os,sys,json,hashlib,math,traceback,shutil
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parent
os.environ.setdefault('QT_QPA_PLATFORM','offscreen');os.environ.setdefault('FONTCONFIG_FILE','/etc/fonts/fonts.conf')
sys.path.insert(0,'/opt/freecad-1.1.3/usr/lib')
import FreeCAD as A,FreeCADGui as G,Part
I=25.4
R={'request_id':'EXISTING-LOFTS-004','status':'failed','timestamp_utc':datetime.now(timezone.utc).isoformat(),'errors':[],'artifact_paths':[]}
def put(name,data):
 p=ROOT/name;p.write_text(json.dumps(data,indent=2)+'\n');assert json.loads(p.read_text())==data

def shape(o):
 s=o.Shape.copy();s.Placement=o.getGlobalPlacement();return s

def bounds(s):
 b=s.BoundBox;return {'x_min':b.XMin,'x_max':b.XMax,'y_min':b.YMin,'y_max':b.YMax,'z_min':b.ZMin,'z_max':b.ZMax}

def near(a,b):return math.isclose(a,b,rel_tol=1e-9,abs_tol=1e-5)
try:
 G.showMainWindow();d=A.openDocument(str(ROOT/'Existing-Garage.FCStd'));A.setActiveDocument(d.Name)
 if d.getObject('ExistingLofts') and '--replace-lofts' not in sys.argv:raise RuntimeError('Use --replace-lofts to rebuild existing loft groups after backup.')
 revision=json.loads((ROOT/'lofts-revision-input.json').read_text())
 original_hashes={n:hashlib.sha256((ROOT/n).read_bytes()).hexdigest() for n in ['Existing-Garage.FCStd','Proposed-Garage.FCStd']}
 progress=json.loads((ROOT/'lofts-progress.txt').read_text()) if (ROOT/'lofts-progress.txt').exists() else {}
 backup=Path(progress.get('backup_directory',''))
 if not (backup/'sha256.json').is_file() or json.loads((backup/'sha256.json').read_text()).get('Existing-Garage.FCStd')!=original_hashes['Existing-Garage.FCStd']:
  backup=ROOT/'backups'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ-before-lofts');backup.mkdir(parents=True,exist_ok=False)
  for n,h in original_hashes.items():shutil.copy2(ROOT/n,backup/n);assert hashlib.sha256((backup/n).read_bytes()).hexdigest()==h
  (backup/'sha256.json').write_text(json.dumps(original_hashes,indent=2)+'\n')
 R['backup_directory']=str(backup)
 roofval=json.loads((ROOT/'roof-validation.json').read_text());wallnames=json.loads((ROOT/'validation.json').read_text())['documents']['Existing-Garage.FCStd']['final_visible_objects']
 protected_names=wallnames+[x['name'] for x in roofval['roof_objects']]
 unchanged_lofts={o.Name:shape(o) for o in d.Objects if (o.Name.startswith(('MiddleLoft','NorthLoft')) or o.Name=='SouthLoftDeck' or (o.Name.startswith('SouthLoft') and o.Name.endswith(('WoodHangerStock','StitchPlate')))) and o.TypeId=='Part::Box'}
 protected={n:shape(d.getObject(n)) for n in protected_names};camera=G.activeDocument().activeView().getCamera()
 if d.getObject('ExistingLofts'):
  removable=[o.Name for o in d.Objects if o.Name in ['ExistingLofts','LoftParameters'] or o.Name.startswith(('SouthLoft','MiddleLoft','NorthLoft'))]
  assert not set(removable).intersection(protected_names)
  for name in reversed(removable):d.removeObject(name)
  d.recompute()
 west=sorted([m for m in roofval['member_layout'] if m['name'].startswith('West')],key=lambda m:m['station_inches'])
 east=sorted([m for m in roofval['member_layout'] if m['name'].startswith('East')],key=lambda m:m['station_inches'])
 main=west[2:7];assert [m['station_inches'] for m in main]==[64,88,112,137,161]
 root=d.addObject('App::DocumentObjectGroup','ExistingLofts');root.Label='Three existing lofts — adjustable approximations'
 root.addProperty('App::PropertyString','Assumptions');root.Assumptions='Measured south west bound and north jamb-relative bounds; south east bound provisional. Hanger/strap placements and stitch plates schematic. No structural capacity claim; unknown reclaimed floorboards omitted.'
 groups={};framing={};new=[];joists=[];decks=[];support_records=[]
 for name,label in [('SouthLoft','South loft — measured 47 in depth'),('MiddleLoft','Middle loft — five triple joists'),('NorthLoft','North loft — approx. 29 in')]:
  g=d.addObject('App::DocumentObjectGroup',name);g.Label=label;root.addObject(g);groups[name]=g
  f=d.addObject('App::DocumentObjectGroup',name+'Framing');f.Label='Framing — '+label;g.addObject(f);framing[name]=f
  h=d.addObject('App::DocumentObjectGroup',name+'Connections');h.Label='Connections — schematic';g.addObject(h);groups[name+'Connections']=h
 sheet=d.addObject('Spreadsheet::Sheet','LoftParameters');sheet.Label='Loft dimensions — assumptions editable';d.getObject('Dimensions').addObject(sheet)
 sheet.set('A1','Loft parameter');sheet.set('B1','Value in inches');sheet.set('C1','Basis / assumption');sheet.setStyle('A1:C1','bold','add')
 sheet.setColumnWidth('A',265);sheet.setColumnWidth('B',160);sheet.setColumnWidth('C',660)
 row=2;cells={}
 def param(alias,label,value,note=''):
  global row
  cell=f'B{row}';sheet.set(f'A{row}',label);sheet.set(cell,f'{value} in' if isinstance(value,(int,float)) else '='+value);sheet.setAlias(cell,alias);sheet.set(f'C{row}',note);cells[alias]=cell;row+=1
 for args in [
 ('CoreWidth','Garage core width','Parameters.Width','Linked; existing walls unchanged'),('CoreLength','Garage core length','Parameters.Length','Linked'),('WallCore','Existing wall core thickness','Parameters.Core','6 inches; NOT changed to joist depth'),('JoistBottom','All joist bottoms','Parameters.Height','98.5 inches, wall-top datum'),('JoistThickness','Actual 2x6 thickness',1.5,'On edge'),('JoistDepth','Actual 2x6 depth',5.5,'Joist tops at 104 inches'),('DeckThickness','Deck thickness',.75,'Deck tops at 104.75 inches'),('SouthDepth','South projection from interior wall',47,'OWNER MEASURED, second south rafter support'),('SouthWestInside','South west bound from inside west',69,'OWNER EXPLICIT: use 69, not measured station 70'),('MainFirstInside','Main first support from inside south',72,'OWNER MEASURED, third support'),('NorthEastInset','North east bound west of door east jamb',25,'OWNER CONFIRMED inside opening'),('NorthDepth','North projection from interior wall',29,'Approximate, adjustable'),('SideOpening','Middle deck side openings',48,'From each INSIDE east/west wall'),('FrameSpacing','South/north cross framing spacing',24,'Approximate fixed-count topology'),('SupportInset','Hanger/strap inset from platform edges',12,'ASSUMED; follows actual revised platform boundaries'),('PlateThickness','Schematic stitch plate thickness',.125,'ASSUMED illustrative flat plate, no fastener schedule'),('PlateWidth','Schematic stitch plate width',3,'ASSUMED'),('PlateHeight','Schematic stitch plate height',6,'ASSUMED'),('StrapThickness','North metal strap thickness',.125,'ASSUMED'),('StrapWidth','North metal strap width',1.5,'ASSUMED'),('BearingInset','Main joist end inset','WallCore/2','ASSUMED ends at wall midlines; no engineered bearing detail')]:param(*args)
 for k,m in enumerate(main,1):
  offset=m['station_inches']-main[0]['station_inches']
  param('MainOffset'+str(k),'Provisional main station offset '+str(k),offset,'Retained prior relative spacing; later stations UNMEASURED')
  param('MainStation'+str(k),'Main support center '+str(k),'WallCore+MainFirstInside+MainOffset'+str(k),'First measured; later centers shifted with prior spacings, roof unchanged')
 for args in [('SouthWest','South platform west core bound','WallCore+SouthWestInside','Measured 69 from inside west'),('SouthWidth','South platform width',96,'Five positions / four approximately 24-inch bays'),('SouthEast','South platform east core bound','SouthWest+SouthWidth','Owner correction: stops after five support positions'),('NorthWest','North platform west core bound','Parameters.Width-Parameters.O5Offset-Parameters.O5Width','Garage-door west jamb'),('NorthEast','North platform east core bound','Parameters.Width-Parameters.O5Offset-NorthEastInset','25 inches WEST of garage-door east jamb'),('JoistTop','Joist top elevation','JoistBottom+JoistDepth',''),('DeckTop','Deck top elevation','JoistTop+DeckThickness',''),('SouthEdge','South free north edge','WallCore+SouthDepth',''),('NorthEdge','North free south edge','CoreLength-WallCore-NorthDepth',''),('MainDeckX','Main deck west edge','WallCore+SideOpening',''),('MainDeckWidth','Main deck width','CoreWidth-2*WallCore-2*SideOpening',''),('MainDeckY','Main deck south edge','MainStation1-1.5*JoistThickness','Covers outer edges of first/last triple assembly'),('MainDeckLength','Main deck north-south length','MainStation5-MainStation1+3*JoistThickness','Four station bays plus end half-widths')]:param(*args)
 d.recompute()
 def framing_x(west_alias,east_alias):
  west_value=getattr(sheet,west_alias).Value;east_value=getattr(sheet,east_alias).Value
  count=int(math.floor((east_value-west_value-sheet.JoistThickness.Value)/sheet.FrameSpacing.Value))+1
  values=[f'{west_alias}+{n}*FrameSpacing' for n in range(count)]
  if not near(west_value+(count-1)*sheet.FrameSpacing.Value,east_value-sheet.JoistThickness.Value):values.append(f'{east_alias}-JoistThickness')
  return values
 def q(expr):
  import re
  return re.sub(r'\b('+ '|'.join(sorted(cells,key=len,reverse=True))+r')\b',lambda m:'LoftParameters.'+m[0],expr)
 def box(name,group,size,pos,label,color=(.70,.49,.29),isjoist=False):
  o=d.addObject('Part::Box',name);o.Label=label;group.addObject(o)
  for prop,val in zip(['Length','Width','Height','Placement.Base.x','Placement.Base.y','Placement.Base.z'],size+pos):o.setExpression(prop,q(val))
  o.ViewObject.ShapeColor=color;o.ViewObject.Visibility=True;new.append(o)
  if isjoist:joists.append(o)
  return o
 def deck(name,x,y,length,width,label):
  o=box(name+'Deck',groups[name],[length,width,'DeckThickness'],[x,y,'JoistTop'],label,(.70,.66,.49));decks.append(o)
 # South: one back ledger, triple free-edge beam and eleven north-south joists.
 for k in range(3):box('SouthLoftWallSidePly'+str(k+1),framing['SouthLoft'],['CoreWidth-2*BearingInset','JoistThickness','JoistDepth'],['BearingInset',f'WallCore+{k}*JoistThickness','JoistBottom'],f'South wall-side full-width built-up ply {k+1} of 3 — interpreted',isjoist=True)
 for k in range(3):box('SouthLoftFreeEdgePly'+str(k+1),framing['SouthLoft'],['CoreWidth-2*BearingInset','JoistThickness','JoistDepth'],['BearingInset',f'SouthEdge-3*JoistThickness+{k}*JoistThickness','JoistBottom'],f'South free edge built-up ply {k+1} of 3',isjoist=True)
 for k,x in enumerate(framing_x('SouthWest','SouthEast'),1):
  box('SouthLoftJoist'+str(k),framing['SouthLoft'],['JoistThickness','SouthDepth-6*JoistThickness','JoistDepth'],[x,'WallCore+3*JoistThickness','JoistBottom'],f'South N–S framing {k} — approximate spacing',isjoist=True)
 deck('SouthLoft','SouthWest','WallCore','SouthEast-SouthWest','SouthDepth','South loft deck — toggle independently')
 # Middle: five east-west triple assemblies, matching existing roof y stations.
 for k in range(1,6):
  ag=d.addObject('App::DocumentObjectGroup','MiddleLoftAssembly'+str(k));ag.Label=f'Middle E–W assembly {k} — shifted provisional station';framing['MiddleLoft'].addObject(ag)
  ag.addProperty('App::PropertyString','ConnectionDescription');ag.ConnectionDescription='Described as bolted; no invented bolt locations/schedule. Outer plies flank the assembly reference; center ply lies between. Revised main centers differ from unchanged roof stations; connections schematic.'
  for ply in range(3):box(f'MiddleLoftStation{k+2}Ply{ply+1}',ag,['CoreWidth-2*BearingInset','JoistThickness','JoistDepth'],['BearingInset',f'MainStation{k}-1.5*JoistThickness+{ply}*JoistThickness','JoistBottom'],f'Middle roof station {k+2}, ply {ply+1}/3',isjoist=True)
 deck('MiddleLoft','MainDeckX','MainDeckY','MainDeckWidth','MainDeckLength','Middle central deck — 48-inch openings at both sides')
 # North: simple single-ply edges and N–S framing, no triple construction.
 for label,y in [('FreeEdge','NorthEdge'),('WallEdge','CoreLength-WallCore-JoistThickness')]:
  box('NorthLoft'+label,framing['NorthLoft'],['NorthEast-NorthWest','JoistThickness','JoistDepth'],['NorthWest',y,'JoistBottom'],'North '+label+' — single ply',isjoist=True)
 for k,x in enumerate(framing_x('NorthWest','NorthEast'),1):
  box('NorthLoftJoist'+str(k),framing['NorthLoft'],['JoistThickness','NorthDepth-2*JoistThickness','JoistDepth'],[x,'NorthEdge+JoistThickness','JoistBottom'],f'North simple N–S framing {k} — approximate spacing',isjoist=True)
 deck('NorthLoft','NorthWest','NorthEdge','NorthEast-NorthWest','NorthDepth','North plywood deck — toggle independently')
 def angled(name,group,start,end,width,depth,color,label):
  assembly=d.addObject('App::Part',name);assembly.Label=label;group.addObject(assembly)
  axis=d.addObject('App::DocumentObject',name+'Axis');axis.Label=label+' endpoints — adjustable';d.getObject('Dimensions').addObject(axis)
  for prop in ['Start','End']:axis.addProperty('App::PropertyVector',prop,'Connection layout')
  for prop in ['Run','Rise']:axis.addProperty('App::PropertyLength',prop,'Connection layout')
  for prop in ['Pitch','Yaw']:axis.addProperty('App::PropertyAngle',prop,'Connection layout')
  for k in range(3):
   axis.setExpression('Start.'+'xyz'[k],q(start[k]));axis.setExpression('End.'+'xyz'[k],q(end[k]));assembly.setExpression('Placement.Base.'+'xyz'[k],name+'Axis.Start.'+'xyz'[k])
  axis.setExpression('Run','sqrt((End.x-Start.x)^2+(End.y-Start.y)^2)');axis.setExpression('Rise','End.z-Start.z');axis.setExpression('Pitch','atan2(Rise; Run)');axis.setExpression('Yaw','atan2(End.y-Start.y; End.x-Start.x)')
  assembly.Placement.Rotation=A.Rotation(A.Vector(0,0,1),0);assembly.setExpression('Placement.Rotation.Angle',name+'Axis.Yaw')
  o=d.addObject('Part::Box',name+'Stock');o.Label=label+' — rectangular schematic';assembly.addObject(o)
  o.setExpression('Length',f'sqrt({name}Axis.Run^2+{name}Axis.Rise^2)');o.setExpression('Width',q(width));o.setExpression('Height',q(depth))
  o.Placement.Rotation=A.Rotation(A.Vector(0,1,0),0);o.setExpression('Placement.Rotation.Angle',f'-{name}Axis.Pitch')
  o.setExpression('Placement.Base.x',f'sin({name}Axis.Pitch)*({q(depth)})/2');o.setExpression('Placement.Base.y',f'-({q(width)})/2');o.setExpression('Placement.Base.z',f'-cos({name}Axis.Pitch)*({q(depth)})/2')
  o.ViewObject.ShapeColor=color;o.ViewObject.Visibility=True;new.append(o);support_records.append({'name':name,'axis':axis.Name,'stock':o.Name})
  return axis
 # Schematic supports follow revised deck bounds and target extant roof members.
 def anchor_height(target,x,y):
  return f'{target}.Start.z*1 mm+tan({target}.Pitch)*sqrt((({x})-{target}.Start.x*1 mm)^2+(({y})-{target}.Start.y*1 mm)^2)-RoofParameters.BoardDepth/(2*cos({target}.Pitch))'
 roofmap={m['name']:m['output'] for m in roofval['member_layout']}
 for side in ['West','East']:
  x='SouthWest+SupportInset' if side=='West' else 'SouthEast-SupportInset'
  target='SouthNear4Axis' if side=='West' else 'SouthFar4Axis'
  tx=target+'.Start.x*1 mm'
  ty='SouthEdge+JoistThickness/2'
  top=anchor_height(target,tx,ty)
  a=angled('SouthLoft'+side+'WoodHanger',groups['SouthLoftConnections'],[x,'SouthEdge+JoistThickness/2','JoistBottom+JoistDepth/2'],[tx,ty,top],'JoistThickness','JoistDepth',(.50,.31,.16),f'South {side.lower()} 2x6 hanger — boundary-following schematic')
  support_records[-1]['roof_anchor_output']=roofmap[target[:-4]]
  for end in ['Start','End']:
   box('SouthLoft'+side+end+'StitchPlate',groups['SouthLoftConnections'],['PlateThickness','PlateWidth','PlateHeight'],[f'{a.Name}.{end}.x*1 mm+JoistThickness/2',f'{a.Name}.{end}.y*1 mm-PlateWidth/2',f'{a.Name}.{end}.z*1 mm-PlateHeight/2'],f'South {side.lower()} {end.lower()} stitch plate — schematic, no bolt pattern',(.43,.46,.49))
  x='NorthWest+SupportInset' if side=='West' else 'NorthEast-SupportInset'
  target='NorthNear3Axis' if side=='West' else 'NorthFar3Axis'
  tx=target+'.Start.x*1 mm';ty='NorthEdge';top=anchor_height(target,tx,ty)
  angled('NorthLoft'+side+'MetalStrap',groups['NorthLoftConnections'],[x,'NorthEdge','JoistBottom+JoistDepth/2'],[tx,ty,top],'StrapThickness','StrapWidth',(.42,.46,.50),f'North {side.lower()} metal strap — follows revised deck bound')
  support_records[-1]['roof_anchor_output']=roofmap[target[:-4]]
 d.recompute()
 sheet.ViewObject.Visibility=False
 def validate(check_old=True):
  data=[]
  for o in new:
   s=shape(o);assert s.isValid() and len(s.Solids)==1,(o.Name,'invalid');assert o.ViewObject.Visibility,o.Name
   data.append({'name':o.Name,'label':o.Label,'volume_mm3':s.Volume,'valid':True,'solids':1,'visible':True,'bounds_mm':bounds(s),'view_provider':o.ViewObject.TypeId})
  for o in joists:
   b=shape(o).BoundBox;assert near(b.ZMin,98.5*I) and near(b.ZMax,104*I),(o.Name,b)
  for o in decks:
   b=shape(o).BoundBox;assert near(b.ZMin,104*I) and near(b.ZMax,104.75*I),(o.Name,b)
  if check_old:
   for n,old in protected.items():
    now=shape(d.getObject(n));assert near(now.Volume,old.Volume) and now.cut(old).Volume<1e-4 and old.cut(now).Volume<1e-4,(n,'prior geometry changed')
    assert d.getObject(n).ViewObject.Visibility,(n,'prior visibility changed')
  for m in roofval['member_layout']:
   if m['kind']!='ridge':assert shape(d.getObject(m['output'])).BoundBox.ZMin>=98.5*I-1e-6
  south=shape(d.getObject('SouthLoftDeck')).BoundBox;north=shape(d.getObject('NorthLoftDeck')).BoundBox;middle=shape(d.getObject('MiddleLoftDeck')).BoundBox
  assert near(south.YMin,6*I) and near(south.YLength,47*I) and near(south.XMin,75*I) and near(south.XMax,171*I)
  assert near(north.YMax,243*I) and near(north.YLength,29*I) and near(north.XMin,56.25*I) and near(north.XMax,196.25*I)
  assert near(middle.XMin-6*I,48*I) and near(243.5*I-middle.XMax,48*I)
  assert near(middle.YMin,75.75*I) and near(middle.YMax,177.25*I)
  for n,old in unchanged_lofts.items():
   now=shape(d.getObject(n));assert near(now.Volume,old.Volume) and now.cut(old).Volume<1e-4 and old.cut(now).Volume<1e-4,(n,'other loft changed')
  southparts=[o for o in new if o.Name.startswith('SouthLoft') and not o.Name.startswith(('SouthLoftFreeEdgePly','SouthLoftWallSidePly'))]
  assert all(shape(o).BoundBox.XMin>=75*I-1e-6 and shape(o).BoundBox.XMax<=171*I+1e-6 for o in southparts)
  boundary=[o for o in joists if o.Name.startswith(('SouthLoftFreeEdgePly','SouthLoftWallSidePly'))]
  assert len(boundary)==6
  for o in boundary:
   bb=shape(o).BoundBox;assert near(bb.XMin,3*I) and near(bb.XMax,246.5*I)
  for o in joists:
   if o.Name.startswith('SouthLoftJoist'):
    bb=shape(o).BoundBox;assert near(bb.YMin,10.5*I) and near(bb.YMax,48.5*I)
  assert len([o for o in joists if o.Name.startswith('SouthLoftJoist')])==5
  for k,expected in enumerate([78,102,126,151,175],3):
   bb=shape(d.getObject(f'MiddleLoftStation{k}Ply2')).BoundBox;assert near((bb.YMin+bb.YMax)/2,expected*I)
  for rec in support_records:
   axis=d.getObject(rec['axis']);assert shape(d.getObject(rec['roof_anchor_output'])).isInside(axis.End,1e-5,True),(rec['name'],'anchor outside existing roof member')
  assert near(d.getObject('Parameters').Core.Value,6*I)
  return data
 checks=validate()
 # Edit projection and verify a downstream framing/deck change, then restore.
 oldedge=shape(d.getObject('SouthLoftDeck')).BoundBox.YMax
 sheet.set(cells['SouthDepth'],'48 in');d.recompute();assert near(shape(d.getObject('SouthLoftDeck')).BoundBox.YMax-oldedge,I)
 assert near(shape(d.getObject('SouthLoftFreeEdgePly3')).BoundBox.YMax,54*I)
 sheet.set(cells['SouthDepth'],'47 in');d.recompute()
 sheet.set(cells['DeckThickness'],'1 in');d.recompute();assert all(near(shape(o).BoundBox.ZMax,105*I) for o in decks)
 sheet.set(cells['DeckThickness'],'0.75 in');d.recompute();checks=validate()
 newnames=[o.Name for o in new];joistnames=[o.Name for o in joists];decknames=[o.Name for o in decks]
 for o in decks:o.ViewObject.Visibility=False
 assert all(o.ViewObject.Visibility for o in joists)
 for o in decks:o.ViewObject.Visibility=True
 G.activeDocument().activeView().setCamera(camera);d.recompute();d.save()
 A.closeDocument(d.Name);d=A.openDocument(str(ROOT/'Existing-Garage.FCStd'));A.setActiveDocument(d.Name)
 new=[d.getObject(n) for n in newnames];joists=[d.getObject(n) for n in joistnames];decks=[d.getObject(n) for n in decknames];checks=validate()
 assert 'Camera' in G.activeDocument().activeView().getCamera()
 allobjects=[d.getObject(n) for n in protected_names]+new
 Part.makeCompound([shape(o) for o in allobjects]).exportStep(str(ROOT/'Existing-Garage-lofts.step'))
 def mesh(objects):
  result={'units':'mm','objects':[]}
  for o in objects:
   vs,ts=shape(o).tessellate(.5);result['objects'].append({'name':o.Name,'label':o.Label,'color':list(o.ViewObject.ShapeColor),'vertices':[[v.x,v.y,v.z] for v in vs],'triangles':[list(t) for t in ts]})
  return result
 put('visible-mesh-lofts.json',mesh(allobjects));put('visible-mesh-lofts-only.json',mesh(new))
 step=Part.Shape();step.read(str(ROOT/'Existing-Garage-lofts.step'));assert step.isValid() and len(step.Solids)==len(allobjects)
 assert hashlib.sha256((ROOT/'Proposed-Garage.FCStd').read_bytes()).hexdigest()==original_hashes['Proposed-Garage.FCStd']
 params={'request_id':R['request_id'],'units':'inches','joist_bottom':98.5,'joist_top':104,'joist_actual_section':[1.5,5.5],'deck_thickness':.75,'deck_top':104.75,'wall_core_unchanged':6,
 'south':{'x_extent':[75,171],'y_extent':[6,53],'west_start_inside_west':69,'projection':47,'width':96,'five_support_positions_four_approx_24_in_bays':True,'east_bound_core':171,'free_edge_plies':3,'wall_side_boundary_plies':3,'boundary_joist_x_extent':[3,246.5],'wall_side_joist_y_extent':[6,10.5],'free_edge_joist_y_extent':[48.5,53],'crossmember_y_extent':[10.5,48.5],'south_wall_side_triple_is_interpretation':True,'wood_hangers':2,'hanger_bottom_x':[87,159],'hanger_anchor_notes':'Left follows new west edge and targets existing SouthNear4; right follows the new east edge and targets existing SouthFar4. Connections remain schematic, not measured.','stitch_plates':4,'plate_section_assumed':[.125,3,6]},
 'middle':{'station_indices_from_south':[3,4,5,6,7],'station_y':[78,102,126,151,175],'first_center_inside_south':72,'relative_offsets_provisional':[0,24,48,73,97],'translation_from_prior_inches':14,'plies_per_assembly':3,'joist_x_extent':[3,246.5],'bearing_ends_at_wall_midlines_assumed':True,'deck_x_extent':[54,195.5],'deck_y_extent':[75.75,177.25],'open_strip_each_side':48,'bolts':'Described only; no invented schedule or exact roof alignment','unknown_reclaimed_floorboards':'Not located or fabricated'},
 'north':{'x_extent':[56.25,196.25],'y_extent':[214,243],'width':140,'projection':29,'west_bound':'garage-door west jamb','east_bound':'25 inches WEST of garage-door east jamb, inside opening','garage_door_x_extent':[56.25,221.25],'simple_single_ply_edges':True,'metal_straps_assumed_count':2,'strap_bottom_x':[68.25,184.25],'strap_roof_anchors':['NorthNear3','NorthFar3'],'strap_section_assumed':[.125,1.5]},
 'roof_survey':{'south_roof_station_x_from_inside_west':[17.5,46,70],'survey_x_core':[23.5,52,76],'unchanged_model_x_core':[16,40,64],'survey_minus_model_inches':[7.5,12,12],'south_west_platform_from_inside':69,'survey_third_station_from_inside':70,'explicit_one_inch_difference_preserved':True,'south_second_support_y_core':53,'unchanged_modeled_second_station_y':40,'main_first_support_y_core':78,'unchanged_modeled_third_station_y':64,'roof_relayout_performed':False},
 'cross_framing_spacing_assumed':24,'assumptions':['South deck remains96 inches wide, x75..171; both bounding E-W joists now span wall-to-wall x3..246.5 with three plies each. Southern triple assembly interprets the owner statement between two joists; crossmembers fit between them.','Later four main support centers retain prior relative spacings after shifting first center to measured72 inches from inside south; they remain unmeasured.','Main joist end faces at wall midlines remain provisional.','Hangers and straps follow revised platform boundaries with assumed12-inch insets and connect schematically to extant roof members. These connections are not surveyed exact details.','Stitch plates, strap sections and fastenings remain illustrative.','Measured roof stations disagree with existing model; survey recorded without changing roof.','Unknown existing reclaimed horizontal members remain unmodeled.','No structural capacity or exact joinery claim.']}
 put('lofts-parameters.json',params)
 validation={'request_id':R['request_id'],'freecad_version':A.Version(),'new_solid_count':len(new),'joist_solid_count':len(joists),'deck_solid_count':len(decks),'full_model_solid_count':len(allobjects),'by_loft':{name:sum(o.Name.startswith(name) for o in new) for name in ['SouthLoft','MiddleLoft','NorthLoft']},'objects':checks,'elevations_inches':{'joist_bottom':98.5,'joist_top':104,'deck_bottom':104,'deck_top':104.75},'native_reopen_success':True,'visible_view_providers':True,'decks_independently_toggleable':True,'prior_61_solids_unchanged_geometrically':True,'middle_and_north_lofts_unchanged_geometrically':True,'south_five_cross_framing_positions':True,'south_deck_crossmembers_hangers_within_x_75_171_inches':True,'south_two_three_ply_boundary_assemblies_span_x_3_246_5':True,'south_deck_and_hangers_unchanged_geometrically':True,'roof_global_98_5_datum_preserved':True,'wall_core_6_inches_preserved':True,'proposed_sha256_unchanged':True,'original_sha256':original_hashes,'backup_directory':str(backup),'parameter_checks':{'south_projection_48_in_updates_deck_and_free_edge_then_restored':True,'deck_thickness_1_in_updates_all_decks_then_restored':True},'step_valid':True,'step_solid_count':len(step.Solids),'support_connections':support_records,'limitations':params['assumptions']}
 put('lofts-validation.json',validation)
 names=['Existing-Garage.FCStd','loft-generator.py','lofts-revision-input.json','Existing-Garage-lofts.step','visible-mesh-lofts.json','visible-mesh-lofts-only.json','lofts-parameters.json','lofts-validation.json','LOFTS-README.md']
 for n in names:assert (ROOT/n).stat().st_size>0
 R.update(status='complete',summary='South loft now lies between two full-width three-ply E-W boundary joists; narrow deck and hangers preserved. Middle/north geometry preserved. Supports follow new bounds and remain schematic. Previous walls and globally clipped roof unchanged; Proposed unchanged. Shape, elevation, extents, restored parameter and native reopen checks passed.',artifact_paths=[str(ROOT/n) for n in names],counts=validation['by_loft'],new_solids=len(new),full_model_solids=len(allobjects),elevations_inches=validation['elevations_inches'],native_reopen_success=True,previous_geometry_preserved=True,proposed_unchanged=True)
 A.closeDocument(d.Name)
except Exception:R['errors'].append(traceback.format_exc())
finally:
 put('lofts-agent-result.json',R);put('lofts-progress.txt',R);print(json.dumps(R,indent=2),flush=True);sys.stdout.flush();sys.stderr.flush();os._exit(0 if R['status']=='complete' else 1)
