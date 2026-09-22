import json
from pathlib import Path
import analyze_network as runner
P=Path(__file__).resolve().parent;runner.P=P/'connected-candidate'
reports=[]
for path in sorted(runner.P.glob('*.network.json')):
 reports.append(runner.run(path,False))
(runner.P/'run-validation.json').write_text(json.dumps(reports,indent=2))
for path in sorted(runner.P.glob('*.network.json')):
 d=json.loads(path.read_text());case='service_patches' if d['stage']=='complete' else 'roof_first_service'
 runner.render(runner.model_from_file(d,case),d,case,path.name.replace('.network.json',''),modes=['network','deformed'])
