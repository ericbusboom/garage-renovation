"""Publish the study viewer and report, without overwriting the confirmed model."""
from pathlib import Path
from html import escape
import json
from dataclasses import fields
import s3_removal_study as T
import s3_final_checks as FC
import solid_view as SV
import loads

out=T.OUT
f,spec=FC.final_frame();T.clean(f)
d=json.loads((out/'s3-clear-floor-pdelta.json').read_text())
r=T.A.Result(**{k:d[k] for k in {x.name for x in fields(T.A.Result)} if k in d and k!='members'})
r.members={k:T.A.MemberOutcome(**v) for k,v in d['members'].items()}
assert d['passes'] and 'S3.base' not in f.nodes
assert all(min(f.xyz(i)[2],f.xyz(j)[2])>=112.5 for m,i,j in f.segments if m=='S3')
labels=[('visible-baseline','Visible starting frame'),('s3-lower-removed','S3 below loft removed, no reinforcement'),
        ('beam-only','S3 below loft removed + larger R-W1'),('beam-stiff-pdelta','Larger R-W1 + west brace; original joist'),
        ('s3-clear-floor-pdelta','Proposed: larger R-W1 + west brace + doubled joist'),
        ('w1-w2-s3-clear-floor-pdelta','Same proposal, also remove W1/W2 below loft'),
        ('whole-s3-strengthened','Entire S3 removed + eight section changes'),
        ('whole-s3-pdelta','Entire S3 removed + thirteen member changes')]
rows=[]; mdrows=[]
for tag,label in labels:
    a=json.loads((out/(tag+'.json')).read_text());dr=min(v['ratio'] for v in a['drift'].values() if v['ratio'])
    method='P–Delta' if a.get('second_order') else 'Linear'
    status='Passes screen' if a['passes'] else 'Fails screen'
    vals=[label,method,f"{a['max_dcr']:.3f}",f'H/{dr:.0f}',str(len(a['deflection_violations'])),status]
    rows.append('<tr>'+''.join('<td>'+escape(x)+'</td>' for x in vals)+'</tr>')
    mdrows.append('| '+' | '.join(vals)+' |')
