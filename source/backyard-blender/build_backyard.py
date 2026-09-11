"""Blender 5: corrected existing site + photo-derived surface maps, no proposed garage."""
import bpy,bmesh,json,math,random,sys
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parent;random.seed(4227)
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
scene=bpy.context.scene
cols={}
def collection(name):
 if name not in cols:
  cols[name]=bpy.data.collections.new(name);scene.collection.children.link(cols[name])
 return cols[name]
def link(o,g):
 for c in list(o.users_collection):c.objects.unlink(o)
 collection(g).objects.link(o);return o
def linear(v):return v/12.92 if v<=.04045 else ((v+.055)/1.055)**2.4
def material(name,color,rough=.7,metal=0):
 m=bpy.data.materials.new(name);m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=tuple(linear(c) for c in color)+(1,);p.inputs['Roughness'].default_value=rough;p.inputs['Metallic'].default_value=metal;return m
def hx(s):return [int(s[i:i+2],16)/255 for i in [0,2,4]]
manifest=json.loads((R/'textures/manifest.json').read_text());photos={};periods={}
for spec in manifest:
 name=spec['material'];m=material('PHOTO / '+name,[.7]*3);ns=m.node_tree.nodes;ls=m.node_tree.links;p=ns.get('Principled BSDF')
 for suffix,input_name in [('color','Base Color'),('roughness','Roughness')]:
  tex=ns.new('ShaderNodeTexImage');tex.image=bpy.data.images.load(str(R/'textures'/f'{name}_{suffix}.png'),check_existing=True);tex.extension='REPEAT';tex.interpolation='Linear';tex.image.colorspace_settings.name='sRGB' if suffix=='color' else 'Non-Color';ls.new(tex.outputs['Color'],p.inputs[input_name])
 tex=ns.new('ShaderNodeTexImage');tex.image=bpy.data.images.load(str(R/'textures'/f'{name}_bump.png'),check_existing=True);tex.image.colorspace_settings.name='Non-Color';tex.extension='REPEAT'
 bump=ns.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.22;bump.inputs['Distance'].default_value=.014 if name=='woodchips' else .008 if name=='flagstone' else .0015;ls.new(tex.outputs['Color'],bump.inputs['Height']);ls.new(bump.outputs[0],p.inputs['Normal'])
 m['source_photo']=spec['source'];m['source_crop']=str(spec['source_crop_pixels']);m['limitation']='Photographic color with residual illumination; luminance-derived bump and estimated roughness, not scanned PBR.'
 photos[name]=m;periods[m.name]=spec['atlas_period_metres']
wood=material('Warm weathered bench timber',hx('a47a43'),.47)
metal=material('Dark painted metal',hx('343b39'),.40,.55)
white=material('Warm white trim',hx('e7e7db'),.52)
glass=material('Dark reflective glazing',hx('3f6068'),.17,.35)
gp=glass.node_tree.nodes.get('Principled BSDF');gp.inputs['Coat Weight'].default_value=.5
silver=material('Brushed Airstream aluminum',hx('cbd0cf'),.29,.82)
roof=material('Weathered gray shingles',hx('686c68'),.86)
ns=roof.node_tree.nodes;ls=roof.node_tree.links;p=ns.get('Principled BSDF');uv=ns.new('ShaderNodeTexCoord');brick=ns.new('ShaderNodeTexBrick');brick.inputs['Scale'].default_value=1;brick.inputs['Brick Width'].default_value=.33;brick.inputs['Row Height'].default_value=.16;brick.inputs['Mortar Size'].default_value=.003;brick.inputs['Color1'].default_value=(.20,.22,.22,1);brick.inputs['Color2'].default_value=(.30,.32,.31,1);brick.inputs['Mortar'].default_value=(.075,.08,.08,1);ls.new(uv.outputs['UV'],brick.inputs['Vector']);ls.new(brick.outputs['Color'],p.inputs['Base Color']);bump=ns.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.2;bump.inputs['Distance'].default_value=.012;ls.new(brick.outputs['Fac'],bump.inputs['Height']);ls.new(bump.outputs[0],p.inputs['Normal'])
# Fine procedural grain complements photo textures on narrow parts where source texels are insufficient.
for m,scale,strength in [(wood,25,.004),(silver,180,.00035)]:
 ns=m.node_tree.nodes;ls=m.node_tree.links;t=ns.new('ShaderNodeTexNoise');t.inputs['Scale'].default_value=scale;b=ns.new('ShaderNodeBump');b.inputs['Strength'].default_value=.16;b.inputs['Distance'].default_value=strength;ls.new(t.outputs['Fac'],b.inputs['Height']);ls.new(b.outputs[0],ns.get('Principled BSDF').inputs['Normal'])
