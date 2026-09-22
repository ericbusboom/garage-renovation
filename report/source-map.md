# Working Source Map

This map points to useful material in the workspace. It does **not** declare these files current, verified, or approved. Promote only after coordination under the report README.

| Subject | Working location | Candidate material | Caution |
|---|---|---|---|
| Existing garage CAD | `../data/model/` | `garage.FCStd`, `garage-existing.step`, parameters and validation | Field dimensions and current completeness require review. |
| Existing backyard/site | `../render/20260908.01-existing-site/` | `existing-backyard.FCStd`, `site-plan.png`, `site-review.pdf`, tree/site images | Model is photo-derived/working geometry, not a boundary survey. |
| Current exposed-frame concept | `../studies/20260911.01-structural-optimization/exposed-frame/` | `Garage-Exposed-Steel.FCStd`, STEP, Blender model, two renders | Preliminary member selections and geometry; coordinate with current roof concept. |
| Roof options | `../studies/20260915.01-roof-options/` | `south-post-solar-clerestory.*`, west elevation options | Alternatives and recent concept work; no permit status. |
| Structural optimization | `../studies/20260911.01-structural-optimization/` | candidate reports, network analysis, truss submodels | Multiple iterations exist. Do not promote by filename or date alone. |
| Truss analyses | `../studies/20260908.03-structural-analysis-v3/`, `../studies/20260909.02-structural-analysis-v5/` | design images, load plans, calculations, CSV/JSON results | Preliminary; geometry and connections have changed; professional validation required. |
| Construction sequence | `../studies/20260909.03-construction-sequence/`, `../studies/20260909.04-roof-first-feasibility/` | roof-clearance and staged T1 studies | Feasibility studies only; temporary works require engineered design. |
| Solar/energy | `../studies/20260915.03-solar/optimization/results/` | optimization PDF, charts, CSVs, summary JSON | Update tariff, costs, final roof geometry, shading, equipment, and consumption data before issue. |
| Site-context renders | `../render/20260908.02-backyard-existing/`, `../render/20260910.01-backyard-proposal/`, `../render/20260908.03-garage-site/`, `../render/20260907.01-site-concepts/` | Blender packages and renderings | Illustrative; several generations of building design exist. |
| Wall panel and glazing research | (desk research, no working directory) | `../report/07-building-envelope/wall-panel-options/` | Published manufacturer and trade sources accessed 2026-09-17. Prices are market ranges, not quotations. No samples, mockups or quotes obtained. |
| Published wiki | `../archive/wiki-publish/` | HTML content and copied deliverables | Publication mirror/archive; not the design source of truth. |

## Candidate files for first coordinated package

The following are useful starting points, but none are automatically accepted as the current deliverable:

- Existing reference model: `../data/model/garage.FCStd` and `../data/model/garage-existing.step`
- Proposed-frame editable model: `../studies/20260911.01-structural-optimization/exposed-frame/Garage-Exposed-Steel.FCStd`
- Proposed-frame exchange model: `../studies/20260911.01-structural-optimization/exposed-frame/Garage-Exposed-Steel.step`
- Recent roof concept drawing: `../studies/20260915.01-roof-options/south-post-solar-clerestory.pdf`
- Preliminary solar report: `../studies/20260915.03-solar/optimization/results/Garage-Solar-Optimization.pdf`
- Preliminary truss calculation package: `../studies/20260908.03-structural-analysis-v3/truss-design-and-calculations.pdf`

Before promotion, reconcile the proposed-frame CAD with the selected roof, current truss geometry, loft dimensions, openings, balcony/loading concept, and latest structural load model.


## Chapter 3 research provenance

LAND-005 is the draft synthesis at `03-land-use-and-permitting/setbacks-and-roof-findings.md`. Its source table records official references and access dates; its local-source list identifies the inspected studies. These links do not promote the working drawings or certify their dimensions.

## Consolidated solar record

SOL-001 revision 1 is now assembled in [Chapter 8](08-solar-electrical-and-energy/README.md). Its source archive preserves the solar studies and related roof-option sources, with a checksummed inventory. Reproduction code is in `../studies/20260915.03-solar/chapter8/`. Historical capacity estimates based on about 401 ft² do not establish fit on the newer 325 ft² solar face.

## Floor-plan study provenance

[ARCH-006 — Combined floor plan study](05-architectural-design/floor-plan-study/floor-plan-study.pdf), revision 4, 2026-09-15, status `draft`. One plan shows the structure, columns, possible ground-floor extension, north door bay and optional east-wall framing. [Editable drawing and source notes](05-architectural-design/floor-plan-study/README.md). Duplicate sheets and old report copies removed at owner request; current generator: `../studies/20260915.04-floor-plan-setbacks/draw_floor_plan_study.py`.

## Coordinated frame geometry provenance

STR-006 revision 0 is saved in [Chapter 6](06-structural-engineering/frame-geometry-study/README.md). Working generators and pinned dependencies remain in `../studies/20260917.01-compas-frame/`; the report source inventory records their hashes and those of the floor-plan basis, framing register, original model and dimension sources. Owner-directed corrections in STR-006 develop ARCH-006 but do not revise that earlier architectural sheet.
