import os,json,pathlib
os.environ['MPLCONFIGDIR']='/private/tmp/garage-wall-preview-mpl'
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from matplotlib.patches import Rectangle
p=pathlib.Path('/Volumes/Proj/Buzzkill-Proj/garage')
d=json.loads((p/'visible-mesh-lofts-only.json').read_text())
fig=plt.figure(figsize=(16,9),layout='constrained')
a=fig.add_subplot(121,projection='3d'); b=fig.add_subplot(122)
for o in d['objects']:
 v=[[c/25.4 for c in q] for q in o['vertices']]; t=o['triangles']; name=(o.get('name','')+' '+o.get('label','')).lower()
 col=o.get('color',[.7,.5,.3])[:3]
 poly=[[v[i] for i in tri] for tri in t]
 a.add_collection3d(Poly3DCollection(poly,facecolors=[col],edgecolors='#65594c',linewidths=.15,alpha=.8 if 'deck' in name else 1))
 # Draw plan only deck and horizontal framing, omitting elevated hangers.
 if max(q[2] for q in v)<=105:
  x=[q[0] for q in v];y=[q[1] for q in v]
  b.add_patch(Rectangle((min(x),min(y)),max(x)-min(x),max(y)-min(y),facecolor=col,edgecolor='#65594c',linewidth=.5,alpha=.8))
for x,y,w,h in [(0,0,249.5,6),(0,243,249.5,6),(0,6,6,237),(243.5,6,6,237)]:
 b.add_patch(Rectangle((x,y),w,h,fc='#b8bfc5',ec='#626970'))
 a.plot([x,x+w,x+w,x,x],[y,y,y+h,y+h,y],[98.5]*5,color='#596572',lw=2)
a.set(xlim=(-5,255),ylim=(-5,255),zlim=(85,160),xlabel='East (in)',ylabel='North (in)',zlabel='Height (in)');a.set_box_aspect((250,250,120),zoom=.85);a.view_init(elev=45,azim=-125)
a.set_title('Lofts and supports • roof omitted',fontsize=16)
b.set(xlim=(-27,292),ylim=(-25,275),aspect='equal',xlabel='East (in)',ylabel='North (in)');b.set_title('Top view • north up',fontsize=16)
def dim(x1,y1,x2,y2,s):
 b.annotate('',(x1,y1),(x2,y2),arrowprops=dict(arrowstyle='<->',color='#253a50'));b.text((x1+x2)/2+3,(y1+y2)/2+3,s,fontsize=10,color='#253a50',bbox=dict(fc='white',ec='none',alpha=.85))
dim(-12,6,-12,53,'47″');dim(-12,214,-12,243,'29″');dim(6,115,54,115,'48″ open');dim(195.5,115,243.5,115,'48″ open')
dim(6,15,75,15,'69″ open');dim(196.25,258,221.25,258,'25″');dim(265,6,265,78,'72″');
b.plot([56.25,221.25],[249,249],color='#28608e',lw=4);dim(75,60,171,60,'96″ / 5 rafters');b.text(123,25,'SOUTH LOFT',ha='center',fontsize=11);b.text(124.75,227,'NORTH PLATFORM',ha='center',fontsize=11)
fig.suptitle('Existing garage • three storage lofts',fontsize=22)
fig.supxlabel('Joist bottom 98½″  •  joist top 104″  •  decking top 104¾″\nApproximate reconstruction: later middle-joist spacing and hanger locations remain approximate.',fontsize=12)
fig.savefig('/private/tmp/Existing-Garage-lofts-preview.png',dpi=150)
