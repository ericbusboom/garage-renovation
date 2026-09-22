# Backyard with proposed hip-cap garage

This proposal starts from the exact `backyard-existing.blend` embedded in the supplied `backyard-blender/Backyard-Blender-Package.zip`, rather than the older approximate garden scene.

The source backyard remains intact except for removal of its existing garage roof. Proposed columns, beams, upper walls, loft floor, balcony and current roof are inserted from `garage-model.json`. Both models use metres, X east, Y north, Z up, with the same southwest garage origin, so no translation or rescaling is applied. The lower garage walls and original work shelter are retained without duplicate geometry.

The rear hip cap rises 18 inches above its eaves with an 8-inch overhang and white soffit/fascia. Proposed structural sizes and connections remain conceptual. The combined model exposes spatial relationships; it does not establish foundations, load capacity or clearance compliance.

## Contents

- `backyard-proposed-hip-cap.blend`: editable Blender scene, with packed baseline photographic textures and named PROPOSED collections.
- Three PNG renders: whole-yard overview, patio toward garage, elevated west.
- `build_proposal.py`: inserts the proposal into the baseline and reproduces all three renders with Blender 5.
- `backyard-existing.blend`: unchanged source scene extracted from the supplied ZIP.
- `garage-model.json`: current proposed garage mesh geometry, materials and dimensions.
- `validation.json`: source hash, removed roof object names, added object count and coordinate basis.

Run `blender -b -t 12 --python build_proposal.py` from this directory. Rendering uses Cycles CPU, 80 samples with denoising, 1800 × 1350 pixels. The original backyard package is preserved separately. The backyard itself remains a reviewed visual reconstruction, with the dimensions and limitations documented in the original package; it is not a survey.
