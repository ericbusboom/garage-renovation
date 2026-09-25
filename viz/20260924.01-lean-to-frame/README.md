# Lean-to frame visualization

This is the selected working 3-D view of the garage frame, including the
continuous east posts, steel lean-to rafters, current structural-analysis color
modes, pre-demolition view, cabinet layout, shed equipment, fixed viewpoints,
and walkthrough controls.

- **Open:** [lean-to-frame-3d.html](lean-to-frame-3d.html)
- **Analysis:** [analysis.json](analysis.json)
- **Geometry:** [geometry.json](geometry.json)
- **Connections:** the *Connections* checkbox puts a dot on every physical
  joint, coloured welded / welded-with-pinned-attachments / pinned / pinned
  base. The 2026-09-24 connection audit (`src/structural-analysis-v6/connections.py`)
  joined four places where members touched or crossed without a joint; the
  joint schedule is in `geometry.json` under `connections`.
- **Status:** current preliminary working visualization; not construction design
- **Generator:** `src/structural-analysis-v6/lean_to_report.py`
- **Layout source:** `src/structural-analysis-v6/cabinets.py`

The analysis lineage and reconstruction baseline are kept in
`studies/20260924.01-lean-to-frame-development/`. Earlier option viewers and the
old nested `s3-removal` output tree are archived and are not current.
