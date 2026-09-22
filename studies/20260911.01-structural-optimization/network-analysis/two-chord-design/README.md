# TE/TW: two straight upper-chord runs

[Open updated diagrams (PDF)](Two-Chord-Trusses.pdf)

Interactive models: [TE](networks/TE-complete-interactive.html), [TW](networks/TW-complete-interactive.html). In the standalone ZIP, these HTML files are at the package root.


This structural-model revision implements the requested arrangement on both side trusses:

1. One retained straight sloping upper chord beneath the solar roof.
2. One continuous horizontal upper chord beneath the rear hip cap.

The two axes meet at a single knee. The horizontal axis is at 224.25 in (18 ft 8¼ in) above the ground datum, from north station 122.762 in to 253 in. Its horizontal length is 130.238 in (10 ft 10¼ in approximately). These are chord-axis dimensions, not roof-surface dimensions.

TE's previous three rear chord segments are consolidated into one physical member. TW's rear chord is lowered to meet its slope chord directly. Web ends and roof/upper-wall brace endpoints attached to these chords are adjusted; column connections are moved to the new chord height on the existing columns. Column extents and all other member stock sizes are retained. FE subdivisions at load points and joints do not imply additional physical chord pieces or splices.

The existing hip-cap roof outline remains the architectural roof envelope. Its lightweight, sheet-metal secondary frame is outside the detailed member model. The suggested 1 in, 11-gauge tubing is recorded as a possible material only; it has NOT been sized or assigned structural capacity. Existing cap dead/live-load allowances remain in the whole-frame model, and cladding weight is computed from the retained roof envelope, not the newly lowered chord. The secondary-frame takeoff must eventually be checked against that allowance.

The previous connected network is retained in `../final-networks`. This folder contains the revised geometry, whole-frame solutions, independently rebuilt truss networks, native solver drawings, and result comparisons. Native FreeCAD solids have not been regenerated in this structural-analysis step.

Numerical connection offsets remain assumptions pending physical joint design. Whole-frame linear and second-order analysis, plus roof-first analysis, are rerun before individual network verification. No optimized sizes or construction approval are implied.

## Standalone package

Install the included `requirements.txt` into a Python environment, then run `python analyze_network.py` (all models) or `python analyze_network.py TE-complete.network.json`. Use `--no-images` for numerical analysis only. The exported JSON is the editable node/element network; subdivisions at joints and load stations are analysis segments, not physical chord splices.

The roughly 0.835 partial member-screen ratio covers the study design cases, not the separate 125 psf storage sensitivity. “350 cases verified” means numerical solves and agreement with the refreshed global reference, not approval of every loading scenario.
