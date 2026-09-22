import json,copy
from pathlib import Path
import numpy as np
P=Path(__file__).resolve().parent;c=json.loads((P.parent/'tn-door-correction/geometry.json').read_text());old=copy.deepcopy(c);mm={m['id']:m for m in c['members']};braces={'BR-N-ground-1','BR-N-ground-2'};checks=[]
for co in c['connectivity']['intended_connections']:
 for side,other in [('from','to'),('to','from')]:
  r=co[side]
  if r['member_id'] not in braces:continue
  assert r['axis_fraction'] in [0,1]
  target=co[other];post=mm[target['member_id']];assert target['member_id'] in ['W4','N1 / U-W'];t=target['axis_fraction'];pt=((1-t)*np.array(post['a'])+t*np.array(post['b'])).tolist();end='a' if r['axis_fraction']==0 else 'b';mm[r['member_id']][end]=pt
for co in c['connectivity']['intended_connections']:
 for side in ['from','to']:
  r=co[side];m=mm[r['member_id']];t=r['axis_fraction'];r['point']=((1-t)*np.array(m['a'])+t*np.array(m['b'])).tolist()
 v=np.array(co['to']['point'])-co['from']['point'];co['offset_vector_inches']=v.tolist();co['axis_gap_inches']=float(np.linalg.norm(v))
 if any(co[s]['member_id'] in braces for s in ['from','to']):assert co['axis_gap_inches']<1e-8;checks.append(co['id'])
for m in c['members']:
 if m['id'] in braces:m['length_inches']=float(np.linalg.norm(np.array(m['b'])-m['a']))
for m,was in zip(c['members'],old['members']):
 if m['id'] not in braces:assert m==was
assert len(checks)==4
c['revision_note']='Only BR-N-ground-1/2 moved onto W4/N1 column axes. Four4in northward eccentric offsets eliminated; brace endpoint heights unchanged. TN mini-truss and all other physical members unchanged.'
(P/'geometry.json').write_text(json.dumps(c,indent=2));(P/'geometry-checks.json').write_text(json.dumps(dict(aligned_braces=sorted(braces),coincident_column_joints=checks,removed_offset_in=4,previous_offset_direction='north',all_other_members_unchanged=True),indent=2));print('Four brace-column endpoints exactly coincident')
