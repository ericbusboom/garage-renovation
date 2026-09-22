import os,json,math,sys,csv
from pathlib import Path
os.environ['QT_QPA_PLATFORM']='offscreen'
import FreeCAD as A, Part, FreeCADGui as G
G.showMainWindow()
P=Path(__file__).resolve().parent;ROOT=P.parents[1];U=25.4
src=ROOT/'optimization/exposed-frame/Garage-Exposed-Steel.FCStd'
d=A.openDocument(str(src))
# Retain the old envelope concept, adapting proposed X extent to the current setback row.
for group in ['SolarRoof','HipRoofCap','Truss_TE']:
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
colors={'rafter':(.70,.36,.12),'steel':(.19,.23,.25),'roof':(.25,.30,.32),'pv':(.09,.18,.25),'glass':(.30,.69,.80),'trim':(.88,.90,.88)}
groups={};new=[]
def V(p):return A.Vector(*[q*U for q in p])
def panel(name,pts,mat,group,thick=.3):
 shape=Part.Face(Part.makePolygon([V(p) for p in pts]+[V(pts[0])])).extrude(A.Vector(0,0,-thick*U))
 assert shape.isValid() and shape.Volume>0,name
 o=d.addObject('PartDesign::Feature','RoofStudy');o.Label=name;o.Shape=shape
 if group not in groups:groups[group]=d.addObject('App::DocumentObjectGroup',group)
 groups[group].addObject(o);o.ViewObject.ShapeColor=colors[mat]
 o.addProperty('App::PropertyString','StudyMaterial');o.StudyMaterial=mat
 if mat=='glass':o.ViewObject.Transparency=35
 new.append(o)
 return o
west=-34;east=211.5;outer=247.5;south=-64;north=269
br=122.7624491117621
z=lambda y:128+(y+63)*math.tan(math.pi/6)
# Three PV rows and one glazed upper row, with no opaque roof skin behind skylights.
for j in range(4):
 ya=south+j*(br-south)/4;yb=south+(j+1)*(br-south)/4
 for i in range(6):
  xa=west+i*(east-west)/6;xb=west+(i+1)*(east-west)/6
  pts=[(xa+.4,ya+.4,z(ya+.4)),(xb-.4,ya+.4,z(ya+.4)),(xb-.4,yb-.4,z(yb-.4)),(xa+.4,yb-.4,z(yb-.4))]
  panel(('Skylight' if j==3 else 'Solar panel')+f' {i+1}-{j+1}',pts,'glass' if j==3 else 'pv','Skylights' if j==3 else 'SolarRoof')
# Thin perimeter strips make the opening edges clear in the rough model.
for x in [west,east-1]:panel('Main slope edge',[(x,south,z(south)),(x+1,south,z(south)),(x+1,br,z(br)),(x,br,z(br))],'trim','RoofTrim',1)
for y in [south, south+3*(br-south)/4, br-1]:panel('Roof row boundary',[(west,y,z(y)),(east,y,z(y)),(east,y+1,z(y+1)),(west,y+1,z(y+1))],'trim','RoofTrim',1)
# Hip cap retained as a shallow four-sided cap above rear plateau.
x0=west-8;x1=east+8;y0=br;y1=north+2;eave=235.25;ridge=eave+18;ym=(y0+y1)/2;run=(y1-y0)/2;rl=x0+run;rr=x1-run
for label,pts in [('S',[(x0,y0,eave),(x1,y0,eave),(rr,ym,ridge),(rl,ym,ridge)]),('E',[(x1,y0,eave),(x1,y1,eave),(rr,ym,ridge)]),('N',[(x1,y1,eave),(x0,y1,eave),(rl,ym,ridge),(rr,ym,ridge)]),('W',[(x0,y1,eave),(x0,y0,eave),(rl,ym,ridge)])]:panel('Hip cap '+label,pts,'roof','HipRoofCap')
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
with (P/'coordinated-truss-members.csv').open() as f:te=[r for r in csv.DictReader(f) if r['assembly']=='T-E']
for r in te:
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
notes=d.addObject('App::FeaturePython','RoofStudyNotes');notes.addProperty('App::PropertyString','Basis');notes.Basis='2026-09-15 rough massing study. Old exposed-frame model adapted to upper east X211.5 / lower east beam X247.5. Top solar row replaced by skylights. T-E and east roof rafters use coordinated chord endpoints; remaining historical steel is context only, not an engineering model.'
d.recompute();G.activeDocument().activeView().viewAxonometric();G.activeDocument().activeView().fitAll()
d.saveAs(str(P/'garage-east-infill-skylights.FCStd'))
objects=[];export=[]
for o in d.Objects:
 if 'Shape' not in o.PropertiesList or o.Shape.isNull():continue
 assert o.Shape.isValid(),o.Label
 export.append(o);vs,ts=o.Shape.tessellate(2)
 mat=o.StudyMaterial if 'StudyMaterial' in o.PropertiesList else ('stucco' if any(g.Name=='ExistingGarage' for g in o.InList) else 'steel' if any(g.Name.startswith(('Truss','Columns','Bracing')) for g in o.InList) else 'panel')
 objects.append(dict(name=o.Label,group=next((g.Name for g in o.InList if g.TypeId=='App::DocumentObjectGroup'),'Context'),material=mat,vertices=[[v.x/U,v.y/U,v.z/U] for v in vs],triangles=ts))
Part.export(export,str(P/'garage-east-infill-skylights.step'))
(P/'cad-mesh.json').write_text(json.dumps({'objects':objects,'units':'inches'}))
(P/'validation.json').write_text(json.dumps({'valid_shapes':len(objects),'skylights':6,'pv_panels':18,'east_rafters':12,'rafter_spacing_in':23,'rafter_endpoint_checks':'12 lower endpoints on E-OB axis; 12 upper endpoints interpolated on coordinated T-E top chord','upper_east_x':east,'east_beam_x':outer,'status':'rough massing; not structural analysis'},indent=2))
print('CAD COMPLETE',len(objects),flush=True)
