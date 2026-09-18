from pathlib import Path
import csv,json,hashlib,shutil
from pypdf import PdfReader,PdfWriter
R=Path(__file__).resolve().parent.parent/'report';W=R.parent/'floor-plan-setbacks';D=R/'05-architectural-design/floor-plan-study';A=D/'superseded/revision-1'
assert not A.exists();A.mkdir(parents=True)
for p in D.iterdir():
 if p.is_file():shutil.copy2(p,A/p.name)
for stem in ('floor-plan-setbacks','east-wall-floor-plan'):
 for ext in ('pdf','svg','png'):shutil.copy2(W/f'{stem}.{ext}',D/f'{stem}.{ext}')
for f in ('basis.json','east-wall-floor-plan-basis.json'):shutil.copy2(W/f,D/f)
w=PdfWriter()
for f in ('floor-plan-setbacks.pdf','east-wall-floor-plan.pdf'):w.append(D/f)
w.add_metadata({'/Title':'ARCH-006 — Floor plan study with possible ground-floor extension','/Subject':'Revision 2; draft; 2026-09-15'})
w.write(D/'floor-plan-study.pdf')
p=D/'README.md';s=p.read_text().replace('**Revision:** 1','**Revision:** 2').replace('Working plan revision 09','Working plan revision 10').replace('Working revision EW-P4','Working revision EW-P5').replace('second controlled report copy','third controlled report copy')
s+='\n## Revision 2 — possible ground-floor extension\n\nOrange highlights WB3 → W3 → W4 → N1 → N2, then south to the existing north wall, returning along existing walls to WB3. The shaded L-shaped area is a possible ground-floor extension only; it is not a selected enclosure, demolition plan or finished wall layout. Solid orange tracks the requested post-center route; dashed orange closes against the building. Roof and loft geometry is unchanged. Existing north garage-door access, affected wall openings, foundations and enclosure implications remain unresolved (OI-FP-04). This option does not supersede DEC-007 retaining exterior garage walls until a scheme is adopted. Revision 1 is archived in `superseded/revision-1/`. Packaging: `../../../floor-plan-setbacks/update_report_rev2.py`.\n'
p.write_text(s)
for name in ('00-report-index.md','05-architectural-design/README.md','source-map.md'):
 p=R/name;lines=p.read_text().splitlines()
 for i,line in enumerate(lines):
  if 'ARCH-006' in line:lines[i]=line.replace('revision 1','revision 2').replace('working rev 09','working rev 10').replace('EW-P4','EW-P5')+' Orange route shows a possible ground-floor extension, not an adopted enclosure.'
 p.write_text('\n'.join(lines)+'\n')
p=R/'00-project-controls/open-items.md';p.write_text(p.read_text()+'\n| OI-FP-04 | Evaluate the optional ground-floor extension WB3–W3–W4–N1–N2 returning to the existing north wall; resolve garage-door access, wall openings, enclosure/retention implications, foundations and finished wall faces. | Orange route in ARCH-006 rev 2 is a concept option, not an adopted expansion; prior open-walkway design remains the baseline. | Owner / architect / structural engineer | Option selection | draft |\n')
p=D/'source-inventory.csv'
with p.open(newline='') as f:rd=csv.DictReader(f);fields=rd.fieldnames;rows=list(rd)
for row in rows:
 row['revision']='2';row['sha256']=hashlib.sha256((D/row['file']).read_bytes()).hexdigest()
 if row['file'] in ('README.md','floor-plan-study.pdf'):row['working_source']='../floor-plan-setbacks/update_report_rev2.py'
with p.open('w',newline='') as f:wr=csv.DictWriter(f,fieldnames=fields);wr.writeheader();wr.writerows(rows)
p=R/'document-manifest.csv'
with p.open(newline='') as f:rd=csv.DictReader(f);fields=rd.fieldnames;rows=list(rd)
arch=[]
for row in rows:
 if row['document_id'].startswith('ARCH-006') and row['status']!='superseded':
  old=dict(row);old['document_id']+='-R1';old['status']='superseded';old['report_path']=str((A/Path(row['report_path']).name).relative_to(R));old['notes']+='; Superseded by revision 2';arch.append(old)
  row['notes']='Revision 2; draft; possible ground-floor extension only; SHA256 '+hashlib.sha256((R/row['report_path']).read_bytes()).hexdigest()
  if Path(row['report_path']).name in ('README.md','floor-plan-study.pdf','source-inventory.csv'):row['working_source']='../floor-plan-setbacks/update_report_rev2.py'
with p.open('w',newline='') as f:wr=csv.DictWriter(f,fieldnames=fields);wr.writeheader();wr.writerows(rows+arch)
for page in PdfReader(D/'floor-plan-study.pdf').pages:assert 'Rev 2' in page.extract_text()
for name in ('basis.json','east-wall-floor-plan-basis.json'):
 b=json.loads((D/name).read_text());points=b['possible_ground_floor_extension']['path'];cols={c['id']:(c['x'],c['y']) for c in b['columns']}
 assert [tuple(pt) for pt in points[:5]]==[cols[n] for n in ('WB3','W3','W4','N1','N2')]
print('Revision 2 stored and route checked; revision 1 retained; index, manifest and open item updated.')
