"""Linked west elevation: current CAD tessellation -> COMPAS meshes -> SVG/PDF/HTML."""
import sys,json,hashlib,os
from pathlib import Path
os.environ.setdefault('MPLCONFIGDIR','/tmp/garage-mpl')
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection
from compas.datastructures import Mesh
from compas.data import json_dump,json_load
ROOT=Path(__file__).resolve().parents[1]
P=Path(sys.argv[1]).resolve() if len(sys.argv)>1 else ROOT/'roof-studies/east-clerestory';OUT=P/'elevations';OUT.mkdir(exist_ok=True)
src=P/'cad-mesh.json';raw=json.loads(src.read_text())
objects=[]
for i,e in enumerate(raw['objects']):
 mesh=Mesh.from_vertices_and_faces(e['vertices'],e['triangles'])
 if not mesh.is_valid():
  # Boolean-cut compound solids can share tessellation edges; keep render triangles separate.
  vertices=[e['vertices'][i] for f in e['triangles'] for i in f]
  mesh=Mesh.from_vertices_and_faces(vertices,[[i,i+1,i+2] for i in range(0,len(vertices),3)])
 assert mesh.is_valid(),e['name']
 objects.append(dict(id=f'W{i+1:03}',name=e['name'],group=e['group'],material=e['material'],mesh=mesh))
bundle=dict(units='inches',source='../cad-mesh.json',source_sha256=hashlib.sha256(src.read_bytes()).hexdigest(),view='west looking east; north left, south right',objects=objects)
json_dump(bundle,OUT/'west-elevation.compas.json')
loaded=json_load(OUT/'west-elevation.compas.json');assert len(loaded['objects'])==len(objects)
colors={'steel':'#3c505a','rafter':'#b77939','roof':'#727e83','pv':'#233d50','glass':'#85c6d5','trim':'#e3e5e1','panel':'#d0d7d8','stucco':'#e6e3dc','wood':'#b99b77','slab':'#bbbdbb'}
# Far-to-near object ordering in orthographic west view (camera at negative X).
ordered=sorted(loaded['objects'],key=lambda o:np.mean(o['mesh'].vertices_attributes('xyz'),axis=0)[0],reverse=True)
fig,ax=plt.subplots(figsize=(14,10));fig.patch.set_facecolor('#fbfbf8');ax.set_facecolor('#fbfbf8')
registry={}
for o in ordered:
 vs,fs=o['mesh'].to_vertices_and_faces();vs=np.array(vs)
 triangles=[np.column_stack([-vs[f,1],vs[f,2]]) for f in fs]
 coll=PolyCollection(triangles,facecolors=colors.get(o['material'],'#aab6ba'),edgecolors='none',linewidths=0,zorder=2)
 coll.set_gid(o['id']);ax.add_collection(coll)
 registry[o['id']]={k:v for k,v in o.items() if k!='mesh'}
 registry[o['id']]['bounds_in']={'min':vs.min(0).tolist(),'max':vs.max(0).tolist()}
ax.set_aspect('equal');ax.set_xlim(-325,125);ax.set_ylim(-22,290)
ax.set_xlabel('Plan Y coordinate / inches — north ← → south',labelpad=12)
ys=[-64,0,69.75,185,249,261];ax.set_xticks([-y for y in ys],[str(y) for y in ys]);ax.set_ylabel('Height above study floor / inches')
ax.set_yticks([0,98.5,107.25,150,200,235.25,253.25],['0','98.5','107.25','150','200','235.25','253.25']);ax.grid(alpha=.12,zorder=0)
ax.spines[['top','right']].set_visible(False)
ax.axhline(0,color='#677078',lw=.8,zorder=1)
fig.suptitle('WEST ELEVATION · VERTICAL CLERESTORY STUDY',x=.07,ha='left',fontsize=18,weight='bold')
fig.text(.07,.918,'Looking east  |  North left · South right  |  Draft geometry · Not to scale',fontsize=10,color='#4c6069')
def bounds(group):
 a=np.array([v for o in objects if o['group']==group for v in o['mesh'].vertices_attributes('xyz')]);return a.min(0),a.max(0)
