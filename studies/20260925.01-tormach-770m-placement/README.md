# Tormach placement (770M, then PCNC 440)

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

## PCNC 440 (current direction)

Tormach's space-planning drawing is D35684, "PCNC 440 w Stand and Enclosure":

- **Typical footprint:** 42 × 36 in., 72 in. tall, about 600 lb equipped.
- **ATC:** hangs off the left of the head, so plan 46 × 36 in. to be safe.
- **Console:** mounts on the wall, so no side clearance is needed.
- **Front:** 24 in. for one person, 36 in. for two.

The machine and its 36 in. front zone fit entirely inside the NW pop-out, which has about 69 × 78 in. clear.

**Option 1 (recommended): back on the W3–W4 wall, facing east.**

- **Machine position:** x −31.5 to 4.5, y 219.5 to 265.5.
- **Front zone:** runs east to x 40.5, which is the N1 line.
- **Console:** on the north wall, at the operator's right.
- **ATC side:** faces south into a free strip about 69 × 32 in. along the W3 wall. That strip can take a bench or tooling cart and leaves room to service the ATC.

**Option 2: back on the W4–N1 wall, facing south.**

- **Machine position:** x −31.5 to 14.5, y 229.5 to 265.5.
- **Front zone:** reaches y 193.5, which leaves 6 in. to the W3 wall.
- **ATC side:** sits against the west wall.
- **Spare space:** only a 23 in. strip east of the machine.

In both options the X-brace in the W4–N1 wall stays as it is. The only wall attachment is the console.

## Files

- `draw_440.py` regenerates `tormach-440-popout.png` and `.pdf`: the two 440 orientations.
- `draw_placement.py` regenerates `tormach-popout.png` and `.pdf`: the plan, plus the W4–N1 wall elevation.

  ```sh
  archive/.venv/bin/python studies/20260925.01-tormach-770m-placement/draw_placement.py
  ```
