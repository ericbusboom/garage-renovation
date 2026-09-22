"""Common plan registry -> five parametric truss families -> drawings and audits.

Current-plan coordination is a draft. Baselines reproduce the older source model.
Run: .venv/bin/python compas-study/coordinated_study.py
"""
import copy
import csv
import hashlib
import json
import math
import textwrap
from collections import Counter

import numpy as np
from compas.data import json_dump, json_load
from compas.datastructures import Graph
from compas.geometry import Line, Point, Polygon, Translation
from compas_model.models import Model
from compas_model.elements import ColumnElement
from geometry_types import MemberElement, MeshElement
from build_study import ROOT, HERE, box_mesh, build, plt, Patch, ConvexHull, go, INK, BLUE, TEAL, ORANGE
from parametric_truss import fingerprint
from matplotlib.backends.backend_pdf import PdfPages
import frame_models

OUT=HERE/'output'/'coordinated'
NAMES=('T-S','T1','T-W','T-E','T-N')


def read(path):return json.loads((ROOT/path).read_text())


def make_plan(overrides=None):
    source=read('studies/20260915.04-floor-plan-setbacks/floor-plan-study-basis.json')
    old=read('studies/20260908.01-structural-design/framing-member-register.json')
    plan={'units':'inches','supports':{},'members':{},'outlines':{},'decisions':[]}
    for c in source['columns']:
        plan['supports'][c['id']]=dict(x=c['x'],y=c['y'],width=4,depth=4,status='proposed',
            source='current floor-plan basis; center coordinates',base=None,top=None)
    for c in source['east_wall_posts']:
        plan['supports'][c['id']]=dict(x=c['x']+c['width']/2,y=c['y']+c['depth']/2,
            width=c['width'],depth=c['depth'],status=c['option'],
            source='current floor-plan basis; lower-left converted to center',base=None,top=None)
    for key,changes in (overrides or {}).items():plan['supports'][key].update(changes)
    for key,s in plan['supports'].items():
        s.update(base=0,top=98.5,elevation_basis='visualization: floor datum to common frame bottom; east-wall heights provisional' if key.startswith('E-') else
                 'concept column from floor datum to common frame bottom; footing detail unresolved')
    c=plan['supports'];west=c['W2']['x'];east=c['N2']['x'];north=c['N2']['y'];south=source['south_beam_centerline_y']
    def add(name,kind,a,b,status,basis,targets=(),bottom=98.5):
        plan['members'][name]=dict(kind=kind,line=Line([*a,0],[*b,0]),bottom=bottom,
            position_status=status,basis=basis,targets=list(targets),section=None)
    add('T-SO','beam',(c['W1']['x'],south),(c['S2']['x'],south),'draft endpoints / source axis',
        'Y=-64 retained; endpoint X from W1/S2. Source posts remain Y=-66.',('W1','S1','S2'))
    add('T-S','truss',(west,0),(east,0),'west-row correction / draft endpoints',
        'Retain Y=0; extend between far-west T-W and revised T-E.',('S3',))
    add('T-W','truss',(west,c['W1']['y']),(west,north),'user-corrected far-west location',
        'Suspended on the far-west W1-W4 column row, not above the existing wall at X=0.',('W1','W2','W3','W4'))
    add('T-E','truss',(east,south),(east,north),'derived from current supports',
        'Axis from N2/S2; ends use T-SO and north row.',('S2','S3','N2'))
    add('T-N','truss',(c['W4']['x'],north),(east,north),'draft resized',
        'North upper-wall truss uses W4/N1/N2 row; loft door remains separate from ground door.',('W4','N1','N2'))
    for name,station in [('T1',c['W2']['y']),('B2',c['W3']['y'])]:
        add(name,'truss' if name=='T1' else 'beam',(west,station),(east,station),'derived / west-row correction',
            'Station from '+('W2' if name=='T1' else 'W3')+'; continuous reference from far-west T-W to east T-E.',
            ('W2',) if name=='T1' else ('W3','WB3'))
    add('B3','beam',(west,source['existing_length']),(east,source['existing_length']),'west-row correction / draft endpoints',
        'Y=249 retained; extend to far-west T-W. Distinct from north upper truss Y=269.')
    add('B-WO','beam',(c['W1']['x'],c['W1']['y']),(c['W4']['x'],c['W4']['y']),'derived from current supports',
        'Outer west beam follows west post row.',('W1','W2','W3','W4'))
    for name,support in [('O2','W2'),('O3','W3')]:
        add(name,'subsegment reference',(c[support]['x'],c[support]['y']),(0,c[support]['y']),'absorbed into extended cross-member',
            'Historical west extension now contained within '+('T1' if name=='O2' else 'B2')+'; not a separate overlapping beam.')
        plan['members'][name]['parent']='T1' if name=='O2' else 'B2'
    add('E-OB','beam',(c['E-S']['x'],c['E-S']['y']-c['E-S']['depth']/2),
        (c['E-N']['x'],c['E-N']['y']+c['E-N']['depth']/2),'user-confirmed column-top beam',
        'Across E-S/E-N tops, level with truss bottom chords; retain plan end-face extents. 3-inch display envelope only.',
        ('E-S','E-N','E-M'),bottom=c['E-S']['top'])
    plan['beam_model']=Model(name='East overhead beam')
    m=plan['members']['E-OB'];a=m['line'].start;b=m['line'].end
    plan['beam_model'].add_element(MemberElement([a.x,a.y,m['bottom']+1.5],
        [b.x,b.y,m['bottom']+1.5],3,3,name='E-OB'))
    for support,target in [('E-S','S3'),('E-M','T-E'),('E-N','T-E')]:
        s=c[support];end=(c[target]['x'],c[target]['y']) if target in c else (east,s['y'])
        name='C-'+support.replace('-','')
        add(name,'beam',(s['x'],s['y']),end,'user-requested connection reference',
            f'{support} to {target} at column-top Z={s["top"]:g}; section and joint detail unassigned.'+
            (' E-M retains option B status.' if support=='E-M' else ''),
            (support,target) if target in c else (support,),bottom=s['top'])
        plan['members'][name].update(from_support=support,connection_to=target)
    ob=old['existing_shelter_beam']
    add('OB1','existing context beam',ob['start'],ob['end'],'historical context only',
        'Outbuilding beam outside proposed frame; elevation/supports not supplied here.',bottom=None)
    for key in ('upper_structure_outline','roof_outline','loft_outline'):
        plan['outlines'][key]=Polygon([[x,y,0] for x,y in source[key]])
    plan['source_basis']=source
    plan['roof_trial']={'start_y':south,'start_z':106.5,'plateau_z':227.25,'slope_degrees':30,
        'status':'coordination assumption: retain old roof slope/heights, anchor start to current T-SO'}
    plan['column_model']=make_columns(plan)
    plan['user_correction']='T-W belongs on the far-west column row, not above the existing west wall. Show all columns in 3D.'
    plan['decisions']=[{'id':key,**{k:v for k,v in m.items() if k in ('position_status','basis')}} for key,m in plan['members'].items()]
    return plan


