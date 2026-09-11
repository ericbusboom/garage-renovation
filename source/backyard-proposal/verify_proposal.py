import bpy,json,hashlib
from pathlib import Path
R=Path(__file__).resolve().parent
def signatures():
 result={}
 for o in bpy.data.objects:
  if o.type!='MESH':continue
  vals=[tuple(row) for row in o.matrix_world]+[tuple(v.co) for v in o.data.vertices]
  result[o.name]=hashlib.sha256(repr(vals).encode()).hexdigest()
 return result
bpy.ops.wm.open_mainfile(filepath=str(R/'backyard-existing.blend'));base=signatures()
removed={o.name for o in bpy.data.collections['garage_roof'].objects}
bpy.ops.wm.open_mainfile(filepath=str(R/'backyard-proposed-hip-cap.blend'));new=signatures()
assert all(new.get(n)==h for n,h in base.items() if n not in removed)
assert not any(n in new for n in removed)
assert all('PROPOSED / Hip cap '+n in new for n in ['north','south','east','west'])
images={n.image for m in bpy.data.materials if m.use_nodes for n in m.node_tree.nodes if n.type=='TEX_IMAGE' and n.image}
assert all(i.packed_file for i in images)
r=json.loads((R/'validation.json').read_text());r.update({'native_reopen_verified':True,'baseline_meshes_preserved':len(base)-len(removed),'packed_texture_images':len(images),'all_textures_packed':True,'four_hip_faces_verified':True});(R/'validation.json').write_text(json.dumps(r,indent=2));print(json.dumps(r),flush=True)
