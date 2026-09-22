"""Eliminate duplicate uprights and superposed upper bracing systems; preserve real load paths."""
import json,copy
from pathlib import Path
import numpy as np
from audit_geometry import audit
P=Path(__file__).resolve().parent;c=json.loads((P.parent/'grounded-walls/geometry.json').read_text());old={m['id']:copy.deepcopy(m) for m in c['members']};mm={m['id']:m for m in c['members']}
merge={'T-S vertical 1':'W1','T-S vertical 7':'S3','T-W vertical 2':'W1','T-W vertical 5':'W3','T-W vertical 7':'W4','T-W vertical 11':'W3','T-W vertical 14':'T-W vertical 6','T-E vertical 2':'S3','T-E vertical 9':'N2','T-N vertical 1':'W4','T-N vertical 4':'N2','T-N vertical 10':'N1 / U-W','T-N vertical 14':'T-N upper east jamb','T1 vertical 1':'T-W vertical 3','T1 vertical 5':'T-E vertical 3','T1 future hanger 1':'T-W vertical 3','T1 future hanger 5':'T-E vertical 3'}
remove={'T-N vertical 2','T-N vertical 3','T-N diagonal 6','T-N diagonal 7','BR-N-upper-2','T-E vertical 5','T-E vertical 7','T-E vertical 8','BR-E-upper-2','T-W vertical 12','T-E diagonal 10','T-W diagonal 8'}
# Single north upper diagonal spans the W4-to-N1 panel; no overlaid narrow panels.
mm['BR-N-upper-1']['b']=[53.25,249.,224.25]
cons=[]
for con in c['connectivity']['intended_connections']:
 if any(con[s]['member_id'] in remove for s in ['from','to']):continue
 for s in ['from','to']:
  ref=con[s];mid=ref['member_id']
  if mid in merge:
   point=np.array(old[mid]['a'])+ref['axis_fraction']*(np.array(old[mid]['b'])-old[mid]['a']);target=mm[merge[mid]];a=np.array(target['a']);v=np.array(target['b'])-a
   ref['member_id']=merge[mid];ref['axis_fraction']=float(np.clip(np.dot(point-a,v)/np.dot(v,v),0,1))
 # Match the moved north diagonal endpoint on the existing horizontal chord.
 if any(con[s]['member_id']=='BR-N-upper-1' and con[s]['axis_fraction']==1 for s in ['from','to']):
  for s in ['from','to']:
   if con[s]['member_id']=='T-N top / segment 1':con[s]['axis_fraction']=(53.25+32)/281.5
 if con['from']['member_id']==con['to']['member_id']:continue
 for s in ['from','to']:
  ref=con[s];m=mm[ref['member_id']];t=ref['axis_fraction'];ref['point']=((1-t)*np.array(m['a'])+t*np.array(m['b'])).tolist()
 con['offset_vector_inches']=(np.array(con['to']['point'])-con['from']['point']).tolist();con['axis_gap_inches']=float(np.linalg.norm(con['offset_vector_inches']));cons.append(con)
# Coalesced uprights can leave several numerical links representing the SAME joint.
# Keep shortest centroid link for a physical-member pair in a localized (<8 in) joint region.
retained=[];redundant=[]
for con in sorted(cons,key=lambda c:c['axis_gap_inches']):
 pair=set(con[s]['member_id'] for s in ['from','to']);center=np.mean([con[s]['point'] for s in ['from','to']],axis=0)
 dup=next((x for x in retained if set(x[s]['member_id'] for s in ['from','to'])==pair and np.linalg.norm(center-np.mean([x[s]['point'] for s in ['from','to']],axis=0))<8),None)
 if dup:redundant.append({'removed':con['id'],'kept':dup['id']})
 else:retained.append(con)
c['connectivity']['intended_connections']=retained;c['members']=[m for m in c['members'] if m['id'] not in remove|set(merge)]
for m in c['members']:m['length_inches']=float(np.linalg.norm(np.array(m['b'])-m['a']))
c['revision_note']='Simplified candidate: duplicate/adjacent truss uprights use shared columns or side-truss uprights; one diagonal per north/east upper bay. Ground and roof-plan X bracing retained. All changes require updated analysis.'
(P/'geometry.json').write_text(json.dumps(c,indent=2));(P/'changes.json').write_text(json.dumps(dict(merged_into=merge,removed=sorted(remove),duplicate_joint_links_removed=redundant,retained_nearby_member='TW vertical6 is a separate balcony-door jamb at y247, six inches from W4 at y253; retained to preserve the opening.',intentional_double_levels='T1 has a staged upper truss and separate lower trolley/floor rail. These are at different heights and retained.'),indent=2));(P/'after-audit.json').write_text(json.dumps(audit(c),indent=2));print('Removed',len(remove),'merged',len(merge),'joint links coalesced',len(redundant));print(audit(c)['parallel_overlaps'])
