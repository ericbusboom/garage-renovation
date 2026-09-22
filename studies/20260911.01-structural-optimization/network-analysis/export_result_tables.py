import csv,json,os
from pathlib import Path
P=Path(os.environ.get('GARAGE_NETWORK_REPORT_DIR',str(Path(__file__).resolve().parent)))
with open(P/'member-axial-results.csv','w') as f:
 w=csv.writer(f);w.writerow(['truss','stage','case','physical_member','maximum_compression_lb','maximum_tension_lb'])
 for p in sorted(P.glob('*-results.json')):
  r=json.loads(p.read_text());d=json.loads((P/r['input_network']).read_text())
  for case,res in r['cases'].items():
   rows={}
   for e in res['element_forces'].values():
    if e['kind']=='connection_offset':continue
    row=rows.setdefault(e['physical_member'],[0.,0.]);v=e['axial_mid_lb'];row[0]=max(row[0],v);row[1]=max(row[1],-v)
   for mid,values in rows.items():w.writerow([d['truss'],d['stage'],case,mid,*values])
print('member-axial-results.csv written; bending/torsion/end actions retained in full results JSON')
