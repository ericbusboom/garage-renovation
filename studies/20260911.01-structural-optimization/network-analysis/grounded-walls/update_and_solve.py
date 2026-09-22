"""Flatten TN, retain roof envelope, export a unique ground-supported global network."""
import json,copy,sys,hashlib
from pathlib import Path
import numpy as np
P=Path(__file__).resolve().parent; ROOT=P.parent.parent;sys.path.insert(0,str(ROOT))
import export_truss_submodels as ex
import iterate_design as q
c=json.loads((P.parent/'two-chord-design/geometry.json').read_text()); old={m['id']:copy.deepcopy(m) for m in c['members']}; mm={m['id']:m for m in c['members']}
tops={k for k,m in old.items() if m.get('truss')=='TN' and m['role']=='top_chord'}; keep='T-N top / segment 1'; level=224.25
mm[keep]['a']=[-32.,249.,level];mm[keep]['b']=[249.5,249.,level];changes={}
for con in c['connectivity']['intended_connections']:
 for side,other in [('from','to'),('to','from')]:
  s=con[side]
  if s['member_id'] not in tops:continue
  om=old[s['member_id']];pt=np.array(om['a'])+s['axis_fraction']*(np.array(om['b'])-om['a']);dz=level-pt[2]
  s['member_id']=keep;s['axis_fraction']=float((pt[0]+32)/281.5)
  o=con[other];m=mm[o['member_id']];t=o['axis_fraction']
  if m['axis_source'].get('ground_post'):o['axis_fraction']=(level-m['a'][2])/(m['b'][2]-m['a'][2])
  elif m.get('truss')=='TN' and m['role']!='top_chord' or m['id'].startswith('BR-'):
   assert min(abs(t),abs(t-1))<1e-6,(m['id'],t)
   end='a' if t<.5 else 'b';key=(m['id'],end)
   if key in changes:assert abs(changes[key]-dz)<1e-5
   changes[key]=dz
for (mid,end),dz in changes.items():mm[mid][end][2]+=dz
c['members']=[m for m in c['members'] if m['id'] not in tops-{keep}]
for m in c['members']:m['length_inches']=float(np.linalg.norm(np.array(m['b'])-m['a']))
for con in c['connectivity']['intended_connections']:
 for side in ['from','to']:
  s=con[side];m=mm[s['member_id']];t=s['axis_fraction'];assert -1e-6<=t<=1.000001
  s['point']=((1-t)*np.array(m['a'])+t*np.array(m['b'])).tolist()
 con['offset_vector_inches']=(np.array(con['to']['point'])-con['from']['point']).tolist();con['axis_gap_inches']=float(np.linalg.norm(con['offset_vector_inches']))
c['revision_note']='TN continuous horizontal upper chord axis224.25in; TE/TW unchanged. Unique ground columns; no new ground post in garage opening. Full global network exported.'
(P/'geometry.json').write_text(json.dumps(c,indent=2));ex.a.CAD=c;q.MEM.update(mm)

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
 r=ex.a.analyze('grounded_'+stage,remove=['W2'],selection=ex.selection,catalog=q.CAT,link_factor=10,demand_export=True,lateral_sensitivity=True,study_stage=stage,export_hook=export,export_basic_cases=True)
 assert r['status']=='solved_conditional',r.get('traceback',r)
 r['member_screen']=q.screen(r,ex.selection);r['max_member_screen_ratio']=max(v['ratio'] for v in r['member_screen'].values());(P/('global-'+stage+'.json')).write_text(json.dumps(r,indent=2,default=lambda v:v.item()));print(stage,r['max_member_screen_ratio'],flush=True)
r=ex.a.analyze('grounded_PDelta',remove=['W2'],selection=ex.selection,catalog=q.CAT,link_factor=10,second_order=True,demand_export=True,lateral_sensitivity=True)
assert r['status']=='solved_conditional',r.get('traceback',r)
r['member_screen']=q.screen(r,ex.selection);r['max_member_screen_ratio']=max(v['ratio'] for v in r['member_screen'].values());(P/'global-complete-PDelta.json').write_text(json.dumps(r,indent=2,default=lambda v:v.item()));print('PDelta',r['max_member_screen_ratio'],flush=True)
