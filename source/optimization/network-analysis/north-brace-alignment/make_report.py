import json,os,zipfile
from pathlib import Path
os.environ['MPLCONFIGDIR']='/private/tmp/garage-network-mpl'
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
P=Path(__file__).resolve().parent;checks=json.loads((P/'geometry-checks.json').read_text());v=json.loads((P/'validation.json').read_text());r=json.loads((P/'global-complete-PDelta.json').read_text())
notes='North ground-brace alignment correction\n\nBoth X-braces between W4 and N1 / U-W were offset 4 inches north of\nthe column axes. All four brace endpoints now coincide with those axes.\nThe analytical offset links at those four connections are eliminated.\nAttachment heights remain at 6 inches and 115 inches above datum.\n\nW4 is at north-coordinate 253 inches; N1 is at 252.5 inches. The braces\nfollow the plane between those columns, including that half-inch difference.\nThe TN truss above remains in its existing plane at north-coordinate 249 inches.\nIts short connections to the posts are separate from this ground-brace correction.\n\nThe corrected over-door mini-truss and every other physical member are unchanged.\nBoth construction stages and the final second-order analysis were rerun.\nThe whole-frame network contains each column and brace once.\n\nThese are structural centerlines. Gussets, brace crossing clearance, bolts,\nwelds and foundations remain to be detailed; this is not a fabrication drawing.'
with PdfPages(P/'North-Brace-Alignment.pdf') as pdf:
 f=plt.figure(figsize=(11,8.5));f.text(.07,.92,notes,fontsize=12,linespacing=1.5,va='top');f.text(.07,.08,f"Export replay verified {sum(x['cases'] for x in v.values())} combinations. Maximum partial second-order screen: {r['max_member_screen_ratio']:.3f}.\nThe screen excludes the 125 psf storage sensitivity; it is not complete design approval.",fontsize=10);pdf.savefig(f);plt.close(f)
 for name in ['TN-wall','NORTH-wall','TN-door-detail','ALL-wall']:
  f,ax=plt.subplots(figsize=(14,10 if name!='TN-door-detail' else 6));ax.imshow(plt.imread(P/(name+'.png')));ax.axis('off');f.subplots_adjust(0,0,1,1);pdf.savefig(f,dpi=170);plt.close(f)
(P/'README.md').write_text('# North brace alignment\n\n'+notes+'\n\nOpen North-Brace-Alignment.pdf, TN-door-detail.png, or TN-interactive.html. complete.network.json and roof_first.network.json contain the globally solved networks with all applied loads and supports. verify_and_draw.py replays these networks; make_geometry.py and solve.py require the parent project and previous clean-layout geometry.\n')
with zipfile.ZipFile(P/'North-Brace-Alignment-Package.zip','w',zipfile.ZIP_DEFLATED) as z:
 for p in P.iterdir():
  if p.is_file() and p.suffix!='.zip':z.write(p,p.name)
 z.write(P.parent/'requirements-lock-macos.txt','requirements-lock-macos.txt')
print('Report and package complete')
