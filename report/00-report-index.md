# Garage Rebuild — Master Report Index

**Project:** Garage rebuild and loft/solar superstructure  
**Site:** 1370 Wilbur Avenue, San Diego, CA 92109  
**Document status:** Draft report framework  
**Purpose:** Design development, professional coordination, permitting, bidding, construction, and closeout  
**Last updated:** 2026-09-21

## How the document set works

The report has three layers:

1. **Project record:** decisions, assumptions, existing conditions, analyses, and design narrative.
2. **Permit and construction set:** coordinated drawings, specifications, calculations, and agency responses prepared for a stated issue.
3. **Record documents:** approved permits, inspections, submittals, testing, warranties, and as-built information.

The Markdown index is the navigable table of contents. PDFs and images provide fixed review copies. Native CAD and exchange models provide editable geometry. The manifest records status and provenance for every controlled artifact.

The project workspace was reorganized on 2026-09-21 into `report/`, `studies/`, `data/`, `viz/`, `render/`, `plans/`, `src/`, and `archive/`. This changed file locations and provenance links only; it did not change the status or technical conclusions of any controlled document.

## Table of contents

| Section | Content | Principal outputs | Current state |
|---|---|---|---|
| [00 Project controls](00-project-controls/) | Document requirements, decisions, assumptions, open issues, revision and issue history | Registers, responsibility matrix, issue checklist | Draft framework |
| [01 Project definition](01-project-definition/) | Owner goals, scope, selected scheme, performance criteria, budget, exclusions, success measures | Project brief, basis of design, room/use schedule | Planned |
| [02 Existing conditions](02-existing-conditions/) | Boundary/topographic survey, measured garage, photos, utilities, power lines, drainage, vegetation, condition assessment, permit history | Survey, existing plans/sections, photo log, utility plan, hazardous-material screening | Source candidates identified; unverified |
| [03 Land use and permitting](03-land-use-and-permitting/) | Parcel data, title/easements, base zone, community plan, coastal and other overlays, setbacks, height, lot coverage/FAR, parking/use, permit path | Zoning and code summary, parcel/overlay exhibit, permit matrix, agency meeting record | LAND-005 draft findings completed; survey and agency interpretations pending |
| [04 Geotechnical and foundations](04-geotechnical-and-foundations/) | Geologic hazards, soil/fill conditions, investigation need, bearing/lateral criteria, excavations, new piers/footings, existing slab limitations | Geotechnical report or waiver basis, foundation criteria, footing/pier schedule | Planned |
| [05 Architectural design](05-architectural-design/) | Selected massing, floor plans, roof plan, elevations, sections, doors/windows, balcony/loading opening, access, finishes | Design narrative, dimensioned drawing set, door/window/finish schedules, renderings | ARCH-006 rev 4: floor-plan and east-wall study; draft |
| [06 Structural engineering](06-structural-engineering/) | Design criteria and loads, load paths, global analysis, truss/beam/column design, trolley/hoist effects, connections, foundations, temporary stability | Structural basis, calculations, framing plans, member and connection schedules | STR-007 rev 0: frame FEA, gravity, wind and seismic screening; STR-006 geometry retained |
| [07 Building envelope](07-building-envelope/) | Integrated solar roof, low hip cap, metal wall panels, waterproofing, flashing, drainage, insulation, condensation, ventilation, fire exposure | Envelope sections/details, product requirements, drainage plan | ENV-003 rev 0: wall panel options research; draft |
| [08 Solar, electrical, and energy](08-solar-electrical-and-energy/) | Solar resource, array geometry, PV/ESS sizing, production, tariff/economics, one-line, equipment and interconnection | Energy report, array layout, electrical one-line, equipment schedule, utility/permit documents | SOL-001 rev 1: consolidated solar/battery report and 30°/35°/40° analysis; draft |
| [09 MEP and life safety](09-mep-and-life-safety/) | Electrical distribution, lighting/receptacles, ventilation, any mechanical/plumbing, alarms, egress, guards, fire separation, exterior access | MEP/life-safety plans, schedules, code analysis | Planned |
| [10 Construction planning](10-construction-planning/) | Existing-roof retention sequence, demolition, temporary bracing/shoring, access, crane/hoist operations, neighbor/site protection, inspections | Phasing drawings, temporary works criteria, logistics plan, inspection/test plan | Preliminary feasibility studies exist |
| [11 Cost, schedule, and procurement](11-cost-schedule-and-procurement/) | Quantity takeoff, alternatives, fabrication/erection strategy, allowances, contingency, schedule, long-lead items | Estimate, bid scope, schedule, procurement register | Planned |
| [12 Permit and construction set](12-permit-and-construction-set/) | Coordinated issued drawings, specifications, calculations, forms, deferred submittals, plan-check responses | Permit issue and construction issue packages | Not started |
| [13 Record documents](13-record-documents/) | RFIs, submittals, substitutions, inspections, tests, change record, as-builts, commissioning, warranties | Closeout and owner record package | Future |
| [Appendices](appendices/) | Source register, calculations/data supporting the narrative, meeting notes, selected option comparisons | Reference material with provenance | Planned |
| [Deliverables](deliverables/) | Frozen, coordinated packages assembled for a named issue | ZIP/PDF/model packages and checksums | Empty by design |

