# Squared upper west wall — comparison variant

2026-09-16, draft geometry for owner discussion. Builds from east-clerestory without
replacing that variant. The flat west top chord extends forward to the clerestory
front (Y76.0718 in), making a rectangular upper bay between that line and W3.
Its top meets the soffit underside at Z231.25. Matching wall infill replaces the
west triangular gray cheek. The continuous cap fascia and soffit carry through
along that new square edge: 4-in fascia, 4-in front/back soffits and 8-in sides.

For this first interpretation, the rear W3–W4 diagonal rising north is retained;
the opposite diagonal is moved into the new square bay, rising south from W3 to
the clerestory-aligned vertical. The former short intermediate diagonal is removed.
This brace direction is a draft interpretation pending owner feedback.

The roof cap, glazing/solar field, east roof and ground-floor extension walls keep
their previous basis. Member sections and joints are illustrative; this variant
is not structural analysis or a change to controlled STR-006. This specifically
revises the west frame, not the separately coordinated east truss.

CAD: garage-square-upper-west.FCStd and .step. Blender: garage-square-upper-west.blend.
West view: elevations/west-elevation.html, .png, .pdf, .svg and COMPAS snapshot.
The elevation is generated directly from cad-mesh.json, as are the Blender meshes.
Run `.venv/bin/python compas-study/west_elevation.py roof-studies/square-upper-west`
from the project root after regenerating the CAD mesh. See west-markup-revision.json
for exact chord and brace geometry decisions.

## Second marked elevation — 2026-09-16

Preserved owner markup as west-markup-2026-09-16.png. Removed the diagonal from
the clerestory/slope intersection down to the Y0 bottom-chord station and the
short T-W vertical near Y=-21. The clerestory-aligned vertical remains at its
existing station and now has a 4 × 4 inch display section, spanning between the
bottom chord and the underside of the new square top chord. These are geometric
edits; no structural section grade, wall thickness or capacity is implied.

## Matching east and west trusses

The east truss is now generated as an exact reflection of the revised west truss
from X=-34 to X211.5. This includes the square upper chord, two retained diagonals,
4-inch clerestory post and upper portions of the main posts. matching-trusses.json
records every source/copy pair. East rafters regenerate to the mirrored top profile.
The abrupt change from solar slope to square top is retained as geometry for review;
roof junction details remain unresolved. Other framing and lower support positions
still include historical context and require coordination before structural analysis.

Open [the interactive COMPAS frame review](compas/current-frame-3d.html).
North, South, East, West and Top buttons use orthographic cameras on the same
current model; 3D restores the previous rotatable perspective. Cardinal elevations
show their near-side framing dark and other framing pale. The layer selector offers
Frame, West + east trusses, and Roof + walls; ghost existing walls and shared joints
have independent toggles. Switch between member colors and cream/black. Click a
member for its name; Fit view resets pan/zoom for the selected view.

The standalone HTML embeds Plotly and model geometry; no internet is needed.
Rebuild with `.venv/bin/python compas-study/current_frame_view.py`. The viewer
reads connected-frame/scene-mesh.json and round-trips COMPAS meshes plus the joint
graph and specification into compas/current-frame.compas.json. This working viewer
does not overwrite the earlier STR-006 report snapshot or refresh Blender.

## Transverse connections — 2026-09-16

The inherited T-S, T1 and loft transverse members stopped at X189.4791,
about 22 inches inside the current east truss. Their spans now reach X211.5.
T1, its future floor beam and hangers move from Y69.75 to the clerestory
post station Y76.0718 so the cross-truss chords meet the side posts.
The historical transverse meshes are stretched across the corrected span;
member sections remain illustrative. Nine transverse chords/beams are checked
for solid contact with both side frames in crossbeam-connections.json.
These checks establish geometric contact, not engineered connection details.

The truss-only viewer includes the clipped upper west post portions alongside
the west members, matching the east group. All ten displayed member pairs are
checked after COMPAS round-trip for mirrored vertex agreement within 0.000001 in.
Full columns remain available in the frame view.

## Current source: connected COMPAS frame

The current viewer now reads connected-frame/frame-spec.json through the COMPAS
joint-graph compiler, rather than using the parent CAD frame meshes as its source.
See [the connected-frame notes](connected-frame/README.md) for the complete end audit,
explicit retired-member register, regeneration tests and current CAD/Blender exports.
The parent model files remain the preceding variant.