leafm=[]
for i,c in enumerate(['476236','617c44','7d8e51','536b3c','86935e']):
 m=material('Leaf '+str(i),hx(c),.53);p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Subsurface Weight'].default_value=.055;leafm.append(m)
bark=material('Bark',hx('8a806b'),.95)
matcache={}
def fallback(p):
 key=tuple(p['color'])
 if key not in matcache:matcache[key]=material('Source '+str(len(matcache)),p['color'])
 return matcache[key]
def select_mat(p):
 n=p['name'].lower();g=p['group']
 if g=='garage':
  if 'confirmed sill' in n:return glass
  if 'assumed height' in n:return wood
  if 'floor datum' in n:return photos['flagstone']
  return photos['garage_stucco']
 if g in ['garage_roof','house_roof']:return roof
 if g=='house':
  if n=='west rear sash':return glass
  if any(s in n for s in ['trim','sash','jamb','vertical']):return white
  if any(s in n for s in ['window','french door']):return glass
  return photos['house_stucco']
 if g in ['pergola','pergola_roof']:return photos['painted_timber']
 if g=='boundary' or g=='garden_fence':return photos['weathered_fence']
 if g=='trunks':return bark
 if g=='seating':return metal if any(s in n for s in ['metal','arm','support']) else fallback(p) if 'stone' in n else wood
 if g=='fire_pit':return wood if 'log' in n else metal
 if g=='trailer':return glass if 'window' in n else metal if 'wheel' in n or 'tongue' in n else silver
 if 'pot' in n:
  m=fallback(p);bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Roughness'].default_value=.23;bs.inputs['Coat Weight'].default_value=.45;return m
 if g=='paths':return fallback(p) if 'brick' in n or 'driveway' in n or 'work patio' in n else photos['flagstone']
 if g=='ground' or g=='beds':
  if 'rectangular planting' in n:return photos['weathered_fence']
  return photos['woodchips']
 if g=='shelter':return metal if 'upright' in n else photos['garage_stucco'] if 'pillar' in n else wood
 return fallback(p)
def mesh(name,vertices,faces,g,m):
 me=bpy.data.meshes.new(name);me.from_pydata(vertices,[],faces);me.update();o=bpy.data.objects.new(name,me);collection(g).objects.link(o)
 if m:o.data.materials.append(m)
 return o
def uvmap(o,m):
 uv=o.data.uv_layers.new(name='Photo metric projection');sx,sy=periods.get(m.name,[1,1])
 for face in o.data.polygons:
  normal=face.normal;axis=max(range(3),key=lambda i:abs(normal[i]))
  for li in face.loop_indices:
   v=o.data.vertices[o.data.loops[li].vertex_index].co
   a,b=(v.x,v.y) if axis==2 else (v.x,v.z) if axis==1 else (v.y,v.z)
   uv.data[li].uv=(a/sx,b/sy)
def rod(name,a,b,r,m,g='Render detail'):
 a,b=Vector(a),Vector(b);d=b-a;bpy.ops.mesh.primitive_cone_add(vertices=7,radius1=r,radius2=r*.65,depth=d.length,location=(a+b)/2);o=link(bpy.context.object,g);o.name=name;o.rotation_euler=d.to_track_quat('Z','Y').to_euler();o.data.materials.append(m);return o
