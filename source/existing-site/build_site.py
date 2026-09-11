"""Photo-informed existing conditions. All geometry in metres, X east/Y north/Z up."""
from pathlib import Path
import json, math, random, struct, re
R=Path(__file__).resolve().parent
random.seed(4198)
P=[]
C={'ground':'b3a18a','paving':'626e72','joints':'c4c3b8','planting':'8b8965','wood':'997959','metal':'394648','wall':'d9d5c3','roof':'828889','glass':'435f66','house':'8c9faa','white':'eeeae0','silver':'c3cbce','leaf':'627854','red':'784957','pot':'244c88'}
def add(name,group,v,f,c):
 t=[]
 for face in f:
  for i in range(1,len(face)-1):t.append([face[0],face[i],face[i+1]])
 color=C.get(c,c)
 P.append(dict(name=name,group=group,vertices=v,triangles=t,color=[int(color[i:i+2],16)/255 for i in (0,2,4)]))
 return P[-1]
def box(name,g,x,y,z,w,d,h,c):
 v=[[x+dx*w,y+dy*d,z+dz*h] for dz in [0,1] for dy in [0,1] for dx in [0,1]]
 return add(name,g,v,[[0,2,3,1],[4,5,7,6],[0,1,5,4],[1,3,7,5],[3,2,6,7],[2,0,4,6]],c)
def ellipsoid(name,g,x,y,z,rx,ry,rz,c,n=12,m=7):
 v=[[x+rx*math.sin(math.pi*j/m)*math.cos(i*math.tau/n),y+ry*math.sin(math.pi*j/m)*math.sin(i*math.tau/n),z+rz*math.cos(math.pi*j/m)] for j in range(m+1) for i in range(n)]
 f=[[j*n+i,j*n+(i+1)%n,(j+1)*n+(i+1)%n,(j+1)*n+i] for j in range(m) for i in range(n)]
 return add(name,g,v,f,c)
def rod(name,g,a,b,r,c,n=8):
 import numpy as np
 a,b=np.array(a),np.array(b);d=b-a;d=d/np.linalg.norm(d);u=np.cross(d,[0,0,1] if abs(d[2])<.9 else [0,1,0]);u=u/np.linalg.norm(u);w=np.cross(d,u)
 v=[(p+r*(u*math.cos(i*math.tau/n)+w*math.sin(i*math.tau/n))).tolist() for p in [a,b] for i in range(n)]
 return add(name,g,v,[list(reversed(range(n))),list(range(n,2*n))]+[[i,(i+1)%n,(i+1)%n+n,i+n] for i in range(n)],c)
def polygon(name,g,xy,z,color):
 # Ear clipping for concave plan outlines.
 area=sum(xy[i][0]*xy[(i+1)%len(xy)][1]-xy[(i+1)%len(xy)][0]*xy[i][1] for i in range(len(xy)))
 if area<0:xy=list(reversed(xy))
 ids=list(range(len(xy)));f=[]
 def cross(a,b,c):return (b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0])
 while len(ids)>3:
  for k in range(len(ids)):
   a,b,c=[ids[j%len(ids)] for j in [k-1,k,k+1]]
   if cross(xy[a],xy[b],xy[c])<=1e-8:continue
   if any(all(cross(xy[u],xy[v],xy[p])>=-1e-8 for u,v in [(a,b),(b,c),(c,a)]) for p in ids if p not in [a,b,c]):continue
   f.append([a,b,c]);ids.pop(k);break
  else:raise ValueError('Non-simple polygon '+name)
 f.append(ids)
 return add(name,g,[[x,y,z] for x,y in xy],f,color)
def walk(name,pts,width):
 for i,(a,b) in enumerate(zip(pts,pts[1:])):
  dx,dy=b[0]-a[0],b[1]-a[1];l=math.hypot(dx,dy);nx,ny=-dy/l*width/2,dx/l*width/2
  polygon(name+str(i),'paths',[(a[0]+nx,a[1]+ny),(a[0]-nx,a[1]-ny),(b[0]-nx,b[1]-ny),(b[0]+nx,b[1]+ny)],.025,'paving')
  # Irregular cross joints make the flagstone routing legible.
  for j in range(int(l/.45)):
   t=(j+.5)*.45/l;x=a[0]+dx*t;y=a[1]+dy*t
   rod('Flagstone joint','details',(x+nx,y+ny,.031),(x-nx+dx/l*.12,y-ny+dy/l*.12,.031),.012,'joints',4)
