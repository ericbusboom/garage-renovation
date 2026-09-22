# STR-007 — Frame finite element analysis and member optimisation study

**Revision:** 0 · **Date:** 2026-09-18 · **Status:** `draft`
**Purpose:** Establish the design loads, test the frame against them, and show
where members can be reduced or removed.

> This is a preliminary engineering study, not a construction document. No
> connection, base plate, anchor or foundation is designed or checked here.
> Structural drawings and calculations require review and sealing by the
> responsible California-licensed structural engineer.

## Read this first

- **[Structural analysis report](structural-analysis.md)** — the findings, the
  verification, and what has to change.
- **[Interactive 3-D model](fea-model-3d.html)** — self-contained; open in a
  browser. Switch the colouring between utilisation, recommended action,
  removability and what governs each member. Hover any member for its full
  schedule row.
- **[Design load basis](design-load-basis.md)** — every load, with its source.
- **[Findings](findings.csv)** — the numbered findings as a table.

## Headline results

| | |
|---|---|
| Frame as drawn | max DCR **4.92**, 9 members over capacity |
| With the upper roof framed | max DCR **4.46**, 11 members over capacity |
| With the X-brace crossings also connected | max DCR **1.56**, 7 members over capacity |
| Members that can be deleted outright | **0** of 135, 0 lb |
| Sections verified one or more sizes lighter | **44** |
| Sections that must get heavier | **6** |

## Figures

- [Utilisation, frame as drawn](figures/utilisation-as-drawn.png)
- [Utilisation, upper roof framed](figures/utilisation.png)
- [Utilisation, adequate frame](figures/utilisation-adequate.png)
- [Where material can come out](figures/opportunity-map.png)
- [Member weight by group, before and after](figures/weight-by-group.png)
- [Distribution of utilisation](figures/utilisation-histogram.png)

## Data

- [Member schedule](member-schedule.csv) — every member with its section,
  unbraced length, slenderness, demands, DCR, governing combination, removal
  verdict and proposed section.
- [Applied load cases](load-cases.csv) — the resultant of every case as applied.
- [Support reactions](reactions.csv) — maximum compression, uplift and shear at
  each of the 12 bases.
- [Full result set](results.json) — machine-readable, every scenario.
- [Source inventory](source-inventory.csv) — checksums of the input model, the
  generating code and every published file.

## Provenance

Geometry: `frame-models/frame-20260917.05-square-upper-west.compas.json` — the canonical model, unmodified.
Analysis: PyNite 3.2.0 (linear elastic 3-D frame), COMPAS 2.15.1 geometry.
Generated 2026-09-18 10:26 by `structural-analysis-v6/run_all.py`; published by
`structural-analysis-v6/publish.py`. To reproduce, from the project root:

```
.venv/bin/python structural-analysis-v6/run_all.py
.venv/bin/python structural-analysis-v6/publish.py
```

This study consumes [frame-20260917.05-square-upper-west] and develops
[STR-006](../frame-geometry-study/README.md), which established the geometry and
explicitly assigned no loads, materials, restraints or capacities. It does not
supersede STR-006; it is the next stage against it.
