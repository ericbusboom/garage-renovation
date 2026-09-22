# BEAM-001 — beam-scheme plan

**Revision:** 13 · **Date:** 2026-09-18 · **Status:** draft for discussion

Alternate design that uses **rolled beams in place of the truss families**. This sheet
is the plan only: every specified column, the beam grid, and the existing building
underneath.

- [beam-plan.png](beam-plan.png) — the sheet
- [beam-plan.svg](beam-plan.svg) — same drawing, named groups per layer
- `geometry.py` — the beam-scheme spec; stations derive from the existing building
- `draw_plan.py` — regenerates both outputs

```
/Volumes/Proj/proj/CAD/garage/.venv/bin/python draw_plan.py
```

## Revision 13 — the shelf framed through

Owner direction: the ladder openings go. The plan since revision 2 left two 3 ft
gaps in the south storage shelf — one beside BWI-3, one beside BE — so the owner
could come up from below on a ladder. That is no longer the intent, so the shelf
is now **one deck from BW to BE**, `x` = −34 to 211.5, with joists at the loft
spacing (16 lines at 15.34 in o.c.) and no rims: BW and BE frame its ends.

| | `x` from | `x` to | Width | |
|---|---|---|---|---|
| **SH** | −34 | 211.5 | **20 ft 5½ in** | one deck, BW to BE, joists through |
| **SH-E** | 211.5 | 247.5 | **3 ft** | unchanged; over the lean-to zone, its west edge on BE |

The shelf is now where the storage cabinets, machines and crate go, backed under
the south slope with their fronts on the clerestory line at `y` = 71.
`structural-analysis-v6/cabinets.py` holds the current layout and the true-section
viewer has a **Cabinet layout** button that draws it with clearances. `SHELF_GAPS` is empty and
`verify.py`'s open-gap check is therefore vacuous; the edge and spacing checks
still run on SH.

## Revision 12 — the rafters run straight (correction)

Owner correction, and a fair one: revision 11 broke each slope rafter into two
segments that kinked at R-W1, and wrote the kink off as a modelling convention. That
was wrong — a rafter is one piece and it runs **across the top of** R-W1.

### What made it work

Putting the slope rafters on the **slope chord axis line** does it, because `solar_z`
is a straight line through both of the points they have to reach:

| | |
|---|---|
| Low end | `y` = −63, `z` = 117 — R-SO, the eave |
| High end | `y` = 71, `z` = 194.365 — CT.bottom |
| Run / rise | 134.0 in / 77.4 in — **one straight run at 30°** |

Two members moved so that holds:

- **R-SO drops to `z` = 117**, onto that line, so the rafters frame into it at the eave
  instead of sitting proud of it. S1 follows to 117.
- **R-W1 drops to axis `z` = 147.355**, so its top at 153.355 *is* the rafter soffit.
  The rafters pass over it, touching exactly. It was at 150.548 with its top flush with
  the slope surface, which is where a rafter's top belongs, not a beam's.

The **flat rafters run dead level** at `z` = 225.25 for the same reason: **CT.top drops
to the roof beams' axis** so all three lines it touches — CT.top, R-W3, R-W4 — share one
elevation. Its flange top is then 228.25, three inches under the square chord, which is
where a window head belongs anyway.

`verify.py` now checks straightness directly rather than describing a convention: each
slope rafter's rise over run against `SOLAR_SLOPE` to 1e-9, its soffit against R-W1's
top to 1e-9, and each flat rafter's two ends at equal `z`. 195 checks.

### Section change that follows

A one-piece slope rafter spans the whole **154.7 in rake**, not 76 in, so it goes up:

| | Section | Weight |
|---|---|---|
| Slope rafters, one piece | **HSS3½×3½×⅛** | 5.24 lb/ft |
| Flat rafters, split at R-W3 | HSS2½×2½×⅛ | 3.65 lb/ft |
| R-SO, the eave | HSS3½×3½×⅛ | 5.24 lb/ft |

Ten rafter members became five longer ones, so the count drops from 137 to 127.

**The model ignores R-W1's midspan bearing**, which is conservative: tangency is not a
joint in a line model, so each slope rafter is analysed over its full 154.7 in even
though it physically rests on R-W1 halfway along. Sized that way too. Worst rafter DCR
is 0.29 and nothing in the frame exceeds **W2 at 0.755** — still self weight only.

## Revision 11 — north wall resolved, and light roof framing

### N-M is a second-floor post

Owner correction: **it does not reach the ground.** It now runs `z` = 104.5 → 225.25,
standing on B-N and carrying R-W4 at midspan. It is a hung vertical, not a column, and
takes **no footing** — the support count stays at 14.

### The north wall, both levels

| | Level | Bay | Note |
|---|---|---|---|
| **BR-N** | ground, `z` = 0 → 104.5 | W4 → N1, 74.35 in | the open crane bay is *above* this |
| **BR-NU** | second floor, `z` = 104.5 → 225.25 | N-M → N2, 122.75 in | |

That resolves the question from the last revision: N1 stays where it is at `x` = 40.35,
the ground floor is braced in the W4–N1 bay, and the upper bay west of N-M is left
clear for the crane.

### Light roof framing

