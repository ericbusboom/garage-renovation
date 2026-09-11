import json,os,zipfile
from pathlib import Path
os.environ['MPLCONFIGDIR']='/private/tmp/garage-network-mpl'
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
P=Path(__file__).resolve().parent;checks=json.loads((P/'geometry-checks.json').read_text());v=json.loads((P/'validation.json').read_text());r=json.loads((P/'global-complete-PDelta.json').read_text())
notes='''TN over-door mini-truss correction

The bottom chord/header now runs level between the support axes.
Four equal 25.5-inch panels span 102 inches (8 ft 6 in) between those axes.
Chord axes are at 207 and 224.25 inches above datum: 17.25 inches apart.
These are structural centerline dimensions, not the clear finished door opening.

All mini-truss diagonals and verticals now terminate exactly on chord nodes.
The east upper jamb reaches the upper chord. The short sloping header-end
connection that caused the visible uptick has been removed.

N1 / U-W is 3.5 inches north of the TN plane. Its connection is an explicit
out-of-plane centroid offset, not a gap or an upward-sloping header end.
The right jamb remains above the loft; no ground post was added in the door.

TE, TW and TS physical geometry and section choices are unchanged.
Both stages and the final second-order whole-frame analysis were rerun.
Connections, welds, bolts, foundations, roof-brace crossings and site/code
requirements remain preliminary. These are analytical centerline drawings.'''
with PdfPages(P/'Corrected-TN-Door-Truss.pdf') as pdf:
 f=plt.figure(figsize=(11,8.5));f.text(.07,.92,notes,fontsize=12,linespacing=1.5,va='top');f.text(.07,.08,f"Export replay verified {sum(x['cases'] for x in v.values())} combinations. Maximum partial second-order screen: {r['max_member_screen_ratio']:.3f}.\nThe screen excludes the 125 psf storage sensitivity; it is not complete design approval.",fontsize=10);pdf.savefig(f);plt.close(f)
 for name in ['TN-door-detail','TN-wall','TE-wall','TW-wall','TS-wall','T1-wall','ALL-wall']:
  f,ax=plt.subplots(figsize=(14,10 if name!='TN-door-detail' else 6));ax.imshow(plt.imread(P/(name+'.png')));ax.axis('off');f.subplots_adjust(0,0,1,1);pdf.savefig(f,dpi=170);plt.close(f)
(P/'README.md').write_text('# TN door mini-truss correction\n\n'+notes+'\n\nOpen Corrected-TN-Door-Truss.pdf, TN-door-detail.png, or TN-interactive.html. complete.network.json and roof_first.network.json contain the globally solved networks with all applied loads and supports. verify_and_draw.py replays these networks; make_geometry.py and solve.py require the parent project and previous clean-layout geometry.\n')
with zipfile.ZipFile(P/'Corrected-TN-Package.zip','w',zipfile.ZIP_DEFLATED) as z:
 for p in P.iterdir():
  if p.is_file() and p.suffix!='.zip':z.write(p,p.name)
 z.write(P.parent/'requirements-lock-macos.txt','requirements-lock-macos.txt')
print('Report and package complete')
