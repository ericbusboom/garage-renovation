"""One upper-roof-plane diagonal, retaining clear space below BW."""
import json,math
import west_lower_removal as W
import completion as C

def build():
    f,s,c=W.build('W1+W2')
    lengths=W.D.T.A.unbraced_lengths(f)
    def node(x,y,z):
        n=min(f.nodes,key=lambda n:math.dist(f.xyz(n),(x,y,z)))
        assert math.dist(f.xyz(n),(x,y,z))<.01
        return n
    a=node(-34,71,233.25);b=node(211.5,268,233.25)
    name='BR-ROOF-D1'
    C._add_member(f,name,a,b,'HSS5X5X1/4',5,5,'Bracing',note='Trial roof-plane diagonal; pinned ends; full length unbraced')
    lengths[name]=f.member_length(name)
    f.unbraced_length_overrides.update(lengths)
    aa,bb=f.xyz(a),f.xyz(b)
    for k in range(1,math.ceil(math.dist(aa,bb)/12)):
        count=math.ceil(math.dist(aa,bb)/12)
        C._split(f,name,tuple(aa[q]+(bb[q]-aa[q])*k/count for q in range(3)),f'ROOF-D1.{k}')
    # Refine the other long braces whose force-recovery spikes become visible
    # in this load path. Preserve full unbraced lengths and physical end pins.
    for member in ('BR-W-2','BR-NU-1'):
        for mm,i,j in list(f.segments):
            if mm!=member:continue
            a0,b0=f.xyz(i),f.xyz(j)
            count=math.ceil(math.dist(a0,b0)/12)
            for k in range(1,count):
                C._split(f,member,tuple(a0[q]+(b0[q]-a0[q])*k/count for q in range(3)),f'RF.{len(f.nodes)}')
        origin=min(f.xyz(n) for mm,i,j in f.segments if mm==member for n in (i,j))
        f.segments=[(mm,j,i) if mm==member and math.dist(f.xyz(i),origin)>math.dist(f.xyz(j),origin) else (mm,i,j) for mm,i,j in f.segments]
    W.D.T.clean(f)
    return f,s

if __name__=='__main__':
    f,s=build();W.D.T.OUT=W.OUT
    W.D.T.solve('both-removed-roof-diagonal',f,s,second_order=True)
