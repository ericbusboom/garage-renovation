# Vertical clerestory and forward-extended hip cap

Draft roof-shape variant, 2026-09-15. Develops the east-infill-skylights study.

The six inclined upper glazing panels become vertical panes at the upper edge of
the remaining three solar rows. The cap extends south to their top edge. Its eave
and ridge elevations remain unchanged for this first comparison: Z235.25 and
Z253.25 inches. The cap advances approximately 46.69 inches; vertical glazing is
approximately 26.96 inches high. This preserves the previous solar field rather
than preserving the inclined pane length. Triangular side cheeks close the ends.

The east roof, evenly spaced rafters, and metal cladding are retained. Roof junctions,
flashings, members and glazing modules remain conceptual. Framing context limits
from the earlier study still apply; this is not a structural analysis update.

CAD inputs use inches, FreeCAD/STEP millimetres, Blender metres. X east, Y north,
Z up. CAD and Blender share the same tessellation. See validation.json for exact
geometry dimensions and counts. The southwest image is 04-southwest-draft.png.

Native files: garage-east-clerestory.FCStd and garage-east-clerestory.blend;
neutral solids: garage-east-clerestory.step. Generators and copied coordinated
T-E endpoints are kept alongside them. Previous inclined-glazing variant is
preserved in ../east-infill-skylights/ for comparison.

## Linked elevation review

[West elevation](elevations/west-elevation.html) provides selectable model parts
and numbered discussion callouts. [PDF](elevations/west-elevation.pdf) and
[PNG](elevations/west-elevation.png) provide fixed copies. Generate it from the
current cad-mesh.json with `.venv/bin/python compas-study/west_elevation.py` from
the project root. The COMPAS snapshot and source checksum are saved alongside it.

## North-face correction

Owner correction: the new north face is a single vertical alignment at Y261,
12 inches north of the existing wall face Y249. Rear cladding and opening infill
are moved to that face; rear context framing is fitted inside it and clipped at
the face. The cap north edge is flush with it, removing the prior projecting
upper edge. T-E's rear stations are refitted from Y185 to the revised north end.
This is a roof-study correction; the separately controlled STR-006 model still
uses its earlier north row and needs reconciliation before the next engineering step.

## Fascia and soffit revision — 2026-09-16

The owner requested a 4-inch fascia and at least 4 inches of soffit all around.
The cap now has continuous white fascia 4 inches high, front/rear soffits 4 inches
deep, and side soffits 8 inches deep. Front eave is 4 inches south of the clerestory;
north eave is Y265, while the flush north wall remains Y261. This requested roof
overhang supersedes the earlier flush cap edge, not the wall alignment.

Cap eave and ridge heights remain Z235.25 and Z253.25. Soffit underside and glazing
head are Z231.25, reducing the vertical glazing height by 4 inches. Fascia is
represented with a half-inch thickness and soffit with a quarter-inch thickness
for visualization; attachment, ventilation and flashing details are unresolved.

## Balcony removal — 2026-09-16

Removed the recessed balcony floor, rails, side reveals and balcony door/glazing
with its trim. The former door opening is filled with matching inboard west-wall
metal cladding; the separate small west window remains. The west elevation's
reference 5 now identifies that infill. The requested framing-to-solar-surface
alignment is a separate pending geometry change and is not included in this pass.

## Ground-floor extension walls — 2026-09-16

Added the requested W3–W4 west wall and W3–WB3 return wall from the orange
possible-extension route in floor-plan-setbacks/floor-plan-study-basis.json.
A copy is kept here as floor-plan-basis.json for reproducible CAD builds. W3 is
(-34,185), WB3 (-2,185). The old plan lists W4 at Y269; this study retains the
later owner-directed north face at Y261 and records both values in validation.json.

Wall cladding is placed inside the exposed frame, aligned with the upper west
cladding. It runs from floor Z0 to Z98.5; thickness is a visualization allowance.
The exterior X-bracing remains. These two requested wall segments are modeled;
this does not fill in or adopt the entire orange enclosure option. Doorways,
wall assemblies, bracing connections and foundations remain to be detailed.

## Marked west-elevation revision — 2026-09-16

Applied the owner's red/green markup: removed the old balcony header, small
header truss, inner rear jamb and two obsolete upper verticals. Added a full
upper W3–W4 X; placed one vertical at the clerestory front (Y76.0718 approximately)
from the bottom chord to the soffit underside; moved the connected diagonal apex
to the new vertical station. Historical posts are clipped to the lower faces of
the sloping/horizontal upper chords so their ends no longer project above them.
The clerestory support intentionally continues above the sloping chord to the cap.

west-markup-revision.json records exact removed names, alignment and trimmed posts.
This change uses provisional visual member envelopes; crossing-brace offsets,
joints and structural behavior are not resolved. The previously requested change
to make chord tops flush with the solar surface is still a separate pending revision.
