# Chapter 8 — Solar, battery and roof design

SOL-001 / Revision 1 / 2026-09-15 / draft


## 08 / Solar, battery and roof design

1370 Wilbur Avenue • Pacific Beach, San Diego, CA 92109

SOL-001 • Revision 1 • 15 September 2026 • Draft design-development report

Plan around approximately **5.6–6.0 kW of solar and one 13.5 kWh battery**. Develop the **35° roof option**: it shifts energy toward winter and gains loft envelope with almost no annual generation penalty. Confirm panel fit and clerestory height before selecting the roof.

Typical-year production from cached PVGIS data; household load inferred from six bills.

![Typical-year production from cached PVGIS data; household load inferred from six bills.](figures/seasonal-production.png)

The current 325 ft² solar face is smaller than the 401 ft² face used in earlier energy studies. This chapter corrects that mismatch, retains the historical work with labels, and adds 30°/35°/40° generation, battery-dispatch and geometric comparisons.

This is a planning recommendation for owner review. The array layout, approved roofing system, electrical design, utility provider, site shade, permitting envelope and contractor prices remain to be resolved.


## Reading guide and evidence status

| Part | What it establishes |
| --- | --- |
| 1. Demand and solar resource | Six bills; weather model; sunlight and seasonal production. |
| 2. Roof area and tilt | 325 ft² current concept; physical panel fit; 30°/35°/40° tradeoffs. |
| 3. Storage and economics | Battery operation; system-size comparison; cost and tariff sensitivity. |
| 4. Design coordination | Integrated roof details; next design decisions; source register. |
| Appendix / historical figures | All recovered solar charts plus related roof studies, labeled with their limitations. |

The report contains new calculations and curated historical material. New calculations use the same cached solar/weather inputs and financial framework as the earlier study, allowing changes caused by pitch to be isolated. Historical charts and PDFs are evidence of prior analysis; their older roof-area assumptions do not govern the current concept.

kW is power: the rate of production or use. kWh is energy accumulated over time. A 6 kW solar array is its DC nameplate rating under test conditions. It does not supply 6 kW continuously. One average kW across a year means 8,760 kWh/year.

The data folder supplies bill inputs, monthly production, geometry, system comparisons, sun geometry and validation tables. The accompanying analysis archive preserves the original reports, source data, scripts and hourly runs. Editable report text is supplied as Markdown.


## 1 / Household demand

| 2026 bill | Reported kWh | Reported cost |
| --- | --- | --- |
| 2026-02 | 768 | $303 |
| 2026-03 | 874 | $350 |
| 2026-04 | 712 | $280 |
| 2026-06 | 997 | $390 |
| 2026-07 | 1179 | $460 |
| 2026-08 | 1409 | $544 |

February is treated as a month without air conditioning: 768 / 28 = **27.43 kWh/day**, or **1.14 kW continuously**. The earlier recollection of 24 kWh/day was approximate. Calendar month lengths substitute for actual billing dates.

The retained change-point model is daily kWh = 27.43 + 1.53 × max(monthly mean temperature − 63.57°F, 0). Normal weather gives about **11,096 kWh/year**, including roughly 10,011 kWh of base consumption and 1,085 kWh of cooling. The warmer 2016–2025 weather average gives about 11,335 kWh/year.

The six-point fit has about 56 kWh/month root-mean-square error. April is below the assumed fixed base; this exposes billing-period and usage variability. The inferred base/cooling split is provisional, not a measured end-use breakdown. Obtain 12 months of bills and interval data before ordering equipment.

The historical bill relationship is about $15.15/month + $0.3765/kWh, giving $4,360/year at modeled normal use. The tariff simulation uses a separate bundled SDG&E EV-TOU-5 baseline of $4,303/year. These are different estimation methods, not two simultaneous charges.


## 2 / Sun, weather and energy basis

PVGIS 5.2 calculations use approximate location 32.80°N, 117.24°W, south-facing crystalline-silicon modules, building-integrated mounting, 14% user system losses, and NSRDB radiation data for 2005–2015. Cloud variability is already reflected in irradiance. Do not subtract an additional cloud percentage. Building mounting includes temperature effects; the 14% input is not the model’s entire loss budget. [1]

