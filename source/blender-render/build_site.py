import bpy, math, random
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parent
random.seed(41)
bpy.ops.wm.open_mainfile(filepath=str(R/'garage.blend'))
scene=bpy.context.scene
site=bpy.data.collections.new('Photo-informed site');scene.collection.children.link(site)
def move(o):
 for c in list(o.users_collection):c.objects.unlink(o)
 site.objects.link(o);return o
def rgb(h):
 cs=[int(h[i:i+2],16)/255 for i in (1,3,5)];return tuple(c/12.92 if c<=.04045 else ((c+.055)/1.055)**2.4 for c in cs)+(1,)
def mat(name,color,rough=.7):
 m=bpy.data.materials.new(name);m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=rgb(color);p.inputs['Roughness'].default_value=rough;return m
def texture(m,scale,depth):
 n=m.node_tree.nodes;l=m.node_tree.links;t=n.new('ShaderNodeTexNoise');t.inputs['Scale'].default_value=scale;t.inputs['Detail'].default_value=3;b=n.new('ShaderNodeBump');b.inputs['Strength'].default_value=.2;b.inputs['Distance'].default_value=depth;l.new(t.outputs['Fac'],b.inputs['Height']);l.new(b.outputs[0],n.get('Principled BSDF').inputs['Normal'])
def box(name,loc,dim,m,bev=.01):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=move(bpy.context.object);o.name=name;o.dimensions=dim;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.data.materials.append(m)
 if bev:b=o.modifiers.new('Rounded edges','BEVEL');b.width=bev;b.segments=2
 return o
def mesh(name,v,f,m):
 me=bpy.data.meshes.new(name);me.from_pydata(v,[],f);me.update();o=bpy.data.objects.new(name,me);site.objects.link(o);o.data.materials.append(m);return o
def rod(name,a,b,r,m):
 a,b=Vector(a),Vector(b);d=b-a;bpy.ops.mesh.primitive_cone_add(vertices=7,radius1=r,radius2=r*.7,depth=d.length,location=(a+b)/2);o=move(bpy.context.object);o.name=name;o.rotation_euler=d.to_track_quat('Z','Y').to_euler();o.data.materials.append(m);return o
soil=mat('Warm gravel and leaf litter','#8b7b62');texture(soil,170,.018)
cream=mat('Existing garage warm stucco','#d5d0be');texture(cream,160,.002)
blue=mat('House blue gray stucco','#859ba8');texture(blue,180,.002)
white=mat('Painted warm white trim','#ece9de',.4)
wood=mat('Weathered garden timber','#77624c');texture(wood,12,.015)
teak=mat('Bench honey wood','#ad7b42');texture(teak,32,.004)
metal=mat('Bench dark metal','#29302c',.35)
roof=mat('House charcoal shingles','#464947');texture(roof,90,.012)
stone=mat('Flagstone charcoal with pale joints','#666d6d');n=stone.node_tree.nodes;l=stone.node_tree.links
tex=n.new('ShaderNodeTexCoord');vor=n.new('ShaderNodeTexVoronoi');vor.feature='DISTANCE_TO_EDGE';vor.inputs['Scale'].default_value=2.7;l.new(tex.outputs['Object'],vor.inputs['Vector']);ramp=n.new('ShaderNodeValToRGB');ramp.color_ramp.elements[0].position=.018;ramp.color_ramp.elements[0].color=rgb('#aeb0a8');ramp.color_ramp.elements[1].position=.035;ramp.color_ramp.elements[1].color=rgb('#505a5e');l.new(vor.outputs['Distance'],ramp.inputs[0]);l.new(ramp.outputs[0],n.get('Principled BSDF').inputs['Base Color']);texture(stone,110,.007)
clay=mat('Cobalt glazed pots','#244b8d',.22);clay.node_tree.nodes.get('Principled BSDF').inputs['Coat Weight'].default_value=.35
bark=mat('Tree bark','#8b8879');texture(bark,17,.035)
greens=[mat('Leaf '+str(i),h,.72) for i,h in enumerate(['#586640','#778150','#354b32','#687748','#89906a','#485b37'])]
reds=[mat('Burgundy foliage '+str(i),h) for i,h in enumerate(['#673c45','#83505a','#975c58'])]
flower=mat('Lavender flowers','#a590b1')
# Source boolean-cut wall meshes inherited window/door materials. Restore opaque stucco.
for o in bpy.data.objects:
 if o.name in ['South window opening','West window 2 opening','North garage door opening'] or o.name=='East wall':
  o.data.materials.clear();o.data.materials.append(cream)
 if o.name.startswith('Electrical pillar'):o.data.materials.clear();o.data.materials.append(cream)
