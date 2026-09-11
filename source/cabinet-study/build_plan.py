from pathlib import Path
import json,math
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
R=Path(__file__).resolve().parent;W=249.5;L=249
# Explicit trial assumptions, awaiting confirmation.
y0=6+49.5;posts=[y0+.5+49*i for i in range(4)];cf=W-6-.25-30
beamys=[69.75,185];east=211.5
fig,ax=plt.subplots(figsize=(13,13));fig.subplots_adjust(left=.08,right=.90,top=.85,bottom=.15)
ink='#34434b';blue='#326e8b';orange='#b45f2d'
def rect(x,y,w,h,c,**kw):ax.add_patch(Rectangle((x,y),w,h,facecolor=c,edgecolor=ink,lw=.8,**kw))
def txt(x,y,t,**kw):ax.text(x,y,t,fontsize=kw.pop('fontsize',10),color=kw.pop('color',ink),ha=kw.pop('ha','center'),va='center',**kw)
def dimy(a,b,x,origin,t):
 for yy in [a,b]:ax.plot([origin,x],[yy,yy],color=blue,lw=.5)
 ax.annotate('',(x,a),(x,b),arrowprops=dict(arrowstyle='|-|',color=blue));txt(x+4,(a+b)/2,t,rotation=90,color=blue)
def dimx(a,b,y,origin,t):
 for xx in [a,b]:ax.plot([xx,xx],[origin,y],color=blue,lw=.5)
 ax.annotate('',(a,y),(b,y),arrowprops=dict(arrowstyle='|-|',color=blue));txt((a+b)/2,y-5,t,color=blue)
# Exterior shell with actual openings from measured model.
ops=json.loads((R.parent/'model/scene.json').read_text())['parameters']['openings']
rect(0,0,W,6,'#cfd5d7');rect(W-6,0,6,L,'#cfd5d7');rect(0,0,7.5,L,'#cfd5d7');rect(0,L-8,W,8,'#cfd5d7')
for o in ops:
 if o['side'] in ['south','north']:
  x=W-o['offset']-o['width'];yy=0 if o['side']=='south' else L-8
  rect(x,yy,o['width'],6 if o['side']=='south' else 8,'white')
 else:
  rect(0,o['offset'],7.5,o['width'],'white')
# Cabinet footprint and three 48-in double-door bays.
rect(cf,y0,30,148,'#eee0bf');ax.plot([W-6-.25]*2,[y0,y0+148],color='#b9994d',lw=2)
for j,py in enumerate(posts):
 rect(cf,py-.5,30,1,'#4d6570');txt(cf+15,py+5,f'P{j+1}',fontsize=8)
for j in range(3):
 ya=y0+1+j*49
 ax.plot([cf,cf],[ya,ya+48],color='#d49126',lw=3)
 ax.plot([cf-2,cf+2],[ya+24,ya+24],color='#d49126',lw=1)
 txt(cf+16,ya+24,f'48″ pair\n2 doors',fontsize=8)
# Beam lines from original Canvas: exact internal centerlines; adopted west offset.
for yy in beamys:
 rect(0,yy-2,209.5,4,'#bd956a')
 ax.plot([-32,0],[yy,yy],color=orange,lw=3)
 txt(103,yy+8,f'Cross-beam at y={yy:g}″',fontsize=9,color=orange)
rect(east-2,-19.25,4,270.25,'#bd956a')
for yy in [-21.25,253]:
 ax.plot([-32,east],[yy,yy],color='#bd956a',lw=4)
for yy in [-21.25,69.75,185,253]:rect(-35,yy-3,6,6,'#866141')
ax.plot([-32,-32],[-21.25,253],color='#bd956a',lw=3)
for yy in beamys:
 ax.plot([east,cf],[yy,yy],color='#b52f34',lw=2)
 ax.scatter([cf],[yy],s=65,facecolors='none',edgecolors='#b52f34',zorder=8)
# key comparisons and dimension strings
for i in range(3):dimy(posts[i]+.5,posts[i+1]-.5,272,cf+30,'48″')
dimy(y0,y0+148,289,cf+30,'148″ cabinet run*')
dimy(6,y0,272,cf+30,'49½″ from inside face*')
dimx(cf,cf+30,220,y0+148,'30″ cabinet depth')
dimx(-32,0,-40,0,'32″');dimx(0,W,-58,0,'249½″ overall E–W')
txt(85,280,'NORTH ↑  /  GARAGE DOOR',fontsize=12)
txt(93,127,'Roof removed\nBeam lines shown above cabinet plan',fontsize=12)
ax.annotate('East beam CL x=211½″\nCabinet front x=213¼″*\n1¾″ transverse mismatch',xy=(cf,185),xytext=(90,226),fontsize=9,color='#b52f34',arrowprops=dict(arrowstyle='-',color='#b52f34'))
ax.set_xlim(-65,320);ax.set_ylim(-70,290);ax.set_aspect('equal');ax.axis('off')
fig.suptitle('Roof-off plan · beams and cabinet support study',x=.07,ha='left',fontsize=22,y=.965)
fig.text(.07,.915,'TRIAL LOCATION: EAST WALL · six leaves in three 48″ pairs · north up, west left',fontsize=12,color=blue)
fig.text(.07,.09,'* Assumed: 49½″ begins at inside south-wall face; cabinet run on east wall. Confirm these before using the intersections.',fontsize=10,color=blue)
fig.text(.07,.067,'Solid brown/orange: specified structural beams. All specified columns are structural supports on reported concrete pilings.',fontsize=10,color=ink)
fig.text(.07,.044,'Pilings reported approximately 18″ diameter × 36″ deep. Cabinet-frame foundation details remain separate / unconfirmed.',fontsize=10,color=ink)
for ext in ['png','svg','pdf']:fig.savefig(R/f'roof-off-cabinet-plan.{ext}',dpi=180,facecolor='white')
# Demand-only calculation, normalized per100 plf; no inferred member capacity.
span=(east+32)/12
calc={'assumptions':{'cabinet_wall':'east UNCONFIRMED','south_offset_from':'inside face UNCONFIRMED','paired_door_opening':48,'cabinet_run':148,'post_centers_from_south_outside':posts,'cabinet_front_x':cf,'east_beam_CL_x':east,'tube_wall':None,'foundation_capacity':None},'simple_span_crossbeam':{'span_ft':span,'per_100_plf':{'each_end_reaction_lb':100*span/2,'max_moment_lb_ft':100*span**2/8},'description':'Simply supported uniform load only; excludes cantilevers, continuity, point loads and load combinations'},'transfer_locations':[]}
for yy in beamys:
 lo=max(v for v in posts if v<=yy);hi=min(v for v in posts if v>=yy);a=yy-lo;b=hi-yy
 calc['transfer_locations'].append({'beam_y':yy,'post_south_y':lo,'post_north_y':hi,'a_in':a,'b_in':b,'south_post_fraction_of_point_load':b/(a+b),'north_post_fraction_of_point_load':a/(a+b),'header_max_moment_per_lb_in':a*b/(a+b)})
(R/'demand-study.json').write_text(json.dumps(calc,indent=2))
print(json.dumps(calc,indent=2))
