"""Deterministic garage mesh model + VTK physically shaded renders. No image generation.
Coordinates entered in inches, exported geometry in meters. Materials are illustrative.
"""
from pathlib import Path
import math,json,collections
import numpy as np
import vtk
from PIL import Image,ImageDraw,ImageFont
OUT=Path(__file__).parent;ROOT=OUT.parent
DIM=json.loads((ROOT/'structural-study/section-dimensions.json').read_text())
H=98.5;F=107.25;BT=106.5;XS=224.25;YS=-63;YN=255;W=249.5;BR=DIM['break_y_from_south_wall'];M=math.tan(math.pi/6)
def roof(y):return min(BT+(y-YS)*M,F+120)
materials={'steel':('#4c626e',.50,.32),'beam':('#38637c',.48,.32),'truss':('#a36543',.48,.35),'wall':('#b0bcc1',.0,.85),'trim':('#eeeae1',.0,.45),'glass':('#588393',.35,.17),'roof':('#242f38',.40,.25),'pv':('#223545',.65,.13),'wood':('#b5946b',.0,.68),'endwood':('#94734c',.0,.73),'slab':('#babdb8',.0,.85),'ground':('#d5d8d5',.0,.95),'dark':('#263941',.45,.4),'shelter':('#83988c',.0,.65)}
objects=[]
def mesh(name,vertices,faces,mat,group):objects.append(dict(name=name,vertices=[[float(t)*.0254 for t in v] for v in vertices],faces=faces,material=mat,group=group))
def box(name,x,y,z,dx,dy,dz,mat='steel',group='frame'):
 if min(dx,dy,dz)<=0:return
 v=[(x,y,z),(x+dx,y,z),(x+dx,y+dy,z),(x,y+dy,z),(x,y,z+dz),(x+dx,y,z+dz),(x+dx,y+dy,z+dz),(x,y+dy,z+dz)]
 mesh(name,v,[[0,3,2,1],[4,5,6,7],[0,1,5,4],[1,2,6,5],[2,3,7,6],[3,0,4,7]],mat,group)
def member(name,a,b,width=3,depth=None,mat='truss',group='frame'):
 a=np.array(a,float);b=np.array(b,float);d=b-a;d/=np.linalg.norm(d);ref=np.array([0,0,1.])
 if abs(d@ref)>.95:ref=np.array([1.,0,0])
 u=np.cross(d,ref);u/=np.linalg.norm(u);v=np.cross(d,u);depth=depth or width
 vs=[p+su*u*width/2+sv*v*depth/2 for p in [a,b] for su,sv in [(-1,-1),(1,-1),(1,1),(-1,1)]]
 mesh(name,vs,[[0,3,2,1],[4,5,6,7],[0,1,5,4],[1,2,6,5],[2,3,7,6],[3,0,4,7]],mat,group)
def sheet(name,pts,mat,group,thick=.3):
 n=len(pts);v=pts+[(x,y,z-thick) for x,y,z in pts]
 faces=[list(range(n)),list(reversed(range(n,2*n)))]+[[i,(i+1)%n,(i+1)%n+n,i+n] for i in range(n)]
 mesh(name,v,faces,mat,group)
def ibeam(name,a,b,d=8,bf=8,mat='beam'):
 # Horizontal longitudinal members, actual I-shaped faces.
 a=np.array(a,float);b=np.array(b,float);l=np.linalg.norm(b-a);u=(b-a)/l;v=np.array([-u[1],u[0],0.]);tf=.5;tw=.375
 cross=[(-bf/2,0),(bf/2,0),(bf/2,tf),(tw/2,tf),(tw/2,d-tf),(bf/2,d-tf),(bf/2,d),(-bf/2,d),(-bf/2,d-tf),(-tw/2,d-tf),(-tw/2,tf),(-bf/2,tf)]
 vs=[p+v*x+np.array([0,0,z]) for p in [a,b] for x,z in cross];n=len(cross)
 mesh(name,vs,[list(reversed(range(n))),list(range(n,2*n))]+[[i,(i+1)%n,(i+1)%n+n,i+n] for i in range(n)],mat,'frame')
