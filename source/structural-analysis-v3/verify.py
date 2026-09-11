import numpy as np
from frame_solver import Frame,E,test
print(test())
s=dict(A=9,I=100,Iy=100,Iz=15,J=.8)
ff=Frame([[0,0,0],[120,0,0]],[dict(ij=[0,1],family='s')],{'s':s},range(6))
for dof,I in [(8,100),(7,15)]:
 F=np.zeros(12);F[dof]=-1000;u,r,f=ff.solve(F);assert abs(u[dof]/(-1000*120**3/(3*E*I))-1)<1e-9
print('PASS W-section strong/weak bending axis benchmark')
# Square HSS must retain original solver behavior.
s={'A':4.,'I':50.,'J':80.};e=[{'ij':(0,1),'family':'s','releases':[4,5]},{'ij':(1,2),'family':'s','releases':[10,11]}]
f=Frame([[0,0,0],[60,0,0],[120,0,0]],e,{'s':s},list(range(6))+list(range(12,18)))
F=np.zeros(18);F[8]=-1000;u,r,ends=f.solve(F)
assert abs(u[8]/(-1000*120**3/(48*E*s['I']))-1)<1e-9
assert abs(ends[0][4])+abs(ends[1][10])<1e-8
print('PASS released-end bending benchmark')
