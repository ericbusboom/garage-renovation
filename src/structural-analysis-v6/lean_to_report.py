"""Current analysis-colored viewer for the steel lean-to rafter option."""
import json,math
from dataclasses import fields
import lean_to_rafters as L
import solid_view as SV
import phasing
import owner_revisions as OR
import cost
import frame as F
import moment_frames as MF
import connections as CN
f,s,g=L.build()
stage=phasing.before_demo(f,defer=set(OR.DEFER_BEFORE_DEMO),
                          include=set(OR.BUILD_BEFORE_DEMO))
d=json.loads((L.OUT/'analysis.json').read_text())
r=L.T.A.Result(**{k:d[k] for k in {x.name for x in fields(L.T.A.Result)} if k in d and k!='members'})
r.members={m:L.T.A.MemberOutcome(**v) for m,v in d['members'].items()}
dr=min(v['ratio'] for v in d['drift'].values() if v['ratio'])
worst=max((r.members[m] for m in g['rafters']),key=lambda m:m.dcr)
pin_groups={group:[m for m in f.members if f.group(m)==group]
            for group in sorted(F.PIN_ENDED_GROUPS)}
pin_members=sum(len(v) for v in pin_groups.values())
quantities=cost.measure(f)
moment_audit=MF.audit(f)
joints=CN.schedule(f,g['connections_added'])
joint_counts={k:sum(r['kind']==k for r in joints) for k in CN.KINDS}
joins=g['connections_added']
join_list='; '.join(f"{' × '.join(j['members'])} ({j['kind']})" for j in joins)
rows=''.join(f'<tr><td>{m}</td><td>{r.members[m].section}</td><td>{r.members[m].dcr:.3f}</td><td>{r.members[m].combo}</td></tr>' for m in ['BE.upper','BE','E.clerestory','E.W3',worst.member])
report=f'''<style>body{{font-family:system-ui;margin:16px;color:#222}}#frameplot{{height:76vh!important;min-height:480px}}.notes{{max-width:1080px;line-height:1.55;margin:24px auto}}td,th{{padding:8px;border-bottom:1px solid #ddd;text-align:left}}table{{border-collapse:collapse;width:100%}}</style>
<section class="notes"><h2>Lean-to rafters — steel-supported fit</h2>
<p><b>12 HSS2×2×⅛ steel rafters</b> at {g['spacing']:.3f} in. centers, running from the smaller BE.upper down to the outer BE beam. Top-edge horizontal span {g['horizontal_run']:.2f} in.; top-edge length about {g['cuts'][worst.member]['top_length']:.1f} in.; pitch about {g['cuts'][worst.member]['angle_deg']:.1f} degrees. The first and last rafters sit half a bay in from the roof ends, leaving room around the posts. Roof coverage y=2.5–268 in.; no extension south of BE.upper is assumed.</p>
<p>The top edge runs directly from the top/east corner of BE.upper to the top/east corner of the lower BE flange. The upper end has a vertical bevel cut, flush with the higher beam’s east flange edge. The lower end has a horizontal bevel cut, sitting on the lower beam’s top flange and ending at its outer east edge. Both cuts are drawn in the solid geometry; raised brackets have been removed. The new rafters use current analysis colors.</p>
<p><b>Changed load path:</b> both ends now bear on steel. The old assumed existing-wall bearing at z=98.5 in. would conflict with the retained outer beam; this option raises the low bearing to BE instead. Previous separate wood-roof reaction loads have been removed and replaced by actual rafter self weight, roof dead/live load and the inherited canopy wind cases. The full lean-to load now reaches the frame; none is assigned to the existing wall.</p>
<h2>{'Passes' if d['passes'] else 'Does not pass'} the preliminary frame screen</h2>
<p>Maximum checked ratio <b>{d['max_dcr']:.3f}</b>; worst top-roof drift <b>H/{dr:.0f}</b>; {len(d['deflection_violations'])} span-deflection violations. Worst new rafter ratio <b>{worst.dcr:.3f}</b>. Analysis uses corrected end releases and second-order effects. Rafter ends release bending; cut-face offsets transfer forces to the supporting beam axes. Existing beam buckling lengths are retained.</p>
<table><tr><th>Member</th><th>Section</th><th>Checked ratio</th><th>Governing combination</th></tr>{rows}</table>
<p>Continuous HSS5×5×¼ east posts, BE.upper W6×8.5, E.top HSS4×4×¼ and BE W14×22 remain. Lower W1/W2/S3 remain removed; no added roof-bay braces. Corrected solar rafters, steel door posts, existing information controls and cabinets remain.</p>
<h2>Connection assumptions in this model</h2>
<p><b>{pin_members} members are pin-ended:</b> {len(pin_groups['Bracing'])} braces, {len(pin_groups['Joists'])} wood joists and {len(pin_groups['Rafters'])} rafters. That creates {2*pin_members} released member ends. There are also <b>{len(f.pinned_ends)} explicitly declared pin locations</b>—the two steel door-post heads, four simple-support locations along BE.upper and the brace hinges at the new crossing joints—and <b>{len(f.supports)} pinned bases</b>. The remaining modeled joints transfer moment unless an end release says otherwise.</p>
<h2>Connections</h2>
<p>Tick <b>Connections</b> above the model to put a dot on every one of the <b>{len(joints)} physical joints</b>, coloured by the connection the analysis assumes: <b style="color:{CN.KINDS['welded'][0]}">{joint_counts['welded']} welded</b> (every attaching end moment-continuous), <b style="color:{CN.KINDS['mixed'][0]}">{joint_counts['mixed']} welded joints with pinned attachments</b> (for example a welded beam-column joint receiving a bolted brace), <b style="color:{CN.KINDS['pinned'][0]}">{joint_counts['pinned']} pinned</b> (bolted gussets, rafter seats, joist hangers) and <b>{joint_counts['base']} pinned bases</b>. The members dim while the dots are on; hover a dot to see which member ends meet there and which are released.</p>
<p><b>Connection audit.</b> Every member end was checked against the solid of every other member. Where an end touched another member, or two members passed through each other, with no joint in the model, a joint was added: {join_list}. The south brace BR-S-2 ran straight through the B-SO web and now connects to it with a pinned gusset; the S1 column top, the BR-S-2 head and the RS @ 170.58 solar-rafter seat now form one joint; both X-brace pairs are bolted at their crossings. The brace is released at each new joint, and the crossing nodes are not credited as brace points in the member checks. After re-running the analysis the maximum ratio is {d['max_dcr']:.3f} (0.896 before); RS @ 170.58 went from 0.558 to {r.members['RS @ 170.58'].dcr:.3f} because it now shares the S1 column head. “Welded” means moment-continuous in the solver, not a designed weld.</p>
<p><b>No actual fastener schedule exists.</b> The cost model counts {quantities.steel_joints} fitted steel ends and carries a budgeting allowance for about {round(quantities.steel_joints/2)} field-bolted connection locations, plus shop fitting/welding and end plates on {quantities.beams} W-shape pieces. Those are cost placeholders, not bolt counts, screw counts, weld sizes or approved joint details. The {len(f.links)} short analytical links transfer loads across bearing offsets; they do not prove that the physical connection is welded or moment-resisting.</p>
<p><b>Moment-frame designation:</b> the new “What are the moment frames?” view marks two intentional ground-to-floor longitudinal frames in red: the west <b>BW</b> line (BW with SW0/W1/W2/W3/W4) and the east <b>BE</b> line (BE with E-S2/E-S3/E-N2). Green members are diagonal bracing; blue members are deliberately simple/pinned. The <b>{moment_audit['counts']['unassigned']} amber members</b> are the important warning: the solver currently transfers moment through them, but they have not been assigned to a deliberate moment frame. The upper roof and clerestory are still largely in this category and must be released or formally added to the lateral system before connection detailing.</p>
<table><tr><th style="color:#c83e4d">Red</th><td>designated moment-frame member</td><th style="color:#6b8e23">Green</th><td>braced-frame member</td></tr><tr><th style="color:#377eb8">Blue</th><td>simple or pin-ended</td><th style="color:#d89028">Amber</th><td>rigid in solver; lateral role unresolved</td></tr></table>
<p><b>Pre-demo:</b> the restored control shows {len(stage['build'])} members that clear the existing roof or can be erected with localized eave work and have a supported first-stage load path. It hides {len(stage['wait'])} members that wait for roof demolition. {len(stage['penetrating'])} early members need limited eave penetrations or trimming; temporary erection stability still needs its own bracing plan.</p>
<p>Proposed fit and preliminary screening, not a construction design. Connection plates, bolts, welds, local HSS/flange strength, uplift attachment and foundations remain unsized. The inherited steep-canopy wind approximation needs project-specific verification; cladding edge overhangs and attachment are also not checked. The rafter top is about 50 in. above the loft beam axis at the high end and 7 in. at the low end, so this covers the side strip rather than usable standing-height loft space. Simple connections must accommodate the modeled rotation: <a href="https://www.aisc.org/aisc/solutions-center/engineering-faqs/5-connections/">AISC connection guidance</a>.</p></section>'''
SV.EX.THICK['south']=5
original=SV._member_mesh
cut_meshes={}
for member,cut in g['cuts'].items():
    _,i,j=next(v for v in f.segments if v[0]==member)
    vertices=[[x,cut['y']+dy,z] for dy in [-1,1] for x,z in cut['polygon']]
    faces=[(0,1,2),(0,2,3),(4,6,5),(4,7,6)]
    for k in range(4):
        n=(k+1)%4
        faces.extend([(k,n,n+4),(k,n+4,k+4)])
    cut_meshes[(f.xyz(i),f.xyz(j))]=(vertices,faces)
