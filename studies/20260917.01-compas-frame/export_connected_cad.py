"""Export the exact COMPAS scene meshes as closed FreeCAD solids; verify all frame contacts."""
import os,json,sys,hashlib
from pathlib import Path
os.environ['QT_QPA_PLATFORM']='offscreen'
import FreeCAD as A,Part
P=Path(sys.argv[1]);data=json.loads((P/'scene-mesh.json').read_text());spec=json.loads((P/'frame-spec.json').read_text())
d=A.newDocument('GarageConnectedFrame');groups={};members={};member_data={};objects=[]
for e in data['objects']:
 faces=[]
 for face in e['triangles']:
  pts=[A.Vector(*[c*25.4 for c in e['vertices'][i]]) for i in face]
  if (pts[1]-pts[0]).cross(pts[2]-pts[0]).Length<1e-8:continue
  faces.append(Part.Face(Part.makePolygon(pts+[pts[0]])))
 shell=Part.makeShell(faces)
 # CAD context may contain multiple independent shells; these remain tessellated context.
 sh=Part.makeSolid(shell) if shell.isClosed() else Part.makeCompound(faces)
 if 'member_id' in e:
  assert shell.isClosed() and sh.isValid() and abs(sh.Volume)>1e-6,e['name']
  members[e['member_id']]=sh;member_data[e['member_id']]=e
 o=d.addObject('PartDesign::Feature','ConnectedMember' if 'member_id' in e else 'Envelope');o.Label=e['name'];o.Shape=sh
 g=e['group']
 if g not in groups:groups[g]=d.addObject('App::DocumentObjectGroup',g)
 groups[g].addObject(o)
 if 'member_id' in e:
  for name,value in [('MemberId',e['member_id']),('JointIds',json.dumps(e['joint_ids'])),('SourceSpecification','frame-spec.json / COMPAS')]:
   o.addProperty('App::PropertyString',name);setattr(o,name,value)
 objects.append(o)
# Independent solid checks against the explicitly declared per-end connection schedule.
import csv
rows=list(csv.DictReader((P/'member-end-audit.csv').open()));checks=[]
for row in rows:
 if row['status']!='connected':continue
 own=members[row['member']];targets=row['connected_to'].split('; ')
 endpoint=member_data[row['member']][row['end']]
 terminal=own.common(Part.makeSphere(.1*25.4,A.Vector(*[v*25.4 for v in endpoint])))
 assert not terminal.isNull() and terminal.Volume>0,(row['member'],row['end'],'empty terminal region')
 gap=min(terminal.distToShape(members[t])[0]/25.4 for t in targets)
 assert gap<1e-5,(row['member'],row['end'],gap)
 checks.append(dict(member=row['member'],end=row['end'],minimum_solid_gap_in=gap))
d.recompute();d.saveAs(str(P/'garage-connected-frame.FCStd'));Part.export(objects,str(P/'garage-connected-frame.step'))
(P/'solid-contact-audit.json').write_text(json.dumps({'source_scene_sha256':hashlib.sha256((P/'scene-mesh.json').read_bytes()).hexdigest(),'spec_sha256':hashlib.sha256((P/'frame-spec.json').read_bytes()).hexdigest(),'frame_solids':len(members),'connected_ends_checked':len(checks),'max_solid_gap_in':max(r['minimum_solid_gap_in'] for r in checks),'checks':checks},indent=2))
print('Saved connected CAD:',len(members),'frame solids;',len(checks),'end-contact checks passed')
