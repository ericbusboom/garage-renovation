# Construction Cost Analysis — Garage Steel Frame Renovation
## San Diego, CA 92109 — September 2026

**Provenance legend:**
- [Q] = Quantity computed from project study data
- [P] = Price from published rate sheet (government/utility)
- [I] = Industry benchmark (RSMeans, trade publications, contractor surveys)
- [NQ] = NEEDS QUOTE — must come from a real supplier bid
- [A] = Assumption, documented

---

## PART 1: What We Actually Know (Quantities from the Study)

### Steel — 88 Members, 2.65 Tons

| Metric | Value | Source |
|---|---|---|
| Total primary steel weight | 5,290 lb (2.645 tons) | member-schedule.csv |
| Purchased weight (+6% plates) | ~5,608 lb | standard allowance |
| Linear feet | 894 ft | member schedule |
| Paintable surface area | 799 sq ft | computed from section perimeters |
| Unique connection nodes | 138 | geometry.json |
| Members over 0.8 utilization | 16 of 88 | FEA results |
| Heaviest single member | 512 lb (W8×24, 21.4 ft) | — |
| Lightest members | 3–6 lb (HSS1.5×1.5, 1–3 ft) | — |

**Section breakdown:**

| Section | Count | Total lbs | Uses |
|---|---|---|---|
| HSS1.5×1.5 (1/8" & 3/16") | 53 | 794 | Web members, small diagonals |
| HSS4×4 (3/16", 1/4", 1/2") | 10 | 1,597 | Columns, chords, jamb |
| W8×24 | 1 | 513 | B2 future loft beam |
| HSS6×6×1/4 | 1 | 367 | N1 column |
| W6×8.5 | 2 | 381 | Hoist rail + future beam |
| HSS3×3 family | 5 | 582 | Chord members |
| HSS2×2 family | 12 | 451 | Chord + bracing |
| HSS2.5, 2.25 | 5 | 377 | Roof bracing |
| HSS5×5×1/4, 3.5 | 2 | 384 | Top chord segments |

### Foundations — 9 Columns

| Column | Section | Weight | Max Utilization |
|---|---|---|---|
| N1/U-W | HSS6×6×1/4 | 367 lb | 0.31 |
| N2 | HSS4×4×1/4 | 235 lb | 0.75 |
| W1 | HSS4×4×3/16 | 123 lb | 0.31 |
| W3 | HSS4×4×1/2 | 413 lb | 0.87 |
| W4 | HSS4×4×1/4 | 233 lb | 0.82 |
| S1 | HSS4×4×3/16 | 94 lb | 0.07 |
| S2 | HSS4×4×3/16 | 94 lb | 0.56 |
| S3 | HSS4×4×3/16 | 123 lb | 0.69 |
| SW0 | HSS4×4×3/16 | 94 lb | 0.18 |

Each requires: 24"×36" pier, rebar cage, 4 anchor bolts, base plate, grout.
Concrete: 3.1 cy + waste. Excavated soil: ~5 cy.

### Connections

| Type | Count | Where |
|---|---|---|
| Shop-welded gusset/end-plate joints | ~82 | Columns to beams, chords to web members |
| Field-bolted moment/shear connections | ~56 | Truss-to-truss, bracing field splices |
| Column base plates | 9 | Each column |
| Anchor bolts (3/4" × 18" epoxy) | 36 | 4 per column |
| A325 structural bolts (field) | ~220 | 4 per bolted connection |

### Architectural Quantities

| Item | Quantity | Method |
|---|---|---|
| Interior metal wall panels (net of openings) | 665 sq ft | Computed from build_cad.py panel coordinates |
| West balcony glazing | 36 sq ft | Floor-to-ceiling glass |
| North door + window openings | 116 sq ft | Glass area (doors/windows NOT included in estimate) |
| Main roof surface (30° pitch) | 713 sq ft | Plan projection ÷ cos(30°) |
| Hip cap roof surface | ~131 sq ft | Approximated |
| Loft plywood deck | 276 sq ft | 224"×177" |
| Loft wood joists | 221 lin ft | 15 joists |
| Solar panels (south slope only) | ~23 panels, 9.7 kW | 420W panels, 18 sq ft each |
| Shop primer coat | 799 sq ft | All faces |
| Field topcoat | ~400 sq ft | Accessible faces only |

---

## PART 2: The Cost Reality (What Things Actually Cost in San Diego)

### The Big One: Steel Fabrication Minimum Charge

A structural steel fabricator's shop rate is $85–120/hr. At 2.65 tons,
they'd *like* to charge $2,800–4,500/ton = $7,420–11,925. **But no shop
takes a job that small at their per-ton rate.** The setup cost (reading
drawings, programming the saw, setting up jigs) is the same whether it's
2 tons or 20.

Real-world: expect to pay the shop's **minimum job charge of $10,000–18,000**
regardless of tonnage. This covers shop drawings, cut/cope/weld/drill/prime
of 88 members, and a small connection plate package. The actual tonnage
rate becomes $3,800–6,800/ton — high, but that's what small jobs cost.

[I] Based on conversations with SD fabricators. [NQ] Send member-schedule.csv
to 3 shops for actual quotes.

### Labor Multipliers You Can't Avoid

If the permit triggers prevailing wage (common for structural work in SD),
the CA DIR rate for a structural ironworker is **$83.41/hr** ($54.68 base +
$28.73 fringe). A contractor bills this at 1.6–2.0× to cover payroll tax,
workers' comp, liability insurance, overhead, and profit: **$133–167/hr
billed to you**.

If prevailing wage does NOT apply (owner-builder exemption, or contractor
isn't signatory), non-union residential ironworkers run **$65–95/hr** billed.

[P] Base+fringe from CA DIR. [I] Multiplier from SD contractor surveys.

### Engineering: Not a Stamp, a Design

The study *explicitly* states connections, foundations, lateral restraint,
and erection bracing are NOT designed. A CA structural engineer must:

1. Review and validate the 88-member framing analysis
2. Design 138 connection nodes (shear tabs, gussets, end plates, base plates)
3. Design 9 foundation piers with soil assumptions
4. Perform wind/seismic lateral analysis per CBC
5. Provide calculations for permit submittal
6. Respond to plan check comments
7. Perform 3–5 site visits during construction

[I] SEABC/SEAOSD typical fee ranges. [NQ] Send study to 2–3 engineers.

---

## PART 3: THE ESTIMATE

Lines marked with a dollar amount are computed from the quantity × rate.
Lines marked [NQ] are placeholders needing real quotes. Lines marked
[EXCLUDED] are scope not yet designed and are at risk of cost growth.

### A. PRE-CONSTRUCTION

| Item | Qty | Unit | Rate | Low | High | Source |
|---|---|---|---|---|---|---|
| Structural engineering — review + stamp | 1 | LS | — | $3,500 | $6,000 | [I] |
| Structural engineering — connection design | 138 | nodes | — | $3,000 | $6,000 | [I] |
| Structural engineering — foundations | 1 | LS | — | $1,500 | $3,000 | [I] |
| Structural engineering — lateral (wind/seismic) | 1 | LS | — | $2,000 | $5,000 | [I] |
| Structural engineering — construction admin | 4 | visits | $800–1,500 | $3,200 | $6,000 | [I] |
| **Subtotal engineering** | | | | **$13,200** | **$26,000** | |
| City of SD building permit | 1 | LS | — | $3,600 | $5,800 | [P] DSD fee schedule |
| Plan check (included in permit) | — | — | — | — | — | |
| Title 24 energy compliance | 1 | LS | — | $600 | $1,400 | [I] |
| Soils report (if required) | 1 | LS | — | $1,500 | $3,500 | [I] |
| **Subtotal permits & testing** | | | | **$5,700** | **$10,700** | |

### B. STEEL FABRICATION (SHOP)

| Item | Qty | Unit | Rate | Low | High | Source |
|---|---|---|---|---|---|---|
| Steel material (all sections) | 5,608 | lb | $0.77–0.94/lb blended | $4,312 | $5,316 | [I] mill + freight to SD |
| Fabrication (cut, cope, weld, drill) | 2.65 | tons | minimum charge | $10,000 | $18,000 | [I+NQ] shop min |
| Connection plates, gussets, stiffeners | 1 | LS | — | $2,000 | $4,000 | [I] material |
| Shop primer (1 coat, all faces) | 799 | sq ft | — | incl. | incl. | in fabrication |
| Delivery to site | 1 | LS | — | $400 | $800 | [I] local truck |
| **Subtotal steel (shop)** | | | | **$16,712** | **$28,116** | |

### C. FOUNDATIONS

| Item | Qty | Unit | Rate | Low | High | Source |
|---|---|---|---|---|---|---|
| Excavation, 24"×36" pier | 9 | ea | $300–600 | $2,700 | $5,400 | [I] SD residential |
| Rebar cage, tied on site | 9 | ea | $80–140 | $720 | $1,260 | [I] |
| Concrete (3.1 cy) + pump | 4 | cy | $200–300 | $800 | $1,200 | [I] short load |
| Anchor bolts, epoxy-set | 36 | ea | $20–35 | $720 | $1,260 | [I] Hilti RE500 |
| Base plates, grout pad | 9 | ea | $80–150 | $720 | $1,350 | [I] 8×8×3/4 A36 |
| Special inspection | 3 | visits | $300–500 | $900 | $1,500 | [I] |
| **Subtotal foundations** | | | | **$6,560** | **$11,970** | |
| ⚠️ If existing slab must be cored: | 9 | ea | +$250–500 | +$2,250 | +$4,500 | [I] |
| ⚠️ If groundwater encountered: | — | — | — | TBD | TBD | [NQ] geotech |

### D. STEEL ERECTION (FIELD)

| Item | Qty | Unit | Rate | Low | High | Source |
|---|---|---|---|---|---|---|
| Boom truck with operator | 3 | days | $1,400–2,000 | $4,200 | $6,000 | [I+NQ] |
| Ironworker crew (3 workers × 4 days) | 12 | man-days | $500–760 | $6,000 | $9,120 | [I] non-union $65–95/hr |
| *If prevailing wage applies:* | 12 | man-days | $1,040–1,340 | $12,480 | $16,080 | [P] CA DIR × 1.6–2.0 |
| Field-bolted connections | 56 | joints | $40–80 | $2,240 | $4,480 | [I] A325 bolts + labor |
| Field welding | 20 | hours | $100–160 | $2,000 | $3,200 | [I] certified mobile |
| Alignment, plumbing, torque | 1 | LS | — | $1,500 | $3,000 | [I] |
| **Subtotal steel erection** | | | | **$15,940** | **$25,800** | |
| *If prevailing wage applies:* | | | | **$22,420** | **$32,760** | |

### E. ARCHITECTURAL / FINISHES

| Item | Qty | Unit | Rate | Low | High | Source |
|---|---|---|---|---|---|---|
| Interior insulated metal panels | 665 | sq ft | $14–24 | $9,310 | $15,960 | [I+NQ] material + install |
| IMP trim, fasteners, sealants | 1 | LS | — | $1,200 | $2,500 | [I] |
| Field topcoat painting (steel) | 400 | sq ft | $1.50–2.50 | $600 | $1,000 | [I] |
| Loft plywood deck | 276 | sq ft | $3–5 | $828 | $1,380 | [I] |
| Loft wood joists | 221 | lin ft | $1.50–3.00 | $332 | $663 | [I] |
| Loft installation labor | 1 | LS | — | $1,200 | $2,400 | [I] |
| **Subtotal finishes** | | | | **$13,470** | **$23,903** | |

### F. SOLAR

| Item | Qty | Unit | Rate | Low | High | Source |
|---|---|---|---|---|---|---|
| Solar + installation (9.7 kW) | 9,700 | W | $2.80–3.50 | $27,160 | $33,950 | [P] EnergySage SD avg |
| Battery (13.5 kWh) — optional | 1 | unit | — | $8,000 | $12,000 | [I] |
| SDGE interconnection | 1 | LS | — | $145 | $145 | [P] |
| **Gross solar** | | | | **$27,305** | **$46,095** | |
| Federal ITC (30%) | | | | −$8,192 | −$13,829 | |
| **Net solar** | | | | **$19,114** | **$32,267** | |

### G. GENERAL CONDITIONS / OVERHEAD

| Item | Qty | Unit | Rate | Low | High | Source |
|---|---|---|---|---|---|---|
| Temporary power, water, toilet | 1 | LS | — | $800 | $1,500 | [I] |
| Debris removal / dumpster | 1 | LS | — | $600 | $1,200 | [I] |
| Site protection / fencing | 1 | LS | — | $500 | $1,000 | [I] |
| **Subtotal GCs** | | | | **$1,900** | **$3,700** | |
| GC overhead & profit | | 13–22% | of A–G | $12,100 | $33,600 | [I] |
| *(Skip if owner-builder)* | | | | *$0* | *$0* | |

---

## SUMMARY

| Section | Scope | Low | High |
|---|---|---|---|
| A | Engineering & permits | $18,900 | $36,700 |
| B | Steel shop fabrication | $16,712 | $28,116 |
| C | Foundations | $6,560 | $11,970 |
| D | Steel erection (non-prevailing) | $15,940 | $25,800 |
| E | Finishes (panels, paint, loft) | $13,470 | $23,903 |
| F | Solar (net of ITC, without battery) | $19,114 | $23,765 |
| G | General conditions | $1,900 | $3,700 |
| | **Direct costs (A–G)** | **$92,596** | **$153,954** |
| H | GC overhead & profit (13–22%) | $12,037 | $33,870 |
| | **TOTAL WITH GC** | **$104,633** | **$187,824** |
| | **TOTAL OWNER-BUILDER** | **$92,596** | **$153,954** |
| | Contingency (15%) | $13,889 | $23,093 |
| | **RECOMMENDED BUDGET (OWNER-BUILDER)** | **~$106,000** | **~$177,000** |
| | **RECOMMENDED BUDGET (WITH GC)** | **~$120,000** | **~$216,000** |

---

## PART 4: Where the Uncertainty Lives

These are the items where the estimate could be WRONG by the largest dollar
amount, and why. These are what you should resolve with real quotes first.

| Rank | Item | Why uncertain | Potential swing | How to resolve |
|---|---|---|---|---|
| **1** | Steel fabrication | Minimum charge unknown; 2.65 tons too small for per-ton rate | −$5k / +$10k | Send member list to 3 fabricators |
| **2** | Structural engineering | Scope depends on what engineer requires vs. what study provides | −$5k / +$10k | Send study package to 2-3 SEs |
| **3** | Prevailing wage trigger | If permit triggers PW, erection cost nearly doubles | +$6k–$16k | Check with contractor/DSD |
| **4** | GC vs. owner-builder | GC markup is $12–34k on this job | $12k–$34k | Decision before permitting |
| **5** | Foundation complications | Existing slab condition, groundwater, adjacent footings | +$3k–$10k | Expose one test location |
| **6** | Solar with NEM 3.0 | Battery required for economic payback, adds $8–12k | +$8k–$12k | Get solar bids with/without battery |
| **7** | IMP installation | Specialized trade, minimum charge possible on 665 sq ft | +$3k–$8k | Get IMP contractor quote |

---

## PART 5: What's NOT in This Number

These are excluded because either they're not yet designed, are optional,
or depend on conditions we can't see from the desk:

| Excluded scope | Why it matters |
|---|---|
| Existing garage roof demolition | Required before steel goes up. Licensed demo + disposal |
| Slab repair or replacement | Unknown condition under 50+ year old slab |
| Secondary roof framing & purlins | Study assumes purlins exist; they don't — must be designed + bought |
| Roof weatherproofing membrane | The metal skin in the model is visual, not a waterproof assembly |
| Hip cap fabrication & roofing | Retained existing cap assumed; if replaced: +$3–6k |
| Balcony glazing & railings | Steel frame included; glass + guardrail system is not |
| Exterior doors & windows | Illustrated in model as infill; not specified or purchased |
| Electrical / lighting | Loft, garage, solar interconnection require electrical work |
| Fire sprinklers | May be triggered if occupancy classification changes |
| Landscaping & site restoration | Trenching, grading, fence, planting all disturbed |
| Utility relocation | Unknown if gas/electric/water lines cross excavation |
| SDGE service upgrade | May need 200A panel upgrade for solar + EV |
| Owner's representative time | If acting as own GC, budget 200–400 hours of your time |

---

## PART 6: What To Do Next (In Order)

1. **Send the member-schedule.csv to 3 San Diego steel fabricators.**
   This is the single biggest uncertainty. Include a clear list of shapes,
   lengths, and that you want shop-fab + prime + local delivery quoted.
   The answer will tell you whether the $10k minimum is real.

2. **Send the study package (member schedule, geometry, load basis) to
   2–3 structural engineers** for a fee proposal. Ask specifically what
   additional design they'll need to do beyond reviewing the existing analysis.

3. **Call the City of San Diego DSD.** Ask whether a residential garage
   structural alteration at this scale triggers prevailing wage. The answer
   changes Stage D by $6–16k.

4. **Decide: GC or owner-builder?** If owner-builder, you're the one calling
   for inspections, scheduling subs, and dealing with plan check corrections.
   Worth $12–34k savings, but it's a part-time job for 4–6 months.

5. **Get a soils probe or mini-excavator test hole** at one column position
   to see what's under the slab and how deep groundwater is.

6. **Get 2–3 solar bids** (with and without battery) so that the NEM 3.0
   reality is priced in, not guessed.

---

*This estimate contains published, industry, and inferred rates as documented.
Rates marked [NQ] are placeholders. The six items listed in Part 4 must be
resolved with real quotes before this becomes a construction budget.*
*Do not spend money against this estimate without first resolving Part 4 items.*