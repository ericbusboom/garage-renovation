import bpy
from pathlib import Path
R=Path(__file__).resolve().parent
bpy.ops.wm.open_mainfile(filepath=str(R/'garage-site.blend'))
o=bpy.data.objects['House low rear wing'];o.dimensions.x=9.2;o.location.x=-1.4
bpy.context.view_layer.update()
s=bpy.context.scene;s.camera=bpy.data.objects['House and garden context']
s.render.filepath=str(R/'site-house-context.png')
bpy.ops.wm.save_as_mainfile(filepath=str(R/'garage-site.blend'))
bpy.ops.render.render(write_still=True)