# Ground and foundation slab (no invented finished-site survey).
box('Studio ground',-330,-250,-5,900,830,3,'ground','site')
box('Existing garage slab',0,0,-2,249.5,249,2,'slab','existing')
# Import measured lower wall and window/door meshes from the existing editable model.
base=json.loads((ROOT/'model/scene.json').read_text())
for p in base['parts']:
 if p['group'] not in ['existing','infill']:continue
 name=p['name'];mat='glass' if 'window' in name.lower() else 'trim' if 'door' in name.lower() else 'wall'
 mesh(name,p['vertices'],p['triangles'],mat,'existing')
# Exterior columns, retained locations; all tops at98.5. S1 pending connection retained as visible column.
reg=json.loads((ROOT/'structural-study/framing-member-register.json').read_text())
for p in reg['posts']:
 x=p['x'];y=p['y'];n=p['id'];box(n+' steel column',x-2,y-2,0,4,4,H,'steel','columns')
 box(n+' base plate',x-4,y-4,0,8,8,.5,'dark','columns')
 box(n+' cap plate',x-4,y-4,H-.5,8,8,.5,'steel','columns')
 for xx in [-2.8,2.8]:
  for yy in [-2.8,2.8]:box(n+' anchor',x+xx-.25,y+yy-.25,.5,.5,.5,.5,'steel','columns')
# Beams from current plan, not truss substitutions.
ibeam('T-SO beam',(-32,YS,H),(249.5,YS,H))
ibeam('B2 beam',(0,185,H),(XS,185,H))
ibeam('B3 beam',(0,249,H),(246.5,249,H))
ibeam('B-WO beam',(-32,YS,H),(-32,253,H))
for n,y in [('O2',69.75),('O3',185)]:ibeam(n,(-32,y,H),(0,y,H),d=8,bf=6)
# Full height transverse trusses. Interior rectangles are concept moment-frame bays.
def transverse(name,y,a,b,top,panels=6):
 lo=H+1.5;hi=top-1.5
 member(name+' bottom',(a,y,lo),(b,y,lo));member(name+' top',(a,y,hi),(b,y,hi))
 xx=np.linspace(a,b,panels+1)
 for x in xx:member(name+' upright',(x,y,lo),(x,y,hi))
 for i in [0,panels-1]:member(name+' end brace',(xx[i],y,lo if i==0 else hi),(xx[i+1],y,hi if i==0 else lo),2.5)
 for x in xx[1:-1]:box(name+' joint plate',x-3,y-1.75,hi-5,6,.5,6,'truss','frame')
transverse('T-S',0,0,246.5,roof(0))
transverse('T1',69.75,0,XS,roof(69.75))
# Longitudinal trusses, top chords follow the new roof profile.
for name,x in [('T-W',0),('T-E',XS)]:
 cuts=sorted(set([YS,-21.25,0,69.75,BR,185,253]+([186,246] if name=='T-W' else [126])))
 member(name+' bottom',(x,YS,H+1.5),(x,253,H+1.5))
 for a,b in zip(cuts[:-1],cuts[1:]):
  member(name+' top',(x,a,roof(a)-1.5),(x,b,roof(b)-1.5))
  # Keep west French-door bay clear; no lattice on west walkway.
  if not(name=='T-W' and a>=185):member(name+' web',(x,a,H+3),(x,b,roof(b)-3),2.5)
 for y in cuts:member(name+' vertical',(x,y,H+1.5),(x,y,roof(y)-1.5))
 if name=='T-W':member('French door header',(x,186,F+83),(x,246,F+83))
