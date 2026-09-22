"""In-plane bracing between the actual R-W1 and B-S elevations."""
import json
from dataclasses import asdict,fields
import s3_removal_study as T
from s3_final_checks import final_frame
import completion as C

OUT=T.OUT/'rw1-bs-bracing'
OUT.mkdir(exist_ok=True)

def build(layout='ends',large_beam=False,north_upgrade=False):
    f,s=final_frame()
    if not large_beam:f.section_of['R-W1']=T.section('W12X16')
    if north_upgrade:f.section_of['BR-N-1']=T.section('HSS3X3X1/8')
    original=T.A.unbraced_lengths(f)
    f.unbraced_length_overrides={m:original[m] for m in ['R-W1','B-S']}
    top=sorted({n for m,i,j in f.segments if m=='R-W1' for n in (i,j)},key=lambda n:f.xyz(n)[0])
    a,b=f.xyz(top[0]),f.xyz(top[-1]);left,right=a[0],b[0]
    bottom_z=f.xyz('@211.5,3')[2]
    # Three equal bays. Ends leave the middle bay clear; truss braces all three
    # and adds two verticals. Crossed diagonals are unconnected at crossings.
    xs=[left+(right-left)*i/3 for i in range(4)]
    panels=range(3) if layout=='truss' else [0,2]
    added=[]
    for i in range(4):
        x=xs[i];t=(x-left)/(right-left)
        C._split(f,'R-W1',(x,a[1],a[2]+t*(b[2]-a[2])),f'RWBS.top.{i}')
        C._split(f,'B-S',(x,a[1],bottom_z),f'RWBS.bottom.{i}')
    def node(m,x):return min({n for mm,i,j in f.segments if mm==m for n in(i,j)},key=lambda n:abs(f.xyz(n)[0]-x))
    def add(name,n1,n2):
        C._add_member(f,name,n1,n2,'HSS2-1/2X2-1/2X1/8',2.5,2.5,'Bracing',note='R-W1/B-S in-plane bracing; no out-of-plane restraint credit')
        added.append(name)
    for i in panels:
        add(f'RWBS.X{i+1}a',node('B-S',xs[i]),node('R-W1',xs[i+1]))
        add(f'RWBS.X{i+1}b',node('R-W1',xs[i]),node('B-S',xs[i+1]))
    if layout=='truss':
        for i in [1,2]:add(f'RWBS.V{i}',node('B-S',xs[i]),node('R-W1',xs[i]))
    T.clean(f)
    assert 'S3.base' not in f.nodes
    assert 'S3' in f.members
    assert abs(f.member_length('R-W1')-245.5)<1e-6
    assert abs(f.member_length('B-S')-281.5)<1e-6
    assert T.A.unbraced_lengths(f)['R-W1']>=245.5
    for m,i,j in f.segments:
        if m in added:
            assert min(f.xyz(i)[2],f.xyz(j)[2])>=bottom_z
            assert abs(f.xyz(i)[1]+6)<1e-6 and abs(f.xyz(j)[1]+6)<1e-6
    return f,s,added

def run(tag,layout,large=False,north_upgrade=False):
    f,s,added=build(layout,large,north_upgrade)
    old=T.OUT;T.OUT=OUT
    try:r=T.solve(tag,f,s,second_order=True)
    finally:T.OUT=old
    manifest=dict(layout=layout,north_upgrade=north_upgrade,beam=f.section_of['R-W1'].name,added=added,
        added_weight_lb=sum(f.member_weight(m) for m in added),
        unbraced_length_overrides=f.unbraced_length_overrides,
        nodes={n:f.xyz(n) for m,i,j in f.segments if m in added for n in (i,j)},
        retained_other_reinforcement=['BR-W-2 HSS3X3X3/16','double shelf SH joist 15'],
        note='Pin-ended braces; crossings unconnected. W1/W2 retained; S3 retained only above loft.')
    (OUT/(tag+'-geometry.json')).write_text(json.dumps(manifest,indent=2))
    return r

if __name__=='__main__':
    run('ends-w12','ends')
    run('truss-w12','truss')
    run('ends-w14','ends',True)
