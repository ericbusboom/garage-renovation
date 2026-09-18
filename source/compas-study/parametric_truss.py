"""Programmatic T1 assembly, original-shape verification and dimension variants."""
from dataclasses import dataclass, asdict, replace
import copy
import csv
import json
import math
import hashlib
import numpy as np
from compas.data import json_dump, json_load
from compas.datastructures import Graph
from compas.geometry import Line, Point
from compas_model.models import Model
from geometry_types import MemberElement, MeshElement
from build_study import ROOT, OUT, box_mesh, plt, Patch, ConvexHull, go, INK, ORANGE, BLUE


@dataclass(frozen=True)
class TrussParameters:
    span: float
    depth: float
    x: float = 0
    y: float = 69.75
    bottom: float = 98.5
    panels: int = 6
    chord_size: float = 3
    upright_size: float = 3
    brace_size: float = 2.5

    def validate(self):
        if not all(math.isfinite(v) for v in asdict(self).values()):
            raise ValueError('All parameters must be finite')
        if type(self.panels) is not int or self.panels < 2:
            raise ValueError('Panel count must be an integer of at least two')
        if min(self.span,self.depth,self.chord_size,self.upright_size,self.brace_size)<=0:
            raise ValueError('Span, depth and section envelopes must be positive')
        if self.depth <= self.chord_size + 6:
            raise ValueError('Depth cannot accommodate source chord spacing and 6-inch plate')
        if self.span/self.panels <= max(self.upright_size,6):
            raise ValueError('Panel width must exceed upright/plate envelope')


def source_parameters():
    reg=json.loads((ROOT/'structural-study/framing-member-register.json').read_text())
    scene=json.loads((ROOT/'model-renders/garage-model.json').read_text())
    ref=next(m for m in reg['members'] if m['id']=='T1')
    return TrussParameters(span=ref['end'][0]-ref['start'][0],
        depth=scene['basis']['depth_assumptions']['T1'],x=ref['start'][0],
        y=ref['start'][1],bottom=ref['bottom_elevation'])


def make_truss(p):
    p.validate()
    model=Model(name='T1 parametric concept assembly')
    graph=Graph(name='T1 shared geometric joints (not connection specifications)')
    members={};plates={}
    low=p.bottom+p.chord_size/2
    high=p.bottom+p.depth-p.chord_size/2
    for row,z in [('L',low),('U',high)]:
        for i in range(p.panels+1):
            graph.add_node(f'{row}{i}',x=p.x+i*p.span/p.panels,y=p.y,z=z)
    def add(name,role,joints,size):
        a=graph.node_coordinates(joints[0]);b=graph.node_coordinates(joints[-1])
        model.add_element(MemberElement(a,b,size,size,name=name))
        members[name]={'role':role,'joints':joints,'section_basis':'source visualization envelope; not a selected section'}
        for j,k in zip(joints,joints[1:]):graph.add_edge(j,k,member=name)
    add('T1.bottom','bottom chord',[f'L{i}' for i in range(p.panels+1)],p.chord_size)
    add('T1.top','top chord',[f'U{i}' for i in range(p.panels+1)],p.chord_size)
    for i in range(p.panels+1):add(f'T1.upright.{i}','upright',[f'L{i}',f'U{i}'],p.upright_size)
    add('T1.brace.west','end brace',['L0','U1'],p.brace_size)
    add('T1.brace.east','end brace',[f'U{p.panels-1}',f'L{p.panels}'],p.brace_size)
    for i in range(1,p.panels):
        x,y,z=graph.node_coordinates(f'U{i}')
        key=f'T1.plate.{i}'
        model.add_element(MeshElement(geometry=box_mesh(x-3,y-1.75,z-5,6,.5,6,key),name=key))
        plates[key]={'joint':f'U{i}','basis':'original illustrative plate, regenerated from joint'}
    return {'parameters':asdict(p),'units':'inches','model':model,'graph':graph,
        'members':members,'plates':plates,
        'notes':['End-braced rectangular layout retained from source; not a pin-jointed triangulated design.',
                 'Joint sharing checks geometry only; physical joints, bearing and load capacity are unresolved.',
                 'Span measures end joint centers; end uprights extend half a section beyond them.',
                 'Depth is chord outside-face to outside-face; decorative plate envelopes can extend above it.']}


