"""Compare lower W1/W2 removals without replacing the accepted door-post view."""
import json
from dataclasses import fields
import west_lower_removal as W
import solid_view as SV

out=W.OUT
original_mesh=SV._member_mesh
def physical_mesh(a,b,sec):
    if sec.name=='HSS6X2X1/4':b=(b[0],b[1],106.5)
    return original_mesh(a,b,sec)
SV._member_mesh=physical_mesh
cases=[('door-posts-1-4-pdelta-mesh12','Keep W1 and W2',W.D.OUT),('w1-lower-removed','Remove lower W1',out),('w2-lower-removed','Remove lower W2',out),('w1-w2-lower-removed','Remove both below BW',out)]
if (out/'w1-w2-lower-removed-west-stiff.json').exists():
    cases.append(('w1-w2-lower-removed-west-stiff','Remove both + thicker west brace',out))
if (out/'w1-w2-lower-removed-north-stiff.json').exists():
    cases.append(('w1-w2-lower-removed-north-stiff','Remove both + larger north brace',out))
rows=[]
for tag,label,folder in cases:
    d=json.loads((folder/(tag+'.json')).read_text())
    dr=min((v['ratio'] for v in d['drift'].values() if v['ratio']),default=0)
    worst=d['worst'][0]['member'] if d['worst'] else 'No stable solution'
    rows.append(f'<tr><td>{label}</td><td>{d["max_dcr"]:.3f}</td><td>{worst}</td><td>H/{dr:.0f}</td><td>{len(d["deflection_violations"])}</td><td>{"Passes screen" if d["passes"] else "Fails screen"}</td></tr>')
variants=[('W1',False,False),('W2',False,False),('W1+W2',False,False)]
if (out/'w1-w2-lower-removed-west-stiff.json').exists():variants.append(('W1+W2',True,False))
if (out/'w1-w2-lower-removed-north-stiff.json').exists():variants.append(('W1+W2',False,True))
for which,stiff,north in variants:
    f,s,cuts=W.build(which,stiff,north)
    tag=which.lower().replace('+','-')+'-lower-removed'+('-west-stiff' if stiff else '-north-stiff' if north else '')
    d=json.loads((out/(tag+'.json')).read_text())
    if not d['stable']:continue
    r=W.D.T.A.Result(**{k:d[k] for k in {x.name for x in fields(W.D.T.A.Result)} if k in d and k!='members'})
    r.members={m:W.D.T.A.MemberOutcome(**v) for m,v in d['members'].items()}
    top=''.join(f'<tr><td>{v["member"]}</td><td>{v["section"]}</td><td>{v["dcr"]:.3f}</td><td>{v["mode"]}</td></tr>' for v in d['worst'][:8])
    collateral=[m for c in cuts.values() for m in c['collateral']]
    report=f'''<style>body{{font-family:system-ui;margin:16px;color:#222}}#frameplot{{height:76vh!important;min-height:480px}}.notes{{max-width:1080px;line-height:1.55;margin:24px auto}}table{{border-collapse:collapse;width:100%}}td,th{{padding:8px;text-align:left;border-bottom:1px solid #ddd}}</style><section class="notes"><h2>{which}: remove below BW only</h2><p>{'Existing BR-W-2 upgraded from HSS3×3×3⁄16 to HSS3×3×¼; same position, no additional brace.' if stiff else 'Existing BR-N-1 upgraded from HSS2½×2½×⅛ to HSS3×3×⅛; same position, no additional brace.' if north else 'No section changes beyond the configured door-post frame.'}</p><p>BW is the west loft beam at z = 112.5 inches. All W1/W2 segments above that elevation remain unchanged. The lower segments and their base supports are absent from the analysis. Additional members removed because their base anchor was lost: {', '.join(collateral) if collateral else 'none'}. The two HSS 6×2×¼ door posts, retained upper S3, wall-aligned B-S and R-W1, and previous reinforcement remain.</p><p><b>{'Passes the preliminary screen' if d['passes'] else 'Does not pass the preliminary screen'}.</b> These are current results for this removal option, not colors carried over from the starting frame.</p><table><tr><th>Option</th><th>Max ratio</th><th>Controlling member</th><th>Drift</th><th>Deflection failures</th><th>Result</th></tr>{''.join(rows)}</table><h2>Highest checked demands</h2><table><tr><th>Member</th><th>Section</th><th>Ratio</th><th>Check</th></tr>{top}</table><p>Same inherited 27 strength and 8 service load combinations, 100 psf loft live load, 96 mph Exposure C wind, and second-order analysis as the configured door-post study. The 12-inch refinement of BR-N-1 and RS @ 170.58 and the conservative unbraced-length overrides are retained. New section or stability failures require follow-up; a failed result is not a removal recommendation.</p><p>Preliminary comparison only. Connections, column-to-beam load transfer, foundations, anchorage and removal sequence are not designed. The simplified member checks, assumed bracing and inherited load basis remain limitations. <a href="../wall-aligned-door-posts-3d-solid.html">Return to the accepted door-post frame</a>.</p></section>'''
    summary=dict(removal={},frame_model=which+' below BW removed · CURRENT OPTION ANALYSIS',live_case='L100',exposure='C',basis=dict(loft_live={'L100':100},wind={'V':96}))
    SV.EX.THICK['south']=5
    path=out/(tag+'-3d-solid.html')
    SV.write(f,r,{},dict(sections={}),[],summary,path,cabinets=True,report_html=report)
    h=path.read_text().replace('Garage frame &mdash; members at true section size',which+' removed below BW — upper portions retained')
    h=h.replace('How hard it is working','How hard is it working?').replace('What governs it"','What governs it?"')
    h=h.replace('</body>',"<script>Plotly.relayout('frameplot',{'scene.camera.eye':{x:-1.8,y:-1.5,z:0.8}}).then(()=>Plotly.Plots.resize('frameplot'));</script></body>")
    path.write_text(h)
    (out/(tag+'-geometry.json')).write_text(json.dumps(dict(cuts=cuts,nodes=f.nodes,segments=f.segments,sections={m:v.name for m,v in f.section_of.items()},west_brace_upgraded=stiff,north_brace_upgraded=north),indent=2))
    print(path)
