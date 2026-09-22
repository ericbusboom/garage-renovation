import json
import optimize as o
P=o.P;s=json.loads((P/'selected.json').read_text())
r=o.a.analyze('base-pinned-no-basic',remove=['W2'],selection=s,catalog=o.q.CAT,link_factor=10,second_order=True,base_pinned=True,demand_export=True,lateral_sensitivity=True,export_basic_cases=False)
if r['status']=='solved_conditional':r['member_screen']=o.screens(r,s);r['max_screen_ratio']=max(v['ratio'] for v in r['member_screen'].values());print('base-pinned solved',r['max_screen_ratio'],r['results']['service_patches']['max_floor_abs_DY_in'],flush=True)
else:print(r.get('error'),flush=True)
(P/'base-pinned-confirmation.json').write_text(json.dumps(r,default=float))
(P/'solver-benchmark.json').write_text(json.dumps(o.a.benchmark(),indent=2))
