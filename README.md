# Garage Renovation

Structural analysis, CAD modeling, and architectural visualization of a garage renovation project. Involves replacing an existing garage roof structure with an exposed steel frame, interior metal panels, loft, balcony, and solar roof.

## Key Files

### Structural Analysis
- `source/optimization/network-analysis/weight-sizing/` — **Member sizing study** (5,290 lb primary steel, 38% reduction from baseline)
  - `Fixed-Geometry-Member-Sizing.pdf` — Engineering report
  - `selection.json` — Selected steel sections (W8×24, HSS4×4×1/2, etc.)
  - `catalog.json` — AISC v16 section properties
  - `member-schedule.csv` — Per-member demands and capacity ratios

### CAD & 3D Models
- `source/optimization/exposed-frame/Garage-Exposed-Steel.FCStd` — FreeCAD solid model (88 steel members)
- `source/optimization/exposed-frame/Garage-Exposed-Steel.step` — Exchange CAD
- `source/optimization/exposed-frame/Garage-Exposed-Steel.blend` — Blender scene for rendering
- `buzzkill/Existing-Garage.FCStd` — Measured existing garage (reference)
- `buzzkill/Proposed-Garage.FCStd` — Proposed overlay

### Backyard Scene
- `source/backyard-blender/` — Existing backyard reconstruction with photo textures
- `source/backyard-proposal/` — Combined backyard + proposed garage scenes
  - `backyard-existing.blend` — Base backyard scene
  - `build_exposed_frame.py` — Inserts exposed-frame garage into backyard
  - `build_apocalypse.py` — Adds volcanic/nuclear hellscape environment
  - `build_proposal.py` — Original hip-cap proposal

### Site Measurements
- `source/existing-site/` — Existing garage survey and measurements

### Build Scripts
- `source/optimization/exposed-frame/build_cad.py` — Generate FreeCAD model from study data
- `source/optimization/exposed-frame/render_blender.py` — Render exposed-frame steel + panels  
- `source/backyard-proposal/build_exposed_frame.py` — Backyard exposed-frame scene
- `source/backyard-proposal/build_apocalypse.py` — Apocalypse variant

## Working Context

- **FreeCAD 1.1** (`/Applications/FreeCAD.app/Contents/Resources/bin/freecadcmd` on macOS, `/opt/freecad-1.1.3/` on Linux/Buzzkill)
- **Blender 5.0** (Cycles CPU renderer, 16 threads on Buzzkill)
- **Python** (for PyNiteFEA structural analysis, see `source/optimization/requirements.txt`)

## Limitations

This is an owner-study preliminary structural sizing. Connections, foundations, site wind/seismic, erection sequence, and detailed bracing are not designed. Not for construction without professional engineering review.

## Sync

`sync.sh` pulls source from the local working copy on gala and from Buzzkill (the Linux compute host). Run:

```sh
./sync.sh [/path/to/repo]
```

Default target is `/Volumes/Proj/garage-renovation`.