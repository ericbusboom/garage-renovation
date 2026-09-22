# Separate truss analysis — Candidate 9

[Point-load drawings and schedules](point-loads/README.md) · [PDF](point-loads/Truss-Point-Loads.pdf)

The updated exports include separate basic load cases for roof, floor, cladding, steel, live loads and individual hoist positions, together with the existing combinations.

Yes: the current model supplies enough information for preliminary connection-load extraction and separate truss analysis. This is a global/local submodel workflow. It does not yet establish verified building loads, fabricated connection stiffness, site lateral loads, or construction adequacy.

## Programs

Run `TE.py`, `TW.py`, `TN.py`, `TS.py`, or `T1.py` with Python, NumPy and SciPy. Add `--stage roof_first` for erection-stage geometry. T1 includes its suspended floor rail and hangers only in the completed stage. B2, columns and perimeter/roof braces remain in the surrounding global frame.

Example on this Mac:

    /Applications/FreeCAD.app/Contents/Resources/bin/python TE.py
    /Applications/FreeCAD.app/Contents/Resources/bin/python T1.py --stage roof_first

Each program independently assembles/solves the exported truss matrix with the global interface movements prescribed and verifies the baseline displacement and force results. It writes signed member end actions to a replay JSON. These are linear-elastic reference submodels; the prior whole-frame P-delta checks remain separate.

The matrix was assembled using the actual member sections and rigid-joint assumptions of Candidate 9, including internal centroid-offset links. It is a three-dimensional frame representation of the truss, not an idealized pin-jointed axial-only model. External braces and columns cut at the truss interface. Changing the connection philosophy requires rebuilding the model.

## Data and sign conventions

Each truss has a JSON geometry/element/case manifest, a compressed NumPy matrix/load/displacement bundle, and a connection-actions CSV for each stage. Units: inches, pounds, pound-inches, radians. Solver vector order: FX,FY,FZ,MX,MY,MZ, and DX,DY,DZ,RX,RY,RZ. Solver axes are X east, Y up, Z north. Node coordinates in the manifest/CSV are separately identified as CAD x east, y north, z up. Do not casually permute moment/rotation axes: use the documented solver basis.

CSV actions are the equivalent net external actions required at each cut node for this truss, INCLUDING any directly applied load at that shared node. They are not isolated connection hardware forces. They act ON the selected truss. Keep every load combination intact; never combine six separately maximized components into a fictitious simultaneous case. Interior load checks compare assembled end actions against original applied global nodal loads. Direct loads along members remain at their real mesh stations, not lumped indiscriminately into truss panel joints.

The replay uses prescribed boundary movements plus interior loads. It does NOT apply boundary forces a second time to those constrained degrees of freedom. The exported forces provide a comparison target and connection-load record.

## Optimization workflow

1. Solve the complete frame for the roof-first and final stages, gravity, equipment, and eventual site-specific lateral combinations.
2. Export signed forces/moments and interface movements for each case.
3. Use a truss-specific program to propose different chords, webs or panel layouts. Rebuild its stiffness and self-weight; preserve interface geometry and explicitly define releases/restraints. Check compression buckling, chord bending, deflection, lateral restraint and connection feasibility, not just axial yielding.
4. Put proposed sections back into the global model; rerun and refresh the exports. Loads redistribute as stiffness changes. Recheck other trusses, columns, anchors, foundations, stability and erection stages.
5. Repeat until the proposed global design passes the defined checks. Count fabrication, joints, transport and erection as well as steel weight. A locally lightest truss need not produce the cheapest building.

The current standalone scripts establish and verify the baseline; they are not automatic optimizers or comprehensive member-design software. Their matrices describe the current sections only. A future local optimizer can use a condensed stiffness matrix for the surrounding frame (a Schur complement) instead of frozen boundary movements. That captures linear elastic redistribution while keeping most of the global degrees of freedom out of the local solve. Rebuild/recheck the whole model for geometry, self-weight or nonlinear changes.

Do not use fixed exported point loads as a permanent design contract unless the actual connections and load path justify that independence. No capacity is credited to the old garage walls here. The modeled 40 psf loft loading, 75 psf storage patches, 1,000 lb hoist plus equipment/impact, roof/solar allowances and diagnostic lateral cases retain the limitations in Candidate 9. Site wind/seismic and final occupancy/loading classification remain unresolved.

Method reference: https://ansyshelp.ansys.com/public/Views/Secured/corp/v252/en/wb_sim/ds_submodeling.html
