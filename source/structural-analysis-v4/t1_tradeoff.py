"""Joint T1 chord/web tradeoff, retaining the v3 connected frame and load cases."""
from pathlib import Path
import sys,json,itertools
P=Path(__file__).resolve().parent
sys.path.insert(0,str(P.parent/'structural-analysis-v3'))
import engineer as a
r=json.loads((P.parent/'structural-analysis-v3/results.json').read_text());base=r['selection'];rows=[]
lowers=[k for k in ['W6X15','W6X16','W6X20','W6X25','W8X24'] if k in a.cat]
uppers=[k for k in ['W6X20','W6X25','W8X24','W8X31','HSS4x4x0.188'] if k in a.cat]
webs=['HSS2x2x0.125','HSS2x2x0.188','HSS2.5x2.5x0.125']
for i,(lo,up,web) in enumerate(itertools.product(lowers,uppers,webs)):
 sel=base.copy();sel.update({'T1:lower':lo,'T1:upper':up,'T1:web':web});o=a.solve(sel)
 rows.append(dict(lower=lo,upper=up,web=web,passes=a.acceptable(o),weight=o['steel_with_connections_lb'],T1_weight=sum(v for k,v in o['weights'].items() if k.startswith('T1:')),ratio=o['max_ratio'],movement=o['max_vertical_in'],governing=max(o['families'].values(),key=lambda x:x['ratio']),T1={k:v for k,v in o['families'].items() if k.startswith('T1:')}))
 if i%15==0:print(i,lo,up,web,o['max_ratio'],o['max_vertical_in'],flush=True)
rows.sort(key=lambda x:x['weight']);(P/'tradeoffs.json').write_text(json.dumps(dict(baseline=r,rows=rows),indent=2))
for row in [x for x in rows if x['passes']][:5]:print('PASS', {k:v for k,v in row.items() if k not in ['T1','governing']},flush=True)
print('DONE',len(rows),sum(x['passes'] for x in rows),flush=True)
