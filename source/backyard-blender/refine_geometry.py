"""Render-only refinement: thin curved strap leaves and resolve coplanar paving overlaps."""
import bpy,bmesh,math
from mathutils import Vector
from pathlib import Path
R=Path(__file__).resolve().parent
def refine():
 for o in list(bpy.data.objects):
  if o.type!='MESH':continue
  if o.name.startswith('Burgundy strap leaf') and not o.get('curved_ribbon'):
   v=[x.co.copy() for x in o.data.vertices];base=(v[0]+v[1])/2;tip=v[3];control=v[2]*2-(base+tip)*.5
   direction=Vector((tip.x-base.x,tip.y-base.y,0)).normalized();side=Vector((-direction.y,direction.x,0));verts=[];faces=[]
   for angle,scale in [(0,1),(.12,.83),(-.13,.92)]:
    start=len(verts)
    for i in range(17):
     t=i/16;q=(1-t)**2*base+2*(1-t)*t*control+t*t*tip;delta=(q-base)*scale;q=base+Vector((delta.x*math.cos(angle)-delta.y*math.sin(angle),delta.x*math.sin(angle)+delta.y*math.cos(angle),delta.z));w=.032*math.sin(math.pi*t)**.65
     verts.extend([q-side*w,q+side*w])
    faces.extend([(start+2*i,start+2*i+1,start+2*i+3,start+2*i+2) for i in range(16)])
   old=o.data;me=bpy.data.meshes.new(o.name+' curved leaf mesh');me.from_pydata(verts,[],faces);me.update()
   for m in old.materials:me.materials.append(m)
   o.data=me;o['curved_ribbon']=True
   for p in me.polygons:p.use_smooth=True
 paths=[o for o in bpy.data.objects if o.type=='MESH' and any(c.name=='paths' for c in o.users_collection) and any(s in o.name.lower() for s in ['access path','garden flagstone','shelter access'])]
 for i,o in enumerate(paths):
  if o.get('paving_overlap_resolved'):continue
  o.location.z+=.00015*(i+1)
  bm=bmesh.new();bm.from_mesh(o.data);bm.normal_update();bmesh.ops.reverse_faces(bm,faces=[f for f in bm.faces if f.normal.z<0]);bm.to_mesh(o.data);bm.free();o['paving_overlap_resolved']=True
 bpy.context.scene['render_geometry_refinements']='Curved tapered red strap leaves within original plant positions; sub-centimetre separation of overlapping path meshes to avoid ray-tracing artifacts.'
if __name__=='__main__':
 bpy.ops.wm.open_mainfile(filepath=str(R/'backyard-existing.blend'));refine();bpy.ops.wm.save_as_mainfile(filepath=str(R/'backyard-existing.blend'))
 s=bpy.context.scene;s.cycles.samples=32;s.render.resolution_percentage=60;s.camera=bpy.data.objects['02 / Patio toward garage'];s.render.filepath=str(R/'02-detail-check.png');bpy.ops.render.render(write_still=True);print('DETAIL_REFINEMENT_COMPLETE',flush=True)
