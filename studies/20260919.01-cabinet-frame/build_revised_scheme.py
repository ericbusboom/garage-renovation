from pathlib import Path
import json
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from matplotlib.backends.backend_pdf import PdfPages
R=Path(__file__).resolve().parent
src=(R/'build_plan.py').read_text().split("for ext in ['png','svg','pdf']")[0]
src=src.replace('east=211.5','east=224.25').replace('209.5,4','east,4').replace("'East beam CL x=211½″\\nCabinet front x=213¼″*\\n1¾″ transverse mismatch'","'Beam CL x=224¼″\\n11″ inside cabinet front\\nAligned with NE jamb post'")
src=src.replace('xytext=(90,226)','xytext=(92,225)').replace('end in [','end in [')
src=src.replace('148″ cabinet run*','148″ cabinet run').replace('49½″ from inside face*','49½″*')
src=src.replace('Solid brown/orange: specified structural beams. All specified columns are structural supports on reported concrete pilings.','All shown beams and posts structural in design intent. Existing exterior columns reported on concrete pilings.')
src=src.replace('ax.scatter([cf],[yy]', 'ax.scatter([east],[yy]').replace('ax.plot([east,cf],[yy,yy]', 'ax.plot([east,east],[yy,yy]').replace('xy=(cf,185)', 'xy=(east,185)')
s={'__file__':str(R/'build_plan.py')};exec(src,s)
fig=s['fig'];ax=s['ax'];cf=s['cf'];posts=s['posts'];east=s['east']
# Add all south supports from the source plan and both new/adopted north jamb posts.
for x,y,n in [(148.5,-21.25,'S1'),(211.5,-21.25,'S2'),(53.25,253,'NJ-W'),(224.25,253,'NJ-E')]:
 ax.add_patch(Rectangle((x-3,y-3),6,6,facecolor='#866141',edgecolor='#34434b',lw=.8,zorder=9))
 ax.text(x,y+9 if y>0 else y-10,n,fontsize=8,ha='center',color='#34434b')
ax.plot([-32,249.5],[253,253],color='#bd956a',lw=4,zorder=6)
# Call out strengthening of P2 and P3 without erasing P1/P4.
for j in [1,2]:
 yy=posts[j]
 ax.plot([cf,cf+30],[yy,yy],color='#196a87',lw=4,zorder=8)
 ax.scatter([cf+15],[yy],s=120,facecolors='none',edgecolors='#c56b20',linewidths=1.6,zorder=10)
