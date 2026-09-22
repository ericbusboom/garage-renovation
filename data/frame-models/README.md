# Frame models — the only place for structural COMPAS files

**Every COMPAS serialization of the building structure lives in this directory.**
Nothing else in the project may hold one. If you are writing a script that emits a
full-frame COMPAS model, it writes here, and it writes through
`compas-study/frame_models.py` — never by hand-building a path.

This rule exists because the frame model had drifted into four locations with three
different names, and no one could tell which file was current. There is now one
directory, one naming rule, and a resolver that always returns the newest model.

## Naming

```
frame-<YYYYMMDD>.<NN>-<description>.compas.json
└─┬─┘ └───┬────┘ └┬┘ └─────┬─────┘
  │       │       │        └─ what this version is about, kebab-case
  │       │       └────────── two-digit increment within that date, starting 01
  │       └────────────────── date the model geometry was generated
  └────────────────────────── fixed base name; every canonical model starts with it
```

The version string is `<YYYYMMDD>.<NN>` — the same date-dot-increment scheme used
elsewhere in this project. The increment restarts at `01` each date. Bump `NN`
every time you regenerate on the same day; never overwrite an existing file.

```
frame-20260916.01-square-upper-west.compas.json
frame-20260916.02-square-upper-west.compas.json     second run that day
frame-20260917.01-east-clerestory.compas.json       new date, back to 01
```

Sort order is chronological as plain text, so `ls` and `sorted()` both give you
history in order and `[-1]` is the newest.

## Lineages

The description carries the lineage. More than one may be live at a time — a
variant under discussion does not invalidate the one it branched from.

| Lineage | Description slug | Source script | Status |
|---|---|---|---|
| Connected frame | `square-upper-west` | `compas-study/connected_frame.py` | current |
| Beam scheme | `beam-scheme` | `beam-design/build_frame.py` | current, alternate |
| Coordinated study | `coordinated` | `compas-study/coordinated_study.py` | superseded, retained |

To resolve within a lineage, pass the slug:

```python
from frame_models import latest, allocate
latest()                        # newest model of any lineage
latest('square-upper-west')     # newest of that lineage only
allocate('square-upper-west')   # path to write the next version to
```

`allocate()` picks today's date and the next free `NN`, and refuses to return a
path that already exists.

## What belongs here, and what does not

**Here** — COMPAS serializations of the complete structural frame: the member set,
its joint graph, and the element model.

**Not here:**

| File | Why not | Where it lives |
|---|---|---|
| `west-elevation.compas.json` | one projected elevation, not the frame | beside its viewer in the study dir |
| `T1-*.compas.json` | one truss under parametric sweep, not the frame | `compas-study/output/` |
| `current-frame.compas.json` | display round-trip derived from a canonical model | beside its viewer |
| `scene-mesh.json` | derived display/CAD/Blender export | beside its exports |
| `report/.../coordinated.compas.json` | controlled STR-006 distribution copy | in the issued report |

A report snapshot is a frozen copy issued with a controlled document. It is a
distribution of a frame model, not the model itself, and it is never edited in
place — a new revision means a new report. `publish_report.py` copies the
canonical file into the report under its versioned name.

The test is whether the file is an authoritative description of the whole
structure. A projection, a single member group, or a rendering bundle is an
output of a frame model, not a frame model.

## sandbox/

`sandbox/` is for exploratory COMPAS work — trying a joint scheme, testing a
loader, pulling one truss apart to look at it. Nothing in `sandbox/` is
authoritative, nothing downstream may read from it, and it is not versioned.
Name files there however you like.

When something in `sandbox/` becomes real, promote it: regenerate it through its
build script so it gets a proper version, rather than renaming the scratch file.

## Provenance

| Version | Moved from | Generated |
|---|---|---|
| `frame-20260917.01-beam-scheme` | built from `beam-design/geometry.py` | 2026-09-17 |
| `frame-20260917.01-square-upper-west` | rebuilt from `frame-spec.json` | 2026-09-17 |
| `frame-20260916.01-square-upper-west` | `roof-studies/square-upper-west/connected-frame/frame.compas.json` | 2026-09-16 22:00 |
| `frame-20260915.01-coordinated` | `compas-study/output/coordinated/coordinated.compas.json` | 2026-09-15 21:24 |

The two moved files are byte-identical to their originals; only location and name
changed. `20260917.01` is a rebuild that verified the new write path — its geometry
is identical to `20260916.01`, differing only in the GUIDs COMPAS mints on each
serialization. It is the current version because it is the one the viewer and the
framing elevations were last regenerated against.

The `beam-scheme` lineage is the BEAM-001 alternate design: rolled beams in place of
the truss families, on one plane at the existing wall top. It is a live variant of the
frame, not a replacement for `square-upper-west`, and both lineages resolve
independently through `latest(<slug>)`. Note that `latest()` with no slug returns the
newest model of *any* lineage, so scripts that mean the truss frame must name it.

Section envelopes, contact checks and joint references in these models are
geometric. None of them constitute structural analysis or connection design.
