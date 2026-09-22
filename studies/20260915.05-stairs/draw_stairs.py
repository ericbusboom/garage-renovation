from pathlib import Path
import math, json
P=Path(__file__).resolve().parent
S=2.55
L=108/math.sin(math.radians(50)); run=108/math.tan(math.radians(50))
parts=['<svg xmlns="http://www.w3.org/2000/svg" width="1500" height="1500" viewBox="0 0 1500 1500"><rect width="1500" height="1500" fill="#faf9f5"/>']
def line(x,y,x2,y2,c='#50606a',w=2,d=''):
 parts.append(f'<line x1="{x}" y1="{y}" x2="{x2}" y2="{y2}" stroke="{c}" stroke-width="{w}" '+(f'stroke-dasharray="{d}"' if d else '')+'/>')
def text(x,y,t,size=17,c='#263a46'):
 parts.append(f'<text x="{x}" y="{y}" font-family="Arial, sans-serif" font-size="{size}" fill="{c}">{t}</text>')
def poly(pts,c,w=2,fill='none',dash=''):
 parts.append('<polyline points="'+' '.join(f'{x},{y}' for x,y in pts)+f'" fill="{fill}" stroke="{c}" stroke-width="{w}" stroke-dasharray="{dash}"/>')
def circle(x,y,r,c): parts.append(f'<circle cx="{x}" cy="{y}" r="{r}" fill="{c}"/>')
def panel(base,up):
 X=lambda y:150+(269-y)*S
 Z=lambda z:base-z*S
 text(70,base-455,'01  /  STAIR RAISED' if up else '02  /  STAIR LOWERED',24)
 # existing projected roof and wall
 poly([(X(249),Z(0)),(X(249),Z(98.5)),(X(133.5),Z(158.5)),(X(115.5),Z(158.5)),(X(0),Z(98.5)),(X(0),Z(0))],'#d4d6d4',2,'#eeefeb','6 5')
 text(X(235),Z(145),'Existing roof behind stair',15,'#929a99')
 text(X(235),Z(137),'Projected outline only',14,'#929a99')
 line(90,base,1110,base,'#687675',2)
 # elevated loft and posts (schematic)
 line(X(269),Z(126),X(69.75),Z(126),'#406b7c',7)
 text(100,base-375,'Loft +10′ 6″ assumed',17,'#406b7c')
 for name,y in [('W4',269),('W3',185),('W2',69.75),('W1',-66)]:
  line(X(y),base,X(y),Z(126),'#8ca0a7',6)
  text(X(y)-15,base+25,name,17)
  line(X(y),base+32,X(y),base+54,'#a9b0b0',1)
 # loft opening / fixed stair
 line(X(185),Z(126),X(149),Z(126),'#faf9f5',9)
 poly([(X(185),Z(126)),(X(185),Z(117)),(X(176),Z(117)),(X(176),Z(108)),(X(167),Z(108)),(X(149),Z(108))],'#b17a36',5)
 # moving flight transformation from pivot
 def pt(a,b):
  # local down-stair axis a; b perpendicular above axis
  angle=0 if up else math.radians(50)
  return X(149)+S*(a*math.cos(angle)+b*math.sin(angle)), Z(108)+S*(a*math.sin(angle)-b*math.cos(angle))
 poly([pt(0,-3),pt(L,-3)],'#c35b3c',7)
 # tread schematic rotated with rigid body, horizontal when deployed
 for i in range(12):
  a=(i+.5)*L/12
  dx=7*math.cos(math.radians(50)); db=7*math.sin(math.radians(50))
  poly([pt(a-dx/2,-db/2),pt(a+dx/2,db/2)],'#c35b3c',3)
 # rail shown only lowered, schematic
 if not up:
  poly([pt(0,20),pt(L,20)],'#c35b3c',2)
  for a in [0,L/3,2*L/3,L]: poly([pt(a,0),pt(a,20)],'#c35b3c',2)
 circle(*pt(0,0),7,'#b17a36')
 # dimensions
 yy=base+49
 line(X(185),yy,X(69.75),yy,'#50606a',1)
 for y in [185,69.75]: line(X(y)-4,yy+4,X(y)+4,yy-4,'#50606a',1)
 text(X(185)+24,yy+24,'W3–W2  9′ 7¼″',16)
 # pivot leader
 px,py=pt(0,0)
 poly([(px,py),(px+28,py-38),(px+190,py-38)],'#b17a36',1)
 text(px+34,py-45,'Pivot +9′ 0″',17,'#9c672a')
 if up:
  tx,ty=pt(L,0)
  poly([(tx,ty),(tx+30,ty-45),(tx+220,ty-45)],'#c35b3c',1)
  text(tx+35,ty-70,'Stored flight ≈11′ 9″',17,'#a7472e')
  text(tx+35,ty-48,'Ends ≈5′ 2″ past W2',16,'#a7472e')
  # beam circle
  parts.append(f'<circle cx="{X(69.75)}" cy="{Z(113)}" r="25" fill="none" stroke="#b17a36" stroke-width="2" stroke-dasharray="4 4"/>')
  text(1130,base-290,'CHECK AT W2',17,'#9c672a')
  text(1130,base-265,'Beam depth, stair',16)
  text(1130,base-244,'thickness and folded',16)
  text(1130,base-223,'rail clearance.',16)
  text(1130,base-180,'Rails omitted here;',16)
  text(1130,base-159,'folding detail needed.',16)
  text(510,base-120,'Walkway beneath stored stair',17,'#75817e')
 else:
  text(820,base-135,'50° study angle',19,'#a7472e')
  text(820,base-108,'Foot ≈11⅜″ past W2',16,'#a7472e')
  text(1130,base-290,'FIXED TOP ASSEMBLY',17,'#9c672a')
  text(1130,base-265,'Two 9″ drops;',16)
  text(1130,base-244,'two 9″ goings +',16)
  text(1130,base-223,'18″ pivot platform.',16)
  text(1130,base-190,'Pivot is 36″ south',16)
  text(1130,base-169,'of the W3 line.',16)
  line(*pt(L,0),pt(L,0)[0]+90,base,'#b17a36',5)
  text(820,base+24,'Landing extent to design',15,'#9c672a')
text(70,65,'STORAGE LOFT / LIFTING STAIR',34)
text(70,101,'West-side elevation · looking east · NORTH ←                         → SOUTH',19)
text(70,134,'ST-01 · Draft concept · 15 Sep 2026 · Dimensioned study, not a construction drawing',15,'#75817e')
panel(640,True)
panel(1225,False)
line(70,745,1430,745,'#d5d9d7',1)
text(70,1340,'ASSUMPTIONS &amp; LIMITS',18)
text(70,1371,'Loft +126″; pivot +108″; level outside landing at 0″. Heights and 50° pitch are illustrative, not adopted or code-approved.',16)
text(70,1397,'Plan post locations retained. Fixed assembly, rails, pivot support, beam depths and counterbalance require design.',16)
text(70,1423,'Retained roof is shown behind the stair in projection; this does not establish beam-to-roof clearance. Upper roof omitted.',16)
text(70,1449,'Sources: ARCH-006 rev 4 basis.json (plan); model/parameters.json (existing roof). No controlled report drawings changed.',15,'#75817e')
parts.append('</svg>')
(P/'west-elevation-stairs.svg').write_text('\n'.join(parts))
print({'moving_length':L,'deployed_run':run,'stored_past_W2':L-79.25,'down_past_W2':run-79.25})
