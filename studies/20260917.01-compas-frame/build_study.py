"""Rebuild a COMPAS experiment from existing, explicitly separate study revisions.

Run from any directory with ../.venv/bin/python build_study.py.
All renderers consume the JSON-reloaded COMPAS objects, never the source meshes.
"""
from pathlib import Path
import copy
import hashlib
import json
import math
import os

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
OUT = HERE / 'output'
os.environ.setdefault('MPLCONFIGDIR', str(HERE / '.cache'))
os.environ.setdefault('XDG_CACHE_HOME', str(HERE / '.cache'))
import compas
from compas.data import json_dump, json_load
from compas.datastructures import Graph, Mesh
from compas.geometry import Frame, Line, Point, Polygon, Transformation, Translation
from compas_model.models import Model
from compas_model.elements import ColumnElement
from geometry_types import MeshElement
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon as Patch
from matplotlib.backends.backend_pdf import PdfPages
from scipy.spatial import ConvexHull
import numpy as np
import plotly.graph_objects as go

BLUE = '#235f87'
TEAL = '#18877e'
ORANGE = '#bd7137'
INK = '#283842'
SOURCE_PATHS = {
    'plan': 'studies/20260915.04-floor-plan-setbacks/floor-plan-study-basis.json',
    'parameters': 'data/model/parameters.json',
    'register': 'studies/20260908.01-structural-design/framing-member-register.json',
    'legacy_mesh': 'render/20260907.02-garage-model/garage-model.json',
}


def load_sources():
    return {k: json.loads((ROOT / p).read_text()) for k, p in SOURCE_PATHS.items()}


def polygon2(points, name):
    return Polygon([[x, y, 0] for x, y in points], name=name)


def rectangle(x, y, w, h, name):
    return polygon2([(x, y), (x+w, y), (x+w, y+h), (x, y+h)], name)


def box_mesh(x, y, z, w, d, h, name):
    if min(w, d, h) <= 0:
        raise ValueError(f'{name}: nonpositive box dimension')
    vertices = [[x,y,z],[x+w,y,z],[x+w,y+d,z],[x,y+d,z],
                [x,y,z+h],[x+w,y,z+h],[x+w,y+d,z+h],[x,y+d,z+h]]
    return Mesh.from_vertices_and_faces(vertices, [[0,3,2,1],[4,5,6,7],
        [0,1,5,4],[1,2,6,5],[2,3,7,6],[3,0,4,7]])


