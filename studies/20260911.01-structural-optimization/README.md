# Current model and sizing study

- [Exposed-frame CAD and Blender model](exposed-frame/README.md): selected sections, metal wall panels inside the frame, retained hip roof cap.
- [Fixed-geometry sizing study](network-analysis/weight-sizing/README.md): load basis, member sizes and conditional analysis results.

The earlier candidate files below are retained history.

# Earlier structural study — candidate 9

Start with [Candidate 9 results](CANDIDATE-9-RESULTS.md) and **Garage-Candidate-9-Results.pdf**. The separately saved **Garage-Candidate-9.FCStd** is in this same directory on the shared Buzzkill project. Original garage and proposed baseline files are unchanged.

This candidate removes W2, adds explicit bracing, uses a W8×24 B2 and W6×15 T1 suspended rail, and changes TE's lower chord to a raised 4×4×1/2 HSS. Its inside face trims 2 inches from the east edge of the loft deck; floor and roof elevations are unchanged. The calculations retain the slightly larger prior floor load footprint conservatively.

The tested basis is 40 psf floor live load with 75 psf storage bands and one 1,000-lb rated hoist. These are owner-study loads, not a determination of the code-required occupancy load. The 125 psf storage sensitivity fails. Connections, foundations, site wind/seismic loads, secondary roof framing, bracing details and erection sequence still require engineering. Study checks are not construction approval.

## Files

- `candidate9_complete.json`, `candidate9_roof_first.json`, `candidate9_base_pinned.json`: complete stage, roof-first and pinned-base comparisons.
- `candidate9_link_sensitivity.json`: weaker numerical offset links; same P–Delta formulation as the completed candidate.
- `candidate9-member-checks.csv`: section and governing force/capacity screen for every modeled steel member.
- `candidate9-foundation-reactions.csv`: per-case vertical reactions. Lateral test forces are NOT final wind design loads.
- `candidate9-clearance-check.json`: native CAD comparisons against 107 existing components; roof cladding is not modeled.
- `candidate9-validation.json`: numerical and artifact checks.
- `candidate9-secondary-framing.json`: preliminary joist/purlin property demands, not product selections.
- `candidate9-candidate-geometry.json`, `candidate9-candidate-selection.json`: explicit geometry and stock-section selection.
- `candidate9-overview.png`, `candidate9-comparison.png`, `candidate9-truss-elevations.png`: model and analysis views.

## Repeat or revise

Install `requirements.txt` in a Python environment, then run `python candidate9.py` and `python final_sensitivity9.py`. The scripts use the supplied `cad-analytical-members.json`, `stock-catalog-source.json`, `w-sections.json`, `design-basis.json`, and the selection recorded in `practical_no_W2_reinforced.json`. This repeats the current candidate; it does not automatically search every design.

`iterate_design.py` performs a demand-driven stock-section search on the initial geometry. That search is only a partial strength/stiffness screen. Candidate scripts add explicit bracing and clearance adjustments; do not substitute section search results without repeating the full geometry, stage and sensitivity checks.

For CAD regeneration on Buzzkill, run its bundled FreeCAD Python with `build_candidate9_cad.py`, then `check_candidate9_cad.py`. These generate a separate native-solid model and mesh. Copy the updated mesh/check outputs beside the Python study, then run `report_candidate9.py`. Regenerate CAD before publishing new figures when geometry or sections change. Stock-size labels in the CAD are metadata; editing a label alone does not regenerate a section.

Earlier `iteration2`, `practical`, `braced`, and candidate files are historical trials. They have different assumptions and are not the current design. The original `results.json` belongs to iteration 1; do not treat its uplift or section screens as the latest result.
