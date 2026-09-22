import os,json,math,sys,csv
from pathlib import Path
os.environ['QT_QPA_PLATFORM']='offscreen'
import FreeCAD as A, Part, FreeCADGui as G
G.showMainWindow()
P=Path(__file__).resolve().parent;ROOT=P.parents[1];U=25.4
src=ROOT/'optimization/exposed-frame/Garage-Exposed-Steel.FCStd'
d=A.openDocument(str(src))
# Retain the old envelope concept, adapting proposed X extent to the current setback row.
for group in ['SolarRoof','HipRoofCap','Truss_TE','Balcony']:
 g=d.getObject(group)
 if g:
  for o in list(g.Group):d.removeObject(o.Name)
  d.removeObject(g.Name)
for o in list(d.Objects):
 if 'Shape' not in o.PropertiesList or o.Shape.isNull():continue
 if any(g.Name=='ExistingGarage' for g in o.InList):continue
 m=A.Matrix();m.A11=(211.5+34)/(249.5+32);m.A14=(-34+32*m.A11)*U
 o.Shape=o.Shape.transformGeometry(m)
 if 'DetailStatus' in o.PropertiesList:o.DetailStatus='Massing revision only; historical frame transformed to setback width, not a structural sizing model'
# Remove former balcony door/glazing and frame pieces; retain the small west window.
for o in list(d.Objects):
 if 'Shape' not in o.PropertiesList or o.Shape.isNull():continue
 if any(g.Name=='DoorsWindows' for g in o.InList) and o.Label.startswith('West ') and o.Shape.BoundBox.YMin/U>=180:
  d.removeObject(o.Name)
# Fill the old west balcony door opening with the same inboard metal wall thickness.
wall=d.addObject('PartDesign::Feature','FormerBalconyWallInfill');wall.Label='West wall infill — balcony removed'
scale=(211.5+34)/(249.5+32);xwall=-34+3.5*scale
wall.Shape=Part.makeBox(2*scale*U,60*U,(206-120.75)*U,A.Vector(xwall*U,186*U,120.75*U))
d.getObject('InteriorMetalPanels').addObject(wall);wall.ViewObject.ShapeColor=(.68,.72,.73)
# Owner correction: one flush new north face, 12 inches beyond existing Y249.
NORTH_FACE=261.0
for o in list(d.Objects):
 if 'Shape' not in o.PropertiesList or o.Shape.isNull():continue
 if any(g.Name=='ExistingGarage' for g in o.InList):continue
 label=o.Label;shape=o.Shape.copy()
 if label.startswith('N inside metal panel') or label.startswith('North '):
  shape.translate(A.Vector(0,12*U,0))
 elif shape.BoundBox.YMax/U>185:
  # Refit the rear context only. End faces of side cladding reach the wall;
  # rear steel centerlines remain just inside it.
  is_side=label.startswith(('W inside metal panel','E inside metal panel'))
  target=261 if is_side else 259
  scale=(target-185)/(253-185)
  # Split at the rear station to retain the southern geometry.
  lower=shape.common(Part.makeBox(2000*U,1185*U,1000*U,A.Vector(-1000*U,-1000*U,-100*U)))
  upper=shape.common(Part.makeBox(2000*U,1000*U,1000*U,A.Vector(-1000*U,185*U,-100*U)))
  if not upper.isNull():
   t=A.Matrix();t.A22=scale;t.A24=185*(1-scale)*U
   upper=upper.transformGeometry(t)
   shape=Part.makeCompound([q for q in [lower,upper] if not q.isNull()])
 shape=shape.common(Part.makeBox(2000*U,1261*U,1000*U,A.Vector(-1000*U,-1000*U,-100*U)))
 if not shape.isNull():o.Shape=shape
colors={'rafter':(.70,.36,.12),'steel':(.19,.23,.25),'roof':(.25,.30,.32),'pv':(.09,.18,.25),'glass':(.30,.69,.80),'trim':(.88,.90,.88)}
groups={};new=[]
def V(p):return A.Vector(*[q*U for q in p])
def panel(name,pts,mat,group,thick=.3):
 face=Part.Face(Part.makePolygon([V(p) for p in pts]+[V(pts[0])]))
 normal=face.normalAt(0,0)
 direction=A.Vector(0,-thick*U,0) if abs(normal.z)<1e-7 else A.Vector(0,0,-thick*U)
 shape=face.extrude(direction)
 assert shape.isValid() and shape.Volume>0,name
 o=d.addObject('PartDesign::Feature','RoofStudy');o.Label=name;o.Shape=shape
 if group not in groups:groups[group]=d.addObject('App::DocumentObjectGroup',group)
 groups[group].addObject(o);o.ViewObject.ShapeColor=colors[mat]
 o.addProperty('App::PropertyString','StudyMaterial');o.StudyMaterial=mat
 if mat=='glass':o.ViewObject.Transparency=35
 new.append(o)
 return o
