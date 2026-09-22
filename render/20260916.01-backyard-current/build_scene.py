"""Current COMPAS frame in reviewed backyard: Cycles stills and lightweight GLB."""
import bpy,bmesh,json,hashlib,sys,math
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parent
BASE=Path('/proj/garage/backyard-proposal/backyard-existing.blend')
bpy.ops.wm.open_mainfile(filepath=str(BASE));scene=bpy.context.scene
removed=[]
for c in list(bpy.data.collections):
 if c.name=='garage_roof':
  for o in list(c.objects):removed.append(o.name);bpy.data.objects.remove(o,do_unlink=True)
colors={'rafter':('bc702c',.35,.4),'steel':('354247',.48,.34),'panel':('b6c0c2',.3,.42),'trim':('ecebe4',.08,.38),'roof':('606d70',.52,.4),'pv':('243d50',.62,.18),'glass':('63a5b5',.2,.16),'wood':('aa865c',0,.62),'stucco':('b7b9b3',0,.83),'slab':('a6a7a2',0,.84)}
def linear(c):return c/12.92 if c<=.04045 else ((c+.055)/1.055)**2.4
mats={}
for key,(hx,metal,rough) in colors.items():
 m=bpy.data.materials.new('CURRENT / '+key);m.use_nodes=True;n=m.node_tree.nodes;p=n.get('Principled BSDF');p.inputs['Base Color'].default_value=tuple(linear(int(hx[i:i+2],16)/255) for i in (0,2,4))+(1,);p.inputs['Metallic'].default_value=metal;p.inputs['Roughness'].default_value=rough
 if key in ('pv','glass'):p.inputs['Coat Weight'].default_value=.5
 if key in ('panel','steel'):
  noise=n.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=180;b=n.new('ShaderNodeBump');b.inputs['Distance'].default_value=.00035;b.inputs['Strength'].default_value=.2;m.node_tree.links.new(noise.outputs['Fac'],b.inputs['Height']);m.node_tree.links.new(b.outputs['Normal'],p.inputs['Normal'])
 mats[key]=m
src=json.loads((R/'scene-mesh.json').read_text());cols={};added=[];skipped=[]
for e in src['objects']:
 # Use the reviewed backyard's existing lower walls, windows, doors and floor.
 if e['group'] in ('ExistingGarage','Context') or (e['group']=='DoorsWindows' and max(v[2] for v in e['vertices'])<=98.5+1e-6):
  skipped.append(e['name']);continue
 g='CURRENT / '+e['group']
 if g not in cols:cols[g]=bpy.data.collections.new(g);scene.collection.children.link(cols[g])
 mesh=bpy.data.meshes.new(e['name']);mesh.from_pydata([[v*.0254 for v in p] for p in e['vertices']],[],e['triangles']);mesh.update();bm=bmesh.new();bm.from_mesh(mesh);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(mesh);bm.free()
 ob=bpy.data.objects.new('CURRENT / '+e['name'],mesh);cols[g].objects.link(ob);ob.data.materials.append(mats[e['material']]);ob['compas_member']=e.get('member_id','envelope');added.append(ob.name)
 if e['material'] in ('steel','trim','panel','wood'):
  b=ob.modifiers.new('Edge highlights','BEVEL');b.width=.00065;b.segments=2
scene['frame_spec_sha256']=hashlib.sha256((R/'frame-spec.json').read_bytes()).hexdigest()
scene['basis']='Latest COMPAS framing; S1 west face at south door east edge X143.5 in. Existing reviewed backyard kept in shared metre coordinates. Roof/wall envelope from preceding study.'
def cam(name,pos,target,lens):
 bpy.ops.object.camera_add(location=pos);o=bpy.context.object;o.name=name;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler();o.data.lens=lens;return o
cameras=[(cam('CURRENT / Patio toward garage',(-6.3,-12,4.5),(1.8,2,3.0),29),'01-patio-to-garage'),(cam('CURRENT / Southwest garden',(-10,-9,8.5),(1.5,1.8,2.6),34),'02-southwest-backyard')]
scene.render.engine='CYCLES';scene.cycles.device='CPU';scene.cycles.samples=192;scene.cycles.use_denoising=True;scene.cycles.adaptive_threshold=.012
scene.render.resolution_x=2400;scene.render.resolution_y=1800;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG';scene.render.image_settings.color_mode='RGB'
scene.view_settings.view_transform='AgX';scene.camera=cameras[0][0]
bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(R/'backyard-current.blend'))
report={'frame_spec_sha256':scene['frame_spec_sha256'],'scene_sha256':hashlib.sha256((R/'scene-mesh.json').read_bytes()).hexdigest(),'baseline_sha256':hashlib.sha256(BASE.read_bytes()).hexdigest(),'removed_baseline_roof':removed,'added_objects':len(added),'skipped_duplicate_context':skipped,'cycles_samples':192,'resolution':[2400,1800],'source_frame_members':len(json.loads((R/'frame-spec.json').read_text())['members']),'interactive_note':'Same building geometry; simplified foliage and 1024px textures. Real-time PBR lighting differs from Cycles.'}
# Export a lighter browser copy; saved .blend and Cycles renders retain all detail.
leaf_reduced=0
for ob in list(bpy.data.objects):
 if ob.type!='MESH':continue
 if len(ob.data.polygons)>1000 and any(m and m.name.startswith('Leaf ') for m in ob.data.materials):
  old=ob.data;faces=[p for p in old.polygons if (p.index//4)%4==0];used=sorted({v for p in faces for v in p.vertices});mapping={v:i for i,v in enumerate(used)};me=bpy.data.meshes.new(old.name+' web');me.from_pydata([old.vertices[i].co for i in used],[],[[mapping[i] for i in p.vertices] for p in faces]);me.update()
  for m in old.materials:me.materials.append(m)
  for p,q in zip(me.polygons,faces):p.material_index=q.material_index
  ob.data=me;leaf_reduced+=1
for im in bpy.data.images:
 if im.type=='IMAGE' and max(im.size)>1024:
  ratio=1024/max(im.size);im.scale(max(1,int(im.size[0]*ratio)),max(1,int(im.size[1]*ratio)))
bpy.ops.object.select_all(action='DESELECT')
for ob in scene.objects:
 if ob.type=='MESH' and not ob.hide_render and ob.name!='Surrounding ground':ob.hide_set(False);ob.select_set(True)
bpy.ops.export_scene.gltf(filepath=str(R/'backyard-current.glb'),export_format='GLB',use_selection=True,export_apply=True,export_cameras=False,export_lights=False,export_yup=True)
report['interactive_reduced_foliage_objects']=leaf_reduced;(R/'validation.json').write_text(json.dumps(report,indent=2));print('INTERACTIVE_READY',flush=True)
bpy.ops.wm.open_mainfile(filepath=str(R/'backyard-current.blend'));scene=bpy.context.scene
for name,file in [('CURRENT / Patio toward garage','01-patio-to-garage'),('CURRENT / Southwest garden','02-southwest-backyard')]:
 scene.camera=bpy.data.objects[name];scene.render.filepath=str(R/(file+'.png'));bpy.ops.render.render(write_still=True);print('RENDER_READY '+file,flush=True)
print('BACKYARD_COMPLETE',flush=True)