def validate_truss(data):
    p=TrussParameters(**data['parameters']);p.validate()
    g=data['graph'];elements={el.name:el for el in data['model'].elements()}
    if set(elements)!=set(data['members'])|set(data['plates']):
        raise ValueError('Assembly and member/plate register disagree')
    if set(g.nodes())!={f'{r}{i}' for r in ('L','U') for i in range(p.panels+1)}:
        raise ValueError('Joint IDs do not match panel layout')
    for r,z in [('L',p.bottom+p.chord_size/2),('U',p.bottom+p.depth-p.chord_size/2)]:
        for i in range(p.panels+1):
            if not np.allclose(g.node_coordinates(f'{r}{i}'),[p.x+i*p.span/p.panels,p.y,z],rtol=0,atol=1e-8):
                raise ValueError('Joint no longer matches parameters: '+f'{r}{i}')
    expected_edges={}
    for name,meta in data['members'].items():
        el=elements[name];el.check_parameters()
        joints=meta['joints']
        if any(j not in g.node for j in joints):raise ValueError('Missing joint: '+name)
        for point,joint in [(el.start,joints[0]),(el.end,joints[-1])]:
            if point.distance_to_point(Point(*g.node_coordinates(joint)))>1e-8:
                raise ValueError('Member endpoint misses joint: '+name)
        # Chords are single physical members but have explicit intermediate attachments.
        for j in joints:
            pt=Point(*g.node_coordinates(j))
            if abs(el.start.distance_to_point(pt)+pt.distance_to_point(el.end)-el.start.distance_to_point(el.end))>1e-7:
                raise ValueError('Attachment outside member segment: '+name)
        for j,k in zip(joints,joints[1:]):expected_edges[frozenset((j,k))]=name
    actual={frozenset(edge):attrs['member'] for edge,attrs in g.edges(data=True)}
    if actual!=expected_edges:raise ValueError('Connectivity graph differs from physical member attachments')
    seen=set();todo=[next(iter(g.nodes()))]
    while todo:
        node=todo.pop()
        if node not in seen:seen.add(node);todo.extend(g.neighbors(node))
    if len(seen)!=g.number_of_nodes():raise ValueError('Disconnected joint graph')
    for name,el in elements.items():
        mesh=el.compute_elementgeometry()
        if not mesh.is_valid() or not mesh.is_closed():raise ValueError('Invalid member mesh: '+name)
        if name in data['plates']:
            j=data['plates'][name]['joint'];x,y,z=g.node_coordinates(j)
            xyz=np.array(mesh.vertices_attributes('xyz'))
            if not np.allclose(xyz.min(0),[x-3,y-1.75,z-5]) or not np.allclose(xyz.max(0),[x+3,y-1.25,z+1]):
                raise ValueError('Plate no longer follows its joint: '+name)
    return {'physical_members':len(data['members']),'plates':len(data['plates']),
        'joints':g.number_of_nodes(),'graph_segments':g.number_of_edges()}


def fingerprint(mesh):
    return sorted(tuple(round(v,7) for v in mesh.vertex_coordinates(i)) for i in mesh.vertices())


def verify_source(data):
    source=json.loads((ROOT/'model-renders/garage-model.json').read_text())
    objs=[o for o in source['objects'] if o['name'].startswith('T1 ') and o['group']=='frame']
    expected=sorted(sorted(tuple(round(v/.0254,7) for v in xyz) for xyz in o['vertices']) for o in objs)
    actual=sorted(fingerprint(el.modelgeometry) for el in data['model'].elements())
    if expected!=actual:raise ValueError('Parametric baseline differs from original T1 mesh envelopes')
    return f'All {len(objs)} baseline member/plate vertex sets match original T1 to 1e-7 inches'