No horizon or local shading is included, following the owner’s sunny-site description. A measured horizon, nearby trees, the clerestory, fascia/cap projection, and future vegetation still need checking. The cap overlap in the older area calculation was removed geometrically; its shadow was not simulated.

| Mid-month | Sunrise | Sunset | Daylight | Noon elevation |
| --- | --- | --- | --- | --- |
| Jan | 06:51 PST | 17:04 PST | 10.2 h | 36.2° |
| Mar | 06:58 PDT | 18:56 PDT | 12.0 h | 55.3° |
| Jun | 05:40 PDT | 19:58 PDT | 14.3 h | 80.5° |
| Jul | 05:51 PDT | 19:58 PDT | 14.1 h | 78.6° |
| Aug | 06:12 PDT | 19:34 PDT | 13.4 h | 71.1° |
| Sep | 06:32 PDT | 18:56 PDT | 12.4 h | 60.0° |
| Dec | 06:44 PST | 16:44 PST | 10.0 h | 33.9° |

Azimuth is compass bearing: south is 180°. The retained azimuth study found small August gains for southwest orientation at 15°, but that changes the roof direction and does not justify reorienting this design. Its numerical table remains in the supporting data.

Weather inputs use ERA5 via Open-Meteo, with 1991–2020 normals and a 2016–2025 comparison. They describe regional coastal climate rather than a sensor on this roof. [2]


## 3 / How much roof do we have?

| Geometry generation | Solar face | Use in this chapter |
| --- | --- | --- |
| Earlier exposed-frame design | 419.3 ft² gross; 401.3 ft² after cap overlap | Historical 7–8 kW studies only. |
| Current south-post / clerestory concept | 325 ft² gross sloped face | Primary design comparison; full width 23 ft 5½ in. |
| Current 30° plan projection | 281.5 ft² | About 12 ft run; starts 5 ft 3 in south of existing wall. |

The old drawing calls 325 ft² an “active solar plane.” That label overstates what is available to generating modules. Here, 325 ft² is **gross roof face**, including panel gaps, edge treatments, non-generating glass, and any required access clearances.

| System | Module area at 22% | Gross face at 90% coverage |
| --- | --- | --- |
| 5.64 kW | 276 ft² | 307 ft² |
| 6.00 kW | 294 ft² | 326 ft² |
| 7.00 kW | 342 ft² | 381 ft² |

At 22% module efficiency, 325 ft² accommodates 5.31 kW at 80% coverage, 5.65 kW at 85%, or 5.98 kW at 90%. At 23% and 90%, it reaches 6.25 kW. These are area budgets, not proven module layouts. Equation: kW = roof ft² × 0.09290304 × module efficiency × coverage.

Roof dormers, balconies and non-generating infill reduce this budget; surrounding shadows can cost additional energy. A 6 kW array leaves little discretionary roof area in the 325 ft² version.


## 4 / A physical module fit check

Slope-face view, inches, schematic. North is upslope; east/west orientation is not material to this fit test.

![Slope-face view, inches, schematic. North is upslope; east/west orientation is not material to this fit test.](figures/module-layout.png)

A current REC Alpha Pure-RX example is 470 W and about 68.0 × 47.4 in. (22.4 ft²), with maximum module efficiency about 22.6%. Twelve modules in a four-by-three landscape grid give **5.64 kW** and about **269 ft²** of modules. This is an example for checking scale, not a product selection. [3]

With illustrative half-inch gaps, the grid occupies 273.5 × 143.2 in. The roof is 281.5 × 166.3 in. That leaves only about 4 in. on each east/west edge and 11.5 in. at each upslope/down-slope edge if centered. Required fire access, roof edges, clamps and waterproofing may invalidate this layout.

Adding a thirteenth module cannot be justified merely from remaining square feet; it needs a real packing layout. Sixteen of these modules do not fit the 325 ft² face. At a fixed 12-ft run, even 40° gives only about 188 in. slope length, short of four 47.4-in. rows plus gaps.

Recommendation: request layouts in the 5.6–6.0 kW range using approved roof/module assemblies; price alternatives before changing the building around a nominal panel-area target.


## 5 / Pitch: annual and seasonal generation

