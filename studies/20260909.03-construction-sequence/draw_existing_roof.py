from pathlib import Path
import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from matplotlib.patches import Polygon, Rectangle

OUT=Path(__file__).resolve().parent
p=json.loads((OUT/'existing-roof-parameters.json').read_text())
W,L,H,R=[p[k] for k in ['width','length','wall_height','roof_rise']]
P=H+R
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':11})
fig=plt.figure(figsize=(12,10))
fig.suptitle('Existing garage · corrected pyramid roof',x=.07,ha='left',fontsize=20)
fig.text(.07,.925,'Walls 8 ft 2½ in  +  roof rise 4 ft 10 in  =  peak 13 ft ½ in above slab',fontsize=13)
ax=fig.add_subplot(221)
corners=[(0,0),(W,0),(W,L),(0,L)]
colors=['#b5c8ce','#95b0bb','#d0dce0','#a7bec7']
for i in range(4):ax.add_patch(Polygon([corners[i],corners[(i+1)%4],(W/2,L/2)],facecolor=colors[i],edgecolor='#425c68',lw=1.5))
ax.plot(W/2,L/2,'o',color='#263f4b');ax.text(W/2,L/2+17,'Central peak',ha='center')
ax.annotate('',xy=(W+20,L),xytext=(W+20,0),arrowprops={'arrowstyle':'<->'})
ax.text(W+30,L/2,'23 ft 10¼ in*',rotation=90,va='center')
ax.annotate('',xy=(0,-20),xytext=(W,-20),arrowprops={'arrowstyle':'<->'})
ax.text(W/2,-42,'20 ft 9½ in',ha='center')
ax.text(W/2,L+15,'NORTH',ha='center',fontsize=10)
ax.set(xlim=(-20,W+65),ylim=(-60,L+40),aspect='equal');ax.axis('off');ax.set_title('Roof plan · four triangular faces',loc='left')
ax=fig.add_subplot(222,projection='3d')
base=[(x,y,0) for x,y in corners];eave=[(x,y,H) for x,y in corners];peak=(W/2,L/2,P)
walls=[[base[i],base[(i+1)%4],eave[(i+1)%4],eave[i]] for i in range(4)]
roof=[[eave[i],eave[(i+1)%4],peak] for i in range(4)]
ax.add_collection3d(Poly3DCollection(walls,facecolors='#e4e5e0',edgecolors='#657179',linewidths=1))
ax.add_collection3d(Poly3DCollection(roof,facecolors=colors,edgecolors='#425c68',linewidths=1.3))
ax.set(xlim=(0,W),ylim=(0,L),zlim=(0,P));ax.set_box_aspect((W,L,P));ax.view_init(elev=25,azim=-57);ax.set_axis_off();ax.set_title('Three-dimensional shape · no ridge segment',loc='left')
for pos,span,label,dim in [(223,W,'South elevation','20 ft 9½ in'),(224,L,'West elevation','23 ft 10¼ in*')]:
 ax=fig.add_subplot(pos)
 ax.add_patch(Rectangle((0,0),span,H,facecolor='#e4e5e0',edgecolor='#657179'))
 ax.add_patch(Polygon([(0,H),(span/2,P),(span,H)],facecolor='#b5c8ce',edgecolor='#425c68',lw=1.5))
 ax.axhline(0,color='#657179',lw=1)
 ax.annotate('',xy=(-15,0),xytext=(-15,H),arrowprops={'arrowstyle':'<->'})
 ax.text(-21,H/2,'8 ft 2½ in',rotation=90,va='center',ha='right')
 ax.annotate('',xy=(span+15,H),xytext=(span+15,P),arrowprops={'arrowstyle':'<->'})
 ax.text(span+24,(H+P)/2,'4 ft 10 in',rotation=90,va='center')
 ax.text(span/2,-20,dim,ha='center');ax.text(span/2,P+12,'Peak 13 ft ½ in',ha='center')
 ax.set(xlim=(-45,span+50),ylim=(-35,P+35),aspect='equal');ax.axis('off');ax.set_title(label,loc='left')
fig.text(.07,.065,'* Long footprint dimension provisional: adopted from the original plan label for this requested redraw.',fontsize=10)
fig.text(.07,.043,'Roof starts at wall tops; eaves are not yet measured. Openings omitted to make the roof geometry clear.',fontsize=10)
fig.tight_layout(rect=(.03,.10,.98,.9),h_pad=2,w_pad=3)
for ext in ['png','pdf','svg']:fig.savefig(OUT/f'existing-garage-corrected.{ext}',dpi=160)
assert P==156.5 and p['ridge_length']==0
print('Four triangular roof faces; peak (in):',W/2,L/2,P)
