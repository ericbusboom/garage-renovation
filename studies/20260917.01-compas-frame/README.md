# COMPAS floor-plan and truss trial

**Latest deliverable:** `output/coordinated/floor-plan-and-truss-studies.pdf` and
`output/coordinated/coordinated-3d.html`. These expand the trial to the complete
named primary frame and all five trusses; see the coordinated-study section below.

This experiment uses the existing project data to create actual COMPAS geometry
and a COMPAS Model assembly. It generates its drawings **after saving and reloading
the COMPAS JSON model**. No IFC or desktop CAD application is required.

## Open the results

- `output/floor-plan.png` / `.svg` / `.pdf`: current floor-plan study, including
  walls and openings, all 13 plan column symbols, footprints, reference lines,
  the proposed extension option, and selected dimensions.
- `output/truss-elevations.png` / `.svg` / `.pdf`: five earlier truss assemblies
  projected from the imported COMPAS meshes.
- `output/study.pdf`: both sheets together.
- `output/model-3d.html`: self-contained interactive Plotly model. Open in a
  browser, drag to orbit, scroll to zoom, and click legend entries to toggle layers.
  Hover over geometry to identify members. It needs no internet connection.
- `output/garage.compas.json`: reloadable COMPAS objects, including the assembly,
  plan geometry, source metadata and reference graph.
- `output/validation.json`: successful checks, deliberately rejected edits, and
  coordinate differences between source revisions.

## Environment and rebuild

The project virtual environment is `../.venv`, using Python 3.12. The experiment
uses COMPAS 2.15.1, COMPAS Model 0.9.3, Matplotlib and Plotly. Exact installed
dependencies are in `requirements-lock.txt`; direct dependencies are in
`requirements.txt`.

From the project root:

```sh
.venv/bin/python compas-study/build_study.py
```

To recreate the environment:

```sh
python3.12 -m venv .venv
.venv/bin/python -m pip install -r compas-study/requirements-lock.txt
```

## What is modeled

- `Point`, `Line`, `Polygon`: current column centers and symbols, reference lines,
  property boundaries, loft/roof/structure outlines, and extension option.
- `Mesh`: wall volumes with source opening gaps, sills and headers; imported
  truss and beam solids. Original mesh vertices are converted from meters to inches.
- `ColumnElement`: the nine historical column solids are rebuilt parametrically,
  using the old 4-inch square visualization section and 98.5-inch source height.
  These are actual COMPAS Model parametric elements, not only mesh imports.
- `Model` / `MeshElement`: named assembly elements with persistent GUIDs.
  The small adapter in `geometry_types.py` supplies mesh geometry and serialization
  for COMPAS Model's abstract base element. Keep that module available when loading
  this experiment's JSON.
- `Graph`: eleven registered framing reference lines and their named endpoints.
  Reference endpoints are deliberately not merged into structural joints.
- Annotations reference column IDs, so a column move retains label identity.

The experiment uses core COMPAS and COMPAS Model. It does not install COMPAS
Timber: these source trusses are steel concepts, and the generic geometry/model
classes are a better initial test. It performs no structural analysis.

## Source revision boundaries

The current plan is read from `floor-plan-setbacks/floor-plan-study-basis.json`.
Existing wall dimensions/openings come from `model/parameters.json`.
Historical framing comes from `structural-study/framing-member-register.json`
and `model-renders/garage-model.json`.

The current plan has changed since the historical truss model. The trusses are
imported without deformation or relocation. The 3D view displays the current
plan on a drawing plane at Z=0 for comparison; it is **not** a reconciled design.
Current plan column base/top elevations remain null. The current plan's 4-inch
squares are diagram symbols, not newly selected structural sections.

In particular, the south row is at Y=-66 while its provisional beam reference
is at Y=-64; the old east truss reference is X=224.25 while current S2/N2 centers
are X=211.5. The report lists all changed historical post coordinates. These are
source differences, not automatic geometry repair instructions.

Wall openings follow the existing renderer's convention: horizontal offsets
are measured from the east end. Door heights retain the existing placeholders.

Every input is recorded with a path and SHA-256 hash in the model. Regeneration
overwrites only the experiment's output directory; original studies are untouched.

## Checks and programmatic editing

The build validates finite coordinates, positive symbol sizes, point/footprint
agreement, label targets, nonzero graph member lengths, closed valid mesh topology,
the source north-door center spacing, and the source south support row.
It also checks JSON round-trip coordinates/topology, original imported vertices,
and bounds of the reconstructed parametric columns.

The check suite moves WB3 12 inches north in a disposable model and checks both
its point and footprint. It then verifies that a missing label target, negative
section, collapsed member, and misplaced north-door support are rejected.

Example, from the `compas-study` directory using the project environment:

