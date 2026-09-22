"""Native FreeCAD solid frame and inward mounted metal envelope. Inch inputs, mm CAD."""
import os,sys,json,re,math
from pathlib import Path
os.environ.setdefault('QT_QPA_PLATFORM','offscreen');os.environ.setdefault('FONTCONFIG_FILE','/etc/fonts/fonts.conf')
sys.path.insert(0,'/opt/freecad-1.1.3/usr/lib')
import FreeCAD as A, FreeCADGui as G, Part
P=Path(__file__).resolve().parent;I=25.4
cad=json.loads((P/'geometry.json').read_text());sel=json.loads((P/'selected.json').read_text());cat=json.loads((P/'catalog.json').read_text());members={m['id']:m for m in cad['members']}
G.showMainWindow();d=A.newDocument('GarageExposedSteel');groups={};objects=[];valid=[]
colors={'steel':(.19,.23,.25),'panel':(.68,.72,.73),'trim':(.9,.9,.87),'roof':(.22,.26,.28),'pv':(.07,.12,.17),'glass':(.25,.43,.49),'wood':(.67,.49,.30),'stucco':(.70,.71,.69),'slab':(.53,.54,.52)}
def V(p):return A.Vector(*[v*I for v in p])
def obj(name,shape,group,mat,props=None):
 assert shape.isValid() and shape.Volume>1e-6,name
 key=re.sub('[^A-Za-z0-9_]','_',name)
 o=d.addObject('PartDesign::Feature',key);o.Label=name;o.Shape=shape
 if group not in groups:groups[group]=d.addObject('App::DocumentObjectGroup',group)
 groups[group].addObject(o);o.ViewObject.ShapeColor=colors[mat];o.ViewObject.LineColor=(.12,.15,.17)
 for k,v in (props or {}).items():o.addProperty('App::PropertyString',k);setattr(o,k,str(v))
 vv,tt=shape.tessellate(.8);objects.append(dict(name=name,group=group,material=mat,vertices=[[p.x/I,p.y/I,p.z/I] for p in vv],triangles=tt));valid.append(name);return o

def boxshape(x,y,z,dx,dy,dz):return Part.makeBox(dx*I,dy*I,dz*I,V((x,y,z)))
def box(name,x,y,z,dx,dy,dz,group,mat):return obj(name,boxshape(x,y,z,dx,dy,dz),group,mat)
def prism(pts,delta):return Part.Face(Part.makePolygon([V(p) for p in pts]+[V(pts[0])])).extrude(V(delta))
# Preserve centerlines exactly; profile wall thickness and flange dimensions from catalog.
for mid,key in sel.items():
 m=members[mid];s=cat[key];v0=V(m['a']);axis=V(m['b'])-v0;length=axis.Length;axis.normalize();t=A.Vector(0,0,1).cross(axis)
 if t.Length<1e-6:t=A.Vector(1,0,0)
 t.normalize();u=axis.cross(t);u.normalize()
 def face(points):
  pp=[v0+t*(x*I)+u*(y*I) for x,y in points];return Part.Face(Part.makePolygon(pp+[pp[0]]))
 h=s['d']/2
 if s['type']=='HSS':
  k=h-s['t'];shape=face([(-h,-h),(h,-h),(h,h),(-h,h)]).cut(face([(-k,-k),(k,-k),(k,k),(-k,k)])).extrude(axis*length)
 else:
  w=s['bf']/2;tw=s['tw']/2;tf=s['tf'];shape=face([(-w,-h),(w,-h),(w,-h+tf),(tw,-h+tf),(tw,h-tf),(w,h-tf),(w,h),(-w,h),(-w,h-tf),(-tw,h-tf),(-tw,-h+tf),(-w,-h+tf)]).extrude(axis*length)
 group='Columns' if m['role']=='column' else 'Bracing' if mid.startswith('BR-') else 'LoftSteel' if 'future' in mid else 'Truss_'+(m.get('truss') or 'Other')
 obj(mid+' | '+s['aisc_label'],shape,group,'steel',dict(MemberId=mid,StockSection=s['aisc_label'],SizingBasis='Fixed-geometry weight-sizing study, preliminary',AxisStartIn=m['a'],AxisEndIn=m['b'],LengthIn=length/I,DetailStatus='Centerline solids; joints/miters/bracing and foundations not fabrication-detailed'))
