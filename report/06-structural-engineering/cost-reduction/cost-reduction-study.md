# STR-008 — Frame cost reduction study

**Revision:** 3 · **Date:** 2026-09-18 · **Status:** `draft` · **Section:** 06 Structural engineering
**Scheme analysed:** BEAM-001, `frame-models/frame-20260920.01-beam-scheme.compas.json`
**Live load:** 100 psf (DEC-014) · **Wind:** 96 mph, Exposure C · **Code:** 2022 CBC / ASCE 7-16
**Rates:** `EW-TRUSS-PROCUREMENT.md` §3 and `COST-ESTIMATE.md` §D/§E, via `structural-analysis-v6/cost.py`
**Interactive models** — both switch colouring between utilisation, recommended
action, removability and what governs:
[**cost-reduction-3d-solid.html**](cost-reduction-3d-solid.html), every member
extruded at its actual cross-section so relative sizes are readable, and
[cost-reduction-3d.html](cost-reduction-3d.html), the lighter line version.
Green removes, red enlarges, blue re-sections, grey stays.
**Plan:** [frame-plan.png](frame-plan.png) — every member named and dimensioned,
openings hatched; [frame-plan-stair-middle.png](frame-plan-stair-middle.png) is
the superseded arrangement, kept for comparison (§10).

> Preliminary engineering study. Not a quotation and not a construction document.
> No connection, base plate, anchor or foundation is designed or checked.

> **Revision 3** adds the second north-wall post (§11). **Revision 2** adopted the
> owner's stairwell move (§10) into the drawn model.
>
> **Revision 1 corrects revision 0.** Revision 0 proposed deleting 33 of 54 floor
> joists. That was a defect in the deck-span check, not a finding — it would have
> left one shelf with no framing at all and a 128 in. gap in a loft bay. **No floor
> joist can be deleted.** See §3 and §13. The saving falls from $7,220 to $5,630.

---

## 1. The finding that reorders everything else

**Optimising this frame for weight optimises the cheapest thing in it.**

| Cost driver | Rate |
|---|---|
| Steel material | $0.77–0.94/lb — **1,000 lb is worth about $850** |
| Shop fitting and welding | 0.20–0.35 hr per joint at $80–110/hr — **$16–39 per joint** |
| Field-bolted connections | $40–80 each |
| Erection, per piece | $55–95 |
| Procurement and stocking | $150–400 per **distinct section** |
| Shop fabrication minimum | $10,000–18,000 as a job charge |

So the quantities that move money are **pieces, joints and distinct sections**. The
project's own procurement note reached this independently:

> *"A truss that saves 180 lb of steel (worth about $130) while adding 46 joints
> (worth $736–1,794) is a worse buy, and no amount of steel price movement closes
> that gap."* — `loft-span-study/cost.py`

## 2. Four strategies, all verified by re-analysis

Each option below was re-solved against every governing load combination and
checked for strength, span deflection **and** wind drift before being counted.

| Option | Steel | Pieces | Joints | Sections | Cost (mid) | Change |
|---|---:|---:|---:|---:|---:|---:|
| As drawn | 9,718 lb | 73 | 135 | 11 | $32,202 | — |
| Adequate — 3 members enlarged | 9,776 lb | 73 | 135 | 13 | $32,826 | +$624 |
| **Adequate, 46 pieces removed** | 8,860 lb | **60** | **108** | 12 | **$27,035** | **−$5,167** |
| Adequate, 46 sections lightened | 7,123 lb | 73 | 135 | 17 | $30,115 | −$2,087 |

**Removing pieces saves two and a half times what lightening sections saves — while
removing a third as much weight.** 860 lb removed beats 2,653 lb shaved, because
deleting a member deletes its joints, its handling and its erection, and thinning a
member's wall deletes none of those. Lightening also *adds* distinct sections
(11 → 17), which costs money at $150–400 each.

These two are alternatives, not additions. They compete for the same margin: after
lightening, the frame sits at DCR 0.99 and drift H/405, and nothing further can be
removed. **Remove first.**

## 3. What can be removed — steel only, no joists

