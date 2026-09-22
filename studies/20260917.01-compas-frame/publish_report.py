"""Publish the owner-requested STR-006 draft; source analysis remains here."""
import csv, hashlib, json, shutil
from pathlib import Path
import coordinated_study as study
import frame_models
from compas.data import json_load
from matplotlib.backends.backend_pdf import PdfPages

ROOT=study.ROOT
DEST=ROOT/'report/06-structural-engineering/frame-geometry-study'
DEST.mkdir(parents=True,exist_ok=True)
OUT=study.OUT
stamp='STR-006 | Revision 0 | 2026-09-15 | draft | Inches | Not to scale'
MODEL=frame_models.latest('coordinated')
bundle=json_load(MODEL)
plan=bundle['plan'];draft=bundle['trusses'];baseline=bundle['baselines']
study.validate_plan(plan)
for d in draft.values():study.validate_truss(d)
report=json.loads((OUT/'validation.json').read_text())
shutil.copy2(MODEL,DEST/MODEL.name)
for name in ['beam-and-truss-positions.csv','support-positions.csv','support-offsets.csv','truss-members.csv','validation.json','coordination-report.md']:
    shutil.copy2(OUT/name,DEST/name)
notes=DEST/'coordination-report.md'
notes.write_text(notes.read_text().replace('# Coordinated COMPAS floor plan and trusses','# STR-006 — Coordinated COMPAS floor plan and trusses\n\n'+stamp))
html=(OUT/'coordinated-3d.html').read_text().replace('<head>','<head><title>STR-006 — Frame geometry study — draft rev 0</title>',1)
html=html.replace('Garage / east overhead beam + connections','STR-006 / Frame geometry study · draft rev 0 · 2026-09-15')
html=html.replace('E-OB spans E-S to E-N · beam underside level with truss bottoms at Z98.5','Inches · X east / Y north / Z up · NTS · E-OB underside Z98.5 · provisional sections')
(DEST/'model-3d.html').write_text(html)
background=study.build()
figs=[('floor-plan',study.plot_plan(plan,background))]
figs[0][1].axes[0].annotate('N',xy=(276,295),xytext=(276,274),ha='center',arrowprops=dict(arrowstyle='->',color=study.INK))
schedules=study.schedule_pages(plan,report)
figs+=schedules[:2]
figs += [(n+'-study',study.plot_truss(n,draft[n],baseline[n])) for n in study.NAMES]
figs.append(schedules[2])
with PdfPages(DEST/'frame-geometry-study.pdf',metadata={'Title':'STR-006 — Coordinated frame geometry study','Author':'Project study / COMPAS generator','Subject':stamp}) as pdf:
    for name,fig in figs:
        fig.text(.04,.009,stamp,fontsize=8,color=study.INK)
        pdf.savefig(fig)
        if name=='floor-plan':fig.savefig(DEST/'floor-plan.png',dpi=150)
        study.plt.close(fig)
# Neutral mesh/reference export: named objects, inches explicitly declared.
lines=['# STR-006 rev 0 2026-09-15 draft; units inches; X east Y north Z up',
       '# Proposed solids and unsized reference lines only. No existing walls or historical baseline.']
offset=1
for model in [*(d['model'] for d in draft.values()),plan['column_model'],plan['beam_model']]:
    for e in model.elements():
        vs,fs=e.modelgeometry.to_vertices_and_faces();lines.append('o '+e.name.replace(' ','_'))
        lines += ['v '+' '.join(f'{v:.9g}' for v in p) for p in vs]
        lines += ['f '+' '.join(str(offset+i) for i in face) for face in fs]
        offset+=len(vs)
for name,m in plan['members'].items():
    if m['kind']=='beam' and m['bottom'] is not None and name!='E-OB':
        lines += ['o '+name+'_reference']
        lines += [f'v {p.x:.9g} {p.y:.9g} {m["bottom"]:.9g}' for p in (m['line'].start,m['line'].end)]
        lines += [f'l {offset} {offset+1}'];offset+=2
(DEST/'frame-geometry.obj').write_text('\n'.join(lines)+'\n')
source_paths=['compas-study/'+n for n in ['coordinated_study.py','publish_report.py','geometry_types.py','parametric_truss.py','build_study.py','requirements-lock.txt']]
source_paths += list(report['source_hashes'])+['model/parameters.json','structural-study/section-dimensions.json']
with (DEST/'source-inventory.csv').open('w') as f:
    w=csv.writer(f);w.writerow(['workspace_path','sha256'])
    for path in source_paths:w.writerow([path,hashlib.sha256((ROOT/path).read_bytes()).hexdigest()])
