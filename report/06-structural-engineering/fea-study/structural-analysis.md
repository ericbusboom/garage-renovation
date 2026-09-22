# STR-007 — Frame finite element analysis and member optimisation study

**Revision:** 0 · **Date:** 2026-09-18 · **Status:** `draft` · **Section:** 06 Structural engineering
**Site:** 1370 Wilbur Avenue, San Diego, CA 92109 · **Risk Category:** II · **Code:** 2022 CBC / ASCE 7-16
**Geometry:** `frame-models/frame-20260917.05-square-upper-west.compas.json` (version 20260917.05), unmodified
**Software:** PyNite 3.2.0 (linear elastic 3-D frame), COMPAS 2.15.1 geometry

---

## 1. Summary

The frame as drawn does not carry its design loads. Three things are wrong with
it, and all three are cheap to fix:

1. **The flat upper roof has no framing across it** and the head of the clerestory
   has no beam, so the roof load has nowhere to go but the perimeter (F-1).
2. **One column is connected to nothing** — the analysis found it as a rigid-body
   mode before it found anything else (F-2).
3. **Six pairs of X-braces cross without being joined**, so every one of those
   twelve braces is unbraced over its full length (F-3).

Framing the roof and connecting the six crossings — the second of which costs no
material at all — brings the worst utilisation from **4.92 to
1.56**. Four members then need to be one size larger, a
total of **+125 lb**, and the frame passes at
**0.97**.

From that adequate frame, **44 members verify at a
lighter section, saving 1,310 lb**, and
no member survives the combined removal test — the frame carries less spare redundancy than a one-at-a-time check suggests.

The loft is designed to **75 psf** by owner decision, a
value chosen for an equipment loft rather than taken from a table: ASCE 7-16
offers 40 psf for an ordinary dwelling floor and
125 psf for a commercial storage warehouse, and neither
describes this space. The loft framing reaches **DCR 1.01** at that load and the joists must be redesigned (F-4).

No connection, base plate, anchor or foundation is designed or checked here.
Nothing in this document authorises construction.

## 2. What this study does, and what it does not

It takes the canonical frame geometry, assigns materials, section properties,
supports and the design loads recorded in the
[design load basis](design-load-basis.md), solves 27
ASCE 7-16 strength combinations plus the serviceability set, checks every member
to AISC 360-16 and NDS, and then asks two optimisation questions: which members
can be lighter, and which can be deleted.

It does not design anything. The analysis is linear-elastic and first-order.
Section 9 lists every excluded behaviour.

## 3. The model

| | |
|---|---|
| Geometry | 135 members resolved into 301 beam elements |
| Supports | 12 column bases, pinned |
| Steel | ASTM A500 Gr. C (HSS) and A992 (W), Fy = 50 ksi, E = 29,000 ksi |
| Timber | Douglas fir-larch No. 2, E = 1,600 ksi, checked to NDS allowable stress design |

The COMPAS joint graph is used directly as the finite element mesh. Its nodes
carry resolved coordinates and support flags, and its edges are member segments
between consecutive joints — a mesh in all but name. Nothing is re-meshed
between the drawing and the analysis, so every result maps back to a named
member.

**Connection assumptions.** Welded HSS joints are modelled as continuous, which is
the realistic idealisation for this construction but remains an assumption: no
joint has been designed, and a joint detailed as a simple connection would
redistribute force away from the flexural capacity relied on here. Discrete
braces are released for bending at both ends. Column bases are pinned — no
fixity is taken from the footings, because no foundation exists yet and
assumption ASM-005 is open.

**Section properties.** Where the geometry model names an AISC designation, it is
used. Where it records only a `concept envelope` — **61 of the
130 members do** — the
lightest standard wall for that outside dimension is assumed. That is the
conservative reading, and it is what makes Section 7 meaningful: a member still
lightly stressed at the thinnest available wall can come down in nominal size.

**How area loads reach the members.** Roof, floor and wall pressures are resolved
onto the members in each surface by a Voronoi tessellation of sample points taken
along every member lying in that surface, clipped to the surface outline. A
clipped Voronoi diagram partitions its outline exactly, so the load applied
always equals pressure times area — checked in Section 5, not assumed. Diagonal
bracing takes no area load: an in-plane brace resists force in its own plane and
is not what a deck or purlin bears on.

## 4. Loads and combinations

