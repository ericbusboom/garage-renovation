from pathlib import Path
import shutil,csv,hashlib,json
import xml.etree.ElementTree as ET
from pypdf import PdfReader
from PIL import Image
W=Path(__file__).resolve().parent;R=W.parent/'report';D=R/'05-architectural-design/floor-plan-study'
# Validate the replacement before removing the duplicate/history files the owner requested deleted.
assert len(PdfReader(W/'floor-plan-study.pdf').pages)==1
assert 'Rev 4' in PdfReader(W/'floor-plan-study.pdf').pages[0].extract_text()
ET.parse(W/'floor-plan-study.svg')
with Image.open(W/'floor-plan-study.png') as im:im.verify()
b=json.loads((W/'floor-plan-study-basis.json').read_text());c={v['id']:v for v in b['columns']}
assert 'WBN' not in c and c['N2']['x']-c['N1']['x']==192
readme='''# ARCH-006 — Floor plan study

**Revision:** 4 · **Date:** 2026-09-15 · **Status:** draft

One combined drawing contains the existing garage, upper structure, full-width loft, columns, possible ground-floor extension, new north door bay, and **optional east-wall framing**.

- [PDF](floor-plan-study.pdf)
- [Preview](floor-plan-study.png)
- [Editable SVG](floor-plan-study.svg)
- [Coordinate data](basis.json)

## Current layout

- Orange: possible extension from WB3 → W3 → W4 → N1 → N2, returning along the existing building.
- WBN is removed. N1 is 16 ft west of N2, center-to-center; the 4-in post symbols leave 188 in between faces before jambs and finishes.
- WB3 is against the west wall, aligned with W3. S3 aligns with E-S; E-M/B aligns with W3.
- Purple: optional east-wall support frame. Option A uses E-S/E-N; option B adds concealed E-M. The full 12-in east strip remains clear of posts.
- Blue: upper structural outline and north roof overhang. Teal: full-width loft outline.

## Basis and remaining coordination

Units are inches in the coordinate data; X east, Y north, origin at the existing outside southwest corner. The earlier existing footprint is 249.5 × 249 in. Property lines use owner-stated 12-in east and 82-in north clearances. Requested east/north limits are 4 ft / 5 ft, with a 27-in north roof overhang. These are study inputs, not a survey or agency approval.

Post symbols are 4 in square. South column centers are Y=-66, west row X=-34; provisional beam centers remain Y=-64 and X=-32. Connections, offsets, foundations, the transfer to the east-wall frame, door sizing and wall alterations remain unresolved. The extension and east-wall framing are options, not adopted construction work. Earlier elevations and analyses may not match this plan.

## Source and upkeep

The single current generator is [draw_floor_plan_study.py](../../../floor-plan-setbacks/draw_floor_plan_study.py); [publish_clean_study.py](../../../floor-plan-setbacks/publish_clean_study.py) publishes and checks the report copy. Sources: [existing dimensions](../../../model/parameters.json), [earlier framing register](../../../structural-study/framing-member-register.json), [member-width model](../../../model-renders/build_and_render.py), and [East Wall Study](../../../east-wall-study/README.md), with owner corrections recorded in the current geometry. Relative source paths inside `basis.json` refer to the working `floor-plan-setbacks/` folder.

Keep this directory to these five current files. Replace them when the study changes; do not add duplicate plan sheets or old revision folders here. The owner requested removal of the previous report copies. Working source history remains outside this folder. The report manifest records current checksums and provenance.
'''
# Exact user-named study directory only. No signed or issued documents are present.
assert D.resolve()==(R/'05-architectural-design/floor-plan-study').resolve()
for p in D.iterdir():
 if p.is_dir():shutil.rmtree(p)
 else:p.unlink()
for ext in ('pdf','svg','png'):shutil.copy2(W/f'floor-plan-study.{ext}',D/f'floor-plan-study.{ext}')
shutil.copy2(W/'floor-plan-study-basis.json',D/'basis.json');(D/'README.md').write_text(readme)
p=R/'05-architectural-design/README.md';s=p.read_text();s=s[:s.index('## Current draft studies')]+'''## Current draft study

[ARCH-006 — Floor plan study](floor-plan-study/floor-plan-study.pdf), **revision 4**, 2026-09-15, status `draft`.

One combined plan shows the upper structure, full-width loft, columns, possible ground-floor extension and new north door bay. East-wall framing is marked as optional. WBN is removed; N1–N2 spacing is 16 ft center-to-center. S3 aligns with E-S, and E-M/B aligns with W3.

[Editable drawing, coordinates and study notes](floor-plan-study/README.md). ARCH-002 remains planned.

![Combined floor plan study](floor-plan-study/floor-plan-study.png)
''';p.write_text(s)
for filename in ('00-report-index.md','source-map.md'):
 p=R/filename;lines=p.read_text().splitlines()
 for i,line in enumerate(lines):
  if line.startswith('[ARCH-006') or line.startswith('ARCH-006 revision'):
   lines[i]='[ARCH-006 — Combined floor plan study](05-architectural-design/floor-plan-study/floor-plan-study.pdf), revision 4, 2026-09-15, status `draft`. One plan shows the structure, columns, possible ground-floor extension, north door bay and optional east-wall framing. [Editable drawing and source notes](05-architectural-design/floor-plan-study/README.md). Duplicate sheets and old report copies removed at owner request; current generator: `../floor-plan-setbacks/draw_floor_plan_study.py`.'
  elif 'ARCH-006 rev 3' in line:lines[i]=line.replace('ARCH-006 rev 3','ARCH-006 rev 4')
 p.write_text('\n'.join(lines)+'\n')
p=R/'00-project-controls/decision-log.md';s=p.read_text()
entry='| DEC-011 | 2026-09-15 | Consolidate ARCH-006 into one combined plan and remove duplicate drawings and old revisions from the floor-plan-study report folder. | East-wall framing remains optional; retain only current PDF, PNG, SVG, coordinate data and README. | Owner | ARCH-006 revision 4 | draft |'
if '| DEC-011 |' not in s:p.write_text(s+'\n'+entry+'\n')
p=R/'document-manifest.csv'
with p.open(newline='') as f:rd=csv.DictReader(f);fields=rd.fieldnames;rows=[row for row in rd if not row['document_id'].startswith('ARCH-006')]
for i,name in enumerate(('floor-plan-study.pdf','floor-plan-study.png','floor-plan-study.svg','basis.json','README.md')):
 rows.append(dict(document_id='ARCH-006' if i==0 else f'ARCH-006-A{i:02}',section='05',title='Combined floor plan study' if i==0 else name,status='draft',discipline='Architectural/Structural',required_for='Owner/design review',authoritative_source='Owner-directed study; sources in study README',report_path=str((D/name).relative_to(R)),working_source='../floor-plan-setbacks/'+('publish_clean_study.py' if name=='README.md' else 'draw_floor_plan_study.py'),last_verified='2026-09-15',notes='Revision 4; optional east-wall framing; prior duplicate/history files removed per DEC-011; SHA256 '+hashlib.sha256((D/name).read_bytes()).hexdigest()))
with p.open('w',newline='') as f:wr=csv.DictWriter(f,fieldnames=fields);wr.writeheader();wr.writerows(rows)
assert len(list(D.iterdir()))==5
assert all((R/r['report_path']).exists() for r in rows if r['document_id'].startswith('ARCH-006'))
print('Clean report folder: one diagram in PDF/PNG/SVG, one coordinate file and README. Prior duplicates and revision folders deleted; report references synchronized.')
