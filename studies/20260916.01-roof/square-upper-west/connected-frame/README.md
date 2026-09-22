# Connected frame study

This is the current framing source. `frame-spec.json` declares 122 members using
named joint references, including attachment points constrained to parent members.
It accounts for all 127 frame members in the preceding CAD study: the superseded
east-wall brace and a coincident north/east post are explicitly retired, with reasons.

Run `.venv/bin/python compas-study/connected_frame.py` from the project root to
compile the specification into a native COMPAS Graph and COMPAS Model, generate
member geometry, check every endpoint and verify the serialized result. Then run
`.venv/bin/python compas-study/current_frame_view.py` to refresh the current viewer.
Do not edit mesh coordinates to change framing. Edit the specification's shared
parameters/joint definitions, then rebuild. The one-time migration script is not
part of ordinary rebuilds and would replace manual specification edits.

Connections are geometric relationships, not pin/fixity or fabricated joint designs.
Adding a COMPAS interaction alone does not constrain geometry. This compiler resolves
shared nodes and dependent member attachments first, then regenerates each member.
It rejects missing references, dependency cycles, off-member attachments, unconnected
ends and disconnected components. Unrelated line crossings do not imply a joint.

All 244 member ends are listed in `member-end-audit.csv`. The only intentional free
ends are E-OB's two 2-inch overhangs beyond its end post centers. Twelve ground datum
supports are declared; footing and reaction design remain unresolved. E-M's one-inch
plan offset is retained as an explicit eccentric bearing within the section envelopes.
The timber joists are included in the audit and now follow their supporting beams.

`frame.compas.json` contains the specification, joint graph, and element model with
explicit interactions. `scene-mesh.json` is the derived display/CAD/Blender export;
its enclosure comes from the preceding roof study. Section shapes here are closed
rectangular display envelopes, not the old hollow/rolled stock profiles. Original
section labels are retained as unverified references, not current sizing selections.

`connectivity-audit.json` records full coverage and regression tests: moving the east
row 12 inches or raising the upper chord 6 inches preserves connectivity; deliberately
broken references and detached ends are rejected. `solid-contact-audit.json` independently
checks a 0.1-inch terminal neighborhood at every connected end in exported CAD solids.
These checks establish geometric contact only, not structural adequacy or joint design.

The previous CAD and Blender variants are preserved in the parent directory. Current
exports live here as `garage-connected-frame.FCStd`, `.step`, and `.blend`.
The earlier STR-006 report snapshot has not been replaced.

S2, S3 and N2 now reference east_x and E.bottom directly. The compiler enforces
vertical alignment below that chord, including after east-row parameter changes.

Owner revision: both S2–S3 ground cross-braces are removed and explicitly retired.
Their support columns remain directly below the east truss.

Blender and all four draft views are refreshed for the S2/S3/N2 support correction
and removal of the two S2–S3 ground cross-braces. render-validation.json records
the current source hashes and checks all 379 scene objects, including 122 members.

Owner revision: north top chord is now a 4 × 4-inch envelope, with its existing
axis and shared joint references retained. Original stock label stays in source
provenance; viewer and exports use the current 4 × 4-inch description.

North brace revision: diagonal 8 now spans from the upper east jamb corner to
the lower north-east corner at N2. Diagonal 9 is explicitly retired.

Current north opening revision: a 4-inch center vertical divides the 245.5-inch
north span into two 122.75-inch bays. N1 stops at the Z115 lower chord. The western
half has a continuous opening header at retained Z207, with the existing above-header
web layout redistributed over its full width. BR-N-upper-1 is removed to clear the
opening. Diagonal 8 connects the center top to N2. Clear framing width is 118.75 in;
header section remains the prior 1.5-inch concept envelope, awaiting sizing.
Frame geometry is updated; architectural wall infill and door assemblies retain
the earlier envelope study and require separate coordination to this new opening.

Current revision: north eastern upper bay has full X-bracing, diagonals 8 and 9.
Diagonal 9 is reinstated with a matching 2-inch concept envelope. Their crossing
is not a declared joint; connection detailing remains unresolved. COMPAS, the
viewer, elevations and CAD are current. Blender/rendered PNGs await the blocked
workstation transfer and still show the preceding single-diagonal revision.