Summarised here; every value and its source is in the
[design load basis](design-load-basis.md).

| Load | Value |
|---|---|
| Superimposed dead — solar roof / upper roof / east canopy / loft | 8 / 10 / 5 / 8 psf |
| Wall cladding and girts | 5 psf of elevation |
| Frame self weight | computed from the sections, 7,012 lb |
| Roof live | 20 psf on the horizontal projection |
| Loft live | **75 psf** design value; 40 and 125 psf also analysed — see F-4 |
| Hoist | 1,000 lb with 25 % vertical impact |
| Snow | none — ground snow load is zero at this site |
| Wind | **96 mph** 3-second gust, Exposure C, enclosed, four directions, both internal-pressure signs |
| Seismic | screening only — SDS 0.667, Cs 0.205, base shear 4,835 lb on 23,573 lb |

All 27 ASCE 7-16 Section 2.3 strength combinations were
solved: 1.4D; 1.2D+1.6L+0.5Lr; 1.2D+1.6Lr+1.0L; 1.2D+1.0W+1.0L+0.5Lr and
0.9D+1.0W for four wind directions and both internal-pressure signs; and
1.2D+1.0E+1.0L and 0.9D+1.0E for four seismic directions. Serviceability used D,
D+L, D+Lr, D+0.75L+0.75Lr and D+0.6W.

The member studies in Sections 7 and 8 re-solve the frame once per member, so
they use the 15 combinations that govern
at least one member in the baseline plus all three gravity combinations. The
12 dropped
combinations govern nothing.

### On San Diego wind

The design case is the code map value, not a Santa Ana event. The strongest gust
ever recorded in San Diego County — 106 mph in February 2020 — was at Sill Hill,
a 3,500 ft mountain site inland of I-8. Santa Ana winds weaken toward the coast,
and Pacific Beach sees a fraction of the inland peak. The 96 mph
map value is a 700-year mean-recurrence-interval 3-second gust and already
envelops any wind recorded near this address. It governs, and it is what was used.

## 5. Verification

These are the checks that say whether the analysis itself can be believed.

| Check | Result |
|---|---|
| Vertical equilibrium — applied load against summed reactions | closes to **0.0e+00** relative error on every gravity combination |
| Tributary-area closure on all load surfaces | **1.0000** — applied area equals true surface area exactly |
| Computed section properties against the AISC Manual | HSS4X4X3/16: A = 2.590 in² and I = 6.219 in⁴ against published 2.58 and 6.21. HSS6X6X1/4: 5.224 and 28.57 against 5.24 and 28.6 |
| Member capacities against AISC Tables 3-2, 3-10 and 4-4 | W8X24 φMp 86.6 kip-ft against published 86.6; at Lb = 20 ft, 51.3 against ≈52. HSS4X4X3/16 φPn at KL = 8 ft, 88.0 kips against ≈88 |
| Wind resultant against a hand check | 20.2 psf on the projected area against 19.8 psf from qh·G·(0.8 + 0.5) |
| Stiffness matrix | non-singular in every scenario. The zero-energy mode in the first run was traced to a real unconnected member — Finding F-2 |
| Span deflection | measured against the chord between each member's own end joints, not element by element; no member exceeds its limit on the adequate frame |

## 6. Findings

### F-1 · The upper roof has no load path across it · **blocking**

The flat upper roof is 0 sq ft with a
0.0 ft clear span and **nothing crosses it**.
Its southern edge, at the head of the clerestory, has no beam at all: `W.top` and
`E.top` both begin at that corner and nothing joins them. Analysed literally, the
roof load can only reach the perimeter, and it lands on the two roof cap braces —
21.8 ft HSS1½×1½×⅛ diagonals — which reach **DCR 4.92**.

This is the geometry model behaving as documented: STR-006 states that it
excludes secondary framing, and open item ENV-OI-04 raises the same omission for
the wall girts. It is a gap in the model, not necessarily in the design intent —
but nothing about sizing means anything until it is closed. This study therefore
adds the minimum framing that gives the roof a load path: a clerestory head beam
and four purlins, tagged `Assumed` throughout and written nowhere near
`frame-models/`. Every result after this point is on that completed frame.

**Required:** the engineer of record must frame the upper roof and the clerestory
head. The members assumed here are a placeholder that works, not a design — and
only just: the four assumed purlins are the worst-deflecting members in the whole
frame at L/201 against an L/180 limit (F-6). A real design would likely deepen
them, or add a mid-span line to halve the 15.2 ft span.

