from pathlib import Path
import numpy as np,json,csv,math,collections,os
from scipy.sparse.csgraph import connected_components
from scipy.sparse import coo_matrix
from frame_solver import Frame,test,E
BASE=Path(__file__).parent;ROOT=BASE.parent;TRIANGULATED=os.environ.get('TRUSS_OPTION')=='triangulated';SHEAR_SEATS=os.environ.get('SHEAR_SEATS')=='1';OUT=BASE/'generated-input'/os.environ.get('LAYOUT','test');OUT.mkdir(exist_ok=True,parents=True)
BEAM_YS=json.loads(os.environ.get('BEAM_YS','[185]'));BEAM_NAMES=['B2'] if len(BEAM_YS)==1 else ['B2-S','B2-N'];LOFT_SUPPORTS=[69.75]+BEAM_YS+[253];LOFT_NAMES=['T1']+BEAM_NAMES+['T-N']
H=98.5;W=249.5;XE=224.25;FLOOR=107.25;BR=-63+(227.25-106.5)/math.tan(math.pi/6)
def roof(y):return min(106.5+(y+63)*math.tan(math.pi/6),227.25)
# Manufacturer Atlas A500 square HSS table: nominal thickness, weight, A, I, S, J, b/t.
raw=[(2,.125,3.05,.84,.486,.486,.796,14.2),(2,.188,4.32,1.19,.641,.641,1.09,8.5),(2.5,.125,3.90,1.07,.998,.798,1.61,18.6),(2.5,.188,5.59,1.54,1.35,1.08,2.25,11.4),(3,.125,4.75,1.30,1.78,1.19,2.84,22.9),(3,.188,6.87,1.89,2.46,1.64,4.03,14.2),(3,.25,8.81,2.44,3.02,2.01,5.08,9.9),(4,.188,9.42,2.58,6.21,3.11,10,20),(4,.25,12.21,3.37,7.80,3.90,12.8,14.2),(4,.313,14.83,4.10,9.14,4.57,15.3,10.7),(4,.375,17.27,4.78,10.3,5.15,17.5,8.5),(4,.5,21.63,6.02,11.9,5.95,21,5.6),(5,.188,11.97,3.28,12.6,5.04,19.9,25.7),(5,.25,15.62,4.30,16,6.40,25.8,18.5),(5,.375,22.37,6.18,21.7,8.68,36.1,11.3),(6,.25,19.02,5.24,28.6,9.53,45.6,22.8),(6,.375,27.48,7.58,39.5,13.2,64.6,14.2),(6,.5,35.24,9.74,48.3,16.1,81.1,9.9),(8,.313,31.84,8.76,85.6,21.4,136,24.5),(8,.375,37.69,10.4,100,25,160,19.9),(8,.5,48.85,13.5,125,31.3,204,14.2),(8,.625,59.32,16.4,146,36.5,244,10.8)]
SECS=[dict(name=f'HSS{d:g}x{d:g}x{t:g}',d=d,t=t,w=w,A=A,I=I,S=S,J=J,bt=bt,Fy=50000.) for d,t,w,A,I,S,J,bt in raw]
(OUT/'sections.json').write_text(json.dumps(SECS,indent=2))
LINES=[]
def line(group,kind,a,b):
 a=np.array(a,float);b=np.array(b,float)
 if np.linalg.norm(b-a)<.001:return
 LINES.append(dict(group=group,family=group+':'+kind,a=a,b=b,kind=kind,L=float(np.linalg.norm(b-a))))
def transverse(n,y,a,b):
 hi=roof(y);xx=np.linspace(a,b,7);line(n,'chord',(a,y,H),(b,y,H));line(n,'chord',(a,y,hi),(b,y,hi))
 for x in xx:line(n,'web',(x,y,H),(x,y,hi))
 for i in (range(6) if TRIANGULATED else [0,5]):line(n,'web',(xx[i],y,H if i==0 else hi),(xx[i+1],y,hi if i==0 else H))
