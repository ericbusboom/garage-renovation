"""Conditional connected-frame member sizing; not a construction design.
W major bending, minor bending and torsion are distinct; warping omitted.
"""
from pathlib import Path
import json,math,csv,collections
import numpy as np
import geometry_builder as b
from frame_solver import Frame,E,test
P=Path(__file__).resolve().parent
# Separate actual upper/lower chords. IDs refer to original physical drawn members,
# not numerical subdivisions. Full chords have conservative <=72 in brace assumption.
es=[dict(e) for e in b.elems]
for e in es:
 if e['kind']=='chord':e['family']=e['group']+(':lower' if np.all(abs(b.N[list(e['ij']),2]-b.H)<.01) else ':upper')
 if e['group'] in b.BEAM_NAMES:
  # Shear seats allow major/minor bending rotation, retain torsion (needs real restraint).
  e['releases']=([4,5] if abs(b.N[e['ij'][0],0])<.01 else [])+([10,11] if abs(b.N[e['ij'][1],0]-b.XE)<.01 else [])
fams=sorted({e['family'] for e in es})
sections=[]
for s in b.SECS:
 q=s.copy();q.update(type='HSS',Iy=s['I'],Iz=s['I'],Smajor=s['S'],Sminor=s['S']);sections.append(q)
for s in json.loads((P/'w-sections.json').read_text()):
 # Restrict to compact flexural / nonslender compression W sections.
 if s['bf/2tf']>.56*math.sqrt(E/50000) or s['h/tw']>1.49*math.sqrt(E/50000):continue
 sections.append(dict(name=s['AISC_Manual_Label'],type='W',d=s['d'],t=s['tw'],w=s['W'],A=s['A'],I=s['Ix'],Iy=s['Ix'],Iz=s['Iy'],Smajor=s['Sx'],Sminor=s['Sy'],S=s['Sx'],J=s['J'],Fy=50000.,bf=s['bf'],tf=s['tf'],tw=s['tw'],Zx=s['Zx'],Cw=s['Cw'],rts=s['rts'],ho=s['ho'],flange_ratio=s['bf/2tf']))
cat={s['name']:s for s in sections}
old=json.loads((P/'baseline-selection.json').read_text())
sel={}
# Nine trolley stations on each rail; one operating hoist at a time.
# 100 lb equipment assumed; simultaneous hoists are not included.
base={k:v.copy() for k,v in b.loads.items()}
for rail,y in list(zip(b.BEAM_NAMES,b.BEAM_YS))+[('T1',69.75)]:
 for n,x in enumerate(np.linspace(0,b.XE,9)):
  name=f'{rail}@{n}/8';b.loads[name]=np.zeros(len(b.N)*6);b.put(name,rail,(x,y,b.H),-1350.)
  # 1,000 lifted + 25% provisional dynamic increment + 100 equipment.
  base[name]=b.loads[name]
combos={'service storage':{'D':1,'BAND':1,'R20':1},'strength floor':{'D':1.2,'BAND':1.6,'R20':.5},'strength roof':{'D':1.2,'BAND':1,'R20':1.6}}
for k in [k for k in base if '@' in k]:
 combos['service '+k]={'D':1,'BAND':1,'R20':1,k:1}
 combos['strength '+k]={'D':1.2,'BAND':1.6,'R20':.5,k:1.6}

