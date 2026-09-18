# Current garage in the backyard

The scene builder inserts the current connected COMPAS framing and the preceding
roof/wall envelope into the reviewed existing backyard. It retains the backyard's
lower garage walls, openings, landscaping and photographic materials, and removes
only the original garage roof. Input geometry is converted from inches to metres
at the same southwest garage origin; no site translation or rotation is applied.

- `backyard-current.blend`: editable full-detail scene with packed textures.
- `01-patio-to-garage.png`, `02-southwest-backyard.png`: 2400 × 1800 Cycles,
  up to 192 samples, adaptive sampling and denoising.
- `backyard-current.glb`: browser copy with one quarter of the procedural foliage
  leaves and textures capped at 1024 pixels; building geometry retained.
- `index.html`: upright turntable viewer with garage, patio, yard and overhead presets.
- `validation.json`: source hashes and export record.

The browser uses real-time PBR rather than Cycles lighting. Procedural Blender
materials may look different in GLB. The backyard is the existing reviewed visual
reconstruction, not a survey. The north opening's architectural envelope remains
from the preceding roof study; current structural framing includes the new north
bracing and S1 moved clear of the south entry.

Viewer library: Google model-viewer 4.2.0 (Apache-2.0), downloaded from the official
npm package distribution. Camera behavior: https://modelviewer.dev/examples/stagingandcameras/
