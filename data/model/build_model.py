"""Run with FreeCAD's Python, or exec this file in FreeCAD's Python console.
All input lengths are inches; CAD geometry is millimetres. No external packages.
"""
import json, pathlib, math, os, xml.etree.ElementTree as ET
import FreeCAD as App
import Part

# Native FCStd deliverables require GUI view providers and camera data even
# when generated from the command line. No on-screen window is needed here.
if not App.GuiUp:
    os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
    import FreeCADGui as Gui
    Gui.showMainWindow()

ROOT = pathlib.Path(__file__).resolve().parent
p = json.loads((ROOT / 'parameters.json').read_text())
doc = App.newDocument('GarageExisting')
U = 25.4
V = App.Vector
W,L,H = (p[k] for k in ('width','length','wall_height'))
groups={}
for key,label in [('existing','Existing garage'),('roof','Existing hip roof'),('infill','Doors and windows (door heights assumed)'),('proposal','Proposed structure - assumed elevation')]:
    g=doc.addObject('App::DocumentObjectGroup',key);g.Label=label;groups[key]=g
metadata=doc.addObject('App::FeaturePython','Dimensions')
metadata.Label='Dimensions and assumptions (see parameters.json to regenerate)'
for k,v in p.items():
    if isinstance(v,(float,int)):
        metadata.addProperty('App::PropertyLength', k, 'Source dimensions');setattr(metadata,k,v*U)
metadata.addProperty('App::PropertyString','Notes');metadata.Notes='North-south wall length 249 in confirmed by user; 286.25 in dimensions other features. Window sills 48 in, height 24 in confirmed. Door heights and overhang unmeasured. X east, Y north, Z up.'
visible=[]
def box(name,x,y,z,dx,dy,dz,group,color):
    o=doc.addObject('Part::Box',''.join(c for c in name if c.isalnum()));o.Label=name
    o.Length=dx*U;o.Width=dy*U;o.Height=dz*U;o.Placement.Base=V(x*U,y*U,z*U)
    groups[group].addObject(o)
    if App.GuiUp: o.ViewObject.ShapeColor=color
    return o
def record(o,group,color): visible.append((o,group,color))
# Plan x increases westwards. Mirror x to use conventional CAD X east, Y north.
gray=(0.70,0.72,0.72); blue=(0.37,0.61,0.69); wood=(0.55,0.34,0.17)
walls={
 'south':box('South wall',0,0,0,W,p['wall_south'],H,'existing',gray),
 'north':box('North wall',0,L-p['wall_north'],0,W,p['wall_north'],H,'existing',gray),
 'east':box('East wall',W-p['wall_east'],p['wall_south'],0,p['wall_east'],L-p['wall_south']-p['wall_north'],H,'existing',gray),
 'west':box('West wall',0,p['wall_south'],0,p['wall_west'],L-p['wall_south']-p['wall_north'],H,'existing',gray)}
for op in p['openings']:
    side=op['side']; w=op['width']; off=op['offset'];typ=op['type']
    z=p['window_sill'] if typ=='window' else 0
    h=p['window_height'] if typ=='window' else p['door_height'] if typ=='door' else p['garage_door_height']
    if side=='south': x,y,dx,dy=W-off-w,-1,w,p['wall_south']+2
    elif side=='north': x,y,dx,dy=W-off-w,L-p['wall_north']-1,w,p['wall_north']+2
    else: x,y,dx,dy=-1,off,p['wall_west']+2,w
    cut=box(op['name']+' cutter',x,y,z,dx,dy,h,'existing',gray)
    wall=walls[side];out=doc.addObject('Part::Cut','OpeningCut');out.Label=op['name']+' opening';out.Base=wall;out.Tool=cut
    groups['existing'].addObject(out);walls[side]=out
    wall.Visibility=False;cut.Visibility=False
    if App.GuiUp: out.ViewObject.ShapeColor=gray
    if side=='west': x,dx=p['wall_west']/2,1
    else: y,dy=(p['wall_south']/2 if side=='south' else L-p['wall_north']/2),1
    pane=box(op['name']+(' (confirmed sill and height)' if typ=='window' else ' (assumed height)'),x,y,z,dx,dy,h,'infill',blue if typ=='window' else wood)
    record(pane,'infill',blue if typ=='window' else wood)
for o in walls.values(): record(o,'existing',gray)
# A floor reference surface only; no slab thickness or structural capacity inferred.
floor=doc.addObject('Part::Feature','FloorReference');floor.Label='Floor datum surface (no thickness specified)'
floor.Shape=Part.Face(Part.makePolygon([V(0,0,0),V(W*U,0,0),V(W*U,L*U,0),V(0,L*U,0),V(0,0,0)]))
groups['existing'].addObject(floor);record(floor,'existing',(0.54,0.55,0.53))
# Closed roof envelope with exactly four slope faces and an 18 inch ridge.
e=p['overhang'];r=p['ridge_length'];peak=H+p['roof_rise']
points=[(-e,-e,H),(W+e,-e,H),(W+e,L+e,H),(-e,L+e,H),(W/2,(L-r)/2,peak),(W/2,(L+r)/2,peak)]
faces=[[0,1,4],[1,2,5,4],[2,3,5],[3,0,4,5],[3,2,1,0]]
ff=[]
for inds in faces:
    vv=[V(*[a*U for a in points[i]]) for i in inds];ff.append(Part.Face(Part.makePolygon(vv+[vv[0]])))
