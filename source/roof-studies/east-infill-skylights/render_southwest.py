import bpy
from pathlib import Path
from mathutils import Vector
P=Path(__file__).resolve().parent
bpy.ops.wm.open_mainfile(filepath=str(P/'garage-east-infill-skylights.blend'))
s=bpy.context.scene
bpy.ops.object.camera_add(location=(-11,-13,10))
c=bpy.context.object;c.name='Southwest roof review';c.rotation_euler=(Vector((2.2,2.1,3.1))-c.location).to_track_quat('-Z','Y').to_euler();c.data.lens=48;s.camera=c
s.render.resolution_x=1100;s.render.resolution_y=900;s.render.resolution_percentage=100;s.cycles.samples=16
s.render.filepath=str(P/'04-southwest-draft.png')
bpy.ops.wm.save_as_mainfile(filepath=str(P/'garage-east-infill-skylights.blend'))
bpy.ops.render.render(write_still=True)
