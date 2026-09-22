import os,json,zipfile
from pathlib import Path
os.environ['MPLCONFIGDIR']='/private/tmp/garage-network-mpl'
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
P=Path(__file__).resolve().parent;N=P/'networks';summary=json.loads((P/'summary.json').read_text());validation=json.loads((N/'run-validation.json').read_text())
assert len(validation)==10 and sum(v['cases'] for v in validation)==350
assert all(summary['load_allowances_unchanged'].values())
with PdfPages(P/'Two-Chord-Trusses.pdf') as pdf:
 f=plt.figure(figsize=(11,8.5));f.text(.07,.9,'TE and TW — two straight upper chords',fontsize=22)
 f.text(.07,.8,'One long sloping run beneath the solar roof.\nOne long horizontal run beneath the separate lightweight hip cap.',fontsize=15,linespacing=1.5)
 f.text(.07,.63,'Horizontal chord axis: 224.25 in above datum (18 ft 8¼ in).\nHorizontal run: 130.24 in (approximately 10 ft 10¼ in).\nThe existing sloping runs are retained; each meets its horizontal run at a single knee.\nThe hip-cap outline and its roof-load allowance remain unchanged.',fontsize=12,linespacing=1.55)
 f.text(.07,.4,f"Whole-frame second-order analysis: solved.\nMaximum partial member-check ratio: {summary['max_partial_member_screen_ratio']:.3f}\nMaximum modeled floor-support movement: {summary['max_service_floor_support_movement_in']:.2f} in\nIndependent verification: 10 networks, 350 load-case solves.\nPrimary steel: {summary['steel_weight_lb']:,.0f} lb; stock sizes unchanged.",fontsize=12,linespacing=1.55)
 f.text(.07,.11,'The separate sheet-metal hip-cap frame is not sized here. Suggested 1 in, 11-gauge tubing\nis not an approved section. Existing load allowances include the cap; verify its eventual takeoff.\nPreliminary model: connection detailing, bracing, foundations and site/code loads remain to verify.\nAll diagrams are rendered directly from the PyNite model, including connection-offset members.',fontsize=10,linespacing=1.4)
 pdf.savefig(f);plt.close(f)
 for g in ['TE','TW','TN','TS','T1']:
  for stage in ['complete','roof_first']:
   f,axs=plt.subplots(2,1,figsize=(12,12),layout='constrained')
   for ax,mode in zip(axs,['network','deformed']):ax.imshow(plt.imread(N/f'{g}-{stage}-{mode}.png'));ax.axis('off')
   pdf.savefig(f,dpi=170);plt.close(f)
with zipfile.ZipFile(P/'Two-Chord-Network-Package.zip','w',zipfile.ZIP_DEFLATED) as z:
 for path in sorted(N.iterdir()):
  if path.is_file():z.write(path,path.name)
 for name in ['analyze_network.py','requirements.txt','requirements-lock-macos.txt']:z.write(P.parent/name,name)
 for name in ['README.md','summary.json','Two-Chord-Trusses.pdf']:z.write(P/name,name)
print('Two-chord PDF and standalone network package written')