def capacities(s,e):
 L=e['Lparent'];Lb=min(L,72) if e['kind']=='chord' else L
 if e['kind']=='column':Lb=b.H
 if s['type']=='W':Lb=min(L,72) # specified but undesigned torsional/lateral brace spacing
 rr=math.sqrt(min(s['Iy'],s['Iz'])/s['A']);Fe=math.pi**2*E/(Lb/rr)**2;Fy=s['Fy'];Fcr=Fy*.658**(Fy/Fe) if Fy/Fe<=2.25 else .877*Fe
 Pc=.9*Fcr*s['A'];Pt=.9*Fy*s['A'];Mmaj=.9*Fy*s['Smajor'];Mmin=.9*Fy*s['Sminor']
 if s['type']=='W':
  ry=math.sqrt(s['Iz']/s['A']);Lp=1.76*ry*math.sqrt(E/Fy);q=s['J']/(s['Smajor']*s['ho']);Lr=1.95*s['rts']*E/(.7*Fy)*math.sqrt(q+math.sqrt(q*q+6.76*(.7*Fy/E)**2));Mp=Fy*s['Zx']
  Mn=Mp if Lb<=Lp else Mp-(Mp-.7*Fy*s['Smajor'])*(Lb-Lp)/(Lr-Lp) if Lb<=Lr else math.pi**2*E/(Lb/s['rts'])**2*math.sqrt(1+.078*q*(Lb/s['rts'])**2)*s['Smajor']
  Mmaj=min(Mmaj,.9*Mn);Mmaj=min(Mmaj,.9*.7*Fy*s['Smajor']) if s['flange_ratio']>.38*math.sqrt(E/Fy) else Mmaj;Vc=.9*.6*Fy*s['d']*s['tw'];Tc=.9*.6*Fy*s['J']/max(s['tf'],s['tw']) # Saint-Venant elastic only, warping unresolved
 else:
  Vc=.9*.6*Fy*2*(s['d']-s['t'])*s['t'];Tc=Vc*s['d']/2
 return dict(Pc=Pc,Pt=Pt,Mmajor=Mmaj,Mminor=Mmin,Vc=Vc,Tc=Tc,Lb=Lb)

def solve(selection,detail=False):
 ss={f:cat[n] for f,n in selection.items()};ff=Frame(b.N,es,ss,b.fixed);ld={k:v.copy() for k,v in base.items()};weights=collections.defaultdict(float)
 caps=[capacities(ss[e['family']],e) for e in es]
 for e,(ix,_,_,L) in zip(es,ff.cache):
  wt=ss[e['family']]['w']*L/12*1.1;ld['D'][ix[2]]-=wt/2;ld['D'][ix[8]]-=wt/2;weights[e['family']]+=wt
 # Solve all load cases together using the same stiffness factorization.
 names=list(combos);F=np.column_stack([sum(v*ld[k] for k,v in c.items()) for c in combos.values()]);U=np.zeros(F.shape);U[ff.free,:]=ff.factor.solve(F[ff.free,:]);R=ff.K@U-F
 assert np.max(abs(R[ff.free,:]))<.1
 assert np.max(abs(np.sum((R+F)[2::6,:],axis=0)))<.1
 for ci in range(F.shape[1]):
  resultant=(R[:,ci]+F[:,ci]).reshape(-1,6)
  assert np.max(abs(np.sum(np.cross(b.N,resultant[:,:3])+resultant[:,3:],axis=0)))<2.
 # Member force / ratio envelope and service displacement envelope.
 env={};floor_env={};caseout={};parentenv={};maxratio=0;maxdef=0
 for ci,name in enumerate(names):
  d=float(np.max(abs(U[2::6,ci])));isstrength=name.startswith('strength')
  if not isstrength:maxdef=max(maxdef,d)
  caseout[name]={'vertical_in':d,'total_lb':float(-F[2::6,ci].sum()),'columns':{n:float(R[6*i+2,ci]) for n,i in b.bases.items()}}
 for e,cap,(ix,k,T,L) in zip(es,caps,ff.cache):
  end=k@T@U[ix,:];nc=np.maximum(0,np.maximum(-end[6],end[0]));nt=np.maximum(0,np.maximum(end[6],-end[0]));my=np.maximum(abs(end[4]),abs(end[10]));mz=np.maximum(abs(end[5]),abs(end[11]));v=np.maximum(np.hypot(end[1],end[2]),np.hypot(end[7],end[8]));tor=np.maximum(abs(end[3]),abs(end[9]));ratio=np.maximum(nc/cap['Pc'],nt/cap['Pt'])+my/cap['Mmajor']+mz/cap['Mminor'];ratio=np.maximum(ratio,v/cap['Vc']+tor/cap['Tc'])
  ids=[i for i,n in enumerate(names) if n.startswith('strength')];j=max(ids,key=lambda i:ratio[i]);value=float(ratio[j]);maxratio=max(maxratio,value)
  row=dict(id=f"M{e['parent']+1:03d}",family=e['family'],group=e['group'],section=selection[e['family']],case=names[j],ratio=value,Nc=float(nc[j]),Nt=float(nt[j]),My=float(my[j]),Mz=float(mz[j]),V=float(v[j]),T=float(tor[j]),**cap)
  if value>env.get(e['family'],{}).get('ratio',-1):env[e['family']]=row
  key=row['id']
  if value>parentenv.get(key,{}).get('ratio',-1):parentenv[key]=row
 result=dict(selection=selection.copy(),steel_with_connections_lb=sum(weights.values()),weights=dict(weights),max_ratio=maxratio,max_vertical_in=maxdef,families=env,physical_members=parentenv,cases=caseout)
 if detail:result.update(nodes=b.N.tolist(),elements=es,service_u=U[:,0].tolist(),bases=b.bases)
 return result