def make_columns(plan):
    model=Model(name='Current support columns')
    for key,s in plan['supports'].items():
        model.add_element(ColumnElement(width=s['width'],depth=s['depth'],height=s['top']-s['base'],
            transformation=Translation.from_vector([s['x'],s['y'],s['base']]),name=key))
    return model


def roof_z(roof,s):
    return min(roof['start_z']+(s-roof['start_y'])*math.tan(math.radians(roof['slope_degrees'])),roof['plateau_z'])


def recipe(name,plan=None):
    old=read('structural-study/framing-member-register.json')
    scene=read('model-renders/garage-model.json')
    if plan:
        m=plan['members'][name];a=list(m['line'].start)[:2];b=list(m['line'].end)[:2]
        roof=plan['roof_trial'];h=m['bottom']
    else:
        m=next(m for m in old['members'] if m['id']==name);a=m['start'];b=m['end'];h=m['bottom_elevation']
        roof={'start_y':-63,'start_z':106.5,'plateau_z':227.25,'slope_degrees':30}
    axis=1 if name in ('T-W','T-E') else 0
    r={'name':name,'axis':axis,'fixed':a[1-axis],'start':a[axis],'end':b[axis],
       'bottom':h,'roof':roof,'floor':scene['basis']['floor'],'coordinated':plan is not None,
       'section_envelopes':{'chord':3,'upright':3,'web':2.5},'panels':6 if name in ('T-S','T1') else 8}
    if name in ('T-W','T-E'):
        br=roof['start_y']+(roof['plateau_z']-roof['start_z'])/math.tan(math.radians(roof['slope_degrees']))
        # Historical stations retained except support rows and the roof breakpoint.
        stations=[r['start'],0,plan['supports']['W2']['y'] if plan else 69.75,
                  br,plan['supports']['W3']['y'] if plan else 185,r['end']]
        stations+=([186,246] if name=='T-W' else [126])
        if plan:
            stations += [plan['supports']['S3']['y']]
        else:stations += [-21.25]
        r['stations']=sorted(set(v for v in stations if r['start']<=v<=r['end']))
        r['door_stations']=[186,246] if name=='T-W' else None
    elif name=='T-N':
        r['stations']=[r['start'],plan['supports']['N1']['x'] if plan else 53.25,81.5,113.5]
        if not plan:r['stations'].append(224.25)
        r['stations'].append(r['end']);r['stations']=sorted(set(r['stations']))
        r['door_stations']=[81.5,113.5]
    return r


