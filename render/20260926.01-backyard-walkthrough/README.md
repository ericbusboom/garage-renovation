# Backyard walkthrough — current building, outer-walls look

The current building from [`viz/latest/lean-to-frame-3d.html`](../../viz/latest/lean-to-frame-3d.html),
as that viewer draws it with **outer walls, roofs and inner walls on**, set into
the reviewed existing backyard (`20260908.02-backyard-existing`). White frame, light-grey
walls, blue-grey doors, near-clear glazing, black solar slope, dark-grey hipped
cap with white soffit and fascia, the BWI stair partition with its mural, and the
cabinet-layout furniture inside. Same origin (the existing garage's outside
south-west corner), x east, y north; the building is converted from inches to
metres and not moved.

- **Open:** `index.html`, served over http (the results server:
  http://localhost:8765/render/20260926.01-backyard-walkthrough/index.html).
  It loads three.js 0.169 from cdn.jsdelivr.net, so it needs a network connection.
- `backyard-walkthrough.glb` — browser copy (quarter of the procedural leaves,
  textures capped at 1024 px). Git-ignored like every `.glb`; rebuild it with the
  command below.
- `backyard-walkthrough.blend` — editable scene, textures packed.
- `walkmap.json`, `walkmap.png` — where you can walk.
- `building-mesh.json` — the building meshes, written by
  `src/structural-analysis-v6/lean_to_report.py` each time the frame viewer is regenerated.
- `validation.json` — base objects removed and clipped, objects added, hashes.

## Walkthrough

Tick **Walkthrough mode**. The keys are the frame viewer's: ↑/W and ↓/S move 6 in.
(18 in. with shift), ←/A and →/D turn 5° (15° with shift), drag to look up and
down, and the mouse wheel changes the field of view. The eye is at 6 ft. Click the minimap to jump
to a spot.

You stay on walkable ground: a 0.44 m wide body must fit entirely on walkable
cells. If the way ahead is blocked you veer, up to 90° either side, and slide
along whatever is in the way. The side that worked last time is tried first, so
you follow a wall instead of jittering against it.

## Walk map

The map is 0.1 m cells over the backyard extent. Nine rays drop from head height
(72 in.) in each cell. A cell is blocked if anything between **18 in.** and head
height is there. Otherwise the highest hit sets the floor height, so paths,
patios, slabs and low beds are walkable. Three details:

- **Building solids:** a ray that starts inside a wall, post or door is caught
  by casting against the building meshes alone. In the full scene a wall's
  bottom face ties with the slab under it.
- **Shrubs:** ground-rooted plants are leaf cards that rays slip between, so each
  also blocks its outline, shrunk 15 % a side.
- **Edges:** the yard's edge counts as a wall.

Overhead canopies above 18 in. at their lowest do not block unless a ray hits leaves.

## What changed in the base scene

The photographic garage walls and old hip roof are removed (the garage floor is
kept). Base objects whose centre falls inside the new building's footprint are
removed. Objects that straddle it are clipped back to its edge. That includes
the north end of the pergola and the shelter roof over the west addition. The
full lists are in `validation.json`.

## Rebuild

```sh
archive/.venv/bin/python src/structural-analysis-v6/lean_to_report.py   # refresh building-mesh.json
scp render/20260926.01-backyard-walkthrough/{build_scene.py,building-mesh.json} ros@buzzkill:~/garage-render/backyard-walkthrough-20260926/
ssh ros@buzzkill 'cd ~/garage-render/backyard-walkthrough-20260926 && blender -b -t 16 --python build_scene.py -- ../existing-backyard-20260908/backyard-existing.blend'
scp ros@buzzkill:~/garage-render/backyard-walkthrough-20260926/{backyard-walkthrough.glb,backyard-walkthrough.blend,walkmap.json,validation.json} render/20260926.01-backyard-walkthrough/
archive/.venv/bin/python render/20260926.01-backyard-walkthrough/draw_walkmap.py
```

The build takes about a minute on buzzkill. Browser lighting is real-time
(hemisphere and sun), not Cycles. This is a visualization, not a survey. The
backyard is the reviewed reconstruction and the building is the preliminary
design.