(DEST/'README.md').write_text('''# STR-006 — Coordinated frame geometry study

**Revision:** 0 · **Date:** 2026-09-15 · **Status:** draft  
**Purpose:** Owner review and geometry handoff for subsequent structural engineering.

## View the study

- [Interactive 3D model](model-3d.html) — self-contained; open in a browser without a server or internet. Drag to orbit, scroll to zoom, click legend entries to hide groups. Existing walls are separate from proposed framing.
- [Nine-page drawing and truss study](frame-geometry-study.pdf) — coordinated floor plan, support/member schedules, five truss comparisons, and open coordination items.
- [Floor-plan preview](floor-plan.png)
- [Geometry decisions and coordination notes](coordination-report.md)

## Data for the next stage

- [Native COMPAS model]('''+MODEL.name+''') — current registry, parametric solids, truss recipes and geometric attachment graphs; historical baselines remain separately identified.
- [Neutral OBJ geometry](frame-geometry.obj) — named proposed solids and reference lines, in inches. Mesh exchange only, not an analysis or BIM model; import units explicitly.
- [Beam and truss positions](beam-and-truss-positions.csv), [support positions](support-positions.csv), [truss member endpoints](truss-members.csv), [support offsets](support-offsets.csv).
- [Geometry validation](validation.json) and [source checksums](source-inventory.csv).

## Recorded geometry

13 columns; five truss families T-S, T1, T-W, T-E and T-N; 94 truss members plus 10 plates. The plan registry contains 16 entries, including historical O2/O3 subsegment references and OB1 context. E-OB is an additional modeled beam.

Owner corrections place T-W on the far-west column row X=-34, extend the cross-members to that row, include all columns, connect E-S to S3 and E-M/E-N to T-E, and restore E-OB over the east column tops. The transverse links are 36, 35 and 36 inches respectively. E-M retains option B status; showing the east frame does not settle the alternatives or connection design.

Units are inches. X increases east, Y north, Z up. Origin is the existing outside southwest garage corner in plan; Z0 is the study floor datum. North is the garage-door side. Columns extend to Z98.5; E-OB underside is Z98.5, matching truss bottom faces. The 4-inch column symbols and 3-inch beam/chord envelopes are provisional geometry, not selected sections. Roof retains a draft 30-degree slope and older heights; loft datum is Z107.25.

## Engineering handoff and limits

No loads, load combinations, material grades, structural section properties, support restraints, connection stiffnesses or deflection limits have been assigned for this coordinated geometry study. No force, equilibrium, stability, capacity or deflection analysis has been performed. Geometric endpoint incidence does not establish a structural joint. Foundations, existing-wall capacity, field dimensions, corrosion and weld quality are unverified. Secondary joists/rafters, diaphragms, bracing design, fasteners and foundations are excluded.

Checks cover source-baseline shape matching, model save/reload, plan/elevation consistency, column bounds, beam geometry, connection endpoints and deliberate invalid edits. These are geometry checks only. Open issues include adjacent west uprights, door clearances, south bearing offsets, east option/offset details and roof coordination. Structural calculations and construction documents require the responsible California-licensed design professional's review and sealing.

This study develops [ARCH-006](../../05-architectural-design/floor-plan-study/README.md). Its far-west truss and east-beam elevation corrections are newer than that architectural drawing; ARCH-006 is retained as its own draft, not silently revised. Reconcile both with the solar/roof studies before an engineering geometry freeze.

## Reproduction and provenance

Generators and reproducible source inputs remain in the working analysis directory: [COMPAS study](../../../compas-study/README.md), [model/drawing generator](../../../compas-study/coordinated_study.py), [report publisher](../../../compas-study/publish_report.py), and [dependency versions](../../../compas-study/requirements-lock.txt). COMPAS 2.15.1, compas_model 0.9.3; other versions are pinned in the lock file. The source inventory records exact code and input hashes at publication.

From the project root, run `.venv/bin/python compas-study/coordinated_study.py`, then `.venv/bin/python compas-study/publish_report.py`. Review updated content before publishing a later revision. Report storage records the owner-directed study, not approval for construction.
''')
manifest=ROOT/'report/document-manifest.csv'
with manifest.open(newline='') as f:r=csv.DictReader(f);fields=r.fieldnames;rows=list(r)
rows=[r for r in rows if not r['document_id'].startswith('STR-006')]
files=[DEST/'frame-geometry-study.pdf']+sorted(p for p in DEST.iterdir() if p.name!='frame-geometry-study.pdf')
for i,p in enumerate(files):
    rows.append(dict(document_id='STR-006' if i==0 else f'STR-006-A{i:02}',section='06',title='Coordinated frame geometry study' if i==0 else p.name,status='draft',discipline='Structural',required_for='Owner review and structural geometry handoff',authoritative_source='Owner-directed geometry; source-inventory.csv; no structural adequacy claim',report_path=str(p.relative_to(ROOT/'report')),working_source='../compas-study/coordinated_study.py; ../compas-study/publish_report.py',last_verified='2026-09-15',notes='Revision 0; geometry checks only; SHA256 '+hashlib.sha256(p.read_bytes()).hexdigest()))
with manifest.open('w',newline='') as f:w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)
print(f'Published {len(files)} controlled artifacts to {DEST}')