def generate(r):
    name=r['name'];a=r['start'];b=r['end'];h=r['bottom'];axis=r['axis'];fixed=r['fixed']
    if not all(math.isfinite(v) for v in [a,b,h,fixed]) or b<=a:raise ValueError('Invalid assembly extent: '+name)
    if type(r['panels']) is not int or r['panels']<2:raise ValueError('Invalid panel count')
    model=Model(name=name+' parametric assembly');records={};counts=Counter()
    def point(s,z):return [s,fixed,z] if axis==0 else [fixed,s,z]
    def member(role,sa,za,sb,zb,size=3):
        idx=counts[role];counts[role]+=1;key=f'{name}.{role}.{idx}'
        model.add_element(MemberElement(point(sa,za),point(sb,zb),size,size,name=key))
        records[key]={'role':role,'kind':'member'}
    def plate(s,high):
        idx=counts['plate'];counts['plate']+=1;key=f'{name}.plate.{idx}'
        mesh=box_mesh(s-3,fixed-1.75,high-5,6,.5,6,key)
        model.add_element(MeshElement(geometry=mesh,name=key));records[key]={'role':'plate','kind':'plate'}
    low=h+1.5
    if name in ('T-S','T1'):
        high=roof_z(r['roof'],fixed)-1.5
        if high<=low+6:raise ValueError('Insufficient transverse depth')
        member('bottom',a,low,b,low);member('top',a,high,b,high)
        stations=np.linspace(a,b,r['panels']+1)
        for s in stations:member('upright',s,low,s,high)
        member('brace',stations[0],low,stations[1],high,2.5)
        member('brace',stations[-2],high,stations[-1],low,2.5)
        for s in stations[1:-1]:plate(s,high)
    elif name in ('T-W','T-E'):
        stations=r['stations']
        member('bottom',a,low,b,low)
        for s,t in zip(stations,stations[1:]):
            member('top',s,roof_z(r['roof'],s)-1.5,t,roof_z(r['roof'],t)-1.5)
            if not(name=='T-W' and s>=185):
                # Original web tips stopped 1.5 in short of chord axes. Draft joins axes explicitly.
                member('web',s,low if r['coordinated'] else h+3,t,
                       roof_z(r['roof'],t)-(1.5 if r['coordinated'] else 3),2.5)
        for s in stations:member('upright',s,low,s,roof_z(r['roof'],s)-1.5)
        if name=='T-W':member('door_header',186,r['floor']+83,246,r['floor']+83)
    else:
        high=r['roof']['plateau_z']-1.5;header=r['floor']+96
        member('bottom',a,low,b,low)
        for s in r['stations']:member('upright',s,low,s,high)
        member('header_lower',a,header,b,header);member('top',a,high,b,high)
        stations=np.linspace(a,b,r['panels']+1)
        for i,(s,t) in enumerate(zip(stations,stations[1:])):
            member('header_vertical',s,header,s,high,2.5)
            member('header_brace',s,header if i%2==0 else high,t,high if i%2==0 else header,2.5)
        member('door_header',81.5,r['floor']+85.5,113.5,r['floor']+85.5)
    data={'recipe':r,'model':model,'records':records}
    data['graph'],data['attachments']=attachment_graph(data)
    return data


def on_segment(pt,a,b,tol=1e-6):
    pa=np.array(pt);aa=np.array(a);bb=np.array(b);d=bb-aa;t=float((pa-aa)@d/(d@d))
    return -tol<=t<=1+tol and np.linalg.norm(pa-(aa+t*d))<tol,t


def attachment_graph(data):
    """Geometric endpoint-on-axis incidence only; never infers a welded/pinned joint."""
    elements=[e for e in data['model'].elements() if isinstance(e,MemberElement)]
    graph=Graph(name='Geometric attachment candidates');coords={};attachments={}
    def node(pt):
        key='p:'+','.join(f'{v:.6f}' for v in pt)
        if key not in coords:
            coords[key]=list(pt);graph.add_node(key,x=pt[0],y=pt[1],z=pt[2])
        return key
    for e in elements:node(e.start);node(e.end)
    for e in elements:
        pts=[]
        for key,pt in coords.items():
            yes,t=on_segment(pt,e.start,e.end)
            if yes:pts.append((t,key))
        pts.sort();attachments[e.name]=[key for _,key in pts]
        for (_,j),(_,k) in zip(pts,pts[1:]):
            if j!=k:
                if graph.has_edge((j,k)):
                    names=list(graph.edge_attribute((j,k),'members'));names.append(e.name)
                    graph.edge_attribute((j,k),'members',names)
                else:graph.add_edge(j,k,members=[e.name])
    return graph,attachments


def validate_truss(data):
    for e in data['model'].elements():
        if isinstance(e,MemberElement):e.check_parameters()
        mesh=e.compute_elementgeometry()
        if not mesh.is_valid() or not mesh.is_closed():raise ValueError('Invalid mesh: '+e.name)
    expected=generate_without_recursion(data['recipe'])
    actual={e.name:fingerprint(e.compute_elementgeometry()) for e in data['model'].elements()}
    if expected!=actual:raise ValueError('Assembly differs from its parametric recipe: '+data['recipe']['name'])
    g,att=attachment_graph(data)
    if att!=data['attachments']:raise ValueError('Attachment register stale')
    def sig(graph):return {tuple(sorted(e)):sorted(a['members']) for e,a in graph.edges(data=True)}
    if sig(g)!=sig(data['graph']):raise ValueError('Attachment graph missing or stale edges')
    incidence=Counter(j for joints in att.values() for j in joints)
    loose=[]
    for e in data['model'].elements():
        if isinstance(e,MemberElement):
            for j in (att[e.name][0],att[e.name][-1]):
                if incidence[j]<2:loose.append({'member':e.name,'point':g.node_coordinates(j)})
    return {'elements':len(actual),'members':len(att),'joints':g.number_of_nodes(),
            'segments':g.number_of_edges(),'unshared_endpoints':loose}


def generate_without_recursion(r):
    d=generate(r)
    return {e.name:fingerprint(e.modelgeometry) for e in d['model'].elements()}


