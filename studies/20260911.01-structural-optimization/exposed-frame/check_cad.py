import os,sys,json,math
from pathlib import Path
os.environ.setdefault('QT_QPA_PLATFORM','offscreen');os.environ.setdefault('FONTCONFIG_FILE','/etc/fonts/fonts.conf');sys.path.insert(0,'/opt/freecad-1.1.3/usr/lib')
import FreeCAD as A,FreeCADGui as G
P=Path(__file__).resolve().parent;G.showMainWindow();d=A.openDocument(str(P/'Garage-Exposed-Steel.FCStd'));sel=json.loads((P/'selected.json').read_text());cat=json.loads((P/'catalog.json').read_text());g=json.loads((P/'geometry.json').read_text());mm={m['id']:m for m in g['members']};steel=[o for o in d.Objects if hasattr(o,'MemberId')];solids=[o for o in d.Objects if o.TypeId=='PartDesign::Feature' and not o.Shape.isNull()]
assert len(steel)==len(sel)==88
for o in steel:
 assert o.StockSection==cat[sel[o.MemberId]]['aisc_label']
 assert abs(float(o.LengthIn)-mm[o.MemberId]['length_inches'])<1e-5
 assert o.Shape.isValid()
assert all(o.Shape.isValid() for o in solids)
assert all(o.ViewObject.Visibility for o in solids)
(P/'reopen-validation.json').write_text(json.dumps(dict(reopened=True,valid_solids=len(solids),selected_member_count=len(steel),sections_match=True,axis_lengths_match=True,visible_solids=True,units='mm native CAD; source inches'),indent=2))
print('REOPEN VERIFIED',flush=True);os._exit(0)
