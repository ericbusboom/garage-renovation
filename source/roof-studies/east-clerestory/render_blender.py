"""Render the actual FreeCAD tessellation: outside steel, inside metal infill."""
import bpy,bmesh,json,math,sys
from pathlib import Path
from mathutils import Vector
P=Path(__file__).resolve().parent
bpy.ops.wm.read_factory_settings(use_empty=True);scene=bpy.context.scene
colors={'rafter':('bc702c',.35,.4),'steel':('354247',.48,.34),'panel':('b6c0c2',.3,.42),'trim':('ecebe4',.08,.38),'roof':('606d70',.52,.4),'pv':('243d50',.62,.18),'glass':('63c6db',.35,.16),'wood':('aa865c',0,.62),'stucco':('b7b9b3',0,.83),'slab':('a6a7a2',0,.84)}
def linear(c):return c/12.92 if c<=.04045 else ((c+.055)/1.055)**2.4
mats={}
for key,(hx,metal,rough) in colors.items():
 m=bpy.data.materials.new(key);m.use_nodes=True;n=m.node_tree.nodes;p=n.get('Principled BSDF');p.inputs['Base Color'].default_value=tuple(linear(int(hx[i:i+2],16)/255) for i in [0,2,4])+(1,);p.inputs['Metallic'].default_value=metal;p.inputs['Roughness'].default_value=rough
 if key in ['pv','glass']:p.inputs['Coat Weight'].default_value=.5
 if key in ['stucco','panel','steel']:
  tex=n.new('ShaderNodeTexNoise');tex.inputs['Scale'].default_value=180 if key!='stucco' else 80;b=n.new('ShaderNodeBump');b.inputs['Distance'].default_value=.00035 if key!='stucco' else .003;b.inputs['Strength'].default_value=.2;m.node_tree.links.new(tex.outputs['Fac'],b.inputs['Height']);m.node_tree.links.new(b.outputs['Normal'],p.inputs['Normal'])
 mats[key]=m
cols={};d=json.loads((P/'cad-mesh.json').read_text())
for e in d['objects']:
 g='Garage / '+e['group']
 if g not in cols:cols[g]=bpy.data.collections.new(g);scene.collection.children.link(cols[g])
 mesh=bpy.data.meshes.new(e['name']);mesh.from_pydata([[v*.0254 for v in p] for p in e['vertices']],[],e['triangles']);mesh.update();bm=bmesh.new();bm.from_mesh(mesh);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(mesh);bm.free()
 ob=bpy.data.objects.new(e['name'],mesh);cols[g].objects.link(ob);ob.data.materials.append(mats[e['material']]);ob['source']='Garage-Exposed-Steel.FCStd / cad-mesh.json'
 if e['material'] in ['steel','trim','panel','wood']:
  b=ob.modifiers.new('Small edge highlight','BEVEL');b.width=.00065;b.segments=2;b.affect='EDGES'
# Studio ground and soft daylight keep the new panel/steel relationship legible.
bpy.ops.mesh.primitive_plane_add(size=2000,location=(2,2,-.06));ground=bpy.context.object;ground.name='Presentation ground';gm=bpy.data.materials.new('Warm concrete ground');gm.diffuse_color=(.56,.58,.56,1);ground.data.materials.append(gm)
world=bpy.data.worlds.new('Daylight');scene.world=world;world.use_nodes=True;bg=world.node_tree.nodes.get('Background');bg.inputs['Color'].default_value=(.55,.65,.8,1);bg.inputs['Strength'].default_value=.5
bpy.ops.object.light_add(type='SUN',location=(-8,-6,12));sun=bpy.context.object;sun.name='Warm afternoon sun';sun.data.energy=2.5;sun.data.angle=.12;sun.rotation_euler=(math.radians(28),math.radians(-35),math.radians(-40))

def light(name,pos,target,power,size):
 bpy.ops.object.light_add(type='AREA',location=pos);o=bpy.context.object;o.name=name;o.data.energy=power;o.data.shape='DISK';o.data.size=size;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler()
light('Soft west fill',(-8,2,9),(2,2,3),1600,9);light('North fill',(2,13,9),(2,2,3),1800,8)
def cam(name,pos,target,lens=45):
 bpy.ops.object.camera_add(location=pos);o=bpy.context.object;o.name=name;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler();o.data.lens=lens;return o
cameras=[(cam('Southeast exterior',(14,-13,11),(2.6,2.1,3),48),'01-southeast-draft'),(cam('Northeast exterior',(15,16,10),(2.7,3.6,3.2),48),'02-northeast-draft')]
scene.render.engine='CYCLES';scene.cycles.device='CPU';scene.cycles.samples=16;scene.cycles.use_denoising=True;scene.cycles.adaptive_threshold=.01;scene.render.resolution_x=1100;scene.render.resolution_y=900;scene.render.resolution_percentage=100;scene.view_settings.view_transform='AgX';scene.view_settings.exposure=0;scene.view_settings.look='AgX - Medium High Contrast';scene.render.image_settings.file_format='PNG';scene.camera=cameras[0][0]
scene['design']='Rough roof concept: east setback infill, retained hip cap, six vertical clerestory panes and extended hip cap. Historical framing for context only.';scene['engineering_limit']='Connection/secondary framing and envelope attachment not designed. This is an architectural assembly visualization.'
bpy.ops.wm.save_as_mainfile(filepath=str(P/'garage-east-clerestory.blend'))
for camera,name in cameras:
 scene.camera=camera;scene.render.filepath=str(P/(name+'.png'));bpy.ops.render.render(write_still=True);print('RENDERED '+name,flush=True)
(P/'render-validation.json').write_text(json.dumps(dict(source_objects=len(d['objects']),render_engine='Cycles CPU',samples=16,resolution=[1100,900],cameras=[c.name for c,_ in cameras],source='Exact CAD tessellation in metres; bevel finish only'),indent=2))

# An explicit roof-off view exposes the requested rafter-to-chord arrangement.
for ob in cols['Garage / EastSetbackRoof'].objects:ob.hide_render=True
for ob in cols.get('Garage / InteriorMetalPanels',[]).objects:
 if ob.name.startswith('E inside'):ob.hide_render=True
scene.camera=cameras[0][0];scene.render.filepath=str(P/'03-east-rafter-study.png');bpy.ops.render.render(write_still=True)
