# Garage model and rendered views

This is a geometry-based model rendered with VTK, not an AI-generated image. All four views share the same geometry. Exterior views hide the conceptual internal truss layer; structural views remove the roof and upper cladding.

## Files

- `01-southwest-exterior.png` and `04-northwest-exterior.png`: finished envelope studies.
- `02-southwest-structure.png` and `03-northwest-structure.png`: framing studies.
- `garage-complete.gltf` / `garage-framing.gltf`: portable 3D scenes with embedded geometry and materials.
- `garage-model.obj` with `garage-model.mtl`: individual mesh objects, including concealed construction.
- `garage-model.json`: named object geometry and design basis.
- `build_and_render.py`: editable Python model and rendering source. Requires numpy, VTK and Pillow, plus the existing project source files referenced in the script.

Exported coordinates are in meters. Model inputs are in inches; X east, Y north, Z up. Origin is the southwest exterior corner of the existing garage.

## Geometry basis

Based on the latest section-and-plan drawings in structural-study. All beam and truss bottom edges use the 98.5-inch wall-top datum; columns carry the proposed framing. Roof underside begins above the trial 8-inch T-SO beam, 63 inches south of the south wall, rises at 30 degrees to 10 feet above the trial loft floor, then reaches the rear cap base. Revision September 8 restores a four-sided shallow hip cap above that rear section, rising 18 inches above its eaves, with an 8-inch perimeter overhang, white soffit and 8-inch fascia. Its ridge runs east–west. The updated section-and-plan drawing includes the hip cap profile, rise, overhang and projected hip lines. Garden renders and the drawing exports are included in this package. A project-source directory includes the dependencies needed to rerun the model and drawing scripts.

T1 and T-S extend to the roof. T-N models the north upper wall and door header. B2 and B3 remain beams. T1 and B2 terminate at T-E. The south six feet inside the existing walls has no loft floor. Cabinets are included without assigning them structural support. The west balcony floor and flat walkway slats are white. Existing outbuilding dimensions are retained, with previously accepted approximate heights.

Member cross-sections, truss webs, roof thickness, joinery and some opening dimensions are illustrative model assumptions, not engineered selections. South support connections remain unresolved in the source plan. This rendering pass does not establish structural capacity or footing sizes. Mesh exports are editable geometry, not native FreeCAD parametric solids.
