from column_location import rail_case
from pathlib import Path
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
p=Path(__file__).parent
r=rail_case(246.5,126.)
(p/'east-column-proposal.json').write_text(json.dumps(r,indent=2))
fig,ax=plt.subplots(figsize=(9,9))
ax.add_patch(Rectangle((0,0),249.5,249,fill=False,edgecolor='#7e898c',linewidth=7))
ax.add_patch(Rectangle((213.25,55.5),30,148,facecolor='#e7d5be',edgecolor='#a89277'))
for y in [56,105,154,203]:ax.plot([213.25,243.25],[y,y],color='#a89277',lw=1)
ax.text(229,128,'EXISTING CABINETS\nNo structural load assigned',rotation=90,ha='center',va='center',fontsize=10)
for y in [-21.25,69.75,185,253]:ax.plot([-32,249.5],[y,y],color='#355e75',lw=3)
ax.plot([-32,-32],[-21.25,253],color='#355e75',lw=3)
ax.plot([246.5,246.5],[-21.25,253],color='#b65b35',lw=4)
for x,y in [(-32,y) for y in [-21.25,69.75,185,253]]+[(148.5,-21.25),(211.5,-21.25),(53.25,253),(224.25,253)]:ax.add_patch(Rectangle((x-2,y-2),4,4,color='#355e75'))
ax.add_patch(Rectangle((244.5,124),4,4,color='#bf392c'));ax.scatter([246.5],[126],s=220,facecolors='none',edgecolors='#bf392c',linewidth=2)
ax.annotate('NEW 4-INCH STEEL COLUMN\nWithin the 6-inch east wall\nBeam centered directly above',xy=(246.5,126),xytext=(290,142),fontsize=11,color='#9a3828',arrowprops=dict(arrowstyle='->',color='#9a3828'),va='center')
ax.annotate('',xy=(280,0),xytext=(280,126),arrowprops=dict(arrowstyle='<->',color='#555'))
ax.text(285,57,'10 ft 6 in\nfrom south\nEXTERIOR face',fontsize=10,va='center')
ax.text(92,127,'Garage interior\nNo new interior column',ha='center',fontsize=12)
ax.text(117,271,'NORTH — GARAGE DOOR',ha='center',fontsize=11)
ax.text(117,-44,'SOUTH',ha='center',fontsize=11)
ax.text(15,191,'Cross beams extend to new east beam line',fontsize=9,color='#355e75')
ax.set(xlim=(-55,435),ylim=(-60,295),aspect='equal');ax.axis('off')
fig.suptitle('Proposed east-wall column location',fontsize=18,y=.92)
fig.text(.07,.12,'Column center: 10 ft from the inside face of the south wall.\nCenter across wall thickness: 3 in from the exterior east face.\nConcept only: new footing and revised beam-end connections required.',fontsize=11,linespacing=1.6)
fig.savefig(p/'east-column-location.png',dpi=150,bbox_inches='tight');plt.close(fig)
print('Proposed column:',r)
