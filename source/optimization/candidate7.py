"""Explicit trial braced bays. Placement requires access/architecture review."""
import json,copy,math
import numpy as np
import run_analysis as a
from iterate_design import CAT,P,screen,MEM
cad=copy.deepcopy(a.CAD);members={m['id']:m for m in cad['members']}
sel=json.loads((P/'practical_no_W2_reinforced.json').read_text())['selection'].copy()
def endpoint(mid,coord):
 m=members[mid];p=np.array(m['a']);v=np.array(m['b'])-p;q=np.array(coord);t=float(np.dot(q-p,v)/np.dot(v,v));return dict(member_id=mid,point=(p+t*v).tolist(),axis_fraction=t)
def post(mid,z):
 p=members[mid]['a'];return endpoint(mid,[p[0],p[1],z])
def top(tr,y):
 es=[m for m in members.values() if m.get('truss')==tr and m['role']=='top_chord'];e=min(es,key=lambda e:max(min(e['a'][1],e['b'][1])-y,0,y-max(e['a'][1],e['b'][1])))
 t=(y-e['a'][1])/(e['b'][1]-e['a'][1]);return endpoint(e['id'],np.array(e['a'])+t*(np.array(e['b'])-e['a']))
def brace(name,aa,bb,group):
 va=np.array(aa['point']);vb=np.array(bb['point']);m=dict(id=name,object=name,truss=group,role='diagonal',stage='roof_first',a=va.tolist(),b=vb.tolist(),length_inches=float(np.linalg.norm(vb-va)),section_family='web',axis_source={'method':'explicit proposed bracing, not existing CAD'},station_axis='z')
 cad['members'].append(m);members[name]=m;MEM[name]=m;sel[name]='HSS3x3x0.188'
 for t,target in [(0,aa),(1,bb)]:
  cad['connectivity']['intended_connections'].append(dict(id=name+str(t),**{'from':{'member_id':name,'point':m['a'] if t==0 else m['b'],'axis_fraction':t},'to':target},axis_gap_inches=0,physical_solid_distance_inches=0,joint_behavior=None))
brace('BR-W-1',post('W3',6),post('W4',115),'BR-W');brace('BR-W-2',post('W4',6),post('W3',115),'BR-W')
brace('BR-S-1',post('S1',6),post('S2',115),'BR-S');brace('BR-S-2',post('S2',6),post('S1',115),'BR-S')
for suffix,y0,y1 in [('main',0,120),('cap',150,235)]:
 brace('BR-R-'+suffix+'-1',top('TW',y0),top('TE',y1),'BR-R');brace('BR-R-'+suffix+'-2',top('TE',y0),top('TW',y1),'BR-R')
a.CAD=cad
(P/'braced-candidate-geometry.json').write_text(json.dumps(cad,indent=2));(P/'braced-candidate-selection.json').write_text(json.dumps(sel,indent=2))
# Upper east wall: triangulate the previously open middle bay.
def lower(mid,station,axis):
 m=members[mid];p=list(m['a']);p[axis]=station;return endpoint(mid,p)
brace('BR-E-upper-1',lower('T-E',122.7624491117621,1),top('TE',185),'BR-E')
brace('BR-E-upper-2',lower('T-E',185,1),top('TE',122.7624491117621),'BR-E')
# North upper west bay stays outside the 8-foot loading door. Window positions need review.
def ntop(x):
 es=[m for m in members.values() if m.get('truss')=='TN' and m['role']=='top_chord']
 e=min(es,key=lambda e:max(min(e['a'][0],e['b'][0])-x,0,x-max(e['a'][0],e['b'][0])))
 t=(x-e['a'][0])/(e['b'][0]-e['a'][0]);return endpoint(e['id'],np.array(e['a'])+t*(np.array(e['b'])-e['a']))
brace('BR-N-upper-1',lower('T-N',-32,0),ntop(50.25),'BR-N')
brace('BR-N-upper-2',lower('T-N',50.25,0),ntop(-32),'BR-N')
brace('BR-N-ground-1',post('W4',6),post('N1 / U-W',115),'BR-N-ground')
brace('BR-N-ground-2',post('N1 / U-W',6),post('W4',115),'BR-N-ground')
sel['W4']='HSS4x4x0.375';sel['N2']='HSS4x4x0.375'
sel['T-W balcony header']='HSS3x3x0.188'
for name in ['T-W top / segment 1','T-W top / segment 2']:sel[name]='HSS4x4x0.313'
for name in ['BR-R-cap-1','BR-R-cap-2']:sel[name]='HSS4x4x0.188'
brace('BR-E-ground-1',post('S2',6),post('S3',115),'BR-E-ground')
brace('BR-E-ground-2',post('S3',6),post('S2',115),'BR-E-ground')
sel['T1 future floor beam']='W6X15'
sel['B2 future floor beam']='W8X24'
# Clearance revision: raise TE lower axis 2 in; use 4-in-deep thick-wall HSS.
# Loft and roof levels stay unchanged. Connection offsets are recalculated.
sel['T-E']='HSS4x4x0.5'
for m in cad['members']:
 if m['id']=='T-E' or m.get('truss')=='TE' or m['id'].startswith('BR-E-upper'):
  for side in ['a','b']:
   if m[side][2]<130:m[side][2]+=2
 if m['id'].startswith('BR-N-ground'):
  for side in ['a','b']:m[side][1]+=4
 m['length_inches']=float(np.linalg.norm(np.array(m['b'])-m['a']))
 members[m['id']]=m;MEM[m['id']]=m
for j in cad['connectivity']['intended_connections']:
 for side in ['from','to']:
  q=j[side];m=members[q['member_id']];q['point']=(np.array(m['a'])+q['axis_fraction']*(np.array(m['b'])-m['a'])).tolist()
 j['axis_gap_inches']=float(np.linalg.norm(np.array(j['from']['point'])-j['to']['point']))
 j['physical_solid_distance_inches']=None
cad['candidate_revision']='TE lower axis +2in, 4x4x1/2 HSS; north ground braces +4in north for eave clearance; loft and roof heights retained. Joint solid distances not recomputed.'
sel['T-W / B-WO']='HSS4x4x0.25'
a.CAD=cad
(P/'candidate7-candidate-geometry.json').write_text(json.dumps(cad,indent=2));(P/'candidate7-candidate-selection.json').write_text(json.dumps(sel,indent=2))
for name,kw in [('candidate7_complete',{'second_order':True}),('candidate7_roof_first',{'study_stage':'roof_first'}),('candidate7_base_pinned',{'base_pinned':True})]:
 r=a.analyze(name,remove=['W2'],selection=sel,catalog=CAT,demand_export=True,lateral_sensitivity=True,link_factor=10,**kw)
 if r['status']=='solved_conditional':
  r['selection']=sel;r['member_checks']=screen(r,sel);r['max_screen_ratio']=max(v['ratio'] for v in r['member_checks'].values());r['lower_chords_unbraced_ratio']=max(v['ratio'] for v in screen(r,sel,brace={i:1e9 for i,m in MEM.items() if m['section_family']=='chord' and m['role']!='top_chord'}).values());r['storage125_sensitivity_ratio']=max(v['ratio'] for v in screen(r,sel,include_storage=True).values())
 (P/(name+'.json')).write_text(json.dumps(r,indent=2,default=lambda v:float(v)))
 print(name,r['status'],r.get('steel_weight_lb'),r.get('max_screen_ratio'),{k:round(v['max_horizontal_displacement_in'],3) for k,v in r.get('results',{}).items() if k.startswith('lateral')},r.get('error'),flush=True)