transverse('T-S',0,0,246.5);transverse('T1',69.75,0,XE)
for n,x in [('T-W',0),('T-E',XE)]:
 cuts=sorted(set([-63,-21.25,0,69.75,BR,185,253]+([186,246] if n=='T-W' else [126])))
 line(n,'chord',(x,-63,H),(x,253,H))
 for a,b in zip(cuts[:-1],cuts[1:]):
  line(n,'chord',(x,a,roof(a)),(x,b,roof(b)))
  if not(n=='T-W' and a>=185):line(n,'web',(x,a,H),(x,b,roof(b)))
 for y in cuts:line(n,'web',(x,y,H),(x,y,roof(y)))
 if n=='T-W':line(n,'web',(x,186,FLOOR+83),(x,246,FLOOR+83))
line('T-N','chord',(-32,253,H),(W,253,H));line('T-N','chord',(-32,253,227.25),(W,253,227.25));line('T-N','chord',(-32,253,203.25),(W,253,203.25))
for x in [-32,53.25,81.5,113.5,XE,W]:line('T-N','web',(x,253,H),(x,253,227.25))
xx=np.linspace(-32,W,9)
for i,(a,b) in enumerate(zip(xx[:-1],xx[1:])):
 line('T-N','web',(a,253,203.25),(a,253,227.25));line('T-N','web',(a,253,203.25 if i%2==0 else 227.25),(b,253,227.25 if i%2==0 else 203.25))
line('T-N','web',(81.5,253,FLOOR+85.5),(113.5,253,FLOOR+85.5))
for n,a,b in [(n,(0,y,H),(XE,y,H)) for n,y in zip(BEAM_NAMES,BEAM_YS)]+[('T-SO',(-32,-63,H),(W,-63,H)),('B-WO',(-32,-63,H),(-32,253,H)),('O2',(-32,69.75,H),(0,69.75,H)),('O3',(-32,185,H),(0,185,H))]:line(n,'beam',a,b)
posts=json.loads((BASE/'inputs/framing-member-register.json').read_text())['posts']
for p in posts:line(p['id'],'column',(p['x'],p['y'],0),(p['x'],p['y'],H));LINES[-1]['family']='columns'
# Split at actual intersections/endpoints and at <=24in to capture bending under distributed loads.
ends=[p for e in LINES for p in [e['a'],e['b']]];N=[];lookup={};elems=[]
def node(p):
 k=tuple(np.round(p,4))
 if k not in lookup:lookup[k]=len(N);N.append(np.array(k))
 return lookup[k]
for idx,e in enumerate(LINES):
 a,b=e['a'],e['b'];v=b-a;L=e['L'];ts=[0,1]
 for p in ends:
  t=np.dot(p-a,v)/L**2
  if -.00001<=t<=1.00001 and np.linalg.norm(p-a-t*v)<1e-5:ts.append(max(0,min(1,t)))
 # Interior crossing between any nonparallel lines: potential rigid joint at exact 3D crossing.
 for f in LINES:
  u=f['b']-f['a'];mat=np.column_stack((v,-u))
  if np.linalg.matrix_rank(mat)<2:continue
  t,r=np.linalg.lstsq(mat,f['a']-a,rcond=None)[0]
  if 0<t<1 and -1e-7<=r<=1+1e-7 and np.linalg.norm(a+t*v-(f['a']+r*u))<1e-5:ts.append(t)
 ts=sorted(set(round(t,9) for t in ts));tt=[]
 for lo,hi in zip(ts[:-1],ts[1:]):tt.extend(np.linspace(lo,hi,max(2,math.ceil((hi-lo)*L/24)+1))[:-1])
 tt.append(1)
 for lo,hi in zip(tt[:-1],tt[1:]):
  if (hi-lo)*L<1e-5:continue
  elems.append(dict(ij=(node(a+lo*v),node(a+hi*v)),group=e['group'],family=e['family'],kind=e['kind'],parent=idx,Lparent=L,releases=(([4,5] if lo==0 else [])+([10,11] if hi==1 else [])) if SHEAR_SEATS and e['group'] in ['B2','B3'] else []))
# Remove duplicated coincident bars (e.g. a north header upright drawn over a full-height post).
unique={}
for e in elems:
 key=(tuple(sorted(e['ij'])),e['group'])
 if key not in unique:unique[key]=e
 elems=list(unique.values())
