from pathlib import Path
import zipfile,hashlib,json
R=Path(__file__).resolve().parent
files=[p for p in R.iterdir() if p.suffix in ['.blend','.json','.py','.md','.png']]
with zipfile.ZipFile(R/'Backyard-Blender-Proposed-Package.zip','w',zipfile.ZIP_DEFLATED) as z:
 for f in files:z.write(f,'Backyard-Proposed/'+f.name)
 for n in ['BACKYARD-EXISTING-CONDITIONS.md','Backyard-Existing-Conditions.pdf']:
  f=R.parent/'backyard-blender'/n
  if f.exists():z.write(f,'Backyard-Proposed/baseline-reference/'+n)
 z.writestr('Backyard-Proposed/file-hashes.json',json.dumps({f.name:hashlib.sha256(f.read_bytes()).hexdigest() for f in files},indent=2))
