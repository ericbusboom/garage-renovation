"""Recover group interface actions, geometry and exact controlling-member calculations."""
import os
os.environ['MPLCONFIGDIR']='/private/tmp/garage-mpl'
import engineer as a
import numpy as np,json,csv
from pathlib import Path
import matplotlib;matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
P=Path(__file__).resolve().parent;r=json.loads((P/'results.json').read_text());N=np.array(r['nodes']);es=r['elements'];U=np.array(r['service_u']);secs={f:a.cat[n] for f,n in r['selection'].items()};ff=a.Frame(N,es,secs,a.b.fixed)
groups=['T-S','T1','T-E','T-W','T-N'];colors={'T-S':'#b08b22','T1':'#c46019','T-E':'#88489e','T-W':'#168576','T-N':'#b84261'}
forces={g:np.zeros(len(U)) for g in {e['group'] for e in es}};direct={g:np.zeros(len(U)) for g in forces};membership={i:set() for i in range(len(N))}
for (case,g),F in a.b.group_loads.items():
 if case in ['D','BAND','R20']:direct[g]+=F
for e,(ix,k,T,L) in zip(es,ff.cache):
 g=e['group'];forces[g][ix]+=T.T@k@T@U[ix];wt=secs[e['family']]['w']*L/12*1.1;direct[g][ix[2]]-=wt/2;direct[g][ix[8]]-=wt/2
 for i in e['ij']:membership[i].add(g)
interfaces={};directtot={}
for g in forces:
 transfer=(forces[g]-direct[g]).reshape(-1,6);rows=[]
 for i,row in enumerate(transfer):
  if np.max(abs(row))>.1:
   assert len(membership[i])>1 or i in a.b.bases.values(),(g,i,row)
   rows.append(dict(node=i,x=N[i,0],y=N[i,1],z=N[i,2],other_groups=sorted(membership[i]-{g}),Fx=row[0],Fy=row[1],Fz=row[2],Mx=row[3],My=row[4],Mz=row[5]))
 interfaces[g]=rows;directtot[g]=-direct[g][2::6].sum()
 assert abs(sum(x['Fz'] for x in rows)-directtot[g])<.5
(P/'load-path.json').write_text(json.dumps(dict(direct_service_load_lb=directtot,interfaces=interfaces),indent=2))
with (P/'connection-actions.csv').open('w') as f:
 writer=csv.writer(f);writer.writerow(['group','node','x_in','y_in','z_in','connected_groups','Fx_lb','Fy_lb','Fz_lb','Mx_lbin','My_lbin','Mz_lbin'])
 for g,rs in interfaces.items():
  for x in rs:writer.writerow([g,x['node'],x['x'],x['y'],x['z'],';'.join(x['other_groups'])]+[x[k] for k in ['Fx','Fy','Fz','Mx','My','Mz']])
