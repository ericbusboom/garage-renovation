# Lean-to frame development lineage

This study contains the reconstruction baseline and intermediate output location
for the selected lean-to frame. The source code historically described this
lineage as “S3 removal” because removing the lower S3 column was the first change
explored. It later accumulated the steel door posts, lower W1/W2 removal, roof
rafter corrections, brace reduction, continuous east posts, lean-to rafters,
connection roles, architectural layout, and walkthrough controls.

Those intermediate branches are development history, not separate current
visualizations. The selected visualization is published through
`viz/latest/lean-to-frame-3d.html`. The earlier generated tree is archived at
`archive/20260924.01-viz-cleanup/legacy-structural-analysis/`.

`baseline/column-removal-3d-solid.html` is retained because
`src/structural-analysis-v6/s3_removal_study.py` reconstructs the starting frame
from that saved view before applying the later code-defined revisions. New
intermediate solver output from that lineage belongs in this study's `lineage/`
directory and must not be published directly as the current visualization.
