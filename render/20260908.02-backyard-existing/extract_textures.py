from pathlib import Path
import json
import numpy as np
from PIL import Image,ImageFilter,ImageDraw
R=Path(__file__).resolve().parent;root=R.parent
specs=[
('flagstone','existing-site/references/patio/IMG_4224.png',(.22,.73,.75,.98),(1024,512),(2.4,1.5)),
('woodchips','existing-site/references/areas/IMG_4220.png',(.47,.48,.53,.60),(512,512),(.65,.9)),
('garage_stucco','existing-site/references/new/IMG_4216.png',(.255,.37,.315,.49),(512,512),(.55,.8)),
('house_stucco','site-renderings/references/IMG_4199.jpg',(.77,.66,.82,.75),(512,512),(.5,.5)),
('painted_timber','existing-site/references/new/IMG_4217.png',(.681,.43,.693,.59),(128,1024),(.13,1.8)),
('weathered_fence','existing-site/references/patio/IMG_4226.png',(.16,.10,.18,.15),(256,512),(.18,.50))]
manifest=[];contact=Image.new('RGB',(1200,840),'white');draw=ImageDraw.Draw(contact)
for i,(name,src,rect,size,metres) in enumerate(specs):
 im=Image.open(root/src).convert('RGB');w,h=im.size;box=tuple(round(v*(w if j%2==0 else h)) for j,v in enumerate(rect));crop=im.crop(box);crop.save(R/'textures'/f'{name}_source.png')
 # Retain photographed color and texture, attenuate broad illumination variation.
 crop=crop.resize(size,Image.Resampling.LANCZOS);a=np.asarray(crop).astype(float)/255
 blur=np.asarray(crop.filter(ImageFilter.GaussianBlur(max(size)*.08))).astype(float)/255
 mean=np.mean(a,axis=(0,1));clean=np.clip(a/(blur+.03)*(mean+.03),0,1)*.6+a*.4
 color=Image.fromarray((np.clip(clean,0,1)*255).astype('uint8'))
 # Mirrored 2x2 atlas has continuous boundaries; repetitive motifs remain possible.
 atlas=Image.new('RGB',(size[0]*2,size[1]*2));atlas.paste(color,(0,0));atlas.paste(color.transpose(Image.Transpose.FLIP_LEFT_RIGHT),(size[0],0));atlas.paste(color.transpose(Image.Transpose.FLIP_TOP_BOTTOM),(0,size[1]));atlas.paste(color.transpose(Image.Transpose.ROTATE_180),(size[0],size[1]));atlas.save(R/'textures'/f'{name}_color.png')
 gray=atlas.convert('L');gray.save(R/'textures'/f'{name}_bump.png')
 # Not physical PBR recovery: neutral roughness modulated very slightly by luminance.
 rough=np.clip(.80+(np.asarray(gray).astype(float)/255-.5)*.10,0,1)
 Image.fromarray((rough*255).astype('uint8')).save(R/'textures'/f'{name}_roughness.png')
 thumb=color.copy();thumb.thumbnail((390,355));x=i%3*400;y=i//3*420;contact.paste(thumb,(x,y+30));draw.text((x+6,y+6),name,fill='black')
 manifest.append({'material':name,'source':str(root/src),'source_crop_pixels':box,'source_crop_normalized':rect,'atlas_period_metres':[v*2 for v in metres],'processing':'Crop, resize, partial broad-illumination normalization, mirrored seamless atlas. Bump is luminance; roughness is an approximation. No generative replacement.','color_space':'sRGB color; Non-Color bump/roughness'})
contact.save(R/'texture-contact.jpg');(R/'textures/manifest.json').write_text(json.dumps(manifest,indent=2))