## Chapter 3 research record

[LAND-005 — Setbacks, retained garage, and proposed storage roof](03-land-use-and-permitting/setbacks-and-roof-findings.md), revision 0, 2026-09-15, status `draft`. The 15-foot side-strip roof is a conditional option requiring City interpretation, not an approved limit for this project.

[LAND-006 — Extending the garage along the existing 1-ft side setback](03-land-use-and-permitting/setback-extension-research.md), revision 0, 2026-09-20, status `draft`. Two code routes allow the 1-ft line to continue, but nothing above one story may sit inside the setback under either.

## Required professional contributions

The exact contracting arrangement remains open, but a complete package is expected to need these roles:

| Role | Expected responsibility |
|---|---|
| Owner | Program, storage and equipment loads, budget, operational constraints, decisions |
| Architect or residential designer | Code/zoning coordination, architectural plans and details, consultant coordination |
| California-licensed land surveyor or civil engineer | Property boundary, topography, improvements, easements and survey control |
| California-licensed structural engineer | Structural design, existing-condition reliance, foundations, connections, temporary stability |
| Geotechnical engineer/geologist, if required | Soil/geologic investigation and design parameters |
| Electrical/solar designer and contractor | PV, ESS, service/load study, one-line, equipment, interconnection |
| Civil/drainage professional, if triggered | Grading, drainage, stormwater, utility work |
| Arborist, if tree work or protected/public trees are affected | Tree condition, root/canopy impacts and protection plan |
| General contractor and fabricator/erector | Constructability, sequencing, cost, shop drawings and field verification |

## Immediate collection priorities

1. Obtain a boundary/topographic survey showing the garage, house, outbuilding, property lines, easements, grades, trees, overhead/underground utilities, and adjacent improvements.
2. Obtain the City parcel/zoning/overlay report and permit history for the address; verify the owner-stated 5-foot setback before fixing the building envelope.
3. Obtain the building/fire classification for the owner-confirmed upstairs storage use; document loads and access requirements.
4. Complete a measured existing-condition set and structural condition assessment, including the slab, walls, foundations, roof framing, and prior lofts.
5. Confirm whether a geotechnical investigation is required and establish design parameters for every new column footing or pier.
6. Freeze one architectural scheme and one coordinated structural grid before promoting CAD files to the report.
7. Establish roof, loft, equipment, hoist, wind, seismic, and construction loads in a signed structural design basis.
8. Coordinate drainage, waterproofing, fire separation, ventilation, egress, balcony/loading opening, PV, ESS, and utility clearances.

## Current design direction — owner-provided, not yet issued

The working direction is a lightweight steel superstructure constructed around the existing garage, with an upper storage level, integrated south-facing solar roof, low hipped rear cap, exposed exterior steel frame, and metal wall panels placed inside the frame. The design includes concentrated equipment storage and a nominal 1,000-pound trolley/hoist requirement. The owner confirms all existing garage walls remain exterior and new posts stand over open ground-level walkways. Geometry, legal occupancy classification, loads, member sizes, foundations, and construction sequence remain subject to coordination and professional design.

## Regulatory note

Current City guidance indicates that structural work supporting PV and construction of a new or modified accessory structure requires building review in addition to electrical requirements. City guidance also makes the need for a geotechnical investigation dependent on code triggers, mapped hazards, fill/expansive soil, and field conditions. Exact zoning, coastal status, setbacks, height, and other parcel controls must be verified for this address before design criteria are treated as fixed.


## Chapter 8 research record

[SOL-001 — Solar, battery and roof design](08-solar-electrical-and-energy/solar-energy-report.pdf), revision 1, 2026-09-15, status `draft`. Includes all recovered solar figures, historical reports, monthly data, new pitch and loft-envelope comparisons, battery dispatch and financial sensitivity. The current 325 ft² face supersedes the older 401 ft² area assumption for this study. Recommendation for review: about 5.6–6.0 kW plus one 13.5 kWh battery; develop 35° while retaining 30° as the height-constrained alternative. [Chapter navigation and source archive](08-solar-electrical-and-energy/README.md).

## Chapter 5 floor-plan study

[ARCH-006 — Combined floor plan study](05-architectural-design/floor-plan-study/floor-plan-study.pdf), revision 4, 2026-09-15, status `draft`. One plan shows the structure, columns, possible ground-floor extension, north door bay and optional east-wall framing. [Editable drawing and source notes](05-architectural-design/floor-plan-study/README.md). Duplicate sheets and old report copies removed at owner request; current generator: `../studies/20260915.04-floor-plan-setbacks/draw_floor_plan_study.py`.

