"""Native roof tail Boolean construction. No external runtime proxy is installed.
Imported by roof-generator.py; FCStd remains editable without this module.
"""

def apply_tail_cuts(App,doc,member_info):
    replacements={};hidden=[]
    for info in member_info:
        if info['kind']=='ridge': continue
        name=info['name'];assembly=doc.getObject(name);axis=doc.getObject(name+'Axis');old=doc.getObject(info['output'])
        if info.get('pre_tail_output'): raise RuntimeError('Tail cuts already present for '+name)
        if info['kind']=='hip':
            sides=(['South'] if 'S' in name[3:] else ['North'])+(['West'] if 'W' in name[3:] else ['East'])
        else: sides=[next(s for s in ['South','North','West','East'] if name.startswith(s))]
        current=old
        for side in sides:
            # Exact exterior-wall half planes, intersected with z below soffit top.
            # Two overlapping tools cover the hip corner without trimming inside the core footprint.
            r='RoofParameters.'
            lo='(-'+r+'EaveOffset-2*'+r+'BoardDepth)'
            xspan=r+'CoreWidth+2*'+r+'EaveOffset+4*'+r+'BoardDepth'
            yspan=r+'CoreLength+2*'+r+'EaveOffset+4*'+r+'BoardDepth'
            reach=r+'EaveOffset+2*'+r+'BoardDepth'
            if side=='South': x,y,l,w=lo,lo,xspan,reach
            elif side=='North': x,y,l,w=lo,r+'CoreLength',xspan,reach
            elif side=='West': x,y,l,w=lo,lo,reach,yspan
            else: x,y,l,w=r+'CoreWidth',lo,reach,yspan
            tool=doc.addObject('Part::Box',name+'Soffit'+side+'UndersideTool');assembly.addObject(tool);tool.Label='Hidden '+side+' soffit-top underside tool'
            tool.setExpression('Length',l);tool.setExpression('Width',w);tool.setExpression('Height','4*RoofParameters.BoardDepth')
            yaw=name+'Axis.Yaw';sx=name+'Axis.Start.x*1 mm';sy=name+'Axis.Start.y*1 mm'
            tool.setExpression('Placement.Base.x',f'cos({yaw})*(({x})-{sx})+sin({yaw})*(({y})-{sy})')
            tool.setExpression('Placement.Base.y',f'-sin({yaw})*(({x})-{sx})+cos({yaw})*(({y})-{sy})')
            tool.setExpression('Placement.Base.z','RoofParameters.WallTop-'+name+'Axis.Start.z*1 mm-4*RoofParameters.BoardDepth')
            tool.Placement.Rotation=App.Rotation(App.Vector(0,0,1),0);tool.setExpression('Placement.Rotation.Angle','-'+yaw)
            cut=doc.addObject('Part::Cut',name+'Soffit'+side+'Trimmed');assembly.addObject(cut);cut.Base=current;cut.Tool=tool;cut.Refine=True
            hidden.extend([current,tool]);current=cut
        for side in sides:
            # World-aligned half-space boxes expressed in the member's local yaw frame.
            r='RoofParameters.'
            lo='(-'+r+'EaveOffset-2*'+r+'BoardDepth)'
            xspan=r+'CoreWidth+2*'+r+'EaveOffset+4*'+r+'BoardDepth'
            yspan=r+'CoreLength+2*'+r+'EaveOffset+4*'+r+'BoardDepth'
            depth=r+'FasciaThickness+2*'+r+'BoardDepth'
            if side=='South': x,y,l,w=lo,lo,xspan,depth
            elif side=='North': x,y,l,w=lo,r+'CoreLength+'+r+'SoffitOffset',xspan,depth
            elif side=='West': x,y,l,w=lo,lo,depth,yspan
            else: x,y,l,w=r+'CoreWidth+'+r+'SoffitOffset',lo,depth,yspan
            t=doc.addObject('Part::Box',name+'Fascia'+side+'Tool');assembly.addObject(t);t.Label='Hidden '+side+' fascia inside-face trim'
            t.setExpression('Length',l);t.setExpression('Width',w);t.setExpression('Height',r+'RoofDelta+8*'+r+'BoardDepth')
            yaw=name+'Axis.Yaw';sx=name+'Axis.Start.x*1 mm';sy=name+'Axis.Start.y*1 mm'
            t.setExpression('Placement.Base.x',f'cos({yaw})*(({x})-{sx})+sin({yaw})*(({y})-{sy})')
            t.setExpression('Placement.Base.y',f'-sin({yaw})*(({x})-{sx})+cos({yaw})*(({y})-{sy})')
            t.setExpression('Placement.Base.z',r+'WallTop-4*'+r+'BoardDepth-'+name+'Axis.Start.z*1 mm')
            t.Placement.Rotation=App.Rotation(App.Vector(0,0,1),0);t.setExpression('Placement.Rotation.Angle','-'+yaw)
            c=doc.addObject('Part::Cut',name+'Fascia'+side+'Trimmed');assembly.addObject(c);c.Base=current;c.Tool=t;c.Refine=True
            hidden.extend([current,t]);current=c
        current.Label=old.Label+' — soffit/fascia clearance';current.ViewObject.ShapeColor=old.ViewObject.ShapeColor
        current.ViewObject.Visibility=True
        info['pre_tail_output']=old.Name;info['output']=current.Name
        replacements[old.Name]=current
    doc.recompute()
    for obj in hidden:obj.ViewObject.Visibility=False
    global_replacements,global_hidden=apply_global_datum(App,doc,member_info)
    replacements={name:global_replacements.get(obj.Name,obj) for name,obj in replacements.items()}
    hidden.extend(global_hidden)
    return replacements,hidden


