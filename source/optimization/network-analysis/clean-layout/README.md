# Simplified structural layouts

The W4–N1 upper bay had TWO superposed systems: narrow original truss panels
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
were removed. Section sizes are unchanged; roof-first and final stages were rerun.

## Results

Steel model 9321.7 to 8511.5 lb. Partial second-order utilization 0.834 to 0.935, governing W3. Screen assumes chord/W-member lateral restraint at up to 72 inches; this restraint is a proposed requirement, not demonstrated by these drawings. Excludes 125 psf storage sensitivity. Does not certify deflection or complete code compliance.

Native PyNite filtered whole-frame views, not independent wall solves. complete.network.json and roof_first.network.json contain the unique global network. Ground bases remain fixed analytically; actual foundations and connections are not designed. No existing wall support credit.

Audits detect collinear overlap and line intersections, not a solid-envelope fabrication clash check. Remaining intentional roof-plane crossings need joint/clearance details; no fabricated intersection capacity is established.

PyNite physical members may subdivide at internal nodes; FE pieces are not additional stock members: https://pynite.readthedocs.io/en/latest/member.html

Run make_candidate.py, solve.py, verify_and_draw.py, then make_report.py. The first two require the parent project solver/catalog; verify_and_draw.py replays exported networks with the included pinned requirements.