**14 steel members, 935 lb**, verified together at max DCR 1.00 and wind drift H/409.

| Member | Why it can go |
|---|---|
| `BW` | West edge beam; the deck reaches the columns without it |
| `CT.mullion.1`–`4`, `CT.diag.E` | Clerestory frame members surplus to the structure |
| `E.rear.brace`, `E.square.brace`, `W.square.brace` | Redundant with the remaining bracing |
| `BR-NU-2`, `BR-W-1` | One diagonal of an X-pair; the other carries both directions |
| `RE-N`, `RE-S`, `RF @ 170.58` | Rafters within the spacing the panel already spans |

`CT.mullion.5` was tested and **rejected** — it pushes the frame to DCR 1.01.

12 members are **critical** — deleting any one leaves a mechanism. 14 more are
required to keep the rest within capacity.

### No floor joist can be deleted

The joists carry the deck, and the deck is not in the structural model. Tested
one at a time against the 23/32 in. OSB span of 24 in., measured across each deck
including out to its framed edges:

| Deck | Joists | Spacing | Can any single joist go? |
|---|---:|---:|---|
| loft bay 1 | 12 | 16.0 in. | **No** — any deletion opens ~31 in. |
| loft bay 2 | 12 | 16.0 in. | **No** |
| loft bay 3 | 15 | 15.3 in. | **No** |
| shelf SH-E | 2 | 12.0 in. | **No** |
| shelf SH-W | 5 | 14.8 in. | One edge joist only, against a rim — not recommended |
| shelf SH-M | 8 | 14.2 in. | One edge joist only, against a rim — not recommended |

At 15.4 in. centres, removing one joist doubles the span to about 31 in. There is
no deletion that lands inside 24 in. **Fewer joists is only available by
re-spacing with a deeper joist — §5, not §3.**

## 4. Fewer distinct sections — the cheapest change of all

Collapsing to one section per structural role:

| | Sections | Steel | Cost (mid) |
|---|---:|---:|---:|
| As drawn | 11 | 9,718 lb | $32,202 |
| One per role | **5** | 9,899 lb | **$30,783** |
| Change | **−6** | **+181 lb** | **−$1,419** |

| Role | Members | Single section |
|---|---:|---|
| Columns | 14 | HSS5X5X3/16 |
| Rafters | 15 | HSS3-1/2X3-1/2X3/16 |
| Truss | 11 | HSS3X3X3/16 |
| Clerestory | 9 | HSS3X3X3/16 |
| Bracing | 8 | HSS2-1/2X2-1/2X1/8 |

**Adding 181 lb of steel saves $1,419**, and the frame gets safer doing it — worst
utilisation falls from 0.98 to 0.77. Verified: stable, no deflection violations.

## 5. Joist spacing

The joists were never sized by structure. At 100 psf they run at DCR 0.19–0.58 and
deflect L/960 against an L/360 limit.

| Option | Joists | Worst DCR | Deflection | Cost Δ | Deck required |
|---|---:|---:|---:|---:|---|
| 2×8 @ 15.4 in. as drawn | 54 | 0.58 | L/960 | — | 19/32 in. OSB |
| 2×8 @ 30.8 in., delete alternate | 32 | **1.02 ✗** | L/539 | −$1,210 | 1⅛ in. OSB |
| **2×10 @ 24 in., respaced** | 36 | 0.57 | L/1369 | **−$990** | 23/32 in. OSB |
| 2×12 @ 32 in., respaced | 29 | 0.60 | L/2004 | −$1,375 | structural panel |
| 2×12 @ 48 in., respaced | 22 | 0.86 | L/1388 | −$1,760 | steel deck + topping |

Two things constrain this. You cannot simply delete alternate joists — a 2×8 at
30.8 in. goes to 1.02. And **the deck governs, not the joist**: every option past
24 in. forces a more expensive deck that consumes most of the saving. NDS also
withdraws the 15 % repetitive-member factor beyond 24 in. centres.

Realistic joist saving: **about $1,000**, and it is now the *only* route to fewer
joists — §3 can remove none. It is additive to the §8 package rather than
overlapping with it, but it needs its own verification run before being counted.