```python
from compas.data import json_load, json_dump
from build_study import move_plan_column, validate

model = json_load('output/garage.compas.json')
move_plan_column(model, 'WB3', dy=12)
validate(model)
json_dump(model, 'output/edited-example.compas.json', pretty=True)
```

These are explicit project rules, not checks COMPAS magically supplies. A valid
mesh does not establish freedom from self-intersections, acceptable connections,
member capacity or a correct load path. Mesh imports also preserve shapes rather
than reconstructing each truss member's original design parameters.

## Findings

The completed run contains 137 assembly elements, 13 current plan column
locations, nine parametric historical columns, and eleven framing reference
lines. Six positive check groups pass; all four deliberately invalid edits are
rejected. The static sheets and interactive 3D rendering were visually inspected.

COMPAS supplies the geometric objects, transformations, mesh topology and JSON
round-trip machinery we need. COMPAS Model adds assemblies and parametric elements.
The remaining project-specific layer is relatively small: stable IDs, source
revisions, reference-face conventions, unknowns, labels, and validation rules.

T1 now also has a separate parametric trial described below. Reconciling the
historical truss placement with the current floor-plan revision remains separate work.

Two integration details emerged in the trial: imported meshes require the small
`MeshElement` adapter, and pretty JSON can change dictionary iteration order.
Geometry comparisons therefore use vertex/face IDs, not list position. Generated
GUIDs survive save/reload; a fresh build creates new GUIDs, while source-based
element names and plan column IDs remain stable.

## Parametric T1 trial

Run from the project root:

```sh
.venv/bin/python compas-study/parametric_truss.py
```

Outputs are `output/parametric-T1.html` (interactive case selector),
`output/parametric-T1.png`, `.svg`, `.pdf`, and
`output/parametric-T1-validation.json`. Each case also has a reloadable
`T1-<case>.compas.json` and a `T1-<case>-members.csv` centerline-length schedule.
The case selector displays Python-generated variants; it does not run Python
or accept arbitrary parameter edits in the browser.

The baseline reconstructs T1 from source dimensions: span 224.25 inches,
depth 84.643248 inches, six equal bays, station Y=69.75, bottom Z=98.5.
It generates 11 physical members, five illustrative joint plates and 14 named
geometric joints. Continuous chords contain intermediate attachment points;
the connectivity graph has 21 segments but does not split the physical chords.

`MemberElement` in `geometry_types.py` stores endpoints and section envelopes
and generates its mesh when needed. `TrussParameters` is immutable; dimension
changes create a new assembly, avoiding stale cached shapes from in-place edits.
For example, from this directory:

```python
from dataclasses import replace
from parametric_truss import source_parameters, make_truss, validate_truss

parameters = replace(source_parameters(), span=248.25)
truss = make_truss(parameters)
validate_truss(truss)
```

The original baseline matches all 16 original member/plate vertex sets within
1e-7 inches. A span increase of 24 inches and a depth increase of 12 inches
regenerate chords, uprights, braces, joint locations, plates, drawings and CSV
lengths. All three cases survive JSON save/reload with the same geometry and IDs.
Tests reject a brace endpoint moved off its joint, a missing joint, a missing
graph connection, a negative span and a noninteger panel count.

These checks establish geometric attachment, not engineered connections or
structural stability. The original end-braced rectangular layout is retained,
including its need for an appropriate frame/joint design. Sections remain source
visualization envelopes; CSV lengths are centerline lengths, not fabrication cuts.
The trial variants do not alter the floor plan or the original full-model preview.

## Coordinated floor plan and five trusses

```sh
.venv/bin/python compas-study/coordinated_study.py
```

Everything for this phase is saved under `output/coordinated/`:

- `floor-plan-and-truss-studies.pdf`: nine pages — plan, support schedule,
  beam/truss position schedule, five baseline-versus-draft truss studies, and
  open coordination items. Each sheet also has a separate SVG, PNG and PDF.
- `coordinated-3d.html`: offline-capable 3D inspection with named truss layers,
  beam bottom reference lines and all 13 solid column locations. Columns run
  from floor Z0 to the common frame bottom Z98.5. East-wall column heights are
  explicitly provisional, and E-M remains option B. East-wall and outbuilding
  beams still have unknown elevations and are listed in the plan/schedule.
- `coordinated.compas.json`: one bundle containing the plan registry, five
  baseline trusses, five parametric draft trusses, geometry graphs and source hashes.
- `beam-and-truss-positions.csv`, `support-positions.csv`: all 13 named plan
  members/references (including context OB1 and historical O2/O3 subsegments)
  and 13 current support locations.
- `truss-members.csv`: 94 physical draft truss members with endpoints, source
  section envelopes and centerline lengths; five illustrative plates on each
  transverse truss are excluded from this member-length schedule.
- `support-offsets.csv`, `coordination-report.md`, `validation.json`: geometric
  offsets, the basis for every position, unresolved items and check results.

