# Visualization cleanup archive

Created 2026-09-24 while converting `viz/` to dated, numbered releases.

- `legacy-structural-analysis/` is the complete former
  `viz/structural-analysis/` tree. It includes the old nested S3-removal,
  bracing, door-frame, column-removal, and other generated option outputs.
- `logs/` contains run and rendering logs removed from active `studies/` and
  `render/` directories during the same cleanup.
- `local-environments/` contains two ignored, study-specific Python environments
  removed from the active studies. The maintained analysis environment remains
  `archive/.venv/`.
- `regenerable-packages/` contains ignored ZIP bundles and application backup
  files removed from active data, render, and study directories. Controlled
  report files and deployable `public/` artifacts were left in place.

These files preserve development history. They are not current visualization
entry points and should not be linked from new work. Use
`viz/latest/lean-to-frame-3d.html` for the selected working model.