Fixed 6 kW nameplate; winter = December–February; summer = June–August.

![Fixed 6 kW nameplate; winter = December–February; summer = June–August.](figures/seasonal-tradeoff.png)

| Pitch | Annual 6 kW | Winter 6 kW | Summer 6 kW | August 6 kW |
| --- | --- | --- | --- | --- |
| 30° | 9,689 | 2,108 | 2,555 | 899 |
| 35° | 9,688 | 2,176 | 2,482 | 881 |
| 40° | 9,632 | 2,231 | 2,398 | 859 |

Relative to 30°, 35° changes annual energy by −0.01%, increases winter energy 3.26%, and decreases summer energy 2.85%. At 40°, annual energy changes −0.58%, winter rises 5.86%, and summer falls 6.14%. The near-identical annual output of 30° and 35° is far below weather and model uncertainty.

For 6 kW, the winter gains are about 69 kWh at 35° and 124 kWh at 40°. They are useful but modest. Steeper pitch does not create seasonal energy storage; the battery still shifts hours, not summer into winter.

The earlier 20° comparison gave about 1,587 kWh per installed kW annually, versus 1,615 at 30°: about 1.7% less. It required about 5.52 kW to average 1 kW over the year, versus 5.42 kW at 30°. Its smaller sloped area over a fixed footprint further reduced available capacity.

The hourly bill model shows only about $9/year more utility cost at 35° and $27/year at 40° for the same 6 kW and one battery. Treat differences this small as economically indistinguishable; choose among these pitches mainly for architecture, height and buildability.


## 6 / Monthly output and sizing targets

| Month | Modeled use | 6 kW / 30° | 6 kW / 35° | 6 kW / 40° |
| --- | --- | --- | --- | --- |
| Jan | 850 | 707 | 732 | 752 |
| Feb | 768 | 724 | 741 | 753 |
| Mar | 850 | 895 | 899 | 898 |
| Apr | 823 | 894 | 881 | 864 |
| May | 850 | 866 | 842 | 813 |
| Jun | 896 | 829 | 800 | 767 |
| Jul | 1,105 | 828 | 802 | 773 |
| Aug | 1,182 | 899 | 881 | 859 |
| Sep | 1,117 | 837 | 835 | 828 |
| Oct | 982 | 802 | 814 | 822 |
| Nov | 823 | 732 | 757 | 776 |
| Dec | 850 | 676 | 704 | 726 |

| Pitch | kW for 1,200 kWh in August | kW for average 1 kW annually |
| --- | --- | --- |
| 30° | 8.01 | 5.42 |
| 35° | 8.17 | 5.43 |
| 40° | 8.39 | 5.46 |

All production and use above are kWh/month. The owner’s final summer target was 1,200 kWh in August. At 30° it requires about 8.01 kW; at 40° about 8.39 kW. At 22% efficiency and 90% coverage these need roughly 435–456 ft², exceeding the 325 ft² concept. Size for useful annual savings unless the summer target becomes a firm requirement.

A 5.64 kW array produces about 9,108 kWh/year at 30° or 9,106 at 35°; 6 kW produces about 9,689. This is 82–87% of modeled annual household consumption before storage losses, not equivalent grid independence.


## 7 / West elevations: loft and clerestory

Schematic envelope sections, not construction drawings. Full east–west width is used for gross area; roof/truss thickness and side slopes are not deducted.

![Schematic envelope sections, not construction drawings. Full east–west width is used for gross area; roof/truss thickness and side slopes are not deducted.](figures/west-sections.png)

These sections retain the newer study’s 9-ft low eave, 9-ft-8-in loft floor top, 17-ft-8-in cap eave, and 18-in cap rise. They do not alter the CAD model or establish zoning compliance. At 40°, the solar top passes above the retained cap eave; a positive clerestory needs a raised cap.


## 8 / Two different ways to steepen the roof

| Keep 325 ft² | 30° | 35° | 40° |
| --- | --- | --- | --- |
| Horizontal run (ft) | 12.00 | 11.35 | 10.61 |
| Solar rise (ft) | 6.93 | 7.95 | 8.91 |
| Gross cap plan (ft²) | 328 | 344 | 361 |
| Clerestory at fixed cap (in) | 20.9 | 8.6 | -2.9 |

