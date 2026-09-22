from pathlib import Path
import json,struct,zipfile
R=Path(__file__).resolve().parent
scene=json.loads((R/'site-scene.json').read_text());parts=scene['parts']
source=json.loads((R.parent/'model/scene.json').read_text())['parts']
for p in source:
 if p['group']=='proposal':continue
 q=next(x for x in parts if x['name']==p['name'])
 assert q['vertices']==[[v*.0254 for v in xyz] for xyz in p['vertices']]
 assert q['triangles']==p['triangles']
assert any(p['name']=='Triangular north-facing bay' for p in parts)
assert sum(p['name']=='White pergola post' for p in parts)==6
assert sum(p['name']=='White pergola overhead slat' for p in parts)==15
b=(R/'existing-backyard.glb').read_bytes();magic,version,total=struct.unpack_from('<III',b);assert(magic,version,total)==(0x46546c67,2,len(b));size,_=struct.unpack_from('<II',b,12);g=json.loads(b[20:20+size]);assert len(g['meshes'])==len(parts)
with zipfile.ZipFile(R/'existing-backyard.FCStd') as z:assert 'MeasuredExistingGarage' in z.read('Document.xml').decode()
v=json.loads((R/'validation.json').read_text());v.update(revision=8,original_garage_geometry_preserved=True,triangular_bay=True,pergola_posts=6,pergola_slats=15,glb_container_valid=True,cad_archive_valid=True,viewer_javascript_syntax_valid=True,viewer_browser_verification='not performed; local file URLs blocked by inspection browser')
(R/'validation.json').write_text(json.dumps(v,indent=2))
files=['README.md','existing-backyard.FCStd','existing-backyard.glb','existing-backyard.obj','existing-backyard.mtl','site-viewer.html','site-scene.json','site-review.pdf','site-plan.png','site-overview.png','site-with-trees.png','house-and-pergola.png','build_site.py','render_review.py','export_cad.py','package_review.py','validation.json']
with zipfile.ZipFile(R/'existing-backyard-package.zip','w',zipfile.ZIP_DEFLATED) as z:
 for f in files:z.write(R/f,'existing-backyard/'+f)
print('Revision 8 verified and packaged:',len(parts),'objects')
