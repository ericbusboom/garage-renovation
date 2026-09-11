# Final connected-network analysis

[Open the native solver diagrams (PDF)](Native-Truss-Networks.pdf)

Interactive networks: [TE](TE-complete-interactive.html), [TW](TW-complete-interactive.html), [TN](TN-complete-interactive.html), [TS](TS-complete-interactive.html), [T1](T1-complete-interactive.html).

The trusses are represented as explicit node/element networks. PyNiteFEA reads their geometry, sections, restraints and loads, solves them, and its native PyVista renderer draws that same model. Connection-offset elements are included.

Three proposed joint corrections were made in the WHOLE-FRAME model before exporting these networks: connect the TE and TW upper chords at the roof-slope transition, and connect the TN east upper jamb to the lower chord. There is no added ground column. Two coincident numerical TE offset pairs were combined with their summed stiffness preserved. No steel member sizes or beam positions were changed.

The complete whole-frame model and the roof-first model were rerun, and fresh connection actions/movements were generated. These final submodels use those updated results. They supersede the original baseline and the intermediate `connected-candidate` local-only sensitivity model.

## Files

- `*.network.json`: human-readable explicit nodes, element endpoints, sections, loads, reference movements, connection identities and graph audits.
- `*-results.json`: independently computed displacements, interface reactions and member forces for each case.
- `*-network.png` / `*-deformed.png`: native solver screenshots; displacement magnification is labeled.
- `*-interactive.html`: native PyVista scene export for rotation/zoom.
- `run-validation.json`: comparison of independent truss solves against the refreshed whole-frame model.

Ten stage-specific networks and 350 cases are solved. These are 3D beam-column representations of the trusses, including bending and torsion, rather than axial-only ideal trusses. Each network must have one connected component, no unreferenced nodes, no zero-length or duplicate edges, and no unplanned automatic subdivisions. The remaining free ends are boundary endpoints or chord overhangs, not the three corrected joint gaps.

Interface restraint symbols represent movements imposed by the surrounding frame. They are not additional ground supports. Interface reactions are not applied twice as loads. As sections or topology change, refresh the whole-frame analysis again.

## Run

In the shared project, run the supplied `run_final_networks.py` from the parent directory using the garage `.venv-network` Python environment. In the standalone ZIP, create a Python environment, install `requirements.txt`, and run:

    python analyze_network.py

To analyze one model:

    python analyze_network.py TE-complete.network.json

`--no-images` runs numerical analysis without graphics.

## Engineering limits

This is a preliminary analysis under the documented study load assumptions. Numerical offset elements represent proposed joint behavior, not completed weld/bolt/gusset details. Site wind/seismic, occupancy load classification, foundations, lateral restraint, connection design and construction-stage engineering remain to verify. No old-wall capacity is credited. The node-network fix does not by itself approve construction or optimize the steel sizes.

Tool research: [PyNite visualization](https://pynite.readthedocs.io/en/latest/rendering.html), [OpenSeesPy/OpsVis](https://opsvis.readthedocs.io/en/latest/), [Frame3DD](https://hpgavin.github.io/frame3dd/web/Frame3DD-manual.html). PyNite was selected for its existing-model compatibility, beam-column behavior and native model/deformation visualization.
