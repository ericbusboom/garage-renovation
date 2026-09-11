import json,sys,copy,hashlib,csv
from pathlib import Path
from types import SimpleNamespace
import numpy as np
import optimize as o
P=o.P;a=o.a;q=o.q;c=o.c;mm=o.mm
selected=json.loads((P/'selected.json').read_text());ex=SimpleNamespace(selection=selected)
# Reuse the validated full-network exporter without executing another study driver.
source=(P.parent/'north-wall-coplanar/solve.py').read_text();exec(source[source.index('def export('):source.index("for stage in ['complete','roof_first']:")])
allchecks={};results={}
for stage in ['complete','roof_first']:
 r=a.analyze('final_'+stage,remove=['W2'],selection=selected,catalog=q.CAT,link_factor=10,demand_export=True,lateral_sensitivity=True,study_stage=stage,export_hook=export,export_basic_cases=True)
 assert r['status']=='solved_conditional',r.get('error');r['member_screen']=o.screens(r,selected);(P/('global-'+stage+'.json')).write_text(json.dumps(r,default=float));results[stage]=r
 print(stage,'exported',flush=True)
# Selected sizing result already has completed second-order analysis and service checks.
chosen=json.loads((P/'selected-summary.json').read_text());label=chosen['label'];r=json.loads((P/(label+'-complete.json')).read_text());r['member_screen']=o.screens(r,selected);(P/'global-complete-PDelta.json').write_text(json.dumps(r,default=float));results['PDelta']=r
# Original member sizes under the same audited load model for a direct comparison.
baseline=a.analyze('audited-original',remove=['W2'],selection=o.sel,catalog=q.CAT,link_factor=10,second_order=True,demand_export=True,lateral_sensitivity=True,export_basic_cases=True,export_hook=o.hook)
assert baseline['status']=='solved_conditional',baseline.get('error')
baseline['member_screen']=o.screens(baseline,o.sel);baseline['serviceability']=o.metrics['complete'];(P/'audited-original.json').write_text(json.dumps(baseline,default=float))
# Sensitivity to connection assumptions; neither assumes extra ground supports.
for title,kwargs in [('web-pinned',dict(web_pinned=True)),('base-pinned',dict(base_pinned=True))]:
 rr=a.analyze(title,remove=['W2'],selection=selected,catalog=q.CAT,link_factor=10,second_order=True,demand_export=True,lateral_sensitivity=True,export_basic_cases=True,export_hook=o.hook,**kwargs)
 if rr['status']=='solved_conditional':rr['member_screen']=o.screens(rr,selected);rr['serviceability']=o.metrics['complete'];rr['max_screen_ratio']=max(v['ratio'] for v in rr['member_screen'].values());print(title,rr['max_screen_ratio'],flush=True)
 else:print(title,rr['status'],rr.get('error'),flush=True)
 (P/(title+'.json')).write_text(json.dumps(rr,default=float))
# Independent capacity sensitivities using the same solved demands.
o.brace=1e9;unbraced=o.screens(r,selected);o.brace=72.;storage=o.screens(r,selected,include_storage=True)
(P/'capacity-sensitivities.json').write_text(json.dumps(dict(full_unbraced=unbraced,storage125=storage),default=float))
rows=[]
for mid in selected:
 candidates=[(stage,rr['member_screen'][mid]) for stage,rr in results.items() if mid in rr['member_screen']];stage,check=max(candidates,key=lambda x:x[1]['ratio']);m=mm[mid];s=q.CAT[selected[mid]]
 rows.append(dict(member=mid,truss=m.get('truss') or 'columns/beams',role=m['role'],section=s['aisc_label'],section_key=selected[mid],length_ft=m['length_inches']/12,weight_lb=m['length_inches']/12*s['w'],utilization=check['ratio'],stage=stage,case=check['case'],compression_lb=check['demands']['compression'],tension_lb=check['demands']['tension'],My_lb_in=check['demands']['My'],Mz_lb_in=check['demands']['Mz']))
with open(P/'member-schedule.csv','w') as f:
 w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
(P/'member-schedule.json').write_text(json.dumps(rows,indent=2))
(P/'solver-benchmark.json').write_text(json.dumps(a.benchmark(),indent=2))
print('Final analysis and schedule complete',flush=True)
