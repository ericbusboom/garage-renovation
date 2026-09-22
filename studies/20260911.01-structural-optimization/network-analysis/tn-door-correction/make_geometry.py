import json,copy
from pathlib import Path
import numpy as np
P=Path(__file__).resolve().parent;c=json.loads((P.parent/'clean-layout/geometry.json').read_text());original=copy.deepcopy(c);mm={m['id']:m for m in c['members']}
header='T-N loading header';top='T-N top / segment 1';jamb='T-N upper east jamb';left='N1 / U-W';z0=207.;z1=224.25;xs=[53.25,78.75,104.25,129.75,155.25]
mini={header}|{'T-N vertical '+str(i) for i in [11,12,13]}|{'T-N diagonal '+str(i) for i in [15,16,17,18]}
mm[header]['a']=[xs[0],249.,z0];mm[header]['b']=[xs[-1],249.,z0];mm[jamb]['b']=[155.25,249.,z1]
for i,x in zip([11,12,13],xs[1:-1]):mm['T-N vertical '+str(i)]['a']=[x,249.,z0];mm['T-N vertical '+str(i)]['b']=[x,249.,z1]
for i in range(4):
 m=mm['T-N diagonal '+str(15+i)];m['a']=[xs[i],249.,z0 if i%2==0 else z1];m['b']=[xs[i+1],249.,z1 if i%2==0 else z0]
# Rebuild the mini-truss joints explicitly; no inherited clipped-end offsets or near-end fractions.
cons=[co for co in c['connectivity']['intended_connections'] if not any(co[s]['member_id'] in mini for s in ['from','to']) and not ({co[s]['member_id'] for s in ['from','to']}=={jamb,top})]
def ref(mid,point):
 m=mm[mid];a=np.array(m['a']);v=np.array(m['b'])-a;t=float(np.dot(np.array(point)-a,v)/np.dot(v,v));assert -1e-8<=t<=1.00000001
 return dict(member_id=mid,axis_fraction=t,point=(a+t*v).tolist())
def link(a,pa,b,pb):
 ra=ref(a,pa);rb=ref(b,pb);v=np.array(rb['point'])-ra['point'];cons.append(dict(id='TN-door-clean-'+str(len(cons)),**{'from':ra,'to':rb},axis_gap_inches=float(np.linalg.norm(v)),offset_vector_inches=v.tolist(),physical_solid_distance_inches=None,joint_behavior='Shared node when coincident; explicit centroid offset at north post only.'))
link(header,mm[header]['a'],left,[53.25,252.5,z0]);link(header,mm[header]['b'],jamb,[155.25,249,z0]);link(jamb,mm[jamb]['b'],top,mm[jamb]['b'])
# Existing left post reaches the top chord through its explicitly modeled 3.5-inch out-of-plane connection.
link(top,[53.25,249,z1],left,[53.25,252.5,z1])
for mid in sorted(mini-{header}):
 for end in ['a','b']:
  p=mm[mid][end];target=header if abs(p[2]-z0)<1e-6 else top;link(mid,p,target,p)
# Preserve the same attachment heights for any other connection to the lengthened jamb.
oldmm={m['id']:m for m in original['members']}
for co in cons:
 if not co['id'].startswith('TN-door-clean-'):
  for s in ['from','to']:
   r=co[s]
   if r['member_id']==jamb:
    old=oldmm[jamb];pt=np.array(old['a'])+r['axis_fraction']*(np.array(old['b'])-old['a']);co[s]=ref(jamb,pt)
 for s in ['from','to']:
  r=co[s];m=mm[r['member_id']];t=r['axis_fraction'];r['point']=((1-t)*np.array(m['a'])+t*np.array(m['b'])).tolist()
 v=np.array(co['to']['point'])-co['from']['point'];co['axis_gap_inches']=float(np.linalg.norm(v));co['offset_vector_inches']=v.tolist()
# Deduplicate exactly repeated joint definitions, without coalescing distinct connections.
unique={}
for co in cons:
 key=tuple(sorted((co[s]['member_id'],round(co[s]['axis_fraction'],8)) for s in ['from','to']));unique.setdefault(key,co)
c['connectivity']['intended_connections']=list(unique.values())
for m in c['members']:m['length_inches']=float(np.linalg.norm(np.array(m['b'])-m['a']))
for m in c['members']:
 if m.get('truss') in ['TE','TW','TS']:assert m==oldmm[m['id']],m['id']
for mid in sorted(mini-{header}):
 for end in ['a','b']:
  p=mm[mid][end];assert p[0] in xs and p[2] in [z0,z1]
assert mm[header]['b']==[155.25,249.,207.]
c['revision_note']='TN door mini-truss rebuilt on four equal25.5in panels, continuous header axis53.25..155.25 at207in, common web/chord nodes, east jamb extended to224.25in. TE/TW/TS unchanged. Left post retains explicit3.5in out-of-plane centroid connection.'
(P/'geometry.json').write_text(json.dumps(c,indent=2));(P/'geometry-checks.json').write_text(json.dumps(dict(panel_width_in=25.5,total_axis_span_in=102,axis_depth_in=17.25,bottom_axis_height_in=z0,top_axis_height_in=z1,web_endpoints_on_chords=True,TE_TW_TS_unchanged=True,left_post_out_of_plane_offset_in=3.5),indent=2));print('Geometry checks passed')
