"""Standalone linear truss submodel replay. Run TE.py, TW.py, TN.py, TS.py or T1.py."""
import json, argparse
from pathlib import Path
import numpy as np
from scipy.sparse import csc_matrix
from scipy.sparse.linalg import splu
P=Path(__file__).resolve().parent

def run(group):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--stage',choices=['complete','roof_first'],default='complete')
    args=parser.parse_args()
    base=P/(group+'-'+args.stage)
    meta=json.loads(Path(str(base)+'.json').read_text());data=np.load(str(base)+'.npz')
    K=data['K'];F=data['F'];reference=data['U'];b=data['boundary'];free=np.setdiff1d(np.arange(len(K)),b)
    U=np.zeros_like(reference);U[:,b]=reference[:,b]
    U[:,free]=splu(csc_matrix(K[np.ix_(free,free)])).solve((F[:,free]-U[:,b]@K[np.ix_(free,b)].T).T).T
    boundary_actions=U@K.T
    displacement_error=float(np.max(np.abs(U-reference)))
    force_error=float(np.max(np.abs(boundary_actions-F)))
    assert displacement_error<1e-5,(group,displacement_error)
    assert force_error<.1,(group,force_error)
    end_actions={}
    for e in meta['elements']:
        end_actions[e['name']]={'member':e['member'],'nodes':e['nodes'],'cases':dict(zip(meta['cases'],(U[:,e['dofs']]@np.array(e['K']).T).tolist()))}
    result=dict(group=group,stage=args.stage,verified=True,maximum_dof_replay_error=displacement_error,maximum_nodal_action_replay_error=force_error,member_end_actions=end_actions,warning='Linear baseline only. Interface movements are prescribed, not extra applied loads. Local member changes require new section stiffness, self-weight, capacity checks and whole-frame reanalysis; no optimization or construction approval is implied.')
    Path(str(base)+'-replay.json').write_text(json.dumps(result))
    print(json.dumps({k:v for k,v in result.items() if k!='member_end_actions'},indent=2))
