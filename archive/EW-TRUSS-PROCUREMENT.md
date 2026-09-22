# East–West Truss Procurement Analysis

**Project:** 1370 Wilbur Avenue, San Diego, CA 92109 — garage steel frame
**Date:** 2026-09-17 · **Status:** draft · **Geometry source:** `roof-studies/square-upper-west/connected-frame/frame-spec.json` (sha256 `03ea5ba2…0d381e`)
**Section source:** `optimization/network-analysis/weight-sizing/member-schedule.csv`

**Provenance:** [Q]=computed from project data [P]=published rate [I]=industry norm [NQ]=needs quote [A]=assumption

> Not a structural verification. Section sizes are from the weight-sizing study, whose
> span for T-S/T-N differs slightly from the current frame-spec; weights below use
> current frame-spec lengths with those sections. Sizing requires review and sealing
> by the responsible California-licensed engineer before anything is ordered.

---

## 1. What is actually spanning east–west

The building grid runs `x` = west→east and `y` = south→north. Every east–west
assembly spans between the west column line (x = −34.0 in) and the east column line
(x = 211.5 in): **245.5 in = 20 ft 5½ in clear**. There are six of them. [Q]

| ID | Station | What it is | Depth | Pcs | Weight | Fitted joints |
|---|---|---|---|---|---|---|
| T-SO | y = −63 (south wall) | single beam, W6×8.5 at z = 116 | — | 1 | 174 lb | 0 |
| T-S | y = 0 | parallel-chord Warren truss, z 115.0 → 153.4 | 38.4 in | 13 | 187 lb | 22 |
| T1 | y = 76.1 (clerestory) | parallel-chord Warren truss, z 150.1 → 193.6 | 43.5 in | 9 | 214 lb | 14 |
| T1 floor beam | y = 76.1 | W6×8.5 at z = 116 + 3 hangers | — | 4 | 193 lb | 6 |
| B2 floor beam | y = 185 | W8×24 at z = 116 | — | 1 | 491 lb | 0 |
| T-N | y = 259 (north wall) | wall frame incl. garage-door header truss (14.26 ft × 30.2 in deep) and loading-door header (10.23 ft) | 109 in | 21 | 444 lb | 38 |
| **Total** | | | | **49** | **1,703 lb (0.85 ton)** | **80** |

That is **32 % of the frame's 5,290 lb** and roughly **44 % of its fitted joints**. [Q]

Approximately 584 in of all-around fillet weld across the 80 mitred tube ends. [Q]

---

## 2. Three findings that change the procurement question

### 2.1 No catalog product matches these — the depths are architectural, not structural

| Truss | Span | Depth | Span/depth |
|---|---|---|---|
| T-S | 20.46 ft | 38.4 in | **6.4** |
| T1 | 20.46 ft | 43.5 in | **5.6** |
| Garage-door header | 14.26 ft | 30.2 in | **5.7** |

The Steel Joist Institute recommends span/depth between **12 and 24**, most economical
12–18, and specifies that a joist's span shall not exceed 24× its depth. [P] These are
**2–4× deeper than any standard joist for their span.** LH-series starts at 18 in deep
but its load tables begin at 21 ft span, so a 20.5 ft × 40 in joist is off the bottom-left
corner of every table. There is no K, LH, DLH, KCS or joist-girder equivalent. [Q]

The depth is set by the roof profile and the clerestory, not by load. The FEA
utilizations confirm it — **T-S members run 0.00 to 0.29**; that truss is carrying almost
nothing. Only T1 is genuinely working (lower chord 0.90, diagonals 0.89/0.93). [Q]

### 2.2 The pole-barn / metal-building truss market cannot supply these either

The bolt-together steel trusses sold by span (Strouds, SteelBarnTruss, Best Buy Metals,
Wheeler, US Steel Truss) are **pitched gable and lean-to only** — no parallel-chord or flat
product, no published gauge or load rating, and no engineering stamp. Published price for
a 20 ft gable in 2 in angle is $306–390. [P] Useful only as a floor on what commodity
steel trussing costs; not usable for a code-stamped coastal San Diego structure.

### 2.3 The order is too small to be a product order — it will be quoted as shop time

0.85 ton. Joist mill orders run 20+ ton; even the whole frame at 2.65 ton is below most
fabricators' efficient minimum. [I] No one will price this by the pound. **The shop's
minimum charge is likely to govern the number, not the weight.**

---

## 3. Splitting the package the way a shop sees it

Your instinct — *"the headers above the garage doors and the upstairs floor can be
ordered"* — is **half right, and the half that is wrong is the garage-door header.**

### 3.1 Genuinely orderable: 858 lb, 3 items, 50 % of the east-west weight

These are plain rolled sections cut to length. A steel service centre sells them over the
counter; only the end plates need a shop.

