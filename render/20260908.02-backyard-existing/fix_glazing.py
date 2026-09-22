import bpy
from pathlib import Path
R=Path(__file__).resolve().parent
bpy.ops.wm.open_mainfile(filepath=str(R/'backyard-existing.blend'))
o=bpy.data.objects['West rear sash'];o.data.materials.clear();o.data.materials.append(bpy.data.materials['Dark reflective glazing'])
s=bpy.context.scene;s.cycles.samples=80;s.render.resolution_percentage=100
bpy.ops.wm.save_as_mainfile(filepath=str(R/'backyard-existing.blend'))
for name,file in [('03 / Conversation area','03-conversation-area'),('04 / House and gardens','04-house-and-gardens')]:
 s.camera=bpy.data.objects[name];s.render.filepath=str(R/(file+'.png'));bpy.ops.render.render(write_still=True)
print('GLAZING_COMPLETE',flush=True)
