"""Current CAD mesh -> round-tripped COMPAS mesh bundle -> interactive 3D review."""
import json,hashlib
from pathlib import Path
import numpy as np
from compas.datastructures import Mesh
from compas.data import json_dump,json_load
import plotly.graph_objects as go
ROOT=Path(__file__).resolve().parents[1];P=ROOT/'roof-studies/square-upper-west';OUT=P/'compas';OUT.mkdir(exist_ok=True)
src=P/'connected-frame/scene-mesh.json';raw=json.loads(src.read_text());objects=[]
for e in raw['objects']:
 mesh=Mesh.from_vertices_and_faces(e['vertices'],e['triangles'])
 if not mesh.is_valid():
  vs=[e['vertices'][i] for f in e['triangles'] for i in f]
  mesh=Mesh.from_vertices_and_faces(vs,[[i,i+1,i+2] for i in range(0,len(vs),3)])
 assert mesh.is_valid(),e['name']
 objects.append({**{k:e[k] for k in ['name','group','material']},'mesh':mesh})
# Include the same clipped upper-post portions in both truss visibility groups.
# West originals belong to Columns; east copies already belong to MatchedEastTruss.
# Reflect only the verified upper-post copies back into the west comparison group.
matching=json.loads((P/'matching-trusses.json').read_text())
upper_names={pair['east']:pair['west'] for pair in matching['pairs'] if pair['upper_post_only']}
for o in list(objects):
 if o['group']=='MatchedEastTruss' and o['name'] in upper_names:
  vertices,faces=o['mesh'].to_vertices_and_faces()
  reflected=[[matching['west_axis_x']+matching['east_axis_x']-x,y,z] for x,y,z in vertices]
  mesh=Mesh.from_vertices_and_faces(reflected,[list(reversed(f)) for f in faces])
  assert mesh.is_valid()
  objects.append({'name':upper_names[o['name']]+' · upper truss portion','group':'WestTrussUpperPosts','material':o['material'],'mesh':mesh})
