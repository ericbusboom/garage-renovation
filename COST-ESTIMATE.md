# Construction Cost Analysis — Garage Steel Frame Renovation
## San Diego, CA 92109 — September 2026 — Revision 3

**Provenance:** [Q]=computed from project data  [P]=published rate  [I]=industry  [NQ]=needs quote  [A]=assumption

---

## PART 1: QUANTITIES FROM THE PROJECT

### Steel — 88 Members, 2.65 Tons

| Metric | Value | Source |
|---|---|---|
| Total primary steel | 5,290 lb (2.645 tons) | member-schedule.csv |
| Purchased weight (+6% plates) | ~5,608 lb | allowance |
| Linear feet | 894 ft | member schedule |
| Paintable surface | 799 sq ft (all faces) | computed |
| Unique connection nodes | 138 | geometry.json |
| Heaviest member | 512 lb (W8×24) | — |
| Members over 0.8 utilization | 16 of 88 | FEA |
| Members over 0.9 utilization | 3 of 88 | FEA |

### Columns & Foundations — 9 Piers

| Column | Section | Weight | Utilization |
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

Each: 24" dia × 36" deep pier. Rebar cage, 4 anchor bolts, base plate, grout.
Total concrete: 3.1 cy. Total excavation: ~5 cy (swell). 138 connection nodes.

### Architectural Quantities

| Item | Quantity | From |
|---|---|---|
| Interior metal panels (net of openings) | 665 sq ft | build_cad.py panel coordinates |
| Wall cavity area (stucco to panel) | 778 sq ft | panel footprint |
| Main roof surface (30° pitch) | 713 sq ft | 282"×214" S + 282"×150" N |
| Hip cap roof surface | ~131 sq ft | 18" rise × ~4 sides |
| Loft deck | 276 sq ft | 224"×177" |
| Loft joists | 15 × 14.75 ft = 221 lin ft | — |
| Steel surface to paint | 799 sq ft | all faces |
| Solar (south face) | 18 panels, 7.7 kW | 6×3 grid, 430W panels |
| Connections | 138 nodes, ~550 bolts, 9 base plates | geometry.json |

---

## PART 2: THE ESTIMATE

### A. EXISTING ROOF DEMOLITION

Before any steel goes up, the existing roof comes off. The stucco walls stay.

| Item | Qty | Unit | Rate | Low | High |
|---|---|---|---|---|---|
| Strip roof (shingles, felt, sheathing) | 750 | sq ft | $1.50–2.50 | $1,125 | $1,875 |
| Remove rafters, ridge, collar ties | 1 | LS | — | $800 | $1,500 |
| Asbestos test (required pre-1990) | 1 | test | — | $200 | $400 |
| 30-yd dumpster + disposal | 1 | trip | — | $600 | $1,000 |
| Labor (3 workers × 2 days) | 6 | man-days | $400–600 | $2,400 | $3,600 |
| Slab protection (plywood overlay) | 1 | LS | — | $300 | $600 |
| **Subtotal demolition** | | | | **$5,425** | **$8,975** |
| ⚠️ If asbestos found | 750 | sq ft | +$4–8 | +$3,000 | +$6,000 |

### B. PRE-CONSTRUCTION

| Item | Qty | Unit | Rate | Low | High |
|---|---|---|---|---|---|
| Structural engineer — review + stamp | 1 | LS | — | $3,500 | $6,000 |
| Structural engineer — connection design | 138 | nodes | — | $3,000 | $6,000 |
| Structural engineer — foundations | 9 | piers | — | $1,500 | $3,000 |
| Structural engineer — lateral (wind/seismic) | 1 | LS | — | $2,000 | $5,000 |
| Structural engineer — construction admin | 4 | visits | $800–1,500 | $3,200 | $6,000 |
| **Engineering subtotal** | | | | **$13,200** | **$26,000** |
| City of SD building permit | 1 | LS | DSD schedule | $3,600 | $5,800 |
| School fee | 618 | sq ft | $0.54 | $334 | $334 |
| Title 24 energy compliance | 1 | LS | — | $600 | $1,400 |
| Electrical permit | 1 | LS | — | $400 | $800 |
| Soils report (if required) | 1 | LS | — | $1,500 | $3,500 |
| **Permits & testing** | | | | **$6,434** | **$11,834** |