def validate_plan(plan):
    c=plan['supports'];m=plan['members']
    for key,s in c.items():
        if not all(math.isfinite(s[k]) for k in ('x','y','width','depth')) or min(s['width'],s['depth'])<=0:raise ValueError('Invalid support: '+key)
    for key,member in m.items():
        if member['line'].length<1e-8:raise ValueError('Zero-length plan member: '+key)
        if any(t not in c for t in member['targets']):raise ValueError('Missing support reference: '+key)
    if abs(c['N2']['x']-c['N1']['x']-192)>1e-7 or c['N1']['y']!=c['N2']['y']:raise ValueError('North door bay/alignment changed')
    if c['S2']['x']!=c['N2']['x'] or c['S3']['x']!=c['N2']['x']:raise ValueError('East support axes disagree')
    for name,support in [('T1','W2'),('O2','W2'),('B2','W3'),('O3','W3')]:
        if abs(m[name]['line'].start.y-c[support]['y'])>1e-7:raise ValueError('Support row not propagated: '+name)
    if abs(m['T-E']['line'].start.x-c['N2']['x'])>1e-7:raise ValueError('East truss axis is stale')
    if abs(m['T-N']['line'].start.y-c['N2']['y'])>1e-7:raise ValueError('North truss row is stale')
    west=c['W2']['x']
    if any(abs(c[k]['x']-west)>1e-7 for k in ('W1','W3','W4')):raise ValueError('West support axes disagree')
    if abs(m['T-W']['line'].start.x-west)>1e-7 or abs(m['T-W']['line'].end.x-west)>1e-7:
        raise ValueError('West truss must be on far-west support row')
    if m['T-W']['line'].start.y>c['W1']['y'] or m['T-W']['line'].end.y<c['W4']['y']:
        raise ValueError('West truss does not reach end columns')
    for key in ('T-S','T1','B2','B3','T-N'):
        if abs(m[key]['line'].start.x-west)>1e-7:raise ValueError('Cross-member misses far-west truss: '+key)
    for support,target in [('E-S','S3'),('E-M','T-E'),('E-N','T-E')]:
        key='C-'+support.replace('-','');link=m.get(key)
        if link is None:raise ValueError('Missing east connection: '+key)
        s=c[support]
        if not np.allclose(list(link['line'].start),[s['x'],s['y'],0],rtol=0,atol=1e-7) or link['bottom']!=s['top']:
            raise ValueError('East connection misses column top: '+key)
        expected=[c[target]['x'],c[target]['y'],0] if target in c else [m[target]['line'].start.x,s['y'],0]
        if not np.allclose(list(link['line'].end),expected,rtol=0,atol=1e-7):raise ValueError('East connection endpoint stale: '+key)
        if target in c:
            if link['bottom']!=c[target]['top']:raise ValueError('East connection misses target column top: '+key)
        elif not on_segment(link['line'].end,m[target]['line'].start,m[target]['line'].end)[0] or link['bottom']!=m[target]['bottom']:
            raise ValueError('East connection misses truss: '+key)
    beam=m['E-OB'];elements=list(plan['beam_model'].elements())
    if len(elements)!=1 or elements[0].name!='E-OB':raise ValueError('Missing east overhead beam solid')
    if beam['bottom']!=c['E-S']['top'] or beam['bottom']!=c['E-N']['top'] or beam['bottom']!=m['T-E']['bottom']:
        raise ValueError('East overhead beam elevation disagrees with frame')
    a=beam['line'].start;b=beam['line'].end
    expected=MemberElement([a.x,a.y,beam['bottom']+1.5],[b.x,b.y,beam['bottom']+1.5],3,3)
    if fingerprint(elements[0].modelgeometry)!=fingerprint(expected.compute_elementgeometry()):raise ValueError('East overhead beam solid is stale')
    for key in ('E-S','E-N'):
        if not on_segment([c[key]['x'],c[key]['y'],0],a,b)[0]:raise ValueError('East overhead beam misses end support')
    columns={e.name:e for e in plan['column_model'].elements()}
    if set(columns)!=set(c):raise ValueError('Missing column geometry')
    for key,e in columns.items():
        s=c[key];mesh=e.modelgeometry;xyz=np.array(mesh.vertices_attributes('xyz'))
        if not mesh.is_closed() or not mesh.is_valid():raise ValueError('Invalid column mesh: '+key)
        if not np.allclose(xyz.min(0),[s['x']-s['width']/2,s['y']-s['depth']/2,s['base']],rtol=0,atol=1e-7) or not np.allclose(xyz.max(0),[s['x']+s['width']/2,s['y']+s['depth']/2,s['top']],rtol=0,atol=1e-7):
            raise ValueError('Column geometry disagrees with support registry: '+key)