Rafters on the **clerestory mullion lines, 40.92 in o.c.**, so the mullions, N-M and the
rafters all share the same five stations:

| | Section | Weight | Span |
|---|---|---|---|
| Rafters, both roof planes | **HSS2½×2½×⅛** | 3.65 lb/ft | 66–114 in |
| **R-SO**, the south eave | **HSS3½×3½×⅛** | 5.24 lb/ft | 179.5 in |

Sized for the project's own metal-roof basis — 5 psf dead (`DEAD['east_roof']`, light
metal panel on exposed rafters) and 20 psf `ROOF_LIVE` — against L/240 and AISC LRFD.
Deflection governs every one of them.

**S1 now reaches the eave** at `z` = 116.69 so R-SO spans 179.5 in rather than 245.5.
Without it the eave needs an HSS5X5X1/8 at 7.6 lb/ft; with it, HSS3½ at 5.2 does. That
is the same trick N-M plays on R-W4 and the mid-width support plays nowhere else — the
cheapest way to keep secondary steel light is to stand something under it.

### The four east lean-to rafters

Owner direction, one from each east-wall post up to the east truss plane:

| | From | To | Rake | Length |
|---|---|---|---|---|
| **RE-S** | E-S | top of S3 | 54.3° | 62.3 in |
| **RE-M1** | E-M1/B | top of E.clerestory | 73.8° | 129.4 in |
| **RE-M** | E-M/B | top of E.W3 | 73.8° | 129.4 in |
| **RE-N** | E-N | top of N2 | 72.2° | 130.5 in |

54 to 74 degrees, which is the range the truss lineage's own east rafters covered.

**These fixed the problem I flagged last revision.** E.clerestory was at DCR 0.952 with
no roof load; RE-M1 now props its head down to the east wall and it has dropped to
**0.455**. E.W3 went from 0.378 to 0.182 the same way. Nothing else in the frame moved
much, and the worst member is now **W2 at 0.743** — the clerestory truss and the rafters
both land on it.

### The axis convention, stated plainly

The primary roof members have their tops flush with the roof surface but different
depths, so their axes sit at different elevations — R-W3 at 225.25, CT.top at 228.25,
W.top at 228.75, all with tops at 231.25. A line model cannot put a rafter on all of
those *and* on one plane. **The rafters therefore run axis-to-axis between the members
they bear on**, which leaves a 3 in kink over 114 in at the clerestory. Real depth
layering — rafter seated on beam, panel on rafter — is a detailing matter this model
does not resolve, and `verify.py` checks only that every rafter end lands on a member
that is not just the next rafter up the same station.

### Two notes

- **R-SO is flagged non-compact.** HSS3½×3½×⅛ at b/t = 28 is marginal against the
  flexural limit. Its DCR is 0.067, so it does not matter yet, but a ⅛ wall at that
  size is at the edge of the table.
- **There is still no roof load in the analysis.** Every DCR above is self weight only,
  and the rafters were sized by the hand check described above, not by the frame run.
  Putting the roof surfaces into `analyze.py` is the next thing that would change any of
  these numbers — along with the hip cap, which is still not framed.

## Revision 10 — north post, cross bracing, clerestory truss

### N-M, the north wall middle post

At **x = 88.75, y = 268** — the exact midpoint between W4 and N2, which is 122.75 in
from W4, or 10 ft 2¾ in. It divides the north wall into two equal 122.75 in bays.

It tops out at **z = 225.25**, on R-W4, not at the square top: there is no east–west
chord at 228.75 on that line, R-W4 is what runs there, and halving R-W4's 245.5 in span
is the structural point of the post. That worked — **R-W4's unbraced length went from
245.5 to 122.75 in, its DCR from 0.116 to 0.064, and its KL/r = 318 slenderness flag
cleared.**

### Cross-braced bays

| | Plane | Bay | Height |
|---|---|---|---|
| **BR-S** | `y` = −63, south row | S1 → S2, 66 in | footings to the beam plane |
| **BR-W** | `x` = −34, west row | W3 → W4, 83 in | footings to the beam plane |

Both are an X in the plane of the wall, HSS2½×2½×3/16, in the `Bracing` group — which
`structural-analysis-v6` pin-releases, as a discrete diagonal wants. BR-W is the same
bay the old west elevation braced as "extension wall W3–W4". Under gravity they carry
almost nothing (0.07 and 0.01); they are there for lateral, which is still not analysed.

### Clerestory truss — replaces R-W2

A vertical truss in the `y` = 71 plane, the full 245.5 in between the truss planes,
from where the slope chords meet the posts up to the square top:

| | |
|---|---|
| Bottom chord | `z` = 194.365, where W.slope and E.slope land on the posts |
| Top chord | `z` = 228.25, flange top flush at **231.25** — level with the square chord |
| Depth | 33.9 in |
| Glazed panels | **6** at 40.92 in |
| Mullions | 5 — and the middle one lands on `x` = 88.75, the same line as N-M |
| End panels | diagonally braced, so those two are spandrels rather than glass |

**The T section.** Two equal-leg angles back to back, stems together: the flange is the
two coplanar legs and faces out, the stem is the two touching legs and points in, giving
the rebate to set glass against. `sections.py` gained `double_angle_tee()`, which
computes every property from the two rectangles rather than transcribing a table — the
areas come out at 4.219 and 1.875 in² against twice the AISC single-angle values of
4.220 and 1.876.