# T-N complete north wall / door framing.
zhead=F+96
transverse('T-N header',253,-32,249.5,F+120,8) if False else None
member('T-N bottom',(-32,253,H+1.5),(249.5,253,H+1.5))
for x in [-32,53.25,81.5,113.5,224.25,249.5]:member('T-N upright',(x,253,H+1.5),(x,253,F+118.5))
member('T-N header lower',(-32,253,zhead),(249.5,253,zhead))
member('T-N top',(-32,253,F+118.5),(249.5,253,F+118.5))
xx=np.linspace(-32,249.5,9)
for i,(a,b) in enumerate(zip(xx[:-1],xx[1:])):
 member('T-N header vertical',(a,253,zhead),(a,253,F+118.5),2.5)
 member('T-N header brace',(a,253,zhead if i%2==0 else F+118.5),(b,253,F+118.5 if i%2==0 else zhead),2.5)
member('T-N door head',(81.5,253,F+85.5),(113.5,253,F+85.5))
# Floor: joists shown between beams; deck begins at72, leaving south6ft void.
for x in np.arange(7.5,XS-2,16):
 for a,b in [(72,181),(189,245)]:box('Wood floor joist',x,a,H+.5,1.5,b-a,7.5,'wood','joists')
box('Loft plywood',0,72,BT,XS,183,.75,'wood','deck')
# Ground-level cabinets are unchanged/nonstructural.
box('Existing cabinets',213.25,55.5,1,30,148,H-1,'wood','cabinets')
for i in range(6):
 y=56+i*24.5;box('Cabinet door',212.5,y,3,.6,23.3,H-5,'endwood','cabinets');box('Cabinet pull',211.8,y+19,45,.7,.6,6,'dark','cabinets')
# Main solar slope and restored shallow four-sided hip cap over the rear section.
for a,b in [(YS,BR)]:sheet('Solar roof assembly',[(0,a,roof(a)+8),(W,a,roof(a)+8),(W,b,roof(b)+8),(0,b,roof(b)+8)],'roof','roof',8)
CAP_RISE=18;OVERHANG=8
x0=-OVERHANG;x1=W+OVERHANG;y0=BR-OVERHANG;y1=YN+OVERHANG
ze=F+120+8;zr=ze+CAP_RISE;yc=(y0+y1)/2
inset=(y1-y0)/2
rl=(x0+inset,yc,zr);rr=(x1-inset,yc,zr)
sw=(x0,y0,ze);se=(x1,y0,ze);ne=(x1,y1,ze);nw=(x0,y1,ze)
for n,pts in [('south',[sw,se,rr,rl]),('east',[se,ne,rr]),('north',[ne,nw,rl,rr]),('west',[nw,sw,rl])]:
 sheet('Hip cap '+n,pts,'roof','roof',.65)
box('Hip cap white soffit',x0,y0,F+120,x1-x0,y1-y0,.75,'trim','roof')
for y in [y0,y1]:box('Hip cap fascia',x0,y-.5,F+120,x1-x0,1,8,'trim','roof')
for x in [x0,x1]:box('Hip cap fascia',x-.5,y0,F+120,1,y1-y0,8,'trim','roof')
DIM['hip_cap']={'rise_inches':CAP_RISE,'overhang_inches':OVERHANG,'fascia_inches':8,'ridge_elevation_inches':zr,'ridge_direction':'east-west','revision':'2026-09-08'}
# Integrated PV surface grid: geometric tiles, flush above the waterproof roof.
for a in np.arange(YS+2,BR-1,39):
 b=min(a+37.8,BR-1)
 for x in np.arange(2,W-1,41.5):
  xx=min(x+40.3,W-1)
  sheet('Flush solar / infill panel',[(x,a,roof(a)+8.12),(xx,a,roof(a)+8.12),(xx,b,roof(b)+8.12),(x,b,roof(b)+8.12)],'pv','roof',.15)
for x in [0,W]:
 member('Roof fascia',(x,YS,roof(YS)+4),(x,BR,roof(BR)+4),1,8,'trim','roof')

