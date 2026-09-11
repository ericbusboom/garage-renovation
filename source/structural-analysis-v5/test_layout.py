"""Position study with fixed support locations, candidate rail/companion upsizing."""
from pathlib import Path
import os,json
import engineer as a
P=Path(__file__).parent;name=os.environ.get('LAYOUT','test');a.P=P
r=json.loads((P.parent/'structural-analysis-v4/selected-options.json').read_text())['B']
sel=r['selection'].copy();sel.pop('B3:beam');sel.pop('B2:beam');sel.pop('T1:vertical');sel.pop('T1:diagonal')
# Retain the previous split T1 webs as distinct families.
for e in a.es:
 if e['family']=='T1:web':e['family']='T1:vertical' if abs(a.b.N[e['ij'][0],0]-a.b.N[e['ij'][1],0])<.01 else 'T1:diagonal'
sel['T1:vertical']='HSS2x2x0.125';sel['T1:diagonal']='HSS2.5x2.5x0.125'
for n in a.b.BEAM_NAMES:sel[n+':beam']='W8X31'
r=a.solve(sel);history=[]
for step in range(6):
 if a.acceptable(r):break
 changed=0
 for f,d in r['families'].items():
  if d['ratio']<=.90:continue
  old=a.cat[sel[f]];opts=[s for s in a.allowed(f) if s['w']>old['w']+.01 and s['Iy']>=old['Iy']]
  if opts:sel[f]=opts[0]['name'];changed+=1
 r=a.solve(sel)
 if not changed:break
# Search rail sizes jointly; then test small reductions in companion families.
import itertools
families=[n+':beam' for n in a.b.BEAM_NAMES]
best=r;bestsel=sel.copy()
for ss in itertools.product(*[a.allowed(f) for f in families]):
 trial=sel.copy();trial.update({f:s['name'] for f,s in zip(families,ss)});rr=a.solve(trial)
 if a.acceptable(rr) and (not a.acceptable(best) or rr['steel_with_connections_lb']<best['steel_with_connections_lb']):best=rr;bestsel=trial
sel=bestsel;r=best
# Keep truss families fixed across the position sweep except required upsizing;
# otherwise the objective changes into a much wider topology/member search.
r.update(layout=name,beam_y=a.b.BEAM_YS,beam_names=a.b.BEAM_NAMES,supports=a.b.LOFT_SUPPORTS,feasible=a.acceptable(r),max_joist_span_in=max(y-x for x,y in zip(a.b.LOFT_SUPPORTS[:-1],a.b.LOFT_SUPPORTS[1:])),notes='No B3; north floor load enters T-N lower chord. Fixed columns and O3 at y=185. T1 W/W split-web option. Other members held except required upsizing.')
(P/'results').mkdir(exist_ok=True);(P/'results'/f'{name}.json').write_text(json.dumps(r,indent=2));print(name,r['feasible'],round(r['steel_with_connections_lb']),r['max_ratio'],r['max_vertical_in'],{f:sel[f] for f in families},flush=True)
