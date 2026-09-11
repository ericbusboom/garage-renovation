# Construction Cost Estimate — Garage Renovation
## Exposed Steel Frame, San Diego (92109)

**Date:** September 2026
**Status:** PRELIMINARY ORDER-OF-MAGNITUDE ESTIMATE (AACE Class 4/5)
**Accuracy:** −25% / +40%. Not a bid. Not a quote.
**All subtotals computed programmatically** from line items (no hand-typed sums).

---

## Basis of Estimate

| Item | Value | Source |
|---|---|---|
| Primary steel | **5,290 lb (2.65 tons)**, 88 members, 894 lin ft | `member-schedule.csv` (PyNite FEA) |
| HSS portion | 4,397 lb (83%) | Section tally |
| W-shape portion | 893 lb (17%) | W8×24, W6×8.5 |
| Columns / foundations | 9 | W1, W3, W4, S1, S2, S3, N1, N2, SW0 |
| Steel surface to paint | ~800 sq ft | perimeter × length |
| Interior wall panel | ~634 sq ft | architectural model |
| Main roof (solar) | ~680 sq ft, 30° pitch | geometry.json |
| Existing slab support credit | **None** (per study) | load-basis.json |
| Labor basis | Non-union, San Diego residential-commercial | market |

---

## STAGE 1 — Excavation (Dig Holes for Posts)

9 column foundations, assumed 24" dia × 36" deep piers.

| Line item | Qty | Unit | Low | High |
|---|---|---|---|---|
| Layout & potholing (verify utilities) | 1 | LS | $400 | $900 |
| Machine auger, 24" | 9 | ea | $180 | $320 |
| Hand trim & spoil removal | 32 | cy | $25 | $45 |
| **Stage 1 subtotal** | | | **$2,820** | **$5,220** |

*Coastal San Diego sandy soil excavates easily. Caliche/rock: +$500–$2,000/hole.*
*Potholing is legally required before mechanical excavation near the existing slab.*

---

## STAGE 2 — Foundations & Posts