N=np.array(N);fixed=[];bases={} 
for p in posts:
 i=node([p['x'],p['y'],0]);bases[p['id']]=i;fixed.extend(range(i*6,i*6+6))
assert len(N)==len(lookup)
# Load distribution: floor N-S joists between T1/B2/B3; roof E-W purlins to T-W/T-E.
# East roof cantilever and cap overhang require collectors; no unverified wall bearing.
families=sorted(set(e['family'] for e in elems));TOTAL={};loads={k:np.zeros(6*len(N)) for k in ['D','L40','L125','BAND','P1000','R20','UP20','X20','Y20']}
group_loads=collections.defaultdict(lambda:np.zeros(6*len(N)))
ledger=collections.defaultdict(float)
def put(k,group,p,value,component=2):
 # Linear nodal distribution to the closest segment in the named physical member group.
 best=None
 for e in elems:
  if e['group']!=group:continue
  i,j=e['ij'];a,b=N[i],N[j];v=b-a;t=np.clip(np.dot(np.array(p)-a,v)/np.dot(v,v),0,1);dist=np.linalg.norm(np.array(p)-(a+t*v))
  if best is None or dist<best[0]:best=(dist,i,j,t)
 dist,i,j,t=best
 if dist>1e-3:raise ValueError((group,p,dist))
 loads[k][6*i+component]+=value*(1-t);loads[k][6*j+component]+=value*t
 group_loads[(k,group)][6*i+component]+=value*(1-t);group_loads[(k,group)][6*j+component]+=value*t

def floorroute(k,x,y,lb):
 ys=LOFT_SUPPORTS;names=LOFT_NAMES;i=max(0,min(len(ys)-2,int(np.searchsorted(ys,y,side='right'))-1));t=(y-ys[i])/(ys[i+1]-ys[i])
 for j,q in [(i,1-t),(i+1,t)]:put(k,names[j],(x,ys[j],H),-lb*q)

def roofroute(k,x,y,lb):
 # Cap overhang mapped to eave supporting line through equivalent nodal force+moment omitted in this route;
 # use actual y within support extent and record this approximation explicitly.
 yy=min(253,max(-63,y));t=x/XE
 for g,xx,q in [('T-W',0,1-t),('T-E',XE,t)]:
  put(k,g,(xx,yy,roof(yy)),-lb*q)
  if abs(y-yy)>1e-9:put(k,g,(xx,yy,roof(yy)),-lb*q*(y-yy),3)
# Deterministic midpoint cells; boundaries exact for floor storage strips.
xs=sorted(set([0,36,XE-36,XE]+list(np.linspace(0,XE,25))))
ys=sorted(set([72,219,255]+LOFT_SUPPORTS[1:]+list(np.linspace(72,255,25))))
for a,b in zip(xs[:-1],xs[1:]):
 for c,d in zip(ys[:-1],ys[1:]):
  x=(a+b)/2;y=(c+d)/2;area=(b-a)*(d-c)/144
  for k,q in [('D',9),('L40',40),('L125',125),('BAND',125 if x<36 or x>XE-36 or y>219 else 40)]:floorroute(k,x,y,area*q)
ledger['loft deck + secondary joists (9 psf)']=XE*183/144*9
# Roof areas from actual outer faces, excluding underside, solar tile seams and fascias.
model=json.loads((BASE/'inputs/garage-model.json').read_text());roofareas={}
for o in model['objects']:
 if o['name'] not in ['Solar roof assembly','Hip cap south','Hip cap north','Hip cap east','Hip cap west']:continue
 v=np.array(o['vertices'])/.0254;face=o['faces'][0];poly=v[face];area=sum(np.linalg.norm(np.cross(poly[i]-poly[0],poly[i+1]-poly[0]))/2 for i in range(1,len(poly)-1))/144;roofareas[o['name']]=area