| Item | Section | Length | Weight | Material | +end plates | +galv | **Total** |
|---|---|---|---|---|---|---|---|
| T-SO | W6×8.5 | 20 ft 5½ in | 174 lb | $96–122 | $48–132 | $52–87 | **$196–341** |
| T1 floor beam | W6×8.5 | 20 ft 5½ in | 193 lb | $106–135 | $48–132 | $58–96 | **$212–364** |
| B2 floor beam | W8×24 | 20 ft 5½ in | 491 lb | $270–344 | $48–132 | $147–246 | **$465–721** |
| | | | 858 lb | | | | **$873–1,426** |

Rates: W-shape $1,100–1,400/ton delivered [P]; shop $80–110/hr loaded, West Coast [P];
galvanizing $0.30–0.50/lb for 100–500 lb pieces [P].

**Availability note:** W6×8.5 is a valid AISC shape and the lightest W6, but **W6×9 is the
more commonly stocked of the two** — confirm stock before specifying, and let the engineer
confirm the 0.5 lb/ft substitution is acceptable. [P]

### 3.2 Must be fabricated to drawing: 845 lb, 3 assemblies, 74 joints

| Assembly | Weight | Joints | Material | Shop hours | Shop labour | Detailing | Galv | **Total** | $/lb |
|---|---|---|---|---|---|---|---|---|---|
| T-S | 187 lb | 22 | $131–168 | 7.4–13.7 | $592–1,507 | $9–19 | $56–94 | **$788–1,788** | 4.22–9.56 |
| T1 | 214 lb | 14 | $150–193 | 5.8–10.9 | $464–1,199 | $11–21 | $64–107 | **$689–1,520** | 3.22–7.10 |
| T-N | 444 lb | 38 | $311–400 | 10.6–19.3 | $848–2,123 | $22–44 | $133–222 | **$1,314–2,789** | 2.96–6.28 |
| | 845 lb | 74 | | | | | | **$2,791–6,096** | |

Rates: HSS $1,400–1,800/ton delivered [P]; 0.20–0.35 hr per fitted tube end (layout, cut,
fit, tack, weld, grind) [I]; 3–6 hr per assembly for jig layout, squaring, camber, QC and
handling [I]; detailing $100–200/ton [P].

**The garage-door header is in this group, not the orderable one.** As drawn it is a
14.26 ft × 30.2 in deep Warren truss of 1½ in tube with eight fitted joints — a
fabricated assembly, not a header you can buy. It becomes orderable only if it is
redesigned as a single rolled section.

---

## 4. What the east–west package costs

**Sum of parts, shop-delivered and galvanized, excluding erection:**

### $3,665 – $7,522 for all six assemblies (1,703 lb) — $4,300–$8,800 per ton [Q]

That per-ton figure is *above* the $4,000–6,500/ton industry all-in number [P] because
these are tiny, joint-dense, galvanized pieces. Light architectural tube work always
prices high per pound; the saving grace is that there is so little of it.

| Scenario | | |
|---|---|---|
| **A — bundled into one whole-frame fabrication contract** | marginal cost of the east-west package | **$3,665 – $7,522** |
| **B — east-west package ordered standalone** | sum of parts | $3,665 – $7,522 |
| | + shop minimum / mobilisation / drawing set [I] | $3,000 – $6,000 |
| | + delivery, one flatbed, local | $300 – $800 |
| | | **$6,965 – $14,322** |

**Ordering these separately roughly doubles the price.** [Q] You pay a second shop
minimum, a second set of shop drawings, a second mobilisation and a second delivery for
0.85 ton of steel. If the whole frame is going to one fabricator, put these in that
contract and the marginal cost is Scenario A.

**Not included and still needed:**

- **Connection design and PE stamp.** California requires a licensed engineer's seal.
  Fabricators do not provide this; either the project engineer designs the 74 joints or
  you buy design-assist. Project basis: $3,000–6,000 for connection design across the
  frame's now-168 nodes. [Q]
- **Erection.** Every east-west assembly is **under 450 lb** — none of them needs a crane.
  T-N at 444 lb and 20.5 ft is a three-person lift with a genie or small boom truck. The
  crane in the main estimate is driven by the north–south wall frames, not by these.
- **Sales tax** (7.75 % San Diego), permit, inspection.

---

## 5. Who can make them

Realistic vendor types, in order of fit:

### 5.1 Local AESS / residential structural steel fabricator — best fit

This is the right category: small tonnage, exposed finish, custom drawing, local seismic
knowledge, and willing to take a residential job.