def audit(plan,trusses):
    rows=[]
    for name,m in plan['members'].items():
        a=np.array(list(m['line'].start)[:2]);b=np.array(list(m['line'].end)[:2]);v=b-a
        for target in m['targets']:
            s=plan['supports'][target];p=np.array([s['x'],s['y']]);t=float((p-a)@v/(v@v));q=a+np.clip(t,0,1)*v
            distance=float(np.linalg.norm(p-q))
            rows.append(dict(member=name,support=target,plan_offset_in=round(distance,5),
                location='on segment' if 0<=t<=1 else 'beyond endpoint',
                status='plan coincidence only' if distance<1e-6 else 'offset / connection unresolved'))
    warnings=[
        'Draft roof retains 30 degrees and old heights, but starts at current T-SO Y=-64. Current roof design is not finalized.',
        'User correction: T-W is on the far-west column row X=-34. Cross-members now extend to that row; O2/O3 are subsegments of T1/B2, not separate beams.',
        'Longitudinal web tips are moved to chord axes in the draft; source-baseline geometry remains separate.',
        'All 13 columns are modeled from floor datum Z=0 to frame bottom Z=98.5 using source plan-symbol sections. East-wall heights are provisional; footing and connection details remain unresolved.',
        'E-OB sits at Z98.5 with a provisional 3-inch display envelope matching truss chords; section sizing is unresolved. OB1 elevation remains unknown.',
        'T-W source uprights at Y185 and Y186 are only 1 inch apart with 3-inch envelopes: overlap retained for review.',
        'T-N loft-door jamb axes X81.5/113.5 give 29 inches between 3-inch faces; source 32 inches is axis spacing.',
        'T-W source door header gives 81.5 inches from loft floor to underside; source opening height needs coordination.',
        'Ground-floor N1/N2 bay is 192 inches center spacing / 188 inches between 4-inch symbols, separate from the T-N loft door.',
        'T-S at Y0 is 2 inches north of S3 at Y=-2; south beam Y=-64 is 2 inches north of the south columns.',
        'E-S connects to S3; E-M/E-N connect to T-E at Z98.5 as unsized references. E-M retains option B and its 1-inch offset from E-OB.',
        'Truss 3-inch section envelopes have not been reconciled with the plan outside-face limit at X213.5.',
        'Mesh validity and geometric connections do not establish structural stability, capacity, connection design or collision-free fabrication.'
    ]
    for name,d in trusses.items():
        result=validate_truss(d)
        if result['unshared_endpoints']:warnings.append(f'{name}: {len(result["unshared_endpoints"])} endpoints do not meet another member axis.')
    return {'support_offsets':rows,'coordination_items':warnings}


def verify_baselines(baselines):
    scene=read('model-renders/garage-model.json');results={}
    for name,d in baselines.items():
        objects=[o for o in scene['objects'] if o['material']=='truss' and
                 (o['name'].startswith(name+' ') or (name=='T-W' and o['name']=='French door header'))]
        original=sorted(sorted(tuple(round(v/.0254,7) for v in p) for p in o['vertices']) for o in objects)
        actual=sorted(fingerprint(e.modelgeometry) for e in d['model'].elements())
        if original!=actual:raise ValueError('Baseline differs from source: '+name)
        results[name]=f'{len(objects)} source member/plate shapes matched'
    return results


def save_csv(path,rows):
    if not rows:return
    with path.open('w') as f:
        writer=csv.DictWriter(f,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)


def plot_plan(plan,background):
    fig,ax=plt.subplots(figsize=(13,13));fig.suptitle('GARAGE / BEAM & SUPPORT COORDINATION DRAFT',fontsize=17,weight='bold',color=INK)
    for poly in background['plan']['walls']:ax.add_patch(Patch(np.array(poly.points)[:,:2],fc='#e2e6e8',ec='#c2cbd1',lw=.5))
    for key,poly in plan['outlines'].items():
        xy=np.array(poly.points)[:,:2];xy=np.vstack([xy,xy[0]])
        ax.plot(*xy.T,color=TEAL if key=='loft_outline' else '#9db7c2',ls='--',lw=1)
    for name,m in plan['members'].items():
        if name=='OB1' or m['kind']=='subsegment reference':continue
        line=m['line'];xy=np.array([line.start,line.end])[:,:2]
        color=ORANGE if m['kind']=='truss' else BLUE
        ax.plot(*xy.T,color=color,lw=2 if m['kind']=='truss' else 1.6,ls='--' if name=='E-OB' else '-')
        mid=line.midpoint;vertical=abs(line.end.y-line.start.y)>abs(line.end.x-line.start.x)
        dx,dy=(5,12) if vertical else (0,5)
        if name=='T-SO':dy=8
        if name=='B3':dy=-10
        if name in ('O2','O3'):dx=-5;dy=8
        ax.text(mid.x+dx,mid.y+dy,name,fontsize=8 if name.startswith('C-') else 10,color=color,rotation=90 if vertical else 0,
            ha='center',bbox=dict(fc='white',ec='none',alpha=.8,pad=1))
    for name,s in plan['supports'].items():
        x,y=s['x'],s['y'];w,d=s['width'],s['depth']
        ax.add_patch(Patch([[x-w/2,y-d/2],[x+w/2,y-d/2],[x+w/2,y+d/2],[x-w/2,y+d/2]],fc=INK))
        dx=-9 if name.startswith('W') and name!='WB3' else 7
        dy=-12 if name.startswith('N') else 5
        ax.text(x+dx,y+dy,name+(' (B)' if name=='E-M' else ''),ha='right' if dx<0 else 'left',fontsize=9)
    ax.set(xlim=(-63,290),ylim=(-94,319),xlabel='X / east (inches)',ylabel='Y / north (inches)');ax.set_aspect('equal');ax.grid(alpha=.14)
    ax.text(70,112,'ORANGE: TRUSSES\nBLUE: BEAMS\nDASHED: REFERENCE / OUTLINE',fontsize=10,color=INK,linespacing=1.6)
    fig.text(.1,.03,'Current support positions drive draft member axes. Geometry only; bearing details unresolved.\nOB1 is listed separately as outbuilding context. E-M is option B only. Roof/loft outlines are plan limits.',fontsize=9)
    fig.subplots_adjust(bottom=.10,top=.93)
    return fig


