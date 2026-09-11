#!/usr/bin/env python3
"""Native FreeCAD garage walls. Run using bundled Python; see README.md."""
import os, sys, json, math, traceback, socket
from pathlib import Path
from datetime import datetime, timezone
ROOT = Path(__file__).resolve().parent
os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
os.environ.setdefault('FONTCONFIG_FILE', '/etc/fonts/fonts.conf')
os.environ.setdefault('XDG_CACHE_HOME', '/tmp/garage-freecad-cache')
Path(os.environ['XDG_CACHE_HOME']).mkdir(parents=True, exist_ok=True)
sys.path.insert(0, '/opt/freecad-1.1.3/usr/lib')
import FreeCAD as App, FreeCADGui as Gui, Part
INCH = 25.4
PARAMS = json.loads((ROOT/'existing-parameters.json').read_text())
RESULT = {'request_id':'EXISTING-GARAGE-WALLS-001','status':'failed','hostname':socket.gethostname(), 'timestamp_utc':datetime.now(timezone.utc).isoformat(), 'errors':[], 'artifact_paths':[], 'summary':''}
validation = {'freecad_version':App.Version(), 'units':'mm', 'documents':{}, 'limitations':['Qt offscreen has no OpenGL rendering; saved view providers, visibility and camera checked. Mesh supplied for preview.', 'Bundled GUI Python has a teardown crash; generator flushes outputs and exits with os._exit after validation.']}

def near(a,b):
    return math.isclose(a,b,rel_tol=1e-8,abs_tol=1e-5)

def set_view():
    # Explicit camera avoids animated view transitions being saved mid-flight.
    rotation=App.Rotation(0.4247082002778669,0.1759198966061612,0.3398511429799874,0.8204732385702833)
    center=App.Vector(PARAMS['width']*INCH/2,PARAMS['length']*INCH/2,PARAMS['wall_height']*INCH/2)
    pos=center+rotation.multVec(App.Vector(0,0,15000))
    axis=rotation.Axis
    camera=f"#Inventor V2.1 ascii\nOrthographicCamera {{ position {pos.x} {pos.y} {pos.z} orientation {axis.x} {axis.y} {axis.z} {rotation.Angle} nearDistance 100 farDistance 30000 aspectRatio 1 focalDistance 15000 height 11000 }}"
    Gui.activeDocument().activeView().setCamera(camera)

