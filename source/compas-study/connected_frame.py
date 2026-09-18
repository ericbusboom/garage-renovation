"""Compile authoritative frame-spec.json into COMPAS graph, model, meshes and audits.
No nearest-neighbour snapping is used in the compiler. All connections are declared.
"""
import copy,csv,hashlib,json,math
from collections import defaultdict
from itertools import combinations
from pathlib import Path
import numpy as np
from compas.data import json_dump,json_load
from compas.datastructures import Graph
from compas.geometry import Point,Line,closest_point_on_segment,distance_point_point
from compas_model.models import Model
from geometry_types import MemberElement
import frame_models
ROOT=Path(__file__).resolve().parents[1];P=ROOT/'roof-studies/square-upper-west';OUT=P/'connected-frame'

def compile_spec(spec):
 nodes=spec['nodes'];members=spec['members'];params=spec['parameters'];resolved={};active=set()
 def point(key):
  if key in resolved:return resolved[key]
  if key in active:raise ValueError('Cyclic joint dependency: '+key)
  if key not in nodes:raise ValueError('Missing joint: '+key)
  active.add(key);n=nodes[key]
  if 'on_member' in n:
   if n['on_member'] not in members:raise ValueError('Missing attachment member: '+key)
   a,b=[np.array(point(k)) for k in members[n['on_member']]['nodes']]
   if 'station' in n:
    axis=n['station']['axis'];v=n['station']['value']
    if isinstance(v,dict):v=params['solar_start_z']+(params[v['solar_at_y']]-params['south_y'])*params['solar_slope']
    elif isinstance(v,str):v=params[v]
    if abs(b[axis]-a[axis])<1e-10:raise ValueError('Undefined attachment station: '+key)
    t=(v-a[axis])/(b[axis]-a[axis])
   else:t=n['fraction']
   if not -1e-9<=t<=1+1e-9:raise ValueError('Attachment outside member: '+key)
   p=a+t*(b-a)
  elif 'offset_from' in n:p=np.array(point(n['offset_from']))+n['offset']
  else:p=[params[v] if isinstance(v,str) else v for v in n['xyz']]
  p=[float(v) for v in p]
  if len(p)!=3 or not all(math.isfinite(v) for v in p):raise ValueError('Invalid joint: '+key)
  resolved[key]=p;active.remove(key);return p
 for n in nodes:point(n)
 # Named support requirements catch a connected but incorrectly positioned column.
 for rule in spec.get('support_alignments',[]):
  mid=rule['member'];m=members[mid];a,b=[resolved[n] for n in m['nodes']]
  if rule.get('vertical') and not np.allclose(a[:2],b[:2],rtol=0,atol=1e-7):raise ValueError('Support is not vertically below its truss: '+mid)
  if abs(a[2]-rule['base_z'])>1e-7:raise ValueError('Wrong support base elevation: '+mid)
  target=members[rule['supports']];line=[resolved[n] for n in target['nodes']]
  if distance_point_point(b,closest_point_on_segment(b,line))>1e-7:raise ValueError('Support top misses required truss: '+mid)
 # Keep the south entry opening clear and its support post vertical.
 if spec.get('south_entry_alignment'):
  rule=spec['south_entry_alignment'];m=members[rule['member']]
  a,b=[resolved[n] for n in m['nodes']]
  edge=params[rule['door_east_x_parameter']]
  if not np.allclose(a[:2],b[:2],rtol=0,atol=1e-7) or abs(a[0]-m['width']/2-edge)>1e-7:
   raise ValueError('S1 west face must align with south entry east edge')
 # North doorway rules: centered split, shortened N1 and full western-half header.
 if spec.get('north_opening'):
  opening=spec['north_opening'];center=members[opening['center_member']]
  lower=np.array([resolved[n] for n in members['T-N']['nodes']]);upper=np.array([resolved[n] for n in members['T-N top / segment 1']['nodes']])
  if not np.allclose(resolved[center['nodes'][0]],lower.mean(axis=0)) or not np.allclose(resolved[center['nodes'][1]],upper.mean(axis=0)):raise ValueError('North vertical must bisect both chords')
  n1top=resolved[members['N1 / U-W']['nodes'][1]]
  if distance_point_point(n1top,closest_point_on_segment(n1top,lower))>1e-7:raise ValueError('N1 must end at north lower chord')
  header=np.array([resolved[n] for n in members[opening['header']]['nodes']])
  if not np.allclose(header[:,0],[lower[0,0],lower[:,0].mean()]) or not np.allclose(header[:,2],opening['header_axis_z']):raise ValueError('Header must span the western half at its declared height')
 # Shared explicit locations may have multiple readable aliases. Merge their IDs,
 # not arbitrary line crossings or near misses. Tolerance is numerical (1e-7 in).
 aliases={};coords={};canonical={}
 for n,p in resolved.items():
  k=tuple(round(v,7) for v in p)
  if k not in canonical:canonical[k]=n;coords[n]=p
  aliases[n]=canonical[k]
 incidence=defaultdict(set);attachments=defaultdict(set);supports=set();free=set()
 for n,d in nodes.items():
  if d.get('support'):supports.add(aliases[n])
  if d.get('free_end'):free.add(aliases[n])
  if 'on_member' in d:incidence[aliases[n]].add(d['on_member']);attachments[d['on_member']].add(aliases[n])
 for mid,m in members.items():
  if len(m['nodes'])!=2:raise ValueError('Member needs two endpoint references: '+mid)
  for n in m['nodes']:incidence[aliases[n]].add(mid);attachments[mid].add(aliases[n])
 # E-M has a declared one-inch eccentric bearing connection within section envelopes.
 for n,d in nodes.items():
  if 'offset_from' in d:
   target=aliases[d['offset_from']];key=aliases[n]
   incidence[key].update(incidence[target]);incidence[target].update(incidence[key])
 graph=Graph(name='Garage shared geometric joints');model=Model(name='Connected garage frame');elements={};rows=[]
 for n,p in coords.items():graph.add_node(n,x=p[0],y=p[1],z=p[2],support=n in supports,free_end=n in free,members=sorted(incidence[n]))
 for mid,m in members.items():
  a,b=[resolved[n] for n in m['nodes']];el=MemberElement(a,b,m['width'],m['depth'],name=mid);mesh=el.compute_elementgeometry()
  if not mesh.is_valid() or not mesh.is_closed():raise ValueError('Invalid closed member mesh: '+mid)
  model.add_element(el);elements[mid]=el
  axis=np.array(b)-a;length=np.linalg.norm(axis)
  att=sorted(attachments[mid],key=lambda n:np.dot(np.array(coords[n])-a,axis)/length**2)
  for n in att:
   if distance_point_point(coords[n],closest_point_on_segment(coords[n],(a,b)))>1e-6:raise ValueError('Attachment off member: '+mid+' / '+n)
  for u,v in zip(att,att[1:]):
   if u==v:continue
   existing=graph.edge_attribute((u,v),'members') if graph.has_edge((u,v)) else []
   graph.add_edge(u,v,members=(existing or [])+[mid],kind='member segment')
  for end,n in zip(('start','end'),m['nodes']):
   key=aliases[n];others=sorted(incidence[key]-{mid})
   status='connected' if others else 'ground support' if key in supports else 'declared overhang' if key in free else 'DISCONNECTED'
   if status=='DISCONNECTED':raise ValueError('Unconnected end: '+mid+' / '+end+' / '+n)
   rows.append({'member':mid,'end':end,'joint':n,'status':status,'connected_to':'; '.join(others),'gap_in':0.,'source_member':m['source_name']})
 for n,d in nodes.items():
  if 'offset_from' in d:graph.add_edge(aliases[n],aliases[d['offset_from']],kind='declared eccentric bearing',members=[])
 # Element interactions are explicit and serialized with COMPAS Model as well.
 linked=set()
 for n,group in incidence.items():
  for a,b in combinations(sorted(group),2):
   if (a,b) not in linked:model.add_interaction(elements[a],elements[b]);linked.add((a,b))
 # No disconnected frame islands; every node has a route to an explicit ground support.
 seen=set();todo=list(supports)
 while todo:
  n=todo.pop()
  if n not in seen:seen.add(n);todo.extend(graph.neighbors(n))
 if seen!=set(graph.nodes()):raise ValueError('Frame nodes without path to a support: '+str(set(graph.nodes())-seen))
 covered={m['source_name'] for m in members.values()}|set(spec['retired_members'])
 if covered!=set(spec['source_inventory']):raise ValueError('Source inventory coverage mismatch')
 return dict(nodes=resolved,aliases=aliases,graph=graph,model=model,elements=elements,rows=rows,interactions=len(linked))

