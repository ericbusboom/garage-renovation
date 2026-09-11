import bpy, math, json, sys
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parent
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
j=json.loads((ROOT/'source/garage-model.json').read_text())
def linear(c): return c/12.92 if c<=.04045 else ((c+.055)/1.055)**2.4
def rgb(h):return tuple(linear(int(h[i:i+2],16)/255) for i in (1,3,5))+(1,)
mats={}
for name,(hx,metal,rough) in j['materials'].items():
 m=bpy.data.materials.new(name);m.use_nodes=True;n=m.node_tree.nodes;l=m.node_tree.links;p=n.get('Principled BSDF')
 p.inputs['Base Color'].default_value=rgb(hx);p.inputs['Metallic'].default_value=metal;p.inputs['Roughness'].default_value=rough
 if name=='glass':
  p.inputs['Base Color'].default_value=rgb('#b8cbd0');p.inputs['Metallic'].default_value=.05;p.inputs['Transmission Weight'].default_value=.9;p.inputs['IOR'].default_value=1.45;p.inputs['Roughness'].default_value=.08
 if name in ('pv','roof'):p.inputs['Coat Weight'].default_value=.35
 if name in ('wall','slab','ground','wood','endwood','steel','trim'):
  tex=n.new('ShaderNodeTexNoise');tex.inputs['Scale'].default_value=110 if name=='wall' else 65;tex.inputs['Detail'].default_value=3
  coord=n.new('ShaderNodeTexCoord');l.new(coord.outputs['Object'],tex.inputs['Vector'])
  if name in ('wood','endwood'):
   mapping=n.new('ShaderNodeVectorMath');mapping.operation='MULTIPLY';mapping.inputs[1].default_value=(3,3,.08);l.new(coord.outputs['Object'],mapping.inputs[0]);l.new(mapping.outputs[0],tex.inputs['Vector'])
  bump=n.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.23;bump.inputs['Distance'].default_value=.012 if name in ('ground','slab') else .002;l.new(tex.outputs['Fac'],bump.inputs['Height']);l.new(bump.outputs['Normal'],p.inputs['Normal'])
 mats[name]=m
collections={}
for o in j['objects']:
 group='internal_trusses' if o['group']=='frame' and o['material']=='truss' else o['group']
 if group=='site':continue
 if group not in collections:
  c=bpy.data.collections.new(group);bpy.context.scene.collection.children.link(c);collections[group]=c
 mesh=bpy.data.meshes.new(o['name']);mesh.from_pydata(o['vertices'],[],o['faces']);mesh.update()
 ob=bpy.data.objects.new(o['name'],mesh);collections[group].objects.link(ob);ob.data.materials.append(mats[o['material']])
 # Recalculate mesh normals without changing the supplied dimensions.
 import bmesh
 bm=bmesh.new();bm.from_mesh(mesh);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(mesh);bm.free()
 if o['material']!='glass':
  mod=ob.modifiers.new('Small edge highlights','BEVEL');mod.width=.003;mod.segments=3
  mod=ob.modifiers.new('Weighted corner normals','WEIGHTED_NORMAL')
 if group=='internal_trusses':ob.hide_render=True;ob.hide_set(True)
bpy.ops.mesh.primitive_plane_add(size=2000,location=(0,0,-.057));bpy.context.object.name='Presentation ground';bpy.context.object.data.materials.append(mats['ground'])
scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.samples=128;scene.cycles.use_denoising=True
scene.cycles.adaptive_threshold=.02
prefs=bpy.context.preferences.addons['cycles'].preferences
print('GPU_PROBE',flush=True)
for backend in ('OPTIX','CUDA','HIP'):
 try:
  prefs.compute_device_type=backend;prefs.get_devices();devices=[d for d in prefs.devices if d.type!='CPU'];print(backend,[(d.name,d.type) for d in prefs.devices],flush=True)
  if devices:
   for d in prefs.devices:d.use=d.type!='CPU'
   scene.cycles.device='GPU';break
 except Exception as e:print(backend,str(e),flush=True)
else:scene.cycles.device='CPU'
scene.world.use_nodes=True;n=scene.world.node_tree.nodes;l=scene.world.node_tree.links;n.clear()
bg=n.new('ShaderNodeBackground');bg.inputs['Color'].default_value=(.55,.65,.8,1);bg.inputs['Strength'].default_value=.45;out=n.new('ShaderNodeOutputWorld');l.new(bg.outputs[0],out.inputs[0])
bpy.ops.object.light_add(type='SUN',location=(-8,-10,12));sun=bpy.context.object;sun.name='Warm afternoon sun';sun.data.energy=2.2;sun.data.angle=math.radians(12);sun.data.color=(1,.89,.76);sun.rotation_euler=(Vector((2,2,0))-sun.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.object.light_add(type='AREA',location=(-8,-6,10));light=bpy.context.object;light.name='Soft west fill';light.data.energy=1800;light.data.shape='DISK';light.data.size=8;light.rotation_euler=(Vector((1,2,2))-light.location).to_track_quat('-Z','Y').to_euler()
def camera(name,pos,target,lens):
 bpy.ops.object.camera_add(location=pos);c=bpy.context.object;c.name=name;c.rotation_euler=(Vector(target)-c.location).to_track_quat('-Z','Y').to_euler();c.data.lens=lens;c.data.clip_end=300;return c
sw=camera('Southwest exterior',(-16,-20,10),(0.7,2.2,2.4),58)
nw=camera('Northwest exterior',(-17,23,9),(0.5,2.7,2.5),55)
scene.camera=sw;scene.render.resolution_x=1600;scene.render.resolution_y=1200;scene.render.resolution_percentage=100
scene.view_settings.view_transform='AgX';scene.view_settings.exposure=0
scene.render.image_settings.file_format='PNG';scene.render.film_transparent=False
scene['source']='garage-render-package.zip; original metre geometry; illustrative materials and presentation ground'
scene['render_device']=scene.cycles.device
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'garage.blend'))
for cam,filename in [(sw,'southwest'),(nw,'northwest')]:
 scene.camera=cam;scene.render.filepath=str(ROOT/(filename+'.png'));bpy.ops.render.render(write_still=True)
print('GARAGE_RENDER_COMPLETE',flush=True)
