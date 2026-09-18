# Frame connectivity audit

**122 retained members; all 244 ends accounted for; no unexplained free ends.**

The COMPAS joint graph has 160 nodes in one connected component. Every member has
a geometric route to a declared ground support. This verifies geometric connectivity,
not force transfer, stability, structural capacity or connection detailing.

- 230 connected ends: independent CAD checks find zero gap in a 0.1-inch terminal
  neighborhood at each end, against its declared target members.
- 12 ground-support ends: declared support locations; foundations are unresolved.
- 2 intentional free ends: E-OB extends 2 inches past each end post center.

All 127 preceding frame objects are accounted for. The obsolete east upper brace
is superseded by the mirrored west web, and the duplicated north/east post is
represented by the existing east rear post. Neither is silently omitted from the audit.

## Corrections

Transverse web uprights and hangers now meet their chords. Roof braces terminate on
the current side chords instead of obsolete roof coordinates. Columns meet their
supported members, and timber joists follow their crossbeam supports. West/east
truss geometry retains matching layouts. Sections are concept display envelopes.

## Regeneration checks

Moving the east row 12 inches and raising the square top chord 6 inches each
regenerates attached members with valid connectivity. Floor elevations stay fixed.
Missing joints, out-of-range attachments and an isolated beam end are rejected.
The COMPAS JSON is reloaded and its generated endpoints checked against the model.

## Files

- [Every member end](member-end-audit.csv)
- [Authoritative specification](frame-spec.json)
- [Native COMPAS graph and model](frame.compas.json)
- [Connectivity results](connectivity-audit.json)
- [Independent solid-contact results](solid-contact-audit.json)
- [Editing and regeneration notes](README.md)

## Member inventory

| Group | Members |
|---|---:|
| Bracing | 10 |
| Columns | 9 |
| EastRoofRafters | 12 |
| EastSupportFrame | 4 |
| LoftJoists | 30 |
| LoftSteel | 5 |
| MatchedEastTruss | 10 |
| Truss_Other | 1 |
| Truss_T1 | 9 |
| Truss_TN | 13 |
| Truss_TS | 13 |
| WestMarkupFraming | 6 |

## Current support and bracing revision

S2, S3 and N2 sit directly below the east truss. Both S2–S3 ground cross-braces
are removed at the owner’s request, bringing the explicit retirement count to four.
COMPAS, the viewer, elevations, local CAD and Blender reflect this revision.
All four draft PNGs were refreshed. Blender base meshes were checked against the
current COMPAS scene; source hashes agree.

North top chord revised to a 4 × 4-inch envelope. Shared joint axis retained;
all 244 endpoint checks and 230 connected-end solid contact checks rerun.

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
