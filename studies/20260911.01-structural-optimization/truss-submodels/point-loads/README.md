# Truss point-load schedules

**The old PDF drawings omit connection-offset elements. Use the [native solver diagrams](../../network-analysis/final-networks/Native-Truss-Networks.pdf) instead.** The load data remain the baseline reference; the final networks include three connection corrections and refreshed whole-frame loads.

[Open the PDF](Truss-Point-Loads.pdf)

The five trusses each have a full-precision JSON and a CSV for completed and roof-first stages. JSON contains every case and point; CSV omits only rows whose six components are all below 0.001 in their respective units. Point labels are stage-specific, with original solver node IDs retained. Coordinates and six component units are explicitly labeled.

Basic cases (`basic_Droof`, `basic_Dfloor`, `basic_Dsteel`, `basic_Dwall`, live-load and individual hoist cases) can be combined linearly using the included factors. The basic actions include the whole frame's response to each source, not just direct loads. Keep signed forces and moments together. Do not add service and strength cases together or double-count the basic cases.

**Boundary actions include the required restraint reactions and any directly applied load at the shared node.** Use interior actions as applied loads and interface movements as the boundary conditions for the existing local replay programs. The interface forces are verification targets. They cannot all be applied as extra loads at fixed supports. For free-body analysis the complete vectors balance; boundary modeling for an optimized truss must be updated as discussed in the parent README.

These loads use Candidate 9 with W2 removed and the existing agreed load allowances. The PDF explains those allowances. Actual steel self-weight must be updated when sections change. One operating hoist is modeled, not two simultaneous hoists. The 75 psf storage case and hoist service cases are separate; strength hoist cases combine storage and the hoist. No arbitrary safety factor has been added to already factored cases.

The JSON contains both applied nodal forces and moments, consistent with [PyNite's nodal-load interface](https://pynite.readthedocs.io/en/latest/node.html). Keep the supplied solver axes for forces, rotations and moments.

## Verification

All load combinations were reconstructed from the basic load cases, and each individual truss free body was checked for force and moment equilibrium. Numerical results are in `validation.json`. The independent linear submodel replay is also rerun for all ten models. This verifies extraction/replay, not structural adequacy or final load selection.