lo,hi=bounds('Clerestory');front=(lo[1]+hi[1])/2
callouts=[('1','Hip cap + 4 in fascia',(-160,247),(-290,276)),('2','Vertical glazing',(-front,(lo[2]+hi[2])/2),(35,262)),('3','Solar slope',(0,164),(85,207)),('4','West upper wall',(-140,176),(-292,190)),('5','Upper west bracing',(-214,149),(-296,145)),('6','Extension wall W3–W4',(-220,45),(-296,40)),('7','West frame',(-10,99),(84,77))]
for n,label,pt,txt in callouts:
 ann=ax.annotate(n+'  '+label,xy=pt,xytext=txt,fontsize=9,ha='center',va='center',color='#213c4a',bbox=dict(boxstyle='round,pad=.4',fc='white',ec='#afbcc1'),arrowprops=dict(arrowstyle='-',color='#6b858f',lw=.8),zorder=20)
 ann.set_gid('callout-'+n)
ax.annotate('',xy=(-261,-11),xytext=(-249,-11),arrowprops=dict(arrowstyle='|-|',color='#213c4a'),zorder=25)
ax.text(-270,-17,'12 in north of existing wall',ha='left',fontsize=8,color='#213c4a')
fig.text(.07,.035,'Linked to the selected study cad-mesh.json through COMPAS meshes. Same geometry as CAD and Blender.\nHistorical framing is context; elevations and connection details remain provisional. Reference numbers are for discussion.',fontsize=9,color='#52636b')
fig.subplots_adjust(left=.09,right=.97,bottom=.13,top=.88)
for ext in ['png','svg','pdf']:fig.savefig(OUT/('west-elevation.'+ext),dpi=160)
plt.close(fig)
(OUT/'element-register.json').write_text(json.dumps(registry,indent=2))
svg=(OUT/'west-elevation.svg').read_text();svg=svg[svg.index('<svg'):]
html='''<!doctype html><html><head><meta charset="utf-8"><title>West elevation · clerestory study</title><style>body{margin:0;background:#fbfbf8;color:#213c4a;font:16px system-ui}header{padding:16px 24px;border-bottom:1px solid #ccd6d9}button{padding:7px 12px;margin-left:14px;cursor:pointer}main{max-width:1350px;margin:auto}svg{width:100%;height:auto}#selected{padding:12px 24px;background:#e9eff0;position:sticky;top:0;z-index:2}g[data-member]{cursor:pointer}g[data-member]:hover path{stroke:#cf7429;stroke-width:.8}g.chosen path{stroke:#d66315;stroke-width:1.2}footer{padding:12px 24px;font-size:13px}a{color:#225d78}</style></head><body><header><strong>West elevation</strong> · Click a part to identify it; use its reference when commenting.<button id="labels">Hide numbered labels</button></header><div id="selected">Select a part, or refer to labels 1–7.</div><main>'''+svg+'''</main><footer><a href="west-elevation.pdf">PDF</a> · <a href="west-elevation.compas.json">COMPAS model</a> · <a href="element-register.json">Element register</a><p>Source SHA256: '''+bundle['source_sha256']+'''</p></footer><script>const members='''+json.dumps(registry).replace('</',r'<\/')+''';for(const [id,m] of Object.entries(members)){const el=document.getElementById(id);if(!el)continue;el.dataset.member=id;el.addEventListener('click',()=>{document.querySelectorAll('.chosen').forEach(x=>x.classList.remove('chosen'));el.classList.add('chosen');document.getElementById('selected').textContent=id+' — '+m.name+' · '+m.group;});}let shown=true;document.getElementById('labels').onclick=()=>{shown=!shown;document.querySelectorAll('[id^="callout-"]').forEach(x=>x.style.display=shown?'':'none');document.getElementById('labels').textContent=shown?'Hide numbered labels':'Show numbered labels';};</script></body></html>'''
(OUT/'west-elevation.html').write_text(html)
(OUT/'README.md').write_text('''# Linked west elevation

Open west-elevation.html to inspect and select named parts; PNG/PDF/SVG are fixed views.
North is left, south right; projection looks east. Units inches; not to scale.

Source of geometry is ../cad-mesh.json, exported by the clerestory CAD generator and
also consumed by Blender. compas-study/west_elevation.py imports it into COMPAS,
round-trips the meshes, and generates these views and the element register. It does
not redraw or independently change building geometry. Run the CAD generator first
when design geometry changes, then rerun this script. A source checksum records the
exact input. This is a mesh projection with object depth ordering, not CAD hidden-line
removal; close overlapping members should be checked in the native model.

Numbered labels 1–7 provide stable discussion topics. W-number selection references
identify objects in this generated revision; their names are retained across rebuilds.
''')
print(json.dumps({'mesh_count':len(objects),'source_sha256':bundle['source_sha256'],'view':'west','outputs':str(OUT)}))