| | Section | Weight | Iz | Compact |
|---|---|---|---|---|
| Chords | **2L3×3×⅜ T** | 14.4 lb/ft | 6.84 in⁴ | yes |
| Mullions | **2L2×2×¼ T** | 6.4 lb/ft | 1.35 in⁴ | yes |
| End diagonals | HSS2×2×⅛ | | | |

⅜ in legs rather than ¼: at ¼ the outstanding leg is b/t = 12 against the 9.15 limit,
so it would be non-compact. ⅜ brings it to 8.

Under gravity the truss is barely working — CT.bottom 0.12, CT.top 0.06 — but it has no
roof or glazing load on it yet.

### Two things this revision surfaced

1. **E.clerestory is at DCR 0.952 with no roof load at all.** 6.5 kip of compression
   over a 124 in unbraced length in an HSS4X4X3/16 — and that ⅛ wall is not a choice
   anyone made, it is what `resolve_section` assigns to a "concept envelope" 4 in tube:
   the lightest standard wall. Either give it a real wall (the old model used
   HSS4X4X1/2 for W3 in the same situation) or put a column under it. It has none — it
   hangs off BE, and both east braces plus the clerestory truss now land on its head.
2. **R-W1 and R-W3 are unbraced over their full 245.5 in**, KL/r = 318 against the 300
   limit. N-M fixed R-W4 by standing under it at midspan; these two want the same, or a
   line of intermediate bracing. That is the next piece of the roof framing.

### Still open

The **8 ft** figure. It is in as an opening *width* question that resolved to the
midpoint, but if 8 ft was meant as the door *height* then the north bay wants a header
at `z` = 96 with bracing above it, the way the old T-N carried a header at 207. Nothing
in the model reflects that yet.

## Revision 9 — W12X16 primary section

Owner direction. Everything that derived from the beam depth moved with it:

| | W14X22 | **W12X16** |
|---|---|---|
| Depth | 13.7 in | **12.0 in** |
| Flange | 5.00 in | **3.99 in** |
| Weight | 22 lb/ft | **16 lb/ft** |
| Beam axis, soffit on the wall top | `z` = 105.35 | **`z` = 104.5** |
| Roof beam axes, tops flush at 231.25 | 224.40 | **225.25** |

`sections.py` gained W12X16 with the same provenance and the same cross-checks as
W14X22: the eleven published properties come from `loft-span-study/wshapes.py`, and
Sy = Iy/(bf/2) = 1.4135 against 1.41, Zy = 2.248 against 2.26, rx = √(Ix/A) = 4.676
against 4.67 all reproduce. J is kept at the published 0.103 rather than the 0.090
thin-walled bound.

### This commits the design to 60 psf

W12X16 was the **60 psf** answer. It does not carry 100 psf on the conservative
reading:

| Live load | Grillage, rigid joints | Simple span between columns |
|---|---|---|
| 60 psf | passes, B-2 at L/484 | **passes**, B-2 at L/468 |
| 100 psf | passes, B-1 at L/476 | **fails** — B-2 at L/281, B-1 at L/352 |

Limit is L/360 on live load. So adopting W12X16 either fixes the live load at 60 psf,
or requires moment connections that actually deliver the continuity the grillage model
assumes. Worth deciding explicitly, because 100 psf was the load the frame was analysed
at two revisions ago.

At 60 psf nothing in the frame is troubling. At 100 psf the grillage says the worst beam
is BE at 0.575 and every deflection is inside — but the bracket says otherwise, and the
bracket is the one that does not assume a connection nobody has designed.

### One member to watch before any roof load

**E.clerestory is at DCR 0.85 carrying no roof load at all** — 6.7 kip of compression
over a 124 in unbraced length in a 4 in tube. It has no column under it; it hangs off
BE, and it is picking up force from frame action as BE deflects beneath it, with
R-W2 and both east braces landing on its head. E.W3, the same condition, is at 0.38.

These two are the east plane's weak point and they will not survive roof load as
drawn. They belong at the top of the bracing conversation.

## Revision 8 — roof beams and a labelled plan tab

### Four east–west roof beams

One across the top of each post that rises above the loft, tying the two truss planes
together at four stations:

| Beam | Station | Axis `z` | Lands on |
|---|---|---|---|
| **R-W1** | `y` = 3 | 150.55 | W1 → S3, under the solar slope |
| **R-W2** | `y` = 71 | 225.25 | W2 → E.clerestory |
| **R-W3** | `y` = 185 | 225.25 | W3 → E.W3 |
| **R-W4** | `y` = 268 | 225.25 | W4 → N2 |

Each spans the full 245.5 in between the planes. Section is the primary beam as a
placeholder — no roof load is defined yet and some of these are to become trusses.

**Owner correction applied:** first drawn with their axes *on* the chord line, which
stood a 12 in beam 6 in proud of the envelope. Their tops are now flush with the top
of the chord they run beside — 231.25 at the square top, and for R-W1 the top of the
raking slope chord at its own station, 156.55. `verify.py` checks that none of them
pokes above its chord.

