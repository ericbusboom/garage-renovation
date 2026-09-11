"""Export linear cut-boundary submodels; baseline Candidate 9, not design approval."""
import json, csv, hashlib
from pathlib import Path
import numpy as np
import run_analysis as a
from iterate_design import CAT
P=Path(__file__).resolve().parent
OUT=P/'truss-submodels'
a.CAD=json.loads((P/'candidate9-candidate-geometry.json').read_text())
selection=json.loads((P/'candidate9-candidate-selection.json').read_text())
def export(M,members,pieces,links,combos,sections,coords,study_stage):
    ownership={m['id']:m.get('truss') for m in members}
    physical={key:mid for key,mid,lo,hi in pieces}
    connection={c['id']:c for c in a.CAD['connectivity']['intended_connections']}
    for key,ni,nj,cid in links:
        c=connection[cid]; left=ownership[c['from']['member_id']];right=ownership[c['to']['member_id']]
        if left==right and left in ['TE','TW','TN','TS','T1']:physical[key]='@'+left
    actual={sub.name:sub for m in M.members.values() for sub in m.sub_members.values()}
    physical={sub.name:physical[k] for k,m in M.members.items() if k in physical for sub in m.sub_members.values()}
    parent_ids={sub.name:k for k,m in M.members.items() for sub in m.sub_members.values()}
    member_ids={k:mid for k,mid,lo,hi in pieces}
    link_connections={k:connection[cid] for k,ni,nj,cid in links}
    def neighbor(k):
        parent=parent_ids[k]
        if parent in member_ids:return [member_ids[parent]]
        c=link_connections[parent]
        return [c[side]['member_id'] for side in ['from','to']]
    for group in ['TE','TW','TN','TS','T1']:
        keys=[k for k,mid in physical.items() if ownership.get(mid)==group or mid=='@'+group]
        used={n.name for k in keys for n in [actual[k].i_node,actual[k].j_node]}
        external={n.name for k,m in actual.items() if k not in keys for n in [m.i_node,m.j_node]}
        names=sorted(used,key=lambda n:int(n[1:])); index={n:i for i,n in enumerate(names)}
        boundary=[n for n in names if n in external]
        K=np.zeros((6*len(names),6*len(names))); elems=[]
        for key in keys:
            m=actual[key]; ends=[m.i_node.name,m.j_node.name]; ix=np.array([index[n]*6+d for n in ends for d in range(6)])
            ke=m.Ke();K[np.ix_(ix,ix)]+=ke
            elems.append(dict(name=key,member=physical[key],nodes=ends,dofs=ix.tolist(),K=ke.tolist()))
        cases=list(combos)
        U=np.array([[getattr(M.nodes[n],d)[case] for n in names for d in ['DX','DY','DZ','RX','RY','RZ']] for case in cases])
        F=U@K.T
        # Interior action must agree with original directly applied loads, independently of replay.
        direct=np.zeros_like(F)
        dirs=['FX','FY','FZ','MX','MY','MZ']
        for ci,case in enumerate(cases):
            for n in names:
                for direction,value,loadcase in M.nodes[n].NodeLoads:
                    direct[ci,6*index[n]+dirs.index(direction)]+=value*combos[case].get(loadcase,0)
        interior=[6*index[n]+d for n in names if n not in boundary for d in range(6)]
        error=float(np.max(np.abs((F-direct)[:,interior]))) if interior else 0
        assert error<.05,(group,error)
        base=OUT/(group+'-'+study_stage)
        np.savez_compressed(str(base)+'.npz',K=K,U=U,F=F,direct_global_node_loads=direct,boundary=np.array([6*index[n]+d for n in boundary for d in range(6)],dtype=int))
        meta=dict(group=group,stage=study_stage,analysis='linear reference, fixed interface movements for local replay',units='in, lb, lb-in, radians',axes='Solver X=east, Y=up, Z=north; moments and rotations about solver axes',nodes={n:coords[n] for n in names},node_coordinate_axes='CAD x=east,y=north,z=up',boundary_nodes=boundary,boundary_neighbors={n:sorted({mid for k,m in actual.items() if k not in keys and n in [m.i_node.name,m.j_node.name] for mid in neighbor(k) if ownership.get(mid)!=group}) for n in boundary},cases=combos,elements=elems,interior_load_check_max_absolute_error=error,source_geometry_sha256=hashlib.sha256(json.dumps(a.CAD,sort_keys=True).encode()).hexdigest(),eligible_for_construction=False)
        Path(str(base)+'.json').write_text(json.dumps(meta))
        with open(str(base)+'-connection-actions.csv','w') as f:
            w=csv.writer(f);w.writerow(['case','node','CAD_x_in','CAD_y_in','CAD_z_in','FX_lb','FY_lb','FZ_lb','MX_lb_in','MY_lb_in','MZ_lb_in'])
            for ci,case in enumerate(cases):
                for n in boundary:w.writerow([case,n,*coords[n],*F[ci,index[n]*6:index[n]*6+6]])
        print(group,study_stage,len(boundary),'interfaces; interior check',error,flush=True)
if __name__=='__main__':
    for stage in ['complete','roof_first']:
        r=a.analyze('submodel_export_'+stage,remove=['W2'],selection=selection,catalog=CAT,link_factor=10,demand_export=True,lateral_sensitivity=True,study_stage=stage,export_hook=export,export_basic_cases=True)
        (OUT/('global-'+stage+'.json')).write_text(json.dumps(r,indent=2,default=lambda v:v.item()))
        assert r['status']=='solved_conditional',r.get('traceback',r)