changes='''<ol><li>Remove S3 from the slab to the loft beam centerline at z = 112.5 in. (9 ft 4½ in.). The 40.7 in. upper portion remains.</li><li>Change R-W1 from W12×16 to W14×22, over its 245.5 in. length.</li><li>Change BR-W-2 from HSS2½×2½×⅛ to HSS3×3×3⁄16.</li><li>Double shelf SH joist 15: two 2×8 DF-L No.2 joists, modeled as a 3×7.25 in. section with equal sharing.</li></ol>'''
limits='''This is a preliminary comparison, not permission to remove a built column. Connections, beam web bearing/crippling, base plates, anchors, foundations and temporary shoring are not designed. The retained upper S3 transfers substantial moment as well as gravity load; it cannot be treated as a simple bearing-only post. The wood checker covers bending and shear, not full axial–bending interaction or the fasteners needed for two joists to share load. Steel checks and assumed brace points need independent review. P–Delta is included, but a full AISC direct-analysis design (including imperfections and stiffness reductions) is not. Wind and seismic values are inherited study assumptions, not a new site-specific design. The east lean-to is not drawn here; its inherited line reactions are included.'''
code_note='''The model retains the project’s 2022 CBC / ASCE 7-16 / AISC 360-16 basis for comparison. San Diego applies the 2025 California codes to projects submitted on or after January 1, 2026. Confirm the applicable permit basis before design.'''
report=f'''<style>body{{font-family:system-ui,sans-serif;margin:0;color:#22262b}}.notes{{max-width:1100px;margin:20px auto;padding:0 20px;line-height:1.6;font-size:14px}}td,th{{text-align:left;padding:8px;border-bottom:1px solid #ddd}}table{{border-collapse:collapse;width:100%}}.warn{{border-left:4px solid #b74a30;padding:12px;background:#fff5ef}}#frameplot{{height:70vh!important;min-height:440px}}</style>
<section class="notes"><h2>Selected direction — retain upper S3</h2><p><b>Ground floor clear at S3; upper S3 retained. W1 and W2 remain as shown in the confirmed original.</b> Red dashed line marks the deleted S3 segment and is not a structural member.</p>{changes}
<p>27 strength combinations plus {len(loads.service_combos('L100'))} service combinations; 100 psf loft live load; 96 mph wind, Exposure C. Proposed maximum checked demand/capacity: <b>{d['max_dcr']:.3f}</b>. Worst wind drift <b>H/410</b>, versus study limit H/400. No span-deflection violations under the program’s L/240 floor and L/180 roof rules. Drift reserve is small (about 2.5%).</p>
<table><thead><tr><th>Configuration</th><th>Analysis</th><th>Max DCR</th><th>Drift</th><th>Deflection failures</th><th>Result</th></tr></thead><tbody>{''.join(rows)}</tbody></table>
<h2>Load transfer and connections</h2><p>The upper S3 now bears on B-S, which reaches the east-wall post E-S3, 36 in. farther east. R-W1, BE.upper and the connected frame also redistribute load. Under the governing strength check, upper S3 carries about 11.5 kip axial force, 26.2 kip-ft bending and 9.8 kip shear. Those are demands at the governing check station, not connection-design envelopes. The E-S3 foundation has a calculated maximum compressive reaction of 28.3 kip. Footing capacity has not been checked.</p>
<h2>Corrections made before comparison</h2><p>The old viewer labeled W1/W2 as removed, but its geometry retained both down to the slab. Its cut height had not followed the 8 in. floor raise. Its solar-roof load plane had also fallen to loft height. The reconstruction matches all 115 saved member meshes; the study corrects both issues and checks the whole load set. Footing compression/uplift report signs were corrected too.</p>
<p class="warn">{limits}</p><p>{code_note} <a href="https://www.sandiego.gov/development-services/codes-regulations">City code basis</a>. <a href="https://www.aisc.org/globalassets/aisc/publications/standards/a360-16-spec-and-commentary_june-2019_linked.pdf">AISC stability requirements</a>.</p></section>'''
summary=dict(removal={},frame_model=f.path.name+' · S3 below loft removed; W1/W2 retained · PRELIMINARY',live_case='L100',exposure='C',basis=dict(loft_live={'L100':100},wind={'V':96}))
p=out/'s3-removal-3d-solid.html'
SV.write(f,r,{},dict(sections={}),[],summary,p,show_existing=True,cabinets=True,report_html=report)
s=p.read_text().replace('Garage frame &mdash; members at true section size','Selected: S3 retained above loft, removed below')
s=s.replace('id="cb_walls"','id="cb_walls" checked',1)
# Highlight only the deleted segment; no ghost participates in the analysis.
s=s.replace('</body>', '''<script>Plotly.addTraces('frameplot',{type:'scatter3d',x:[211.5,211.5],y:[-6,-6],z:[0,112.5],mode:'lines+text',line:{color:'#c1292e',width:7,dash:'dash'},text:['S3 REMOVED BELOW LOFT',''],textposition:'bottom center',name:'Removed S3 — reference only',hovertemplate:'S3 removed below loft — reference only<extra></extra>',showlegend:false}).then(()=>Plotly.Plots.resize('frameplot'));</script></body>''')
p.write_text(s)
md=f'''# S3 removal study

A viable **preliminary screening option clears S3 below the loft**. It retains the upper 40.7 in. portion and retains W1/W2 as actually present in the confirmed HTML. This is not a fully engineered removal detail.

## Proposed changes

1. Remove S3 below z = 112.5 in.; its base support is absent from the analysis.
2. R-W1: W12X16 → W14X22 (245.5 in. long).
3. BR-W-2: HSS2-1/2X2-1/2X1/8 → HSS3X3X3/16.
4. Shelf SH joist 15: double 2x8 DF-L No.2, modeled as 3 × 7.25 in., equal sharing assumed.

## Comparison

All rows below use corrected load planes. DCR ≤ 1 and drift ≥ H/400 are the study screening criteria. These are not comprehensive code-compliance checks.

| Configuration | Analysis | Max DCR | Drift | Deflection failures | Result |
|---|---|---:|---:|---:|---|
{chr(10).join(mdrows)}

The final candidate uses all 27 strength combinations and {len(loads.service_combos('L100'))} service combinations. Maximum gravity-equilibrium relative residual: {max(v['relative'] for v in d['equilibrium'].values()):.1e}. Loft live load applied: 41,901.9 lb, corresponding to 419.019 sf at 100 psf. Surface coverage gaps reported: none. The final candidate is a P–Delta run; it is not a full direct-analysis-method design.

## Load path

The retained upper S3 loads B-S; B-S reaches the E-S3 wall post 36 in. east. R-W1, BE.upper and the rest of the connected frame participate. The governing upper-S3 check has 11.5 kip axial force, 26.2 kip-ft bending and 9.8 kip shear. These are not independent connection-design envelopes. E-S3 maximum factored compression is 28.3 kip. The retained stub and transfer-beam joints therefore require engineered moment/shear details and footing review.

## Source and reproducibility

Source COMPAS: `{f.path.name}`. Source viewer: `../column-removal-3d-solid.html`; SHA256 in `reconstruction.json`. Reconstructed transformations: south line 9 in. south; S1 24 in. east; east-wall frame added; floor/upper frame raised 8 in.; west interior beams merged; south bracing shifted to wall bay; S2 deleted; display sections read from saved HTML. All 115 member meshes match to the viewer’s 0.01 in. rounding. This verifies geometry/sections, not undocumented connection releases. The study uses the repository’s default pinned bases, bracing/joist end releases, rigid steel joints and declared offset links.

Four regression tests cover roof/floor elevations, rejected stale cut height, real removal of raised columns and reaction-envelope signs. No canonical COMPAS file or confirmed HTML has been overwritten. New geometry remains a derived study generated by the scripts, not a promoted design. `legacy-load-planes/` contains discarded comparisons from before the roof-plane fix; do not use them for decisions.

## Limits and applicable basis

{limits}

{code_note} [City of San Diego codes](https://www.sandiego.gov/development-services/codes-regulations). [AISC 360-16 stability provisions](https://www.aisc.org/globalassets/aisc/publications/standards/a360-16-spec-and-commentary_june-2019_linked.pdf).

A qualified structural engineer needs to confirm loads, full member checks, connections, foundations and construction sequence before removal. The complete-removal option described below also passes the screening, with more reinforcement.
'''
(out/'README.md').write_text(md)
print(p)