for o in list(bpy.data.objects):
 if o.name=='Presentation ground':bpy.data.objects.remove(o,do_unlink=True)
box('Garden gravel ground',(0,-6,-.16),(2000,2000,.22),soil,0)
# Paths laid out approximately from the views toward and away from the garage.
def path(name,points,width):
 v=[]
 for i,p in enumerate(points):
  d=Vector(points[min(i+1,len(points)-1)])-Vector(points[max(0,i-1)]);d.normalize();q=Vector((-d.y,d.x))
  for s in [-1,1]:v.append((p[0]+s*q.x*width/2,p[1]+s*q.y*width/2,-.025 if name=='Path to west shelter' else -.033))
 mesh(name,v,[(2*i,2*i+1,2*i+3,2*i+2) for i in range(len(points)-1)],stone)
path('Winding flagstone garden walk',[(2.9,-16),(2.7,-12),(1,-9),(-.4,-6),(-.9,-3),(-.6,-.8),(3.25,-.8),(3.25,.08)],1.12)
path('Path to west shelter',[(-.6,-1),(-2,-.3),(-2,2),(-2,5.8)],1.1)
box('House flagstone terrace',(0,-14.4,-.07),(11,3,.09),stone,0)
# Weathered timber boundary, mainly concealed by planting.
for x in [-6.4,7.3]:
 for i in range(94):box('Boundary fence board',(x,-15+i*.24,.86),(.075,.225,1.8),wood,.004)
 for y in range(-15,9,2):box('Fence post',(x,y,1),(.14,.14,2.05),wood)
# Blue-gray rear of house, estimated location and size from photographs.
box('House low rear wing',(-1.4,-18,1.7),(9.2,5.2,3.4),blue)
box('House tall rear wing',(5.1,-18.8,3.05),(3.8,6.8,6.1),blue)
box('Rear central projecting bay',(-.1,-15.6,1.75),(2.8,.8,3.5),blue)
def hip(name,x,y,w,d,z,rise):
 v=[(x-w/2,y-d/2,z),(x+w/2,y-d/2,z),(x+w/2,y+d/2,z),(x-w/2,y+d/2,z),(x-w*.25,y,z+rise),(x+w*.25,y,z+rise)]
 mesh(name,v,[(0,1,5,4),(1,2,5),(2,3,4,5),(3,0,4)],roof)
 box(name+' white fascia',(x,y+d/2,z-.05),(w,.14,.15),white)
hip('Low house hip roof',-1,-18,10.6,5.8,3.45,.9)
hip('Tall house roof',5.1,-18.8,4.3,7.2,6.15,1)
glass=mat('House window dark reflections','#344e55',.16);glass.node_tree.nodes.get('Principled BSDF').inputs['Metallic'].default_value=.45
# North-facing rear facade openings.
def opening(name,x,y,z,w,h,door=False):
 box(name+' white surround',(x,y,z),(w+.16,.13,h+.16),white)
 box(name+' glazing',(x,y+.075,z),(w,.03,h),glass,.002)
 box(name+' center sash',(x,y+.10,z),(w,.035,.045),white,.002)
 if door:
  for k in [-1,1]:box(name+' muntin',(x+k*w/6,y+.11,z),(.03,.03,h),white,.001)
  for k in [-1,1]:box(name+' horizontal light',(x,y+.11,z+k*h/3),(w,.03,.03),white,.001)
for x in [-4.5,2.1]:opening('French garden door',x,-15.32,1.14,.85,2.18,True)
opening('Projecting bay sash',-.1,-15.13,1.7,1.45,1.55)
opening('West rear window',-3,-15.32,1.8,.9,1.25)
opening('Upper rear sash',5,-15.32,4.7,1.2,1.55)
opening('Lower rear window',5,-15.32,1.8,1.3,.8)
for x in [-4.5,2.1]:box('Garden door step',(x,-14.95,.06),(1.2,.55,.16),stone)
# Shallow horizontal siding on tall wing, as seen on the house.
for z in [3.2+i*.15 for i in range(19)]:
 if 3.8<z<5.55:
  for x,w in [(3.78,1.15),(6.4,1.15)]:box('House lap siding',(x,-15.385,z),(w,.025,.018),blue,.001)
 else:box('House lap siding',(5.1,-15.385,z),(3.8,.025,.018),blue,.001)
