"""Remove only W1/W2 below BW from the analyzed steel-door-post option."""
import json
import sys
import door_post_study as D
import column_study as CS
OUT=D.OUT/'west-column-options'
OUT.mkdir(exist_ok=True)

def build(which, west_stiff=False, north_stiff=False):
    f,s=D.build('1/4',12)
    cuts={}
    for m in which.split('+'):
        before=[(i,j,f.xyz(i),f.xyz(j)) for name,i,j in f.segments if name==m and min(f.xyz(i)[2],f.xyz(j)[2])>=112.5]
        cuts[m]=CS.cut_ground_floor(f,m,112.5)
        after=[(i,j,f.xyz(i),f.xyz(j)) for name,i,j in f.segments if name==m]
        assert before==after and m+'.base' not in f.nodes
    if west_stiff:f.section_of['BR-W-2']=D.T.section('HSS3X3X1/4')
    if north_stiff:f.section_of['BR-N-1']=D.T.section('HSS3X3X1/8')
    D.T.clean(f)
    return f,s,cuts

if __name__=='__main__':
    which=sys.argv[1]
    f,s,cuts=build(which)
    tag=which.lower().replace('+','-')+'-lower-removed'
    # Write manifest before solving so even an unstable run is reviewable.
    (OUT/(tag+'-geometry.json')).write_text(json.dumps(dict(cuts=cuts,nodes=f.nodes,segments=f.segments,sections={m:v.name for m,v in f.section_of.items()}),indent=2))
    D.T.OUT=OUT
    D.T.solve(tag,f,s,second_order=True)