def hip(name,g,x,y,w,d,z,rise,c):
 return add(name,g,[[x,y,z],[x+w,y,z],[x+w,y+d,z],[x,y+d,z],[x+w*.5,y+d*.45,z+rise],[x+w*.5,y+d*.55,z+rise]],[[0,1,4],[1,2,5,4],[2,3,5],[3,0,4,5]],c)
# Preserve the measured existing garage, excluding all proposal objects.
source=json.loads((R.parent/'model/scene.json').read_text())
for part in source['parts']:
 if part['group']=='proposal':continue
 q=dict(part);q['vertices']=[[x*.0254 for x in v] for v in q['vertices']];q['group']='garage_roof' if part['group']=='roof' else 'garage'
 h=C['roof' if part['group']=='roof' else 'glass' if 'confirmed sill' in part['name'] else 'wood' if 'assumed height' in part['name'] else 'wall']
 q['color']=[int(h[i:i+2],16)/255 for i in (0,2,4)];P.append(q)
W,L=6.3373,6.3246
sx,sy=W/299,L/310
xy=lambda u,v:((u-519)*sx,(411-v)*sy)
box('Approximate backyard extent','ground',-8.63,-16.55,-.14,15.28,24.92,.12,'ground')
box('Rear alley context','context',-9.2,8.38,-.12,16.5,2.6,.1,'paving')
box('Garage driveway apron','paths',0,L,0,W,2.04,.035,'joints')
box('Rear work patio','paths',-8.63,4.50,0,8.63,3.87,.035,'joints')
box('Trailer brick parking pad','paths',-8.3,-1.15,.005,2.95,6.3,.04,'947e6d')
for y in [i*.35-1.1 for i in range(18)]:rod('Brick joint','details',(-8.3,y,.051),(-5.35,y,.051),.009,'joints',4)
# West shelter: user correction aligns its north end with the garage north end.
shelter_start=len(P)
shelter_south=L-1.905
box('Work shelter slab','paths',-4.43,0,0,4.43,1.905,.05,'paving')
for x in [-4.43,-.16]:box('Shelter front upright','shelter',x,0,.05,.15,.15,2.25,'metal')
box('Electrical pillar - footprint from study','shelter',-4.426,0,0,.254,1.219,2.25,'wall')
box('Shelter timber front header','shelter',-4.43,-.035,2.12,4.43,.15,.40,'wood')
box('Shelter back screen','shelter',-4.43,1.82,.05,4.43,.08,1.95,'wood')
box('Workbench','shelter',-.686,0,.85,.686,1.905,.09,'wood')
box('Work counter','shelter',-4.1,1.25,.83,3.05,.56,.07,'wood')
# Thin pitched roof and visible corrugation, rather than speculative proposal framing.
add('Existing shallow shelter roof','shelter_roof',[[-4.68,-.254,2.57],[0,-.254,2.57],[0,1.905,2.72],[-4.68,1.905,2.72]],[[0,1,2,3]],'6d7b77')
for i in range(32):
 x=-4.65+i*.145;rod('Shelter roof rib','shelter_roof',(x,-.254,2.58),(x,1.905,2.73),.012,'metal',4)
# Move the complete shelter, including slab, pillar, counter and roof as one assembly.
for part in P[shelter_start:]:
 part['vertices']=[[x,y+shelter_south,z] for x,y,z in part['vertices']]
# Airstream: schematic-calibrated envelope, generic rounded body, not a specific trim.
ellipsoid('Airstream rounded aluminum body','trailer',-7.02,1.35,1.48,1.16,2.30,1.12,'silver',24,12)
box('Airstream straight lower skirt','trailer',-8.06,-.24,.64,2.08,3.15,.70,'silver')
for x in [-8.16,-5.88]:
 for y in [.25,1.1]:rod('Trailer wheel','trailer',(x-.07,y,.40),(x+.07,y,.40),.34,'metal',16)