### Plan tab on the 3D page

[frame-3d.html](frame-3d.html) now opens with two tabs: **3D model** and
**Plan — labelled top view**. The plan is the BEAM-001 sheet inlined into the same
file, so labels, columns, beams, dimensions and the member schedules all travel with
the model. The roof beams appear on it as a pale band behind the floor beam on the
same station, since each sits directly above one, with their own station schedule.

The camera buttons inside the 3D tab are unchanged.

### One builder bug fixed

The crossing test paired every east–west run with every north–south run without
checking they shared an elevation — harmless while the whole frame was one plane, but
it gave each roof beam a phantom joint wherever a floor beam passed beneath it in
plan. 84 spurious joints, now gone: 149 joints and 230 segments.

## Revision 7 — C-EN tie, and the east and west truss planes

### C-EN

E-S reached BE through B-S, and both embedded posts reached it through B-1 and B-2,
but **E-N had no east-west tie** — B-N is at `y` = 268, eight inches north of it. Added
**C-EN** at `y` = 251, `x` = 211.5 → 247.5: 36 in, the same length and the same name
STR-006 gave it.

### The truss planes

The posts now grow past the beam plane to their envelope heights, and each plane gets
the four chord and brace members the previous model carried. **Absolute envelope
heights are preserved** so the elevations read as they did:

| | Now | Previous model |
|---|---|---|
| Square upper chord | `z` = 228.75 | 228.75 ✓ |
| Solar slope start | `z` = 117 | 117 ✓ |
| Solar slope | 30° | 30° ✓ |
| Clerestory station | `y` = **71** | 76.07 |
| North head | `y` = **268** | 259 |
| Bottom chord | `z` = **105.35** (BW / BE, W14X22) | 115 (HSS3½) |

Posts extended: **SW0** → 117, **W1** → 155.11 (up to the slope chord), **W2, W3, W4**
→ 228.75, and on the east **S2** → 117, **S3** → 155.11, **N2** → 228.75. Two verticals
hang off BE at the clerestory and W3 stations — **E.clerestory** and **E.W3** — because
no ground column stands there, exactly as before.

Every one of the four differences above is a consequence of a move already made and
approved: the north wall going 22 in north, B-1 dropping onto the window edge, and the
beams sitting on the existing wall top instead of floating at 115. The clerestory
moving to `y` = 71 puts the vertical on W2 and B-1, which is where it belongs now, and
lengthens the clerestory glazing from 31.46 to 34.39 in.

`verify.py` checks all of it — 91 checks, including that the slope chord passes exactly
through the tops of W1 and S3.

### Bracing: the drawing and the model disagree, and it is yours to settle

The COMPAS model I matched, `frame-20260917.05`, carries **two** braces per plane, a V
fanning up from W3's base — `square.brace` to the clerestory head and `rear.brace` to
the north head. That is what Revision 7 builds.

The west elevation drawing in
[roof-studies/square-upper-west/elevations](../roof-studies/square-upper-west/elevations/west-elevation.png)
shows **more**: an X in the north upper bay rather than a single diagonal, X-bracing in
the W3–W4 extension below the bottom chord, and an X at the south end below it too.
That drawing is 2026-09-16 and the model's own migration notes record the owner
removing ground cross-braces after it — so the model is the newer statement and the
drawing is the fuller one. Which is right is a bracing decision, and it belongs in the
conversation about the rest of the roof.

### Not in the model yet

The **hip cap** (the drawing shows it from 235.25 to 253.25 with a 4 in fascia), the
**solar roof framing**, the **north and south plane framing**, and all roof load. The
truss members currently carry self weight only, so their DCRs mean nothing yet — the
worst, E.slope at 0.43, is a slender 2½ in tube standing in its own weight, not a
result. Nothing over 0.57 anywhere in the frame, but that number does not yet include a
roof.

## Revision 6 — stair opening (correction)

The strip west of BWI-2, between B-1 and B-2, is the **stair opening**. Revisions 3–5
decked it and put joists across it, which was wrong.

| | |
|---|---|
| Opening | `x` = −34 … 3.75, `y` = 71 … 185 |
| Size | 37¾ × 114 in = **29.9 sf** |
| Framed by | BW west, BWI-2 east, B-1 south, B-2 north — all four edges already beams |
| Deck area | 434.8 → **404.9 sf** |
| Joists | 56 → **54** |

Its 114 in length is essentially the `88/sin(50°)` = 114.9 in flight in
[stair-study](../stair-study/draw_stairs_8ft10.py). That study is a west elevation from
the older column lineage, so it carries no `x` extent and I did not pick it up when
building the decks — the loft outline in the plan was the only input, and it says
nothing about openings. Owner correction.

### What it changed

**The "one real finding" of Revision 4 was an artifact of this mistake.** Those two
joists reached DCR 0.88 only because they spanned the full 114 in across what should
have been a hole. With the opening in:

| At 100 psf | Rev 4 | Rev 6 |
|---|---|---|
| Worst joist | 0.879 (west strip) | **0.569** (loft bay 3) |
| Worst beam, B-2 | 0.447 | **0.435** |
| Worst column, W3 | 0.320 | **0.302** |

Nothing in the frame now exceeds 0.57, and the DCR view has no hot member in it at all.

