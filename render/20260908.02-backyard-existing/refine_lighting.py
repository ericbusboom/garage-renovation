import bpy
from pathlib import Path
R=Path(__file__).resolve().parent
bpy.ops.wm.open_mainfile(filepath=str(R/'backyard-existing.blend'))
s=bpy.context.scene;ns=s.world.node_tree.nodes;ls=s.world.node_tree.links;ns.clear();bg=ns.new('ShaderNodeBackground');bg.inputs['Color'].default_value=(.45,.62,.80,1);bg.inputs['Strength'].default_value=.5;out=ns.new('ShaderNodeOutputWorld');ls.new(bg.outputs[0],out.inputs[0]);bpy.data.objects['Soft afternoon sun'].data.energy=2.0;s.view_settings.exposure=0
# Replace only the photograph's cleaner fence crop, preserving all geometry.
m=bpy.data.materials['PHOTO / weathered_fence']
for n in m.node_tree.nodes:
 if n.type=='TEX_IMAGE':
  suffix='bump' if 'bump' in n.image.name else 'roughness' if 'roughness' in n.image.name else 'color'
  im=bpy.data.images.load(str(R/'textures'/('weathered_fence_'+suffix+'.png')),check_existing=False);im.colorspace_settings.name='sRGB' if suffix=='color' else 'Non-Color';n.image=im
for o in bpy.data.objects:
 if o.type=='MESH' and any(x==m for x in o.data.materials):
  uv=o.data.uv_layers.active
  if uv:
   for face in o.data.polygons:
    axis=max(range(3),key=lambda i:abs(face.normal[i]))
    for li in face.loop_indices:
     v=o.data.vertices[o.data.loops[li].vertex_index].co;a,b=(v.x,v.y) if axis==2 else (v.x,v.z) if axis==1 else (v.y,v.z);uv.data[li].uv=(a/.36,b/1.0)
s.cycles.use_denoising=True
for vl in s.view_layers:
 if hasattr(vl,'cycles'):vl.cycles.use_denoising=True
s.cycles.samples=80;s.render.resolution_percentage=100;bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(R/'backyard-existing.blend'))
s.cycles.samples=32;s.render.resolution_percentage=60
for name,file in [('01 / Whole backyard','01-backyard-overview-preview-v2'),('03 / Conversation area','03-conversation-area-preview-v2')]:
 s.camera=bpy.data.objects[name];s.render.filepath=str(R/(file+'.png'));bpy.ops.render.render(write_still=True)
print('REFINED_PREVIEWS_COMPLETE',flush=True)