### F-2 · One column is connected to nothing · **blocking**

`E-M option B`, the optional east mid column, meets `E-OB` at a joint the geometry
model records as a `declared eccentric bearing` — a one-inch offset carried on no
member. The first analysis run returned a singular stiffness matrix, and the
zero-energy mode localised entirely on that column: pinned at the base, attached
at the top only by a joint with no stiffness, free to swing and to spin about its
own axis. It is carried here as a rigid link so the rest of the frame can be
solved. **That bearing needs a real detail, or the column needs to come out.**

### F-3 · The X-brace crossings are not joints, and that is what makes the braces fail · **high**

Six pairs of braces form an X and pass within an inch or two of each other at
mid-length, but the crossings are not declared joints — the model's own migration
notes say so explicitly for the north diagonals. Unconnected, each brace is
unbraced over its **whole** length, which is why the roof cap braces run at
KL/r = 470 against a limit of 200.

Joining the six crossings halves the unbraced length of all twelve braces and
drops the worst utilisation from **4.46 to
1.56** — without adding a pound of steel. It is by a wide
margin the cheapest change available to this structure.

| Crossing | Braces | Unbraced length before → after |
|---|---|---|
| `X.1` | `BR-N-ground-1` + `BR-N-ground-2` | 132 in → **66 in** |
| `X.2` | `BR-R-cap-1` + `BR-R-cap-2` | 261 in → **131 in** |
| `X.3` | `BR-R-main-1` + `BR-R-main-2` | 261 in → **130 in** |
| `X.4` | `BR-S-1` + `BR-S-2` | 127 in → **64 in** |
| `X.5` | `BR-W-1` + `BR-W-2` | 132 in → **66 in** |
| `X.6` | `T-N diagonal 8` + `T-N diagonal 9` | 164 in → **82 in** |

### F-4 · The loft live load is a decision, not a table lookup · **high**

The code offers two rows that get quoted for a space like this and neither one fits it. 40 psf is ASCE 7-16 Table 4.3-1 for "all other areas" of a dwelling — a living-room number, for furniture and people. 125 psf is a light storage **warehouse**: a commercial building with racked goods and pallet traffic, which a detached residential accessory structure is not. The attic rows do not apply either; an attic with limited storage is defined by a clear height under 42 in. and no real access, and this level has a fixed stair, a loading door and a hoist.

| Uniform live load | What it is | Worst loft member | DCR |
|---:|---|---|---:|
| 40 psf | ASCE 7-16 dwelling floor, "all other areas" | `Wood joist 3-1` (1.5x7.25 DF-L No.2) | **0.64** |
| 75 psf | **design value — owner decision DEC-008** | `Wood joist 3-1` (1.5x7.25 DF-L No.2) | **1.01** ⚠ |
| 125 psf | ASCE 7-16 light storage *warehouse* | `Wood joist 3-1` (1.5x7.25 DF-L No.2) | **1.55** ⚠ |

At the 75 psf design value the joists reach DCR 1.01 and must be redesigned.

**The uniform figure is not the binding constraint.** ASCE 7-16 Sec. 4.4 requires the floor to carry a concentrated load wherever that governs, and a dense item on a small footprint defeats any of these numbers locally: an 800 lb machine on 3 sq ft is about 270 psf on that patch while the room average stays trivial. The owner's heavy items and their footprints have to be scheduled before the loft framing is finalised — that schedule, not the table row, is what sizes these joists.

### F-5 · Four members must be larger, and then the frame passes · **high**

With the roof framed and the crossings joined, 7
members remain over capacity:

| Member | Section | DCR | Governed by | Combination |
|---|---|---:|---|---|
| `E.clerestory` | HSS4X4X3/16 | **1.56** | flexure | C3 1.2D+1.6Lr+1.0L |
| `T-SO` | W6X8.5 | **1.51** | H1-1b combined axial + flexure | C5 0.9D+1.0W [WX+.pi] |
| `E.rear.brace` | HSS2-1/4X2-1/4X1/8 | **1.34** | H1-1a combined axial + flexure | C2 1.2D+1.6L+0.5Lr |
| `E.slope` | HSS2-1/2X2-1/2X1/8 | **1.20** | H1-1a combined axial + flexure | C2 1.2D+1.6L+0.5Lr |
| `BR-R-cap-2` | HSS1-1/2X1-1/2X1/8 | **1.15** | H1-1a combined axial + flexure | C5 0.9D+1.0W [WY-.pi] |
| `W.clerestory` | HSS4X4X3/16 | **1.04** | flexure | C3 1.2D+1.6Lr+1.0L |
| `Wood joist 3-1` | 1.5x7.25 DF-L No.2 | **1.01** | bending | S2 D+L |

