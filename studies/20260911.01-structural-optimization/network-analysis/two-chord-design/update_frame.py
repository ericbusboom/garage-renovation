"""Two physical upper-chord runs per TE/TW; hip-cap secondary frame excluded."""
import json,copy,sys
from pathlib import Path
import numpy as np
P=Path(__file__).resolve().parent;ROOT=P.parent.parent;sys.path.insert(0,str(ROOT))
import export_truss_submodels as ex
import iterate_design as q
c=json.loads((P.parent/'global-connected-geometry.json').read_text());old={m['id']:copy.deepcopy(m) for m in c['members']};mm={m['id']:m for m in c['members']};knee=122.7624491117621;level=224.25
caps={mid for mid,m in old.items() if m.get('truss') in ['TE','TW'] and m['role']=='top_chord' and not mid.endswith('segment 1')}
c['roof_envelope_reference_members']=[copy.deepcopy(m) for m in old.values() if m.get('truss') in ['TE','TW'] and m['role']=='top_chord']
for tr,prefix in [('TE','T-E'),('TW','T-W')]:
 m=mm[prefix+' top / segment 2'];m['a']=[m['a'][0],knee,level];m['b']=[m['b'][0],253.,level];m['design_note']='One continuous horizontal physical upper-chord run beneath the separately framed metal hip cap.'
 m['section_description']='Existing stock section retained; joints/load stations subdivide FE mesh only.'
removed=caps-{'T-E top / segment 2','T-W top / segment 2'}
changes={}
for con in c['connectivity']['intended_connections']:
 for side,other in [('from','to'),('to','from')]:
  s=con[side];mid=s['member_id']
  if mid not in caps:continue
  a=np.array(old[mid]['a']);b=np.array(old[mid]['b']);pt=a+s['axis_fraction']*(b-a);dz=level-pt[2]
  s['member_id']=('T-E' if old[mid]['truss']=='TE' else 'T-W')+' top / segment 2';s['axis_fraction']=float((pt[1]-knee)/(253-knee))
  o=con[other];om=mm[o['member_id']];t=o['axis_fraction']
  if om.get('truss') in ['TE','TW'] and om['role']!='top_chord' or om['id'].startswith('BR-'):
   if abs(t)<1e-7 or abs(t-1)<1e-7:
    endpoint='a' if t<.5 else 'b';key=(om['id'],endpoint)
    if key in changes:assert abs(changes[key]-dz)<1e-5
    changes[key]=dz
  elif om['axis_source'].get('ground_post'):
   # Place the cap-chord connection on the column at the new chord elevation.
   o['axis_fraction']=float((level-om['a'][2])/(om['b'][2]-om['a'][2]))
for (mid,end),dz in changes.items():mm[mid][end][2]+=dz
c['members']=[m for m in c['members'] if m['id'] not in removed]
for m in c['members']:m['length_inches']=float(np.linalg.norm(np.array(m['b'])-m['a']))
for con in c['connectivity']['intended_connections']:
 for side in ['from','to']:
  s=con[side];m=mm[s['member_id']];t=s['axis_fraction'];assert -1e-7<=t<=1.0000001
  s['point']=((1-t)*np.array(m['a'])+t*np.array(m['b'])).tolist()
 con['axis_gap_inches']=float(np.linalg.norm(np.array(con['to']['point'])-con['from']['point']))
 con['offset_vector_inches']=(np.array(con['to']['point'])-con['from']['point']).tolist()
c['revision_note']='TE/TW: one retained sloping upper chord, one horizontal upper chord at z224.25in; old hip-cap roof envelope and load allowances retained, separate cap framing not sized.'
for tr in ['TE','TW']:
 tops=[m for m in c['members'] if m.get('truss')==tr and m['role']=='top_chord'];assert len(tops)==2
 tops.sort(key=lambda m:m['a'][1]);assert np.allclose(tops[0]['b'],tops[1]['a']);assert tops[1]['a'][2]==tops[1]['b'][2]
(P/'geometry.json').write_text(json.dumps(c,indent=2));ex.a.CAD=c;ex.OUT=P/'source';ex.OUT.mkdir(exist_ok=True);q.MEM.update({m['id']:m for m in c['members']})
for stage in ['complete','roof_first']:
 r=ex.a.analyze('two_chord_'+stage,remove=['W2'],selection=ex.selection,catalog=q.CAT,link_factor=10,demand_export=True,lateral_sensitivity=True,study_stage=stage,export_hook=ex.export,export_basic_cases=True)
 assert r['status']=='solved_conditional',r.get('traceback',r)
 r['member_screen']=q.screen(r,ex.selection);r['max_member_screen_ratio']=max(v['ratio'] for v in r['member_screen'].values())
 (ex.OUT/('global-'+stage+'.json')).write_text(json.dumps(r,indent=2,default=lambda v:v.item()))
 print(stage,'solved',r['max_member_screen_ratio'],flush=True)
r=ex.a.analyze('two_chord_PDelta',remove=['W2'],selection=ex.selection,catalog=q.CAT,link_factor=10,second_order=True,demand_export=True,lateral_sensitivity=True)
assert r['status']=='solved_conditional',r.get('traceback',r)
r['member_screen']=q.screen(r,ex.selection);r['max_member_screen_ratio']=max(v['ratio'] for v in r['member_screen'].values());(ex.OUT/'global-complete-PDelta.json').write_text(json.dumps(r,indent=2,default=lambda v:v.item()))
print('PDelta solved',r['max_member_screen_ratio'],flush=True)
