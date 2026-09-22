"""Register Chapter 8 artifacts without replacing unrelated report entries."""
from pathlib import Path
import csv, hashlib
ROOT=Path(__file__).resolve().parents[2]; REPORT=ROOT/'report'; C=REPORT/'08-solar-electrical-and-energy'
p=REPORT/'document-manifest.csv'
with p.open() as f: reader=csv.DictReader(f);fields=reader.fieldnames;rows=list(reader)
rows=[r for r in rows if not r['document_id'].startswith('SOL-A')]
for r in rows:
 if r['document_id']=='SOL-001':
  r.update(title='Solar battery sizing and 30-35-40 degree roof analysis',status='draft',working_source='../solar-study/chapter8/build_report.py; ../solar-study/chapter8/analyze_chapter.py',last_verified='2026-09-15',notes='Revision 1; owner-review draft; 325 sqft gross face; includes historical gallery; tariff layout and costs provisional')
for i,path in enumerate(sorted(p for p in C.rglob('*') if p.is_file() and p.name!='solar-energy-report.pdf'),1):
 rel=path.relative_to(REPORT);digest=hashlib.sha256(path.read_bytes()).hexdigest()
 note='Supporting artifact for SOL-001 rev 1; '+('historical source; superseded geometry may appear; ' if 'historical' in str(rel) else '')+'SHA256 '+digest
 rows.append(dict(zip(fields,[f'SOL-A{i:03d}','08',path.name,'draft','Energy/Architectural','Design development','See SOL-001 references and source-inventory.csv',str(rel),'../solar-study/chapter8/build_report.py','2026-09-15',note])))
with p.open('w',newline='') as f:w=csv.DictWriter(f,fields);w.writeheader();w.writerows(rows)
p=REPORT/'00-report-index.md';text=p.read_text();text=text.replace('| Preliminary solar study exists |','| SOL-001 rev 1: consolidated solar/battery report and 30°/35°/40° analysis; draft |')
if '## Chapter 8 research record' not in text:
 text += '\n## Chapter 8 research record\n\n[SOL-001 — Solar, battery and roof design](08-solar-electrical-and-energy/solar-energy-report.pdf), revision 1, 2026-09-15, status `draft`. Includes all recovered solar figures, historical reports, monthly data, new pitch and loft-envelope comparisons, battery dispatch and financial sensitivity. The current 325 ft² face supersedes the older 401 ft² area assumption for this study. Recommendation for review: about 5.6–6.0 kW plus one 13.5 kWh battery; develop 35° while retaining 30° as the height-constrained alternative. [Chapter navigation and source archive](08-solar-electrical-and-energy/README.md).\n'
p.write_text(text)
p=REPORT/'source-map.md';text=p.read_text()
if 'SOL-001 revision 1' not in text:text+='\n## Consolidated solar record\n\nSOL-001 revision 1 is now assembled in [Chapter 8](08-solar-electrical-and-energy/README.md). Its source archive preserves the solar studies and related roof-option sources, with a checksummed inventory. Reproduction code is in `../solar-study/chapter8/`. Historical capacity estimates based on about 401 ft² do not establish fit on the newer 325 ft² solar face.\n'
p.write_text(text)
p=REPORT/'00-project-controls/open-items.md';text=p.read_text()
if 'OI-SOL-01' not in text:text+='\n| OI-SOL-01 | Review SOL-001 recommendation: 5.6–6.0 kW plus one 13.5 kWh battery; 35° with clerestory/cap coordination. | Owner must select system and roof; no decision adopted by report. | Owner / architect / solar designer | Roof freeze | draft |\n| OI-SOL-02 | Produce physical module/access layout for 325 ft² gross face and check cap/clerestory shading. | Area-based capacity does not prove panel fit. | Solar designer / architect | Equipment selection | draft |\n| OI-SOL-03 | Confirm generation provider, rate plan, export vintage, interval demand, current quotes and rebate eligibility. | Financial margin is narrower than input uncertainty. | Owner / solar designer | Procurement | draft |\n'
p.write_text(text)
p=REPORT/'00-project-controls/assumptions-register.md';text=p.read_text()
if 'ASM-SOL-01' not in text:text+='\n| ASM-SOL-01 | SOL-001 uses 325 ft² gross solar face, 281.5-in width, 249-in wall length, 63-in south offset, 9-ft low edge, 9-ft-8-in floor and 17-ft-8-in cap eave. | Angle/loft comparison | CAD generations or surveyed envelope may differ | Coordinate survey and selected roof/CAD; reconcile OI-016 | draft |\n| ASM-SOL-02 | One 13.5 kWh battery, 10% reserve, 90% round-trip efficiency, 5 kW charge/discharge limit, perfect-foresight solar-only dispatch; retained tariff and cost allowances. | SOL-001 comparative economics | Actual equipment controls rates and cost differ | Vendor design plus interval-data and actual-tariff rerun | draft |\n'
p.write_text(text)
print('Registered',len(rows),'total report entries')
