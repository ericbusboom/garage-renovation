from pathlib import Path
import csv, hashlib, json, shutil
import xml.etree.ElementTree as ET
from PIL import Image
from pypdf import PdfReader, PdfWriter
ROOT=Path(__file__).resolve().parent.parent
W=ROOT/'floor-plan-setbacks'; R=ROOT/'report'; D=R/'05-architectural-design/floor-plan-study'
D.mkdir(parents=True,exist_ok=True)
files=[]
for stem in ['floor-plan-setbacks','east-wall-floor-plan']:
 for ext in ['pdf','svg','png']:
  f=stem+'.'+ext;shutil.copy2(W/f,D/f);files.append(f)
for name in ['basis.json','east-wall-floor-plan-basis.json']:
 shutil.copy2(W/name,D/name);files.append(name)
writer=PdfWriter()
for f in ['floor-plan-setbacks.pdf','east-wall-floor-plan.pdf']:writer.append(D/f)
writer.add_metadata({'/Title':'ARCH-006 — Floor plan and east wall study','/Subject':'Revision 0, draft, 2026-09-15','/Author':'Codex; owner-directed geometry study'})
writer.write(D/'floor-plan-study.pdf');files.insert(0,'floor-plan-study.pdf')
readme='''# ARCH-006 — Floor plan and east wall study

**Revision:** 0  
**Date:** 2026-09-15  
**Status:** draft  
**Purpose:** Owner/design-team review of the current footprint, loft, column positions and east-wall support alternatives.

## Review copies

- [Two-sheet study PDF](floor-plan-study.pdf)
- P1 — [Upper structure and columns](floor-plan-setbacks.pdf), [PNG](floor-plan-setbacks.png), [editable SVG](floor-plan-setbacks.svg). Working plan revision 08.
- P2 — [East wall floor plan](east-wall-floor-plan.pdf), [PNG](east-wall-floor-plan.png), [editable SVG](east-wall-floor-plan.svg). Working revision EW-P3.
- [Upper-structure coordinates](basis.json) and [east-wall coordinates](east-wall-floor-plan-basis.json).
- [File and source inventory](source-inventory.csv), including SHA-256 checksums.

This is the first controlled report copy, not a permit or construction issue. The owner directed this study's placement and requested its storage in the report. East-wall options A and B remain alternatives; no final wall-strengthening system is selected by filing this package.

## Current geometry and latest corrections

Coordinates are inches from the existing outside southwest garage corner: X east, Y north, north up. Existing outline uses the earlier 249.5 × 249 in plan. Drawings state not to scale; use dimensions and the scale bar for discussion only.

| Element | Current study position / basis |
|---|---|
| Existing east / north walls | X=249.5; Y=249 |
| Local property lines | X=261.5 east; Y=331 north, located from owner-stated 12 in and 82 in clearances; no surveyed bearings |
| Upper outer limits | X=-36..213.5; Y=-68..271; east 4 ft and north 5 ft from the assumed boundaries |
| North roof edge | Y=298, 27 in beyond north wall; 33 in from assumed property line |
| Loft | Full width X=-36..213.5; Y=69.75 at W2 through Y=271 at north border |
| W1 / W2 / W3 / W4 centers | X=-34; Y=-66 / 69.75 / 185 / 269 respectively |
| S1 / S2 / S3 centers | (148.5,-66), (211.5,-66), (211.5,-2) |
| N1 / N2 centers | (53.25,269), (211.5,269); 4-in symbols have faces flush with north border |
| E-S / E-N envelopes | X=245.5..249.5; Y=-4..0 / 249..253; east faces flush with existing wall |
| E-M/B envelope | X=244.5..248.5; Y=183..187, concealed within the wall; center Y=185 aligns with W3 |
| S3 / E-S alignment | Both centers at Y=-2; S3 remains on upper-frame east edge |

The 12-in east strip contains no post envelopes. The wall-side beam is a symbolic overhead centerline, not a sized beam footprint. Option A has end posts E-S/E-N; option B adds E-M inside the wall. E-M is an intermediate post, no longer at the wall midpoint.

## Sources and regeneration

Working sources remain outside the controlled report:

- [Main generator](../../../floor-plan-setbacks/draw_plan.py)
- [East-wall generator](../../../floor-plan-setbacks/draw_east_wall_plan.py)
- [Packaging and validation](../../../floor-plan-setbacks/store_report.py)
- [Existing geometry](../../../model/parameters.json)
- [Earlier framing register](../../../structural-study/framing-member-register.json)
- [Earlier model/member-width source](../../../model-renders/build_and_render.py)
- [Corrected East Wall Study basis](../../../east-wall-study/README.md), revision 04, plus subsequent owner corrections in this floor-plan task.
- Linked reference task: “Draft East Wall strengthening,” `01a0a6c5-3c15-70a2-b201-839830bb0b20`.

The coordinate JSON files are exact snapshots of working outputs: their relative source paths are interpreted from `floor-plan-setbacks/`, not from this report folder. SVGs preserve editable groups. Regeneration uses Pillow and ReportLab; packaging uses pypdf. Do not overwrite a later controlled revision with this revision-0 packaging script.

## Remaining coordination

- Property lines, setbacks and north overhang are owner-requested study geometry, not a surveyed or agency-approved envelope. Existing 249 versus 286.25 in length conflict remains OI-016.
- The earlier elevation still shows E-M at wall midpoint; this plan places it at W3. That elevation is not copied as a current coordinated sheet.
- South support centers moved to Y=-66 to put their 4-in faces at the retained blue edge Y=-68. The provisional 8-in south beam remains centered Y=-64; the 2-in bearing eccentricity needs design coordination. Earlier 64-in column-center language is superseded by the face-alignment corrections.
- The west beam center is provisionally X=-32 while the aligned west columns are X=-34. Connections and the 2-in offset need coordination.
- Column symbols and beam widths are trial envelopes; base plates, foundations, transfer across the 36-in east offset, lateral resistance and structural capacity are unresolved. The cracked slab is not established as a footing.
- This study does not freeze roof slopes, building heights, solar geometry, material sections or the complete architectural/structural design. Earlier solar/CAD packages may use different dimensions.

Document checks confirmed readable PDFs, valid SVGs, decodable PNGs/JSON, matching coordinate alignments, and source-copy checksums. These checks do not verify structural or regulatory adequacy.
'''
(D/'README.md').write_text(readme);files.append('README.md')
# Open every artifact and check the newest requested alignments.
for f in files:
 p=D/f
 if p.suffix=='.pdf':
  doc=PdfReader(p);assert len(doc.pages)==(2 if f=='floor-plan-study.pdf' else 1)
  for page in doc.pages:assert 'ARCH-006' in page.extract_text()
 elif p.suffix=='.svg':ET.parse(p)
 elif p.suffix=='.png':
  with Image.open(p) as im:im.verify()
 elif p.suffix=='.json':json.loads(p.read_text())
 else:assert p.read_text()