def test_failures(data):
    results={}
    def reject(label,edit):
        d=copy.deepcopy(data)
        try:edit(d);validate_truss(d)
        except ValueError as exc:results[label]=str(exc)
        else:raise AssertionError('Invalid model accepted: '+label)
    def offset(d):
        el=next(e for e in d['model'].elements() if e.name=='T1.brace.west');el.end.x+=1
    reject('brace endpoint moved off joint',offset)
    reject('missing joint',lambda d:d['graph'].delete_node('U1'))
    reject('lost graph connection',lambda d:d['graph'].delete_edge(('L0','U1')))
    reject('negative span',lambda d:d['parameters'].update(span=-1))
    reject('noninteger panels',lambda d:d['parameters'].update(panels=6.5))
    return results


def render(cases):
    fig,axs=plt.subplots(len(cases),1,figsize=(14,12))
    fig.suptitle('T1 / PROGRAMMATIC GEOMETRY TEST',fontsize=20,weight='bold',color=INK)
    plot=go.Figure();starts=[]
    for ax,(key,title,data) in zip(axs,cases):
        p=TrussParameters(**data['parameters']);start=len(plot.data)
        for el in data['model'].elements():
            mesh=el.modelgeometry;xyz=np.array(mesh.vertices_attributes('xyz'))
            pts=xyz[:,[0,2]];pts=np.unique(np.round(pts,8),axis=0)
            ax.add_patch(Patch(pts[ConvexHull(pts).vertices],fc=ORANGE,ec=ORANGE,lw=.3))
            vs,fs=mesh.to_vertices_and_faces();vertices=np.array(vs)
            tris=np.array([[f[0],f[i],f[i+1]] for f in fs for i in range(1,len(f)-1)])
            plot.add_trace(go.Mesh3d(x=vertices[:,0],y=vertices[:,1],z=vertices[:,2],i=tris[:,0],j=tris[:,1],k=tris[:,2],
                color=BLUE if el.name in data['plates'] else ORANGE,name=el.name,showlegend=False,
                visible=key=='baseline',hovertemplate=el.name+'<br>X %{x:.2f} · Y %{y:.2f} · Z %{z:.2f} in<extra></extra>'))
        g=data['graph'];nodes=list(g.nodes());xyz=np.array([g.node_coordinates(n) for n in nodes])
        plot.add_trace(go.Scatter3d(x=xyz[:,0],y=xyz[:,1],z=xyz[:,2],text=nodes,mode='markers',
            marker=dict(size=4,color=INK),name='Shared joints',showlegend=False,visible=key=='baseline',hovertemplate='%{text}<extra></extra>'))
        starts.append((start,len(plot.data),title,p))
        for n in nodes:
            x,y,z=g.node_coordinates(n)
            ax.plot(x,z,'o',ms=3,color=INK);ax.text(x,z+4 if n.startswith('U') else z-7,n,ha='center',fontsize=8)
        ax.set_title(f'{title}   |   span {p.span:g} in · depth {p.depth:.3f} in · {p.panels} bays',loc='left',fontsize=12)
        ax.set_xlim(-8,max(d['parameters']['span'] for _,_,d in cases)+8)
        ax.set_ylim(p.bottom-14,max(d['parameters']['bottom']+d['parameters']['depth'] for _,_,d in cases)+15)
        ax.set_aspect('equal');ax.grid(alpha=.12);ax.set_ylabel('Z (in)');ax.set_xlabel('X (in)')
    fig.text(.075,.025,'Original end-braced concept layout. Variants test regeneration only. Joint dots mark geometric attachments, not designed connections.\nSpan is between end joint centers; 3-in end uprights extend 1.5 in beyond them. No structural analysis or source-plan changes.',fontsize=9,color=INK)
    fig.tight_layout(rect=(.02,.06,.98,.94))
    for ext in ('png','svg','pdf'):fig.savefig(OUT/f'parametric-T1.{ext}',dpi=150)
    plt.close(fig)
    buttons=[]
    for start,end,title,p in starts:
        buttons.append(dict(label=title,method='update',args=[{'visible':[start<=i<end for i in range(len(plot.data))]},
            {'title':{'text':f'T1 / {title}<br><sup>Span {p.span:g} in · depth {p.depth:.3f} in · geometric joints only</sup>', 'x':.04,'y':.98}}]))
    plot.update_layout(title=dict(text='T1 / Original source dimensions',x=.04,y=.98),height=720,
        scene=dict(aspectmode='manual',aspectratio=dict(x=2.16,y=.16,z=1),xaxis=dict(title='X (in)',range=[-10,260]),yaxis=dict(title='Y (in)',range=[60,80]),
            zaxis=dict(title='Z (in)',range=[85,210]),camera=dict(eye=dict(x=.2,y=-2,z=.35))),
        updatemenus=[dict(buttons=buttons,direction='down',x=0,y=1.05,xanchor='left')],
        margin=dict(l=20,r=20,b=20,t=130))
    plot.write_html(OUT/'parametric-T1.html',include_plotlyjs=True,config={'displaylogo':False,'responsive':True})


