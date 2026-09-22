import bpy
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parent
bpy.ops.wm.open_mainfile(filepath=str(R/'garage-site.blend'))
s=bpy.context.scene
c=bpy.data.objects['House and garden context'];c.name='Garage southwest garden view';c.location=(-5.1,-8.6,4.1);c.rotation_euler=(Vector((.9,1.7,2.65))-c.location).to_track_quat('-Z','Y').to_euler();c.data.lens=26
s.camera=c;s.render.filepath=str(R/'site-garage-angle.png')
bpy.ops.wm.save_as_mainfile(filepath=str(R/'garage-site.blend'))
bpy.ops.render.render(write_still=True)
