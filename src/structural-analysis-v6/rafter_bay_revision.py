"""Solar rafters seated at B-SO/R-W1; upper-roof bay bracing trial."""
import math,json
import west_lower_removal as W
import completion as C
OUT=W.OUT/'rafter-bay-revision'
OUT.mkdir(exist_ok=True)

def build():
    f,s,c=W.build('W1+W2')
    # Preserve prior unbraced lengths; added intermediate joints alone do not
    # establish torsional/out-of-plane restraint for the receiving beams.
    lengths=W.D.T.A.unbraced_lengths(f)
    y0,y1,y2=-63.,2.5,71.
    bso_top=112.5+f.section_of['B-SO'].d/2
    rw_top=155.0664427665153+f.section_of['R-W1'].d/2
    slope=(rw_top-bso_top)/(y1-y0)
    offset=math.sqrt(1+slope*slope) # half depth of 2-inch RS, normal to axis
    def z(y):return bso_top+offset+(y-y0)*slope
    solar={m for m in f.members if m.startswith('RS @ ')}|{'W.slope','E.slope'}
    moving={n for m,i,j in f.segments if m in solar or m=='CT.bottom' for n in(i,j)}
    for n in moving:f.nodes[n]['z']=z(f.nodes[n]['y'])
    added_links=[]
    # Existing B-SO seats/links retained. Add the actual intermediate support
    # to each solar rafter, split its beam seat and tie their centerlines.
    for m in sorted(solar):
        x=next(f.xyz(i)[0] for mm,i,j in f.segments if mm==m)
        en=C._split(f,m,(x,y0,z(y0)),f'{m}.BSO')
        eb=C._split(f,'B-SO',(x,y0,112.5),f'BSO.seat@{x:g}')
        if not any({i,j}=={en,eb} for i,j,_ in f.links):
            f.links.append((en,eb,'solar edge/rafter seat connection to B-SO'))
        rn=C._split(f,m,(x,y1,z(y1)),f'{m}.RW1')
        bn=C._split(f,'R-W1',(x,y1,155.0664427665153),f'RW1.seat@{x:g}')
        if rn!=bn:
            link=(rn,bn,'solar rafter seat connection to R-W1')
            f.links.append(link);added_links.append(link)
    # Side slope members retain their existing post/edge-frame connections;
    # the 2-inch RS members define the requested common solar plane.
    xs=sorted({f.xyz(i)[0] for m,i,j in f.segments if m.startswith('RF @ ')})
    # Include perimeter framing as boundaries of the first/last rafter bay.
    xs=sorted(set(xs+[-34.,211.5]))
    def node(x,y):
        target=(x,y,233.25)
        n=min(f.nodes,key=lambda n:math.dist(f.xyz(n),target))
        assert math.dist(f.xyz(n),target)<.01,(target,n,f.xyz(n))
        return n
    added=[]
    for row,(ya,yb) in enumerate([(71.,185.),(185.,268.)]):
        for k,(xa,xb) in enumerate(zip(xs,xs[1:])):
            a,b=(node(xa,ya),node(xb,yb)) if (k+row)%2==0 else (node(xa,yb),node(xb,ya))
            name=f'RF-BR.{row+1}.{k+1}'
            C._add_member(f,name,a,b,'HSS2X2X1/8',2,2,'Bracing',note='Short pinned diagonal within RF rafter bay; full-length buckling check')
            added.append(name);lengths[name]=f.member_length(name)
    # Numerically resolve pinned brace force recovery, retaining physical pins.
    for member in added+['BR-W-2','BR-NU-1','W.rear.brace']:
        for mm,i,j in list(f.segments):
            if mm!=member:continue
            a,b=f.xyz(i),f.xyz(j);count=math.ceil(math.dist(a,b)/12)
            for k in range(1,count):C._split(f,member,tuple(a[q]+(b[q]-a[q])*k/count for q in range(3)),f'BAYM.{len(f.nodes)}')
        origin=min(f.xyz(n) for mm,i,j in f.segments if mm==member for n in(i,j))
        f.segments=[(mm,j,i) if mm==member and math.dist(f.xyz(i),origin)>math.dist(f.xyz(j),origin) else (mm,i,j) for mm,i,j in f.segments]
    for member in solar:
        if member.startswith('RS @ '):lengths[member]=max(lengths[member],f.member_length(member))
    f.unbraced_length_overrides.update(lengths)
    W.D.T.clean(f)
    assert 'BR-ROOF-D1' not in f.members
    for m in solar:
        for mm,i,j in f.segments:
            if mm==m:
                for n in(i,j):assert abs(f.xyz(n)[2]-z(f.xyz(n)[1]))<1e-6
    info=dict(slope=slope,angle_deg=math.degrees(math.atan(slope)),solar_eave_center_z=z(y0),solar_RW1_center_z=z(y1),clerestory_bottom_z=z(y2),clerestory_top_z=233.25,clerestory_axis_height=233.25-z(y2),new_braces=added,new_seat_links=added_links,brace_weight_lb=sum(f.member_weight(m) for m in added),notes=['RS2x2 slope referenced to ideal bearing planes at B-SO and R-W1 top flanges. Sloped seat/cap geometry and welds remain undesigned.','Side 3x3 slope members share the reference centerline and retain edge/post connections; their larger section needs separate connection detailing.'])
    return f,s,info

if __name__=='__main__':
    f,s,info=build()
    (OUT/'geometry.json').write_text(json.dumps(dict(**info,nodes=f.nodes,segments=f.segments,links=f.links,sections={m:v.name for m,v in f.section_of.items()}),indent=2))
    W.D.T.OUT=OUT;W.D.T.solve('rafter-bay-revision',f,s,second_order=True)
