from pathlib import Path
import re
from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer,Image,PageBreak,KeepTogether
from reportlab.lib.styles import getSampleStyleSheet,ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
R=Path(__file__).resolve().parent
styles=getSampleStyleSheet();styles.add(ParagraphStyle(name='BodyCustom',fontName='Helvetica',fontSize=10,leading=15,spaceAfter=9,textColor=colors.HexColor('#34413e')))
styles.add(ParagraphStyle(name='CaptionCustom',fontName='Helvetica',fontSize=9,leading=13,spaceAfter=14,textColor=colors.HexColor('#65736a')))
styles['Title'].textColor=colors.HexColor('#293d34');styles['Heading2'].textColor=colors.HexColor('#293d34')
story=[Paragraph('BACKYARD<br/>EXISTING CONDITIONS',styles['Title']),Paragraph('Photo-informed Blender reconstruction · 8 September 2026',styles['CaptionCustom'])]
hero=R/'01-backyard-overview.png'
if hero.exists():story.append(Image(str(hero),width=510,height=382.5))
story.extend([Paragraph('Current garage, corrected site layout and photo-derived surface materials',styles['Heading2']),Paragraph('An editable baseline for future garage design. The four outdoor rooms, north-aligned work shelter, triangular house bay and shortened pergola reflect the owner’s corrections. Yard dimensions and detailed landscaping remain estimates.',styles['BodyCustom']),PageBreak()])
story.extend([Paragraph('Site organization',styles['Title']),Image(str(R/'source-site-plan.png'),width=450,height=510),Paragraph('Annotated plan from the corrected source model. Dimensions are estimated except where supported by the existing garage measurements. Tree canopies are omitted in this plan for clarity.',styles['CaptionCustom']),PageBreak()])
text=(R/'BACKYARD-EXISTING-CONDITIONS.md').read_text();paras=text.split('\n\n')
for para in paras:
 if para.startswith('# '):continue
 if para.startswith('## Photo-'):continue
 if para.startswith('### '):story.append(Paragraph(para[4:],styles['Heading2']))
 else:
  para=para.replace('&','&amp;').replace('<','&lt;').replace('>','&gt;');para=re.sub(r'`([^`]+)`',r'<font name="Courier">\1</font>',para)
  story.append(Paragraph(para,styles['BodyCustom']))
for file,title,caption in [('02-patio-toward-garage.png','Patio toward the existing garage','Photo-derived stone and stucco; procedural foliage at the corrected planting locations.'),('03-conversation-area.png','Conversation area','Central fire pit and inward-facing seating, north of the planted dividing fence.'),('04-house-and-gardens.png','House and garden context','Existing house massing and garden rooms. The modeled house remains an approximate reconstruction.')]:
 if (R/file).exists():story.extend([PageBreak(),Paragraph(title,styles['Title']),Image(str(R/file),width=510,height=382.5),Paragraph(caption,styles['CaptionCustom'])])
story.extend([PageBreak(),Paragraph('Extracted surface samples',styles['Title']),Image(str(R/'texture-contact.jpg'),width=510,height=357),Paragraph('Photographic color crops after partial illumination normalization. The material atlas repeats mirrored versions of these samples. Bump and roughness maps are approximations. See textures/manifest.json for exact source crop coordinates.',styles['BodyCustom'])])
def footer(c,doc):
 c.setStrokeColor(colors.HexColor('#cbd1c8'));c.line(42,39,570,39);c.setFont('Helvetica',8);c.setFillColor(colors.HexColor('#68736b'));c.drawString(42,25,'BACKYARD EXISTING CONDITIONS  /  PHOTO-INFORMED MODEL');c.drawRightString(570,25,str(doc.page))
doc=SimpleDocTemplate(str(R/'Backyard-Existing-Conditions.pdf'),pagesize=(612,792),rightMargin=51,leftMargin=51,topMargin=42,bottomMargin=55,title='Backyard Existing Conditions',author='Existing site reconstruction')
doc.build(story,onFirstPage=footer,onLaterPages=footer)
print('Report written')