def build():
    s = load_sources()
    p, b, r, legacy = (s[k] for k in ('parameters','plan','register','legacy_mesh'))
    if p['units'] != 'inches' or b['units'] != 'inches' or r['units'] != 'inches':
        raise ValueError('Unexpected source units')
    if legacy['units'] != 'meters':
        raise ValueError('Legacy mesh conversion expects meters')
    model = Model(name='Garage COMPAS trial: source revisions kept separate')
    data = {'format_version': 1, 'units': 'inches', 'model': model,
            'coordinates': 'X east, Y north, Z up; existing exterior SW corner; floor Z=0',
            'sources': {k: {'path': path, 'sha256': hashlib.sha256((ROOT/path).read_bytes()).hexdigest()}
                        for k,path in SOURCE_PATHS.items()},
            'plan': {'columns': {}, 'outlines': {}, 'walls': [], 'openings': [], 'references': {}},
            'elements': {}, 'annotations': [], 'legacy_graph': Graph(name='Registered reference endpoints'),
            'source_basis': b, 'legacy_basis': legacy['basis']}

    def add_mesh(key, mesh, kind, layer, **meta):
        el = model.add_element(MeshElement(geometry=mesh, name=key))
        data['elements'][key] = dict(guid=str(el.guid), kind=kind, layer=layer, **meta)

    # Store floor-plan locations on a drawing plane, with no invented column top elevation.
    for c in b['columns']:
        w = b['column_symbol_width']
        data['plan']['columns'][c['id']] = dict(point=Point(c['x'],c['y'],0),
            footprint=rectangle(c['x']-w/2,c['y']-w/2,w,w,c['id']),
            width=w, depth=w, base_elevation=None, top_elevation=None,
            role='proposed column', size_basis='source plan symbol; not a selected section', source='plan')
    for c in b['east_wall_posts']:
        data['plan']['columns'][c['id']] = dict(
            point=Point(c['x']+c['width']/2,c['y']+c['depth']/2,0),
            footprint=rectangle(c['x'],c['y'],c['width'],c['depth'],c['id']),
            width=c['width'],depth=c['depth'],base_elevation=None,top_elevation=None,
            role=c['option'],size_basis='source plan symbol',source='plan')
    for key in ('upper_structure_outline','roof_outline','loft_outline'):
        data['plan']['outlines'][key] = polygon2(b[key], key)
    data['plan']['outlines']['extension_option'] = polygon2(b['possible_ground_floor_extension']['path'], 'Extension option')
    w, length = p['width'], p['length']
    refs = data['plan']['references']
    refs['east_property'] = Line([b['east_property_x'],-75,0],[b['east_property_x'],b['north_property_y']+20,0])
    refs['north_property'] = Line([-55,b['north_property_y'],0],[b['east_property_x']+15,b['north_property_y'],0])
    refs['south_beam_center'] = Line([-36,b['south_beam_centerline_y'],0],[b['east_truss_outside_edge_x'],b['south_beam_centerline_y'],0])
    refs['T1_support'] = Line([-36,69.75,0],[211.5,69.75,0])
    refs['B2_support'] = Line([-36,185,0],[211.5,185,0])
    refs['B3_reference'] = Line([0,249,0],[211.5,249,0])
    east = {c['id']:c for c in b['east_wall_posts']}
    refs['east_overhead_beam'] = Line([east['E-S']['x']+2,east['E-S']['y'],0],
        [east['E-N']['x']+2,east['E-N']['y']+east['E-N']['depth'],0])
    for key in data['plan']['columns']:
        data['annotations'].append({'target':key,'text':key,'view':'plan'})

    # Wall pieces include the real opening gaps, sills and headers from parameters.json.
    # Horizontal offsets are measured from the east end, as in the existing renderer.
    for side in ('south','north','west','east'):
        thickness = p['wall_'+side]
        horizontal = side in ('south','north')
        start, end = (0,w) if horizontal else (p['wall_south'],length-p['wall_north'])
        openings = []
        for o in p['openings']:
            if o['side'] != side:
                continue
            a = w-o['offset']-o['width'] if horizontal else o['offset']
            sill = p['window_sill'] if o['type']=='window' else 0
            height = p['window_height'] if o['type']=='window' else p['garage_door_height'] if o['type']=='garage' else p['door_height']
            openings.append((a,a+o['width'],sill,sill+height,o))
        def wall_piece(a, end_at, z, h, suffix, show_plan=True):
            if end_at-a <= 0 or h <= 0:
                return
            x,y,dx,dy = (a,0 if side=='south' else length-thickness,end_at-a,thickness) if horizontal else (0 if side=='west' else w-thickness,a,thickness,end_at-a)
            key = f'wall:{side}:{suffix}'
            mesh = box_mesh(x,y,z,dx,dy,h,key)
            add_mesh(key,mesh,'wall','existing',source='parameters')
            if show_plan:
                data['plan']['walls'].append(rectangle(x,y,dx,dy,key))
        cursor = start
        for i,(a,bb,sill,head,o) in enumerate(sorted(openings)):
            wall_piece(cursor,a,0,p['wall_height'],f'piece{i}')
            wall_piece(a,bb,0,sill,f'sill{i}',False)
            wall_piece(a,bb,head,p['wall_height']-head,f'header{i}',False)
            xy = ([a,(thickness/2 if side=='south' else length-thickness/2),0],
                  [bb,(thickness/2 if side=='south' else length-thickness/2),0]) if horizontal else ([thickness/2,a,0],[thickness/2,bb,0])
            data['plan']['openings'].append(dict(name=o['name'],kind=o['type'],line=Line(*xy)))
            cursor = bb
        wall_piece(cursor,end,0,p['wall_height'],'last')

    # Parametric COMPAS Model ColumnElements recreate OLD source columns exactly.
    # ColumnElement extends from local Z=0 to height.
    h = legacy['basis']['common_member_bottom']
    for c in r['posts']:
        name = 'legacy:column:'+c['id']
        f = Frame([c['x'],c['y'],0],[1,0,0],[0,1,0])
        el = model.add_element(ColumnElement(width=4,depth=4,height=h,
            transformation=Transformation.from_frame(f),name=name))
        data['elements'][name] = dict(guid=str(el.guid),kind='column',layer='legacy columns',
            source='register + legacy mesh',size_basis='old visualization placeholder')
    for idx,o in enumerate(legacy['objects']):
        if o['group'] != 'frame' or o['material'] not in ('truss','beam'):
            continue
        mesh = Mesh.from_vertices_and_faces([[v/.0254 for v in xyz] for xyz in o['vertices']],o['faces'])
        key = f'legacy:{idx:03d}:{o["name"]}'
        assembly = next((t for t in ('T-S','T1','T-W','T-E','T-N') if o['name'].startswith(t+' ')), 'beams')
        if o['name']=='French door header':
            assembly='T-W'
        add_mesh(key,mesh,o['material'],'legacy framing',source='legacy_mesh',assembly=assembly,source_name=o['name'],source_index=idx)
    graph = data['legacy_graph']
    for m in r['members']:
        a,bp = [m['start']+[m['bottom_elevation']],m['end']+[m['bottom_elevation']]]
        # Separate reference nodes intentionally: coincident ends do not prove a joint.
        for suffix,xyz in [('a',a),('b',bp)]:
            graph.add_node(m['id']+':'+suffix,x=xyz[0],y=xyz[1],z=xyz[2])
        graph.add_edge(m['id']+':a',m['id']+':b',member_id=m['id'],reference='bottom elevation line',
            description=m['description'],joint_status='not inferred')
    return data


