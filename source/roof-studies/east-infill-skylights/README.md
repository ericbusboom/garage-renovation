# East setback infill and skylights — rough concept

2026-09-15 · draft · low-fidelity massing review. Inches in CAD input and mesh data; millimetres in FreeCAD/STEP; metres in Blender. X east, Y north, Z up.

This revision develops the older `optimization/exposed-frame/Garage-Exposed-Steel.FCStd` capped-hip concept. It retains the lower garage, brings the proposed upper east edge to X211.5, and slopes an infill roof down across the exposed east strip to the E-S/E-N beam line X247.5 at Z101.5. The rear shallow four-sided hip cap remains. Six glazed skylights replace the uppermost row of the south-facing solar slope, immediately below the cap; 18 illustrative solar panels remain below them. Skylight openings have no opaque skin behind them.

The corrected east roof has 12 sloping rafters at equal 23-inch centers from Y=-2 to Y251. Lower endpoints follow E-OB's Z100 axis at X247.5; upper endpoints intersect the actual coordinated T-E top-chord axes at X211.5. T-E is now rebuilt from the saved coordinated truss-member table. Rafters use provisional 3-inch display envelopes; spacing and sections are discussion assumptions, not sizing results. The roof skin follows the closely divided ruled surface above these rafters, replacing the former large diagonal fold. Roof skin and rafters are separate CAD groups and Blender collections. `03-east-rafter-study.png` shows the roof removed to expose the support arrangement. `east-roof-rafters.csv` records stations and endpoints.

The main roof/cap-to-infill weatherproof junction, actual bearing details and envelope clearance remain for later coordination. The current main solar roof retains the older concept elevations.
Files: `garage-east-infill-skylights.FCStd`, `.step`, `.blend`; `01-southeast-draft.png` and `02-northeast-draft.png`; `cad-mesh.json`, `validation.json`, `render-validation.json`; editable generators `build_cad.py` and `render_blender.py`.

Except for T-E and the new east support frame/rafters, the old proposed frame was compressed laterally for massing context. Its historical member metadata must not be used for engineering: this is not a replacement for the coordinated STR-006 structural geometry. The original models and controlled report remain unchanged. After the roof shape is agreed, reconcile envelope, framing, skylight supports, solar layout and connections before detailed rendering or engineering.

CAD generation uses FreeCAD 1.1.3 on the existing Buzzkill modeling workstation; Blender uses its exact tessellation with material finishes. Rough renders are 1100 × 900 at 16 Cycles samples. Sources and outputs are copied back into this project.

Metal-cladding pass: the east roof skin now covers the rafters with a small
provisional outward clearance and 1.5-inch end margins. CAD objects are explicitly
named East metal cladding. The saved Blender scene opens with the cladding on;
the roof-off image remains a separate explanatory view. Panel gauge, seams,
fasteners, flashings and actual assembly thickness are not detailed in this rough pass.
