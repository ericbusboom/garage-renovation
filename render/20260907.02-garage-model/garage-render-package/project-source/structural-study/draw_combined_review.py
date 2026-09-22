"""Compose the existing code-native drawings on one editable vector sheet."""
from pathlib import Path
import re,json
ROOT=Path(__file__).parent
section=(ROOT/'draw_sections.py').read_text()
plan=(ROOT/'draw_framing_plan.py').read_text()
# Reuse geometry/dimension helpers and the exact current sources, not raster screenshots.
exec(section.split('figs=[]')[0])
fig=plt.figure(figsize=(20,22),facecolor='white')
ax=fig.add_axes([.045,.535,.91,.365])
block=section.split('# WEST CUT:')[1].split("figs.append(finish(fig,'west-roof-section'))")[0]
block='\n'.join(block.splitlines()[1:])
block='\n'.join(l for l in block.splitlines() if not l.startswith('fig,ax=') and not l.startswith('fig.text(') and not l.startswith('fig.suptitle('))
exec(block)
ax=fig.add_axes([.025,.095,.65,.375]);key=fig.add_axes([.70,.102,.28,.37]);key.axis('off')
blue='#255d79';orange='#a75a2a';red='#b32e36';grey='#8a9498';purple='#73527c'
block=plan[plan.index('W=249.5;L=249'):plan.index("fig.text(.05,.94")]
exec(block)
fig.text(.045,.962,'GARAGE · SECTION + FRAMING PLAN',fontsize=27,fontweight='bold',color='#253744')
fig.text(.045,.935,'Matching member names · all beam and truss bottoms at 8′ 2½″ · columns carry the loads',fontsize=15,color='#68747b')
fig.text(.045,.906,'01  WEST SECTION — LOOKING EAST',fontsize=16,fontweight='bold',color='#253744')
fig.text(.045,.512,'02  TOP-DOWN FRAMING PLAN — NORTH UP',fontsize=16,fontweight='bold',color='#253744')
fig.text(.045,.486,'Orange = truss    Blue = beam    Green dashed = hip cap outline / hips. T-SO is a BEAM.',fontsize=12,color='#68747b')
fig.text(.045,.071,'T1 replaces B1 and reaches the roof. T-N is the whole north upper-wall truss. B3 is the north beam below the loft floor. B-S is removed.',fontsize=12,color='#253744')
fig.text(.045,.048,'Roof: 30° from T-SO, then 18-in hip cap with 8-in overhang / fascia. Rear ceiling remains 10 ft above trial loft floor.\nT-W / T-E / B-WO are outside the interior section cut and appear in plan. South support-row / T-SO connections remain unresolved; sizes are conceptual.',fontsize=10.5,color='#68747b',linespacing=1.7)
for ext in ['png','svg','pdf']:fig.savefig(ROOT/f'section-and-plan.{ext}',dpi=160)
plt.close(fig)
# Cross-check the shared labels against the generated register.
reg=json.loads((ROOT/'framing-member-register.json').read_text())
ids={m['id'] for m in reg['members']}
assert {'T-SO','T-S','T1','B2','B3','T-N'} <= ids
assert 'B1' not in ids and 'B-N' not in ids and 'B-S' not in ids
print('Combined sheet created; shared member labels verified.')
