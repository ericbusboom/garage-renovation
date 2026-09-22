# Ground-floor column removal study

**Frame:** STR-008 recommended beam scheme (frame-20260918.10 with the owner revisions, five braces removed, role palette), loft live load L100, wind exposure C.
**Baseline:** max DCR 0.775, wind drift H/434 (limit H/400).
**Method:** each candidate column is cut off at the wall-beam level (z = 104.5). Its footing goes, and so does any brace whose only anchor was that footing. Whatever the column does above the beam stays, standing on the beam. Pass = stable, no member over capacity, no span-deflection violation, drift ≥ H/400.
**Candidates:** S1, SW0, W1, W2 (N1, W3, W4 excluded — walls are built on them). S2 and S3 added on request.

## 1. Columns out, no new bracing

| columns cut | result | max DCR (member) | drift | over capacity | what fails |
|---|---|---|---|---|---|
| SW0 | **PASS** | 0.774 (S3) | H/423 | 0 | — |
| W1 | **PASS** | 0.812 (S3) | H/430 | 0 | — |
| W2 | **PASS** | 0.779 (S3) | H/435 | 0 | — |
| SW0+W1 | **PASS** | 0.802 (S3) | H/410 | 0 | — |
| SW0+W2 | **PASS** | 0.779 (S3) | H/424 | 0 | — |
| W1+W2 | **PASS** | 0.811 (S3) | H/425 | 0 | — |
| S1 | FAIL | 0.775 (S3) | H/398 | 0 | drift only; BR-S-1 lost with S1's footing |
| S1+SW0 | FAIL | 0.775 | H/375 | 0 | drift only |
| S1+W1 | FAIL | 0.815 | H/388 | 0 | drift only |
| S1+W2 | FAIL | 0.779 | H/399 | 0 | drift only |
| S1+SW0+W1 | FAIL | 0.816 | H/341 | 0 | drift only |
| S1+SW0+W2 | FAIL | 0.780 | H/376 | 0 | drift only |
| S1+W1+W2 | FAIL | 0.815 | H/381 | 0 | drift only |
| SW0+W1+W2 | FAIL | 2.522 (B-SO) | H/363 | 3 | B-SO 2.52, BW 1.41: the SW corner hangs |
| S1+SW0+W1+W2 | FAIL | 1.755 (BW) | H/233 | 4 | BW 1.75, W.top 1.41, W.slope 1.25, W3 1.16 |
| S2 | FAIL | 0.959 (N2) | H/367 | 0 | drift; N2 0.77 → 0.96; BR-S-2 lost |
| S3 | FAIL | 1.772 (N2) | H/357 | 2 | N2 1.77, BE.upper 1.09 |
| S1+S2+S3 | FAIL | 5.023 (N2) | H/49 | 80 | gravity collapse of the east line |

Footing loads in the baseline: S2 6,617 lb, W4 5,114, W3 4,611, N1 2,231, S1 1,821, S3 1,755, N2 586. SW0, W1 and W2 carry essentially nothing at the footing, which is why they come out for free.

## 2. Bracing to rescue S1

Every S1 failure is drift alone, from losing the south ground-floor X-brace leg BR-S-1. Two places to put the stiffness back were tried.

**A — X-bracing between B-S (z 104.5) and R-W1 (z 147.4), plane y = 3, under the slope.** HSS2-1/2X2-1/2X1/8.

| variant | result | drift | bracing |
|---|---|---|---|
| S1 + A, end bays | PASS (no margin) | H/400 | 4 pcs, 107 lb, DCR 0.47 |
| S1 + A, all three bays | PASS (no margin) | H/400 | 6 pcs, 169 lb |
| S1 + A, end bays, 3/16 wall | PASS (no margin) | H/400 | |
| S1+W2 + A | PASS (no margin) | H/400 | |
| S1+W1 + A | FAIL | H/390 | |
| S1+SW0 + A | FAIL | H/377 | |
| S1+W1+W2 + A | FAIL | H/383 | |

**B — X-bracing in the solar-slope plane between rafters** (W.slope, RS @ 6.9 … 170.6, E.slope).

| variant | result | max DCR | drift | bracing |
|---|---|---|---|---|
| S1 + B, every bay, HSS2-1/2X2-1/2X1/8 | **PASS** | 0.779 | H/492 | 12 pcs, 585 lb, DCR 0.12 |
| S1 + B, every bay, HSS2X2X1/8 | **PASS** | 0.779 | H/493 | 12 pcs, lighter |
| S1 + B, half-bay X's | **PASS** | 0.780 | H/496 | 24 pcs, 640 lb |
| S1 + B, end bays only | **PASS** | 0.776 | H/481 | 4 pcs |
| S1+SW0 + B | **PASS** | 0.780 | H/470 | |
| S1+W1 + B | **PASS** | 0.816 | H/483 | |
| S1+W2 + B | **PASS** | 0.779 | H/490 | |
| S1+SW0+W1 + B | **PASS** | 0.821 (B-SO) | H/435 | |
| S1+SW0+W2 + B | **PASS** | 0.779 | H/468 | |
| S1+W1+W2 + B | **PASS** | 0.816 | H/467 | |
| S1+S2 + B | FAIL | 1.015 (N2) | H/357 | |
| S1+S3 + B | FAIL | 1.774 (N2) | H/386 | |
| S1+S2+S3 + A | FAIL | 5.04 (N2) | H/48 | |

## 3. Conclusions

1. **SW0, W1, W2:** removable, alone or any two. No other change needed.
2. **S1:** removable with slope-plane X-bracing between the rafters. HSS2X2X1/8 in every bay is enough (braces at 12 % utilisation); end bays only also passes. With it, S1 plus any two of SW0/W1/W2 passes.
3. **All three west columns together:** not removable. B-SO and BW lose their corner support.
4. **S2, S3:** not removable. Either one pushes N2 over; both together collapse the east line. This is gravity, not wind, and bracing does not help.
5. **B-S to R-W1 bracing:** the wrong plane. It reaches H/400 exactly with S1 alone and fails with any second column.

Drift throughout is the wind-only service check at the roof (S5 D+0.6W), governed by the WY− case.

Scripts: `column_study.py`, `south_brace_study.py`, `south_brace_followup.py`. Raw output: `column-study.json`, `south-brace-study.log`, `south-brace-followup.log`.
