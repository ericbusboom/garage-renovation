from pathlib import Path
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
p=Path(__file__).resolve().parent
c=canvas.Canvas(str(p/'python-model-visualizations.pdf'),pagesize=(1008,792))
for name in ['model-3d.png','framing-labelled.png','truss-deformation.png']:
 im=ImageReader(str(p/name));w,h=im.getSize();scale=min(960/w,736/h);c.drawImage(im,(1008-w*scale)/2,35+(736-h*scale)/2,width=w*scale,height=h*scale)
 c.setFont('Helvetica',9);c.drawString(28,17,'Python model visualization | Saved preliminary HSS analysis; W-section trolley revision pending');c.showPage()
c.save()