## 6. Where the money is not

- **Weight.** 1,000 lb is $850. It is the last thing to optimise.
- **The clerestory mullions.** Five verify as removable structurally, but they
  carry glazing. Their spacing is set by the glass, not by this analysis.
- **The fabrication minimum.** $10,000–18,000 is a job charge. Below some size,
  making the frame smaller does not make the invoice smaller. Three San Diego
  shops should be quoted before any of these reductions are treated as money.

## 7. Scheme comparison

| | Steel | Pieces | Joints | Sections | Cost |
|---|---:|---:|---:|---:|---:|
| BEAM-001 beam scheme | 9,718 lb | 73 | 135 | 11 | $22,948–41,456 |
| Truss scheme (`square-upper-west`) | 5,825 lb | 100 | 186 | 15 | $21,779–41,165 |

**The beam scheme uses 67 % more steel for the same money** — 27 fewer pieces,
51 fewer joints, 4 fewer sections. This is the project's own procurement thesis,
reproduced from the structural model rather than from a rule of thumb.

## 8. The two changes together — verified as one package

§3 and §4 were each verified against the adequate frame **on their own**. Applied
together they are not automatically valid, and they are not: deleting 46 members
redistributes force into the very members the five-section palette has just
standardised, and the naive combination lands over capacity.

Reconciled (a handful of members stepped back up a size), the package verifies:

| | As drawn | Recommended package | Change |
|---|---:|---:|---:|
| Steel | 9,718 lb | 8,047 lb | −1,671 lb |
| Pieces | 73 | **58** | −15 |
| Fitted joints | 135 | **104** | −31 |
| Distinct sections | 11 | **6** | −5 |
| Cost | $23,028–41,596 | $18,416–32,840 | **−$6,684** |
| Worst utilisation | 0.98 | **0.777** | — |
| Wind drift | H/464 | **H/431** | — |
| Deflection violations | 0 | 0 | — |

These are the current figures, which include the owner revisions carried since
revision 1 — the south slope seated on `B-SO`, the `BE.upper` beam, the east side
rebuilt in wood and analysed as a separate structure, and the stairwell move of
§10 and the second north-wall post of §11. They are larger than the $5,630 quoted
in the revision-1 note above because the east-side rebuild deletes 10 steel
members on its own.

Drift moves the wrong way (H/514 → H/431) and is still well inside the H/400
serviceability target, because the east steel columns that used to stiffen that
wall are gone. That is a consequence of the wood lean-to, not of the stair.

The package is worth more than the sum of its parts as presented in §3 and §4
separately, because removing members and rationalising sections both reduce the
same overheads. The five-section palette:

| Role | Section |
|---|---|
| Columns | HSS5X5X1/4 |
| Rafters | HSS2X2X1/8 |
| Truss | HSS3X3X1/8 |
| Clerestory and bracing | HSS2-1/2X2-1/2X1/8 |

## 9. Recommended sequence

1. **Take the package in §8 as one change**, not as two. Re-verify after any
   deviation from it — the components do not compose safely on their own.
2. **Re-space the joists to 2×10 @ 24 in.** (§5) as a separate change. It is the
   only way to fewer joists; none can simply be deleted.
3. **Do not thin the remaining sections** further. It saves less than removal,
   adds section types, and consumes the margin the package needs.
4. **Quote three San Diego shops** before treating any of this as banked. The
   $10,000–18,000 fabrication minimum may absorb part of it.

## 10. Stairwell moved one bay south — adopted into the model

Owner variant, now the drawn arrangement. The stair sits in the west strip
between `BW` and the inner beams. As drawn it occupied the **middle** of three
bays, y 71–185, so reaching it meant walking the length of the loft. It now
occupies the **south** bay, y 3–128, arriving near the south wall and still
under cover.

Two moves do it:

- **`B-1A` runs west to `BW`** instead of stopping at the inner line, closing the
  strip at y = 128.
- **`B-1` gives up its length west of the inner line** (3 segments), opening the
  strip at y = 71.