for y in [-.1,1.2,2.35]:
 box('Trailer side window','trailer',-5.90,y,1.43,.028,.57,.46,'glass')
 box('Trailer opposite window','trailer',-8.17,y,1.43,.028,.57,.46,'glass')
for a in [-7.8,-6.24]:rod('Trailer A-frame tongue','trailer',(a,3.35,.49),(-7.02,4.55,.43),.045,'metal')
box('Trailer roof vent','trailer',-7.3,.9,2.55,.56,.55,.16,'white')
# Green areas in schematic are planting/gravel, not confirmed lawn.
outline=[xy(u,v) for u,v in [(421,446),(665,446),(665,973),(650,978),(633,1000),(600,1010),(529,1016),(493,1008),(477,994),(468,975),(468,762),(421,762)]]
def oval(cx,cy,rx,ry):return [(cx+rx*math.cos(i*math.tau/40),cy+ry*math.sin(i*math.tau/40)) for i in range(40)]
polygon('South low garden rounded bed','beds',oval(.65,-10.10,2.05,2.80),.012,'98927b')
polygon('North jungle wood-chip clearing','beds',oval(.45,-4.08,2.15,2.95),.012,'ac8968')
patio=[xy(u,v) for u,v in [(173,762),(468,762),(468,975),(477,994),(493,1008),(529,1016),(600,1010),(633,1000),(650,978),(680,966),(744,958),(817,966),(817,1097),(579,1095),(577,1164),(528,1164),(477,1120),(430,1168),(363,1168),(363,1055),(176,1056)]]
polygon('House flagstone patio','paths',patio,.021,'paving')
walk('East access path',[(3.54,-11.8),(3.50,-8),(3.43,-4),(3.45,-1),(3.45,-.5)],.86)
walk('Curving garden flagstone',[(-2.20,-7.35),(-2.25,-6.6),(-2.15,-4.4),(-1.5,-2.4),(-.7,-.5),(1.25,-.5),(3.45,-.5)],1.0)
walk('Work shelter access',[(-1.5,-2.4),(-.8,-1),(-.8,4.65),(-2.3,4.65)],.95)
# One planted fence line divides north and south rooms, with a central walk-through.
# Gap -2.85..-1.50 aligns to the existing curving flagstone path.
for lo,hi in [(-8.40,-2.85),(-1.50,2.70)]:
 count=math.ceil((hi-lo)/1.4)
 for i in range(count+1):
  x=lo+(hi-lo)*i/count
  box('Room dividing fence post','garden_fence',x-.045,-7.20,0,.09,.09,1.20,'wood')
 for z in [.20,1.08]:box('Room dividing fence rail','garden_fence',lo,-7.22,z,hi-lo,.075,.09,'wood')
 for i in range(math.ceil((hi-lo)/.20)):
  x=lo+i*.20
  rod('Room fence lattice','garden_fence',(x,-7.20,.27),(min(x+.45,hi),-7.20,1.06),.017,'wood',4)
  rod('Room fence lattice','garden_fence',(x,-7.18,1.06),(min(x+.45,hi),-7.18,.27),.017,'wood',4)
 for i in range(int((hi-lo)/.42)):
  x=lo+.24+i*.42
  ellipsoid('Plants on room dividing fence','planting',x,-7.18,1.08,.24,.23,.34,'60754e',9,5)
for u,v in [(315,205),(317,264)]:
 x,y=xy(u,v+41);box('Rectangular planting bed','beds',x,y,.02,2.44,.84,.20,'wood');box('Bed soil','beds',x+.08,y+.08,.22,2.28,.68,.015,'planting')
# Approximate boundary fences, separated from legal property information.
for x in [-8.63,6.65]:
 box('Approximate boundary fence','boundary',x,-16.55,0,.07,24.9,1.75,'wood')
 for y in range(-16,9,2):box('Boundary post','boundary',x-.04,y,0,.15,.15,1.85,'wood')
