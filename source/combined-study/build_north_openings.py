from pathlib import Path
import json
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
R=Path(__file__).resolve().parent
s={'__file__':str(R/'build_combined.py')}
exec((R/'build_combined.py').read_text().split('fig,axs=plt.subplots')[0],s)
fig,ax=plt.subplots(figsize=(16,10))
s['project'](ax,'north');ax.set_xlim(-25,455);ax.set_ylim(-40,275)
F=s['F'];ink='#34434b';blue='#326e8b'
# North view left = east; garage door opening spans28.25..193.25.
gleft=28.25;gright=193.25;center=gright-165/4
width=32;height=80
ax.add_patch(Rectangle((center-width/2,F),width,height,facecolor='#f8f8f5',edgecolor=ink,lw=1.2,zorder=100))
ax.add_patch(Rectangle((center-12,F+34),24,40,facecolor='#aacdd8',edgecolor=ink,lw=.7,zorder=101))
ax.plot([center+10],[F+32],marker='o',ms=2,color=ink,zorder=102)
for cx in [center-52,center+52]:
 ax.add_patch(Rectangle((cx-14,F+34),28,40,facecolor='white',edgecolor=ink,lw=.8,zorder=100))
 ax.add_patch(Rectangle((cx-12,F+36),24,36,facecolor='#aacdd8',edgecolor=ink,lw=.8,zorder=101))
 ax.plot([cx-12,cx+12],[F+54,F+54],color='white',lw=1,zorder=102)
# Garage opening outlined and divided into four equal quarters as placement reference.
ax.add_patch(Rectangle((gleft,0),165,84,facecolor='none',edgecolor=ink,lw=.8,zorder=99))
for q in range(1,4):
 x=gleft+q*165/4
 ax.plot([x,x],[0,84],ls=(0,(4,4)),lw=.6,color='#8c9ea7',zorder=100)
for i in range(4):ax.text(gleft+(i+.5)*165/4,38,str(4-i),ha='center',fontsize=11,color=blue,zorder=103)
ax.plot([center,center],[0,F+height+9],ls=(0,(5,3)),lw=.8,color=blue,zorder=103)
ax.annotate('Upstairs door center\n¼ of garage-door width from WEST',xy=(center,F+height+3),xytext=(120,255),fontsize=11,ha='center',color=blue,arrowprops=dict(arrowstyle='-',color=blue))
ax.annotate('',(center,-16),(gright,-16),arrowprops=dict(arrowstyle='|-|',color=blue,lw=1))
ax.text((center+gright)/2,-25,'41¼″',fontsize=11,color=blue,ha='center')
ax.text(28,-5,'EAST',fontsize=9,color=blue,va='top');ax.text(220,-5,'WEST',fontsize=9,color=blue,va='top')
fig.suptitle('North elevation · upstairs entry and two windows',fontsize=22,x=.08,ha='left',y=.97)
fig.text(.08,.92,'Looking south · west is on the right · numbered quarters refer to the existing garage-door opening',fontsize=11,color=blue)
fig.text(.08,.065,'Door: 32″ × 80″. Flanking windows: 24″ × 36″, sills 36″ above loft floor. Sizes and spacing are provisional.',fontsize=11,color=ink)
fig.text(.08,.04,'Door threshold at loft floor, 8′ 11¼″ above datum. Exterior landing / access is not yet drawn.',fontsize=11,color=blue)
for ext in ['png','svg','pdf']:fig.savefig(R/f'north-entry-windows.{ext}',dpi=180,facecolor='white')
(R/'north-openings.json').write_text(json.dumps({'units':'inches','status':'north elevation design trial, not yet cut into 3D scene','garage_door_width':165,'door_center_from_garage_door_west_edge':41.25,'door_center_north_elevation_x':center,'door_center_global_x':249.5-center,'door_width_assumed':32,'door_height_assumed':80,'threshold_height':F,'window_width_assumed':24,'window_height_assumed':36,'window_sill_above_floor_assumed':36,'window_centers_offset_from_door_assumed':[-52,52]},indent=2))
print('Saved north-entry-windows PNG, SVG, PDF.')
