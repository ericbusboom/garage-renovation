"""Linear elastic 3D Euler-Bernoulli frame, lb/in/radians; six DOFs per node.
No automatic fictitious restraints. Includes torsion; excludes warping and geometric stiffness.
"""
import numpy as np
from scipy.sparse import lil_matrix
from scipy.sparse.linalg import splu
E=29e6;G=E/2.6

def element(a,b,s,stiffness=1):
 ex=b-a;L=np.linalg.norm(ex);ex/=L
 ref=np.array([0.,0.,1.]) if abs(ex[2])<.9 else np.array([0.,1.,0.])
 ey=np.cross(ref,ex);ey/=np.linalg.norm(ey);ez=np.cross(ex,ey)
 R=np.array([ex,ey,ez]);T=np.zeros((12,12))
 for i in [0,3,6,9]:T[i:i+3,i:i+3]=R
 k=np.zeros((12,12))
 for ix,c in [([0,6],E*s['A']/L),([3,9],G*s['J']/L)]:k[np.ix_(ix,ix)]+=c*np.array([[1,-1],[-1,1]])
 block=np.array([[12,6*L,-12,6*L],[6*L,4*L*L,-6*L,2*L*L],[-12,-6*L,12,-6*L],[6*L,2*L*L,-6*L,4*L*L]])
 k[np.ix_([1,5,7,11],[1,5,7,11])]+=E*s['I']/L**3*block
 signs=np.diag([1,-1,1,-1]);k[np.ix_([2,4,8,10],[2,4,8,10])]+=E*s['I']/L**3*(signs@block@signs)
 return stiffness*k,T,L

class Frame:
 def __init__(self,nodes,elements,sections,fixed,stiffness=1):
  self.nodes=np.array(nodes,float);self.elements=elements;n=len(nodes)*6;K=lil_matrix((n,n));self.cache=[]
  for e in elements:
   i,j=e['ij'];s=sections[e['family']];k,T,L=element(self.nodes[i],self.nodes[j],s,stiffness)
   releases=e.get('releases',[])
   if releases:
    retained=np.setdiff1d(np.arange(12),releases);cond=k[np.ix_(retained,retained)]-k[np.ix_(retained,releases)]@np.linalg.solve(k[np.ix_(releases,releases)],k[np.ix_(releases,retained)])
    k=np.zeros((12,12));k[np.ix_(retained,retained)]=cond
   ix=np.r_[np.arange(6*i,6*i+6),np.arange(6*j,6*j+6)];K[np.ix_(ix,ix)]+=T.T@k@T;self.cache.append((ix,k,T,L))
  self.K=K.tocsc();self.fixed=np.array(sorted(fixed));self.inactive=np.flatnonzero(np.asarray(abs(self.K).sum(axis=1)).ravel()<1e-6)
  self.free=np.setdiff1d(np.arange(n),np.r_[self.fixed,self.inactive]);self.factor=splu(self.K[self.free,:][:,self.free])
 def solve(self,F):
  assert max(abs(F[self.inactive]),default=0)<1e-7, 'Load on an unrestrained inactive DOF'
  u=np.zeros(len(F));u[self.free]=self.factor.solve(F[self.free]);r=self.K@u-F
  assert np.max(abs(r[self.free]))<max(.01,np.max(abs(F))*1e-6)
  end=[k@T@u[ix] for ix,k,T,L in self.cache]
  return u,r,end

def test():
 s={'A':4.,'I':50.,'J':80.};L=120.;P=1000
 f=Frame([[0,0,0],[L/2,0,0],[L,0,0]],[{'ij':(0,1),'family':'s'},{'ij':(1,2),'family':'s'}],{'s':s},range(6))
 F=np.zeros(18);F[14]=-P;u,r,_=f.solve(F)
 assert abs(u[14]/(-P*L**3/(3*E*s['I']))-1)<1e-9
 assert abs(r[2]-P)<1e-6 and abs(r[4]+P*L)<1e-6
 F=np.zeros(18);F[12]=P;u,r,_=f.solve(F);assert abs(u[12]/(P*L/(E*s['A']))-1)<1e-9
 F=np.zeros(18);F[15]=P;u,r,_=f.solve(F);assert abs(u[15]/(P*L/(G*s['J']))-1)<1e-9
 # Simply supported bending about the other transverse axis.
 fixed=[0,1,2,3,4,6*2+1,6*2+2];f=Frame([[0,0,0],[L/2,0,0],[L,0,0]],[{'ij':(0,1),'family':'s'},{'ij':(1,2),'family':'s'}],{'s':s},fixed)
 F=np.zeros(18);F[7]=-P;u,r,_=f.solve(F);assert abs(u[7]/(-P*L**3/(48*E*s['I']))-1)<1e-9
 return 'PASS cantilever bending, axial, torsion, simple beam point load, residual equilibrium'