# Existing house north outline follows the lower edge of backyard 2023.png.
# The triangular indentation in the patio is the bay projecting north from the house.
west_x,west_y=xy(176,1056);step_x,central_y=xy(363,1168)
east_x,east_y=xy(579,1095);end_x,_=xy(817,1097)
box('House west projecting wing','house',west_x,-21.3,0,step_x-west_x,west_y+21.3,3.35,'house')
box('House recessed central wing','house',step_x,-21.3,0,east_x-step_x,central_y+21.3,3.35,'house')
box('House east projecting wing','house',east_x,-21.3,0,end_x-east_x,east_y+21.3,3.35,'house')
box('House two storey east portion','house',3.35,-21.3,3.35,end_x-3.35,east_y+21.3,2.85,'house')
hip('West house hip roof','house_roof',west_x-.08,-21.4,step_x-west_x+.16,west_y+21.5,3.35,.65,'555d60')
hip('Central house hip roof','house_roof',step_x-.08,-21.4,east_x-step_x+.16,central_y+21.5,3.35,.70,'555d60')
hip('East lower hip roof','house_roof',east_x-.08,-21.4,3.43-east_x,east_y+21.5,3.35,.65,'555d60')
box('Upper house shallow roof','house_roof',3.27,-21.4,6.2,end_x-3.19,east_y+21.5,.16,'555d60')
bay=[xy(430,1168),xy(477,1120),xy(528,1164)]
bv=[[x,y,z] for z in [0,3.5] for x,y in bay]
add('Triangular north-facing bay','house',bv,[[0,2,1],[3,4,5],[0,1,4,3],[1,2,5,4],[2,0,3,5]],'house')
polygon('Triangular bay roof cap','house_roof',bay,3.52,'555d60')
def opening(name,x,y,z,w,h,door=False):
 box(name+' trim','house',x-.08,y,z-.08,w+.16,.09,h+.16,'white');box(name,'house',x,y+.095,z,w,.025,h,'glass')
 for t in ([.25,.5,.75] if door else [.5]):box(name+' sash','house',x,y+.125,z+h*t,w,.025,.035,'white')
 if door:box(name+' vertical','house',x+w*.5,y+.13,z,.035,.025,h,'white')
for x in [-2.95,.35]:
 opening('Rear French door',x,central_y+.015,.16,.70,2.12,True);box('Rear door step','details',x-.1,central_y+.25,0,.9,.50,.16,'paving')
# Window planes and trim align to both angled faces of the triangular bay.
for i,(a,b) in enumerate(zip(bay,bay[1:])):
 dx,dy=b[0]-a[0],b[1]-a[1];length=math.hypot(dx,dy);nx,ny=-dy/length,dx/length
 if ny<0:nx,ny=-nx,-ny
 def facept(t,z,off=.02):return [a[0]+dx*t+nx*off,a[1]+dy*t+ny*off,z]
 add('Angled bay window '+str(i+1),'house',[facept(.12,.8),facept(.88,.8),facept(.88,2.5),facept(.12,2.5)],[[0,1,2,3]],'glass')
 for z in [.75,1.65,2.55]:rod('White bay sash','house',facept(.08,z,.04),facept(.92,z,.04),.035,'white',4)
 for t in [.08,.92]:rod('White bay jamb','house',facept(t,.75,.04),facept(t,2.55,.04),.045,'white',4)
opening('West rear sash',-5.9,west_y+.015,.85,1.1,1.5)
opening('East paired lower window',4.05,east_y+.015,1.05,1.4,1.0)
opening('East paired upper window',4.05,east_y+.015,4.55,1.4,1.1)
# User correction: pergola stops 8 ft north of the dividing fence.
fence_y=-7.20
pergola={'west':2.70,'east':4.27,'south':fence_y+8*.3048,'north':-.45,'beam_underside':2.35}
ps,pn=pergola['south'],pergola['north']
post_rows=[ps+.12,(ps+pn)/2,pn-.12]
for x in [pergola['west'],pergola['east']]:
 for y in post_rows:
  box('White pergola post','pergola',x-.065,y-.065,0,.13,.13,2.57,'white')
 box('White pergola longitudinal beam','pergola',x-.06,ps,2.35,.12,pn-ps,.22,'white')