### Source precedence and draft choices

The current floor-plan basis controls support centers. The final entries in
`structural-study/latest-framing-corrections.md` establish member naming and
the common superstructure bottom datum. Earlier source-model geometry supplies
the baseline truss layouts. The code does not treat all those revisions as an
already coordinated design.

The draft places T-E at X211.5 on N2/S2/S3, T-N at Y269 on W4/N1/N2,
T1 at W2's Y69.75 row and B2 at W3's Y185 row. Per the user correction,
T-W is on the far-west column row at X=-34, from W1 to W4. T-S, T1, B2 and
B3 extend west to meet it. O2/O3 now identify subsegments of T1/B2 rather than
separate overlapping beams. T-SO retains the plan's Y=-64 reference while the south column centers
remain Y=-66. B3 retains Y249, distinct from T-N. No old B-S, B1, B-N or
E1 is silently reintroduced; their historical naming/status is superseded here.

Truss heights for the **draft** use an explicitly assumed continuation of the
old 30-degree roof profile and old elevations, anchored to the revised T-SO
Y=-64 line. The actual roof shape remains unfinished. Longitudinal web ends
are aligned with chord axes in the draft so their geometric attachments are
explicit; original 1.5-inch centerline discrepancies remain in the untouched
baseline. The report records these choices rather than presenting them as
user-approved structural details.

Upper loft-door geometry remains distinct from the new N1–N2 ground-floor
door bay. Historical cramped uprights and door-clearance discrepancies are
reported rather than automatically redesigned.

### Checks and editing

All five baselines are checked against all source member/plate vertex sets:
T-S 16, T1 16, T-W 24, T-E 23, T-N 26. The saved/reloaded draft assemblies
are checked against their recipes, attachment graphs, mesh validity and plan axes.
All draft member endpoints lie on another member axis. This is geometric
incidence, not a statement of structural stability or connection adequacy.

A disposable W2 move of +6 inches propagates through T1, O2, the roof
intersection and both longitudinal truss station lists. Negative tests reject
a member changed without its recipe, a deleted graph edge, inconsistent east
support axes and an altered north door bay. Current source studies remain unchanged.

Example from this directory:

```python
from coordinated_study import make_plan, recipe, generate, validate_plan, validate_truss

plan = make_plan({'W2': {'y': 75.75}})
validate_plan(plan)
trusses = {name: generate(recipe(name, plan))
           for name in ('T-S', 'T1', 'T-W', 'T-E', 'T-N')}
for truss in trusses.values():
    validate_truss(truss)
```

The plan registry is the common input to member positions and truss recipes.
Rebuild assemblies after changing inputs; directly mutating cached element
geometry is not the supported editing path. This phase covers the named primary
frame, not all secondary floor joists, rafters, fasteners or foundations.

### Far-west truss and full columns correction

The user clarified that T-W is suspended over the far-west support row, not
over the existing west wall. The revised plan, recipes, schedules, PDF and 3D
preview apply this correction together. All 13 support locations now have
parametric ColumnElement geometry; frame columns use the common Z98.5 bottom
datum, while east-wall heights remain a visualization assumption. E-M is visibly
identified as option B. Sections remain the 4-inch source symbols.

Additional checks reject returning T-W to X0, cross-members that stop short of
the western truss, missing column solids, and column bounds inconsistent with the
support registry. All checks run after JSON reload. The historical baseline
truss drawings are intentionally retained for comparison.

### East column connections

Three requested transverse references now connect E-S to S3 (36 inches), E-M
to T-E (35 inches), and E-N to T-E (36 inches). All use the provisional column-top
frame datum Z98.5; sections and joint details remain unassigned. E-M retains its
option B status. These links are included in the plan, 3D view, COMPAS JSON and
member schedule, bringing the plan registry to 16 entries. Endpoint checks run
after JSON reload, reject a detached connection, and verify that moving E-M in
both X and Y regenerates its connection to the east truss.

### East overhead beam restored in 3D

E-OB now has a saved parametric solid across E-S and E-N, retaining the floor-plan
extents Y=-4..253 at X247.5. Its underside is Z98.5, across the column tops and
level with the brown truss bottom chords. The brown 3-inch envelope matches the
truss display convention; it does not select a structural section. Round-trip
checks verify the solid against its plan reference, elevation and end supports.

## Current frame: shared-joint specification

Use `connected_frame.py` and the authoritative
`roof-studies/square-upper-west/connected-frame/frame-spec.json` for current framing.
The compiler builds a native COMPAS Graph and Model and validates every member end.
`current_frame_view.py` reads those compiled meshes and includes the graph/model in
its COMPAS bundle. The older CAD-import workflow is preserved only as provenance.
See the connected-frame README and per-end audit for scope and remaining design limits.
