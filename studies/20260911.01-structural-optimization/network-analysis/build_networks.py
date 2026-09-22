"""Explicit solver networks from the solved CAD-linked Candidate 9 mesh.
Every connection-offset element is retained. No graphic geometry inference.
"""
import json,hashlib,os
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent;P=Path(os.environ.get('GARAGE_NETWORK_OUTPUT',str(ROOT/'network-analysis')));P.mkdir(exist_ok=True);SRC=Path(os.environ.get('GARAGE_NETWORK_SOURCE',str(ROOT/'truss-submodels')))
cad=json.loads((ROOT/'candidate9-candidate-geometry.json').read_text());members={m['id']:m for m in cad['members']};selection=json.loads((ROOT/'candidate9-candidate-selection.json').read_text());sections=json.loads((SRC/'global-complete.json').read_text())['sections']
import numpy as np
for stage in ['complete','roof_first']:
 for group in ['TE','TW','TN','TS','T1']:
  stem=group+'-'+stage;meta=json.loads((SRC/(stem+'.json')).read_text());arrays=np.load(SRC/(stem+'.npz'));names=list(meta['nodes']);boundary=set(meta['boundary_nodes']);elements=[]
  for e in meta['elements']:
   offset=e['member'].startswith('@');sec='connection_offset' if offset else selection[e['member']]
   elements.append(dict(id=e['name'],i=e['nodes'][0],j=e['nodes'][1],section=sec,material='steel',physical_member=e['member'],kind='connection_offset' if offset else members[e['member']]['role'],releases=[False]*12))
  stock={e['section']:sections[e['section']] for e in elements if e['section']!='connection_offset'}
  stock['connection_offset']=dict(A=100.,Iy=1000.,Iz=1000.,J=1000.,note='Numerical centroid-offset connection, baseline stiffness factor10; NOT a steel stock section or detailed connection design.')
  # Solver subdivision created two coincident offset segments in TE. Consolidate
  # parallel numerical links by summing stiffness, preserving the original baseline.
  unique={};merged=[]
  for e in elements:
   pair=tuple(sorted([e['i'],e['j']]))
   if pair in unique:
    old=unique[pair];assert old['kind']==e['kind']=='connection_offset'
    old.setdefault('parallel_source_ids',[old['id']]).append(e['id']);old['section']='connection_offset_parallel2'
    stock['connection_offset_parallel2']={**stock['connection_offset'],**{k:2*stock['connection_offset'][k] for k in ['A','Iy','Iz','J']}}
    merged.append([old['id'],e['id']])
   else:unique[pair]=e
  elements=list(unique.values())
  graph={n:set() for n in names};pairs=set();duplicates=[]
  for e in elements:
   assert e['i'] in graph and e['j'] in graph
   assert np.linalg.norm(np.array(meta['nodes'][e['i']])-meta['nodes'][e['j']])>1e-7
   pair=tuple(sorted([e['i'],e['j']]))
   if pair in pairs:duplicates.append(e['id'])
   pairs.add(pair);graph[e['i']].add(e['j']);graph[e['j']].add(e['i'])
  left=set(names);components=[]
  while left:
   todo=[next(iter(left))];seen=set(todo)
   while todo:
    for n in graph[todo.pop()]-seen:seen.add(n);todo.append(n)
   components.append(sorted(seen));left-=seen
  assert len(components)==1,(stem,'Disconnected network',components)
  assert not duplicates,(stem,duplicates)
  loads={};reference={}
  for ci,case in enumerate(meta['cases']):
   loads[case]={n:arrays['F'][ci,6*i:6*i+6].tolist() for i,n in enumerate(names) if n not in boundary}
   reference[case]=dict(displacements={n:arrays['U'][ci,6*i:6*i+6].tolist() for i,n in enumerate(names)},interface_actions={n:arrays['F'][ci,6*i:6*i+6].tolist() for i,n in enumerate(names) if n in boundary})
  data=dict(schema='garage-pynite-network-v1',truss=group,stage=stage,units='inch, pound, radians',axes='X east, Y up, Z north; positive moments right-hand about solver axes',nodes={n:[xyz[0],xyz[2],xyz[1]] for n,xyz in meta['nodes'].items()},elements=elements,sections=stock,materials={'steel':dict(E=29e6,G=29e6/2.6,nu=.3,rho=0,Fy=50000)},boundary_nodes=sorted(boundary),boundary_neighbors=meta['boundary_neighbors'],loads=loads,reference=reference,case_factors=meta['cases'],boundary_method='Prescribed six-component movements from global linear solution, per case. Do not add interface actions as loads.',analysis_assumptions='3D elastic beam-column elements, moment-connected joints and finite-stiffness offset links. Not a pin-jointed ideal truss. No old-wall support credit.',audit=dict(nodes=len(names),elements=len(elements),connected_components=len(components),offset_elements=sum(e['kind']=='connection_offset' for e in elements),duplicate_edges=duplicates,merged_parallel_offset_segments=merged,degree_one_nodes=[n for n in names if len(graph[n])==1],unreferenced_nodes=[n for n in names if not graph[n]]),source_sha256=hashlib.sha256((SRC/(stem+'.json')).read_bytes()).hexdigest(),eligible_for_construction=False)
  (P/(stem+'.network.json')).write_text(json.dumps(data,indent=2))
  print(stem,data['audit'])
