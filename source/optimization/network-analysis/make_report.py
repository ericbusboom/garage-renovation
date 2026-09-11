"""Assemble native PyNite/PyVista screenshots into a PDF; no redrawn structure."""
import os,json
from pathlib import Path
os.environ['MPLCONFIGDIR']='/private/tmp/garage-network-mpl'
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
P=Path(os.environ.get('GARAGE_NETWORK_REPORT_DIR',str(Path(__file__).resolve().parent)))
rows=[]
for g in ['TE','TW','TN','TS','T1']:
 for stage in ['complete','roof_first']:
  r=json.loads((P/(g+'-'+stage+'-results.json')).read_text());case='service_patches' if stage=='complete' else 'roof_first_service'
  rows.append([g,stage,str(r['audit']['nodes']),str(r['audit']['elements']),str(r['audit']['connected_components']),f"{r['cases'][case]['max_vertical_displacement_in']:.3f}"])
with PdfPages(P/'Native-Truss-Networks.pdf') as pdf:
 f=plt.figure(figsize=(11,8.5));f.text(.07,.9,'Trusses drawn by the analysis program',fontsize=23);f.text(.07,.84,'PyNiteFEA 3.0.0 + native PyVista rendering',fontsize=14)
 f.text(.07,.77,'Every image comes from the model PyNite actually solved.\nAll connection-offset elements are included; no custom centerline drawing.\nEach network is connected and independently reconstructed from its JSON data file.',fontsize=11,linespacing=1.5)
 ax=f.add_axes([.07,.33,.86,.32]);ax.axis('off');t=ax.table(cellText=rows,colLabels=['Truss','Stage','Nodes','Elements','Components','Max |vertical| in'],cellLoc='center',bbox=[0,0,1,1]);t.auto_set_font_size(False);t.set_fontsize(10)
 f.text(.07,.27,'Displacements shown for completed storage service load or roof-first service load.\nThey include movement of the surrounding frame, not just truss deflection between bearings.',fontsize=10)
 f.text(.07,.20,'Whole-frame second-order screen: max partial member ratio 0.83; max floor-support movement 0.55 in.',fontsize=10)
 f.text(.07,.09,'Proposed corrections: join TE/TW upper chords at the slope transition; connect TN jamb base.\nWhole-frame analysis was refreshed, then each truss independently solved and verified.\nThe three connections remain proposed details; their stiffness assumptions are explicit.\nBoundary glyphs are imposed movements, not new ground supports.\nPRELIMINARY: connection detailing, global iteration and capacity checks remain.',fontsize=10,linespacing=1.5)
 pdf.savefig(f);plt.close(f)
 for g in ['TE','TW','TN','TS','T1']:
  for stage in ['complete','roof_first']:
   f,axes=plt.subplots(2,1,figsize=(12,12),layout='constrained')
   for ax,mode in zip(axes,['network','deformed']):ax.imshow(plt.imread(P/(g+'-'+stage+'-'+mode+'.png')));ax.axis('off')
   pdf.savefig(f,dpi=170);plt.close(f)
print('Native-Truss-Networks.pdf complete')