def plot_truss(name,d,baseline):
    fig,axs=plt.subplots(2,1,figsize=(15,10));r=d['recipe'];axis=r['axis']
    fig.suptitle(name+' / PARAMETRIC TRUSS STUDY',fontsize=20,weight='bold',color=INK)
    for ax,title,data in [(axs[0],'Source baseline — original geometry',baseline),(axs[1],'Current-plan coordination draft',d)]:
        for el in data['model'].elements():
            pts=np.array(el.modelgeometry.vertices_attributes('xyz'))[:,[axis,2]]
            pts=np.unique(np.round(pts,8),axis=0)
            ax.add_patch(Patch(pts[ConvexHull(pts).vertices],fc=ORANGE,ec=ORANGE,lw=.3))
        rr=data['recipe'];ax.autoscale_view();ax.set_aspect('equal');ax.grid(alpha=.15)
        ax.set_title(f'{title} | reference span {rr["end"]-rr["start"]:.2f} in | fixed {"X" if axis else "Y"}={rr["fixed"]:g}',loc='left',fontsize=11)
        ax.set_xlabel(('Y / north' if axis else 'X / east')+' (inches)');ax.set_ylabel('Z above floor (inches)')
    # Identical scales make the old/current dimensional comparison meaningful.
    xmin=min(d['recipe']['start'],baseline['recipe']['start'])-10
    xmax=max(d['recipe']['end'],baseline['recipe']['end'])+10
    allz=[v[2] for data in (d,baseline) for e in data['model'].elements() for v in e.modelgeometry.vertices_attributes('xyz')]
    for ax in axs:ax.set_xlim(xmin,xmax);ax.set_ylim(min(allz)-8,max(allz)+8)
    fig.text(.08,.035,'All members regenerated from endpoints and section envelopes. Old mesh import is used only to verify the baseline.\nDraft roof and opening details are assumptions; attachment checks are geometric, not structural design.',fontsize=10,color=INK)
    fig.tight_layout(rect=(.02,.08,.98,.94));return fig


def schedule_pages(plan,report):
    result=[]
    def table_page(title,headers,rows,widths,foot):
        fig,ax=plt.subplots(figsize=(15,10));ax.axis('off')
        fig.suptitle(title,fontsize=19,weight='bold',color=INK,x=.06,ha='left')
        table=ax.table(cellText=rows,colLabels=headers,colWidths=widths,loc='center',cellLoc='left')
        table.auto_set_font_size(False);table.set_fontsize(10);table.scale(1,2.2)
        for (row,col),cell in table.get_celld().items():
            cell.set_edgecolor('#d9e0e4')
            if row==0:cell.set_facecolor(INK);cell.set_text_props(color='white',weight='bold')
            elif row%2==0:cell.set_facecolor('#f0f5f5')
        fig.text(.06,.065,foot,fontsize=10,color=INK)
        fig.subplots_adjust(left=.06,right=.96,top=.90,bottom=.13)
        return fig
    rows=[[key,f'{s["x"]:g}',f'{s["y"]:g}',f'{s["width"]:g} × {s["depth"]:g}',s['status'],f'{s["base"]:g} / {s["top"]:g}'+(' trial' if key.startswith('E-') else '')] for key,s in plan['supports'].items()]
    result.append(('support-schedule',table_page('SUPPORT POSITION SCHEDULE / INCHES',
        ['Support','Center X','Center Y','Plan symbol','Status','Base / top Z'],rows,[.12,.13,.13,.17,.22,.23],
        'SW exterior garage corner is X=0, Y=0. Symbol dimensions do not select structural sections.\nAll current support coordinates come from the floor-plan basis; E-M is an option-B support.')))
    rows=[]
    for key,m in plan['members'].items():
            line=m['line'];rows.append([key,m['kind'].replace('existing context beam','context beam').replace('subsegment reference','subsegment'),
            f'({line.start.x:g}, {line.start.y:g})',f'({line.end.x:g}, {line.end.y:g})',f'{line.length:.2f}',
            'unknown' if m['bottom'] is None else f'{m["bottom"]:g}'])
    result.append(('member-position-schedule',table_page('BEAM & TRUSS POSITION SCHEDULE / INCHES',
        ['Member','Type','Start (X, Y)','End (X, Y)','Ref. length','Bottom Z'],rows,[.12,.14,.23,.23,.14,.14],
        'Plan lines are reference axes, not solid member envelopes. Lengths are not fabrication cuts.\nDraft positions and source assumptions are itemized in coordination-report.md. E-OB uses a provisional 3-inch display envelope. OB1 elevation is unknown.')))
    fig,ax=plt.subplots(figsize=(15,11));ax.axis('off')
    fig.suptitle('COORDINATION ITEMS / NOT YET RESOLVED',fontsize=18,weight='bold',color=INK,x=.06,ha='left')
    text='\n\n'.join(f'{i+1}. '+textwrap.fill(item,width=115,subsequent_indent='    ') for i,item in enumerate(report['coordination_items']))
    fig.text(.06,.91,text,va='top',fontsize=9.5,linespacing=1.25,color=INK)
    result.append(('coordination-items',fig))
    return result


