import os,sys,pathlib
os.environ['MPLCONFIGDIR']='/private/tmp/garage-wall-preview-mpl'
sys.path.insert(0,'/Applications/FreeCAD.app/Contents/Resources/lib')
import FreeCAD as A,Part
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
P=pathlib.Path(sys.argv[1]);s=Part.read(str(P/'Existing-Garage-roof.step'));U=25.4
fig,ax=plt.subplots(figsize=(10,7),layout='constrained')
for solid in s.Solids:
 color='#bd925a' if solid.BoundBox.ZMax>102*U else '#d9dedf'
 for wire in solid.slice(A.Vector(0,1,0),16*U):
  pts=wire.discretize(Deflection=0.01)
  ax.add_patch(Polygon([(p.x/U,p.z/U) for p in pts],closed=True,facecolor=color,edgecolor='#46565b',lw=1.3))
ax.axhline(98.5,c='#27867b',ls='--',lw=1)
ax.annotate('Rafter underside trimmed\nto top of soffit',(-2,98.5),xytext=(-5.5,108),arrowprops={'arrowstyle':'->','color':'#27867b'},color='#227467')
ax.annotate('Soffit',(-2,98),xytext=(-2,94.5),arrowprops={'arrowstyle':'->'},ha='center')
ax.annotate('Fascia',(-4.4,100),xytext=(-7,103),arrowprops={'arrowstyle':'->'})
ax.text(6,95,'Existing wall',ha='center')
ax.set(xlim=(-8,16),ylim=(93,113),xlabel='East from west wall core face (in)',ylabel='Height above floor (in)',title='West eave section • through first rafter, 16 in from south corner')
ax.set_aspect('equal');ax.spines[['top','right']].set_visible(False)
fig.supxlabel('Section cut from revised CAD solids. Tail-to-soffit correction only; other bearing/joinery details remain schematic.',fontsize=10)
fig.savefig(P/'Existing-Garage-eave-correction.png',dpi=160)
print('Rendered eave section')
