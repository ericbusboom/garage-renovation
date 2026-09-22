# 06 — Structural Engineering

This section defines and demonstrates the complete structural load path from roof, wall panels, loft, stored equipment, and hoists through members and connections to foundations and soil. It includes existing-condition reliance, design loads, global stability, individual member/truss design, connections, diaphragms/bracing, foundations, and temporary stability.

Current workspace analyses are engineering studies. Permit and construction documents require a California-licensed structural engineer to reconcile, review, sign, and seal the design.

## Required outputs

- structural basis of design
- global model and load take-down
- truss, beam, column, connection, base/anchor, and foundation calculations
- structural plans, elevations, sections, details, and schedules
- hoist/trolley/jib design and manufacturer criteria
- erection and temporary-bracing requirements
- special-inspection and testing schedule


## Current geometry study

[STR-006 — Coordinated frame geometry study](frame-geometry-study/README.md), revision 0, 2026-09-15, status `draft`. Includes the interactive 3D model, nine-page study, native COMPAS data, neutral OBJ geometry, coordinate schedules and geometry validation. This is the geometry handoff for the next structural engineering stage; STR-001 through STR-005 remain planned.

## Current analysis

[STR-007 — Frame finite element analysis and member optimisation study](fea-study/README.md), revision 0, 2026-09-18, status
`draft`. First structural analysis of the frame: design loads established,
27 ASCE 7-16 combinations solved on a
301-element model of `frame-models/frame-20260917.05-square-upper-west.compas.json`,
every member checked to AISC 360-16, and a verified optimisation study.

- [Analysis report](fea-study/structural-analysis.md) — findings, verification and required next steps
- [Interactive 3-D model](fea-study/fea-model-3d.html) — utilisation, recommended action, removability
- [Design load basis](fea-study/design-load-basis.md) — every load with its source
- [Member schedule](fea-study/member-schedule.csv) — 135 members with demands, DCR and proposals
- [Findings](fea-study/findings.csv)

Worst utilisation is 4.46 with the upper roof framed, falling to
1.56 once the X-brace crossings are connected.
44 sections verify lighter,
6 must be heavier, and
0 members can be deleted outright.

This study develops STR-006 and does not supersede it. Section sizes, foundations,
connections and joint design remain unresolved. STR-001 through STR-005 remain
planned: this is not a structural basis of design, and no connection, base plate,
anchor or foundation has been designed or checked.
