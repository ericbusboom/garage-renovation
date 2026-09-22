# Loft span study — W1 to E-S

**Project:** 1370 Wilbur Avenue, San Diego, CA 92109 — garage steel frame
**Date:** 2026-09-17 · **Status:** draft, for discussion
**Geometry source:** `roof-studies/square-upper-west/connected-frame/frame-spec.json`
**Load source:** `structural-analysis-v6/loads.py`

> Preliminary sizing study. **Not a structural verification.** Connection design, the
> columns, the foundations and all lateral load are outside it. Nothing here may be
> ordered or built without review and sealing by the responsible California-licensed
> engineer.

---

## The question

The frame as drawn is a superstructure standing over the existing garage: its loft
beams stop at the inner east column line, `x` = 211.5, and span 245.5 in. This study
asks what happens if the framing is brought down onto the columns that are really
there — **W1** on the west, and **E-S** standing on the existing east wall — so that
one member runs the whole way across, and **three** east-west members carry the loft
floor between them.

| | |
|---|---|
| W1 column axis | `x` = −34.0 in |
| E-S column axis | `x` = +247.5 in |
| **Study span** | **281.5 in = 23.46 ft = 23 ft 5½ in** |
| Span in the built frame, for comparison | 245.5 in = 20 ft 5½ in |
| Loft, north–south | 182.9 in = 15.24 ft |
| Loft plan area over the study span | 358 sf |

Two things about that span are worth naming before any numbers:

- **W1 stands 34 in. outside the existing west wall.** The span is not the building's
  width; it is the building plus a 34 in. reach past it on the west side. Three feet
  of the extra span buys nothing structurally.
- **E-S lands on the existing east wall.** That is what makes this the "tighter"
  scheme — the east reaction goes into existing structure rather than a new column
  standing clear of it, which is a foundation question this study does not settle.

---

## Load basis

Roof, solar and the monorail hoist are **excluded**. This is the loft floor only,
which is what was asked for; the roof and the 8 psf solar array are carried by the
trusses above and do not reach these beams.

| | psf | Source |
|---|---|---|
| Floor dead, superimposed | 8.0 | `loads.DEAD['loft_floor']` — ¾ in. plywood 2.3, underlayment/finish 1.7, services and misc. 4.0 |
| Joist self weight | 1.8 | 2×8 DF-L at 16 in. o.c., smeared |
| **Dead, total** | **9.8** | plus beam self weight, added per section |
| Live — reading A | 40 | Project assumption **ASM-006**, residential attic / light domestic storage |
| Live — reading B | 125 | **ASCE 7-16 Table 4.3-1**, "Storage warehouses, light" |

Deflection limits are IBC Table 1604.3 for floor members: **L/360** on live load
(0.782 in. at this span) and **L/240** on dead plus live (1.173 in.).

### Three beams is not one load case

"Three beams share the floor" can mean two different things, and they are 50 % apart:

- **even third** — each beam takes 15.24 / 3 = **5.08 ft** of tributary. This is the
  brief as stated.
- **centre beam** — three beams at equal spacing across the loft puts the middle one
  at 15.24 / 2 = **7.62 ft** of tributary. This is what actually gets built, and it is
  the one to size to.

Both are carried through below, because the difference is visible in the answer.

---

## The answer

**Deflection governs every case. Strength never comes close** — the beams that satisfy
L/360 run at 0.42 to 0.68 in bending. Sizing this span on moment alone would put in a
beam two sizes too shallow.

| Reading | Tributary | Lightest section | Depth | Weight per beam | Governed by | DCR |
|---|---|---|---|---|---|---|
| 40 psf, even third | 5.08 ft | **W12×14** | 11.9 in | 328 lb | live deflection L/360 | 0.69 |
| 40 psf, centre beam | 7.62 ft | **W12×16** | 12.0 in | 375 lb | live deflection L/360 | 0.89 |
| 125 psf, even third | 5.08 ft | **W14×22** | 13.7 in | 516 lb | live deflection L/360 | 0.96 |
| 125 psf, centre beam | 7.62 ft | **W16×26** | 15.7 in | 610 lb | live deflection L/360 | 0.95 |

### So: 12 to 16 inches, and the live load decides which

- If the loft stays at the project's **40 psf** assumption → **W12×16**, 12 in. deep.
- If it is classified as **storage at 125 psf** → **W16×26**, 15.7 in. deep.

That is a four-inch difference in depth and a 63 % difference in steel weight, turning
entirely on an assumption (ASM-006) that the project has recorded as open.

### Headroom does not bind

