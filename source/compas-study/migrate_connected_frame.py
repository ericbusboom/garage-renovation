"""One-time, explicit migration from the current study to a joint-based specification.
Run deliberately to re-import; normal rebuilds read frame-spec.json, never this file.
"""
import json, math
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
P=ROOT/'roof-studies/square-upper-west'; OUT=P/'connected-frame'
old=json.loads((P/'cad-mesh.json').read_text())
source={m['id']:m for m in json.loads((ROOT/'optimization/exposed-frame/geometry.json').read_text())['members']}
selected=json.loads((ROOT/'optimization/exposed-frame/selected.json').read_text())
catalog=json.loads((ROOT/'optimization/exposed-frame/catalog.json').read_text())
steel_groups={'Columns','Bracing','LoftSteel','WestMarkupFraming','MatchedEastTruss','EastSupportFrame','EastRoofRafters'}
def is_frame(o):return o['group'] in steel_groups or o['group'].startswith('Truss') or o['group']=='LoftJoists'
inventory={o['name']:o for o in old['objects'] if is_frame(o)}
N={};M={};retired={}
front=-64+3*(122.7624491117621+64)/4
params=dict(west_x=-34.,east_x=211.5,south_y=-63.,north_y=259.,clerestory_y=front,bottom_z=115.,square_top_z=228.75,solar_start_z=117.,solar_slope=math.tan(math.pi/6),outer_east_x=247.5,eob_z=100.)
def val(x):return params[x] if isinstance(x,str) else x
def node(name,xyz,support=False):
 N[name]={'xyz':xyz}
 if support:N[name]['support']='ground datum; footing/reaction design unresolved'
 return name
def on(member,t):
 if abs(t)<1e-9:return M[member]['nodes'][0]
 if abs(t-1)<1e-9:return M[member]['nodes'][1]
 key=member+' @ '+format(t,'.12g');N.setdefault(key,{'on_member':member,'fraction':t});return key
# Geometry only; deliberately retain original stock labels as unverified references.
def add(name,a,b,group,size=None,source_name=None):
 source_name=source_name or name
 if source_name in inventory:
  mid=source_name.split(' |')[0];stock=catalog.get(selected.get(mid,''),{})
 else:stock={}
 w,h=size or (stock.get('bf',stock.get('d',2)),stock.get('d',2))
 M[name]={'nodes':[a,b],'width':w,'depth':h,'group':group,'material':'wood' if group=='LoftJoists' else 'rafter' if group=='EastRoofRafters' else 'steel',
 'source_name':source_name,'section_reference':stock.get('aisc_label','concept envelope'),'section_status':'display envelope; section and connection design unverified'}
 return name
