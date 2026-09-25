# Garage Renovation

Working files for the garage renovation, including the controlled report, COMPAS structural data, analysis source, studies, drawings, visualizations, and renders.

| Directory | Purpose |
|---|---|
| `report/` | Controlled project report and document manifest |
| `studies/` | Dated one-off and versioned explorations |
| `data/` | COMPAS and project model data |
| `viz/` | Dated visualization releases; `viz/latest` selects the current one |
| `render/` | Dated Blender and other render packages |
| `plans/` | Approved drawings when available |
| `src/` | Active source code |
| `public/` | Static site for `garage.busboom.org` |
| `archive/` | Retained history and local tooling |

See [archive/reorganization-manifest.csv](archive/reorganization-manifest.csv) for the 2026-09-21 move record. Structural analyses in this repository are preliminary unless signed and sealed by the responsible engineer.

The current interactive frame is always available at
[`viz/latest/lean-to-frame-3d.html`](viz/latest/lean-to-frame-3d.html). Visualization
release directories use `YYYYMMDD.NN-<slug>`; see [`viz/README.md`](viz/README.md)
for revision and rollback rules.

The current large-format concept drawing set is
[`studies/20260924.02-concept-drawing-set/garage-concept-drawing-set.pdf`](studies/20260924.02-concept-drawing-set/garage-concept-drawing-set.pdf).
It combines the current frame and equipment layout with diagrammatic electrical,
Ethernet, dust-collection, and compressed-air routing. Approved drawing packages
will move to `plans/` only after review.