def build(name):
    d=App.newDocument(name)
    d.Label = 'Existing Garage — walls only' if name=='ExistingGarage' else 'Proposed Garage — independent existing-wall starting copy'
    walls=d.addObject('App::DocumentObjectGroup','Walls'); walls.Label='Walls'
    stucco=d.addObject('App::DocumentObjectGroup','ExteriorStucco'); stucco.Label='Exterior stucco'
    dims=d.addObject('App::DocumentObjectGroup','Dimensions'); dims.Label='Dimensions'
    s=d.addObject('Spreadsheet::Sheet','Parameters'); s.Label='Dimensions — editable inches'; dims.addObject(s)
    s.set('A1','Dimension'); s.set('B1','Value (inches)'); s.set('C1','Meaning')
    s.setStyle('A1:C1','bold','add'); s.setColumnWidth('A',240); s.setColumnWidth('B',140); s.setColumnWidth('C',500)
    row=2; cells={}
    def param(alias,label,value,note=''):
        nonlocal row
        cell=f'B{row}'; s.set(f'A{row}',label); s.set(cell,f'{value} in'); s.setAlias(cell,alias); s.set(f'C{row}',note); cells[alias]=cell; row+=1
    for alias,key,label,note in [('Width','width','Core outside width','X east; excludes outboard stucco'),('Length','length','Core outside length','Y north; excludes outboard stucco'),('Height','wall_height','Wall height','Z up'),('Core','wall_thickness','Wall core thickness',''),('Stucco','stucco_thickness','Exterior stucco thickness','Added outboard of core'),('WindowSill','window_sill','Window sill','Above z=0'),('WindowHeight','window_height','Window height',''),('DoorHeight','door_height','South entry height',''),('GarageHeight','garage_door_height','North garage opening height','')]:
        param(alias,label,PARAMS[key],note)
    for i,o in enumerate(PARAMS['openings'],1):
        param(f'O{i}Offset',o['name']+' offset',o['offset'],'From south on west wall; otherwise from east')
        param(f'O{i}Width',o['name']+' width',o['width'],'Clear hole width')
    def expr(t):
        import re
        return re.sub(r'\b(Width|Length|Height|Core|Stucco|WindowSill|WindowHeight|DoorHeight|GarageHeight|O\d+(?:Offset|Width))\b',r'Parameters.\1',t)
    def box(name,label,group,size,pos):
        b=d.addObject('Part::Box',name); b.Label=label; group.addObject(b)
        for prop,value in zip(['Length','Width','Height','Placement.Base.x','Placement.Base.y','Placement.Base.z'],size+pos):
            b.setExpression(prop,expr(value))
        return b
    cutters={}
    for i,o in enumerate(PARAMS['openings'],1):
        height='WindowHeight' if o['type']=='window' else ('GarageHeight' if o['type']=='garage' else 'DoorHeight')
        z='WindowSill' if o['type']=='window' else '0 mm'
        if o['side']=='west':
            size=['Core+2*Stucco+2 mm',f'O{i}Width',height]; pos=['-Stucco-1 mm',f'O{i}Offset',z]
        else:
            size=[f'O{i}Width','Core+2*Stucco+2 mm',height]
            pos=[f'Width-O{i}Offset-O{i}Width','-Stucco-1 mm' if o['side']=='south' else 'Length-Core-1 mm',z]
        cutters[i]=box(f'Opening{i}',o['name']+' — hidden cutter',walls,size,pos)
    specs={
        'South':(['Width','Core','Height'],['0 mm','0 mm','0 mm']),
        'North':(['Width','Core','Height'],['0 mm','Length-Core','0 mm']),
        'West':(['Core','Length-2*Core','Height'],['0 mm','Core','0 mm']),
        'East':(['Core','Length-2*Core','Height'],['Width-Core','Core','0 mm'])}
    sspecs={
        'South':(['Width+2*Stucco','Stucco','Height'],['-Stucco','-Stucco','0 mm']),
        'North':(['Width+2*Stucco','Stucco','Height'],['-Stucco','Length','0 mm']),
        'West':(['Stucco','Length','Height'],['-Stucco','0 mm','0 mm']),
        'East':(['Stucco','Length','Height'],['Width','0 mm','0 mm'])}
    outputs=[]
    for material,group,defs,color in [('Core',walls,specs,(0.73,0.74,0.76)),('Stucco',stucco,sspecs,(0.89,0.83,0.70))]:
        for side,(size,pos) in defs.items():
            current=box(material+side+'Base',side+' '+material.lower()+' base',group,size,pos)
            for i,o in enumerate(PARAMS['openings'],1):
                if o['side']!=side.lower(): continue
                c=d.addObject('Part::Cut',material+side+f'Cut{i}'); group.addObject(c); c.Base=current; c.Tool=cutters[i]; c.Refine=True; current=c
            current.Label=side+' '+('wall core' if material=='Core' else 'exterior stucco')
            current.ViewObject.ShapeColor=color; current.ViewObject.LineColor=(0.22,0.22,0.22)
            outputs.append(current)
    d.recompute()
    for o in d.Objects:
        if o.ViewObject: o.ViewObject.Visibility=o in outputs or o in [walls,stucco,dims]
    set_view()
    return d,s,cells,outputs,cutters

