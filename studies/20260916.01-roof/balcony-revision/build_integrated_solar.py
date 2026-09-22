from pathlib import Path
import runpy, json
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
from matplotlib.backends.backend_pdf import PdfPages
R=Path(__file__).resolve().parent
s=runpy.run_path(str(R/'build_elevations.py'))
fig=s['fig'];a=s['a'];b=s['b'];z=s['z'];W=s['W'];YS=s['YS'];YB=s['YB'];L=s['L'];line=s['line'];label=s['label']
z0=z(YS);zb=z(YB);k=(z(L)-z0)/36;xb=W-(zb-z0)/k
# One integrated finish follows the existing roof surface, with no standoff.
pv=Polygon([(0,z0),(W,z0),(xb,zb),(0,zb)],facecolor='#344c5b',edgecolor='#243741',lw=1.2,zorder=4)
b.add_patch(pv)
for x in range(0,int(W),30):
 art=b.plot([x,x],[z0,zb],color='#9babb3',lw=.55,zorder=5)[0];art.set_clip_path(pv)
for h in range(int(z0)+18,int(zb),18):
 art=b.plot([0,W],[h,h],color='#9babb3',lw=.55,zorder=5)[0];art.set_clip_path(pv)
label(b,95,170,'Integrated PV roof finish',color='white',fontsize=10,zorder=6,ha='center',bbox=dict(facecolor='#344c5b',edgecolor='none',pad=4))
line(a,[(78,zb),(L-YS,z0)],color='#344c5b',lw=3)
fig.suptitle('Flat-cap garage · integrated photovoltaic roof',x=.06,ha='left',fontsize=22,y=.97)
fig.text(.06,.025,'PV joints are illustrative, not a module layout. Existing 8 in roof envelope retained provisionally; final assembly thickness is TBD.',fontsize=10,color='#326e8b')
for ext in ['png','svg']:fig.savefig(R/f'integrated-solar-elevations.{ext}',dpi=180,facecolor='white')
f,ax=plt.subplots(figsize=(13,8));ax.set_xlim(0,130);ax.set_ylim(0,80);ax.axis('off')
f.suptitle('Integrated solar roof · assembly intent',x=.08,ha='left',fontsize=22)
ax.text(3,73,'CONCEPT SECTION · exploded for clarity · not to scale',fontsize=11,color='#326e8b')
# Inclined separated layers; deliberately undimensioned pending system selection.
layers=[(47,3,'#344c5b','Visible photovoltaic roofing surface'),(38,3,'#e1e7e9','Concealed fixing / drainage zone'),(31,1,'#397e95','Continuous concealed waterproof layer'),(23,4,'#b8c1c5','Supporting roof deck'),(10,9,'#e7e3da','Structure + insulation / interior assembly')]
for y,t,col,name in layers:
 ax.add_patch(Polygon([(5,y),(57,y+14),(57,y+14+t),(5,y+t)],facecolor=col,edgecolor='#34434b',lw=1))
 ax.plot([45,68],[y+12,y+12],color='#67747a',lw=.8)
 ax.text(70,y+12,name,fontsize=11,va='center')
ax.text(5,5,'30° roof pitch; no raised rack profile. Layer depths and ventilation depend on the selected system.',fontsize=10)
f.text(.08,.08,'Design intent: spend on waterproofing and durability, not the appearance of hidden layers.\nPV joints, edge flashings and the transition to the shallow rear cap must form a coordinated roofing system.',fontsize=11)
for ext in ['png','svg']:f.savefig(R/f'integrated-solar-section.{ext}',dpi=180,facecolor='white')
with PdfPages(R/'integrated-solar-review.pdf') as pdf:pdf.savefig(fig);pdf.savefig(f)
(R/'integrated-solar-notes.md').write_text('''# Integrated photovoltaic roof revision

South-facing 30-degree surface is the visible PV finish, without a raised rack. Rear shallow cap and west white balcony geometry remain as previously drawn. Module joints are illustrative only. No manufacturer or module count selected.

The existing 8-inch vertical roof envelope is retained as a drawing placeholder, not a validated assembly depth. Actual depth and any effect on overall height or loft clearance must be resolved with system selection. The exploded section is undimensioned.

Concealed waterproofing, drainage/fixing zone, deck and structure are conceptual layers; their arrangement must follow the selected roofing system. Hidden finishes may be economical, but waterproofing is not assumed cheap or optional.

Background: https://www.energy.gov/cmei/systems/articles/expanding-solar-energy-opportunities-rooftops-building-integration
''')
print('Integrated solar elevations, section and two-page PDF saved.')
