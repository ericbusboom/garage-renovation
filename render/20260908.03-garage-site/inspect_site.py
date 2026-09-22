import bpy
from mathutils import Vector
bpy.ops.wm.open_mainfile(filepath='/home/ros/garage-render/garage-site.blend')
s=bpy.context.scene;c=s.camera
frame=c.data.view_frame(scene=s)
for px,py in [(830,910),(824,897),(848,918)]:
 x=px/1800;y=1-py/1200
 left=min(v.x for v in frame);right=max(v.x for v in frame);bottom=min(v.y for v in frame);top=max(v.y for v in frame)
 d=c.matrix_world.to_quaternion()@Vector((left+(right-left)*x,bottom+(top-bottom)*y,frame[0].z)).normalized()
 hit,loc,normal,idx,obj,mat=s.ray_cast(bpy.context.evaluated_depsgraph_get(),c.location,d)
 print('HIT',px,py,obj.name if obj else None,loc[:],flush=True)