def allowed(f):
 return sorted([s for s in sections if (s['type']=='W' if f in [n+':beam' for n in b.BEAM_NAMES]+['T1:lower','T1:upper'] else s['type']=='HSS') and (s['d']==4 if f=='columns' else True)],key=lambda s:s['w'])
def acceptable(r):return r['max_ratio']<=.90 and r['max_vertical_in']<=.75
if __name__=='__main__':
 print(test(),flush=True);r=solve(sel);print('INITIAL',r['max_ratio'],r['max_vertical_in'],r['steel_with_connections_lb'],flush=True);history=[]
 # Upsize failing families; movement can be controlled by interconnected supports.
 for step in range(8):
  if acceptable(r):break
  changes=0
  for f,row in r['families'].items():
   if row['ratio']<=.9:continue
   s=cat[sel[f]];opts=[q for q in allowed(f) if q['w']>s['w']+.01 and q['Iy']>=s['Iy']]
   if opts:sel[f]=opts[0]['name'];changes+=1
  r=solve(sel);print('UP',step,changes,r['max_ratio'],r['max_vertical_in'],flush=True)
  if not changes:break
 # Only claim a feasible search if the complete connected model meets its screens.
 if acceptable(r):
  for sweep in range(3):
   changes=0
   for f in fams:
    opts=[q for q in allowed(f) if q['w']<cat[sel[f]]['w']-.01]
    for q in opts: # try every lighter candidate, not monotonic property assumptions
     trial=sel.copy();trial[f]=q['name'];rr=solve(trial);history.append(dict(family=f,trial=q['name'],accepted=acceptable(rr),ratio=rr['max_ratio'],movement=rr['max_vertical_in'],weight=rr['steel_with_connections_lb']))
     if acceptable(rr):sel=trial;r=rr;changes+=1;break
   print('DOWN',sweep,changes,r['max_ratio'],r['max_vertical_in'],r['steel_with_connections_lb'],flush=True)
   if not changes:break
 r=solve(sel,True);r['feasible_screen']=acceptable(r);r['history']=history;r['lower_trials']=[]
 for f in fams:
  opts=[q for q in allowed(f) if q['w']<cat[sel[f]]['w']-.01]
  if opts:
   q=opts[-1];trial=sel.copy();trial[f]=q['name'];rr=solve(trial);r['lower_trials'].append(dict(family=f,trial=q['name'],accepted=acceptable(rr),max_ratio=rr['max_ratio'],max_vertical_in=rr['max_vertical_in'],weight_saving_lb=r['steel_with_connections_lb']-rr['steel_with_connections_lb']))
 (P/'results.json').write_text(json.dumps(r,indent=2));(P/'sections.json').write_text(json.dumps(cat,indent=2))
 print('DONE',r['feasible_screen'],r['steel_with_connections_lb'],r['max_ratio'],r['max_vertical_in'],flush=True)
