"""Steel-supported lean-to option; preserve the accepted east-post frame."""
import json, math
import east_continuous_posts as E
import completion as C
from project_paths import VIZ_DIR
OUT=VIZ_DIR
OUT.mkdir(parents=True, exist_ok=True)
T=E.T.B.W.D.T

def build():
    f,s,g=E.build('W6X8.5',True,True)
    lengths=T.A.unbraced_lengths(f)
    # Replace the former separate wood-roof reactions. The actual steel
    # rafters receive self weight, canopy dead/live and wind in loadcases.py.
    f.extra_loads=[v for v in f.extra_loads if not (v[0]=='BE.upper' and 'lean-to' in v[3])]
    assert not f.extra_loads
    pitch=(268.-2.5)/12
    seats=[]; rafters=[]; cuts={}
    def beam_point(member,y):
        for m,i,j in f.segments:
            if m!=member:continue
            a,b=f.xyz(i),f.xyz(j)
            if min(a[1],b[1])-1e-8<=y<=max(a[1],b[1])+1e-8:
                t=(y-a[1])/(b[1]-a[1])
                return tuple(a[k]+t*(b[k]-a[k]) for k in range(3))
        raise ValueError((member,y))
    for k in range(12):
        y=2.5+(k+.5)*pitch
        high,low=beam_point('BE.upper',y),beam_point('BE',y)
        ht=high[2]+f.section_of['BE.upper'].d/2
        lt=low[2]+f.section_of['BE'].d/2
        # Upper top corner is flush with the east edge of the high beam's
        # top flange. Lower top corner reaches the outer/east top corner of BE.
        hx=high[0]+f.section_of['BE.upper'].b/2
        lx=low[0]+f.section_of['BE'].b/2
        slope=(ht-lt)/(lx-hx)
        full_depth=2*math.sqrt(1+slope*slope)
        polygon=[(hx,ht),(lx,lt),(lx-full_depth/slope,lt),(hx,ht-full_depth)]
        # Vertical upper cut, horizontal lower cut; use cut-face centroids
        # for eccentric links back to the supporting beam axes.
        endpoints=[(hx,y,ht-full_depth/2),(lx-full_depth/(2*slope),y,lt)]
        nodes=[]
        for side,member,p,end in zip(['high','low'],['BE.upper','BE'],[high,low],endpoints):
            bn=C._split(f,member,p,f'LT.beam.{k+1}.{side}')
            rn=f'LT.rafter.{k+1}.{side}'
            f.nodes[rn]=dict(x=end[0],y=end[1],z=end[2],support=False,members=[])
            nodes.append(rn)
            f.links.append((bn,rn,'Direct bevel-cut connection; eccentric offset to pinned rafter end'))
        name=f'LT.R{k+1:02d}'
        C._add_member(f,name,*nodes,'HSS2X2X1/8',2,2,'Rafters',
                      note='Direct fit: vertical upper cut flush to BE.upper east flange edge; horizontal lower cut on BE top to east edge')
        # The roof reaches the top corners beyond the cut-face centroids.
        # Expand tributary width equivalently to retain the full roof area
        # for dead, live, and wind loading on the shorter analytical axis.
        top_length=math.hypot(lx-hx,ht-lt)
        f.members[name]['canopy_area_factor']=top_length/f.member_length(name)
        lengths[name]=top_length
        cuts[name]=dict(y=y,polygon=polygon,top_length=top_length,angle_deg=math.degrees(math.atan(slope)),top_run=lx-hx)
        rafters.append(name)
    f.unbraced_length_overrides.update(lengths)
    T.clean(f)
    info=dict(rafters=rafters,section='HSS2X2X1/8',count=12,spacing=pitch,
              horizontal_run=cuts[rafters[0]]['top_run'],roof_y=[2.5,268],seats=seats,cuts=cuts,
              fit='Top edge from high beam top/east corner to lower beam top/east corner; vertical high cut, horizontal low cut; no raised seats',
              original_reactions_removed=True,existing_wall_bearing=False)
    return f,s,info

if __name__=='__main__':
    f,s,g=build()
    (OUT/'geometry.json').write_text(json.dumps(dict(**g,nodes=f.nodes,segments=f.segments,links=f.links,sections={m:v.name for m,v in f.section_of.items()}),indent=2))
    T.OUT=OUT
    T.solve('analysis',f,s,second_order=True)