west=-34;east=211.5;outer=247.5;south=-64;north=NORTH_FACE
# Requested two walls from the orange floor-plan extension route; retain exterior bracing.
plan_basis=json.loads((P/'floor-plan-basis.json').read_text())
plan_posts={p['id']:p for p in plan_basis['columns']}
w3=plan_posts['W3'];wb3=plan_posts['WB3'];w4=plan_posts['W4']
assert w3['x']==w4['x'] and w3['y']==wb3['y']
# Match the existing upper inboard cladding face; 2-inch envelope is illustrative.
wall_x=-34+3.5*((211.5+34)/(249.5+32));wall_t=2*((211.5+34)/(249.5+32))
wall_group=d.addObject('App::DocumentObjectGroup','GroundFloorExtensionWalls')
wall_specs=[('Extension wall W3 to W4',wall_x,w3['y'],0,wall_t,NORTH_FACE-w3['y'],98.5),
            ('Extension wall W3 to WB3',wall_x,w3['y']+2,0,wb3['x']-wall_x,2,98.5)]
for name,x,y,h,dx,dy,dz in wall_specs:
 ob=d.addObject('PartDesign::Feature','ExtensionWall');ob.Label=name
 ob.Shape=Part.makeBox(dx*U,dy*U,dz*U,V((x,y,h)))
 assert ob.Shape.isValid() and ob.Shape.Volume>0
 wall_group.addObject(ob);ob.ViewObject.ShapeColor=(.68,.72,.73)
 ob.addProperty('App::PropertyString','SourceBasis');ob.SourceBasis='Floor-plan orange extension route; W4 end follows later north-face correction Y261. Inboard cladding with retained bracing; thickness/attachments provisional.'
br=122.7624491117621
z=lambda y:128+(y+63)*math.tan(math.pi/6)
# Vertical clerestory replaces inclined top glazing, holding the solar area and cap height.
front=south+3*(br-south)/4
sill=z(front);eave=235.25;fascia_height=4.0;glazing_head=eave-fascia_height
for j in range(3):
 ya=south+j*(br-south)/4;yb=south+(j+1)*(br-south)/4
 for i in range(6):
  xa=west+i*(east-west)/6;xb=west+(i+1)*(east-west)/6
  panel('Solar panel %d-%d'%(i+1,j+1),[(xa+.4,ya+.4,z(ya+.4)),(xb-.4,ya+.4,z(ya+.4)),(xb-.4,yb-.4,z(yb-.4)),(xa+.4,yb-.4,z(yb-.4))],'pv','SolarRoof')
for i in range(6):
 xa=west+i*(east-west)/6;xb=west+(i+1)*(east-west)/6
 panel('Vertical clerestory %d'%(i+1),[(xa+.5,front,sill),(xb-.5,front,sill),(xb-.5,front,glazing_head),(xa+.5,front,glazing_head)],'glass','Clerestory')
for i in range(7):
 x=west+i*(east-west)/6
 panel('Clerestory mullion %d'%i,[(x-.5,front-.15,sill),(x+.5,front-.15,sill),(x+.5,front-.15,glazing_head),(x-.5,front-.15,glazing_head)],'trim','RoofTrim',.8)
for h in [sill,glazing_head-1]:panel('Clerestory horizontal trim',[(west,front-.2,h),(east,front-.2,h),(east,front-.2,h+1),(west,front-.2,h+1)],'trim','RoofTrim',.8)
for x in [west,east-1]:panel('Main slope edge',[(x,south,z(south)),(x+1,south,z(south)),(x+1,front,sill),(x,front,sill)],'trim','RoofTrim',1)
# Close triangular clerestory cheeks against the old rising roof-side profile.
for x in [west,east]:
 pts=[(x,front,sill),(x,front,eave),(x,br,eave)]
 face=Part.Face(Part.makePolygon([V(p) for p in pts]+[V(pts[0])]))
 ob=d.addObject('PartDesign::Feature','ClerestoryCheek');ob.Label='Clerestory side cheek';ob.Shape=face.extrude(A.Vector(.3*U,0,0));ob.ViewObject.ShapeColor=colors['roof']
 ob.addProperty('App::PropertyString','StudyMaterial');ob.StudyMaterial='roof'
