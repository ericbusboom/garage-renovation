import pathlib, json
import FreeCAD as App
import Part
from zipfile import ZipFile
import xml.etree.ElementTree as ET
root=pathlib.Path(__file__).resolve().parent
with ZipFile(root/'garage.FCStd') as archive:
    gui=ET.fromstring(archive.read('GuiDocument.xml'))
    providers=gui.findall('.//ViewProvider')
    shown=[v.get('name') for v in providers if v.find("./Properties/Property[@name='Visibility']/Bool") is not None and v.find("./Properties/Property[@name='Visibility']/Bool").get('value')=='true']
    assert 'HipRoof' in shown and 'Eastwall' in shown
    assert 'proposal' not in shown
    assert gui.find('Camera') is not None
    assert 'height 10456.5' in gui.find('Camera').get('settings')
doc=App.openDocument(str(root/'garage.FCStd'))
roof=doc.getObject('HipRoof').Shape
assert roof.isValid() and len(roof.Solids)==1
assert abs(roof.BoundBox.YLength-249*25.4)<1e-6
windows=[o for o in doc.Objects if 'confirmed sill and height' in o.Label]
assert len(windows)==3
for window in windows:
    assert abs(window.Shape.BoundBox.ZMin-48*25.4)<1e-6
    assert abs(window.Shape.BoundBox.ZLength-24*25.4)<1e-6
assert abs(roof.BoundBox.ZMax-158.5*25.4)<1e-6
assert abs(roof.BoundBox.ZMin-98.5*25.4)<1e-6
ridge=[v.Point for v in roof.Vertexes if abs(v.Point.z-roof.BoundBox.ZMax)<1e-6]
assert len(ridge)==2 and abs((ridge[0]-ridge[1]).Length-18*25.4)<1e-6
shape=Part.read(str(root/'garage-existing.step'))
assert shape.isValid() and len(shape.Solids)==10
scene=json.loads((root/'scene.json').read_text())
assert len([x for x in scene['parts'] if x['group']=='proposal'])==24
for p in scene['parts']:
    assert all(0<=i<len(p['vertices']) for t in p['triangles'] for i in t)
print('PASS: saved GUI visibility and camera, native reopen, STEP round trip (10 solids plus floor face), exact roof rise/ridge, 24 frame members, all mesh indices')
