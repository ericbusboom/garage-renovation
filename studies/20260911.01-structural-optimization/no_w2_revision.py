import json
import run_analysis as a
from iterate_design import CAT,P,screen,allowed,MEM
r=json.loads((P/'practical_no_W2.json').read_text());sel=r['selection'].copy()
ids=[i for i,m in MEM.items() if m.get('truss')=='TW' and m['role']=='diagonal']
for s in allowed(ids[0]):
 if s['d']>3:continue
 test=sel.copy()
 for i in ids:test[i]=s['name']
 checks=screen({'member_demands':{i:r['member_demands'][i] for i in ids}},test)
 if max(v['ratio'] for v in checks.values())<=.80:sel=test;break
r=a.analyze('practical_no_W2_reinforced',remove=['W2'],selection=sel,catalog=CAT,demand_export=True,second_order=True)
if r['status']=='solved_conditional':r['selection']=sel;r['member_checks']=screen(r,sel);r['max_screen_ratio']=max(v['ratio'] for v in r['member_checks'].values())
(P/'practical_no_W2_reinforced.json').write_text(json.dumps(r,indent=2,default=lambda v:float(v)))
print(r['status'],r.get('steel_weight_lb'),r.get('max_screen_ratio'),sel[ids[0]],flush=True)