# Replace low-poly foliage envelopes with leaf geometry, retaining source positions and extents.
def foliage(p):
 vs=[Vector(v) for v in p['vertices']];mn=Vector(tuple(min(v[i] for v in vs) for i in range(3)));mx=Vector(tuple(max(v[i] for v in vs) for i in range(3)));c=(mn+mx)/2;r=(mx-mn)/2;g=p['group']
 count=4600 if g=='canopy' else 650 if g=='pergola_foliage' else 700
 length=.105 if g=='canopy' else .065 if 'low' in p['name'].lower() else .095
 vertices=[];faces=[];colors=[]
 for k in range(count):
  z=random.uniform(-1,1);a=random.uniform(0,math.tau);rr=math.sqrt(1-z*z);radius=random.random()**.35
  q=c+Vector((r.x*rr*math.cos(a),r.y*rr*math.sin(a),r.z*z))*radius
  angle=random.random()*math.tau;u=Vector((math.cos(angle),math.sin(angle),random.uniform(-.4,.55))).normalized()*length;w=Vector((-math.sin(angle),math.cos(angle),0))*length*.34
  i=len(vertices);vertices.extend([q-u,q-w,q+u,q+w,q+Vector((0,0,length*.11))]);faces.extend([(i,i+1,i+4),(i+1,i+2,i+4),(i+2,i+3,i+4),(i+3,i,i+4)]);colors.extend([random.randrange(len(leafm))]*4)
 o=mesh(p['name']+' / detailed leaves',vertices,faces,'Vegetation / '+g,leafm[0])
 for m in leafm[1:]:o.data.materials.append(m)
 for face,i in zip(o.data.polygons,colors):face.material_index=i
 if g!='pergola_foliage' and r.z>.25:
  for k in range(4):
   a=k*2.4;rod('Fine plant branch',(c.x,c.y,max(0,c.z-r.z)),(c.x+math.cos(a)*r.x*.55,c.y+math.sin(a)*r.y*.55,c.z+r.z*.55),.012,bark,'Vegetation / branches')
 if 'low bush' in p['name'].lower():
  flower=material('Small muted lavender flowers '+str(len(bpy.data.materials)),hx('a49ab1'),.7)
  # Sparse little blossoms, not an invented carpet of flowers.
  verts=[];faces=[]
  for k in range(12):
   q=c+Vector((random.uniform(-r.x,r.x),random.uniform(-r.y,r.y),r.z*.6));i=len(verts);verts.extend([q+Vector((.017,0,0)),q+Vector((0,.017,0)),q+Vector((-.017,0,0)),q+Vector((0,-.017,0))]);faces.append((i,i+1,i+2,i+3))
  mesh('Small flowers',verts,faces,'Vegetation / flowers',flower)
source=json.loads((R/'site-scene.json').read_text());source_count=0
for part_index,p in enumerate(source['parts']):
 if part_index%150==0:print('IMPORT',part_index,'/',len(source['parts']),flush=True)
 n=p['name'];g=p['group']
 if n in ['Flagstone joint','Jungle wood chip']:continue
 if g in ['planting','canopy','pergola_foliage'] and 'strap leaf' not in n.lower():foliage(p);continue
 m=select_mat(p);o=mesh(n,p['vertices'],p['triangles'],g,m);source_count+=1
 bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(o.data);bm.free();o.data.update();uvmap(o,m)
 if any(k in n.lower() for k in ['rounded aluminum','wheel','pot','roof rib']):
  for f in o.data.polygons:f.use_smooth=True
 if g in ['garage','house','pergola','seating','shelter','garden_fence']:
  mod=o.modifiers.new('Subtle edge highlights','BEVEL');mod.width=.005;mod.segments=2
 if 'strap leaf' in n.lower():
  mod=o.modifiers.new('Leaf thickness','SOLIDIFY');mod.thickness=.002