def original(mid):return next(n for n in inventory if n.split(' |')[0]==mid)
def oldx(x):return -34+(x+32)*245.5/281.5
# Master side geometry: one definition mirrored to east, with shared nodes at intersections.
for side,x,g in [('W','west_x','WestMarkupFraming'),('E','east_x','MatchedEastTruss')]:
 def pt(label,y,z):return node(side+'.'+label,[x,y,z])
 lowS=pt('south.bottom','south_y','bottom_z');lowN=pt('north.bottom','north_y','bottom_z')
 slopeS=pt('south.slope','south_y','solar_start_z')
 slopeF=node(side+'.front.slope',{'formula':'solar_front','side':side})
 topF=pt('front.top','clerestory_y','square_top_z');topN=pt('north.top','north_y','square_top_z')
 bottom=add(side+'.bottom',lowS,lowN,g,(3.5,3.5),original('T-W / B-WO') if side=='W' else 'T-E matching '+original('T-W / B-WO'))
 lowF=on(bottom,(front+63)/322)
 add(side+'.slope',slopeS,slopeF,g,(2.5,2.5),'West solar slope chord' if side=='W' else 'T-E matching West solar slope chord')
 add(side+'.top',topF,topN,g,(5,5),'West square upper chord' if side=='W' else 'T-E matching West square upper chord')
 add(side+'.clerestory',lowF,topF,g,(4,4),'West clerestory-aligned vertical' if side=='W' else 'T-E matching West clerestory-aligned vertical')
 # The slope/front node must also be an explicit attachment on the vertical.
 N[slopeF]={'on_member':side+'.clerestory','fraction':(117+(front+63)*params['solar_slope']-115)/(228.75-115)}
 for label,y,top in [('W1',0,on(side+'.slope',63/(front+63))),('W3',185,on(side+'.top',(185-front)/(259-front))),('W4',259,topN),('SW0',-63,slopeS)]:
  src=original(label)
  a=node(side+'.'+label+'.base',[x,y,0],True) if side=='W' else on(bottom,(y+63)/322)
  add(side+'.'+label,a,top,'Columns' if side=='W' else g,(4,4),src if side=='W' else 'T-E matching '+src)
 add(side+'.rear.brace',on(bottom,248/322),topN,g,(2.25,2.25),'West rear diagonal rising north' if side=='W' else 'T-E matching West rear diagonal rising north')
 add(side+'.square.brace',on(bottom,248/322),topF,g,(2.25,2.25),'West square bay diagonal' if side=='W' else 'T-E matching West square bay diagonal')
# Explicit lower-chord attachments to the full-height west columns.
N['W.south.bottom']={'on_member':'W.SW0','fraction':115/117}
N['W.north.bottom']={'on_member':'W.W4','fraction':115/228.75}
# Main crossmembers attach to side members, not separate coordinate copies.
for mid,a,b,g in [
 ('T-S',on('W.bottom',63/322),on('E.bottom',63/322),'Truss_TS'),
 ('T-S top / segment 1',on('W.slope',63/(front+63)),on('E.slope',63/(front+63)),'Truss_TS'),
 ('T1 upper lower chord',on('W.clerestory',(150.143248-115)/113.75),on('E.clerestory',(150.143248-115)/113.75),'Truss_T1'),
 ('T1 top / segment 1',on('W.clerestory',(193.64324823492282-115)/113.75),on('E.clerestory',(193.64324823492282-115)/113.75),'Truss_T1'),
 ('T1 future floor beam',on('W.clerestory',1/113.75),on('E.clerestory',1/113.75),'LoftSteel'),
 ('B2 future floor beam',on('W.W3',116/228.75),on('E.W3',1/113.75),'LoftSteel'),
 ('T-SO',on('W.SW0',116/117),on('E.SW0',.5),'Truss_Other'),
 ('T-N',on('W.bottom',1),on('E.bottom',1),'Truss_TN'),
 ('T-N top / segment 1',on('W.W4',224.25/228.75),on('E.W4',(224.25-115)/113.75),'Truss_TN')]:add(mid,a,b,g,source_name=original(mid))
# Original inner supports remain at their plan rows, attached to crossmembers.
for mid,x,y,target in [('S1',oldx(148.5),-63,'T-SO'),('S2',oldx(224.25),-63,'T-SO'),('S3',oldx(224.25),0,'T-S'),('N2',oldx(224.25),259,'T-N'),('N1 / U-W',oldx(53.25),259,'T-N top / segment 1')]:
 add(mid,node(mid+'.base',[x,y,0],True),on(target,(x+34)/245.5),'Columns',(4,4) if mid!='N1 / U-W' else (6,6),original(mid))
# Transverse webs: identify their intended parent chords explicitly by family and endpoint level.
for prefix,g,low,high,span in [('T-S','Truss_TS','T-S','T-S top / segment 1',256.25),('T1','Truss_T1','T1 upper lower chord','T1 top / segment 1',256.25)]:
 for mid,r in source.items():
  if not mid.startswith(prefix+' ') or not any(k in mid for k in (' vertical ',' diagonal ')) or not any(n.split(' |')[0]==mid for n in inventory):continue
  ends=[]
  for p in [r['a'],r['b']]:
   target=low if p[2]<(source[low]['a'][2]+source[high]['a'][2])/2 else high
   t=(p[0]+32)/span
   if t<.005:t=0
   if t>.995:t=1
   ends.append(on(target,t))
  add(mid,*ends,g,source_name=original(mid))
