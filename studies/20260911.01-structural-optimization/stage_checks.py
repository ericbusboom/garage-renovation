import json
import run_analysis as a
from iterate_design import CAT,P,screen,choose
sel=json.loads((P/'practical_all.json').read_text())['selection']
for name,kw in [('practical_roof_first',{'study_stage':'roof_first','lateral_sensitivity':True}),('practical_lateral',{'lateral_sensitivity':True})]:
 r=a.analyze(name,selection=sel,catalog=CAT,demand_export=True,**kw)
 if r['status']=='solved_conditional':r['member_checks']=screen(r,sel);r['max_screen_ratio']=max(v['ratio'] for v in r['member_checks'].values())
 (P/(name+'.json')).write_text(json.dumps(r,indent=2,default=lambda v:float(v)))
 print(name,r['status'],r.get('max_screen_ratio'),{k:round(v['max_horizontal_displacement_in'],3) for k,v in r.get('results',{}).items() if k.startswith('lateral')},r.get('error'),flush=True)
