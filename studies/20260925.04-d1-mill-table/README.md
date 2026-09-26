# D1 (RF-30 mill/drill) with its table

**Status:** in the model (`D1` and `D1-T` in `src/structural-analysis-v6/cabinets.py`).

## Machine and table (owner, 2026-09-25)

- **Machine:** 24 in. wide at the front, 36 in. deep, 72 in. tall.
- **Table:** 50 in. across the front (the sweep of its travel), 16 in. deep and 4 in. thick.
- **Table position:** its underside is 36 in. off the floor, and its front edge is 8 in. back from the machine's front face.

## Why D1 was turned

D1 used to stand broadside, with its front facing east or west. In that position the table runs north–south and hits S3 by 13 in. The gap between the east walkway run (y = 128) and S3 (y = 176) is 48 in., which is 2 in. short of the table in any case.

D1 now faces south onto the east walkway run, with its back against S3's south end:

- **Machine:** x 109.75–133.75, y 140–176. It sits 3 in. west of S3's east face.
- **Table:** x 96.75–146.75, y 148–164. It is 36–40 in. above the deck and stops 1 in. short of the shelving run (x = 147.75).
- **Front:** 12 in. of open deck lies between the front and the walkway (T5/T6).

The table carries no deck load of its own, because D1's 300 lb includes it. The layout guards now let a part overlap its own machine but nothing else. The walkway guard also checks the table.

```sh
archive/.venv/bin/python studies/20260925.04-d1-mill-table/draw_d1_iso.py
```

## Superseded later on 2026-09-25

D1 has moved to the ground floor: back to the west wall, facing east, north of the lathe. It is now in `GROUND_ITEMS` (`_ground_items` in `cabinets.py`), and the loft no longer holds it. `draw_d1_iso.py` reads the loft rows, so it describes the loft position above and fails if you run it now. See `studies/20260925.03-ground-floor-outline/ground-floor-layout.png` for the current position.