### C. FOUNDATIONS (BROKEN OUT)

| Item | Qty | Unit | Rate | Low | High |
|---|---|---|---|---|---|
| Layout & survey (mark 9 pier centers) | 1 | LS | — | $400 | $800 |
| Machine auger, 24"×36" | 9 | ea | $180–320 | $1,620 | $2,880 |
| Hand dig around existing slab edges | 3 | hrs | $80–120 | $240 | $360 |
| Sonotube forms, 24"×36" | 9 | ea | $35–55 | $315 | $495 |
| Spoil removal (5 cy) | 1 | LS | — | $200 | $400 |
| **Excavation** | | | | **$2,775** | **$4,935** |
| Rebar cage (#4 vert, #3 spiral ties) | 9 | ea | $80–140 | $720 | $1,260 |
| Concrete, 3,000 psi, 3.1 cy | 3.5 | cy | $185–260 | $648 | $910 |
| Short-load surcharge (under 5 cy) | 1 | LS | — | $200 | $350 |
| Concrete pump (if truck can't reach) | 1 | LS | — | $400 | $800 |
| Anchor bolts, 3/4"×18", epoxy-set | 36 | ea | $20–35 | $720 | $1,260 |
| Base plates, 8"×8"×3/4" A36, drilled | 9 | ea | $80–150 | $720 | $1,350 |
| Non-shrink grout (column base) | 9 | ea | $30–55 | $270 | $495 |
| Backfill & compaction | 1 | LS | — | $300 | $600 |
| **Concrete & steel embedments** | | | | **$3,978** | **$7,025** |
| Special inspection (footing + bolt) | 3 | visits | $300–500 | $900 | $1,500 |
| **Subtotal foundations** | | | | **$7,653** | **$13,460** |

### D. STEEL SHOP FABRICATION

| Item | Qty | Unit | Rate | Low | High |
|---|---|---|---|---|---|
| Steel material (all sections delivered SD) | 5,608 | lb | $0.77–0.94 | $4,312 | $5,316 |
| Fabrication minimum (cut/cope/weld/drill/prime) | 1 | job | $10,000–18,000 | $10,000 | $18,000 |
| Connection plates, gussets, stiffeners | 1 | LS | — | $2,000 | $4,000 |
| Shop primer (in fabrication) | — | — | incl. | — | — |
| Delivery to site | 1 | LS | — | $400 | $800 |
| **Subtotal steel shop** | | | | **$16,712** | **$28,116** |

### E. STEEL ERECTION (FIELD)

| Item | Qty | Unit | Rate | Low | High |
|---|---|---|---|---|---|
| Boom truck + operator | 3 | days | $1,400–2,000 | $4,200 | $6,000 |
| Ironworker crew (3 workers × 4 days) | 12 | man-days | $500–760 | $6,000 | $9,120 |
| *If prevailing wage (83.41/hr × 1.8 bill)* | 12 | man-days | $1,200–1,500 | $14,400 | $18,000 |
| Field-bolted connections | 56 | joints | $40–80 | $2,240 | $4,480 |
| Field welding (20 hr mobile certified) | 20 | hrs | $100–160 | $2,000 | $3,200 |
| Alignment, plumbing, torque | 1 | LS | — | $1,500 | $3,000 |
| **Subtotal erection (non-PW)** | | | | **$15,940** | **$25,800** |
| *If prevailing wage* | | | | *$24,340* | *$34,680* |

### F. SECONDARY ROOF FRAMING

The study explicitly states "roof secondary framing and floor joists have weight
allowances but have NOT been sized." These must be designed by the engineer.

| Item | Qty | Unit | Rate | Low | High |
|---|---|---|---|---|---|
| C or Z purlins, 6"–8", 16 ga | 192 | lin ft | $3.50–5.50 | $672 | $1,056 |
| Purlin clips / hangers | 64 | ea | $4–8 | $256 | $512 |
| Purlin installation labor | 16 | hrs | $65–95 | $1,040 | $1,520 |
| Hip cap secondary framing | 1 | LS | — | $600 | $1,200 |
| **Subtotal secondary framing** | | | | **$2,568** | **$4,288** |

### G. ROOF WEATHERPROOFING

The metal skin in the renders is architectural, not waterproof.

| Item | Qty | Unit | Rate | Low | High |
|---|---|---|---|---|---|
| Metal roof deck (corrugated, 22 ga) | 713 | sq ft | $3.00–4.50 | $2,139 | $3,209 |
| Self-adhered underlayment (peel & stick) | 713 | sq ft | $1.20–2.00 | $856 | $1,426 |
| Standing seam metal roof panels | 713 | sq ft | $6.00–9.00 | $4,278 | $6,417 |
| Flashing (ridge, eave, hip transition) | 1 | LS | — | $800 | $1,600 |
| Gutters + downspouts | 60 | lin ft | $8–12 | $480 | $720 |
| Hip cap roofing (standing seam) | 131 | sq ft | $8–12 | $1,048 | $1,572 |
| **Subtotal roof** | | | | **$9,601** | **$14,944** |

### H. WALL ASSEMBLY (behind metal panels)

Between the existing stucco and the interior metal panels: a framed, insulated wall.

| Item | Qty | Unit | Rate | Low | High |
|---|---|---|---|---|---|
| Metal stud track (top + bottom) | 115 | lin ft | $1.50–2.50 | $173 | $288 |
| Metal studs, 3-5/8" × 16" OC | 584 | lin ft | $1.50–2.50 | $876 | $1,460 |
| R-19 kraft-faced batt insulation | 778 | sq ft | $1.20–1.80 | $934 | $1,400 |
| 6-mil vapor barrier | 778 | sq ft | $0.15–0.25 | $117 | $195 |
| 5/8" Type X drywall (fire code) | 778 | sq ft | $0.55–0.80 | $428 | $622 |
| Drywall tape, mud, texture | 778 | sq ft | $1.50–2.50 | $1,167 | $1,945 |
| Framing + drywall labor (carpenter) | 40 | hrs | $65–85 | $2,600 | $3,400 |
| Taping labor (drywall finisher) | 16 | hrs | $55–75 | $880 | $1,200 |
| Prime coat (before metal panels) | 778 | sq ft | $0.40–0.70 | $311 | $545 |
| **Subtotal wall assembly** | | | | **$7,486** | **$11,055** |

### I. INTERIOR METAL PANELS (installed)

| Item | Qty | Unit | Rate | Low | High |
|---|---|---|---|---|---|
| 2" insulated metal panels (material) | 665 | sq ft | $8–14 | $5,320 | $9,310 |
| Panel trim, fasteners, sealants | 1 | LS | — | $1,200 | $2,500 |
| IMP installation (specialized) | 665 | sq ft | $6–10 | $3,990 | $6,650 |
| **Subtotal panels** | | | | **$10,510** | **$18,460** |

### J. PAINTING (STEEL)

| Item | Qty | Unit | Rate | Low | High |
|---|---|---|---|---|---|
| Shop primer | — | — | in fab | — | — |
| Surface prep (wire brush, solvent wipe) | 799 | sq ft | $0.40–0.80 | $320 | $639 |
| Field topcoat, 2 coats | 400 | sq ft | $1.50–2.50 | $600 | $1,000 |
| Touch-up at bolted connections | 1 | LS | — | $400 | $800 |
| **Subtotal painting** | | | | **$1,320** | **$2,439** |

### K. LOFT BUILD-OUT

| Item | Qty | Unit | Rate | Low | High |
|---|---|---|---|---|---|
| 3/4" T&G plywood deck | 276 | sq ft | $2.50–4.00 | $690 | $1,104 |
| Wood joists (15 × 14.75 ft) | 221 | lin ft | $1.50–3.00 | $332 | $663 |
| Joist hangers + hardware | 30 | ea | $3–6 | $90 | $180 |
| Flooring (engineered wood or LVP) | 276 | sq ft | $4–8 | $1,104 | $2,208 |
| Loft stair / ladder (ship ladder) | 1 | LS | — | $600 | $1,800 |
| Carpenter labor | 24 | hrs | $65–85 | $1,560 | $2,040 |
| **Subtotal loft** | | | | **$4,376** | **$7,995** |

### L. ELECTRICAL

| Item | Qty | Unit | Rate | Low | High |
|---|---|---|---|---|---|
| 100A subpanel (fed from main) | 1 | ea | — | $1,200 | $2,000 |
| 100A feeder cable + conduit (trench) | 40 | lin ft | $8–14 | $320 | $560 |
| Receptacles (12 total, GFCI) | 12 | ea | $55–85 | $660 | $1,020 |
| 240V/50A EV charger circuit (conduit) | 1 | circuit | — | $400 | $800 |
| 240V/30A hoist circuit | 1 | circuit | — | $300 | $600 |
| LED fixtures (6 high-bay) | 6 | ea | $80–140 | $480 | $840 |
| Switches, boxes, cover plates | 1 | LS | — | $300 | $600 |
| Smoke/CO detectors (interconnected) | 2 | ea | $60–100 | $120 | $200 |
| Exterior light at loading door | 1 | ea | $100–180 | $100 | $180 |
| Electrician labor | 40 | hrs | $90–130 | $3,600 | $5,200 |
| Electrical permit (separate) | 1 | LS | — | $400 | $800 |
| **Subtotal electrical** | | | | **$7,880** | **$12,800** |
| ⚠️ If main panel upgrade needed (200A) | 1 | LS | — | $3,000 | $5,000 |

### M. SOLAR

| Item | Qty | Unit | Rate | Low | High |
|---|---|---|---|---|---|
| Solar (7.7 kW, 18 panels, south face only) | 7,700 | W | $2.90–3.50 | $22,330 | $26,950 |
| Battery (13.5 kWh) — strongly recommended NEM 3 | 1 | unit | — | $8,000 | $12,000 |
| SDGE interconnection fee | 1 | LS | — | $145 | $145 |
| **Gross solar** | | | | **$30,475** | **$39,095** |
| Federal ITC (30%) | | | | −$9,143 | −$11,729 |
| **Net solar** | | | | **$21,333** | **$27,367** |

### N. BALCONY (beyond steel frame)

| Item | Qty | Unit | Rate | Low | High |
|---|---|---|---|---|---|
| Tempered glass guardrail (2 panels × 36"×60") | 30 | sq ft | $80–140 | $2,400 | $4,200 |
| Guardrail posts (steel, bolt-to-frame) | 4 | ea | $150–300 | $600 | $1,200 |
| Waterproof deck surface (pedestal paver) | 43 | sq ft | $15–25 | $645 | $1,075 |
| Sliding glass door (access to balcony) | 1 | ea | — | $1,200 | $2,500 |
| Door installation (rough opening, flashing) | 1 | LS | — | $800 | $1,500 |
| **Subtotal balcony** | | | | **$5,645** | **$10,475** |

### O. DOORS & WINDOWS (exterior envelope)

The model shows these as illustrative infill. They need to be specified and purchased.

| Item | Qty | Unit | Rate | Low | High |
|---|---|---|---|---|---|
| North loading door (glass, insulated, 8'×7') | 1 | ea | — | $1,200 | $2,500 |
| West slider or French door | 1 | ea | — | $1,200 | $2,800 |
| Fixed windows (3 shown in north wall) | 3 | ea | $300–600 | $900 | $1,800 |
| Window installation + flashing | 1 | LS | — | $1,200 | $2,400 |
| **Subtotal doors/windows** | | | | **$4,500** | **$9,500** |

### P. GENERAL CONDITIONS

| Item | Qty | Unit | Rate | Low | High |
|---|---|---|---|---|---|
| Portable toilet | 8 | weeks | $35–50 | $280 | $400 |
| Temporary power (construction panel) | 1 | LS | — | $400 | $800 |
| Dumpster (debris + packaging) | 2 | trips | $500–700 | $1,000 | $1,400 |
| Site fencing / protection | 1 | LS | — | $400 | $800 |
| Final cleanup | 1 | LS | — | $500 | $1,000 |
| **Subtotal GCs** | | | | **$2,580** | **$4,400** |

---

## TOTAL COST SUMMARY

| | Section | Low | High | % |
|---|---|---|---|---|
| A | Existing roof demolition | $5,425 | $8,975 | 3% |
| B | Pre-construction (eng + permits) | $19,634 | $37,834 | 14% |
| C | Foundations | $7,653 | $13,460 | 5% |
| D | Steel shop fabrication | $16,712 | $28,116 | 11% |
| E | Steel erection (non-PW) | $15,940 | $25,800 | 11% |
| F | Secondary roof framing | $2,568 | $4,288 | 2% |
| G | Roof weatherproofing | $9,601 | $14,944 | 6% |
| H | Wall assembly (behind panels) | $7,486 | $11,055 | 5% |
| I | Interior metal panels | $10,510 | $18,460 | 7% |
| J | Painting (steel) | $1,320 | $2,439 | 1% |
| K | Loft build-out | $4,376 | $7,995 | 3% |
| L | Electrical | $7,880 | $12,800 | 5% |
| M | Solar (net of ITC) | $21,333 | $27,367 | 12% |
| N | Balcony (beyond frame) | $5,645 | $10,475 | 4% |
| O | Doors & windows | $4,500 | $9,500 | 4% |
| P | General conditions | $2,580 | $4,400 | 2% |
| | **DIRECT COSTS** | **$143,163** | **$237,908** | |
| Q | GC overhead & profit (13–22%) | $18,611 | $52,340 | |
| | **TOTAL WITH GC** | **$161,774** | **$290,248** | |
| R | Contingency (15%) | $21,474 | $35,686 | |
| | **RECOMMENDED BUDGET** | **$183,249** | **$325,934** | |

### Rounded: $185,000 – $325,000. Midpoint ~$255,000.

**Owner-builder (no GC, no contingency on GC markup): ~$160,000 – $270,000**

---

## Where the Money Goes

| Category | % |
|---|---|
| Engineering + permits | 14% |
| Steel (material + fab + erect) | 22% |
| Roof (framing + weatherproofing) | 8% |
| Walls (framing + insulation + panels) | 12% |
| Solar (net of ITC) | 12% |
| Electrical | 5% |
| Loft + balcony + doors/windows | 11% |
| Foundations + demo + GCs + contingency | 26% |

---

## What Still Needs Real Quotes

| # | Item | Swing | Why |
|---|---|---|---|
| 1 | Steel fab minimum charge | −$5k / +$12k | 2.65 tons is tiny. Call 3 SD shops. |
| 2 | Structural engineering | −$6k / +$12k | Connection design scope unknown |
| 3 | Prevailing wage trigger | +$8k–$17k | If DSD requires it, Stage E nearly doubles |
| 4 | Asbestos in old roof | +$3,000–6,000 | Pre-1990 construction |
| 5 | Main panel upgrade (200A) | +$3,000–5,000 | May be needed for solar + EV |
| 6 | GC vs. owner-builder | +$19k–$52k | You decide |
| 7 | Foundation complications | +$3k–$10k | Slab condition, groundwater |
| 8 | Standing seam roof vs. cheaper option | −$3k–$5k | TPO membrane is cheaper than metal |
| 9 | Loft stairs vs. ladder | −$600–$1,200 | Ladder saves |
| 10 | Battery vs. solar-only | −$8k–$12k | NEM 3 makes battery pay back faster |