import sys,json
from pathlib import Path
P=Path(__file__).resolve().parent;sys.path.insert(0,str(P.parent));import analyze_network as runner
runner.P=P/'networks'
reports=[runner.run(path,False) for path in sorted(runner.P.glob('*.network.json'))]
(runner.P/'run-validation.json').write_text(json.dumps(reports,indent=2))
for path in sorted(runner.P.glob('*.network.json')):
 d=json.loads(path.read_text());case='service_patches' if d['stage']=='complete' else 'roof_first_service'
 runner.render(runner.model_from_file(d,case),d,case,path.name.replace('.network.json',''),modes=['network','deformed'])
print('Two-chord variant: all networks solved and rendered')