b=json.loads((D/'east-wall-floor-plan-basis.json').read_text());cols={x['id']:x for x in b['columns']};ep={x['id']:x for x in b['east_wall_posts']}
assert cols['S3']['y']==ep['E-S']['y']+2
assert cols['W3']['y']==ep['E-M']['y']+2
assert all(p['x']+p['width']<=249.5 for p in ep.values())
source_for={}
for f in files:
 source_for[f]='../floor-plan-setbacks/store_report.py' if f in ['README.md','floor-plan-study.pdf'] else '../floor-plan-setbacks/'+('draw_east_wall_plan.py' if f.startswith('east-wall') else 'draw_plan.py')
with (D/'source-inventory.csv').open('w',newline='') as h:
 w=csv.writer(h);w.writerow(['file','sha256','working_source','revision','status'])
 for f in files:w.writerow([f,hashlib.sha256((D/f).read_bytes()).hexdigest(),source_for[f],0,'draft'])
files.append('source-inventory.csv');source_for['source-inventory.csv']='../floor-plan-setbacks/store_report.py'
manifest=R/'document-manifest.csv'
with manifest.open(newline='') as h:reader=csv.DictReader(h);fields=reader.fieldnames;rows=list(reader)
assert not any(row['document_id']=='ARCH-006' for row in rows),'Already registered; do not overwrite a controlled revision.'
with manifest.open('a',newline='') as h:
 writer=csv.DictWriter(h,fieldnames=fields)
 for i,f in enumerate(files):
  ident='ARCH-006' if i==0 else f'ARCH-006-A{i:02}'
  writer.writerow(dict(document_id=ident,section='05',title='Floor plan and east wall study' if i==0 else f'Floor plan study: {f}',status='draft',discipline='Architectural/Structural',required_for='Owner/design review',authoritative_source='Owner-directed geometry; source provenance and unresolved items in study README',report_path=str((D/f).relative_to(R)),working_source=source_for[f],last_verified='2026-09-15',notes=f'Revision 0; file/geometry consistency check only; not survey or engineering verification; SHA256 {hashlib.sha256((D/f).read_bytes()).hexdigest()}'))
