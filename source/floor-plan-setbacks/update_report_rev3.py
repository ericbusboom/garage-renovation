from pathlib import Path
import csv,json,hashlib,shutil
from pypdf import PdfReader,PdfWriter
R=Path(__file__).resolve().parent.parent/'report';W=R.parent/'floor-plan-setbacks';D=R/'05-architectural-design/floor-plan-study';A=D/'superseded/revision-2'
assert not A.exists();A.mkdir(parents=True)
for p in D.iterdir():
 if p.is_file():shutil.copy2(p,A/p.name)
for stem in ('floor-plan-setbacks','east-wall-floor-plan'):
 for ext in ('pdf','svg','png'):shutil.copy2(W/f'{stem}.{ext}',D/f'{stem}.{ext}')
for f in ('basis.json','east-wall-floor-plan-basis.json'):shutil.copy2(W/f,D/f)
w=PdfWriter()
for f in ('floor-plan-setbacks.pdf','east-wall-floor-plan.pdf'):w.append(D/f)
w.add_metadata({'/Title':'ARCH-006 — Floor plan study with possible ground-floor extension','/Subject':'Revision 3; draft; 2026-09-15'})
w.write(D/'floor-plan-study.pdf')
p=D/'README.md';s=p.read_text().replace('**Revision:** 2','**Revision:** 3').replace('Working plan revision 10','Working plan revision 11').replace('Working revision EW-P5','Working revision EW-P6').replace('third controlled report copy','fourth controlled report copy')
s+='\n## Revision 3 — north door location\n\nRemoved WBN. N1 center is now (19.5,269), 16 ft west of N2 at (211.5,269), measured center-to-center. A new door bay is marked along this north support line. The 4-in post envelopes leave 188 in between faces before jambs and finishes; the door opening itself is not sized. The extension remains a possible option. Revision 2 is retained in `superseded/revision-2/`. Packaging source: `../../../floor-plan-setbacks/update_report_rev3.py`.\n'
s=s.replace('(53.25,269), (211.5,269)','(19.5,269), (211.5,269)')
p.write_text(s)
for name in ('00-report-index.md','05-architectural-design/README.md','source-map.md'):
 p=R/name;lines=p.read_text().splitlines()
 for i,line in enumerate(lines):
  if 'ARCH-006' in line:lines[i]=line.replace('revision 2','revision 3').replace('working rev 10','working rev 11').replace('EW-P5','EW-P6')+' WBN removed; N1 relocated 16 ft west of N2 center-to-center for the new door bay.'
 p.write_text('\n'.join(lines)+'\n')
p=R/'00-project-controls/open-items.md';p.write_text(p.read_text()+'\n| OI-FP-05 | Size and detail the new north door bay between N1 and N2, now 16 ft center-to-center; reconcile door clear width, jambs, header and existing door/wall changes. | The 4-in post envelopes provide 188 in between faces, not a 16-ft clear opening. | Owner / architect / structural engineer | Door selection | draft |\n')
p=R/'00-project-controls/decision-log.md';p.write_text(p.read_text()+'\n| DEC-010 | 2026-09-15 | Remove WBN and place N1 16 ft west of N2 for the new door location. | Center-to-center study interpretation; finished opening remains unresolved. | Owner | ARCH-006 revision 3 | draft |\n')
p=D/'source-inventory.csv'
with p.open(newline='') as f:rd=csv.DictReader(f);fields=rd.fieldnames;rows=list(rd)
for row in rows:
 row['revision']='3';row['sha256']=hashlib.sha256((D/row['file']).read_bytes()).hexdigest()
 if row['file'] in ('README.md','floor-plan-study.pdf'):row['working_source']='../floor-plan-setbacks/update_report_rev3.py'
with p.open('w',newline='') as f:wr=csv.DictWriter(f,fieldnames=fields);wr.writeheader();wr.writerows(rows)
p=R/'document-manifest.csv'
with p.open(newline='') as f:rd=csv.DictReader(f);fields=rd.fieldnames;rows=list(rd)
arch=[]
for row in rows:
 if row['document_id'].startswith('ARCH-006') and row['status']!='superseded':
  old=dict(row);old['document_id']+='-R2';old['status']='superseded';old['report_path']=str((A/Path(row['report_path']).name).relative_to(R));old['notes']+='; Superseded by revision 3';arch.append(old)
  row['notes']='Revision 3; draft; possible ground-floor extension only; SHA256 '+hashlib.sha256((R/row['report_path']).read_bytes()).hexdigest()
  if Path(row['report_path']).name in ('README.md','floor-plan-study.pdf','source-inventory.csv'):row['working_source']='../floor-plan-setbacks/update_report_rev3.py'
with p.open('w',newline='') as f:wr=csv.DictWriter(f,fieldnames=fields);wr.writeheader();wr.writerows(rows+arch)
for page in PdfReader(D/'floor-plan-study.pdf').pages:assert 'Rev 3' in page.extract_text()
for name in ('basis.json','east-wall-floor-plan-basis.json'):
 b=json.loads((D/name).read_text());points=b['possible_ground_floor_extension']['path'];cols={c['id']:(c['x'],c['y']) for c in b['columns']}
 assert [tuple(pt) for pt in points[:5]]==[cols[n] for n in ('WB3','W3','W4','N1','N2')]
assert 'WBN' not in cols
assert cols['N2'][0]-cols['N1'][0]==192
print('Report revision 3 stored; WBN removal and 16-ft spacing verified.')