for i in range(15):
 y=ps+i*(pn-ps-.07)/14
 box('White pergola overhead slat','pergola_roof',2.48,y,2.57,2.01,.07,.13,'white')
# Planting along the remaining north access route; no former path corridor through the south garden.
for x0,x1 in [(1.95,3.0),(3.98,5.45)]:
 box('North access side planting soil','beds',x0,-7.0,.015,x1-x0,6.55,.018,'planting')
 for i in range(11):
  y=-6.75+i*.59;x=random.uniform(x0+.22,x1-.22)
  ellipsoid('North access side shrub','planting',x,y,.62,.38,.50,.68,['607651','7d8d66','576f4e'][i%3],10,6)
for x in [2.70,4.27]:
 for y in post_rows:
  for z in [.8,1.55,2.25]:ellipsoid('Pergola climbing vine','planting',x,y,z,.26,.12,.48,'577248',8,5)
 for i in range(7):
  y=ps+.35+i*(pn-ps-.70)/6
  ellipsoid('Pergola overhead vines','pergola_foliage',x,y,2.80,.50,.34,.26,'62784f',10,5)
for i in range(5):
 y=ps+.35+i*(pn-ps-.70)/4
 ellipsoid('Pergola canopy crossing','pergola_foliage',3.48,y,2.82,.50,.34,.20,'6f8156',10,5)
# Trees have separate trunks and canopies; species and heights not established.
trees=[('T1 west garden tree',-4.67,-2.12,3.7,1.05),('Camellia - jungle',-.70,-2.25,2.5,.85),('Lime tree - south of fence',2.10,-7.75,2.8,.8),('Very small central south tree',.90,-10.45,1.25,.38),('T6 west boundary tree',-7.65,-9.38,8.5,3.05)]
for name,x,y,h,r in trees:
 rod(name+' estimated trunk','trunks',(x,y,0),(x+.08,y,h*.70),.09 if h<6 else .23,'wood')
 for i in range(4):
  a=i*2.4;dx,dy=math.cos(a)*r*.4,math.sin(a)*r*.4
  rod(name+' branch','trunks',(x,y,h*.43),(x+dx,y+dy,h*.78),.035,'wood')
  ellipsoid(name+' canopy','canopy',x+dx,y+dy,h*.79,r*.75,r*.75,h*.20,['72865e','607651','7d8d66','576f4e'][i])
# Overhanging east foliage visible in IMG_4201; approximate supporting trunk location.
rod('East mature tree trunk','trunks',(6.35,-1.5,0),(6.6,-1.4,8.7),.24,'wood')
ellipsoid('East overhanging canopy','canopy',6.6,-1.3,7.7,2.5,3.0,2.1,'60744f')
# Low south garden: continuous low planting and a small tree; no internal path.
for i in range(110):
 x,y=random.uniform(-1.35,2.65),random.uniform(-12.85,-7.4)
 if ((x-.65)/1.90)**2+((y+10.10)/2.60)**2>1:continue
 h=random.uniform(.18,.38)
 ellipsoid('South garden low bush','planting',x,y,h,.30+random.random()*.12,.36,h,['8b9670','7d8864','75835f'][i%3],9,5)
# Jungle planting is concentrated at the perimeter, leaving the middle open.
for i in range(17):
 a=i*math.tau/17;x=.45+1.80*math.cos(a);y=-4.08+2.60*math.sin(a)
 if -.6<x<1.4 and y<-6.0:continue
 ellipsoid('Jungle perimeter shrub','planting',x,y,.43,.40,.42,.43,'leaf',9,5)
# A sparse chip texture on the unobstructed central clearing.
for i in range(170):
 x,y=random.uniform(-.7,1.5),random.uniform(-5.8,-2.7)
 if ((x-.4)/1.1)**2+((y+4.25)/1.55)**2>1:continue
 box('Jungle wood chip','details',x,y,.016,.035,.075,.008,['987651','b49470','826b54'][i%3])
