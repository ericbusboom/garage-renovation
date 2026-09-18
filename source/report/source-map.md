# Working Source Map

This map points to useful material in the workspace. It does **not** declare these files current, verified, or approved. Promote only after coordination under the report README.

| Subject | Working location | Candidate material | Caution |
|---|---|---|---|
| Existing garage CAD | `../model/` | `garage.FCStd`, `garage-existing.step`, parameters and validation | Field dimensions and current completeness require review. |
| Existing backyard/site | `../existing-site/` | `existing-backyard.FCStd`, `site-plan.png`, `site-review.pdf`, tree/site images | Model is photo-derived/working geometry, not a boundary survey. |
| Current exposed-frame concept | `../optimization/exposed-frame/` | `Garage-Exposed-Steel.FCStd`, STEP, Blender model, two renders | Preliminary member selections and geometry; coordinate with current roof concept. |
| Roof options | `../roof-options/` | `south-post-solar-clerestory.*`, west elevation options | Alternatives and recent concept work; no permit status. |
| Structural optimization | `../optimization/` | candidate reports, network analysis, truss submodels | Multiple iterations exist. Do not promote by filename or date alone. |
| Truss analyses | `../structural-analysis-v3/`, `../structural-analysis-v5/` | design images, load plans, calculations, CSV/JSON results | Preliminary; geometry and connections have changed; professional validation required. |
| Construction sequence | `../construction-sequence-study/`, `../roof-first-feasibility/` | roof-clearance and staged T1 studies | Feasibility studies only; temporary works require engineered design. |
| Solar/energy | `../solar-study/optimization/results/` | optimization PDF, charts, CSVs, summary JSON | Update tariff, costs, final roof geometry, shading, equipment, and consumption data before issue. |
| Site-context renders | `../backyard-blender/`, `../backyard-proposal/`, `../blender-render/`, `../site-renderings/` | Blender packages and renderings | Illustrative; several generations of building design exist. |
| Wall panel and glazing research | (desk research, no working directory) | `../report/07-building-envelope/wall-panel-options/` | Published manufacturer and trade sources accessed 2026-09-17. Prices are market ranges, not quotations. No samples, mockups or quotes obtained. |
| Published wiki | `../wiki-publish/` | HTML content and copied deliverables | Publication mirror/archive; not the design source of truth. |

## Candidate files for first coordinated package

The following are useful starting points, but none are automatically accepted as the current deliverable:

- Existing reference model: `../model/garage.FCStd` and `../model/garage-existing.step`
- Proposed-frame editable model: `../optimization/exposed-frame/Garage-Exposed-Steel.FCStd`
- Proposed-frame exchange model: `../optimization/exposed-frame/Garage-Exposed-Steel.step`
- Recent roof concept drawing: `../roof-options/south-post-solar-clerestory.pdf`
- Preliminary solar report: `../solar-study/optimization/results/Garage-Solar-Optimization.pdf`
- Preliminary truss calculation package: `../structural-analysis-v3/truss-design-and-calculations.pdf`

Before promotion, reconcile the proposed-frame CAD with the selected roof, current truss geometry, loft dimensions, openings, balcony/loading concept, and latest structural load model.


## Chapter 3 research provenance

LAND-005 is the draft synthesis at `03-land-use-and-permitting/setbacks-and-roof-findings.md`. Its source table records official references and access dates; its local-source list identifies the inspected studies. These links do not promote the working drawings or certify their dimensions.

## Consolidated solar record

SOL-001 revision 1 is now assembled in [Chapter 8](08-solar-electrical-and-energy/README.md). Its source archive preserves the solar studies and related roof-option sources, with a checksummed inventory. Reproduction code is in `../solar-study/chapter8/`. Historical capacity estimates based on about 401 ft² do not establish fit on the newer 325 ft² solar face.

## Floor-plan study provenance

[ARCH-006 — Combined floor plan study](05-architectural-design/floor-plan-study/floor-plan-study.pdf), revision 4, 2026-09-15, status `draft`. One plan shows the structure, columns, possible ground-floor extension, north door bay and optional east-wall framing. [Editable drawing and source notes](05-architectural-design/floor-plan-study/README.md). Duplicate sheets and old report copies removed at owner request; current generator: `../floor-plan-setbacks/draw_floor_plan_study.py`.

## Coordinated frame geometry provenance

STR-006 revision 0 is saved in [Chapter 6](06-structural-engineering/frame-geometry-study/README.md). Working generators and pinned dependencies remain in `../compas-study/`; the report source inventory records their hashes and those of the floor-plan basis, framing register, original model and dimension sources. Owner-directed corrections in STR-006 develop ARCH-006 but do not revise that earlier architectural sheet.