box('South fascia',0,YS-.5,BT,W,1,8,'trim','roof')
# Finished upper enclosure with explicit door/window openings.
def wallplane(name,axis,pos,start,end,openings):
 cuts=sorted(set([start,end]+[q for op in openings for q in op[:2]]+[BR] if axis=='x' and start<BR<end else [start,end]+[q for op in openings for q in op[:2]]))
 for a,b in zip(cuts[:-1],cuts[1:]):
  if a<start or b>end:continue
  topa=roof(a) if axis=='x' else roof(pos);topb=roof(b) if axis=='x' else roof(pos)
  op=next((o for o in openings if o[0]<=a and o[1]>=b),None)
  def face(z1,z2a,z2b):
   pts=[(pos,a,z1),(pos,b,z1),(pos,b,z2b),(pos,a,z2a)] if axis=='x' else [(a,pos,z1),(b,pos,z1),(b,pos,z2b),(a,pos,z2a)]
   mesh(name,pts,[[0,1,2,3]],'wall','enclosure')
  if op:
   if op[2]>H:face(H,op[2],op[2])
   if min(topa,topb)>op[3]:face(op[3],topa,topb)
   # Glazing inset, framing is real geometry.
   pts=[(pos,a,op[2]),(pos,b,op[2]),(pos,b,op[3]),(pos,a,op[3])] if axis=='x' else [(a,pos,op[2]),(b,pos,op[2]),(b,pos,op[3]),(a,pos,op[3])]
   mesh(name+' glazing',pts,[[0,1,2,3]],'glass','enclosure')
   for u in [a,b,(a+b)/2]:
    if axis=='x':box('Opening vertical trim',pos-1,u-1,op[2],2,2,op[3]-op[2],'trim','enclosure')
    else:box('Opening vertical trim',u-1,pos-1,op[2],2,2,op[3]-op[2],'trim','enclosure')
   for z in [op[2],op[3]]:
    if axis=='x':box('Opening horizontal trim',pos-1,a,z-1,2,b-a,2,'trim','enclosure')
    else:box('Opening horizontal trim',a,pos-1,z-1,b-a,2,2,'trim','enclosure')
  else:face(H,topa,topb)
wallplane('West loft wall','x',-.5,0,255,[(131,161,F+30,F+66),(186,246,F,F+80)])
wallplane('East loft wall','x',250,0,255,[])
wallplane('South upper wall','y',0,0,W,[])
wallplane('North upper wall','y',255,0,W,[(33.5,57.5,F+36,F+72),(81.5,113.5,F,F+84),(137.5,161.5,F+36,F+72)])
# White balcony/flat west walkway, no sloped lattice.
for y in np.arange(YS,177,7):box('Flat walkway slat',-32,y,BT-2,32,1.5,2,'trim','walkway')
box('White balcony floor',-32,177,BT,32,78,.75,'trim','walkway')
for y in np.arange(177,256,6):box('Balcony baluster',-33,y,F,1,1,42,'trim','walkway')
box('Balcony handrail',-34,177,F+40,3,78,2,'trim','walkway')
for y in [177,254]:box('Balcony return handrail',-32,y,F+40,32,1,2,'trim','walkway')
# Existing outbuilding, accepted approximate heights.
box('Workbench',-27,174,35,27,75,2,'wood','outbuilding')
box('Workbench rear panel',-1,174,0,1,75,96,'wood','outbuilding')
box('Electrical pillar',-174.25,174,0,10,48,96,'wall','outbuilding')
for x,y in [(-164.25,174),(-164.25,222),(-27,174),(-27,249)]:box('Shelter column',x,y,0,2.5,2.5,96,'steel','outbuilding')
for z in [78,93.5]:member('Existing shelter truss chord',(-164.25,174,z+1.25),(-27,174,z+1.25),2.5,mat='steel',group='outbuilding')
for x in np.linspace(-164.25,-27,7):box('Existing shelter truss vertical',x,174,78,2.5,2.5,18,'steel','outbuilding')
box('Shelter roof',-184.25,164,97.25,184.25,95,.75,'shelter','outbuilding')
for x in np.arange(-184,0,4):member('Roof corrugation',(x,164,98),(x,259,98),.3,mat='shelter',group='outbuilding')
# Exports independent of rendering.
(OUT/'garage-model.json').write_text(json.dumps({'units':'meters','source_units':'inches','objects':objects,'materials':materials,'basis':DIM},indent=1))
with (OUT/'garage-model.obj').open('w') as f:
 f.write('# Garage design study. Units meters. Generated from measured/model parameters.\nmtllib garage-model.mtl\n');idx=1
 for o in objects:
  if o['group']=='site':continue
  f.write('o '+o['name'].replace(' ','_')+'\nusemtl '+o['material']+'\n')
  for v in o['vertices']:f.write('v '+' '.join(f'{q:.7f}' for q in v)+'\n')
  for face in o['faces']:f.write('f '+' '.join(str(idx+i) for i in face)+'\n')
  idx+=len(o['vertices'])
