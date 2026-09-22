"""Six-page coordinated review: section/plan plus every currently named truss.
Projects actual model member meshes to their elevation planes. Not an engineering design.
"""
from pathlib import Path
import json,math
import numpy as np
from scipy.spatial import ConvexHull
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
from matplotlib.backends.backend_pdf import PdfPages
ROOT=Path(__file__).parent
# Reuse the current code-native combined sheet, retaining its Figure as page one.
s=(ROOT/'draw_combined_review.py').read_text();exec(s.split('plt.close(fig)')[0])
pages=[fig]
model=json.loads((ROOT.parent/'model-renders/garage-model.json').read_text())
H=98.5;F=107.25;BR=model['basis']['break_y_from_south_wall']
orange='#a25b32';grey='#65747a';green='#397765'
def rf(y):return min(106.5+(y+63)*math.tan(math.pi/6),227.25)
def fmt(v):
 q=round(v*8);feet=q//96;rem=q%96;inc=rem//8;fra=['','⅛','¼','⅜','½','⅝','¾','⅞'][rem%8]
 return f'{feet}′ {inc}{fra}″'
def dimension(ax,a,b,z,label):
 ax.annotate('',xy=(a,z),xytext=(b,z),arrowprops=dict(arrowstyle='<->',color=grey,lw=.8))
 ax.text((a+b)/2,z,label,ha='center',va='center',fontsize=10,color=grey,bbox=dict(fc='white',ec='none',pad=2))
for name,axis,a,b,top in [('T-S',0,0,246.5,rf(0)),('T1',0,0,224.25,rf(69.75)),('T-W',1,-63,253,227.25),('T-E',1,-63,253,227.25),('T-N',0,-32,249.5,227.25)]:
 fig=plt.figure(figsize=(17,11));ax=fig.add_axes([.06,.31,.88,.50]);figs=fig
 objs=[o for o in model['objects'] if o['group']=='frame' and o['material']=='truss' and (o['name'].startswith(name+' ') or (name=='T-W' and o['name']=='French door header'))]
 assert objs,name
 for o in objs:
  v=np.array(o['vertices'])/.0254;p=v[:,[axis,2]];p[:,1]-=H
  try:poly=p[ConvexHull(p).vertices]
  except:continue
  ax.add_patch(Polygon(poly,fc=orange,ec=orange,lw=.3))
 if axis==1:
  ax.plot([a,BR,b],[rf(a)-H,rf(BR)-H,rf(b)-H],lw=.6,color=green,ls='--')
  heights=[(0,rf(0)-H),(69.75,rf(69.75)-H),(BR,128.75),(253,128.75)]
  station='South → north · station zero = south exterior garage wall'
  stations=sorted(set([-63,-21.25,0,69.75,BR,185,253]+([186,246] if name=='T-W' else [126])))
  rows=['UPRIGHT STATIONS FROM SOUTH WALL (in): '+', '.join(f'{x:.2f}'.rstrip('0').rstrip('.') for x in stations),
        'PANEL SPACINGS (in): '+', '.join(f'{y-x:.2f}'.rstrip('0').rstrip('.') for x,y in zip(stations[:-1],stations[1:])),
        'DEPTHS: south tip 8″; south wall '+fmt(rf(0)-H)+'; at T1 '+fmt(rf(69.75)-H)+'; plateau '+fmt(128.75)+'.',
        'West door header is included.' if name=='T-W' else 'Support axis: N2 / S2 / optional S3.']
  if name=='T-W':rows[-1]+=' Closely spaced uprights at 185 / 186 in are retained from the model; opening framing needs coordination.'
 else:
  station='West → east · dimensions along the framing line'
  heights=[]
  if name in ['T-S','T1']:
   n=6;spacing=(b-a)/n
   for i in range(n):dimension(ax,a+i*spacing,a+(i+1)*spacing,top-H+14,fmt(spacing))
   rows=['Six equal panel bays; dimensions are centerline spacing, not clear openings.',
         'Model layout: verticals throughout; diagonals in the two end bays; central storage bays open.',
         'At station '+('0″ (south wall).' if name=='T-S' else '69¾″ north of south wall.'),
         'End-braced rectangles require engineered moment joints / Vierendeel action; web layout is illustrative.']
  else:
   ax.plot([a,b],[F-H,F-H],ls='--',color=green,lw=.8)
   dimension(ax,81.5,113.5,85,'32″ door width')
   rows=['UPRIGHT STATIONS X (in): -32, 53.25, 81.5, 113.5, 224.25, 249.5.',
         'HEADER: nominal 24″ deep; eight equal bays of 35 3/16 in. Door: 32″ wide × 84″ high above loft floor.',
         'DOOR center X = 97½″; opening edges X = 81½″ / 113½″. Floor is 8¾″ above common truss bottom.',
         'North wall windows and side webs require coordination. Overall truss includes west walkway width; it is not loft-floor width.']
 dimension(ax,a,b,-20,fmt(b-a)+' overall framing-line length')
 ax.annotate('',xy=(b+16,0),xytext=(b+16,top-H),arrowprops=dict(arrowstyle='<->',lw=.8,color=grey))
 ax.text(b+23,(top-H)/2,fmt(top-H)+' maximum height',rotation=90,ha='center',va='center',fontsize=10,color=grey)
 for x,h in heights:
  ax.plot([x,x],[0,h],ls=':',color=grey,lw=.65)
 ax.axhline(0,lw=.7,color=grey)
 ax.set(xlim=(a-12,b+47),ylim=(-32,top-H+30),aspect='equal');ax.axis('off')
 fig.text(.06,.93,name+' · TRUSS ELEVATION',fontsize=24,fontweight='bold',color='#253744')
 fig.text(.06,.884,station+' · member layout projected directly from the current 3D model',fontsize=11,color=grey)
 fig.text(.06,.267,'COMMON BOTTOM = 8′ 2½″ ABOVE GROUND · COLUMN-SUPPORTED',fontsize=12,fontweight='bold',color=orange)
 fig.text(.06,.222,'\n'.join(rows),fontsize=10,linespacing=1.7,color='#354952',va='top')
 fig.text(.06,.065,'Concept geometry, not fabrication drawings. Member sizes, joints, bracing and bearing details require design.\nThe shallow hip roof cap sits above the rear ceiling datum; its internal framing has not been laid out.',fontsize=10,color=grey,linespacing=1.6)
 for ext in ['png','svg','pdf']:fig.savefig(ROOT/f'{name}-truss-elevation.{ext}',dpi=150)
 pages.append(fig)
with PdfPages(ROOT/'section-and-plan.pdf') as pdf:
 for f in pages:pdf.savefig(f)
with PdfPages(ROOT/'all-truss-elevations.pdf') as pdf:
 for f in pages[1:]:pdf.savefig(f)
for f in pages:plt.close(f)
print('Created six-page set; five named trusses from actual model meshes. Loft:224.25 x183 in =',224.25*183/144,'sq ft')
