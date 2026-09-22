# STR-007-A · Design load basis

**Date:** 2026-09-18 · **Site:** 1370 Wilbur Avenue, San Diego, CA 92109 · **Risk Category:** II
**Governing code:** 2022 CBC / ASCE 7-16

Every value used by the analysis, with the source it came from. Values marked
_open_ are project assumptions that have not been confirmed.

## Dead load

| Surface | psf | Build-up |
|---|---:|---|
| Solar roof | 8.0 | PV modules and rail racking 4.0, standing-seam panel 1.5, purlins and miscellaneous 2.5 |
| Upper roof | 10.0 | panel 1.5, rigid insulation 1.5, purlins 3.0, low hip cap framing and miscellaneous 4.0 |
| East canopy | 5.0 | light metal panel on exposed rafters, no ceiling |
| Loft floor | 8.0 | ¾ in. plywood 2.3, underlayment and finish 1.7, services and miscellaneous 4.0 |
| Walls | 5.0 | metal panel 1.5, girts 2.5, miscellaneous 1.0, per sq ft of elevation |

Frame self weight is computed from the assigned sections and material densities,
not assumed. It totals 7,012 lb.

## Live load

| Load | Value | Source |
|---|---:|---|
| Roof live, Lr | 20 psf | ASCE 7-16 Table 4.3-1, on the horizontal projection, taken unreduced |
| **Loft, design value** | **75 psf** | Owner decision DEC-008 — equipment loft |
| Loft, dwelling floor minimum | 40 psf | ASCE 7-16 Table 4.3-1, dwelling "all other areas" |
| Loft, storage warehouse | 125 psf | ASCE 7-16 Table 4.3-1, "Storage warehouses, light" — a commercial occupancy, retained as an upper bound |
| Concentrated equipment load | to be scheduled | ASCE 7-16 Sec. 4.4 — governs locally over any uniform value |
| Hoist | 1,000 lb | Owner requirement |
| Hoist vertical impact | 25 % | ASCE 7-16 Sec. 4.6.2, monorail crane |
| Hoist lateral | 10 % of lifted load | ASCE 7-16 Sec. 4.9 |

All three loft values are carried through as separate load cases. The design
value is the owner's decision, not a table lookup: the code's dwelling-floor row
is a living-room figure and its light-storage row describes a commercial
warehouse, and neither is a backyard equipment loft. Code values are minimums,
not targets.

What the uniform value cannot cover is concentrated load. ASCE 7-16 Sec. 4.4
requires the floor to carry a point load wherever that governs, and a dense item
on a small footprint exceeds any of these numbers locally. The owner's schedule
of heavy items and their footprints is an outstanding input to the loft design.

## Snow

Zero. Ground snow load is zero for coastal San Diego (ASCE 7-16 Fig. 7.2-1).

## Wind — ASCE 7-16 Chapter 27, Directional Procedure

| Parameter | Value |
|---|---|
| Basic wind speed V | **96 mph**, 3-second gust, Risk Category II |
| Exposure | C primary; D run as a sensitivity |
| Directionality Kd | 0.85 |
| Topographic Kzt | 1.0 — flat site, no speed-up |
| Ground elevation Ke | 1.0 |
| Gust effect factor G | 0.85 — rigid building |
| Enclosure | enclosed, GCpi = ±0.18 |
| Velocity pressure at mean roof height | 17.9 psf (Exposure C), 21.5 psf (Exposure D) |

External pressure coefficients are taken from Fig. 27.3-1 and interpolated on
roof slope and h/L: windward wall +0.8 on qz, leeward wall by L/B, side walls
−0.7, and the roof zoned by distance from the windward edge where the wind runs
parallel to the slope. Four directions are analysed, each with both internal
pressure signs, because internal pressure cancels in the global resultant but not
in the load on an individual wall member.

### On San Diego wind

The design value is not driven by Santa Ana events. The strongest gust ever
recorded in San Diego County — 106 mph, February 2020 — was at Sill Hill, a
3,500 ft mountain site inland of I-8. Santa Ana winds weaken toward the coast,
and Pacific Beach sees a fraction of the inland peak. The code map value of
96 mph is a 700-year mean-recurrence-interval 3-second gust and
already envelops any wind recorded near this address. It governs, and it is what
was used.

The east canopy is treated with wall rather than roof pressure coefficients. Its
twelve rafters rake between 55 and 74 degrees from horizontal, which is far
closer to a wall than to a roof.

## Seismic — screening only

| Parameter | Value |
|---|---|
| Ss / S1 | 1.0 g / 0.37 g — screening values for coastal San Diego |
| Site class | D — the default where no geotechnical investigation exists |
| SDS / SD1 | 0.667 / 0.409 |
| Response modification R | 3.25 |
| Approximate period Ta | 0.182 s |
| Seismic response coefficient Cs | 0.2051 |
| Effective seismic weight W | 23,573 lb |
| Base shear V | 4,835 lb |

**This is a screening check, not a seismic design.** Site-specific ground motion
values and a site class from an actual geotechnical investigation are required.
The frame has not been detailed or qualified as any of the braced-frame systems
the assumed R factor belongs to, and no seismic detailing, redundancy factor or
drift amplification has been applied.

## Load combinations

ASCE 7-16 Section 2.3 for strength, Appendix C for serviceability. The full set
is listed in Section 4 of the [analysis report](structural-analysis.md).

## Serviceability limits

| Limit | Value | Source |
|---|---|---|
| Floor live deflection | L/360 | IBC Table 1604.3 |
| Floor total deflection | L/240 | IBC Table 1604.3 |
| Roof live deflection | L/240 | IBC Table 1604.3 |
| Wind drift | H/400 | common serviceability target; not a code minimum |
