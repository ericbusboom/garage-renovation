"""CAD-linked preliminary 3D frame study. inch/lb. Explicit connection offsets.
This is a conditional elasticity comparison, not an AISC design/checking engine.
"""
import os,sys,json,math,hashlib,time,traceback
from pathlib import Path
os.environ['MPLCONFIGDIR']='/private/tmp/garage-wall-preview-mpl'
sys.path.insert(0,'/private/tmp/garage-pynite-runtime')
import numpy as np
from Pynite import FEModel3D
P=Path(__file__).resolve().parent
CAD=json.loads((P/'cad-analytical-members.json').read_text()); BASIS=json.loads((P/'design-basis.json').read_text())
# Published section properties retained from prior project table; no capacity approval.
SECTIONS={
 'column':dict(name='HSS4x4x0.25',A=3.37,Iy=7.8,Iz=7.8,J=12.8,w=12.21,d=4,S=3.9),
 'chord':dict(name='HSS6x6x0.25',A=5.24,Iy=28.6,Iz=28.6,J=46.1,w=19.02,d=6,S=9.53),
 'header':dict(name='HSS6x6x0.25',A=5.24,Iy=28.6,Iz=28.6,J=46.1,w=19.02,d=6,S=9.53),
 'web':dict(name='HSS2x2x0.125',A=.84,Iy=.486,Iz=.486,J=.796,w=3.05,d=2,S=.486),
 'hanger':dict(name='HSS2x2x0.125',A=.84,Iy=.486,Iz=.486,J=.796,w=3.05,d=2,S=.486)}
w=next(s for s in json.loads((P/'w-sections.json').read_text()) if s['AISC_Manual_Label']=='W8X31')
SECTIONS['Wbeam']=dict(name='W8X31',A=w['A'],Iy=w['Iy'],Iz=w['Ix'],J=w['J'],w=w['W'],d=w['d'],S=w['Sx'])
# N1/U-W is the retained 6-inch concept column: analyzed using 6-inch HSS candidate.
def section(m):return 'header' if m['id']=='N1 / U-W' else m['section_family']
def pycoord(p):return (p[0],p[2],p[1])
def benchmark():
 m=FEModel3D();m.add_material('S',29e6,29e6/2.6,.3,0);m.add_section('S',9.13,37.1,110,.536)
 m.add_node('A',0,0,0);m.add_node('B',240,0,0);m.def_support('A',True,True,True,True,False,False);m.def_support('B',False,True,True,False,False,False)
 m.add_member('B','A','B','S','S');m.add_member_pt_load('B','FY',-1000,120,'P');m.add_load_combo('P',{'P':1});m.analyze_linear(check_stability=True)
 actual=m.members['B'].deflection('dy',120,'P');expected=-1000*240**3/(48*29e6*110)
 assert abs(actual/expected-1)<1e-8
 return {'simple_beam_FE_in':actual,'closed_form_in':expected,'relative_error':abs(actual/expected-1)}