def element_meshes(data):
    return {el.name: el.modelgeometry for el in data['model'].elements()}


def validate(data):
    errors=[]
    cols=data['plan']['columns']
    for label in data['annotations']:
        if label['target'] not in cols:
            errors.append('Dangling annotation: '+label['target'])
    for key,c in cols.items():
        if not all(math.isfinite(v) for v in c['point']):
            errors.append('Nonfinite coordinate: '+key)
        if min(c['width'],c['depth'])<=0:
            errors.append('Nonpositive section: '+key)
        center=c['footprint'].centroid
        if center.distance_to_point(c['point'])>1e-7:
            errors.append('Point and footprint disagree: '+key)
    for (a,bb),attr in data['legacy_graph'].edges(data=True):
        pa=data['legacy_graph'].node_coordinates(a)
        pb=data['legacy_graph'].node_coordinates(bb)
        if Line(pa,pb).length<1e-8:
            errors.append('Zero-length member: '+attr['member_id'])
    for key,mesh in element_meshes(data).items():
        Mesh.validate_data(mesh.__data__)
        if not mesh.is_valid() or not mesh.is_closed():
            errors.append('Invalid or open solid mesh: '+key)
        if not all(math.isfinite(v) for xyz in mesh.vertices_attributes('xyz') for v in xyz):
            errors.append('Nonfinite mesh: '+key)
    b=data['source_basis']
    n1,n2=cols['N1']['point'],cols['N2']['point']
    if abs(n2.x-n1.x-b['north_door_bay']['center_spacing_in'])>1e-7 or abs(n1.y-n2.y)>1e-7:
        errors.append('North door bay no longer matches source center spacing/alignment')
    for key in ('W1','S1','S2'):
        if abs(cols[key]['point'].y-b['south_support_centerlines_y'][key])>1e-7:
            errors.append('South support row differs from source: '+key)
    if errors:
        raise ValueError('\n'.join(errors))
    return len(data['elements'])


def move_plan_column(data, key, dx=0, dy=0):
    """A single edit moves the point and footprint; labels reference the stable ID."""
    col=data['plan']['columns'][key]
    t=Translation.from_vector([dx,dy,0])
    col['point'].transform(t)
    col['footprint'].transform(t)