def apply_global_datum(App,doc,member_info):
    """Clip every non-ridge member below wall-top globally, including over walls.
    Each horizontal tool covers the complete member in its native yaw frame.
    Its world bottom is z=0 and its world top is the linked WallTop datum.
    """
    replacements={};hidden=[]
    for info in member_info:
        if info['kind']=='ridge':continue
        name=info['name'];old=doc.getObject(info['output']);assembly=doc.getObject(name)
        if doc.getObject(name+'GlobalDatumTool'):raise RuntimeError('Global datum cut already exists for '+name)
        tool=doc.addObject('Part::Box',name+'GlobalDatumTool');assembly.addObject(tool);tool.Label='Hidden full-member cut below wall-top datum'
        tool.setExpression('Length',name+'Axis.Run+4*RoofParameters.BoardDepth')
        tool.setExpression('Width','RoofParameters.BoardThickness+4*RoofParameters.BoardDepth')
        tool.setExpression('Height','RoofParameters.WallTop')
        tool.setExpression('Placement.Base.x','-2*RoofParameters.BoardDepth')
        tool.setExpression('Placement.Base.y','-RoofParameters.BoardThickness/2-2*RoofParameters.BoardDepth')
        tool.setExpression('Placement.Base.z','-'+name+'Axis.Start.z*1 mm')
        cut=doc.addObject('Part::Cut',name+'GlobalDatumOutput');assembly.addObject(cut);cut.Base=old;cut.Tool=tool;cut.Refine=True
        cut.Label=old.Label+' — global 98.5 in underside datum';cut.ViewObject.ShapeColor=old.ViewObject.ShapeColor;cut.ViewObject.Visibility=True
        info['pre_global_output']=old.Name;info['output']=cut.Name
        replacements[old.Name]=cut;hidden.extend([old,tool])
    doc.recompute()
    for obj in hidden:obj.ViewObject.Visibility=False
    return replacements,hidden


def global_shape(obj):
    shape=obj.Shape.copy();shape.Placement=obj.getGlobalPlacement();return shape


def validate_tail_cuts(doc,member_info):
    soffits=[global_shape(doc.getObject('Soffit'+s)) for s in ['South','North','West','East']]
    fascias=[global_shape(doc.getObject('Fascia'+s)) for s in ['South','North','West','East']]
    import FreeCAD as App, Part
    datum=soffits[0].BoundBox.ZMax
    results=[]
    for info in member_info:
        if info['kind']=='ridge':continue
        o=doc.getObject(info['output']);shape=global_shape(o)
        assert shape.isValid() and len(shape.Solids)==1,(o.Name,'invalid final tail')
        soffit_volumes=[shape.common(s).Volume for s in soffits]
        fascia_volumes=[shape.common(s).Volume for s in fascias]
        assert all(v<1e-4 for v in soffit_volumes),(o.Name,'soffit collision',soffit_volumes)
        assert all(v<1e-4 for v in fascia_volumes),(o.Name,'fascia collision',fascia_volumes)
        bb=shape.BoundBox
        assert bb.ZMin>=datum-1e-6,(o.Name,'below global datum',bb.ZMin,datum)
        floor=min(-1000.0,bb.ZMin-1000.0)
        below=Part.makeBox(bb.XLength+2,bb.YLength+2,datum-floor,App.Vector(bb.XMin-1,bb.YMin-1,floor))
        below_volume=shape.common(below).Volume
        assert below_volume<1e-4,(o.Name,'material below global datum',below_volume)
        distances=[shape.distToShape(s)[0] for s in soffits]
        old=global_shape(doc.getObject(info['pre_tail_output']))
        removed=old.Volume-shape.Volume
        assert removed>1e-4 and shape.cut(old).Volume<1e-4,(o.Name,'cut must only remove material')
        results.append({'name':info['name'],'kind':info['kind'],'output':o.Name,'global_z_min_mm':bb.ZMin,'below_datum_volume_mm3':below_volume,'valid':True,'solids':1,'removed_volume_mm3':removed,'soffit_common_volumes_mm3':soffit_volumes,'fascia_common_volumes_mm3':fascia_volumes,'minimum_soffit_clearance_mm':min(distances),'visible':bool(o.ViewObject.Visibility)})
    return {'global_datum_mm':datum,'minimum_global_z_mm':min(x['global_z_min_mm'] for x in results),'maximum_below_datum_volume_mm3':max(x['below_datum_volume_mm3'] for x in results),'global_z_tolerance_mm':1e-6,'changed_member_count':len(results),'hips':sum(x['kind']=='hip' for x in results),'jacks':sum(x['kind']=='jack' for x in results),'maximum_soffit_intersection_mm3':max(v for x in results for v in x['soffit_common_volumes_mm3']),'maximum_fascia_intersection_mm3':max(v for x in results for v in x['fascia_common_volumes_mm3']),'minimum_soffit_clearance_mm':min(x['minimum_soffit_clearance_mm'] for x in results),'soffit_top_trim_inches':98.5,'members':results}