with (P/'member-checks.csv').open('w') as f:
 rows=list(r['physical_members'].values());writer=csv.DictWriter(f,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
# Complete physical parent geometry; subdivisions retained only in the solver.
parents={}
for e in es:
 key=f"M{e['parent']+1:03d}";parents.setdefault(key,dict(group=e['group'],family=e['family'],ids=set()))['ids'].update(e['ij'])
for k,d in parents.items():
 ids=list(d.pop('ids'));pts=N[ids];i,j=np.unravel_index(np.argmax(np.linalg.norm(pts[:,None,:]-pts[None,:,:],axis=2)),(len(pts),len(pts)));d['ends']=[pts[i].tolist(),pts[j].tolist()];d['length_in']=float(np.linalg.norm(pts[i]-pts[j]))
(P/'physical-members.json').write_text(json.dumps(parents,indent=2))
plt.rcParams.update({'font.size':10})
for g in groups:
 dim=1 if g in ['T-E','T-W'] else 0;fig,axs=plt.subplots(2,1,figsize=(14,9),gridspec_kw={'height_ratios':[1.3,1]},layout='constrained');ax=axs[0]
 for k,d in parents.items():
  if d['group']!=g:continue
  pts=np.array(d['ends']);x=pts[:,dim]/12;z=(pts[:,2]-98.5)/12;ax.plot(x,z,color=colors[g],lw=2);cx=x.mean();cz=z.mean();ax.text(cx,cz,k,fontsize=7,ha='center',bbox=dict(fc='white',ec='none',alpha=.9,pad=.5))
 pts=N[sorted(set(i for e in es if e['group']==g for i in e['ij']))];lo,hi=pts[:,dim].min()/12,pts[:,dim].max()/12;zmax=(pts[:,2].max()-98.5)/12
 ax.annotate('',(lo,-.75),(hi,-.75),arrowprops=dict(arrowstyle='<->'));ax.text((lo+hi)/2,-.65,f'{(hi-lo)*12:.2f} in overall',ha='center');ax.set(xlim=(lo-1,hi+1),ylim=(-1.2,zmax+1.2),ylabel='Above 98.5-in wall top (ft)',xlabel='North coordinate (ft)' if dim==1 else 'East coordinate (ft)');ax.grid(alpha=.13);ax.set_title(g+' — full truss, with physical member IDs',loc='left',fontsize=17,color=colors[g],weight='bold')
 # Applied interface actions at correct positions, positive up.
 ax=axs[1]
 for k,d in parents.items():
  if d['group']==g:
   pts=np.array(d['ends']);ax.plot(pts[:,dim]/12,(pts[:,2]-98.5)/12,color='#d3d9de',lw=1)
 for n,x in enumerate(interfaces[g]):
  if abs(x['Fz'])<50:continue
  q=x['y' if dim==1 else 'x']/12;z=(x['z']-98.5)/12;v=x['Fz'];dz=.7*np.sign(v);ax.annotate('',(q,z),(q,z-dz),arrowprops=dict(arrowstyle='->',color='#167b64' if v>0 else '#bb512d',lw=1.6));ax.annotate(f"{v/1000:+.2f}k",(q,z),xytext=(4,9 if n%2 else -16),textcoords='offset points',fontsize=8)
 ax.set(xlim=(lo-1,hi+1),ylim=(-1.2,zmax+1.2),ylabel='Above wall top (ft)',xlabel='Same coordinate as above');ax.grid(alpha=.13);ax.set_title(f'Service storage: {directtot[g]/1000:.2f} kip directly applied to this group; arrows = actions from connected framing',loc='left',fontsize=11)
 fig.suptitle(' | '.join(f"{role}: {r['selection'][g+':'+role]}" for role in ['lower','upper','web']),fontsize=12);fig.savefig(P/(g+'-design.png'),dpi=150);plt.close(fig)
fig,ax=plt.subplots(figsize=(12,11));ax.add_patch(Rectangle((0,0),249.5,249,fill=False,ec='#999',lw=4));ax.add_patch(Rectangle((0,72),224.25,183,fc='#e8eff3'))
for e in es:
 pts=N[e['ij']]
 if np.all(abs(pts[:,2]-98.5)<.01):ax.plot(pts[:,0],pts[:,1],color=colors.get(e['group'],'#3576a1'),lw=2)
for txt,x,y,rot in [('T-E TRUSS',233,115,90),('T-W TRUSS',-10,115,90),('T1 TRUSS',108,79,0),('B2 W BEAM',108,193,0),('T-S TRUSS',108,8,0),('T-N TRUSS',108,271,0),('B3 BEAM',110,236,0),('T-SO BEAM',108,-56,0)]:ax.text(x,y,txt,rotation=rot,ha='center',weight='bold',bbox=dict(fc='white',ec='none',alpha=.9))
for n,i in r['bases'].items():
 x,y,_=N[i];v=r['cases']['service storage']['columns'][n];ax.scatter(x,y,c='#333',s=40);ax.annotate(f'{n} {v/1000:.2f}k',(x,y),xytext=(5,6 if n not in ['W4','N1','N2'] else -14),textcoords='offset points',fontsize=9)
ax.text(110,130,'Roof loads → T-W / T-E\nFloor loads → T1 / B2 / B3\nConnected frame → columns',ha='center',fontsize=11);ax.text(110,287,'NORTH ↑',ha='center');ax.set(xlim=(-65,310),ylim=(-82,300),xlabel='East (inches)',ylabel='North (inches)');ax.set_aspect('equal');ax.grid(alpha=.1);fig.suptitle('Load-path plan • revised W-rail candidate',fontsize=18,weight='bold');fig.text(.5,.02,'Column labels: service-storage vertical reactions in kip (1 kip = 1,000 lb).\nRoof and floor are applied once; inter-truss transfers are internal forces, not additional building weight.',ha='center');fig.savefig(P/'load-plan.png',dpi=150);plt.close(fig)
print('Details and diagrams created')