**B-1A stopping at BWI-2 is correct after all** — there is nothing to support at
`y` = 128 west of that line. The well needs no header either, because all four of its
edges are beams already.

**The 60 psf sizing answer is unchanged but less marginal.** W12X14 is still the
smallest single section at 3,224 lb; the governing beam B-2 moves from a simple-span
L/366 to **L/402** against the L/360 limit, so the margin goes from 1.7 % to 11.7 %.
W12X14 no longer needs the caveat it carried in Revision 5 — though W12X16 at 460 lb
more is still the choice if you want comfort. The per-beam mixed answer drops to
2,376 lb.

### Still not in the model

**The stair itself.** No dead or live load from the flight, the landing or a guardrail
is applied anywhere, and the stair study's own geometry is a pivoting flight on the
superseded column lineage. Whatever it lands on — B-1, B-2, BW or BWI-2 — takes load
this analysis does not include.

## Revision 5 — smallest standard beam at 60 psf

> Numbers in this section were re-run in Revision 6 after the stair opening was
> corrected. The conclusion held; see above for the revised margins.

> Preliminary sizing, gravity only. **Not a structural verification.**

### The answer: W12X14

| | Section | lb/ft | Depth | Beam steel |
|---|---|---|---|---|
| As drawn | W14X22 | 22 | 13.7 in | 5,066 lb |
| **Smallest single size** | **W12X14** | **14** | **11.9 in** | **3,224 lb** |
| Smallest per beam, 5 sections mixed | W12X16 down to W6X8.5 | — | — | 2,506 lb |

One size throughout saves **1,842 lb, 36 %**. Mixing five sections saves another 718 lb
on top — which by this project's own procurement finding
([EW-TRUSS-PROCUREMENT](../EW-TRUSS-PROCUREMENT.md) §3) is not worth having: handling
and shop time set the price here, not pounds, and five sizes means five of everything.

### Depth beats weight, decisively

Deflection governs, and stiffness goes with depth squared. Walking the whole 30-shape
catalogue, lightest first, the lightest shape that carries every beam at each depth:

| Nominal depth | Lightest that passes | lb/ft |
|---|---|---|
| W6 | **nothing** — W6X8.5 through W6X16 all fail | — |
| W8 | **nothing** — W8X10 through W8X24 all fail | — |
| W10 | W10X19 | 19 |
| **W12** | **W12X14** | **14** |
| W14 | W14X22 | 22 |

W8X24 weighs *more* than the W14X22 now drawn and still fails; W12X14 weighs 14 lb/ft
and passes. Anything under about 10 in of depth is out at this span regardless of how
much steel is in it. The beam that fails first in almost every case is **B-1**, not B-2
— 281.5 in between W2 and E-M1/B.

### How marginal is W12X14

| Reading | B-2 live deflection | B-2 DCR |
|---|---|---|
| Grillage (rigid joints) | L/457 | 0.44 |
| Simple span between columns (no continuity) | **L/366** | 0.57 |
| Limit | L/360 | 1.0 |

**1.7 % of margin** on the conservative reading. **W12X16** — one step up, 460 lb more,
still 1,382 lb lighter than W14X22 — gives L/425 and DCR 0.49, which is real margin. If
the connections are going to be simple shear tabs on cap plates, W12X16 is the honest
pick; W12X14 banks on continuity nobody has designed yet.

### Why the answer is bracketed

The grillage model joins every member rigidly, so each beam gets end restraint from its
column and from the beams crossing it — restraint a bolted cap plate does not give.
Sizing to that alone would be banking on a connection that does not exist yet. So
`simplespan.py` puts the other bracket on it: the same tributary load, carried on a
simply supported span between **columns only**, treating crossing beams as no help at
all. A section has to pass both. For the governing beams the two readings land close
together (B-1: 0.485 vs 0.467; B-2: 0.558 vs 0.494) — the continuity gain and the
flexible-support loss largely cancel.

Four beams — B-1A, BWI-1, BWI-2, BWI-3 — have **no column under either end**. Their
bracket falls back to their own ends on other beams, so for those the conservative
reading is not conservative. They are lightly loaded and land at W6X8.5 either way, but
the check is weaker there and the schedule says so.

### Everything else at 60 psf

Joists and columns were not resized. With the per-beam steel: worst joist **0.58**
(the 114 in west-strip joist again), worst column **0.45**. Both comfortable.

### One consequence worth naming

The beams sit *on* the wall top, so depth pushes the loft floor **up**, not the soffit
down. Going W14X22 → W12X14 lowers the loft deck by 1.8 in and changes no headroom
underneath. That is free, but the roof above is not designed yet, so it is not yet a
number anyone can spend.

### Files

- [sizing-60psf.json](sizing-60psf.json) — per-beam result, both readings, pass history
- `size.py` — the iterative search · `simplespan.py` — the conservative bracket
- `ladder.py` — 30 AISC shapes as `Section` objects, with the derivation check

```
/Volumes/Proj/proj/CAD/garage/.venv/bin/python size.py 60
```

