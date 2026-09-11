"""Refresh whole-frame actions after adding explicit missing joint connections."""
import sys,json,copy
from pathlib import Path
import numpy as np
P=Path(__file__).resolve().parent;sys.path.insert(0,str(P.parent))
import export_truss_submodels as ex
from iterate_design import CAT
c=copy.deepcopy(ex.a.CAD);mm={m['id']:m for m in c['members']}
def add(cid,one,two,t1,t2):
 sides={}
 for label,mid,t in [('from',one,t1),('to',two,t2)]:
  m=mm[mid];p=(1-t)*np.array(m['a'])+t*np.array(m['b']);sides[label]=dict(member_id=mid,axis_fraction=t,point=p.tolist())
 c['connectivity']['intended_connections'].append(dict(id=cid,**sides,basis='Explicit correction of missing joint found in native network audit; proposed connection.',axis_gap_inches=float(np.linalg.norm(np.array(sides['from']['point'])-sides['to']['point']))))
add('FIX_TE_KNEE','T-E top / segment 1','T-E top / segment 2',1.,0.)
add('FIX_TW_KNEE','T-W top / segment 1','T-W top / segment 2',1.,0.)
add('FIX_TN_JAMB','T-N upper east jamb','T-N',0.,(155.25+32)/281.5)
(P/'global-connected-geometry.json').write_text(json.dumps(c,indent=2));ex.a.CAD=c
ex.OUT=P/'global-connected-source';ex.OUT.mkdir(exist_ok=True)
for stage in ['complete','roof_first']:
 r=ex.a.analyze('global_connected_'+stage,remove=['W2'],selection=ex.selection,catalog=CAT,link_factor=10,demand_export=True,lateral_sensitivity=True,study_stage=stage,export_hook=ex.export,export_basic_cases=True)
 (ex.OUT/('global-'+stage+'.json')).write_text(json.dumps(r,indent=2,default=lambda v:v.item()))
 assert r['status']=='solved_conditional',r.get('traceback',r)
print('Whole-frame corrected connection export complete')
