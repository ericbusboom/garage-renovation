"""Demand-driven catalog search with explicit restraint assumptions; preliminary screens only."""
import json,math,copy
from pathlib import Path
import run_analysis as a
P=a.P
raw=json.loads((P/'stock-catalog-source.json').read_text())
CAT={}
for name,s in raw.items():
 q=dict(s);q.update(Iy=s['Sminor']*s['d']/2 if s['type']=='HSS' else s['Iz'],Iz=s['I'],S=s['Smajor'])
 CAT[name]=q
MEM={m['id']:m for m in a.CAD['members']}
def family(m):
 if m['section_family']=='column':return 'post:'+m['id']
 if m['section_family']=='Wbeam':return m['id']
 if m['section_family']=='chord':return (m.get('truss') or m['id'])+(':upper' if m['role']=='top_chord' else ':lower')
 return (m.get('truss') or 'T1')+':'+m['section_family']+(':diagonal' if m['role']=='diagonal' else '')
FAMS={}
for k,m in MEM.items():FAMS.setdefault(family(m),[]).append(k)
def capacity(s,m,brace=72):
 L=m['length_inches']
 # Bracing interval is a proposed requirement, not supplied by FE mesh subdivisions.
 Lb=min(L,brace) if m['section_family'] in ['chord','Wbeam','header'] else L
 E=29e6;Fy=50000.;rr=math.sqrt(min(s['Iy'],s['Iz'])/s['A']);Fe=math.pi**2*E/(Lb/rr)**2;Fcr=Fy*.658**(Fy/Fe) if Fy/Fe<=2.25 else .877*Fe
 Pc=.9*Fcr*s['A'];Pt=.9*Fy*s['A'];My=.9*Fy*s['Sminor'];Mz=.9*Fy*s['Smajor']
 if s['type']=='W':
  ry=math.sqrt(s['Iy']/s['A']);Lp=1.76*ry*math.sqrt(E/Fy);q=s['J']/(s['Smajor']*s['ho']);Lr=1.95*s['rts']*E/(.7*Fy)*math.sqrt(q+math.sqrt(q*q+6.76*(.7*Fy/E)**2));Mp=Fy*s['Zx']
  Mn=Mp if Lb<=Lp else Mp-(Mp-.7*Fy*s['Smajor'])*(Lb-Lp)/(Lr-Lp) if Lb<=Lr else math.pi**2*E/(Lb/s['rts'])**2*math.sqrt(1+.078*q*(Lb/s['rts'])**2)*s['Smajor']
  Mz=min(Mz,.9*Mn)
  if s['flange_ratio']>.38*math.sqrt(E/Fy):Mz=min(Mz,.9*.7*Fy*s['Smajor'])
  V=.9*.6*Fy*s['d']*s['tw']
 else:V=.9*.6*Fy*2*(s['d']-s['t'])*s['t']*.93
 return dict(Pc=Pc,Pt=Pt,My=My,Mz=Mz,V=V,Lb=Lb)
def screen(r,sel,brace=72,include_storage=False):
 rows={}
 for mid,bycase in r.get('member_demands',{}).items():
  cap=capacity(CAT[sel[mid]],MEM[mid],brace.get(mid,72) if isinstance(brace,dict) else brace)
  for case,d in bycase.items():
   if case=="storage125_strength_sensitivity" and not include_storage:continue
   ratio=max(d['compression']/cap['Pc'],d['tension']/cap['Pt'])+d['My']/cap['My']+d['Mz']/cap['Mz']
   ratio=max(ratio,math.hypot(d['Vy'],d['Vz'])/cap['V'])
   if ratio>rows.get(mid,{}).get('ratio',-1):rows[mid]=dict(section=sel[mid],ratio=ratio,case=case,demands=d,capacities=cap)
 return rows
def allowed(mid):
 m=MEM[mid];f=m['section_family']
 ss=[s for s in CAT.values() if s['type']==('W' if f=='Wbeam' else 'HSS')]
 if f=='column':ss=[s for s in ss if s['d']==(6 if mid=='N1 / U-W' else 4)]
 elif f=='Wbeam':ss=[s for s in ss if s['d']<=8.001]
 else:ss=[s for s in ss if s['d']<=6 and s.get('bt',0)<=1.12*math.sqrt(29e6/50000)]
 return sorted(ss,key=lambda s:s['w'])
def choose(r,selection):
 out=dict(selection)
 for fam,ids in FAMS.items():
  ids=[i for i in ids if i in selection]
  if not ids:continue
  options=allowed(ids[0]);best=None
  for s in options:
   trial={i:s['name'] for i in ids};rat=screen({'member_demands':{i:r['member_demands'][i] for i in ids}},trial)
   if max(v['ratio'] for v in rat.values())<=.85:best=s['name'];break
  if best is None:best=options[-1]['name']
  for i in ids:out[i]=best
 return out
if __name__=='__main__':
 sel={mid:a.SECTIONS[a.section(m)]['name'] for mid,m in MEM.items()};hist=[]
 for k in range(4):
  r=a.analyze('iteration2_'+str(k),selection=sel,catalog=CAT,demand_export=True)
  if r['status']!='solved_conditional':print(r['error']);break
  rows=screen(r,sel);r['member_checks']=rows;r['selection']=sel;r['max_screen_ratio']=max(v['ratio'] for v in rows.values());r['full_unbraced_max_ratio']=max(v['ratio'] for v in screen(r,sel,brace=1e9).values())
  (P/f'iteration2-step{k}.json').write_text(json.dumps(r,indent=2,default=lambda v:float(v)))
  print(k,r['steel_weight_lb'],r['max_screen_ratio'],r['results']['service_patches']['max_floor_abs_DY_in'],sorted([(v['ratio'],m) for m,v in rows.items()],reverse=True)[:4],flush=True)
  hist.append({'iteration':k,'steel_lb':r['steel_weight_lb'],'ratio':r['max_screen_ratio'],'service_patch_displacement':r['results']['service_patches']['max_floor_abs_DY_in']})
  new=choose(r,sel)
  # Preserve largest allowed floor rail while investigating floor movement separately.
  for mid in ['B2 future floor beam','T1 future floor beam']:new[mid]='W8X31'
  if new==sel:break
  sel=new
 (P/'iteration2-history.json').write_text(json.dumps(hist,indent=2))
 (P/'iteration2-catalog.json').write_text(json.dumps(CAT,indent=2))