def inspect(d,outputs,cutters):
    d.recompute()
    shapes=[]
    for o in outputs:
        assert o.Shape.isValid() and not o.Shape.isNull(),o.Name+' invalid'
        assert len(o.Shape.Solids)==1,o.Name+' disconnected'
        assert o.ViewObject is not None and o.ViewObject.Visibility,o.Name+' invisible'
        shapes.append({'name':o.Name,'label':o.Label,'valid':True,'volume_mm3':o.Shape.Volume,'solids':len(o.Shape.Solids),'visible':bool(o.ViewObject.Visibility),'view_provider':o.ViewObject.TypeId})
    openings=[]
    for i,src in enumerate(PARAMS['openings'],1):
        c=cutters[i]; bb=c.Shape.BoundBox
        width=bb.YLength if src['side']=='west' else bb.XLength
        height=PARAMS['window_height'] if src['type']=='window' else PARAMS['garage_door_height'] if src['type']=='garage' else PARAMS['door_height']
        assert near(width,src['width']*INCH) and near(bb.ZLength,height*INCH)
        expected_x=-(PARAMS['stucco_thickness']*INCH)-1 if src['side']=='west' else (PARAMS['width']-src['offset']-src['width'])*INCH
        assert near(bb.XMin,expected_x)
        if src['side']=='west': assert near(bb.YMin,src['offset']*INCH)
        assert near(bb.ZMin,(PARAMS['window_sill'] if src['type']=='window' else 0)*INCH)
        overlap=sum(o.Shape.common(c.Shape).Volume for o in outputs)
        assert overlap<1e-4,src['name']+' not open'
        openings.append({'name':src['name'],'side':src['side'],'width_mm':width,'height_mm':bb.ZLength,'sill_mm':bb.ZMin,'x_min_mm':bb.XMin,'y_min_mm':bb.YMin,'remaining_material_mm3':overlap})
    # Compare each wall's net volume against its dimensions minus its holes.
    for idx,o in enumerate(outputs):
        side=['south','north','west','east'][idx%4]
        stu=idx>=4; w=PARAMS['width']; l=PARAMS['length']; t=PARAMS['wall_thickness']; st=PARAMS['stucco_thickness']; h=PARAMS['wall_height']
        span=(w+2*st if side in ['south','north'] else l) if stu else (w if side in ['south','north'] else l-2*t)
        area=span*h
        for src in PARAMS['openings']:
            if src['side']==side:
                oh=PARAMS['window_height'] if src['type']=='window' else PARAMS['garage_door_height'] if src['type']=='garage' else PARAMS['door_height']
                area-=src['width']*oh
        assert near(o.Shape.Volume,area*(st if stu else t)*INCH**3),o.Name+' volume mismatch'
    for a in range(len(outputs)):
        for b in range(a): assert outputs[a].Shape.common(outputs[b].Shape).Volume<1e-4,'Overlapping wall layers'
    camera=Gui.activeDocument().activeView().getCamera()
    assert 'Camera' in camera
    return {'shapes':shapes,'openings':openings,'non_overlapping_layers':True,'analytical_volumes_match':True,'gui_visibility':True,'saved_camera':camera}