ax.text(99,163,'P2 + P3: candidate upgraded frames\nand local foundations within cabinets',fontsize=10,color='#196a87',ha='center')
for t in list(fig.texts):t.remove()
fig.text(.07,.965,'Structural scheme · cabinet frames + garage-door jamb posts',fontsize=20)
fig.text(.07,.915,'All specified beams structural · no added gravity load assigned to existing walls · ≤10″ overall beam depth is a target',fontsize=10,color='#326e8b')
fig.text(.07,.09,'Blue: candidate P2/P3 frame upgrades. Orange rings: local foundation work to investigate, not footing size. P1/P4 remain in the support model.',fontsize=9)
fig.text(.07,.067,'NJ-W and NJ-E sit just outside the existing garage-door opening; they are jamb posts, not the building corners. North header reaches east garage edge.',fontsize=9)
fig.text(.07,.044,'Cabinet location and south offset retain earlier assumptions. Exterior piling dimensions approximate; cabinet footing locations/capacities need design.',fontsize=9)
for ext in ['png','svg']:fig.savefig(R/f'revised-support-plan.{ext}',dpi=180,facecolor='white')
# Concept section of the 1-inch-wide cabinet frame.
f,axs=plt.subplots(1,2,figsize=(15,10));f.subplots_adjust(left=.07,right=.95,top=.85,bottom=.13,wspace=.35)
a,b=axs
for q in axs:q.set_aspect('equal');q.axis('off')
a.set_xlim(-14,60);a.set_ylim(-20,122);a.set_title('Frame P2 / P3 · viewed in cabinet depth',fontsize=13,loc='left')
# 30in deep x98.5in tall side-frame with schematic diagonal members.
a.add_patch(Rectangle((0,0),30,98.5,facecolor='#f2f4f3',edgecolor='#196a87',lw=2))
a.plot([0,30,0],[0,49.25,98.5],color='#196a87',lw=2)
a.plot([30,0,30],[0,49.25,98.5],color='#196a87',lw=2)
a.plot([0,30],[49.25,49.25],color='#196a87',lw=1)
a.add_patch(Rectangle((7,98.5),8,10,facecolor='#bd956a',edgecolor='#34434b'))
a.annotate('Longitudinal beam\n10″ overall depth target',xy=(11,108.5),xytext=(38,108),fontsize=9,arrowprops=dict(arrowstyle='-'))
a.annotate('Beam bears inside\n30″ cabinet depth',xy=(11,98.5),xytext=(37,82),fontsize=9,arrowprops=dict(arrowstyle='-'))
a.annotate('Bracing shown as intent;\nmember sizes / joints TBD',xy=(17,51),xytext=(38,48),fontsize=9,arrowprops=dict(arrowstyle='-'))
a.plot([-3,33],[0,0],color='#c56b20',lw=3)
a.text(15,-10,'Local foundation / base assembly\ninside cabinet zone · TBD',ha='center',fontsize=9,color='#c56b20')
a.text(15,115,'30″ front-to-back',ha='center',fontsize=10)
a.text(-7,49,'Full wall height: 98½″',rotation=90,ha='center',fontsize=9)
b.set_xlim(-10,60);b.set_ylim(-20,122);b.set_title('Front constraint + load-path intent',fontsize=13,loc='left')
b.add_patch(Rectangle((10,0),1,98.5,facecolor='#196a87',edgecolor='#196a87'))
b.text(10.5,112,'1″ width preserved at doors',ha='center',fontsize=10)
b.annotate('Thin direction still needs\nout-of-plane restraint',xy=(10.5,55),xytext=(23,72),fontsize=10,arrowprops=dict(arrowstyle='-'))
b.text(38,32,'Cross-beam\n↓\nLongitudinal transfer beam\n↓\nP1–P4 side frames\n↓\nVerified foundations',fontsize=11,ha='center')
f.suptitle('Cabinet frames · structural concept, not a fabrication detail',fontsize=20,x=.07,ha='left')
f.text(.07,.06,'Existing uprights: reported 2″ × 1″, 11 gauge. Gauge alone does not establish steel grade, actual thickness or capacity.',fontsize=10)
f.text(.07,.035,'The 30″ dimension is interpreted as cabinet depth, not frame height. Diagonals do not by themselves restrain weak-axis buckling between cabinet bays.',fontsize=10)
for ext in ['png','svg']:f.savefig(R/f'cabinet-frame-concept.{ext}',dpi=180,facecolor='white')
with PdfPages(R/'revised-support-review.pdf') as pdf:pdf.savefig(fig);pdf.savefig(f)
# Continuous-beam stiffness sensitivity: same EI, no settlement; unit reactions only.
xs=np.array([-21.25,56,69.75,105,154,185,203,253]);K=np.zeros((16,16));force=np.zeros(16);force[4]=-1000;force[10]=-1000
for j,l in enumerate(np.diff(xs)):
 ke=np.array([[12,6*l,-12,6*l],[6*l,4*l*l,-6*l,2*l*l],[-12,-6*l,12,-6*l],[6*l,2*l*l,-6*l,4*l*l]])/l**3
 ix=[2*j,2*j+1,2*j+2,2*j+3];K[np.ix_(ix,ix)]+=ke
result={}
for name,supports in [('all_frames_engaged',[0,1,3,4,6,7]),('P2_P3_and_end_supports_capacity_sensitivity',[0,3,4,7])]:
 fixed=[2*i for i in supports];free=[i for i in range(16) if i not in fixed];d=np.zeros(16);d[free]=np.linalg.solve(K[np.ix_(free,free)],force[free]);reaction=K@d-force
 assert abs(sum(reaction[2*i] for i in supports)-2000)<1e-6
 assert abs(sum(reaction[2*i]*xs[i] for i in supports)-1000*(69.75+185))<1e-5
 result[name]={str(xs[i]):float(reaction[2*i]) for i in supports}
rows=[]
for q in [50,75,100]:
 l=256.25;trib=8.59375;w=q*trib
 rows.append(dict(illustrative_area_psf=q,tributary_width_ft=trib,line_load_plf=w,end_reaction_lb=w*l/24,moment_kip_ft=w*(l/12)**2/8000,I_required_in4_for_L360=5*(w/12)*l**4/(384*29e6*(l/360))))
(R/'revised-analysis.json').write_text(json.dumps({'beam_depth_target_overall_in':10,'east_rail_x':224.25,'crossbeam_span_in':256.25,'cabinet_post_centers':posts,'new_north_jamb_centers_x':[53.25,224.25],'cabinet_tube_reported':'2x1 11 gauge','normalized_continuous_beam_reactions':result,'illustrative_crossbeam_demands':rows},indent=2))
print('Saved revised support plan, frame concept, PDF and analysis JSON.')