def interactive(plan,trusses,background):
    fig=go.Figure()
    def mesh_trace(elements,name,color,opacity=1):
        vs=[];ts=[];text=[]
        for el in elements:
            verts,faces=el.modelgeometry.to_vertices_and_faces();offset=len(vs);vs.extend(verts);text.extend([el.name]*len(verts))
            for face in faces:
                ts.extend([[offset+face[0],offset+face[i],offset+face[i+1]] for i in range(1,len(face)-1)])
        xyz=np.array(vs);tri=np.array(ts)
        fig.add_trace(go.Mesh3d(x=xyz[:,0],y=xyz[:,1],z=xyz[:,2],i=tri[:,0],j=tri[:,1],k=tri[:,2],text=text,
            color=color,opacity=opacity,name=name,showlegend=True,hovertemplate='%{text}<br>X %{x:.2f} Y %{y:.2f} Z %{z:.2f} in<extra></extra>'))
    for name,d in trusses.items():mesh_trace(list(d['model'].elements()),name,ORANGE)
    mesh_trace(list(plan['beam_model'].elements()),'E-OB · east overhead beam',ORANGE)
    walls=[e for e in background['model'].elements() if e.name.startswith('wall:')]
    mesh_trace(walls,'Existing wall reference','#bec8ce',.18)
    for name,m in plan['members'].items():
        if m['kind']!='beam' or name=='E-OB':continue
        line=m['line'];z=m['bottom']
        if z is None:continue
        fig.add_trace(go.Scatter3d(x=[line.start.x,line.end.x],y=[line.start.y,line.end.y],z=[z,z],mode='lines',
            line=dict(width=6,color=BLUE),name=name+' bottom reference',hovertemplate=name+' · reference line only<extra></extra>'))
    cols=plan['supports'];xyz=np.array([[c['x'],c['y'],0] for c in cols.values()])
    fig.add_trace(go.Scatter3d(x=xyz[:,0],y=xyz[:,1],z=xyz[:,2],mode='markers+text',text=list(cols),marker=dict(size=4,color=TEAL),
        name='Column labels',textposition='bottom center'))
    columns=list(plan['column_model'].elements())
    mesh_trace([e for e in columns if not e.name.startswith('E-')],'Frame columns',BLUE)
    mesh_trace([e for e in columns if e.name in ('E-S','E-N')],'East columns · trial height',TEAL)
    mesh_trace([e for e in columns if e.name=='E-M'],'E-M · option B · trial height',TEAL,.55)
    fig.update_layout(title=dict(text='Garage / east overhead beam + connections<br><sup>E-OB spans E-S to E-N · beam underside level with truss bottoms at Z98.5</sup>',x=.04),
        scene=dict(aspectmode='data',xaxis_title='X east / in',yaxis_title='Y north / in',zaxis_title='Z / in',camera=dict(eye=dict(x=1.5,y=-1.9,z=1.2))),
        height=850,margin=dict(l=15,r=315,t=90,b=15),legend=dict(x=1.01,y=1))
    fig.write_html(OUT/'coordinated-3d.html',include_plotlyjs=True,config={'displaylogo':False,'responsive':True})