def main():
    OUT.mkdir(exist_ok=True)
    p=source_parameters()
    specs=[('baseline','Original source dimensions',p),
           ('span-plus-24','Span +24 inches',replace(p,span=p.span+24)),
           ('depth-plus-12','Depth +12 inches',replace(p,depth=p.depth+12))]
    cases=[];report={'cases':{},'sources':{},'checks':[]}
    for path in ['structural-study/framing-member-register.json','model-renders/garage-model.json','model-renders/build_and_render.py']:
        report['sources'][path]=hashlib.sha256((ROOT/path).read_bytes()).hexdigest()
    for key,title,params in specs:
        d=make_truss(params);validate_truss(d)
        path=OUT/f'T1-{key}.compas.json';json_dump(d,path,pretty=True)
        loaded=json_load(path);counts=validate_truss(loaded)
        before={e.name:fingerprint(e.modelgeometry) for e in d['model'].elements()}
        after={e.name:fingerprint(e.modelgeometry) for e in loaded['model'].elements()}
        if before!=after:raise ValueError('Roundtrip changed regenerated geometry')
        report['cases'][key]={'parameters':asdict(params),**counts,'roundtrip':'passed'}
        cases.append((key,title,loaded))
        with (OUT/f'T1-{key}-members.csv').open('w') as f:
            writer=csv.writer(f);writer.writerow(['id','role','from_joint','to_joint','centerline_length_in','section_width_in','section_depth_in'])
            for el in loaded['model'].elements():
                if el.name in loaded['members']:
                    meta=loaded['members'][el.name];writer.writerow([el.name,meta['role'],meta['joints'][0],meta['joints'][-1],el.start.distance_to_point(el.end),el.width,el.depth])
    report['checks'].append(verify_source(cases[0][2]))
    report['expected_failures']=test_failures(cases[0][2])
    # Confirm controlled changes preserve IDs/topology and affect the expected lengths.
    models=[{e.name:e for e in d['model'].elements()} for _,_,d in cases]
    if not all(set(m)==set(models[0]) for m in models):raise ValueError('Changing dimensions changed member IDs')
    length=lambda e:e.start.distance_to_point(e.end)
    if not math.isclose(length(models[1]['T1.bottom'])-length(models[0]['T1.bottom']),24):raise ValueError('Span change not propagated')
    if not math.isclose(length(models[2]['T1.upright.0'])-length(models[0]['T1.upright.0']),12):raise ValueError('Depth change not propagated')
    report['checks']+=['Three variants preserve member IDs and shared-joint topology',
        'Span +24 propagates to chord length; depth +12 propagates to upright length',
        'All plates remain attached to their regenerated upper joints',
        'All three models reloaded and validated before drawing']
    (OUT/'parametric-T1-validation.json').write_text(json.dumps(report,indent=2)+'\n')
    render(cases)
    print(json.dumps(report,indent=2))


if __name__=='__main__':main()
