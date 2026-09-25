# R-W1 / B-S bracing comparison

Upper S3 remains connected to BE.upper and B-S. Lower S3 is removed. W1/W2 remain. This is a trial, not a replacement of the selected design.

| Configuration | Max DCR | R-W1 DCR | Brace max DCR | Drift | Deflection failures | Screen |
|---|---|---|---|---|---|---|
| Selected option, no new braces | 0.940 | 0.680 | — | H/410 | 0 | Passes screen |
| Two end-bay X braces | 2.218 | 2.218 | 0.850 | H/409 | 0 | Fails screen |
| Three-bay truss | 2.096 | 2.096 | 0.477 | H/410 | 0 | Fails screen |
| End-bay X braces + larger R-W1 | 1.008 | 0.944 | 0.587 | H/414 | 0 | Fails screen |
| End-bay X braces + larger R-W1 + stronger north brace | 0.944 | 0.944 | 0.586 | H/414 | 0 | Passes screen |

All new members are HSS2-1/2X2-1/2X1/8. End-bay variant has four diagonal members; full truss has six diagonals plus two verticals. Equal bays are 81.833 in. wide and 37.659 in. high. Existing west brace and doubled floor joist are held constant. The final end-bay option additionally increases BR-N-1 to HSS3X3X1/8. Crossings are not connected and diagonals use full unbraced lengths.

The capacity checks retain original R-W1 and B-S unbraced lengths; new in-plane nodes alone are not lateral/torsional restraint. [AISC reference](https://www.aisc.org/media/zvaa5lt4/bracing-for-stability.pdf).

Preliminary comparative screening only. Gussets, welds/bolts, beam local forces, brace offsets at crossings, moment connections and foundations are not designed. The existing wood-check and code-basis limitations remain. Crossed diagonals are independent, pin-ended members, with no midpoint connection or buckling-length reduction. Both compression and tension are modeled; these are not tension-only rods. Connection detailing must establish the assumed force transfer.