def main():
    OUT.mkdir(exist_ok=True)
    plan=make_plan();validate_plan(plan)
    baseline={n:generate(recipe(n)) for n in NAMES}
    draft={n:generate(recipe(n,plan)) for n in NAMES}
    report={'baseline_shape_checks':verify_baselines(baseline),'trusses':{},'source_hashes':{}}
    for path in ['floor-plan-setbacks/floor-plan-study-basis.json','structural-study/framing-member-register.json',
                 'model-renders/garage-model.json','structural-study/latest-framing-corrections.md']:
        report['source_hashes'][path]=hashlib.sha256((ROOT/path).read_bytes()).hexdigest()
    bundle={'plan':plan,'trusses':draft,'baselines':baseline,'sources':report['source_hashes']}
    dest=frame_models.allocate('coordinated')
    json_dump(bundle,dest,pretty=True);loaded=json_load(dest)
    plan=loaded['plan'];draft=loaded['trusses'];baseline=loaded['baselines'];validate_plan(plan)
    for n in NAMES:
        report['trusses'][n]={'baseline':validate_truss(baseline[n]),'draft':validate_truss(draft[n])}
        m=plan['members'][n];r=draft[n]['recipe'];axis=r['axis']
        if abs(m['line'].start[axis]-r['start'])+abs(m['line'].end[axis]-r['end'])+abs(m['line'].start[1-axis]-r['fixed'])>1e-7:
            raise ValueError('Plan/elevation mismatch: '+n)
    # A real model edit propagates into plan axes, attachments and truss roof intersection.
    changed=make_plan({'W2':{'y':75.75}});validate_plan(changed)
    edited={n:generate(recipe(n,changed)) for n in NAMES}
    for d in edited.values():validate_truss(d)
    test=edited['T1']
    if test['recipe']['fixed']!=75.75 or changed['members']['O2']['line'].start.y!=75.75:raise ValueError('W2 move failed to propagate')
    for n in ('T-W','T-E'):
        if 75.75 not in edited[n]['recipe']['stations'] or 69.75 in edited[n]['recipe']['stations']:raise ValueError('Old support station retained')
    report['edit_test']='W2 moved +6 inches in a disposable draft; T1/O2 station, T1 roof height, and both longitudinal truss stations regenerated successfully'
    report['expected_failures']={}
    def reject(label,fn):
        try:fn()
        except ValueError as exc:report['expected_failures'][label]=str(exc)
        else:raise AssertionError('Invalid input accepted: '+label)
    def stale():
        d=copy.deepcopy(draft['T-E']);next(e for e in d['model'].elements() if isinstance(e,MemberElement)).end.x+=1;validate_truss(d)
    def missing_edge():
        d=copy.deepcopy(draft['T-N']);d['graph'].delete_edge(next(iter(d['graph'].edges())));validate_truss(d)
    reject('member detached from recipe',stale);reject('missing attachment edge',missing_edge)
    reject('east supports disagree',lambda:validate_plan(make_plan({'S2':{'x':220}})))
    reject('north bay changed',lambda:validate_plan(make_plan({'N1':{'x':30}})))
    def wrong_west():
        p=copy.deepcopy(plan);line=p['members']['T-W']['line'];p['members']['T-W']['line']=Line([0,line.start.y,0],[0,line.end.y,0]);validate_plan(p)
    def missing_column():
        p=copy.deepcopy(plan);p['column_model']=Model(name='empty');validate_plan(p)
    reject('west truss reverted to existing wall',wrong_west)
    reject('missing column solids',missing_column)
    def detached_connection():
        p=copy.deepcopy(plan);link=p['members']['C-EN'];end=list(link['line'].end);end[0]+=1
        link['line']=Line(link['line'].start,end);validate_plan(p)
    reject('detached east connection',detached_connection)
    moved_east=make_plan({'E-M':{'x':248.5,'y':190}});validate_plan(moved_east)
    report['east_connections']={k:dict(from_support=m['from_support'],connection_to=m['connection_to'],
        length_in=m['line'].length,elevation_in=m['bottom']) for k,m in plan['members'].items() if 'connection_to' in m}
    report['east_connection_edit_test']='E-M moved in X and Y; connection regenerated to T-E at the new station and passed attachment checks.'
    report['column_geometry']={'count':len(list(plan['column_model'].elements())),'bounds_and_roundtrip':'passed','west_truss_x':plan['members']['T-W']['line'].start.x}
    report.update(audit(plan,draft));report['status']='Geometry checks passed; coordination items remain open'
    (OUT/'validation.json').write_text(json.dumps(report,indent=2)+'\n')
    rows=[]
    for name,m in plan['members'].items():
        a=m['line'].start;b=m['line'].end
        rows.append(dict(id=name,type=m['kind'],x1=a.x,y1=a.y,x2=b.x,y2=b.y,length_in=m['line'].length,
            bottom_in=m['bottom'],position_status=m['position_status'],basis=m['basis']))
    save_csv(OUT/'beam-and-truss-positions.csv',rows)
    save_csv(OUT/'support-positions.csv',[dict(id=k,**v) for k,v in plan['supports'].items()])
    save_csv(OUT/'support-offsets.csv',report['support_offsets'])
    member_rows=[]
    for name,d in draft.items():
        for e in d['model'].elements():
            if not isinstance(e,MemberElement):continue
            member_rows.append(dict(assembly=name,id=e.name,x1=e.start.x,y1=e.start.y,z1=e.start.z,
                x2=e.end.x,y2=e.end.y,z2=e.end.z,length_in=e.start.distance_to_point(e.end),width_in=e.width,depth_in=e.depth))
    save_csv(OUT/'truss-members.csv',member_rows)
    background=build();figs=[('floor-plan',plot_plan(plan,background))]
    schedules=schedule_pages(plan,report)
    figs += schedules[:2]
    figs += [(n+'-study',plot_truss(n,draft[n],baseline[n])) for n in NAMES]
    figs.append(schedules[2])
    with PdfPages(OUT/'floor-plan-and-truss-studies.pdf') as pdf:
        for name,fig in figs:
            pdf.savefig(fig)
            for ext in ('png','svg','pdf'):fig.savefig(OUT/f'{name}.{ext}',dpi=150)
            plt.close(fig)
    interactive(plan,draft,background)
    summary=['# Coordinated COMPAS floor plan and trusses','',
        'Status: geometry coordination draft; unresolved items below. Units inches, X east, Y north, Z up.','',
        '## Position decisions','', '| Member | Position status | Basis |','|---|---|---|']
    summary += [f'| {k} | {m["position_status"]} | {m["basis"]} |' for k,m in plan['members'].items()]
    summary += ['','## Open coordination items','']+[f'- {x}' for x in report['coordination_items']]
    summary += ['','## Support offsets','', '| Member | Support | Offset (in) | Interpretation |','|---|---|---:|---|']
    summary += [f'| {x["member"]} | {x["support"]} | {x["plan_offset_in"]:g} | {x["status"]} |' for x in report['support_offsets']]
    summary += ['','## Validation','',report['edit_test'],'',
        'All five baseline assemblies match original source vertex sets. All models are saved/reloaded before rendering. Plan and elevation axes agree.',
        'Deliberately invalid member edits, missing graph edges, misaligned east supports and a changed north bay are rejected.',
        'Column solids use Z0 to Z98.5; east-wall heights are provisional. Geometric incidence is not an engineered joint or load path.']
    (OUT/'coordination-report.md').write_text('\n'.join(summary)+'\n')
    print(json.dumps({'status':report['status'],'supports':len(plan['supports']),'plan_members':len(plan['members']),
        'draft_truss_members':len(member_rows),'baseline_checks':report['baseline_shape_checks'],
        'unshared_draft_endpoints':{k:len(v['draft']['unshared_endpoints']) for k,v in report['trusses'].items()},
        'expected_failures':report['expected_failures']},indent=2))


if __name__=='__main__':main()