def checks(data, original):
    result={'passed':[],'expected_failures':{},'source_differences':[]}
    validate(data)
    result['passed'].append('Reloaded COMPAS objects and validated all solid meshes')
    before,after=element_meshes(original),element_meshes(data)
    for key in before:
        # Pretty JSON sorts dictionary keys lexically; compare stable vertex/face IDs,
        # not iteration order (0,1,10,... after reload).
        vertex_keys=sorted(before[key].vertices())
        if set(vertex_keys)!=set(after[key].vertices()):
            raise ValueError('Roundtrip vertex IDs changed: '+key)
        if not np.allclose([before[key].vertex_coordinates(v) for v in vertex_keys],
                           [after[key].vertex_coordinates(v) for v in vertex_keys],rtol=0,atol=1e-9):
            raise ValueError('Roundtrip geometry changed: '+key)
        if {f:before[key].face_vertices(f) for f in before[key].faces()}!={f:after[key].face_vertices(f) for f in after[key].faces()}:
            raise ValueError('Roundtrip topology changed: '+key)
    result['passed'].append('JSON save/reload preserves element vertices and face topology')
    for key,c in original['plan']['columns'].items():
        if c['point'].distance_to_point(data['plan']['columns'][key]['point'])>1e-9:
            raise ValueError('Plan coordinate changed in roundtrip')
    result['passed'].append('JSON save/reload preserves plan column positions')
    source=load_sources()
    for key,meta in data['elements'].items():
        if 'source_index' in meta:
            expected=np.array(source['legacy_mesh']['objects'][meta['source_index']]['vertices'])/.0254
            if not np.allclose([after[key].vertex_coordinates(i) for i in range(len(expected))],expected,rtol=0,atol=1e-9):
                raise ValueError('Imported source coordinates differ: '+key)
    result['passed'].append('Imported truss/beam vertices match original meters converted to inches')
    for c in source['register']['posts']:
        xyz=np.array(after['legacy:column:'+c['id']].vertices_attributes('xyz'))
        if not np.allclose(xyz.min(0),[c['x']-2,c['y']-2,0]) or not np.allclose(xyz.max(0),[c['x']+2,c['y']+2,data['legacy_basis']['common_member_bottom']]):
            raise ValueError('Parametric column has incorrect bounds')
    result['passed'].append('Parametric ColumnElement columns match source bounds')
    # Exercise a successful programmatic edit, then deliberately invalid examples.
    d=copy.deepcopy(data); move_plan_column(d,'WB3',dy=12); validate(d)
    result['passed'].append('Programmatic WB3 move updates point and footprint together')
    def reject(name, mutate):
        d=copy.deepcopy(data);mutate(d)
        try:validate(d)
        except ValueError as exc:result['expected_failures'][name]=str(exc)
        else:raise AssertionError('Bad model accepted: '+name)
    reject('missing label target',lambda d:d['annotations'].append({'target':'MISSING'}))
    reject('negative section',lambda d:d['plan']['columns']['W1'].update(width=-4))
    reject('misplaced north support',lambda d:move_plan_column(d,'N1',dx=12))
    def collapse(d):
        g=d['legacy_graph']; a,bb=next(iter(g.edges()))
        g.node_attributes(bb,'xyz',g.node_coordinates(a))
    reject('zero-length member',collapse)
    for c in source['register']['posts']:
        now=data['plan']['columns'][c['id']]['point']
        if abs(now.x-c['x'])+abs(now.y-c['y'])>1e-7:
            result['source_differences'].append({'id':c['id'],'old':[c['x'],c['y']],
                'current':[now.x,now.y],'delta':[now.x-c['x'],now.y-c['y']]})
    result['notes']=['The current floor plan and historical trusses are separate revisions.',
        'Current plan column Z=0 is a drawing plane; top/base elevations remain null.',
        'Historical 4-inch column sections are visualization placeholders.',
        'South beam center Y=-64 differs from current column centers Y=-66 by 2 inches.',
        'Validation checks geometry/data and selected source constraints; no load analysis performed.',
        'Mesh validity does not establish self-intersection freedom or structural adequacy.']
    return result


def decorate(ax):
    ax.set_aspect('equal');ax.set_xlabel('East / X (inches)');ax.set_ylabel('North / Y (inches)')
    ax.grid(alpha=.13);ax.spines[['top','right']].set_visible(False)


