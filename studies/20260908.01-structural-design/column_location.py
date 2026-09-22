"""Cabinets disengaged: trial replacement-column locations; gravity screening only."""
import json
from pathlib import Path
from analyze import beam, crossloads,Y,E
OUT=Path(__file__).parent

def rail_case(xeast,interior=None):
    pp=[]
    for i in (1,2):
        loads=sum((crossloads(i,k,'storage_bands') for k in ['D','L','R']),[])+[(-32,249.5,49/12)]
        r=beam(-32,249.5,[-32,xeast],loads)
        pp.append((Y[i],r['R'][str(xeast)]))
    supports=[Y[0],Y[-1]] if interior is None else [Y[0],interior,Y[-1]]
    r=beam(Y[0],Y[-1],supports,[(Y[0],Y[-1],49/12)],pp,EI=E*272)
    return {'column_y':interior,'rail_x':xeast,'M_kipft':r['M']/12000,'deflection_in':r['delta'],'reactions_lb':r['R']}
results={'north_only_current_rail':rail_case(224.25),'east_wall_options':[rail_case(246.5,float(y)) for y in range(95,186,5)]}
(OUT/'column-location-study.json').write_text(json.dumps(results,indent=2))
print(json.dumps(results,indent=2))
