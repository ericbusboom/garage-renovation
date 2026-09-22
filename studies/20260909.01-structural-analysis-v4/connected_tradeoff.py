from pathlib import Path
import sys,json
P=Path(__file__).resolve().parent;sys.path.insert(0,str(P.parent/'structural-analysis-v3'))
import engineer as a
r=json.loads((P/'tradeoffs.json').read_text());base=r['baseline']['selection'];rows=[]
# All 75 options, permitting companion-member upsizing while holding requested T1 choices.
for i,x in enumerate(r['rows']):
 sel=base.copy();sel.update({'T1:lower':x['lower'],'T1:upper':x['upper'],'T1:web':x['web']})
 for step in range(4):
  o=a.solve(sel)
  if a.acceptable(o):break
  changes=0
  for f,d in o['families'].items():
   if f.startswith('T1:') or d['ratio']<=.90:continue
   old=a.cat[sel[f]];qs=[s for s in a.allowed(f) if s['w']>old['w']+.01 and s['Iy']>=old['Iy']]
   if qs:sel[f]=qs[0]['name'];changes+=1
  if not changes:break
 o=a.solve(sel)
 rows.append(dict(lower=x['lower'],upper=x['upper'],web=x['web'],passes=a.acceptable(o),weight=o['steel_with_connections_lb'],T1_weight=sum(v for k,v in o['weights'].items() if k.startswith('T1:')),ratio=o['max_ratio'],movement=o['max_vertical_in'],changes={f:n for f,n in sel.items() if n!=base[f]},T1={f:d for f,d in o['families'].items() if f.startswith('T1:')},governing=max(o['families'].values(),key=lambda d:d['ratio'])))
 if i%15==0:print(i,'passes',sum(x['passes'] for x in rows),flush=True)
rows.sort(key=lambda x:x['weight']);(P/'connected-tradeoffs.json').write_text(json.dumps(rows,indent=2))
for x in [x for x in rows if x['passes']][:6]:print({k:v for k,v in x.items() if k not in ['T1','governing']},flush=True)
print('DONE',sum(x['passes'] for x in rows),flush=True)
