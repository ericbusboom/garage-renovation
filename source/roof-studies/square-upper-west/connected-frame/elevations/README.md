# Linked west elevation

Open west-elevation.html to inspect and select named parts; PNG/PDF/SVG are fixed views.
North is left, south right; projection looks east. Units inches; not to scale.

Source of geometry is ../cad-mesh.json, exported by the clerestory CAD generator and
also consumed by Blender. compas-study/west_elevation.py imports it into COMPAS,
round-trips the meshes, and generates these views and the element register. It does
not redraw or independently change building geometry. Run the CAD generator first
when design geometry changes, then rerun this script. A source checksum records the
exact input. This is a mesh projection with object depth ordering, not CAD hidden-line
removal; close overlapping members should be checked in the native model.

Numbered labels 1–7 provide stable discussion topics. W-number selection references
identify objects in this generated revision; their names are retained across rebuilds.