for x in [-8.15,6.15]:
 for y in range(-14,6,2):ellipsoid('Boundary climbing greenery','planting',x,y,1.20,.50,.95,.9,'5f7350',8,5)
for x,y in [(1.9,-2.7),(2.0,-5.6),(-1.25,-4.8)]:
 for i in range(16):
  a=i*2.4;ln=random.uniform(.8,1.5);dx,dy=math.cos(a),math.sin(a)
  add('Burgundy strap leaf','planting',[[x-.055*dy,y+.055*dx,.1],[x+.055*dy,y-.055*dx,.1],[x+.35*dx,y+.35*dy,ln],[x+dx*.85,y+dy*.85,ln*.7]],[[0,1,2],[1,3,2]],'red')
for x,y in [(-.4,-.8),(2,-.7),(-3.0,-1.7),(-3.6,-15),(.9,-15),(4.4,-2.5)]:
 rod('Cobalt garden pot','details',(x,y,.03),(x,y,.5),.23,'pot',12);ellipsoid('Potted plant','planting',x,y,.8,.3,.3,.45,'leaf',8,5)
# Conversation room north of the patio fence and south of the Airstream.
polygon('Conversation area wood-chip surface','beds',[(-7.95,-6.97),(-3.00,-6.97),(-3.00,-2.75),(-7.95,-2.75)],.014,'a18b70')
def bench(name,cx,cy,angle,length=1.55,stone=False):
 start=len(P);mat='a9a598' if stone else 'wood'
 if stone:
  box(name+' seat','seating',-length/2,-.23,.43,length,.46,.09,mat)
  for x in [-length*.34,length*.34]:box(name+' pedestal','seating',x-.10,-.15,0,.20,.30,.43,mat)
 else:
  for x in [-length*.40,length*.40]:
   for y in [-.19,.19]:box(name+' metal leg','seating',x-.025,y-.025,0,.05,.05,.45,'metal')
   rod(name+' back support','seating',(x,.24,.10),(x,.24,.95),.025,'metal')
  for i in range(5):box(name+' timber seat slat','seating',-length/2,-.23+i*.10,.45,length,.08,.045,'wood')
  for i in range(3):box(name+' back slat','seating',-length/2,.22,.65+i*.13,length,.045,.08,'wood')
  for x in [-length/2,length/2]:rod(name+' arm','seating',(x,-.22,.68),(x,.24,.68),.025,'metal')
 for part in P[start:]:
  part['vertices']=[[cx+x*math.cos(angle)-y*math.sin(angle),cy+x*math.sin(angle)+y*math.cos(angle),z] for x,y,z in part['vertices']]
bench('Conversation east bench',-3.55,-5.05,-math.pi/2)
bench('Conversation west bench',-7.1,-4.80,math.pi/2)
bench('Conversation south bench',-5.3,-6.40,math.pi)
bench('Conversation chair',-6.75,-6.15,2.45,.62)
# Open cylindrical metal fire pit with a recessed dark interior; no active fire.
fx,fy=-5.25,-4.75
v=[]
for radius,z in [(.43,.06),(.43,.53),(.37,.53),(.37,.12)]:
 for i in range(24):v.append([fx+radius*math.cos(i*math.tau/24),fy+radius*math.sin(i*math.tau/24),z])
f=[]
for j in range(3):
 for i in range(24):f.append([j*24+i,j*24+(i+1)%24,(j+1)*24+(i+1)%24,(j+1)*24+i])
add('Conversation central metal fire pit','fire_pit',v,f,'66605a')
rod('Fire pit interior','fire_pit',(fx,fy,.105),(fx,fy,.12),.37,'302f2b',24)
rod('Fire pit log','fire_pit',(fx-.20,fy-.14,.17),(fx+.23,fy+.10,.28),.075,'wood')
rod('Fire pit log','fire_pit',(fx-.16,fy+.20,.17),(fx+.10,fy-.20,.30),.065,'wood')
# Low stone/mosaic-style benches visible along patio edges; pool intentionally omitted.
bench('Rear patio north stone bench',-5.5,-7.62,0,1.35,True)
bench('Rear patio west stone bench',-7.1,-10.75,math.pi/2,1.5,True)
for x,y in [(-7.3,-7.65),(-3.35,-7.7),(-7.0,-12.0)]:
 rod('Patio edge blue pot','details',(x,y,.03),(x,y,.48),.23,'pot',12)
 ellipsoid('Patio edge potted foliage','planting',x,y,.68,.34,.34,.35,'leaf',9,5)
