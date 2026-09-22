from pathlib import Path
import runpy
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle,Polygon
from matplotlib.backends.backend_pdf import PdfPages
R=Path(__file__).resolve().parent
s=runpy.run_path(str(R/'build_elevations.py'));plt.close(s['fig'])
F=s['F'];H=s['H'];B=s['B'];L=s['L'];YS=s['YS'];z=s['z'];YB=s['YB']
fig,axes=plt.subplots(1,2,figsize=(18,9));fig.subplots_adjust(left=.05,right=.97,top=.82,bottom=.2,wspace=.16)
ink='#34434b';blue='#326e8b'
def line(ax,pts,**kw):ax.plot(*zip(*pts),color=kw.pop('color',ink),lw=kw.pop('lw',1),**kw)
def rect(ax,x,y,w,h,c='white'):ax.add_patch(Rectangle((x,y),w,h,facecolor=c,edgecolor=ink,lw=1))
def window(ax,x,y,w,h):
 rect(ax,x-2,y-2,w+4,h+4);rect(ax,x,y,w,h,'#b7d5df');line(ax,[(x+w/2,y),(x+w/2,y+h)],lw=.6)
for ax,title in zip(axes,['A · One window south of the balcony','B · Three small windows following the slope']):
 ax.set_title(title,loc='left',fontsize=15,pad=20);ax.set_aspect('equal');ax.set_xlim(-12,294);ax.set_ylim(-25,253);ax.axis('off')
 rect(ax,6,0,249,H,'#dce2e5')
 ax.add_patch(Polygon([(0,B),(L,B),(L,z(0)-8),(78,z(YB)-8),(0,z(L)-8)],facecolor='#dce2e5',edgecolor=ink))
 for yy in range(114,220,6):
  end=min(L,L-(yy-B)/s['m']-YS)
  if yy>z(YB)-8:end=78-(yy-(z(YB)-8))*48
  if end>0:line(ax,[(0,yy),(end,yy)],lw=.3,color='#abbac1')
 prof=[(0,z(L)),(78,z(YB)),(L-YS,z(YS))]
 ax.add_patch(Polygon(prof+[(x,y-8) for x,y in reversed(prof)],facecolor='white',edgecolor=ink))
 line(ax,prof[1:],lw=3,color='#344c5b')
 for yy,w in [(73,28.5),(153.25,28.75)]:rect(ax,L-yy-w,48,w,24)
 rect(ax,9,F,60,80)
 for x in [12,42]:
  rect(ax,x,F+22,24,54,'#e7f1f4')
  for yy in [F+40,F+58]:line(ax,[(x,yy),(x+24,yy)],lw=.6)
 for x in [2,89,178,275]:rect(ax,x-3,0,6,H)
 rect(ax,0,H,L-YS,8)
 for x in range(82,279,7):rect(ax,x,B-2,1.5,2)
 for x in range(0,79,6):line(ax,[(x,F),(x,F+42)],lw=.65)
 rect(ax,0,F+40,78,2);rect(ax,0,F+6,78,2)
 line(ax,[(-5,F),(284,F)],ls=(0,(5,3)),lw=.6,color=blue)
 ax.text(0,-15,'NORTH',fontsize=9);ax.text(278,-15,'SOUTH',fontsize=9,ha='right')
 ax.text(180,200,'30° integrated solar roof',rotation=-30,fontsize=9,ha='center')
# Geometry-checked candidate openings, inches. x increases south in this elevation.
options=[[(94,F+30,30,36)],[(94,F+57,18,18),(136,F+33,18,18),(178,F+9,18,18)]]
for ax,windows in zip(axes,options):
 for x,y,w,h in windows:
  assert y>=F
  assert y+h+2 < z(L-(x+w+2))-8, 'Window trim must fit below roof underside'
  window(ax,x,y,w,h)
fig.suptitle('West loft wall · window alternatives',x=.05,ha='left',fontsize=23,y=.96)
fig.text(.05,.90,'White balcony / walkway and flat-cap roof retained · Looking east: north left, south right',fontsize=12,color=blue)
fig.text(.05,.14,'A: 30″ × 36″ opening; sill 30″ above loft floor.\nA single window keeps the wall simple and relates to the French doors.',fontsize=11,color=ink)
fig.text(.54,.14,'B: three 18″ × 18″ openings; sills 57″, 33″ and 9″ above loft floor.\nThe stepped arrangement fits the descending roof; the last window is low.',fontsize=11,color=ink)
fig.text(.05,.055,'All new window sizes and positions are design trials. Openings fit the drawn roof profile; framing, glazing and operability are not specified.',fontsize=10,color=blue)
for ext in ['png','svg','pdf']:fig.savefig(R/f'west-window-options.{ext}',dpi=180,facecolor='white')
print('Saved west-window-options PNG, SVG, PDF')