# Apply render-only refinement consistently during future rebuilds.
sys.path.insert(0,str(R))
from refine_geometry import refine
refine()
# Broader neutral ground behind the clipped house and alley; no invented neighboring architecture.
bpy.ops.mesh.primitive_plane_add(size=200,location=(0,0,-.16));o=link(bpy.context.object,'Context');o.name='Surrounding ground';o.data.materials.append(material('Backdrop earth',hx('a89c86'),.95))
# Lighting and cameras.
scene.render.engine='CYCLES';scene.cycles.device='CPU';scene.cycles.samples=64;scene.cycles.use_denoising=True;scene.cycles.adaptive_threshold=.045
scene.world.use_nodes=True;ns=scene.world.node_tree.nodes;ls=scene.world.node_tree.links;ns.clear();bg=ns.new('ShaderNodeBackground');bg.inputs['Color'].default_value=(.45,.62,.80,1);bg.inputs['Strength'].default_value=.5;out=ns.new('ShaderNodeOutputWorld');ls.new(bg.outputs[0],out.inputs[0])
bpy.ops.object.light_add(type='SUN',location=(-10,-8,18));sun=link(bpy.context.object,'Lighting');sun.name='Soft afternoon sun';sun.data.energy=2.0;sun.data.angle=math.radians(8);sun.rotation_euler=(Vector((0,0,0))-sun.location).to_track_quat('-Z','Y').to_euler()
def camera(name,pos,target,lens=35,ortho=None):
 bpy.ops.object.camera_add(location=pos);o=link(bpy.context.object,'Cameras');o.name=name;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler();o.data.lens=lens;o.data.clip_end=300
 if ortho:o.data.type='ORTHO';o.data.ortho_scale=ortho
 return o
cams=[(camera('01 / Whole backyard',(-22,-32,29),(-1,-5,.5),ortho=37),'01-backyard-overview'),(camera('02 / Patio toward garage',(-6.3,-12.0,3.0),(-.5,.2,1.5),26),'02-patio-toward-garage'),(camera('03 / Conversation area',(-3.0,-2.2,2.6),(-5.45,-5.65,.9),30),'03-conversation-area'),(camera('04 / House and gardens',(-5.1,1.0,5.2),(-.1,-13.0,1.0),30),'04-house-and-gardens')]
scene.render.resolution_x=1800;scene.render.resolution_y=1350;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG';scene.view_settings.view_transform='AgX';scene.view_settings.exposure=0
scene['basis']='Existing backyard revision 8, photo-informed manual reconstruction. Current garage; north-aligned shelter; four rooms; no pool; no internal south-garden path; pergola ends 8 ft north of fence, path continues to patio.'
scene['texture_method']='Six photo-cropped surface color maps. Luminance bump and roughness are approximations, not measured PBR scans.'
scene['source_parts']=len(source['parts']);scene.camera=cams[0][0]
# Pack all used image data for a portable native file.
bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(R/'backyard-existing.blend'))
info={'source_parts':len(source['parts']),'blender_objects':len(bpy.data.objects),'packed_images':len(bpy.data.images),'cameras':[c.name for c,_ in cams],'render_engine':'Cycles CPU','samples':64,'resolution':[1800,1350]};(R/'scene-validation.json').write_text(json.dumps(info,indent=2))
args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
if 'build-only' in args:print('BACKYARD_BUILD_COMPLETE',flush=True);sys.exit(0)
# Preview first for review; full renders are produced from the saved scene afterward.
scene.cycles.samples=20;scene.render.resolution_percentage=60
for c,name in [cams[0],cams[2]]:
 scene.camera=c;scene.render.filepath=str(R/(name+'-preview.png'));bpy.ops.render.render(write_still=True)
print('BACKYARD_PREVIEWS_COMPLETE',flush=True)
