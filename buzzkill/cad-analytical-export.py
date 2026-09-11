"""Export intended axes from native construction data, never mesh PCA or global snapping."""
import math,json,hashlib
from pathlib import Path
I=25.4

def export_analytical(d,reg,root,loft_data):
 import FreeCAD as A
 def shape(o):
  s=o.Shape.copy();s.Placement=o.getGlobalPlacement();return s
 def bb(o):
  b=shape(o).BoundBox;return [x/I for x in [b.XMin,b.YMin,b.ZMin,b.XMax,b.YMax,b.ZMax]]
 def xyz(v):return [v.x/I,v.y/I,v.z/I]
 def point(box,p):return xyz(box.getGlobalPlacement().multVec(A.Vector(*(v*I for v in p))))
 records=[];mapping={};byid={};trusses=reg['trusses'];members=reg['members'];meta={r['object']:r for r in members}
 topmap={};bottommap={v['bottom_object']:k for k,v in trusses.items()}
 def truss_for(r):
  n=r['object']
  if n in bottommap:return bottommap[n]
  if r['role']=='top_chord':return {'T-S top':'TS','T1 top':'T1','T-W top':'TW','T-E top':'TE','T-N top':'TN'}[r['id']]
  for k in ['TS','T1','TW','TE','TN']:
   if n.startswith('Frame'+k+'Web'):return k
  if n.startswith('TN'):return 'TN'
  if n.startswith('TW'):return 'TW'
  if 'T1' in n:return 'T1'
  return None
 def add(r,a,b,family,station_axis,basis,suffix='',extra=None):
  ident=r['id']+suffix;assert math.dist(a,b)>1e-7,(ident,'zero axis')
  rec={'id':ident,'object':r['object'],'truss':truss_for(r),'role':r['role'],'stage':r['stage'],'a':a,'b':b,'section_family':family,'section_description':r['section'],'cad_bounding_box_inches':bb(d.getObject(r['object'])),'station_axis':station_axis,'axis_source':basis,'length_inches':math.dist(a,b),'intended_joint_offsets':[]}
  if extra:rec.update(extra)
  records.append(rec);mapping.setdefault(r['object'],[]).append(ident);byid[ident]=rec
  return rec
 # All ordinary axes follow the known native primitive's design orientation.
 for r in members:
  o=d.getObject(r['object']);role=r['role'];n=o.Name
  if role=='top_chord':topmap[truss_for(r)]=n;continue
  if role in ['vertical','diagonal']:
   sk=o.Base;vertices=[sk.getGlobalPlacement().multVec(g.StartPoint) for g in sk.Geometry]
   assert len(vertices)==4,(n,len(vertices))
   shift=A.Vector(o.Dir);shift.normalize();shift*=o.LengthFwd.Value/2
   # full-frame-generator.web(): corners0/1 are the first cap, corners2/3 the second.
   a=xyz((vertices[0]+vertices[1])*.5+shift);b=xyz((vertices[2]+vertices[3])*.5+shift)
   k=truss_for(r);station='z' if role=='vertical' else trusses[k]['axis']
   add(r,a,b,'web',station,{'method':'Native closed Sketcher profile cap midpoints + half extrusion width','profile_object':sk.Name,'generator_function':'web / vertical / diagonal','profile_vertices_inches':[xyz(v) for v in vertices],'endpoint_pairs':[[0,1],[2,3]],'extrusion_midplane_shift_inches':xyz(shift)})
  elif role in ['column','upper_jamb','hanger']:
   stock=o.Base if o.TypeId=='Part::Cut' else o
   assert stock.TypeId=='Part::Box',(n,stock.TypeId)
   x=stock.Length.Value/I/2;y=stock.Width.Value/I/2;h=stock.Height.Value/I
   add(r,point(stock,[x,y,0]),point(stock,[x,y,h]),'hanger' if role=='hanger' else 'column','z',{'method':'Known vertical native stock axis','stock_object':stock.Name,'ground_post':point(stock,[x,y,0])[2]<1e-7})
  elif role=='chord':
   k=bottommap[n];axis=trusses[k]['axis'];lx=o.Length.Value/I;ly=o.Width.Value/I;hz=o.Height.Value/I/2
   a,b=([0,ly/2,hz],[lx,ly/2,hz]) if axis=='x' else ([lx/2,0,hz],[lx/2,ly,hz])
   add(r,point(o,a),point(o,b),'chord',axis,{'method':'Original native Part::Box axis and truss orientation','center_elevation_note':'115 inches for lower floor chords; permanent upper T1 is150.143248 inches.'})
  elif role in ['beam','future']:
   stock=d.getObject(n+'BottomFlange');assert stock is not None,n
   lx=stock.Length.Value/I;ly=stock.Width.Value/I;depth=d.getObject('OverlayParameters').BeamDepth.Value/I
   add(r,point(stock,[0,ly/2,depth/2]),point(stock,[lx,ly/2,depth/2]),'Wbeam','x',{'method':'Native generic I bottom flange plan axis plus half full beam depth','stock_object':stock.Name,'center_elevation_inches':116})
  elif role=='header':
   axis='y' if n=='TWBalconyHeader' else 'x';lx=o.Length.Value/I;ly=o.Width.Value/I;z=o.Height.Value/I/2
   a,b=([0,ly/2,z],[lx,ly/2,z]) if axis=='x' else ([lx/2,0,z],[lx/2,ly,z])
   add(r,point(o,a),point(o,b),'header',axis,{'method':'Native header box and explicitly defined opening span'})
  else:raise RuntimeError(('Unhandled structural member',r))
 # Top axes use the generator's exact roof planes intersected with the intended truss plane.
 for k,n in topmap.items():
  r=meta[n];tm=trusses[k];along=0 if tm['axis']=='x' else 1;cross=1-along;fixed=tm['fixed_coordinate_inches'];segments=[]
  for patch in tm['top_surface_patches']:
   poly=patch['plan_vertices_inches'];values=[]
   for p,q in zip(poly,poly[1:]+poly[:1]):
    dp=p[cross]-fixed;dq=q[cross]-fixed
    if abs(dp)<1e-7:values.append(p[along])
    if dp*dq<0:
     t=dp/(dp-dq);values.append(p[along]+t*(q[along]-p[along]))
   if len(values)<2 or max(values)-min(values)<1e-7:continue
   start,end=min(values),max(values);pl=patch['plane_z_ax_by_c'];pts=[]
   for u in [start,end]:
    x,y=(u,fixed) if along==0 else (fixed,u);pts.append([x,y,pl[0]*x+pl[1]*y+pl[2]-3])
   segments.append((start,end,pts,patch))
  segments.sort(key=lambda x:x[0]);assert segments
  for idx,(start,end,pts,patch) in enumerate(segments,1):
   panelstations=sorted(set(tm.get('panel_stations_inches',[])+tm.get('web_stations_inches',[])+tm.get('roof_and_panel_stations_inches',[])))
   add(r,pts[0],pts[1],'chord',tm['axis'],{'method':'Generator roof-plane polygon intersected with intended truss axis; centerline top minus3in','roof_plane_z_ax_by_c':patch['plane_z_ax_by_c'],'zone':patch['zone'],'top_depth_vertical_inches':6,'plan_polygon_inches':patch['plan_vertices_inches']},suffix=' / segment '+str(idx),extra={'segment_index':idx,'segment_station_interval_inches':[start,end],'suggested_panel_split_stations_inches':[u for u in panelstations if start<=u<=end]})
  assert abs(segments[0][0]-tm['span_inches'][0])<1e-6 and abs(segments[-1][1]-tm['span_inches'][1])<1e-6
  for left,right in zip(segments,segments[1:]):assert abs(left[1]-right[0])<1e-6,(k,'axis interval gap/overlap')
 assert set(mapping)==set(meta),set(meta)-set(mapping)
 # Project only onto an EXPLICITLY NAMED target, preserving its design station coordinate.
 # This creates an offset report, never a merged node, global nearest-neighbor link, or stiffness.
 def candidates(obj,p):
  out=[]
  for ident in mapping[obj]:
   m=byid[ident];c={'x':0,'y':1,'z':2}[m['station_axis']];den=m['b'][c]-m['a'][c];assert abs(den)>1e-8
   raw=(p[c]-m['a'][c])/den;t=max(0,min(1,raw));q=[m['a'][j]+t*(m['b'][j]-m['a'][j]) for j in range(3)]
   out.append({'member_id':ident,'object':obj,'point':q,'axis_fraction':t,'station_clamped':abs(raw-t)>1e-7,'offset_distance_inches':math.dist(p,q)})
  inside=[v for v in out if not v['station_clamped']];return inside or out
 def onaxis(obj,p):return min(candidates(obj,p),key=lambda v:v['offset_distance_inches'])
 connections=[]
 def relation(oa,pa,ob,pb,basis,source_endpoint=None):
  aa=onaxis(oa,pa);bbp=onaxis(ob,pb);offset=[b-a for a,b in zip(aa['point'],bbp['point'])]
  ident='J'+str(len(connections)+1).zfill(4)
  rec={'id':ident,'from':aa,'to':bbp,'source_endpoint':source_endpoint,'basis':basis,'offset_vector_inches':offset,'axis_gap_inches':math.dist(aa['point'],bbp['point']),'physical_solid_distance_inches':shape(d.getObject(oa)).distToShape(shape(d.getObject(ob)))[0]/I,'joint_behavior':None,'detail_status':'unresolved; solver must explicitly choose joint/offset treatment','coordinates_merged':False}
  target_candidates=candidates(ob,pb)
  if len(target_candidates)>1:rec['target_axis_candidates_at_station']=target_candidates;rec['candidate_selection']='Smallest offset among segments of the explicitly named CAD target; no node merging.'
  connections.append(rec)
  for endpoint,other in [(aa,bbp),(bbp,aa)]:byid[endpoint['member_id']]['intended_joint_offsets'].append({'connection_id':ident,'axis_fraction':endpoint['axis_fraction'],'own_point':endpoint['point'],'target_member_id':other['member_id'],'target_point':other['point'],'offset_vector_inches':[b-a for a,b in zip(endpoint['point'],other['point'])]})
  return rec
 pairs={}
 for c in reg['connection_checks']:pairs.setdefault(c['a'],[]).append(c['b'])
 for obj,targets in pairs.items():
  targets=list(dict.fromkeys(targets));m=byid[mapping[obj][0]]
  if m['role'] in ['vertical','diagonal','hanger']:
   assert len(targets)==2,(obj,targets)
   a,b=m['a'],m['b'];direct=onaxis(targets[0],a)['offset_distance_inches']+onaxis(targets[1],b)['offset_distance_inches'];reverse=onaxis(targets[1],a)['offset_distance_inches']+onaxis(targets[0],b)['offset_distance_inches']
   ordered=targets if direct<=reverse else targets[::-1]
   for end,p,target in zip(['a','b'],[a,b],ordered):relation(obj,p,target,p,'Explicit target from full-frame-generator connection list; endpoint ordering resolved only within these two named targets.',end)
  elif m['role']=='upper_jamb':relation(obj,m['b'],targets[0],m['b'],'Explicit upper-jamb to top-chord target from generator.','b')
  elif m['role']=='header':
   for target,p in zip(targets,[m['a'],m['b']]):relation(obj,p,target,p,'Explicit header end support from generator.')
  else:raise RuntimeError(('Unexpected connection source',obj))
 def link(oa,ob,p,basis):return relation(oa,p,ob,p,basis)
 def axis_point(obj,coord,z=115):
  m=byid[mapping[obj][0]];p=m['a'][:];c={'x':0,'y':1,'z':2}[m['station_axis']];p[c]=coord
  if c!=2:p[2]=z
  return p
 # Named column-to-member relationships from the established framing layout; no spatial discovery.
 col_targets={
 'ProposedColumnW1':['ProposedTS','ProposedTW',topmap['TS'],topmap['TW']],
 'ProposedColumnW2':['ProposedTW','ProposedT1Upper','ProposedT1Future',topmap['T1'],topmap['TW']],
 'ProposedColumnW3':['ProposedTW','ProposedB2Future',topmap['TW']],
 'ProposedColumnW4':['ProposedTW','ProposedTN',topmap['TW'],topmap['TN']],
 'ProposedColumnSW0':['ProposedTW','ProposedTSO',topmap['TW']],
 'ProposedColumnS1':['ProposedTSO'],
 'ProposedColumnS2':['ProposedTE','ProposedTSO',topmap['TE']],
 'ProposedColumnS3':['ProposedTS','ProposedTE',topmap['TS'],topmap['TE']],
 'ProposedColumnN2':['ProposedTE','ProposedTN',topmap['TE'],topmap['TN']],
 'ProposedNorthPostUW':['ProposedTN',topmap['TN']]}
 for col,targets in col_targets.items():
  cm=byid[mapping[col][0]]
  for target in targets:
   p=cm['b'][:];q=onaxis(target,p)['point'];p[2]=q[2]
   relation(col,p,target,q,'Explicit named column support in current framing layout; station and eccentricity retained.')
 # Bottom beam/chord crossings with differing center elevations kept as offsets.
 for cross,longs,ystation in [('ProposedTS',['ProposedTW','ProposedTE'],0),('ProposedTN',['ProposedTW','ProposedTE'],249),('ProposedTSO',['ProposedTW','ProposedTE'],-63),('ProposedT1Future',['ProposedTW','ProposedTE'],69.75),('ProposedB2Future',['ProposedTW','ProposedTE'],185)]:
  for lng,x in zip(longs,[-32,224.25]):link(cross,lng,[x,ystation,byid[mapping[cross][0]]['a'][2]],'Explicit transverse beam/chord meeting longitudinal bottom chord; offsets retained.')
 # Roof-chord intersections are explicit truss junctions.
 for k,y in [('TS',0),('T1',69.75),('TN',249)]:
  for side,x in [('TW',-32),('TE',224.25)]:
   p=[x,y,0];p=onaxis(topmap[k],p)['point'];link(topmap[k],topmap[side],p,'Explicit crossing of transverse and longitudinal roof top chords.')
 # Raised T1 lower chord ends meet the side-truss verticals at the same69.75 station.
 for side,x in [('TW',-32),('TE',224.25)]:
  matches=[m for m in records if m['truss']==side and m['role']=='vertical' and abs(m['a'][1]-69.75)<1e-6]
  assert len(matches)==1
  link('ProposedT1Upper',matches[0]['object'],[x,69.75,150.143248],'T1 raised bottom chord endpoint meets explicitly matching side-truss panel vertical at y69.75.')
 # West opening header terminates at vertical inner faces; axes differ by1in longitudinally.
 for station,end in [(185,'a'),(247,'b')]:
  matches=[m for m in records if m['truss']=='TW' and m['role']=='vertical' and abs(m['a'][1]-station)<1e-6 and m['a'][2]<120]
  assert len(matches)==1
  header=byid[mapping['TWBalconyHeader'][0]];link('TWBalconyHeader',matches[0]['object'],header[end],'Explicit west opening header jamb vertical;1in face-to-axis offset retained.')
 seams=[]
 for k,n in topmap.items():
  ids=mapping[n]
  for left,right in zip(ids,ids[1:]):
   a=byid[left]['b'];b=byid[right]['a'];offset=[y-x for x,y in zip(a,b)]
   seams.append({'truss':k,'object':n,'left_member_id':left,'right_member_id':right,'left_point':a,'right_point':b,'offset_vector_inches':offset,'gap_inches':math.dist(a,b),'same_native_fused_solid':True,'joint_behavior':None,'note':'Plane kink or preserved main/cap vertical step. No artificial connecting bar or rigid joint added.'})
 # Native profile axes must lie within each corresponding CAD solid bounding box.
 for m in records:
  bounds=m['cad_bounding_box_inches']
  for p in [m['a'],m['b']]:assert all(bounds[i]-1e-6<=p[i]<=bounds[i+3]+1e-6 for i in range(3)),(m['id'],p,bounds)
 out={'schema_version':1,'request_id':'RENOVATED-LOFT-001','units':'inches','coordinate_system':{'x':'east','y':'north','z':'up','origin':'existing garage southwest floor datum'},'cad_snapshot':{'path':str(root/'Proposed-Garage.FCStd'),'sha256':hashlib.sha256((root/'Proposed-Garage.FCStd').read_bytes()).hexdigest()},'provenance':{'full_frame_generator_sha256':hashlib.sha256((root/'full-frame-generator.py').read_bytes()).hexdigest(),'axis_exporter_sha256':hashlib.sha256((root/'cad-analytical-export.py').read_bytes()).hexdigest(),'method':'Direct native stock axes, exact native Sketcher cap endpoint pairs, and generator roof-plane/panel metadata. No mesh PCA. No global nearest-neighbor snapping.'},'members':records,'object_to_member_ids':mapping,'native_structural_object_count':len(mapping),'analytical_segment_count':len(records),'connectivity':{'automatic_node_merging':False,'intended_connections':connections,'top_chord_plane_junctions':seams,'policy':'Relationships name their intended CAD targets. Axis offsets, finite-end clamps and branch alternatives are explicit. This file imposes no releases, rigid links, supports or stiffness. Parent solver must choose them. Other crossing lines are not implicitly joined.'},'truss_panelpoint_source':trusses,'floor':loft_data,'existing_objects_included':False,'strength_analysis_run':False,'section_sizes_status':'Geometric placeholders; not validated sizes. Wood joists require separate engineering.','unresolved':['Connection stiffness, releases, gussets and offsets','Column base restraint and foundations','Main/cap top-chord axis steps','Temporary stability and untriangulated rectangular bays','Joist hangers and bearing','Optional north ledge support','No material strengths or loads selected in this geometry export']}
 path=root/'optimization'/'cad-analytical-members.json';path.parent.mkdir(exist_ok=True);path.write_text(json.dumps(out,indent=2)+'\n');return out
