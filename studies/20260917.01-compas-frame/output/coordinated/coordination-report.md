# Coordinated COMPAS floor plan and trusses

Status: geometry coordination draft; unresolved items below. Units inches, X east, Y north, Z up.

## Position decisions

| Member | Position status | Basis |
|---|---|---|
| B-WO | derived from current supports | Outer west beam follows west post row. |
| B2 | derived / west-row correction | Station from W3; continuous reference from far-west T-W to east T-E. |
| B3 | west-row correction / draft endpoints | Y=249 retained; extend to far-west T-W. Distinct from north upper truss Y=269. |
| C-EM | user-requested connection reference | E-M to T-E at column-top Z=98.5; section and joint detail unassigned. E-M retains option B status. |
| C-EN | user-requested connection reference | E-N to T-E at column-top Z=98.5; section and joint detail unassigned. |
| C-ES | user-requested connection reference | E-S to S3 at column-top Z=98.5; section and joint detail unassigned. |
| E-OB | user-confirmed column-top beam | Across E-S/E-N tops, level with truss bottom chords; retain plan end-face extents. 3-inch display envelope only. |
| O2 | absorbed into extended cross-member | Historical west extension now contained within T1; not a separate overlapping beam. |
| O3 | absorbed into extended cross-member | Historical west extension now contained within B2; not a separate overlapping beam. |
| OB1 | historical context only | Outbuilding beam outside proposed frame; elevation/supports not supplied here. |
| T-E | derived from current supports | Axis from N2/S2; ends use T-SO and north row. |
| T-N | draft resized | North upper-wall truss uses W4/N1/N2 row; loft door remains separate from ground door. |
| T-S | west-row correction / draft endpoints | Retain Y=0; extend between far-west T-W and revised T-E. |
| T-SO | draft endpoints / source axis | Y=-64 retained; endpoint X from W1/S2. Source posts remain Y=-66. |
| T-W | user-corrected far-west location | Suspended on the far-west W1-W4 column row, not above the existing wall at X=0. |
| T1 | derived / west-row correction | Station from W2; continuous reference from far-west T-W to east T-E. |

## Open coordination items

- Draft roof retains 30 degrees and old heights, but starts at current T-SO Y=-64. Current roof design is not finalized.
- User correction: T-W is on the far-west column row X=-34. Cross-members now extend to that row; O2/O3 are subsegments of T1/B2, not separate beams.
- Longitudinal web tips are moved to chord axes in the draft; source-baseline geometry remains separate.
- All 13 columns are modeled from floor datum Z=0 to frame bottom Z=98.5 using source plan-symbol sections. East-wall heights are provisional; footing and connection details remain unresolved.
- E-OB sits at Z98.5 with a provisional 3-inch display envelope matching truss chords; section sizing is unresolved. OB1 elevation remains unknown.
- T-W source uprights at Y185 and Y186 are only 1 inch apart with 3-inch envelopes: overlap retained for review.
- T-N loft-door jamb axes X81.5/113.5 give 29 inches between 3-inch faces; source 32 inches is axis spacing.
- T-W source door header gives 81.5 inches from loft floor to underside; source opening height needs coordination.
- Ground-floor N1/N2 bay is 192 inches center spacing / 188 inches between 4-inch symbols, separate from the T-N loft door.
- T-S at Y0 is 2 inches north of S3 at Y=-2; south beam Y=-64 is 2 inches north of the south columns.
- E-S connects to S3; E-M/E-N connect to T-E at Z98.5 as unsized references. E-M retains option B and its 1-inch offset from E-OB.
- Truss 3-inch section envelopes have not been reconciled with the plan outside-face limit at X213.5.
- Mesh validity and geometric connections do not establish structural stability, capacity, connection design or collision-free fabrication.

## Support offsets

| Member | Support | Offset (in) | Interpretation |
|---|---|---:|---|
| B-WO | W1 | 0 | plan coincidence only |
| B-WO | W2 | 0 | plan coincidence only |
| B-WO | W3 | 0 | plan coincidence only |
| B-WO | W4 | 0 | plan coincidence only |
| B2 | W3 | 0 | plan coincidence only |
| B2 | WB3 | 0 | plan coincidence only |
| C-EM | E-M | 0 | plan coincidence only |
| C-EN | E-N | 0 | plan coincidence only |
| C-ES | E-S | 0 | plan coincidence only |
| C-ES | S3 | 0 | plan coincidence only |
| E-OB | E-S | 0 | plan coincidence only |
| E-OB | E-N | 0 | plan coincidence only |
| E-OB | E-M | 1 | offset / connection unresolved |
| T-E | S2 | 2 | offset / connection unresolved |
| T-E | S3 | 0 | plan coincidence only |
| T-E | N2 | 0 | plan coincidence only |
| T-N | W4 | 0 | plan coincidence only |
| T-N | N1 | 0 | plan coincidence only |
| T-N | N2 | 0 | plan coincidence only |
| T-S | S3 | 2 | offset / connection unresolved |
| T-SO | W1 | 2 | offset / connection unresolved |
| T-SO | S1 | 2 | offset / connection unresolved |
| T-SO | S2 | 2 | offset / connection unresolved |
| T-W | W1 | 0 | plan coincidence only |
| T-W | W2 | 0 | plan coincidence only |
| T-W | W3 | 0 | plan coincidence only |
| T-W | W4 | 0 | plan coincidence only |
| T1 | W2 | 0 | plan coincidence only |

## Validation

W2 moved +6 inches in a disposable draft; T1/O2 station, T1 roof height, and both longitudinal truss stations regenerated successfully

All five baseline assemblies match original source vertex sets. All models are saved/reloaded before rendering. Plan and elevation axes agree.
Deliberately invalid member edits, missing graph edges, misaligned east supports and a changed north bay are rejected.
Column solids use Z0 to Z98.5; east-wall heights are provisional. Geometric incidence is not an engineered joint or load path.
