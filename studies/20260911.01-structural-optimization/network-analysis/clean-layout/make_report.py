import json,os,zipfile
from pathlib import Path
os.environ['MPLCONFIGDIR']='/private/tmp/garage-network-mpl'
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
P=Path(__file__).resolve().parent;old=P.parent/'grounded-walls'
r=json.loads((P/'global-complete-PDelta.json').read_text());b=json.loads((old/'global-complete-PDelta.json').read_text());v=json.loads((P/'validation.json').read_text());changes=json.loads((P/'changes.json').read_text());before=json.loads((P/'before-audit.json').read_text());after=json.loads((P/'after-audit.json').read_text())
summary=dict(physical_members_before=before['physical_members'],physical_members_after=after['physical_members'],merged_members=len(changes['merged_into']),removed_members=len(changes['removed']),steel_before_lb=b['steel_weight_lb'],steel_after_lb=r['steel_weight_lb'],steel_saved_lb=b['steel_weight_lb']-r['steel_weight_lb'],partial_screen_before=b['max_member_screen_ratio'],partial_screen_after=r['max_member_screen_ratio'],governing_member=max(r['member_screen'],key=lambda k:r['member_screen'][k]['ratio']),validation=v,remaining_adjacent_members=after['parallel_overlaps'])
(P/'summary.json').write_text(json.dumps(summary,indent=2))
notes='''The W4–N1 upper bay had TWO superposed systems: narrow original truss panels
plus a later broad X-brace. It now uses one diagonal spanning the whole bay.
TE also had an X-brace superposed on intermediate uprights; it now uses one
upper-bay diagonal. Old roof-cap layout uprights that crossed webs were removed.

17 uprights/hangers were merged into existing columns or side-truss uprights.
12 other members were removed. 30 redundant localized joint links were coalesced.
TS end uprights use W1/S3. T1 end uprights and end hangers use TE/TW uprights.
Shared member stiffness and self-weight occur once in the global model.

Retained deliberately:
• T1 upper truss and lower floor/trolley rail: different elevations and functions.
• TW balcony jamb at y=247 in: 6 in from W4; preserves the door opening.
• Ground and roof-plan X-braces: lateral systems, not duplicate upper truss webs.
  Their crossings/clearances and gusset details remain to be designed.
  Roof-plan braces still pass the T1 chord; crossing hardware is not resolved here.

No ground columns, floor area, roof envelope, solar allowance or occupancy loads
were removed. Section sizes are unchanged; roof-first and final stages were rerun.'''
with PdfPages(P/'Simplified-Truss-Layouts.pdf') as pdf:
 f=plt.figure(figsize=(11,8.5));f.text(.065,.94,'Audit and simplified truss layouts',fontsize=21);f.text(.065,.865,notes,fontsize=10.7,linespacing=1.48,va='top');f.text(.065,.08,f"Steel model: {b['steel_weight_lb']:,.0f} → {r['steel_weight_lb']:,.0f} lb ({summary['steel_saved_lb']:,.0f} lb removed).\nPartial second-order screen: {b['max_member_screen_ratio']:.3f} → {r['max_member_screen_ratio']:.3f}; W3 governs.\nPreliminary model. Not a complete strength, deflection, connection, foundation or code approval.",fontsize=10);pdf.savefig(f);plt.close(f)
 f,axs=plt.subplots(1,2,figsize=(16,9));
 for ax,path,title in zip(axs,[old/'TN-wall.png',P/'TN-wall.png'],['BEFORE — overlapping upper bracing','AFTER — single upper-bay diagonal']):ax.imshow(plt.imread(path));ax.axis('off');ax.set_title(title,fontsize=14)
 f.tight_layout();pdf.savefig(f,dpi=160);plt.close(f)
 for group in ['TN','TE','TW','TS','T1','ALL']:
  f,ax=plt.subplots(figsize=(14,10));ax.imshow(plt.imread(P/(group+'-wall.png')));ax.axis('off');f.subplots_adjust(0,0,1,1);pdf.savefig(f,dpi=160);plt.close(f)
 f=plt.figure(figsize=(11,8.5));f.text(.07,.93,'Member-by-member audit disposition',fontsize=20);lines=[a+'  →  '+b for a,b in changes['merged_into'].items()];lines+=['','Removed:']+changes['removed'];f.text(.07,.865,'\n'.join(lines),fontsize=9.5,linespacing=1.35,va='top');pdf.savefig(f);plt.close(f)
readme='# Simplified structural layouts\n\n'+notes+'\n\n## Results\n\n'+f"Steel model {summary['steel_before_lb']:.1f} to {summary['steel_after_lb']:.1f} lb. Partial second-order utilization {summary['partial_screen_before']:.3f} to {summary['partial_screen_after']:.3f}, governing {summary['governing_member']}. Screen assumes chord/W-member lateral restraint at up to 72 inches; this restraint is a proposed requirement, not demonstrated by these drawings. Excludes 125 psf storage sensitivity. Does not certify deflection or complete code compliance.\n\n"+'Native PyNite filtered whole-frame views, not independent wall solves. complete.network.json and roof_first.network.json contain the unique global network. Ground bases remain fixed analytically; actual foundations and connections are not designed. No existing wall support credit.\n\nAudits detect collinear overlap and line intersections, not a solid-envelope fabrication clash check. Remaining intentional roof-plane crossings need joint/clearance details; no fabricated intersection capacity is established.\n\nPyNite physical members may subdivide at internal nodes; FE pieces are not additional stock members: https://pynite.readthedocs.io/en/latest/member.html\n\nRun make_candidate.py, solve.py, verify_and_draw.py, then make_report.py. The first two require the parent project solver/catalog; verify_and_draw.py replays exported networks with the included pinned requirements.\n'
(P/'README.md').write_text(readme)
with zipfile.ZipFile(P/'Simplified-Truss-Package.zip','w',zipfile.ZIP_DEFLATED) as z:
 for p in P.iterdir():
  if p.is_file() and p.suffix!='.zip':z.write(p,p.name)
 z.write(P.parent/'requirements-lock-macos.txt','requirements-lock-macos.txt')
print('PDF and package complete')
