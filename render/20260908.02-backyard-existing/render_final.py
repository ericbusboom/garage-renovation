import bpy,json
from mathutils import Vector
from pathlib import Path
R=Path(__file__).resolve().parent
bpy.ops.wm.open_mainfile(filepath=str(R/'backyard-existing.blend'))
s=bpy.context.scene
s.world.node_tree.nodes.get('Background').inputs['Strength'].default_value=.8
s.view_settings.exposure=.8
if 'Soft conversation fill' not in bpy.data.objects:
 bpy.ops.object.light_add(type='AREA',location=(-4.6,-3.0,4.2));light=bpy.context.object;light.name='Soft conversation fill';light.data.energy=350;light.data.shape='DISK';light.data.size=4;light.rotation_euler=(Vector((-5.3,-5.2,.5))-light.location).to_track_quat('-Z','Y').to_euler()
s.cycles.samples=80;s.cycles.adaptive_threshold=.035;s.render.resolution_percentage=100
cameras=[('01 / Whole backyard','01-backyard-overview'),('02 / Patio toward garage','02-patio-toward-garage'),('03 / Conversation area','03-conversation-area'),('04 / House and gardens','04-house-and-gardens')]
for name,file in cameras:
 s.camera=bpy.data.objects[name];s.render.filepath=str(R/(file+'.png'));bpy.ops.render.render(write_still=True)
s.camera=bpy.data.objects[cameras[0][0]];bpy.ops.wm.save_as_mainfile(filepath=str(R/'backyard-existing.blend'))
info={'source_parts':s.get('source_parts'),'blender_objects':len(bpy.data.objects),'packed_texture_images':sum(bool(i.packed_file) for i in bpy.data.images),'render_engine':'Cycles CPU','samples':80,'resolution':[s.render.resolution_x,s.render.resolution_y],'cameras':[n for n,_ in cameras]};(R/'scene-validation.json').write_text(json.dumps(info,indent=2))
print('BACKYARD_FINAL_COMPLETE',flush=True)
