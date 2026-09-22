# STR-006 — Coordinated frame geometry study

**Revision:** 0 · **Date:** 2026-09-15 · **Status:** draft  
**Purpose:** Owner review and geometry handoff for subsequent structural engineering.

## View the study

- [Interactive 3D model](model-3d.html) — self-contained; open in a browser without a server or internet. Drag to orbit, scroll to zoom, click legend entries to hide groups. Existing walls are separate from proposed framing.
- [Nine-page drawing and truss study](frame-geometry-study.pdf) — coordinated floor plan, support/member schedules, five truss comparisons, and open coordination items.
- [Floor-plan preview](floor-plan.png)
- [Geometry decisions and coordination notes](coordination-report.md)

## Data for the next stage

- [Native COMPAS model](coordinated.compas.json) — current registry, parametric solids, truss recipes and geometric attachment graphs; historical baselines remain separately identified.
- [Neutral OBJ geometry](frame-geometry.obj) — named proposed solids and reference lines, in inches. Mesh exchange only, not an analysis or BIM model; import units explicitly.
- [Beam and truss positions](beam-and-truss-positions.csv), [support positions](support-positions.csv), [truss member endpoints](truss-members.csv), [support offsets](support-offsets.csv).
- [Geometry validation](validation.json) and [source checksums](source-inventory.csv).

## Recorded geometry

13 columns; five truss families T-S, T1, T-W, T-E and T-N; 94 truss members plus 10 plates. The plan registry contains 16 entries, including historical O2/O3 subsegment references and OB1 context. E-OB is an additional modeled beam.

Owner corrections place T-W on the far-west column row X=-34, extend the cross-members to that row, include all columns, connect E-S to S3 and E-M/E-N to T-E, and restore E-OB over the east column tops. The transverse links are 36, 35 and 36 inches respectively. E-M retains option B status; showing the east frame does not settle the alternatives or connection design.

Units are inches. X increases east, Y north, Z up. Origin is the existing outside southwest garage corner in plan; Z0 is the study floor datum. North is the garage-door side. Columns extend to Z98.5; E-OB underside is Z98.5, matching truss bottom faces. The 4-inch column symbols and 3-inch beam/chord envelopes are provisional geometry, not selected sections. Roof retains a draft 30-degree slope and older heights; loft datum is Z107.25.

## Engineering handoff and limits

No loads, load combinations, material grades, structural section properties, support restraints, connection stiffnesses or deflection limits have been assigned for this coordinated geometry study. No force, equilibrium, stability, capacity or deflection analysis has been performed. Geometric endpoint incidence does not establish a structural joint. Foundations, existing-wall capacity, field dimensions, corrosion and weld quality are unverified. Secondary joists/rafters, diaphragms, bracing design, fasteners and foundations are excluded.

Checks cover source-baseline shape matching, model save/reload, plan/elevation consistency, column bounds, beam geometry, connection endpoints and deliberate invalid edits. These are geometry checks only. Open issues include adjacent west uprights, door clearances, south bearing offsets, east option/offset details and roof coordination. Structural calculations and construction documents require the responsible California-licensed design professional's review and sealing.

This study develops [ARCH-006](../../05-architectural-design/floor-plan-study/README.md). Its far-west truss and east-beam elevation corrections are newer than that architectural drawing; ARCH-006 is retained as its own draft, not silently revised. Reconcile both with the solar/roof studies before an engineering geometry freeze.

## Reproduction and provenance

Generators and reproducible source inputs remain in the working analysis directory: [COMPAS study](../../../studies/20260917.01-compas-frame/README.md), [model/drawing generator](../../../studies/20260917.01-compas-frame/coordinated_study.py), [report publisher](../../../studies/20260917.01-compas-frame/publish_report.py), and [dependency versions](../../../studies/20260917.01-compas-frame/requirements-lock.txt). COMPAS 2.15.1, compas_model 0.9.3; other versions are pinned in the lock file. The source inventory records exact code and input hashes at publication.

From the project root, run `.venv/bin/python compas-study/coordinated_study.py`, then `.venv/bin/python compas-study/publish_report.py`. Review updated content before publishing a later revision. Report storage records the owner-directed study, not approval for construction.
