# Cabinet frames as columns under BE

**Frame:** 20260918.10, loft live load L100. **Cabinet geometry:** `cabinet-study/cabinet_frames.py` (frames at y = 56, 105, 154, 203, front legs on x = 211.5).

## 1. Variants

| variant | result | max DCR (member) | BE | worst leg | drift | over capacity |
|---|---|---|---|---|---|---|
| recommended frame, no cabinets | **PASS** | 0.777 (N2) | 0.706 | — | H/434 | 0 |
| cabinet frames as they stand | **PASS** | 0.794 (CF3.front) | 0.218 | CF3.front 0.79 (H1-1a combined axial + flexure, Lb 40 in) | H/455 | 0 |
| strengthened frames | **PASS** | 0.636 (R-W1) | 0.177 | CF3.front 0.37 (H1-1a combined axial + flexure, Lb 40 in) | H/547 | 0 |
| strengthened, all 27 combinations | **PASS** | 0.636 (R-W1) | 0.184 | CF3.front 0.37 (H1-1a combined axial + flexure, Lb 40 in) | H/547 | 0 |
| strengthened, S3 cut at the beam | **PASS** | 0.670 (R-W1) | 0.274 | CF1.front 0.48 (H1-1a combined axial + flexure, Lb 40 in) | H/494 | 0 |
| strengthened, S2 cut at the beam | **PASS** | 0.636 (R-W1) | 0.185 | CF3.front 0.37 (H1-1a combined axial + flexure, Lb 40 in) | H/494 | 0 |
| strengthened, S2 and S3 both cut | **PASS** | 0.677 (R-W1) | 0.276 | CF1.front 0.67 (H1-1a combined axial + flexure, Lb 40 in) | H/446 | 0 |
| S2 and S3 cut, all 27 combinations | **PASS** | 0.677 (R-W1) | 0.276 | CF1.front 0.67 (H1-1a combined axial + flexure, Lb 40 in) | H/446 | 0 |

## 2. What BE and its columns do

| member | recommended frame, no cabinets | cabinet frames as they stand | strengthened frames | strengthened, all 27 combinations | strengthened, S3 cut at the beam | strengthened, S2 cut at the beam | strengthened, S2 and S3 both cut | S2 and S3 cut, all 27 combinations |
|---|---|---|---|---|---|---|---|---|
| BE | 0.706 | 0.218 | 0.177 | 0.184 | 0.274 | 0.185 | 0.276 | 0.276 |
| BE.upper | 0.602 | 0.525 | 0.525 | 0.525 | 0.541 | 0.525 | 0.524 | 0.524 |
| B-S | 0.519 | 0.519 | 0.285 | 0.285 | 0.294 | 0.291 | 0.326 | 0.326 |
| B-1 | 0.454 | 0.453 | 0.453 | 0.453 | 0.453 | 0.453 | 0.453 | 0.453 |
| B-1A | 0.602 | 0.612 | 0.611 | 0.611 | 0.613 | 0.611 | 0.614 | 0.614 |
| B-2 | 0.560 | 0.572 | 0.571 | 0.571 | 0.571 | 0.571 | 0.572 | 0.572 |
| C-EN | — | — | — | — | — | — | — | — |
| S2 | 0.235 | 0.213 | 0.150 | 0.150 | 0.198 | 0.026 | 0.031 | 0.031 |
| S3 | 0.775 | 0.487 | 0.477 | 0.477 | 0.445 | 0.478 | 0.464 | 0.464 |
| N2 | 0.777 | 0.331 | 0.327 | 0.327 | 0.383 | 0.324 | 0.306 | 0.306 |

## 3. Footing reactions (LRFD, lb, largest downward load over the strength combinations)

| support | recommended frame, no cabinets | cabinet frames as they stand | strengthened frames | strengthened, all 27 combinations | strengthened, S3 cut at the beam | strengthened, S2 cut at the beam | strengthened, S2 and S3 both cut | S2 and S3 cut, all 27 combinations |
|---|---|---|---|---|---|---|---|---|
| CF1.front.base | — | 4,747 | 5,147 | 5,211 | 8,977 | 5,444 | 10,946 | 10,946 |
| CF1.rear.base | — | 83 | 3,458 | 3,458 | 4,297 | 3,575 | 5,775 | 5,775 |
| CF2.front.base | — | 7,398 | 6,935 | 6,935 | 6,961 | 6,918 | 5,908 | 6,129 |
| CF2.rear.base | — | 114 | 3,663 | 3,663 | 3,829 | 3,722 | 4,124 | 4,124 |
| CF3.front.base | — | 7,829 | 7,292 | 7,292 | 6,809 | 7,293 | 6,385 | 6,385 |
| CF3.rear.base | — | 109 | 3,953 | 3,953 | 3,883 | 3,971 | 3,788 | 3,788 |
| CF4.front.base | — | 5,622 | 5,357 | 5,357 | 5,105 | 5,313 | 5,331 | 5,331 |
| CF4.rear.base | — | 83 | 3,318 | 3,318 | 3,262 | 3,332 | 3,229 | 3,229 |
| N2.base | 20,462 | 10,827 | 10,551 | 10,551 | 11,073 | 10,523 | 10,418 | 10,418 |
| S2.base | 1,520 | 2,614 | 1,658 | 1,838 | 4,538 | — | — | — |
| S3.base | 31,982 | 10,606 | 9,240 | 9,240 | — | 9,365 | — | — |

## 4. Foundations at 1500 psf allowable (service = LRFD / 1.4)

Sized on the **strengthened** variant.

| frame | front (LRFD) | rear (LRFD) | service | pad, 30 in. deep x along wall |
|---|---:|---:|---:|---|
| CF1 | 5,147 | 3,458 | 6,146 | 30 x 20 in |
| CF2 | 6,935 | 3,663 | 7,570 | 30 x 24 in |
| CF3 | 7,292 | 3,953 | 8,032 | 30 x 26 in |
| CF4 | 5,357 | 3,318 | 6,196 | 30 x 20 in |

Strip alternative: 27,945 lb service over 14.3 ft needs a strip **16 in. wide** (continuous under the frame line, one foot past each end frame).

## 5. Notes

- Frame stations, tube gauge, rail levels and the 98.5 in. height are assumptions listed in cabinet_frames.py; none has been measured for this study.
- The front leg is joined rigidly to BE at its station and its top 6 in. stands in for the beam half-depth. A real seat would be a cap plate under the bottom flange.
- Unbraced lengths are taken between nodes where any member frames in, so a bolted rail along the wall counts as a brace point in both directions. That is right for the weak (1 in.) axis and optimistic for the front-to-back axis of an unbraced frame.
- Combinations are the pruned governing set from the baseline unless --full is given; cabinet members could in principle be governed by a combination not in that set.
- Bearing is presumptive (1500 psf). Nothing is known about the slab thickness or the soil; the pads assume the slab is cut out under each frame.
- No connection, base plate, anchor, weld or cap plate is designed here.
