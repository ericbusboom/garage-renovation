# Roof studies for chat review

These two geometric studies replace the existing hip roof with a loft and the
proposed frame. They do not modify `model/garage.FCStd`. CAD transfer is deferred
until the user approves the form.

Open `option-a-four-views.png` and `option-b-four-views.png` for each four-view
sheet, or `roof-options-four-views.pdf` for both pages at full resolution. Each
sheet contains a southwest orthographic perspective, north-up roof plan, south
elevation looking north, and west elevation looking east. SVG versions preserve
vector drafting linework and dimensions with an embedded perspective image.

## Geometric definition

Coordinates use X east, Y north, Z up, in inches. Ground = Z 0. The southwest
outside wall corner is X 0, Y 0. The existing footprint is 249.5 east–west by
249 north–south. Existing wall height is 98.5. Windows retain confirmed 48-inch
sills and 24-inch heights.

Both schemes start at the **south face of the south beam, Y = -23.25 inches**,
1 ft 11¼ in beyond the existing south wall. The roof underside bears at the
beam-top elevation, 106.5 inches. The west lattice extends to the same south
beam line. The dashed line in the plan identifies the south wall underneath
this roof extension.

At the north, the roof, loft floor and new loft north wall extend 6 inches beyond
the existing garage wall, to Y = 255 inches. The north beam outer face is aligned
to this corrected boundary. The ground-floor garage north wall remains at Y =
249 inches. The roof now spans 278.25 inches (23 ft 2¼ in) north–south between
the outer south and north beam faces. Both roof ends follow the frame, not the
existing garage footprint.

Both schemes use a 30° south-facing main roof. The northern 78 inches (6 ft 6 in)
begin at Y = 177 inches, measured from the new north roof/loft wall at Y = 255. The underside height above the loft floor is:

`h(Y) = -0.75 + tan(30°) * (Y + 23.25)`

- A: at Y 177, switch to a shallow plane rising north at 0.25 inches per foot.
  Clearance at the roof break is 114.864 inches; at the rear wall it is 116.489
  inches (approximately 9 ft 8½ in).
- B: continue the 30° plane to Y 255. The rear wall has 159.898 inches of clear
  height (approximately 13 ft 4 in).
- Both have 110.674 inches (approximately 9 ft 2¾ in) of central loft depth at
  or above 8 ft headroom, and 152.243 inches (approximately 12 ft 8¼ in) at or
  above 6 ft, excluding the east hip reduction.

Starting the roof on the beam top raises the entire main roof plane relative
to the earlier wall-start study. The rear cap remains 6½ ft long, but 8 ft
headroom is now a minimum requirement exceeded throughout that zone, not the
exact height at the break. The loft floor now spans to the south wall; the
previous unusable low south tip has been removed. The space between the south
wall and beam remains a roof overhang, not an extension of the enclosed loft.

## Assumed vertical construction dimensions

The new beams have their undersides at the existing wall tops (98.5 in).
An assumed 8-inch beam depth and ¾-inch floor deck place the loft floor at
107.25 inches above ground. The roof is shown as an 8-inch vertical envelope
above its underside. These are drawing assumptions, not designed member sizes
or a specified roof assembly. All vertical dimensions change if these change.

The north roof-top elevations are 231.739 inches (A) and 275.148 inches (B).
The south beam-line roof top is 114.5 inches (9 ft 6½ in) for both schemes.
Dimensions on sheets round to the nearest ¼ inch. Clear heights and roof-top
elevations are distinguished throughout the sheets.

## East roof face

A true planar steep roof face runs along the east edge. Its intersection with
the main solar roof produces the diagonal hip shown on the roof plan. The east
face has its maximum horizontal width, 36 inches, at the north end; it narrows
toward the south. The capped scheme has a second short hip segment beside its
shallow cap. Pitches are approximately 72.9° (A) and 77.4° (B).

A constant-width 3 ft strip with a changing upper-edge height would instead
require a different surface definition or additional facets. The planar
interpretation here is explicit and adjustable. The slope does not establish
reduced loading on the long east beam.

## West lattice and frame

The west outboard post centerline is 60 inches from the existing west wall.
This defines the requested 5 ft roof/lattice run in this study. **It is not a
5 ft clear distance between post faces or an exact beam cut length.** The source
drawing's 7 ft 3¼ in annotation measures a beam between features, so the reference
used for the new 5 ft dimension should be confirmed before fabrication layout.

The source 6-inch-square post footprints and 4-inch beam plan widths are retained
as conceptual dimensions. South and intermediate north–south frame positions are preserved from Canvas 1.
The north row is aligned with the user-confirmed beam outer face 6 inches beyond
the existing north wall; longitudinal members end at that row. Members
that previously went to the outboard west line are shortened to the new line.
Source offsets and apparent connections are not engineered or corrected here.

The user confirmed 2×2 lattice at 6–8-inch spacing. The drawings use 7-inch
center spacing and a conceptual 2-inch-square member section. Each transverse
member rises straight from the outer beam to the west roof edge. Five
longitudinal strings intersect those members. These form an open, non-planar
grid; there is no solid west roof. Pitch varies along the building, reaching
approximately 64.4° (A) or 70.4° (B) near the north. Plants are not drawn so the
roof lines and frame remain visible.

## Scope limits

Solar rectangles illustrate the south-facing roof area, not selected modules,
an installation layout, required setbacks, or output estimates. Gross 30° plane
areas before solar setbacks are about 372 sq ft (A) and 517 sq ft (B).

Loft enclosure, roof support framing, lateral bracing, connections, foundation
locations, and load paths are not designed in these images. Placement at wall-top
elevation does not establish that the existing walls or slab can carry loads.
Power-line elevations/offsets and the east-side fire/setback constraints have
not been evaluated. No clearance distances or compliance are asserted.

## Rebuild

Edit `parameters.json`, then run:

```sh
MPLCONFIGDIR=/private/tmp/garage-mpl /Applications/FreeCAD.app/Contents/Resources/bin/python roof-studies/build_studies.py
```

This uses bundled Python plotting libraries only; it does not open FreeCAD or
save CAD files. The perspective uses a per-pixel depth buffer, while dimensions
and elevations derive from the same roof functions. `measurements.json` records
the computed heights and angles. `option-*-scene.json` preserves drawing meshes
for subsequent rendering revisions.