solarA=roofareas['Solar roof assembly'];capA=sum(v for k,v in roofareas.items() if k!='Solar roof assembly')
# Solar surface 8 psf: 2.4 PV/glass +2.6 metal/foam +1 waterproof details +2 secondary framing.
for a,b in zip(np.linspace(-63,BR,50)[:-1],np.linspace(-63,BR,50)[1:]):
 for c,d in zip(np.linspace(0,W,20)[:-1],np.linspace(0,W,20)[1:]):
  x=(c+d)/2;y=(a+b)/2;plan=(b-a)*(d-c)/144
  roofroute('D',x,y,plan/math.cos(math.pi/6)*9.5)
  roofroute('R20',x,y,plan*20);roofroute('UP20',x,y,-plan*20)
# Hip cap total distributed to main truss roof lines over rear support interval, retaining centroid.
for y in np.linspace((BR-8)+(271-BR)/40,263-(271-BR)/40,20):
 for x in np.linspace(-8+(W+16)/40,W+8-(W+16)/40,20):
  roofroute('D',x,y,capA*6.6/400)
  proj=(W+16)*(255-BR+16)/144
  roofroute('R20',x,y,proj*20/400);roofroute('UP20',x,y,-proj*20/400)
ledger['solar-slope assembly (9.5 psf actual surface)']=solarA*9.5;ledger['hip-cap assembly (6.6 psf actual surface)']=capA*6.6
# Upper wall panel area gross, before openings: conservative 4psf incl girts/trim.
wall_area=2*((BR+0)/2*(roof(0)-H+roof(BR)-H)+(255-BR)*(227.25-H))/144+W*((roof(0)-H)+(227.25-H))/144
for y in np.linspace(255/80,255-255/80,40):
 for g,x in [('T-W',0),('T-E',XE)]:
  q=4*(roof(y)-H)*255/40/144;put('D',g,(x,min(y,253),H),-q)
  if g=='T-E':put('D',g,(x,min(y,253),H),q*(W-XE),4)
for g,y,width in [('T-S',0,246.5),('T-N',253,W)]:
 for x in np.linspace(width/80,width-width/80,40):put('D',g,(x,y,H),-4*W/40*(roof(y)-H)/144)
ledger['upper panel walls/girts (4 psf gross)']=-loads['D'][2::6].sum()-sum(ledger.values())
# Balcony 32x78; load divided between inner T-W and outer B-WO; guard allowance lumped D.
for y in np.linspace(177+78/40,255-78/40,20):
 for g,x in [('T-W',0),('B-WO',-32)]:
  put('D',g,(x,min(y,253),H),-(32*78/144*12+200)/40)
  for k in ['L40','L125','BAND']:put(k,g,(x,min(y,253),H),-32*78/144*60/40)
ledger['balcony deck and guards']=32*78/144*12+200
floorroute('P1000',XE/2,185,1000)
# Diagnostic lateral forces only: 20psf on gross projected upper side area; NOT site-specific wind/seismic.
for g,x in [('T-W',0),('T-E',XE)]:
 for y in np.linspace(255/40,255-255/40,20):put('X20',g,(x,min(y,253),roof(min(y,253))),20*(wall_area-W*((roof(0)-H)+(227.25-H))/144)/2/40,0)
for x in np.linspace(W/40,W-W/40,20):put('Y20','T-N',(x,253,227.25),20*W*(227.25-H)/144/20,1)
# Save geometry prior to solutions, incl isolated S1 support.
(OUT/'analysis-model.json').write_text(json.dumps({'units':'in/lb','nodes':N.tolist(),'elements':elems,'bases':bases,'roof_surface_ft2':roofareas,'ledger_lb':dict(ledger)},indent=2))

COMBOS={'service occupied':{'D':1,'L40':1,'R20':1},'service storage bands':{'D':1,'BAND':1,'R20':1},'service full125':{'D':1,'L125':1,'R20':1},'service patch1000':{'D':1,'L40':1,'P1000':1,'R20':1},'strength floor':{'D':1.2,'BAND':1.6,'R20':.5},'strength roof':{'D':1.2,'BAND':1,'R20':1.6},'uplift sensitivity':{'D':.9,'UP20':1},'lateral X sensitivity':{'D':1,'L40':1,'X20':1},'lateral Y sensitivity':{'D':1,'L40':1,'Y20':1}}