Stepping each one up the section ladder — one size per round, re-analysing after
each, because stiffening a brace makes it attract more load — brings the frame
to **DCR 0.97** for
**+125 lb** of extra steel:

| Member | As drawn | Required | Why |
|---|---|---|---|
| `BR-R-cap-2` | HSS1-1/2X1-1/2X1/8 | **HSS2X2X1/8** | H1-1a combined axial + flexure |
| `E.clerestory` | HSS4X4X3/16 | **HSS5X5X1/4** | flexure |
| `E.rear.brace` | HSS2-1/4X2-1/4X1/8 | **HSS3X3X1/8** | H1-1a combined axial + flexure |
| `E.slope` | HSS2-1/2X2-1/2X1/8 | **HSS3X3X1/8** | H1-1a combined axial + flexure |
| `T-SO` | W6X8.5 | **HSS4X4X3/16** | H1-1b combined axial + flexure |
| `W.clerestory` | HSS4X4X3/16 | **HSS5X5X3/16** | flexure |

`T-SO` moves from a wide flange to a tube. It is the south eave beam on an
exposed exterior frame, where a closed section is the better answer anyway, and
an HSS4X4X3/16 is both lighter and stiffer about the weak axis than the W6X8.5 it
replaces.

### F-6 · Deflection · **medium**

**Gravity.** Every member that spans is checked against the chord between its own
two end joints — not element by element, which would flatter a beam that joists
frame into. The worst spans on the adequate frame:

| Member | Span | Combination | Deflection | Ratio | Limit | |
|---|---:|---|---:|---:|---:|---|
| `A.purlin.3` | 183 in | S3 D+Lr | 0.907 in | **L/202** | L/180 | ok |
| `A.purlin.2` | 183 in | S3 D+Lr | 0.899 in | **L/203** | L/180 | ok |
| `A.purlin.4` | 183 in | S3 D+Lr | 0.836 in | **L/219** | L/180 | ok |
| `A.purlin.1` | 183 in | S3 D+Lr | 0.833 in | **L/220** | L/180 | ok |
| `Wood joist 7-0` | 109 in | S2 D+L | 0.258 in | **L/423** | L/240 | ok |
| `B2 future floor beam` | 246 in | S2 D+L | 0.577 in | **L/426** | L/240 | ok |
| `Wood joist 6-0` | 109 in | S2 D+L | 0.251 in | **L/434** | L/240 | ok |
| `Wood joist 8-0` | 109 in | S2 D+L | 0.244 in | **L/446** | L/240 | ok |

**Wind.** Worst drift is **H/415** against a serviceability target of
H/400. It passes, barely, and it gets worse if any bracing comes out — which is
why the removal study in Section 7 tests drift as well as strength.

### F-7 · The wind exposure category has not been verified · **medium**

Exposure C is used. If the site is ruled to be inside the shoreline exposure
band, Exposure D applies and the worst utilisation rises to
**5.40**, 21 %
higher. The distance from this address to open water should be established before
sections are fixed.

## 7. Where the material can come out

![Opportunity map](figures/opportunity-map.png)

Everything in this section is measured against the **adequate frame** of F-5 —
roof framed, crossings joined, four members enlarged — and not against the frame
as drawn. Asking which members can be deleted from a structure that is already
over capacity answers nothing, because the test would have to be "no worse than
something that does not work".

### Lighter sections

44 members verify at a lighter section, saving
**1,310 lb**, which is
19 % of the
frame. Sizing is not done member by member in isolation. Members are taken
least-stressed first, a dozen at a time, and every batch is verified by a full
re-analysis against strength, slenderness **and span deflection** before it is
accepted; members implicated in a failure are reverted and frozen. Only changes
that survived that re-analysis are reported.

The deflection gate matters. Checked on strength alone the ladder will happily
swap a W8X24 floor beam for a tube that carries the moment and then sags four
times as far.

Per-member proposals are in the [member schedule](member-schedule.csv).


