import json,sys
from dataclasses import fields
import east_continuous_posts as E
import solid_view as SV
section=sys.argv[1] if len(sys.argv)>1 else 'W6X8.5'
simple=len(sys.argv)>2 and sys.argv[2]=='simple'
reinforced=len(sys.argv)>3 and sys.argv[3]=='reinforced'
tag=section.lower().replace('.','p').replace('/','-')+('-simple' if simple else '')+('-reinforced' if reinforced else '');out=E.OUT
f,s,g=E.build(section,simple,reinforced)
d=json.loads((out/(tag+'.json')).read_text())
r=E.T.B.W.D.T.A.Result(**{k:d[k] for k in {x.name for x in fields(E.T.B.W.D.T.A.Result)} if k in d and k!='members'})
r.members={m:E.T.B.W.D.T.A.MemberOutcome(**v) for m,v in d['members'].items()}
rows=[]
for sec,trialtag in [('Existing W14×22 frame — corrected releases','baseline-release-corrected'),('W6X8.5 simple spans + 5-inch posts','w6x8p5-simple'),('Same + E.top and BE reinforcement','w6x8p5-simple-reinforced')]:
 a=json.loads((out/(trialtag+'.json')).read_text())
 dr=min((v['ratio'] for v in a['drift'].values() if v['ratio']),default=0)
 rows.append(f'<tr><td>{sec}</td><td>{a["members"].get("BE.upper",{}).get("dcr",0):.3f}</td><td>{a["max_dcr"]:.3f}</td><td>H/{dr:.0f}</td><td>{"Passes" if a["passes"] else "Fails"}</td></tr>')
dr=min(v['ratio'] for v in d['drift'].values() if v['ratio'])
postrows=''.join(f'<tr><td>{m}</td><td>{d["members"][m]["section"]}</td><td>{d["members"][m]["dcr"]:.3f}</td></tr>' for m in ['E.clerestory','E.W3'])
report=f'''<style>body{{font-family:system-ui;margin:16px;color:#222}}#frameplot{{height:76vh!important;min-height:480px}}.notes{{max-width:1080px;line-height:1.55;margin:24px auto}}td,th{{padding:8px;border-bottom:1px solid #ddd;text-align:left}}table{{border-collapse:collapse;width:100%}}</style><section class="notes"><h2>Continuous east posts + smaller lean-to support</h2><p><b>Analysis correction:</b> end-release flags now accumulate correctly at both ends of a member. The prior frame and this option have been rerun using that correction; earlier results from the overwritten-release implementation are superseded.</p><p>E.clerestory runs from B-1 at z=112.5 in. to the top at z=236.75 in. E.W3 runs from B-2 to the same top elevation. Both are continuous {g['post_section']} posts, 124.25 in. long. The former .lower members have been merged into their full-height posts. Intermediate analysis joints represent attached beams, not post splices. The full post height is conservatively used for buckling.</p><p>BE.upper is now <b>{section}</b>, replacing W14×22. Its axis rises {g['beam_axis_raise']:.3f} in. to preserve the previous top bearing elevation, so the lean-to roof support line remains in place. The beam still carries the original lean-to dead and roof-live reactions; no load was dropped. {'BE.upper uses simple spans, with bending released at each supporting post; its axial continuity remains modeled. Post sections are increased from HSS3×3×⅛ to HSS5×5×¼. The joint details must match these assumptions.' if simple else 'The model retains rigid beam/post joints, so the beam participates in lateral framing. Those connections remain to be designed.'}</p><p>{'Additional reinforcement: E.top changes from HSS3×3×⅛ to HSS4×4×¼; the outer east loft beam BE changes from W12×16 to W14×22.' if reinforced else 'No additional E.top or BE reinforcement in this option.'}</p><p>This revises the existing east frame; the unselected mirrored-east option and its new ground-floor post were not adopted. Corrected solar rafters, the shorter clerestory, steel door posts and zero added roof-bay braces remain. Lower W1/W2/S3 remain removed.</p><h2>{'Passes' if d['passes'] else 'Fails'} the preliminary screen</h2><p>Current maximum checked ratio <b>{d['max_dcr']:.3f}</b>; worst top-roof drift <b>H/{dr:.0f}</b>; {len(d['deflection_violations'])} span-deflection violations. Current colors and hover values include these revisions.</p><table><tr><th>Lean-to beam</th><th>Beam ratio</th><th>Whole frame maximum</th><th>Drift</th><th>Screen</th></tr>{''.join(rows)}</table><table><tr><th>Continuous post</th><th>Section</th><th>Checked ratio</th></tr>{postrows}</table><p>The earlier model already used rigid joints between the two post segments. Merging the names alone does not introduce extra stiffness. The tested simple-span option additionally changes the post sections and beam-end releases as described above. Connections, beam seats, welds, foundations, local clerestory movement and complete stability checks remain outstanding. The inherited 27 strength and 8 service combinations, 100 psf loft loading and 96 mph Exposure C wind remain. Preliminary comparison, not a construction design. The simple beam connections must accommodate the modeled end rotation: <a href="https://www.aisc.org/aisc/solutions-center/engineering-faqs/5-connections/">AISC connection guidance</a>.</p></section>'''
SV.EX.THICK['south']=5
orig=SV._member_mesh
def mesh(a,b,sec):
 if sec.name=='HSS6X2X1/4':b=(b[0],b[1],106.5)
 return orig(a,b,sec)
SV._member_mesh=mesh
summary=dict(removal={},frame_model='Continuous east posts + '+section+' lean-to beam · CURRENT PRELIMINARY ANALYSIS',live_case='L100',exposure='C',basis=dict(loft_live={'L100':100},wind={'V':96}))
p=out/'continuous-east-posts-3d-solid.html'
SV.write(f,r,{},dict(sections={}),[],summary,p,cabinets=True,report_html=report)
h=p.read_text().replace('Garage frame &mdash; members at true section size','Continuous east posts + smaller lean-to beam')
h=h.replace('How hard it is working','How hard is it working?').replace('What governs it"','What governs it?"')
h=h.replace('</body>',"<script>Plotly.relayout('frameplot',{'scene.camera.eye':{x:1.6,y:-1.5,z:1.1}}).then(()=>Plotly.Plots.resize('frameplot'));</script></body>")
p.write_text(h)
(out/'selected.json').write_text(json.dumps(dict(section=section,result=tag,passes_screen=d['passes'],max_dcr=d['max_dcr'],drift=dr,**{k:v for k,v in g.items() if k!='section'}),indent=2))
print(p)