The ladder reuses [loft-span-study/wshapes.py](../loft-span-study/wshapes.py), which
carries strong-axis properties only. Sy, Zy, J and rx are derived from the published
dimensions and checked against the two shapes both project tables share: Sy exact,
Zy within 0.7 %, rx within 0.07 %, J 10–14 % low — which is the conservative direction
for lateral-torsional buckling, so it is left alone.

## Revision 4 — gravity analysis at 100 psf

> Preliminary analysis, gravity only. **Not a structural verification.** Requires review
> and sealing by the responsible California-licensed engineer.

### The answer: the W14X22s handle it with room to spare

| Group | Worst member | DCR | Governed by |
|---|---|---|---|
| **Beams** | **B-2** | **0.45** | flexure, 1.2D + 1.6L |
| Columns | W3 | 0.32 | H1-1b combined axial + flexure |
| Joists | loft west strip joist 2 | 0.88 | bending, NDS ASD |

Nothing is over capacity and nothing is over a deflection limit. The worst beam runs
at **45 % of capacity**, so the W14X22 is roughly twice the section gravity needs. The
binding element in the whole frame is not the steel — it is a 2×8 joist.

### Beams, worst first

| Beam | Lb | DCR | Span | L/live | L/total |
|---|---|---|---|---|---|
| B-2 | 36 | 0.45 | 281.5 | 571 | 495 |
| B-1 | 16 | 0.38 | 281.5 | 692 | 595 |
| B-1A | 36 | 0.36 | 243.8 | 768 | 665 |
| BE | 83 | 0.35 | 331.0 | 1660 | 1430 |
| BWI-2 | 57 | 0.33 | 114.0 | 1969 | 1707 |
| BWI-1 | 83 | 0.24 | 83.0 | 6602 | 5724 |
| B-S | 36 | 0.13 | 281.5 | 2693 | 2234 |
| BEW | 68 | 0.12 | 257.0 | 14287 | 11797 |
| B-N | 15 | 0.10 | 245.5 | 7931 | 6833 |
| BWI-3 | 68 | 0.08 | 68.0 | 22762 | 19610 |
| BW | 114 | 0.03 | 331.0 | 36257 | 30587 |
| B-SO | 180 | 0.02 | 245.5 | 81612 | 43499 |

Limits are L/360 on live and L/240 on total, IBC Table 1604.3. The worst beam is at
L/571 live — comfortable. BW and B-SO are almost unloaded because nothing decks onto
them; they are perimeter members carrying little more than themselves.

### Loads and the equilibrium check

| | |
|---|---|
| Deck | 434.8 sf |
| Live, 100 psf | 43,479 lb |
| Dead: 8 psf superimposed + 7,270 lb frame self weight | 10,748 lb |
| 1.2D + 1.6L | 82,464 lb |

Every deck's tributary closure is **1.0000** — the Voronoi distribution assigned the
area exactly, with nothing lost at the edges. Applied load equals the sum of the
reactions to **zero** residual in both strength combinations.

### Hand checks

The two governing members were re-derived by closed form, outside the model:

| | Hand | Model |
|---|---|---|
| West-strip joist, live deflection | 0.252 in = L/452 | 0.229 in = L/498 |
| West-strip joist, bending stress | fb = 1,169 psi vs Fb = 1,242 psi | DCR 0.879 |
| B-2 as a simple span, DCR | 0.561 | 0.447 |
| B-2 as a simple span, D+L sag | 0.770 in = L/366 | L/495 |

Both B-2 numbers come out lower in the model than by hand, and they should: BE crosses
it at `x` = 211.5 and gives it a third support the hand calculation ignores. The joist
agrees within about 9 %, the difference being the Voronoi tributary against a uniform
strip.

### The one real finding

**B-1A stops at BWI-2, so the loft deck west of the west wall has no support at
`y` = 128.** PyNite caught it as two unstable joist ends before it caught anything
else. The joists in that 37¾ in strip therefore have to run the whole way from B-1 to
B-2 — a **114 in (9 ft 6 in) span** — and that is what puts a 2×8 at DCR 0.88, against
0.27 for the same joist in the bays either side of B-1A.

It passes, but it is the tightest thing in the frame and it is tight only because of a
gap in the beam layout. Three ways out, cheapest first:

1. **Turn those joists east–west** in that strip, spanning 37¾ in between BW and
   BWI-2 instead of 114 in north–south. No steel changes.
2. **Extend B-1A west to BW.** 37¾ in more W14X22, and it makes the loft framing
   uniform across the full width.
3. **Deepen the joists** in that strip to 2×10.

### Not analysed

**No lateral load at all.** This scheme has no roof, no cladding and no lateral system
yet, so there is no enclosure to put wind or seismic on — the surfaces the truss model
loaded do not exist here. That is a gap in the scheme, not a result, and it is the
next thing that has to be settled: a 14-column pinned-base grillage with no bracing has
no lateral system whatsoever.

Also absent: every connection, every footing, and the 5 in flange bearing on a 6 in
wall that the plan already flags.

### Files

- [analysis-results.json](analysis-results.json) — basis, loads, equilibrium, verdict
- [member-schedule.csv](member-schedule.csv) — all 82 members, DCR-sorted
- [frame-3d.html](frame-3d.html) — now has a **Colour: DCR** button beside the views
- `analyze.py`

```
/Volumes/Proj/proj/CAD/garage/.venv/bin/python analyze.py
```

