import bpy,json,bmesh
from pathlib import Path
R=Path(__file__).resolve().parent
bpy.ops.wm.open_mainfile(filepath=str(R/'garage-site.blend'))
j=json.loads((R/'hip-cap-model.json').read_text())
c=bpy.data.collections['roof']
for o in list(c.objects):bpy.data.objects.remove(o,do_unlink=True)
for o in j['objects']:
 if o['group']!='roof':continue
 m=bpy.data.meshes.new(o['name']);m.from_pydata(o['vertices'],[],o['faces']);m.update()
 bm=bmesh.new();bm.from_mesh(m);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(m);bm.free()
 ob=bpy.data.objects.new(o['name'],m);c.objects.link(ob);ob.data.materials.append(bpy.data.materials[o['material']])
 mod=ob.modifiers.new('Edge highlight','BEVEL');mod.width=.002;mod.segments=2
s=bpy.context.scene;s.cycles.samples=96;s.cycles.use_denoising=True
s['roof_revision']='2026-09-08: 18 inch hip rise, 8 inch overhang and fascia; current model-renders geometry'
bpy.ops.wm.save_as_mainfile(filepath=str(R/'garage-site-hip-cap.blend'))
for cam,name in [('Garden approach photo-informed','site-garden'),('Garage southwest garden view','site-garage-angle')]:
 s.camera=bpy.data.objects[cam];s.render.filepath=str(R/(name+'-hip-cap.png'));bpy.ops.render.render(write_still=True)
 print('DONE '+name,flush=True)
