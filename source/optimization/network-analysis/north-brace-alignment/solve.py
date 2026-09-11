import json,sys,hashlib
from pathlib import Path
import numpy as np
P=Path(__file__).resolve().parent;ROOT=P.parent.parent;sys.path.insert(0,str(ROOT))
import export_truss_submodels as ex
import iterate_design as q
c=json.loads((P/'geometry.json').read_text());ex.a.CAD=c;q.MEM.update({m['id']:m for m in c['members']})
def export(M,members,pieces,links,combos,sections,coords,study_stage):
 physical={k:mid for k,mid,lo,hi in pieces}; linkmap={k:cid for k,ni,nj,cid in links};elements=[];stock={}
 for k,parent in M.members.items():
  mid=physical.get(k);sec=ex.selection[mid] if mid else 'offset'
  stock[sec]={p:float(getattr(parent.section,p)) for p in ['A','Iy','Iz','J']}
  for sub in parent.sub_members.values():elements.append(dict(id=sub.name,i=sub.i_node.name,j=sub.j_node.name,section=sec,physical_member=mid,connection_id=linkmap.get(k),releases=list(sub.Releases)))
 nodes={n:[v.X,v.Y,v.Z] for n,v in M.nodes.items()}; used={e[k] for e in elements for k in ['i','j']};assert used==set(nodes)
 graph={n:set() for n in nodes}
 for e in elements:
  assert np.linalg.norm(np.array(nodes[e['i']])-nodes[e['j']])>1e-7
  graph[e['i']].add(e['j']);graph[e['j']].add(e['i'])
 seen={next(iter(nodes))};todo=list(seen)
 while todo:
  for n in graph[todo.pop()]-seen:seen.add(n);todo.append(n)
 assert seen==set(nodes),'Disconnected global mesh'
 supports={n:[bool(getattr(v,'support_'+d)) for d in ['DX','DY','DZ','RX','RY','RZ']] for n,v in M.nodes.items() if any(getattr(v,'support_'+d) for d in ['DX','DY','DZ','RX','RY','RZ'])}
 ref={case:dict(displacements={n:[float(getattr(v,d)[case]) for d in ['DX','DY','DZ','RX','RY','RZ']] for n,v in M.nodes.items()},reactions={n:[float(getattr(M.nodes[n],d)[case]) for d in ['RxnFX','RxnFY','RxnFZ','RxnMX','RxnMY','RxnMZ']] for n in supports}) for case in combos}
 d=dict(schema='garage-global-grounded-v1',stage=study_stage,axes='X east,Y up,Z north; inches,pounds,radians',nodes=nodes,elements=elements,sections=stock,supports=supports,nodal_loads={n:v.NodeLoads for n,v in M.nodes.items() if v.NodeLoads},combinations=combos,reference=ref,physical_members=members,connections=c['connectivity']['intended_connections'],geometry_sha256=hashlib.sha256(json.dumps(c,sort_keys=True).encode()).hexdigest(),assumptions='Fixed column bases. Moment-connected elastic frame members, numerical centroid-offset links. Shared posts modeled once. No existing wall support credit. Preliminary, not construction design.')
 (P/(study_stage+'.network.json')).write_text(json.dumps(d));print('Exported',study_stage,len(nodes),len(elements),'base nodes',len(supports),flush=True)
for stage in ['complete','roof_first']:
 r=ex.a.analyze('clean_'+stage,remove=['W2'],selection=ex.selection,catalog=q.CAT,link_factor=10,demand_export=True,lateral_sensitivity=True,study_stage=stage,export_hook=export,export_basic_cases=True)
 assert r['status']=='solved_conditional',r.get('traceback',r)
 r['member_screen']=q.screen(r,ex.selection);r['max_member_screen_ratio']=max(v['ratio'] for v in r['member_screen'].values());(P/('global-'+stage+'.json')).write_text(json.dumps(r,indent=2,default=lambda v:v.item()));print(stage,r['max_member_screen_ratio'],flush=True)
r=ex.a.analyze('clean_PDelta',remove=['W2'],selection=ex.selection,catalog=q.CAT,link_factor=10,second_order=True,demand_export=True,lateral_sensitivity=True)
assert r['status']=='solved_conditional',r.get('traceback',r)
r['member_screen']=q.screen(r,ex.selection);r['max_member_screen_ratio']=max(v['ratio'] for v in r['member_screen'].values());(P/'global-complete-PDelta.json').write_text(json.dumps(r,indent=2,default=lambda v:v.item()));print('PDelta',r['max_member_screen_ratio'],flush=True)
