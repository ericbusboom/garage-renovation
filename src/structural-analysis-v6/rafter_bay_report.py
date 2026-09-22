import json
from dataclasses import fields
import rafter_bay_revision as B
import solid_view as SV
f,s,g=B.build();out=B.OUT
d=json.loads((out/'rafter-bay-revision.json').read_text())
r=B.W.D.T.A.Result(**{k:d[k] for k in {x.name for x in fields(B.W.D.T.A.Result)} if k in d and k!='members'})
r.members={m:B.W.D.T.A.MemberOutcome(**v) for m,v in d['members'].items()}
assert d['stable'],d['message']
drift=min(v['ratio'] for v in d['drift'].values() if v['ratio'])
worst=''.join(f'<tr><td>{v["member"]}</td><td>{v["section"]}</td><td>{v["dcr"]:.3f}</td><td>{v["mode"]}</td></tr>' for v in d['worst'][:10])
report=f'''<style>body{{font-family:system-ui;margin:16px;color:#222}}#frameplot{{height:76vh!important;min-height:480px}}.notes{{max-width:1080px;line-height:1.55;margin:24px auto}}td,th{{padding:8px;border-bottom:1px solid #ddd;text-align:left}}table{{width:100%;border-collapse:collapse}}</style><section class="notes"><h2>Corrected solar rafters + RF bay bracing</h2><p>The single HSS5×5×¼ roof diagonal is removed. Twelve HSS2×2×⅛ diagonals zigzag within the RF bays, between the cross-beam lines at y=71, 185 and 268 inches. Each diagonal connects to a rafter/end-frame joint, with no unsupported crossing connection. Their combined modeled weight is {g['brace_weight_lb']:.0f} lb versus 383 lb for the previous long diagonal.</p><p>Every RS solar rafter starts at a B-SO bearing connection, passes over the top flange of R-W1 at an actual intermediate support, and ends at the clerestory plane y=71 inches. The previous B-SO centerline links are retained and their elevations corrected; new R-W1 support links are included in the analysis. The solar rafter centerlines are straight and coplanar.</p><table><tr><th>Geometry</th><th>Revised value</th></tr><tr><td>Solar slope</td><td>{g['angle_deg']:.2f}°</td></tr><tr><td>RS centerline at B-SO</td><td>{g['solar_eave_center_z']:.2f} in.</td></tr><tr><td>RS centerline above R-W1</td><td>{g['solar_RW1_center_z']:.2f} in.</td></tr><tr><td>Clerestory lower centerline</td><td>{g['clerestory_bottom_z']:.2f} in.</td></tr><tr><td>Clerestory upper centerline</td><td>233.25 in.</td></tr><tr><td>Clerestory centerline height</td><td>{g['clerestory_axis_height']:.2f} in. (was 35.64 in.)</td></tr></table><p>These are member-centerline dimensions, not clear glazing dimensions. The side slope members and their post joints follow the revised solar line. W1/W2 remain absent below BW and retained above; upper S3 and both steel door posts remain.</p><h2>Current analysis: {'passes preliminary screen' if d['passes'] else 'does not pass preliminary screen'}</h2><p>Maximum checked member ratio <b>{d['max_dcr']:.3f}</b>; worst top-roof drift <b>H/{drift:.0f}</b> versus H/400; {len(d['deflection_violations'])} span-deflection failures. All colors and hover results come from this corrected geometry. The inherited 27 strength and 8 service combinations, 100 psf loft load and 96 mph Exposure C wind remain.</p><table><tr><th>Member</th><th>Section</th><th>Ratio</th><th>Check</th></tr>{worst}</table><p>Sloped rafter seats, welds, local flange/web checks and cap plates remain to be detailed. Analytical offset links represent those connections; they are not fabricated details. The larger 3-inch side slope members retain edge/post connections and need separate fit-up details. The bay diagonals are pin-ended; their full lengths govern buckling and existing member unbraced-length assumptions are not shortened simply by adding mesh nodes. Current drift reporting checks the top roof, not every local clerestory displacement.</p><p>Preliminary study only: connection, foundation and anchorage design, full stability and cladding/serviceability review remain outstanding. <a href="https://www.aisc.org/architecture-center/resources/engineering-basics/loads/">Lateral load-path basis</a>.</p></section>'''
SV.EX.THICK['south']=5
orig=SV._member_mesh
def mesh(a,b,sec):
    if sec.name=='HSS6X2X1/4':b=(b[0],b[1],106.5)
    return orig(a,b,sec)
SV._member_mesh=mesh
summary=dict(removal={},frame_model='Corrected solar support geometry + RF bay bracing · CURRENT PRELIMINARY ANALYSIS',live_case='L100',exposure='C',basis=dict(loft_live={'L100':100},wind={'V':96}))
p=out/'rafter-bay-revision-3d-solid.html'
SV.write(f,r,{},dict(sections={}),[],summary,p,cabinets=True,report_html=report)
h=p.read_text().replace('Garage frame &mdash; members at true section size','Solar rafters connected + bracing between RF rafters')
h=h.replace('How hard it is working','How hard is it working?').replace('What governs it"','What governs it?"')
h=h.replace('</body>',"<script>Plotly.relayout('frameplot',{'scene.camera.eye':{x:-1.6,y:-1.5,z:1.4}}).then(()=>Plotly.Plots.resize('frameplot'));</script></body>")
p.write_text(h);print(p)
