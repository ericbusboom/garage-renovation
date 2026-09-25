"""Reconstruct the confirmed saved view, then study S3 removal. No canonical writes."""
from pathlib import Path
import copy, json, re, hashlib, argparse
from dataclasses import asdict
import frame as F
import sections as S
import owner_revisions as OR
import south_brace_study as SB
import column_study as CS
import solid_view as SV
import analysis as A
import studies as ST
from project_paths import ANALYSIS_STUDY_DIR

HERE=Path(__file__).resolve().parent
OUT=ANALYSIS_STUDY_DIR/'lineage'
SOURCE=ANALYSIS_STUDY_DIR/'baseline'/'column-removal-3d-solid.html'
OUT.mkdir(parents=True, exist_ok=True)

def traces():
    s=SOURCE.read_text(); q=s[s.rfind('Plotly.newPlot(')+len('Plotly.newPlot('):].lstrip()
    dec=json.JSONDecoder(); _,n=dec.raw_decode(q); data,n=dec.raw_decode(q[n:].lstrip(', \n'))
    return {t['name']:t for t in data if 'DCR ' in t.get('hovertemplate','')}

def section(name):
    return F.resolve_section(dict(section_reference=name,width=5,depth=5,material='steel')) if name.startswith('HSS') else S.get(name)

def reconstruct():
    f=F.load(F.FRAME_DIR/'frame-20260920.01-beam-scheme.compas.json')
    spec=json.loads(f.path.read_text())['specification']
    SB.move_south_line(f,9)
    SB.move_s1(f,24)
    SB.east_frame(f,beam_section='W12X16')
    SB.raise_floor(f,8)
    SB.merge_bwi(f)
    SB.south_x_to_wall(f)
    OR._drop(f,'S2')
    ts=traces()
    assert set(ts)==set(f.members),(set(ts)-set(f.members),set(f.members)-set(ts))
    mismatch=[]
    for m,t in ts.items():
        name=re.search(r'· <b>(.*?)</b>',t['hovertemplate']).group(1)
        if f.material(m)!='wood': f.section_of[m]=section(name)
        assert f.section_of[m].name==name,(m,name,f.section_of[m].name)
        pairs=F._ordered(f,[(i,j) for mm,i,j in f.segments if mm==m])
        vs,_=SV._member_mesh(f.xyz(pairs[0][0]),f.xyz(pairs[-1][1]),f.section_of[m])
        actual=sorted(tuple(round(c,2) for c in v) for v in vs)
        expected=sorted(zip(t['x'],t['y'],t['z']))
        if actual!=expected: mismatch.append(m)
    audit={'source_html':str(SOURCE),'sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
           'source_json':str(f.path),'members':len(ts),'mesh_mismatches':mismatch,
           'transformations':{'south_shift_in':9,'s1_east_shift_in':24,'east_wall_frame':True,
                              'floor_raise_in':8,'merge_bwi':True,'south_x_to_wall':True,'dropped':['S2']},
           'saved_view_has_ground_floor_columns':['W1','W2','S3'],
           'note':'HTML geometry matches do not establish undocumented connection/release settings.'}
    (OUT/'reconstruction.json').write_text(json.dumps(audit,indent=2))
    assert not mismatch,mismatch
    return f,spec

def clean(f):
    # Incidence must reflect actual remaining segments, not stale member records.
    used={n for _,i,j in f.segments for n in (i,j)}
    f.nodes={n:v for n,v in f.nodes.items() if n in used}
    for n,v in f.nodes.items(): v['members']=sorted({m for m,i,j in f.segments if n in (i,j)})
    f.links=[x for x in f.links if x[0] in used and x[1] in used]
    f.pinned_ends=[x for x in f.pinned_ends if x[0] in f.members and x[1] in used]

def solve(tag,f,spec,second_order=False):
    clean(f)
    print('RUN',tag, len(f.members),'members',flush=True)
    r=A.run(f,spec['parameters'],'L100',second_order=second_order)
    out=asdict(r)
    out.update(second_order=second_order,load_planes='corrected named-member elevations',max_dcr=r.max_dcr,passes=ST._passes(f,r),deflection_violations=A.deflection_violations(f,r),
               worst=[asdict(m) for m in sorted(r.members.values(),key=lambda m:-m.dcr)[:12]])
    (OUT/(tag+'.json')).write_text(json.dumps(out,indent=2))
    drift=min((v['ratio'] for v in r.drift.values() if v['ratio']),default=0)
    print(tag,'DCR',round(r.max_dcr,3),'drift',round(drift,1),'defl',len(out['deflection_violations']),'pass',out['passes'],flush=True)
    print([(m.member,round(m.dcr,3)) for m in sorted(r.members.values(),key=lambda m:-m.dcr)[:5]],flush=True)
    return r

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--baseline-only',action='store_true');args=p.parse_args()
    OUT.mkdir(exist_ok=True)
    f,spec=reconstruct(); solve('visible-baseline',f,spec)
    if not args.baseline_only:
        g=copy.deepcopy(f);CS.cut_ground_floor(g,'S3',112.5);solve('s3-lower-removed',g,spec)
        g=copy.deepcopy(f);OR._drop(g,'S3');solve('s3-entire-removed',g,spec)
        g=copy.deepcopy(f)
        for c in ['W1','W2','S3']:CS.cut_ground_floor(g,c,112.5)
        solve('w1-w2-s3-lower-removed',g,spec)