The loft floor sits at `z` = 116 and the existing wall plate at `z` = 98.5, so there is
a **17.5 in. depth budget** before a beam soffit drops below the top of the existing
structure. Every candidate above fits inside it:

| Section | Soffit | Clear below |
|---|---|---|
| W12×16 | `z` = 104.0 | 8 ft 8 in. |
| W14×22 | `z` = 102.3 | 8 ft 6 in. |
| W16×26 | `z` = 100.3 | 8 ft 4 in. |

All of them clear the existing garage door head at `z` = 86 by more than a foot. **Depth
is free here up to about a W16** — which is not usually true, and is worth knowing
before anyone spends effort making the framing shallow.

### What each depth costs, if you do want it shallower

| Nominal depth | 40 psf, centre beam | 125 psf, centre beam |
|---|---|---|
| W10 | W10×19 — 446 lb, DCR 0.95 | *nothing passes* |
| W12 | **W12×16 — 375 lb**, DCR 0.89 | *nothing passes* |
| W14 | W14×22 — 516 lb, DCR 0.46 | W14×30 — 704 lb, DCR 0.98 |
| W16 | W16×26 — 610 lb, DCR 0.30 | **W16×26 — 610 lb**, DCR 0.95 |
| W18 | W18×35 — 821 lb | W18×35 — 821 lb, DCR 0.56 |

Note the W14/W16 line under 125 psf: **W16×26 is both lighter and deeper than W14×30.**
Going shallower costs 94 lb per beam and buys 1.9 in. of nothing, since the headroom is
not needed.

### Vibration

First-mode frequency of the bare beam under sustained load is 5.7–6.9 Hz across the
four cases. For a storage loft that is comfortable. It is an indicative number only —
a real walking-vibration check under AISC Design Guide 11 needs the deck and joist
modes combined with the beam mode, and is only worth doing if the loft becomes a
workspace rather than storage.

---

## Does the deck reach between three beams?

Three beams leaves a **7.62 ft** joist bay — nearly double the 4.1 ft the two current
loft beams leave. Worth confirming before accepting three, because if the joists cannot
make it the answer is a fourth beam, not a deeper one.

| Beams | Bay | 40 psf | 125 psf |
|---|---|---|---|
| 3 | 7.62 ft | DCR 0.35, bending | **DCR 0.96, bending** |
| 4 | 5.08 ft | DCR 0.16 | DCR 0.43 |

2×8 DF-L No.2 at 16 in. o.c. reaches, both ways. At the 125 psf reading it is at 0.96 —
it works, with nothing left. If the loft goes to the storage classification, the joists
become a second thing to re-examine alongside the beams.

---

## Trusses instead?

A parallel-chord Warren truss in HSS was analysed over the same span at five depths, by
plane pin-jointed direct stiffness, sized off the project's own HSS ladder, including
top-chord local bending between panel points (the joists land at 16 in. o.c., not at
panel points, so the chord spans between them too).

| Depth | Span/depth | Panels | Chord | Web | Weight | Joints | DCR |
|---|---|---|---|---|---|---|---|
| **40 psf, centre beam** | | | | | | | |
| 12 in | 23.5 | 4 | HSS2½×2½×3/16 | HSS1½×1½×⅛ | 267 lb | 22 | 0.99 |
| 18 in | 15.6 | 8 | HSS2×2×⅛ | HSS1½×1½×⅛ | 195 lb | 46 | 0.88 |
| 24 in | 11.7 | 10 | HSS1½×1½×⅛ | HSS1½×1½×⅛ | 188 lb | 58 | 0.95 |
| **125 psf, centre beam** | | | | | | | |
| 18 in | 15.6 | 6 | HSS3½×3½×3/16 | HSS1½×1½×⅛ | 389 lb | 34 | 0.97 |
| 24 in | 11.7 | 10 | HSS2½×2½×3/16 | HSS1½×1½×⅛ | 330 lb | 58 | 0.94 |
| 30 in | 9.4 | 8 | HSS3×3×⅛ | HSS1½×1½×⅛ | 292 lb | 46 | 0.97 |

Unlike the roof trusses in `EW-TRUSS-PROCUREMENT.md` §2.1, **these span/depth ratios are
in the sensible range** — a 12–24 in. truss over 23.5 ft is exactly what the joist
industry builds. So the geometric objection that ruled out catalogue joists for the roof
does not apply here.

### But the money still says no

On the rates this project already established (`EW-TRUSS-PROCUREMENT.md` §3), for all
three members:

