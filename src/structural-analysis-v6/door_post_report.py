"""Publish the analyzed door-post option with the existing analysis controls."""
import json
import re
from dataclasses import fields
import door_post_study as D
import solid_view as SV
import codecheck
import loads

out=D.OUT
final_tag='door-posts-1-4-pdelta-mesh12'
d=json.loads((out/(final_tag+'.json')).read_text())
f,spec=D.build('1/4',12)
r=D.T.A.Result(**{k:d[k] for k in {x.name for x in fields(D.T.A.Result)} if k in d and k!='members'})
r.members={m:D.T.A.MemberOutcome(**v) for m,v in d['members'].items()}
assert r.stable and len(r.members)==len(f.members)
rows=[]
for tag,label in [('door-posts-1-4-linear','¼ in. wall — linear comparison'),('door-posts-3-16-pdelta-mesh24','3⁄16 in. wall — second order, 24 in. mesh'),('door-posts-1-4-pdelta-mesh24','¼ in. wall — second order, 24 in. mesh'),(final_tag,'¼ in. wall — second order, 12 in. mesh')]:
    a=json.loads((out/(tag+'.json')).read_text())
    drift=min(v['ratio'] for v in a['drift'].values() if v['ratio'])
    rows.append(f"<tr><td>{label}</td><td>{a['max_dcr']:.3f}</td><td>H/{drift:.0f}</td><td>{'Passes screen' if a['passes'] else 'Does not pass'}</td></tr>")
postrows=[]
for m,label in [('DOOR-W','West door post'),('DOOR-E','East door post')]:
    v=d['members'][m];rx=d['reactions'][m+'.base']
    postrows.append(f"<tr><td>{label}</td><td>{v['dcr']:.3f}</td><td>{rx['max_compression']/1000:.2f} kip</td><td>{rx['max_uplift']/1000:.2f} kip</td><td>{rx['max_shear']/1000:.3f} kip</td></tr>")
