#!/usr/bin/env python3
"""Prepare nominal roof member axes only; never modify FCStd files.
No stock dimensions are inferred. Run with system Python.
"""
import json, hashlib
from pathlib import Path
from datetime import datetime, timezone
ROOT=Path(__file__).resolve().parent
p=json.loads((ROOT/'existing-parameters.json').read_text())
w,l,z=p['width'],p['length'],p['wall_height']
ridge_length=18.0; rise=60.0; south=(l-ridge_length)/2; north=(l+ridge_length)/2
params={
 'request_id':'EXISTING-ROOF-FRAMING-001','units':'inches','status':'layout_prepared_awaiting_sections',
 'core_width':w,'core_length':l,'wall_top':z,'ridge_length':ridge_length,'rise_approximate':rise,
 'ridge_south':[w/2,south,z+rise],'ridge_north':[w/2,north,z+rise],
 'first_station_from_each_corner':16.0,'nominal_station_spacing':24.0,
 'available_board_face_widths':[5.0,5.5],'board_thickness':None,'board_orientation':None,
 'member_face_width_assignment':None,'hip_and_ridge_section_confirmation':None,
 'soffit_projection':3.5,'soffit_thickness':None,'soffit_top_approximate':z,
 'fascia_height':3.5,'fascia_thickness':0.75,'fascia_direction':'upward from soffit; outboard attachment',
 'roof_covering_overhang_past_fascia':1.0,'roof_covering_modeled':False,
 'eave_projection_reference_face':None,
 'notes':[
 '18 inch north-south ridge supersedes the point-pyramid concept.',
 'Axes use nominal core outside wall corners at wall-top elevation. These are layout datums, not exact bearing or finished board faces.',
 'No notches, tongue-and-groove profiles, joinery, roof cladding or structural capacity claims.',
 'Board sections, assignment of 5 vs 5.5 inch stock, and eave reference face require confirmation before final solids.',
 'Soffit thickness is unspecified; do not invent a solid thickness.',
 'Rafter tails beyond wall edges remain unresolved pending section orientation and eave datum.'
 ]}

def stations(span):
 a=[]; x=16.0
 while x<span/2:
  a.append(x); x+=24.0
 values=sorted(set(a+[span-x for x in a]))
 return values, span-2*a[-1]

members=[{'id':'Ridge','group':'Ridge','kind':'ridge','start':params['ridge_south'],'end':params['ridge_north']}]
for label,corner,target in [('SW',[0,0,z],params['ridge_south']),('SE',[w,0,z],params['ridge_south']),('NW',[0,l,z],params['ridge_north']),('NE',[w,l,z],params['ridge_north'])]:
 members.append({'id':'Hip'+label,'group':'Hip rafters','kind':'hip','start':corner,'end':target})
wall_layout={}
for side,span in [('South',w),('North',w),('West',l),('East',l)]:
 values,gap=stations(span)
 wall_layout[side]={'stations_inches':values,'central_bay_inches':gap,'corner_bays_inches':[16.0,16.0]}
 for i,s in enumerate(values,1):
  if side in ['South','North']:
   frac=min(s,w-s)/(w/2)
   yy=south*frac if side=='South' else l-south*frac
   start=[s,0 if side=='South' else l,z]; end=[s,yy,z+rise*frac]
   target='ridge' if abs(s-w/2)<1e-8 else 'hip'
  else:
   frac=s/south if s<south else ((l-s)/south if s>north else 1.0)
   xx=w/2*frac if side=='West' else w-w/2*frac
   start=[0 if side=='West' else w,s,z]; end=[xx,s,z+rise*frac]
   target='ridge' if south<=s<=north else 'hip'
  members.append({'id':f'{side}Rafter{i:02d}','group':'Common and jack rafters','kind':'common' if target=='ridge' else 'jack','station_inches':s,'wall':side,'start':start,'end':end,'terminates_on':target})
assert len(members)==45
assert all(all(isinstance(x,(int,float)) for x in m['start']+m['end']) for m in members)
layout={'units':'inches','datum':'Nominal core wall exterior edges at wall top; centerline schematic only','wall_layout':wall_layout,'members':members,'counts':{k:sum(m['kind']==k for m in members) for k in ['ridge','hip','common','jack']},'findings':['The exact symmetric 16 + 24 inch station pattern gives a 25.5 inch central bay on north/south walls and 25 inch central bay on east/west walls.','With the 18 inch ridge centered between y=115.5 and 133.5, east/west stations y=112 and 137 bracket the ridge. Therefore the unmodified station pattern yields 40 jack rafters and no common rafters. A central common pair would require an explicitly added or shifted station. No such member is invented here.']}
for f,obj in [('roof-parameters.json',params),('roof-layout.json',layout)]:
 (ROOT/f).write_text(json.dumps(obj,indent=2)+'\n')
hashes={f:hashlib.sha256((ROOT/f).read_bytes()).hexdigest() for f in ['Existing-Garage.FCStd','Proposed-Garage.FCStd']}
progress={'request_id':params['request_id'],'status':'awaiting_section_confirmation','timestamp_utc':datetime.now(timezone.utc).isoformat(),'model_sha256_unchanged_baseline':hashes,'counts':layout['counts'],'findings':layout['findings'],'pending':['board thickness','on-edge or flat orientation','5 vs 5.5 inch stock assignment, including hip and ridge','soffit thickness (or omit pending specification)','eave projection datum'],'artifacts':[str(ROOT/f) for f in ['roof-parameters.json','roof-layout.json','roof-layout.py','roof-generator.py']],'summary':'Layout prepared; neither FCStd changed. Await parent follow-up before generating section solids.'}
(ROOT/'roof-progress.txt').write_text(json.dumps(progress,indent=2)+'\n')
print(json.dumps(progress,indent=2))
