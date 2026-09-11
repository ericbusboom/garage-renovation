"""Generate two four-view roof studies from one explicit geometric definition.
No FreeCAD document is modified. Lengths are inches; heights are from ground.
"""
from pathlib import Path
import json, math
import numpy as np
from PIL import Image
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon, Rectangle, Arc
from matplotlib.backends.backend_pdf import PdfPages

ROOT=Path(__file__).resolve().parent
p=json.loads((ROOT/'parameters.json').read_text())
W=p['width_east_west']; LG=p['length_north_south']; L=LG+p['north_roof_extension']; H=p['wall_height']
B=H+p['beam_depth_assumed']; F=B+p['floor_deck_assumed']; T=p['roof_vertical_depth_assumed']
RUN=p['west_lattice_run_to_outer_post_centerline']; E=p['east_hip_maximum_inset']
YB=L-p['rear_zone_length']; M=math.tan(math.radians(p['south_roof_pitch_degrees']))
YS=p['south_roof_start_y']
HE=B-F
HS=HE-YS*M
HB=HS+YB*M
COL={'wall':'#d9dcdb','roof':'#8b9ea6','east':'#c0c9cc','timber':'#9d7044','floor':'#c1b6a3','glass':'#93b7c0','solar':'#456a80','ink':'#28363d','muted':'#67747a','dim':'#446b82','head':'#477d63'}
base=json.loads((ROOT.parent/'model/scene.json').read_text())
frame=json.loads((ROOT.parent/'model/plan_structure.json').read_text())
# User correction: north roof and loft wall end at the outer beam face, 6 in
# beyond the existing garage wall. Align the conceptual north frame with it.
for member in frame:
    if member['y']>240:
        member['y']=L-2-member['height']/2 if member['post'] else L-member['height']
    elif not member['post'] and member['height']>member['width'] and member['y']+member['height']>240:
        member['height']=L-4-member['y']