with (OUT/'garage-model.mtl').open('w') as f:
 for n,(hx,metal,rough) in materials.items():
  rgb=[int(hx[i:i+2],16)/255 for i in [1,3,5]];f.write(f'newmtl {n}\nKd '+ ' '.join(map(str,rgb))+f'\nKs .3 .3 .3\nNs {max(5,(1-rough)*100):.1f}\n\n')
# Batched VTK geometry; normals and proper triangulation, same scene for every camera.
batches=collections.defaultdict(list)
for o in objects:batches[('trusses' if o['group']=='frame' and o['material']=='truss' else o['group'],o['material'])].append(o)
renderer=vtk.vtkRenderer();renderer.SetBackground(.89,.91,.91);renderer.SetBackground2(.98,.98,.97);renderer.GradientBackgroundOn()
actors=[]
for (group,mat),obs in batches.items():
 points=vtk.vtkPoints();cells=vtk.vtkCellArray();idx=0
 for o in obs:
  for v in o['vertices']:points.InsertNextPoint(*v)
  for face in o['faces']:
   cells.InsertNextCell(len(face))
   for i in face:cells.InsertCellPoint(idx+i)
  idx+=len(o['vertices'])
 pd=vtk.vtkPolyData();pd.SetPoints(points);pd.SetPolys(cells)
 tri=vtk.vtkTriangleFilter();tri.SetInputData(pd);tri.Update()
 normals=vtk.vtkPolyDataNormals();normals.SetInputConnection(tri.GetOutputPort());normals.ConsistencyOn();normals.AutoOrientNormalsOn();normals.SplittingOn();normals.SetFeatureAngle(35);normals.Update()
 mapper=vtk.vtkPolyDataMapper();mapper.SetInputConnection(normals.GetOutputPort());actor=vtk.vtkActor();actor.SetMapper(mapper)
 hx,metal,rough=materials[mat];rgb=[int(hx[i:i+2],16)/255 for i in [1,3,5]]
 prop=actor.GetProperty();prop.SetColor(*rgb);prop.SetInterpolationToPBR();prop.SetMetallic(metal);prop.SetRoughness(rough);prop.SetAmbient(.15);prop.SetDiffuse(.8);prop.SetSpecular(.3)
 renderer.AddActor(actor);actors.append((group,actor))