| Shop | Location | Why | Contact |
|---|---|---|---|
| **Struc Steel, Inc.** | 1402 Presioca St, Spring Valley CA 91977 | Strongest match. Since 1996. Explicitly lists AESS "canopies, feature frames, **trusses** and exposed connections", residential moment frames and lateral systems, and **steel detailing / design-assist**. Cuts, fits and welds in their own shop. CA Lic. #724066. ~20 min from the site. | (619) 466-4086, Mon–Fri 6am–4pm |
| **S.S. Steel Fabricators, Inc.** | San Diego County | Family shop since 1983. Structural + miscellaneous steel; portfolio includes **tube steel trellises**, catwalks, custom hangers — the right kind of light tube work. No in-house detailing advertised. Lic. #483934. | (619) 443-4846 |
| **White's Steel, Inc.** | Southern California | Full-service structural fabricator/erector; specialises in high-end custom homes and complicated curved work. | — |
| **Antonio's Metal Works** | San Diego | Licensed for structural steel, does both commercial and residential. | — |

### 5.2 Service centre + separate welding shop — cheapest material, you own the coordination

Buy the mill sections yourself and hand a small shop the drawings. Material drops toward
distributor pricing, but you carry the coordination, the PE stamp and the fit-up risk.

- **Totten Tubes** — San Diego branch, HSS specialist (square/rect/round to jumbo),
  custom cut-to-length and laser processing. 800-882-3748.
- **Industrial Metal Supply** — Kearny Mesa, cut-to-size, sawing, laser, waterjet.

### 5.3 Galvanizing

- **San Diego Galvanizing, Inc.** — hot-dip since 1967, San Diego. (619) 233-4763.
  **Ask their kettle length first** — the assemblies are 20 ft 5½ in and many kettles are
  shorter than that. [NQ] Galvanizing also requires vent and drain holes designed into
  the tubes, so it has to be decided before shop drawings, not after. The site is under a
  mile from the ocean, so this is worth doing rather than painting.

### 5.4 Ruled out

- **Steel joist manufacturers** (Vulcraft/Nucor, New Millennium, Valley Joist, Canam) —
  out on both geometry (§2.1) and tonnage (§2.3).
- **Pole-barn / metal-building truss vendors** — gable and lean-to only, no stamp (§2.2).
- **Out-of-state truss fabricators** (e.g. Tech Fab, Houston) — freighting 0.85 ton of
  light trusses across the country, without a CA stamp, makes no sense.
- **Cold-formed steel truss systems** (MiTek Ultra-Span, Alpine TrusSteel) — not usable
  for the exposed HSS roof trusses. *Possibly* relevant if the **loft floor** were
  reconceived as a CFS floor-truss deck instead of steel beams + wood joists; the nearest
  authorised TrusSteel fabricator found is Steel Truss & Supply, Redding CA — 700 mi away.
  Treat as a design alternative, not a supply route for the current design.

---

## 6. Value engineering — and why it barely pays here

T-S carries almost nothing (utilizations 0.00–0.29) and is deep only because the roof
profile puts its top chord on the solar plane. Substituting a single rolled beam:

| | Shop cost | Joints removed |
|---|---|---|
| T-S as drawn (13-piece truss) | $788–1,788 | — |
| T-S as a W8×10 beam | $265–378 | 22 |
| **Saving** | **$542–1,410** | + $400–800 of connection-design scope [Q] |

**Total saving on the order of $1,000–2,200 — not worth redesigning for cost alone.**
These trusses are cheap because they are tiny. Simplify them only if you do not want the
open-web look, not to save money.

**One caveat before anyone swaps it:** T-S has chords at *two* elevations — top at
z = 153.4 (on the solar roof plane, where the load lands) and bottom at z = 115 (the
same datum as the W and E bottom chords). A single beam can only be at one of them, so
the swap may remove part of the z = 115 horizontal plane. That is an engineer's call, not
a procurement one.

---

## 7. What to do next

1. **Do not order these as a separate package** unless the rest of the frame is already
   bought. Scenario B costs roughly double Scenario A for the same steel.
2. **Split the RFQ three ways** — (a) three rolled beams from a service centre, (b) three
   fabricated assemblies to drawing, (c) galvanizing. Quote (b) both standalone and as
   part of the whole frame so the minimum charge is visible.
3. **Call Struc Steel first** and ask for design-assist on the three fabricated
   assemblies. They are the only shop found that advertises AESS trusses, residential
   work and detailing together.
4. **Confirm the galvanizing kettle length (20 ft 5½ in) before shop drawings.** [NQ]
5. **Decide the garage-door header form** — truss as drawn (fabricated) or single rolled
   section (orderable). This is the one item where your "can be ordered" assumption does
   not hold as currently modelled.
6. **Confirm W6×8.5 vs W6×9 stock** with the engineer before releasing the beam order.

---

## Sources

Rates and industry figures: SteelFlo 2026 steel fabrication and structural steel cost
guides. Joist standards: Steel Joist Institute standard specifications and load tables;
New Millennium economical design guide; Vulcraft LH-series load tables. Commodity truss
pricing: Strouds Building Supply, SteelBarnTruss.com. Supplier information: company
websites, accessed 2026-09-17.
