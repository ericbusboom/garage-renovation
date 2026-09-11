#!/usr/bin/env python3
"""Rebuild full primary concept frame from the immutable revision003 backup.
Native Sketcher profiles, extrusions, boxes, and fusions. No structural analysis.
"""
import os,sys,json,math,hashlib,shutil,traceback
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parent
os.environ.setdefault('QT_QPA_PLATFORM','offscreen');os.environ.setdefault('FONTCONFIG_FILE','/etc/fonts/fonts.conf')
sys.path.insert(0,'/opt/freecad-1.1.3/usr/lib')
import FreeCAD as A, FreeCADGui as G, Part, Sketcher
I=25.4; RID='PROPOSED-FULL-FRAME-001'
def put(n,v): (ROOT/n).write_text(json.dumps(v,indent=2)+'\n')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def progress(t): (ROOT/'newframe-progress.txt').write_text(datetime.now(timezone.utc).isoformat()+' '+RID+' '+t+'\n')
def shape(o):
 s=o.Shape.copy();s.Placement=o.getGlobalPlacement();return s

def bbox(s):
 b=s.BoundBox;return [b.XMin,b.YMin,b.ZMin,b.XMax,b.YMax,b.ZMax]
def close(a,b):return abs(a-b)<1e-5
R={'request_id':RID,'status':'running','started_utc':datetime.now(timezone.utc).isoformat()}
try:
 inp=json.loads((ROOT/'full-frame-input.json').read_text());backup=ROOT/inp['base_directory'];R['backup_directory']=str(backup)
 existing_hash=sha(ROOT/'Existing-Garage.FCStd');base_hash=sha(backup/'Proposed-Garage.FCStd');put('newframe-result.json',R)
 progress('Opening preserved revision003 model; creating native primary frame.')
 G.showMainWindow()
 d=A.openDocument(str(backup/'Proposed-Garage.FCStd'));A.setActiveDocument(d.Name)
 walls=json.loads((ROOT/'validation.json').read_text())['documents']['Existing-Garage.FCStd']['final_visible_objects']
 rv=json.loads((ROOT/'roof-validation.json').read_text());roof=[v['name'] for v in rv['roof_objects']]
 lofts=[v['name'] for v in json.loads((ROOT/'lofts-validation.json').read_text())['objects']]
 oldnames=walls+roof+lofts;assert len(oldnames)==107
 oldshapes={n:shape(d.getObject(n)) for n in oldnames};oldtypes={n:d.getObject(n).TypeId for n in oldnames}
 regbase=json.loads((backup/'proposed-overlay-member-register.json').read_text())
 removed=['ProposedNorthPostUE','ProposedNorthPostNEW','ProposedNorthPostNEE']
 register=[dict(r) for r in regbase['members'] if r['object'] not in removed]
 preserved={r['object']:shape(d.getObject(r['object'])) for r in register}
 wire_names=[o['name'] for o in json.loads((backup/'proposed-overlay-new.json').read_text())['objects'] if o.get('lines')]
 roof_names=[o.Name for o in d.getObject('RoofReference').Group]
 roof_shapes={n:shape(d.getObject(n)) for n in roof_names}
 for n in removed:
  assert d.getObject(n);d.removeObject(n)
 if d.getObject('NorthExtensionAlternative'):d.removeObject('NorthExtensionAlternative')
 d.getObject('NorthExtension').Label='North support — consolidated N1 / U-W only'
 d.Label='Proposed full primary frame — editable geometric concept'
 s=d.getObject('OverlayParameters');cell=s.getCellFromAlias('T1UpperTop');s.set(cell,'=196.64324823492282 in')
 d.getObject('T1EnvelopeReference').Label='Hidden T1 envelope — roof top 196.643248 inches'
 dims=d.getObject('ProposedDimensions');fs=d.addObject('Spreadsheet::Sheet','FullFrameParameters');dims.addObject(fs)
 fs.set('A1','Full primary frame geometry; sections unverified');fs.set('A2','Top chord VERTICAL depth');fs.set('B2','=6 in');fs.setAlias('B2','TopDepth')
 fs.set('A3','Web width');fs.set('B3','=2 in');fs.setAlias('B3','WebWidth')
 fs.set('A4','Future hanger bottom');fs.set('B4','=120 in');fs.setAlias('B4','HangerBottom')
 fs.set('A5','Future hanger top');fs.set('B5','=147.143248 in');fs.setAlias('B5','HangerTop')
 fs.set('A6','Header bottom');fs.set('B6','=204 in');fs.setAlias('B6','HeaderBottom')
 fs.set('A7','Header depth');fs.set('B7','=6 in');fs.setAlias('B7','HeaderDepth')
 fs.setColumnWidth('A',320);fs.setColumnWidth('B',180)
 primary=d.addObject('App::DocumentObjectGroup','PrimaryTrusses');primary.Label='Primary trusses — top chords, reused bottoms, webs';d.getObject('ProposedStructure').addObject(primary)
 trusses={};top_objects={};new=[];hidden=[];connections=[];panelmeta={};omitted=[]
 color=(.14,.57,.59);webcolor=(.22,.65,.65);amber=(.95,.64,.15)
 def group(name,label,parent):
  g=d.addObject('App::DocumentObjectGroup',name);g.Label=label;parent.addObject(g);return g
 def record(o,ident,role,stage='permanent_roof_first',notes='',section='2x2 solid visualization placeholder'):
  for p,v in [('MemberID',ident),('Stage',stage),('SourceNotes',notes)]:
   o.addProperty('App::PropertyString',p,'Frame');setattr(o,p,v)
  o.Label=ident+' — '+role;o.ViewObject.ShapeColor=amber if 'future' in stage else (color if 'chord' in role else webcolor);o.ViewObject.Visibility=True
  register.append({'id':ident,'object':o.Name,'role':role,'stage':stage,'status':'modeled_placeholder','section':section,'notes':notes})
  new.append(o);return o
 def extrude_polygon(name,points,direction,length,parent,expr=None):
  vv=[A.Vector(*(q*I for q in p)) for p in points]
  origin=vv[0];ex=vv[1]-origin;ex.normalize();normal=ex.cross(vv[2]-origin);normal.normalize();ey=normal.cross(ex);ey.normalize()
  rotation=A.Rotation(ex,ey,normal,'ZXY');inv=rotation.inverted()
  sk=d.addObject('Sketcher::SketchObject',name+'Profile');parent.addObject(sk);sk.Label=name+' — editable closed profile'
  sk.Placement=A.Placement(origin,rotation)
  pp=[inv.multVec(v-origin) for v in vv]
  for p,q in zip(pp,pp[1:]+pp[:1]):
   assert (p-q).Length>1e-6
   sk.addGeometry(Part.LineSegment(A.Vector(p.x,p.y,0),A.Vector(q.x,q.y,0)),False)
  o=d.addObject('Part::Extrusion',name);parent.addObject(o);o.Base=sk;o.DirMode='Custom';o.Dir=A.Vector(*direction);o.LengthFwd=length*I;o.Solid=True
  if expr:o.setExpression('LengthFwd',expr)
  hidden.append(sk);return o
 def box(name,pos,size,parent):
  o=d.addObject('Part::Box',name);parent.addObject(o);o.Length=size[0]*I;o.Width=size[1]*I;o.Height=size[2]*I;o.Placement.Base=A.Vector(*(v*I for v in pos));return o
 br=inp['main_break_y'];cs=inp['cap_south_y'];half=(271-cs)/2;slope=18/half
 planes=[(slope,0,227.25+40*slope),(-slope,0,227.25+257.5*slope),(0,slope,227.25-cs*slope),(0,-slope,227.25+271*slope),(0,0,245.25)]
 def cap(x,y):return min(a*x+b*y+c for a,b,c in planes)
 def roofz(x,y):return 120+(y+63)*math.tan(math.pi/6) if y<=br+1e-9 else cap(x,y)
 def rect(x0,x1,y0,y1):return [(x0,y0),(x1,y0),(x1,y1),(x0,y1)]
 def clip(poly,a,b,c):
  out=[]
  if not poly:return out
  for p,q in zip(poly,poly[1:]+poly[:1]):
   fp=a*p[0]+b*p[1]+c;fq=a*q[0]+b*q[1]+c
   if fp<=1e-9:out.append(p)
   if (fp< -1e-9 and fq>1e-9) or (fp>1e-9 and fq< -1e-9):
    t=fp/(fp-fq);out.append((p[0]+t*(q[0]-p[0]),p[1]+t*(q[1]-p[1])))
  clean=[]
  for p in out:
   if not clean or math.dist(p,clean[-1])>1e-7:clean.append(p)
  if len(clean)>1 and math.dist(clean[0],clean[-1])<1e-7:clean.pop()
  return clean
 def area(poly):return abs(sum(p[0]*q[1]-q[0]*p[1] for p,q in zip(poly,poly[1:]+poly[:1])))/2 if len(poly)>2 else 0
 specs={'TS':('T-S','x',0,-32,224.25,'ProposedTS',118), 'T1':('T1','x',69.75,-32,224.25,'ProposedT1Upper',153.143248),'TW':('T-W','y',-32,-63,253,'ProposedTW',118),'TE':('T-E','y',224.25,-63,253,'ProposedTE',118),'TN':('T-N','x',249,-32,249.5,'ProposedTN',118)}
 def xyz(k,u,z,cross=0):
  _,axis,fixed,*_=specs[k];return (u,fixed+cross,z) if axis=='x' else (fixed+cross,u,z)
 def rz(k,u):
  p=xyz(k,u,0);return roofz(p[0],p[1])
 for k,(label,axis,fixed,start,end,bottom,zbase) in specs.items():
  g=group('Truss'+k,label+' — primary frame',primary);trusses[k]=g
  d.getObject('ProposedChords').removeObject(d.getObject(bottom));g.addObject(d.getObject(bottom))
  for rec in register:
   if rec['object']==bottom:rec['notes']='Original revision003 native bottom reused unchanged in '+label+'; no duplicated bottom.'
  parts=group('TopProfiles'+k,'Editable roof-following top chord profiles',g);patches=[]
  regions=[]
  if axis=='x':
   regions.append((rect(start,end,fixed-3,fixed+3),'main' if fixed+3<=br else 'cap'))
  else:
   regions.extend([(rect(fixed-3,fixed+3,start,br),'main'),(rect(fixed-3,fixed+3,br,end),'cap')])
  patch_records=[]
  for poly,zone in regions:
   pplanes=[(0,math.tan(math.pi/6),120+63*math.tan(math.pi/6))] if zone=='main' else planes
   for i,pl in enumerate(pplanes):
    cellpoly=poly[:]
    for other in pplanes:
     if other==pl:continue
     cellpoly=clip(cellpoly,pl[0]-other[0],pl[1]-other[1],pl[2]-other[2])
    if area(cellpoly)<1e-7:continue
    pts=[(x,y,pl[0]*x+pl[1]*y+pl[2]) for x,y in cellpoly]
    o=extrude_polygon('Top'+k+'Patch'+str(len(patches)+1),pts,(0,0,-1),6,parts,'FullFrameParameters.TopDepth');patches.append(o)
    patch_records.append({'zone':zone,'plane_z_ax_by_c':pl,'plan_vertices_inches':cellpoly})
  if len(patches)==1:
   top=patches[0];parts.removeObject(top);g.addObject(top)
  else:
   top=d.addObject('Part::MultiFuse','TopChord'+k);g.addObject(top);top.Shapes=patches;top.Refine=True;hidden.extend(patches)
  record(top,label+' top','top_chord',notes='Native planar Sketcher patches extruded vertically down 6 inches and fused. Top faces coincide with unchanged roof planes across full width. Main/cap step retained.',section='6-inch width, 6-inch VERTICAL depth placeholder')
  top_objects[k]=top;panelmeta[k]={'top_surface_patches':patch_records,'bottom_object':bottom,'axis':axis,'fixed_coordinate_inches':fixed,'span_inches':[start,end]}
 d.recompute()
 progress('Native roof-following top chords created for all five trusses. Adding webs, opening headers, and future hangers.')
 counts={k:0 for k in specs}
 def web(k,poly,role,targets,notes=''):
  counts[k]+=1;name='Frame'+k+'Web'+str(counts[k]);pts=[xyz(k,u,z,-1) for u,z in poly];axis=specs[k][1]
  o=extrude_polygon(name,pts,(0,1,0) if axis=='x' else (1,0,0),2,trusses[k],'FullFrameParameters.WebWidth')
  record(o,specs[k][0]+' '+role+' '+str(counts[k]),role,notes=notes)
  for target in targets:connections.append((o.Name,target))
  return o
 def vertical(k,u,zlow=None,zhi=None,targets=None):
  if zlow is None:zlow=specs[k][-1]-.5
  if zhi is None:zhi=min(rz(k,u-1),rz(k,u+1))-5
  if zhi<=zlow+1e-6:
   omitted.append({'truss':k,'station_inches':u,'reason':'Top and bottom chords overlap at shallow south end; no zero-length web.'});return
  if targets is None:targets=[specs[k][-2],top_objects[k].Name]
  return web(k,[(u-1,zlow),(u+1,zlow),(u+1,zhi),(u-1,zhi)],'vertical',targets,'2x2 solid; schematic chord embed, connection design unresolved.')
 def diagonal(k,u0,z0,u1,z1,targets=None):
  length=math.hypot(u1-u0,z1-z0);nx=-(z1-z0)/length;nz=(u1-u0)/length
  if targets is None:targets=[specs[k][-2],top_objects[k].Name]
  return web(k,[(u0+nx,z0+nz),(u0-nx,z0-nz),(u1-nx,z1-nz),(u1+nx,z1+nz)],'diagonal',targets,'2x2 solid, ends embedded schematically into chords; no connection design.')
 for k,num in [('TS',6),('T1',4)]:
  a,b=specs[k][3:5];nodes=[a+(b-a)*i/num for i in range(num+1)];panelmeta[k]['panel_stations_inches']=nodes
  adjusted=[max(a+1,min(b-1,u)) for u in nodes]
  for u in adjusted:vertical(k,u)
  for i,(u,v) in enumerate(zip(adjusted,adjusted[1:])):
   zlow=specs[k][-1]-3
   if i%2==0:diagonal(k,u,zlow,v,rz(k,v)-3)
   else:diagonal(k,u,rz(k,u)-3,v,zlow)
 # Longitudinal top profiles have exact hip kinks plus requested roof/panel stations.
 for k in ['TW','TE']:
  x=specs[k][2];dist=min(x+40,257.5-x,half)
  requested=sorted(set([-63,0,69.75,br,185,inp['cap_ridge_y'],253,cs+dist,271-dist]))
  panelmeta[k]['roof_and_panel_stations_inches']=requested
  nodes=[-62,-21,0,69.75,br,185,247,252] if k=='TW' else [-62,-21,0,69.75,br,cs+dist,185,inp['cap_ridge_y'],271-dist,252]
  nodes=sorted(set(u for u in nodes if -63<=u<=253));panelmeta[k]['web_stations_inches']=nodes
  for u in nodes:vertical(k,u)
  # End diagonals and selected clear bays only; middle rectangular bays remain connection-dependent.
  diagonal(k,-61,115,-21,rz(k,-21)-3)
  diagonal(k,0,115,69.75,rz(k,69.75)-3)
  diagonal(k,69.75,rz(k,69.75)-3,br-1,115)
  if k=='TE':diagonal(k,185,115,251,rz(k,251)-3)
  else:
   header=box('TWBalconyHeader',xyz(k,186,204,-3),(6,60,6),trusses[k]);record(header,'T-W balcony header','header',notes='Approximate historical opening y186..246, z120..204; header above clear opening.',section='6x6 placeholder');header.setExpression('Height','FullFrameParameters.HeaderDepth')
   connections.extend([(header.Name,'FrameTWWeb6'),(header.Name,'FrameTWWeb7')]) if False else None
   for u in [187,inp['cap_ridge_y'],216,245]:vertical(k,u,209.5,None,[header.Name,top_objects[k].Name])
   diagonal(k,187,207,216,rz(k,216)-3,[header.Name,top_objects[k].Name]);diagonal(k,216,rz(k,216)-3,245,207,[header.Name,top_objects[k].Name])
   panelmeta[k]['opening']=inp['TW_opening'];panelmeta[k]['header_object']=header.Name
 # TN: use existing west ground column as west jamb. East jamb begins above floor only.
 k='TN';g=trusses[k]
 east=box('TNUpperEastJamb',(152.25,246,120),(6,6,min(cap(152.25,246),cap(158.25,252))-5-120),g)
 record(east,'T-N upper east jamb','upper_jamb',notes='Above-floor jamb only: x152.25..158.25, starts z120. U-E ground post removed. West jamb uses existing N1/U-W.',section='6x6 solid placeholder');connections.append((east.Name,top_objects[k].Name))
 header=box('TNLoadingHeader',(56.25,246,204),(96,6,6),g);header.setExpression('Height','FullFrameParameters.HeaderDepth')
 record(header,'T-N loading header','header',notes='96-inch opening x56.25..152.25, clear z120..204; header bottom204 top210.',section='6x6 solid placeholder');connections.extend([(header.Name,'ProposedNorthPostUW'),(header.Name,east.Name)])
 for u in [-31,0,180,224.25,248.5]:vertical(k,u)
 diagonal(k,-31,115,0,rz(k,0)-3);diagonal(k,1,115,49,rz(k,49)-3)
 diagonal(k,160,rz(k,160)-3,224.25,115);diagonal(k,224.25,rz(k,224.25)-3,248.5,115)
 for u in [57.25,80.25,104.25,128.25,151.25]:vertical(k,u,209.5,None,[header.Name,top_objects[k].Name])
 hnodes=[57.25,80.25,104.25,128.25,151.25]
 for i,(u,v) in enumerate(zip(hnodes,hnodes[1:])):
  diagonal(k,u,207 if i%2==0 else rz(k,u)-3,v,rz(k,v)-3 if i%2==0 else 207,[header.Name,top_objects[k].Name])
 panelmeta[k].update(opening=inp['TN_opening'],west_jamb_reused='ProposedNorthPostUW',east_jamb=east.Name,header_object=header.Name,header_band_nodes_inches=hnodes)
 future=d.getObject('FutureLoftMembers');future.ViewObject.Visibility=True;future.Label='Future loft beams and T1 hangers — visible amber; stage after existing roof removal'
 for n in ['ProposedT1Future','ProposedB2Future']:d.getObject(n).ViewObject.Visibility=True;d.getObject(n).ViewObject.ShapeColor=amber
 for i,x in enumerate(panelmeta['T1']['panel_stations_inches']):
  o=box('FutureT1Hanger'+str(i+1),(x-1,68.75,120),(2,2,147.143248-120),future)
  o.setExpression('Height','FullFrameParameters.HangerTop-FullFrameParameters.HangerBottom');o.setExpression('Placement.Base.z','FullFrameParameters.HangerBottom')
  record(o,'T1 future hanger '+str(i+1),'hanger','future_after_existing_roof_removal','Suspension hanger at T1 panel point; beam top120 to permanent bottom147.143248. Connections unresolved.')
  connections.extend([(o.Name,'ProposedT1Future'),(o.Name,'ProposedT1Upper')])
 for n in ['BelowGradeReference','FloorReference','T1EnvelopeReference']:d.getObject(n).ViewObject.Visibility=False
 for o in hidden:o.ViewObject.Visibility=False
 for r in register:d.getObject(r['object']).ViewObject.Visibility=True
 for o in hidden:o.ViewObject.Visibility=False
 d.recompute()
 # Exact contact checks and geometry preservation, including all original proposed retained solids.
 def check_preserved():
  for n,prior in {**oldshapes,**preserved}.items():
   now=shape(d.getObject(n));assert close(now.Volume,prior.Volume),(n,'volume changed')
   assert now.cut(prior).Volume<1e-4 and prior.cut(now).Volume<1e-4,(n,'shape changed')
  for n,t in oldtypes.items():assert d.getObject(n).TypeId==t
  for n,prior in roof_shapes.items():
   now=shape(d.getObject(n));assert close(now.Length,prior.Length) and now.distToShape(prior)[0]<1e-5,(n,'roof reference changed')
 def validate():
  global top_face_checks
  top_face_checks=[]
  check_preserved();out=[]
  for r in register:
   o=d.getObject(r['object']);ss=shape(o);assert ss.isValid() and ss.Volume>1e-4 and len(ss.Solids)==1,(o.Name,'invalid',len(ss.Solids))
   out.append({'name':o.Name,'valid':True,'solids':1,'volume_mm3':ss.Volume,'bounds_mm':bbox(ss),'native_type':o.TypeId,'visible':bool(o.ViewObject.Visibility)})
  for r in register:
   if r['role']!='top_chord':continue
   for face in shape(d.getObject(r['object'])).Faces:
    if face.normalAt(0,0).z<=0.1:continue
    p=face.CenterOfMass;expected=roofz(p.x/I,p.y/I)*I;error=abs(p.z-expected)
    assert error<1e-5,(r['object'],'top face off roof',error)
    top_face_checks.append({'object':r['object'],'top_face_center_mm':[p.x,p.y,p.z],'roof_error_mm':error})
  for n in removed:assert d.getObject(n) is None
  for n in ['ProposedTW','ProposedTE']:assert close(shape(d.getObject(n)).BoundBox.ZMin,112*I) and close(shape(d.getObject(n)).BoundBox.ZMax,118*I)
  assert d.getObject('FutureLoftMembers').ViewObject.Visibility
  return out
 checks=validate();contacts=[]
 for a,b in connections:
  distance=shape(d.getObject(a)).distToShape(shape(d.getObject(b)))[0]
  contacts.append({'a':a,'b':b,'distance_mm':distance,'touches_or_overlaps':distance<1e-5})
  assert distance<1e-5,(a,b,'not connected',distance)
 # All new members must belong to a connected solid graph rooted in retained lower chords/columns/beams.
 established=[shape(d.getObject(n)) for n in preserved];pending=list(new);graph=[]
 while pending:
  progressed=False
  for o in pending[:]:
   ss=shape(o)
   if any(ss.distToShape(base)[0]<1e-5 for base in established):
    established.append(ss);pending.remove(o);graph.append(o.Name);progressed=True
  assert progressed,('Disconnected new members',[o.Name for o in pending])
 tn_open=Part.makeBox(96*I,6*I,84*I,A.Vector(56.25*I,246*I,120*I))
 tw_open=Part.makeBox(6*I,60*I,84*I,A.Vector(-35*I,186*I,120*I))
 opening_checks=[]
 for label,opening in [('TN_loading',tn_open),('TW_balcony_approximate',tw_open)]:
  hits=[]
  for o in new:
   vol=shape(o).common(opening).Volume
   if vol>1e-4:hits.append({'object':o.Name,'volume_mm3':vol})
  opening_checks.append({'opening':label,'new_solid_intersections':hits,'clear':not hits});assert not hits,(label,hits)
 # New members at floor/roof elevations only; no new ground column introduced.
 assert all(shape(o).BoundBox.ZMin>=112*I-1e-5 for o in new)
 progress('Native solids and opening clearances passed initial validation; computing exact intersections with the existing garage.')
 framing=[m['output'] for m in rv['member_layout']];categories={'existing_roof_framing':framing,'existing_soffit_fascia':[n for n in roof if n not in framing],'existing_walls_and_stucco':walls,'existing_lofts':lofts}
 pairs=[];members=[]
 def overlap(a,b):return all(min(a[k+3],b[k+3])-max(a[k],b[k])>1e-7 for k in range(3))
 for r in register:
  ss=shape(d.getObject(r['object']));bb=bbox(ss);totals={cat:0.0 for cat in categories};hits=0
  for cat,names in categories.items():
   for n in names:
    old=oldshapes[n]
    if not overlap(bb,bbox(old)):continue
    v=ss.common(old).Volume
    if v>1e-4:
     pairs.append({'proposed_id':r['id'],'proposed_object':r['object'],'stage':r['stage'],'existing_object':n,'category':cat,'intersection_mm3':v,'intersection_in3':v/I**3});totals[cat]+=v;hits+=1
  r['collision_pair_count']=hits;r['pairwise_intersection_totals_mm3']=totals
  members.append({'id':r['id'],'stage':r['stage'],'pair_count':hits,'pairwise_volume_totals_mm3':totals,'through_wall_interference':r['role'] in ['column','concept'] and totals['existing_walls_and_stucco']>1e-4})
 collision={'request_id':RID,'method':'Exact common solid volumes after bbox broad phase; threshold 1e-4 mm3. Pairwise sums can double-count overlapping existing members.','categories':{k:len(v) for k,v in categories.items()},'pair_count':len(pairs),'pairs':pairs,'members':members,'future_stage_pairs':[p for p in pairs if p['stage']=='future_after_existing_roof_removal'],'column_wall_interferences':[m for m in members if m['through_wall_interference']],'feasibility_claim':False,'not_tested':['Existing roof cladding absent','Strength or capacity','Connection design','Temporary stability','Foundation adequacy']}
 put('proposed-overlay-collision-report.json',collision)
 issues=[{'id':'CONCEPT_ONLY','note':'Native geometric correction model. No strength analysis or stability certification was run. All sections remain placeholders.'},{'id':'RECTANGULAR_BAYS','note':'TS and T1 diagonals triangulate all panels; longitudinal members include verticals and selected diagonals with rectangular bays. Those bays are NOT represented as stable pin-jointed trusses; frame action and all connections are unresolved.'},{'id':'ROOF_SEAM','note':'Unchanged roof reference has a small height step at main/cap break y122.7624491117621. Top-chord native roof-plane patches preserve that step and overlap vertically at the seam. Fabricated transition/joint detail unresolved.'},{'id':'TOP_DEPTH','note':'Top chords use 6-inch VERTICAL depth (not normal-to-slope section depth), full width6. Exact roof faces maintained; visual sections unverified.'},{'id':'OPENINGS','note':'TN clear x56.25..152.25 z120..204. TW historic approximate opening y186..246 z120..204 retained. No new solids inside either clear volume.'},{'id':'WEST_JAMB','note':'Consolidated N1/U-W retained unchanged and used as TN west jamb; it overlaps TN across 2.5 inches in y. No second west jamb. East upper jamb begins120, two inches above chord top118 per requested opening-floor reference.'},{'id':'FUTURE_STAGE','note':'T1 future beam, B2 and five hangers visible amber but remain after-existing-roof-removal stage. Exact existing collisions reported.'},{'id':'CONNECTIONS','note':'Webs embed schematically into chord/header solids to guarantee geometric joins. No gussets, bolts, welds, joint stiffness or fabrication details designed.'}]
 d.addObject('App::DocumentObjectGroup','FullFrameNotes');notes=d.getObject('FullFrameNotes');dims.addObject(notes)
 for issue in issues:
  o=d.addObject('App::DocumentObject','Note'+issue['id'].replace('_',''));notes.addObject(o);o.Label=issue['id'];o.addProperty('App::PropertyString','Explanation');o.Explanation=issue['note']
 rot=A.Rotation(.4247082002778669,.1759198966061612,.3398511429799874,.8204732385702833);center=A.Vector(111.25*I,102.5*I,110*I);pos=center+rot.multVec(A.Vector(0,0,22000));axis=rot.Axis
 G.activeDocument().activeView().setCamera(f'#Inventor V2.1 ascii\nOrthographicCamera {{ position {pos.x} {pos.y} {pos.z} orientation {axis.x} {axis.y} {axis.z} {rot.Angle} nearDistance 100 farDistance 44000 focalDistance 22000 height 16000 }}')
 d.recompute();d.saveAs(str(ROOT/'Proposed-Garage.FCStd'));A.closeDocument(d.Name)
 d=A.openDocument(str(ROOT/'Proposed-Garage.FCStd'));A.setActiveDocument(d.Name);checks=validate()
 assert sha(ROOT/'Existing-Garage.FCStd')==existing_hash
 def mesh(objects,wireobjs=[]):
  out={'units':'mm','objects':[]}
  for o in objects:
   vs,ts=shape(o).tessellate(.5);out['objects'].append({'name':o.Name,'label':o.Label,'color':list(o.ViewObject.ShapeColor),'vertices':[[v.x,v.y,v.z] for v in vs],'triangles':[list(t) for t in ts]})
  for o in wireobjs:
   if not o.ViewObject.Visibility:continue
   lines=[]
   for e in o.Shape.Edges:
    ps=e.discretize(Number=65) if o.TypeId=='Part::Circle' else [e.Vertexes[0].Point,e.Vertexes[-1].Point];lines.append([[p.x,p.y,p.z] for p in ps])
   out['objects'].append({'name':o.Name,'label':o.Label,'color':list(o.ViewObject.LineColor),'vertices':[],'triangles':[],'lines':lines})
  return out
 objects=[d.getObject(r['object']) for r in register];oldobjects=[d.getObject(n) for n in oldnames];wires=[d.getObject(n) for n in wire_names]
 put('proposed-overlay-full.json',mesh(oldobjects+objects,wires));put('proposed-overlay-new.json',mesh(objects,wires));put('proposed-overlay-future.json',mesh([d.getObject(r['object']) for r in register if r['stage']=='future_after_existing_roof_removal']));put('proposed-overlay-optional-north.json',{'units':'mm','objects':[]})
 progress('Saved and reopened native FCStd successfully. Exporting STEP and final metadata.')
 Part.makeCompound([shape(o) for o in oldobjects+objects]).exportStep(str(ROOT/'Proposed-Garage-overlay.step'))
 step=Part.Shape();step.read(str(ROOT/'Proposed-Garage-overlay.step'));assert step.isValid() and len(step.Solids)==len(oldobjects)+len(objects)
 resolutions=[r for r in regbase['superseded_and_aliases'] if r.get('id') not in ['U-E','NE-W','NE-E']]+[{'id':n,'status':'removed_entirely','note':'Excluded from native model and exports; preserved only in external pre-fullframe backup.'} for n in ['U-E','NE-W','NE-E']]
 regbase.update(request_id=RID,members=register,superseded_and_aliases=resolutions,unresolved=issues,connection_checks=contacts,trusses=panelmeta)
 put('proposed-overlay-member-register.json',regbase)
 params=json.loads((backup/'proposed-overlay-parameters.json').read_text());params.update(request_id=RID,trusses=panelmeta,unresolved=issues,visible_future_members=True,geometry_omissions=['Secondary purlins / roof joists','Roof cladding','Connections','Foundations','Crane and door solids'],removed_ground_posts=['U-E','NE-W','NE-E'])
 params['parameters']['T1UpperTop']={'value':196.64324823492282,'note':'Supersedes prior183.143248; current roof top at T1 centerline.'};params['north_extension'].update(upper_jamb_boxes=[[50.25,56.25,249.5,255.5],[152.25,158.25,246,252]],outer_jamb_boxes=[],outer_row_default_visible=False,east_jamb_bottom=120)
 params['connection_checks']=contacts;params['source_hashes']['reference-layout/old-truss-geometry.py']=sha(ROOT/'reference-layout/old-truss-geometry.py');params['old_layout_usage']='Read only for vertical/end-diagonal pattern inspiration; not executed and old elevations not adopted.'
 put('proposed-overlay-parameters.json',params)
 validation={'request_id':RID,'freecad_version':A.Version(),'existing_sha256_before':existing_hash,'existing_sha256_after':sha(ROOT/'Existing-Garage.FCStd'),'authoritative_existing_unchanged':True,'native_existing_copy_preserved':True,'retained_proposed_solids_preserved':True,'roof_reference_preserved':True,'roof_top_face_checks':top_face_checks,'base_model_sha256':base_hash,'backup_directory':str(backup),'existing_solid_count':107,'new_solid_count':len(new),'proposed_solid_count':len(objects),'default_proposed_solid_count':len(objects),'step_solid_count':len(step.Solids),'native_reopen_success':True,'visible_future_members':True,'removed_ground_posts':removed,'proposed_objects':checks,'connection_checks':contacts,'all_new_members_connected_to_retained_frame':True,'opening_checks':opening_checks,'no_new_ground_post':True,'omitted_shallow_webs':omitted,'collision_pair_count':len(pairs),'strength_analysis_run':False,'all_sizes_unverified':True,'capacity_or_feasibility_claim':False}
 put('proposed-overlay-validation.json',validation)
 readme='# Proposed full primary frame\n\nRequest '+RID+'. Native FreeCAD geometric concept, all sections unverified.\n\n'
 readme+='Five primary trusses reuse their original bottom chords. New roof-following top chords are native Sketcher planar profiles and Part extrusions/fusions. Edit the profile sketches for layout; FullFrameParameters controls top depth and web extrusion width. Rerun full-frame-generator.py with the bundled FreeCAD Python to rebuild from the immutable revision003 backup and full-frame-input.json. The active proposed-overlay-generator.py redirects here. Roof changes require regeneration of the profiles; roof outline and columns retain their original spreadsheet expressions.\n\n'
 readme+='Future T1 floor beam, B2 and five 2x2 hangers are visible amber. U-E and optional NE-W/NE-E ground posts were removed entirely. N2 and consolidated N1/U-W remain. The east TN jamb is only above floor level. No old analysis was run.\n\n'
 readme+='Validation: existing file hash unchanged;107 native existing solids and all retained original proposed shapes preserved; every new solid valid and nonzero; explicit member joins verified; all new members connected to retained frame; both openings tested for zero positive solid intersection; saved FCStd reopened; STEP solid count checked. Collision report uses exact intersections with existing native solids.\n\n'
 readme+='\n'.join('- '+v['note'] for v in issues)+'\n\nMesh schema: millimeters, objects with global vertices/triangles; reference objects use lines as lists of polylines. Full/new meshes include visible future members; future export isolates them. Optional-north export is empty.\n'
 (ROOT/'PROPOSED-OVERLAY-README.md').write_text(readme)
 files=['Proposed-Garage.FCStd','Proposed-Garage-overlay.step','proposed-overlay-full.json','proposed-overlay-new.json','proposed-overlay-future.json','proposed-overlay-optional-north.json','proposed-overlay-parameters.json','proposed-overlay-member-register.json','proposed-overlay-collision-report.json','proposed-overlay-validation.json','PROPOSED-OVERLAY-README.md','full-frame-generator.py','full-frame-input.json','proposed-overlay-generator.py','preview-full-frame.py']
 R.update(status='complete',completed_utc=datetime.now(timezone.utc).isoformat(),artifact_paths=[str(ROOT/n) for n in files],artifact_sha256={n:sha(ROOT/n) for n in files},existing_unchanged=True,native_reopen_success=True,existing_solids=107,proposed_solids=len(objects),new_solids=len(new),step_solids=len(step.Solids),collision_pairs=len(pairs),opening_checks=opening_checks,strength_analysis_run=False,default_future_visible=True,removed_ground_posts=['U-E','NE-W','NE-E'],unresolved=issues)
 put('newframe-result.json',R);put('proposed-overlay-result.json',R);put('proposed-overlay-progress.txt',R);Path('/home/ros/Documents/Codex/2026-09-09/oh/garage-agent-result.json').write_text(json.dumps(R,indent=2)+'\n');progress('COMPLETE: updated Proposed-Garage.FCStd, meshes, STEP and validation written. See newframe-result.json.')
except Exception as e:
 R.update(status='failed',error=str(e),traceback=traceback.format_exc());put('newframe-result.json',R);progress('FAILED: '+str(e)+'; see newframe-result.json.');Path('/home/ros/Documents/Codex/2026-09-09/oh/garage-agent-result.json').write_text(json.dumps(R,indent=2)+'\n')
finally:
 sys.stdout.flush();sys.stderr.flush();os._exit(0 if R.get('status')=='complete' else 1)