def geometry(c,spec):
 objects=[]
 for mid,m in spec['members'].items():
  vs,faces=c['elements'][mid].compute_elementgeometry().to_vertices_and_faces()
  tri=[[f[0],f[i],f[i+1]] for f in faces for i in range(1,len(f)-1)]
  objects.append(dict(name=m.get('display_name',m['source_name']),member_id=mid,group=m['group'],material=m['material'],vertices=vs,triangles=tri,
    start=c['nodes'][m['nodes'][0]],end=c['nodes'][m['nodes'][1]],joint_ids=m['nodes'],width=m['width'],depth=m['depth']))
 return objects

def tests(spec,base):
 results=[]
 # Shared-node edit: extend east row; all dependent framing regenerates from the same specification.
 for name,edit in [('east row moved 12 inches',lambda s:s['parameters'].__setitem__('east_x',s['parameters']['east_x']+12)),
                   ('square chord raised 6 inches',lambda s:s['parameters'].__setitem__('square_top_z',s['parameters']['square_top_z']+6))]:
  changed=copy.deepcopy(spec);edit(changed);c=compile_spec(changed)
  assert any(not np.allclose(c['nodes'][n],base['nodes'][n]) for n in c['nodes'])
  assert len(c['rows'])==len(base['rows'])
  for side in ('W','E'):
   for label in ('south.bottom','north.bottom'):
    assert abs(c['nodes'][side+'.'+label][2]-spec['parameters']['bottom_z'])<1e-7
  results.append({'test':name,'result':'all endpoints and support paths remain connected'})
 for name,edit in [('east support moved off truss axis',lambda s:s['nodes']['S3.base']['xyz'].__setitem__(0,189.4791296625222)),
                   ('missing joint reference',lambda s:s['nodes'].pop('W.front.top')),
                   ('attachment beyond member end',lambda s:s['nodes'][next(n for n,v in s['nodes'].items() if 'fraction' in v)].update(fraction=1.1)),
                   ('isolated beam end',lambda s:(s['nodes'].update({'bad':{'xyz':[1000,1000,1000]}}),s['members']['BR-R-main-1']['nodes'].__setitem__(1,'bad')))]:
  changed=copy.deepcopy(spec);edit(changed)
  try:compile_spec(changed)
  except ValueError as e:results.append({'test':name,'result':'rejected','message':str(e)})
  else:raise AssertionError('Invalid specification accepted: '+name)
 return results