With the same sloped face, 35° moves the cap about 7.8 in. south, increasing gross cap plan area by 15.2 ft². At 40° it moves 16.6 in. south, gaining 32.5 ft². The cap areas are 328.5, 343.7 and 361.0 ft². These use the full 23-ft-5½-in roof width and the existing north-wall station; they are **not net usable interior loft area**. Side slopes, walls, stairs, voids and structure must be deducted.

The 20.9-in clerestory at 30° shrinks to 8.6 in. at 35° and becomes a 2.9-in downward step at 40°. To preserve the original window band, raise the cap 12.2 in. at 35° or 23.7 in. at 40°. The cap ridge then becomes approximately 20.19 ft or 21.14 ft above the study grade, before any new assembly allowance.

| Keep 12-ft run | 30° | 35° | 40° |
| --- | --- | --- | --- |
| Gross solar face (ft²) | 325.0 | 343.6 | 367.4 |
| Area-based kW at 22%, 90% | 5.98 | 6.32 | 6.76 |
| Solar top above grade (ft) | 15.93 | 17.40 | 19.07 |

At fixed footprint, steeper pitch provides more solar area and headroom under the slope, but no extra cap footprint. Preserving the clerestory requires cap raises of 17.7 in. at 35° or 37.7 in. at 40°. Greater PV capacity is only possible if additional modules physically fit. The 20.75-ft north–south wall length is the roof-study input; Chapter 3 records a conflicting model dimension that must be reconciled.


## 9 / Geometry tradeoff and recommended pitch

The dotted alternative keeps the roof transition at the same plan position; the solid alternative keeps generating-face area constant.

![The dotted alternative keeps the roof transition at the same plan position; the solid alternative keeps generating-face area constant.](figures/geometry-tradeoff.png)

**Develop 35° with approximately 325 ft² of solar face.** It preserves annual production, improves winter production, and gains a modest amount of tall loft envelope. Keep 30° as the height-constrained fallback. Use 40° if the extra loft space is worth the cap/clerestory redesign, rather than for the small energy gain alone.

If preserving the current 20.9-in window band is important, study an approximately 12.2-in cap raise at 35°. If height cannot increase, redesign the clerestory with its roughly 8.6-in remaining gross band; actual glazing will be smaller after framing and flashings.

No numerical net-floor-area gain is claimed here. The full roof width includes areas outside the garage footprint, and the loft’s side slopes and structural depths remain unsettled. The new geometry CSV retains gross headroom-envelope calculations solely as coordination data.


## 10 / Why one battery is the useful starting point

Synthetic average days for 6 kW / 35° / one 13.5 kWh battery. Dispatch assumes perfect knowledge of the modeled year; actual control will differ.

![Synthetic average days for 6 kW / 35° / one 13.5 kWh battery. Dispatch assumes perfect knowledge of the modeled year; actual control will differ.](figures/battery-operation.png)

The model uses 13.5 kWh nominal energy, a 10% reserve, 90% round-trip efficiency, and a conservative 5 kW charge/discharge limit. It permits solar-only charging and discharge to serve the building; no grid arbitrage or battery export. Tesla’s current 13.5 kWh Powerwall is one example of this capacity class, not the specified product. [4]

At 6 kW / 35°, battery discharge is about 3,531 kWh/year. The modeled building still imports about 3,020 kWh/year and exports about 1,219 kWh/year. Annual energy balancing is not enough to eliminate imports because production and consumption occur at different hours.

A 12.15 kWh operating window divided by the 1.14 kW base load is about 10.6 hours before further operating losses or restrictions. Air conditioning and machinery shorten backup time. A battery does not provide backup by itself: transfer/islanding hardware, circuit selection and inverter starting capacity must be designed.


## 11 / Capacity and battery comparison

Planning tariff model at 30°. Gray region exceeds the current approximate area budget; it is retained to show the economic trend.

![Planning tariff model at 30°. Gray region exceeds the current approximate area budget; it is retained to show the economic trend.](figures/battery-sizing.png)