# Expand the shallow hip cap forward to meet the vertical glazing; retain eave/ridge elevations.
x0=west-8;x1=east+8;y0=front-4;y1=north+4;ridge=eave+18;ym=(y0+y1)/2;run=(y1-y0)/2;rl=x0+run;rr=x1-run
for label,pts in [('S',[(x0,y0,eave),(x1,y0,eave),(rr,ym,ridge),(rl,ym,ridge)]),('E',[(x1,y0,eave),(x1,y1,eave),(rr,ym,ridge)]),('N',[(x1,y1,eave),(x0,y1,eave),(rl,ym,ridge),(rr,ym,ridge)]),('W',[(x0,y1,eave),(x0,y0,eave),(rl,ym,ridge)])]:panel('Hip cap '+label,pts,'roof','HipRoofCap')
# Continuous white eaves: 4-inch fascia, 4-inch front/rear soffit and 8-inch sides.
def trimbox(name,x,y,z,dx,dy,dz):
 o=d.addObject('PartDesign::Feature','CapTrim');o.Label=name
 o.Shape=Part.makeBox(dx*U,dy*U,dz*U,V((x,y,z)))
 assert o.Shape.isValid() and o.Shape.Volume>0,name
 if 'RoofEaves' not in groups:groups['RoofEaves']=d.addObject('App::DocumentObjectGroup','RoofEaves')
 groups['RoofEaves'].addObject(o);o.ViewObject.ShapeColor=colors['trim']
 o.addProperty('App::PropertyString','StudyMaterial');o.StudyMaterial='trim'
 return o
for name,x,y,dx,dy in [('front',x0,y0,x1-x0,.5),('rear',x0,y1-.5,x1-x0,.5),('west',x0,y0,.5,y1-y0),('east',x1-.5,y0,.5,y1-y0)]:
 trimbox('Cap fascia '+name,x,y,glazing_head,dx,dy,fascia_height)
for name,x,y,dx,dy in [('front',x0,y0,x1-x0,4),('rear',x0,north,x1-x0,4),('west',x0,front,8,north-front),('east',east,front,8,north-front)]:
 trimbox('Cap soffit '+name,x,y,glazing_head,dx,dy,.25)
# Rebuild T-E from the coordinated study; rafter endpoints follow its actual chord axes.
def beam(name,a,b,width,depth,group,mat):
 axis=V(b)-V(a);length=axis.Length;axis.normalize()
 u=A.Vector(0,1,0) if abs(axis.y)<.99 else A.Vector(1,0,0)
 v=axis.cross(u);v.normalize();u=v.cross(axis);u.normalize()
 center=V(a)
 pts=[center+u*(i*width*U/2)+v*(j*depth*U/2) for i,j in [(-1,-1),(1,-1),(1,1),(-1,1)]]
 sh=Part.Face(Part.makePolygon(pts+[pts[0]])).extrude(axis*length)
 assert sh.isValid() and sh.Volume>0,name
 o=d.addObject('PartDesign::Feature','StudyBeam');o.Label=name;o.Shape=sh
 if group not in groups:groups[group]=d.addObject('App::DocumentObjectGroup',group)
 groups[group].addObject(o);o.ViewObject.ShapeColor=colors[mat]
 o.addProperty('App::PropertyString','StudyMaterial');o.StudyMaterial=mat
 return o
# West-elevation owner markup: remove obsolete balcony header/jamb and replace web layout.
removed_west=['T-W balcony header','T-W vertical 13','T-W diagonal 15','T-W diagonal 16',
              'T-W vertical 6','T-W vertical 3','T-W vertical 4','T-W diagonal 9','T-W diagonal 10']
for o in list(d.Objects):
 if any(o.Label==name or o.Label.startswith(name+' |') for name in removed_west):d.removeObject(o.Name)