def analyze(name,remove=(),web_pinned=False,base_pinned=False,link_factor=1000,second_order=False,scale=1,diagnostic=False):
 start=time.time(); out={'case':name,'removed_columns':list(remove),'web_bending_releases':web_pinned,'bases':'pinned' if base_pinned else 'fixed_assumed','offset_link_stiffness_factor':link_factor,'analysis':'PDelta' if second_order else 'linear','section_scale':scale,'eligible_for_construction':False}
 members=[dict(x) for x in CAD['members'] if x['id'] not in remove]; mm={x['id']:x for x in members}
 con=[c for c in CAD['connectivity']['intended_connections'] if c['from']['member_id'] in mm and c['to']['member_id'] in mm]
 cuts={k:{0.,1.} for k in mm}
 for c in con:
  for side in ['from','to']:cuts[c[side]['member_id']].add(round(c[side]['axis_fraction'],9))
 # Build point loads on named members, preserving source-specific load paths.
 loads=[];ledger={}
 def put(mid,p,case,fy,mx=0,mz=0):
  e=mm[mid];a=np.array(e['a']);b=np.array(e['b']);p=np.array(p);t=float(np.dot(p-a,b-a)/np.dot(b-a,b-a));t=max(0,min(1,t));t=round(t,9);cuts[mid].add(t)
  loads.append((mid,t,case,float(fy),float(mx),float(mz)));ledger[case]=ledger.get(case,0)-float(fy)
 def floor(x,y,case,weight):
  ys=[69.75,185,249];ids=['T1 future floor beam','B2 future floor beam','T-N'];i=0 if y<=185 else 1;t=(y-ys[i])/(ys[i+1]-ys[i])
  for j,q in [(i,1-t),(i+1,t)]:put(ids[j],[x,ys[j],116 if j<2 else 115],case,-weight*q)
 for x0,x1 in zip(np.linspace(0,224.25,13)[:-1],np.linspace(0,224.25,13)[1:]):
  for y0,y1 in zip(np.linspace(72,249,17)[:-1],np.linspace(72,249,17)[1:]):
   x=(x0+x1)/2;y=(y0+y1)/2;area=(x1-x0)*(y1-y0)/144
   for case,q in [('Dfloor',BASIS['floor']['dead_psf_excluding_primary_steel']),('L40',BASIS['floor']['live_psf']),('L30',BASIS['floor']['typical_use_psf']),('L75patch',BASIS['floor']['storage_patch_psf'] if x>224.25-BASIS['floor']['storage_patch_width_in'] or y>249-BASIS['floor']['storage_patch_width_in'] else BASIS['floor']['live_psf']),('L125',BASIS['floor']['code_sensitivity_psf'])]:floor(x,y,case,q*area)
 floor(112.125,145,'P200',200)
 for mid,ys in [('B2 future floor beam',185),('T1 future floor beam',69.75)]:
  for pos in [.25,.5,.75]:put(mid,[-32+256.25*pos,ys,116],('HB' if ys==185 else 'HT')+str(pos),-(BASIS['equipment']['hoist_rated_load_lb']*BASIS['equipment']['vertical_impact_factor_assumed']+BASIS['equipment']['trolley_hoist_dead_lb_assumed']))
 def top(tr,y):
  candidates=[m for m in members if m['role']=='top_chord' and m['truss']==tr]
  def distance(m):return max(min(m['a'][1],m['b'][1])-y,0,y-max(m['a'][1],m['b'][1]))
  e=min(candidates,key=distance);a=np.array(e['a']);b=np.array(e['b']);t=np.clip((y-a[1])/(b[1]-a[1]),0,1);return e,a+t*(b-a)
 br=122.7624491117621;cs=br-8; half=(271-cs)/2
 # Roof reactions from hypothetical E-W simply supported purlins: only valid if provided.
 for lo,hi,q,surfacefactor in [(-63,br,9.5,1/math.cos(math.pi/6)),(br,271,6.6,math.sqrt(1+(18/half)**2))]:
  xx=np.linspace(-32 if lo<0 else -40,249.5 if lo<0 else 257.5,15);yy=np.linspace(lo,hi,19)
  for x0,x1 in zip(xx[:-1],xx[1:]):
   for y0,y1 in zip(yy[:-1],yy[1:]):
    x=(x0+x1)/2;y=(y0+y1)/2;area=(x1-x0)*(y1-y0)/144;t=(x+32)/256.25
    for tr,f in [('TW',1-t),('TE',t)]:
     e,p=top(tr,y)
     for case,psf in [('Droof',q*surfacefactor),('R20',20),('U20',-20)]:
      wt=psf*area*f;put(e['id'],p,case,-wt,(y-p[1])*wt)
 # Side cladding gross allowance, applied to lower chords. Opening deductions omitted.
 for tr,mid,x in [('TW','T-W / B-WO',-32),('TE','T-E',224.25)]:
  yy=np.linspace(0,249,17)
  for y0,y1 in zip(yy[:-1],yy[1:]):
   y=(y0+y1)/2;e,p=top(tr,y);wt=4*(p[2]+3-120)*(y1-y0)/144;put(mid,[x,y,115],'Dwall',-wt)
 for mid,y,ht in [('T-S',0,156.37306696),('T-N',249,231.5)]:
  xx=np.linspace(-32,224.25,13)
  for x0,x1 in zip(xx[:-1],xx[1:]):put(mid,[(x0+x1)/2,y,115],'Dwall',-4*(ht-120)*(x1-x0)/144)
 # Discretize physical members for bending response. Never use subdivisions as buckling lengths.
 for mid,e in mm.items():
  cuts[mid].update(float(v) for v in np.linspace(0,1,max(2,math.ceil(e['length_inches']/30)+1)))
 M=FEModel3D();M.add_material('steel',29e6,29e6/2.6,.3,0,50000)
 for fam,s in SECTIONS.items():M.add_section(fam,s['A']*scale,s['Iy']*scale,s['Iz']*scale,s['J']*scale)
 M.add_section('offset',10*link_factor,100*link_factor,100*link_factor,100*link_factor)
 coords={};ids={}; membernodes={};pieces=[];links=[];N=[]
 def node(p):
  key=tuple(round(float(v),6) for v in p)
  if key not in ids:
   n='N'+str(len(ids));ids[key]=n;coords[n]=list(key);N.append(n);M.add_node(n,*pycoord(key))
  return ids[key]
 for mid,e in mm.items():
  a=np.array(e['a']);b=np.array(e['b']);ts=sorted(cuts[mid]);pts=[node(a+t*(b-a)) for t in ts];membernodes[mid]=dict(zip(ts,pts))
  for k,(lo,hi) in enumerate(zip(ts[:-1],ts[1:])):
   if hi-lo<1e-7:continue
   ni=pts[k];nj=pts[k+1]
   if ni==nj:continue
   key='M'+str(len(pieces));M.add_member(key,ni,nj,'steel',section(e));pieces.append((key,mid,lo,hi))
   if web_pinned and e['section_family'] in ['web','hanger']:
    # Only physical endpoints released, interior FE subdivisions stay continuous.
    M.def_releases(key,Ryi=lo==0,Rzi=lo==0,Ryj=hi==1,Rzj=hi==1)
   wt=SECTIONS[section(e)]['w']*scale*e['length_inches']*(hi-lo)/12
   M.add_node_load(ni,'FY',-wt/2,'Dsteel');M.add_node_load(nj,'FY',-wt/2,'Dsteel');ledger['Dsteel']=ledger.get('Dsteel',0)+wt
 def nt(mid,t):return membernodes[mid][min(membernodes[mid],key=lambda x:abs(x-t))]
 connected=set()
 for c in con:
  ni=nt(c['from']['member_id'],c['from']['axis_fraction']);nj=nt(c['to']['member_id'],c['to']['axis_fraction'])
  pair=tuple(sorted([ni,nj]))
  if ni==nj or pair in connected:continue
  connected.add(pair);key='J'+str(len(links));M.add_member(key,ni,nj,'steel','offset');links.append((key,ni,nj,c['id']))
 bases={}
 for mid,e in mm.items():
  if e['axis_source'].get('ground_post'):
   n=nt(mid,0);M.def_support(n,True,True,True,not base_pinned,not base_pinned,not base_pinned);bases[mid]=n
 for mid,t,case,fy,mx,mz in loads:
  n=nt(mid,t);M.add_node_load(n,'FY',fy,case)
  if mx:M.add_node_load(n,'MX',mx,case)
  if mz:M.add_node_load(n,'MZ',mz,case)
 D={k:1 for k in ['Dsteel','Dfloor','Droof','Dwall']}
 combos={'service40':dict(D,L40=1,R20=1),'service_patches':dict(D,L75patch=1,R20=1),'typical30':dict(D,L30=1),'storage125_sensitivity':dict(D,L125=1,R20=1),'live_only':{'L40':1},'machine200':dict(D,L40=1,P200=1),'uplift20_sensitivity':{**{k:.6 for k in D},'U20':1},'strength_screen':{**{k:1.2 for k in D},'L75patch':1.6,'R20':.5}}
 for h in ['HB0.25','HB0.5','HB0.75','HT0.25','HT0.5','HT0.75']:combos[h]={**D,'L40':1,h:1}
 if diagnostic:combos={k:{k:1} for k in ['Dsteel','Dfloor','Droof','Dwall','L40','R20']}
 for k,v in combos.items():M.add_load_combo(k,v)
 out.update(nodes=len(coords),elements=len(pieces),offset_links=len(links),steel_weight_lb=ledger['Dsteel'],load_ledger_lb=ledger,sections=SECTIONS)
 # Explicit connectivity audit, no automatic fictitious restraints.
 adj={n:set() for n in coords}
 for key,m in M.members.items():adj[m.i_node.name].add(m.j_node.name);adj[m.j_node.name].add(m.i_node.name)
 seen=set(bases.values());stack=list(seen)
 while stack:
  for n in adj[stack.pop()]:
   if n not in seen:seen.add(n);stack.append(n)
 out['unconnected_node_count']=len(coords)-len(seen)
 if len(coords)!=len(seen):out['status']='disconnected';out['unconnected_nodes']=[coords[n] for n in coords if n not in seen];return out
 try:
  if second_order:M.analyze_PDelta(check_stability=True,max_iter=20)
  else:M.analyze_linear(check_stability=True)
  out['status']='solved_conditional';results={}
  for combo,factors in combos.items():
   expected=sum(ledger.get(k,0)*q for k,q in factors.items());ry=sum(M.nodes[n].RxnFY[combo] for n in bases.values());err=abs(ry-expected)/max(1,abs(expected))
   if err>1e-5:raise ValueError(('equilibrium',combo,ry,expected,err))
   # Six-component global equilibrium audit. Node loads are the complete load set.
   residual_force=np.zeros(3); residual_moment=np.zeros(3); force_norm=0.;moment_norm=0.
   for nn in M.nodes.values():
    f=np.zeros(3);mom=np.zeros(3);r=np.array([nn.X,nn.Y,nn.Z])
    for direction,value,case in nn.NodeLoads:
     q=value*factors.get(case,0)
     if direction in ['FX','FY','FZ']:f[['FX','FY','FZ'].index(direction)]+=q
     elif direction in ['MX','MY','MZ']:mom[['MX','MY','MZ'].index(direction)]+=q
    rf=np.array([nn.RxnFX.get(combo,0),nn.RxnFY.get(combo,0),nn.RxnFZ.get(combo,0)])
    rm=np.array([nn.RxnMX.get(combo,0),nn.RxnMY.get(combo,0),nn.RxnMZ.get(combo,0)])
    residual_force+=f+rf;residual_moment+=mom+rm+np.cross(r,f+rf)
    force_norm+=np.linalg.norm(f)+np.linalg.norm(rf);moment_norm+=np.linalg.norm(mom)+np.linalg.norm(rm)+np.linalg.norm(np.cross(r,f))+np.linalg.norm(np.cross(r,rf))
   force_error=np.linalg.norm(residual_force)/max(force_norm,1);moment_error=np.linalg.norm(residual_moment)/max(moment_norm,1)
   if not second_order and max(force_error,moment_error)>1e-5:raise ValueError(('global equilibrium',combo,force_error,moment_error))
   floor_nodes=set(membernodes['B2 future floor beam'].values())|set(membernodes['T1 future floor beam'].values())|set(membernodes['T-N'].values())
   disps={n:M.nodes[n].DY[combo] for n in floor_nodes};worst=min(disps,key=disps.get)
   stresses=[]
   for key,mid,lo,hi in pieces:
    e=mm[mid];s=SECTIONS[section(e)];m=M.members[key]
    for x in [0,m.L()/2,m.L()]:
     axial=m.axial(x,combo);my=m.moment('My',x,combo);mz=m.moment('Mz',x,combo)
     sy=s['Iy']/(s['d']/2)*scale;sz=s['Iz']/(s['d']/2)*scale
     ratio=(abs(axial)/(s['A']*scale)+abs(my)/sy+abs(mz)/sz)/50000
     stresses.append((ratio,mid))
   worststress=max(stresses)
   results[combo]={'floor_min_DY_in':disps[worst],'floor_worst_node_xyz_in':coords[worst],'max_floor_abs_DY_in':max(abs(v) for v in disps.values()),'vertical_equilibrium_relative_error':err,'global_force_relative_error':force_error,'global_moment_relative_error':moment_error,'reactions_lb':{k:M.nodes[n].RxnFY[combo] for k,n in bases.items()},'max_elastic_stress_over_Fy':worststress[0],'stress_member':worststress[1]}
  out['results']=results
  if diagnostic:
   out['elapsed_seconds']=time.time()-start
   return out
  out['screen_only']= {'live_deflection_L360_in':256.25/360,'live_deflection_screen':results['live_only']['max_floor_abs_DY_in']<=256.25/360,'stress_screen':results['strength_screen']['max_elastic_stress_over_Fy']<=.9,'omitted':['member buckling and LTB','HSS joint limits','gussets/welds/bolts','real base fixity/soil','wood joists/deck local loads','lateral/seismic/wind design','roof-first temporary bracing','hoist local flange and lateral/dynamic forces']}
  if name=='baseline':
   dump={'units':'in/lb','nodes':coords,'elements':[{'name':k,'member':mid,'a':M.members[k].i_node.name,'b':M.members[k].j_node.name,'family':section(mm[mid])} for k,mid,lo,hi in pieces], 'connections':[{'name':k,'a':ni,'b':nj,'source':j} for k,ni,nj,j in links],'bases':bases,'displacements_service40':{n:[M.nodes[n].DX['service40'],M.nodes[n].DZ['service40'],M.nodes[n].DY['service40']] for n in coords},'cad_sha':CAD['cad_snapshot']['sha256']}
   (P/'analysis-model.json').write_text(json.dumps(dump,indent=2))
 except Exception as ex:out['status']='unstable_or_failed';out['error']=str(ex);out['traceback']=traceback.format_exc()
 out['elapsed_seconds']=time.time()-start;return out
if __name__=='__main__':
 (P/'solver-benchmark.json').write_text(json.dumps(benchmark(),indent=2))
 cases=[('baseline',{}),('remove_W2',{'remove':['W2']}),('remove_W3',{'remove':['W3']}),('remove_W2_W3',{'remove':['W2','W3']}),('baseline_web_pinned',{'web_pinned':True}),('baseline_base_pinned',{'base_pinned':True}),('baseline_link_sensitivity',{'link_factor':100}),('baseline_PDelta',{'second_order':True})]
 result=[]
 for name,kw in cases:
  print('RUN',name,flush=True);r=analyze(name,**kw);result.append(r);(P/'results.json').write_text(json.dumps(result,indent=2,default=lambda v:v.item() if hasattr(v,"item") else str(v)));print(name,r['status'],r.get('results',{}).get('service40',{}),flush=True)
