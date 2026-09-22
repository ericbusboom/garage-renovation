import json
import run_analysis as a
from iterate_design import P,CAT,MEM,screen
c=json.loads((P/'candidate7-candidate-geometry.json').read_text());a.CAD=c;MEM.update({m['id']:m for m in c['members']});sel=json.loads((P/'candidate7-candidate-selection.json').read_text())
r=a.analyze('candidate7_link_sensitivity',remove=['W2'],selection=sel,catalog=CAT,demand_export=True,lateral_sensitivity=True,link_factor=1)
if r['status']=='solved_conditional':r['member_checks']=screen(r,sel);r['max_screen_ratio']=max(v['ratio'] for v in r['member_checks'].values())
(P/'candidate7_link_sensitivity.json').write_text(json.dumps(r,indent=2,default=lambda v:float(v)));print(r['status'],r.get('max_screen_ratio'),r.get('error'))
