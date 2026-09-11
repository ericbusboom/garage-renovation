import bpy,bmesh,json,hashlib
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parent
bpy.ops.wm.open_mainfile(filepath=str(R/'backyard-existing.blend'))
s=bpy.context.scene
# Both source models use metres, same southwest garage origin and orientation.
removed=[]
for c in list(bpy.data.collections):
 if c.name=='garage_roof':
  for o in list(c.objects):removed.append(o.name);bpy.data.objects.remove(o,do_unlink=True)
# Keep the surveyed/reviewed lower garage, shelter and entire backyard intact.
j=json.loads((R/'garage-model.json').read_text())
def rgb(h):
 def lin(v):return v/12.92 if v<=.04045 else ((v+.055)/1.055)**2.4
 return tuple(lin(int(h[i:i+2],16)/255) for i in [1,3,5])+(1,)
mats={}
for name,(hx,metal,rough) in j['materials'].items():
 m=bpy.data.materials.new('PROPOSED / '+name);m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=rgb(hx);p.inputs['Metallic'].default_value=metal;p.inputs['Roughness'].default_value=rough
 if name in ['roof','pv']:p.inputs['Coat Weight'].default_value=.35
 mats[name]=m
cols={};added=[]
for o in j['objects']:
 if o['group'] in ['site','existing','outbuilding']:continue
 g='PROPOSED / '+o['group']
 if g not in cols:
  cols[g]=bpy.data.collections.new(g);s.collection.children.link(cols[g])
 m=bpy.data.meshes.new(o['name']);m.from_pydata(o['vertices'],[],o['faces']);m.update();bm=bmesh.new();bm.from_mesh(m);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(m);bm.free()
 ob=bpy.data.objects.new('PROPOSED / '+o['name'],m);cols[g].objects.link(ob);ob.data.materials.append(mats[o['material']]);added.append(ob.name)
 mod=ob.modifiers.new('Edge highlights','BEVEL');mod.width=.002;mod.segments=2
 if o['group']=='frame' and o['material']=='truss':ob.hide_render=True;ob.hide_set(True)
s['proposal_basis']='Current hip-cap garage placed in supplied Backyard-Blender-Package.zip baseline. Shared metre coordinates; original garage roof removed; lower walls and all site context retained.'
s['hip_cap_rise_inches']=18;s['hip_cap_overhang_inches']=8
# Keep reviewed yard cameras and lighting; raise garage-facing aim to include the loft.
def cam(name,pos,target,lens=35,ortho=None):
 bpy.ops.object.camera_add(location=pos);c=bpy.context.object;c.name=name;c.rotation_euler=(Vector(target)-c.location).to_track_quat('-Z','Y').to_euler();c.data.lens=lens
 if ortho:c.data.type='ORTHO';c.data.ortho_scale=ortho
 return c
cameras=[(bpy.data.objects['01 / Whole backyard'],'01-proposed-backyard-overview'),(cam('PROPOSED / Patio to garage',(-6.3,-12,3.8),(.7,1.6,3.1),26),'02-proposed-patio-to-garage'),(cam('PROPOSED / Elevated southwest',(-10,0,12),(1,2,2.5),26),'03-proposed-garage-context')]
s.render.engine='CYCLES';s.cycles.device='CPU';s.cycles.samples=80;s.cycles.use_denoising=True;s.cycles.adaptive_threshold=.035;s.render.resolution_x=1800;s.render.resolution_y=1350;s.render.resolution_percentage=100
bpy.ops.file.pack_all();s.camera=cameras[0][0]
bpy.ops.wm.save_as_mainfile(filepath=str(R/'backyard-proposed-hip-cap.blend'))
report={'source':'Backyard-Blender-Package.zip','source_blend_sha256':hashlib.sha256((R/'backyard-existing.blend').read_bytes()).hexdigest(),'removed':removed,'added_objects':len(added),'hip_cap':j['basis']['hip_cap'],'transform':'identity; metres, X east / Y north / Z up','retained':'all baseline objects except garage_roof','cameras':[c.name for c,_ in cameras]}
(R/'validation.json').write_text(json.dumps(report,indent=2))
for c,n in cameras:
 s.camera=c;s.render.filepath=str(R/(n+'.png'));bpy.ops.render.render(write_still=True);print('DONE '+n,flush=True)
