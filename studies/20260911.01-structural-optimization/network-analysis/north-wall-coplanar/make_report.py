import json,os,zipfile
from pathlib import Path
os.environ['MPLCONFIGDIR']='/private/tmp/garage-network-mpl'
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
P=Path(__file__).resolve().parent;checks=json.loads((P/'geometry-checks.json').read_text());v=json.loads((P/'validation.json').read_text());r=json.loads((P/'global-complete-PDelta.json').read_text())
notes='Entire north-wall frame aligned\n\nTN chords, webs, door header and jambs, north braces, W4, N1 and N2\nnow occupy one plane at north-coordinate 253 inches.\nTN moved 4 inches north; N1 moved 0.5 inch north to align with W4/N2.\nAll 36 internal north-wall connections now have coincident member axes.\n\nThe east-end vertical and diagonals now terminate at actual chord nodes.\nThe upper door jamb meets the bottom chord directly.\nThe five-inch height difference between TE and TN bottom chords is carried\nby the real N2 column segment; the redundant offset link was removed.\nColumns retain their existing extensions above the top chord.\n\nTE, TW and TS member geometry is unchanged. TE/TW rear connections now\nmeet TN at their ends. Floor load distribution uses the actual TN support\nstation (253 inches) with the same loaded floor area and load intensities.\n\nBoth stages and final second-order analysis were rerun. The revised global\nnetwork has been replayed independently across 70 load combinations.\n\nThese are analytical centerlines, not fabrication details. Connection hardware,\nfoundations, roof-brace crossing details and full code checks remain unresolved.'
with PdfPages(P/'Aligned-North-Wall.pdf') as pdf:
 f=plt.figure(figsize=(11,8.5));f.text(.07,.92,notes,fontsize=12,linespacing=1.5,va='top');f.text(.07,.08,f"Export replay verified {sum(x['cases'] for x in v.values())} combinations. Maximum partial second-order screen: {r['max_member_screen_ratio']:.3f}.\nThe screen excludes the 125 psf storage sensitivity; it is not complete design approval.",fontsize=10);pdf.savefig(f);plt.close(f)
 for name in ['TN-wall','NORTH-wall','TN-door-detail','ALL-wall']:
  f,ax=plt.subplots(figsize=(14,10 if name!='TN-door-detail' else 6));ax.imshow(plt.imread(P/(name+'.png')));ax.axis('off');f.subplots_adjust(0,0,1,1);pdf.savefig(f,dpi=170);plt.close(f)
(P/'README.md').write_text('# Whole north-wall alignment\n\n'+notes+'\n\nOpen Aligned-North-Wall.pdf, TN-door-detail.png, or TN-interactive.html. complete.network.json and roof_first.network.json contain the globally solved networks with all applied loads and supports. verify_and_draw.py replays these networks; make_geometry.py and solve.py require the parent project and previous clean-layout geometry.\n')
with zipfile.ZipFile(P/'Aligned-North-Wall-Package.zip','w',zipfile.ZIP_DEFLATED) as z:
 for p in P.iterdir():
  if p.is_file() and p.suffix!='.zip':z.write(p,p.name)
 z.write(P.parent/'requirements-lock-macos.txt','requirements-lock-macos.txt')
print('Report and package complete')
