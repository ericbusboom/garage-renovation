import os,sys,json,pathlib
os.environ['MPLCONFIGDIR']='/private/tmp/garage-wall-preview-mpl'
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
P=pathlib.Path(sys.argv[1]); inp=pathlib.Path(sys.argv[2]); data=json.loads(inp.read_text())
fig=plt.figure(figsize=(12,10),layout='constrained');ax=fig.add_subplot(111,projection='3d')
for obj in data['objects']:
 vs=obj['vertices']; ts=obj['triangles']; color=obj.get('color',[.72,.72,.72])[:3]
 polys=[[(vs[i][0]/25.4,vs[i][1]/25.4,vs[i][2]/25.4) for i in t] for t in ts]
 ax.add_collection3d(Poly3DCollection(polys,facecolors=[color],edgecolors='#726e66',linewidths=.12))
ax.set(xlim=(-10,259.5),ylim=(-10,259),zlim=(0,168),xlabel='East (in)',ylabel='North (in)',zlabel='Height (in)')
ax.set_box_aspect((249.5,249,168));ax.view_init(elev=32,azim=-135)
ax.set_title('Existing garage • open roof framing',fontsize=19,pad=20)
fig.supxlabel('CAD geometry preview • centered 18-in north–south ridge • roof cladding omitted\nReclaimed board framing and eave details are a dimensional reconstruction, not a structural design.',fontsize=11)
fig.savefig(P/'Existing-Garage-roof-framing.png',dpi=160)
print('Rendered',len(data['objects']),'CAD objects')
