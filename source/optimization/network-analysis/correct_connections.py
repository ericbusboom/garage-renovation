"""Explicit proposed fixes to three missing physical-joint representations."""
import json,copy,importlib.util
from pathlib import Path
import numpy as np
P=Path(__file__).resolve().parent;O=P/'connected-candidate';O.mkdir(exist_ok=True)
for path in sorted(P.glob('*.network.json')):
 d=json.loads(path.read_text());g=d['truss'];changes=[]
 if g in ['TE','TW']:
  matches=[n for n,p in d['nodes'].items() if abs(p[2]-122.762)<.002 and p[1]>223]
  assert len(matches)==2
  a,b=sorted(matches,key=lambda n:d['nodes'][n][1])
  d['elements'].append(dict(id='FIX_TOP_KNEE',i=a,j=b,section='connection_offset',material='steel',physical_member='Proposed '+g+' top-chord knee connection',kind='connection_offset',releases=[False]*12))
  changes.append('Connect the upper-chord axes at the roof transition with a 1.843 in centroid-offset joint; physical connection detail remains to be designed.')
 if g=='TN':
  target=np.array([155.25,115.,249.]);node='FIX_JAMB_BASE'
  candidates=[]
  for e in d['elements']:
   if e['physical_member']!='T-N':continue
   a=np.array(d['nodes'][e['i']]);b=np.array(d['nodes'][e['j']]);t=float(np.dot(target-a,b-a)/np.dot(b-a,b-a))
   if 0<t<1 and np.linalg.norm(a+t*(b-a)-target)<1e-6:candidates.append((e,t))
  assert len(candidates)==1
  e,t=candidates[0];d['elements'].remove(e);d['nodes'][node]=target.tolist()
  for key,ni,nj in [(e['id']+'_a',e['i'],node),(e['id']+'_b',node,e['j'])]:d['elements'].append({**e,'id':key,'i':ni,'j':nj})
  jamb=next(n for n,p in d['nodes'].items() if np.linalg.norm(np.array(p)-[155.25,120,249])<1e-6)
  d['elements'].append(dict(id='FIX_JAMB_SEAT',i=node,j=jamb,section='connection_offset',material='steel',physical_member='Proposed TN jamb to lower-chord connection',kind='connection_offset',releases=[False]*12))
  for case in d['loads']:d['loads'][case][node]=[0.]*6
  # The added node is free, not constrained. Interpolation is reference metadata only.
  for case,r in d['reference'].items():r['displacements'][node]=((1-t)*np.array(r['displacements'][e['i']])+t*np.array(r['displacements'][e['j']])).tolist()
  changes.append('Connect east upper jamb at 120 in to the lower chord at 115 in, adding an explicit lower-chord node and a 5 in centroid-offset seat connection. No new ground column.')
 d['proposed_connection_changes']=changes;d['comparison_policy']='Reaction/displacement differences from original are expected after connection corrections; no global load redistribution update claimed.'
 graph={n:set() for n in d['nodes']}
 pairs=set()
 for e in d['elements']:
  pair=tuple(sorted([e['i'],e['j']]))
  assert pair not in pairs;pairs.add(pair)
  graph[e['i']].add(e['j']);graph[e['j']].add(e['i'])
 seen=set();todo=[next(iter(graph))]
 while todo:
  n=todo.pop()
  if n in seen:continue
  seen.add(n);todo.extend(graph[n]-seen)
 assert len(seen)==len(graph)
 d['audit']={**d['audit'],'nodes':len(graph),'elements':len(d['elements']),'degree_one_nodes':[n for n,v in graph.items() if len(v)==1],'connected_components':1,'offset_elements':sum(e['kind']=='connection_offset' for e in d['elements'])}
 (O/path.name).write_text(json.dumps(d,indent=2))
print('Corrected candidate network files written')
