import bpy
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parent
bpy.ops.wm.open_mainfile(filepath=str(R/'backyard-proposed-hip-cap.blend'))
s=bpy.context.scene;c=bpy.data.objects['PROPOSED / Elevated southwest'];c.location=(-10,0,12);c.rotation_euler=(Vector((1,2,2.5))-c.location).to_track_quat('-Z','Y').to_euler();c.data.lens=26;s.camera=c
s.render.filepath=str(R/'03-proposed-garage-context.png')
bpy.ops.wm.save_as_mainfile(filepath=str(R/'backyard-proposed-hip-cap.blend'))
bpy.ops.render.render(write_still=True)
