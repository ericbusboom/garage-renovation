"""North framing elevation from the authoritative, round-tripped COMPAS model."""
import os,json,hashlib
from pathlib import Path
os.environ.setdefault('MPLCONFIGDIR','/tmp/garage-mpl')
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection
from compas.data import json_load
import frame_models
ROOT=Path(__file__).resolve().parents[1];P=ROOT/'roof-studies/square-upper-west/connected-frame';OUT=P/'elevations';OUT.mkdir(exist_ok=True)
SRC=frame_models.latest('square-upper-west')
data=json_load(SRC);spec=data['specification'];elements={e.name:e for e in data['model'].elements()}
fig,ax=plt.subplots(figsize=(14,10));fig.patch.set_facecolor('#fbfbf8');ax.set_facecolor('#fbfbf8')
registry={};north=[];background=[]
for mid,e in elements.items():
 m=spec['members'][mid];vs,fs=e.compute_elementgeometry().to_vertices_and_faces();vs=np.array(vs)
 foreground=m['group']=='Truss_TN' or mid in ('W.W4','E.W4','N2','N1 / U-W') or mid.startswith('BR-N-')
 entry=(mid,vs,fs,m)
 (north if foreground else background).append(entry)
for layer,entries in [('background',background),('north',north)]:
 for i,(mid,vs,fs,m) in enumerate(sorted(entries,key=lambda o:o[1][:,1].mean())):
  ref=layer+'-'+str(i);triangles=[np.column_stack([-vs[f,0],vs[f,2]]) for f in fs]
  coll=PolyCollection(triangles,facecolors='#355867' if layer=='north' else '#cdd4d5',edgecolors='none',alpha=1 if layer=='north' else .42,zorder=3 if layer=='north' else 1)
  coll.set_gid(ref);ax.add_collection(coll);registry[ref]={'member':mid,'name':m.get('display_name',m['source_name']),'group':m['group'],'layer':layer,'joints':m['nodes']}
ax.set_aspect('equal');ax.set_xlim(-278,70);ax.set_ylim(-26,250)
ax.set_xlabel('Plan X coordinate / inches — east ← → west',labelpad=12);ax.set_ylabel('Height above study floor / inches',labelpad=12)
xs=[-34,0,100,211.5,247.5];ax.set_xticks([-x for x in xs],[str(x) for x in xs]);ax.set_yticks([0,50,100,115,150,200,224.25,228.75],['0','50','100','115','150','200','224.25','228.75']);ax.tick_params(axis='y',labelsize=9)
ax.spines[['top','right']].set_visible(False);ax.grid(alpha=.12);ax.axhline(0,color='#71818a',lw=.8)
for mid,label in [('N2','N2'),('N1 / U-W','N1'),('W.W4','W4')]:
 e=elements[mid];x=-e.start.x
 ax.annotate(label,xy=(x,2),xytext=(x,-15),ha='center',fontsize=11,weight='bold',color='#264c5d',arrowprops=dict(arrowstyle='-',color='#6d858d'),zorder=6)
ax.text(-27.375,151,'Western-half doorway',ha='center',fontsize=11,color='#264c5d',bbox=dict(fc='white',ec='none',alpha=.85),zorder=7)
for label,point,text in [('1  North upper chord · 4 × 4 in',(-86,224.25),(-116,241)),('2  Full western-half header',(-27.375,207),(-27.375,188)),('3  North lower chord',(-105,115),(-138,134)),('4  Center vertical · 4 × 4 in',(-88.75,161),(-151,177))]:
 ax.annotate(label,xy=point,xytext=text,ha='center',fontsize=10,color='#264c5d',bbox=dict(boxstyle='round,pad=.35',fc='white',ec='#b7c7cc'),arrowprops=dict(arrowstyle='-',color='#6d858d'),zorder=7)
fig.suptitle('NORTH ELEVATION · TRUSSES AND FRAMING',x=.075,ha='left',fontsize=19,weight='bold')
fig.text(.075,.921,'Looking south  |  East left · West right  |  Roof and wall cladding hidden',fontsize=11,color='#4b6570')
fig.text(.075,.885,'Dark: north framing at Y259 in.    Pale: framing beyond, shown for context.',fontsize=10,color='#4b6570')
fig.text(.075,.038,'Linked to frame-spec.json → COMPAS joint graph and member model. Includes corrected east supports; S2–S3 braces removed.\nGeometric study; joint detailing and structural sizing remain unresolved. Mesh projection with depth ordering; not a fabrication drawing.',fontsize=9,color='#526b73')
fig.subplots_adjust(left=.12,right=.96,top=.85,bottom=.14)
for ext in ('png','svg','pdf'):fig.savefig(OUT/('north-framing-elevation.'+ext),dpi=180)
plt.close(fig)
(OUT/'north-framing-register.json').write_text(json.dumps(registry,indent=2))
svg=(OUT/'north-framing-elevation.svg').read_text();svg=svg[svg.index('<svg'):]
html='''<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>North framing elevation</title><style>body{margin:0;background:#fbfbf8;color:#264c5d;font:15px system-ui}header{padding:12px 22px;border-bottom:1px solid #ccd6d9}button{padding:7px 12px;margin-left:16px;cursor:pointer}main{max-width:1350px;margin:auto}svg{width:100%;height:auto}#selected{padding:10px 22px;background:#e9eff0;position:sticky;top:0;z-index:2}g[data-member]{cursor:pointer}g[data-member]:hover path{stroke:#d06c31;stroke-width:.8}footer{padding:12px 22px}a{color:#225d78}</style></head><body><header><strong>North framing elevation</strong><button id="context">Hide framing beyond</button></header><div id="selected">Click a member to identify it. Labels 1–4 and support names are available for discussion.</div><main>'''+svg+'''</main><footer><a href="north-framing-elevation.png">PNG for markup</a> · <a href="north-framing-elevation.pdf">PDF</a> · <a href="north-framing-elevation.svg">SVG</a></footer><script>const members='''+json.dumps(registry)+''';for(const [id,m] of Object.entries(members)){const el=document.getElementById(id);if(el){el.dataset.member=id;el.onclick=()=>document.getElementById('selected').textContent=m.member+' — '+m.name+' · '+m.layer+' framing';}}let show=true;document.getElementById('context').onclick=()=>{show=!show;document.querySelectorAll('[id^="background-"]').forEach(e=>e.style.display=show?'':'none');document.getElementById('context').textContent=show?'Hide framing beyond':'Show framing beyond';};</script></body></html>'''
(OUT/'north-framing-elevation.html').write_text(html)
(OUT/'north-framing-validation.json').write_text(json.dumps({'source_sha256':hashlib.sha256(SRC.read_bytes()).hexdigest(),'view':'north looking south; east left, west right','frame_members':len(elements),'foreground_members':len(north),'background_members':len(background),'enclosure_objects':0},indent=2))
print(OUT/'north-framing-elevation.png')