bundle={'units':'inches','source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'objects':objects,'matching_trusses':json.loads((P/'matching-trusses.json').read_text())}
connected=json_load(P/'connected-frame/frame.compas.json')
bundle.update(joint_graph=connected['joint_graph'],frame_model=connected['model'],specification=connected['specification'])
json_dump(bundle,OUT/'current-frame.compas.json');bundle=json_load(OUT/'current-frame.compas.json')
# Check every displayed pair after COMPAS serialization, independent of vertex order.
by_name={o['name']:o for o in bundle['objects']}
mirror_errors=[]
for pair in matching['pairs']:
 west_name=pair['west']+(' · upper truss portion' if pair['upper_post_only'] else '')
 w=np.array(by_name[west_name]['mesh'].vertices_attributes('xyz'))
 e=np.array(by_name[pair['east']]['mesh'].vertices_attributes('xyz'))
 e[:,0]=matching['west_axis_x']+matching['east_axis_x']-e[:,0]
 distances=np.linalg.norm(w[:,None,:]-e[None,:,:],axis=2)
 error=float(max(distances.min(axis=0).max(),distances.min(axis=1).max()))
 assert error<1e-6,(west_name,error)
 mirror_errors.append({'west':west_name,'max_mirrored_vertex_error_in':error})
def category(o):
 g=o['group']
 if g=='MatchedEastTruss':return 'East truss · matches west'
 if g in ['Truss_TW','WestMarkupFraming','WestTrussUpperPosts']:return 'West truss · revised'
 if g=='EastRoofRafters':return 'East roof rafters'
 if g=='EastSupportFrame':return 'East beam and posts'
 if g=='LoftJoists':return 'Loft joists'
 if g=='Columns':return 'Columns'
 if g=='Bracing':return 'Wall and roof bracing'
 if g.startswith('Truss') or g=='LoftSteel':return 'Crossbeams and transverse trusses'
 if g in ['SolarRoof','Skylights','Clerestory']:return 'Solar panels and clerestory'
 if g in ['HipRoofCap','RoofEaves','RoofTrim','EastSetbackRoof']:return 'Roof, fascia and soffits'
 if g in ['ExistingGarage']:return 'Existing garage'
 if g in ['InteriorMetalPanels','GroundFloorExtensionWalls','DoorsWindows','Context']:return 'Wall cladding and infill'
 return 'Floor and secondary context'
member_by_name={m.get('display_name',m['source_name']):(mid,m) for mid,m in bundle['specification']['members'].items()}
def elevation_faces(o):
 mid,m=member_by_name.get(o['name'],('',{}))
 g=m.get('group',o['group'])
 faces=[]
 if g=='Truss_TN' or mid in ('W.W4','E.W4','N2','N1 / U-W') or mid.startswith('BR-N-'):faces.append('north')
 if g in ('Truss_TS','Truss_Other') or mid in ('W.W1','W.SW0','E.W1','E.SW0','S1','S2','S3') or mid.startswith('BR-S-'):faces.append('south')
 xyz=np.array(o['mesh'].vertices_attributes('xyz'))
 if xyz[:,0].max()<=matching['west_axis_x']+6 or g=='WestTrussUpperPosts':faces.append('west')
 if xyz[:,0].min()>=matching['east_axis_x']-6:faces.append('east')
 return tuple(faces)
categories={}
for o in bundle['objects']:categories.setdefault((category(o),elevation_faces(o)),[]).append(o)
colors={'East truss · matches west':'#b47735','West truss · revised':'#315e7a','East roof rafters':'#bda477','East beam and posts':'#367d7f','Columns':'#768790','Wall and roof bracing':'#7c8c94','Crossbeams and transverse trusses':'#85939b','Solar panels and clerestory':'#467e94','Roof, fascia and soffits':'#b0b9b9','Existing garage':'#d8d4c9','Wall cladding and infill':'#bac8cb','Floor and secondary context':'#bcad93','Loft joists':'#bcad93'}
fig=go.Figure();names=[];trace_faces=[]
for (name,faces),obs in categories.items():
 vs=[];fs=[];labels=[]
 for o in obs:
  v,f=o['mesh'].to_vertices_and_faces();n=len(vs);vs.extend(v);fs.extend([[n+i for i in face] for face in f]);labels.extend([o['name']]*len(v))
 xyz=np.array(vs);tri=np.array(fs)
 frame=name in list(colors)[:7] or name=='Loft joists'
 fig.add_trace(go.Mesh3d(x=xyz[:,0],y=xyz[:,1],z=xyz[:,2],i=tri[:,0],j=tri[:,1],k=tri[:,2],text=labels,name=name,color=colors[name],showlegend=True,visible=True if frame else 'legendonly',flatshading=True,hovertemplate='%{text}<br>X %{x:.2f} · Y %{y:.2f} · Z %{z:.2f} in<extra></extra>'))
 names.append(name);trace_faces.append(faces)
# Light context derived from the existing wall cores and slab, not a guessed box.
# Keep creases and boundary edges; suppress tessellation diagonals on flat faces.
ghost_name='Existing ground floor · ghost'
ghost_objects=[o for o in bundle['objects'] if o['group']=='ExistingGarage' and
               (o['name'].endswith('wall core') or o['name']=='Existing slab reference')]
verts=[];triangles=[];edge_xyz=[[],[],[]]
for o in ghost_objects:
 v,f=o['mesh'].to_vertices_and_faces();offset=len(verts);verts.extend(v)
 triangles.extend([[offset+i for i in face] for face in f])
 edge_faces={}
 for face in f:
  points=np.array([v[i] for i in face]);normal=np.cross(points[1]-points[0],points[2]-points[0]);length=np.linalg.norm(normal)
  if length<1e-10:continue
  normal=normal/length
  for a,b in zip(face,face[1:]+face[:1]):
   key=tuple(sorted((tuple(round(c,7) for c in v[a]),tuple(round(c,7) for c in v[b]))))
   edge_faces.setdefault(key,[]).append(normal)
 for (a,b),normals in edge_faces.items():
  if len(normals)>1 and all(abs(np.dot(normals[0],n))>0.9999 for n in normals[1:]):continue
  for i in range(3):edge_xyz[i].extend([a[i],b[i],None])
v=np.array(verts);f=np.array(triangles)
fig.add_trace(go.Mesh3d(x=v[:,0],y=v[:,1],z=v[:,2],i=f[:,0],j=f[:,1],k=f[:,2],
 name=ghost_name,legendgroup='existing-ghost',showlegend=False,visible=True,
 color='#8da4ad',opacity=.065,flatshading=True,hoverinfo='skip'))
names.append(ghost_name)
fig.add_trace(go.Scatter3d(x=edge_xyz[0],y=edge_xyz[1],z=edge_xyz[2],mode='lines',
 line=dict(color='rgba(93,119,131,0.38)',width=1.5),name=ghost_name,legendgroup='existing-ghost',
 visible=True,hoverinfo='skip'))
names.append(ghost_name)
joint_graph=bundle['joint_graph'];joint_keys=list(joint_graph.nodes());joint_xyz=np.array([joint_graph.node_coordinates(n) for n in joint_keys])
fig.add_trace(go.Scatter3d(x=joint_xyz[:,0],y=joint_xyz[:,1],z=joint_xyz[:,2],mode='markers',text=[n+'<br>'+', '.join(joint_graph.node_attribute(n,'members') or []) for n in joint_keys],name='Shared joints',visible='legendonly',marker=dict(size=3,color='#d34a31'),hovertemplate='%{text}<extra></extra>'))
names.append('Shared joints')
frame=[True if n in list(colors)[:7] or n in ('Loft joists',ghost_name) else 'legendonly' for n in names]
trusses=[True if n in list(colors)[:2] or n==ghost_name else 'legendonly' for n in names]
exterior=[True if n not in ['Floor and secondary context','Shared joints',ghost_name] else 'legendonly' for n in names]
# One model, six cameras. No separately cached elevation geometry.
fig.update_layout(
 scene=dict(aspectmode='data',
   xaxis=dict(range=[-60,270],visible=False),
   yaxis=dict(range=[-80,280],visible=False),
   zaxis=dict(range=[-5,265],visible=False),
   bgcolor='#f5f3ec',dragmode='turntable',
   camera=dict(eye=dict(x=-1.35,y=-1.43,z=.87))),
 paper_bgcolor='#f5f3ec',plot_bgcolor='#f5f3ec',
 margin=dict(l=0,r=0,t=0,b=0,autoexpand=False),autosize=True,showlegend=False)
review={'names':names,'colors':[colors.get(n) for n in names],
 'meshIndices':[i for i,n in enumerate(names) if n in colors],
 'elevationFaces':trace_faces,'ghostName':ghost_name,'presets':{'frame':frame,'trusses':trusses,'exterior':exterior}}
controls=(ROOT/'compas-study/frame_view_controls.js').read_text()
plot=fig.to_html(include_plotlyjs=True,full_html=False,div_id='frame-plot',
 default_width='100%',default_height='100%',
 config={'displayModeBar':False,'displaylogo':False,'responsive':True,'scrollZoom':True},
 post_script='window.frameReview='+json.dumps(review)+';\n'+controls)
template=(ROOT/'compas-study/frame_view_template.html').read_text()
html=template.replace('<!-- FRAME_PLOT -->',plot).replace('{{MEMBER_COUNT}}',str(len(bundle['specification']['members'])))
(OUT/'current-frame-3d.html').write_text(html)
(OUT/'validation.json').write_text(json.dumps({'ghost_context':{'source_objects':[o['name'] for o in ghost_objects],'surface_opacity':.065,'outline_opacity':.38,'default_visible':True},'roundtrip_mesh_count':len(bundle['objects']),'source_sha256':bundle['source_sha256'],'matched_member_pairs':len(bundle['matching_trusses']['pairs']),'connectivity_audit':json.loads((P/'connected-frame/connectivity-audit.json').read_text()),'valid_compas_meshes':True,'displayed_truss_mirror_checks':mirror_errors},indent=2))
print('Saved COMPAS model and viewer:',OUT)