roof=doc.addObject('Part::Feature','HipRoof');roof.Label='Existing hip roof envelope - 18 inch N-S ridge'
roof.Shape=Part.makeSolid(Part.makeShell(ff));groups['roof'].addObject(roof);record(roof,'roof',(0.34,0.40,0.44))
# Preserve proposal XY literally from SVG (6 drawing units/in), without stretching.
for spec in json.loads((ROOT/'plan_structure.json').read_text()):
    x=W-spec['x']-spec['width']; y=spec['y']; post=spec['post']
    o=box(('Post ' if post else 'Beam ')+spec['id'],x,y,0 if post else p['beam_bottom'],spec['width'],spec['height'],p['beam_bottom'] if post else p['beam_depth'],'proposal',wood if post else (0.72,0.68,0.57))
    record(o,'proposal',wood if post else (0.72,0.68,0.57))
doc.recompute()
mesh=[];checks=[]
for o,g,c in visible:
    checks.append({'name':o.Label,'valid':o.Shape.isValid(),'solids':len(o.Shape.Solids),'volume_mm3':o.Shape.Volume})
    vs,ts=o.Shape.tessellate(1)
    mesh.append({'name':o.Label,'group':g,'color':c,'vertices':[[v.x/U,v.y/U,v.z/U] for v in vs],'triangles':[list(t) for t in ts]})
    if App.GuiUp: o.ViewObject.ShapeColor=c
    o.Visibility=g!='proposal'
assert all(c['valid'] for c in checks), checks
doc.recompute()
if App.GuiUp:
    import FreeCADGui as Gui
    # Set group visibility first: changing it can propagate to every child.
    for key, group in groups.items(): group.ViewObject.Visibility=key!='proposal'
    for o in doc.Objects:
        if hasattr(o, 'Shape'): o.ViewObject.Visibility=False
    for o,g,c in visible: o.ViewObject.Visibility=g!='proposal'
    Gui.activeDocument().activeView().viewAxonometric()
    camera=App.Rotation(V(0,0,1),225).multiply(App.Rotation(V(1,0,0),55))
    offset=camera.multVec(V(0,0,20000))
    view=Gui.activeDocument().activeView()
    view.setCamera('#Inventor V2.1 ascii\nOrthographicCamera { position %g %g %g orientation %g %g %g %g nearDistance 1 farDistance 100000 focalDistance 20000 height %g }' % (W*U/2+offset.x,L*U/2+offset.y,H*U/2+offset.z,camera.Axis.x,camera.Axis.y,camera.Axis.z,camera.Angle,max(W,L)*U*1.65))
doc.saveAs(str(ROOT/'garage.FCStd'))
Part.export([o for o,g,c in visible if g!='proposal'],str(ROOT/'garage-existing.step'))
Part.export([o for o,g,c in visible if g=='proposal'],str(ROOT/'proposal-concept.step'))
(ROOT/'scene.json').write_text(json.dumps({'parameters':p,'parts':mesh},separators=(',',':')))
(ROOT/'validation.json').write_text(json.dumps(checks,indent=2))
# OBJ and COLLADA in metres, with individual named objects.
obj=['# Garage existing; metres; X east Y north Z up'];idx=1
for part in mesh:
    if part['group']=='proposal':continue
    obj.append('o '+part['name'].replace(' ','_'))
    obj.extend('v '+' '.join(str(v*.0254) for v in vert) for vert in part['vertices'])
    obj.extend('f '+' '.join(str(i+idx) for i in tri) for tri in part['triangles']);idx+=len(part['vertices'])
(ROOT/'garage-existing.obj').write_text('\n'.join(obj)+'\n')
ns='http://www.collada.org/2005/11/COLLADASchema';ET.register_namespace('',ns)
def el(parent,name,attrs={},text=None):
    n=ET.SubElement(parent,'{'+ns+'}'+name,attrs);n.text=text;return n
root=ET.Element('{'+ns+'}COLLADA',{'version':'1.4.1'});asset=el(root,'asset');el(asset,'created',text='2026-09-07T00:00:00Z');el(asset,'modified',text='2026-09-07T00:00:00Z');el(asset,'unit',{'name':'meter','meter':'1'});el(asset,'up_axis',text='Z_UP')
lib=el(root,'library_geometries');vl=el(root,'library_visual_scenes');scene=el(vl,'visual_scene',{'id':'Garage'})
for j,part in enumerate(mesh):
    if part['group']=='proposal':continue
    ident='part'+str(j);geom=el(lib,'geometry',{'id':ident,'name':part['name']});m=el(geom,'mesh');src=el(m,'source',{'id':ident+'pos'})
    el(src,'float_array',{'id':ident+'array','count':str(len(part['vertices'])*3)},' '.join(str(v*.0254) for vert in part['vertices'] for v in vert))
    tech=el(src,'technique_common');acc=el(tech,'accessor',{'source':'#'+ident+'array','count':str(len(part['vertices'])),'stride':'3'})
    for axis in 'XYZ':el(acc,'param',{'name':axis,'type':'float'})
    verts=el(m,'vertices',{'id':ident+'verts'});el(verts,'input',{'semantic':'POSITION','source':'#'+ident+'pos'})
    tris=el(m,'triangles',{'count':str(len(part['triangles']))});el(tris,'input',{'semantic':'VERTEX','source':'#'+ident+'verts','offset':'0'});el(tris,'p',text=' '.join(str(i) for t in part['triangles'] for i in t))
    node=el(scene,'node',{'id':ident+'node','name':part['name']});el(node,'instance_geometry',{'url':'#'+ident})
el(el(root,'scene'),'instance_visual_scene',{'url':'#Garage'})
ET.ElementTree(root).write(ROOT/'garage-existing.dae',encoding='utf-8',xml_declaration=True)
print('Saved native CAD, STEP, OBJ, DAE and scene;',len(mesh),'parts; all shapes valid.')
