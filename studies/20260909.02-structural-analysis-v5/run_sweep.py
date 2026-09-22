import subprocess,os,json
from pathlib import Path
p=Path(__file__).resolve().parent;python='/Applications/FreeCAD.app/Contents/Resources/bin/python'
cases=[('single-161',[161.375]),('single-130',[130]),('single-145',[145]),('single-175',[175]),('single-185',[185]),('single-200',[200]),('two-equal',[130.833333,191.916667]),('two-south',[120,185]),('two-north',[140,205])]
for name,ys in cases:
 e=os.environ.copy();e.update(LAYOUT=name,BEAM_YS=json.dumps(ys));subprocess.run([python,str(p/'test_layout.py')],env=e,check=True)
