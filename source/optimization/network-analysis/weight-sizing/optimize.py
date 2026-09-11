"""Fixed geometry, discrete stock sizing. Conditional local search, not a global optimum proof."""
import json,sys,copy,math,time
from pathlib import Path
import numpy as np
P=Path(__file__).resolve().parent;ROOT=P.parents[1];sys.path.insert(0,str(ROOT))
import study_solver as a
import iterate_design as q
c=json.loads((P.parent/'north-wall-coplanar/geometry.json').read_text());a.CAD=c;a.BASIS=json.loads((P/'load-basis.json').read_text());q.CAT=json.loads((P/'catalog.json').read_text());q.MEM={m['id']:m for m in c['members']};mm=q.MEM
sel=json.loads((ROOT/'candidate9-candidate-selection.json').read_text());sel={k:v.replace('x0.188','x0.1875').replace('x0.313','x0.3125') for k,v in sel.items() if k in mm and k!='W2'};assert all(v in q.CAT for v in sel.values()),set(sel.values())-set(q.CAT)
start_selection=copy.deepcopy(sel);history=[];snapshots={};metrics={}
# Restrained chord lengths are explicit design requirements, not inferred from mesh nodes.
brace=72.
def screens(r,s,include_storage=False):
 rows=q.screen(r,s,brace=brace,include_storage=include_storage)
 for mid,row in rows.items():
  sec=q.CAT[s[mid]]
  if sec['type']=='HSS':
   tc=.9*.6*50000*sec['C'];rat=0.;case=None
   for case,d in r.get('member_demands',{}).get(mid,{}).items():
    if case=='storage125_strength_sensitivity' and not include_storage:continue
    cap=q.capacity(sec,mm[mid],brace);normal=max(d['compression']/cap['Pc'],d['tension']/cap['Pt'])+d['My']/cap['My']+d['Mz']/cap['Mz'];shear=math.hypot(d['Vy'],d['Vz'])/cap['V'];tor=d['T']/tc
    # Conservative linear normal+bending+shear+torsion screening, not full H3 design.
    demand=max(normal+shear+tor,row['ratio'])
    if demand>row['ratio']:row.update(ratio=demand,case=case,demands=d)
   row['torsion_capacity_screen_lb_in']=tc
 return rows

def hook(M,members,pieces,links,combos,sections,coords,study_stage):
 floorids={'B2 future floor beam','T1 future floor beam','T-N','T-E','T-W / B-WO'};fn={n.name for key,mid,lo,hi in pieces if mid in floorids for n in [M.members[key].i_node,M.members[key].j_node]};rn={n.name for key,mid,lo,hi in pieces if mm[mid]['role']=='top_chord' for n in [M.members[key].i_node,M.members[key].j_node]};limits=[]
 if study_stage=='complete':
  for case in ['live_only','patches_live_only']:
   val=max(abs(M.nodes[n].DY[case]) for n in fn);limits.append(dict(check='floor live movement',case=case,value=val,limit=256.25/360,ratio=val/(256.25/360)))
  for case in ['service_patches','HB0.25','HB0.5','HB0.75','HT0.25','HT0.5','HT0.75']:
   val=max(abs(M.nodes[n].DY[case]) for n in fn);limits.append(dict(check='floor total movement',case=case,value=val,limit=256.25/240,ratio=val/(256.25/240)))
  for case in ['basic_HB0.25','basic_HB0.5','basic_HB0.75','basic_HT0.25','basic_HT0.5','basic_HT0.75']:
   val=max(abs(M.nodes[n].DY[case]) for n in fn);limits.append(dict(check='incremental hoist movement study target',case=case,value=val,limit=256.25/450,ratio=val/(256.25/450)))
 case='service_patches' if study_stage=='complete' else 'roof_first_service';val=max(abs(M.nodes[n].DY[case]) for n in rn);limits.append(dict(check='roof total movement study target',case=case,value=val,limit=253/240,ratio=val/(253/240)))
 for case in ['lateral_HX','lateral_HZ']:
  val=max(math.hypot(M.nodes[n].DX[case],M.nodes[n].DZ[case]) for n in rn);limits.append(dict(check='diagnostic roof drift H240',case=case,value=val,limit=231.5/240,ratio=val/(231.5/240)))
 metrics[study_stage]=limits

