## Latest revision — fixed-geometry member sizing

Use [member-sizing study](weight-sizing/README.md) and [PDF report](weight-sizing/Fixed-Geometry-Member-Sizing.pdf). Selected primary steel is 5,290 lb (38% reduction). Geometry unchanged; explicit bracing, occupancy and connection limitations apply.

## Previous revision — whole north wall coplanar

Use [aligned north wall](north-wall-coplanar/README.md) and [updated PDF](north-wall-coplanar/Aligned-North-Wall.pdf). TN framing and W4/N1/N2 share north-coordinate 253 in. All36 internal north-wall joints have zero axis gap; TE/TW/TS member geometry is retained.

## Previous revision — W4/N1 ground-brace alignment

Use [north brace alignment](north-brace-alignment/README.md) and [updated PDF](north-brace-alignment/North-Brace-Alignment.pdf). Both lower X-braces now meet the column axes directly; four 4-inch offsets removed. Other physical members are unchanged.

## Previous revision — corrected TN over-door mini-truss

Use [TN door correction](tn-door-correction/README.md) and [updated PDF](tn-door-correction/Corrected-TN-Door-Truss.pdf). Four equal panels meet the header and top chord at common nodes. TE, TW and TS geometry is unchanged from clean-layout.

## Previous revision — simplified truss layouts

Use [simplified layouts and audit](clean-layout/README.md) and [the before/after PDF](clean-layout/Simplified-Truss-Layouts.pdf). Duplicate uprights and superposed upper braces are removed; the revised unique global frame has been rerun. Ground and roof-plane X-brace crossing details remain preliminary.

## Previous revision — ground-supported walls

Use [ground-supported truss views](grounded-walls/README.md) and [the full-wall PDF](grounded-walls/Grounded-Truss-Walls.pdf). TN now has a horizontal top chord. Views include real ground columns; shared columns occur once in the whole-frame network. Earlier outputs below are retained for comparison.

## Previous revision — two upper-chord runs

Use [TE/TW two-chord design](two-chord-design/README.md) and the [updated PDF](two-chord-design/Two-Chord-Trusses.pdf). Both side trusses now have one sloping and one horizontal upper chord. Earlier connected-network outputs below are retained for comparison.

# Earlier connected-network deliverable

Use the [final, globally refreshed connected networks](final-networks/README.md) and [PDF](final-networks/Native-Truss-Networks.pdf). The files in this parent folder are the retained baseline audit. The missing joints documented below have been corrected in the final network variant and the whole frame rerun.

# Truss networks analyzed and drawn by PyNite

[Open the native solver diagrams (PDF)](Native-Truss-Networks.pdf)

Interactive completed-stage networks: [TE](TE-complete-interactive.html), [TW](TW-complete-interactive.html), [TN](TN-complete-interactive.html), [TS](TS-complete-interactive.html), [T1](T1-complete-interactive.html).

## Program research and choice

| Program | Relevant capabilities | Decision |
|---|---|---|
| [PyNiteFEA + native PyVista renderer](https://pynite.readthedocs.io/en/latest/rendering.html) | 3D beam-column analysis; member releases; loads, deflections and member-force diagrams drawn directly from the solver model | Selected. Preserves the bending, torsion and connection-offset assumptions in the existing model and makes the displayed model identical to the solved network. |
| [OpenSeesPy + OpsVis](https://opsvis.readthedocs.io/en/latest/) | Structural solver with model, load, reaction, deformation and section-force visualization | Strong alternative, especially for later nonlinear work. Not required to resolve the current disconnected-looking plots. |
| [Frame3DD](https://hpgavin.github.io/frame3dd/web/Frame3DD-manual.html) | Explicit text input for nodes, members, restraints, loads and prescribed movements; frame/truss analysis | Usable, but PyNite provides a more direct existing-model and visualization workflow. |

PyNite's [member documentation](https://pynite.readthedocs.io/en/latest/member.html) explains its beam-column elements and rotational releases. These models retain moment-connected members, not an axial-only pin-jointed idealization. Roof/floor loading between panel joints and the trolley rail require bending to remain represented.

## Why the previous plots looked disconnected

The old report skipped elements whose physical-member label began with `@`. Those are the actual finite-stiffness centroid-offset connection elements. Showing the separate member centerlines without those connections made the trusses look disconnected. That was a visualization error.

These networks retain every connection. Two coincident pairs of offset segments in TE, created by solver subdivision, are consolidated by summing their stiffnesses. The source IDs and consolidation are recorded. This preserves the baseline response; it does not certify that those numerical links represent a fabricated joint accurately.

## Network files

There is one `*.network.json` per truss and construction stage. They contain:

- Explicit node IDs and coordinates, in the solver's X-east, Y-up, Z-north axes.
- Elements with start/end node IDs, material, section properties, end releases and physical-member identity.
- Explicit connection-offset elements, distinguished from physical steel.
- Every basic load case and combination from the point-load study.
- Applied interior nodal loads and case-specific interface movements from the whole-frame model.
- Reference movements and interface actions for verification; source provenance and graph audit.

`analyze_network.py` builds a NEW PyNite FEModel3D from the JSON, solves it and compares its response to the reference. It does not solve using an exported stiffness matrix. The JSON is an open project schema with a supplied loader, not a proprietary PyNite file format.

The graph audit requires one connected component, no missing endpoints, no zero-length elements, no duplicate edges after the recorded consolidation, and no unexpected implicit subdivisions when PyNite analyzes the explicit network. Degree-one nodes are recorded for review; they can be boundary connection points or member overhang ends and are not automatically treated as missing connections.

## Run

From the garage directory on this Mac:

    optimization/.venv-network/bin/python optimization/network-analysis/analyze_network.py

For just one truss:

    optimization/.venv-network/bin/python optimization/network-analysis/analyze_network.py optimization/network-analysis/TE-complete.network.json

Use `--no-images` for analysis only. The local virtual environment is isolated from FreeCAD's incompatible VTK runtime. For another machine, create a fresh virtual environment and install `requirements.txt`; do not copy the macOS virtual environment to Linux.

## Interpretation

Native PyNite/PyVista images show the actual solved elements and nodes. The deformed image overlays an exaggerated displacement shape (scale labeled). Interactive HTML files are exported by PyVista from those same scenes.

Interface restraint glyphs mean imposed movements from the surrounding global frame, not new ground supports. The resulting interface reactions are not extra applied loads. This is a linear submodel analysis under the existing global stiffness assumptions. Changing truss stiffness requires a new global analysis or a model of the surrounding stiffness.

No sizing optimization or construction approval is claimed. The existing preliminary load basis, connection assumptions, lateral-load limitations and no-old-wall-capacity assumption remain. These plots show the analytical connection network; the numerical offsets still need physical connection design.

## Endpoint finding: TN door jamb

The east upper door jamb (`T-N upper east jamb`) ends at height 120 in with no modeled link to the lower chord at 115 in. It remains connected to the header/top structure, so the whole graph is connected, but its lower end is free. This is preserved and exposed in the native network drawing, not silently snapped to the chord. A jamb-base connection needs to be defined and the global load distribution refreshed before TN optimization. Other recorded free tips include chord overhangs at the roof transition and north/east ends. Graph connectivity alone is not a connection-design approval.

## Completed run

All 10 networks were reconstructed and solved for 350 cases in total. The maximum difference from the global reference was 2.28e-9 in/radian in displacement components and 0.00227 lb/lb-in in action components. Those are numerical replay errors, not engineering safety margins. Full per-case results are in the `*-results.json` files; `member-axial-results.csv` summarizes physical-member axial demands. No frame geometry or stock size was optimized in this pass.
