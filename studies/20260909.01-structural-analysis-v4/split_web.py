from pathlib import Path
import sys,json,itertools
P=Path(__file__).resolve().parent;sys.path.insert(0,str(P.parent/'structural-analysis-v3'));import engineer as a
r=json.loads((P.parent/'structural-analysis-v3/results.json').read_text());base=r['selection'].copy();base.pop('T1:web');base['T1:vertical']='HSS2x2x0.125';base['T1:diagonal']='HSS2.5x2.5x0.125'
for e in a.es:
 if e['family']=='T1:web':e['family']='T1:vertical' if abs(a.b.N[e['ij'][0],0]-a.b.N[e['ij'][1],0])<.01 else 'T1:diagonal'
rows=[]
for lo,up in itertools.product(['W6X16','W6X20','W6X25','W8X24'],['HSS4x4x0.188','W6X20','W8X24']):
 sel=base.copy();sel.update({'T1:lower':lo,'T1:upper':up,'O3:beam':'HSS3x3x0.188'});o=a.solve(sel)
 rows.append(dict(lower=lo,upper=up,vertical=sel['T1:vertical'],diagonal=sel['T1:diagonal'],passes=a.acceptable(o),weight=o['steel_with_connections_lb'],T1_weight=sum(v for k,v in o['weights'].items() if k.startswith('T1:')),ratio=o['max_ratio'],movement=o['max_vertical_in'],selection=sel,T1={f:d for f,d in o['families'].items() if f.startswith('T1:')}))
rows.sort(key=lambda x:x['weight']);(P/'split-web.json').write_text(json.dumps(rows,indent=2))
for x in rows:print(x['lower'],x['upper'],x['passes'],round(x['weight']),round(x['ratio'],3),flush=True)
