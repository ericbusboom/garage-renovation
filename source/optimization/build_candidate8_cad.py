"""Separate native CAD candidate; original Proposed-Garage is never modified."""
import os,sys,json,re,math
from pathlib import Path
os.environ.setdefault('QT_QPA_PLATFORM','offscreen');os.environ.setdefault('FONTCONFIG_FILE','/etc/fonts/fonts.conf')
sys.path.insert(0,'/opt/freecad-1.1.3/usr/lib')
import FreeCAD as A,FreeCADGui as G,Part
P=Path(__file__).resolve().parent;I=25.4
cad=json.loads((P/'candidate8-candidate-geometry.json').read_text());sel=json.loads((P/'candidate8-candidate-selection.json').read_text());cat=json.loads((P/'iteration2-catalog.json').read_text());result=json.loads((P/'candidate8_complete.json').read_text())
G.showMainWindow();d=A.newDocument('GarageCandidate8');root=d.addObject('App::DocumentObjectGroup','StructuralCandidate');root.Label='Candidate 8 — preliminary; joints, bracing and foundations require design';groups={};mesh=[];count=0
for m in cad['members']:
 if m['id']=='W2':continue
 s=cat[sel[m['id']]];v0=A.Vector(*[x*I for x in m['a']]);v1=A.Vector(*[x*I for x in m['b']]);axis=v1-v0;length=axis.Length;axis.normalize()
 t=A.Vector(0,0,1).cross(axis)
 if t.Length<1e-6:t=A.Vector(1,0,0)
 t.normalize();u=axis.cross(t);u.normalize()
 def face(points):
  vv=[v0+t*(x*I)+u*(y*I) for x,y in points];return Part.Face(Part.makePolygon(vv+[vv[0]]))
 if s['type']=='HSS':
  h=s['d']/2;inside=h-s['t'];outer=face([(-h,-h),(h,-h),(h,h),(-h,h)]);inner=face([(-inside,-inside),(inside,-inside),(inside,inside),(-inside,inside)]);profile=outer.cut(inner)
 else:
  h=s['d']/2;w=s['bf']/2;tw=s['tw']/2;tf=s['tf'];profile=face([(-w,-h),(w,-h),(w,-h+tf),(tw,-h+tf),(tw,h-tf),(w,h-tf),(w,h),(-w,h),(-w,h-tf),(-tw,h-tf),(-tw,-h+tf),(-w,-h+tf)])
 shape=profile.extrude(axis*length);assert shape.isValid() and shape.Volume>0,m['id']
 name=re.sub('[^A-Za-z0-9_]','_',m['id']);o=d.addObject('PartDesign::Feature',name);o.Label=m['id']+' — '+s['name'];o.Shape=shape
 group='Bracing' if m['id'].startswith('BR-') else 'Columns' if m['axis_source'].get('ground_post') else 'FutureLoftSteel' if m['section_family']=='hanger' or m['id'] in ['B2 future floor beam','T1 future floor beam'] else 'PrimaryTrusses'
 if group not in groups:groups[group]=d.addObject('App::DocumentObjectGroup',group);root.addObject(groups[group])
 groups[group].addObject(o)
 for key,val in [('MemberId',m['id']),('StockSection',s['name']),('ConstructionStage','After old roof removal' if group=='FutureLoftSteel' else 'Proposed roof-first frame'),('ModelLimit','Centerline study. Overlaps/gaps at joints need actual connection detailing; not shop drawings.')]:o.addProperty('App::PropertyString',key);setattr(o,key,val)
 color=(.58,.30,.70) if group=='Bracing' else (.77,.48,.23) if group=='Columns' else (.20,.38,.68) if group=='FutureLoftSteel' else (.12,.52,.53)
 o.ViewObject.ShapeColor=color;o.ViewObject.LineColor=(.15,.18,.21)
 vv,tt=shape.tessellate(2);mesh.append(dict(name=m['id'],group=group,section=s['name'],vertices=[[p.x/I,p.y/I,p.z/I] for p in vv],triangles=tt,color=color));count+=1
roofgroup=d.addObject('App::DocumentObjectGroup','RoofReference');root.addObject(roofgroup);rooflines=[]
source=json.loads((P.parent/'renovated-loft-mesh.json').read_text())
for item in source['objects']:
 if not item['name'].startswith(('MainRoofLine','CapEaveLine','CapHipLine','CapRidgeLine')):continue
 for k,line in enumerate(item.get('lines',[])):
  o=d.addObject('PartDesign::Feature',item['name']+'_'+str(k));o.Label=item.get('label',item['name']);o.Shape=Part.makePolygon([A.Vector(*p) for p in line]);roofgroup.addObject(o);o.ViewObject.LineColor=(.35,.40,.47);o.ViewObject.LineWidth=1.5;rooflines.append([[x/I for x in p] for p in line])
loft=d.addObject('App::DocumentObjectGroup','LoftDeck');root.addObject(loft)
o=d.addObject('Part::Box','Deck');o.Label='3/4-inch loft deck — connections not detailed';o.Length=224.25*I;o.Width=177*I;o.Height=.75*I;o.Placement.Base=A.Vector(0,72*I,120*I);loft.addObject(o);o.ViewObject.ShapeColor=(.83,.74,.57);o.ViewObject.Transparency=65
joists=d.addObject('App::DocumentObjectGroup','WoodJoists');root.addObject(joists)
for n,x in enumerate([.75+16*i for i in range(14)]+[223.5]):
 for bay,(y0,y1) in enumerate([(72.75,181.75),(188.25,246)]):
  j=d.addObject('Part::Box','Joist_%s_%s'%(n,bay));j.Label='2x8 joist — species/grade and hangers not selected';j.Length=1.5*I;j.Width=(y1-y0)*I;j.Height=7.25*I;j.Placement.Base=A.Vector((x-.75)*I,y0*I,112.75*I);joists.addObject(j);j.ViewObject.ShapeColor=(.65,.46,.25)
notes=d.addObject('Spreadsheet::Sheet','CandidateNotes');root.addObject(notes)
for i,(k,v) in enumerate([('Status','Preliminary candidate, not a fabrication design'),('Removed post','W2 only; original model retained separately'),('Floor live load','40 psf plus 75 psf storage bands; occupancy code minimum unresolved'),('Hoist','1000 lb rated + assumed impact and hardware'),('Bracing','Purple. Verify clearance to windows, walkway and outbuilding.'),('Restraint','Chords/rails require designed lateral/torsional braces at <=72 in.'),('Wall support','No vertical capacity credited to original garage walls/slab.'),('Joints','Centerlines retained while sections change. Bearings and offsets require detailing.'),('Wind','10 and 20 psf lateral-force sensitivities; not site wind design.')],1):notes.set('A'+str(i),k);notes.set('B'+str(i),v)
notes.setColumnWidth('A',160);notes.setColumnWidth('B',650)
d.recompute();G.activeDocument().activeView().viewAxonometric();G.activeDocument().activeView().fitAll();d.recompute();d.saveAs(str(P/'Garage-Candidate-8.FCStd'))
(P/'candidate8-cad-mesh.json').write_text(json.dumps({'units':'in','objects':mesh,'removed_columns':['W2'],'stage':'proposed','roof_lines':rooflines},indent=2))
(P/'candidate8-cad-validation.json').write_text(json.dumps({'valid_members':count,'invalid_members':0,'source_model_unchanged':True,'candidate_path':str(P/'Garage-Candidate-8.FCStd')},indent=2))
print('Saved separate candidate CAD:',count,'valid members')
sys.stdout.flush();os._exit(0)
