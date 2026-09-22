import json
from dataclasses import fields
import roof_drift_brace as R
import solid_view as SV

f,s=R.build();out=R.W.OUT
p=out/'both-removed-roof-diagonal.json'
d=json.loads(p.read_text())
r=R.W.D.T.A.Result(**{k:d[k] for k in {x.name for x in fields(R.W.D.T.A.Result)} if k in d and k!='members'})
r.members={m:R.W.D.T.A.MemberOutcome(**v) for m,v in d['members'].items()}
base=json.loads((out/'w1-w2-lower-removed.json').read_text())
rows=[]
for c,v in d['drift'].items():
    rows.append(f'<tr><td>{c}</td><td>{base["drift"][c]["drift_in"]:.4f} in.</td><td>{v["drift_in"]:.4f} in.</td><td>H/{v["ratio"]:.0f}</td></tr>')
brace=d['members']['BR-ROOF-D1']
report=f'''<style>body{{font-family:system-ui;margin:16px}}#frameplot{{height:76vh!important;min-height:480px}}.notes{{max-width:1050px;line-height:1.55;margin:24px auto}}td,th{{padding:8px;border-bottom:1px solid #ddd;text-align:left}}table{{border-collapse:collapse;width:100%}}</style><section class="notes"><h2>Trial: one diagonal in the upper roof plane</h2><p>BR-ROOF-D1 runs from the southwest upper-roof corner (−34, 71, 233.25 inches) to the northeast corner (211.5, 268, 233.25 inches). Trial section: HSS5×5×¼, {brace['length']:.1f} inches long. This is a tested trial section, not a minimum-size optimization. The lower W1/W2 segments remain removed; all their upper segments remain. No new ground-floor obstruction or vertical wall brace is added.</p><p><b>{'Passes' if d['passes'] else 'Fails'} the preliminary screen.</b> Maximum member demand/capacity {d['max_dcr']:.3f}; roof diagonal {brace['dcr']:.3f}; span-deflection failures {len(d['deflection_violations'])}.</p><table><tr><th>Wind case</th><th>Without roof diagonal</th><th>With roof diagonal</th><th>New drift ratio</th></tr>{''.join(rows)}</table><p>The reported drift is the horizontal resultant at nodes near the top roof, checked against H/400. It is not a complete story-drift or cladding check. The unbraced trial also showed larger local movement at lower clerestory members; that needs separate serviceability review.</p><p>Brace ends are pinned and its full length is used for compression buckling. Its numerical segments do not earn extra bracing credit. No crossing/rafter restraint is assumed. Connection eccentricity, attachment plates, roof clearance, load collectors, foundations and anchorage remain undesigned. Existing post, moment-joint and load-basis assumptions remain. No roof sheathing diaphragm stiffness was added.</p><p>Increasing existing lower west, lower north and upper north brace sections individually did not resolve the original drift. Roof bracing targets the load transfer between the roof and those frames. <a href="https://www.aisc.org/architecture-center/resources/engineering-basics/loads/">AISC explanation of the lateral load path</a>.</p></section>'''
SV.EX.THICK['south']=5
original=SV._member_mesh
def mesh(a,b,sec):
    if sec.name=='HSS6X2X1/4':b=(b[0],b[1],106.5)
    return original(a,b,sec)
SV._member_mesh=mesh
summary=dict(removal={},frame_model='Both lower west columns removed + one upper-roof diagonal · PRELIMINARY',live_case='L100',exposure='C',basis=dict(loft_live={'L100':100},wind={'V':96}))
path=out/'both-removed-roof-diagonal-3d-solid.html'
SV.write(f,r,{},dict(sections={}),[],summary,path,cabinets=True,report_html=report)
h=path.read_text().replace('Garage frame &mdash; members at true section size','W1/W2 below BW removed + upper-roof diagonal')
h=h.replace('How hard it is working','How hard is it working?').replace('What governs it"','What governs it?"')
h=h.replace('</body>',"<script>Plotly.relayout('frameplot',{'scene.camera.eye':{x:-1.6,y:-1.5,z:1.5}}).then(()=>Plotly.Plots.resize('frameplot'));</script></body>")
path.write_text(h)
(out/'both-removed-roof-diagonal-geometry.json').write_text(json.dumps(dict(nodes=f.nodes,segments=f.segments,sections={m:v.name for m,v in f.section_of.items()},unbraced_length_overrides=f.unbraced_length_overrides),indent=2))
print(path)