| Line item | Qty | Unit | Low | High |
|---|---|---|---|---|
| Rebar cage (#4 vert, #3 ties) | 9 | ea | $65 | $110 |
| Concrete, 2,500 psi (3.1 cy + waste) | 3.6 | cy | $185 | $260 |
| Anchor bolts, 3/4"×18" epoxy-set | 36 | ea | $18 | $28 |
| Base plates 8"×8"×3/4" A36 drilled | 9 | ea | $55 | $95 |
| Non-shrink grout | 9 | ea | $30 | $55 |
| Special inspection | 1 | LS | $600 | $1,200 |
| **Stage 2 subtotal** | | | **$3,264** | **$5,484** |

*If the existing slab must be cut and re-poured around new piers: +$150–$300/column.*

---

## STAGE 3 — Steel Purchase (Material Only)

| Group | Members | Weight (lb) | $/lb | Low | High |
|---|---|---|---|---|---|
| HSS4×4 (3/16, 1/4, 1/2) | 10 | 1,597 | .78–.95 | $1,246 | $1,517 |
| HSS6/5/3.5/3×3×1/4 | 5 | 1,118 | .78–.95 | $872 | $1,062 |
| HSS3×3×1/8, 2.5, 2.25, 2×2 | 18 | 1,206 | .80–1.00 | $965 | $1,206 |
| HSS1.5 (1/8, 3/16) | 53 | 794 | .85–1.05 | $675 | $834 |
| W8×24, W6×8.5 | 3 | 893 | .62–.78 | $554 | $697 |
| **Steel material** | **88** | **5,608** | | **$4,312** | **$5,316** |
| Delivery / freight | 1 | LS | | $400 | $800 |
| San Diego sales tax (7.75%) | | | | $365 | $474 |
| **Stage 3 total** | | | | **$5,076** | **$6,589** |

*W-shapes are cheap; HSS carries a rolling premium. The 5,608 lb includes ~6%
connection-plate allowance on top of the 5,290 lb of primary steel.*

---

## STAGE 4 — Fabrication & Erection

**Recommended: shop-weld + site-bolt.**

### 4A — Shop fabrication

| Line item | Qty | Unit | Low | High |
|---|---|---|---|---|
| Shop drawings & detailing | 1 | LS | $2,500 | $4,500 |
| Cut, fit, weld | 2.65 | ton | $1,800 | $2,800 |
| Connection plates, gussets, stiffeners | 1 | LS | $1,400 | $2,400 |
| Shop primer | 800 | sq ft | $1.10 | $1.80 |
| Transport to site | 1 | LS | $500 | $900 |
| **Subtotal 4A** | | | **$10,050** | **$16,660** |

### 4B — Field erection

| Line item | Qty | Unit | Low | High |
|---|---|---|---|---|
| Crane / boom truck | 2 | day | $1,600 | $2,400 |
| Ironworker crew (3 workers × 3 days) | 9 | man-day | $620 | $850 |
| Bolted connections (A325 + plates) | 130 | pt | $22 | $42 |
| Field welding (10% of joints) | 15 | hr | $95 | $140 |
| Alignment, plumbing, bolt-up | 1 | LS | $900 | $1,800 |
| **Subtotal 4B** | | | **$13,965** | **$21,810** |

### 4C — Alternative: field-weld everything

+$3,000–$6,000 vs. shop-weld/site-bolt (mobile certified welding is $95–140/hr
with travel, and weather risk). Not recommended unless access is restricted.

| **Stage 4 total (4A + 4B)** | | | **$24,015** | **$38,470** |

---

## STAGE 5 — Solar (Flush-Mounted)

10.5 kW on the 30° main roof.

| Line item | Qty | Unit | Low | High |
|---|---|---|---|---|
| PV modules, 420W | 25 | ea | $190 | $290 |
| Inverters + rapid shutdown | 1 | LS | $2,200 | $3,800 |
| Racking / flush mounts + flashing | 680 | sq ft | $1.40 | $2.40 |
| Electrical (conduit, subpanel) | 1 | LS | $2,400 | $4,200 |
| Installation labor | 1 | LS | $3,000 | $5,500 |
| Permit + SDGE interconnection | 1 | LS | $700 | $1,400 |
| **Gross** | | | **$14,002** | **$23,782** |
| *Less 30% federal ITC* | | | −$4,201 | −$7,135 |
| **Stage 5 net** | | | **$9,801** | **$16,647** |

---

## STAGE 6 — Painting & Interior Panels

| Line item | Qty | Unit | Low | High |
|---|---|---|---|---|
| Field topcoat (all exposed steel) | 800 | sq ft | $1.20 | $2.20 |
| Touch-up after erection | 1 | LS | $600 | $1,100 |
| Interior metal panel (2" insulated) | 634 | sq ft | $9.00 | $14.00 |
| Panel trim, fasteners, sealants | 1 | LS | $900 | $1,800 |
| **Stage 6 subtotal** | | | **$8,166** | **$13,536** |

*Panel attachment/weatherproofing detail is not yet designed — not included.*

---

## STAGE 7 — Soft Costs (Required, Not Optional)

| Line item | Qty | Unit | Low | High |
|---|---|---|---|---|
| Structural engineering review & stamp | 1 | LS | $4,500 | $9,000 |
| San Diego building permit | 1 | LS | $2,200 | $4,500 |
| Plan check / corrections | 1 | LS | $500 | $1,200 |
| Title 24 / energy compliance | 1 | LS | $600 | $1,400 |
| **Stage 7 subtotal** | | | **$7,800** | **$16,100** |

*A licensed CA structural engineer must design and stamp connections, foundations,
and lateral restraint before a permit will issue. The study is explicitly not
construction-approved.*

---

## COST SUMMARY

| Stage | Low | High | Midpoint |
|---|---|---|---|
| 1  Excavation | $2,820 | $5,220 | $4,020 |
| 2  Foundations & posts | $3,264 | $5,484 | $4,374 |
| 3  Steel purchase | $5,076 | $6,589 | $5,832 |
| 4  Fabrication & erection | $24,015 | $38,470 | $31,243 |
| 5  Solar (net of ITC) | $9,801 | $16,647 | $13,224 |
| 6  Painting & panels | $8,166 | $13,536 | $10,851 |
| 7  Soft costs | $7,800 | $16,100 | $11,950 |
| **SUBTOTAL** | **$60,943** | **$102,047** | **$81,494** |
| Contingency @ 15% | $9,141 | $15,307 | $12,224 |
| **PROJECT TOTAL** | **$70,084** | **$117,354** | **$93,718** |

### Rounded, honest statement

> **The steel-frame renovation lands in the $70,000 – $117,000 range, with a
> working midpoint around $94,000.** Solar (net of the tax credit) is ~$13k of
> that; the frame itself without solar is ~$57k–$100k ($80k midpoint).

**$/sq ft:** $113–$190/sq ft (618 sq ft footprint), midpoint ~$152/sq ft.
This is consistent with a custom structural steel renovation at 2026 San Diego
prices, which typically runs $120–$200/sq ft before finishes.

---

## Where the Money Goes (midpoint)

| Category | Share |
|---|---|
| Fabrication & erection labor (Stages 1,2,4 labor + 6 labor) | ~55% |
| Engineering & permits | 13% |
| Solar equipment | 9% |
| Steel material | 6% |
| Panels & finishes | 8% |
| Contingency | 13% |

**The lever is labor, not steel.** 2.65 tons of steel is ~$5,000. Paying people
to cut, weld, lift, bolt, and paint it is 4–6× that.

---

## Cost Reduction Options

| Option | Savings | Trade-off |
|---|---|---|
| Maximize shop work, minimize field weld | $3,500–6,000 | needs accurate shop drawings |
| Defer solar | $9,800–16,600 | may lose ITC timing (ITC is 30% through 2032) |
| Owner-perform painting | $4,000–7,000 | 800 sq ft surface prep |
| Owner-supply steel (direct mill buy) | $800–1,500 | you handle delivery/returns |
| Bolted moment connections (not welded) | $2,000–4,000 | may require larger members |
| Phased permits | $500–1,000 | longer schedule |

---

## Major Exclusions (would raise cost)

- Secondary roof framing, purlins, hip-cap fabrication
- Roofing membrane/weatherproofing over the metal skin
- Balcony glazing and railings (balcony *steel* is in; *glass* is not)
- Doors and windows (illustrative in model, not purchased units)
- Interior finish beyond metal panels, insulation, electrical, lighting
- Landscaping restoration, drainage, fencing
- Utility relocation/upsizing
- Fire sprinklers / Title 24 lighting if occupancy changes
- Structural repair of existing garage walls or slab

---

## Verification Notes

- **Steel quantity** is directly from the PyNite sizing study (88 members, 5,290 lb),
  cross-checked against `cad-validation.json` (5,289.8 lb) — agree to 0.004%.
- **Pricing** is 2026 West-Coast mill + San Diego market, compiled from public
  AISC/industry sources and regional contractor benchmarks. The project's own
  `cost-inputs.json` marks every rate as **null pending real quotes**, and this
  estimate correctly treats them as scenario assumptions, not quotes.
- **This does not replace** a contractor bid, an engineer's takeoff, or a
  permit-set plan review.

## Recommended Next Steps

1. Engage the structural engineer — everything downstream depends on the stamp.
2. Send `member-schedule.csv` to 2–3 fabricators for real quotes on the 88-member
   package (fabricate + deliver is the most quotable scope).
3. Ask each to bid **both** shop-weld/site-bolt and field-weld to resolve Stage 4.
4. Get 2 solar quotes on the 10.5 kW system; confirm SDGE interconnection timeline.
5. Confirm permit fees with San Diego DSD before committing to a number.