cap=min(codecheck.compression_capacity(f.section_of['DOOR-W'],50,112.5,a) for a in ('weak','strong'))
drift=min(v['ratio'] for v in d['drift'].values() if v['ratio'])
report=f'''<style>body{{font-family:system-ui;margin:16px;color:#222}}#frameplot{{height:76vh!important;min-height:480px}}.notes{{max-width:1080px;line-height:1.55;margin:24px auto}}td,th{{text-align:left;padding:8px;border-bottom:1px solid #ddd}}table{{border-collapse:collapse;width:100%}}</style>
<section class="notes"><h2>Configured trial: two HSS 6 × 2 × ¼ steel door posts</h2>
<p>Six-inch dimension through the wall; two-inch dimension beside the door. Outside faces preserve the 32-inch door opening. Posts end at the underside of B-S, z = 106.5 in. The analysis conservatively uses 112.5 in. to the beam centerline, unbraced for the full height. Steel follows the inherited ASTM A500 Grade C assumption, Fy = 50 ksi, with design wall thickness 0.93 × nominal.</p>
<p>B-S is over the 5-inch south wall at y = 2.5 in. R-W1 moved north 8.5 in. and up 4.91 in. Upper S3 remains; lower S3 and the trial RW1–B-S braces are absent. W1 and E-S3 base positions follow the approved wall alignment. Existing W14×22 R-W1, west-brace reinforcement and doubled shelf joist remain.</p>
<p><b>Current second-order result: maximum checked ratio {d['max_dcr']:.3f}; worst drift H/{drift:.0f} against H/400; {len(d['deflection_violations'])} span-deflection violations.</b> {len(loads.strength_combos('L100'))} strength and {len(loads.service_combos('L100'))} service combinations; inherited 100 psf loft load and 96 mph Exposure C wind. All model members now carry the current analysis colors and hover results.</p>
<h2>Door-post demands</h2><table><tr><th>Post</th><th>Governing check ratio</th><th>Max compression</th><th>Max uplift</th><th>Max base shear</th></tr>{''.join(postrows)}</table>
<p>The calculated compression resistance of each ¼-inch-wall post is {cap:.1f} kip under the study's K = 1 assumption. The displayed ratio follows the program's axial–bending interaction equation; below its 0.2 axial threshold it is half the axial utilization. Base reactions above are separate load-combination envelopes, not simultaneous forces.</p>
<h2>Thickness and numerical checks</h2><table><tr><th>Run</th><th>Maximum ratio</th><th>Drift</th><th>Screen</th></tr>{''.join(rows)}</table>
<p>¼-inch wall is the configured trial because it gives compact walls in the section checker and more connection allowance; 3⁄16 inch was also evaluated. This does not establish the minimum available or final fabricated section. A coarse second-order run produced large bending spikes in BR-N-1 and RS @ 170.58. Those two members were subdivided for the published run; their original unbraced lengths were preserved. The 24- and 12-inch mesh results above expose the numerical sensitivity. Coarse results are retained for diagnosis, not used as the selected design.</p>
<h2>Connection and foundation assumptions</h2><p>Post heads and bases are pinned for bending. No new door-post moment-frame action is credited, and the posts do not shorten the existing assumed beam torsional-bracing lengths. Bases are assumed restrained in all translations. Uplift requires an anchored load path; the existing slab has not been demonstrated to support these reactions. Head bearing/cap plates, beam web bearing or crippling, welds, base plates, anchors and foundations are not sized here. Door height remains the unverified 80-inch survey placeholder.</p>
<p><b>Preliminary screening only.</b> Small wind-drift reserve remains. The model inherits simplified steel checks and timber bending/shear checks, assumed connections and bracing, and the existing seismic/load basis. P–Delta alone is not a complete AISC direct-analysis design. The local 5-inch wall and 6-inch tube need finish/detail coordination. <a href="https://www.aisc.org/globalassets/aisc/publications/standards/a360-16-spec-and-commentary_june-2019_linked.pdf">AISC 360-16</a>; <a href="https://www.aisc.org/aisc/solutions-center/engineering-faqs/5-connections/">AISC connection guidance</a>.</p></section>'''
summary=dict(removal={},frame_model='Wall-aligned beams + steel door posts · CURRENT PRELIMINARY ANALYSIS',live_case='L100',exposure='C',basis=dict(loft_live={'L100':100},wind={'V':96}))
SV.EX.THICK['south']=5
original_mesh=SV._member_mesh
# Draw physical post to underside; FE length remains conservative to centerline.
def mesh(a,b,sec):
    if sec.name=='HSS6X2X1/4':b=(b[0],b[1],106.5)
    return original_mesh(a,b,sec)
SV._member_mesh=mesh
path=out/'wall-aligned-door-posts-3d-solid.html'
SV.write(f,r,{},dict(sections={}),[],summary,path,cabinets=True,report_html=report)
html=path.read_text().replace('Garage frame &mdash; members at true section size','South wall beams + steel door posts — analyzed')
html=html.replace('How hard it is working','How hard is it working?').replace('What governs it"','What governs it?"')
html=html.replace('id="cb_walls" checked','id="cb_walls"',1)
html=html.replace('</body>',"<script>Plotly.relayout('frameplot',{'scene.camera.eye':{x:0.5,y:-2.2,z:0.8}}).then(()=>Plotly.Plots.resize('frameplot'));</script></body>")
assert 'Previous-model DCR' not in html and 'How hard is it working?' in html
path.write_text(html)
(out/'configured-posts.json').write_text(json.dumps(dict(status='Configured preliminary study; not construction design',analysis=final_tag,section='HSS6X2X1/4',through_wall_in=6,along_wall_in=2,physical_post_height_in=106.5,analysis_length_in=112.5,head='pinned',base='pinned; anchored translational restraint assumed',members={m:d['members'][m] for m in ('DOOR-W','DOOR-E')},reactions={m:d['reactions'][m+'.base'] for m in ('DOOR-W','DOOR-E')},max_dcr=d['max_dcr'],drift_ratio=drift,passes_screen=d['passes']),indent=2))
print(path)
