from pathlib import Path
import json, html, math
from PIL import Image, ImageDraw, ImageFont
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor

OUT=Path(__file__).resolve().parent
p=json.loads((OUT.parent/'model/parameters.json').read_text())
W,L=p['width'],p['length']; E=W+12; N=L+82
PW,PH=1500,1100
im=Image.new('RGB',(PW*2,PH*2),'white'); dr=ImageDraw.Draw(im)
pdf=canvas.Canvas(str(OUT/'floor-plan-study.pdf'),pagesize=(PW,PH))
svg=[f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:inkscape="http://www.inkscape.org/namespaces/inkscape" width="{PW}" height="{PH}" viewBox="0 0 {PW} {PH}"><rect width="100%" height="100%" fill="white"/>']
gray='#dedede'; label='#999999'; ink='#333e46'; blue='#32677e'; teal='#397f77'; amber='#b08648'
fontpath='/System/Library/Fonts/Supplemental/Arial.ttf'
def line(x1,y1,x2,y2,c=ink,w=1,dash=False):
    svg.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{c}" stroke-width="{w}"'+(' stroke-dasharray="8 6"' if dash else '')+'/>')
    pdf.setStrokeColor(HexColor(c));pdf.setLineWidth(w);pdf.setDash([8,6] if dash else []);pdf.line(x1,PH-y1,x2,PH-y2)
    if dash:
        dist=math.hypot(x2-x1,y2-y1)
        for k in range(0,int(dist),14):
            a=k/dist;b=min(k+8,dist)/dist
            dr.line([(2*(x1+(x2-x1)*a),2*(y1+(y2-y1)*a)),(2*(x1+(x2-x1)*b),2*(y1+(y2-y1)*b))],fill=c,width=max(1,round(2*w)))
    else: dr.line([(x1*2,y1*2),(x2*2,y2*2)],fill=c,width=max(1,round(2*w)))
def text(x,y,t,size=15,c=ink,anchor='start'):
    svg.append(f'<text x="{x}" y="{y}" fill="{c}" font-family="Arial, sans-serif" font-size="{size}" text-anchor="{anchor}">{html.escape(t)}</text>')
    pdf.setFillColor(HexColor(c));pdf.setFont('Helvetica',size)
    {'start':pdf.drawString,'middle':pdf.drawCentredString,'end':pdf.drawRightString}[anchor](x,PH-y,t)
    dr.text((x*2,y*2),t,fill=c,font=ImageFont.truetype(fontpath,size*2),anchor={'start':'ls','middle':'ms','end':'rs'}[anchor])
def group(name):svg.append(f'<g id="{name}">')
def end():svg.append('</g>')
S=1.65
def xy(x,y):return 205+x*S,805-y*S
def pl(x1,y1,x2,y2,c=ink,w=1,dash=False):line(*xy(x1,y1),*xy(x2,y2),c,w,dash)
def pt(x,y,t,size=14,c=ink,anchor='start'):text(*xy(x,y),t,size,c,anchor)
def rect(x,y,w,h,c=gray):
    for a,b,d,e in [(x,y,x+w,y),(x+w,y,x+w,y+h),(x+w,y+h,x,y+h),(x,y+h,x,y)]:pl(a,b,d,e,c)
def dh(x1,x2,y,t,c=ink):
    pl(x1,y,x2,y,c,.8)
    for x in (x1,x2):pl(x-2,y-3,x+2,y+3,c,.8)
    pt((x1+x2)/2,y+5,t,13,c,'middle')
def dv(x,y1,y2,t,c=ink):
    pl(x,y1,x,y2,c,.8)
    for y in (y1,y2):pl(x-3,y-2,x+3,y+2,c,.8)
    pt(x-5,(y1+y2)/2,t,13,c,'end')

text(60,65,'GARAGE / FLOOR PLAN STUDY',28)
text(60,98,'Combined plan • upper structure, possible extension and optional east-wall framing',16)
text(60,126,'Discussion sketch  |  September 15, 2026',13,label)
text(60,154,'ARCH-006  |  Rev 4  |  2026-09-15  |  Status: draft  |  Units: ft / in  |  Not to scale; use dimensions',12,label)
# Possible ground-floor extension: conceptual path through specified post centers.
extension_path=[(-2,185),(-34,185),(-34,L+20),(W-38-192,L+20),(W-38,L+20),(W-38,L),(0,L),(0,185)]
extension_color='#c67b20'
group('possible-ground-floor-extension-fill')
pts=[xy(x,y) for x,y in extension_path]
svg.append('<polygon points="'+' '.join(f'{x},{y}' for x,y in pts)+'" fill="#fff0cd"/>')
path=pdf.beginPath();path.moveTo(pts[0][0],PH-pts[0][1])
for x,y in pts[1:]:path.lineTo(x,PH-y)
path.close();pdf.setFillColor(HexColor('#fff0cd'));pdf.drawPath(path,fill=1,stroke=0)
dr.polygon([(x*2,y*2) for x,y in pts],fill='#fff0cd')
end()
text(60,183,'ORANGE / POSSIBLE GROUND-FLOOR EXTENSION — option for discussion',13,extension_color)
group('existing-walls-and-openings')
# Horizontal opening offsets in source are measured from EAST, not west.
for side,y,t in [('south',0,p['wall_south']),('north',L-p['wall_north'],p['wall_north'])]:
    ops=sorted([o for o in p['openings'] if o['side']==side],key=lambda o:W-o['offset']-o['width'])
    cursor=0
    for o in ops:
        x=W-o['offset']-o['width'];rect(cursor,y,x-cursor,t);cursor=x+o['width']
        if o['type']=='window':
            pl(x,y+t/2-1,x+o['width'],y+t/2-1,gray);pl(x,y+t/2+1,x+o['width'],y+t/2+1,gray)
            pt(x+o['width']/2,-13,'WINDOW',11,label,'middle')
        elif o['type']=='garage':
            pl(x,y+t/2,x+o['width'],y+t/2,gray)
            pt(x+o['width']/2,L-20,'EXISTING GARAGE DOOR',13,label,'middle')
        else:
            pl(x,0,x,-o['width'],gray)
            # Swing symbolic only; hinge is not established by the source.
            pt(x+o['width']/2,-44,'ENTRY DOOR',11,label,'middle')
    rect(cursor,y,W-cursor,t)
rect(W-p['wall_east'],p['wall_south'],p['wall_east'],L-p['wall_north']-p['wall_south'])
cursor=p['wall_south']
for o in sorted([o for o in p['openings'] if o['side']=='west'],key=lambda o:o['offset']):
    y=o['offset'];rect(0,cursor,p['wall_west'],y-cursor)
    for x in (p['wall_west']/2-1,p['wall_west']/2+1):pl(x,y,x,y+o['width'],gray)
    pt(8,y+o['width']/2,'WINDOW',10,label);cursor=y+o['width']
rect(0,cursor,p['wall_west'],L-p['wall_north']-cursor)
pt(92,29,'EXISTING GARAGE BELOW',14,label,'middle')
end()
group('property-lines')
pl(-65,N,E+65,N,ink,1.8,True);pl(E,-40,E,N+28,ink,1.8,True)
pt(100,N+24,'NORTH / ALLEY',18,ink,'middle')
pt(-60,N+5,'PROPERTY LINE',12)
pt(E+9,26,'EAST',14);pt(E+9,14,'NEIGHBOR',12)
end()
# South support row corrected by user: column and beam centers 64 in south of wall.
SOUTH_CL=-64
# Retain earlier 8-in beam width provisionally: outer face 4 in beyond centerline.
XW,YS,XE,YN=-36,SOUTH_CL-4,E-48,N-60
reg=json.loads((OUT.parent/'structural-study/framing-member-register.json').read_text())
columns=[]
for source in reg['posts']:
    col=dict(source)
    col['source_x']=col['x'];col['source_y']=col['y']
    # 4-in concept column symbol matches the earlier rendered model.
    if col['x']==224.25:col['x']=XE-2
    if col['id'] in ('W1','S1','S2'):col['y']=SOUTH_CL
    if col['id'] in ('W4','N1','N2'):col['y']=YN-2
    if col['id']=='N1':col['x']=XE-2-192
    if col['id'] in ('W1','W2','W3','W4'):col['x']=XW+2
    if col['id'] in ('W1','S1','S2'):col['y']=YS+2
    if col['id']=='S3':
        col['status']='proposed'
        col['y']=-2  # Align center with E-S envelope y=-4..0.
    columns.append(col)
# Added west-wall posts: east faces touch existing wall at X=0.
columns.extend([{'id':'WB3','x':-2,'y':185,'status':'proposed','basis':'Aligned with W3; outside west wall'}])
group('complete-upper-structure-outline')
for a,b,c,d in [(XW,YS,XE,YS),(XE,YS,XE,YN),(XE,YN,XW,YN),(XW,YN,XW,YS)]:pl(a,b,c,d,blue,2.5)
# North column outside faces meet the 5-ft limit.
pt(15,SOUTH_CL+13,'T-SO / SUPPORTED SOUTH ROOF EDGE',11,blue)
pl(XW,SOUTH_CL+4,XE,SOUTH_CL+4,blue,.8)
pl(XW,SOUTH_CL,XE,SOUTH_CL,blue,.7,True)
end()
group('roof-overhang-outline')
pl(XW,N-33,XE,N-33,blue,1.6,True)
pl(XW,YN,XW,N-33,blue,1.6,True);pl(XE,YN,XE,N-33,blue,1.6,True)
pt(0,N-33+8,'ROOF EDGE • NORTH OVERHANG',12,blue)
end()
group('loft-floor-and-framing')
# User revision: full width, W2 support line to the north border.
LOFT_SOUTH=69.75
for a,b,c,d in [(XW,LOFT_SOUTH,XE,LOFT_SOUTH),(XE,LOFT_SOUTH,XE,YN),(XE,YN,XW,YN),(XW,YN,XW,LOFT_SOUTH)]:
    # Teal dashes overlay the common blue boundary; no geometric inset.
    pl(a,b,c,d,teal,2.6,True)
for yy,name in [(69.75,'T1 / W2 support line'),(185,'B2 / W3 support line'),(249,'B3 reference')]:
    pl(XW if yy!=249 else 0,yy,XE-2,yy,'#aec6c0',.8)
    pt(12,yy-10,name,11,teal)
pt(90,146,'FULL-WIDTH LOFT',18,teal,'middle')
pt(90,132,'west outer edge to east limit',12,teal,'middle')
pt(90,117,'W2 support line to north border',11,teal,'middle')
pt(105,53,'OPEN BELOW',12,teal,'middle')
end()
group('possible-ground-floor-extension-path')
for i in range(len(extension_path)):
    a,b=extension_path[i],extension_path[(i+1)%len(extension_path)]
    pl(*a,*b,extension_color,2.4,i>=5)
end()
group('proposed-columns')
for col in columns:
    x,y=col['x'],col['y'];optional=col['status']=='optional'
    c=label if optional else ink
    rect(x-2,y-2,4,4,c)
    if not optional:
        pl(x-2,y-2,x+2,y+2,c,1.7);pl(x-2,y+2,x+2,y-2,c,1.7)
    n=col['id']+(' opt.' if optional else '')
    if n in ('WB3','WBN'):pt(x+10,y+7,n,12,c)
    elif n.startswith('W'):pt(x-9,y-3,n,12,c,'end')
    elif n.startswith('N'):pt(x-6,y-13,n,12,c,'end')
    elif n in ('S2','S3'):pt(x-7,y-11,n,12,c,'end')
    elif optional:pt(x-8,y+5,n,10,c,'end')
    else:pt(x,y-13,n,12,c,'middle')
end()
group('new-north-door-bay')
dh(XE-2-192,XE-2,207,'16 ft N1–N2 centers',extension_color)
pt((XE-2-192+XE-2)/2,258,'NEW DOOR BAY',11,extension_color,'middle')
end()
group('dimensions')
dv(-60,L,N,'82 in existing')
dv(287,YN,N,'5 ft',blue)
dv(190,N-33,N,'2 ft 9 in',blue)
dv(116,YN,N-33,'2 ft 3 in',blue)
dh(W,E,207,'12 in',label)
dh(XE,E,157,'4 ft',blue)
dv(-72,YS+2,0,'66 in centers',blue)
pl(-77,0,0,0,label,.7,True)
pl(-77,YS+2,XW+2,YS+2,blue,.7,True)
dh(XW,0,-85,'3 ft',blue)
dh(0,W,-104,'EXISTING 20 ft 9½ in',label)
pt(-34,-97,'west projection',10,blue)
end()
purple='#a05371'
wall_posts=[{'id':'E-S','x':W-4,'y':-4,'width':4,'depth':4,'option':'A and B'},
            {'id':'E-N','x':W-4,'y':L,'width':4,'depth':4,'option':'A and B'},
            {'id':'E-M','x':W-5,'y':next(c['y'] for c in columns if c['id']=='W3')-2,'width':4,'depth':4,'option':'B only'}]
group('east-wall-strengthening')
# Dashed overhead centerline is symbolic: beam width and connections unresolved.
pl(W-2,-4,W-2,L+4,purple,1.4,True)
for post in wall_posts:
    x,y=post['x'],post['y'];concealed=post['id']=='E-M'
    for a,b,c,d in [(x,y,x+4,y),(x+4,y,x+4,y+4),(x+4,y+4,x,y+4),(x,y+4,x,y)]:pl(a,b,c,d,purple,2,concealed)
    if not concealed:pl(x,y,x+4,y+4,purple,1.5);pl(x,y+4,x+4,y,purple,1.5)
    yy=y+2
    pl(x+4,yy,282,yy,purple,.7)
    pt(286,yy+3,post['id']+(' / B' if concealed else ''),13,purple)
dh(XE,W,100,'36 in offset',purple)
end()
line(828,182,828,1000,'#e4e4e4')
text(870,204,'OPTIONAL EAST-WALL FRAMING',18,purple)
for i,t in enumerate(['A — E-S + E-N end posts with overhead beam/truss.',
                       'B — Same frame, plus concealed E-M aligned with W3.',
                       'Purple dashes along wall = overhead beam centerline.',
                       'E-S/E-N are separate from upper-frame S/N columns.',
                       'End-post east faces align with existing wall east face.',
                       'Entire 12-in east strip stays clear of posts.']):text(870,240+i*26,t,15)
# Enlarged local plans, same 10 px/in scale. North is up.
def detail_rect(x,y,w,h,c,dash=False):
    for a,b,e,f in [(x,y,x+w,y),(x+w,y,x+w,y+h),(x+w,y+h,x,y+h),(x,y+h,x,y)]:line(a,b,e,f,c,1.7,dash)
text(870,433,'1 / NORTH END POST — PLAN DETAIL',16)
# wall east face at 1020; 6 in wall / 12 in clear strip
for yy in [490,735]:
    detail_rect(960,yy,60,90,label)
    line(1140,yy-50,1140,yy+100,ink,1.3,True)
    line(1020,yy-35,1140,yy-35,ink,.8)
    text(1080,yy-43,'12 in clear',13,ink,'middle')
    text(1080,yy+50,'NO POSTS',12,label,'middle')
detail_rect(980,450,40,40,purple)
text(895,474,'E-N',14,purple);line(929,470,980,470,purple,.8)
text(1160,480,'Property line',13)
text(1160,517,'End post beyond wall end;',13,purple)
text(1160,539,'east face flush with wall.',13,purple)
text(950,600,'6-in existing wall',13,label)
text(870,634,'South end mirrors this: E-S lies just south of the wall.',14)
text(870,679,'2 / CENTER POST — PLAN DETAIL (B ONLY)',16)
detail_rect(970,758,40,40,purple,True)
text(1160,764,'E-M: 4-in post within wall.',13,purple)
text(1160,788,'Local cutout; plaster flush.',13,purple)
line(1010,778,1032,804,purple,.8)
text(950,846,'Dashed post is concealed by restored wall finish.',13,purple)
text(870,895,'CONNECTIONS TO DEVELOP',16)
for i,t in enumerate(['Upper steel edge stays 36 in inward of the wall face.',
                       'Beam width, transfer connections and foundations are unresolved.',
                       'E-M/B now aligns with W3 at 185 in north of the south wall.',
                       'WBN removed; N1 moved 16 ft west of N2 (centers).']):text(870,922+i*22,t,13)
text(60,1020,'Sources: Draft East Wall strengthening (linked task), East Wall Study rev. 04, and current floor plan rev. 11.',12,label)
# North arrow and physical scale, independent of printed page size.
line(750,829,750,765,ink,1.5);line(750,765,744,778,ink,1.5);line(750,765,756,778,ink,1.5);text(750,752,'N',16,ink,'middle')
for i in range(3):pl(i*24,-154,(i+1)*24,-154,ink,3 if i%2==0 else 1)
for i in range(4):pt(i*24,-167,str(i*2)+' ft',12,ink,'middle')
text(60,1090,'Local boundary segments only • no surveyed bearings • layout study using requested setbacks, not a code determination.',12,label)
svg.append('</svg>');(OUT/'floor-plan-study.svg').write_text('\n'.join(svg))
pdf.showPage();pdf.save();im.save(OUT/'floor-plan-study.png')
basis={'units':'inches','source':'../model/parameters.json','origin':'existing outside southwest corner; x east, y north','existing_width':W,'existing_length':L,'east_property_x':E,'north_property_y':N,'east_truss_outside_edge_x':E-48,'truss_width':None,'north_wall_outside_face_y':N-60,'north_roof_overhang':27,'north_roof_edge_y':N-33,'north_roof_edge_property_clearance':33,'remaining_roof_geometry':'slopes and east/west eave details to develop','upper_structure_outline':[[XW,YS],[XE,YS],[XE,YN],[XW,YN]],'roof_outline':[[XW,YS],[XE,YS],[XE,N-33],[XW,N-33]],'columns':columns,'column_symbol_width':4,'south_support_centerlines_y':{c['id']:c['y'] for c in columns if c['id'] in ('W1','S1','S2')},'south_beam_centerline_y':SOUTH_CL,'south_beam_width_provisional':8,'south_roof_edge_y':YS,'south_roof_edge_basis':'Blue edge retained at y=-68; W1/S1/S2 south faces flush with edge; column centers y=-66; provisional beam center remains y=-64','loft_outline':[[XW,LOFT_SOUTH],[XE,LOFT_SOUTH],[XE,YN],[XW,YN]],'loft_outline_basis':'User expanded deck to full width and north border, south edge at W2 support line','north_column_alignment':'Outer faces flush to north border; W4 west face flush to west border','framing_source':'../structural-study/framing-member-register.json','deck_and_member_width_source':'../model-renders/build_and_render.py','north_wall_extension_beyond_existing':22,'east_interpretation_confirmed':True,'setback_basis':'User correction: east limit 4 ft; north wall 5 ft; north roof overhang 2 ft 3 in.'}
basis['north_door_bay']={'west_post':'N1','east_post':'N2','center_spacing_in':192,'clear_between_4in_posts_in':188,'finished_opening':'not yet sized'}
basis['possible_ground_floor_extension']={'status':'option only','path':extension_path,'route':'WB3 -> W3 -> W4 -> N1 -> N2 -> existing north wall; close along existing wall to WB3','geometry_basis':'concept route through post centers; not finished wall faces'}
basis['east_wall_posts']=wall_posts
basis['east_wall_source']='../east-wall-study/README.md revision 04; task 01a0a6c5-3c15-70a2-b201-839830bb0b20'
basis['east_wall_overhead_beam']='symbolic centerline x=247.5, y=-4..253; width and connections unresolved'
assert all(post['x']+post['width']<=W for post in wall_posts)
assert wall_posts[2]['x']>=W-6
assert wall_posts[2]['y']+2==next(c['y'] for c in columns if c['id']=='W3')
assert next(c for c in columns if c['id']=='S3')['y']==wall_posts[0]['y']+wall_posts[0]['depth']/2
(OUT/'floor-plan-study-basis.json').write_text(json.dumps(basis,indent=2)+'\n')
assert next(c for c in columns if c['id']=='WB3')['y']==next(c for c in columns if c['id']=='W3')['y']
assert all(c['x']+2==0 for c in columns if c['id'] in ('WB3','WBN'))
assert not any(c['id']=='WBN' for c in columns)
assert next(c['x'] for c in columns if c['id']=='N2')-next(c['x'] for c in columns if c['id']=='N1')==192
assert N-(N-60)==60
assert E-(E-48)==48
assert (N-60)-L==22
assert (N-33)-(N-60)==27
assert all(c['x']+2<=XE for c in columns)
assert next(c for c in columns if c['id']=='W1')['y']-2==YS
assert next(c for c in columns if c['id']=='W1')['x']-2==XW
assert all(c['y']-2==YS for c in columns if c['id'] in ('S1','S2'))
assert all(c['x']-2==XW for c in columns if c['id'] in ('W2','W3','W4'))
assert next(c for c in columns if c['id']=='S3')['status']=='proposed'
assert next(c for c in columns if c['id']=='S3')['y']==-2
assert YS+4==SOUTH_CL
assert all(c['y']+2==YN for c in columns if c['id'] in ('W4','N1','N2'))
assert next(c for c in columns if c['id']=='W4')['x']-2==XW
print('Created single combined floor-plan study.')
