import bpy
from pathlib import Path
from mathutils import Vector
P=Path(__file__).resolve().parent
bpy.ops.wm.open_mainfile(filepath=str(P/'garage-connected-frame.blend'))
s=bpy.context.scene
bpy.ops.object.camera_add(location=(-11,-13,10))
c=bpy.context.object;c.name='Southwest roof review';c.rotation_euler=(Vector((2.2,2.1,3.1))-c.location).to_track_quat('-Z','Y').to_euler();c.data.lens=48;s.camera=c
s.render.resolution_x=1100;s.render.resolution_y=900;s.render.resolution_percentage=100;s.cycles.samples=16
s.render.filepath=str(P/'04-southwest-draft.png')
bpy.ops.wm.save_as_mainfile(filepath=str(P/'garage-connected-frame.blend'))
bpy.ops.render.render(write_still=True)

# Verify saved object geometry against the current COMPAS scene, then stamp provenance.
import json,hashlib
data=json.loads((P/'scene-mesh.json').read_text())
max_error=0.;frame_count=0
for e in data['objects']:
 ob=bpy.data.objects.get(e['name'])
 assert ob is not None,e['name']
 assert len(ob.data.vertices)==len(e['vertices']),e['name']
 for vertex,expected in zip(ob.data.vertices,e['vertices']):
  error=(vertex.co-Vector([x*.0254 for x in expected])).length
  max_error=max(max_error,error)
  assert error<1e-5,(e['name'],error)
 if 'member_id' in e:
  ob['member_id']=e['member_id'];ob['joint_ids']=json.dumps(e['joint_ids']);frame_count+=1
assert frame_count==len(json.loads((P/'frame-spec.json').read_text())['members']),frame_count
assert not any(ob.get('member_id') in ('BR-E-ground-1','BR-E-ground-2') for ob in bpy.data.objects)
s['source_scene_sha256']=hashlib.sha256((P/'scene-mesh.json').read_bytes()).hexdigest()
s['source_spec_sha256']=hashlib.sha256((P/'frame-spec.json').read_bytes()).hexdigest()
bpy.ops.wm.save_as_mainfile(filepath=str(P/'garage-connected-frame.blend'))
report=json.loads((P/'render-validation.json').read_text())
report.update(source='Exact COMPAS scene geometry in metres; bevel finish only',source_scene_sha256=s['source_scene_sha256'],source_spec_sha256=s['source_spec_sha256'],verified_objects=len(data['objects']),verified_frame_members=frame_count,max_base_mesh_error_metres=max_error,views=['01-southeast-draft.png','02-northeast-draft.png','03-east-rafter-study.png','04-southwest-draft.png'])
(P/'render-validation.json').write_text(json.dumps(report,indent=2))
print('VERIFIED',len(data['objects']),'objects;',frame_count,'frame members; max error',max_error,flush=True)
