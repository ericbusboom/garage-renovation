"""Publish reduced roof bracing with current results, preserving viewer controls."""
import json
from dataclasses import fields
import trim_roof_bracing as T
import solid_view as SV
out=T.OUT
selection=json.loads((out/'selected.json').read_text())
keep=selection['keep'];tag=selection['tag']
f,s,g=T.build(keep)
d=json.loads((out/(tag+'.json')).read_text())
r=T.B.W.D.T.A.Result(**{k:d[k] for k in {x.name for x in fields(T.B.W.D.T.A.Result)} if k in d and k!='members'})
r.members={m:T.B.W.D.T.A.MemberOutcome(**v) for m,v in d['members'].items()}
base=json.loads((T.B.OUT/'rafter-bay-revision.json').read_text())
drift=min(v['ratio'] for v in d['drift'].values() if v['ratio'])
rows=[]
for label,a in [('12 roof-bay braces',base),(f'{len(keep)} roof-bay braces',d)]:
 dr=min(v['ratio'] for v in a['drift'].values() if v['ratio'])
 rows.append(f'<tr><td>{label}</td><td>{a["max_dcr"]:.3f}</td><td>H/{dr:.0f}</td><td>{len(a["deflection_violations"])}</td><td>{"Passes" if a["passes"] else "Fails"}</td></tr>')
convergence=''
if not keep:
 refined=json.loads((out/'no-roof-bay-braces-mesh6.json').read_text())
 convergence=f'<p>South-brace force recovery was checked with 12- and 6-inch analysis segments, retaining full physical buckling lengths and endpoint pins. The finer run gives maximum ratio {refined["max_dcr"]:.3f}; the two runs agree to within {abs(d["max_dcr"]-refined["max_dcr"]):.4f}. The initial coarse-member diagnostic is retained separately.</p>'
report=f'''<style>body{{font-family:system-ui;margin:16px;color:#222}}#frameplot{{height:76vh!important;min-height:480px}}.notes{{max-width:1080px;line-height:1.55;margin:24px auto}}td,th{{padding:8px;border-bottom:1px solid #ddd;text-align:left}}table{{width:100%;border-collapse:collapse}}</style><section class="notes"><h2>Roof-bracing reduction: {len(keep)} added bay braces remain</h2><p>{'All twelve RF bay diagonals are removed. No further added roof braces remain to delete.' if not keep else 'Remaining braces: '+', '.join(keep)} The former long roof diagonal is also absent. Existing wall/vertical braces remain. Solar rafter connections to B-SO and R-W1, the revised clerestory, steel door posts and upper W1/W2/S3 remain unchanged. W1/W2/S3 are absent below their loft beam lines.</p><table><tr><th>Configuration</th><th>Maximum checked ratio</th><th>Worst top-roof drift</th><th>Span-deflection failures</th><th>Preliminary screen</th></tr>{''.join(rows)}</table><p>Current colors and hover values use this reduced-bracing model. The drift criterion is H/400. The corrected solar supports are included; the earlier uncorrected-roof study does not establish how many braces this frame needs.</p>{convergence}<h2>Retained solar geometry</h2><p>Solar slope {g['angle_deg']:.2f}°. Rafters start at B-SO, pass over supported R-W1 seats, and meet the clerestory plane. Clerestory centerline height {g['clerestory_axis_height']:.2f} inches; clear glazing height is smaller. The new door posts remain HSS6×2×¼.</p><p><b>Preliminary screening only.</b> Removing all added roof diagonals does not establish that roof sheathing, local member restraint or construction bracing can be omitted. Connections, bearing seats, anchors, foundations, local clerestory movement and complete stability requirements still need design. No added sheathing diaphragm stiffness was assumed. The study retains its existing unbraced-length and rigid-joint assumptions, 27 strength and 8 service combinations, 100 psf loft live load and 96 mph Exposure C wind.</p></section>'''
SV.EX.THICK['south']=5
orig=SV._member_mesh
def mesh(a,b,sec):
 if sec.name=='HSS6X2X1/4':b=(b[0],b[1],106.5)
 return orig(a,b,sec)
SV._member_mesh=mesh
summary=dict(removal={},frame_model='Corrected solar rafters · reduced roof bracing · CURRENT PRELIMINARY ANALYSIS',live_case='L100',exposure='C',basis=dict(loft_live={'L100':100},wind={'V':96}))
p=out/'reduced-roof-bracing-3d-solid.html'
SV.write(f,r,{},dict(sections={}),[],summary,p,cabinets=True,report_html=report)
h=p.read_text().replace('Garage frame &mdash; members at true section size',f'Corrected solar rafters — {len(keep)} added roof braces')
h=h.replace('How hard it is working','How hard is it working?').replace('What governs it"','What governs it?"')
h=h.replace('</body>',"<script>Plotly.relayout('frameplot',{'scene.camera.eye':{x:-1.6,y:-1.5,z:1.4}}).then(()=>Plotly.Plots.resize('frameplot'));</script></body>")
p.write_text(h)
(out/'reduced-geometry.json').write_text(json.dumps(dict(kept_roof_braces=keep,nodes=f.nodes,segments=f.segments,links=f.links,sections={m:v.name for m,v in f.section_of.items()}),indent=2))
print(p)