def draw_plan(data):
    fig,ax=plt.subplots(figsize=(12,13))
    plan=data['plan'];b=data['source_basis']
    fig.suptitle('GARAGE / COMPAS FLOOR-PLAN STUDY',x=.1,ha='left',fontsize=19,weight='bold',color=INK)
    ax.set_title('Current plan coordinates · imported as COMPAS points, lines and polygons',loc='left',fontsize=10,pad=16)
    for key,c,fill,style in [('extension_option',ORANGE,.12,'--'),('loft_outline',TEAL,.07,'--'),
                            ('roof_outline',BLUE,0,'--'),('upper_structure_outline',BLUE,0,'-')]:
        pts=np.array(plan['outlines'][key].points)[:,:2]
        ax.add_patch(Patch(pts,facecolor=c if fill else 'none',alpha=fill if fill else 1,edgecolor='none'))
        closed=np.vstack([pts,pts[0]])
        ax.plot(*closed.T,color=c,lw=1.7,ls=style,label=key.replace('_',' '))
    for wall in plan['walls']:
        ax.add_patch(Patch(np.array(wall.points)[:,:2],fc='#d5dbdf',ec='#929da5',lw=.6))
    for o in plan['openings']:
        xy=np.array([o['line'].start,o['line'].end])[:,:2]
        ax.plot(*xy.T,color='#7d9da6',lw=2 if o['kind']=='window' else .7,ls='-' if o['kind']=='window' else ':')
    for name,line in plan['references'].items():
        xy=np.array([line.start,line.end])[:,:2]
        ax.plot(*xy.T,color=INK if 'property' in name else TEAL,lw=1 if 'property' in name else .8,ls='--')
        if name in ('T1_support','B2_support','B3_reference'):
            ax.text(40,line.start.y-8,name.replace('_',' '),color=TEAL,fontsize=8)
    for key,c in plan['columns'].items():
        ax.add_patch(Patch(np.array(c['footprint'].points)[:,:2],fc=ORANGE if key.startswith('E-') else INK))
        point=c['point'];dx=-9 if key.startswith('W') and key!='WB3' else 7
        dy=8 if key in ('WB3','E-M') else -10 if key.startswith('N') else 5
        ax.text(point.x+dx,point.y+dy,key+(' (B)' if key=='E-M' else ''),fontsize=9,ha='right' if dx<0 else 'left',color=INK)
    def dim(a,bb,text,offset=(0,4)):
        ax.annotate('',xy=a,xytext=bb,arrowprops=dict(arrowstyle='|-|',color=INK,lw=.8))
        ax.text((a[0]+bb[0])/2+offset[0],(a[1]+bb[1])/2+offset[1],text,ha='center',fontsize=9,
                bbox=dict(facecolor='white',edgecolor='none',pad=2))
    n1=plan['columns']['N1']['point'];n2=plan['columns']['N2']['point']
    dim((n1.x,224),(n2.x,224),'192 in / 16 ft centers')
    dim((b['east_truss_outside_edge_x'],155),(b['east_property_x'],155),'48 in',offset=(0,5))
    dim((155,b['north_wall_outside_face_y']),(155,b['north_property_y']),'60 in',offset=(-17,0))
    dim((0,-89),(b['existing_width'],-89),'Existing width 249.5 in')
    ax.text(96,122,'LOFT FOOTPRINT',ha='center',color=TEAL,fontsize=12)
    ax.text(90,34,'EXISTING GARAGE',ha='center',color='#79858e',fontsize=11)
    ax.text(72,340,'NORTH / ALLEY PROPERTY LINE',fontsize=9,color=INK)
    ax.set_xlim(-65,296);ax.set_ylim(-105,352);decorate(ax)
    ax.legend(loc='lower left',fontsize=8,framealpha=.95)
    fig.text(.1,.025,'Current plan source: floor-plan-study-basis.json. E-M is option B only.\nColumn squares show source symbols; current heights are unresolved. Orange extension remains an option.',fontsize=9,color='#66747e')
    fig.subplots_adjust(left=.1,right=.95,top=.92,bottom=.09)
    for ext in ('png','svg','pdf'):fig.savefig(OUT/f'floor-plan.{ext}',dpi=160)
    return fig


def draw_trusses(data):
    meshes=element_meshes(data)
    fig,axs=plt.subplots(3,2,figsize=(15,12))
    fig.suptitle('TRUSSES / EXISTING SOURCE GEOMETRY IN COMPAS',fontsize=18,weight='bold',color=INK)
    for ax,name in zip(axs.flat,('T-S','T1','T-W','T-E','T-N')):
        axis=1 if name in ('T-W','T-E') else 0
        for key,meta in data['elements'].items():
            if meta.get('assembly')!=name:continue
            pts=np.array(meshes[key].vertices_attributes('xyz'))[:,[axis,2]]
            pts=np.unique(np.round(pts,8),axis=0)
            if len(pts)<3:continue
            hull=ConvexHull(pts)
            ax.add_patch(Patch(pts[hull.vertices],fc=ORANGE,ec=ORANGE,lw=.3))
        ax.autoscale_view();ax.set_aspect('equal');ax.grid(alpha=.15)
        ax.set_title(name,loc='left',fontsize=13,weight='bold');ax.set_xlabel(('Y' if axis else 'X')+' (inches)');ax.set_ylabel('Z above floor (inches)')
    axs[2,1].axis('off')
    axs[2,1].text(0,.85,'Exact mesh import, with unit conversion\n\nFive original truss assemblies.\nNo rescaling to newer column positions.\n\nThese are earlier concept layouts;\nthe current plan is a separate source revision.\n\nAll views are drawn after COMPAS JSON reload.',va='top',fontsize=12,linespacing=1.6,color=INK)
    fig.tight_layout(rect=(0,0,1,.95))
    for ext in ('png','svg','pdf'):fig.savefig(OUT/f'truss-elevations.{ext}',dpi=150)
    return fig