| System at 30° | Installed allowance | Utility / year | Saving / year |
| --- | --- | --- | --- |
| 4 kW + 0 kWh | $20,240 | $2,761 | $1,542 |
| 6 kW + 0 kWh | $25,360 | $2,449 | $1,855 |
| 5.64 kW + 13.5 kWh | $38,688 | $924 | $3,380 |
| 6 kW + 13.5 kWh | $39,610 | $839 | $3,465 |
| 7 kW + 13.5 kWh | $42,170 | $660 | $3,643 |
| 6 kW + 27 kWh | $51,360 | $674 | $3,629 |

Moving from 6 kW alone to 6 kW plus one battery adds a $14,250 installed allowance and saves about $1,610/year in this model. Moving to a second battery adds about $11,750 but saves only another $165/year. A second battery is therefore a backup-duration choice, not the preferred bill-saving choice under these assumptions.

The numerical optimum is shallow: 5.64, 6 and 6.5 kW plus one battery are close financially. Panel layout, real quotes and actual interval demand should choose the final number, not a tiny modeled difference.


## 12 / Installed cost and lifecycle value

| 6 kW + one battery cost basis | Allowance |
| --- | --- |
| Conventional PV hardware/install at $2.56/W | $15,360 |
| 13.5 kWh battery and controls | $14,250 |
| Electrical allowance | $2,500 |
| Custom integrated-looking roof increment | $7,500 |
| Total central allowance | $39,610 |

These are retained planning allowances, not current contractor quotes. They exclude the garage structure and main roof construction, major service upgrades beyond the allowance, and any unpriced integrated-roof certification or fabrication. Obtain separate bids for the waterproof roof, active PV, matching infill, electrical work and battery to avoid double counting.

The prior $2.56/W regional benchmark is preserved as an assumption rather than a verified market offer. A ±20% total-installed-cost range gives roughly $31,700–$47,500 for the central system. The cost of a bespoke solar skin could vary more than this range.

At 30°, the central model gives about $3,465 first-year bill savings and roughly 11.4 years simple payback. With a 25-year horizon, 5% real discount rate, 0.5% annual savings degradation, maintenance of 0.5% of PV cost, and year-15 inverter/battery replacement, levelized net savings are only about $58/year; 25-year NPV is about $815. At 35°, they are about $49/year and $692. This is approximately break-even within uncertainty.

If the $7,500 custom finish would be built regardless of solar, allocating it to the building budget improves the 30° solar investment’s levelized net benefit to about $590/year. This changes cost allocation, not the total cash required. A higher custom premium, more expensive replacement battery, cheaper future electricity or less consumption can reverse the result.

No federal homeowner tax credit is deducted: current IRS guidance excludes residential clean-energy property placed in service after December 31, 2025. Business ownership and other tax provisions are outside this homeowner model. [5]


## 13 / Export credits, tariffs and incentives

SDG&E’s Solar Billing Plan values imported and exported energy by time. Residential customers use EV-TOU-5; evening imports from 4–9 p.m. make stored solar valuable. Export credits appear on the bill. A CCA customer must use its generation provider’s rules as well as SDG&E delivery charges. [6]

The analysis retains bundled rates effective August 1, 2026: about 80.2 cents/kWh summer peak, 49.6 cents off-peak and 13.1 cents super off-peak; winter values are about 52.4, 46.6 and 12.3 cents. It includes $0.79343/day base service charge. Current weekday 10 a.m.–2 p.m. super-off-peak treatment is held across the planning year. [7, 8]

The cached “Current 2026” export file contains NBT00 records although its README describes NBT26. That unresolved vintage mismatch is retained explicitly. The model approximates separate generation/delivery credit buckets, non-bypassable charges and annual surplus adjustment; it is not a full utility billing engine. [9]

Annual net-surplus energy is repriced at net-surplus compensation rather than keeping the ordinary hourly export value. The prior model used 1.702 cents/kWh for that settlement. This is a historical assumption, not a guaranteed future rate. Whether a remaining balance is paid or carried forward depends on the applicable utility/CCA settlement rules; it must be confirmed before treating exports as cash income. [10]

