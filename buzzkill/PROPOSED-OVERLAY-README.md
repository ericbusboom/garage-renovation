# Proposed full primary frame

Request PROPOSED-FULL-FRAME-001. Native FreeCAD geometric concept, all sections unverified.

Five primary trusses reuse their original bottom chords. New roof-following top chords are native Sketcher planar profiles and Part extrusions/fusions. Edit the profile sketches for layout; FullFrameParameters controls top depth and web extrusion width. Rerun full-frame-generator.py with the bundled FreeCAD Python to rebuild from the immutable revision003 backup and full-frame-input.json. The active proposed-overlay-generator.py redirects here. Roof changes require regeneration of the profiles; roof outline and columns retain their original spreadsheet expressions.

Future T1 floor beam, B2 and five 2x2 hangers are visible amber. U-E and optional NE-W/NE-E ground posts were removed entirely. N2 and consolidated N1/U-W remain. The east TN jamb is only above floor level. No old analysis was run.

Validation: existing file hash unchanged;107 native existing solids and all retained original proposed shapes preserved; every new solid valid and nonzero; explicit member joins verified; all new members connected to retained frame; both openings tested for zero positive solid intersection; saved FCStd reopened; STEP solid count checked. Collision report uses exact intersections with existing native solids.

- Native geometric correction model. No strength analysis or stability certification was run. All sections remain placeholders.
- TS and T1 diagonals triangulate all panels; longitudinal members include verticals and selected diagonals with rectangular bays. Those bays are NOT represented as stable pin-jointed trusses; frame action and all connections are unresolved.
- Unchanged roof reference has a small height step at main/cap break y122.7624491117621. Top-chord native roof-plane patches preserve that step and overlap vertically at the seam. Fabricated transition/joint detail unresolved.
- Top chords use 6-inch VERTICAL depth (not normal-to-slope section depth), full width6. Exact roof faces maintained; visual sections unverified.
- TN clear x56.25..152.25 z120..204. TW historic approximate opening y186..246 z120..204 retained. No new solids inside either clear volume.
- Consolidated N1/U-W retained unchanged and used as TN west jamb; it overlaps TN across 2.5 inches in y. No second west jamb. East upper jamb begins120, two inches above chord top118 per requested opening-floor reference.
- T1 future beam, B2 and five hangers visible amber but remain after-existing-roof-removal stage. Exact existing collisions reported.
- Webs embed schematically into chord/header solids to guarantee geometric joins. No gussets, bolts, welds, joint stiffness or fabrication details designed.

Mesh schema: millimeters, objects with global vertices/triangles; reference objects use lines as lists of polylines. Full/new meshes include visible future members; future export isolates them. Optional-north export is empty.