# Clip historical posts to chord undersides, including far-side posts visible in elevation.
m=math.tan(math.pi/6);break_y=br
slope_under=lambda y:117+(y+63)*m-1.25/math.cos(math.pi/6)
# Two half-space solids follow the sloping and horizontal chord bottom faces.
def yz_prism(points):
 face=Part.Face(Part.makePolygon([V((-1000,y,h)) for y,h in points]+[V((-1000,*points[0]))]))
 return face.extrude(A.Vector(2000*U,0,0))
slope_clip=yz_prism([(-100,-100),(break_y,-100),(break_y,slope_under(break_y)),(-100,slope_under(-100))])
flat_clip=yz_prism([(break_y,-100),(400,-100),(400,221.75),(break_y,221.75)])
clip=Part.makeCompound([slope_clip,flat_clip])
trimmed_posts=[]
for o in d.Objects:
 if 'Shape' not in o.PropertiesList or o.Shape.isNull():continue
 if any(g.Name=='Columns' for g in o.InList):
  o.Shape=o.Shape.common(clip);trimmed_posts.append(o.Label)
# New X in the entire former balcony bay, endpoints fitted inside the chords.
for name,a,b in [('West upper X brace A',[-34,185,116.75],[-34,259,221.75]),
                 ('West upper X brace B',[-34,259,116.75],[-34,185,221.75])]:
 ob=beam(name,a,b,2.25,2.25,'WestMarkupFraming','steel')
 ob.Shape=ob.Shape.common(Part.makeBox(100*U,74*U,105*U,V((-80,185,116.75))))
beam('West clerestory-aligned vertical',[-34,front,116.75],[-34,front,glazing_head],1.5,1.5,'WestMarkupFraming','steel')
# Move the connected diagonal apex with the vertical, retaining the other end stations.
meet=117+(front+63)*m
beam('West revised diagonal south',[-34,0,115],[-34,front,meet],2.25,2.25,'WestMarkupFraming','steel')
beam('West revised diagonal north',[-34,front,meet],[-34,br-1,115],1.5,1.5,'WestMarkupFraming','steel')
markup_record={'removed_members':removed_west,'added_upper_bay_x':True,'clerestory_vertical_y':front,
 'clerestory_vertical_top_z':glazing_head,'trimmed_posts':trimmed_posts,
 'note':'Sketch-directed geometry; sizes provisional; X crossing and joints not detailed. Flush solar-plane chord revision remains separate.'}
(P/'west-markup-revision.json').write_text(json.dumps(markup_record,indent=2))
with (P/'coordinated-truss-members.csv').open() as f:te=[r for r in csv.DictReader(f) if r['assembly']=='T-E']
for r in te:
 for k in ('y1','y2'):
  if float(r[k])>185:r[k]=str(185+(float(r[k])-185)*(NORTH_FACE-185)/(269-185))
 beam(r['id'],[float(r[k]) for k in ('x1','y1','z1')],[float(r[k]) for k in ('x2','y2','z2')],float(r['width_in']),float(r['depth_in']),'CoordinatedTE','steel')
top=[r for r in te if '.top.' in r['id']]
def chord(y):
 for r in top:
  a,b=float(r['y1']),float(r['y2'])
  if a-1e-7<=y<=b+1e-7:
   return float(r['z1'])+(y-a)/(b-a)*(float(r['z2'])-float(r['z1']))
 raise ValueError('No T-E chord at station '+str(y))
beam('E-OB', [outer,-4,100],[outer,253,100],3,3,'EastSupportFrame','steel')
for label,y in [('E-S',-2),('E-N',251)]:beam(label,[outer,y,0],[outer,y,98.5],4,4,'EastSupportFrame','steel')
beam('E-M option B',[246.5,185,0],[246.5,185,98.5],4,4,'EastSupportFrame','steel')
# Twelve illustrative rafters: eleven equal 23-inch bays between E-S and E-N.
stations=[-2+23*i for i in range(12)];rows=[]
for i,y in enumerate(stations):
 a=[outer,y,100];b=[east,y,chord(y)]
 beam('East rafter %02d'%(i+1),a,b,3,3,'EastRoofRafters','rafter')
 rows.append(dict(id='ER-%02d'%(i+1),y=y,x1=a[0],z1=a[2],x2=b[0],z2=b[2],spacing_in=23))