def interactive(data):
    meshes=element_meshes(data);fig=go.Figure()
    groups={}
    for key,meta in data['elements'].items():
        group=meta.get('assembly',meta['layer'])
        groups.setdefault(group,[]).append(key)
    for group,keys in groups.items():
        vertices=[];triangles=[];labels=[]
        for key in keys:
            mesh=meshes[key];vs,fs=mesh.to_vertices_and_faces();off=len(vertices)
            vertices.extend(vs);labels.extend([key]*len(vs))
            # Source beam end caps can be concave I profiles: triangulate by ear clipping.
            from compas.geometry import earclip_polygon
            for face in fs:
                if len(face)==3:triangles.append([off+i for i in face]);continue
                for tri in earclip_polygon(Polygon([vs[i] for i in face])):
                    triangles.append([off+face[i] for i in tri])
        xyz=np.array(vertices);tri=np.array(triangles)
        color='#aeb9c1' if group=='existing' else BLUE if group in ('beams','legacy columns') else ORANGE
        fig.add_trace(go.Mesh3d(x=xyz[:,0],y=xyz[:,1],z=xyz[:,2],i=tri[:,0],j=tri[:,1],k=tri[:,2],
            color=color,opacity=.32 if group=='existing' else 1,name=group,showlegend=True,
            text=labels,hovertemplate='%{text}<br>X %{x:.2f} · Y %{y:.2f} · Z %{z:.2f} in<extra></extra>'))
    for key,color in [('upper_structure_outline',BLUE),('loft_outline',TEAL),('roof_outline','#7797ab')]:
        pts=list(data['plan']['outlines'][key].points);pts.append(pts[0]);xyz=np.array(pts)
        fig.add_trace(go.Scatter3d(x=xyz[:,0],y=xyz[:,1],z=xyz[:,2],mode='lines',line=dict(color=color,width=5,dash='dash'),name='Current plan: '+key.replace('_outline','')))
    cols=data['plan']['columns'];xyz=np.array([c['point'] for c in cols.values()])
    fig.add_trace(go.Scatter3d(x=xyz[:,0],y=xyz[:,1],z=xyz[:,2],mode='markers+text',text=list(cols),
        textposition='bottom center',marker=dict(size=4,color=TEAL),name='Current plan columns (drawing plane)',
        hovertemplate='%{text}<br>X %{x:.2f} · Y %{y:.2f} in<br>Height unresolved<extra></extra>'))
    fig.update_layout(title=dict(text='Garage / COMPAS model inspection<br><sup>Earlier trusses + earlier columns; current plan shown at Z=0 for comparison · inches</sup>',x=.04),
        scene=dict(aspectmode='data',xaxis_title='X / east (in)',yaxis_title='Y / north (in)',zaxis_title='Z / up (in)',
            camera=dict(eye=dict(x=1.5,y=-1.9,z=1.3))),
        legend=dict(title='Click a layer to hide/show',x=1.01,y=1),margin=dict(l=15,r=270,b=15,t=85),
        paper_bgcolor='#fafbfc',height=850)
    fig.write_html(OUT/'model-3d.html',include_plotlyjs=True,full_html=True,
        config={'displaylogo':False,'responsive':True})


def main():
    OUT.mkdir(exist_ok=True)
    data=build();validate(data)
    json_dump(data,OUT/'garage.compas.json',pretty=True)
    loaded=json_load(OUT/'garage.compas.json')
    results=checks(loaded,data)
    results['counts']={'model_elements':len(loaded['elements']),'plan_columns':len(loaded['plan']['columns']),
        'reference_members':loaded['legacy_graph'].number_of_edges(),
        'parametric_columns':sum(isinstance(e,ColumnElement) for e in loaded['model'].elements())}
    (OUT/'validation.json').write_text(json.dumps(results,indent=2)+'\n')
    figs=[draw_plan(loaded),draw_trusses(loaded)]
    with PdfPages(OUT/'study.pdf') as pdf:
        for fig in figs:pdf.savefig(fig)
    for fig in figs:plt.close(fig)
    interactive(loaded)
    print(json.dumps({'compas':compas.__version__,**results},indent=2))


if __name__=='__main__':main()