# Bench with timber slats and dark metal supports along the path.
for y in [-8.4,-7.1]:
 for x in [-2.7,-2.2]:rod('Bench leg',(x,y,-.02),(x,y,.46),.025,metal)
for k in range(6):box('Bench seat slat',(-2.75+k*.11,-7.75,.48),(.09,1.7,.055),teak)
for k in range(4):box('Bench back slat',(-2.85,-7.75,.65+k*.115),(.055,1.7,.085),teak)
for y in [-8.45,-7.05]:rod('Bench back support',(-2.85,y,.05),(-2.85,y,1.07),.025,metal)
# Linked, batched leaf meshes provide real foliage silhouettes and dappled shadows.
def leaves(name,centers,ms,length=.11,width=.035):
 v=[];f=[];indices=[]
 for c in centers:
  c=Vector(c);theta=random.random()*math.tau;u=Vector((math.cos(theta),math.sin(theta),random.uniform(-.5,.7))).normalized()*length;w=Vector((-math.sin(theta),math.cos(theta),0))*width
  idx=len(v);v.extend([c-u,c-w,c+u,c+w,c+Vector((0,0,width*.35))]);f.extend([(idx,idx+1,idx+4),(idx+1,idx+2,idx+4),(idx+2,idx+3,idx+4),(idx+3,idx,idx+4)]);indices.extend([random.randrange(len(ms))]*4)
 o=mesh(name,v,f,ms[0])
 for m in ms[1:]:o.data.materials.append(m)
 for p,idx in zip(o.data.polygons,indices):p.material_index=idx
 return o
def shrub(x,y,r=.65,h=.9):
 cs=[]
 for k in range(950):
  a=random.uniform(0,math.tau);z=random.uniform(.04,1);rr=r*math.sqrt(random.random())*math.sqrt(max(0,1-(2*z-1)**2));cs.append((x+rr*math.cos(a),y+rr*math.sin(a),z*h))
 leaves('Dense garden shrub',cs,greens,.09,.032)
 for k in range(6):
  a=k*math.tau/6;rod('Shrub stem',(x,y,0),(x+r*.6*math.cos(a),y+r*.6*math.sin(a),h*.75),.013,wood)
def spiky(x,y,s=1,burgundy=False):
 v=[];f=[]
 for k in range(52):
  a=random.random()*math.tau;length=random.uniform(.65,1.5)*s;lean=random.uniform(.3,1);start=len(v)
  for i in range(7):
   t=i/6;rr=length*lean*t*t;z=.1+length*(1.4*t-.65*t*t);w=.045*s*math.sin(math.pi*(t*.9+.05))
   v.extend([(x+rr*math.cos(a)-w*math.sin(a),y+rr*math.sin(a)+w*math.cos(a),z),(x+rr*math.cos(a)+w*math.sin(a),y+rr*math.sin(a)-w*math.cos(a),z)])
  f.extend([(start+2*i,start+2*i+1,start+2*i+3,start+2*i+2) for i in range(6)])
 mesh('Burgundy cordyline' if burgundy else 'Strappy green planting',v,f,reds[0] if burgundy else greens[1])
def pot(x,y,r=.25,h=.45):
 v=[];f=[]
 for rad,z in [(r*.65,0),(r,h),(r*.92,h),(r*.83,h*.87)]:
  for i in range(24):a=i*math.tau/24;v.append((x+rad*math.cos(a),y+rad*math.sin(a),z))
 for row in range(3):
  for i in range(24):a=row*24+i;b=row*24+(i+1)%24;f.append((a,b,b+24,a+24))
 mesh('Blue glazed garden pot',v,f,clay)
 leaves('Potted foliage',[(x+random.uniform(-r,r),y+random.uniform(-r,r),h+random.random()*.65) for _ in range(180)],greens,.12,.025)
for x,y in [(-1.5,-.8),(2,-.6),(4.3,-.7),(-4.8,-13.9),(2.8,-14),(5.8,-3),(-3,3)]:pot(x,y)
for x,y,s in [(3,-5,1.2),(4.7,-8,1.25),(1,-11,.8),(5.8,-1,1),(-3.8,-11,.85)]:spiky(x,y,s,True)
for x,y in [(2,-5),(3.8,-8),(2.8,-10),(-1.5,-10),(-3.3,-4),(5.7,-6),(-4,-12)]:spiky(x,y,.65)
for x,y,r,h in [(-4.8,-2,.85,1.1),(-4.9,-4,.8,1),(-4.8,-7,.9,1.2),(-4.9,-10,1,1.1),(4.8,-3,1,1.3),(5.7,-5,.9,1.5),(5.9,-9,1,1.1),(5.4,-12,.8,.8),(0,-11,.8,.6),(-2,-11,.8,.7),(-3,-10,.65,.7),(3,-3,.8,.6),(-2.9,-3,.65,.75),(-2.8,-5,.6,.5)]:shrub(x,y,r,h)
# Low, spreading planting fills the beds visible in the photographs.
for x,y in [(-3.8,-8),(-3.8,-6),(-3.9,-3),(-4.1,-1),(4,-4),(4.7,-6),(5,-10),(4,-12),(1,-12),(-1,-12),(-3.5,-12),(-2.6,-9.5)]:
 shrub(x,y,.8,.65)
