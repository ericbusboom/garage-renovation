# Ground-floor outline for machine placement

**Status:** working study. This is the base plan for deciding where the ground-floor machines go.

The plan is a top-down view of the bottom floor on the renovated envelope:

- **Kept walls:** the existing south, east and west walls (the west wall only south of W3), with their windows and the 32 in. south door.
- **New walls:** the NW pop-out (W3–W4–N1) and the north wall moved out to y = 268.
- **Removed:** the old north wall, which had the 165 in. door, and the old west wall north of W3.
- **North line N1–N2 (171 in.):** its doors and wall are not decided yet.
- **Also shown:** the posts on the slab, the X-braced bays, the stair in the covered west strip, the south lean-to and the shed.
- **Current equipment:** ghosted as dashed outlines.

Clear floor: 236 in. east–west between the old walls, and 260 in. north–south from the south wall to the new north wall.

```sh
archive/.venv/bin/python studies/20260925.03-ground-floor-outline/draw_outline.py
```

## Equipment layout (2026-09-25)

`ground-floor-layout.png` shows the ground floor with the equipment drawn solid. The layout lives in `_ground_items()` in `src/structural-analysis-v6/cabinets.py`:

- **CHEST:** Craftsman tool chest, 26 × 18 × 58. It stands in the niche south of the Tormach, back to the W3–W4 wall, with its south end on the W3 infill wall.
- **West wall, going north from B-S:**
  - **HUSKY:** 46 × 25 × 36.
  - **LATHE:** 57 × 24.
  - **D1:** the RF-30, facing east. Its 50 in. table sweep runs north–south across the front, and the table's south end meets the lathe.
- **WOOD and METAL tables:** 60 × 36 and 48 × 36. They meet on the south door's centre line (x = 127.5), with their south edges 72 in. north of the inside south wall. Their heights are assumed at 36.
- **SAW:** the saw/router unit, 32 × 77 × 38. Its west edge is on the door's east jamb (x = 143.5).
- **SIDE table:** 26 × 32, height assumed 38. It is centred on the saw and runs from the new north wall's inside face (y = 265.5) south to the saw.

`_check_ground` raises an error if any of these overlap each other or the fixed pieces: B-S, the lathe, the Tormach, the laundry and GF-C1–C3.
