# Renovated loft geometry

ExistingGarage is hidden as a group. All existing native geometry and all100 steel solids remain unchanged; Existing-Garage.FCStd is untouched.

Deck bottom120, thickness0.75, finished floor120.75. This is0.75 above previous120 reference; unchanged loading header bottom204 gives83.25in finished clear height.

Specified deck south edge y72 is2.25in north of T1 center y69.75, and0.75in south of joist ends/steel north face y72.75. These exact coordinates are retained; a2.25in free cantilever is not asserted.

Joist top120, bottom112.75. Bay ends72.75..182 and188..246 meet steel beam faces. Hangers, bearing, notches and fasteners unresolved; none invented.

Centers begin x0.75 at16in increments; a last closure joist at220.5 ends flush against T-E west face221.25, with11.75in last spacing. Joists run north-south.

Main deck covers x0..224.25, y72..249. First72in of existing garage remain open. West walkway region x-32..0 remains distinct and is not decked.

Deck is the requested rectangular0.75in placeholder. Exact intersections with steel webs/jambs are listed as required deck notches in renovated-loft-parameters.json; notches/edge blocking are not detailed. East closure joist ends atx221.25,3in inside deck edge224.25.

Optional deck x56.25..152.25, y249..271 is hidden. No support members or new columns added.

Only intended member axes and explicit connection offsets exported. No capacity, joist design, material strength, loads, solver or cost optimization run.

The default full/new mesh exports now contain only visible proposed steel, renovated loft deck/joists and reference lines. existing-garage-analysis-mesh.json preserves the107 existing final solids separately. Mesh objects carry group paths, transparency percent and opacity. The optional ledge is isolated in optional-loading-ledge-mesh.json and hidden in CAD.

optimization/cad-analytical-members.json contains exact native construction axes in INCHES. Web endpoints come from original Sketcher profile cap pairs, not mesh PCA. Top chords split where generator roof planes change. All named connections retain their axis offsets; no global snapping or fictitious zero-gap joints. Main/cap axis steps are reported explicitly. Wood joists and floor area are separate from steel members.

Run renovated-loft-generator.py with bundled FreeCAD Python to reproduce from the immutable pre-loft full-frame snapshot; active proposed-overlay-generator.py routes here. No earlier frame generation or structural analysis is executed.