def mesh(a,b,sec):
    if (tuple(a),tuple(b)) in cut_meshes:return cut_meshes[(tuple(a),tuple(b))]
    if sec.name=='HSS6X2X1/4':b=(b[0],b[1],106.5)
    return original(a,b,sec)
SV._member_mesh=mesh
p=L.OUT/'lean-to-frame-3d.html'
summary=dict(removal={},frame_model='Lean-to steel rafters + continuous east posts · CURRENT PRELIMINARY ANALYSIS',live_case='L100',exposure='C',basis=dict(loft_live={'L100':100},wind={'V':96}))
SV.write(f,r,{},dict(sections={}),[],summary,p,cabinets=True,report_html=report,
         proposed_seats=g['seats'],before_demo=set(stage['build']),connections=joints,
         outer_walls=True)
h=p.read_text().replace('Garage frame &mdash; members at true section size','Lean-to steel rafters + continuous east posts')
h=h.replace('How hard it is working','How hard is it working?').replace('What governs it"','What governs it?"')
h=h.replace('</body>',"<script>Plotly.relayout('frameplot',{'scene.camera.eye':{x:1.8,y:-1.5,z:1.0}}).then(()=>Plotly.Plots.resize('frameplot'));</script></body>")
h='\n'.join(line.rstrip() for line in h.splitlines())+'\n'
p.write_text(h)
print(p)