San Diego Community Power currently advertises $350/kWh for market-rate customers installing new solar plus battery: $4,725 for 13.5 kWh if eligible. Enrollment, approved equipment/installer, dispatch participation, available funds and service-provider eligibility must be checked. Keeping the upfront rebate requires at least five years in the program. No rebate or performance incentive is included in the central model. [11]

Because provider, tariff and export vintage remain unconfirmed, dollar figures should be used to compare concepts. The narrow lifecycle margin is not sufficient evidence for a purchase decision.


## 14 / Integrated roof and electrical scope

The desired appearance is a continuous glossy solar face. Standard PV modules must remain intact; odd triangular areas can use compatible non-generating panels. Those pieces add no electrical capacity and need their own wind, impact, fire, drainage and attachment design.

A concealed waterproof layer can be visually simple, but it must be durable, code-compliant and repairable. Ordinary rack-mounted modules do not automatically form an approved waterproof roof. Select either a tested integrated system or a coordinated weatherproof roof with compatible PV attachment, drainage and ventilation. Keep roof and solar costs separate in bids.

The clerestory/cap projection requires a shadow check on the upper module row. Roof pathways, setbacks, access to junctions, module replacement and firefighter requirements may reduce the 325 ft² allocation. City IB-301 describes PV/ESS electrical submittals and the building-review requirements for structural modifications. [12]

| Next design deliverable | Required content |
| --- | --- |
| Final array plan | Exact modules, dimensions, strings, setbacks/pathways, active/inactive infill, shading. |
| Electrical one-line | Service rating, inverter/ESS, circuit protection, conductors, grounding, disconnects and rapid shutdown. |
| Battery location and backup | Impact protection, clearances, transfer equipment, critical circuits and loads. |
| Roof details | Waterproof layer, flashings, drainage, ventilation, attachment and replacement access. |
| Commercial scope | Separate waterproof roof, PV, infill, battery, electrical and utility work prices. |


## Sensitivity / How strong is the cost conclusion?

| Retained scenario | Selected kW / battery kWh | Net benefit per year |
| --- | --- | --- |
| Custom roof, central | 6 / 13.5 | $58 |
| Conventional installation | 6 / 13.5 | $590 |
| Custom premium $15,000 | 6 / 13.5 | $-474 |
| Installed cost -20% | 6.5 / 13.5 | $722 |
| Installed cost +20% | 3.5 / 0 | $-377 |
| Discount rate 3% | 6.5 / 13.5 | $561 |
| Discount rate 8% | 3 / 0 | $-491 |
| Conditional SDCP rebate | 6 / 13.5 | $393 |
| Battery replacement full price | 4 / 0 | $-84 |
| Recent 2016-25 climate | 6 / 13.5 | $98 |
| Cooling +50% | 7 / 13.5 | $135 |
| Base computers -20% | 4 / 0 | $-224 |
| Base computers +20% | 7 / 13.5 | $339 |
| PV weather -10% | 7 / 13.5 | $-79 |
| PV weather +10% | 6 / 13.5 | $167 |
| Battery usable capacity -20% | 6 / 13.5 | $-64 |
| Import rates -20% | 4 / 0 | $-364 |
| Import rates +20% | 6 / 13.5 | $710 |
| Export credits halved | 6 / 13.5 | $35 |
| AC delayed four hours | 6 / 13.5 | $77 |

Historical sweep: 30° and the prior summer-optimal pitch; older 401 ft² area constraint. Dollar values retain prior inputs. Some selected sizes exceed the current 325 ft² layout budget. These rows show how uncertainty changes the decision; they are not current installation quotes. New 30°/35°/40° cases are in the current system-comparison data.


## 15 / Recommendation and remaining decisions

**Carry 5.6–6.0 kW DC and one 13.5 kWh battery into design development.** Compare 35° with the 30° fallback. The illustrated twelve-module 5.64 kW layout is a realistic scale check; its clearances still need professional layout review.

Keep the 325 ft² face as the current area budget. If more capacity is wanted, enlarge the roof or identify a different approved module arrangement. The 8 kW summer-target system belongs to a larger roof concept; neither 35° nor 40° makes it fit within an unchanged 325 ft² face.

Before selecting 35°, decide whether to raise the cap approximately one foot to preserve the window band. Coordinate that height with Chapter 3 setbacks, the survey, side-roof geometry, overhead utilities and structural depth. Keep all existing and proposed datums explicit.