box('Patio table','details',4.1,-12.6,.74,1.45,.8,.07,'wood')
for x in [4.2,5.4]:
 for y in [-12.5,-12.0]:box('Table leg','details',x,y,0,.07,.07,.74,'wood')
# Machine-readable model and standard Z-up OBJ.
data={'units':'metres','coordinates':'X east, Y north, Z up; garage southwest outside corner = origin','parts':P}
(R/'site-scene.json').write_text(json.dumps(data,separators=(',',':')))
lines=['# Existing backyard; metres; X east Y north Z up','mtllib existing-backyard.mtl'];mtl=[];offset=1
for i,p in enumerate(P):
 name=re.sub(r'[^a-zA-Z0-9_-]','_',p['name'])+'_'+str(i);lines+=['o '+name,'usemtl m'+str(i)]
 lines+=['v '+' '.join(f'{x:.6f}' for x in v) for v in p['vertices']];lines+=['f '+' '.join(str(x+offset) for x in t) for t in p['triangles']];offset+=len(p['vertices'])
 mtl+=['newmtl m'+str(i),'Kd '+' '.join(str(x) for x in p['color']),'Ka 0.2 0.2 0.2']
(R/'existing-backyard.obj').write_text('\n'.join(lines));(R/'existing-backyard.mtl').write_text('\n'.join(mtl))
# Self-contained GLB. Root rotates source Z-up to glTF Y-up, preserving object coordinates.
binary=bytearray();views=[];access=[];meshes=[];nodes=[];materials=[]
def buf(vals,fmt,ctype,typ,count,mins=None,maxs=None):
 while len(binary)%4:binary.append(0)
 start=len(binary);binary.extend(struct.pack('<'+fmt*len(vals),*vals));vi=len(views);views.append({'buffer':0,'byteOffset':start,'byteLength':len(binary)-start});a={'bufferView':vi,'componentType':ctype,'count':count,'type':typ}
 if mins is not None:a.update(min=mins,max=maxs)
 access.append(a);return len(access)-1
for i,p in enumerate(P):
 v=p['vertices'];pos=buf([x for q in v for x in q],'f',5126,'VEC3',len(v),[min(q[j] for q in v) for j in range(3)],[max(q[j] for q in v) for j in range(3)])
 idx=buf([x for t in p['triangles'] for x in t],'I',5125,'SCALAR',len(p['triangles'])*3)
 materials.append({'name':p['name'],'pbrMetallicRoughness':{'baseColorFactor':p['color']+[1],'metallicFactor':.6 if p['group']=='trailer' else 0,'roughnessFactor':.65},'doubleSided':True})
 meshes.append({'name':p['name'],'primitives':[{'attributes':{'POSITION':pos},'indices':idx,'material':i}]});nodes.append({'name':p['name'],'mesh':i,'extras':{'group':p['group']}})
