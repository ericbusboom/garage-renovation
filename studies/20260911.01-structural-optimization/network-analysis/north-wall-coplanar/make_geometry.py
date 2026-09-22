import json,copy
from pathlib import Path
import numpy as np
P=Path(__file__).resolve().parent;c=json.loads((P.parent/'north-brace-alignment/geometry.json').read_text());old=copy.deepcopy(c);mm={m['id']:m for m in c['members']};om={m['id']:m for m in old['members']}
north={k for k,m in mm.items() if m.get('truss')=='TN' or k.startswith('BR-N-') or k=='N1 / U-W'}
for k in north:
 for end in ['a','b']:mm[k][end][1]=253.
mm['T-N upper east jamb']['a'][2]=115.
mm['T-N diagonal 8']['a']=[155.25,253.,224.25]
mm['T-N diagonal 9']['b']=[249.5,253.,115.]
mm['T-N vertical 5']['a']=[249.5,253.,115.];mm['T-N vertical 5']['b']=[249.5,253.,224.25]
def point(r):
 m=mm[r['member_id']];t=r['axis_fraction'];return (1-t)*np.array(m['a'])+t*np.array(m['b'])
def project(r,p):
 m=mm[r['member_id']];a=np.array(m['a']);v=np.array(m['b'])-a;r['axis_fraction']=float(np.clip(np.dot(p-a,v)/np.dot(v,v),0,1))
cons=[]
for co in c['connectivity']['intended_connections']:
 pair={co[s]['member_id'] for s in ['from','to']}
 # The east lower chords attach at separate heights on the same N2 column.
 # Its real column segment carries that transfer; do not duplicate it with a stiff offset element.
 if pair=={'T-N','T-E'}:continue
 for side in ['from','to']:
  r=co[side];k=r['member_id'];t=r['axis_fraction']
  if k=='T-N upper east jamb' and 1e-8<t<1-1e-8:
   m=om[k];pt=(1-t)*np.array(m['a'])+t*np.array(m['b']);pt[1]=253;project(r,pt)
 # Connections from the north wall to TE/TW move to their actual rear endpoints.
 for side,other in [('from','to'),('to','from')]:
  r=co[side];o=co[other]
  if r['member_id'] in north and mm[o['member_id']].get('truss') in ['TE','TW']:project(o,point(r))
 # Reattach edited web/jamb endpoints at their exact chord coordinates.
 for side,other in [('from','to'),('to','from')]:
  r=co[side];o=co[other];m=mm[r['member_id']]
  if m.get('truss')=='TN' and m['role'] in ['diagonal','vertical','upper_jamb'] and min(abs(r['axis_fraction']),abs(r['axis_fraction']-1))<1e-8:
   if mm[o['member_id']]['role'] in ['chord','top_chord','header']:project(o,point(r))
 for side in ['from','to']:co[side]['point']=point(co[side]).tolist()
 v=point(co['to'])-point(co['from']);co['axis_gap_inches']=float(np.linalg.norm(v));co['offset_vector_inches']=v.tolist();cons.append(co)
c['connectivity']['intended_connections']=cons
for m in c['members']:m['length_inches']=float(np.linalg.norm(np.array(m['b'])-m['a']))
checks=[]
for co in cons:
 pair={co[s]['member_id'] for s in ['from','to']}
 if any(k in north for k in pair) and all(k in north|{'W4','N2'} for k in pair):
  assert co['axis_gap_inches']<1e-7,(co['id'],co['axis_gap_inches']);checks.append(co['id'])
for k in north|{'W4','N2'}:assert mm[k]['a'][1]==mm[k]['b'][1]==253.
for m in c['members']:
 if m.get('truss') in ['TE','TW','TS']:assert m==om[m['id']]
c['revision_note']='Whole north wall at y253: TN chords/webs/header/jambs, north braces and W4/N1/N2 coplanar. N1 shifted0.5in north. TN moved4in north. All internal north joints coincident. TE/TW/TS physical members unchanged; rear connections now at their ends. East5in bottom-chord elevation difference transferred through N2, not a duplicate offset.'
(P/'geometry.json').write_text(json.dumps(c,indent=2));(P/'geometry-checks.json').write_text(json.dumps(dict(common_north_plane_in=253,zero_gap_joint_count=len(checks),zero_gap_joints=checks,N1_moved_north_in=.5,TN_moved_north_in=4,TE_TW_TS_geometry_unchanged=True),indent=2));print('All',len(checks),'north-wall joints have zero axis gap')