### Members that can be deleted

Of 135 members tested, **68** are individually redundant and **11** are critical — deleting any one of those leaves a mechanism.

No member survives the combined removal test: each one that is individually redundant becomes necessary once another is gone. The frame carries less spare redundancy than the one-at-a-time result suggests.

Each candidate was deleted from the model, the frame rebuilt, and every governing
combination re-solved — including recomputing the unbraced lengths of the members
the deleted one used to restrain, which is the effect a by-hand review misses
most often. A member is called removable only if the frame stays stable, nothing
goes over capacity, no span deflection limit is breached, and wind drift stays
inside H/400. The individually-removable set was then deleted cumulatively and
greedily, re-verifying after each one, because members that are removable one at a
time are often not removable together.

One constraint here is not structural. There are no plates anywhere in this model, so the decking does not exist as far as the solver is concerned, and deleting every second joist looks free when it is not — something still has to span between the ones that are left. Maximum surviving spacing is therefore enforced directly: 24 in. for the 3/4 in. plywood floor deck and 32 in. for the metal roof panel over exposed rafters. That rule rejected **10 further members** the frame analysis was perfectly happy to lose — an earlier pass without it proposed deleting joists in a run that would have left a 56 in. gap in the floor. Those limits are ordinary sheathing capacities, not a design, and the deck itself still has to be checked — particularly if the loft is classified as storage (F-4).

![Member weight by group](figures/weight-by-group.png)

### Net effect

| | Weight |
|---|---:|
| Completed frame — as drawn plus the assumed roof framing | 7,012 lb |
| After the verified reductions | 5,702 lb |
| **Net change** | **-1,310 lb (19 % lighter)** |

## 8. Sensitivity

| Variant | Worst utilisation |
|---|---|
| As drawn | 4.92 |
| Upper roof framed | 4.46 |
| X-brace crossings joined | 1.56 |
| Four members enlarged — the adequate frame | **0.97** |
| Wind Exposure D instead of C | 5.40 |
| Loft at 125 psf instead of the 75 psf design value | loft framing 1.55 against 1.01 |

## 9. Excluded behaviour

Not analysed, not checked, and required before construction:

- **every connection** — welds, bolts, gussets, base plates, anchor rods
- **foundations** — footings, piers, bearing, uplift resistance, lateral capacity
- **the existing garage structure** — no reliance on it is modelled and no
  assessment of it has been made
- second-order (P-Delta) effects beyond the linear solution
- seismic detailing, ductility, redundancy factors and drift amplification. The
  seismic case here is an equivalent-lateral-force **screening** check against
  default site values, not a seismic design, and the frame has not been detailed
  or qualified as any of the braced-frame systems its assumed R factor belongs to
- torsion combined with flexure in the wide-flange members
- web local yielding, crippling and all local limit states at load points
- fatigue from hoist use, hoist runway design, trolley lateral and longitudinal loads
- corrosion, fire, weld quality, erection stability and construction loading
- the secondary framing of every surface except the upper-roof members added here
- differential settlement, thermal movement, and the stiffness contributed by
  glazing and cladding

Every result depends on unknown foundations, undesigned connections and
unverified field dimensions. The pinned-base assumption alone means the column
bases carry no moment, which the real footings may not honour.

## 10. What to do next

1. **Frame the upper roof and the clerestory head.** Nothing else here is
   conclusive until the roof has a load path (F-1).
2. **Resolve or delete `E-M option B`** and its eccentric bearing (F-2).
3. **Connect the six X-brace crossings.** Largest single improvement available,
   at no material cost (F-3).
4. **Schedule the heavy items that will actually go up there** — what they weigh
   and what footprint they sit on. The 75 psf design value
   covers the floor on average; concentrated loads are what will size the joists,
   and only the owner has that list (F-4).
5. **Verify the wind exposure category** for the address (F-7).
6. Take the member schedule to the engineer of record as a starting set, not as a
   design. Sections are assumed wherever the geometry model records only an
   envelope.
7. Commission the geotechnical work needed to close ASM-005, so the bases can be
   modelled as they will actually be built.

---

_Generated 2026-09-18 10:26 from `frame-models/frame-20260917.05-square-upper-west.compas.json` by
`structural-analysis-v6/run_all.py`. Checksums of the input model, the generating
code and every published file are in [source-inventory.csv](source-inventory.csv)._