## Revision 3 — analysis model

Owner direction: **every beam sits on top of the existing walls and is a W14X22**,
every column is 4 in bolted to a concrete pier, and the deck is designed for
**100 psf**. That single sentence resolves the two-level split earlier revisions
carried — there is now one beam plane.

| | |
|---|---|
| Existing wall top | `z` = 98.5 |
| Beam soffit | `z` = 98.5, on the wall top |
| **Beam axis** | **`z` = 105.35** (98.5 + 13.7 ⁄ 2) |
| Beams | W14X22 — 12 of them, 5,086 lb |
| Columns | HSS4X4X1/4, `z` = 0 to 105.35, pinned — 14, 1,407 lb |
| Joists | 2×8 DF-L No.2 at ≤16 in o.c. — 60, 800 lb |
| Frame self weight | 7,293 lb (3.65 tons) |
| Deck area | 434.8 sf |
| Design live | 100 psf → 43.5 kip |

Also this revision: every shelf panel edge carries a framing member (the first and
last joist of each panel), and **E-M1/B and E-M/B moved to the BEW axis `x` = 247.5**.
The truss scheme had them 1 in off at 246.5 as an eccentric bearing beside a 3 in
tube; with a W14X22 on the wall top the post sits under the beam axis instead.

### Files

- [frame-3d.html](frame-3d.html) — the 3D model, self-contained. Buttons for
  Isometric / West / East / South / North / Plan; groups toggle from the legend.
- `frame-models/frame-20260917.01-beam-scheme.compas.json` — the canonical COMPAS
  model (Graph of joints + Model of element solids), written through
  `compas-study/frame_models.py` like every other frame model in the project.
- [verification.json](verification.json) — 62 independent geometry checks, all passing
- [frame-audit.json](frame-audit.json), [member-end-audit.csv](member-end-audit.csv)
- `build_frame.py`, `viewer.py`, `verify.py`

```
/Volumes/Proj/proj/CAD/garage/.venv/bin/python build_frame.py
/Volumes/Proj/proj/CAD/garage/.venv/bin/python viewer.py
/Volumes/Proj/proj/CAD/garage/.venv/bin/python verify.py
```

### Reused from the existing analysis work

The model is written in the same schema the truss lineage uses, so
[`structural-analysis-v6`](../structural-analysis-v6/) loads it unchanged:
`frame.load()` reads it, resolves sections and assembles a PyNite model of 130 nodes
and 198 beam elements with no re-meshing. Two edits were needed there:

- `sections.py` gained **W14X22**. Its wt, A, d, bf, tw, tf, Ix, Sx, Zx, Iy and ry
  agree exactly with this project's other AISC transcription,
  `loft-span-study/wshapes.py`. Sy, Zy, J and rx are new here and each reproduces
  from the geometry — Sy = Iy/(bf/2) = 2.800 exactly, Zy = 4.36 against 4.39
  published, rx = √(Ix/A) = 5.537, and J = 0.208 sits above the thin-walled lower
  bound of 0.178.
- `frame.py` added `Joists` to `PIN_ENDED_GROUPS`. Wood framed into steel is a
  simple span; continuity there would be fictitious stiffness.

### How the joints were found

