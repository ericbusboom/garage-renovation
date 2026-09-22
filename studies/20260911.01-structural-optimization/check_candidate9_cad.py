import os,sys,json
from pathlib import Path
sys.path.insert(0,'/opt/freecad-1.1.3/usr/lib')
import FreeCAD as A,Part
P=Path(__file__).resolve().parent
new=A.openDocument(str(P/'Garage-Candidate-9.FCStd'));old=A.openDocument(str(P.parent/'Existing-Garage.FCStd'))
names=[o['name'] for o in json.loads((P.parent/'existing-garage-analysis-mesh.json').read_text())['objects']]
parts=[o for o in new.Objects if hasattr(o,'MemberId')];assert len(parts)==121;assert all(o.Shape.isValid() for o in parts)
oldparts=[]
for name in names:
 o=old.getObject(name)
 if o and hasattr(o,'Shape') and not o.Shape.isNull():
  shape=o.Shape.copy();shape.Placement=o.getGlobalPlacement();oldparts.append((name,o.Label,shape))
assert len(oldparts)>90,len(oldparts)
def overlap(a,b):return a.XMin<b.XMax and a.XMax>b.XMin and a.YMin<b.YMax and a.YMax>b.YMin and a.ZMin<b.ZMax and a.ZMax>b.ZMin
clashes=[]
for o in parts:
 if o.ConstructionStage=='After old roof removal':continue
 for name,label,shape in oldparts:
  if not overlap(o.Shape.BoundBox,shape.BoundBox):continue
  vol=o.Shape.common(shape).Volume
  if vol>.01:clashes.append(dict(new_member=o.MemberId,existing=name,label=label,volume_cubic_inches=vol/25.4**3))
te=next(o for o in parts if o.MemberId=='T-E')
roofparts=[(name,label,shape) for name,label,shape in oldparts if any(t in name for t in ['GlobalDatumOutput','RidgeBoardOutput'])]
closest=min((te.Shape.distToShape(shape)[0]/25.4,name) for name,label,shape in roofparts)
r={'TE_min_distance_to_modeled_roof_framing_in':closest[0],'TE_nearest_existing_member':closest[1],'reopened_valid_members':len(parts),'existing_solids_compared':len(oldparts),'roof_first_solid_intersections':clashes,'limitations':'Existing roof cladding is not modeled; erection tolerances and access are not checked. Intersections at columns may require planned local openings; these are not automatically acceptable.'}
(P/'candidate9-clearance-check.json').write_text(json.dumps(r,indent=2));print(json.dumps(r),flush=True)
os._exit(0)