# Boundary greenery and tall overhanging trees, estimated positions.
for y in [-12,-9,-6,-3,0,3,6]:
 shrub(6.8,y,1,2);shrub(-5.9,y,1,1.6)
def tree(x,y,h,r):
 rod('Mature tree trunk',(x,y,0),(x+.3,y,h*.8),.18,bark);cs=[]
 for k in range(16):
  a=k*2.4;tip=Vector((x+math.cos(a)*r*random.uniform(.4,1),y+math.sin(a)*r*random.uniform(.4,1),h*random.uniform(.65,1)))
  rod('Tree branch',(x+.15,y,h*random.uniform(.4,.72)),tip,.025,bark)
  for i in range(900):
   q=Vector((random.gauss(0,r*.3),random.gauss(0,r*.3),random.gauss(0,.45)));cs.append(tip+q)
 leaves('Fine overhanging tree canopy',cs,greens,.16,.025)
for x,y,h,r in [(7,-1,10,2.5),(-6,-4,8,2.4),(7,-12,11,2.5),(-4,8.5,8,2.5)]:tree(x,y,h,r)
# Gravel scatter catches small highlights without covering paths.
v=[];f=[]
for i in range(9500):
 x=random.uniform(-6,7);y=random.uniform(-15,7)
 if (x>-.6 and y>-.5) or (-2.8<x<4 and y<-13):continue
 z=-.05;r=random.uniform(.012,.033);k=len(v);v.extend([(x-r,y-r,z),(x+r,y-r,z),(x+r,y+r,z),(x-r,y+r,z),(x,y,z+r)]);f.extend([(k,k+1,k+4),(k+1,k+2,k+4),(k+2,k+3,k+4),(k+3,k,k+4)])
mesh('Small garden gravel',v,f,wood)
# Cameras looking from house garden toward the proposal and back toward the house.
def camera(name,pos,target,lens):
 bpy.ops.object.camera_add(location=pos);o=move(bpy.context.object);o.name=name;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler();o.data.lens=lens;return o
cam=camera('Garden approach photo-informed',(-6,-13,3.4),(1,1.5,2.45),31)
context=camera('Garage southwest garden view',(-5.1,-8.6,4.1),(.9,1.7,2.65),26)
scene.camera=cam;scene.cycles.samples=96;scene.cycles.adaptive_threshold=.035
scene.render.resolution_x=1800;scene.render.resolution_y=1200
scene.view_settings.exposure=.45
# Soft blue sky with procedural cloud variation.
wn=scene.world.node_tree.nodes;wl=scene.world.node_tree.links;bg=wn.get('Background')
tc=wn.new('ShaderNodeTexCoord');noise=wn.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=3.5;noise.inputs['Detail'].default_value=2
wl.new(tc.outputs['Normal'],noise.inputs['Vector']);cr=wn.new('ShaderNodeValToRGB');cr.color_ramp.elements[0].position=.44;cr.color_ramp.elements[0].color=(.3,.5,.78,1);cr.color_ramp.elements[1].position=.65;cr.color_ramp.elements[1].color=(.85,.88,.9,1)
wl.new(noise.outputs['Fac'],cr.inputs[0]);wl.new(cr.outputs[0],bg.inputs['Color'])
scene['site_basis']='Photo-informed reconstruction from IMG_4198-4201 Live Photo frames. House spacing, boundary positions, planting and grade estimated; proposed garage geometry retained. Opaque material restored to existing wall meshes with inherited glazing material.'
bpy.ops.wm.save_as_mainfile(filepath=str(R/'garage-site.blend'))
for c,name in [(cam,'site-garden'),(context,'site-garage-angle')]:
 scene.camera=c;scene.render.filepath=str(R/(name+'.png'));bpy.ops.render.render(write_still=True)
print('SITE_RENDER_COMPLETE',flush=True)