Members are declared by their two endpoints only. The builder then finds every
place an east–west and a north–south run cross, adds those as joints, and splits
both members there — so the file is a finite-element mesh rather than a picture, and
the beams carry real local bending between joist landings. 130 joints, 198 segments,
14 pinned bases, 2 declared overhangs (BEW's 2 in past E-S and E-N), zero
disconnected ends, and every joint has a path to a support.

### What this model is not

No connection is designed, no footing is designed, and no force or capacity appears
in it. Bases are pinned because no foundation exists to justify fixity. Joists are
modelled at the beam axis rather than sitting on top of the flanges, which is the
normal grillage simplification and removes a real but small eccentricity. Section
widths and depths are the owner's directed sizes, not a verified selection.

## Revision 2 — south storage shelf

A storage shelf, not a floor: **ladder access from below, no walking surface.** It fills
the 68 in (5 ft 8 in) bay between B-S and B-1 in three panels on a 3 ft module measured
westward from BEW, with the middle panel taking whatever is left.

| | `x` from | `x` to | Width | |
|---|---|---|---|---|
| **SH-E** | 211.5 | 247.5 | **3 ft** | 3 ft west of BEW — its west edge lands exactly on BE |
| open | 175.5 | 211.5 | 3 ft | |
| **SH-M** | 75.75 | 175.5 | **8 ft 3¾ in** | the remainder |
| open | 39.75 | 75.75 | 3 ft | |
| **SH-W** | −34 | 39.75 | **6 ft 1¾ in** | BW across the west wall, 3 ft past BWI-3 into the main space |

The chain closes exactly: 36 + 36 + 99.75 + 36 + 73.75 = 281.5 = BEW − BW.

**The shelf bears on members 15 in apart in height.** B-S runs on the existing south
wall near `z` = 100; B-1 is at frame level near `z` = 115. A deck spanning between them
is not level — one end needs a ledger, or the two beams need a common soffit. Nothing on
this sheet resolves that.

SH-M's side edges have no north–south beam under them; it is a deck spanning B-S to B-1.

## Revision 1 — the owner's moves

Each station is derived rather than typed, so the arithmetic stays checkable.

| Move | Result |
|---|---|
| B-1 south onto the south window's edge | 4 in beam, north face on `y` = 73 → **center `y` = 71** |
| Column at B-1 × BW | **W2** at (−34, 71) — restores the ARCH-006 ID |
| B-1 runs through to the east wall | west row to `x` = 247.5, supported at both ends like B-2 |
| Embedded east-wall post under B-1 | **E-M1/B** at (246.5, 71), the analog of E-M/B |
| North wall moves north 22 in | new outside face `y` = 271 |
| B-N and W4 / N1 / N2 north | 6 in beam, north face flush at 271 → **center `y` = 268**, 19 in north of the existing wall face |
| B-S onto the top of the south wall | centered on the 6 in wall → **`y` = 3**; W1 follows |
| B-S east end | ties into **BEW**, which E-S supports — not into E-S directly |
| WB3 | removed, confirmed not needed |
| Beam along the west wall, interrupted | **BWI-1 / BWI-2 / BWI-3** at `x` = 3.75, centered on the 7.5 in wall |
| New east-west beam | **B-1A**, BWI-2 → BEW |

Rev 0 positions are no longer marked on the sheet; the table above is the record of what moved.

## Two calls I made

- **B-1A's station is not fixed by anything you said.** "From BWI-2 to BEW" gives the
  ends but not the line. It is drawn at `y` = 128, the midpoint of BWI-2, which also
  falls in the clear zone between the two west windows (101.5–153.25) — so an embedded
  west-wall post under it stays possible if one is ever wanted. Say the word and it moves.
- **S3 moved with B-S.** You named W1; S3 is the other column on that beam, so it went
  to `y` = 3 as well, keeping it under the B-S × BE crossing.

## The beam grid

Beams now run along all four existing walls. Two families, and they are at different
elevations.

| Beam | Station | Sits on | Family |
|---|---|---|---|
| B-SO | `y` = −63 | SW0 / S1 / S2 | frame |
| B-S | `y` = 3 | existing south wall; W1 / S3, ties into BEW | wall |
| B-1 | `y` = 71 | W2 → E-M1/B | frame |
| B-1A | `y` = 128 | BWI-2 → BEW, no column either end | frame |
| B-2 | `y` = 185 | W3 → E-M/B | frame |
| B-N | `y` = 268 | W4 / N1 / N2 | frame |
| BW | `x` = −34 | SW0 / W1 / W2 / W3 / W4 | frame |
| BE | `x` = 211.5 | S2 / S3 / N2 | frame |
| BWI-1 | `x` = 3.75 | existing west wall, B-2 → B-N | wall |
| BWI-2 | `x` = 3.75 | existing west wall, B-1 → B-2 | wall |
| BWI-3 | `x` = 3.75 | existing west wall, B-S → B-1 | wall |
| BEW | `x` = 247.5 | existing east wall — E-S / E-M1 / E-M / E-N | wall |

Ten columns stand on the ground in the frame — SW0, W1, W2, W3, W4, S1, S2, S3, N1, N2 —
plus E-S, E-N and the two embedded option-B posts E-M1/B and E-M/B on the existing east wall.

## What this revision opened up

1. **The wall beams sit about 15 in below the frame beams.** B-S, BWI and BEW run on
   existing wall plates near `z` = 100; the frame beams are near `z` = 115. Every
   crossing is a level change, and B-S, B-1 and B-1A each cross BWI or tie into BEW.
   Nothing on this sheet resolves those elevations.
2. **B-1 no longer sits on the clerestory line.** The truss frame put that member at
   `y` = 76.07, where the solar slope meets the square top. At `y` = 71 the beam and
   that roof line are 5 in apart, so the roof geometry above wants re-coordinating —
   see [`roof-studies/square-upper-west`](../roof-studies/square-upper-west/README.md).
3. **BWI-1 runs 19 in past the end of the existing west wall** to reach B-N at `y` = 268.
   That length is over the north wall extension, not over existing masonry.
4. **E-M1/B naming.** Called E-M1/B here as the analog under B-1, leaving E-M/B —
   established in [`east-wall-study`](../east-wall-study/README.md) rev 04 and EW-P3 — as
   the one under B-2. Worth renaming both to E-B1/B and E-B2/B if that reads better.

## Why beams at all

[`loft-span-study`](../loft-span-study/README.md) reached this from the cost side: over
the same span a truss saves 540–839 lb of steel, worth roughly $400–650, and costs
$2,400–7,600 more, because a fitted tube end is worth $16–39 of shop time and there are
138–174 of them. Its conclusion was *rolled beams, not trusses*. It also found the loft
beams have a 17.5 in depth budget before a soffit drops below the existing wall plate,
so depth is close to free up to about a W16.

## Limits

Layout only. No member sizes, sections, connections, reactions, load cases, lateral
system or foundations are established here, and nothing on this sheet has been analysed.
The 4 in and 6 in widths used to set the B-1 and B-N stations are the owner's working
assumptions, not selected sections — if a section changes, those two stations move with
it. Structural design requires review and sealing by the responsible California-licensed
engineer.
