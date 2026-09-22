"""Same solid viewer, updated for the R-W1/B-S bracing alternatives."""
import json
from dataclasses import fields
from html import escape
import rw1_bs_bracing as B
import s3_removal_study as T
import solid_view as SV

OUT=B.OUT
cases=[('ends-w12','Two end-bay X braces','ends',False),('truss-w12','Three-bay truss','truss',False),('ends-w14','End-bay X braces + larger R-W1','ends',True),('ends-w14-north','End-bay X braces + larger R-W1 + stronger north brace','ends',True)]
data={tag:json.loads((OUT/(tag+'.json')).read_text()) for tag,_,_,_ in cases}
base=json.loads((T.OUT/'s3-clear-floor-pdelta.json').read_text())
rows=[]
for tag,label,_,_ in [('baseline','Selected option, no new braces',None,None)]+cases:
    d=base if tag=='baseline' else data[tag]
    dr=min(v['ratio'] for v in d['drift'].values() if v['ratio'])
    brace_max=max((m['dcr'] for n,m in d['members'].items() if n.startswith('RWBS.')),default=0)
    vals=[label,f"{d['max_dcr']:.3f}",f"{d['members']['R-W1']['dcr']:.3f}",f"{brace_max:.3f}" if tag!='baseline' else '—',f'H/{dr:.0f}',str(len(d['deflection_violations'])),'Passes screen' if d['passes'] else 'Fails screen']
    rows.append(vals)
head=['Configuration','Max DCR','R-W1 DCR','Brace max DCR','Drift','Deflection failures','Screen']
table='<table><tr>'+''.join('<th>'+x+'</th>' for x in head)+'</tr>'+''.join('<tr>'+''.join('<td>'+escape(x)+'</td>' for x in row)+'</tr>' for row in rows)+'</table>'
style='<style>body{font-family:system-ui;margin:0;color:#22262b}.notes{max-width:1100px;margin:20px auto;padding:0 20px;font-size:14px;line-height:1.6}td,th{padding:8px;text-align:left;border-bottom:1px solid #ddd}table{border-collapse:collapse}#frameplot{height:70vh!important;min-height:440px}.warn{padding:12px;border-left:4px solid #b74a30;background:#fff5ef}</style>'
limits='Preliminary comparative screening only. Gussets, welds/bolts, beam local forces, brace offsets at crossings, moment connections and foundations are not designed. The existing wood-check and code-basis limitations remain. Crossed diagonals are independent, pin-ended members, with no midpoint connection or buckling-length reduction. Both compression and tension are modeled; these are not tension-only rods. Connection detailing must establish the assumed force transfer.'
links=' · '.join(f'<a href="{tag}-3d-solid.html">{label}</a>' for tag,label,_,_ in cases)
for tag,label,layout,large in cases:
    f,s,added=B.build(layout,large,tag=='ends-w14-north');d=data[tag]
    r=T.A.Result(**{k:d[k] for k in {x.name for x in fields(T.A.Result)} if k in d and k!='members'})
    r.members={k:T.A.MemberOutcome(**v) for k,v in d['members'].items()}
    geo=json.loads((OUT/(tag+'-geometry.json')).read_text())
    report=style+f'<section class="notes"><h2>{label}</h2><p>{links}</p><p>Upper S3 still connects BE.upper to B-S; the post below the loft remains removed. W1 and W2 remain. New braces are HSS2½×2½×⅛, in the plane y = −6 in., between z = 112.5 and 150.159 in. Brace bays are about 81.8 in. wide; the full truss also has two interior verticals. Crossings are shown schematically with no connection.</p><p>R-W1: <b>{f.section_of["R-W1"].name}</b>. Added members: <b>{len(added)}</b>; approximately <b>{geo["added_weight_lb"]:.0f} lb</b> of member steel, excluding connections. The existing BR-W-2 reinforcement and doubled shelf SH joist 15 are retained for this comparison. {'BR-N-1 is increased to HSS3×3×⅛ for this variant.' if tag=='ends-w14-north' else ''}</p>{table}<p>All results use P–Delta with 27 strength and 8 service combinations and the corrected roof/floor elevations. In-plane brace joints do not shorten the assumed lateral/torsional unbraced lengths of R-W1 or B-S. R-W1 retains a 245.5 in. check length. Actual lateral/torsional brace strength and stiffness require connection-specific assessment: <a href="https://www.aisc.org/media/zvaa5lt4/bracing-for-stability.pdf">AISC beam-bracing reference</a>.</p><p class="warn">{limits}</p></section>'
    summary=dict(removal={},frame_model=f.path.name+' · '+label+' · UPPER S3 RETAINED · PRELIMINARY',live_case='L100',exposure='C',basis=dict(loft_live={'L100':100},wind={'V':96}))
    p=OUT/(tag+'-3d-solid.html')
    SV.write(f,r,{},dict(sections={}),[],summary,p,cabinets=True,report_html=report)
    text=p.read_text().replace('Garage frame &mdash; members at true section size',label+' — upper S3 retained').replace('id="cb_walls"','id="cb_walls" checked',1)
    text=text.replace('</body>',"<script>Plotly.Plots.resize('frameplot');</script></body>")
    p.write_text(text)
md='# R-W1 / B-S bracing comparison\n\nUpper S3 remains connected to BE.upper and B-S. Lower S3 is removed. W1/W2 remain. This is a trial, not a replacement of the selected design.\n\n'
md+='| '+' | '.join(head)+' |\n|'+ '|'.join(['---']*len(head))+'|\n'
md+='\n'.join('| '+' | '.join(row)+' |' for row in rows)
md+='\n\nAll new members are HSS2-1/2X2-1/2X1/8. End-bay variant has four diagonal members; full truss has six diagonals plus two verticals. Equal bays are 81.833 in. wide and 37.659 in. high. Existing west brace and doubled floor joist are held constant. The final end-bay option additionally increases BR-N-1 to HSS3X3X1/8. Crossings are not connected and diagonals use full unbraced lengths.\n\nThe capacity checks retain original R-W1 and B-S unbraced lengths; new in-plane nodes alone are not lateral/torsional restraint. [AISC reference](https://www.aisc.org/media/zvaa5lt4/bracing-for-stability.pdf).\n\n'+limits+'\n'
(OUT/'README.md').write_text(md)
print('\n'.join(str(OUT/(tag+'-3d-solid.html')) for tag,_,_,_ in cases))
