# Backyard Existing Conditions
## Photo-informed Blender reconstruction — 8 September 2026

### Purpose

Establish an editable representation of the current backyard for evaluating a future garage replacement. This scene represents the existing garage and corrected site arrangement, not a garage proposal. It consolidates the site schematic, aerial image, existing measured garage model, ground-level photographs, and the owner's successive corrections.

### Spatial organization

The garden is organized as four outdoor rooms. On the west are the rear stone patio beside the house and, north of it, the conversation area south of the Airstream. On the east are the low south garden and the jungle to its north. A planted, low lattice fence divides the northern rooms from the southern rooms, with a walk-through gap at the central stone path.

The rear patio is irregular flagstone, with low benches and pots around its edges. The temporary above-ground pool visible in the photographs is deliberately omitted. The conversation area has an open wood-chip surface, a central round metal fire pit, timber-and-metal benches and a chair. It is modeled at the common yard datum; “conversation pit” does not imply a sunken excavation.

The low south garden contains low bushes and a very small central tree. It has no internal path. The larger lime tree is near its north edge beside the walkway, just south of the dividing fence. The jungle has a relatively open wood-chip center, with the camellia, reddish strap-leaf plants and other planting around the perimeter. The former large tree is not modeled as still present.

### Buildings and circulation

The existing garage retains the prior project's geometry: 249.5 in east–west by 249 in north–south; 98.5 in wall height; 60 in roof rise; and an 18 in north–south ridge. Earlier project documentation identifies the wall length and heights as owner-confirmed; some opening dimensions and roof margins remain provisional. Source garage geometry has been preserved through the site revisions.

The work shelter is west of the garage. Its north end aligns with the garage's north end. Both green rectangular planters remain south of it. The owner established this relationship explicitly: the aerial predates completion of the work patio and does not govern the shelter's current placement. Shelter depth, height and framing are still approximate.

The stone path between the jungle and garage runs straight against the garage's south wall. The central garden path leads through the dividing-fence gap onto the rear patio. A second route runs under the white pergola and continues uncovered all the way to the patio beside the low south garden. The pergola itself stops approximately 8 ft north of the dividing fence. Posts, beams, slats and climbing vegetation stop with the structure; the path continues beyond it.

The house's stepped north outline and triangular bay follow the original backyard schematic and owner clarification. The bay has glazing on both angled faces. House heights, windows, roof forms and the truncated southern context are approximate; the house is not a measured architectural reconstruction.

### Coordinate and dimensional basis

All scene geometry uses metres, with X east, Y north and Z up. The origin is the outside southwest corner of the existing garage at floor datum. “North” follows the established garage model convention rather than a verified surveyed bearing.

The schematic is scaled to the garage outline: image x=519–818 maps to 6.3373 m; image y=101–411 maps to 6.3246 m. This provides consistent proportions but does not make the schematic a survey. Yard boundaries, distances, grades, furniture positions and plant dimensions remain estimated. Ground is represented as broadly level, with shallow modeled door steps. Fences are visual boundaries, not surveyed property lines.

### Photograph and texture evidence

IMG_4198–4201 established house and garage appearance, flagstone, pots, planting and the shelter. IMG_4210–4214 and IMG_4216–4219 documented the pergola and dense vegetation. IMG_4220–4223 clarified the low south garden and open jungle. IMG_4224–4227 documented the planted fence, patio benches and conversation seating/fire pit.

Six material samples were extracted directly from photographs: flagstone, wood chips, garage stucco, blue-gray house stucco, white painted timber, and weathered fence boards. `textures/manifest.json` records each source image, crop rectangle, processing and assumed world scale. The source crops and processed maps are included.

Processing crops and resizes the photographed surface, partially attenuates broad illumination variation, and mirrors it into a repeating atlas. It does not invent replacement surface imagery. Color textures therefore retain actual photographed appearance, but may also retain shadows, reflections and camera processing. Mirrored motifs may be visible at close range. These are practical material samples, not calibrated reflectance measurements.

Bump maps are derived from image luminance; roughness maps are neutral estimates with small luminance variation. Neither is physically recovered from the photos. Bump is kept shallow, and no displacement modifies the site's measured geometry. Roof shingles, metal, glass, bench wood and foliage use procedural or manually assigned materials where a clean photographic sample was not available. No fabricated leaf-species identification is claimed; names such as lime and camellia come from the owner.

### Blender implementation

The corrected revision-8 site scene is imported as named meshes and grouped into collections. Coarse plant envelopes are replaced by individual procedural leaves while retaining the source planting locations and approximate extents. Photo materials receive world-scale planar UV projection. Small bevels add edge highlights to building and furniture meshes. The reddish strap-leaf plants use tapered curved ribbons. Overlapping paving meshes receive sub-centimetre vertical separation to avoid ray-tracing artifacts; this is a rendering treatment, not an inferred site grade. Cycles lighting uses a blue ambient environment, an approximate afternoon sun and a soft fill for the shaded conversation area; it is not a time-and-location daylight analysis.

All texture images used by the scene are packed into `backyard-existing.blend`. The separate textures and build script are also retained for editing. Rendering runs on the owner's workstation `ros@buzzkill`, in a new directory separate from the earlier proposed-garage render.

### Limitations and next refinements

This is a manual, photo-informed visualization, not a photogrammetric scan, survey, construction drawing or structural design. Its strongest evidence is the garage model and the owner's relative-layout corrections. Its weakest evidence is the yard's absolute spacing, grade, detailed house geometry, foliage volumes and texture calibration.

The most useful measurements for refinement are the garage-to-house distance, yard width, pergola width/height/length, fence position and gap width, and shelter depth. A straight-on photograph with a scale reference would improve each major surface sample. Those refinements can be incorporated into the same named objects and material library.
