# Tormach 770M placement

**Status:** working study; not yet in the 3-D model.

## Machine and clearances

Owner-supplied sizing:

- **Machine block:** 56 in. wide × 49 in. deep × 88 in. tall.
- **Back and left side:** can sit against walls.
- **Right side:** needs 18 in. for the electrical-cabinet door and the console arm.
- **Front:** needs 24 in. for one operator, 36 in. with students.

That makes the footprint 74 × 73 in. tight, or 74 × 85 in. comfortable.

## Location: NW pop-out (W3–W4–N1)

The plan uses the new envelope, not the old garage:

- The NW pop-out is bounded by N1–W4, W4–W3 and the W3 infill wall to the existing building.
- The existing west wall is removed between W3 and the north wall.
- The whole north wall moves out to y = 268.

**Option A (recommended).** The machine's back is against the W4–N1 wall and its left side against the W3–W4 wall; it faces south.

- **Machine position:** x −31.5 to 24.5, y 216.5 to 265.5.
- **Right side:** the electrical cabinet faces east toward N1 and gets the full 18 in. N1 stands in the wall line and does not enter the door swing.
- **Front:** 29 in. clear where it faces the short W3 infill wall (west of x = 0), and 36 in. or more east of x = 0.
- **Height:** 88 in. fits under B-N, whose underside is at about 106 in.
- **Structure:** no bracing changes.

**Option B.** The machine faces east with its electrical cabinet against the W4–N1 wall, reached through a new exterior door.

- The door (about x −31 to −4, 0 to 80 in.) is crossed by both BR-N-1 and BR-N-2.
- It would need a portal frame or a relocated brace, followed by a lateral re-analysis.

## Files

- `draw_placement.py` regenerates `tormach-popout.png` and `.pdf`: the plan, plus the W4–N1 wall elevation.

  ```sh
  archive/.venv/bin/python studies/20260925.01-tormach-770m-placement/draw_placement.py
  ```
