import json,os,csv,zipfile
from pathlib import Path
os.environ['MPLCONFIGDIR']='/private/tmp/garage-network-mpl'
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
P=Path(__file__).resolve().parent
r=json.loads((P/'global-complete-PDelta.json').read_text());v=json.loads((P/'validation.json').read_text())
rows=list(csv.DictReader(open(P/'column-reactions.csv')));service=[x for x in rows if x['case']=='service_patches']
notes='''TN now has one horizontal top chord at 224.25 in (18 ft 8 1/4 in) above datum.
The hip-cap roof remains separate; its roof load allowance is retained.
N1 / U-W is the existing full-height ground column beside the loading door.
The upper east jamb bears on TN; no ground column is added in the garage opening.

Columns appear in multiple wall views but occur ONCE in the global model.
Shared posts carry combined actions; reactions are not arbitrarily divided in half.
T1 is supported by TE and TW, not by new ground columns beneath T1.
All wall images are native PyNite views filtered from the solved global model.
They are not independently solved frames with invented supports at cut edges.

Model assumptions: fixed bases, moment-connected frame members and offset links.
The nine foundations, connections and site wind/seismic loads still need design.
This is a preliminary analytical model, not a construction-ready design.'''
with PdfPages(P/'Grounded-Truss-Walls.pdf') as pdf:
 f=plt.figure(figsize=(11,8.5));f.text(.07,.92,'Trusses and their ground supports',fontsize=22);f.text(.07,.82,notes,fontsize=11,linespacing=1.6,va='top');f.text(.07,.13,f"Global second-order partial member screen: {r['max_member_screen_ratio']:.3f}\nSteel model weight: {r['steel_weight_lb']:,.0f} lb. Export replay: {sum(a['cases'] for a in v.values())} load combinations verified.\nScreen excludes the 125 psf storage sensitivity and is not a complete code check.",fontsize=10);pdf.savefig(f);plt.close(f)
 for group in ['TN','TE','TW','TS','T1','ALL']:
  f,ax=plt.subplots(figsize=(14,10));ax.imshow(plt.imread(P/(group+'-wall.png')));ax.axis('off');f.subplots_adjust(0,0,1,1);pdf.savefig(f,dpi=160);plt.close(f)
 f,ax=plt.subplots(figsize=(11,8.5));ax.axis('off');ax.set_title('Total column reactions — service storage patches',fontsize=18,pad=25)
 tab=ax.table(cellText=[[x['column'],f"{float(x['vertical_Fy_lb']):,.0f}"] for x in service],colLabels=['Ground column','Vertical reaction (lb)'],loc='center',cellLoc='center');tab.auto_set_font_size(False);tab.set_fontsize(13);tab.scale(1,2.3)
 f.text(.13,.1,'Positive = upward support reaction on the frame (compression into foundation).\nNegative = downward hold-down reaction (uplift tendency). Values include all attached members.\nSee CSV for every force and moment component and every load combination.',fontsize=10);pdf.savefig(f);plt.close(f)
(P/'README.md').write_text('# Ground-supported truss views\n\n'+notes+'\n\nOpen Grounded-Truss-Walls.pdf or the interactive HTML views.\ncomplete.network.json and roof_first.network.json contain the entire unique global network, real ground supports, applied loads and reference displacements/reactions.\nRun verify_and_draw.py with the parent requirements-lock-macos.txt runtime to replay and render. update_and_solve.py requires the parent project solver and catalog.\n\ncolumn-reactions.csv contains global linear reactions; global-complete-PDelta.json contains the second-order analysis and partial member screens. All results are preliminary.\n')
with zipfile.ZipFile(P/'Grounded-Walls-Package.zip','w',zipfile.ZIP_DEFLATED) as z:
 for p in P.iterdir():
  if p.is_file() and p.suffix!='.zip':z.write(p,p.name)
 z.write(P.parent/'requirements-lock-macos.txt','requirements-lock-macos.txt')
print('PDF/package complete')
