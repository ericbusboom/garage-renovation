"""B2 alternatives after permitting deep perimeter framing. Preliminary gravity only."""
from pathlib import Path
import json
from analyze import beam,crossloads,E
p=Path(__file__).parent
sections=[dict(name='W8x24',d=7.93,I=82.7,S=20.9,w=24),dict(name='W8x31',d=8.,I=110,S=27.5,w=31)]
for b,t in [(12,.5),(12,.625),(14,.625)]:
 d=8;tw=.375;h=d-2*t;I=2*(b*t**3/12+b*t*((d-t)/2)**2)+tw*h**3/12
 sections.append(dict(name=f'Fabricated 8 deep, {b} wide, {t} flanges, 0.375 web',d=d,I=I,S=I/4,w=(2*b*t+tw*h)*490/144))
rows=[]
for case in ['storage_bands','storage125']:
 for roof in [False,True]:
  for c in sections:
   D=crossloads(2,'D',case)
   if not roof:
    from analyze import TR
    D=D+[(0,249.5,-15*TR[2]/144)]
   loads={'D':D+[(0,249.5,c['w']/12)],'L':crossloads(2,'L',case),'R':crossloads(2,'R',case) if roof else []}
   # Balcony west of new wall support is not carried by B2 in this scheme; separate exterior frame.
   loads={k:[(max(0,a),b,q) for a,b,q in ll if b>0] for k,ll in loads.items()}
   r={k:beam(0,249.5,[0,246.5],ll,EI=E*c['I']) for k,ll in loads.items()}
   rows.append(dict(case=case,roof_on_B2=roof,section=c,delta_total=sum(z['delta'] for z in r.values()),delta_live=r['L']['delta'],moment_kipft=sum(z['M'] for z in r.values())/12000,west_reaction_lb=sum(z['R']['0'] for z in r.values()),east_reaction_lb=sum(z['R']['246.5'] for z in r.values())))
(p/'truss-revision-B2.json').write_text(json.dumps(rows,indent=2))
for r in rows:
 print(r['case'],r['roof_on_B2'],r['section']['name'],round(r['delta_total'],3),round(r['delta_live'],3),round(r['moment_kipft'],1))