nodes.append({'name':'Existing backyard — metres','rotation':[-math.sqrt(.5),0,0,math.sqrt(.5)],'children':list(range(len(P)))})
gltf={'asset':{'version':'2.0','generator':'Photo-informed existing-site build_site.py'},'scene':0,'scenes':[{'nodes':[len(P)]}],'nodes':nodes,'meshes':meshes,'materials':materials,'buffers':[{'byteLength':len(binary)}],'bufferViews':views,'accessors':access}
j=json.dumps(gltf,separators=(',',':')).encode();j+=b' '*((-len(j))%4);binary+=b'\x00'*((-len(binary))%4)
(R/'existing-backyard.glb').write_bytes(struct.pack('<III',0x46546c67,2,12+8+len(j)+8+len(binary))+struct.pack('<II',len(j),0x4e4f534a)+j+struct.pack('<II',len(binary),0x004e4942)+binary)
# The established project's offline canvas viewer, adapted to whole-site geometry.
f=(R.parent/'model/viewer-fragment.html').read_text()
f=f.replace('GARAGE_SCENE_DATA',json.dumps({'parameters':{'width':W,'length':L,'wall_height':2.5019,'roof_rise':1.524,'overhang':0},'parts':P},separators=(',',':')))
f=f.replace('Plan · south up','Plan · north up').replace('Proposed structure','Tree canopies').replace('Doors / glazing','Planting').replace('<span class="form-check-label">Roof</span>','<span class="form-check-label">Roofs</span>')
f=f.replace('id="garage-proposal"','id="garage-proposal" checked')
f=re.sub(r'    <label class="form-label">Roof rise.*?</label>\n','',f);f=re.sub(r'    <label class="form-label">Ridge length.*?</label>\n','',f)
f=f.replace('450px','640px').replace('350px','450px').replace('let az=2.3,el=.52','let az=.32,el=.90')
f=re.sub(r'function vertex\(v,g\).*?\nfunction draw', 'function vertex(v,g){return v;}\nfunction draw',f)
f=f.replace('center=[proposal?p.width*.36:p.width/2,p.length/2,65]','center=[-1,-5,1.3]').replace('Math.min(w/(proposal?620:460),h/410)','Math.min(w/29,h/35)').replace('1100','65')
a=f.index(' // Reference grid');b=f.index(' const tris=[];',a);f=f[:a]+f[b:]
f=f.replace("if(part.group==='roof'&&!get('roof').checked||part.group==='proposal'&&!proposal||part.group==='infill'&&!get('infill').checked)continue;","if((part.group.endsWith('_roof')||part.group==='pergola_foliage')&&!get('roof').checked||part.group==='canopy'&&!proposal||part.group==='planting'&&!get('infill').checked)continue;")
f=f.replace("part.group==='existing'?col.wall:col[part.group]","'#'+part.color.map(c=>Math.round(c*255).toString(16).padStart(2,'0')).join('')")
a=f.index(' // Roof perimeter');b=f.index("get('camera').onchange",a)
f=f[:a]+''' ctx.fillStyle=col.fg;ctx.font='12px system-ui';ctx.textAlign='left';ctx.fillText('Existing conditions · approximate site geometry · metres',12,h-12);
 if(mode==='top'){ctx.fillText('N ↑',w-45,24);}
}
'''+f[b:]
f=f.replace('orbit:[2.3,.52],top:[Math.PI,Math.PI/2]','orbit:[.32,.90],top:[0,Math.PI/2]')
f=re.sub(r"for\(const id of \['rise','ridge'\]\).*?\n",'',f)
f=f.replace('Drag to orbit · scroll to zoom · window sills 4 ft · windows 2 ft high · door heights assumed','Drag to orbit · scroll to zoom · hide tree canopies for the site layout. Yard geometry is estimated; garage uses the existing measured model.')
f=f.replace('Rotatable garage model with hip roof and short north–south ridge.','Rotatable existing backyard model with garage, shelter, trailer, paths and planting.')
(R/'site-viewer.html').write_text('<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Existing backyard</title><style>body{max-width:1300px;margin:24px auto;padding:0 22px;background:#f7f7f4;color:#263437;font:14px system-ui}button,select{font:inherit;padding:6px}h1{font-size:23px}</style></head><body><h1>Backyard · existing conditions</h1>'+f+'</body></html>')
assert not any(p['group']=='proposal' for p in P)
for p in P:
 assert all(math.isfinite(x) for v in p['vertices'] for x in v)
 assert all(0<=i<len(p['vertices']) for t in p['triangles'] for i in t)
(R/'validation.json').write_text(json.dumps({'objects':len(P),'triangles':sum(len(p['triangles']) for p in P),'finite_coordinates':True,'mesh_indices_valid':True,'proposal_objects':0,'garage_width_m':W,'garage_length_m':L,'site_dimensions':'estimated; not surveyed'},indent=2))
print('Built',len(P),'objects')