# Existing lower walls copied from the measured native CAD, not the older visual model.
old=A.openDocument(str(P.parents[1]/'Existing-Garage.FCStd'));ref=json.loads((P/'existing-walls-reference.json').read_text())
for e in ref['objects']:obj(e['label'],old.getObject(e['name']).Shape.copy(),'ExistingGarage','stucco')
A.closeDocument(old.Name);A.setActiveDocument(d.Name)
box('Existing slab reference',0,0,-2,249.5,249,2,'ExistingGarage','slab')
# New loft deck matches analytical loaded footprint. Joists remain a visual allowance.
box('Loft plywood deck',0,72,120,224.25,177,.75,'LoftDeck','wood')
for i,x in enumerate([.75+16*i for i in range(14)]+[223.5]):
 for j,(a,b) in enumerate([(72.75,182),(188,249)]):box('Wood joist %s-%s'%(i,j),x-.75,a,112.75,1.5,b-a,7.25,'LoftJoists','wood')
# Side panels are wholly inboard of external steel. Panel thickness is architectural only.
br=122.7624491117621
zroof=lambda y: min(120+(y+63)*math.tan(math.pi/6),227.25)
openings={'W':[(145,173,153,177),(186,246,120.75,206)],'E':[],'N':[(-13,30,153,185),(54.75,153.75,120.75,206),(174,211,153,185)],'S':[]}
# Build individually removable 24-in-wide vertical infill panels with actual opening cutouts.
def panels(side,lo,hi,base,top,axis,thick):
 edges=[lo]+[v for v in range(math.ceil(lo/24)*24,math.ceil(hi/24)*24,24) if lo<v<hi]+[hi]
 for i,(a,b) in enumerate(zip(edges[:-1],edges[1:])):
  a+=.045;b-=.045;pts=[(a,base),(b,base),(b,top(b)),(a,top(a))]
  if a<br<b and side in ['W','E']:pts.insert(3,(br,top(br)))
  if side in ['W','E']:
   sh=prism([(axis,q,z) for q,z in pts],(thick,0,0))
   for q0,q1,z0,z1 in openings[side]:sh=sh.cut(boxshape(axis-5,q0,z0,12,q1-q0,z1-z0))
  else:
   sh=prism([(q,axis,z) for q,z in pts],(0,thick,0))
   for q0,q1,z0,z1 in openings[side]:sh=sh.cut(boxshape(q0,axis-5,z0,q1-q0,12,z1-z0))
  if sh.Volume>1e-6:obj(side+' inside metal panel '+str(i+1),sh,'InteriorMetalPanels','panel',dict(PanelSide='Inside structural frame',ThicknessIn=abs(thick),DetailStatus='Illustrative insulated metal infill; attachment design pending'))
panels('W',-63,253,98.5,zroof,-28.5,2)
panels('E',-63,253,98.5,zroof,220.75,-2)
panels('N',-28.5,249.5,98.5,lambda q:227.25,249,-2)
panels('S',-28.5,220.75,98.5,lambda q:zroof(3.5),3.5,2)
# Window and door infill, white reveals. West balcony is recessed behind the frame.
def opening(side,q0,q1,z0,z1,plane,door=False):
 g='DoorsWindows';w=2
 if side=='W':
  box('West glazing',plane,q0+w,z0+w,.2,q1-q0-2*w,z1-z0-2*w,g,'glass')
  for q in [q0,q1-w,(q0+q1)/2-w/2]:box('West opening vertical trim',plane-.4,q,z0,.8,w,z1-z0,g,'trim')
  for z in [z0,z1-w]:box('West opening horizontal trim',plane-.4,q0,z,.8,q1-q0,w,g,'trim')
 else:
  box('North loading door glass' if door else 'North window glass',q0+w,plane,z0+w,q1-q0-2*w,.2,z1-z0-2*w,g,'glass')
  for q in [q0,q1-w,(q0+q1)/2-w/2]:box('North opening vertical trim',q,plane-.4,z0,w,.8,z1-z0,g,'trim')
  for z in [z0,z1-w]:box('North opening horizontal trim',q0,plane-.4,z,q1-q0,.8,w,g,'trim')
