"""P-Delta screening of the owner-approved wall-aligned frame and door posts."""
import json
import math
from pathlib import Path
import s3_final_checks as FC
import s3_removal_study as T
import completion as C
import frame as F

OUT=T.OUT/'door-frame'

def build(thickness='1/4', mesh=0):
    f,s=FC.final_frame();T.clean(f)
    original=T.A.unbraced_lengths(f)
    for v in f.nodes.values():
        if abs(v['y']+6)<.001:
            v['y']=2.5
            if v['z']>112.51:v['z']+=8.5*.57735
    # New gravity supports are not credited as beam torsional restraint.
    f.unbraced_length_overrides={m:original[m] for m in ('B-S','R-W1')}
    for side,x in [('W',110.5),('E',144.5)]:
        name='DOOR-'+side
        top=C._split(f,'B-S',(x,2.5,112.5),name+'.top')
        base=name+'.base'
        f.nodes[base]=dict(x=x,y=2.5,z=0,support=True,members=[])
        # b=6 along local z (model north/south); d=2 along local y (east/west).
        C._add_member(f,name,base,top,'HSS6X2X'+thickness,6,2,'Columns',note='Pinned base and pinned head, 6 inches through wall; full-height unbraced')
        f.pinned_ends.append((name,top))
        f.unbraced_length_overrides[name]=112.5
    T.clean(f)
    if mesh:
        lengths=T.A.unbraced_lengths(f)
        f.unbraced_length_overrides.update(lengths)
        for member,i,j in list(f.segments):
            if member not in ('BR-N-1','RS @ 170.58'):continue
            a,b=f.xyz(i),f.xyz(j)
            count=math.ceil(math.dist(a,b)/mesh)
            for k in range(1,count):
                xyz=tuple(a[q]+(b[q]-a[q])*k/count for q in range(3))
                C._split(f,member,xyz,f'MESH.{len(f.nodes)}')
        T.clean(f)
    model,index=F.build(f)
    for name in ('DOOR-W','DOOR-E'):
        el=model.members[index[name][0]]
        assert abs(el.T()[1,0])==1 and abs(el.T()[2,2])==1
        assert f.section_of[name].b==6 and f.section_of[name].d==2
    assert not any('RWBS' in m for m in f.members)
    assert 'S3.base' not in f.nodes and 'S3' in f.members
    return f,s

def run(thickness,mesh=0):
    f,s=build(thickness,mesh)
    tag='door-posts-'+thickness.replace('/','-')+'-pdelta'+(f'-mesh{mesh:g}' if mesh else '')
    old=T.OUT;T.OUT=OUT
    try:r=T.solve(tag,f,s,second_order=True)
    finally:T.OUT=old
    (OUT/(tag+'-geometry.json')).write_text(json.dumps(dict(nodes=f.nodes,segments=f.segments,sections={m:v.as_dict() for m,v in f.section_of.items()},pinned_ends=f.pinned_ends,unbraced_length_overrides=f.unbraced_length_overrides,notes=['Pinned post heads and bases; no moment-frame credit for door posts.','New foundations assumed translationally fixed; foundations and anchorage not designed.','Column analysis to beam centerline; actual post ends at beam underside.','Six-inch section dimension through wall; two inches along wall.']),indent=2))
    return r

if __name__=='__main__':
    import sys
    run(sys.argv[1] if len(sys.argv)>1 else '1/4',float(sys.argv[2]) if len(sys.argv)>2 else 0)