| | Weight | Joints | Shop-delivered, galvanized |
|---|---|---|---|
| **40 psf** — 3 × W12×16 | 1,126 lb | 0 | **$1,101 – $1,747** |
| 3 × 18 in. truss | 586 lb | 138 | $3,544 – $8,172 |
| **125 psf** — 3 × W16×26 | 1,830 lb | 0 | **$1,699 – $2,592** |
| 3 × 24 in. truss | 991 lb | 174 | $4,544 – $10,165 |

The truss saves 540–839 lb of steel — worth roughly $400–650 — and costs **$2,400–7,600
more**, because a fitted tube end is worth $16–39 of shop time and there are 138–174 of
them. This is the same finding as the roof package, arriving from the other direction:
on this project joints, not pounds, set the price.

**Rolled beams, not trusses.** Build the truss only if the open-web look is wanted for
its own sake.

### Two alternatives not pursued here

- **Open-web steel joist (K-series).** Geometrically this is the natural product for a
  23.5 ft floor span, and it would be cheaper per pound than either option above. It was
  ruled out on the same ground as the roof package: the order is far below any joist
  mill's minimum, and §2.3 of the procurement study found no one will price three pieces.
  Worth one phone call if a local joist stockist carries 18K or 24K in inventory.
- **Castellated / cellular beam.** Buys stiffness per pound and lets services pass
  through the web. Not relevant when the depth budget is not binding, and it is a
  fabricated item with the same shop-minimum problem.

---

## Recommendation

**Three W16×26, 15.7 in. deep, 610 lb each.**

It carries the storage reading at 0.95 and the project assumption at 0.30, so it is
correct whichever way ASM-006 resolves. It fits inside the 17.5 in. depth budget with
1.8 in. to spare and leaves 8 ft 4 in. clear below. Against the W12×16 that the 40 psf
reading alone would justify, the premium is about 700 lb of steel — roughly **$600–850**
across all three beams, which is less than the cost of discovering later that the loft
needs to be classified as storage.

If ASM-006 is settled at 40 psf first, and settled in writing, **W12×16** is the correct
and lighter answer.

### Open items this study does not resolve

1. **ASM-006.** 40 psf or 125 psf. Everything above turns on it.
2. **The east reaction.** E-S lands on the existing east wall. Whether that wall and its
   footing can take a floor-beam reaction is a foundation question, not addressed here.
3. **The 34 in. west overhang.** W1 stands outside the building. If the loft does not
   actually need to extend that far west, landing the beams on the existing west wall
   instead cuts the span to 247.5 in. (20.62 ft) — and that alone takes the 125 psf
   answer from **W16×26 down to W14×22** (516 lb, DCR 0.98) and the 40 psf answer from
   W12×16 down to **W12×14**. Three feet of span is worth a whole section size; it is
   the cheapest thing on this list.
4. **Connections.** Six beam-to-column connections, none designed.
5. **Lateral.** These beams are also a diaphragm chord and collector in the east-west
   direction. That is a frame-level question and is outside a gravity span study.

---

## Running it

```bash
../.venv/bin/python run.py
```

| File | What it is |
|---|---|
| `span_model.py` | Study geometry, read from `frame-spec.json`; builds the 2-D COMPAS graph |
| `wshapes.py` | AISC W6–W21 candidates (the project library carries only two W shapes) |
| `design.py` | Load takedown, beam checks, joist bay check |
| `truss.py` | Plane pin-jointed direct stiffness solver and truss sizing |
| `cost.py` | Beam vs. truss on the rates from `EW-TRUSS-PROCUREMENT.md` |
| `draw.py` | The two drawings |
| `run.py` | Driver |

Outputs land in `output/`: `elevation.png/.svg`, `answer.png/.svg`, `results.json`,
and the serialised COMPAS models `span-model.compas.json` and
`span-model-truss.compas.json`.

Those two `.compas.json` files are **single lines of framing in the x–z plane**, not
frame models, so per `frame-models/README.md` they stay here beside their viewer rather
than going into the canonical store.

---

## Sources

Geometry: `roof-studies/square-upper-west/connected-frame/frame-spec.json` and
`scene-mesh.json` (existing garage extents). Loads: `structural-analysis-v6/loads.py`,
which cites 2022 CBC / ASCE 7-16. HSS section properties:
`structural-analysis-v6/sections.py`. W-shape properties: AISC Shapes Database v15.0.
Strength: AISC 360-16 LRFD. Deflection: IBC Table 1604.3. Wood: NDS ASD with the
reference values and adjustment factors in `structural-analysis-v6/codecheck.py`.
Fabrication rates: `EW-TRUSS-PROCUREMENT.md` §3.
