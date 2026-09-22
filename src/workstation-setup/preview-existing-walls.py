import os,sys,json,pathlib
os.environ['MPLCONFIGDIR']='/private/tmp/garage-wall-preview-mpl'
sys.path.insert(0,'/Applications/FreeCAD.app/Contents/Resources/lib')
import FreeCAD,Part
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
P=pathlib.Path(sys.argv[1]); shape=Part.read(str(P/'Existing-Garage.step'))
fig=plt.figure(figsize=(12,9),layout='constrained'); ax=fig.add_subplot(111,projection='3d')
for solid in shape.Solids:
 for face in solid.Faces:
  vs,ts=face.tessellate(5)
  polys=[[(vs[i].x/25.4,vs[i].y/25.4,vs[i].z/25.4) for i in t] for t in ts]
  n=face.normalAt(0,0)
  shade=.69+.2*abs(n.z)+.04*n.x
  ax.add_collection3d(Poly3DCollection(polys,facecolors=[(shade,shade+.015,min(1,shade+.02))],edgecolors='none'))
  for edge in face.Edges:
   pts=edge.discretize(12)
   ax.plot([p.x/25.4 for p in pts],[p.y/25.4 for p in pts],[p.z/25.4 for p in pts],color='#63777e',lw=.35)
ax.set(xlim=(-15,264),ylim=(-15,264),zlim=(0,112),xlabel='East (in)',ylabel='North (in)',zlabel='Height (in)')
ax.set_box_aspect((249.5,249,112));ax.view_init(elev=35,azim=-135)
ax.set_title('Existing garage • walls and openings only',fontsize=18,pad=20)
fig.supxlabel('CAD geometry preview • 6-in wall cores + ½-in exterior stucco • wall height 8 ft 2½ in\nSouth door 80 in • north garage door 86 in • windows: 48-in sill, 24-in height • no roof',fontsize=11)
fig.savefig(P/'Existing-Garage-preview.png',dpi=160)
print('Preview rendered from exported CAD solids:',len(shape.Solids))
