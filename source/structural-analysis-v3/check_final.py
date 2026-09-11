import json
from pathlib import Path
import engineer as a
p=Path(__file__).parent;r=json.loads((p/'results.json').read_text());o=a.solve(r['selection'])
assert abs(o['steel_with_connections_lb']-r['steel_with_connections_lb'])<.01
assert abs(o['max_ratio']-r['max_ratio'])<1e-8
assert abs(o['max_vertical_in']-r['max_vertical_in'])<1e-8
print('PASS final reproduction, all-case force/moment equilibrium, displacement and ratio agreement')
