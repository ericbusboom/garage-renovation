"""Owner's wall-aligned door-post geometry trial; deliberately no capacity results."""
import json
import re
from types import SimpleNamespace
from dataclasses import fields
import plotly.graph_objects as go
import s3_final_checks as FC
import s3_removal_study as T
import south_brace_study as SB
import solid_view as SV

OUT=T.OUT/'door-frame'
OUT.mkdir(exist_ok=True)
f,spec=FC.final_frame()
T.clean(f)
wall_y=2.5
shift=wall_y-(-6)
moved=[]
for name,node in f.nodes.items():
    if abs(node['y']+6)<.001:
        before=[node[k] for k in ('x','y','z')]
        node['y']=wall_y
        if node['z']>112.51:
            node['z']+=shift*SB.SLOPE
        moved.append(dict(node=name,before=before,after=[node[k] for k in ('x','y','z')]))
assert not any('RWBS' in m for m in f.members)
for member in ('B-S','R-W1'):
    assert all(abs(f.nodes[n]['y']-wall_y)<1e-9 for m,i,j in f.segments if m==member for n in (i,j))
assert min(f.xyz(n)[2] for m,i,j in f.segments if m=='S3' for n in(i,j))==112.5
# Literal 2 x 6 envelopes, steel selected; wall thickness not selected. Six inches
# through wall, two inches along wall; clear opening remains 32 inches.
post_top=112.5-f.section_of['B-S'].d/2
posts=[]
for label,x in [('west',110.5),('east',144.5)]:
    verts,faces=SV._box((x,wall_y,0),(x,wall_y,post_top),(0,1,0),(1,0,0),6,2)
    posts.append(go.Mesh3d(x=[v[0] for v in verts],y=[v[1] for v in verts],z=[v[2] for v in verts],i=[v[0] for v in faces],j=[v[1] for v in faces],k=[v[2] for v in faces],color='#aeb4bc',name=f'Door post — {label}',flatshading=True,showlegend=False,hovertemplate=f'<b>New {label} door post</b><br>2 × 6 in. envelope; steel HSS; wall thickness unselected<br>Top at B-S underside: {post_top:.2f} in.<br>Geometry only — capacity not checked<extra></extra>').to_plotly_json())
manifest=dict(status='Geometry only; no analysis results apply',wall_thickness_in=5,wall_center_y_in=wall_y,beam_north_shift_in=shift,roof_beam_rise_in=shift*SB.SLOPE,moved_nodes=moved,door_clear_x_in=[111.5,143.5],post_centers_x_in=[110.5,144.5],post_envelope_in=dict(along_wall=2,through_wall=6),post_top_z_in=post_top,post_material="steel",notes=['Trial RW1–BS braces absent.','Upper S3 retained; lower S3 absent.','Connected south-line nodes, including W1 and E-S3 bases, move with the beams; existing footing reuse is not established.','Door height remains survey placeholder 80 inches.','Six-inch post envelopes extend half an inch beyond each face of the five-inch wall.'],nodes=f.nodes,segments=f.segments,sections={m:v.name for m,v in f.section_of.items()})
(OUT/'wall-aligned-layout.json').write_text(json.dumps(manifest,indent=2))
report=f'''<style>body{{font-family:system-ui;margin:16px;color:#222}}#frameplot{{height:76vh!important;min-height:480px}}.notes{{max-width:1000px;line-height:1.5;margin:24px auto}}</style><section class="notes"><h2>Beams over the south wall</h2><p>Trial RW1–B-S braces removed. B-S moves {shift:g} inches north, at unchanged height. R-W1 moves {shift:g} inches north and {shift*SB.SLOPE:.2f} inches up along the existing slope. Upper S3 remains connected; lower S3 stays removed. B-SO stays in place.</p><p>Two gray posts flank the existing 32-inch door opening and rise to the underside of B-S ({post_top:.2f} inches). Shown as literal 2 × 6-inch envelopes, with the six-inch dimension through the wall. Rectangular steel HSS selected; wall thickness remains unselected. They project half an inch past each face of the five-inch wall.</p><p>Shared beam joints and connected framing follow the move, including the W1 and E-S3 column lines and base locations. These are proposed positions, not confirmation of existing footing locations. Other reinforcement from the previous brace-free option is retained.</p><p><b>Layout only.</b> The previous structural ratings do not apply to this changed geometry. Post capacity, beam bearing, connections and foundations have not been checked. Door height shown is the existing unverified 80-inch survey placeholder.</p></section>'''
summary=dict(removal={},frame_model='South wall alignment — geometry only',live_case='L100',exposure='C',basis=dict(loft_live={'L100':100},wind={'V':96}))
SV.EX.THICK['south']=5
path=OUT/'wall-aligned-door-posts-3d-solid.html'
baseline=json.loads((T.OUT/'s3-clear-floor-pdelta.json').read_text())
reference=SimpleNamespace(members={m:T.A.MemberOutcome(**v) for m,v in baseline['members'].items()})
SV.write(f,reference,{},dict(sections={}),[],summary,path,cabinets=True,report_html=report)
html=path.read_text()
html=re.sub(r'<div id="viewhead">.*?</div>','<div id="viewhead"><h1>South wall beams + two door posts</h1><p>Analysis colors and member details restored from the previous brace-free model. Reference results only: revised geometry has not been analyzed. Gray door posts: not yet checked.</p></div>',html,count=1,flags=re.S)
html=html.replace('id="cb_walls" checked','id="cb_walls"',1)
js="""<script>
(async()=>{const gd=document.getElementById('frameplot');
await Plotly.relayout(gd,{'scene.camera.eye':{x:0.5,y:-2.2,z:0.8}});
await Plotly.addTraces(gd,POST_DATA);
const menus=gd.layout.updatemenus;
for(const menu of menus) for(const button of menu.buttons) button.args[0].color.push('#aeb4bc','#aeb4bc');
await Plotly.relayout(gd,{updatemenus:menus});
applyVis();Plotly.Plots.resize(gd);
})();</script>""".replace('POST_DATA',json.dumps(posts))
html=html.replace('</body>',js+'</body>')
html=html.replace('<b>DCR ', '<b>Previous-model DCR ')
html=html.replace('How hard it is working','How hard is it working?').replace('What governs it"','What governs it?"')
assert 'How hard is it working?' in html and 'What governs it?' in html
path.write_text(html)
print(path)
print(json.dumps({k:manifest[k] for k in ('beam_north_shift_in','roof_beam_rise_in','post_top_z_in')}))
