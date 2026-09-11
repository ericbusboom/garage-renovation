import json
import run_analysis as a
from iterate_design import CAT,MEM,screen,P
seed=json.loads((P/'iteration2-step3.json').read_text())['selection']
practical=dict(seed)
for mid,m in MEM.items():
 if m['section_family']=='chord' and CAT[practical[mid]]['d']<3:practical[mid]='HSS3x3x0.188'
 if m.get('truss')=='TE' and m['section_family']=='chord':practical[mid]='HSS6x6x0.25'
 if m.get('truss')=='TE' and m['section_family']=='web':practical[mid]='HSS3x3x0.25'
 if m['axis_source'].get('ground_post') and mid not in ['N2','N1 / U-W']:practical[mid]='HSS4x4x0.25'
practical['T-N']='HSS3x3x0.188'
for name,sel,kwargs in [('practical_all',practical,{}),('practical_no_W2',practical,{'remove':['W2']}),('practical_released_webs',practical,{'web_pinned':True}),('practical_PDelta',practical,{'second_order':True})]:
 r=a.analyze(name,selection=sel,catalog=CAT,demand_export=True,**kwargs)
 if r['status']=='solved_conditional':
  r['selection']=sel;r['member_checks']=screen(r,sel);r['max_screen_ratio']=max(v['ratio'] for v in r['member_checks'].values())
 (P/(name+'.json')).write_text(json.dumps(r,indent=2,default=lambda v:float(v)))
 print(name,r['status'],r.get('steel_weight_lb'),r.get('max_screen_ratio'),r.get('results',{}).get('service_patches',{}).get('max_floor_abs_DY_in'),flush=True)