Before selecting equipment, obtain interval demand, full bills including the generation provider, a shade study, electrical-service information, fire-access layout and at least comparable contractor quotes. Test the design with a non-ideal battery controller and the actual tariff/credit rules. Re-run the financial analysis after those inputs are known.

The 30 new system simulations pass annual energy balance with residual below 0.00000001 kWh. Monthly PV is normalized to the cached PVGIS totals. These checks establish internal numerical consistency; they do not validate the assumed household profile, legal roof envelope, product layout or future prices.


## 16 / Methods and reproducibility

The extension imports the definition portion of the earlier analysis into an isolated output directory and runs identical 30°/35°/40° cases. It preserves the original bill fit, PVGIS monthly totals, hourly TMY solar shapes, load timing, tariff model, battery reserve/power/efficiency and financial assumptions. No old result files are overwritten.

Hourly solar shape uses pvlib irradiance transposition and temperature response, then scales each month to the official cached PVGIS energy estimate. Linear programming chooses solar charging and load-serving discharge over the year with cyclic battery state. Perfect foresight and idealized dispatch make this an optimistic operational comparison; the financial objective also simplifies credit caps.

Roof calculations use width W = 281.5/12 ft, gross sloped face A = 325 ft², low eave 9 ft, floor top 9 + 8/12 ft, existing wall length 249/12 ft, and south-post offset 63/12 ft. For fixed face: slope length = A/W; run = length × cos(pitch); rise = length × sin(pitch). For fixed run: area = W × run / cos(pitch).

Gross cap area uses W × (existing north-wall station − slope-end station). It is a roof-plan coordination quantity, not measured usable floor. Clear headroom must subtract roof and structure depths, and net floor must exclude side strips, openings, stairs and any undecked areas.

The prior solar datasets use 2005–2015 radiation, so results describe that climatology, not a 2026 weather forecast. Annual differences of less than 1% between pitches should not be interpreted more precisely than the input data supports.

The source archive preserves all recovered solar analysis code, raw cached inputs, CSV/JSON results, hourly audit files, original PDFs and diagrams, plus the relevant roof-option sources. It excludes software environments, cache files, logs and redundant downloaded ZIP containers. A file inventory records SHA-256 checksums.


## 17 / Sources and supporting documents — 1

[1] **European Commission PVGIS**