try:
    targets=['Existing-Garage.FCStd','Proposed-Garage.FCStd','Existing-Garage.step','validation.json','visible-mesh.json','agent-result.json']
    occupied=[x for x in targets if (ROOT/x).exists()]
    if occupied: raise RuntimeError('Refusing to overwrite prior outputs: '+', '.join(occupied))
    Gui.showMainWindow()
    for name,filename in [('ExistingGarage','Existing-Garage.FCStd'),('ProposedGarage','Proposed-Garage.FCStd')]:
        d,s,cells,outputs,cutters=build(name)
        check=inspect(d,outputs,cutters)
        oldx=outputs[3].Shape.BoundBox.XMax; oldopening=cutters[1].Shape.BoundBox.XMin
        s.set(cells['Width'],str(PARAMS['width']+1)+' in'); d.recompute()
        assert near(outputs[3].Shape.BoundBox.XMax-oldx,INCH)
        assert near(cutters[1].Shape.BoundBox.XMin-oldopening,INCH)
        assert all(o.Shape.isValid() for o in outputs)
        s.set(cells['Width'],str(PARAMS['width'])+' in'); d.recompute()
        assert near(outputs[3].Shape.BoundBox.XMax,oldx)
        check=inspect(d,outputs,cutters)
        check['parameter_expression_edit_check']={'alias':'Width','delta_inches':1,'east_wall_shift_mm':25.4,'south_opening_shift_mm':25.4,'restored':True}
        set_view()
        d.recompute(); d.saveAs(str(ROOT/filename))
        if name=='ExistingGarage':
            Part.export(outputs,str(ROOT/'Existing-Garage.step'))
            mesh={'units':'mm','axes':{'x':'east','y':'north','z':'up'},'objects':[]}
            for o in outputs:
                verts,triangles=o.Shape.tessellate(0.5)
                mesh['objects'].append({'name':o.Name,'label':o.Label,'color':list(o.ViewObject.ShapeColor),'vertices':[[v.x,v.y,v.z] for v in verts],'triangles':[list(t) for t in triangles]})
            (ROOT/'visible-mesh.json').write_text(json.dumps(mesh))
        onames=[o.Name for o in outputs]; cnames={i:o.Name for i,o in cutters.items()}
        App.closeDocument(d.Name)
        d=App.openDocument(str(ROOT/filename)); App.setActiveDocument(d.Name)
        outputs=[d.getObject(n) for n in onames]; cutters={i:d.getObject(n) for i,n in cnames.items()}
        reopened=inspect(d,outputs,cutters)
        assert all(o.TypeId in ['Part::Cut','Part::Box'] for o in outputs)
        assert any(o.ExpressionEngine for o in d.Objects if o.TypeId=='Part::Box')
        check['native_reopen_success']=True; check['reopened_gui_visibility']=reopened['gui_visibility']; check['reopened_camera']=reopened['saved_camera']
        check['final_visible_objects']=[o.Name for o in outputs]
        check['only_final_geometry_visible']=all(not o.ViewObject.Visibility for o in d.Objects if o.TypeId in ['Part::Box','Part::Cut'] and o not in outputs)
        assert check['only_final_geometry_visible']
        validation['documents'][filename]=check
        App.closeDocument(d.Name)
    step=Part.Shape(); step.read(str(ROOT/'Existing-Garage.step'))
    assert step.isValid() and len(step.Solids)==8
    validation['step']={'valid':True,'solids':len(step.Solids),'volume_mm3':step.Volume}
    (ROOT/'validation.json').write_text(json.dumps(validation,indent=2)+'\n')
    artifacts=['generator.py','existing-parameters.json','Existing-Garage.FCStd','Proposed-Garage.FCStd','Existing-Garage.step','visible-mesh.json','validation.json','README.md']
    for f in artifacts:
        assert (ROOT/f).stat().st_size>0,f
    for f in ['visible-mesh.json','validation.json']: json.loads((ROOT/f).read_text())
    RESULT.update(status='complete',artifact_paths=[str(ROOT/f) for f in artifacts],summary='Two independent native editable walls-only FreeCAD files built and reopened with visible geometry and isometric cameras. Dimensions, holes, volume, layer separation and restored expression edit checked. STEP and mesh exported; no roof or proposed design added.')
except Exception:
    RESULT['errors'].append(traceback.format_exc()); RESULT['summary']='Build or validation failed; inspect errors and partial artifacts.'
finally:
    (ROOT/'agent-result.json').write_text(json.dumps(RESULT,indent=2)+'\n')
    assert json.loads((ROOT/'agent-result.json').read_text())==RESULT
    print(json.dumps(RESULT,indent=2),flush=True)
    sys.stdout.flush(); sys.stderr.flush()
    os._exit(0 if RESULT['status']=='complete' else 1)