for mid,r in source.items():
 if mid.startswith('T1 future hanger') and any(n.split(' |')[0]==mid for n in inventory):
  t=(r['a'][0]+32)/256.25;add(mid,on('T1 future floor beam',t),on('T1 upper lower chord',t),'LoftSteel',source_name=original(mid))
# North opening framing retained; attachments follow the north chords and opening jambs.
add('T-N upper east jamb',on('T-N',187.25/281.5),on('T-N top / segment 1',187.25/281.5),'Truss_TN',source_name=original('T-N upper east jamb'))
add('T-N loading header',on('N1 / U-W',207/224.25),on('T-N upper east jamb',92/109.25),'Truss_TN',source_name=original('T-N loading header'))
for mid,r in source.items():
 if not mid.startswith('T-N ') or not any(k in mid for k in (' vertical ',' diagonal ')) or not any(n.split(' |')[0]==mid for n in inventory):continue
 ends=[]
 for x,y,z in [r['a'],r['b']]:
  target='T-N top / segment 1' if z>220 else 'T-N loading header' if z>200 else 'T-N'
  t=(x-53.25)/102 if target=='T-N loading header' else (x+32)/281.5
  ends.append(on(target,t))
 add(mid,*ends,'Truss_TN',source_name=original(mid))
# Explicit brace attachment schedule, replacing stale independent roof coordinates.
braces={
 'BR-W-1':(on('W.W3',6/228.75),on('W.W4',115/228.75)),
 'BR-W-2':(on('W.W4',6/228.75),on('W.W3',115/228.75)),
 'BR-S-1':(on('S1',6/116),on('S2',115/116)),
 'BR-S-2':(on('S2',6/116),on('S1',115/116)),
 'BR-E-ground-1':(on('S2',6/116),on('S3',1)),
 'BR-E-ground-2':(on('S3',6/115),on('S2',115/116)),
 'BR-N-ground-1':(on('W.W4',6/228.75),on('N1 / U-W',115/224.25)),
 'BR-N-ground-2':(on('N1 / U-W',6/224.25),on('W.W4',115/228.75)),
 'BR-N-upper-1':(on('W.W4',115/228.75),on('N1 / U-W',1)),
 'BR-R-main-1':(on('W.slope',63/(front+63)),on('E.slope',1)),
 'BR-R-main-2':(on('E.slope',63/(front+63)),on('W.slope',1)),
 'BR-R-cap-1':(on('W.top',(150-front)/(259-front)),on('E.top',(239.41176470588235-front)/(259-front))),
 'BR-R-cap-2':(on('E.top',(150-front)/(259-front)),on('W.top',(239.41176470588235-front)/(259-front))) }
for mid,ends in braces.items():add(mid,*ends,'Bracing',source_name=original(mid))
retired[original('BR-E-upper-1')]='Superseded historical east-wall brace; current east web explicitly mirrors owner-revised west web.'
# East overhead beam: full post stations, small end overhangs explicitly recorded.
a=node('EOB.south',['outer_east_x',-4,'eob_z']);b=node('EOB.north',['outer_east_x',253,'eob_z']);add('E-OB',a,b,'EastSupportFrame',(3,3))
for mid,x,y in [('E-S',247.5,-2),('E-N',247.5,251),('E-M option B',246.5,185)]:
 # Option B's one-inch plan offset is retained as an explicit bearing offset, not silently moved.
 target=on('E-OB',(y+4)/257)
 if x!=247.5:
  key='E-M.bearing';N[key]={'offset_from':target,'offset':[-1,0,0],'connection':'one-inch eccentric bearing inside 4-inch post / 3-inch beam envelopes'};target=key
 add(mid,node(mid+'.base',[x,y,0],True),target,'EastSupportFrame',(4,4))