# Ambient occlusion gives true geometric contact shadows.
steps=vtk.vtkRenderStepsPass();ssao=vtk.vtkSSAOPass();ssao.SetDelegatePass(steps);ssao.SetRadius(.65);ssao.SetBias(.005);ssao.SetKernelSize(128);ssao.BlurOn();renderer.SetPass(ssao)
renderer.AutomaticLightCreationOff()
for pos,intensity,color in [((-8,-10,18),1.3,(1,.94,.86)),((10,-3,12),.75,(.8,.9,1)),((0,12,16),1.05,(1,1,1))]:
 light=vtk.vtkLight();light.SetLightTypeToSceneLight();light.SetPosition(*pos);light.SetFocalPoint(2,2,2);light.SetIntensity(intensity);light.SetColor(*color);renderer.AddLight(light)
window=vtk.vtkRenderWindow();window.SetOffScreenRendering(1);window.AddRenderer(renderer);window.SetSize(2200,1600);window.SetMultiSamples(0)
cam=renderer.GetActiveCamera();cam.SetViewUp(0,0,1);cam.ParallelProjectionOn()
views=[
 ('01-southwest-exterior',(-15,-20,13),(1,2.4,2.8),7.2,{'site','existing','columns','frame','enclosure','roof','walkway','outbuilding','deck','joists','cabinets'},'SOUTHWEST · FINISHED ENVELOPE'),
 ('02-southwest-structure',(-15,-19,15),(1.2,2.4,2.8),7.0,{'site','existing','columns','frame','trusses','walkway','deck','joists','cabinets'},'SOUTHWEST · ROOF AND CLADDING REMOVED'),
 ('03-northwest-structure',(-16,24,14),(1.1,2.5,2.6),7.2,{'site','existing','columns','frame','trusses','walkway','deck','joists','cabinets'},'NORTHWEST · FULL NORTH WALL TRUSS'),
 ('04-northwest-exterior',(-15,24,12),(1,2.7,2.8),7.3,{'site','existing','columns','frame','enclosure','roof','walkway','outbuilding','deck','joists','cabinets'},'NORTHWEST · LOFT DOOR AND BALCONY')]
for name,pos,target,scale,visible,title in views:
 for g,a in actors:a.SetVisibility(g in visible)
 cam.SetPosition(*pos);cam.SetFocalPoint(*target);cam.SetParallelScale(scale);renderer.ResetCameraClippingRange();window.Render()
 grab=vtk.vtkWindowToImageFilter();grab.SetInput(window);grab.SetInputBufferTypeToRGB();grab.ReadFrontBufferOff();grab.Update()
 writer=vtk.vtkPNGWriter();writer.SetFileName(str(OUT/(name+'.png')));writer.SetInputConnection(grab.GetOutputPort());writer.Write();print('Rendered '+name,flush=True)
 # Add only editorial title/notes to the renderer's output, never edit the geometry image content.
 im=Image.open(OUT/(name+'.png'));d=ImageDraw.Draw(im)
 fontpath='/System/Library/Fonts/Helvetica.ttc'
 try:font=ImageFont.truetype(fontpath,32);small=ImageFont.truetype(fontpath,19)
 except:font=small=ImageFont.load_default()
 d.text((64,48),title,font=font,fill='#293e47');d.text((64,94),'GARAGE STUDY  /  PARAMETRIC 3D MODEL  /  SEPTEMBER 8, 2026',font=small,fill='#62727a')
 d.text((64,1535),'Model-derived render · member sizes / truss webs illustrative · south support connections unresolved',font=small,fill='#62727a');im.save(OUT/(name+'.png'))
# Export interactive-friendly glTF scene, geometry in meters, embedded buffers.
for g,a in actors:a.SetVisibility(g not in ['site','enclosure','roof','outbuilding'])
exporter=vtk.vtkGLTFExporter();exporter.SetRenderWindow(window);exporter.SetFileName(str(OUT/'garage-framing.gltf'));exporter.InlineDataOn();exporter.SaveNormalOn();exporter.Write()
for g,a in actors:a.SetVisibility(g!='site')
exporter.SetFileName(str(OUT/'garage-complete.gltf'));exporter.Write()
print(f'Exported {len(objects)} named mesh objects and glTF/OBJ models.',flush=True)
