import study,json,math
from pathlib import Path
O=Path(__file__).parent;r=json.loads((O/'results.json').read_text());sel={f:next(i for i,s in enumerate(study.SECS) if s['name']==v['name']) for f,v in r['selection'].items()}
o,_,_=study.run(sel,omit_s3=True)
r['sensitivity']['without optional S3']={c:{k:d[k] for k in ['max_vertical_in','max_horizontal_in','columns']} for c,d in o.items() if c in ['service storage bands','lateral X sensitivity','lateral Y sensitivity']}
(O/'results.json').write_text(json.dumps(r,indent=2))
# Secondary member tests are independent simply supported flexure screens, not complete joist designs.
L=115.25;q=(9+40)*(16/12)/12
rows=[]
for d in [7.25,9.25]:
 A=1.5*d;I=1.5*d**3/12;S=I/(d/2);E=1.6e6;M=q*L*L/8+1000*L/4
 rows.append({'member':f'wood 1.5 x {d} in; E=1.6e6 assumed','weight_plf_at_35pcf':A/144*35,'required_bending_stress_psi':M/S,'total_deflection_in':5*q*L**4/(384*E*I)+1000*L**3/(48*E*I),'live_deflection_in':5*(40*16/12/12)*L**4/(384*E*I)+1000*L**3/(48*E*I),'live_limit_L360':L/360})
for s in [s for s in study.SECS if s['d'] in [3,4] and s['t'] in [.125,.188]]:
 I=s['I'];M=q*L*L/8+1000*L/4;rows.append({'member':s['name'],'weight_plf':s['w'],'elastic_stress_psi':M/s['S'],'total_deflection_in':5*q*L**4/(384*29e6*I)+1000*L**3/(48*29e6*I),'live_deflection_in':5*(40*16/12/12)*L**4/(384*29e6*I)+1000*L**3/(48*29e6*I),'live_limit_L360':L/360})
roof=[]
for s in study.SECS:
 L=224.25;q=((9.5/math.cos(math.pi/6)+20)*4+s['w'])/12 # includes own weight again: conservative check
 delta=5*q*L**4/(384*29e6*s['I']);stress=q*L*L/8/s['S']
 if delta<L/240 and stress<50000/1.67:roof.append({'member':s['name'],'plf':s['w'],'delta_in':delta,'stress_psi':stress})
(O/'secondary-checks.json').write_text(json.dumps({'floor_joist_1000lb_on_one_member_plus_uniform':rows,'roof_purlin_4ft_plan_spacing_candidates':sorted(roof,key=lambda x:x['plf']),'notes':'Simple flexure only. No bearing, local patch deck design, vibration, cold-formed design, connections, or timber grade verification.'},indent=2))
print('Extra checks complete; omitted-S3 service deflection:',r['sensitivity']['without optional S3']['service storage bands']['max_vertical_in'])
