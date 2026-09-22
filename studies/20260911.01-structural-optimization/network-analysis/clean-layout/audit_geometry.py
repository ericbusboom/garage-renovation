import json,itertools
from pathlib import Path
import numpy as np
P=Path(__file__).resolve().parent

def audit(c):
 ms=[m for m in c['members'] if m['id']!='W2'];parallel=[];cross=[]
 for a,b in itertools.combinations(ms,2):
  pa,qa,pb,qb=[np.array(m[k],float) for m,k in [(a,'a'),(a,'b'),(b,'a'),(b,'b')]];u=qa-pa;v=qb-pb;lu=np.linalg.norm(u);lv=np.linalg.norm(v);uu=u/lu;vv=v/lv
  if abs(np.dot(uu,vv))>.99999:
   gap=np.linalg.norm(np.cross(pb-pa,uu));ts=sorted([np.dot(pb-pa,uu),np.dot(qb-pa,uu)]);overlap=min(lu,ts[1])-max(0,ts[0])
   if gap<6.01 and overlap>10:parallel.append(dict(members=[a['id'],b['id']],gap_inches=float(gap),overlap_inches=float(overlap),type='coincident' if gap<.01 else 'adjacent'))
  else:
   ts=np.linalg.lstsq(np.column_stack([u,-v]),pb-pa,rcond=None)[0];dist=np.linalg.norm(pa+ts[0]*u-pb-ts[1]*v)
   if dist<.01 and all(.001<t<.999 for t in ts):cross.append(dict(members=[a['id'],b['id']],point=(pa+ts[0]*u).tolist(),note='Geometric crossing; does not establish a fabricated joint.'))
 return dict(parallel_overlaps=parallel,interior_crossings=cross,physical_members=len(ms))
if __name__=='__main__':
 c=json.loads((P.parent/'grounded-walls/geometry.json').read_text());r=audit(c);(P/'before-audit.json').write_text(json.dumps(r,indent=2));print(json.dumps(r,indent=2))
