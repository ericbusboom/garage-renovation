**SUPERSEDED LOCAL SENSITIVITY — use [final networks](../final-networks/README.md).**

# Connection-corrected truss candidate

[Open native solver diagrams (PDF)](Native-Truss-Networks.pdf)

The explicit network audit and native renderer exposed three missing connections in the prior model. This separate candidate adds:

- TE: a joint between the upper-chord axes at the main-slope/cap transition (1.843 in offset).
- TW: the corresponding upper-chord transition joint (1.843 in offset).
- TN: the east upper door jamb connected to the lower chord, through a 5 in centroid-offset connection. The chord is explicitly split at the new node. This is NOT an added ground column.

These use the existing finite-stiffness offset-link representation; they are proposed connections, not fabrication details. The earlier baseline networks are retained in the parent directory. Two coincident TE numerical offset pairs were also consolidated with their summed stiffness preserved.

Each truss has an explicit `.network.json`, a PyNite `*-results.json`, a native network PNG and a deformed-shape PNG. Completed-stage interactive HTML files are native PyVista scene exports. The geometry displayed is the geometry solved; no connection elements are omitted.

All 350 cases are solved for this local candidate. Equilibrium is checked after each solve. Original global-frame interface displacements are imposed, so the three corrected trusses may have different interface reactions. This is a valid local sensitivity analysis, NOT a newly equilibrated whole-building design. Refresh the whole-frame model with these connections before optimizing or adopting sections. The floor, roof, hoist, lateral-load and connection-detail limitations of the study still apply.

Run from the garage root with the supplied environment:

    optimization/.venv-network/bin/python optimization/network-analysis/run_corrected.py

The parent README contains the research comparison and installation instructions. `correct_connections.py` reproducibly generates this candidate's network files from the audited baseline. It records every connection correction and rechecks graph connectivity.
