"""Independent checks and local-load demands; import analyze.py without running batch."""
from analyze import beam,E,OUT,Y,TF,TR,system
import json,numpy as np
r=beam(-32,249.5,[-32,224.25],[(0,249.5,60)],points=[(96.125,1000)],step=4)
s=beam(-32,249.5,[-32,224.25],[(0,249.5,60)],points=[(96.125,1000)],step=2)
assert abs(r['delta']/s['delta']-1)<.001
# One joist receiving the entire 1000 lb patch, before distributed load. No assumed plywood sharing.
L=185-69.75
joist={'span_in':L,'patch_only_midspan_moment_lb_in':1000*L/4,'patch_only_each_end_reaction_lb':500,
       'I_required_for_L360_at_E1_6million_in4':1000*L**3/(48*1.6e6*(L/360))}
# Idealized cabinet upright geometry; NOT code capacity, ignores rounded corners/tolerances.
b=1;d=2;t=.12;Iw=(d*b**3-(d-2*t)*(b-2*t)**3)/12
cab={'assumed_wall_in':t,'ideal_weak_I_in4':Iw,'unbraced_length_in':98.5,
     'ideal_pinned_Euler_load_lb':np.pi**2*E*Iw/98.5**2,'warning':'Euler is an upper-bound elastic instability reference, not allowable strength. Actual gauge, bracing, material and connections unverified.'}
# Global load balance through sequential transfer, includes W-rail self weight.
bal={}
for case in ['occupied40','storage_bands','storage125','patch1000']:
 for kind in ['D','L','R']:
  z=system(case,kind);external=sum(z['columns'].values())+sum(v for k,v in z['E-rail']['R'].items() if float(k) not in (Y[0],Y[-1]))+sum(z['W-rail']['R'].values())
  # Headers' input includes rail-end transferred forces, subtract those to recover external applied load.
  applied=sum(z[n]['load'] for n in ['B1','B2','S-header','N-header','W-rail'])-z['E-rail']['R'][str(Y[0])]-z['E-rail']['R'][str(Y[-1])]+(39/12*(Y[-1]-Y[0]) if kind=='D' else 0)
  assert abs(external-applied)<.01
  bal[case+'_'+kind]=dict(applied_lb=applied,support_reactions_lb=external)
(OUT/'detail-checks.json').write_text(json.dumps(dict(mesh_relative_delta_difference=abs(r['delta']/s['delta']-1),joist=joist,cabinet=cab,balance=bal),indent=2))
print(json.dumps(dict(joist=joist,cabinet=cab),indent=2))
# Manufacturer shear-deflection expression for uniform wood beam, consistent with Timoshenko stiffness.
import analyze
b=7.;d=18.;Em=2e6;L=240.;q=10.;I=b*d**3/12
analyze.SHEAR_GA=Em*b*d/19.2
z=beam(0,L,[0,L],[(0,L,q)],EI=Em*I,step=2)
expected=5*q*L**4/(384*Em*I)+q*L**2/(8*analyze.SHEAR_GA)
assert abs(z['delta']/expected-1)<1e-5
analyze.SHEAR_GA=None
print('PASS: wood bending + shear deformation agrees with manufacturer expression')