## Chapter 6 frame geometry study

[STR-006 — Coordinated frame geometry study](06-structural-engineering/frame-geometry-study/README.md), revision 0, 2026-09-15, status `draft`. [3D viewer](06-structural-engineering/frame-geometry-study/model-3d.html) · [Drawing and truss study PDF](06-structural-engineering/frame-geometry-study/frame-geometry-study.pdf). Includes the far-west truss correction, all 13 columns, east transverse links and E-OB; model data and schedules are saved for subsequent engineering. Section sizes, loads, foundations and joint design remain unresolved.


## Chapter 6 frame finite element analysis

[STR-007 — Frame finite element analysis and member optimisation study](06-structural-engineering/fea-study/structural-analysis.md),
revision 0, 2026-09-18, status `draft`.
[Interactive 3-D model](06-structural-engineering/fea-study/fea-model-3d.html) ·
[Design load basis](06-structural-engineering/fea-study/design-load-basis.md) ·
[Member schedule](06-structural-engineering/fea-study/member-schedule.csv).

First analysis of the frame against design loads: 27
ASCE 7-16 combinations covering gravity, 96 mph wind
from four directions, and a seismic screening check. Vertical equilibrium closes
exactly and member capacities reconcile with the AISC Manual.

Three blocking findings. The flat upper roof has no framing across it and the
clerestory head has no beam, so the frame as drawn cannot carry its roof. One
column is connected only by a bearing joint carried on no member. Six X-brace
crossings are not declared joints, and connecting them alone drops the worst
utilisation from 4.46 to 1.56 at no
material cost. The loft joists fail at the code storage live load of 125 psf
though they pass at the project's assumed 40 psf, which makes the occupancy
classification a structural question.

No connection, base plate, anchor or foundation is designed or checked.
Preliminary engineering only; not for construction.

## Chapter 6 cost reduction

[STR-008 — Frame cost reduction study](06-structural-engineering/cost-reduction/cost-reduction-study.md),
revision 1, 2026-09-18, status `draft`.
[Interactive 3-D model, true section sizes](06-structural-engineering/cost-reduction/cost-reduction-3d-solid.html).

Scores changes to the frame in dollars rather than pounds, on the project's own
procurement rates. Steel is $0.77–0.94/lb, so weight is the cheapest thing in the
frame; fitted joints are $16–39 each and each distinct section carries $150–400 of
procurement. The verified package removes 14 steel members and collapses eleven
distinct sections to five: 59 pieces instead of 73, 106 joints instead of 135,
**$5,630**, with the frame at 0.951 of capacity and wind drift improved to H/514.

**No floor joist can be deleted** — at 15.4 in. centres any deletion exceeds the
24 in. span of the OSB deck. Fewer joists is available only by re-spacing to
2×10 at 24 in., worth about $1,000 and requiring its own verification. Revision 0
proposed deleting 33 joists in error; see §11 of the study.

## Chapter 7 wall panel research

[ENV-003 — Infill wall panel options](07-building-envelope/wall-panel-options/wall-panel-options.md), revision 1, 2026-09-17, status `draft`. Owner-directed survey of metal, translucent, glazed and non-metal infill materials, with installed-cost ranges, the continuous-face versus bay-infill attachment decision, and whether the panels should be recruited for lateral stiffness. [Study notes and findings](07-building-envelope/wall-panel-options/README.md).

Four findings bear on decisions already recorded. Insulated metal panels cannot act as shear walls, so retaining the current 2-inch IMP basis closes the rigidity question in favour of the frame. No bay clear width is a whole multiple of any standard panel width, so tongue-and-groove products suit continuous inside-face installation rather than bay-by-bay infill. Published Galvalume warranties exclude sites within 1,500 feet of salt water, which may disqualify the default substrate at this address and makes painted aluminum the warrantable choice. The 5/8-inch Type X drywall in the working estimate may also be serving as the Chapter 26 thermal barrier and should not be deleted as redundant insulation. Raises ENV-OI-01 through ENV-OI-08. No product is selected and no price is a quotation.

Revision 1 carries the coastal-corrosion finding through to the roof (study section 8A). The standing seam in [COST-ESTIMATE.md](../COST-ESTIMATE.md) item G names no substrate, and Galvalume is what its $6.00-9.00/sq ft price point implies. The roof is the harder case: it is the outermost surface, roughly 84% of the south face sits under PV modules where rain never rinses the salt away, and panels under a fixed array cannot be replaced without removing the array. Position for review is painted aluminum with a coastal-rated paint warranty, 316 stainless clips and fasteners, aluminum or stainless gutters, non-penetrating seam clamps, and isolation pads at dissimilar-metal contacts, at a roof-subtotal delta of roughly $1,065-2,397. Adds ENV-OI-09 through ENV-OI-12.