def append(name,content):
 p=R/name;p.write_text(p.read_text()+content)
append('05-architectural-design/README.md','\n## Current draft studies\n\n[ARCH-006 — Floor plan and east wall study](floor-plan-study/floor-plan-study.pdf), revision 0, 2026-09-15, status `draft`. Two sheets record the full-width loft, aligned perimeter columns, and east-wall support alternatives, including S3/E-S and E-M/W3 alignment. [Basis, editable drawings and remaining coordination](floor-plan-study/README.md). This is a study record; ARCH-002 remains planned.\n')
append('00-report-index.md','\n## Chapter 5 floor-plan study\n\n[ARCH-006 — Floor plan and east wall study](05-architectural-design/floor-plan-study/floor-plan-study.pdf), revision 0, 2026-09-15, status `draft`. Includes P1 upper structure/columns (working rev 08) and P2 east-wall plan (EW-P3). [Study basis and editable drawings](05-architectural-design/floor-plan-study/README.md). Owner-directed geometry is recorded; structural connections, foundations, source-elevation coordination and regulatory verification remain open.\n')
append('source-map.md','\n## Floor-plan study provenance\n\nARCH-006 revision 0 is stored in [Chapter 5](05-architectural-design/floor-plan-study/README.md). Generators and historical revisions remain in `../floor-plan-setbacks/`; source references are `../model/parameters.json`, `../structural-study/framing-member-register.json`, `../model-renders/build_and_render.py` and the corrected `../east-wall-study/README.md`. Current owner corrections supersede source coordinates only as recorded in ARCH-006. The east-wall elevation midpoint is stale relative to the new E-M/W3 plan alignment.\n')
append('00-project-controls/decision-log.md','\n| DEC-008 | 2026-09-15 | Store the owner-directed floor-plan study in Chapter 5 as ARCH-006 revision 0, including full-width loft, flush perimeter columns, required S3 aligned with E-S, and E-M/B aligned with W3. | Records current study geometry and alternatives; does not adopt a final strengthening scheme or establish structural/code adequacy. | Owner | ARCH-006; ARCH-002 and STR-004 remain planned | draft |\n')
append('00-project-controls/assumptions-register.md','\n| ASM-FP-01 | ARCH-006 uses the earlier 249.5 × 249 in existing footprint, 4-in post symbols, provisional 8-in beam width, owner-stated 12/82 in clearances and requested 48/60 in east/north limits plus 27 in north overhang. | Floor-plan and wall-support discussion | Survey, member sizing or regulatory review may change the geometry | Resolve OI-016 and coordinate surveyed faces, member widths and permits | draft |\n')
append('00-project-controls/open-items.md','\n| OI-FP-01 | Coordinate ARCH-006 with elevations, CAD and structural models: E-M now at W3 Y=185, S3 at E-S Y=-2; south column centers Y=-66 versus provisional beam center Y=-64; west columns X=-34 versus beam X=-32. | Existing elevation midpoint and earlier support/beam alignments no longer match the current plan; bearing offsets and 36-in transfer to wall-side frame need design. | Architect / structural engineer | Coordinated design freeze | draft |\n| OI-FP-02 | Evaluate east-wall support options A/B, connections, lateral resistance, foundations and setback/fire treatment without crediting the cracked slab as a footing. | ARCH-006 is geometry only; neither wall-support alternative is selected or validated by report storage. | Owner / architect / structural engineer | Selection and structural issue | draft |\n')
# Verify inventory and manifest paths for every added controlled artifact.
with manifest.open(newline='') as h:
 for row in csv.DictReader(h):
  if row['document_id'].startswith('ARCH-006'):assert (R/row['report_path']).is_file()
print(f'Stored and validated {len(files)} controlled artifacts in {D}; report index, manifest, source map and registers updated.')
