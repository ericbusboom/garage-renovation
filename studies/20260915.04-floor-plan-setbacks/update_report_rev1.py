from pathlib import Path
import csv,json,hashlib,shutil
import xml.etree.ElementTree as ET
from PIL import Image
from pypdf import PdfReader,PdfWriter
R=Path(__file__).resolve().parent.parent/'report';W=R.parent/'floor-plan-setbacks';D=R/'05-architectural-design/floor-plan-study';A=D/'superseded/revision-0'
assert not A.exists(),'Revision 0 already archived'
A.mkdir(parents=True)
current=list(D.glob('*'))
for p in current:
 if p.is_file():shutil.copy2(p,A/p.name)
for stem in ('floor-plan-setbacks','east-wall-floor-plan'):
 for ext in ('pdf','svg','png'):shutil.copy2(W/f'{stem}.{ext}',D/f'{stem}.{ext}')
for f in ('basis.json','east-wall-floor-plan-basis.json'):shutil.copy2(W/f,D/f)
w=PdfWriter()
for f in ('floor-plan-setbacks.pdf','east-wall-floor-plan.pdf'):w.append(D/f)
w.add_metadata({'/Title':'ARCH-006 — Floor plan and east wall study','/Subject':'Revision 1, draft, 2026-09-15'})
w.write(D/'floor-plan-study.pdf')
p=D/'README.md';s=p.read_text().replace('**Revision:** 0','**Revision:** 1').replace('Working plan revision 08','Working plan revision 09').replace('Working revision EW-P3','Working revision EW-P4').replace('This is the first controlled report copy','This is the second controlled report copy').replace('revision-0 packaging script','initial packaging script')
s+='\n## Revision 1 — west-wall posts\n\nAdded WB3, centered X=-2, Y=185, aligned with W3; and WBN, centered X=-2, Y=247, with its north face flush with the existing north wall at Y=249. Both 4-in post symbols occupy X=-4..0, against the outside of the west wall. Attachment and foundations remain unresolved. See OI-FP-03. Prior controlled files are retained in `superseded/revision-0/`; current regeneration uses the working drawing scripts and `../../../floor-plan-setbacks/update_report_rev1.py`.\n'
p.write_text(s)
for name in ('00-report-index.md','05-architectural-design/README.md','source-map.md'):
 p=R/name;s=p.read_text()
 # Only the ARCH-006 sections are revised.
 lines=s.splitlines()
 for i,line in enumerate(lines):
  if 'ARCH-006' in line:lines[i]=line.replace('revision 0','revision 1').replace('working rev 08','working rev 09').replace('EW-P3','EW-P4')+' Added west-wall posts WB3 and WBN.'
 p.write_text('\n'.join(lines)+'\n')
for name,row in [('decision-log.md','| DEC-009 | 2026-09-15 | Add WB3 against the west wall aligned with W3, and WBN against the west wall with its north face flush to the existing north wall. | 4-in study envelopes; records owner-directed position, not designed attachments or foundations. | Owner | ARCH-006 revision 1 | draft |'),('open-items.md','| OI-FP-03 | Design attachment and foundations for new west-wall posts WB3 and WBN; confirm finish/connection clearances. | Posts are drawn against the existing wall; wall capacity and support details are unverified. | Structural engineer / architect | Structural coordination | draft |')]:
 p=R/'00-project-controls'/name;p.write_text(p.read_text()+'\n'+row+'\n')
# Refresh checked inventory while retaining source references.
p=D/'source-inventory.csv'
with p.open(newline='') as f:rd=csv.DictReader(f);fields=rd.fieldnames;rows=list(rd)
for row in rows:
 row['revision']='1';row['sha256']=hashlib.sha256((D/row['file']).read_bytes()).hexdigest()
 if row['file'] in ('README.md','floor-plan-study.pdf'):row['working_source']='../floor-plan-setbacks/update_report_rev1.py'
with p.open('w',newline='') as f:wr=csv.DictWriter(f,fieldnames=fields);wr.writeheader();wr.writerows(rows)
p=R/'document-manifest.csv'
with p.open(newline='') as f:rd=csv.DictReader(f);fields=rd.fieldnames;rows=list(rd)
archived=[]
for row in rows:
 if row['document_id'].startswith('ARCH-006'):
  old=dict(row);old['document_id']+='-R0';old['status']='superseded';old['report_path']=str((A/Path(row['report_path']).name).relative_to(R));old['notes']+='; Superseded by ARCH-006 revision 1';archived.append(old)
  row['notes']='Revision 1; draft; added WB3 and WBN; file checks only; SHA256 '+hashlib.sha256((R/row['report_path']).read_bytes()).hexdigest()
  if Path(row['report_path']).name in ('README.md','floor-plan-study.pdf','source-inventory.csv'):row['working_source']='../floor-plan-setbacks/update_report_rev1.py'
with p.open('w',newline='') as f:wr=csv.DictWriter(f,fieldnames=fields);wr.writeheader();wr.writerows(rows+archived)
for p in D.iterdir():
 if p.suffix=='.pdf':
  for page in PdfReader(p).pages:assert 'Rev 1' in page.extract_text()
 elif p.suffix=='.svg':ET.parse(p)
 elif p.suffix=='.png':
  with Image.open(p) as im:im.verify()
 elif p.suffix=='.json':json.loads(p.read_text())
print('Report revision 1 stored; revision 0 archived; index, manifest and registers updated.')
