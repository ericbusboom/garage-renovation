import bpy,json
from pathlib import Path
R=Path(__file__).resolve().parent
bpy.ops.wm.open_mainfile(filepath=str(R/'backyard-existing.blend'))
s=bpy.context.scene
assert s.get('source_parts')==899
assert not any('proposal' in c.name.lower() for c in bpy.data.collections)
used_images={n.image for m in bpy.data.materials if m.use_nodes for n in m.node_tree.nodes if n.type=='TEX_IMAGE' and n.image}
assert all(i.packed_file for i in used_images)
assert len([m for m in bpy.data.materials if m.name.startswith('PHOTO /')])==6
assert all(n in bpy.data.objects for n in ['01 / Whole backyard','02 / Patio toward garage','03 / Conversation area','04 / House and gardens'])
ps=[o for o in bpy.data.objects if o.type=='MESH' and any(c.name in ['pergola','pergola_roof'] for c in o.users_collection)]
y=min((o.matrix_world@v.co).y for o in ps for v in o.data.vertices)
assert abs(y-(-7.2+8*.3048))<1e-5
report={'verified_native_reopen':True,'source_revision':8,'source_parts':899,'photo_materials':6,'used_images':len(used_images),'all_used_images_packed':True,'proposal_collections':0,'pergola_south_y_m':y,'fence_to_pergola_ft':8,'render_engine':s.render.engine,'samples':s.cycles.samples,'resolution':[s.render.resolution_x,s.render.resolution_y],'render_geometry_refinements':s.get('render_geometry_refinements'),'cameras':4}
(R/'scene-validation.json').write_text(json.dumps(report,indent=2));print(json.dumps(report),flush=True)