def ft(v):
    sign='−' if v<0 else '';v=abs(v);n=round(v*4)/4;feet=int(n//12);inch=n-feet*12
    whole=int(inch);frac={0:'',.25:'¼',.5:'½',.75:'¾'}[round(inch-whole,2)]
    return f'{sign}{feet}′ {whole}{frac}″'

def profiles(kind):
    def h(y):
        if kind=='A' and y>YB:return HB+(y-YB)*p['rear_roof_rise_per_foot_assumed']/12
        return HS+M*y
    k=(h(L)-HE)/E
    def east_hip(y):return W-(h(y)-HE)/k
    def z(x,y):return F+T+min(h(y),HE+k*(W-x))
    return h,k,east_hip,z

def geometry(kind):
    h,k,xhip,z=profiles(kind);polys=[]
    def poly(v,color,name=''):
        polys.append({'vertices':[[float(a) for a in q] for q in v],'color':color,'name':name})
    def box(x,y,z0,dx,dy,dz,color,name):
        v=[[x,y,z0],[x+dx,y,z0],[x+dx,y+dy,z0],[x,y+dy,z0],[x,y,z0+dz],[x+dx,y,z0+dz],[x+dx,y+dy,z0+dz],[x,y+dy,z0+dz]]
        for inds in [[0,3,2,1],[4,5,6,7],[0,1,5,4],[1,2,6,5],[2,3,7,6],[3,0,4,7]]:poly([v[i] for i in inds],color,name)
    def stick(a,b,width,color,name):
        a=np.array(a,dtype=float);b=np.array(b,dtype=float);v=b-a;v/=np.linalg.norm(v)
        t=np.cross(v,[0,0,1])
        if np.linalg.norm(t)<.01:t=np.cross(v,[0,1,0])
        t=t/np.linalg.norm(t)*width/2;u=np.cross(v,t)
        vs=[a-t-u,a+t-u,a+t+u,a-t+u,b-t-u,b+t-u,b+t+u,b-t+u]
        for ix in [[0,3,2,1],[4,5,6,7],[0,1,5,4],[1,2,6,5],[2,3,7,6],[3,0,4,7]]:poly([vs[i] for i in ix],color,name)
    # Reuse all measured walls and windows; remove the current hip roof.
    for part in base['parts']:
        if part['group'] not in ('existing','infill'):continue
        c=COL['glass'] if part['group']=='infill' and 'window' in part['name'].lower() else COL['wall']
        if part['group']=='infill' and 'door' in part['name'].lower():c=COL['timber']
        if 'Floor datum' in part['name']:c='#b5b8b5'
        for tri in part['triangles']:poly([part['vertices'][i] for i in tri],c,part['name'])
    # Source frame in plan: only outboard west line and connecting lengths change.
    for s in frame:
        x=W-s['x']-s['width'];y=s['y'];dx=s['width'];dy=s['height']
        if s['post'] and s['x']>300:x=-RUN-dx/2
        elif not s['post']:
            if s['x']>300:x=-RUN-dx/2
            elif s['x']>=255: x,dx=-RUN+3,(-5.75)-(-RUN+3)
            elif s['width']>300:
                xmax=W-s['x'];x=-RUN+3;dx=xmax-x
        box(x,y,0 if s['post'] else H,dx,dy,H if s['post'] else p['beam_depth_assumed'],COL['timber'],s['id'])
    # The low south tip has no usable loft floor, avoiding roof/floor overlap.
    floor_start=max(0,-HS/M)
    poly([[0,floor_start,F],[W,floor_start,F],[W,L,F],[0,L,F]],COL['floor'],'Loft floor datum')
    ys=[YS,YB,L] if kind=='A' else [YS,L]
    for a,b in zip(ys,ys[1:]):
        poly([[0,a,z(0,a)],[xhip(a),a,z(xhip(a),a)],[xhip(b),b,z(xhip(b),b)],[0,b,z(0,b)]],COL['roof'],'South facing roof' if a==YS else 'Rear shallow roof')
        poly([[xhip(a),a,z(xhip(a),a)],[W,a,z(W,a)],[W,b,z(W,b)],[xhip(b),b,z(xhip(b),b)]],COL['east'],'East steep plane')
        # Close the loft west wall, north wall, and east low fascia.
        aa=max(0,a)
        poly([[0,aa,B],[0,b,B],[0,b,z(0,b)-T],[0,aa,z(0,aa)-T]],COL['wall'],'West loft enclosure')
        poly([[0,a,z(0,a)-T],[0,b,z(0,b)-T],[0,b,z(0,b)],[0,a,z(0,a)]],COL['east'],'West fascia')
        poly([[W,a,B],[W,b,B],[W,b,z(W,b)],[W,a,z(W,a)]],COL['wall'],'East low fascia')
    poly([[0,L,B],[W,L,B],[W,L,z(W,L)],[xhip(L),L,z(xhip(L),L)],[0,L,z(0,L)]],COL['wall'],'North loft enclosure')
    poly([[0,YS,B],[W,YS,B],[W,YS,z(W,YS)],[0,YS,z(0,YS)]],COL['east'],'South beam-line fascia')
    poly([[0,0,B],[W,0,B],[W,0,z(W,0)-T],[xhip(0),0,z(xhip(0),0)-T],[0,0,z(0,0)-T]],COL['wall'],'South loft enclosure at wall')
    # Lattice is an open ruled surface: straight cross-members, variable pitch.
    step=p['lattice_spacing_assumed']; size=p['lattice_nominal_size']
    for y in np.arange(YS,L+.01,step):stick([-RUN,y,B+size/2],[0,y,z(0,y)-size/2],size,COL['timber'],'Open lattice rafter')
    for x in np.linspace(-RUN,0,5):
        t=(x+RUN)/RUN
        for a,b in zip(ys,ys[1:]):stick([x,a,B+size/2+t*(z(0,a)-B-size)],[x,b,B+size/2+t*(z(0,b)-B-size)],size,COL['timber'],'Open lattice stringer')
    # Illustrative solar rectangles (not a final module or setback layout).
    limit=YB if kind=='A' else L
    for y in np.arange(YS+16,limit-42,45):
        for x in np.arange(10,W-36,42):
            yy=y+39
            if x+36>xhip(yy)-8:continue
            poly([[x,y,z(x,y)+1],[x+36,y,z(x+36,y)+1],[x+36,yy,z(x+36,yy)+1],[x,yy,z(x,yy)+1]],COL['solar'],'Illustrative solar module')
    return polys

def perspective(polys,path):
    # Orthographic software depth buffer: no CAD GUI / OpenGL dependency.
    width,height=1500,1100;eye=np.array([-1,-1,.8]);eye/=np.linalg.norm(eye)
    right=np.cross([0,0,1],eye);right/=np.linalg.norm(right);up=np.cross(eye,right)
    allv=np.array([v for p in polys for v in p['vertices']]);q=np.column_stack((allv@right,allv@up))
    lo=q.min(0);hi=q.max(0);scale=min((width-130)/(hi[0]-lo[0]),(height-110)/(hi[1]-lo[1]));mid=(lo+hi)/2
    zbuf=np.full((height,width),-np.inf);img=np.full((height,width,3),255,dtype=np.uint8)
    for face in polys:
        v=np.array(face['vertices']);screen=np.column_stack(((v@right-mid[0])*scale+width/2,height/2-(v@up-mid[1])*scale,v@eye))
        rgb=np.array([int(face['color'][i:i+2],16) for i in (1,3,5)])
        n=np.cross(v[1]-v[0],v[2]-v[0]);norm=np.linalg.norm(n)
        light=.76+.24*abs(np.dot(n/norm,[-.3,-.4,.866])) if norm>0 else 1
        rgb=(rgb*light).clip(0,255).astype(np.uint8)
        for j in range(1,len(v)-1):
            a,b,c=screen[[0,j,j+1]];den=(b[1]-c[1])*(a[0]-c[0])+(c[0]-b[0])*(a[1]-c[1])
            if abs(den)<1e-9:continue
            xmin=max(0,int(np.floor(min(a[0],b[0],c[0]))));xmax=min(width-1,int(np.ceil(max(a[0],b[0],c[0]))))
            ymin=max(0,int(np.floor(min(a[1],b[1],c[1]))));ymax=min(height-1,int(np.ceil(max(a[1],b[1],c[1]))))
            xx,yy=np.meshgrid(np.arange(xmin,xmax+1)+.5,np.arange(ymin,ymax+1)+.5)
            u=((b[1]-c[1])*(xx-c[0])+(c[0]-b[0])*(yy-c[1]))/den
            v1=((c[1]-a[1])*(xx-c[0])+(a[0]-c[0])*(yy-c[1]))/den;t=1-u-v1;d=u*a[2]+v1*b[2]+t*c[2]
            buf=zbuf[ymin:ymax+1,xmin:xmax+1];mask=(u>=-1e-8)&(v1>=-1e-8)&(t>=-1e-8)&(d>buf)
            buf[mask]=d[mask];img[ymin:ymax+1,xmin:xmax+1][mask]=rgb
    Image.fromarray(img).save(path)

def line(ax,pts,**kw):
    a=np.asarray(pts);ax.plot(a[:,0],a[:,1],color=kw.pop('color',COL['ink']),lw=kw.pop('lw',1.05),**kw)
def text(ax,x,y,s,**kw):
    return ax.text(x,y,s,fontsize=kw.pop('fontsize',10),color=kw.pop('color',COL['ink']),va=kw.pop('va','center'),ha=kw.pop('ha','center'),**kw)
def dimx(ax,a,b,y,origin,label):
    for x in (a,b):line(ax,[(x,origin),(x,y-3)],color=COL['dim'],lw=.6)
    ax.annotate('',(a,y),(b,y),arrowprops={'arrowstyle':'|-|','color':COL['dim'],'lw':.8})
    text(ax,(a+b)/2,y+5,label,color=COL['dim'],fontsize=10,va='bottom',bbox={'facecolor':'white','edgecolor':'none','pad':1.5})
def dimy(ax,a,b,x,origin,label):
    for y in (a,b):line(ax,[(origin,y),(x+3,y)],color=COL['dim'],lw=.6)
    ax.annotate('',(x,a),(x,b),arrowprops={'arrowstyle':'|-|','color':COL['dim'],'lw':.8})
    text(ax,x-5,(a+b)/2,label,color=COL['dim'],fontsize=10,rotation=90)
def setup(ax,title,xlim,ylim):
    ax.set_title(title,loc='left',fontsize=13,pad=14,fontweight='medium',color=COL['ink']);ax.set_xlim(*xlim);ax.set_ylim(*ylim);ax.set_aspect('equal');ax.axis('off')
def datum(ax,x0,x1,y,label,where='left'):
    line(ax,[(x0,y),(x1,y)],lw=.7,color=COL['muted'],ls=(0,(5,3)))
    text(ax,x0 if where=='left' else x1,y-4,label,ha=where,va='top',fontsize=8.5,color=COL['muted'])

def sheet(kind,pdf):
    h,k,xhip,z=profiles(kind);polys=geometry(kind);(ROOT/f'option-{kind.lower()}-scene.json').write_text(json.dumps(polys,separators=(',',':')))
    preview=ROOT/f'option-{kind.lower()}-perspective.png';perspective(polys,preview)
    fig,axes=plt.subplots(2,2,figsize=(18,14),gridspec_kw={'hspace':.32,'wspace':.17});fig.subplots_adjust(left=.045,right=.96,bottom=.12,top=.88)
    title='A · 30° solar roof + shallow rear cap' if kind=='A' else 'B · 30° solar roof all the way north'
    fig.suptitle(title,x=.045,ha='left',fontsize=23,color=COL['ink'],fontweight='medium',y=.975)
    fig.text(.045,.94,'GARAGE ROOF STUDY   /   Ground datum = 0′ 0″   /   Loft headroom measured to underside of roof',fontsize=11,color=COL['muted'])
    fig.text(.045,.915,f'North roof top {ft(z(0,L))}   •   Rear clear height {ft(h(L))}   •   8 ft+ zone: {ft(L-(96-HS)/M)} deep   •   6 ft+ zone: {ft(L-(72-HS)/M)} deep',fontsize=12,color=COL['ink'])
    ax=axes[0,0];ax.imshow(Image.open(preview));ax.axis('off');ax.set_title('01  Southwest perspective',loc='left',fontsize=13,pad=14,fontweight='medium');ax.text(.02,.01,'SOUTH: entry + window     /     WEST: open lattice',transform=ax.transAxes,fontsize=9,color=COL['muted'])
    ax=axes[0,1];setup(ax,'02  Roof plan · north up',(-115,W+50),(-85,L+55))
    line(ax,[(0,YS),(W,YS),(W,L),(0,L),(0,YS)],lw=1.4)
    line(ax,[(0,0),(W,0)],lw=.8,color=COL['muted'],ls=(0,(4,3)))
    text(ax,W*.5,7,'South wall below',fontsize=8,color=COL['muted'])
    line(ax,[(0,LG),(W,LG)],lw=.8,color=COL['muted'],ls=(0,(4,3)))
    ax.annotate('6″ to north beam / loft wall',xy=(W*.45,(LG+L)/2),xytext=(W*.35,L+15),fontsize=8,color=COL['dim'],ha='center',arrowprops={'arrowstyle':'-','color':COL['dim'],'lw':.6})
    for yy in np.arange(YS,L+.01,p['lattice_spacing_assumed']):line(ax,[(-RUN,yy),(0,yy)],lw=.45,color=COL['muted'])
    for xx in np.linspace(-RUN,0,5):line(ax,[(xx,YS),(xx,L)],lw=.5,color=COL['muted'])
    ylist=[YS,YB,L] if kind=='A' else [YS,L]
    line(ax,[(xhip(y),y) for y in ylist],lw=1.6)
    if kind=='A':line(ax,[(0,YB),(xhip(YB),YB)],lw=1.6)
    for s in frame:
        if not s['post']:continue
        x=W-s['x']-s['width']/2;y=s['y']+s['height']/2
        if s['x']>300:x=-RUN
        ax.add_patch(Rectangle((x-3,y-3),6,6,facecolor=COL['ink']))
    ax.annotate('',(W*.42,35),(W*.42,100),arrowprops={'arrowstyle':'->','color':COL['ink'],'lw':1.3})
    text(ax,W*.42,118,'30° fall to SOUTH',fontsize=11)
    text(ax,-RUN/2,L*.52,'OPEN LATTICE',rotation=90,fontsize=9,bbox={'facecolor':'white','edgecolor':'none','pad':2})
    text(ax,W-11,L*.5,'STEEP EAST FACE',rotation=90,fontsize=8)
    if kind=='A':text(ax,90,YB+36,'Shallow cap · ¼″/ft¹',fontsize=10)
    dimx(ax,-RUN,0,YS-30,YS,'5′ 0″²');dimx(ax,0,W-36,L+24,L,ft(W-36));dimx(ax,W-36,W,L+24,L,'3′ 0″ max')
    dimy(ax,YS,L,W+35,W,ft(L-YS)+' roof run')
    dimy(ax,YS,0,-90,-RUN,ft(-YS))
    if kind=='A':dimy(ax,YB,L,-90,-RUN,'6′ 6″')
    text(ax,10,L+48,'N ↑',fontsize=12,ha='left')
    # South elevation: rear roof and eastern hip visible above the low front eave.
    ax=axes[1,0];setup(ax,'03  South elevation · looking north',(-110,W+75),(-68,310))
    # South view has west on the left, east on the right.
    ax.add_patch(Rectangle((0,0),W,H,facecolor='#f0f1ef',edgecolor=COL['ink'],lw=1))
    for op in base['parameters']['openings']:
        if op['side']!='south':continue
        ox=W-op['offset']-op['width'];zz=48 if op['type']=='window' else 0;hh=24 if op['type']=='window' else 80
        ax.add_patch(Rectangle((ox,zz),op['width'],hh,facecolor='white',edgecolor=COL['muted'],lw=.6))
    # Roof silhouette and true fold positions; minimal fill, drafting line weights.
    ax.add_patch(Polygon([(0,z(0,YS)),(W,z(W,YS)),(W-36,z(W-36,L)),(0,z(0,L))],closed=True,facecolor='#edf1f2',edgecolor=COL['ink'],lw=1.3))
    if kind=='A':line(ax,[(0,z(0,YB)),(xhip(YB),z(0,YB)),(W,z(W,YS))],lw=1)
    else:line(ax,[(W,z(W,YS)),(W-36,z(0,L))],lw=1.1)
    line(ax,[(-RUN,0),(-RUN,B),(0,z(0,L))],lw=1.4)
    line(ax,[(-RUN,B),(0,z(0,YS))],lw=.7)
    for t in [.25,.5,.75]:line(ax,[(-RUN+t*RUN,B+t*(z(0,YS)-B)),(-RUN+t*RUN,B+t*(z(0,L)-B))],lw=.6,color=COL['muted'])
    line(ax,[(0,H),(W,H),(W,B),(0,B),(0,H)],color=COL['timber'],lw=1.3)
    for post in frame:
        if post['post'] and post['y']<0:
            xx=-RUN if post['x']>300 else W-post['x']-post['width']/2
            ax.add_patch(Rectangle((xx-3,0),6,H,facecolor='#e6d9c9',edgecolor=COL['timber'],lw=.7))
    line(ax,[(-RUN,H),(W-40,H),(W-40,B),(-RUN,B)],color=COL['timber'],lw=1)
    datum(ax,-80,W+30,F,'');text(ax,W/2,H-13,f'Loft floor {ft(F)}¹',fontsize=9,color=COL['muted'])
    dimy(ax,0,z(0,L),W+53,W-36,ft(z(0,L))+' roof top')
    dimx(ax,-RUN,0,-25,0,'5′ 0″²');dimx(ax,W-36,W,z(0,L)+24,z(0,L),'3′ 0″ max')
    text(ax,110,z(0,YS)+36,'30° south-facing roof',fontsize=10)
    text(ax,W-5,z(0,L)-33,f'{math.degrees(math.atan(k)):.1f}° east',ha='left',rotation=90,fontsize=9)
    # West elevation. North is left and south is right for a viewer facing east.
    ax=axes[1,1];setup(ax,'04  West elevation · looking east',(-85,L+75),(-68,310))
    ax.add_patch(Rectangle((L-LG,0),LG,H,facecolor='#f0f1ef',edgecolor=COL['ink'],lw=1))
    for op in base['parameters']['openings']:
        if op['side']=='west':ax.add_patch(Rectangle((L-op['offset']-op['width'],48),op['width'],24,facecolor='white',edgecolor=COL['muted'],lw=.6))
    prof=[(L-y,z(0,y)) for y in ylist];under=[(L-y,z(0,y)-T) for y in ylist]
    ax.add_patch(Polygon([(0,B),(L-YS,B)]+prof,closed=True,facecolor='#f2f1ed',edgecolor='none'))
    for yy in np.arange(YS,L+.01,p['lattice_spacing_assumed']):line(ax,[(L-yy,B),(L-yy,z(0,yy))],lw=.32,color='#b0a394')
    line(ax,prof,lw=1.7);line(ax,under,lw=.8,color=COL['muted'],ls=(0,(4,3)))
    line(ax,[(0,B),(0,z(0,L))],lw=1.2)
    line(ax,[(0,H),(L,H),(L,B),(0,B)],lw=1.3,color=COL['timber'])
    for post in frame:
        if post['post'] and post['x']>300:
            xx=L-post['y']-post['height']/2
            ax.add_patch(Rectangle((xx-3,0),6,H,facecolor='#e6d9c9',edgecolor=COL['timber'],lw=.7))
    line(ax,[(0,H),(L-YS,H),(L-YS,B),(0,B)],color=COL['timber'],lw=1)
    datum(ax,-18,L+18,F,'');text(ax,L/2,H-13,f'Loft floor {ft(F)}¹',fontsize=9,color=COL['muted'])
    dimy(ax,F,F+h(L),-32,0,ft(h(L))+' clear')
    dimy(ax,0,z(0,L),-66,0,ft(z(0,L))+' roof top')
    dimy(ax,0,z(0,YS),L+52,L-YS,ft(z(0,YS))+' south eave')
    line(ax,[(L-LG,H),(L-LG,F)],lw=.8,color=COL['dim'],ls=(0,(4,3)))
    ax.annotate('6″ north extension',xy=(3,H),xytext=(-20,65),fontsize=8,color=COL['dim'],ha='right',arrowprops={'arrowstyle':'-','color':COL['dim'],'lw':.6})
    line(ax,[(L,F),(L,z(0,0))],lw=.8,ls=(0,(4,3)),color=COL['dim'])
    dimx(ax,L,L-YS,-24,0,ft(-YS))
    # Clearance contours describe the central loft, excluding the east hip.
    for clear,yy,offset in [(96,(96-HS)/M,0),(72,(72-HS)/M,-18)]:
        xx=L-yy
        line(ax,[(0,F+clear),(xx,F+clear)],color=COL['head'],lw=1,ls=(0,(5,3)))
        ax.annotate('',(xx,F),(xx,F+clear),arrowprops={'arrowstyle':'|-|','color':COL['head'],'lw':.8})
        text(ax,xx+5,F+clear*.48,ft(clear)+' clear',rotation=90,fontsize=9,color=COL['head'])
    dimx(ax,0,L-(96-HS)/M,-23,0,ft(L-(96-HS)/M)+' at ≥8 ft');dimx(ax,0,L-(72-HS)/M,-47,0,ft(L-(72-HS)/M)+' at ≥6 ft')
    if kind=='A':text(ax,39,z(0,L)+15,'¼″/ft¹',fontsize=10);text(ax,78,z(0,YB)+18,ft(z(0,YB)),fontsize=9,ha='left')
    else:text(ax,60,z(0,L)-10,'30°',fontsize=12,rotation=-30)
    text(ax,175,z(0,85)+20,'30°',fontsize=12,rotation=-30)
    text(ax,0,-61,'NORTH / GARAGE DOOR',ha='left',fontsize=8,va='top');text(ax,L,-61,'SOUTH',ha='right',fontsize=8,va='top')
    lattice_angle=math.degrees(math.atan((z(0,L)-B)/RUN))
    notes=[f'¹ ASSUMED BUILDUP: {ft(H)} wall + 8″ beam + ¾″ deck → {ft(F)} loft floor. Roof depth shown as 8″ vertical; not sized.',
           f'² WEST: 5′ 0″ from wall to outboard post centerline. Lattice 2×2 at 7″ centers; pitch increases northward to {lattice_angle:.1f}°.',
           'Headroom depths apply to the central roof area; the east hip reduces usable width. Roof/loft supports and solar modules are conceptual.',
           f'Roof follows beams: south {ft(-YS)} beyond wall; north roof + loft wall 6″ beyond existing wall. Loads and clearances remain unresolved.']
    for i,n in enumerate(notes):fig.text(.045,.088-i*.018,n,fontsize=9.5,color=COL['muted'])
    fig.savefig(ROOT/f'option-{kind.lower()}-four-views.png',dpi=180,facecolor='white')
    fig.savefig(ROOT/f'option-{kind.lower()}-four-views.svg',facecolor='white')
    pdf.savefig(fig,facecolor='white');plt.close(fig)
    return {'option':kind,'floor_datum':F,'existing_north_wall_y':LG,'north_roof_and_loft_wall_y':L,'north_extension':L-LG,'roof_run_north_south':L-YS,'south_roof_start_y':YS,'south_roof_underside':z(0,YS)-T,'south_roof_top':z(0,YS),'roof_top_at_south_wall':z(0,0),'north_roof_top':z(0,L),'north_headroom':h(L),'break_headroom':h(YB),'east_pitch_degrees':math.degrees(math.atan(k)),'west_lattice_max_pitch_degrees':lattice_angle,'depth_at_8ft':L-(96-HS)/M,'depth_at_6ft':L-(72-HS)/M,'solar_surface_gross_sqft':sum((b-a)*((xhip(a)+xhip(b))/2)/math.cos(math.radians(30))/144 for a,b in zip(ylist,ylist[1:]) if kind=='B' or a==YS)}

with PdfPages(ROOT/'roof-options-four-views.pdf') as pdf:
    summary=[sheet(kind,pdf) for kind in ['A','B']]
(ROOT/'measurements.json').write_text(json.dumps(summary,indent=2))
assert summary[0]['break_headroom']>=p['headroom_at_roof_break_minimum']
assert abs(summary[0]['south_roof_underside']-B)<1e-9
assert abs(summary[1]['north_headroom']-(HB+78*M))<1e-9
assert all(v['depth_at_6ft']>119 for v in summary)
print(json.dumps(summary,indent=2))
