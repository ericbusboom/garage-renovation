# ARCH-006 — Floor plan study

**Revision:** 4 · **Date:** 2026-09-15 · **Status:** draft

One combined drawing contains the existing garage, upper structure, full-width loft, columns, possible ground-floor extension, new north door bay, and **optional east-wall framing**.

- [PDF](floor-plan-study.pdf)
- [Preview](floor-plan-study.png)
- [Editable SVG](floor-plan-study.svg)
- [Coordinate data](basis.json)

## Current layout

- Orange: possible extension from WB3 → W3 → W4 → N1 → N2, returning along the existing building.
- WBN is removed. N1 is 16 ft west of N2, center-to-center; the 4-in post symbols leave 188 in between faces before jambs and finishes.
- WB3 is against the west wall, aligned with W3. S3 aligns with E-S; E-M/B aligns with W3.
- Purple: optional east-wall support frame. Option A uses E-S/E-N; option B adds concealed E-M. The full 12-in east strip remains clear of posts.
- Blue: upper structural outline and north roof overhang. Teal: full-width loft outline.

## Basis and remaining coordination

Units are inches in the coordinate data; X east, Y north, origin at the existing outside southwest corner. The earlier existing footprint is 249.5 × 249 in. Property lines use owner-stated 12-in east and 82-in north clearances. Requested east/north limits are 4 ft / 5 ft, with a 27-in north roof overhang. These are study inputs, not a survey or agency approval.

Post symbols are 4 in square. South column centers are Y=-66, west row X=-34; provisional beam centers remain Y=-64 and X=-32. Connections, offsets, foundations, the transfer to the east-wall frame, door sizing and wall alterations remain unresolved. The extension and east-wall framing are options, not adopted construction work. Earlier elevations and analyses may not match this plan.

## Source and upkeep

The single current generator is [draw_floor_plan_study.py](../../../studies/20260915.04-floor-plan-setbacks/draw_floor_plan_study.py); [publish_clean_study.py](../../../studies/20260915.04-floor-plan-setbacks/publish_clean_study.py) publishes and checks the report copy. Sources: [existing dimensions](../../../data/model/parameters.json), [earlier framing register](../../../studies/20260908.01-structural-design/framing-member-register.json), [member-width model](../../../render/20260907.02-garage-model/build_and_render.py), and [East Wall Study](../../../studies/20260915.02-east-wall/README.md), with owner corrections recorded in the current geometry. Relative source paths inside `basis.json` refer to the working `floor-plan-setbacks/` folder.

Keep this directory to these five current files. Replace them when the study changes; do not add duplicate plan sheets or old revision folders here. The owner requested removal of the previous report copies. Working source history remains outside this folder. The report manifest records current checksums and provenance.
