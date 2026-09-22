from pathlib import Path
import runpy
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon,Rectangle
from matplotlib.backends.backend_pdf import PdfPages
R=Path(__file__).resolve().parent
figures=[]
for kind in ['cornice','hip']:
 s=runpy.run_path(str(R/'build_window_options.py'));fig=s['fig'];axes=s['axes'];z=s['z'];L=s['L'];YB=s['YB'];line=s['line'];ink=s['ink']
 for ax in axes:
  ax.set_xlim(-25,294);ax.set_ylim(-25,280)
  # Preserve the solar slope. Overlay only the new rear cap and its cornice.
  if kind=='cornice':
   north=-12;south=90;topN=z(L)+3;topS=z(YB)+3
   profile=[(north,topN),(south,topS),(south,topS-10),(north,topN-10)]
   ax.add_patch(Polygon(profile,facecolor='white',edgecolor=ink,lw=1.1,zorder=8))
   line(ax,[(north-1,topN),(south+1,topS)],lw=2.2,zorder=9)
   line(ax,[(north,topN-3),(south,topS-3)],lw=.7,zorder=9)
   line(ax,[(north+2,topN-8),(south-2,topS-8)],lw=.7,zorder=9)
   ax.annotate('12″ north + west projection*\n10″ layered white fascia*',xy=(-9,topN-5),xytext=(6,269),fontsize=8,color='#326e8b',arrowprops=dict(arrowstyle='-',color='#326e8b'))
  else:
   north=-16;south=94;base=z(L)+2;peak=base+8
   ax.add_patch(Polygon([(north,base),(18,peak),(60,peak),(south,base)],facecolor='#8c9aa2',edgecolor=ink,lw=1.1,zorder=8))
   ax.add_patch(Rectangle((north,base-8),110,8,facecolor='white',edgecolor=ink,lw=1,zorder=8))
   ax.plot([north,south],[base-2,base-2],color=ink,lw=.7,zorder=9)
   ax.annotate('Low hip · 8″ rise*\n16″ north + west projection*',xy=(18,peak),xytext=(8,269),fontsize=8,color='#326e8b',arrowprops=dict(arrowstyle='-',color='#326e8b'))
  # Deliberate loft ventilation: controllable wall louvers below cornice.
  ventY=205
  ax.add_patch(Rectangle((12,ventY),54,9,facecolor='white',edgecolor=ink,lw=.8,zorder=10))
  for yy in [ventY+2,ventY+4,ventY+6]:ax.plot([14,64],[yy,yy],color='#5b737d',lw=.65,zorder=11)
  ax.annotate('High-level loft vent*',xy=(40,210),xytext=(112,216),fontsize=8,color='#326e8b',arrowprops=dict(arrowstyle='-',color='#326e8b'))
 # Replace prior page text, keeping both window variants visibly labeled.
 for t in list(fig.texts):t.remove()
 fig.text(.05,.96,('1 · Projecting shallow cap and layered cornice' if kind=='cornice' else '2 · Low hipped cap and projecting soffit'),ha='left',fontsize=22)
 fig.text(.05,.90,'WEST ELEVATIONS · both window options retained · white walkway / balcony below',fontsize=12,color='#326e8b')
 fig.text(.05,.14,'A: one 30″ × 36″ window.\nB: three 18″ squares stepping down with the solar slope.',fontsize=11,color=ink)
 fig.text(.54,.14,'* New cap, vent and trim dimensions are exploratory.\nOverhang on north and west only; east setback edge stays tight.',fontsize=11,color=ink)
 fig.text(.05,.055,'Loft louvers shown as a concept; pair with controllable inlet openings. Roof-cavity ventilation is a separate system design.',fontsize=10,color='#326e8b')
 for ext in ['png','svg']:fig.savefig(R/f'cap-{kind}-window-options.{ext}',dpi=180,facecolor='white')
 figures.append(fig)
# Solar finish diagram separates active rectangles from purpose-made non-active edges.
f,ax=plt.subplots(figsize=(12,8));ax.set_aspect('equal');ax.axis('off');ax.set_xlim(-10,135);ax.set_ylim(-18,102)
shape=Polygon([(0,0),(100,0),(82,78),(0,78)],facecolor='#344c5b',edgecolor=ink,lw=1.5);ax.add_patch(shape)
for row in range(4):
 for col in range(5):
  x=col*20;y=row*19.5;right=100-18*((y+19.5)/78)
  if x+20<=right+.001:
   ax.add_patch(Rectangle((x+.6,y+.6),18.8,18.3,facecolor='#344c5b',edgecolor='#a3b1b8',lw=.7))
  else:
   poly=Polygon([(x,y),(min(x+20,100-18*y/78),y),(min(x+20,right),y+19.5),(x,y+19.5)],facecolor='#344c5b',edgecolor='#a3b1b8',lw=.7,hatch='///')
   if x<right:ax.add_patch(poly);poly.set_clip_path(shape)
ax.text(0,94,'One glossy roof surface · two panel types',fontsize=19)
ax.text(0,86,'Diagram in the roof plane · illustrative joints, not a panel schedule',fontsize=10,color='#326e8b')
ax.annotate('Active rectangular\nPV modules',xy=(30,40),xytext=(105,56),fontsize=11,arrowprops=dict(arrowstyle='-',color=ink))
ax.annotate('Shaped non-active\nmatching infill',xy=(91,25),xytext=(105,24),fontsize=11,arrowprops=dict(arrowstyle='-',color=ink))
ax.text(0,-9,'Hatching identifies infill in this drawing only; installed finish should match in color and gloss.',fontsize=10)
ax.text(0,-15,'Custom infill material, glazing, attachment and flashings TBD; active modules remain uncut.',fontsize=10)
for ext in ['png','svg']:f.savefig(R/f'solar-active-infill.{ext}',dpi=180,facecolor='white')
figures.append(f)
with PdfPages(R/'cap-and-solar-options.pdf') as pdf:
 for fig in figures:pdf.savefig(fig)
(R/'cap-options-notes.md').write_text('''# Rear-cap and solar infill studies
Both west window options are retained. New files are alternatives, not changes to the CAD model.

1. Shallow cap: 12-inch north/west overhang, 10-inch layered fascia. Top is 3 inches above preceding cap datum. Approximate north high point 19 ft 6.75 in.
2. Low hipped cap: 16-inch north/west projection, 8-inch fascia, 8-inch rise above an eave placed 2 inches above preceding cap datum. Approximate high point 20 ft 1.75 in. Ridge arrangement and east transition require roof-plan development.

No added east overhang because of the stated tight setback. Dimensions, high-level controllable loft louvers and ventilation capacities are unvalidated design trials. Room ventilation uses inlet/outlet openings; a vented roof cavity, if selected, is a separate path. Product selection must account for the user's stated fire concerns.

South solar finish: rectangular active PV modules with custom matching glossy non-active infill at irregular edges. Hatch is a drawing identifier only. No assumed product, panel count or generation capacity. Infill must be a compatible roofing component, not ordinary decorative glass. Waterproofing and flashing design remains unresolved.

Natural ventilation background: https://bsesc.energy.gov/energy-basics/natural-ventilation-and-cooling
''')
print('Saved roof-cap alternatives with both window options, solar infill diagram and combined PDF.')
