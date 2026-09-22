import numpy as np
from frame_solver import Frame,E,test
print(test())
s={'A':4.,'I':50.,'J':80.};L=120.;P=1000.
e=[{'ij':(0,1),'family':'s','releases':[4,5]},{'ij':(1,2),'family':'s','releases':[10,11]}]
f=Frame([[0,0,0],[60,0,0],[120,0,0]],e,{'s':s},list(range(6))+list(range(12,18)))
F=np.zeros(18);F[8]=-P;u,r,ends=f.solve(F)
assert abs(u[8]/(-P*L**3/(48*E*s['I']))-1)<1e-9
assert abs(ends[0][4])+abs(ends[1][10])<1e-8
print('PASS released-end beam: zero end moment and exact midspan deflection')