for q0,q1,z0,z1 in openings['N']:opening('N',q0,q1,z0,z1,247.8,q0==54.75)
opening('W',145,173,153,177,-27.8)
opening('W',188,244,120.75,204.5,0,True)
box('White recessed balcony floor',-32,186,120,32,60,.75,'Balcony','trim')
for y in [186,246]:box('Balcony inside reveal',-26.5,y,120.75,26.5,1.5,85.25,'Balcony','panel')
for y in range(187,247,5):box('Balcony railing',-32.5,y,120.75,1,1,38,'Balcony','steel')
box('Balcony top rail',-32.75,186,157.75,1.5,61,1.5,'Balcony','steel')
# Retain hipped cap: reference eave is underside; 8-in fascia zone above it, 18-in hip rise.
x0=-40;x1=257.5;y0=br-8;y1=271;eave=235.25;ridge=eave+18;ym=(y0+y1)/2;run=(y1-y0)/2;rl=x0+run;rr=x1-run
for name,pts in [('south',[(x0,y0,eave),(x1,y0,eave),(rr,ym,ridge),(rl,ym,ridge)]),('east',[(x1,y0,eave),(x1,y1,eave),(rr,ym,ridge)]),('north',[(x1,y1,eave),(x0,y1,eave),(rl,ym,ridge),(rr,ym,ridge)]),('west',[(x0,y1,eave),(x0,y0,eave),(rl,ym,ridge)])]:obj('Hip cap metal '+name,prism(pts,(0,0,-.08)),'HipRoofCap','roof')
# Soffit only perimeter strips, preserving open cap cavity and frame view from inside.
for name,x,y,dx,dy in [('S',x0,y0,x1-x0,8),('N',x0,y1-8,x1-x0,8),('W',x0,y0,8,y1-y0),('E',x1-8,y0,8,y1-y0)]:box('White soffit '+name,x,y,227.25,dx,dy,.4,'HipRoofCap','trim')
for name,x,y,dx,dy in [('S',x0,y0,x1-x0,.75),('N',x0,y1-.75,x1-x0,.75),('W',x0,y0,.75,y1-y0),('E',x1-.75,y0,.75,y1-y0)]:box('White fascia '+name,x,y,227.25,dx,dy,8,'HipRoofCap','trim')
# Continuous weather skin + glass-faced solar grid, no elevated racks. Roof-line plus 8-in assembly zone.
obj('Main metal waterproof roof skin',prism([(-32,-63,127.8),(249.5,-63,127.8),(249.5,br,235.05),(-32,br,235.05)],(0,0,.08)),'SolarRoof','roof')
for i in range(6):
 for j in range(4):
  xa=-32+i*281.5/6+.18;xb=-32+(i+1)*281.5/6-.18;ya=-63+j*(br+63)/4+.18;yb=-63+(j+1)*(br+63)/4-.18
  z=lambda y:128+(y+63)*math.tan(math.pi/6)
  obj('Flush solar-glass panel %s-%s'%(i+1,j+1),prism([(xa,ya,z(ya)),(xb,ya,z(ya)),(xb,yb,z(yb)),(xa,yb,z(yb))],(0,0,.12)),'SolarRoof','pv')
# Fascia encloses the reserved lightweight secondary roof zone at exposed edges.
box('Main roof south fascia',-32,-63,120,281.5,.5,8,'SolarRoof','roof')
for x,label in [(-32,'west'),(249,'east')]:
 obj('Main roof '+label+' fascia',prism([(x,-63,120),(x,br,227.25),(x,br,235.25),(x,-63,128)],(.5,0,0)),'SolarRoof','roof')
# Existing ground-floor door/window infill on measured openings.
box('South entry door',111.5,-.3,0,32,.5,80,'ExistingGarage','trim')
box('South window',42,-.3,48,28,.3,24,'ExistingGarage','glass')
for y,w in [(73,28.5),(153.25,28.75)]:box('Existing west window',-.3,y,48,.3,w,24,'ExistingGarage','glass')
box('Existing north garage door',56.25,249,0,165,.5,86,'ExistingGarage','trim')
notes=d.addObject('Spreadsheet::Sheet','ModelNotes')
for i,(k,v) in enumerate([('Revision','Selected weight-sizing geometry and sections; exposed frame / inside panels'),('Frame','All selected 88 members retain analyzed axes. HSS square corners simplified.'),('Panels','2-in illustrative insulated infill; placed inside steel, not exterior wrap.'),('Roof cap','18-in rise; white 8-in fascia; reference roof envelope retained.'),('Existing','Original lower walls retained; original roof excluded from finished renovation.'),('Detail limit','Connections, crossings, miters, panel fasteners and secondary framing require design.'),('Structural limit','Sizing study conditional on <=6ft chord restraint; envelope is not a designed diaphragm.')],1):notes.set('A'+str(i),k);notes.set('B'+str(i),v)
notes.setColumnWidth('A',130);notes.setColumnWidth('B',720)
d.recompute();G.activeDocument().activeView().viewAxonometric();G.activeDocument().activeView().fitAll();d.saveAs(str(P/'Garage-Exposed-Steel.FCStd'))
Part.export([o for o in d.Objects if o.TypeId=='PartDesign::Feature' and not o.Shape.isNull()],str(P/'Garage-Exposed-Steel.step'))
(P/'cad-mesh.json').write_text(json.dumps(dict(units='in',objects=objects)))
(P/'cad-validation.json').write_text(json.dumps(dict(valid_solids=len(valid),steel_members=len(sel),primary_weight_lb=sum(members[k]['length_inches']/12*cat[v]['w'] for k,v in sel.items()),north_wall_plane_in=253,panel_exterior_faces_in=dict(west_x=-28.5,east_x=220.75,north_y=249),status='Native solids valid; connection detailing is not complete'),indent=2))
print('CAD COMPLETE',len(valid),'solids',len(sel),'steel members',flush=True);os._exit(0)
