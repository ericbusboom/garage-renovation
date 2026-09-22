# Fixed-geometry member sizing — 10 September 2026

[Report](Fixed-Geometry-Member-Sizing.pdf) · [Summary plot](Sizing-Summary.png) · [Member schedule](member-schedule.csv) · [Whole-frame interactive model](ALL-interactive.html)

The lightest candidate found weighs **5,289.8 lb of primary steel**, versus **8,526.1 lb** initially (38% reduction). This is a discrete, local stock-section search, not proof of an absolute minimum and not a construction-ready design. Geometry is unchanged from `../north-wall-coplanar/geometry.json`; the entire TN wall remains coplanar at north coordinate 253 in. Nine retained columns; W2 was already absent before this round.

## Loads and outcome

Main loft is 275.64 sq ft. Load allowances: 10 psf main solar roof and 7 psf cap on actual surface area; 20 psf roof live on plan; 4 psf upper cladding; 12 psf floor dead; 40 psf loft live with approximately 3 ft north/east bands at 75 psf. West balcony: 13.33 sq ft at 12 psf dead and 100 psf live, with eccentricity. Traveling hoist: 1,000 lb rated × 1.25 impact + 100 lb equipment = 1,350 lb. Primary steel is recalculated plus a 10% connection-weight allowance. No support credit from existing walls or slab.

Manufacturer sources and detailed component budgets are in [load-basis.json](load-basis.json). Roof secondary framing and floor joists have weight allowances but have not been sized. Roof reactions assume explicit east-west purlins at approximately 4 ft plan stations onto TE/TW. The rear cap frame remains separate.

- Main complete/roof-first/P-delta member envelope: 0.951 utilization.
- Separate completed-stage pinned-web run: 0.986; separate pinned-base run: 0.987. Not a combined release case.
- Requires designed chord/rail lateral restraint at ≤6 ft. Full-length unrestrained sensitivity fails at 8.44.
- 125 psf storage sensitivity fails at 1.60. The applicable occupancy live-load minimum is not established.
- B2: W8×24. T1 suspended floor rail: W6×8.5 **global member candidate only**; underhung trolley local flange/wheel effects are not checked.
- W3: HSS4×4×1/2 under the retained 4 in outside-envelope restriction.

No complete site wind/seismic, connection, footing, secondary bracing, erection-stability, rail-wheel or jib-crane design is claimed. Current lateral/uplift cases are sensitivities. A partial AISC-based capacity screen is used, not a complete code checking engine. Smaller primary members can require more secondary bracing and fabrication; this is not a minimum installed-cost result.

## Files and validation

- `selected.json`, `catalog.json`, `geometry.json`: selected section keys, published AISC v16 properties, unchanged physical geometry.
- `member-schedule.csv/json`: main-envelope demands/capacity and separate web/base sensitivity utilization for every member.
- `global-complete-PDelta.json`: completed second-order result. `global-complete.json`, `global-roof_first.json`: exported linear references.
- `complete.network.json`, `roof_first.network.json`: explicit solver nodes, elements, supports, loads and combinations.
- `column-reactions.csv`: linear case-specific base actions; second-order results are in the P-delta JSON.
- `web-pinned.json`, `base-pinned-confirmation.json`, `capacity-sensitivities.json`: sensitivity results. The earlier `base-pinned.json` is a near-zero basic-case numerical-tolerance failure, superseded by confirmation on actual combinations.
- `validation.json`: all 76 linear cases replayed independently; max displacement error 8.24e-7, force 0.016 lb, moment 0.045 lb-in.
- `solver-benchmark.json`: simple-beam closed-form deflection match.
- `*-wall.png`, `*-interactive.html`: native PyNite/PyVista views of the solved geometry. Lines are member axes, not fabricated profiles.

`history.json` records the final purlin-load-path stock search. Earlier baseline/iteration/compact/sizing trial files are retained locally for provenance and superseded. The selected final trial is `purlin4`.

## Reproduction

Use a fresh Python environment with the parent `requirements.txt` plus NumPy, SciPy and Matplotlib. On this Mac the native renderer runs in `optimization/.venv-network`; analysis also ran with FreeCAD's Python plus the isolated PyNite install. Do not copy a macOS virtual environment to Linux.

From the garage project root:

```sh
python optimization/network-analysis/weight-sizing/verify_and_draw.py
python optimization/network-analysis/weight-sizing/make_report.py
```

The first command rebuilds and solves the exported final linear networks, then renders them. The second builds the report from stored results without changing the design.

`optimize.py` implements the discrete search; `study_solver.py` implements audited loads and global analysis. They use project-relative dependencies in `optimization/iterate_design.py` and the retained source data. `finalize.py` generates final comparisons and sensitivities; `check_base.py` performs the confirmed pinned-base run. `setup.py` regenerates catalog/load-basis inputs from the AISC workbook; do not use it casually to overwrite an audited load basis. The source package retains dependency paths for these scripts.