[https://re.jrc.ec.europa.eu/pvg_tools/en/](https://re.jrc.ec.europa.eu/pvg_tools/en/)

Cached 5.2 NSRDB monthly outputs and TMY; building-integrated c-Si, 14% user losses.

[2] **Open-Meteo historical weather API**

[https://open-meteo.com/en/docs/historical-weather-api](https://open-meteo.com/en/docs/historical-weather-api)

Retained ERA5 inputs and normal/recent temperature analysis.

[3] **REC Alpha Pure-RX US datasheet**

[https://www.recgroup.com/sites/default/files/2026-03/DS_Alpha_Pure-RX_UL%20DC.pdf](https://www.recgroup.com/sites/default/files/2026-03/DS_Alpha_Pure-RX_UL%20DC.pdf)

470 W example; 68.0 × 47.4 in.; about 22.6% efficiency.

[4] **Tesla Powerwall 3 US datasheet**

[https://energylibrary.tesla.com/docs/Public/EnergyStorage/Powerwall/3/Datasheet/en-us/Powerwall-3-Datasheet.pdf](https://energylibrary.tesla.com/docs/Public/EnergyStorage/Powerwall/3/Datasheet/en-us/Powerwall-3-Datasheet.pdf)

13.5 kWh example; actual power ratings vary by configuration.

[5] **IRS Residential Clean Energy Credit**

[https://www.irs.gov/credits-deductions/residential-clean-energy-credit](https://www.irs.gov/credits-deductions/residential-clean-energy-credit)

No homeowner credit for property placed in service after 2025.

[6] **SDG&E Solar Billing Plan**

[https://www.sdge.com/solar/solar-billing-plan](https://www.sdge.com/solar/solar-billing-plan)

Residential EV-TOU-5 and hourly export credits; CCA rules may differ.

Official regulatory/product pages checked 15 September 2026 where cited. The retained cost allowances are not quotes. The model’s cached source records and acquisition URLs are preserved in the analysis archive.


## 17 / Sources and supporting documents — 2

[7] **SDG&E Total Electric Rates**

[https://www.sdge.com/total-electric-rates](https://www.sdge.com/total-electric-rates)

Cached August 1, 2026 bundled EV-TOU-5 table.

[8] **SDG&E Extended Super Off-Peak Hours**

[https://www.sdge.com/fil/node/33521](https://www.sdge.com/fil/node/33521)

Year-round weekday 10 a.m.–2 p.m. off-peak extension.

[9] **SDG&E export pricing**

[https://www.sdge.com/solar/solar-billing-plan/export-pricing](https://www.sdge.com/solar/solar-billing-plan/export-pricing)

2026 download and unresolved NBT00/NBT26 labeling.

[10] **SDG&E Understanding Your Solar Bill**

[https://www.sdge.com/fil/node/25491](https://www.sdge.com/fil/node/25491)

Annual surplus repricing and credit adjustment.

[11] **Community Power Solar Battery Savings**

[https://sdcommunitypower.org/solar-battery-savings/](https://sdcommunitypower.org/solar-battery-savings/)

Conditional new-system rebate and enrollment terms.

[12] **City of San Diego IB-301**

[https://www.sandiego.gov/development-services/forms-publications/information-bulletins/301](https://www.sandiego.gov/development-services/forms-publications/information-bulletins/301)

PV/ESS permitting and structural-work review.

Official regulatory/product pages checked 15 September 2026 where cited. The retained cost allowances are not quotes. The model’s cached source records and acquisition URLs are preserved in the analysis archive.


## Appendix / Historical figure 01

monthly-production.png

Early 7–8 kW production illustration based on the older, larger solar face. Current 325 ft² roof capacity is lower.

![Early 7–8 kW production illustration based on the older, larger solar face. Current 325 ft² roof capacity is lower.](figures/historical-monthly-production.png)


## Appendix / Historical figure 02

bill-by-system.png

Historical 30° battery comparison; curve retained for traceability. Current face cannot automatically fit the larger systems.

![Historical 30° battery comparison; curve retained for traceability. Current face cannot automatically fit the larger systems.](figures/historical-bill-by-system.png)


## Appendix / Historical figure 03

monthly-energy-and-cost.png

Historical demand backfill and 7 kW comparison; monthly bills precede full credit settlement.

![Historical demand backfill and 7 kW comparison; monthly bills precede full credit settlement.](figures/historical-monthly-energy-and-cost.png)


## Appendix / Historical figure 04

roof-angle-and-fit.png

Historical fixed-footprint angle study using the older 401 ft² face. Do not use its area limit for the current roof.

![Historical fixed-footprint angle study using the older 401 ft² face. Do not use its area limit for the current roof.](figures/historical-roof-angle-and-fit.png)


## Appendix / Historical figure 05

system-economics.png

Historical capacity sweep with 401 ft² area gate. Replaced for roof-fit decisions by the current 325 ft² comparison.

![Historical capacity sweep with 401 ft² area gate. Replaced for roof-fit decisions by the current 325 ft² comparison.](figures/historical-system-economics.png)


## Appendix / Historical figure 06

temperature-fit.png

Retained six-bill temperature fit and climate comparison. Calendar billing approximation remains provisional.

![Retained six-bill temperature fit and climate comparison. Calendar billing approximation remains provisional.](figures/historical-temperature-fit.png)


## Appendix / Historical figure 07

south-post-solar-clerestory.png

Current roof-study source. Its “active solar plane” label is reinterpreted here as gross face; cap projection/shading and usable module area remain unresolved.

![Current roof-study source. Its “active solar plane” label is reinterpreted here as gross face; cap projection/shading and usable module area remain unresolved.](figures/historical-south-post-solar-clerestory.png)


## Appendix / Historical figure 08

west-elevation-roof-options.png

Earlier massing alternatives retained to explain the design path; not the selected envelope.

![Earlier massing alternatives retained to explain the design path; not the selected envelope.](figures/historical-west-elevation-roof-options.png)