N[a]['free_end']='2-inch beam overhang beyond E-S center';N[b]['free_end']='2-inch beam overhang beyond E-N center'
for i,y in enumerate([-2+23*i for i in range(12)]):
 target='E.slope' if y<front else 'E.top';t=(y+63)/(front+63) if y<front else (y-front)/(259-front)
 add('East rafter %02d'%(i+1),on('E-OB',(y+4)/257),on(target,t),'EastRoofRafters',(3,3))
# Timber joists are audited too: both ends reference their actual supporting beam.
for name,o in inventory.items():
 if o['group']!='LoftJoists':continue
 vs=o['vertices'];x=(min(v[0] for v in vs)+max(v[0] for v in vs))/2;t=(x+34)/245.5
 bay=int(name.rsplit('-',1)[1]);low='T1 future floor beam' if bay==0 else 'B2 future floor beam';high='B2 future floor beam' if bay==0 else 'T-N'
 add(name,on(low,t),on(high,t),'LoftJoists',(1.5,7.25))
# The north end vertical duplicates the mirrored east rear post.
M.pop('T-N vertical 5')
retired[original('T-N vertical 5')]='Coincident with the mirrored east rear post; one physical post retained.'
# One source object must be accounted for exactly once; no dropping hard-to-connect members.
covered=[m['source_name'] for m in M.values()]
assert len(covered)==len(set(covered))
assert set(covered)|set(retired)==set(inventory),(set(inventory)-set(covered)-set(retired),set(covered)-set(inventory))
# Preserve absolute floor elevations and plan stations when roof heights change.
# Fractions remain appropriate for transverse panel spacing; side/vertical attachments
# use constrained coordinates instead of stretching the floor with an upper chord.
def initial_point(k):
 n=N[k]
 if 'on_member' in n:
  a,b=[initial_point(j) for j in M[n['on_member']]['nodes']]
  return [u+n['fraction']*(v-u) for u,v in zip(a,b)]
 if 'offset_from' in n:return [v+d for v,d in zip(initial_point(n['offset_from']),n['offset'])]
 return [val(v) for v in n['xyz']]
initial={k:initial_point(k) for k in N}
for k,n in N.items():
 if 'on_member' not in n:continue
 a,b=[initial[j] for j in M[n['on_member']]['nodes']]
 axis=2 if abs(a[0]-b[0])+abs(a[1]-b[1])<1e-8 else 1 if abs(a[0]-b[0])<1e-8 else None
 if axis is None:continue
 v=initial[k][axis]
 if axis==1 and abs(v-front)<1e-7:v='clerestory_y'
 if axis==2 and abs(v-115)<1e-7:v='bottom_z'
 if k in ('W.front.slope','E.front.slope'):v={'solar_at_y':'clerestory_y'}
 n.pop('fraction');n['station']={'axis':axis,'value':v}
spec={'schema':'garage.connected-frame/1','units':'inches','parameters':params,'nodes':N,'members':M,'retired_members':retired,
 'source_inventory':list(inventory),'intent':'Explicit geometric connectivity; not an analysis or fabrication model.',
 'joint_policy':'Endpoints refer to node IDs. Attachment nodes are dependent points on named members. Crossings connect only when declared; ground supports and two E-OB end overhangs are explicit exceptions.',
 'migration_notes':['Removed obsolete east upper brace already replaced by mirrored web.', 'Roof braces terminate on current slope/cap chords.', 'Short transverse web and hanger ends extend to chord axes.', 'Timber joists follow their supporting crossbeams; original unsupported tail positions are retired.']}
(OUT/'frame-spec.json').write_text(json.dumps(spec,indent=2))
print('Specification:',len(M),'members;',len(N),'named nodes;',len(retired),'explicitly retired source members')