The deck follows: the shelf gives up its west end, and the strip from y 128 to
185 — the old stair's north half — is decked as `west strip infill`.

### Verification

Both arrangements were run through the **same** pipeline — same owner revisions,
same removals, same five-section palette, same reconciliation loop — so the two
columns are comparable rather than merely adjacent. Reproduce the left column
with `STAIR_SOUTH=0 python make_view.py`.

| | Stair in middle bay | **Stair south (adopted)** |
|---|---:|---:|
| Adequate | yes | **yes** |
| Worst utilisation | 0.754 | **0.777** |
| Wind drift | H/441 | **H/431** |
| Deflection violations | 0 | **0** |
| Steel | 8,002 lb | **8,002 lb** |
| Pieces / fitted joints | 58 / 104 | **57 / 102** |
| Cost (mid) | $25,551 | **$25,382** |
| Before-demo members | 50 up, 62 wait | **50 up, 61 wait** |

**The move is free, and the splice it removes pays a dividend.** Steel is
identical to the pound, because `B-1A` gains exactly the length `B-1` gives up.
Utilisation rises 0.754 → 0.777 and drift falls H/441 → H/431, both small enough
to sit inside the reconciliation's own step size, and the governing members are
unchanged — `N2` and `S3` under 1.2D+1.6L, neither of which touches the stair.
One piece and two fitted ends come out with the `BWI` splice below, worth $169.

### `BWI-2` and `BWI-3` become one beam

`BWI` was split at y = 71 because `B-1` crossed there and carried on west to
`BW`. `B-1` stops at this line now, so the splice was left sitting in the middle
of the **free edge of the stair opening** — the last place to put one.

The two merge into a single `W12X16` running the full **182 in.** from `B-S` to
`B-2`. The node stays, because `B-1` still frames into the side of the beam;
what goes is the splice, and with it one piece and two fitted ends. The
continuous beam deflects L/814 over the opening.

### The vacated bay is framed, not just decked

The strip from y 128 to 185 — the old stair's north half — becomes floor.
Declaring the `west strip infill` deck is not the same as framing it: with
nothing underneath, the tributary machinery hands that floor load straight to
the four beams around it, they carry it, and the frame verifies over a bay with
nothing for the sheathing to land on. **That is the §13 blind spot exactly, in a
new place.**

Two 2×8 DF-L No.2 joists now span the 57 in. from `B-1A` to `B-2`, on the same
x stations as the bay immediately north (x = −18.66 and −3.31) so the lines run
through across `B-2` rather than stopping and restarting a few inches over.
Measured out to the framed edges of the strip — the fix §13 had to make three
times before it stuck — the widest gap is **15.4 in.** against the deck's 24 in.
span:

| Station | −34.0 (`BW`) | −18.66 | −3.31 | 3.75 (`BWI-2`) |
|---|---:|---:|---:|---:|
| Gap to the next | 15.34 in. | 15.35 in. | 7.06 in. | — |

`_check_deck_span` in `owner_revisions.py` raises if that ever exceeds 24 in., so
the bay cannot quietly go back to being decked but unframed.

The before-demolition stage nets one member: two deleted shelf joists out, two
infill joists in, and one beam absorbed by the merge.

### The number to watch

`B-1A` now spans the full **245.5 in.** instead of 207.75, and it becomes the
softest member in the floor:

| Beam | Middle bay | **Stair south** |
|---|---:|---:|
| `B-1A` | 207.8 in. · L/574 | **245.5 in. · L/334** |
| `B-2` | 245.5 in. · L/372 | 245.5 in. · L/387 |
| `B-1` | 245.5 in. · L/376 | 207.8 in. · L/523 |
| `BE` | 331.0 in. · L/780 | 331.0 in. · L/780 |

The two beams trade places: `B-1` was the long one and is now the short one.

L/334 passes the L/240 total-load floor limit with room to spare and is not a
violation. It is softer than anything in the middle-bay arrangement (worst
L/372), because `B-1A` carries the wider of the two strips over the longer
span. It is recorded because it is the member to deepen if the bay is ever
wanted stiffer underfoot, and because nothing else in the floor is close to it.