# Roof follows the ruled surface defined by the rafter family, with short faceted strips.
# Offset outward above the 3-inch rafter display envelope, rather than making a giant diagonal fold.
ys=sorted(set([-3.5,252.5]+stations+[float(r['y1']) for r in top if -2<float(r['y1'])<251]))
def roofpoint(y,t):
 dz=chord(max(-2,min(251,y)))-100;run=outer-east;norm=math.hypot(dz,run)
 return (outer-t*run+2.5*dz/norm,y,100+t*dz+2.5*run/norm)
for i,(ya,yb) in enumerate(zip(ys,ys[1:])):
 for j in range(4):
  p0,p1,p2,p3=roofpoint(ya,j/4),roofpoint(ya,(j+1)/4),roofpoint(yb,(j+1)/4),roofpoint(yb,j/4)
  for k,tri in enumerate([(p0,p1,p2),(p0,p2,p3)]):panel('East metal cladding %d-%d-%d'%(i,j,k),list(tri),'roof','EastSetbackRoof',.08)
with (P/'east-roof-rafters.csv').open('w') as f:
 w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
assert all(abs(rows[i+1]['y']-rows[i]['y']-23)<1e-8 for i in range(11))
# Replace old notes with explicit draft limits.
old=d.getObject('ModelNotes')
if old:d.removeObject(old.Name)
notes=d.addObject('App::FeaturePython','RoofStudyNotes');notes.addProperty('App::PropertyString','Basis');notes.Basis='2026-09-15 rough massing study. Old exposed-frame model adapted to upper east X211.5 / lower east beam X247.5. North face flush at Y261, 12 inches north of existing wall; vertical clerestory at solar top; hip cap extended forward at unchanged eave height; four-inch fascia, four-inch front/rear and eight-inch side soffits. T-E and east roof rafters use coordinated chord endpoints; remaining historical steel is context only, not an engineering model.'
for o in d.Objects:
 if 'Shape' in o.PropertiesList and not o.Shape.isNull() and not any(g.Name in ('ExistingGarage','HipRoofCap','RoofEaves') for g in o.InList) and o.Shape.BoundBox.YMax>261*U+1e-5:
  o.Shape=o.Shape.common(Part.makeBox(2000*U,1261*U,1000*U,A.Vector(-1000*U,-1000*U,-100*U)))
d.recompute();G.activeDocument().activeView().viewAxonometric();G.activeDocument().activeView().fitAll()
d.saveAs(str(P/'garage-east-clerestory.FCStd'))
objects=[];export=[]
for o in d.Objects:
 if 'Shape' not in o.PropertiesList or o.Shape.isNull():continue
 assert o.Shape.isValid(),o.Label
 export.append(o);vs,ts=o.Shape.tessellate(2)
 mat=o.StudyMaterial if 'StudyMaterial' in o.PropertiesList else ('stucco' if any(g.Name=='ExistingGarage' for g in o.InList) else 'steel' if any(g.Name.startswith(('Truss','Columns','Bracing')) for g in o.InList) else 'panel')
 objects.append(dict(name=o.Label,group=next((g.Name for g in o.InList if g.TypeId=='App::DocumentObjectGroup'),'Context'),material=mat,vertices=[[v.x/U,v.y/U,v.z/U] for v in vs],triangles=ts))
Part.export(export,str(P/'garage-east-clerestory.step'))
(P/'cad-mesh.json').write_text(json.dumps({'objects':objects,'units':'inches'}))
(P/'validation.json').write_text(json.dumps({'west_markup':markup_record,'extension_walls':['W3-W4','W3-WB3'],'extension_wall_height_in':98.5,'extension_source_north_y':w4['y'],'extension_current_north_face_y':NORTH_FACE,'balcony_removed':True,'former_balcony_opening':'matching west wall infill','north_face_y_in':NORTH_FACE,'existing_north_face_y_in':249,'north_offset_in':12,'valid_shapes':len(objects),'vertical_clerestory_panes':6,'clerestory_height_in':glazing_head-sill,'fascia_height_in':4,'soffit_depths_in':{'front':4,'rear':4,'west':8,'east':8},'cap_north_edge_y_in':north+4,'cap_forward_extension_in':br-front,'pv_panels':18,'east_rafters':12,'rafter_spacing_in':23,'rafter_endpoint_checks':'12 lower endpoints on E-OB axis; 12 upper endpoints interpolated on coordinated T-E top chord','upper_east_x':east,'east_beam_x':outer,'status':'rough massing; not structural analysis'},indent=2))
print('CAD COMPLETE',len(objects),flush=True)