def run(selection,stiffness=1,flexible_columns=False,flexible_trusses=False,pinned_bases=False,omit_s3=False):
 secs={f:SECS[i].copy() for f,i in selection.items()}
 for f,s in secs.items():
  if (flexible_columns and f=='columns') or (flexible_trusses and (f.endswith(':chord') or f.endswith(':web'))):
   s['I']*=.25;s['J']*=.25
 es=[e for e in elems if not(omit_s3 and e['group']=='S3')]
 ff=Frame(N,es,secs,[v for v in fixed if v%6<3 or v//6==bases['S1']] if pinned_bases else fixed,stiffness);ld={k:v.copy() for k,v in loads.items()};weights=collections.defaultdict(float)
 for e,(ix,k,T,L) in zip(es,ff.cache):
  wt=secs[e['family']]['w']*L/12*1.10 # 10% allowance for plates/joints included as gravity, not stiffness
  ld['D'][ix[2]]-=wt/2;ld['D'][ix[8]]-=wt/2;weights[e['group']]+=wt
 out={};demand={f:[] for f in families}
 for case,coef in COMBOS.items():
  load=sum(v*ld[k] for k,v in coef.items());u,reactions,forces=ff.solve(load)
  err=float(abs(reactions[2::6].sum()+load[2::6].sum()))
  assert err<max(.01,abs(load[2::6].sum())*1e-6)
  resultant=(load+reactions).reshape(-1,6)
  moment_error=np.sum(np.cross(N,resultant[:,:3])+resultant[:,3:],axis=0)
  assert np.max(abs(moment_error))<2.,moment_error
  rows=[]
  for e,end,(ix,k,T,L) in zip(es,forces,ff.cache):
   s=secs[e['family']];Nc=max(0,-end[6],end[0]);Nt=max(0,end[6],-end[0]);M=max(abs(end[4])+abs(end[5]),abs(end[10])+abs(end[11]));V=max(np.linalg.norm(end[[1,2]]),np.linalg.norm(end[[7,8]]));tor=max(abs(end[3]),abs(end[9]))
   # Explicit assumed effective length; numerical subdivisions do not shorten buckling length.
   lb=min(e['Lparent'],72) if e['kind']=='chord' else e['Lparent']
   if e['kind']=='column':lb=H
   r=(s['I']/s['A'])**.5;Fe=math.pi**2*E/(lb/r)**2;Fy=s['Fy'];Fcr=Fy*.658**(Fy/Fe) if Fy/Fe<=2.25 else .877*Fe
   pc=.9*Fcr*s['A'];mc=.9*Fy*s['S'];util=max(Nc/pc,Nt/(.9*Fy*s['A']))+M/mc
   # Limited elastic axial+bending and conservative shear/torsion screen; not full HSS connection/local design.
   tc=2*(s['d']-s['t'])*s['t']*.6*Fy*.9
   util=max(util,(V+2*tor/s['d'])/tc)
   rows.append(dict(group=e['group'],family=e['family'],Ncomp=Nc,Ntension=Nt,M=M,V=V,T=tor,ratio=util,Lb=lb))
   if case.startswith('strength'):demand[e['family']].append(rows[-1])
  out[case]={'weight_lb':-float(load[2::6].sum()),'max_vertical_in':float(max(abs(u[2::6]))),'max_horizontal_in':float(max(np.hypot(u[0::6],u[1::6]))),'reaction_balance_error_lb':err,'columns':{name:{'P_lb':float(reactions[6*i+2]),'Vx_lb':float(reactions[6*i]),'Vy_lb':float(reactions[6*i+1]),'Mx_lbin':float(reactions[6*i+3]),'My_lbin':float(reactions[6*i+4])} for name,i in bases.items()},'groups':{g:{k:float(max(r[k] for r in rows if r['group']==g)) for k in ['Ncomp','Ntension','M','V','T','ratio']} for g in set(e['group'] for e in es)},'u':u.tolist()}
 return out,demand,dict(weights)

def optimize():
 selection={f:8 if f=='columns' else 18 if f.endswith(':beam') else 8 if f.endswith(':chord') else 5 for f in families}
 history=[]
 for it in range(8):
  out,dem,weights=run(selection);changes=0
  for f,rows in dem.items():
   current=selection[f];old=SECS[current];peak=max(r['ratio'] for r in rows)
   if peak<=.85:continue
   choices=[i for i,s in enumerate(SECS) if s['I']>old['I']*1.08 and (s['d']==4 if f=='columns' else s['d']<=8)]
   if choices:selection[f]=min(choices,key=lambda i:SECS[i]['w']);changes+=1
  history.append({'iteration':it,'steel_with_connections_lb':sum(weights.values()),'max_screen_ratio':max(max(r['ratio'] for r in rows) for rows in dem.values()),'changes':changes});print(history[-1],flush=True)
  if not changes:break
 out,dem,weights=run(selection)
 def acceptable(o):
  strength=max(g['ratio'] for c,d in o.items() if c.startswith('strength') for g in d['groups'].values())
  return strength<=.90 and o['service storage bands']['max_vertical_in']<=.75
 # Coordinate-descent section search with each accepted change re-solving the connected frame.
 # Not proof of global minimum; connections/lateral design not included in admissibility.
 if acceptable(out):
  for sweep in range(3):
   changed=0
   for f in families:
    old=SECS[selection[f]]
    choices=sorted([i for i,s in enumerate(SECS) if s['w']<old['w']-.01 and (s['d']==4 if f=='columns' else True)],key=lambda i:SECS[i]['w'],reverse=True)
    for i in choices:
     trial=selection.copy();trial[f]=i;o,_,wt=run(trial)
     if acceptable(o):selection=trial;out=o;weights=wt;changed+=1
     else:break
   print('DOWNSIZE',sweep,changed,round(sum(weights.values())),flush=True)
   history.append({'downsizing_sweep':sweep,'accepted_changes':changed,'steel_with_connections_lb':sum(weights.values())})
   if not changed:break
 out,dem,weights=run(selection)
 return selection,out,weights,history
if __name__=='__main__':
 tests=test();print(tests,flush=True)
 selection,out,weights,history=optimize()
 # Stiffness sensitivity: halve all frame stiffness, which doubles deformations but leaves reactions unchanged.
 # More useful: selectively halve truss I/A/J, represented by alternative section choices in separate follow-up.
 sens={}
 for name,kw in [('column bending stiffness 25%',{'flexible_columns':True}),('truss bending/torsion stiffness 25%',{'flexible_trusses':True}),('pinned column bases',{'pinned_bases':True})]:
  ss,_,_=run(selection,**kw);sens[name]={c:{k:d[k] for k in ['max_vertical_in','max_horizontal_in','columns']} for c,d in ss.items() if c in ['service storage bands','lateral X sensitivity','lateral Y sensitivity']}
 results={'sensitivity':sens,'status':'FIRST-ORDER SCREEN ONLY; unresolved joints/load transfer; no construction sizing','tests':tests,'selection':{f:SECS[i] for f,i in selection.items()},'history':history,'steel_weight_by_group_lb':weights,'dead_load_nonprimary_lb':dict(ledger),'roof_surface_ft2':roofareas,'cases':out,'nodes':len(N),'elements':len(elems)}
 (OUT/'results.json').write_text(json.dumps(results,indent=2))
 with (OUT/'column-reactions.csv').open('w') as f:
  writer=csv.DictWriter(f,fieldnames=['case','column','P_lb','Vx_lb','Vy_lb','Mx_lbin','My_lbin']);writer.writeheader()
  for c,d in out.items():
   for n,r in d['columns'].items():writer.writerow(dict(case=c,column=n,**r))
 with (OUT/'member-group-demands.csv').open('w') as f:
  writer=csv.DictWriter(f,fieldnames=['case','group','Ncomp','Ntension','M','V','T','ratio']);writer.writeheader()
  for c,d in out.items():
   for n,r in d['groups'].items():writer.writerow(dict(case=c,group=n,**r))
 print('COMPLETE',len(N),'nodes',len(elems),'elements',flush=True)
