"""Greedy deletion study of roof-bay diagonals with current solar connections."""
import json,sys,math
import completion as C
import rafter_bay_revision as B
import owner_revisions as OR
OUT=B.OUT/'brace-reduction'
OUT.mkdir(exist_ok=True)
def build(keep, mesh=12):
 f,s,g=B.build()
 for m in g['new_braces']:
  if m not in keep:OR._drop(f,m)
 for member in ['BR-S-1','BR-S-2']:
  length=f.member_length(member)
  f.unbraced_length_overrides[member]=max(length,f.unbraced_length_overrides.get(member,0))
  for mm,i,j in list(f.segments):
   if mm!=member:continue
   a,b=f.xyz(i),f.xyz(j);count=math.ceil(math.dist(a,b)/mesh)
   for k in range(1,count):C._split(f,member,tuple(a[q]+(b[q]-a[q])*k/count for q in range(3)),f'TRIM.{len(f.nodes)}')
  origin=min(f.xyz(n) for mm,i,j in f.segments if mm==member for n in(i,j))
  f.segments=[(mm,j,i) if mm==member and math.dist(f.xyz(i),origin)>math.dist(f.xyz(j),origin) else (mm,i,j) for mm,i,j in f.segments]
 B.W.D.T.clean(f)
 return f,s,g

def run(keep,tag,mesh=12):
 f,s,g=build(keep,mesh)
 B.W.D.T.OUT=OUT
 r=B.W.D.T.solve(tag,f,s,second_order=True)
 d=json.loads((OUT/(tag+'.json')).read_text())
 d['kept_roof_braces']=sorted(keep)
 (OUT/(tag+'.json')).write_text(json.dumps(d,indent=2))
 return d
if __name__=='__main__':
 d=run([], 'no-roof-bay-braces')
 if d['passes']:
  (OUT/'selected.json').write_text(json.dumps(dict(tag='no-roof-bay-braces',keep=[],reason='Zero added roof-bay braces passes the screen; no further deletions possible.'),indent=2))
 else:
  f,s,g=B.build();keep=list(g['new_braces']);accepted='original-12-braces'
  trials=[];changed=True
  while changed:
   changed=False
   for member in list(keep):
    trial=[m for m in keep if m!=member]
    tag='trial-'+str(len(trials)+1)
    result=run(trial,tag)
    trials.append(dict(tag=tag,removed=member,passes=result['passes']))
    if result['passes']:keep=trial;accepted=tag;changed=True
  (OUT/'selected.json').write_text(json.dumps(dict(tag=accepted,keep=keep,trials=trials,reason='No single remaining brace can be removed while passing the preliminary screen; greedy subset, not proof of global optimum.'),indent=2))
