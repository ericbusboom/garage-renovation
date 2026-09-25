# Visualizations

Interactive and generated visualizations are published here as dated releases.
Release directories use the same naming scheme as studies:
`YYYYMMDD.NN-<slug>`.

The authoritative working release is always [`latest`](latest), a relative
symlink that can point to any retained release. Do not infer current status from
the largest version number or newest modification time. The current 3-D frame is:

- [Latest structural frame](latest/lean-to-frame-3d.html)
- [Release notes](latest/README.md)
- [Analysis results](latest/analysis.json)
- [Geometry](latest/geometry.json)

## Revision workflow

Small corrections to the active design regenerate files in the directory to
which `latest` points. A major geometry, analysis, or presentation direction
gets a new `YYYYMMDD.NN-<slug>` directory. Copy only the useful starting assets,
update that release's README and manifest, review it, and then repoint `latest`.

If a new direction is abandoned, leave its numbered directory for history and
repoint `latest` to the selected earlier release. This makes rollback explicit
and avoids treating the numerically newest release as automatically approved.

Keep `viz/` reviewable: one README and manifest per release, the visualization,
and the data needed to understand it. Solver experiments, intermediate options,
logs, screenshots, and development branches belong in `studies/` or `archive/`.
The superseded pre-versioning visualization tree is retained at
`archive/20260924.01-viz-cleanup/legacy-structural-analysis/`.
