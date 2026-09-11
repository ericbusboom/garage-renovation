from pathlib import Path
import os,json,re
os.environ.setdefault('QT_QPA_PLATFORM','offscreen')
import FreeCAD as App, Part, Mesh

R=Path(__file__).resolve().parent
doc=App.newDocument('ExistingBackyard')
groups={}
obj=doc.addObject('PartDesign::Feature','MeasuredExistingGarage');obj.Label='Existing garage — measured source solid';obj.Shape=Part.read(str(R.parent/'model/garage-existing.step'))
for i,p in enumerate(json.loads((R/'site-scene.json').read_text())['parts']):
 if p['group'] in ['garage','garage_roof']:continue
 g=p['group']
 if g not in groups:
  groups[g]=doc.addObject('App::DocumentObjectGroup',g);groups[g].Label=g.replace('_',' ').title()+' — estimated'
 v=[App.Vector(*[x*1000 for x in q]) for q in p['vertices']]
 mesh=Mesh.Mesh([[v[j] for j in t] for t in p['triangles']])
 o=doc.addObject('Mesh::Feature','SiteMesh'+str(i));o.Label=p['name'];o.Mesh=mesh;groups[g].addObject(o)
info=doc.addObject('App::FeaturePython','Basis');info.addProperty('App::PropertyString','Notes');info.Notes='CAD units millimetres. Garage SW corner origin, X east Y north Z up. Existing garage STEP solid imported; site objects editable named meshes. Site estimated from schematic and photographs, not a survey. Source build_site.py regenerates meshes.'
doc.recompute()
doc.saveAs(str(R/'existing-backyard.FCStd'))
assert obj.Shape.isValid()
print('CAD saved; garage solid valid; objects:',len(doc.Objects))
App.closeDocument(doc.Name)