def run(s,label,second=True):
 out={};allrows={};checks=[]
 for stage in ['complete','roof_first']:
  r=a.analyze(label+'_'+stage,remove=['W2'],selection=s,catalog=q.CAT,link_factor=10,second_order=second and stage=='complete',demand_export=True,lateral_sensitivity=True,study_stage=stage,export_hook=hook,export_basic_cases=True)
  if r['status']!='solved_conditional':(P/(label+'-failure.json')).write_text(json.dumps(r,indent=2,default=float));return None
  rows=screens(r,s);r['member_screen']=rows;r['serviceability']=metrics[stage];checks+=metrics[stage]
  for mid,row in rows.items():
   if row['ratio']>allrows.get(mid,{}).get('ratio',-1):allrows[mid]={**row,'stage':stage}
  out[stage]=r;(P/(label+'-'+stage+'.json')).write_text(json.dumps(r,default=float))
 worst=max(allrows,key=lambda m:allrows[m]['ratio']);ratio=allrows[worst]['ratio'];d=max(checks,key=lambda x:x['ratio']);weight=out['complete']['steel_weight_lb'];feasible=bool(ratio<=1 and d['ratio']<=1)
 item=dict(label=label,steel_lb=weight,strength_ratio=ratio,governing_member=worst,service_ratio=d['ratio'],governing_service=d,feasible=feasible);history.append(item);(P/'history.json').write_text(json.dumps(history,indent=2));(P/(label+'-selection.json')).write_text(json.dumps(s,indent=2));print(item,flush=True)
 return dict(results=out,rows=allrows,checks=checks,summary=item,selection=copy.deepcopy(s))

def options(mid):
 m=mm[mid];f=m['section_family'];vals=[v for v in q.CAT.values() if v['type']==('W' if f=='Wbeam' else 'HSS') and (v['type']=='W' or v['bt']<=1.12*math.sqrt(29e6/50000))]
 if f=='column':vals=[v for v in vals if v['d']==(6 if mid=='N1 / U-W' else 4)]
 elif f=='Wbeam':vals=[v for v in vals if v['d']<=8.001 and v['bf']>=3.]
 else:vals=[v for v in vals if v['bt']<=1.12*math.sqrt(29e6/50000)]
 return sorted(vals,key=lambda v:(v['w'],v['d']))

def proposed(state):
 new={}
 for mid in sel:
  demands={}
  for stage,r in state['results'].items():
   for case,d in r['member_demands'].get(mid,{}).items():demands[stage+'_'+case]=d
  chosen=None
  for sec in options(mid):
   # Each phase separately, so storage sensitivity remains excluded consistently.
   ratios=[]
   for stage,r in state['results'].items():
    rows=screens({'member_demands':{mid:r['member_demands'][mid]}},{mid:sec['name']}) if mid in r['member_demands'] else {}
    ratios += [v['ratio'] for v in rows.values()]
   if max(ratios,default=0)<=.95:chosen=sec['name'];break
  new[mid]=chosen or options(mid)[-1]['name']
 # Prevent repeatedly proposing an obviously too-flexible B2; global reanalysis still decides acceptance.
 mid='B2 future floor beam';oldsec=q.CAT[state['selection'][mid]]
 delta=state['results']['complete']['relative_floor_deflection']['HB0.5'][mid]
 minimum_I=oldsec['Iz']*delta/(.9*256.25/240)
 if q.CAT[new[mid]]['Iz']<minimum_I:
  eligible=[v for v in options(mid) if v['Iz']>=minimum_I and v['w']>=q.CAT[new[mid]]['w']]
  if eligible:new[mid]=eligible[0]['name']
 return new

if __name__=='__main__':
 sel=json.loads((P/'resume-selection.json').read_text()) if (P/'resume-selection.json').exists() else sel
 state=run(sel,'purlin-start');assert state
 best=state if state['summary']['feasible'] else None
 for i in range(1,5):
  new=proposed(state)
  # Do not let an already observed global serviceability violation drive further softening.
  if state['summary']['service_ratio']>.98:
   preserve={'B2 future floor beam','T1 future floor beam','T-E','T-W / B-WO','T-N'}|{k for k,m in mm.items() if m['role']=='top_chord'}
   for mid in preserve&set(new):
    oldsec=q.CAT[state['selection'][mid]]
    if state['summary']['service_ratio']>1:
     larger=[v for v in options(mid) if v['Iz']>oldsec['Iz']*1.08 and v['w']>oldsec['w']]
     if larger:new[mid]=larger[0]['name']
    elif q.CAT[new[mid]]['Iz']<oldsec['Iz']:new[mid]=oldsec['name']
  if new==state['selection']:print('Demand sizing converged',flush=True);break
  trial=run(new,'purlin'+str(i))
  if trial is None:break
  state=trial
  if state['summary']['feasible'] and (best is None or state['summary']['steel_lb']<best['summary']['steel_lb']):best=state
  if len(history)>3 and history[-1]['steel_lb']==history[-3]['steel_lb']:break
 assert best is not None,'No feasible candidate under study constraints'
 (P/'selected.json').write_text(json.dumps(best['selection'],indent=2));(P/'selected-summary.json').write_text(json.dumps(best['summary'],indent=2));print('SELECTED',best['summary'],flush=True)