def main():
 spec=json.loads((OUT/'frame-spec.json').read_text());c=compile_spec(spec);test_results=tests(spec,c)
 data={'specification':spec,'joint_graph':c['graph'],'model':c['model']}
 dest=frame_models.allocate('square-upper-west')
 json_dump(data,dest);rt=json_load(dest);verify=compile_spec(rt['specification'])
 assert rt['joint_graph'].number_of_nodes()==c['graph'].number_of_nodes()
 saved={el.name:el for el in rt['model'].elements()}
 for mid,el in verify['elements'].items():
  assert np.allclose(list(saved[mid].start),list(el.start)) and np.allclose(list(saved[mid].end),list(el.end))
 old=json.loads((P/'cad-mesh.json').read_text());inventory=set(spec['source_inventory'])
 scene=[o for o in old['objects'] if o['name'] not in inventory]+geometry(c,spec)
 (OUT/'scene-mesh.json').write_text(json.dumps({'objects':scene,'units':'inches','source':'frame-spec.json -> COMPAS Graph + Model; enclosure from prior CAD study'}))
 with (OUT/'member-end-audit.csv').open('w') as f:
  w=csv.DictWriter(f,fieldnames=list(c['rows'][0]));w.writeheader();w.writerows(c['rows'])
 audit={'members':len(spec['members']),'member_ends':len(c['rows']),'disconnected_ends':0,'joint_nodes':c['graph'].number_of_nodes(),'element_interactions':c['interactions'],
 'all_members_have_path_to_ground_support':True,'source_members_accounted_for':len(inventory),'retired_members':spec['retired_members'],
 'support_alignments':[{**r,'base':c['nodes'][spec['members'][r['member']]['nodes'][0]],'top':c['nodes'][spec['members'][r['member']]['nodes'][1]]} for r in spec.get('support_alignments',[])],
 'ground_supports':sum(n.get('support',False)!=False for n in spec['nodes'].values()),'declared_free_ends':{n:v['free_end'] for n,v in spec['nodes'].items() if 'free_end' in v},
 'spec_sha256':hashlib.sha256((OUT/'frame-spec.json').read_bytes()).hexdigest(),'tests':test_results,
 'meaning':'Explicit geometric connectivity and regeneration checks; this is not a verification of joints, stability, forces or capacity.'}
 (OUT/'connectivity-audit.json').write_text(json.dumps(audit,indent=2));print(json.dumps(audit,indent=2))
if __name__=='__main__':main()