# Complete-removal alternative: same viewer and checks, no S3 member at any height.
from s3_whole_check import whole_option
whole_f,whole_spec=whole_option();T.clean(whole_f)
whole_d=json.loads((out/'whole-s3-pdelta.json').read_text())
whole_r=T.A.Result(**{k:whole_d[k] for k in {x.name for x in fields(T.A.Result)} if k in whole_d and k!='members'})
whole_r.members={k:T.A.MemberOutcome(**v) for k,v in whole_d['members'].items()}
assert whole_d['passes'] and 'S3' not in whole_f.members and 'S3.base' not in whole_f.nodes
base,_=T.reconstruct()
changes_all=[(m,base.section_of[m].name,whole_f.section_of[m].name) for m in whole_f.members if whole_f.section_of[m].name!=base.section_of[m].name]
assert len(changes_all)==13,len(changes_all)
change_table='<table><tr><th>Member</th><th>Existing in saved view</th><th>Study section</th></tr>'+''.join('<tr><td>'+escape(m)+'</td><td>'+escape(a)+'</td><td>'+escape(b)+'</td></tr>' for m,a,b in changes_all)+'</table>'
whole_report=report[:report.index('<section')]+f"""<section class="notes"><h2>Unselected alternative — do not use as the current design</h2><p>The owner selected retention of upper S3 between BE.upper and B-S. This full-removal option is retained only for comparison.</p>
<p><b>No S3 at any elevation and no new replacement floor post.</b> W1 and W2 remain, as they do in the confirmed model. Red dashed line marks the former S3 position.</p>
<p>This option removes the upper portion as well as the ground-floor post. Its larger beams and posts redistribute load into the east-wall frame and the remaining frame. The connected model relies on rigid steel joints; their moment connections have not been designed.</p>
<p><b>Second-order maximum checked demand/capacity: {whole_d['max_dcr']:.3f}. Wind drift: H/411 versus H/400. No reported span-deflection violations.</b> All 27 strength and 8 service combinations were included. This is a limited screening result, not a complete structural design.</p>
<h2>13 reinforcement changes</h2>{change_table}
<p><a href="s3-removal-3d-solid.html">Compare the simpler option: remove S3 below the loft only</a> — that option retains its upper portion and needs three reinforcements.</p>
<h2>Comparison</h2><table><tr><th>Configuration</th><th>Analysis</th><th>Max DCR</th><th>Drift</th><th>Deflection failures</th><th>Result</th></tr>{''.join(rows)}</table>
<p class="warn">{limits.replace('The retained upper S3 transfers substantial moment as well as gravity load; it cannot be treated as a simple bearing-only post. ', '')}</p>
<p>{code_note} <a href="https://www.sandiego.gov/development-services/codes-regulations">City code basis</a>. <a href="https://www.aisc.org/globalassets/aisc/publications/standards/a360-16-spec-and-commentary_june-2019_linked.pdf">AISC stability requirements</a>.</p></section>"""
whole_summary=dict(removal={},frame_model=whole_f.path.name+' · ALL OF S3 REMOVED; W1/W2 retained · PRELIMINARY',live_case='L100',exposure='C',basis=dict(loft_live={'L100':100},wind={'V':96}))
whole_path=out/'s3-entirely-removed-3d-solid.html'
SV.write(whole_f,whole_r,{},dict(sections={}),[],whole_summary,whole_path,show_existing=True,cabinets=True,report_html=whole_report)
wh=whole_path.read_text().replace('Garage frame &mdash; members at true section size','Unselected: entire S3 removal study').replace('id="cb_walls"','id="cb_walls" checked',1)
wh=wh.replace('</body>',"<script>Plotly.addTraces('frameplot',{type:'scatter3d',x:[211.5,211.5],y:[-6,-6],z:[0,153.159],mode:'lines',line:{color:'#c1292e',width:7,dash:'dash'},name:'S3 removed entirely',hovertemplate:'Former S3 position — reference only<extra></extra>',showlegend:false}).then(()=>Plotly.Plots.resize('frameplot'));</script></body>")
whole_path.write_text(wh)
all_md='\n'.join('| '+m+' | '+a+' | '+b+' |' for m,a,b in changes_all)
md += f"""
## Complete S3 removal alternative

The entire S3 member can also be eliminated in the preliminary model, without adding a new post, with these 13 reinforcement changes. W1 and W2 remain. Viewer: `s3-entirely-removed-3d-solid.html`. This is a tested candidate, not an optimization or claim of minimum changes/cost.

| Member | Section in saved view | Candidate section |
|---|---|---|
{all_md}

Second-order result: max checked DCR {whole_d['max_dcr']:.3f}; worst drift H/411; zero reported span-deflection failures. The controlling checked member is {whole_d['worst'][0]['member']}. Maximum gravity equilibrium relative residual: {max(v['relative'] for v in whole_d['equilibrium'].values()):.1e}. All limitations above also apply. There is no S3 segment, member or footing in this candidate. The full removal was explicitly verified in the generated member set and viewer.
"""
md=md.replace('A viable **preliminary screening option clears S3 below the loft**.', '**Selected by the owner: retain upper S3 as the connection from BE.upper down to B-S; remove S3 only below the loft.** The below-loft option needs three reinforcement changes. Entire-S3 removal is an unselected comparison, not the current direction.')
(out/'README.md').write_text(md)
print(whole_path)
