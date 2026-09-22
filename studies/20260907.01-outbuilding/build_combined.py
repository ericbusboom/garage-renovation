from pathlib import Path
import runpy
from matplotlib.patches import Rectangle
R=Path(__file__).resolve().parent
s=runpy.run_path(str(R.parent/'roof-studies/balcony-revision/build_window_options.py'))
fig=s['fig'];axes=s['axes']
for ax in axes:
 # North garage wall at x=6; bench extends south 75 in to x=81.
 # Outbuilding is closer to west observer and obscures garage ground-floor geometry.
 ax.add_patch(Rectangle((6,0),75,96,facecolor='#e9ddca',edgecolor='#657a83',lw=1,zorder=15))
 for y in range(8,96,8):ax.plot([6,81],[y,y],color='#bdab91',lw=.4,zorder=16)
 for x in [6,33,78.5]:ax.add_patch(Rectangle((x,0),2.5,96,facecolor='#788a93',edgecolor='#657a83',lw=.6,zorder=17))
 ax.plot([-4,91],[98,98],color='#4d7271',lw=3,zorder=18)
 ax.annotate('Existing outbuilding roof',xy=(47,98),xytext=(109,78),fontsize=8,color='#4d7271',arrowprops=dict(arrowstyle='-',color='#4d7271'),zorder=20)
for t in list(fig.texts):t.remove()
fig.text(.05,.96,'Garage + existing outbuilding · west elevation comparison',ha='left',fontsize=22)
fig.text(.05,.90,'Both window options retained · outbuilding shown in front of garage · north left / south right',fontsize=12,color='#326e8b')
fig.text(.05,.14,'Existing outbuilding: tan infill, gray steel and green roof line.\nProposed garage walkway / balcony: white framing at loft-floor level.',fontsize=11,color='#34434b')
fig.text(.54,.14,'Outbuilding heights and grade remain approximate, as accepted.\nApparent roof-to-balcony separation is not a verified clearance.',fontsize=11,color='#34434b')
fig.text(.05,.055,'Base shallow-cap profile used for this overlay. Both projecting-cornice and low-hip alternatives remain available. No FreeCAD geometry changed.',fontsize=10,color='#326e8b')
for ext in ['png','svg','pdf']:fig.savefig(R/f'garage-outbuilding-west-options.{ext}',dpi=180,facecolor='white')
(R/'review-status.md').write_text('''# Outbuilding review status
User accepted the standalone dimension check as close enough for the analysis. Ground is not flat; existing approximate vertical geometry is intentionally retained. Beam-end interpretation and unknown heights are not promoted to measured facts.

Combined west elevations show both window options with the existing outbuilding in the foreground. Apparent roof/balcony clearance is not verified. Base shallow roof cap used; decorative cap alternatives remain separate. CAD remains unchanged pending design review.
''')
print('Saved combined west elevation PNG, SVG, PDF.')
