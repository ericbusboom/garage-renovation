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
- **Outer walls / Roofs:** *Outer walls* closes the building in: white frame,
  light-grey 2 in. panels on the inside of the steel, blue-grey doors, each
  section hover-labelled by face, storey and number (e.g. `WL2`, `NU3`). *Roofs*
  adds the black solar slope, the 18 in. hipped cap with white soffit and
  fascia, and the dark-grey lean-to and shed roofs. `NJ` is the non-structural
  garage-door jamb post between N1 and N2. Source:
  `src/structural-analysis-v6/outer_walls.py`.
- **Status:** current preliminary working visualization; not construction design
- **Generator:** `src/structural-analysis-v6/lean_to_report.py`
- **Layout source:** `src/structural-analysis-v6/cabinets.py`

The analysis lineage and reconstruction baseline are kept in
`studies/20260924.01-lean-to-frame-development/`. Earlier option viewers and the
old nested `s3-removal` output tree are archived and are not current.