### Two joists came out with it

`shelf SH joist 1` and `shelf SH joist 2` spanned from `B-S` up to `B-1`.
Cutting `B-1` back left their north ends in mid-air — the eigenvalue solver
flagged them as unstable nodes before any drawing would have. They stand inside
the new stair opening in any case, so they are deleted rather than re-supported.

This is the same class of error as §13: the geometry change was drawn correctly
and the consequence two members away was not visible in the drawing.

### Opening area

The opening grows slightly, from 29.9 sf to **32.8 sf** — the south bay is the
longer of the two. That is a stair-design input, not a structural one, and the
headroom over the run has not been checked here.

## 11. Second post in the north wall — the loading opening cut to 6 ft

Owner revision. Above the loft the north wall is carried by three posts: `W4` at
x = −34, `N-M` at x = 88.75 and `N2` at x = 211.5. The bay from `W4` to `N-M` is
**122.75 in. of nothing** — the loading opening.

`N-M2` is added at **x = 16.75**, 6 ft west of `N-M`, as that post's twin: same
`HSS4X4X1/4`, same group, standing on `B-N` and carrying `R-W4` over the same
120.75 in. The opening becomes the 6 ft the owner wants, and the **50.75 in.
from `N-M2` to `W4` is walled**.

### It costs one post and pays for itself in stiffness

| | Before | After |
|---|---:|---:|
| Worst utilisation | 0.777 | **0.777** |
| Wind drift | H/431 | **H/434** |
| Deflection violations | 0 | 0 |
| Steel | 8,002 lb | 8,047 lb (+45) |
| Pieces / fitted joints | 57 / 102 | 58 / 104 |
| Cost (mid) | $25,382 | $25,628 (+$246) |

Halving a 122.75 in. span of `R-W4` is worth slightly more than the post costs in
utilisation and drift, which is why both numbers move the right way.

### The dead load does not change

`surfaces.py` already models the north wall as **a solid rectangle from sill to
roof** — the loading opening lives in the label, not in the outline. The cladding
over that bay has therefore been carried in every analysis run to date. Walling
it is load the frame was already designed for, and the post is a pure addition.

That is conservative in the right direction, but it should be said plainly: the
model has never taken credit for the opening, so none of the wind or gravity
results above change when the opening closes.

## 12. Limits

Gravity, wind and a seismic screening check only. No connection, base plate, anchor
or foundation is designed. Costs are parametric estimates on this project's own
rates, not quotations; the ranges are wide and the differences between options are
more reliable than the totals. Every reduction here is conditional on the
100 psf live load of DEC-014 and on the concentrated equipment loads of ASM-011,
which remain open.

---

_Generated by `structural-analysis-v6/cost.py`, `spacing.py` and `studies.py` from
`frame-models/frame-20260920.01-beam-scheme.compas.json`._

## 13. Correction history

**Revision 1, 2026-09-18.** Revision 0 reported 46 removable members including 33
floor joists, and a $7,220 saving. The deck-span check that should have caught it
failed three times over, each fix exposing the next:

1. It grouped all 54 joists as **one set** measured across the building, so
   deleting every joist in one shelf did not widen that set's spacing — joists in
   the other decks stood at the same stations. Fixed by keying sets to the deck
   rectangle the model declares.
2. It allowed each set its own as-drawn worst gap as precedent. Across a single
   set that meant the 27 in. walkway between two shelves licensed 27 in. holes in
   the middle of a floor. Fixed by applying that allowance per deck, where it is
   correct, rather than across the floor.
3. It measured only **between** surviving joists, never out to the deck edge, so
   deleting the joists at one end of a shelf left three feet of deck cantilevered
   over nothing while the check read 14.8 in. Fixed by including the framed deck
   edges in the measurement.

The frame solver never objected at any stage, because there are no plates in the
model: with the joists gone the tributary machinery handed the floor load straight
to the beams, and the beams could carry it. Nothing in a bare frame analysis knows
whether there is anything left for the sheathing to sit on. That is the standing
limitation behind this whole study, not a one-off.
